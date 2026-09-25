"""
Config module for Phase 22-XR evaluation harness.
"""
from typing import List, Dict
import numpy as np

# Evaluation Seeds
EVAL_SEEDS: List[int] = [42, 137, 618, 1024, 2026]

# Latent State Dimensions (D = 6)
STATE_DIM = 6
STATE_DIM_NAMES: List[str] = [
    "load",       # Estimated cognitive processing strain in [-1, 1]
    "agency",     # Goal-directedness vs exploratory drift in [-1, 1]
    "valence",    # Conversational affective alignment in [-1, 1]
    "urgency",    # Time pressure / deadline sensitivity in [0, 1]
    "receptive",  # Openness to epistemic clarification in [0, 1]
    "alignment",  # Agreement vs contradiction with Lucia in [-1, 1]
]

# Intent Classes (K = 8)
INTENT_CLASSES: List[str] = [
    "Query",
    "Clarification",
    "Affirmation",
    "Correction",
    "Elaboration",
    "TopicShift",
    "Disengagement",
    "Feedback",
]
NUM_INTENTS = len(INTENT_CLASSES)
INTENT_TO_IDX = {intent: i for i, intent in enumerate(INTENT_CLASSES)}
IDX_TO_INTENT = {i: intent for i, intent in enumerate(INTENT_CLASSES)}

# Psychological Probes for Observation Heads (M = 6)
PROBE_NAMES: List[str] = [
    "probe_load",
    "probe_agency",
    "probe_valence",
    "probe_urgency",
    "probe_receptive",
    "probe_alignment",
]
NUM_PROBES = len(PROBE_NAMES)

# Distribution Shift Regimes
REGIME_CANONICAL = "Canonical"
REGIME_NOISE_SURGE = "DS-1_NoiseSurge"
REGIME_TOPIC_SHIFT = "DS-2_TopicShift"
REGIME_CONTRADICTION = "DS-3_Contradiction"
REGIME_LEXICAL_SPARSITY = "DS-4_LexicalSparsity"
REGIME_INTENT_SHIFT = "DS-5_IntentShift"

ALL_REGIMES = [
    REGIME_CANONICAL,
    REGIME_NOISE_SURGE,
    REGIME_TOPIC_SHIFT,
    REGIME_CONTRADICTION,
    REGIME_LEXICAL_SPARSITY,
    REGIME_INTENT_SHIFT,
]

# Pre-registered Architecture Gate Thresholds
GATE_THRESHOLDS = {
    "G-XR1": {"metric": "ECE_shift", "required": 0.10, "falsify": 0.15, "cmp": "le"},
    "G-XR2": {"metric": "Tracking_R2", "required": 0.85, "falsify": 0.70, "cmp": "ge"},
    "G-XR3": {"metric": "Flapping_Rate", "required": 0.095, "falsify": 0.15, "cmp": "le"},
    "G-XR4": {"metric": "Density_Coverage_H2", "required": 0.75, "falsify": 0.50, "cmp": "ge"},
    "G-XR5": {"metric": "Contradiction_Recovery_Turns", "required": 1.0, "falsify": 2.0, "cmp": "le"},
    "G-XR6_CPU": {"metric": "CPU_Latency_ms", "required": 350.0, "falsify": 500.0, "cmp": "le"},
    "G-XR6_GPU": {"metric": "GPU_Latency_ms", "required": 50.0, "falsify": 100.0, "cmp": "le"},
}
