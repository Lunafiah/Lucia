"""
src/core/cognition/contract/__init__.py

Public interface for Phase 23-G: Semantic Substrate -> Cognitive Core Contract.
"""

from src.core.cognition.contract.arena import (
    ArenaCapacityExceededError,
    TermArena,
)
from src.core.cognition.contract.epistemic import (
    EpistemicStatus,
    KleeneValue,
    kleene_all,
    kleene_and,
    kleene_any,
    kleene_not,
    kleene_or,
)
from src.core.cognition.contract.inference import (
    ASSERT_ERR_CAPACITY_EXCEEDED,
    ASSERT_ERR_ILLEGAL_EPITEMIC_UPGRADE,
    ASSERT_ERR_MISSING_PREMISES,
    ASSERT_ERR_MISSING_RULE,
    ASSERT_ERR_PREMISE_FALSE,
    ASSERT_ERR_PREMISE_INACTIVE,
    ASSERT_ERR_PREMISE_NOT_FOUND,
    ASSERT_ERR_PREMISE_UNKNOWN,
    ASSERT_SUCCESS,
    AssertionResult,
    AssertInferredTerm,
    DisambiguationSubgoal,
    EvaluateAmbiguity,
    RetractAndCascadeInvalidate,
)
from src.core.cognition.contract.matcher import (
    EvaluateConjunctionKleene,
    EvaluateTermKleene,
    QueryTermPattern,
    QueryTermPatternIntoBuffer,
)
from src.core.cognition.contract.projection import (
    ProjectGraphToTerms,
    ProjectionResult,
    SymbolTable,
)
from src.core.cognition.contract.provenance import ProvenanceRecord
from src.core.cognition.contract.synthesis import (
    SynthesizeIntentGraph,
    SynthesisResult,
)
from src.core.cognition.contract.terms import (
    BindingSet,
    EntityTerm,
    LogicalTerm,
    SCOPE_TYPE_INTENSIONAL,
    SCOPE_TYPE_MODAL,
    SCOPE_TYPE_NEGATION,
    SCOPE_TYPE_ROOT,
    ScopeTerm,
    TermQueryPattern,
)

__all__ = [
    # Epistemic & Kleene
    "EpistemicStatus",
    "KleeneValue",
    "kleene_and",
    "kleene_or",
    "kleene_not",
    "kleene_all",
    "kleene_any",
    "EvaluateTermKleene",
    "EvaluateConjunctionKleene",
    # Terms & Containers
    "LogicalTerm",
    "ScopeTerm",
    "EntityTerm",
    "TermQueryPattern",
    "BindingSet",
    "ProvenanceRecord",
    "SCOPE_TYPE_ROOT",
    "SCOPE_TYPE_NEGATION",
    "SCOPE_TYPE_MODAL",
    "SCOPE_TYPE_INTENSIONAL",
    # Memory Arena
    "TermArena",
    "ArenaCapacityExceededError",
    "SymbolTable",
    # Projection & Synthesis
    "ProjectGraphToTerms",
    "ProjectionResult",
    "SynthesizeIntentGraph",
    "SynthesisResult",
    # Inference & Disambiguation
    "AssertInferredTerm",
    "AssertionResult",
    "RetractAndCascadeInvalidate",
    "EvaluateAmbiguity",
    "DisambiguationSubgoal",
    "QueryTermPattern",
    "QueryTermPatternIntoBuffer",
    # Assertion error constants
    "ASSERT_SUCCESS",
    "ASSERT_ERR_MISSING_RULE",
    "ASSERT_ERR_MISSING_PREMISES",
    "ASSERT_ERR_PREMISE_NOT_FOUND",
    "ASSERT_ERR_PREMISE_INACTIVE",
    "ASSERT_ERR_PREMISE_FALSE",
    "ASSERT_ERR_PREMISE_UNKNOWN",
    "ASSERT_ERR_CAPACITY_EXCEEDED",
    "ASSERT_ERR_ILLEGAL_EPITEMIC_UPGRADE",
]
