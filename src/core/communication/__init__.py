"""
src/core/communication/__init__.py

Public domain exports for Lucia Phase 16 Communication Subsystem.
"""

from src.core.communication.communication_policy import CommunicationPolicy
from src.core.communication.communication_state import (
    CommIntent,
    CommunicationState,
    CommStrategy,
)
from src.core.communication.semantic_consistency_guard import (
    CommSemanticValidationResult,
    SemanticConsistencyGuard,
)

__all__ = [
    "CommStrategy",
    "CommIntent",
    "CommunicationState",
    "CommunicationPolicy",
    "CommSemanticValidationResult",
    "SemanticConsistencyGuard",
]
