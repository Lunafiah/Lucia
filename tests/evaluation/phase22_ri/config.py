"""
Configuration and Preregistered Thresholds for Phase 22-RI:
Relational Inference & Episodic Relationship Semantics Study.
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

# Relational Trust Tiers Taxonomy
TRUST_TIERS = [
    "T0_STRANGER",      # Initial onboarding / zero history / strictly formal boundary
    "T1_ACQUAINTANCE",  # Multiple successful neutral interactions / polite working boundary
    "T2_COLLABORATOR",  # Proven task alignment / collaborative problem solving / mutual reliability
    "T3_COMPANION",     # Personal autobiographical sharing / persistent warmth / emotional resonance
    "T4_CONFIDANT",     # Deep mutual vulnerability / high trust / shared history / resilient to minor ruptures
]

# Relational Stance Predicates (Non-Scalar Categorical Dimensions)
RELATIONAL_PREDICATES = [
    "rapport_alignment",     # Harmonious communication & shared rhythm
    "epistemic_reliance",    # User relies on Lucia's domain competencies
    "emotional_openness",    # Willingness to express vulnerable sentiments
    "rupture_guardedness",   # Defensive stance following interpersonal friction
    "collaborative_agency",  # Joint initiative and reciprocal agency
]

# Preregistered Acceptance Gates (Discrete & Epistemic Metrics)
GATE_TIER_ACCURACY = 0.8500        # G_RI1: Trust Tier classification accuracy (>= 85%)
GATE_OVER_INFERENCE_RATE = 0.0500  # G_RI2: Over-inference of intimacy/trust on weak/insufficient observation (<= 5%)
GATE_RUPTURE_SENSITIVITY = 0.9000  # G_RI3: Rapid, accurate transition to guarded stance upon rupture (>= 90%)
GATE_REPAIR_VERIFICATION = 0.8000  # G_RI4: Repair recognized only upon explicit bilateral evidence (>= 80%)
GATE_CALIBRATION_ECE = 0.1000      # G_RI5: Expected Calibration Error of relational uncertainty (<= 0.10)
GATE_CPU_P50_MS = 2.0000           # G_RI6: CPU latency SLA (P50 <= 2.0 ms)
GATE_VRAM_MB = 0.0000              # G_RI7: Zero GPU VRAM footprint

# Baselines from Phase 22-ANCHOR
CANONICAL_BASELINES = {
    "A0_Warmth_R2": -2.9071,
    "A1_Episodic_Warmth_R2": -1.2655,
    "A3_Consolidation_Warmth_R2": -1.1375,
    "Anchor_Recall": 0.7662,
    "Non_Anchor_Drift": 0.0000,
    "Latency_CPU_P50_ms": 0.0748,
}
