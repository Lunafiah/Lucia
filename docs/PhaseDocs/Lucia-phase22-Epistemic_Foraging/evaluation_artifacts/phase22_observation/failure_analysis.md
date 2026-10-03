# PHASE 22 OBSERVATION LAYER STUDY: SYSTEMATIC FAILURE ANALYSIS

> **Evaluation Phase:** Phase 22 Observation Layer Replacement Study  
> **Status:** SCIENTIFIC DISSECTION OF CANDIDATE BOTTLENECKS  
> **Governance:** Pre-Registered Thresholds Kept Frozen (No Post-Hoc Threshold Modification)  

---

## 1. Disentanglement: Observation Layer Failures vs. Downstream Dynamics

A primary objective of this study was to isolate whether observed defects stem from the **upstream Observation Layer** or the **downstream Continuous Filter**:

```text
                      UPSTREAM OBSERVATION LAYER                     DOWNSTREAM FILTER
                   (Where the actual failure occurs)           (Mathematically Sound)
                                  │                                       │
            ┌─────────────────────┴─────────────────────┐                 │
            ▼                                           ▼                 ▼
   COORDINATE MISMATCH                         CALIBRATION SKEW       TRAJECTORY DENSITY
(R² in falsification region)                   (ECE in C1/C2/C5)       (100% Coverage)
- Zero-shot cosine & keyword heads             - Softmax over-        - Lyapunov diffusion
  cannot model subtle continuous OU drift        concentration on       forecasts remain fully
- High MAE residual causes innovation shock      lexical heads          calibrated across all C1-C6
```

---

## 2. Failure Analysis by Architectural Class

### Candidate C1: Lightweight Multilingual Sentence Encoder (MiniLM Bi-Encoder)
- **Observed Metrics:** $R^2 = -0.9706$, $ECE = 0.2517$, Flapping $= 59.11\%$.
- **Failure Cause:** Sentence bi-encoders map semantic proximity, not continuous psychological parameters. Projecting dense embeddings onto anchor vectors fails to track smooth inter-turn drift.

### Candidate C2 & C6: Distilled Semantic Encoder & Decoupled Projector
- **Observed Metrics:** $R^2 = -0.5750$, $MAE = 0.1568$, Flapping $= 41.67\% - 67.65\%$.
- **Failure Cause:** Distilled conversational act heads emit discrete categorical step-functions. When true user state shifts continuously, the step-function output creates high variance residuals ($R^2 < 0$), though $MAE \le 0.16$ remains bounded.

### Candidate C3: Audio-First Prosodic DSP
- **Observed Metrics:** $ECE = 0.0783$ (Passed), $R^2 = -3.6096$, Flapping $= 64.65\%$.
- **Failure Cause:** While acoustic features (pitch, tempo, RMS energy) exhibit exceptional calibration and sub-4ms latency, audio prosody alone cannot disambiguate cognitive focus from emotional frustration.

### Candidate C4: Hybrid Multimodal Observation
- **Observed Metrics:** $ECE = 0.1448$ (Passed), $R^2 = -0.7606$, Flapping $= 67.48\%$.
- **Failure Cause:** Fusing text embeddings and audio features resolved probability overconfidence, but linear cross-modal fusion could not resolve the underlying coordinate misalignment present in both modalities.

### Candidate C5: Structured Semantic Observation
- **Observed Metrics:** $ECE = 0.8122$, $R^2 = -2.2530$, Recovery $= 5.0\text{ turns}$.
- **Failure Cause:** Quantization into discrete dialogue slots destroys continuous variation.
