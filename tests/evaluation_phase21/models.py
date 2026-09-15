"""
tests/evaluation_phase21/models.py

Data models and state containers for Phase 21 Experimental Validation Cycle.
Enforces structural boundary discipline: strictly zero self-model / introspective fields.
"""

from __future__ import annotations

import time
from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Dict, List, Optional

import numpy as np


class CounterfactualType(Enum):
    """Experimental condition classification for counterfactual evaluations."""
    AUTHENTIC = "authentic"
    SHUFFLED = "shuffled"
    RANDOM = "random"
    ORTHOGONAL = "orthogonal"


@dataclass
class HomeostaticState:
    """
    4-dimensional homeostatic state vector m in [0, 1]^4.
    Dimensions:
      - energy: Available conversational / metabolic stamina [0, 1]
      - cognitive_load: Operational burden across rolling window [0, 1]
      - tension: Acute mismatch / threat discrepancy [0, 1]
      - stability: Resistance to limbic turbulence [0, 1]
    """
    energy: float = 1.0
    cognitive_load: float = 0.0
    tension: float = 0.0
    stability: float = 1.0
    timestamp: float = field(default_factory=time.monotonic)

    def to_array(self) -> np.ndarray:
        return np.array(
            [self.energy, self.cognitive_load, self.tension, self.stability],
            dtype=np.float64,
        )

    @classmethod
    def from_array(cls, arr: np.ndarray, timestamp: Optional[float] = None) -> "HomeostaticState":
        clamped = np.clip(arr, 0.0, 1.0)
        return cls(
            energy=float(clamped[0]),
            cognitive_load=float(clamped[1]),
            tension=float(clamped[2]),
            stability=float(clamped[3]),
            timestamp=time.monotonic() if timestamp is None else float(timestamp),
        )


@dataclass
class ConsolidationExperience:
    """
    Interaction tuple captured for offline consolidation replay.
    Mathematical contents: (x, h_before, h_after, R, r_slow, salience, sequence_id)
    Strict invariant: Pure dynamical tensors; zero introspective self-model fields.
    """
    stimulus: np.ndarray          # x in R^16
    h_before: np.ndarray          # h_fast before turn in R^32
    h_after: np.ndarray           # h_fast after turn in R^32
    s_slow: np.ndarray            # s_slow after turn in R^16
    relational_state: np.ndarray  # R in [0, 1]^4
    r_slow_recollection: np.ndarray  # r_slow in R^16
    salience: float
    sequence_id: int
    timestamp: float = field(default_factory=time.monotonic)


@dataclass
class SynapticParameterState:
    """
    Snapshot of trainable continuous parameter matrices Theta.
    Enforces spectral norm computation on W_rel.
    """
    W_f: np.ndarray        # (32, 32)
    U_f: np.ndarray        # (32, 16)
    b_f: np.ndarray        # (32,)
    W_tau: np.ndarray      # (32, 32)
    U_tau: np.ndarray      # (32, 16)
    b_tau: np.ndarray      # (32,)
    W_rel: np.ndarray      # (16, 4)

    @property
    def w_rel_spectral_norm(self) -> float:
        """Operator / spectral norm sigma_max(W_rel)."""
        s = np.linalg.svd(self.W_rel, compute_uv=False)
        return float(s[0]) if len(s) > 0 else 0.0

    def copy(self) -> "SynapticParameterState":
        return SynapticParameterState(
            W_f=self.W_f.copy(),
            U_f=self.U_f.copy(),
            b_f=self.b_f.copy(),
            W_tau=self.W_tau.copy(),
            U_tau=self.U_tau.copy(),
            b_tau=self.b_tau.copy(),
            W_rel=self.W_rel.copy(),
        )

    def flatten_weights(self) -> np.ndarray:
        """Flatten all trainable parameters into a single 1D vector for cosine similarity."""
        return np.concatenate([
            self.W_f.ravel(),
            self.U_f.ravel(),
            self.b_f.ravel(),
            self.W_tau.ravel(),
            self.U_tau.ravel(),
            self.b_tau.ravel(),
            self.W_rel.ravel(),
        ])


@dataclass
class HomeostaticTrajectory:
    """Time-series recording of homeostatic settling."""
    timestamps: List[float] = field(default_factory=list)
    energies: List[float] = field(default_factory=list)
    tensions: List[float] = field(default_factory=list)
    cognitive_loads: List[float] = field(default_factory=list)
    stabilities: List[float] = field(default_factory=list)


@dataclass
class SimulationResult:
    """Output summary of an evaluation simulation run."""
    condition: CounterfactualType
    initial_pad: np.ndarray
    final_pad: np.ndarray
    final_slow: np.ndarray
    pad_trajectory: np.ndarray       # (T, 3)
    slow_trajectory: np.ndarray      # (T, 16)
    homeostatic_history: HomeostaticTrajectory
    delta_theta: Optional[np.ndarray] = None
    step_latencies_ms: List[float] = field(default_factory=list)
    train_latencies_ms: List[float] = field(default_factory=list)
    lock_wait_latencies_ms: List[float] = field(default_factory=list)
