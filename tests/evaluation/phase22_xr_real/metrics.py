"""Metrics, evaluation statistics, and gate calculators for Phase 22-XR-L."""

from typing import Any, Dict, List, Tuple
import numpy as np


def compute_r2(y_true: np.ndarray, y_pred: np.ndarray) -> Tuple[float, np.ndarray]:
    """Compute overall R^2 and per-dimension R^2."""
    # y_true, y_pred: (N, D)
    ss_res = np.sum((y_true - y_pred) ** 2, axis=0)
    ss_tot = np.sum((y_true - np.mean(y_true, axis=0, keepdims=True)) ** 2, axis=0)
    
    # Avoid zero division
    r2_per_dim = np.where(ss_tot > 1e-12, 1.0 - (ss_res / ss_tot), 0.0)
    
    total_ss_res = np.sum((y_true - y_pred) ** 2)
    total_ss_tot = np.sum((y_true - np.mean(y_true, axis=0, keepdims=True)) ** 2)
    r2_aggregate = float(1.0 - (total_ss_res / total_ss_tot)) if total_ss_tot > 1e-12 else 0.0
    
    return r2_aggregate, r2_per_dim


def compute_mse_mae(y_true: np.ndarray, y_pred: np.ndarray) -> Tuple[float, float]:
    """Compute MSE and MAE."""
    mse = float(np.mean((y_true - y_pred) ** 2))
    mae = float(np.mean(np.abs(y_true - y_pred)))
    return mse, mae


def compute_ece(probs: np.ndarray, true_classes: np.ndarray, num_bins: int = 10) -> float:
    """Compute Expected Calibration Error (ECE) for multi-class classification."""
    confidences = np.max(probs, axis=1)
    predictions = np.argmax(probs, axis=1)
    accuracies = (predictions == true_classes).astype(float)

    bin_boundaries = np.linspace(0, 1, num_bins + 1)
    ece = 0.0
    n = len(confidences)

    for i in range(num_bins):
        bin_lower = bin_boundaries[i]
        bin_upper = bin_boundaries[i + 1]

        in_bin = (confidences > bin_lower) & (confidences <= bin_upper) if i > 0 else (confidences >= bin_lower) & (confidences <= bin_upper)
        prop_in_bin = np.sum(in_bin) / float(n)

        if prop_in_bin > 0:
            accuracy_in_bin = np.mean(accuracies[in_bin])
            avg_confidence_in_bin = np.mean(confidences[in_bin])
            ece += np.abs(avg_confidence_in_bin - accuracy_in_bin) * prop_in_bin

    return float(ece)


def compute_brier_score(probs: np.ndarray, true_classes: np.ndarray, num_classes: int = 6) -> float:
    """Compute multi-class Brier score."""
    n = len(true_classes)
    one_hot = np.zeros((n, num_classes))
    one_hot[np.arange(n), true_classes] = 1.0
    brier = float(np.mean(np.sum((probs - one_hot) ** 2, axis=1)))
    return brier


def compute_nll(probs: np.ndarray, true_classes: np.ndarray, eps: float = 1e-12) -> float:
    """Compute Negative Log-Likelihood (cross-entropy loss)."""
    n = len(true_classes)
    clipped_probs = np.clip(probs, eps, 1.0)
    true_class_probs = clipped_probs[np.arange(n), true_classes]
    return float(-np.mean(np.log(true_class_probs)))


def compute_flapping(actions: List[str]) -> float:
    """Compute flapping rate: proportion of consecutive 2-turn oscillations (A -> B -> A)."""
    if len(actions) < 3:
        return 0.0
    flaps = 0
    total = len(actions) - 2
    for i in range(total):
        if actions[i] == actions[i + 2] and actions[i] != actions[i + 1]:
            flaps += 1
    return float(flaps / total)
