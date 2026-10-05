# P25-Q2: TBD-Q2-04 Identification Protocol Design Space — Scientific Audit & Methodological Mapping

> **DOCUMENT ID:** `DOC-P25-012`  
> **DOCUMENT TYPE:** RESEARCH SPECIFICATION / METHODOLOGICAL AUDIT & MAPPING  
> **PHASE:** PHASE 25 — TEMPORAL EMBODIMENT & SOCIAL FEEDBACK  
> **RESEARCH HORIZON:** P25-Q2 (Reciprocal Social Feedback Dynamics)  
> **TARGET PROBLEM:** Protocol Design Space for $w_{\text{fb}}$ System Identification (`TBD-Q2-04`)  
> **FINAL DECISION:** **`PROTOCOL DESIGN SPACE SUFFICIENTLY MAPPED`**  
> **Q2-04 EPISTEMIC STATUS:** **`EVIDENCE GAP / IDENTIFIABILITY ISSUE REMAINS OPEN`**  
> **PARAMETER STATUS:** **`w_fb NOT IDENTIFIED / NOT CALIBRATED / NOT RATIFIED`**  
> **CONDITION C2 GATE:** **`STRICTLY BLOCKED / FAIL-FAST WITH TBDGainUnestablishedError`**  
> **HYPOTHESIS $\mathcal{H}$-B:** **`BLOCKED / INCONCLUSIVE`**  
> **RERUN AUTHORIZATION:** **`NOT AUTHORIZED`**  
> **ARCHITECTURE GATE:** **`LOCKED`** (No production mutation; zero ADRs)  
> **IMPLEMENTATION GATE:** **`LOCKED`** (Zero production diff; `src/`, `electron/`, `data/`, `config/` untouched)  
> **GENESIS INVARIANT (`INV-8`):** **`PRESERVED BIT-EXACT`** (`data/profile.json == {"is_onboarded": false}`)  
> **GOVERNANCE INVARIANT:** `Design Space Mapped ≠ Protocol Selected ≠ Protocol Ratified ≠ w_fb Calibrated ≠ C2 Unblocked ≠ Rerun Authorized`

---

## 1. Executive Summary & Objective

This document provides a formal **correction-only scientific audit and design space mapping** for identifying the feedback gain $\mathbf{w}_{\text{fb}}$ (`TBD-Q2-04`) in Condition C2 of `EXP-P25-Q2.1`.

Following prior research clarification (`P25_Q2_RESEARCH_CLARIFICATION.md`, `DOC-P25-010`) and system identifiability auditing (`P25_Q2_Q2-04_WFB_IDENTIFIABILITY_AUDIT.md`, `DOC-P25-011`), this pass systematizes the experimental and observational design options capable of resolving the practical identifiability bottleneck.

### Core Objectives:
1. Systematically audit candidate protocol designs across observational, interventional, controller-regime, and instrumental-variable paradigms.
2. Remove ungrounded methodological overclaims, universal assertions, and premature structural assumptions.
3. Formally establish the boundary:
   $$\textbf{Protocol Design Space Sufficiently Mapped} \quad \ne \quad \textbf{Protocol Ratified / Experiment Ready}$$
4. Identify the prerequisite evidence properties required for valid closed-loop estimation without designing the final protocol or unblocking Condition C2.

---

## 2. Epistemic Audit of Core Methodological Claims

To eliminate overclaims while retaining valid control-theoretic and causal distinctions, the following core methodological claims are audited and corrected:

### 2.1 Instrumental Variables (IV) & Closed-Loop Endogeneity
- *Prior Overclaim:* "Hybrid Closed-Loop Identification + Instrumental Variables bypasses closed-loop endogeneity."
- *Audited Correction:*  
  - Instrumental Variable (IV) estimation is a **candidate identification methodology** for closed-loop settings with simultaneous feedback.
  - Its empirical validity depends entirely on unverified assumptions: instrument relevance ($\operatorname{Cov}(Z, X) \ne 0$), exclusion restriction / exogeneity ($\operatorname{Cov}(Z, \epsilon) = 0$), observability, and correct functional specification.
  - IV does **not** automatically remove endogeneity; an invalid or weak instrument produces severe asymptotic bias and inflated finite-sample variance.
  - No specific instrumental variable design has yet been evaluated or validated for Lucia's conversational controller.
- *Epistemic Status:* **`METHODOLOGICALLY PREFERRED / NOT YET VALIDATED FOR C2`**. No specific instrument is introduced or ratified in this document.

### 2.2 Natural Observational Interaction
- *Prior Overclaim:* "Natural observational interaction = No parameter identification / biased."
- *Audited Correction:*  
  - This claim was overly absolute. In linear and non-linear system identification, passive closed-loop observational data *can* achieve consistent parameter estimation under favorable conditions (e.g., delay in the feedback path, known noise spectrum, sufficiently high model order, or non-Gaussian innovations).
  - However, **under the current Q2-04 design and available evidence, natural observational interaction alone does not provide a sufficient demonstrated basis for identifying the actual C2 $w_{\text{fb}}$, and carries substantial endogeneity and collinearity risk.**
  - Passive observational data is not universally incapable of identification, but remains undemonstrated and high-risk for the specific C2 formulation.

### 2.3 Regressor Separation
- *Prior Overclaim:* "Data must break the strict linear feedback loop."
- *Audited Correction:*  
  - The necessary mathematical condition is: **the evidence must provide sufficient informative variation and separation of $o_k$ and $R_U(k)$ under the specified identification model.**
  - Breaking the loop entirely is merely one specific physical approach. Separation can potentially arise from:
    1. Controlled forward intervention (e.g. latency shifts);
    2. Controller-regime variation (e.g. multiple operating points);
    3. Informative natural variation (e.g. asymmetric user turn dynamics);
    4. Valid instrumental variables;
    5. Exogenous stochastic excitation;
    6. Other valid identification designs.
  - None of these mechanisms is universally mandatory at this stage.

### 2.4 Independently Grounded Variation
- *Prior Overclaim:* "Independently grounded variation is universally REQUIRED."
- *Audited Correction:*  
  - **Required Evidence Property:** The identification problem requires sufficient informative variation that is independently grounded enough to support the intended inference under the selected identification methodology.
  - **Status of Mechanism:** The exact mechanism generating that variation (external perturbation, natural user heterogeneity, multi-controller switching, or exogenous instrument) is **NOT YET RATIFIED**.
  - A general evidence property must not be conflated with a specific implementation mechanism.

### 2.5 Temporal Ordering vs. Causal Attribution
- *Audit Distinction:*  
  - **Temporal Ordering:** Establishes temporal precedence: $\text{Lucia output}(t) \to \text{User response}(t+\Delta)$. Temporal precedence is **`REQUIRED`** for forward dynamic modeling, but temporal precedence alone does *not* prove causal attribution (post hoc ergo propter hoc).
  - **Causal Attribution:** Requires explicit causal identification assumptions (e.g., unconfoundedness, randomized assignment, valid instruments, or structural invariance under intervention). Controlled intervention, randomized variation, or quasi-experimental contrasts may contribute depending on the adopted framework.
  - No single causal identification framework is universally mandatory.

### 2.6 Baseline / Reference Condition Status
- *Prior Overclaim:* "Baseline / reference condition = REQUIRED."
- *Audited Correction:*  
  - Because the operational definition of $R_U(k)$ remains unratified, the baseline requirement is:
    $$\textbf{METHODOLOGICALLY PREFERRED / CONDITIONALLY REQUIRED DEPENDING ON } R_U \textbf{ DEFINITION}$$
  - If $R_U(k)$ is explicitly formulated as a deviation from a moving-average baseline ($U(t+\Delta) - U_{\text{baseline}}(t)$), establishing an unperturbed baseline condition is necessary for that specific operationalization.
  - If alternative non-baseline-subtracted formulations are explored, a separate baseline condition may be optional. The baseline definition is not frozen here.

### 2.7 Estimator Stability & Consistency
- *Prior Overclaim:* "Must guarantee consistent convergence with bounded uncertainty."
- *Audited Correction:*  
  - In finite-sample human interaction experiments, mathematical consistency is an asymptotic property under specified model assumptions, not a universal empirical requirement.
  - The audit distinguishes:
    1. Convergence behavior under sample growth;
    2. Finite-sample estimator variance;
    3. Sensitivity to measurement noise;
    4. Robustness across interaction seeds;
    5. Theoretical consistency under explicit identification assumptions.
  - No numerical uncertainty thresholds or confidence intervals are arbitrarily invented at this stage.

### 2.8 Prediction Error Methods (PEM) in Closed Loop
- *Prior Overclaim:* "Naive Direct PEM on natural data will converge to biased/incorrect values."
- *Audited Correction:*  
  - In closed-loop system identification (Ljung 1999; Forssell & Ljung 1999), direct prediction error methods (Direct PEM) applied to closed-loop data **may suffer from bias, inconsistency, or invalid inference under certain feedback, noise, or model structures** (e.g., if the controller feedback is exact and noise-free, causing regressor collinearity).
  - Direct PEM can be consistent if the feedback loop contains sufficient delay and the noise model is correctly parameterized.
  - The failure mode is preserved as a severe practical hazard, but not asserted as a universal impossibility theorem.

---

## 3. Protocol Design Space Classification

The design space for establishing data informative enough to estimate or calibrate $w_{\text{fb}}$ spans four primary protocol classes:

```
┌────────────────────────────────────────────────────────────────────────┐
│                   PROTOCOL DESIGN SPACE TAXONOMY                       │
├────────────────────┬────────────────────┬──────────────────────────────┤
│ Protocol Class     │ Intervention / Mod │ Primary Identifiability Base │
├────────────────────┼────────────────────┼──────────────────────────────┤
│ Class 1: Passive   │ None (naturalistic │ Natural user stochasticity,  │
│ Observational      │ interaction)       │ lag dynamics, multi-session  │
├────────────────────┼────────────────────┼──────────────────────────────┤
│ Class 2: Inter-    │ Lucia-output       │ Forward causal variation     │
│ ventional Forward  │ perturbations      │ breaking collinearity        │
├────────────────────┼────────────────────┼──────────────────────────────┤
│ Class 3: Multi-    │ Controller-regime  │ Discrete operating regime    │
│ Regime Switching   │ variation          │ contrast (gain / delay)      │
├────────────────────┼────────────────────┼──────────────────────────────┤
│ Class 4: Instru-   │ Exogenous source / │ Instrumental variable        │
│ mental / Two-Stage │ two-stage mapping  │ orthogonality condition      │
└────────────────────┴────────────────────┴──────────────────────────────┘
```

### 3.1 Class 1: Passive Observational Interaction
- **Mechanism:** Continuous natural interaction between user and agent without injected timing perturbations.
- **Evaluation:** High ecological validity, zero conversational disruption. However, in short turn sequences ($N \approx 40$), natural cadence tends toward synchrony, causing high collinearity between $o_k$ and $R_U(k)$.
- **Status:** **`HIGH CONFOUNDING RISK / NOT DEMONSTRATED FOR C2`**.

### 3.2 Class 2: Interventional Forward Perturbation
- **Mechanism:** Structured, randomized, or pseudo-random timing shifts injected into Lucia's output latency $\tau_L(k)$ or tempo $\Delta v_L(k)$ (e.g. step delay, dither, or phase impulse).
- **Evaluation:** Directly generates forward variation: $\text{Lucia Actuation } B_L(t) \to \text{User Event } U(t+\Delta)$.
- **Epistemic Correction:** Does not automatically guarantee identification; success depends on whether the user's reactive response $R_U(t+\Delta)$ is measurable above baseline noise and accurately captured by the feature extractor.
- **Status:** **`METHODOLOGICALLY PROMISING CANDIDATE / UNRATIFIED`**.

### 3.3 Class 3: Controller-Regime Variation
- **Mechanism:** Operating the agent under multiple distinct controller parameterizations across sessions or blocks (e.g., varying $\lambda$, nominal latency $\tau_{\text{nom}}$, or observation gain $w_{\text{obs}}$).
- **Evaluation:** Provides quasi-experimental contrast across different closed-loop transfer functions. In linear systems, varying the feedback controller across multiple regimes is a standard technique to achieve full parameter identifiability (Ljung 1999).
- **Epistemic Correction:** Does not automatically identify $w_{\text{fb}}$ unless the user's internal response model is invariant across regimes.
- **Status:** **`PROVISIONAL / METHODOLOGICALLY PROMISING`**.

### 3.4 Class 4: Instrumental Variable / Two-Stage Closed-Loop Estimation
- **Mechanism:** Employing an exogenous signal $Z_k$ (e.g. conversational prompt length, topic switch event, or randomized latency seed) correlated with Lucia's actuation but uncorrelated with conversational turn error innovations.
- **Evaluation:** Well-established econometrical and control-theoretic framework for consistent estimation under feedback endogeneity.
- **Epistemic Correction:** Valid instruments are notoriously difficult to isolate in dyadic speech, and weak instruments cause severe finite-sample degradation.
- **Status:** **`METHODOLOGICALLY PREFERRED / NOT YET VALIDATED FOR C2`**.

---

## 4. Evaluation of Actuator & Interlocutor Perturbation Roles

To clarify the causal structure of candidate perturbations:

```
[Lucia Controller] ──> [Lucia Output Perturbation] ──> [User Response] ──> [Lucia Feedback Input]
         │                                                      │
         └─── Forward Causal Probe for Lucia -> User            └─── Manipulating User Response
              (Informative for Dyadic Identification)                (Not directly appropriate
                                                                      for identifying w_fb)
```

### 4.1 Lucia-Output Perturbation
- **Role:** Modulating agent expressive parameters (e.g., injecting $+300\text{ ms}$ delay or shifting syllabic rate).
- **Methodological Character:** Probes the forward causal link $\text{Lucia}(t) \to \text{User}(t+\Delta)$. If user response dynamics exist, this generates independent variation in $R_U(k)$ relative to baseline $o_k$.
- **Correction:** Perturbation validity depends on user perceptual threshold and response latency; no specific perturbation waveform (step, pulse, dither) is ratified.

### 4.2 User-Response Perturbation
- **Role:** Directly manipulating the user's measured response (e.g. synthetically altering $R_U$).
- **Methodological Character:** Manipulating user response directly does not identify Lucia's internal feedback gain; it tests Lucia's controller sensitivity to artificial inputs. Its usefulness is limited to controller stress-testing, not dyadic system identification.

---

## 5. Minimum Protocol Properties Ledger

A scientifically defensible protocol for identifying $w_{\text{fb}}$ must be evaluated across the following essential properties:

| # | Protocol Property | Epistemic Classification | Scientific Rationale |
|---|---|---|---|
| **1** | **Temporal Observability / Order** | **`REQUIRED`** | Essential for forward temporal tracking ($\text{Lucia}_t \to \text{User}_{t+\Delta}$). |
| **2** | **Causal Attribution** | **`REQUIRED AS EVIDENCE GOAL`** | Core scientific purpose of C2; exact causal methodology remains open. |
| **3** | **Informative Regressor Variation** | **`REQUIRED AS EVIDENCE PROPERTY`** | Required to prevent regressor collinearity; mechanism remains open. |
| **4** | **Measurable Output & Response** | **`REQUIRED`** | Sensors must capture turn transitions and prosody above noise floor. |
| **5** | **Baseline / Reference Condition** | **`CONDITIONALLY REQUIRED`** | Depends on whether $R_U$ operationalization requires baseline subtraction. |
| **6** | **Repeated Independent Units** | **`REQUIRED FOR REPRODUCIBILITY`** | Required for statistical inference; exact unit structure (turns/sessions) open. |
| **7** | **Out-of-Sample Validation** | **`METHODOLOGICALLY PREFERRED`** | Prevents overfitting; specific split rules remain open. |
| **8** | **Explicit Latency Treatment** | **`REQUIRED`** | Audio pipeline and dispatch delays must be explicitly budgeted ($< 2.0\text{ ms}$). |

---

## 6. Protocol-to-Evidence Matrix

To map candidate protocol classes against required evidence properties without declaring an exclusive path:

| Required Evidence Property | Class 1: Passive Observational | Class 2: Interventional Forward | Class 3: Multi-Regime Switching | Class 4: Instrumental / Two-Stage |
|---|---|---|---|---|
| **Informative Variation** | Weak / Low Excitation | Strong (Controlled) | Moderate (Multi-point) | Strong (if instrument strong) |
| **Endogeneity Control** | High Risk of Bias | Bounded by Intervention | Bounded across Regimes | Explicitly Addressed |
| **Ecological Naturalness** | Maximum | Moderate Disruption | High (Natural dialogue) | High (Natural dialogue) |
| **Implementation Complexity** | Minimal | Low (Timing offsets) | Moderate (Controller blocks) | High (Instrument isolation) |
| **Maturity for Lucia C2** | Undemonstrated | Conceptual Candidate | Conceptual Candidate | Methodologically Preferred |

### Synthesis Rule
Informative variation is **`REQUIRED AS AN EVIDENCE PROPERTY`**; however, whether that variation is achieved via controlled intervention, regime switching, instrumental variables, or structured natural contrast is a **`METHODOLOGICAL CHOICE`** to be investigated, not an architectural dogma.

---

## 7. Systematic Failure Mode Analysis

The protocol design space contains four well-characterized methodological hazards:

```
┌────────────────────────────────────────────────────────────────────────┐
│                   METHODOLOGICAL FAILURE MODES                         │
├───────────────────────────────┬────────────────────────────────────────┤
│ FM-1: Circular Synthetic Loop │ FM-2: Metric Equivalence Fallacy       │
│ Tuning w_fb to track an       │ Assuming TE > 0 or r₁ > θ₉₅           │
│ unvalidated synthetic user    │ proves that w_fb is identified.        │
│ creates a self-fulfilling     │ (Diagnostic metrics are not            │
│ simulation artifact.          │ parameter estimators).                 │
├───────────────────────────────┼────────────────────────────────────────┤
│ FM-3: Common-Cause Pacing     │ FM-4: Naive Closed-Loop PEM            │
│ Shared script structure       │ Direct regression in closed loop       │
│ creates apparent correlation  │ may yield biased, inconsistent         │
│ without causal coupling.      │ estimates under feedback endogeneity.  │
└───────────────────────────────┴────────────────────────────────────────┘
```

1. **FM-1 (Circular Synthetic User Coupling):**  
   *Risk:* Designing a synthetic user model with unratified coupling ($\beta_U$) and fitting $w_{\text{fb}}$ to optimize synchrony in simulation.  
   *Correction:* Identifies parameters of the synthetic fixture, not the true C2 interaction.
2. **FM-2 (Conflating Diagnostic Metrics with Identification):**  
   *Risk:* Assuming that observing $\text{TE} > 0$ or $r_1 > \theta_{95}$ means $w_{\text{fb}}$ has been identified.  
   *Correction:* Diagnostic synchrony metrics detect statistical association; they do not estimate structural feedback gains.
3. **FM-3 (Common-Cause Script Entrainment):**  
   *Risk:* Spurious coupling created by shared script pacing rather than genuine mutual adaptation.  
   *Correction:* Controlled by cross-session surrogate null reference ($\theta_{95}$).
4. **FM-4 (Closed-Loop Estimation Bias):**  
   *Risk:* Direct OLS / naive PEM regression on closed-loop data without addressing simultaneous feedback.  
   *Correction:* Requires appropriate closed-loop identification design (IV, two-stage, or interventional decoupling).

---

## 8. Methodological Invariants: What Can and Cannot Be Frozen

To protect research-first governance, this audit explicitly codifies the boundary between established methodological invariants and open design parameters:

### 8.1 Methodological Invariants (FROZEN)
1. **Separation of Concepts:** Association $\ne$ Information Flow $\ne$ Causal Attribution $\ne$ Parameter Identification.
2. **Observability Requirement:** Regressor variables $\mathbf{o}_k$ and $\mathbf{R}_U(k)$ must be physically observable and measurable from sensor streams.
3. **Informative Variation:** Parameter identification requires sufficient informative variation between regressors under the chosen identification model.
4. **Reproducibility Structure:** Statistical evidence requires repeated independent interaction units (cross-session or cross-block).
5. **Latency Accounting:** Hardware, acoustic buffer, and algorithmic dispatch latencies must be explicitly quantified.

### 8.2 Open Design Parameters (NOT FROZEN)
1. **Instrumental Variable Selection:** No specific instrument ($Z_k$) is ratified.
2. **Perturbation Waveform:** No specific dither, step delay, or timing modulation is adopted.
3. **Intervention Exclusivity:** Controlled perturbation is not declared the sole valid route to identification.
4. **Baseline Definition:** Operational construction of $U_{\text{baseline}}(t)$ remains open.
5. **Specific Estimator:** Exact numerical estimator (Two-Stage Least Squares, Closed-Loop PEM, Bayesian system identification) is not frozen.
6. **HITL Exclusivity:** Human-in-the-loop interaction is not declared universally mandatory for all preliminary identification research.

---

## 9. Next Research & Design Step

To ensure governance compliance:

> [!CAUTION]
> **GOVERNANCE CONSTRAINT ON NEXT STEPS:**  
> Agents are strictly prohibited from inventing a new numbered phase (e.g. "Phase 28") or formal sub-phase (e.g. "P25-Q2.2") without explicit project authorization.

### The Authorized Next Step:
**`Next research/design step: Q2-04 Protocol Specification Research Pass`**

This is an analytical research and design activity strictly contained within the existing planned horizon of **Phase 25 (Temporal Embodiment & Social Feedback)**. Its mandate will be to:
1. Formalize alternative concrete protocol specifications within Classes 2, 3, and 4;
2. Evaluate estimator robustness and sample size requirements mathematically;
3. Prepare a formal protocol specification for review before any harness implementation or experiment authorization.

---

## 10. Final Decision & Epistemic Verdict

In accordance with the audited evidence:

### **`FINAL DECISION: PROTOCOL DESIGN SPACE SUFFICIENTLY MAPPED`**

### Narrow Interpretation of Verdict:
- The evidence requirements, protocol design classes, methodological properties, failure modes, and open design parameters are **sufficiently mapped to permit a future protocol-specification research pass**.
- **This verdict does NOT mean:**
  - Protocol is selected;
  - Protocol is ratified;
  - Experiment is ready;
  - Rerun is authorized;
  - Condition C2 is unblocked;
  - $w_{\text{fb}}$ is calibrated;
  - Human-in-the-loop interaction is universally required.

---

## 11. Governance Ledger & Verification Summary

| Governance Dimension | Status | Verification Detail |
|---|---|---|
| **Q2-04 Epistemic State** | **`IDENTIFIABILITY ISSUE REMAINS OPEN`** | Admissible design space mapped; parameter unidentified |
| **Feedback Gain $w_{\text{fb}}$** | **`NOT IDENTIFIED / NOT CALIBRATED`** | Zero numerical values chosen or tuned |
| **Condition C2 Gate** | **`STRICTLY BLOCKED / FAIL-FAST`** | [`tests/evaluation/phase25/exp_p25_q2_1.py#L301-L308`](file:///c:/Users/Lunafiah/Desktop/My_project/Lucia/tests/evaluation/phase25/exp_p25_q2_1.py#L301-L308) raises `TBDGainUnestablishedError` |
| **Hypothesis $\mathcal{H}$-B** | **`BLOCKED / INCONCLUSIVE`** | Reciprocal incrementality unexamined |
| **Rerun Authorization** | **`NOT AUTHORIZED`** | Rerun gate remains locked |
| **Experiment Execution** | **`NOT EXECUTED`** | Zero trials run; zero new outcome numbers |
| **Production Codebase Diff** | **`0 files changed`** | `git diff --stat -- src/ data/ electron/ config/` is empty |
| **Relational State ($\mathbf{R}_t$)** | **`UNCHANGED`** | Canonical 4D contract in `src/core/relationship/state.py` preserved |
| **Genesis Onboarding (`INV-8`)** | **`BIT-EXACT`** | [`data/profile.json`](file:///c:/Users/Lunafiah/Desktop/My_project/Lucia/data/profile.json) is bit-exact: `{"is_onboarded": false}` |
| **Architecture Gate** | **`LOCKED`** | No ADR authored or adopted |
| **Implementation Gate** | **`LOCKED`** | Phase 25 remains `PLANNED` |

> **GOVERNANCE REMINDER:**  
> **Protocol Design Space Mapped ≠ Protocol Ratified ≠ Experiment Authorized ≠ C2 Unblocked.**  
> Condition C2 remains strictly fail-fast blocked under research-first governance.
