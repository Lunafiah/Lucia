"""
P23 Interface Contract Module for Phase 22-XR.
Validates the observation forcing signal: psi_user(t) = [z_user(t), diag(P_t)] in R^12.
Validates shape, boundedness, continuity, temporal consistency, and language independence.
"""
from typing import Dict, List, Tuple, Any
import numpy as np
import time

class P23InterfaceContract:
    """
    Validates interface vector psi_user(t) toward Phase 23 continuous semantic state.
    Strictly isolated from Phase 23 internal dynamics.
    """
    def __init__(self):
        self.expected_dim = 12

    def construct_forcing_vector(self, z_user: np.ndarray, P_cov: np.ndarray) -> np.ndarray:
        """Constructs psi_user(t) = [z_user, diag(P)]."""
        diag_p = np.diag(P_cov)
        psi = np.concatenate([z_user, diag_p])
        return psi

    def validate_contract(self, psi_vectors: List[np.ndarray]) -> Dict[str, Any]:
        """
        Validates mathematical properties across an episode:
        - Exactly 12 dimensions
        - Bounded Linf <= 1.5
        - Zero NaN / Inf
        - Continuity / small step displacement
        """
        arr = np.array(psi_vectors)
        dim = arr.shape[1]
        has_nan = bool(np.isnan(arr).any())
        has_inf = bool(np.isinf(arr).any())
        max_linf = float(np.max(np.abs(arr)))
        
        # Step displacements: ||psi_{t+1} - psi_t||_2
        displacements = []
        for i in range(len(arr) - 1):
            disp = float(np.linalg.norm(arr[i+1] - arr[i]))
            displacements.append(disp)
            
        max_step_disp = float(np.max(displacements)) if displacements else 0.0
        mean_step_disp = float(np.mean(displacements)) if displacements else 0.0
        
        passed = (dim == self.expected_dim) and (not has_nan) and (not has_inf) and (max_linf <= 1.5)
        return {
            "dimension": dim,
            "expected_dimension": self.expected_dim,
            "has_nan": has_nan,
            "has_inf": has_inf,
            "max_linf": max_linf,
            "bounded_linf": max_linf <= 1.5,
            "mean_step_displacement": mean_step_disp,
            "max_step_displacement": max_step_disp,
            "contract_passed": passed
        }

    def test_multilingual_invariance(self, english_psi: np.ndarray, vietnamese_psi: np.ndarray, japanese_psi: np.ndarray) -> Dict[str, Any]:
        """
        Tests whether equivalent semantic turns in different surface languages
        produce consistent interface vectors within bounded tolerance.
        """
        diff_vi = float(np.linalg.norm(english_psi - vietnamese_psi))
        diff_ja = float(np.linalg.norm(english_psi - japanese_psi))
        max_diff = max(diff_vi, diff_ja)
        return {
            "diff_en_vi": diff_vi,
            "diff_en_ja": diff_ja,
            "max_cross_lingual_diff": max_diff,
            "language_independent": max_diff <= 0.35
        }
