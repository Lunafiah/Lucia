"""
Simulated Kanerva Sparse Distributed Memory (SDM) Store for Phase 22-MR.

Provides:
- A lightweight simulation of the Kanerva SDM address/value storage mechanism.
- Episodic anchor storage with metadata (type, session, turn, language, content).
- Address generation from anchor feature vectors.
- Hamming-ball neighbor search for retrieval.
- Ground-truth relevance labels for each stored memory (for oracle evaluation).

This is NOT a production SDM implementation. It is a controlled simulation
to benchmark retrieval candidates M0–M4 under measurable, reproducible conditions.

No production code is touched. No GPU is used. All computation is CPU-bound NumPy.
"""
from __future__ import annotations
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Tuple
import numpy as np


@dataclass
class MemoryTrace:
    """One episodic anchor stored in the simulated SDM."""
    trace_id:       int
    anchor_type:    str         # e.g. "milestone_bonding"
    session_idx:    int
    turn_idx:       int
    language:       str
    utterance:      str
    relevance:      float       # Oracle ground-truth relevance [0.0, 1.0]
    is_mandatory:   bool        # True for ruptures, repairs, milestones
    address:        np.ndarray  # Binary SDM address (SDM_ADDRESS_DIM bits)
    value_vec:      np.ndarray  # Float feature vector (SDM_VALUE_DIM dims)
    stress_regime:  str         = "ID"
    is_noisy:       bool        = False  # Synthetic noise trace (should NOT be retrieved)


class SimulatedSDM:
    """
    Lightweight Kanerva SDM simulation for Phase 22-MR benchmarking.

    Storage:
        - Each trace is stored at a binary address derived from its feature vector.
        - Hamming-ball retrieval returns all traces within hamming_r of the query address.

    Relevance Ground Truth:
        - Each stored trace carries an oracle relevance score assigned at write time.
        - Used by the Oracle retrieval candidate and for metric computation.
    """

    def __init__(self, address_dim: int, value_dim: int, capacity: int,
                 hamming_r: int, rng: np.random.RandomState):
        self.address_dim  = address_dim
        self.value_dim    = value_dim
        self.capacity     = capacity
        self.hamming_r    = hamming_r
        self._rng         = rng

        self.traces:        List[MemoryTrace] = []
        self._trace_counter: int = 0

    def reset(self) -> None:
        self.traces = []
        self._trace_counter = 0

    # ── Address generation ────────────────────────────────────────────────────

    def _feature_to_address(self, feature_vec: np.ndarray) -> np.ndarray:
        """
        Convert a continuous feature vector into a binary SDM address via
        random projection + threshold.  Deterministic per feature vector
        (project matrix is fixed per SDM instance so the same feature always
        maps to the same address).
        """
        if not hasattr(self, "_proj"):
            self._proj = self._rng.randn(self.address_dim, len(feature_vec))
        projected = self._proj @ feature_vec  # (address_dim,)
        return (projected > 0.0).astype(np.uint8)

    def _make_value_vec(self, feature_vec: np.ndarray,
                        anchor_type: str) -> np.ndarray:
        """Encode content into value vector (normalized feature + type one-hot stub)."""
        val = np.zeros(self.value_dim, dtype=np.float32)
        n = min(self.value_dim, len(feature_vec))
        val[:n] = feature_vec[:n]
        # Embed anchor type index as a single float in the last dimension
        from .config import ANCHOR_TYPES
        try:
            type_idx = ANCHOR_TYPES.index(anchor_type) / max(1, len(ANCHOR_TYPES) - 1)
        except ValueError:
            type_idx = 0.5
        val[-1] = float(type_idx)
        return val

    # ── Write ─────────────────────────────────────────────────────────────────

    def write(self, anchor_type: str, session_idx: int, turn_idx: int,
              language: str, utterance: str, feature_vec: np.ndarray,
              relevance: float, is_mandatory: bool,
              stress_regime: str = "ID",
              is_noisy: bool = False) -> MemoryTrace:
        """Store one episodic anchor. Evicts oldest trace if at capacity."""
        if len(self.traces) >= self.capacity:
            self.traces.pop(0)   # FIFO eviction — oldest anchor dropped

        address   = self._feature_to_address(feature_vec)
        value_vec = self._make_value_vec(feature_vec, anchor_type)
        trace     = MemoryTrace(
            trace_id      = self._trace_counter,
            anchor_type   = anchor_type,
            session_idx   = session_idx,
            turn_idx      = turn_idx,
            language      = language,
            utterance     = utterance,
            relevance     = relevance,
            is_mandatory  = is_mandatory,
            address       = address,
            value_vec     = value_vec,
            stress_regime = stress_regime,
            is_noisy      = is_noisy,
        )
        self.traces.append(trace)
        self._trace_counter += 1
        return trace

    # ── Query ─────────────────────────────────────────────────────────────────

    def hamming_neighbors(self, query_address: np.ndarray) -> List[Tuple[MemoryTrace, int]]:
        """
        Return all stored traces whose address is within hamming_r bits of the
        query address, together with their Hamming distance.
        """
        results: List[Tuple[MemoryTrace, int]] = []
        for trace in self.traces:
            dist = int(np.sum(query_address != trace.address))
            if dist <= self.hamming_r:
                results.append((trace, dist))
        # Sorted by distance (closest first)
        results.sort(key=lambda x: x[1])
        return results

    def cosine_similarity(self, query_vec: np.ndarray) -> List[Tuple[MemoryTrace, float]]:
        """
        Return all traces ranked by cosine similarity of value vectors to query.
        """
        q_norm = np.linalg.norm(query_vec)
        if q_norm < 1e-9:
            return []
        results: List[Tuple[MemoryTrace, float]] = []
        for trace in self.traces:
            t_norm = np.linalg.norm(trace.value_vec)
            if t_norm < 1e-9:
                sim = 0.0
            else:
                sim = float(np.dot(query_vec, trace.value_vec) / (q_norm * t_norm))
            results.append((trace, sim))
        results.sort(key=lambda x: -x[1])
        return results

    # ── Helpers ───────────────────────────────────────────────────────────────

    @property
    def n_traces(self) -> int:
        return len(self.traces)

    def mandatory_traces(self) -> List[MemoryTrace]:
        """Return all mandatory-class traces (ruptures, repairs, milestones)."""
        return [t for t in self.traces if t.is_mandatory and not t.is_noisy]

    def relevant_traces(self, threshold: float = 0.50) -> List[MemoryTrace]:
        """Ground-truth relevant traces above relevance threshold."""
        return [t for t in self.traces
                if t.relevance >= threshold and not t.is_noisy]

    def irrelevant_traces(self, threshold: float = 0.50) -> List[MemoryTrace]:
        """Ground-truth irrelevant traces (neutral_task or low-relevance noise)."""
        return [t for t in self.traces
                if t.relevance < threshold or t.is_noisy]

    def make_query_address(self, feature_vec: np.ndarray) -> np.ndarray:
        """Produce the binary SDM query address for a given feature vector."""
        return self._feature_to_address(feature_vec)

    def make_query_value(self, feature_vec: np.ndarray,
                         anchor_type: str = "neutral_task") -> np.ndarray:
        """Produce a value-space query vector."""
        return self._make_value_vec(feature_vec, anchor_type)
