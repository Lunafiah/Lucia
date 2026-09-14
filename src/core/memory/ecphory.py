"""
EcphoryEngine — resonance scoring and echo vector assembly.

Scores stored Memory_Traces by PAD-space cosine resonance with the current
emotional state, then assembles a weighted Echo_Vector from the top-K resonant traces.

Requirements: 9.1–9.9, 10.1–10.7, 16.2, 16.4
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import List, Optional, Tuple

import numpy as np

from src.core.config import EmotionConfig
from src.core.memory.affective_memory import AffectiveMemory, MemoryTrace
from src.core.models import PADState


@dataclass
class RecollectionResult:
    """
    Diagnostic & signal packet emitted by EcphoryEngine at Stage 6.

    r_slow_bounded is strictly an instantaneous retrieval-cue signal snapshot synthesized
    at Stage 6 for exogenous ODE forcing and pacing modulation.
    It is NOT the live physiological state of EmotionCore.
    """

    salience: float = 0.0
    r_slow_raw: Optional[np.ndarray] = None
    r_slow_bounded: np.ndarray = field(
        default_factory=lambda: np.zeros(16, dtype=np.float64)
    )
    winning_trace_id: Optional[int] = None
    active: bool = False


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

    @staticmethod
    def _cosine_sim(v1: np.ndarray, v2: np.ndarray) -> float:
        """Compute cosine similarity between two 1D float vectors."""
        n1 = float(np.linalg.norm(v1))
        n2 = float(np.linalg.norm(v2))
        if n1 <= 1e-9 or n2 <= 1e-9:
            return 0.0
        dot = float(np.dot(v1, v2))
        return float(np.clip(dot / (n1 * n2), -1.0, 1.0))

    def query_recollection(
        self,
        pad_state: PADState,
        stimulus_vec: np.ndarray,
        traces: List[MemoryTrace],
        config: Optional[EmotionConfig] = None,
    ) -> Tuple[Optional[np.ndarray], RecollectionResult]:
        """
        Evaluate memory retrieval across store, apply competitive softmax gating,
        and construct bounded slow-field perturbation vector r_slow.

        Emits (echo_vector, RecollectionResult).
        """
        echo_vector = self.query(pad_state, traces)

        theta_gate = config.recollection_gate_threshold if config is not None else 0.50
        tau_comp = config.recollection_softmax_temp if config is not None else 0.20
        philia_base = config.resting_baseline if config is not None else (0.25, -0.05, 0.05)
        philia_slow_base = (
            config.philia_slow_baseline if config is not None else (0.20, -0.05, 0.05)
        )

        p_philia = np.array(philia_base, dtype=np.float64)
        s_philia = np.zeros(16, dtype=np.float64)
        for idx, val in enumerate(philia_slow_base[:16]):
            s_philia[idx] = float(val)

        if not traces:
            return echo_vector, RecollectionResult(salience=0.0, active=False)

        viable_traces = [
            t for t in traces if t.decay_weight > self._config.viability_threshold
        ]
        if not viable_traces:
            return echo_vector, RecollectionResult(salience=0.0, active=False)

        cur_p = np.array(
            [pad_state.pleasure, pad_state.arousal, pad_state.dominance],
            dtype=np.float64,
        )
        delta_cur = cur_p - p_philia

        scored: List[Tuple[MemoryTrace, float]] = []
        for trace in viable_traces:
            # 1. Semantic affinity
            content = trace.content_vec.astype(np.float64)
            v_stim = np.zeros(len(content), dtype=np.float64)
            k = min(len(stimulus_vec), len(content))
            v_stim[:k] = stimulus_vec[:k]
            s_sem = self._cosine_sim(v_stim, content)

            # 2. Affective ecphoric affinity
            enc_p = np.array(
                [
                    trace.pad_tag.pleasure,
                    trace.pad_tag.arousal,
                    trace.pad_tag.dominance,
                ],
                dtype=np.float64,
            )
            delta_enc = enc_p - p_philia
            s_aff = self._cosine_sim(delta_cur, delta_enc)

            # 3. Composite salience score
            composite = (
                0.60 * max(0.0, s_sem)
                + 0.25 * max(0.0, s_aff)
                + 0.15 * trace.decay_weight
            )
            scored.append((trace, composite))

        max_salience = max(s for _, s in scored)
        passing = [(t, s) for (t, s) in scored if s >= theta_gate]

        if not passing:
            return echo_vector, RecollectionResult(
                salience=float(max_salience), active=False
            )

        # Competitive Softmax Gating
        comps = np.array([s for (_, s) in passing], dtype=np.float64)
        max_c = np.max(comps)
        exp_c = np.exp((comps - max_c) / tau_comp)
        softmax_weights = exp_c / np.sum(exp_c)

        # Winning trace is highest scored
        best_trace = max(passing, key=lambda item: item[1])[0]

        # Construct r_slow via convex combination of centered traces
        r_slow = np.zeros(16, dtype=np.float64)
        for (trace, _), alpha in zip(passing, softmax_weights):
            if trace.slow_latent_trace is not None:
                s_enc = trace.slow_latent_trace
            else:
                s_enc = AffectiveMemory.synthesize_legacy_latent(
                    trace.pad_tag, philia_base, philia_slow_base, 16
                )
            delta_s = s_enc - s_philia
            r_slow += alpha * delta_s

        # Bounded saturation (strictly <= 0.85)
        r_slow_bounded = np.clip(np.tanh(r_slow) * 0.85, -0.85, 0.85)

        return echo_vector, RecollectionResult(
            salience=float(max_salience),
            r_slow_raw=r_slow,
            r_slow_bounded=r_slow_bounded,
            winning_trace_id=best_trace.trace_id,
            active=True,
        )
