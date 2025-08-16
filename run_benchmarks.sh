#!/usr/bin/env bash
set -euo pipefail

# Run new solver experiments (greedy + new_solver1)
python src/benchmarks/run_new_experiments.py

# Aggregate all solver results into results/ALL_RESULTS.csv
python src/aggregator/compile_results.py

# Generate plots from aggregated results
python src/plots/plot_performance.py

echo "✅ All done. Check results/ for CSV and plots."

