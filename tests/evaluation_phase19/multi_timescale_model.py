"""
MultiTimescaleEmotionCore — Coupled Multi-Timescale Liquid Neural Network (MT-LNN).

Isolated research model for Phase 19 evaluating multi-timescale affective dynamics:
    Fast reactive state:  h_fast in R^32  (tau_fast in [0.05s, 1.5s])
    Slow momentum state:  s_slow in R^16  (tau_slow in [30.0s, 120.0s])
    Philia attractor:     s*_philia in R^16
    Homeostatic coupling: m_homeo in R^4 (energy, load, tension, stability)

Asymmetric Fast-Attack / Slow-Relaxation Dynamics:
    dh_fast/dt = (-h_fast + tanh(W_ff*h_fast + W_fs*(s_slow - s*_philia) + U_f*x)) / tau_fast
    ds_slow/dt = -(s_slow - s*_philia) / tau_slow_decay + tanh(W_sf*h_fast + W_sh*delta_m_homeo) / tau_slow_charge

Coupled PAD projection:
    When ablate_philia_attractor=False:
        PAD(t) = clip(W_proj_f*h_fast + W_proj_s*(s_slow - s*_philia) + p*_philia, -1.0, 1.0)
        At resting equilibrium (h_fast = 0, s_slow = s*_philia): PAD* = p*_philia bit-exact.
    When ablate_philia_attractor=True:
        PAD(t) = clip(W_proj_f*h_fast + W_proj_s*s_slow, -1.0, 1.0)
        At unforced equilibrium (h_fast = 0, s_slow = 0): PAD* = [0, 0, 0] (Phase 10 origin collapse).
"""

from __future__ import annotations

import logging
import threading
import time
from collections import deque
from dataclasses import dataclass
from typing import List, Optional, Tuple

import numpy as np
from scipy.integrate import solve_ivp
from scipy.special import expit, softplus

from src.core.models import PADState

logger = logging.getLogger(__name__)


def _xavier_uniform(shape: tuple, rng: np.random.Generator) -> np.ndarray:
    fan_in, fan_out = shape[-1], shape[0]
    limit = np.sqrt(6.0 / (fan_in + fan_out))
    return rng.uniform(-limit, limit, size=shape).astype(np.float64)


@dataclass
class MultiTimescaleConfig:
    """Configuration for Coupled Multi-Timescale EmotionCore."""
    hidden_fast_dim: int = 32
    hidden_slow_dim: int = 16
    stimulus_dim: int = 16
    homeo_dim: int = 4
    loop_cadence_ms: int = 200
    resting_baseline: Tuple[float, float, float] = (0.25, -0.05, 0.05)
    ode_step_size: float = 0.1
    # Timescale boundaries
    tau_fast_min: float = 0.10
    tau_fast_max: float = 1.50
    tau_slow_charge: float = 3.5
    tau_slow_decay: float = 28.0
    # Coupling coefficients
    coupling_fs_strength: float = 0.05  # Kept small to guarantee loop gain < 1.0 (prevents latching)
    coupling_sf_strength: float = 1.00  # Strong fast-to-slow momentum uptake
    coupling_homeo_strength: float = 0.40
    # Ablation Flags
    ablate_slow_field: bool = False
    ablate_philia_attractor: bool = False
    ablate_homeostatic_coupling: bool = False
    ablate_adaptive_tau: bool = False
    init_seed: int = 42


class MultiTimescaleEmotionCore:
    """Coupled Multi-Timescale Liquid Neural Network (MT-LNN)."""

    def __init__(self, config: Optional[MultiTimescaleConfig] = None) -> None:
        if config is None:
            config = MultiTimescaleConfig()
        self._config = config

        Hf = config.hidden_fast_dim
        Hs = config.hidden_slow_dim
        Nx = config.stimulus_dim
        Nm = config.homeo_dim

        rng = np.random.default_rng(config.init_seed)

        # Fast Layer weights
        self.W_ff = _xavier_uniform((Hf, Hf), rng) * 0.20
        self.W_fs = np.zeros((Hf, Hs), dtype=np.float64)
        self.U_f = _xavier_uniform((Hf, Nx), rng) * 0.3
        self.b_f = np.zeros(Hf, dtype=np.float64)

        # Sensory alignment on principal fast channels
        self.U_f[0, 0] = 1.00  # Valence -> Pleasure
        self.U_f[1, 1] = 1.00  # Arousal -> Arousal
        self.U_f[2, 2] = 0.80  # Dominance/Density -> Dominance

        # Fast Time-Constant weights
        self.W_tau_f = _xavier_uniform((Hf, Hf), rng) * 0.1
        self.U_tau_f = _xavier_uniform((Hf, Nx), rng) * 0.1
        self.b_tau_f = np.zeros(Hf, dtype=np.float64)

        # Slow Layer weights (asymmetric charging)
        self.W_sf = np.zeros((Hs, Hf), dtype=np.float64)
        self.W_sh = np.zeros((Hs, Nm), dtype=np.float64)

        # Cross-timescale alignment
        self.W_sf[0, 0] = config.coupling_sf_strength
        self.W_sf[1, 1] = config.coupling_sf_strength
        self.W_sf[2, 2] = config.coupling_sf_strength * 0.8

        # Dissipative slow-to-fast priming (strictly bounded)
        self.W_fs[0, 0] = config.coupling_fs_strength
        self.W_fs[1, 1] = config.coupling_fs_strength
        self.W_fs[2, 2] = config.coupling_fs_strength * 0.8

        # Homeostatic coupling:
        # m_homeo = [energy, load, tension, stability]
        # delta_m = m_homeo - [1.0, 0.0, 0.0, 1.0]
        self.W_sh[0, 2] = -0.60 * config.coupling_homeo_strength  # tension reduces pleasure
        self.W_sh[0, 1] = -0.20 * config.coupling_homeo_strength  # cognitive load reduces pleasure
        self.W_sh[1, 2] = +0.70 * config.coupling_homeo_strength  # tension elevates arousal
        self.W_sh[1, 1] = +0.10 * config.coupling_homeo_strength  # active load mildly elevates arousal
        self.W_sh[1, 0] = +0.50 * config.coupling_homeo_strength  # energy depletion (delta_m[0] < 0) lowers arousal (fatigue)

        # Projections to PAD:
        self.W_proj_f = np.zeros((3, Hf), dtype=np.float64)
        self.W_proj_f[0, 0] = 0.70
        self.W_proj_f[1, 1] = 0.70
        self.W_proj_f[2, 2] = 0.60

        self.W_proj_s = np.zeros((3, Hs), dtype=np.float64)
        self.W_proj_s[0, 0] = 0.45
        self.W_proj_s[1, 1] = 0.45
        self.W_proj_s[2, 2] = 0.35

        # Canonical Philia coordinate
        p_base = np.array(config.resting_baseline, dtype=np.float64)
        self.p_philia = p_base.copy()

        # Philia in slow latent space
        self.s_philia = np.zeros(Hs, dtype=np.float64)
        self.s_philia[0] = 0.20
        self.s_philia[1] = -0.05
        self.s_philia[2] = 0.05

        # Resting homeostatic reference
        self.m_homeo_resting = np.array([1.0, 0.0, 0.0, 1.0], dtype=np.float64)

        # States
        self._h_fast: np.ndarray = np.zeros(Hf, dtype=np.float64)
        self._s_slow: np.ndarray = self.s_philia.copy() if not config.ablate_philia_attractor else np.zeros(Hs)
        self._m_homeo: np.ndarray = self.m_homeo_resting.copy()

        # Concurrency & Sync
        self._state_lock = threading.Lock()
        self._stimulus_lock = threading.Lock()
        self._step_lock = threading.Lock()
        self._train_lock = threading.Lock()

        # Resting PAD snapshot
        self._pad_resting = PADState(
            pleasure=float(p_base[0]),
            arousal=float(p_base[1]),
            dominance=float(p_base[2]),
            timestamp=time.monotonic(),
        )
        self._pad_snapshot: PADState = self._pad_resting

        # FIFO Stimulus Queue
        self._pending_stimuli: deque[Tuple[int, np.ndarray]] = deque()
        self._stimulus_seq: int = 0
        self._committed_stimulus_seq: int = 0
        self._tick_counter: int = 0

        # Background thread control
        self._stop_event = threading.Event()
        self._thread: Optional[threading.Thread] = None

    # ------------------------------------------------------------------
    # Lifecycle
    # ------------------------------------------------------------------

    def start(self) -> None:
        if self._thread is not None and self._thread.is_alive():
            return
        self._stop_event.clear()
        self._thread = threading.Thread(
            target=self._fast_loop_worker,
            name="MT-EmotionCore-FastLoop",
            daemon=True,
        )
        self._thread.start()

    def stop(self) -> None:
        self._stop_event.set()

    def is_alive(self) -> bool:
        return self._thread is not None and self._thread.is_alive()

    def tick_count(self) -> int:
        return self._tick_counter

    # ------------------------------------------------------------------
    # Public Thread-Safe Accessors
    # ------------------------------------------------------------------

    def get_pad_state(self) -> PADState:
        with self._state_lock:
            return self._pad_snapshot

    def get_fast_state(self) -> np.ndarray:
        with self._state_lock:
            return self._h_fast.copy()

    def get_slow_state(self) -> np.ndarray:
        with self._state_lock:
            return self._s_slow.copy()

    def get_attractor_distance(self) -> float:
        with self._state_lock:
            p = np.array([self._pad_snapshot.pleasure, self._pad_snapshot.arousal, self._pad_snapshot.dominance])
            return float(np.linalg.norm(p - self.p_philia))

    def update_homeostatic_context(self, energy: float, load: float, tension: float, stability: float) -> None:
        with self._step_lock:
            self._m_homeo = np.clip(np.array([energy, load, tension, stability], dtype=np.float64), 0.0, 1.0)

    def push_stimulus(self, vector: np.ndarray) -> int:
        with self._stimulus_lock:
            self._stimulus_seq += 1
            seq = self._stimulus_seq
            self._pending_stimuli.append((seq, np.array(vector, dtype=np.float64)))
            return seq

    def reset_to_resting(self) -> None:
        with self._step_lock:
            with self._stimulus_lock:
                self._pending_stimuli.clear()
                self._stimulus_seq = 0
                self._committed_stimulus_seq = 0
            with self._state_lock:
                self._h_fast = np.zeros(self._config.hidden_fast_dim, dtype=np.float64)
                self._s_slow = self.s_philia.copy() if not self._config.ablate_philia_attractor else np.zeros(self._config.hidden_slow_dim)
                self._m_homeo = self.m_homeo_resting.copy()
                self._pad_snapshot = self._pad_resting

    # ------------------------------------------------------------------
    # ODE Numerical Stepper
    # ------------------------------------------------------------------

    def _ode_step(
        self,
        h_fast: np.ndarray,
        s_slow: np.ndarray,
        x: np.ndarray,
        m_homeo: np.ndarray,
        dt: float,
    ) -> Tuple[np.ndarray, np.ndarray]:
        cfg = self._config
        Hf = cfg.hidden_fast_dim
        Hs = cfg.hidden_slow_dim

        y0 = np.concatenate([h_fast, s_slow])

        W_fs = np.zeros((Hf, Hs)) if cfg.ablate_slow_field else self.W_fs
        W_sf = np.zeros((Hs, Hf)) if cfg.ablate_slow_field else self.W_sf
        W_sh = np.zeros((Hs, cfg.homeo_dim)) if cfg.ablate_homeostatic_coupling else self.W_sh
        s_target = np.zeros(Hs) if cfg.ablate_philia_attractor else self.s_philia

        # Homeostatic deviation from resting state
        delta_m = m_homeo - self.m_homeo_resting

        def rhs(t: float, y: np.ndarray) -> np.ndarray:
            y_f = np.clip(y[:Hf], -1.0, 1.0)
            y_s = np.clip(y[Hf:], -1.0, 1.0)
            delta_s = y_s - s_target

            # Fast timescale
            if cfg.ablate_adaptive_tau:
                tau_f = 0.20
            else:
                tau_f_raw = softplus(self.W_tau_f @ y_f + self.U_tau_f @ x + self.b_tau_f)
                tau_f = np.clip(tau_f_raw, cfg.tau_fast_min, cfg.tau_fast_max)

            f_fast = np.tanh(self.W_ff @ y_f + W_fs @ delta_s + self.U_f @ x + self.b_f)
            dh_fast = (-y_f + f_fast) / tau_f

            # Slow timescale (fast charging attack, slow relaxation decay)
            tau_decay = cfg.tau_slow_decay
            tau_charge = cfg.tau_slow_charge

            forcing = np.tanh(W_sf @ y_f + W_sh @ delta_m)
            ds_slow = (-delta_s / tau_decay) + (forcing / tau_charge)

            return np.concatenate([dh_fast, ds_slow])

        res = solve_ivp(
            rhs,
            t_span=(0.0, dt),
            y0=y0,
            method="RK45",
            max_step=dt / 2.0,
            dense_output=False,
            vectorized=False,
        )

        y_next = res.y[:, -1]
        h_next = np.clip(y_next[:Hf], -1.0, 1.0)
        s_next = np.clip(y_next[Hf:], -1.0, 1.0)
        return h_next, s_next

    def _project_to_pad(self, h_fast: np.ndarray, s_slow: np.ndarray) -> PADState:
        if self._config.ablate_philia_attractor:
            # Ablated: projection to origin baseline [0, 0, 0]
            pad_raw = (self.W_proj_f @ h_fast) + (self.W_proj_s @ s_slow)
        else:
            # Full model: projection anchored at Philia resting attractor
            delta_s = s_slow - self.s_philia
            W_proj_s = np.zeros_like(self.W_proj_s) if self._config.ablate_slow_field else self.W_proj_s
            pad_raw = (self.W_proj_f @ h_fast) + (W_proj_s @ delta_s) + self.p_philia

        pad_clamped = np.clip(pad_raw, -1.0, 1.0)
        return PADState(
            pleasure=float(pad_clamped[0]),
            arousal=float(pad_clamped[1]),
            dominance=float(pad_clamped[2]),
            timestamp=time.monotonic(),
        )

    def _consume_stimulus(self) -> Tuple[np.ndarray, Optional[int]]:
        with self._stimulus_lock:
            if self._pending_stimuli:
                seq, vec = self._pending_stimuli.popleft()
                return vec, seq
            return np.zeros(self._config.stimulus_dim, dtype=np.float64), None

    def step_once(self, custom_timestamp: Optional[float] = None, dt_override: Optional[float] = None) -> PADState:
        with self._step_lock:
            x, seq = self._consume_stimulus()
            dt = dt_override if dt_override is not None else self._config.ode_step_size
            h_new, s_new = self._ode_step(self._h_fast, self._s_slow, x, self._m_homeo, dt)
            pad = self._project_to_pad(h_new, s_new)

            if custom_timestamp is not None:
                pad = PADState(
                    pleasure=pad.pleasure,
                    arousal=pad.arousal,
                    dominance=pad.dominance,
                    timestamp=custom_timestamp,
                )

            self._h_fast = h_new
            self._s_slow = s_new

            with self._state_lock:
                self._pad_snapshot = pad

            if seq is not None:
                self._committed_stimulus_seq = max(self._committed_stimulus_seq, seq)
            self._tick_counter += 1
            return pad

    def commit_stimulus(self, target_seq: Optional[int] = None) -> PADState:
        with self._step_lock:
            with self._stimulus_lock:
                max_submitted = self._stimulus_seq
                if target_seq is None:
                    target_seq = max_submitted

            target_seq = min(target_seq, max_submitted)
            if target_seq <= 0:
                return self.get_pad_state()

            while self._committed_stimulus_seq < target_seq:
                with self._stimulus_lock:
                    if not self._pending_stimuli:
                        break
                self._consume_and_step_unlocked()

            return self.get_pad_state()

    def _consume_and_step_unlocked(self) -> PADState:
        x, seq = self._consume_stimulus()
        dt = self._config.ode_step_size
        h_new, s_new = self._ode_step(self._h_fast, self._s_slow, x, self._m_homeo, dt)
        pad = self._project_to_pad(h_new, s_new)
        self._h_fast = h_new
        self._s_slow = s_new
        with self._state_lock:
            self._pad_snapshot = pad
        if seq is not None:
            self._committed_stimulus_seq = max(self._committed_stimulus_seq, seq)
        self._tick_counter += 1
        return pad

    def _fast_loop_worker(self) -> None:
        while not self._stop_event.is_set():
            t0 = time.monotonic()
            self.step_once()
            elapsed_ms = (time.monotonic() - t0) * 1000.0
            sleep_s = max(0.0, self._config.loop_cadence_ms - elapsed_ms) / 1000.0
            time.sleep(sleep_s)
