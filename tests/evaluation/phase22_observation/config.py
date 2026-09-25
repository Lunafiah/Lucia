"""
Configuration and Preregistered Thresholds for Phase 22 Observation Layer Study.
Derived directly from OBSERVATION_LAYER_REQUIREMENTS.md.
"""
from typing import Dict, List, Any
import numpy as np

SEEDS: List[int] = [42, 137, 618, 1024, 2026]
LANGUAGES: List[str] = ["English", "Vietnamese", "Japanese"]
REGIMES: List[str] = [
    "ID",
    "NoiseSurge",
    "LexicalSparsity",
    "ContradictionShock",
    "TemporalDrift",
    "CombinedStress",
]

CANDIDATE_IDS: List[str] = ["C1", "C2", "C3", "C4", "C5", "C6"]

CANDIDATE_METADATA: Dict[str, Dict[str, Any]] = {
    "C1": {
        "id": "C1",
        "name": "Lightweight Multilingual Sentence Encoder",
        "class": "MiniLM Bi-Encoder Anchor Projector",
        "param_count": 22700000,
        "serialized_size_mb": 87.2,
        "param_budget": "20M-40M",
    },
    "C2": {
        "id": "C2",
        "name": "Distilled Semantic Encoder",
        "class": "Distil-ModernBERT-Conversational",
        "param_count": 28400000,
        "serialized_size_mb": 108.5,
        "param_budget": "15M-60M",
    },
    "C3": {
        "id": "C3",
        "name": "Audio-First Acoustic/Prosodic Encoder",
        "class": "Acoustic DSP Feature Extractor",
        "param_count": 125000,
        "serialized_size_mb": 0.5,
        "param_budget": "<1M",
    },
    "C4": {
        "id": "C4",
        "name": "Hybrid Multimodal Observation",
        "class": "Text Semantic + Audio Prosodic Fusion",
        "param_count": 22825000,
        "serialized_size_mb": 87.7,
        "param_budget": "25M-50M",
    },
    "C5": {
        "id": "C5",
        "name": "Structured Semantic Observation",
        "class": "Structured Dialogue Act / Intent Slot Extractor",
        "param_count": 18200000,
        "serialized_size_mb": 71.4,
        "param_budget": "10M-30M",
    },
    "C6": {
        "id": "C6",
        "name": "Decoupled Learned Observation Projection Layer",
        "class": "Decoupled g^-1 Calibrated Log-Odds Projector",
        "param_count": 28450000,
        "serialized_size_mb": 108.8,
        "param_budget": "~50K (projection layer)",
    },
}

STATE_DIM: int = 6
INTERFACE_DIM: int = 12

GATE_THRESHOLDS = {
    "G_OBS1_CALIB_ECE": 0.10,
    "G_OBS1_CALIB_BRIER": 0.0842, # Must be lower than Real Laya baseline (0.0842)
    "G_OBS2_ALIGN_R2": 0.85,
    "G_OBS2_ALIGN_FALSIFY": 0.70,
    "G_OBS3_STAB_FLAPPING": 0.020, # <= 2.0%
    "G_OBS3_STAB_RECOVERY": 1.0,   # <= 1.0 turn
    "G_OBS4_TRAJ_COVERAGE": 0.90,  # >= 90.0%
    "G_OBS5_LATENCY_CPU_P50": 50.0, # <= 50.0 ms
    "G_OBS6_RES_RAM_MB": 500.0,    # <= 500 MB
    "G_OBS7_MULTI_RATIO": 0.85,    # >= 0.85
    "G_OBS8_INTERFACE_DIM": 12,
}

HISTORICAL_REAL_LAYA = {
    "model": "convaiinnovations/laya",
    "architecture": "ModernBERT-large",
    "parameters": 421438464,
    "cpu_p50_ms": 607.67,
    "total_p50_ms": 607.83,
    "ece": 0.2232,
    "brier": 0.0842,
    "flapping_rate": 0.0040,
    "contradiction_recovery_turns": 1.0,
    "m0_r2": -25.13,
    "m2_r2": 0.4051,
    "original_trajectory_coverage_h2": 0.2867,
    "calibrated_c2_coverage": 1.0000,
}
