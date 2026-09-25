"""
Metrics calculation for Phase 22-X Isolated Research Evaluation.
Calculates ECE, Brier score, NLL, Total Variation distance, and Entropy.
Strictly CPU-based.
"""
from typing import Dict, List, Tuple
import numpy as np


def compute_ece(probs: np.ndarray, labels: np.ndarray, num_bins: int = 10) -> float:
    """
    Expected Calibration Error (ECE) with equal-width confidence bins.
    """
    confidences = np.max(probs, axis=1)
    predictions = np.argmax(probs, axis=1)
    accuracies = (predictions == labels).astype(float)
    
    bin_boundaries = np.linspace(0, 1, num_bins + 1)
    ece = 0.0
    n_samples = len(labels)
    
    for i in range(num_bins):
        bin_lower = bin_boundaries[i]
        bin_upper = bin_boundaries[i + 1]
        
        in_bin = (confidences > bin_lower) & (confidences <= bin_upper)
        prop_in_bin = np.mean(in_bin)
        
        if prop_in_bin > 0:
            accuracy_in_bin = np.mean(accuracies[in_bin])
            avg_confidence_in_bin = np.mean(confidences[in_bin])
            ece += np.abs(avg_confidence_in_bin - accuracy_in_bin) * prop_in_bin
            
    return float(ece)


def compute_brier_score(probs: np.ndarray, labels: np.ndarray, num_classes: int) -> float:
    """
    Multi-class Brier Score: 1/N \sum_i \|\mathbf{p}_i - \mathbf{y}_i^*\|_2^2
    """
    one_hot = np.zeros((len(labels), num_classes), dtype=float)
    one_hot[np.arange(len(labels)), labels] = 1.0
    return float(np.mean(np.sum((probs - one_hot) ** 2, axis=1)))


def compute_nll(probs: np.ndarray, labels: np.ndarray) -> float:
    """
    Negative Log-Likelihood (cross-entropy error).
    """
    clipped = np.clip(probs, 1e-12, 1.0)
    log_probs = np.log(clipped)
    nll = -np.mean(log_probs[np.arange(len(labels)), labels])
    return float(nll)


def compute_tv_distance(p: np.ndarray, q: np.ndarray) -> float:
    """
    Total Variation Distance between two probability distributions:
    TV(p, q) = 0.5 * \sum_k |p_k - q_k|
    """
    return float(0.5 * np.sum(np.abs(p - q)))


def compute_entropy(p: np.ndarray) -> float:
    """
    Shannon Entropy in nats: H(p) = -\sum_k p_k \ln p_k
    """
    clipped = np.clip(p, 1e-12, 1.0)
    return float(-np.sum(p * np.log(clipped)))
