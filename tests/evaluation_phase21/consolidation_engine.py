"""
tests/evaluation_phase21/consolidation_engine.py

Isolated research prototype for Phase 21: Long-Term Relational Consolidation & Synaptic Homeostasis.
Integrates MT-LNN dynamical substrate, relational attractor bias, analytical homeostatic settling,
and CPU-only offline parameter consolidation (backpropagation-through-ODE).

Strict isolation: zero modification to src/core/** or canonical production data.
"""

from __future__ import annotations

import logging
import threading
import time
from typing import Any, Dict, List, Optional, Tuple

import numpy as np
import torch
import torch.nn as nn
from scipy.special import expit, softplus
from torchdiffeq import odeint

from tests.evaluation_phase21.models import (
    ConsolidationExperience,
    CounterfactualType,
    HomeostaticState,
    HomeostaticTrajectory,
    SimulationResult,
    SynapticParameterState,
)

logger = logging.getLogger(__name__)


def _xavier_uniform(shape: tuple, rng: np.random.Generator) -> np.ndarray:
    fan_in, fan_out = shape[-1], shape[0]
    limit = np.sqrt(6.0 / (fan_in + fan_out))
    return rng.uniform(-limit, limit, size=shape).astype(np.float64)


class _DifferentiableODEModel(nn.Module):
    """PyTorch CPU module for backpropagation-through-ODE."""

    def __init__(self, params: SynapticParameterState) -> None:
        super().__init__()
        self.device = torch.device("cpu")
        self.W_f = nn.Parameter(torch.from_numpy(params.W_f).float())
        self.U_f = nn.Parameter(torch.from_numpy(params.U_f).float())
        self.b_f = nn.Parameter(torch.from_numpy(params.b_f).float())
        self.W_tau = nn.Parameter(torch.from_numpy(params.W_tau).float())
        self.U_tau = nn.Parameter(torch.from_numpy(params.U_tau).float())
        self.b_tau = nn.Parameter(torch.from_numpy(params.b_tau).float())
        self._x: Optional[torch.Tensor] = None

    def forward(self, t: torch.Tensor, h: torch.Tensor) -> torch.Tensor:
        h_c = torch.clamp(h, -1.0, 1.0)
        tau = torch.nn.functional.softplus(
            self.W_tau @ h_c + (self.U_tau @ self._x if self._x is not None else 0.0) + self.b_tau
        )
        tau = torch.clamp(tau, 0.10, 1.50)
        f = torch.tanh(
            self.W_f @ h_c + (self.U_f @ self._x if self._x is not None else 0.0) + self.b_f
        )
        return (-h_c + f) / tau


class RelationalConsolidationEngine:
    """
    Isolated prototype engine modeling Phase 21 dynamics:
      1. Coupled MT-LNN: fast state h in R^32, slow state s in R^16
      2. Dynamic relational bias: s*_eff(R) = s*_philia + W_rel (R_t - R_0)
      3. Homeostatic settling: energy recovery & tension dissipation
      4. Computational synaptic consolidation: CPU backprop-through-ODE
    """

    def __init__(
        self,
        hidden_dim: int = 32,
        hidden_slow_dim: int = 16,
        stimulus_dim: int = 16,
        seed: int = 42,
        w_rel_spectral_bound: float = 0.05,
    ) -> None:
        self.hidden_dim = hidden_dim
        self.hidden_slow_dim = hidden_slow_dim
        self.stimulus_dim = stimulus_dim
        self.w_rel_spectral_bound = float(w_rel_spectral_bound)

        self.rng = np.random.default_rng(seed)

        # Baseline canonical Philia resting attractors
        self.p_philia = np.array([0.25, -0.05, 0.05], dtype=np.float64)
        self.s_philia = np.zeros(hidden_slow_dim, dtype=np.float64)
        self.s_philia[0] = 0.20
        self.s_philia[1] = -0.05
        self.s_philia[2] = 0.05

        # Canonical initial relationship baseline (stranger)
        self.R_0 = np.array([0.0, 0.50, 0.0, 0.50], dtype=np.float64)
        self.R_t = self.R_0.copy()

        # Weight matrices
        self.W_f = _xavier_uniform((hidden_dim, hidden_dim), self.rng) * 0.20
        self.U_f = _xavier_uniform((hidden_dim, stimulus_dim), self.rng) * 0.30
        if stimulus_dim >= 3 and hidden_dim >= 3:
            self.U_f[0, 0] = 1.00
            self.U_f[1, 1] = 1.00
            self.U_f[2, 2] = 0.80
        self.b_f = np.zeros(hidden_dim, dtype=np.float64)

        self.W_tau = _xavier_uniform((hidden_dim, hidden_dim), self.rng) * 0.10
        self.U_tau = _xavier_uniform((hidden_dim, stimulus_dim), self.rng) * 0.10
        self.b_tau = np.zeros(hidden_dim, dtype=np.float64)

        # Projections
        self.W_proj_f = np.zeros((3, hidden_dim), dtype=np.float64)
        self.W_proj_f[0, 0] = 0.70
        self.W_proj_f[1, 1] = 0.70
        self.W_proj_f[2, 2] = 0.60
        self.b_proj = np.zeros(3, dtype=np.float64)

        self.W_proj_s = np.zeros((3, hidden_slow_dim), dtype=np.float64)
        self.W_proj_s[0, 0] = 0.45
        self.W_proj_s[1, 1] = 0.45
        self.W_proj_s[2, 2] = 0.35

        # Coupling strengths & matrices
        self.w_fs_coupling = 0.05
        self.w_sf_coupling = 1.00
        self.w_homeo_coupling = 0.40
        self.tau_slow_charge = 3.50
        self.tau_slow_decay = 28.00

        self.W_fs = np.zeros((hidden_dim, hidden_slow_dim), dtype=np.float64)
        if hidden_dim >= 3 and hidden_slow_dim >= 3:
            self.W_fs[0, 0] = self.w_fs_coupling
            self.W_fs[1, 1] = self.w_fs_coupling
            self.W_fs[2, 2] = self.w_fs_coupling * 0.80

        self.W_sf = np.zeros((hidden_slow_dim, hidden_dim), dtype=np.float64)
        if hidden_slow_dim >= 3 and hidden_dim >= 3:
            self.W_sf[0, 0] = self.w_sf_coupling
            self.W_sf[1, 1] = self.w_sf_coupling
            self.W_sf[2, 2] = self.w_sf_coupling * 0.80

        # W_rel (16 x 4) bounded by spectral norm
        raw_w_rel = _xavier_uniform((hidden_slow_dim, 4), self.rng)
        # Scale to ensure sigma_max <= w_rel_spectral_bound
        s_max = np.linalg.svd(raw_w_rel, compute_uv=False)[0]
        if s_max > 0:
            self.W_rel = raw_w_rel * (self.w_rel_spectral_bound / s_max) * 0.95
        else:
            self.W_rel = raw_w_rel

        # Thread synchronization locks (RLock for re-entrant safety within same thread)
        self._step_lock = threading.RLock()
        self._train_lock = threading.RLock()
        self._state_lock = threading.RLock()

        # Baseline snapshot for regularization
        self._initial_params = self.get_parameter_state()

        # Dynamic state vectors
        self._h_fast = np.zeros(hidden_dim, dtype=np.float64)
        self._s_slow = self.s_philia.copy()
        self._homeo = HomeostaticState()

        # Consolidation experience buffer
        self.experience_buffer: List[ConsolidationExperience] = []
        self._warmup_diffeq()

    def _warmup_diffeq(self) -> None:
        """Warm up torchdiffeq autograd dispatch to avoid cold-start lag."""
        try:
            m = _DifferentiableODEModel(self._initial_params)
            m._x = torch.zeros(self.stimulus_dim, dtype=torch.float32)
            t = torch.tensor([0.0, 0.01], dtype=torch.float32)
            h = torch.zeros(self.hidden_dim, dtype=torch.float32)
            out = odeint(m, h, t, method="euler")
            loss = torch.norm(out)
            loss.backward()
        except Exception as e:
            print(f"WARMUP ERROR: {e}")

    def get_parameter_state(self) -> SynapticParameterState:
        with self._train_lock:
            return SynapticParameterState(
                W_f=self.W_f.copy(),
                U_f=self.U_f.copy(),
                b_f=self.b_f.copy(),
                W_tau=self.W_tau.copy(),
                U_tau=self.U_tau.copy(),
                b_tau=self.b_tau.copy(),
                W_rel=self.W_rel.copy(),
            )

    def set_parameter_state(self, params: SynapticParameterState) -> None:
        """Atomically swap parameters inside _train_lock."""
        with self._train_lock:
            # Enforce spectral norm discipline on W_rel
            s_max = params.w_rel_spectral_norm
            if s_max > self.w_rel_spectral_bound:
                scale = self.w_rel_spectral_bound / (s_max + 1e-12)
                params.W_rel = params.W_rel * scale

            self.W_f = params.W_f.copy()
            self.U_f = params.U_f.copy()
            self.b_f = params.b_f.copy()
            self.W_tau = params.W_tau.copy()
            self.U_tau = params.U_tau.copy()
            self.b_tau = params.b_tau.copy()
            self.W_rel = params.W_rel.copy()

    def get_effective_slow_attractor(self, R: Optional[np.ndarray] = None) -> np.ndarray:
        """
        Compute relationship-conditioned slow attractor:
        s*_eff(R) = s*_philia + W_rel (R_t - R_0)
        """
        if R is None:
            R = self.R_t
        delta_r = np.clip(R, 0.0, 1.0) - self.R_0
        with self._train_lock:
            displacement = self.W_rel @ delta_r
        return self.s_philia + displacement

    def project_to_pad(
        self,
        h_fast: np.ndarray,
        s_slow: np.ndarray,
    ) -> np.ndarray:
        """
        Canonical closed-form mapping to 3D PAD space:
        PAD(t) = clip(W_proj_f h_f + W_proj_s (s_slow - s*_philia) + p*_philia + b_proj, -1.0, 1.0)
        """
        delta_s = s_slow - self.s_philia
        pad = (self.W_proj_f @ h_fast) + (self.W_proj_s @ delta_s) + self.p_philia + self.b_proj
        return np.clip(pad, -1.0, 1.0)

    def compute_resting_pad(self, R: Optional[np.ndarray] = None) -> np.ndarray:
        """
        Evaluate output PAD at resting equilibrium for given relationship state:
        h_f = 0, s_slow = s*_eff(R)
        """
        s_eff = self.get_effective_slow_attractor(R)
        h_zero = np.zeros(self.hidden_dim, dtype=np.float64)
        return self.project_to_pad(h_zero, s_eff)

    def step_ode(
        self,
        stimulus: np.ndarray,
        dt: float = 0.20,
        recollection_forcing: Optional[np.ndarray] = None,
    ) -> Tuple[np.ndarray, np.ndarray]:
        """
        Execute one discrete numerical step of coupled MT-LNN ODE.
        Returns: (h_fast, s_slow)
        """
        t0 = time.perf_counter()
        with self._step_lock:
            # Read snapshots under locks
            with self._train_lock:
                W_f, U_f, b_f = self.W_f, self.U_f, self.b_f
                W_tau, U_tau, b_tau = self.W_tau, self.U_tau, self.b_tau
                s_eff = self.get_effective_slow_attractor()

            h = self._h_fast.copy()
            s = self._s_slow.copy()

            # Time constant
            tau_input = W_tau @ h + U_tau @ stimulus + b_tau
            tau_fast = 0.10 + 1.40 * expit(tau_input)

            # Fast ODE derivative
            delta_s_eff = s - s_eff
            h_input = W_f @ h + U_f @ stimulus + (self.W_fs @ delta_s_eff) + b_f
            dh_dt = (-h + np.tanh(h_input)) / tau_fast

            # Slow ODE derivative
            rec_term = recollection_forcing if recollection_forcing is not None else np.zeros(self.hidden_slow_dim)
            homeo_term = np.zeros(self.hidden_slow_dim)
            homeo_term[0] = -0.60 * self.w_homeo_coupling * self._homeo.tension
            homeo_term[1] = +0.70 * self.w_homeo_coupling * self._homeo.tension

            charge_input = (self.W_sf @ h) + homeo_term + rec_term
            ds_dt = -(s - s_eff) / self.tau_slow_decay + np.tanh(charge_input) / self.tau_slow_charge

            # Forward Euler step
            h_next = np.clip(h + dh_dt * dt, -1.0, 1.0)
            s_next = np.clip(s + ds_dt * dt, -1.0, 1.0)

            self._h_fast = h_next
            self._s_slow = s_next

            with self._state_lock:
                pad_out = self.project_to_pad(h_next, s_next)

        return h_next, s_next

    def integrate_unforced_idle(
        self,
        duration_s: float,
        dt: float = 0.20,
        record_trajectory: bool = True,
    ) -> Tuple[np.ndarray, np.ndarray, HomeostaticTrajectory]:
        """
        Integrate system through an unforced rest / idle interval (x = 0).
        Evaluates dynamic homeostatic settling and slow-field relaxation.
        """
        n_steps = int(duration_s / dt)
        stim_zero = np.zeros(self.stimulus_dim, dtype=np.float64)

        traj_times: List[float] = []
        traj_energies: List[float] = []
        traj_tensions: List[float] = []
        traj_loads: List[float] = []
        traj_stabilities: List[float] = []

        pad_history: List[np.ndarray] = []
        slow_history: List[np.ndarray] = []

        gamma_E = 0.05
        gamma_T = 0.10
        gamma_C = 0.08

        curr_t = 0.0

        for _ in range(n_steps):
            # Dynamic homeostatic update
            # dE/dt = gamma_E * (1 - E)
            # dT/dt = -gamma_T * T
            # dC/dt = -gamma_C * C
            e_curr = self._homeo.energy
            t_curr = self._homeo.tension
            c_curr = self._homeo.cognitive_load

            e_next = e_curr + gamma_E * (1.0 - e_curr) * dt
            t_next = t_curr - gamma_T * t_curr * dt
            c_next = c_curr - gamma_C * c_curr * dt

            self._homeo.energy = float(np.clip(e_next, 0.0, 1.0))
            self._homeo.tension = float(np.clip(t_next, 0.0, 1.0))
            self._homeo.cognitive_load = float(np.clip(c_next, 0.0, 1.0))
            self._homeo.stability = float(np.clip(1.0 - 0.5 * t_next, 0.0, 1.0))

            # Advance ODE
            h_step, s_step = self.step_ode(stim_zero, dt=dt)
            curr_t += dt

            if record_trajectory:
                traj_times.append(curr_t)
                traj_energies.append(self._homeo.energy)
                traj_tensions.append(self._homeo.tension)
                traj_loads.append(self._homeo.cognitive_load)
                traj_stabilities.append(self._homeo.stability)
                pad_history.append(self.project_to_pad(h_step, s_step))
                slow_history.append(s_step.copy())

        ht = HomeostaticTrajectory(
            timestamps=traj_times,
            energies=traj_energies,
            tensions=traj_tensions,
            cognitive_loads=traj_loads,
            stabilities=traj_stabilities,
        )

        return (
            np.array(pad_history) if pad_history else np.zeros((0, 3)),
            np.array(slow_history) if slow_history else np.zeros((0, self.hidden_slow_dim)),
            ht,
        )

    def record_experience(
        self,
        stimulus: np.ndarray,
        h_before: np.ndarray,
        h_after: np.ndarray,
        s_slow: np.ndarray,
        salience: float,
        relational_state: Optional[np.ndarray] = None,
        r_slow: Optional[np.ndarray] = None,
    ) -> None:
        """Store interaction transition into consolidation buffer."""
        exp = ConsolidationExperience(
            stimulus=stimulus.copy(),
            h_before=h_before.copy(),
            h_after=h_after.copy(),
            s_slow=s_slow.copy(),
            relational_state=self.R_t.copy() if relational_state is None else relational_state.copy(),
            r_slow_recollection=np.zeros(self.hidden_slow_dim) if r_slow is None else r_slow.copy(),
            salience=float(salience),
            sequence_id=len(self.experience_buffer),
        )
        self.experience_buffer.append(exp)

    def run_offline_consolidation(
        self,
        batch: List[ConsolidationExperience],
        learning_rate: float = 1e-4,
        gradient_clip_norm: float = 1.0,
        lambda_homeo: float = 0.05,
        lambda_philia: float = 0.10,
        t_span: float = 0.10,
        n_epochs: int = 3,
        ode_method: str = "euler",
    ) -> Tuple[SynapticParameterState, Dict[str, float]]:
        """
        Execute offline parameter consolidation using backprop-through-ODE on CPU.
        Returns: (new_params, metrics)
        """
        if not batch:
            return self.get_parameter_state(), {"loss": 0.0, "backward_latency_ms": 0.0}

        t_start = time.perf_counter()
        current_params = self.get_parameter_state()
        model = _DifferentiableODEModel(current_params)
        optimizer = torch.optim.AdamW(model.parameters(), lr=learning_rate)

        total_ode_loss = torch.tensor(0.0, dtype=torch.float32)
        time_tensor = torch.tensor([0.0, t_span], dtype=torch.float32)

        for epoch in range(n_epochs):
            optimizer.zero_grad()
            epoch_loss = torch.tensor(0.0, dtype=torch.float32)
            h_prev = torch.from_numpy(batch[0].h_before).float()

            for idx, exp in enumerate(batch):
                model._x = torch.from_numpy(exp.stimulus[:self.stimulus_dim]).float()
                if idx == 0:
                    h0 = torch.from_numpy(exp.h_before).float()
                else:
                    h0 = 0.60 * h_prev + 0.40 * torch.from_numpy(exp.h_before).float()

                h_target = torch.from_numpy(exp.h_after).float()

                trajectory = odeint(model, h0, time_tensor, method=ode_method)
                h_pred = trajectory[-1]
                loss_step = torch.nn.functional.mse_loss(h_pred, h_target)
                epoch_loss = epoch_loss + loss_step
                h_prev = h_pred

            epoch_loss = epoch_loss / len(batch)

            # Homeostatic baseline regularization: ||Theta - Theta_0||^2
            w0 = torch.from_numpy(self._initial_params.flatten_weights()).float()
            w_curr = torch.cat([p.view(-1) for p in model.parameters()])
            homeo_penalty = torch.norm(w_curr - w0[:len(w_curr)]) ** 2

            # Philia attractor preservation penalty
            h_zero = torch.zeros(self.hidden_dim, dtype=torch.float32)
            model._x = torch.zeros(self.stimulus_dim, dtype=torch.float32)
            unforced_traj = odeint(model, h_zero, time_tensor, method=ode_method)
            philia_penalty = torch.norm(unforced_traj[-1]) ** 2

            total_loss = epoch_loss + (lambda_homeo * homeo_penalty) + (lambda_philia * philia_penalty)

            t_backward_start = time.perf_counter()
            total_loss.backward()
            backward_latency_ms = (time.perf_counter() - t_backward_start) * 1000.0

            torch.nn.utils.clip_grad_norm_(model.parameters(), gradient_clip_norm)
            optimizer.step()
            total_ode_loss = epoch_loss

        # Extract updated weights
        new_params = SynapticParameterState(
            W_f=model.W_f.detach().numpy().astype(np.float64),
            U_f=model.U_f.detach().numpy().astype(np.float64),
            b_f=model.b_f.detach().numpy().astype(np.float64),
            W_tau=model.W_tau.detach().numpy().astype(np.float64),
            U_tau=model.U_tau.detach().numpy().astype(np.float64),
            b_tau=model.b_tau.detach().numpy().astype(np.float64),
            W_rel=self.W_rel.copy(),
        )

        total_batch_time_ms = (time.perf_counter() - t_start) * 1000.0

        # Swap weights into engine under train lock
        t_swap_start = time.perf_counter()
        self.set_parameter_state(new_params)
        swap_latency_ms = (time.perf_counter() - t_swap_start) * 1000.0

        metrics = {
            "loss": float(total_loss.item()),
            "ode_loss": float(total_ode_loss.item()),
            "backward_latency_ms": backward_latency_ms,
            "total_batch_time_ms": total_batch_time_ms,
            "swap_latency_ms": swap_latency_ms,
        }

        return new_params, metrics

    def update_relationship_state(
        self,
        signals: np.ndarray,
        alpha: float = 0.03,
        decay_rate: float = 0.005,
    ) -> np.ndarray:
        """
        Advance 4D relationship state:
        R_{t+1} = clip(R_t + alpha * signals - decay_rate * (R_t - R_0), 0.0, 1.0)
        """
        delta = alpha * signals - decay_rate * (self.R_t - self.R_0)
        self.R_t = np.clip(self.R_t + delta, 0.0, 1.0)
        return self.R_t.copy()

    def evaluate_baseline_probe_loss(self, probe_inputs: List[Tuple[np.ndarray, np.ndarray]]) -> float:
        """
        Evaluate baseline loss on standard probes to detect catastrophic forgetting.
        """
        losses = []
        stim_dim = self.stimulus_dim
        for stim, h_targ in probe_inputs:
            h_step, _ = self.step_ode(stim, dt=0.20)
            diff = np.mean((h_step - h_targ) ** 2)
            losses.append(diff)
        return float(np.mean(losses)) if losses else 0.0

    def evaluate_experience_loss(
        self,
        batch: List[ConsolidationExperience],
        t_span: float = 0.10,
    ) -> float:
        """
        Evaluate sequential trajectory reconstruction loss on an interaction session.
        """
        if not batch:
            return 0.0
        current_params = self.get_parameter_state()
        model = _DifferentiableODEModel(current_params)
        time_tensor = torch.tensor([0.0, t_span], dtype=torch.float32)
        total_loss = 0.0
        h_prev = torch.from_numpy(batch[0].h_before).float()
        with torch.no_grad():
            for idx, exp in enumerate(batch):
                model._x = torch.from_numpy(exp.stimulus[:self.stimulus_dim]).float()
                if idx == 0:
                    h0 = torch.from_numpy(exp.h_before).float()
                else:
                    h0 = 0.60 * h_prev + 0.40 * torch.from_numpy(exp.h_before).float()
                h_target = torch.from_numpy(exp.h_after).float()
                trajectory = odeint(model, h0, time_tensor, method="rk4")
                h_pred = trajectory[-1]
                total_loss += float(torch.nn.functional.mse_loss(h_pred, h_target).item())
                h_prev = h_pred
        return float(total_loss / len(batch))
