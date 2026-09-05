"""
Speech-to-Text Engine (stt_engine.py)
Self-contained, offline audio transcription using faster-whisper.
Runs on CPU or CUDA without any external Google API or network dependency.
"""

from __future__ import annotations

import io
import logging
import os
import tempfile
from typing import Optional

from dataclasses import dataclass

logger = logging.getLogger(__name__)


@dataclass
class SpeechToTextConfig:
    model_size: str = "base"
    download_root: Optional[str] = None


class SpeechToTextEngine:
    """
    Manages audio transcription via faster-whisper with lazy initialization.
    """

    def __init__(
        self,
        config: Optional[SpeechToTextConfig] = None,
        model_size: str = "base",
        download_root: Optional[str] = None,
    ):
        if config is not None:
            self.model_size = config.model_size
            self.download_root = config.download_root or os.path.join("models", "voice", "whisper")
        else:
            self.model_size = model_size
            self.download_root = download_root or os.path.join("models", "voice", "whisper")
        self._model = None

    def _ensure_model(self):
        if self._model is not None:
            return self._model

        try:
            from faster_whisper import WhisperModel
            import torch

            device = "cuda" if torch.cuda.is_available() else "cpu"
            compute_type = "float16" if device == "cuda" else "int8"

            os.makedirs(self.download_root, exist_ok=True)
            logger.info(
                "Loading faster-whisper model '%s' on device=%s, compute_type=%s...",
                self.model_size,
                device,
                compute_type,
            )
            self._model = WhisperModel(
                self.model_size,
                device=device,
                compute_type=compute_type,
                download_root=self.download_root,
            )
            logger.info("faster-whisper model loaded successfully.")
            return self._model
        except Exception as exc:
            logger.error("Failed to load faster-whisper model: %s", exc)
            raise

    def transcribe_bytes(
        self,
        audio_bytes: bytes,
        language: Optional[str] = None,
        beam_size: int = 5,
    ) -> str:
        """
        Transcribe raw audio bytes (wav, webm, mp3, ogg, etc.) to text.
        """
        if not audio_bytes or len(audio_bytes) < 100:
            return ""

        model = self._ensure_model()

        # Write to temporary file for robust ffmpeg/av decoding by faster-whisper
        with tempfile.NamedTemporaryFile(suffix=".webm", delete=False) as tmp:
            tmp.write(audio_bytes)
            tmp_path = tmp.name

        try:
            segments, info = model.transcribe(
                tmp_path,
                beam_size=beam_size,
                language=language,
                vad_filter=True,
                vad_parameters=dict(min_silence_duration_ms=500),
            )
            texts = [seg.text.strip() for seg in segments if seg.text.strip()]
            full_text = " ".join(texts)
            logger.info(
                "Transcription complete (detected lang=%s, prob=%.2f): '%s'",
                getattr(info, "language", "unknown"),
                getattr(info, "language_probability", 0.0),
                full_text,
            )
            return full_text
        except Exception as exc:
            logger.error("Transcription failed: %s", exc)
            return ""
        finally:
            if os.path.exists(tmp_path):
                try:
                    os.remove(tmp_path)
                except Exception:
                    pass


# Singleton instance
_stt_engine: Optional[SpeechToTextEngine] = None


def get_stt_engine() -> SpeechToTextEngine:
    global _stt_engine
    if _stt_engine is None:
        _stt_engine = SpeechToTextEngine(model_size="base")
    return _stt_engine
