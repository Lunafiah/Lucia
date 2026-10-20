"""
src/core/language/adapter/contracts.py

Language Adapter Boundary & Semantic Substrate Contract (Phase 23-F).

Architectural Contract:
    Surface Language (EN, VI, JA)
          ↓
    Language Ingress Gate (strict gating: {en, vi, ja})
          ↓
    Language Adapter (ParseToSubstrate)
          ↓
    Language-independent Semantic Representation (SemanticGraph)
          ↓
    Cognitive Core / Semantic Fortification (P23-E)
          ↓
    Language Egress Gate (RealizeFromSubstrate)
          ↓
    Surface Language Output

Invariants:
    1. Language Independence: SemanticGraph contains ZERO natural-language tokens,
       grammar rules, or language-specific branching.
    2. Epistemic Preservation: UNKNOWN, AMBIGUOUS, INFERRED states must be preserved.
       Fortification and Adapters MUST NOT auto-bind UNKNOWN or arbitrarily disambiguate.
    3. Strict Ingress/Egress Gating: Only 'en', 'vi', 'ja' are admitted.
       All other languages are blocked at the perimeter.
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from enum import Enum, IntEnum
from typing import Any, Dict, List, Optional, Set, Tuple

from src.core.cognition.contract.epistemic import EpistemicStatus
from src.core.knowledge.fortification import (
    EpistemicState,
    ProvenanceRecord,
    ScopeBoundary,
    ScopeType,
    SemanticEdge,
    SemanticGraph,
    SemanticNode,
)

# Supported language codes (ISO 639-1)
SUPPORTED_LANGUAGES: frozenset[str] = frozenset({"en", "vi", "ja"})


class SupportedLanguage(str, Enum):
    """Enumeration of officially admitted languages in Project Lucia."""
    EN = "en"
    VI = "vi"
    JA = "ja"


# ── Exceptions ─────────────────────────────────────────────────────────────────

class LanguageAdapterError(Exception):
    """Base exception for all language adapter errors."""
    pass


class UnsupportedLanguageError(LanguageAdapterError):
    """Raised when an unadmitted language code is presented."""
    pass


class IngressGateBlockedError(LanguageAdapterError):
    """Raised when the ingress gate intercepts and rejects an unsupported language."""
    pass


class EgressGateBlockedError(LanguageAdapterError):
    """Raised when the egress gate intercepts and rejects an unsupported target language."""
    pass


class EpistemicLeakageError(LanguageAdapterError):
    """Raised when parsing or realization violates epistemic non-escalation invariants."""
    pass


class EpistemicEscalationError(LanguageAdapterError):
    """Raised when an ungrounded or untrusted candidate attempts to escalate epistemic authority (NEG-02)."""
    pass


class SubstrateViolationError(LanguageAdapterError):
    """Raised when natural language tokens or grammar rules contaminate the substrate."""
    pass


# ── Result & Report Data Structures ────────────────────────────────────────────

@dataclass(frozen=True)
class ParseResult:
    """
    Result of parsing surface language text into a SemanticGraph.
    
    Attributes:
        graph: The language-independent semantic graph.
        source_language: The ISO 639-1 language code of the input.
        coverage_score: Proportion of surface content represented in the graph [0.0, 1.0].
        unparsed_segments: Text fragments that could not be mapped to semantic concepts.
        epistemic_states_detected: Counts of epistemic states (FACT, INFERRED, AMBIGUOUS, UNKNOWN).
        metadata: Additional extraction and timing metadata.
    """
    graph: SemanticGraph
    source_language: str
    coverage_score: float
    unparsed_segments: Tuple[str, ...] = ()
    epistemic_states_detected: Dict[str, int] = field(default_factory=dict)
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass(frozen=True)
class RealizeResult:
    """
    Result of realizing a SemanticGraph into surface language text.
    
    Attributes:
        surface_text: The generated natural language output.
        target_language: The target ISO 639-1 language code.
        fidelity_score: Estimated preservation of graph information [0.0, 1.0].
        unrealized_nodes: IDs of nodes that could not be rendered in the surface text.
        metadata: Generation metadata (e.g. style, honorifics applied).
    """
    surface_text: str
    target_language: str
    fidelity_score: float
    unrealized_nodes: Tuple[str, ...] = ()
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass(frozen=True)
class CoverageReport:
    """
    Report detailing the lexical and structural coverage of surface text.
    
    Attributes:
        coverage_ratio: Proportion of input recognized [0.0, 1.0].
        recognized_tokens_count: Number of recognized input elements.
        total_tokens_count: Total number of input elements.
        unrecognized_segments: List of tokens or phrases with no substrate mapping.
    """
    coverage_ratio: float
    recognized_tokens_count: int
    total_tokens_count: int
    unrecognized_segments: Tuple[str, ...] = ()


# ── Abstract Base Interface ───────────────────────────────────────────────────

class LanguageAdapter(ABC):
    """
    Minimal contract for language-specific adapter drivers.
    
    All language-specific lexical knowledge, tokenization, morphology,
    classifiers, and honorific handling are strictly encapsulated here.
    The Cognitive Core and Semantic Fortifier have zero access to this logic.
    """

    @abstractmethod
    def can_handle_language(self, lang: str) -> bool:
        """
        Check if this driver can handle the given language code.
        
        Args:
            lang: ISO 639-1 language code.
            
        Returns:
            True if supported, False otherwise.
        """
        ...

    @abstractmethod
    def parse_to_substrate(
        self,
        text: str,
        lang: str,
        session_id: str = "session:default",
        turn_id: str = "turn:0",
    ) -> ParseResult:
        """
        Parse surface natural language text into a language-independent SemanticGraph.
        
        Must strictly preserve:
        - UNKNOWN referents without auto-binding to default entities.
        - AMBIGUOUS branches without speculative resolution.
        - INFERRED provenance and supporting premise links.
        
        Args:
            text: Surface natural language text.
            lang: Language code.
            session_id: Identifier for session provenance.
            turn_id: Identifier for conversational turn.
            
        Returns:
            ParseResult containing the resulting SemanticGraph and coverage metadata.
        """
        ...

    @abstractmethod
    def realize_from_substrate(
        self,
        graph: SemanticGraph,
        lang: str,
    ) -> RealizeResult:
        """
        Realize a language-independent SemanticGraph into surface natural language text.
        
        Must accurately reflect:
        - UNKNOWN arguments (e.g. passive or indefinite expression, never a fabricated name).
        - AMBIGUOUS nodes (e.g. expressing ambiguity or requesting clarification).
        
        Args:
            graph: Language-independent SemanticGraph.
            lang: Target language code.
            
        Returns:
            RealizeResult containing generated text and fidelity metrics.
        """
        ...

    @abstractmethod
    def validate_coverage(
        self,
        text: str,
        lang: str,
    ) -> CoverageReport:
        """
        Evaluate semantic coverage of surface input without mutating state.
        
        Args:
            text: Surface natural language text.
            lang: Language code.
            
        Returns:
            CoverageReport detailing coverage metrics.
        """
        ...


# ── ADR-038 Grounded Propositional Causal Ingress Contracts ────────────────────

class CausalRelation(IntEnum):
    """
    Ratified bounded vocabulary for F15 epistemic ingress causal links.
    """
    SPONTANEOUS = 1
    """User-authored content initiated without assistant prompt or topical seed."""

    SUPPLIED_ANSWER = 2
    """User-authored content answering an open assistant question (e.g. 'Where do you live?' -> 'Hanoi')."""

    CONFIRMED_ECHO = 3
    """User passively assenting to or repeating an assistant-seeded closed hypothesis. Downgraded to UNKNOWN."""

    CORRECTED_NEGATION = 4
    """User explicitly denying, correcting, or refuting an assistant-seeded closed hypothesis."""

    ELABORATED = 5
    """User confirming an assistant topic while supplying independent, novel evidential propositions."""


class IngressSourceClass(str, Enum):
    """
    Authority classes distinguishing epistemic origin of candidate assertions.
    """
    USER_DISCOURSE = "USER_DISCOURSE"
    PERCEPTUAL = "PERCEPTUAL"
    DERIVED = "DERIVED"
    MEMORY = "MEMORY"


@dataclass(frozen=True)
class IngressCandidateAssertion:
    """
    R4 Validated Minimal Epistemic Ingress Candidate Contract (ADR-038).
    Evaluated by Language Ingress Gate BEFORE admission into P23-H TermArena.
    NOTE: Does NOT contain epistemic_status (assigned only upon gate certification).
    """
    predicate_id: int
    arg0_id: int
    arg1_id: int = 0
    arg2_id: int = 0
    polarity: bool = True
    scope_id: int = 1
    source_class: IngressSourceClass = IngressSourceClass.USER_DISCOURSE
    causal_relation: CausalRelation = CausalRelation.SPONTANEOUS
    antecedent_term_id: int = 0
    rule_id: int = 0
    supporting_premise_ids: Tuple[int, ...] = ()


@dataclass(frozen=True)
class RetractionDirective:
    """
    Typed directive emitted by LanguageIngressGate when user negates an assistant hypothesis.
    Processed by CognitiveOrchestrator at Stage S10b via JTMS.retract_premise().
    """
    target_term_id: int
    reason: str = "USER_CORRECTED_NEGATION"


@dataclass(frozen=True)
class QualifiedLogicalAssertion:
    """
    Certified logical proposition emitted by LanguageIngressGate after epistemic verification.
    Ready for interning into TermArena and allocation of ProvenanceRecord.
    """
    predicate_id: int
    arg0_id: int
    arg1_id: int = 0
    arg2_id: int = 0
    polarity: bool = True
    scope_id: int = 1
    epistemic_status: EpistemicStatus = EpistemicStatus.FACT
    causal_relation: CausalRelation = CausalRelation.SPONTANEOUS
    antecedent_term_id: int = 0
    rule_id: int = 0
    supporting_premise_ids: Tuple[int, ...] = ()


@dataclass(frozen=True)
class CertificationResult:
    """
    Result of evaluating candidate assertions through the Epistemic Ingress Gate.
    """
    assertions: Tuple[QualifiedLogicalAssertion, ...] = ()
    retraction_directives: Tuple[RetractionDirective, ...] = ()

