"""
tests/evaluation/phase25/test_p25_discrim.py

Automated Test Suite for EXP-P25-DISCRIM (Phase 25 Discrimination Experiment).
Verifies methodological validity, hypothesis testing (H-A vs H-B vs H-C),
affective decoupling, probe neutrality, and epistemic boundaries under pytest.
"""

from __future__ import annotations

import json
from pathlib import Path
import pytest
import numpy as np

PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent.parent

from tests.evaluation.phase25.exp_p25_discrim import (
    DiscrimConfig,
    DiscrimExperimentSummary,
    P25DiscrimEvaluator,
    PHILIA_PAD,
)
from src.core.relationship.state import RelationshipState


@pytest.fixture(scope="module")
def discrim_benchmark():
    evaluator = P25DiscrimEvaluator(DiscrimConfig(random_seed=42))
    summary, trials = evaluator.run_benchmark(num_trials=8)
    return summary, trials


# ============================================================================
# 1. METHODOLOGY VALIDATION TESTS
# ============================================================================

def test_methodology_canonical_rt_definition():
    """Verify canonical 4D R_t state representation [Trust, Familiarity, Closeness, Reciprocity]."""
    rel = RelationshipState.initial()
    arr = rel.to_array()
    assert len(arr) == 4, f"R_t must be 4-dimensional, got {len(arr)}"
    assert np.all((arr >= 0.0) & (arr <= 1.0)), "R_t coordinates must lie in [0, 1]^4"
    d = rel.to_dict()
    assert "trust" in d and "familiarity" in d and "closeness" in d and "reciprocity" in d


def test_methodology_affective_decoupling(discrim_benchmark):
    """Verify R_t is strictly decoupled from PAD and both histories relax to Philia before probe."""
    summary, trials = discrim_benchmark
    assert summary.mean_pad_residual <= 1e-4, (
        f"Mean PAD residual {summary.mean_pad_residual} exceeded threshold 1e-4"
    )
    assert summary.mean_pad_leakage <= 1e-4, (
        f"Mean PAD leakage {summary.mean_pad_leakage} exceeded threshold 1e-4"
    )
    for t in trials:
        assert t.pad_a_residual <= 1e-4
        assert t.pad_b_residual <= 1e-4
        assert t.pad_leakage_distance <= 1e-4


def test_methodology_matched_convergent_rt(discrim_benchmark):
    """Verify History A and History B converge to nearly identical R_t within tolerance."""
    summary, trials = discrim_benchmark
    assert summary.max_r_distance <= 0.005, (
        f"Max R_t distance {summary.max_r_distance} exceeded tolerance 0.005"
    )
    for t in trials:
        assert t.r_distance <= 0.005


def test_methodology_neutral_probe_non_encoding(discrim_benchmark):
    """Verify the future conversational probe is neutral and does not hardcode expected answers."""
    _, trials = discrim_benchmark
    probe = trials[0].probe_text
    # Probe must be the exact same for all trials
    for t in trials:
        assert t.probe_text == probe
    # Must not contain biased prescriptive guidance
    for forbidden in ["be cautious", "you should be angry", "broken trust", "act reserved", "cautious response"]:
        assert forbidden not in probe.lower(), f"Probe contained prescriptive oracle bias: {forbidden}"


# ============================================================================
# 2. HYPOTHESIS TESTING: H-A (CONDITION A)
# ============================================================================

def test_condition_a_fails_to_distinguish_histories(discrim_benchmark):
    """
    Verify Condition A (R_t alone, memory disabled) fails to differentiate histories.
    Yields evidence against Hypothesis H-A.
    """
    summary, trials = discrim_benchmark
    assert summary.cond_a_success_rate == 0.0, (
        f"Condition A should not distinguish histories when R_t is matched, got success rate {summary.cond_a_success_rate}"
    )
    assert summary.mean_cond_a_diff < 0.05, (
        f"Mean Delta S in Condition A ({summary.mean_cond_a_diff}) was not < 0.05"
    )
    assert summary.h_a_supported is False, "H-A must not be supported"


# ============================================================================
# 3. HYPOTHESIS TESTING: H-B (CONDITION B)
# ============================================================================

def test_condition_b_distinguishes_histories_with_existing_memory(discrim_benchmark):
    """
    Verify Condition B (R_t + existing memory/semantic substrates) successfully differentiates histories.
    Yields evidence supporting Hypothesis H-B for the tested configuration.
    """
    summary, trials = discrim_benchmark
    assert summary.cond_b_success_rate == 1.0, (
        f"Condition B failed to distinguish histories across all trials: {summary.cond_b_success_rate}"
    )
    assert summary.mean_cond_b_diff >= 0.15, (
        f"Mean Delta S in Condition B ({summary.mean_cond_b_diff}) was not >= 0.15"
    )
    assert summary.h_b_supported_for_tested_config is True, "H-B must be supported for tested configuration"
    for t in trials:
        assert t.retrieval_success_b is True
        assert t.cond_b_distinguished is True


def test_difference_causally_attributed_to_retrieved_history(discrim_benchmark):
    """
    Verify the output difference in Condition B is causally attributable to memory retrieval.
    When memory is disabled (Condition A), difference collapses to near-zero.
    """
    summary, trials = discrim_benchmark
    # Ratio between Condition B diff and Condition A diff should be > 100x
    ratio = summary.mean_cond_b_diff / max(summary.mean_cond_a_diff, 1e-9)
    assert ratio > 100.0, f"Condition B differentiation was not sufficiently larger than Condition A: ratio={ratio}"


# ============================================================================
# 4. EPISTEMIC BOUNDS & NO UNWARRANTED PROMOTION
# ============================================================================

def test_epistemic_bounds_and_inconclusive_verdict(discrim_benchmark):
    """Verify strict epistemic boundaries: H-B is not claimed universally, P25-Q1 remains INCONCLUSIVE."""
    summary, _ = discrim_benchmark
    assert "INCONCLUSIVE — MORE RESEARCH REQUIRED" in summary.epistemic_conclusion
    assert "tested configuration" in summary.epistemic_conclusion
    assert summary.h_c_indicated is False, "H-C should not be promoted when H-B succeeds on tested config"
    assert len(summary.limitations) > 20


# ============================================================================
# 5. SAFETY & INVARIANT CHECKS
# ============================================================================

def test_genesis_invariant_preserved():
    """Verify data/profile.json remains exactly bit-exact {"is_onboarded": false}."""
    profile_path = PROJECT_ROOT / "data" / "profile.json"
    with open(profile_path, "r", encoding="utf-8") as f:
        data = json.load(f)
    assert data == {"is_onboarded": False}


def test_no_forbidden_production_classes_introduced():
    """Verify that no unratified classes or expanding models were imported into production."""
    import src.core.relationship.state as rstate
    assert not hasattr(rstate, "RelationalRupture")
    assert not hasattr(rstate, "RepairEvent")
    assert not hasattr(rstate, "JTMS")
