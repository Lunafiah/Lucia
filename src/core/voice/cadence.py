"""
src/core/voice/cadence.py

Canonical Cadence Adaptation Module for Lucia Phase 24.
Implements bounded orthographic punctuation rules conforming to ADR-032.2 and Contract Domain B.

Invariants:
- Semantic Separation Invariant: Cadence conditioning operates strictly on orthographic prosodic markers
  ('...', ',', '!'). It MUST NOT rewrite, delete, or alter semantic content, named entities, or numerical values.
- Hard Upper Bound: <= 3 inserted/modified punctuation marks per response.
- Zero Inner SSML Invariant: No XML/SSML tags are ever injected into the text stream.
"""

from __future__ import annotations

import re
from typing import Optional


def format_cadence_punctuation(
    text: str,
    formality: float = 0.50,
    supportiveness: float = 0.50,
    max_marks: int = 3,
) -> str:
    """
    Apply bounded orthographic cadence punctuation without altering semantic content.

    Parameters
    ----------
    text : str
        Clean input text from the cognitive pipeline or LLM.
    formality : float
        Formality score F_verbal in [0.0, 1.0].
    supportiveness : float
        Supportiveness score S_verbal in [0.0, 1.0].
    max_marks : int
        Strict cap on modified/inserted punctuation marks (default: 3).

    Returns
    -------
    str
        Orthographically conditioned text for TTS synthesis.
    """
    if not text or not text.strip():
        return text

    clean = text.strip()

    # Rule 1: High Formality (F >= 0.65) -> Clean grammatical punctuation, zero ellipses
    if formality >= 0.65:
        # Replace ellipses with commas or periods (counts toward max_marks)
        replaced = 0
        def _ellipsis_sub(match: re.Match) -> str:
            nonlocal replaced
            if replaced < max_marks:
                replaced += 1
                return ", "
            return match.group(0)

        result = re.sub(r"\s*\.\.\.\s*", _ellipsis_sub, clean)
        # Ensure clean sentence-ending period
        if result and result[-1] not in ".!?":
            result += "."
        return result

    # Rule 2: Low Formality / High Warmth (F <= 0.35) -> Conversational breathing cadence
    if formality <= 0.35:
        marks_used = 0
        result = clean

        # Intro phrase pattern for conversational breathing pause (~800ms in Edge-TTS)
        # Matches common conversational intros across EN, VI, JP
        intro_patterns = [
            r"^(Hello|Hi|Hey|Good morning|Good afternoon|Well|Chào bạn|Chào buổi sáng|Xin chào|おはようございます|こんにちは)[,!]?\s+",
        ]

        for pat in intro_patterns:
            if marks_used >= max_marks:
                break
            match = re.search(pat, result, flags=re.IGNORECASE)
            if match:
                matched_str = match.group(0)
                # Replace trailing comma/space with ellipsis for respiratory pause if not already ellipsis
                if not matched_str.endswith("... "):
                    clean_intro = matched_str.rstrip(",! ")
                    result = clean_intro + "... " + result[match.end():]
                    marks_used += 1
                break

        # Empathetic exclamation at peak warmth/supportiveness (S >= 0.70)
        if supportiveness >= 0.70 and marks_used < max_marks:
            if result.endswith("."):
                result = result[:-1] + "!"
                marks_used += 1

        return result

    # Rule 3: Balanced Formality (0.35 < F < 0.65) -> Preserve natural phrasing
    return clean
