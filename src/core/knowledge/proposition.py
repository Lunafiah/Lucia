"""
src/core/knowledge/proposition.py

Canonical Proposition, Concept, Relation, and Provenance models for
Phase 16 production Knowledge Subsystem.
"""

from __future__ import annotations

import time
from dataclasses import asdict, dataclass, field
from enum import Enum
from typing import Any, Dict, List, Optional, Tuple


class ProvenanceType(str, Enum):
    """
    Eight-state provenance classification for all knowledge items.
    Enforces epistemic accountability for stored propositions.
    """
    USER_STATED = "USER_STATED"      # Stated directly by user
    OBSERVED = "OBSERVED"            # Sensed directly from system/telemetry
    LLM_PROPOSED = "LLM_PROPOSED"    # Proposed by LLM; candidate unverified
    INFERRED = "INFERRED"            # Inferred via associative/probabilistic logic
    DERIVED = "DERIVED"              # Formally deduced via rule-based derivation
    VERIFIED = "VERIFIED"            # Confirmed via external ground truth
    UNCERTAIN = "UNCERTAIN"          # Conflicting or insufficient evidence
    CONTRADICTED = "CONTRADICTED"    # Explicitly refuted by newer validated fact


@dataclass
class Proposition:
    """
    Atomic unit of factual knowledge represented as an explicit (Subject, Predicate, Object) tuple.
    Does not rely on unstructured natural language sentences for internal representation.
    """
    id: str
    subject: str
    predicate: str
    object: str
    confidence: float                  # Calibrated confidence in [0.0, 1.0]
    provenance: ProvenanceType
    evidence_ids: List[str] = field(default_factory=list)
    created_at: float = field(default_factory=time.time)
    valid: bool = True                 # Invalidation flag for belief revision
    superseded_by: Optional[str] = None

    def to_tuple(self) -> Tuple[str, str, str]:
        return (self.subject, self.predicate, self.object)

    def to_dict(self) -> Dict[str, Any]:
        d = asdict(self)
        d["provenance"] = self.provenance.value
        return d

    @classmethod
    def from_dict(cls, d: Dict[str, Any]) -> "Proposition":
        d_copy = d.copy()
        d_copy["provenance"] = ProvenanceType(d_copy["provenance"])
        return cls(**d_copy)


@dataclass
class Concept:
    """
    Explicit conceptual entity with domain classification, properties, and relations.
    """
    id: str
    name: str
    domain: str
    definition: str
    properties: Dict[str, Any] = field(default_factory=dict)
    relations: Dict[str, List[str]] = field(default_factory=dict)  # relation_type -> list of concept_ids

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)

    @classmethod
    def from_dict(cls, d: Dict[str, Any]) -> "Concept":
        return cls(**d)


@dataclass
class InferenceRule:
    """
    Symbolic deduction rule of the form:
      IF Antecedents THEN Consequent
    """
    id: str
    name: str
    domain: str
    antecedents: List[Tuple[str, str, str]]   # Patterns with variable placeholders like "?x"
    consequent_pattern: Tuple[str, str, str]  # Pattern generating the new proposition
    confidence_decay: float = 0.95           # Confidence multiplier on derived conclusion

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)

    @classmethod
    def from_dict(cls, d: Dict[str, Any]) -> "InferenceRule":
        return cls(**d)
