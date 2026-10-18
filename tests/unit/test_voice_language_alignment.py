"""
Unit and regression tests for Lucia Voice & Language Runtime Alignment.

Verifies:
1. English input: text language = en, voice language = ja
2. Vietnamese input: text language = vi, voice language = ja
3. Japanese input: text language = ja, voice language = ja
4. Voice boundary receives explicit language metadata
5. VoiceEngine does NOT infer voice language from arbitrary text
6. Japanese voice path uses the configured Japanese voice (ja-JP-NanamiNeural)
7. RVC configuration behaves consistently with verified Phase 24 pipeline (VaresaGIJP, index_rate 0.25)
8. Non-RVC fallback does not receive unsafe unconditional +60Hz pitch boost (uses +0Hz)
9. Audio playback remains functional with blob media under Electron CSP
"""

from __future__ import annotations

import asyncio
from pathlib import Path
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from src.core.language.detection import detect_active_language
from src.core.language.contract import (
    CommunicativeAct,
    EpistemicStatus,
    RealizationInputContract,
    RealizationOutput,
    SemanticRoleBinding,
    TextRealization,
    VoiceRealization,
)
from src.core.language.realization import (
    construct_realization_output,
    realize_japanese_voice_text,
)
from src.core.voice.voice_engine import VoiceEngine, VoiceEngineConfig, _DEFAULT_VOICE


# ---------------------------------------------------------------------------
# Tests 1-3: Language Decoupling (Text follows user language, Voice is Japanese)
# ---------------------------------------------------------------------------

class TestLanguageRealizationDecoupling:
    """Test text/voice language decoupling and deterministic Japanese realization."""

    def _create_sample_contract(self, target_lang: str) -> RealizationInputContract:
        role = SemanticRoleBinding(
            role=":ARG1",
            concept_id="concept:user",
            canonical_lemma="friend",
        )
        return RealizationInputContract(
            contract_id="test_contract_1",
            target_language=target_lang,
            act=CommunicativeAct.ACKNOWLEDGE,
            polarity=True,
            epistemic_status=EpistemicStatus.FACT,
            role_bindings=(role,),
        )

    def test_english_input_decoupling(self):
        """1. English input: text language = en, voice language = ja."""
        detected = detect_active_language("Hello Lucia, how are you today?")
        assert detected == "en"

        contract = self._create_sample_contract(detected)
        realization = construct_realization_output(
            safe_response="I am here with you.",
            user_language=detected,
            contract=contract,
        )

        assert realization.text.language == "en"
        assert realization.text.content == "I am here with you."
        assert realization.voice.language == "ja"
        # Spoken realization must be Japanese
        assert any("\u3040" <= c <= "\u309f" or "\u30a0" <= c <= "\u30ff" or "\u4e00" <= c <= "\u9fff" for c in realization.voice.content)

    def test_vietnamese_input_decoupling(self):
        """2. Vietnamese input: text language = vi, voice language = ja."""
        detected = detect_active_language("Chào bạn, hôm nay bạn thế nào?")
        assert detected == "vi"

        contract = self._create_sample_contract(detected)
        realization = construct_realization_output(
            safe_response="Mình luôn ở đây cùng bạn.",
            user_language=detected,
            contract=contract,
        )

        assert realization.text.language == "vi"
        assert realization.text.content == "Mình luôn ở đây cùng bạn."
        assert realization.voice.language == "ja"
        # Spoken realization must be Japanese
        assert any("\u3040" <= c <= "\u309f" or "\u30a0" <= c <= "\u30ff" or "\u4e00" <= c <= "\u9fff" for c in realization.voice.content)

    def test_japanese_input_decoupling(self):
        """3. Japanese input: text language = ja, voice language = ja."""
        detected = detect_active_language("こんにちは、ルシア。元気ですか？")
        assert detected == "ja"

        contract = self._create_sample_contract(detected)
        realization = construct_realization_output(
            safe_response="はい、元気ですよ。一緒にいます。",
            user_language=detected,
            contract=contract,
        )

        assert realization.text.language == "ja"
        assert realization.text.content == "はい、元気ですよ。一緒にいます。"
        assert realization.voice.language == "ja"
        # When text is already Japanese, voice directly shares the natural generated Japanese
        assert realization.voice.content == "はい、元気ですよ。一緒にいます。"


# ---------------------------------------------------------------------------
# Test 4: Voice boundary receives explicit language metadata
# ---------------------------------------------------------------------------

class TestVoiceBoundaryMetadata:
    """Test explicit language metadata across realization -> voice boundary."""

    def test_realization_output_contract_shape(self):
        """4a. RealizationOutput explicitly bundles text and voice with language tags."""
        t = TextRealization(content="Hello", language="en")
        v = VoiceRealization(content="こんにちは", language="ja")
        out = RealizationOutput(text=t, voice=v)

        d = out.to_dict()
        assert d["text"]["language"] == "en"
        assert d["text"]["content"] == "Hello"
        assert d["voice"]["language"] == "ja"
        assert d["voice"]["content"] == "こんにちは"

    def test_synthesize_speech_explicit_language_parameter(self):
        """4b. VoiceEngine.synthesize_speech accepts explicit language='ja'."""
        config = VoiceEngineConfig(active_rvc_model="default")
        engine = VoiceEngine(config)

        # synthesize_speech parameter accepts explicit language
        import inspect
        sig = inspect.signature(engine.synthesize_speech)
        assert "language" in sig.parameters
        assert sig.parameters["language"].default == "ja"


# ---------------------------------------------------------------------------
# Test 5 & 6: VoiceEngine does NOT infer voice language from text & uses Japanese voice
# ---------------------------------------------------------------------------

class DummyCommunicate:
    last_instance = None

    def __init__(self, *args, **kwargs):
        self.args = args
        self.kwargs = kwargs
        DummyCommunicate.last_instance = self

    async def stream(self):
        if False:
            yield None


class TestVoiceEngineLanguageHandling:
    """Test VoiceEngine language discipline and Japanese voice selection."""

    @pytest.mark.anyio
    async def test_voice_engine_does_not_infer_language_from_text(self):
        """5. VoiceEngine must NOT inspect text content to dynamically switch voice languages."""
        config = VoiceEngineConfig(base_voice="ja-JP-NanamiNeural", active_rvc_model="default")
        engine = VoiceEngine(config)

        with patch("edge_tts.Communicate", DummyCommunicate):
            # Call with English text
            await engine.synthesize_speech("English sentence", language="ja")
            assert DummyCommunicate.last_instance.kwargs["voice"] == "ja-JP-NanamiNeural"

            # Call with Vietnamese text
            await engine.synthesize_speech("Câu tiếng Việt", language="ja")
            assert DummyCommunicate.last_instance.kwargs["voice"] == "ja-JP-NanamiNeural"

            # Call with Japanese text
            await engine.synthesize_speech("日本語のテキスト", language="ja")
            assert DummyCommunicate.last_instance.kwargs["voice"] == "ja-JP-NanamiNeural"

    def test_default_base_voice_is_japanese(self):
        """6. Default base voice must be configured to Japanese ja-JP-NanamiNeural."""
        assert _DEFAULT_VOICE == "ja-JP-NanamiNeural"
        config = VoiceEngineConfig()
        assert config.base_voice == "ja-JP-NanamiNeural"


# ---------------------------------------------------------------------------
# Test 7: Phase 24 RVC Configuration Parity
# ---------------------------------------------------------------------------

class TestPhase24RVCConfiguration:
    """Test Phase 24 canonical RVC configuration restoration."""

    def test_canonical_varesa_auto_selection(self, tmp_path):
        """7. VoiceEngineConfig auto-discovers VaresaGIJP if present in models_dir."""
        # Setup simulated models dir with VaresaGIJP
        rvc_dir = tmp_path / "rvc"
        varesa_dir = rvc_dir / "VaresaGIJP"
        varesa_dir.mkdir(parents=True)
        (varesa_dir / "VaresaGIJP.pth").write_bytes(b"dummy")

        # When active_rvc_model is 'default', config auto-selects VaresaGIJP
        config = VoiceEngineConfig(models_dir=str(rvc_dir), active_rvc_model="default")
        assert config.active_rvc_model == "VaresaGIJP"
        assert config.index_rate == 0.25


# ---------------------------------------------------------------------------
# Test 8: Non-RVC fallback safe pitch (+0Hz vs +60Hz)
# ---------------------------------------------------------------------------

class TestPitchDiscipline:
    """Test safe pitch logic: non-RVC fallback must NOT receive +60Hz boost."""

    @pytest.mark.anyio
    async def test_non_rvc_fallback_receives_zero_hz(self, tmp_path):
        """8a. Non-RVC path uses +0Hz to prevent chipmunk distortion."""
        empty_dir = tmp_path / "empty_rvc"
        empty_dir.mkdir(parents=True)
        config = VoiceEngineConfig(models_dir=str(empty_dir), active_rvc_model="default")
        engine = VoiceEngine(config)

        with patch("edge_tts.Communicate", DummyCommunicate):
            await engine.synthesize_speech("こんにちは", language="ja")
            # Since RVC is inactive/default, pitch must be +0Hz
            assert DummyCommunicate.last_instance.kwargs["pitch"] == "+0Hz"

    @pytest.mark.anyio
    async def test_rvc_active_receives_phase24_60hz_boost(self, tmp_path):
        """8b. When RVC is active, base TTS uses +60Hz (Phase 24 ADR-032 acoustic base)."""
        rvc_dir = tmp_path / "rvc"
        varesa_dir = rvc_dir / "VaresaGIJP"
        varesa_dir.mkdir(parents=True)
        (varesa_dir / "VaresaGIJP.pth").write_bytes(b"dummy")

        config = VoiceEngineConfig(models_dir=str(rvc_dir), active_rvc_model="VaresaGIJP")
        engine = VoiceEngine(config)

        # RVC model is in _available_models
        engine._available_models["VaresaGIJP"] = MagicMock()

        with patch("edge_tts.Communicate", DummyCommunicate):
            await engine.synthesize_speech("こんにちは", language="ja")
            assert DummyCommunicate.last_instance.kwargs["pitch"] == "+60Hz"

    @pytest.mark.anyio
    async def test_explicit_pitch_override_respected(self):
        """8c. Explicitly provided pitch parameter overrides defaults."""
        config = VoiceEngineConfig(active_rvc_model="default")
        engine = VoiceEngine(config)

        with patch("edge_tts.Communicate", DummyCommunicate):
            await engine.synthesize_speech("こんにちは", language="ja", pitch="+15Hz")
            assert DummyCommunicate.last_instance.kwargs["pitch"] == "+15Hz"


# ---------------------------------------------------------------------------
# Test 9: Electron CSP and Playback Safety
# ---------------------------------------------------------------------------

class TestElectronPlaybackSafety:
    """Test Electron CSP includes blob media and playback error handling."""

    def test_electron_index_html_csp_includes_blob_media(self):
        """9a. electron/renderer/index.html includes media-src 'self' blob:."""
        index_html_path = Path(__file__).resolve().parents[2] / "electron" / "renderer" / "index.html"
        assert index_html_path.is_file(), f"Missing {index_html_path}"
        content = index_html_path.read_text(encoding="utf-8")

        # Verify Content-Security-Policy meta tag allows blob: for media
        assert "media-src 'self' blob:" in content

    def test_lip_sync_audio_play_rejection_handled(self):
        """9b. lip-sync.js wraps audio.play() in catch handler and invokes onEnded."""
        lip_sync_path = Path(__file__).resolve().parents[2] / "electron" / "renderer" / "avatar" / "lip-sync.js"
        assert lip_sync_path.is_file(), f"Missing {lip_sync_path}"
        content = lip_sync_path.read_text(encoding="utf-8")

        # Verify play() error handling
        assert "audio.play()" in content
        assert "playPromise.catch" in content or "catch" in content
        assert "onEnded" in content

    def test_construct_realization_with_turn_specific_japanese(self):
        """10. construct_realization_output prioritizes turn-specific translated Japanese voice text."""
        contract = RealizationInputContract(
            contract_id="c_turn_spec",
            target_language="en",
            act=CommunicativeAct.ASSERT,
            polarity=True,
            epistemic_status=EpistemicStatus.FACT,
        )
        # Without specific Japanese text -> fallback template
        out1 = construct_realization_output(
            safe_response="Quantum entanglement is fascinating.",
            user_language="en",
            contract=contract,
        )
        assert out1.voice.language == "ja"

        # With turn-specific Japanese translation -> uses translated text
        out2 = construct_realization_output(
            safe_response="Quantum entanglement is fascinating.",
            user_language="en",
            contract=contract,
            japanese_voice_text="量子もつれは実に魅力的です。",
        )
        assert out2.voice.language == "ja"
        assert out2.voice.content == "量子もつれは実に魅力的です。"

    @pytest.mark.anyio
    async def test_synthesize_speech_uses_to_thread_for_rvc(self):
        """11. VoiceEngine.synthesize_speech dispatches RVC conversion to asyncio.to_thread."""
        config = VoiceEngineConfig(active_rvc_model="VaresaGIJP")
        engine = VoiceEngine(config)
        engine._available_models["VaresaGIJP"] = MagicMock()

        dummy_audio = b"dummy_mp3_stream"
        dummy_res_audio = b"dummy_rvc_stream"

        with patch("edge_tts.Communicate", DummyCommunicate), \
             patch("src.core.voice.boundary.extract_boundaries", return_value=[]), \
             patch("src.core.voice.boundary.compute_f0_contour", return_value=None), \
             patch("src.core.voice.rvc_pipeline.decode_audio_to_16k", return_value=b"\x00" * 320), \
             patch.object(engine, "_apply_rvc_conversion", return_value=dummy_res_audio) as mock_rvc, \
             patch("asyncio.to_thread", side_effect=asyncio.to_thread) as mock_to_thread:

            # Mock stream chunk
            class MockCommWithData:
                def __init__(self, *args, **kwargs):
                    pass
                async def stream(self):
                    yield {"type": "audio", "data": dummy_audio}

            with patch("edge_tts.Communicate", MockCommWithData):
                result = await engine.synthesize_speech("こんにちは", language="ja")
                assert result == dummy_res_audio
                assert mock_to_thread.called
                assert mock_rvc.called
