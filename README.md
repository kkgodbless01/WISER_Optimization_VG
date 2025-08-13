# WISER Optimization VG — Benchmarking

This repository benchmarks solver performance on provided instances and auto-generates comparison tables for clear, reproducible results.

## Benchmarking process and results

### Approach
- **Solver:** PuLP (CBC backend, classical MILP)
- **Problem:** Knapsack-like selection from JSON instances
- **Inputs:** `data/*.json`
- **Metrics:** objective_value, runtime_seconds, status, selected_count, total_weight

### Variations and tuning
- **Current:** Default CBC parameters (no extra tuning)
- **Reproducibility layout:**
  - `results/baseline_runs` — raw solver outputs in JSON
  - `results/comparison_tables` — auto-generated Markdown summaries

### How to reproduce
```bash
# Activate environment
source venv/bin/activate

# Run solver on a specific instance (example)
python src/run_baseline_solver.py data/example_small.json

# Generate Markdown comparison table
python src/make_markdown_table.py

