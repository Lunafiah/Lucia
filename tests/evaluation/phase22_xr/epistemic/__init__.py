"""
Epistemic Action Selection (EIG Policy).
Selects conversational actions (e.g., answer, elaborate, clarify, probe, reflect)
balancing expected information gain against pragmatic conversational utility.
"""
from typing import Dict, List, Tuple
import numpy as np
from ..schemas import ContinuousBeliefState

ACTIONS: List[str] = [
    "answer",
    "elaborate",
    "clarify",
    "probe",
    "reflect",
]

class EpistemicActionPolicy:
    """
    Continuous EIG Policy.
    Clarification actions are triggered only when uncertainty exceeds ambiguity threshold tau_amb.
    """
    def __init__(
        self,
        tau_amb: float = 0.12,
        alpha_eig: float = 0.35,
    ):
        self.tau_amb = tau_amb
        self.alpha_eig = alpha_eig

    def select_action(self, belief: ContinuousBeliefState) -> Tuple[str, float, float]:
        """
        Returns:
            (selected_action, expected_info_gain, current_uncertainty)
        """
        # Current belief uncertainty: differential entropy proxy H ~ 0.5 * ln|P| or trace(P)
        trace_p = float(np.trace(belief.covariance))
        current_uncertainty = trace_p / 6.0
        
        # If uncertainty is low, default to pragmatic action (answer / elaborate)
        if current_uncertainty < self.tau_amb:
            eig = 0.0
            act = "elaborate" if belief.z_mean[1] > 0.3 else "answer"
            return act, eig, current_uncertainty
            
        # Ambiguity detected: compute EIG for epistemic queries
        # Clarify targets alignment & load
        # Probe targets agency & urgency
        # Reflect targets valence
        eig_clarify = 0.45 * (belief.covariance[0, 0] + belief.covariance[5, 5])
        eig_probe   = 0.40 * (belief.covariance[1, 1] + belief.covariance[3, 3])
        eig_reflect = 0.35 * (belief.covariance[2, 2] + belief.covariance[4, 4])
        
        options = [
            ("clarify", eig_clarify),
            ("probe", eig_probe),
            ("reflect", eig_reflect),
        ]
        options.sort(key=lambda x: x[1], reverse=True)
        best_act, best_eig = options[0]
        return best_act, float(best_eig), current_uncertainty
