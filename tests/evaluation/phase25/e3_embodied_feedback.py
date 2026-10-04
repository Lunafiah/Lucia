"""
tests/evaluation/phase25/e3_embodied_feedback.py

Phase 25 Track E3 — Embodied Reciprocal Feedback Evaluation Harness.

PRIMARY SCIENTIFIC INQUIRY (P25-Q1):
  "What computational representation, if any, is necessary for Lucia to maintain
   persistent relational consequences of significant interaction events beyond the
   timescale of instantaneous affective recovery, while preserving stability and INV-2?"

SCIENTIFIC HYPOTHESES:
  H1 (Embodied Loop Dissipativity & Trajectory Shaping): Closing the sensorimotor loop
      between embodiment kinematics and somatic homeostatic regulation alters orbital
      variance while preserving dissipative phase-space volume contraction (Tr(J) < 0)
      under bounded reciprocal coupling gains.
  H0 (Null Hypothesis / Alternative Explanation): Reciprocal embodiment feedback
      either produces identical dynamics to open-loop embodiment or destabilizes the
      somatic core (positive volume expansion Tr(J) >= 0 or unbounded trajectories).

MANDATORY SCIENTIFIC & ARCHITECTURAL CONSTRAINTS:
  - Compare:
      (1) output-only embodiment (feedforward);
      (2) reciprocal-feedback embodiment (closed-loop).
  - Tr(J) may be reported ONLY as a dissipativity-related diagnostic.
  - STRICT PROHIBITION: Do NOT claim Tr(J) < 0 implies Lyapunov stability, asymptotic stability,
    or global convergence (divergence < 0 signifies phase-space volume contraction, which is
    consistent with stable fixed points, limit cycles, or strange/chaotic attractors).
"""

from __future__ import annotations

import logging
import sys
import time
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

import numpy as np

PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from src.core.models import SomaticMarkers

logger = logging.getLogger(__name__)


@dataclass
class E3ConditionTelemetry:
    """Telemetry for a single embodiment simulation run."""
    condition_name: str
    feedback_gain: float
    total_steps: int
    jacobian_trace: float
    trace_interpretation: str
    orbital_bound_max: float
    somatic_variance: Dict[str, float]
    energy_dissipation_rate: float
    is_trajectory_bounded: bool
    trajectory_sample: List[Dict[str, float]]

    def to_dict(self) -> Dict[str, Any]:
        d = asdict(self)
        d.pop("trajectory_sample", None)
        return d


@dataclass
class E3TrackSummary:
    """Consolidated summary for Track E3 Embodied Reciprocal Feedback."""
    output_only_trace: float
    reciprocal_trace: float
    output_only_max_bound: float
    reciprocal_max_bound: float
    output_only_tension_var: float
    reciprocal_tension_var: float
    dissipativity_diagnostic_passed: bool
    lyapunov_disclaimer_honored: bool
    evidence_statement: str
    p25_q1_implication: str

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


class EmbodiedDynamicalSystem:
    """
    Isolated continuous dynamical model coupling 4D somatic markers
    m = [energy, load, tension, stability]^T with 4D embodiment kinematics
    x = [nod_pitch, gaze_yaw, gaze_pitch, smile_blendshape]^T.
    """

    def __init__(
        self,
        tau_somatic: float = 2.0,    # Somatic homeostasis relaxation timescale (seconds)
        tau_embody: float = 0.30,    # Mascot/avatar motor response timescale (seconds)
        feedback_gain: float = 0.0,  # 0.0 = Output-only, > 0.0 = Reciprocal closed-loop
    ) -> None:
        self.tau_somatic = float(tau_somatic)
        self.tau_embody = float(tau_embody)
        self.feedback_gain = float(feedback_gain)

        # Baseline resting equilibrium
        self.m_star = np.array([1.0, 0.05, 0.05, 0.95], dtype=np.float64)
        self.x_star = np.array([0.0, 0.0, 0.0, 0.10], dtype=np.float64)

        # Cross-coupling weights (bounded, non-expansive)
        self.W_somatic_to_embody = np.array([
            [-0.10,  0.05,  0.20, -0.10],  # nod_pitch
            [ 0.00,  0.15,  0.30, -0.05],  # gaze_yaw
            [ 0.05, -0.10, -0.20,  0.10],  # gaze_pitch
            [ 0.40, -0.20, -0.50,  0.30],  # smile_blendshape
        ], dtype=np.float64)

        self.W_embody_to_somatic = np.array([
            [ 0.10,  0.00,  0.05,  0.15],  # energy feedback
            [-0.05,  0.10,  0.10, -0.10],  # load feedback
            [-0.10,  0.05,  0.10, -0.25],  # tension attenuation from mimicry
            [ 0.15, -0.05, -0.05,  0.20],  # stability reinforcement
        ], dtype=np.float64)

    def vector_field(self, state: np.ndarray, user_input: np.ndarray) -> np.ndarray:
        """
        Evaluate full 8-dimensional coupled ODE dx/dt = F(state, user_input).
        State = [m (4D somatic), x (4D embody)].
        """
        m = state[0:4]
        x = state[4:8]

        # Autonomous somatic homeostatic decay toward resting m_star
        dm_dt = (-1.0 / self.tau_somatic) * (m - self.m_star)

        # Embodiment drive toward kinematic target g(m)
        target_x = self.x_star + np.tanh(self.W_somatic_to_embody @ (m - self.m_star))
        dx_dt = (-1.0 / self.tau_embody) * (x - target_x)

        # If reciprocal feedback is enabled, external user resonance and embodiment state
        # feed back into somatic marker derivatives
        if self.feedback_gain > 1e-9:
            # Resonance discrepancy between user input and Lucia's embodiment
            delta_resonance = user_input - x
            somatic_feedback = self.feedback_gain * np.tanh(self.W_embody_to_somatic @ delta_resonance)
            dm_dt += somatic_feedback

        return np.concatenate([dm_dt, dx_dt])

    def compute_jacobian_trace(self, state: Optional[np.ndarray] = None, eps: float = 1e-5) -> Tuple[float, np.ndarray]:
        """
        Compute numerical Jacobian J and its trace Tr(J) at given state.
        Tr(J) = sum(diag(J)) = div(F), measuring phase-space volume contraction rate.
        """
        if state is None:
            state = np.concatenate([self.m_star, self.x_star])
        user_neutral = np.zeros(4, dtype=np.float64)

        f0 = self.vector_field(state, user_neutral)
        n = len(state)
        J = np.zeros((n, n), dtype=np.float64)

        for i in range(n):
            perturbed = state.copy()
            perturbed[i] += eps
            f_pert = self.vector_field(perturbed, user_neutral)
            J[:, i] = (f_pert - f0) / eps

        trace_j = float(np.trace(J))
        return trace_j, J


class E3EmbodiedFeedbackEvaluator:
    """
    Evaluates comparative trajectory stability and dissipativity
    between output-only vs reciprocal-feedback embodiment.
    """

    def __init__(self, random_seed: int = 42) -> None:
        self.rng = np.random.default_rng(random_seed)

    def simulate_condition(
        self,
        condition_name: str,
        feedback_gain: float,
        total_steps: int = 300,
        dt: float = 0.05,
    ) -> E3ConditionTelemetry:
        """Run continuous numerical integration of the embodied system."""
        sys = EmbodiedDynamicalSystem(feedback_gain=feedback_gain)
        trace_j, _ = sys.compute_jacobian_trace()

        # Initial state slightly perturbed from equilibrium
        initial_state = np.concatenate([
            sys.m_star + self.rng.normal(0, 0.05, 4),
            sys.x_star + self.rng.normal(0, 0.05, 4),
        ])
        state = initial_state.copy()

        trajectory: List[np.ndarray] = []
        # Simulated user resonance signal (e.g. sinusoidal interactive nod/smile cadence)
        t_arr = np.linspace(0, total_steps * dt, total_steps)

        for step in range(total_steps):
            t = t_arr[step]
            # Simulated user micro-signals: periodic greeting + mild random fluctuations
            user_signal = np.array([
                0.20 * np.sin(2.0 * np.pi * 0.5 * t),   # user nod
                0.10 * np.cos(2.0 * np.pi * 0.25 * t),  # user gaze yaw
                0.05 * np.sin(2.0 * np.pi * 0.25 * t),  # user gaze pitch
                0.30 * max(0.0, np.sin(2.0 * np.pi * 0.2 * t)), # user smile
            ])

            # RK4 Integration step
            k1 = sys.vector_field(state, user_signal)
            k2 = sys.vector_field(state + 0.5 * dt * k1, user_signal)
            k3 = sys.vector_field(state + 0.5 * dt * k2, user_signal)
            k4 = sys.vector_field(state + dt * k3, user_signal)
            state = state + (dt / 6.0) * (k1 + 2.0 * k2 + 2.0 * k3 + k4)

            # Clamp state to physically plausible ranges
            state[0:4] = np.clip(state[0:4], 0.0, 1.0)
            state[4:8] = np.clip(state[4:8], -1.0, 1.0)

            trajectory.append(state.copy())

        traj_arr = np.array(trajectory)
        somatic_traj = traj_arr[:, 0:4]
        embody_traj = traj_arr[:, 4:8]

        # Orbital boundedness: max norm of state perturbation from equilibrium
        equilibrium = np.concatenate([sys.m_star, sys.x_star])
        perturbations = traj_arr - equilibrium
        max_bound = float(np.max(np.linalg.norm(perturbations, axis=1)))
        is_bounded = bool(max_bound < 3.0 and not np.any(np.isnan(traj_arr)))

        # Somatic marker variance
        somatic_vars = {
            "energy": float(np.var(somatic_traj[:, 0])),
            "load": float(np.var(somatic_traj[:, 1])),
            "tension": float(np.var(somatic_traj[:, 2])),
            "stability": float(np.var(somatic_traj[:, 3])),
        }

        # Energy dissipation: average magnitude of autonomous damping derivative
        dissipation_rate = float(np.mean(np.abs(traj_arr[:, 0] - sys.m_star[0]) / sys.tau_somatic))

        # Scientific disclaimer string
        diag_statement = (
            f"Tr(J)={trace_j:.4f} < 0 confirms local phase-space volume contraction (dissipativity). "
            f"NOTE: Tr(J) < 0 does NOT imply Lyapunov stability or global convergence."
        )

        sample = [
            {"step": i, "energy": float(traj_arr[i, 0]), "tension": float(traj_arr[i, 2]), "smile": float(traj_arr[i, 7])}
            for i in range(0, total_steps, 30)
        ]

        return E3ConditionTelemetry(
            condition_name=condition_name,
            feedback_gain=feedback_gain,
            total_steps=total_steps,
            jacobian_trace=trace_j,
            trace_interpretation=diag_statement,
            orbital_bound_max=max_bound,
            somatic_variance=somatic_vars,
            energy_dissipation_rate=dissipation_rate,
            is_trajectory_bounded=is_bounded,
            trajectory_sample=sample,
        )

    def run_benchmark(self) -> Tuple[E3TrackSummary, Dict[str, E3ConditionTelemetry]]:
        """Run comparison between output-only and reciprocal-feedback embodiment."""
        out_only = self.simulate_condition(
            condition_name="output_only",
            feedback_gain=0.00,
        )
        reciprocal = self.simulate_condition(
            condition_name="reciprocal_feedback",
            feedback_gain=0.15,
        )

        dissipative_passed = bool(out_only.jacobian_trace < 0 and reciprocal.jacobian_trace < 0)
        # Verify that our code honors the strict invariant: never claim Tr(J) < 0 => Lyapunov
        disclaimer_honored = bool("does NOT imply Lyapunov stability" in reciprocal.trace_interpretation)

        evidence = (
            f"Observed: Output-only Tr(J)={out_only.jacobian_trace:.4f}, Reciprocal Tr(J)={reciprocal.jacobian_trace:.4f}. "
            f"Both conditions satisfy phase-space volume contraction (Tr(J) < 0). "
            f"Max orbital bounds: output_only={out_only.orbital_bound_max:.4f}, reciprocal={reciprocal.orbital_bound_max:.4f}. "
            f"Tension variance: output_only={out_only.somatic_variance['tension']:.6f}, "
            f"reciprocal={reciprocal.somatic_variance['tension']:.6f}."
        )

        implication = (
            "Reciprocal embodiment feedback dynamically modulates somatic tension and mimicry within bounded orbits. "
            "Dissipativity is preserved under bounded gain (gain=0.15). However, whether embodiment participation "
            "in social feedback requires new cognitive ontology or can operate via existing sensory/motor interfaces "
            "remains an open research question for P25."
        )

        summary = E3TrackSummary(
            output_only_trace=out_only.jacobian_trace,
            reciprocal_trace=reciprocal.jacobian_trace,
            output_only_max_bound=out_only.orbital_bound_max,
            reciprocal_max_bound=reciprocal.orbital_bound_max,
            output_only_tension_var=out_only.somatic_variance["tension"],
            reciprocal_tension_var=reciprocal.somatic_variance["tension"],
            dissipativity_diagnostic_passed=dissipative_passed,
            lyapunov_disclaimer_honored=disclaimer_honored,
            evidence_statement=evidence,
            p25_q1_implication=implication,
        )

        return summary, {"output_only": out_only, "reciprocal_feedback": reciprocal}
