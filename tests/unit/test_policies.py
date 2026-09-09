"""
Unit tests for Phase 9 Cognitive Policy Objects (policies.py).

Requirements: Phase 9 (ADR-015, ADR-017, ADR-020, PHASE_9_ARCHITECTURE_GATE.md §§ 11, 12).
"""

from dataclasses import FrozenInstanceError
import numpy as np
import pytest

from src.core.models import BehavioralConstraints, PADState, SomaticMarkers
from src.core.orchestrator.policies import (
    CognitiveTurnResult,
    GenerationPolicy,
    PlasticityPolicy,
    SurpriseModulationPolicy,
)


class TestSurpriseModulationPolicy:
    def test_default_initialization(self):
        policy = SurpriseModulationPolicy()
        assert policy.alpha_cognitive_load == pytest.approx(0.25)
        assert policy.tension_threshold == pytest.approx(0.40)
        assert policy.alpha_tension == pytest.approx(0.35)
        assert policy.deliberative_surprise_threshold == pytest.approx(0.60)
        assert policy.deliberative_tension_threshold == pytest.approx(0.70)

    def test_parameter_validation_bounds(self):
        with pytest.raises(ValueError):
            SurpriseModulationPolicy(alpha_cognitive_load=-0.1)
        with pytest.raises(ValueError):
            SurpriseModulationPolicy(tension_threshold=1.5)
        with pytest.raises(ValueError):
            SurpriseModulationPolicy(alpha_tension=-0.5)
        with pytest.raises(ValueError):
            SurpriseModulationPolicy(deliberative_surprise_threshold=2.5)

    def test_modulate_somatic_zero_surprise(self):
        policy = SurpriseModulationPolicy()
        base = SomaticMarkers(stability=0.8, cognitive_load=0.2, energy=0.9, tension=0.1)
        modulated = policy.modulate_somatic(base, surprise=0.0)

        assert modulated.stability == pytest.approx(0.8)
        assert modulated.energy == pytest.approx(0.9)
        assert modulated.cognitive_load == pytest.approx(0.2)
        assert modulated.tension == pytest.approx(0.1)

    def test_modulate_somatic_sub_threshold_surprise(self):
        policy = SurpriseModulationPolicy(tension_threshold=0.40, alpha_cognitive_load=0.25)
        base = SomaticMarkers(stability=0.8, cognitive_load=0.2, energy=0.9, tension=0.1)
        # surprise 0.30 is below tension_threshold 0.40
        modulated = policy.modulate_somatic(base, surprise=0.30)

        assert modulated.cognitive_load == pytest.approx(0.2 + 0.25 * 0.30)
        # Tension should not increase since surprise <= 0.40
        assert modulated.tension == pytest.approx(0.1)
        assert modulated.stability == pytest.approx(0.8)
        assert modulated.energy == pytest.approx(0.9)

    def test_modulate_somatic_high_surprise_and_clamping(self):
        policy = SurpriseModulationPolicy(
            alpha_cognitive_load=0.5,
            tension_threshold=0.40,
            alpha_tension=0.5,
        )
        base = SomaticMarkers(stability=0.5, cognitive_load=0.8, energy=0.7, tension=0.8)
        modulated = policy.modulate_somatic(base, surprise=1.0)

        # 0.8 + 0.5 * 1.0 = 1.3 -> clamped to 1.0
        assert modulated.cognitive_load == 1.0
        # 0.8 + 0.5 * (1.0 - 0.4) = 0.8 + 0.3 = 1.1 -> clamped to 1.0
        assert modulated.tension == 1.0
        assert modulated.energy == pytest.approx(0.7)
        assert modulated.stability == pytest.approx(0.5)

    def test_is_deliberative(self):
        policy = SurpriseModulationPolicy(
            deliberative_surprise_threshold=0.60,
            deliberative_tension_threshold=0.70,
        )
        assert not policy.is_deliberative(surprise=0.3, tension=0.4)
        assert policy.is_deliberative(surprise=0.65, tension=0.2)
        assert policy.is_deliberative(surprise=0.2, tension=0.75)
        assert policy.is_deliberative(surprise=0.8, tension=0.8)


class TestPlasticityPolicy:
    def test_default_initialization(self):
        policy = PlasticityPolicy()
        assert policy.salience_tag_threshold == pytest.approx(0.35)
        assert policy.consolidation_idle_timeout_s == pytest.approx(45.0)
        assert policy.min_consolidation_batch_size == 4
        assert policy.max_buffer_overflow_threshold == 8

    def test_parameter_validation(self):
        with pytest.raises(ValueError):
            PlasticityPolicy(salience_tag_threshold=-0.1)
        with pytest.raises(ValueError):
            PlasticityPolicy(consolidation_idle_timeout_s=0.0)
        with pytest.raises(ValueError):
            PlasticityPolicy(min_consolidation_batch_size=0)
        with pytest.raises(ValueError):
            PlasticityPolicy(max_buffer_overflow_threshold=2, min_consolidation_batch_size=5)

    def test_should_tag(self):
        policy = PlasticityPolicy(salience_tag_threshold=0.35)
        assert not policy.should_tag(0.20)
        assert not policy.should_tag(0.349)
        assert policy.should_tag(0.35)
        assert policy.should_tag(0.80)


class TestGenerationPolicy:
    def test_fatigued_policy(self):
        p = GenerationPolicy.fatigued()
        assert p.mode == "fatigued"
        assert p.reasoning_depth == 0
        assert p.scaffolding_steps == 0
        assert p.token_expansion_factor < 1.0

    def test_reflexive_policy(self):
        p = GenerationPolicy.reflexive()
        assert p.mode == "reflexive"
        assert p.reasoning_depth == 1
        assert p.scaffolding_steps == 1
        assert p.token_expansion_factor == 1.0

    def test_deliberative_policy(self):
        p = GenerationPolicy.deliberative()
        assert p.mode == "deliberative"
        assert p.reasoning_depth == 2
        assert p.scaffolding_steps == 3
        assert p.token_expansion_factor > 1.0

    def test_selection_priority_fatigued_trumps_deliberative(self):
        # Even with high surprise, depleted energy must choose fatigued
        surprise_policy = SurpriseModulationPolicy()
        markers = SomaticMarkers(stability=0.5, cognitive_load=0.9, energy=0.15, tension=0.9)
        selected = GenerationPolicy.select(markers, surprise=1.2, surprise_policy=surprise_policy)
        assert selected.mode == "fatigued"

    def test_selection_priority_deliberative(self):
        surprise_policy = SurpriseModulationPolicy()
        # High surprise with normal energy
        markers = SomaticMarkers(stability=0.8, cognitive_load=0.5, energy=0.8, tension=0.2)
        selected = GenerationPolicy.select(markers, surprise=0.75, surprise_policy=surprise_policy)
        assert selected.mode == "deliberative"

        # High tension with normal energy
        markers_tension = SomaticMarkers(stability=0.8, cognitive_load=0.5, energy=0.8, tension=0.75)
        selected_tension = GenerationPolicy.select(markers_tension, surprise=0.2, surprise_policy=surprise_policy)
        assert selected_tension.mode == "deliberative"

    def test_selection_priority_reflexive(self):
        surprise_policy = SurpriseModulationPolicy()
        markers = SomaticMarkers(stability=0.8, cognitive_load=0.2, energy=0.85, tension=0.1)
        selected = GenerationPolicy.select(markers, surprise=0.2, surprise_policy=surprise_policy)
        assert selected.mode == "reflexive"

    def test_apply_to_constraints_fatigued(self):
        p = GenerationPolicy.fatigued()
        base = BehavioralConstraints(max_tokens=150, temperature=0.7, latency_ms=100, reasoning_depth=1)
        adjusted = p.apply_to_constraints(base)
        assert adjusted.max_tokens < 150
        assert adjusted.reasoning_depth == 0
        assert adjusted.latency_ms == 100
        assert adjusted.temperature > 0.7

    def test_apply_to_constraints_deliberative(self):
        p = GenerationPolicy.deliberative()
        base = BehavioralConstraints(max_tokens=150, temperature=0.7, latency_ms=100, reasoning_depth=1)
        adjusted = p.apply_to_constraints(base)
        assert adjusted.max_tokens > 150
        assert adjusted.reasoning_depth == 2
        assert adjusted.latency_ms == 100
        assert adjusted.temperature < 0.7


class TestCognitiveTurnResult:
    def test_immutability(self):
        pad_init = PADState(0.25, -0.05, 0.05, 0.0)
        pad_fin = PADState(0.30, 0.00, 0.08, 0.1)
        stim = np.zeros(16, dtype=np.float32)
        somatic = SomaticMarkers(0.8, 0.2, 0.9, 0.1)
        constraints = BehavioralConstraints(150, 0.7, 0, 1)
        policy = GenerationPolicy.reflexive()

        result = CognitiveTurnResult(
            call_id="call-123",
            response_text="Hello friend",
            pad_initial=pad_init,
            pad_final=pad_fin,
            stimulus=stim,
            prediction_error=0.12,
            somatic=somatic,
            constraints=constraints,
            generation_policy=policy,
            echo_vector=None,
            trace_stored=True,
            experience_queued=False,
            execution_time_s=0.045,
        )

        assert result.call_id == "call-123"
        assert result.response_text == "Hello friend"
        assert result.prediction_error == 0.12
        assert result.generation_policy.mode == "reflexive"

        with pytest.raises(FrozenInstanceError):
            result.response_text = "mutated"
