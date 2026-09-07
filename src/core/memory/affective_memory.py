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

    def store(self, content_vector: np.ndarray, pad_state: PADState) -> int:
        """
        Store a content vector paired with a PAD emotional state snapshot.

        Parameters
        ----------
        content_vector : np.ndarray
            Content vector of shape (M,), float.
        pad_state : PADState
            Emotional state snapshot at the moment of encoding.

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
