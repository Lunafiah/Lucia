"""
src/core/cognition/contract/condition.py

Phase 23-D: Minimal, immutable contract for UnresolvedCondition.
Enforces the 6 frozen fields, strict lifecycle transitions, and deterministic identity
mandated by DOC-P23D-ARCH-CONTRACT-R2-001 and DOC-P23D-IMP-SPEC-V1-001.

Strict Invariants:
1. Exactly six frozen fields: condition_id, condition_type, referent_key, status, resolution_source, epoch_created.
2. Zero speculative fields (no tension_weight, retry_count, priority, confidence, backoff).
3. Immutable instance semantics (frozen=True) with copy-on-write lifecycle transitions.
4. Fail-closed deserialization: malformed or incomplete records raise ValueError.
"""

from __future__ import annotations

import re
from dataclasses import asdict, dataclass, replace
from enum import Enum
from typing import Any, Dict


class ConditionType(str, Enum):
    """Categorical classification of an unresolved cognitive condition."""
    MISSING_PREMISE = "MISSING_PREMISE"
    CONTRADICTION = "CONTRADICTION"
    RELATIONAL_RUPTURE = "RELATIONAL_RUPTURE"


class ConditionStatus(str, Enum):
    """Lifecycle status of an unresolved cognitive condition."""
    ACTIVE = "ACTIVE"
    DEFERRED = "DEFERRED"
    SUPPRESSED = "SUPPRESSED"
    RESOLVED = "RESOLVED"


class ResolutionSource(str, Enum):
    """Authorized resolution boundary for resolving the condition."""
    INTERNAL_SEARCH = "INTERNAL_SEARCH"
    EXTERNAL_USER = "EXTERNAL_USER"
    SYSTEM_ENVIRONMENT = "SYSTEM_ENVIRONMENT"


# Pre-compiled regex for validating SHA-256 hex digest condition IDs
_SHA256_HEX_REGEX = re.compile(r"^[a-f0-9]{64}$")

# Set of permitted lifecycle transitions: (CurrentStatus, TargetStatus)
_PERMITTED_TRANSITIONS = {
    (ConditionStatus.ACTIVE, ConditionStatus.DEFERRED),
    (ConditionStatus.ACTIVE, ConditionStatus.SUPPRESSED),
    (ConditionStatus.ACTIVE, ConditionStatus.RESOLVED),
    (ConditionStatus.DEFERRED, ConditionStatus.ACTIVE),
    (ConditionStatus.DEFERRED, ConditionStatus.RESOLVED),
    (ConditionStatus.SUPPRESSED, ConditionStatus.DEFERRED),
    (ConditionStatus.SUPPRESSED, ConditionStatus.RESOLVED),
}


@dataclass(frozen=True)
class UnresolvedCondition:
    """
    Immutable primitive representing an unresolved epistemic gap, conflict,
    or relational condition persisting across turn and process boundaries.
    """
    condition_id: str
    condition_type: ConditionType
    referent_key: str
    status: ConditionStatus
    resolution_source: ResolutionSource
    epoch_created: int

    def __post_init__(self) -> None:
        if not isinstance(self.condition_id, str) or not _SHA256_HEX_REGEX.match(self.condition_id):
            raise ValueError(f"Invalid condition_id (must be 64-char SHA-256 hex): {self.condition_id}")
        if not isinstance(self.condition_type, ConditionType):
            raise ValueError(f"Invalid condition_type: {self.condition_type}")
        if not isinstance(self.referent_key, str) or not self.referent_key.strip():
            raise ValueError(f"referent_key must be non-empty string: {self.referent_key}")
        if not isinstance(self.status, ConditionStatus):
            raise ValueError(f"Invalid status: {self.status}")
        if not isinstance(self.resolution_source, ResolutionSource):
            raise ValueError(f"Invalid resolution_source: {self.resolution_source}")
        if not isinstance(self.epoch_created, int) or self.epoch_created < 0:
            raise ValueError(f"epoch_created must be a non-negative integer: {self.epoch_created}")

    def transition_to(self, new_status: ConditionStatus, reason: str = "") -> UnresolvedCondition:
        """
        Produce a new UnresolvedCondition with updated status via copy-on-write.
        Enforces permitted state machine transitions from P23-D Spec v1 §8.
        """
        if self.status == new_status:
            return self

        if (self.status, new_status) not in _PERMITTED_TRANSITIONS:
            raise ValueError(
                f"Illegal lifecycle transition from {self.status.value} to {new_status.value} "
                f"for condition {self.condition_id}."
            )

        return replace(self, status=new_status)

    def to_dict(self) -> Dict[str, Any]:
        """Serialize condition to primitive JSON-safe dictionary."""
        return {
            "condition_id": self.condition_id,
            "condition_type": self.condition_type.value,
            "referent_key": self.referent_key,
            "status": self.status.value,
            "resolution_source": self.resolution_source.value,
            "epoch_created": int(self.epoch_created),
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> UnresolvedCondition:
        """
        Deserialize and validate condition dictionary.
        Fails closed by raising ValueError if any required field is missing or malformed.
        """
        if not isinstance(data, dict):
            raise ValueError(f"Expected dict for UnresolvedCondition serialization, got {type(data).__name__}")

        required_fields = {
            "condition_id",
            "condition_type",
            "referent_key",
            "status",
            "resolution_source",
            "epoch_created",
        }
        missing = required_fields - set(data.keys())
        if missing:
            raise ValueError(f"Missing required fields for UnresolvedCondition: {sorted(missing)}")

        try:
            cond_type = ConditionType(data["condition_type"])
        except Exception as exc:
            raise ValueError(f"Invalid condition_type '{data.get('condition_type')}': {exc}") from exc

        try:
            status = ConditionStatus(data["status"])
        except Exception as exc:
            raise ValueError(f"Invalid status '{data.get('status')}': {exc}") from exc

        try:
            res_source = ResolutionSource(data["resolution_source"])
        except Exception as exc:
            raise ValueError(f"Invalid resolution_source '{data.get('resolution_source')}': {exc}") from exc

        try:
            epoch_val = int(data["epoch_created"])
        except Exception as exc:
            raise ValueError(f"Invalid epoch_created '{data.get('epoch_created')}': {exc}") from exc

        return cls(
            condition_id=str(data["condition_id"]),
            condition_type=cond_type,
            referent_key=str(data["referent_key"]),
            status=status,
            resolution_source=res_source,
            epoch_created=epoch_val,
        )


@dataclass(frozen=True)
class CommunicativeAffordance:
    """
    Structured downstream communicative affordance produced by endogenous cognition.
    Quarantined in _pending_communicative_affordance as contextual dialogue bias for the
    subsequent user turn; NEVER emitted autonomously.
    """
    condition_id: str
    target_predicate_id: int = 0
    arg0_id: int = 0
    reason_code: int = 1
    predicate: str = ""
    subject: str = ""
    object: str = ""
    resolution_source: ResolutionSource = ResolutionSource.EXTERNAL_USER


@dataclass(frozen=True)
class EndogenousTurnResult:
    """
    Consolidated outcome of an endogenous cognitive pass (process_endogenous).
    """
    success: bool
    condition_id: str
    final_status: ConditionStatus
    execution_time_s: float
    communicative_affordance: Optional[CommunicativeAffordance] = None
    detail: str = ""

