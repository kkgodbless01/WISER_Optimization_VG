#!/usr/bin/env python3
from pathlib import Path
import pandas as pd
import matplotlib.pyplot as plt

ROOT = Path(__file__).resolve().parents[2]
RESULTS = ROOT / "results"
ALL = RESULTS / "ALL_RESULTS.csv"
PLOTS = RESULTS / "plots"
PLOTS.mkdir(exist_ok=True)

def main():
    if not ALL.exists():
        raise SystemExit("ALL_RESULTS.csv not found. Run aggregator first.")
    df = pd.read_csv(ALL)

    plt.figure(figsize=(7,5))
    for solver, g in df.groupby("solver"):
        plt.scatter(g["runtime_s"], g["
