"""
EmotionCore — Coupled Multi-Timescale Liquid Neural Network (MT-LNN) Emotional Engine.

Implements a coupled dual-timescale dynamical system:
    Fast reactive layer:  h_fast in R^32  (tau_fast in [0.10s, 1.50s])
    Slow latent field:    s_slow in R^16  (tau_slow in [3.5s charge, 28.0s decay])
    Philia attractor:     s*_philia in R^16, p*_philia in R^3
    Homeostatic coupling: m_homeo in R^4 (energy, cognitive_load, tension, stability)

Coupled Differential Equations:
    dh_f/dt = (-h_f + tanh(W_ff·h_f + W_fs·(s_s - s*_philia) + U_f·x + b_f)) / tau_fast
    ds_s/dt = -(s_s - s*_philia) / tau_decay + tanh(W_sf·h_f + W_sh·delta_m) / tau_charge

Coupled PAD Projection:
    PAD(t) = clip(W_proj_f·h_f + W_proj_s·(s_s - s*_philia) + p*_philia + b_proj, -1.0, 1.0)
    At resting equilibrium (h_f = 0, s_s = s*_philia): PAD* = p*_philia bit-exact.

Threading & Concurrency Discipline:
    Canonical Lock Hierarchy: _turn_lock -> _step_lock -> _train_lock -> _stimulus_lock -> _state_lock
    - _step_lock:     serializes ODE integration ticks
    - _train_lock:    protects atomic LNN weight swaps by LNNTrainer
    - _stimulus_lock: protects FIFO pending stimuli queue
    - _state_lock:    protects ephemeral PADState snapshot (<= 1ms read deadline)
"""

from __future__ import annotations

import logging
import threading
import time
from collections import deque
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple, Union

import numpy as np
from scipy.integrate import solve_ivp
from scipy.special import softplus

from src.core.config import EmotionConfig
from src.core.models import PADState
from src.core.emotion.consolidation import (
    ConsolidationEngine,
    ConsolidationExperience,
    HomeostaticTrajectory,
    SynapticParameterState,
)
from src.core.emotion.persistence import (
    DEFAULT_DYNAMICAL_STATE_PATH,
    DynamicalStateSnapshot,
    load_dynamical_checkpoint,
    save_dynamical_checkpoint,
)

logger = logging.getLogger(__name__)

# RNG seed for reproducible weight initialisation
_INIT_SEED = 42


def _xavier_uniform(shape: tuple, rng: np.random.Generator) -> np.ndarray:
    """Xavier uniform initialisation for a weight matrix of the given shape."""
    fan_in, fan_out = shape[-1], shape[0]
    limit = np.sqrt(6.0 / (fan_in + fan_out))
    return rng.uniform(-limit, limit, size=shape).astype(np.float64)


class EmotionCore:
    """
    Continuous Coupled Multi-Timescale Liquid Neural Network (MT-LNN) emotional engine.

    Usage::

        core = EmotionCore(EmotionConfig())
        core.start()
        ...
        pad = core.get_pad_state()
        core.stop()
    """

    def __init__(
        self,
        config: Optional[EmotionConfig] = None,
        storage_path: Optional[Union[str, Path]] = None,
        auto_restore: bool = True,
    ) -> None:
        if config is None:
            config = EmotionConfig()
        self._config = config

        H = config.hidden_dim
        Hs = config.hidden_slow_dim
        N_in = 16  # default Stimulus_Vector dimensionality; updated via push_stimulus
        Nm = 4     # homeostatic context: [energy, load, tension, stability]

        rng = np.random.default_rng(_INIT_SEED)

        # Fast Layer weight matrices (trainable by LNNTrainer via W_f, U_f, b_f aliases)
        self.W_f = _xavier_uniform((H, H), rng) * 0.20
        self.U_f = _xavier_uniform((H, N_in), rng) * 0.30
        if N_in >= 3 and H >= 3:
            self.U_f[0, 0] = 1.00  # Valence -> Pleasure
            self.U_f[1, 1] = 1.00  # Arousal -> Arousal
            self.U_f[2, 2] = 0.80  # Dominance/Density -> Dominance
        self.b_f = np.zeros(H, dtype=np.float64)

        self.W_tau = _xavier_uniform((H, H), rng) * 0.10
        self.U_tau = _xavier_uniform((H, N_in), rng) * 0.10
        self.b_tau = np.zeros(H, dtype=np.float64)

        # Fast layer PAD projection
        self.W_proj = _xavier_uniform((3, H), rng) * 0.10
        if H >= 3:
            self.W_proj[0, 0] = 0.70
            self.W_proj[1, 1] = 0.70
            self.W_proj[2, 2] = 0.60
        self.b_proj = np.zeros(3, dtype=np.float64)

        # Slow Layer weights & cross-timescale coupling (structural constants)
        self.W_fs = np.zeros((H, Hs), dtype=np.float64)
        if H >= 3 and Hs >= 3:
            self.W_fs[0, 0] = config.w_fs_coupling
            self.W_fs[1, 1] = config.w_fs_coupling
            self.W_fs[2, 2] = config.w_fs_coupling * 0.80

        self.W_sf = np.zeros((Hs, H), dtype=np.float64)
        if Hs >= 3 and H >= 3:
            self.W_sf[0, 0] = config.w_sf_coupling
            self.W_sf[1, 1] = config.w_sf_coupling
            self.W_sf[2, 2] = config.w_sf_coupling * 0.80

        self.W_sh = np.zeros((Hs, Nm), dtype=np.float64)
        if Hs >= 3 and Nm >= 4:
            self.W_sh[0, 2] = -0.60 * config.w_homeo_coupling  # tension reduces pleasure
            self.W_sh[0, 1] = -0.20 * config.w_homeo_coupling  # cognitive load reduces pleasure
            self.W_sh[1, 2] = +0.70 * config.w_homeo_coupling  # tension elevates arousal
            self.W_sh[1, 1] = +0.10 * config.w_homeo_coupling  # load elevates arousal
            self.W_sh[1, 0] = +0.50 * config.w_homeo_coupling  # energy depletion reduces arousal

        self.W_proj_s = np.zeros((3, Hs), dtype=np.float64)
        if Hs >= 3:
            self.W_proj_s[0, 0] = 0.45
            self.W_proj_s[1, 1] = 0.45
            self.W_proj_s[2, 2] = 0.35

        # Philia dynamic resting attractor coordinates
        p_base = np.array(config.resting_baseline, dtype=np.float64)
        self.p_philia = p_base.copy()

        self.s_philia = np.zeros(Hs, dtype=np.float64)
        for i, val in enumerate(config.philia_slow_baseline):
            if i < Hs:
                self.s_philia[i] = float(val)

        self.m_homeo_resting = np.array([1.0, 0.0, 0.0, 1.0], dtype=np.float64)

        # Ephemeral runtime state vectors (strictly RAM-only; zero disk persistence)
        self._h: np.ndarray = np.zeros(H, dtype=np.float64)
        self._s_slow: np.ndarray = self.s_philia.copy()
        self._m_homeo: np.ndarray = self.m_homeo_resting.copy()

        # Resting PAD snapshot (frozen dataclass)
        p, a, d = config.resting_baseline
        self._pad_resting = PADState(
            pleasure=float(p),
            arousal=float(a),
            dominance=float(d),
            timestamp=time.monotonic(),
        )

        # Shared state (protected by _state_lock)
        self._pad_snapshot: PADState = self._pad_resting
        self._state_lock = threading.Lock()

        # Step synchronization lock (serializes ODE stepping)
        self._step_lock = threading.Lock()

        # Phase 4: Training lock for atomic weight updates
        self._train_lock = threading.Lock()

        # Pending stimuli FIFO queue and sequence tracking (protected by _stimulus_lock)
        self._pending_stimuli: deque[Tuple[int, np.ndarray]] = deque()
        self._stimulus_lock = threading.Lock()
        self._stimulus_seq: int = 0
        self._committed_stimulus_seq: int = 0

        # Phase 20: External recollection forcing weight & state
        self.W_rec = np.eye(Hs, dtype=np.float64) * config.recollection_coupling_weight
        self._recollection_forcing = np.zeros(Hs, dtype=np.float64)
        self._recollection_remaining_sim = 0.0

        # Phase 21: Tier 2 Relational Attractor Coupling (W_rel in R^(Hs x 4))
        raw_w_rel = _xavier_uniform((Hs, 4), rng)
        s_max = np.linalg.svd(raw_w_rel, compute_uv=False)[0]
        target_norm = min(0.0475, config.w_rel_spectral_bound)
        if s_max > 0:
            self.W_rel = raw_w_rel * (target_norm / s_max)
        else:
            self.W_rel = raw_w_rel

        self.R_0 = np.array(config.relationship_baseline, dtype=np.float64)
        self._R_t = self.R_0.copy()

        # Phase 21: Tier 3 Offline Synaptic Consolidation Service
        self._consolidation_engine: Optional[ConsolidationEngine] = (
            ConsolidationEngine(config, stimulus_dim=N_in)
            if config.enable_relational_consolidation
            else None
        )

        # Loop control
        self._stop_event = threading.Event()
        self._thread: Optional[threading.Thread] = None
        self._tick_counter: int = 0

        # F-02: Persistent Dynamical State Storage & Cold Restart Recovery
        self._storage_path: Optional[Path] = Path(storage_path) if storage_path is not None else None
        if self._storage_path is not None and auto_restore:
            self.restore_from_checkpoint(self._storage_path)

    # ------------------------------------------------------------------
    # Property Aliases for MT-LNN & LNNTrainer Compatibility
    # ------------------------------------------------------------------

    @property
    def W_ff(self) -> np.ndarray:
        return self.W_f

    @W_ff.setter
    def W_ff(self, val: np.ndarray) -> None:
        self.W_f = val

    @property
    def W_tau_f(self) -> np.ndarray:
        return self.W_tau

    @W_tau_f.setter
    def W_tau_f(self, val: np.ndarray) -> None:
        self.W_tau = val

    @property
    def U_tau_f(self) -> np.ndarray:
        return self.U_tau

    @U_tau_f.setter
    def U_tau_f(self, val: np.ndarray) -> None:
        self.U_tau = val

    @property
    def b_tau_f(self) -> np.ndarray:
        return self.b_tau

    @b_tau_f.setter
    def b_tau_f(self, val: np.ndarray) -> None:
        self.b_tau = val

    @property
    def W_proj_f(self) -> np.ndarray:
        return self.W_proj

    @W_proj_f.setter
    def W_proj_f(self, val: np.ndarray) -> None:
        self.W_proj = val

    @property
    def _h_fast(self) -> np.ndarray:
        return self._h

    @_h_fast.setter
    def _h_fast(self, val: np.ndarray) -> None:
        self._h = val

    # ------------------------------------------------------------------
    # F-02: Persistent Dynamical State Checkpoint & Recovery
    # ------------------------------------------------------------------

    def snapshot_dynamical_state(self, epoch_id: Optional[int] = None) -> DynamicalStateSnapshot:
        """
        Snapshot canonical dynamical state under strict descending lock discipline.
        Acquires _step_lock -> _state_lock, copies arrays within <= 1ms, and releases
        locks before returning to ensure zero disk I/O under locks.
        """
        with self._step_lock:
            with self._state_lock:
                h_copy = self._h.copy()
                s_copy = self._s_slow.copy()
                m_copy = self._m_homeo.copy()
                pad_snap = self._pad_snapshot

        return DynamicalStateSnapshot(
            h_fast=h_copy,
            s_slow=s_copy,
            created_at=time.time(),
            m_homeo=m_copy,
            pad={
                "pleasure": pad_snap.pleasure,
                "arousal": pad_snap.arousal,
                "dominance": pad_snap.dominance,
            },
            epoch_id=epoch_id,
        )

    def checkpoint(
        self,
        filepath: Optional[Union[str, Path]] = None,
        epoch_id: Optional[int] = None,
    ) -> Optional[Path]:
        """
        Atomically persist a coherent dynamical state snapshot to disk.
        Zero disk I/O under locks: snapshot is created under locks and serialized after release.
        """
        target = Path(filepath) if filepath else self._storage_path
        if target is None:
            return None
        snapshot = self.snapshot_dynamical_state(epoch_id=epoch_id)
        return save_dynamical_checkpoint(snapshot, filepath=target)

    def apply_dynamical_snapshot(
        self,
        snapshot: DynamicalStateSnapshot,
        apply_elapsed_time: bool = True,
        current_time: Optional[float] = None,
    ) -> None:
        """
        Restore dynamical vectors into live runtime state.
        Under _step_lock -> _state_lock, sets _h, _s_slow, and updates PAD.
        If apply_elapsed_time is True and elapsed physical time > 0, integrates
        system through unforced rest interval using canonical integrate_unforced_idle().
        """
        with self._step_lock:
            with self._state_lock:
                self._h = np.clip(snapshot.h_fast.copy(), -1.0, 1.0)
                self._s_slow = np.clip(snapshot.s_slow.copy(), -1.0, 1.0)
                if snapshot.m_homeo is not None:
                    self._m_homeo = np.clip(snapshot.m_homeo.copy(), 0.0, 1.0)
                self._pad_snapshot = self._project_to_pad(self._h, self._s_slow)

        if apply_elapsed_time:
            now = time.time() if current_time is None else current_time
            elapsed_s = max(0.0, now - snapshot.created_at)
            if elapsed_s > 0.0:
                self.integrate_unforced_idle(
                    duration_s=elapsed_s,
                    dt=self._config.ode_step_size,
                    record_trajectory=False,
                )

    def restore_from_checkpoint(
        self,
        filepath: Optional[Union[str, Path]] = None,
        apply_elapsed_time: bool = True,
        current_time: Optional[float] = None,
    ) -> bool:
        """
        Attempt to restore dynamical state from the latest valid checkpoint.
        Falls back to previous valid checkpoint if primary is corrupted, or
        returns False (retaining existing initial Philia baseline) if no valid
        checkpoint exists.
        """
        target = Path(filepath) if filepath else self._storage_path
        if target is None:
            return False
        snapshot = load_dynamical_checkpoint(target)
        if snapshot is None:
            return False
        self.apply_dynamical_snapshot(
            snapshot,
            apply_elapsed_time=apply_elapsed_time,
            current_time=current_time,
        )
        return True

    # ------------------------------------------------------------------
    # Lifecycle
    # ------------------------------------------------------------------

    def start(self) -> None:
        """Start the Fast_Loop background thread."""
        if self._thread is not None and self._thread.is_alive():
            return  # already running
        self._stop_event.clear()
        self._thread = threading.Thread(
            target=self._fast_loop_worker,
            name="EmotionCore-FastLoop",
            daemon=True,
        )
        self._thread.start()

    def stop(self) -> None:
        """Signal the Fast_Loop to stop. Does not join — caller must join if needed."""
        self._stop_event.set()

    def is_alive(self) -> bool:
        """Return True if the Fast_Loop thread is alive."""
        return self._thread is not None and self._thread.is_alive()

    def tick_count(self) -> int:
        """Monotonically increasing count of completed Fast_Loop ticks."""
        return self._tick_counter

    # ------------------------------------------------------------------
    # Thread-safe API & Public Accessors
    # ------------------------------------------------------------------

    def get_pad_state(self) -> PADState:
        """
        Return a snapshot of the current PAD_State.

        Acquires _state_lock with a 1 ms deadline (Requirement 1.9).
        Returns last known snapshot if the lock cannot be acquired in time.
        """
        acquired = self._state_lock.acquire(timeout=0.001)
        try:
            return self._pad_snapshot
        finally:
            if acquired:
                self._state_lock.release()

    def get_fast_state(self) -> np.ndarray:
        """Return a thread-safe snapshot copy of the fast reactive hidden state."""
        with self._state_lock:
            return self._h.copy()

    def get_slow_state(self) -> np.ndarray:
        """Return a thread-safe snapshot copy of the slow affective latent field."""
        with self._state_lock:
            return self._s_slow.copy()

    def get_slow_latent_state(self) -> np.ndarray:
        """
        Return a thread-safe snapshot copy of the live slow affective latent field (s_slow).
        Adheres to <= 1ms read deadline under _state_lock.
        """
        with self._state_lock:
            return self._s_slow.copy()

    @property
    def config(self) -> EmotionConfig:
        """Return read-only reference to the active EmotionConfig."""
        return self._config

    def inject_recollection(
        self, r_slow: np.ndarray, duration_sec: Optional[float] = None
    ) -> None:
        """
        Inject an external affective recollection forcing signal into the slow latent field.

        Thread-safe under _step_lock. Duration is tracked strictly in simulation/integration
        time (dt) to ensure deterministic trajectory evolution independent of wall-clock timing.
        """
        if not self._config.enable_affective_recollection:
            return

        Hs = self._config.hidden_slow_dim
        if len(r_slow) != Hs:
            logger.warning(
                "EmotionCore.inject_recollection: dimension mismatch (expected %d, got %d); padded/truncated.",
                Hs,
                len(r_slow),
            )
            vec = np.zeros(Hs, dtype=np.float64)
            n = min(Hs, len(r_slow))
            vec[:n] = r_slow[:n]
        else:
            vec = np.array(r_slow, dtype=np.float64)

        if not np.all(np.isfinite(vec)):
            logger.warning(
                "EmotionCore.inject_recollection: non-finite values detected; sanitized to zeros."
            )
            vec = np.zeros(Hs, dtype=np.float64)

        dur = (
            duration_sec
            if duration_sec is not None
            else self._config.recollection_pulse_duration_sec
        )
        with self._step_lock:
            self._recollection_forcing = np.clip(vec, -1.0, 1.0)
            self._recollection_remaining_sim = max(0.0, float(dur))

    def get_attractor_distance(self) -> float:
        """Return the Euclidean distance from current PAD to Philia resting coordinate."""
        with self._state_lock:
            p = np.array([self._pad_snapshot.pleasure, self._pad_snapshot.arousal, self._pad_snapshot.dominance])
            return float(np.linalg.norm(p - self.p_philia))

    def update_homeostatic_context(
        self, energy: float, load: float, tension: float, stability: float
    ) -> None:
        """
        Push updated homeostatic somatic markers into the limbic slow-layer context.
        Thread-safe under _step_lock.
        """
        with self._step_lock:
            self._m_homeo = np.clip(
                np.array([energy, load, tension, stability], dtype=np.float64),
                0.0,
                1.0,
            )

    @property
    def _pending_stimulus(self) -> Optional[Tuple[int, np.ndarray]]:
        """Backwards-compatible view of the front pending stimulus."""
        with self._stimulus_lock:
            return self._pending_stimuli[0] if self._pending_stimuli else None

    @_pending_stimulus.setter
    def _pending_stimulus(self, value: Optional[Tuple[int, np.ndarray]]) -> None:
        """Backwards-compatible setter for clearing or setting pending stimuli."""
        with self._stimulus_lock:
            self._pending_stimuli.clear()
            if value is not None:
                self._pending_stimuli.append(value)

    def push_stimulus(self, vector: np.ndarray) -> int:
        """
        Inject a Stimulus_Vector to be consumed on the next ODE step.

        Thread-safe. Assigns a monotonically increasing sequence token.
        Appends to internal FIFO queue so no stimuli are dropped.
        Returns the assigned sequence token.
        """
        # Resize input weight matrices if the stimulus dimensionality changed
        self._ensure_input_dim(len(vector))
        with self._stimulus_lock:
            self._stimulus_seq += 1
            seq = self._stimulus_seq
            self._pending_stimuli.append((seq, np.array(vector, dtype=np.float64)))
            return seq

    def reset_to_resting(self) -> None:
        """
        Reset fast state, slow state, pending stimuli, learned weights, and PAD state to resting baseline.
        Adheres to concurrency lock hierarchy: _step_lock -> _train_lock -> _stimulus_lock -> _state_lock.
        """
        with self._step_lock:
            with self._train_lock:
                rng = np.random.default_rng(_INIT_SEED)
                H = self._config.hidden_dim
                Hs = self._config.hidden_slow_dim
                current_n = self.U_f.shape[1]

                self.W_f = _xavier_uniform((H, H), rng) * 0.20
                self.U_f = _xavier_uniform((H, current_n), rng) * 0.30
                if current_n >= 3 and H >= 3:
                    self.U_f[0, 0] = 1.00
                    self.U_f[1, 1] = 1.00
                    self.U_f[2, 2] = 0.80
                self.b_f = np.zeros(H, dtype=np.float64)

                self.W_tau = _xavier_uniform((H, H), rng) * 0.10
                self.U_tau = _xavier_uniform((H, current_n), rng) * 0.10
                self.b_tau = np.zeros(H, dtype=np.float64)

                self.W_proj = _xavier_uniform((3, H), rng) * 0.10
                if H >= 3:
                    self.W_proj[0, 0] = 0.70
                    self.W_proj[1, 1] = 0.70
                    self.W_proj[2, 2] = 0.60
                self.b_proj = np.zeros(3, dtype=np.float64)

                self.W_fs = np.zeros((H, Hs), dtype=np.float64)
                if H >= 3 and Hs >= 3:
                    self.W_fs[0, 0] = self._config.w_fs_coupling
                    self.W_fs[1, 1] = self._config.w_fs_coupling
                    self.W_fs[2, 2] = self._config.w_fs_coupling * 0.80

                self.W_sf = np.zeros((Hs, H), dtype=np.float64)
                if Hs >= 3 and H >= 3:
                    self.W_sf[0, 0] = self._config.w_sf_coupling
                    self.W_sf[1, 1] = self._config.w_sf_coupling
                    self.W_sf[2, 2] = self._config.w_sf_coupling * 0.80

                self.W_sh = np.zeros((Hs, 4), dtype=np.float64)
                if Hs >= 3:
                    self.W_sh[0, 2] = -0.60 * self._config.w_homeo_coupling
                    self.W_sh[0, 1] = -0.20 * self._config.w_homeo_coupling
                    self.W_sh[1, 2] = +0.70 * self._config.w_homeo_coupling
                    self.W_sh[1, 1] = +0.10 * self._config.w_homeo_coupling
                    self.W_sh[1, 0] = +0.50 * self._config.w_homeo_coupling

                self.W_proj_s = np.zeros((3, Hs), dtype=np.float64)
                if Hs >= 3:
                    self.W_proj_s[0, 0] = 0.45
                    self.W_proj_s[1, 1] = 0.45
                    self.W_proj_s[2, 2] = 0.35

                # Phase 20: Reset recollection forcing and coupling matrix
                self.W_rec = np.eye(Hs, dtype=np.float64) * self._config.recollection_coupling_weight
                self._recollection_forcing = np.zeros(Hs, dtype=np.float64)
                self._recollection_remaining_sim = 0.0

                # Phase 21: Reset W_rel and R_t
                raw_w_rel = _xavier_uniform((Hs, 4), rng)
                s_max = np.linalg.svd(raw_w_rel, compute_uv=False)[0]
                target_norm = min(0.0475, self._config.w_rel_spectral_bound)
                if s_max > 0:
                    self.W_rel = raw_w_rel * (target_norm / s_max)
                else:
                    self.W_rel = raw_w_rel
                self._R_t = self.R_0.copy()

                with self._stimulus_lock:
                    self._pending_stimuli.clear()
                    self._stimulus_seq = 0
                    self._committed_stimulus_seq = 0

                with self._state_lock:
                    self._h = np.zeros(H, dtype=np.float64)
                    self._s_slow = self.s_philia.copy()
                    self._m_homeo = self.m_homeo_resting.copy()
                    p, a, d = self._config.resting_baseline
                    self._pad_resting = PADState(
                        pleasure=float(p),
                        arousal=float(a),
                        dominance=float(d),
                        timestamp=time.monotonic(),
                    )
                    self._pad_snapshot = self._pad_resting

    # ------------------------------------------------------------------
    # Core Coupled MT-LNN Computation
    # ------------------------------------------------------------------

    def _ode_step(
        self,
        h: np.ndarray,
        x: np.ndarray,
        r_step: Optional[np.ndarray] = None,
    ) -> Tuple[np.ndarray, np.ndarray]:
        """
        Advance the coupled fast/slow states by one ODE integration step.

        Uses scipy solve_ivp with RK45. Intermediate values are clamped to
        [-1.0, 1.0] within the RHS to maintain numerical bounded stability.
        """
        with self._train_lock:
            W_tau = self.W_tau.copy()
            U_tau = self.U_tau.copy()
            b_tau = self.b_tau.copy()
            W_f = self.W_f.copy()
            U_f = self.U_f.copy()
            b_f = self.b_f.copy()
            W_fs = self.W_fs.copy()
            W_sf = self.W_sf.copy()
            W_sh = self.W_sh.copy()
            W_rec = self.W_rec.copy()
            W_rel = self.W_rel.copy()
            s_philia = self.s_philia.copy()
            m_homeo = self._m_homeo.copy()
            R_t = self._R_t.copy()

        Hf = len(h)
        Hs = len(self._s_slow)
        y0 = np.concatenate([h, self._s_slow])
        dt = self._config.ode_step_size
        delta_m = m_homeo - self.m_homeo_resting
        r_forcing = (
            np.zeros(Hs, dtype=np.float64)
            if r_step is None
            else np.array(r_step, dtype=np.float64)
        )

        def rhs(t: float, y: np.ndarray) -> np.ndarray:
            y_f = np.clip(y[:Hf], -1.0, 1.0)
            y_s = np.clip(y[Hf:], -1.0, 1.0)

            if self._config.enable_relational_consolidation:
                delta_r = np.clip(R_t, 0.0, 1.0) - self.R_0
                s_eff = s_philia + W_rel @ delta_r
                delta_s = y_s - s_eff
            else:
                delta_s = y_s - s_philia

            # Fast timescale
            tau_f_raw = softplus(W_tau @ y_f + U_tau @ x + b_tau)
            tau_f = np.clip(tau_f_raw, self._config.tau_fast_min, self._config.tau_fast_max)

            f_fast = np.tanh(W_f @ y_f + W_fs @ delta_s + U_f @ x + b_f)
            dh_fast = (-y_f + f_fast) / tau_f

            # Slow timescale (fast charging attack, slow relaxation decay)
            tau_decay = self._config.tau_slow_decay
            tau_charge = self._config.tau_slow_charge

            forcing = np.tanh(W_sf @ y_f + W_sh @ delta_m + W_rec @ r_forcing)
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
        if not np.all(np.isfinite(y_next)):
            logger.warning("EmotionCore: non-finite values detected in ODE solve; falling back to Philia baseline.")
            self._s_slow = s_philia.copy()
            return np.zeros(Hf, dtype=np.float64)

        h_next = np.clip(y_next[:Hf], -1.0, 1.0)
        s_next = np.clip(y_next[Hf:], -1.0, 1.0)
        self._s_slow = s_next
        return h_next

    def _project_to_pad(self, h: np.ndarray, s: Optional[np.ndarray] = None) -> PADState:
        """
        Map fast hidden state h and slow state s -> PADState via coupled projection + clamp.
        Anchored at Philia dynamic resting attractor.
        """
        if s is None:
            s = self._s_slow
        delta_s = s - self.s_philia
        pad_raw = (self.W_proj @ h) + (self.W_proj_s @ delta_s) + self.p_philia + self.b_proj
        pad_clamped = np.clip(pad_raw, -1.0, 1.0)
        return PADState(
            pleasure=float(pad_clamped[0]),
            arousal=float(pad_clamped[1]),
            dominance=float(pad_clamped[2]),
            timestamp=time.monotonic(),
        )

    # ------------------------------------------------------------------
    # Fast Loop worker & Turn Step Methods
    # ------------------------------------------------------------------

    def _consume_stimulus(self) -> Tuple[np.ndarray, Optional[int]]:
        """
        Atomically return the pending stimulus (vector, seq) in FIFO order and clear it.
        If no pending stimulus, returns (zero_vector, None).
        """
        with self._stimulus_lock:
            if self._pending_stimuli:
                seq, vec = self._pending_stimuli.popleft()
                return vec, seq
            return np.zeros(self.U_f.shape[1], dtype=np.float64), None

    def _step_once_unlocked(self, custom_timestamp: Optional[float] = None) -> PADState:
        """
        Advance the MT-LNN ODE by exactly one tick deterministically.
        Must be called under _step_lock.
        Consumes any pending stimulus (or zeroes if none).
        Updates hidden state, slow state, PAD snapshot, and committed sequence token.
        """
        seq = None
        try:
            x, seq = self._consume_stimulus()
            if not np.all(np.isfinite(x)):
                logger.warning("EmotionCore: non-finite stimulus vector received; sanitized to zeros.")
                x = np.zeros_like(x)

            # Phase 20: Snapshot recollection forcing in simulation time
            dt = self._config.ode_step_size
            if self._config.enable_affective_recollection and self._recollection_remaining_sim > 0.0:
                r_step = self._recollection_forcing.copy()
                self._recollection_remaining_sim = max(0.0, self._recollection_remaining_sim - dt)
            else:
                r_step = np.zeros(self._config.hidden_slow_dim, dtype=np.float64)

            import inspect
            try:
                sig = inspect.signature(self._ode_step)
                if "r_step" in sig.parameters:
                    h_res = self._ode_step(self._h, x, r_step=r_step)
                else:
                    h_res = self._ode_step(self._h, x)
            except Exception:
                h_res = self._ode_step(self._h, x, r_step=r_step)
            if isinstance(h_res, tuple) and len(h_res) == 2:
                h_new, s_new = h_res
            else:
                h_new = h_res
                s_new = self._s_slow

            pad = self._project_to_pad(h_new, s_new)
            if custom_timestamp is not None:
                pad = PADState(
                    pleasure=pad.pleasure,
                    arousal=pad.arousal,
                    dominance=pad.dominance,
                    timestamp=custom_timestamp,
                )
            self._h = h_new
            self._s_slow = s_new
            with self._state_lock:
                self._pad_snapshot = pad
            if seq is not None:
                self._committed_stimulus_seq = max(self._committed_stimulus_seq, seq)
            self._tick_counter += 1
            return pad
        except Exception:
            logger.exception("EmotionCore step_once exception — resetting to resting baseline")
            Hf = self._config.hidden_dim
            Hs = self._config.hidden_slow_dim
            self._h = np.zeros(Hf, dtype=np.float64)
            self._s_slow = self.s_philia.copy()
            self._m_homeo = self.m_homeo_resting.copy()
            self._recollection_forcing = np.zeros(Hs, dtype=np.float64)
            self._recollection_remaining_sim = 0.0
            p, a, d = self._config.resting_baseline
            resting = PADState(
                pleasure=float(p),
                arousal=float(a),
                dominance=float(d),
                timestamp=custom_timestamp if custom_timestamp is not None else time.monotonic(),
            )
            with self._state_lock:
                self._pad_snapshot = resting
            if seq is not None:
                self._committed_stimulus_seq = max(self._committed_stimulus_seq, seq)
            return resting

    def step_once(self, custom_timestamp: Optional[float] = None) -> PADState:
        """
        Advance the MT-LNN ODE by exactly one tick deterministically.
        Thread-safe; serializes ODE stepping via _step_lock.
        Consumes any pending stimulus (or zeroes if none).
        Allows virtual clock (SimClock) to drive EmotionCore in simulation mode.
        """
        with self._step_lock:
            return self._step_once_unlocked(custom_timestamp=custom_timestamp)

    def commit_stimulus(self, target_seq: Optional[int] = None) -> PADState:
        """
        Deterministically commit the state transition for a submitted stimulus.

        Enforces the temporal boundary for cognitive turns:
          Case A: target stimulus has not yet been committed (committed_seq < target_seq).
                  Advances the ODE under _step_lock, consuming and integrating pending
                  stimuli in causal FIFO order, publishing the new PAD snapshot, and
                  marking each committed.
          Case B: target stimulus was already consumed and committed by the background
                  worker thread in the interim (committed_seq >= target_seq).
                  Observes that target_seq is already committed; does NOT execute a duplicate
                  ODE tick (guaranteeing exactly-once execution). Returns the committed state.

        Parameters
        ----------
        target_seq : Optional[int]
            The sequence token of the stimulus to commit. If None, targets the latest
            submitted stimulus token (_stimulus_seq).

        Returns
        -------
        PADState
            The committed post-stimulus PAD state snapshot.
        """
        with self._step_lock:
            with self._stimulus_lock:
                max_submitted = self._stimulus_seq
                if target_seq is None:
                    target_seq = max_submitted

            target_seq = min(target_seq, max_submitted)
            if target_seq <= 0:
                return self.get_pad_state()

            # Drain pending stimuli up to target_seq in FIFO order
            while self._committed_stimulus_seq < target_seq:
                with self._stimulus_lock:
                    if not self._pending_stimuli:
                        # Defensive: pending queue empty; avoid infinite idle-looping
                        break
                self._step_once_unlocked()

            return self.get_pad_state()

    def _fast_loop_worker(self) -> None:
        """Background thread: advance MT-LNN state continuously."""
        while not self._stop_event.is_set():
            tick_start = time.monotonic()
            self.step_once()
            elapsed_ms = (time.monotonic() - tick_start) * 1000.0
            sleep_s = max(0.0, self._config.loop_cadence_ms - elapsed_ms) / 1000.0
            time.sleep(sleep_s)

    # ------------------------------------------------------------------
    # Internal: dynamic input dimension handling
    # ------------------------------------------------------------------

    def _ensure_input_dim(self, n: int) -> None:
        """
        Resize U_f and U_tau if incoming stimulus has a different dimensionality.
        Preserves existing recurrent and cross-layer weights.
        """
        current_n = self.U_f.shape[1]
        if n == current_n:
            return
        rng = np.random.default_rng(_INIT_SEED)
        H = self._config.hidden_dim
        self.U_f = _xavier_uniform((H, n), rng) * 0.30
        if n >= 3 and H >= 3:
            self.U_f[0, 0] = 1.00
            self.U_f[1, 1] = 1.00
            self.U_f[2, 2] = 0.80
        self.U_tau = _xavier_uniform((H, n), rng) * 0.10
        logger.debug("EmotionCore: resized input weights from dim %d to %d", current_n, n)

    # ------------------------------------------------------------------
    # Phase 21: Relational State, Weight Access & Consolidation API
    # ------------------------------------------------------------------

    def get_parameter_state(self) -> SynapticParameterState:
        """Return snapshot of trainable synaptic parameters under _train_lock."""
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
        """
        Atomically swap synaptic parameters under _train_lock.
        Enforces spectral norm constraint sigma_max(W_rel) <= w_rel_spectral_bound.
        """
        with self._train_lock:
            s_max = params.w_rel_spectral_norm
            if s_max > self._config.w_rel_spectral_bound:
                scale = self._config.w_rel_spectral_bound / (s_max + 1e-12)
                params.W_rel = params.W_rel * scale

            self.W_f = params.W_f.copy()
            self.U_f = params.U_f.copy()
            self.b_f = params.b_f.copy()
            self.W_tau = params.W_tau.copy()
            self.U_tau = params.U_tau.copy()
            self.b_tau = params.b_tau.copy()
            self.W_rel = params.W_rel.copy()

    def get_relational_weights(self) -> np.ndarray:
        """Return copy of W_rel under _train_lock."""
        with self._train_lock:
            return self.W_rel.copy()

    def set_relational_weights(self, w_rel: np.ndarray) -> None:
        """Set and clamp W_rel under _train_lock."""
        w = np.array(w_rel, dtype=np.float64)
        s_max = np.linalg.svd(w, compute_uv=False)[0] if len(w) > 0 else 0.0
        if s_max > self._config.w_rel_spectral_bound:
            scale = self._config.w_rel_spectral_bound / (s_max + 1e-12)
            w = w * scale
        with self._train_lock:
            self.W_rel = w

    def get_relationship_context(self) -> np.ndarray:
        """Return copy of current relationship context R_t under _step_lock."""
        with self._step_lock:
            return self._R_t.copy()

    def update_relationship_context(self, R: np.ndarray) -> None:
        """
        Update relationship context R_t under _step_lock.
        ADR-022 compliant: called at Stage 16.3 post-turn.
        """
        with self._step_lock:
            self._R_t = np.clip(np.array(R, dtype=np.float64), 0.0, 1.0)

    def get_effective_slow_attractor(self, R: Optional[np.ndarray] = None) -> np.ndarray:
        """
        Compute relationship-conditioned slow attractor:
        s*_eff(R) = s*_philia + W_rel (R_t - R_0) when enabled;
        otherwise s*_philia bit-exact.
        """
        if not self._config.enable_relational_consolidation:
            return self.s_philia.copy()

        with self._step_lock:
            R_val = self._R_t if R is None else np.clip(np.array(R, dtype=np.float64), 0.0, 1.0)
            delta_r = R_val - self.R_0

        with self._train_lock:
            displacement = self.W_rel @ delta_r
        return self.s_philia + displacement

    def compute_resting_pad(self, R: Optional[np.ndarray] = None) -> np.ndarray:
        """
        Evaluate output PAD at resting equilibrium for given relationship state:
        h_fast = 0, s_slow = s*_eff(R).
        """
        s_eff = self.get_effective_slow_attractor(R)
        h_zero = np.zeros(self._config.hidden_dim, dtype=np.float64)
        pad_state = self._project_to_pad(h_zero, s_eff)
        return np.array([pad_state.pleasure, pad_state.arousal, pad_state.dominance], dtype=np.float64)

    def get_consolidation_engine(self) -> Optional[ConsolidationEngine]:
        """Return consolidation engine instance if enabled."""
        return self._consolidation_engine

    def record_consolidation_experience(
        self,
        stimulus: np.ndarray,
        h_before: np.ndarray,
        h_after: np.ndarray,
        s_slow: np.ndarray,
        salience: float,
        relational_state: Optional[np.ndarray] = None,
        r_slow: Optional[np.ndarray] = None,
    ) -> None:
        """Record salient turn transition into consolidation engine."""
        if not self._config.enable_relational_consolidation or self._consolidation_engine is None:
            return
        r_val = self._R_t if relational_state is None else relational_state
        self._consolidation_engine.record_experience(
            stimulus=stimulus,
            h_before=h_before,
            h_after=h_after,
            s_slow=s_slow,
            salience=salience,
            relational_state=r_val,
            r_slow=r_slow,
        )

    def run_offline_consolidation(
        self,
        batch: Optional[List[ConsolidationExperience]] = None,
        **kwargs: Any,
    ) -> Tuple[SynapticParameterState, Dict[str, float]]:
        """Trigger offline consolidation via ConsolidationEngine on CPU."""
        if not self._config.enable_relational_consolidation or self._consolidation_engine is None:
            return self.get_parameter_state(), {"loss": 0.0, "backward_latency_ms": 0.0}
        return self._consolidation_engine.run_offline_consolidation(
            batch=batch,
            emotion_core=self,
            **kwargs,
        )

    def step_ode(
        self,
        stimulus: np.ndarray,
        dt: float = 0.20,
        recollection_forcing: Optional[np.ndarray] = None,
    ) -> Tuple[np.ndarray, np.ndarray]:
        """
        Execute one discrete numerical step of coupled MT-LNN ODE using forward Euler.
        Matches the validated Phase 21 forward dynamics with sub-millisecond execution.
        Returns: (h_fast, s_slow)
        """
        with self._step_lock:
            with self._train_lock:
                W_f, U_f, b_f = self.W_f.copy(), self.U_f.copy(), self.b_f.copy()
                W_tau, U_tau, b_tau = self.W_tau.copy(), self.U_tau.copy(), self.b_tau.copy()
                W_fs, W_sf, W_sh, W_rec = self.W_fs.copy(), self.W_sf.copy(), self.W_sh.copy(), self.W_rec.copy()
                W_rel = self.W_rel.copy()
                s_philia = self.s_philia.copy()
                R_t = self._R_t.copy()

            if self._config.enable_relational_consolidation:
                delta_r = np.clip(R_t, 0.0, 1.0) - self.R_0
                s_eff = s_philia + W_rel @ delta_r
            else:
                s_eff = s_philia

            h = self._h.copy()
            s = self._s_slow.copy()

            # Time constant
            tau_input = W_tau @ h + U_tau @ stimulus + b_tau
            tau_fast = np.clip(softplus(tau_input), self._config.tau_fast_min, self._config.tau_fast_max)

            # Fast ODE derivative
            delta_s_eff = s - s_eff
            h_input = W_f @ h + U_f @ stimulus + (W_fs @ delta_s_eff) + b_f
            dh_dt = (-h + np.tanh(h_input)) / tau_fast

            # Slow ODE derivative
            rec_term = (
                recollection_forcing
                if recollection_forcing is not None
                else np.zeros(self._config.hidden_slow_dim, dtype=np.float64)
            )
            delta_m = self._m_homeo - self.m_homeo_resting
            homeo_term = W_sh @ delta_m

            charge_input = (W_sf @ h) + homeo_term + rec_term
            ds_dt = -(s - s_eff) / self._config.tau_slow_decay + np.tanh(charge_input) / self._config.tau_slow_charge

            # Forward Euler step
            h_next = np.clip(h + dh_dt * dt, -1.0, 1.0)
            s_next = np.clip(s + ds_dt * dt, -1.0, 1.0)

            self._h = h_next
            self._s_slow = s_next

            with self._state_lock:
                pad_out = self._project_to_pad(h_next, s_next)
                self._pad_snapshot = pad_out

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

        F-02 Ratified Hybrid Model (D-02):
        - Short downtime (duration_s <= tau_candidate): exact numerical forward Euler.
        - Long downtime (duration_s >= tau_asymptotic): direct equilibrium projection O(1)
          to relationally conditioned attractor s*_eff(R_t), h_fast -> 0, E -> 1.0, C -> 0.0.
        - Intermediate (tau_candidate < duration_s < tau_asymptotic): forward Euler up to
          tau_candidate, followed by asymptotic exponential decay toward s*_eff(R_t).
        """
        tau_candidate = float(getattr(self._config, "recovery_short_replay_cutoff_s", 180.0))
        tau_asymptotic = float(getattr(self._config, "recovery_asymptotic_cutoff_s", 300.0))
        duration_s = max(0.0, float(duration_s))

        traj_times: List[float] = []
        traj_energies: List[float] = []
        traj_tensions: List[float] = []
        traj_loads: List[float] = []
        traj_stabilities: List[float] = []
        pad_history: List[np.ndarray] = []
        slow_history: List[np.ndarray] = []

        # Relationally conditioned attractor target
        s_eff = self.get_effective_slow_attractor()

        # ── Case 1: Long-downtime Direct Equilibrium Projection (Delta t >= tau_asymptotic) ──
        if duration_s >= tau_asymptotic:
            with self._step_lock:
                self._h = np.zeros(self._config.hidden_dim, dtype=np.float64)
                self._s_slow = s_eff.copy()
                self._m_homeo = np.array([1.0, 0.0, 0.0, 1.0], dtype=np.float64)
                with self._state_lock:
                    pad_snap = self._project_to_pad(self._h, self._s_slow)
                    self._pad_snapshot = pad_snap

            if record_trajectory:
                traj_times.append(duration_s)
                traj_energies.append(1.0)
                traj_loads.append(0.0)
                traj_tensions.append(0.0)
                traj_stabilities.append(1.0)
                pad_history.append(np.array([pad_snap.pleasure, pad_snap.arousal, pad_snap.dominance]))
                slow_history.append(self._s_slow.copy())

            ht = HomeostaticTrajectory(
                timestamps=traj_times,
                energies=traj_energies,
                tensions=traj_tensions,
                cognitive_loads=traj_loads,
                stabilities=traj_stabilities,
            )
            return (
                np.array(pad_history) if pad_history else np.zeros((0, 3)),
                np.array(slow_history) if slow_history else np.zeros((0, self._config.hidden_slow_dim)),
                ht,
            )

        # ── Numerical Replay (Euler) for min(duration_s, tau_candidate) ──
        euler_duration = min(duration_s, tau_candidate)
        n_steps = int(euler_duration / dt) if dt > 0 else 0
        stim_zero = np.zeros(self.U_f.shape[1], dtype=np.float64)

        gamma_E = 0.05
        gamma_T = 0.10
        gamma_C = 0.08
        curr_t = 0.0

        for _ in range(n_steps):
            e_curr = self._m_homeo[0]
            c_curr = self._m_homeo[1]
            t_curr = self._m_homeo[2]

            e_next = e_curr + gamma_E * (1.0 - e_curr) * dt
            t_next = t_curr - gamma_T * t_curr * dt
            c_next = c_curr - gamma_C * c_curr * dt
            s_next = 1.0 - 0.5 * t_next

            with self._step_lock:
                self._m_homeo = np.clip(
                    np.array([e_next, c_next, t_next, s_next], dtype=np.float64),
                    0.0,
                    1.0,
                )

            h_step, s_step = self.step_ode(stim_zero, dt=dt)
            curr_t += dt

            if record_trajectory:
                with self._state_lock:
                    pad_snap = self._pad_snapshot
                traj_times.append(curr_t)
                traj_energies.append(float(self._m_homeo[0]))
                traj_loads.append(float(self._m_homeo[1]))
                traj_tensions.append(float(self._m_homeo[2]))
                traj_stabilities.append(float(self._m_homeo[3]))
                pad_history.append(np.array([pad_snap.pleasure, pad_snap.arousal, pad_snap.dominance]))
                slow_history.append(s_step.copy())

        # ── Case 2: Intermediate Relaxation (tau_candidate < duration_s < tau_asymptotic) ──
        if duration_s > tau_candidate:
            rem_time = duration_s - tau_candidate
            tau_decay = self._config.tau_slow_decay
            decay_factor = np.exp(-rem_time / tau_decay) if tau_decay > 0 else 0.0
            with self._step_lock:
                s_cur = self._s_slow.copy()
                s_rec = s_eff + (s_cur - s_eff) * decay_factor
                self._h = np.zeros(self._config.hidden_dim, dtype=np.float64)
                self._s_slow = np.clip(s_rec, -1.0, 1.0)
                self._m_homeo = np.array([1.0, 0.0, 0.0, 1.0], dtype=np.float64)
                with self._state_lock:
                    pad_snap = self._project_to_pad(self._h, self._s_slow)
                    self._pad_snapshot = pad_snap

            if record_trajectory:
                traj_times.append(duration_s)
                traj_energies.append(1.0)
                traj_loads.append(0.0)
                traj_tensions.append(0.0)
                traj_stabilities.append(1.0)
                pad_history.append(np.array([pad_snap.pleasure, pad_snap.arousal, pad_snap.dominance]))
                slow_history.append(self._s_slow.copy())

        ht = HomeostaticTrajectory(
            timestamps=traj_times,
            energies=traj_energies,
            tensions=traj_tensions,
            cognitive_loads=traj_loads,
            stabilities=traj_stabilities,
        )
        return (
            np.array(pad_history) if pad_history else np.zeros((0, 3)),
            np.array(slow_history) if slow_history else np.zeros((0, self._config.hidden_slow_dim)),
            ht,
        )
