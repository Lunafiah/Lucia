"""
Pytest Test Suite for Phase 23 Semantic Formation Microbenchmark v0.2 (Audited).
Asserts all 12 Master Acceptance Gates (G-MB-1 through G-MB-12) programmatically.
"""
import pytest
from tests.evaluation.phase23.run_benchmark import run_microbenchmark
from tests.evaluation.phase23.config import SEEDS, GATES_V02


@pytest.fixture(scope="module")
def benchmark_results():
    """Runs the benchmark across preregistered seeds and caches results."""
    return run_microbenchmark(seeds=SEEDS)


def test_g_mb_1_structural_graph_validity(benchmark_results):
    """G-MB-1: Structural Graph Validity Rate (SGVR) >= 95.0%"""
    g = benchmark_results["gate_verdicts"]["G-MB-1"]
    assert g["passed"], f"G-MB-1 failed: measured {g['measured']} < target {g['target']}"


def test_g_mb_2_causal_formation_sensitivity(benchmark_results):
    """G-MB-2: Causal Formation Sensitivity (CFS) >= 80.0%"""
    g = benchmark_results["gate_verdicts"]["G-MB-2"]
    assert g["passed"], f"G-MB-2 failed: measured {g['measured']} < target {g['target']}"


def test_g_mb_3_referential_grounding_precision(benchmark_results):
    """G-MB-3: Referential Grounding Precision (RGP) >= 90.0%"""
    g = benchmark_results["gate_verdicts"]["G-MB-3"]
    assert g["passed"], f"G-MB-3 failed: measured {g['measured']} < target {g['target']}"


def test_g_mb_4_longitudinal_drift(benchmark_results):
    """G-MB-4: 50-Turn Longitudinal Drift (D50) <= 0.050"""
    g = benchmark_results["gate_verdicts"]["G-MB-4"]
    assert g["passed"], f"G-MB-4 failed: measured {g['measured']} > target {g['target']}"


def test_g_mb_5_nested_proposition_fidelity(benchmark_results):
    """G-MB-5: Nested Proposition Fidelity @ D=3 (RF3) >= 85.0%"""
    g = benchmark_results["gate_verdicts"]["G-MB-5"]
    assert g["passed"], f"G-MB-5 failed: measured {g['measured']} < target {g['target']}"


def test_g_mb_6_negation_polarity_accuracy(benchmark_results):
    """G-MB-6: Negation Polarity Accuracy (NPA) >= 95.0%"""
    g = benchmark_results["gate_verdicts"]["G-MB-6"]
    assert g["passed"], f"G-MB-6 failed: measured {g['measured']} < target {g['target']}"


def test_g_mb_7_decision_flapping_rate(benchmark_results):
    """G-MB-7: Decision Flapping Rate (DFR) <= 5.0%"""
    g = benchmark_results["gate_verdicts"]["G-MB-7"]
    assert g["passed"], f"G-MB-7 failed: measured {g['measured']} > target {g['target']}"


def test_g_mb_8_lyapunov_stability(benchmark_results):
    """G-MB-8: Limbic Lyapunov Exponent (lambda_max) <= 0.000"""
    g = benchmark_results["gate_verdicts"]["G-MB-8"]
    assert g["passed"], f"G-MB-8 failed: measured {g['measured']} > target {g['target']}"


def test_g_mb_9_fact_retention_after_delta(benchmark_results):
    """G-MB-9: Fact Retention After Delta (RUF) >= 98.0%"""
    g = benchmark_results["gate_verdicts"]["G-MB-9"]
    assert g["passed"], f"G-MB-9 failed: measured {g['measured']} < target {g['target']}"


def test_g_mb_10_historical_semantic_drift(benchmark_results):
    """G-MB-10: Historical Semantic Drift (Delta_drift) <= 0.050"""
    g = benchmark_results["gate_verdicts"]["G-MB-10"]
    assert g["passed"], f"G-MB-10 failed: measured {g['measured']} > target {g['target']}"


def test_g_mb_11_taxonomic_placement_accuracy(benchmark_results):
    """G-MB-11: Taxonomic Placement Accuracy (TPA) >= 80.0%"""
    g = benchmark_results["gate_verdicts"]["G-MB-11"]
    assert g["passed"], f"G-MB-11 failed: measured {g['measured']} < target {g['target']}"


def test_g_mb_12_hardware_execution_sla(benchmark_results):
    """G-MB-12: Hardware Execution SLA (CPU <= 5.0ms, VRAM == 0MB)"""
    g = benchmark_results["gate_verdicts"]["G-MB-12"]
    assert g["passed"], f"G-MB-12 failed: measured {g['measured']} exceeded target {g['target']}"


def test_candidates_comparative_matrix_completeness(benchmark_results):
    """Asserts that all candidates C1..C5 have empirical measurements across D1..D4."""
    matrix = benchmark_results["candidates_matrix_summary"]
    for c in ["C1", "C2", "C3", "C4", "C5"]:
        assert c in matrix
        for d in range(1, 5):
            assert f"D{d}" in matrix[c]
            assert 0.0 <= matrix[c][f"D{d}"] <= 1.0


def test_overall_master_acceptance(benchmark_results):
    """Verifies that all 12/12 gates passed simultaneously."""
    assert benchmark_results["all_passed"], "Not all 12 gates passed!"

