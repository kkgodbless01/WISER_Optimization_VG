import argparse, json, os, sys, time, subprocess, platform
from datetime import datetime, timezone, timedelta

# Ghana local time helper
def now_accra_str():
    try:
        # Accra is UTC+0 (no DST). Represent plainly.
        return datetime.utcnow().strftime("%d-%b-%Y %H:%M")
    except Exception:
        return datetime.now().strftime("%d-%b-%Y %H:%M")

def git_sha_short():
    try:
        return subprocess.check_output(["git", "rev-parse", "--short", "HEAD"], stderr=subprocess.DEVNULL).decode().strip()
    except Exception:
        return "N/A"

def py_version():
    return platform.python_version()

def load_problem(path):
    with open(path, "r") as f:
        return json.load(f)

def greedy_fill(problem):
    # Objective: minimize leftover = budget - sum(prices of chosen assets), with sum <= budget
    budget = float(problem.get("budget", 0.0))
    assets = list(problem.get("assets", []))
    # Sort by price ascending (simple baseline)
    assets.sort(key=lambda a: float(a.get("price", 0.0)))
    chosen = []
    total = 0.0
    for a in assets:
        p = float(a.get("price", 0.0))
        if total + p <= budget:
            chosen.append({"id": a.get("id"), "price": p})
            total += p
    leftover = max(0.0, budget - total)
    return {
        "budget": budget,
        "total_spend": round(total, 4),
        "leftover": round(leftover, 4),
        "chosen_count": len(chosen),
        "chosen": chosen
    }

def main(argv=None):
    ap = argparse.ArgumentParser(description="Step 1: Static cost-minimization baseline")
    ap.add_argument("--input", default="data/problem.json", help="Path to problem JSON")
    ap.add_argument("--outdir", default="outputs/step_1", help="Output directory")
    ap.add_argument("--debug", action="store_true", help="Verbose prints")
    args = ap.parse_args(argv)

    os.makedirs(args.outdir, exist_ok=True)

    t0 = time.perf_counter()
    try:
        problem = load_problem(args.input)
    except Exception as e:
        print(f"[step1] Failed to load problem: {e}", file=sys.stderr)
        return 2

    solution = greedy_fill(problem)
    t1 = time.perf_counter()
    runtime = round(t1 - t0, 6)

    # Metrics and artifacts
    sha = git_sha_short()
    metrics = {
        "step": "step_1_static_solver",
        "status": "success",
        "objective": "min leftover budget (greedy baseline)",
        "best_cost": solution["leftover"],  # lower is better
        "runtime_s": runtime,
        "timestamp_local": now_accra_str(),
        "git_sha": sha,
        "python": py_version(),
        "input_file": os.path.abspath(args.input),
        "outdir": os.path.abspath(args.outdir)
    }

    sol_path = os.path.join(args.outdir, "solution.json")
    met_path = os.path.join(args.outdir, "metrics.json")
    with open(sol_path, "w") as f:
        json.dump(solution, f, indent=2)
    with open(met_path, "w") as f:
        json.dump(metrics, f, indent=2)

    if args.debug:
        print("[step1] Objective:", metrics["objective"])
        print("[step1] Best cost (leftover):", metrics["best_cost"])
        print("[step1] Runtime (s):", metrics["runtime_s"])
        print("[step1] Artifacts:", sol_path, met_path)

    return 0

if __name__ == "__main__":
    raise SystemExit(main())
