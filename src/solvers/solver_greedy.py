from dataclasses import dataclass
from typing import List, Dict
import time

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

def greedy_ratio(values: List[float], weights: List[float], capacity: float) -> Dict:
    start = time.perf_counter()
    items = list(range(len(values)))
    items.sort(key=lambda i: values[i]/weights[i], reverse=True)
    total_w = 0.0
    total_v = 0.0
    chosen = [0]*len(values)
    for i in items:
        if total_w + weights[i] <= capacity:
            chosen[i] = 1
            total_w += weights[i]
            total_v += values[i]
    runtime = time.perf_counter() - start
    return {
        "chosen": chosen,
        "best_value": float(total_v),
        "total_weight": float(total_w),
        "feasible": total_w <= capacity + 1e-9,
        "runtime_s": runtime,
        "iterations": len(values)
    }

def solve(values: List[float], weights: List[float], capacity: float, instance_id: str) -> KnapsackResult:
    out = greedy_ratio(values, weights, capacity)
    return KnapsackResult(
        solver="greedy",
        instance_id=instance_id,
        n_items=len(values),
        capacity=int(capacity),
        best_value=out["best_value"],
        total_weight=out["total_weight"],
        feasible=out["feasible"],
        runtime_s=out["runtime_s"],
        iterations=out["iterations"],
    )

