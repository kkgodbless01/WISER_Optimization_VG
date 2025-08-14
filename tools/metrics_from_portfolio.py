#!/usr/bin/env python3
import json, math, glob, os, re
from typing import Dict, Tuple, Optional

TABLE_MD = "results/comparison_tables/solver_vs_baseline.md"

def load_json(path: str) -> Optional[dict]:
    try:
        with open(path, "r") as f:
            return json.load(f)
    except Exception:
        return None

def autodetect_runs() -> Tuple[Optional[str], Optional[str]]:
    # Prefer explicit names, else the most recent matching pattern
    solver = None
    baseline = None
    # Common patterns
    candidates = sorted(glob.glob("results/solver_runs/*_solver.json")) + sorted(glob.glob("results/solver_runs/*solver*.json"))
    if candidates:
        solver = max(candidates, key=os.path.getmtime)
    candidates = sorted(glob.glob("results/solver_runs/*_baseline.json")) + sorted(glob.glob("results/solver_runs/*baseline*.json"))
    if candidates:
        baseline = max(candidates, key=os.path.getmtime)
    return solver, baseline

def extract_struct(d: dict):
    """
    Try multiple key conventions to find:
      - targets: {bucket: {char: value}}
      - achieved: {bucket: {char: value}}   (portfolio features)
      - guardrails: {violations:int, total:int} or list of constraints with 'satisfied' boolean
      - objective: float
      - runtime: float seconds (optional)
    """
    targets = d.get("targets") or d.get("Ktarget") or d.get("target") or {}
    achieved = d.get("achieved") or d.get("characteristics") or d.get("portfolio") or {}
    objective = d.get("objective") or d.get("obj") or None
    runtime = d.get("runtime_sec") or d.get("runtime") or None

    # Normalize nested dicts to {bucket:{char:value}}
    def nest(obj):
        if isinstance(obj, dict) and all(isinstance(v, dict) for v in obj.values()):
            return obj
        # If flat list of features, bucket under "ALL"
        if isinstance(obj, dict):
            return {"ALL": obj}
        return {}

    targets = nest(targets)
    achieved = nest(achieved)

    # Guardrails
    guards = d.get("guardrails") or d.get("constraints") or {}
    violations = None
    total = None
    if isinstance(guards, dict):
        violations = guards.get("violations") or guards.get("viol_count") or None
        total = guards.get("total") or guards.get("count") or None
        # Maybe list under guards["items"]
        items = guards.get("items") if isinstance(guards.get("items"), list) else None
        if items and (violations is None or total is None):
            total = len(items)
            violations = sum(0 if (it.get("satisfied") is True) else 1 for it in items)
    elif isinstance(guards, list):
        total = len(guards)
        violations = sum(0 if (it.get("satisfied") is True) else 1 for it in guards)

    return targets, achieved, objective, runtime, (violations, total)

def relative_error(a: float, t: float) -> float:
    denom = abs(t) if abs(t) > 1e-12 else 1.0
    return abs(a - t) / denom

def compute_match_score(targets: Dict, achieved: Dict) -> float:
    """
    Compute 100 * (1 - avg relative error) across all (bucket,char) found in targets.
    If a feature is missing on achieved, skip it; if nothing found, return NaN.
    """
    errors = []
    for bucket, chars in targets.items():
        a_chars = achieved.get(bucket, {})
        for ch, t in (chars or {}).items():
            if ch in a_chars and isinstance(a_chars[ch], (int, float)) and isinstance(t, (int, float)):
                errors.append(relative_error(float(a_chars[ch]), float(t)))
    if not errors:
        return float("nan")
    avg_err = sum(errors) / len(errors)
    score = max(0.0, min(1.0, 1.0 - avg_err)) * 100.0
    return round(score, 1)

def compute_guardrail_score(violations: Optional[int], total: Optional[int]) -> float:
    if violations is None or total is None or total <= 0:
        return float("nan")
    ok = max(0, total - max(0, violations))
    return round((ok / total) * 100.0, 1)

def combine_accuracy(match: Optional[float], guard: Optional[float], w_match=0.7, w_guard=0.3) -> Optional[float]:
    parts = []
    weights = []
    if match is not None and not math.isnan(match):
        parts.append(match); weights.append(w_match)
    if guard is not None and not math.isnan(guard):
        parts.append(guard); weights.append(w_guard)
    if not parts:
        return None
    wsum = sum(weights)
    acc = sum(p*w for p, w in zip(parts, weights)) / (wsum if wsum else 1.0)
    return round(acc, 1)

def read_table_values(table_path: str):
    solver_rt = base_rt = solver_acc = base_acc = speedup = None
    if not os.path.isfile(table_path):
        return solver_rt, base_rt, solver_acc, base_acc, speedup
    with open(table_path, "r") as f:
        txt = f.read()
    def pick(label, col):
        m = re.search(rf"^\|\s*{label}\s*\|\s*([^|]+)\|\s*([^|]+)\|", txt, flags=re.M)
        if not m:
            return None
        return (m.group(1).strip(), m.group(2).strip())[col-1]
    solver_rt = pick("Average Runtime \\(s\\)", 1)
    base_rt   = pick("Average Runtime \\(s\\)", 2)
    solver_acc= pick("Solution Accuracy \\(\\%\\)", 1)
    base_acc  = pick("Solution Accuracy \\(\\%\\)", 2)
    speedup   = pick("Speedup Factor", 1)
    return solver_rt, base_rt, solver_acc, base_acc, speedup

def write_table(table_path: str, solver_rt, base_rt, solver_acc, base_acc, speedup):
    import datetime as dt
    ts = dt.datetime.utcnow().strftime("%Y-%m-%d %H:%M:%SZ")
    os.makedirs(os.path.dirname(table_path), exist_ok=True)
    with open(table_path, "w") as f:
        f.write(f"# Solver vs baseline\n\nUpdated: {ts}\n\n")
        f.write("| Metric                 | Solver | Baseline |\n")
        f.write("|------------------------|:------:|:--------:|\n")
        f.write(f"| Average Runtime (s)    | {solver_rt} | {base_rt} |\n")
        f.write(f"| Solution Accuracy (%)  | {solver_acc} | {base_acc} |\n")
        f.write(f"| Speedup Factor         | {speedup} | — |\n\n")
        f.write("Notes:\n")
        f.write('- Accuracy derived from portfolio–target match and guardrail satisfaction (weighted blend).\n')
        f.write("- Runtimes may come from logs or solver metadata.\n")

def coalesce(new_val: Optional[float], current: Optional[str]) -> str:
    # Keep existing value if new is missing; otherwise format numeric
    if new_val is None:
        return current if (current and current not in ["None", "pending", "—", "-"]) else "pending"
    return f"{new_val}"

def main():
    solver_path, base_path = autodetect_runs()
    solver = load_json(solver_path) if solver_path else None
    base = load_json(base_path) if base_path else None

    # Compute accuracy components where possible
    solver_acc = base_acc = None
    solver_rt = base_rt = None

    # Read current table to preserve values if we can't compute new ones
    cur_solver_rt, cur_base_rt, cur_solver_acc, cur_base_acc, cur_speedup = read_table_values(TABLE_MD)

    if solver:
        t,a,obj,rt,guards = extract_struct(solver)
        m = compute_match_score(t,a)
        g = compute_guardrail_score(*(guards if guards else (None, None)))
        solver_acc = combine_accuracy(m,g)
        if isinstance(rt, (int,float)):
            solver_rt = round(float(rt), 2)
    if base:
        t,a,obj,rt,guards = extract_struct(base)
        m = compute_match_score(t,a)
        g = compute_guardrail_score(*(guards if guards else (None, None)))
        base_acc = combine_accuracy(m,g)
        if isinstance(rt, (int,float)):
            base_rt = round(float(rt), 2)

    # Speedup if both runtimes exist
    speedup = None
    try:
        if solver_rt is not None and base_rt is not None and float(solver_rt) > 0:
            speedup = f"{round(float(base_rt)/float(solver_rt), 2)}×"
    except Exception:
        pass

    # Coalesce with current table values
    solver_rt_out = coalesce(solver_rt, cur_solver_rt)
    base_rt_out   = coalesce(base_rt,   cur_base_rt)
    solver_acc_out= coalesce(solver_acc,cur_solver_acc)
    base_acc_out  = coalesce(base_acc,  cur_base_acc)
    speedup_out   = (speedup if speedup is not None else (cur_speedup if cur_speedup else "—"))

    write_table(TABLE_MD, solver_rt_out, base_rt_out, solver_acc_out, base_acc_out, speedup_out)
    print("Wrote", TABLE_MD)

if __name__ == "__main__":
    main()
