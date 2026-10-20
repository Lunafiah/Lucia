"""
src/core/language/adapter/gate.py

Language Ingress & Egress Gates for Phase 23-F.

Architectural Purpose:
    Acts as the perimeter firewall around the Cognitive Core and Semantic Fortifier.
    
    Ingress:
    - Enforces language admission policy: strictly vi/en/ja.
    - Rejects all unsupported languages (e.g. fr, de, zh, es, ru) before they can
      reach the Cognitive Core or Semantic Fortification.
    - Audits emitted SemanticGraph for substrate purity (no surface tokens, no grammar rules).
    
    Egress:
    - Enforces that realization only proceeds to officially admitted target languages.
    - Rejects attempts to realize into unsupported languages.
"""

from __future__ import annotations

import logging
import re
import time
from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Dict, List, Optional, Sequence, Set, Tuple

from src.core.cognition.contract.epistemic import EpistemicStatus
from src.core.knowledge.fortification import EpistemicState, SemanticGraph
from src.core.language.adapter.contracts import (
    SUPPORTED_LANGUAGES,
    CausalRelation,
    CertificationResult,
    EgressGateBlockedError,
    EpistemicEscalationError,
    EpistemicLeakageError,
    IngressCandidateAssertion,
    IngressGateBlockedError,
    IngressSourceClass,
    ParseResult,
    QualifiedLogicalAssertion,
    RealizeResult,
    RetractionDirective,
    SubstrateViolationError,
)
from src.core.language.adapter.registry import LanguageDriverRegistry

logger = logging.getLogger(__name__)


class GateVerdict(str, Enum):
    """Verdict of ingress or egress language admission evaluation."""
    ADMITTED = "ADMITTED"
    BLOCKED = "BLOCKED"


@dataclass(frozen=True)
class GateReport:
    """Report summarizing gate evaluation."""
    verdict: GateVerdict
    language: str
    reason: Optional[str] = None
    timestamp: float = field(default_factory=time.time)


class LanguageIngressGate:
    """
    Perimeter ingress firewall protecting the Cognitive Core and Semantic Substrate.
    
    Guarantees:
    1. Zero ingress for unsupported languages (fr, de, zh, etc.).
    2. Substrate purity validation: checks that graphs emitted by language drivers
       contain no raw text tokens, grammar rules, or ungrounded bindings.
    """

    def __init__(self, admitted_languages: Set[str] = SUPPORTED_LANGUAGES) -> None:
        self._admitted_languages = frozenset(l.lower().strip() for l in admitted_languages)

    def evaluate_language(self, lang: str) -> GateReport:
        """
        Evaluate if a language code is admitted through the ingress perimeter.
        
        Args:
            lang: Language code.
            
        Returns:
            GateReport with ADMITTED or BLOCKED verdict.
        """
        norm_lang = lang.strip().lower()
        if norm_lang in self._admitted_languages:
            return GateReport(verdict=GateVerdict.ADMITTED, language=norm_lang)
        
        reason = (
            f"Language '{norm_lang}' is not admitted by Lucia Ingress Policy. "
            f"Only {sorted(self._admitted_languages)} are permitted into Core."
        )
        logger.warning("Ingress gate blocked language: %s", norm_lang)
        return GateReport(verdict=GateVerdict.BLOCKED, language=norm_lang, reason=reason)

    def admit_and_parse(
        self,
        text: str,
        lang: str,
        registry: LanguageDriverRegistry,
        session_id: str = "session:default",
        turn_id: str = "turn:0",
    ) -> ParseResult:
        """
        Intercept input, enforce language admission, and parse via registered driver.
        
        Args:
            text: Surface natural language text.
            lang: Language code.
            registry: Driver registry.
            session_id: Session identifier.
            turn_id: Conversational turn identifier.
            
        Returns:
            ParseResult containing pure SemanticGraph.
            
        Raises:
            IngressGateBlockedError: If language is not in admitted set.
            SubstrateViolationError: If parsed graph violates substrate purity.
            EpistemicLeakageError: If epistemic states are malformed.
        """
        gate_report = self.evaluate_language(lang)
        if gate_report.verdict == GateVerdict.BLOCKED:
            raise IngressGateBlockedError(gate_report.reason or f"Blocked language: {lang}")

        driver = registry.get_driver(gate_report.language)
        parse_result = driver.parse_to_substrate(
            text=text,
            lang=gate_report.language,
            session_id=session_id,
            turn_id=turn_id,
        )

        # Substrate Purity & Epistemic Verification
        self._verify_substrate_purity(parse_result.graph, gate_report.language)

        return parse_result

    def _verify_substrate_purity(self, graph: SemanticGraph, source_lang: str) -> None:
        """
        Verify that the graph emitted by the adapter adheres to substrate neutrality:
        - No natural language word tokens in node IDs or concept symbols.
        - Epistemic states are valid.
        - UNKNOWN nodes are strictly preserved as EpistemicState.UNKNOWN.
        """
        # Forbidden surface patterns: e.g. token:word, pos:NN, lang prefixes inside concepts
        forbidden_pattern = re.compile(r"^(token:|word:|pos:|tag:)", re.IGNORECASE)

        for node_id, node in graph.nodes.items():
            if forbidden_pattern.match(node_id):
                raise SubstrateViolationError(
                    f"Substrate purity violated: node ID '{node_id}' contains surface token prefix"
                )
            if forbidden_pattern.match(node.concept_symbol):
                raise SubstrateViolationError(
                    f"Substrate purity violated: concept symbol '{node.concept_symbol}' contains surface token prefix"
                )

            # Epistemic integrity check
            if not isinstance(node.epistemic_state, EpistemicState):
                raise EpistemicLeakageError(
                    f"Invalid epistemic state on node '{node_id}': {node.epistemic_state}"
                )

            # UNKNOWN must not be resolved to concrete known entities
            if node.epistemic_state == EpistemicState.UNKNOWN:
                if node.concept_symbol in ("e:lucia", "e:user", "ent:lucia", "ent:user"):
                    raise EpistemicLeakageError(
                        f"Epistemic violation: UNKNOWN node '{node_id}' was illegally bound to concrete '{node.concept_symbol}'"
                    )

    def certify_candidate_assertion(
        self,
        candidate: IngressCandidateAssertion,
        confidence: float = 1.0,
    ) -> Tuple[QualifiedLogicalAssertion, Optional[RetractionDirective]]:
        """
        Certify an untrusted IngressCandidateAssertion into a QualifiedLogicalAssertion (ADR-038).

        Enforces non-escalation invariants:
        1. Invariant NEG-02: Continuous perceptual confidence c >= theta NEVER asserts FACT.
        2. F15 Anti-Echo Defense: Assistant CONFIRMED_ECHO is assigned EpistemicStatus.UNKNOWN.
        3. User Correction: CORRECTED_NEGATION outputs polarity=False and emits RetractionDirective.
        4. User Open Answer / Spontaneous: SUPPLIED_ANSWER and SPONTANEOUS are certified as FACT.
        5. Inferred Admissibility: DERIVED requires supporting premises and rule ID.
        6. Untrusted Self-Assertion: Candidate assertions cannot specify their own epistemic_status.
        """
        if not isinstance(candidate, IngressCandidateAssertion):
            raise EpistemicLeakageError(
                f"Candidate must be an instance of IngressCandidateAssertion, got {type(candidate).__name__}"
            )

        assigned_polarity: bool = candidate.polarity
        directive: Optional[RetractionDirective] = None

        # Invariant NEG-02: Continuous confidence cannot assert discrete FACT.
        # Scalar confidence represents measurement reliability or sensor SNR, not ontological proof.
        # Any perceptual input or confidence < 1.0 is strictly assigned UNKNOWN.
        if candidate.source_class == IngressSourceClass.PERCEPTUAL or confidence < 1.0:
            assigned_status = EpistemicStatus.UNKNOWN
        elif candidate.source_class == IngressSourceClass.DERIVED:
            if not candidate.supporting_premise_ids or candidate.rule_id == 0:
                raise EpistemicEscalationError(
                    "DERIVED candidate proposition lacks required supporting premises or rule ID"
                )
            assigned_status = EpistemicStatus.INFERRED
        elif candidate.source_class == IngressSourceClass.USER_DISCOURSE:
            if candidate.causal_relation == CausalRelation.CONFIRMED_ECHO:
                # F15 Anti-Echo Defense: Assistant echo cannot become external FACT
                assigned_status = EpistemicStatus.UNKNOWN
            elif candidate.causal_relation == CausalRelation.CORRECTED_NEGATION:
                assigned_status = EpistemicStatus.FACT
                assigned_polarity = False
                if candidate.antecedent_term_id > 0:
                    directive = RetractionDirective(
                        target_term_id=candidate.antecedent_term_id,
                        reason="USER_CORRECTED_NEGATION",
                    )
            elif candidate.causal_relation in (
                CausalRelation.SPONTANEOUS,
                CausalRelation.SUPPLIED_ANSWER,
                CausalRelation.ELABORATED,
            ):
                assigned_status = EpistemicStatus.FACT
            else:
                assigned_status = EpistemicStatus.FACT
        elif candidate.source_class == IngressSourceClass.MEMORY:
            assigned_status = EpistemicStatus.FACT
        else:
            assigned_status = EpistemicStatus.UNKNOWN

        qualified = QualifiedLogicalAssertion(
            predicate_id=candidate.predicate_id,
            arg0_id=candidate.arg0_id,
            arg1_id=candidate.arg1_id,
            arg2_id=candidate.arg2_id,
            polarity=assigned_polarity,
            scope_id=candidate.scope_id,
            epistemic_status=assigned_status,
            causal_relation=candidate.causal_relation,
            antecedent_term_id=candidate.antecedent_term_id,
            rule_id=candidate.rule_id,
            supporting_premise_ids=candidate.supporting_premise_ids,
        )
        return qualified, directive

    def certify_candidates(
        self,
        candidates: Sequence[IngressCandidateAssertion],
        confidence: float = 1.0,
    ) -> CertificationResult:
        """
        Certify a sequence of candidate assertions.
        """
        assertions: List[QualifiedLogicalAssertion] = []
        retractions: List[RetractionDirective] = []

        for cand in candidates:
            qualified, directive = self.certify_candidate_assertion(cand, confidence=confidence)
            assertions.append(qualified)
            if directive is not None:
                retractions.append(directive)

        return CertificationResult(
            assertions=tuple(assertions),
            retraction_directives=tuple(retractions),
        )

    def attribute_causal_relation(
        self,
        has_denial: bool = False,
        has_affirmation: bool = False,
        has_novel_content: bool = False,
        discourse_state: Optional[Any] = None,
    ) -> Tuple[CausalRelation, int]:
        """
        Attribute causal relation and antecedent term ID for a proposition based on discourse state.
        """
        seed_id = getattr(discourse_state, "active_assistant_seed_term_id", 0) if discourse_state else 0
        inquiry_type = getattr(discourse_state, "inquiry_type", None) if discourse_state else None
        unresolved = getattr(discourse_state, "unresolved_expectation", None) if discourse_state else None

        # Closed assistant inquiry with active seed
        if seed_id > 0 and inquiry_type == "CLOSED":
            if has_denial:
                return CausalRelation.CORRECTED_NEGATION, seed_id
            if has_affirmation and has_novel_content:
                return CausalRelation.ELABORATED, seed_id
            if has_affirmation:
                return CausalRelation.CONFIRMED_ECHO, seed_id
            if has_novel_content:
                return CausalRelation.ELABORATED, seed_id

        # Open inquiry response
        if inquiry_type == "OPEN" or unresolved == "USER_RESPONSE_EXPECTED":
            if has_novel_content or has_affirmation or not has_denial:
                return CausalRelation.SUPPLIED_ANSWER, seed_id

        return CausalRelation.SPONTANEOUS, 0


class LanguageEgressGate:
    """
    Perimeter egress firewall controlling realization from the Semantic Substrate.
    
    Guarantees:
    1. Only admitted target languages ('en', 'vi', 'ja') can receive realized output.
    2. Blocks requests to realize into unadmitted languages.
    """

    def __init__(self, admitted_languages: Set[str] = SUPPORTED_LANGUAGES) -> None:
        self._admitted_languages = frozenset(l.lower().strip() for l in admitted_languages)

    def evaluate_target_language(self, lang: str) -> GateReport:
        """Check if target language is admitted for egress."""
        norm_lang = lang.strip().lower()
        if norm_lang in self._admitted_languages:
            return GateReport(verdict=GateVerdict.ADMITTED, language=norm_lang)
        
        reason = (
            f"Target language '{norm_lang}' is not admitted by Lucia Egress Policy. "
            f"Only {sorted(self._admitted_languages)} are permitted for realization."
        )
        logger.warning("Egress gate blocked target language: %s", norm_lang)
        return GateReport(verdict=GateVerdict.BLOCKED, language=norm_lang, reason=reason)

    def admit_and_realize(
        self,
        graph: SemanticGraph,
        target_lang: str,
        registry: LanguageDriverRegistry,
    ) -> RealizeResult:
        """
        Enforce egress gating and realize SemanticGraph into target natural language.
        
        Args:
            graph: Language-independent SemanticGraph.
            target_lang: Desired surface language.
            registry: Driver registry.
            
        Returns:
            RealizeResult with surface text.
            
        Raises:
            EgressGateBlockedError: If target language is unsupported.
        """
        gate_report = self.evaluate_target_language(target_lang)
        if gate_report.verdict == GateVerdict.BLOCKED:
            raise EgressGateBlockedError(gate_report.reason or f"Blocked target language: {target_lang}")

        driver = registry.get_driver(gate_report.language)
        return driver.realize_from_substrate(graph, gate_report.language)
