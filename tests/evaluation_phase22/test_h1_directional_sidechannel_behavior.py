"""
tests/evaluation_phase22/test_h1_directional_sidechannel_behavior.py

Validation suite for Phase 22 H1 Directional Side-Channel Behavioral Utilization Study.

Verifies:
1. Manifest and results file integrity (SHA-256 match, schema completeness).
2. Strict governance invariants (H1 INCONCLUSIVE, Gate 2 BLOCKED, 0 mutations).
3. Methodological scope locks (isolated research adapter, counterfactual validity,
   exploratory classification threshold, ternary sign representation).
4. RQ1 Behavioral Sensitivity (C1 and C2 exceed exploratory threshold).
5. RQ2 Continuous vs Discrete Information (Test 2A & 2B results).
6. RQ3 Collapse Pairs Behavioral Differentiation (358 pairs at T=12).
7. RQ4 Directional Component Correlations (v_P, v_D, v_A).
8. RQ5 Scalar Surprise Monotonicity Preservation.
9. RQ6 Null Shuffle Controls (C1 vs C4, C2 vs C5).
10. State Classification: State B (R3 Discrete Behavioral Sufficiency).
"""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
import pytest

REPO_ROOT = Path(__file__).resolve().parent.parent.parent
RESULTS_FILE = REPO_ROOT / "tests" / "evaluation_phase22" / "results" / "h1_directional_sidechannel_behavior" / "directional_behavior_results.json"
MANIFEST_FILE = REPO_ROOT / "tests" / "evaluation_phase22" / "fixtures" / "manifest_h1_directional_sidechannel_behavior.json"
GENESIS_PROFILE = REPO_ROOT / "data" / "profile.json"


@pytest.fixture(scope="module")
def results_data() -> dict:
    assert RESULTS_FILE.exists(), f"Results file missing: {RESULTS_FILE}"
    with open(RESULTS_FILE, "r", encoding="utf-8") as f:
        return json.load(f)


@pytest.fixture(scope="module")
def manifest_data() -> dict:
    assert MANIFEST_FILE.exists(), f"Manifest file missing: {MANIFEST_FILE}"
    with open(MANIFEST_FILE, "r", encoding="utf-8") as f:
        return json.load(f)


def test_01_manifest_and_file_integrity(results_data: dict, manifest_data: dict):
    """Test 1: Verify manifest exists, valid JSON, and SHA-256 matches bit-exact."""
    with open(RESULTS_FILE, "rb") as f:
        computed_sha = hashlib.sha256(f.read()).hexdigest()

    manifest_sha = manifest_data["files"]["directional_behavior_results.json"]["sha256"]
    assert computed_sha == manifest_sha, f"SHA-256 mismatch: {computed_sha} != {manifest_sha}"
    assert results_data["metadata"]["status"] == "COMPLETED"
    assert results_data["metadata"]["n_probes"] == 270


def test_02_governance_invariants(results_data: dict, manifest_data: dict):
    """Test 2: Verify all strict governance invariants remain locked."""
    gov = results_data["metadata"]["governance"]
    assert gov["phase_22_h1"] == "INCONCLUSIVE"
    assert gov["gate_2"] == "BLOCKED"
    assert gov["protocol_v1_5"] == "NOT AUTHORIZED"
    assert gov["architecture_gate"] == "STRICTLY LOCKED"
    assert gov["src_core_mutations"] == 0
    assert gov["genesis_profile"] == "PRESERVED_BIT_EXACT"

    # Verify genesis profile on disk
    assert GENESIS_PROFILE.exists()
    with open(GENESIS_PROFILE, "r", encoding="utf-8") as f:
        profile = json.load(f)
    assert profile.get("is_onboarded") is False


def test_03_methodology_locks_recorded(results_data: dict, manifest_data: dict):
    """Test 3: Verify the 7 mandatory user methodological locks are formally registered."""
    locks = manifest_data["methodology_locks"]
    assert "downstream policy/conditioning utilization" in locks["behavioral_scope"].lower()
    assert "counterfactual_validity" in locks
    assert "predefined exploratory classification threshold" in locks["classification_threshold"].lower()
    assert "ternary sign symbols" in locks["r3_representation"].lower()
    assert "dual_metric_evaluation" in locks
    assert "rq5_observed_monotonicity_scope" in locks
    assert "missing_sidechannel_invariant" in locks


def test_04_rq1_behavioral_sensitivity(results_data: dict):
    """Test 4: Verify RQ1 behavioral sensitivity exceeds exploratory threshold with dual metrics."""
    rq1 = results_data["rq1_behavioral_sensitivity"]
    for t_str in ["1", "2", "4", "8", "12", "16", "25"]:
        t_data = rq1[t_str]
        # Discrete argmax policy switch rate
        assert t_data["d_pol_c1"] >= 0.05
        assert t_data["p_val_c1"] < 0.05
        assert t_data["passes_exploratory_threshold_c1"] is True
        # Continuous policy distribution shift (JS divergence and TV distance)
        assert t_data["mean_d_js_c1"] > 0.0
        assert t_data["mean_d_js_c2"] > 0.0
        assert t_data["mean_d_tv_c1"] > 0.0
        assert t_data["mean_d_tv_c2"] > 0.0
        # Missing side-channel semantics invariant: C3 (zeroed direction) has 0 discrete shift and negligible divergence
        assert t_data["d_pol_c3"] == 0.0
        assert t_data["mean_d_js_c3"] < 1e-5

    # At T=12, verify specific metrics
    t12 = rq1["12"]
    assert t12["d_pol_c1"] == pytest.approx(0.4963, abs=1e-3)
    assert t12["d_pol_c2"] == pytest.approx(1.0000, abs=1e-3)
    assert t12["mean_d_js_c1"] == pytest.approx(0.000728, abs=1e-5)
    assert t12["mean_d_js_c2"] == pytest.approx(0.002194, abs=1e-5)
    assert t12["passes_exploratory_threshold_c2"] is True


def test_05_rq2_continuous_vs_discrete_tests(results_data: dict):
    """Test 5: Verify RQ2 Test 2A within-quadrant and Test 2B sign transition results."""
    rq2 = results_data["rq2_continuous_vs_discrete"]
    t12 = rq2["12"]
    # Test 2A: identical signs produce no additional divergence for C1
    assert t12["d_pol_test_2a_c1_continuous"] == 0.0
    assert t12["c1_additional_value_in_same_sign"] is False

    # Test 2B: discrete sign transitions produce strong, statistically significant divergence
    assert t12["n_test_2b_pairs"] > 0
    assert t12["d_pol_test_2b_c2_discrete"] >= 0.05
    assert t12["p_val_test_2b"] < 0.05
    assert t12["c2_sufficient_for_sign_transition"] is True


def test_06_rq3_collapse_pairs_differentiation(results_data: dict):
    """Test 6: Verify RQ3 differentiation on the 358 Medium-High collapse pairs at T=12."""
    rq3 = results_data["rq3_utilization_vs_geometric"]
    assert rq3["n_collapse_pairs_at_t12"] == 358

    rates = rq3["action_differentiation_rate"]
    assert rates["c0_scalar"] == 0.0
    assert rates["c1_continuous"] == pytest.approx(0.7989, abs=1e-3)
    assert rates["c2_ternary_signs"] == pytest.approx(0.7989, abs=1e-3)

    # C2 matches C1 differentiation bit-exact on collapse pairs
    assert rates["c2_ternary_signs"] == rates["c1_continuous"]
    assert rq3["p_val_action_c1_vs_c0"] < 1e-10
    assert rq3["p_val_action_c2_vs_c0"] < 1e-10

    # Policy distribution divergence
    js_div = rq3["pair_policy_distribution_divergence_mean_d_js"]
    assert js_div["c0_scalar"] < 1e-5
    assert js_div["c1_continuous"] > 1e-3
    assert js_div["c2_ternary_signs"] > 1e-3


def test_07_rq4_directional_correlations(results_data: dict):
    """Test 7: Verify RQ4 directional axis correlations with downstream policies."""
    corrs = results_data["rq4_directional_effects"]["spearman_correlations"]
    r_vp = corrs["valence_vs_supportiveness"]["r"]
    r_vd = corrs["dominance_vs_directness"]["r"]

    assert r_vp > 0.90, f"v_P vs supportiveness correlation too low: {r_vp}"
    assert r_vd > 0.90, f"v_D vs directness correlation too low: {r_vd}"


def test_08_rq5_scalar_preservation(results_data: dict):
    """Test 8: Verify RQ5 scalar surprise preservation of intensity/gating role."""
    rq5 = results_data["rq5_scalar_preservation"]
    assert rq5["evaluation_scope"] == "observed_monotonic_association_across_frozen_stimuli_and_exposures"
    for cond in ["C0", "C1", "C2", "C3"]:
        assert rq5[cond]["scalar_monotonicity_preserved"] is True
        assert rq5[cond]["spearman_s_vs_cognitive_load"] >= 0.85
        assert rq5[cond]["spearman_s_vs_tension"] >= 0.80


def test_09_rq6_null_shuffle_controls(results_data: dict):
    """Test 9: Verify RQ6 null shuffle controls break semantic correspondence."""
    rq6 = results_data["rq6_null_controls"]
    for t_str in ["1", "2", "4", "8", "12", "16", "25"]:
        t_data = rq6[t_str]
        assert t_data["discordance_c1_vs_c4_null"] >= 0.05
        assert t_data["discordance_c2_vs_c5_null"] >= 0.05
        assert t_data["p_val_c1_vs_c4"] < 1e-10
        assert t_data["p_val_c2_vs_c5"] < 1e-10
        assert t_data["true_channel_significantly_distinct_from_null"] is True


def test_10_state_classification_state_b(results_data: dict, manifest_data: dict):
    """Test 10: Verify final classification is State B (R3 Discrete Behavioral Sufficiency)."""
    state_res = results_data["state_classification"]
    assert state_res["assigned_state"] == "STATE_B"
    assert manifest_data["assigned_state"] == "STATE_B"
    assert "State B — R3 Discrete Behavioral Sufficiency" in state_res["title"]
    assert state_res["metrics_at_t12"]["d_pol_c2"] >= 0.05
    assert state_res["metrics_at_t12"]["d_pol_test_2a_c1_in_same_sign"] == 0.0
