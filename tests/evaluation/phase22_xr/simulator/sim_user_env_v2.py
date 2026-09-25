"""
SimUserEnv-v2: Isolated Synthetic User Simulation Environment for Phase 22-XR.
Maintains continuous ground-truth latent state z*(t) in R^6 evolving via
Ornstein-Uhlenbeck drift with topic momentum and continuous Brownian noise.
"""
from typing import Dict, List, Tuple, Optional
import numpy as np
from ..config import (
    STATE_DIM,
    STATE_DIM_NAMES,
    INTENT_CLASSES,
    NUM_INTENTS,
    INTENT_TO_IDX,
    REGIME_CANONICAL,
    REGIME_NOISE_SURGE,
    REGIME_TOPIC_SHIFT,
    REGIME_CONTRADICTION,
    REGIME_LEXICAL_SPARSITY,
    REGIME_INTENT_SHIFT,
)
from ..schemas import SimUserStep

# Baseline attractor z_0* in R^6
Z0_DEFAULT = np.array([0.0, 0.2, 0.2, 0.1, 0.5, 0.3], dtype=np.float64)

# Relaxation rates Gamma*
GAMMA_DEFAULT = np.array([0.15, 0.10, 0.20, 0.25, 0.10, 0.15], dtype=np.float64)

# Utterance templates keyed by dominant state
UTTERANCE_BANK = {
    "high_load": [
        "I'm feeling really overwhelmed right now, could we keep this brief?",
        "There's too much going on, my brain is fried.",
        "Wait, slow down, this is too complicated.",
    ],
    "high_agency": [
        "Let's focus directly on optimizing the memory retrieval pipeline.",
        "Here is the exact issue: the cache isn't invalidating properly.",
        "What specific algorithm are you using for the spatial indexing?",
    ],
    "negative_valence": [
        "That's not helpful at all, you're missing the point.",
        "I'm frustrated that we have to keep re-doing this.",
        "No, this explanation makes no sense.",
    ],
    "positive_valence": [
        "That makes total sense, wonderful explanation!",
        "Thanks Lucia, I really appreciate your patience.",
        "Yes! That solved it completely.",
    ],
    "high_urgency": [
        "Quick, I need the answer right this second!",
        "Urgent: production is throwing 500 errors!",
        "Hurry, deadline is in 5 minutes.",
    ],
    "sparse": [
        "Wait",
        "Huh?",
        "No",
        "...",
        "Why?",
    ],
    "neutral": [
        "Okay, let me review what you just said.",
        "Understood. What is the next step?",
        "Can you elaborate on that point?",
    ]
}

class SimUserEnvV2:
    """
    Simulation Environment for Phase 22-XR testing.
    Provides verifiable, deterministic ground truth latent states in R^6.
    """
    def __init__(
        self,
        seed: int = 42,
        regime: str = REGIME_CANONICAL,
        episode_id: int = 0,
        dt: float = 1.0,
    ):
        self.rng = np.random.RandomState(seed)
        self.regime = regime
        self.episode_id = episode_id
        self.dt = dt
        
        self.z0 = Z0_DEFAULT.copy()
        self.gamma = GAMMA_DEFAULT.copy()
        self.q_noise = 0.05 * np.ones(STATE_DIM, dtype=np.float64)
        
        # Apply regime adjustments
        if self.regime == REGIME_NOISE_SURGE:
            self.q_noise *= 5.0
        elif self.regime == REGIME_TOPIC_SHIFT:
            self.z0[3] += 0.5  # Surge urgency
            self.z0[0] += 0.4  # Surge load

        self.z_true: np.ndarray = self.z0.copy() + self.rng.normal(0, 0.1, size=STATE_DIM)
        self.z_true = np.clip(self.z_true, -1.0, 1.0)
        self.turn: int = 0

    def reset(self, initial_z: Optional[np.ndarray] = None) -> SimUserStep:
        self.turn = 0
        if initial_z is not None:
            self.z_true = np.clip(initial_z.copy(), -1.0, 1.0)
        else:
            self.z_true = self.z0.copy() + self.rng.normal(0, 0.1, size=STATE_DIM)
            self.z_true = np.clip(self.z_true, -1.0, 1.0)
        return self._emit_step()

    def step(self) -> SimUserStep:
        self.turn += 1
        
        # Contradiction Shock at turn 15
        if self.regime == REGIME_CONTRADICTION and self.turn == 15:
            # Reversal: invert alignment and valence
            self.z_true[2] = -self.z_true[2]
            self.z_true[5] = -self.z_true[5]

        # Continuous OU Drift: dz = -Gamma(z - z0)*dt + sigma*dW
        drift = -self.gamma * (self.z_true - self.z0) * self.dt
        diffusion = self.rng.normal(0, self.q_noise) * np.sqrt(self.dt)
        self.z_true = self.z_true + drift + diffusion
        
        # Clip to mathematical bounds
        self.z_true[0:3] = np.clip(self.z_true[0:3], -1.0, 1.0)   # load, agency, valence
        self.z_true[3:5] = np.clip(self.z_true[3:5],  0.0, 1.0)   # urgency, receptive
        self.z_true[5]   = np.clip(self.z_true[5],   -1.0, 1.0)   # alignment
        
        return self._emit_step()

    def _emit_step(self) -> SimUserStep:
        # Determine intent conditioned on true state
        intent, intent_idx = self._sample_intent(self.z_true)
        
        # Generate utterance text
        utterance = self._generate_utterance(self.z_true, intent)
        
        # Generate acoustic/timing observation features in R^6
        # [lexical_density, duration_norm, latency_norm, sentiment_val, question_flag, interruption_flag]
        acoustic_features = self._generate_acoustics(self.z_true, intent)
        
        return SimUserStep(
            turn=self.turn,
            true_latent_state=self.z_true.copy(),
            utterance=utterance,
            acoustic_features=acoustic_features,
            true_intent=intent,
            true_intent_idx=intent_idx,
            ds_regime=self.regime,
            episode_id=self.episode_id,
            metadata={"z0": self.z0.tolist(), "turn": self.turn}
        )

    def _sample_intent(self, z: np.ndarray) -> Tuple[str, int]:
        # Unnormalized intent logits conditioned on z
        logits = np.zeros(NUM_INTENTS, dtype=np.float64)
        logits[0] = 1.0 + 1.5 * z[1]                    # Query boosted by agency
        logits[1] = 0.5 + 1.2 * z[4]                    # Clarification boosted by receptivity
        logits[2] = 0.5 + 1.0 * z[5] + 0.5 * z[2]       # Affirmation boosted by alignment & valence
        logits[3] = 0.2 - 2.0 * z[5]                    # Correction boosted by negative alignment
        logits[4] = 0.8 + 1.0 * z[1]                    # Elaboration boosted by agency
        logits[5] = 0.3 + 1.2 * z[3]                    # TopicShift boosted by urgency
        logits[6] = 0.1 + 1.5 * z[0] - 1.0 * z[4]       # Disengagement boosted by load, lowered by receptivity
        logits[7] = 0.4 + 1.0 * z[2]                    # Feedback boosted by valence
        
        if self.regime == REGIME_INTENT_SHIFT:
            logits = np.roll(logits, shift=2)

        exp_l = np.exp(logits - np.max(logits))
        probs = exp_l / np.sum(exp_l)
        idx = self.rng.choice(NUM_INTENTS, p=probs)
        return INTENT_CLASSES[idx], idx

    def _generate_utterance(self, z: np.ndarray, intent: str) -> str:
        if self.regime == REGIME_LEXICAL_SPARSITY and self.rng.rand() < 0.7:
            bank = UTTERANCE_BANK["sparse"]
        elif z[0] > 0.4:
            bank = UTTERANCE_BANK["high_load"]
        elif z[3] > 0.6:
            bank = UTTERANCE_BANK["high_urgency"]
        elif z[2] < -0.3:
            bank = UTTERANCE_BANK["negative_valence"]
        elif z[2] > 0.5:
            bank = UTTERANCE_BANK["positive_valence"]
        elif z[1] > 0.3:
            bank = UTTERANCE_BANK["high_agency"]
        else:
            bank = UTTERANCE_BANK["neutral"]
            
        return self.rng.choice(bank)

    def _generate_acoustics(self, z: np.ndarray, intent: str) -> np.ndarray:
        # Features: [lexical_density, duration_norm, latency_norm, sentiment_val, question_flag, silence_flag]
        base = np.array([
            0.5 - 0.3 * z[0] + 0.2 * z[1],               # lexical density
            0.5 + 0.2 * z[1] - 0.2 * z[3],               # duration norm
            0.5 - 0.4 * z[3] + 0.3 * z[0],               # latency norm
            z[2],                                        # sentiment val
            1.0 if intent in ["Query", "Clarification"] else 0.0,
            1.0 if z[0] > 0.6 and self.rng.rand() < 0.5 else 0.0,
        ], dtype=np.float64)
        
        noise_scale = 0.35 if self.regime == REGIME_NOISE_SURGE else 0.05
        noise = self.rng.normal(0, noise_scale, size=6)
        return np.clip(base + noise, -1.0, 1.0)
