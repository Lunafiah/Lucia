"""
Forecasting Models:
1. DiscretePredictionTree: Combinatorial path exploration over discrete intents (P22-X failure).
2. ContinuousTrajectoryForecaster: Continuous trajectory density forecast via ODE drift and covariance propagation (P22-XR).
"""
from typing import Dict, List, Tuple, Optional
import numpy as np
import time
from ..schemas import DiscreteTreeForecast, TrajectoryDensityForecast, ContinuousBeliefState, DiscreteBeliefState
from ..config import STATE_DIM

class DiscretePredictionTree:
    """
    Combinatorial discrete prediction tree branching over top-k intent transitions.
    Suffers exponential path dispersion (30% coverage at H=2 in P22-X).
    """
    def __init__(self, branching_factor: int = 3, max_horizon: int = 2):
        self.branching_factor = branching_factor
        self.max_horizon = max_horizon

    def forecast(self, discrete_belief: DiscreteBeliefState) -> DiscreteTreeForecast:
        t0 = time.perf_counter()
        # Branch over top states
        paths = []
        probs = []
        
        # Level 1: top-B states
        top_indices = np.argsort(discrete_belief.b_simplex)[::-1][:self.branching_factor]
        for s1 in top_indices:
            p1 = discrete_belief.b_simplex[s1]
            if self.max_horizon == 1:
                paths.append([s1])
                probs.append(p1)
            else:
                # Level 2 branching (B * B = 9 paths)
                for s2 in top_indices:
                    p2 = p1 * 0.33
                    paths.append([s1, s2])
                    probs.append(p2)
                    
        latency_us = (time.perf_counter() - t0) * 1e6
        return DiscreteTreeForecast(
            horizon=self.max_horizon,
            branching_factor=self.branching_factor,
            leaves_count=len(paths),
            leaf_paths=paths,
            leaf_probabilities=probs,
            latency_us=latency_us
        )


class ContinuousTrajectoryForecaster:
    """
    Continuous prospective trajectory density forecasting in R^6.
    Integrates forward ODE drift and propagates covariance ellipsoids.
    """
    def __init__(self, gamma: Optional[np.ndarray] = None, z0: Optional[np.ndarray] = None):
        self.gamma = gamma if gamma is not None else np.array([0.15, 0.10, 0.20, 0.25, 0.10, 0.15])
        self.z0 = z0 if z0 is not None else np.array([0.0, 0.2, 0.2, 0.1, 0.5, 0.3])
        self.Q = np.eye(STATE_DIM) * 0.05

    def forecast(self, belief: ContinuousBeliefState, max_horizon: int = 3, dt: float = 1.0) -> TrajectoryDensityForecast:
        t0 = time.perf_counter()
        means = []
        covs = []
        
        curr_z = belief.z_mean.copy()
        curr_P = belief.covariance.copy()
        
        for k in range(1, max_horizon + 1):
            # Forward ODE step: z(t+k) = z(t+k-1) - Gamma * (z - z0) * dt
            curr_z = curr_z - self.gamma * (curr_z - self.z0) * dt
            # Covariance growth
            phi = np.diag(np.exp(-self.gamma * dt))
            curr_P = np.dot(phi, np.dot(curr_P, phi.T)) + self.Q * dt
            
            # Clip bounds
            z_clamped = curr_z.copy()
            z_clamped[0:3] = np.clip(z_clamped[0:3], -1.0, 1.0)
            z_clamped[3:5] = np.clip(z_clamped[3:5],  0.0, 1.0)
            z_clamped[5]   = np.clip(z_clamped[5],   -1.0, 1.0)
            
            means.append(z_clamped)
            covs.append(curr_P.copy())
            
        latency_us = (time.perf_counter() - t0) * 1e6
        return TrajectoryDensityForecast(
            horizon=max_horizon,
            mean_trajectory=means,
            cov_trajectory=covs,
            latency_us=latency_us
        )
