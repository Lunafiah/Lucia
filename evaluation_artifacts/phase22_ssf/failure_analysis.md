# Failure Analysis & Bottleneck Identification — Phase 22-SSF

## 1. Executive Summary

Phase 22-SSF set out to evaluate whether decoupling fast observable states ($z_0–z_3$) from slow accumulated states ($z_4–z_5$) resolves the continuous latent alignment bottleneck.

The empirical results reveal:
- **Fast states achieved stable recovery:** $R^2_{\text{fast}} = 0.5716$, matching the raw baseline and capturing working memory load ($z_0 = 0.6767$) and valence ($z_1 = 0.6333$).
- **Decoupled slow states collapsed:** $R^2_{\text{slow}} = -0.9446$ ($z_4 = -1.6089, z_5 = -0.2803$).
- **Overall alignment fell from $0.7003$ to $0.4767$**, failing the $0.85$ target gate and falling below the $0.70$ falsification threshold.

---

## 2. Root Cause Analysis of the Decoupling Failure

### 1. The Open-Loop Somatic Drift Problem
- In the decoupled SSF model, slow states ($z_4$ fatigue, $z_5$ warmth) were updated purely forward in time via heuristic leaky integration:
  $$z_{\text{slow}, t} = (1 - \beta) z_{\text{slow}, t-1} + \beta \cdot g(z_{\text{fast}, t}, \text{latency}_t)$$
- Because this accumulation occurred **without direct observational residual correction**, small estimation errors in the fast coordinates ($z_0, z_1$) accumulated monotonically over multi-turn conversations.
- In contrast, the ground-truth environment's slow states fluctuate with continuous Gaussian diffusion ($q_{\text{noise}} \sim 0.05$). An open-loop accumulator cannot track stochastic diffusion without measurement feedback.

### 2. The Raw Baseline Paradox
- The raw baseline model—which performed joint ridge regression directly from all 23 multimodal features into the full 6D state—achieved **$R^2 = 0.7003$** ($R^2_{\text{fast}} = 0.5716, R^2_{\text{slow}} = +0.4402$).
- Even though $z_4$ and $z_5$ are noisy, empirical linear regression over turn latency, pause ratio, and acoustics extracted real statistical correlation ($z_4 = 0.5807, z_5 = 0.2997$), preventing drift.

### 3. Target Ontology & Identifiability Mismatch
- Attempting to track $z_5$ (relational warmth) as an objective mathematical coordinate in a single session is fundamentally misspecified. Warmth is not an instantaneous physical variable; it is a relational attractor that evolves across sessions.

---

## 3. Bottleneck Attribution Matrix

| Candidate Bottleneck | Evaluated Status | Empirical Finding |
| :--- | :---: | :--- |
| **Observation Information Bottleneck** | **PARTIALLY RESOLVED** | 23D multimodal stream provides sufficient signal for $R^2 \ge 0.70$ when jointly regressed. |
| **Target Ontology Bottleneck** | **CONFIRMED** | Slow states ($z_4, z_5$) have fundamentally different noise dynamics than fast states ($z_0–z_3$). |
| **State Estimator Architecture** | **CONFIRMED DEFECTIVE** | Open-loop accumulation fails ($R^2 = -0.9446$). A Kalman-style state estimator with innovation updates is strictly required. |
| **Temporal Dynamics Bottleneck** | **CONFIRMED** | Excessive inertia in slow integration increases contradiction recovery time from 2.0 to 4.75 turns. |
