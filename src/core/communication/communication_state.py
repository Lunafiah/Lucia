"""
src/core/communication/communication_state.py

Communication production state C_t and communicative intent models for Phase 16.
Enforces bounded parameters, strategy categorization, and 10D vector serialization.
"""

from __future__ import annotations

from dataclasses import asdict, dataclass, field
from enum import Enum
from typing import Any, Dict, List, Optional, Tuple

import numpy as np


class CommStrategy(str, Enum):
    """Discrete communicative strategies produced by CommunicationPolicy."""
    DIRECT_FACTUAL = "direct_factual"
    REASSURING_WARM = "reassuring_warm"
    ELABORATIVE_EXPLANATORY = "elaborative_explanatory"
    CONCISE_RESERVED = "concise_reserved"
    COLLABORATIVE_INQUIRING = "collaborative_inquiring"


class ResponseDepth(str, Enum):
    """
    Discrete presence & response depth levels produced by CommunicationPolicy.
    Authoritatively determines how much presence Lucia occupies in the conversational moment.
    """
    MINIMAL = "minimal"   # Immediate presence ping / brief greeting (e.g. "Em đây.")
    SHORT = "short"       # Concise direct answer / check-in / simple query (1-2 sentences)
    MEDIUM = "medium"     # Balanced explanation / concept / moderate narrative sharing
    DEEP = "deep"         # Structured in-depth explanation / technical analysis / multi-layered response


RESPONSE_DEPTH_BUDGET_MAP: Dict[ResponseDepth, Tuple[int, int]] = {
    ResponseDepth.MINIMAL: (5, 40),
    ResponseDepth.SHORT: (20, 100),
    ResponseDepth.MEDIUM: (80, 220),
    ResponseDepth.DEEP: (180, 500),
}


@dataclass
class CommIntent:
    """
    Formal representation of communicative semantic intent.
    Holds structured subject-predicate-object propositions, entities, and numeric values.
    """
    subject: str
    predicate: str
    object: str
    polarity: bool = True  # True = affirmative, False = negated
    named_entities: Dict[str, str] = field(default_factory=dict)
    numerical_values: Dict[str, float] = field(default_factory=dict)

    def canonical_triple(self) -> Tuple[str, str, str, bool]:
        return (self.subject, self.predicate, self.object, self.polarity)

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)

    @classmethod
    def from_dict(cls, d: Dict[str, Any]) -> "CommIntent":
        return cls(**d)


@dataclass
class CommunicationState:
    """
    Formal representation of communicative production state C_t.
    Holds 10 continuous modulation dimensions and selected communicative strategy,
    along with authoritative response depth and generation budget.
    """
    strategy: CommStrategy = CommStrategy.DIRECT_FACTUAL
    directness: float = 0.50                 # [0.10, 0.95] (1.0 = direct/unbuffered, 0.1 = cushioned)
    elaboration_depth: float = 0.50          # [0.10, 1.00] (0.1 = minimal, 1.0 = comprehensive)
    supportiveness: float = 0.30             # [0.00, 1.00] (0.0 = detached, 1.0 = warm reassuring)
    formality_score: float = 0.60            # [0.00, 1.00] (0.0 = intimate/informal, 1.0 = formal/distant)
    acknowledgement_level: float = 0.40      # [0.10, 1.00] (0.1 = straight to answer, 1.0 = grounded)
    question_frequency: float = 0.10         # [0.00, 1.00] (0.0 = declarative only, 1.0 = inquisitive)
    injected_pacing_latency_ms: float = 0.0  # [0.0, 1000.0] ms
    memory_context_ref: float = 0.0          # [0.00, 0.50]
    knowledge_context_ref: float = 0.0       # [0.00, 0.50]
    semantic_safe: bool = True
    provenance: str = "CommunicationPolicy/v1"
    response_depth: ResponseDepth = ResponseDepth.SHORT
    max_tokens_budget: int = 100

    @property
    def contextual_reference(self) -> float:
        """Sum of memory and knowledge contextual reference components in [0.0, 1.0]."""
        return min(1.0, self.memory_context_ref + self.knowledge_context_ref)

    def to_vector(self) -> np.ndarray:
        """Continuous parameter vector for mathematical and variance evaluation."""
        return np.array(
            [
                self.directness,
                self.elaboration_depth,
                self.supportiveness,
                self.formality_score,
                self.acknowledgement_level,
                self.question_frequency,
                self.injected_pacing_latency_ms / 1000.0,
                self.memory_context_ref,
                self.knowledge_context_ref,
                self.contextual_reference,
            ],
            dtype=np.float64,
        )

    def is_bounded(self) -> bool:
        """Verify parameters strictly conform to bounded domains."""
        if not (0.10 <= self.directness <= 0.95):
            return False
        if not (0.10 <= self.elaboration_depth <= 1.00):
            return False
        if not (0.00 <= self.supportiveness <= 1.00):
            return False
        if not (0.00 <= self.formality_score <= 1.00):
            return False
        if not (0.10 <= self.acknowledgement_level <= 1.00):
            return False
        if not (0.00 <= self.question_frequency <= 1.00):
            return False
        if not (0.0 <= self.injected_pacing_latency_ms <= 1000.0):
            return False
        if not (0.00 <= self.memory_context_ref <= 0.50):
            return False
        if not (0.00 <= self.knowledge_context_ref <= 0.50):
            return False
        if not (0.00 <= self.contextual_reference <= 1.00):
            return False
        if not isinstance(self.response_depth, ResponseDepth):
            return False
        if not (1 <= self.max_tokens_budget <= 2048):
            return False
        return True

    def to_dict(self) -> Dict[str, Any]:
        return {
            "strategy": self.strategy.value,
            "directness": float(self.directness),
            "elaboration_depth": float(self.elaboration_depth),
            "supportiveness": float(self.supportiveness),
            "formality_score": float(self.formality_score),
            "acknowledgement_level": float(self.acknowledgement_level),
            "question_frequency": float(self.question_frequency),
            "injected_pacing_latency_ms": float(self.injected_pacing_latency_ms),
            "memory_context_ref": float(self.memory_context_ref),
            "knowledge_context_ref": float(self.knowledge_context_ref),
            "contextual_reference": float(self.contextual_reference),
            "semantic_safe": bool(self.semantic_safe),
            "provenance": str(self.provenance),
            "response_depth": self.response_depth.value if hasattr(self.response_depth, "value") else str(self.response_depth),
            "max_tokens_budget": int(self.max_tokens_budget),
        }

    @classmethod
    def from_dict(cls, d: Dict[str, Any]) -> "CommunicationState":
        raw_depth = d.get("response_depth", ResponseDepth.SHORT.value)
        try:
            depth = ResponseDepth(raw_depth)
        except (ValueError, TypeError):
            depth = ResponseDepth.SHORT
        return cls(
            strategy=CommStrategy(d.get("strategy", CommStrategy.DIRECT_FACTUAL.value)),
            directness=float(d.get("directness", 0.5)),
            elaboration_depth=float(d.get("elaboration_depth", 0.5)),
            supportiveness=float(d.get("supportiveness", 0.3)),
            formality_score=float(d.get("formality_score", 0.6)),
            acknowledgement_level=float(d.get("acknowledgement_level", 0.4)),
            question_frequency=float(d.get("question_frequency", 0.1)),
            injected_pacing_latency_ms=float(d.get("injected_pacing_latency_ms", 0.0)),
            memory_context_ref=float(d.get("memory_context_ref", 0.0)),
            knowledge_context_ref=float(d.get("knowledge_context_ref", 0.0)),
            semantic_safe=bool(d.get("semantic_safe", True)),
            provenance=str(d.get("provenance", "from_dict")),
            response_depth=depth,
            max_tokens_budget=int(d.get("max_tokens_budget", 100)),
        )
