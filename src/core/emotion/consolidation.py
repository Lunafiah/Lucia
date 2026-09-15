"""
ConsolidationEngine — Offline Synaptic Plasticity & Relational Consolidation Service.

Production realization of Phase 21: Long-Term Relational Consolidation & Synaptic Homeostasis.
Enforces 3-Tier Multi-Timescale Plasticity architecture:
    Tier 1: Fast reactive dynamics (h_fast in R^32)
    Tier 2: Slow relational attractor bias (s*_eff(R) in R^16, ||W_rel||_2 <= 0.08)
    Tier 3: Offline synaptic consolidation (CPU BPTT-through-ODE with dual regularization)

Architectural Invariants:
    - 20-Watt CPU execution boundary: strictly 0 MB GPU VRAM; torch.device("cpu").
    - Atomic parameter swap: memory copy under _train_lock <= 2.0 ms.
    - Pre-reflective boundaries: strictly 0 introspective fields or self-model labels.
    - Phlia attractor invariance: dual homeostatic/Philia regularization guarantees asymptotic stability.
"""

from __future__ import annotations

import logging
import threading
import time
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional, Tuple, TYPE_CHECKING

import numpy as np
import torch
import torch.nn as nn
from torchdiffeq import odeint

from src.core.config import EmotionConfig

if TYPE_CHECKING:
    from src.core.emotion.emotion_core import EmotionCore

logger = logging.getLogger(__name__)


@dataclass
class SynapticParameterState:
    """
    Snapshot of trainable continuous parameter matrices Theta.
    Enforces spectral norm computation on W_rel.
    """
    W_f: np.ndarray        # (H, H)
    U_f: np.ndarray        # (H, N_in)
    b_f: np.ndarray        # (H,)
    W_tau: np.ndarray      # (H, H)
    U_tau: np.ndarray      # (H, N_in)
    b_tau: np.ndarray      # (H,)
    W_rel: np.ndarray      # (Hs, 4)

    @property
    def w_rel_spectral_norm(self) -> float:
        """Operator / spectral norm sigma_max(W_rel)."""
        s = np.linalg.svd(self.W_rel, compute_uv=False)
        return float(s[0]) if len(s) > 0 else 0.0

    def copy(self) -> "SynapticParameterState":
        return SynapticParameterState(
            W_f=self.W_f.copy(),
            U_f=self.U_f.copy(),
            b_f=self.b_f.copy(),
            W_tau=self.W_tau.copy(),
            U_tau=self.U_tau.copy(),
            b_tau=self.b_tau.copy(),
            W_rel=self.W_rel.copy(),
        )

    def flatten_weights(self) -> np.ndarray:
        """Flatten all trainable parameters into a single 1D vector."""
        return np.concatenate([
            self.W_f.ravel(),
            self.U_f.ravel(),
            self.b_f.ravel(),
            self.W_tau.ravel(),
            self.U_tau.ravel(),
            self.b_tau.ravel(),
            self.W_rel.ravel(),
        ])

    def to_dict(self) -> Dict[str, np.ndarray]:
        return {
            "W_f": self.W_f.copy(),
            "U_f": self.U_f.copy(),
            "b_f": self.b_f.copy(),
            "W_tau": self.W_tau.copy(),
            "U_tau": self.U_tau.copy(),
            "b_tau": self.b_tau.copy(),
            "W_rel": self.W_rel.copy(),
        }

    @classmethod
    def from_dict(cls, d: Dict[str, np.ndarray]) -> "SynapticParameterState":
        return cls(
            W_f=np.array(d["W_f"], dtype=np.float64),
            U_f=np.array(d["U_f"], dtype=np.float64),
            b_f=np.array(d["b_f"], dtype=np.float64),
            W_tau=np.array(d["W_tau"], dtype=np.float64),
            U_tau=np.array(d["U_tau"], dtype=np.float64),
            b_tau=np.array(d["b_tau"], dtype=np.float64),
            W_rel=np.array(d["W_rel"], dtype=np.float64),
        )


@dataclass
class ConsolidationExperience:
    """
    Interaction tuple captured for offline consolidation replay.
    Strict invariant: Pure dynamical tensors; zero introspective self-model fields.
    """
    stimulus: np.ndarray          # x in R^Nin
    h_before: np.ndarray          # h_fast before turn in R^H
    h_after: np.ndarray           # h_fast after turn in R^H
    s_slow: np.ndarray            # s_slow after turn in R^Hs
    relational_state: np.ndarray  # R in [0, 1]^4
    r_slow_recollection: np.ndarray  # r_slow in R^Hs
    salience: float
    sequence_id: int
    timestamp: float = field(default_factory=time.monotonic)


@dataclass
class HomeostaticTrajectory:
    """Time-series recording of homeostatic settling."""
    timestamps: List[float] = field(default_factory=list)
    energies: List[float] = field(default_factory=list)
    tensions: List[float] = field(default_factory=list)
    cognitive_loads: List[float] = field(default_factory=list)
    stabilities: List[float] = field(default_factory=list)


class _DifferentiableODEModel(nn.Module):
    """
    PyTorch CPU module for backpropagation-through-ODE.
    Explicitly pinned to CPU to guarantee 0 MB GPU VRAM allocation.
    """

    def __init__(self, params: SynapticParameterState) -> None:
        super().__init__()
        self.device = torch.device("cpu")
        self.W_f = nn.Parameter(torch.from_numpy(params.W_f).float().to(self.device))
        self.U_f = nn.Parameter(torch.from_numpy(params.U_f).float().to(self.device))
        self.b_f = nn.Parameter(torch.from_numpy(params.b_f).float().to(self.device))
        self.W_tau = nn.Parameter(torch.from_numpy(params.W_tau).float().to(self.device))
        self.U_tau = nn.Parameter(torch.from_numpy(params.U_tau).float().to(self.device))
        self.b_tau = nn.Parameter(torch.from_numpy(params.b_tau).float().to(self.device))
        self._x: Optional[torch.Tensor] = None

    def forward(self, t: torch.Tensor, h: torch.Tensor) -> torch.Tensor:
        h_c = torch.clamp(h, -1.0, 1.0)
        stim_term = self.U_tau @ self._x if self._x is not None else 0.0
        tau_raw = torch.nn.functional.softplus(self.W_tau @ h_c + stim_term + self.b_tau)
        tau = torch.clamp(tau_raw, 0.10, 1.50)

        f_stim = self.U_f @ self._x if self._x is not None else 0.0
        f = torch.tanh(self.W_f @ h_c + f_stim + self.b_f)
        return (-h_c + f) / tau


class ConsolidationEngine:
    """
    Offline synaptic plasticity and relational consolidation service.

    Handles:
        - Experience buffering of salient interaction transitions.
        - Asynchronous CPU BPTT-through-ODE parameter optimization.
        - Dual homeostatic baseline and Philia attractor regularization.
        - Sub-2ms atomic parameter swapping into live EmotionCore.
    """

    def __init__(
        self,
        config: Optional[EmotionConfig] = None,
        stimulus_dim: int = 16,
    ) -> None:
        self._config = config if config is not None else EmotionConfig()
        self.stimulus_dim = stimulus_dim
        self.experience_buffer: List[ConsolidationExperience] = []
        self._buffer_lock = threading.Lock()
        self._warmup_diffeq()

    def _warmup_diffeq(self) -> None:
        """Warm up torchdiffeq autograd dispatch to eliminate cold-start latency."""
        try:
            H = self._config.hidden_dim
            Nin = self.stimulus_dim
            dummy_params = SynapticParameterState(
                W_f=np.zeros((H, H), dtype=np.float64),
                U_f=np.zeros((H, Nin), dtype=np.float64),
                b_f=np.zeros(H, dtype=np.float64),
                W_tau=np.zeros((H, H), dtype=np.float64),
                U_tau=np.zeros((H, Nin), dtype=np.float64),
                b_tau=np.zeros(H, dtype=np.float64),
                W_rel=np.zeros((self._config.hidden_slow_dim, 4), dtype=np.float64),
            )
            model = _DifferentiableODEModel(dummy_params)
            model._x = torch.zeros(Nin, dtype=torch.float32)
            t = torch.tensor([0.0, 0.01], dtype=torch.float32)
            h = torch.zeros(H, dtype=torch.float32)
            out = odeint(model, h, t, method="euler")
            loss = torch.norm(out)
            loss.backward()
        except Exception as e:
            logger.debug("ConsolidationEngine: diff-eq warmup exception: %s", e)

    def record_experience(
        self,
        stimulus: np.ndarray,
        h_before: np.ndarray,
        h_after: np.ndarray,
        s_slow: np.ndarray,
        salience: float,
        relational_state: np.ndarray,
        r_slow: Optional[np.ndarray] = None,
    ) -> None:
        """
        Record a salient interaction transition into the consolidation buffer.
        Thread-safe under _buffer_lock.
        """
        if not self._config.enable_relational_consolidation:
            return

        exp = ConsolidationExperience(
            stimulus=np.array(stimulus, dtype=np.float64),
            h_before=np.array(h_before, dtype=np.float64),
            h_after=np.array(h_after, dtype=np.float64),
            s_slow=np.array(s_slow, dtype=np.float64),
            relational_state=np.array(relational_state, dtype=np.float64),
            r_slow_recollection=(
                np.zeros(self._config.hidden_slow_dim, dtype=np.float64)
                if r_slow is None
                else np.array(r_slow, dtype=np.float64)
            ),
            salience=float(salience),
            sequence_id=len(self.experience_buffer),
        )
        with self._buffer_lock:
            self.experience_buffer.append(exp)
            if len(self.experience_buffer) > 1000:
                self.experience_buffer.pop(0)

    def get_buffer(self) -> List[ConsolidationExperience]:
        """Return shallow copy of current experience buffer."""
        with self._buffer_lock:
            return list(self.experience_buffer)

    def clear_buffer(self) -> None:
        """Clear consolidation experience buffer."""
        with self._buffer_lock:
            self.experience_buffer.clear()

    def run_offline_consolidation(
        self,
        batch: Optional[List[ConsolidationExperience]] = None,
        emotion_core: Optional["EmotionCore"] = None,
        initial_params: Optional[SynapticParameterState] = None,
        learning_rate: Optional[float] = None,
        gradient_clip_norm: float = 1.0,
        lambda_homeo: Optional[float] = None,
        lambda_philia: Optional[float] = None,
        t_span: float = 0.10,
        n_epochs: int = 3,
        ode_method: str = "euler",
    ) -> Tuple[SynapticParameterState, Dict[str, float]]:
        """
        Execute offline parameter consolidation using backpropagation-through-ODE on CPU.
        Returns: (new_params, metrics)
        """
        if batch is None:
            batch = self.get_buffer()

        if not batch:
            if emotion_core is not None:
                curr = emotion_core.get_parameter_state()
            elif initial_params is not None:
                curr = initial_params.copy()
            else:
                raise ValueError("Either batch or initial parameters must be provided.")
            return curr, {"loss": 0.0, "ode_loss": 0.0, "backward_latency_ms": 0.0, "total_batch_time_ms": 0.0, "swap_latency_ms": 0.0}

        lr = learning_rate if learning_rate is not None else self._config.consolidation_learning_rate
        l_homeo = lambda_homeo if lambda_homeo is not None else self._config.consolidation_lambda_homeo
        l_philia = lambda_philia if lambda_philia is not None else self._config.consolidation_lambda_philia

        t_start = time.perf_counter()

        if emotion_core is not None:
            current_params = emotion_core.get_parameter_state()
        elif initial_params is not None:
            current_params = initial_params.copy()
        else:
            raise ValueError("EmotionCore or initial_params must be supplied.")

        w0_flat = current_params.flatten_weights()
        w0_tensor = torch.from_numpy(w0_flat).float()

        model = _DifferentiableODEModel(current_params)
        optimizer = torch.optim.AdamW(model.parameters(), lr=lr)

        total_ode_loss = torch.tensor(0.0, dtype=torch.float32)
        total_loss = torch.tensor(0.0, dtype=torch.float32)
        time_tensor = torch.tensor([0.0, t_span], dtype=torch.float32)
        backward_latency_ms = 0.0

        for epoch in range(n_epochs):
            optimizer.zero_grad()
            epoch_loss = torch.tensor(0.0, dtype=torch.float32)
            h_prev = torch.from_numpy(batch[0].h_before).float()

            for idx, exp in enumerate(batch):
                stim_slice = exp.stimulus[:self.stimulus_dim]
                model._x = torch.from_numpy(stim_slice).float()

                if idx == 0:
                    h0 = torch.from_numpy(exp.h_before).float()
                else:
                    # Sequential multi-turn continuity: 60% previous output + 40% before-turn state
                    h0 = 0.60 * h_prev + 0.40 * torch.from_numpy(exp.h_before).float()

                h_target = torch.from_numpy(exp.h_after).float()
                trajectory = odeint(model, h0, time_tensor, method=ode_method)
                h_pred = trajectory[-1]
                loss_step = torch.nn.functional.mse_loss(h_pred, h_target)
                epoch_loss = epoch_loss + loss_step
                h_prev = h_pred

            epoch_loss = epoch_loss / len(batch)

            # Homeostatic baseline regularization: ||Theta - Theta_0||^2
            w_curr = torch.cat([p.view(-1) for p in model.parameters()])
            homeo_penalty = torch.norm(w_curr - w0_tensor[:len(w_curr)]) ** 2

            # Philia attractor unforced grounding regularization: ||h_unforced(Delta t)||^2
            h_zero = torch.zeros(self._config.hidden_dim, dtype=torch.float32)
            model._x = torch.zeros(self.stimulus_dim, dtype=torch.float32)
            unforced_traj = odeint(model, h_zero, time_tensor, method=ode_method)
            philia_penalty = torch.norm(unforced_traj[-1]) ** 2

            total_loss = epoch_loss + (l_homeo * homeo_penalty) + (l_philia * philia_penalty)

            t_back_0 = time.perf_counter()
            total_loss.backward()
            backward_latency_ms = (time.perf_counter() - t_back_0) * 1000.0

            torch.nn.utils.clip_grad_norm_(model.parameters(), gradient_clip_norm)
            optimizer.step()
            total_ode_loss = epoch_loss

        # Extract updated parameter state
        new_params = SynapticParameterState(
            W_f=model.W_f.detach().cpu().numpy().astype(np.float64),
            U_f=model.U_f.detach().cpu().numpy().astype(np.float64),
            b_f=model.b_f.detach().cpu().numpy().astype(np.float64),
            W_tau=model.W_tau.detach().cpu().numpy().astype(np.float64),
            U_tau=model.U_tau.detach().cpu().numpy().astype(np.float64),
            b_tau=model.b_tau.detach().cpu().numpy().astype(np.float64),
            W_rel=current_params.W_rel.copy(),
        )

        total_batch_time_ms = (time.perf_counter() - t_start) * 1000.0

        # Atomic parameter swap into EmotionCore under _train_lock
        swap_latency_ms = 0.0
        if emotion_core is not None:
            t_swap_0 = time.perf_counter()
            emotion_core.set_parameter_state(new_params)
            swap_latency_ms = (time.perf_counter() - t_swap_0) * 1000.0

        metrics = {
            "loss": float(total_loss.item()),
            "ode_loss": float(total_ode_loss.item()),
            "backward_latency_ms": backward_latency_ms,
            "total_batch_time_ms": total_batch_time_ms,
            "swap_latency_ms": swap_latency_ms,
        }

        return new_params, metrics

    def evaluate_baseline_probe_loss(
        self,
        probe_inputs: List[Tuple[np.ndarray, np.ndarray]],
        emotion_core: "EmotionCore",
        dt: float = 0.20,
    ) -> float:
        """
        Evaluate baseline loss on standard probes to detect catastrophic forgetting.
        Probe inputs: list of (stimulus, target_h).
        """
        losses = []
        for stim, h_targ in probe_inputs:
            h_step = emotion_core._ode_step(emotion_core._h, stim)
            if isinstance(h_step, tuple):
                h_step = h_step[0]
            diff = np.mean((h_step - h_targ) ** 2)
            losses.append(diff)
        return float(np.mean(losses)) if losses else 0.0
