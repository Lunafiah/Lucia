# Phase 22 — H1 Protocol Amendment v1.3
## Methodological Cleanup: S-Target Definition, Cell-Level T Balancing, Exact Design Rank & Power Synchronization

> **Project:** Lucia — Embodied Whole-Brain Architecture  
> **Phase:** Phase 22 — Active Inference & Prospective Epistemic Foraging  
> **Subsystem:** Layer 4 (Active Inference) & Layer 2 (EmotionCore Coupled MT-LNN)  
> **Document Role:** Formal Specification & Preregistration Proposal (Design Only)  
> **Author:** Antigravity (Execution / Research Implementation Agent)  
> **Reviewer:** Ciah (Research Reviewer)  
> **Governance Status:** **[CURRENT RESEARCH / SPECIFICATION ONLY — ARCHITECTURE GATE LOCKED]**  
> **Date:** September 2026  
> **Governing Documents:** [`AGENTS.md`](file:///c:/Users/Lunafiah/Desktop/My_project/Lucia/AGENTS.md), [`docs/00_PROJECT_OVERVIEW.md`](file:///c:/Users/Lunafiah/Desktop/My_project/Lucia/docs/00_PROJECT_OVERVIEW.md), [`docs/ARCHITECTURE.md`](file:///c:/Users/Lunafiah/Desktop/My_project/Lucia/docs/ARCHITECTURE.md)  
> **Supersedes:** [`PHASE_22_H1_PROTOCOL_AMENDMENT_v1.2.md`](file:///c:/Users/Lunafiah/Desktop/My_project/Lucia/docs/specs/Lucia-phase22-Epistemic_Foraging/PHASE_22_H1_PROTOCOL_AMENDMENT_v1.2.md), [`PHASE_22_H1_PROTOCOL_AMENDMENT_v1.1.md`](file:///c:/Users/Lunafiah/Desktop/My_project/Lucia/docs/specs/Lucia-phase22-Epistemic_Foraging/PHASE_22_H1_PROTOCOL_AMENDMENT_v1.1.md), and [`PHASE_22_H1_PROTOCOL_AMENDMENT_v1.0.md`](file:///c:/Users/Lunafiah/Desktop/My_project/Lucia/docs/specs/Lucia-phase22-Epistemic_Foraging/PHASE_22_H1_PROTOCOL_AMENDMENT_v1.0.md)  
> **Reason for Amendment (v1.3):** Methodological cleanup resolving four reviewer findings on v1.2:
> 1. Formally defines $S_{\text{target}}$ as **Target Stimulus Affective Intensity** (lexical arousal and urgency tier) completely decoupled from exposure duration $T$.
> 2. Balances exposure duration $T \in \{1, 4, 12\}$ symmetrically *within every single* $S_{\text{target}} \times U_{\text{target}}$ cell ($5/5/5$ distribution across all 9 cells).
> 3. Mathematically locks the exact design matrix, contrast coding, and full column rank ($\text{rank} = 11$, $p = 10$) for Track B residualization.
> 4. Synchronizes statistical power calculations to the exact effective degrees of freedom ($N_{\text{eff}} = 122, \text{SE}_z = 0.0905$), establishing rigorous power curves and explicit inconclusive criteria.

---

## 0. Governance & Evidentiary Classification

### 0.1 Evidentiary Status
This document is a **formal research specification proposal** amending Hypothesis 1 (H1) of Phase 22.
- It does **NOT** authorize execution or benchmark reruns.
- It does **NOT** authorize modifications to `src/core/` production modules, canonical cognitive stages S1–S16, or existing orchestrators.
- It does **NOT** alter the existential Genesis Gate (`data/profile.json` remains bit-exact `{"is_onboarded": false}`).
- It does **NOT** open the Architecture Gate.

```text
Historical Evidence (H1 FAILED)
             ≠
Amended Protocol v1.3 (This Document)
             ≠
Future Experimental Execution (Pending Ratification)
             ≠
Architecture Approval Gate
             ≠
Production Realization
```

### 0.2 Canonical Historical Truth
The historical Phase 22 benchmark result recorded on September 16, 2026 (`phase22_evaluation_summary.json`, commit `5e7dbdc`) is an **immutable research artifact**:
- Observed Linear Fit: $R^2 = 0.2766, \quad r = -0.5260, \quad p = 5.433 \times 10^{-7}$
- Original Preregistered Criterion: $R^2 < 0.15$
- Canonical Historical Verdict: **FAILED**

> [!IMPORTANT]
> **Governing Historical Statement:**  
> **The original H1 primary result FAILED its preregistered statistical criterion, but its architectural interpretation as evidence of genuine S–U coupling is confounded by benchmark construction and measurement design.**  
> *The original result was not "invalid" nor is it erased; it is preserved as the empirical justification for this deconfounding amendment.*

---

## 1. Historical H1 Result & Problem Diagnosis

### 1.1 Summary of Initial Benchmark Construction
The original Phase 22 benchmark evaluated 80 probes partitioned into 8 discrete strata (10 probes each). While Hypotheses H2 (Unnecessary Question Rate reduction $= 100\%$, Wilcoxon $p = 1.60 \times 10^{-8}$) and H3 (Metabolic clarification suppression $= 100\%$) strongly met their targets, H1 exhibited a statistically significant negative correlation ($r = -0.5260, R^2 = 0.2766$).

### 1.2 Granular Audit & Root-Cause Diagnosis
An audit of [`phase22_evaluation_matrix.json`](file:///c:/Users/Lunafiah/Desktop/My_project/Lucia/tests/evaluation_phase22/results/phase22_evaluation_matrix.json) and subsequent pre-execution measurement audits identified four structural confounding factors:

1. **Zero Within-Stratum Variance in Semantic Uncertainty**:
   In all 8 strata, proposition confidences were uniform across the 10 probes within each stratum ($U_{\text{sem}} = 0.192$ in S1, $0.999$ in S2, $0.502$ in S3, $0.344$ in S4, $0.141$ in S5, $0.999$ in S6, $1.000$ in S7, $0.286$ in S8). Consequently:
   $$\text{Var}(U_{\text{sem}} \mid \text{stratum}) = 0.000 \implies r(S_t, U_{\text{sem}} \mid \text{stratum}) \text{ was mathematically degenerate / non-informative ($0/0$)}.$$
2. **Simpson's Paradox & Bimodal Cluster Leverage**:
   The cross-benchmark negative correlation was generated by the macro-placement of scenario clusters: Stratum 5 paired extreme surprise ($S_t \approx 0.735$) with trivial semantic uncertainty ($U_{\text{sem}} = 0.141$), while Strata 2, 6, and 7 paired minimal surprise ($S_t \approx 0.05-0.10$) with maximal semantic uncertainty ($U_{\text{sem}} \approx 1.000$). These opposing clusters anchored opposite corners of the scatter, artificially forcing an aggregate downward slope.
3. **Exploratory Ablation Evidence**:
   Excluding Stratum 5 ($N=70$) dropped $R^2$ to **$0.1168$** ($p = 0.0038 < 0.15$), and ecological regression across stratum means was non-significant ($p = 0.179$). However, post-hoc exclusion of inconvenient data cannot convert a failed result into a pass; prospective deconfounding is mandatory.
4. **Synthetic Bypass & Physical Envelope Disconnect**:
   The original benchmark manually assigned `surprise_s = 0.68 + 0.01 * i` and `pad_final = (0.40, 0.75, 0.10)` in probe dataclasses. The measurement audit revealed that in a single ODE tick ($dt = 0.1\text{s}$) starting from resting Philia equilibrium, continuous MT-LNN dynamics physically bounds displacement to $\|\Delta\mathbf{p}\|_2 \le 0.122$. Reaching $S \ge 0.60$ dynamically requires accumulated multi-tick exposure.

---

## 2. Revised H1 Research Question

The amended H1 protocol investigates:

> **Are retrospective physiological prediction surprise ($S_{\text{observed}}$) and semantic uncertainty ($U_{\text{sem\_observed}}$) empirically separable operational dimensions in Lucia's cognitive architecture, or does variation in one dimension induce cross-factor spillover or non-negligible shared variance in the other when evaluated across varied exposure durations and stimulus intensities?**

---

## 3. Operational Definitions & Ontological Variable Classification

To eliminate conceptual confusion between engineering instruments, physiological states, and propositional definitions, variables are formally categorized as follows:

| Concept | Ontological Status | Mathematical / System Entity | Operational Range | Role in Experiment |
|---|---|---|---|---|
| **Target Stimulus Affective Intensity ($S_{\text{target}}$)** | **Manipulated Experimental Factor** | Lexical arousal, valence extremity, and urgency tier of authored probe text: $\{S_L, S_M, S_H\}$. | Qualitative factor levels: Low/Neutral, Moderate, High Urgency. | Manipulated stimulus factor driving differential limbic input forcing. |
| **Exposure Duration ($T$)** | **Experimental Implementation Variable** | Number of discrete integration ticks ($dt = 0.10\text{s}$) through `EmotionCore.commit_stimulus()`. | $T \in \{1, 4, 12\}$ ticks ($0.10\text{s} - 1.20\text{s}$). | Engineering vehicle allowing continuous ODE trajectories to unfold; balanced $5/5/5$ in every cell; controlled covariate in statistical models. |
| **Observed Physiological Surprise ($S_{\text{observed}}$)** | **Actual Continuous Physiological Variable** | Euclidean norm between prior predicted PAD state $\hat{\mathbf{p}}_0 = \mathbf{A}\mathbf{p}_0 + \mathbf{b}$ captured at Stage 2 and committed post-stimulus limbic PAD state $\mathbf{p}_T$ after $T$ integration ticks at Stage 4: $$S_{\text{observed}} = S_{\text{exposure}} = \|\hat{\mathbf{p}}_0 - \mathbf{p}_T\|_2$$ | $[0.0, \sqrt{12}] \approx [0.0, 3.46]$; operational envelope $[0.002, 0.85]$. | Primary continuous physiological dependent variable representing retrospective prediction error. |
| **Instantaneous Single-Tick Surprise ($S_t$)** | **Canonical Single-Transition Entity** | Euclidean prediction error across exactly one tick ($T=1$): $$S_t = \|\hat{\mathbf{p}}_{t-1} - \mathbf{p}_t\|_2$$ | Physical single-step bound from Philia: $[0.00, 0.122]$. | Canonical subsystem entity; $S_{\text{observed}} \equiv S_t$ when $T=1$. |
| **Semantic Uncertainty Target ($U_{\text{target}}$)** | **Manipulated Experimental Factor** | Target uncertainty tier parameterizing the authored proposition graph: $\{U_L, U_M, U_H\}$. | Qualitative factor levels: Low ($0.10-0.25$), Med ($0.45-0.60$), High ($0.80-0.95$). | Manipulated experimental factor parameterizing probe candidate propositions. |
| **Observed Semantic Uncertainty ($U_{\text{sem\_observed}}$)** | **Deterministic / Derived Propositional Metric** | Normalized aggregate binary Shannon entropy across retrieved proposition set $P = \{p_1, \dots, p_K\}$: $$U_{\text{sem\_observed}} = \frac{1}{|P|} \sum_{i=1}^{|P|} H(c_i)$$ where $H(c_i) = -c_i \log_2 c_i - (1-c_i) \log_2(1-c_i)$. | $[0.0, 1.0]$ bits/proposition. | Derived measurement verifying realized propositional entropy of authored candidate memory/knowledge graph. |
| **Active Inference Generative Model** | **Generative Substrate** | 3x3 linear transition model $\hat{\mathbf{p}}_t = \mathbf{A}\mathbf{p}_{t-1} + \mathbf{b}$ updating online via analytic free energy gradients with KL regularization toward identity. | Matrix $\mathbf{A} \in [-2.0, 2.0]^{3 \times 3}$, vector $\mathbf{b} \in \mathbb{R}^3$. | Substrate generating prediction expectations. |
| **Coupled MT-LNN Limbic Core** | **Limbic Substrate** | Fast reactive hidden state $\mathbf{h} \in \mathbb{R}^{32}$ and slow latent field $\mathbf{s}_{\text{slow}} \in \mathbb{R}^{16}$ integrated via RK45 differential equations. | Bounded in $[-1.0, 1.0]$. | Substrate integrating sensory stimulus across time. |

### 3.1 Ontological Clarification on Semantic Uncertainty ($U_{\text{sem}}$)
In the full embodied Lucia runtime, $U_{\text{sem}}$ is calculated from propositions retrieved from long-term memory (SDM/Episodic) where affective resonance (Ecphory) can dynamically modulate retrieval salience.  
In this isolated H1 deconfounding harness:
- Candidate propositions and their confidences $\{c_i\}$ are authored fixtures parameterizing $U_{\text{target}}$.
- Therefore, **$U_{\text{target}}$ is an experimental construction**, and **$U_{\text{sem\_observed}}$ is a deterministic / derived measurement from the authored proposition set**.
- $U_{\text{sem\_observed}}$ is NOT an emergent, differential-equation-driven physiological state like $S_{\text{observed}}$. It functions as an empirical verification of the exact realized propositional entropy of the stimulus scenario.

---

## 4. Target Factors, Implementation Variables & Observed Measurements

The amendment enforces causal clarity between experimental inputs, implementation variables, and observed system states:

```text
┌────────────────────────────────────────────────────────┐
│             EXPERIMENTAL MANIPULATION TARGETS          │
│   • Target Stimulus Affective Intensity: S_target      │
│     S_target ∈ {S_Low, S_Med, S_High} (Text Arousal)   │
│   • Semantic Uncertainty Target: U_target              │
│     U_target ∈ {U_Low, U_Med, U_High} (Proposition H)  │
└──────────────────────────┬─────────────────────────────┘
                           │
                           │ Parameterizes 9 crossed cells
                           ▼
┌────────────────────────────────────────────────────────┐
│             MANIPULATED STIMULUS PROBE (N=135)         │
│   • 15 unique probes per cell                          │
│   • Pre-turn PAD state p_0 (Resting Philia baseline)   │
│   • Authored candidate propositions with confidences c │
└──────────────────────────┬─────────────────────────────┘
                           │
                           │ Paired with balanced implementation duration
                           ▼
┌────────────────────────────────────────────────────────┐
│         CELL-LEVEL IMPLEMENTATION BALANCING            │
│   • Exposure duration T ∈ {1, 4, 12} ticks             │
│   • Exactly 5 probes T=1, 5 probes T=4, 5 probes T=12  │
│     WITHIN EVERY SINGLE CELL (5/5/5 in all 9 cells)    │
│   • Strictly orthogonal to S_target and U_target       │
└──────────────────────────┬─────────────────────────────┘
                           │
                           │ Executes headless pipeline
                           ▼
┌────────────────────────────────────────────────────────┐
│        LUCIA ARCHITECTURAL MEASUREMENT PIPELINE        │
│   1. StimulusProcessor.encode(text)                    │
│   2. EmotionCore.get_pad_state() -> p_0                │
│   3. T × EmotionCore.commit_stimulus() -> p_T          │
│   4. ActiveInferenceEngine.step(p_0, p_T) -> S_obs     │
│   5. Derived Proposition Entropy -> U_sem_obs          │
└──────────────────────────┬─────────────────────────────┘
                           │
                           │ Emits
                           ▼
┌────────────────────────────────────────────────────────┐
│             OBSERVED MEASUREMENTS (EVALUATED)          │
│   • S_observed = S_exposure = ||p_hat_0 - p_T||_2      │
│   • U_sem_observed = (1/K) * sum H(c_i)                │
└──────────────────────────┬─────────────────────────────┘
                           │
                           │ Evaluated in
                           ▼
┌────────────────────────────────────────────────────────┐
│             PRIMARY STATISTICAL ANALYSIS               │
│   • Spillover GLM: S_obs ~ S_target + U_target + T     │
│   • Equivalence Testing: Partial Corr(S_obs, U_obs)    │
│     controlling for design matrix X (rank = 11)        │
│   • Primary evidence: Effect sizes & TOST 90% CI       │
└────────────────────────────────────────────────────────┘
```

---

## 5. Dynamic Measurement Path & API Invariants

### 5.1 Canonical Execution Sequence
In accordance with [`PHASE_22_H1_MEASUREMENT_AUDIT_REPORT.md`](file:///c:/Users/Lunafiah/Desktop/My_project/Lucia/docs/specs/Lucia-phase22-Epistemic_Foraging/PHASE_22_H1_MEASUREMENT_AUDIT_REPORT.md), $S_{\text{observed}}$ is obtained by executing the genuine headless production pipeline:

```python
# 1. Initialize headless production components
sp = StimulusProcessor(StimulusConfig())
core = EmotionCore(EmotionConfig())  # Thread not started (synchronous mode)
ai = ActiveInferenceEngine(ActiveInferenceConfig())

# 2. Ingest and encode text surface (Stage 1)
stimulus = sp.encode(probe.stimulus_text)

# 3. Capture prior expectation baseline (Stage 2)
pad_before = core.get_pad_state()

# 4. Integrate stimulus over balanced exposure duration T (Stage 3)
pad_after: PADState
for _ in range(probe.exposure_ticks):
    token = core.push_stimulus(stimulus)
    pad_after = core.commit_stimulus(token)

# 5. Measure genuine turn-level prediction error (Stage 4)
s_observed = ai.step(pad_before, pad_after)

# 6. Compute derived proposition entropy
u_sem_observed = compute_proposition_entropy(probe.propositions)
```

### 5.2 Strict Prohibition Against Synthetic Bypass
The following patterns are formally classified as **SYNTHETIC SURROGATE / MEASUREMENT BYPASS** and are strictly forbidden:
1. Setting `record.surprise_s = probe.surprise_s` directly from a static fixture attribute.
2. Hardcoding `pad_final = (P, A, D)` as a tuple inside the probe dataclass.
3. Passing a manually crafted `pad_final` tuple into `ActiveInferenceEngine.step(pad_initial, pad_final)`.
4. Replacing `EmotionCore` with a mock class that bypasses RK45 integration.

---

## 6. Multi-Tick Measurement Semantics & Construct Validity

### 6.1 Formal Definition of $S_{\text{exposure}}$ vs. $S_t$
The measurement audit demonstrated that in a single ODE tick ($dt = 0.1\text{s}$), continuous MT-LNN relaxation dynamics ($\tau_{\text{fast}} \ge 0.10\text{s}$) physically bounds state displacement to $\|\Delta\mathbf{p}\|_2 \le 0.122$ from resting Philia.

To evaluate surprise across a scientifically meaningful dynamic range without synthetic fixture bypass, the protocol adopts **Cumulative Turn-Exposure Surprise ($S_{\text{exposure}}$)**:
$$S_{\text{exposure}} = \|\hat{\mathbf{p}}_0 - \mathbf{p}_T\|_2 = \|\mathbf{A}\mathbf{p}_0 + \mathbf{b} - \mathbf{p}_T\|_2$$
where $\mathbf{p}_0$ is the initial limbic state at Stage 2 before stimulus integration, and $\mathbf{p}_T$ is the committed post-stimulus limbic state after $T$ ticks of sensory exposure.

### 6.2 Construct Validity Justification
1. **Turn-Level Operational Meaning**: In Lucia's embodied cognitive architecture ([`src/core/orchestrator/cognitive_orchestrator.py`](file:///c:/Users/Lunafiah/Desktop/My_project/Lucia/src/core/orchestrator/cognitive_orchestrator.py)), a conversation turn is an extended acoustic/semantic event. Stage 2 captures the prior expectation before the utterance; Stage 3 integrates the sensory input across the utterance duration; Stage 4 reads the resulting committed limbic state and updates beliefs. `ActiveInferenceEngine.step()` is called **exactly once per turn**, comparing the pre-turn expectation to the post-turn commitment.
2. **Equivalence at $T=1$**: For an instantaneous single-tick prompt ($T=1$), $S_{\text{exposure}} \equiv S_t$.
3. **Relevance to H1**: The scientific question of H1 is whether the magnitude of the physiological limbic disruption elicited by an incoming utterance couples with the propositional uncertainty of the candidate memory/knowledge propositions. $S_{\text{exposure}}$ directly measures this physiological displacement.

### 6.3 Absolute Boundary Regarding Canonical $S > 0.60$ Trigger
> [!CAUTION]
> **DISENTANGLING H1 FROM THE S > 0.60 DELIBERATIVE TRIGGER:**  
> Exposure duration $T$ is used solely as an experimental implementation variable to allow the continuous ODE to express its dynamic range.  
> **H1 is NOT a benchmark of whether the canonical deliberative trigger ($S > 0.60$) is optimal or calibrated.**  
> The $S > 0.60$ threshold remains an immutable production architectural property; it must NOT be recalibrated or tuned as part of this H1 deconfounding amendment.

---

## 7. Experimental Design: Definition of $S_{\text{target}}$ & Within-Cell $T$ Balancing

### 7.1 Separation of $S_{\text{target}}$ from $T$
In v1.1 and v1.2, $T$ was varied across cells but was confounded with $S_{\text{target}}$ because each surprise tier was assigned a single duration ($S_L \to T=1, S_M \to T=4, S_H \to T=12$).  
In v1.3, this confounding is completely eliminated:

1. **$S_{\text{target}}$ is Defined by Stimulus Content**:
   - $S_{\text{Low}}$: Calm / neutral phrasing, baseline informational tone, zero affective markers (Lexical Arousal $\approx 0.0$, Valence $\approx 0.0$).
   - $S_{\text{Med}}$: Mild affective tension, conversational surprise, expressive phrasing (Lexical Arousal $\approx 0.40 - 0.60$).
   - $S_{\text{High}}$: Urgent vocabulary, high emotional intensity, exclamations, emergency framing (Lexical Arousal $\ge 0.80$, extreme Valence).
2. **Exposure Duration $T$ is Balanced Within Every Single Cell**:
   Within each of the 9 cells of $n = 15$ probes:
   - Exactly $5$ probes have $T = 1\text{ tick}$ ($0.10\text{s}$)
   - Exactly $5$ probes have $T = 4\text{ ticks}$ ($0.40\text{s}$)
   - Exactly $5$ probes have $T = 12\text{ ticks}$ ($1.20\text{s}$)
   $$\sum T\text{-allocations} = 5 + 5 + 5 = 15\text{ probes per cell}$$

### 7.2 Balanced Factorial Matrix ($3 \times 3 \times [3_T]$)

```text
                       Semantic Uncertainty Target (U_target)
                        Low (0.10–0.25)       Med (0.45–0.60)       High (0.80–0.95)
                     ┌─────────────────────┬─────────────────────┬─────────────────────┐
  S_Low Target       │       Cell 1        │       Cell 2        │       Cell 3        │
  (Calm text)        │  5×T=1, 5×T=4, 5×T=12│  5×T=1, 5×T=4, 5×T=12│  5×T=1, 5×T=4, 5×T=12│
Stimulus             ├─────────────────────┼─────────────────────┼─────────────────────┤
Affect Target        │       Cell 4        │       Cell 5        │       Cell 6        │
  S_Med Target       │  5×T=1, 5×T=4, 5×T=12│  5×T=1, 5×T=4, 5×T=12│  5×T=1, 5×T=4, 5×T=12│
(S_target)           ├─────────────────────┼─────────────────────┼─────────────────────┤
                     │       Cell 7        │       Cell 8        │       Cell 9        │
  S_High Target      │  5×T=1, 5×T=4, 5×T=12│  5×T=1, 5×T=4, 5×T=12│  5×T=1, 5×T=4, 5×T=12│
  (Urgent text)      │  [Old Stratum 5]    │  5×T=1, 5×T=4, 5×T=12│  5×T=1, 5×T=4, 5×T=12│
                     └─────────────────────┴─────────────────────┴─────────────────────┘
```

### 7.3 Mathematical Orthogonality Properties
By virtue of the identical $5/5/5$ within-cell allocation:
1. **$T \perp S_{\text{target}}$**: Across all 45 probes in $S_{\text{Low}}$, exactly 15 have $T=1$, 15 have $T=4$, 15 have $T=12$. The same holds identically for $S_{\text{Med}}$ and $S_{\text{High}}$.
2. **$T \perp U_{\text{target}}$**: Across all 45 probes in $U_{\text{Low}}$, exactly 15 have $T=1$, 15 have $T=4$, 15 have $T=12$. The same holds identically for $U_{\text{Med}}$ and $U_{\text{High}}$.
3. **$T \perp (S_{\text{target}} \times U_{\text{target}})$**: Within every individual interaction cell, the marginal distribution of $T$ is identical.
4. **Zero Structural Confounding**: Exposure duration carries zero design information about stimulus affect or semantic uncertainty.

### 7.4 Sample Allocation & Statistical Unit
- **Sample Allocation**: Exactly $n = 15$ unique probes per cell ($N = 135$ total probes across 9 cells).
- **Repeated Environmental Seeds**: 5 canonical fixed seeds ($42, 43, 44, 45, 46$).
- **Total Evaluations**: $135 \times 5 = 675$ evaluations per condition ($2,025$ evaluations across 3 conditions).
- **Unit of Statistical Analysis**: The **Probe** ($N = 135$). For each probe, seed observations are averaged across the 5 seeds to form a single probe-level mean $(\bar{S}_i, \bar{U}_i)$ prior to primary statistical modeling.

---

## 8. Exposure Assignment & Quality Controls

### 8.1 Design Independence by Construction
> **Design Balance Invariant:**  
> Exposure duration $T$ is assigned independently of $U_{\text{target}}$ and $S_{\text{target}}$, with identical marginal exposure-duration allocation ($5/5/5$) across all 9 cells.
- This structural orthogonality is guaranteed by experimental construction, preventing any information leakage between exposure duration, stimulus affect, and semantic uncertainty.
- Domain balancing: Semantic domains (system telemetry, project status, relational milestones, factual knowledge) are evenly distributed across all 9 cells.
- Randomized presentation order: Probe presentation order is fully randomized across cells for every seed run, eliminating sequence, warm-up, or drift confounds.

---

## 9. Manipulation Checks & Quality Gates

Before testing the primary decoupling hypothesis, the dataset must satisfy two independent, confirmatory manipulation checks:

### 9.1 Surprise Manipulation Check
- **Objective**: Verify that stimuli and implementation exposure parameters reliably manipulate $S_{\text{observed}}$ through the production pipeline.
- **Criteria**:
  1. Execution of genuine production pipeline verified (zero synthetic PAD injection).
  2. Main effect of stimulus affect target $S_{\text{target}}$ on $S_{\text{observed}}$ is statistically significant: $p < 0.001$.
  3. Monotonic separation across target tiers: $\bar{S}_{\text{observed}}(S_L) < \bar{S}_{\text{observed}}(S_M) < \bar{S}_{\text{observed}}(S_H)$.
  4. Minimum separation thresholds:
     $$\bar{S}_{\text{observed}}(S_M) - \bar{S}_{\text{observed}}(S_L) \ge 0.10$$
     $$\bar{S}_{\text{observed}}(S_H) - \bar{S}_{\text{observed}}(S_M) \ge 0.15$$
- **Failure Consequence**: If unmet, the surprise manipulation is invalid; experiment aborts to **INCONCLUSIVE**.

### 9.2 Semantic Uncertainty Manipulation Check
- **Objective**: Verify that authored proposition graphs for $U_{\text{target}}$ produce properly separated derived entropy values $U_{\text{sem\_observed}}$.
- **Criteria**:
  1. Main effect of $U_{\text{target}}$ on $U_{\text{sem\_observed}}$ is statistically significant: $p < 0.001$.
  2. Monotonic separation: $\bar{U}_{\text{sem\_observed}}(U_L) < \bar{U}_{\text{sem\_observed}}(U_M) < \bar{U}_{\text{sem\_observed}}(U_H)$.
  3. Minimum separation thresholds:
     $$\bar{U}_{\text{sem\_observed}}(U_M) - \bar{U}_{\text{sem\_observed}}(U_L) \ge 0.25$$
     $$\bar{U}_{\text{sem\_observed}}(U_H) - \bar{U}_{\text{sem\_observed}}(U_M) \ge 0.25$$
- **Failure Consequence**: If unmet, the uncertainty manipulation is invalid; experiment aborts to **INCONCLUSIVE**.

---

## 10. Within-Cell Variance Requirements & Anti-Cherry-Picking

To eliminate the degenerate $r = 0.000$ artifact of the original benchmark without introducing post-hoc selection bias, the experiment enforces a strictly forward methodological sequence:

```text
Predefined stimulus distributions
              ↓
Runtime measurement pipeline
              ↓
Observed variance evaluation on probe-level means
              ↓
Accept / Reject manipulation validity (Never regenerate to fit)
```

### 10.1 Forward Authoring Rules
> [!CAUTION]
> **STRICT PROHIBITION AGAINST POST-HOC VARIANCE TUNING:**  
> Probes must **NOT** be generated by trial-and-error filtering or retaining only probes that happen to hit variance targets. That would constitute post-hoc selection bias. Stimuli must be generated from fixed, predefined distributions prior to execution.

1. **In Surprise**: Probes within each cell are authored with varied lexical phrasing, punctuation intensity, and syntactic density so that observed $S_{\text{observed}}$ exhibits natural continuous variation around the cell centroid.
2. **In Uncertainty**: Probes within each cell feature varying numbers of candidate propositions ($K \in \{2, 3, 4\}$) and varying calibrated confidences drawn from predefined uniform distribution windows (e.g., $c \sim U(0.75, 0.88)$ in Medium uncertainty), rather than constant scalars.

### 10.2 Locked Unit of Variance Evaluation: Probe-Level Means After Seed Aggregation
For each cell $k \in \{1, \dots, 9\}$, containing $n = 15$ probes:
For each probe $i \in \{1, \dots, n\}$, seed aggregation produces the mean across 5 seeds:
$$\bar{S}_{k,i} = \frac{1}{5}\sum_{s=1}^5 S_{k,i,s}, \qquad \bar{U}_{k,i} = \frac{1}{5}\sum_{s=1}^5 U_{k,i,s}$$
The within-cell variance floors are evaluated strictly on these $n = 15$ **probe-level means**:
$$\text{Var}_{\text{probe}}\left(\bar{S}_i \mid \text{Cell}_k\right) = \frac{1}{n-1}\sum_{i=1}^n \left(\bar{S}_{k,i} - \bar{S}_k\right)^2 \ge 0.0005 \quad (\text{SD}_{\text{probe}} \ge 0.0224)$$
$$\text{Var}_{\text{probe}}\left(\bar{U}_i \mid \text{Cell}_k\right) = \frac{1}{n-1}\sum_{i=1}^n \left(\bar{U}_{k,i} - \bar{U}_k\right)^2 \ge 0.0020 \quad (\text{SD}_{\text{probe}} \ge 0.0447)$$

> [!WARNING]
> **PROHIBITION AGAINST RAW SEED VARIANCE EVALUATION:**  
> Computing variance across all $15 \times 5 = 75$ raw observations per cell is strictly forbidden. Raw seed observations pool inter-seed environmental stochasticity with inter-probe stimulus variance, which would artificially inflate variance and mask degenerate, constant-stimulus probes.
>
> If any cell fails these probe-level variance floors upon runtime measurement, the manipulation validity for that cell is rejected and the benchmark terminates as **INCONCLUSIVE**. Selectively regenerating probes to force variance compliance is prohibited.

---

## 11. State Isolation & Statistical Independence

### 11.1 Methodological Correction on Inter-Probe Independence
> [!NOTE]
> **CORRECTION OF INDEPENDENCE CLAIM:**  
> Resetting runtime state demonstrates **state isolation and complete absence of designed cross-probe state carry-over**. Statistical independence between probe observations is an **experimental design assumption** established through isolated execution and randomization, not a mathematically guaranteed covariance identity.

### 11.2 Inter-Probe Reset Protocol
Between consecutive probe evaluations:
1. `ActiveInferenceEngine.reset()` is invoked, restoring belief parameters to $\mathbf{A} = \mathbf{I}_{3 \times 3}, \mathbf{b} = \mathbf{0}_3$.
2. `EmotionCore.reset_to_resting()` is invoked (or a fresh `EmotionCore` instance is initialized), restoring $\mathbf{h} = \mathbf{0}_{32}, \mathbf{s}_{\text{slow}} = \mathbf{s}^*_{\text{philia}}, \mathbf{m}_{\text{homeo}} = \mathbf{m}^*$, draining all pending stimuli, and resetting synaptic weights with `_INIT_SEED = 42`.
3. RAM garbage collection is triggered, preventing memory-leak side effects.

---

## 12. Primary Statistical Analysis Framework

The primary analysis comprises two complementary inferential tracks, adhering strictly to the principle that **effect size and equivalence bounds constitute primary evidence**, while **$p$-values serve as supporting diagnostics**:

### Track A — Cross-Factor Spillover Modeling (General Linear Models)
Two separate general linear models test for directional cross-factor spillover, explicitly incorporating the orthogonal implementation variable $T$:

$$\text{Model A}_1: \quad S_{\text{observed}} = \mu_S + \beta_S S_{\text{target}} + \beta_U U_{\text{target}} + \beta_{SU} (S_{\text{target}} \times U_{\text{target}}) + \beta_T T + \epsilon_S$$

$$\text{Model A}_2: \quad U_{\text{sem\_observed}} = \mu_U + \gamma_U U_{\text{target}} + \gamma_S S_{\text{target}} + \gamma_{US} (U_{\text{target}} \times S_{\text{target}}) + \gamma_T T + \epsilon_U$$

- **Primary Inferential Metric**: Partial eta-squared ($\eta_p^2$).
  - **Decoupling Supported (Negligible Spillover)**:
    $$\eta_p^2(U \to S \mid S_{\text{target}}, T) < 0.02 \quad \text{and} \quad \eta_p^2(S \to U \mid U_{\text{target}}, T) < 0.02$$
  - **Coupling Supported (Substantial Spillover)**:
    $$\eta_p^2(U \to S \mid S_{\text{target}}, T) \ge 0.06 \quad \text{or} \quad \eta_p^2(S \to U \mid U_{\text{target}}, T) \ge 0.06$$
  - **Intermediate / Inconclusive Zone**:
    $$0.02 \le \eta_p^2 < 0.06 \implies \text{INTERMEDIATE EFFECT / INCONCLUSIVE}$$
- **Supporting Diagnostic**: Omnibus $F$-test $p$-value ($p > 0.05$ reported as secondary consistency check; does not alone prove absence of coupling).

---

### Track B — Equivalence Testing on Partial Association (TOST)

To evaluate whether residual continuous physiological surprise $S_{\text{observed}}$ and semantic uncertainty $U_{\text{sem\_observed}}$ share non-negligible variance after conditioning on the experimental design:

#### 12.1 Design Matrix Specification & Exact Rank
For $N = 135$ probe-level observations, the conditioning design matrix $\mathbf{X} \in \mathbb{R}^{135 \times 11}$ is constructed with exactly $11$ orthogonal columns:

$$\mathbf{X} = \begin{bmatrix} \mathbf{x}_0 & \mathbf{x}_1 & \mathbf{x}_2 & \mathbf{x}_3 & \mathbf{x}_4 & \mathbf{x}_5 & \mathbf{x}_6 & \mathbf{x}_7 & \mathbf{x}_8 & \mathbf{x}_9 & \mathbf{x}_{10} \end{bmatrix}$$

| Column Index | Variable / Term | Contrast Definition (Normalized Orthogonal Polynomial) | Column Properties |
|---|---|---|---|
| $\mathbf{x}_0$ | **Intercept** | $\mathbf{1}_{135}$ | Constant vector |
| $\mathbf{x}_1$ | $S_{\text{target}}$ Linear | $\mathbf{c}_{S,\text{lin}} \in \{-1, 0, +1\} / \sqrt{2}$ | Orthogonal main effect |
| $\mathbf{x}_2$ | $S_{\text{target}}$ Quadratic | $\mathbf{c}_{S,\text{quad}} \in \{+1, -2, +1\} / \sqrt{6}$ | Orthogonal main effect |
| $\mathbf{x}_3$ | $U_{\text{target}}$ Linear | $\mathbf{c}_{U,\text{lin}} \in \{-1, 0, +1\} / \sqrt{2}$ | Orthogonal main effect |
| $\mathbf{x}_4$ | $U_{\text{target}}$ Quadratic | $\mathbf{c}_{U,\text{quad}} \in \{+1, -2, +1\} / \sqrt{6}$ | Orthogonal main effect |
| $\mathbf{x}_5$ | $S_{\text{lin}} \times U_{\text{lin}}$ | $\mathbf{x}_1 \odot \mathbf{x}_3$ | Orthogonal interaction |
| $\mathbf{x}_6$ | $S_{\text{lin}} \times U_{\text{quad}}$ | $\mathbf{x}_1 \odot \mathbf{x}_4$ | Orthogonal interaction |
| $\mathbf{x}_7$ | $S_{\text{quad}} \times U_{\text{lin}}$ | $\mathbf{x}_2 \odot \mathbf{x}_3$ | Orthogonal interaction |
| $\mathbf{x}_8$ | $S_{\text{quad}} \times U_{\text{quad}}$ | $\mathbf{x}_2 \odot \mathbf{x}_4$ | Orthogonal interaction |
| $\mathbf{x}_9$ | $T$ Linear | $\mathbf{c}_{T,\text{lin}} \in \{-1, 0, +1\} / \sqrt{2}$ ($T \in \{1, 4, 12\}$) | Orthogonal implementation main effect |
| $\mathbf{x}_{10}$ | $T$ Quadratic | $\mathbf{c}_{T,\text{quad}} \in \{+1, -2, +1\} / \sqrt{6}$ ($T \in \{1, 4, 12\}$) | Orthogonal implementation main effect |

#### 12.2 Rank & Degrees of Freedom Proof
- Because $T$ is balanced with exactly $5/5/5$ probes in every single cell, the implementation columns $\mathbf{x}_9, \mathbf{x}_{10}$ are **strictly orthogonal** to the 8 design columns $\mathbf{x}_1 \dots \mathbf{x}_8$ and to the intercept $\mathbf{x}_0$.
- All 11 columns are mutually orthogonal: $\mathbf{X}^\top \mathbf{X}$ is a diagonal matrix.
- **Exact Rank of $\mathbf{X}$**:
  $$\text{rank}(\mathbf{X}) = 11 \quad (\text{Full Column Rank, Condition Number } = 1.0)$$
- **Number of Conditioning Predictors (excluding intercept)**:
  $$p = 10$$
- **Residual Degrees of Freedom**:
  $$\text{df}_{\text{residual}} = N - \text{rank}(\mathbf{X}) = 135 - 11 = 124$$
- **Effective Sample Size for Partial Correlation Fisher $z$**:
  $$N_{\text{eff}} = N - p - 3 = 135 - 10 - 3 = 122$$
- **Exact Fisher's $z$ Standard Error**:
  $$\text{SE}_z = \frac{1}{\sqrt{N_{\text{eff}}}} = \frac{1}{\sqrt{122}} \approx 0.090535$$

#### 12.3 Residualization & Confidence Interval
1. *Residualization*:
   $$\bar{S}_i = \mathbf{X}_i \hat{\boldsymbol{\beta}} + e_{S,i}, \qquad \bar{U}_i = \mathbf{X}_i \hat{\boldsymbol{\gamma}} + e_{U,i}$$
2. *Sample Partial Correlation*:
   $$\hat{\rho}_{\text{partial}} = \frac{\sum_{i=1}^{135} e_{S,i} e_{U,i}}{\sqrt{\sum_{i=1}^{135} e_{S,i}^2 \sum_{i=1}^{135} e_{U,i}^2}}$$
3. *Fisher's $z$ Transformation*:
   $$\hat{z} = \frac{1}{2} \ln \left(\frac{1 + \hat{\rho}_{\text{partial}}}{1 - \hat{\rho}_{\text{partial}}}\right)$$
4. *Two One-Sided Tests (TOST) at $\alpha = 0.05$*:
   The $90\%$ confidence interval for $z$ is:
   $$\text{CI}_{90\%}(z) = \left[\hat{z} - 1.644853 \cdot \text{SE}_z, \quad \hat{z} + 1.644853 \cdot \text{SE}_z\right] = \left[\hat{z} - 0.148916, \quad \hat{z} + 0.148916\right]$$
   Transformed back to correlation space: $[\tanh(z_{\text{lower}}), \tanh(z_{\text{upper}})]$.
5. *Decoupling Decision Rules*:
   - **Equivalence Confirmed (Decoupling Supported)**: $\text{CI}_{90\%}(\rho) \subset (-\Delta, +\Delta)$.
   - **Coupling Confirmed**: $\text{CI}_{90\%}(\rho)$ strictly outside $(-\Delta, +\Delta)$.
   - **Indeterminate / Inconclusive**: $\text{CI}_{90\%}(\rho)$ straddles either boundary $-\Delta$ or $+\Delta$.

---

## 13. Synchronized Statistical Power & Sample Size Analysis

### 13.1 Mathematical Power Formulation for TOST
Under the exact locked parameters ($N_{\text{eff}} = 122, \text{SE}_z = 0.090535$), TOST rejects both null hypotheses ($H_{01}: z \le -\Delta_z$ and $H_{02}: z \ge +\Delta_z$) if and only if the sample estimate $\hat{z}$ falls within the interior acceptance interval:
$$\hat{z} \in \left(-\Delta_z + 1.644853 \cdot \text{SE}_z, \quad +\Delta_z - 1.644853 \cdot \text{SE}_z\right)$$
where $\Delta_z = \frac{1}{2}\ln\left(\frac{1+\Delta}{1-\Delta}\right)$.

When true population correlation is zero ($\rho_0 = 0 \implies z_0 = 0$), statistical power $1 - \beta$ is:
$$\text{Power} = \Phi\left(\frac{\Delta_z - 1.644853 \cdot \text{SE}_z}{\text{SE}_z}\right) - \Phi\left(\frac{-\Delta_z + 1.644853 \cdot \text{SE}_z}{\text{SE}_z}\right)$$

### 13.2 Exact Power Matrix
Computing across candidate equivalence margins and sample size allocations yields:

| Sample Size ($N$) | Alloc. / Cell ($n$) | Eff. $N_{\text{eff}}$ | $\text{SE}_z$ | Power ($\Delta = 0.20$) | Power ($\Delta = 0.25$) | Power ($\Delta = 0.30$) |
|---|---|---|---|---|---|---|
| **$N = 135$ (Current Baseline)** | $15$ probes/cell | **$122$** | **$0.0905$** | **$44.78\%$** | **$76.05\%$** | **$92.39\%$** |
| $N = 180$ | $20$ probes/cell | $167$ | $0.0774$ | $67.05\%$ | $91.75\%$ | $98.81\%$ |
| $N = 225$ | $25$ probes/cell | $212$ | $0.0687$ | $80.95\%$ | $97.28\%$ | $99.85\%$ |
| $N = 270$ | $30$ probes/cell | $257$ | $0.0624$ | $89.15\%$ | $99.14\%$ | $99.98\%$ |

### 13.3 Methodological Implications & Reviewer Decision Framing
1. **At $N = 135$ and $\Delta = 0.20$**: Power to confirm equivalence is **$44.78\%$**. The critical bound is $\Delta_z - 1.6449 \cdot \text{SE}_z = 0.2027 - 0.1489 = 0.0538$.  
   Any sample correlation $|\hat{\rho}| > 0.053$ will cause the $90\%$ CI to straddle $\pm 0.20$, resulting in an **INCONCLUSIVE** outcome.
2. **Explicit Preregistration Rule for Inconclusive Zone**:  
   If $N = 135$ and $\Delta = 0.20$ are retained, an intermediate boundary-straddling result is **formally classified as INCONCLUSIVE due to sample size precision limits**, NOT as empirical evidence of coupling.
3. **Three Rational Execution Pathways Submitted to Ciah**:
   - **Path A (Current Baseline $N=135, \Delta=0.20$)**: Maintain $N=135$ probes and strict $\Delta=0.20$. Accept $44.8\%$ statistical power, treating any CI overlap as `INCONCLUSIVE`.
   - **Path B (Calibrated Margin $N=135, \Delta=0.28-0.30$)**: Maintain $N=135$ probes, but calibrate the equivalence margin to $\Delta = 0.29$ ($R^2 < 0.084$), achieving **$90.4\%$ power**.
   - **Path C (Scaled Sample Size $N=270, \Delta=0.20$)**: Double the probe suite to $n = 30$ probes/cell ($N = 270$ total), achieving **$89.2\%$ power** under strict $\Delta = 0.20$.

---

## 14. Decision Criteria Matrix

| Evaluation Criterion | Preregistered Requirement | Decoupling Supported | Intermediate / Inconclusive | Coupling Supported |
|---|---|---|---|---|
| **1. Measurement Validity** | Genuine production pipeline; zero synthetic PAD injection; $T$ balanced $5/5/5$ in all cells. | Mandatory Pass | Unverified / synthetic bypass $\implies$ **INCONCLUSIVE** | — |
| **2. Surprise Manipulation Check** | Monotonic separation; $p < 0.001$; $\Delta \ge 0.10$ & $\ge 0.15$. | Mandatory Pass | Failed separation $\implies$ **INCONCLUSIVE** | — |
| **3. Uncertainty Manipulation Check**| Monotonic separation; $p < 0.001$; $\Delta \ge 0.25$ & $\ge 0.25$. | Mandatory Pass | Failed separation $\implies$ **INCONCLUSIVE** | — |
| **4. Within-Cell Variance Floors** | Probe-level $\text{Var}_{\text{probe}}(\bar{S} \mid \text{cell}) \ge 0.0005$, $\text{Var}_{\text{probe}}(\bar{U} \mid \text{cell}) \ge 0.0020$ (all 9 cells). | Mandatory Pass | Any cell below floor $\implies$ **INCONCLUSIVE** | — |
| **5. Spillover $U \to S \mid S_{\text{target}}, T$ ($\eta_p^2$)** | GLM effect size controlling for stimulus affect and $T$. | $\eta_p^2 < 0.02$ | $0.02 \le \eta_p^2 < 0.06 \implies$ **INCONCLUSIVE** | $\eta_p^2 \ge 0.06$ (with $p < 0.01$) |
| **6. Spillover $S \to U \mid U_{\text{target}}, T$ ($\eta_p^2$)** | GLM effect size controlling for target uncertainty and $T$. | $\eta_p^2 < 0.02$ | $0.02 \le \eta_p^2 < 0.06 \implies$ **INCONCLUSIVE** | $\eta_p^2 \ge 0.06$ (with $p < 0.01$) |
| **7. Partial Equivalence (TOST)** | 90% CI of residual $\hat{\rho}_{\text{partial}}$ vs margin $\pm \Delta$ ($\text{rank}=11$). | CI $\subset (-\Delta, +\Delta)$ | CI straddles $-\Delta$ or $+\Delta \implies$ **INCONCLUSIVE** | CI strictly outside $(-\Delta, +\Delta)$ |
| **8. Multiplicity Correction** | Holm-Bonferroni control across all confirmatory tests. | Mandatory Pass | Unadjusted reporting $\implies$ **INVALID** | — |

---

## 15. Anti-Post-Hoc Rules

1. **Pre-Frozen Estimands**: All factor levels, exposure assignments ($5/5/5$ per cell), variance floors, and equivalence margins are frozen upon ratification of this specification.
2. **Zero Post-Hoc Exclusions**: No probe or cell may be excluded post-hoc from the primary analysis for producing unfavorable outcomes.
3. **Preservation of Historical Evidence**: The historical Phase 22 result ($R^2 = 0.2766, p = 5.43 \times 10^{-7}$) remains in project archives as evidence of benchmark confounding. The post-hoc ablation ($R^2 = 0.1168$ without Stratum 5) remains strictly labeled as exploratory sensitivity analysis.

---

## 16. Interpretation Boundaries & "What This Amendment Does NOT Establish"

To maintain philosophical and pre-reflective discipline:
- It does **NOT** establish conscious self-awareness, sentience, or subjective feeling.
- It does **NOT** claim general intelligence or biological equivalence.
- It does **NOT** prove the mathematical optimality of Expected Free Energy in conversational AI.
- It does **NOT** validate conversational performance with real human users.
- It does **NOT** constitute production readiness or open the Architecture Gate.

---

## 17. Implementation Preconditions & Reviewer Ratification Gate

The following items are submitted to Ciah (Research Reviewer) for final ratification:
1. **$S_{\text{target}}$ and Within-Cell $T$ Balancing Ratification**: Formally ratify defining $S_{\text{target}}$ as stimulus affective intensity and enforcing balanced $5/5/5$ allocations of $T \in \{1, 4, 12\}$ within every single cell.
2. **Design Matrix Rank Ratification**: Formally ratify $\text{rank}(\mathbf{X}) = 11, p = 10, N_{\text{eff}} = 122$ with $\text{SE}_z = 0.090535$.
3. **Execution Pathway Selection**: Choose among Path A ($N=135, \Delta=0.20, \text{Power}=44.8\%$), Path B ($N=135, \Delta=0.29, \text{Power}=90.4\%$), or Path C ($N=270, \Delta=0.20, \text{Power}=89.2\%$).

---

## 18. Preregistration Checklist (Proposal State)

- [ ] `[PROPOSED — PENDING APPROVAL]` $S_{\text{target}}$ defined strictly by stimulus text affect, completely decoupled from $T$.
- [ ] `[PROPOSED — PENDING APPROVAL]` $T \in \{1, 4, 12\}$ balanced with exactly $5/5/5$ probes in every single cell.
- [ ] `[AUDITED — FEASIBILITY VERIFIED]` Headless dynamic measurement path confirmed via `EmotionCore.commit_stimulus()`.
- [ ] `[PROPOSED — PENDING APPROVAL]` Confirmatory manipulation checks preregistered with dynamically calibrated separation floors ($\ge 0.10, \ge 0.15$).
- [ ] `[PROPOSED — PENDING APPROVAL]` Within-cell variance floors locked strictly to probe-level means after seed aggregation ($\text{Var}_{\text{probe}}(\bar{S}) \ge 0.0005, \text{Var}_{\text{probe}}(\bar{U}) \ge 0.0020$).
- [ ] `[LOCKED — DERIVATION VERIFIED]` Exact design matrix $\mathbf{X}$ ($\text{rank} = 11, p = 10, \text{SE}_z = 0.090535$) locked for Track B.
- [ ] `[SYNCHRONIZED — TABLE VERIFIED]` Exact power calculations synchronized across candidate sample sizes and margins.
- [ ] `[PROPOSED — PENDING CIAH SELECTION]` Execution pathway (Path A, B, or C) submitted for reviewer sign-off.
- [ ] `[PROPOSED — PENDING APPROVAL]` Multiplicity control (Holm-Bonferroni) preregistered.
- [ ] `[PROPOSED — PENDING APPROVAL]` Anti-post-hoc rules and historical result preservation explicitly declared.
- [ ] `[PROPOSED — PENDING APPROVAL]` Inconclusive outcome criteria defined without forcing binary pass/fail.
- [ ] `[PROPOSED — PENDING APPROVAL]` Implementation boundary and governance gates strictly preserved.

---

## 19. Revision History

- **v1.0 (September 16, 2026)**: Initial deconfounding specification proposing 3 × 3 crossed factorial design, variance injection, TOST equivalence testing ($\Delta = 0.20$), and probe-level analysis.
- **v1.1 (September 16, 2026)**: Refined measurement semantics based on pre-execution measurement audit findings. Formalized Cumulative Turn-Exposure Surprise ($S_{\text{exposure}}$), introduced multi-tick exposure duration $T$, corrected inter-probe independence language, and re-calibrated surprise manipulation check floors.
- **v1.2 (September 16, 2026)**: Resolved reviewer audit findings on $T$–$S$ confounding. Reframed $T$ as an experimental implementation variable and $S_{\text{observed}}$ as the actual continuous physiological variable; clarified the deterministic/derived status of $U_{\text{sem\_observed}}$ from authored proposition graphs; removed pre-empirical sample correlation claims; locked within-cell variance floors to probe-level means after seed aggregation; and formulated equivalence testing on partial correlation conditioning on $T$.
- **v1.3 (September 16, 2026 - Current)**: Methodological cleanup resolving reviewer audit on v1.2. Defined $S_{\text{target}}$ as stimulus affective intensity and balanced $T \in \{1, 4, 12\}$ symmetrically ($5/5/5$) inside every single cell; mathematically locked design matrix $\mathbf{X}$ ($\text{rank} = 11, p = 10, N_{\text{eff}} = 122$); synchronized exact statistical power curves ($\text{Power} = 44.8\%$ at $N=135, \Delta=0.20$; $92.4\%$ at $\Delta=0.30$); and framed execution pathways (Path A, B, C) for reviewer ratification.
