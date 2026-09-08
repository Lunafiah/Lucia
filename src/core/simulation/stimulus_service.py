"""
StimulusService — Normal sensory pathway and debug vector probe for Lucia Simulation (Phase 8).

Architectural Invariant (INV-3 / User Requirement 2):
- Normal sensory pathway: Text → StimulusProcessor → 16D stimulus vector → Brain.
- Developer/Debug probe: Direct 16D vector injection is isolated explicitly and marked as debug_probe.
"""

from __future__ import annotations

from collections import deque
from dataclasses import asdict
import logging
import time
from typing import Any, Dict, List, Optional, Sequence, Union

import numpy as np

from src.core.config import StimulusConfig
from src.core.emotion.emotion_core import EmotionCore
from src.core.gating.stimulus_processor import StimulusProcessor
from src.core.models import PADState

logger = logging.getLogger("lucia.simulation.stimulus_service")


def _pad_to_dict(pad: PADState) -> Dict[str, Any]:
    return {
        "pleasure": round(float(pad.pleasure), 4),
        "arousal": round(float(pad.arousal), 4),
        "dominance": round(float(pad.dominance), 4),
        "timestamp": float(pad.timestamp),
    }

# Predefined standard emotional vectors (16D) and representative sensory text
PRESET_STIMULI: Dict[str, Dict[str, Any]] = {
    "joy": {
        "label": "Joyful / Uplifting",
        "description": "High positive valence, moderate arousal, warm tone",
        "text": "I'm so incredibly happy to see you today! Everything feels wonderful!",
        "vector": [0.85, 0.60, 0.40] + [0.0] * 13,
    },
    "calm": {
        "label": "Calm / Peaceful",
        "description": "Moderate positive valence, low arousal, soothing baseline",
        "text": "Everything is quiet and gentle now. Let us rest peacefully.",
        "vector": [0.40, 0.05, 0.10] + [0.0] * 13,
    },
    "tension": {
        "label": "High Tension / Urgent",
        "description": "Negative valence, high arousal, high semantic pressure",
        "text": "CRITICAL ALERT: Something has gone wrong! We need to act immediately!",
        "vector": [-0.70, 0.85, 0.50] + [0.0] * 13,
    },
    "affection": {
        "label": "Affection / Warmth",
        "description": "High valence, gentle arousal, deep resonance",
        "text": "Thank you for being here with me. I truly appreciate you.",
        "vector": [0.75, 0.25, 0.30] + [0.0] * 13,
    },
    "fatigue": {
        "label": "Fatigue / Exhaustion",
        "description": "Low valence, near-zero arousal, low dominance",
        "text": "I am so tired... running out of energy completely...",
        "vector": [-0.30, -0.60, -0.40] + [0.0] * 13,
    },
    "curiosity": {
        "label": "Curiosity / Wonder",
        "description": "Positive valence, high arousal, inquisitive",
        "text": "What does this mean? Tell me more about how this works!",
        "vector": [0.50, 0.65, 0.40] + [0.0] * 13,
    },
    "resting_attractor": {
        "label": "Philia Resting Attractor",
        "description": "Canonical Philia resting state baseline (P=+0.25, A=-0.05, D=+0.05)",
        "text": "Good morning. I am here with you.",
        "vector": [0.25, -0.05, 0.05] + [0.0] * 13,
    },
}


class StimulusService:
    """
    Manages sensory stimulus generation and developer probe injection in simulation.
    """

    def __init__(
        self,
        emotion_core: EmotionCore,
        stimulus_processor: Optional[StimulusProcessor] = None,
        history_limit: int = 100,
    ) -> None:
        self._emotion_core = emotion_core
        self._stimulus_processor = stimulus_processor or StimulusProcessor(StimulusConfig())
        self._history: deque = deque(maxlen=history_limit)

    # ------------------------------------------------------------------
    # Normal Sensory Pathway (Text → Processor → Vector → Brain)
    # ------------------------------------------------------------------

    def inject_text(
        self,
        text: str,
        source: str = "simulation_ui",
        custom_timestamp: Optional[float] = None,
    ) -> Dict[str, Any]:
        """
        Processes text through the full sensory encoder pipeline:
        Text → StimulusProcessor.encode() → 16D vector → EmotionCore.
        """
        if not isinstance(text, str):
            raise TypeError(f"text must be a string, got {type(text)}")

        pad_before = self._emotion_core.get_pad_state()

        # Step 1: Sensory encoding
        vector_np = self._stimulus_processor.encode(text)
        vector_list = [float(v) for v in vector_np]

        # Step 2: Inject to brain
        self._emotion_core.push_stimulus(vector_np)
        pad_after = self._emotion_core.step_once(custom_timestamp=custom_timestamp)

        delta = {
            "p": round(pad_after.pleasure - pad_before.pleasure, 4),
            "a": round(pad_after.arousal - pad_before.arousal, 4),
            "d": round(pad_after.dominance - pad_before.dominance, 4),
        }

        entry = {
            "pathway": "sensory_text",
            "source": source,
            "text": text,
            "vector": vector_list,
            "timestamp": custom_timestamp if custom_timestamp is not None else time.monotonic(),
            "pad_before": _pad_to_dict(pad_before),
            "pad_after": _pad_to_dict(pad_after),
            "pad_delta": delta,
        }
        self._history.append(entry)
        logger.info("Injected sensory text (len=%d) via %s -> PAD delta: %s", len(text), source, delta)
        return entry

    # ------------------------------------------------------------------
    # Developer / Debug Probe (Direct 16D Vector Injection ONLY)
    # ------------------------------------------------------------------

    def inject_vector(
        self,
        vector: Union[Sequence[float], np.ndarray],
        source: str = "debug_probe",
        custom_timestamp: Optional[float] = None,
    ) -> Dict[str, Any]:
        """
        Explicit developer/debug instrumentation probe.
        Directly injects a raw 16D vector into EmotionCore.
        Clearly separated from normal sensory text processing.
        """
        if isinstance(vector, np.ndarray):
            vec_list = [float(v) for v in vector]
        elif isinstance(vector, (list, tuple)):
            vec_list = [float(v) for v in vector]
        else:
            raise TypeError(f"vector must be a list, tuple, or np.ndarray, got {type(vector)}")

        if len(vec_list) != 16:
            raise ValueError(f"Stimulus vector must have exactly 16 dimensions, got {len(vec_list)}")

        for i, val in enumerate(vec_list):
            if not np.isfinite(val):
                raise ValueError(f"Vector component {i} is not finite: {val}")

        # Clamped to [-1.0, 1.0] for safety
        clamped_vec = np.clip(np.array(vec_list, dtype=np.float64), -1.0, 1.0)
        pad_before = self._emotion_core.get_pad_state()

        self._emotion_core.push_stimulus(clamped_vec)
        pad_after = self._emotion_core.step_once(custom_timestamp=custom_timestamp)

        delta = {
            "p": round(pad_after.pleasure - pad_before.pleasure, 4),
            "a": round(pad_after.arousal - pad_before.arousal, 4),
            "d": round(pad_after.dominance - pad_before.dominance, 4),
        }

        entry = {
            "pathway": "debug_vector_probe",
            "source": source,
            "text": None,
            "vector": [float(v) for v in clamped_vec],
            "timestamp": custom_timestamp if custom_timestamp is not None else time.monotonic(),
            "pad_before": _pad_to_dict(pad_before),
            "pad_after": _pad_to_dict(pad_after),
            "pad_delta": delta,
        }
        self._history.append(entry)
        logger.info("Injected debug vector probe via %s -> PAD delta: %s", source, delta)
        return entry

    # ------------------------------------------------------------------
    # Presets and History
    # ------------------------------------------------------------------

    def get_presets(self) -> Dict[str, Dict[str, Any]]:
        """Return predefined sensory/probe presets."""
        return dict(PRESET_STIMULI)

    def inject_preset(
        self,
        preset_name: str,
        pathway: str = "sensory_text",
        source: str = "preset_injector",
        custom_timestamp: Optional[float] = None,
    ) -> Dict[str, Any]:
        """Inject one of the standard presets either as sensory text or debug vector."""
        if preset_name not in PRESET_STIMULI:
            raise KeyError(f"Unknown preset '{preset_name}'. Available: {list(PRESET_STIMULI.keys())}")

        preset = PRESET_STIMULI[preset_name]
        if pathway == "sensory_text":
            return self.inject_text(preset["text"], source=f"{source}:{preset_name}", custom_timestamp=custom_timestamp)
        elif pathway in ("debug_vector_probe", "vector"):
            return self.inject_vector(preset["vector"], source=f"{source}:{preset_name}", custom_timestamp=custom_timestamp)
        else:
            raise ValueError(f"Unsupported pathway '{pathway}'. Must be 'sensory_text' or 'debug_vector_probe'.")

    def get_history(self, limit: int = 50) -> List[Dict[str, Any]]:
        """Return the most recent stimulus injection history."""
        items = list(self._history)
        return items[-limit:]

    def clear_history(self) -> None:
        """Clear the stimulus injection history."""
        self._history.clear()
