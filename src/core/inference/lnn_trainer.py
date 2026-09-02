"""
Online LNN Plasticity Trainer — Backpropagation-Through-ODE.

Performs asynchronous gradient descent on Liquid Neural Network weights
using torchdiffeq on a dedicated background CPU thread.

Requirements: Phase 4 (4.1–4.6, 5.1–5.6, 6.1–6.6)
"""

from __future__ import annotations

import logging
import threading
import time
from collections import deque
from dataclasses import dataclass
from typing import List, Optional, Tuple

import numpy as np
import torch
import torch.nn as nn
from torchdiffeq import odeint

from src.core.emotion.emotion_core import EmotionCore

logger = logging.getLogger(__name__)


@dataclass
class LNNTrainerConfig:
    """
    Configuration for LNNTrainer.

    Parameters
    ----------
    batch_size : int
        Number of experience tuples per training step. In [4, 128] or 0 (0 disables training).
    learning_rate : float
        AdamW learning rate. Must be in (0.0, 1.0]. Default: 1e-4.
    gradient_clip_norm : float
        Maximum gradient norm for gradient clipping. In (0.0, 10.0]. Default: 1.0.
    t_span : float
        ODE time span for RK4 trajectory solving. In (0.0, 1.0]. Default: 0.1.
    hidden_dim : int
        Dimensionality of LNN hidden state. >= 1. Default: 32.
    stimulus_dim : int
        Dimensionality of stimulus vector. >= 1. Default: 16.
    """

    batch_size: int = 16
    learning_rate: float = 1e-4
    gradient_clip_norm: float = 1.0
    t_span: float = 0.1
    hidden_dim: int = 32
    stimulus_dim: int = 16

    def __post_init__(self) -> None:
        if self.batch_size != 0 and not (4 <= self.batch_size <= 128):
            raise ValueError(
                f"LNNTrainerConfig.batch_size ({self.batch_size}) must be 0 or in [4, 128]"
            )
        if not (0.0 < self.learning_rate <= 1.0):
            raise ValueError(
                f"LNNTrainerConfig.learning_rate ({self.learning_rate}) must be in (0.0, 1.0]"
            )
        if not (0.0 < self.gradient_clip_norm <= 10.0):
            raise ValueError(
                f"LNNTrainerConfig.gradient_clip_norm ({self.gradient_clip_norm}) must be in (0.0, 10.0]"
            )
        if not (0.0 < self.t_span <= 1.0):
            raise ValueError(
                f"LNNTrainerConfig.t_span ({self.t_span}) must be in (0.0, 1.0]"
            )
        if self.hidden_dim < 1:
            raise ValueError(f"hidden_dim ({self.hidden_dim}) must be >= 1")
        if self.stimulus_dim < 1:
            raise ValueError(f"stimulus_dim ({self.stimulus_dim}) must be >= 1")


class _LNNModel(nn.Module):
    """
    Differentiable Liquid Time-Constant (LTC) neural ODE model for CPU training.
    """

    def __init__(
        self, emotion_core: EmotionCore, hidden_dim: int, stimulus_dim: int
    ) -> None:
        super().__init__()
        self.device = torch.device("cpu")

        # Initialise parameters from live EmotionCore weights
        self.W_f = nn.Parameter(
            torch.from_numpy(emotion_core.W_f.copy()).float().to(self.device)
        )
        self.U_f = nn.Parameter(
            torch.from_numpy(emotion_core.U_f.copy()).float().to(self.device)
        )
        self.b_f = nn.Parameter(
            torch.from_numpy(emotion_core.b_f.copy()).float().to(self.device)
        )

        self.W_tau = nn.Parameter(
            torch.from_numpy(emotion_core.W_tau.copy()).float().to(self.device)
        )
        self.U_tau = nn.Parameter(
            torch.from_numpy(emotion_core.U_tau.copy()).float().to(self.device)
        )
        self.b_tau = nn.Parameter(
            torch.from_numpy(emotion_core.b_tau.copy()).float().to(self.device)
        )

        self.W_proj = nn.Parameter(
            torch.from_numpy(emotion_core.W_proj.copy()).float().to(self.device)
        )
        self.b_proj = nn.Parameter(
            torch.from_numpy(emotion_core.b_proj.copy()).float().to(self.device)
        )

        self._x: Optional[torch.Tensor] = None

    def forward(self, t: torch.Tensor, h: torch.Tensor) -> torch.Tensor:
        """
        Evaluate LTC differential equation f(t, h).
        """
        h_c = torch.clamp(h, -1.0, 1.0)
        tau = torch.nn.functional.softplus(
            self.W_tau @ h_c + self.U_tau @ self._x + self.b_tau
        )
        f = torch.tanh(self.W_f @ h_c + self.U_f @ self._x + self.b_f)
        return (-h_c + f) / tau


class LNNTrainer:
    """
    Asynchronous trainer performing online backpropagation-through-ODE.
    """

    def __init__(
        self, emotion_core: EmotionCore, config: Optional[LNNTrainerConfig] = None
    ) -> None:
        if config is None:
            config = LNNTrainerConfig()
        config.__post_init__()
        self._config = config
        self._emotion_core = emotion_core

        self._training_active = config.batch_size > 0
        self._step_count: int = 0
        self._consecutive_bad_updates: int = 0

        self._buffer: deque = deque(
            maxlen=max(1, config.batch_size) if config.batch_size > 0 else 1
        )
        self._buffer_lock = threading.Lock()
        self._batch_ready = threading.Event()
        self._stop_event = threading.Event()

        # Thread synchronization
        self._train_lock = getattr(emotion_core, "_train_lock", threading.Lock())
        self._thread: Optional[threading.Thread] = None

        if self._training_active:
            self._model = _LNNModel(
                emotion_core, config.hidden_dim, config.stimulus_dim
            )
            self._optimizer = torch.optim.AdamW(
                self._model.parameters(), lr=config.learning_rate
            )
        else:
            self._model = None
            self._optimizer = None

    def push_sample(
        self, stimulus: np.ndarray, h_before: np.ndarray, h_after: np.ndarray
    ) -> None:
        """
        Record one interaction turn into the training ring buffer.
        """
        if not self._training_active or self._config.batch_size == 0:
            return

        with self._buffer_lock:
            self._buffer.append(
                (stimulus.copy(), h_before.copy(), h_after.copy())
            )
            if len(self._buffer) >= self._config.batch_size:
                self._batch_ready.set()

    def _gradient_step(
        self, batch: List[Tuple[np.ndarray, np.ndarray, np.ndarray]]
    ) -> None:
        """
        Execute one backpropagation-through-ODE step over the accumulated batch.
        """
        if not self._training_active or self._model is None or not batch:
            return

        self._optimizer.zero_grad()
        t_span = torch.tensor([0.0, self._config.t_span], dtype=torch.float32)

        total_loss = torch.tensor(0.0, dtype=torch.float32)

        for stimulus_np, h0_np, h_target_np in batch:
            stim_slice = stimulus_np[: self._config.stimulus_dim]
            if len(stim_slice) < self._config.stimulus_dim:
                pad_width = self._config.stimulus_dim - len(stim_slice)
                stim_slice = np.pad(stim_slice, (0, pad_width), "constant")

            self._model._x = torch.from_numpy(stim_slice).float()
            h0 = torch.from_numpy(h0_np).float()
            h_target = torch.from_numpy(h_target_np).float()

            trajectory = odeint(self._model, h0, t_span, method="rk4")
            h_pred = trajectory[-1]

            loss_sample = torch.nn.functional.mse_loss(h_pred, h_target)
            total_loss = total_loss + loss_sample

        total_loss = total_loss / len(batch)
        total_loss.backward()

        # Check for finite gradients
        all_finite = True
        for p in self._model.parameters():
            if p.grad is not None and not torch.all(torch.isfinite(p.grad)):
                all_finite = False
                break

        if all_finite:
            torch.nn.utils.clip_grad_norm_(
                self._model.parameters(), self._config.gradient_clip_norm
            )
            self._optimizer.step()
            self._step_count += 1
            self._consecutive_bad_updates = 0
            self._weight_swap()
        else:
            self._consecutive_bad_updates += 1
            logger.warning(
                "LNNTrainer: non-finite gradients encountered (bad_updates=%d)",
                self._consecutive_bad_updates,
            )
            if self._consecutive_bad_updates >= 5:
                self._training_active = False
                logger.error(
                    "LNNTrainer: disabled training due to 5 consecutive non-finite gradient steps"
                )

    def _weight_swap(self) -> None:
        """
        Atomically copy updated weights from PyTorch model to live EmotionCore.
        """
        if self._model is None:
            return

        with self._train_lock:
            self._emotion_core.W_f = (
                self._model.W_f.detach().numpy().astype(np.float64).copy()
            )
            self._emotion_core.U_f = (
                self._model.U_f.detach().numpy().astype(np.float64).copy()
            )
            self._emotion_core.b_f = (
                self._model.b_f.detach().numpy().astype(np.float64).copy()
            )
            self._emotion_core.W_tau = (
                self._model.W_tau.detach().numpy().astype(np.float64).copy()
            )
            self._emotion_core.U_tau = (
                self._model.U_tau.detach().numpy().astype(np.float64).copy()
            )
            self._emotion_core.b_tau = (
                self._model.b_tau.detach().numpy().astype(np.float64).copy()
            )
            self._emotion_core.W_proj = (
                self._model.W_proj.detach().numpy().astype(np.float64).copy()
            )
            self._emotion_core.b_proj = (
                self._model.b_proj.detach().numpy().astype(np.float64).copy()
            )

    def _train_loop_worker(self) -> None:
        """
        Background daemon loop processing full batches.
        """
        while not self._stop_event.is_set():
            self._batch_ready.wait(timeout=5.0)
            if self._stop_event.is_set():
                break

            self._batch_ready.clear()

            with self._buffer_lock:
                if len(self._buffer) >= self._config.batch_size:
                    batch = list(self._buffer)
                    self._buffer.clear()
                else:
                    batch = []

            if batch:
                try:
                    self._gradient_step(batch)
                except Exception:
                    logger.exception("LNNTrainer exception in _gradient_step")

    def start(self) -> None:
        """
        Start the background training thread.
        """
        if not self._training_active or self._config.batch_size == 0:
            return

        if self._thread is not None and self._thread.is_alive():
            return

        self._stop_event.clear()
        self._thread = threading.Thread(
            target=self._train_loop_worker,
            name="LNN-Trainer",
            daemon=True,
        )
        self._thread.start()

    def stop(self) -> None:
        """
        Stop the background training thread and wait for it to join.
        """
        self._stop_event.set()
        self._batch_ready.set()
        if self._thread is not None and self._thread.is_alive():
            self._thread.join(timeout=5.0)
        self._training_active = False

    def is_training_active(self) -> bool:
        """
        Return True if online training is active.
        """
        return self._training_active

    def training_step_count(self) -> int:
        """
        Return the number of completed gradient steps.
        """
        return self._step_count
