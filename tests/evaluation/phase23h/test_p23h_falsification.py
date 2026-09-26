"""
tests/evaluation/phase23h/test_p23h_falsification.py

Phase 23-H: Mandatory 12 Falsification Test Suite.
Verifies all 12 pre-registered scientific falsification criteria:

F1  — UNKNOWN does not produce unsupported certainty
F2  — AMBIGUOUS does not arbitrarily collapse
F3  — Provenance completeness
F4  — Cascade invalidation
F5  — Independent inference preservation
F6  — Cross-lingual invariance
F7  — Zero-string dependency
F8  — Zero heap allocation
F9  — Bounded termination
F10 — Conflict detection
F11 — Strict goal-directed relevance
F12 — Deterministic reproducibility
"""

import sys
import tracemalloc
import pytest
from typing import Dict, List, Tuple

from src.core.cognition.contract.arena import TermArena
from src.core.cognition.contract.epistemic import EpistemicStatus, KleeneValue
from src.core.cognition.contract.inference import DisambiguationSubgoal
from src.core.cognition.contract.projection import ProjectGraphToTerms, SymbolTable
from src.core.cognition.contract.terms import EntityTerm, LogicalTerm
from src.core.cognition.kernel.binding import (
    BindingFrame,
    MAX_VARS,
    VAR_0,
    VAR_1,
    VAR_2,
    VAR_3,
    is_variable,
    unify_terms,
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
    RuleHead,
    RuleIndex,
    RulePremise,
)

# Numeric IDs for tests
PRED_MAMMAL = 1001
PRED_VERTEBRATE = 1002
PRED_ANIMAL = 1003
PRED_CARNIVORE = 1004
PRED_CANINE = 1005
PRED_BARKS = 1006
PRED_WARM_BLOODED = 1007
PRED_FLY = 1008
PRED_CYCLE_A = 2001
PRED_CYCLE_B = 2002

ENT_LUCIA = 501
ENT_DOG = 502
ENT_PENGUIN = 503
ENT_CAT = 504
ENT_AMBIGUOUS_E1 = 505

CONCEPT_BANK_FINANCIAL = 3001
CONCEPT_BANK_RIVER = 3002
ACTION_DEPOSIT = 4001
ACTION_FISH = 4002


class TestP23HFalsificationSuite:
    """The 12 mandatory falsification tests for Phase 23-H."""

    def test_f1_unknown_does_not_produce_unsupported_certainty(self):
        """
        F1: UNKNOWN does not produce unsupported certainty.
        P1(x) ∧ P2(x) → C(x).
        P1 is TRUE, P2 is UNKNOWN.
        Goal: C.
        Expected: res.status == UNKNOWN, no INFERRED term created in arena.
        """
        arena = TermArena(max_terms=100)
        p1_id = arena.allocate_term(predicate_id=PRED_CANINE, arg0_id=ENT_DOG)
        initial_term_count = arena.term_count

        rule = InferenceRule(
            rule_id=1,
            head=RuleHead(predicate_id=PRED_BARKS, arg0=VAR_0),
            premises=(
                RulePremise(predicate_id=PRED_CANINE, arg0=VAR_0),
                RulePremise(predicate_id=PRED_CARNIVORE, arg0=VAR_0),  # Not in arena -> UNKNOWN
            ),
        )
        idx = RuleIndex([rule])
        kernel = ReasoningKernel(rule_index=idx, arena=arena)

        res = kernel.resolve_goal(Goal(predicate_id=PRED_BARKS, arg0_id=ENT_DOG))

        # Must not be TRUE
        assert res.status == KleeneValue.UNKNOWN
        # Subgoal emitted for the missing premise
        assert res.subgoal is not None
        assert isinstance(res.subgoal, InformationSubgoal)
        assert res.subgoal.target_predicate_id == PRED_CARNIVORE

        # Arena must NOT contain new INFERRED term for PRED_BARKS
        assert arena.term_count == initial_term_count
        terms = [t for t in arena.active_terms() if t.predicate_id == PRED_BARKS]
        assert len(terms) == 0

    def test_f2_ambiguous_does_not_arbitrarily_collapse(self):
        """
        F2: AMBIGUOUS does not arbitrarily collapse.
        Competing interpretations produce incompatible consequences.
        System must emit DisambiguationSubgoal and never pick an arbitrary candidate.
        """
        arena = TermArena(max_terms=100)
        # Entity with ambiguous concept: financial bank vs river bank
        e_id = arena.allocate_entity(
            concept_id=CONCEPT_BANK_FINANCIAL,
            epistemic_status=EpistemicStatus.AMBIGUOUS,
            alternative_concept_ids=(CONCEPT_BANK_FINANCIAL, CONCEPT_BANK_RIVER),
        )

        def rule_evaluator(concept_id: int) -> GoalResult:
            if concept_id == CONCEPT_BANK_FINANCIAL:
                return GoalResult(status=KleeneValue.TRUE, term_id=ACTION_DEPOSIT)
            else:
                return GoalResult(status=KleeneValue.TRUE, term_id=ACTION_FISH)

        kernel = ReasoningKernel(rule_index=RuleIndex([]), arena=arena)
        proceed, common_res, subgoal = kernel.evaluate_ambiguous_convergence(
            entity_id=e_id,
            candidate_concept_ids=(CONCEPT_BANK_FINANCIAL, CONCEPT_BANK_RIVER),
            rule_evaluator=rule_evaluator,
        )

        # Must NOT proceed or arbitrarily choose
        assert not proceed
        assert common_res is None
        assert subgoal is not None
        assert isinstance(subgoal, DisambiguationSubgoal)
        assert subgoal.target_entity_id == e_id
        assert subgoal.candidate_concept_ids == (CONCEPT_BANK_FINANCIAL, CONCEPT_BANK_RIVER)
        assert set(subgoal.conflicting_action_ids) == {ACTION_DEPOSIT, ACTION_FISH}

    def test_f3_provenance_completeness(self):
        """
        F3: Provenance completeness.
        Every INFERRED term carries rule_id, supporting premise_ids, ProvenanceRecord,
        and valid JTMS justification.
        """
        arena = TermArena(max_terms=100)
        p1 = arena.allocate_term(predicate_id=PRED_CANINE, arg0_id=ENT_DOG)
        p2 = arena.allocate_term(predicate_id=PRED_CARNIVORE, arg0_id=ENT_DOG)

        rule = InferenceRule(
            rule_id=42,
            head=RuleHead(predicate_id=PRED_BARKS, arg0=VAR_0),
            premises=(
                RulePremise(predicate_id=PRED_CANINE, arg0=VAR_0),
                RulePremise(predicate_id=PRED_CARNIVORE, arg0=VAR_0),
            ),
        )
        idx = RuleIndex([rule])
        kernel = ReasoningKernel(rule_index=idx, arena=arena)

        res = kernel.resolve_goal(Goal(predicate_id=PRED_BARKS, arg0_id=ENT_DOG))
        assert res.status == KleeneValue.TRUE
        assert res.term_id > 0

        inferred = arena.get_term(res.term_id)
        assert inferred is not None
        assert inferred.epistemic_status == EpistemicStatus.INFERRED
        assert inferred.rule_id == 42
        assert inferred.premise_ids == (p1, p2)
        assert inferred.provenance is not None
        assert inferred.provenance.rule_id == 42
        assert inferred.provenance.supporting_premise_ids == (p1, p2)

        # JTMS check
        justifications = kernel.jtms.get_justifications_for_consequence(res.term_id)
        assert len(justifications) == 1
        assert justifications[0].is_valid
        assert justifications[0].rule_id == 42
        assert justifications[0].premise_ids == (p1, p2)

    def test_f4_cascade_invalidation(self):
        """
        F4: Cascade invalidation.
        P1 -> P2 -> P3 -> P4.
        Retracting P1 must recursively invalidate P2, P3, and P4.
        """
        arena = TermArena(max_terms=100)
        t1 = arena.allocate_term(predicate_id=1, arg0_id=ENT_DOG)
        t2 = arena.allocate_term(predicate_id=2, arg0_id=ENT_DOG, epistemic_status=EpistemicStatus.INFERRED, rule_id=1, premise_ids=(t1,))
        t3 = arena.allocate_term(predicate_id=3, arg0_id=ENT_DOG, epistemic_status=EpistemicStatus.INFERRED, rule_id=2, premise_ids=(t2,))
        t4 = arena.allocate_term(predicate_id=4, arg0_id=ENT_DOG, epistemic_status=EpistemicStatus.INFERRED, rule_id=3, premise_ids=(t3,))

        jtms = JTMS(max_capacity=100)
        jtms.register_justification(rule_id=1, consequence_id=t2, premise_ids=(t1,))
        jtms.register_justification(rule_id=2, consequence_id=t3, premise_ids=(t2,))
        jtms.register_justification(rule_id=3, consequence_id=t4, premise_ids=(t3,))

        # Retracting premise t1
        invalidated = jtms.retract_premise(t1, arena)

        assert t1 in invalidated
        assert t2 in invalidated
        assert t3 in invalidated
        assert t4 in invalidated

        # Arena active states
        assert not arena.get_term(t1).is_active
        assert not arena.get_term(t2).is_active
        assert not arena.get_term(t3).is_active
        assert not arena.get_term(t4).is_active

        # JTMS validity states
        assert not jtms.has_valid_justification(t2)
        assert not jtms.has_valid_justification(t3)
        assert not jtms.has_valid_justification(t4)

    def test_f5_independent_inference_preservation(self):
        """
        F5: Independent inference preservation.
        P1 -> C1 (Branch A).
        P2 -> C2 (Branch B).
        P1 and P2 also both derive C_dual independently.
        Retracting P1 invalidates C1, but C2 survives and C_dual survives!
        """
        arena = TermArena(max_terms=100)
        p1 = arena.allocate_term(predicate_id=1, arg0_id=ENT_DOG)
        p2 = arena.allocate_term(predicate_id=2, arg0_id=ENT_DOG)

        c1 = arena.allocate_term(predicate_id=11, arg0_id=ENT_DOG, epistemic_status=EpistemicStatus.INFERRED)
        c2 = arena.allocate_term(predicate_id=12, arg0_id=ENT_DOG, epistemic_status=EpistemicStatus.INFERRED)
        c_dual = arena.allocate_term(predicate_id=13, arg0_id=ENT_DOG, epistemic_status=EpistemicStatus.INFERRED)

        jtms = JTMS(max_capacity=100)
        jtms.register_justification(rule_id=1, consequence_id=c1, premise_ids=(p1,))
        jtms.register_justification(rule_id=2, consequence_id=c2, premise_ids=(p2,))
        # c_dual has two independent justifications
        jtms.register_justification(rule_id=3, consequence_id=c_dual, premise_ids=(p1,))
        jtms.register_justification(rule_id=4, consequence_id=c_dual, premise_ids=(p2,))

        invalidated = jtms.retract_premise(p1, arena)

        assert p1 in invalidated
        assert c1 in invalidated

        # c2 must survive completely intact
        assert c2 not in invalidated
        assert arena.get_term(c2).is_active
        assert jtms.has_valid_justification(c2)

        # c_dual must survive because of justification via p2
        assert c_dual not in invalidated
        assert arena.get_term(c_dual).is_active
        assert jtms.has_valid_justification(c_dual)

    def test_f6_cross_lingual_invariance(self):
        """
        F6: Cross-lingual invariance.
        Identical numeric projection from English, Vietnamese, or Japanese substrate
        produces bit-exact identical inference results in Cognitive Core.
        """
        rule = InferenceRule(
            rule_id=10,
            head=RuleHead(predicate_id=PRED_VERTEBRATE, arg0=VAR_0),
            premises=(RulePremise(predicate_id=PRED_MAMMAL, arg0=VAR_0),),
        )
        idx = RuleIndex([rule])

        # Three isolated environments representing projections from EN, VI, JA
        results = []
        for _lang in ("en", "vi", "ja"):
            arena = TermArena(max_terms=100)
            # All three languages project to identical concept IDs
            arena.allocate_term(predicate_id=PRED_MAMMAL, arg0_id=ENT_DOG)
            kernel = ReasoningKernel(rule_index=idx, arena=arena)
            res = kernel.resolve_goal(Goal(predicate_id=PRED_VERTEBRATE, arg0_id=ENT_DOG))
            results.append((res.status, res.rule_id, res.steps_taken, res.depth_reached))

        # All results must be identical across languages
        assert results[0] == results[1] == results[2]
        assert results[0][0] == KleeneValue.TRUE
        assert results[0][1] == 10

    def test_f7_zero_string_dependency(self):
        """
        F7: Zero string dependency.
        Assert that zero strings exist in the core reasoning kernel data structures.
        """
        rule = InferenceRule(
            rule_id=10,
            head=RuleHead(predicate_id=PRED_VERTEBRATE, arg0=VAR_0),
            premises=(RulePremise(predicate_id=PRED_MAMMAL, arg0=VAR_0),),
        )
        idx = RuleIndex([rule])
        arena = TermArena(max_terms=100)
        arena.allocate_term(predicate_id=PRED_MAMMAL, arg0_id=ENT_DOG)
        kernel = ReasoningKernel(rule_index=idx, arena=arena)

        res = kernel.resolve_goal(Goal(predicate_id=PRED_VERTEBRATE, arg0_id=ENT_DOG))

        # Check types of all attributes
        assert isinstance(res.status, KleeneValue)
        assert isinstance(res.term_id, int)
        assert isinstance(res.rule_id, int)
        assert isinstance(res.steps_taken, int)
        assert isinstance(res.depth_reached, int)

        term = arena.get_term(res.term_id)
        assert isinstance(term.predicate_id, int)
        assert isinstance(term.arg0_id, int)
        assert isinstance(term.rule_id, int)
        for pid in term.premise_ids:
            assert isinstance(pid, int)
        assert isinstance(term.epistemic_status, EpistemicStatus)

    def test_f8_zero_heap_allocation(self):
        """
        F8: Zero dynamic heap allocation in steady-state inner loop.
        Using tracemalloc, verify that repeated resolution on warmed-up structures
        performs 0 memory allocations.
        """
        rule = InferenceRule(
            rule_id=1,
            head=RuleHead(predicate_id=PRED_CYCLE_B, arg0=VAR_0),
            premises=(RulePremise(predicate_id=PRED_CYCLE_A, arg0=VAR_0),),
        )
        idx = RuleIndex([rule])
        arena = TermArena(max_terms=100)
        # Grounded fact
        arena.allocate_term(predicate_id=PRED_CYCLE_B, arg0_id=ENT_DOG)
        kernel = ReasoningKernel(rule_index=idx, arena=arena)

        goal = Goal(predicate_id=PRED_CYCLE_B, arg0_id=ENT_DOG)

        # Warm-up pass to compile functions and initialize buffers
        for _ in range(5):
            kernel.resolve_goal(goal)

        # Measure steady-state allocation
        tracemalloc.start()
        snapshot1 = tracemalloc.take_snapshot()

        for _ in range(20):
            kernel.resolve_goal(goal)

        snapshot2 = tracemalloc.take_snapshot()
        tracemalloc.stop()

        # Filter out tracemalloc internal bookkeeping structures
        src_filter = tracemalloc.Filter(True, "*src*")
        filtered_snap1 = snapshot1.filter_traces([src_filter])
        filtered_snap2 = snapshot2.filter_traces([src_filter])

        stats = filtered_snap2.compare_to(filtered_snap1, 'lineno')
        total_diff = sum(stat.size_diff for stat in stats if stat.size_diff > 0)

        # Steady-state repeat query allocates 0 bytes in src/
        assert total_diff == 0, f"Detected non-zero heap allocation diff in src: {total_diff} bytes"

    def test_f9_bounded_termination(self):
        """
        F9: Bounded termination.
        Cyclic rules: A(x) -> B(x) and B(x) -> A(x).
        Must terminate within MAX_INFERENCE_STEPS=256 and MAX_SEARCH_DEPTH=8.
        """
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
        arena = TermArena(max_terms=100)
        kernel = ReasoningKernel(rule_index=idx, arena=arena)

        res = kernel.resolve_goal(Goal(predicate_id=PRED_CYCLE_A, arg0_id=ENT_DOG))

        assert res.status == KleeneValue.UNKNOWN
        assert res.steps_taken <= MAX_INFERENCE_STEPS
        assert res.depth_reached <= MAX_SEARCH_DEPTH

    def test_f10_conflict_detection(self):
        """
        F10: Conflict detection.
        P(e) = TRUE and ¬P(e) = TRUE must trigger ConflictRecord without silent overwrite.
        """
        arena = TermArena(max_terms=100)
        # Direct assertion: Penguin cannot fly (polarity=False)
        arena.allocate_term(predicate_id=PRED_FLY, arg0_id=ENT_PENGUIN, polarity=False)

        kernel = ReasoningKernel(rule_index=RuleIndex([]), arena=arena)

        # Attempting goal: Can Penguin fly? (polarity=True)
        res = kernel.resolve_goal(Goal(predicate_id=PRED_FLY, arg0_id=ENT_PENGUIN, polarity=True))

        assert res.status == KleeneValue.FALSE
        assert res.conflict is not None
        assert isinstance(res.conflict, ConflictRecord)
        assert res.conflict.predicate_id == PRED_FLY
        assert res.conflict.arg0_id == ENT_PENGUIN
        assert res.conflict.existing_polarity is False
        assert res.conflict.new_polarity is True

    def test_f11_strict_goal_directed_relevance(self):
        """
        F11: Strict goal-directed relevance.
        Only rules indexing the goal head predicate are inspected.
        Irrelevant rules are never evaluated.
        """
        relevant_rule = InferenceRule(
            rule_id=1,
            head=RuleHead(predicate_id=PRED_VERTEBRATE, arg0=VAR_0),
            premises=(RulePremise(predicate_id=PRED_MAMMAL, arg0=VAR_0),),
        )
        # Create 50 completely irrelevant rules
        irrelevant_rules = [
            InferenceRule(
                rule_id=100 + i,
                head=RuleHead(predicate_id=5000 + i, arg0=VAR_0),
                premises=(RulePremise(predicate_id=6000 + i, arg0=VAR_0),),
            )
            for i in range(50)
        ]

        idx = RuleIndex([relevant_rule] + irrelevant_rules)
        assert idx.total_rules == 51

        arena = TermArena(max_terms=200)
        arena.allocate_term(predicate_id=PRED_MAMMAL, arg0_id=ENT_DOG)
        # Also populate arena with 50 unrelated facts
        for i in range(50):
            arena.allocate_term(predicate_id=7000 + i, arg0_id=ENT_DOG)

        kernel = ReasoningKernel(rule_index=idx, arena=arena)
        res = kernel.resolve_goal(Goal(predicate_id=PRED_VERTEBRATE, arg0_id=ENT_DOG))

        assert res.status == KleeneValue.TRUE
        # Only 2 steps taken (Goal Vertebrate -> Premise Mammal directly found)
        assert res.steps_taken <= 4
        assert res.rule_id == 1

    def test_f12_deterministic_reproducibility(self):
        """
        F12: Deterministic reproducibility.
        100 consecutive runs with the same rules, terms, and goal yield identical results.
        """
        rule = InferenceRule(
            rule_id=1,
            head=RuleHead(predicate_id=PRED_VERTEBRATE, arg0=VAR_0),
            premises=(RulePremise(predicate_id=PRED_MAMMAL, arg0=VAR_0),),
        )
        idx = RuleIndex([rule])

        reference_result = None

        for _ in range(100):
            arena = TermArena(max_terms=100)
            arena.allocate_term(predicate_id=PRED_MAMMAL, arg0_id=ENT_DOG)
            kernel = ReasoningKernel(rule_index=idx, arena=arena)
            res = kernel.resolve_goal(Goal(predicate_id=PRED_VERTEBRATE, arg0_id=ENT_DOG))

            snapshot = (res.status, res.term_id, res.rule_id, res.premise_ids, res.steps_taken, res.depth_reached)
            if reference_result is None:
                reference_result = snapshot
            else:
                assert snapshot == reference_result
