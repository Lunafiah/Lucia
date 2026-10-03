# Phase 22 — H1 Protocol Amendment v1.2
## Multi-Tick Measurement Semantics & Experimental Validity Refinement

> **Project:** Lucia — Embodied Whole-Brain Architecture  
> **Phase:** Phase 22 — Active Inference & Prospective Epistemic Foraging  
> **Subsystem:** Layer 4 (Active Inference) & Layer 2 (EmotionCore Coupled MT-LNN)  
> **Document Role:** Formal Specification & Preregistration Proposal (Design Only)  
> **Author:** Antigravity (Execution / Research Implementation Agent)  
> **Reviewer:** Ciah (Research Reviewer)  
> **Governance Status:** **[CURRENT RESEARCH / SPECIFICATION ONLY — ARCHITECTURE GATE LOCKED]**  
> **Date:** September 2026  
> **Governing Documents:** [`AGENTS.md`](file:///c:/Users/Lunafiah/Desktop/My_project/Lucia/AGENTS.md), [`docs/00_PROJECT_OVERVIEW.md`](file:///c:/Users/Lunafiah/Desktop/My_project/Lucia/docs/00_PROJECT_OVERVIEW.md), [`docs/ARCHITECTURE.md`](file:///c:/Users/Lunafiah/Desktop/My_project/Lucia/docs/ARCHITECTURE.md)  
> **Supersedes:** [`PHASE_22_H1_PROTOCOL_AMENDMENT_v1.1.md`](file:///c:/Users/Lunafiah/Desktop/My_project/Lucia/docs/specs/Lucia-phase22-Epistemic_Foraging/PHASE_22_H1_PROTOCOL_AMENDMENT_v1.1.md) and [`PHASE_22_H1_PROTOCOL_AMENDMENT_v1.0.md`](file:///c:/Users/Lunafiah/Desktop/My_project/Lucia/docs/specs/Lucia-phase22-Epistemic_Foraging/PHASE_22_H1_PROTOCOL_AMENDMENT_v1.0.md)  
> **Reason for Amendment (v1.2):** Reviewer audit (Ciah) of v1.1 identified that equating target surprise tiers with exposure durations ($S_L \to T=1, S_M \to T=4, S_H \to T=12$) created an experimental confound between exposure duration $T$ and physiological surprise $S$. v1.2 formally reframes $T$ as an experimental implementation variable, establishes $S_{\text{observed}}$ as the continuous physiological variable, clarifies the deterministic/derived status of $U_{\text{sem\_observed}}$ from authored proposition graphs, removes pre-empirical sample correlation claims, and locks within-cell variance floors to probe-level means after seed aggregation.

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
Amended Protocol v1.2 (This Document)
             ≠
Future Experimental Execution (Pending Approval)
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
| **Exposure Duration ($T$)** | **Experimental Implementation Variable** | Number of discrete integration ticks ($dt = 0.10\text{s}$) through `EmotionCore.commit_stimulus()`. | $T \in \{1, 4, 12\}$ ticks ($0.10\text{s} - 1.20\text{s}$). | Engineering vehicle to allow continuous ODE trajectory expression across turn durations; controlled covariate in statistical analysis. |
| **Observed Physiological Surprise ($S_{\text{observed}}$)** | **Actual Continuous Physiological Variable** | Euclidean norm between prior predicted PAD state $\hat{\mathbf{p}}_0 = \mathbf{A}\mathbf{p}_0 + \mathbf{b}$ captured at Stage 2 and committed post-stimulus limbic PAD state $\mathbf{p}_T$ after $T$ integration ticks at Stage 4: $$S_{\text{observed}} = S_{\text{exposure}} = \|\hat{\mathbf{p}}_0 - \mathbf{p}_T\|_2$$ | $[0.0, \sqrt{12}] \approx [0.0, 3.46]$; operational envelope $[0.01, 0.85]$. | Primary dependent variable of interest representing retrospective limbic prediction error. |
| **Instantaneous Single-Tick Surprise ($S_t$)** | **Canonical Single-Transition Entity** | Euclidean prediction error across exactly one tick ($T=1$): $$S_t = \|\hat{\mathbf{p}}_{t-1} - \mathbf{p}_t\|_2$$ | Physical single-step bound from Philia: $[0.00, 0.122]$. | Canonical subsystem entity; $S_{\text{observed}} \equiv S_t$ when $T=1$. |
| **Semantic Uncertainty Target ($U_{\text{target}}$)** | **Experimental Construction / Factor** | Target uncertainty tier parameterizing the authored proposition graph: Low, Medium, High. | Discrete factor levels $\{U_L, U_M, U_H\}$. | Manipulated experimental factor parameterizing probe fixtures. |
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
│   • Semantic Uncertainty Target: U_target ∈ {L, M, H}  │
│   • Lexical Affective Profile (Valence, Arousal, Domin)│
└──────────────────────────┬─────────────────────────────┘
                           │
                           │ Parameterizes
                           ▼
┌────────────────────────────────────────────────────────┐
│             MANIPULATED STIMULUS PROBE                 │
│   • Authored text surface with varied lexical arousal  │
│   • Pre-turn PAD state p_0 (Resting Philia baseline)   │
│   • Authored candidate propositions with confidences c │
└──────────────────────────┬─────────────────────────────┘
                           │
                           │ Ingested by pipeline under
                           ▼
┌────────────────────────────────────────────────────────┐
│             IMPLEMENTATION VARIABLE CONTROL            │
│   • Exposure duration T ∈ {1, 4, 12} ticks             │
│   • Assigned independently of U_target                 │
│   • Explicitly modeled as covariate in analysis        │
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
│   • Spillover ANOVA: S_obs ~ U_target + T + (U × T)    │
│   • Equivalence Testing: Partial Corr(S_obs, U_obs | T)│
│   • Effect sizes & TOST bounds serve as primary proof  │
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

# 4. Integrate stimulus over implementation exposure duration T (Stage 3)
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

## 7. Experimental Design & Deconfounding Architecture

### 7.1 Deconfounding Exposure Duration ($T$) from Surprise ($S$)
In v1.1, nominal surprise factor levels were deterministically tied to single exposure durations ($S_L \to T=1, S_M \to T=4, S_H \to T=12$). This conflated exposure duration with physiological surprise.  
In reality, physiological displacement in Lucia is governed by:
$$\Delta\mathbf{p} = f\left(\text{Lexical Affective Profile}, T, \mathbf{p}_0\right)$$
Empirical audit data proves that $T$ alone does not dictate surprise:
- Neutral text with $T=12$ yields $S = 0.024$ (Low Surprise).
- Calming text with $T=4$ yields $S = 0.150$ (Low/Med Surprise).
- High-arousal urgent text with $T=4$ yields $S = 0.347$ (Med/High Surprise).
- High-arousal urgent text with $T=12$ yields $S = 0.710$ (High Surprise).

Therefore, in v1.2:
1. **$T$ is an Experimental Implementation Variable**: Exposure duration is varied across probes ($T \in \{1, 4, 12\}$) as an instrument to allow the dynamical limbic system to reach different trajectory points.
2. **$S_{\text{observed}}$ is the Physiological Dependent Variable**: The primary hypothesis operates directly on the continuous physiological prediction error $S_{\text{observed}}$.
3. **Controlled Covariate Analysis**: In all statistical models, $T$ is explicitly accounted for as a design covariate. Equivalence testing (TOST) evaluates the partial correlation $\hat{\rho}(S_{\text{observed}}, U_{\text{sem\_observed}} \mid T)$, guaranteeing that any evaluated relationship between surprise and uncertainty is independent of exposure duration.

### 7.2 Balanced Probe Allocation Grid (3 × 3)
Stimuli are arranged in a balanced grid crossing target Semantic Uncertainty ($U_{\text{target}} \in \{L, M, H\}$) with target Physiological Displacement bands populated by combinations of lexical intensity and implementation durations ($T \in \{1, 4, 12\}$):

```text
                                Semantic Uncertainty Target (U_target)
                                 Low (0.10–0.25)    Med (0.45–0.60)    High (0.80–0.95)
                               ┌──────────────────┬──────────────────┬──────────────────┐
  Mild Displacement Target     │      Cell 1      │      Cell 2      │      Cell 3      │
  (Calm text / low T)          │    (S_L, U_L)    │    (S_L, U_M)    │    (S_L, U_H)    │
Physiological                  ├──────────────────┼──────────────────┼──────────────────┤
Displacement Target            │      Cell 4      │      Cell 5      │      Cell 6      │
  Moderate Displacement Target │    (S_M, U_L)    │    (S_M, U_M)    │    (S_M, U_H)    │
  (Varied text / mid T)        ├──────────────────┼──────────────────┼──────────────────┤
                               │      Cell 7      │      Cell 8      │      Cell 9      │
  Strong Displacement Target   │    (S_H, U_L)    │    (S_H, U_M)    │    (S_H, U_H)    │
  (Urgent text / high T)       │ [Old Stratum 5]  │    (S_H, U_M)    │    (S_H, U_H)    │
                               └──────────────────┴──────────────────┴──────────────────┘
```

### 7.3 Sample Allocation & Statistical Unit
- **Sample Allocation**: Exactly $n = 15$ unique probes per cell ($N = 135$ total probes across 9 cells).
- **Repeated Environmental Seeds**: 5 canonical fixed seeds ($42, 43, 44, 45, 46$).
- **Total Evaluations**: $135 \times 5 = 675$ evaluations per condition ($2,025$ evaluations across 3 conditions).
- **Unit of Statistical Analysis**: The **Probe** ($N = 135$). For each probe, observations are averaged across the 5 seeds to form a single probe-level mean $(\bar{S}_i, \bar{U}_i)$ prior to primary statistical modeling.

---

## 8. Exposure Assignment & Orthogonality to Semantic Uncertainty

### 8.1 Design Independence by Construction
To ensure exposure duration does not confound semantic uncertainty:
1. **Identical Marginal Allocation**:
   > **Design Balance Statement:**  
   > Exposure duration $T$ is assigned independently of $U_{\text{target}}$, with identical marginal exposure-duration allocation across all semantic uncertainty levels.
   - For every level of $U_{\text{target}}$ (Low, Med, High), the distribution of $T$ across its 45 probes is identical: exactly 15 probes with $T = 1$, 15 probes with $T = 4$, and 15 probes with $T = 12$.
   - This structural orthogonality is guaranteed by experimental construction, preventing any information leakage between exposure duration and semantic uncertainty.
2. **Domain Balancing**: Semantic domains (system telemetry, project status, relational milestones, factual knowledge) are evenly distributed across all 9 cells.
3. **Randomized Presentation Order**: Probe presentation order is fully randomized across cells for every seed run, eliminating sequence, warm-up, or drift confounds.

---

## 9. Manipulation Checks & Quality Gates

Before testing the primary decoupling hypothesis, the dataset must satisfy two independent, confirmatory manipulation checks:

### 9.1 Surprise Manipulation Check
- **Objective**: Verify that stimuli and implementation exposure parameters reliably manipulate $S_{\text{observed}}$ through the production pipeline.
- **Criteria**:
  1. Execution of genuine production pipeline verified (zero synthetic PAD injection).
  2. Main effect of stimulus displacement target on $S_{\text{observed}}$ is statistically significant: $p < 0.001$.
  3. Monotonic separation across target tiers: $\bar{S}_{\text{observed}}(\text{Low}) < \bar{S}_{\text{observed}}(\text{Med}) < \bar{S}_{\text{observed}}(\text{High})$.
  4. Minimum separation thresholds (calibrated to multi-tick dynamical envelope):
     $$\bar{S}_{\text{observed}}(\text{Med}) - \bar{S}_{\text{observed}}(\text{Low}) \ge 0.10$$
     $$\bar{S}_{\text{observed}}(\text{High}) - \bar{S}_{\text{observed}}(\text{Med}) \ge 0.25$$
- **Failure Consequence**: If unmet, the surprise manipulation is invalid; experiment aborts to **INCONCLUSIVE**.

### 9.2 Semantic Uncertainty Manipulation Check
- **Objective**: Verify that authored proposition graphs for $U_{\text{target}}$ produce properly separated derived entropy values $U_{\text{sem\_observed}}$.
- **Criteria**:
  1. Main effect of $U_{\text{target}}$ on $U_{\text{sem\_observed}}$ is statistically significant: $p < 0.001$.
  2. Monotonic separation: $\bar{U}_{\text{sem\_observed}}(\text{Low}) < \bar{U}_{\text{sem\_observed}}(\text{Med}) < \bar{U}_{\text{sem\_observed}}(\text{High})$.
  3. Minimum separation thresholds:
     $$\bar{U}_{\text{sem\_observed}}(\text{Med}) - \bar{U}_{\text{sem\_observed}}(\text{Low}) \ge 0.25$$
     $$\bar{U}_{\text{sem\_observed}}(\text{High}) - \bar{U}_{\text{sem\_observed}}(\text{Med}) \ge 0.25$$
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
Two separate general linear models test for directional cross-factor spillover, explicitly incorporating the implementation variable $T$:

$$\text{Model A}_1: \quad S_{\text{observed}} = \mu_S + \beta_U U_{\text{target}} + \beta_T T + \beta_{UT} (U_{\text{target}} \times T) + \epsilon_S$$

$$\text{Model A}_2: \quad U_{\text{sem\_observed}} = \mu_U + \gamma_S S_{\text{target}} + \gamma_T T + \gamma_{ST} (S_{\text{target}} \times T) + \epsilon_U$$

- **Primary Inferential Metric**: Partial eta-squared ($\eta_p^2$).
  - **Decoupling Supported (Negligible Spillover)**:
    $$\eta_p^2(U \to S \mid T) < 0.02 \quad \text{and} \quad \eta_p^2(S \to U \mid T) < 0.02$$
  - **Coupling Supported (Substantial Spillover)**:
    $$\eta_p^2(U \to S \mid T) \ge 0.06 \quad \text{or} \quad \eta_p^2(S \to U \mid T) \ge 0.06$$
  - **Intermediate / Inconclusive Zone**:
    $$0.02 \le \eta_p^2 < 0.06 \implies \text{INTERMEDIATE EFFECT / INCONCLUSIVE}$$
- **Supporting Diagnostic**: Omnibus $F$-test $p$-value ($p > 0.05$ reported as secondary consistency check; does not alone prove absence of coupling).

### Track B — Equivalence Testing on Partial Association (TOST)
To evaluate the absence of meaningful operational association between continuous physiological surprise and semantic uncertainty:
- **Operational Equivalence Margin ($\Delta$)**:
  We propose $\Delta = 0.20$ as the **operational architectural margin proposed for this experiment**, corresponding to $< 4.0\%$ residual shared variance ($R^2 < 0.04$).  
  *(Must be formally approved by Ciah / Project Owner before execution freezing).*
- **Calculation Pipeline**:
  1. *Seed Aggregation*: For each probe $i \in \{1, \dots, 135\}$, calculate probe-level means across the 5 canonical seeds:
     $$\bar{S}_i = \frac{1}{5} \sum_{s=1}^5 S_{i,s}, \quad \bar{U}_i = \frac{1}{5} \sum_{s=1}^5 U_{i,s}$$
  2. *Conditioning Model*: Regress $\bar{S}_i$ and $\bar{U}_i$ on the implementation variable $T$ and experimental design contrasts ($k = 9$ predictor degrees of freedom):
     $$\bar{S}_i = \mathbf{X}_i \boldsymbol{\beta} + e_{S,i}, \quad \bar{U}_i = \mathbf{X}_i \boldsymbol{\gamma} + e_{U,i}$$
  3. *Partial Correlation Coefficient*:
     $$\hat{\rho}_{\text{partial}} = \text{Corr}\left(e_{S,i}, e_{U,i}\right)$$
  4. *Confidence Interval via Fisher's $z$ Transformation*:
     $$z = \frac{1}{2} \ln \left(\frac{1 + \hat{\rho}_{\text{partial}}}{1 - \hat{\rho}_{\text{partial}}}\right), \quad \text{SE}_z = \frac{1}{\sqrt{N - k - 3}} = \frac{1}{\sqrt{135 - 12}} = \frac{1}{\sqrt{123}} \approx 0.0902$$
     The $90\%$ confidence interval (corresponding to two one-sided tests at $\alpha = 0.05$) is $[z \pm 1.6449 \cdot \text{SE}_z]$, transformed back to correlation scale via $\tanh(z)$.
  5. *Decoupling Decision Rule*:
     - **Equivalence Confirmed (Decoupling)**: $90\%$ CI strictly bounded within $(-\Delta, +\Delta)$.
     - **Coupling Confirmed**: $90\%$ CI strictly outside $(-\Delta, +\Delta)$.
     - **Indeterminate / Inconclusive**: $90\%$ CI straddles either boundary $-\Delta$ or $+\Delta$.

---

## 13. Power and Sample Size Rationale

> [!WARNING]
> **POWER CALCULATION STATUS: PROVISIONAL / SUPERSEDED BY MEASUREMENT-SEMANTICS REVISION**  
> Because the dependent variable definition has been refined to continuous turn-exposure surprise ($S_{\text{observed}}$) and exposure duration $T$ is included as a conditioning covariate, historical power calculations from v1.0 are designated provisional. Final statistical power must be recomputed from the frozen conditioning model and verified against the runtime environment before execution.

- **Sample Size Baseline**: $N = 135$ probes ($n = 15$ per cell across 9 cells).
- **Recomputation Prerequisite**: Prior to data collection, the final analytical script must execute an automated Monte Carlo power simulation under the frozen $\text{SE}_z = 1/\sqrt{123}$ model to verify that power to reject $|\rho_{\text{partial}}| \ge 0.20$ at $\alpha = 0.05$ exceeds $90\%$ when true $\rho = 0.00$.

---

## 14. Decision Criteria Matrix

| Evaluation Criterion | Preregistered Requirement | Decoupling Supported | Intermediate / Inconclusive | Coupling Supported |
|---|---|---|---|---|
| **1. Measurement Validity** | Production pipeline executed headlessly; zero synthetic PAD injection; $T$ assigned independently of $U$. | Mandatory Pass | Unverified / synthetic bypass $\implies$ **INCONCLUSIVE** | — |
| **2. Surprise Manipulation Check** | Monotonic separation; $p < 0.001$; $\Delta \ge 0.10$ & $\ge 0.25$. | Mandatory Pass | Failed separation $\implies$ **INCONCLUSIVE** | — |
| **3. Uncertainty Manipulation Check**| Monotonic separation; $p < 0.001$; $\Delta \ge 0.25$ & $\ge 0.25$. | Mandatory Pass | Failed separation $\implies$ **INCONCLUSIVE** | — |
| **4. Within-Cell Variance Floors** | Probe-level $\text{Var}_{\text{probe}}(\bar{S} \mid \text{cell}) \ge 0.0005$, $\text{Var}_{\text{probe}}(\bar{U} \mid \text{cell}) \ge 0.0020$ (all 9 cells). | Mandatory Pass | Any cell below floor $\implies$ **INCONCLUSIVE** | — |
| **5. Spillover $U \to S \mid T$ ($\eta_p^2$)** | GLM effect size controlling for exposure duration $T$. | $\eta_p^2 < 0.02$ | $0.02 \le \eta_p^2 < 0.06 \implies$ **INCONCLUSIVE** | $\eta_p^2 \ge 0.06$ (with $p < 0.01$) |
| **6. Spillover $S \to U \mid T$ ($\eta_p^2$)** | GLM effect size controlling for exposure duration $T$. | $\eta_p^2 < 0.02$ | $0.02 \le \eta_p^2 < 0.06 \implies$ **INCONCLUSIVE** | $\eta_p^2 \ge 0.06$ (with $p < 0.01$) |
| **7. Partial Equivalence (TOST)** | 90% CI of residual $\hat{\rho}_{\text{partial}} \mid T$ vs margin $\pm \Delta$. | CI $\subset (-\Delta, +\Delta)$ | CI straddles $-\Delta$ or $+\Delta \implies$ **INCONCLUSIVE** | CI strictly outside $(-\Delta, +\Delta)$ |
| **8. Multiplicity Correction** | Holm-Bonferroni control across all confirmatory tests. | Mandatory Pass | Unadjusted reporting $\implies$ **INVALID** | — |

---

## 15. Anti-Post-Hoc Rules

1. **Pre-Frozen Estimands**: All factor levels, exposure assignments ($T \in \{1, 4, 12\}$), variance floors, and equivalence margins are frozen upon approval of this specification.
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

## 17. Implementation Preconditions & Open Decisions

The following items are submitted to Ciah (Research Reviewer) for final ratification:
1. **Deconfounded Framing Approval**: Approve framing $T \in \{1, 4, 12\}$ as an implementation variable, $S_{\text{observed}}$ as the continuous physiological variable, and $U_{\text{sem\_observed}}$ as the derived propositional metric.
2. **Operational Equivalence Margin Approval**: Formally ratify $\Delta = 0.20$ ($< 4.0\%$ residual shared variance) for partial correlation $\hat{\rho}(S_{\text{observed}}, U_{\text{sem\_observed}} \mid T)$.
3. **Sample Size & Allocation Approval**: Ratify $N = 135$ probes ($15$ per cell across 9 cells) and probe-level variance evaluation.

---

## 18. Preregistration Checklist (Proposal State)

- [ ] `[PROPOSED — PENDING APPROVAL]` Primary research question defined unambiguously on continuous $S_{\text{observed}}$ and derived $U_{\text{sem\_observed}}$.
- [ ] `[PROPOSED — PENDING APPROVAL]` $T \in \{1, 4, 12\}$ framed as an experimental implementation variable and assigned independently of $U_{\text{target}}$.
- [ ] `[AUDITED — FEASIBILITY VERIFIED]` Headless dynamic measurement path confirmed via `EmotionCore.commit_stimulus()`.
- [ ] `[PROPOSED — PENDING APPROVAL]` Confirmatory manipulation checks preregistered with dynamically calibrated separation floors ($\ge 0.10, \ge 0.25$).
- [ ] `[PROPOSED — PENDING APPROVAL]` Within-cell variance floors locked strictly to probe-level means after seed aggregation ($\text{Var}_{\text{probe}}(\bar{S}) \ge 0.0005, \text{Var}_{\text{probe}}(\bar{U}) \ge 0.0020$).
- [ ] `[PROPOSED — PENDING APPROVAL]` Primary statistical models (GLM spillover controlling for $T$ & Partial Correlation TOST) formalized with intermediate zone $[0.02, 0.06)$.
- [ ] `[PROPOSED — PENDING CIAH APPROVAL]` Operational equivalence margin $\Delta = 0.20$ submitted for reviewer approval.
- [ ] `[PROVISIONAL — PENDING FINAL SIMULATION]` Power analysis labeled provisional pending recomputation on frozen conditioning model.
- [ ] `[PROPOSED — PENDING APPROVAL]` Multiplicity control (Holm-Bonferroni) preregistered.
- [ ] `[PROPOSED — PENDING APPROVAL]` Anti-post-hoc rules and historical result preservation explicitly declared.
- [ ] `[PROPOSED — PENDING APPROVAL]` Inconclusive outcome criteria defined without forcing binary pass/fail.
- [ ] `[PROPOSED — PENDING APPROVAL]` Implementation boundary and governance gates strictly preserved.

---

## 19. Revision History

- **v1.0 (September 16, 2026)**: Initial deconfounding specification proposing 3 × 3 crossed factorial design, variance injection, TOST equivalence testing ($\Delta = 0.20$), and probe-level analysis.
- **v1.1 (September 16, 2026)**: Refined measurement semantics based on pre-execution measurement audit findings. Formalized Cumulative Turn-Exposure Surprise ($S_{\text{exposure}}$), introduced multi-tick exposure duration $T$, corrected inter-probe independence language, and re-calibrated surprise manipulation check floors.
- **v1.2 (September 16, 2026 - Current)**: Resolved reviewer audit findings on $T$–$S$ confounding. Reframed $T$ as an experimental implementation variable and $S_{\text{observed}}$ as the actual continuous physiological variable; clarified the deterministic/derived status of $U_{\text{sem\_observed}}$ from authored proposition graphs; removed pre-empirical sample correlation claims in favor of design independence by construction; locked within-cell variance floors to probe-level means after seed aggregation; and formulated equivalence testing on partial correlation conditioning on $T$.
