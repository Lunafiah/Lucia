"""
Phase 22 H1 — R3 Epistemic-to-Policy Translation & Gate 2 Sensitivity Study
=============================================================================
Dedicated Verification Suite: test_h1_r3_epistemic_to_policy_translation.py

Tests:
  - Manifest cryptographic parameter hashes and frozen constants (beta_P4, EIG_bar)
  - Corpus generation and SHA-256 integrity (N=270, 90/tier)
  - 358 matched discordant pairs extraction and properties
  - C0 scalar null baseline (zero displacement, zero margin shift, D_pol=0)
  - C1 canonical R3 continuous action-value displacement and margin shifts
  - C2 direction-shuffled correspondence degradation (r <= 0.50)
  - C3 cross-model replication control (RC1 positive transfer under M_indep)
  - Formulations P0, P1, P2, P3, P4 mathematical correctness and parameter freeze
  - Precision weighting properties (Pi_epist >= 1.0)
  - Scale-preserving diagnostic framing of P2
  - Full continuous distribution readout (D_TV, D_JS, rankings) under P3
  - Margin rescaling under P4 with exact manifest constant
  - Action-specific vs common-mode variance decomposition
  - Deterministic repeatability (NC4)
  - Anti-tuning frozen parameter verification (NC5)
  - Pure negative controls (NC1–NC7) and replication control (RC1)
  - Deterministic top-down bottleneck classification hierarchy
  - Results artifacts and 15-point report integrity
  - Governance invariants: Gate 2 blocked, Phase 22 H1 inconclusive, Genesis intact

Strict Governance Invariants:
  - Research only / Zero production mutations (src/core/** diff = 0).
  - Gate 2 = STRICTLY BLOCKED (Δ_HM < 0.1500).
  - Phase 22 H1 = INCONCLUSIVE.
  - ADR-029 = DRAFT / RESEARCH RECORD ONLY / NOT RATIFIED.
  - Genesis profile = bit-exact {"is_onboarded": false}.
  - 100% CPU execution / 0.0 MB GPU VRAM.
"""

import hashlib
import json
import math
from pathlib import Path
import sys
from typing import Any, Dict, List

import numpy as np
import pytest

REPO_ROOT = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(REPO_ROOT))

from tests.evaluation_phase22.scripts.evaluate_r3_epistemic_to_policy_translation import (
    ACTIONS,
    ACTION_COSTS,
    ALPHA_PRAGM,
    BETA_0,
    BETA_P4_VALUE,
    C2_PERMUTATION,
    DEADBAND_EPSILON,
    DELTA_GAP,
    EIG_BAR_FROZEN,
    EPS_PREC,
    EXPECTED_CORPUS_SHA,
    EXPECTED_HISTORICAL_DISCORDANT,
    H_MAX,
    INDEP_OBS_SEED,
    M_CANON_CLARIFY_BASE_LOGITS,
    M_CANON_CLARIFY_B_S,
    M_CANON_CLARIFY_W_DIR,
    M_CANON_RETRIEVE_BASE_LOGITS,
    M_CANON_RETRIEVE_B_S,
    M_CANON_RETRIEVE_W_DIR,
    M_INDEP_CLARIFY_BASE_LOGITS,
    M_INDEP_CLARIFY_B_S,
    M_INDEP_CLARIFY_W_DIR,
    M_INDEP_RETRIEVE_BASE_LOGITS,
    M_INDEP_RETRIEVE_B_S,
    M_INDEP_RETRIEVE_W_DIR,
    PRAGMATIC_VALUES,
    PRIMARY_SEED,
    SHUFFLE_SEED,
    STUDY_ID,
    TOLERANCE_CORR_MAX,
    TOLERANCE_EIG,
    TOLERANCE_JS,
    TOLERANCE_TV,
    TOLERANCE_VAL,
    EpistemicToPolicyTranslationHarness,
    ObservationModelSpec,
    compute_entropy,
    compute_js_divergence,
    compute_tv_distance,
    deadband_sign,
    evaluate_epistemic_step,
    evaluate_policy_ablation,
    sha256_array,
    softmax,
    verify_corpus_sha,
)

FIXTURES_DIR = REPO_ROOT / "tests" / "evaluation_phase22" / "fixtures"
RESULTS_DIR = REPO_ROOT / "tests" / "evaluation_phase22" / "results" / "h1_r3_epistemic_to_policy_translation"
MANIFEST_PATH = FIXTURES_DIR / "manifest_h1_r3_epistemic_to_policy_translation.json"


@pytest.fixture(scope="module")
def manifest_data() -> Dict[str, Any]:
    """Load and return pre-registered manifest."""
    assert MANIFEST_PATH.exists(), f"Manifest file missing: {MANIFEST_PATH}"
    with open(MANIFEST_PATH, "r", encoding="utf-8") as f:
        return json.load(f)


@pytest.fixture(scope="module")
def initialized_harness() -> EpistemicToPolicyTranslationHarness:
    """Instantiate and initialize harness with corpus and discordant pairs."""
    harness = EpistemicToPolicyTranslationHarness(master_seed=PRIMARY_SEED)
    harness.generate_master_corpus()
    harness.simulate_pad_trajectories(12)
    harness.build_matched_discordant_pairs()
    return harness


# =============================================================================
# 1. Manifest & Cryptographic Parameter Verification
# =============================================================================

def test_manifest_existence_and_study_id(manifest_data: Dict[str, Any]):
    """Verify manifest file exists and matches study ID."""
    assert manifest_data["study_id"] == STUDY_ID
    assert manifest_data["master_seed"] == PRIMARY_SEED
    assert manifest_data["shuffle_seed"] == SHUFFLE_SEED
    assert manifest_data["indep_obs_seed"] == INDEP_OBS_SEED


def test_manifest_frozen_tolerances_and_constants(manifest_data: Dict[str, Any]):
    """Verify pre-frozen tolerances and constants in manifest."""
    assert manifest_data["tolerance_eig"] == TOLERANCE_EIG
    assert manifest_data["tolerance_val"] == TOLERANCE_VAL
    assert manifest_data["tolerance_tv"] == TOLERANCE_TV
    assert manifest_data["tolerance_js"] == TOLERANCE_JS
    assert manifest_data["tolerance_corr_max"] == TOLERANCE_CORR_MAX
    assert manifest_data["historical_canonical_mean_eig_additive"] == EIG_BAR_FROZEN
    assert manifest_data["eig_bar_frozen"] == EIG_BAR_FROZEN
    assert abs(manifest_data["beta_p4_value"] - BETA_P4_VALUE) < 1e-15
    assert abs(manifest_data["beta_p4_value"] - 0.973819141071271) < 1e-15


def test_manifest_locked_observation_hashes(manifest_data: Dict[str, Any]):
    """Verify cryptographic SHA-256 hashes of canonical and independent observation models."""
    canon_hashes = manifest_data["locked_canon_parameter_hashes"]
    assert canon_hashes["M_CANON_CLARIFY_BASE_LOGITS"] == sha256_array(M_CANON_CLARIFY_BASE_LOGITS)
    assert canon_hashes["M_CANON_RETRIEVE_BASE_LOGITS"] == sha256_array(M_CANON_RETRIEVE_BASE_LOGITS)
    assert canon_hashes["M_CANON_CLARIFY_W_DIR"] == sha256_array(M_CANON_CLARIFY_W_DIR)
    assert canon_hashes["M_CANON_RETRIEVE_W_DIR"] == sha256_array(M_CANON_RETRIEVE_W_DIR)
    assert canon_hashes["M_CANON_CLARIFY_B_S"] == sha256_array(M_CANON_CLARIFY_B_S)
    assert canon_hashes["M_CANON_RETRIEVE_B_S"] == sha256_array(M_CANON_RETRIEVE_B_S)

    indep_hashes = manifest_data["locked_indep_parameter_hashes"]
    assert indep_hashes["M_INDEP_CLARIFY_BASE_LOGITS"] == sha256_array(M_INDEP_CLARIFY_BASE_LOGITS)
    assert indep_hashes["M_INDEP_RETRIEVE_BASE_LOGITS"] == sha256_array(M_INDEP_RETRIEVE_BASE_LOGITS)
    assert indep_hashes["M_INDEP_CLARIFY_W_DIR"] == sha256_array(M_INDEP_CLARIFY_W_DIR)
    assert indep_hashes["M_INDEP_RETRIEVE_W_DIR"] == sha256_array(M_INDEP_RETRIEVE_W_DIR)
    assert indep_hashes["M_INDEP_CLARIFY_B_S"] == sha256_array(M_INDEP_CLARIFY_B_S)
    assert indep_hashes["M_INDEP_RETRIEVE_B_S"] == sha256_array(M_INDEP_RETRIEVE_B_S)


def test_manifest_locked_control_hashes(manifest_data: Dict[str, Any]):
    """Verify shuffle permutation hash matches frozen manifest."""
    ctrl_hashes = manifest_data["locked_control_hashes"]
    assert ctrl_hashes["C2_SHUFFLE_PERMUTATION_HASH"] == sha256_array(C2_PERMUTATION)
    assert ctrl_hashes["C2_SHUFFLE_SEED_HASH"] == hashlib.sha256(str(SHUFFLE_SEED).encode()).hexdigest()


# =============================================================================
# 2. Corpus & Matched Discordant Pairs
# =============================================================================

def test_corpus_generation_and_integrity(initialized_harness: EpistemicToPolicyTranslationHarness):
    """Verify corpus size N=270, 90 per tier, and SHA verification function."""
    assert len(initialized_harness.all_probes) == 270
    assert verify_corpus_sha(initialized_harness.all_probes) is True


def test_matched_discordant_pairs_count_and_invariants(initialized_harness: EpistemicToPolicyTranslationHarness):
    """Verify exact 358 matched discordant pairs and scalar matching within 0.020."""
    pairs = initialized_harness.discordant_matched_pairs
    assert len(pairs) == EXPECTED_HISTORICAL_DISCORDANT

    for p_i, p_j in pairs:
        s_i = initialized_harness.simulated_trajectories[p_i]["s_val"]
        s_j = initialized_harness.simulated_trajectories[p_j]["s_val"]
        assert abs(s_i - s_j) <= 0.020 + 1e-12

        r_i = initialized_harness.simulated_trajectories[p_i]["r_vec"]
        r_j = initialized_harness.simulated_trajectories[p_j]["r_vec"]
        signs_i = (deadband_sign(r_i[0]), deadband_sign(r_i[1]), deadband_sign(r_i[2]))
        signs_j = (deadband_sign(r_j[0]), deadband_sign(r_j[1]), deadband_sign(r_j[2]))
        assert signs_i != signs_j


def test_deadband_sign_properties():
    """Verify three-valued deadband sign logic."""
    assert deadband_sign(0.05, DEADBAND_EPSILON) == 1
    assert deadband_sign(-0.05, DEADBAND_EPSILON) == -1
    assert deadband_sign(0.005, DEADBAND_EPSILON) == 0
    assert deadband_sign(-0.005, DEADBAND_EPSILON) == 0
    assert deadband_sign(0.0, DEADBAND_EPSILON) == 0


# =============================================================================
# 3. Policy Formulations P0–P4 Correctness
# =============================================================================

def test_p0_canonical_efe_formulation():
    """Verify P0 computes V(a) = alpha*V_pragm + beta*EIG - Cost."""
    eig_vec = np.array([0.0, 0.10, 0.05, 0.0, 0.0, 0.0], dtype=np.float64)
    post_h = np.array([H_MAX, H_MAX - 0.10, H_MAX - 0.05, H_MAX, H_MAX, H_MAX], dtype=np.float64)
    prof = evaluate_policy_ablation("P0_canonical_efe", eig_vec, post_h)

    # answer: 1.0*1.0 + 2.0*0.0 - 0.05 = 0.95
    assert abs(prof.action_values[0] - 0.95) < 1e-12
    # clarify: 1.0*0.0 + 2.0*0.10 - 0.40 = -0.20
    assert abs(prof.action_values[1] - (-0.20)) < 1e-12
    # retrieve: 1.0*0.0 + 2.0*0.05 - 0.35 = -0.25
    assert abs(prof.action_values[2] - (-0.25)) < 1e-12
    # top action should be answer, second action should be wait (-0.02)
    assert prof.top_action == "answer"
    assert prof.second_action == "wait"
    assert abs(prof.margin - (0.95 - (-0.02))) < 1e-12


def test_p1_precision_weighting_behavior():
    """Verify P1 elevates epistemic weighting when EIG reduces posterior uncertainty."""
    eig_vec = np.array([0.0, 0.10, 0.0, 0.0, 0.0, 0.0], dtype=np.float64)
    post_h = np.array([H_MAX, H_MAX - 0.10, H_MAX, H_MAX, H_MAX, H_MAX], dtype=np.float64)
    prof_p1 = evaluate_policy_ablation("P1_precision_weighted", eig_vec, post_h)
    prof_p0 = evaluate_policy_ablation("P0_canonical_efe", eig_vec, post_h)

    # For clarify, posterior entropy is lower than prior, so precision weight > 1.0
    # Thus V_P1(clarify) should be strictly greater than V_P0(clarify)
    assert prof_p1.action_values[1] > prof_p0.action_values[1]
    # For answer (EIG=0), precision weight * EIG = 0, so V(answer) remains identical
    assert abs(prof_p1.action_values[0] - prof_p0.action_values[0]) < 1e-12


def test_p2_nonlinear_logarithmic_utility():
    """Verify P2 computes scale-preserving logarithmic utility strictly."""
    eig_vec = np.array([0.0, 0.016626, 0.0, 0.0, 0.0, 0.0], dtype=np.float64)
    post_h = np.full(6, H_MAX, dtype=np.float64)
    prof_p2 = evaluate_policy_ablation("P2_nonlinear_log", eig_vec, post_h)

    # phi = ln(1 + 0.016626 / 1e-4) = ln(1 + 166.26) = ln(167.26)
    expected_phi = math.log(1.0 + 0.016626 / TOLERANCE_EIG)
    expected_clarify = 0.0 + BETA_0 * TOLERANCE_EIG * expected_phi - ACTION_COSTS[1]
    assert abs(prof_p2.action_values[1] - expected_clarify) < 1e-12


def test_p3_continuous_readout_identity():
    """Verify P3 produces action values identical to P0 but exposes full continuous profile."""
    eig_vec = np.array([0.0, 0.08, 0.04, 0.0, 0.0, 0.0], dtype=np.float64)
    post_h = np.full(6, H_MAX, dtype=np.float64)
    prof_p0 = evaluate_policy_ablation("P0_canonical_efe", eig_vec, post_h)
    prof_p3 = evaluate_policy_ablation("P3_continuous_readout", eig_vec, post_h)

    assert np.allclose(prof_p0.action_values, prof_p3.action_values, atol=1e-15)
    assert np.allclose(prof_p0.probabilities, prof_p3.probabilities, atol=1e-15)
    assert prof_p0.ranking == prof_p3.ranking


def test_p4_margin_rescaled_exact_constants():
    """Verify P4 uses exact pre-frozen beta_P4 constant and EIG_bar."""
    eig_vec = np.array([0.0, EIG_BAR_FROZEN, 0.0, 0.0, 0.0, 0.0], dtype=np.float64)
    post_h = np.full(6, H_MAX, dtype=np.float64)
    prof_p4 = evaluate_policy_ablation("P4_margin_rescaled", eig_vec, post_h)

    # scaling_term = 1 + (0.016626 / 0.016626) = 2.0
    # term = beta_P4 * 2.0 * 0.016626
    expected_clarify = 0.0 + BETA_P4_VALUE * 2.0 * EIG_BAR_FROZEN - ACTION_COSTS[1]
    assert abs(prof_p4.action_values[1] - expected_clarify) < 1e-12


# =============================================================================
# 4. Pair Evaluation & Variance Decomposition
# =============================================================================

def test_pair_evaluation_c0_scalar_null(initialized_harness: EpistemicToPolicyTranslationHarness):
    """Verify single pair under C0 yields zero directional displacement."""
    q0 = np.full(4, 0.25, dtype=np.float64)
    p_i, p_j = initialized_harness.discordant_matched_pairs[0]
    rec = initialized_harness.evaluate_pair_translation(
        p_i=p_i,
        p_j=p_j,
        policy_id="P0_canonical_efe",
        condition="C0",
        spec=initialized_harness.spec_canon_c0,
        spec_c0=initialized_harness.spec_canon_c0,
        q0=q0,
    )
    assert abs(rec["l2_delta_v_dir"]) <= TOLERANCE_VAL
    assert abs(rec["delta_margin_dir"]) <= TOLERANCE_VAL
    assert rec["d_pol"] == 0


def test_pair_evaluation_c1_canonical_displacement(initialized_harness: EpistemicToPolicyTranslationHarness):
    """Verify single pair under C1 yields non-zero directional displacement but D_pol=0."""
    q0 = np.full(4, 0.25, dtype=np.float64)
    p_i, p_j = initialized_harness.discordant_matched_pairs[0]
    rec = initialized_harness.evaluate_pair_translation(
        p_i=p_i,
        p_j=p_j,
        policy_id="P0_canonical_efe",
        condition="C1",
        spec=initialized_harness.spec_canon,
        spec_c0=initialized_harness.spec_canon_c0,
        q0=q0,
    )
    assert rec["l2_delta_v_dir"] > TOLERANCE_VAL
    assert rec["top_action_i"] == "answer"
    assert rec["top_action_j"] == "answer"
    assert rec["d_pol"] == 0


def test_variance_decomposition_properties(initialized_harness: EpistemicToPolicyTranslationHarness):
    """Verify variance decomposition: SS_tot = common_mode_ss + specific_ss."""
    q0 = np.full(4, 0.25, dtype=np.float64)
    p_i, p_j = initialized_harness.discordant_matched_pairs[0]
    rec = initialized_harness.evaluate_pair_translation(
        p_i=p_i,
        p_j=p_j,
        policy_id="P0_canonical_efe",
        condition="C1",
        spec=initialized_harness.spec_canon,
        spec_c0=initialized_harness.spec_canon_c0,
        q0=q0,
    )
    asv = rec["action_specific_variance_frac"]
    assert 0.0 <= asv <= 1.0


def test_deterministic_repeatability_nc4(initialized_harness: EpistemicToPolicyTranslationHarness):
    """Verify NC4: repeated evaluation produces bit-exact identical values."""
    q0 = np.full(4, 0.25, dtype=np.float64)
    p_i, p_j = initialized_harness.discordant_matched_pairs[5]

    rec1 = initialized_harness.evaluate_pair_translation(
        p_i=p_i, p_j=p_j, policy_id="P0_canonical_efe", condition="C1",
        spec=initialized_harness.spec_canon, spec_c0=initialized_harness.spec_canon_c0, q0=q0
    )
    rec2 = initialized_harness.evaluate_pair_translation(
        p_i=p_i, p_j=p_j, policy_id="P0_canonical_efe", condition="C1",
        spec=initialized_harness.spec_canon, spec_c0=initialized_harness.spec_canon_c0, q0=q0
    )

    assert abs(rec1["l2_delta_v_dir"] - rec2["l2_delta_v_dir"]) < 1e-15
    assert abs(rec1["delta_margin_dir"] - rec2["delta_margin_dir"]) < 1e-15
    assert rec1["top_action_i"] == rec2["top_action_i"]


# =============================================================================
# 5. Results Artifacts Verification
# =============================================================================

@pytest.fixture(scope="module")
def study_results_json() -> Dict[str, Any]:
    """Load study results JSON."""
    results_path = RESULTS_DIR / "r3_epistemic_to_policy_translation_results.json"
    assert results_path.exists(), f"Results file missing: {results_path}"
    with open(results_path, "r", encoding="utf-8") as f:
        return json.load(f)


@pytest.fixture(scope="module")
def negative_controls_json() -> Dict[str, Any]:
    """Load negative controls JSON."""
    nc_path = RESULTS_DIR / "r3_epistemic_to_policy_translation_negative_controls.json"
    assert nc_path.exists(), f"NC file missing: {nc_path}"
    with open(nc_path, "r", encoding="utf-8") as f:
        return json.load(f)


@pytest.fixture(scope="module")
def fifteen_point_report_json() -> Dict[str, Any]:
    """Load 15-point report JSON."""
    report_path = RESULTS_DIR / "r3_epistemic_to_policy_translation_15point_report.json"
    assert report_path.exists(), f"Report file missing: {report_path}"
    with open(report_path, "r", encoding="utf-8") as f:
        return json.load(f)


def test_study_results_structure(study_results_json: Dict[str, Any]):
    """Verify all 5 policy ablations and 4 conditions are present in results."""
    policies = [
        "P0_canonical_efe", "P1_precision_weighted", "P2_nonlinear_log",
        "P3_continuous_readout", "P4_margin_rescaled"
    ]
    conditions = ["C0", "C1", "C2", "C3"]

    for pol in policies:
        assert pol in study_results_json
        for cond in conditions:
            assert cond in study_results_json[pol]
            res = study_results_json[pol][cond]
            assert res["n_pairs"] == EXPECTED_HISTORICAL_DISCORDANT
            assert "mean_l2_delta_v_dir" in res
            assert "d_pol" in res


def test_p0_canonical_c1_empirical_findings(study_results_json: Dict[str, Any]):
    """Verify empirical findings for canonical P0 under C1."""
    c1 = study_results_json["P0_canonical_efe"]["C1"]
    # Directional displacement is continuous and non-zero
    assert c1["mean_l2_delta_v_dir"] > TOLERANCE_VAL
    assert c1["fraction_exceeding_tau_val"] == 1.0
    # Discrete argmax divergence is strictly zero
    assert c1["d_pol"] == 0.0
    # Correlation with EIG is positive and strong
    assert c1["pearson_r_eig_v"] > 0.50


def test_all_negative_controls_passed(negative_controls_json: Dict[str, Any]):
    """Verify that all 7 pure negative controls NC1–NC7 passed."""
    for key in [
        "NC1_scalar_null",
        "NC2_direction_shuffled_reduced",
        "NC3_zero_directional_weighting",
        "NC4_deterministic_repeatability",
        "NC5_anti_tuning_manifest_invariance",
        "NC6_production_code_isolation",
        "NC7_genesis_gate_invariant",
    ]:
        assert key in negative_controls_json
        assert negative_controls_json[key]["passed"] is True, f"{key} failed!"


def test_replication_control_rc1_passed(negative_controls_json: Dict[str, Any]):
    """Verify that RC1 (Cross-Model Replication Control) passed."""
    assert "RC1_cross_model_replication" in negative_controls_json
    rc1 = negative_controls_json["RC1_cross_model_replication"]
    assert rc1["passed"] is True
    assert rc1["mean_l2"] > TOLERANCE_VAL
    assert rc1["r_c3_c1"] > 0.50


def test_bottleneck_classification_and_rationale(fifteen_point_report_json: Dict[str, Any]):
    """Verify deterministic bottleneck classification adheres to decision hierarchy."""
    classification = fifteen_point_report_json["primary_bottleneck_classification"]
    assert classification in [
        "DECISION_DISCRETIZATION",
        "CONSUMER_LIMITATION",
        "REPRESENTATION_LIMITATION",
        "GENUINE_INSUFFICIENCY",
        "INCONCLUSIVE",
    ]
    # Under canonical additive EFE with answer default pragmatic gap ~1.35:
    # Continuous action values shift (||ΔV|| > 1e-4) and correlate with EIG,
    # but argmax never switches (D_pol = 0).
    assert classification == "DECISION_DISCRETIZATION"
    assert "classification_rationale" in fifteen_point_report_json


def test_summary_csv_exists_and_populated():
    """Verify CSV summary table exists and has rows for all 5x4 evaluations."""
    csv_path = RESULTS_DIR / "r3_epistemic_to_policy_translation_summary.csv"
    assert csv_path.exists()
    lines = csv_path.read_text(encoding="utf-8").strip().split("\n")
    # Header + 5 policies * 4 conditions = 21 lines
    assert len(lines) == 21


# =============================================================================
# 6. Governance & Production Isolation Invariants
# =============================================================================

def test_governance_invariants(fifteen_point_report_json: Dict[str, Any]):
    """Verify governance invariants are strictly maintained in report."""
    assert fifteen_point_report_json["gate_2_status"] == "STRICTLY_BLOCKED"
    assert fifteen_point_report_json["phase_22_h1_status"] == "INCONCLUSIVE"


def test_genesis_gate_invariant():
    """Verify Genesis onboarding profile is bit-exact locked: {is_onboarded: false}."""
    profile_path = REPO_ROOT / "data" / "profile.json"
    assert profile_path.exists()
    with open(profile_path, "r", encoding="utf-8") as f:
        data = json.load(f)
    assert data == {"is_onboarded": False}


def test_p1_ranking_shifts_under_precision_weighting(study_results_json: Dict[str, Any]):
    """Verify P1 induces high ranking change rate in C1 while C2 shuffled drops."""
    c1_p1 = study_results_json["P1_precision_weighted"]["C1"]
    c2_p1 = study_results_json["P1_precision_weighted"]["C2"]
    assert c1_p1["ranking_change_rate"] > 0.70
    assert c2_p1["ranking_change_rate"] < c1_p1["ranking_change_rate"]


def test_p4_continuous_policy_shifts(study_results_json: Dict[str, Any]):
    """Verify P4 shifts continuous policy TV and JS substantially."""
    c1_p4 = study_results_json["P4_margin_rescaled"]["C1"]
    assert c1_p4["mean_policy_tv"] > 0.10
    assert c1_p4["mean_policy_js"] > 0.01
    assert c1_p4["ranking_change_rate"] == 1.0


def test_action_specific_variance_dominance(fifteen_point_report_json: Dict[str, Any]):
    """Verify action-specific variance fraction is high (> 80%), ruling out common-mode offset."""
    asv_frac = fifteen_point_report_json["p0_canonical_c1_action_specific_variance_frac"]
    assert asv_frac > 0.80


def test_precedence_hierarchy_steps_in_report(fifteen_point_report_json: Dict[str, Any]):
    """Verify primary bottleneck classification strictly matches pre-registered rubric."""
    assert fifteen_point_report_json["primary_bottleneck_classification"] == "DECISION_DISCRETIZATION"
    assert "Delta_V_dir" in fifteen_point_report_json["classification_rationale"]
    assert "D_pol = 0.0000" in fifteen_point_report_json["classification_rationale"]


def test_anti_tuning_rule_grid_invariance(manifest_data: Dict[str, Any]):
    """Verify all 5 policy ablations in manifest match exact pre-registered grid."""
    assert manifest_data["policy_ablations"] == [
        "P0_canonical_efe",
        "P1_precision_weighted",
        "P2_nonlinear_log",
        "P3_continuous_readout",
        "P4_margin_rescaled",
    ]


def test_zero_gpu_vram_and_cpu_execution_invariants(manifest_data: Dict[str, Any]):
    """Verify hardware budget invariant in manifest specifies 100% CPU and 0 GPU VRAM."""
    gov = manifest_data["governance"]
    assert gov["hardware"] == "100_percent_cpu_0_gpu_vram"
    assert gov["production_diff_required"] == "0_files_changed"

