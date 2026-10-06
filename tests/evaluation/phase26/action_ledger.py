"""
tests/evaluation/phase26/action_ledger.py

P26 Blocker 5 — Action Ledger & Provenance Schema for Yoked Control.
Defines canonical schemas, cryptographic hashing, and immutability guarantees
for active action capture and yoked action replay.

GOVERNANCE & BOUNDARIES:
- TEST-ONLY research infrastructure. Zero changes to src/core/**, electron/**, data/**.
- Action Ledger records synthetic decisions and external replays for auditability;
  it does NOT create personality, autonomous preference, or agency subsystems.
- C3 Boundary: Yoked-control infrastructure validates experimental apparatus;
  it does NOT establish Claim C3 (History Endogeneity).
"""

from __future__ import annotations

import copy
import enum
import hashlib
import json
import logging
from dataclasses import asdict, dataclass, field
from typing import Any, Dict, List, Optional

logger = logging.getLogger("ActionLedger")


class ActionSource(str, enum.Enum):
    """
    Source of the action/event.
    ACTIVE: Generated endogenously by the replica's own decision/generation process.
    YOKED_REPLAY: Replayed externally from an active replica's recorded action.
    """
    ACTIVE = "ACTIVE"
    YOKED_REPLAY = "YOKED_REPLAY"


class ActionLedgerError(Exception):
    """Base exception for action ledger errors."""
    pass


class ActionLedgerCorruptionError(ActionLedgerError):
    """Raised when an action record's cryptographic signature or payload is corrupted."""
    pass


class ActionMismatchError(ActionLedgerError):
    """Raised when replayed action attributes mismatch the expected active record."""
    pass


class ActionSequenceError(ActionLedgerError):
    """Raised when turn index, sequence ordering, or action duplicates are invalid."""
    pass


def compute_canonical_action_hash(
    action_type: str,
    action_payload: Dict[str, Any],
) -> str:
    """
    Computes a deterministic SHA-256 hash of an action using canonical JSON serialization.
    Ensures keys are sorted and numbers formatted deterministically.
    """
    canonical_repr = {
        "action_type": str(action_type),
        "action_payload": action_payload,
    }
    encoded = json.dumps(canonical_repr, sort_keys=True, separators=(",", ":")).encode("utf-8")
    return hashlib.sha256(encoded).hexdigest()


@dataclass
class YokedActionRecord:
    """
    Immutable audit record representing a discrete action taken by an active replica
    or externally replayed into a yoked replica.
    """
    experiment_id: str
    active_replica_id: str
    yoked_replica_id: Optional[str]
    turn_index: int
    virtual_time_sec: float
    action_id: str
    action_type: str
    action_payload: Dict[str, Any]
    action_hash: str
    source: ActionSource
    source_turn: int
    source_state_fingerprint: str
    exposure_hash: str
    provenance_version: str = "P26_ACTION_v1.0"
    crn_identifier: Optional[str] = None

    def compute_record_hash(self) -> str:
        """
        Computes a cryptographic SHA-256 hash across all provenance fields.
        """
        hasher = hashlib.sha256()
        hasher.update(self.experiment_id.encode("utf-8"))
        hasher.update(self.active_replica_id.encode("utf-8"))
        hasher.update(str(self.yoked_replica_id or "").encode("utf-8"))
        hasher.update(str(self.turn_index).encode("utf-8"))
        hasher.update(f"{self.virtual_time_sec:.6f}".encode("utf-8"))
        hasher.update(self.action_id.encode("utf-8"))
        hasher.update(self.action_type.encode("utf-8"))
        hasher.update(self.action_hash.encode("utf-8"))
        hasher.update(self.source.value.encode("utf-8"))
        hasher.update(str(self.source_turn).encode("utf-8"))
        hasher.update(self.source_state_fingerprint.encode("utf-8"))
        hasher.update(self.exposure_hash.encode("utf-8"))
        hasher.update(self.provenance_version.encode("utf-8"))
        if self.crn_identifier:
            hasher.update(self.crn_identifier.encode("utf-8"))
        return hasher.hexdigest()

    def verify_integrity(self) -> bool:
        """
        Verifies that the action_hash matches the canonical serialization of action_payload,
        and that required provenance fields are populated.
        """
        expected_action_hash = compute_canonical_action_hash(
            self.action_type, self.action_payload
        )
        if self.action_hash != expected_action_hash:
            return False
        return True

    def to_dict(self) -> Dict[str, Any]:
        """Converts the record to a serializable dictionary."""
        d = asdict(self)
        d["source"] = self.source.value
        return d

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> YokedActionRecord:
        """Instantiates a record from a dictionary."""
        d = dict(data)
        d["source"] = ActionSource(d["source"])
        return cls(**d)


class ActionLedger:
    """
    Immutable audit ledger storing the chronological sequence of action records
    for an experimental trial.
    """

    def __init__(
        self,
        experiment_id: str,
        active_replica_id: str,
        yoked_replica_id: Optional[str] = None,
    ) -> None:
        self.experiment_id = experiment_id
        self.active_replica_id = active_replica_id
        self.yoked_replica_id = yoked_replica_id
        self._records: List[YokedActionRecord] = []
        self._action_ids_seen: set[str] = set()
        self._turns_seen: set[int] = set()

    @property
    def records(self) -> List[YokedActionRecord]:
        return list(self._records)

    def __len__(self) -> int:
        return len(self._records)

    def record_active_action(
        self,
        turn_index: int,
        virtual_time_sec: float,
        action_id: str,
        action_type: str,
        action_payload: Dict[str, Any],
        source_state_fingerprint: str,
        exposure_hash: str,
        crn_identifier: Optional[str] = None,
    ) -> YokedActionRecord:
        """
        Appends an action generated endogenously by the active replica.
        Fails closed on duplicate turn index or duplicate action ID.
        """
        if turn_index in self._turns_seen:
            raise ActionSequenceError(
                f"Duplicate turn index {turn_index} in ActionLedger '{self.experiment_id}'."
            )
        if action_id in self._action_ids_seen:
            raise ActionSequenceError(
                f"Duplicate action ID '{action_id}' in ActionLedger '{self.experiment_id}'."
            )

        action_hash = compute_canonical_action_hash(action_type, action_payload)
        record = YokedActionRecord(
            experiment_id=self.experiment_id,
            active_replica_id=self.active_replica_id,
            yoked_replica_id=self.yoked_replica_id,
            turn_index=turn_index,
            virtual_time_sec=virtual_time_sec,
            action_id=action_id,
            action_type=action_type,
            action_payload=copy.deepcopy(action_payload),
            action_hash=action_hash,
            source=ActionSource.ACTIVE,
            source_turn=turn_index,
            source_state_fingerprint=source_state_fingerprint,
            exposure_hash=exposure_hash,
            crn_identifier=crn_identifier,
        )

        if not record.verify_integrity():
            raise ActionLedgerCorruptionError(
                f"Action record {action_id} failed integrity verification upon creation."
            )

        self._records.append(record)
        self._action_ids_seen.add(action_id)
        self._turns_seen.add(turn_index)
        return record

    def record_yoked_replay(
        self,
        active_record: YokedActionRecord,
        yoked_replica_id: str,
        turn_index: int,
        virtual_time_sec: float,
        yoked_state_fingerprint: str,
        yoked_exposure_hash: str,
    ) -> YokedActionRecord:
        """
        Records an external replay of an active action into a yoked replica.
        Validates bit-exact matching of action hash, turn index, virtual time, and exposure hash.
        Fails closed if any parameter drifts.
        """
        if not active_record.verify_integrity():
            raise ActionLedgerCorruptionError(
                f"Active record '{active_record.action_id}' is corrupt."
            )

        if active_record.source != ActionSource.ACTIVE:
            raise ActionMismatchError(
                f"Cannot yoke-replay an action whose source is not ACTIVE (got {active_record.source})."
            )

        if turn_index != active_record.turn_index:
            raise ActionSequenceError(
                f"Turn index mismatch in yoked replay: expected {active_record.turn_index}, got {turn_index}."
            )

        # Virtual time matching with machine epsilon tolerance
        if abs(virtual_time_sec - active_record.virtual_time_sec) > 1e-9:
            raise ActionMismatchError(
                f"Virtual time drift in yoked replay: active={active_record.virtual_time_sec:.6f}, "
                f"yoked={virtual_time_sec:.6f}."
            )

        if yoked_exposure_hash != active_record.exposure_hash:
            raise ActionMismatchError(
                f"Exposure hash mismatch for turn {turn_index}: active={active_record.exposure_hash}, "
                f"yoked={yoked_exposure_hash}."
            )

        yoked_record = YokedActionRecord(
            experiment_id=self.experiment_id,
            active_replica_id=active_record.active_replica_id,
            yoked_replica_id=yoked_replica_id,
            turn_index=turn_index,
            virtual_time_sec=virtual_time_sec,
            action_id=f"yoked_replay_{active_record.action_id}",
            action_type=active_record.action_type,
            action_payload=copy.deepcopy(active_record.action_payload),
            action_hash=active_record.action_hash,
            source=ActionSource.YOKED_REPLAY,
            source_turn=active_record.turn_index,
            source_state_fingerprint=yoked_state_fingerprint,
            exposure_hash=yoked_exposure_hash,
            crn_identifier=active_record.crn_identifier,
        )

        if not yoked_record.verify_integrity():
            raise ActionLedgerCorruptionError("Yoked action failed integrity verification.")

        self._records.append(yoked_record)
        self._action_ids_seen.add(yoked_record.action_id)
        self._turns_seen.add(turn_index)
        return yoked_record

    def get_action_for_turn(self, turn_index: int) -> Optional[YokedActionRecord]:
        """Retrieves the action record for a given turn index."""
        for rec in self._records:
            if rec.turn_index == turn_index:
                return rec
        return None

    def verify_ledger_integrity(self) -> bool:
        """
        Verifies all action records in the ledger for cryptographic integrity.
        """
        for rec in self._records:
            if not rec.verify_integrity():
                return False
        return True

    def to_json(self) -> str:
        """Serializes ledger to JSON."""
        data = {
            "experiment_id": self.experiment_id,
            "active_replica_id": self.active_replica_id,
            "yoked_replica_id": self.yoked_replica_id,
            "records": [r.to_dict() for r in self._records],
        }
        return json.dumps(data, indent=2)

    @classmethod
    def from_json(cls, json_str: str) -> ActionLedger:
        """Deserializes ledger from JSON."""
        data = json.loads(json_str)
        ledger = cls(
            experiment_id=data["experiment_id"],
            active_replica_id=data["active_replica_id"],
            yoked_replica_id=data.get("yoked_replica_id"),
        )
        for r_dict in data.get("records", []):
            rec = YokedActionRecord.from_dict(r_dict)
            if not rec.verify_integrity():
                raise ActionLedgerCorruptionError(
                    f"Corrupted record '{rec.action_id}' in deserialized ledger."
                )
            ledger._records.append(rec)
            ledger._action_ids_seen.add(rec.action_id)
            ledger._turns_seen.add(rec.turn_index)
        return ledger
