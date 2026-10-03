# Innovation Dynamics & Kalman Gain Telemetry Report — Phase 22-EKF

## 1. Overview & Mathematical Formulation

The Extended Kalman Filter (EKF) update equation balances the prior dynamic expectation with fresh sensory evidence:
$$\mathbf{y}_{\text{innov}} = \mathbf{z}_{\text{meas}} - H \hat{\mathbf{z}}_{\text{prior}}$$
$$S = H P_{\text{prior}} H^T + R$$
$$K = P_{\text{prior}} H^T S^{-1}$$
$$\hat{\mathbf{z}}_{\text{post}} = \hat{\mathbf{z}}_{\text{prior}} + K \mathbf{y}_{\text{innov}}$$

Where:
- $\mathbf{y}_{\text{innov}}$ is the measurement innovation (prediction residual).
- $K \in \mathbb{R}^{6 \times 6}$ is the Kalman gain matrix determining how aggressively sensory evidence overwrites the continuous prior.

---

## 2. Empirical Telemetry Across Latent Coordinates

Measured across held-out trajectories under Model 3 (EKF):

| Coordinate Name | Semantic Identity | Mean Innovation Magnitude $\|\mathbf{y}_{\text{innov}}\|$ | Mean Kalman Gain $K_{ii}$ | Dynamic Prior Weight ($1 - K_{ii}$) | Innovation Role / Behavior |
| :--- | :--- | :---: | :---: | :---: | :--- |
| **$z_0$ Cognitive Load** | Working memory demand | 0.0789 | **0.5240** | 0.4760 | Balanced observation & temporal drift |
| **$z_1$ Affective Valence** | Emotional polarity | 0.0958 | **0.4363** | 0.5637 | Prior inertia prevents erratic polarity flips |
| **$z_2$ Agency** | Dominance & autonomy | 0.0749 | **0.4033** | 0.5967 | Prior suppresses single-turn interruption noise |
| **$z_3$ Urgency** | Temporal task pressure | 0.0513 | **0.6095** | 0.3905 | Fast sensory tracking from response latency |
| **$z_4$ Fatigue** | Metabolic exhaustion | 0.0666 | **0.6163** | 0.3837 | Measurement innovation eliminates open-loop drift |
| **$z_5$ Warmth** | Relational affinity | 0.1007 | **0.3139** | 0.6861 | High measurement residual; prior dominates |

---

## 3. Analysis & Key Telemetry Insights

1. **Why Fatigue ($z_4$) Drift Was Fixed:**
   - In M2 (open-loop SSF), $z_4$ had $K_{44} = 0.0$ (zero measurement feedback).
   - In M3 (EKF), the filter assigns a high Kalman gain ($K_{44} = 0.6163$) to sensory innovation derived from pause duration and response latency.
   - This high gain actively pulls the state toward empirical reality on every turn, completely arresting open-loop drift ($R^2 = -1.6089 \to +0.6638$).

2. **The Relational Warmth ($z_5$) Bottleneck:**
   - $z_5$ produces the highest average innovation magnitude ($0.1007$), but has the lowest Kalman gain ($K_{55} = 0.3139$).
   - The filter recognizes that the observation residual covariance for warmth is large ($R_{55} \gg P_{55}$), meaning surface features are noisy and unreliable for $z_5$.
   - Consequently, the filter defaults to relying heavily on the continuous prior ($68.6\%$ prior weight), which prevents erratic jumps but keeps overall alignment low ($R^2 = 0.2558$).
