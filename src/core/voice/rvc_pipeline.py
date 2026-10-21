"""
src/core/voice/rvc_pipeline.py

Authentic on-device RVC v2 (Retrieval-based Voice Conversion) neural inference pipeline.
Executes pure-PyTorch inference for VITS / NSF-HiFiGAN architectures without legacy fairseq dependencies.

Pipeline Stages:
1. Decode base audio (WAV/MP3) to 16 kHz mono float32.
2. Pitch estimation via Parselmouth AC (with unvoiced interpolation & coarse mel bins 1..255).
3. ContentVec/HuBERT 768-D feature extraction at 50 Hz.
4. Faiss index k=8 retrieval with inverse squared distance weighting.
5. 2x linear temporal interpolation to 100 Hz.
6. SynthesizerTrn generator inference (SineGen NSF harmonic excitation + MRF ResBlock synthesis at 40 kHz).
7. Headroom-safe normalization and polyphase anti-aliasing resampling to 24 kHz 16-bit mono PCM WAV.
"""

from __future__ import annotations

import io
import logging
import math
import os
import wave
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

import av
import numpy as np
import torch
import torch.nn as nn
import torch.nn.functional as F
from scipy import signal

from src.core.voice.rvc_modules.models import SynthesizerTrnMs768NSFsid

logger = logging.getLogger("RVCPipeline")

# Global singleton cache for models to avoid reload latency
_PIPELINE_CACHE: Dict[str, Any] = {}


@dataclass
class RVCConversionResult:
    """Structured result of an RVC conversion attempt."""
    audio_bytes: bytes
    rvc_applied: bool
    execution_status: str  # "success" | "environment_limited" | "failed"
    model_name: str
    sample_rate: int
    duration_ms: float
    error_message: Optional[str] = None
    device: str = "cpu"


# ---------------------------------------------------------------------------
# 1. RVC v2 Neural Architecture (PyTorch Native Wrapper)
# ---------------------------------------------------------------------------

class SynthesizerTrn(SynthesizerTrnMs768NSFsid):
    """
    RVC v2 Generative Architecture wrapper.
    Matches all 457 weight tensors in production RVC checkpoints (enc_p, flow, dec, emb_g)
    with strict=True compatibility (training-only enc_q excluded).
    Supports both 4-argument (phone, pitch, pitchf, sid) and 5-argument (phone, lengths, pitch, pitchf, sid) infer signatures.
    """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, is_half=False, **kwargs)
        # Remove training-only posterior encoder so strict=True loading matches 457 inference weights
        if hasattr(self, "enc_q"):
            del self.enc_q

    def infer(self, phone: torch.Tensor, *args, **kwargs) -> Any:
        """
        Execute vocoder inference with flexible signature support:
        - 4 arguments: (phone, pitch, pitchf, sid) -> automatically builds phone_lengths
        - 5 arguments: (phone, phone_lengths, pitch, pitchf, sid) -> standard official RVC call
        """
        if len(args) == 3:
            pitch, pitchf, sid = args
            lengths = torch.tensor([phone.shape[1]], device=phone.device).long()
            return super().infer(phone, lengths, pitch, pitchf, sid, **kwargs)
        return super().infer(phone, *args, **kwargs)


# ---------------------------------------------------------------------------
# 2. Audio Processing & Feature Extraction Utilities
# ---------------------------------------------------------------------------

def decode_audio_to_16k(audio_bytes: bytes) -> np.ndarray:
    """Decode input audio bytes (MP3/WAV) to 16 kHz mono float32 numpy array."""
    container = av.open(io.BytesIO(audio_bytes))
    resampler = av.AudioResampler(format='flt', layout='mono', rate=16000)
    audio_frames = []
    for frame in container.decode(audio=0):
        for resampled in resampler.resample(frame):
            audio_frames.append(resampled.to_ndarray())
    container.close()
    if not audio_frames:
        return np.zeros(0, dtype=np.float32)
    audio_16k = np.concatenate(audio_frames, axis=1)[0]
    return audio_16k


def estimate_f0_pyin(
    audio_16k: np.ndarray,
    hop_length: int = 160,
    f0_min: float = 50.0,
    f0_max: float = 1100.0,
) -> Tuple[np.ndarray, np.ndarray]:
    """
    Extract continuous F0 in Hz and coarse pitch bins [1..255] matching RVC training standards.
    Uses Parselmouth autocorrelation (official RVC 'pm' method) with linear interpolation across
    unvoiced regions and logarithmic mel-bin quantization.
    Falls back gracefully to normalized autocorrelation if Parselmouth is unavailable.
    """
    total_samples = len(audio_16k)
    p_len = max(1, total_samples // hop_length)

    f0_mel_min = 1127.0 * np.log(1.0 + f0_min / 700.0)
    f0_mel_max = 1127.0 * np.log(1.0 + f0_max / 700.0)

    f0 = None
    try:
        import parselmouth
        time_step = hop_length / 16000.0
        snd = parselmouth.Sound(audio_16k, 16000)
        pitch_obj = snd.to_pitch_ac(
            time_step=time_step,
            voicing_threshold=0.6,
            pitch_floor=f0_min,
            pitch_ceiling=f0_max,
        )
        f0_raw = pitch_obj.selected_array["frequency"]
        pad_size = (p_len - len(f0_raw) + 1) // 2
        if pad_size > 0 or p_len - len(f0_raw) - pad_size > 0:
            f0_raw = np.pad(f0_raw, [[pad_size, max(0, p_len - len(f0_raw) - pad_size)]], mode="constant")
        f0 = f0_raw[:p_len].astype(np.float32)
    except Exception as exc:
        logger.warning("RVCPipeline: Parselmouth unavailable (%s), using normalized autocorrelation fallback", exc)
        f0 = np.zeros(p_len, dtype=np.float32)
        min_period = int(16000.0 / f0_max)
        max_period = int(16000.0 / f0_min)
        frame_len = 2 * max_period
        for i in range(p_len):
            start = i * hop_length
            end = start + frame_len
            frame = audio_16k[start:end] if end <= total_samples else np.pad(audio_16k[start:], (0, end - total_samples))
            if np.sum(frame ** 2) < 1e-4:
                continue
            corr = np.correlate(frame, frame, mode='full')
            corr = corr[len(corr) // 2:]
            peak_range = corr[min_period:max_period]
            if len(peak_range) > 0:
                best_lag = min_period + np.argmax(peak_range)
                if corr[best_lag] > 0.45 * corr[0]:
                    f0[i] = 16000.0 / float(best_lag)

    # Official RVC unvoiced interpolation: linearly interpolate across unvoiced segments
    uv = (f0 == 0)
    if np.all(uv):
        f0 = np.ones_like(f0) * 200.0
    elif np.any(uv):
        f0[uv] = np.interp(np.where(uv)[0], np.where(~uv)[0], f0[~uv])

    f0_continuous = f0.copy()

    # Coarse pitch quantization to 1..255 bins
    f0_mel = 1127.0 * np.log(1.0 + f0 / 700.0)
    f0_mel[f0_mel > 0] = (f0_mel[f0_mel > 0] - f0_mel_min) * 254.0 / (f0_mel_max - f0_mel_min) + 1.0
    f0_mel[f0_mel <= 1.0] = 1.0
    f0_mel[f0_mel > 255.0] = 255.0
    f0_coarse = np.rint(f0_mel).astype(np.int64)

    return f0_continuous, f0_coarse


# ---------------------------------------------------------------------------
# 3. High-Level RVC Inference Pipeline
# ---------------------------------------------------------------------------

class RVCPipeline:
    """
    Self-contained RVC v2 inference manager.
    Loads models on-demand, executes full speech feature conversion, and resamples to 24 kHz WAV.
    """

    def __init__(self, device: Optional[str] = None) -> None:
        if device is None:
            if torch.cuda.is_available():
                chosen_device = "cuda:0"
                logger.info(
                    "RVCPipeline: CUDA detected (%s). Selected inference device: %s",
                    torch.cuda.get_device_name(0),
                    chosen_device,
                )
            else:
                chosen_device = "cpu"
                logger.info("RVCPipeline: CUDA not available. Selected inference device: cpu (fallback)")
        else:
            if device.startswith("cuda") and not torch.cuda.is_available():
                logger.warning(
                    "RVCPipeline: CUDA requested (%s) but not available. Falling back to cpu",
                    device,
                )
                chosen_device = "cpu"
            else:
                chosen_device = device
                if chosen_device.startswith("cuda"):
                    logger.info("RVCPipeline: Explicit CUDA device selected: %s", chosen_device)
                else:
                    logger.info("RVCPipeline: Explicit CPU device selected: %s", chosen_device)

        self.device = torch.device(chosen_device)
        self.active_net_g: Optional[SynthesizerTrn] = None
        self.active_index: Optional[Any] = None
        self.index_vectors: Optional[np.ndarray] = None
        self.active_hubert: Optional[Any] = None
        self.current_model_path: Optional[str] = None
        self.current_index_path: Optional[str] = None

    @property
    def device_str(self) -> str:
        """Return the device string representation."""
        return str(self.device)

    @property
    def is_cuda(self) -> bool:
        """Return True if running on a CUDA device."""
        return self.device.type == "cuda"

    def _get_or_load_hubert(self) -> Any:
        """Load ContentVec / HuBERT feature extractor from local HuggingFace cache."""
        if self.active_hubert is not None:
            return self.active_hubert

        try:
            try:
                from transformers.models.hubert.modeling_hubert import HubertModel
            except (ImportError, ModuleNotFoundError):
                from transformers import HubertModel

            logger.info("RVCPipeline: Loading ContentVec / HuBERT feature extractor on %s...", self.device)
            try:
                hubert = HubertModel.from_pretrained(
                    'lj1995/VoiceConversionWebUI',
                    subfolder='hubert_base',
                    local_files_only=True,
                )
            except Exception:
                hubert = HubertModel.from_pretrained(
                    'lj1995/VoiceConversionWebUI',
                    subfolder='hubert_base',
                )
            hubert = hubert.float().to(self.device)
            hubert.eval()
            self.active_hubert = hubert
            hubert_device = next(hubert.parameters()).device
            logger.info("RVCPipeline: HuBERT device: %s", hubert_device)
            return hubert
        except Exception as exc:
            logger.error("RVCPipeline: Failed to load HubertModel: %s", exc)
            raise

    def load_model(self, pth_path: str, index_path: Optional[str] = None) -> bool:
        """Load RVC checkpoint and optional Faiss index."""
        pth_file = Path(pth_path)
        if not pth_file.exists():
            logger.error("RVCPipeline: Checkpoint not found: %s", pth_path)
            return False

        try:
            logger.info("RVCPipeline: Loading RVC v2 checkpoint: %s (target device: %s)", pth_path, self.device)
            ckpt = torch.load(pth_path, map_location=self.device)
            cfg = ckpt['config']
            net_g = SynthesizerTrn(
                spec_channels=cfg[0], segment_size=cfg[1], inter_channels=cfg[2],
                hidden_channels=cfg[3], filter_channels=cfg[4], n_heads=cfg[5],
                n_layers=cfg[6], kernel_size=cfg[7], p_dropout=cfg[8],
                resblock=cfg[9], resblock_kernel_sizes=cfg[10],
                resblock_dilation_sizes=cfg[11], upsample_rates=cfg[12],
                upsample_initial_channel=cfg[13], upsample_kernel_sizes=cfg[14],
                spk_embed_dim=cfg[15], gin_channels=cfg[16], sr=cfg[17],
            )
            net_g.load_state_dict(ckpt['weight'], strict=True)
            net_g.remove_weight_norm()
            net_g.to(self.device).eval()
            self.active_net_g = net_g
            self.current_model_path = pth_path
            generator_device = next(net_g.parameters()).device
            logger.info("RVCPipeline: Generator device: %s", generator_device)
            logger.info("RVCPipeline: RVC device: %s", self.device)

            # Load Faiss index if provided and faiss is available
            if index_path and Path(index_path).exists():
                try:
                    import faiss
                    logger.info("RVCPipeline: Loading Faiss index: %s", index_path)
                    index = faiss.read_index(index_path)
                    self.active_index = index
                    self.index_vectors = index.reconstruct_n(0, index.ntotal)
                    self.current_index_path = index_path
                except Exception as exc:
                    logger.warning("RVCPipeline: Could not load index %s: %s", index_path, exc)
                    self.active_index = None
                    self.index_vectors = None
            else:
                self.active_index = None
                self.index_vectors = None

            return True
        except Exception as exc:
            logger.error("RVCPipeline: Failed to instantiate/load SynthesizerTrn from %s: %s", pth_path, exc)
            self.active_net_g = None
            raise

    def convert(
        self,
        base_audio: bytes,
        pth_path: str,
        index_path: Optional[str] = None,
        model_name: str = "VaresaGIJP",
        index_rate: float = 0.25,
        pitch_shift_semitones: float = 0.0,
        f0_contour: Optional[np.ndarray] = None,
    ) -> RVCConversionResult:
        """
        Execute full RVC voice conversion on input speech bytes.
        Supports both static pitch_shift_semitones and continuous dynamic f0_contour (ADR-032.2).
        """
        # 1. Validate environment & checkpoint existence
        if not Path(pth_path).exists():
            return RVCConversionResult(
                audio_bytes=base_audio,
                rvc_applied=False,
                execution_status="environment_limited",
                model_name=model_name,
                sample_rate=24000,
                duration_ms=0.0,
                error_message=f"Model checkpoint not found: {pth_path}",
                device=str(self.device),
            )

        try:
            # 2. Ensure model is loaded
            if self.active_net_g is None or self.current_model_path != pth_path:
                self.load_model(pth_path, index_path)

            hubert = self._get_or_load_hubert()

            # 3. Decode base audio to 16 kHz float32
            audio_16k = decode_audio_to_16k(base_audio)
            if len(audio_16k) == 0:
                return RVCConversionResult(
                    audio_bytes=base_audio,
                    rvc_applied=False,
                    execution_status="failed",
                    model_name=model_name,
                    sample_rate=24000,
                    duration_ms=0.0,
                    error_message="Input audio bytes contained zero readable frames",
                    device=str(self.device),
                )

            # 4. Extract continuous F0 and coarse pitch
            f0_hz, f0_coarse = estimate_f0_pyin(audio_16k, hop_length=160)
            p_len = len(f0_hz)

            if f0_contour is not None:
                # Dynamic F0 trajectory S(t) in semitones (ADR-032.2)
                contour = np.asarray(f0_contour, dtype=np.float32)
                if len(contour) != p_len:
                    contour = np.interp(
                        np.linspace(0, 1, p_len),
                        np.linspace(0, 1, len(contour)),
                        contour,
                    )
                # Hard safety clamp to [-12.0, +12.0] st
                semitone_curve = np.clip(contour, -12.0, 12.0)
                f0_hz = f0_hz * (2.0 ** (semitone_curve / 12.0))
            elif pitch_shift_semitones != 0:
                # Clamp static shift to [-12.0, +12.0] st
                shift_clamped = float(np.clip(pitch_shift_semitones, -12.0, 12.0))
                f0_hz = f0_hz * (2.0 ** (shift_clamped / 12.0))

            if f0_contour is not None or pitch_shift_semitones != 0:
                # Recompute coarse mel bins
                f0_mel_min = 1127.0 * np.log(1.0 + 50.0 / 700.0)
                f0_mel_max = 1127.0 * np.log(1.0 + 1100.0 / 700.0)
                f0_mel = 1127.0 * np.log(1.0 + f0_hz / 700.0)
                f0_mel[f0_mel > 0] = (f0_mel[f0_mel > 0] - f0_mel_min) * 254.0 / (f0_mel_max - f0_mel_min) + 1.0
                f0_mel[f0_mel <= 1.0] = 1.0
                f0_mel[f0_mel > 255.0] = 255.0
                f0_coarse = np.rint(f0_mel).astype(np.int64)

            # 5. Extract 768-D features via ContentVec/HuBERT at 50 Hz
            with torch.no_grad():
                input_tensor = torch.from_numpy(audio_16k).unsqueeze(0).to(self.device)
                feats_50hz = hubert(input_tensor).last_hidden_state  # [1, T_hubert, 768]

            # 6. Apply Faiss index retrieval on 50 Hz representation before interpolation
            if (
                self.active_index is not None
                and self.index_vectors is not None
                and index_rate > 0.0
            ):
                try:
                    npy_50hz = feats_50hz[0].cpu().numpy().astype(np.float32)
                    score, ix = self.active_index.search(npy_50hz, k=8)
                    weight = np.square(1.0 / (score + 1e-8))
                    weight /= weight.sum(axis=1, keepdims=True)
                    retrieved = np.sum(self.index_vectors[ix] * np.expand_dims(weight, axis=2), axis=1)
                    feats_blended = (1.0 - index_rate) * feats_50hz + index_rate * torch.from_numpy(retrieved).unsqueeze(0).to(self.device).float()
                except Exception as idx_err:
                    logger.warning("RVCPipeline: Index search skipped due to: %s", idx_err)
                    feats_blended = feats_50hz
            else:
                feats_blended = feats_50hz

            # 7. 2x Linear Temporal Interpolation (50 Hz -> 100 Hz) matching RVC v2 standard
            feats = F.interpolate(feats_blended.permute(0, 2, 1), scale_factor=2).permute(0, 2, 1)

            # 8. Align temporal lengths
            p_len = min(feats.shape[1], len(f0_hz))
            feats = feats[:, :p_len, :]
            pitch = torch.from_numpy(f0_coarse[:p_len]).unsqueeze(0).to(self.device).long()
            pitchf = torch.from_numpy(f0_hz[:p_len]).unsqueeze(0).to(self.device).float()
            p_len_t = torch.tensor([p_len], device=self.device).long()
            sid = torch.tensor([0], device=self.device).long()

            # 9. Neural Generator Inference (40 kHz synthesis)
            with torch.no_grad():
                out_wav_40k = self.active_net_g.infer(feats, p_len_t, pitch, pitchf, sid)[0]
                out_wav_np = out_wav_40k.squeeze().cpu().numpy()

            # 10. Headroom-safe normalization to 0.90 (-0.91 dBFS) before resampling to prevent sinc filter overshoot
            max_val = np.max(np.abs(out_wav_np))
            if max_val > 0:
                out_wav_np = out_wav_np / max_val * 0.90

            # 11. Resample 40 kHz -> 24 kHz using polyphase anti-aliasing filtering
            out_wav_24k = signal.resample_poly(out_wav_np, 3, 5).astype(np.float32)

            # 12. Guard against filter overshoot to guarantee zero hard clipping
            peak_24k = np.max(np.abs(out_wav_24k))
            if peak_24k > 0.95:
                out_wav_24k = out_wav_24k / peak_24k * 0.95

            # 13. Encode to 24 kHz mono 16-bit linear PCM WAV
            out_pcm_16 = (np.clip(out_wav_24k, -1.0, 1.0) * 32767.0).astype(np.int16)
            wav_buffer = io.BytesIO()
            with wave.open(wav_buffer, 'wb') as wf:
                wf.setnchannels(1)
                wf.setsampwidth(2)
                wf.setframerate(24000)
                wf.writeframes(out_pcm_16.tobytes())

            converted_bytes = wav_buffer.getvalue()
            duration_ms = float(len(out_pcm_16) / 24000.0 * 1000.0)

            # 14. VRAM Safety: Release transient intermediate activations if running on CUDA
            if self.device.type == "cuda":
                torch.cuda.empty_cache()

            return RVCConversionResult(
                audio_bytes=converted_bytes,
                rvc_applied=True,
                execution_status="success",
                model_name=model_name,
                sample_rate=24000,
                duration_ms=duration_ms,
                error_message=None,
                device=str(self.device),
            )

        except Exception as exc:
            logger.error("RVCPipeline: Neural voice conversion failed with exception: %s", exc, exc_info=True)
            if self.device.type == "cuda":
                torch.cuda.empty_cache()
            return RVCConversionResult(
                audio_bytes=base_audio,
                rvc_applied=False,
                execution_status="failed",
                model_name=model_name,
                sample_rate=24000,
                duration_ms=0.0,
                error_message=str(exc),
                device=str(self.device),
            )
