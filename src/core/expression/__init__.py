"""
src/core/expression/__init__.py

Public domain exports for Lucia Phase 16 Multimodal Expression Subsystem.
"""

from src.core.expression.expression_policy import ExpressionPolicy
from src.core.expression.expression_state import (
    ExpressionState,
    FacialExpression,
    PostureGaze,
    TextStyle,
    VoiceProsody,
)
from src.core.expression.semantic_consistency_guard import (
    SemanticConsistencyGuard,
    SemanticIntent,
    SemanticValidationResult,
)

__all__ = [
    "TextStyle",
    "VoiceProsody",
    "FacialExpression",
    "PostureGaze",
    "ExpressionState",
    "ExpressionPolicy",
    "SemanticIntent",
    "SemanticValidationResult",
    "SemanticConsistencyGuard",
]
