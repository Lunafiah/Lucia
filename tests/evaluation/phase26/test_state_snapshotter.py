"""
tests/evaluation/phase26/test_state_snapshotter.py

Unit and integration tests for StateSnapshotter (P26 Blocker 4):
- Deep-copy isolation (snapshot is immune to subsequent replica mutations)
- Bit-exact state restoration across EmotionCore, SDMCore, and VirtualClock
- Cryptographic integrity verification and fail-closed rejection of corrupt snapshots
- Schema version and dimension compatibility validation
- Memory trace accumulation and rollback verification
"""

import copy
import numpy as np
import pytest

from tests.evaluation.phase26.replica_ensemble_manager import (
    InputEvent,
    ReplicaConfig,
    ReplicaEnsembleManager,
)
from tests.evaluation.phase26.state_snapshotter import (
    IncompatibleSchemaError,
    ReplicaStateSnapshot,
    SnapshotCorruptionError,
    StateSnapshotter,
)


@pytest.fixture
def manager() -> ReplicaEnsembleManager:
    mgr = ReplicaEnsembleManager(shared_sdm_topology_seed=42)
    yield mgr
    mgr.teardown()


def test_snapshot_capture_and_deep_copy_isolation(manager: ReplicaEnsembleManager):
    """
    Verification that taking a snapshot creates completely decoupled copies
    of limbic ODE tensors, SDM accumulators, and clocks. Subsequent mutations
    to the active replica must NOT mutate the snapshot.
    """
    replica = manager.create_replica(ReplicaConfig(replica_id="rep_snap", seed=1001))

    # Advance 2 turns to accumulate non-trivial state
    stim = np.zeros(16, dtype=np.float64)
    stim[0] = 0.50
    manager.step_identical_turn(InputEvent(stimulus_vector=stim), dt_sec=0.200, sub_steps=2)

    # Write an SDM trace
    addr = np.zeros(replica.sdm._D, dtype=np.uint8)
    content = np.ones(replica.sdm._M, dtype=np.float32) * 2.0
    replica.sdm.write(addr, content)

    # Capture snapshot
    snapshot = StateSnapshotter.capture_snapshot(replica)
    assert snapshot.turn_index == 1
    assert snapshot.virtual_time_sec == pytest.approx(0.400)
    assert snapshot.sdm_state["trace_count"] == 1
    assert StateSnapshotter.verify_integrity(snapshot) is True

    # 1. Mutate replica's limbic state directly
    orig_snap_h = np.copy(snapshot.emotion_state["h_fast"])
    replica.emotion_core._h += 5.0
    assert not np.array_equal(replica.emotion_core._h, orig_snap_h)
    # Snapshot must remain unchanged
    assert np.array_equal(snapshot.emotion_state["h_fast"], orig_snap_h)

    # 2. Mutate replica's SDM accumulator directly
    orig_snap_accum = np.copy(snapshot.sdm_state["accumulator"])
    replica.sdm._accumulator += 10.0
    assert not np.array_equal(replica.sdm._accumulator, orig_snap_accum)
    # Snapshot accumulator must remain unchanged
    assert np.array_equal(snapshot.sdm_state["accumulator"], orig_snap_accum)


def test_snapshot_restore_bit_exactness(manager: ReplicaEnsembleManager):
    """
    Verification that restoring a snapshot returns all subsystems to bit-exact
    identical dynamic states.
    """
    replica = manager.create_replica(ReplicaConfig(replica_id="rep_restore", seed=2002))

    # Step turn 1
    stim = np.array([0.3, 0.4] + [0.0] * 14, dtype=np.float64)
    res1 = manager.step_identical_turn(
        InputEvent(input_text="Turn 1 query", stimulus_vector=stim),
        dt_sec=0.200,
        sub_steps=2,
    )
    fp_at_turn1 = res1["rep_restore"].state_fingerprint
    pad_at_turn1 = (
        res1["rep_restore"].pad_state.pleasure,
        res1["rep_restore"].pad_state.arousal,
        res1["rep_restore"].pad_state.dominance,
    )

    # Checkpoint at turn 1
    snapshot1 = StateSnapshotter.capture_snapshot(replica)

    # Step turn 2 (altering state heavily)
    stim2 = np.array([-0.6, 0.7] + [0.0] * 14, dtype=np.float64)
    res2 = manager.step_identical_turn(
        InputEvent(input_text="Turn 2 intense input", stimulus_vector=stim2),
        dt_sec=0.200,
        sub_steps=3,
    )
    assert replica.turn_index == 2
    assert replica.current_virtual_time == pytest.approx(1.000)
    assert replica.compute_state_fingerprint() != fp_at_turn1

    # Restore back to turn 1
    StateSnapshotter.restore_snapshot(replica, snapshot1)

    assert replica.turn_index == 1
    assert replica.current_virtual_time == pytest.approx(0.400)
    assert replica.compute_state_fingerprint() == fp_at_turn1

    restored_pad = replica.emotion_core.get_pad_state()
    assert (
        restored_pad.pleasure,
        restored_pad.arousal,
        restored_pad.dominance,
    ) == pad_at_turn1


def test_corrupt_snapshot_fail_closed(manager: ReplicaEnsembleManager):
    """
    Verification that tampered snapshots fail cryptographic integrity validation
    and are rejected fail-closed with SnapshotCorruptionError.
    """
    replica = manager.create_replica(ReplicaConfig(replica_id="rep_tamper", seed=3003))
    snapshot = StateSnapshotter.capture_snapshot(replica)

    assert StateSnapshotter.verify_integrity(snapshot) is True

    # Tamper with internal fast limbic state bytes
    snapshot.emotion_state["h_fast"][0] += 0.001

    # Verification must fail
    assert StateSnapshotter.verify_integrity(snapshot) is False

    # Restore must raise SnapshotCorruptionError
    with pytest.raises(SnapshotCorruptionError) as exc_info:
        StateSnapshotter.restore_snapshot(replica, snapshot, verify_integrity=True)
    assert "cryptographic integrity verification" in str(exc_info.value)


def test_incompatible_schema_rejection(manager: ReplicaEnsembleManager):
    """
    Verification that snapshots with mismatched schema versions or incompatible
    dimensions are rejected fail-closed.
    """
    replica = manager.create_replica(ReplicaConfig(replica_id="rep_schema", seed=4004))
    snapshot = StateSnapshotter.capture_snapshot(replica)

    # Incompatible schema version
    snapshot.schema_version = "P26_SNAPSHOT_v999.0"
    with pytest.raises(IncompatibleSchemaError) as exc_info:
        StateSnapshotter.restore_snapshot(replica, snapshot, verify_integrity=False)
    assert "Incompatible snapshot schema version" in str(exc_info.value)

    # Dimension mismatch
    snapshot.schema_version = "P26_SNAPSHOT_v1.0"
    snapshot.emotion_state["h_fast"] = np.zeros(99, dtype=np.float64)  # Wrong dimension
    with pytest.raises(IncompatibleSchemaError) as exc_info:
        StateSnapshotter.restore_snapshot(replica, snapshot, verify_integrity=False)
    assert "dimension mismatch" in str(exc_info.value)


def test_sdm_memory_rollback_on_restore(manager: ReplicaEnsembleManager):
    """
    Verification that SDM memory traces added after a snapshot are completely
    rolled back upon restore, while pre-snapshot traces are preserved.
    """
    replica = manager.create_replica(ReplicaConfig(replica_id="rep_sdm_roll", seed=5005))

    # Write trace 1
    addr1 = np.ones(replica.sdm._D, dtype=np.uint8)
    cont1 = np.ones(replica.sdm._M, dtype=np.float32)
    replica.sdm.write(addr1, cont1)
    assert replica.sdm.trace_count == 1

    # Checkpoint
    snapshot = StateSnapshotter.capture_snapshot(replica)

    # Write trace 2 and 3 post-checkpoint
    addr2 = np.zeros(replica.sdm._D, dtype=np.uint8)
    cont2 = np.ones(replica.sdm._M, dtype=np.float32) * 5.0
    replica.sdm.write(addr2, cont2)
    assert replica.sdm.trace_count == 2

    # Restore
    StateSnapshotter.restore_snapshot(replica, snapshot)

    # Must rollback to exactly 1 trace
    assert replica.sdm.trace_count == 1
    assert 0 in replica.sdm._trace_addresses
    assert 1 not in replica.sdm._trace_addresses
