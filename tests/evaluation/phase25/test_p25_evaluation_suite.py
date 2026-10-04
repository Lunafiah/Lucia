"""
tests/evaluation/phase25/test_p25_evaluation_suite.py

Automated Test Suite for Phase 25 Evaluation Harness & Research Validation.
Verifies all 5 evaluation tracks, scientific invariants, boundary constraints,
and P25-Q1 research discipline under pytest.
"""

from __future__ import annotations

import json
from pathlib import Path
import pytest
import numpy as np

PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent.parent
from tests.evaluation.phase25.e1_recovery_asymmetry import E1RecoveryAsymmetryEvaluator
from tests.evaluation.phase25.e2_repair_dynamics import E2RepairDynamicsEvaluator
from tests.evaluation.phase25.e3_embodied_feedback import E3EmbodiedFeedbackEvaluator, EmbodiedDynamicalSystem
from tests.evaluation.phase25.e4_conversational_entrainment import E4ConversationalEntrainmentEvaluator
from tests.evaluation.phase25.e5_peripheral_authority import E5PeripheralAuthorityEvaluator
from tests.evaluation.phase25.models import (
    DirectnessMetric,
    SocialPredictionError,
    SupportivenessMetric,
)


@pytest.fixture(scope="module")
def e1_benchmark_results():
    evaluator = E1RecoveryAsymmetryEvaluator(random_seed=42)
    summary, trials = evaluator.run_benchmark(num_trials=8)
    return summary, trials


@pytest.fixture(scope="module")
def e2_benchmark_results():
    evaluator = E2RepairDynamicsEvaluator(random_seed=42)
    summary, trials = evaluator.run_benchmark(num_trials=8)
    return summary, trials


@pytest.fixture(scope="module")
def e3_benchmark_results():
    evaluator = E3EmbodiedFeedbackEvaluator(random_seed=42)
    summary, conditions = evaluator.run_benchmark()
    return summary, conditions


@pytest.fixture(scope="module")
def e4_benchmark_results():
    evaluator = E4ConversationalEntrainmentEvaluator(random_seed=42)
    summary, metrics = evaluator.run_sweep(
        candidate_gammas=[0.00, 0.05, 0.10, 0.20, 0.30, 0.50, 0.80],
        num_turns=100,
    )
    return summary, metrics


@pytest.fixture(scope="module")
def e5_benchmark_results():
    evaluator = E5PeripheralAuthorityEvaluator(random_seed=42)
    summary, reports = evaluator.run_benchmark()
    return summary, reports


# ============================================================================
# TRACK E1: RELATIONAL RECOVERY ASYMMETRY
# ============================================================================

def test_e1_relational_consequence_persists_beyond_affective_recovery(e1_benchmark_results):
    """Verify that negative rupture leaves persistent relational displacement after PAD relaxes to Philia."""
    summary, trials = e1_benchmark_results
    assert summary.persistent_relational_consequence_observed is True
    assert summary.negative_rel_residual_mean > summary.neutral_control_residual_mean
    # At the step where PAD relaxed to Philia, relational displacement must remain strictly positive
    neg_trials = [t for t in trials if t.condition_name == "negative_rupture"]
    assert len(neg_trials) > 0
    for t in neg_trials:
        assert t.relational_displacement_at_affective_recovery > 0.02, (
            f"Relational displacement collapsed immediately upon affective relaxation for intensity {t.intensity}"
        )


def test_e1_no_hardcoded_thresholds_or_mandatory_classes(e1_benchmark_results):
    """Ensure E1 does not hardcode R_trust <= 0.40 or enforce a mandatory RepairEvent class."""
    summary, trials = e1_benchmark_results
    # Trust values should vary smoothly with intensity rather than snapping to a hard threshold
    neg_trials = [t for t in trials if t.condition_name == "negative_rupture"]
    post_trusts = [t.trust_post_perturbation for t in neg_trials]
    # Verify values are continuous and not identical constants
    assert len(set(round(x, 4) for x in post_trusts)) > 1
    # Check that asymmetry index is reported with statistical bounds
    assert summary.asymmetry_index_mean > 0.0
    assert len(summary.asymmetry_index_ci95) == 2


# ============================================================================
# TRACK E2: REPAIR VS ORDINARY INTERACTION
# ============================================================================

def test_e2_repair_exhibits_lower_spe_and_higher_directness(e2_benchmark_results):
    """Verify explicit repair achieves lower SPE, higher Directness, and higher Supportiveness than neutral."""
    summary, trials = e2_benchmark_results
    assert summary.measurable_separation_observed is True
    assert summary.mean_repair_spe < summary.mean_no_repair_spe
    assert summary.spe_diff_mean > 0.0
    assert summary.mean_repair_directness > summary.mean_no_repair_directness
    assert summary.mean_repair_supportiveness > summary.mean_no_repair_supportiveness


def test_e2_metrics_are_evaluation_only(e2_benchmark_results):
    """Verify that evaluation metrics do NOT leak into production ontology."""
    # Ensure SocialPredictionError is an evaluation metric class, not in src.core
    import src.core.relationship.state as rel_state
    assert not hasattr(rel_state, "RelationalRupture")
    assert not hasattr(rel_state, "RepairEvent")
    assert not hasattr(rel_state, "SocialPredictionError")


# ============================================================================
# TRACK E3: EMBODIED RECIPROCAL FEEDBACK
# ============================================================================

def test_e3_dissipativity_diagnostic_volume_contraction(e3_benchmark_results):
    """Verify phase-space volume contraction Tr(J) < 0 for both open-loop and closed-loop."""
    summary, conditions = e3_benchmark_results
    assert summary.output_only_trace < 0.0
    assert summary.reciprocal_trace < 0.0
    assert summary.dissipativity_diagnostic_passed is True


def test_e3_lyapunov_claim_prohibition_strictly_honored(e3_benchmark_results):
    """CRITICAL: Ensure the system explicitly disclaims claiming Tr(J) < 0 implies Lyapunov stability."""
    summary, conditions = e3_benchmark_results
    assert summary.lyapunov_disclaimer_honored is True
    for cond_name, telem in conditions.items():
        assert "does NOT imply Lyapunov stability" in telem.trace_interpretation


# ============================================================================
# TRACK E4: CONVERSATIONAL ENTRAINMENT SWEEP
# ============================================================================

def test_e4_parameter_sweep_coverage_and_boundedness(e4_benchmark_results):
    """Verify complete parameter sweep across gamma values without unbounded drift."""
    summary, metrics = e4_benchmark_results
    assert len(summary.sweep_configurations) >= 5
    assert summary.all_sweeps_bounded is True
    for key, metric_dict in summary.metrics_per_gamma.items():
        assert metric_dict["bounded_stability_ratio"] >= 0.95
        assert metric_dict["mean_cpu_time_us"] > 0.0


def test_e4_no_architecture_promotion_guard(e4_benchmark_results):
    """Verify that entrainment coupling values remain experimental only, not in production config."""
    from src.core.config import EmotionConfig
    cfg = EmotionConfig()
    assert not hasattr(cfg, "conversational_entrainment_gamma")
    assert not hasattr(cfg, "canonical_entrainment_coupling")


# ============================================================================
# TRACK E5: PERIPHERAL AUTHORITY CONTENTION
# ============================================================================

def test_e5_fault_model_detects_contention_failure_modes(e5_benchmark_results):
    """Verify that multiple continuous cognitive authorities cause split-brain divergence."""
    summary, reports = e5_benchmark_results
    assert "split_brain" in reports
    assert reports["split_brain"].split_brain_detected is True
    assert summary.split_brain_divergence_max > 0.10
    # Race condition detected
    assert "race_condition" in reports
    assert reports["race_condition"].conflicting_write_count > 0
    # Ordering inversion detected
    assert "ordering_inversion" in reports
    assert reports["ordering_inversion"].observed_divergence > 0.0


def test_e5_no_universal_prevention_claimed(e5_benchmark_results):
    """CRITICAL: Ensure finite testing does NOT claim 100% universal prevention."""
    summary, reports = e5_benchmark_results
    assert summary.no_universal_prevention_claimed is True
    assert "Finite test passing does NOT guarantee universal 100% prevention" in summary.p25_q1_implication


# ============================================================================
# RESEARCH INVARIANTS & GENESIS SAFEGUARD
# ============================================================================

def test_genesis_onboarding_status_strictly_preserved():
    """Verify that data/profile.json remains bit-exact: {"is_onboarded": false}."""
    profile_path = PROJECT_ROOT / "data" / "profile.json"
    assert profile_path.exists(), "data/profile.json is missing!"
    with open(profile_path, "r", encoding="utf-8") as f:
        data = json.load(f)
    assert data == {"is_onboarded": False}, f"Genesis gate violated! Found: {data}"


def test_p25_q1_scientific_null_result_permitted():
    """Verify that P25-Q1 evaluation allows the null result and reports INCONCLUSIVE."""
    runner_path = PROJECT_ROOT / "tests" / "evaluation" / "phase25" / "run_p25_evaluation.py"
    with open(runner_path, "r", encoding="utf-8") as f:
        content = f.read()
    assert "INCONCLUSIVE — MORE RESEARCH REQUIRED" in content
    assert "No new representation/mechanism is necessary" in content
