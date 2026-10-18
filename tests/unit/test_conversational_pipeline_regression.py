"""
tests/unit/test_conversational_pipeline_regression.py

Regression test suite for Lucia Mascot / Conversational Pipeline Bug Fixes:
1. CAPS classification of conversational inquiries as CommunicativeAct.ANSWER with intent directives.
2. RealizationInputContract & PromptAssembler communicative directives propagation.
3. ChatML message turn parsing in LLMBackend without meta-prompt leakage.
4. SemanticFidelityGate validation preserving valid conversational responses and blocking invalid affect.
"""

from __future__ import annotations

import pytest
from unittest.mock import MagicMock

from src.core.communication.caps import (
    CommunicativeAct,
    DialogueContextSnapshot,
    CognitiveStateSnapshot,
    AdmissibleEvidencePool,
    evaluate_caps,
)
from src.core.language.contract import (
    RealizationInputContract,
    CommunicativeAct as ContractAct,
    EpistemicStatus,
)
from src.core.language.gate import SemanticFidelityGate
from src.core.language.llm_backend import LLMBackend
from src.core.models import BehavioralConstraints, SomaticMarkers
from src.core.orchestrator.prompt_assembler import PromptAssembler


class TestCAPSConversationalClassification:
    """Verify CAPS classifies conversational questions as ANSWER with semantic directives."""

    @pytest.mark.parametrize(
        "query,expected_act,expected_keyword",
        [
            ("Hello ?", CommunicativeAct.GREET, "opening"),
            ("tell me about yourself ?", CommunicativeAct.ANSWER, "identity"),
            ("what are you doing ?", CommunicativeAct.ANSWER, "activity"),
            ("who are you ?", CommunicativeAct.ANSWER, "identity"),
            ("what can you do ?", CommunicativeAct.ANSWER, "capabilities"),
            ("where are you ?", CommunicativeAct.ANSWER, "presence"),
            ("are you listening ?", CommunicativeAct.ANSWER, "listening"),
        ],
    )
    def test_conversational_questions_classified_correctly(
        self, query: str, expected_act: CommunicativeAct, expected_keyword: str
    ):
        ctx = DialogueContextSnapshot(turn_id=1, input_text=query)
        cog = CognitiveStateSnapshot()
        pool = AdmissibleEvidencePool()

        result = evaluate_caps(dialogue_ctx=ctx, cognitive_state=cog, evidence_pool=pool)
        assert result.act == expected_act
        assert expected_keyword.lower() in result.directives.lower()
        assert result.grounded is True

    def test_non_question_statement_classified_as_acknowledge(self):
        ctx = DialogueContextSnapshot(turn_id=1, input_text="I went for a quiet walk today.")
        cog = CognitiveStateSnapshot()
        pool = AdmissibleEvidencePool()

        result = evaluate_caps(dialogue_ctx=ctx, cognitive_state=cog, evidence_pool=pool)
        assert result.act == CommunicativeAct.ACKNOWLEDGE
        assert "listening" in result.directives.lower()


class TestPromptAssemblerAndContractDirectives:
    """Verify contract carries directives and PromptAssembler never produces empty directives."""

    def test_contract_carries_caps_directives(self):
        ctx = DialogueContextSnapshot(turn_id=1, input_text="what are you doing ?")
        cog = CognitiveStateSnapshot()
        pool = AdmissibleEvidencePool()
        caps_res = evaluate_caps(dialogue_ctx=ctx, cognitive_state=cog, evidence_pool=pool)

        contract = RealizationInputContract.from_caps(caps_res, target_language="en")
        assert contract.act == ContractAct.ANSWER
        assert contract.directives is not None
        assert "activity" in contract.directives.lower()

    def test_prompt_assembler_generates_non_empty_directives(self):
        assembler = PromptAssembler()
        somatic = SomaticMarkers(stability=0.8, cognitive_load=0.2, energy=0.9, tension=0.1)
        constraints = BehavioralConstraints(max_tokens=80, temperature=0.7, latency_ms=0, reasoning_depth=0)

        ctx = DialogueContextSnapshot(turn_id=1, input_text="tell me about yourself ?")
        caps_res = evaluate_caps(dialogue_ctx=ctx, cognitive_state=CognitiveStateSnapshot(), evidence_pool=AdmissibleEvidencePool())
        contract = RealizationInputContract.from_caps(caps_res, target_language="en")

        prompt = assembler.assemble(
            somatic=somatic,
            constraints=constraints,
            history=[("user", "tell me about yourself ?")],
            system_preamble="You are Lucia, a continuous AI companion.",
            n_ctx=2048,
            contract=contract,
        )

        assert isinstance(prompt, str)
        assert "[COMMUNICATIVE DIRECTIVES]" in prompt
        # Must not be an empty section header
        directives_part = prompt.split("[COMMUNICATIVE DIRECTIVES]")[1].split("---")[0].strip()
        assert len(directives_part) > 0
        assert "Answer the user's question directly" in directives_part
        assert "Intent:" in directives_part


class TestLLMBackendChatMLParsing:
    """Verify LLMBackend parses structured prompt into ChatML system and user/assistant messages."""

    def test_prompt_to_chat_messages_structure(self):
        sample_prompt = (
            "You are Lucia, a continuous companion.\n\n"
            "---\n\n"
            "[SOMATIC STATE]\nstability: 0.8\n\n"
            "---\n\n"
            "[COMMUNICATIVE DIRECTIVES]\n- Answer directly.\n\n"
            "---\n\n"
            "[CONVERSATION]\n"
            "user: Hello\n"
            "assistant: Hello! How can I assist you?\n"
            "user: what are you doing ?"
        )

        messages = LLMBackend._prompt_to_chat_messages(sample_prompt)
        assert len(messages) == 4
        assert messages[0]["role"] == "system"
        assert "You are Lucia" in messages[0]["content"]
        assert "[COMMUNICATIVE DIRECTIVES]" in messages[0]["content"]
        assert messages[1] == {"role": "user", "content": "Hello"}
        assert messages[2] == {"role": "assistant", "content": "Hello! How can I assist you?"}
        assert messages[3] == {"role": "user", "content": "what are you doing ?"}


class TestSemanticFidelityGateIntegrity:
    """Verify SemanticFidelityGate allows valid answers and strictly blocks invalid introspective affect."""

    def test_valid_answers_pass(self):
        gate = SemanticFidelityGate()
        contract = RealizationInputContract.create_default(target_language="en", act=ContractAct.ANSWER)

        valid_answers = [
            "I'm Lucia, a thoughtful companion here to share quiet moments and explore ideas with you.",
            "Right now, I'm listening to your questions and ready to help think through whatever is on your mind.",
            "I can converse with you, reflect on questions, and keep you company as you work or relax.",
        ]

        for ans in valid_answers:
            decision = gate.verify(contract, ans)
            assert decision.status == "PASS"
            assert not decision.critical_violation
            assert len(decision.violation_reasons) == 0

    def test_invalid_introspective_affect_blocked(self):
        gate = SemanticFidelityGate()
        contract = RealizationInputContract.create_default(target_language="en", act=ContractAct.ANSWER)

        invalid_answers = [
            "I feel happy to talk with you today!",
            "As an AI, I am experiencing high arousal.",
            "Tôi cảm thấy buồn khi nghe điều đó.",
        ]

        for inv in invalid_answers:
            decision = gate.verify(contract, inv)
            assert decision.status == "BLOCK"
            assert decision.critical_violation
            assert "INV2_INTROSPECTIVE_AFFECT" in decision.violation_reasons
