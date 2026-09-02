"""
Unit tests for LNNTrainer online plasticity system.

Requirements: Phase 4 (4.1–4.6, 5.1–5.6, 6.1–6.6)
"""

import time
from unittest.mock import MagicMock

import numpy as np
import pytest
import torch

from src.core.emotion.emotion_core import EmotionConfig, EmotionCore
from src.core.inference.lnn_trainer import (
    LNNTrainer,
    LNNTrainerConfig,
    _LNNModel,
)


@pytest.fixture
def emotion_core():
    core = EmotionCore(EmotionConfig(hidden_dim=8))
    return core


class TestLNNTrainerConfig:
    def test_valid_config(self):
        cfg = LNNTrainerConfig(batch_size=8, learning_rate=1e-3, gradient_clip_norm=2.0)
        assert cfg.batch_size == 8
        assert cfg.learning_rate == 1e-3

    def test_batch_size_zero_allowed(self):
        cfg = LNNTrainerConfig(batch_size=0)
        assert cfg.batch_size == 0

    def test_invalid_batch_size_raises(self):
        with pytest.raises(ValueError, match="batch_size"):
            LNNTrainerConfig(batch_size=3)

        with pytest.raises(ValueError, match="batch_size"):
            LNNTrainerConfig(batch_size=129)

    def test_invalid_learning_rate_raises(self):
        with pytest.raises(ValueError, match="learning_rate"):
            LNNTrainerConfig(learning_rate=0.0)

    def test_invalid_clip_norm_raises(self):
        with pytest.raises(ValueError, match="gradient_clip_norm"):
            LNNTrainerConfig(gradient_clip_norm=0.0)


class TestLNNTrainerExecution:
    def test_disabled_trainer_when_batch_size_zero(self, emotion_core):
        trainer = LNNTrainer(emotion_core, LNNTrainerConfig(batch_size=0))
        assert not trainer.is_training_active()

        # push_sample should be a clean no-op
        stim = np.zeros(16)
        h = np.zeros(8)
        trainer.push_sample(stim, h, h)
        assert len(trainer._buffer) == 0

    def test_start_and_stop_lifecycle(self, emotion_core):
        trainer = LNNTrainer(
            emotion_core, LNNTrainerConfig(batch_size=4, hidden_dim=8, stimulus_dim=16)
        )
        trainer.start()
        assert trainer.is_training_active()
        assert trainer._thread is not None and trainer._thread.is_alive()

        trainer.stop()
        assert not trainer.is_training_active()
        assert not trainer._thread.is_alive()

    def test_push_sample_and_training_step_execution(self, emotion_core):
        trainer = LNNTrainer(
            emotion_core,
            LNNTrainerConfig(
                batch_size=4,
                learning_rate=1e-2,
                hidden_dim=8,
                stimulus_dim=16,
                t_span=0.05,
            ),
        )
        trainer.start()

        # Record initial weights
        w_f_initial = emotion_core.W_f.copy()

        # Push 4 samples to trigger batch training
        for _ in range(4):
            stim = np.random.randn(16).astype(np.float64)
            h_before = np.random.uniform(-0.5, 0.5, size=8).astype(np.float64)
            h_after = np.random.uniform(-0.5, 0.5, size=8).astype(np.float64)
            trainer.push_sample(stim, h_before, h_after)

        # Wait up to 3 seconds for training step to process
        t0 = time.monotonic()
        while trainer.training_step_count() < 1 and time.monotonic() - t0 < 3.0:
            time.sleep(0.05)

        trainer.stop()

        assert trainer.training_step_count() >= 1
        # Weights should have updated via weight swap
        assert not np.array_equal(emotion_core.W_f, w_f_initial)

    def test_non_finite_gradient_deactivation(self, emotion_core):
        trainer = LNNTrainer(
            emotion_core, LNNTrainerConfig(batch_size=4, hidden_dim=8, stimulus_dim=16)
        )

        batch = [
            (np.zeros(16), np.zeros(8), np.zeros(8)) for _ in range(4)
        ]

        # Inject NaN gradients
        for p in trainer._model.parameters():
            p.grad = torch.full_like(p, float("nan"))

        # Run multiple gradient steps that fail
        with pytest.MonkeyPatch.context() as mp:
            # Force loss.backward to produce NaN
            def bad_backward(*args, **kwargs):
                for p in trainer._model.parameters():
                    p.grad = torch.full_like(p, float("nan"))

            mp.setattr(torch.Tensor, "backward", bad_backward)

            for _ in range(5):
                trainer._gradient_step(batch)

            assert not trainer.is_training_active()
