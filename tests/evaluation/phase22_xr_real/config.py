"""Configuration for Phase 22-XR-L Real Laya Observation Verification."""

import os
from dataclasses import dataclass, field
from pathlib import Path
from typing import List, Tuple

# Base paths
PROJECT_ROOT = Path(__file__).resolve().parents[3]
EVAL_DIR = Path(__file__).resolve().parent
ARTIFACTS_DIR = PROJECT_ROOT / "evaluation_artifacts" / "phase22_xr_real"
LAYA_REPO_DIR = Path(r"C:\Users\Lunafiah\Desktop\My_project\laya")

# Seeds
SEEDS: List[int] = [42, 137, 618, 1024, 2026]

# Gates
GATE_THRESHOLDS = {
    "G_XRL1_ECE_TARGET": 0.10,
    "G_XRL1_ECE_FALSIFY": 0.15,
    "G_XRL2_R2_TARGET": 0.85,
    "G_XRL2_R2_FALSIFY": 0.70,
    "G_XRL3_FLAPPING_TARGET": 0.095,  # <= 9.5%
    "G_XRL4_CONTRADICTION_TARGET": 1.0,  # <= 1.0 turn
    "G_XRL5_LATENCY_CPU_TARGET_MS": 350.0,  # <= 350 ms CPU
}

# Laya configuration
LAYA_CHECKPOINT_ID = "convaiinnovations/laya"
EXPECTED_BASE_MODEL = "answerdotai/ModernBERT-large"
NUM_CLASSES = 6
DIM_STATE = 6

CLASSES = [
    "clarification",
    "direct_answer",
    "elaborate",
    "summarize",
    "suggest_alternative",
    "acknowledge",
]

LATENT_DIMS = [
    "engagement",
    "cognitive_load",
    "receptivity",
    "clarity_need",
    "valence",
    "epistemic_trust",
]

# Perturbation regimes
REGIMES = [
    "clean",
    "lexical_perturbation",
    "typo_noise",
    "lexical_sparsity",
    "contradiction",
    "multilingual_en",
    "multilingual_vi",
    "multilingual_ja",
]
