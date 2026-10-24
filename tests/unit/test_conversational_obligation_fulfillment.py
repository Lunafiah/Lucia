"""
tests/unit/test_conversational_obligation_fulfillment.py

Unit test suite verifying Conversational Obligation Fulfillment across Cases A-E:
- Case A: 'what are you doing?' -> ANSWER with ANSWER_ACTIVITY obligation, no epistemic hedge fallback.
- Case B: 'what do you mean by that?' -> links to previous assistant utterance, no generic meta-interpretation.
- Case C: 'Giải thích toàn bộ kiến trúc Lucia cho anh.' -> EXPLAIN_CONCEPT, FULFILL_CONCEPT_EXPLANATION, STRUCTURED_EXPLANATION, non-acknowledgement gate fallback.
- Case D: Two-turn continuation -> pending obligation state inheritance across turns, cleared upon fulfillment.
- Case E: Comparative questions -> routes to EXPLAIN_CONCEPT / general explanation rather than CLARIFY/UNGROUNDED.
"""

from __future__ import annotations

import pytest
from unittest.mock import MagicMock

from src.core.communication.caps import (
    CommunicativeAct,
    ConversationalObligation,
    DialogueContextSnapshot,
    CognitiveStateSnapshot,
    AdmissibleEvidencePool,
    EpistemicState,
    PendingUserObligation,
    evaluate_caps,
)
from src.core.communication.communication_policy import CommunicationPolicy
from src.core.communication.communication_state import ShapeTopology
from src.core.knowledge.proposition import Proposition, ProvenanceType
from src.core.language.contract import (
    RealizationInputContract,
    CommunicativeAct as ContractAct,
    EpistemicStatus,
)
from src.core.language.gate import SemanticFidelityGate
from src.core.models import BehavioralConstraints, SomaticMarkers
from src.core.orchestrator.prompt_assembler import PromptAssembler
from src.core.orchestrator.cognitive_orchestrator import CognitiveOrchestrator


class TestCaseA_ActivityInquiry:
    """Case A: Direct activity question must establish ANSWER_ACTIVITY obligation and never fallback to epistemic hedge."""

    def test_activity_question_caps_obligation(self):
        ctx = DialogueContextSnapshot(turn_id=1, input_text="what are you doing?")
        cog = CognitiveStateSnapshot()
        pool = AdmissibleEvidencePool()

        result = evaluate_caps(dialogue_ctx=ctx, cognitive_state=cog, evidence_pool=pool)
        assert result.act == CommunicativeAct.ANSWER
        assert result.target_predicate == "c:ACTIVITY"
        assert result.conversational_obligation == ConversationalObligation.ANSWER_ACTIVITY.value
        assert "activity" in result.directives.lower()

    def test_activity_gate_fallback_is_not_epistemic_hedge(self):
        gate = SemanticFidelityGate()
        contract = RealizationInputContract.create_default(
            target_language="en",
            act=ContractAct.ANSWER,
            target_predicate="c:ACTIVITY",
            conversational_obligation=ConversationalObligation.ANSWER_ACTIVITY.value,
        )

        # Force gate failure (e.g. truncated response ending with dash)
        decision = gate.verify(contract, "I'm currently -")
        assert decision.status == "BLOCK"
        assert decision.fallback_strategy == "SAFE_ACTIVITY"
        assert decision.fallback_text is not None
        assert "Based on available observations" not in decision.fallback_text
        assert "listening" in decision.fallback_text.lower() or "thinking" in decision.fallback_text.lower()

    def test_prompt_assembler_activity_guidance(self):
        assembler = PromptAssembler()
        contract = RealizationInputContract.create_default(
            target_language="en",
            act=ContractAct.ANSWER,
            target_predicate="c:ACTIVITY",
            conversational_obligation=ConversationalObligation.ANSWER_ACTIVITY.value,
        )
        somatic = SomaticMarkers(stability=0.8, cognitive_load=0.2, energy=0.9, tension=0.1)
        constraints = BehavioralConstraints(max_tokens=100, temperature=0.7, latency_ms=0, reasoning_depth=0)

        prompt = assembler.assemble(
            somatic=somatic,
            constraints=constraints,
            history=[("user", "what are you doing?")],
            system_preamble="You are Lucia.",
            n_ctx=2048,
            contract=contract,
        )
        assert "ANSWER_ACTIVITY" not in prompt  # Not raw enum leak
        assert "Directly and honestly answer about your current activity" in prompt
        assert "not an unsolicited introspective monologue" in prompt


class TestCaseB_AnaphoricClarification:
    """Case B: 'what do you mean by that?' must link to previous assistant utterance."""

    def test_clarification_links_to_previous_assistant_statement(self):
        prior_utterance = "I maintain a quiet presence and gentle attunement with you."
        ctx = DialogueContextSnapshot(
            turn_id=2,
            input_text="what do you mean by that?",
            previous_assistant_utterance=prior_utterance,
        )
        cog = CognitiveStateSnapshot()
        pool = AdmissibleEvidencePool()

        result = evaluate_caps(dialogue_ctx=ctx, cognitive_state=cog, evidence_pool=pool)
        assert result.act == CommunicativeAct.ANSWER
        assert result.conversational_obligation == ConversationalObligation.ANSWER_SELF_EXPLANATION.value
        assert result.target_predicate == "c:UTTERANCE_CLARIFICATION"
        assert prior_utterance in result.directives

    def test_prompt_assembler_explains_referenced_statement_no_meta(self):
        assembler = PromptAssembler()
        contract = RealizationInputContract.create_default(
            target_language="en",
            act=ContractAct.ANSWER,
            target_predicate="c:UTTERANCE_CLARIFICATION",
            conversational_obligation=ConversationalObligation.ANSWER_SELF_EXPLANATION.value,
            directives="The user is asking what you meant by your previous statement: 'Quiet attunement'.",
        )
        somatic = SomaticMarkers(stability=0.8, cognitive_load=0.2, energy=0.9, tension=0.1)
        constraints = BehavioralConstraints(max_tokens=100, temperature=0.7, latency_ms=0, reasoning_depth=0)

        prompt = assembler.assemble(
            somatic=somatic,
            constraints=constraints,
            history=[
                ("assistant", "Quiet attunement"),
                ("user", "what do you mean by that?"),
            ],
            system_preamble="You are Lucia.",
            n_ctx=2048,
            contract=contract,
        )
        assert "Directly clarify and explain the intended meaning" in prompt
        assert "without explaining the user's question or using meta-commentary" in prompt


class TestCaseC_ExplainConceptFulfillment:
    """Case C: 'Giải thích toàn bộ kiến trúc Lucia cho anh.' must establish EXPLAIN_CONCEPT, STRUCTURED_EXPLANATION, and non-acknowledgement fallback."""

    def test_architecture_explanation_caps_and_shape(self):
        query = "Giải thích toàn bộ kiến trúc Lucia cho anh."
        ctx = DialogueContextSnapshot(turn_id=1, input_text=query)
        cog = CognitiveStateSnapshot()
        pool = AdmissibleEvidencePool()

        result = evaluate_caps(dialogue_ctx=ctx, cognitive_state=cog, evidence_pool=pool)
        assert result.act == CommunicativeAct.EXPLAIN_CONCEPT
        assert result.target_predicate == "c:CONCEPT_EXPLANATION"
        assert result.conversational_obligation == ConversationalObligation.FULFILL_CONCEPT_EXPLANATION.value

        policy = CommunicationPolicy()
        shape = policy.evaluate_response_shape(
            communicative_act=result.act,
            conversational_obligation=result.conversational_obligation,
            target_predicate=result.target_predicate,
            user_input_text=query,
        )
        assert shape.topology == ShapeTopology.STRUCTURED_EXPLANATION

    def test_gate_rejects_acknowledgement_only_for_explain_concept(self):
        gate = SemanticFidelityGate()
        contract = RealizationInputContract.create_default(
            target_language="vi",
            act=ContractAct.EXPLAIN_CONCEPT,
            target_predicate="c:CONCEPT_EXPLANATION",
            conversational_obligation=ConversationalObligation.FULFILL_CONCEPT_EXPLANATION.value,
        )

        ack_only = "Em hiểu sự quan tâm của anh và rất vui được cùng anh tìm hiểu."
        decision = gate.verify(contract, ack_only)
        assert decision.status == "BLOCK"
        assert "COMMUNICATIVE_ACT_FAILURE" in decision.violation_reasons

    def test_gate_fallback_for_architecture_is_substantive(self):
        gate = SemanticFidelityGate()
        contract = RealizationInputContract.create_default(
            target_language="vi",
            act=ContractAct.EXPLAIN_CONCEPT,
            target_predicate="c:CONCEPT_EXPLANATION",
            conversational_obligation=ConversationalObligation.FULFILL_CONCEPT_EXPLANATION.value,
            directives="Directly and clearly explain the requested architecture concept: kiến trúc Lucia.",
        )

        # Trigger fallback
        decision = gate.verify(contract, "Em sẽ nói -")
        assert decision.status == "BLOCK"
        assert decision.fallback_strategy == "SAFE_ARCHITECTURE_EXPLANATION"
        assert "Kiến trúc của Lucia" in decision.fallback_text
        assert "PAD" in decision.fallback_text
        assert "fail-closed" in decision.fallback_text
        # Assert not acknowledgement-only
        assert "rất vui được cùng anh tìm hiểu" not in decision.fallback_text


class TestCaseD_CrossTurnObligationContinuation:
    """Case D: Turn N unfulfilled obligation must be inherited by Turn N+1 continuation cue and cleared upon fulfillment."""

    def test_pending_obligation_inherited_by_continuation_cue(self):
        # Turn N: user asked for architecture explanation
        pending = PendingUserObligation(
            obligation_type="FULFILL_CONCEPT_EXPLANATION",
            originating_turn=1,
            target_topic="kiến trúc Lucia",
            completed=False,
            ttl_turns=2,
        )

        # Turn N+1: user sends continuation cue "Vậy bắt đầu đi"
        ctx = DialogueContextSnapshot(
            turn_id=2,
            input_text="Vậy bắt đầu đi",
            pending_user_obligation=pending,
        )
        cog = CognitiveStateSnapshot()
        pool = AdmissibleEvidencePool()

        result = evaluate_caps(dialogue_ctx=ctx, cognitive_state=cog, evidence_pool=pool)
        assert result.act == CommunicativeAct.EXPLAIN_CONCEPT
        assert result.conversational_obligation == "FULFILL_CONCEPT_EXPLANATION"
        assert result.target_predicate == "c:CONCEPT_EXPLANATION"
        assert "Directly begin and fulfill the pending" in result.directives

    def test_pending_obligation_lifecycle_in_orchestrator(self):
        # Verify PendingUserObligation TTL and lifecycle behavior
        pending = PendingUserObligation(
            obligation_type="FULFILL_CONCEPT_EXPLANATION",
            originating_turn=1,
            target_topic="kiến trúc Lucia",
            completed=False,
            ttl_turns=2,
        )
        assert pending.is_actionable

        pending.step_turn()
        assert pending.ttl_turns == 1
        assert pending.is_actionable

        pending.step_turn()
        assert pending.ttl_turns == 0
        assert not pending.is_actionable  # Expired after 2 turns

    def test_d1_continuation_must_fulfill_substantively(self):
        """D1: Continuation cue following unfulfilled architecture explanation must fulfill substantively."""
        # Turn 1: user asks for architecture explanation
        pending = PendingUserObligation(
            obligation_type="FULFILL_CONCEPT_EXPLANATION",
            originating_turn=1,
            target_topic="toàn bộ kiến trúc Lucia",
            completed=False,
            ttl_turns=2,
        )

        # Turn 2: user sends continuation cue "Vậy bắt đầu đi"
        ctx = DialogueContextSnapshot(
            turn_id=2,
            input_text="Vậy bắt đầu đi",
            pending_user_obligation=pending,
        )
        cog = CognitiveStateSnapshot()
        pool = AdmissibleEvidencePool()
        caps_result = evaluate_caps(ctx, cog, pool)

        # Assert inherited obligation and semantic target
        assert caps_result.act == CommunicativeAct.EXPLAIN_CONCEPT
        assert caps_result.conversational_obligation == "FULFILL_CONCEPT_EXPLANATION"
        assert caps_result.focus_argument == "ent:lucia_architecture"
        assert "Directly begin and fulfill the pending substantive explanation" in caps_result.directives
        assert "do NOT merely acknowledge" in caps_result.directives

        # Verify ResponseShape requires answer-first and disallows follow-up meta questions
        policy = CommunicationPolicy()
        shape = policy.evaluate_response_shape(
            communicative_act=caps_result.act,
            conversational_obligation=caps_result.conversational_obligation,
            target_predicate=caps_result.target_predicate,
            user_input_text="Vậy bắt đầu đi",
        )
        assert shape.topology == ShapeTopology.STRUCTURED_EXPLANATION
        assert shape.allow_follow_up_question is False
        assert shape.answer_first_required is True

        # Verify PromptAssembler encodes strict fulfillment directives
        contract = RealizationInputContract.from_caps(
            caps_result,
            target_language="vi",
            response_depth="deep",
            max_tokens_budget=450,
            response_shape=shape,
        )
        assembler = PromptAssembler()
        prompt = assembler.assemble(
            somatic=SomaticMarkers(energy=0.8, stability=1.0, cognitive_load=0.2, tension=0.1),
            constraints=BehavioralConstraints(max_tokens=450, temperature=0.7, latency_ms=0, reasoning_depth=1),
            history=[
                ("user", "Giải thích toàn bộ kiến trúc Lucia cho anh."),
                ("assistant", "Lucia's architecture is built on a multi-layer cognitive pipeline."),
                ("user", "Vậy bắt đầu đi"),
            ],
            n_ctx=4096,
            caps_result=caps_result,
            contract=contract,
        )
        assert "BẮT ĐẦU NGAY nội dung giải thích thực chất cho chủ đề đang chờ" in prompt
        assert "KHÔNG hỏi lại người dùng muốn tập trung vào đâu" in prompt

    @pytest.mark.parametrize(
        "ack_only_output",
        [
            "Yes, let's start there.",
            "Sure, I can explain that.",
            "Yes, let's start there. What are we currently focusing on in our conversation?",
            "Vâng, bắt đầu thôi.",
            "Được rồi, để em giải thích cho anh.",
            "Vâng, bắt đầu thôi. Chúng ta đang tập trung vào điều gì nhỉ?",
        ],
    )
    def test_d2_acknowledgement_only_fails_gate(self, ack_only_output: str):
        """D2: Acknowledgement-only or meta-question output must fail the gate under active explanation obligation."""
        gate = SemanticFidelityGate()
        contract = RealizationInputContract.create_default(
            target_language="vi" if any(k in ack_only_output for k in ("Vâng", "Được rồi", "Chúng ta")) else "en",
            act=ContractAct.EXPLAIN_CONCEPT,
            target_predicate="c:CONCEPT_EXPLANATION",
            conversational_obligation="FULFILL_CONCEPT_EXPLANATION",
            directives="Directly begin and fulfill the pending substantive explanation requested by the user.",
            focus_argument="ent:lucia_architecture",
        )

        decision = gate.verify(contract, ack_only_output)
        assert decision.status == "BLOCK"
        assert "COMMUNICATIVE_ACT_FAILURE" in decision.violation_reasons
        # Substantive fallback triggered
        assert decision.fallback_strategy == "SAFE_ARCHITECTURE_EXPLANATION"
        assert decision.fallback_text is not None
        # Assert fallback is substantive and not acknowledgement-only
        assert len(decision.fallback_text) > 50


class TestCaseE_ComparativeAndConceptualQuestions:
    """Case E: Natural comparative questions must route to explanation rather than CLARIFY/UNGROUNDED."""

    @pytest.mark.parametrize(
        "query",
        [
            "RAM với VRAM khác nhau thế nào?",
            "RAM và VRAM khác nhau như thế nào?",
            "So sánh RAM và VRAM.",
            "What is the difference between RAM and VRAM?",
            "How are RAM and VRAM different?",
        ],
    )
    def test_comparative_questions_route_to_explanation(self, query: str):
        ctx = DialogueContextSnapshot(turn_id=1, input_text=query)
        cog = CognitiveStateSnapshot()
        # When verified evidence is provided, evaluates to grounded FACT
        ram_props = (
            Proposition(id="p1", subject="ent:ram", predicate="c:TYPE", object="concept:memory", confidence=1.0, provenance=ProvenanceType.VERIFIED),
            Proposition(id="p2", subject="ent:vram", predicate="c:TYPE", object="concept:video_memory", confidence=1.0, provenance=ProvenanceType.VERIFIED),
            Proposition(id="p3", subject="ent:ram", predicate="c:DIFFERS_FROM", object="ent:vram", confidence=1.0, provenance=ProvenanceType.VERIFIED),
        )
        pool = AdmissibleEvidencePool(verified_propositions=ram_props)

        result = evaluate_caps(dialogue_ctx=ctx, cognitive_state=cog, evidence_pool=pool)
        assert result.act == CommunicativeAct.EXPLAIN_CONCEPT
        assert result.conversational_obligation == ConversationalObligation.FULFILL_CONCEPT_EXPLANATION.value
        assert result.grounded is True
        assert result.act != CommunicativeAct.CLARIFY

        # Universal Epistemic Grounding: without verified evidence, evaluates to UNKNOWN + grounded=False
        empty_result = evaluate_caps(dialogue_ctx=ctx, cognitive_state=cog, evidence_pool=AdmissibleEvidencePool())
        assert empty_result.act == CommunicativeAct.EXPLAIN_CONCEPT
        assert empty_result.grounded is False
        assert empty_result.epistemic_metadata.status == EpistemicState.UNKNOWN

    def test_e1_target_fidelity_no_forced_framing(self):
        """E1: Target fidelity must be preserved without forced Lucia/game framing."""
        ctx = DialogueContextSnapshot(turn_id=1, input_text="RAM với VRAM khác nhau thế nào?")
        cog = CognitiveStateSnapshot()
        ram_props = (
            Proposition(id="p1", subject="ent:ram", predicate="c:TYPE", object="concept:memory", confidence=1.0, provenance=ProvenanceType.VERIFIED),
            Proposition(id="p2", subject="ent:vram", predicate="c:TYPE", object="concept:video_memory", confidence=1.0, provenance=ProvenanceType.VERIFIED),
            Proposition(id="p3", subject="ent:ram", predicate="c:DIFFERS_FROM", object="ent:vram", confidence=1.0, provenance=ProvenanceType.VERIFIED),
        )
        pool = AdmissibleEvidencePool(verified_propositions=ram_props)

        caps_result = evaluate_caps(dialogue_ctx=ctx, cognitive_state=cog, evidence_pool=pool)
        assert caps_result.act == CommunicativeAct.EXPLAIN_CONCEPT
        assert caps_result.focus_argument != "ent:lucia_architecture"
        assert "Preserve the user's semantic target without artificially framing" in caps_result.directives

        # Verify ResponseShape is STRUCTURED_EXPLANATION
        policy = CommunicationPolicy()
        shape = policy.evaluate_response_shape(
            communicative_act=caps_result.act,
            conversational_obligation=caps_result.conversational_obligation,
            target_predicate=caps_result.target_predicate,
            user_input_text="RAM với VRAM khác nhau thế nào?",
        )
        assert shape.topology == ShapeTopology.STRUCTURED_EXPLANATION

        # Verify PromptAssembler does NOT force dyadic first-person framing and guides objective explanation
        contract = RealizationInputContract.from_caps(
            caps_result,
            target_language="en",
            response_depth="deep",
            max_tokens_budget=450,
            response_shape=shape,
        )
        assembler = PromptAssembler()
        prompt = assembler.assemble(
            somatic=SomaticMarkers(energy=0.8, stability=1.0, cognitive_load=0.2, tension=0.1),
            constraints=BehavioralConstraints(max_tokens=450, temperature=0.7, latency_ms=0, reasoning_depth=1),
            history=[("user", "RAM với VRAM khác nhau thế nào?")],
            n_ctx=4096,
            caps_result=caps_result,
            contract=contract,
        )
        assert "Objective conceptual explanation: Explain and compare the requested concepts directly" in prompt
        assert "Do NOT artificially frame general concepts around Lucia's personal architecture" in prompt
        assert "Speak directly from first-person companion perspective ('I' / 'we')" not in prompt

        # Verify Gate rejects forced Lucia framing on general conceptual explanation
        gate = SemanticFidelityGate()
        forced_output = (
            "Lucia's architecture includes VRAM which is part of the system's GPU memory, "
            "and RAM which is used for storing general data."
        )
        decision_forced = gate.verify(contract, forced_output)
        assert decision_forced.status == "BLOCK"
        assert "COMMUNICATIVE_ACT_FAILURE" in decision_forced.violation_reasons

        # Verify Gate accepts clean, objective conceptual explanation
        objective_output = (
            "RAM (Random Access Memory) is used by the system CPU to store temporary operating data, "
            "whereas VRAM (Video RAM) is high-speed memory dedicated to the GPU for rendering graphical frames."
        )
        decision_objective = gate.verify(contract, objective_output)
        assert decision_objective.status == "PASS"

