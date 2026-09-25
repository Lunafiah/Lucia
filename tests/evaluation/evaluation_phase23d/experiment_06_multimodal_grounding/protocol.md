# Phase 23-D — EXP-06: Multimodal Grounding & Token-Free Embodiment Protocol

> **Experiment ID:** EXP-06  
> **Status:** `[EVALUATION PROTOCOL SPECIFICATION / AUDITED]`  
> **Governance Authority:** `AGENTS.md` §0, §6, §7; Phase 23-D Evaluation Scaffold  
> **Target Subsystems:** Semantic Substrates (UMR-TPG, V-UMR, DRS-Graph)  
> **Production Boundary:** Evaluation experiment only. Zero modifications to `src/core/**`.

---

## 1. Experimental Objective

The objective of **EXP-06** is to empirically test whether continuous multimodal sensory streams (continuous limbic ODE states $[P, A, D]$, eGeMAPS acoustic prosody, conversational rhythm) can be transformed into language-independent semantic states and drive physical embodiment **without relying on a natural-language token sequence** as the cognitive substrate.

Specifically, the experiment tests:
```text
continuous multimodal signals
        ↓
feature representation
        ↓
semantic grounding
        ↓
candidate semantic substrate
        ↓
stable concept / relation state
        ↓
downstream physical embodiment (blendshapes, prosody, pacing delay)
```

---

## 2. Token-Free Embodiment Constraint

1. **Strictly Token-Free:** No LLM, no natural-language tokenizers, no token sequences, and no text prompts are permitted as the cognitive substrate.
2. **Representational Grounding:** Semantic states must be represented directly in the candidate substrate (e.g. UMR reified event frames, V-UMR metric vectors, DRS box conditions).
3. **Decoupled Oracle Labels:** Symbolic concept identifiers (`AFFECT_JOY`, `RELATIONAL_PHILIA`) are used strictly as evaluation/oracle comparison targets and are never the cognitive representation being tested.

---

## 3. Evaluated Modalities & Test Scenarios

### Continuous Signals Evaluated
- **Limbic ODE State:** $[P, A, D] \in [-1, 1]^3$, Energy $\mathcal{E} \in [0, 1]$, Cognitive Load $\mathcal{C} \in [0, 1]$.
- **eGeMAPS Acoustic Prosody:** Fundamental frequency mean/jitter ($F_0$), loudness/energy, speech rate.
- **Conversational Cadence:** Somatic pacing delay and inter-turn cadence.

### Experimental Test Scenarios
1. **Single-Modality Grounding:** PAD only and Acoustic only mapping.
2. **Multimodal Convergence:** Synchronous PAD and acoustic streams converging into a single concept without duplication.
3. **Temporal Trajectory:** 10-step ODE limbic trajectory (Resting Philia $\to$ Stimulus excitation $\to$ Dissipative homeostatic relaxation).
4. **Conflicting Evidence:** Acoustic high arousal ($A=+0.85$) vs Limbic calm ($A=-0.35$) triggering explicit `EVIDENCE_CONFLICT` and high uncertainty score ($\ge 0.50$).
5. **Missing Modality / Dropout:** Graceful degradation when acoustic stream is absent (`None`).
6. **Perturbation Robustness:** Stability under Gaussian jitter within deadband.
7. **Boundary Oscillations:** Sinusoidal stimulus near threshold evaluating Decision Flapping Rate under deadband hysteresis ($\pm 0.08$).
8. **Semantically Unrelated Simultaneous Signals:** Environmental electrical mains hum (60Hz) isolated without spurious cross-modal conflict.

---

## 4. Software SLA Gates & Falsification Boundaries

| Metric | Target Gate | Falsification Boundary (Failure) | Status |
|---|---|---|---|
| **Centroid Placement Accuracy (CPA)** | $\ge 0.90$ | $< 0.80$ | **Empirical Gate** |
| **Cross-Modal Consistency (CMC)** | **$1.000$** | $< 1.000$ (Spurious duplicate nodes) | **Logical Invariant** |
| **Uncertainty / Conflict Preservation (UCP)** | **$1.000$** | $< 1.000$ (Arbitrary modality selection) | **Logical Invariant** |
| **Max Lyapunov Exponent ($\lambda_{\max}$)** | $\le 0.000$ | $> 0.000$ (Runaway instability) | **Mathematical Criterion** |
| **Decision Flapping Rate (DFR)** | **$0.0\%$** | $> 0.0\%$ under deadband hysteresis | **Limbic Invariant** |
| **Embodiment Correlation ($r_{\text{embodiment}}$)** | $\ge 0.85$ | $< 0.70$ | **Engineering Target** |
| **Token-Free Compliance** | **$100\%$** | $< 100\%$ (Token leakage) | **Canonical Invariant** |
| **GPU VRAM Impact** | **$0.0\text{ MB}$** | $> 0.0\text{ MB}$ | **Hardware Invariant** |

---

## 5. Hardware & Environmental Limitations

- **Physical 20W TDP Measurement:** Direct CPU package wattage measurement is unavailable without dedicated hardware power monitoring tools. This aspect is explicitly classified as **`UNVERIFIED`**.
- **Synthetic Signals Notice:** Results establish controlled multimodal grounding behavior under deterministic synthetic signals; they do not establish performance on real-world noisy sensor distributions.
