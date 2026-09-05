"""
Unit tests for SpeechToTextEngine and /voice/transcribe API endpoint.
"""

from unittest.mock import MagicMock, patch
import pytest
from starlette.testclient import TestClient

from src.core.voice.stt_engine import SpeechToTextEngine, SpeechToTextConfig
from src.api.server import app


class TestSpeechToTextEngine:
    def test_empty_audio_bytes_returns_empty_string(self):
        engine = SpeechToTextEngine()
        assert engine.transcribe_bytes(b"") == ""
        assert engine.transcribe_bytes(b"short") == ""

    @patch("faster_whisper.WhisperModel")
    def test_transcribe_segments_joined(self, mock_whisper_cls):
        mock_model = MagicMock()
        mock_whisper_cls.return_value = mock_model

        mock_seg1 = MagicMock()
        mock_seg1.text = "Xin chào"
        mock_seg2 = MagicMock()
        mock_seg2.text = "Lucia"

        mock_model.transcribe.return_value = ([mock_seg1, mock_seg2], MagicMock())

        engine = SpeechToTextEngine()
        engine._model = mock_model

        # Feed dummy bytes larger than 128 bytes
        dummy_audio = b"0" * 256
        result = engine.transcribe_bytes(dummy_audio)
        assert result == "Xin chào Lucia"


class TestVoiceTranscribeEndpoint:
    @pytest.fixture
    def client(self):
        return TestClient(app)

    def test_empty_transcribe_returns_ok_empty(self, client):
        response = client.post("/voice/transcribe", content=b"")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "ok"
        assert data["text"] == ""

    @patch("src.api.server.get_stt_engine")
    def test_transcribe_file_upload(self, mock_get_stt, client):
        mock_engine = MagicMock()
        mock_engine.transcribe_bytes.return_value = "Hôm nay thời tiết thế nào?"
        mock_get_stt.return_value = mock_engine

        files = {"file": ("speech.webm", b"mock_audio_data_stream_1234567890", "audio/webm")}
        response = client.post("/voice/transcribe", files=files)
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "ok"
        assert data["text"] == "Hôm nay thời tiết thế nào?"
