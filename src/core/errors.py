"""
Custom error types for Lucia Core Phase 1 and Phase 2.
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


class CapacityError(Exception):
    """
    Raised when a write is attempted on a full SDM store (Requirement 4.2, 4.4).
    """

    def __init__(
        self,
        capacity: int,
        address_preview: str = "",
        message: str | None = None,
    ) -> None:
        self.capacity = capacity
        self.address_preview = address_preview
        if message is None:
            message = (
                f"SDM at capacity ({capacity}); attempted write at address "
                f"{address_preview}..."
            )
        super().__init__(message)
        self.message = message

    def __repr__(self) -> str:
        return (
            f"CapacityError(capacity={self.capacity!r}, "
            f"address_preview={self.address_preview!r})"
        )
