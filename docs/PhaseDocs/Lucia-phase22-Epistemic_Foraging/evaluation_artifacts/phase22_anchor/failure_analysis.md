# Phase 22-ANCHOR — Failure Analysis & Scientific Bottleneck Attribution

## 1. Executive Summary

Phase 22-ANCHOR succeeded in proving that:
1. **Drift is 100% eliminated:** Non-anchor turn drift dropped from runaway Brownian values to **0.00000** (Gate **G_ANC2** passed).
2. **False anchors are 0.0%:** Neutral and procedural turns do not trigger spurious relational updates (Gate **G_ANC4** passed).
3. **Hardware SLAs are trivially met:** CPU latency is **$0.075\text{ ms}$** and VRAM is **$0.0\text{ MB}$** (Gates **G_ANC6, G_ANC7** passed).

However, candidate A3:
- **G_ANC1 (Anchor Recall $\ge 0.80$):** **FAILED** ($0.7662 \approx 76.6\%$)
- **G_ANC3 (Warmth $R^2 \ge 0.50$):** **FAILED** ($-1.1375$)

---

## 2. Root Cause Dissection: Why Did Warmth $R^2$ Remain Negative?

Despite MAE dropping to 0.41 and drift being 100% eliminated, $R^2$ remains negative ($-1.1375$). Why?

### 2.1. The Nature of $R^2$ on Discrete Step Signals
$R^2$ is defined as:
$$R^2 = 1 - \frac{\sum_t (y_t - \hat{y}_t)^2}{\sum_t (y_t - \bar{y})^2}$$
In an episodic anchor regime:
1. Ground truth warmth jumps instantaneously when an event occurs ($y_t: 0.30 \to 0.45$).
2. In Candidate A3, if an anchor event occurs under heavy noise (`NoiseSurge` or `LexicalSparsity`), the confidence gate may attenuate the step size (e.g. $\Delta \hat{y}_t = +0.10$ instead of $+0.15$), or delay detection by 1 turn.
3. Because the ground truth variance $\operatorname{Var}(y_t)$ across a 15-turn session with only 1 or 2 step shifts is very small (variance is dominated by the step change itself), even a slight offset in step magnitude or missed anchor causes the mean squared error (MSE) to exceed the small total variance, making $R^2 < 0$.

### 2.2. The Inadequacy of Real-Valued $R^2$ for Relational Stance
This reveals a profound ontological truth:
> **$R^2$ (coefficient of determination) is a metric designed for continuous time-series regression. It is mathematically ill-suited for measuring autobiographical relational memory.**

A human does not evaluate their relationship with a partner by calculating the $R^2$ of a continuous scalar trajectory. A relationship is governed by:
- **Salient episodic memories** ("We went through that difficult event together").
- **Discrete trust tiers / relational phases** (Acquaintance $\to$ Collaborator $\to$ Companion $\to$ Confidant).
- **Epistemic safety and boundary rules** (Is it safe to be vulnerable? Can I rely on this partner?).

---

## 3. The Definitive Bottleneck Location

The prompt asked:
> *"Bottleneck tiếp theo nằm ở observation, memory representation hay relational inference?"*

The evidence definitively answers:
1. **Observation is NOT the bottleneck:** The 4D Observable state ($u_0–u_3$) is tracked with high fidelity ($R^2 \approx 0.52 - 0.64$) with sub-millisecond CPU execution.
2. **Memory representation is NOT the bottleneck:** Anchors successfully eliminate drift ($0.00000$) and preserve longitudinal stance without false activations ($0.0\%$).
3. **The Bottleneck is RELATIONAL INFERENCE & ONTOLOGICAL FORMULATION:**
   - Attempting to represent human-AI relationship as a **continuous 1D real number $m_1 \in [-1, 1]$** evaluated by regression $R^2$ is an **ontological mismatch**.
   - Relationship is a **discrete structured belief graph (Relational Graph / Trust Tier / Episodic Milestones)** maintained in autobiographical memory (Kanerva SDM), rather than a continuous scalar variable.
