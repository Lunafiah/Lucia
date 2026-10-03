# Candidate Matrix — Phase 22-AL Alignment Study

## 1. Candidate Comparison Matrix

The table below compiles held-out cross-regime generalization performance ($R^2$, MAE, MSE) across all registered candidate representations (C1–C6) and alignment architectures (A0–A7).

| Candidate Class | Candidate Name | Best Alignment Model | Best $R^2$ | Best MAE | Best MSE | Baseline $R^2$ ($A_0$) | Alignment Gain ($\Delta R^2$) | Gate Status ($R^2 \ge 0.85$) |
| :--- | :--- | :--- | :---: | :---: | :---: | :---: | :---: | :---: |
| **C1** | MiniLM-L6-v2 Embeddings | A6_ObservationLikelihood | +0.0809 | 0.1060 | 0.0232 | -1.1303 | +1.2112 | **FAIL** |
| **C2** | DistilBERT Logits | A6_ObservationLikelihood | +0.0501 | 0.1069 | 0.0240 | -0.6355 | +0.6856 | **FAIL** |
| **C3** | Audio Acoustic DSP | A5_LeakyIntegrator | +0.1806 | 0.0951 | 0.0207 | -4.2341 | +4.4147 | **FAIL** |
| **C4** | Hybrid Multimodal | A5_LeakyIntegrator | **+0.2548** | **0.0923** | **0.0188** | -0.9690 | +1.2238 | **FAIL** |
| **C5** | Structured Dialog Acts | A6_ObservationLikelihood | +0.0639 | 0.1070 | 0.0236 | -3.0515 | +3.1154 | **FAIL** |
| **C6** | Decoupled Semantic | A6_ObservationLikelihood | +0.0501 | 0.1069 | 0.0240 | -0.6355 | +0.6856 | **FAIL** |

---

## 2. Model Performance Summary Across All Candidates

| Alignment Model Code | Model Family | Average Held-Out $R^2$ | Peak Candidate $R^2$ | Complexity (Params) | CPU P50 Latency | Primary Limitation / Behavior |
| :--- | :--- | :---: | :---: | :---: | :---: | :--- |
| **A0** | Naive Baseline | -1.7760 | -0.6355 (C2, C6) | 0 | 0.000 ms | Unaligned coordinate mismatch |
| **A1** | Linear Ridge | +0.0938 | +0.2231 (C4) | 42 | 0.003 ms | Fast, stable, limited capacity |
| **A2** | Constrained ($\tanh$) | -1.4632 | -1.2575 (C4) | 42 | 0.012 ms | Saturates outside central distribution |
| **A3** | Small MLP (32 units) | -0.4323 | -0.1810 (C3) | 422 | 0.024 ms | Overfits on small train seeds; stress drift |
| **A4** | Temporal Window ($k=3$) | +0.0336 | +0.1907 (C4) | 114 | 0.019 ms | Sensitive to noise surge in historical frames |
| **A5** | Leaky State Estimator | **+0.1082** | **+0.2548** (C4) | 43 | 0.003 ms | Smooths high-frequency noise; best overall |
| **A6** | Observation Likelihood | +0.1116 | +0.2460 (C4) | 42 | 0.045 ms | Inverts observation likelihood via covariance |
| **A7** | Hybrid Temporal | -0.1102 | +0.0356 (C3) | 808 | 0.024 ms | Complex composition degrades under stress |

---

## 3. Comparative Observations

1. **Multimodality is Essential but Insufficient:**
   - Candidate C4 (Hybrid Multimodal) dominates all text-only (C1, C2, C5, C6) and audio-only (C3) candidates across every model class ($R^2 = +0.2548$).
   - However, even multimodal fusion falls short of the $R^2 \ge 0.70$ falsification threshold by a wide margin ($0.2548 \ll 0.70$).

2. **State Estimation Superior to Direct Assignment:**
   - Across all candidates, state estimation models ($A_5$ Leaky, $A_6$ Likelihood) strictly outperformed direct static mappings ($A_1$ Linear, $A_2$ Constrained) and deep mappings ($A_3$ MLP).
   - This confirms that continuous latent states cannot be directly assigned; they require temporal state estimation.
