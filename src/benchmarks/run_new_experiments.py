#!/usr/bin/env python3
import numpy as np
import pandas as pd
from pathlib import Path
from datetime import datetime

from solvers.solver_greedy import solve as solve_greedy
from solvers.solver_new1 import solve as solve_new1

ROOT = Path(__file__).resolve().parents[2]
RESULTS = ROOT / "results"
RESULTS.mkdir(exist_ok=True)

def make_instance(n: int, seed: int):
    rng = np.random.default_rng(seed)
    values = np.round(rng.uniform(10, 100, size=n), 2).tolist()
    weights = np.round(rng.uniform(1, 30, size=n), 2).tolist()
    capacity = float(np.round(sum(weights) * 0.4, 2))
    return values, weights, capacity

def write_row(solver_name: str, row: dict):
    out_dir = RESULTS / solver_name / "processed"
    out_dir.mkdir(parents=True, exist_ok=True)
    csv_path = out_dir / "metrics.csv"
    df_row = pd.DataFrame([{
        "solver": solver_name,
        "instance_id": row["instance_id"],
        "n_items": row["n_items"],
        "capacity": row["capacity"],
        "best_value": row["best_value"],
        "total_weight": row["total_weight"],
        "feasible": row["feasible"],
        "runtime_s": row["runtime_s"],
        "iterations": row["iterations"],
        "timestamp": datetime.utcnow().isoformat(timespec="seconds") + "Z",
    }])
    if csv_path.exists():
        df_row.to_csv(csv_path, mode="a", header=False, index=False)
    else:
        df_row.to_csv(csv_path, index=False)

def main():
    instances = [
        ("inst_n18_s1", *make_instance(18, 1)),
        ("inst_n22_s7", *make_instance(22, 7)),
        ("inst_n30_s13", *make_instance(30, 13)),
    ]
    for instance_id, values, weights, capacity in instances:
        g = solve_greedy(values, weights, capacity, instance_id)
        ns1 = solve_new1(values, weights, capacity, instance_id)
        write_row("greedy", g.__dict__)
        write_row("new_solver1", ns1.__dict__)
        print(f"Done: {instance_id} -> greedy value={g.best_value:.2f}, new_solver1 value={ns1.best_value:.2f}")

if __name__ == "__main__":
    main()

