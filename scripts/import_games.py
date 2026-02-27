import argparse
from collections import defaultdict
from datetime import date
from decimal import Decimal, InvalidOperation
import os
from pathlib import Path
from typing import Any

import pandas as pd
import psycopg
from psycopg.rows import dict_row
from slugify import slugify

DATABASE_URL = os.getenv('DATABASE_URL', 'postgresql://steam:steam@localhost:5432/steamgames')
SEED_DATASET_PATH = Path('data/seed/steam_games_seed.csv')

DIMENSION_COLUMNS = {
    'developers': 'developers',
    'publishers': 'publishers',
    'genres': 'genres',
    'tags': 'tags',
    'categories': 'categories',
}

JUNCTION_CONFIG = {
    'genres': ('game_genres', 'genre_id'),
    'tags': ('game_tags', 'tag_id'),
    'categories': ('game_categories', 'category_id'),
    'developers': ('game_developers', 'developer_id'),
    'publishers': ('game_publishers', 'publisher_id'),
}


def parse_pipe_list(value: Any) -> list[str]:
    if value is None:
        return []
    text = str(value).strip()
    if not text or text.lower() == 'nan':
        return []
    return [part.strip() for part in text.split('|') if part.strip()]


def parse_bool(value: Any) -> bool:
    if isinstance(value, bool):
        return value
    if value is None:
        return False
    text = str(value).strip().lower()
    return text in {'1', 'true', 't', 'yes', 'y'}


def parse_int(value: Any, default: int = 0) -> int:
    if value is None:
        return default
    text = str(value).strip()
    if not text or text.lower() == 'nan':
        return default
    try:
        return int(float(text))
    except ValueError:
        return default


def parse_decimal(value: Any) -> Decimal | None:
    if value is None:
        return None
    text = str(value).strip()
    if not text or text.lower() == 'nan':
        return None
    try:
        return Decimal(text)
    except InvalidOperation:
        return None


def parse_date(value: Any) -> date | None:
    if value is None:
        return None
    text = str(value).strip()
    if not text or text.lower() == 'nan':
        return None
    try:
        return pd.to_datetime(text, errors='coerce').date()
    except Exception:
        return None


def make_slug(name: str) -> str:
    return slugify(name, lowercase=True)


def load_dataset(input_csv: Path) -> pd.DataFrame:
    if not input_csv.exists():
        raise FileNotFoundError(f'Dataset not found: {input_csv}')

    df = pd.read_csv(input_csv)
    required_columns = {'steam_app_id', 'name'}
    missing = required_columns.difference(df.columns)
    if missing:
        raise ValueError(f'Missing required columns: {sorted(missing)}')

    cleaned = (
        df.dropna(subset=['steam_app_id', 'name'])
        .drop_duplicates(subset=['steam_app_id'])
        .copy()
    )
    cleaned['steam_app_id'] = pd.to_numeric(cleaned['steam_app_id'], errors='coerce')
    cleaned = cleaned.dropna(subset=['steam_app_id'])
    cleaned['steam_app_id'] = cleaned['steam_app_id'].astype('int64')
    return cleaned


def extract_dimensions(df: pd.DataFrame) -> dict[str, dict[str, str]]:
    values_by_table: dict[str, set[str]] = defaultdict(set)

    for table_name, column_name in DIMENSION_COLUMNS.items():
        if column_name not in df.columns:
            continue
        for raw in df[column_name].tolist():
            for item in parse_pipe_list(raw):
                values_by_table[table_name].add(item)

    result: dict[str, dict[str, str]] = {}
    for table_name, names in values_by_table.items():
        result[table_name] = {name: make_slug(name) for name in sorted(names)}
    return result


def upsert_dimension_table(conn: psycopg.Connection, table_name: str, values: dict[str, str]) -> None:
    if not values:
        return

    sql = f"INSERT INTO {table_name} (name, slug) VALUES (%s, %s) ON CONFLICT (name) DO NOTHING;"
    rows = [(name, slug) for name, slug in values.items()]
    with conn.cursor() as cur:
        cur.executemany(sql, rows)


def fetch_dimension_ids(conn: psycopg.Connection, table_name: str) -> dict[str, int]:
    with conn.cursor() as cur:
        cur.execute(f'SELECT id, name FROM {table_name};')
        rows = cur.fetchall()
    return {row[1]: row[0] for row in rows}


def build_game_rows(df: pd.DataFrame) -> list[tuple[Any, ...]]:
    rows: list[tuple[Any, ...]] = []
    for record in df.to_dict(orient='records'):
        is_free = parse_bool(record.get('is_free'))
        price = Decimal('0') if is_free else parse_decimal(record.get('price_usd'))
        rows.append(
            (
                int(record['steam_app_id']),
                str(record.get('name') or '').strip(),
                record.get('short_description'),
                record.get('detailed_description'),
                parse_date(record.get('release_date')),
                price,
                is_free,
                parse_int(record.get('metacritic_score'), default=0) or None,
                parse_int(record.get('positive_reviews'), default=0),
                parse_int(record.get('negative_reviews'), default=0),
                parse_int(record.get('required_age'), default=0),
                record.get('website'),
                record.get('header_image'),
                parse_bool(record.get('windows', True)),
                parse_bool(record.get('mac')),
                parse_bool(record.get('linux')),
            )
        )
    return rows


def upsert_games(conn: psycopg.Connection, game_rows: list[tuple[Any, ...]]) -> None:
    if not game_rows:
        return

    sql = """
    INSERT INTO games (
        steam_app_id,
        name,
        short_description,
        detailed_description,
        release_date,
        price_usd,
        is_free,
        metacritic_score,
        positive_reviews,
        negative_reviews,
        required_age,
        website,
        header_image,
        windows,
        mac,
        linux
    )
    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
    ON CONFLICT (steam_app_id) DO UPDATE SET
        name = EXCLUDED.name,
        short_description = EXCLUDED.short_description,
        detailed_description = EXCLUDED.detailed_description,
        release_date = EXCLUDED.release_date,
        price_usd = EXCLUDED.price_usd,
        is_free = EXCLUDED.is_free,
        metacritic_score = EXCLUDED.metacritic_score,
        positive_reviews = EXCLUDED.positive_reviews,
        negative_reviews = EXCLUDED.negative_reviews,
        required_age = EXCLUDED.required_age,
        website = EXCLUDED.website,
        header_image = EXCLUDED.header_image,
        windows = EXCLUDED.windows,
        mac = EXCLUDED.mac,
        linux = EXCLUDED.linux;
    """

    with conn.cursor() as cur:
        cur.executemany(sql, game_rows)


def fetch_game_ids(conn: psycopg.Connection, steam_app_ids: list[int]) -> dict[int, int]:
    with conn.cursor() as cur:
        cur.execute('SELECT id, steam_app_id FROM games WHERE steam_app_id = ANY(%s);', (steam_app_ids,))
        rows = cur.fetchall()
    return {row[1]: row[0] for row in rows}


def insert_junction_rows(conn: psycopg.Connection, table_name: str, foreign_key: str, rows: list[tuple[int, int]]) -> None:
    if not rows:
        return
    sql = f"INSERT INTO {table_name} (game_id, {foreign_key}) VALUES (%s, %s) ON CONFLICT DO NOTHING;"
    with conn.cursor() as cur:
        cur.executemany(sql, rows)


def build_junction_rows(
    df: pd.DataFrame,
    game_ids_by_app_id: dict[int, int],
    dim_ids_by_table: dict[str, dict[str, int]],
) -> dict[str, list[tuple[int, int]]]:
    rows_by_table: dict[str, list[tuple[int, int]]] = defaultdict(list)

    for record in df.to_dict(orient='records'):
        app_id = int(record['steam_app_id'])
        game_id = game_ids_by_app_id.get(app_id)
        if game_id is None:
            continue

        for dimension_table, column in DIMENSION_COLUMNS.items():
            values = parse_pipe_list(record.get(column))
            for value in values:
                dimension_id = dim_ids_by_table.get(dimension_table, {}).get(value)
                if dimension_id is None:
                    continue
                junction_table, _ = JUNCTION_CONFIG[dimension_table]
                rows_by_table[junction_table].append((game_id, dimension_id))

    return rows_by_table


def run_import(input_csv: Path, dry_run: bool) -> None:
    df = load_dataset(input_csv)
    dimensions = extract_dimensions(df)
    game_rows = build_game_rows(df)

    print(f'Loaded {len(df)} game rows from {input_csv}')
    for table_name in DIMENSION_COLUMNS:
        print(f'{table_name}: {len(dimensions.get(table_name, {}))} unique names')

    if dry_run:
        print(f'games rows prepared: {len(game_rows)}')
        print('Dry-run enabled: skipping database writes.')
        return

    with psycopg.connect(DATABASE_URL, row_factory=dict_row) as conn:
        for table_name in DIMENSION_COLUMNS:
            upsert_dimension_table(conn, table_name, dimensions.get(table_name, {}))

        upsert_games(conn, game_rows)

        steam_ids = [int(row[0]) for row in game_rows]
        game_ids_by_app_id = fetch_game_ids(conn, steam_ids)
        dim_ids = {table: fetch_dimension_ids(conn, table) for table in DIMENSION_COLUMNS}
        junction_rows = build_junction_rows(df, game_ids_by_app_id, dim_ids)

        for dimension_table, (junction_table, foreign_key) in JUNCTION_CONFIG.items():
            insert_junction_rows(conn, junction_table, foreign_key, junction_rows.get(junction_table, []))

        refresh_search_vectors(conn)
        conn.commit()

    print('Game and dimension import complete.')


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description='Import Steam game dataset into PostgreSQL.')
    parser.add_argument('--mode', choices=['seed', 'full'], default='seed', help='seed uses committed sample data, full uses your local full CSV.')
    parser.add_argument('--input', type=Path, default=None, help='Optional dataset path. Required when --mode full.')
    parser.add_argument('--dry-run', action='store_true', help='Load and normalize only; skip DB writes.')
    return parser.parse_args()


def resolve_input_path(mode: str, input_path: Path | None) -> Path:
    if input_path is not None:
        return input_path
    if mode == 'seed':
        return SEED_DATASET_PATH
    raise ValueError('--input is required when --mode full')


def refresh_search_vectors(conn: psycopg.Connection) -> None:
    with conn.cursor() as cur:
        cur.execute(
            """
            UPDATE games g
            SET search_vector =
                setweight(to_tsvector('english', COALESCE(g.name, '')), 'A') ||
                setweight(to_tsvector('english', COALESCE(g.short_description, '')), 'B') ||
                setweight(
                    to_tsvector(
                        'english',
                        COALESCE(
                            (
                                SELECT string_agg(t.name, ' ')
                                FROM game_tags gt
                                JOIN tags t ON t.id = gt.tag_id
                                WHERE gt.game_id = g.id
                            ),
                            ''
                        )
                    ),
                    'C'
                );
            """
        )


def main() -> None:
    args = parse_args()
    input_path = resolve_input_path(args.mode, args.input)
    run_import(input_path, args.dry_run)


if __name__ == '__main__':
    main()
