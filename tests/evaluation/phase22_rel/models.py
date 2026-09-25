"""
Architectures for Phase 22-REL:
Relational & Somatic Memory Consolidation Study.

Candidates:
1. O1 — Legacy 6D joint ridge regression baseline.
2. O2 — Open-loop Layer B baseline (Phase 22-ONT decoupled model).
3. O3 — Episodic Consolidation (SDM-like episodic evidence extraction + offline consolidation + sleep restoration).
4. O4 — Episodic Consolidation with Uncertainty & Closed-Loop Error Correction (Kalman innovation gating on episodic traces).
5. Oracle — Oracle Latent State Filter.
"""
from typing import Dict, List, Tuple, Optional
import numpy as np

class Candidate_O1_Legacy6D:
    """O1: Legacy single-timescale 6D ridge regression."""
    def __init__(self, alpha: float = 0.35, ridge_lambda: float = 1e-3):
        self.alpha = alpha
        self.ridge_lambda = ridge_lambda
        self.W = None
        self.b = None
        self.z = None

    def fit(self, X: np.ndarray, Y_6d: np.ndarray):
        N, D = X.shape
        X_aug = np.hstack([X, np.ones((N, 1))])
        reg = self.ridge_lambda * np.eye(D + 1)
        reg[-1, -1] = 0.0
        W_aug = np.linalg.solve(X_aug.T @ X_aug + reg, X_aug.T @ Y_6d)
        self.W = W_aug[:-1, :].T # (6, 23)
        self.b = W_aug[-1, :]    # (6,)

    def reset_session(self, z_init: Optional[np.ndarray] = None):
        self.z = z_init.copy() if z_init is not None else np.array([0.0, 0.2, 0.2, 0.1, 0.2, 0.3])

    def step(self, x: np.ndarray) -> np.ndarray:
        if self.z is None:
            self.reset_session()
        z_obs = self.W @ x + self.b
        self.z = (1.0 - self.alpha) * self.z + self.alpha * z_obs
        self.z[0:3] = np.clip(self.z[0:3], -1.0, 1.0)
        self.z[3:5] = np.clip(self.z[3:5],  0.0, 1.0)
        self.z[5]   = np.clip(self.z[5],   -1.0, 1.0)
        return self.z.copy()

    def consolidate_inter_session(self):
        # Legacy model has no inter-session consolidation logic; state simply persists or resets
        pass

class Candidate_O2_OpenLoopDecoupled:
    """O2: Decoupled 4D EKF + Open-loop Slow State Accumulation (Identical to Phase 22-ONT O2/O3)."""
    def __init__(self, beta_m: float = 0.05, ridge_lambda: float = 1e-3):
        self.beta_m = beta_m
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
        self.W_u = W_aug[:-1, :].T # (4, 23)
        self.b_u = W_aug[-1, :]    # (4,)

    def reset_session(self, u_init: Optional[np.ndarray] = None, m_init: Optional[np.ndarray] = None):
        self.u = u_init.copy() if u_init is not None else np.array([0.0, 0.2, 0.2, 0.1])
        if self.m is None:
            self.m = m_init.copy() if m_init is not None else np.array([0.2, 0.3])
        self.P_u = 0.05 * np.eye(4)

    def step(self, x: np.ndarray) -> Tuple[np.ndarray, np.ndarray]:
        if self.u is None or self.m is None:
            self.reset_session()
        # 1. 4D EKF
        u_pred = self.u - np.array([0.15, 0.10, 0.20, 0.25]) * (self.u - np.array([0.0, 0.2, 0.2, 0.1]))
        P_pred = self.P_u + 0.005 * np.eye(4)
        y = self.W_u @ x + self.b_u
        S = P_pred + 0.02 * np.eye(4)
        K = P_pred @ np.linalg.inv(S)
        self.u = u_pred + K @ (y - u_pred)
        self.P_u = (np.eye(4) - K) @ P_pred
        self.u[0:3] = np.clip(self.u[0:3], -1.0, 1.0)
        self.u[3]   = np.clip(self.u[3],    0.0, 1.0)
        
        # 2. Open-loop slow accumulation
        coupling = np.array([
            0.05 * max(0.0, self.u[0]) + 0.05 * self.u[3],
            0.04 * self.u[1] + 0.02 * self.u[2]
        ])
        self.m += -0.02 * (self.m - np.array([0.2, 0.3])) + coupling
        self.m[0] = np.clip(self.m[0],  0.0, 1.0)
        self.m[1] = np.clip(self.m[1], -1.0, 1.0)
        return self.u.copy(), self.m.copy()

    def consolidate_inter_session(self):
        # Open-loop model does nothing between sessions (drifts)
        pass

class Candidate_O3_EpisodicConsolidation:
    """
    O3: Episodic Memory Consolidation.
    - Layer A: Fast 4D Observable state tracked via closed-loop EKF.
    - Turn level: Extracts salient episodic evidence vectors e_t = [delta_fatigue, delta_warmth].
    - Inter-session / offline consolidation:
      * Aggregates session episodic memory traces into consolidated synaptic state m_consolidated.
      * Applies homeostatic sleep restoration to metabolic fatigue (80% reset).
      * Preserves relational warmth with high synaptic retention (>90%).
    """
    def __init__(self, ridge_lambda: float = 1e-3):
        self.ridge_lambda = ridge_lambda
        self.W_u = None
        self.b_u = None
        self.u = None
        self.P_u = None
        
        # Persistent Relational / Somatic Memory
        self.m_persistent = np.array([0.2, 0.3], dtype=np.float64) # Basal fatigue=0.2, warmth=0.3
        self.m_session_current = np.array([0.2, 0.3], dtype=np.float64)
        self.session_episodic_buffer: List[np.ndarray] = []

    def fit(self, X: np.ndarray, U_4d: np.ndarray):
        N, D = X.shape
        X_aug = np.hstack([X, np.ones((N, 1))])
        reg = self.ridge_lambda * np.eye(D + 1)
        reg[-1, -1] = 0.0
        W_aug = np.linalg.solve(X_aug.T @ X_aug + reg, X_aug.T @ U_4d)
        self.W_u = W_aug[:-1, :].T # (4, 23)
        self.b_u = W_aug[-1, :]    # (4,)

    def reset_session(self, u_init: Optional[np.ndarray] = None, m_init: Optional[np.ndarray] = None):
        self.u = u_init.copy() if u_init is not None else np.array([0.0, 0.2, 0.2, 0.1])
        self.P_u = 0.05 * np.eye(4)
        if m_init is not None and not hasattr(self, "_initialized"):
            self.m_persistent = m_init.copy()
            self._initialized = True
        self.m_session_current = self.m_persistent.copy()
        self.session_episodic_buffer = []

    def step(self, x: np.ndarray) -> Tuple[np.ndarray, np.ndarray]:
        if self.u is None:
            self.reset_session()
        # 1. Layer A 4D EKF
        u_pred = self.u - np.array([0.15, 0.10, 0.20, 0.25]) * (self.u - np.array([0.0, 0.2, 0.2, 0.1]))
        P_pred = self.P_u + 0.005 * np.eye(4)
        y = self.W_u @ x + self.b_u
        S = P_pred + 0.02 * np.eye(4)
        K = P_pred @ np.linalg.inv(S)
        self.u = u_pred + K @ (y - u_pred)
        self.P_u = (np.eye(4) - K) @ P_pred
        self.u[0:3] = np.clip(self.u[0:3], -1.0, 1.0)
        self.u[3]   = np.clip(self.u[3],    0.0, 1.0)
        
        # 2. Extract turn episodic evidence trace
        # Epistemic / interaction markers: turn latency, pause ratio, synchrony
        pause_signal = x[15] # temporal t2 ~ pause ratio
        sync_signal = x[21]  # interaction i2 ~ dyadic synchrony
        latency_signal = x[19] # interaction i0
        
        delta_fatigue = 0.04 * max(0.0, self.u[0]) + 0.04 * self.u[3] + 0.03 * (pause_signal - 0.3)
        delta_warmth = 0.035 * self.u[1] + 0.015 * self.u[2] + 0.03 * (sync_signal - 0.5)
        
        episodic_delta = np.array([delta_fatigue, delta_warmth])
        self.session_episodic_buffer.append(episodic_delta)
        
        # Intra-session somatic projection
        self.m_session_current += episodic_delta - 0.01 * (self.m_session_current - np.array([0.2, 0.3]))
        self.m_session_current[0] = np.clip(self.m_session_current[0],  0.0, 1.0)
        self.m_session_current[1] = np.clip(self.m_session_current[1], -1.0, 1.0)
        
        return self.u.copy(), self.m_session_current.copy()

    def consolidate_inter_session(self):
        """
        Offline Synaptic / Episodic Consolidation (Phase 21 Homeostasis):
        1. Summarize episodic memory buffer.
        2. Homeostatic sleep resets fatigue: 80% restored to rested 0.2.
        3. Warmth consolidates into persistent state with 95% retention.
        """
        if self.session_episodic_buffer:
            mean_session_delta = np.mean(self.session_episodic_buffer, axis=0)
            net_warmth_gain = np.sum([d[1] for d in self.session_episodic_buffer])
            # Consolidate into persistent relational memory
            self.m_persistent[1] = 0.95 * (self.m_persistent[1] + 0.3 * net_warmth_gain) + 0.05 * 0.3
            self.m_persistent[1] = np.clip(self.m_persistent[1], -1.0, 1.0)
            
        # Homeostatic fatigue reset
        self.m_persistent[0] = 0.20 # Fully restored after sleep

class Candidate_O4_EpisodicConsolidationCorrected:
    """
    O4: Episodic Consolidation with Uncertainty & Closed-Loop Error Correction.
    - Layer A: Fast 4D Observable state tracked via closed-loop EKF.
    - Layer B: Dual-timescale relational consolidation:
      * Gated by epistemic certainty Tr(P_u). When observable uncertainty is high, weight of evidence is attenuated.
      * Closed-loop innovation correction from dyadic synchrony and pause acoustics.
      * Offline synaptic consolidation + homeostatic sleep.
    """
    def __init__(self, ridge_lambda: float = 1e-3):
        self.ridge_lambda = ridge_lambda
        self.W_u = None
        self.b_u = None
        self.u = None
        self.P_u = None
        
        self.m_persistent = np.array([0.2, 0.3], dtype=np.float64)
        self.m_session_current = np.array([0.2, 0.3], dtype=np.float64)
        self.session_episodic_buffer: List[np.ndarray] = []

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
        self.P_u = 0.05 * np.eye(4)
        if m_init is not None and not hasattr(self, "_initialized"):
            self.m_persistent = m_init.copy()
            self._initialized = True
        self.m_session_current = self.m_persistent.copy()
        self.session_episodic_buffer = []

    def step(self, x: np.ndarray) -> Tuple[np.ndarray, np.ndarray]:
        if self.u is None:
            self.reset_session()
        # 1. 4D EKF
        u_pred = self.u - np.array([0.15, 0.10, 0.20, 0.25]) * (self.u - np.array([0.0, 0.2, 0.2, 0.1]))
        P_pred = self.P_u + 0.005 * np.eye(4)
        y = self.W_u @ x + self.b_u
        S = P_pred + 0.02 * np.eye(4)
        K = P_pred @ np.linalg.inv(S)
        self.u = u_pred + K @ (y - u_pred)
        self.P_u = (np.eye(4) - K) @ P_pred
        self.u[0:3] = np.clip(self.u[0:3], -1.0, 1.0)
        self.u[3]   = np.clip(self.u[3],    0.0, 1.0)
        
        # 2. Epistemic certainty gating
        epistemic_certainty = np.clip(1.0 - np.trace(self.P_u), 0.1, 1.0)
        
        # Closed-loop measurement markers for slow state
        pause_signal = x[15] # temporal t2 ~ pause ratio
        sync_signal = x[21]  # interaction i2 ~ dyadic synchrony
        latency_signal = x[19] # interaction i0
        
        # Innovation correction for fatigue and warmth
        fatigue_innov = (pause_signal - 0.3) / 0.4
        warmth_innov = (sync_signal - 0.5) / 0.3
        
        delta_fatigue = epistemic_certainty * (0.04 * max(0.0, self.u[0]) + 0.04 * self.u[3]) + 0.02 * fatigue_innov
        delta_warmth = epistemic_certainty * (0.035 * self.u[1] + 0.015 * self.u[2]) + 0.025 * warmth_innov
        
        episodic_delta = np.array([delta_fatigue, delta_warmth])
        self.session_episodic_buffer.append(episodic_delta)
        
        self.m_session_current += episodic_delta - 0.01 * (self.m_session_current - np.array([0.2, 0.3]))
        self.m_session_current[0] = np.clip(self.m_session_current[0],  0.0, 1.0)
        self.m_session_current[1] = np.clip(self.m_session_current[1], -1.0, 1.0)
        
        return self.u.copy(), self.m_session_current.copy()

    def consolidate_inter_session(self):
        """Offline Synaptic Consolidation with error-damped retention."""
        if self.session_episodic_buffer:
            net_warmth_gain = np.sum([d[1] for d in self.session_episodic_buffer])
            self.m_persistent[1] = 0.95 * (self.m_persistent[1] + 0.25 * net_warmth_gain) + 0.05 * 0.3
            self.m_persistent[1] = np.clip(self.m_persistent[1], -1.0, 1.0)
        # Homeostatic fatigue restoration
        self.m_persistent[0] = 0.20

class OracleControlREL:
    """Perfect Oracle Filter."""
    def __init__(self):
        pass
    def reset_session(self, u_true: np.ndarray, m_true: np.ndarray):
        pass
    def step(self, u_true: np.ndarray, m_true: np.ndarray) -> Tuple[np.ndarray, np.ndarray]:
        # Adds microscopic measurement precision error
        return u_true + np.random.normal(0, 0.01, size=4), m_true + np.random.normal(0, 0.01, size=2)
    def consolidate_inter_session(self):
        pass
