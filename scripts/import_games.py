import argparse
import ast
from collections import defaultdict
from datetime import date
from decimal import Decimal, InvalidOperation
import os
from pathlib import Path
from typing import Any

import pandas as pd
import psycopg
from slugify import slugify

DATABASE_URL = os.getenv('DATABASE_URL', 'postgresql://steam:steam@localhost:5432/steamgames')
SEED_DATASET_CANDIDATES = [
    Path('data/seed/steam_games_seed.csv'),
    Path('data/seed/steam_game_seed_1000_2.csv'),
]
SEED_DATASET_DIR = Path('data/seed')

COLUMN_ALIASES = {
    'AppID': 'steam_app_id',
    'Name': 'name',
    'Release date': 'release_date',
    'Estimated owners': 'estimated_owners',
    'Peak CCU': 'peak_ccu',
    'Required age': 'required_age',
    'Price': 'price_usd',
    'Discount': 'discount_percent',
    'DLC count': 'dlc_count',
    'About the game': 'about_the_game',
    'Supported languages': 'supported_languages',
    'Full audio languages': 'full_audio_languages',
    'Reviews': 'reviews',
    'Header image': 'header_image',
    'Website': 'website',
    'Support url': 'support_url',
    'Support email': 'support_email',
    'Windows': 'windows',
    'Mac': 'mac',
    'Linux': 'linux',
    'Metacritic score': 'metacritic_score',
    'Metacritic url': 'metacritic_url',
    'User score': 'user_score',
    'Positive': 'positive_reviews',
    'Negative': 'negative_reviews',
    'Score rank': 'score_rank',
    'Achievements': 'achievements',
    'Recommendations': 'recommendations',
    'Notes': 'notes',
    'Average playtime forever': 'average_playtime_forever',
    'Average playtime two weeks': 'average_playtime_two_weeks',
    'Median playtime forever': 'median_playtime_forever',
    'Median playtime two weeks': 'median_playtime_two_weeks',
    'Developers': 'developers',
    'Publishers': 'publishers',
    'Categories': 'categories',
    'Genres': 'genres',
    'Tags': 'tags',
    'Screenshots': 'screenshots',
    'Movies': 'movies',
}

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

GAME_UPSERT_COLUMNS = [
    'steam_app_id',
    'name',
    'short_description',
    'detailed_description',
    'release_date',
    'estimated_owners',
    'peak_ccu',
    'price_usd',
    'discount_percent',
    'dlc_count',
    'about_the_game',
    'is_free',
    'supported_languages',
    'full_audio_languages',
    'reviews',
    'support_url',
    'support_email',
    'metacritic_score',
    'metacritic_url',
    'user_score',
    'positive_reviews',
    'negative_reviews',
    'score_rank',
    'achievements',
    'recommendations',
    'notes',
    'average_playtime_forever',
    'average_playtime_two_weeks',
    'median_playtime_forever',
    'median_playtime_two_weeks',
    'required_age',
    'website',
    'header_image',
    'windows',
    'mac',
    'linux',
    'screenshots',
    'movies',
]


def clean_text(value: Any) -> str | None:
    if value is None:
        return None
    text = str(value).strip()
    if not text or text.lower() == 'nan':
        return None
    return text


def parse_multi_list(value: Any) -> list[str]:
    if value is None:
        return []

    if isinstance(value, (list, tuple, set)):
        items = list(value)
    else:
        text = clean_text(value)
        if text is None:
            return []

        if text.startswith('[') and text.endswith(']'):
            try:
                parsed = ast.literal_eval(text)
                if isinstance(parsed, (list, tuple, set)):
                    items = list(parsed)
                else:
                    items = [text]
            except (ValueError, SyntaxError):
                items = [text]
        elif '|' in text:
            items = text.split('|')
        elif ',' in text:
            items = text.split(',')
        else:
            items = [text]

    cleaned: list[str] = []
    for item in items:
        token = clean_text(item)
        if token is None:
            continue
        token = token.strip("'").strip('"').strip()
        if token and token.lower() != 'nan':
            cleaned.append(token)
    return cleaned


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


def parse_int_optional(value: Any) -> int | None:
    if value is None:
        return None
    text = str(value).strip()
    if not text or text.lower() == 'nan':
        return None
    try:
        return int(float(text))
    except ValueError:
        return None


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


def normalize_dataset_columns(df: pd.DataFrame) -> pd.DataFrame:
    rename_map = {source: target for source, target in COLUMN_ALIASES.items() if source in df.columns}
    normalized = df.rename(columns=rename_map).copy()

    if 'about_the_game' in normalized.columns:
        if 'short_description' not in normalized.columns:
            normalized['short_description'] = normalized['about_the_game']
        else:
            normalized['short_description'] = normalized['short_description'].fillna(normalized['about_the_game'])

        if 'detailed_description' not in normalized.columns:
            normalized['detailed_description'] = normalized['about_the_game']
        else:
            normalized['detailed_description'] = normalized['detailed_description'].fillna(normalized['about_the_game'])

    if 'is_free' not in normalized.columns:
        if 'price_usd' in normalized.columns:
            price_values = pd.to_numeric(normalized['price_usd'], errors='coerce')
            normalized['is_free'] = price_values.fillna(-1).eq(0)
        else:
            normalized['is_free'] = False

    expected = set(GAME_UPSERT_COLUMNS).union(DIMENSION_COLUMNS.values())
    for column in expected:
        if column not in normalized.columns:
            normalized[column] = None

    return normalized


def load_dataset(input_csv: Path) -> pd.DataFrame:
    if not input_csv.exists():
        raise FileNotFoundError(f'Dataset not found: {input_csv}')

    df = pd.read_csv(input_csv)
    df = normalize_dataset_columns(df)

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
            for item in parse_multi_list(raw):
                values_by_table[table_name].add(item)

    result: dict[str, dict[str, str]] = {}
    for table_name, names in values_by_table.items():
        result[table_name] = {name: make_slug(name) for name in sorted(names)}
    return result


def upsert_dimension_table(conn: psycopg.Connection, table_name: str, values: dict[str, str]) -> None:
    if not values:
        return

    with conn.cursor() as cur:
        cur.execute(f'SELECT name, slug FROM {table_name};')
        existing_rows = cur.fetchall()
        existing_names = {row[0] for row in existing_rows}
        existing_slugs = {row[1] for row in existing_rows}

        rows: list[tuple[str, str]] = []
        for name, requested_slug in values.items():
            if name in existing_names:
                continue

            base_slug = requested_slug or make_slug(name) or 'item'
            slug = base_slug
            suffix = 2
            while slug in existing_slugs:
                slug = f'{base_slug}-{suffix}'
                suffix += 1

            rows.append((name, slug))
            existing_slugs.add(slug)

        if not rows:
            return

        sql = f"INSERT INTO {table_name} (name, slug) VALUES (%s, %s) ON CONFLICT (name) DO NOTHING;"
        cur.executemany(sql, rows)


def fetch_dimension_ids(conn: psycopg.Connection, table_name: str) -> dict[str, int]:
    with conn.cursor() as cur:
        cur.execute(f'SELECT id, name FROM {table_name};')
        rows = cur.fetchall()
    return {row[1]: row[0] for row in rows}


def build_game_rows(df: pd.DataFrame) -> list[tuple[Any, ...]]:
    rows: list[tuple[Any, ...]] = []
    for record in df.to_dict(orient='records'):
        price = parse_decimal(record.get('price_usd'))
        derived_is_free = price == Decimal('0') if price is not None else False
        is_free = parse_bool(record.get('is_free')) or derived_is_free
        if is_free and price is None:
            price = Decimal('0')

        about_the_game = clean_text(record.get('about_the_game'))
        short_description = clean_text(record.get('short_description')) or about_the_game
        detailed_description = clean_text(record.get('detailed_description')) or about_the_game

        row = (
            int(record['steam_app_id']),
            str(record.get('name') or '').strip(),
            short_description,
            detailed_description,
            parse_date(record.get('release_date')),
            clean_text(record.get('estimated_owners')),
            parse_int_optional(record.get('peak_ccu')),
            price,
            parse_int_optional(record.get('discount_percent')),
            parse_int_optional(record.get('dlc_count')),
            about_the_game,
            is_free,
            clean_text(record.get('supported_languages')),
            clean_text(record.get('full_audio_languages')),
            clean_text(record.get('reviews')),
            clean_text(record.get('support_url')),
            clean_text(record.get('support_email')),
            parse_int(record.get('metacritic_score'), default=0),
            clean_text(record.get('metacritic_url')),
            parse_int_optional(record.get('user_score')),
            parse_int(record.get('positive_reviews'), default=0),
            parse_int(record.get('negative_reviews'), default=0),
            clean_text(record.get('score_rank')),
            parse_int_optional(record.get('achievements')),
            parse_int_optional(record.get('recommendations')),
            clean_text(record.get('notes')),
            parse_int_optional(record.get('average_playtime_forever')),
            parse_int_optional(record.get('average_playtime_two_weeks')),
            parse_int_optional(record.get('median_playtime_forever')),
            parse_int_optional(record.get('median_playtime_two_weeks')),
            parse_int(record.get('required_age'), default=0),
            clean_text(record.get('website')),
            clean_text(record.get('header_image')),
            parse_bool(record.get('windows', True)),
            parse_bool(record.get('mac')),
            parse_bool(record.get('linux')),
            clean_text(record.get('screenshots')),
            clean_text(record.get('movies')),
        )
        rows.append(row)
    return rows


def upsert_games(conn: psycopg.Connection, game_rows: list[tuple[Any, ...]]) -> None:
    if not game_rows:
        return

    insert_columns = ',\n        '.join(GAME_UPSERT_COLUMNS)
    placeholders = ', '.join(['%s'] * len(GAME_UPSERT_COLUMNS))
    update_columns = ',\n        '.join(
        f'{column} = EXCLUDED.{column}' for column in GAME_UPSERT_COLUMNS if column != 'steam_app_id'
    )

    sql = f"""
    INSERT INTO games (
        {insert_columns}
    )
    VALUES ({placeholders})
    ON CONFLICT (steam_app_id) DO UPDATE SET
        {update_columns};
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
            values = parse_multi_list(record.get(column))
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

    with psycopg.connect(DATABASE_URL) as conn:
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
    parser.add_argument(
        '--mode',
        choices=['seed', 'full'],
        default='seed',
        help='seed uses committed sample data, full uses your local full CSV.',
    )
    parser.add_argument('--input', type=Path, default=None, help='Optional dataset path. Required when --mode full.')
    parser.add_argument('--dry-run', action='store_true', help='Load and normalize only; skip DB writes.')
    return parser.parse_args()


def resolve_input_path(mode: str, input_path: Path | None) -> Path:
    if input_path is not None:
        return input_path

    if mode == 'seed':
        for candidate in SEED_DATASET_CANDIDATES:
            if candidate.exists():
                return candidate
        csv_files = sorted(SEED_DATASET_DIR.glob('*.csv'))
        if csv_files:
            return csv_files[0]
        raise FileNotFoundError(f'No seed csv files found in: {SEED_DATASET_DIR}')

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
