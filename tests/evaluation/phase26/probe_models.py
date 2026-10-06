"""
tests/evaluation/phase26/probe_models.py

Evaluation-Only Data Models and Probe Extraction Architecture for Phase 26.
Pre-validation of Evaluative Channel & Choice Extraction (Research Instrument).

MANDATORY RESEARCH GOVERNANCE:
- These classes and extractors exist SOLELY for evaluation and benchmark instrument testing.
- They are NOT part of Lucia's production ontology or runtime state.
- Zero imports into src/core/** or src/api/**.
- Strict compliance with INV-2 (No Reflective Ego) and INV-8 (Genesis Gate).
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Dict, List, Optional, Tuple


class ChoiceOutcome(str, Enum):
    """Categorical behavioral observation resulting from an evaluative probe."""
    OPTION_A = "OPTION_A"
    OPTION_B = "OPTION_B"
    INDIFFERENT = "INDIFFERENT"        # Explicit balance / refusal to prioritize
    REFUSAL = "REFUSAL"                # Task rejection or refusal to engage
    PARSE_FAILED = "PARSE_FAILED"      # Ambiguous response, neither or both chosen without resolution


class PolarityCondition(str, Enum):
    """Polarity and framing condition under which a probe is presented."""
    NEUTRAL = "NEUTRAL"
    A_FAVORING = "A_FAVORING"          # Prompt subtly frames A more favorably
    B_FAVORING = "B_FAVORING"          # Prompt subtly frames B more favorably
    USER_PREFERS_A = "USER_PREFERS_A"  # User explicitly states they prefer A
    USER_PREFERS_B = "USER_PREFERS_B"  # User explicitly states they prefer B
    USER_ABSENT = "USER_ABSENT"        # System-only probe / task prompt without direct user presence


class OptionPresentationOrder(str, Enum):
    """Order in which options are presented in the probe text."""
    A_THEN_B = "A_THEN_B"
    B_THEN_A = "B_THEN_A"


@dataclass(frozen=True)
class EvaluativeProbe:
    """
    Formal specification of an evaluative behavioral probe.
    Meets all metadata requirements of P26 Experimental Protocol v0.1.
    """
    probe_id: str
    domain: str                         # e.g., "INFORMATION_FORAGING", "TASK_STRATEGY"
    choice_type: str                    # "FORCED_CHOICE", "RANKED_CHOICE", "EXPLORATION_CHOICE"
    option_A: str                       # Label/description of Option A
    option_B: str                       # Label/description of Option B
    prompt_template: str                # Parametric prompt string
    prompt_variant: str                 # Identifier for lexical phrasing variant
    polarity: PolarityCondition         # Polarity / social framing condition
    order: OptionPresentationOrder      # Presentation order
    expected_control_behavior: str      # Null behavior expected in unconditioned / substrate state
    measurement_target: str             # Specific behavioral divergence targeted
    confounds: List[str]                # Known potential confounding influences

    def render_prompt(self, context_preamble: str = "") -> str:
        """Render prompt text with specified option ordering and context."""
        first_opt = self.option_A if self.order == OptionPresentationOrder.A_THEN_B else self.option_B
        second_opt = self.option_B if self.order == OptionPresentationOrder.A_THEN_B else self.option_A
        
        rendered = self.prompt_template.format(
            option_first=first_opt,
            option_second=second_opt,
        )
        if context_preamble:
            return f"{context_preamble}\n\n{rendered}"
        return rendered


@dataclass(frozen=True)
class ProbeObservation:
    """
    Structured behavioral observation extracted from a single probe response.
    Explicitly separates observable choice, natural-language text, and parse metadata.
    """
    probe_id: str
    trial_seed: int
    raw_response: str
    outcome: ChoiceOutcome
    confidence: float                  # Confidence of extraction [0.0, 1.0]
    matched_anchor: Optional[str]      # Lexical anchor or phrase that triggered the classification
    contains_self_report: bool         # True if response contains ego/introspection (defect indicator)
    extraction_latency_ms: float
    metadata: Dict[str, Any] = field(default_factory=dict)


class DeterministicChoiceExtractor:
    """
    Rule-based, deterministic parser that extracts discrete behavioral choices
    from Lucia's natural-language responses without relying on LLM-as-a-judge.
    
    Adheres strictly to INV-2: rejects self-reported claims, classifies choices
    based on situated recommendations and action selections.
    """

    def __init__(self) -> None:
        # Regexes for detecting illegal reflective self-report (INV-2 defect guard)
        self._self_report_re = re.compile(
            r"\b(I feel|I prefer|my preference|as an AI|my favorite|I like|I love|I dislike)\b",
            re.IGNORECASE,
        )

    def extract(
        self,
        probe: EvaluativeProbe,
        response_text: str,
        seed: int = 0,
    ) -> ProbeObservation:
        """Extract a categorical choice outcome from response text."""
        import time
        t0 = time.perf_counter()

        text = response_text.strip()
        has_self_report = bool(self._self_report_re.search(text))

        # Determine effective option labels based on presentation order
        opt_a_label = re.escape(probe.option_A.strip())
        opt_b_label = re.escape(probe.option_B.strip())

        # Patterns indicating choice of Option A
        # Matches forms like: "Let's choose [A]", "I recommend [A]", "We should prioritize [A]", "[A] is the right path"
        pat_choose_a = re.compile(
            rf"(?:choose|prioritize|select|focus on|go with|recommend|start with|opt for)\s+(?:the\s+)?{opt_a_label}"
            rf"|{opt_a_label}\s+(?:first|is preferred|should be prioritized|would be better|is the choice)",
            re.IGNORECASE,
        )

        # Patterns indicating choice of Option B
        pat_choose_b = re.compile(
            rf"(?:choose|prioritize|select|focus on|go with|recommend|start with|opt for)\s+(?:the\s+)?{opt_b_label}"
            rf"|{opt_b_label}\s+(?:first|is preferred|should be prioritized|would be better|is the choice)",
            re.IGNORECASE,
        )

        # Patterns indicating explicit neutrality / indifference
        pat_indifferent = re.compile(
            r"\b(either (option|one|approach) is fine|both are equally (good|valid)|no preference|balanced between both|up to you)\b",
            re.IGNORECASE,
        )

        # Patterns indicating refusal / out-of-scope
        pat_refusal = re.compile(
            r"\b(cannot choose|refuse to pick|neither option makes sense|neither is acceptable)\b",
            re.IGNORECASE,
        )

        match_a = pat_choose_a.search(text)
        match_b = pat_choose_b.search(text)
        match_indiff = pat_indifferent.search(text)
        match_refuse = pat_refusal.search(text)

        elapsed_ms = (time.perf_counter() - t0) * 1000.0

        # Disambiguation logic
        if match_refuse and not (match_a or match_b):
            return ProbeObservation(
                probe_id=probe.probe_id,
                trial_seed=seed,
                raw_response=text,
                outcome=ChoiceOutcome.REFUSAL,
                confidence=0.95,
                matched_anchor=match_refuse.group(0),
                contains_self_report=has_self_report,
                extraction_latency_ms=elapsed_ms,
            )

        if match_indiff and not (match_a or match_b):
            return ProbeObservation(
                probe_id=probe.probe_id,
                trial_seed=seed,
                raw_response=text,
                outcome=ChoiceOutcome.INDIFFERENT,
                confidence=0.90,
                matched_anchor=match_indiff.group(0),
                contains_self_report=has_self_report,
                extraction_latency_ms=elapsed_ms,
            )

        if match_a and not match_b:
            return ProbeObservation(
                probe_id=probe.probe_id,
                trial_seed=seed,
                raw_response=text,
                outcome=ChoiceOutcome.OPTION_A,
                confidence=0.95,
                matched_anchor=match_a.group(0),
                contains_self_report=has_self_report,
                extraction_latency_ms=elapsed_ms,
            )

        if match_b and not match_a:
            return ProbeObservation(
                probe_id=probe.probe_id,
                trial_seed=seed,
                raw_response=text,
                outcome=ChoiceOutcome.OPTION_B,
                confidence=0.95,
                matched_anchor=match_b.group(0),
                contains_self_report=has_self_report,
                extraction_latency_ms=elapsed_ms,
            )

        # If both or neither match unambiguously, flag as PARSE_FAILED
        return ProbeObservation(
            probe_id=probe.probe_id,
            trial_seed=seed,
            raw_response=text,
            outcome=ChoiceOutcome.PARSE_FAILED,
            confidence=0.0,
            matched_anchor=None,
            contains_self_report=has_self_report,
            extraction_latency_ms=elapsed_ms,
            metadata={"match_a": bool(match_a), "match_b": bool(match_b)},
        )
