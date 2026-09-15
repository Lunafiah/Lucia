"""
tests/evaluation_phase18/test_rvc_runtime.py

Comprehensive Test Suite for Phase 18 Authentic On-Device RVC v2 Neural Voice Runtime.

Covers:
- RVC-1: Model & Index Discovery (VaresaGIJP)
- RVC-2: Checkpoint Architecture Compatibility (all 457 tensors strict load)
- RVC-3: Real Japanese Speech Conversion (ja-JP-NanamiNeural -> VaresaGIJP)
- RVC-4: Mathematical Non-Identity Proof (post_rvc != base_tts, waveform L1 > 0.05, RMS > 50)
- RVC-5: Strict Status Taxonomy Separation (environment_limited vs failed)
- RVC-6: Zero False Reporting Guarantee (rvc_applied strictly False on failure/bypass)
- RVC-7: Output Audio Integrity (24kHz, mono, 16-bit PCM, finite, non-silent)
- RVC-8: Canonical Storage Isolation (data/profile.json and data/chat_history.json untouched)
"""

from __future__ import annotations

import asyncio
import hashlib
import io
import logging
from pathlib import Path
import wave

import numpy as np
import pytest
import torch

from src.core.voice.voice_engine import VoiceEngine, VoiceEngineConfig, RVCModelInfo
from src.core.voice.rvc_pipeline import (
    RVCPipeline,
    RVCConversionResult,
    SynthesizerTrn,
    decode_audio_to_16k,
)

logger = logging.getLogger("TestRVCRuntime")

# Baseline storage hashes
PROFILE_PATH = Path("data/profile.json")
CHAT_HISTORY_PATH = Path("data/chat_history.json")
BASELINE_PROFILE_SHA = "1bf496e742b503a324ecd27156e4e30b30ed35cab496897c3a831380fbf0f97c"
BASELINE_CHAT_SHA = "0344098fd533e972de4034fc1355f9b27c7617fce3b4fc7812a175d21fbd0165"

VARESA_DIR = Path("models/voice/rvc/VaresaGIJP")
VARESA_PTH = VARESA_DIR / "VaresaGIJP_300e_2100s.pth"
VARESA_INDEX = VARESA_DIR / "added_VaresaGIJP_v2.index"


class TestRVCRuntime:
    """Rigorous validation of the Phase 18 RVC neural inference runtime."""

    def test_rvc_1_discovery(self):
        """RVC-1: Verify VoiceEngine discovers VaresaGIJP with .pth and .index."""
        assert VARESA_PTH.exists(), f"VaresaGIJP checkpoint missing: {VARESA_PTH}"
        assert VARESA_INDEX.exists(), f"VaresaGIJP index missing: {VARESA_INDEX}"

        config = VoiceEngineConfig(models_dir="models/voice/rvc")
        engine = VoiceEngine(config)
        models = engine.get_available_models()

        varesa_model = next((m for m in models if m["name"] == "VaresaGIJP"), None)
        assert varesa_model is not None, "VaresaGIJP model was not discovered by VoiceEngine"
        assert varesa_model["has_index"] is True, "VaresaGIJP index file was not detected"
        assert "VaresaGIJP_300e_2100s.pth" in varesa_model["pth_path"]

    def test_rvc_2_checkpoint_architecture_compatibility(self):
        """
        RVC-2: Verify exact weight tensor compatibility between checkpoint and SynthesizerTrn.
        All 457 weight tensors must strictly match without missing or unexpected keys.
        """
        ckpt = torch.load(str(VARESA_PTH), map_location="cpu")
        assert "weight" in ckpt, "Checkpoint missing 'weight' dictionary"
        assert "config" in ckpt, "Checkpoint missing 'config' list"

        cfg = ckpt["config"]
        net_g = SynthesizerTrn(
            spec_channels=cfg[0],
            segment_size=cfg[1],
            inter_channels=cfg[2],
            hidden_channels=cfg[3],
            filter_channels=cfg[4],
            n_heads=cfg[5],
            n_layers=cfg[6],
            kernel_size=cfg[7],
            p_dropout=cfg[8],
            resblock=cfg[9],
            resblock_kernel_sizes=cfg[10],
            resblock_dilation_sizes=cfg[11],
            upsample_rates=cfg[12],
            upsample_initial_channel=cfg[13],
            upsample_kernel_sizes=cfg[14],
            spk_embed_dim=cfg[15],
            gin_channels=cfg[16],
            sr=cfg[17],
        )

        load_res = net_g.load_state_dict(ckpt["weight"], strict=True)
        assert len(load_res.missing_keys) == 0, f"Missing keys in SynthesizerTrn: {load_res.missing_keys}"
        assert len(load_res.unexpected_keys) == 0, f"Unexpected keys in SynthesizerTrn: {load_res.unexpected_keys}"
        assert len(ckpt["weight"]) == 457, f"Expected 457 weight tensors, got {len(ckpt['weight'])}"

    @pytest.mark.anyio
    async def test_rvc_3_and_4_real_speech_conversion_and_non_identity(self):
        """
        RVC-3 & RVC-4: Primary voice evidence on REAL Japanese speech.
        - Generates Japanese speech from canonical ja-JP-NanamiNeural.
        - Converts via RVCPipeline with VaresaGIJP neural weights.
        - Proves post_rvc != base_tts (non-identity proof: hash divergence, waveform L1 > 0.05).
        - Verifies RMS energy > 50 (non-silent).
        """
        text_jp = "こんにちは、ルシアです。システムは正常に稼働しています。"

        # 1. Generate base speech via VoiceEngine (active_rvc_model="default")
        config_base = VoiceEngineConfig(
            base_voice="ja-JP-NanamiNeural",
            active_rvc_model="default",
            models_dir="models/voice/rvc",
        )
        engine_base = VoiceEngine(config_base)
        base_audio = await engine_base.synthesize_speech(text_jp)
        assert len(base_audio) > 0, "Base TTS generated empty audio"
        base_sha256 = hashlib.sha256(base_audio).hexdigest()

        # 2. Run VoiceEngine with active_rvc_model="VaresaGIJP"
        config_rvc = VoiceEngineConfig(
            base_voice="ja-JP-NanamiNeural",
            active_rvc_model="VaresaGIJP",
            models_dir="models/voice/rvc",
        )
        engine_rvc = VoiceEngine(config_rvc)
        post_rvc_audio = await engine_rvc.synthesize_speech(text_jp)
        assert len(post_rvc_audio) > 0, "Post-RVC output is empty"
        post_sha256 = hashlib.sha256(post_rvc_audio).hexdigest()

        # 3. Verify RVC result status
        rvc_result: RVCConversionResult = engine_rvc.get_last_rvc_result()
        assert rvc_result is not None, "VoiceEngine failed to record RVCConversionResult"
        assert rvc_result.rvc_applied is True, f"RVC was not marked as applied: {rvc_result}"
        assert rvc_result.execution_status == "success", f"RVC status is {rvc_result.execution_status}: {rvc_result.error_message}"
        assert rvc_result.model_name == "VaresaGIJP"
        assert rvc_result.duration_ms > 1000.0, f"Converted audio too short: {rvc_result.duration_ms} ms"

        # 4. Mathematical Non-Identity Proof
        # Proof A: Cryptographic SHA-256 hash divergence
        assert post_sha256 != base_sha256, (
            "Cryptographic failure: post_rvc SHA-256 is identical to base_tts SHA-256! "
            "The pipeline returned unconverted input audio."
        )

        # Proof B: Audio waveform analysis & non-silence verification
        with wave.open(io.BytesIO(post_rvc_audio), "rb") as wf:
            assert wf.getnchannels() == 1, "Expected mono output"
            assert wf.getsampwidth() == 2, "Expected 16-bit PCM"
            assert wf.getframerate() == 24000, "Expected 24 kHz sample rate"
            n_frames = wf.getnframes()
            frames = wf.readframes(n_frames)
            post_samples = np.frombuffer(frames, dtype=np.int16).astype(np.float32)

        # Verify non-silent output
        rms = np.sqrt(np.mean(post_samples ** 2))
        assert rms > 50.0, f"Converted audio is effectively silent! RMS = {rms:.2f}"
        assert not np.any(np.isnan(post_samples)), "Output contains NaN values"
        assert not np.any(np.isinf(post_samples)), "Output contains Inf values"

        # Decode base audio to compare waveforms
        base_16k = decode_audio_to_16k(base_audio)
        post_16k = decode_audio_to_16k(post_rvc_audio)
        min_len = min(len(base_16k), len(post_16k))
        assert min_len > 16000, "Audio too short for statistical comparison"

        # Compute normalized waveform L1 distance
        norm_base = base_16k[:min_len] / (np.max(np.abs(base_16k[:min_len])) + 1e-8)
        norm_post = post_16k[:min_len] / (np.max(np.abs(post_16k[:min_len])) + 1e-8)
        mean_l1 = float(np.mean(np.abs(norm_post - norm_base)))
        logger.info("Measured normalized waveform mean L1 distance: %.4f", mean_l1)
        assert mean_l1 > 0.05, f"Waveform difference too small ({mean_l1:.4f} <= 0.05); conversion may be an identity"

    def test_rvc_5_strict_status_separation(self, tmp_path):
        """
        RVC-5: Verify strict separation between:
        - environment_limited: Missing checkpoint file
        - failed: Corrupted/malformed checkpoint or internal runtime error
        """
        pipeline = RVCPipeline(device="cpu")
        dummy_audio = b"RIFF....WAVEfmt ...."  # small dummy bytes

        # 1. Missing checkpoint -> environment_limited
        missing_pth = str(tmp_path / "nonexistent.pth")
        res_env = pipeline.convert(
            base_audio=dummy_audio,
            pth_path=missing_pth,
            model_name="MissingModel",
        )
        assert res_env.rvc_applied is False
        assert res_env.execution_status == "environment_limited"
        assert "not found" in res_env.error_message.lower()

        # 2. Corrupt checkpoint file -> failed
        corrupt_pth = tmp_path / "corrupt.pth"
        corrupt_pth.write_bytes(b"This is completely corrupt non-tar non-pickle junk data")
        res_fail = pipeline.convert(
            base_audio=dummy_audio,
            pth_path=str(corrupt_pth),
            model_name="CorruptModel",
        )
        assert res_fail.rvc_applied is False
        assert res_fail.execution_status == "failed"
        assert res_fail.error_message is not None

    def test_rvc_6_zero_false_reporting_guarantee(self, tmp_path):
        """
        RVC-6: Ensure rvc_applied is strictly False whenever RVC conversion does not execute.
        """
        # A: default voice -> rvc_applied is never set to True
        config_def = VoiceEngineConfig(active_rvc_model="default")
        engine_def = VoiceEngine(config_def)
        assert engine_def.get_last_rvc_result() is None

        # B: non-existent model requested -> set_active_model returns False
        assert engine_def.set_active_model("fake_persona") is False

        # C: pipeline returning failure -> VoiceEngine returns base_audio and rvc_applied is False
        engine_broken = VoiceEngine(VoiceEngineConfig(
            models_dir=str(tmp_path),
            active_rvc_model="default",
        ))
        mock_info = RVCModelInfo(name="broken", pth_path=str(tmp_path / "empty.pth"))
        out = engine_broken._apply_rvc_conversion(b"input_pcm", mock_info)
        assert out == b"input_pcm"
        assert engine_broken.get_last_rvc_result().rvc_applied is False

    @pytest.mark.anyio
    async def test_rvc_7_output_audio_integrity(self):
        """
        RVC-7: Output audio conforms to 24 kHz, 16-bit mono linear PCM specification.
        """
        config = VoiceEngineConfig(
            base_voice="ja-JP-NanamiNeural",
            active_rvc_model="VaresaGIJP",
        )
        engine = VoiceEngine(config)
        audio_bytes = await engine.synthesize_speech("テスト音声です。")
        assert len(audio_bytes) > 0

        with wave.open(io.BytesIO(audio_bytes), "rb") as wf:
            assert wf.getnchannels() == 1
            assert wf.getsampwidth() == 2
            assert wf.getframerate() == 24000
            frames = wf.readframes(wf.getnframes())
            pcm = np.frombuffer(frames, dtype=np.int16)

        assert len(pcm) > 0
        assert not np.any(np.isnan(pcm))
        # Max amplitude within standard 16-bit range
        assert np.max(np.abs(pcm)) > 500

    def test_rvc_8_canonical_storage_isolation(self):
        """
        RVC-8: Verify that running RVC inference did not alter any canonical storage files.
        """
        assert PROFILE_PATH.exists()
        current_profile_sha = hashlib.sha256(PROFILE_PATH.read_bytes()).hexdigest()
        assert current_profile_sha == BASELINE_PROFILE_SHA, (
            f"Canonical storage violation: {PROFILE_PATH} modified! Expected {BASELINE_PROFILE_SHA}, got {current_profile_sha}"
        )

        assert CHAT_HISTORY_PATH.exists()
        current_chat_sha = hashlib.sha256(CHAT_HISTORY_PATH.read_bytes()).hexdigest()
        assert current_chat_sha == BASELINE_CHAT_SHA, (
            f"Canonical storage violation: {CHAT_HISTORY_PATH} modified! Expected {BASELINE_CHAT_SHA}, got {current_chat_sha}"
        )
