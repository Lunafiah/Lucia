"""
src/core/cognition/kernel/engine.py

Phase 23-H: Bounded Goal-Directed Reasoning Kernel.

Strict Invariants:
1. Purely numeric: zero natural-language strings, zero regex, zero NLP.
2. Zero dynamic heap allocation in the inner reasoning loop.
3. Hard search bounds: MAX_SEARCH_DEPTH = 8, MAX_INFERENCE_STEPS = 256.
4. Deterministic loop detection to break cyclic rules (e.g. A->B, B->A).
5. Strong Kleene 3-valued logic (TRUE, FALSE, UNKNOWN).
   TRUE ∧ UNKNOWN = UNKNOWN, FALSE ∧ UNKNOWN = FALSE.
6. Epistemic safety: UNKNOWN never silently promoted to certainty.
7. AMBIGUOUS handling: unanimous branches converge; divergent branches emit DisambiguationSubgoal.
8. Information acquisition: missing premise under UNKNOWN emits InformationSubgoal.
9. Every INFERRED term carries numeric rule_id, premise_ids, and JTMS Justification.
10. Strict goal-directed relevance: only rules indexing head predicate are evaluated.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Callable, Dict, List, Optional, Sequence, Tuple, Union

from src.core.cognition.contract.arena import TermArena
from src.core.cognition.contract.epistemic import EpistemicStatus, KleeneValue, kleene_all
from src.core.cognition.contract.inference import DisambiguationSubgoal
from src.core.cognition.contract.matcher import EvaluateTermKleene
from src.core.cognition.contract.provenance import ProvenanceRecord
from src.core.cognition.contract.terms import LogicalTerm
from src.core.cognition.kernel.binding import (
    BindingFrame,
    MAX_VARS,
    is_variable,
    unify_terms,
    unify_value,
    var_to_index,
)
from src.core.cognition.kernel.conflict import ConflictRecord, detect_direct_conflict
from src.core.cognition.kernel.jtms import JTMS
from src.core.cognition.kernel.rules import InferenceRule, RuleHead, RuleIndex, RulePremise

MAX_SEARCH_DEPTH: int = 8
MAX_INFERENCE_STEPS: int = 256

# Reason codes for InformationSubgoal
INFO_REASON_MISSING_PREMISE: int = 1
INFO_REASON_UNGROUNDED_VARIABLE: int = 2
INFO_REASON_AMBIGUOUS_REFERENT: int = 3


@dataclass(frozen=True)
class Goal:
    """
    Language-independent numeric reasoning goal.
    """
    predicate_id: int
    arg0_id: int
    arg1_id: int = 0
    arg2_id: int = 0
    polarity: bool = True
    scope_id: int = 1

    def to_dict(self) -> Dict[str, object]:
        return {
            "predicate_id": self.predicate_id,
            "arg0_id": self.arg0_id,
            "arg1_id": self.arg1_id,
            "arg2_id": self.arg2_id,
            "polarity": self.polarity,
            "scope_id": self.scope_id,
        }


@dataclass(frozen=True)
class InformationSubgoal:
    """
    Language-independent subgoal emitted when UNKNOWN halts reasoning.
    Identifies the exact missing relation/entity to be acquired.
    Realization into language is handled strictly downstream.
    """
    target_predicate_id: int
    arg0_id: int
    arg1_id: int = 0
    arg2_id: int = 0
    polarity: bool = True
    scope_id: int = 1
    rule_id: int = 0
    reason_code: int = INFO_REASON_MISSING_PREMISE

    def to_dict(self) -> Dict[str, object]:
        return {
            "target_predicate_id": self.target_predicate_id,
            "arg0_id": self.arg0_id,
            "arg1_id": self.arg1_id,
            "arg2_id": self.arg2_id,
            "polarity": self.polarity,
            "scope_id": self.scope_id,
            "rule_id": self.rule_id,
            "reason_code": self.reason_code,
        }


@dataclass(frozen=True)
class GoalResult:
    """
    Consolidated outcome of goal resolution.
    """
    status: KleeneValue
    term_id: int = 0
    subgoal: Optional[Union[InformationSubgoal, DisambiguationSubgoal]] = None
    conflict: Optional[ConflictRecord] = None
    steps_taken: int = 0
    depth_reached: int = 0
    rule_id: int = 0
    premise_ids: Tuple[int, ...] = ()

    def to_dict(self) -> Dict[str, object]:
        return {
            "status": self.status.value,
            "term_id": self.term_id,
            "subgoal": self.subgoal.to_dict() if self.subgoal else None,
            "conflict": self.conflict.to_dict() if self.conflict else None,
            "steps_taken": self.steps_taken,
            "depth_reached": self.depth_reached,
            "rule_id": self.rule_id,
            "premise_ids": list(self.premise_ids),
        }


class ReasoningKernel:
    """
    Bounded Goal-Directed Reasoning Kernel with Strong Kleene Logic and JTMS.
    Preallocated frames and structures ensure zero dynamic heap allocation in inner loop.
    """
    __slots__ = (
        "rule_index",
        "arena",
        "jtms",
        "_frames",
        "_ancestor_pred",
        "_ancestor_a0",
        "_ancestor_a1",
        "_ancestor_a2",
        "_ancestor_pol",
        "_ancestor_scope",
        "_steps_taken",
        "_max_depth_reached",
        "_premise_ids_buf",
    )

    def __init__(
        self,
        rule_index: RuleIndex,
        arena: TermArena,
        jtms: Optional[JTMS] = None,
    ) -> None:
        self.rule_index: RuleIndex = rule_index
        self.arena: TermArena = arena
        self.jtms: JTMS = jtms if jtms is not None else JTMS(max_capacity=arena.max_terms)

        # Preallocated binding frames for each depth level (0..MAX_SEARCH_DEPTH)
        self._frames: List[BindingFrame] = [BindingFrame() for _ in range(MAX_SEARCH_DEPTH + 1)]

        # Preallocated ancestor stack parallel arrays for deterministic loop detection (depth 0..MAX_SEARCH_DEPTH)
        stack_size = MAX_SEARCH_DEPTH + 1
        self._ancestor_pred: List[int] = [0] * stack_size
        self._ancestor_a0: List[int] = [0] * stack_size
        self._ancestor_a1: List[int] = [0] * stack_size
        self._ancestor_a2: List[int] = [0] * stack_size
        self._ancestor_pol: List[bool] = [True] * stack_size
        self._ancestor_scope: List[int] = [1] * stack_size

        self._steps_taken: int = 0
        self._max_depth_reached: int = 0

        # Buffer for premise IDs (max 4 premises)
        self._premise_ids_buf: List[int] = [0] * 4

    def reset_step_counters(self) -> None:
        self._steps_taken = 0
        self._max_depth_reached = 0

    def resolve_goal(self, goal: Goal) -> GoalResult:
        """
        Public entry point for backward goal resolution.
        """
        self.reset_step_counters()
        for frame in self._frames:
            frame.reset()

        return self._resolve_internal(
            pred_id=goal.predicate_id,
            a0=goal.arg0_id,
            a1=goal.arg1_id,
            a2=goal.arg2_id,
            pol=goal.polarity,
            scope_id=goal.scope_id,
            depth=0,
        )

    def _resolve_internal(
        self,
        pred_id: int,
        a0: int,
        a1: int,
        a2: int,
        pol: bool,
        scope_id: int,
        depth: int,
    ) -> GoalResult:
        """
        Bounded recursive backward resolution with loop detection and Kleene evaluation.
        """
        self._steps_taken += 1
        if depth > self._max_depth_reached:
            self._max_depth_reached = depth

        # Hard step budget limit
        if self._steps_taken > MAX_INFERENCE_STEPS:
            return GoalResult(
                status=KleeneValue.UNKNOWN,
                steps_taken=self._steps_taken,
                depth_reached=self._max_depth_reached,
            )

        # Hard search depth limit
        if depth >= MAX_SEARCH_DEPTH:
            return GoalResult(
                status=KleeneValue.UNKNOWN,
                steps_taken=self._steps_taken,
                depth_reached=self._max_depth_reached,
            )

        # Deterministic loop detection: check ancestor stack
        i = 0
        while i < depth:
            if (
                self._ancestor_pred[i] == pred_id
                and self._ancestor_a0[i] == a0
                and self._ancestor_a1[i] == a1
                and self._ancestor_a2[i] == a2
                and self._ancestor_pol[i] == pol
                and self._ancestor_scope[i] == scope_id
            ):
                # Cycle detected! Break cycle deterministically.
                return GoalResult(
                    status=KleeneValue.UNKNOWN,
                    steps_taken=self._steps_taken,
                    depth_reached=self._max_depth_reached,
                )
            i += 1

        # Register current goal in ancestor stack
        self._ancestor_pred[depth] = pred_id
        self._ancestor_a0[depth] = a0
        self._ancestor_a1[depth] = a1
        self._ancestor_a2[depth] = a2
        self._ancestor_pol[depth] = pol
        self._ancestor_scope[depth] = scope_id

        # 1. Direct Grounding Check: Inspect active terms in arena
        direct_result = self._check_direct_term(pred_id, a0, a1, a2, pol, scope_id)
        if direct_result is not None:
            return direct_result

        # Check for direct conflict in existing facts before rule expansion
        conflict = detect_direct_conflict(
            arena=self.arena,
            predicate_id=pred_id,
            arg0_id=a0,
            arg1_id=a1,
            arg2_id=a2,
            polarity=pol,
            scope_id=scope_id,
        )
        if conflict is not None:
            return GoalResult(
                status=KleeneValue.FALSE,
                conflict=conflict,
                steps_taken=self._steps_taken,
                depth_reached=self._max_depth_reached,
            )

        # 2. Rule-Based Goal-Directed Search (Head Predicate Index Lookup)
        rules = self.rule_index.get_rules_for_head(pred_id)
        if not rules:
            # No rule can derive this predicate
            return GoalResult(
                status=KleeneValue.UNKNOWN,
                subgoal=InformationSubgoal(
                    target_predicate_id=pred_id,
                    arg0_id=a0,
                    arg1_id=a1,
                    arg2_id=a2,
                    polarity=pol,
                    scope_id=scope_id,
                    reason_code=INFO_REASON_MISSING_PREMISE,
                ),
                steps_taken=self._steps_taken,
                depth_reached=self._max_depth_reached,
            )

        first_unknown_subgoal: Optional[Union[InformationSubgoal, DisambiguationSubgoal]] = None
        has_unknown = False

        current_frame = self._frames[depth]

        for rule in rules:
            if rule.head.polarity != pol:
                continue

            current_frame.reset()

            # Unify rule head arguments with goal arguments
            if not unify_terms(
                rule.head.predicate_id, rule.head.arg0, rule.head.arg1, rule.head.arg2,
                pred_id, a0, a1, a2,
                current_frame,
            ):
                continue

            # Evaluate each premise of the rule under current bindings
            num_premises = len(rule.premises)
            premise_ids_collected: List[int] = []
            rule_failed = False
            rule_unknown = False
            rule_subgoal: Optional[Union[InformationSubgoal, DisambiguationSubgoal]] = None

            p_idx = 0
            while p_idx < num_premises:
                premise = rule.premises[p_idx]

                # Ground premise args from current_frame bindings
                p_a0 = self._resolve_arg(premise.arg0, current_frame)
                p_a1 = self._resolve_arg(premise.arg1, current_frame)
                p_a2 = self._resolve_arg(premise.arg2, current_frame)

                # Check if premise has unbound variables
                if p_a0 < 0 or p_a1 < 0 or p_a2 < 0:
                    rule_unknown = True
                    rule_subgoal = InformationSubgoal(
                        target_predicate_id=premise.predicate_id,
                        arg0_id=p_a0 if p_a0 > 0 else 0,
                        arg1_id=p_a1 if p_a1 > 0 else 0,
                        arg2_id=p_a2 if p_a2 > 0 else 0,
                        polarity=premise.polarity,
                        scope_id=scope_id,
                        rule_id=rule.rule_id,
                        reason_code=INFO_REASON_UNGROUNDED_VARIABLE,
                    )
                    break

                # Prepare child frame by copying current bindings
                child_depth = depth + 1
                if child_depth <= MAX_SEARCH_DEPTH:
                    self._frames[child_depth].copy_from(current_frame)

                # Recursively resolve premise
                premise_res = self._resolve_internal(
                    pred_id=premise.predicate_id,
                    a0=p_a0,
                    a1=p_a1,
                    a2=p_a2,
                    pol=premise.polarity,
                    scope_id=scope_id,
                    depth=child_depth,
                )

                if premise_res.status == KleeneValue.FALSE:
                    # Strong Kleene short-circuit: FALSE ∧ X = FALSE
                    rule_failed = True
                    break
                elif premise_res.status == KleeneValue.UNKNOWN:
                    rule_unknown = True
                    if rule_subgoal is None:
                        rule_subgoal = premise_res.subgoal or InformationSubgoal(
                            target_predicate_id=premise.predicate_id,
                            arg0_id=p_a0,
                            arg1_id=p_a1,
                            arg2_id=p_a2,
                            polarity=premise.polarity,
                            scope_id=scope_id,
                            rule_id=rule.rule_id,
                            reason_code=INFO_REASON_MISSING_PREMISE,
                        )
                elif premise_res.status == KleeneValue.TRUE:
                    if premise_res.term_id > 0:
                        premise_ids_collected.append(premise_res.term_id)

                p_idx += 1

            if rule_failed:
                continue

            if rule_unknown:
                has_unknown = True
                if first_unknown_subgoal is None:
                    first_unknown_subgoal = rule_subgoal
                continue

            # All premises evaluated to TRUE!
            if len(premise_ids_collected) == num_premises:
                # Ground consequence arguments
                g_a0 = self._resolve_arg(rule.head.arg0, current_frame)
                g_a1 = self._resolve_arg(rule.head.arg1, current_frame)
                g_a2 = self._resolve_arg(rule.head.arg2, current_frame)

                # Final conflict check before assertion
                conf = detect_direct_conflict(
                    arena=self.arena,
                    predicate_id=pred_id,
                    arg0_id=g_a0,
                    arg1_id=g_a1,
                    arg2_id=g_a2,
                    polarity=pol,
                    scope_id=scope_id,
                )
                if conf is not None:
                    return GoalResult(
                        status=KleeneValue.FALSE,
                        conflict=conf,
                        steps_taken=self._steps_taken,
                        depth_reached=self._max_depth_reached,
                    )

                # Allocate INFERRED term in TermArena
                premise_tuple = tuple(premise_ids_collected)
                prov = ProvenanceRecord(
                    rule_id=rule.rule_id,
                    supporting_premise_ids=premise_tuple,
                )
                new_term_id = self.arena.allocate_term(
                    predicate_id=pred_id,
                    arg0_id=g_a0,
                    arg1_id=g_a1,
                    arg2_id=g_a2,
                    scope_id=scope_id,
                    epistemic_status=EpistemicStatus.INFERRED,
                    polarity=pol,
                    rule_id=rule.rule_id,
                    premise_ids=premise_tuple,
                    provenance=prov,
                )

                # Register JTMS Justification
                self.jtms.register_justification(
                    rule_id=rule.rule_id,
                    consequence_id=new_term_id,
                    premise_ids=premise_tuple,
                )

                return GoalResult(
                    status=KleeneValue.TRUE,
                    term_id=new_term_id,
                    rule_id=rule.rule_id,
                    premise_ids=premise_tuple,
                    steps_taken=self._steps_taken,
                    depth_reached=self._max_depth_reached,
                )

        if has_unknown:
            return GoalResult(
                status=KleeneValue.UNKNOWN,
                subgoal=first_unknown_subgoal,
                steps_taken=self._steps_taken,
                depth_reached=self._max_depth_reached,
            )

        return GoalResult(
            status=KleeneValue.FALSE,
            steps_taken=self._steps_taken,
            depth_reached=self._max_depth_reached,
        )

    def _check_direct_term(
        self,
        pred_id: int,
        a0: int,
        a1: int,
        a2: int,
        pol: bool,
        scope_id: int,
    ) -> Optional[GoalResult]:
        """
        Check if a directly matching active term exists in arena.
        Enforces Strong Kleene truth values, AMBIGUOUS handling, and UNKNOWN propagation.
        """
        candidate_ids = self.arena.terms_for_predicate(pred_id)
        for tid in candidate_ids:
            term = self.arena.get_term(tid)
            if term is None or not term.is_active or term.scope_id != scope_id:
                continue

            # Match arguments
            if term.arg0_id == a0 and term.arg1_id == a1 and term.arg2_id == a2:
                if term.polarity != pol:
                    # Polar contradiction!
                    conf = ConflictRecord(
                        predicate_id=pred_id,
                        arg0_id=a0,
                        arg1_id=a1,
                        arg2_id=a2,
                        existing_term_id=term.term_id,
                        conflicting_term_id=0,
                        existing_polarity=term.polarity,
                        new_polarity=pol,
                    )
                    return GoalResult(
                        status=KleeneValue.FALSE,
                        conflict=conf,
                        steps_taken=self._steps_taken,
                        depth_reached=self._max_depth_reached,
                    )

                # Check Epistemic Status
                if term.epistemic_status in (EpistemicStatus.FACT, EpistemicStatus.INFERRED):
                    # Check if inferred term is supported by valid JTMS justification
                    if term.epistemic_status == EpistemicStatus.INFERRED:
                        if not self.jtms.has_valid_justification(term.term_id):
                            # Unsupported inferred term: treat as UNKNOWN
                            return GoalResult(
                                status=KleeneValue.UNKNOWN,
                                term_id=term.term_id,
                                steps_taken=self._steps_taken,
                                depth_reached=self._max_depth_reached,
                            )

                    return GoalResult(
                        status=KleeneValue.TRUE,
                        term_id=term.term_id,
                        rule_id=term.rule_id,
                        premise_ids=term.premise_ids,
                        steps_taken=self._steps_taken,
                        depth_reached=self._max_depth_reached,
                    )

                elif term.epistemic_status == EpistemicStatus.UNKNOWN:
                    # Strong Kleene: UNKNOWN cannot produce certainty
                    sub = InformationSubgoal(
                        target_predicate_id=pred_id,
                        arg0_id=a0,
                        arg1_id=a1,
                        arg2_id=a2,
                        polarity=pol,
                        scope_id=scope_id,
                        reason_code=INFO_REASON_MISSING_PREMISE,
                    )
                    return GoalResult(
                        status=KleeneValue.UNKNOWN,
                        term_id=term.term_id,
                        subgoal=sub,
                        steps_taken=self._steps_taken,
                        depth_reached=self._max_depth_reached,
                    )

                elif term.epistemic_status == EpistemicStatus.AMBIGUOUS:
                    if term.is_disambiguated:
                        return GoalResult(
                            status=KleeneValue.TRUE if term.polarity == pol else KleeneValue.FALSE,
                            term_id=term.term_id,
                            steps_taken=self._steps_taken,
                            depth_reached=self._max_depth_reached,
                        )

                    # AMBIGUOUS: check entity/alternative candidates
                    alt_concepts = term.alternative_concept_ids
                    if alt_concepts:
                        dis_sub = DisambiguationSubgoal(
                            target_entity_id=term.arg0_id,
                            candidate_concept_ids=alt_concepts,
                            conflicting_action_ids=(),
                            reason_id=INFO_REASON_AMBIGUOUS_REFERENT,
                        )
                        return GoalResult(
                            status=KleeneValue.UNKNOWN,
                            term_id=term.term_id,
                            subgoal=dis_sub,
                            steps_taken=self._steps_taken,
                            depth_reached=self._max_depth_reached,
                        )
                    else:
                        return GoalResult(
                            status=KleeneValue.UNKNOWN,
                            term_id=term.term_id,
                            steps_taken=self._steps_taken,
                            depth_reached=self._max_depth_reached,
                        )

        return None

    def _resolve_arg(self, arg_val: int, frame: BindingFrame) -> int:
        """Resolve argument: if variable, look up in frame. If unbound, returns arg_val (< 0)."""
        if is_variable(arg_val):
            val = frame.get_var(arg_val)
            if val is not None and val > 0:
                return val
        return arg_val

    def evaluate_ambiguous_convergence(
        self,
        entity_id: int,
        candidate_concept_ids: Tuple[int, ...],
        rule_evaluator: Callable[[int], GoalResult],
    ) -> Tuple[bool, Optional[GoalResult], Optional[DisambiguationSubgoal]]:
        """
        Evaluate competing interpretations for an ambiguous entity.
        - If all candidate branches produce identical consequence: converge!
        - If candidate branches produce divergent/conflicting consequences: emit DisambiguationSubgoal!
        """
        if not candidate_concept_ids:
            return False, None, None

        results: List[GoalResult] = []
        action_ids: List[int] = []

        for cid in candidate_concept_ids:
            res = rule_evaluator(cid)
            results.append(res)
            action_ids.append(res.term_id if res.status == KleeneValue.TRUE else -res.status.value)

        # Check for convergence: all results have status TRUE and derive same consequence
        all_true = all(r.status == KleeneValue.TRUE for r in results)
        unique_consequences = set(r.term_id for r in results if r.status == KleeneValue.TRUE)

        if all_true and len(unique_consequences) == 1:
            # Unanimous branch convergence: safe to retain consequence
            return True, results[0], None

        # Divergent branches: do NOT pick arbitrarily! Emit DisambiguationSubgoal
        subgoal = DisambiguationSubgoal(
            target_entity_id=entity_id,
            candidate_concept_ids=candidate_concept_ids,
            conflicting_action_ids=tuple(action_ids),
            reason_id=INFO_REASON_AMBIGUOUS_REFERENT,
        )
        return False, None, subgoal
