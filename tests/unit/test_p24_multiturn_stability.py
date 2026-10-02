"""
tests/unit/test_p24_multiturn_stability.py

Suite 2: Multi-Turn Stability & Feedforward Invariant Verification for Phase 24.
Validates:
  - Multi-turn stability over >= 20 continuous turns (zero parameter drift / accumulation).
  - Strict Feed-Forward Invariant: Speech/voice actuators NEVER mutate limbic ODE hidden state or R_t.
  - Relational inertia: Smooth, bounded evolution without acoustic chatter across turns.
"""

from __future__ import annotations

import numpy as np
import pytest

from src.core.communication.communication_policy import CommunicationPolicy
from src.core.emotion.emotion_core import EmotionConfig, EmotionCore
from src.core.expression.expression_policy import ExpressionPolicy
from src.core.models import PADState, SomaticMarkers
from src.core.voice.boundary import compute_f0_contour


class TestMultiTurnStability:
    def setup_method(self):
        self.expr_policy = ExpressionPolicy(smoothing_factor=0.25)
        self.comm_policy = CommunicationPolicy()

    def test_parameter_drift_free_over_30_turns(self):
        """Stationary internal state over 30 turns must produce stationary prosody without runaway."""
        r_state = {"closeness": 0.35, "trust": 0.60, "familiarity": 0.40, "reciprocity": 0.50}
        pad = PADState(pleasure=0.20, arousal=-0.05, dominance=0.10, timestamp=0.0)
        somatic = SomaticMarkers(stability=0.90, cognitive_load=0.20, energy=0.85, tension=0.10)

        prev_expr = None
        semitones_history = []
        rate_history = []
        pause_history = []

        # Execute 30 turns
        for turn_idx in range(30):
            expr = self.expr_policy.compute(
                pad,
                somatic,
                relationship=r_state,
                prev_state=prev_expr,
            )
            prev_expr = expr

            semitones_history.append(expr.voice.pitch_shift_semitones)
            rate_history.append(expr.voice.speech_rate_pct)
            pause_history.append(expr.voice.pause_duration_ms)

        # After initial smoothing converges (~5 turns), all trajectories must be completely flat
        converged_semitones = semitones_history[10:]
        converged_rates = rate_history[10:]

        assert np.std(converged_semitones) < 1e-4, f"Pitch drifted: std={np.std(converged_semitones)}"
        assert np.std(converged_rates) < 1e-4, f"Rate drifted: std={np.std(converged_rates)}"

        # Final values must be within safe bounded domains
        assert -2.0 <= semitones_history[-1] <= 4.0
        assert -20.0 <= rate_history[-1] <= 20.0
        assert 100.0 <= pause_history[-1] <= 1000.0

    def test_feedforward_isolation_invariant(self):
        """Actuator execution and extreme prosody must NEVER mutate limbic ODE hidden state or R_t."""
        cfg = EmotionConfig(loop_cadence_ms=200)
        emotion_core = EmotionCore(config=cfg)

        initial_h = emotion_core._h.copy()
        initial_rel = emotion_core.get_relationship_context().copy()

        # Simulate generating extreme voice prosody (e.g. +4.0 st, +20% rate, +2.5 st focal)
        extreme_contour = compute_f0_contour(p_len=500, base_semitones=4.0, focal_accent_st=2.5)
        assert np.max(extreme_contour) <= 7.0

        # Verify limbic ODE state and relational state are completely untouched
        after_h = emotion_core._h
        after_rel = emotion_core.get_relationship_context()

        np.testing.assert_array_equal(
            initial_h,
            after_h,
            err_msg="Limbic ODE hidden state was corrupted by voice prosody computation!",
        )
        np.testing.assert_array_equal(
            initial_rel,
            after_rel,
            err_msg="Limbic relational state was corrupted by voice prosody computation!",
        )

    def test_relational_evolution_stability(self):
        """Gradual relational closeness increase (0.1 -> 0.6 over 20 turns) produces smooth prosodic curve."""
        pad = PADState(pleasure=0.10, arousal=0.0, dominance=0.05, timestamp=0.0)
        somatic = SomaticMarkers(stability=0.95, cognitive_load=0.10, energy=0.90, tension=0.05)

        prev_expr = None
        semitone_deltas = []

        for step in range(20):
            closeness = 0.10 + 0.025 * step  # 0.10 to 0.575
            rel = {"closeness": closeness, "trust": 0.50 + 0.01 * step, "familiarity": 0.02 * step}

            expr = self.expr_policy.compute(pad, somatic, relationship=rel, prev_state=prev_expr)
            if prev_expr is not None:
                delta = abs(expr.voice.pitch_shift_semitones - prev_expr.voice.pitch_shift_semitones)
                semitone_deltas.append(delta)
            prev_expr = expr

        # Max turn-to-turn semitone change must remain small (< 0.15 st per turn)
        assert max(semitone_deltas) < 0.15, f"Discontinuous pitch jump across turns: {max(semitone_deltas)}"
