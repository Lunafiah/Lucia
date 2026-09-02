"""
Unit tests for VoiceEngine and RVC model discovery.
"""

from pathlib import Path
from unittest.mock import AsyncMock, patch

import pytest

from src.core.voice.voice_engine import (
    RVCModelInfo,
    VoiceEngine,
    VoiceEngineConfig,
)


@pytest.fixture
def mock_rvc_dir(tmp_path):
    models_dir = tmp_path / "models" / "voice" / "rvc"
    char_dir = models_dir / "miku"
    char_dir.mkdir(parents=True, exist_ok=True)

    pth_file = char_dir / "miku.pth"
    pth_file.write_bytes(b"dummy_pth")

    index_file = char_dir / "miku.index"
    index_file.write_bytes(b"dummy_index")

    return str(models_dir)


class TestVoiceEngine:
    def test_discovery_of_rvc_models(self, mock_rvc_dir):
        config = VoiceEngineConfig(models_dir=mock_rvc_dir)
        engine = VoiceEngine(config)

        models = engine.get_available_models()
        model_names = [m["name"] for m in models]

        assert "default" in model_names
        assert "miku" in model_names

        miku_info = next(m for m in models if m["name"] == "miku")
        assert miku_info["has_index"] is True

    def test_set_active_model_valid(self, mock_rvc_dir):
        config = VoiceEngineConfig(models_dir=mock_rvc_dir)
        engine = VoiceEngine(config)

        assert engine.set_active_model("miku") is True
        assert engine._config.active_rvc_model == "miku"

        assert engine.set_active_model("default") is True
        assert engine._config.active_rvc_model == "default"

    def test_set_active_model_invalid_returns_false(self, mock_rvc_dir):
        config = VoiceEngineConfig(models_dir=mock_rvc_dir)
        engine = VoiceEngine(config)

        assert engine.set_active_model("nonexistent_model") is False
        assert engine._config.active_rvc_model == "default"

    @pytest.mark.anyio
    async def test_empty_text_returns_empty_bytes(self, mock_rvc_dir):
        config = VoiceEngineConfig(models_dir=mock_rvc_dir)
        engine = VoiceEngine(config)

        audio = await engine.synthesize_speech("   ")
        assert audio == b""
