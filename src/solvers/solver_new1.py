from dataclasses import dataclass
from typing import List, Tuple
import random, time

@dataclass
class KnapsackResult:
    solver: str
    instance_id: str
    n_items: int
    capacity: int
    best_value: float
    total_weight: float
    feasible: bool
    runtime_s: float
    iterations: int

def _score(chosen, values, weights, capacity) -> Tuple[float, float, bool]:
    w = sum(wi for ci, wi in zip(chosen, weights) if ci)
    v = sum(vi for ci, vi in zip(chosen, values) if ci)
    feasible = w <= capacity + 1e-9
    return v, w, feasible

def local_search(values: List[float], weights: List[float], capacity: float, max_iters: int = 5000, seed: int = 42):
    rnd = random.Random(seed)
    start = time.perf_counter()
    n = len(values)
    chosen = [0]*n
    order = list(range(n))
    order.sort(key=lambda i: values[i]/weights[i], reverse=True)
    for i in order:
        if sum(weights[j] for j in range(n) if chosen[j]) + weights[i] <= capacity:
            chosen[i] = 1

    best = chosen[:]
    best_v, best_w, _ = _score(best, values, weights, capacity)

    iters = 0
    while iters < max_iters:
        iters += 1
        i = rnd.randrange(n)
        j = rnd.randrange(n)
        neighbor = best[:]
        if i != j:
            neighbor[i] = 1 - neighbor[i]
            neighbor[j] = 1 - neighbor[j]
        else:
            neighbor[i] = 1 - neighbor[i]
        v, w, feas = _score(neighbor, values, weights, capacity)
        if feas and v > best_v:
            best, best_v, best_w = neighbor, v, w

    runtime = time.perf_counter() - start
    feas = best_w <= capacity + 1e-9
    return {
        "chosen": best,
        "best_value": float(best_v),
        "total_weight": float(best_w),
        "feasible": feas,
        "runtime_s": runtime,
        "iterations": iters
    }

def solve(values: List[float], weights: List[float], capacity: float, instance_id: str) -> KnapsackResult:
    out = local_search(values, weights, capacity, max_iters=6000, seed=123)
    return KnapsackResult(
        solver="new_solver1",
        instance_id=instance_id,
        n_items=len(values),
        capacity=int(capacity),
        best_value=out["best_value"],
        total_weight=out["total_weight"],
        feasible=out["feasible"],
        runtime_s=out["runtime_s"],
        iterations=out["iterations"],
    )

