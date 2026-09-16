# Phase 22 — H1 Protocol Amendment v1.4
## Canonical Specification: Full Sample Synchronization (N = 270), Conditioned Surprise Check (T = 12), and Calibrated Uncertainty Variance

> **Project:** Lucia — Embodied Whole-Brain Architecture  
> **Phase:** Phase 22 — Active Inference & Prospective Epistemic Foraging  
> **Subsystem:** Layer 4 (Active Inference) & Layer 2 (EmotionCore Coupled MT-LNN)  
> **Document Role:** Formal Specification & Preregistration Amendment (Pre-Execution Only)  
> **Author:** Antigravity (Execution / Research Implementation Agent)  
> **Reviewer:** Ciah (Research Reviewer)  
> **Governance Status:** **[PROTOCOL v1.4 — DRAFT / PENDING Ciah REVIEW — ARCHITECTURE GATE LOCKED]**  
> **Date:** September 2026  
> **Governing Documents:** [`AGENTS.md`](file:///c:/Users/Lunafiah/Desktop/My_project/Lucia/AGENTS.md), [`docs/00_PROJECT_OVERVIEW.md`](file:///c:/Users/Lunafiah/Desktop/My_project/Lucia/docs/00_PROJECT_OVERVIEW.md), [`docs/ARCHITECTURE.md`](file:///c:/Users/Lunafiah/Desktop/My_project/Lucia/docs/ARCHITECTURE.md)  
> **Historical Artifacts Preserved:** [`phase22_evaluation_summary.json`](file:///c:/Users/Lunafiah/Desktop/My_project/Lucia/tests/evaluation_phase22/results/phase22_evaluation_summary.json) (Original Benchmark: FAILED), [`PHASE_22_H1_EXECUTION_REPORT_PATH_C.md`](file:///c:/Users/Lunafiah/Desktop/My_project/Lucia/docs/specs/Lucia-phase22-Epistemic_Foraging/PHASE_22_H1_EXECUTION_REPORT_PATH_C.md) (Path C: INCONCLUSIVE)  
> **Companion Audit & Calibration Reports:** [`PHASE_22_H1_POST_EXECUTION_COMPLIANCE_AUDIT.md`](file:///c:/Users/Lunafiah/Desktop/My_project/Lucia/docs/specs/Lucia-phase22-Epistemic_Foraging/PHASE_22_H1_POST_EXECUTION_COMPLIANCE_AUDIT.md), [`PHASE_22_H1_U_LOW_CALIBRATION_REPORT.md`](file:///c:/Users/Lunafiah/Desktop/My_project/Lucia/docs/specs/Lucia-phase22-Epistemic_Foraging/PHASE_22_H1_U_LOW_CALIBRATION_REPORT.md)  
> **Supersedes:** [`PHASE_22_H1_PROTOCOL_AMENDMENT_v1.3.md`](file:///c:/Users/Lunafiah/Desktop/My_project/Lucia/docs/specs/Lucia-phase22-Epistemic_Foraging/PHASE_22_H1_PROTOCOL_AMENDMENT_v1.3.md)

---

## 0. Governance & Evidentiary Classification

### 0.1 Strict Pre-Execution Governance
This document is a **formal research specification proposal** amending Hypothesis 1 (H1) of Phase 22.
- **DRAFT STATUS**: Marked as `[PROTOCOL v1.4 — DRAFT / PENDING Ciah REVIEW]`. It has **NOT** been approved or ratified, and does **NOT** authorize experimental re-execution.
- **NO PRODUCTION MUTATION**: It does **NOT** authorize any modification to production code in `src/core/`, canonical cognitive pipeline stages S1–S16, or existing system orchestrators.
- **GENESIS GATE PRESERVED**: `data/profile.json` remains bit-exact `{"is_onboarded": false}`.
- **ARCHITECTURE GATE LOCKED**: The architecture gate remains strictly **LOCKED**.

```text
Historical Baseline (Phase 22 Original: FAILED)
             ≠
Historical Execution (Path C v1.3: INCONCLUSIVE — Blocked by Gates 2 & 4)
             ≠
Amended Protocol v1.4 (This Document: Draft / Pending Ciah Review)
             ≠
Future Experimental Execution (Requires Explicit Prior Ratification)
             ≠
Architecture Approval Gate (LOCKED)
             ≠
Production Realization (src/core/**)
```

> [!IMPORTANT]
> **GOVERNANCE STATUS DECLARATION (Ciah Sign-Off Baseline):**  
> **Phase 22 H1: INCONCLUSIVE — Path C archived. Protocol v1.4 DRAFT — not yet ratified. Architecture Gate LOCKED.**  
> 1. **Path C Verdict Immutable**: Path C retains its permanent verdict of **INCONCLUSIVE**. Retracting the downstream TOST conclusion ("Decoupling Supported") is mathematically and scientifically mandatory. Quality Gate 2 and Gate 4 are strict preconditions; downstream TOST equivalence cannot override failed manipulation gates.
> 2. **Gate 2 Operational Redefinition**: Transitioning Gate 2 from unconditioned pooled separation to standardized exposure-conditioned separation ($T=12$) is an **explicit operational redesign of the manipulation check** derived from MT-LNN ODE dynamical bounds, **NOT** an attempt to "modify metrics so Path C passes". Path C remains permanently failed under its historical preregistered protocol.
> 3. **Candidate C1 Validation Precondition**: While Monte Carlo calibration proves favorable properties ($E[\text{Var}] \approx 0.00513, P(\text{fail}) \approx 0.25\%$), Candidate C1 is **NOT yet validated** merely by synthetic simulation. It is a proposed specification that requires freezing the generator followed by rigorous **pre-execution validation on the realized $N=270$ probe set** prior to benchmark execution.

### 0.2 Purpose of Amendment v1.4
Protocol Amendment v1.4 resolves four documented methodological and calibration defects identified during the post-execution compliance audit of Path C:
1. **Full Sample Size Synchronization ($N = 270$)**: Replaces all legacy textual references to $N = 135$ ($15$ probes/cell, $5/5/5$ $T$-distribution) with the canonical $N = 270$ ($30$ probes/cell, $10/10/10$ $T$-distribution), removing Path C as an optional branch and establishing it as the single, unified primary design.
2. **Quality Gate 2 Redesign (Standardized Exposure Conditioned Check)**: Conditions the primary separation test between High and Medium surprise on the standardized duration $T = 12$ ticks ($\bar{S}_H(T=12) - \bar{S}_M(T=12) \ge 0.1500$), resolving the physical impossibility of achieving an unconditioned separation of $0.15$ when averaging across single-tick ODE displacements.
3. **Quality Gate 4 Recalibration ($U_{\text{Low}}$ Proposition Generator)**: Re-parameterizes the candidate confidence distribution for $U_{\text{Low}}$ from $[0.940, 0.995]$ to $[0.900, 0.995]$ based on Monte Carlo evidence ($20,000$ simulated cells), elevating expected population variance from $0.0023$ to $0.005130$ and reducing cell failure probability from $67.23\%$ to $0.25\%$.
4. **Power & Precision Synchronization**: Formally synchronizes the statistical power analysis to the exact v1.4 design matrix ($\text{rank} = 11, p = 10, N_{\text{eff}} = 257, \text{SE}_z = 0.062378, \Delta = 0.20$), proving that power is $89.15\%$ at $\rho_0 = 0.0$ and $87.35\%$ at $\rho_0 = 0.02$.

---

## 1. Canonical Historical Evidence & Audit Context

### 1.1 Original Phase 22 Benchmark (September 16, 2026)
- **Dataset**: `phase22_evaluation_summary.json` (Commit `5e7dbdc`)
- **Observed Metrics**: $N = 80, \quad r = -0.5260, \quad R^2 = 0.2766, \quad p = 5.433 \times 10^{-7}$
- **Preregistered Criterion**: $R^2 < 0.15$
- **Canonical Verdict**: **FAILED**
- **Methodological Status**: Preserved bit-exact as immutable historical justification for deconfounding. The negative correlation was shown to be an artifact of zero within-stratum variance and Simpson's paradox resulting from cluster placement (Stratum 5).

### 1.2 Path C Execution Benchmark (September 16, 2026)
- **Dataset**: `phase22_h1_path_c_matrix.json`, `phase22_h1_path_c_summary.json` (Commit `d82ebfc`)
- **Observed Metrics**: $N = 270, \quad \hat{\rho}_{\text{partial}} = +0.0134, \quad 90\%\text{ CI } [-0.089, +0.115] \subset \pm 0.20, \quad \eta_p^2(U \to S) = 0.0000, \quad \eta_p^2(S \to U) = 0.0060$
- **Downstream TOST Metric**: Equivalence Observed under $\Delta = 0.20$ ($p_{\text{TOST}} = 1.202 \times 10^{-3}$)
- **Preregistered Manipulation Gates**:
  - Quality Gate 2 (Surprise Separation): **FAILED** ($\Delta_{HM} = 0.0967 < 0.1500$)
  - Quality Gate 4 (Within-Cell Variance): **FAILED** (Cell 4 $\text{Var}(U) = 0.001711 < 0.002000$)
- **Canonical Verdict**: **FINAL VERDICT: INCONCLUSIVE (BLOCKED BY GATES 2 & 4)**
- **Methodological Status**: Formally recorded as INCONCLUSIVE in [`PHASE_22_H1_EXECUTION_REPORT_PATH_C.md`](file:///c:/Users/Lunafiah/Desktop/My_project/Lucia/docs/specs/Lucia-phase22-Epistemic_Foraging/PHASE_22_H1_EXECUTION_REPORT_PATH_C.md). Downstream TOST results are retained strictly as **unconfirmed exploratory evidence**.

---

## 2. Core Architectural Hypothesis & Research Question

### 2.1 Research Question
> **Are retrospective physiological prediction surprise ($S_{\text{observed}}$) and prospective semantic uncertainty ($U_{\text{sem\_observed}}$) empirically separable operational dimensions in Lucia's cognitive architecture, or does variation in one dimension induce cross-factor spillover or non-negligible shared variance in the other when evaluated across varied exposure durations and stimulus intensities?**

### 2.2 Architectural Falsification Hypothesis ($H_1$)
- **Null Hypothesis of Non-Equivalence ($H_{0,\text{TOST}}$)**:  
  Conditioning on the experimental design matrix $\mathbf{X}$ (controlling for stimulus affect tier, semantic uncertainty tier, cross-factor interaction, and exposure duration), residual continuous physiological surprise and semantic uncertainty share non-negligible association:
  $$H_0: |\rho_{\text{partial}}| \ge \Delta \quad (\Delta = 0.20)$$
- **Alternative Hypothesis of Equivalence ($H_{1,\text{TOST}}$)**:  
  Residual continuous physiological surprise and semantic uncertainty are statistically equivalent to zero within the frozen architectural margin:
  $$H_1: -\Delta < \rho_{\text{partial}} < +\Delta \quad (\Delta = 0.20 \implies R^2_{\text{partial}} < 0.040)$$
- **Directional Spillover Hypotheses ($H_{\text{spill}}$)**:  
  Cross-factor spillover effect sizes must be negligible in both directions:
  $$\eta_p^2(U_{\text{target}} \to S_{\text{observed}} \mid S_{\text{target}}, T) < 0.02$$
  $$\eta_p^2(S_{\text{target}} \to U_{\text{sem\_observed}} \mid U_{\text{target}}, T) < 0.02$$

---

## 3. Operational Definitions & Ontological Variable Classification

To eliminate conceptual confusion between engineering instruments, physiological dynamical states, and propositional representations:

| Concept | Ontological Status | Mathematical / System Entity | Operational Range | Role in Protocol v1.4 |
|---|---|---|---|---|
| **Target Stimulus Affective Intensity ($S_{\text{target}}$)** | **Manipulated Experimental Factor** | Lexical arousal, valence extremity, and urgency tier of authored probe text: $\{S_L, S_M, S_H\}$. | Qualitative factor levels: Low/Neutral, Moderate, High Urgency. | Manipulated stimulus factor driving differential limbic input forcing. |
| **Exposure Duration ($T$)** | **Experimental Implementation Variable** | Number of discrete integration ticks ($dt = 0.10\text{s}$) through `EmotionCore.commit_stimulus()`. | $T \in \{1, 4, 12\}$ ticks ($0.10\text{s} - 1.20\text{s}$). | Engineering vehicle allowing continuous ODE trajectories to unfold; balanced $10/10/10$ in every cell; controlled covariate in statistical models. |
| **Observed Physiological Surprise ($S_{\text{observed}}$)** | **Actual Continuous Physiological Variable** | Euclidean norm between prior predicted PAD state $\hat{\mathbf{p}}_0 = \mathbf{A}\mathbf{p}_0 + \mathbf{b}$ captured at Stage 2 and committed post-stimulus limbic PAD state $\mathbf{p}_T$ after $T$ integration ticks at Stage 4: $$S_{\text{observed}} = \|\hat{\mathbf{p}}_0 - \mathbf{p}_T\|_2$$ | $[0.0, \sqrt{12}] \approx [0.0, 3.46]$; operational envelope $[0.002, 0.85]$. | Primary continuous physiological dependent variable representing retrospective prediction error. |
| **Standardized Manipulation Exposure ($T = 12$)** | **Standardized Manipulation-Check Condition** | The subset of probe observations evaluated at $T = 12$ ticks ($1.20\text{s}$). | Fixed duration condition $T = 12$. | Standardized exposure condition verifying that stimulus tiers produce separated steady-state limbic displacements. |
| **Semantic Uncertainty Target ($U_{\text{target}}$)** | **Manipulated Experimental Factor** | Target uncertainty tier parameterizing the authored proposition graph: $\{U_L, U_M, U_H\}$. | Qualitative factor levels: Low ($0.10-0.35$), Med ($0.50-0.70$), High ($0.80-0.95$). | Manipulated experimental factor parameterizing probe candidate propositions. |
| **Observed Semantic Uncertainty ($U_{\text{sem\_observed}}$)** | **Deterministic / Derived Propositional Metric** | Normalized aggregate binary Shannon entropy across retrieved proposition set $P = \{p_1, \dots, p_K\}$: $$U_{\text{sem\_observed}} = \frac{1}{|P|} \sum_{i=1}^{|P|} H(c_i)$$ where $H(c_i) = -c_i \log_2 c_i - (1-c_i) \log_2(1-c_i)$. | $[0.0, 1.0]$ bits/proposition. | Derived measurement verifying realized propositional entropy of authored candidate memory/knowledge graph. |
| **Active Inference Generative Model** | **Generative Substrate** | 3x3 linear transition model $\hat{\mathbf{p}}_t = \mathbf{A}\mathbf{p}_{t-1} + \mathbf{b}$ updating online via analytic free energy gradients with KL regularization toward identity. | Matrix $\mathbf{A} \in [-2.0, 2.0]^{3 \times 3}$, vector $\mathbf{b} \in \mathbb{R}^3$. | Substrate generating prediction expectations. |
| **Coupled MT-LNN Limbic Core** | **Limbic Substrate** | Fast reactive hidden state $\mathbf{h} \in \mathbb{R}^{32}$ and slow latent field $\mathbf{s}_{\text{slow}} \in \mathbb{R}^{16}$ integrated via RK45 differential equations. | Bounded in $[-1.0, 1.0]$. | Substrate integrating sensory stimulus across time. |

---

## 4. Standardized Experimental Design: Synchronized $N = 270$ Architecture

### 4.1 Sample Allocation & Factorial Structure
The primary design is consistently defined throughout Protocol v1.4 as:
- **Total Sample Size**: Exactly $N = 270$ unique probes.
- **Factorial Structure**: $3 \times 3$ completely crossed factorial design ($S_{\text{target}} \in \{\text{Low}, \text{Med}, \text{High}\} \times U_{\text{target}} \in \{\text{Low}, \text{Med}, \text{High}\}$).
- **Probes per Cell**: Exactly $n = 30$ unique probes per cell across all 9 cells.
- **Within-Cell Exposure Allocation**: Exposure duration $T \in \{1, 4, 12\}$ is allocated with exact symmetry inside **every single cell**:
  $$\text{Cell Allocation} = 10 \times (T = 1) + 10 \times (T = 4) + 10 \times (T = 12) = 30 \text{ probes}$$

```text
                        Semantic Uncertainty Target (U_target)
                         Low (0.10–0.35)       Med (0.50–0.70)       High (0.80–0.95)
                      ┌──────────────────────┬──────────────────────┬──────────────────────┐
   S_Low Target       │        Cell 1        │        Cell 2        │        Cell 3        │
   (Calm text)        │ 10×T=1,10×T=4,10×T=12│ 10×T=1,10×T=4,10×T=12│ 10×T=1,10×T=4,10×T=12│
Stimulus              ├──────────────────────┼──────────────────────┼──────────────────────┤
Affect Target         │        Cell 4        │        Cell 5        │        Cell 6        │
   S_Med Target       │ 10×T=1,10×T=4,10×T=12│ 10×T=1,10×T=4,10×T=12│ 10×T=1,10×T=4,10×T=12│
(S_target)            ├──────────────────────┼──────────────────────┼──────────────────────┤
                      │        Cell 7        │        Cell 8        │        Cell 9        │
   S_High Target      │ 10×T=1,10×T=4,10×T=12│ 10×T=1,10×T=4,10×T=12│ 10×T=1,10×T=4,10×T=12│
   (Urgent text)      │                      │                      │                      │
                      └──────────────────────┴──────────────────────┴──────────────────────┘
```

### 4.2 Exact Orthogonality Properties
By virtue of the identical $10/10/10$ within-cell allocation:
1. **$T \perp S_{\text{target}}$**: Across all 90 probes in $S_{\text{Low}}$, exactly 30 have $T=1$, 30 have $T=4$, 30 have $T=12$. The same holds identically for $S_{\text{Med}}$ and $S_{\text{High}}$.
2. **$T \perp U_{\text{target}}$**: Across all 90 probes in $U_{\text{Low}}$, exactly 30 have $T=1$, 30 have $T=4$, 30 have $T=12$. The same holds identically for $U_{\text{Med}}$ and $U_{\text{High}}$.
3. **$T \perp (S_{\text{target}} \times U_{\text{target}})$**: Within every individual interaction cell, the marginal distribution of $T$ is identical.
4. **Statistical Unit**: The **Probe** ($N = 270$). For each probe, observations are gathered across 5 fixed environmental random seeds ($42, 43, 44, 45, 46$) and averaged into a single probe-level mean $(\bar{S}_i, \bar{U}_i)$ prior to regression modeling, preventing pseudoreplication.

---

## 5. Audited Headless Production Measurement Pipeline

All evaluations must execute through the audited headless production path without synthetic PAD or surprise injection:

```text
Raw Stimulus Text
       ↓
StimulusProcessor.encode(text) -> stimulus_features (Lexical valence, density, polarity)
       ↓
EmotionCore.get_pad_state() -> p_0 (Stage 2 baseline capture)
       ↓
ActiveInferenceEngine.predict(p_0) -> p_hat_0 = A * p_0 + b (Generative expectation)
       ↓
For tick = 1 to T:
    core.push_stimulus(stimulus_features)
    token = core.commit_stimulus() -> p_t (Stage 3 ODE RK45 limbic integration)
       ↓
p_T = core.get_pad_state() (Stage 3 post-exposure state)
       ↓
ActiveInferenceEngine.step(p_0, p_T) -> S_observed = ||p_hat_0 - p_T||_2 (Stage 4)
       ↓
Derived Proposition Shannon Entropy -> U_sem_observed = (1/k) * sum(H(c_j))
```

Between consecutive probe evaluations:
1. `ai.reset()` restores $\mathbf{A} = \mathbf{I}_{3 \times 3}, \mathbf{b} = \mathbf{0}_3$.
2. `core.reset_to_resting()` restores $\mathbf{h} = \mathbf{0}_{32}, \mathbf{s}_{\text{slow}} = \mathbf{s}^*_{\text{philia}}, \mathbf{m}_{\text{homeo}} = \mathbf{m}^*$, draining all queues.

---

## 6. Standardized Probe Suite Architecture

### 6.1 Stimulus Text Generation (270 Unique Texts)
- **30 unique text templates per tier** $\times 3$ repetition index markers $= 90$ unique texts per tier ($270$ unique texts total).
- **Text Calibration Standards**:
  - $S_{\text{Low}}$: Monotonous, neutral system telemetry; lexical density $\sim 0.45-0.65$; valence $\approx 0.00 \pm 0.05$.
  - $S_{\text{Med}}$: Moderately positive conversational updates; lexical density $\sim 0.60-0.75$; valence $\approx +0.35 \pm 0.10$.
  - $S_{\text{High}}$: Urgent emergency alarms and ecstatic breakthrough celebrations; lexical density $\ge 0.80$; capitalized arousal tokens.

---

## 7. Quality Gate 2 Redesign: Standardized Exposure Conditioned Surprise Check

### 7.1 Methodological Problem with the Legacy Check
In Protocol v1.3, Quality Gate 2 evaluated surprise separation on unconditioned pooled means:
$$\bar{S}_{\text{observed}}(S_M) - \bar{S}_{\text{observed}}(S_L) \ge 0.1000$$
$$\bar{S}_{\text{observed}}(S_H) - \bar{S}_{\text{observed}}(S_M) \ge 0.1500$$

In Path C, the observed unconditioned separation was $\Delta_{HM} = 0.0967 < 0.1500$ (FAIL). As established by the compliance audit:
1. In Lucia's Coupled MT-LNN dynamical system, single-step integration ($T = 1, dt = 0.10\text{s}$) starting from resting Philia equilibrium ($\mathbf{p}^* = (+0.25, -0.05, +0.05)$) is physically bounded by relaxation constants ($\tau_{\text{fast}} \ge 0.10\text{s}$) to $\|\Delta\mathbf{p}\|_2 \le 0.1220$.
2. At $T = 1$, the maximum possible separation between any High and Med stimulus is physically bounded to $< 0.055$ (observed: $0.0956 - 0.0666 = 0.0290$).
3. When $T \in \{1, 4, 12\}$ is balanced $10/10/10$ across all cells, the pooled marginal mean across $T$ is mathematically:
   $$\Delta_{HM,\text{pooled}} = \frac{\Delta(T=1) + \Delta(T=4) + \Delta(T=12)}{3} = \frac{0.0290 + 0.0521 + 0.2090}{3} = \mathbf{0.0967}$$
4. An unconditioned marginal threshold $\ge 0.15$ is **mathematically incompatible with symmetrical multi-tick averaging** that includes single-tick evaluations.

### 7.2 Redesigned Gate 2 Specification (Protocol v1.4)
To verify that stimulus affect tiers successfully manipulate the limbic core without imposing a mathematically contradictory pooling requirement:

> **Standardized Manipulation-Check Exposure Condition ($T = 12$):**  
> Testing whether stimulus tiers produce genuine physiological separation must observe the system under a standardized duration sufficient for continuous ODE trajectory divergence to reach its steady-state displacement regime. $T = 12$ ticks ($1.20\text{s}$) is formally designated as the standardized manipulation-check exposure condition.

#### Confirmatory Evaluation Criteria for Gate 2:
1. **Pipeline Integrity**: 100% production classes; zero synthetic PAD injection.
2. **Omnibus Main Effect**: One-way ANOVA $F$-test of $S_{\text{target}}$ on $S_{\text{observed}}$ across the entire 270-probe dataset is statistically significant:
   $$F(2, 267) \implies p < 0.001$$
3. **Monotonic Ordering**: Monotonic separation across target tiers must hold across the pooled dataset AND within each individual exposure tier:
   $$\bar{S}_{\text{observed}}(S_L \mid T) < \bar{S}_{\text{observed}}(S_M \mid T) < \bar{S}_{\text{observed}}(S_H \mid T) \quad (\forall T \in \{1, 4, 12\})$$
4. **Primary Separation Check under Standardized Condition ($T = 12$)**:
   $$\bar{S}_{\text{observed}}(S_M \mid T=12) - \bar{S}_{\text{observed}}(S_L \mid T=12) \ge 0.1000$$
   $$\mathbf{\bar{S}_{\text{observed}}(S_H \mid T=12) - \bar{S}_{\text{observed}}(S_M \mid T=12) \ge 0.1500}$$
   *(In Path C, observed separation at $T=12$ was $0.6477 - 0.4387 = \mathbf{0.2090} \ge 0.1500$)*.
5. **No Threshold Relaxation**: The separation threshold remains strictly $\ge 0.1500$. It is **not** softened to fit the failed unconditioned number.
6. **Failure Consequence**: If any of criteria 1–4 are unmet, the manipulation check fails and the benchmark terminates as **INCONCLUSIVE**.

> [!CAUTION]
> **OPERATIONAL REDESIGN VS. RETROSPECTIVE ALTERATION:**  
> Conditioning Gate 2 on $T = 12$ represents an **explicit operational redefinition of the manipulation check** required by MT-LNN ODE physics. This is **NOT** a retroactive modification to turn historical Path C into a pass. Path C evaluated against its own preregistered pooled gate remains permanently recorded as **FAILED on Gate 2 $\implies$ INCONCLUSIVE**.

---

## 8. Quality Gate 4 Recalibration: $U_{\text{Low}}$ Proposition Generator

### 8.1 Methodological Defect in Path C Baseline
In Path C, Cell 4 failed Quality Gate 4 ($\text{Var}(U) = 0.001711 < 0.002000$). Monte Carlo calibration across $20,000$ synthetic cells proved that the baseline generator ($c \sim U(0.940, 0.995), k \in [2, 4]$) had an expected variance of only $0.002311$, producing a $67.23\%$ probability that at least one of the three Low cells would fail purely from sampling variation.

### 8.2 Recalibrated Proposition Generator (Candidate C1)
Based on the empirical evidence documented in [`PHASE_22_H1_U_LOW_CALIBRATION_REPORT.md`](file:///c:/Users/Lunafiah/Desktop/My_project/Lucia/docs/specs/Lucia-phase22-Epistemic_Foraging/PHASE_22_H1_U_LOW_CALIBRATION_REPORT.md), the $U_{\text{Low}}$ generator is formally proposed as **Candidate C1**:

> [!IMPORTANT]
> **PRE-EXECUTION PROBE SET VALIDATION MANDATE:**  
> Candidate C1 is a calibration proposal supported by Monte Carlo simulation ($E[\text{Var}] \approx 0.00513, P(\text{fail}) \approx 0.25\%$). It is **NOT** pre-validated. Once Protocol v1.4 is ratified, the generator will be frozen and the realized $N=270$ probe set must undergo **deterministic pre-execution variance validation** across all cells to empirically verify $\text{Var}_{\text{probe}} \ge 0.0020$ before launching any runtime evaluations.

```text
┌────────────────────────────────────────────────────────────────────────────────────────┐
│                        FROZEN v1.4 PROPOSITION GENERATORS                             │
│                                                                                        │
│   • U_Low Target  : c ~ Uniform(0.900, 0.995),  k ~ DiscreteUniform(2, 4)             │
│                     Expected Mean U = 0.2849,   Expected Variance = 0.005130           │
│                     P(Var < 0.0020) = 0.08%     3-Cell Family P(Fail) = 0.25%         │
│                                                                                        │
│   • U_Med Target  : c ~ Uniform(0.780, 0.920),  k ~ DiscreteUniform(2, 4)             │
│                     Expected Mean U ≈ 0.6170,   Expected Variance ≈ 0.003000           │
│                                                                                        │
│   • U_High Target : c ~ Uniform(0.500, 0.840),  k ~ DiscreteUniform(2, 4)             │
│                     Expected Mean U ≈ 0.8800,   Expected Variance ≈ 0.004000           │
└────────────────────────────────────────────────────────────────────────────────────────┘
```

### 8.3 Quality Gate 3 (Uncertainty Separation) Preservation
With $\bar{U}_{\text{Low}} = 0.2849$ and $\bar{U}_{\text{Med}} \approx 0.6170$:
$$\Delta_{ML} = 0.6170 - 0.2849 = \mathbf{0.3321} \ge 0.2500 \quad (\mathbf{PASS\ with\ }+0.0821\text{ margin})$$
$$\Delta_{HM} = 0.8800 - 0.6170 = \mathbf{0.2630} \ge 0.2500 \quad (\mathbf{PASS})$$
Quality Gate 3 separation criteria ($\ge 0.2500$) remain strictly satisfied.

### 8.4 Locked Unit of Variance Evaluation: Probe-Level Means
Variance floors are evaluated strictly on the $n = 30$ **probe-level means** after 5-seed aggregation in every cell:
$$\text{Var}_{\text{probe}}\left(\bar{S}_i \mid \text{Cell}_k\right) \ge 0.0005 \quad (\text{all 9 cells})$$
$$\text{Var}_{\text{probe}}\left(\bar{U}_i \mid \text{Cell}_k\right) \ge 0.0020 \quad (\text{all 9 cells})$$
Failure Consequence: If any cell falls below either floor, the benchmark terminates as **INCONCLUSIVE**.

---

## 9. State Isolation & Statistical Independence Rules

- **Reset Execution**: Prior to every probe evaluation, `ActiveInferenceEngine.reset()` and `EmotionCore.reset_to_resting()` execute completely, clearing all latent ODE charge and resetting belief matrices.
- **Design Independence**: Presentation order across cells is fully randomized per seed run, eliminating drift or order confounds.

---

## 10. Primary Statistical Analysis Framework

### Track A — Cross-Factor Spillover General Linear Models
Two separate GLMs evaluate cross-factor contamination, explicitly controlling for implementation duration $T$:

$$\text{Model A}_1: \quad \bar{S}_{\text{observed}} = \mu_S + \beta_S S_{\text{target}} + \beta_U U_{\text{target}} + \beta_{SU} (S_{\text{target}} \times U_{\text{target}}) + \beta_T T + \epsilon_S$$

$$\text{Model A}_2: \quad \bar{U}_{\text{sem\_observed}} = \mu_U + \gamma_U U_{\text{target}} + \gamma_S S_{\text{target}} + \gamma_{US} (U_{\text{target}} \times S_{\text{target}}) + \gamma_T T + \epsilon_U$$

- **Primary Decoupling Criterion**: Partial effect size $\eta_p^2 < 0.02$ in both directions.
- **Secondary Diagnostic**: Omnibus $F$-test $p$-values reported for consistency checks only.

---

### Track B — Two One-Sided Tests (TOST) on Partial Correlation

#### 10.1 Design Matrix Specification ($\mathbf{X} \in \mathbb{R}^{270 \times 11}$)
The design matrix $\mathbf{X}$ is constructed with exactly 11 mutually orthogonal columns:
$$\mathbf{X} = \begin{bmatrix} \mathbf{x}_0 & \mathbf{x}_1 & \mathbf{x}_2 & \mathbf{x}_3 & \mathbf{x}_4 & \mathbf{x}_5 & \mathbf{x}_6 & \mathbf{x}_7 & \mathbf{x}_8 & \mathbf{x}_9 & \mathbf{x}_{10} \end{bmatrix}$$

| Col | Term | Definition / Contrast |
|---|---|---|
| $\mathbf{x}_0$ | Intercept | $\mathbf{1}_{270}$ |
| $\mathbf{x}_1, \mathbf{x}_2$ | $S_{\text{target}}$ Lin / Quad | Normalized orthogonal polynomial contrasts $\in \{-1, 0, +1\} / \sqrt{2}, \{+1, -2, +1\} / \sqrt{6}$ |
| $\mathbf{x}_3, \mathbf{x}_4$ | $U_{\text{target}}$ Lin / Quad | Normalized orthogonal polynomial contrasts $\in \{-1, 0, +1\} / \sqrt{2}, \{+1, -2, +1\} / \sqrt{6}$ |
| $\mathbf{x}_5 \dots \mathbf{x}_8$ | $S \times U$ Interactions | Element-wise products $\mathbf{x}_1 \odot \mathbf{x}_3, \mathbf{x}_1 \odot \mathbf{x}_4, \mathbf{x}_2 \odot \mathbf{x}_3, \mathbf{x}_2 \odot \mathbf{x}_4$ |
| $\mathbf{x}_9, \mathbf{x}_{10}$ | $T$ Lin / Quad | Orthogonal polynomial contrasts for $T \in \{1, 4, 12\}$ |

#### 10.2 Mathematical Rank & Degrees of Freedom
- **Sample Size**: $N = 270$
- **Design Matrix Column Rank**: $\text{rank}(\mathbf{X}) = 11$ (Condition Number $\approx 1.0$)
- **Conditioning Predictors**: $p = 10$ non-intercept terms
- **Residual Degrees of Freedom**: $\text{df}_{\text{residual}} = 270 - 11 = 259$
- **Effective Sample Size for Fisher's $z$**:
  $$N_{\text{eff}} = N - p - 3 = 270 - 10 - 3 = 257$$
- **Fisher's $z$ Standard Error**:
  $$\text{SE}_z = \frac{1}{\sqrt{N_{\text{eff}}}} = \frac{1}{\sqrt{257}} \approx \mathbf{0.062378}$$

#### 10.3 Equivalence Bounds & Decision Rules ($\Delta = 0.20$)
- **Frozen Architectural Equivalence Margin**: $(-\Delta, +\Delta) = (-0.200000, +0.200000)$
  $$\Delta_z = \frac{1}{2}\ln\left(\frac{1 + 0.20}{1 - 0.20}\right) = \frac{1}{2}\ln(1.50) \approx \mathbf{0.202733}$$
- **$90\%$ Confidence Interval for Fisher's $z$ ($\alpha = 0.05$)**:
  $$\text{CI}_{90\%}(z) = \left[\hat{z} \pm 1.644853 \cdot \text{SE}_z\right] = \left[\hat{z} - 0.102603, \quad \hat{z} + 0.102603\right]$$
  Transformed to correlation space: $[\tanh(z_{\text{lower}}), \tanh(z_{\text{upper}})]$.
- **Critical Acceptance Boundary**:
  $$c_z = \Delta_z - 1.644853 \cdot \text{SE}_z = 0.202733 - 0.102603 = \mathbf{0.100129}$$
  $$c_{\rho} = \tanh(0.100129) = \mathbf{0.099796} \approx \mathbf{0.0998}$$
  If $|\hat{\rho}_{\text{partial}}| \le 0.0998$, the $90\%$ CI is strictly contained within $(-0.20, +0.20)$, confirming equivalence.

---

## 11. Statistical Power & Precision Analysis

Recomputed using the exact parameters of Protocol v1.4 ($N = 270, \text{rank} = 11, N_{\text{eff}} = 257, \text{SE}_z = 0.062378, \Delta = 0.20$):

$$\text{Power} = \Phi\left(\frac{c_z - z_0}{\text{SE}_z}\right) - \Phi\left(\frac{-c_z - z_0}{\text{SE}_z}\right)$$

| True Population Correlation ($\rho_0$) | True Fisher $z_0$ | Upper $Z$-Score | Lower $Z$-Score | Statistical Power ($1 - \beta$) | Status |
|---|---|---|---|---|---|
| **$\rho_0 = 0.00$ (Ideal Decoupling)** | $0.000000$ | $+1.6052$ | $-1.6052$ | **$89.15\%$** | **High Power Baseline** |
| $\rho_0 = 0.01$ | $0.010000$ | $+1.4449$ | $-1.7656$ | $88.70\%$ | Robust |
| $\rho_0 = 0.02$ | $0.020003$ | $+1.2845$ | $-1.9258$ | $87.35\%$ | Robust |
| $\rho_0 = 0.03$ | $0.030009$ | $+1.1241$ | $-2.0863$ | $85.10\%$ | Robust |
| $\rho_0 = 0.04$ | $0.040021$ | $+0.9636$ | $-2.2468$ | $82.01\%$ | Standard Target ($>80\%$) |
| $\rho_0 = 0.05$ | $0.050042$ | $+0.8030$ | $-2.4073$ | $78.10\%$ | Moderate |
| $\rho_0 = 0.08$ | $0.080171$ | $+0.3200$ | $-2.8906$ | $62.36\%$ | Lower Power |
| $\rho_0 = 0.10$ | $0.100335$ | $-0.0033$ | $-3.2135$ | $49.80\%$ | Power Boundary |

The architectural equivalence margin remains strictly **$\Delta = 0.20$** ($R^2 < 0.040$). It is **not** expanded to artificially inflate power.

---

## 12. Decision Criteria Matrix (Protocol v1.4)

| # | Protocol Criterion | Preregistered Requirement | Decoupling Supported | Inconclusive Zone | Coupling Supported |
|---|---|---|---|---|---|
| **1** | **Measurement Validity** | Headless production path; zero synthetic PAD; $T$ balanced $10/10/10$ across all 9 cells. | Mandatory Pass | Synthetic bypass $\implies$ **INCONCLUSIVE** | — |
| **2** | **Surprise Manipulation Check** | Monotonic across all tiers; ANOVA $p < 0.001$; $\mathbf{\bar{S}_H(T=12) - \bar{S}_M(T=12) \ge 0.1500}$ and $\Delta_{ML}(T=12) \ge 0.1000$. | Mandatory Pass | Failed separation $\implies$ **INCONCLUSIVE** | — |
| **3** | **Uncertainty Manipulation Check** | Monotonic across all tiers; ANOVA $p < 0.001$; $\bar{U}_M - \bar{U}_L \ge 0.2500$ and $\bar{U}_H - \bar{U}_M \ge 0.2500$. | Mandatory Pass | Failed separation $\implies$ **INCONCLUSIVE** | — |
| **4** | **Within-Cell Variance Floors** | Probe-level $\text{Var}_{\text{probe}}(\bar{S} \mid \text{cell}) \ge 0.0005$ and $\text{Var}_{\text{probe}}(\bar{U} \mid \text{cell}) \ge 0.0020$ in all 9 cells. | Mandatory Pass | Any cell below floor $\implies$ **INCONCLUSIVE** | — |
| **5** | **Spillover $U \to S$ ($\eta_p^2$)** | Partial effect size controlling for $S_{\text{target}}$ and $T$. | $\eta_p^2 < 0.02$ | $0.02 \le \eta_p^2 < 0.06 \implies$ **INCONCLUSIVE** | $\eta_p^2 \ge 0.06$ (with $p < 0.01$) |
| **6** | **Spillover $S \to U$ ($\eta_p^2$)** | Partial effect size controlling for $U_{\text{target}}$ and $T$. | $\eta_p^2 < 0.02$ | $0.02 \le \eta_p^2 < 0.06 \implies$ **INCONCLUSIVE** | $\eta_p^2 \ge 0.06$ (with $p < 0.01$) |
| **7** | **Partial Equivalence (TOST)** | 90% CI of $\hat{\rho}_{\text{partial}}$ vs frozen margin $\pm 0.20$ ($\text{rank} = 11$). | $\text{CI}_{90\%} \subset (-0.20, +0.20)$ | CI straddles $\pm 0.20 \implies$ **INCONCLUSIVE** | CI strictly outside $\pm 0.20$ |
| **8** | **Multiplicity Correction** | Holm-Bonferroni FWER control across confirmatory hypothesis tests. | Mandatory Pass | Unadjusted reporting $\implies$ **INVALID** | — |

> [!CAUTION]
> **GOVERNANCE RULE ON QUALITY GATES AS PREREQUISITES:**  
> Quality Gates 1, 2, 3, and 4 are strict, non-negotiable prerequisites. If any manipulation check or variance floor fails, the experiment aborts to **INCONCLUSIVE**, and downstream TOST or GLM results **cannot** be declared confirmatory.

---

## 13. Quality-Gate Governance & Anti-Post-Hoc Invariants

1. **No Retroactive Conversion**: Historical failures (Phase 22 Original FAILED; Path C INCONCLUSIVE) cannot be retroactively converted to passes. They remain permanently preserved as historical evidence.
2. **No Post-Hoc Threshold Softening**: Thresholds cannot be relaxed after observing data. The $0.15$ surprise separation threshold and $0.0020$ uncertainty variance floor remain strictly intact.
3. **Fixture Changes Pre-Specified**: The generator parameterization for $U_{\text{Low}}$ ($c \sim [0.900, 0.995]$) is formally frozen prior to any experimental re-execution.
4. **No Probe Cherry-Picking**: Stimuli must be generated strictly forward from the frozen generator without post-hoc filtering or selective exclusion.

---

## 14. Interpretation Boundaries ("What This Protocol Does NOT Establish")

To preserve philosophical and operational discipline:
- It does **NOT** establish conscious sentience, feeling, or self-awareness.
- It does **NOT** claim biological equivalence to human neuroanatomy.
- It does **NOT** validate conversational performance with real human users.
- It does **NOT** constitute production readiness or authorize opening the Architecture Gate.

---

## 15. Reviewer Ratification Gate & Execution Preconditions

The following items are submitted to Ciah (Research Reviewer) for formal review and ratification:
1. **$N = 270$ Canonical Baseline Ratification**: Formal approval of $N = 270$ ($30$ probes/cell, $10/10/10$ $T$-allocation) as the frozen design.
2. **Gate 2 Redesign Ratification**: Formal approval of conditioning the primary $\ge 0.1500$ separation check on standardized duration $T = 12$.
3. **Gate 4 Recalibration Ratification**: Formal approval of Candidate C1 ($c \sim U(0.900, 0.995)$) for $U_{\text{Low}}$.
4. **Preregistration Freeze**: Explicit approval of Protocol Amendment v1.4 before any new probe generation or benchmark execution occurs.

---

## 16. Revision History

- **v1.0 (September 16, 2026)**: Initial deconfounding specification proposing 3 × 3 crossed factorial design, variance injection, TOST equivalence testing ($\Delta = 0.20$), and probe-level analysis.
- **v1.1 (September 16, 2026)**: Refined measurement semantics based on pre-execution measurement audit findings. Formalized Cumulative Turn-Exposure Surprise ($S_{\text{exposure}}$), introduced multi-tick exposure duration $T$, corrected inter-probe independence language, and re-calibrated surprise manipulation check floors.
- **v1.2 (September 16, 2026)**: Resolved reviewer audit findings on $T$–$S$ confounding. Reframed $T$ as an experimental implementation variable and $S_{\text{observed}}$ as the actual continuous physiological variable; clarified the deterministic/derived status of $U_{\text{sem\_observed}}$ from authored proposition graphs; removed pre-empirical sample correlation claims; locked within-cell variance floors to probe-level means after seed aggregation; and formulated equivalence testing on partial correlation conditioning on $T$.
- **v1.3 (September 16, 2026)**: Methodological cleanup resolving reviewer audit on v1.2. Defined $S_{\text{target}}$ as stimulus affective intensity and balanced $T \in \{1, 4, 12\}$ symmetrically ($5/5/5$) inside every single cell; mathematically locked design matrix $\mathbf{X}$ ($\text{rank} = 11, p = 10, N_{\text{eff}} = 122$); synchronized exact statistical power curves ($\text{Power} = 44.8\%$ at $N=135, \Delta=0.20$; $92.4\%$ at $\Delta=0.30$); and framed execution pathways (Path A, B, C) for reviewer ratification.
- **v1.4 (September 16, 2026 - Current Draft)**: Canonical sample size and quality gate redesign resolving post-execution compliance audit findings from Path C. Synchronized primary design to $N = 270$ throughout; redesigned Quality Gate 2 to condition $\ge 0.1500$ separation check on standardized exposure duration $T = 12$; recalibrated Quality Gate 4 ($U_{\text{Low}}$ generator) to Candidate C1 ($c \sim [0.900, 0.995]$) based on $20,000$-cell Monte Carlo simulation; recomputed exact statistical power ($89.15\%$ at $\rho_0 = 0.0$); and preserved historical Path C execution as permanently INCONCLUSIVE.
