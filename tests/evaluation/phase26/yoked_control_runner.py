"""
tests/evaluation/phase26/yoked_control_runner.py

P26 Blocker 5 — Yoked-Control Runner & Action-Contingency Validation Harness.
Orchestrates paired Active/Yoked research replicas to audit whether behavioral
differentiation depends on action-contingent history rather than input streams alone.

GOVERNANCE & BOUNDARIES:
- TEST-ONLY research infrastructure. Zero changes to src/core/**, electron/**, data/**.
- INV-1 (Anti-Branching): Replicas are transient RAM-resident evaluation fixtures.
  No live-user branching or multi-persona cloning is created.
- Scientific Scope: Validates experimental apparatus for yoked control;
  does NOT run full C3 experiment and does NOT claim Claim C3 (History Endogeneity).
"""

from __future__ import annotations

import copy
import hashlib
import json
import logging
from dataclasses import asdict, dataclass, field
from typing import Any, Callable, Dict, List, Optional, Tuple

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
from tests.evaluation.phase26.replica_ensemble_manager import (
    ExposureEquivalenceValidator,
    ExposureRecord,
    InputEvent,
    ReplicaConfig,
    ReplicaEnsembleManager,
    ResearchReplica,
    TurnResult,
)

logger = logging.getLogger("YokedControlRunner")


class ProvenanceMismatchError(Exception):
    """Raised when action provenance, source tag, or state fingerprint continuity is violated."""
    pass


class VirtualTimeMismatchError(Exception):
    """Raised when virtual clock coordinates drift between active and yoked replicas."""
    pass


class ExposureMismatchError(Exception):
    """Raised when sensory or conversational exposure sequences between active and yoked diverge."""
    pass


@dataclass
class ContingencyAuditReport:
    """
    Formal audit report evaluating equivalence, synchronization, and declared source
    distinction between paired active and yoked replicas.
    """
    is_valid: bool
    total_turns_audited: int
    active_replica_id: str
    yoked_replica_id: str
    action_hashes_matched: bool
    exposure_hashes_matched: bool
    virtual_time_matched: bool
    source_distinction_preserved: bool
    declared_difference_isolated: bool
    crn_aligned: bool
    first_mismatch_turn: Optional[int] = None
    mismatch_type: Optional[str] = None
    discrepancy_details: Dict[str, Any] = field(default_factory=dict)


class ActionContingencyValidator:
    """
    Fail-closed validator verifying that:
    1. Active and Yoked replicas experienced bit-exact equivalent exposure histories.
    2. Virtual time coordinates remained synchronous.
    3. Action types, payloads, and action hashes matched identically.
    4. Action sources strictly preserved the declared distinction:
       Active actions have source == ACTIVE.
       Yoked actions have source == YOKED_REPLAY.
    5. No undeclared variance or mutation bleed occurred.
    """

    @classmethod
    def validate_pairing(
        cls,
        active_replica: ResearchReplica,
        yoked_replica: ResearchReplica,
        active_ledger: ActionLedger,
        yoked_ledger: ActionLedger,
        time_tolerance: float = 1e-9,
    ) -> ContingencyAuditReport:
        """
        Performs an exhaustive turn-by-turn audit across active and yoked executions.
        Fails closed on any discrepancy outside the declared action source distinction.
        """
        active_records = active_ledger.records
        yoked_records = yoked_ledger.records

        if len(active_records) != len(yoked_records):
            return ContingencyAuditReport(
                is_valid=False,
                total_turns_audited=max(len(active_records), len(yoked_records)),
                active_replica_id=active_replica.replica_id,
                yoked_replica_id=yoked_replica.replica_id,
                action_hashes_matched=False,
                exposure_hashes_matched=False,
                virtual_time_matched=False,
                source_distinction_preserved=False,
                declared_difference_isolated=False,
                crn_aligned=False,
                first_mismatch_turn=min(len(active_records), len(yoked_records)),
                mismatch_type="TURN_COUNT_MISMATCH",
                discrepancy_details={
                    "active_turns": len(active_records),
                    "yoked_turns": len(yoked_records),
                },
            )

        n = len(active_records)

        # 1. CRN Alignment Check
        crn_aligned = True
        if active_replica.crn_seed != yoked_replica.crn_seed:
            crn_aligned = False
            return ContingencyAuditReport(
                is_valid=False,
                total_turns_audited=n,
                active_replica_id=active_replica.replica_id,
                yoked_replica_id=yoked_replica.replica_id,
                action_hashes_matched=False,
                exposure_hashes_matched=False,
                virtual_time_matched=False,
                source_distinction_preserved=False,
                declared_difference_isolated=False,
                crn_aligned=False,
                first_mismatch_turn=0,
                mismatch_type="CRN_SEED_MISMATCH",
                discrepancy_details={
                    "active_crn": active_replica.crn_seed,
                    "yoked_crn": yoked_replica.crn_seed,
                },
            )

        # 2. Turn-by-Turn Verification
        for i in range(n):
            act_rec = active_records[i]
            yok_rec = yoked_records[i]

            # Turn index matching
            if act_rec.turn_index != yok_rec.turn_index or act_rec.turn_index != (i + 1):
                return ContingencyAuditReport(
                    is_valid=False,
                    total_turns_audited=i + 1,
                    active_replica_id=active_replica.replica_id,
                    yoked_replica_id=yoked_replica.replica_id,
                    action_hashes_matched=False,
                    exposure_hashes_matched=False,
                    virtual_time_matched=False,
                    source_distinction_preserved=False,
                    declared_difference_isolated=False,
                    crn_aligned=crn_aligned,
                    first_mismatch_turn=i + 1,
                    mismatch_type="TURN_INDEX_MISMATCH",
                    discrepancy_details={
                        "active_turn": act_rec.turn_index,
                        "yoked_turn": yok_rec.turn_index,
                    },
                )

            # Virtual time equivalence
            dt = abs(act_rec.virtual_time_sec - yok_rec.virtual_time_sec)
            if dt > time_tolerance:
                return ContingencyAuditReport(
                    is_valid=False,
                    total_turns_audited=i + 1,
                    active_replica_id=active_replica.replica_id,
                    yoked_replica_id=yoked_replica.replica_id,
                    action_hashes_matched=False,
                    exposure_hashes_matched=False,
                    virtual_time_matched=False,
                    source_distinction_preserved=False,
                    declared_difference_isolated=False,
                    crn_aligned=crn_aligned,
                    first_mismatch_turn=i + 1,
                    mismatch_type="VIRTUAL_TIME_DRIFT",
                    discrepancy_details={
                        "active_time": act_rec.virtual_time_sec,
                        "yoked_time": yok_rec.virtual_time_sec,
                        "drift": dt,
                    },
                )

            # Action payload and hash equivalence
            if act_rec.action_hash != yok_rec.action_hash or act_rec.action_payload != yok_rec.action_payload:
                return ContingencyAuditReport(
                    is_valid=False,
                    total_turns_audited=i + 1,
                    active_replica_id=active_replica.replica_id,
                    yoked_replica_id=yoked_replica.replica_id,
                    action_hashes_matched=False,
                    exposure_hashes_matched=False,
                    virtual_time_matched=True,
                    source_distinction_preserved=False,
                    declared_difference_isolated=False,
                    crn_aligned=crn_aligned,
                    first_mismatch_turn=i + 1,
                    mismatch_type="ACTION_HASH_MISMATCH",
                    discrepancy_details={
                        "active_hash": act_rec.action_hash,
                        "yoked_hash": yok_rec.action_hash,
                    },
                )

            # Exposure hash equivalence
            if act_rec.exposure_hash != yok_rec.exposure_hash:
                return ContingencyAuditReport(
                    is_valid=False,
                    total_turns_audited=i + 1,
                    active_replica_id=active_replica.replica_id,
                    yoked_replica_id=yoked_replica.replica_id,
                    action_hashes_matched=True,
                    exposure_hashes_matched=False,
                    virtual_time_matched=True,
                    source_distinction_preserved=False,
                    declared_difference_isolated=False,
                    crn_aligned=crn_aligned,
                    first_mismatch_turn=i + 1,
                    mismatch_type="EXPOSURE_HASH_MISMATCH",
                    discrepancy_details={
                        "active_exposure": act_rec.exposure_hash,
                        "yoked_exposure": yok_rec.exposure_hash,
                    },
                )

            # Declared Source Distinction:
            # Active must be ACTIVE; Yoked must be YOKED_REPLAY.
            if act_rec.source != ActionSource.ACTIVE or yok_rec.source != ActionSource.YOKED_REPLAY:
                return ContingencyAuditReport(
                    is_valid=False,
                    total_turns_audited=i + 1,
                    active_replica_id=active_replica.replica_id,
                    yoked_replica_id=yoked_replica.replica_id,
                    action_hashes_matched=True,
                    exposure_hashes_matched=True,
                    virtual_time_matched=True,
                    source_distinction_preserved=False,
                    declared_difference_isolated=False,
                    crn_aligned=crn_aligned,
                    first_mismatch_turn=i + 1,
                    mismatch_type="SOURCE_DISTINCTION_VIOLATION",
                    discrepancy_details={
                        "active_source": act_rec.source.value,
                        "yoked_source": yok_rec.source.value,
                    },
                )

            # Cryptographic integrity of both records
            if not act_rec.verify_integrity() or not yok_rec.verify_integrity():
                return ContingencyAuditReport(
                    is_valid=False,
                    total_turns_audited=i + 1,
                    active_replica_id=active_replica.replica_id,
                    yoked_replica_id=yoked_replica.replica_id,
                    action_hashes_matched=True,
                    exposure_hashes_matched=True,
                    virtual_time_matched=True,
                    source_distinction_preserved=True,
                    declared_difference_isolated=False,
                    crn_aligned=crn_aligned,
                    first_mismatch_turn=i + 1,
                    mismatch_type="RECORD_INTEGRITY_COMPROMISED",
                )

        return ContingencyAuditReport(
            is_valid=True,
            total_turns_audited=n,
            active_replica_id=active_replica.replica_id,
            yoked_replica_id=yoked_replica.replica_id,
            action_hashes_matched=True,
            exposure_hashes_matched=True,
            virtual_time_matched=True,
            source_distinction_preserved=True,
            declared_difference_isolated=True,
            crn_aligned=crn_aligned,
        )


class YokedControlRunner:
    """
    Coordinates synchronous execution of paired Active and Yoked replicas.
    Captures active actions endogenously, and executes verified external replay
    into the yoked replica.
    """

    def __init__(
        self,
        experiment_id: str,
        active_config: ReplicaConfig,
        yoked_config: ReplicaConfig,
        shared_sdm_topology_seed: Optional[int] = 42,
    ) -> None:
        self.experiment_id = experiment_id
        self.manager = ReplicaEnsembleManager(shared_sdm_topology_seed=shared_sdm_topology_seed)

        self.active_replica = self.manager.create_replica(active_config)
        self.yoked_replica = self.manager.create_replica(yoked_config)

        self.active_ledger = ActionLedger(
            experiment_id=experiment_id,
            active_replica_id=active_config.replica_id,
            yoked_replica_id=yoked_config.replica_id,
        )
        self.yoked_ledger = ActionLedger(
            experiment_id=experiment_id,
            active_replica_id=active_config.replica_id,
            yoked_replica_id=yoked_config.replica_id,
        )

    def execute_active_turn(
        self,
        input_event: InputEvent,
        decision_fn: Callable[[ResearchReplica, TurnResult], Dict[str, Any]],
        dt_sec: float = 0.200,
        sub_steps: int = 1,
    ) -> Tuple[TurnResult, YokedActionRecord]:
        """
        Executes a turn on the active replica:
        1. Steps the active replica with input_event.
        2. Evaluates decision_fn to obtain the endogenous action payload.
        3. Records the action in active_ledger with source = ActionSource.ACTIVE.
        """
        results = self.manager.step_turn(
            {self.active_replica.replica_id: input_event},
            dt_sec=dt_sec,
            sub_steps=sub_steps,
        )
        turn_res = results[self.active_replica.replica_id]

        action_decision = decision_fn(self.active_replica, turn_res)
        action_type = str(action_decision.get("type", "GENERIC_ACTION"))
        action_payload = action_decision.get("payload", {})
        action_id = f"act_{self.active_replica.replica_id}_t{turn_res.turn_index}"

        exp_hash = turn_res.exposure_record.compute_exposure_hash()

        record = self.active_ledger.record_active_action(
            turn_index=turn_res.turn_index,
            virtual_time_sec=turn_res.virtual_time_sec,
            action_id=action_id,
            action_type=action_type,
            action_payload=action_payload,
            source_state_fingerprint=turn_res.state_fingerprint,
            exposure_hash=exp_hash,
            crn_identifier=f"CRN_SEED_{self.active_replica.crn_seed}"
            if self.active_replica.crn_seed is not None
            else None,
        )

        return turn_res, record

    def execute_yoked_turn(
        self,
        input_event: InputEvent,
        active_record: YokedActionRecord,
        dt_sec: float = 0.200,
        sub_steps: int = 1,
    ) -> Tuple[TurnResult, YokedActionRecord]:
        """
        Executes a turn on the yoked replica:
        1. Steps the yoked replica with input_event (matching active exposure).
        2. Injects the externally replayed active_record into yoked_ledger.
        3. Enforces fail-closed validation of exposure hash, virtual time, and action hash.
        """
        results = self.manager.step_turn(
            {self.yoked_replica.replica_id: input_event},
            dt_sec=dt_sec,
            sub_steps=sub_steps,
        )
        turn_res = results[self.yoked_replica.replica_id]

        yok_exp_hash = turn_res.exposure_record.compute_exposure_hash()

        # Enforce fail-closed matching
        if abs(turn_res.virtual_time_sec - active_record.virtual_time_sec) > 1e-9:
            raise VirtualTimeMismatchError(
                f"Virtual time drift: active={active_record.virtual_time_sec:.6f}, "
                f"yoked={turn_res.virtual_time_sec:.6f}"
            )

        if yok_exp_hash != active_record.exposure_hash:
            raise ExposureMismatchError(
                f"Exposure mismatch on turn {turn_res.turn_index}: "
                f"active={active_record.exposure_hash}, yoked={yok_exp_hash}"
            )

        yoked_record = self.yoked_ledger.record_yoked_replay(
            active_record=active_record,
            yoked_replica_id=self.yoked_replica.replica_id,
            turn_index=turn_res.turn_index,
            virtual_time_sec=turn_res.virtual_time_sec,
            yoked_state_fingerprint=turn_res.state_fingerprint,
            yoked_exposure_hash=yok_exp_hash,
        )

        return turn_res, yoked_record

    def step_paired_turn(
        self,
        input_event: InputEvent,
        decision_fn: Callable[[ResearchReplica, TurnResult], Dict[str, Any]],
        dt_sec: float = 0.200,
        sub_steps: int = 1,
    ) -> Tuple[TurnResult, TurnResult, YokedActionRecord, YokedActionRecord]:
        """
        Convenience method executing a synchronized paired turn across both replicas:
        Active generates endogenous action; Yoked receives identical exposure and externally replayed action.
        """
        res_act, rec_act = self.execute_active_turn(
            input_event=input_event,
            decision_fn=decision_fn,
            dt_sec=dt_sec,
            sub_steps=sub_steps,
        )
        res_yok, rec_yok = self.execute_yoked_turn(
            input_event=input_event,
            active_record=rec_act,
            dt_sec=dt_sec,
            sub_steps=sub_steps,
        )
        return res_act, res_yok, rec_act, rec_yok

    def audit_contingency(self) -> ContingencyAuditReport:
        """
        Runs the full ActionContingencyValidator audit across active and yoked ledgers.
        """
        return ActionContingencyValidator.validate_pairing(
            active_replica=self.active_replica,
            yoked_replica=self.yoked_replica,
            active_ledger=self.active_ledger,
            yoked_ledger=self.yoked_ledger,
        )
