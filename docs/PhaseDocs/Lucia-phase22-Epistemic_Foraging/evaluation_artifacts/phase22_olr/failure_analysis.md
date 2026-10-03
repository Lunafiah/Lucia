# PHASE 22-OLR: SYSTEMATIC FAILURE ANALYSIS

> **Evaluation Phase:** Phase 22-OLR (Observation Layer Replacement Study)  
> **Status:** SCIENTIFIC DISSECTION OF CANDIDATE BOTTLENECKS  
> **Governance:** Pre-Registered Thresholds Kept Frozen — No Post-Hoc Threshold Lowering  

---

## 1. Executive Summary of Failure Modes

In Phase 22-OLR, six distinct candidate observation classes (C1 through C6) were evaluated against pre-registered acceptance criteria. While all candidates successfully solved the execution latency and resource bottleneck of Real Laya ($<30\text{ ms}$ vs $607\text{ ms}$, $<250\text{ MB}$ RAM vs $1.6\text{ GB}$), **no candidate achieved overall gate passage**.

This failure analysis isolates the root causes behind candidate rejections without altering thresholds or inventing ad-hoc fixes.

```text
                               CANDIDATE FAILURE TAXONOMY
                                          │
       ┌──────────────────────────────────┴──────────────────────────────────┐
       ▼                                                                     ▼
LATENT ALIGNMENT DEFECT                                              CALIBRATION DEFECT
(C1, C2, C3, C4, C5, C6)                                             (C1, C2, C5, C6)
- Negative R² across all models                                      - Overconfident probability mass
- Zero-shot cosine / keyword heuristic                               - Temperature uncalibrated on 
  fails to model subtle OU drift                                       conversational turns
- High MAE / coordinate distortion                                   - Extreme quantization error in C5
       │
       ▼
TEMPORAL DYNAMICS FLAPPING
(C1, C2, C3, C4, C6)
- High observation residual injects innovation shocks
- Fast observation noise updates overwhelm continuous inertia
```

---

## 2. Deep-Dive by Candidate Architecture Class

### 2.1 Candidate C1: Lightweight Multilingual Sentence Encoder (MiniLM Bi-Encoder)
* **Observed Failure:** $R^2 = -0.8507$, $ECE = 0.2367$, Flapping $= 62.99\%$.
* **Root Cause Mechanism:**
  - Semantic sentence embeddings excel at detecting broad topic similarity, but exhibit weak sensitivity to fine-grained emotional valence and relational dominance.
  - Projecting dense 384-dimensional embeddings onto 6 continuous latent axes via uncalibrated anchor vectors caused severe geometric distortion.
  - High observation noise shocks passed directly into the Kalman innovation step ($z_{\text{obs}} - z_{\text{prior}}$), triggering severe trajectory flapping ($62.99\%$).

### 2.2 Candidate C2 & C6: Distilled Semantic Encoder & Decoupled Projector
* **Observed Failure:** $R^2 = -0.5161$, $ECE = 0.2047$, Flapping $= 40.58\% - 69.19\%$, Recovery $= 3.3\text{ turns}$.
* **Root Cause Mechanism:**
  - While achieving the lowest Mean Absolute Error ($MAE = 0.1535 \le 0.30$, which passed gate), the zero-shot distilled act model plateaued on non-linear variance tracking ($R^2 < 0$).
  - When the user state drifts smoothly between turns via the Ornstein-Uhlenbeck process, discrete conversational act classifications emit constant step-function outputs until a threshold is crossed, creating severe quantization residuals against true continuous coordinates.
  - Adding the log-odds projection (C6) stabilized covariance estimation but could not recover unobserved continuous gradation from high-level conversational acts.

### 2.3 Candidate C3: Audio-First Acoustic / Prosodic DSP
* **Observed Failure:** $R^2 = -3.4698$, Flapping $= 66.75\%$, Contradiction Recovery $= 5.0\text{ turns}$.
* **Root Cause Mechanism:**
  - Candidate C3 demonstrated extraordinary calibration ($ECE = 0.0500$) and unprecedented speed ($3.82\text{ ms}$ CPU), but suffered complete coordinate blindness on factual and cognitive dimensions (cognitive load, attentional alignment).
  - Acoustic prosody (pitch, tempo, RMS energy) is highly sensitive to arousal and urgency, but completely incapable of distinguishing whether high arousal is driven by productive cognitive focus or hostile frustration.
  - Treating audio prosody as a standalone observation layer for 6D user state is an invalid architectural reduction.

### 2.4 Candidate C4: Hybrid Multimodal Observation
* **Observed Failure:** $R^2 = -0.7523$, Brier $= 1.6954$, Flapping $= 68.35\%$.
* **Root Cause Mechanism:**
  - Fusing text (C1) and audio (C3) yielded well-calibrated confidence ($ECE = 0.1284 \le 0.15$), confirming that multimodal cross-reinforcement mitigates unimodal uncertainty.
  - However, because both underlying modalities suffered from negative latent alignment ($R^2 < 0$), linear cross-modal fusion merely averaged two distorted coordinate projections, failing to achieve positive correlation with ground truth.

### 2.5 Candidate C5: Structured Semantic Observation (P23 Compatible)
* **Observed Failure:** $ECE = 0.8094$, $R^2 = -2.2710$, Recovery $= 5.0\text{ turns}$.
* **Root Cause Mechanism:**
  - Extracting discrete dialogue acts and slot keys introduces severe discretization boundaries.
  - Under continuous temporal drift, discrete slots remain completely unchanged over $80\%$ of turns, resulting in an empirical accuracy of only $3.05\%$ against fine continuous state variations.
  - Extreme overconfidence ($84\%$ confidence on discrete categorical slots) induced massive calibration error ($ECE = 0.8094$).

---

## 3. The Fundamental Scientific Bottleneck: Discretization vs. Continua

The failure of all six candidates to pass the $R^2 \ge 0.70$ alignment gate reveals a fundamental scientific finding for Lucia:

> **High-level conversational abstractions (dialogue acts, sentiment categories, intent labels, topic embeddings) lack the continuous gradation necessary to track a continuous psychological dynamical state ($z^* \in \mathbb{R}^6$) zero-shot.**

When observation primitives emit step-wise categorical probabilities, treating them as continuous measurements forces the Kalman filter to oscillate between stagnant step-values and violent innovation jumps.

---

## 4. Architectural Prescriptions for Next Research Iteration

To overcome this bottleneck in future research without violating governance:
1. **Supervised Regression Calibration:** Future candidate encoders must be trained directly on continuous regression targets rather than relying on zero-shot cosine projections or discrete classification heads.
2. **Explicit Kalman Innovation Deadband:** To prevent high-frequency flapping ($>40\%$), the filter must incorporate an innovation deadband ($\|z_{\text{obs}} - z_{\text{prior}}\| < \delta \implies K_t = 0$) when inputs are sparse or ambiguous.
3. **Preserve Multimodal Decoupling:** Multimodal fusion (C4) proved scientifically superior in calibration ($ECE = 0.1284$). When combined with continuous regression calibration, hybrid text-audio fusion remains the most promising long-term architectural direction.
