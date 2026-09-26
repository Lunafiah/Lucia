"""
tests/evaluation/phase23g/test_p23g_falsification.py

Phase 23-G Preregistered Falsification Test Suite:
Semantic Substrate -> Cognitive Core Contract.

1. FALSIFICATION-1: UNKNOWN Preservation (A ∧ UNKNOWN must never produce certain conclusion)
2. FALSIFICATION-2: Kleene Conjunction Truth Table (All 9 3-valued semantics verified)
3. FALSIFICATION-3: AMBIGUOUS Non-Collapse (Conflicting branches must generate DisambiguationSubgoal)
4. FALSIFICATION-4: Cross-Lingual Invariance (Parallel EN/VI/JA substrate graphs yield equivalent terms)
5. FALSIFICATION-5: Provenance Retention (Every INFERRED term retains rule_id and premise references)
6. FALSIFICATION-6: Cascade Invalidation (P1 -> P2 -> P3 -> P4 dependency invalidation)
7. FALSIFICATION-7: Independent-State Preservation (Retracting P1 preserves unrelated facts)
8. FALSIFICATION-8: Zero Dynamic Allocation (Inner reasoning loop allocates 0 dynamic bytes)
9. FALSIFICATION-9: String-Independence (Static audit confirms zero language strings inside Core)
10. FALSIFICATION-10: Arena Exhaustion (Exceeding capacity returns explicit failure; no silent truncation)
11. FALSIFICATION-11: Round-Trip Preservation (Substrate -> Terms -> Substrate preserves concepts, entities, scopes, epistemic states, provenance)
"""

import ast
import os
import tracemalloc
from pathlib import Path

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
    ASSERT_ERR_MISSING_PREMISES,
    ASSERT_ERR_MISSING_RULE,
    ASSERT_ERR_PREMISE_FALSE,
    ASSERT_ERR_PREMISE_UNKNOWN,
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
from src.core.language.adapter import (
    LanguageDriverRegistry,
    LanguageIngressGate,
)


# ── FALSIFICATION-1: UNKNOWN Preservation ─────────────────────────────────────

def test_falsification_1_unknown_preservation():
    """
    FALSIFICATION-1: UNKNOWN Preservation.
    Hypothesis: A ∧ UNKNOWN must never evaluate to TRUE (certainty).
    Falsification Condition: Any conjunction involving UNKNOWN producing TRUE falsifies the engine.
    """
    # 1. Direct Kleene evaluation
    assert kleene_and(KleeneValue.TRUE, KleeneValue.UNKNOWN) == KleeneValue.UNKNOWN
    assert kleene_and(KleeneValue.UNKNOWN, KleeneValue.TRUE) == KleeneValue.UNKNOWN
    assert kleene_and(KleeneValue.UNKNOWN, KleeneValue.UNKNOWN) == KleeneValue.UNKNOWN
    # Only FALSE can dominate UNKNOWN
    assert kleene_and(KleeneValue.FALSE, KleeneValue.UNKNOWN) == KleeneValue.FALSE

    # 2. In arena: Conjunction of a FACT and an UNKNOWN term
    arena = TermArena(max_terms=10)
    t_fact = arena.allocate_term(predicate_id=101, arg0_id=1, epistemic_status=EpistemicStatus.FACT)
    t_unk = arena.allocate_term(predicate_id=102, arg0_id=2, epistemic_status=EpistemicStatus.UNKNOWN)

    term_fact = arena.get_term(t_fact)
    term_unk = arena.get_term(t_unk)
    assert term_fact is not None and term_unk is not None

    conj_val = EvaluateConjunctionKleene([term_fact, term_unk])
    assert conj_val == KleeneValue.UNKNOWN

    # 3. Asserting an inferred conclusion from UNKNOWN premises is strictly rejected
    prov = ProvenanceRecord(rule_id=1, supporting_premise_ids=(t_unk,))
    res = AssertInferredTerm(
        arena,
        predicate_id=201,
        arg0_id=1,
        rule_id=1,
        premise_ids=(t_unk,),
        provenance=prov,
    )
    assert not res.success
    assert res.error_code == ASSERT_ERR_PREMISE_UNKNOWN


# ── FALSIFICATION-2: Kleene Conjunction Truth Table ───────────────────────────

def test_falsification_2_kleene_conjunction_truth_table():
    """
    FALSIFICATION-2: Kleene Conjunction Truth Table Completeness.
    Hypothesis: Strong Kleene 3-valued semantics must hold for all 3x3 combinations.
    Falsification Condition: Any cell diverging from standard Strong Kleene truth table falsifies.
    """
    expected_table = {
        (KleeneValue.FALSE, KleeneValue.FALSE): KleeneValue.FALSE,
        (KleeneValue.FALSE, KleeneValue.TRUE): KleeneValue.FALSE,
        (KleeneValue.FALSE, KleeneValue.UNKNOWN): KleeneValue.FALSE,
        (KleeneValue.TRUE, KleeneValue.FALSE): KleeneValue.FALSE,
        (KleeneValue.TRUE, KleeneValue.TRUE): KleeneValue.TRUE,
        (KleeneValue.TRUE, KleeneValue.UNKNOWN): KleeneValue.UNKNOWN,
        (KleeneValue.UNKNOWN, KleeneValue.FALSE): KleeneValue.FALSE,
        (KleeneValue.UNKNOWN, KleeneValue.TRUE): KleeneValue.UNKNOWN,
        (KleeneValue.UNKNOWN, KleeneValue.UNKNOWN): KleeneValue.UNKNOWN,
    }

    for (a, b), expected in expected_table.items():
        actual = kleene_and(a, b)
        assert actual == expected, f"Failed Strong Kleene {a.name} ∧ {b.name}: expected {expected.name}, got {actual.name}"


# ── FALSIFICATION-3: AMBIGUOUS Non-Collapse ────────────────────────────────────

def test_falsification_3_ambiguous_non_collapse():
    """
    FALSIFICATION-3: AMBIGUOUS Non-Collapse.
    Hypothesis: Conflicting interpretations must generate a DisambiguationSubgoal
    rather than choosing arbitrarily or picking a probabilistic default.
    """
    arena = TermArena(max_terms=10, max_entities=10)
    # Ambiguous entity with two competing hypotheses (e.g. Financial Bank vs River Bank)
    ambig_ent = arena.allocate_entity(
        concept_id=50,
        epistemic_status=EpistemicStatus.AMBIGUOUS,
        alternative_concept_ids=(51, 52),
    )

    # 1. When candidates produce conflicting actions -> must NOT collapse
    action_eval_conflicting = lambda cid: 100 if cid == 51 else 200
    proceed, act, subgoal = EvaluateAmbiguity(arena, ambig_ent, action_eval_conflicting)
    assert proceed is False
    assert act is None
    assert isinstance(subgoal, DisambiguationSubgoal)
    assert subgoal.target_entity_id == ambig_ent
    assert set(subgoal.candidate_concept_ids) == {51, 52}
    assert set(subgoal.conflicting_action_ids) == {100, 200}

    # 2. When candidates produce identical actions -> action may proceed
    action_eval_unanimous = lambda cid: 999
    proceed_u, act_u, subgoal_u = EvaluateAmbiguity(arena, ambig_ent, action_eval_unanimous)
    assert proceed_u is True
    assert act_u == 999
    assert subgoal_u is None


# ── FALSIFICATION-4: Cross-Lingual Invariance ──────────────────────────────────

def test_falsification_4_cross_lingual_invariance():
    """
    FALSIFICATION-4: Cross-Lingual Invariance.
    Hypothesis: Equivalent EN, VI, and JA substrate graphs produce identical
    LogicalTerms inside the Cognitive Core, with zero surface text in Core.
    """
    registry = LanguageDriverRegistry.create_default_registry()
    ingress_gate = LanguageIngressGate()

    # Parallel canonical inputs across three admitted languages
    en_text = "User solves the problem"
    vi_text = "Anh người dùng giải quyết cái vấn đề"
    ja_text = "ユーザーが問題を解決した"

    res_en = ingress_gate.admit_and_parse(en_text, "en", registry)
    res_vi = ingress_gate.admit_and_parse(vi_text, "vi", registry)
    res_ja = ingress_gate.admit_and_parse(ja_text, "ja", registry)

    shared_sym_table = SymbolTable()

    arena_en = TermArena(max_terms=20, max_entities=10)
    arena_vi = TermArena(max_terms=20, max_entities=10)
    arena_ja = TermArena(max_terms=20, max_entities=10)

    p_en = ProjectGraphToTerms(res_en.graph, arena_en, shared_sym_table)
    p_vi = ProjectGraphToTerms(res_vi.graph, arena_vi, shared_sym_table)
    p_ja = ProjectGraphToTerms(res_ja.graph, arena_ja, shared_sym_table)

    assert p_en.success and p_vi.success and p_ja.success

    # Verify that the primary active logical terms are isomorphic
    terms_en = arena_en.active_terms()
    terms_vi = arena_vi.active_terms()
    terms_ja = arena_ja.active_terms()

    assert len(terms_en) == len(terms_vi) == len(terms_ja) == 1

    t_en = terms_en[0]
    t_vi = terms_vi[0]
    t_ja = terms_ja[0]

    # Exactly identical predicate concept ID
    assert t_en.predicate_id == t_vi.predicate_id == t_ja.predicate_id
    assert shared_sym_table.get_concept_symbol(t_en.predicate_id) == "c:SOLVE_PROBLEM"

    # Exactly identical epistemic status
    assert t_en.epistemic_status == t_vi.epistemic_status == t_ja.epistemic_status == EpistemicStatus.FACT

    # Role mappings are identical
    assert t_en.role0_id == t_vi.role0_id == t_ja.role0_id
    assert shared_sym_table.get_role_symbol(t_en.role0_id) == ":ARG0"
    assert t_en.role1_id == t_vi.role1_id == t_ja.role1_id
    assert shared_sym_table.get_role_symbol(t_en.role1_id) == ":ARG1"


# ── FALSIFICATION-5: Provenance Retention ──────────────────────────────────────

def test_falsification_5_provenance_retention():
    """
    FALSIFICATION-5: Provenance Retention.
    Hypothesis: Every INFERRED term must contain rule_id and premise references.
    Falsification Condition: Creating an INFERRED term without rule/premise succeeds,
    or provenance is lost.
    """
    arena = TermArena(max_terms=20, max_entities=10)
    p1 = arena.allocate_term(predicate_id=101, arg0_id=1, epistemic_status=EpistemicStatus.FACT)

    # 1. Missing rule ID rejected
    res_no_rule = AssertInferredTerm(
        arena, predicate_id=201, arg0_id=1, rule_id=0, premise_ids=(p1,),
        provenance=ProvenanceRecord(rule_id=0, supporting_premise_ids=(p1,)),
    )
    assert not res_no_rule.success
    assert res_no_rule.error_code == ASSERT_ERR_MISSING_RULE

    # 2. Missing premises rejected
    res_no_prem = AssertInferredTerm(
        arena, predicate_id=201, arg0_id=1, rule_id=42, premise_ids=(),
        provenance=ProvenanceRecord(rule_id=42, supporting_premise_ids=()),
    )
    assert not res_no_prem.success
    assert res_no_prem.error_code == ASSERT_ERR_MISSING_PREMISES

    # 3. Valid inferred term retains complete provenance
    prov = ProvenanceRecord(rule_id=42, supporting_premise_ids=(p1,), session_id=1, turn_id=3)
    res_ok = AssertInferredTerm(
        arena, predicate_id=201, arg0_id=1, rule_id=42, premise_ids=(p1,),
        provenance=prov,
    )
    assert res_ok.success
    inf_term = arena.get_term(res_ok.term_id)
    assert inf_term is not None
    assert inf_term.rule_id == 42
    assert inf_term.premise_ids == (p1,)
    assert inf_term.provenance == prov


# ── FALSIFICATION-6: Cascade Invalidation ──────────────────────────────────────

def test_falsification_6_cascade_invalidation():
    """
    FALSIFICATION-6: Cascade Invalidation (JTMS Dependency Tracking).
    Hypothesis: Retracting P1 invalidates P2, P3, P4 where P1 -> P2 -> P3 -> P4.
    Falsification Condition: Any dependent inferred term remains active after premise retraction.
    """
    arena = TermArena(max_terms=20, max_entities=10)

    p1 = arena.allocate_term(predicate_id=101, arg0_id=1, epistemic_status=EpistemicStatus.FACT)

    # P2 depends on P1
    r2 = AssertInferredTerm(arena, predicate_id=102, arg0_id=1, rule_id=1, premise_ids=(p1,),
                            provenance=ProvenanceRecord(1, (p1,)))
    p2 = r2.term_id

    # P3 depends on P2
    r3 = AssertInferredTerm(arena, predicate_id=103, arg0_id=1, rule_id=2, premise_ids=(p2,),
                            provenance=ProvenanceRecord(2, (p2,)))
    p3 = r3.term_id

    # P4 depends on P3
    r4 = AssertInferredTerm(arena, predicate_id=104, arg0_id=1, rule_id=3, premise_ids=(p3,),
                            provenance=ProvenanceRecord(3, (p3,)))
    p4 = r4.term_id

    assert all(arena.get_term(t).is_active for t in (p1, p2, p3, p4))

    # Retract P1
    invalidated = RetractAndCascadeInvalidate(arena, p1)

    assert set(invalidated) == {p1, p2, p3, p4}
    assert not arena.get_term(p1).is_active
    assert not arena.get_term(p2).is_active
    assert not arena.get_term(p3).is_active
    assert not arena.get_term(p4).is_active


# ── FALSIFICATION-7: Independent-State Preservation ───────────────────────────

def test_falsification_7_independent_state_preservation():
    """
    FALSIFICATION-7: Independent-State Preservation.
    Hypothesis: Retracting P1 must not invalidate unrelated facts or parallel derivations.
    Falsification Condition: Unrelated facts or derivations are modified.
    """
    arena = TermArena(max_terms=20, max_entities=10)

    # Independent fact
    f_unrelated = arena.allocate_term(predicate_id=999, arg0_id=99, epistemic_status=EpistemicStatus.FACT)

    # Independent derivation branch: Q1 -> Q2
    q1 = arena.allocate_term(predicate_id=301, arg0_id=3, epistemic_status=EpistemicStatus.FACT)
    r_q2 = AssertInferredTerm(arena, predicate_id=302, arg0_id=3, rule_id=9, premise_ids=(q1,),
                              provenance=ProvenanceRecord(9, (q1,)))
    q2 = r_q2.term_id

    # Retracted branch: P1 -> P2
    p1 = arena.allocate_term(predicate_id=101, arg0_id=1, epistemic_status=EpistemicStatus.FACT)
    r_p2 = AssertInferredTerm(arena, predicate_id=102, arg0_id=1, rule_id=1, premise_ids=(p1,),
                              provenance=ProvenanceRecord(1, (p1,)))
    p2 = r_p2.term_id

    # Retract P1
    invalidated = RetractAndCascadeInvalidate(arena, p1)
    assert set(invalidated) == {p1, p2}

    # Independent facts and parallel derivations MUST remain active!
    assert arena.get_term(f_unrelated).is_active
    assert arena.get_term(q1).is_active
    assert arena.get_term(q2).is_active


# ── FALSIFICATION-8: Zero Dynamic Allocation ──────────────────────────────────

def test_falsification_8_zero_dynamic_allocation():
    """
    FALSIFICATION-8: Zero Dynamic Allocation in Inner Reasoning Loop.
    Hypothesis: Query operations in TermArena using preallocated output buffers
    perform zero dynamic allocations on the heap.
    Falsification Condition: Heap allocations occur inside the inner query loop.
    """
    arena = TermArena(max_terms=100, max_entities=50)
    for i in range(1, 21):
        arena.allocate_term(predicate_id=101, arg0_id=i)

    buf = [0] * 50
    pat = TermQueryPattern(predicate_id=101)

    # Warmup loop to eliminate Python interpreter bytecode/frame caching effects
    for _ in range(5):
        QueryTermPatternIntoBuffer(arena, pat, buf)

    tracemalloc.start()
    s1 = tracemalloc.take_snapshot()

    for _ in range(100):
        cnt = QueryTermPatternIntoBuffer(arena, pat, buf)

    s2 = tracemalloc.take_snapshot()
    tracemalloc.stop()

    assert cnt == 20

    # Filter out any internal tracemalloc overhead
    app_allocs = [
        st for st in s2.compare_to(s1, "lineno")
        if "tracemalloc" not in st.traceback[0].filename
    ]
    assert len(app_allocs) == 0, f"Detected dynamic heap allocations in query loop: {app_allocs}"


# ── FALSIFICATION-9: String-Independence Static Audit ─────────────────────────

def test_falsification_9_string_independence():
    """
    FALSIFICATION-9: String-Independence Static Code Audit.
    Hypothesis: Core contract modules (terms, arena, matcher, inference, epistemic)
    must not contain language-specific branches or surface grammar keywords.
    Falsification Condition: References to language codes ('en', 'vi', 'ja') or
    surface tokens found inside Core reasoning logic.
    """
    contract_dir = Path("src/core/cognition/contract")
    core_modules = ["terms.py", "arena.py", "matcher.py", "inference.py", "epistemic.py"]

    forbidden_keywords = ["'en'", '"en"', "'vi'", '"vi"', "'ja'", '"ja"', "english", "vietnamese", "japanese"]

    for mod_name in core_modules:
        file_path = contract_dir / mod_name
        assert file_path.exists(), f"Module {mod_name} missing"
        source = file_path.read_text(encoding="utf-8")

        for kw in forbidden_keywords:
            assert kw not in source.lower(), f"Forbidden language string '{kw}' detected in Core module {mod_name}"

        # Parse AST to ensure no syntax errors
        ast.parse(source)


# ── FALSIFICATION-10: Arena Exhaustion ────────────────────────────────────────

def test_falsification_10_arena_exhaustion():
    """
    FALSIFICATION-10: Arena Exhaustion.
    Hypothesis: Exceeding TermArena capacity returns an explicit failure
    and never silently overwrites or truncates.
    Falsification Condition: Allocations beyond capacity succeed silently or overwrite.
    """
    arena = TermArena(max_terms=5, max_entities=3, max_scopes=2)

    for i in range(1, 6):
        tid = arena.allocate_term(predicate_id=100 + i, arg0_id=i)
        assert tid == i

    assert arena.term_count == 5

    # 6th term must raise ArenaCapacityExceededError
    with pytest.raises(ArenaCapacityExceededError):
        arena.allocate_term(predicate_id=106, arg0_id=6)

    # Verify no corruption or silent truncation of term 1..5
    for i in range(1, 6):
        t = arena.get_term(i)
        assert t is not None
        assert t.predicate_id == 100 + i


# ── FALSIFICATION-11: Round-Trip Preservation ─────────────────────────────────

def test_falsification_11_round_trip_preservation():
    """
    FALSIFICATION-11: Round-Trip Preservation.
    Hypothesis: Substrate -> Terms -> Substrate preserves concepts, entities,
    scope boundaries, epistemic states, and provenance links bit-exact.
    Falsification Condition: Concept/entity loss, scope mutation, or epistemic promotion.
    """
    # Create source graph with all 4 epistemic states and scopes
    src_graph = SemanticGraph(session_id="session:rt_falsification")
    src_graph.add_scope(ScopeBoundary("scope:neg_01", ScopeType.NEGATION, "scope:root"))

    # FACT entity
    src_graph.add_node(SemanticNode("ent:user", EpistemicState.FACT, "c:USER"))
    # UNKNOWN entity
    src_graph.add_node(SemanticNode("ent:unknown_agent", EpistemicState.UNKNOWN, "c:UNKNOWN_REFERENT"))
    # AMBIGUOUS entity
    src_graph.add_node(SemanticNode(
        "ent:bank", EpistemicState.AMBIGUOUS, "c:BANK",
        attributes={"alternative_hypotheses": ["c:FINANCIAL_BANK", "c:RIVER_BANK"]}
    ))
    # INFERRED event in negation scope
    src_graph.add_node(SemanticNode(
        "node:event_solve", EpistemicState.INFERRED, "c:SOLVE_PROBLEM",
        scope_id="scope:neg_01", polarity=False,
        provenance=P23EProvenanceRecord(
            derivation_rule_id="RULE_MODUS_TOLLENS",
            supporting_premises=("node:premise_01",),
        )
    ))
    src_graph.add_node(SemanticNode("node:premise_01", EpistemicState.FACT, "c:ASSIST", scope_id="scope:neg_01"))

    src_graph.add_edge(SemanticEdge("node:event_solve", "ent:user", ":ARG0", is_cross_scope_link=True))
    src_graph.add_edge(SemanticEdge("node:event_solve", "node:premise_01", ":cause"))

    # Project to Terms
    arena = TermArena(max_terms=50, max_entities=50, max_scopes=10)
    sym_table = SymbolTable()
    proj = ProjectGraphToTerms(src_graph, arena, sym_table)
    assert proj.success

    # Synthesize back to Intent Substrate Graph
    synth = SynthesizeIntentGraph(arena, sym_table, session_id="session:rt_falsification")
    assert synth.success
    dst_graph = synth.graph
    assert dst_graph is not None

    # Verify Scope
    assert "scope:neg_01" in dst_graph.scopes
    assert dst_graph.scopes["scope:neg_01"].scope_type == ScopeType.NEGATION

    # Verify FACT node
    assert dst_graph.nodes["ent:user"].epistemic_state == EpistemicState.FACT
    assert dst_graph.nodes["ent:user"].concept_symbol == "c:USER"

    # Verify UNKNOWN node
    assert dst_graph.nodes["ent:unknown_agent"].epistemic_state == EpistemicState.UNKNOWN

    # Verify AMBIGUOUS node & alternative hypotheses
    assert dst_graph.nodes["ent:bank"].epistemic_state == EpistemicState.AMBIGUOUS
    assert dst_graph.nodes["ent:bank"].attributes.get("alternative_hypotheses") == ["c:FINANCIAL_BANK", "c:RIVER_BANK"]

    # Verify INFERRED node & provenance
    inf_node = dst_graph.nodes["node:event_solve"]
    assert inf_node.epistemic_state == EpistemicState.INFERRED
    assert inf_node.polarity is False
    assert inf_node.provenance is not None
    assert inf_node.provenance.derivation_rule_id == "RULE_MODUS_TOLLENS"

    # Verify Edges
    edges = dst_graph.get_edges_for_node("node:event_solve")
    role_set = {e.relation_role for e in edges}
    assert ":ARG0" in role_set
    assert ":cause" in role_set
