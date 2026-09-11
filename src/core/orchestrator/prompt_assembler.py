"""
PromptAssembler — builds the Conditioned_Prompt from somatic markers,
behavioral constraints, conversation history, and optional memory echo vector.

Section order:
  1. System preamble
  2. [SOMATIC STATE]  — numeric key-value pairs only, no prose emotional labels
  3. [MEMORY ECHO]     — numeric key-value pairs only (Phase 2, omitted if None)
  4. [REASONING]       — omitted when reasoning_depth == 0
  5. [CONVERSATION]    — trimmed to max 10 turns or token budget

Requirements: Phase 1 (5.1–5.8), Phase 2 (11.2–11.4, 12.1, 12.5, 16.3)
"""

from __future__ import annotations

from typing import TYPE_CHECKING, List, Optional, Tuple, Union

import numpy as np

from src.core.errors import AssemblyError
from src.core.models import BehavioralConstraints, SomaticMarkers

if TYPE_CHECKING:
    from src.core.communication.communication_state import CommunicationState
    from src.core.knowledge.proposition import Proposition

# Section separator (Requirement 5.1)
_SEP = "\n\n---\n\n"

FORBIDDEN_RECALL_PHRASES = [
    "I remember",
    "I recall",
    "last time",
    "you mentioned",
    "you said",
    "I know from before",
    "previously you",
    "my memory",
]


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
        *,
        echo_vector: Optional[np.ndarray] = None,
        comm_state: Optional[CommunicationState] = None,
        knowledge_propositions: Optional[List[Proposition]] = None,
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
        echo_vector : np.ndarray | None, optional
            Echo_Vector synthesized by EcphoryEngine (Phase 2).
        comm_state : CommunicationState | None, optional
            Communication strategy and framing state (Phase 16).
        knowledge_propositions : list of Proposition | None, optional
            Structured knowledge facts retrieved for grounding (Phase 16).

        Returns
        -------
        str
            The assembled prompt.
        AssemblyError
            If the preamble + somatic state section alone exceeds n_ctx
            (Requirement 5.8) or if forbidden phrases appear.
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

        # --- Section 3: memory echo (Phase 2) ---
        echo_section = ""
        if echo_vector is not None:
            try:
                echo_section = self._encode_echo_section(echo_vector)
            except AssemblyError as err:
                return err

        # --- Section 4: grounded knowledge (Phase 16) ---
        knowledge_section = ""
        if knowledge_propositions:
            facts = [f"({p.subject}, {p.predicate}, {p.object})" for p in knowledge_propositions[:5]]
            knowledge_section = "[GROUNDED KNOWLEDGE]\n" + "\n".join(facts)

        # --- Section 5: communication strategy (Phase 16) ---
        comm_section = ""
        if comm_state is not None:
            comm_section = (
                "[COMMUNICATION STRATEGY]\n"
                f"strategy: {comm_state.strategy.value}\n"
                f"directness: {comm_state.directness:.2f}\n"
                f"formality: {comm_state.formality_score:.2f}\n"
                f"elaboration: {comm_state.elaboration_depth:.2f}\n"
                f"supportiveness: {comm_state.supportiveness:.2f}"
            )

        # --- Section 6: reasoning trace (Requirement 5.4, 5.5) ---
        reasoning_section = self._build_reasoning_section(constraints.reasoning_depth)

        # --- Check preamble + somatic + echo + knowledge + comm fits (Requirement 5.8) ---
        base_parts = [preamble_section, somatic_section]
        if echo_section:
            base_parts.append(echo_section)
        if knowledge_section:
            base_parts.append(knowledge_section)
        if comm_section:
            base_parts.append(comm_section)
        if reasoning_section:
            base_parts.append(reasoning_section)
        base_prompt = _SEP.join(p for p in base_parts if p)
        if _estimate_tokens(base_prompt) > n_ctx:
            return AssemblyError(
                f"System preamble alone exceeds context window "
                f"(~{_estimate_tokens(base_prompt)} tokens > {n_ctx})"
            )

        # --- Section 7: conversation history (Requirement 5.3, 5.7) ---
        history_section = self._build_history_section(history, constraints, n_ctx, base_prompt)

        # --- Assemble all sections ---
        all_sections = [preamble_section, somatic_section]
        if echo_section:
            all_sections.append(echo_section)
        if knowledge_section:
            all_sections.append(knowledge_section)
        if comm_section:
            all_sections.append(comm_section)
        if reasoning_section:
            all_sections.append(reasoning_section)
        all_sections.append(history_section)

        prompt = _SEP.join(s for s in all_sections if s)
        return prompt

    # ------------------------------------------------------------------
    # Private helpers
    # ------------------------------------------------------------------

    def _encode_echo_section(self, echo_vector: np.ndarray) -> str:
        """
        Encode Echo_Vector as lines of `echo_{i}: {val:.6f}` under [MEMORY ECHO].
        Validates that no forbidden recall phrases appear.
        """
        lines = ["[MEMORY ECHO]"]
        for i, val in enumerate(echo_vector):
            lines.append(f"echo_{i}: {float(val):.6f}")
        section = "\n".join(lines)

        for phrase in FORBIDDEN_RECALL_PHRASES:
            if phrase.lower() in section.lower():
                raise AssemblyError(
                    f"[MEMORY ECHO] section contains forbidden recall phrase: '{phrase}'"
                )
        return section

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
