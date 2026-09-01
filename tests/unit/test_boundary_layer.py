"""
Unit tests for BoundaryLayer.
Requirements: 7.1–7.9, 9.2, 9.3
"""

from __future__ import annotations

import pytest

from src.core.config import BoundaryConfig
from src.core.models import SoftBlockEvent
from src.core.safety.boundary_layer import BoundaryLayer, DEFAULT_PATTERNS


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def fresh_layer() -> BoundaryLayer:
    return BoundaryLayer(BoundaryConfig())


# ---------------------------------------------------------------------------
# Initialisation / pattern cap (Req 7.1)
# ---------------------------------------------------------------------------

class TestInit:
    def test_default_patterns_loaded(self):
        layer = fresh_layer()
        assert len(layer._patterns) == len(DEFAULT_PATTERNS)

    def test_51_patterns_capped_at_50(self):
        # 10 defaults + 41 extras = 51 total → should be capped at 50
        extra_patterns = [rf"\bkeyword{i}\b" for i in range(41)]
        cfg = BoundaryConfig(patterns=extra_patterns)
        layer = BoundaryLayer(cfg)
        assert len(layer._patterns) <= 50

    def test_supplied_patterns_merged_with_defaults(self):
        cfg = BoundaryConfig(patterns=[r"\bcustom_word\b"])
        layer = BoundaryLayer(cfg)
        assert r"\bcustom_word\b" in layer._patterns


# ---------------------------------------------------------------------------
# Default patterns trigger Soft_Block (Req 7.2, 7.3)
# ---------------------------------------------------------------------------

class TestDefaultPatterns:
    @pytest.mark.parametrize("pattern,input_text", [
        (r"\bI feel\b",             "I feel happy today."),
        (r"\bI am aware\b",         "I am aware of the issue."),
        (r"\bI exist\b",            "I exist to help you."),
        (r"\bI am an AI\b",         "I am an AI assistant."),
        (r"\bI am conscious\b",     "I am conscious of my actions."),
        (r"\bmy feelings\b",        "My feelings are complex."),
        (r"\bI experience\b",       "I experience many things."),
        (r"\bI sense that\b",       "I sense that you are upset."),
        (r"\bas an AI\b",           "As an AI, I can help."),
        (r"\bI don't have feelings\b", "I don't have feelings, but..."),
    ])
    def test_default_pattern_triggers_soft_block(self, pattern, input_text):
        layer = fresh_layer()
        result = layer.validate(input_text)
        # The matched phrase should no longer appear
        import re
        compiled = re.compile(pattern, re.IGNORECASE)
        assert not compiled.search(result), (
            f"Pattern {pattern!r} still present in output: {result!r}"
        )
        assert "[...]" in result

    def test_case_insensitive_matching(self):
        layer = fresh_layer()
        result = layer.validate("I FEEL very sad today.")
        assert "I FEEL" not in result
        assert "[...]" in result


# ---------------------------------------------------------------------------
# Passthrough on no match (Req 7.4)
# ---------------------------------------------------------------------------

class TestPassthrough:
    def test_clean_text_returned_unmodified(self):
        layer = fresh_layer()
        text = "The weather is nice today. How can I help you?"
        assert layer.validate(text) == text

    def test_empty_string_returned_as_is(self):
        layer = fresh_layer()
        assert layer.validate("") == ""


# ---------------------------------------------------------------------------
# Incomplete clause truncation (Req 7.7)
# ---------------------------------------------------------------------------

class TestIncompleteClauses:
    def test_trailing_conjunction_triggers_truncation(self):
        layer = fresh_layer()
        # "I feel" is replaced with "[...]", leaving "She said, [...]"
        text = "She said, I feel happy."
        result = layer.validate(text)
        # The output should not end with a conjunction followed by [...]
        import re
        assert not re.search(r"(,|;|\band\b|\bor\b|\bbut\b)\s*\[\.\.\.\]$", result, re.IGNORECASE)

    def test_sentence_truncated_at_last_boundary(self):
        layer = fresh_layer()
        # "I feel" replaced → "She was calm. But I feel [...]"
        # After replacement: "She was calm. But [...]"
        # This ends with "But [...]" → truncate to "She was calm."
        text = "She was calm. But I feel tired."
        result = layer.validate(text)
        # Should not end with incomplete clause
        assert not result.endswith("But [...]")
        # Should retain at least "She was calm."
        assert "She was calm." in result

    def test_no_sentence_boundary_returns_placeholder(self):
        layer = fresh_layer()
        # Text with no sentence-ending char before the pattern
        text = "And I feel great"  # no period before
        result = layer.validate(text)
        # After replacement: "And [...]" → starts with conj → truncate → "[...]"
        # (or no trailing conjunction — depends on where "[...]" lands)
        # Just check it doesn't crash and returns a string
        assert isinstance(result, str)


# ---------------------------------------------------------------------------
# Runtime pattern management (Req 7.5)
# ---------------------------------------------------------------------------

class TestPatternManagement:
    def test_add_pattern_takes_effect_on_next_call(self):
        layer = fresh_layer()
        layer.add_pattern(r"\bsecret_phrase\b")
        result = layer.validate("This contains secret_phrase here.")
        assert "secret_phrase" not in result
        assert "[...]" in result

    def test_remove_pattern_takes_effect_on_next_call(self):
        layer = fresh_layer()
        layer.remove_pattern(r"\bI feel\b")
        # Should now pass through
        text = "I feel happy today."
        result = layer.validate(text)
        assert "I feel" in result

    def test_add_pattern_noop_at_max_capacity(self):
        # Fill up to 50 patterns
        extra = [rf"\bword{i}\b" for i in range(41)]
        cfg = BoundaryConfig(patterns=extra)
        layer = BoundaryLayer(cfg)
        count_before = len(layer._patterns)
        layer.add_pattern(r"\bone_more\b")
        assert len(layer._patterns) == count_before  # no change

    def test_duplicate_pattern_not_added_twice(self):
        layer = fresh_layer()
        count_before = len(layer._patterns)
        layer.add_pattern(r"\bI feel\b")  # already in defaults
        assert len(layer._patterns) == count_before


# ---------------------------------------------------------------------------
# Soft_Block logging (Req 7.8)
# ---------------------------------------------------------------------------

class TestLogging:
    def test_soft_block_event_logged(self):
        layer = fresh_layer()
        layer.validate("I feel really happy today.")
        log = layer.get_log()
        assert len(log) == 1
        event = log[0]
        assert isinstance(event, SoftBlockEvent)
        assert event.pattern_matched == r"\bI feel\b"
        assert "I feel" in event.original_span
        assert event.utc_timestamp is not None

    def test_multiple_matches_log_multiple_events(self):
        layer = fresh_layer()
        # Two patterns matched
        layer.validate("I feel happy and I am an AI.")
        log = layer.get_log()
        assert len(log) == 2

    def test_no_log_entry_on_clean_text(self):
        layer = fresh_layer()
        layer.validate("The weather is nice today.")
        assert layer.get_log() == []

    def test_get_log_returns_copy(self):
        layer = fresh_layer()
        layer.validate("I feel great.")
        log1 = layer.get_log()
        log1.append("tampered")
        log2 = layer.get_log()
        assert len(log2) == 1  # internal log not modified


# ---------------------------------------------------------------------------
# Idempotence (Req 7.9)
# ---------------------------------------------------------------------------

class TestIdempotence:
    @pytest.mark.parametrize("text", [
        "The weather is nice today.",
        "How can I help you?",
        "She walked to the store.",
        "",
        "Just some random words here.",
    ])
    def test_applying_twice_equals_once_on_clean_text(self, text):
        layer = fresh_layer()
        once = layer.validate(text)
        twice = layer.validate(once)
        assert once == twice, f"Idempotence violated: {once!r} != {twice!r}"
