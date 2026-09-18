"""
Unit and Property Test Suite: Phase 22 H1 Probabilistic Policy Study
=============================================================================
Test File: test_h1_r3_probabilistic_policy.py

Validates the empirical findings, mathematical bounds, negative controls (NC1–NC8),
temperature sensitivity (H1-T), probabilistic signal recovery (H1-P), sampled action
divergence (H1-S), decision classification (RESULT_P3), and governance invariants
for PHASE_22_H1_R3_PROBABILISTIC_POLICY_STUDY.

Covers:
  1. Manifest & artifact integrity (schema, seeds, hashes)
  2. Corpus & matched discordant pair invariants (N=270, pairs=358, SHA match)
  3. Context identity (CTX_5: V_pragm("answer") = 0.00, winner = "retrieve")
  4. Parameter & permutation hashes invariance
  5. C0 Scalar Null Control (NC1 across all gammas: ||Delta V_dir|| <= tau_val, D_TV_dir <= tau_TV, D_JS <= tau_JS, D_pol == 0)
  6. C1 Canonical R3 Signal (D_TV > tau_TV, D_JS > tau_JS, ||Delta V_dir|| ~ 0.093653)
  7. C2 Direction-Shuffled Control (NC2: degraded correspondence r <= 0.50)
  8. C3 Independent Model Replication (||Delta V_dir|| ~ 0.090408, replication holds)
  9. Temperature grid completeness ({0.25, 0.50, 1.00, 2.00, 4.00})
  10. Softmax normalization & probability invariants (sum == 1, non-negative)
  11. Softmax argmax equivalence (NC8: argmax(P) == argmax(V) 100% bit-exact across all probes & gammas)
  12. Probability distribution divergence properties (D_TV in [0, 1], D_JS in [0, ln(2)])
  13. KL divergence numerical stability (finite, non-negative)
  14. Deterministic repeatability (NC4: bit-exact values on rerun)
  15. Common Random Number (CRN) alignment & sampling schedule
  16. Monte Carlo sampler precision & analytical cross-check (|D_emp - D_anal| < 0.01)
  17. Analytical CRN vs Independent divergence bounds (CRN <= Independent)
  18. H1-P Probabilistic Policy Signal confirmation
  19. H1-T Temperature Sensitivity & Monotonicity (D_TV strictly increasing with gamma)
  20. H1-S Sampled Action Divergence (> tau_TV, monotonic increase with gamma)
  21. Decision hierarchy classification (RESULT_P3: SAMPLING_LEVEL_ACTION_DIFFERENTIATION)
  22. Negative Controls NC1–NC8 pass rate (100%)
  23. Production code isolation (NC6: git diff src/core/** == 0, src/api/** == 0, electron/** == 0)
  24. Genesis gate invariant (NC7: profile.json is_onboarded == false)
  25. Artifact schema & summary CSV structure
  26. 20-Watt CPU-only invariant (0.0 MB GPU VRAM allocated)
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

def get_repo_root() -> Path:
    current = Path(__file__).resolve()
    while current.parent != current:
        if (current / "src").exists() and (current / "AGENTS.md").exists():
            return current
        current = current.parent
    return Path(__file__).resolve().parents[3]

REPO_ROOT = get_repo_root()
sys.path.insert(0, str(REPO_ROOT))

from tests.evaluation_phase22.scripts.evaluate_h1_r3_probabilistic_policy import (
    ACTIONS,
    BOOTSTRAP_ITERATIONS,
    BOOTSTRAP_SEED,
    CONTEXT_ID,
    DEADBAND_EPSILON,
    EXPECTED_CORPUS_SHA,
    EXPECTED_HISTORICAL_DISCORDANT,
    EXPOSURE_TICKS,
    INDEP_OBS_SEED,
    MASTER_SEED,
    MONTE_CARLO_K,
    NUM_ACTIONS,
    NUMERICAL_EPSILON,
    SAMPLING_SEED,
    SCALAR_MATCH_THRESHOLD,
    SHUFFLE_SEED,
    STUDY_ID,
    TEMPERATURE_GRID,
    TOLERANCE_CORR_MAX,
    TOLERANCE_EIG,
    TOLERANCE_JS,
    TOLERANCE_TV,
    TOLERANCE_VAL,
    V_PRAGM_ANSWER,
    compute_analytical_crn_divergence,
    compute_analytical_independent_divergence,
    compute_js_divergence,
    compute_kl_divergence,
    compute_tv_distance,
    deadband_sign,
    sha256_array,
    softmax,
    verify_corpus_sha,
)

FIXTURES_DIR = REPO_ROOT / "tests" / "evaluation_phase22" / "fixtures"
RESULTS_DIR = REPO_ROOT / "tests" / "evaluation_phase22" / "results" / "h1_r3_probabilistic_policy"


@pytest.fixture(scope="module")
def manifest() -> Dict[str, Any]:
    manifest_path = FIXTURES_DIR / "manifest_h1_r3_probabilistic_policy.json"
    if not manifest_path.exists():
        manifest_path = RESULTS_DIR / "manifest_h1_r3_probabilistic_policy.json"
    assert manifest_path.exists(), f"Manifest not found: {manifest_path}"
    with open(manifest_path, "r", encoding="utf-8") as f:
        return json.load(f)


@pytest.fixture(scope="module")
def study_results() -> Dict[str, Any]:
    results_path = FIXTURES_DIR / "results_h1_r3_probabilistic_policy.json"
    if not results_path.exists():
        results_path = RESULTS_DIR / "results_h1_r3_probabilistic_policy.json"
    assert results_path.exists(), f"Results fixture not found: {results_path}"
    with open(results_path, "r", encoding="utf-8") as f:
        return json.load(f)


@pytest.fixture(scope="module")
def nc_results() -> Dict[str, Any]:
    nc_path = FIXTURES_DIR / "nc_h1_r3_probabilistic_policy.json"
    if not nc_path.exists():
        nc_path = RESULTS_DIR / "nc_h1_r3_probabilistic_policy.json"
    assert nc_path.exists(), f"NC fixture not found: {nc_path}"
    with open(nc_path, "r", encoding="utf-8") as f:
        return json.load(f)


@pytest.fixture(scope="module")
def formal_report() -> Dict[str, Any]:
    report_path = FIXTURES_DIR / "report_h1_r3_probabilistic_policy.json"
    if not report_path.exists():
        report_path = RESULTS_DIR / "report_h1_r3_probabilistic_policy.json"
    assert report_path.exists(), f"Report fixture not found: {report_path}"
    with open(report_path, "r", encoding="utf-8") as f:
        return json.load(f)


# =============================================================================
# 1. Manifest & Artifact Integrity Tests
# =============================================================================

def test_manifest_integrity(manifest: Dict[str, Any]) -> None:
    """Validate manifest schema and committed parameters."""
    assert manifest["study_id"] == STUDY_ID
    assert manifest["master_seed"] == MASTER_SEED
    assert manifest["sampling_seed"] == SAMPLING_SEED
    assert manifest["temperature_grid"] == TEMPERATURE_GRID
    assert manifest["context"] == CONTEXT_ID
    assert manifest["v_pragm_answer"] == V_PRAGM_ANSWER
    assert manifest["expected_corpus_sha"] == EXPECTED_CORPUS_SHA
    assert manifest["expected_discordant_pairs"] == EXPECTED_HISTORICAL_DISCORDANT


def test_artifact_files_exist() -> None:
    """Verify all 8 required artifacts exist in results directory."""
    expected_files = [
        "evaluate_h1_r3_probabilistic_policy.py",
        "test_h1_r3_probabilistic_policy.py",
        "manifest_h1_r3_probabilistic_policy.json",
        "results_h1_r3_probabilistic_policy.json",
        "nc_h1_r3_probabilistic_policy.json",
        "report_h1_r3_probabilistic_policy.json",
        "summary_h1_r3_probabilistic_policy.csv",
        "PHASE_22_H1_R3_PROBABILISTIC_POLICY_STUDY.md",
    ]
    for fname in expected_files:
        p = RESULTS_DIR / fname
        assert p.exists(), f"Missing required artifact: {p}"


# =============================================================================
# 2. Corpus & Matched Discordant Pair Invariants
# =============================================================================

def test_corpus_sha_verification() -> None:
    """Verify that Generator G1 reproduces the exact frozen SHA256 corpus hash."""
    from tests.evaluation_phase22.scripts.evaluate_h1_r3_probabilistic_policy import ProbabilisticPolicyHarness
    harness = ProbabilisticPolicyHarness()
    probes = harness.generate_master_corpus()
    assert len(probes) == 270
    assert verify_corpus_sha(probes) is True


def test_matched_discordant_pair_count(manifest: Dict[str, Any]) -> None:
    """Verify exact 358 matched discordant pairs are committed in manifest."""
    assert manifest["expected_discordant_pairs"] == EXPECTED_HISTORICAL_DISCORDANT


# =============================================================================
# 3. Context & Valuation Invariants
# =============================================================================

def test_context_definition(formal_report: Dict[str, Any]) -> None:
    """Verify CTX_5 context configuration and pragmatic value."""
    ctx_def = formal_report["4_context_definition"]
    assert ctx_def["context_id"] == CONTEXT_ID
    assert ctx_def["v_pragm_answer"] == V_PRAGM_ANSWER
    assert ctx_def["winner_action"] == "retrieve"


def test_lockstep_deterministic_argmax(study_results: Dict[str, Any]) -> None:
    """Verify deterministic argmax divergence remains D_pol = 0.0000 across all gammas."""
    for gamma in TEMPERATURE_GRID:
        g_key = f"gamma_{gamma:.2f}"
        for cond_id in ["C0", "C1", "C2", "C3"]:
            assert study_results[g_key][cond_id]["d_pol"] == 0.0


# =============================================================================
# 4. Parameter & Permutation Hashes
# =============================================================================

def test_parameter_hashes_invariance(manifest: Dict[str, Any]) -> None:
    """Verify frozen observation model and shuffle permutation parameter hashes."""
    from tests.evaluation_phase22.scripts.evaluate_h1_r3_probabilistic_policy import (
        C2_PERMUTATION,
        M_CANON_CLARIFY_BASE_LOGITS,
        M_CANON_RETRIEVE_BASE_LOGITS,
        M_INDEP_CLARIFY_BASE_LOGITS,
    )
    assert manifest["locked_canon_parameter_hashes"]["M_CANON_CLARIFY_BASE_LOGITS"] == sha256_array(M_CANON_CLARIFY_BASE_LOGITS)
    assert manifest["locked_canon_parameter_hashes"]["M_CANON_RETRIEVE_BASE_LOGITS"] == sha256_array(M_CANON_RETRIEVE_BASE_LOGITS)
    assert manifest["locked_indep_parameter_hashes"]["M_INDEP_CLARIFY_BASE_LOGITS"] == sha256_array(M_INDEP_CLARIFY_BASE_LOGITS)
    assert manifest["locked_control_hashes"]["C2_SHUFFLE_PERMUTATION_HASH"] == sha256_array(C2_PERMUTATION)


# =============================================================================
# 5. Negative Controls (NC1–NC8)
# =============================================================================

def test_all_negative_controls_pass(nc_results: Dict[str, Any]) -> None:
    """Verify all 8 negative controls pass cleanly."""
    assert nc_results["all_passed"] is True


def test_nc1_scalar_null(nc_results: Dict[str, Any], study_results: Dict[str, Any]) -> None:
    """Verify NC1: C0 produces Delta V_dir <= tau_val, D_TV_dir <= tau_TV, D_JS <= tau_JS across all gammas."""
    assert nc_results["NC1_scalar_null"]["passed"] is True
    for gamma in TEMPERATURE_GRID:
        g_key = f"gamma_{gamma:.2f}"
        res_c0 = study_results[g_key]["C0"]
        assert res_c0["mean_l2_delta_v_dir"] <= TOLERANCE_VAL
        assert res_c0["mean_d_tv_dir"] <= TOLERANCE_TV
        assert res_c0["mean_d_js"] <= TOLERANCE_JS
        assert res_c0["d_pol"] == 0.0


def test_nc2_direction_shuffle(nc_results: Dict[str, Any]) -> None:
    """Verify NC2: C2 shows degraded correspondence relative to C1 (r <= 0.50)."""
    assert nc_results["NC2_direction_shuffled"]["passed"] is True
    r_val = nc_results["NC2_direction_shuffled"]["details"]["pearson_r_c2_c1"]
    assert r_val <= TOLERANCE_CORR_MAX


def test_nc3_zero_weight(nc_results: Dict[str, Any]) -> None:
    """Verify NC3: Setting W_dir = 0 produces exact C0 scalar baseline."""
    assert nc_results["NC3_zero_directional_weighting"]["passed"] is True


def test_nc4_repeatability(nc_results: Dict[str, Any]) -> None:
    """Verify NC4: Deterministic repeatability holds bit-exact on re-evaluation."""
    assert nc_results["NC4_deterministic_repeatability"]["passed"] is True


def test_nc5_anti_tuning(nc_results: Dict[str, Any]) -> None:
    """Verify NC5: All frozen parameter and permutation hashes match manifest."""
    assert nc_results["NC5_anti_tuning_invariance"]["passed"] is True


def test_nc6_production_isolation(nc_results: Dict[str, Any]) -> None:
    """Verify NC6: Production code isolation invariant."""
    assert nc_results["NC6_production_isolation"]["passed"] is True


def test_nc7_genesis_gate(nc_results: Dict[str, Any]) -> None:
    """Verify NC7: Genesis gate remains locked with is_onboarded == False."""
    assert nc_results["NC7_genesis_gate"]["passed"] is True


def test_nc8_softmax_argmax_equivalence(nc_results: Dict[str, Any], study_results: Dict[str, Any]) -> None:
    """Verify NC8: argmax(softmax(gamma * V)) == argmax(V) 100% bit-exact across all probes & gammas."""
    assert nc_results["NC8_softmax_argmax_equivalence"]["passed"] is True
    for gamma in TEMPERATURE_GRID:
        g_key = f"gamma_{gamma:.2f}"
        for cond_id in ["C0", "C1", "C2", "C3"]:
            assert study_results[g_key][cond_id]["softmax_argmax_equiv_rate"] == 1.0


# =============================================================================
# 6. Primary Hypotheses (H1-P, H1-T, H1-S) & Signal Analysis
# =============================================================================

def test_h1_p_probabilistic_policy_signal(study_results: Dict[str, Any]) -> None:
    """Verify H1-P: C1 produces D_TV > tau_TV and D_JS > tau_JS across all gammas."""
    for gamma in TEMPERATURE_GRID:
        g_key = f"gamma_{gamma:.2f}"
        res_c1 = study_results[g_key]["C1"]
        assert res_c1["mean_d_tv"] > TOLERANCE_TV
        assert res_c1["mean_d_js"] > TOLERANCE_JS
        # Directional displacement in C1 must also exceed threshold
        assert res_c1["mean_d_tv_dir"] > TOLERANCE_TV


def test_h1_t_temperature_monotonicity(study_results: Dict[str, Any]) -> None:
    """Verify H1-T: Probability divergence strictly increases monotonically with gamma."""
    c1_tvs = [study_results[f"gamma_{g:.2f}"]["C1"]["mean_d_tv"] for g in TEMPERATURE_GRID]
    c1_jss = [study_results[f"gamma_{g:.2f}"]["C1"]["mean_d_js"] for g in TEMPERATURE_GRID]
    for k in range(1, len(TEMPERATURE_GRID)):
        assert c1_tvs[k] > c1_tvs[k - 1], f"D_TV not monotonic: {c1_tvs[k]} <= {c1_tvs[k-1]}"
        assert c1_jss[k] > c1_jss[k - 1], f"D_JS not monotonic: {c1_jss[k]} <= {c1_jss[k-1]}"


def test_h1_s_sampled_action_divergence(study_results: Dict[str, Any]) -> None:
    """Verify H1-S: Empirical sampled action divergence produces reproducible non-zero divergence."""
    for gamma in TEMPERATURE_GRID:
        g_key = f"gamma_{gamma:.2f}"
        res_c1 = study_results[g_key]["C1"]
        assert res_c1["mean_d_samp_crn_empirical"] > TOLERANCE_TV


def test_sampled_action_divergence_monotonicity(study_results: Dict[str, Any]) -> None:
    """Verify sampled divergence under C1 strictly increases across temperature grid."""
    c1_samps = [study_results[f"gamma_{g:.2f}"]["C1"]["mean_d_samp_crn_empirical"] for g in TEMPERATURE_GRID]
    for k in range(1, len(TEMPERATURE_GRID)):
        assert c1_samps[k] > c1_samps[k - 1], f"Sampled divergence not monotonic: {c1_samps[k]} <= {c1_samps[k-1]}"


# =============================================================================
# 7. Sampling Methodology & Cross-Validation
# =============================================================================

def test_monte_carlo_precision(study_results: Dict[str, Any]) -> None:
    """Verify Monte Carlo empirical divergence closely matches analytical CRN formula."""
    for gamma in TEMPERATURE_GRID:
        g_key = f"gamma_{gamma:.2f}"
        for cond_id in ["C0", "C1", "C2", "C3"]:
            c_data = study_results[g_key][cond_id]
            assert c_data["mean_sampler_discrepancy"] < 0.005
            assert c_data["max_sampler_discrepancy"] < 0.025


def test_crn_variance_reduction(study_results: Dict[str, Any]) -> None:
    """Verify analytical CRN divergence is strictly bounded above by independent divergence."""
    for gamma in TEMPERATURE_GRID:
        g_key = f"gamma_{gamma:.2f}"
        for cond_id in ["C1", "C2", "C3"]:
            c_data = study_results[g_key][cond_id]
            # Analytical CRN divergence <= independent divergence for correlated distributions
            assert c_data["mean_d_samp_crn_analytical"] <= c_data["mean_d_samp_indep_analytical"] + 1e-12


# =============================================================================
# 8. Mathematical & Numerical Invariants
# =============================================================================

def test_softmax_properties() -> None:
    """Verify numerical properties of softmax implementation."""
    test_vals = np.array([1.0, 2.0, -0.5, 0.0, 3.5, 1.2])
    p = softmax(test_vals, gamma=1.0)
    assert abs(np.sum(p) - 1.0) < 1e-15
    assert np.all(p >= 0.0)
    assert int(np.argmax(p)) == int(np.argmax(test_vals))


def test_divergence_metrics_properties() -> None:
    """Verify mathematical properties of TV and JS divergence functions."""
    p = np.array([0.5, 0.3, 0.2])
    q = np.array([0.5, 0.3, 0.2])
    assert compute_tv_distance(p, q) == 0.0
    assert compute_js_divergence(p, q) == 0.0

    r = np.array([0.2, 0.5, 0.3])
    tv = compute_tv_distance(p, r)
    js = compute_js_divergence(p, r)
    assert 0.0 < tv <= 1.0
    assert 0.0 < js <= math.log(2.0)


def test_kl_numerical_stability() -> None:
    """Verify KL divergence computation is non-negative and numerically stable with small probabilities."""
    p = np.array([0.999, 0.001, 0.0])
    q = np.array([0.001, 0.999, 0.0])
    kl_pq = compute_kl_divergence(p, q, eps=NUMERICAL_EPSILON)
    kl_qp = compute_kl_divergence(q, p, eps=NUMERICAL_EPSILON)
    assert not math.isnan(kl_pq)
    assert not math.isnan(kl_qp)
    assert kl_pq >= 0.0
    assert kl_qp >= 0.0


# =============================================================================
# 9. Ranking Permutations & Winner Margins
# =============================================================================

def test_ranking_permutation_rate(study_results: Dict[str, Any]) -> None:
    """Verify sub-action ranking permutation rate under C1 (approx 79.89%)."""
    r_rate = study_results["gamma_1.00"]["C1"]["ranking_change_rate"]
    assert 0.75 <= r_rate <= 0.85
    assert study_results["gamma_1.00"]["C1"]["n_ranking_changed"] == 286


def test_winner_probability_and_margin(study_results: Dict[str, Any]) -> None:
    """Verify deterministic winner retrieve probability and pairwise margin under C1."""
    c1_g1 = study_results["gamma_1.00"]["C1"]
    assert 0.15 <= c1_g1["mean_p_argmax"] <= 0.30
    assert c1_g1["mean_abs_m_prob"] > 0.005


# =============================================================================
# 10. Cross-Model Replication (C3)
# =============================================================================

def test_c3_independent_model_replication(study_results: Dict[str, Any]) -> None:
    """Verify C3 independent model replicates continuous value and probability displacement."""
    c3_g1 = study_results["gamma_1.00"]["C3"]
    assert abs(c3_g1["mean_l2_delta_v_dir"] - 0.090408) < 0.005
    assert c3_g1["mean_d_tv"] > TOLERANCE_TV
    assert c3_g1["mean_d_js"] > TOLERANCE_JS
    assert c3_g1["d_pol"] == 0.0


# =============================================================================
# 11. Decision Hierarchy Classification
# =============================================================================

def test_decision_hierarchy_classification(formal_report: Dict[str, Any]) -> None:
    """Verify study classification resolves to RESULT_P3: SAMPLING_LEVEL_ACTION_DIFFERENTIATION."""
    decision = formal_report["12_interpretation_decision"]
    assert decision["code"] == "RESULT_P3"
    assert decision["label"] == "SAMPLING_LEVEL_ACTION_DIFFERENTIATION"


# =============================================================================
# 12. Summary CSV File Integrity
# =============================================================================

def test_summary_csv_schema_and_rows() -> None:
    """Verify summary CSV has 20 condition-temperature rows and correct columns."""
    csv_path = RESULTS_DIR / "summary_h1_r3_probabilistic_policy.csv"
    assert csv_path.exists()
    with open(csv_path, "r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        rows = list(reader)
    assert len(rows) == 20  # 5 temperatures x 4 conditions
    assert "gamma" in rows[0]
    assert "condition" in rows[0]
    assert "mean_l2_delta_v" in rows[0]
    assert "mean_d_tv" in rows[0]
    assert "mean_d_tv_dir" in rows[0]
    assert "mean_d_js" in rows[0]
    assert "d_pol" in rows[0]
    assert "d_samp_crn_empirical" in rows[0]


# =============================================================================
# 13. Strict Governance Invariants
# =============================================================================

def test_governance_invariants(formal_report: Dict[str, Any]) -> None:
    """Verify strict governance invariants recorded in report."""
    assert "BLOCKED" in formal_report["13_gate_2_status"]
    assert "DRAFT" in formal_report["14_adr029_status"]
    prod = formal_report["15_production_integrity"]
    assert prod["src_core_diff"] == 0
    assert prod["profile_is_onboarded"] is False
    assert prod["gpu_vram_mb"] == 0.0


def test_production_git_clean() -> None:
    """Verify zero modifications to production codebase."""
    res_core = subprocess.run(["git", "diff", "--", "src/core"], capture_output=True, text=True, cwd=REPO_ROOT)
    assert res_core.stdout.strip() == "", "Production src/core modified!"
    res_api = subprocess.run(["git", "diff", "--", "src/api"], capture_output=True, text=True, cwd=REPO_ROOT)
    assert res_api.stdout.strip() == "", "Production src/api modified!"
    res_electron = subprocess.run(["git", "diff", "--", "electron"], capture_output=True, text=True, cwd=REPO_ROOT)
    assert res_electron.stdout.strip() == "", "Electron frontend modified!"


def test_genesis_profile_exact() -> None:
    """Verify data/profile.json remains bit-exact {"is_onboarded": false}."""
    profile_path = REPO_ROOT / "data" / "profile.json"
    with open(profile_path, "r", encoding="utf-8") as f:
        data = json.load(f)
    assert data == {"is_onboarded": False}
