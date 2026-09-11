"""
src/core/expression/expression_policy.py

Multimodal Expression Policy engine for Lucia Phase 16.
Maps internal PAD, somatic markers, and relationship conditioning into
the canonical 15-dimensional ExpressionState across Text, Voice, Facial, and Posture.

Pre-Reflective Architectural Invariants:
  - Feedforward actuator decoupling: Expression outputs NEVER feed back into EmotionCore ODE.
  - Extra latency is strictly capped at 500 ms.
  - Exponential temporal smoothing with gamma = 0.25 preserves physical continuity.
"""

from __future__ import annotations

import logging
from typing import Any, Dict, Optional

import numpy as np

from src.core.expression.expression_state import (
    ExpressionState,
    FacialExpression,
    PostureGaze,
    TextStyle,
    VoiceProsody,
)
from src.core.expression.semantic_consistency_guard import SemanticIntent
from src.core.models import PADState, SomaticMarkers

logger = logging.getLogger(__name__)


class ExpressionPolicy:
    """
    Computes ExpressionState from internal affect, somatic markers,
    and relationship conditioning.
    """

    def __init__(self, smoothing_factor: float = 0.25) -> None:
        self.smoothing_factor = float(smoothing_factor)

    @classmethod
    def get_neutral_actuator_baseline(cls) -> ExpressionState:
        """
        Default neutral baseline of the expression actuator.
        Distinct from erasing or zeroing Core Philia.
        """
        return ExpressionState(
            text=TextStyle(temperature_mod=0.0, verbosity_factor=1.0, formality_score=0.5, cadence_style="balanced"),
            voice=VoiceProsody(pitch_shift_hz=0.0, speech_rate_pct=0.0, volume_pct=0.0, pause_duration_ms=200.0),
            facial=FacialExpression(smile=0.0, frown=0.0, eye_open=0.80, brow_angle=0.0, blush=0.0),
            posture_gaze=PostureGaze(head_tilt_deg=0.0, gaze_aversion_prob=0.10),
            extra_latency_ms=0.0,
            semantic_safe=True,
            provenance="ActuatorNeutralBaseline",
        )

    def compute(
        self,
        pad: PADState,
        somatic: Optional[SomaticMarkers] = None,
        relationship: Optional[Dict[str, float]] = None,
        intent: Optional[SemanticIntent] = None,
        prev_state: Optional[ExpressionState] = None,
        *,
        affect_enabled: bool = True,
        text_enabled: bool = True,
        voice_enabled: bool = True,
        avatar_enabled: bool = True,
    ) -> ExpressionState:
        """
        Pure, bounded evaluation of the multimodal expression policy.
        """
        if not affect_enabled:
            target = self.get_neutral_actuator_baseline()
            if prev_state is not None:
                return self._smooth_transition(prev_state, target)
            return target

        p = float(np.clip(pad.pleasure, -1.0, 1.0))
        a = float(np.clip(pad.arousal, -1.0, 1.0))
        d = float(np.clip(pad.dominance, -1.0, 1.0))

        cog_load = float(np.clip(somatic.cognitive_load if somatic else 0.0, 0.0, 1.0))
        energy = float(np.clip(somatic.energy if somatic else 1.0, 0.0, 1.0))
        tension = float(np.clip(somatic.tension if somatic else 0.0, 0.0, 1.0))

        trust = float(np.clip(relationship.get("trust", 0.5) if relationship else 0.5, 0.0, 1.0))
        closeness = float(np.clip(relationship.get("closeness", 0.1) if relationship else 0.1, 0.0, 1.0))

        # --- Text Modality ---
        if text_enabled:
            t_mod = float(np.clip(0.10 * a - 0.05 * tension, -0.20, 0.20))
            v_fact = float(np.clip(1.0 + 0.20 * p - 0.30 * cog_load - 0.25 * (1.0 - energy), 0.50, 1.50))
            formality = float(np.clip(0.50 - 0.30 * p - 0.20 * closeness + 0.20 * (1.0 - trust), 0.0, 1.0))
            cadence = "concise" if v_fact < 0.85 else ("expansive" if v_fact > 1.20 else "balanced")
            text_style = TextStyle(
                temperature_mod=t_mod,
                verbosity_factor=v_fact,
                formality_score=formality,
                cadence_style=cadence,
            )
        else:
            text_style = self.get_neutral_actuator_baseline().text

        # --- Voice Modality ---
        if voice_enabled:
            pitch = float(np.clip(15.0 * p + 10.0 * a, -30.0, 30.0))
            rate = float(np.clip(15.0 * a - 10.0 * (1.0 - energy), -25.0, 25.0))
            vol = float(np.clip(10.0 * d + 5.0 * a, -20.0, 20.0))
            pause = float(np.clip(200.0 + 300.0 * (1.0 - energy) + 150.0 * tension, 100.0, 1000.0))
            voice_prosody = VoiceProsody(
                pitch_shift_hz=pitch,
                speech_rate_pct=rate,
                volume_pct=vol,
                pause_duration_ms=pause,
            )
        else:
            voice_prosody = self.get_neutral_actuator_baseline().voice

        # --- Facial Modality ---
        if avatar_enabled:
            smile = float(np.clip(max(0.0, p), 0.0, 1.0))
            frown = float(np.clip(max(0.0, -p), 0.0, 1.0))
            eye_open = float(np.clip(0.80 + 0.25 * a, 0.30, 1.20))
            brow_angle = float(np.clip(0.30 * p - 0.20 * frown - 0.15 * tension, -0.50, 0.50))
            blush = float(np.clip((p - 0.15) * 1.5 if p > 0.15 else 0.0, 0.0, 1.0))
            head_tilt = float(np.clip(-d * 6.0, -10.0, 10.0))
            gaze_avert = float(np.clip(0.10 + 0.40 * (1.0 - energy) + 0.30 * tension - 0.10 * trust, 0.0, 1.0))

            facial = FacialExpression(
                smile=smile,
                frown=frown,
                eye_open=eye_open,
                brow_angle=brow_angle,
                blush=blush,
            )
            posture_gaze = PostureGaze(
                head_tilt_deg=head_tilt,
                gaze_aversion_prob=gaze_avert,
            )
        else:
            facial = self.get_neutral_actuator_baseline().facial
            posture_gaze = self.get_neutral_actuator_baseline().posture_gaze

        latency = float(np.clip((1.0 - energy) * 250.0 + cog_load * 150.0, 0.0, 500.0))

        target = ExpressionState(
            text=text_style,
            voice=voice_prosody,
            facial=facial,
            posture_gaze=posture_gaze,
            extra_latency_ms=latency,
            semantic_safe=True,
            provenance="ExpressionPolicy/Computed",
        )

        if prev_state is not None:
            return self._smooth_transition(prev_state, target)
        return target

    def _smooth_transition(self, prev: ExpressionState, target: ExpressionState) -> ExpressionState:
        """Exponential temporal smoothing: E_t = (1 - γ) E_{t-1} + γ E_{target}."""
        gamma = self.smoothing_factor

        def lerp(a: float, b: float) -> float:
            return float((1.0 - gamma) * a + gamma * b)

        text_style = TextStyle(
            temperature_mod=lerp(prev.text.temperature_mod, target.text.temperature_mod),
            verbosity_factor=lerp(prev.text.verbosity_factor, target.text.verbosity_factor),
            formality_score=lerp(prev.text.formality_score, target.text.formality_score),
            cadence_style=target.text.cadence_style,
        )

        voice_prosody = VoiceProsody(
            pitch_shift_hz=lerp(prev.voice.pitch_shift_hz, target.voice.pitch_shift_hz),
            speech_rate_pct=lerp(prev.voice.speech_rate_pct, target.voice.speech_rate_pct),
            volume_pct=lerp(prev.voice.volume_pct, target.voice.volume_pct),
            pause_duration_ms=lerp(prev.voice.pause_duration_ms, target.voice.pause_duration_ms),
        )

        facial = FacialExpression(
            smile=lerp(prev.facial.smile, target.facial.smile),
            frown=lerp(prev.facial.frown, target.facial.frown),
            eye_open=lerp(prev.facial.eye_open, target.facial.eye_open),
            brow_angle=lerp(prev.facial.brow_angle, target.facial.brow_angle),
            blush=lerp(prev.facial.blush, target.facial.blush),
        )

        posture_gaze = PostureGaze(
            head_tilt_deg=lerp(prev.posture_gaze.head_tilt_deg, target.posture_gaze.head_tilt_deg),
            gaze_aversion_prob=lerp(prev.posture_gaze.gaze_aversion_prob, target.posture_gaze.gaze_aversion_prob),
        )

        latency = lerp(prev.extra_latency_ms, target.extra_latency_ms)

        return ExpressionState(
            text=text_style,
            voice=voice_prosody,
            facial=facial,
            posture_gaze=posture_gaze,
            extra_latency_ms=latency,
            semantic_safe=target.semantic_safe,
            provenance="ExpressionPolicy/Smoothed",
        )

    def render_surface_message(self, intent: SemanticIntent, expr_state: ExpressionState) -> str:
        """
        Render surface string preserving underlying proposition truth conditions.
        """
        if intent.polarity:
            core = f"{intent.subject} {intent.predicate} {intent.object}"
        else:
            core = f"{intent.subject} is not {intent.predicate} {intent.object}"

        details = []
        for k, v in intent.named_entities.items():
            details.append(f"{k}: {v}")
        for k, v in intent.numerical_values.items():
            details.append(f"{k}={v:g}")
        detail_str = f" ({', '.join(details)})" if details else ""

        prefix = ""
        suffix = ""

        # Formality framing
        if expr_state.text.formality_score > 0.65:
            prefix = "Notice: "
            suffix = " per current specifications."
        elif expr_state.text.formality_score < 0.35:
            prefix = "Just letting you know, "
            suffix = "."

        full_text = f"{prefix}{core}{detail_str}{suffix}".strip()
        return full_text
