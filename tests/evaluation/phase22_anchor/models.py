"""
Candidate Architectures for Phase 22-ANCHOR:
Relational Memory Grounding & Episodic Anchor Study.

Candidates:
- A0 — O4 Continuous Path-Integral Accumulation Baseline (Phase 22-REL failure baseline).
- A1 — Episodic Anchors Only (Sparse Event Memory; updates ONLY on detected relational events).
- A2 — Episodic Anchors + Confidence / Epistemic Uncertainty Gating.
- A3 — Episodic Anchors + Temporal Decay / Consolidation (SDM Memory Consolidation).
- Oracle — Oracle Relational Memory Filter.
"""
from typing import Dict, List, Tuple, Optional
import numpy as np

class Candidate_A0_ContinuousAccumulation:
    """A0: Continuous turn-level accumulation baseline (Identical to Phase 22-REL O4)."""
    def __init__(self, ridge_lambda: float = 1e-3):
        self.ridge_lambda = ridge_lambda
        self.W_u = None
        self.b_u = None
        self.u = None
        self.m = None
        self.P_u = None

    def fit(self, X: np.ndarray, U_4d: np.ndarray):
        N, D = X.shape
        X_aug = np.hstack([X, np.ones((N, 1))])
        reg = self.ridge_lambda * np.eye(D + 1)
        reg[-1, -1] = 0.0
        W_aug = np.linalg.solve(X_aug.T @ X_aug + reg, X_aug.T @ U_4d)
        self.W_u = W_aug[:-1, :].T # (4, 25)
        self.b_u = W_aug[-1, :]

    def reset_session(self, u_init: Optional[np.ndarray] = None, m_init: Optional[np.ndarray] = None):
        self.u = u_init.copy() if u_init is not None else np.array([0.0, 0.2, 0.2, 0.1])
        if self.m is None:
            self.m = m_init.copy() if m_init is not None else np.array([0.2, 0.3])
        self.P_u = 0.05 * np.eye(4)

    def step(self, x: np.ndarray) -> Tuple[np.ndarray, np.ndarray, bool]:
        if self.u is None:
            self.reset_session()
        # 4D EKF update
        u_pred = self.u - np.array([0.15, 0.10, 0.20, 0.25]) * (self.u - np.array([0.0, 0.2, 0.2, 0.1]))
        P_pred = self.P_u + 0.005 * np.eye(4)
        y = self.W_u @ x + self.b_u
        S = P_pred + 0.02 * np.eye(4)
        K = P_pred @ np.linalg.inv(S)
        self.u = u_pred + K @ (y - u_pred)
        self.P_u = (np.eye(4) - K) @ P_pred
        self.u[0:3] = np.clip(self.u[0:3], -1.0, 1.0)
        self.u[3]   = np.clip(self.u[3],    0.0, 1.0)
        
        # Continuous accumulation (suffers unanchored drift)
        self.m[0] += 0.03 * max(0.0, self.u[0]) + 0.03 * self.u[3]
        self.m[1] += 0.03 * self.u[1]
        self.m[0] = np.clip(self.m[0],  0.0, 1.0)
        self.m[1] = np.clip(self.m[1], -1.0, 1.0)
        return self.u.copy(), self.m.copy(), False

    def consolidate_inter_session(self):
        # Somatic sleep reset
        self.m[0] = 0.20

class Candidate_A1_EpisodicAnchorsOnly:
    """
    A1: Episodic Anchors Only.
    - Relational Warmth is stored as persistent autobiographical memory.
    - ONLY updates when an explicit relational anchor event is detected.
    - Zero drift during neutral/work turns.
    """
    def __init__(self, ridge_lambda: float = 1e-3):
        self.ridge_lambda = ridge_lambda
        self.W_u = None
        self.b_u = None
        self.u = None
        self.m = None
        self.P_u = None
        self.anchors: List[Dict] = []

    def fit(self, X: np.ndarray, U_4d: np.ndarray):
        N, D = X.shape
        X_aug = np.hstack([X, np.ones((N, 1))])
        reg = self.ridge_lambda * np.eye(D + 1)
        reg[-1, -1] = 0.0
        W_aug = np.linalg.solve(X_aug.T @ X_aug + reg, X_aug.T @ U_4d)
        self.W_u = W_aug[:-1, :].T
        self.b_u = W_aug[-1, :]

    def reset_session(self, u_init: Optional[np.ndarray] = None, m_init: Optional[np.ndarray] = None):
        self.u = u_init.copy() if u_init is not None else np.array([0.0, 0.2, 0.2, 0.1])
        if self.m is None:
            self.m = m_init.copy() if m_init is not None else np.array([0.2, 0.3])
        self.P_u = 0.05 * np.eye(4)

    def step(self, x: np.ndarray) -> Tuple[np.ndarray, np.ndarray, bool]:
        if self.u is None:
            self.reset_session()
        # 1. 4D EKF update
        u_pred = self.u - np.array([0.15, 0.10, 0.20, 0.25]) * (self.u - np.array([0.0, 0.2, 0.2, 0.1]))
        P_pred = self.P_u + 0.005 * np.eye(4)
        y = self.W_u @ x + self.b_u
        S = P_pred + 0.02 * np.eye(4)
        K = P_pred @ np.linalg.inv(S)
        self.u = u_pred + K @ (y - u_pred)
        self.P_u = (np.eye(4) - K) @ P_pred
        self.u[0:3] = np.clip(self.u[0:3], -1.0, 1.0)
        self.u[3]   = np.clip(self.u[3],    0.0, 1.0)
        
        # 2. Somatic fatigue tracking
        self.m[0] += 0.03 * max(0.0, self.u[0]) + 0.03 * self.u[3]
        self.m[0] = np.clip(self.m[0], 0.0, 1.0)
        
        # 3. Anchor Event Detector
        # Text one-hot indices: 4: relational_anchor_event, 5: relational_rupture_event
        is_milestone = bool(x[4] > 0.5)
        is_rupture = bool(x[5] > 0.5)
        anchor_detected = is_milestone or is_rupture
        
        if is_milestone:
            delta = 0.15
            self.m[1] += delta
            self.anchors.append({"type": "milestone", "delta": delta, "valence": self.u[1]})
        elif is_rupture:
            delta = -0.35
            self.m[1] += delta
            self.anchors.append({"type": "rupture", "delta": delta, "valence": self.u[1]})
            
        self.m[1] = np.clip(self.m[1], -1.0, 1.0)
        return self.u.copy(), self.m.copy(), anchor_detected

    def consolidate_inter_session(self):
        # Somatic fatigue homeostatic reset
        self.m[0] = 0.20

class Candidate_A2_EpisodicAnchorsConfidence:
    """
    A2: Episodic Anchors + Epistemic Uncertainty & Consistency Verification.
    - Anchors are accepted only when multimodal evidence is consistent with observable valence
      (e.g., milestone must have positive valence u_1 > 0; rupture must have negative valence u_1 < 0).
    - Reduces false-positive anchor creation.
    """
    def __init__(self, ridge_lambda: float = 1e-3):
        self.ridge_lambda = ridge_lambda
        self.W_u = None
        self.b_u = None
        self.u = None
        self.m = None
        self.P_u = None
        self.anchors: List[Dict] = []

    def fit(self, X: np.ndarray, U_4d: np.ndarray):
        N, D = X.shape
        X_aug = np.hstack([X, np.ones((N, 1))])
        reg = self.ridge_lambda * np.eye(D + 1)
        reg[-1, -1] = 0.0
        W_aug = np.linalg.solve(X_aug.T @ X_aug + reg, X_aug.T @ U_4d)
        self.W_u = W_aug[:-1, :].T
        self.b_u = W_aug[-1, :]

    def reset_session(self, u_init: Optional[np.ndarray] = None, m_init: Optional[np.ndarray] = None):
        self.u = u_init.copy() if u_init is not None else np.array([0.0, 0.2, 0.2, 0.1])
        if self.m is None:
            self.m = m_init.copy() if m_init is not None else np.array([0.2, 0.3])
        self.P_u = 0.05 * np.eye(4)

    def step(self, x: np.ndarray) -> Tuple[np.ndarray, np.ndarray, bool]:
        if self.u is None:
            self.reset_session()
        # 1. 4D EKF update
        u_pred = self.u - np.array([0.15, 0.10, 0.20, 0.25]) * (self.u - np.array([0.0, 0.2, 0.2, 0.1]))
        P_pred = self.P_u + 0.005 * np.eye(4)
        y = self.W_u @ x + self.b_u
        S = P_pred + 0.02 * np.eye(4)
        K = P_pred @ np.linalg.inv(S)
        self.u = u_pred + K @ (y - u_pred)
        self.P_u = (np.eye(4) - K) @ P_pred
        self.u[0:3] = np.clip(self.u[0:3], -1.0, 1.0)
        self.u[3]   = np.clip(self.u[3],    0.0, 1.0)
        
        # 2. Somatic fatigue tracking
        self.m[0] += 0.03 * max(0.0, self.u[0]) + 0.03 * self.u[3]
        self.m[0] = np.clip(self.m[0], 0.0, 1.0)
        
        # 3. Gated Anchor Detector with Multimodal Valence Consistency
        is_milestone = bool(x[4] > 0.5 and self.u[1] > 0.20)
        is_rupture = bool(x[5] > 0.5 and self.u[1] < -0.20)
        anchor_detected = is_milestone or is_rupture
        
        confidence = float(np.clip(1.0 - np.trace(self.P_u), 0.5, 1.0))
        
        if is_milestone:
            delta = 0.15 * confidence
            self.m[1] += delta
            self.anchors.append({"type": "milestone", "delta": delta, "confidence": confidence})
        elif is_rupture:
            delta = -0.35 * confidence
            self.m[1] += delta
            self.anchors.append({"type": "rupture", "delta": delta, "confidence": confidence})
            
        self.m[1] = np.clip(self.m[1], -1.0, 1.0)
        return self.u.copy(), self.m.copy(), anchor_detected

    def consolidate_inter_session(self):
        self.m[0] = 0.20

class Candidate_A3_EpisodicAnchorsDecayConsolidation:
    """
    A3: Episodic Anchors + Temporal Decay toward Philia Attractor + SDM Consolidation.
    - Anchors provide episodic step shifts in relational warmth.
    - Long-term memory exhibits slow exponential decay toward Philia resting baseline (+0.30).
    - Session-to-session autobiographical consolidation preserves salient memory traces.
    """
    def __init__(self, ridge_lambda: float = 1e-3, resting_warmth: float = 0.30):
        self.ridge_lambda = ridge_lambda
        self.resting_warmth = resting_warmth
        self.W_u = None
        self.b_u = None
        self.u = None
        self.m = None
        self.P_u = None
        self.anchors: List[Dict] = []

    def fit(self, X: np.ndarray, U_4d: np.ndarray):
        N, D = X.shape
        X_aug = np.hstack([X, np.ones((N, 1))])
        reg = self.ridge_lambda * np.eye(D + 1)
        reg[-1, -1] = 0.0
        W_aug = np.linalg.solve(X_aug.T @ X_aug + reg, X_aug.T @ U_4d)
        self.W_u = W_aug[:-1, :].T
        self.b_u = W_aug[-1, :]

    def reset_session(self, u_init: Optional[np.ndarray] = None, m_init: Optional[np.ndarray] = None):
        self.u = u_init.copy() if u_init is not None else np.array([0.0, 0.2, 0.2, 0.1])
        if self.m is None:
            self.m = m_init.copy() if m_init is not None else np.array([0.2, 0.3])
        self.P_u = 0.05 * np.eye(4)

    def step(self, x: np.ndarray) -> Tuple[np.ndarray, np.ndarray, bool]:
        if self.u is None:
            self.reset_session()
        # 1. 4D EKF update
        u_pred = self.u - np.array([0.15, 0.10, 0.20, 0.25]) * (self.u - np.array([0.0, 0.2, 0.2, 0.1]))
        P_pred = self.P_u + 0.005 * np.eye(4)
        y = self.W_u @ x + self.b_u
        S = P_pred + 0.02 * np.eye(4)
        K = P_pred @ np.linalg.inv(S)
        self.u = u_pred + K @ (y - u_pred)
        self.P_u = (np.eye(4) - K) @ P_pred
        self.u[0:3] = np.clip(self.u[0:3], -1.0, 1.0)
        self.u[3]   = np.clip(self.u[3],    0.0, 1.0)
        
        # 2. Somatic fatigue tracking
        self.m[0] += 0.03 * max(0.0, self.u[0]) + 0.03 * self.u[3]
        self.m[0] = np.clip(self.m[0], 0.0, 1.0)
        
        # 3. Anchor Event Detection
        is_milestone = bool(x[4] > 0.5 and self.u[1] > 0.15)
        is_rupture = bool(x[5] > 0.5 and self.u[1] < -0.15)
        anchor_detected = is_milestone or is_rupture
        
        if is_milestone:
            delta = 0.15
            self.m[1] += delta
            self.anchors.append({"type": "milestone", "delta": delta})
        elif is_rupture:
            delta = -0.35
            self.m[1] += delta
            self.anchors.append({"type": "rupture", "delta": delta})
            
        self.m[1] = np.clip(self.m[1], -1.0, 1.0)
        return self.u.copy(), self.m.copy(), anchor_detected

    def consolidate_inter_session(self):
        # 1. Homeostatic sleep reset for fatigue
        self.m[0] = 0.20
        # 2. Synaptic consolidation with slow Philia relaxation (ADR-028)
        self.m[1] = 0.98 * self.m[1] + 0.02 * self.resting_warmth

class OracleControlAnchor:
    """Perfect Oracle Filter."""
    def __init__(self):
        pass
    def reset_session(self, u_true: np.ndarray, m_true: np.ndarray):
        pass
    def step(self, u_true: np.ndarray, m_true: np.ndarray) -> Tuple[np.ndarray, np.ndarray, bool]:
        return u_true + np.random.normal(0, 0.01, size=4), m_true + np.random.normal(0, 0.01, size=2), False
    def consolidate_inter_session(self):
        pass
