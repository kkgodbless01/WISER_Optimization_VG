#!/bin/bash
set -e

echo "[Solver Runner] Starting..."

# List all scenarios to run
SCENARIOS=("example_small")   # Add more like "scenario2" "scenario3"

for SC in "${SCENARIOS[@]}"; do
    echo "[Solver] Running: $SC"
    # Replace with your actual solver script call
    python experiments/sbo_step4.py --instance "data/${SC}.json"
done

echo "[Solver Runner] All scenarios complete."

