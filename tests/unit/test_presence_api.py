"""
Unit tests for presence & voice FastAPI endpoints.
"""

from unittest.mock import AsyncMock, patch

import pytest
from fastapi.testclient import TestClient

from src.api.server import app


@pytest.fixture
def client():
    return TestClient(app)


class TestPresenceVoiceAPI:
    def test_get_voice_models(self, client):
        response = client.get("/voice/models")
        assert response.status_code == 200
        data = response.json()
        assert "models" in data
        assert "active_model" in data
        assert len(data["models"]) >= 1

    def test_select_voice_model_default(self, client):
        response = client.post("/voice/select-model", json={"model_name": "default"})
        assert response.status_code == 200
        assert response.json()["active_model"] == "default"

    def test_select_voice_model_invalid_404(self, client):
        response = client.post(
            "/voice/select-model", json={"model_name": "definitely_not_a_model_12345"}
        )
        assert response.status_code == 404

    def test_synthesize_voice_empty_text(self, client):
        response = client.post("/voice/synthesize", json={"text": "   "})
        assert response.status_code == 200
        assert response.content == b""

    @patch("src.core.voice.voice_engine.VoiceEngine.synthesize_speech", new_callable=AsyncMock)
    def test_synthesize_voice_success(self, mock_synth, client):
        mock_synth.return_value = b"RIFFfakeaudio"
        response = client.post("/voice/synthesize", json={"text": "Hello Lucia"})
        assert response.status_code == 200
        assert response.content == b"RIFFfakeaudio"
        assert response.headers["content-type"] == "audio/mpeg"
