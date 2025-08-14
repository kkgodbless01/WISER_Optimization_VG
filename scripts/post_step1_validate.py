from pathlib import Path
import json, sys, math

metrics_path = Path("outputs/step_1/metrics.json")
if not metrics_path.exists():
    sys.stderr.write("❌ metrics.json not found — Step 1 may have failed.\n")
    sys.exit(1)

try:
    data = json.loads(metrics_path.read_text())
except Exception as e:
    sys.stderr.write(f"❌ Could not parse metrics.json: {e}\n")
    sys.exit(1)

allocs = data.get("allocations", [])
total_cost = data.get("total_cost", data.get("best_cost", 0))  # be tolerant on key name
budget = data.get("budget", None)

errors = []
if not isinstance(allocs, list) or len(allocs) == 0:
    errors.append("Allocations missing or empty")
else:
    s = sum(allocs)
    if not math.isfinite(s) or abs(s - 1.0) > 1e-6:
        errors.append(f"Allocations do not sum to 1.0 (sum={s})")
    if min(allocs) < 0:
        errors.append("Negative allocation detected")
if not (isinstance(total_cost, (int, float)) and total_cost > 0):
    errors.append("Total cost is non‑positive")

if errors:
    print("⚠ Validation failed:")
    for e in errors:
        print("  -", e)
    sys.exit(1)

pretty = {
    "best_cost": round(float(total_cost), 3),
    "allocations": [round(float(a), 3) for a in allocs],
    "runtime_sec": round(float(data.get("runtime", data.get("runtime_sec", 0))), 3),
    "budget": budget,
    "constraints": data.get("constraints", {})
}
metrics_path.write_text(json.dumps(pretty, indent=2))
print("✅ Step 1 metrics validated & formatted.")
