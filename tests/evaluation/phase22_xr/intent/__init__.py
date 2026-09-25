"""
Intent Interpretation Module:
1. ProspectiveIntentPredictor (P22-X failure baseline: predicting intent prior to user utterance).
2. PostObservationIntentInterpreter (P22-XR: interpreting intent conditioned on utterance + latent state).
"""
from typing import Dict, List, Tuple
import numpy as np
from ..schemas import IntentPredictionResult, ContinuousBeliefState
from ..config import INTENT_CLASSES, NUM_INTENTS, INTENT_TO_IDX

class ProspectiveIntentPredictor:
    """
    P22-X formulation: Predicting fine-grained intent *prior* to user utterance.
    Achieved only 34.15% accuracy in P22-X (near static prior of 32.15%).
    """
    def __init__(self):
        # Prior distribution over intents
        self.intent_prior = np.array([0.35, 0.15, 0.15, 0.05, 0.15, 0.05, 0.05, 0.05])

    def predict(self, z_pred: np.ndarray) -> IntentPredictionResult:
        # Modest adjustment from predicted state
        logits = np.log(self.intent_prior + 1e-12) + 0.3 * z_pred[1]
        exp_l = np.exp(logits - np.max(logits))
        probs = exp_l / np.sum(exp_l)
        
        top2 = np.argsort(probs)[::-1][:2].tolist()
        best_idx = int(top2[0])
        return IntentPredictionResult(
            predicted_intent=INTENT_CLASSES[best_idx],
            predicted_intent_idx=best_idx,
            top2_indices=top2,
            probabilities=probs,
            mode="prospective"
        )


class PostObservationIntentInterpreter:
    """
    P22-XR formulation: Post-observation semantic interpretation conditioned on
    both the observed utterance/features and continuous user belief:
    P(intent_t | u_t, z_user(t)) proportional to P(u_t | intent_t) * P(intent_t | z_user(t)).
    """
    def __init__(self):
        pass

    def interpret(self, utterance: str, acoustic_features: np.ndarray, belief: ContinuousBeliefState) -> IntentPredictionResult:
        z = belief.z_mean
        u_lower = utterance.lower()
        
        # 1. Prior from continuous state P(intent | z)
        prior_logits = np.zeros(NUM_INTENTS)
        prior_logits[0] = 0.5 + 1.2 * z[1]                    # Query
        prior_logits[1] = 0.3 + 1.0 * z[4]                    # Clarification
        prior_logits[2] = 0.4 + 1.2 * z[5] + 0.5 * z[2]       # Affirmation
        prior_logits[3] = 0.1 - 2.0 * z[5]                    # Correction
        prior_logits[4] = 0.6 + 1.0 * z[1]                    # Elaboration
        prior_logits[5] = 0.2 + 1.5 * z[3]                    # TopicShift
        prior_logits[6] = 0.1 + 1.5 * z[0] - 1.0 * z[4]       # Disengagement
        prior_logits[7] = 0.3 + 1.2 * z[2]                    # Feedback

        # 2. Utterance observation likelihood P(u | intent)
        obs_logits = np.zeros(NUM_INTENTS)
        if any(w in u_lower for w in ["what", "how", "why", "which", "could", "is", "?"]):
            obs_logits[0] += 2.5
        if any(w in u_lower for w in ["elaborate", "slow down", "mean", "repeat"]):
            obs_logits[1] += 2.8
        if any(w in u_lower for w in ["yes", "exactly", "thanks", "great", "solved"]):
            obs_logits[2] += 3.2
        if any(w in u_lower for w in ["no", "not", "wrong", "makes no sense", "missing"]):
            obs_logits[3] += 3.5
        if any(w in u_lower for w in ["focus", "optimizing", "specifically", "algorithm"]):
            obs_logits[4] += 2.4
        if any(w in u_lower for w in ["quick", "urgent", "deadline", "production"]):
            obs_logits[5] += 2.6
        if any(w in u_lower for w in ["bye", "done", "leave", "tired", "fried"]):
            obs_logits[6] += 2.8
        if any(w in u_lower for w in ["appreciate", "helpful", "good explanation"]):
            obs_logits[7] += 2.5
            
        # Acoustic modulation
        obs_logits[0] += acoustic_features[4] * 1.5 # question flag
        
        # Posterior synthesis
        total_logits = prior_logits + obs_logits
        exp_l = np.exp(total_logits - np.max(total_logits))
        probs = exp_l / np.sum(exp_l)
        
        top2 = np.argsort(probs)[::-1][:2].tolist()
        best_idx = int(top2[0])
        return IntentPredictionResult(
            predicted_intent=INTENT_CLASSES[best_idx],
            predicted_intent_idx=best_idx,
            top2_indices=top2,
            probabilities=probs,
            mode="post_observation"
        )
