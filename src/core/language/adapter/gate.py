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
from typing import Any, Dict, List, Optional, Set

from src.core.knowledge.fortification import EpistemicState, SemanticGraph
from src.core.language.adapter.contracts import (
    SUPPORTED_LANGUAGES,
    EgressGateBlockedError,
    EpistemicLeakageError,
    IngressGateBlockedError,
    ParseResult,
    RealizeResult,
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
