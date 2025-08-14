#!/usr/bin/env bash
set -euo pipefail

echo "==> Ensuring output folders exist"
mkdir -p results/comparison_tables
mkdir -p results/plots

echo "==> Building solver_vs_baseline.md (baseline-aware)"
python3 build_solver_vs_baseline.py

echo "==> Optional: plotting (will skip if script not found)"
if [ -f "scripts/plot_results.py" ]; then
  python3 scripts/plot_results.py || echo "Plotting script returned non-zero; continuing"
elif [ -f "results/plot_results.py" ]; then
  python3 results/plot_results.py || echo "Plotting script returned non-zero; continuing"
elif [ -f "plot_results.py" ]; then
  python3 plot_results.py || echo "Plotting script returned non-zero; continuing"
else
  echo "No plotting script detected. Skipping."
fi

echo "==> Filling recruiter-facing metrics"
python3 fill_best_metrics.py

echo "==> Git commit & push"
# Add common files
git add results/comparison_tables/solver_vs_baseline.md || true
git add results/plots || true
git add README.md PROJECT_SUMMARY.md LINKEDIN_POST.txt || true

# Create a timestamped message
ts=$(date -u +"%Y-%m-%dT%H:%M:%SZ")
git commit -m "Pipeline: rebuild table, update metrics, plots [${ts}]" || echo "No changes to commit."
git push origin main

echo "✅ Pipeline complete."

