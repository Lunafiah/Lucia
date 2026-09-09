"""
EmotionCore — continuous LNN-based emotional state machine.

Implements a Liquid Time-Constant (LTC) network:

    dh/dt = (-h + tanh(W_f·h + U_f·x + b_f)) / softplus(W_tau·h + U_tau·x + b_tau)

Hidden state h evolves continuously via scipy.integrate.solve_ivp (RK45).
A linear projection maps h → PAD space (pleasure, arousal, dominance).

The Fast_Loop runs in a background daemon thread, advancing the state every
loop_cadence_ms milliseconds regardless of user activity.

Threading model:
  - _state_lock:     protects _pad_snapshot (written by Fast_Loop, read by callers)
  - _stimulus_lock:  protects _pending_stimulus (written by push_stimulus, read by Fast_Loop)
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

# RNG seed for reproducible weight initialisation during Phase 1
_INIT_SEED = 42


def _xavier_uniform(shape: tuple, rng: np.random.Generator) -> np.ndarray:
    """Xavier uniform initialisation for a weight matrix of the given shape."""
    fan_in, fan_out = shape[-1], shape[0]
    limit = np.sqrt(6.0 / (fan_in + fan_out))
    return rng.uniform(-limit, limit, size=shape).astype(np.float64)


class EmotionCore:
    """
    Continuous LNN emotional state machine.

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
        N_in = 16  # default Stimulus_Vector dimensionality; updated via push_stimulus

        rng = np.random.default_rng(_INIT_SEED)

        # LTC weight matrices — fixed in Phase 1 (training deferred to Phase 2)
        self.W_f   = _xavier_uniform((H, H), rng)   # hidden × hidden
        self.U_f   = _xavier_uniform((H, N_in), rng) # hidden × input
        self.b_f   = np.zeros(H, dtype=np.float64)

        self.W_tau = _xavier_uniform((H, H), rng)
        self.U_tau = _xavier_uniform((H, N_in), rng)
        self.b_tau = np.zeros(H, dtype=np.float64)

        # PAD projection: (3, H) → pleasure, arousal, dominance
        self.W_proj = _xavier_uniform((3, H), rng)
        self.b_proj = np.zeros(3, dtype=np.float64)

        # Hidden state — initialised to resting baseline via projection
        self._h: np.ndarray = np.zeros(H, dtype=np.float64)

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

        # Phase 4: Training lock for atomic weight updates
        self._train_lock = threading.Lock()

        # Pending stimuli FIFO queue and sequence tracking (protected by _stimulus_lock)
        self._pending_stimuli: deque[Tuple[int, np.ndarray]] = deque()
        self._stimulus_lock = threading.Lock()
        self._stimulus_seq: int = 0
        self._committed_stimulus_seq: int = 0

        # Step synchronization lock (serializes ODE stepping between turn and background thread)
        self._step_lock = threading.Lock()

        # Loop control
        self._stop_event = threading.Event()
        self._thread: Optional[threading.Thread] = None
        self._tick_counter: int = 0

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
    # Thread-safe API
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
        Reset hidden state, pending stimulus, learned weights, and PAD state to resting baseline.
        Adheres to concurrency lock hierarchy: _step_lock -> _train_lock -> _stimulus_lock -> _state_lock.
        """
        with self._step_lock:
            with self._train_lock:
                rng = np.random.default_rng(_INIT_SEED)
                H = self._config.hidden_dim
                current_n = self.U_f.shape[1]
                self.W_f = _xavier_uniform((H, H), rng)
                self.U_f = _xavier_uniform((H, current_n), rng)
                self.b_f = np.zeros(H, dtype=np.float64)
                self.W_tau = _xavier_uniform((H, H), rng)
                self.U_tau = _xavier_uniform((H, current_n), rng)
                self.b_tau = np.zeros(H, dtype=np.float64)
                self.W_proj = _xavier_uniform((3, H), rng)
                self.b_proj = np.zeros(3, dtype=np.float64)

                with self._stimulus_lock:
                    self._pending_stimuli.clear()
                    self._stimulus_seq = 0
                    self._committed_stimulus_seq = 0

                with self._state_lock:
                    self._h = np.zeros(H, dtype=np.float64)
                    p, a, d = self._config.resting_baseline
                    self._pad_resting = PADState(
                        pleasure=float(p),
                        arousal=float(a),
                        dominance=float(d),
                        timestamp=time.monotonic(),
                    )
                    self._pad_snapshot = self._pad_resting

    # ------------------------------------------------------------------
    # Core computation
    # ------------------------------------------------------------------

    def _ode_step(self, h: np.ndarray, x: np.ndarray) -> np.ndarray:
        """
        Advance the hidden state by one ODE integration step.

        Uses scipy solve_ivp with RK45. Intermediate values are clamped to
        [-1.0, 1.0] within the RHS to prevent blow-up (Requirement 1.4).
        """
        with self._train_lock:
            W_tau = self.W_tau.copy()
            U_tau = self.U_tau.copy()
            b_tau = self.b_tau.copy()
            W_f = self.W_f.copy()
            U_f = self.U_f.copy()
            b_f = self.b_f.copy()

        def rhs(t: float, y: np.ndarray) -> np.ndarray:
            y_c = np.clip(y, -1.0, 1.0)  # intermediate clamp
            tau = softplus(W_tau @ y_c + U_tau @ x + b_tau)
            f = np.tanh(W_f @ y_c + U_f @ x + b_f)
            return (-y_c + f) / tau

        result = solve_ivp(
            rhs,
            t_span=(0.0, self._config.ode_step_size),
            y0=h,
            method="RK45",
            max_step=self._config.ode_step_size / 4.0,
            dense_output=False,
            vectorized=False,
        )
        h_new = result.y[:, -1]
        return np.clip(h_new, -1.0, 1.0)  # post-step clamp (Requirement 1.4, 1.7)

    def _project_to_pad(self, h: np.ndarray) -> PADState:
        """
        Map hidden state h → PADState via linear projection + clamp.

        Requirement 1.6, 1.7.
        """
        pad_raw = self.W_proj @ h + self.b_proj
        pad_clamped = np.clip(pad_raw, -1.0, 1.0)
        return PADState(
            pleasure=float(pad_clamped[0]),
            arousal=float(pad_clamped[1]),
            dominance=float(pad_clamped[2]),
            timestamp=time.monotonic(),
        )

    # ------------------------------------------------------------------
    # Fast Loop worker
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
        Advance the LNN ODE by exactly one tick deterministically.
        Must be called under _step_lock.
        Consumes any pending stimulus (or zeroes if none).
        Updates hidden state, PAD snapshot, and committed sequence token.
        """
        seq = None
        try:
            x, seq = self._consume_stimulus()
            h_new = self._ode_step(self._h, x)
            pad = self._project_to_pad(h_new)
            if custom_timestamp is not None:
                pad = PADState(
                    pleasure=pad.pleasure,
                    arousal=pad.arousal,
                    dominance=pad.dominance,
                    timestamp=custom_timestamp,
                )
            self._h = h_new
            with self._state_lock:
                self._pad_snapshot = pad
            if seq is not None:
                self._committed_stimulus_seq = max(self._committed_stimulus_seq, seq)
            self._tick_counter += 1
            return pad
        except Exception:
            logger.exception("EmotionCore step_once exception — resetting to resting baseline")
            self._h = np.zeros(self._config.hidden_dim, dtype=np.float64)
            resting = PADState(
                pleasure=float(self._config.resting_baseline[0]),
                arousal=float(self._config.resting_baseline[1]),
                dominance=float(self._config.resting_baseline[2]),
                timestamp=custom_timestamp if custom_timestamp is not None else time.monotonic(),
            )
            with self._state_lock:
                self._pad_snapshot = resting
            if seq is not None:
                self._committed_stimulus_seq = max(self._committed_stimulus_seq, seq)
            return resting

    def step_once(self, custom_timestamp: Optional[float] = None) -> PADState:
        """
        Advance the LNN ODE by exactly one tick deterministically.
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
                self._step_once_unlocked()

            return self.get_pad_state()

    def _fast_loop_worker(self) -> None:
        """Background thread: advance LNN state continuously."""
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
        Resize U_f and U_tau if the incoming stimulus has a different
        dimensionality from what was initialised with.

        This covers the case where StimulusProcessor is configured with a
        non-default vector_dim. Weights are re-initialised with the same seed
        to keep behaviour deterministic.
        """
        current_n = self.U_f.shape[1]
        if n == current_n:
            return
        rng = np.random.default_rng(_INIT_SEED)
        H = self._config.hidden_dim
        # Re-roll all weights to keep seed-consistent initialisation
        self.W_f   = _xavier_uniform((H, H), rng)
        self.U_f   = _xavier_uniform((H, n), rng)
        self.b_f   = np.zeros(H, dtype=np.float64)
        self.W_tau = _xavier_uniform((H, H), rng)
        self.U_tau = _xavier_uniform((H, n), rng)
        self.b_tau = np.zeros(H, dtype=np.float64)
        self.W_proj = _xavier_uniform((3, H), rng)
        self.b_proj  = np.zeros(3, dtype=np.float64)
        logger.debug("EmotionCore: resized input weights from dim %d to %d", current_n, n)
