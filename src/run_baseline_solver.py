#!/usr/bin/env python3
import argparse, json, os, sys, time
from datetime import datetime
from pathlib import Path

try:
    import pulp
except ImportError:
    print("PuLP not installed. Run: pip install pulp", file=sys.stderr)
    sys.exit(1)

def load_instance(path: Path):
    with open(path, "r") as f:
        data = json.load(f)
    # Required fields
    if "items" not in data or "capacity" not in data:
        raise ValueError("Instance JSON must contain 'items' (list of {id,value,weight}) and 'capacity' (number).")
    # Normalize
    for i, it in enumerate(data["items"]):
        if "id" not in it:
            it["id"] = f"item_{i}"
        for k in ("value", "weight"):
            if k not in it:
                raise ValueError(f"Item {it.get('id', i)} missing '{k}'")
    data["instance_id"] = data.get("instance_id", Path(path).stem)
    return data

def solve_knapsack_pulp(items, capacity):
    prob = pulp.LpProblem("baseline_knapsack", pulp.LpMaximize)
    x = {it["id"]: pulp.LpVariable(f"x_{it['id']}", lowBound=0, upBound=1, cat=pulp.LpBinary) for it in items}
    prob += pulp.lpSum(it["value"] * x[it["id"]] for it in items)
    prob += pulp.lpSum(it["weight"] * x[it["id"]] for it in items) <= capacity
    t0 = time.perf_counter()
    prob.solve(pulp.PULP_CBC_CMD(msg=False))
    t1 = time.perf_counter()

    status = pulp.LpStatus[prob.status]
    obj = pulp.value(prob.objective) if prob.status == pulp.LpStatusOptimal else None

    if prob.status == pulp.LpStatusOptimal:
        chosen = [i for i in x if pulp.value(x[i]) > 0.5]
    else:
        chosen = []

    total_weight = sum(
        next(it["weight"] for it in items if it["id"] == i) for i in chosen
    ) if chosen else 0.0

    return {
        "status": status,
        "objective_value": obj,
        "runtime_seconds": round(t1 - t0, 6),
        "selected_items": chosen,
        "selected_count": len(chosen),
        "total_weight": total_weight,
    }

def main():
    ap = argparse.ArgumentParser(description="Baseline solver runner (PuLP/CBC) for knapsack-like instances")
    ap.add_argument("instance", type=str, help="Path to JSON instance file")
    ap.add_argument("--outdir", type=str, default="results/baseline_runs", help="Directory to write result JSON")
    ap.add_argument("--tag", type=str, default="pulp", help="Solver tag to embed in output filename")
    args = ap.parse_args()

    instance_path = Path(args.instance)
    if not instance_path.exists():
        print(f"Instance not found: {instance_path}", file=sys.stderr)
        sys.exit(2)

    data = load_instance(instance_path)
    items, capacity = data["items"], data["capacity"]

    res = solve_knapsack_pulp(items, capacity)

    outdir = Path(args.outdir)
    outdir.mkdir(parents=True, exist_ok=True)

    ts = datetime.utcnow().strftime("%Y%m%dT%H%M%SZ")
    fname = f"{ts}_{data['instance_id']}_{args.tag}.json"
    out_path = outdir / fname

    payload = {
        "instance_id": data["instance_id"],
        "instance_path": str(instance_path),
        "solver": args.tag,
        "metrics": res,
        "capacity": capacity,
        "n_items": len(items),
        "cwd": os.getcwd(),
        "timestamp_utc": ts,
    }

    with open(out_path, "w") as f:
        json.dump(payload, f, indent=2)

    print(f"Wrote: {out_path}")
    print(json.dumps(payload["metrics"], indent=2))

if __name__ == "__main__":
    main()

