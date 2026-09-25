"""
Configuration and Preregistered Thresholds for Phase 22-INF:
Information Sufficiency & Semantic State Formation Study.
"""
from typing import Dict, List, Tuple
import numpy as np

# Canonical Seeds
TRAIN_SEEDS = [42, 137, 618]
HELD_OUT_SEEDS = [1024, 2026]
ALL_SEEDS = TRAIN_SEEDS + HELD_OUT_SEEDS

# Stress Regimes
STRESS_REGIMES = [
    "ID",
    "NoiseSurge",
    "LexicalSparsity",
    "ContradictionShock",
    "TemporalDrift",
    "CombinedStress",
]

# Supported Languages
LANGUAGES = ["English", "Vietnamese", "Japanese"]

# Latent State Dimension and Coordinates
STATE_DIM = 6
DIM_NAMES = [
    "z0_cognitive_load",
    "z1_valence",
    "z2_agency",
    "z3_urgency",
    "z4_metabolic_fatigue",
    "z5_relational_warmth",
]

# Preregistered Gates & Thresholds
GATE_R2_TARGET = 0.85          # Required for production architecture realization design
GATE_R2_FALSIFICATION = 0.70   # Below this is considered falsified
GATE_DOWNSTREAM_FLAPPING = 0.05 # Flapping rate <= 5%
GATE_CONTRADICTION_RECOVERY = 2.0 # Recovery in <= 2 turns
GATE_TRAJECTORY_COVERAGE = 0.90 # Horizon H=1,2 coverage >= 90%
GATE_CPU_P50_MS = 1.0          # State formation latency <= 1.0 ms
GATE_VRAM_MB = 0.0             # 0 MB GPU VRAM utilized

# Canonical Baselines for Evidence Preservation
CANONICAL_BASELINES = {
    "REAL_LAYA_MODERNBERT_PARAMS": 421.4e6,
    "REAL_LAYA_CPU_P50_MS": 607.67,
    "REAL_LAYA_ECE": 0.2232,
    "PHASE_22_XR_FLAPPING": 0.0040,
    "PHASE_22_XR_RECOVERY_TURNS": 1.0,
    "PHASE_22_XR_CALIBRATED_COVERAGE": 1.0,
    "PHASE_22_AL_PEAK_HELD_OUT_R2": 0.25476,
    "PHASE_22_AL_ORACLE_R2": 0.90179,
}
