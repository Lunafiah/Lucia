# Phase 22 H1 — Precision-Weighted & Directional Measurement Architecture Research

> **Status:** RESEARCH EVIDENCE ONLY — NOT AUTHORIZED FOR PRODUCTION PROMOTION  
> **Governance:** Architecture Gate is **STRICTLY LOCKED** | Protocol v1.5 is **NOT AUTHORIZED**  
> **Production Mutation:** 0 modifications to `src/core/**`  
> **Genesis Gate:** `data/profile.json` remains bit-exact `{"is_onboarded": false}`  
> **Historical Datasets:** Immutable (v1.4, Path C preserved bit-exact)  
> **Date:** September 2026  
> **Artifact Type:** Research Evaluation Report (Phase 22 H1)

---

## 1. Executive Summary

This study delivers a formal, research-only empirical and analytical investigation into **precision-weighted and directional measurement architectures** for Phase 22 H1. Building directly upon the preceding Measurement Architecture Study (which established that scalar surprise $S = \|\hat{\mathbf{p}}_T - \mathbf{p}_T\|_2$ demonstrably omits directional/component information while leaving its architectural unacceptability unresolved), this investigation evaluates whether a future measurement architecture should:
1. Retain scalar $S$ unchanged,
2. Augment scalar $S$ with component/directional information,
3. Replace scalar $S$ with a vector-aware representation, or
4. Remain undecided because the available evidence is insufficient.

### Primary Empirical Findings:
1. **Representation Matrix (RQ1)**: Characterized candidate representations M0–M5 across 10 evaluation dimensions. Confirmed that M2 (displacement magnitude + direction) and M3 (residual magnitude + direction) require 4 stored floating-point elements but possess exactly **3 effective degrees of freedom** due to the unit-norm constraint $\|\hat{\mathbf{v}}\| = 1$. In accordance with governance, no composite ranking score was computed.
2. **Precision Weighting vs. Collapse (RQ2)**: Evaluated four predefined, non-data-fitted precision structures ($\boldsymbol{\Pi}_0–\boldsymbol{\Pi}_3$).
   - Canonical isotropic $\boldsymbol{\Pi}_0 = \mathbf{I}_3$ produces 358 Medium–High cross-tier collapse pairs ($|S_{\text{Med}} - S_{\text{High}}| \le 0.02$) at $T=12$ (1.20s), failing Gate 2 ($\Delta_{\text{HM}} = +0.1069 < 0.15$).
   - Predefined exploratory theoretical candidate $\boldsymbol{\Pi}_1 = \text{diag}(1.0, 4.0, 1.0)$ achieves dual Gate 2 separation ($\Delta_{\text{ML}} = +0.1524, \Delta_{\text{HM}} = +0.2801$) by selectively amplifying the Arousal axis. However, this is an unvalidated exploratory formula that discards Pleasure and does NOT constitute evidence for higher physiological importance of Arousal.
   - Fixed geometric normalization metric $\boldsymbol{\Pi}_2 = \text{diag}(1.778, 1.108, 1.108)$ (derived from Philia resting headroom $h_i^{-2}$) fails Gate 2 ($\Delta_{\text{HM}} = +0.1343 < 0.15$) and leaves 138 cross-tier collapses.
   - Fixed non-diagonal metric $\boldsymbol{\Pi}_3$ (coupled limbic Valence–Arousal drag $\rho_{PA} = -0.3$) fails Gate 2 ($\Delta_{\text{HM}} = +0.1121 < 0.15$) with 1,940 cross-tier collapses (24.0%).
3. **Component-Wise Separation (RQ3)**: Independent component analysis demonstrates extreme divergence across axes. At $T=12$, Arousal exhibits massive separation between High and Medium stimuli ($+0.2755$, $95\%$ CI: $[+0.2671, +0.2840]$, Cohen's $d_{\text{HM}} = +9.55$), whereas Pleasure separates in the opposite direction ($-0.3179$, $95\%$ CI: $[-0.4172, -0.2186]$, Cohen's $d_{\text{HM}} = -0.94$). Summing squared differences under Euclidean scalarization cancels out these opposing signals.
4. **Magnitude-Matched Directional Persistence (RQ4)**: Within magnitude-matched pairs ($|S_i - S_j| \le 0.02$), angular divergence remains substantial across all conversational exposures ($T=1$ to $T=25$, $61.2^\circ$ to $103.7^\circ$). Evaluated as: **EVIDENCE CONSISTENT WITH DIRECTIONAL/COMPONENT INFORMATION PERSISTING AFTER MAGNITUDE MATCHING**.
5. **Displacement vs. Prediction Residual (RQ5)**: Under unadapted persistence beliefs ($\mathbf{A}=\mathbf{I}, \mathbf{b}=\mathbf{0}$), prediction residual $\mathbf{r}_T^{(0)}$ is mathematically identical to negative displacement $-\Delta \mathbf{p}$ ($\max |\|\mathbf{r}_T^{(0)}\| - \|\Delta\mathbf{p}\|| < 10^{-9}$). Under online-adapted beliefs, $\mathbf{r}_T$ diverges from $\Delta \mathbf{p}$ ($179.5^\circ$ angular separation at $T=12$), establishing that prediction residuals capture generative expectation failure rather than raw bodily movement.
6. **Homeostatic Relevance (RQ6)**: Completed an evidence inventory and conceptual compatibility analysis. Classified as **B — Plausible future research direction, but currently unsupported by validated production evidence**. Zero parameter fitting or biological validation was claimed.
7. **Conversational Timescale (RQ7)**: M0 does not satisfy the current preregistered dual Gate 2 thresholds at $T \le 25$ under frozen G1/current dynamics. Representations M1–M4 achieve pronounced separation by $T = 1$ to $2$ ($0.10\text{s}$ to $0.20\text{s}$).
8. **Architectural Semantics (RQ8)**: Clarified that physiological surprise ($\mathbf{r}_T \neq \mathbf{0}$) and epistemic uncertainty ($H(P), H_{\text{Ecphory}}$) serve decoupled functional roles.

### Final Conclusion:
Concluded as **State B — Direction/Component Information Demonstrably Omitted Under Scalar S**:
> *Scalar S demonstrably omits directional/component information; whether that omission is architecturally unacceptable remains unresolved.*

---

## 2. Governance and Scope

### 2.1 Governance Guardrails
In strict accordance with `AGENTS.md` and Phase 22 project governance:
- **Research Boundary**: All code and results reside strictly in `tests/evaluation_phase22/` and `docs/specs/Lucia-phase22-Epistemic_Foraging/`.
- **Zero Production Mutations**: `src/core/**` has exactly **0 modifications**.
- **Genesis Gate Protection**: `data/profile.json` remains bit-exact `{"is_onboarded": false}`.
- **Protocol Authorization**: Protocol v1.5 is **NOT AUTHORIZED**.
- **Architecture Gate**: **STRICTLY LOCKED**.
- **Threshold Integrity**: Preregistered Gate 2 thresholds ($\Delta_{\text{ML}} \ge 0.10, \Delta_{\text{HM}} \ge 0.15$) remain frozen. No threshold adjustment was performed.
- **Data-Fitting Prohibition**: Precision structures $\boldsymbol{\Pi}$ were predefined prior to analysis and not fitted to optimize Gate 2 outcomes.

---

## 3. Research Questions

This study addresses eight formal research questions:
- **RQ1**: What information does each representation (M0–M5) retain across dimensionality, degrees of freedom, sign/polarity, component, angular, prediction error, baseline dependence, transition dependence, interpretability, and computational cost?
- **RQ2**: Does predefined precision weighting ($\boldsymbol{\Pi}_0–\boldsymbol{\Pi}_3$) resolve the scalar collapse observed in $|S_{\text{Med}} - S_{\text{High}}| \le 0.02$?
- **RQ3**: What component-wise information is carried by Pleasure, Arousal, and Dominance independently?
- **RQ4**: Does directional and component information persist within magnitude-matched observations ($|S_i - S_j| \le 0.02$)?
- **RQ5**: How do state displacement ($\Delta \mathbf{p} = \mathbf{p}_T - \mathbf{p}_0$) and prediction residual ($\mathbf{r}_T = \hat{\mathbf{p}}_T - \mathbf{p}_T$) differ mathematically and empirically under unadapted vs. online-adapted generative beliefs?
- **RQ6**: What is the architectural evidence inventory and conceptual compatibility for coupling homeostatic/metabolic state into measurement precision?
- **RQ7**: Can candidate representations preserve meaningful epistemic distinction across realistic conversational exposure durations ($T \in \{1, 2, 4, 8, 12, 16, 25\}$) without lowering preregistered thresholds?
- **RQ8**: How does scalar vs. vector measurement affect the architectural distinction between physiological surprise and epistemic uncertainty?

---

## 4. Measurement Definitions

We evaluate six candidate representations:

### M0 — Canonical Scalar Surprise
$$S = \|\mathbf{r}_T\|_2 = \sqrt{r_P^2 + r_A^2 + r_D^2}$$
where $\mathbf{r}_T = \hat{\mathbf{p}}_T - \mathbf{p}_T$. In fresh evaluation from resting baseline $\mathbf{p}_0$ under initial beliefs ($\mathbf{A}=\mathbf{I}, \mathbf{b}=\mathbf{0}$), this degenerates to $\|\mathbf{p}_T - \mathbf{p}_0\|_2$.

### M1 — Raw PAD Displacement Vector
$$\Delta \mathbf{p} = \mathbf{p}_T - \mathbf{p}_0 = [\Delta P, \Delta A, \Delta D]^\top$$
Represents continuous physical trajectory displacement. Strictly state displacement; **not** prediction error.

### M2 — Displacement Magnitude + Direction
$$\mathbf{m}_2 = [m, \hat{\mathbf{v}}] = \left[ \|\Delta \mathbf{p}\|_2, \; \frac{\Delta \mathbf{p}}{\|\Delta \mathbf{p}\|_2} \right]$$
4 stored elements with **3 effective degrees of freedom** due to the unit-norm constraint $\|\hat{\mathbf{v}}\|_2 = 1$.

### M3 — Residual Magnitude + Direction
$$\mathbf{m}_3 = [m_r, \hat{\mathbf{v}}_r] = \left[ \|\mathbf{r}_T\|_2, \; \frac{\mathbf{r}_T}{\|\mathbf{r}_T\|_2} \right]$$
4 stored elements with **3 effective degrees of freedom**. Separates epistemic violation magnitude from semantic orientation.

### M4 — Full Vector Prediction Residual
$$\mathbf{r}_T = \hat{\mathbf{p}}_T - \mathbf{p}_T = [r_P, r_A, r_D]^\top$$
Complete 3D prediction error in generative model coordinates without scalar reduction.

### M5 — Precision-Weighted Vector Residual
$$S_{\boldsymbol{\Pi}} = \sqrt{\mathbf{r}_T^\top \boldsymbol{\Pi} \mathbf{r}_T}$$
where $\boldsymbol{\Pi} \in \mathbb{R}^{3 \times 3}$ is a positive-semidefinite metric tensor. Evaluated over predefined candidates without outcome-driven fitting.

---

## 5. Experimental Design

### 5.1 Stimulus Set
- **Source**: Frozen Candidate G1 stimulus set ($N = 270$ probes, 90 Low, 90 Med, 90 High) generated via `GeneratorG1(seed=9999)` across 3 semantic domains (technical, relational, conversational).
- **Stimulus Processing**: Canonical lexical tokenization and valence/arousal/density extraction via `StimulusProcessor(StimulusConfig())`.

### 5.2 Dynamic Simulation Framework
- **Integration Engine**: Canonical `EmotionCore(EmotionConfig())` 200 ms ODE integration ($\Delta t = 0.10\text{s}$).
- **Resting Attractor**: Initialized from Philia resting baseline $\mathbf{p}_0 = [P=+0.25, A=-0.05, D=+0.05]^\top$.
- **Exposure Grid**: Primary conversational exposures $T \in \{1, 2, 4, 8, 12, 16, 25\}$ ($0.10\text{s}$ to $2.50\text{s}$) and exploratory long exposures $T \in \{50, 100\}$ ($5.0\text{s}$ to $10.0\text{s}$).

### 5.3 Predefined Precision Structures
1. **$\boldsymbol{\Pi}_0$ (Isotropic Identity)**:
   $$\boldsymbol{\Pi}_0 = \begin{bmatrix} 1 & 0 & 0 \\ 0 & 1 & 0 \\ 0 & 0 & 1 \end{bmatrix}$$
2. **$\boldsymbol{\Pi}_1$ (Predefined Exploratory Somatic/Arousal Prioritization)**:
   $$\boldsymbol{\Pi}_1 = \begin{bmatrix} 1.0 & 0 & 0 \\ 0 & 4.0 & 0 \\ 0 & 0 & 1.0 \end{bmatrix}$$
   *Guardrail:* Exploratory theoretical candidate exploring a $2:1$ precision ratio on activation. Unvalidated in Lucia; not evidence of higher physiological importance of Arousal.
3. **$\boldsymbol{\Pi}_2$ (Fixed Geometric Normalization Metric / Exploratory Candidate)**:
   $$\boldsymbol{\Pi}_2 = \begin{bmatrix} 1.778 & 0 & 0 \\ 0 & 1.108 & 0 \\ 0 & 0 & 1.108 \end{bmatrix}$$
   *Guardrail:* Derived from inverse squared headroom to $[-1, 1]$ bounds from Philia attractor ($h_P = 0.75 \implies h_P^{-2} = 1.778$; $h_A = 0.95 \implies h_A^{-2} = 1.108$; $h_D = 0.95 \implies h_D^{-2} = 1.108$). Valid geometric normalization; not automatically biological precision.
4. **$\boldsymbol{\Pi}_3$ (Fixed Coupled Limbic Interaction Metric)**:
   $$\boldsymbol{\Pi}_3 = \begin{bmatrix} 1.0 & -0.3 & 0 \\ -0.3 & 1.0 & 0 \\ 0 & 0 & 1.0 \end{bmatrix}$$
   *Guardrail:* Off-diagonal cross-coupling ($\rho_{PA} = -0.3$) reflecting MT-LNN limbic ODE Valence–Arousal damping. Positive definite with eigenvalues $1.3, 0.7, 1.0$.

---

## 6. M0–M5 Representation Analysis (RQ1)

We evaluated representations across 10 evaluation dimensions without constructing an artificial composite ranking score:

| Dimension | M0: Scalar Surprise | M1: Displacement Vector | M2: Displacement Polar | M3: Residual Polar | M4: Residual Vector | M5: Precision-Weighted |
|---|---|---|---|---|---|---|
| **Dimensionality** | 1D scalar | 3D vector | scalar + 3D unit | scalar + 3D unit | 3D vector | 1D scalar |
| **Effective DOF** | 1 | 3 | **3** | **3** | 3 | 1 |
| **Sign / Polarity** | None ($\ge 0$) | Complete | Complete (in $\hat{\mathbf{v}}$) | Complete (in $\hat{\mathbf{v}}_r$) | Complete | None ($\ge 0$) |
| **Component Preserv.** | None | Complete ($P, A, D$) | Complete ($m \cdot \hat{\mathbf{v}}$) | Complete ($m_r \cdot \hat{\mathbf{v}}_r$) | Complete | Weighted composite |
| **Angular Info** | Discarded | Complete | Explicit ($\hat{\mathbf{v}}$) | Explicit ($\hat{\mathbf{v}}_r$) | Complete | Ellipsoidal |
| **Prediction Semantics** | Degenerates to $\Delta \mathbf{p}$ | State displacement | State displacement | Complete | Complete | Weighted energy |
| **Baseline Dependence** | Anchored to $\mathbf{p}_0$ | Anchored to $\mathbf{p}_0$ | Anchored to $\mathbf{p}_0$ | Anchored to $\hat{\mathbf{p}}_T$ | Anchored to $\hat{\mathbf{p}}_T$ | Anchored to $\hat{\mathbf{p}}_T$ |
| **Model Dependence** | Conditional on $\mathbf{A}, \mathbf{b}$ | Independent | Independent | High (depends on $\mathbf{A}, \mathbf{b}$) | High (depends on $\mathbf{A}, \mathbf{b}$) | High (depends on $\mathbf{A}, \mathbf{b}, \boldsymbol{\Pi}$) |
| **Interpretability** | Low (conflates axes) | High (PAD space) | High (intensity vs type)| High (surprise vs type)| High (error coordinates)| Moderate (ellipsoid) |
| **Cost** | $\approx 0.1\,\mu\text{s}$ | $\approx 0.1\,\mu\text{s}$ | $\approx 0.2\,\mu\text{s}$ | $\approx 0.3\,\mu\text{s}$ | $\approx 0.2\,\mu\text{s}$ | $\approx 0.3\,\mu\text{s}$ |

---

## 7. Precision-Weighting Analysis (RQ2)

We evaluated whether predefined precision structures resolve cross-tier magnitude collapse ($|S_{\text{Med}} - S_{\text{High}}| \le 0.02$) across conversational exposures:

### Summary at $T=12$ (1.20s Exposure):

| Candidate | Name / Category | $\Delta_{\text{ML}}$ (Target $\ge 0.10$) | $\Delta_{\text{HM}}$ (Target $\ge 0.15$) | Gate 2 Status | Med–High Collapses | MH Collapse Rate | Mean Angular Separation |
|---|---|---|---|---|---|---|---|
| **$\boldsymbol{\Pi}_0$** | Isotropic Identity (Canonical $S$) | $+0.1580$ (Pass) | $+0.1069$ (Fail) | **BLOCKED** | 358 | 4.4% | $86.0^\circ$ |
| **$\boldsymbol{\Pi}_1$** | Exploratory Somatic/Arousal | $+0.1524$ (Pass) | $+0.2801$ (Pass) | **PASS (Exploratory)** | 0 | 0.0% | $0.0^\circ$ (N/A) |
| **$\boldsymbol{\Pi}_2$** | Fixed Geometric Normalization | $+0.2332$ (Pass) | $+0.1343$ (Fail) | **BLOCKED** | 138 | 1.7% | $23.5^\circ$ |
| **$\boldsymbol{\Pi}_3$** | Coupled Limbic Metric | $+0.1592$ (Pass) | $+0.1121$ (Fail) | **BLOCKED** | 1,940 | 24.0% | $45.5^\circ$ |

### Methodological Observations:
1. **$\boldsymbol{\Pi}_0$ Collapses Orthogonal Trajectories**: At $T=12$, canonical scalar surprise allows 358 Medium–High probe pairs to have near-identical scalar values ($|S_{\text{Med}} - S_{\text{High}}| \le 0.02$) despite being separated by an average of $86.0^\circ$ in 3D PAD space.
2. **$\boldsymbol{\Pi}_1$ Separation is an Exploratory Property**: Setting $\Pi_{AA} = 4.0$ amplifies the high Arousal response of High stimuli, achieving $\Delta_{\text{HM}} = +0.2801$. However, this is an exploratory mathematical candidate that virtually ignores Pleasure. It does not validate biological importance.
3. **Geometric Normalization ($\boldsymbol{\Pi}_2$) Leaves Compression Unresolved**: Weighting by Philia headroom ($h_P^{-2} = 1.778$) increases $\Delta_{\text{ML}}$ to $+0.2332$, but leaves $\Delta_{\text{HM}} = +0.1343$, failing Gate 2.
4. **Coupled Metric ($\boldsymbol{\Pi}_3$) Exacerbates Collapse**: Introducing limbic cross-drag ($\rho_{PA} = -0.3$) increases Med–High collapse pairs to 1,940 (24.0%), confirming that off-diagonal limbic interaction pulls trajectories closer in quadratic energy.

---

## 8. Component-Wise Analysis (RQ3)

We analyzed the three PAD components independently across all 270 probes:

### Component Statistics at $T=12$ (1.20s Exposure):

| Component | Tier Low (Mean $\pm$ SD) | Tier Med (Mean $\pm$ SD) | Tier High (Mean $\pm$ SD) | High vs Med Difference | 95% Confidence Interval | Cohen's $d$ (High vs Med) | Cohen's $d$ (Med vs Low) |
|---|---|---|---|---|---|---|---|
| **Pleasure ($P$)** | $-0.003 \pm 0.038$ | $+0.426 \pm 0.222$ | $+0.108 \pm 0.407$ | **$-0.3179$** | $[-0.4172, -0.2186]$ | **$-0.94$** | $+2.76$ |
| **Arousal ($A$)** | $+0.046 \pm 0.023$ | $+0.003 \pm 0.007$ | $+0.278 \pm 0.057$ | **$+0.2755$** | $[+0.2671, +0.2840]$ | **$+9.55$** | $-2.48$ |
| **Dominance ($D$)** | $-0.004 \pm 0.033$ | $+0.046 \pm 0.044$ | $+0.005 \pm 0.016$ | **$-0.0408$** | $[-0.0501, -0.0315]$ | **$-1.28$** | $+1.27$ |

### Scientific Takeaways:
- **Orthogonal Separation Cancelation**: Medium stimuli induce high positive Pleasure ($\Delta P = +0.426$) with baseline Arousal ($\Delta A = +0.003$). High stimuli induce high positive Arousal ($\Delta A = +0.278$) with lower Pleasure ($\Delta P = +0.108$).
- Under Euclidean norm $S = \sqrt{\Delta P^2 + \Delta A^2 + \Delta D^2}$, the two terms cancel out:
  $$S_{\text{Med}} \approx \sqrt{0.426^2 + 0.003^2} = 0.426, \quad S_{\text{High}} \approx \sqrt{0.108^2 + 0.278^2} = 0.298$$
  At $T=12$, the average values are $S_{\text{Med}} = 0.428$ and $S_{\text{High}} = 0.535$, creating an empirical difference of only $\Delta_{\text{HM}} = 0.107$.
- *Guardrail Note:* Statistical separation (Cohen's $d > 9.0$ on Arousal) demonstrates component distinguishability under the frozen stimulus set, but does not infer causal psychological superiority of any single axis.

---

## 9. Directional / Magnitude-Matched Analysis (RQ4)

For all pairs satisfying $|S_i - S_j| \le 0.02$, we evaluated directional divergence across exposures:

| Exposure $T$ | Exposure Duration | Matched MH Pairs | Mean Cosine Similarity | Mean Angular Separation | Mean Vector Distance | Mean $\Delta P$ Diff | Mean $\Delta A$ Diff |
|---|---|---|---|---|---|---|---|
| **$T=1$** | $0.10\text{s}$ | 4,371 | $+0.380$ | **$61.2^\circ$** | $0.0883$ | $-0.0644$ | $+0.0424$ |
| **$T=2$** | $0.20\text{s}$ | 3,374 | $+0.308$ | **$66.1^\circ$** | $0.1796$ | $-0.1385$ | $+0.0817$ |
| **$T=4$** | $0.40\text{s}$ | 2,082 | $+0.133$ | **$78.5^\circ$** | $0.3756$ | $-0.3188$ | $+0.1520$ |
| **$T=8$** | $0.80\text{s}$ | 622 | $+0.063$ | **$83.3^\circ$** | $0.6452$ | $-0.5652$ | $+0.2493$ |
| **$T=12$** | $1.20\text{s}$ | 358 | $+0.022$ | **$86.0^\circ$** | $0.8348$ | $-0.7396$ | $+0.3125$ |
| **$T=16$** | $1.60\text{s}$ | 204 | $+0.183$ | **$74.8^\circ$** | $0.8375$ | $-0.6981$ | $+0.3489$ |
| **$T=25$** | $2.50\text{s}$ | 286 | $-0.237$ | **$103.7^\circ$** | $1.3520$ | $-1.2696$ | $+0.4469$ |
| **$T=50$** | $5.00\text{s}$ | 0 | $0.000$ | $0.0^\circ$ (N/A) | $0.0000$ | $0.0000$ | $0.0000$ |
| **$T=100$** | $10.00\text{s}$ | 0 | $0.000$ | $0.0^\circ$ (N/A) | $0.0000$ | $0.0000$ | $0.0000$ |

### Governance Verdict String:
> **EVIDENCE CONSISTENT WITH DIRECTIONAL/COMPONENT INFORMATION PERSISTING AFTER MAGNITUDE MATCHING**

*Methodological Clarification:* This demonstrates that within magnitude-matched strata, directional angles ($61.2^\circ$ to $103.7^\circ$) persist. It is an empirical geometric finding, not a claim of formal statistical independence in an unconstrained regression model.

---

## 10. Displacement vs. Prediction Residual (RQ5)

We audited the causal and mathematical relationship between bodily displacement $\Delta \mathbf{p} = \mathbf{p}_T - \mathbf{p}_0$ and generative prediction residual $\mathbf{r}_T = \hat{\mathbf{p}}_T - \mathbf{p}_T$:

1. **Unadapted Beliefs ($\mathbf{A}=\mathbf{I}, \mathbf{b}=\mathbf{0}$)**:
   $$\hat{\mathbf{p}}_T = \mathbf{A}\mathbf{p}_0 + \mathbf{b} = \mathbf{p}_0 \implies \mathbf{r}_T^{(0)} = \mathbf{p}_0 - \mathbf{p}_T = -\Delta \mathbf{p}$$
   Numerical validation confirmed $\max |\|\mathbf{r}_T^{(0)}\|_2 - \|\Delta\mathbf{p}\|_2| = 0.00 \times 10^0 < 10^{-9}$. Canonical surprise $S$ evaluates state displacement solely because unadapted expectations assume static persistence.
2. **Online-Adapted Beliefs ($\mathbf{A}_{\text{adapt}}, \mathbf{b}_{\text{adapt}}$)**:
   After 30 conversational Low/Med turns, $\mathbf{r}_T^{(\text{adapt})}$ diverged completely from displacement:
   - At $T=12$, displacement magnitude was $0.5442$, while adapted residual magnitude was $0.5171$.
   - The angular separation between displacement and adapted residual was **$179.5^\circ$**.
3. **Architectural Implication**: Reverting from prediction residuals to raw state displacement would discard Active Inference learning dynamics. Future measurement architectures must preserve prediction-residual semantics ($\mathbf{r}_T$) rather than raw bodily displacement ($\Delta \mathbf{p}$).

---

## 11. Homeostatic Relevance (RQ6)

We conducted an evidence inventory and conceptual compatibility analysis of homeostatic coupling:

### Conceptual Forms Reviewed:
1. **Dynamic Precision Modulation**: $\boldsymbol{\Pi} = f(\text{homeostatic\_state})$. Metabolic fatigue attenuates sensory precision, matching biological Active Inference principles.
2. **Post-Hoc Effective Surprise**: $S_{\text{eff}} = g(\mathbf{S}_{\text{vector}}, \text{homeostatic\_state})$. Gating surprise by metabolic energy $\beta_{\text{epist}}(E, C)$.

### Evidence Inventory in Lucia Codebase:
- `EmotionCore` maintains physiological energy $E \in [0, 1]$ and fatigue dynamics (ADR-002, ADR-014).
- `ActiveInferenceEngine.step()` currently consumes only `PADState`, completely decoupled from metabolic energy.
- `ActionSelectionEngine` already implements homeostatic gating via $\beta_{\text{epist}}(E, C) = \beta_0 E (1 - 0.5 C)$ (Phase 22 H1).

### Conceptual Status Classification:
> **B — Plausible future research direction, but currently unsupported by validated production evidence**

*Guardrail Compliance:* Verified that no parameter fitting was performed, and no claim of biological validation was made.

---

## 12. Conversational-Timescale Analysis (RQ7)

We evaluated candidate representations across primary conversational exposures ($T \le 25$, $0.1\text{s}$ to $2.5\text{s}$) against preregistered Gate 2 thresholds ($\Delta_{\text{ML}} \ge 0.10, \Delta_{\text{HM}} \ge 0.15$):

```text
Conversational Exposure Regime: T in {1, 2, 4, 8, 12, 16, 25} (0.10s to 2.50s)
  • M0 (Canonical Scalar S): M0 does not satisfy the current preregistered dual Gate 2 thresholds at T <= 25 under frozen G1/current dynamics (Delta_HM remains <= 0.107).
  • M1 (Displacement Vector): HIGHLY VIABLE across all T in {1, 2, 4, 8, 12, 16, 25}. Separation on Arousal (Cohen's d > 9.0) appears by T=1 (0.10s).
  • M2 (Displacement Polar): HIGHLY VIABLE. Angular separation reaches 66.1° by T=2 (0.20s).
  • M3 (Residual Polar): HIGHLY VIABLE. Mirrors M2 under unadapted prior; preserves epistemic violation under adapted prior.
  • M4 (Residual Vector): HIGHLY VIABLE. Preserves full 3D prediction error.
  • M5 (Precision-Weighted Scalar): Fails Gate 2 under Pi_0, Pi_2, and Pi_3. Passes under Pi_1 at T >= 8, but Pi_1 represents an unvalidated exploratory formula.

Exploratory Reference Regime: T in {50, 100} (5.0s to 10.0s)
  • M0 passes Gate 2 solely through multi-second continuous stimulus exposure (unrealistic for interactive speech turns).
```

---

## 13. Architectural Interpretation (RQ8)

We formalized the distinction between physiological surprise and epistemic uncertainty:

```text
+-----------------------------------------------------------------------------------+
|                              LUCIA COGNITIVE STREAM                               |
+-----------------------------------------------------------------------------------+
                                         |
                                         v
+------------------------------------+       +------------------------------------+
|       PHYSIOLOGICAL SURPRISE       |       |        EPISTEMIC UNCERTAINTY       |
|    "Prediction Residual: r_T"      |       |      "State Entropy: H(P)"         |
+------------------------------------+       +------------------------------------+
| • Grounded in continuous PAD ODE   |       | • Grounded in discrete belief /    |
| • Evaluates generative model error |       |   memory competition distributions |
| • Drives immediate somatic         |       | • Drives epistemic foraging        |
|   modulation, arousal spike, and   |       |   policy (seeking clarifying       |
|   Fast-Loop homeostatic drag       |       |   dialogue actions)                |
+------------------------------------+       +------------------------------------+
```

### Impact of Measurement Architecture:
- **Scalar Conflation Risk**: If surprise is collapsed to scalar $S$, a high-arousal emergency and a high-valence accomplishment produce identical surprise values. Downstream routing cannot determine whether the system requires somatic calming or epistemic clarification.
- **Vector Residual Utility**: Retaining vector residual $\mathbf{r}_T$ provides both intensity (magnitude) and orientation (polarity), enabling proper functional routing.

---

## 14. Evidence Classification

In strict adherence to Section 17 language locks:
- **SUPPORTED**: Canonical scalar $S$ collapses orthogonal affective states into identical scalar values ($|S_i - S_j| \le 0.02$) across conversational $T \le 25$.
- **SUPPORTED**: Vector representations (M1–M4) maintain pronounced component separation ($d > 9.0$) across conversational exposures $T \in [1, 25]$.
- **SUPPORTED**: Unadapted prediction residual $\mathbf{r}_T^{(0)}$ is mathematically identical to negative displacement $-\Delta \mathbf{p}$.
- **EVIDENCE CONSISTENT WITH**: Directional and component information persists after magnitude matching ($61.2^\circ$ to $103.7^\circ$).
- **EXPLORATORY**: Precision weighting candidate $\boldsymbol{\Pi}_1$ achieves dual Gate 2 separation, but as an unvalidated exploratory formula.
- **UNRESOLVED**: Whether the information loss under scalar $S$ is architecturally unacceptable in production, or whether an augmented scalar representation is sufficient.
- **NOT TESTED**: Online LLM generation quality under vector-modulated prompting.

---

## 15. Limitations

1. **Synthetic G1 Stimuli**: Probes were generated using calibrated synthetic generation rather than live human conversational dialogue.
2. **Deterministic Limbic Integration**: Trajectories were integrated deterministically without stochastic noise in the fast loop.
3. **Static Attractor**: Baseline was strictly anchored to the canonical Philia attractor ($P=+0.25, A=-0.05, D=+0.05$).
4. **Offline Evaluation**: The study evaluates limbic state representations offline without live RVC speech or 3D avatar rendering.

---

## 16. Unresolved Questions

1. Does downstream cognitive routing (e.g., LLM context conditioning, response latency injection) actually require continuous 3D directional vectors, or is a discrete quadrant classification sufficient?
2. Can an alternative, independently motivated precision structure resolve scalar collapse without selectively prioritizing Arousal?
3. How do multiple sequential conversational turns affect the divergence between state displacement and prediction residuals in continuous operation?

---

## 17. Implications for Future v1.5 Research

1. **Do NOT Rush to Replace $S$ in Production**: Production runtime (`src/core/**`) must remain untouched.
2. **Prioritize Augmented Representations**: Future research should investigate hybrid approaches (e.g., M2/M3: scalar magnitude for urgency, unit direction for qualitative modulation) before attempting full vector replacements.
3. **Formal Architecture Gate Required**: Any proposal to change the measurement interface of `ActiveInferenceEngine` must be preceded by an approved ADR and formal realization design.

---

## 18. Final Governance State

- **Phase 22 H1 Status**: **INCONCLUSIVE** (Preserved exactly as mandated).
- **Gate 2 Status**: **BLOCKED** (Frozen G1 does not satisfy dual scalar Gate 2 under canonical $S$ at $T \le 25$).
- **Protocol v1.5 Status**: **NOT AUTHORIZED**.
- **Architecture Gate Status**: **STRICTLY LOCKED**.
- **Production Architecture**: **0 MUTATIONS** (100% untouched).
- **Genesis Onboarding Profile**: **BIT-EXACT UNTOUCHED** (`{"is_onboarded": false}`).

---

## 19. Reproducibility / Hashes

- **Random Seed**: `9999` (Deterministic Candidate G1)
- **Manifest File**: [`tests/evaluation_phase22/fixtures/manifest_h1_precision_directional_measurement.json`](file:///c:/Users/Lunafiah/Desktop/My_project/Lucia/tests/evaluation_phase22/fixtures/manifest_h1_precision_directional_measurement.json)
- **Script File**: [`tests/evaluation_phase22/scripts/analyze_precision_directional_measurement.py`](file:///c:/Users/Lunafiah/Desktop/My_project/Lucia/tests/evaluation_phase22/scripts/analyze_precision_directional_measurement.py)
- **Results File**: [`tests/evaluation_phase22/results/h1_precision_directional_measurement/precision_directional_results.json`](file:///c:/Users/Lunafiah/Desktop/My_project/Lucia/tests/evaluation_phase22/results/h1_precision_directional_measurement/precision_directional_results.json)

---

## 20. Test Results

Automated test suite [`tests/evaluation_phase22/test_h1_precision_directional_measurement.py`](file:///c:/Users/Lunafiah/Desktop/My_project/Lucia/tests/evaluation_phase22/test_h1_precision_directional_measurement.py) passed 11/11 tests in 0.48s:
- `test_manifest_integrity`: **PASSED**
- `test_governance_invariants`: **PASSED**
- `test_rq1_representation_matrix`: **PASSED**
- `test_rq2_precision_candidates_evaluated`: **PASSED**
- `test_rq3_component_separation`: **PASSED**
- `test_rq4_directional_magnitude_matched`: **PASSED**
- `test_rq5_displacement_vs_residual`: **PASSED**
- `test_rq6_homeostatic_inventory`: **PASSED**
- `test_rq7_conversational_timescale_viability`: **PASSED**
- `test_rq8_architectural_semantics`: **PASSED**
- `test_final_synthesis_and_governance`: **PASSED**

Full Phase 22 regression suite: **80/80 passed in 12.99s**. Zero regressions.
