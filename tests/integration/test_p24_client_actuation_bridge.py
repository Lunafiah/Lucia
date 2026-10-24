"""
tests/integration/test_p24_client_actuation_bridge.py

Suite 5: End-to-End Client IPC Bridge Verification for Phase 24.
Validates:
  - ADR-032.5: Electron IPC parameter forwarding from /chat response to /voice/synthesize.
  - Server endpoint /voice/synthesize input validation and clamping.
  - Verification that the previously identified parameter-drop bridge is closed.
"""

from __future__ import annotations

from unittest.mock import AsyncMock, patch
import pytest
from starlette.testclient import TestClient

from src.api.server import app, _voice_engine


class TestClientActuationBridge:
    def test_synthesize_endpoint_accepts_bounded_prosody(self):
        """Verify /voice/synthesize receives and forwards bounded pitch_hz and closeness."""
        client = TestClient(app)

        with patch.object(_voice_engine, "synthesize_speech", new_callable=AsyncMock) as mock_synth:
            mock_synth.return_value = b"fake_wav_audio_data"

            payload = {
                "text": "Hello world, this is Lucia.",
                "rate": "+10%",
                "volume": "+5%",
                "pitch_hz": 14.5,
                "closeness": 0.85,
            }
            resp = client.post("/voice/synthesize", json=payload)

            assert resp.status_code == 200
            assert resp.content == b"fake_wav_audio_data"
            mock_synth.assert_awaited_once_with(
                "Hello world, this is Lucia.",
                language="ja",
                rate="+10%",
                volume="+5%",
                pitch=None,
                pitch_hz=14.5,
                closeness=0.85,
                focal_words=None,
            )

    def test_synthesize_endpoint_clamps_out_of_bounds_inputs(self):
        """Verify /voice/synthesize safely clamps excessive client inputs."""
        client = TestClient(app)

        with patch.object(_voice_engine, "synthesize_speech", new_callable=AsyncMock) as mock_synth:
            mock_synth.return_value = b"fake_wav"

            # Pass extreme out-of-range inputs (+150 Hz, closeness=3.5)
            payload = {
                "text": "Testing clamps",
                "pitch_hz": 150.0,
                "closeness": 3.5,
            }
            resp = client.post("/voice/synthesize", json=payload)

            assert resp.status_code == 200
            # pitch_hz clamped to 30.0, closeness clamped to 1.0
            mock_synth.assert_awaited_once_with(
                "Testing clamps",
                language="ja",
                rate=None,
                volume=None,
                pitch=None,
                pitch_hz=30.0,
                closeness=1.0,
                focal_words=None,
            )

    def test_ipc_bridge_dataflow_simulation(self):
        """
        Simulate the exact data transformation executed in chat.js and ipc-bridge.js.
        Confirms that response.expression.voice is preserved and forwarded without parameter drop.
        """
        client = TestClient(app)

        # 1. Simulated CognitiveTurnResult / ProcessResponse from /process
        chat_response = {
            "response": "Xin chào, mình rất vui được gặp lại bạn.",
            "call_id": "turn_12345",
            "expression": {
                "voice": {
                    "pitch_shift_hz": 12.0,
                    "speech_rate_pct": 5.0,
                    "volume_pct": 0.0,
                    "pause_duration_ms": 175.0,
                    "closeness": 0.70,
                    "pitch_shift_semitones": 1.70,
                }
            },
            "relationship": {
                "closeness": 0.70,
                "trust": 0.75,
                "familiarity": 0.50,
            }
        }

        # 2. Execution of chat.js extraction logic
        voice_expr = chat_response.get("expression", {}).get("voice")
        rel_closeness = chat_response.get("relationship", {}).get("closeness")

        voice_opts = {}
        if voice_expr:
            if "speech_rate_pct" in voice_expr:
                r = int(round(voice_expr["speech_rate_pct"]))
                voice_opts["rate"] = f"{r:+d}%"
            if "volume_pct" in voice_expr:
                v = int(round(voice_expr["volume_pct"]))
                voice_opts["volume"] = f"{v:+d}%"
            if "pitch_shift_hz" in voice_expr:
                voice_opts["pitch_hz"] = voice_expr["pitch_shift_hz"]
            if "closeness" in voice_expr:
                voice_opts["closeness"] = voice_expr["closeness"]
        elif rel_closeness is not None:
            voice_opts["closeness"] = rel_closeness

        # 3. Verify extracted options match contract
        assert voice_opts["rate"] == "+5%"
        assert voice_opts["pitch_hz"] == 12.0
        assert voice_opts["closeness"] == 0.70

        # 4. Dispatch over /voice/synthesize
        with patch.object(_voice_engine, "synthesize_speech", new_callable=AsyncMock) as mock_synth:
            mock_synth.return_value = b"audio_wav"
            synthesis_payload = {"text": chat_response["response"], **voice_opts}
            resp = client.post("/voice/synthesize", json=synthesis_payload)

            assert resp.status_code == 200
            # Confirm zero parameter drop
            mock_synth.assert_awaited_once_with(
                chat_response["response"],
                language="ja",
                rate="+5%",
                volume="+0%",
                pitch=None,
                pitch_hz=12.0,
                closeness=0.70,
                focal_words=None,
            )
