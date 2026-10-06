"""
tests/evaluation/phase26/test_counterfactual_replay.py

Comprehensive test matrix for CounterfactualReplayHarness (P26 Blocker 4):
- Test A: Same snapshot + same future exposure -> bit-exact same trajectory
- Test B: Same snapshot + declared counterfactual exposure -> divergence onset pinpointed
- Test C: Prefix mismatch -> fail-closed rejection with PrefixMismatchError
- Test D: Snapshot mutation -> original snapshot remains immutable
- Test E: Corrupt snapshot -> rejected fail-closed
- Test F: Incompatible schema/version -> rejected fail-closed
- Test G: Seed / RNG restoration -> reproducible continuation
- Test H: SDM restoration -> memory state exactly restored across replays
- Test I: Virtual clock restoration -> exact time coordinate preservation
- Test J: State fingerprint continuity -> restored continuation matches original baseline
"""

import copy
import numpy as np
import pytest

from tests.evaluation.phase26.counterfactual_replay import (
    CounterfactualDifferenceLedger,
    CounterfactualReplayHarness,
    PrefixEquivalenceValidator,
    PrefixMismatchError,
    ReplayConfigurationError,
)
from tests.evaluation.phase26.replica_ensemble_manager import (
    InputEvent,
    ReplicaConfig,
    ReplicaEnsembleManager,
)
from tests.evaluation.phase26.state_snapshotter import (
    IncompatibleSchemaError,
    SnapshotCorruptionError,
    StateSnapshotter,
)


@pytest.fixture
def replay_setup():
    manager = ReplicaEnsembleManager(shared_sdm_topology_seed=42)
    harness = CounterfactualReplayHarness(manager)
    yield manager, harness
    manager.teardown()


def test_A_same_snapshot_same_future_exposure_bit_exact(replay_setup):
    """
    Test A: Same snapshot + same future exposure -> bit-exact identical trajectory.
    Verifies that forking from a snapshot and providing identical future inputs
    yields zero divergence.
    """
    manager, harness = replay_setup
    baseline = manager.create_replica(ReplicaConfig(replica_id="rep_base", seed=1001, crn_seed=555))

    # Rollout prefix H[0:2]
    ev1 = InputEvent(input_text="Prefix 1", stimulus_vector=np.array([0.2, 0.1] + [0.0]*14))
    ev2 = InputEvent(input_text="Prefix 2", stimulus_vector=np.array([0.4, -0.2] + [0.0]*14))
    manager.step_identical_turn(ev1, dt_sec=0.200, sub_steps=2)
    manager.step_identical_turn(ev2, dt_sec=0.200, sub_steps=2)

    # Snapshot at turn 2
    snapshot = StateSnapshotter.capture_snapshot(baseline)

    # Create twin replica restored from snapshot
    twin = manager.create_replica(ReplicaConfig(replica_id="rep_twin", seed=1001, crn_seed=555))
    StateSnapshotter.restore_snapshot(twin, snapshot)

    # Identical future exposure H[3:4]
    future_ev3 = InputEvent(input_text="Future 3", stimulus_vector=np.array([0.1, 0.5] + [0.0]*14))
    future_ev4 = InputEvent(input_text="Future 4", stimulus_vector=np.array([0.3, 0.0] + [0.0]*14))

    ledger = harness.run_replay_comparison(
        baseline_replica_id="rep_base",
        counterfactual_replica_id="rep_twin",
        checkpoint_turn=2,
        snapshot=snapshot,
        future_baseline_inputs=[future_ev3, future_ev4],
        future_counterfactual_inputs=[future_ev3, future_ev4],
        declared_difference={"type": "IDENTICAL_CONTROL"},
    )

    # Must observe bit-exact identical continuation: NO divergence
    assert ledger.divergence_onset_turn is None
    assert ledger.divergence_onset_time is None
    assert ledger.state_fingerprints_baseline == ledger.state_fingerprints_counterfactual
    assert ledger.baseline_exposure_hashes == ledger.counterfactual_exposure_hashes


def test_B_counterfactual_divergence_onset_detection(replay_setup):
    """
    Test B: Same snapshot + declared counterfactual exposure -> replay executes
    and divergence onset is pinpointed at the exact turn.
    """
    manager, harness = replay_setup
    baseline = manager.create_replica(ReplicaConfig(replica_id="rep_b_base", seed=2002, crn_seed=777))

    # Prefix H[0:1]
    ev1 = InputEvent(input_text="Prefix turn", stimulus_vector=np.array([0.3] * 16))
    manager.step_identical_turn(ev1, dt_sec=0.200, sub_steps=1)

    snapshot = StateSnapshotter.capture_snapshot(baseline)

    # Fork branch
    cf = manager.create_replica(ReplicaConfig(replica_id="rep_b_cf", seed=2002, crn_seed=777))
    StateSnapshotter.restore_snapshot(cf, snapshot)

    # Future: Turn 2 identical, Turn 3 divergent
    ev2 = InputEvent(input_text="Common Turn 2", stimulus_vector=np.array([0.1] * 16))
    ev3_base = InputEvent(input_text="Base Choice A", stimulus_vector=np.array([0.5, 0.2] + [0.0]*14))
    ev3_cf = InputEvent(input_text="CF Choice B", stimulus_vector=np.array([-0.5, 0.8] + [0.0]*14))

    ledger = harness.run_replay_comparison(
        baseline_replica_id="rep_b_base",
        counterfactual_replica_id="rep_b_cf",
        checkpoint_turn=1,
        snapshot=snapshot,
        future_baseline_inputs=[ev2, ev3_base],
        future_counterfactual_inputs=[ev2, ev3_cf],
        declared_difference={"turn_3": ["stimulus_vector", "input_text"]},
    )

    # Divergence must begin exactly at Turn 3 (virtual time 0.600s)
    assert ledger.divergence_onset_turn == 3
    assert ledger.divergence_onset_time == pytest.approx(0.600)
    # Turn 1 and Turn 2 fingerprints match
    assert ledger.state_fingerprints_baseline[0] == ledger.state_fingerprints_counterfactual[0]
    assert ledger.state_fingerprints_baseline[1] == ledger.state_fingerprints_counterfactual[1]
    # Turn 3 fingerprints diverge
    assert ledger.state_fingerprints_baseline[2] != ledger.state_fingerprints_counterfactual[2]


def test_C_prefix_mismatch_rejected_fail_closed(replay_setup):
    """
    Test C: Prefix mismatch -> fail-closed rejection with PrefixMismatchError.
    """
    manager, harness = replay_setup
    rep1 = manager.create_replica(ReplicaConfig(replica_id="rep_c1", seed=100))
    rep2 = manager.create_replica(ReplicaConfig(replica_id="rep_c2", seed=200))

    # Stepping with different inputs
    manager.step_turn({
        "rep_c1": InputEvent(input_text="Input Alpha"),
        "rep_c2": InputEvent(input_text="Input Beta"),
    })

    snap1 = StateSnapshotter.capture_snapshot(rep1)

    # Prefix validator must reject comparing rep2 against snap1
    with pytest.raises(PrefixMismatchError) as exc_info:
        PrefixEquivalenceValidator.validate_prefix_equivalence(
            history_a=rep2.exposure_history,
            history_b=snap1.exposure_history,
            up_to_turn=1,
            state_fingerprint_a=rep2.compute_state_fingerprint(),
            state_fingerprint_b=snap1.compute_integrity_hash(),
        )
    assert "Prefix exposure mismatch" in str(exc_info.value)


def test_D_snapshot_immutability_and_deep_copy(replay_setup):
    """
    Test D: Snapshot mutation -> original snapshot remains immutable.
    """
    manager, _ = replay_setup
    rep = manager.create_replica(ReplicaConfig(replica_id="rep_d", seed=555))
    manager.step_identical_turn(InputEvent(stimulus_vector=np.array([0.4] * 16)))

    snap = StateSnapshotter.capture_snapshot(rep)
    snap_hash = snap.compute_integrity_hash()

    # Deepcopy snapshot and mutate the copy
    snap_copy = copy.deepcopy(snap)
    snap_copy.emotion_state["h_fast"][0] += 99.0

    # Original snapshot must remain intact and valid
    assert snap.compute_integrity_hash() == snap_hash
    assert StateSnapshotter.verify_integrity(snap) is True
    # Mutated copy must fail integrity
    assert StateSnapshotter.verify_integrity(snap_copy) is False


def test_E_corrupt_snapshot_rejected(replay_setup):
    """
    Test E: Corrupt snapshot -> rejected fail-closed during restore.
    """
    manager, _ = replay_setup
    rep = manager.create_replica(ReplicaConfig(replica_id="rep_e", seed=777))
    snap = StateSnapshotter.capture_snapshot(rep)

    # Corrupt SDM accumulator bytes
    snap.sdm_state["accumulator"][0, 0] += 0.5

    with pytest.raises(SnapshotCorruptionError):
        StateSnapshotter.restore_snapshot(rep, snap, verify_integrity=True)


def test_F_incompatible_schema_version_rejected(replay_setup):
    """
    Test F: Incompatible schema/version -> rejected fail-closed.
    """
    manager, _ = replay_setup
    rep = manager.create_replica(ReplicaConfig(replica_id="rep_f", seed=888))
    snap = StateSnapshotter.capture_snapshot(rep)

    snap.schema_version = "P26_SNAPSHOT_INVALID_v0.0"
    with pytest.raises(IncompatibleSchemaError):
        StateSnapshotter.restore_snapshot(rep, snap, verify_integrity=False)


def test_G_seed_and_rng_restoration(replay_setup):
    """
    Test G: Seed / RNG restoration -> stochastic backend produces reproducible continuation.
    Verifies 4 distinct levels of RNG/determinism restoration:
      1. Seed restoration (pre-snapshot seed preserved, post-snapshot mutations reverted)
      2. Call-count restoration (call counter accurately rolled back)
      3. Deterministic output restoration (identical prompt/seed yields identical mock output)
      4. PRNG internal state restoration (R1 == R1' and R2 == R2' across generator resumption)
    """
    manager, _ = replay_setup
    rep = manager.create_replica(ReplicaConfig(replica_id="rep_g", seed=1234, crn_seed=4321))

    # Pre-snapshot activity
    _ = rep.rng.random(3)
    rep.llm.generate("Pre-snapshot query", seed=1111)
    assert rep.llm.call_count == 1
    assert rep.llm.last_seed_used == 1111

    # Capture snapshot
    snap = StateSnapshotter.capture_snapshot(rep)

    # Baseline continuation: generate sequences R1, R2 from replica RNG and LLM output
    r1_baseline = rep.rng.random(5).tolist()
    r2_baseline = rep.rng.random(5).tolist()
    prompt = "Should we inspect Deep-sea hydrothermal ecosystems or Medieval maritime cartography first?"
    llm_out_baseline = rep.llm.generate(prompt, seed=rep.crn_seed)
    assert rep.llm.call_count == 2
    assert rep.llm.last_seed_used == 4321

    # Mutate / diverge replica state (both PRNG stream and LLM)
    _ = rep.rng.random(25)
    rep.llm.generate("Divergent query", seed=9999)
    assert rep.llm.call_count == 3
    assert rep.llm.last_seed_used == 9999

    # Restore snapshot
    StateSnapshotter.restore_snapshot(rep, snap)

    # 1. Level 1 & 2: Seed & call-count restoration
    assert rep.llm.call_count == 1
    assert rep.llm.last_seed_used == 1111

    # 2. Level 4: True PRNG internal state restoration (R1 == R1', R2 == R2')
    r1_restored = rep.rng.random(5).tolist()
    r2_restored = rep.rng.random(5).tolist()
    assert r1_baseline == r1_restored, "PRNG sequence R1 diverged after snapshot restoration!"
    assert r2_baseline == r2_restored, "PRNG sequence R2 diverged after snapshot restoration!"

    # 3. Level 3: Deterministic output restoration
    llm_out_restored = rep.llm.generate(prompt, seed=rep.crn_seed)
    assert llm_out_baseline == llm_out_restored
    assert rep.llm.call_count == 2
    assert rep.llm.last_seed_used == 4321


def test_H_sdm_restoration_bit_exact(replay_setup):
    """
    Test H: SDM restoration -> memory state exactly restored across rollbacks.
    """
    manager, _ = replay_setup
    rep = manager.create_replica(ReplicaConfig(replica_id="rep_h", seed=900))

    addr = np.zeros(rep.sdm._D, dtype=np.uint8)
    content = np.ones(rep.sdm._M, dtype=np.float32)
    rep.sdm.write(addr, content)

    snap = StateSnapshotter.capture_snapshot(rep)
    assert snap.sdm_state["trace_count"] == 1

    # Add 2 more traces
    rep.sdm.write(addr, content * 2)
    rep.sdm.write(addr, content * 3)
    assert rep.sdm.trace_count == 3

    # Restore
    StateSnapshotter.restore_snapshot(rep, snap)
    assert rep.sdm.trace_count == 1
    read_cont = rep.sdm.read(addr)
    # Recovered content must be aligned with 1 write
    assert np.allclose(read_cont, content, atol=1e-5)


def test_I_virtual_clock_restoration(replay_setup):
    """
    Test I: Virtual clock restoration -> exact time coordinate preservation.
    """
    manager, _ = replay_setup
    rep = manager.create_replica(ReplicaConfig(replica_id="rep_i", seed=321))
    manager.step_identical_turn(InputEvent(), dt_sec=0.200, sub_steps=5)
    assert rep.current_virtual_time == pytest.approx(1.000)

    snap = StateSnapshotter.capture_snapshot(rep)

    # Advance clock further
    manager.advance_virtual_time(dt_sec=0.200, ticks=10)
    assert rep.current_virtual_time == pytest.approx(3.000)

    # Restore
    StateSnapshotter.restore_snapshot(rep, snap)
    assert rep.current_virtual_time == pytest.approx(1.000)
    assert rep.turn_index == 1


def test_J_state_fingerprint_continuity(replay_setup):
    """
    Test J: State fingerprint continuity -> restored continuation matches original
    baseline when future exposure is identical.
    """
    manager, _ = replay_setup
    rep_a = manager.create_replica(ReplicaConfig(replica_id="rep_ja", seed=707, crn_seed=808))
    rep_b = manager.create_replica(ReplicaConfig(replica_id="rep_jb", seed=707, crn_seed=808))

    ev1 = InputEvent(input_text="Step 1", stimulus_vector=np.array([0.2] * 16))
    ev2 = InputEvent(input_text="Step 2", stimulus_vector=np.array([0.4] * 16))

    # Advance both replicas identically
    manager.step_identical_turn(ev1)
    snap_a = StateSnapshotter.capture_snapshot(rep_a)

    # Advance A with ev2
    res_a2 = manager.step_turn({"rep_ja": ev2})
    fp_a_turn2 = res_a2["rep_ja"].state_fingerprint

    # Restore B from snap_a, then step B with ev2
    StateSnapshotter.restore_snapshot(rep_b, snap_a)
    res_b2 = manager.step_turn({"rep_jb": ev2})
    fp_b_turn2 = res_b2["rep_jb"].state_fingerprint

    # State fingerprints must be bit-exact identical
    assert fp_a_turn2 == fp_b_turn2
