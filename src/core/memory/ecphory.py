"""
EcphoryEngine — resonance scoring and echo vector assembly.

Scores stored Memory_Traces by PAD-space cosine resonance with the current
emotional state, then assembles a weighted Echo_Vector from the top-K resonant traces.

Requirements: 9.1–9.9, 10.1–10.7, 16.2, 16.4
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import List, Optional

import numpy as np

from src.core.memory.affective_memory import MemoryTrace
from src.core.models import PADState


@dataclass
class EcphoryConfig:
    """
    Configuration for EcphoryEngine.

    Parameters
    ----------
    resonance_threshold : float
        Minimum cosine similarity in PAD space for a trace to resonate [0.0, 1.0].
    ecphory_k : int
        Maximum number of top resonant traces combined into the Echo_Vector [1, 50].
    viability_threshold : float
        Decay weight threshold below which traces are ignored (matches DecayConfig).
    """

    resonance_threshold: float = 0.6
    ecphory_k: int = 5
    viability_threshold: float = 0.05

    def __post_init__(self) -> None:
        if not (0.0 <= self.resonance_threshold <= 1.0):
            raise ValueError(
                f"resonance_threshold ({self.resonance_threshold}) must be in [0.0, 1.0]"
            )
        if not (1 <= self.ecphory_k <= 50):
            raise ValueError(
                f"ecphory_k ({self.ecphory_k}) must be in [1, 50]"
            )
        if not (0.0 < self.viability_threshold < 1.0):
            raise ValueError(
                f"viability_threshold ({self.viability_threshold}) must be in (0.0, 1.0)"
            )


class EcphoryEngine:
    """
    Computes affective memory resonance and synthesizes numeric Echo_Vectors.
    """

    def __init__(self, config: EcphoryConfig) -> None:
        if not isinstance(config, EcphoryConfig):
            raise ValueError("config must be an EcphoryConfig instance")
        config.__post_init__()
        self._config = config

    def _resonance_score(self, pad_state: PADState, pad_tag: PADState) -> float:
        """
        Compute cosine similarity between two 3D PAD states.
        Returns 0.0 if either vector has norm zero.
        """
        a = np.array(
            [pad_state.pleasure, pad_state.arousal, pad_state.dominance],
            dtype=np.float64,
        )
        b = np.array(
            [pad_tag.pleasure, pad_tag.arousal, pad_tag.dominance],
            dtype=np.float64,
        )
        norm_a = np.linalg.norm(a)
        norm_b = np.linalg.norm(b)
        if norm_a == 0.0 or norm_b == 0.0:
            return 0.0
        dot = np.dot(a, b)
        cosine = dot / (norm_a * norm_b)
        return float(np.clip(cosine, -1.0, 1.0))

    def query(
        self,
        pad_state: PADState,
        traces: List[MemoryTrace],
    ) -> Optional[np.ndarray]:
        """
        Query memory traces for affective resonance against active pad_state.

        Parameters
        ----------
        pad_state : PADState
            Active emotional state.
        traces : list of MemoryTrace
            Snapshot of memory traces.

        Returns
        -------
        np.ndarray | None
            Echo_Vector of shape (M,), float32 in [-1.0, 1.0], or None if no resonance.
        """
        for dim, val in [
            ("pleasure", pad_state.pleasure),
            ("arousal", pad_state.arousal),
            ("dominance", pad_state.dominance),
        ]:
            if not (-1.0 <= val <= 1.0):
                raise ValueError(
                    f"PAD dimension '{dim}'={val} outside [-1.0, 1.0]"
                )

        pad_vec = np.array(
            [pad_state.pleasure, pad_state.arousal, pad_state.dominance],
            dtype=np.float64,
        )
        if np.linalg.norm(pad_vec) == 0.0:
            return None

        scored: List[tuple[float, MemoryTrace]] = []
        for trace in traces:
            if trace.decay_weight <= self._config.viability_threshold:
                continue
            score = self._resonance_score(pad_state, trace.pad_tag)
            if score > self._config.resonance_threshold:
                scored.append((score, trace))

        if not scored:
            return None

        # Sort descending by resonance score
        scored.sort(key=lambda t: t[0], reverse=True)
        top_k = scored[: self._config.ecphory_k]

        weights = np.array(
            [score * trace.decay_weight for score, trace in top_k],
            dtype=np.float64,
        )
        content_matrix = np.stack(
            [trace.content_vec.astype(np.float64) for _, trace in top_k],
            axis=0,
        )

        weight_sum = weights.sum()
        if weight_sum == 0.0:
            return None

        echo = (content_matrix * weights[:, np.newaxis]).sum(axis=0) / weight_sum
        return np.clip(echo, -1.0, 1.0).astype(np.float32)
