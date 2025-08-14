#!/usr/bin/env python3
from pathlib import Path
import pandas as pd

ROOT = Path(__file__).resolve().parents[2]
RESULTS = ROOT / "results"
OUT_ALL = RESULTS / "ALL_RESULTS.csv"

def gather():
    rows = []
    for solver_dir in RESULTS.iterdir():
        if not solver_dir.is_dir():
            continue
        if solver_dir.name == "plots":
            continue
        csv_path = solver_dir / "processed" / "metrics.csv"
        if csv_path.exists():
            df = pd.read_csv(csv_path)
            df["solver"] = solver_dir.name
            rows.append(df)
    if not rows:
        raise SystemExit("No results found. Run benchmarks first.")
    all_df = pd.concat(rows, ignore_index=True)
    all_df.to_csv(OUT_ALL, index=False)
    print(f"Wrote {OUT_ALL} with {len(all_df)} rows.")

if __name__ == "__main__":
    gather()

