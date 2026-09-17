"""
tests/evaluation_phase22/test_h1_r3_temporal_stability.py

Automated Test Suite for Phase 22 H1: R3 Temporal Stability & Sign-Jitter Feasibility Study.
Validates:
- Manifest and cryptographic hashes
- Governance invariants (H1 INCONCLUSIVE, Gate 2 BLOCKED, Protocol v1.5 NOT AUTHORIZED, Gate LOCKED)
- Raw sign mathematics and ternary discretization
- RQ1 Temporal sign stability across both regimes (Intra-turn static vs Multi-turn conversational)
- RQ2 Transition classification with orthogonal diagnostic labels across predefined epsilon sweep
- RQ3 Magnitude vs sign-jitter relationship across predefined magnitude bins
- RQ4 & RQ5 Deadband sweep, independent dimensions of retention and suppression without composite scoring
- RQ6 Short-timescale (T < 12) vs conversational timescale exposure dynamics
- RQ7 Candidate temporal policies (P0 Raw, P1 Deadband, P2 Persistence, P3 Hysteresis, P4 Exposure-Annotated)
- RQ8 Temporal lag and distortion metrics across policies
- RQ9 Behavioral consequences (Part 1: 358 matched collapse pairs at T=12; Part 2: Multi-exposure trajectory replay)
- RQ10 Architectural invariants (INV-1 to INV-9) and failure modes (FM-T01 to FM-T12)
- ADR readiness state (READY FOR ADR DRAFT UPDATE while Production Architecture Gate remains STRICTLY LOCKED)
"""

import hashlib
import json
import math
from pathlib import Path
import pytest

REPO_ROOT = Path(__file__).resolve().parent.parent.parent
RESULTS_DIR = REPO_ROOT / "tests" / "evaluation_phase22" / "results" / "h1_r3_temporal_stability"
FIXTURES_DIR = REPO_ROOT / "tests" / "evaluation_phase22" / "fixtures"

RESULTS_FILE = RESULTS_DIR / "r3_temporal_stability_results.json"
MANIFEST_FILE = FIXTURES_DIR / "manifest_h1_r3_temporal_stability.json"


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


def compute_sha256(path: Path) -> str:
    with open(path, "rb") as f:
        return hashlib.sha256(f.read()).hexdigest()


# ---------------------------------------------------------------------------
# Test 01: Manifest and Results Integrity
# ---------------------------------------------------------------------------

def test_01_manifest_and_results_integrity(manifest_data: dict):
    assert manifest_data["manifest_version"] == "1.0"
    assert manifest_data["study_name"] == "Phase 22 H1 R3 Temporal Stability Feasibility Study"

    file_entry = manifest_data["files"]["r3_temporal_stability_results.json"]
    expected_sha = file_entry["sha256"]
    actual_sha = compute_sha256(RESULTS_FILE)
    assert actual_sha == expected_sha, f"SHA-256 mismatch: expected {expected_sha}, got {actual_sha}"
    assert file_entry["size_bytes"] == RESULTS_FILE.stat().st_size


# ---------------------------------------------------------------------------
# Test 02: Governance Invariants
# ---------------------------------------------------------------------------

def test_02_governance_invariants(results_data: dict, manifest_data: dict):
    gov = results_data["metadata"]["governance"]
    assert gov["phase_22_h1"] == "INCONCLUSIVE"
    assert gov["gate_2"] == "BLOCKED"
    assert gov["protocol_v1_5"] == "NOT AUTHORIZED"
    assert gov["architecture_gate"] == "STRICTLY LOCKED"
    assert gov["src_core_mutations"] == 0
    assert gov["genesis_profile"] == "PRESERVED_BIT_EXACT"
    assert "Delta_HM = 0.0685 < 0.1500" in gov["gate_2_metric"]
    assert "S_M = 0.5792" in gov["gate_2_metric"]
    assert "S_H = 0.6477" in gov["gate_2_metric"]

    # Manifest governance sync
    m_gov = manifest_data["governance_invariants"]
    assert m_gov["phase_22_h1"] == "INCONCLUSIVE"
    assert m_gov["gate_2"] == "BLOCKED"
    assert m_gov["protocol_v1_5"] == "NOT AUTHORIZED"
    assert m_gov["architecture_gate"] == "STRICTLY LOCKED"
    assert m_gov["genesis_profile"] == "PRESERVED_BIT_EXACT"
    assert m_gov["src_core_mutations"] == 0

    # Genesis profile on disk
    profile_path = REPO_ROOT / "data" / "profile.json"
    if profile_path.exists():
        with open(profile_path, "r", encoding="utf-8") as f:
            profile = json.load(f)
            assert profile.get("is_onboarded") is False


# ---------------------------------------------------------------------------
# Test 03: Raw Sign Mathematics & Ternary Discretization
# ---------------------------------------------------------------------------

def test_03_raw_sign_mathematics():
    def ternary_sign(val: float, eps: float = 0.0) -> int:
        if val > eps:
            return 1
        elif val < -eps:
            return -1
        return 0

    # Strict mathematical identity checks
    assert ternary_sign(0.05) == 1
    assert ternary_sign(-0.05) == -1
    assert ternary_sign(0.0) == 0
    assert ternary_sign(0.005, eps=0.01) == 0
    assert ternary_sign(-0.005, eps=0.01) == 0
    assert ternary_sign(0.015, eps=0.01) == 1
    assert ternary_sign(-0.015, eps=0.01) == -1


# ---------------------------------------------------------------------------
# Test 04: RQ1 Temporal Sign Stability Across Dual Regimes
# ---------------------------------------------------------------------------

def test_04_rq1_temporal_sign_stability_dual_regime(results_data: dict):
    rq1 = results_data["rq1_temporal_sign_stability"]

    # Regime 1: Intra-Turn Static Exposure
    r1 = rq1["regime_1_intra_turn_static"]
    r1_comps = r1["components"]
    for c_name in ["Pleasure", "Arousal", "Dominance"]:
        comp = r1_comps[c_name]
        assert comp["total_transitions"] == 0, f"Expected 0 transitions in Regime 1 for {c_name}"
        assert comp["transition_rate_per_step"] == 0.0
        assert comp["mean_consecutive_run_length"] == 25.0
    assert "100% stable within single-turn exposure" in r1["finding"]

    # Regime 2: Multi-Turn Conversational Stream
    r2 = rq1["regime_2_conversational_stream"]
    r2_comps = r2["components"]
    assert r2_comps["Pleasure"]["total_transitions"] == 89
    assert r2_comps["Arousal"]["total_transitions"] == 115
    assert r2_comps["Dominance"]["total_transitions"] == 105

    vec = r2["vector_level"]
    assert vec["total_vector_transitions"] == 162
    assert 0.14 <= vec["vector_transition_rate_per_step"] <= 0.16
    assert vec["unique_states_observed"] == 9
    assert len(vec["top_states"]) == 5
    # Dominant state is (1, -1, 1)
    assert vec["top_states"][0][0] == "(1, -1, 1)"


# ---------------------------------------------------------------------------
# Test 05: RQ2 Transition Classification Across Predefined Sweep
# ---------------------------------------------------------------------------

def test_05_rq2_transition_classification_orthogonal_labels(results_data: dict):
    rq2 = results_data["rq2_transition_classification"]
    assert rq2["total_transitions_analyzed"] == 309

    sweep = rq2["epsilon_sweep_classifications"]
    expected_epsilons = ["0.001", "0.0025", "0.005", "0.01", "0.02", "0.035", "0.05"]
    assert list(sweep.keys()) == expected_epsilons

    # Verify orthogonal diagnostic property: Type A and Type B vary with epsilon
    assert sweep["0.001"]["type_a_genuine_reversal_count"] == 190
    assert sweep["0.001"]["type_b_near_zero_crossing_count"] == 119
    assert sweep["0.01"]["type_a_genuine_reversal_count"] == 42
    assert sweep["0.01"]["type_b_near_zero_crossing_count"] == 267
    assert sweep["0.05"]["type_a_genuine_reversal_count"] == 15
    assert sweep["0.05"]["type_b_near_zero_crossing_count"] == 294

    # Type D persistence is independent of epsilon definition
    for eps_key in expected_epsilons:
        res = sweep[eps_key]
        assert res["type_d_sustained_k2_count"] == 301
        assert res["type_d_sustained_k3_count"] == 297
        # Verify orthogonal overlap reports non-empty joint states
        assert res["orthogonal_overlap"]["A_and_D_k2"] > 0
        assert res["orthogonal_overlap"]["B_and_D_k2"] > 0

    assert "orthogonal diagnostic labels" in rq2["methodological_principle"]


# ---------------------------------------------------------------------------
# Test 06: RQ3 Magnitude vs. Sign Instability Across Predefined Bins
# ---------------------------------------------------------------------------

def test_06_rq3_magnitude_instability_bins(results_data: dict):
    rq3 = results_data["rq3_magnitude_instability_relationship"]
    bins = rq3["predefined_bins_evaluation"]

    # Verify 6 predefined bins
    assert "[0, .005)" in bins
    assert "[.005, .01)" in bins
    assert "[.01, .02)" in bins
    assert "[.02, .05)" in bins
    assert "[.05, .10)" in bins
    assert "[.10, inf)" in bins

    # Transitions concentrated below 0.01
    assert bins["[0, .005)"]["transitions_at_magnitude"] == 212
    assert bins["[.005, .01)"]["transitions_at_magnitude"] == 49
    total_below_01 = bins["[0, .005)"]["transitions_at_magnitude"] + bins["[.005, .01)"]["transitions_at_magnitude"]
    assert total_below_01 == 261
    assert abs(rq3["concentration_below_0_01"]["percentage_of_all_transitions"] - (261 / 309)) < 1e-4

    # High magnitude stability (0 transitions at |r| >= 0.10)
    assert bins["[.10, inf)"]["transitions_at_magnitude"] == 0
    assert bins["[.10, inf)"]["conditional_transition_rate"] == 0.0


# ---------------------------------------------------------------------------
# Test 07: RQ4 & RQ5 Deadband Sweep and Independent Retention
# ---------------------------------------------------------------------------

def test_07_rq4_rq5_deadband_sweep_and_retention(results_data: dict):
    rq4_rq5 = results_data["rq4_rq5_deadband_and_retention"]
    assert rq4_rq5["raw_baseline_transitions"] == 309

    metrics = rq4_rq5["sweep_metrics"]
    assert "0.01" in metrics
    p1_metrics = metrics["0.01"]

    # At primary epsilon = 0.010
    assert p1_metrics["deadband_transitions"] == 131
    assert abs(p1_metrics["stability_gain_pct"] - 0.57605) < 1e-4
    assert p1_metrics["reversibility_preservation_rate"] == 1.0  # 100% preservation of genuine reversals
    assert p1_metrics["reversibility_total_events"] == 42

    # Verify independent dimensions statement
    assert "reported independently without arbitrary composite scoring" in rq4_rq5["independent_dimensions_statement"]


# ---------------------------------------------------------------------------
# Test 08: RQ6 Timescale Exposure Analysis
# ---------------------------------------------------------------------------

def test_08_rq6_timescale_exposure_analysis(results_data: dict):
    rq6 = results_data["rq6_timescale_exposure_analysis"]
    grid = rq6["exposure_grid_evaluation"]

    for tick_str in ["1", "2", "4", "8", "12", "16", "25"]:
        assert tick_str in grid
        entry = grid[tick_str]
        assert entry["intra_turn_transitions"] == 0
        assert entry["intra_turn_transition_rate"] == 0.0

    assert "Under constant stimulus presentation, zero sign transitions occur" in rq6["timescale_finding"]
    assert "at T < 12, directional signs retain 66-968 Medium-High collapse pairs" in rq6["timescale_finding"]


# ---------------------------------------------------------------------------
# Test 09: RQ7 Candidate Temporal Policies
# ---------------------------------------------------------------------------

def test_09_rq7_candidate_temporal_policies(results_data: dict):
    rq7 = results_data["rq7_candidate_temporal_policies"]

    # P0 Raw R3
    assert rq7["P0_Raw_R3"]["transitions"] == 309
    assert rq7["P0_Raw_R3"]["stability_gain_pct"] == 0.0

    # P1 Static Deadband (eps = 0.010)
    assert rq7["P1_Static_Deadband_0_01"]["transitions"] == 131
    assert abs(rq7["P1_Static_Deadband_0_01"]["stability_gain_pct"] - 0.57605) < 1e-4

    # P2 Persistence
    assert rq7["P2_Persistence_k2"]["transitions"] == 296
    assert rq7["P2_Persistence_k3"]["transitions"] == 288

    # P3 Hysteresis
    assert rq7["P3_Hysteresis_0_02_0_01"]["transitions"] == 73
    assert rq7["P3_Hysteresis_0_01_0_005"]["transitions"] == 123

    # P4 Exposure-Annotated Raw R3
    p4 = rq7["P4_Exposure_Annotated_R3"]
    assert p4["transitions"] == 309
    assert "w_exp(T) = min(1.0, T / 12.0)" in p4["operational_character"]


# ---------------------------------------------------------------------------
# Test 10: RQ8 Temporal Lag and Distortion
# ---------------------------------------------------------------------------

def test_10_rq8_temporal_lag_and_distortion(results_data: dict):
    rq8 = results_data["rq8_temporal_lag_and_distortion"]

    p1 = rq8["P1_Deadband_0_01"]
    assert p1["total_reversals_evaluated"] == 309
    assert p1["delayed_reversals_count"] == 218
    assert p1["missed_reversals_count"] == 21

    p2 = rq8["P2_Persistence_k2"]
    assert p2["median_lag_ticks"] == 1.0
    assert p2["delayed_reversals_count"] == 302
    assert p2["missed_reversals_count"] == 1

    p3 = rq8["P3_Hysteresis_0_02_0_01"]
    assert p3["delayed_reversals_count"] == 70
    assert p3["missed_reversals_count"] == 186


# ---------------------------------------------------------------------------
# Test 11: RQ9 Behavioral Consequences (Two-Part Replay)
# ---------------------------------------------------------------------------

def test_11_rq9_behavioral_consequences_two_part_replay(results_data: dict):
    rq9 = results_data["rq9_behavioral_consequences"]

    # Part 1: T=12 Matched Collapse Pairs Replay (358 pairs)
    part1 = rq9["part_1_t12_collapse_pairs_replay"]
    assert part1["P0_Raw"]["total_pairs"] == 358
    assert part1["P0_Raw"]["d_pol_count"] == 286
    assert abs(part1["P0_Raw"]["d_pol"] - 0.79888) < 1e-4

    assert part1["P1_Deadband_0_01"]["d_pol_count"] == 286
    assert abs(part1["P1_Deadband_0_01"]["d_pol"] - 0.79888) < 1e-4

    assert part1["P4_Exposure_Annotated_T12"]["d_pol_count"] == 286
    assert abs(part1["P4_Exposure_Annotated_T12"]["d_pol"] - 0.79888) < 1e-4
    assert part1["P4_Exposure_Annotated_T12"]["mean_d_js"] == part1["P0_Raw"]["mean_d_js"]

    # Part 2: Multi-Exposure Trajectory Replay across T in [1, 25]
    part2 = rq9["part_2_multi_exposure_trajectory_replay"]
    assert "1" in part2
    assert "12" in part2
    assert "25" in part2

    # At T=1, strong damping of directional influence
    assert abs(part2["1"]["w_exp"] - (1.0 / 12.0)) < 1e-4
    assert part2["1"]["damping_effect_pct"] > 0.99

    # At T=12, w_exp reaches 1.0 and damping effect is 0.0%
    assert part2["12"]["w_exp"] == 1.0
    assert part2["12"]["damping_effect_pct"] == 0.0
    assert part2["12"]["mean_d_js_p4_vs_scalar_c0"] == part2["12"]["mean_d_js_p0_vs_scalar_c0"]

    # At T=25, w_exp remains 1.0
    assert part2["25"]["w_exp"] == 1.0
    assert part2["25"]["damping_effect_pct"] == 0.0

    assert "Part 1 evaluates 358 matched collapse pairs at T=12" in rq9["methodological_boundary"]
    assert "No claims of end-to-end SLM text generation are made" in rq9["methodological_boundary"]


# ---------------------------------------------------------------------------
# Test 12: RQ10 Architectural Invariants & Failure Modes
# ---------------------------------------------------------------------------

def test_12_rq10_invariants_and_failure_modes(results_data: dict):
    rq10 = results_data["rq10_invariants_failure_modes_adr"]

    invariants = rq10["invariants_audit"]
    assert len(invariants) == 9
    for inv in invariants:
        assert inv["status"] == "PRESERVED_BIT_EXACT"

    failure_modes = rq10["failure_modes"]
    assert len(failure_modes) == 12
    fm_ids = {fm["id"] for fm in failure_modes}
    assert fm_ids == {f"FM-T{i:02d}" for i in range(1, 13)}


# ---------------------------------------------------------------------------
# Test 13: ADR Readiness & Architecture Gate Locking
# ---------------------------------------------------------------------------

def test_13_adr_readiness_and_gate_locking(results_data: dict, manifest_data: dict):
    rq10 = results_data["rq10_invariants_failure_modes_adr"]
    adr = rq10["adr_readiness"]

    assert adr["status"] == "READY_FOR_ADR_DRAFT_UPDATE"
    assert manifest_data["adr_readiness_state"] == "READY_FOR_ADR_DRAFT_UPDATE"
    assert adr["gate_status"] == "STRICTLY LOCKED"

    op_meaning = adr["operational_meaning"]
    assert "READY FOR ADR DRAFT UPDATE" in op_meaning
    assert "does NOT authorize Architecture Gate ratification" in op_meaning
    assert "The Production Architecture Gate remains STRICTLY LOCKED" in op_meaning
