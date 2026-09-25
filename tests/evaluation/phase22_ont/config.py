"""
Configuration and Preregistered Thresholds for Phase 22-ONT:
Target Ontology Redesign Study.
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

# Coordinate Definitions
# Observable 4D Interaction Space (Layer A)
OBSERVABLE_4D_DIMS = [
    "u0_cognitive_load",
    "u1_valence",
    "u2_agency",
    "u3_urgency",
]

# Relational / Somatic Memory Space (Layer B)
SLOW_MEMORY_DIMS = [
    "m0_metabolic_fatigue",
    "m1_relational_warmth",
]

LEGACY_6D_DIMS = [
    "z0_cognitive_load",
    "z1_valence",
    "z2_agency",
    "z3_urgency",
    "z4_metabolic_fatigue",
    "z5_relational_warmth",
]

# Preregistered Target Thresholds
GATE_OBSERVABLE_4D_R2 = 0.70      # Acceptance threshold for observable 4D interaction state
GATE_TARGET_RECOVERY_TURNS = 1.0   # Contradiction recovery <= 1.0 turn
GATE_FLAPPING_RATE = 0.05          # Flapping rate <= 5%
GATE_CPU_P50_MS = 1.0             # CPU Latency SLA <= 1.0 ms
GATE_VRAM_MB = 0.0                # 0 MB GPU VRAM

# Canonical Baseline Historical Records
CANONICAL_BASELINES = {
    "REAL_LAYA_MODERNBERT_PARAMS": 421.4e6,
    "REAL_LAYA_CPU_P50_MS": 607.67,
    "REAL_LAYA_ECE": 0.2232,
    "PHASE_22_XR_FLAPPING": 0.0040,
    "PHASE_22_XR_RECOVERY_TURNS": 1.0,
    "PHASE_22_XR_CALIBRATED_COVERAGE": 1.0,
    "PHASE_22_AL_PEAK_HELD_OUT_R2": 0.25476,
    "PHASE_22_INF_PEAK_HELD_OUT_R2": 0.69880,
    "PHASE_22_SSF_RAW_BASELINE_R2": 0.70034,
    "PHASE_22_EKF_R2": 0.70303,
}
