"""
tests/evaluation/phase26/test_yoked_control_runner.py

Verification suite for P26 Blocker 5 — Yoked-Control Runner & Action-Contingency Validation.
Verifies Test Matrix A through O:
  A. Active action capture
  B. Yoked action replay
  C. Action hash integrity
  D. Wrong-turn rejection
  E. Wrong-source rejection
  F. Missing-action rejection
  G. Duplicate-action rejection
  H. Exposure mismatch rejection
  I. Virtual-time mismatch rejection
  J. Provenance chain validation
  K. Active/yoked distinction preservation
  L. Deterministic replay
  M. Tampered ledger rejection
  N. B2 regression
  O. B4 regression
"""

from __future__ import annotations

import copy
import pytest
import numpy as np

from tests.evaluation.phase26.action_ledger import (
    ActionLedger,
    ActionLedgerCorruptionError,
    ActionMismatchError,
    ActionSequenceError,
    ActionSource,
    YokedActionRecord,
    compute_canonical_action_hash,
)
from tests.evaluation.phase26.yoked_control_runner import (
    ActionContingencyValidator,
    ContingencyAuditReport,
    ExposureMismatchError,
    VirtualTimeMismatchError,
    YokedControlRunner,
)
from tests.evaluation.phase26.replica_ensemble_manager import (
    InputEvent,
    ReplicaConfig,
    ReplicaEnsembleManager,
)
from tests.evaluation.phase26.state_snapshotter import (
    StateSnapshotter,
)


@pytest.fixture
def runner_fixture():
    active_cfg = ReplicaConfig(replica_id="active_rep", seed=100, crn_seed=555)
    yoked_cfg = ReplicaConfig(replica_id="yoked_rep", seed=200, crn_seed=555)
    runner = YokedControlRunner(
        experiment_id="exp_test_yoked",
        active_config=active_cfg,
        yoked_config=yoked_cfg,
        shared_sdm_topology_seed=42,
    )
    return runner


def dummy_decision_fn(replica, turn_result):
    """Deterministic synthetic decision function for testing."""
    return {
        "type": "PROBE_SELECTION",
        "payload": {
            "chosen_probe": "A",
            "confidence": 0.85,
            "turn": turn_result.turn_index,
        },
    }


def test_A_active_action_capture(runner_fixture):
    """Test A: Active action capture records valid action record with source=ACTIVE."""
    runner = runner_fixture
    inp = InputEvent(input_text="Choose option A or B", stimulus_vector=np.array([0.1, 0.0, 0.0]))

    turn_res, rec = runner.execute_active_turn(inp, dummy_decision_fn)

    assert rec.turn_index == 1
    assert rec.source == ActionSource.ACTIVE
    assert rec.action_type == "PROBE_SELECTION"
    assert rec.action_payload["chosen_probe"] == "A"
    assert rec.action_payload["confidence"] == 0.85
    assert len(rec.action_hash) == 64
    assert rec.source_state_fingerprint == turn_res.state_fingerprint
    assert len(runner.active_ledger) == 1


def test_B_yoked_action_replay(runner_fixture):
    """Test B: Yoked replica replays active action with identical payload and source=YOKED_REPLAY."""
    runner = runner_fixture
    inp = InputEvent(input_text="Choose option A or B", stimulus_vector=np.array([0.1, 0.0, 0.0]))

    _, act_rec = runner.execute_active_turn(inp, dummy_decision_fn)
    yok_res, yok_rec = runner.execute_yoked_turn(inp, act_rec)

    assert yok_rec.turn_index == 1
    assert yok_rec.source == ActionSource.YOKED_REPLAY
    assert yok_rec.action_hash == act_rec.action_hash
    assert yok_rec.action_payload == act_rec.action_payload
    assert len(runner.yoked_ledger) == 1


def test_C_action_hash_integrity():
    """Test C: Cryptographic integrity check validates canonical payload hash."""
    payload = {"option": "A", "val": [1, 2, 3]}
    act_hash = compute_canonical_action_hash("TEST_TYPE", payload)

    rec = YokedActionRecord(
        experiment_id="exp1",
        active_replica_id="act",
        yoked_replica_id="yok",
        turn_index=1,
        virtual_time_sec=0.2,
        action_id="act_1",
        action_type="TEST_TYPE",
        action_payload=payload,
        action_hash=act_hash,
        source=ActionSource.ACTIVE,
        source_turn=1,
        source_state_fingerprint="fp1",
        exposure_hash="exp_hash1",
    )
    assert rec.verify_integrity() is True

    # Tampering with payload
    rec.action_payload["option"] = "B"
    assert rec.verify_integrity() is False


def test_D_wrong_turn_rejection(runner_fixture):
    """Test D: Replaying an action with a mismatched turn index raises ActionSequenceError."""
    runner = runner_fixture
    inp = InputEvent(input_text="Turn 1 input")

    _, act_rec = runner.execute_active_turn(inp, dummy_decision_fn)

    # Corrupt turn_index on active_record
    tampered_rec = copy.deepcopy(act_rec)
    tampered_rec.turn_index = 99

    with pytest.raises(ActionSequenceError, match="Turn index mismatch"):
        runner.execute_yoked_turn(inp, tampered_rec)


def test_E_wrong_source_rejection(runner_fixture):
    """Test E: Attempting to yoke-replay a record whose source is not ACTIVE raises ActionMismatchError."""
    runner = runner_fixture
    inp = InputEvent(input_text="Turn 1 input")

    _, act_rec = runner.execute_active_turn(inp, dummy_decision_fn)

    # Set source to YOKED_REPLAY prematurely
    tampered_rec = copy.deepcopy(act_rec)
    tampered_rec.source = ActionSource.YOKED_REPLAY

    with pytest.raises(ActionMismatchError, match="source is not ACTIVE"):
        runner.execute_yoked_turn(inp, tampered_rec)


def test_F_missing_action_rejection(runner_fixture):
    """Test F: Missing action record in yoked execution leads to fail-closed audit rejection."""
    runner = runner_fixture
    inp1 = InputEvent(input_text="Turn 1")
    inp2 = InputEvent(input_text="Turn 2")

    # Step active twice
    runner.execute_active_turn(inp1, dummy_decision_fn)
    runner.execute_active_turn(inp2, dummy_decision_fn)

    # Step yoked only once
    act_rec1 = runner.active_ledger.records[0]
    runner.execute_yoked_turn(inp1, act_rec1)

    # Audit must detect turn count mismatch
    report = runner.audit_contingency()
    assert report.is_valid is False
    assert report.mismatch_type == "TURN_COUNT_MISMATCH"


def test_G_duplicate_action_rejection():
    """Test G: Duplicate turn index or duplicate action ID raises ActionSequenceError."""
    ledger = ActionLedger(experiment_id="exp1", active_replica_id="act")
    ledger.record_active_action(
        turn_index=1,
        virtual_time_sec=0.2,
        action_id="act_1",
        action_type="TYPE_A",
        action_payload={"p": 1},
        source_state_fingerprint="fp1",
        exposure_hash="exp1",
    )

    # Attempting duplicate turn index
    with pytest.raises(ActionSequenceError, match="Duplicate turn index 1"):
        ledger.record_active_action(
            turn_index=1,
            virtual_time_sec=0.4,
            action_id="act_2",
            action_type="TYPE_A",
            action_payload={"p": 2},
            source_state_fingerprint="fp2",
            exposure_hash="exp2",
        )


def test_H_exposure_mismatch_rejection(runner_fixture):
    """Test H: Different input event presented to yoked replica raises ExposureMismatchError."""
    runner = runner_fixture
    inp_active = InputEvent(input_text="Option A")
    inp_yoked = InputEvent(input_text="Option B")

    _, act_rec = runner.execute_active_turn(inp_active, dummy_decision_fn)

    with pytest.raises(ExposureMismatchError, match="Exposure mismatch"):
        runner.execute_yoked_turn(inp_yoked, act_rec)


def test_I_virtual_time_mismatch_rejection(runner_fixture):
    """Test I: Clock drift between active and yoked raises VirtualTimeMismatchError."""
    runner = runner_fixture
    inp = InputEvent(input_text="Sync test")

    # Active turn with dt=0.2
    _, act_rec = runner.execute_active_turn(inp, dummy_decision_fn, dt_sec=0.200)

    # Yoked turn with dt=0.4 (causing clock drift)
    with pytest.raises(VirtualTimeMismatchError, match="Virtual time drift"):
        runner.execute_yoked_turn(inp, act_rec, dt_sec=0.400)


def test_J_provenance_chain_validation(runner_fixture):
    """Test J: Compute record hash changes if any provenance field is altered."""
    runner = runner_fixture
    inp = InputEvent(input_text="Provenance test")
    _, rec = runner.execute_active_turn(inp, dummy_decision_fn)

    base_hash = rec.compute_record_hash()

    rec_mod = copy.deepcopy(rec)
    rec_mod.source_turn = 99
    assert rec_mod.compute_record_hash() != base_hash

    rec_mod2 = copy.deepcopy(rec)
    rec_mod2.virtual_time_sec += 0.1
    assert rec_mod2.compute_record_hash() != base_hash


def test_K_active_yoked_distinction_preservation(runner_fixture):
    """Test K: Paired rollout cleanly isolates the declared difference (source only)."""
    runner = runner_fixture
    for t in range(3):
        inp = InputEvent(input_text=f"Turn {t + 1} stimulus")
        runner.step_paired_turn(inp, dummy_decision_fn)

    report = runner.audit_contingency()
    assert report.is_valid is True
    assert report.total_turns_audited == 3
    assert report.action_hashes_matched is True
    assert report.exposure_hashes_matched is True
    assert report.virtual_time_matched is True
    assert report.source_distinction_preserved is True
    assert report.declared_difference_isolated is True
    assert report.crn_aligned is True


def test_L_deterministic_replay():
    """Test L: Two independent trials with identical configuration yield bit-exact ledgers."""
    def run_trial():
        cfg_act = ReplicaConfig(replica_id="act", seed=42, crn_seed=123)
        cfg_yok = ReplicaConfig(replica_id="yok", seed=84, crn_seed=123)
        r = YokedControlRunner("exp_det", cfg_act, cfg_yok)
        for t in range(2):
            inp = InputEvent(input_text=f"Probe {t}", stimulus_vector=np.array([0.1, -0.1, 0.0]))
            r.step_paired_turn(inp, dummy_decision_fn)
        return r.active_ledger.to_json(), r.yoked_ledger.to_json()

    act1, yok1 = run_trial()
    act2, yok2 = run_trial()

    assert act1 == act2
    assert yok1 == yok2


def test_M_tampered_ledger_rejection(runner_fixture):
    """Test M: Post-execution tampering of action ledger triggers fail-closed audit rejection."""
    runner = runner_fixture
    inp = InputEvent(input_text="Turn 1")
    runner.step_paired_turn(inp, dummy_decision_fn)

    # Tamper with yoked ledger record payload without updating hash
    runner.yoked_ledger._records[0].action_payload["chosen_probe"] = "Z"

    report = runner.audit_contingency()
    assert report.is_valid is False
    assert report.mismatch_type in ("ACTION_HASH_MISMATCH", "RECORD_INTEGRITY_COMPROMISED")


def test_N_b2_regression():
    """Test N: Multi-replica isolation from B2 remains fully functional alongside yoked runner."""
    mgr = ReplicaEnsembleManager(shared_sdm_topology_seed=10)
    c1 = ReplicaConfig(replica_id="r1", seed=10)
    c2 = ReplicaConfig(replica_id="r2", seed=20)
    mgr.create_replica(c1)
    mgr.create_replica(c2)

    audit = mgr.verify_isolation()
    assert audit.is_isolated is True
    assert audit.mutation_bleed_detected is False


def test_O_b4_regression(runner_fixture):
    """Test O: State snapshotting and restoration from B4 operates seamlessly on yoked replicas."""
    runner = runner_fixture
    inp = InputEvent(input_text="Step 1")
    runner.step_paired_turn(inp, dummy_decision_fn)

    # Snapshot yoked replica
    snap = StateSnapshotter.capture_snapshot(runner.yoked_replica)
    assert snap.turn_index == 1

    # Step again
    inp2 = InputEvent(input_text="Step 2")
    runner.step_paired_turn(inp2, dummy_decision_fn)
    assert runner.yoked_replica.turn_index == 2

    # Restore snapshot
    StateSnapshotter.restore_snapshot(runner.yoked_replica, snap)
    assert runner.yoked_replica.turn_index == 1
