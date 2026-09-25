# State Formation & Latent Decoupling Report — Phase 22-SSF

## 1. Executive Summary

Phase 22-SSF evaluated the core architectural hypothesis:
> **"Can Semantic State Formation (SSF) successfully decouple fast observable states ($z_0–z_3$) from slow internally accumulated states ($z_4–z_5$), avoiding the errors of direct observation inversion?"**

---

## 2. Quantitative Comparison: Raw vs SSF vs Oracle

Measured on held-out seeds (1024, 2026) across all 6 stress regimes:

| Model Architecture | Overall $R^2$ | Fast States $R^2$ ($z_0–z_3$) | Slow States $R^2$ ($z_4–z_5$) | MAE | MSE | P50 Latency |
| :--- | :---: | :---: | :---: | :---: | :---: | :---: |
| **Raw Baseline Model** | **0.7003** | 0.5716 | **+0.4402** | **0.0807** | **0.0156** | 0.023 ms |
| **Decoupled SSF Model** | 0.4767 | 0.5716 | **-0.9446** | 0.1072 | 0.0272 | **0.0349 ms** |
| **Oracle Control** | **0.9531** | **0.9531** | **0.9531** | **0.0391** | **0.0024** | 0.023 ms |

---

## 3. Dimension-Wise Performance Breakdown

| Coordinate Name | Semantic Identity | Partition | Raw Baseline $R^2$ | Decoupled SSF $R^2$ | Empirical Diagnosis |
| :--- | :--- | :---: | :---: | :---: | :--- |
| **$z_0$ Cognitive Load** | Working memory demand | FAST | **0.6767** | **0.6767** | Highly identifiable; matches raw baseline |
| **$z_1$ Affective Valence** | Affective polarity | FAST | **0.6333** | **0.6333** | Highly identifiable; robust tracking |
| **$z_2$ Agency** | User autonomy & dominance | FAST | **0.4638** | **0.4638** | Moderately identifiable via latency/interruption |
| **$z_3$ Urgency** | Temporal task pressure | FAST | **0.5127** | **0.5127** | Moderately identifiable via cadence/energy |
| **$z_4$ Fatigue** | Metabolic exhaustion | SLOW | **+0.5807** | **-1.6089** | **Decoupled integration drifted from target** |
| **$z_5$ Warmth** | Interpersonal affinity | SLOW | **+0.2997** | **-0.2803** | **Decoupled integration drifted from target** |

---

## 4. Key Discovery: The Autonomous Accumulation Paradox

1. **Fast State Parity:**
   - On the fast observable partition ($z_0, z_1, z_2, z_3$), the decoupled SSF layer achieves exact parity with the raw baseline ($R^2_{\text{fast}} = 0.5716$). Fast dimensions are effectively captured by learned linear projection from multimodal inputs.

2. **The Slow Drift Failure:**
   - On the slow partition ($z_4, z_5$), the decoupled model attempted to track fatigue and warmth via autonomous leaky accumulation based on proxy rules (cognitive load accumulation and valence integration) without direct regression supervision.
   - Because the synthetic environment's ground-truth state evolves via its own independent Ornstein-Uhlenbeck drift ($dz = -\gamma(z - \mu)dt + \sigma dW$), an autonomous forward accumulator without observational error correction accumulates phase error and mean drift over extended dialogue turns.
   - Consequently, slow state alignment collapsed to **$R^2_{\text{slow}} = -0.9446$** ($z_4 = -1.6089, z_5 = -0.2803$).
   - In contrast, the raw baseline—which directly regressed observation features against all 6 dimensions—achieved **$R^2_{\text{slow}} = +0.4402$** ($z_4 = +0.5807$).

3. **Definitive Conclusion:**
   - **Hypothesis REJECTED as implemented:** Slow internal states cannot be maintained purely open-loop without observational feedback.
   - A valid state estimator requires **Kalman-style observational correction**: an internal dynamical prior must be continuously conditioned on sensory prediction residuals.
