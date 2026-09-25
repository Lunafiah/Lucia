"""
Config module for Phase 22-XR Follow-Up evaluation harness.
"""
from typing import List, Dict

# Evaluation Seeds
EVAL_SEEDS: List[int] = [42, 137, 618, 1024, 2026]
CALIBRATION_SEED: int = 9999

# Dimensions
STATE_DIM = 6
NUM_PROBES = 6

STATE_DIM_NAMES: List[str] = [
    "load",       # Estimated cognitive processing strain in [-1, 1]
    "agency",     # Goal-directedness vs exploratory drift in [-1, 1]
    "valence",    # Conversational affective alignment in [-1, 1]
    "urgency",    # Time pressure / deadline sensitivity in [0, 1]
    "receptive",  # Openness to epistemic clarification in [0, 1]
    "alignment",  # Agreement vs contradiction with Lucia in [-1, 1]
]

# Preregistered Architecture Gate Thresholds
GATE_THRESHOLDS = {
    "G-XR1": {"metric": "ECE_shift", "required": 0.10, "falsify": 0.15, "cmp": "le"},
    "G-XR2": {"metric": "Tracking_R2", "required": 0.85, "falsify": 0.70, "cmp": "ge"},
    "G-XR3": {"metric": "Flapping_Rate", "required": 0.095, "falsify": 0.15, "cmp": "le"},
    "G-XR4": {"metric": "Density_Coverage_H2", "required": 0.75, "falsify": 0.50, "cmp": "ge"},
    "G-XR5": {"metric": "Contradiction_Recovery_Turns", "required": 1.0, "falsify": 2.0, "cmp": "le"},
    "G-XR6": {"metric": "CPU_Total_P50_ms", "required": 350.0, "falsify": 500.0, "cmp": "le"},
}
