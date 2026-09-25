# Alignment Models Evaluation Report — Phase 22-AL

## 1. Overview & Evaluation Protocol

Phase 22-AL investigates whether an explicit Observation-to-Latent State Formation layer (A1–A7) bridges semantic observation evidence $e_t$ to continuous user-state dynamics $z_t \in \mathbb{R}^6$, moving beyond the zero-shot direct assignment failure observed in Phase 22-OLR ($A_0$).

### Anti-Cheating & Split Discipline
- **Training Seeds:** 42, 137, 618
- **Held-Out Generalization Seeds:** 1024, 2026
- **Stress Regimes Evaluated:** ID, NoiseSurge, LexicalSparsity, ContradictionShock, TemporalDrift, CombinedStress
- **Target Threshold:** $R^2 \ge 0.85$ (Target for production realization design authorization)
- **Falsification Threshold:** $R^2 < 0.70$ (Preregistered falsification region)

---

## 2. Model Ladder Definitions

- **A0 — Naive Baseline:** Direct coordinate pass-through (historical canonical baseline).
- **A1 — Linear Projection:** Ridge regression ($W e_t + b$) with $L_2$ regularization.
- **A2 — Constrained Projection:** Bounded nonlinear projection ($\tanh(W e_t + b)$).
- **A3 — Small MLP:** 2-layer perceptron with 32 hidden units, ReLU activation, CPU-native.
- **A4 — Temporal Window:** Linear projection over multi-frame concatenated window $[e_{t-k+1}, \dots, e_t]$ for $k=3$.
- **A5 — Leaky State Estimator:** First-order continuous exponential decay filter $z_t = (1-\alpha)z_{t-1} + \alpha f(e_t)$ with $\alpha=0.35$.
- **A6 — Observation Likelihood Estimator:** Bayesian inversion estimating $z_t$ from $p(e_t \mid z_t) \sim \mathcal{N}(H z_t, R)$ with empirical residual noise covariance.
- **A7 — Hybrid Temporal Alignment:** Concatenated temporal window ($k=3$), non-linear hidden transformation, bounded projection, and leaky integration.

---

## 3. Empirical Results Across Candidates (Held-Out Seeds: 1024, 2026)

All values represent cross-regime held-out averages.

| Candidate | Model | $R^2$ Score | MAE | MSE | Status |
| :--- | :--- | :---: | :---: | :---: | :---: |
| **C1** (MiniLM-L6-v2) | A0_Naive | -1.1303 | 0.1775 | 0.0538 | Baseline Defect |
| | A1_Linear | +0.0635 | 0.1071 | 0.0236 | Sub-Falsification |
| | A2_Constrained | -1.5419 | 0.1870 | 0.0641 | Negative |
| | A3_SmallMLP | -0.6357 | 0.1355 | 0.0413 | Negative |
| | A4_TemporalWindow_k3 | +0.0156 | 0.1079 | 0.0248 | Sub-Falsification |
| | A5_LeakyIntegrator | +0.0729 | 0.1056 | 0.0234 | Sub-Falsification |
| | A6_ObservationLikelihood | +0.0809 | 0.1060 | 0.0232 | Sub-Falsification |
| | A7_HybridTemporal | -0.1530 | 0.1151 | 0.0291 | Negative |
| **C2** (DistilBERT Logits) | A0_Naive | -0.6355 | 0.1453 | 0.0413 | Baseline Defect |
| | A1_Linear | +0.0365 | 0.1077 | 0.0243 | Sub-Falsification |
| | A2_Constrained | -1.5623 | 0.1865 | 0.0647 | Negative |
| | A3_SmallMLP | -0.3621 | 0.1263 | 0.0344 | Negative |
| | A4_TemporalWindow_k3 | +0.0181 | 0.1082 | 0.0248 | Sub-Falsification |
| | A5_LeakyIntegrator | +0.0431 | 0.1070 | 0.0241 | Sub-Falsification |
| | A6_ObservationLikelihood | +0.0501 | 0.1069 | 0.0240 | Sub-Falsification |
| | A7_HybridTemporal | -0.1186 | 0.1123 | 0.0282 | Negative |
| **C3** (Audio Acoustic DSP) | A0_Naive | -4.2341 | 0.2897 | 0.1321 | Baseline Defect |
| | A1_Linear | +0.1560 | 0.0977 | 0.0213 | Sub-Falsification |
| | A2_Constrained | -1.3082 | 0.1753 | 0.0582 | Negative |
| | A3_SmallMLP | -0.1810 | 0.1174 | 0.0298 | Negative |
| | A4_TemporalWindow_k3 | +0.1616 | 0.0967 | 0.0212 | Sub-Falsification |
| | A5_LeakyIntegrator | +0.1806 | 0.0951 | 0.0207 | Sub-Falsification |
| | A6_ObservationLikelihood | +0.1788 | 0.0961 | 0.0207 | Sub-Falsification |
| | A7_HybridTemporal | +0.0356 | 0.1042 | 0.0243 | Sub-Falsification |
| **C4** (Hybrid Text+Audio) | A0_Naive | -0.9690 | 0.1845 | 0.0497 | Baseline Defect |
| | A1_Linear | +0.2231 | 0.0962 | 0.0196 | Sub-Falsification |
| | A2_Constrained | -1.2575 | 0.1749 | 0.0570 | Negative |
| | A3_SmallMLP | -0.4665 | 0.1286 | 0.0370 | Negative |
| | A4_TemporalWindow_k3 | +0.1907 | 0.0959 | 0.0204 | Sub-Falsification |
| | A5_LeakyIntegrator | **+0.2548** | **0.0923** | **0.0188** | **Peak Held-Out** |
| | A6_ObservationLikelihood | +0.2460 | 0.0944 | 0.0190 | Sub-Falsification |
| | A7_HybridTemporal | +0.0157 | 0.1037 | 0.0248 | Sub-Falsification |
| **C5** (Structured Dialog Acts)| A0_Naive | -3.0515 | 0.2522 | 0.1022 | Baseline Defect |
| | A1_Linear | +0.0469 | 0.1075 | 0.0241 | Sub-Falsification |
| | A2_Constrained | -1.5469 | 0.1847 | 0.0643 | Negative |
| | A3_SmallMLP | -0.5875 | 0.1244 | 0.0401 | Negative |
| | A4_TemporalWindow_k3 | -0.1853 | 0.1120 | 0.0299 | Negative |
| | A5_LeakyIntegrator | +0.0545 | 0.1079 | 0.0239 | Sub-Falsification |
| | A6_ObservationLikelihood | +0.0639 | 0.1070 | 0.0236 | Sub-Falsification |
| | A7_HybridTemporal | -0.3221 | 0.1159 | 0.0334 | Negative |
| **C6** (Decoupled Semantic) | A0_Naive | -0.6355 | 0.1453 | 0.0413 | Baseline Defect |
| | A1_Linear | +0.0365 | 0.1077 | 0.0243 | Sub-Falsification |
| | A2_Constrained | -1.5623 | 0.1865 | 0.0647 | Negative |
| | A3_SmallMLP | -0.3621 | 0.1263 | 0.0344 | Negative |
| | A4_TemporalWindow_k3 | +0.0181 | 0.1082 | 0.0248 | Sub-Falsification |
| | A5_LeakyIntegrator | +0.0431 | 0.1070 | 0.0241 | Sub-Falsification |
| | A6_ObservationLikelihood | +0.0501 | 0.1069 | 0.0240 | Sub-Falsification |
| | A7_HybridTemporal | -0.1186 | 0.1123 | 0.0282 | Negative |

---

## 4. Key Findings & Scientific Diagnosis

1. **Mapping Improvement vs. Gate Satisfaction:**
   - Shifting from unaligned $A_0$ to aligned models ($A_1, A_5, A_6$) produces massive relative gains ($\Delta R^2 > +1.2$ for C4, $\Delta R^2 > +4.3$ for C3).
   - However, the absolute peak performance achieves $R^2 = +0.2548$ (C4 with A5 Leaky Integrator) on held-out seeds.
   - This falls decisively below the target ($R^2 \ge 0.85$) and firmly inside the preregistered **Falsification Region** ($R^2 < 0.70$).

2. **Linear vs. Non-linear Regimes:**
   - Over-parameterized non-linear projections ($A_3$ Small MLP, $A_7$ Hybrid) suffered from out-of-distribution drift under stress regimes, yielding negative $R^2$ scores across several candidates.
   - Linear ridge projection ($A_1$) and continuous leaky filtering ($A_5$) proved significantly more robust to distributional shift than unregularized neural layers.

3. **Conclusion:**
   - The failure of raw observation representations C1–C6 to meet the continuous latent alignment gate is **not merely an absence of coordinate remapping**. Even with optimal linear projection, temporal windowing, and continuous state estimation, candidate representations do not capture the fine-grained Ornstein-Uhlenbeck continuous drift dynamics.
