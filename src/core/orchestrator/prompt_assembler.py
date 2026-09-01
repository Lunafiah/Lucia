"""
PromptAssembler — builds the Conditioned_Prompt from somatic markers,
behavioral constraints, and conversation history.

Section order (Requirement 5.1):
  1. System preamble
  2. [SOMATIC STATE]  — numeric key-value pairs only, no prose emotional labels
  3. [REASONING]      — omitted when reasoning_depth == 0
  4. [CONVERSATION]   — trimmed to max 10 turns or token budget

Requirements: 5.1–5.8
"""

from __future__ import annotations

from typing import List, Tuple, Union

from src.core.errors import AssemblyError
from src.core.models import BehavioralConstraints, SomaticMarkers

# Section separator (Requirement 5.1)
_SEP = "\n\n---\n\n"


def _estimate_tokens(text: str) -> int:
    """Rough token count: len(text) // 4 (matches design.md specification)."""
    return max(1, len(text) // 4)


class PromptAssembler:
    """
    Assembles the conditioned prompt passed to the LLM_Backend.

    The assembler is stateless — all inputs are passed to assemble().
    """

    SECTION_SEP = _SEP

    def assemble(
        self,
        somatic: SomaticMarkers,
        constraints: BehavioralConstraints,
        history: List[Tuple[str, str]],
        system_preamble: str = "",
        n_ctx: int = 4096,
    ) -> Union[str, AssemblyError]:
        """
        Build the Conditioned_Prompt string.

        Parameters
        ----------
        somatic : SomaticMarkers
            Current somatic state — inserted as numeric key-value pairs.
        constraints : BehavioralConstraints
            Generation parameters that shape history trimming and reasoning depth.
        history : list of (role, text) tuples
            Conversation history, oldest first.
        system_preamble : str
            Static system prompt prefix.
        n_ctx : int
            LLM context window token limit. Used for overflow detection.

        Returns
        -------
        str
            The assembled prompt.
        AssemblyError
            If the preamble + somatic state section alone exceeds n_ctx
            (Requirement 5.8).
        """
        # --- Section 1: system preamble ---
        preamble_section = system_preamble.strip()

        # --- Section 2: somatic state (numeric only — Requirement 5.2) ---
        somatic_section = (
            "[SOMATIC STATE]\n"
            f"stability: {somatic.stability:.6f}\n"
            f"cognitive_load: {somatic.cognitive_load:.6f}\n"
            f"energy: {somatic.energy:.6f}\n"
            f"tension: {somatic.tension:.6f}"
        )

        # --- Section 3: reasoning trace (Requirement 5.4, 5.5) ---
        reasoning_section = self._build_reasoning_section(constraints.reasoning_depth)

        # --- Check preamble alone fits (Requirement 5.8) ---
        base_parts = [preamble_section, somatic_section]
        if reasoning_section:
            base_parts.append(reasoning_section)
        base_prompt = _SEP.join(p for p in base_parts if p)
        if _estimate_tokens(base_prompt) > n_ctx:
            return AssemblyError(
                f"System preamble alone exceeds context window "
                f"(~{_estimate_tokens(base_prompt)} tokens > {n_ctx})"
            )

        # --- Section 4: conversation history (Requirement 5.3, 5.7) ---
        history_section = self._build_history_section(history, constraints, n_ctx, base_prompt)

        # --- Assemble all sections ---
        all_sections = [preamble_section, somatic_section]
        if reasoning_section:
            all_sections.append(reasoning_section)
        all_sections.append(history_section)

        prompt = _SEP.join(s for s in all_sections if s)
        return prompt

    # ------------------------------------------------------------------
    # Private helpers
    # ------------------------------------------------------------------

    def _build_reasoning_section(self, reasoning_depth: int) -> str:
        """
        Build the [REASONING] section.

        steps = min((depth * 2) - 1, 5)
        Returns empty string when reasoning_depth == 0 (Requirement 5.4).
        """
        if reasoning_depth <= 0:
            return ""
        steps = min((reasoning_depth * 2) - 1, 5)
        lines = ["[REASONING]"]
        for i in range(1, steps + 1):
            lines.append(f"Step {i}: <think>")
        return "\n".join(lines)

    def _build_history_section(
        self,
        history: List[Tuple[str, str]],
        constraints: BehavioralConstraints,
        n_ctx: int,
        base_prompt: str,
    ) -> str:
        """
        Select the most-recent conversation turns that fit within the budget.

        Budget (Requirement 5.3):
            max_turns = min(10, turns whose total tokens ≤ max_tokens * 4)

        Then trim further if the full assembled prompt would exceed n_ctx
        (Requirement 5.7).
        """
        if not history:
            return "[CONVERSATION]\n(no history)"

        token_budget = constraints.max_tokens * 4
        max_turns = 10

        # Walk history from newest to oldest, accumulating turns
        selected: List[Tuple[str, str]] = []
        token_sum = 0
        for role, text in reversed(history):
            if len(selected) >= max_turns:
                break
            turn_tokens = _estimate_tokens(f"{role}: {text}")
            if token_sum + turn_tokens > token_budget:
                break
            selected.insert(0, (role, text))
            token_sum += turn_tokens

        # Build the history text and check against n_ctx
        # Trim oldest turns one-by-one if needed (Requirement 5.7)
        base_tokens = _estimate_tokens(base_prompt)
        while selected:
            history_text = self._format_history(selected)
            full_tokens = base_tokens + _estimate_tokens(_SEP + history_text)
            if full_tokens <= n_ctx:
                break
            selected.pop(0)  # drop oldest turn

        if not selected:
            return "[CONVERSATION]\n(no history)"

        return self._format_history(selected)

    def _format_history(self, turns: List[Tuple[str, str]]) -> str:
        lines = ["[CONVERSATION]"]
        for role, text in turns:
            lines.append(f"{role}: {text}")
        return "\n".join(lines)
