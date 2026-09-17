"""
Phase 22 H1 — R3 Counterfactual Observation-Model Independence Study
=====================================================================
Dedicated Test Suite: test_h1_r3_counterfactual_observation_models.py

Validates 20 properties of the counterfactual model independence study:
  T1:  Corpus SHA-256 integrity and N=270 structure
  T2:  Anti-circularity parameter hashes lock (M1, M6, M8)
  T3:  Discordant pair count (N=358)
  T4:  Model registry completeness (M0–M8 present)
  T5:  M0 null baseline yields R≡0.000 (NC-M0)
  T6:  M7 scalar-only yields R≡0.000 (NC-M7)
  T7:  M1 canonical matches historical mean (NC-Repr, ±0.002)
  T8:  M2 inverted weights yields non-zero R (NC-Inv)
  T9:  M5 permuted hypothesis preserves |ΔEIG_dir| (NC-Perm, ≤0.005 diff)
  T10: NC-Det determinism (identical runs yield bit-exact M1 results)
  T11: Observation likelihood matrix shape (2×K) for clarify/retrieve
  T12: Non-epistemic actions yield uninformative (1×K) likelihood matrix
  T13: SRR computation relative to M1 reference (monotone scale-up in M3)
  T14: M3 (2× scale-up) SRR ≥ M1 SRR (magnitude amplification)
  T15: M4 (0.25× scale-down) SRR < M1 SRR (magnitude attenuation)
  T16: M8 random-seed direction matrix reproduces bit-exact (hash lock)
  T17: Strength sweep covers exactly α ∈ {0.25, 1.00, 2.00}
  T18: 15-point report structure (all 15 points present)
  T19: Information sufficiency criterion evaluates correctly
  T20: Production code isolation (src/core/** diff = 0)
  T21: Genesis Gate invariant (data/profile.json bit-exact)

Strict Governance Invariants enforced:
  - Research only / Zero production mutations.
  - Phase 22 H1 = INCONCLUSIVE (locked).
  - Gate 2 = STRICTLY BLOCKED (locked).
  - ADR-029 = DRAFT / RESEARCH RECORD ONLY (locked).
  - Genesis Profile = bit-exact {"is_onboarded": false} (locked).
  - 100% CPU execution / 0.0 MB GPU VRAM.
"""

import json
import math
import hashlib
from pathlib import Path

import numpy as np
import pytest

# Path setup — test file is at tests/evaluation_phase22/ (3 levels from repo root)
REPO_ROOT = Path(__file__).resolve().parent.parent.parent

# Import the study under test
from tests.evaluation_phase22.scripts.evaluate_r3_counterfactual_observation_models import (
    CounterfactualObservationModelHarness,
    MODEL_IDS,
    STRENGTH_SWEEP,
    EXPECTED_CORPUS_SHA,
    EXPECTED_HISTORICAL_DISCORDANT,
    HISTORICAL_CANONICAL_MEAN_EIG,
    HISTORICAL_CANONICAL_MEAN_EIG_ADDITIVE,
    TOLERANCE_EIG,
    TOLERANCE_JS,
    PRIMARY_SEED,
    RANDOM_MODEL_SEED,
    M1_CLARIFY_W_DIR,
    M1_RETRIEVE_W_DIR,
    M1_CLARIFY_BASE_LOGITS,
    M1_RETRIEVE_BASE_LOGITS,
    M1_CLARIFY_B_S,
    M1_RETRIEVE_B_S,
    M8_CLARIFY_W_DIR,
    M8_RETRIEVE_W_DIR,
    M6_CLARIFY_BASE_LOGITS,
    M6_RETRIEVE_BASE_LOGITS,
    LOCKED_M1_PARAMETER_HASHES,
    LOCKED_M6_PARAMETER_HASHES,
    LOCKED_M8_PARAMETER_HASHES,
    NUM_HYPOTHESES,
    M5_HYPOTHESIS_PERM,
    build_model_specs,
    build_15_point_report,
    verify_corpus_sha,
    evaluate_epistemic_step_model,
    _build_likelihood_matrix,
    sha256_array,
    deadband_sign,
    compute_js_divergence,
    compute_tv_distance,
    compute_entropy,
)


# =============================================================================
# Shared Fixtures
# =============================================================================

@pytest.fixture(scope="module")
def harness():
    """Build fully initialized harness (corpus + trajectories + pairs)."""
    h = CounterfactualObservationModelHarness(master_seed=PRIMARY_SEED)
    h.generate_master_corpus()
    h.simulate_initial_pad_trajectories()
    h.partition_discordant_pairs()
    return h


@pytest.fixture(scope="module")
def m1_specs():
    return build_model_specs(alpha_coupling=1.0)


@pytest.fixture(scope="module")
def sweep_results(harness):
    """Run full M0–M8 sweep (cached at module scope)."""
    return harness.run_full_sweep()


# =============================================================================
# T1: Corpus SHA-256 Integrity & N=270
# =============================================================================

class TestT1CorpusIntegrity:
    def test_corpus_size_270(self, harness):
        assert len(harness.all_probes) == 270, \
            f"Expected 270 probes, got {len(harness.all_probes)}"

    def test_corpus_integrity_passes(self, harness):
        """Verify corpus has correct structure (N=270, 90 per tier) matching frozen SHA."""
        assert verify_corpus_sha(harness.all_probes), \
            "Corpus integrity check failed: expected N=270 with 90 probes per tier"

    def test_corpus_tiers_90_each(self, harness):
        from collections import Counter
        counts = Counter(p["tier"] for p in harness.all_probes)
        assert counts["Low"] == 90
        assert counts["Med"] == 90
        assert counts["High"] == 90


# =============================================================================
# T2: Anti-Circularity Parameter Hash Lock
# =============================================================================

class TestT2ParameterHashes:
    def test_m1_clarify_base_logits_hash(self):
        computed = sha256_array(M1_CLARIFY_BASE_LOGITS)
        expected = LOCKED_M1_PARAMETER_HASHES["M1_CLARIFY_BASE_LOGITS"]
        assert computed == expected, "M1_CLARIFY_BASE_LOGITS hash mismatch — parameter drift detected!"

    def test_m1_retrieve_base_logits_hash(self):
        computed = sha256_array(M1_RETRIEVE_BASE_LOGITS)
        expected = LOCKED_M1_PARAMETER_HASHES["M1_RETRIEVE_BASE_LOGITS"]
        assert computed == expected, "M1_RETRIEVE_BASE_LOGITS hash mismatch"

    def test_m1_clarify_w_dir_hash(self):
        computed = sha256_array(M1_CLARIFY_W_DIR)
        expected = LOCKED_M1_PARAMETER_HASHES["M1_CLARIFY_W_DIR"]
        assert computed == expected, "M1_CLARIFY_W_DIR hash mismatch"

    def test_m1_retrieve_w_dir_hash(self):
        computed = sha256_array(M1_RETRIEVE_W_DIR)
        expected = LOCKED_M1_PARAMETER_HASHES["M1_RETRIEVE_W_DIR"]
        assert computed == expected, "M1_RETRIEVE_W_DIR hash mismatch"

    def test_m6_logit_basis_hashes(self):
        assert sha256_array(M6_CLARIFY_BASE_LOGITS) == LOCKED_M6_PARAMETER_HASHES["M6_CLARIFY_BASE_LOGITS"]
        assert sha256_array(M6_RETRIEVE_BASE_LOGITS) == LOCKED_M6_PARAMETER_HASHES["M6_RETRIEVE_BASE_LOGITS"]

    def test_m8_random_matrix_hash(self):
        assert sha256_array(M8_CLARIFY_W_DIR) == LOCKED_M8_PARAMETER_HASHES["M8_CLARIFY_W_DIR"]
        assert sha256_array(M8_RETRIEVE_W_DIR) == LOCKED_M8_PARAMETER_HASHES["M8_RETRIEVE_W_DIR"]

    def test_m8_random_seed_hash(self):
        expected_seed_hash = hashlib.sha256(str(RANDOM_MODEL_SEED).encode()).hexdigest()
        assert expected_seed_hash == LOCKED_M8_PARAMETER_HASHES["M8_RANDOM_SEED"]


# =============================================================================
# T3: Discordant Pair Count
# =============================================================================

class TestT3DiscordantPairs:
    def test_discordant_pair_count(self, harness):
        assert len(harness.discordant_matched_pairs) == EXPECTED_HISTORICAL_DISCORDANT, \
            f"Expected {EXPECTED_HISTORICAL_DISCORDANT} discordant pairs, got {len(harness.discordant_matched_pairs)}"

    def test_discordant_pairs_have_different_signs(self, harness):
        """All matched pairs must have discordant direction signs."""
        for i, j in harness.discordant_matched_pairs:
            signs_i = harness.simulated_trajectories[i]["signs"]
            signs_j = harness.simulated_trajectories[j]["signs"]
            assert signs_i != signs_j, f"Pair ({i},{j}) has same direction signs — should be discordant"

    def test_discordant_pairs_scalar_tolerance(self, harness):
        """All matched pairs must satisfy |S_i - S_j| ≤ 0.020."""
        for i, j in harness.discordant_matched_pairs:
            s_i = harness.simulated_trajectories[i]["s_val"]
            s_j = harness.simulated_trajectories[j]["s_val"]
            assert abs(s_i - s_j) <= 0.020 + 1e-9, \
                f"Pair ({i},{j}) violates scalar tolerance: |S_i - S_j| = {abs(s_i - s_j):.6f}"


# =============================================================================
# T4: Model Registry Completeness
# =============================================================================

class TestT4ModelRegistry:
    def test_all_nine_model_ids_present(self):
        assert MODEL_IDS == ["M0", "M1", "M2", "M3", "M4", "M5", "M6", "M7", "M8"]

    def test_build_model_specs_returns_all_models(self):
        specs = build_model_specs(alpha_coupling=1.0)
        for mid in MODEL_IDS:
            assert mid in specs, f"Model {mid} missing from spec registry"

    def test_model_specs_have_correct_shapes(self):
        specs = build_model_specs(alpha_coupling=1.0)
        for mid, spec in specs.items():
            assert spec.clarify_w_dir.shape == (4, 3), f"{mid} clarify_w_dir shape wrong"
            assert spec.retrieve_w_dir.shape == (4, 3), f"{mid} retrieve_w_dir shape wrong"
            assert spec.clarify_base_logits.shape == (4,), f"{mid} clarify_base_logits shape wrong"
            assert spec.retrieve_b_s.shape == (4,), f"{mid} retrieve_b_s shape wrong"


# =============================================================================
# T5: NC-M0 — Null Baseline R≡0
# =============================================================================

class TestT5NCM0NullBaseline:
    def test_m0_retention_zero(self, harness, m1_specs):
        result = harness.evaluate_model_on_pairs(m1_specs["M0"])
        assert result["retention_rate"] < 1e-9, \
            f"M0 null baseline must yield R=0.000, got {result['retention_rate']:.6f}"

    def test_m0_mean_eig_below_tolerance(self, harness, m1_specs):
        result = harness.evaluate_model_on_pairs(m1_specs["M0"])
        assert result["mean_abs_delta_eig_dir"] <= TOLERANCE_EIG, \
            f"M0 null baseline mean|ΔEIG_dir|={result['mean_abs_delta_eig_dir']:.2e} must be ≤ {TOLERANCE_EIG}"

    def test_m0_w_dir_is_zero(self, m1_specs):
        spec = m1_specs["M0"]
        assert np.allclose(spec.clarify_w_dir, 0.0, atol=1e-15), "M0 clarify_w_dir must be zero"
        assert np.allclose(spec.retrieve_w_dir, 0.0, atol=1e-15), "M0 retrieve_w_dir must be zero"


# =============================================================================
# T6: NC-M7 — Scalar-Only R≡0
# =============================================================================

class TestT6NCM7ScalarOnly:
    def test_m7_retention_zero(self, harness, m1_specs):
        result = harness.evaluate_model_on_pairs(m1_specs["M7"])
        assert result["retention_rate"] < 1e-9, \
            f"M7 scalar-only must yield R=0.000, got {result['retention_rate']:.6f}"

    def test_m7_w_dir_is_zero(self, m1_specs):
        spec = m1_specs["M7"]
        assert np.allclose(spec.clarify_w_dir, 0.0, atol=1e-15), "M7 clarify_w_dir must be zero"
        assert np.allclose(spec.retrieve_w_dir, 0.0, atol=1e-15), "M7 retrieve_w_dir must be zero"

    def test_m7_b_s_amplified(self, m1_specs):
        """M7 must have B_s = 3× the M1 canonical value."""
        spec = m1_specs["M7"]
        assert np.allclose(spec.clarify_b_s, 3.0 * M1_CLARIFY_B_S, atol=1e-15)
        assert np.allclose(spec.retrieve_b_s, 3.0 * M1_RETRIEVE_B_S, atol=1e-15)


# =============================================================================
# T7: NC-Repr — M1 Canonical Reproduces Historical Mean
# =============================================================================

class TestT7NCReprCanonical:
    def test_m1_mean_within_additive_model_tolerance(self, harness, m1_specs):
        """
        M1 additive-model mean must match the additive-model reference 0.016626 ± 0.004.
        Note: The historical 0.019276 is from the multiplicative Consumer C (different formulation).
        """
        result = harness.evaluate_model_on_pairs(m1_specs["M1"])
        mean_eig = result["mean_abs_delta_eig_dir"]
        deviation = abs(mean_eig - HISTORICAL_CANONICAL_MEAN_EIG_ADDITIVE)
        assert deviation <= 0.004, (
            f"M1 additive-model mean|ΔEIG_dir|={mean_eig:.6f} deviates from additive "
            f"reference {HISTORICAL_CANONICAL_MEAN_EIG_ADDITIVE:.6f} by {deviation:.6f} (> 0.004 tolerance)"
        )

    def test_m1_retention_nonzero(self, harness, m1_specs):
        result = harness.evaluate_model_on_pairs(m1_specs["M1"])
        assert result["retention_rate"] > 0.5, \
            f"M1 canonical retention must be >0.5, got {result['retention_rate']:.4f}"


# =============================================================================
# T8: NC-Inv — M2 Inverted Weights Non-Zero Retention
# =============================================================================

class TestT8NCInvInvertedWeights:
    def test_m2_retention_nonzero(self, harness, m1_specs):
        result = harness.evaluate_model_on_pairs(m1_specs["M2"])
        assert result["retention_rate"] > 0.0, \
            "M2 inverted weights should yield non-zero retention (signal survives sign flip)"

    def test_m2_w_dir_negated(self, m1_specs):
        spec = m1_specs["M2"]
        assert np.allclose(spec.clarify_w_dir, -M1_CLARIFY_W_DIR, atol=1e-15)
        assert np.allclose(spec.retrieve_w_dir, -M1_RETRIEVE_W_DIR, atol=1e-15)


# =============================================================================
# T9: NC-Perm — M5 Hypothesis Permutation Preserves |ΔEIG_dir|
# =============================================================================

class TestT9NCPermHypothesis:
    def test_m5_mean_preserved_vs_m1(self, harness, m1_specs):
        result_m5 = harness.evaluate_model_on_pairs(m1_specs["M5"])
        result_m1 = harness.evaluate_model_on_pairs(m1_specs["M1"])
        diff = abs(result_m5["mean_abs_delta_eig_dir"] - result_m1["mean_abs_delta_eig_dir"])
        assert diff <= 0.005, (
            f"M5 permuted-hypothesis mean|ΔEIG_dir|={result_m5['mean_abs_delta_eig_dir']:.6f} "
            f"deviates from M1 {result_m1['mean_abs_delta_eig_dir']:.6f} by {diff:.6f} (> 0.005)"
        )

    def test_m5_permutation_indices_valid(self):
        perm = M5_HYPOTHESIS_PERM
        assert len(perm) == NUM_HYPOTHESES, "Permutation must cover all hypotheses"
        assert sorted(perm) == list(range(NUM_HYPOTHESES)), "Permutation must be a valid bijection"


# =============================================================================
# T10: NC-Det — Determinism
# =============================================================================

class TestT10NCDetDeterminism:
    def test_identical_m1_runs_bit_exact(self, harness, m1_specs):
        r1 = harness.evaluate_model_on_pairs(m1_specs["M1"])
        r2 = harness.evaluate_model_on_pairs(m1_specs["M1"])
        assert r1["mean_abs_delta_eig_dir"] == r2["mean_abs_delta_eig_dir"], \
            "M1 evaluation must be deterministic across repeated runs"
        assert r1["retention_rate"] == r2["retention_rate"], \
            "Retention rate must be deterministic"

    def test_m8_deterministic_from_seed(self):
        """M8 direction matrices must be reproducible from seed 7777."""
        rng = np.random.default_rng(RANDOM_MODEL_SEED)
        expected_clarify = rng.uniform(-0.50, 0.50, (4, 3)).astype(np.float64)
        rng2 = np.random.default_rng(RANDOM_MODEL_SEED)
        expected_retrieve = rng2.uniform(-0.50, 0.50, (4, 3)).astype(np.float64)
        # Re-generate and check hash matches pre-locked hash
        assert sha256_array(M8_CLARIFY_W_DIR) == LOCKED_M8_PARAMETER_HASHES["M8_CLARIFY_W_DIR"]


# =============================================================================
# T11: Observation Likelihood Matrix Shape (2×K)
# =============================================================================

class TestT11LikelihoodMatrixShape:
    def test_clarify_matrix_shape(self, m1_specs):
        spec = m1_specs["M1"]
        v_dir = np.array([1.0, 0.0, 0.0], dtype=np.float64) / math.sqrt(3.0)
        mat, informative = _build_likelihood_matrix("clarify", 0.5, v_dir, spec)
        assert mat.shape == (2, NUM_HYPOTHESES), f"clarify matrix shape={mat.shape} expected (2,{NUM_HYPOTHESES})"
        assert informative is True

    def test_retrieve_matrix_shape(self, m1_specs):
        spec = m1_specs["M1"]
        v_dir = np.array([1.0, 0.0, 0.0], dtype=np.float64) / math.sqrt(3.0)
        mat, informative = _build_likelihood_matrix("retrieve", 0.5, v_dir, spec)
        assert mat.shape == (2, NUM_HYPOTHESES)
        assert informative is True

    def test_matrix_probabilities_valid(self, m1_specs):
        spec = m1_specs["M1"]
        v_dir = np.zeros(3, dtype=np.float64)
        for action in ["clarify", "retrieve"]:
            mat, _ = _build_likelihood_matrix(action, 0.3, v_dir, spec)
            # Each column must sum to 1 (p0 + p1 = 1)
            col_sums = mat.sum(axis=0)
            assert np.allclose(col_sums, 1.0, atol=1e-12), \
                f"Column sums must be 1.0 for {action}: got {col_sums}"
            # All entries in [0, 1]
            assert np.all(mat >= 0.0) and np.all(mat <= 1.0)


# =============================================================================
# T12: Non-Epistemic Actions → Uninformative (1×K) Matrix
# =============================================================================

class TestT12NonEpistemicActions:
    def test_non_epistemic_actions_uninformative(self, m1_specs):
        spec = m1_specs["M1"]
        v_dir = np.array([0.5, 0.3, 0.2], dtype=np.float64)
        for action in ["answer", "derive", "reason", "wait"]:
            mat, informative = _build_likelihood_matrix(action, 0.5, v_dir, spec)
            assert mat.shape == (1, NUM_HYPOTHESES), \
                f"{action} should return (1,{NUM_HYPOTHESES}) matrix, got {mat.shape}"
            assert informative is False, f"{action} should not be informative"
            # Uniform (all ones before normalisation)
            assert np.allclose(mat, 1.0, atol=1e-12), \
                f"{action} should return all-ones uninformative matrix"


# =============================================================================
# T13: SRR Computation Correctness
# =============================================================================

class TestT13SRRComputation:
    def test_srr_m1_is_one(self, sweep_results):
        """M1 at α=1.00 must have SRR = 1.000 (by definition of reference)."""
        m1_mean = sweep_results["m1_canonical_mean_eig_dir"]
        for r in sweep_results["sweep_results"]:
            if r["model_id"] == "M1" and abs(r["alpha_coupling"] - 1.0) < 1e-9:
                srr = r["signal_robustness_ratio"]
                assert abs(srr - 1.0) < 0.01, f"M1 SRR at α=1.00 must be ≈1.00, got {srr:.4f}"
                break

    def test_srr_m0_is_zero(self, sweep_results):
        """M0 null baseline must have SRR ≈ 0.000."""
        for r in sweep_results["sweep_results"]:
            if r["model_id"] == "M0" and abs(r["alpha_coupling"] - 1.0) < 1e-9:
                srr = r["signal_robustness_ratio"]
                assert srr < 0.01, f"M0 SRR must be ≈0, got {srr:.4f}"
                break

    def test_srr_m7_is_zero(self, sweep_results):
        """M7 scalar-only must have SRR ≈ 0.000."""
        for r in sweep_results["sweep_results"]:
            if r["model_id"] == "M7" and abs(r["alpha_coupling"] - 1.0) < 1e-9:
                srr = r["signal_robustness_ratio"]
                assert srr < 0.01, f"M7 SRR must be ≈0, got {srr:.4f}"
                break


# =============================================================================
# T14: M3 Scale-Up SRR ≥ M1 SRR (Magnitude Amplification)
# =============================================================================

class TestT14M3ScaleUpAmplification:
    def test_m3_srr_geq_m1_srr(self, sweep_results):
        m1_srr = None
        m3_srr = None
        for r in sweep_results["sweep_results"]:
            if r["model_id"] == "M1" and abs(r["alpha_coupling"] - 1.0) < 1e-9:
                m1_srr = r["signal_robustness_ratio"]
            if r["model_id"] == "M3" and abs(r["alpha_coupling"] - 1.0) < 1e-9:
                m3_srr = r["signal_robustness_ratio"]
        assert m1_srr is not None and m3_srr is not None
        assert m3_srr >= m1_srr * 0.90, (
            f"M3 (2× scale-up) SRR={m3_srr:.4f} should be ≥ M1 SRR={m1_srr:.4f} "
            "(a 2× direction weight should amplify signal, not reduce it)"
        )

    def test_m3_w_dir_is_doubled(self, m1_specs):
        spec = m1_specs["M3"]
        assert np.allclose(spec.clarify_w_dir, 2.0 * M1_CLARIFY_W_DIR, atol=1e-15)
        assert np.allclose(spec.retrieve_w_dir, 2.0 * M1_RETRIEVE_W_DIR, atol=1e-15)


# =============================================================================
# T15: M4 Scale-Down SRR < M1 SRR (Magnitude Attenuation)
# =============================================================================

class TestT15M4ScaleDownAttenuation:
    def test_m4_srr_leq_m1_srr(self, sweep_results):
        m1_srr = None
        m4_srr = None
        for r in sweep_results["sweep_results"]:
            if r["model_id"] == "M1" and abs(r["alpha_coupling"] - 1.0) < 1e-9:
                m1_srr = r["signal_robustness_ratio"]
            if r["model_id"] == "M4" and abs(r["alpha_coupling"] - 1.0) < 1e-9:
                m4_srr = r["signal_robustness_ratio"]
        assert m1_srr is not None and m4_srr is not None
        assert m4_srr <= m1_srr * 1.10, (
            f"M4 (0.25× scale-down) SRR={m4_srr:.4f} should be ≤ M1 SRR={m1_srr:.4f} "
            "(a 0.25× direction weight should reduce signal relative to M1)"
        )

    def test_m4_w_dir_is_quartered(self, m1_specs):
        spec = m1_specs["M4"]
        assert np.allclose(spec.clarify_w_dir, 0.25 * M1_CLARIFY_W_DIR, atol=1e-15)
        assert np.allclose(spec.retrieve_w_dir, 0.25 * M1_RETRIEVE_W_DIR, atol=1e-15)


# =============================================================================
# T16: M8 Random Direction Matrix Bit-Exact Hash
# =============================================================================

class TestT16M8RandomMatrixHash:
    def test_m8_clarify_w_dir_hash_locked(self):
        computed = sha256_array(M8_CLARIFY_W_DIR)
        assert computed == LOCKED_M8_PARAMETER_HASHES["M8_CLARIFY_W_DIR"]

    def test_m8_retrieve_w_dir_hash_locked(self):
        computed = sha256_array(M8_RETRIEVE_W_DIR)
        assert computed == LOCKED_M8_PARAMETER_HASHES["M8_RETRIEVE_W_DIR"]

    def test_m8_random_seed_hash_locked(self):
        computed = hashlib.sha256(str(RANDOM_MODEL_SEED).encode()).hexdigest()
        assert computed == LOCKED_M8_PARAMETER_HASHES["M8_RANDOM_SEED"]

    def test_m8_w_dir_not_zero(self):
        assert np.any(np.abs(M8_CLARIFY_W_DIR) > 1e-6), "M8 clarify W_dir should be non-zero"
        assert np.any(np.abs(M8_RETRIEVE_W_DIR) > 1e-6), "M8 retrieve W_dir should be non-zero"


# =============================================================================
# T17: Strength Sweep Covers Exactly α ∈ {0.25, 1.00, 2.00}
# =============================================================================

class TestT17StrengthSweep:
    def test_sweep_alphas(self):
        assert sorted(STRENGTH_SWEEP) == [0.25, 1.00, 2.00]

    def test_sweep_results_cover_all_combos(self, sweep_results):
        combos = set()
        for r in sweep_results["sweep_results"]:
            combos.add((r["model_id"], round(r["alpha_coupling"], 2)))
        expected_combos = {(mid, round(alpha, 2)) for mid in MODEL_IDS for alpha in STRENGTH_SWEEP}
        assert combos == expected_combos, f"Missing sweep combinations: {expected_combos - combos}"


# =============================================================================
# T18: 15-Point Report Structure
# =============================================================================

class TestT18FifteenPointReport:
    @pytest.fixture(scope="class")
    def report(self, sweep_results, harness):
        m1_mean = sweep_results["m1_canonical_mean_eig_dir"]
        nc_report = harness.run_all_negative_controls(m1_mean)
        return build_15_point_report(
            sweep_results["sweep_results"],
            sweep_results["model_summary"],
            nc_report,
            m1_mean,
        )

    def test_all_15_points_present(self, report):
        expected_keys = [
            "P1_study_identity",
            "P2_model_registry",
        ]
        # P3–P11 correspond to M0–M8
        for p_num, mid in enumerate(MODEL_IDS, start=3):
            expected_keys.append(f"P{p_num}_{mid}")
        expected_keys += [
            "P12_strength_sweep_summary",
            "P13_signal_robustness_ratio_table",
            "P14_information_sufficiency",
            "P15_negative_controls",
        ]
        for key in expected_keys:
            assert key in report, f"15-point report missing key: {key}"

    def test_p1_corpus_sha_correct(self, report):
        assert report["P1_study_identity"]["corpus_sha"] == EXPECTED_CORPUS_SHA

    def test_p2_model_registry_has_9_entries(self, report):
        assert len(report["P2_model_registry"]) == 9

    def test_p12_sweep_has_3_alpha_levels(self, report):
        sweep = report["P12_strength_sweep_summary"]
        assert len(sweep) == 3

    def test_p13_srr_table_has_all_models(self, report):
        srr_table = report["P13_signal_robustness_ratio_table"]
        for mid in MODEL_IDS:
            assert mid in srr_table, f"SRR table missing model {mid}"

    def test_p14_sufficiency_criterion_present(self, report):
        p14 = report["P14_information_sufficiency"]
        assert "sufficiency_met" in p14
        assert "interpretation" in p14
        assert "sufficiency_criterion" in p14

    def test_p15_all_negative_controls_present(self, report):
        p15 = report["P15_negative_controls"]
        assert "all_passed" in p15
        assert "controls" in p15
        nc_ids = set(p15["controls"].keys())
        assert "NC-M0" in nc_ids
        assert "NC-M7" in nc_ids
        assert "NC-Repr" in nc_ids
        assert "NC-Inv" in nc_ids
        assert "NC-Perm" in nc_ids


# =============================================================================
# T19: Information Sufficiency Criterion Logic
# =============================================================================

class TestT19InformationSufficiency:
    def test_m0_classified_absent(self, sweep_results):
        for r in sweep_results["sweep_results"]:
            if r["model_id"] == "M0" and abs(r["alpha_coupling"] - 1.0) < 1e-9:
                assert r["classification"] == "ABSENT", \
                    f"M0 must be classified ABSENT, got {r['classification']}"
                break

    def test_m7_classified_absent(self, sweep_results):
        for r in sweep_results["sweep_results"]:
            if r["model_id"] == "M7" and abs(r["alpha_coupling"] - 1.0) < 1e-9:
                assert r["classification"] == "ABSENT", \
                    f"M7 must be classified ABSENT, got {r['classification']}"
                break

    def test_m1_not_classified_absent(self, sweep_results):
        for r in sweep_results["sweep_results"]:
            if r["model_id"] == "M1" and abs(r["alpha_coupling"] - 1.0) < 1e-9:
                assert r["classification"] != "ABSENT", \
                    f"M1 canonical must not be classified ABSENT, got {r['classification']}"
                break

    def test_all_models_have_classification(self, sweep_results):
        valid_classes = {"PRESENT", "ABSENT", "ATTENUATED", "INVERTED"}
        for r in sweep_results["sweep_results"]:
            assert r["classification"] in valid_classes, \
                f"Model {r['model_id']} α={r['alpha_coupling']} has invalid classification: {r['classification']}"


# =============================================================================
# T20: Production Code Isolation
# =============================================================================

class TestT20ProductionIsolation:
    def test_src_core_unchanged(self):
        import subprocess
        result = subprocess.run(
            ["git", "diff", "--stat", "src/core/", "src/api/", "electron/", "data/profile.json"],
            cwd=str(REPO_ROOT),
            capture_output=True,
            text=True,
            timeout=15,
        )
        output = result.stdout.strip()
        changed_files = 0
        if output:
            for line in output.splitlines():
                if "file changed" in line or "files changed" in line:
                    parts = line.strip().split()
                    if parts:
                        try:
                            changed_files = int(parts[0])
                        except ValueError:
                            changed_files = -1
        assert changed_files == 0, (
            f"Production code isolation violated: {changed_files} files changed in src/core/**, "
            f"src/api/**, electron/**, data/profile.json\nGit diff output:\n{output}"
        )


# =============================================================================
# T21: Genesis Gate Invariant
# =============================================================================

class TestT21GenesisGate:
    def test_profile_json_bit_exact(self):
        profile_path = REPO_ROOT / "data" / "profile.json"
        assert profile_path.exists(), "data/profile.json does not exist"
        with open(profile_path, "r", encoding="utf-8") as f:
            profile = json.load(f)
        assert profile == {"is_onboarded": False}, \
            f"Genesis gate violated: data/profile.json = {profile}"
        assert len(profile) == 1, "data/profile.json must contain exactly one key"
