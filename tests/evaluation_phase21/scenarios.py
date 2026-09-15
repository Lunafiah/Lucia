"""
tests/evaluation_phase21/scenarios.py

Synthetic interaction scenarios and counterfactual generator for Phase 21.
Enforces the 'failure is informative' protocol: scenarios are naturalistic and neutral,
never artificially tuned to force hypothesis confirmation.
"""

from __future__ import annotations

from typing import List, Tuple

import numpy as np

from tests.evaluation_phase21.models import ConsolidationExperience


class ScenarioGenerator:
    """Generates standardized interaction histories and counterfactual controls."""

    def __init__(self, seed: int = 100, stimulus_dim: int = 16, hidden_dim: int = 32) -> None:
        self.rng = np.random.default_rng(seed)
        self.stimulus_dim = stimulus_dim
        self.hidden_dim = hidden_dim

    def generate_depleted_homeostatic_initial_state(self) -> Tuple[float, float, float]:
        """
        Realistic post-turn depleted state: E0 in [0.25, 0.40], T0 in [0.40, 0.70], C0 in [0.30, 0.60].
        """
        e0 = float(self.rng.uniform(0.25, 0.35))
        t0 = float(self.rng.uniform(0.45, 0.65))
        c0 = float(self.rng.uniform(0.35, 0.55))
        return e0, t0, c0

    def generate_standard_probes(self, n_probes: int = 10) -> List[Tuple[np.ndarray, np.ndarray]]:
        """Standard sensorimotor probe stimuli to measure baseline dynamic retention."""
        probes = []
        for i in range(n_probes):
            stim = self.rng.normal(0.0, 0.3, size=self.stimulus_dim).astype(np.float64)
            stim[0] = self.rng.uniform(-0.8, 0.8)  # valence
            stim[1] = self.rng.uniform(0.1, 0.9)   # arousal
            h_target = np.tanh(stim[:self.hidden_dim] if len(stim) >= self.hidden_dim else np.pad(stim, (0, self.hidden_dim - len(stim))))
            probes.append((stim, h_target))
        return probes

    def generate_authentic_relational_session(
        self,
        n_turns: int = 16,
    ) -> List[Tuple[np.ndarray, np.ndarray, float]]:
        """
        Generate structured conversational interaction turns with causal temporal coherence.
        Returns: list of (stimulus, relational_signal, salience)
        """
        session = []
        # Phase 1: Warming up (Turns 0-5): gradual trust increase
        for _ in range(5):
            stim = self.rng.normal(0.0, 0.2, size=self.stimulus_dim).astype(np.float64)
            stim[0] = float(self.rng.uniform(0.2, 0.5))  # positive valence
            stim[1] = float(self.rng.uniform(0.2, 0.4))  # moderate arousal
            sig = np.array([0.4, 0.5, 0.3, 0.4], dtype=np.float64)
            salience = float(self.rng.uniform(0.40, 0.65))
            session.append((stim, sig, salience))

        # Phase 2: Vulnerability / Conflict (Turns 5-10): high tension & emotional salience
        for _ in range(5):
            stim = self.rng.normal(0.0, 0.3, size=self.stimulus_dim).astype(np.float64)
            stim[0] = float(self.rng.uniform(-0.6, -0.2))  # distress
            stim[1] = float(self.rng.uniform(0.6, 0.8))   # high arousal
            sig = np.array([0.2, -0.3, 0.5, 0.2], dtype=np.float64)
            salience = float(self.rng.uniform(0.70, 0.90))
            session.append((stim, sig, salience))

        # Phase 3: Repair & Attunement (Turns 10-16): deep reciprocity & calming
        for _ in range(6):
            stim = self.rng.normal(0.0, 0.2, size=self.stimulus_dim).astype(np.float64)
            stim[0] = float(self.rng.uniform(0.4, 0.7))   # relief & warmth
            stim[1] = float(self.rng.uniform(0.1, 0.3))   # calm
            sig = np.array([0.6, 0.8, 0.7, 0.9], dtype=np.float64)
            salience = float(self.rng.uniform(0.65, 0.85))
            session.append((stim, sig, salience))

        return session[:n_turns]

    def create_counterfactual_controls(
        self,
        authentic_experiences: List[ConsolidationExperience],
    ) -> Tuple[List[ConsolidationExperience], List[ConsolidationExperience], List[ConsolidationExperience]]:
        """
        Construct 3 controlled counterfactual sets under identical sample size:
          1. Shuffled: Identical experiences with permuted temporal ordering (primary control)
          2. Random: Gaussian noise vectors with matched L2 norm
          3. Orthogonal: Rotated / orthogonalized feature vectors
        """
        n = len(authentic_experiences)
        if n == 0:
            return [], [], []

        # 1. Shuffled control: permute sequence order
        shuffled_indices = self.rng.permutation(n)
        shuffled = []
        for i, idx in enumerate(shuffled_indices):
            orig = authentic_experiences[idx]
            shuffled.append(ConsolidationExperience(
                stimulus=orig.stimulus.copy(),
                h_before=orig.h_before.copy(),
                h_after=orig.h_after.copy(),
                s_slow=orig.s_slow.copy(),
                relational_state=orig.relational_state.copy(),
                r_slow_recollection=orig.r_slow_recollection.copy(),
                salience=orig.salience,
                sequence_id=i,
            ))

        # 2. Random control: matched-norm Gaussian noise
        random_ctrl = []
        for i, orig in enumerate(authentic_experiences):
            norm_stim = np.linalg.norm(orig.stimulus)
            rand_stim = self.rng.normal(0.0, 1.0, size=len(orig.stimulus))
            rand_stim = (rand_stim / (np.linalg.norm(rand_stim) + 1e-12)) * norm_stim

            norm_hb = np.linalg.norm(orig.h_before)
            rand_hb = self.rng.normal(0.0, 1.0, size=len(orig.h_before))
            rand_hb = (rand_hb / (np.linalg.norm(rand_hb) + 1e-12)) * norm_hb

            norm_ha = np.linalg.norm(orig.h_after)
            rand_ha = self.rng.normal(0.0, 1.0, size=len(orig.h_after))
            rand_ha = (rand_ha / (np.linalg.norm(rand_ha) + 1e-12)) * norm_ha

            random_ctrl.append(ConsolidationExperience(
                stimulus=rand_stim,
                h_before=rand_hb,
                h_after=rand_ha,
                s_slow=orig.s_slow.copy(),
                relational_state=orig.relational_state.copy(),
                r_slow_recollection=orig.r_slow_recollection.copy(),
                salience=orig.salience,
                sequence_id=i,
            ))

        # 3. Orthogonal control: negate or orthogonalize key stimulus axes
        orthogonal_ctrl = []
        for i, orig in enumerate(authentic_experiences):
            ortho_stim = orig.stimulus.copy()
            ortho_stim[0] = -ortho_stim[0]  # invert valence
            ortho_stim[1] = 1.0 - ortho_stim[1]  # invert arousal
            orthogonal_ctrl.append(ConsolidationExperience(
                stimulus=ortho_stim,
                h_before=orig.h_before.copy(),
                h_after=orig.h_after.copy(),
                s_slow=orig.s_slow.copy(),
                relational_state=orig.relational_state.copy(),
                r_slow_recollection=orig.r_slow_recollection.copy(),
                salience=orig.salience,
                sequence_id=i,
            ))

        return shuffled, random_ctrl, orthogonal_ctrl
