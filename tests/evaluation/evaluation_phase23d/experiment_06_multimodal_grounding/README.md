# Experiment 06 — Multimodal Grounding & Embodiment Coupling

> **Track:** EXP-06  
> **Target Capability:** Continuous Sensor Grounding, Limbic Coupling & Token-Free Embodiment  
> **Status:** `[EVALUATION PROTOCOL SPECIFICATION]`  
> **Governing Documents:** `candidate_spec.md`, `metrics.md`, `research_baseline.md`

---

## 1. Scientific Context & Hypothesis Formulation

A foundational principle of Lucia is that **affect and embodiment are continuous dynamical states**, not text strings or prompt instructions (`AGENTS.md` §1). Lucia never declares *"I feel happy"*; instead, internal affective states $[P, A, D]$, somatic tension $\mathcal{T}$, and acoustic prosody directly modulate physical embodiment:
- Conversational latency $\Delta\tau_{\text{pace}}$
- Avatar blendshape weights (Live2D / VRM facial parameters)
- Sampling temperature and token budgets

In Phase 23-D, EXP-06 evaluates how candidate semantic representations bridge the gap between **continuous multimodal sensors** (eGeMAPS acoustic prosody, user input cadence, limbic ODE state) and **discrete concept structures**, and in turn drive embodiment without requiring an LLM as a cognitive mediator.

### 1.1 Testable Hypotheses

- **$H_1$ (Bidirectional Continuous-Discrete Dynamic Stability):**  
  Coupling continuous limbic states $[P, A, D]$ to candidate semantic nodes (via salience modulation) preserves closed-loop Lyapunov stability ($\lambda_{\max} \le 0.000$) and zero Decision Flapping Rate ($\text{DFR} = 0.0\%$) under deadband hysteresis ($\pm 0.08$).
- **$H_0$ (Dynamical Destabilization Null Hypothesis):**  
  Injecting discrete semantic state transitions back into the MT-LNN ODE triggers high-frequency limit cycles or runaway excitation ($\lambda_{\max} > 0.0$).
- **$H_2$ (V-UMR Continuous Grounding Advantage):**  
  Because V-UMR maintains metric vectors $\mathbf{z}_v \in \mathbb{R}^{32}$ for all concepts, incoming continuous sensory features can be directly assimilated via regularized Mahalanobis distance without discrete quantization, achieving Centroid Placement Accuracy ($\text{CPA}$) $\ge 0.90$.
- **$H_3$ (UMR-TPG Symbolic Grounding via Attribute Links):**  
  UMR-TPG grounds multimodal features by attaching continuous attribute nodes (`:intensity`, `:tempo`) to reified event frames, maintaining exact logical relationships while delegating metric similarity to auxiliary indexing.

---

## 2. Experimental Setup & Sensor Integration Protocol

### 2.1 Multimodal Ingestion Suite
Test fixtures provide synchronized continuous sensory vectors:
1. **Limbic ODE State:** Continuous $[P, A, D] \in [-1, 1]^3$, Energy $\mathcal{E} \in [0, 1]$, Cognitive Load $\mathcal{C} \in [0, 1]$.
2. **Acoustic Prosody Features (eGeMAPS):** Fundamental frequency mean/jitter ($F_0$), loudness/energy, and speech rate.
3. **Conversational Rhythm:** Inter-turn response latency $\Delta t_{\text{user}}$ and density.

### 2.2 Downstream Embodiment Generation
The candidate representation must drive physical embodiment parameters without an LLM:
- **Prosodic Modulation:** Target pitch shift $\Delta F_0$ and speaking rate factor $\alpha_{\text{rate}}$.
- **Facial Blendshapes:** Primary blendshape weights (e.g. `Blink`, `Smile_W`, `Brow_Inner_Up`).
- **Response Latency:** Somatic pacing delay $\Delta\tau_{\text{pace}} \in [0, 1200\text{ ms}]$.

---

## 3. Manipulated & Measured Variables

| Variable | Type | Description |
|---|---|---|
| **Affective Perturbation** | Independent | Stimulus vectors shifting PAD by $\pm 0.2$ to $\pm 0.6$ |
| **Acoustic Prosodic Style** | Independent | Agitated / High Pitch vs Calm / Low Pitch vs Neutral |
| **Max Lyapunov Exponent ($\lambda_{\max}$)** | Dependent | Asymptotic stability indicator (must be $\le 0.0$) |
| **Decision Flapping Rate ($\text{DFR}$)** | Dependent | Oscillations across semantic thresholds per turn |
| **Centroid Placement Accuracy ($\text{CPA}$)** | Dependent | Accuracy in mapping continuous sensor vectors to ontology concepts |
| **Embodiment Correlation ($r_{\text{embodiment}}$)** | Dependent | Pearson correlation between affective state and blendshape output |

---

## 4. Falsification Criteria & Thresholds

| Candidate | Metric | Passing Threshold | Falsification Boundary (Failure) | Epistemological Status |
|---|---|---|---|---|
| **All** | Max Lyapunov Exponent ($\lambda_{\max}$) | $\le 0.000$ | $> 0.000$ (Instability / runaway) | **Mathematical Proof / Benchmark** |
| **All** | Decision Flapping Rate ($\text{DFR}$) | **$0.0\%$** | $> 0.0\%$ under static input | **Validated Invariant** |
| **V-UMR** | Centroid Placement Accuracy ($\text{CPA}$) | $\ge 0.90$ | $< 0.80$ | **Testable Benchmark** |
| **UMR-TPG** | Embodiment Correlation ($r_{\text{embodiment}}$) | $\ge 0.85$ | $< 0.70$ | **Engineering Hypothesis** |
| **DRS-Graph** | Quantization Discontinuity | Low | Severe step discontinuities | **Expected Limitation** |

> [!NOTE]
> **Open / Unverified Boundary:**  
> Direct zero-shot grounding of raw, unaligned acoustic waveforms into semantic concept graphs without an intermediate phonological or lexical transducer remains **`[Open / Unverified]`**. The evaluation protocol uses standardized acoustic feature vectors (eGeMAPS) as inputs.
