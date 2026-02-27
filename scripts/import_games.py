import argparse
from collections import defaultdict
import os
from pathlib import Path
from typing import Any

import pandas as pd
import psycopg
from psycopg.rows import dict_row
from slugify import slugify

DATABASE_URL = os.getenv('DATABASE_URL', 'postgresql://steam:steam@localhost:5432/steamgames')


DIMENSION_COLUMNS = {
    'developers': 'developers',
    'publishers': 'publishers',
    'genres': 'genres',
    'tags': 'tags',
    'categories': 'categories',
}


def parse_pipe_list(value: Any) -> list[str]:
    if value is None:
        return []
    text = str(value).strip()
    if not text or text.lower() == 'nan':
        return []
    return [part.strip() for part in text.split('|') if part.strip()]


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


def run_dimension_import(input_csv: Path, dry_run: bool) -> None:
    df = load_dataset(input_csv)
    dimensions = extract_dimensions(df)

    print(f'Loaded {len(df)} game rows from {input_csv}')
    for table_name in DIMENSION_COLUMNS:
        print(f'{table_name}: {len(dimensions.get(table_name, {}))} unique names')

    if dry_run:
        print('Dry-run enabled: skipping database writes.')
        return

    with psycopg.connect(DATABASE_URL, row_factory=dict_row) as conn:
        for table_name in DIMENSION_COLUMNS:
            upsert_dimension_table(conn, table_name, dimensions.get(table_name, {}))
        conn.commit()

    print('Dimension upserts complete.')


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description='Import Steam game dataset into PostgreSQL.')
    parser.add_argument('--input', type=Path, required=True, help='Path to CSV dataset to import.')
    parser.add_argument('--dry-run', action='store_true', help='Load and normalize only; skip DB writes.')
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    run_dimension_import(args.input, args.dry_run)


if __name__ == '__main__':
    main()
