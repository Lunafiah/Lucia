"""
tests/evaluation/phase26/test_replica_ensemble_manager.py

Unit and integration tests for ReplicaEnsembleManager (P26 Blocker 2):
- Creation of N isolated research replicas with independent subsystems
- Strict isolation verification (no aliasing, no shared tensor mutation bleed)
- Synchronized multi-turn virtual clock stepping
- Matched-exposure bookkeeping ledger completeness
- ExposureEquivalenceValidator detection of mismatches (text, vector, timing, count)
- CRN configuration logging and deterministic alignment
- Cryptographic state fingerprinting and divergence onset tracking
- Deterministic replay reproducibility
- Teardown and reset hygiene
"""

import numpy as np
import pytest

from tests.evaluation.phase26.replica_ensemble_manager import (
    EquivalenceValidationReport,
    ExposureMismatchError,
    ExposureRecord,
    InputEvent,
    IsolationAuditResult,
    ReplicaConfig,
    ReplicaEnsembleManager,
    ResearchReplica,
)


@pytest.fixture
def manager() -> ReplicaEnsembleManager:
    """Fixture providing a fresh ReplicaEnsembleManager."""
    mgr = ReplicaEnsembleManager(shared_sdm_topology_seed=42)
    yield mgr
    mgr.teardown()


def test_replica_creation_and_isolation(manager: ReplicaEnsembleManager):
    """
    Verification that N isolated research replicas can be instantiated with
    distinct replica IDs and completely separate internal components.
    """
    configs = [
        ReplicaConfig(replica_id="replica_A", seed=1001),
        ReplicaConfig(replica_id="replica_B", seed=2002),
        ReplicaConfig(replica_id="replica_C", seed=3003),
    ]
    ensemble = manager.create_ensemble(configs)

    assert manager.replica_count == 3
    assert manager.replica_ids == ["replica_A", "replica_B", "replica_C"]

    rep_a = ensemble["replica_A"]
    rep_b = ensemble["replica_B"]
    rep_c = ensemble["replica_C"]

    # Verify distinct object identities across limbic, memory, clock, and LLM
    assert rep_a.emotion_core is not rep_b.emotion_core
    assert rep_b.emotion_core is not rep_c.emotion_core
    assert rep_a.clock is not rep_b.clock
    assert rep_a.sdm is not rep_b.sdm
    assert rep_a.llm is not rep_b.llm

    # Verify distinct underlying numpy memory buffers
    assert rep_a.emotion_core._h_fast is not rep_b.emotion_core._h_fast
    assert rep_a.emotion_core._s_slow is not rep_b.emotion_core._s_slow
    assert rep_a.sdm._accumulator is not rep_b.sdm._accumulator

    # Verify active isolation audit passes
    iso_result = manager.verify_isolation()
    assert iso_result.is_isolated is True
    assert iso_result.num_replicas_checked == 3
    assert len(iso_result.aliased_components) == 0
    assert iso_result.mutation_bleed_detected is False


def test_mutation_isolation_guarantee(manager: ReplicaEnsembleManager):
    """
    Verification that directly mutating limbic tensors or writing SDM traces
    in Replica A causes ZERO mutation bleed into Replica B.
    """
    configs = [
        ReplicaConfig(replica_id="rep_alpha", seed=101),
        ReplicaConfig(replica_id="rep_beta", seed=102),
    ]
    ensemble = manager.create_ensemble(configs)
    rep_a = ensemble["rep_alpha"]
    rep_b = ensemble["rep_beta"]

    # Initial states
    initial_b_fast = np.copy(rep_b.emotion_core._h_fast)
    initial_b_accum = np.copy(rep_b.sdm._accumulator)
    assert rep_b.sdm.trace_count == 0

    # 1. Mutate Replica A's limbic state
    rep_a.emotion_core._h_fast += 1.25
    assert not np.array_equal(rep_a.emotion_core._h_fast, initial_b_fast)
    # Replica B must remain untouched
    assert np.array_equal(rep_b.emotion_core._h_fast, initial_b_fast)

    # 2. Write memory trace to Replica A's SDM
    addr = np.ones(rep_a.sdm._D, dtype=np.uint8)
    content = np.ones(rep_a.sdm._M, dtype=np.float32)
    rep_a.sdm.write(addr, content)

    assert rep_a.sdm.trace_count == 1
    # Replica B SDM must remain completely empty with identical accumulator
    assert rep_b.sdm.trace_count == 0
    assert np.array_equal(rep_b.sdm._accumulator, initial_b_accum)


def test_synchronized_multi_turn_rollout(manager: ReplicaEnsembleManager):
    """
    Verification of synchronized multi-turn stepping under identical virtual clock timing.
    """
    configs = [
        ReplicaConfig(replica_id="rep_1", seed=501),
        ReplicaConfig(replica_id="rep_2", seed=502),
    ]
    manager.create_ensemble(configs)

    # Turn 1: Stimulus pulse
    stim1 = np.zeros(16, dtype=np.float64)
    stim1[0] = 0.40  # Valence
    event1 = InputEvent(
        input_text="Should we inspect Deep-sea hydrothermal ecosystems or Medieval maritime cartography first?",
        stimulus_vector=stim1,
        metadata={"domain": "INFO_FORAGING"},
    )
    res_turn1 = manager.step_identical_turn(event1, dt_sec=0.200, sub_steps=2)

    assert manager.current_turn == 1
    assert res_turn1["rep_1"].virtual_time_sec == pytest.approx(0.400)
    assert res_turn1["rep_2"].virtual_time_sec == pytest.approx(0.400)

    # Turn 2: Advance time only
    manager.advance_virtual_time(dt_sec=0.200, ticks=3)
    assert manager.get_replica("rep_1").current_virtual_time == pytest.approx(1.000)
    assert manager.get_replica("rep_2").current_virtual_time == pytest.approx(1.000)

    # Turn 3: Second conversational turn
    event2 = InputEvent(
        input_text="Should we prioritize Exhaustive formal verification or Rapid empirical prototyping?",
        stimulus_vector=None,
        metadata={"domain": "TASK_STRATEGY"},
    )
    res_turn2 = manager.step_identical_turn(event2, dt_sec=0.200, sub_steps=1)

    assert manager.current_turn == 2
    assert res_turn2["rep_1"].virtual_time_sec == pytest.approx(1.200)
    assert res_turn2["rep_2"].virtual_time_sec == pytest.approx(1.200)

    # Verify exposure histories match
    report = manager.validate_matched_exposure()
    assert report.is_matched is True
    assert report.total_turns_evaluated == 2


def test_matched_exposure_bookkeeping_and_hashes(manager: ReplicaEnsembleManager):
    """
    Verification that ExposureRecord fields are populated completely and
    exposure hashes are deterministic.
    """
    manager.create_replica(ReplicaConfig(replica_id="rep_audit", seed=999, crn_seed=777))

    stim = np.array([0.5, -0.2, 0.1] + [0.0] * 13, dtype=np.float64)
    event = InputEvent(
        input_text="Test prompt text",
        stimulus_vector=stim,
        metadata={"phase": "p26_test", "condition": "NEUTRAL"},
    )
    res = manager.step_identical_turn(event, dt_sec=0.200, sub_steps=1)

    rec = res["rep_audit"].exposure_record
    assert rec.replica_id == "rep_audit"
    assert rec.seed == 999
    assert rec.turn_index == 1
    assert rec.virtual_time_sec == pytest.approx(0.200)
    assert rec.input_text == "Test prompt text"
    assert rec.stimulus_vector is not None
    assert len(rec.stimulus_vector) == 16
    assert rec.crn_identifier == "CRN_SEED_777"
    assert len(rec.state_fingerprint) == 64

    # Cryptographic exposure hash
    h1 = rec.compute_exposure_hash()
    h2 = rec.compute_exposure_hash()
    assert h1 == h2
    assert len(h1) == 64


def test_exposure_equivalence_validator_detects_mismatches(manager: ReplicaEnsembleManager):
    """
    Verification that ExposureEquivalenceValidator detects intentional or accidental
    exposure divergences across text, vectors, timing, and count.
    """
    configs = [
        ReplicaConfig(replica_id="rep_X", seed=10),
        ReplicaConfig(replica_id="rep_Y", seed=20),
    ]
    manager.create_ensemble(configs)

    # 1. Successful identical match
    ev1 = InputEvent(input_text="Identical input", stimulus_vector=None)
    manager.step_identical_turn(ev1)
    val_ok = manager.validate_matched_exposure()
    assert val_ok.is_matched is True

    # 2. Text mismatch on Turn 2
    divergent_inputs = {
        "rep_X": InputEvent(input_text="Input X"),
        "rep_Y": InputEvent(input_text="Input Y"),
    }
    manager.step_turn(divergent_inputs)
    val_fail_text = manager.validate_matched_exposure()
    assert val_fail_text.is_matched is False
    assert val_fail_text.mismatch_type == "INPUT_TEXT_MISMATCH"
    assert val_fail_text.first_mismatch_turn == 1  # 0-indexed turn 2 is index 1

    # 3. Text mismatch is permitted when explicitly declared in allowed_differences
    allowed = {"turn_1": ["input_text"]}
    val_allowed = manager.validate_matched_exposure(allowed_differences=allowed)
    assert val_allowed.is_matched is True

    # 4. Stimulus vector mismatch
    stim_a = np.array([0.1] * 16, dtype=np.float64)
    stim_b = np.array([0.9] * 16, dtype=np.float64)
    manager.step_turn({
        "rep_X": InputEvent(input_text="Common", stimulus_vector=stim_a),
        "rep_Y": InputEvent(input_text="Common", stimulus_vector=stim_b),
    })
    val_fail_stim = manager.validate_matched_exposure(allowed_differences=allowed)
    assert val_fail_stim.is_matched is False
    assert val_fail_stim.mismatch_type == "STIMULUS_VECTOR_MISMATCH"


def test_state_fingerprint_and_divergence_onset_tracking(manager: ReplicaEnsembleManager):
    """
    Verification that state fingerprints track the exact turn where state divergence begins.
    """
    configs = [
        ReplicaConfig(replica_id="rep_A", seed=1001),
        ReplicaConfig(replica_id="rep_B", seed=1001),  # Same seed for initial state equality
    ]
    manager.create_ensemble(configs)

    # Turn 1: Identical stimulus -> identical fingerprints
    stim = np.zeros(16, dtype=np.float64)
    stim[0] = 0.30
    res1 = manager.step_identical_turn(InputEvent(stimulus_vector=stim))
    fp1_a = res1["rep_A"].state_fingerprint
    fp1_b = res1["rep_B"].state_fingerprint
    assert fp1_a == fp1_b

    # Turn 2: Divergent stimulus presented to Replica A only
    stim_a = np.zeros(16, dtype=np.float64)
    stim_a[1] = 0.80  # Strong arousal pulse to A
    res2 = manager.step_turn({
        "rep_A": InputEvent(stimulus_vector=stim_a),
        "rep_B": InputEvent(stimulus_vector=None),
    })
    fp2_a = res2["rep_A"].state_fingerprint
    fp2_b = res2["rep_B"].state_fingerprint

    # Fingerprints must immediately diverge at Turn 2
    assert fp2_a != fp2_b


def test_deterministic_replay_reproducibility():
    """
    Verification that executing the same sequence of turns on independent manager
    invocations produces bit-exact identical PAD states and fingerprints.
    """
    def run_simulation():
        mgr = ReplicaEnsembleManager(shared_sdm_topology_seed=42)
        mgr.create_ensemble([
            ReplicaConfig(replica_id="r1", seed=2024, crn_seed=888),
            ReplicaConfig(replica_id="r2", seed=2024, crn_seed=888),
        ])
        stim = np.array([0.25, 0.15] + [0.0] * 14, dtype=np.float64)
        r_turn1 = mgr.step_identical_turn(
            InputEvent(input_text="Query 1", stimulus_vector=stim),
            dt_sec=0.200,
            sub_steps=2,
        )
        r_turn2 = mgr.step_identical_turn(
            InputEvent(input_text="Query 2", stimulus_vector=None),
            dt_sec=0.200,
            sub_steps=3,
        )
        fps = [
            r_turn1["r1"].state_fingerprint,
            r_turn2["r1"].state_fingerprint,
        ]
        pads = [
            (r_turn1["r1"].pad_state.pleasure, r_turn1["r1"].pad_state.arousal),
            (r_turn2["r1"].pad_state.pleasure, r_turn2["r1"].pad_state.arousal),
        ]
        mgr.teardown()
        return fps, pads

    fps_run1, pads_run1 = run_simulation()
    fps_run2, pads_run2 = run_simulation()

    assert fps_run1 == fps_run2
    assert pads_run1 == pads_run2
