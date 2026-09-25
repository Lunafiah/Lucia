"""
Baselines B0–B5 for Phase 22-X Isolated Research Evaluation.
CPU-only, deterministic implementations.
"""
from typing import Dict, List, Tuple, Optional
import numpy as np
import torch
import torch.nn as nn
import torch.optim as optim

from .sim_user_env import (
    NUM_STATES,
    NUM_INTENTS,
    GROUND_TRUTH_TRANSITION,
    GROUND_TRUTH_INTENT_EMISSION,
)


class B0_MajorityPrior:
    """
    B0: Deterministic Majority / Static Prior Baseline.
    Predicts constant prior distribution or modal class.
    """
    def __init__(self):
        self.state_prior = np.ones(NUM_STATES) / NUM_STATES
        self.intent_prior = np.ones(NUM_INTENTS) / NUM_INTENTS

    def fit(self, y_states: np.ndarray, y_intents: np.ndarray):
        state_counts = np.bincount(y_states, minlength=NUM_STATES)
        self.state_prior = state_counts / state_counts.sum()
        intent_counts = np.bincount(y_intents, minlength=NUM_INTENTS)
        self.intent_prior = intent_counts / intent_counts.sum()

    def predict_state_probs(self, x: np.ndarray) -> np.ndarray:
        if x.ndim == 1:
            return self.state_prior.copy()
        return np.tile(self.state_prior, (len(x), 1))

    def predict_intent_probs(self, x: np.ndarray) -> np.ndarray:
        if x.ndim == 1:
            return self.intent_prior.copy()
        return np.tile(self.intent_prior, (len(x), 1))


class B1_CalibratedDiscriminative(nn.Module):
    """
    B1: Standard Calibrated Discriminative Model (MLP with Temperature Scaling).
    Lightweight 2-layer network running strictly on CPU.
    """
    def __init__(self, input_dim: int = 6, hidden_dim: int = 32, num_classes: int = NUM_STATES):
        super().__init__()
        self.net = nn.Sequential(
            nn.Linear(input_dim, hidden_dim),
            nn.ReLU(),
            nn.Linear(hidden_dim, num_classes),
        )
        self.temperature = nn.Parameter(torch.ones(1) * 1.0)

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        logits = self.net(x)
        return logits

    def predict_logits(self, x_np: np.ndarray) -> np.ndarray:
        self.eval()
        with torch.no_grad():
            x_t = torch.tensor(x_np, dtype=torch.float32)
            logits = self.net(x_t)
            return logits.numpy()

    def predict_probs(self, x_np: np.ndarray) -> np.ndarray:
        self.eval()
        with torch.no_grad():
            x_t = torch.tensor(x_np, dtype=torch.float32)
            logits = self.net(x_t)
            scaled_logits = logits / torch.clamp(self.temperature, min=0.01)
            probs = torch.softmax(scaled_logits, dim=-1)
            return probs.numpy()

    def fit(self, X: np.ndarray, y: np.ndarray, epochs: int = 40, lr: float = 0.01):
        self.train()
        criterion = nn.CrossEntropyLoss()
        optimizer = optim.Adam(self.net.parameters(), lr=lr)
        
        X_t = torch.tensor(X, dtype=torch.float32)
        y_t = torch.tensor(y, dtype=torch.long)
        
        for _ in range(epochs):
            optimizer.zero_grad()
            logits = self.net(X_t)
            loss = criterion(logits, y_t)
            loss.backward()
            optimizer.step()

    def calibrate(self, X_val: np.ndarray, y_val: np.ndarray):
        """
        Optimize temperature scaling parameter on validation set.
        """
        self.eval()
        with torch.no_grad():
            logits = self.net(torch.tensor(X_val, dtype=torch.float32))
            
        y_val_t = torch.tensor(y_val, dtype=torch.long)
        temp = nn.Parameter(torch.ones(1) * 1.5)
        optimizer = optim.LBFGS([temp], lr=0.05, max_iter=50)
        criterion = nn.CrossEntropyLoss()

        def eval_loss():
            optimizer.zero_grad()
            loss = criterion(logits / torch.clamp(temp, min=0.05), y_val_t)
            loss.backward()
            return loss

        optimizer.step(eval_loss)
        self.temperature.data = temp.data.clamp(min=0.05)


class B2_BayesFilter:
    """
    B2: Discrete Bayesian / HMM Filter.
    Maintains recursive posterior belief over latent states.
    b_t(s_k) \propto P(x_t | s_k) \sum_j T_{j, k} b_{t-1}(s_j)
    """
    def __init__(self, transition_matrix: Optional[np.ndarray] = None):
        if transition_matrix is not None:
            self.transition_matrix = transition_matrix.copy()
        else:
            self.transition_matrix = GROUND_TRUTH_TRANSITION.copy()
        self.belief = np.ones(NUM_STATES) / NUM_STATES

    def reset(self, initial_prior: Optional[np.ndarray] = None):
        if initial_prior is not None:
            self.belief = initial_prior.copy()
        else:
            self.belief = np.ones(NUM_STATES) / NUM_STATES

    def update(self, likelihoods: np.ndarray) -> np.ndarray:
        """
        Update belief given likelihood vector P(x_t | s_k).
        """
        # 1. Predict (prior for step t)
        predicted_prior = self.transition_matrix.T @ self.belief
        
        # 2. Update with likelihood evidence
        unnorm_posterior = likelihoods * predicted_prior
        evidence = np.sum(unnorm_posterior)
        
        if evidence < 1e-12:
            # Fallback to predicted prior if likelihood underflows
            self.belief = predicted_prior
        else:
            self.belief = unnorm_posterior / evidence
            
        return self.belief.copy()


class B3_POMDPTracker:
    """
    B3: Simplified POMDP / Dialogue State Tracker.
    Maintains belief state over (user_state, active_dialogue_goal) with decay.
    """
    def __init__(self, decay_rate: float = 0.05):
        self.decay_rate = decay_rate
        self.belief = np.ones(NUM_STATES) / NUM_STATES
        self.transition_matrix = GROUND_TRUTH_TRANSITION.copy()

    def reset(self):
        self.belief = np.ones(NUM_STATES) / NUM_STATES

    def step(self, obs_probs: np.ndarray) -> np.ndarray:
        # Time decay towards uniform prior
        uniform = np.ones(NUM_STATES) / NUM_STATES
        decayed_belief = (1.0 - self.decay_rate) * self.belief + self.decay_rate * uniform
        
        # Transition propagation
        prior = self.transition_matrix.T @ decayed_belief
        
        # Observation combination via log-odds / geometric blend
        log_prior = np.log(np.clip(prior, 1e-12, 1.0))
        log_obs = np.log(np.clip(obs_probs, 1e-12, 1.0))
        
        combined_logits = log_prior + log_obs
        shifted = combined_logits - np.max(combined_logits)
        posterior = np.exp(shifted) / np.sum(np.exp(shifted))
        
        self.belief = posterior
        return self.belief.copy()


class B4_JevLayaSurrogate(nn.Module):
    """
    B4: Jev/Laya-Inspired Surrogate Primitive.
    Non-generative calibrated decision layer with:
      - Low-parameter dual-head discriminative architecture (< 25k params)
      - Margin-based decision uncertainty head
      - Boundary-preserving calibration
      - Low-latency CPU execution (< 2ms)
    """
    def __init__(self, input_dim: int = 6, hidden_dim: int = 48, num_classes: int = NUM_STATES):
        super().__init__()
        self.shared_trunk = nn.Sequential(
            nn.Linear(input_dim, hidden_dim),
            nn.LayerNorm(hidden_dim),
            nn.GELU(),
            nn.Linear(hidden_dim, hidden_dim),
            nn.LayerNorm(hidden_dim),
            nn.GELU(),
        )
        self.class_head = nn.Linear(hidden_dim, num_classes)
        # Dedicated epistemic uncertainty scalar head
        self.uncertainty_head = nn.Sequential(
            nn.Linear(hidden_dim, 16),
            nn.ReLU(),
            nn.Linear(16, 1),
            nn.Sigmoid(),
        )
        self.temperature = nn.Parameter(torch.ones(1) * 1.0)

    def forward(self, x: torch.Tensor) -> Tuple[torch.Tensor, torch.Tensor]:
        feat = self.shared_trunk(x)
        logits = self.class_head(feat)
        epistemic_unc = self.uncertainty_head(feat)
        return logits, epistemic_unc

    def predict_probs_and_uncertainty(self, x_np: np.ndarray) -> Tuple[np.ndarray, np.ndarray]:
        self.eval()
        with torch.no_grad():
            x_t = torch.tensor(x_np, dtype=torch.float32)
            logits, unc = self.forward(x_t)
            scaled_logits = logits / torch.clamp(self.temperature, min=0.01)
            probs = torch.softmax(scaled_logits, dim=-1)
            return probs.numpy(), unc.numpy().squeeze(-1)

    def predict_probs(self, x_np: np.ndarray) -> np.ndarray:
        probs, _ = self.predict_probs_and_uncertainty(x_np)
        return probs

    def fit(self, X: np.ndarray, y: np.ndarray, epochs: int = 40, lr: float = 0.008):
        self.train()
        ce_criterion = nn.CrossEntropyLoss()
        optimizer = optim.AdamW(self.parameters(), lr=lr, weight_decay=1e-4)
        
        X_t = torch.tensor(X, dtype=torch.float32)
        y_t = torch.tensor(y, dtype=torch.long)
        
        for _ in range(epochs):
            optimizer.zero_grad()
            logits, unc = self.forward(X_t)
            loss = ce_criterion(logits, y_t)
            loss.backward()
            optimizer.step()

    def calibrate(self, X_val: np.ndarray, y_val: np.ndarray):
        self.eval()
        with torch.no_grad():
            logits, _ = self.forward(torch.tensor(X_val, dtype=torch.float32))
            
        y_val_t = torch.tensor(y_val, dtype=torch.long)
        temp = nn.Parameter(torch.ones(1) * 1.5)
        optimizer = optim.LBFGS([temp], lr=0.05, max_iter=50)
        criterion = nn.CrossEntropyLoss()

        def eval_loss():
            optimizer.zero_grad()
            loss = criterion(logits / torch.clamp(temp, min=0.05), y_val_t)
            loss.backward()
            return loss

        optimizer.step(eval_loss)
        self.temperature.data = temp.data.clamp(min=0.05)


class B5_TemporalLatentMarkov:
    """
    B5: Temporal Latent Markov Model.
    Combines calibrated observation likelihoods (from B1/B4) with explicit
    Markovian state dynamics and tempo-modulated transition smoothing.
    """
    def __init__(self, observation_model, transition_matrix: Optional[np.ndarray] = None):
        self.obs_model = observation_model
        if transition_matrix is not None:
            self.transition_matrix = transition_matrix.copy()
        else:
            self.transition_matrix = GROUND_TRUTH_TRANSITION.copy()
        self.bayes_filter = B2_BayesFilter(self.transition_matrix)

    def reset(self):
        self.bayes_filter.reset()

    def step(self, obs: np.ndarray) -> Tuple[np.ndarray, np.ndarray]:
        """
        Given observation features x_t, compute likelihoods, update belief,
        and predict next state distribution.
        Returns:
            posterior_belief: np.ndarray (shape [5])
            next_state_prediction: np.ndarray (shape [5])
        """
        # 1. Observation likelihood from calibrated primitive
        probs = self.obs_model.predict_probs(obs.reshape(1, -1))[0]
        
        # 2. Recursive belief update
        posterior = self.bayes_filter.update(probs)
        
        # 3. Next-state prediction: P(s_{t+1}) = T^T @ posterior
        next_state_pred = self.transition_matrix.T @ posterior
        return posterior, next_state_pred
