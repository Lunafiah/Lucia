"""
Unit tests for ActiveInferenceEngine.

Requirements: Phase 4 (1.1–1.5, 2.1–2.8)
"""

import numpy as np
import pytest

from src.core.inference.active_inference import (
    ActiveInferenceConfig,
    ActiveInferenceEngine,
)
from src.core.models import PADState


class TestActiveInferenceConfig:
    def test_valid_config(self):
        cfg = ActiveInferenceConfig(kl_weight=0.05, learning_rate=0.01)
        assert cfg.kl_weight == 0.05
        assert cfg.learning_rate == 0.01

    def test_invalid_kl_weight_raises(self):
        with pytest.raises(ValueError, match="kl_weight"):
            ActiveInferenceConfig(kl_weight=-0.01)

        with pytest.raises(ValueError, match="kl_weight"):
            ActiveInferenceConfig(kl_weight=1.1)

    def test_invalid_learning_rate_raises(self):
        with pytest.raises(ValueError, match="learning_rate"):
            ActiveInferenceConfig(learning_rate=0.0)

        with pytest.raises(ValueError, match="learning_rate"):
            ActiveInferenceConfig(learning_rate=1.5)


class TestActiveInferenceEngine:
    def test_initial_belief_state_is_identity(self):
        engine = ActiveInferenceEngine()
        state = engine.get_belief_state()
        np.testing.assert_array_equal(state["A_matrix"], np.eye(3))
        np.testing.assert_array_equal(state["b_vector"], np.zeros(3))

    def test_out_of_bounds_pad_raises_without_mutation(self):
        engine = ActiveInferenceEngine()
        invalid_pad = PADState(1.5, 0.0, 0.0, 0.0)
        valid_pad = PADState(0.5, 0.0, 0.0, 0.0)

        with pytest.raises(ValueError, match="pad_before.pleasure"):
            engine.step(invalid_pad, valid_pad)

        # Belief state remains identity
        state = engine.get_belief_state()
        np.testing.assert_array_equal(state["A_matrix"], np.eye(3))

    def test_zero_pad_before_returns_zero_without_mutation(self):
        engine = ActiveInferenceEngine()
        zero_pad = PADState(0.0, 0.0, 0.0, 0.0)
        target_pad = PADState(0.5, 0.2, -0.1, 0.0)

        err = engine.step(zero_pad, target_pad)
        assert err == 0.0

        state = engine.get_belief_state()
        np.testing.assert_array_equal(state["A_matrix"], np.eye(3))

    def test_reset_restores_identity_and_zeros(self):
        engine = ActiveInferenceEngine(ActiveInferenceConfig(learning_rate=0.1))
        p1 = PADState(0.5, 0.5, 0.5, 0.0)
        p2 = PADState(-0.5, -0.5, -0.5, 0.0)

        engine.step(p1, p2)
        state_mutated = engine.get_belief_state()
        assert not np.array_equal(state_mutated["A_matrix"], np.eye(3))

        engine.reset()
        state_reset = engine.get_belief_state()
        np.testing.assert_array_equal(state_reset["A_matrix"], np.eye(3))
        np.testing.assert_array_equal(state_reset["b_vector"], np.zeros(3))

    def test_convergence_on_fixed_input_pair(self):
        engine = ActiveInferenceEngine(
            ActiveInferenceConfig(kl_weight=0.001, learning_rate=0.05)
        )
        p = PADState(0.6, -0.2, 0.4, 0.0)
        q = PADState(0.2, 0.5, -0.3, 0.0)

        initial_err = engine.step(p, q)
        last_err = initial_err

        for _ in range(100):
            last_err = engine.step(p, q)

        assert last_err < initial_err
        assert last_err < 0.05

    def test_a_matrix_bounds_clamped_to_range(self):
        engine = ActiveInferenceEngine(ActiveInferenceConfig(learning_rate=0.5))
        p = PADState(1.0, 1.0, 1.0, 0.0)
        q = PADState(-1.0, -1.0, -1.0, 0.0)

        for _ in range(50):
            engine.step(p, q)

        state = engine.get_belief_state()
        assert np.all(state["A_matrix"] >= -2.0)
        assert np.all(state["A_matrix"] <= 2.0)
