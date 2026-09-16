"""
tests/evaluation_phase22/metrics/latency.py

High-resolution microsecond latency measurement for Phase 22.
Distinguishes pure CPU policy computation from simulated somatic pacing latency.
"""

from __future__ import annotations

import time
from dataclasses import dataclass, field
from typing import Dict, List, Sequence

import numpy as np


@dataclass(frozen=True)
class LatencyRecord:
    """Detailed latency measurement for a single evaluation step."""
    policy_compute_latency_ms: float
    simulated_somatic_latency_ms: float
    end_to_end_contextual_latency_ms: float


@dataclass(frozen=True)
class LatencyStatistics:
    """Aggregated latency percentiles and empirical SLA evaluation."""
    count: int
    mean_ms: float
    median_ms: float
    p90_ms: float
    p95_ms: float
    p99_ms: float
    max_ms: float
    target_mean_ms: float = 3.0
    target_p95_ms: float = 5.0

    @property
    def target_met(self) -> bool:
        """True if empirical performance meets the Tier-1 targets."""
        return self.mean_ms <= self.target_mean_ms and self.p95_ms <= self.target_p95_ms


def compute_latency_statistics(latencies_ms: Sequence[float]) -> LatencyStatistics:
    """Compute standard percentiles from an array of latency measurements in ms."""
    arr = np.asarray(latencies_ms, dtype=np.float64)
    if len(arr) == 0:
        return LatencyStatistics(
            count=0,
            mean_ms=0.0,
            median_ms=0.0,
            p90_ms=0.0,
            p95_ms=0.0,
            p99_ms=0.0,
            max_ms=0.0,
        )

    return LatencyStatistics(
        count=len(arr),
        mean_ms=float(np.mean(arr)),
        median_ms=float(np.median(arr)),
        p90_ms=float(np.percentile(arr, 90)),
        p95_ms=float(np.percentile(arr, 95)),
        p99_ms=float(np.percentile(arr, 99)),
        max_ms=float(np.max(arr)),
    )


class HighPrecisionTimer:
    """High-resolution context timer using perf_counter_ns."""

    def __init__(self) -> None:
        self._t0: int = 0
        self._t1: int = 0

    def start(self) -> None:
        self._t0 = time.perf_counter_ns()

    def stop(self) -> float:
        self._t1 = time.perf_counter_ns()
        # Return elapsed time in milliseconds
        return (self._t1 - self._t0) / 1_000_000.0
