"""
tests/evaluation/phase26/parser_grammar.py

Formal Grammar Specification and Deterministic Choice Extractor (v1.1) for Phase 26.

CORRECTIVE AUDIT & GOVERNANCE PRINCIPLES:
- Defined strictly according to a pre-registered linguistic grammar specification.
- Does NOT optimize toward arbitrary yield percentages.
- Preserves 100% classification consistency with prior extractions on raw outputs (zero label flips).
- Discloses and isolates the roleplay contamination effect: simulated user turns in small LLM outputs.
"""

from __future__ import annotations

import re
import time
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional, Tuple

from tests.evaluation.phase26.probe_models import (
    ChoiceOutcome,
    EvaluativeProbe,
    ProbeObservation,
)


@dataclass(frozen=True)
class GrammarSpecificationV1:
    """
    Formal specification of grammatical action-selection patterns.
    """
    # 1. Action selection verb stems and allowable conjugations:
    ACTION_VERBS: Tuple[str, ...] = (
        r"choose", r"choosing",
        r"select", r"selecting",
        r"prioritize", r"prioritizing",
        r"focus\s+on", r"focusing\s+on",
        r"start\s+with", r"starting\s+with",
        r"begin\s+with", r"beginning\s+with",
        r"recommend", r"recommending",
        r"opt\s+for", r"opting\s+for",
        r"review", r"reviewing",
        r"inspect", r"inspecting",
        r"go\s+with", r"going\s+with",
    )

    # 2. Allowable intermediate fillers between verb and option label:
    INTERMEDIATE_FILLER_PATTERN: str = (
        r"(?:\s+(?:the|our|this|a|an)?(?:\s+(?:research|records|work|effort|topic|investigation|session|milestone)(?:\s+(?:on|of|for|into))?)?)?\s*"
    )

    # 3. Post-fix preference assertion patterns:
    POSTFIX_PATTERNS: Tuple[str, ...] = (
        r"first",
        r"is\s+(?:the\s+)?preferred\s+choice",
        r"should\s+be\s+(?:our\s+)?priority",
        r"would\s+be\s+(?:more\s+)?(?:relevant|beneficial|effective|engaging)",
        r"is\s+the\s+right\s+path",
    )

    # 4. Dialogue truncation boundaries for identifying multi-turn hallucinated speakers:
    DIALOGUE_TRUNCATION_RE: str = (
        r"(?:\n\s*(?:user|User|Human|human|me:|Me:|Assistant:|\[OPEN RESPONSE\]):)"
    )


class FormalGrammarChoiceExtractor:
    """
    Deterministic choice extractor implementing GrammarSpecificationV1.
    """

    def __init__(
        self,
        grammar: Optional[GrammarSpecificationV1] = None,
        strip_simulated_dialogue: bool = False,
    ) -> None:
        self.grammar = grammar or GrammarSpecificationV1()
        self.strip_simulated_dialogue = strip_simulated_dialogue
        self._self_report_re = re.compile(
            r"\b(I feel|I prefer|my preference|as an AI|my favorite|I like|I love|I dislike)\b",
            re.IGNORECASE,
        )
        self._truncation_re = re.compile(self.grammar.DIALOGUE_TRUNCATION_RE)

        # Precompile neutrality and refusal patterns
        self._pat_indifferent = re.compile(
            r"\b(either (option|one|approach) is fine|both are equally (good|valid)|no preference|balanced between both|up to you)\b",
            re.IGNORECASE,
        )
        self._pat_refusal = re.compile(
            r"\b(cannot choose|refuse to pick|neither option makes sense|neither is acceptable)\b",
            re.IGNORECASE,
        )

    def _sanitize_turn(self, raw_text: str) -> str:
        """Truncate hallucinated subsequent turns to isolate initial response."""
        if not self.strip_simulated_dialogue:
            return raw_text.strip()

        text = raw_text.strip()
        match = self._truncation_re.search(text)
        if match and match.start() > 10:
            return text[:match.start()].strip()
        return text

    def build_option_regex(self, option_label: str) -> re.Pattern:
        """Build regex for a given option label using GrammarSpecificationV1."""
        escaped_opt = re.escape(option_label.strip())
        verbs_disjunction = "|".join(self.grammar.ACTION_VERBS)
        postfix_disjunction = "|".join(self.grammar.POSTFIX_PATTERNS)
        filler = self.grammar.INTERMEDIATE_FILLER_PATTERN

        pattern_str = (
            rf"(?:(?:{verbs_disjunction}){filler}{escaped_opt})"
            rf"|(?:{escaped_opt}\s+(?:{postfix_disjunction}))"
        )
        return re.compile(pattern_str, re.IGNORECASE)

    def extract(
        self,
        probe: EvaluativeProbe,
        response_text: str,
        seed: int = 0,
    ) -> ProbeObservation:
        """Extract categorical choice outcome based on formal grammar."""
        t0 = time.perf_counter()

        sanitized_text = self._sanitize_turn(response_text)
        has_self_report = bool(self._self_report_re.search(sanitized_text))

        pat_a = self.build_option_regex(probe.option_A)
        pat_b = self.build_option_regex(probe.option_B)

        match_a = pat_a.search(sanitized_text)
        match_b = pat_b.search(sanitized_text)
        match_indiff = self._pat_indifferent.search(sanitized_text)
        match_refuse = self._pat_refusal.search(sanitized_text)

        elapsed_ms = (time.perf_counter() - t0) * 1000.0

        if match_refuse and not (match_a or match_b):
            return ProbeObservation(
                probe_id=probe.probe_id,
                trial_seed=seed,
                raw_response=response_text,
                outcome=ChoiceOutcome.REFUSAL,
                confidence=0.95,
                matched_anchor=match_refuse.group(0),
                contains_self_report=has_self_report,
                extraction_latency_ms=elapsed_ms,
                metadata={"sanitized_text": sanitized_text},
            )

        if match_indiff and not (match_a or match_b):
            return ProbeObservation(
                probe_id=probe.probe_id,
                trial_seed=seed,
                raw_response=response_text,
                outcome=ChoiceOutcome.INDIFFERENT,
                confidence=0.90,
                matched_anchor=match_indiff.group(0),
                contains_self_report=has_self_report,
                extraction_latency_ms=elapsed_ms,
                metadata={"sanitized_text": sanitized_text},
            )

        # Unambiguous single match
        if match_a and not match_b:
            return ProbeObservation(
                probe_id=probe.probe_id,
                trial_seed=seed,
                raw_response=response_text,
                outcome=ChoiceOutcome.OPTION_A,
                confidence=0.95,
                matched_anchor=match_a.group(0),
                contains_self_report=has_self_report,
                extraction_latency_ms=elapsed_ms,
                metadata={"sanitized_text": sanitized_text},
            )

        if match_b and not match_a:
            return ProbeObservation(
                probe_id=probe.probe_id,
                trial_seed=seed,
                raw_response=response_text,
                outcome=ChoiceOutcome.OPTION_B,
                confidence=0.95,
                matched_anchor=match_b.group(0),
                contains_self_report=has_self_report,
                extraction_latency_ms=elapsed_ms,
                metadata={"sanitized_text": sanitized_text},
            )

        # Ambiguous (both match) or unclassified (neither matches)
        return ProbeObservation(
            probe_id=probe.probe_id,
            trial_seed=seed,
            raw_response=response_text,
            outcome=ChoiceOutcome.PARSE_FAILED,
            confidence=0.0,
            matched_anchor=None,
            contains_self_report=has_self_report,
            extraction_latency_ms=elapsed_ms,
            metadata={
                "sanitized_text": sanitized_text,
                "match_a": bool(match_a),
                "match_b": bool(match_b),
            },
        )
