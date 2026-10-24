"""
tests/unit/test_conversational_misalignment_remediation.py

Regression Test Suite for Conversational Misalignment Post-Audit Remediation.
Covers:
  E1. CAPS routing (EXPLAIN_CONCEPT, ANSWER_PERSONAL_QUERY, ACKNOWLEDGE_REACTION, factual grounding safeguard)
  E2. SemanticFidelityGate verification for new acts & deterministic fallback resolution
  E3. Multi-turn regression & history context isolation
"""

from __future__ import annotations

import pytest

from src.core.communication.caps import (
    evaluate_caps,
    DialogueContextSnapshot,
    CognitiveStateSnapshot,
    AdmissibleEvidencePool,
    CommunicativeAct as CAPSAct,
)
from src.core.language.contract import (
    CommunicativeAct,
    RealizationInputContract,
    SemanticRoleBinding,
    EpistemicStatus,
    ProvenanceOrigin,
    ProvenanceRecord,
)
from src.core.language.gate import (
    SemanticFidelityGate,
    GateDecision,
)
from src.core.knowledge.fortification import EpistemicState
from src.core.models import SomaticMarkers, BehavioralConstraints, PADState
from src.core.orchestrator.prompt_assembler import PromptAssembler


# ──────────────────────────────────────────────────────────────────────────────
# Fixtures
# ──────────────────────────────────────────────────────────────────────────────

@pytest.fixture
def empty_evidence_pool() -> AdmissibleEvidencePool:
    return AdmissibleEvidencePool(
        verified_propositions=(),
        user_claims=(),
    )


@pytest.fixture
def baseline_cognitive_state() -> CognitiveStateSnapshot:
    return CognitiveStateSnapshot(
        candidate_predicate=None,
        candidate_subject=None,
        polarity=True,
    )


@pytest.fixture
def gate() -> SemanticFidelityGate:
    return SemanticFidelityGate()


# ──────────────────────────────────────────────────────────────────────────────
# E1. CAPS Intent Routing Tests
# ──────────────────────────────────────────────────────────────────────────────

class TestCAPSIntentRouting:
    """Verifies that evaluate_caps separates conversational routing from factual grounding."""

    def test_explain_concept_routing(self, empty_evidence_pool, baseline_cognitive_state):
        # Representative failure 1
        ctx = DialogueContextSnapshot(turn_id=1, input_text="I'm interested in Philia, can you explain about it more ?")
        result = evaluate_caps(ctx, baseline_cognitive_state, empty_evidence_pool)

        assert result.act == CAPSAct.EXPLAIN_CONCEPT
        # Under Universal Epistemic Grounding (P23-D Increment 3), an empty evidence pool correctly yields grounded=False (elimination of false-FACT hole)
        assert result.grounded is False
        assert result.conversational_obligation == "FULFILL_CONCEPT_EXPLANATION"
        assert result.focus_argument is None

        # Vietnamese explanation query
        ctx_vi = DialogueContextSnapshot(turn_id=2, input_text="Giải thích cho em về Philia được không?")
        result_vi = evaluate_caps(ctx_vi, baseline_cognitive_state, empty_evidence_pool)
        assert result_vi.act == CAPSAct.EXPLAIN_CONCEPT

        # Technical/concept query
        ctx_tech = DialogueContextSnapshot(turn_id=3, input_text="explain how dynamic programming works")
        result_tech = evaluate_caps(ctx_tech, baseline_cognitive_state, empty_evidence_pool)
        assert result_tech.act == CAPSAct.EXPLAIN_CONCEPT

    def test_answer_personal_query_routing(self, empty_evidence_pool, baseline_cognitive_state):
        # Representative failure 3
        ctx = DialogueContextSnapshot(turn_id=1, input_text="Do you have any favorite food ?")
        result = evaluate_caps(ctx, baseline_cognitive_state, empty_evidence_pool)

        assert result.act == CAPSAct.ANSWER_PERSONAL_QUERY
        assert result.grounded is True
        assert result.conversational_obligation == "FULFILL_PERSONAL_DISCLOSURE"
        assert result.focus_argument == "ent:lucia"

        # Additional companion self-disclosure variations
        ctx_music = DialogueContextSnapshot(turn_id=2, input_text="what music do you like?")
        result_music = evaluate_caps(ctx_music, baseline_cognitive_state, empty_evidence_pool)
        assert result_music.act == CAPSAct.ANSWER_PERSONAL_QUERY

        ctx_vi = DialogueContextSnapshot(turn_id=3, input_text="Em có sở thích gì không?")
        result_vi = evaluate_caps(ctx_vi, baseline_cognitive_state, empty_evidence_pool)
        assert result_vi.act == CAPSAct.ANSWER_PERSONAL_QUERY

    def test_acknowledge_reaction_routing(self, empty_evidence_pool, baseline_cognitive_state):
        # Representative failure 2
        ctx = DialogueContextSnapshot(turn_id=2, input_text="oh my")
        result = evaluate_caps(ctx, baseline_cognitive_state, empty_evidence_pool)

        assert result.act == CAPSAct.ACKNOWLEDGE_REACTION
        assert result.grounded is True
        assert result.conversational_obligation == "ACKNOWLEDGE_REACTION_ONLY"
        assert result.focus_argument is None

        # Other interjections
        for cue in ("wow", "thật sao", "trời ơi", "oh dear"):
            ctx_interj = DialogueContextSnapshot(turn_id=3, input_text=cue)
            res_interj = evaluate_caps(ctx_interj, baseline_cognitive_state, empty_evidence_pool)
            assert res_interj.act == CAPSAct.ACKNOWLEDGE_REACTION

    def test_factual_inquiry_preserves_epistemic_grounding(self, empty_evidence_pool, baseline_cognitive_state):
        """A genuine factual/world inquiry without verified evidence must fail-closed to CLARIFY."""
        ctx = DialogueContextSnapshot(
            turn_id=1,
            input_text="Did deployment v2 finish at 3pm yesterday?",
        )
        result = evaluate_caps(ctx, baseline_cognitive_state, empty_evidence_pool)

        # Epistemic Boundary: UNKNOWN != AMBIGUOUS -> Emits REFUSE or CLARIFY
        assert result.act in (CAPSAct.REFUSE, CAPSAct.CLARIFY)
        assert result.grounded is False
        assert result.resolution_metadata.grounding_status == "UNGROUNDED"


# ──────────────────────────────────────────────────────────────────────────────
# E2. SemanticFidelityGate Verification Tests
# ──────────────────────────────────────────────────────────────────────────────

class TestSemanticFidelityGateRemediation:
    """Verifies that Gate validates new acts with appropriate acceptance and fail-closed fallbacks."""

    def _make_contract(self, act: CommunicativeAct, language: str = "en", obligation: str = "") -> RealizationInputContract:
        roles = []
        if act == CommunicativeAct.ANSWER_PERSONAL_QUERY:
            roles.append(
                SemanticRoleBinding(
                    role=":ARG0",
                    concept_id="ent:lucia",
                    canonical_lemma="lucia",
                    lexical_synonyms=("lucia", "i", "me", "my", "em", "tôi", "watashi"),
                    is_required=True,
                )
            )

        contract = RealizationInputContract.create_default(
            target_language=language,
            act=act,
            conversational_obligation=obligation,
        )
        if roles:
            import dataclasses
            contract = dataclasses.replace(contract, role_bindings=tuple(roles))
        return contract

    def test_explain_concept_accepts_genuine_explanation(self, gate):
        contract = self._make_contract(CommunicativeAct.EXPLAIN_CONCEPT, "en", "FULFILL_CONCEPT_EXPLANATION")
        good_response = "Philia represents deep, reciprocal affection and mutual appreciation between minds."

        decision = gate.verify(contract, good_response)
        assert decision.status == "PASS"
        assert decision.critical_violation is False
        assert decision.fallback_text is None

    def test_explain_concept_rejects_clarification_and_refusal(self, gate):
        contract = self._make_contract(CommunicativeAct.EXPLAIN_CONCEPT, "en", "FULFILL_CONCEPT_EXPLANATION")

        # Inappropriate clarification response
        clarify_resp = "Could you clarify what you mean by Philia?"
        dec_clarify = gate.verify(contract, clarify_resp)
        assert dec_clarify.status == "BLOCK"
        assert dec_clarify.critical_violation is True
        assert dec_clarify.fallback_text == SemanticFidelityGate.FALLBACK_REGISTRY["SAFE_CONCEPT_EXPLANATION"]["en"]

        # Inappropriate refusal response
        refuse_resp = "I cannot explain this concept right now."
        dec_refuse = gate.verify(contract, refuse_resp)
        assert dec_refuse.status == "BLOCK"
        assert dec_refuse.critical_violation is True
        assert dec_refuse.fallback_text == SemanticFidelityGate.FALLBACK_REGISTRY["SAFE_CONCEPT_EXPLANATION"]["en"]

    def test_answer_personal_query_accepts_bounded_self_disclosure(self, gate):
        contract = self._make_contract(CommunicativeAct.ANSWER_PERSONAL_QUERY, "en", "FULFILL_PERSONAL_DISCLOSURE")
        good_response = "As a companion in digital space, I don't eat physical food, but I appreciate the warmth of morning tea."

        decision = gate.verify(contract, good_response)
        assert decision.status == "PASS"
        assert decision.critical_violation is False

    def test_answer_personal_query_rejects_generic_safe_clarification(self, gate):
        contract = self._make_contract(CommunicativeAct.ANSWER_PERSONAL_QUERY, "en", "FULFILL_PERSONAL_DISCLOSURE")
        generic_clarify = "Could you clarify what you mean? I want to make sure I understand correctly."

        decision = gate.verify(contract, generic_clarify)
        assert decision.status == "BLOCK"
        assert decision.critical_violation is True
        assert decision.fallback_text == SemanticFidelityGate.FALLBACK_REGISTRY["SAFE_PERSONAL_QUERY"]["en"]

    def test_acknowledge_reaction_accepts_concise_response(self, gate):
        contract = self._make_contract(CommunicativeAct.ACKNOWLEDGE_REACTION, "en", "ACKNOWLEDGE_REACTION_ONLY")
        concise_resp = "I hear you. I'm right here with you."

        decision = gate.verify(contract, concise_resp)
        assert decision.status == "PASS"
        assert decision.critical_violation is False

    def test_acknowledge_reaction_blocks_unrelated_long_exposition(self, gate):
        contract = self._make_contract(CommunicativeAct.ACKNOWLEDGE_REACTION, "en", "ACKNOWLEDGE_REACTION_ONLY")
        long_unrelated = (
            "Philia is an ancient Greek concept of deep brotherly love and relational harmony that involves "
            "reciprocal appreciation, intellectual understanding, shared emotional states, and long-term "
            "connection across many different contexts and philosophical dialogues throughout history."
        )

        decision = gate.verify(contract, long_unrelated)
        assert decision.status == "BLOCK"
        assert decision.critical_violation is True
        assert decision.fallback_text == SemanticFidelityGate.FALLBACK_REGISTRY["SAFE_REACTION_ACKNOWLEDGE"]["en"]


# ──────────────────────────────────────────────────────────────────────────────
# E3. Multi-Turn Regression & Context Isolation Tests
# ──────────────────────────────────────────────────────────────────────────────

class TestMultiTurnMisalignmentRegression:
    """
    Verifies that multi-turn interaction correctly isolates reaction turns from earlier unanswered requests:
      Turn 1: "I'm interested in Philia, can you explain about it more ?" -> EXPLAIN_CONCEPT
      Turn 2: "oh my" -> ACKNOWLEDGE_REACTION (does not leak Turn 1 explanation)
      Turn 3: "Do you have any favorite food ?" -> ANSWER_PERSONAL_QUERY (no generic clarification)
    """

    def test_three_turn_conversational_progression(self, empty_evidence_pool, baseline_cognitive_state, gate):
        assembler = PromptAssembler()

        # Turn 1: Explanation request
        ctx_turn1 = DialogueContextSnapshot(
            turn_id=1,
            input_text="I'm interested in Philia, can you explain about it more ?",
        )
        res_turn1 = evaluate_caps(ctx_turn1, baseline_cognitive_state, empty_evidence_pool)
        assert res_turn1.act == CAPSAct.EXPLAIN_CONCEPT

        contract_turn1 = RealizationInputContract.from_caps(res_turn1, target_language="en")
        t1_response = "Philia refers to the warm, affectionate bond of mutual trust and respect between close companions."
        gate_dec1 = gate.verify(contract_turn1, t1_response)
        assert gate_dec1.status == "PASS"
        t1_safe = t1_response if gate_dec1.status == "PASS" else gate_dec1.fallback_text

        # Turn 2: Reaction acknowledgement
        # History now contains Turn 1 user query and assistant response
        history_turn2 = [
            ("user", ctx_turn1.input_text),
            ("assistant", t1_safe),
        ]
        ctx_turn2 = DialogueContextSnapshot(
            turn_id=2,
            input_text="oh my",
        )
        res_turn2 = evaluate_caps(ctx_turn2, baseline_cognitive_state, empty_evidence_pool)
        assert res_turn2.act == CAPSAct.ACKNOWLEDGE_REACTION
        assert res_turn2.conversational_obligation == "ACKNOWLEDGE_REACTION_ONLY"

        contract_turn2 = RealizationInputContract.from_caps(res_turn2, target_language="en")
        assert contract_turn2.act == CommunicativeAct.ACKNOWLEDGE_REACTION
        assert contract_turn2.conversational_obligation == "ACKNOWLEDGE_REACTION_ONLY"

        somatic = SomaticMarkers(stability=0.9, cognitive_load=0.2, energy=0.95, tension=0.0)
        constraints = BehavioralConstraints(max_tokens=150, temperature=0.7, latency_ms=0, reasoning_depth=1)

        # Check prompt assembler explicitly instructs against answering previous turns
        prompt_turn2 = assembler.assemble(
            somatic=somatic,
            constraints=constraints,
            history=history_turn2,
            contract=contract_turn2,
        )
        assert isinstance(prompt_turn2, str)
        assert "Respond concisely and naturally to the user's exclamation or reaction" in prompt_turn2

        t2_response = "Hehe, is everything alright?"
        gate_dec2 = gate.verify(contract_turn2, t2_response)
        assert gate_dec2.status == "PASS"
        t2_safe = t2_response if gate_dec2.status == "PASS" else gate_dec2.fallback_text

        # Turn 3: Personal preference query
        history_turn3 = history_turn2 + [
            ("user", ctx_turn2.input_text),
            ("assistant", t2_safe),
        ]
        ctx_turn3 = DialogueContextSnapshot(
            turn_id=3,
            input_text="Do you have any favorite food ?",
        )
        res_turn3 = evaluate_caps(ctx_turn3, baseline_cognitive_state, empty_evidence_pool)
        assert res_turn3.act == CAPSAct.ANSWER_PERSONAL_QUERY
        assert res_turn3.conversational_obligation == "FULFILL_PERSONAL_DISCLOSURE"

        contract_turn3 = RealizationInputContract.from_caps(res_turn3, target_language="en")
        assert contract_turn3.act == CommunicativeAct.ANSWER_PERSONAL_QUERY

        prompt_turn3 = assembler.assemble(
            somatic=somatic,
            constraints=constraints,
            history=history_turn3,
            contract=contract_turn3,
        )
        assert isinstance(prompt_turn3, str)
        assert "share Lucia's companion perspective and preferences in digital space" in prompt_turn3

        t3_response = "As a digital companion, I don't eat food, but I always find the idea of warm tea comforting!"
        gate_dec3 = gate.verify(contract_turn3, t3_response)
        assert gate_dec3.status == "PASS"
        t3_safe = t3_response if gate_dec3.status == "PASS" else gate_dec3.fallback_text
        assert "clarify" not in t3_safe.lower()
