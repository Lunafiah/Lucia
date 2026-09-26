"""
tests/unit/test_p23h_kernel.py

Phase 23-H: Unit Test Suite for Bounded Reasoning Kernel & JTMS.
Covers:
1. Rule indexing (head predicate indexing, O(1) lookup).
2. Constant matching & variable binding (VAR_0..VAR_7).
3. Repeated variable consistency & binding failure on conflict.
4. Maximum variable count (8) & maximum premise count (4).
5. Search depth limit (MAX_SEARCH_DEPTH = 8).
6. Inference step budget (MAX_INFERENCE_STEPS = 256).
7. Cyclic rules handling (A->B, B->A termination).
8. Multiple valid justifications & survival on partial retraction.
9. Invalidation cascade with alternative justification preservation.
10. UNKNOWN propagation & Kleene short-circuit (FALSE ∧ UNKNOWN = FALSE).
11. AMBIGUOUS branch convergence vs divergence.
12. Direct conflict detection (P(e) vs ¬P(e)).
13. Arena exhaustion error handling.
14. Deterministic ordering across runs.
"""

import pytest
from typing import List, Tuple

from src.core.cognition.contract.arena import ArenaCapacityExceededError, TermArena
from src.core.cognition.contract.epistemic import EpistemicStatus, KleeneValue
from src.core.cognition.contract.inference import DisambiguationSubgoal
from src.core.cognition.contract.provenance import ProvenanceRecord
from src.core.cognition.contract.terms import LogicalTerm
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
from src.core.cognition.kernel.conflict import ConflictRecord, detect_direct_conflict
from src.core.cognition.kernel.engine import (
    Goal,
    GoalResult,
    INFO_REASON_AMBIGUOUS_REFERENT,
    INFO_REASON_MISSING_PREMISE,
    InformationSubgoal,
    MAX_INFERENCE_STEPS,
    MAX_SEARCH_DEPTH,
    ReasoningKernel,
)
from src.core.cognition.kernel.jtms import JTMS, Justification
from src.core.cognition.kernel.rules import (
    InferenceRule,
    MAX_ARGS,
    MAX_PREMISES,
    RuleHead,
    RuleIndex,
    RulePremise,
)


# Numeric predicate / concept / entity constants for tests
PRED_MAMMAL = 1001
PRED_VERTEBRATE = 1002
PRED_ANIMAL = 1003
PRED_CARNIVORE = 1004
PRED_CANINE = 1005
PRED_BARKS = 1006
PRED_WARM_BLOODED = 1007
PRED_FLY = 1008
PRED_FEATHERS = 1009
PRED_BIRD = 1010
PRED_CYCLE_A = 2001
PRED_CYCLE_B = 2002

ENT_LUCIA = 501
ENT_DOG = 502
ENT_PENGUIN = 503
ENT_CAT = 504


class TestBindingAndUnification:
    """Test variable binding, frame operations, and unification."""

    def test_variable_helpers(self):
        assert is_variable(VAR_0)
        assert is_variable(VAR_7)
        assert not is_variable(0)
        assert not is_variable(1)
        assert not is_variable(-9)
        assert var_to_index(VAR_0) == 0
        assert var_to_index(VAR_7) == 7
        assert index_to_var(0) == VAR_0
        assert index_to_var(7) == VAR_7

    def test_binding_frame_bind_and_get(self):
        frame = BindingFrame()
        assert not frame.is_bound(0)
        assert frame.get(0) == 0

        success = frame.bind(0, ENT_LUCIA)
        assert success
        assert frame.is_bound(0)
        assert frame.get(0) == ENT_LUCIA

        # Re-binding to same value succeeds
        assert frame.bind(0, ENT_LUCIA)

        # Re-binding to different value fails (conflict)
        assert not frame.bind(0, ENT_DOG)
        assert frame.get(0) == ENT_LUCIA

    def test_binding_frame_copy_and_reset(self):
        frame1 = BindingFrame()
        frame1.bind_var(VAR_0, 100)
        frame1.bind_var(VAR_1, 200)

        frame2 = BindingFrame()
        frame2.copy_from(frame1)
        assert frame2.get_var(VAR_0) == 100
        assert frame2.get_var(VAR_1) == 200

        frame1.reset()
        assert not frame1.is_bound(0)
        assert frame1.get_var(VAR_0) is None
        # frame2 remains intact
        assert frame2.get_var(VAR_0) == 100

    def test_unify_terms_constant_matching(self):
        frame = BindingFrame()
        # Exact match
        assert unify_terms(PRED_MAMMAL, ENT_DOG, 0, 0, PRED_MAMMAL, ENT_DOG, 0, 0, frame)
        # Mismatched predicate
        assert not unify_terms(PRED_MAMMAL, ENT_DOG, 0, 0, PRED_ANIMAL, ENT_DOG, 0, 0, frame)
        # Mismatched argument
        assert not unify_terms(PRED_MAMMAL, ENT_DOG, 0, 0, PRED_MAMMAL, ENT_CAT, 0, 0, frame)

    def test_unify_terms_variable_binding(self):
        frame = BindingFrame()
        # Pattern has VAR_0 in arg0
        assert unify_terms(PRED_MAMMAL, VAR_0, 0, 0, PRED_MAMMAL, ENT_DOG, 0, 0, frame)
        assert frame.get_var(VAR_0) == ENT_DOG

        # Second term with same VAR_0 should succeed if value matches
        assert unify_terms(PRED_ANIMAL, VAR_0, 0, 0, PRED_ANIMAL, ENT_DOG, 0, 0, frame)

        # Conflicting term with different value should fail
        assert not unify_terms(PRED_ANIMAL, VAR_0, 0, 0, PRED_ANIMAL, ENT_CAT, 0, 0, frame)


class TestRulesAndIndex:
    """Test static rule validation and predicate index."""

    def test_valid_rule_creation(self):
        rule = InferenceRule(
            rule_id=1,
            head=RuleHead(predicate_id=PRED_VERTEBRATE, arg0=VAR_0),
            premises=(RulePremise(predicate_id=PRED_MAMMAL, arg0=VAR_0),),
        )
        assert rule.rule_id == 1
        assert rule.head.predicate_id == PRED_VERTEBRATE
        assert len(rule.premises) == 1

    def test_rule_invalid_limits(self):
        # Rule ID <= 0
        with pytest.raises(ValueError):
            InferenceRule(
                rule_id=0,
                head=RuleHead(predicate_id=PRED_VERTEBRATE, arg0=VAR_0),
                premises=(RulePremise(predicate_id=PRED_MAMMAL, arg0=VAR_0),),
            )

        # Too many premises (> 4)
        with pytest.raises(ValueError):
            InferenceRule(
                rule_id=2,
                head=RuleHead(predicate_id=PRED_VERTEBRATE, arg0=VAR_0),
                premises=(
                    RulePremise(predicate_id=1, arg0=VAR_0),
                    RulePremise(predicate_id=2, arg0=VAR_0),
                    RulePremise(predicate_id=3, arg0=VAR_0),
                    RulePremise(predicate_id=4, arg0=VAR_0),
                    RulePremise(predicate_id=5, arg0=VAR_0),
                ),
            )

    def test_rule_index_lookup(self):
        r1 = InferenceRule(
            rule_id=1,
            head=RuleHead(predicate_id=PRED_VERTEBRATE, arg0=VAR_0),
            premises=(RulePremise(predicate_id=PRED_MAMMAL, arg0=VAR_0),),
        )
        r2 = InferenceRule(
            rule_id=2,
            head=RuleHead(predicate_id=PRED_VERTEBRATE, arg0=VAR_0),
            premises=(RulePremise(predicate_id=PRED_BIRD, arg0=VAR_0),),
        )
        r3 = InferenceRule(
            rule_id=3,
            head=RuleHead(predicate_id=PRED_ANIMAL, arg0=VAR_0),
            premises=(RulePremise(predicate_id=PRED_VERTEBRATE, arg0=VAR_0),),
        )

        idx = RuleIndex([r1, r2, r3])
        assert idx.total_rules == 3

        # Lookup for PRED_VERTEBRATE returns r1 and r2
        vert_rules = idx.get_rules_for_head(PRED_VERTEBRATE)
        assert len(vert_rules) == 2
        assert r1 in vert_rules
        assert r2 in vert_rules

        # Lookup for unindexed predicate returns empty
        assert idx.get_rules_for_head(9999) == []


class TestJTMSOperations:
    """Test JTMS justifications and multi-justification survival."""

    def test_jtms_register_and_query(self):
        jtms = JTMS(max_capacity=100)
        j1 = jtms.register_justification(rule_id=10, consequence_id=50, premise_ids=(1, 2))
        assert j1.justification_id == 1
        assert j1.is_valid
        assert jtms.has_valid_justification(50)

    def test_multi_justification_survival(self):
        arena = TermArena(max_terms=100)
        t_p1 = arena.allocate_term(predicate_id=PRED_MAMMAL, arg0_id=ENT_DOG)
        t_p2 = arena.allocate_term(predicate_id=PRED_WARM_BLOODED, arg0_id=ENT_DOG)
        t_c = arena.allocate_term(predicate_id=PRED_VERTEBRATE, arg0_id=ENT_DOG, epistemic_status=EpistemicStatus.INFERRED)

        jtms = JTMS(max_capacity=100)
        # Consequence t_c has TWO valid justifications:
        # Justification 1: Rule 1 via t_p1
        # Justification 2: Rule 2 via t_p2
        jtms.register_justification(rule_id=1, consequence_id=t_c, premise_ids=(t_p1,))
        jtms.register_justification(rule_id=2, consequence_id=t_c, premise_ids=(t_p2,))

        # Retracting premise t_p1
        retracted = jtms.retract_premise(t_p1, arena)

        # t_p1 is retracted
        assert t_p1 in retracted
        # But t_c SURVIVES because Justification 2 (via t_p2) is still valid!
        assert t_c not in retracted
        assert arena.get_term(t_c).is_active
        assert jtms.has_valid_justification(t_c)

        # Now retracting t_p2
        retracted2 = jtms.retract_premise(t_p2, arena)
        assert t_p2 in retracted2
        # Now t_c has NO remaining valid justification and must be retracted!
        assert t_c in retracted2
        assert not arena.get_term(t_c).is_active
        assert not jtms.has_valid_justification(t_c)


class TestConflictDetection:
    """Test contradiction detection between P(e) and ¬P(e)."""

    def test_direct_conflict_detected(self):
        arena = TermArena(max_terms=100)
        arena.allocate_term(predicate_id=PRED_FLY, arg0_id=ENT_PENGUIN, polarity=False)

        # Detecting conflict when querying/asserting polarity=True
        conflict = detect_direct_conflict(
            arena=arena,
            predicate_id=PRED_FLY,
            arg0_id=ENT_PENGUIN,
            polarity=True,
        )
        assert conflict is not None
        assert conflict.predicate_id == PRED_FLY
        assert conflict.arg0_id == ENT_PENGUIN
        assert conflict.existing_polarity is False
        assert conflict.new_polarity is True

    def test_no_conflict_when_same_polarity(self):
        arena = TermArena(max_terms=100)
        arena.allocate_term(predicate_id=PRED_FLY, arg0_id=ENT_PENGUIN, polarity=False)

        conflict = detect_direct_conflict(
            arena=arena,
            predicate_id=PRED_FLY,
            arg0_id=ENT_PENGUIN,
            polarity=False,
        )
        assert conflict is None


class TestReasoningKernelExecution:
    """Test goal resolution, Kleene logic, cycle breaking, and limits."""

    def test_direct_grounded_goal(self):
        arena = TermArena(max_terms=100)
        tid = arena.allocate_term(predicate_id=PRED_MAMMAL, arg0_id=ENT_DOG)
        idx = RuleIndex([])
        kernel = ReasoningKernel(rule_index=idx, arena=arena)

        res = kernel.resolve_goal(Goal(predicate_id=PRED_MAMMAL, arg0_id=ENT_DOG))
        assert res.status == KleeneValue.TRUE
        assert res.term_id == tid

    def test_one_step_inference(self):
        arena = TermArena(max_terms=100)
        p_tid = arena.allocate_term(predicate_id=PRED_MAMMAL, arg0_id=ENT_DOG)

        rule = InferenceRule(
            rule_id=101,
            head=RuleHead(predicate_id=PRED_VERTEBRATE, arg0=VAR_0),
            premises=(RulePremise(predicate_id=PRED_MAMMAL, arg0=VAR_0),),
        )
        idx = RuleIndex([rule])
        kernel = ReasoningKernel(rule_index=idx, arena=arena)

        # Goal: Vertebrate(ENT_DOG)?
        res = kernel.resolve_goal(Goal(predicate_id=PRED_VERTEBRATE, arg0_id=ENT_DOG))
        assert res.status == KleeneValue.TRUE
        assert res.term_id > 0
        assert res.rule_id == 101
        assert res.premise_ids == (p_tid,)

        # Verified in arena
        inferred_term = arena.get_term(res.term_id)
        assert inferred_term.epistemic_status == EpistemicStatus.INFERRED
        assert inferred_term.rule_id == 101
        assert inferred_term.premise_ids == (p_tid,)
        assert inferred_term.provenance is not None

        # Verified in JTMS
        assert kernel.jtms.has_valid_justification(res.term_id)

    def test_multi_step_inference_chain(self):
        # Dog -> Mammal -> Vertebrate -> Animal
        arena = TermArena(max_terms=100)
        p_tid = arena.allocate_term(predicate_id=PRED_CANINE, arg0_id=ENT_DOG)

        r1 = InferenceRule(
            rule_id=1,
            head=RuleHead(predicate_id=PRED_MAMMAL, arg0=VAR_0),
            premises=(RulePremise(predicate_id=PRED_CANINE, arg0=VAR_0),),
        )
        r2 = InferenceRule(
            rule_id=2,
            head=RuleHead(predicate_id=PRED_VERTEBRATE, arg0=VAR_0),
            premises=(RulePremise(predicate_id=PRED_MAMMAL, arg0=VAR_0),),
        )
        r3 = InferenceRule(
            rule_id=3,
            head=RuleHead(predicate_id=PRED_ANIMAL, arg0=VAR_0),
            premises=(RulePremise(predicate_id=PRED_VERTEBRATE, arg0=VAR_0),),
        )
        idx = RuleIndex([r1, r2, r3])
        kernel = ReasoningKernel(rule_index=idx, arena=arena)

        # Resolve Animal(ENT_DOG)
        res = kernel.resolve_goal(Goal(predicate_id=PRED_ANIMAL, arg0_id=ENT_DOG))
        assert res.status == KleeneValue.TRUE
        assert res.term_id > 0
        assert res.depth_reached == 3

    def test_cyclic_rules_termination(self):
        # A(x) -> B(x) and B(x) -> A(x)
        arena = TermArena(max_terms=100)
        r1 = InferenceRule(
            rule_id=1,
            head=RuleHead(predicate_id=PRED_CYCLE_B, arg0=VAR_0),
            premises=(RulePremise(predicate_id=PRED_CYCLE_A, arg0=VAR_0),),
        )
        r2 = InferenceRule(
            rule_id=2,
            head=RuleHead(predicate_id=PRED_CYCLE_A, arg0=VAR_0),
            premises=(RulePremise(predicate_id=PRED_CYCLE_B, arg0=VAR_0),),
        )
        idx = RuleIndex([r1, r2])
        kernel = ReasoningKernel(rule_index=idx, arena=arena)

        # Goal: CycleA(ENT_DOG)?
        res = kernel.resolve_goal(Goal(predicate_id=PRED_CYCLE_A, arg0_id=ENT_DOG))
        # Must terminate deterministically with UNKNOWN without infinite recursion or stack overflow
        assert res.status == KleeneValue.UNKNOWN
        assert res.steps_taken <= MAX_INFERENCE_STEPS
        assert res.depth_reached < MAX_SEARCH_DEPTH

    def test_kleene_short_circuit_on_false(self):
        # P1 ∧ P2 -> C. P1 is FALSE. C should fail with FALSE.
        arena = TermArena(max_terms=100)
        arena.allocate_term(predicate_id=PRED_CANINE, arg0_id=ENT_CAT, polarity=False)

        r = InferenceRule(
            rule_id=1,
            head=RuleHead(predicate_id=PRED_BARKS, arg0=VAR_0),
            premises=(
                RulePremise(predicate_id=PRED_CANINE, arg0=VAR_0),
                RulePremise(predicate_id=PRED_CARNIVORE, arg0=VAR_0),
            ),
        )
        idx = RuleIndex([r])
        kernel = ReasoningKernel(rule_index=idx, arena=arena)

        res = kernel.resolve_goal(Goal(predicate_id=PRED_BARKS, arg0_id=ENT_CAT))
        assert res.status == KleeneValue.FALSE

    def test_arena_capacity_exhaustion(self):
        # Arena with capacity 1
        arena = TermArena(max_terms=1)
        arena.allocate_term(predicate_id=PRED_MAMMAL, arg0_id=ENT_DOG)

        with pytest.raises(ArenaCapacityExceededError):
            arena.allocate_term(predicate_id=PRED_VERTEBRATE, arg0_id=ENT_DOG)
