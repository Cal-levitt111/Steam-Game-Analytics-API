#!/usr/bin/env python3
"""
Generate a 1000-row seed CSV from fronkongames/steam-games-dataset using kagglehub.

Prereqs:
  pip install -U pandas kagglehub[pandas-datasets]

Auth:
  kagglehub uses your Kaggle credentials. Typically:
  - Put kaggle.json in ~/.kaggle/kaggle.json (chmod 600)
  OR
  - Set env vars KAGGLE_USERNAME / KAGGLE_KEY

Usage:
  python make_seed.py
  python make_seed.py --file_path "steam_games.csv" --n 1000 --out steam_seed_1000.csv
"""

from __future__ import annotations

import argparse
import os
from pathlib import Path
import pandas as pd

import kagglehub
from kagglehub import KaggleDatasetAdapter


DATASET = "fronkongames/steam-games-dataset"


def _auto_detect_file_path(dataset: str) -> str:
    """
    If you don't know the exact file_path inside the Kaggle dataset,
    download it and pick the first CSV/Parquet we find.
    """
    local_dir = Path(kagglehub.dataset_download(dataset))
    candidates = []
    for ext in (".csv", ".parquet", ".pq"):
        candidates.extend(sorted(local_dir.rglob(f"*{ext}")))

    if not candidates:
        raise RuntimeError(
            f"No .csv/.parquet files found after downloading dataset into: {local_dir}"
        )

    # kagglehub.load_dataset expects the path *inside* the dataset, but in practice
    # passing the filename works for many KaggleHub datasets. We'll pass the relative path.
    rel = candidates[0].relative_to(local_dir)
    return str(rel)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--dataset", default=DATASET)
    parser.add_argument("--file_path", default="", help="Path to file inside dataset (e.g. 'steam_games.csv'). Leave blank to auto-detect.")
    parser.add_argument("--n", type=int, default=1000, help="Number of rows to sample.")
    parser.add_argument("--seed", type=int, default=42, help="Random seed for reproducibility.")
    parser.add_argument("--out", default="steam_games_seed_1000.csv", help="Output CSV filename.")
    parser.add_argument("--ensure_unique", default="", help="Optional column name to enforce uniqueness on (e.g. 'app_id').")
    args = parser.parse_args()

    file_path = args.file_path.strip()
    if not file_path:
        file_path = _auto_detect_file_path(args.dataset)
        print(f"[info] Auto-detected file_path: {file_path}")

    print(f"[info] Loading dataset={args.dataset} file_path={file_path}")
    df = kagglehub.load_dataset(
        KaggleDatasetAdapter.PANDAS,
        args.dataset,
        file_path,
        # You can pass pandas_kwargs here if needed, e.g.:
        # pandas_kwargs={"dtype_backend": "pyarrow"}  # pandas >= 2.0
    )

    if not isinstance(df, pd.DataFrame):
        raise TypeError(f"Expected DataFrame, got: {type(df)}")

    print(f"[info] Loaded rows={len(df):,} cols={len(df.columns):,}")

    n = min(args.n, len(df))
    seed_df = df.sample(n=n, random_state=args.seed)

    # Optional: enforce uniqueness on a key column (useful for Postgres primary keys)
    if args.ensure_unique:
        col = args.ensure_unique
        if col not in seed_df.columns:
            raise ValueError(f"--ensure_unique column '{col}' not found in dataset columns.")
        # Drop duplicates, then top-up if we fell below n (best-effort)
        seed_df = seed_df.drop_duplicates(subset=[col])
        if len(seed_df) < n:
            remaining = df[~df[col].isin(seed_df[col])].sample(
                n=min(n - len(seed_df), len(df)),
                random_state=args.seed,
            )
            seed_df = pd.concat([seed_df, remaining], ignore_index=True).head(n)

    out_path = Path(args.out).resolve()
    seed_df.to_csv(out_path, index=False)
    print(f"[info] Wrote seed CSV: {out_path} (rows={len(seed_df):,})")

    # Helpful quick sanity output
    print("[info] Sample preview:")
    print(seed_df.head(3).to_string(index=False))

    return 0


if __name__ == "__main__":
    raise SystemExit(main())