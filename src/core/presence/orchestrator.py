"""
Presence Orchestrator — Multimodal Voice and Desktop Presence.

Extends Phase 4 InferencePipelineOrchestrator with VoiceEngine integration.
"""

from __future__ import annotations

import logging
from dataclasses import dataclass
from typing import Optional, Tuple

from src.core.inference.orchestrator import (
    InferenceOrchestratorConfig,
    InferencePipelineOrchestrator,
)
from src.core.voice.voice_engine import VoiceEngine, VoiceEngineConfig

logger = logging.getLogger(__name__)


@dataclass
class PresenceOrchestratorConfig(InferenceOrchestratorConfig):
    """
    Configuration for PresenceOrchestrator.

    Extends InferenceOrchestratorConfig with VoiceEngine settings.
    """

    base_voice: str = "en-US-AnaNeural"
    active_rvc_model: str = "default"
    voice_models_dir: str = "models/voice/rvc"
    pitch_shift: int = 0
    speech_rate: str = "+0%"
    speech_volume: str = "+0%"

    def to_voice_engine_config(self) -> VoiceEngineConfig:
        return VoiceEngineConfig(
            base_voice=self.base_voice,
            active_rvc_model=self.active_rvc_model,
            models_dir=self.voice_models_dir,
            pitch_shift=self.pitch_shift,
            speech_rate=self.speech_rate,
            speech_volume=self.speech_volume,
        )


class PresenceOrchestrator(InferencePipelineOrchestrator):
    """
    Complete presence-enabled orchestrator coordinating emotional ODE,
    subconscious memory, active inference, and real-time voice synthesis.
    """

    def __init__(self, config: PresenceOrchestratorConfig) -> None:
        if not isinstance(config, PresenceOrchestratorConfig):
            raise ValueError("config must be a PresenceOrchestratorConfig instance")

        super().__init__(config)
        self._presence_config = config
        self._voice_engine = VoiceEngine(config.to_voice_engine_config())

    @property
    def voice_engine(self) -> VoiceEngine:
        return self._voice_engine

    async def process_with_voice(self, input_text: str) -> Tuple[str, bytes]:
        """
        Execute full cognitive pipeline and synthesize matching spoken voice.
        """
        response_text = self.process(input_text)
        audio_bytes = await self._voice_engine.synthesize_speech(response_text)
        return response_text, audio_bytes
