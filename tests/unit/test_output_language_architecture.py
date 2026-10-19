"""
tests/unit/test_output_language_architecture.py

Regression Test Suite for Simplified Lucia Output Language Architecture.
Companion Architecture Decision: ADR-035 / Phase 23 Output Realization Simplification.

Verifies:
1. Multilingual input perception enters language-independent semantic representation.
2. Production text target is canonically English ('en').
3. Production voice target is canonically Japanese ('ja').
4. English and Japanese targets do NOT leak into cognition or semantic representations.
5. Realization branches are parallel and decoupled (voice realizes directly from semantic/pragmatic state).
6. First-person dyadic companion perspective is strictly enforced (narrator drift is blocked).
7. Non-English research realization paths remain available when explicitly requested.
"""

from __future__ import annotations

import re
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest
import numpy as np

from src.core.communication.caps import (
    AdmissibleEvidencePool,
    CAPSResult,
    CognitiveStateSnapshot,
    CommunicativeAct,
    DialogueContextSnapshot,
    EpistemicMetadata,
    ProvenanceMetadata,
    ResolutionAdmissibilityMetadata,
    ResolutionStatus,
    evaluate_caps,
)
from src.core.config import MemoryOrchestratorConfig
from src.core.knowledge.fortification import (
    EpistemicState,
    SemanticGraph,
    SemanticNode,
)
from src.core.knowledge.proposition import Proposition, ProvenanceType
from src.core.language.contract import (
    CANONICAL_TEXT_OUTPUT_LANGUAGE,
    CANONICAL_VOICE_OUTPUT_LANGUAGE,
    EpistemicStatus,
    RealizationInputContract,
    RealizationOutput,
    SemanticRoleBinding,
    TextRealization,
    VoiceRealization,
)
from src.core.language.detection import detect_active_language
from src.core.language.gate import GateDecision, SemanticFidelityGate
from src.core.language.realization import (
    construct_realization_output,
    realize_japanese_voice_text,
)
from src.core.orchestrator.cognitive_orchestrator import (
    CognitiveOrchestrator,
    build_cognitive_orchestrator,
)
from src.core.orchestrator.policies import CognitiveTurnResult
from src.core.orchestrator.prompt_assembler import PromptAssembler
from src.core.models import BehavioralConstraints, SomaticMarkers


# ──────────────────────────────────────────────────────────────────────────────
# Fixtures
# ──────────────────────────────────────────────────────────────────────────────

@pytest.fixture
def mock_orchestrator(tmp_path):
    """Provides CognitiveOrchestrator with isolated LLM backend."""
    model_file = tmp_path / "model.gguf"
    model_file.write_bytes(b"mock-weights")

    config = MemoryOrchestratorConfig(
        model_path=str(model_file),
        loop_cadence_ms=100,
        decay_loop_cadence_seconds=60,
        fallback_response="I hear you, and I am listening with quiet attention.",
    )

    with patch("src.core.orchestrator.cognitive_orchestrator.LLMBackend") as mock_llm_cls:
        mock_llm = MagicMock()
        mock_llm.is_ready.return_value = True
        mock_llm.generate.return_value = "I am truly glad we have met and can talk together."
        mock_llm.translate_to_japanese.return_value = "お会いできて嬉しいです。"
        mock_llm_cls.return_value = mock_llm

        orch = build_cognitive_orchestrator(
            config,
            relationship_storage_path=tmp_path / "relationship.json",
        )
        yield orch, mock_llm
        orch.shutdown()


# ──────────────────────────────────────────────────────────────────────────────
# Test Suite: Output Language Simplification & Decoupled Realization
# ──────────────────────────────────────────────────────────────────────────────

class TestOutputLanguageArchitecture:
    """Verifies that English text + Japanese voice are canonical realization targets."""

    def test_canonical_constants(self):
        """1. Verify canonical output language constants."""
        assert CANONICAL_TEXT_OUTPUT_LANGUAGE == "en"
        assert CANONICAL_VOICE_OUTPUT_LANGUAGE == "ja"

    def test_multilingual_input_to_production_targets(self, mock_orchestrator):
        """
        2. Multilingual input (VI, JA, EN) perception produces:
           text target = 'en'
           voice target = 'ja'
        """
        orch, mock_llm = mock_orchestrator
        mock_llm.generate.return_value = "I am truly glad we have met and can talk together."

        test_inputs = [
            ("vi", "Chào em. Cuối cùng cũng gặp em rồi."),
            ("ja", "こんにちは、ルシア。元気ですか？"),
            ("en", "Hello Lucia, it is good to finally meet you."),
        ]

        for source_lang, user_query in test_inputs:
            # Execute turn through production entrypoint (no user_language override)
            result = orch.process(user_query)

            assert isinstance(result, CognitiveTurnResult)
            assert result.realization is not None

            # Production Text target is ALWAYS English
            assert result.realization.text.language == "en"
            assert len(result.realization.text.content) > 0
            # Ensure text is not Vietnamese or Japanese
            assert not any("\u3040" <= c <= "\u309f" for c in result.realization.text.content)

            # Production Voice target is ALWAYS Japanese
            assert result.realization.voice.language == "ja"
            voice_content = result.realization.voice.content
            assert len(voice_content) > 0
            # Voice content must contain Japanese characters (hiragana/katakana/kanji)
            has_japanese = any(
                "\u3040" <= c <= "\u309f" or "\u30a0" <= c <= "\u30ff" or "\u4e00" <= c <= "\u9fff"
                for c in voice_content
            )
            assert has_japanese, f"Expected Japanese voice text, got: {voice_content}"

            # Contract target_language in cognitive pipeline was 'en'
            assert result.realization_contract.target_language == "en"

    def test_direct_parallel_voice_realization_independent_of_english(self):
        """
        3. Japanese voice realizes directly from semantic/pragmatic contract
           without requiring English text translation.
        """
        contract_greet = RealizationInputContract.create_default(
            target_language="en",
            act=CommunicativeAct.GREET,
        )
        voice_greet = realize_japanese_voice_text(contract_greet)
        assert "こんにちは" in voice_greet

        contract_refuse = RealizationInputContract.create_default(
            target_language="en",
            act=CommunicativeAct.REFUSE,
        )
        voice_refuse = realize_japanese_voice_text(contract_refuse)
        assert "お答えできません" in voice_refuse or "情報がないため" in voice_refuse

        contract_neg = RealizationInputContract(
            contract_id="c_neg",
            target_language="en",
            act=CommunicativeAct.ASSERT,
            polarity=False,
            epistemic_status=EpistemicStatus.FACT,
        )
        voice_neg = realize_japanese_voice_text(contract_neg)
        assert "完了していません" in voice_neg or "ない" in voice_neg

        # Construct realization output without translated text
        out = construct_realization_output(
            safe_response="I cannot answer this question without verified data.",
            user_language="en",
            contract=contract_refuse,
            japanese_voice_text=None,
        )
        assert out.text.language == "en"
        assert out.text.content == "I cannot answer this question without verified data."
        assert out.voice.language == "ja"
        assert out.voice.content == voice_refuse

    def test_dyadic_perspective_enforcement_blocks_narrator_drift(self):
        """
        4. Perspective / Dyadic grounding:
           Blocks external-observer / narrator drift ('two people', 'hai người', '二人').
        """
        gate = SemanticFidelityGate()
        contract_en = RealizationInputContract.create_default(
            target_language="en",
            act=CommunicativeAct.ASSERT,
        )

        # Narrator drift candidates in English
        drift_candidates_en = [
            "Two people are having a conversation right now.",
            "The two of them can talk together.",
            "Both people are happy to meet.",
        ]
        for candidate in drift_candidates_en:
            decision = gate.verify(contract_en, candidate)
            assert decision.status == "BLOCK"
            assert "DYADIC_PERSPECTIVE_DRIFT" in decision.violation_reasons
            # Fallback must be clean first-person dyadic
            assert decision.fallback_text is not None
            assert "two people" not in decision.fallback_text.lower()

        # Narrator drift candidates in Vietnamese
        contract_vi = RealizationInputContract.create_default(
            target_language="vi",
            act=CommunicativeAct.ASSERT,
            speaker_honorific="em",
            addressee_honorific="anh",
        )
        drift_candidates_vi = [
            "Cuối cùng hai người cũng được gặp nhau.",
            "Hai đứa mình có thể nói chuyện rồi.",
            "Cả hai người hãy bắt đầu nhé.",
        ]
        for candidate in drift_candidates_vi:
            decision = gate.verify(contract_vi, candidate)
            assert decision.status == "BLOCK"
            assert "DYADIC_PERSPECTIVE_DRIFT" in decision.violation_reasons
            assert "hai người" not in decision.fallback_text

        # First-person companion candidates PASS
        valid_en = "I am truly glad we have met and can talk together."
        dec_valid_en = gate.verify(contract_en, valid_en)
        assert dec_valid_en.status == "PASS"

        valid_vi = "Dạ, em chào anh ạ. Cuối cùng em và anh đã được trò chuyện cùng nhau."
        dec_valid_vi = gate.verify(contract_vi, valid_vi)
        assert dec_valid_vi.status == "PASS"

    def test_no_language_leakage_into_cognitive_representations(self):
        """
        5. Verify that neither 'en' nor 'ja' leaks into language-independent
           cognition or semantic substrate representations.
        """
        # Semantic graph nodes contain abstract concepts, zero surface language tokens
        node = SemanticNode(
            id="n:encounter_1",
            concept_symbol="c:MUTUAL_ENCOUNTER",
            epistemic_state=EpistemicState.FACT,
            polarity=True,
            provenance=None,
        )
        assert not node.concept_symbol.startswith("en:")
        assert not node.concept_symbol.startswith("ja:")
        assert not node.concept_symbol.startswith("vi:")

        # CAPS evaluates intent purely on epistemic & dialogue state
        ctx = DialogueContextSnapshot(turn_id=1, input_text="Em biết đây là lần đầu mình nói chuyện không?")
        evidence_pool = AdmissibleEvidencePool(verified_propositions=(
            Proposition(
                id="prop:1",
                subject="ent:lucia",
                predicate="c:IS_FIRST_CONVERSATION",
                object="true",
                confidence=1.0,
                provenance=ProvenanceType.VERIFIED,
            ),
        ))

        caps = evaluate_caps(ctx, CognitiveStateSnapshot(), evidence_pool)
        assert caps.act in (CommunicativeAct.ACKNOWLEDGE, CommunicativeAct.ANSWER)
        assert caps.target_predicate in ("c:ENCOUNTER", "c:IS_FIRST_CONVERSATION")
        # Target predicate is purely semantic
        assert ":" in caps.target_predicate

    def test_research_override_path_retained(self, mock_orchestrator):
        """
        6. Explicitly specifying user_language allows research evaluation
           of non-English realization paths without mutating production defaults.
        """
        orch, mock_llm = mock_orchestrator
        mock_llm.generate.return_value = "Dạ, em chào anh ạ. Em rất vui được trò chuyện cùng anh."

        # Explicit non-production override
        result = orch.process("Chào em", user_language="vi")

        assert result.realization.text.language == "vi"
        assert result.realization.voice.language == "ja"

        # Subsequent call without user_language returns to canonical 'en' production target
        mock_llm.generate.return_value = "Hello! I am glad to be here with you."
        res_prod = orch.process("Chào em")
        assert res_prod.realization.text.language == "en"
        assert res_prod.realization.voice.language == "ja"
