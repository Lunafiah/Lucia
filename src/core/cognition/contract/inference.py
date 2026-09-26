"""
src/core/cognition/contract/inference.py

Phase 23-G: Non-Monotonic Inference, Epistemic Safety, and AMBIGUOUS Subgoal Resolution.

Strict Invariants:
1. INFERRED terms can ONLY be created through valid Cognitive Core assertions.
2. Every INFERRED term MUST contain rule_id, supporting premise IDs, and ProvenanceRecord.
3. Strong Kleene premise validation: premises evaluating to UNKNOWN or FALSE cannot
   produce certain INFERRED conclusions.
4. Cascade Invalidation (JTMS): Retracting P1 recursively invalidates P2, P3, P4
   dependent on it, while preserving independent FACTs and unlinked inferences.
5. AMBIGUOUS resolution: If competing interpretations produce identical action, proceed.
   If competing interpretations produce incompatible actions, produce DisambiguationSubgoal.
   NEVER pick an arbitrary or probabilistic default.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Callable, Dict, List, Optional, Set, Tuple

from src.core.cognition.contract.arena import ArenaCapacityExceededError, TermArena
from src.core.cognition.contract.epistemic import EpistemicStatus, KleeneValue, kleene_all
from src.core.cognition.contract.matcher import EvaluateTermKleene
from src.core.cognition.contract.provenance import ProvenanceRecord
from src.core.cognition.contract.terms import LogicalTerm


# Error codes for AssertionResult
ASSERT_SUCCESS = 0
ASSERT_ERR_MISSING_RULE = 1
ASSERT_ERR_MISSING_PREMISES = 2
ASSERT_ERR_PREMISE_NOT_FOUND = 3
ASSERT_ERR_PREMISE_INACTIVE = 4
ASSERT_ERR_PREMISE_FALSE = 5
ASSERT_ERR_PREMISE_UNKNOWN = 6
ASSERT_ERR_CAPACITY_EXCEEDED = 7
ASSERT_ERR_ILLEGAL_EPITEMIC_UPGRADE = 8


@dataclass(frozen=True)
class AssertionResult:
    """Consolidated outcome of AssertInferredTerm."""
    success: bool
    term_id: int
    error_code: int = ASSERT_SUCCESS
    error_message: str = ""

    def to_dict(self) -> Dict[str, Any]:
        return {
            "success": self.success,
            "term_id": self.term_id,
            "error_code": self.error_code,
            "error_message": self.error_message,
        }


@dataclass(frozen=True)
class DisambiguationSubgoal:
    """
    Subgoal emitted when competing ambiguous hypotheses produce incompatible actions.
    Enforces that the Core does not arbitrarily pick an interpretation.
    """
    target_entity_id: int
    candidate_concept_ids: Tuple[int, ...]
    conflicting_action_ids: Tuple[int, ...]
    reason_id: int = 0

    def to_dict(self) -> Dict[str, Any]:
        return {
            "target_entity_id": self.target_entity_id,
            "candidate_concept_ids": list(self.candidate_concept_ids),
            "conflicting_action_ids": list(self.conflicting_action_ids),
            "reason_id": self.reason_id,
        }


def AssertInferredTerm(
    arena: TermArena,
    predicate_id: int,
    arg0_id: int,
    rule_id: int,
    premise_ids: Tuple[int, ...],
    provenance: ProvenanceRecord,
    arg1_id: int = 0,
    arg2_id: int = 0,
    role0_id: int = 0,
    role1_id: int = 0,
    role2_id: int = 0,
    scope_id: int = 1,
    polarity: bool = True,
) -> AssertionResult:
    """
    Assert an INFERRED term into the Cognitive Core TermArena.
    
    Enforces:
    1. rule_id > 0
    2. len(premise_ids) > 0
    3. All premise terms exist and are active
    4. Strong Kleene conjunction of premises must evaluate to TRUE
       - If any premise is FALSE -> rejected (ASSERT_ERR_PREMISE_FALSE)
       - If any premise is UNKNOWN -> rejected (ASSERT_ERR_PREMISE_UNKNOWN)
    """
    if rule_id <= 0:
        return AssertionResult(
            success=False,
            term_id=0,
            error_code=ASSERT_ERR_MISSING_RULE,
            error_message="Inferred term requires positive numeric rule_id.",
        )

    if not premise_ids:
        return AssertionResult(
            success=False,
            term_id=0,
            error_code=ASSERT_ERR_MISSING_PREMISES,
            error_message="Inferred term requires at least one supporting premise.",
        )

    premise_terms: List[LogicalTerm] = []
    for pid in premise_ids:
        p_term = arena.get_term(pid)
        if p_term is None:
            return AssertionResult(
                success=False,
                term_id=0,
                error_code=ASSERT_ERR_PREMISE_NOT_FOUND,
                error_message=f"Supporting premise term_id={pid} not found in arena.",
            )
        if not p_term.is_active:
            return AssertionResult(
                success=False,
                term_id=0,
                error_code=ASSERT_ERR_PREMISE_INACTIVE,
                error_message=f"Supporting premise term_id={pid} is inactive/retracted.",
            )
        premise_terms.append(p_term)

    # Strong Kleene logic evaluation across all premises
    kleene_states = [EvaluateTermKleene(pt) for pt in premise_terms]
    conjunction_val = kleene_all(kleene_states)

    if conjunction_val == KleeneValue.FALSE:
        return AssertionResult(
            success=False,
            term_id=0,
            error_code=ASSERT_ERR_PREMISE_FALSE,
            error_message="Supporting premises conjunction evaluated to FALSE in Kleene logic.",
        )
    elif conjunction_val == KleeneValue.UNKNOWN:
        return AssertionResult(
            success=False,
            term_id=0,
            error_code=ASSERT_ERR_PREMISE_UNKNOWN,
            error_message="Supporting premises conjunction evaluated to UNKNOWN; certain inference prohibited.",
        )

    try:
        term_id = arena.allocate_term(
            predicate_id=predicate_id,
            arg0_id=arg0_id,
            arg1_id=arg1_id,
            arg2_id=arg2_id,
            role0_id=role0_id,
            role1_id=role1_id,
            role2_id=role2_id,
            scope_id=scope_id,
            epistemic_status=EpistemicStatus.INFERRED,
            polarity=polarity,
            rule_id=rule_id,
            premise_ids=premise_ids,
            provenance=provenance,
        )
        return AssertionResult(success=True, term_id=term_id)
    except ArenaCapacityExceededError as e:
        return AssertionResult(
            success=False,
            term_id=0,
            error_code=ASSERT_ERR_CAPACITY_EXCEEDED,
            error_message=str(e),
        )


def RetractAndCascadeInvalidate(arena: TermArena, term_id: int) -> List[int]:
    """
    Non-monotonic cascade invalidation (JTMS).
    
    When term_id is retracted:
    - Retracts term_id (marks is_active = False).
    - Recursively finds and invalidates all terms whose premise justifications
      depend on term_id (P1 -> P2 -> P3 -> P4).
    - Preserves independent FACTs and unlinked inferences intact.
    - Returns the list of all newly invalidated term IDs.
    """
    invalidated: List[int] = []
    to_visit: List[int] = [term_id]
    visited: Set[int] = set()

    while to_visit:
        curr_id = to_visit.pop(0)
        if curr_id in visited:
            continue
        visited.add(curr_id)

        target = arena.get_term(curr_id)
        if target and target.is_active:
            arena.retract_term(curr_id)
            invalidated.append(curr_id)

        # Find terms directly dependent on curr_id
        deps = arena.get_dependents(curr_id)
        for dep_id in deps:
            if dep_id not in visited:
                to_visit.append(dep_id)

    return invalidated


def EvaluateAmbiguity(
    arena: TermArena,
    target_entity_id: int,
    action_evaluator: Callable[[int], int],
) -> Tuple[bool, Optional[int], Optional[DisambiguationSubgoal]]:
    """
    Evaluate competing interpretations for an ambiguous entity or term.
    
    Invariant 4:
    - If all valid candidate concepts produce the same action: action may proceed.
    - If candidate concepts produce incompatible actions: do NOT guess.
      Emit a DisambiguationSubgoal.
    
    Returns:
        (proceed, common_action_id, disambiguation_subgoal)
    """
    entity = arena.get_entity(target_entity_id)
    if entity is None:
        return False, None, None

    candidates = entity.alternative_concept_ids
    if not candidates:
        # Single candidate or not ambiguous
        action = action_evaluator(entity.concept_id)
        return True, action, None

    # Evaluate action for each candidate branch
    action_to_concepts: Dict[int, List[int]] = {}
    actions: List[int] = []

    for cid in candidates:
        act = action_evaluator(cid)
        actions.append(act)
        if act not in action_to_concepts:
            action_to_concepts[act] = []
        action_to_concepts[act].append(cid)

    unique_actions = list(dict.fromkeys(actions))

    if len(unique_actions) == 1:
        # Unanimous / compatible outcome across all ambiguous interpretations
        return True, unique_actions[0], None

    # Incompatible actions -> produce DisambiguationSubgoal
    subgoal = DisambiguationSubgoal(
        target_entity_id=target_entity_id,
        candidate_concept_ids=tuple(candidates),
        conflicting_action_ids=tuple(unique_actions),
    )
    return False, None, subgoal
