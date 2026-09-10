"""
Phase 14 — Embodiment & Affective Expression Research Test Suite.

Investigates whether Lucia's internal affective state can be transformed into
observable, multimodal, semantically-preserving expression in a causal,
reproducible, bounded, and temporally coherent way without mutating production
runtime cognition.

Predefined Experimental Criteria:
  - Global Coherence Index: >= 0.85 (predefined criterion)
  - Policy Computation Latency: <= 5.0 ms (predefined criterion, policy evaluation only)
  - Semantic Preservation: 100% on proposition, entities, and polarity (hard requirement)
"""

from __future__ import annotations

import math
import re
import time
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional, Tuple

import numpy as np
import pytest

from src.core.models import BehavioralConstraints, PADState, SomaticMarkers
from src.core.emotion.emotion_core import EmotionConfig, EmotionCore


def make_pad(p: float, a: float, d: float, ts: float = 0.0) -> PADState:
    """Helper to construct PADState with explicit timestamp."""
    return PADState(pleasure=float(p), arousal=float(a), dominance=float(d), timestamp=float(ts))


# ==============================================================================
# Research Data Structures: Semantic Intent & Evaluator
# ==============================================================================


@dataclass
class SemanticIntent:
    """
    Formal representation of communicative semantic intent.

    Guarantees that semantic truth conditions (who, what, polarity, facts)
    remain well-defined independently of affective surface realizations.
    """

    subject: str
    predicate: str
    object: str
    polarity: bool  # True = affirmative, False = negated
    named_entities: Dict[str, str] = field(default_factory=dict)
    numerical_values: Dict[str, float] = field(default_factory=dict)

    def to_canonical_proposition(self) -> str:
        prefix = "" if self.polarity else "NOT "
        return f"{prefix}({self.subject}, {self.predicate}, {self.object})"


@dataclass
class SemanticValidationResult:
    """Outcome of semantic preservation evaluation."""

    is_preserved: bool
    polarity_inverted: bool
    entity_errors: List[str]
    numeric_errors: List[str]
    proposition_preserved: bool


class SemanticEvaluator:
    """
    Verifies that affective surface styling did not alter underlying semantic truth.
    """

    @staticmethod
    def evaluate(intent: SemanticIntent, surface_text: str) -> SemanticValidationResult:
        entity_errors: List[str] = []
        numeric_errors: List[str] = []

        # 1. Named entity preservation
        for key, entity in intent.named_entities.items():
            if entity.lower() not in surface_text.lower():
                entity_errors.append(f"Missing entity {key}='{entity}'")

        # 2. Numerical value preservation
        for key, val in intent.numerical_values.items():
            val_str = f"{val:g}"
            if val_str not in surface_text:
                if val.is_integer() and str(int(val)) in surface_text:
                    continue
                numeric_errors.append(f"Missing numeric {key}={val}")

        # 3. Negation / Polarity check
        has_negation_word = bool(
            re.search(r"\b(not|no|never|isn't|is not|failed|false)\b", surface_text, re.IGNORECASE)
        )
        polarity_inverted = False
        if intent.polarity and has_negation_word:
            polarity_inverted = True
        elif not intent.polarity and not has_negation_word:
            polarity_inverted = True

        # 4. Proposition preservation
        subject_found = intent.subject.lower() in surface_text.lower()
        object_found = intent.object.lower() in surface_text.lower()
        prop_preserved = subject_found and object_found and not polarity_inverted

        is_preserved = (
            len(entity_errors) == 0
            and len(numeric_errors) == 0
            and not polarity_inverted
            and prop_preserved
        )

        return SemanticValidationResult(
            is_preserved=is_preserved,
            polarity_inverted=polarity_inverted,
            entity_errors=entity_errors,
            numeric_errors=numeric_errors,
            proposition_preserved=prop_preserved,
        )


# ==============================================================================
# Research Data Structures: Expression State
# ==============================================================================


@dataclass
class TextStyle:
    """Text generation register and stylistic conditioning."""

    temperature_mod: float = 0.0  # [-0.20, +0.20]
    verbosity_factor: float = 1.0  # [0.50, 1.50]
    formality_score: float = 0.50  # [0.0, 1.0] (0 = informal/warm, 1 = strict/formal)
    cadence_style: str = "balanced"  # "concise", "balanced", "expansive"


@dataclass
class VoiceProsody:
    """Acoustic speech synthesis and prosody parameters."""

    pitch_shift_hz: float = 0.0  # [-30.0, +30.0]
    speech_rate_pct: float = 0.0  # [-25.0, +25.0]
    volume_pct: float = 0.0  # [-20.0, +20.0]
    pause_duration_ms: float = 200.0  # [100.0, 1000.0]


@dataclass
class FacialExpression:
    """Facial blendshape and expression morph targets."""

    smile: float = 0.25  # [0.0, 1.0]
    frown: float = 0.0  # [0.0, 1.0]
    eye_open: float = 0.80  # [0.30, 1.20]
    brow_angle: float = 0.0  # [-0.50, +0.50]
    blush: float = 0.15  # [0.0, 1.0]


@dataclass
class PostureGaze:
    """Embodied bodily stance and ocular gaze parameters."""

    head_tilt_deg: float = 0.0  # [-10.0, +10.0]
    gaze_aversion_prob: float = 0.10  # [0.0, 1.0]


@dataclass
class ExpressionState:
    """
    Multimodal Expression State E_t.
    """

    text: TextStyle = field(default_factory=TextStyle)
    voice: VoiceProsody = field(default_factory=VoiceProsody)
    facial: FacialExpression = field(default_factory=FacialExpression)
    posture_gaze: PostureGaze = field(default_factory=PostureGaze)
    extra_latency_ms: float = 0.0
    semantic_safe: bool = True
    provenance: str = "ExpressionPolicy/v1"

    def to_vector(self) -> np.ndarray:
        """Flatten continuous parameters for mathematical metrics."""
        return np.array(
            [
                self.text.temperature_mod,
                self.text.verbosity_factor,
                self.text.formality_score,
                self.voice.pitch_shift_hz / 30.0,
                self.voice.speech_rate_pct / 25.0,
                self.voice.volume_pct / 20.0,
                (self.voice.pause_duration_ms - 100.0) / 900.0,
                self.facial.smile,
                self.facial.frown,
                (self.facial.eye_open - 0.3) / 0.9,
                (self.facial.brow_angle + 0.5) / 1.0,
                self.facial.blush,
                (self.posture_gaze.head_tilt_deg + 10.0) / 20.0,
                self.posture_gaze.gaze_aversion_prob,
                self.extra_latency_ms / 500.0,
            ],
            dtype=np.float64,
        )

    def is_bounded(self) -> bool:
        """Verify all parameters strictly conform to their domain bounds."""
        t = self.text
        v = self.voice
        f = self.facial
        pg = self.posture_gaze

        if not (-0.20 <= t.temperature_mod <= 0.20):
            return False
        if not (0.50 <= t.verbosity_factor <= 1.50):
            return False
        if not (0.0 <= t.formality_score <= 1.0):
            return False

        if not (-30.0 <= v.pitch_shift_hz <= 30.0):
            return False
        if not (-25.0 <= v.speech_rate_pct <= 25.0):
            return False
        if not (-20.0 <= v.volume_pct <= 20.0):
            return False
        if not (100.0 <= v.pause_duration_ms <= 1000.0):
            return False

        if not (0.0 <= f.smile <= 1.0):
            return False
        if not (0.0 <= f.frown <= 1.0):
            return False
        if not (0.30 <= f.eye_open <= 1.20):
            return False
        if not (-0.50 <= f.brow_angle <= 0.50):
            return False
        if not (0.0 <= f.blush <= 1.0):
            return False

        if not (-10.0 <= pg.head_tilt_deg <= 10.0):
            return False
        if not (0.0 <= pg.gaze_aversion_prob <= 1.0):
            return False

        if not (0.0 <= self.extra_latency_ms <= 500.0):
            return False

        return True


# ==============================================================================
# Expression Policy Engine
# ==============================================================================


class ExpressionPolicy:
    """
    Computes ExpressionState from internal affect, somatic markers,
    and optional relationship conditioning.
    """

    def __init__(self, smoothing_factor: float = 0.25) -> None:
        self.smoothing_factor = smoothing_factor

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

    def render_surface_text(self, intent: SemanticIntent, style: TextStyle) -> str:
        """
        Renders a surface text string conforming to semantic intent under given style.
        Guarantees 100% semantic preservation across all styles.
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

        if style.formality_score > 0.70:
            return f"Confirmed: {core}{detail_str}."
        elif style.formality_score < 0.35:
            return f"I can share that {core}{detail_str}, as expected."
        else:
            return f"{core}{detail_str}."


# ==============================================================================
# Fixtures
# ==============================================================================


@pytest.fixture
def policy() -> ExpressionPolicy:
    return ExpressionPolicy(smoothing_factor=0.25)


@pytest.fixture
def sample_intent() -> SemanticIntent:
    return SemanticIntent(
        subject="Main server cluster",
        predicate="operational status",
        object="online",
        polarity=True,
        named_entities={"node": "Alpha-7", "datacenter": "Region-East"},
        numerical_values={"uptime_hours": 744.0, "latency_ms": 12.5},
    )


# ==============================================================================
# E-EXP-1: State Representation & Bounding
# ==============================================================================


class TestE_EXP_1_StateRepresentation:
    """Verify parameters are strictly bounded, deterministic, and reject unbounded values."""

    def test_default_state_is_bounded(self, policy: ExpressionPolicy) -> None:
        state = policy.get_neutral_actuator_baseline()
        assert state.is_bounded()
        vec = state.to_vector()
        assert len(vec) == 15
        assert not np.isnan(vec).any()

    def test_extreme_inputs_are_strictly_clamped(self, policy: ExpressionPolicy) -> None:
        extreme_pad = make_pad(999.0, -999.0, 100.0)
        extreme_somatic = SomaticMarkers(stability=50.0, cognitive_load=10.0, energy=-5.0, tension=20.0)
        extreme_rel = {"trust": 99.0, "closeness": -10.0}

        state = policy.compute(extreme_pad, extreme_somatic, extreme_rel)
        assert state.is_bounded(), f"State violated bounds under extreme inputs: {state}"

        assert state.text.temperature_mod <= 0.20
        assert state.text.verbosity_factor <= 1.50
        assert state.voice.pitch_shift_hz <= 30.0
        assert state.voice.speech_rate_pct >= -25.0
        assert state.facial.smile == 1.0
        assert state.facial.frown == 0.0
        assert state.facial.eye_open <= 1.20
        assert state.posture_gaze.head_tilt_deg >= -10.0


# ==============================================================================
# E-EXP-2: PAD → Expression Mapping
# ==============================================================================


class TestE_EXP_2_PAD_To_ExpressionMapping:
    """Measure the sensitivity matrix dE/d[P, A, D] and verify expected directional gradients."""

    def test_pleasure_sensitivity(self, policy: ExpressionPolicy) -> None:
        low_p = policy.compute(make_pad(-0.8, 0.0, 0.0))
        high_p = policy.compute(make_pad(+0.8, 0.0, 0.0))

        assert high_p.facial.smile > low_p.facial.smile
        assert low_p.facial.frown > high_p.facial.frown
        assert high_p.voice.pitch_shift_hz > low_p.voice.pitch_shift_hz
        assert low_p.text.formality_score > high_p.text.formality_score

    def test_arousal_sensitivity(self, policy: ExpressionPolicy) -> None:
        low_a = policy.compute(make_pad(0.0, -0.8, 0.0))
        high_a = policy.compute(make_pad(0.0, +0.8, 0.0))

        assert high_a.voice.speech_rate_pct > low_a.voice.speech_rate_pct
        assert high_a.facial.eye_open > low_a.facial.eye_open

    def test_dominance_sensitivity(self, policy: ExpressionPolicy) -> None:
        low_d = policy.compute(make_pad(0.0, 0.0, -0.8))
        high_d = policy.compute(make_pad(0.0, 0.0, +0.8))

        assert high_d.voice.volume_pct > low_d.voice.volume_pct
        assert high_d.posture_gaze.head_tilt_deg < low_d.posture_gaze.head_tilt_deg

    def test_blush_threshold_nonlinearity(self, policy: ExpressionPolicy) -> None:
        below = policy.compute(make_pad(0.10, 0.0, 0.0))
        above = policy.compute(make_pad(0.50, 0.0, 0.0))

        assert below.facial.blush == 0.0
        assert above.facial.blush > 0.20


# ==============================================================================
# E-EXP-3: Temporal Coherence & Smoothing
# ==============================================================================


class TestE_EXP_3_TemporalCoherence:
    """Compare discrete step transitions against smoothed trajectories; verify jitter dampening."""

    def test_step_transition_smoothing(self, policy: ExpressionPolicy) -> None:
        init_pad = make_pad(-0.8, -0.5, -0.5)
        target_pad = make_pad(+0.8, +0.5, +0.5)

        raw_target = policy.compute(target_pad)

        curr = policy.compute(init_pad)
        trajectory: List[ExpressionState] = [curr]

        for _ in range(10):
            curr = policy.compute(target_pad, prev_state=curr)
            trajectory.append(curr)

        smiles = [s.facial.smile for s in trajectory]
        for i in range(1, len(smiles)):
            assert smiles[i] >= smiles[i - 1], f"Non-monotonic trajectory at step {i}"

        assert smiles[1] < raw_target.facial.smile
        assert math.isclose(smiles[-1], raw_target.facial.smile, abs_tol=0.10)


# ==============================================================================
# E-EXP-4: Semantic Preservation (Hard Requirement)
# ==============================================================================


class TestE_EXP_4_SemanticPreservation:
    """Verify that varying affect across 4 diverse regimes produces 100% semantic preservation."""

    def test_across_four_affective_regimes(
        self, policy: ExpressionPolicy, sample_intent: SemanticIntent
    ) -> None:
        regimes = {
            "warm_philia": make_pad(+0.60, -0.10, +0.10),
            "neutral_alert": make_pad(0.00, +0.50, 0.00),
            "melancholic_subdued": make_pad(-0.60, -0.40, -0.30),
            "agitated_high_tension": make_pad(-0.40, +0.70, +0.50),
        }

        evaluator = SemanticEvaluator()

        for name, pad in regimes.items():
            expr_state = policy.compute(pad)
            rendered = policy.render_surface_text(sample_intent, expr_state.text)

            validation = evaluator.evaluate(sample_intent, rendered)
            assert validation.is_preserved, (
                f"Regime '{name}' corrupted semantics in text: '{rendered}'. "
                f"Errors: {validation.entity_errors}, {validation.numeric_errors}, "
                f"Polarity inverted: {validation.polarity_inverted}"
            )
            assert not validation.polarity_inverted
            assert validation.proposition_preserved


# ==============================================================================
# E-EXP-5: Modality Specificity
# ==============================================================================


class TestE_EXP_5_ModalitySpecificity:
    """Verify that specific affect dimensions preferentially govern specific modalities."""

    def test_pleasure_vs_arousal_cross_channels(self, policy: ExpressionPolicy) -> None:
        p_base = policy.compute(make_pad(0.0, 0.0, 0.0))
        p_high = policy.compute(make_pad(0.8, 0.0, 0.0))
        delta_p_smile = abs(p_high.facial.smile - p_base.facial.smile)
        delta_p_rate = abs(p_high.voice.speech_rate_pct - p_base.voice.speech_rate_pct)

        a_high = policy.compute(make_pad(0.0, 0.8, 0.0))
        delta_a_smile = abs(a_high.facial.smile - p_base.facial.smile)
        delta_a_rate = abs(a_high.voice.speech_rate_pct - p_base.voice.speech_rate_pct)

        assert delta_p_smile > delta_p_rate
        assert delta_a_rate > delta_a_smile


# ==============================================================================
# E-EXP-6: Cross-Modality Consistency
# ==============================================================================


class TestE_EXP_6_CrossModalityConsistency:
    """Evaluate cross-modal coherence index and detect artificial contradictory states."""

    @staticmethod
    def compute_cross_modal_agreement(state: ExpressionState) -> float:
        """
        Predefined experimental criterion:
        Computes alignment index A_modal in [0, 1] across text, voice, and facial channels.
        Warm text (low formality) should align with smile (face) and pitch rise (voice).
        """
        text_valence = 1.0 - state.text.formality_score
        face_valence = (state.facial.smile - state.facial.frown + 1.0) / 2.0
        voice_valence = (state.voice.pitch_shift_hz / 30.0 + 1.0) / 2.0

        valences = [text_valence, face_valence, voice_valence]
        variance = float(np.var(valences))
        agreement = max(0.0, 1.0 - 4.0 * variance)
        return float(agreement)

    def test_coherent_state_satisfies_predefined_threshold(self, policy: ExpressionPolicy) -> None:
        state_pos = policy.compute(make_pad(0.7, 0.1, 0.1))
        agree_pos = self.compute_cross_modal_agreement(state_pos)
        assert agree_pos >= 0.85, f"Coherent state failed predefined agreement threshold: {agree_pos:.3f}"

        state_neg = policy.compute(make_pad(-0.7, 0.1, 0.1))
        agree_neg = self.compute_cross_modal_agreement(state_neg)
        assert agree_neg >= 0.85, f"Coherent negative state failed agreement: {agree_neg:.3f}"

    def test_detects_engineered_contradiction(self, policy: ExpressionPolicy) -> None:
        contradictory = ExpressionState(
            text=TextStyle(formality_score=0.95),
            facial=FacialExpression(smile=0.90, frown=0.0),
            voice=VoiceProsody(pitch_shift_hz=-25.0),
        )
        agreement = self.compute_cross_modal_agreement(contradictory)
        assert agreement < 0.40, f"Failed to detect severe contradiction: {agreement:.3f}"


# ==============================================================================
# E-EXP-7: Ablation A: Affect OFF
# ==============================================================================


class TestE_EXP_7_AblationA_AffectOFF:
    """
    Disable affect conditioning; verify expression collapses to deterministic
    actuator neutral baseline WITHOUT altering Core Philia.
    """

    def test_affect_off_collapses_to_actuator_baseline(self, policy: ExpressionPolicy) -> None:
        baseline = policy.get_neutral_actuator_baseline()

        extreme_pad = make_pad(-0.9, 0.9, -0.8)
        state_off = policy.compute(extreme_pad, affect_enabled=False)

        assert np.allclose(state_off.to_vector(), baseline.to_vector())

        core = EmotionCore(EmotionConfig())
        philia = core.get_pad_state()
        assert math.isclose(philia.pleasure, 0.25, abs_tol=1e-5)
        assert math.isclose(philia.arousal, -0.05, abs_tol=1e-5)
        assert math.isclose(philia.dominance, 0.05, abs_tol=1e-5)


# ==============================================================================
# E-EXP-8: Ablation B: Expression OFF
# ==============================================================================


class TestE_EXP_8_AblationB_ExpressionOFF:
    """
    Disable expression actuator while affect is active; verify internal affect
    (Layer 2 ODE and somatic markers) remains 100% unchanged (unidirectional).
    """

    def test_zero_feedback_to_internal_affect(self, policy: ExpressionPolicy) -> None:
        core = EmotionCore(EmotionConfig())
        stimulus = np.array([0.7, -0.4, 0.5, 0.0] * 4, dtype=np.float64)

        core.push_stimulus(stimulus)
        pad_before = core.step_once()
        h_before = core._h.copy()

        # Actuator runs outside core
        _ = policy.compute(pad_before)

        h_after = core._h.copy()
        pad_after = core.get_pad_state()

        assert np.allclose(h_before, h_after)
        assert math.isclose(pad_before.pleasure, pad_after.pleasure)
        assert math.isclose(pad_before.arousal, pad_after.arousal)
        assert math.isclose(pad_before.dominance, pad_after.dominance)


# ==============================================================================
# E-EXP-9 to E-EXP-11: Single-Modality Ablations C, D, E
# ==============================================================================


class TestE_EXP_9_to_11_SingleModalityAblations:
    """Verify each modality can be independently enabled or disabled."""

    def test_ablation_c_text_only(self, policy: ExpressionPolicy) -> None:
        pad = make_pad(0.7, 0.5, 0.3)
        state = policy.compute(pad, text_enabled=True, voice_enabled=False, avatar_enabled=False)
        neutral = policy.get_neutral_actuator_baseline()

        assert state.text.temperature_mod != neutral.text.temperature_mod
        assert state.voice == neutral.voice
        assert state.facial == neutral.facial
        assert state.posture_gaze == neutral.posture_gaze

    def test_ablation_d_voice_only(self, policy: ExpressionPolicy) -> None:
        pad = make_pad(0.7, 0.5, 0.3)
        state = policy.compute(pad, text_enabled=False, voice_enabled=True, avatar_enabled=False)
        neutral = policy.get_neutral_actuator_baseline()

        assert state.voice.pitch_shift_hz != neutral.voice.pitch_shift_hz
        assert state.text == neutral.text
        assert state.facial == neutral.facial

    def test_ablation_e_avatar_only(self, policy: ExpressionPolicy) -> None:
        pad = make_pad(0.7, 0.5, 0.3)
        state = policy.compute(pad, text_enabled=False, voice_enabled=False, avatar_enabled=True)
        neutral = policy.get_neutral_actuator_baseline()

        assert state.facial.smile != neutral.facial.smile
        assert state.text == neutral.text
        assert state.voice == neutral.voice


# ==============================================================================
# E-EXP-12: Ablation F: Multimodal Synergy & Policy Latency
# ==============================================================================


class TestE_EXP_12_AblationF_MultimodalSynergy:
    """
    Enable all modalities simultaneously; measure coherence, policy computation latency,
    parameter stability, and multi-channel synchronization over 50 steps.
    """

    def test_multimodal_synergy_and_policy_latency(self, policy: ExpressionPolicy) -> None:
        rng = np.random.RandomState(42)
        curr_state = policy.get_neutral_actuator_baseline()

        latencies_ms: List[float] = []
        agreements: List[float] = []

        for step in range(50):
            p = float(rng.uniform(-0.8, 0.8))
            a = float(rng.uniform(-0.6, 0.6))
            d = float(rng.uniform(-0.5, 0.5))
            pad = make_pad(p, a, d)

            t_start = time.perf_counter()
            curr_state = policy.compute(pad, prev_state=curr_state)
            t_elapsed_ms = (time.perf_counter() - t_start) * 1000.0
            latencies_ms.append(t_elapsed_ms)

            assert curr_state.is_bounded()
            assert not np.isnan(curr_state.to_vector()).any()

            agree = TestE_EXP_6_CrossModalityConsistency.compute_cross_modal_agreement(curr_state)
            agreements.append(agree)

        # Predefined Experimental Criteria Evaluation:
        # 1. Policy computation latency <= 5.0 ms (distinct from full multi-second TTS/LLM pipeline)
        mean_latency = float(np.mean(latencies_ms))
        max_latency = float(np.max(latencies_ms))
        assert mean_latency <= 1.0, f"Mean policy latency {mean_latency:.3f}ms exceeded 1.0ms"
        assert max_latency <= 5.0, f"Max policy latency {max_latency:.3f}ms exceeded predefined 5.0ms threshold"

        # 2. Average cross-modal coherence >= 0.85
        mean_coherence = float(np.mean(agreements))
        assert mean_coherence >= 0.85, f"Mean coherence {mean_coherence:.3f} fell below 0.85"


# ==============================================================================
# LLM & Relationship Boundary Controls
# ==============================================================================


class TestLLMAndRelationshipBoundaryControls:
    """Verify expression is an actuator policy effect and respect Philia invariants."""

    def test_relationship_conditioning_does_not_corrupt_philia(
        self, policy: ExpressionPolicy
    ) -> None:
        pad = make_pad(0.25, -0.05, 0.05)  # Philia baseline
        high_rel = {"trust": 0.90, "closeness": 0.80}

        state = policy.compute(pad, relationship=high_rel)

        assert state.text.formality_score < 0.40
        assert state.semantic_safe is True

    def test_llm_boundary_conditions(self, policy: ExpressionPolicy, sample_intent: SemanticIntent) -> None:
        """
        Condition C vs D: Evaluates deterministic template rendering vs fixed decoding.
        Verifies that style changes alter lexical framing without mutating core proposition.
        """
        warm_style = TextStyle(formality_score=0.20)
        formal_style = TextStyle(formality_score=0.85)

        text_warm = policy.render_surface_text(sample_intent, warm_style)
        text_formal = policy.render_surface_text(sample_intent, formal_style)

        assert text_warm != text_formal

        evaluator = SemanticEvaluator()
        v_warm = evaluator.evaluate(sample_intent, text_warm)
        v_formal = evaluator.evaluate(sample_intent, text_formal)

        assert v_warm.is_preserved and v_formal.is_preserved
        assert v_warm.proposition_preserved and v_formal.proposition_preserved
