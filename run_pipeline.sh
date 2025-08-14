#!/bin/bash
set -euo pipefail

# Always operate from repo root
cd "$(dirname "$0")"
ROOT="$(pwd)"

echo "=== Step 0: Environment bootstrap ==="
# --- Dependency Auto-Installer ---
echo "🔍 Checking core Python packages..."
PY_BIN="${VENV_PYTHON:-$(command -v python3 || command -v python)}"

REQUIRED_PKGS=(
  pandas
  matplotlib
  docplex
  mip
  numpy
  scikit-learn
)

for pkg in "${REQUIRED_PKGS[@]}"; do
  if ! "$PY_BIN" -c "import importlib; m='$pkg'; alias={'scikit-learn':'sklearn'}; importlib.import_module(alias.get(m, m))" &>/dev/null; then
    echo "📦 Installing missing package: $pkg"
    "$PY_BIN" -m pip install "$pkg"
  else
    echo "✅ $pkg already installed"
  fi
done
echo "✅ All core packages verified"
# --- End Dependency Auto-Installer ---
# Create venv if missing
if [ ! -d "venv" ]; then
  python3 -m venv venv
fi
# Activate venv
source venv/bin/activate
echo "Python: $(python -V)"
echo "Which python: $(which python)"

# Install deps for reproducibility
if [ -f requirements.txt ]; then
  echo "[Deps] Installing from requirements.txt..."
  pip install -r requirements.txt
else
  echo "[Deps] No requirements.txt found. Skipping."
fi

# Ensure Python can import from project root
export PYTHONPATH="$PYTHONPATH:$ROOT"

# Prepare directories
mkdir -p results/baseline_runs results/solver_runs results/comparison_tables results/plots

echo "=== Step 1: Archive old timestamped baselines (kept for audit) ==="
mkdir -p results/baseline_runs/_bak
# Move only files with leading timestamp like 20250813T213320Z_*.json
find results/baseline_runs -maxdepth 1 -type f -regextype posix-extended \
  -regex '.*/[0-9]{8}T[0-9]{6}Z_.*\.json' -print -exec mv {} results/baseline_runs/_bak/ \; || true

echo "=== Step 2: Run baseline experiments ==="
if [ -x ./experiments/run_baseline_all.sh ]; then
  ./experiments/run_baseline_all.sh
else
  echo "[Baseline] Missing ./experiments/run_baseline_all.sh — skipping baseline stage."
fi

echo "=== Step 3: Run solver experiments ==="
if [ -x ./experiments/run_solver_all.sh ]; then
  ./experiments/run_solver_all.sh
else
  echo "[Solver] Missing ./experiments/run_solver_all.sh — skipping solver stage."
fi

echo "=== Step 4: Build merged solver_vs_baseline.md ==="
python build_solver_vs_baseline.py
TABLE="results/comparison_tables/solver_vs_baseline.md"
if [ -f "$TABLE" ]; then
  echo "[Table] Wrote $TABLE"
  echo "[Table] Preview:"
  grep -m 3 '|' "$TABLE" || true
fi

echo "=== Step 5: Generate quick plots (runtime/objective) ==="
python - <<'PY'
import os, re, pandas as pd, matplotlib.pyplot as plt
table_path = "results/comparison_tables/solver_vs_baseline.md"
out_dir = "results/plots"
os.makedirs(out_dir, exist_ok=True)

# Parse the markdown table by splitting on pipes and cleaning
with open(table_path, "r") as f:
    lines = [ln.rstrip("\n") for ln in f]

# Find the header row that starts the table
start = next((i for i, ln in enumerate(lines) if ln.strip().startswith("| Instance |")), None)
if start is None:
    raise SystemExit("No table header found in solver_vs_baseline.md")

data_lines = [ln for ln in lines[start+2:] if ln.strip().startswith("|")]
records = []
headers = [h.strip() for h in lines[start].strip().strip("|").split("|")]
for ln in data_lines:
    parts = [p.strip() for p in ln.strip().strip("|").split("|")]
    if len(parts) != len(headers):
        continue
    rec = dict(zip(headers, parts))
    # Skip separator or empty rows
    if rec.get("Instance", "").lower() in ("", "instance", "---"):
        continue
    records.append(rec)

if not records:
    raise SystemExit("No data rows in table")

df = pd.DataFrame(records)

# Convert numeric columns
for col in ["Objective", "Runtime (s)", "Baseline Objective", "Baseline Runtime (s)"]:
    df[col] = pd.to_numeric(df[col].replace("-", pd.NA), errors="coerce")

# Plot 1: Runtime comparison
plt.figure(figsize=(8,4))
ix = range(len(df))
plt.bar([i - 0.2 for i in ix], df["Runtime (s)"], width=0.4, label="Solver")
plt.bar([i + 0.2 for i in ix], df["Baseline Runtime (s)"], width=0.4, label="Baseline")
plt.xticks(list(ix), df["Instance"], rotation=0)
plt.ylabel("Seconds")
plt.title("Runtime: Solver vs Baseline")
plt.legend()
plt.tight_layout()
plt.savefig(os.path.join(out_dir, "runtime_comparison.png"))
plt.close()

# Plot 2: Objective comparison
plt.figure(figsize=(8,4))
plt.bar([i - 0.2 for i in ix], df["Objective"], width=0.4, label="Solver")
plt.bar([i + 0.2 for i in ix], df["Baseline Objective"], width=0.4, label="Baseline")
plt.xticks(list(ix), df["Instance"], rotation=0)
plt.ylabel("Objective")
plt.title("Objective: Solver vs Baseline")
plt.legend()
plt.tight_layout()
plt.savefig(os.path.join(out_dir, "objective_comparison.png"))
plt.close()

print("[Plots] Saved to results/plots: runtime_comparison.png, objective_comparison.png")
PY

echo "=== Step 6: Update PROJECT_SUMMARY.md snapshot metrics ==="
python - <<'PY'
import re, pandas as pd, math

table_path = "results/comparison_tables/solver_vs_baseline.md"
summary_path = "PROJECT_SUMMARY.md"

# Read table
df = pd.read_csv(table_path, sep="|", engine="python").dropna(how="all", axis=1)
df.columns = [c.strip() for c in df.columns]
df = df[df["Instance"].astype(str).str.len() > 0]
num = lambda s: pd.to_numeric(df[s].replace("-", pd.NA), errors="coerce")

avg_solver_time = num("Runtime (s)").mean()
avg_baseline_time = num("Baseline Runtime (s)").mean()
avg_solver_obj = num("Objective").mean()
avg_baseline_obj = num("Baseline Objective").mean()

speedup = (avg_baseline_time / avg_solver_time) if (pd.notna(avg_solver_time) and pd.notna(avg_baseline_time) and avg_solver_time>0) else pd.NA
accuracy = (avg_solver_obj / avg_baseline_obj * 100) if (pd.notna(avg_solver_obj) and pd.notna(avg_baseline_obj) and avg_baseline_obj!=0) else pd.NA

def fmt(x, prec=2, suffix=""):
    try:
        return f"{float(x):.{prec}f}{suffix}"
    except Exception:
        return "pending"

with open(summary_path, "r", encoding="utf-8") as f:
    text = f.read()

# Replace three snapshot lines if present; otherwise, do nothing
text = re.sub(r"\| Average Runtime \(s\) \| .*? \| .*? \|",
              f"| Average Runtime (s) | {fmt(avg_solver_time)} | {fmt(avg_baseline_time)} |", text)
text = re.sub(r"\| Solution Accuracy \(\%\) \| .*? \| .*? \|",
              f"| Solution Accuracy (%) | {fmt(accuracy)} | — |", text)
text = re.sub(r"\| Speedup Factor \| .*? \| .*? \|",
              f"| Speedup Factor | {fmt(speedup, 2, '×')} | — |", text)

with open(summary_path, "w", encoding="utf-8") as f:
    f.write(text)

print("[Summary] PROJECT_SUMMARY.md updated.")
PY

echo "=== Done ==="
echo "Table: results/comparison_tables/solver_vs_baseline.md"
echo "Plots: results/plots/runtime_comparison.png, results/plots/objective_comparison.png"

