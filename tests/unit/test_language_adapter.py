"""
tests/unit/test_language_adapter.py

Unit tests for Phase 23-F: Language Adapter Boundary & Semantic Substrate Contract.
Tests the isolation, registry, ingress/egress gating, and driver contracts across EN, VI, and JA.
"""

import pytest

from src.core.knowledge.fortification import (
    ConservativeSemanticFortifier,
    EpistemicState,
    SemanticEdge,
    SemanticGraph,
    SemanticNode,
)
from src.core.language.adapter import (
    SUPPORTED_LANGUAGES,
    EgressGateBlockedError,
    EnglishLanguageDriver,
    EpistemicLeakageError,
    GateVerdict,
    IngressGateBlockedError,
    JapaneseLanguageDriver,
    LanguageDriverRegistry,
    LanguageEgressGate,
    LanguageIngressGate,
    SubstrateViolationError,
    UnsupportedLanguageError,
    VietnameseLanguageDriver,
)


@pytest.fixture
def default_registry() -> LanguageDriverRegistry:
    return LanguageDriverRegistry.create_default_registry()


@pytest.fixture
def ingress_gate() -> LanguageIngressGate:
    return LanguageIngressGate()


@pytest.fixture
def egress_gate() -> LanguageEgressGate:
    return LanguageEgressGate()


# ── Registry Tests ─────────────────────────────────────────────────────────────

def test_registry_registration_and_lookup(default_registry: LanguageDriverRegistry):
    """Verifies that default registry registers and retrieves EN, VI, JA drivers correctly."""
    assert set(default_registry.registered_languages()) == {"en", "ja", "vi"}
    
    en_driver = default_registry.get_driver("en")
    assert isinstance(en_driver, EnglishLanguageDriver)
    
    vi_driver = default_registry.get_driver("vi")
    assert isinstance(vi_driver, VietnameseLanguageDriver)
    
    ja_driver = default_registry.get_driver("ja")
    assert isinstance(ja_driver, JapaneseLanguageDriver)


def test_registry_unsupported_language_rejection(default_registry: LanguageDriverRegistry):
    """Verifies that requesting unsupported language codes raises UnsupportedLanguageError."""
    unsupported = ["fr", "de", "zh", "es", "ru", "ko", "latin", "unknown"]
    for lang in unsupported:
        assert not default_registry.is_language_supported(lang)
        with pytest.raises(UnsupportedLanguageError):
            default_registry.get_driver(lang)


# ── Ingress Gate Tests ─────────────────────────────────────────────────────────

def test_ingress_gate_blocks_unsupported_languages(
    ingress_gate: LanguageIngressGate,
    default_registry: LanguageDriverRegistry,
):
    """Verifies that LanguageIngressGate strictly intercepts and blocks unadmitted languages."""
    unsupported_probes = [
        ("fr", "Bonjour le monde"),
        ("de", "Guten Tag"),
        ("zh", "你好世界"),
        ("es", "Hola mundo"),
        ("ru", "Привет мир"),
        ("it", "Ciao mondo"),
    ]
    for lang, text in unsupported_probes:
        report = ingress_gate.evaluate_language(lang)
        assert report.verdict == GateVerdict.BLOCKED
        assert "not admitted" in report.reason

        with pytest.raises(IngressGateBlockedError) as exc_info:
            ingress_gate.admit_and_parse(text, lang, default_registry)
        assert "not admitted" in str(exc_info.value)


def test_ingress_gate_admits_supported_languages(
    ingress_gate: LanguageIngressGate,
    default_registry: LanguageDriverRegistry,
):
    """Verifies that LanguageIngressGate admits EN, VI, JA inputs."""
    for lang in ["en", "vi", "ja"]:
        report = ingress_gate.evaluate_language(lang)
        assert report.verdict == GateVerdict.ADMITTED


def test_ingress_gate_verifies_substrate_purity(
    ingress_gate: LanguageIngressGate,
):
    """Verifies that IngressGate rejects graphs contaminated with raw tokens or prefixes."""
    # Graph with illegal token prefix in node ID
    bad_graph = SemanticGraph(session_id="session:test")
    bad_graph.add_node(
        SemanticNode(
            id="token:word_01",
            epistemic_state=EpistemicState.FACT,
            concept_symbol="c:TEST",
        )
    )
    with pytest.raises(SubstrateViolationError):
        ingress_gate._verify_substrate_purity(bad_graph, "en")


def test_ingress_gate_verifies_unknown_binding_rejection(
    ingress_gate: LanguageIngressGate,
):
    """Verifies that IngressGate catches illegal binding of UNKNOWN to concrete entities."""
    bad_graph = SemanticGraph(session_id="session:test")
    bad_graph.add_node(
        SemanticNode(
            id="ent:unknown_01",
            epistemic_state=EpistemicState.UNKNOWN,
            concept_symbol="e:lucia",  # ILLEGAL: UNKNOWN bound to concrete Lucia!
        )
    )
    with pytest.raises(EpistemicLeakageError):
        ingress_gate._verify_substrate_purity(bad_graph, "en")


# ── Egress Gate Tests ─────────────────────────────────────────────────────────

def test_egress_gate_blocks_unsupported_target(
    egress_gate: LanguageEgressGate,
    default_registry: LanguageDriverRegistry,
):
    """Verifies that LanguageEgressGate intercepts requests to realize into unadmitted languages."""
    graph = SemanticGraph(session_id="session:test")
    for lang in ["fr", "de", "zh", "es", "ko"]:
        report = egress_gate.evaluate_target_language(lang)
        assert report.verdict == GateVerdict.BLOCKED
        with pytest.raises(EgressGateBlockedError):
            egress_gate.admit_and_realize(graph, lang, default_registry)


def test_egress_gate_admits_supported_target(
    egress_gate: LanguageEgressGate,
):
    """Verifies that LanguageEgressGate admits EN, VI, JA targets."""
    for lang in ["en", "vi", "ja"]:
        report = egress_gate.evaluate_target_language(lang)
        assert report.verdict == GateVerdict.ADMITTED


# ── Vietnamese Driver Kinship & Classifier Separation ──────────────────────────

def test_vietnamese_kinship_and_classifier_separation(
    ingress_gate: LanguageIngressGate,
    default_registry: LanguageDriverRegistry,
):
    """Verifies that Vietnamese kinship honorifics and classifiers do not pollute node IDs."""
    text = "Anh người dùng giải quyết cái vấn đề"
    result = ingress_gate.admit_and_parse(text, "vi", default_registry)
    graph = result.graph

    # Verify core entities are clean
    assert "ent:user" in graph.nodes
    assert "ent:problem" in graph.nodes
    assert "node:event_solve_01" in graph.nodes

    # Core concept symbols must not contain kinship or classifier words
    assert graph.nodes["ent:user"].concept_symbol == "c:USER"
    assert graph.nodes["ent:problem"].concept_symbol == "c:PROBLEM"
    assert graph.nodes["node:event_solve_01"].concept_symbol == "c:SOLVE_PROBLEM"

    # Social honorifics must be preserved as attributes, not node IDs
    user_attrs = graph.nodes["ent:user"].attributes
    assert user_attrs.get("social_honorific") == "anh"


# ── Japanese Driver Zero-Anaphora Preservation ─────────────────────────────────

def test_japanese_zero_anaphora_preservation(
    ingress_gate: LanguageIngressGate,
    default_registry: LanguageDriverRegistry,
):
    """Verifies that Japanese omitted subject strictly produces EpistemicState.UNKNOWN."""
    # "問題を解決した" (Solved the problem - no subject)
    text = "問題を解決した"
    result = ingress_gate.admit_and_parse(text, "ja", default_registry)
    graph = result.graph

    assert "node:event_solve_01" in graph.nodes
    assert "ent:problem" in graph.nodes
    assert "ent:unknown_agent_01" in graph.nodes

    unknown_node = graph.nodes["ent:unknown_agent_01"]
    assert unknown_node.epistemic_state == EpistemicState.UNKNOWN
    assert unknown_node.concept_symbol == "c:UNKNOWN_REFERENT"

    # Invariant: Must NOT be bound to user or lucia
    assert unknown_node.id != "ent:user"
    assert unknown_node.id != "ent:lucia"


# ── Ambiguity Preservation ────────────────────────────────────────────────────

def test_ambiguity_preservation(
    ingress_gate: LanguageIngressGate,
    default_registry: LanguageDriverRegistry,
):
    """Verifies that ambiguous inputs retain EpistemicState.AMBIGUOUS with alternative hypotheses."""
    text = "User visits bank"
    result = ingress_gate.admit_and_parse(text, "en", default_registry)
    graph = result.graph

    bank_node = graph.nodes["ent:ambiguous_bank_01"]
    assert bank_node.epistemic_state == EpistemicState.AMBIGUOUS
    assert "c:FINANCIAL_BANK" in bank_node.attributes["alternative_hypotheses"]
    assert "c:RIVER_BANK" in bank_node.attributes["alternative_hypotheses"]


# ── End-to-End Parse, Fortify, and Realize Round-Trip ──────────────────────────

def test_round_trip_parse_fortify_realize(
    ingress_gate: LanguageIngressGate,
    egress_gate: LanguageEgressGate,
    default_registry: LanguageDriverRegistry,
):
    """Verifies end-to-end flow: Ingress -> Parse -> Fortify (P23-E) -> Realize (Egress)."""
    fortifier = ConservativeSemanticFortifier()

    # 1. Parse from English
    text_in = "User solves the problem"
    parse_res = ingress_gate.admit_and_parse(text_in, "en", default_registry)
    graph = parse_res.graph

    # 2. Fortify via P23-E (Audit, Normalize, Freeze, Checksum)
    fortified_graph, audit_report = fortifier.fortify_session(graph)
    assert audit_report.is_valid
    assert fortified_graph.is_frozen
    assert fortified_graph.structural_checksum is not None

    # 3. Realize to Vietnamese
    realize_vi = egress_gate.admit_and_realize(fortified_graph, "vi", default_registry)
    assert "Người dùng giải quyết vấn đề" in realize_vi.surface_text
    assert realize_vi.fidelity_score == 1.0

    # 4. Realize to Japanese
    realize_ja = egress_gate.admit_and_realize(fortified_graph, "ja", default_registry)
    assert "ユーザーが問題を解決した" in realize_ja.surface_text
    assert realize_ja.fidelity_score == 1.0


def test_round_trip_unknown_realization(
    ingress_gate: LanguageIngressGate,
    egress_gate: LanguageEgressGate,
    default_registry: LanguageDriverRegistry,
):
    """Verifies that UNKNOWN agent is realized passively without inventing a name."""
    fortifier = ConservativeSemanticFortifier()

    # Parse Japanese zero-anaphora
    parse_ja = ingress_gate.admit_and_parse("問題を解決した", "ja", default_registry)
    fortified_graph, audit_report = fortifier.fortify_session(parse_ja.graph)
    assert audit_report.is_valid

    # Realize in English: must be passive/unknown, not concrete user/lucia
    realize_en = egress_gate.admit_and_realize(fortified_graph, "en", default_registry)
    assert "The problem was solved" in realize_en.surface_text
    assert "lucia" not in realize_en.surface_text.lower()
    assert "user" not in realize_en.surface_text.lower()
