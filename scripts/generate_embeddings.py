import argparse
import os

import psycopg

DATABASE_URL = os.getenv('DATABASE_URL', 'postgresql://steam:steam@localhost:5432/steamgames')
DEFAULT_MODEL = os.getenv('EMBEDDING_MODEL', 'sentence-transformers/all-MiniLM-L6-v2')
DEFAULT_DIM = int(os.getenv('EMBEDDING_DIM', '384'))
DEFAULT_BATCH_SIZE = int(os.getenv('EMBEDDING_BATCH_SIZE', '64'))
DEFAULT_SEED_LIMIT = 1000


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description='Generate and store pgvector embeddings for games.')
    parser.add_argument('--mode', choices=['seed', 'full'], default='seed')
    parser.add_argument('--limit', type=int, default=None, help='Max number of games to embed in this run.')
    parser.add_argument('--batch-size', type=int, default=DEFAULT_BATCH_SIZE)
    parser.add_argument('--model', type=str, default=DEFAULT_MODEL)
    parser.add_argument('--embedding-dim', type=int, default=DEFAULT_DIM)
    parser.add_argument('--only-missing', action='store_true', help='Only process rows where embedding is NULL.')
    parser.add_argument('--dry-run', action='store_true', help='Print candidates only; do not generate/update.')
    return parser.parse_args()


def _effective_limit(mode: str, limit: int | None) -> int | None:
    if limit is not None:
        return max(1, limit)
    if mode == 'seed':
        return DEFAULT_SEED_LIMIT
    return None


def _build_embedding_text(name: str | None, about_the_game: str | None) -> str:
    game_name = (name or '').strip()
    description = (about_the_game or '').strip()
    if description:
        return f'{game_name}\n\n{description}'
    return game_name


def _to_vector_literal(values: list[float]) -> str:
    return '[' + ','.join(f'{value:.8f}' for value in values) + ']'


def _fetch_candidates(
    conn: psycopg.Connection,
    *,
    limit: int | None,
    only_missing: bool,
) -> list[tuple[int, str, str | None]]:
    where_sql = 'WHERE g.embedding IS NULL' if only_missing else ''
    limit_sql = 'LIMIT %s' if limit is not None else ''
    sql = f"""
        SELECT
            g.id,
            g.name,
            g.about_the_game
        FROM games g
        {where_sql}
        ORDER BY (COALESCE(g.positive_reviews, 0) + COALESCE(g.negative_reviews, 0)) DESC, g.id ASC
        {limit_sql}
    """
    with conn.cursor() as cur:
        if limit is not None:
            cur.execute(sql, (limit,))
        else:
            cur.execute(sql)
        rows = cur.fetchall()
    return [(int(row[0]), str(row[1]), row[2]) for row in rows]


def _load_model(model_name: str):
    try:
        from sentence_transformers import SentenceTransformer
    except ModuleNotFoundError as exc:
        raise RuntimeError(
            'sentence-transformers is not installed. Install dependencies from requirements.txt first.'
        ) from exc
    return SentenceTransformer(model_name)


def run() -> None:
    args = parse_args()
    effective_limit = _effective_limit(args.mode, args.limit)

    with psycopg.connect(DATABASE_URL) as conn:
        candidates = _fetch_candidates(
            conn,
            limit=effective_limit,
            only_missing=args.only_missing,
        )
        print(f'Candidates selected: {len(candidates)}')

        if not candidates:
            print('No rows to process.')
            return

        if args.dry_run:
            for game_id, name, _ in candidates[:10]:
                print(f'  id={game_id} name={name}')
            print('Dry-run enabled: skipping embedding generation and database updates.')
            return

        model = _load_model(args.model)
        texts = [_build_embedding_text(name, about_the_game) for _, name, about_the_game in candidates]
        vectors = model.encode(
            texts,
            batch_size=args.batch_size,
            convert_to_numpy=True,
            normalize_embeddings=True,
            show_progress_bar=True,
        )
        if vectors.shape[1] != args.embedding_dim:
            raise RuntimeError(
                f'Embedding dimension mismatch: model produced {vectors.shape[1]}, expected {args.embedding_dim}.'
            )

        rows = [
            (_to_vector_literal(vectors[index].tolist()), game_id)
            for index, (game_id, _, _) in enumerate(candidates)
        ]
        with conn.cursor() as cur:
            cur.executemany(
                """
                UPDATE games
                SET embedding = %s::vector
                WHERE id = %s
                """,
                rows,
            )
        conn.commit()
        print(f'Updated embeddings: {len(rows)}')


if __name__ == '__main__':
    run()
