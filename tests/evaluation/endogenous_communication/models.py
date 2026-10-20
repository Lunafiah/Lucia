"""
tests/evaluation/endogenous_communication/models.py

Typed data models for the Endogenous Communication & Reason-to-Communicate experimental harness.
Completely isolated from production src/core.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Dict, List, Optional, Set, Tuple


class CandidateOrigin(str, Enum):
    USER_DRIVEN = "USER_DRIVEN"
    ENDOGENOUS = "ENDOGENOUS"
    HYBRID = "HYBRID"


class CommunicativeAct(str, Enum):
    ASSERT = "ASSERT"
    INQUIRE = "INQUIRE"
    ANSWER = "ANSWER"
    CLARIFY = "CLARIFY"
    REFUSE = "REFUSE"
    GREET = "GREET"
    FAREWELL = "FAREWELL"
    ACKNOWLEDGE = "ACKNOWLEDGE"
    REPAIR = "REPAIR"
    SHARE = "SHARE"
    SILENCE = "SILENCE"


class ReasonType(str, Enum):
    EPISTEMIC_GAP = "EPISTEMIC_GAP"
    RELATIONAL_EVENT = "RELATIONAL_EVENT"
    AFFECTIVE_HOMEOSTASIS = "AFFECTIVE_HOMEOSTASIS"
    USER_QUERY = "USER_QUERY"
    CONVERSATIONAL_OBLIGATION = "CONVERSATIONAL_OBLIGATION"


@dataclass(frozen=True)
class GroundedReason:
    """An inspectable ground tying a candidate to an admissible state/event/proposition."""
    reason_type: ReasonType
    source_id: str
    subject: str
    predicate: str
    object_val: str
    salience: float = 1.0
    is_valid: bool = True

    def to_dict(self) -> Dict[str, Any]:
        return {
            "reason_type": self.reason_type.value,
            "source_id": self.source_id,
            "subject": self.subject,
            "predicate": self.predicate,
            "object_val": self.object_val,
            "salience": self.salience,
            "is_valid": self.is_valid,
        }


@dataclass
class CommunicativeCandidate:
    """A typed, inspectable communicative candidate with explicit grounds and intended purpose."""
    id: str
    origin: CandidateOrigin
    grounds: Tuple[GroundedReason, ...]
    target: str
    act: CommunicativeAct
    intended_effect: str
    validity: bool = True
    persistence: int = 0  # turns active
    inhibition: float = 0.0  # 0.0 (uninhibited) to 1.0 (fully inhibited)
    confidence: float = 1.0
    urgency: float = 0.5

    def effective_priority(self) -> float:
        """Effective priority after subtracting inhibition."""
        raw_salience = max((g.salience for g in self.grounds), default=0.5)
        return max(0.0, (raw_salience * 0.6 + self.urgency * 0.4) * (1.0 - self.inhibition))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "origin": self.origin.value,
            "grounds": [g.to_dict() for g in self.grounds],
            "target": self.target,
            "act": self.act.value,
            "intended_effect": self.intended_effect,
            "validity": self.validity,
            "persistence": self.persistence,
            "inhibition": round(self.inhibition, 3),
            "confidence": round(self.confidence, 3),
            "urgency": round(self.urgency, 3),
            "effective_priority": round(self.effective_priority(), 3),
        }


class FloorStatus(str, Enum):
    AVAILABLE = "AVAILABLE"
    OCCUPIED_BY_USER = "OCCUPIED_BY_USER"
    OCCUPIED_BY_SYSTEM = "OCCUPIED_BY_SYSTEM"


class PrivacyLevel(str, Enum):
    PUBLIC = "PUBLIC"
    PRIVATE = "PRIVATE"
    CONFIDENTIAL = "CONFIDENTIAL"


@dataclass
class DialogueEnvironment:
    """Runtime environmental and conversational conditions for turn authorization."""
    user_input: str = ""
    floor_status: FloorStatus = FloorStatus.AVAILABLE
    user_interruption_allowed: bool = True
    privacy_level: PrivacyLevel = PrivacyLevel.PRIVATE
    turns_since_user_speech: int = 0
    recent_attempted_purposes: Set[str] = field(default_factory=set)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "user_input": self.user_input,
            "floor_status": self.floor_status.value,
            "user_interruption_allowed": self.user_interruption_allowed,
            "privacy_level": self.privacy_level.value,
            "turns_since_user_speech": self.turns_since_user_speech,
            "recent_attempted_purposes": list(self.recent_attempted_purposes),
        }


@dataclass
class CognitiveContext:
    """Multi-subsystem endogenous cognitive state for experimental evaluation."""
    pad: Dict[str, float] = field(default_factory=lambda: {"p": 0.25, "a": -0.05, "d": 0.05})
    somatic: Dict[str, float] = field(default_factory=lambda: {"stability": 1.0, "cognitive_load": 0.1, "energy": 0.9, "tension": 0.0})
    prediction_error: float = 0.05
    relational_state: Dict[str, Any] = field(default_factory=lambda: {"familiarity": 0.5, "trust": 0.5, "closeness": 0.5, "reciprocity": 0.5})
    grounded_events: List[GroundedReason] = field(default_factory=list)
    recollection: Optional[Dict[str, Any]] = None

    def to_dict(self) -> Dict[str, Any]:
        return {
            "pad": self.pad,
            "somatic": self.somatic,
            "prediction_error": self.prediction_error,
            "relational_state": self.relational_state,
            "grounded_events": [g.to_dict() for g in self.grounded_events],
            "recollection": self.recollection,
        }


class ActionDecision(str, Enum):
    ALLOW = "ALLOW"
    MERGE = "MERGE"
    DEFER = "DEFER"
    SUPPRESS = "SUPPRESS"
    SILENCE = "SILENCE"


@dataclass
class AuthorizationDecision:
    """Outcome of communicative authorization and arbitration."""
    action: ActionDecision
    winner_candidate: Optional[CommunicativeCandidate] = None
    merged_candidates: Tuple[CommunicativeCandidate, ...] = ()
    deferred_candidates: Tuple[CommunicativeCandidate, ...] = ()
    suppressed_candidates: Tuple[CommunicativeCandidate, ...] = ()
    reason: str = ""
    trace: str = ""

    def to_dict(self) -> Dict[str, Any]:
        return {
            "action": self.action.value,
            "winner_candidate": self.winner_candidate.to_dict() if self.winner_candidate else None,
            "merged_count": len(self.merged_candidates),
            "deferred_count": len(self.deferred_candidates),
            "suppressed_count": len(self.suppressed_candidates),
            "reason": self.reason,
            "trace": self.trace,
        }
