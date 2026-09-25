"""
SimUserEnv-v1: Synthetic Evaluation Environment for Phase 22-X.
Deterministic, isolated, CPU-only generator with known ground truth.
"""
from typing import Dict, List, Tuple, Optional
import numpy as np

LATENT_STATES: List[str] = [
    "FOCUSED_TASK",
    "EXPLORATORY",
    "COGNITIVE_OVERLOAD",
    "AFFECTIVE_SHARING",
    "AMBIGUOUS_PASSIVE",
]
NUM_STATES = len(LATENT_STATES)
STATE_TO_IDX = {s: i for i, s in enumerate(LATENT_STATES)}
IDX_TO_STATE = {i: s for i, s in enumerate(LATENT_STATES)}

INTENT_CLASSES: List[str] = [
    "Query",
    "Clarification",
    "Affirmation",
    "Correction",
    "Elaboration",
    "TopicShift",
    "Disengagement",
    "Feedback",
]
NUM_INTENTS = len(INTENT_CLASSES)
INTENT_TO_IDX = {intent: i for i, intent in enumerate(INTENT_CLASSES)}
IDX_TO_INTENT = {i: intent for i, intent in enumerate(INTENT_CLASSES)}

# Canonical Ground-Truth Transition Matrix T* (shape: [5, 5])
# T[j, k] = P(s_{t+1} = k | s_t = j)
GROUND_TRUTH_TRANSITION: np.ndarray = np.array([
    [0.75, 0.10, 0.05, 0.05, 0.05],  # from FOCUSED_TASK
    [0.15, 0.70, 0.05, 0.05, 0.05],  # from EXPLORATORY
    [0.10, 0.05, 0.70, 0.05, 0.10],  # from COGNITIVE_OVERLOAD
    [0.05, 0.10, 0.05, 0.75, 0.05],  # from AFFECTIVE_SHARING
    [0.20, 0.20, 0.20, 0.10, 0.30],  # from AMBIGUOUS_PASSIVE
], dtype=np.float64)

# Intent Emission Matrix E* (shape: [5, 8])
# E[k, m] = P(intent = m | state = k)
GROUND_TRUTH_INTENT_EMISSION: np.ndarray = np.array([
    # Query, Clar, Affirm, Corr, Elab, Shift, Diseng, Feedb
    [0.60, 0.05, 0.15, 0.05, 0.10, 0.02, 0.01, 0.02],  # FOCUSED_TASK
    [0.35, 0.10, 0.10, 0.05, 0.25, 0.10, 0.02, 0.03],  # EXPLORATORY
    [0.10, 0.30, 0.05, 0.25, 0.05, 0.05, 0.15, 0.05],  # COGNITIVE_OVERLOAD
    [0.10, 0.05, 0.25, 0.02, 0.35, 0.05, 0.03, 0.15],  # AFFECTIVE_SHARING
    [0.20, 0.30, 0.10, 0.05, 0.05, 0.15, 0.10, 0.05],  # AMBIGUOUS_PASSIVE
], dtype=np.float64)

# Feature Means per State in R^6
# Features: [lexical_density, duration_norm, latency_norm, sentiment_val, question_flag, silence_flag]
STATE_FEATURE_MEANS: np.ndarray = np.array([
    [0.85, 0.60, 0.20,  0.10, 0.80, 0.05],  # FOCUSED_TASK
    [0.55, 0.75, 0.40,  0.40, 0.60, 0.10],  # EXPLORATORY
    [0.25, 0.20, 0.85, -0.60, 0.30, 0.50],  # COGNITIVE_OVERLOAD
    [0.70, 0.85, 0.30,  0.75, 0.40, 0.05],  # AFFECTIVE_SHARING
    [0.30, 0.25, 0.65, -0.10, 0.50, 0.40],  # AMBIGUOUS_PASSIVE
], dtype=np.float64)

STATE_FEATURE_STDS: np.ndarray = np.array([
    [0.10, 0.15, 0.10, 0.15, 0.10, 0.05],
    [0.15, 0.15, 0.15, 0.20, 0.15, 0.10],
    [0.12, 0.10, 0.12, 0.20, 0.15, 0.15],
    [0.12, 0.15, 0.10, 0.15, 0.15, 0.05],
    [0.20, 0.20, 0.20, 0.25, 0.20, 0.20],
], dtype=np.float64)


class SimUserEnv:
    """
    Synthetic User Environment generating controllable, reproducible dialogue streams.
    Provides verifiable ground truth for latent states, transitions, emissions, and intents.
    """
    def __init__(self, seed: int = 42, noise_level: float = 0.10, ds_regime: Optional[str] = None):
        self.rng = np.random.RandomState(seed)
        self.noise_level = noise_level
        self.ds_regime = ds_regime
        
        # Setup transition matrix (apply DS-2 if specified)
        self.transition_matrix = GROUND_TRUTH_TRANSITION.copy()
        if self.ds_regime == "DS-2":
            # Transition dynamics shift: blend with uniform matrix
            uniform_t = np.ones((NUM_STATES, NUM_STATES)) / NUM_STATES
            self.transition_matrix = 0.6 * self.transition_matrix + 0.4 * uniform_t
            
        self.intent_matrix = GROUND_TRUTH_INTENT_EMISSION.copy()
        if self.ds_regime == "DS-5":
            # Unseen intent co-occurrence / shift
            self.intent_matrix = np.roll(self.intent_matrix, shift=2, axis=1)

        self.current_state: int = self.rng.choice(NUM_STATES)
        self.turn: int = 0

    def reset(self, initial_state: Optional[int] = None) -> int:
        self.turn = 0
        if initial_state is not None:
            self.current_state = initial_state
        else:
            self.current_state = self.rng.choice(NUM_STATES)
        return self.current_state

    def step(self, agent_action: Optional[str] = None) -> Tuple[np.ndarray, int, int, Dict]:
        """
        Advance one turn in the environment.
        Returns:
            observation_features: np.ndarray (R^6)
            observed_intent: int
            current_state: int (ground truth)
            metadata: Dict
        """
        self.turn += 1
        
        # 1. State transition
        trans_probs = self.transition_matrix[self.current_state]
        
        # Epistemic action influence: if agent asks a targeted clarification, ambiguous states resolve faster
        if agent_action == "ClarifySpecific" and self.current_state == STATE_TO_IDX["AMBIGUOUS_PASSIVE"]:
            # Ambiguity resolves to FOCUSED_TASK or EXPLORATORY with 85% probability
            trans_probs = np.array([0.45, 0.40, 0.05, 0.05, 0.05])
        elif agent_action == "ClarifyOpen" and self.current_state == STATE_TO_IDX["AMBIGUOUS_PASSIVE"]:
            trans_probs = np.array([0.30, 0.40, 0.05, 0.20, 0.05])
        elif agent_action == "ClarifySpecific" and self.current_state == STATE_TO_IDX["COGNITIVE_OVERLOAD"]:
            # Redundant questioning during overload increases overload
            trans_probs = np.array([0.02, 0.02, 0.85, 0.01, 0.10])
            
        # DS-3: Contradictory evidence injection
        if self.ds_regime == "DS-3" and self.turn == 25:
            self.current_state = STATE_TO_IDX["COGNITIVE_OVERLOAD"]
        else:
            self.current_state = self.rng.choice(NUM_STATES, p=trans_probs)

        # 2. Intent emission
        intent_probs = self.intent_matrix[self.current_state]
        intent = self.rng.choice(NUM_INTENTS, p=intent_probs)

        # 3. Observation feature emission
        means = STATE_FEATURE_MEANS[self.current_state]
        stds = STATE_FEATURE_STDS[self.current_state]
        
        current_noise = self.noise_level
        if self.ds_regime == "DS-1":
            # Noise surge
            current_noise = 0.50
            
        obs = self.rng.normal(means, stds + current_noise)
        
        if self.ds_regime == "DS-4":
            # Silent / sparse interaction: drop density and set high silence/latency
            obs[0] = 0.05  # near zero lexical density
            obs[1] = 0.10  # short duration
            obs[2] = 0.95  # extreme latency
            obs[5] = 0.90  # silence flag

        metadata = {
            "turn": self.turn,
            "ground_truth_state": self.current_state,
            "ground_truth_state_name": IDX_TO_STATE[self.current_state],
            "ground_truth_intent": intent,
            "ground_truth_intent_name": IDX_TO_INTENT[intent],
            "agent_action_received": agent_action,
        }
        return obs, intent, self.current_state, metadata

    def generate_dataset(self, num_samples: int) -> Tuple[np.ndarray, np.ndarray, np.ndarray]:
        """
        Generate (X_features, y_state, y_intent) batches for training and evaluation.
        """
        X = np.zeros((num_samples, 6), dtype=np.float64)
        y_state = np.zeros(num_samples, dtype=np.int64)
        y_intent = np.zeros(num_samples, dtype=np.int64)

        for i in range(num_samples):
            obs, intent, state, _ = self.step()
            X[i] = obs
            y_state[i] = state
            y_intent[i] = intent

        return X, y_state, y_intent
