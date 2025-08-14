#!/usr/bin/env python3
import json, sys
from pathlib import Path
from datetime import datetime

ROOT = Path(__file__).resolve().parent.parent
OUR_RESULTS_DIR = ROOT / "results" / "baseline_runs"
COMPARISON_DIR = ROOT / "results" / "comparison_tables"
OUT_PATH = COMPARISON_DIR / "solver_vs_baseline.md"

# Optional: point this to a baseline JSON later if you have one.
# Supported formats:
# - dict keyed by instance_id -> {objective_value, runtime_seconds}
# - list of entries with instance_id, metrics or flat fields
BASELINE_PATH = ROOT / "misc" / "baseline_results.json"

def load_our_results():
    if not OUR_RESULTS_DIR.exists():
        return []
    rows = []
    for fp in sorted(OUR_RESULTS_DIR.glob("*.json")):
        try:
            with open(fp, "r") as f:
                payload = json.load(f)
            m = payload.get("metrics", {})
            rows.append({
                "instance_id": payload.get("instance_id", "unknown"),
                "solver": payload.get("solver", "unknown"),
                "objective": m.get("objective_value"),
                "runtime": m.get("runtime_seconds"),
                "status": m.get("status", "unknown"),
                "selected": m.get("selected_count"),
                "total_weight": m.get("total_weight"),
                "source": str(fp.relative_to(ROOT)),
            })
        except Exception as e:
            print(f"Warning: failed to read {fp}: {e}", file=sys.stderr)
    return rows

def normalize_baseline_entry(entry):
    # Accept both {metrics:{...}} and flat fields
    if "metrics" in entry and isinstance(entry["metrics"], dict):
        m = entry["metrics"]
        return {
            "objective": m.get("objective_value"),
            "runtime": m.get("runtime_seconds"),
        }
    return {
        "objective": entry.get("objective_value"),
        "runtime": entry.get("runtime_seconds"),
    }

def load_baseline():
    # Return a dict: instance_id -> {objective, runtime}
    if not BASELINE_PATH.exists():
        return {}
    try:
        with open(BASELINE_PATH, "r") as f:
            data = json.load(f)
    except Exception as e:
        print(f"Warning: cannot read baseline at {BASELINE_PATH}: {e}", file=sys.stderr)
        return {}

    baseline = {}
    if isinstance(data, dict):
        # Either already keyed by instance_id, or a single entry with instance_id
        if all(isinstance(v, dict) for v in data.values()):
            for k, v in data.items():
                entry = normalize_baseline_entry(v)
                baseline[k] = entry
        else:
            iid = data.get("instance_id")
            if iid:
                baseline[iid] = normalize_baseline_entry(data)
    elif isinstance(data, list):
        for rec in data:
            iid = rec.get("instance_id")
            if iid:
                baseline[iid] = normalize_baseline_entry(rec)
    else:
        print(f"Warning: unsupported baseline format in {BASELINE_PATH}", file=sys.stderr)
    return baseline

def fmt(x, nd=3):
    if x is None:
        return "-"
    try:
        return f"{float(x):.{nd}f}"
    except Exception:
        return str(x)

def fmt_delta(our, base, nd=3):
    if our is None or base is None:
        return "-"
    try:
        d = float(our) - float(base)
        sign = "+" if d >= 0 else ""
        return f"{sign}{d:.{nd}f}"
    except Exception:
        return "-"

def build_markdown(ours, baseline_map):
    lines = []
    ts = datetime.utcnow().strftime("%Y-%m-%d %H:%M:%SZ")
    lines.append(f"# Solver vs baseline")
    lines.append("")
    lines.append(f"- **Generated:** {ts} UTC")
    if baseline_map:
        lines.append(f"- **Baseline:** {BASELINE_PATH.relative_to(ROOT)}")
    else:
        lines.append(f"- **Baseline:** None detected (deltas shown as '-')")
    lines.append("")
    headers = [
        "Instance", "Solver", "Objective", "Runtime (s)", "Status",
        "Selected", "TotalWeight", "ΔObj vs Base", "ΔTime vs Base", "Source"
    ]
    lines.append("| " + " | ".join(headers) + " |")
    lines.append("| " + " | ".join(["---"] * len(headers)) + " |")
    for r in ours:
        base = baseline_map.get(r["instance_id"], {})
        row = [
            r["instance_id"],
            r["solver"],
            fmt(r["objective"], 3),
            fmt(r["runtime"], 3),
            str(r["status"]),
            str(r["selected"]) if r["selected"] is not None else "-",
            str(r["total_weight"]) if r["total_weight"] is not None else "-",
            fmt_delta(r["objective"], base.get("objective"), 3),
            fmt_delta(r["runtime"], base.get("runtime"), 3),
            r["source"],
        ]
        lines.append("| " + " | ".join(row) + " |")
    return "\n".join(lines)

def main():
    COMPARISON_DIR.mkdir(parents=True, exist_ok=True)
    ours = load_our_results()
    if not ours:
        print(f"No result JSON files found in {OUR_RESULTS_DIR}", file=sys.stderr)
        sys.exit(1)
    baseline_map = load_baseline()
    md = build_markdown(ours, baseline_map)
    OUT_PATH.write_text(md, encoding="utf-8")
    print(f"Wrote: {OUT_PATH}")

if __name__ == "__main__":
    main()

