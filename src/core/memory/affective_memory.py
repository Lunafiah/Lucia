"""
AffectiveMemory — trace encoding, storage, and retrieval with PAD tags.

Wraps SDMCore to co-encode each stored trace with a PAD affective tag
representing emotional context at the moment of encoding.

Requirements: 5.1–5.8, 6.1–6.5, 15.4, 15.5
"""

from __future__ import annotations

import sys
import threading
import time
from dataclasses import dataclass, field
from typing import Dict, List

import numpy as np

from src.core.memory.sdm import SDMConfig, SDMCore
from src.core.models import PADState


@dataclass
class MemoryTrace:
    """
    Mutable memory trace: decay_weight is updated in-place by Decay_Engine.
    """

    trace_id: int
    address_vec: np.ndarray  # uint8, shape (D,)
    content_vec: np.ndarray  # float32, shape (M,)
    pad_tag: PADState  # frozen copy of PADState at encoding moment
    timestamp: float  # time.monotonic() at store() call
    decay_weight: float  # initialized to 1.0; mutated by Decay_Engine
    slow_latent_trace: Optional[np.ndarray] = None


@dataclass
class AffectiveMemoryConfig:
    """
    Configuration for AffectiveMemory.

    Parameters
    ----------
    sdm_config : SDMConfig
        Underlying SDM configuration.
    m : int
        Content vector dimensionality (must match sdm_config.content_dim).
    """

    sdm_config: SDMConfig = field(default_factory=SDMConfig)
    m: int = 64

    def __post_init__(self) -> None:
        if self.m != self.sdm_config.content_dim:
            raise ValueError(
                f"AffectiveMemoryConfig.m ({self.m}) must match "
                f"sdm_config.content_dim ({self.sdm_config.content_dim})"
            )


class AffectiveMemory:
    """
    Affective memory store that pairs semantic content with PAD emotional context.
    """

    def __init__(self, config: AffectiveMemoryConfig) -> None:
        if not isinstance(config, AffectiveMemoryConfig):
            raise ValueError("config must be an AffectiveMemoryConfig instance")
        config.__post_init__()
        self._config = config
        self._sdm = SDMCore(config.sdm_config)
        self._M = config.m
        self._index: Dict[int, MemoryTrace] = {}
        self._index_lock = threading.RLock()

    @staticmethod
    def synthesize_legacy_latent(
        pad_tag: PADState | np.ndarray | tuple | list,
        philia_baseline: tuple = (0.25, -0.05, 0.05),
        philia_slow_baseline: tuple = (0.20, -0.05, 0.05),
        slow_dim: int = 16,
    ) -> np.ndarray:
        """
        Deterministic compatibility approximation: maps a 3D PAD tag -> 16D slow latent field.

        Strict 3-Case Semantic Acceptance Contract:
        1. Case 1 — Canonical Resting Baseline Input:
           When p_tag == p*_philia (within atol=1e-6), returns s*_philia bit-exact (zero drift).
        2. Case 2 — Non-Baseline Valid Input:
           When p_tag != p*_philia, returns clip(W_pad->slow @ (p_tag - p*_philia) + s*_philia, -0.85, 0.85).
           Deterministic (Delta < 10^-12) and bounded (||s||_inf <= 0.85).
        3. Case 3 — Non-Finite / Invalid Input (NaN / Inf):
           Returns s*_philia defensively if any component is non-finite.
        """
        s_star = np.zeros(slow_dim, dtype=np.float64)
        for i, val in enumerate(philia_slow_baseline):
            if i < slow_dim:
                s_star[i] = float(val)

        if isinstance(pad_tag, PADState):
            p = np.array(
                [pad_tag.pleasure, pad_tag.arousal, pad_tag.dominance],
                dtype=np.float64,
            )
        else:
            p = np.array(pad_tag, dtype=np.float64)[:3]

        # Case 3: Defensive fallback on NaN / Inf
        if not np.all(np.isfinite(p)):
            return s_star.copy()

        p_star = np.array(philia_baseline, dtype=np.float64)

        # Case 1: Canonical Resting Baseline Input -> bit-exact s*_philia
        if np.allclose(p, p_star, atol=1e-6):
            return s_star.copy()

        # Case 2: Non-Baseline Valid Input -> bounded deterministic approximation
        w_pad_to_slow = np.zeros((slow_dim, 3), dtype=np.float64)
        w_pad_to_slow[0, 0] = 0.60
        w_pad_to_slow[1, 1] = 0.60
        w_pad_to_slow[2, 2] = 0.50

        delta_p = p - p_star
        s_approx = (w_pad_to_slow @ delta_p) + s_star
        return np.clip(s_approx, -0.85, 0.85)

    def store(
        self,
        content_vector: np.ndarray,
        pad_state: PADState,
        slow_latent_trace: Optional[np.ndarray] = None,
    ) -> int:
        """
        Store a content vector paired with a PAD emotional state snapshot and slow latent trace.

        Parameters
        ----------
        content_vector : np.ndarray
            Content vector of shape (M,), float.
        pad_state : PADState
            Emotional state snapshot at the moment of encoding.
        slow_latent_trace : Optional[np.ndarray]
            Phase 20: 16D slow latent state snapshot s_slow(t). If None, synthesizes
            legacy fallback via synthesize_legacy_latent(pad_state).

        Returns
        -------
        int
            Assigned trace ID.
        """
        if content_vector.shape != (self._M,):
            raise ValueError(
                f"content_vector dim {content_vector.shape[0]} != expected {self._M}"
            )

        for dim, val in [
            ("pleasure", pad_state.pleasure),
            ("arousal", pad_state.arousal),
            ("dominance", pad_state.dominance),
        ]:
            if not (-1.0 <= val <= 1.0):
                raise ValueError(
                    f"PAD dimension '{dim}'={val} outside [-1.0, 1.0]"
                )

        if slow_latent_trace is None:
            latent_vec = self.synthesize_legacy_latent(pad_state)
        else:
            latent_arr = np.array(slow_latent_trace, dtype=np.float64)
            if not np.all(np.isfinite(latent_arr)):
                latent_vec = self.synthesize_legacy_latent(pad_state)
            else:
                if len(latent_arr) != 16:
                    padded = np.zeros(16, dtype=np.float64)
                    n = min(16, len(latent_arr))
                    padded[:n] = latent_arr[:n]
                    latent_vec = np.clip(padded, -1.0, 1.0)
                else:
                    latent_vec = np.clip(latent_arr, -1.0, 1.0)

        with self._index_lock:
            # Evict lowest decay_weight trace if at capacity
            if self._sdm.trace_count >= self._sdm.capacity:
                victim_id = min(
                    self._index, key=lambda tid: self._index[tid].decay_weight
                )
                self.delete_trace(victim_id)

            # Derive binary address by thresholding content vector at zero
            raw_addr = (content_vector >= 0.0).astype(np.uint8)
            if raw_addr.shape[0] == self._sdm._D:
                address = raw_addr
            elif raw_addr.shape[0] < self._sdm._D:
                address = np.zeros(self._sdm._D, dtype=np.uint8)
                address[: raw_addr.shape[0]] = raw_addr
            else:
                address = raw_addr[: self._sdm._D]

            trace_id = self._sdm.write(address, content_vector.astype(np.float32))
            trace = MemoryTrace(
                trace_id=trace_id,
                address_vec=address.copy(),
                content_vec=content_vector.astype(np.float32).copy(),
                pad_tag=pad_state,
                timestamp=time.monotonic(),
                decay_weight=1.0,
                slow_latent_trace=latent_vec,
            )
            self._index[trace_id] = trace
            return trace_id

    def get_all_traces(self) -> List[MemoryTrace]:
        """
        Return a thread-safe snapshot list of all stored traces.
        """
        with self._index_lock:
            return list(self._index.values())

    def get_trace(self, trace_id: int) -> MemoryTrace:
        """
        Retrieve a single trace by trace_id.
        """
        with self._index_lock:
            if trace_id not in self._index:
                raise KeyError(
                    f"trace_id {trace_id} not found in AffectiveMemory store"
                )
            return self._index[trace_id]

    def delete_trace(self, trace_id: int) -> None:
        """
        Delete a trace by ID from both the SDM store and memory index.
        Caller MUST hold _index_lock (or re-enter via RLock).
        """
        with self._index_lock:
            self._sdm.delete(trace_id)
            self._index.pop(trace_id, None)

    def clear(self) -> None:
        """
        Clear all stored memory traces and reset the underlying SDM store.
        """
        with self._index_lock:
            self._sdm.clear()
            self._index.clear()

    def index_memory_usage_bytes(self) -> int:

        """
        Return the approximate memory usage in bytes of the index dict.
        """
        with self._index_lock:
            return sum(sys.getsizeof(t) for t in self._index.values())

    @property
    def trace_count(self) -> int:
        """
        Return the number of active memory traces.
        """
        with self._index_lock:
            return len(self._index)
