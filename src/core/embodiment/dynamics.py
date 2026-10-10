"""
src/core/embodiment/dynamics.py

Multi-timescale temporal evolution, elapsed-time decay, and stability diagnostics.
Handles physical elapsed time (dt_idle):
  - Affective relaxation toward Philia resting attractor (P=+0.25, A=-0.05, D=+0.05).
  - Somatic energy replenishment during inactive periods.
  - Cognitive load and tension decay.
  - Relational absence decay toward neutral baseline R_0 = [0.0, 0.5, 0.0, 0.5]^T.

Stability Guardrail:
  Tr(J) < 0 is reported strictly as a supporting local dissipativity diagnostic
  (phase-space volume contraction via Liouville's theorem). It does NOT imply
  Lyapunov stability, asymptotic contraction, or global convergence.
"""

from __future__ import annotations

import logging
import math
from typing import Optional, Tuple

import numpy as np

from src.core.embodiment.contract import IdleDynamicsResult
from src.core.models import PADState

logger = logging.getLogger(__name__)

# Philia resting attractor coordinates
PHILIA_P: float = 0.25
PHILIA_A: float = -0.05
PHILIA_D: float = 0.05

# Decay rate constants (per second)
K_PAD_RELAXATION: float = 0.02       # Half-life ~35 seconds
K_ENERGY_RECOVERY_HR: float = 0.20   # Recovers ~20% energy per hour of rest
K_TENSION_DECAY: float = 0.05        # Half-life ~14 seconds


class TemporalDynamicsEngine:
    """
    Simulates multi-timescale physical decay and recovery across idle intervals.
    """

    def __init__(
        self,
        tau_pad: float = 40.0,
        tau_somatic: float = 20.0,
        tau_relational_hours: float = 200.0,
    ) -> None:
        self.tau_pad = max(1.0, float(tau_pad))
        self.tau_somatic = max(1.0, float(tau_somatic))
        self.tau_relational_hours = max(1.0, float(tau_relational_hours))

    def step_idle(
        self,
        dt_seconds: float,
        current_pad: PADState,
        current_energy: float = 1.0,
        current_tension: float = 0.0,
    ) -> IdleDynamicsResult:
        """
        Compute state relaxation and recovery over physical elapsed time dt.
        """
        dt = max(0.0, float(dt_seconds))
        dt_hours = dt / 3600.0

        # 1. PAD exponential relaxation toward Philia attractor
        # P_dot = - (P - P*) / tau_pad
        decay_factor_pad = 1.0 - math.exp(-dt / self.tau_pad)
        delta_p = -decay_factor_pad * (current_pad.pleasure - PHILIA_P)
        delta_a = -decay_factor_pad * (current_pad.arousal - PHILIA_A)
        delta_d = -decay_factor_pad * (current_pad.dominance - PHILIA_D)
        pad_delta = np.array([delta_p, delta_a, delta_d], dtype=np.float64)

        # 2. Somatic energy replenishment during downtime (asymptote to 1.0)
        # dE/dt = (1.0 - E) * (K_energy / 3600)
        recovery_rate = K_ENERGY_RECOVERY_HR * dt_hours
        energy_replenishment = max(0.0, (1.0 - current_energy) * min(1.0, recovery_rate))

        # 3. Somatic tension decay
        # Tension decays toward 0.0 with time constant tau_somatic
        decay_factor_tension = 1.0 - math.exp(-dt / self.tau_somatic)
        tension_decay = max(0.0, current_tension * decay_factor_tension)

        # 4. Relational absence hours for high-inertia updater
        relational_absence_hours = dt_hours

        # 5. Dissipativity diagnostic Tr(J)
        tr_j = self.compute_dissipativity_diagnostic()

        return IdleDynamicsResult(
            dt_seconds=dt,
            pad_delta=pad_delta,
            energy_replenishment=energy_replenishment,
            tension_decay=tension_decay,
            relational_absence_hours=relational_absence_hours,
            dissipativity_diagnostic=tr_j,
        )

    def compute_dissipativity_diagnostic(self) -> float:
        """
        Compute local Jacobian trace Tr(J) strictly as a dissipativity diagnostic.

        Mathematical note:
          For uncoupled diagonal relaxation:
            J = diag(-1/tau_pad, -1/tau_pad, -1/tau_pad, -1/tau_somatic, ...)
          Tr(J) = -3/tau_pad - 1/tau_somatic < 0
          This confirms local phase-space volume contraction.

        SCIENTIFIC GUARDRAIL:
          Tr(J) < 0 does NOT alone guarantee Lyapunov stability, contraction,
          or global convergence. It is reported solely as a dissipativity diagnostic.
        """
        tr_pad = -3.0 / self.tau_pad
        tr_somatic = -1.0 / self.tau_somatic
        return tr_pad + tr_somatic
