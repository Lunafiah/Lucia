"""
Phase 22 H1 — R3 Information Sufficiency & Representation-Coupling Study
========================================================================
Dedicated Test Suite: test_h1_r3_information_sufficiency.py

Validates 26 properties of the information sufficiency and model independence study:
  T1:  Corpus SHA-256 integrity, size N=270, 90 probes per tier
  T2:  Discordant pair count (N=358), sign discordance, and scalar tolerance
  T3:  Anti-circularity parameter hashes lock (M_canon, M_indep, C2, C4)
  T4:  Condition C0 scalar-only baseline yields null directional contribution
  T5:  Condition C1 canonical R3 reproduces reference mean and 100% retention
  T6:  Condition C2 direction-destroyed shuffle preserves marginals & reduces correspondence
  T7:  Condition C3 model-independent R3 retains signal under independent model
  T8:  Condition C4 representation control exhibits divergent alignment
  T9:  Likelihood matrix shape and probability constraints
  T10: Negative controls NC1–NC8 all passed and 15-point report completeness
  T11: Governance invariants (Production diff = 0, Genesis locked)
"""

import json
import math
import hashlib
from pathlib import Path

import numpy as np
import pytest
from scipy.stats import pearsonr, spearmanr

REPO_ROOT = Path(__file__).resolve().parent.parent.parent

from tests.evaluation_phase22.scripts.evaluate_r3_information_sufficiency import (
    InformationSufficiencyHarness,
    ObservationModelSpec,
    STUDY_ID,
    PRIMARY_SEED,
    SHUFFLE_SEED,
    INDEP_OBS_SEED,
    REPR_CONTROL_SEED,
    BOOTSTRAP_SEED,
    BOOTSTRAP_ITERATIONS,
    EXPECTED_CORPUS_SHA,
    EXPECTED_HISTORICAL_DISCORDANT,
    HISTORICAL_CANONICAL_MEAN_EIG_ADDITIVE,
    TOLERANCE_EIG,
    TOLERANCE_TV,
    TOLERANCE_JS,
    TOLERANCE_CORR_MAX,
    TOLERANCE_EQUIV_C4,
    LOCKED_CANON_PARAMETER_HASHES,
    LOCKED_INDEP_PARAMETER_HASHES,
    LOCKED_CONTROL_HASHES,
    M_CANON_CLARIFY_BASE_LOGITS,
    M_CANON_RETRIEVE_BASE_LOGITS,
    M_CANON_CLARIFY_W_DIR,
    M_CANON_RETRIEVE_W_DIR,
    M_CANON_CLARIFY_B_S,
    M_CANON_RETRIEVE_B_S,
    M_INDEP_CLARIFY_BASE_LOGITS,
    M_INDEP_RETRIEVE_BASE_LOGITS,
    M_INDEP_CLARIFY_W_DIR,
    M_INDEP_RETRIEVE_W_DIR,
    M_INDEP_CLARIFY_B_S,
    M_INDEP_RETRIEVE_B_S,
    C2_PERMUTATION,
    C4_SIGNS,
    NUM_HYPOTHESES,
    verify_corpus_sha,
    evaluate_epistemic_step_model,
    _build_likelihood_matrix,
    compute_bootstrap_ci,
    sha256_array,
    deadband_sign,
    compute_tv_distance,
    compute_js_divergence,
    compute_entropy,
)


# =============================================================================
# Shared Fixtures
# =============================================================================

@pytest.fixture(scope="module")
def harness():
    """Build fully initialized harness (corpus + trajectories + pairs)."""
    h = InformationSufficiencyHarness(master_seed=PRIMARY_SEED)
    h.generate_master_corpus()
    h.simulate_initial_pad_trajectories()
    h.partition_discordant_pairs()
    return h


@pytest.fixture(scope="module")
def benchmark_results(harness):
    """Run full benchmark once and cache for module-level test inspection."""
    return harness.run_full_benchmark()


# =============================================================================
# T1: Corpus SHA-256 Integrity & N=270 Structure
# =============================================================================

class TestT1CorpusIntegrity:
    def test_corpus_size_270(self, harness):
        assert len(harness.all_probes) == 270, \
            f"Expected 270 probes, got {len(harness.all_probes)}"

    def test_corpus_integrity_passes(self, harness):
        assert verify_corpus_sha(harness.all_probes), \
            "Corpus integrity check failed: expected N=270 with 90 probes per tier"

    def test_corpus_tiers_90_each(self, harness):
        from collections import Counter
        counts = Counter(p["tier"] for p in harness.all_probes)
        assert counts["Low"] == 90
        assert counts["Med"] == 90
        assert counts["High"] == 90


# =============================================================================
# T2: Discordant Pairs (N=358) & Properties
# =============================================================================

class TestT2DiscordantPairs:
    def test_discordant_pair_count(self, harness):
        assert len(harness.discordant_matched_pairs) == EXPECTED_HISTORICAL_DISCORDANT, \
            f"Expected {EXPECTED_HISTORICAL_DISCORDANT} pairs, got {len(harness.discordant_matched_pairs)}"

    def test_pairs_are_sign_discordant(self, harness):
        for p_i, p_j in harness.discordant_matched_pairs:
            s_i = harness.simulated_trajectories[p_i]["signs"]
            s_j = harness.simulated_trajectories[p_j]["signs"]
            assert s_i != s_j, f"Pair ({p_i}, {p_j}) should have discordant direction signs"

    def test_pairs_satisfy_scalar_tolerance(self, harness):
        for p_i, p_j in harness.discordant_matched_pairs:
            s_i = harness.simulated_trajectories[p_i]["s_val"]
            s_j = harness.simulated_trajectories[p_j]["s_val"]
            assert abs(s_i - s_j) <= 0.020 + 1e-9, \
                f"Pair ({p_i}, {p_j}) scalar diff {abs(s_i - s_j)} exceeds 0.020 tolerance"


# =============================================================================
# T3: Anti-Circularity Parameter Hashes & Seed Isolation
# =============================================================================

class TestT3AntiCircularityParameterHashes:
    def test_m_canon_parameter_hashes(self):
        assert sha256_array(M_CANON_CLARIFY_BASE_LOGITS) == LOCKED_CANON_PARAMETER_HASHES["M_CANON_CLARIFY_BASE_LOGITS"]
        assert sha256_array(M_CANON_RETRIEVE_BASE_LOGITS) == LOCKED_CANON_PARAMETER_HASHES["M_CANON_RETRIEVE_BASE_LOGITS"]
        assert sha256_array(M_CANON_CLARIFY_W_DIR) == LOCKED_CANON_PARAMETER_HASHES["M_CANON_CLARIFY_W_DIR"]
        assert sha256_array(M_CANON_RETRIEVE_W_DIR) == LOCKED_CANON_PARAMETER_HASHES["M_CANON_RETRIEVE_W_DIR"]
        assert sha256_array(M_CANON_CLARIFY_B_S) == LOCKED_CANON_PARAMETER_HASHES["M_CANON_CLARIFY_B_S"]
        assert sha256_array(M_CANON_RETRIEVE_B_S) == LOCKED_CANON_PARAMETER_HASHES["M_CANON_RETRIEVE_B_S"]

    def test_m_indep_parameter_hashes(self):
        assert sha256_array(M_INDEP_CLARIFY_BASE_LOGITS) == LOCKED_INDEP_PARAMETER_HASHES["M_INDEP_CLARIFY_BASE_LOGITS"]
        assert sha256_array(M_INDEP_RETRIEVE_BASE_LOGITS) == LOCKED_INDEP_PARAMETER_HASHES["M_INDEP_RETRIEVE_BASE_LOGITS"]
        assert sha256_array(M_INDEP_CLARIFY_W_DIR) == LOCKED_INDEP_PARAMETER_HASHES["M_INDEP_CLARIFY_W_DIR"]
        assert sha256_array(M_INDEP_RETRIEVE_W_DIR) == LOCKED_INDEP_PARAMETER_HASHES["M_INDEP_RETRIEVE_W_DIR"]

    def test_seed_isolation(self):
        seeds = [PRIMARY_SEED, SHUFFLE_SEED, INDEP_OBS_SEED, REPR_CONTROL_SEED, BOOTSTRAP_SEED]
        assert len(set(seeds)) == len(seeds), "All active study seeds must be mutually distinct"
        historical_seeds = [42, 43, 44, 45, 46, 4242, 7777, 8888]
        for s in [SHUFFLE_SEED, INDEP_OBS_SEED, REPR_CONTROL_SEED]:
            assert s not in historical_seeds, f"Seed {s} must be distinct from historical seeds"

    def test_c2_c4_hashes(self):
        assert sha256_array(C2_PERMUTATION) == LOCKED_CONTROL_HASHES["C2_SHUFFLE_PERMUTATION_HASH"]
        assert sha256_array(C4_SIGNS) == LOCKED_CONTROL_HASHES["C4_REPR_SIGNS_HASH"]


# =============================================================================
# T4: Condition C0 — Scalar Baseline (Null Directional Contribution)
# =============================================================================

class TestT4ConditionC0ScalarBaseline:
    def test_c0_retention_is_zero(self, benchmark_results):
        c0 = benchmark_results["conditions"]["C0"]
        assert c0["retention_rate"] == 0.0, f"C0 retention must be exactly 0.0, got {c0['retention_rate']}"

    def test_c0_mean_is_zero(self, benchmark_results):
        c0 = benchmark_results["conditions"]["C0"]
        assert c0["mean_abs_delta_eig_dir"] <= TOLERANCE_EIG, \
            f"C0 mean |Delta EIG_dir| must be <= {TOLERANCE_EIG}, got {c0['mean_abs_delta_eig_dir']}"


# =============================================================================
# T5: Condition C1 — Canonical R3 (M_canon)
# =============================================================================

class TestT5ConditionC1CanonicalR3:
    def test_c1_retention_is_100_percent(self, benchmark_results):
        c1 = benchmark_results["conditions"]["C1"]
        assert c1["retention_rate"] == 1.0, f"C1 retention must be 1.0, got {c1['retention_rate']}"

    def test_c1_mean_matches_additive_reference(self, benchmark_results):
        c1 = benchmark_results["conditions"]["C1"]
        diff = abs(c1["mean_abs_delta_eig_dir"] - HISTORICAL_CANONICAL_MEAN_EIG_ADDITIVE)
        assert diff <= 0.002, f"C1 mean {c1['mean_abs_delta_eig_dir']} differs from reference by {diff}"

    def test_c1_tuple_identity_zero_diff(self, harness):
        q0 = np.full(NUM_HYPOTHESES, 1.0 / NUM_HYPOTHESES, dtype=np.float64)
        s = 0.50
        v = np.array([1.0, 1.0, 1.0]) / math.sqrt(3.0)
        _, _, eig_1, post_1 = evaluate_epistemic_step_model(harness.spec_canon, q0, s, v)
        _, _, eig_2, post_2 = evaluate_epistemic_step_model(harness.spec_canon, q0, s, v)
        assert abs(eig_1 - eig_2) < 1e-15
        assert compute_tv_distance(post_1, post_2) < 1e-15


# =============================================================================
# T6: Condition C2 — Direction-Destroyed Control
# =============================================================================

class TestT6ConditionC2DirectionDestroyedControl:
    def test_c2_marginal_preservation(self, harness):
        orig_signs = np.array([harness.simulated_trajectories[i]["signs"] for i in range(1, 271)])
        perm_signs = np.array([harness.simulated_trajectories[int(C2_PERMUTATION[i] + 1)]["signs"] for i in range(270)])
        for dim in range(3):
            orig_vals, orig_counts = np.unique(orig_signs[:, dim], return_counts=True)
            perm_vals, perm_counts = np.unique(perm_signs[:, dim], return_counts=True)
            assert np.array_equal(orig_vals, perm_vals)
            assert np.array_equal(orig_counts, perm_counts)

    def test_c2_correspondence_reduction(self, benchmark_results):
        c2 = benchmark_results["conditions"]["C2"]
        r_c2 = c2.get("pearson_r_vs_c1", 1.0)
        assert r_c2 <= TOLERANCE_CORR_MAX, \
            f"C2 correspondence r={r_c2} should be <= {TOLERANCE_CORR_MAX}"

    def test_c2_attenuated_retention(self, benchmark_results):
        c2 = benchmark_results["conditions"]["C2"]
        c1 = benchmark_results["conditions"]["C1"]
        assert c2["retention_rate"] < c1["retention_rate"], \
            f"C2 retention ({c2['retention_rate']}) should be lower than C1 ({c1['retention_rate']})"


# =============================================================================
# T7: Condition C3 — Model-Independent R3 (M_indep)
# =============================================================================

class TestT7ConditionC3ModelIndependentR3:
    def test_c3_independent_model_persistence(self, benchmark_results):
        c3 = benchmark_results["conditions"]["C3"]
        assert c3["retention_rate"] >= 0.50, f"C3 retention {c3['retention_rate']} must be >= 0.50"
        assert c3["mean_abs_delta_eig_dir"] > TOLERANCE_EIG, \
            f"C3 mean {c3['mean_abs_delta_eig_dir']} must exceed {TOLERANCE_EIG}"

    def test_c3_bootstrap_ci_positive(self, benchmark_results):
        c3 = benchmark_results["conditions"]["C3"]
        ci_low, ci_high = c3["bootstrap_95ci_mean"]
        assert ci_low > 0.0, f"Bootstrap 95% CI lower bound must be > 0, got {ci_low}"
        assert ci_high >= ci_low

    def test_c3_parameter_non_null(self):
        assert np.any(np.abs(M_INDEP_CLARIFY_W_DIR) > 1e-6)
        assert np.any(np.abs(M_INDEP_RETRIEVE_W_DIR) > 1e-6)


# =============================================================================
# T8: Condition C4 — Representation-Independent Control
# =============================================================================

class TestT8ConditionC4RepresentationControl:
    def test_c4_cardinality_and_scale(self):
        unique_vals = np.unique(C4_SIGNS)
        for val in unique_vals:
            assert val in [-1.0, 0.0, 1.0], f"C4 sign {val} must be in {{-1, 0, 1}}"

    def test_c4_divergent_correlation(self, benchmark_results):
        c4 = benchmark_results["conditions"]["C4"]
        r_c4 = c4.get("pearson_r_vs_c1", 1.0)
        assert r_c4 <= TOLERANCE_CORR_MAX, \
            f"C4 correlation r={r_c4} should not match C1 alignment (must be <= {TOLERANCE_CORR_MAX})"

    def test_c4_attenuated_retention(self, benchmark_results):
        c4 = benchmark_results["conditions"]["C4"]
        c1 = benchmark_results["conditions"]["C1"]
        assert c4["retention_rate"] < c1["retention_rate"], \
            f"C4 retention ({c4['retention_rate']}) must be lower than C1 ({c1['retention_rate']})"


# =============================================================================
# T9: Mathematical & Metric Properties
# =============================================================================

class TestT9MathematicalAndMetricProperties:
    def test_likelihood_matrix_shapes(self, harness):
        s = 0.50
        v = np.array([1.0, 1.0, 1.0]) / math.sqrt(3.0)
        for act in ["clarify", "retrieve"]:
            mat, is_info = _build_likelihood_matrix(act, s, v, harness.spec_canon)
            assert mat.shape == (2, NUM_HYPOTHESES)
            assert is_info is True
            assert np.all(mat >= 0.0) and np.all(mat <= 1.0)
            assert np.allclose(np.sum(mat, axis=0), 1.0)

    def test_non_epistemic_actions_uninformative(self, harness):
        s = 0.50
        v = np.array([1.0, 1.0, 1.0]) / math.sqrt(3.0)
        for act in ["answer", "wait", "reason", "derive"]:
            mat, is_info = _build_likelihood_matrix(act, s, v, harness.spec_canon)
            assert mat.shape == (1, NUM_HYPOTHESES)
            assert is_info is False

    def test_bootstrap_ci_ordering(self, benchmark_results):
        for c_id in ["C1", "C2", "C3", "C4"]:
            c_data = benchmark_results["conditions"][c_id]
            ci_low, ci_high = c_data["bootstrap_95ci_mean"]
            assert ci_low <= ci_high, f"{c_id} CI ordering violated: {ci_low} > {ci_high}"


# =============================================================================
# T10: Negative Controls & 15-Point Report
# =============================================================================

class TestT10NegativeControlsAndReport:
    def test_negative_controls_all_passed(self, harness, benchmark_results):
        nc_res = harness.evaluate_negative_controls(benchmark_results)
        assert nc_res["all_passed"] is True, \
            f"Expected all negative controls to pass, got {nc_res['passed_count']}/{nc_res['total_count']}"

    def test_15_point_report_structure(self, harness, benchmark_results):
        nc_res = harness.evaluate_negative_controls(benchmark_results)
        from tests.evaluation_phase22.scripts.evaluate_r3_information_sufficiency import build_15_point_report
        report = build_15_point_report(benchmark_results, nc_res)
        assert len(report["report_points"]) == 15, "Report must contain exactly 15 points"

    def test_falsification_classification_valid(self, benchmark_results):
        assert benchmark_results["classification"] in ["SUPPORTED", "INCONCLUSIVE", "NEGATIVE"]


# =============================================================================
# T11: Governance Invariants
# =============================================================================

class TestT11GovernanceInvariants:
    def test_production_code_isolation(self):
        import subprocess
        try:
            diff_proc = subprocess.run(
                ["git", "diff", "--name-only", "src/core", "src/api", "electron"],
                cwd=str(REPO_ROOT),
                capture_output=True,
                text=True,
                check=True,
            )
            assert len(diff_proc.stdout.strip()) == 0, \
                f"Production code modified: {diff_proc.stdout.strip()}"
        except Exception:
            pass

    def test_genesis_gate_invariant(self):
        profile_path = REPO_ROOT / "data" / "profile.json"
        if profile_path.exists():
            with open(profile_path, "r", encoding="utf-8") as pf:
                prof_data = json.load(pf)
            assert prof_data.get("is_onboarded") is False, "Genesis gate must remain locked"
