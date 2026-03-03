#!/usr/bin/env python3
"""
Generate a seed CSV from fronkongames/steam-games-dataset using kagglehub.

This script also detects a common issue where the dataset is "shifted left"
(i.e. AppID is missing in the underlying file, so Name ends up under AppID, etc.)
and fixes it by:
  - shifting column labels left by one
  - dropping the final empty column
  - inserting a synthetic numeric AppID suitable for Postgres primary keys

Prereqs:
  pip install -U pandas kagglehub[pandas-datasets]

Usage:
  python make_seed.py
  python make_seed.py --file_path "steam_games.csv" --n 1000 --out seed.csv
  python make_seed.py --no_autofix   # if you want to disable the auto-fix
"""

from __future__ import annotations

import argparse
from pathlib import Path
import pandas as pd

import kagglehub
from kagglehub import KaggleDatasetAdapter


DATASET = "fronkongames/steam-games-dataset"


def _auto_detect_file_path(dataset: str) -> str:
    """Download dataset and pick the first CSV/Parquet we find."""
    local_dir = Path(kagglehub.dataset_download(dataset))
    candidates: list[Path] = []
    for ext in (".csv", ".parquet", ".pq"):
        candidates.extend(sorted(local_dir.rglob(f"*{ext}")))

    if not candidates:
        raise RuntimeError(f"No .csv/.parquet files found in: {local_dir}")

    rel = candidates[0].relative_to(local_dir)
    return str(rel)


def _looks_like_shifted_left(df: pd.DataFrame) -> bool:
    """
    Heuristic:
      - AppID should be mostly numeric
      - Name should NOT look like a date
    If AppID is mostly non-numeric and Name looks like "Apr 22, 2022" for many rows,
    assume the dataset is shifted-left (missing AppID in the underlying file).
    """
    if "AppID" not in df.columns or "Name" not in df.columns:
        return False

    appid = df["AppID"].astype(str).str.strip()
    name = df["Name"].astype(str).str.strip()

    pct_appid_numeric = appid.str.fullmatch(r"\d+").mean()
    pct_name_dateish = name.str.fullmatch(r"[A-Za-z]{3} \d{1,2}, \d{4}").mean()

    # Tuneable thresholds; these work well for your observed output.
    return (pct_appid_numeric < 0.20) and (pct_name_dateish > 0.10)


def _fix_shifted_left(df: pd.DataFrame) -> pd.DataFrame:
    """
    Re-map columns so:
      current AppID -> Name
      current Name -> Release date
      ...
      current Screenshots -> Movies
      current Movies -> (missing, drop)

    Then insert a synthetic numeric AppID at the front.
    """
    cols = list(df.columns)
    if len(cols) < 2:
        return df

    # Shift labels left by one; last becomes a placeholder we drop.
    shifted_cols = cols[1:] + ["__missing__"]
    df = df.copy()
    df.columns = shifted_cols

    # Drop placeholder if present
    if "__missing__" in df.columns:
        df = df.drop(columns=["__missing__"])

    # Insert synthetic AppID as an integer PK candidate.
    # Use stable IDs based on row order in this fixed DataFrame.
    # (Sampling happens later with a fixed random_state, so seeds remain reproducible.)
    df.insert(0, "AppID", range(1, len(df) + 1))

    return df


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--dataset", default=DATASET)
    parser.add_argument(
        "--file_path",
        default="",
        help="Path to file inside dataset (e.g. 'steam_games.csv'). Leave blank to auto-detect.",
    )
    parser.add_argument("--n", type=int, default=1000, help="Number of rows to sample.")
    parser.add_argument("--seed", type=int, default=42, help="Random seed for reproducibility.")
    parser.add_argument("--out", default="steam_games_seed_1000.csv", help="Output CSV filename.")
    parser.add_argument(
        "--no_autofix",
        action="store_true",
        help="Disable the automatic 'shifted-left' fix.",
    )
    args = parser.parse_args()

    file_path = args.file_path.strip() or _auto_detect_file_path(args.dataset)
    if not args.file_path.strip():
        print(f"[info] Auto-detected file_path: {file_path}")

    print(f"[info] Loading dataset={args.dataset} file_path={file_path}")
    df = kagglehub.load_dataset(
        KaggleDatasetAdapter.PANDAS,
        args.dataset,
        file_path,
    )

    if not isinstance(df, pd.DataFrame):
        raise TypeError(f"Expected DataFrame, got: {type(df)}")

    print(f"[info] Loaded rows={len(df):,} cols={len(df.columns):,}")

    if not args.no_autofix and _looks_like_shifted_left(df):
        print("[warn] Detected shifted-left dataset (AppID likely missing). Applying fix…")
        df = _fix_shifted_left(df)
        print(f"[info] After fix: rows={len(df):,} cols={len(df.columns):,}")
        print(f"[info] First columns now: {df.columns[:6].tolist()}")

    n = min(args.n, len(df))
    seed_df = df.sample(n=n, random_state=args.seed)

    out_path = Path(args.out).resolve()
    seed_df.to_csv(out_path, index=False)
    print(f"[info] Wrote seed CSV: {out_path} (rows={len(seed_df):,})")
    print("[info] Preview:")
    print(seed_df.head(3).to_string(index=False))

    return 0


if __name__ == "__main__":
    raise SystemExit(main())