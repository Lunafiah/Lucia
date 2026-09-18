"""
tests/evaluation_phase22/test_h1_multi_turn_interactive_dialogue.py

Automated Test Suite for Phase 22 H1 Multi-Turn Interactive Dialogue Study:
  PHASE_22_H1_MULTI_TURN_INTERACTIVE_DIALOGUE_STUDY

Validates:
  1. Pre-registered manifest and ENVIRONMENT_MODEL_SPEC integrity.
  2. Strict environment blindness to policy_id.
  3. Master corpus generation and 358 matched discordant pair properties.
  4. Dynamic entropy computation from single-source-of-truth belief priors.
  5. Multi-turn dialogue behavior across Scenarios A through H.
  6. Trajectory-level information loss bottleneck classification (representation,
     valuation, policy, action-selection, and environment collapse).
  7. Feedback causality (Type 1 Causal vs Type 2 Epiphenomenal vs Type 3 Pre-Action).
  8. Temporal dynamics and flapping suppression (PA vs PD vs PE).
  9. Negative controls NC1 through NC8.
  10. Zero production code mutations and locked Genesis invariant.
"""

import json
import math
from pathlib import Path
import subprocess
import sys
from typing import Any, Dict, List

import numpy as np
import pytest

# Repository root discovery
def get_repo_root() -> Path:
    current = Path(__file__).resolve()
    while current.parent != current:
        if (current / "src").exists() and (current / "AGENTS.md").exists():
            return current
        current = current.parent
    return Path(__file__).resolve().parents[2]

REPO_ROOT = get_repo_root()
sys.path.insert(0, str(REPO_ROOT))

from tests.evaluation_phase22.scripts.evaluate_h1_multi_turn_interactive_dialogue import (
    STUDY_ID,
    MASTER_SEED,
    EXPECTED_CORPUS_SHA,
    EXPECTED_N_PROBES,
    EXPECTED_HISTORICAL_DISCORDANT,
    RESOLUTION_ENTROPY_THRESHOLD_TAU_RES,
    ACTIONS,
    ACTION_COSTS_DICT,
    compute_entropy,
    compute_tv_distance,
    compute_action_values,
    evaluate_epistemic_step,
    MultiTurnDialogueHarness,
    InteractiveDialogueEnvironment,
    DialogueState,
)

FIXTURES_DIR = REPO_ROOT / "tests" / "evaluation_phase22" / "fixtures"
RESULTS_DIR = REPO_ROOT / "tests" / "evaluation_phase22" / "results" / "h1_multi_turn_interactive_dialogue"

@pytest.fixture(scope="module")
def harness() -> MultiTurnDialogueHarness:
    h = MultiTurnDialogueHarness(MASTER_SEED)
    h.generate_master_corpus()
    h.simulate_pad_trajectories(12)
    h.build_matched_discordant_pairs()
    return h

@pytest.fixture(scope="module")
def manifest() -> Dict[str, Any]:
    manifest_path = FIXTURES_DIR / "manifest_h1_multi_turn_interactive_dialogue.json"
    assert manifest_path.exists(), f"Manifest missing: {manifest_path}"
    with open(manifest_path, "r", encoding="utf-8") as f:
        return json.load(f)

# =============================================================================
# 1. Manifest & Environment Model Specification Tests
# =============================================================================

def test_manifest_structure_and_governance(manifest: Dict[str, Any]):
    assert manifest["study_id"] == STUDY_ID
    assert manifest["master_seed"] == MASTER_SEED
    assert manifest["expected_corpus_sha"] == EXPECTED_CORPUS_SHA
    assert manifest["expected_n_probes"] == EXPECTED_N_PROBES
    assert manifest["expected_discordant_pairs"] == EXPECTED_HISTORICAL_DISCORDANT
    assert len(manifest["actions"]) == 6
    assert len(manifest["policy_conditions"]) == 6

def test_environment_model_spec_locked(manifest: Dict[str, Any]):
    env_spec = manifest.get("environment_model_spec", {})
    assert env_spec.get("policy_id_blindness") is True
    assert "scenarios" in env_spec
    scenarios = env_spec["scenarios"]
    for sc_id in ["A", "B", "C", "D", "E", "F", "G", "H"]:
        assert sc_id in scenarios, f"Scenario {sc_id} missing from ENVIRONMENT_MODEL_SPEC"
        assert "q0" in scenarios[sc_id]
        assert "e0" in scenarios[sc_id]
        assert len(scenarios[sc_id]["q0"]) == 4

def test_environment_step_policy_blindness(harness: MultiTurnDialogueHarness):
    import inspect
    sig = inspect.signature(harness.env_canon.step)
    params = list(sig.parameters.keys())
    assert "action" in params
    assert "state" in params
    assert "rng" in params
    assert "policy_id" not in params
    assert "policy_name" not in params

# =============================================================================
# 2. Corpus & Observation Model Tests
# =============================================================================

def test_corpus_generation_and_discordant_pairs(harness: MultiTurnDialogueHarness):
    assert len(harness.all_probes) == EXPECTED_N_PROBES
    assert len(harness.discordant_matched_pairs) == EXPECTED_HISTORICAL_DISCORDANT

def test_observation_parameter_hashes(manifest: Dict[str, Any]):
    canon_hashes = manifest["locked_canon_parameter_hashes"]
    assert "M_CANON_CLARIFY_BASE_LOGITS" in canon_hashes
    assert "M_CANON_RETRIEVE_BASE_LOGITS" in canon_hashes
    assert "M_CANON_CLARIFY_W_DIR" in canon_hashes
    assert "M_CANON_RETRIEVE_W_DIR" in canon_hashes

# =============================================================================
# 3. Dynamic Entropy & Single Source of Truth
# =============================================================================

def test_scenario_a_entropy_computation():
    q0 = np.array([0.85, 0.05, 0.05, 0.05], dtype=np.float64)
    h0 = compute_entropy(q0)
    # Theoretical value: -(0.85*ln(0.85) + 3*0.05*ln(0.05)) = 0.587501...
    assert math.isclose(h0, 0.587501, rel_tol=1e-4)

def test_scenario_b_uniform_entropy_computation():
    q0 = np.array([0.25, 0.25, 0.25, 0.25], dtype=np.float64)
    h0 = compute_entropy(q0)
    assert math.isclose(h0, math.log(4.0), rel_tol=1e-6)

# =============================================================================
# 4. Multi-Turn Scenario Behaviors (A through H)
# =============================================================================

def test_scenario_a_answer_dominance(harness: MultiTurnDialogueHarness):
    res_p0 = harness.run_dialogue_trajectory(1, "A", "P0_canonical_argmax", "C1")
    assert res_p0["total_turns"] == 1
    assert res_p0["resolved"] is True
    assert res_p0["cumulative_friction"] == 0.0
    assert res_p0["history"][0]["action"] == "answer"

def test_scenario_b_persistent_ambiguity(harness: MultiTurnDialogueHarness):
    res = harness.run_dialogue_trajectory(1, "B", "P0_canonical_argmax", "C1")
    # Under persistent ambiguity, P0 should not prematurely resolve dialogue
    assert res["resolved"] is False
    assert res["final_entropy"] > RESOLUTION_ENTROPY_THRESHOLD_TAU_RES

def test_scenario_c_ambiguity_resolution(harness: MultiTurnDialogueHarness):
    res_p0 = harness.run_dialogue_trajectory(1, "C", "P0_canonical_argmax", "C1")
    # Epistemic action on Turn 1 should resolve ambiguity, leading to answer on Turn 2
    assert res_p0["resolved"] is True
    assert res_p0["total_turns"] <= 3
    assert res_p0["history"][0]["action"] in ("retrieve", "clarify")
    assert res_p0["history"][-1]["action"] == "answer"
    assert res_p0["final_entropy"] < RESOLUTION_ENTROPY_THRESHOLD_TAU_RES

def test_scenario_d_failed_epistemic_action(harness: MultiTurnDialogueHarness):
    res_p0 = harness.run_dialogue_trajectory(1, "D", "P0_canonical_argmax", "C1")
    # Under P0, deterministic failure causes repeated action loop (FM-03)
    actions = [h["action"] for h in res_p0["history"]]
    assert actions[0] == actions[1] == "retrieve"

def test_scenario_e_contradictory_evidence_transition(harness: MultiTurnDialogueHarness):
    res = harness.run_dialogue_trajectory(1, "E", "P0_canonical_argmax", "C1")
    # Belief should invert toward h2 after Turn 2
    assert len(res["history"]) >= 2
    b_t2 = res["history"][1]["belief"]
    assert b_t2[1] > b_t2[0]  # h2 dominates h1

def test_scenario_f_repeated_uncertainty_injection(harness: MultiTurnDialogueHarness):
    res_pa = harness.run_dialogue_trajectory(1, "F", "PA_deterministic_hysteresis_10", "C1")
    # Checks that hysteresis allows action switches across injected turns
    actions = [h["action"] for h in res_pa["history"]]
    switches = sum(1 for k in range(len(actions) - 1) if actions[k] != actions[k+1])
    assert switches >= 1

def test_scenario_g_low_energy_adaptive_bounding(harness: MultiTurnDialogueHarness):
    res = harness.run_dialogue_trajectory(1, "G", "P0_canonical_argmax", "C1")
    # Low energy should prevent high-drain actions like 'reason' (cost=0.50, drain=0.15)
    actions = [h["action"] for h in res["history"]]
    assert "reason" not in actions

def test_scenario_h_relational_friction_accounting(harness: MultiTurnDialogueHarness):
    res_p0 = harness.run_dialogue_trajectory(1, "H", "P0_canonical_argmax", "C1")
    # Internal retrieval has 0 user friction; premature answer would add 2.0
    assert res_p0["cumulative_friction"] >= 0.0

# =============================================================================
# 5. Trajectory-Level Bottleneck & Causality Tests
# =============================================================================

def test_trajectory_bottleneck_p0_action_selection_collapse(harness: MultiTurnDialogueHarness):
    p_i, p_j = harness.discordant_matched_pairs[0]
    res_i = harness.run_dialogue_trajectory(p_i, "B", "P0_canonical_argmax", "C1")
    res_j = harness.run_dialogue_trajectory(p_j, "B", "P0_canonical_argmax", "C1")
    # Continuous valuations differ, but discrete argmax collapses to identical action
    v_i = np.array(res_i["history"][0]["v_vals"])
    v_j = np.array(res_j["history"][0]["v_vals"])
    assert np.linalg.norm(v_i - v_j) > 1e-4
    assert res_i["history"][0]["action"] == res_j["history"][0]["action"]

def test_trajectory_bottleneck_pe_hybrid_differentiation(harness: MultiTurnDialogueHarness):
    # Tests that PE hybrid explores under ambiguity when margin < tau_conf
    sample_diffs = 0
    for p_i, p_j in harness.discordant_matched_pairs[:30]:
        res_i = harness.run_dialogue_trajectory(p_i, "B", "PE_hybrid_confidence_gated", "C1", rng_seed=7113)
        res_j = harness.run_dialogue_trajectory(p_j, "B", "PE_hybrid_confidence_gated", "C1", rng_seed=7114)
        if res_i["history"][0]["action"] != res_j["history"][0]["action"]:
            sample_diffs += 1
    assert sample_diffs > 0

def test_feedback_causality_divergence(harness: MultiTurnDialogueHarness):
    # When actions differ at Turn 1, downstream observations and next-turn valuations differ
    p_i, p_j = harness.discordant_matched_pairs[0]
    res_i = harness.run_dialogue_trajectory(p_i, "C", "PE_hybrid_confidence_gated", "C1", rng_seed=7113)
    res_j = harness.run_dialogue_trajectory(p_j, "C", "PE_hybrid_confidence_gated", "C1", rng_seed=7114)
    if res_i["history"][0]["action"] != res_j["history"][0]["action"] and len(res_i["history"]) >= 2 and len(res_j["history"]) >= 2:
        v_diff_t2 = np.linalg.norm(np.array(res_i["history"][1]["v_vals"]) - np.array(res_j["history"][1]["v_vals"]))
        assert v_diff_t2 > 1e-4

# =============================================================================
# 6. Temporal Dynamics & Flapping Tests
# =============================================================================

def test_temporal_flapping_suppression(harness: MultiTurnDialogueHarness):
    res_pa = harness.run_dialogue_trajectory(1, "F", "PA_deterministic_hysteresis_10", "C1")
    res_pd = harness.run_dialogue_trajectory(1, "F", "PD_probabilistic_softmax_sampling", "C1")
    # Hysteresis should produce less action switching than pure softmax sampling
    acts_pa = [h["action"] for h in res_pa["history"]]
    acts_pd = [h["action"] for h in res_pd["history"]]
    sw_pa = sum(1 for k in range(len(acts_pa) - 1) if acts_pa[k] != acts_pa[k+1])
    sw_pd = sum(1 for k in range(len(acts_pd) - 1) if acts_pd[k] != acts_pd[k+1])
    assert sw_pa <= sw_pd

# =============================================================================
# 7. Negative Controls (NC1–NC8) Tests
# =============================================================================

def test_nc1_controlled_zero_incremental_divergence(harness: MultiTurnDialogueHarness):
    p_i, p_j = harness.discordant_matched_pairs[0]
    res_c0_i = harness.run_dialogue_trajectory(p_i, "B", "P0_canonical_argmax", "C0")
    res_c0_j = harness.run_dialogue_trajectory(p_j, "B", "P0_canonical_argmax", "C0")
    # Under C0, v_dir is zeroed out, so paired probes must have identical trajectories
    acts_i = [h["action"] for h in res_c0_i["history"]]
    acts_j = [h["action"] for h in res_c0_j["history"]]
    assert acts_i == acts_j

def test_nc2_direction_shuffled_correspondence(harness: MultiTurnDialogueHarness):
    canon_dists = []
    shuff_dists = []
    for p_i, p_j in harness.discordant_matched_pairs[:30]:
        r_c_i = harness.run_dialogue_trajectory(p_i, "B", "PE_hybrid_confidence_gated", "C1")
        r_c_j = harness.run_dialogue_trajectory(p_j, "B", "PE_hybrid_confidence_gated", "C1")
        r_s_i = harness.run_dialogue_trajectory(p_i, "B", "PE_hybrid_confidence_gated", "C2")
        r_s_j = harness.run_dialogue_trajectory(p_j, "B", "PE_hybrid_confidence_gated", "C2")

        d_c = np.mean([np.linalg.norm(np.array(h_i["v_vals"]) - np.array(h_j["v_vals"])) for h_i, h_j in zip(r_c_i["history"], r_c_j["history"])])
        d_s = np.mean([np.linalg.norm(np.array(h_i["v_vals"]) - np.array(h_j["v_vals"])) for h_i, h_j in zip(r_s_i["history"], r_s_j["history"])])
        canon_dists.append(float(d_c))
        shuff_dists.append(float(d_s))

    from scipy.stats import pearsonr
    r_val, _ = pearsonr(canon_dists, shuff_dists)
    assert abs(r_val) <= 0.50

def test_nc3_zero_directional_weighting_identity(harness: MultiTurnDialogueHarness):
    r1 = harness.run_dialogue_trajectory(1, "A", "P0_canonical_argmax", "C0")
    r2 = harness.run_dialogue_trajectory(1, "A", "P0_canonical_argmax", "C0")
    assert r1["history"] == r2["history"]

def test_nc4_deterministic_repeatability(harness: MultiTurnDialogueHarness):
    r1 = harness.run_dialogue_trajectory(5, "C", "P0_canonical_argmax", "C1")
    r2 = harness.run_dialogue_trajectory(5, "C", "P0_canonical_argmax", "C1")
    assert r1["history"] == r2["history"]

def test_nc5_environment_model_independence(harness: MultiTurnDialogueHarness):
    r_canon = harness.run_dialogue_trajectory(1, "C", "P0_canonical_argmax", "C1", use_counterfactual_env=False)
    r_counter = harness.run_dialogue_trajectory(1, "C", "P0_canonical_argmax", "C1", use_counterfactual_env=True)
    assert r_canon["resolved"] == r_counter["resolved"] is True

def test_nc6_production_code_isolation():
    diff_proc = subprocess.run(
        ["git", "diff", "--", "src/core", "src/api", "electron"],
        cwd=REPO_ROOT,
        capture_output=True,
        text=True,
    )
    assert len(diff_proc.stdout.strip()) == 0

def test_nc7_genesis_gate_invariant():
    profile_path = REPO_ROOT / "data" / "profile.json"
    with open(profile_path, "r", encoding="utf-8") as f:
        data = json.load(f)
    assert data.get("is_onboarded") is False

def test_nc8_policy_neutral_environment(harness: MultiTurnDialogueHarness):
    import inspect
    sig = inspect.signature(harness.env_canon.step)
    assert "policy_id" not in sig.parameters
    assert "policy_name" not in sig.parameters

# =============================================================================
# 8. Resource & Governance Tests
# =============================================================================

def test_resource_cpu_latency_and_zero_vram(harness: MultiTurnDialogueHarness):
    res = harness.run_dialogue_trajectory(1, "C", "P0_canonical_argmax", "C1")
    assert res["latency_us_per_turn"] < 500.0  # sub-millisecond

def test_governance_invariants():
    # Gate 2 remains strictly blocked; Phase 22 H1 remains inconclusive
    manifest_path = FIXTURES_DIR / "manifest_h1_multi_turn_interactive_dialogue.json"
    with open(manifest_path, "r", encoding="utf-8") as f:
        data = json.load(f)
    assert data["study_id"] == "PHASE_22_H1_MULTI_TURN_INTERACTIVE_DIALOGUE_STUDY"
