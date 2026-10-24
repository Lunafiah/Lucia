"""
src/core/communication/__init__.py

Public domain exports for Lucia Phase 16 Communication Subsystem.
"""

from src.core.communication.caps import (
    AdmissibleEvidencePool,
    CAPSResult,
    CognitiveStateSnapshot,
    CommunicativeAct,
    CommunicationPolicySnapshot,
    DialogueContextSnapshot,
    EpistemicMetadata,
    ProvenanceMetadata,
    ResolutionAdmissibilityMetadata,
    build_assertion_graph,
    build_inquire_graph,
    evaluate_caps,
)
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
from src.core.communication.response_completion_planner import (
    CompletionPlan,
    LanguageDensityProfile,
    ResponseCompletionPlanner,
)

__all__ = [
    "CommStrategy",
    "CommIntent",
    "CommunicationState",
    "CommunicationPolicy",
    "CommSemanticValidationResult",
    "SemanticConsistencyGuard",
    "CommunicativeAct",
    "DialogueContextSnapshot",
    "CognitiveStateSnapshot",
    "AdmissibleEvidencePool",
    "CommunicationPolicySnapshot",
    "EpistemicMetadata",
    "ProvenanceMetadata",
    "ResolutionAdmissibilityMetadata",
    "CAPSResult",
    "build_inquire_graph",
    "build_assertion_graph",
    "evaluate_caps",
    "ResponseCompletionPlanner",
    "CompletionPlan",
    "LanguageDensityProfile",
]
