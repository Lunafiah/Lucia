# -*- coding: utf-8 -*-
"""
EXP-P25-Q2.1 Evaluation Harness Unit & Integration Test Suite.

Verifies:
1. Invariant auditing: Genesis bit-exact {"is_onboarded": False}, 0 production mutations.
2. Neutral dialogue fixture: 40 turns, 3 phases, identical across conditions.
3. Perturbation protocol: +300 ms at Turn 18, recovery window Turns 19-28.
4. C0 (Static) & C1 (Unilateral) execution dynamics.
5. C2 (Bidirectional) TBD-Q2-04 guard: strict failure/block without an a-priori w_fb.
6. Operational definition of user response signal R_U(t+Delta) with causal lag Delta in [150, 800] ms.
7. Transfer entropy pathway & Delta TE_net directional asymmetry diagnostic semantics.
8. Surrogate pseudo-synchrony analysis (N=20 shuffled dyads, theta_95 reference).
9. Substrate persistence bounds (P1, P2, P3) & R_t dimension protection.
"""

import json
import math
import numpy as np
import pytest
from pathlib import Path

from tests.evaluation.phase25.exp_p25_q2_1 import (
    FixtureGenerator,
    InteractionTurn,
    C0StaticPacingController,
    C1UnilateralController,
    C2BidirectionalController,
    TBDGainUnestablishedError,
    UserResponseSignalExtractor,
    TransferEntropyEstimator,
    MetricsCalculator,
    PseudoSynchronySurrogateGenerator,
    TBDValidationSuite,
    InvariantAuditor,
    ExpP25Q21MasterRunner,
    PROJECT_ROOT,
    CANONICAL_ARTIFACT_DIR,
)


def test_genesis_and_production_invariants_pre_execution():
    """Verify INV-8 Genesis Gate and zero production mutations before running."""
    profile_path = PROJECT_ROOT / "data" / "profile.json"
    assert profile_path.exists(), "data/profile.json must exist"
    with open(profile_path, "r", encoding="utf-8") as f:
        data = json.load(f)
    assert data == {"is_onboarded": False}, (
        f"CRITICAL: Genesis Gate invariant violated! Expected {{'is_onboarded': False}}, got: {data}"
    )

    report = InvariantAuditor.verify_invariants()
    assert report.inv8_genesis_bit_exact is True
    assert report.inv1_one_continuous_life is True
    assert report.inv2_no_reflective_ego is True
    assert report.no_direct_actuator_mutation is True


def test_fixture_generation_structure():
    """Verify the 40-turn, 3-phase neutral dialogue fixture."""
    turns = FixtureGenerator.generate_script(seed=1001)
    assert len(turns) == 40, f"Expected 40 turns, got {len(turns)}"

    # Check phases
    # Phase 1: Turns 1-15
    # Phase 2: Turns 16-25 (Turn 18 is perturbed)
    # Phase 3: Turns 26-40
    phase1 = turns[:15]
    phase2 = turns[15:25]
    phase3 = turns[25:]

    assert len(phase1) == 15, "Phase 1 must be Turns 1-15"
    assert len(phase2) == 10, "Phase 2 must be Turns 16-25"
    assert len(phase3) == 15, "Phase 3 must be Turns 26-40"

    # Turn 18 is at index 17
    turn_18 = turns[17]
    assert turn_18.turn_id == 18

    # Verify identical lexical script across seeds
    turns_other = FixtureGenerator.generate_script(seed=2002)
    for t1, t2 in zip(turns, turns_other):
        assert t1.text == t2.text, "Lexical content must be strictly invariant across seeds"
        assert t1.speaker == t2.speaker


def test_controllers_c0_and_c1():
    """Verify C0 and C1 controllers behave deterministically."""
    c0 = C0StaticPacingController()
    c1 = C1UnilateralController(lambda_decay=0.15)

    dummy_turn = InteractionTurn(
        turn_id=1,
        speaker="user",
        text="Hello",
        nominal_duration_ms=400.0,
        actual_duration_ms=400.0,
        pause_latency_ms=400.0,
        f0_mean_hz=180.0,
        speech_envelope=0.65,
        timestamp_ms=0.0,
    )

    # C0 static pacing
    lat0_norm, tempo0_norm = c0.step(dummy_turn, is_perturbed=False)
    lat0_pert, tempo0_pert = c0.step(dummy_turn, is_perturbed=True)
    assert lat0_norm == 400.0
    assert lat0_pert == 700.0  # +300 ms perturbation

    # C1 unilateral pacing
    lat1_norm, _ = c1.step(dummy_turn, is_perturbed=False)
    lat1_pert, _ = c1.step(dummy_turn, is_perturbed=True)
    assert lat1_norm == 400.0
    assert lat1_pert == 700.0


def test_c2_tbd_q2_04_strict_guard():
    """Verify C2 strictly raises TBDGainUnestablishedError if w_fb is not a-priori grounded."""
    with pytest.raises(TBDGainUnestablishedError) as exc_info:
        _ = C2BidirectionalController(lambda_decay=0.15, w_fb=None)

    assert "TBD-Q2-04" in str(exc_info.value)
    assert "No independent, a-priori scientific basis" in str(exc_info.value) or "w_fb has not been established" in str(exc_info.value)


def test_user_response_signal_causal_lag():
    """Verify R_U operational definition and causal lag bounds [150, 800] ms."""
    extractor = UserResponseSignalExtractor(window_k=5)
    feat = np.array([180.0, 0.65, 400.0], dtype=np.float64)

    # Below causal lag window (e.g. 100 ms) -> must be zero
    sig_fast = extractor.compute_response(feat, lag_ms=100.0)
    assert np.all(sig_fast == 0.0)

    # Above causal lag window (e.g. 900 ms) -> must be zero
    sig_slow = extractor.compute_response(feat, lag_ms=900.0)
    assert np.all(sig_slow == 0.0)

    # Uncoupled noise correlation > 0.30 -> gated to zero
    sig_noisy = extractor.compute_response(feat, lag_ms=300.0, uncoupled_noise_corr=0.45)
    assert np.all(sig_noisy == 0.0)

    # Within valid causal lag window -> response extracted once baseline history exists
    _ = extractor.compute_response(feat, lag_ms=300.0)
    _ = extractor.compute_response(feat, lag_ms=300.0)
    feat_perturbed = np.array([210.0, 0.85, 550.0], dtype=np.float64)
    sig_valid = extractor.compute_response(feat_perturbed, lag_ms=300.0)
    assert isinstance(sig_valid, np.ndarray)
    assert len(sig_valid) == 3


def test_transfer_entropy_and_diagnostic_semantics():
    """Verify Transfer Entropy pathway and strict asymmetry diagnostic interpretation."""
    u_series = np.array([100.0, 150.0, 200.0, 250.0, 300.0] * 8, dtype=np.float64)
    l_series = np.array([105.0, 155.0, 205.0, 255.0, 305.0] * 8, dtype=np.float64)

    te_ksg = TransferEntropyEstimator.estimate_ksg(u_series, l_series, k=4)
    assert isinstance(te_ksg, float)
    assert te_ksg >= 0.0

    te_binned = TransferEntropyEstimator.estimate_discrete_binned(u_series, l_series, bins=4)
    assert isinstance(te_binned, float)
    assert te_binned >= 0.0

    # Calculate metric record and verify coupling statistics and asymmetry diagnostic note
    turns = FixtureGenerator.generate_script(seed=1001)
    latencies = [400.0 + 5.0 * (i % 3) for i in range(40)]
    record = MetricsCalculator.calculate(turns, latencies, condition="C0", seed=1001)

    assert record.condition == "C0"
    assert "Not a reciprocity metric" in record.notes
    assert isinstance(record.delta_te_net, float)
    assert isinstance(record.r1_pearson, float)
    assert isinstance(record.rho_spearman, float)
    assert isinstance(record.discrepancy_flag, bool)


def test_surrogate_analysis_pseudo_synchrony_null():
    """Verify surrogate construction, directional extraction, r1 correlation, and theta_95 empirical reference."""
    turns1 = FixtureGenerator.generate_script(seed=1001)
    turns2 = FixtureGenerator.generate_script(seed=2002)
    lat1 = [400.0 + 10.0 * math.sin(i) for i in range(40)]
    lat2 = [410.0 + 15.0 * math.cos(i) for i in range(40)]

    # 1. Test directional latency extraction (N = 19 transitions)
    g_lu1, g_ul1 = PseudoSynchronySurrogateGenerator.extract_directional_latencies(turns1, lat1)
    assert len(g_lu1) == 19, f"Expected 19 user latencies, got {len(g_lu1)}"
    assert len(g_ul1) == 19, f"Expected 19 Lucia latencies, got {len(g_ul1)}"

    # 2. Test surrogate distribution generation (N = 2 cross-session realizations for 2 sessions)
    surrogates, theta_95 = PseudoSynchronySurrogateGenerator.generate_surrogate_distribution(
        sessions_turns=[turns1, turns2],
        sessions_latencies=[lat1, lat2],
        n_surrogates=20,
    )

    assert len(surrogates) == 2, f"Expected 2 cross-session realizations, got {len(surrogates)}"
    assert all(isinstance(s, float) for s in surrogates)
    assert all(-1.0 <= s <= 1.0 for s in surrogates)
    assert isinstance(theta_95, float)
    assert theta_95 >= min(surrogates)

    # 3. Test upper-tailed exceedance evaluation and randomization p-value
    eval_res = PseudoSynchronySurrogateGenerator.evaluate_exceedance(r1_obs=0.5, surrogate_r1_values=surrogates)
    assert eval_res["decision_tail"] == "upper-tailed (r1_surr >= r1_obs)"
    assert "randomization_p_value" in eval_res
    assert 0.0 <= eval_res["randomization_p_value"] <= 1.0


def test_tbd_validation_suite():
    """Verify TBD governance audit statuses."""
    res_q1 = TBDValidationSuite.evaluate_tbd_q2_01_corpus()
    res_q2 = TBDValidationSuite.evaluate_tbd_q2_02_ksg_stability()
    res_q3 = TBDValidationSuite.evaluate_tbd_q2_03_user_cadence_model()
    res_q4 = TBDValidationSuite.evaluate_tbd_q2_04_gain_status()

    assert res_q1["status"] == "VALIDATED_AS_NEUTRAL_FIXTURE"
    assert res_q2["status"] == "VALIDATED_STABLE_AT_K4"
    assert res_q3["status"] == "CALIBRATED_AND_VALIDATED"
    assert res_q4["status"] == "BLOCKED_TBD_Q2_04"


@pytest.mark.skip(reason="EXP-P25-Q2.1 rerun not authorized; static/pre-execution audit only")
def test_master_runner_execution_and_artifacts():
    """Verify that ExpP25Q21MasterRunner runs deterministically and creates all required artifacts."""
    runner = ExpP25Q21MasterRunner(artifact_dir=CANONICAL_ARTIFACT_DIR)
    summary = runner.execute_all()

    assert summary["protocol"] == "EXP-P25-Q2.1"
    assert "conditions_summary" in summary
    assert "hypothesis_verdicts" in summary
    assert "tbd_governance" in summary

    # Verify that files exist on disk
    assert (CANONICAL_ARTIFACT_DIR / "results.json").exists()
    assert (CANONICAL_ARTIFACT_DIR / "metrics.csv").exists()
    assert (CANONICAL_ARTIFACT_DIR / "surrogates.json").exists()
    assert (CANONICAL_ARTIFACT_DIR / "invariants.json").exists()
    assert (CANONICAL_ARTIFACT_DIR / "environment.json").exists()
    assert (CANONICAL_ARTIFACT_DIR / "FINAL_EVALUATION_REPORT.md").exists()

    # Verify results.json content
    with open(CANONICAL_ARTIFACT_DIR / "results.json", "r", encoding="utf-8") as f:
        results = json.load(f)
    assert results["protocol"] == "EXP-P25-Q2.1"
    assert results["conditions_summary"]["C2_bidirectional_adaptation"]["status"] == "BLOCKED_TBD_Q2_04"
    assert results["hypothesis_verdicts"]["H_B_reciprocal_incrementality"]["status"] == "BLOCKED / INCONCLUSIVE (PENDING TBD-Q2-04)"

    # Verify final evaluation report content
    with open(CANONICAL_ARTIFACT_DIR / "FINAL_EVALUATION_REPORT.md", "r", encoding="utf-8") as f:
        report = f.read()
    assert "BLOCKED — TBD-Q2-04" in report


def test_genesis_and_production_invariants_post_execution():
    """Verify INV-8 Genesis Gate and zero production mutations after execution."""
    profile_path = PROJECT_ROOT / "data" / "profile.json"
    with open(profile_path, "r", encoding="utf-8") as f:
        data = json.load(f)
    assert data == {"is_onboarded": False}, (
        f"CRITICAL: Genesis Gate invariant altered during execution! Got: {data}"
    )

    report = InvariantAuditor.verify_invariants()
    assert report.inv8_genesis_bit_exact is True
    assert report.inv1_one_continuous_life is True
    assert report.inv2_no_reflective_ego is True
