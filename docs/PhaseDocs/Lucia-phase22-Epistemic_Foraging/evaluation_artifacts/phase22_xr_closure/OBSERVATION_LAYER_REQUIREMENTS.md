# OBSERVATION LAYER REQUIREMENTS: RESEARCH SPECIFICATION & ACCEPTANCE CRITERIA

> **Document Type:** Research Criteria Specification  
> **Status:** FROZEN REQUIREMENTS BASELINE  
> **Applicability:** Observation Layer Replacement Study (Successor to Phase 22-XR)  
> **Target Subsystem:** Continuous Observation Extraction & Belief Projection  

---

## 1. Overview & Architectural Role

The **Observation Layer** sits at the perceptual boundary of Lucia's cognitive architecture. Its sole responsibility is to translate raw conversational inputs (text utterances, prosodic audio, interaction timings) into a calibrated, temporally coherent semantic evidence vector $\mathbf{y}_t \in \mathbb{R}^{d_y}$ accompanied by an observation uncertainty matrix $\mathbf{R}_t$.

The continuous user-state filter consumes $(\mathbf{y}_t, \mathbf{R}_t)$ to update its internal belief state $\mathbf{z}(t) \in \mathbb{R}^6$ and covariance $\boldsymbol{\Sigma}(t)$.

```text
User Utterance / Audio
          │
          ▼
┌────────────────────────────────────────────────────────┐
│                   OBSERVATION LAYER                    │
│                                                        │
│  [Perceptual Encoder] ──> [Calibration / Projection]   │
└────────────────────────────────────────────────────────┘
          │
          │ Evidence: (y_t, R_t)
          ▼
┌────────────────────────────────────────────────────────┐
│            CONTINUOUS COGNITIVE DYNAMICS               │
│                                                        │
│   Continuous Prior (ODE) + Discrete Update (Kalman)    │
│            State: z(t) in R^6, Sigma(t) in R^(6x6)     │
└────────────────────────────────────────────────────────┘
```

To prevent the performance and calibration bottlenecks observed in Real Laya (ModernBERT-large 421M), any candidate observation architecture must satisfy the frozen requirements defined below.

---

## 2. Measurable Requirements Ledger

### 2.1 Calibration Requirements
Overconfident or poorly calibrated observations corrupt the continuous Kalman gain, causing excessive belief jumps or ignoring contradictory evidence.

* **Expected Calibration Error ($ECE$):**
  $$\text{Target: } ECE \le 0.10 \quad (\text{Threshold: } \le 0.15)$$
  Evaluated over 10 uniform reliability bins on validation utterances.
* **Brier Score:**
  $$\text{Target: } \text{Brier} \le 0.08$$
* **Negative Log-Likelihood ($NLL$):**
  Monitored to detect probability over-concentration and catastrophic overconfidence.

### 2.2 Alignment Requirements
The semantic evidence vector $\mathbf{y}_t$ must correlate strongly with the underlying continuous latent dimensions $\mathbf{z}^* \in \mathbb{R}^6$ (cognitive load, valence, dominance, communicative intimacy, openness, uncertainty).

* **Coefficient of Determination ($R^2$):**
  $$\text{Target: } R^2 \ge 0.85 \quad (\text{Threshold: } R^2 \ge 0.70)$$
  Evaluated between projected observation states $\hat{\mathbf{z}} = g^{-1}(\mathbf{y})$ and true latent states $\mathbf{z}^*$.
* **Mean Absolute Error ($MAE$):**
  $$\text{Target: } MAE \le 0.20 \quad (\text{on standardized } [-1, 1] \text{ scale})$$
* **Mean Squared Error ($MSE$):**
  $$\text{Target: } MSE \le 0.08$$

### 2.3 Temporal Stability & Dynamics Requirements
Continuous user modeling must guarantee smooth conversational tracking without belief jitter.

* **Continuous Belief Flapping:**
  $$\text{Target: } \text{Flapping} \le 2.0\% \quad (\text{Hard Upper Bound: } \le 9.5\%)$$
  Defined as sign or regime reversals occurring within $\le 2$ consecutive turns under steady input conditions.
* **Contradiction Recovery:**
  $$\text{Target: } \le 1.0\text{ turn}$$
  When presented with an explicit semantic shift or contradiction, the belief mean must adapt within $\le 1$ observation update without divergence.
* **Spectral Bound & Stability:**
  Continuous ODE transition matrix $\mathbf{F}$ must satisfy Lyapunov stability ($\text{Re}(\lambda_i(\mathbf{F})) < 0$).

### 2.4 Latency & Execution Budget (20-Watt Edge Target)
Lucia operates entirely on local consumer hardware. The observation layer must leave ample CPU/GPU headroom for language generation, limbic integration, and avatar rendering.

* **Observation Neural Inference Latency ($T_{\text{obs}}$):**
  - **P50:** $\le 50.0\text{ ms}$ (CPU)
  - **P95:** $\le 100.0\text{ ms}$ (CPU)
  - **P99:** $\le 150.0\text{ ms}$ (CPU)
  *(Real Laya baseline was $607.67\text{ ms}$; target is a $>6\times$ speedup).*
* **Continuous Filter & Projection Latency ($T_{\text{filter}}$):**
  - **P50:** $\le 1.0\text{ ms}$
  - **P99:** $\le 5.0\text{ ms}$
* **Total Observation-to-Belief Pipeline Latency ($T_{\text{total}} = T_{\text{obs}} + T_{\text{filter}}$):**
  - **P50:** $\le 60.0\text{ ms}$
  - **P95:** $\le 120.0\text{ ms}$

### 2.5 Resource Constraints
* **Model Parameter Count ($N_{\text{params}}$):**
  $$\text{Target: } \le 100\text{M parameters} \quad (\text{Preferred: } 20\text{M} - 60\text{M})$$
* **Host RAM Footprint:**
  $$\text{Target: } \le 500\text{ MB additional RAM}$$
* **GPU VRAM Impact:**
  $$\text{Target: } 0\text{ MB VRAM (Strict CPU execution)}$$
  *(All available VRAM is reserved for the primary GGUF language model).*

### 2.6 Multilingual Robustness
Lucia interacts natively across multiple languages. The observation encoder must extract stable semantic evidence across:
1. **English (EN)** (Core baseline)
2. **Vietnamese (VI)** (Primary conversational target)
3. **Japanese (JA)** (East-Asian relational structure)

* **Multilingual Consistency ($R^2_{\text{multi}} / R^2_{\text{EN}}$):**
  $$\text{Target: } \frac{R^2_{\text{VI}}}{R^2_{\text{EN}}} \ge 0.85, \quad \frac{R^2_{\text{JA}}}{R^2_{\text{EN}}} \ge 0.85$$
* Cross-lingual ECE degradation must not exceed $+0.05$ relative to English.

---

## 3. Summary Compliance Gate Table

| Dimension | Metric | Hard Acceptance Gate | Preferred Target |
|:---|:---|:---:|:---:|
| **Calibration** | $ECE$ | $\le 0.15$ | $\le 0.10$ |
| | Brier Score | $\le 0.12$ | $\le 0.08$ |
| **Alignment** | Latent $R^2$ | $\ge 0.70$ | $\ge 0.85$ |
| | Latent $MAE$ | $\le 0.30$ | $\le 0.20$ |
| **Stability** | Flapping Rate | $\le 9.5\%$ | $\le 2.0\%$ |
| | Contradiction Recovery | $\le 1.0\text{ turn}$ | $\le 1.0\text{ turn}$ |
| **Latency** | Observation CPU P50 | $\le 100.0\text{ ms}$ | $\le 50.0\text{ ms}$ |
| | Observation CPU P95 | $\le 200.0\text{ ms}$ | $\le 100.0\text{ ms}$ |
| | Total Pipeline P50 | $\le 120.0\text{ ms}$ | $\le 60.0\text{ ms}$ |
| **Resources** | Parameter Count | $\le 150\text{M}$ | $20\text{M} - 80\text{M}$ |
| | RAM Footprint | $\le 1.0\text{ GB}$ | $\le 500\text{ MB}$ |
| | GPU VRAM | $0\text{ MB}$ (CPU native) | $0\text{ MB}$ |
| **Multilingual**| VI/EN Performance Ratio | $\ge 0.75$ | $\ge 0.85$ |
| | JA/EN Performance Ratio | $\ge 0.75$ | $\ge 0.85$ |

These criteria are frozen and must govern all experimental trials in the Observation Layer Replacement Study.
