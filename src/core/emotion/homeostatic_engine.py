"""
HomeostaticEngine — derives somatic markers from PAD state and translates
them into behavioral constraints for the LLM_Backend.

Two responsibilities:
  1. compute_somatic_markers()  — stability, cognitive_load, energy, tension
  2. compute_behavioral_constraints() — max_tokens, temperature, latency_ms, reasoning_depth

The engine maintains rolling instance state (energy, input timestamps) that
persists between calls. Construct a fresh instance per test to reset state.

Design ref: design.md §HomeostaticEngine
Requirements: 2.1–2.7, 3.1–3.12
"""

from __future__ import annotations

import time
from collections import deque
from typing import Deque, Optional

import numpy as np

from src.core.config import HomeostaticConfig
from src.core.models import (
    BehavioralConstraints,
    PADState,
    SomaticMarkers,
    default_behavioral_constraints,
)

# ---------------------------------------------------------------------------
# Defaults produced when no threshold condition applies (Requirement 3.10)
# ---------------------------------------------------------------------------
_DEFAULT_MAX_TOKENS = 150
_DEFAULT_TEMPERATURE = 0.75
_DEFAULT_LATENCY_MS = 0
_DEFAULT_REASONING_DEPTH = 1

# How many inputs/min is considered the maximum frequency contribution
_FREQ_SATURATION = 10.0   # 10 inputs within 60 s → cognitive_load freq component = 1.0

# Energy depletion per record_input() call
_ENERGY_DEPLETION_PER_INPUT = 0.05

# Energy recovery per second during idle (after 60 s idle threshold)
_ENERGY_RECOVERY_PER_SECOND = 0.02

# Idle threshold before energy recovery starts (seconds)
_IDLE_RECOVERY_THRESHOLD_S = 60.0


class HomeostaticEngine:
    """
    Derives somatic markers and behavioral constraints from PAD state.

    Instance state:
        _energy              float in [0.0, 1.0], init 1.0
        _input_timestamps    deque of monotonic timestamps for rolling 60-s window
        _last_input_time     monotonic time of the last record_input() call
        _last_constraints    last valid BehavioralConstraints (for error fallback)
    """

    def __init__(self, config: Optional[HomeostaticConfig] = None) -> None:
        if config is None:
            config = HomeostaticConfig()
        self._cfg = config

        # Persistent state
        self._energy: float = 1.0
        self._input_timestamps: Deque[float] = deque()
        self._last_input_time: Optional[float] = None
        self._last_constraints: Optional[BehavioralConstraints] = None

    # ------------------------------------------------------------------
    # Public: record input event
    # ------------------------------------------------------------------

    def record_input(self) -> None:
        """
        Record that a user input was received right now.
        Updates the rolling 60-second input counter and depletes energy.
        """
        now = time.monotonic()
        self._input_timestamps.append(now)
        self._prune_old_timestamps(now)
        self._last_input_time = now

        # Deplete energy (Requirement 2.4)
        self._energy = max(0.0, self._energy - _ENERGY_DEPLETION_PER_INPUT)

    def reset(self) -> None:
        """
        Reset rolling homeostatic state, energy level, and cached constraints to baseline.
        """
        self._energy = 1.0
        self._input_timestamps.clear()
        self._last_input_time = None
        self._last_constraints = None

    # ------------------------------------------------------------------
    # Public: compute somatic markers
    # ------------------------------------------------------------------

    def compute_somatic_markers(
        self,
        pad: PADState,
        valence: Optional[float] = None,
    ) -> SomaticMarkers:
        """
        Derive the four somatic markers from *pad* and optionally *valence*.

        Parameters
        ----------
        pad : PADState
            Current emotional state. All dims must be in [-1.0, 1.0].
        valence : float | None
            Incoming stimulus valence in [0.0, 1.0].  If None, tension = 0.0.
            If outside [0.0, 1.0], raises ValueError (Requirement 2.5).

        Returns
        -------
        SomaticMarkers
            All four values in [0.0, 1.0], computed within 5 ms.

        Raises
        ------
        ValueError
            If any PAD dimension is outside [-1.0, 1.0], or if valence is
            provided but outside [0.0, 1.0].
        """
        self._validate_pad(pad)

        if valence is not None and not (0.0 <= valence <= 1.0):
            raise ValueError(
                f"valence={valence!r} must be in [0.0, 1.0] or None"
            )

        # Apply idle energy recovery before computing
        self._apply_idle_recovery()

        now = time.monotonic()
        self._prune_old_timestamps(now)

        stability = self._compute_stability(pad)
        cognitive_load = self._compute_cognitive_load(pad)
        energy = self._energy   # already updated by record_input() / idle recovery
        tension = self._compute_tension(pad, valence)

        return SomaticMarkers(
            stability=float(np.clip(stability, 0.0, 1.0)),
            cognitive_load=float(np.clip(cognitive_load, 0.0, 1.0)),
            energy=float(np.clip(energy, 0.0, 1.0)),
            tension=float(np.clip(tension, 0.0, 1.0)),
        )

    # ------------------------------------------------------------------
    # Public: compute behavioral constraints
    # ------------------------------------------------------------------

    def compute_behavioral_constraints(
        self,
        markers: SomaticMarkers,
        pad: PADState,
    ) -> BehavioralConstraints:
        """
        Translate *markers* into LLM generation parameters.

        Parameters
        ----------
        markers : SomaticMarkers
        pad : PADState
            Used only for PAD dimension validation (Requirement 3.12).

        Returns
        -------
        BehavioralConstraints

        Raises
        ------
        ValueError
            If any PAD dimension is outside [-1.0, 1.0] (then returns last
            valid constraints or defaults, per Requirement 3.12).
        """
        self._validate_pad(pad)   # raises ValueError if invalid

        cfg = self._cfg
        cl = markers.cognitive_load
        ar = pad.arousal
        en = markers.energy
        st = markers.stability

        # --- max_tokens ---
        max_tokens = self._resolve_max_tokens(cl, en)

        # --- temperature ---
        temperature = self._resolve_temperature(ar, st)

        # --- latency_ms ---
        latency_ms = self._resolve_latency_ms(cl, en)

        # --- reasoning_depth ---
        reasoning_depth = self._resolve_reasoning_depth(en, cl)

        constraints = BehavioralConstraints(
            max_tokens=max_tokens,
            temperature=temperature,
            latency_ms=latency_ms,
            reasoning_depth=reasoning_depth,
        )
        self._last_constraints = constraints
        return constraints

    # ------------------------------------------------------------------
    # Private: somatic marker formulas
    # ------------------------------------------------------------------

    def _compute_stability(self, pad: PADState) -> float:
        """
        stability decreases when arousal > 0.5 and dominance < 0.5.

        Formula (design.md):
            base    = 1.0 - max(0, arousal - 0.5) * 2
            penalty = max(0, 0.5 - dominance) * 2
            stability = base - penalty * (1 - base)
        """
        # Map PAD arousal/dominance from [-1, 1] to [0, 1] for threshold comparison
        arousal_01 = (pad.arousal + 1.0) / 2.0
        dominance_01 = (pad.dominance + 1.0) / 2.0

        base = 1.0 - max(0.0, arousal_01 - 0.5) * 2.0
        penalty = max(0.0, 0.5 - dominance_01) * 2.0
        stability = base - penalty * (1.0 - base)
        return float(np.clip(stability, 0.0, 1.0))

    def _compute_cognitive_load(self, pad: PADState) -> float:
        """
        cognitive_load increases with input frequency and high arousal.

        Formula (design.md):
            freq_component    = clip(input_count_60s / 10.0, 0, 1)
            arousal_component = clip(max(0, arousal_01 - 0.5) * 2, 0, 1)
            cognitive_load    = (freq_component + arousal_component) / 2.0
        """
        arousal_01 = (pad.arousal + 1.0) / 2.0

        input_count = len(self._input_timestamps)
        freq_component = float(np.clip(input_count / _FREQ_SATURATION, 0.0, 1.0))

        arousal_component = float(np.clip(max(0.0, arousal_01 - 0.5) * 2.0, 0.0, 1.0))

        return float(np.clip((freq_component + arousal_component) / 2.0, 0.0, 1.0))

    def _compute_tension(self, pad: PADState, valence: Optional[float]) -> float:
        """
        tension = |valence - pleasure_01|  where pleasure_01 maps [-1,1]→[0,1].

        Returns 0.0 when valence is None.
        Raises ValueError when valence is outside [0.0, 1.0] (caller validates first).
        """
        if valence is None:
            return 0.0
        pleasure_01 = (pad.pleasure + 1.0) / 2.0
        raw = abs(valence - pleasure_01)
        return float(np.clip(raw, 0.0, 1.0))

    def _apply_idle_recovery(self) -> None:
        """
        Recover energy if no input has been received for >= 60 seconds.
        Recovery rate: _ENERGY_RECOVERY_PER_SECOND per second of idle time
        beyond the 60-second threshold.
        """
        if self._last_input_time is None:
            return
        now = time.monotonic()
        idle_seconds = now - self._last_input_time
        if idle_seconds >= _IDLE_RECOVERY_THRESHOLD_S:
            recovery_seconds = idle_seconds - _IDLE_RECOVERY_THRESHOLD_S
            recovery = recovery_seconds * _ENERGY_RECOVERY_PER_SECOND
            self._energy = min(1.0, self._energy + recovery)

    def _prune_old_timestamps(self, now: float) -> None:
        """Remove timestamps older than 60 seconds from the rolling window."""
        cutoff = now - 60.0
        while self._input_timestamps and self._input_timestamps[0] < cutoff:
            self._input_timestamps.popleft()

    # ------------------------------------------------------------------
    # Private: behavioral constraint resolution
    # ------------------------------------------------------------------

    def _resolve_max_tokens(self, cognitive_load: float, energy: float) -> int:
        """
        Priority (highest cognitive_load condition wins — Requirement 3.11):
          IF cognitive_load > 0.75  → ≤ 80   (Requirement 3.2)
          IF cl < 0.3 AND energy > 0.7 → ≥ 300  (Requirement 3.3)
          else → default 150
        """
        cfg = self._cfg
        # Collect active conditions as (priority_metric, resolver)
        conditions = []

        if cognitive_load > cfg.cognitive_load_high:
            conditions.append((cognitive_load, "high_load"))   # → ≤ 80

        if cognitive_load < cfg.cognitive_load_low and energy > cfg.energy_high:
            conditions.append((cognitive_load, "low_load"))    # → ≥ 300

        if not conditions:
            return _DEFAULT_MAX_TOKENS

        # Highest cognitive_load wins (Requirement 3.11)
        conditions.sort(key=lambda c: c[0], reverse=True)
        winner = conditions[0][1]

        if winner == "high_load":
            return 60   # midpoint ≤ 80
        else:
            return 350  # midpoint ≥ 300

    def _resolve_temperature(self, arousal: float, stability: float) -> float:
        """
        Priority (highest arousal condition wins — Requirement 3.11):
          IF arousal > 0.7   → (0.85, 2.0]  (Requirement 3.4)
          IF arousal < 0.3 AND stability > 0.7 → [0.0, 0.65)  (Requirement 3.5)
          else → default 0.75

        Note: arousal here is the PAD arousal mapped to [0, 1].
        """
        cfg = self._cfg
        # Map PAD arousal from [-1, 1] to [0, 1]
        arousal_01 = (arousal + 1.0) / 2.0
        stability_01 = stability  # stability is already in [0, 1]

        conditions = []

        if arousal_01 > cfg.arousal_high:
            conditions.append((arousal_01, "high_arousal"))

        if arousal_01 < cfg.arousal_low and stability_01 > cfg.stability_high:
            conditions.append((arousal_01, "low_arousal_high_stability"))

        if not conditions:
            return _DEFAULT_TEMPERATURE

        # Highest arousal wins (Requirement 3.11)
        conditions.sort(key=lambda c: c[0], reverse=True)
        winner = conditions[0][1]

        if winner == "high_arousal":
            return 1.0    # in (0.85, 2.0]
        else:
            return 0.5    # in [0.0, 0.65)

    def _resolve_latency_ms(self, cognitive_load: float, energy: float) -> int:
        """
        Priority (highest cognitive_load condition wins — Requirement 3.11):
          IF cl > 0.8 AND energy < 0.3  → ≥ 400 ms  (Requirement 3.6)
          IF energy > 0.7 AND cl < 0.4  → 0 ms       (Requirement 3.7)
          else → default 0
        """
        cfg = self._cfg
        conditions = []

        if cognitive_load > cfg.cognitive_load_very_high and energy < cfg.energy_low:
            conditions.append((cognitive_load, "high_load_low_energy"))

        if energy > cfg.energy_high and cognitive_load < cfg.cognitive_load_for_latency:
            conditions.append((cognitive_load, "high_energy_low_load"))

        if not conditions:
            return _DEFAULT_LATENCY_MS

        conditions.sort(key=lambda c: c[0], reverse=True)
        winner = conditions[0][1]

        if winner == "high_load_low_energy":
            return 500    # ≥ 400 ms
        else:
            return 0

    def _resolve_reasoning_depth(self, energy: float, cognitive_load: float) -> int:
        """
        IF energy <= 0.2          → 0  (Requirement 3.8, inclusive boundary)
        IF energy > 0.7 AND cl < 0.4 → 3  (Requirement 3.9)
        else → default 1
        """
        cfg = self._cfg

        if energy <= cfg.energy_very_low:
            return 0

        if energy > cfg.energy_high and cognitive_load < cfg.cognitive_load_for_latency:
            return 3

        return _DEFAULT_REASONING_DEPTH

    # ------------------------------------------------------------------
    # Private: PAD validation
    # ------------------------------------------------------------------

    def _validate_pad(self, pad: PADState) -> None:
        """
        Raise ValueError if any PAD dimension is outside [-1.0, 1.0].
        Per Requirement 3.12: the engine then returns the last valid constraints
        (caller is responsible for catching and using self._last_constraints).
        """
        for name, val in [
            ("pleasure", pad.pleasure),
            ("arousal", pad.arousal),
            ("dominance", pad.dominance),
        ]:
            if not (-1.0 <= val <= 1.0):
                raise ValueError(
                    f"PADState.{name}={val!r} is outside [-1.0, 1.0]. "
                    f"Returning last valid constraints."
                )
