#!/bin/bash
set -e

echo "[Baseline Runner] Starting..."

# List all scenarios you want to run
SCENARIOS=("example_small")   # add more like "scenario2" "scenario3"

for SC in "${SCENARIOS[@]}"; do
    echo "[Baseline] Running: $SC"
    # Replace with your actual baseline script call
    python experiments/doe.py --instance "data/${SC}.json"
done

echo "[Baseline Runner] All scenarios complete."

