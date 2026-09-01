"""
Custom error types for Lucia Core Phase 1.
"""

from __future__ import annotations


class AssemblyError(Exception):
    """
    Raised (or returned as a sentinel) by PromptAssembler when the conditioned
    prompt cannot be assembled — specifically when the system preamble alone
    exceeds the LLM_Backend context window.

    The Orchestrator checks ``isinstance(result, AssemblyError)`` rather than
    truthiness to distinguish this from empty-string responses.
    """

    def __init__(self, message: str = "Prompt assembly failed") -> None:
        super().__init__(message)
        self.message = message

    def __repr__(self) -> str:
        return f"AssemblyError({self.message!r})"
