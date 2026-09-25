"""
Configuration and Preregistered Thresholds for Phase 22-REL:
Relational & Somatic Memory Consolidation Study.
"""
from typing import Dict, List

# Split Discipline
TRAIN_SEEDS = [42, 137, 618]
HELD_OUT_SEEDS = [1024, 2026]
ALL_SEEDS = TRAIN_SEEDS + HELD_OUT_SEEDS

STRESS_REGIMES = [
    "ID",
    "NoiseSurge",
    "LexicalSparsity",
    "ContradictionShock",
    "TemporalDrift",
    "CombinedStress",
]

LANGUAGES = ["English", "Vietnamese", "Japanese"]

# Target Vector Dimensions
OBSERVABLE_4D_DIMS = ["u0_load", "u1_valence", "u2_agency", "u3_urgency"]
RELATIONAL_MEMORY_DIMS = ["m0_fatigue", "m1_relational_warmth"]
LEGACY_6D_DIMS = OBSERVABLE_4D_DIMS + RELATIONAL_MEMORY_DIMS
P23_PSI_USER_12D_DIMS = [
    "u_load", "u_valence", "u_agency", "u_urgency", # 4D Observable state
    "u_dot_load", "u_dot_valence", "u_dot_agency", "u_dot_urgency", # 4D Derivatives
    "m_fatigue", "m_warmth", # 2D Consolidated Relational/Somatic Memory
    "pi_uncertainty", "r_resonance" # 2D Epistemic & Contextual Resonance
]

# Preregistered Acceptance Gates
GATE_REL_WARMTH_R2 = 0.5000       # G_REL1: Relational Warmth consolidation quality
GATE_FATIGUE_R2 = 0.5000          # G_REL2: Fatigue accumulation quality
GATE_SESSION_RETENTION = 0.8000   # G_REL3: Session-to-session memory retention (> 80% persistence)
GATE_RECOVERY_TURNS = 1.0000      # G_REL4: Rapid recovery under observable shock (<= 1 turn)
GATE_CPU_P50_MS = 2.0000          # G_REL5: CPU execution SLA (P50 <= 2.0 ms)
GATE_VRAM_MB = 0.0000             # G_REL6: VRAM footprint (0.0 MB strictly)

# Canonical Baselines from Phase 22-ONT
CANONICAL_BASELINES = {
    "O1_Legacy6D_Overall_R2": 0.8242,
    "O1_Legacy6D_Warmth_R2": 0.7704,
    "O2_Decoupled4D2D_Overall_R2": -0.1168,
    "O2_Decoupled4D2D_Warmth_R2": -1.8236,
    "O3_MultiTimescale_Overall_R2": 0.5119,
    "O3_MultiTimescale_Warmth_R2": -0.1948,
    "Observable_4D_EKF_R2": 0.6385,
    "Contradiction_Recovery_Turns": 1.0000,
    "Flapping_Rate_Pct": 1.2000,
    "Latency_CPU_P50_ms": 0.0785,
}
