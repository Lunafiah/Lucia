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
from typing import Optional, Tuple

import numpy as np
from scipy.integrate import solve_ivp
from scipy.special import softplus

from src.core.config import EmotionConfig
from src.core.models import PADState

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

    def __init__(self, config: Optional[EmotionConfig] = None) -> None:
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

        # Loop control
        self._stop_event = threading.Event()
        self._thread: Optional[threading.Thread] = None
        self._tick_counter: int = 0

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
            s_philia = self.s_philia.copy()
            m_homeo = self._m_homeo.copy()

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
