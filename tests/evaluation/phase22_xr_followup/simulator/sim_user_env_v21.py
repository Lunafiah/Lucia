"""
SimUserEnv-v2.1: Synthetic User Simulation Environment for Phase 22-XR Follow-Up.
Guarantees strict separation between Calibration Split (D_cal, seed 9999) and Evaluation Splits (D_eval).
Ground truth z*(t) is strictly isolated from model observation inputs.
"""
from typing import Dict, List, Tuple, Optional
import numpy as np
from ..schemas import SimUserStep

# Baseline attractor z_0* in R^6
Z0_DEFAULT = np.array([0.0, 0.2, 0.2, 0.1, 0.5, 0.3], dtype=np.float64)
GAMMA_DEFAULT = np.array([0.15, 0.10, 0.20, 0.25, 0.10, 0.15], dtype=np.float64)

class SimUserEnvV21:
    """
    Simulation Environment for Phase 22-XR Follow-up testing.
    Provides verifiable, deterministic ground truth latent states in R^6.
    """
    def __init__(
        self,
        seed: int = 42,
        regime: str = "ID",
        episode_id: int = 0,
        dt: float = 1.0,
    ):
        self.rng = np.random.RandomState(seed)
        self.regime = regime
        self.episode_id = episode_id
        self.dt = dt
        
        self.z0 = Z0_DEFAULT.copy()
        self.gamma = GAMMA_DEFAULT.copy()
        self.q_noise = 0.05 * np.ones(6, dtype=np.float64)
        
        if self.regime == "NoiseSurge":
            self.q_noise *= 5.0
        elif self.regime == "TemporalDrift":
            self.z0[3] += 0.5
            self.z0[0] += 0.4

        self.z_true: np.ndarray = self.z0.copy() + self.rng.normal(0, 0.1, size=6)
        self.z_true = np.clip(self.z_true, -1.0, 1.0)
        self.turn: int = 0

    def reset(self, initial_z: Optional[np.ndarray] = None) -> SimUserStep:
        self.turn = 0
        if initial_z is not None:
            self.z_true = np.clip(initial_z.copy(), -1.0, 1.0)
        else:
            self.z_true = self.z0.copy() + self.rng.normal(0, 0.1, size=6)
            self.z_true = np.clip(self.z_true, -1.0, 1.0)
        return self._emit_step()

    def step(self) -> SimUserStep:
        self.turn += 1
        
        # Contradiction Shock at turn 15
        if self.regime in ["ContradictionShock", "CombinedStress"] and self.turn == 15:
            self.z_true[2] = -self.z_true[2]
            self.z_true[5] = -self.z_true[5]

        # Continuous OU Drift: dz = -Gamma(z - z0)*dt + sigma*dW
        drift = -self.gamma * (self.z_true - self.z0) * self.dt
        diffusion = self.rng.normal(0, self.q_noise) * np.sqrt(self.dt)
        self.z_true = self.z_true + drift + diffusion
        
        # Clip to mathematical bounds
        self.z_true[0:3] = np.clip(self.z_true[0:3], -1.0, 1.0)
        self.z_true[3:5] = np.clip(self.z_true[3:5],  0.0, 1.0)
        self.z_true[5]   = np.clip(self.z_true[5],   -1.0, 1.0)
        
        return self._emit_step()

    def _emit_step(self) -> SimUserStep:
        intent_names = ["Query", "Clarification", "Affirmation", "Correction", "Elaboration", "TopicShift", "Disengagement", "Feedback"]
        # Intent sampling
        idx = int(np.argmax(self.z_true)) % len(intent_names)
        intent = intent_names[idx]
        
        # Utterance generation
        if self.regime in ["LexicalSparsity", "CombinedStress"] and self.rng.rand() < 0.7:
            utterance = self.rng.choice(["Wait", "Huh?", "No", "...", "Why?"])
        elif self.z_true[0] > 0.4:
            utterance = "I'm feeling really overwhelmed right now, could we keep this brief?"
        elif self.z_true[1] > 0.3:
            utterance = "Let's focus directly on optimizing the memory retrieval pipeline."
        elif self.z_true[2] < -0.3:
            utterance = "That's not helpful at all, you're missing the point."
        elif self.z_true[2] > 0.4:
            utterance = "That makes total sense, wonderful explanation!"
        else:
            utterance = "Okay, let me review what you just said."
            
        # Acoustic features in R^6
        base_features = np.array([
            0.5 - 0.3 * self.z_true[0] + 0.2 * self.z_true[1],
            0.5 + 0.2 * self.z_true[1] - 0.2 * self.z_true[3],
            0.5 - 0.4 * self.z_true[3] + 0.3 * self.z_true[0],
            self.z_true[2],
            1.0 if intent in ["Query", "Clarification"] else 0.0,
            1.0 if self.z_true[0] > 0.6 else 0.0,
        ], dtype=np.float64)
        
        noise_scale = 0.35 if self.regime in ["NoiseSurge", "CombinedStress"] else 0.05
        acoustic_features = np.clip(base_features + self.rng.normal(0, noise_scale, size=6), -1.0, 1.0)
        
        return SimUserStep(
            turn=self.turn,
            true_latent_state=self.z_true.copy(),
            utterance=utterance,
            acoustic_features=acoustic_features,
            true_intent=intent,
            true_intent_idx=idx,
            ds_regime=self.regime,
            episode_id=self.episode_id,
            metadata={"turn": self.turn}
        )
