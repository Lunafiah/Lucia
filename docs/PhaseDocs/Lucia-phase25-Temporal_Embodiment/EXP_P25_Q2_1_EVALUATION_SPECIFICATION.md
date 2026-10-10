# EXP-P25-Q2.1: Reciprocal Embodied Synchrony & Social Feedback Dynamics — Formal Evaluation Specification

> **DOCUMENT TYPE:** RESEARCH-ONLY EVALUATION SPECIFICATION<br>
> **STATUS:** HISTORICAL EVALUATION SPECIFICATION / HARNESS EXECUTED (C2 BLOCKED UNDER TBD-Q2-04, H-B UNPROVEN) / SEC 10 SUPERSEDED BY DOC-P25-006 & DOC-P25-007<br>
> **PREREQUISITE RATIFIED SPECIFICATION:** [`P25_Q2_SCIENTIFIC_CALIBRATION.md`](file:///c:/Users/Lunafiah/Desktop/My_project/Lucia/docs/PhaseDocs/Lucia-phase25-Temporal_Embodiment/P25_Q2_SCIENTIFIC_CALIBRATION.md)<br>
> **PHASE 25 HORIZON STATUS:** PLANNED (ACTIVE FUTURE RESEARCH HORIZON)<br>
> **GATE PROGRESSION:** `P25-Q1 CLOSED` → `P25-Q2 CLOSED (H-A supported, C2 blocked, H-B unproven)` → `Architecture Candidate / Evidence Synthesis` → `Ciah Review` → `Owner Decision` → `Implementation Gate`<br>
> **ARCHITECTURE GATE:** LOCKED (NO PRODUCTION MUTATION AUTHORIZED)<br>
> **IMPLEMENTATION GATE:** LOCKED  
> **GENESIS INVARIANT (INV-8):** PRESERVED BIT-EXACT (`data/profile.json == {"is_onboarded": false}`)  
> **CANONICAL INVARIANTS:** INV-1 (ONE CONTINUOUS LIFE), INV-2 (NO REFLECTIVE EGO) STRICTLY PRESERVED  

---

## 1. Purpose & Research Questions

### 1.1 Purpose
This document establishes the formal, research-only evaluation protocol for **EXP-P25-Q2.1**. It operationalizes the empirical testing of bidirectional temporal adaptation in conversational embodiment against matched unilateral baselines, testing whether reciprocal social feedback produces genuine incremental attunement and whether any observed consequences persist beyond the immediate interaction.

### 1.2 Primary Research Question
> *Under matched controller capabilities and output constraints, does genuine bidirectional temporal adaptation between User and Lucia produce measurable incremental benefit over unilateral adaptation?*

### 1.3 Secondary Research Question
> *If an incremental effect is observed, does it produce consequences that persist beyond the immediate episode into subsequent interaction episodes / future sessions?*

### 1.4 Conceptual Distinctions (Mandatory Separation)
The evaluation protocol strictly distinguishes between four separate phenomena:
1. **Immediate Synchrony:** Concurrent or short-lag statistical alignment of behavioral features (e.g., turn-gap minimization, phase alignment) within an active interaction window.
2. **Reciprocal Adaptation:** The specific causal feedback loop wherein each agent dynamically modifies its temporal trajectory in response to the other's preceding adaptations.
3. **Persistence:** The empirical retention of state adjustments or behavioral biases across conversational turns, episodic boundaries, or subsequent sessions.
4. **Relational Change:** Macro-level evolution of interpersonal stance ($\mathbf{R}_t$).

> **EPISTEMIC GUARDRAIL & SCIENTIFIC BOUNDARIES:**<br>
> - **Unilateral Baseline vs Reciprocal Hypothesis:** The supported baseline is unilateral adaptation (`observed user signal → Lucia state estimation → Lucia adaptation`). Bidirectional/reciprocal coupling (`Lucia expression → user response → reciprocal relational adaptation`) is an **unproven research hypothesis**. C2 remains **BLOCKED** and H-B remains **UNPROVEN**.
> - **Synchrony ≠ Causality:** P25-Q2 established that statistical synchrony or correlation does not imply causality or reciprocal attunement.
> - **Candidate Operational Definition:** Formulations of temporal embodiment are strictly **candidate operational definitions**; no formal validation is claimed until supported by P25 evaluation evidence.
> - **P24 Feedforward Boundary:** Phase 24 validated the feedforward affective expression path; this does **NOT** validate the P25 reciprocal social-feedback loop.
> - **P25/P26 Boundary:** Phase 25 addresses how interaction flows and produces temporal/social adaptation; Phase 26 governs what Lucia values, prefers, or autonomously pursues. P25 mechanisms must not introduce autonomous preference formation.

---

## 2. Hypotheses Formalization

The study evaluates four formal, non-architectural hypotheses:

* **Hypothesis H-A (Reactive Sufficiency):**  
  Under controlled conversational conditions, unilateral adaptive temporal coordination (Lucia adapting strictly to user observations without feedback of user response) is sufficient to explain all measurable short-term coordination benefits and perturbation recoveries.
* **Hypothesis H-B (Reciprocal Incrementality):**  
  Under matched controller capabilities and identical physical actuator constraints, bidirectional adaptation (closing the loop so user responses to Lucia's actions modulate Lucia's subsequent updates) yields a statistically significant and substantial incremental coordination benefit beyond unilateral adaptation.
* **Hypothesis H-C (Persistence):**  
  Bidirectional synchrony events produce measurable behavioral or state consequences that survive beyond the immediate interaction episode into subsequent interaction episodes / future sessions.
* **Hypothesis H-D (Substrate Sufficiency):**  
  If persistence is observed under H-C, it can be fully represented and mediated by Lucia's existing memory (Kanerva SDM), semantic substrate (`KnowledgeStore`), and relational state ($\mathbf{R}_t$). A new dedicated persistent relational representation becomes a viable research question only if the existing substrate fails to account for the empirical retention.

> **NON-COMMITMENT CLAUSE:**  
> No hypothesis outcome authorizes an architectural decision or production codebase modification. Hypotheses remain purely experimental constructs.

---

## 3. Experimental Conditions

The protocol specifies exactly three experimental conditions with strictly matched parameterization:

```
Condition C0 (Static Pacing Baseline):
  User Behavior U(t) ──> [Fixed Pacing Policy] ──> Output Actuation A_L(0)
                        (No dynamic state updates)

Condition C1 (Unilateral Adaptation):
  User Behavior U(t) ──> [Observation O_U(t)] ──> Leaky Controller ──> A_L(t)
                                                         │
                                                         ▼
                                               Output Actuation only
                                          (User response NOT fed back)

Condition C2 (Bidirectional Adaptation):
  User Behavior U(t) ──> [Observation O_U(t)] ──> Leaky Controller ──> A_L(t)
          ▲                                              ▲
          │                                              │
   User Response R_U(t+Δ) <────── Expression B_L(t) <────┘
          │
          └──────────────── (Feedback Modulates Next Update) ────┘
```

### Condition C0 — Static Pacing Baseline
- **Controller:** Static baseline controller without dynamic adaptation.
- **Behavior:** Fixed normative conversational latency and static speech tempo.
- **Purpose:** Establish baseline variance, uncoordinated overlap rate, and raw recovery duration following external perturbation.

### Condition C1 — Unilateral Adaptation
- **Controller:** Dynamic leaky-integrator temporal controller.
- **Information Flow:** $\text{User} \to \text{Lucia}$.
- **Behavior:** Lucia continuously estimates user speech envelope and turn boundaries, adapting her response latency and tempo toward entrainment.
- **Isolation Constraint:** User reactions to Lucia's preceding expressive behavior do **not** enter the controller's state update. The user signal is treated as an exogenous driving source.

### Condition C2 — Bidirectional Adaptation
- **Controller:** Matched dynamic leaky-integrator temporal controller.
- **Information Flow:** $\text{Lucia}(t) \to \text{User}(t+\Delta) \to \text{Lucia}(t+2\Delta)$.
- **Behavior:** Lucia adapts to incoming user signals, but the controller explicitly incorporates the user's measurable response increment to Lucia's preceding expressive output into its next state update.

### Strictly Matched Controller Parameters across C1 and C2
To guarantee that C2 is **not** specified as "C1 + an extra feature", the controllers must be strictly matched:
- **Controller Mathematical Class:** Discrete-time leaky integrator $\mathbf{s}_{t+1} = (1 - \lambda)\mathbf{s}_t + \lambda \mathbf{x}_t$.
- **Leakage Parameter:** $\lambda = 0.15$ (matched across C1 and C2).
- **Feature Representation:** Identical 3-feature observation space (Section 5).
- **Actuator Limits:** Identical clamping bounds (Section 5).
- **Latency Constraints:** Identical internal dispatch budgets ($< 2.0\text{ ms}$).
- **Interaction Fixture:** Identical conversational scripts and turn structures.
- **Perturbation Protocol:** Identical +300 ms injected delay timing.
- **Computational Budget:** Matched single-core CPU execution, zero GPU VRAM.
- **Manipulated Factor:** Exclusively the **directionality of the adaptive feedback loop**.

---

## 4. Operational Definition of Condition C2

To prevent C2 from degenerating into an abstract concept or an arbitrary residual-feature controller, the user's response to Lucia's preceding behavior is operationally defined through a causal temporal pipeline:

### 4.1 Measurable Temporal Signals
The interaction stream is discretized into turn-level and frame-level events:
- $t$: Timestamp of Lucia's expressive action onset (e.g., turn transition or pitch contour inflection).
- $B_L(t)$: Lucia's expressive output parameter vector (tempo adjustment $\Delta v_L \in [-0.15, +0.15]$, response latency $\tau_L \in [0, 1000]\text{ ms}$).
- $U(t + \Delta)$: The measured user behavioral feature at lag $\Delta$.

### 4.2 Causal Ordering & Lag Window
- **Lag Window ($\Delta$):** The response window is defined as a candidate operational range $\Delta \in [150, 800]\text{ ms}$ following Lucia's output. Any user event occurring $< 150\text{ ms}$ is treated as candidate overlapping execution, and events occurring $> 800\text{ ms}$ are treated as candidate uncoupled actions for the evaluation harness. These thresholds are exploratory candidate parameters, not biological constants or ungrounded falsification criteria.
- **Causal Sequence:**
  $$\text{Lucia Actuation } B_L(t) \xrightarrow{\Delta} \text{User Event } U(t+\Delta) \xrightarrow{\Delta} \text{Lucia Adaptation } \mathbf{s}_{t+2\Delta}$$

### 4.3 Baseline Construction & Operational Response Signal
The user's response signal $R_U(t + \Delta)$ is defined as the deviation from the user's running moving-average baseline:
$$U_{\text{baseline}}(t) = \frac{1}{K} \sum_{k=1}^K U(t - k \cdot T_{\text{turn}})$$
$$R_U(t + \Delta) = U(t + \Delta) - U_{\text{baseline}}(t)$$
- **Normalization:** $R_U$ is normalized by the running standard deviation $\sigma_U$ and clamped to $[-2.0, +2.0]$.

### 4.4 Closed-Loop State Update in C2
In C2, Lucia's controller state update is driven by the coupled feedback vector:
$$\mathbf{x}_t^{(\text{C2})} = \mathbf{w}_{\text{obs}} \odot U(t + \Delta) + \mathbf{w}_{\text{fb}} \odot \mathcal{F}\big(R_U(t + \Delta), B_L(t)\big)$$
where $\mathcal{F}(R_U, B_L)$ evaluates whether the user shifted their cadence in alignment with or in compensation against Lucia's preceding behavior $B_L(t)$.
- In C1, $\mathbf{w}_{\text{fb}} \equiv \mathbf{0}$, isolating the controller to unilateral tracking.

> [!IMPORTANT]
> **STRICT METHODOLOGICAL GUARDRAIL ON FEEDBACK GAIN ($\mathbf{w}_{\text{fb}}$):**
> To prevent C2 from inadvertently becoming an artificially tuned controller optimized specifically to outperform C1, the specification establishes four hard constraints:
> 1. **A Priori / Independent Determination:** The feedback gain vector $\mathbf{w}_{\text{fb}}$ (scaling constant for $\mathcal{F}$) must be established *a priori* or derived from an independent, decoupled calibration protocol prior to running test trials.
> 2. **Prohibition on Outcome-Driven Selection:** The gain must **NEVER** be chosen or adjusted based on the comparative performance or outcome of C1 vs C2.
> 3. **Prohibition on Post-Hoc Tuning:** The gain must **NEVER** be tuned post-hoc to maximize synchrony metrics, minimize turn-gap variance, or force C2 to exceed C1.
> 4. **Mandatory TBD Lock:** If an independent, empirically justified basis for $\mathbf{w}_{\text{fb}}$ is not established, the parameter remains strictly **TBD** and implementers are **strictly forbidden** from arbitrarily selecting or guessing a gain during harness implementation.

### 4.5 Safeguard Against Pseudo-Adaptation
To prevent unrelated spontaneous user drift from registering as reciprocal adaptation:
- If $|R_U(t + \Delta)|$ correlates significantly ($p < 0.05$) with an uncoupled control channel (e.g., unrelated background noise or unprompted pace change during user monologues), the feedback term is gated to zero for that turn.

---

## 5. Controlled Features & Physical Actuator Constraints

The experiment restricts sensory inputs and physical outputs strictly to calibrated variables:

### 5.1 Controlled Sensory Features (Input Space)
1. **eGeMAPS Pitch Mean ($F_0$):** Mean fundamental frequency of the user's turn segment, extracted via calibrated acoustic frontend ($[50, 400]\text{ Hz}$).
2. **Speech Envelope:** Short-time energy envelope tracking syllabic pacing and voice activity detection (VAD).
3. **Turn-Boundary Timing:** Duration of inter-turn silences (pause latency in ms) and inter-speech gaps.

> **NO SPECULATIVE MODALITIES:**  
> Computer vision, facial blendshape tracking, biometric heart-rate variability, and EEG/EDA are strictly **excluded** from this specification.

### 5.2 Actuator Limits & Clamping (Output Space)
Lucia's physical embodiment and voice pipeline must strictly respect the ratified boundary constraints:
- **Actuator Latency:** Clamped strictly within $[0, 1000]\text{ ms}$. Instantaneous responses ($< 100\text{ ms}$) violate conversational naturalness (Failure Mode S01).
- **Speech Tempo Adjustment:** Clamped strictly within $\pm 15\%$ of nominal speaking rate ($\text{tempo\_scale} \in [0.85, 1.15]$). Runaway acceleration or deceleration is prevented (Failure Mode S02).

---

## 6. Interaction Fixtures & Conversational Scripts

To eliminate lexical, syntactic, and topic confounds across conditions:

### 6.1 Fixture Structure
1. **Matched Dialogue Scripts:** Standardized 40-turn conversational scripts structured into three phases:
   - **Phase I (Turns 1–15): Baseline Entrainment.** Steady turn-taking dialogue under regular tempo.
   - **Phase II (Turns 16–25): Perturbation & Recovery.** Injection of calibrated temporal perturbation.
   - **Phase III (Turns 26–40): Post-Perturbation Coordination.** Assessment of residual attunement.
2. **Script Content Uniformity:** Scripts must contain semantically neutral, collaborative content (e.g., collaborative schedule planning, project milestone reviews).
3. **Execution Script Fixture Version:** `FIXTURE-P25-Q2-SCRIPT-v0.1` (*Specification Item: Full text of scripts is staged in `tests/evaluation/phase25/fixtures/` and must remain bit-exact across C0, C1, and C2*).

---

## 7. Perturbation Protocol

To evaluate dynamical stability and recovery elasticity, a standardized perturbation is injected:

### 7.1 Calibrated Perturbation Details
- **Perturbation Magnitude:** Exactly **$+300\text{ ms}$** artificial temporal latency injected into the turn-transition boundary.
- **Injection Schedule:** Injected deterministically at Turn 18 of the interaction script.
- **Perturbed Signal:** Lucia's dispatch response latency $\tau_{\text{dispatch}} \leftarrow \tau_{\text{dispatch}} + 300\text{ ms}$.
- **Duration:** Exactly one turn (transient delta impulse).
- **Recovery Window:** Analyzed across the subsequent 10 turns (Turns 19–28).
- **Exclusion Criteria:** If a hardware scheduler jitter exceeds $50\text{ ms}$ during Turn 18, the trial is invalidated and re-run with a fresh deterministic seed.
- **Prohibition on Speculative Thresholds:** No alternate perturbation magnitudes (e.g., $+100\text{ ms}$ or $+1000\text{ ms}$) are authorized for primary endpoint evaluation.

---

## 8. Primary Metrics & Semantic Rules

The evaluation records six core diagnostic metrics:

### 8.1 Metric Definitions
1. **Turn-Gap Variance ($\sigma^2_{\text{gap}}$):** Variance of silence duration between speaker transitions across turns (lower indicates tighter coordination).
2. **Overlap Ratio ($\rho_{\text{overlap}}$):** Percentage of total interaction time where both agents speak simultaneously (penalty metric; reflects failure of timing boundary).
3. **Perturbation Recovery Time ($T_{\text{recov}}$):** Number of turns required after Turn 18 for turn-gap duration to return to within $1.0\sigma$ of Phase I baseline.
4. **User-to-Lucia Transfer Entropy ($\text{TE}(U \to L)$):** Directed predictive information flow from user signals to Lucia's updates.
5. **Lucia-to-User Transfer Entropy ($\text{TE}(L \to U)$):** Directed predictive information flow from Lucia's behavior to subsequent user actions.
6. **Net Transfer Entropy Asymmetry ($\Delta\text{TE}_{\text{net}}$):**
   $$\Delta\text{TE}_{\text{net}} = \text{TE}(U \to L) - \text{TE}(L \to U)$$

### 8.2 Strict Semantic Rules on Metrics
> [!CAUTION]
> **CRITICAL METRIC CLASSIFICATION:**  
> - $\Delta\text{TE}_{\text{net}}$ is **ONLY** a **directional asymmetry diagnostic**.  
> - $\Delta\text{TE}_{\text{net}}$ is **NOT** a measure or evidence of "reciprocity".  
> - A net difference near zero can indicate either high bidirectional coupling or zero coupling.  
> - **NO ad-hoc reciprocity metric is invented.** A true bidirectional reciprocity index is deferred until formally justified by established dyadic coordination literature.

---

## 9. Transfer Entropy Estimation Protocol

To prevent estimation artifacts and spurious causality claims:

### 9.1 Estimator Family & Formulation
- **Estimator:** Kraskov-Stögbauer-Grassberger (KSG) continuous mutual information estimator or symbol-discretized plugin estimator ($k=4$ nearest neighbors).
- **Embedding Choice:** Embedding dimension $d=2$, delay $\tau=1$ turn.
- **Discretization:** Quantile binning into $B=4$ equiprobable bins if discrete estimator is deployed.
- **Bias Correction:** Miller-Madow or Grassberger analytical finite-sample bias correction.

### 9.2 Epistemic Interpretation Hierarchy
All information-theoretic results must be classified according to the 4-level evidence hierarchy:
- **Level 1 (Temporal Correlation):** Significant Pearson/Spearman correlation between time series ($r > 0$, $p < 0.05$). Does not establish direction.
- **Level 2 (Directed Information Transfer):** $\text{TE}(X \to Y) > 0$ and exceeds null noise floor. Establishes predictive asymmetry.
- **Level 3 (Reciprocal Adaptation):** Both $\text{TE}(U \to L) > 0$ and $\text{TE}(L \to U) > 0$ simultaneously exceed surrogate controls under closed-loop conditions.
- **Level 4 (Causal Reciprocal Coupling):** Perturbation in one agent induces a measurable, predictable trajectory deviation in the other that cascades back to the initiator.

---

## 10. Surrogate Control Protocol

> [!WARNING]
> **METHODOLOGY AUDIT NOTICE (2026-10-04):**  
> The surrogate methodology in this section has been **INVALIDATED** following post-execution audit.
> 1. Raw turn-gap variance is a univariate penalty metric (lower = tighter coordination); using an upper-tail $\theta_{95}$ reference as evidence for synchrony is mathematically inverted.
> 2. Recomputing univariate variance on cross-session dyads does not test bivariate coupling.
> 3. An arithmetic mean construction in the harness (`(u.pause + l_lat)/2`) introduced an artificial $2\times$ variance compression artifact.
> 
> This section is formally **SUPERSEDED** by [`P25_Q2_SURROGATE_METHODOLOGY_REVIEW.md`](file:///c:/Users/Lunafiah/Desktop/My_project/Lucia/docs/PhaseDocs/Lucia-phase25-Temporal_Embodiment/P25_Q2_SURROGATE_METHODOLOGY_REVIEW.md) and ratified in [`P25_Q2_METRIC_RATIFICATION.md`](file:///c:/Users/Lunafiah/Desktop/My_project/Lucia/docs/PhaseDocs/Lucia-phase25-Temporal_Embodiment/P25_Q2_METRIC_RATIFICATION.md). Any future rerun requires implementing the ratified coupling-sensitive null methodology.

To guard against spurious synchrony resulting from shared script structure or shared speaking rates (pseudo-synchrony):

### 10.1 Pseudo-Synchrony Surrogate Architecture (Historical / Superseded)
- **Surrogate Set Size:** Exactly **$N = 20$** cross-session shuffled dyads.
- **Shuffling Methodology:** Pair Lucia's temporal trajectory from Session $i$ with a user's temporal trajectory from Session $j$ ($i \ne j$), where both sessions executed the identical dialogue script.
- **Invariants Preserved:** Individual marginal distributions, auto-correlation structures, and speech rates are preserved exactly.
- **Recomputation:** Turn-gap variance, overlap ratio, and transfer entropies are recomputed on all 20 shuffled dyads.
- **95th Percentile Reference:** The empirical 95th percentile ($\theta_{95}$) of surrogate values defines the empirical 95th-percentile reference under the pseudo-synchrony surrogate null.

### 10.2 Interpretation of Surrogate Exceedance (Historical / Superseded)
Exceeding the 95th percentile of the surrogate distribution provides evidence against the independent-pacing surrogate null at the defined significance level. However:
> **GUARD:** Surrogate exceedance rejects independent cross-session pacing under this specific surrogate construction; it does **not** by itself prove "genuine attunement" or higher-level psychological or causal reciprocity.

---

## 11. Primary Endpoint & Statistical Decision Logic

The primary endpoint tests Hypothesis H-B (incremental benefit of C2 over C1):

### 11.1 Primary Composite Endpoint
The primary endpoint $\Delta_{\text{coord}}$ measures the relative coordination improvement:
$$\Delta_{\text{coord}} = \frac{\sigma^2_{\text{gap}}(\text{C1}) - \sigma^2_{\text{gap}}(\text{C2})}{\sigma^2_{\text{gap}}(\text{C1})}$$

### 11.2 Decision Logic Branches
1. **Branch A (No Incremental Benefit Observed):**
   $$\Delta_{\text{coord}} \le 0 \quad \text{or} \quad p \ge 0.05$$
   - **Conclusion:** **NO EVIDENCE SUPPORTING H-B UNDER TESTED CONDITIONS** (findings remain consistent with Reactive Sufficiency, H-A).
   - **Epistemic & Statistical Guardrail:** This outcome reflects an absence of empirical evidence for incremental benefit under the evaluated configuration. It must **NOT** be automatically classified as universal FALSIFIED or proof of zero effect across all possible dyadic regimes, as distinguishing "true absence of effect" from "insufficient experimental sensitivity/power" requires formal statistical power analysis and equivalence/non-inferiority margins.
2. **Branch B (Inconclusive / Spurious Benefit):**
   $$\Delta_{\text{coord}} > 0, \quad p < 0.05, \quad \text{but C2 metrics do NOT exceed Surrogate } \theta_{95}$$
   - **Conclusion:** **INCONCLUSIVE**. The observed difference is consistent with generic pacing adjustments rather than dyadic reciprocal coupling.
3. **Branch C (Supported Reciprocal Benefit):**
   $$\Delta_{\text{coord}} > 0, \quad p < 0.05, \quad \text{AND C2 metrics exceed Surrogate } \theta_{95}$$
   - **Conclusion:** H-B is **SUPPORTED** under the tested experimental configuration. Genuine bidirectional adaptation provides measurable incremental coordination beyond unilateral tracking.

---

## 12. Persistence Evaluation Across Temporal Tiers (P1, P2, P3)

The evaluation tracks whether observed attunement persists beyond immediate interaction:

### 12.1 Temporal Tiers
1. **Tier P1 (Immediate Synchrony):** Measured within Phase I and Phase II of the active session (Turns 1–25).
2. **Tier P2 (Short-Term Residual):** Measured in Phase III post-perturbation turns (Turns 26–40) within the same episode.
3. **Tier P3 (Relational Persistence Across Sessions):** Measured in **subsequent interaction episodes / future sessions** following a complete session teardown, somatic relaxation to Philia resting attractor ($P=+0.25, A=-0.05, D=+0.05$), and multi-turn idle interval.

> **TIME HORIZON INVARIANT:**  
> The protocol strictly forbids arbitrary calendar units ("days/weeks"). P3 evaluates persistence strictly across discrete episodic boundaries.

### 12.2 Substrate Sufficiency Test (Hypothesis H-D)
If P3 persistence is detected (e.g., faster re-entrainment in Session 2):
1. **Test 1:** Attempt to account for retention using existing `KnowledgeStore` propositions and SDM traces.
2. **Test 2:** Attempt to account for retention via canonical $\mathbf{R}_t$ updates in `RelationshipState`.
3. **Decision Rule:** If existing substrates account for the variance, H-D is **SUPPORTED**. No new persistent relational representation or memory kernel is warranted.

---

## 13. Evaluation Failure Modes

The protocol monitors five distinct failure modes to prevent degenerate coordination:

| Mode ID | Designation | Operational Failure Criteria | Governance Action |
|---|---|---|---|
| **S01** | Mechanical Mimicry | Response latency $\tau_L < 100\text{ ms}$ on $> 15\%$ of turns | Invalidate trial; controller pacing under-damped |
| **S02** | Acoustic Runaway | Tempo adjustment hitting $\pm 15\%$ clamp on $> 20\%$ consecutive turns | Invalidate trial; unstable positive feedback loop |
| **S03** | Phase Locking | Zero variance in turn-gap ($\sigma^2_{\text{gap}} < 10^{-6}$); rigid robotic periodicity | Flag as degenerate artifact; lacks naturalistic jitter |
| **S04** | Pseudo-Synchrony | C2 coordination metric fails to exceed surrogate $\theta_{95}$ reference | Surrogate null retained; observed coordination does not exceed pseudo-synchrony baseline |
| **S05** | Relational Inflation | Direct unmediated mutation of $\mathbf{R}_t$ or affect from raw sensory pacing | **FATAL INVARIANT VIOLATION**; violates Stage S16 pipeline |

---

## 14. Documentation Authority & Relational Vector ($R_t$)

The evaluation specification strictly adheres to repository governance regarding relational state representations:

### 14.1 Canonical Runtime Authority
All evaluation harnesses, test fixtures, and mock observers must reference the canonical production contract defined in [`src/core/relationship/state.py`](file:///c:/Users/Lunafiah/Desktop/My_project/Lucia/src/core/relationship/state.py):
$$\mathbf{R}_t = [\text{familiarity}, \text{trust}, \text{closeness}, \text{reciprocity}] \in [0.0, 1.0]^4$$
The canonical relationship representation remains strictly 4-dimensional ($\mathbf{R}_t \in \mathbb{R}^4$). Do **NOT** add a negative, grievance, or rupture dimension. Any such extension remains an unresolved owner/architecture decision.

### 14.2 Documentation Drift Isolation
In [`docs/ARCHITECTURE.md`](file:///c:/Users/Lunafiah/Desktop/My_project/Lucia/docs/ARCHITECTURE.md), an older conceptual vector appears:
$$\mathbf{R}_t = [\text{Trust}, \text{Familiarity}, \text{Attunement}, \text{Shared Experience}]$$
- This discrepancy is formally documented as historical **documentation drift**.
- The evaluation specification does **not** reconcile, alter, or patch either representation in production code.
- Production code must **not** be modified.

---

## 15. Invariant & Governance Guardrails

The evaluation protocol explicitly verifies system invariants before, during, and after experimental runs:

1. **One Continuous Life (`INV-1`):** No independent cognitive branches or competing continuous authorities may be spawned during simulation.
2. **Pre-Reflective Affect Boundary (`INV-2`):** Controllers and metrics must remain external diagnostic instruments. Lucia must never self-report or verbalize synchrony metrics.
3. **Genesis Onboarding Invariant (`INV-8`):**  
   [`data/profile.json`](file:///c:/Users/Lunafiah/Desktop/My_project/Lucia/data/profile.json) must remain bit-exact:
   ```json
   {"is_onboarded": false}
   ```
   Simulation $\neq$ Activation. No onboarding state transition may occur.

---

## 16. Research Isolation & Artifact Boundaries

To guarantee complete separation between exploratory research and production runtime:
- **Specification Path:** [`docs/PhaseDocs/Lucia-phase25-Temporal_Embodiment/EXP_P25_Q2_1_EVALUATION_SPECIFICATION.md`](file:///c:/Users/Lunafiah/Desktop/My_project/Lucia/docs/PhaseDocs/Lucia-phase25-Temporal_Embodiment/EXP_P25_Q2_1_EVALUATION_SPECIFICATION.md)
- **Future Test Harness Path:** `tests/evaluation/phase25/` (when authorized)
- **Persistent Artifacts & Telemetry:** `docs/PhaseDocs/Lucia-phase25-Temporal_Embodiment/evaluation_artifacts/phase25/`
- **Forbidden Directories:** No files in `src/core/**`, `src/api/**`, `electron/**`, or `config/**` may be created or modified.

---

## 17. Reproducibility & Environment Contract

The experimental environment must guarantee deterministic reproducibility:
- **Random Seeds:** Master seeds $S \in \{1001, 2002, 3003, 4004, 5005\}$ governing trial generation.
- **Hardware Profile:** 100% CPU execution on standard edge host; **0.0 MB GPU VRAM** target.
- **Python Runtime:** Python 3.12+ virtual environment (`.venv`).
- **Telemetry Emission:** All raw measurements must be emitted to `raw_telemetry_q2_1.json` alongside `summary_q2_1.csv`.
- **TBD Items Ledger:** Any variable not locked in Section 19 is explicitly recorded as TBD.

---

## 18. Scientific Outcome Categories & Epistemic Boundaries

Experimental results will be categorized into one of three explicit outcomes for each hypothesis:

| Outcome Class | Operational Meaning | Permitted Downstream Actions | Prohibited Downstream Actions |
|---|---|---|---|
| **SUPPORTED** | Statistically significant difference observed, surrogate rejected, controls satisfied | Authorize drafting of research report; evaluate candidate mechanism boundaries | **NO** production promotion, **NO** ADR authoring, **NO** new ontology, **NO** direct actuator-to-$\mathbf{R}_t$ writes |
| **NOT SUPPORTED / FALSIFIED** | No statistically significant difference observed ($\Delta_{\text{coord}} \le 0$ or $p \ge 0.05$) under tested conditions. Concluded as 'NOT SUPPORTED under tested conditions'; classified as FALSIFIED only if statistical power / equivalence testing formally rules out the minimum detectable effect size. | Archive empirical findings as evidence of reactive sufficiency (H-A) under tested parameters. | Do not overclaim universal falsification or claim proof of zero effect without equivalence testing; do not re-run identical parameterization without architectural justification. |
| **INCONCLUSIVE** | Inconsistent effect across seeds, high jitter, or execution failure modes triggered | Refine experimental protocol, recalibrate noise floor, or restage | Do not claim partial validation or lower acceptance thresholds |

---

## 19. Specification Open Questions & TBD Items Ledger

The following parameters are deliberately held as **TBD (To Be Determined)** for explicit resolution during harness implementation:

1. **`TBD-Q2-01` (Exact Dialogue Corpus Sentences):** The specific conversational prompts and simulated speech turn lengths for `FIXTURE-P25-Q2-SCRIPT-v0.1` must be finalized in test fixtures without altering lexical neutrality.
2. **`TBD-Q2-02` (KSG Estimator k-parameter):** While $k=4$ is staged as reference, calibration under short-time turn series ($N < 50$) will be verified empirically in the harness.
3. **`TBD-Q2-03` (User Simulated Cadence Model):** The exact stochastic model simulating user cadence variance (e.g., Ornstein-Uhlenbeck process vs autoregressive AR(1)) for offline automated harness testing.
4. **`TBD-Q2-04` (A Priori Feedback Gain Determination for $\mathbf{w}_{\text{fb}}$):** The scaling gain mapping user response increment $R_U$ into Lucia's controller state update $\mathbf{x}_t^{(\text{C2})}$.  
   *Strict Lockdown Requirements:*
   - The gain must be determined *a priori* or derived via an independent calibration procedure prior to running trials;
   - The gain must **NOT** be selected based on the comparative outcomes of C1 vs C2;
   - The gain must **NOT** be tuned post-hoc to maximize synchrony or force C2 to outperform C1;
   - If an independent empirical/theoretical basis is absent, the gain **MUST remain locked as TBD** and cannot be arbitrarily invented in the implementation (preventing C2 from becoming "C1 + a controller tuned to beat C1").

---

## 20. Governance Ledger & Gate Status

- **Evaluation Specification EXP-P25-Q2.1:** **RATIFIED AS SPECIFICATION**
- **Authoritative Gate Progression:** `P25-Q1 CLOSED` → `P25-Q2 CLOSED (H-A supported, C2 blocked, H-B unproven)` → `Architecture Candidate / Evidence Synthesis` → `Ciah Review` → `Owner Decision` → `Implementation Gate`
- **Condition C2 & Hypothesis H-B:** **C2 BLOCKED (under TBD-Q2-04), H-B UNPROVEN** (synchrony ≠ causality)
- **Evaluation Harness Implementation:** **STRICTLY BLOCKED / NOT STARTED**
- **Architecture Gate:** **LOCKED** (No ADR authorized)
- **Implementation Gate:** **LOCKED** (Zero production code mutations)
- **Production Diff:** **0 files**
- **Genesis Onboarding (`INV-8`):** **LOCKED & BIT-EXACT** (`{"is_onboarded": false}`)
