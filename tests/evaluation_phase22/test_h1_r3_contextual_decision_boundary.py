"""
Unit and Property Test Suite: Phase 22 H1 Contextual Decision Boundary Study
=============================================================================
Test File: test_h1_r3_contextual_decision_boundary.py

Validates the empirical findings, mathematical bounds, negative controls (NC1–NC8),
replication control (RC1), decision hierarchy classification, and governance invariants
for PHASE_22_H1_CONTEXTUAL_DECISION_BOUNDARY_ACTION_SELECTION_STUDY.

Covers:
  1. Manifest & artifact integrity
  2. Corpus & matched discordant pair invariants (N=270, pairs=358)
  3. Negative Controls NC1–NC8 & Replication Control RC1
  4. Decision classification (RESULT_B: PERSISTENT_DETERMINISTIC_DISCRETIZATION)
  5. Continuous directional value displacement persistence (||Delta V_dir|| ~ 0.094 nats)
  6. Boundary dynamics (B sign flip from negative in CTX_0..CTX_4 to positive in CTX_5)
  7. Lockstep action transition (100% answer in CTX_0..CTX_4 -> 100% retrieve in CTX_5)
  8. Sub-action ranking permutation rate in CTX_5 (~79.89%)
  9. Diagnostic probabilistic policy shift (D_TV > tau_TV, D_JS > tau_JS)
  10. Strict governance invariants (Gate 2 BLOCKED, Phase 22 H1 INCONCLUSIVE, profile unmutated, 0 GPU VRAM)
"""

import csv
import json
import math
from pathlib import Path
import subprocess
import sys
from typing import Any, Dict

import numpy as np
import pytest

REPO_ROOT = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(REPO_ROOT))

from tests.evaluation_phase22.scripts.evaluate_h1_r3_contextual_decision_boundary import (
    ACTIONS,
    CONTEXT_PRAGMATIC_GRID,
    DEADBAND_EPSILON,
    EXPECTED_CORPUS_SHA,
    EXPECTED_HISTORICAL_DISCORDANT,
    EXPOSURE_TICKS,
    MASTER_SEED,
    NUM_ACTIONS,
    TOLERANCE_CORR_MAX,
    TOLERANCE_EIG,
    TOLERANCE_JS,
    TOLERANCE_TIE,
    TOLERANCE_TV,
    TOLERANCE_VAL,
    ContextualDecisionBoundaryHarness,
    deadband_sign,
    sha256_array,
    verify_corpus_sha,
)

FIXTURES_DIR = REPO_ROOT / "tests" / "evaluation_phase22" / "fixtures"


@pytest.fixture(scope="module")
def manifest() -> Dict[str, Any]:
    manifest_path = FIXTURES_DIR / "manifest_h1_r3_contextual_decision_boundary.json"
    assert manifest_path.exists(), f"Manifest not found: {manifest_path}"
    with open(manifest_path, "r", encoding="utf-8") as f:
        return json.load(f)


@pytest.fixture(scope="module")
def study_results() -> Dict[str, Any]:
    results_path = FIXTURES_DIR / "results_h1_r3_contextual_decision_boundary.json"
    assert results_path.exists(), f"Results fixture not found: {results_path}"
    with open(results_path, "r", encoding="utf-8") as f:
        return json.load(f)


@pytest.fixture(scope="module")
def nc_results() -> Dict[str, Any]:
    nc_path = FIXTURES_DIR / "nc_h1_r3_contextual_decision_boundary.json"
    assert nc_path.exists(), f"NC fixture not found: {nc_path}"
    with open(nc_path, "r", encoding="utf-8") as f:
        return json.load(f)


@pytest.fixture(scope="module")
def formal_report() -> Dict[str, Any]:
    report_path = FIXTURES_DIR / "report_h1_r3_contextual_decision_boundary.json"
    assert report_path.exists(), f"Report fixture not found: {report_path}"
    with open(report_path, "r", encoding="utf-8") as f:
        return json.load(f)


# =============================================================================
# 1. Manifest & Artifact Integrity Tests
# =============================================================================

def test_manifest_integrity(manifest: Dict[str, Any]) -> None:
    """Validate manifest schema and committed parameters."""
    assert manifest["study_id"] == "PHASE_22_H1_CONTEXTUAL_DECISION_BOUNDARY_ACTION_SELECTION_STUDY"
    assert manifest["master_seed"] == MASTER_SEED
    assert manifest["expected_n_probes"] == 270
    assert manifest["expected_discordant_pairs"] == 358
    assert len(manifest["context_pragmatic_grid"]) == 6
    assert "locked_canon_parameter_hashes" in manifest
    assert "locked_indep_parameter_hashes" in manifest
    assert "locked_control_hashes" in manifest


def test_results_fixture_integrity(study_results: Dict[str, Any]) -> None:
    """Validate that results fixture contains all 6 contexts and 4 conditions."""
    for ctx_id in CONTEXT_PRAGMATIC_GRID:
        assert ctx_id in study_results, f"Missing context {ctx_id}"
        for cond_id in ["C0", "C1", "C2", "C3"]:
            assert cond_id in study_results[ctx_id], f"Missing condition {cond_id} in {ctx_id}"
            entry = study_results[ctx_id][cond_id]
            assert entry["n_pairs"] == 358
            assert "mean_b" in entry
            assert "mean_l2_delta_v_dir" in entry
            assert "mean_delta_b_dir" in entry
            assert "d_pol" in entry
            assert "mean_policy_tv" in entry
            assert "mean_policy_js" in entry


def test_nc_fixture_integrity(nc_results: Dict[str, Any]) -> None:
    """Validate that all negative controls passed."""
    assert nc_results["all_passed"] is True
    for key in ["NC1_scalar_null", "NC2_direction_shuffled", "NC3_zero_directional_weighting",
                "NC4_deterministic_repeatability", "NC5_anti_tuning_invariance",
                "NC6_production_isolation", "NC7_genesis_gate", "NC8_context_monotonicity",
                "RC1_replication_control"]:
        assert key in nc_results
        assert nc_results[key]["passed"] is True


def test_report_fixture_integrity(formal_report: Dict[str, Any]) -> None:
    """Validate 15-point formal report structure."""
    assert formal_report["1_study_id"] == "PHASE_22_H1_CONTEXTUAL_DECISION_BOUNDARY_ACTION_SELECTION_STUDY"
    assert "2_parent_commit" in formal_report
    assert "3_hypothesis_tested" in formal_report
    assert "10_controls_evaluation" in formal_report
    assert formal_report["10_controls_evaluation"]["all_passed"] is True
    assert formal_report["11_interpretation_decision"]["code"] == "RESULT_B"
    assert formal_report["11_interpretation_decision"]["label"] == "PERSISTENT_DETERMINISTIC_DISCRETIZATION"


def test_summary_csv_integrity() -> None:
    """Validate CSV summary has exactly 24 data rows (6 contexts x 4 conditions)."""
    csv_path = FIXTURES_DIR / "summary_h1_r3_contextual_decision_boundary.csv"
    assert csv_path.exists()
    with open(csv_path, "r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        rows = list(reader)
    assert len(rows) == 24
    for row in rows:
        assert float(row["mean_l2_delta_v"]) >= 0.0
        assert float(row["tie_rate"]) == 0.0


# =============================================================================
# 2. Corpus & Pair Invariants
# =============================================================================

def test_corpus_dimensions_and_sha() -> None:
    """Verify master corpus generation dimensions and tier counts."""
    harness = ContextualDecisionBoundaryHarness()
    probes = harness.generate_master_corpus()
    assert len(probes) == 270
    assert verify_corpus_sha(probes) is True


def test_discordant_pair_count() -> None:
    """Verify exactly 358 matched discordant pairs are extracted."""
    harness = ContextualDecisionBoundaryHarness()
    harness.generate_master_corpus()
    harness.simulate_pad_trajectories(EXPOSURE_TICKS)
    pairs = harness.build_matched_discordant_pairs()
    assert len(pairs) == EXPECTED_HISTORICAL_DISCORDANT


# =============================================================================
# 3. Negative Controls NC1–NC8 & Replication Control RC1
# =============================================================================

def test_nc1_scalar_null_all_contexts(study_results: Dict[str, Any]) -> None:
    """NC1: Under scalar C0, directional value displacement is strictly zero across all contexts."""
    for ctx_id in CONTEXT_PRAGMATIC_GRID:
        c0_res = study_results[ctx_id]["C0"]
        assert c0_res["mean_l2_delta_v_dir"] <= TOLERANCE_VAL
        assert c0_res["d_pol"] == 0.0
        assert c0_res["mean_delta_b_dir"] <= TOLERANCE_VAL


def test_nc2_shuffled_correspondence(nc_results: Dict[str, Any]) -> None:
    """NC2: Direction-shuffled correspondence with C1 must be degraded (r <= 0.50)."""
    r_val = nc_results["NC2_direction_shuffled"]["details"]["pearson_r_c2_c1"]
    assert r_val <= TOLERANCE_CORR_MAX
    assert r_val < 0.15  # Observed r ~ 0.072


def test_nc3_zero_directional_weighting_identity() -> None:
    """NC3: Setting W_dir = 0 produces bit-exact scalar baseline EIG."""
    from tests.evaluation_phase22.scripts.evaluate_h1_r3_contextual_decision_boundary import (
        M_CANON_CLARIFY_BASE_LOGITS,
        M_CANON_CLARIFY_B_S,
        M_CANON_RETRIEVE_BASE_LOGITS,
        M_CANON_RETRIEVE_B_S,
        ObservationModelSpec,
        evaluate_epistemic_step,
    )
    q0 = np.full(4, 0.25, dtype=np.float64)
    zero_w_spec = ObservationModelSpec(
        model_id="M_zero_w",
        description="Zero directional weighting test",
        clarify_base_logits=M_CANON_CLARIFY_BASE_LOGITS.copy(),
        retrieve_base_logits=M_CANON_RETRIEVE_BASE_LOGITS.copy(),
        clarify_w_dir=np.zeros((4, 3), dtype=np.float64),
        retrieve_w_dir=np.zeros((4, 3), dtype=np.float64),
        clarify_b_s=M_CANON_CLARIFY_B_S.copy(),
        retrieve_b_s=M_CANON_RETRIEVE_B_S.copy(),
    )
    eig_zw, _, _, _, _, _ = evaluate_epistemic_step(zero_w_spec, q0, 0.5, np.ones(3)/math.sqrt(3.0))
    harness = ContextualDecisionBoundaryHarness()
    eig_c0, _, _, _, _, _ = evaluate_epistemic_step(harness.spec_canon_c0, q0, 0.5, np.zeros(3))
    assert np.allclose(eig_zw, eig_c0, atol=1e-15)


def test_nc4_deterministic_repeatability(nc_results: Dict[str, Any]) -> None:
    """NC4: Bit-exact repeatability across identical evaluations."""
    assert nc_results["NC4_deterministic_repeatability"]["passed"] is True


def test_nc5_anti_tuning_invariance(nc_results: Dict[str, Any]) -> None:
    """NC5: Pre-registered parameter and permutation hashes match manifest."""
    assert nc_results["NC5_anti_tuning_invariance"]["passed"] is True


def test_nc6_production_code_isolation() -> None:
    """NC6: Zero git diff in production src/core/ codebase."""
    res = subprocess.run(
        ["git", "diff", "--name-only", "HEAD", "--", "src/core"],
        cwd=str(REPO_ROOT),
        capture_output=True,
        text=True,
    )
    assert res.stdout.strip() == "", f"Production files modified: {res.stdout}"


def test_nc7_genesis_gate_invariant() -> None:
    """NC7: Genesis onboarding profile must remain bit-exact is_onboarded=False."""
    profile_path = REPO_ROOT / "data" / "profile.json"
    with open(profile_path, "r", encoding="utf-8") as f:
        data = json.load(f)
    assert data.get("is_onboarded") is False


def test_nc8_context_monotonicity(study_results: Dict[str, Any]) -> None:
    """NC8: Boundary distance B strictly increases monotonically from CTX_0 to CTX_5."""
    b_means = [study_results[f"CTX_{k}"]["C1"]["mean_b"] for k in range(6)]
    for k in range(1, 6):
        assert b_means[k] > b_means[k-1], f"Monotonicity failed at step {k}: {b_means[k]} <= {b_means[k-1]}"
        # Step size is exactly 0.20
        assert abs((b_means[k] - b_means[k-1]) - 0.20) < 1e-6


def test_rc1_replication_control(study_results: Dict[str, Any]) -> None:
    """RC1: Cross-model replication: independent observation model (C3) maintains ||Delta V_dir|| > tau_val."""
    for ctx_id in CONTEXT_PRAGMATIC_GRID:
        l2_val = study_results[ctx_id]["C3"]["mean_l2_delta_v_dir"]
        assert l2_val > TOLERANCE_VAL
        assert abs(l2_val - 0.0904) < 0.010  # Consistent ~0.090 nats


# =============================================================================
# 4. Empirical Findings & Boundary Dynamics Tests
# =============================================================================

def test_decision_hierarchy_result_b(formal_report: Dict[str, Any]) -> None:
    """Verify the top-down decision hierarchy classification is RESULT_B."""
    decision = formal_report["11_interpretation_decision"]
    assert decision["code"] == "RESULT_B"
    assert decision["label"] == "PERSISTENT_DETERMINISTIC_DISCRETIZATION"


def test_deterministic_policy_divergence_zero(study_results: Dict[str, Any]) -> None:
    """Verify D_pol == 0.0000 across all 6 contexts under C1."""
    for ctx_id in CONTEXT_PRAGMATIC_GRID:
        assert study_results[ctx_id]["C1"]["d_pol"] == 0.0000


def test_value_displacement_persistence(study_results: Dict[str, Any]) -> None:
    """Verify C1 value displacement ||Delta V_dir|| is ~0.0937 nats across all contexts."""
    for ctx_id in CONTEXT_PRAGMATIC_GRID:
        l2 = study_results[ctx_id]["C1"]["mean_l2_delta_v_dir"]
        assert abs(l2 - 0.093653) < 1e-4
        assert l2 > TOLERANCE_VAL


def test_boundary_shift_persistence(study_results: Dict[str, Any]) -> None:
    """Verify directional boundary displacement Delta B_dir is ~0.0299 nats across all contexts."""
    for ctx_id in CONTEXT_PRAGMATIC_GRID:
        db = study_results[ctx_id]["C1"]["mean_delta_b_dir"]
        assert abs(db - 0.029858) < 1e-4
        assert db > TOLERANCE_VAL


def test_boundary_sign_flip_at_ctx5(study_results: Dict[str, Any]) -> None:
    """Verify mean boundary distance B is negative in CTX_0..CTX_4 and flips positive in CTX_5."""
    for k in range(5):
        assert study_results[f"CTX_{k}"]["C1"]["mean_b"] < 0.0
    assert study_results["CTX_5"]["C1"]["mean_b"] > 0.0
    assert study_results["CTX_5"]["C1"]["mean_b"] > 0.10  # ~ +0.112 nats


def test_lockstep_action_transition(study_results: Dict[str, Any]) -> None:
    """Verify actions transition in lockstep from 100% 'answer' to 100% 'retrieve'."""
    for k in range(5):
        dist = study_results[f"CTX_{k}"]["C1"]["action_distribution"]
        assert dist.get("answer") == 716
        assert len(dist) == 1

    dist_5 = study_results["CTX_5"]["C1"]["action_distribution"]
    assert dist_5.get("retrieve") == 716
    assert len(dist_5) == 1


def test_subaction_ranking_change_ctx5(study_results: Dict[str, Any]) -> None:
    """Verify sub-action ranking permutation rate is ~79.89% in CTX_5."""
    rate = study_results["CTX_5"]["C1"]["ranking_change_rate"]
    assert abs(rate - 0.79888) < 0.001
    assert rate > 0.70


def test_probabilistic_policy_divergence(study_results: Dict[str, Any]) -> None:
    """Verify diagnostic probabilistic branch exhibits significant continuous divergence across all contexts."""
    for ctx_id in CONTEXT_PRAGMATIC_GRID:
        tv = study_results[ctx_id]["C1"]["mean_policy_tv"]
        js = study_results[ctx_id]["C1"]["mean_policy_js"]
        assert tv > TOLERANCE_TV
        assert js > TOLERANCE_JS
        assert tv > 0.010  # ~ 0.011 to 0.014


def test_probabilistic_tv_increases_with_context(study_results: Dict[str, Any]) -> None:
    """Verify Total Variation distance strictly increases as pragmatic certainty decreases."""
    tv_vals = [study_results[f"CTX_{k}"]["C1"]["mean_policy_tv"] for k in range(6)]
    for k in range(1, 6):
        assert tv_vals[k] > tv_vals[k-1]


def test_tie_rate_zero(study_results: Dict[str, Any]) -> None:
    """Verify tie rate is exactly 0.0 under tolerance tau_tie = 1e-6."""
    for ctx_id in CONTEXT_PRAGMATIC_GRID:
        for cond_id in ["C0", "C1", "C2", "C3"]:
            assert study_results[ctx_id][cond_id]["tie_rate"] == 0.0


def test_bootstrap_confidence_intervals(study_results: Dict[str, Any]) -> None:
    """Verify non-parametric bootstrap 95% CIs are well-formed and positive for C1 value displacement."""
    for ctx_id in CONTEXT_PRAGMATIC_GRID:
        ci_l2 = study_results[ctx_id]["C1"]["bootstrap_95ci_l2_delta_v_dir"]
        assert ci_l2[0] < ci_l2[1]
        assert ci_l2[0] > 0.085
        assert ci_l2[1] < 0.100


# =============================================================================
# 5. Governance & Invariant Tests
# =============================================================================

def test_gate2_blocked_invariant(formal_report: Dict[str, Any]) -> None:
    """Verify Gate 2 remains strictly blocked and ADR-029 unratified."""
    assert "STRICTLY BLOCKED" in formal_report["12_gate_2_status"]
    assert "DRAFT" in formal_report["13_adr029_status"]


def test_cpu_only_execution(formal_report: Dict[str, Any]) -> None:
    """Verify CPU-only execution with 0.0 MB GPU VRAM."""
    assert formal_report["14_production_integrity"]["gpu_vram_mb"] == 0.0
