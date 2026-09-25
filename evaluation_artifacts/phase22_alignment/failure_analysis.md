# Failure Analysis & Attribution — Phase 22-AL

## 1. Executive Summary

Phase 22-AL set out to isolate the exact cause of the continuous latent alignment failure:
> *Was the failure in Phase 22-OLR caused by the absence of an explicit Observation-to-Latent State Formation layer, or by an intrinsic Information Bottleneck in candidate representations C1–C6?*

The empirical results provide an unambiguous, mathematically falsifiable diagnosis:
**The primary failure mode is an INFORMATION BOTTLENECK within candidate representations C1–C6, compounded by a secondary MAPPING BOTTLENECK in zero-shot baselines.**

---

## 2. Quantitative Bottleneck Decomposition

We decompose the total variance unexplained ($1 - R^2$) into three distinct structural components:
1. **Coordinate Remapping Deficit:** Resolved by moving from $A_0$ to $A_1$ (Linear Ridge).
2. **Dynamical Estimation Deficit:** Resolved by moving from static $A_1$ to state estimator $A_5$ (Leaky Filter).
3. **Representation Information Bottleneck:** The remaining unexplained gap between peak alignment ($A_5$) and Oracle ($D$).

### Quantitative Decomposition on Candidate C4 (Hybrid Multimodal)

| Metric Layer | $R^2$ Level | $\Delta R^2$ Relative to Baseline | Fraction of Total Gap Resolved | Unresolved Bottleneck |
| :--- | :---: | :---: | :---: | :--- |
| **A0 (Naive Zero-Shot)** | -0.9690 | Baseline | 0.0% | Complete Coordinate Mismatch |
| **A1 (Linear Projection)** | +0.2231 | +1.1921 | 63.7% | Resolves static coordinate scaling |
| **A5 (Leaky State Estimator)** | +0.2548 | +0.0317 | 1.7% | Smooths high-frequency noise |
| **Oracle (Ground Truth $D$)** | **+0.9018** | **+0.6470** | **34.6%** | **Unreachable Information Deficit** |

### Key Insight
- Introducing an explicit alignment mechanism ($A_1$) rescues catastrophic negative baseline behavior ($R^2 = -0.9690 \to +0.2231$).
- However, the alignment improvement saturates at **$R^2 = +0.2548$**.
- The remaining **$+0.6470$ $R^2$ gap to the oracle** cannot be closed by any tested state formation architecture (MLP, temporal windowing, Bayesian inversion, or leaky integration).
- Thus, **over 34.6% of the absolute gap (and 100% of the gate shortfall $0.85 - 0.2548 = 0.5952$) is attributable directly to lack of information in the observation representations**.

---

## 3. Physical & Mathematical Causes of the Information Bottleneck

### 1. Discrete Lexical / Dialog Act Logits Lack Continuous Micro-Dynamics
- Candidates C2 (DistilBERT logits), C5 (Dialog acts), and C6 (Decoupled semantic) discretize language into categorical probability distributions (e.g., greeting, query, affirmation, confrontation).
- In contrast, the continuous latent user state in Lucia is governed by an Ornstein-Uhlenbeck dynamical system with inertia, friction, and continuous drifting velocities:
  $$dz_t = -\Theta (z_t - \mu) dt + \Sigma dW_t$$
- Turn-level categorical classifications do not contain the continuous velocity or micro-temporal gradients necessary to invert an OU state.

### 2. Sentence Embeddings Compress Out Affective State Coordinates
- Candidate C1 (MiniLM-L6-v2) generates 384-dimensional dense semantic embeddings trained for topical retrieval and semantic similarity.
- These representations collapse fine-grained emotional valence, arousal tension, and relational agency into broad semantic clusters. Moving from $A_0$ to $A_1$ only yields $R^2 = +0.0635$.

### 3. Acoustic Features Provide Incomplete Coordinates
- Candidate C3 (Audio DSP) captures acoustic energy, pitch jitter, and speaking rate. These correlate moderately with arousal and dominance ($R^2 = +0.1806$).
- However, acoustic features carry zero semantic valence, creating an orthogonal blind spot that prevents holistic 6D state reconstruction.

### 4. Overfitting & Sensitivity in Non-Linear Encoders
- Non-linear networks ($A_3$ MLP, $A_7$ Hybrid) suffered from extreme degradation under stress regimes (e.g., NoiseSurge, ContradictionShock), dropping $R^2$ into negative numbers.
- Small calibration networks lack inductive physical biases and easily overfit to spurious features when trained on limited dialogue trajectories.

---

## 4. Final Diagnostic Summary

| Hypothesis | Evaluated Status | Empirical Basis |
| :--- | :---: | :--- |
| **H-AL1 (Coordinate Transformation)** | **PARTIALLY SUPPORTED** | Linear projection lifts $R^2$ from negative to positive ($+0.22$), but plateaus far below $0.85$. |
| **H-AL2 (Temporal Integration)** | **REJECTED** | Expanding raw observation context $k \in [1, 10]$ monotonically degrades held-out $R^2$. |
| **H-AL3 (State Estimation)** | **SUPPORTED** | Leaky state estimation ($A_5$) and likelihood inversion ($A_6$) strictly outperform static mappings. |
| **H-AL4 (Supervised Alignment)** | **REJECTED AS SUFFICIENT** | Supervised alignment alone cannot overcome missing representation signals. |
| **H-AL5 (Representation Sufficiency)** | **CONFIRMED DEFICIENT** | Candidate representations lack the necessary mathematical signal to recover $z_t$ ($R^2_{\max} = 0.2548 \ll 0.85$). |
