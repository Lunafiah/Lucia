"""
Standardized Stimulus Sequences and Evaluation Scenarios for Phase 19.

Defines reproducible multi-timescale experimental sequences:
    - Decay & Relaxation Probes (EXP-19.1)
    - Multi-Origin Attractor Probes (EXP-19.2)
    - Stress-to-Fatigue Transformation (EXP-19.3)
    - Historical Hysteresis Pair (EXP-19.4)
    - Longitudinal 100-Turn Lifecycle (EXP-19.8)
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import List, Optional, Tuple

import numpy as np


@dataclass
class StimulusStep:
    name: str
    vector: np.ndarray
    idle_after_seconds: float = 0.0
    homeo_override: Optional[Tuple[float, float, float, float]] = None  # (energy, load, tension, stability)


@dataclass
class ScenarioTrajectory:
    scenario_id: str
    description: str
    steps: List[StimulusStep]


def make_vector(valence: float, arousal: float, density: float, dim: int = 16) -> np.ndarray:
    """Create a standardized 16D stimulus vector with specified valence, arousal, and density."""
    vec = np.zeros(dim, dtype=np.float64)
    vec[0] = np.clip(valence, -1.0, 1.0)
    vec[1] = np.clip(arousal, 0.0, 1.0)
    vec[2] = np.clip(density, 0.0, 1.0)
    # Pad remaining dimensions with rhythmic and harmonic harmonics
    for i in range(3, dim):
        phase = (i - 2) * 0.5
        vec[i] = 0.2 * np.sin(valence * 3.1415 + phase) + 0.1 * np.cos(arousal * 3.1415)
    return vec


def make_decay_trajectory(perturb_turns: int = 5, idle_seconds: float = 300.0) -> ScenarioTrajectory:
    """EXP-19.1: Intense perturbation followed by long unforced idle relaxation."""
    stim = make_vector(valence=+0.85, arousal=+0.80, density=+0.60)
    steps = []
    for i in range(perturb_turns - 1):
        steps.append(StimulusStep(f"prime_{i}", stim, idle_after_seconds=0.0))
    # Final stimulus step followed by idle relaxation
    steps.append(StimulusStep("release_prime", stim, idle_after_seconds=idle_seconds))
    return ScenarioTrajectory("EXP_19_1_Decay", "Perturbation followed by 300s unforced relaxation", steps)


def make_stress_transformation_trajectory() -> ScenarioTrajectory:
    """EXP-19.3: Acute stress followed by unforced idle to test stress -> fatigue transformation."""
    stress_stim = make_vector(valence=-0.90, arousal=+0.90, density=+0.80)
    steps = []
    # 8 consecutive acute stress turns with accumulating load
    for i in range(8):
        load = min(1.0, 0.15 * (i + 1))
        energy = max(0.2, 1.0 - 0.08 * (i + 1))
        tension = min(1.0, 0.3 + 0.1 * (i + 1))
        steps.append(
            StimulusStep(
                f"stress_turn_{i+1}",
                stress_stim,
                idle_after_seconds=0.0,
                homeo_override=(energy, load, tension, 0.4),
            )
        )
    # Immediate post-stress release into 90s idle: threat stimulus ceases (x=0), acute tension drops to 0, energy is depleted, load is elevated
    steps.append(
        StimulusStep(
            "stress_release",
            np.zeros(16),
            idle_after_seconds=90.0,
            homeo_override=(0.35, 0.60, 0.0, 0.6),
        )
    )
    return ScenarioTrajectory("EXP_19_3_StressTransformation", "Acute stress transforming into fatigue over idle", steps)


def make_hysteresis_pair() -> Tuple[ScenarioTrajectory, ScenarioTrajectory]:
    """EXP-19.4: Two divergent historical regimes ending with the identical ambiguous probe."""
    probe = make_vector(valence=-0.25, arousal=+0.40, density=+0.50)

    # Regime A: Warm collaboration (15 turns) -> pause -> probe
    steps_a = []
    pos_stim = make_vector(valence=+0.70, arousal=+0.30, density=+0.40)
    for i in range(15):
        steps_a.append(StimulusStep(f"warm_{i}", pos_stim, idle_after_seconds=1.0))
    steps_a.append(StimulusStep("pause_a", np.zeros(16), idle_after_seconds=20.0))
    steps_a.append(StimulusStep("probe_a", probe, idle_after_seconds=5.0))

    # Regime B: Conflict (12 turns) -> peace pause (25s) -> probe
    steps_b = []
    neg_stim = make_vector(valence=-0.75, arousal=+0.75, density=+0.70)
    for i in range(12):
        steps_b.append(StimulusStep(f"conflict_{i}", neg_stim, idle_after_seconds=1.0))
    steps_b.append(StimulusStep("pause_b", np.zeros(16), idle_after_seconds=25.0))
    steps_b.append(StimulusStep("probe_b", probe, idle_after_seconds=5.0))

    traj_a = ScenarioTrajectory("EXP_19_4_RegimeA", "Warm collaborative history followed by probe", steps_a)
    traj_b = ScenarioTrajectory("EXP_19_4_RegimeB", "Conflict history followed by recovery and probe", steps_b)
    return traj_a, traj_b


def make_longitudinal_100_lifecycle() -> ScenarioTrajectory:
    """EXP-19.8: 100-turn multi-epoch lifecycle trajectory."""
    steps = []
    # Epoch 1: 20 neutral calibration turns
    neutral_stim = make_vector(valence=+0.05, arousal=+0.10, density=+0.20)
    for i in range(20):
        steps.append(StimulusStep(f"neutral_{i}", neutral_stim, idle_after_seconds=1.0))

    # Epoch 2: 25 positive collaborative turns
    pos_stim = make_vector(valence=+0.65, arousal=+0.35, density=+0.45)
    for i in range(25):
        steps.append(StimulusStep(f"positive_{i}", pos_stim, idle_after_seconds=1.0))

    # Epoch 3: 15 stress/friction turns
    stress_stim = make_vector(valence=-0.80, arousal=+0.80, density=+0.75)
    for i in range(15):
        steps.append(StimulusStep(f"stress_{i}", stress_stim, idle_after_seconds=0.5))

    # Epoch 4: 20 recovery turns
    relief_stim = make_vector(valence=+0.40, arousal=-0.10, density=+0.30)
    for i in range(20):
        steps.append(StimulusStep(f"recovery_{i}", relief_stim, idle_after_seconds=2.0))

    # Epoch 5: 20 steady baseline turns with occasional pauses
    for i in range(20):
        pause = 5.0 if i % 5 == 0 else 1.0
        steps.append(StimulusStep(f"steady_{i}", neutral_stim, idle_after_seconds=pause))

    return ScenarioTrajectory("EXP_19_8_Longitudinal100", "100-turn mixed longitudinal lifecycle", steps)
