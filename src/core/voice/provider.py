"""Modular voice provider interfaces and base classes."""
from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional


class BaseVoiceProvider(ABC):
    """Abstract base provider for speech synthesis and voice conversion engines."""

    @abstractmethod
    async def synthesize(
        self,
        text: str,
        voice_name: str = "default",
        pitch_shift: int = 0,
        rate_pct: int = 0,
        volume_pct: int = 0,
    ) -> bytes:
        """Synthesize speech audio bytes from text."""
        pass

    @abstractmethod
    def list_available_models(self) -> List[Dict[str, Any]]:
        """Return a list of available voice models for this provider."""
        pass
