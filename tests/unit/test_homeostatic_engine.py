"""
Unit tests for HomeostaticEngine — somatic markers and behavioral constraints.
Requirements: 2.1–2.7, 3.1–3.12
"""

from __future__ import annotations

import time

import pytest

from src.core.config import HomeostaticConfig
from src.core.emotion.homeostatic_engine import HomeostaticEngine
from src.core.models import PADState, SomaticMarkers, BehavioralConstraints


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def make_pad(
    pleasure: float = 0.1,
    arousal: float = 0.0,
    dominance: float = 0.0,
) -> PADState:
    return PADState(pleasure=pleasure, arousal=arousal, dominance=dominance, timestamp=0.0)


def resting_pad() -> PADState:
    return make_pad(0.1, 0.0, 0.0)


def fresh_engine() -> HomeostaticEngine:
    """Always return a new engine with default config and full energy."""
    return HomeostaticEngine()


# ===========================================================================
# Somatic markers — Task 4.3
# ===========================================================================

class TestSomaticMarkersResting:
    """Requirement 2.7: resting baseline + 60 s idle → specific bounds."""

    def test_stability_ge_08(self):
        eng = fresh_engine()
        m = eng.compute_somatic_markers(resting_pad())
        assert m.stability >= 0.8, f"stability={m.stability}"

    def test_cognitive_load_le_02(self):
        eng = fresh_engine()
        m = eng.compute_somatic_markers(resting_pad())
        assert m.cognitive_load <= 0.2, f"cognitive_load={m.cognitive_load}"

    def test_energy_ge_08(self):
        eng = fresh_engine()
        m = eng.compute_somatic_markers(resting_pad())
        assert m.energy >= 0.8, f"energy={m.energy}"

    def test_tension_le_02(self):
        eng = fresh_engine()
        m = eng.compute_somatic_markers(resting_pad())
        assert m.tension <= 0.2, f"tension={m.tension}"

    def test_all_four_markers_present(self):
        eng = fresh_engine()
        m = eng.compute_somatic_markers(resting_pad())
        assert isinstance(m, SomaticMarkers)
        assert hasattr(m, "stability")
        assert hasattr(m, "cognitive_load")
        assert hasattr(m, "energy")
        assert hasattr(m, "tension")


class TestSomaticMarkersValence:
    """Requirement 2.5: tension computation with valence."""

    def test_valence_1_5_raises_value_error(self):
        eng = fresh_engine()
        with pytest.raises(ValueError, match="valence"):
            eng.compute_somatic_markers(resting_pad(), valence=1.5)

    def test_valence_minus_0_1_raises_value_error(self):
        eng = fresh_engine()
        with pytest.raises(ValueError):
            eng.compute_somatic_markers(resting_pad(), valence=-0.1)

    def test_valence_0_5_succeeds(self):
        eng = fresh_engine()
        m = eng.compute_somatic_markers(resting_pad(), valence=0.5)
        assert isinstance(m, SomaticMarkers)
        assert 0.0 <= m.tension <= 1.0

    def test_valence_0_0_boundary_valid(self):
        eng = fresh_engine()
        m = eng.compute_somatic_markers(resting_pad(), valence=0.0)
        assert 0.0 <= m.tension <= 1.0

    def test_valence_1_0_boundary_valid(self):
        eng = fresh_engine()
        m = eng.compute_somatic_markers(resting_pad(), valence=1.0)
        assert 0.0 <= m.tension <= 1.0

    def test_valence_none_tension_is_zero(self):
        eng = fresh_engine()
        m = eng.compute_somatic_markers(resting_pad(), valence=None)
        assert m.tension == 0.0

    def test_opposite_valence_gives_high_tension(self):
        # pleasure=0.1 maps to pleasure_01 ≈ 0.55, valence=0.0 → tension ≈ 0.55
        eng = fresh_engine()
        m = eng.compute_somatic_markers(make_pad(pleasure=0.8), valence=0.0)
        # pleasure_01 = (0.8+1)/2 = 0.9, valence=0.0, tension=|0.0 - 0.9|=0.9
        assert m.tension >= 0.8, f"Expected high tension, got {m.tension}"


class TestSomaticMarkersInvalidPAD:
    """Requirement 2.x: out-of-bounds PAD raises ValueError."""

    def test_pleasure_too_high_raises(self):
        eng = fresh_engine()
        bad = PADState(pleasure=1.1, arousal=0.0, dominance=0.0, timestamp=0.0)
        with pytest.raises(ValueError):
            eng.compute_somatic_markers(bad)

    def test_pleasure_too_low_raises(self):
        eng = fresh_engine()
        bad = PADState(pleasure=-1.1, arousal=0.0, dominance=0.0, timestamp=0.0)
        with pytest.raises(ValueError):
            eng.compute_somatic_markers(bad)

    def test_arousal_too_high_raises(self):
        eng = fresh_engine()
        bad = PADState(pleasure=0.0, arousal=1.5, dominance=0.0, timestamp=0.0)
        with pytest.raises(ValueError):
            eng.compute_somatic_markers(bad)

    def test_dominance_too_low_raises(self):
        eng = fresh_engine()
        bad = PADState(pleasure=0.0, arousal=0.0, dominance=-2.0, timestamp=0.0)
        with pytest.raises(ValueError):
            eng.compute_somatic_markers(bad)


class TestSomaticMarkersAllInBounds:
    """All returned marker values must be in [0.0, 1.0]."""

    @pytest.mark.parametrize("pleasure,arousal,dominance", [
        (-1.0, -1.0, -1.0),
        (1.0, 1.0, 1.0),
        (0.0, 0.0, 0.0),
        (0.5, 0.8, -0.3),
        (-0.7, 0.9, 0.1),
    ])
    def test_markers_in_range(self, pleasure, arousal, dominance):
        eng = fresh_engine()
        pad = make_pad(pleasure, arousal, dominance)
        m = eng.compute_somatic_markers(pad, valence=0.5)
        assert 0.0 <= m.stability <= 1.0, f"stability={m.stability}"
        assert 0.0 <= m.cognitive_load <= 1.0, f"cl={m.cognitive_load}"
        assert 0.0 <= m.energy <= 1.0, f"energy={m.energy}"
        assert 0.0 <= m.tension <= 1.0, f"tension={m.tension}"


class TestEnergyDepletion:
    """Requirement 2.4: energy depletes with inputs, recovers during idle."""

    def test_energy_depletes_with_inputs(self):
        eng = fresh_engine()
        initial = eng._energy
        for _ in range(5):
            eng.record_input()
        assert eng._energy < initial, "Energy should decrease after inputs"

    def test_energy_clamped_at_zero(self):
        eng = fresh_engine()
        for _ in range(30):
            eng.record_input()
        assert eng._energy >= 0.0, "Energy must not go below 0"


# ===========================================================================
# Behavioral constraints — Task 5.3
# ===========================================================================

def make_markers(
    stability: float = 0.9,
    cognitive_load: float = 0.1,
    energy: float = 0.9,
    tension: float = 0.05,
) -> SomaticMarkers:
    return SomaticMarkers(
        stability=stability,
        cognitive_load=cognitive_load,
        energy=energy,
        tension=tension,
    )


class TestConstraintsMaxTokens:
    """Requirements 3.2, 3.3."""

    def test_high_cognitive_load_gives_low_max_tokens(self):
        """Requirement 3.2: cognitive_load > 0.75 → max_tokens ≤ 80."""
        eng = fresh_engine()
        pad = make_pad(arousal=0.0)
        m = make_markers(cognitive_load=0.9, energy=0.2)
        c = eng.compute_behavioral_constraints(m, pad)
        assert c.max_tokens <= 80, f"max_tokens={c.max_tokens}"

    def test_low_cognitive_load_high_energy_gives_high_max_tokens(self):
        """Requirement 3.3: cognitive_load < 0.3 AND energy > 0.7 → max_tokens ≥ 300."""
        eng = fresh_engine()
        pad = make_pad(arousal=0.0)
        m = make_markers(cognitive_load=0.2, energy=0.8)
        c = eng.compute_behavioral_constraints(m, pad)
        assert c.max_tokens >= 300, f"max_tokens={c.max_tokens}"


class TestConstraintsTemperature:
    """Requirements 3.4, 3.5."""

    def test_high_arousal_gives_high_temperature(self):
        """Requirement 3.4: arousal > 0.7 → temperature > 0.85."""
        eng = fresh_engine()
        # PAD arousal=0.6 maps to arousal_01=0.8 > 0.7 threshold
        pad = make_pad(arousal=0.6)
        m = make_markers(stability=0.3)
        c = eng.compute_behavioral_constraints(m, pad)
        assert c.temperature > 0.85, f"temperature={c.temperature}"

    def test_low_arousal_high_stability_gives_low_temperature(self):
        """Requirement 3.5: arousal < 0.3 AND stability > 0.7 → temperature < 0.65."""
        eng = fresh_engine()
        # PAD arousal=-0.5 maps to arousal_01=0.25 < 0.3 threshold
        pad = make_pad(arousal=-0.5)
        m = make_markers(stability=0.85)
        c = eng.compute_behavioral_constraints(m, pad)
        assert c.temperature < 0.65, f"temperature={c.temperature}"


class TestConstraintsLatency:
    """Requirements 3.6, 3.7."""

    def test_very_high_load_low_energy_gives_latency(self):
        """Requirement 3.6: cognitive_load > 0.8 AND energy < 0.3 → latency_ms ≥ 400."""
        eng = fresh_engine()
        pad = make_pad(arousal=0.0)
        m = make_markers(cognitive_load=0.9, energy=0.2)
        c = eng.compute_behavioral_constraints(m, pad)
        assert c.latency_ms >= 400, f"latency_ms={c.latency_ms}"

    def test_high_energy_low_load_gives_zero_latency(self):
        """Requirement 3.7: energy > 0.7 AND cognitive_load < 0.4 → latency_ms = 0."""
        eng = fresh_engine()
        pad = make_pad(arousal=0.0)
        m = make_markers(cognitive_load=0.2, energy=0.8)
        c = eng.compute_behavioral_constraints(m, pad)
        assert c.latency_ms == 0, f"latency_ms={c.latency_ms}"


class TestConstraintsReasoningDepth:
    """Requirements 3.8, 3.9."""

    def test_very_low_energy_gives_zero_depth(self):
        """Requirement 3.8: energy ≤ 0.2 → reasoning_depth = 0."""
        eng = fresh_engine()
        pad = make_pad()
        m = make_markers(energy=0.05)
        c = eng.compute_behavioral_constraints(m, pad)
        assert c.reasoning_depth == 0, f"reasoning_depth={c.reasoning_depth}"

    def test_energy_exactly_02_gives_zero_depth(self):
        """Requirement 3.8: energy = 0.2 (inclusive) → reasoning_depth = 0."""
        eng = fresh_engine()
        pad = make_pad()
        m = make_markers(energy=0.2)
        c = eng.compute_behavioral_constraints(m, pad)
        assert c.reasoning_depth == 0, f"reasoning_depth={c.reasoning_depth}"

    def test_high_energy_low_load_gives_depth_3(self):
        """Requirement 3.9: energy > 0.7 AND cognitive_load < 0.4 → reasoning_depth = 3."""
        eng = fresh_engine()
        pad = make_pad(arousal=0.0)
        m = make_markers(cognitive_load=0.2, energy=0.8)
        c = eng.compute_behavioral_constraints(m, pad)
        assert c.reasoning_depth == 3, f"reasoning_depth={c.reasoning_depth}"

    def test_energy_and_latency_zero_simultaneously(self):
        """When energy > 0.7 AND cl < 0.4, both latency=0 and depth=3."""
        eng = fresh_engine()
        pad = make_pad(arousal=0.0)
        m = make_markers(cognitive_load=0.3, energy=0.8)
        c = eng.compute_behavioral_constraints(m, pad)
        assert c.latency_ms == 0
        assert c.reasoning_depth == 3


class TestConstraintsOutputRanges:
    """Requirement 3.1: all constraint values within documented ranges."""

    @pytest.mark.parametrize("cl,en,arousal,st", [
        (0.1, 0.9, 0.0, 0.9),   # relaxed
        (0.9, 0.1, 0.5, 0.3),   # stressed
        (0.5, 0.5, 0.0, 0.5),   # neutral
        (0.8, 0.25, 0.6, 0.4),  # high load
        (0.2, 0.85, -0.5, 0.8), # low load
    ])
    def test_constraints_in_documented_ranges(self, cl, en, arousal, st):
        eng = fresh_engine()
        pad = make_pad(arousal=arousal)
        m = make_markers(cognitive_load=cl, energy=en, stability=st)
        c = eng.compute_behavioral_constraints(m, pad)
        assert 1 <= c.max_tokens <= 2048, f"max_tokens={c.max_tokens}"
        assert 0.0 <= c.temperature <= 2.0, f"temperature={c.temperature}"
        assert 0 <= c.latency_ms <= 5000, f"latency_ms={c.latency_ms}"
        assert 0 <= c.reasoning_depth <= 3, f"reasoning_depth={c.reasoning_depth}"


class TestConstraintsInvalidPAD:
    """Requirement 3.12: out-of-bounds PAD raises ValueError."""

    def test_invalid_pad_raises_value_error(self):
        eng = fresh_engine()
        bad_pad = PADState(pleasure=1.5, arousal=0.0, dominance=0.0, timestamp=0.0)
        m = make_markers()
        with pytest.raises(ValueError):
            eng.compute_behavioral_constraints(m, bad_pad)

    def test_invalid_pad_returns_last_valid_if_available(self):
        """After a valid call, invalid PAD raises but last_constraints is set."""
        eng = fresh_engine()
        pad = make_pad()
        m = make_markers()
        # First call sets _last_constraints
        c1 = eng.compute_behavioral_constraints(m, pad)
        assert eng._last_constraints is not None

        # Now try invalid PAD
        bad_pad = PADState(pleasure=2.0, arousal=0.0, dominance=0.0, timestamp=0.0)
        with pytest.raises(ValueError):
            eng.compute_behavioral_constraints(m, bad_pad)
        # Last valid constraints should still be c1
        assert eng._last_constraints == c1

    def test_no_prior_constraints_returns_defaults_on_error(self):
        """First call with invalid PAD: _last_constraints is None → caller uses defaults."""
        eng = fresh_engine()
        assert eng._last_constraints is None
        bad_pad = PADState(pleasure=3.0, arousal=0.0, dominance=0.0, timestamp=0.0)
        m = make_markers()
        with pytest.raises(ValueError):
            eng.compute_behavioral_constraints(m, bad_pad)
        assert eng._last_constraints is None  # never set


class TestConstraintsDefaults:
    """Requirement 3.10: defaults when no threshold condition applies."""

    def test_defaults_when_no_threshold_active(self):
        """
        With cognitive_load = 0.5 (not < 0.3, not > 0.75),
        energy = 0.5 (not < 0.2, not > 0.7),
        arousal_01 = 0.5 (not < 0.3, not > 0.7):
        all default values should be returned.
        """
        eng = fresh_engine()
        pad = make_pad(arousal=0.0)  # arousal_01 = 0.5
        m = make_markers(cognitive_load=0.5, energy=0.5, stability=0.5)
        c = eng.compute_behavioral_constraints(m, pad)
        assert c.max_tokens == 150, f"expected default 150, got {c.max_tokens}"
        assert c.temperature == pytest.approx(0.75), f"expected 0.75, got {c.temperature}"
        assert c.latency_ms == 0, f"expected 0, got {c.latency_ms}"
        assert c.reasoning_depth == 1, f"expected 1, got {c.reasoning_depth}"
