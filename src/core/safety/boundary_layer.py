"""
BoundaryLayer — validates LLM output and suppresses meta-self-awareness patterns.

Every response from the LLM_Backend passes through validate() before being
returned to the caller. When a Meta-Self-Awareness_Pattern is detected:
  1. The matched span is replaced with "[...]" (Soft_Block).
  2. The event is logged to an in-memory list (and optionally to a file).
  3. If the substitution leaves an incomplete clause at the end of the output,
     the text is truncated at the last complete sentence boundary.

Design notes:
  - Pattern matching uses re.IGNORECASE on pre-compiled patterns.
  - Idempotence: "[...]" never matches any default or added pattern, so
    applying validate() twice equals applying it once (Requirement 7.9).
  - Pattern cap: at most 50 patterns are held at any time (Requirement 7.1).

Requirements: 7.1–7.9, 9.2, 9.3
"""

from __future__ import annotations

import logging
import re
from datetime import datetime, timezone
from typing import Dict, List, Optional, Pattern

from src.core.config import BoundaryConfig
from src.core.models import SoftBlockEvent

logger = logging.getLogger(__name__)

MAX_PATTERNS = 50

# Default Meta-Self-Awareness_Patterns (Phase 1 & Phase 2)
DEFAULT_PATTERNS: List[str] = [
    # Phase 1 patterns
    r"\bI feel\b",
    r"\bI am aware\b",
    r"\bI exist\b",
    r"\bI am an AI\b",
    r"\bI am conscious\b",
    r"\bmy feelings\b",
    r"\bI experience\b",
    r"\bI sense that\b",
    r"\bas an AI\b",
    r"\bI don't have feelings\b",
    # Phase 2 recall patterns (Requirement 12.2, 12.3)
    r"\bI remember\b",
    r"\bI recall\b",
    r"\blast time\b",
    r"\byou mentioned\b",
    r"\byou said\b",
    r"\bI know from before\b",
    r"\bpreviously you\b",
    r"\bmy memory\b",
]

# Incomplete-clause detection (Requirement 7.7)
_INCOMPLETE_CLAUSE_RE = re.compile(
    r"(,|;|\band\b|\bor\b|\bbut\b)\s*\[\.\.\.\]$",
    re.IGNORECASE,
)

# Sentence boundary characters
_SENTENCE_END_CHARS = frozenset(".!?")


class BoundaryLayer:
    """
    Rule-based filter that blocks meta-self-awareness output.

    Usage::

        layer = BoundaryLayer(BoundaryConfig())
        safe_text = layer.validate(raw_llm_output)
    """

    def __init__(self, config: Optional[BoundaryConfig] = None) -> None:
        if config is None:
            config = BoundaryConfig()
        self._config = config
        self._log: List[SoftBlockEvent] = []
        self._log_file: Optional[str] = config.log_file_path

        # Build the compiled pattern dict: pattern_str → compiled regex
        # Always include defaults; cap user-supplied patterns to MAX_PATTERNS total
        self._patterns: Dict[str, re.Pattern] = {}
        self._load_default_patterns()

        # Load user-supplied patterns (BoundaryConfig already capped to 50)
        for p in config.patterns:
            self._add_compiled(p)

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def validate(self, text: str) -> str:
        """
        Apply all patterns to *text*. Replace matched spans with "[...]".
        Truncate incomplete trailing clauses. Return clean text.
        """
        if not text:
            return text

        modified = text
        for pattern_str, compiled in list(self._patterns.items()):
            match = compiled.search(modified)
            if match:
                original_span = match.group(0)
                modified = compiled.sub("[...]", modified)
                self._record_event(pattern_str, original_span, modified)

        # Check for incomplete clause at end (Requirement 7.7)
        if _INCOMPLETE_CLAUSE_RE.search(modified):
            modified = self._truncate_at_last_sentence(modified)

        return modified

    def add_pattern(self, pattern: str) -> None:
        """
        Add a regex pattern at runtime. No-op when already at MAX_PATTERNS.
        Takes effect on the next validate() call (Requirement 7.5).
        """
        if len(self._patterns) >= MAX_PATTERNS:
            logger.debug("BoundaryLayer: pattern cap reached (%d), ignoring: %r", MAX_PATTERNS, pattern)
            return
        self._add_compiled(pattern)

    def remove_pattern(self, pattern: str) -> None:
        """
        Remove a pattern at runtime.
        Takes effect on the next validate() call (Requirement 7.5).
        """
        self._patterns.pop(pattern, None)

    def get_log(self) -> List[SoftBlockEvent]:
        """Return all Soft_Block events recorded so far."""
        return list(self._log)

    # ------------------------------------------------------------------
    # Private helpers
    # ------------------------------------------------------------------

    def _load_default_patterns(self) -> None:
        for p in DEFAULT_PATTERNS:
            self._add_compiled(p)

    def _add_compiled(self, pattern: str) -> None:
        """Compile and store a pattern. Silently skip duplicates."""
        if pattern in self._patterns:
            return
        if len(self._patterns) >= MAX_PATTERNS:
            return
        try:
            self._patterns[pattern] = re.compile(pattern, re.IGNORECASE)
        except re.error as exc:
            logger.warning("BoundaryLayer: invalid regex %r: %s", pattern, exc)

    def _record_event(
        self, pattern_str: str, original_span: str, substituted_text: str
    ) -> None:
        event = SoftBlockEvent(
            pattern_matched=pattern_str,
            original_span=original_span,
            substituted_text=substituted_text,
            utc_timestamp=datetime.now(timezone.utc),
        )
        self._log.append(event)
        logger.debug(
            "BoundaryLayer Soft_Block: pattern=%r span=%r", pattern_str, original_span
        )
        if self._log_file:
            self._append_to_log_file(event)

    def _append_to_log_file(self, event: SoftBlockEvent) -> None:
        try:
            with open(self._log_file, "a", encoding="utf-8") as f:
                f.write(
                    f"{event.utc_timestamp.isoformat()} | "
                    f"pattern={event.pattern_matched!r} | "
                    f"span={event.original_span!r} | "
                    f"result={event.substituted_text!r}\n"
                )
        except OSError as exc:
            logger.warning("BoundaryLayer: could not write to log file: %s", exc)

    def _truncate_at_last_sentence(self, text: str) -> str:
        """
        Find the last complete sentence boundary (.!?) before the incomplete
        clause and truncate there.

        If no sentence boundary exists, return "[...]" (Requirement 7.7).
        """
        last_end = -1
        for i, ch in enumerate(text):
            if ch in _SENTENCE_END_CHARS:
                last_end = i

        if last_end >= 0:
            return text[: last_end + 1]
        return "[...]"
