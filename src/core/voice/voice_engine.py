"""
Voice Engine — Direct RVC & Neural Voice Synthesis.

Generates character voice audio for Lucia with support for direct RVC
(Retrieval-based Voice Conversion) .pth and .index models from models/voice/rvc/.
"""

from __future__ import annotations

import io
import logging
import os
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
        self._last_rvc_result: Optional[Any] = None
        self._scan_rvc_models()

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
        """
        if model_name == "default" or model_name in self._available_models:
            self._config.active_rvc_model = model_name
            logger.info("VoiceEngine: Active model set to %s", model_name)
            return True
        logger.warning("VoiceEngine: Model %s not found in %s", model_name, self._models_dir)
        return False

    async def synthesize_speech(
        self,
        text: str,
        *,
        rate: Optional[str] = None,
        volume: Optional[str] = None,
        pitch: Optional[str] = None,
    ) -> bytes:
        """
        Synthesize speech from text asynchronously.

        Parameters
        ----------
        text : str
            Text string to speak.
        rate : Optional[str]
            Override speech rate (e.g. '+5%').
        volume : Optional[str]
            Override speech volume (e.g. '+0%').
        pitch : Optional[str]
            Override speech pitch (e.g. '+0Hz' or '+2Hz').

        Returns
        -------
        bytes
            Audio stream bytes (MP3/WAV format).
        """
        clean_text = text.strip()
        if not clean_text:
            return b""

        speech_rate = rate or self._config.speech_rate
        speech_volume = volume or self._config.speech_volume
        pitch_str = pitch or (f"{self._config.pitch_shift:+d}Hz" if self._config.pitch_shift != 0 else "+0Hz")

        cache_key = f"{clean_text.lower()}|{self._config.active_rvc_model}|{speech_rate}|{speech_volume}|{pitch_str}"
        if cache_key in self._cache:
            self._last_rvc_result = self._rvc_result_cache.get(cache_key)
            return self._cache[cache_key]

        communicate = edge_tts.Communicate(
            clean_text,
            voice=self._config.base_voice,
            rate=speech_rate,
            volume=speech_volume,
            pitch=pitch_str,
        )

        audio_buffer = io.BytesIO()
        async for chunk in communicate.stream():
            if chunk["type"] == "audio":
                audio_buffer.write(chunk["data"])

        raw_audio = audio_buffer.getvalue()

        # If an active RVC model is selected and available, apply voice conversion
        if (
            self._config.active_rvc_model != "default"
            and self._config.active_rvc_model in self._available_models
        ):
            model_info = self._available_models[self._config.active_rvc_model]
            raw_audio = self._apply_rvc_conversion(raw_audio, model_info)
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

    def _apply_rvc_conversion(self, base_audio: bytes, model_info: RVCModelInfo) -> bytes:
        """
        Pass base audio through authentic RVC neural network weights.
        Returns converted audio bytes if successful, or base_audio on failure/limitation.
        """
        try:
            from src.core.voice.rvc_pipeline import RVCPipeline, RVCConversionResult
        except (ImportError, ModuleNotFoundError) as env_err:
            logger.warning("VoiceEngine: RVC pipeline unavailable due to missing dependencies: %s", env_err)
            self._last_rvc_result = None
            return base_audio

        if self._pipeline is None:
            try:
                self._pipeline = RVCPipeline(device="cpu")
            except (ImportError, ModuleNotFoundError) as env_err:
                logger.warning("VoiceEngine: RVCPipeline initialization limited by dependencies: %s", env_err)
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
            except Exception as init_err:
                logger.error("VoiceEngine: Failed to initialize RVCPipeline: %s", init_err, exc_info=True)
                self._last_rvc_result = RVCConversionResult(
                    audio_bytes=base_audio,
                    rvc_applied=False,
                    execution_status="failed",
                    model_name=model_info.name,
                    sample_rate=24000,
                    duration_ms=0.0,
                    error_message=str(init_err),
                )
                return base_audio

        logger.info(
            "VoiceEngine: Applying RVC conversion with model=%s (pth=%s)",
            model_info.name,
            model_info.pth_path,
        )

        try:
            result = self._pipeline.convert(
                base_audio=base_audio,
                pth_path=model_info.pth_path,
                index_path=model_info.index_path,
                model_name=model_info.name,
                index_rate=self._config.index_rate,
                pitch_shift_semitones=self._config.pitch_shift,
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
