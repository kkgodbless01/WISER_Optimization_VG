import json
import time
from pathlib import Path
import argparse

parser = argparse.ArgumentParser()
parser.add_argument("--instance", required=True, help="Path to instance JSON file")
parser.add_argument("--output", required=True, help="Path to output JSON file")
args = parser.parse_args()

# --- Load the instance ---
instance_path = Path(args.instance)
if not instance_path.exists():
    raise FileNotFoundError(f"Instance file not found: {instance_path}")

with open(instance_path) as f:
    instance_data = json.load(f)

# --- Simulate solving ---
start = time.time()

# Here you’d put your actual solver call. For now we hard‑code a result.
objective_value = 50.0
selected_items = 4
total_weight = 50
status = "Optimal"

time.sleep(0.02)  # pretend it took some time
runtime_s = time.time() - start

# --- Build output dict ---
result = {
    "instance": instance_data.get("name", instance_path.stem),
    "solver": "pulp",
    "objective": objective_value,
    "runtime_s": runtime_s,
    "status": status,
    "selected": selected_items,
    "total_weight": total_weight
}

# --- Save JSON ---
out_path = Path(args.output)
out_path.parent.mkdir(parents=True, exist_ok=True)
with open(out_path, "w") as f:
    json.dump(result, f, indent=2)

print(f"✅ Wrote solver results to {out_path}")

