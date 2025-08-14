import json
from pathlib import Path
from datetime import datetime, timezone

TABLE_PATH = Path("results/comparison_tables/solver_vs_baseline.md")

def read_json_safe(p):
    try:
        return json.loads(p.read_text())
    except Exception:
        return {}

def pick_first_nonempty(*vals):
    for v in vals:
        if v not in (None, "", "-"):
            return v
    return None

def get_field(d, names, default=None):
    for n in names:
        if n in d and d[n] not in (None, ""):
            return d[n]
    # nested common locations
    meta = d.get("meta") or d.get("metadata") or {}
    for n in names:
        if n in meta and meta[n] not in (None, ""):
            return meta[n]
    return default

def to_float(x):
    try:
        return float(x)
    except Exception:
        return None

def format_float(x, nd=3):
    return f"{x:.{nd}f}"

def classify_path(p: Path) -> str:
    parts = [s.lower() for s in p.parts]
    # heuristics: anything in a "baseline" folder or filename treated as baseline
    if any("baseline" in s for s in parts):
        return "baseline"
    return "solver"

def infer_instance_from_name(name: str) -> str:
    # strip timestamps and solver tags heuristically
    # keep it simple: take middle portion if separated by underscores
    base = name.replace(".json", "")
    return base

def load_runs():
    solver, baseline = [], []
    for p in Path("results").rglob("*.json"):
        kind = classify_path(p)
        d = read_json_safe(p)
        # fields
        instance = pick_first_nonempty(
            get_field(d, ["instance", "problem", "case", "dataset", "name"]),
            infer_instance_from_name(p.name)
        )
        solver_name = pick_first_nonempty(
            get_field(d, ["solver", "method", "variant", "algorithm"]), "unknown"
        )
        objective = get_field(d, ["objective", "obj", "value"])
        runtime_s = get_field(d, ["runtime_s", "runtime", "elapsed_s", "time", "duration_s"])
        status = get_field(d, ["status", "solve_status", "result"], "Unknown")
        selected = get_field(d, ["selected", "num_selected", "k", "chosen"])
        total_weight = get_field(d, ["total_weight", "TotalWeight", "weight", "sum_weight"])

        rec = {
            "path": str(p),
            "instance": str(instance),
            "solver": str(solver_name),
            "objective": objective,
            "runtime_s": runtime_s,
            "status": status,
            "selected": selected,
            "total_weight": total_weight,
        }
        (baseline if kind == "baseline" else solver).append(rec)
    return solver, baseline

def pick_best(records):
    # Choose record with numeric runtime; prefer Optimal then Feasible
    def status_rank(s):
        s = (s or "").lower()
        if "optimal" in s:
            return 0
        if "feas" in s:
            return 1
        return 2

    def key(rec):
        rt = to_float(rec["runtime_s"])
        return (status_rank(rec["status"]), rt if rt is not None else float("inf"))

    by_instance = {}
    for r in records:
        inst = r["instance"]
        if inst not in by_instance:
            by_instance[inst] = r
        else:
            # keep the better key
            if key(r) < key(by_instance[inst]):
                by_instance[inst] = r
    return by_instance

def build_table():
    solver_runs, baseline_runs = load_runs()
    best_solver = pick_best(solver_runs)
    best_base = pick_best(baseline_runs)

    instances = sorted(set(best_solver.keys()) | set(best_base.keys()))
    lines = []
    lines.append("# Solver vs baseline")
    # header metadata
    now = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%SZ UTC")
    baseline_state = "Detected" if best_base else "None detected (deltas shown as '-')" 
    lines.append("")
    lines.append(f"- **Generated:** {now}")
    lines.append(f"- **Baseline:** {baseline_state}")
    lines.append("")
    header = [
        "Instance", "Solver", "Objective", "Runtime (s)", "Status",
        "Selected", "TotalWeight",
        "Baseline Objective", "Baseline Runtime (s)",
        "ΔObj vs Base", "ΔTime vs Base", "Source"
    ]
    lines.append("| " + " | ".join(header) + " |")
    lines.append("| " + " | ".join(["---"] * len(header)) + " |")

    for inst in instances:
        srec = best_solver.get(inst)
        brec = best_base.get(inst)

        solver_name = srec["solver"] if srec else "-"
        s_obj_f = to_float(srec["objective"]) if srec else None
        s_rt_f = to_float(srec["runtime_s"]) if srec else None
        s_stat = srec["status"] if srec else "-"
        s_sel = srec["selected"] if srec else "-"
        s_tw = srec["total_weight"] if srec else "-"

        b_obj_f = to_float(brec["objective"]) if brec else None
        b_rt_f = to_float(brec["runtime_s"]) if brec else None

        # formatted
        s_obj = format_float(s_obj_f, 3) if s_obj_f is not None else "-"
        s_rt = format_float(s_rt_f, 3) if s_rt_f is not None else "-"
        b_obj = format_float(b_obj_f, 3) if b_obj_f is not None else "-"
        b_rt = format_float(b_rt_f, 3) if b_rt_f is not None else "-"

        d_obj = "-"
        d_time = "-"
        if s_obj_f is not None and b_obj_f is not None:
            d_obj = format_float(s_obj_f - b_obj_f, 3)
        if s_rt_f is not None and b_rt_f is not None:
            d_time = format_float(s_rt_f - b_rt_f, 3)

        source = srec["path"] if srec else (brec["path"] if brec else "-")

        row = [
            inst, solver_name, s_obj, s_rt, s_stat,
            str(s_sel), str(s_tw),
            b_obj, b_rt,
            d_obj, d_time, source
        ]
        lines.append("| " + " | ".join(row) + " |")

    TABLE_PATH.parent.mkdir(parents=True, exist_ok=True)
    TABLE_PATH.write_text("\n".join(lines))
    print(f"Wrote {TABLE_PATH}")

if __name__ == "__main__":
    build_table()

