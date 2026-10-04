"""
tests/evaluation/phase25/models.py

Evaluation-Only Data Models and Scientific Instrumentation for Phase 25.

IMPORTANT RESEARCH GOVERNANCE NOTICE:
These data classes, metrics, and simulators exist SOLELY for evaluation and benchmark
characterization. They are NOT part of Lucia's production ontology or runtime state.
Do NOT import these into src/core/** or src/api/**.
"""

from __future__ import annotations

import time
from dataclasses import asdict, dataclass, field
from typing import Any, Dict, List, Optional, Tuple

import numpy as np


@dataclass(frozen=True)
class EvaluationPADSnapshot:
    """Evaluation snapshot of 3D PAD vector."""
    pleasure: float
    arousal: float
    dominance: float

    def to_array(self) -> np.ndarray:
        return np.array([self.pleasure, self.arousal, self.dominance], dtype=np.float64)


@dataclass(frozen=True)
class EvaluationRelSnapshot:
    """Evaluation snapshot of 4D canonical relationship vector R_t."""
    familiarity: float
    trust: float
    closeness: float
    reciprocity: float

    def to_array(self) -> np.ndarray:
        return np.array(
            [self.familiarity, self.trust, self.closeness, self.reciprocity],
            dtype=np.float64,
        )


@dataclass(frozen=True)
class EvaluationSomaticSnapshot:
    """Evaluation snapshot of 4D homeostatic somatic markers."""
    energy: float
    cognitive_load: float
    tension: float
    stability: float

    def to_array(self) -> np.ndarray:
        return np.array(
            [self.energy, self.cognitive_load, self.tension, self.stability],
            dtype=np.float64,
        )


@dataclass
class TrajectoryRecord:
    """Evaluation record capturing a single step in a simulated interaction trajectory."""
    step: int
    pad: EvaluationPADSnapshot
    relationship: EvaluationRelSnapshot
    somatic: EvaluationSomaticSnapshot
    stimulus_label: str
    timestamp: float = field(default_factory=time.time)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "step": self.step,
            "pad": asdict(self.pad),
            "relationship": asdict(self.relationship),
            "somatic": asdict(self.somatic),
            "stimulus_label": self.stimulus_label,
            "timestamp": self.timestamp,
        }


# ============================================================================
# EVALUATION-ONLY METRICS (NOT PRODUCTION ONTOLOGY)
# ============================================================================

@dataclass(frozen=True)
class SocialPredictionError:
    """
    Evaluation Metric: Social Prediction Error (SPE).
    Measures Euclidean norm between actual relational outcome and counterfactual
    expected outcome under an unperturbed / default interaction trajectory.
    """
    relational_spe: float          # || R_actual - R_expected ||_2
    affective_spe: float           # || PAD_actual - PAD_expected ||_2
    composite_spe: float           # Weighted composite error

    @classmethod
    def compute(
        cls,
        actual_rel: np.ndarray,
        expected_rel: np.ndarray,
        actual_pad: np.ndarray,
        expected_pad: np.ndarray,
        rel_weight: float = 0.70,
        pad_weight: float = 0.30,
    ) -> "SocialPredictionError":
        rel_err = float(np.linalg.norm(actual_rel - expected_rel))
        pad_err = float(np.linalg.norm(actual_pad - expected_pad))
        comp = float(rel_weight * rel_err + pad_weight * pad_err)
        return cls(relational_spe=rel_err, affective_spe=pad_err, composite_spe=comp)


@dataclass(frozen=True)
class DirectnessMetric:
    """
    Evaluation Metric: Directness.
    Quantifies the cosine alignment between a corrective interaction signal vector
    and the breach deficit vector: delta_breach = R_baseline - R_ruptured.
    """
    alignment_score: float         # Cosine similarity in [-1.0, 1.0]
    magnitude_ratio: float         # Relative scale of repair step vs breach depth

    @classmethod
    def compute(
        cls,
        signal_delta: np.ndarray,
        breach_deficit: np.ndarray,
    ) -> "DirectnessMetric":
        norm_sig = float(np.linalg.norm(signal_delta))
        norm_def = float(np.linalg.norm(breach_deficit))
        if norm_sig < 1e-9 or norm_def < 1e-9:
            return cls(alignment_score=0.0, magnitude_ratio=0.0)
        cos_sim = float(np.dot(signal_delta, breach_deficit) / (norm_sig * norm_def))
        cos_sim = max(-1.0, min(1.0, cos_sim))
        mag_ratio = float(norm_sig / norm_def)
        return cls(alignment_score=cos_sim, magnitude_ratio=mag_ratio)


@dataclass(frozen=True)
class SupportivenessMetric:
    """
    Evaluation Metric: Supportiveness.
    Quantifies restorative yield on cooperative relational dimensions
    (trust and reciprocity) normalized by internal somatic tension.
    Supportiveness = (Delta_trust + Delta_reciprocity) / (1.0 + tension)
    """
    score: float
    raw_relational_yield: float
    tension_attenuation: float

    @classmethod
    def compute(
        cls,
        delta_trust: float,
        delta_reciprocity: float,
        somatic_tension: float,
    ) -> "SupportivenessMetric":
        yield_val = delta_trust + delta_reciprocity
        tension_clamped = max(0.0, float(somatic_tension))
        score_val = float(yield_val / (1.0 + tension_clamped))
        return cls(
            score=score_val,
            raw_relational_yield=yield_val,
            tension_attenuation=1.0 / (1.0 + tension_clamped),
        )


@dataclass(frozen=True)
class EntrainmentMetrics:
    """
    Evaluation Metrics for Track E4 Conversational Entrainment.
    Characterizes timing coordination, latency, jitter, stability, and CPU cost.
    """
    gamma: float                   # Coupling coefficient parameter
    coordination_plv: float        # Phase-Locking Value in [0.0, 1.0]
    rhythmic_correlation: float    # Pearson correlation of cadence intervals
    mean_lag_ms: float             # Mean turn-taking gap discrepancy
    jitter_std_ms: float           # Standard deviation of response timing
    bounded_stability_ratio: float # Fraction of turns within safe window [200ms, 3000ms]
    mean_cpu_time_us: float        # Wall-clock CPU time per adaptation tick (microseconds)

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


@dataclass
class ContentionFaultReport:
    """
    Evaluation Telemetry for Track E5 Peripheral Authority Contention.
    Characterizes failure modes under competing continuous cognitive authorities.
    """
    fault_mode: str
    channel_count: int
    total_steps: int
    divergent_trace_distance_mean: float
    divergent_trace_distance_max: float
    conflicting_write_count: int
    ordering_violation_count: int
    state_corruption_count: int
    split_brain_detected: bool
    observed_divergence: float

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)
