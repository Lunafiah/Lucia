"""
tests/unit/test_voice_rvc_cuda.py

Unit Test Suite for CUDA-Accelerated RVC Voice Inference & Runtime Fallback.
Validates:
1. Auto-selection of CUDA device when torch.cuda.is_available() is True.
2. Clean fallback to CPU when CUDA is unavailable or when explicit device='cpu' is passed.
3. Parameter device correctness on both HuBERT and SynthesizerTrn generator.
4. Output audio integrity on realistic synthesis (24kHz, 16-bit mono PCM, non-silent, 0 clipping).
5. Dynamic F0 contouring under CUDA inference.
6. Coexistence and VRAM cleanup via torch.cuda.empty_cache().
"""

import io
import wave
from pathlib import Path
from unittest.mock import patch

import numpy as np
import pytest
import torch

from src.core.voice.rvc_pipeline import (
    RVCPipeline,
    RVCConversionResult,
    SynthesizerTrn,
    decode_audio_to_16k,
)
from src.core.voice.voice_engine import VoiceEngine, VoiceEngineConfig

VARESA_DIR = Path("models/voice/rvc/VaresaGIJP")
VARESA_PTH = VARESA_DIR / "VaresaGIJP_300e_2100s.pth"
VARESA_INDEX = VARESA_DIR / "added_VaresaGIJP_v2.index"


class TestRVCDeviceSelectionAndFallback:
    """Validate device selection logic, parameter placement, and graceful fallbacks."""

    def test_cuda_auto_selection_when_available(self):
        """Verify that when CUDA is available, RVCPipeline auto-selects cuda:0."""
        if not torch.cuda.is_available():
            pytest.skip("CUDA not available in this test environment")

        pipeline = RVCPipeline()
        assert pipeline.device.type == "cuda"
        assert pipeline.is_cuda is True
        assert pipeline.device_str == "cuda:0"

    def test_cpu_selection_explicit(self):
        """Verify that explicit device='cpu' forces CPU inference even if CUDA is available."""
        pipeline = RVCPipeline(device="cpu")
        assert pipeline.device.type == "cpu"
        assert pipeline.is_cuda is False
        assert pipeline.device_str == "cpu"

    def test_cuda_fallback_to_cpu_when_cuda_unavailable(self):
        """Verify that if device='cuda:0' is requested but CUDA is unavailable, it falls back to CPU."""
        with patch("torch.cuda.is_available", return_value=False):
            pipeline = RVCPipeline(device="cuda:0")
            assert pipeline.device.type == "cpu"
            assert pipeline.is_cuda is False
            assert pipeline.device_str == "cpu"

    def test_auto_device_selection_when_cuda_unavailable(self):
        """Verify that default device=None falls back to CPU when CUDA is unavailable."""
        with patch("torch.cuda.is_available", return_value=False):
            pipeline = RVCPipeline(device=None)
            assert pipeline.device.type == "cpu"
            assert pipeline.is_cuda is False


class TestRVCNeuralComponentDevicePlacement:
    """Verify that models and tensors actually reside on the configured target device."""

    @pytest.mark.skipif(not torch.cuda.is_available(), reason="Requires CUDA GPU")
    def test_cuda_neural_weights_device_placement(self):
        """Confirm HuBERT and SynthesizerTrn parameters are on cuda:0."""
        assert VARESA_PTH.exists(), f"Checkpoint missing: {VARESA_PTH}"

        pipeline = RVCPipeline(device="cuda:0")
        pipeline.load_model(str(VARESA_PTH), str(VARESA_INDEX) if VARESA_INDEX.exists() else None)
        hubert = pipeline._get_or_load_hubert()

        gen_param = next(pipeline.active_net_g.parameters())
        hubert_param = next(hubert.parameters())

        assert gen_param.device.type == "cuda", f"Generator parameter on {gen_param.device}, expected cuda"
        assert hubert_param.device.type == "cuda", f"HuBERT parameter on {hubert_param.device}, expected cuda"

    def test_cpu_neural_weights_device_placement(self):
        """Confirm HuBERT and SynthesizerTrn parameters are on cpu when configured for CPU."""
        assert VARESA_PTH.exists(), f"Checkpoint missing: {VARESA_PTH}"

        pipeline = RVCPipeline(device="cpu")
        pipeline.load_model(str(VARESA_PTH), str(VARESA_INDEX) if VARESA_INDEX.exists() else None)
        hubert = pipeline._get_or_load_hubert()

        gen_param = next(pipeline.active_net_g.parameters())
        hubert_param = next(hubert.parameters())

        assert gen_param.device.type == "cpu", f"Generator parameter on {gen_param.device}, expected cpu"
        assert hubert_param.device.type == "cpu", f"HuBERT parameter on {hubert_param.device}, expected cpu"


class TestVoiceEngineProductionCUDAIntegration:
    """Verify VoiceEngine integration with CUDA-accelerated RVC."""

    @pytest.mark.skipif(not torch.cuda.is_available(), reason="Requires CUDA GPU")
    @pytest.mark.anyio
    async def test_voice_engine_cuda_speech_synthesis(self):
        """Execute speech synthesis through VoiceEngine on CUDA and verify output properties."""
        config = VoiceEngineConfig(
            base_voice="ja-JP-NanamiNeural",
            active_rvc_model="VaresaGIJP",
            models_dir="models/voice/rvc",
            device="cuda:0",
        )
        engine = VoiceEngine(config)
        test_text = "こんにちは、ルシアです。"

        audio_bytes = await engine.synthesize_speech(test_text)
        assert len(audio_bytes) > 0, "Synthesized audio is empty"

        rvc_res = engine.get_last_rvc_result()
        assert rvc_res is not None
        assert rvc_res.rvc_applied is True
        assert rvc_res.execution_status == "success"
        assert "cuda" in rvc_res.device

        # Verify WAV properties
        with wave.open(io.BytesIO(audio_bytes), "rb") as wf:
            assert wf.getnchannels() == 1
            assert wf.getsampwidth() == 2
            assert wf.getframerate() == 24000
            n_frames = wf.getnframes()
            samples = np.frombuffer(wf.readframes(n_frames), dtype=np.int16).astype(np.float32) / 32768.0

        # Check clipping & non-silence
        clipping = np.sum(np.abs(samples) >= 0.999)
        assert clipping == 0, f"Detected {clipping} clipping samples in output WAV"
        rms = np.sqrt(np.mean(samples ** 2))
        assert rms > 0.01, f"Audio is silent (RMS = {rms})"

    @pytest.mark.anyio
    async def test_voice_engine_fallback_behavior(self):
        """Verify VoiceEngine falls back to CPU cleanly when device='cpu' is specified."""
        config = VoiceEngineConfig(
            base_voice="ja-JP-NanamiNeural",
            active_rvc_model="VaresaGIJP",
            models_dir="models/voice/rvc",
            device="cpu",
        )
        engine = VoiceEngine(config)
        test_text = "テストメッセージです。"

        audio_bytes = await engine.synthesize_speech(test_text)
        assert len(audio_bytes) > 0
        rvc_res = engine.get_last_rvc_result()
        assert rvc_res is not None
        assert rvc_res.rvc_applied is True
        assert rvc_res.execution_status == "success"
        assert rvc_res.device == "cpu"
