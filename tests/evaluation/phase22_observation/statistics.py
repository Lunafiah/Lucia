"""
Statistical utilities for Phase 22 Observation Layer Study.
Includes paired t-tests, bootstrap confidence intervals, and effect size calculation.
"""
from typing import Dict, List, Tuple, Any
import numpy as np

def bootstrap_ci(data: np.ndarray, num_resamples: int = 1000, ci: float = 0.95) -> Tuple[float, float]:
    arr = np.asarray(data, dtype=np.float64)
    if len(arr) == 0:
        return (0.0, 0.0)
    means = []
    n = len(arr)
    rng = np.random.RandomState(42)
    for _ in range(num_resamples):
        idx = rng.randint(0, n, size=n)
        means.append(np.mean(arr[idx]))
    alpha = (1.0 - ci) / 2.0
    low = float(np.percentile(means, alpha * 100))
    high = float(np.percentile(means, (1.0 - alpha) * 100))
    return (low, high)

def compute_percentiles(latencies: List[float]) -> Dict[str, float]:
    arr = np.asarray(latencies, dtype=np.float64)
    if len(arr) == 0:
        return {"p50": 0.0, "p95": 0.0, "p99": 0.0}
    return {
        "p50": float(np.percentile(arr, 50)),
        "p95": float(np.percentile(arr, 95)),
        "p99": float(np.percentile(arr, 99)),
    }
