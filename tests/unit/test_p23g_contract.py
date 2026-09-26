"""
tests/unit/test_p23g_contract.py

Unit tests for Phase 23-G: Semantic Substrate -> Cognitive Core Contract.
Validates:
1. EpistemicStatus mapping & Strong Kleene Logic truth table
2. TermArena allocation, bounds enforcement, and arena exhaustion
3. TermQueryPattern matching and BindingSet variable binding
4. AssertInferredTerm epistemic safety and premise validation
5. Non-monotonic cascade invalidation (P1 -> P2 -> P3 -> P4)
6. Independent fact preservation during retraction
7. AMBIGUOUS evaluation (unanimous action vs DisambiguationSubgoal)
8. Substrate -> Terms projection and Intent Graph synthesis round-trip
"""

import pytest

from src.core.cognition.contract.arena import (
    ArenaCapacityExceededError,
    TermArena,
)
from src.core.cognition.contract.epistemic import (
    EpistemicStatus,
    KleeneValue,
    kleene_all,
    kleene_and,
    kleene_not,
    kleene_or,
)
from src.core.cognition.contract.inference import (
    ASSERT_ERR_CAPACITY_EXCEEDED,
    ASSERT_ERR_MISSING_PREMISES,
    ASSERT_ERR_MISSING_RULE,
    ASSERT_ERR_PREMISE_FALSE,
    ASSERT_ERR_PREMISE_UNKNOWN,
    ASSERT_SUCCESS,
    AssertInferredTerm,
    DisambiguationSubgoal,
    EvaluateAmbiguity,
    RetractAndCascadeInvalidate,
)
from src.core.cognition.contract.matcher import (
    EvaluateConjunctionKleene,
    EvaluateTermKleene,
    QueryTermPattern,
)
from src.core.cognition.contract.projection import (
    ProjectGraphToTerms,
    SymbolTable,
)
from src.core.cognition.contract.provenance import ProvenanceRecord
from src.core.cognition.contract.synthesis import SynthesizeIntentGraph
from src.core.cognition.contract.terms import (
    BindingSet,
    EntityTerm,
    LogicalTerm,
    TermQueryPattern,
)
from src.core.knowledge.fortification import (
    EpistemicState,
    ScopeBoundary,
    ScopeType,
    SemanticEdge,
    SemanticGraph,
    SemanticNode,
)
from src.core.knowledge.fortification import ProvenanceRecord as P23EProvenanceRecord


# ── 1. Kleene Truth Table & UNKNOWN Preservation ──────────────────────────────

def test_kleene_conjunction_truth_table():
    """Verify complete Strong Kleene conjunction truth table."""
    # FALSE ∧ x = FALSE
    assert kleene_and(KleeneValue.FALSE, KleeneValue.FALSE) == KleeneValue.FALSE
    assert kleene_and(KleeneValue.FALSE, KleeneValue.TRUE) == KleeneValue.FALSE
    assert kleene_and(KleeneValue.FALSE, KleeneValue.UNKNOWN) == KleeneValue.FALSE

    # TRUE ∧ x
    assert kleene_and(KleeneValue.TRUE, KleeneValue.FALSE) == KleeneValue.FALSE
    assert kleene_and(KleeneValue.TRUE, KleeneValue.TRUE) == KleeneValue.TRUE
    assert kleene_and(KleeneValue.TRUE, KleeneValue.UNKNOWN) == KleeneValue.UNKNOWN

    # UNKNOWN ∧ x
    assert kleene_and(KleeneValue.UNKNOWN, KleeneValue.FALSE) == KleeneValue.FALSE
    assert kleene_and(KleeneValue.UNKNOWN, KleeneValue.TRUE) == KleeneValue.UNKNOWN
    assert kleene_and(KleeneValue.UNKNOWN, KleeneValue.UNKNOWN) == KleeneValue.UNKNOWN


def test_kleene_unknown_preservation():
    """Mandatory: A ∧ UNKNOWN must never produce a certain conclusion."""
    assert kleene_and(KleeneValue.TRUE, KleeneValue.UNKNOWN) == KleeneValue.UNKNOWN
    assert kleene_and(KleeneValue.UNKNOWN, KleeneValue.UNKNOWN) == KleeneValue.UNKNOWN
    # Only FALSE can dominate UNKNOWN in conjunction
    assert kleene_and(KleeneValue.FALSE, KleeneValue.UNKNOWN) == KleeneValue.FALSE


def test_kleene_disjunction_and_negation():
    """Verify disjunction and negation under Strong Kleene."""
    assert kleene_or(KleeneValue.TRUE, KleeneValue.UNKNOWN) == KleeneValue.TRUE
    assert kleene_or(KleeneValue.FALSE, KleeneValue.UNKNOWN) == KleeneValue.UNKNOWN
    assert kleene_or(KleeneValue.UNKNOWN, KleeneValue.UNKNOWN) == KleeneValue.UNKNOWN

    assert kleene_not(KleeneValue.TRUE) == KleeneValue.FALSE
    assert kleene_not(KleeneValue.FALSE) == KleeneValue.TRUE
    assert kleene_not(KleeneValue.UNKNOWN) == KleeneValue.UNKNOWN


# ── 2. TermArena & Capacity Exhaustion ─────────────────────────────────────────

def test_arena_allocation_and_capacity_exhaustion():
    """Verify TermArena raises explicit error on capacity exhaustion; never silently truncate."""
    small_arena = TermArena(max_terms=3, max_entities=2, max_scopes=2)

    t1 = small_arena.allocate_term(predicate_id=101, arg0_id=1)
    t2 = small_arena.allocate_term(predicate_id=102, arg0_id=2)
    t3 = small_arena.allocate_term(predicate_id=103, arg0_id=3)
    assert t1 == 1 and t2 == 2 and t3 == 3
    assert small_arena.term_count == 3

    # Exceeding capacity must raise ArenaCapacityExceededError
    with pytest.raises(ArenaCapacityExceededError):
        small_arena.allocate_term(predicate_id=104, arg0_id=4)

    # Entities
    e1 = small_arena.allocate_entity(concept_id=201)
    e2 = small_arena.allocate_entity(concept_id=202)
    assert e1 == 1 and e2 == 2
    with pytest.raises(ArenaCapacityExceededError):
        small_arena.allocate_entity(concept_id=203)


# ── 3. TermQueryPattern & Matching ─────────────────────────────────────────────

def test_pattern_matching_with_variable_binding():
    """Verify TermQueryPattern matches numeric fields and unifies variables."""
    arena = TermArena(max_terms=10, max_entities=10)
    t1 = arena.allocate_term(predicate_id=101, arg0_id=1, arg1_id=2, role0_id=10, role1_id=20)
    t2 = arena.allocate_term(predicate_id=101, arg0_id=1, arg1_id=3, role0_id=10, role1_id=20)
    t3 = arena.allocate_term(predicate_id=102, arg0_id=1, arg1_id=2, role0_id=10, role1_id=20)

    # Exact query for predicate 101, arg1 = 2
    pat = TermQueryPattern(predicate_id=101, arg1_id=2)
    matches = QueryTermPattern(arena, pat)
    assert matches == [t1]

    # Query with variable binding: ?X = -1 for arg1
    bindings = BindingSet()
    pat_var = TermQueryPattern(predicate_id=101, arg1_id=-1)
    match_ids = QueryTermPattern(arena, pat_var, bindings=bindings)
    assert t1 in match_ids and t2 in match_ids
    # bindings should have recorded first unified value
    assert bindings.get(-1) is not None


# ── 4. AssertInferredTerm & Epistemic Safety ───────────────────────────────────

def test_assert_inferred_term_epistemic_safety():
    """Verify AssertInferredTerm requires rule, active premises, and Kleene validity."""
    arena = TermArena(max_terms=20, max_entities=10)

    # Setup fact premise
    fact_id = arena.allocate_term(predicate_id=101, arg0_id=1, epistemic_status=EpistemicStatus.FACT)
    # Setup unknown premise
    unknown_id = arena.allocate_term(predicate_id=102, arg0_id=2, epistemic_status=EpistemicStatus.UNKNOWN)

    prov = ProvenanceRecord(rule_id=1, supporting_premise_ids=(fact_id,))

    # 1. Missing rule_id rejected
    res_no_rule = AssertInferredTerm(
        arena, predicate_id=201, arg0_id=1, rule_id=0,
        premise_ids=(fact_id,), provenance=prov
    )
    assert not res_no_rule.success
    assert res_no_rule.error_code == ASSERT_ERR_MISSING_RULE

    # 2. Missing premises rejected
    res_no_prem = AssertInferredTerm(
        arena, predicate_id=201, arg0_id=1, rule_id=1,
        premise_ids=(), provenance=prov
    )
    assert not res_no_prem.success
    assert res_no_prem.error_code == ASSERT_ERR_MISSING_PREMISES

    # 3. Premise evaluating to UNKNOWN rejects certain inference
    prov_unk = ProvenanceRecord(rule_id=1, supporting_premise_ids=(unknown_id,))
    res_unk = AssertInferredTerm(
        arena, predicate_id=201, arg0_id=1, rule_id=1,
        premise_ids=(unknown_id,), provenance=prov_unk
    )
    assert not res_unk.success
    assert res_unk.error_code == ASSERT_ERR_PREMISE_UNKNOWN

    # 4. Valid premise asserts successfully
    res_ok = AssertInferredTerm(
        arena, predicate_id=201, arg0_id=1, rule_id=1,
        premise_ids=(fact_id,), provenance=prov
    )
    assert res_ok.success
    assert res_ok.term_id > 0
    inferred_term = arena.get_term(res_ok.term_id)
    assert inferred_term.epistemic_status == EpistemicStatus.INFERRED
    assert inferred_term.rule_id == 1
    assert inferred_term.premise_ids == (fact_id,)


# ── 5. Cascade Invalidation & Independent Fact Preservation ────────────────────

def test_cascade_invalidation_and_independent_facts():
    """
    Verify dependency tracking:
    P1 -> P2 -> P3 -> P4
    Retracting P1 invalidates P2, P3, P4.
    Independent FACT (F_ind) remains active.
    """
    arena = TermArena(max_terms=20, max_entities=10)

    # Independent fact
    f_ind = arena.allocate_term(predicate_id=999, arg0_id=99, epistemic_status=EpistemicStatus.FACT)

    # P1: Root fact
    p1 = arena.allocate_term(predicate_id=101, arg0_id=1, epistemic_status=EpistemicStatus.FACT)

    # P2 inferred from P1
    prov2 = ProvenanceRecord(rule_id=1, supporting_premise_ids=(p1,))
    res2 = AssertInferredTerm(arena, predicate_id=102, arg0_id=1, rule_id=1, premise_ids=(p1,), provenance=prov2)
    p2 = res2.term_id

    # P3 inferred from P2
    prov3 = ProvenanceRecord(rule_id=2, supporting_premise_ids=(p2,))
    res3 = AssertInferredTerm(arena, predicate_id=103, arg0_id=1, rule_id=2, premise_ids=(p2,), provenance=prov3)
    p3 = res3.term_id

    # P4 inferred from P3
    prov4 = ProvenanceRecord(rule_id=3, supporting_premise_ids=(p3,))
    res4 = AssertInferredTerm(arena, predicate_id=104, arg0_id=1, rule_id=3, premise_ids=(p3,), provenance=prov4)
    p4 = res4.term_id

    assert all(arena.get_term(t).is_active for t in (p1, p2, p3, p4, f_ind))

    # Retract P1
    invalidated = RetractAndCascadeInvalidate(arena, p1)
    assert p1 in invalidated
    assert p2 in invalidated
    assert p3 in invalidated
    assert p4 in invalidated

    # All P1..P4 are now inactive
    assert not arena.get_term(p1).is_active
    assert not arena.get_term(p2).is_active
    assert not arena.get_term(p3).is_active
    assert not arena.get_term(p4).is_active

    # Independent fact remains active!
    assert arena.get_term(f_ind).is_active


# ── 6. AMBIGUOUS Evaluation: Unanimous vs Subgoal ──────────────────────────────

def test_ambiguous_resolution_compatible_and_incompatible():
    """
    Invariant 4:
    - If all valid branches yield same action -> proceed.
    - If branches yield incompatible actions -> emit DisambiguationSubgoal.
    """
    arena = TermArena(max_terms=10, max_entities=10)

    # Entity with ambiguous concepts: 101 (bank_finance) and 102 (bank_river)
    ent_id = arena.allocate_entity(
        concept_id=100,  # general bank
        epistemic_status=EpistemicStatus.AMBIGUOUS,
        alternative_concept_ids=(101, 102),
    )

    # 1. Compatible action evaluator: both require action 500 (e.g. check_schedule)
    eval_compatible = lambda cid: 500
    proceed, act, subgoal = EvaluateAmbiguity(arena, ent_id, eval_compatible)
    assert proceed is True
    assert act == 500
    assert subgoal is None

    # 2. Incompatible action evaluator: 101 -> deposit (action 1), 102 -> fish (action 2)
    eval_conflicting = lambda cid: 1 if cid == 101 else 2
    proceed, act, subgoal = EvaluateAmbiguity(arena, ent_id, eval_conflicting)
    assert proceed is False
    assert act is None
    assert isinstance(subgoal, DisambiguationSubgoal)
    assert subgoal.target_entity_id == ent_id
    assert set(subgoal.candidate_concept_ids) == {101, 102}
    assert set(subgoal.conflicting_action_ids) == {1, 2}


# ── 7. Substrate -> Terms -> Substrate Round-Trip Fidelity ────────────────────

def test_substrate_terms_round_trip_fidelity():
    """Verify complete round-trip preservation of concepts, entities, scopes, epistemic states, provenance."""
    graph = SemanticGraph(session_id="session:test_roundtrip")
    graph.add_scope(ScopeBoundary("scope:modal_01", ScopeType.MODAL, "scope:root"))

    # Nodes
    event_node = SemanticNode(
        id="node:event_solve_01",
        epistemic_state=EpistemicState.INFERRED,
        concept_symbol="c:SOLVE_PROBLEM",
        scope_id="scope:modal_01",
        provenance=P23EProvenanceRecord(
            derivation_rule_id="RULE_ASSIST_SOLVE",
            supporting_premises=("node:premise_01",),
            originating_session_id="session:1",
            originating_turn_id="turn:1",
        ),
    )
    user_node = SemanticNode(
        id="ent:user",
        epistemic_state=EpistemicState.FACT,
        concept_symbol="c:USER",
        scope_id="scope:modal_01",
    )
    premise_node = SemanticNode(
        id="node:premise_01",
        epistemic_state=EpistemicState.FACT,
        concept_symbol="c:ASSIST",
        scope_id="scope:modal_01",
    )

    graph.add_node(event_node)
    graph.add_node(user_node)
    graph.add_node(premise_node)
    graph.add_edge(SemanticEdge("node:event_solve_01", "ent:user", ":ARG0"))
    graph.add_edge(SemanticEdge("node:event_solve_01", "node:premise_01", ":cause"))

    # Project to Terms
    arena = TermArena(max_terms=50, max_entities=50, max_scopes=10)
    sym_table = SymbolTable()
    proj_res = ProjectGraphToTerms(graph, arena, sym_table)
    assert proj_res.success
    assert proj_res.term_count >= 1
    assert proj_res.entity_count >= 1

    # Reconstruct Intent Graph
    synth_res = SynthesizeIntentGraph(arena, sym_table, session_id="session:test_roundtrip")
    assert synth_res.success
    reconstructed_graph = synth_res.graph
    assert reconstructed_graph is not None

    # Verify Preservations
    # 1. Scope
    assert "scope:modal_01" in reconstructed_graph.scopes
    assert reconstructed_graph.scopes["scope:modal_01"].scope_type == ScopeType.MODAL

    # 2. Nodes & Concepts
    assert "node:event_solve_01" in reconstructed_graph.nodes
    rec_event = reconstructed_graph.nodes["node:event_solve_01"]
    assert rec_event.concept_symbol == "c:SOLVE_PROBLEM"
    assert rec_event.epistemic_state == EpistemicState.INFERRED
    assert rec_event.provenance is not None
    assert rec_event.provenance.derivation_rule_id == "RULE_ASSIST_SOLVE"

    # 3. Entity
    assert "ent:user" in reconstructed_graph.nodes
    rec_user = reconstructed_graph.nodes["ent:user"]
    assert rec_user.concept_symbol == "c:USER"
    assert rec_user.epistemic_state == EpistemicState.FACT

    # 4. Edges
    arg0_edges = [e for e in reconstructed_graph.edges if e.source_id == "node:event_solve_01" and e.relation_role == ":ARG0"]
    assert len(arg0_edges) == 1
    assert arg0_edges[0].target_id == "ent:user"
