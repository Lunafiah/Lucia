"""
src/core/cognition/kernel/__init__.py

Phase 23-H: Bounded Goal-Directed Reasoning Kernel & JTMS.
Language-Independent Core Reasoning Substrate.
"""

from src.core.cognition.kernel.binding import (
    BindingFrame,
    MAX_VARS,
    VAR_0,
    VAR_1,
    VAR_2,
    VAR_3,
    VAR_4,
    VAR_5,
    VAR_6,
    VAR_7,
    index_to_var,
    is_variable,
    unify_terms,
    unify_value,
    var_to_index,
)
from src.core.cognition.kernel.conflict import (
    ConflictRecord,
    detect_direct_conflict,
)
from src.core.cognition.kernel.engine import (
    Goal,
    GoalResult,
    INFO_REASON_AMBIGUOUS_REFERENT,
    INFO_REASON_MISSING_PREMISE,
    INFO_REASON_UNGROUNDED_VARIABLE,
    InformationSubgoal,
    MAX_INFERENCE_STEPS,
    MAX_SEARCH_DEPTH,
    ReasoningKernel,
)
from src.core.cognition.kernel.jtms import (
    JTMS,
    Justification,
)
from src.core.cognition.kernel.rules import (
    InferenceRule,
    MAX_ARGS,
    MAX_PREMISES,
    RuleHead,
    RuleIndex,
    RulePremise,
)

__all__ = [
    # Binding
    "MAX_VARS",
    "VAR_0",
    "VAR_1",
    "VAR_2",
    "VAR_3",
    "VAR_4",
    "VAR_5",
    "VAR_6",
    "VAR_7",
    "is_variable",
    "var_to_index",
    "index_to_var",
    "BindingFrame",
    "unify_value",
    "unify_terms",
    # Rules
    "MAX_PREMISES",
    "MAX_ARGS",
    "RuleHead",
    "RulePremise",
    "InferenceRule",
    "RuleIndex",
    # JTMS
    "Justification",
    "JTMS",
    # Conflict
    "ConflictRecord",
    "detect_direct_conflict",
    # Engine
    "MAX_SEARCH_DEPTH",
    "MAX_INFERENCE_STEPS",
    "INFO_REASON_MISSING_PREMISE",
    "INFO_REASON_UNGROUNDED_VARIABLE",
    "INFO_REASON_AMBIGUOUS_REFERENT",
    "Goal",
    "InformationSubgoal",
    "GoalResult",
    "ReasoningKernel",
]
