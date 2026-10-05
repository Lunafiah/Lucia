# P25-Q2: TBD-Q2-04 Identification Protocol Specification — Scientific Audit & Candidate Re-Evaluation

> **DOCUMENT ID:** `DOC-P25-013`  
> **DOCUMENT TYPE:** RESEARCH SPECIFICATION / SCIENTIFIC AUDIT & RE-EVALUATION  
> **PHASE:** PHASE 25 — TEMPORAL EMBODIMENT & SOCIAL FEEDBACK  
> **RESEARCH HORIZON:** P25-Q2 (Reciprocal Social Feedback Dynamics)  
> **TARGET PROBLEM:** Protocol Specification for $w_{\text{fb}}$ System Identification (`TBD-Q2-04`)  
> **FINAL DECISION:** **`PROTOCOL CANDIDATE SELECTION NOT RATIFIED — SCIENTIFIC CORRECTIONS REQUIRED`**  
> **DESIGN SPACE STATUS:** **`PROTOCOL DESIGN SPACE SUFFICIENTLY MAPPED`**  
> **EXTENDED IV STATUS:** **`STRONG CANDIDATE / NOT RATIFIED`**  
> **HITL PARADIGM STATUS:** **`STRONG CANDIDATE / NOT PROVEN UNIQUELY NECESSARY`**  
> **PARAMETER STATUS:** **`w_fb NOT IDENTIFIED / NOT CALIBRATED / NOT RATIFIED`**  
> **CONDITION C2 GATE:** **`STRICTLY BLOCKED / FAIL-FAST WITH TBDGainUnestablishedError`**  
> **HYPOTHESIS $\mathcal{H}$-B:** **`BLOCKED / INCONCLUSIVE`**  
> **RERUN AUTHORIZATION:** **`NOT AUTHORIZED`**  
> **ARCHITECTURE GATE:** **`LOCKED`** (No production mutation; zero ADRs)  
> **IMPLEMENTATION GATE:** **`LOCKED`** (Zero production diff; `src/`, `electron/`, `data/`, `config/` untouched)  
> **GENESIS INVARIANT (`INV-8`):** **`PRESERVED BIT-EXACT`** (`data/profile.json == {"is_onboarded": false}`)  
> **GOVERNANCE INVARIANT:** `Design Space Mapped ≠ Candidate Selected ≠ Protocol Ratified ≠ w_fb Calibrated ≠ C2 Unblocked ≠ Rerun Authorized`

---

## 1. Executive Summary & Audit Mandate

Following the formal mapping of the protocol design space ([`P25_Q2_Q2-04_PROTOCOL_DESIGN_SPACE.md`](file:///c:/Users/Lunafiah/Desktop/My_project/Lucia/docs/PhaseDocs/Lucia-phase25-Temporal_Embodiment/P25_Q2_Q2-04_PROTOCOL_DESIGN_SPACE.md), `DOC-P25-012`), this document provides a rigorous **correction-only scientific audit** of the candidate protocol specification proposal (*"Closed-Loop Extended IV Protocol"*).

The proposal asserted that a Closed-Loop Extended Instrumental Variable (IV) design combined with active Human-in-the-Loop (HITL) excitation officially settles the identification methodology and guarantees consistent recovery of the true C2 feedback gain $w_{\text{fb}}$. 

**This scientific audit establishes that the proposed selection is NOT RATIFIED.** The proposal contains critical methodological conflations—most centrally treating endogenous user behavioral response $R_U$ as if it were an exogenous instrumental variable—and overstates asymptotic mathematical guarantees. 

This document systematically refutes those overclaims, restores sound control-theoretic and econometrics foundations, and codifies the precise epistemic boundaries under which protocol specification research must proceed.

---

## 2. Critical Methodological Audits & Corrective Refutations

### 2.1 Critical Correction: Conflation of User Response $R_U$ with External Instrument $r_{\text{ext}}$

The candidate proposal conflated two fundamentally distinct objects in closed-loop system theory:

$$\begin{aligned}
\text{Lucia Output } o_k &\longrightarrow \text{User Behavioral Response } R_U(k+\Delta) \\
R_U(k+\Delta) &\longrightarrow \text{Lucia Adaptation } \Delta o_{k+2\Delta} \quad (\text{governed by } w_{\text{fb}})
\end{aligned}$$

1. **Definition of $R_U$ in Lucia C2:**
   $R_U$ is the **observed user behavioral response** following Lucia's preceding communicative output $o_k$. By structural definition, $R_U$ is inside the feedback loop, influenced by Lucia's outputs, personal user state, environmental distractions, unobserved conversational history, and measurement noise $e_U(k)$.
2. **The Proposal's Fatal Conflation:**
   The proposal treated $R_U$ as if it were a classical external reference signal $r(t)$ or an exogenous instrument $Z$ that enters from outside the feedback loop. It proposed *"active HITL injecting exogenous $R_U$"*.
3. **Scientific Refutation:**
   - **$R_U$ MUST NOT be classified as exogenous by assumption.** User response is inherently endogenous in conversational interaction.
   - **$R_U$ MUST NOT be promoted to an instrumental variable.** An instrumental variable $Z$ must satisfy the exclusion restriction $\operatorname{Cov}(Z, \epsilon) = 0$. Since user response $R_U$ is coupled with the unobserved conversational dynamics and noise, assuming it is uncorrelated with the error term is ungrounded.
   - **$R_U$ MUST NOT be described as independent of noise/disturbance without empirical evidence.**
   - Assuming $R_U$ is a valid instrument introduces circular reasoning: validating that $R_U$ faithfully reflects forward conversational coupling is part of the unresolved Q2-04 identification question itself.
4. **Correct Formal Distinction ($R_U$ vs $r_{\text{ext}}$):**
   - If an external reference or perturbation signal is introduced to excite the loop, it must be designated with a distinct symbol, e.g., $r_{\text{ext}}(t)$ (or $d_{\text{ext}}(t)$).
   - $r_{\text{ext}}(t)$ represents an experimentally controlled perturbation (e.g., an exogenous acoustic prompt offset, scripted conversational probe, or randomized interaction stimulus) that is generated independently of the dyad.
   - $R_U(t)$ remains strictly the **endogenous measured user response**.
   - The existence, physical feasibility, experimental validity, and usefulness of an external instrument $r_{\text{ext}}$ remain **open research questions**.

---

### 2.2 Reclassification of Closed-Loop Extended IV

- *Proposal Overclaim:* "Closed-Loop Extended IV Protocol is officially selected and guarantees $w_{\text{fb}}$ identification."
- *Audited Correction:*
  - **`Extended IV = STRONG CANDIDATE / NOT RATIFIED`**
  - Instrumental Variable estimation is a well-established candidate framework for systems operating in closed loop (e.g., Landau, Ljung, Söderström & Stoica). However, its consistency and validity strictly depend on five necessary conditions:
    1. **Instrument Relevance:** $\operatorname{Rank}\left(\mathbb{E}\left[Z_k \varphi_k^T\right]\right) = \dim(\theta)$, ensuring the instrument is sufficiently correlated with the endogenous regressors.
    2. **Exclusion / Exogeneity:** $\mathbb{E}\left[Z_k \epsilon_k\right] = 0$, ensuring the instrument is asymptotically orthogonal to equation errors and unmodeled disturbances.
    3. **Order / Rank Identifiability:** The instrument dimension must be at least as large as the parameter dimension, and the excitation matrix must be non-singular.
    4. **Observability:** All regressor and instrument components must be observable with characterized measurement latency and noise properties.
    5. **Correct Structural Model:** The parameterization must accurately capture the underlying linear/non-linear dynamics without structural misspecification.
  - **IV does NOT automatically:**
    - Remove unobserved confounding;
    - Guarantee causal identification;
    - Guarantee parameter identification;
    - Guarantee estimator consistency;
    - Guarantee finite-sample unbiasedness;
    - Eliminate the necessity of strict modeling assumptions.
  - Weak instruments yield severe finite-sample bias (often exceeding OLS bias) and vast parameter variance. No instrumental design has yet been empirically tested or validated for Lucia's communicative state space.

---

### 2.3 Strict Decoupling of the Four Inference Levels

A critical defect in the proposal was treating causal demonstration as synonymous with parameter estimation. The four levels of inference must remain explicitly decoupled:

```text
Level 1: Association / Correlation
    │   Cov(Lucia, User) ≠ 0
    ▼
Level 2: Temporal Precedence / Information Transfer
    │   TE(Lucia → User) > 0, Granger causality, lagged cross-correlation
    ▼
Level 3: Causal Influence / Intervention Effect
    │   do(Lucia = o*) → E[User | do(o*)] ≠ E[User]
    ▼
Level 4: Structural Parameter Identification
        w_fb uniquely and consistently recovered from observations
```

> [!IMPORTANT]
> **Causal Influence $\ne$ Parameter Identification**  
> Even if a controlled intervention proves that Lucia's output exerts a statistically significant causal effect on user response ($\text{Level 3}$), that causal effect does **not** by itself establish that the resulting data uniquely identify the internal gain parameter $w_{\text{fb}}$ of Condition C2 ($\text{Level 4}$).  
> Parameter identification requires:
> 1. A defensible mathematical mapping from the causal response surface to the specific structural parameter $w_{\text{fb}}$;
> 2. Sufficient empirical information to isolate $w_{\text{fb}}$ from user sensitivity $\beta_U$, internal cognitive latencies $\tau$, and environmental disturbances.

---

### 2.4 Structural Identifiability vs Optimization Minimization

- *Proposal Overclaim:* "Structural identifiability is proven because the quadratic cost function has a unique global minimizer when the regressor matrix is full rank."
- *Audited Correction:*
  - Having a unique minimizer in a sample objective function is a property of convex numerical optimization, **not** structural identifiability.
  - The distinct concepts must be separated:
    1. **Model Structural Identifiability:** Theoretical property that distinct parameter vectors generate distinct probability distributions of the observables: $\theta_1 \ne \theta_2 \implies P(Y | \theta_1) \ne P(Y | \theta_2)$ under infinite noise-free data.
    2. **Parameter-to-Observable Mapping:** The injectivity of the transfer function or state-space mapping from system parameters $(w_{\text{fb}}, \beta_U, \tau)$ to the observable input-output sequences.
    3. **Estimator Consistency:** Asymptotic convergence of $\hat{\theta}_N \xrightarrow{p} \theta_0$ as $N \to \infty$.
    4. **Optimization / Numerical Solvability:** Presence of a unique global minimum in finite-sample loss surfaces $\mathcal{J}_N(\theta)$.
    5. **Practical Identifiability:** Ability to estimate parameters with acceptable confidence intervals given finite, noisy, collinear, or bandwidth-limited real data.
  - A full-rank regressor matrix across a specific sample does **not** prove structural identifiability of the complete closed-loop C2 dyad.
  - Current Status: **`Structural Identifiability: PLAUSIBLE / NOT DEMONSTRATED`**.

---

### 2.5 Persistent Excitation (PE) and Informative Variation

- *Proposal Overclaim:* "Persistent excitation of order $2n$ is universally mandatory for any parameter identification."
- *Audited Correction:*
  - In classical linear system identification, a signal $u_k$ is persistently exciting of order $n$ if the spectrum is non-zero at $\ge n$ points. While this is a sufficient condition for linear difference equations, it is **not** a universal numerical requirement across all closed-loop identification paradigms.
  - For Q2-04, the scientifically defensible requirement is:
    > **Sufficient informative variation and regressor separation are required under the chosen model and identification method; the exact excitation condition depends on the model structure, estimator, sampling interval, dynamic orders, and observation design.**
  - Classical PE is a **candidate formal condition**, but no specific numerical PE order is ratified for Lucia.

---

### 2.6 Methodological Comparison: Direct PEM, Subspace, and IV

The proposal claimed that Direct Prediction Error Methods (PEM) are inherently biased, Subspace Identification is categorically invalid, and Extended IV is universally superior.

*Audited Scientific Comparison:*

| Method Class | Theoretical Status in Closed Loop | Empirical Vulnerability in C2 | Epistemic Classification |
|---|---|---|---|
| **Direct PEM** | Consistent if the noise model is correctly specified, or if adequate causal delays exist in the loop ($\Delta \ge 1$). | Severe parameter bias if the disturbance model is misspecified or if feedforward/feedback delays are unmodeled. | `CANDIDATE METHOD / CONDITIONAL` |
| **Two-Stage / Indirect** | Estimates open-loop dynamics using known controller dynamics. | Requires complete knowledge of Lucia's and User's controller equations; sensitive to model order mismatch. | `CANDIDATE METHOD / COMPLEX` |
| **Subspace Identification (4SID)** | Consistent closed-loop variants exist (e.g., PBSID, predictor-based subspace). | Requires large state orders and high sample rates; sensitive to non-uniform conversational turn latencies. | `CANDIDATE METHOD / SENSITIVE` |
| **Extended IV** | Consistent if valid instruments $Z_k$ exist that are correlated with inputs and orthogonal to noise. | Severe variance inflation and bias if instruments are weak or if user response $R_U$ is erroneously treated as exogenous. | `STRONG CANDIDATE / NOT RATIFIED` |

**Conclusion:** Applicability, consistency, and efficiency depend on loop delays, controller properties, observability, noise models, and identification design. No method is universally superior independent of empirical validation.

---

### 2.7 Cramér–Rao Bound and Efficiency Overclaim

- *Proposal Overclaim:* "Tailor-made IV asymptotically approaches the Cramér–Rao lower bound, ensuring optimal statistical efficiency."
- *Audited Correction:*
  - While optimal instrumental variable estimators (such as those using optimal prefilters $W(q)$ and instruments generated from noise-free simulations) can asymptotically achieve the Cramér–Rao lower bound under linear Gaussian conditions with known noise spectra (Ljung, 1999), this holds only when the true system lies in the model set ($\mathcal{S} \in \mathcal{M}$) and the noise color is known exactly.
  - For the conversational feedback loop with human behavioral variance, these assumptions are wholly unverified.
  - Status: **`NOT ESTABLISHED`**.

---

### 2.8 Non-Gaussian Noise Assertions

- *Proposal Overclaim:* "IV automatically wins and provides consistent estimates because human conversation noise is non-Gaussian."
- *Audited Correction:*
  - Non-Gaussian noise does not automatically favor IV over PEM or maximum likelihood methods. In fact, non-Gaussian innovations can permit direct identification in closed loops where Gaussian systems are non-identifiable (e.g., ICA-based and higher-order moment identification).
  - Regardless of noise distribution, IV consistency still strictly depends on instrument exogeneity $\mathbb{E}[Z_k \epsilon_k] = 0$ and relevance. Non-Gaussianity neither bypasses endogeneity nor validates an instrument.

---

### 2.9 Human-in-the-Loop (HITL) Necessity Audit

- *Proposal Overclaim:* "Active Human-in-the-Loop (HITL) intervention is the unique prerequisite for identifying $w_{\text{fb}}$."
- *Audited Correction:*
  - **`HITL = STRONG CANDIDATE / NOT PROVEN UNIQUELY NECESSARY`**
  - While active human interaction provides authentic ecological validity, it is not proven to be the *sole* viable identification pathway. Candidate alternatives include:
    1. **Controlled HITL Intervention:** Human user subjected to controlled, non-disruptive timing perturbations.
    2. **Experimentally Manipulated Multi-Dyad Corpora:** Re-analysis of structured conversational datasets with randomized experimental conditions.
    3. **Controller-Regime Variation:** Operating Lucia under multiple known controller regimes to produce identifiability without manipulating the user.
    4. **Independently Grounded Stochastic Variation:** Utilizing exogenous environmental or contextual timing variations if verified as exogenous.
    5. **Valid External Instruments:** Employing verifiable exogenous instruments ($r_{\text{ext}}$) if discovered.
  - No single variation source is ratified as exclusive.

---

### 2.10 Existing Observational Datasets

- *Proposal Overclaim:* "All existing conversational datasets (such as SEMAINE) are categorically useless for parameter identification."
- *Audited Correction:*
  - Existing datasets are **not** categorically useless:
    - They provide empirical boundary conditions, baseline variance spectra, realistic conversational latency distributions, and prior distributions for cognitive parameters.
    - Datasets with distinct condition contrasts (e.g., SEMAINE's multiple Sensitive Artificial Listener [SAL] character modes) exhibit regime-shifting dynamics that can illuminate behavioral responsiveness.
  - However: **no reviewed existing dataset has yet been demonstrated to identify Lucia's actual C2 feedback parameter $w_{\text{fb}}$**. The distinction between observing natural human variance and identifying a specific synthetic control parameter remains absolute.

---

### 2.11 Prohibition of Absolute Guarantees

- *Proposal Overclaim:* "The protocol guarantees that $w_{\text{fb}}$ represents real structural control reality."
- *Audited Correction:*
  - Deleted entirely. No empirical identification protocol can offer absolute epistemological guarantees.
  - Permitted scientific statement:
    > **"The protocol could provide a defensible route to parameter identification if its structural assumptions, instrument validity conditions, and empirical observability requirements are rigorously satisfied."**

---

## 3. Comprehensive Epistemic State Matrix

The authoritative status of all components following this scientific audit is codified below:

| Component / Subsystem | Current Epistemic Status | Governing Principle / Constraint |
|---|---|---|
| **Protocol Design Space** | **`SUFFICIENTLY MAPPED`** | Classes 1–5 mapped in `DOC-P25-012` |
| **Extended Instrumental Variables (IV)** | **`STRONG CANDIDATE / NOT RATIFIED`** | Feasible closed-loop framework; validity unverified |
| **Human-in-the-Loop (HITL)** | **`STRONG CANDIDATE / NOT PROVEN UNIQUELY NECESSARY`** | High ecological validity; alternative routes remain open |
| **External Instrument ($r_{\text{ext}}$)** | **`NOT ESTABLISHED`** | Concept defined; concrete realization undiscovered |
| **$R_U$ as Instrument** | **`INVALID ASSUMPTION / MUST NOT BE PROMOTED`** | $R_U$ is endogenous user response; conflation rejected |
| **$R_U$ Operational Definition** | **`OPEN / MUST BE OPERATIONALIZED`** | Baseline/reference metric awaiting formal operationalization |
| **Structural Identifiability** | **`PLAUSIBLE / NOT DEMONSTRATED`** | Theoretical mapping open; rank tests unexecuted |
| **Practical Identifiability** | **`HIGH CONFOUNDING RISK`** | Collinearity and observational confounding unmitigated |
| **Feedback Gain Parameter $w_{\text{fb}}$** | **`UNIDENTIFIED / UNCALIBRATED / UNRATIFIED`** | Zero numerical calibration adopted |
| **Condition C2 Gate** | **`STRICTLY BLOCKED / FAIL-FAST`** | Throws `TBDGainUnestablishedError` |
| **Hypothesis $\mathcal{H}$-B** | **`BLOCKED / INCONCLUSIVE`** | Cannot evaluate without unblocking C2 |
| **Experiment Rerun Authorization** | **`NOT AUTHORIZED`** | Prerequisite protocol specification pass incomplete |
| **Phase 25 Overall** | **`PLANNED`** | Research horizon; not Lucia Activation |

---

## 4. What Remains Open for Protocol Specification

To prevent premature closure, the following technical dimensions are formally cataloged as **unresolved research questions**:

1. **Identification of Valid $r_{\text{ext}}$:** Can an external stimulus or experimental perturbation be engineered that satisfies both instrument relevance ($\operatorname{Cov}(r_{\text{ext}}, o_k) \ne 0$) and exclusion ($\operatorname{Cov}(r_{\text{ext}}, e_U) = 0$)?
2. **Operational Definition of $R_U$:** Is $R_U(k)$ to be operationalized as raw user turn duration, normalized prosodic valence, inter-turn latency deviation, or multi-modal engagement index?
3. **Finite-Sample Power & Sample Size:** What minimum interaction sequence length $N$ is required to achieve parameter convergence under realistic human behavioral noise?
4. **Safety & Dyadic Integrity:** Can informative excitation be injected without degrading conversational naturalness or causing user fatigue?

---

## 5. Final Epistemic Decision

In accordance with strict research governance:

### **`FINAL DECISION: PROTOCOL CANDIDATE SELECTION NOT RATIFIED — SCIENTIFIC CORRECTIONS REQUIRED`**

### Definitive Boundary Interpretation:
$$\textbf{Design Space Mapped} \quad \ne \quad \textbf{Candidate Selected} \quad \ne \quad \textbf{Protocol Ratified} \quad \ne \quad \textbf{w}_{\text{fb}}\ \textbf{Identified} \quad \ne \quad \textbf{C2 Unblocked}$$

1. The Protocol Design Space remains **sufficiently mapped** ([`DOC-P25-012`](file:///c:/Users/Lunafiah/Desktop/My_project/Lucia/docs/PhaseDocs/Lucia-phase25-Temporal_Embodiment/P25_Q2_Q2-04_PROTOCOL_DESIGN_SPACE.md)).
2. The proposal to select and ratify the *Closed-Loop Extended IV Protocol* is **REJECTED AS PREMATURE AND METHODOLOGICALLY DEFECTIVE**.
3. Extended IV and HITL remain **strong candidates**, but are neither uniquely necessary nor ratified.
4. Condition C2 remains **strictly blocked and fail-fast** until a scientifically validated protocol specification is achieved.

---

## 6. Governance & Invariant Ledger

| Invariant / Rule | Status | Verification Detail |
|---|---|---|
| **Architecture Gate** | **`LOCKED`** | No ADR introduced; architecture unchanged |
| **Implementation Gate** | **`LOCKED`** | No production code modified; Phase 25 remains `PLANNED` |
| **Production Code Diff** | **`0 files changed`** | `git diff --stat -- src/ data/ electron/ config/` is empty |
| **Relational Vector $\mathbf{R}_t$** | **`CANONICAL (4D)`** | Unchanged in `src/core/relationship/state.py` |
| **Genesis Invariant (`INV-8`)** | **`BIT-EXACT`** | `data/profile.json` remains `{"is_onboarded": false}` |
| **Condition C2 Safety** | **`FAIL-FAST`** | `TBDGainUnestablishedError` active in `exp_p25_q2_1.py` |
| **Execution Lock** | **`ENFORCED`** | Zero experiment trials run; zero new outcome numbers |
| **Phase Scope** | **`PHASE 25 ONLY`** | No new numbered or official sub-phases created |

```text
[GOVERNANCE VERIFICATION: PASS]
All architectural gates remain locked. No production mutations. Epistemic integrity preserved.
```
