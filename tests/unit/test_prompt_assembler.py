"""
Unit tests for PromptAssembler.
Requirements: 5.1–5.8
"""

from __future__ import annotations

from typing import List, Tuple

import pytest

from src.core.errors import AssemblyError
from src.core.models import BehavioralConstraints, SomaticMarkers
from src.core.orchestrator.prompt_assembler import PromptAssembler, _SEP


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def make_somatic(st=0.9, cl=0.1, en=0.9, te=0.05) -> SomaticMarkers:
    return SomaticMarkers(stability=st, cognitive_load=cl, energy=en, tension=te)


def make_constraints(max_t=150, temp=0.75, lat=0, depth=1) -> BehavioralConstraints:
    return BehavioralConstraints(
        max_tokens=max_t, temperature=temp, latency_ms=lat, reasoning_depth=depth
    )


def make_history(n: int) -> List[Tuple[str, str]]:
    return [(("user" if i % 2 == 0 else "assistant"), f"Message {i}") for i in range(n)]


ASSEMBLER = PromptAssembler()


# ---------------------------------------------------------------------------
# Section order (Req 5.1)
# ---------------------------------------------------------------------------

class TestSectionOrder:
    def test_preamble_appears_first(self):
        result = ASSEMBLER.assemble(
            make_somatic(), make_constraints(), [], "My preamble"
        )
        assert isinstance(result, str)
        assert result.startswith("My preamble")

    def test_somatic_state_after_preamble(self):
        result = ASSEMBLER.assemble(
            make_somatic(), make_constraints(depth=0), [], "PREAMBLE"
        )
        assert isinstance(result, str)
        preamble_end = result.index("[SOMATIC STATE]")
        somatic_end = result.index("[CONVERSATION]")
        assert preamble_end < somatic_end

    def test_reasoning_after_somatic_when_present(self):
        result = ASSEMBLER.assemble(
            make_somatic(), make_constraints(depth=2), [], "PREAMBLE"
        )
        assert isinstance(result, str)
        somatic_pos = result.index("[SOMATIC STATE]")
        reasoning_pos = result.index("[REASONING]")
        conv_pos = result.index("[CONVERSATION]")
        assert somatic_pos < reasoning_pos < conv_pos

    def test_sections_separated_by_sep(self):
        result = ASSEMBLER.assemble(
            make_somatic(), make_constraints(depth=1), [], "PREAMBLE"
        )
        assert isinstance(result, str)
        # All section boundaries must use the defined separator
        assert _SEP in result


# ---------------------------------------------------------------------------
# Somatic state section — numeric only (Req 5.2)
# ---------------------------------------------------------------------------

class TestSomaticSection:
    def test_somatic_contains_numeric_values(self):
        result = ASSEMBLER.assemble(make_somatic(st=0.9), make_constraints(), [])
        assert isinstance(result, str)
        assert "stability: 0.900000" in result

    def test_somatic_contains_all_four_markers(self):
        result = ASSEMBLER.assemble(make_somatic(), make_constraints(), [])
        assert isinstance(result, str)
        for key in ["stability:", "cognitive_load:", "energy:", "tension:"]:
            assert key in result

    def test_somatic_contains_no_emotional_prose(self):
        result = ASSEMBLER.assemble(make_somatic(), make_constraints(), [])
        assert isinstance(result, str)
        forbidden = [
            "feels calm", "feels stressed", "the system feels",
            "is feeling", "system is anxious",
        ]
        for phrase in forbidden:
            assert phrase.lower() not in result.lower(), (
                f"Emotional prose found: {phrase!r}"
            )


# ---------------------------------------------------------------------------
# Reasoning section (Req 5.4, 5.5)
# ---------------------------------------------------------------------------

class TestReasoningSection:
    def test_depth_0_omits_reasoning(self):
        result = ASSEMBLER.assemble(make_somatic(), make_constraints(depth=0), [])
        assert isinstance(result, str)
        assert "[REASONING]" not in result

    def test_depth_1_gives_1_step(self):
        result = ASSEMBLER.assemble(make_somatic(), make_constraints(depth=1), [])
        assert isinstance(result, str)
        assert "[REASONING]" in result
        # (1*2)-1 = 1 step
        assert result.count("Step ") == 1

    def test_depth_2_gives_3_steps(self):
        result = ASSEMBLER.assemble(make_somatic(), make_constraints(depth=2), [])
        assert isinstance(result, str)
        # (2*2)-1 = 3 steps
        assert result.count("Step ") == 3

    def test_depth_3_gives_5_steps_capped(self):
        result = ASSEMBLER.assemble(make_somatic(), make_constraints(depth=3), [])
        assert isinstance(result, str)
        # (3*2)-1 = 5, which equals the cap
        assert result.count("Step ") == 5

    def test_steps_labelled_sequentially(self):
        result = ASSEMBLER.assemble(make_somatic(), make_constraints(depth=2), [])
        assert isinstance(result, str)
        assert "Step 1:" in result
        assert "Step 2:" in result
        assert "Step 3:" in result


# ---------------------------------------------------------------------------
# History trimming (Req 5.3)
# ---------------------------------------------------------------------------

class TestHistoryTrimming:
    def test_max_10_turns_enforced(self):
        history = make_history(15)
        result = ASSEMBLER.assemble(
            make_somatic(), make_constraints(max_t=2000), history
        )
        assert isinstance(result, str)
        # Count occurrences of "Message " in CONVERSATION section
        conv_section = result.split("[CONVERSATION]")[-1]
        message_count = conv_section.count("Message ")
        assert message_count <= 10, f"Expected ≤10 messages, got {message_count}"

    def test_empty_history_shows_placeholder(self):
        result = ASSEMBLER.assemble(make_somatic(), make_constraints(), [])
        assert isinstance(result, str)
        assert "[CONVERSATION]" in result

    def test_most_recent_turns_kept(self):
        history = make_history(15)
        result = ASSEMBLER.assemble(
            make_somatic(), make_constraints(max_t=2000), history
        )
        assert isinstance(result, str)
        # The most recent message should always be present
        assert "Message 14" in result

    def test_token_budget_limits_history(self):
        # With max_tokens=10, token budget = 40 — should severely limit history
        history = make_history(15)
        result = ASSEMBLER.assemble(
            make_somatic(), make_constraints(max_t=10), history
        )
        assert isinstance(result, str)
        conv_section = result.split("[CONVERSATION]")[-1]
        message_count = conv_section.count("Message ")
        # With budget of 40 tokens, very few turns should fit
        assert message_count < 10


# ---------------------------------------------------------------------------
# Context window overflow (Req 5.7, 5.8)
# ---------------------------------------------------------------------------

class TestContextOverflow:
    def test_preamble_exceeds_n_ctx_returns_assembly_error(self):
        # A preamble whose token count alone exceeds n_ctx=10
        huge_preamble = "word " * 100  # ~500 tokens by estimate
        result = ASSEMBLER.assemble(
            make_somatic(), make_constraints(), [], huge_preamble, n_ctx=10
        )
        assert isinstance(result, AssemblyError), (
            f"Expected AssemblyError, got: {type(result).__name__}"
        )

    def test_long_history_trimmed_to_fit_n_ctx(self):
        # Use a tight n_ctx but a preamble that fits
        history = make_history(20)
        result = ASSEMBLER.assemble(
            make_somatic(), make_constraints(max_t=500), history,
            system_preamble="", n_ctx=200
        )
        # Should succeed (not an AssemblyError) — history trimmed to fit
        assert isinstance(result, str)

    def test_assembly_error_has_descriptive_message(self):
        huge_preamble = "x " * 500
        result = ASSEMBLER.assemble(
            make_somatic(), make_constraints(), [], huge_preamble, n_ctx=5
        )
        assert isinstance(result, AssemblyError)
        assert "context window" in str(result).lower() or "exceeds" in str(result).lower()
