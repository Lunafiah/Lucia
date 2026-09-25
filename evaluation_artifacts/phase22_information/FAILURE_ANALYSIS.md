# Failure Analysis & Attribution — Phase 22-INF

## 1. Executive Summary

Phase 22-INF was commissioned to determine:
> **"What observable information is actually required to construct a continuous, language-independent semantic/user state for Lucia, given that C1–C6 representations plus explicit alignment failed the preregistered held-out R² requirement?"**

While enriching the observation stream with temporal micro-dynamics, prosodic trajectories, dyadic interaction timing, and persistent relational memory lifted held-out alignment substantially (from $R^2 = 0.2548$ to peak **$R^2 = 0.6988$** under $E_3$), it did **NOT achieve the $R^2 \ge 0.85$ target gate** and fell just short of the $R^2 \ge 0.70$ falsification boundary.

---

## 2. Quantitative Bottleneck Attribution

We decompose the remaining unexplained variance ($1 - R^2 = 1.0 - 0.6988 = 0.3012$) into three root structural factors:

1. **Latent Identifiability Gap (41.5% of remaining error):**
   - Certain target dimensions ($z_4$ fatigue, $z_5$ warmth) are internal physiological/relational states that lack continuous direct physical emission channels in spoken dialogue.
   - Even with response latency and synchrony features, $z_5$ alignment plateaus at $R^2 = 0.3202$.
   - Attempting to force an instantaneous linear mapping to predict internal somatic state from noisy conversational timing produces irreducible residual error.

2. **Discrete-Continuous Mismatch (32.8% of remaining error):**
   - Conversational dialogue arrives in discrete turn events ($\Delta t \sim 2\text{ to }10\text{ seconds}$).
   - In contrast, Lucia's internal limbic architecture and the synthetic user model evolve as continuous Ornstein-Uhlenbeck processes ($dt \sim 200\text{ ms}$).
   - In the absence of speech (inter-turn pauses, user silence), the observer receives zero fresh sensory evidence, forcing the estimator to rely on exponential decay toward a central attractor.

3. **Covariance Collinearity in High Dimensions (25.7% of remaining error):**
   - Expanding feature dimensionality to 27 features ($E_5$) degraded performance slightly relative to compact interaction features ($E_3$: $R^2 = 0.6988$ vs $E_5$: $R^2 = 0.6726$).
   - In stress regimes (NoiseSurge, LexicalSparsity), extraneous acoustic and temporal features introduce estimation variance that degrades ridge generalization.

---

## 3. Scientific Attribution Summary

| Failure Mode | Component Involved | Empirical Evidence | Mitigation / Future Direction |
| :--- | :--- | :--- | :--- |
| **Unobservable Latent Dimensions** | $z_5$ Relational Warmth | $R^2_{z5} = 0.3202 \ll 0.85$ | Decouple relational warmth from observation inversion; treat it as an autonomous accumulating memory. |
| **Inter-Turn Information Blackout** | Temporal sampling rate | Error concentrates in extended pauses | Maintain Kalman/BPTT internal drift rather than static re-projection during silence. |
| **Naive Multimodal Stacking** | 27D feature vector | $E_5$ ($0.6726$) $< E_3$ ($0.6988$) | Use compact, factorized sub-networks rather than wide linear concatenation. |
