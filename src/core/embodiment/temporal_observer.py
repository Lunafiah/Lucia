"""
src/core/embodiment/temporal_observer.py

Extracts temporal and social interaction cues from incoming user input:
  - Inter-turn elapsed idle time (dt_idle)
  - Estimated or measured user turn latency
  - Estimated user speech tempo / cadence ratio
  - User pause duration and punctuation density

Decoupled from output actuation: strictly observes incoming user signals.
"""

from __future__ import annotations

import logging
import re
import threading
import time
from typing import Optional

import numpy as np

from src.core.embodiment.contract import TemporalObservation

logger = logging.getLogger(__name__)


class TemporalObserver:
    """
    Thread-safe observer extracting temporal and interaction markers from user turns.
    """

    def __init__(self, default_nominal_latency_ms: float = 400.0) -> None:
        self.default_nominal_latency_ms = float(default_nominal_latency_ms)
        self._last_turn_timestamp: Optional[float] = None
        self._last_turn_duration_estimate: float = 0.0
        self._lock = threading.Lock()

    def observe(
        self,
        current_timestamp: Optional[float] = None,
        user_text: str = "",
        explicit_user_latency_ms: Optional[float] = None,
        audio_duration_ms: Optional[float] = None,
        pause_duration_ms: Optional[float] = None,
    ) -> TemporalObservation:
        """
        Produce a TemporalObservation snapshot from the current turn.
        """
        now = time.time() if current_timestamp is None else float(current_timestamp)

        with self._lock:
            # 1. Compute elapsed idle time since the conclusion of the previous turn
            if self._last_turn_timestamp is None:
                dt_idle = 0.0
            else:
                dt_idle = max(0.0, now - self._last_turn_timestamp)

            # 2. Determine or estimate user turn latency
            if explicit_user_latency_ms is not None:
                user_latency = max(50.0, min(5000.0, float(explicit_user_latency_ms)))
            elif self._last_turn_timestamp is not None and dt_idle < 30.0:
                # If conversational turn occurs within 30s, dt_idle serves as latency proxy
                user_latency = max(50.0, min(5000.0, dt_idle * 1000.0))
            else:
                user_latency = self.default_nominal_latency_ms

            # 3. Analyze text structure for tempo and pauses
            clean_text = user_text.strip() if user_text else ""
            tokens = clean_text.split()
            token_count = max(1, len(tokens))

            # Punctuation analysis
            ellipsis_count = len(re.findall(r"\.\.\.|…", clean_text))
            comma_count = len(re.findall(r",|、", clean_text))
            period_count = len(re.findall(r"\.|\?|!|。|？|！", clean_text))
            total_punct = ellipsis_count + comma_count + period_count
            char_count = max(1, len(clean_text))
            punct_density = min(1.0, total_punct / char_count)

            # Pause duration estimate: ellipses indicate hesitation / longer pause
            if pause_duration_ms is not None:
                pause_est = max(0.0, min(2000.0, float(pause_duration_ms)))
            else:
                base_pause = 150.0
                if ellipsis_count > 0:
                    base_pause += min(600.0, ellipsis_count * 200.0)
                if comma_count > 0:
                    base_pause += min(200.0, comma_count * 50.0)
                pause_est = base_pause

            # Tempo ratio estimate: average word length and exclamation/punctuation density
            # Baseline tempo ratio is 1.0 (normative). Fast speech > 1.0, slow speech < 1.0
            tempo_ratio = 1.0
            if token_count > 1:
                avg_token_len = char_count / token_count
                if avg_token_len > 7.0 or ellipsis_count > 0:
                    # Longer words or ellipses suggest deliberate/slower pacing
                    tempo_ratio -= min(0.25, 0.05 * ellipsis_count + 0.02 * (avg_token_len - 5.0))
                elif avg_token_len < 4.0 and total_punct <= 1:
                    # Short, terse words suggest rapid conversational pace
                    tempo_ratio += min(0.25, 0.05 * (4.0 - avg_token_len))
            tempo_ratio = float(np.clip(tempo_ratio, 0.70, 1.30))

            # Update internal state tracking
            self._last_turn_timestamp = now

            return TemporalObservation(
                timestamp=now,
                dt_idle_seconds=dt_idle,
                user_latency_ms=user_latency,
                speech_tempo_ratio=tempo_ratio,
                pause_duration_ms=pause_est,
                turn_token_count=token_count,
                punct_density=punct_density,
            )

    def reset(self) -> None:
        """Reset internal turn timestamps."""
        with self._lock:
            self._last_turn_timestamp = None
            self._last_turn_duration_estimate = 0.0
