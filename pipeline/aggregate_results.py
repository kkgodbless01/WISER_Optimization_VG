import pandas as pd
from datetime import datetime
from pathlib import Path

# Paths for results and outputs
RESULTS_DIR = Path("results/solver_outputs")
BASELINE_DIR = Path("results/baseline_outputs")
COMPARISON_PATH = Path("results/comparison_tables/solver_vs_baseline.md")
SUMMARY_PATH = Path("PROJECT_SUMMARY.md")

def load_results(folder):
    """Load CSV results and return as DataFrame."""
    files = list(folder.glob("*.csv"))
    if not files:
        raise FileNotFoundError(f"No CSV files found in {folder}")
    dfs = [pd.read_csv(f) for f in files]
    return pd.concat(dfs, ignore_index=True)

def aggregate_metrics():
    # Load solver + baseline data
    solver_df = load_results(RESULTS_DIR)
    baseline_df = load_results(BASELINE_DIR)

    # Calculate metrics
    avg_runtime_solver = solver_df["runtime_sec"].mean()
    avg_runtime_baseline = baseline_df["runtime_sec"].mean()

    accuracy_solver = solver_df["accuracy_percent"].mean()
    accuracy_baseline = baseline_df["accuracy_percent"].mean()

    speedup_factor = avg_runtime_baseline / avg_runtime_solver if avg_runtime_solver else None

    # NEW: Cost Function Value metric
    cost_solver = solver_df["cost"].mean()
    cost_baseline = baseline_df["cost"].mean()

    # Build Markdown table for comparison file
    lines = []
    lines.append(f"# Solver vs baseline\n")
    lines.append(f"Updated: {datetime.utcnow().strftime('%Y-%m-%d %H:%M:%SZ')}\n")
    lines.append("\n| Metric | Solver | Baseline |")
    lines.append("| ------------------------ | :------: | :--------: |")
    lines.append(f"| Average Runtime (s) | {avg_runtime_solver:.2f} | {avg_runtime_baseline:.2f} |")
    lines.append(f"| Solution Accuracy (%) | {accuracy_solver:.1f} | {accuracy_baseline:.1f} |")
    lines.append(f"| Speedup Factor | {speedup_factor:.2f}× | — |")
    lines.append(f"| Cost Function Value | {cost_solver:.2f} | {cost_baseline:.2f} |")

    COMPARISON_PATH.write_text("\n".join(lines))

    # Update PROJECT_SUMMARY.md snapshot section
    summary_lines = [
        "## Key results (snapshot)",
        "| Metric | Solver Variant | Baseline |",
        "| ----------------------- | ---------------- | ---------- |",
        f"| Average Runtime (s) | {avg_runtime_solver:.2f} | {avg_runtime_baseline:.2f} |",
        f"| Solution Accuracy (%) | {accuracy_solver:.1f} | {accuracy_baseline:.1f} |",
        f"| Speedup Factor | {speedup_factor:.2f}× | — |",
        f"| Cost Function Value | {cost_solver:.2f} | {cost_baseline:.2f} |",
        "",
        "Full table:",
        "- results/comparison_tables/solver_vs_baseline.md"
    ]
    SUMMARY_PATH.write_text("\n".join(summary_lines))

if __name__ == "__main__":
    aggregate_metrics()
    print("✅ Aggregation complete. Tables updated with Cost Function Value.")

