# OBS-E3: CONTINUOUS DYNAMICAL STABILITY REPORT

> **Track Identifier:** OBS-E3  
> **Source Data:** `raw_measurements.json`  
> **Preregistered Gate:** Flapping $\le 2.0\%$ (Target), $\le 9.5\%$ (Gate), Contradiction Recovery $\le 1.0\text{ turn}$  

---

## 1. Measured Continuous Stability Statistics

When connected to the continuous Bucy-Kalman user-state tracker, the belief state evolves via:
$$\dot{\mathbf{z}} = -\boldsymbol{\Gamma}(\mathbf{z} - \mathbf{z}_0) + \mathbf{K}_t (\mathbf{z}_{\text{obs}} - \hat{\mathbf{z}})$$

| Candidate ID | Model / Architecture Class | Flapping Rate (%) | Flapping Gate Compliance | Contradiction Recovery (turns) | Recovery Compliance |
|:---|:---|:---:|:---:|:---:|:---:|
| **Discrete Phase 22-X**| Baseline Discrete Categorical | **23.80%** | Baseline | — | Baseline |
| **Real Laya Baseline** | ModernBERT + Kalman | **0.40%** | **PASS** | **1.0 turn** | **PASS** |
| **C1** | MiniLM Bi-Encoder | 59.11% | **FAIL** | 1.17 turns | **FAIL** |
| **C2** | Distilled Semantic ModernBERT | 41.67% | **FAIL** | 3.03 turns | **FAIL** |
| **C3** | Audio-First Prosodic DSP | 64.65% | **FAIL** | 5.00 turns | **FAIL** |
| **C4** | Hybrid Multimodal Fusion | 67.48% | **FAIL** | 2.63 turns | **FAIL** |
| **C5** | Structured Dialogue Act Slots | 19.07% | **FAIL** | 5.00 turns | **FAIL** |
| **C6** | Decoupled Log-Odds Projector | 67.65% | **FAIL** | 3.10 turns | **FAIL** |

---

## 2. Findings & Root-Cause Attribution

1. **Observation Noise Innovation Shocks:**
   In Phase 22-XR, Real Laya's continuous Kalman filter achieved $0.40\%$ flapping because Real Laya's observation updates were relatively smooth across conversational turns. In contrast, the zero-shot candidate encoders exhibited high turn-to-turn variance in their projected coordinates ($\mathbf{z}_{\text{obs}}$).
2. **Failure of Kalman Smoothing Under Raw Noisy Projections:**
   Because observation covariance $\mathbf{R}_t$ was not calibrated to heavily penalize high-frequency lexical shifts, the innovation $(\mathbf{z}_{\text{obs}} - \hat{\mathbf{z}})$ injected high-amplitude shocks into the continuous state, inducing high flapping ($41\% - 68\%$).
3. **Contradiction Recovery:**
   Candidate C1 recovered in $1.17\text{ turns}$, nearly meeting the $1.0\text{ turn}$ target, whereas discrete slot representations (C5) and audio-only features (C3) required up to $5.0\text{ turns}$ to re-center following a $180^\circ$ polarity inversion.
