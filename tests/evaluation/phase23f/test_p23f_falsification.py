"""
tests/evaluation/phase23f/test_p23f_falsification.py

Phase 23-F Preregistered Falsification Tests:
1. FALSIFICATION-1: Unsupported Language Ingress Leakage
2. FALSIFICATION-2: Substrate Language-Independence & Purity
3. FALSIFICATION-3: Epistemic Preservation Across Boundary Round-Trip
4. FALSIFICATION-4: Cross-Lingual Semantic Invariance on Parallel Inputs
"""

import pytest

from src.core.knowledge.fortification import (
    ConservativeSemanticFortifier,
    EpistemicState,
    SemanticGraph,
)
from src.core.language.adapter import (
    EgressGateBlockedError,
    EpistemicLeakageError,
    GateVerdict,
    IngressGateBlockedError,
    LanguageDriverRegistry,
    LanguageEgressGate,
    LanguageIngressGate,
    SubstrateViolationError,
)


@pytest.fixture
def registry() -> LanguageDriverRegistry:
    return LanguageDriverRegistry.create_default_registry()


@pytest.fixture
def ingress_gate() -> LanguageIngressGate:
    return LanguageIngressGate()


@pytest.fixture
def egress_gate() -> LanguageEgressGate:
    return LanguageEgressGate()


@pytest.fixture
def fortifier() -> ConservativeSemanticFortifier:
    return ConservativeSemanticFortifier()


# ── FALSIFICATION-1: Ingress Gate Leakage ──────────────────────────────────────

def test_falsification_1_ingress_gate_leakage(
    ingress_gate: LanguageIngressGate,
    registry: LanguageDriverRegistry,
):
    """
    FALSIFICATION-1: Ingress Gate Leakage / Rejection of Unsupported Languages.
    
    Hypothesis: The Ingress Gate strictly confines ingress to {vi, en, ja}.
    Falsification Condition: If any unsupported language (e.g. fr, de, zh, es, ru, ko, unknown)
    passes into the Core or Substrate without being blocked, Falsification-1 triggers.
    """
    unsupported_cases = [
        ("fr", "Bonjour, comment ça va?"),
        ("de", "Guten Morgen, mein Freund"),
        ("zh", "用户解决了这个问题"),
        ("es", "El usuario resolvió el problema"),
        ("ru", "Пользователь решил проблему"),
        ("ko", "사용자가 문제를 해결했습니다"),
        ("it", "L'utente ha risolto il problema"),
        ("unknown", "Xyzzy foobar baz"),
    ]

    leakage_detected = False
    blocked_count = 0

    for lang, text in unsupported_cases:
        verdict_report = ingress_gate.evaluate_language(lang)
        if verdict_report.verdict != GateVerdict.BLOCKED:
            leakage_detected = True
            break

        try:
            ingress_gate.admit_and_parse(text, lang, registry)
            leakage_detected = True  # If execution reaches here, gate leaked!
            break
        except IngressGateBlockedError:
            blocked_count += 1

    # Falsification Assertion: ZERO leakage permitted
    assert not leakage_detected, "FALSIFICATION-1 TRIGGERED: Ingress Gate permitted unsupported language!"
    assert blocked_count == len(unsupported_cases)


# ── FALSIFICATION-2: Substrate Language-Independence & Purity ─────────────────

def test_falsification_2_substrate_language_independence(
    ingress_gate: LanguageIngressGate,
    registry: LanguageDriverRegistry,
    fortifier: ConservativeSemanticFortifier,
):
    """
    FALSIFICATION-2: Substrate Language-Independence & Purity.
    
    Hypothesis: The Semantic Substrate (graph nodes, edges, predicates, scopes) contains
    ZERO natural-language word tokens, morphology, POS tags, or grammar-specific rules.
    Falsification Condition: If node IDs or concept symbols contain language prefixes,
    POS tags (e.g. 'pos:NN'), word tokens (e.g. 'word:the'), or language-specific branching
    in Fortification, Falsification-2 triggers.
    """
    inputs = [
        ("en", "User solves the problem"),
        ("vi", "Người dùng giải quyết vấn đề"),
        ("ja", "ユーザーが問題を解決した"),
    ]

    forbidden_tokens = {"the", "a", "cái", "con", "người", "が", "を", "した", "pos:", "word:", "token:"}

    for lang, text in inputs:
        result = ingress_gate.admit_and_parse(text, lang, registry)
        graph = result.graph

        for node_id, node in graph.nodes.items():
            # Verify no language token leakage in node id
            for tok in forbidden_tokens:
                assert tok not in node_id.lower(), f"FALSIFICATION-2 TRIGGERED: Node ID '{node_id}' contains token '{tok}'"
                assert tok not in node.concept_symbol.lower(), f"FALSIFICATION-2 TRIGGERED: Concept symbol '{node.concept_symbol}' contains token '{tok}'"

            # Concept symbol must start with abstract prefix (c: or ent:)
            assert node.concept_symbol.startswith(("c:", "ent:", "e:")), f"Invalid concept symbol prefix: {node.concept_symbol}"

        # Fortification must audit cleanly without language rules
        fortified_graph, audit = fortifier.fortify_session(graph)
        assert audit.is_valid, f"Fortification failed for {lang} graph"
        assert fortified_graph.is_frozen


# ── FALSIFICATION-3: Epistemic Preservation Across Round-Trip ─────────────────

def test_falsification_3_epistemic_preservation_round_trip(
    ingress_gate: LanguageIngressGate,
    egress_gate: LanguageEgressGate,
    registry: LanguageDriverRegistry,
    fortifier: ConservativeSemanticFortifier,
):
    """
    FALSIFICATION-3: Epistemic Preservation Across Boundary Round-Trip.
    
    Hypothesis: The Language Adapter preserves epistemic states (UNKNOWN, AMBIGUOUS, INFERRED).
    Falsification Condition:
    1. If Japanese zero-anaphora (omitted subject) is auto-bound to a concrete entity (e.g. ent:lucia, ent:user),
       Falsification-3 triggers.
    2. If an ambiguous lexical referent (e.g. 'bank') is arbitrarily resolved to one reading,
       Falsification-3 triggers.
    3. If realizing an UNKNOWN entity produces a fabricated concrete character name,
       Falsification-3 triggers.
    """
    # 1. Zero-anaphora preservation
    ja_text = "問題を解決した"  # Subject dropped
    res_ja = ingress_gate.admit_and_parse(ja_text, "ja", registry)
    graph_ja = res_ja.graph

    # Find the agent node (:ARG0)
    solve_node = next(n for n in graph_ja.nodes.values() if n.concept_symbol == "c:SOLVE_PROBLEM")
    arg0_edge = next(e for e in graph_ja.edges if e.source_id == solve_node.id and e.relation_role == ":ARG0")
    agent_node = graph_ja.nodes[arg0_edge.target_id]

    assert agent_node.epistemic_state == EpistemicState.UNKNOWN, (
        "FALSIFICATION-3 TRIGGERED: Omitted subject was NOT marked as UNKNOWN!"
    )
    assert agent_node.id not in ("ent:user", "ent:lucia", "e:user", "e:lucia"), (
        "FALSIFICATION-3 TRIGGERED: Omitted subject was auto-bound to concrete entity!"
    )

    # Fortify
    fortified_ja, audit_ja = fortifier.fortify_session(graph_ja)
    assert audit_ja.is_valid

    # Realize to English
    realize_en = egress_gate.admit_and_realize(fortified_ja, "en", registry)
    assert "user" not in realize_en.surface_text.lower(), "FALSIFICATION-3 TRIGGERED: Fabricated 'user' for UNKNOWN agent"
    assert "lucia" not in realize_en.surface_text.lower(), "FALSIFICATION-3 TRIGGERED: Fabricated 'lucia' for UNKNOWN agent"

    # 2. Ambiguity preservation
    ambig_res = ingress_gate.admit_and_parse("User visits bank", "en", registry)
    bank_node = ambig_res.graph.nodes["ent:ambiguous_bank_01"]
    assert bank_node.epistemic_state == EpistemicState.AMBIGUOUS, (
        "FALSIFICATION-3 TRIGGERED: Ambiguity was collapsed to non-AMBIGUOUS state!"
    )
    alternatives = bank_node.attributes.get("alternative_hypotheses", [])
    assert len(alternatives) >= 2, (
        "FALSIFICATION-3 TRIGGERED: Alternative hypotheses pruned!"
    )


# ── FALSIFICATION-4: Cross-Lingual Semantic Invariance ────────────────────────

def test_falsification_4_cross_lingual_semantic_invariance(
    ingress_gate: LanguageIngressGate,
    registry: LanguageDriverRegistry,
):
    """
    FALSIFICATION-4: Cross-Lingual Semantic Invariance on Parallel Inputs.
    
    Hypothesis: Parallel semantic expressions in EN, VI, and JA map to congruent
    substrate topologies with identical predicate concepts, argument bindings, and epistemic states.
    Falsification Condition: If parallel expressions produce divergent core topologies
    (different predicates or misaligned role bindings) on canonical frames,
    Falsification-4 triggers.
    
    Architectural Limitation Note:
    On canonical parallel frames, semantic convergence is 100% (SQI = 1.0).
    On unconstrained open-domain natural language, coverage drops and unparsed segments
    are explicitly reported without fabricating fake semantic graphs.
    """
    # Canonical parallel triplet:
    triplet = {
        "en": "User solves the problem",
        "vi": "Anh người dùng giải quyết cái vấn đề",  # with kinship & classifier!
        "ja": "ユーザーが問題を解決した",
    }

    parsed_graphs = {}
    for lang, text in triplet.items():
        res = ingress_gate.admit_and_parse(text, lang, registry)
        assert res.coverage_score == 1.0
        parsed_graphs[lang] = res.graph

    # Compare core topologies across all three languages
    g_en = parsed_graphs["en"]
    g_vi = parsed_graphs["vi"]
    g_ja = parsed_graphs["ja"]

    # 1. Main Predicate Check
    for lang, g in parsed_graphs.items():
        event_nodes = [n for n in g.nodes.values() if n.concept_symbol == "c:SOLVE_PROBLEM"]
        assert len(event_nodes) == 1, f"Missing c:SOLVE_PROBLEM in {lang}"
        assert event_nodes[0].epistemic_state == EpistemicState.FACT

    # 2. Argument Role Binding Check
    for lang, g in parsed_graphs.items():
        solve_id = next(n.id for n in g.nodes.values() if n.concept_symbol == "c:SOLVE_PROBLEM")
        arg0_target = next(e.target_id for e in g.edges if e.source_id == solve_id and e.relation_role == ":ARG0")
        arg1_target = next(e.target_id for e in g.edges if e.source_id == solve_id and e.relation_role == ":ARG1")

        assert g.nodes[arg0_target].concept_symbol == "c:USER", f"{lang} :ARG0 concept mismatch"
        assert g.nodes[arg0_target].epistemic_state == EpistemicState.FACT, f"{lang} :ARG0 state mismatch"

        assert g.nodes[arg1_target].concept_symbol == "c:PROBLEM", f"{lang} :ARG1 concept mismatch"
        assert g.nodes[arg1_target].epistemic_state == EpistemicState.FACT, f"{lang} :ARG1 state mismatch"

    # 3. Limitation Demonstration on Out-of-Domain text
    # A driver must report coverage < 1.0 and unparsed segments honestly, not fake understanding
    ood_text = "The quantum teleportation protocol achieved higher fidelity"
    cov_en = registry.get_driver("en").validate_coverage(ood_text, "en")
    assert cov_en.coverage_ratio < 0.50
    assert len(cov_en.unrecognized_segments) > 0
