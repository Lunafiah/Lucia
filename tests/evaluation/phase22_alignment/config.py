"""
Configuration and Preregistered Thresholds for Phase 22-AL
(Observation-to-Latent Alignment Study).
"""
from typing import Dict, List, Any
import numpy as np

# Anti-Cheating Seed Split
TRAIN_SEEDS: List[int] = [42, 137, 618]
HELD_OUT_SEEDS: List[int] = [1024, 2026]
ALL_SEEDS: List[int] = TRAIN_SEEDS + HELD_OUT_SEEDS

LANGUAGES: List[str] = ["English", "Vietnamese", "Japanese"]
REGIMES: List[str] = [
    "ID",
    "NoiseSurge",
    "LexicalSparsity",
    "ContradictionShock",
    "TemporalDrift",
    "CombinedStress",
]

CANDIDATES: List[str] = ["C1", "C2", "C3", "C4", "C5", "C6"]
ALIGNMENT_MODELS: List[str] = ["A0", "A1", "A2", "A3", "A4", "A5", "A6", "A7"]
TEMPORAL_WINDOWS: List[int] = [1, 3, 5, 10]

STATE_DIM: int = 6
INTERFACE_DIM: int = 12

GATE_THRESHOLDS = {
    "target_r2": 0.85,
    "falsification_r2": 0.70,
    "target_mae": 0.20,
    "gate_mae": 0.30,
    "target_flapping": 0.020, # <= 2.0%
    "gate_flapping": 0.095,   # <= 9.5%
    "target_recovery_turns": 1.0,
    "target_cpu_p50_ms": 50.0,
    "gate_cpu_p50_ms": 100.0,
    "trajectory_coverage_h2": 0.90,
}

HISTORICAL_BASELINES = {
    "Real_Laya": {
        "params": 421438464,
        "cpu_p50_ms": 607.67,
        "ece": 0.2232,
        "m2_r2": 0.4051,
        "flapping": 0.0040,
        "recovery": 1.0,
    },
    "C1_zero_shot_r2": -0.9706,
    "C2_zero_shot_r2": -0.5750,
    "C3_zero_shot_r2": -3.6096,
    "C4_zero_shot_r2": -0.7606,
    "C5_zero_shot_r2": -2.2530,
    "C6_zero_shot_r2": -0.5750,
}
