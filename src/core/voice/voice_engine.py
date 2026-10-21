"""
Voice Engine — Direct RVC & Neural Voice Synthesis.

Generates character voice audio for Lucia with support for direct RVC
(Retrieval-based Voice Conversion) .pth and .index models from models/voice/rvc/.
"""

from __future__ import annotations

import asyncio
import io
import logging
import os
import threading
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Dict, List, Optional

import edge_tts

logger = logging.getLogger(__name__)

_DEFAULT_VOICE = "ja-JP-NanamiNeural"


@dataclass
class RVCModelInfo:
    """Metadata for a discovered RVC voice model."""

    name: str
    pth_path: str
    index_path: Optional[str] = None


@dataclass
class VoiceEngineConfig:
    """
    Configuration for VoiceEngine.

    Parameters
    ----------
    base_voice : str
        Default base neural voice (e.g. 'en-US-AnaNeural' or 'en-US-JennyNeural').
    active_rvc_model : str
        Name of the active RVC model folder in models/voice/rvc/ (or 'default').
    models_dir : str
        Path to RVC voice models directory. Default: 'models/voice/rvc'.
    pitch_shift : int
        Pitch shift in semitones. Default: 0.
    speech_rate : str
        Relative speech rate string (e.g. '+0%', '+5%'). Default: '+0%'.
    speech_volume : str
        Relative speech volume string (e.g. '+0%'). Default: '+0%'.
    """

    base_voice: str = _DEFAULT_VOICE
    active_rvc_model: str = "default"
    models_dir: str = "models/voice/rvc"
    pitch_shift: int = 0
    speech_rate: str = "+0%"
    speech_volume: str = "+0%"
    index_rate: float = 0.25
    device: Optional[str] = None  # None: auto-detect (CUDA if available, else CPU fallback)

    def __post_init__(self) -> None:
        # Restore canonical Phase 24 VaresaGIJP RVC model if present in models_dir
        if self.active_rvc_model == "default":
            canonical_dir = Path(self.models_dir) / "VaresaGIJP"
            if canonical_dir.is_dir():
                self.active_rvc_model = "VaresaGIJP"


class VoiceEngine:
    """
    High-performance, low-resource voice synthesis engine.
    """

    def __init__(self, config: Optional[VoiceEngineConfig] = None) -> None:
        if config is None:
            config = VoiceEngineConfig()
        self._config = config
        self._models_dir = Path(config.models_dir)
        self._models_dir.mkdir(parents=True, exist_ok=True)

        self._available_models: Dict[str, RVCModelInfo] = {}
        self._cache: Dict[str, bytes] = {}
        self._rvc_result_cache: Dict[str, Optional[Any]] = {}
        self._pipeline: Optional[Any] = None
        self._pipeline_lock = threading.Lock()
        self._last_rvc_result: Optional[Any] = None
        self._scan_rvc_models()

    @property
    def rvc_device(self) -> Optional[str]:
        """Return the active inference device of the underlying RVC pipeline, or None if uninitialized."""
        return str(self._pipeline.device) if self._pipeline is not None else None

    def _scan_rvc_models(self) -> None:
        """
        Scan models/voice/rvc/ directory for .pth and .index model files.
        """
        self._available_models.clear()
        if not self._models_dir.exists():
            return

        for entry in self._models_dir.iterdir():
            if entry.is_dir():
                model_name = entry.name
                pth_files = list(entry.glob("*.pth"))
                if pth_files:
                    pth_path = str(pth_files[0])
                    index_files = list(entry.glob("*.index"))
                    index_path = str(index_files[0]) if index_files else None
                    self._available_models[model_name] = RVCModelInfo(
                        name=model_name,
                        pth_path=pth_path,
                        index_path=index_path,
                    )

        logger.info(
            "VoiceEngine: Discovered %d RVC models in %s",
            len(self._available_models),
            self._models_dir,
        )

    def get_available_models(self) -> List[Dict[str, Any]]:
        """
        Return list of discovered RVC models with their metadata.
        """
        self._scan_rvc_models()
        models = [
            {
                "name": "default",
                "is_active": self._config.active_rvc_model == "default",
                "has_index": False,
                "description": f"Lucia Base Voice ({self._config.base_voice})",
            }
        ]
        for name, info in self._available_models.items():
            models.append(
                {
                    "name": name,
                    "is_active": self._config.active_rvc_model == name,
                    "has_index": info.index_path is not None,
                    "description": f"RVC Model ({name})",
                    "pth_path": info.pth_path,
                }
            )
        return models

    def set_active_model(self, model_name: str) -> bool:
        """
        Set the active RVC model. Returns True if successfully set.
        Preloads the model checkpoint if the pipeline is already warmed up.
        """
        if model_name == "default" or model_name in self._available_models:
            self._config.active_rvc_model = model_name
            logger.info("VoiceEngine: Active model set to %s", model_name)
            if self._pipeline is not None and model_name in self._available_models:
                info = self._available_models[model_name]
                try:
                    self._pipeline.load_model(info.pth_path, info.index_path)
                except Exception as e:
                    logger.warning("VoiceEngine: Preloading active model %s failed: %s", model_name, e)
            return True
        logger.warning("VoiceEngine: Model %s not found in %s", model_name, self._models_dir)
        return False

    def _ensure_pipeline(self) -> Optional[Any]:
        """
        Lazily initialize or return the RVCPipeline instance.
        """
        if self._pipeline is not None:
            return self._pipeline

        with self._pipeline_lock:
            if self._pipeline is not None:
                return self._pipeline

            try:
                from src.core.voice.rvc_pipeline import RVCPipeline
            except (ImportError, ModuleNotFoundError) as env_err:
                logger.warning("VoiceEngine: RVC pipeline unavailable due to missing dependencies: %s", env_err)
                return None

            import torch
            req_device = self._config.device
            if req_device is None:
                target_device = "cuda:0" if torch.cuda.is_available() else "cpu"
            else:
                target_device = req_device if (not req_device.startswith("cuda") or torch.cuda.is_available()) else "cpu"

            try:
                self._pipeline = RVCPipeline(device=target_device)
                logger.info("VoiceEngine: RVCPipeline initialized with active device: %s", self._pipeline.device)
                return self._pipeline
            except (ImportError, ModuleNotFoundError) as env_err:
                logger.warning("VoiceEngine: RVCPipeline initialization limited by dependencies: %s", env_err)
                return None
            except Exception as init_err:
                if target_device != "cpu":
                    logger.warning(
                        "VoiceEngine: Failed to initialize RVCPipeline on %s (%s). Attempting CPU fallback...",
                        target_device,
                        init_err,
                    )
                    try:
                        self._pipeline = RVCPipeline(device="cpu")
                        logger.info("VoiceEngine: RVCPipeline initialized on CPU fallback")
                        return self._pipeline
                    except Exception as cpu_err:
                        logger.error("VoiceEngine: CPU fallback also failed: %s", cpu_err, exc_info=True)
                        return None
                else:
                    logger.error("VoiceEngine: Failed to initialize RVCPipeline on CPU: %s", init_err, exc_info=True)
                    return None

    def warmup_rvc(self) -> bool:
        """
        Pre-initialize RVCPipeline, load active model checkpoint and HuBERT feature extractor.
        Ensures RVC is connected and warm at startup rather than lazily on the first utterance.
        """
        model_name = self._config.active_rvc_model
        if model_name == "default":
            logger.info("VoiceEngine: Active model is 'default' (no RVC conversion needed)")
            return False

        model_info = self._available_models.get(model_name)
        if model_info is None or not Path(model_info.pth_path).exists():
            logger.info("VoiceEngine: No local RVC model checkpoint to warm up (%s)", model_name)
            return False

        pipeline = self._ensure_pipeline()
        if pipeline is None:
            logger.warning("VoiceEngine: RVC warmup skipped because pipeline could not be initialized")
            return False

        with self._pipeline_lock:
            try:
                pipeline.load_model(model_info.pth_path, model_info.index_path)
                pipeline._get_or_load_hubert()
                logger.info("VoiceEngine: RVC pipeline warmed up and connected successfully for %s", model_info.name)
                return True
            except Exception as exc:
                logger.warning("VoiceEngine: RVC warmup encountered non-fatal error: %s", exc)
                return False


    async def synthesize_speech(
        self,
        text: str,
        *,
        language: str = "ja",
        rate: Optional[str] = None,
        volume: Optional[str] = None,
        pitch: Optional[str] = None,
        pitch_hz: Optional[float] = None,
        closeness: Optional[float] = None,
        focal_words: Optional[List[str]] = None,
    ) -> bytes:
        """
        Synthesize speech from text asynchronously with adaptive prosody support (ADR-032).

        Parameters
        ----------
        text : str
            Text string to speak.
        language : str
            Explicit voice language metadata (always 'ja' for vocal actuation).
        rate : Optional[str]
            Override speech rate (clamped to [-20%, +20%]).
        volume : Optional[str]
            Override speech volume (clamped to [-20%, +20%]).
        pitch : Optional[str]
            Override speech pitch string for Edge-TTS.
        pitch_hz : Optional[float]
            Limbic affect pitch shift in Hz in [-30.0, +30.0].
        closeness : Optional[float]
            Relational closeness in [0.0, 1.0] (+1.50 semitones max).
        focal_words : Optional[List[str]]
            List of words to receive dynamic Hanning focal accentuation.

        Returns
        -------
        bytes
            Audio stream bytes (MP3/WAV format).
        """
        import re
        import numpy as np
        from src.core.voice.boundary import extract_boundaries, compute_f0_contour
        from src.core.voice.rvc_pipeline import decode_audio_to_16k

        clean_text = text.strip()
        if not clean_text:
            return b""

        # Sanitize text: strip any stray XML/SSML tags to avoid NoAudioReceived
        clean_text = re.sub(r"<[^>]+>", "", clean_text).strip()
        if not clean_text:
            return b""

        # Clamp speech rate to [-20%, +20%]
        raw_rate = rate or self._config.speech_rate
        try:
            rate_num = float(raw_rate.replace("%", "").replace("+", "").strip())
            speech_rate = f"{int(np.clip(rate_num, -20.0, 20.0)):+d}%"
        except (ValueError, TypeError):
            speech_rate = "+0%"

        # Clamp speech volume to [-20%, +20%]
        raw_vol = volume or self._config.speech_volume
        try:
            vol_num = float(raw_vol.replace("%", "").replace("+", "").strip())
            speech_volume = f"{int(np.clip(vol_num, -20.0, 20.0)):+d}%"
        except (ValueError, TypeError):
            speech_volume = "+0%"

        # Determine whether RVC conversion will be applied
        is_rvc_active = (
            self._config.active_rvc_model != "default"
            and self._config.active_rvc_model in self._available_models
        )

        # Baseline pitch in Edge-TTS:
        # If pitch is explicitly passed, respect it.
        # Otherwise:
        #   - When RVC is active: use +60Hz to provide a bright acoustic base below saturation ceiling (ADR-032).
        #   - When RVC is bypassed / inactive: do NOT use +60Hz (use +0Hz) to prevent chipmunk output.
        if pitch is not None:
            speech_pitch = pitch
        elif is_rvc_active:
            speech_pitch = "+60Hz"
        else:
            speech_pitch = "+0Hz"

        # Determine language telemetry support: vi-* rejects WordBoundary with NoAudioReceived
        is_vietnamese = self._config.base_voice.lower().startswith("vi-") or self._config.base_voice.lower().startswith("vi_")
        boundary_arg = "SentenceBoundary" if is_vietnamese else "WordBoundary"

        cache_key = f"{clean_text.lower()}|{language}|{self._config.active_rvc_model}|{speech_rate}|{speech_volume}|{speech_pitch}|{pitch_hz}|{closeness}"
        if cache_key in self._cache:
            self._last_rvc_result = self._rvc_result_cache.get(cache_key)
            return self._cache[cache_key]

        communicate = edge_tts.Communicate(
            clean_text,
            voice=self._config.base_voice,
            rate=speech_rate,
            volume=speech_volume,
            pitch=speech_pitch,
            boundary=boundary_arg,
        )

        audio_buffer = io.BytesIO()
        telemetry_events: List[Dict[str, Any]] = []
        async for chunk in communicate.stream():
            if chunk["type"] == "audio":
                audio_buffer.write(chunk["data"])
            elif chunk["type"] in ("WordBoundary", "SentenceBoundary"):
                telemetry_events.append(chunk)

        raw_audio = audio_buffer.getvalue()
        if not raw_audio:
            return b""

        # If an active RVC model is selected and available, apply voice conversion
        if (
            self._config.active_rvc_model != "default"
            and self._config.active_rvc_model in self._available_models
        ):
            model_info = self._available_models[self._config.active_rvc_model]

            # Compute canonical semitone base shift (ADR-032.1 & ADR-032.4)
            if pitch_hz is not None or closeness is not None:
                p_hz = float(np.clip(pitch_hz or 0.0, -30.0, 30.0))
                c = float(np.clip(closeness or 0.0, 0.0, 1.0))
                s_base = float(np.clip(12.0 * np.log2(1.0 + p_hz / 250.0) + 1.50 * c, -2.0, 4.0))
            else:
                s_base = float(self._config.pitch_shift)

            def _do_rvc_transform() -> bytes:
                # Extract boundaries and build continuous F0 contour
                try:
                    audio_16k = decode_audio_to_16k(raw_audio)
                    p_len = max(1, len(audio_16k) // 160)
                    segments = extract_boundaries(
                        clean_text,
                        self._config.base_voice,
                        telemetry_events=telemetry_events,
                        audio_16k=audio_16k,
                        focal_words=focal_words,
                    )
                    f0_contour = compute_f0_contour(p_len, s_base, segments)
                except Exception as b_err:
                    logger.warning("VoiceEngine: Boundary extraction failed (%s), falling back to static pitch", b_err)
                    f0_contour = None

                return self._apply_rvc_conversion(
                    raw_audio,
                    model_info,
                    pitch_shift=s_base,
                    f0_contour=f0_contour,
                )

            raw_audio = await asyncio.to_thread(_do_rvc_transform)
        else:
            self._last_rvc_result = None

        # Cache short frequently-spoken phrases (under 200 chars)
        if len(clean_text) <= 200 and len(raw_audio) > 0:
            if len(self._cache) > 100:
                oldest_key = next(iter(self._cache))
                self._cache.pop(oldest_key, None)
                self._rvc_result_cache.pop(oldest_key, None)
            self._cache[cache_key] = raw_audio
            self._rvc_result_cache[cache_key] = self._last_rvc_result

        return raw_audio

    def get_last_rvc_result(self) -> Optional[Any]:
        """Return the result of the most recent RVC conversion attempt, if any."""
        return self._last_rvc_result

    def _apply_rvc_conversion(
        self,
        base_audio: bytes,
        model_info: RVCModelInfo,
        pitch_shift: float = 0.0,
        f0_contour: Optional[Any] = None,
    ) -> bytes:
        """
        Pass base audio through authentic RVC neural network weights.
        Returns converted audio bytes if successful, or base_audio on failure/limitation.
        """
        try:
            from src.core.voice.rvc_pipeline import RVCConversionResult
        except (ImportError, ModuleNotFoundError) as env_err:
            logger.warning("VoiceEngine: RVC pipeline unavailable due to missing dependencies: %s", env_err)
            self._last_rvc_result = None
            return base_audio

        pipeline = self._ensure_pipeline()
        if pipeline is None:
            self._last_rvc_result = RVCConversionResult(
                audio_bytes=base_audio,
                rvc_applied=False,
                execution_status="environment_limited",
                model_name=model_info.name,
                sample_rate=24000,
                duration_ms=0.0,
                error_message="RVC pipeline unavailable",
                device="none",
            )
            return base_audio


        logger.info(
            "VoiceEngine: Applying RVC conversion with model=%s (pth=%s, pitch_shift=%.2f st)",
            model_info.name,
            model_info.pth_path,
            pitch_shift,
        )

        try:
            with self._pipeline_lock:
                result = self._pipeline.convert(
                    base_audio=base_audio,
                    pth_path=model_info.pth_path,
                    index_path=model_info.index_path,
                    model_name=model_info.name,
                    index_rate=self._config.index_rate,
                    pitch_shift_semitones=pitch_shift,
                    f0_contour=f0_contour,
                )
            self._last_rvc_result = result
            if result.rvc_applied and result.execution_status == "success":
                logger.info("VoiceEngine: RVC conversion succeeded for %s (%d bytes)", model_info.name, len(result.audio_bytes))
                return result.audio_bytes
            elif result.execution_status == "environment_limited":
                logger.warning("VoiceEngine: RVC conversion limited by environment: %s", result.error_message)
                return base_audio
            else:
                logger.error("VoiceEngine: RVC conversion failed: %s", result.error_message)
                return base_audio
        except (ImportError, ModuleNotFoundError) as env_err:
            logger.warning("VoiceEngine: RVC conversion limited by dependencies: %s", env_err)
            self._last_rvc_result = RVCConversionResult(
                audio_bytes=base_audio,
                rvc_applied=False,
                execution_status="environment_limited",
                model_name=model_info.name,
                sample_rate=24000,
                duration_ms=0.0,
                error_message=str(env_err),
            )
            return base_audio
        except Exception as exc:
            logger.error("VoiceEngine: Unexpected exception in RVC conversion: %s", exc, exc_info=True)
            self._last_rvc_result = RVCConversionResult(
                audio_bytes=base_audio,
                rvc_applied=False,
                execution_status="failed",
                model_name=model_info.name,
                sample_rate=24000,
                duration_ms=0.0,
                error_message=str(exc),
            )
            return base_audio
