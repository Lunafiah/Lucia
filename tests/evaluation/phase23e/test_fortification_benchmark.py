"""
tests/evaluation/phase23e/test_fortification_benchmark.py

Automated Evaluation & Resource Budget Gates for Phase 23-E.
Verifies:
1. Small scale meets performance TARGET (<= 15 MB RAM, <= 10 ms latency).
2. Medium scale meets performance TARGET.
3. Large & Stress scales strictly respect HARD SAFETY CEILING (<= 30 MB RAM, <= 25 ms latency).
4. Fortification-Originated Unsupported Insertion Rate is 0.0 (Zero novel entities).
5. Epistemic Safety Invariant is satisfied (No UNKNOWN/AMBIGUOUS promotions).
"""

import pytest
from tests.evaluation.phase23e.benchmark_runner import (
    HARD_CEILING_LATENCY_MS,
    HARD_CEILING_RAM_MB,
    TARGET_LATENCY_MS,
    TARGET_RAM_MB,
    run_single_scale_benchmark,
)


def test_small_scale_benchmark_target():
    """Verify small session graphs meet performance target."""
    res = run_single_scale_benchmark(num_nodes=20, num_edges=30, num_iterations=15)
    assert res["gates"]["latency_target_met"] is True, f"Median latency {res['latency_ms']['p50_median']} ms exceeded {TARGET_LATENCY_MS} ms"
    assert res["gates"]["ram_target_met"] is True, f"Peak RAM {res['peak_ram_mb']} MB exceeded {TARGET_RAM_MB} MB"
    assert res["invariants"]["fortification_originated_unsupported_insertion_rate"] == 0.0
    assert res["invariants"]["epistemic_safety_invariant_satisfied"] is True


def test_medium_scale_benchmark_target():
    """Verify medium session graphs meet performance target."""
    res = run_single_scale_benchmark(num_nodes=100, num_edges=150, num_iterations=15)
    assert res["gates"]["latency_target_met"] is True, f"Median latency {res['latency_ms']['p50_median']} ms exceeded {TARGET_LATENCY_MS} ms"
    assert res["gates"]["ram_target_met"] is True, f"Peak RAM {res['peak_ram_mb']} MB exceeded {TARGET_RAM_MB} MB"
    assert res["invariants"]["fortification_originated_unsupported_insertion_rate"] == 0.0
    assert res["invariants"]["epistemic_safety_invariant_satisfied"] is True


def test_large_scale_benchmark_hard_ceiling():
    """Verify large graphs respect hard safety ceiling."""
    res = run_single_scale_benchmark(num_nodes=500, num_edges=800, num_iterations=10)
    assert res["latency_ms"]["p50_median"] <= HARD_CEILING_LATENCY_MS, f"Median latency {res['latency_ms']['p50_median']} ms exceeded ceiling {HARD_CEILING_LATENCY_MS} ms"
    assert res["gates"]["ram_ceiling_met"] is True, f"Peak RAM {res['peak_ram_mb']} MB exceeded ceiling {HARD_CEILING_RAM_MB} MB"
    assert res["invariants"]["fortification_originated_unsupported_insertion_rate"] == 0.0
    assert res["invariants"]["epistemic_safety_invariant_satisfied"] is True
