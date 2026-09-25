"""
Configuration and Preregistered Thresholds for Phase 22-ANCHOR:
Relational Memory Grounding & Episodic Anchor Study.
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
P23_PSI_USER_12D_DIMS = [
    "u_load", "u_valence", "u_agency", "u_urgency", # 4D Observable state
    "u_dot_load", "u_dot_valence", "u_dot_agency", "u_dot_urgency", # 4D Derivatives
    "m_fatigue", "m_warmth", # 2D Consolidated Relational/Somatic Memory
    "pi_uncertainty", "r_resonance" # 2D Epistemic & Contextual Resonance
]

# Preregistered Acceptance Gates for Phase 22-ANCHOR
GATE_RETRIEVAL_ACCURACY = 0.8000   # G_ANC1: Precision of retrieving relational stance from memory (>= 80%)
GATE_DRIFT_RESISTANCE = 0.0500     # G_ANC2: Drift over multi-session without new anchors (<= 0.05 drift / stability)
GATE_WARMTH_R2 = 0.5000            # G_ANC3: Relational Warmth ground truth tracking R^2 >= 0.50
GATE_FALSE_ANCHOR_RATE = 0.1000    # G_ANC4: False-positive anchor creation rate on neutral/sparse turns (<= 10%)
GATE_SESSION_RETENTION = 0.8500    # G_ANC5: Multi-session persistent memory retention (>= 85%)
GATE_CPU_P50_MS = 2.0000           # G_ANC6: CPU latency SLA (P50 <= 2.0 ms)
GATE_VRAM_MB = 0.0000              # G_ANC7: Zero GPU VRAM footprint

# Baselines from Phase 22-REL
CANONICAL_BASELINES = {
    "O4_Warmth_R2": -4.5120,
    "O4_Fatigue_R2": 0.3781,
    "O3_Fatigue_R2": 0.5702,
    "Observable_4D_R2": 0.5192,
    "Session_Retention_Ratio": 0.9840,
    "Latency_CPU_P50_ms": 0.0001,
}
