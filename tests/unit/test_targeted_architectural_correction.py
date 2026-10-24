"""
tests/unit/test_targeted_architectural_correction.py

Authoritative Unit Tests for Targeted Architectural Correction:
Contract -> Prompt -> Realization Fidelity + Epistemic Boundary (Parts H1-H7).
"""

from __future__ import annotations

import pytest

from src.core.cognition.self_model import ReflectiveSelfModel, SelfObservationSnapshot
from src.core.communication.caps import (
    AdmissibleEvidencePool,
    CAPSResult,
    CognitiveStateSnapshot,
    CommunicativeAct,
    ConversationalObligation,
    DialogueContextSnapshot,
    DyadicDiscourseState,
    EpistemicMetadata,
    EpistemicState,
    PendingUserObligation,
    PragmaticStance,
    evaluate_caps,
)
from src.core.knowledge.proposition import Proposition, ProvenanceType
from src.core.language.contract import (
    EpistemicStatus,
    NaturalLanguageTargetEvidence,
    RealizationInputContract,
    SemanticRoleBinding,
)
from src.core.language.detection import detect_active_language
from src.core.language.gate import SemanticFidelityGate
from src.core.models import BehavioralConstraints, SomaticMarkers
from src.core.orchestrator.discourse_cache import DiscourseReferent, ResolutionStatus
from src.core.orchestrator.prompt_assembler import PromptAssembler


# ==============================================================================
# H1: Canonical entity does not require literal snake_case
# ==============================================================================

def test_h1_canonical_entity_does_not_require_literal_snake_case():
    """
    Given focus_argument = ent:lucia_architecture, a natural response such as:
    "Lucia's architecture is organized around..."
    or "Kiến trúc của Lucia bao gồm..."
    must not fail merely because literal "lucia_architecture" is absent.
    """
    # 1. Direct SemanticRoleBinding check
    evidence = NaturalLanguageTargetEvidence(lemmas=("architecture", "lucia"))
    role_binding = SemanticRoleBinding(
        role=":ARG1",
        concept_id="ent:lucia_architecture",
        canonical_lemma="lucia_architecture",
        lexical_synonyms=("architecture", "lucia"),
        target_evidence=evidence,
    )

    en_text = "Lucia's architecture is organized around a continuous affective dynamical core."
    vi_text = "Kiến trúc của Lucia bao gồm các tầng nhận thức phối hợp chặt chẽ với nhau."

    assert role_binding.matches_text(en_text), "English natural text should match target evidence"

    # Vietnamese binding
    role_binding_vi = SemanticRoleBinding(
        role=":ARG1",
        concept_id="ent:lucia_architecture",
        canonical_lemma="lucia_architecture",
        lexical_synonyms=("kiến trúc", "lucia"),
        target_evidence=NaturalLanguageTargetEvidence(lemmas=("kiến trúc", "lucia")),
    )
    assert role_binding_vi.matches_text(vi_text), "Vietnamese natural text should match target evidence"

    # 2. Gate Verification check
    gate = SemanticFidelityGate()
    contract_en = RealizationInputContract.create_default(
        target_language="en",
        act=CommunicativeAct.EXPLAIN_CONCEPT,
        focus_argument="ent:lucia_architecture",
    )
    # Re-wrap contract with role binding
    contract_en = RealizationInputContract(
        contract_id=contract_en.contract_id,
        target_language="en",
        act=contract_en.act,
        polarity=True,
        epistemic_status=EpistemicStatus.FACT,
        role_bindings=(role_binding,),
        focus_argument="ent:lucia_architecture",
    )

    decision = gate.verify(contract_en, en_text)
    assert decision.status == "PASS"
    assert "ARGUMENT_ENTITY_LOSS" not in decision.violation_reasons


# ==============================================================================
# H2: Vietnamese language propagation
# ==============================================================================

def test_h2_vietnamese_language_propagation():
    """
    Input: "RAM với VRAM khác nhau thế nào?"
    Must result in Vietnamese language detection and Vietnamese realization contract.
    """
    input_text = "RAM với VRAM khác nhau thế nào?"
    detected = detect_active_language(input_text)
    assert detected == "vi", f"Expected 'vi', got '{detected}'"

    # Verify contract creation with detected active language
    contract = RealizationInputContract.create_default(
        target_language=detected,
        act=CommunicativeAct.EXPLAIN_CONCEPT,
    )
    assert contract.target_language == "vi"
    assert contract.speaker_honorific == "em"
    assert contract.addressee_honorific == "anh"
    assert "bạn" in contract.forbidden_additions

    # Verify PromptAssembler uses Vietnamese directives
    assembler = PromptAssembler()
    somatic = SomaticMarkers(stability=0.9, cognitive_load=0.2, energy=0.9, tension=0.0)
    constraints = BehavioralConstraints(latency_ms=0, reasoning_depth=0, max_tokens=200, temperature=0.7)
    prompt = assembler.assemble(
        somatic=somatic,
        constraints=constraints,
        history=[("user", input_text)],
        contract=contract,
    )
    assert isinstance(prompt, str)
    assert "Xưng hô bắt buộc" in prompt
    assert "tự xưng là 'em'" in prompt.lower()


# ==============================================================================
# H3: English language propagation
# ==============================================================================

def test_h3_english_language_propagation():
    """
    Input: "What is the difference between RAM and VRAM?"
    Must remain English realization contract.
    """
    input_text = "What is the difference between RAM and VRAM?"
    detected = detect_active_language(input_text)
    assert detected == "en", f"Expected 'en', got '{detected}'"

    contract = RealizationInputContract.create_default(
        target_language=detected,
        act=CommunicativeAct.EXPLAIN_CONCEPT,
    )
    assert contract.target_language == "en"
    assert contract.speaker_honorific is None
    assert "bạn" not in contract.forbidden_additions

    assembler = PromptAssembler()
    somatic = SomaticMarkers(stability=0.9, cognitive_load=0.2, energy=0.9, tension=0.0)
    constraints = BehavioralConstraints(latency_ms=0, reasoning_depth=0, max_tokens=200, temperature=0.7)
    prompt = assembler.assemble(
        somatic=somatic,
        constraints=constraints,
        history=[("user", input_text)],
        contract=contract,
    )
    assert isinstance(prompt, str)
    assert "Objective conceptual explanation" in prompt or "Conversational obligation" in prompt or "Directly" in prompt


# ==============================================================================
# H4: Activity answer fidelity
# ==============================================================================

def test_h4_activity_answer_fidelity():
    """
    Input: "what are you doing?"
    Must produce an answer whose primary content concerns current activity/presence.
    A relational paragraph alone must not satisfy the obligation, and directives
    must explicitly require operational answer first.
    """
    caps_res = evaluate_caps(
        dialogue_ctx=DialogueContextSnapshot(turn_id=1, input_text="what are you doing?"),
        cognitive_state=CognitiveStateSnapshot(),
        evidence_pool=AdmissibleEvidencePool(),
    )
    assert caps_res.act == CommunicativeAct.ANSWER
    assert caps_res.conversational_obligation == ConversationalObligation.ANSWER_ACTIVITY.value
    assert caps_res.target_predicate == "c:ACTIVITY"

    assembler = PromptAssembler()
    contract = RealizationInputContract.from_caps(caps_res, target_language="en")
    somatic = SomaticMarkers(stability=0.9, cognitive_load=0.1, energy=0.95, tension=0.0)
    constraints = BehavioralConstraints(latency_ms=0, reasoning_depth=0, max_tokens=150, temperature=0.7)
    prompt = assembler.assemble(
        somatic=somatic,
        constraints=constraints,
        history=[("user", "what are you doing?")],
        contract=contract,
    )
    assert isinstance(prompt, str)
    # Check that directive separates relational quality from activity answer
    assert "Directly answer the activity question first" in prompt
    assert "affectionate or emotional commentary must NEVER replace the direct activity answer" in prompt


# ==============================================================================
# H5: Somatic state isolation
# ==============================================================================

def test_h5_somatic_state_isolation():
    """
    Given an architecture question and nontrivial somatic state, verify that
    somatic variables are framed as background modulation only and cannot
    leak into semantic answer content.
    """
    assembler = PromptAssembler()
    contract = RealizationInputContract.create_default(
        target_language="vi",
        act=CommunicativeAct.EXPLAIN_CONCEPT,
        focus_argument="ent:lucia_architecture",
        conversational_obligation="FULFILL_CONCEPT_EXPLANATION",
    )
    somatic = SomaticMarkers(stability=0.888888, cognitive_load=0.333333, energy=0.777777, tension=0.111111)
    constraints = BehavioralConstraints(latency_ms=0, reasoning_depth=0, max_tokens=300, temperature=0.7)
    prompt = assembler.assemble(
        somatic=somatic,
        constraints=constraints,
        history=[("user", "Giải thích toàn bộ kiến trúc Lucia cho anh.")],
        contract=contract,
    )
    assert isinstance(prompt, str)
    # Verify somatic section boundary annotation
    assert "[SOMATIC STATE]" in prompt
    assert "# Operational context for expressive modulation only" in prompt
    # Verify directive isolation
    assert "Ranh giới thể trạng" in prompt
    assert "Tuyệt đối KHÔNG liệt kê hay giải thích các chỉ số này" in prompt


# ==============================================================================
# H6: Deep architecture obligation
# ==============================================================================

def test_h6_deep_architecture_obligation_natural_fulfillment():
    """
    Verify that a substantive natural architecture explanation in Vietnamese
    passes Gate without collapsing to static fallback.
    """
    gate = SemanticFidelityGate()
    contract = RealizationInputContract.create_default(
        target_language="vi",
        act=CommunicativeAct.EXPLAIN_CONCEPT,
        focus_argument="ent:lucia_architecture",
        conversational_obligation="FULFILL_CONCEPT_EXPLANATION",
    )

    # Substantive natural response in Vietnamese without snake_case "lucia_architecture"
    substantive_response = (
        "Kiến trúc của Lucia được tổ chức thành một chu trình nhận thức toàn vẹn gồm nhiều tầng chính: "
        "tầng động lực cảm xúc PAD liên tục qua Liquid Neural Network, hạ tầng ký ức phân tán SDM và hồi ức Ecphory, "
        "lõi lập luận tri thức chặt chẽ K3/JTMS, và cổng ngôn ngữ fail-closed bảo đảm tính xác thực của mọi phát ngôn."
    )

    decision = gate.verify(contract, substantive_response)
    assert decision.status == "PASS"
    assert decision.fallback_text is None
    assert "ARGUMENT_ENTITY_LOSS" not in decision.violation_reasons
    assert "COMMUNICATIVE_ACT_FAILURE" not in decision.violation_reasons


# ==============================================================================
# H7: Epistemic boundary: KNOWN, PARTIAL, UNKNOWN, AMBIGUOUS
# ==============================================================================

def test_h7_epistemic_boundary():
    """
    Verify the distinction between KNOWN, PARTIAL, UNKNOWN, and AMBIGUOUS.
    Crucially: UNKNOWN must route to REFUSE (not CLARIFY).
    AMBIGUOUS must route to CLARIFY.
    """
    # 1. KNOWN: Grounded verified proposition exists
    known_prop = Proposition(
        id="prop:1",
        subject="ent:ram",
        predicate="c:FUNCTION",
        object="temporary_storage",
        confidence=1.0,
        provenance=ProvenanceType.VERIFIED,
    )
    caps_known = evaluate_caps(
        dialogue_ctx=DialogueContextSnapshot(turn_id=1, input_text="What is RAM?"),
        cognitive_state=CognitiveStateSnapshot(candidate_predicate="c:FUNCTION", candidate_subject="ent:ram", candidate_object="temporary_storage"),
        evidence_pool=AdmissibleEvidencePool(verified_propositions=(known_prop,)),
    )
    assert caps_known.act in (CommunicativeAct.ANSWER, CommunicativeAct.ASSERT)
    assert caps_known.epistemic_metadata.status == EpistemicState.FACT

    # 2. PARTIAL: Epistemic status represented in contract
    contract_partial = RealizationInputContract.create_default(
        target_language="vi",
        act=CommunicativeAct.ANSWER,
    )
    contract_partial = RealizationInputContract(
        contract_id=contract_partial.contract_id,
        target_language="vi",
        act=CommunicativeAct.ANSWER,
        polarity=True,
        epistemic_status=EpistemicStatus.PARTIAL,
    )
    assert contract_partial.epistemic_status == EpistemicStatus.PARTIAL
    assembler = PromptAssembler()
    somatic = SomaticMarkers(stability=0.9, cognitive_load=0.1, energy=0.9, tension=0.0)
    constraints = BehavioralConstraints(latency_ms=0, reasoning_depth=0, max_tokens=150, temperature=0.7)
    prompt_partial = assembler.assemble(somatic=somatic, constraints=constraints, history=[], contract=contract_partial)
    assert "nhưng chưa đủ cơ sở để khẳng định" in prompt_partial

    # 3. UNKNOWN: Unambiguous question about completely ungrounded concept
    caps_unknown = evaluate_caps(
        dialogue_ctx=DialogueContextSnapshot(turn_id=1, input_text="Thủ đô của quốc gia Wakanda là gì?"),
        cognitive_state=CognitiveStateSnapshot(),
        evidence_pool=AdmissibleEvidencePool(),
    )
    # UNKNOWN must NOT route to CLARIFY!
    assert caps_unknown.act == CommunicativeAct.REFUSE, f"Expected REFUSE for UNKNOWN, got {caps_unknown.act}"
    assert caps_unknown.epistemic_metadata.status == EpistemicState.UNKNOWN

    # 4. AMBIGUOUS: Competing referents or ambiguous query
    caps_ambiguous = evaluate_caps(
        dialogue_ctx=DialogueContextSnapshot(
            turn_id=1,
            input_text="RAM là RAM máy tính hay RAM cho tiến trình?",
            resolution_status=ResolutionStatus.AMBIGUOUS,
        ),
        cognitive_state=CognitiveStateSnapshot(),
        evidence_pool=AdmissibleEvidencePool(),
    )
    assert caps_ambiguous.act == CommunicativeAct.CLARIFY
    assert caps_ambiguous.epistemic_metadata.status == EpistemicState.AMBIGUOUS
