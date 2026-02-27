import argparse
from pathlib import Path

import pandas as pd


DEFAULT_SIZE = 500
DEFAULT_SEED = 42


def create_seed_sample(input_csv: Path, output_csv: Path, sample_size: int, random_seed: int) -> int:
    if not input_csv.exists():
        raise FileNotFoundError(f'Input dataset not found: {input_csv}')

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

    if sample_size >= len(cleaned):
        sampled = cleaned.sort_values('steam_app_id')
    else:
        sampled = cleaned.sample(n=sample_size, random_state=random_seed).sort_values('steam_app_id')

    output_csv.parent.mkdir(parents=True, exist_ok=True)
    sampled.to_csv(output_csv, index=False)
    return len(sampled)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description='Create deterministic seed sample from full Steam dataset.')
    parser.add_argument('--input', required=True, type=Path, help='Path to full Kaggle Steam dataset CSV.')
    parser.add_argument('--output', default=Path('data/seed/steam_games_seed.csv'), type=Path, help='Output path.')
    parser.add_argument('--size', default=DEFAULT_SIZE, type=int, help='Number of rows in the sample.')
    parser.add_argument('--seed', default=DEFAULT_SEED, type=int, help='Random seed.')
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    rows = create_seed_sample(args.input, args.output, args.size, args.seed)
    print(f'Wrote {rows} seed rows to {args.output}')


if __name__ == '__main__':
    main()