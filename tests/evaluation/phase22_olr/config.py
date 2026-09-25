"""
Configuration, Constants, and Thresholds for Phase 22-OLR
(Observation Layer Replacement Study).

Derived strictly from OBSERVATION_LAYER_REQUIREMENTS.md.
"""
from typing import Dict, List, Tuple
import numpy as np

# Canonical Seeds
SEEDS: List[int] = [42, 137, 618, 1024, 2026]

# Canonical Languages
LANGUAGES: List[str] = ["English", "Vietnamese", "Japanese"]

# Stress Regimes (matching SimUserEnv-v2)
REGIMES: List[str] = [
    "ID",
    "NoiseSurge",
    "LexicalSparsity",
    "ContradictionShock",
    "TemporalDrift",
    "CombinedStress",
]

# Candidate Classes
CANDIDATE_IDS: List[str] = ["C1", "C2", "C3", "C4", "C5", "C6"]

CANDIDATE_METADATA: Dict[str, Dict[str, str]] = {
    "C1": {
        "name": "Lightweight Multilingual Sentence Encoder",
        "description": "Compact bi-encoder embedding with anchor vector projection (MiniLM-style)",
        "parameter_budget": "20M-40M",
    },
    "C2": {
        "name": "Distilled Semantic Encoder",
        "description": "Compressed conversational act encoder distilled with temperature scaling",
        "parameter_budget": "15M-60M",
    },
    "C3": {
        "name": "Audio-First Acoustic/Prosodic Encoder",
        "description": "Non-verbal acoustic DSP (pitch, jitter, energy, tempo, silence duration)",
        "parameter_budget": "<1M",
    },
    "C4": {
        "name": "Hybrid Multimodal Observation",
        "description": "Dynamically fused text semantic embedding and acoustic prosodic features",
        "parameter_budget": "25M-50M",
    },
    "C5": {
        "name": "Structured Semantic Observation",
        "description": "Renderer-independent dialogue acts & intent slot representation (P23 compatible)",
        "parameter_budget": "10M-30M",
    },
    "C6": {
        "name": "Decoupled Learned Observation Projection Layer",
        "description": "Frozen encoder with explicit calibrated inverse measurement projection g^-1",
        "parameter_budget": "~50K (projection layer)",
    },
}

# State Dimensions
STATE_DIM: int = 6
P23_INTERFACE_DIM: int = 12

STATE_DIM_NAMES: List[str] = [
    "cognitive_load",
    "relational_valence",
    "dominance_agency",
    "urgency",
    "receptive_openness",
    "attentional_alignment",
]

# Frozen Preregistered Acceptance Gates (OBSERVATION_LAYER_REQUIREMENTS.md)
GATE_THRESHOLDS = {
    "ece_threshold": 0.15,
    "ece_target": 0.10,
    "brier_threshold": 0.12,
    "brier_target": 0.08,
    "r2_threshold": 0.70,
    "r2_target": 0.85,
    "mae_threshold": 0.30,
    "mae_target": 0.20,
    "flapping_threshold": 0.095,  # 9.5%
    "flapping_target": 0.020,     # 2.0%
    "recovery_turns_threshold": 1.0,
    "cpu_p50_latency_threshold_ms": 100.0,
    "cpu_p50_latency_target_ms": 50.0,
    "total_p50_latency_threshold_ms": 120.0,
    "ram_mb_threshold": 1000.0,
    "ram_mb_target": 500.0,
    "gpu_vram_mb_ceiling": 0.0,
    "multilingual_transfer_threshold": 0.75,
    "multilingual_transfer_target": 0.85,
}

# Historical Baselines for Comparison
HISTORICAL_BASELINES = {
    "real_laya": {
        "model": "convaiinnovations/laya",
        "architecture": "ModernBERT-large",
        "params": 421438464,
        "ece": 0.2232,
        "brier": 0.0842,
        "cpu_p50_ms": 607.67,
        "total_p50_ms": 607.83,
        "flapping_rate": 0.0040,
        "contradiction_recovery_turns": 1.0,
        "m0_r2": -25.13,
        "m2_r2": 0.4051,
        "m4_r2": 0.4049,
        "original_trajectory_coverage_h2": 0.2867,
        "calibrated_c2_coverage": 1.0000,
    },
    "phase22_x_discrete": {
        "flapping_rate": 0.2380,
    }
}
