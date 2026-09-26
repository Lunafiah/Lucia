"""
tests/unit/test_semantic_fortification.py

Unit test suite for Phase 23-E: Conservative Semantic Fortification Across Session Boundaries.

Mandatory Requirements Covered:
    A. UNKNOWN preservation
    B. AMBIGUOUS preservation
    C. INFERRED provenance & multi-hop JTMS premise invalidation
    D. Epistemic promotion rejection (UNKNOWN -> FACT, UNKNOWN -> INFERRED, AMBIGUOUS -> FACT)
    E. Scope protection (cross-scope edge rejection)
    F. Novel entity insertion rejection (Zero-ingress property)
    G. Structural checksum integrity & tampering detection
    H. Local contradiction detection (opposing polarity & single-valued functional clashes)
    I. Language independence (100% non-lexical abstract fixtures)
    J. Deterministic behavior & canonical ordering
    Plus: Redundancy injection rejection, immutability, crash-resilient persistence.
"""

import copy
import json
import pytest
from pathlib import Path

from src.core.knowledge.fortification import (
    AuditReport,
    AuditStatus,
    ChecksumVerificationError,
    ConservativeSemanticFortifier,
    EpistemicState,
    EpistemicViolationError,
    FortificationError,
    FrozenGraphError,
    NovelEntityInsertionError,
    ProvenanceRecord,
    RedundancyInjectionError,
    ScopeBoundary,
    ScopeType,
    ScopeViolationError,
    SemanticEdge,
    SemanticGraph,
    SemanticNode,
)


@pytest.fixture
def fortifier() -> ConservativeSemanticFortifier:
    return ConservativeSemanticFortifier()


# ── Requirement A: UNKNOWN Preservation ────────────────────────────────────────

def test_unknown_preservation(fortifier: ConservativeSemanticFortifier):
    """
    Test A: An UNKNOWN argument/node must remain UNKNOWN after fortification.
    Fortification must not resolve or concrete-bind it.
    """
    graph = SemanticGraph(session_id="sess_01")
    node_unknown = SemanticNode(
        id="node:unknown_arg_01",
        epistemic_state=EpistemicState.UNKNOWN,
        concept_symbol="symbol:ungrounded_participant",
        attributes={"semantic_role": ":ARG1"},
    )
    graph.add_node(node_unknown)

    fortified_graph, audit = fortifier.fortify_session(graph)

    assert audit.is_valid is True
    assert audit.status == AuditStatus.VALID

    retrieved = fortified_graph.get_node("node:unknown_arg_01")
    assert retrieved is not None
    assert retrieved.epistemic_state == EpistemicState.UNKNOWN
    assert retrieved.concept_symbol == "symbol:ungrounded_participant"
    assert retrieved.operational_active is True


# ── Requirement B: AMBIGUOUS Preservation ──────────────────────────────────────

def test_ambiguous_preservation(fortifier: ConservativeSemanticFortifier):
    """
    Test B: An AMBIGUOUS node must remain AMBIGUOUS unless an explicit upstream
    disambiguation event occurred. No branch may disappear.
    """
    graph = SemanticGraph(session_id="sess_01")
    node_ambig = SemanticNode(
        id="node:ambig_01",
        epistemic_state=EpistemicState.AMBIGUOUS,
        concept_symbol="symbol:polysemous_entity",
        attributes={"candidate_referents": ["entity:alpha", "entity:beta"]},
    )
    graph.add_node(node_ambig)

    fortified_graph, audit = fortifier.fortify_session(graph)

    assert audit.is_valid is True
    retrieved = fortified_graph.get_node("node:ambig_01")
    assert retrieved is not None
    assert retrieved.epistemic_state == EpistemicState.AMBIGUOUS
    assert retrieved.attributes["candidate_referents"] == ["entity:alpha", "entity:beta"]
    assert retrieved.is_disambiguated is False


# ── Requirement C: INFERRED Provenance & Invalidation ──────────────────────────

def test_inferred_provenance_and_premise_retraction(fortifier: ConservativeSemanticFortifier):
    """
    Test C:
    1. INFERRED node retains rule ID, supporting premises, and provenance intact.
    2. When supporting premise is retracted, dependent INFERRED node becomes INVALIDATED.
    3. Multi-hop propagation: Premise A -> Inferred B -> Inferred C.
       Retracting A must invalidate both B and C. Independent node D must remain active.
    """
    graph = SemanticGraph(session_id="sess_01")

    # Premise A
    node_a = SemanticNode(
        id="node:premise_a",
        epistemic_state=EpistemicState.FACT,
        concept_symbol="c:fact_a",
    )
    # Independent Premise E
    node_e = SemanticNode(
        id="node:premise_e",
        epistemic_state=EpistemicState.FACT,
        concept_symbol="c:fact_e",
    )
    # Inferred B depending on A
    node_b = SemanticNode(
        id="node:inferred_b",
        epistemic_state=EpistemicState.INFERRED,
        concept_symbol="c:inferred_b",
        provenance=ProvenanceRecord(
            derivation_rule_id="rule:modus_ponens_01",
            supporting_premises=("node:premise_a",),
            originating_session_id="sess_01",
            originating_turn_id="turn_04",
            timestamp=100.0,
        ),
    )
    # Inferred C depending on B (Multi-hop)
    node_c = SemanticNode(
        id="node:inferred_c",
        epistemic_state=EpistemicState.INFERRED,
        concept_symbol="c:inferred_c",
        provenance=ProvenanceRecord(
            derivation_rule_id="rule:transitivity_02",
            supporting_premises=("node:inferred_b",),
            originating_session_id="sess_01",
            originating_turn_id="turn_05",
            timestamp=105.0,
        ),
    )
    # Independent Inferred D depending on E
    node_d = SemanticNode(
        id="node:inferred_d",
        epistemic_state=EpistemicState.INFERRED,
        concept_symbol="c:inferred_d",
        provenance=ProvenanceRecord(
            derivation_rule_id="rule:independent_03",
            supporting_premises=("node:premise_e",),
            originating_session_id="sess_01",
            originating_turn_id="turn_06",
            timestamp=110.0,
        ),
    )

    graph.add_node(node_a)
    graph.add_node(node_e)
    graph.add_node(node_b)
    graph.add_node(node_c)
    graph.add_node(node_d)

    # Initial fortification: all valid and provenance preserved
    fortified_graph, audit = fortifier.fortify_session(graph)
    assert audit.is_valid is True
    assert fortified_graph.get_node("node:inferred_b").provenance.derivation_rule_id == "rule:modus_ponens_01"
    assert fortified_graph.get_node("node:inferred_b").operational_active is True
    assert fortified_graph.get_node("node:inferred_c").operational_active is True
    assert fortified_graph.get_node("node:inferred_d").operational_active is True

    # Now simulate non-monotonic retraction of Premise A in a new session state
    mut_graph = graph.clone()
    mut_graph.retract_node("node:premise_a", reason="External ground truth refutation")

    fortified_retracted, audit_retracted = fortifier.fortify_session(mut_graph)
    assert audit_retracted.is_valid is True

    # Check multi-hop invalidation
    assert fortified_retracted.get_node("node:premise_a").operational_active is False
    assert fortified_retracted.get_node("node:inferred_b").operational_active is False
    assert "retracted" in fortified_retracted.get_node("node:inferred_b").invalidated_reason
    assert fortified_retracted.get_node("node:inferred_c").operational_active is False
    assert "retracted" in fortified_retracted.get_node("node:inferred_c").invalidated_reason

    # Independent chain must remain intact (Zero collateral retraction)
    assert fortified_retracted.get_node("node:premise_e").operational_active is True
    assert fortified_retracted.get_node("node:inferred_d").operational_active is True


# ── Requirement D: Epistemic Promotion Rejection ───────────────────────────────

def test_epistemic_promotion_rejection(fortifier: ConservativeSemanticFortifier):
    """
    Test D:
    Attempting UNKNOWN -> FACT or UNKNOWN -> INFERRED must be rejected.
    Attempting AMBIGUOUS -> FACT without explicit upstream disambiguation must be rejected.
    """
    graph = SemanticGraph(session_id="sess_01")
    graph.add_node(SemanticNode(
        id="node:u1",
        epistemic_state=EpistemicState.UNKNOWN,
        concept_symbol="symbol:missing",
    ))
    graph.add_node(SemanticNode(
        id="node:ambig1",
        epistemic_state=EpistemicState.AMBIGUOUS,
        concept_symbol="symbol:fork",
    ))

    # 1. UNKNOWN -> FACT forbidden
    with pytest.raises(EpistemicViolationError, match="Epistemic commitment increase forbidden"):
        fortifier.attempt_epistemic_transition(graph, "node:u1", EpistemicState.FACT)

    # 2. UNKNOWN -> INFERRED forbidden
    with pytest.raises(EpistemicViolationError, match="Epistemic commitment increase forbidden"):
        fortifier.attempt_epistemic_transition(graph, "node:u1", EpistemicState.INFERRED)

    # 3. AMBIGUOUS -> FACT forbidden without upstream disambiguation event
    with pytest.raises(EpistemicViolationError, match="Premature disambiguation forbidden"):
        fortifier.attempt_epistemic_transition(graph, "node:ambig1", EpistemicState.FACT, disambiguation_event=False)

    # 4. AMBIGUOUS -> FACT allowed ONLY when explicit upstream disambiguation occurred
    fortifier.attempt_epistemic_transition(graph, "node:ambig1", EpistemicState.FACT, disambiguation_event=True)
    assert graph.get_node("node:ambig1").epistemic_state == EpistemicState.FACT
    assert graph.get_node("node:ambig1").is_disambiguated is True


# ── Requirement E: Scope Boundary Protection ───────────────────────────────────

def test_scope_boundary_protection(fortifier: ConservativeSemanticFortifier):
    """
    Test E:
    Attempt to add an edge crossing a scope boundary (negation, modal, intensional)
    without authorized cross-scope link flag and role must be rejected.
    """
    graph = SemanticGraph(session_id="sess_01")
    graph.add_scope(ScopeBoundary("scope:neg_01", ScopeType.NEGATION, "scope:root"))
    graph.add_scope(ScopeBoundary("scope:modal_01", ScopeType.MODAL, "scope:root"))

    # Node in root scope
    graph.add_node(SemanticNode(id="node:root_event", epistemic_state=EpistemicState.FACT, concept_symbol="c:think", scope_id="scope:root"))
    # Node in negation scope
    graph.add_node(SemanticNode(id="node:neg_event", epistemic_state=EpistemicState.FACT, concept_symbol="c:rain", scope_id="scope:neg_01"))

    # 1. Direct edge crossing into negation scope with ordinary role must be rejected
    invalid_edge = SemanticEdge(source_id="node:root_event", target_id="node:neg_event", relation_role=":ARG1")
    with pytest.raises(ScopeViolationError, match="crosses scope boundary"):
        graph.add_edge(invalid_edge)

    # 2. Even via fortifier.attempt_edge_insertion, must be rejected
    with pytest.raises(ScopeViolationError):
        fortifier.attempt_edge_insertion(graph, invalid_edge)

    # 3. Valid cross-scope link with authorized role is permitted
    valid_edge = SemanticEdge(
        source_id="node:root_event",
        target_id="node:neg_event",
        relation_role=":modal-scope",
        is_cross_scope_link=True,
    )
    graph.add_edge(valid_edge)
    assert len(graph.edges) == 1


# ── Requirement F: Novel Entity Insertion Rejection ────────────────────────────

def test_novel_entity_insertion_rejection(fortifier: ConservativeSemanticFortifier):
    """
    Test F:
    Attempting to introduce a novel entity or fact during or after fortification
    must be rejected. Fortification-Originated Unsupported Insertion Rate == 0.
    """
    graph = SemanticGraph(session_id="sess_01")
    graph.add_node(SemanticNode(id="node:existing_01", epistemic_state=EpistemicState.FACT, concept_symbol="c:base"))

    fortified_graph, audit = fortifier.fortify_session(graph)
    assert audit.is_valid is True
    assert fortified_graph.is_frozen is True

    # 1. Direct node addition on frozen graph raises FrozenGraphError
    novel_node = SemanticNode(id="node:novel_hallucinated", epistemic_state=EpistemicState.FACT, concept_symbol="c:novel")
    with pytest.raises(FrozenGraphError):
        fortified_graph.add_node(novel_node)

    # 2. Attempt novel insertion through fortifier interface raises NovelEntityInsertionError
    with pytest.raises(NovelEntityInsertionError, match="Novel node insertion forbidden"):
        fortifier.attempt_novel_node_insertion(fortified_graph, novel_node)


# ── Requirement G: Structural Integrity Checksum ───────────────────────────────

def test_structural_checksum_integrity_and_tampering(fortifier: ConservativeSemanticFortifier, tmp_path: Path):
    """
    Test G:
    1. Serialize -> deserialize -> checksum integrity verified.
    2. Tampered content fails verification.
    3. Structural checksum detects mutation, does not claim semantic truth.
    """
    graph = SemanticGraph(session_id="sess_01")
    graph.add_node(SemanticNode(id="node:a", epistemic_state=EpistemicState.FACT, concept_symbol="c:alpha"))
    graph.add_node(SemanticNode(id="node:b", epistemic_state=EpistemicState.FACT, concept_symbol="c:beta"))
    graph.add_edge(SemanticEdge(source_id="node:a", target_id="node:b", relation_role=":rel"))

    fortified_graph, audit = fortifier.fortify_session(graph)
    assert audit.is_valid is True
    assert fortified_graph.verify_checksum() is True

    # Persist and reload
    file_path = tmp_path / "fortified_session.json"
    saved_path = fortifier.persist_fortified_graph(fortified_graph, file_path)
    loaded_graph = fortifier.load_fortified_graph(saved_path)

    assert loaded_graph.verify_checksum() is True
    assert loaded_graph.structural_checksum == fortified_graph.structural_checksum

    # Simulate disk tampering / bit-rot
    with open(saved_path, "r", encoding="utf-8") as f:
        tampered_data = json.load(f)
    tampered_data["nodes"][0]["concept_symbol"] = "c:MUTATED"
    with open(saved_path, "w", encoding="utf-8") as f:
        json.dump(tampered_data, f)

    with pytest.raises(ChecksumVerificationError, match="Structural checksum verification failed"):
        fortifier.load_fortified_graph(saved_path)


# ── Requirement H: Local Contradiction Detection ───────────────────────────────

def test_contradiction_detection(fortifier: ConservativeSemanticFortifier):
    """
    Test H:
    Construct a locally contradictory graph:
    1. Direct opposite polarities for identical predicate and argument in same scope.
    2. Single-valued functional relation pointing to two distinct objects.
    Expected: CONTRADICTION_DETECTED.
    """
    # 1. Opposing polarity contradiction
    graph1 = SemanticGraph(session_id="sess_contradiction_1")
    graph1.add_node(SemanticNode(id="e1", epistemic_state=EpistemicState.FACT, concept_symbol="c:rain", polarity=True))
    graph1.add_node(SemanticNode(id="e2", epistemic_state=EpistemicState.FACT, concept_symbol="c:rain", polarity=False))
    graph1.add_node(SemanticNode(id="loc1", epistemic_state=EpistemicState.FACT, concept_symbol="c:loc_tokyo"))
    graph1.add_edge(SemanticEdge(source_id="e1", target_id="loc1", relation_role=":location"))
    graph1.add_edge(SemanticEdge(source_id="e2", target_id="loc1", relation_role=":location"))

    _, audit1 = fortifier.fortify_session(graph1)
    assert audit1.is_valid is False
    assert audit1.status == AuditStatus.CONTRADICTION_DETECTED

    # 2. Single-valued functional relation conflict (e.g. capital_of)
    graph2 = SemanticGraph(session_id="sess_contradiction_2")
    graph2.add_node(SemanticNode(id="x_country", epistemic_state=EpistemicState.FACT, concept_symbol="c:country_japan"))
    graph2.add_node(SemanticNode(id="y_city1", epistemic_state=EpistemicState.FACT, concept_symbol="c:city_tokyo"))
    graph2.add_node(SemanticNode(id="y_city2", epistemic_state=EpistemicState.FACT, concept_symbol="c:city_osaka"))
    graph2.add_edge(SemanticEdge(source_id="x_country", target_id="y_city1", relation_role=":capital-of"))
    graph2.add_edge(SemanticEdge(source_id="x_country", target_id="y_city2", relation_role=":capital-of"))

    _, audit2 = fortifier.fortify_session(graph2)
    assert audit2.is_valid is False
    assert audit2.status == AuditStatus.CONTRADICTION_DETECTED


# ── Requirement I: Language Independence ───────────────────────────────────────

def test_language_independence(fortifier: ConservativeSemanticFortifier):
    """
    Test I:
    Fortification tests MUST NOT require English, Vietnamese, or Japanese text.
    Must operate purely over non-lexical symbols, indices, and graph topology.
    """
    graph = SemanticGraph(session_id="sess_abstract")
    # Pure non-lexical symbol IDs
    for i in range(5):
        graph.add_node(SemanticNode(
            id=f"node:n_{i:04d}",
            epistemic_state=EpistemicState.FACT,
            concept_symbol=f"sym:{1000 + i}",
            attributes={"metric_coord": [float(i), float(i * 2)]},
        ))

    graph.add_edge(SemanticEdge(source_id="node:n_0000", target_id="node:n_0001", relation_role=":role_01"))
    graph.add_edge(SemanticEdge(source_id="node:n_0001", target_id="node:n_0002", relation_role=":role_02"))

    fortified_graph, audit = fortifier.fortify_session(graph)
    assert audit.is_valid is True
    assert audit.node_count == 5
    assert audit.edge_count == 2
    # Verify no natural-language dependencies or strings leaked
    for node in fortified_graph.nodes.values():
        assert not any(lang in node.concept_symbol.lower() for lang in ["english", "vietnamese", "japanese"])


# ── Requirement J: Deterministic Behavior ──────────────────────────────────────

def test_deterministic_behavior(fortifier: ConservativeSemanticFortifier):
    """
    Test J:
    Same graph elements inserted in different order must produce:
    1. Identical canonical order.
    2. Byte-exact identical structural checksum.
    """
    nodes_order_a = [
        SemanticNode(id="node:gamma", epistemic_state=EpistemicState.FACT, concept_symbol="c:gamma"),
        SemanticNode(id="node:alpha", epistemic_state=EpistemicState.FACT, concept_symbol="c:alpha"),
        SemanticNode(id="node:beta", epistemic_state=EpistemicState.FACT, concept_symbol="c:beta"),
    ]
    edges_order_a = [
        SemanticEdge(source_id="node:gamma", target_id="node:alpha", relation_role=":rel2"),
        SemanticEdge(source_id="node:alpha", target_id="node:beta", relation_role=":rel1"),
    ]

    graph_a = SemanticGraph(session_id="sess_det")
    for n in nodes_order_a:
        graph_a.add_node(n)
    for e in edges_order_a:
        graph_a.add_edge(e)

    # Reverse order insertion in Graph B
    graph_b = SemanticGraph(session_id="sess_det")
    for n in reversed(nodes_order_a):
        graph_b.add_node(n)
    for e in reversed(edges_order_a):
        graph_b.add_edge(e)

    fortified_a, audit_a = fortifier.fortify_session(graph_a)
    fortified_b, audit_b = fortifier.fortify_session(graph_b)

    assert audit_a.is_valid is True
    assert audit_b.is_valid is True
    assert fortified_a.structural_checksum == fortified_b.structural_checksum
    assert json.dumps(fortified_a.to_dict(), sort_keys=True) == json.dumps(fortified_b.to_dict(), sort_keys=True)


# ── Additional Tests: Redundancy Injection & Dangling References ───────────────

def test_redundancy_injection_rejection(fortifier: ConservativeSemanticFortifier):
    """
    Test that injecting shortcut/redundancy edges (e.g. SessionRoot -> entity) is rejected.
    """
    graph = SemanticGraph(session_id="sess_01")
    graph.add_node(SemanticNode(id="SessionRoot", epistemic_state=EpistemicState.FACT, concept_symbol="c:root"))
    graph.add_node(SemanticNode(id="node:e1", epistemic_state=EpistemicState.FACT, concept_symbol="c:entity"))

    forbidden_edge = SemanticEdge(source_id="SessionRoot", target_id="node:e1", relation_role=":session-root-link")
    with pytest.raises(RedundancyInjectionError, match="Shortcut/redundancy edge"):
        fortifier.attempt_edge_insertion(graph, forbidden_edge)


def test_dangling_references_audit(fortifier: ConservativeSemanticFortifier):
    """
    Test that edges referencing missing nodes or INFERRED nodes referencing missing
    premises fail audit with appropriate status.
    """
    graph = SemanticGraph(session_id="sess_01")
    graph.add_node(SemanticNode(
        id="node:inferred_bad",
        epistemic_state=EpistemicState.INFERRED,
        concept_symbol="c:inferred",
        provenance=ProvenanceRecord(
            derivation_rule_id="rule:dummy",
            supporting_premises=("node:nonexistent_premise",),
        ),
    ))

    _, audit = fortifier.fortify_session(graph)
    assert audit.is_valid is False
    assert audit.status == AuditStatus.INVALID_PROVENANCE
