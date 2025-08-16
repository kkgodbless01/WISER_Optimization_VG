#!/usr/bin/env python3
import os, json, re
from datetime import datetime

ROOT = os.path.dirname(os.path.abspath(__file__))
RES = os.path.join(ROOT, "results")
SOLVER_DIR = os.path.join(RES, "solver_runs")
BASELINE_DIR = os.path.join(RES, "baseline_runs")
OUT_DIR = os.path.join(RES, "comparison_tables")
OUT_PATH = os.path.join(OUT_DIR, "solver_vs_baseline.md")

os.makedirs(OUT_DIR, exist_ok=True)

TIMESTAMP_RE = re.compile(r"^\d{8}T\d{6}Z_")
SUFFIX_RE = re.compile(r"_(pulp|solver|baseline)$", re.IGNORECASE)

def norm_instance_from_name(name: str) -> str:
    stem = os.path.splitext(os.path.basename(name))[0]
    stem = TIMESTAMP_RE.sub("", stem)
    stem = SUFFIX_RE.sub("", stem)
    return stem

def dig(d, path):
    cur = d
    for p in path.split("."):
        if isinstance(cur, dict) and p in cur:
            cur = cur[p]
        else:
            return None
    return cur

def first(d, keys):
    for k in keys:
        v = dig(d, k) if "." in k else d.get(k)
        if v is not None:
            return v
    return None

def to_float(x):
    try:
        return float(x)
    except Exception:
        return None

def load_records(folder, is_baseline_hint=False):
    recs = []
    if not os.path.isdir(folder):
        return recs
    for fn in os.listdir(folder):
        if not fn.endswith(".json"):
            continue
        path = os.path.join(folder, fn)
        try:
            with open(path, "r") as f:
                data = json.load(f)
        except Exception:
            continue

        inst = first(data, ["instance", "Instance", "instance_id"])
        if not inst:
            inst = norm_instance_from_name(fn)
        norm_inst = norm_instance_from_name(inst)

        solver = first(data, ["solver", "metrics.solver"]) or ("baseline" if is_baseline_hint else "unknown")
        if is_baseline_hint and solver.lower() in ("pulp", "cbc", "gurobi", "solver"):
            solver = "baseline"

        objective = first(data, ["objective", "metrics.objective", "metrics.objective_value"])
        runtime = first(data, ["runtime_s", "metrics.runtime_s", "metrics.runtime_sec", "runtime_seconds"])
        status = first(data, ["status", "metrics.status"])
        selected = first(data, ["selected", "metrics.selected"])
        total_weight = first(data, ["total_weight", "metrics.total_weight"])

        recs.append({
            "instance": norm_inst,
            "raw_instance": inst,
            "solver": str(solver),
            "objective": to_float(objective),
            "runtime_s": to_float(runtime),
            "status": status if status else "-",
            "selected": int(selected) if isinstance(selected, (int,float,str)) and str(selected).isdigit() else selected,
            "total_weight": int(total_weight) if isinstance(total_weight, (int,float,str)) and str(total_weight).isdigit() else total_weight,
            "source": os.path.relpath(path, ROOT),
            "is_baseline": is_baseline_hint,
            "display_name": norm_inst if not is_baseline_hint else os.path.splitext(fn)[0]
        })
    return recs

solver_recs = load_records(SOLVER_DIR, is_baseline_hint=False)
baseline_recs = load_records(BASELINE_DIR, is_baseline_hint=True)

sol_by_inst = {r["instance"]: r for r in solver_recs}
base_by_inst = {r["instance"]: r for r in baseline_recs}
instances = sorted(set(sol_by_inst.keys()) | set(base_by_inst.keys()))

rows = []
for inst in instances:
    s = sol_by_inst.get(inst)
    b = base_by_inst.get(inst)
    d_obj = d_time = None
    if s and b and s.get("objective") is not None and b.get("objective") is not None:
        d_obj = s["objective"] - b["objective"]
    if s and b and s.get("runtime_s") is not None and b.get("runtime_s") is not None:
        d_time = s["runtime_s"] - b["runtime_s"]

    rows.append({
        "Instance": inst,
        "Solver": s["solver"] if s else "-",
        "Objective": s["objective"] if s else "-",
        "Runtime (s)": s["runtime_s"] if s else "-",
        "Status": s["status"] if s else "-",
        "Selected": s["selected"] if s else "-",
        "TotalWeight": s["total_weight"] if s else "-",
        "Baseline Objective": b["objective"] if b else "-",
        "Baseline Runtime (s)": b["runtime_s"] if b else "-",
        "ΔObj vs Base": d_obj if d_obj is not None else "-",
        "ΔTime vs Base": d_time if d_time is not None else "-",
        "Source": s["source"] if s else (b["source"] if b else "-"),
        "BaselineSource": b["source"] if b else "-"
    })

ts = datetime.utcnow().strftime("%Y-%m-%d %H:%M:%SZ UTC")
lines = []
lines.append("# Solver vs baseline\n")
lines.append(f"- **Generated:** {ts}\n")
lines.append(f"- **Baseline:** {'Detected' if baseline_recs else 'None'}\n")
lines.append("")
lines.append("| Instance | Solver | Objective | Runtime (s) | Status | Selected | TotalWeight | Baseline Objective | Baseline Runtime (s) | ΔObj vs Base | ΔTime vs Base | Source |")
lines.append("| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |")

def fmt(x):
    if isinstance(x, float):
        return f"{x:.3f}"
    return str(x)

for r in rows:
    lines.append("| " + " | ".join([
        r["Instance"],
        fmt(r["Solver"]),
        fmt(r["Objective"]),
        fmt(r["Runtime (s)"]),
        fmt(r["Status"]),
        fmt(r["Selected"]),
        fmt(r["TotalWeight"]),
        fmt(r["Baseline Objective"]),
        fmt(r["Baseline Runtime (s)"]),
        fmt(r["ΔObj vs Base"]),
        fmt(r["ΔTime vs Base"]),
        r["Source"],
    ]) + " |")

with open(OUT_PATH, "w") as f:
    f.write("\n".join(lines) + "\n")

print(f"Wrote {OUT_PATH}")
