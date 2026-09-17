"""
Phase 22 H1 — R3 Consumer Plausibility & Utility-Compatibility Study
===================================================================
Script: evaluate_r3_consumer_plausibility.py

Research Question:
Are the parameter regimes in which R3 becomes behaviorally visible compatible
with the intended utility and homeostatic role of a Lucia downstream consumer,
or does achieving R3 differentiation require economically implausible distortion
of the consumer's primary objectives?

Evaluates:
  - Controls: A_REFERENCE, B_DIRECTIONAL_SEPARABLE
  - Consumer C: C_baseline (gamma_C=1.00), C_qual_1.50 (gamma_C=1.50), C_qual_2.00 (gamma_C=2.00)
  - Consumer D: D_baseline (mu_d=0.20, gamma_kappa=1.00), D_qual_corner (mu_d=1.00, gamma_kappa=0.50)
  - Intermediate Counterfactuals for D: D_scalar_half (mu_d=0.20, gamma_kappa=0.50), D_dir_5x (mu_d=1.00, gamma_kappa=1.00)

Decomposition:
  - BASE
  - BASE + scalar
  - BASE + directional (Diagnostic counterfactual intervention only; not a physical state)
  - BASE + scalar + directional

Governance:
  - STRICTLY RESEARCH-ONLY / RESEARCH_HARNESS_ONLY
  - Architecture Gate LOCKED (production diff = 0)
  - Quality Gate 2 BLOCKED (Delta_HM = 0.0685 < 0.1500)
  - Phase 22 H1 INCONCLUSIVE
  - ADR-029 DRAFT / RESEARCH RECORD ONLY / NOT RATIFIED
  - 100% CPU Execution / 0.0 MB GPU VRAM
"""

from __future__ import annotations

import csv
import hashlib
import json
import math
import os
import sys
import time
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

import numpy as np

REPO_ROOT = Path(__file__).resolve().parent.parent.parent.parent
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from src.core.config import EmotionConfig, StimulusConfig
from src.core.emotion.emotion_core import EmotionCore
from src.core.gating.stimulus_processor import StimulusProcessor
from src.core.inference.active_inference import ActiveInferenceConfig, ActiveInferenceEngine
from tests.evaluation_phase22.scripts.calibrate_stimulus_representation import GeneratorG1

# Constants & Governance
PRIMARY_SEED = 9999
CONSUMER_SEEDS = [42, 43, 44, 45, 46]
PRIMARY_EXPOSURE_T = 12
DEADBAND_EPSILON = 0.010
SCALAR_MATCH_THRESHOLD = 0.020

ACTIONS = [
    "answer",    # A1: immediate response
    "clarify",   # A2: external clarification
    "retrieve",  # A3: extended SDM memory probe
    "derive",    # A4: knowledge derivation
    "reason",    # A5: deep reasoning mode shift
    "wait",      # A6: wait conversational pause
]

# =============================================================================
# Locked Base Parameter Arrays (Bit-Exact from Transferability & Sensitivity)
# =============================================================================

# --- Consumer A: Historical Reference EFE Adapter ---
A_BASE_COSTS = np.array([0.15, 0.45, 0.35, 0.40, 0.60, 0.10], dtype=np.float64)
A_BASE_DK = np.array([0.05, 0.70, 0.40, 0.50, 0.60, 0.00], dtype=np.float64)
A_BASE_DM = np.array([0.05, 0.20, 0.65, 0.30, 0.40, 0.00], dtype=np.float64)
A_ACTION_WEIGHTS = np.array([
    [ 0.10, -0.15,  0.10],  # answer
    [-0.25,  0.15, -0.10],  # clarify
    [ 0.20, -0.10,  0.15],  # retrieve
    [ 0.10,  0.15,  0.10],  # derive
    [-0.15,  0.25, -0.15],  # reason
    [-0.10, -0.20, -0.20],  # wait
], dtype=np.float64)

# --- Consumer B: Historical Direction-Separable Additive Model ---
B_G_BASE = np.array([0.25, 0.55, 0.45, 0.50, 0.70, 0.20], dtype=np.float64)
B_ALPHA_S = np.array([-0.10, 0.25, 0.15, 0.20, 0.35, -0.20], dtype=np.float64)
B_BETA_S2 = np.array([0.30, 0.10, 0.20, 0.15, 0.40, 0.50], dtype=np.float64)
B_W_DIR = np.array([
    [ 0.15, -0.20,  0.05],  # answer
    [-0.30,  0.20, -0.15],  # clarify
    [ 0.25, -0.15,  0.20],  # retrieve
    [ 0.05,  0.20,  0.15],  # derive
    [-0.20,  0.30, -0.10],  # reason
    [-0.15, -0.25, -0.25],  # wait
], dtype=np.float64)

# --- Consumer C: Base Parameter Vectors ---
C_U_BASE = np.array([1.20, 0.60, 0.80, 0.70, 0.50, 1.10], dtype=np.float64)
C_COST_S = np.array([0.40, 0.15, 0.25, 0.30, 0.10, 0.50], dtype=np.float64)
C_M_BASE = np.array([
    [ 0.25, -0.30,  0.15],  # answer
    [-0.35,  0.30, -0.20],  # clarify
    [ 0.30, -0.15,  0.25],  # retrieve
    [ 0.15,  0.25,  0.10],  # derive
    [-0.25,  0.40, -0.15],  # reason
    [-0.15, -0.35, -0.30],  # wait
], dtype=np.float64)

# --- Consumer D: Base Parameter Vectors ---
D_G_BASE = np.array([0.10, 0.30, 0.20, 0.25, 0.40, 0.05], dtype=np.float64)
D_KAPPA_S_BASE = np.array([1.50, 4.00, 2.50, 3.00, 5.50, 0.80], dtype=np.float64)
D_W_DIR = np.array([
    [ 0.10, -0.15,  0.10],  # answer
    [-0.20,  0.15, -0.10],  # clarify
    [ 0.20, -0.10,  0.15],  # retrieve
    [ 0.10,  0.15,  0.10],  # derive
    [-0.15,  0.25, -0.15],  # reason
    [-0.10, -0.20, -0.20],  # wait
], dtype=np.float64)


def array_hash(arr: np.ndarray) -> str:
    return hashlib.sha256(arr.tobytes()).hexdigest()


LOCKED_BASE_HASHES = {
    "C_U_BASE": array_hash(C_U_BASE),
    "C_COST_S": array_hash(C_COST_S),
    "C_M_BASE": array_hash(C_M_BASE),
    "D_G_BASE": array_hash(D_G_BASE),
    "D_KAPPA_S_BASE": array_hash(D_KAPPA_S_BASE),
    "D_W_DIR": array_hash(D_W_DIR),
}


# =============================================================================
# Mathematical Helpers
# =============================================================================

def compute_sha256(path: Path) -> str:
    with open(path, "rb") as f:
        return hashlib.sha256(f.read()).hexdigest()


def deadband_sign(x: float, eps: float = DEADBAND_EPSILON) -> int:
    if abs(x) <= eps:
        return 0
    return 1 if x > 0 else -1


def compute_js_divergence(p: np.ndarray, q: np.ndarray) -> float:
    p_safe = np.clip(p, 1e-12, 1.0)
    q_safe = np.clip(q, 1e-12, 1.0)
    p_safe /= np.sum(p_safe)
    q_safe /= np.sum(q_safe)
    m = 0.5 * (p_safe + q_safe)
    kl_p_m = np.sum(p_safe * np.log(p_safe / m))
    kl_q_m = np.sum(q_safe * np.log(q_safe / m))
    return float(0.5 * (kl_p_m + kl_q_m))


def compute_tv_distance(p: np.ndarray, q: np.ndarray) -> float:
    return float(0.5 * np.sum(np.abs(p - q)))


def compute_entropy(p: np.ndarray) -> float:
    p_safe = np.clip(p, 1e-12, 1.0)
    p_safe /= np.sum(p_safe)
    return float(-np.sum(p_safe * np.log(p_safe)))


def spearman_rank_correlation(x: np.ndarray, y: np.ndarray) -> float:
    if len(x) != len(y) or len(x) < 2:
        return 1.0
    rank_x = np.argsort(np.argsort(x)).astype(float)
    rank_y = np.argsort(np.argsort(y)).astype(float)
    d = rank_x - rank_y
    n = len(x)
    denom = n * (n * n - 1)
    if denom == 0:
        return 1.0
    return float(1.0 - (6.0 * np.sum(d ** 2)) / denom)


# =============================================================================
# Valuation & Decomposition Data Structures
# =============================================================================

@dataclass(frozen=True)
class ConsumerValuationResult:
    consumer_id: str
    condition: str
    scalar_s: float
    ternary_signs: Tuple[int, int, int]
    valuations: List[float]
    probabilities: List[float]
    selected_action: str
    selected_action_idx: int
    entropy: float


@dataclass(frozen=True)
class CounterfactualDecompositionResult:
    probe_id: int
    scalar_s: float
    ternary_signs: Tuple[int, int, int]
    v_base: List[float]
    v_base_scalar: List[float]
    v_base_dir: List[float]
    v_full: List[float]
    action_base: str
    action_base_scalar: str
    action_base_dir: str
    action_full: str
    norm_scalar_contrib: float
    norm_dir_contrib: float
    relative_ratio: float
    dcf: float
    dir_flips_action_from_scalar: bool
    scalar_flips_action_from_base: bool


class BaseConsumer:
    """Abstract base consumer for action valuation and decomposition."""

    def __init__(self, consumer_id: str, gamma: float = 1.0) -> None:
        self.consumer_id = consumer_id
        self.gamma = gamma

    def evaluate(
        self,
        s_val: float,
        d_signs: Tuple[int, int, int],
        condition: str,
        tie_break_noise: Optional[np.ndarray] = None,
    ) -> ConsumerValuationResult:
        raise NotImplementedError

    def decompose(
        self,
        probe_id: int,
        s_val: float,
        d_signs: Tuple[int, int, int],
        tie_break_noise: Optional[np.ndarray] = None,
    ) -> CounterfactualDecompositionResult:
        raise NotImplementedError


# =============================================================================
# Consumer Implementations
# =============================================================================

class ReferenceConsumerA(BaseConsumer):
    """Consumer A: Historical Reference EFE Adapter (Lower is Better)."""

    def __init__(self, gamma: float = 1.0) -> None:
        super().__init__("A_REFERENCE", gamma)

    def evaluate(
        self,
        s_val: float,
        d_signs: Tuple[int, int, int],
        condition: str,
        tie_break_noise: Optional[np.ndarray] = None,
    ) -> ConsumerValuationResult:
        beta_k = 1.0 + 0.50 * math.tanh(2.0 * s_val)
        beta_m = 1.0 + 0.30 * math.tanh(2.0 * s_val)

        g_pragmatic = A_BASE_COSTS
        g_epistemic = -beta_k * A_BASE_DK - beta_m * A_BASE_DM

        if condition == "C0":
            d_vec = np.zeros(3, dtype=np.float64)
        else:
            d_vec = np.array(d_signs, dtype=np.float64) / math.sqrt(3.0)

        delta_g_dir = -np.dot(A_ACTION_WEIGHTS, d_vec)
        g_vals = g_pragmatic + g_epistemic + delta_g_dir

        g_eval = g_vals.copy()
        if tie_break_noise is not None:
            g_eval += tie_break_noise

        neg_g = -self.gamma * (g_eval - np.min(g_eval))
        exp_g = np.exp(neg_g)
        probs = exp_g / np.sum(exp_g)

        best_idx = int(np.argmin(g_eval))
        best_action = ACTIONS[best_idx]
        ent = compute_entropy(probs)

        return ConsumerValuationResult(
            consumer_id=self.consumer_id,
            condition=condition,
            scalar_s=float(s_val),
            ternary_signs=d_signs,
            valuations=[float(v) for v in g_vals],
            probabilities=[float(p) for p in probs],
            selected_action=best_action,
            selected_action_idx=best_idx,
            entropy=ent,
        )

    def decompose(
        self,
        probe_id: int,
        s_val: float,
        d_signs: Tuple[int, int, int],
        tie_break_noise: Optional[np.ndarray] = None,
    ) -> CounterfactualDecompositionResult:
        d_vec = np.array(d_signs, dtype=np.float64) / math.sqrt(3.0)
        beta_k = 1.0 + 0.50 * math.tanh(2.0 * s_val)
        beta_m = 1.0 + 0.30 * math.tanh(2.0 * s_val)

        v_base = A_BASE_COSTS - 1.0 * A_BASE_DK - 1.0 * A_BASE_DM
        v_base_scalar = A_BASE_COSTS - beta_k * A_BASE_DK - beta_m * A_BASE_DM
        v_base_dir = v_base - np.dot(A_ACTION_WEIGHTS, d_vec)
        v_full = v_base_scalar - np.dot(A_ACTION_WEIGHTS, d_vec)

        act_base = ACTIONS[int(np.argmin(v_base))]
        act_base_scalar = ACTIONS[int(np.argmin(v_base_scalar))]
        act_base_dir = ACTIONS[int(np.argmin(v_base_dir))]
        act_full = ACTIONS[int(np.argmin(v_full))]

        diff_scalar = v_base_scalar - v_base
        diff_dir = v_full - v_base_scalar
        norm_s = float(np.linalg.norm(diff_scalar))
        norm_d = float(np.linalg.norm(diff_dir))
        rel_ratio = float(norm_d / (norm_s + 1e-12))
        dcf = float(norm_d / (norm_s + norm_d + 1e-12))

        return CounterfactualDecompositionResult(
            probe_id=probe_id,
            scalar_s=s_val,
            ternary_signs=d_signs,
            v_base=[float(x) for x in v_base],
            v_base_scalar=[float(x) for x in v_base_scalar],
            v_base_dir=[float(x) for x in v_base_dir],
            v_full=[float(x) for x in v_full],
            action_base=act_base,
            action_base_scalar=act_base_scalar,
            action_base_dir=act_base_dir,
            action_full=act_full,
            norm_scalar_contrib=norm_s,
            norm_dir_contrib=norm_d,
            relative_ratio=rel_ratio,
            dcf=dcf,
            dir_flips_action_from_scalar=(act_full != act_base_scalar),
            scalar_flips_action_from_base=(act_base_scalar != act_base),
        )


class DirectionalSeparableConsumerB(BaseConsumer):
    """Consumer B: Additive Linear-Quadratic Cost Model (Lower is Better)."""

    def __init__(self, gamma: float = 1.0) -> None:
        super().__init__("B_DIRECTIONAL_SEPARABLE", gamma)

    def evaluate(
        self,
        s_val: float,
        d_signs: Tuple[int, int, int],
        condition: str,
        tie_break_noise: Optional[np.ndarray] = None,
    ) -> ConsumerValuationResult:
        g_scalar = B_G_BASE + B_ALPHA_S * s_val + B_BETA_S2 * (s_val ** 2)

        if condition == "C0":
            d_vec = np.zeros(3, dtype=np.float64)
        else:
            d_vec = np.array(d_signs, dtype=np.float64) / math.sqrt(3.0)

        delta_g_dir = -np.dot(B_W_DIR, d_vec)
        g_vals = g_scalar + delta_g_dir

        g_eval = g_vals.copy()
        if tie_break_noise is not None:
            g_eval += tie_break_noise

        neg_g = -self.gamma * (g_eval - np.min(g_eval))
        exp_g = np.exp(neg_g)
        probs = exp_g / np.sum(exp_g)

        best_idx = int(np.argmin(g_eval))
        best_action = ACTIONS[best_idx]
        ent = compute_entropy(probs)

        return ConsumerValuationResult(
            consumer_id=self.consumer_id,
            condition=condition,
            scalar_s=float(s_val),
            ternary_signs=d_signs,
            valuations=[float(v) for v in g_vals],
            probabilities=[float(p) for p in probs],
            selected_action=best_action,
            selected_action_idx=best_idx,
            entropy=ent,
        )

    def decompose(
        self,
        probe_id: int,
        s_val: float,
        d_signs: Tuple[int, int, int],
        tie_break_noise: Optional[np.ndarray] = None,
    ) -> CounterfactualDecompositionResult:
        d_vec = np.array(d_signs, dtype=np.float64) / math.sqrt(3.0)

        v_base = B_G_BASE.copy()
        v_base_scalar = B_G_BASE + B_ALPHA_S * s_val + B_BETA_S2 * (s_val ** 2)
        v_base_dir = B_G_BASE - np.dot(B_W_DIR, d_vec)
        v_full = v_base_scalar - np.dot(B_W_DIR, d_vec)

        act_base = ACTIONS[int(np.argmin(v_base))]
        act_base_scalar = ACTIONS[int(np.argmin(v_base_scalar))]
        act_base_dir = ACTIONS[int(np.argmin(v_base_dir))]
        act_full = ACTIONS[int(np.argmin(v_full))]

        diff_scalar = v_base_scalar - v_base
        diff_dir = v_full - v_base_scalar
        norm_s = float(np.linalg.norm(diff_scalar))
        norm_d = float(np.linalg.norm(diff_dir))
        rel_ratio = float(norm_d / (norm_s + 1e-12))
        dcf = float(norm_d / (norm_s + norm_d + 1e-12))

        return CounterfactualDecompositionResult(
            probe_id=probe_id,
            scalar_s=s_val,
            ternary_signs=d_signs,
            v_base=[float(x) for x in v_base],
            v_base_scalar=[float(x) for x in v_base_scalar],
            v_base_dir=[float(x) for x in v_base_dir],
            v_full=[float(x) for x in v_full],
            action_base=act_base,
            action_base_scalar=act_base_scalar,
            action_base_dir=act_base_dir,
            action_full=act_full,
            norm_scalar_contrib=norm_s,
            norm_dir_contrib=norm_d,
            relative_ratio=rel_ratio,
            dcf=dcf,
            dir_flips_action_from_scalar=(act_full != act_base_scalar),
            scalar_flips_action_from_base=(act_base_scalar != act_base),
        )


class ContinuousUtilityConsumerC(BaseConsumer):
    """Consumer C: Multiplicative Exponential Utility (Higher is Better)."""

    def __init__(self, gamma_C: float, gamma: float = 1.0) -> None:
        c_id = f"C_gamma_{gamma_C:.2f}"
        super().__init__(c_id, gamma)
        self.gamma_C = float(gamma_C)
        self.m_dir = self.gamma_C * C_M_BASE

    def evaluate(
        self,
        s_val: float,
        d_signs: Tuple[int, int, int],
        condition: str,
        tie_break_noise: Optional[np.ndarray] = None,
    ) -> ConsumerValuationResult:
        if condition == "C0":
            d_vec = np.zeros(3, dtype=np.float64)
        else:
            d_vec = np.array(d_signs, dtype=np.float64) / math.sqrt(3.0)

        dir_mult = np.exp(np.dot(self.m_dir, d_vec))
        u_vals = C_U_BASE * dir_mult - C_COST_S * s_val

        u_eval = u_vals.copy()
        if tie_break_noise is not None:
            u_eval += tie_break_noise

        pos_u = self.gamma * (u_eval - np.max(u_eval))
        exp_u = np.exp(pos_u)
        probs = exp_u / np.sum(exp_u)

        best_idx = int(np.argmax(u_eval))
        best_action = ACTIONS[best_idx]
        ent = compute_entropy(probs)

        return ConsumerValuationResult(
            consumer_id=self.consumer_id,
            condition=condition,
            scalar_s=float(s_val),
            ternary_signs=d_signs,
            valuations=[float(v) for v in u_vals],
            probabilities=[float(p) for p in probs],
            selected_action=best_action,
            selected_action_idx=best_idx,
            entropy=ent,
        )

    def decompose(
        self,
        probe_id: int,
        s_val: float,
        d_signs: Tuple[int, int, int],
        tie_break_noise: Optional[np.ndarray] = None,
    ) -> CounterfactualDecompositionResult:
        d_vec = np.array(d_signs, dtype=np.float64) / math.sqrt(3.0)

        v_base = C_U_BASE.copy()
        v_base_scalar = C_U_BASE - C_COST_S * s_val
        dir_mult = np.exp(np.dot(self.m_dir, d_vec))
        v_base_dir = C_U_BASE * dir_mult
        v_full = C_U_BASE * dir_mult - C_COST_S * s_val

        act_base = ACTIONS[int(np.argmax(v_base))]
        act_base_scalar = ACTIONS[int(np.argmax(v_base_scalar))]
        act_base_dir = ACTIONS[int(np.argmax(v_base_dir))]
        act_full = ACTIONS[int(np.argmax(v_full))]

        diff_scalar = v_base_scalar - v_base
        diff_dir = v_full - v_base_scalar
        norm_s = float(np.linalg.norm(diff_scalar))
        norm_d = float(np.linalg.norm(diff_dir))
        rel_ratio = float(norm_d / (norm_s + 1e-12))
        dcf = float(norm_d / (norm_s + norm_d + 1e-12))

        return CounterfactualDecompositionResult(
            probe_id=probe_id,
            scalar_s=s_val,
            ternary_signs=d_signs,
            v_base=[float(x) for x in v_base],
            v_base_scalar=[float(x) for x in v_base_scalar],
            v_base_dir=[float(x) for x in v_base_dir],
            v_full=[float(x) for x in v_full],
            action_base=act_base,
            action_base_scalar=act_base_scalar,
            action_base_dir=act_base_dir,
            action_full=act_full,
            norm_scalar_contrib=norm_s,
            norm_dir_contrib=norm_d,
            relative_ratio=rel_ratio,
            dcf=dcf,
            dir_flips_action_from_scalar=(act_full != act_base_scalar),
            scalar_flips_action_from_base=(act_base_scalar != act_base),
        )


class MagnitudeDominantConsumerD(BaseConsumer):
    """Consumer D: Magnitude-Dominant Non-Linear Model (Lower is Better)."""

    def __init__(self, mu_d: float, gamma_kappa: float, gamma: float = 1.0) -> None:
        c_id = f"D_mu_{mu_d:.2f}_gk_{gamma_kappa:.2f}"
        super().__init__(c_id, gamma)
        self.mu_d = float(mu_d)
        self.gamma_kappa = float(gamma_kappa)
        self.kappa_s = self.gamma_kappa * D_KAPPA_S_BASE

    def evaluate(
        self,
        s_val: float,
        d_signs: Tuple[int, int, int],
        condition: str,
        tie_break_noise: Optional[np.ndarray] = None,
    ) -> ConsumerValuationResult:
        if condition == "C0":
            d_vec = np.zeros(3, dtype=np.float64)
        else:
            d_vec = np.array(d_signs, dtype=np.float64) / math.sqrt(3.0)

        g_scalar = D_G_BASE + self.kappa_s * s_val
        delta_g_dir = -self.mu_d * np.dot(D_W_DIR, d_vec)
        g_vals = g_scalar + delta_g_dir

        g_eval = g_vals.copy()
        if tie_break_noise is not None:
            g_eval += tie_break_noise

        neg_g = -self.gamma * (g_eval - np.min(g_eval))
        exp_g = np.exp(neg_g)
        probs = exp_g / np.sum(exp_g)

        best_idx = int(np.argmin(g_eval))
        best_action = ACTIONS[best_idx]
        ent = compute_entropy(probs)

        return ConsumerValuationResult(
            consumer_id=self.consumer_id,
            condition=condition,
            scalar_s=float(s_val),
            ternary_signs=d_signs,
            valuations=[float(v) for v in g_vals],
            probabilities=[float(p) for p in probs],
            selected_action=best_action,
            selected_action_idx=best_idx,
            entropy=ent,
        )

    def decompose(
        self,
        probe_id: int,
        s_val: float,
        d_signs: Tuple[int, int, int],
        tie_break_noise: Optional[np.ndarray] = None,
    ) -> CounterfactualDecompositionResult:
        d_vec = np.array(d_signs, dtype=np.float64) / math.sqrt(3.0)

        v_base = D_G_BASE.copy()
        v_base_scalar = D_G_BASE + self.kappa_s * s_val
        v_base_dir = D_G_BASE - self.mu_d * np.dot(D_W_DIR, d_vec)
        v_full = v_base_scalar - self.mu_d * np.dot(D_W_DIR, d_vec)

        act_base = ACTIONS[int(np.argmin(v_base))]
        act_base_scalar = ACTIONS[int(np.argmin(v_base_scalar))]
        act_base_dir = ACTIONS[int(np.argmin(v_base_dir))]
        act_full = ACTIONS[int(np.argmin(v_full))]

        diff_scalar = v_base_scalar - v_base
        diff_dir = v_full - v_base_scalar
        norm_s = float(np.linalg.norm(diff_scalar))
        norm_d = float(np.linalg.norm(diff_dir))
        rel_ratio = float(norm_d / (norm_s + 1e-12))
        dcf = float(norm_d / (norm_s + norm_d + 1e-12))

        return CounterfactualDecompositionResult(
            probe_id=probe_id,
            scalar_s=s_val,
            ternary_signs=d_signs,
            v_base=[float(x) for x in v_base],
            v_base_scalar=[float(x) for x in v_base_scalar],
            v_base_dir=[float(x) for x in v_base_dir],
            v_full=[float(x) for x in v_full],
            action_base=act_base,
            action_base_scalar=act_base_scalar,
            action_base_dir=act_base_dir,
            action_full=act_full,
            norm_scalar_contrib=norm_s,
            norm_dir_contrib=norm_d,
            relative_ratio=rel_ratio,
            dcf=dcf,
            dir_flips_action_from_scalar=(act_full != act_base_scalar),
            scalar_flips_action_from_base=(act_base_scalar != act_base),
        )


# =============================================================================
# Evaluator Engine
# =============================================================================

class R3ConsumerPlausibilityEvaluator:
    """Evaluation harness for R3 consumer plausibility and utility compatibility."""

    def __init__(self, primary_seed: int = PRIMARY_SEED) -> None:
        self.primary_seed = primary_seed
        self.core = EmotionCore(EmotionConfig())
        self.ai = ActiveInferenceEngine(ActiveInferenceConfig())
        self.sp = StimulusProcessor(StimulusConfig())

        self.all_probes: List[Dict[str, Any]] = []
        self.simulated_trajectories: Dict[int, Dict[str, Any]] = {}
        self.exhaustive_matched_pairs: List[Tuple[int, int]] = []
        self.discordant_matched_pairs: List[Tuple[int, int]] = []
        self.same_direction_matched_pairs: List[Tuple[int, int]] = []

    def generate_candidate_g1_corpus(self) -> List[Dict[str, Any]]:
        """Generate canonical frozen Candidate G1 stimulus corpus (Seed 9999, N=270, 90/tier)."""
        gen = GeneratorG1(self.sp)
        rng = np.random.default_rng(self.primary_seed)
        tiers = ["Low", "Med", "High"]
        all_probes = []

        for tier in tiers:
            for i in range(90):
                idx = (i % 30) + 1
                text, dom = gen.generate_text(tier, rng, idx)
                vec = self.sp.encode(text)
                global_idx = len(all_probes) + 1
                item = {
                    "probe_idx": i + 1,
                    "global_idx": global_idx,
                    "tier": tier,
                    "domain": dom,
                    "text": text,
                    "vector": vec.tolist(),
                }
                all_probes.append(item)

        self.all_probes = all_probes
        return all_probes

    def simulate_pad_trajectories(self, exposure_t: int = PRIMARY_EXPOSURE_T) -> Dict[int, Dict[str, Any]]:
        """Simulate Fast-Loop ODE trajectories up to exposure T=12 for all probes."""
        trajectories = {}
        for p in self.all_probes:
            g_idx = p["global_idx"]
            vec = np.array(p["vector"], dtype=np.float64)

            self.core.reset_to_resting()
            self.ai.reset()

            p0 = self.core.get_pad_state()
            p0_vec = np.array([p0.pleasure, p0.arousal, p0.dominance], dtype=np.float64)

            for _ in range(1, exposure_t + 1):
                token = self.core.push_stimulus(vec)
                pt = self.core.commit_stimulus(token)

            pt_vec = np.array([pt.pleasure, pt.arousal, pt.dominance], dtype=np.float64)
            r_vec = pt_vec - p0_vec
            s_val = float(np.linalg.norm(r_vec))
            signs = (
                deadband_sign(r_vec[0]),
                deadband_sign(r_vec[1]),
                deadband_sign(r_vec[2]),
            )

            trajectories[g_idx] = {
                "global_idx": g_idx,
                "tier": p["tier"],
                "domain": p["domain"],
                "s_val": s_val,
                "r_vec": r_vec,
                "signs": signs,
            }

        self.simulated_trajectories = trajectories
        return trajectories

    def partition_matched_pairs(self, tolerance: float = SCALAR_MATCH_THRESHOLD) -> None:
        """Extract matched pairs (|Delta S| <= tolerance) and partition by direction."""
        n_probes = len(self.all_probes)
        exhaustive = []

        for i in range(1, n_probes + 1):
            s_i = self.simulated_trajectories[i]["s_val"]
            for j in range(i + 1, n_probes + 1):
                s_j = self.simulated_trajectories[j]["s_val"]
                diff = abs(s_i - s_j)
                if diff <= tolerance:
                    exhaustive.append((diff, i, j))

        exhaustive.sort(key=lambda x: (round(x[0], 8), x[1], x[2]))
        self.exhaustive_matched_pairs = [(item[1], item[2]) for item in exhaustive]

        discordant = []
        same_dir = []
        for i, j in self.exhaustive_matched_pairs:
            s_i = self.simulated_trajectories[i]["signs"]
            s_j = self.simulated_trajectories[j]["signs"]
            if s_i != s_j:
                discordant.append((i, j))
            else:
                same_dir.append((i, j))

        self.discordant_matched_pairs = discordant
        self.same_direction_matched_pairs = same_dir

    def evaluate_consumer_on_seed(
        self,
        consumer: BaseConsumer,
        consumer_seed: int,
    ) -> Dict[str, Any]:
        """Evaluate consumer under C0, C2, C4 across corpus and matched pairs."""
        rng = np.random.default_rng(consumer_seed)
        n_probes = len(self.all_probes)

        noise_c0 = rng.uniform(0.0, 1e-6, size=(n_probes + 1, 6))
        noise_c2 = rng.uniform(0.0, 1e-6, size=(n_probes + 1, 6))
        noise_c4 = rng.uniform(0.0, 1e-6, size=(n_probes + 1, 6))

        shuffled_indices = list(range(1, n_probes + 1))
        rng.shuffle(shuffled_indices)
        shuffled_map = {orig: shuf for orig, shuf in zip(range(1, n_probes + 1), shuffled_indices)}

        outcomes: Dict[str, Dict[int, ConsumerValuationResult]] = {"C0": {}, "C2": {}, "C4": {}}

        for pid in range(1, n_probes + 1):
            info = self.simulated_trajectories[pid]
            s_val = info["s_val"]
            d_signs = info["signs"]

            outcomes["C0"][pid] = consumer.evaluate(s_val, d_signs, "C0", noise_c0[pid])
            outcomes["C2"][pid] = consumer.evaluate(s_val, d_signs, "C2", noise_c2[pid])

            shuf_d = self.simulated_trajectories[shuffled_map[pid]]["signs"]
            outcomes["C4"][pid] = consumer.evaluate(s_val, shuf_d, "C4", noise_c4[pid])

        # Discordant pairs analysis
        action_diffs_c2 = 0
        action_diffs_c0 = 0
        delta_v_c2 = []
        delta_v_c0 = []
        for i, j in self.discordant_matched_pairs:
            res_i_c2 = outcomes["C2"][i]
            res_j_c2 = outcomes["C2"][j]
            if res_i_c2.selected_action != res_j_c2.selected_action:
                action_diffs_c2 += 1
            v_i_c2 = np.array(res_i_c2.valuations)
            v_j_c2 = np.array(res_j_c2.valuations)
            delta_v_c2.append(float(np.mean(np.abs(v_i_c2 - v_j_c2))))

            res_i_c0 = outcomes["C0"][i]
            res_j_c0 = outcomes["C0"][j]
            if res_i_c0.selected_action != res_j_c0.selected_action:
                action_diffs_c0 += 1
            v_i_c0 = np.array(res_i_c0.valuations)
            v_j_c0 = np.array(res_j_c0.valuations)
            delta_v_c0.append(float(np.mean(np.abs(v_i_c0 - v_j_c0))))

        diffrate_c2 = action_diffs_c2 / len(self.discordant_matched_pairs)
        d_pair_c0 = action_diffs_c0 / len(self.discordant_matched_pairs)
        dir_gain = diffrate_c2 - d_pair_c0

        # C2 vs C4 condition shift across 270 probes
        c2_c4_flips = sum(
            1 for pid in range(1, n_probes + 1)
            if outcomes["C2"][pid].selected_action != outcomes["C4"][pid].selected_action
        )
        cond_shift = c2_c4_flips / n_probes

        # Action distribution under C2 and C0
        c2_actions = [outcomes["C2"][pid].selected_action for pid in range(1, n_probes + 1)]
        c0_actions = [outcomes["C0"][pid].selected_action for pid in range(1, n_probes + 1)]
        c2_dist = [c2_actions.count(a) / n_probes for a in ACTIONS]
        c0_dist = [c0_actions.count(a) / n_probes for a in ACTIONS]

        # Tier-stratified action distributions under C2
        tier_dists = {}
        for tier_name in ["Low", "Med", "High"]:
            tier_pids = [
                pid for pid in range(1, n_probes + 1)
                if self.simulated_trajectories[pid]["tier"] == tier_name
            ]
            tier_acts = [outcomes["C2"][pid].selected_action for pid in tier_pids]
            tier_dists[tier_name] = [tier_acts.count(a) / len(tier_pids) for a in ACTIONS]

        mean_ent = float(np.mean([outcomes["C2"][pid].entropy for pid in range(1, n_probes + 1)]))

        return {
            "consumer_id": consumer.consumer_id,
            "consumer_seed": consumer_seed,
            "diffrate_disc_c2": diffrate_c2,
            "d_pair_action_c0": d_pair_c0,
            "directional_gain": dir_gain,
            "condition_shift_c2_c4": cond_shift,
            "c2_mean_delta_v": float(np.mean(delta_v_c2)),
            "c0_mean_delta_v": float(np.mean(delta_v_c0)),
            "mean_entropy": mean_ent,
            "c2_action_distribution": c2_dist,
            "c0_action_distribution": c0_dist,
            "tier_distributions": tier_dists,
            "c2_action_choices": c2_actions,
            "c0_action_choices": c0_actions,
        }

    def evaluate_counterfactual_decomposition(self, consumer: BaseConsumer) -> Dict[str, Any]:
        """Perform 4-way counterfactual valuation decomposition on all 270 probes."""
        n_probes = len(self.all_probes)
        decomp_results: List[CounterfactualDecompositionResult] = []

        for pid in range(1, n_probes + 1):
            info = self.simulated_trajectories[pid]
            decomp = consumer.decompose(pid, info["s_val"], info["signs"])
            decomp_results.append(decomp)

        mean_norm_scalar = float(np.mean([d.norm_scalar_contrib for d in decomp_results]))
        mean_norm_dir = float(np.mean([d.norm_dir_contrib for d in decomp_results]))
        mean_rel_ratio = float(np.mean([d.relative_ratio for d in decomp_results]))
        mean_dcf = float(np.mean([d.dcf for d in decomp_results]))

        dir_flips_count = sum(1 for d in decomp_results if d.dir_flips_action_from_scalar)
        scalar_flips_count = sum(1 for d in decomp_results if d.scalar_flips_action_from_base)

        dir_flip_rate = dir_flips_count / n_probes
        scalar_flip_rate = scalar_flips_count / n_probes

        return {
            "consumer_id": consumer.consumer_id,
            "mean_norm_scalar": mean_norm_scalar,
            "mean_norm_dir": mean_norm_dir,
            "mean_relative_ratio": mean_rel_ratio,
            "mean_dcf": mean_dcf,
            "dir_flip_rate_from_scalar": dir_flip_rate,
            "scalar_flip_rate_from_base": scalar_flip_rate,
            "dir_flips_count": dir_flips_count,
            "scalar_flips_count": scalar_flips_count,
        }

    def evaluate_hard_tuple_identity(self, consumer: BaseConsumer) -> Dict[str, Any]:
        """Hard Invariant NC2: identical (S, d) tuples must yield delta_action=0, D_JS<1e-12."""
        synthetic_tuples = [
            (0.15, ( 1,  0, -1)),
            (0.35, (-1,  1,  0)),
            (0.55, ( 0, -1,  1)),
            (0.75, ( 1,  1, -1)),
            (0.90, (-1, -1,  1)),
        ]
        max_action_diff = 0
        max_js = 0.0

        for s_val, signs in synthetic_tuples:
            res1 = consumer.evaluate(s_val, signs, "C2", tie_break_noise=None)
            res2 = consumer.evaluate(s_val, signs, "C2", tie_break_noise=None)
            if res1.selected_action != res2.selected_action:
                max_action_diff += 1
            p1 = np.array(res1.probabilities)
            p2 = np.array(res2.probabilities)
            js = compute_js_divergence(p1, p2)
            if js > max_js:
                max_js = js

        return {
            "consumer_id": consumer.consumer_id,
            "delta_action_identity": float(max_action_diff),
            "d_js_identity": float(max_js),
            "passed": (max_action_diff == 0 and max_js < 1e-12),
        }


# =============================================================================
# Execution Workflow
# =============================================================================

def run_consumer_plausibility_study() -> None:
    print("=" * 76)
    print("Phase 22 H1 — R3 Consumer Plausibility & Utility-Compatibility Study")
    print("Evaluating 7 Regimes (Controls A & B, C Baseline & Qualifying, D Baseline & Qualifying)")
    print("=" * 76)

    evaluator = R3ConsumerPlausibilityEvaluator(primary_seed=PRIMARY_SEED)

    print("\n[Step 1/5] Generating Single Frozen Candidate G1 Corpus (N=270, Master Seed 9999)...")
    evaluator.generate_candidate_g1_corpus()
    print(f"  Generated {len(evaluator.all_probes)} probes across Low, Med, High tiers.")

    print("\n[Step 2/5] Simulating Fast-Loop Limbic ODE Trajectories at Exposure T=12...")
    t0 = time.time()
    evaluator.simulate_pad_trajectories(exposure_t=PRIMARY_EXPOSURE_T)
    print(f"  Trajectory simulation completed in {time.time() - t0:.2f}s (CPU-only).")

    print("\n[Step 3/5] Partitioning Matched-Magnitude Pairs (|Delta S| <= 0.02)...")
    evaluator.partition_matched_pairs(tolerance=SCALAR_MATCH_THRESHOLD)
    print(f"  Total matched pairs: {len(evaluator.exhaustive_matched_pairs)}")
    print(f"  Discordant matched pairs: {len(evaluator.discordant_matched_pairs)} (Expected 358)")
    print(f"  Same-direction matched pairs: {len(evaluator.same_direction_matched_pairs)} (Expected 6376)")

    # Define Regimes to Evaluate
    consumers: Dict[str, BaseConsumer] = {
        "A_REFERENCE": ReferenceConsumerA(),
        "B_DIRECTIONAL_SEPARABLE": DirectionalSeparableConsumerB(),
        "C_baseline": ContinuousUtilityConsumerC(gamma_C=1.00),
        "C_qual_1.50": ContinuousUtilityConsumerC(gamma_C=1.50),
        "C_qual_2.00": ContinuousUtilityConsumerC(gamma_C=2.00),
        "D_baseline": MagnitudeDominantConsumerD(mu_d=0.20, gamma_kappa=1.00),
        "D_qual_corner": MagnitudeDominantConsumerD(mu_d=1.00, gamma_kappa=0.50),
        # Diagnostic intermediate counterfactuals for Consumer D RQ2 analysis:
        "D_scalar_half": MagnitudeDominantConsumerD(mu_d=0.20, gamma_kappa=0.50),
        "D_dir_5x": MagnitudeDominantConsumerD(mu_d=1.00, gamma_kappa=1.00),
    }

    print("\n[Step 4/5] Executing Cross-Seed Behavioral & Utility Evaluation (5 Seeds)...")
    regime_results: Dict[str, Any] = {}

    for regime_id, consumer in consumers.items():
        seed_runs = []
        for s in CONSUMER_SEEDS:
            res = evaluator.evaluate_consumer_on_seed(consumer, s)
            seed_runs.append(res)

        # Aggregate across seeds
        diffrate_mean = float(np.mean([r["diffrate_disc_c2"] for r in seed_runs]))
        diffrate_std = float(np.std([r["diffrate_disc_c2"] for r in seed_runs]))
        c0_pair_mean = float(np.mean([r["d_pair_action_c0"] for r in seed_runs]))
        c0_pair_std = float(np.std([r["d_pair_action_c0"] for r in seed_runs]))
        gain_mean = float(np.mean([r["directional_gain"] for r in seed_runs]))
        gain_std = float(np.std([r["directional_gain"] for r in seed_runs]))
        shift_mean = float(np.mean([r["condition_shift_c2_c4"] for r in seed_runs]))
        shift_std = float(np.std([r["condition_shift_c2_c4"] for r in seed_runs]))
        delta_v_c2_mean = float(np.mean([r["c2_mean_delta_v"] for r in seed_runs]))
        delta_v_c0_mean = float(np.mean([r["c0_mean_delta_v"] for r in seed_runs]))
        entropy_mean = float(np.mean([r["mean_entropy"] for r in seed_runs]))

        # Mean action distributions
        mean_c2_dist = [
            float(np.mean([r["c2_action_distribution"][a_idx] for r in seed_runs]))
            for a_idx in range(6)
        ]
        mean_c0_dist = [
            float(np.mean([r["c0_action_distribution"][a_idx] for r in seed_runs]))
            for a_idx in range(6)
        ]

        # Mean tier distributions
        mean_tier_dists = {}
        for tier_name in ["Low", "Med", "High"]:
            mean_tier_dists[tier_name] = [
                float(np.mean([r["tier_distributions"][tier_name][a_idx] for r in seed_runs]))
                for a_idx in range(6)
            ]

        # Tuple identity check (NC2)
        tuple_id_res = evaluator.evaluate_hard_tuple_identity(consumer)

        # Counterfactual valuation decomposition
        decomp_res = evaluator.evaluate_counterfactual_decomposition(consumer)

        regime_results[regime_id] = {
            "regime_id": regime_id,
            "consumer_id": consumer.consumer_id,
            "diffrate_disc_c2_mean": diffrate_mean,
            "diffrate_disc_c2_std": diffrate_std,
            "d_pair_action_c0_mean": c0_pair_mean,
            "d_pair_action_c0_std": c0_pair_std,
            "directional_gain_mean": gain_mean,
            "directional_gain_std": gain_std,
            "condition_shift_c2_c4_mean": shift_mean,
            "condition_shift_c2_c4_std": shift_std,
            "c2_mean_delta_v": delta_v_c2_mean,
            "c0_mean_delta_v": delta_v_c0_mean,
            "mean_entropy": entropy_mean,
            "c2_action_distribution": mean_c2_dist,
            "c0_action_distribution": mean_c0_dist,
            "tier_distributions": mean_tier_dists,
            "tuple_identity": tuple_id_res,
            "decomposition": decomp_res,
            "per_seed_runs": seed_runs,
        }
        print(f"  {regime_id:<20}: DiffRate={diffrate_mean:.4f}, DirGain={gain_mean:+.4f}, "
              f"DCF={decomp_res['mean_dcf']:.4f}, DirFlips={decomp_res['dir_flip_rate_from_scalar']:.2%}")

    print("\n[Step 5/5] Computing Primary Consumer Preservation & Comparative Compatibility...")

    # Pairwise comparisons: C_baseline vs C_qual_1.50 and C_qual_2.00
    comp_c_150 = compute_regime_comparison(regime_results["C_baseline"], regime_results["C_qual_1.50"])
    comp_c_200 = compute_regime_comparison(regime_results["C_baseline"], regime_results["C_qual_2.00"])

    # Pairwise comparison: D_baseline vs D_qual_corner
    comp_d_corner = compute_regime_comparison(regime_results["D_baseline"], regime_results["D_qual_corner"])

    # Intermediate counterfactual comparisons for D (RQ2 analysis)
    comp_d_scalar_half = compute_regime_comparison(regime_results["D_baseline"], regime_results["D_scalar_half"])
    comp_d_dir_5x = compute_regime_comparison(regime_results["D_baseline"], regime_results["D_dir_5x"])

    comparisons = {
        "C_baseline_vs_C_qual_1.50": comp_c_150,
        "C_baseline_vs_C_qual_2.00": comp_c_200,
        "D_baseline_vs_D_qual_corner": comp_d_corner,
        "D_baseline_vs_D_scalar_half": comp_d_scalar_half,
        "D_baseline_vs_D_dir_5x": comp_d_dir_5x,
    }

    # Serialization
    out_dir = REPO_ROOT / "tests" / "evaluation_phase22" / "results" / "h1_r3_consumer_plausibility"
    os.makedirs(out_dir, exist_ok=True)
    results_path = out_dir / "r3_consumer_plausibility_results.json"
    summary_csv_path = out_dir / "r3_consumer_plausibility_summary.csv"
    manifest_path = REPO_ROOT / "tests" / "evaluation_phase22" / "fixtures" / "manifest_h1_r3_consumer_plausibility.json"

    full_output = {
        "study_metadata": {
            "study_id": "PHASE_22_H1_R3_CONSUMER_PLAUSIBILITY_STUDY",
            "timestamp_utc": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
            "primary_seed": PRIMARY_SEED,
            "consumer_seeds": CONSUMER_SEEDS,
            "exposure_t": PRIMARY_EXPOSURE_T,
            "deadband_epsilon": DEADBAND_EPSILON,
            "scalar_match_threshold": SCALAR_MATCH_THRESHOLD,
            "locked_base_parameter_hashes": LOCKED_BASE_HASHES,
            "governance": {
                "architecture_gate": "STRICTLY_LOCKED",
                "adr029_status": "DRAFT / RESEARCH RECORD ONLY / NOT RATIFIED",
                "quality_gate_2": "STRICTLY_BLOCKED",
                "phase22_h1_status": "INCONCLUSIVE",
                "genesis_profile_bit_exact": True,
                "hardware_budget": "100% CPU / 0.0 MB GPU VRAM",
            },
        },
        "regime_results": regime_results,
        "pairwise_comparisons": comparisons,
    }

    with open(results_path, "w", encoding="utf-8") as f:
        json.dump(full_output, f, indent=2)
    results_sha = compute_sha256(results_path)

    # Export Summary CSV
    write_summary_csv(summary_csv_path, regime_results, comparisons)
    csv_sha = compute_sha256(summary_csv_path)

    # Manifest
    manifest_data = {
        "manifest_version": "1.0",
        "study_id": "PHASE_22_H1_R3_CONSUMER_PLAUSIBILITY_STUDY",
        "timestamp_utc": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "corpus_seed": PRIMARY_SEED,
        "corpus_n": len(evaluator.all_probes),
        "consumer_seeds": CONSUMER_SEEDS,
        "locked_base_parameter_hashes": LOCKED_BASE_HASHES,
        "evaluated_regimes": list(consumers.keys()),
        "artifacts": {
            "results_json": {
                "path": str(results_path.relative_to(REPO_ROOT)).replace("\\", "/"),
                "sha256": results_sha,
                "bytes": results_path.stat().st_size,
            },
            "summary_csv": {
                "path": str(summary_csv_path.relative_to(REPO_ROOT)).replace("\\", "/"),
                "sha256": csv_sha,
                "bytes": summary_csv_path.stat().st_size,
            },
        },
        "governance_invariants": {
            "architecture_gate": "STRICTLY_LOCKED",
            "adr029_status": "DRAFT / RESEARCH RECORD ONLY / NOT RATIFIED",
            "quality_gate_2": "STRICTLY_BLOCKED",
            "phase22_h1_status": "INCONCLUSIVE",
            "genesis_profile_bit_exact": True,
            "hardware_budget": "100% CPU / 0.0 MB GPU VRAM",
        },
    }

    with open(manifest_path, "w", encoding="utf-8") as f:
        json.dump(manifest_data, f, indent=2)

    print(f"\n[OK] Results written to: {results_path} ({results_sha[:16]}..., {results_path.stat().st_size} bytes)")
    print(f"[OK] Summary CSV written to: {summary_csv_path} ({csv_sha[:16]}...)")
    print(f"[OK] Manifest written to: {manifest_path}")
    print("Execution complete.")


def compute_regime_comparison(base_res: Dict[str, Any], qual_res: Dict[str, Any]) -> Dict[str, Any]:
    """Compute Axis B preservation metrics between baseline and qualifying regime."""
    p_base = np.array(base_res["c2_action_distribution"])
    p_qual = np.array(qual_res["c2_action_distribution"])
    tv_shift = compute_tv_distance(p_qual, p_base)
    js_shift = compute_js_divergence(p_qual, p_base)

    c0_stab_list = []
    for s_idx in range(len(base_res["per_seed_runs"])):
        base_c0_acts = base_res["per_seed_runs"][s_idx]["c0_action_choices"]
        qual_c0_acts = qual_res["per_seed_runs"][s_idx]["c0_action_choices"]
        matches = sum(1 for b, q in zip(base_c0_acts, qual_c0_acts) if b == q)
        c0_stab_list.append(matches / len(base_c0_acts))
    scalar_c0_stability = float(np.mean(c0_stab_list))

    entropy_shift = float(qual_res["mean_entropy"] - base_res["mean_entropy"])

    rank_corrs = {}
    for tier in ["Low", "Med", "High"]:
        tier_p_base = np.array(base_res["tier_distributions"][tier])
        tier_p_qual = np.array(qual_res["tier_distributions"][tier])
        rank_corrs[tier] = spearman_rank_correlation(tier_p_qual, tier_p_base)
    mean_rank_corr = float(np.mean(list(rank_corrs.values())))

    urgency_indices = [0, 1, 5]
    base_high_urgency = sum(base_res["tier_distributions"]["High"][idx] for idx in urgency_indices)
    qual_high_urgency = sum(qual_res["tier_distributions"]["High"][idx] for idx in urgency_indices)
    urgency_shift = float(qual_high_urgency - base_high_urgency)

    return {
        "baseline_regime": base_res["regime_id"],
        "qualifying_regime": qual_res["regime_id"],
        "action_distribution_tv_shift": tv_shift,
        "action_distribution_js_shift": js_shift,
        "scalar_c0_action_stability": scalar_c0_stability,
        "entropy_shift": entropy_shift,
        "scalar_tier_rank_correlations": rank_corrs,
        "mean_scalar_tier_rank_corr": mean_rank_corr,
        "baseline_high_tier_urgency_freq": float(base_high_urgency),
        "qualifying_high_tier_urgency_freq": float(qual_high_urgency),
        "urgency_frequency_shift": urgency_shift,
        "diffrate_gain_above_baseline": float(qual_res["diffrate_disc_c2_mean"] - base_res["diffrate_disc_c2_mean"]),
        "decomp_dcf_qualifying": qual_res["decomposition"]["mean_dcf"],
        "decomp_dir_flip_rate_qualifying": qual_res["decomposition"]["dir_flip_rate_from_scalar"],
    }


def write_summary_csv(
    csv_path: Path,
    regime_results: Dict[str, Any],
    comparisons: Dict[str, Any],
) -> None:
    headers = [
        "regime_id",
        "diffrate_disc_c2",
        "directional_gain",
        "condition_shift_c2_c4",
        "mean_entropy",
        "norm_scalar_contrib",
        "norm_dir_contrib",
        "relative_ratio",
        "dcf",
        "dir_flip_rate",
        "c0_pair_diff",
    ]
    with open(csv_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(headers)
        for r_id, r in regime_results.items():
            d = r["decomposition"]
            writer.writerow([
                r_id,
                f"{r['diffrate_disc_c2_mean']:.4f}",
                f"{r['directional_gain_mean']:+.4f}",
                f"{r['condition_shift_c2_c4_mean']:.4f}",
                f"{r['mean_entropy']:.4f}",
                f"{d['mean_norm_scalar']:.4f}",
                f"{d['mean_norm_dir']:.4f}",
                f"{d['mean_relative_ratio']:.4f}",
                f"{d['mean_dcf']:.4f}",
                f"{d['dir_flip_rate_from_scalar']:.4f}",
                f"{r['d_pair_action_c0_mean']:.4f}",
            ])


if __name__ == "__main__":
    run_consumer_plausibility_study()
