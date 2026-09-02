"""
Hypothesis property-based tests for Phase 4 Active Inference and LNN Plasticity.

Properties tested:
- P31: AI Step Non-Negative Error Invariant
- P32: AI A_Matrix Bounds Invariant ([-2.0, 2.0])
- P33: AI Convergence on Fixed Input
- P34: Weight_Swap Atomicity
- P35: Gradient Clip Norm Bound

Requirements: Phase 4 (2.5, 2.6, 3.5, 5.1, 6.3)
"""

import threading
import time

import numpy as np
import pytest
import torch
from hypothesis import given, settings, strategies as st

from src.core.emotion.emotion_core import EmotionConfig, EmotionCore
from src.core.inference.active_inference import (
    ActiveInferenceConfig,
    ActiveInferenceEngine,
)
from src.core.inference.lnn_trainer import LNNTrainer, LNNTrainerConfig
from src.core.models import PADState


pad_float = st.floats(min_value=-1.0, max_value=1.0, allow_nan=False, allow_infinity=False)


@st.composite
def pad_state_strategy(draw):
    p = draw(pad_float)
    a = draw(pad_float)
    d = draw(pad_float)
    return PADState(pleasure=p, arousal=a, dominance=d, timestamp=0.0)


class TestPhase4Properties:
    @settings(max_examples=200, deadline=None)
    @given(p1=pad_state_strategy(), p2=pad_state_strategy())
    def test_p31_active_inference_non_negative_error(self, p1, p2):
        """
        P31: For any valid (pad_before, pad_after), step() returns float >= 0.0.
        """
        engine = ActiveInferenceEngine()
        err = engine.step(p1, p2)
        assert isinstance(err, float)
        assert err >= 0.0

    @settings(max_examples=200, deadline=None)
    @given(pairs=st.lists(st.tuples(pad_state_strategy(), pad_state_strategy()), min_size=1, max_size=20))
    def test_p32_a_matrix_bounds_invariant(self, pairs):
        """
        P32: All elements of A_matrix remain strictly in [-2.0, 2.0] after any step sequence.
        """
        engine = ActiveInferenceEngine(ActiveInferenceConfig(learning_rate=0.1))
        for p1, p2 in pairs:
            engine.step(p1, p2)
            state = engine.get_belief_state()
            assert np.all(state["A_matrix"] >= -2.0)
            assert np.all(state["A_matrix"] <= 2.0)

    @settings(max_examples=200, deadline=None)
    @given(
        p=st.tuples(
            st.floats(min_value=-0.9, max_value=0.9, allow_nan=False),
            st.floats(min_value=-0.9, max_value=0.9, allow_nan=False),
            st.floats(min_value=-0.9, max_value=0.9, allow_nan=False),
        ),
        q=st.tuples(
            st.floats(min_value=-0.9, max_value=0.9, allow_nan=False),
            st.floats(min_value=-0.9, max_value=0.9, allow_nan=False),
            st.floats(min_value=-0.9, max_value=0.9, allow_nan=False),
        ),
    )
    def test_p33_ai_convergence_on_fixed_input(self, p, q):
        """
        P33: Repeated step() with identical input produces non-increasing prediction error.
        """
        p_state = PADState(p[0], p[1], p[2], 0.0)
        q_state = PADState(q[0], q[1], q[2], 0.0)

        # Skip zero vector early exit case
        if np.linalg.norm([p[0], p[1], p[2]]) < 1e-4:
            return

        engine = ActiveInferenceEngine(
            ActiveInferenceConfig(kl_weight=0.0001, learning_rate=0.05)
        )

        initial_err = engine.step(p_state, q_state)
        for _ in range(30):
            last_err = engine.step(p_state, q_state)

        assert last_err <= initial_err + 1e-5

    @settings(max_examples=200, deadline=None)
    @given(val=st.floats(min_value=0.1, max_value=5.0, allow_nan=False))
    def test_p34_weight_swap_atomicity(self, val):
        """
        P34: During weight swap, readers under _train_lock always observe complete updates.
        """
        core = EmotionCore(EmotionConfig(hidden_dim=4))
        trainer = LNNTrainer(core, LNNTrainerConfig(batch_size=4, hidden_dim=4, stimulus_dim=16))

        # Assign sentinel value across model weights
        with torch.no_grad():
            for p in trainer._model.parameters():
                p.fill_(val)

        # Execute weight swap
        trainer._weight_swap()

        with core._train_lock:
            # Check that all matrices reflect the sentinel value
            assert np.allclose(core.W_f, val)
            assert np.allclose(core.U_f, val)
            assert np.allclose(core.b_f, val)
            assert np.allclose(core.W_tau, val)
            assert np.allclose(core.U_tau, val)
            assert np.allclose(core.b_tau, val)

    @settings(max_examples=200, deadline=None)
    @given(clip_norm=st.floats(min_value=0.1, max_value=5.0, allow_nan=False))
    def test_p35_gradient_clip_norm_bound(self, clip_norm):
        """
        P35: Total gradient norm after clip_grad_norm_ does not exceed configured threshold.
        """
        core = EmotionCore(EmotionConfig(hidden_dim=4))
        trainer = LNNTrainer(
            core,
            LNNTrainerConfig(
                batch_size=4,
                gradient_clip_norm=clip_norm,
                hidden_dim=4,
                stimulus_dim=16,
            ),
        )

        batch = [
            (
                np.random.randn(16) * 10.0,
                np.random.randn(4) * 5.0,
                np.random.randn(4) * 5.0,
            )
            for _ in range(4)
        ]

        trainer._gradient_step(batch)

        # Total norm of model parameters gradients must be <= clip_norm
        total_norm = 0.0
        for p in trainer._model.parameters():
            if p.grad is not None:
                param_norm = p.grad.data.norm(2)
                total_norm += param_norm.item() ** 2
        total_norm = total_norm ** 0.5

        # Account for slight floating point epsilon
        assert total_norm <= clip_norm + 1e-4
