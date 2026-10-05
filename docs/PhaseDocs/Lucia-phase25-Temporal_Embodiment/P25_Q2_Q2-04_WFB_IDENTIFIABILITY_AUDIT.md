# P25-Q2: TBD-Q2-04 Scientific Identifiability Audit & Classification

> **DOCUMENT ID:** `DOC-P25-011`  
> **DOCUMENT TYPE:** RESEARCH SPECIFICATION / METHODOLOGICAL IDENTIFIABILITY AUDIT  
> **PHASE:** PHASE 25 — TEMPORAL EMBODIMENT & SOCIAL FEEDBACK  
> **RESEARCH HORIZON:** P25-Q2 (Reciprocal Social Feedback Dynamics)  
> **TARGET PROBLEM:** System Identifiability of Condition C2 Feedback Gain $w_{\text{fb}}$ (`TBD-Q2-04`)  
> **FINAL CLASSIFICATION:** **`PRACTICAL IDENTIFIABILITY PROBLEM`**  
> **EVALUATION VERDICT:** **`Q2-04 IDENTIFIABILITY CLASSIFICATION RATIFIED`**  
> **PARAMETER STATUS:** **`w_fb NOT IDENTIFIED / NOT CALIBRATED / NOT RATIFIED`**  
> **CONDITION C2 GATE:** **`STRICTLY BLOCKED / FAIL-FAST WITH TBDGainUnestablishedError`**  
> **ARCHITECTURE GATE:** **`LOCKED`** (No production mutation; zero ADRs)  
> **IMPLEMENTATION GATE:** **`LOCKED`** (Zero production diff; `src/`, `electron/`, `data/`, `config/` untouched)  
> **GENESIS INVARIANT (`INV-8`):** **`PRESERVED BIT-EXACT`** (`data/profile.json == {"is_onboarded": false}`)  
> **GOVERNANCE BOUNDARY:**  
> `Metric Ratified ≠ Identifiability Established`  
> `Identifiability Problem Classified ≠ w_fb Calibrated`  
> `w_fb Calibrated ≠ C2 Unblocked`  
> `Architecture Review Passed ≠ Rerun Authorized`

---

## 1. Executive Summary & Audit Context

This document provides the formal scientific audit, epistemic calibration, and classification ratification for the system identifiability of **`TBD-Q2-04`** (the Condition C2 feedback gain vector $\mathbf{w}_{\text{fb}}$) within the temporal embodiment architecture of Lucia Phase 25.

### 1.1 The Previous Epistemic Claim & Audit Need
In prior discussions, two polarized and methodologically flawed claims emerged:
1. *Extreme Claim 1:* "$\mathbf{w}_{\text{fb}}$ is structurally unidentifiable as currently formulated."  
   *Audit Finding:* **Structural non-identifiability was NOT proven.** There is no mathematical theorem showing that $o(k)$ and $R_U(k)$ must be linearly dependent under all informative observation regimes.
2. *Extreme Claim 2:* "$\operatorname{rank}(\boldsymbol{\Phi}) = 2$ almost surely because $R_U$ contains latency, nonlinearities, and stochasticity, establishing structural identifiability."  
   *Audit Finding:* **Overclaim.** Plausibility of independent variation is not an empirical or mathematical demonstration. No proof or empirical dataset has shown that $\operatorname{rank}(\boldsymbol{\Phi}) = 2$ holds stably for the actual C2 interaction model.

### 1.2 Ratified Epistemic Position
Following systematic control-theoretic analysis:
- **Correct Problem Classification:** **`B — PRACTICAL IDENTIFIABILITY PROBLEM`**.
- **Structural Identifiability Status:** **`PLAUSIBLE / NOT DEMONSTRATED`**.
- **Practical Identifiability Status:** **`PROBLEMATIC / HIGH CONFOUNDING RISK`**.
- **Empirical Identification of $w_{\text{fb}}$:** **`NOT ESTABLISHED`**.
- **Numerical Calibration:** **`NOT AUTHORIZED`**.
- **Condition C2 Execution:** **`STRICTLY BLOCKED / FAIL-FAST`**.

---

## 2. Structural vs. Practical Identifiability: Controlled Definitions

To prevent conceptual conflation, this audit establishes a rigorous demarcation between structural and practical identifiability in accordance with classical system identification theory:

```
┌────────────────────────────────────────────────────────────────────────┐
│               SYSTEM IDENTIFIABILITY TAXONOMY                          │
├──────────────────────────────────┬─────────────────────────────────────┤
│ STRUCTURAL IDENTIFIABILITY       │ PRACTICAL IDENTIFIABILITY           │
├──────────────────────────────────┼─────────────────────────────────────┤
│ Question:                        │ Question:                           │
│ Does there exist a unique        │ Given finite, noisy, collinear,     │
│ mapping from ideal, noise-free,  │ and band-limited observations under │
│ infinitely informative data to   │ operational excitation, can the     │
│ the parameter vector θ?          │ parameter be estimated stably?      │
│                                  │                                     │
│ Current Status for w_fb:         │ Current Status for w_fb:            │
│ PLAUSIBLE / NOT DEMONSTRATED     │ PROBLEMATIC / HIGH CONFOUNDING RISK │
└──────────────────────────────────┴─────────────────────────────────────┘
```

### 2.1 Structural Identifiability
- **Mathematical Condition:** Consider the parameter vector $\boldsymbol{\theta} = [w_{\text{obs}}, w_{\text{fb}}]^T \in \Theta$. A model structure is structurally globally identifiable if for almost all $\boldsymbol{\theta}^* \in \Theta$:
  $$y(k, \boldsymbol{\theta}) \equiv y(k, \boldsymbol{\theta}^*) \quad \forall k \implies \boldsymbol{\theta} = \boldsymbol{\theta}^*$$
- **C2 Formulation Status:** Plausible under an observed-input regressor formulation, because $R_U(k)$ is conceptually a delayed, baseline-subtracted signal that is not mathematically identical to direct observation $o(k)$. However, **it has NOT been demonstrated** for the actual closed-loop C2 interaction model.

### 2.2 Practical Identifiability
- **Mathematical Condition:** Even if structural identifiability is plausible, the Fisher Information Matrix (or regressor gramian) over a finite trial of length $N$:
  $$\mathbf{F}_N = \frac{1}{N} \boldsymbol{\Phi}^T \boldsymbol{\Phi} = \frac{1}{N} \sum_{k=1}^N \begin{bmatrix} o(k)^2 & o(k) R_U(k) \\ o(k) R_U(k) & R_U(k)^2 \end{bmatrix}$$
  may be severely ill-conditioned ($\kappa(\mathbf{F}_N) \gg 1$), dominated by observation noise, or degraded by high collinearity ($\operatorname{Corr}(o, R_U) \approx 1$).
- **C2 Formulation Status:** Severely compromised. In human conversational pacing under naturalistic scripts, conversational turns exhibit high mutual correlation and low persistent excitation, producing an acute practical identifiability bottleneck.

---

## 3. Audit of the Regressor Formulation & Separation Conditions

### 3.1 State Equation & Linear Regressor
In Condition C2, the discrete-time leaky integrator turn update is:
$$\mathbf{s}_{k+1} = (1 - \lambda)\mathbf{s}_k + \lambda \mathbf{x}_k^{(\text{C2})}$$
where $\mathbf{x}_k^{(\text{C2})} = w_{\text{obs}} \mathbf{o}_k + w_{\text{fb}} \mathbf{R}_U(k)$.

Rearranging for the effective driving input $y_k \equiv \frac{\mathbf{s}_{k+1} - (1 - \lambda)\mathbf{s}_k}{\lambda}$:
$$y_k = \begin{bmatrix} \mathbf{o}_k & \mathbf{R}_U(k) \end{bmatrix} \begin{bmatrix} w_{\text{obs}} \\ w_{\text{fb}} \end{bmatrix} = \boldsymbol{\phi}_k^T \boldsymbol{\theta}$$
Over $N$ interaction turns, the regressor matrix is:
$$\boldsymbol{\Phi} = \begin{bmatrix} \mathbf{o}_1 & \mathbf{R}_U(1) \\ \mathbf{o}_2 & \mathbf{R}_U(2) \\ \vdots & \vdots \\ \mathbf{o}_N & \mathbf{R}_U(N) \end{bmatrix} \in \mathbb{R}^{N \times 2}$$

### 3.2 Critical Correction on $\operatorname{rank}(\boldsymbol{\Phi})$
The claim that $\operatorname{rank}(\boldsymbol{\Phi}) = 2$ "almost surely" because $R_U$ incorporates latency and stochasticity is **REJECTED AS AN UNPROVEN OVERCLAIM**.

To maintain scientific integrity, the project distinguishes three tiers:
1. **Mathematical Condition (A):** $\operatorname{rank}(\boldsymbol{\Phi}) = 2$ requires linear independence of the column vectors $\mathbf{o} = [o_1, \dots, o_N]^T$ and $\mathbf{R}_U = [R_U(1), \dots, R_U(N)]^T$.
2. **Theoretical Plausibility (B):** Human communicative responses may introduce independent variation through processing latency, history dependence, prosodic nonlinearities, and motor stochasticity.
3. **Empirical / Model Demonstration (C):** Demonstrating that the specific operational definition:
   $$R_U(k) = \operatorname{clip}\left(\frac{U(t+\Delta) - U_{\text{baseline}}(t)}{\sigma_U}, -2.0, 2.0\right)$$
   yields $\operatorname{rank}(\boldsymbol{\Phi}) = 2$ with condition number $\kappa(\boldsymbol{\Phi}^T \boldsymbol{\Phi}) < \kappa_{\text{threshold}}$ under actual C2 turn sequences.

**Epistemic Verdict:** Tier C is **NOT DEMONSTRATED**.  
Therefore, the authoritative wording must be:
> *"Structural identifiability remains plausible under an observed-input formulation, but has not yet been demonstrated for the actual C2 interaction model."*

### 3.3 Necessary Conditions for Separating $w_{\text{obs}}$ and $w_{\text{fb}}$
Separating direct observation weight $w_{\text{obs}}$ from feedback gain $w_{\text{fb}}$ requires satisfying 10 formal conditions:

| # | Necessary Condition | Operational Meaning in Lucia C2 | Current Status |
|---|---|---|---|
| **1** | **Independent Variation** | $\mathbf{R}_U(k)$ must not be a deterministic scalar multiple of $\mathbf{o}_k$. | `PLAUSIBLE / UNPROVEN` |
| **2** | **Sufficient Temporal Diversity** | Pacing must span multiple frequency modes to excite both regressors. | `TBD / NOT ESTABLISHED` |
| **3** | **Observability** | Interlocutor response increment must be measurable above sensor noise floor. | `TBD / NOT ESTABLISHED` |
| **4** | **Bounded Noise Level** | Acoustic SNR must not drown out $R_U$ relative to direct turn duration. | `TBD / NOT ESTABLISHED` |
| **5** | **Low Collinearity** | Empirical correlation $|\operatorname{Corr}(o, R_U)| < 0.85$ over trial duration. | `TBD / HIGH RISK` |
| **6** | **Sufficient Observation Count** | $N$ must exceed asymptotic convergence sample size ($N \gg 40$). | `TBD / NOT ESTABLISHED` |
| **7** | **History Dependence** | Running baseline $U_{\text{baseline}}(t)$ must decouple fast response from drift. | `TBD / NOT ESTABLISHED` |
| **8** | **Actuator Linearity** | State coordinates must not saturate $\tau_L$ or $\Delta v_L$ during excitation. | `TBD / NOT ESTABLISHED` |
| **9** | **Delayed Response Window** | Response lag $\Delta \in [150, 800]\text{ ms}$ must cleanly isolate reactivity. | `RATIFIED SPEC (§4.2)` |
| **10** | **Measurement Precision** | Turn transition timestamps must maintain sub-10 ms accuracy. | `CANONICAL SPEC` |

Because empirical data to evaluate conditions 1–8 does not yet exist, they are formally recorded as **`TBD / NOT ESTABLISHED`**.

---

## 4. Audit of $w_{\text{obs}}$ & Unratified Design Assumptions

### 4.1 Prohibition on Re-adopting $w_{\text{obs}} = 1 - w_{\text{fb}}$
The relation $w_{\text{obs}} = 1 - w_{\text{fb}}$ was previously proposed as a convex combination to preserve input scale.

**Epistemic Re-affirmation:**
- This relation is **NOT** a canonical architectural requirement.
- It is **NOT** present in `EXP_P25_Q2_1_EVALUATION_SPECIFICATION.md`.
- It directly contradicts current harness code (`w_obs = np.array([0.7, 0.7, 0.7])`).
- It remains classified strictly as an:
  $$\mathbf{w}_{\text{obs}} = 1 - \mathbf{w}_{\text{fb}} \quad \Longrightarrow \quad \textbf{UNRATIFIED DESIGN ASSUMPTION}$$
- It must **NEVER** be used as a mathematical proof that $w_{\text{fb}}$ is identifiable or that the parameter space is 1-dimensional.

---

## 5. Audit of External Corpora (SEMAINE Corpus Review)

The SEMAINE (Sensitive Artificial Listener) corpus provides recorded human-agent interactions under multimodal affective dialogue.

### 5.1 Rejection of "Purely Passive / No Intervention" Characterization
Calling SEMAINE "purely passive" is incorrect:
- SEMAINE agents operate with four distinct conversational personas (Poppy = outgoing/happy, Prudence = pragmatic/sensible, Spike = angry/confrontational, Obadiah = depressive/sad).
- The deliberate switching of agent personas introduces structured behavioral variation and operating-regime contrast.

### 5.2 Prohibition on Overclaiming SEMAINE as a Causal Experiment for C2
However, treating SEMAINE persona-switching as a causal identification experiment for Lucia's C2 controller is **EQUALLY UNGROUNDED**:
- **Regime Variation $\ne$ Causal Intervention:** Persona switching provides macro-level emotional contrast; it does not perform controlled micro-timing perturbations on conversational turn latency.
- **Model Discrepancy:** SEMAINE dialogue does not instantiate Lucia's 3D leaky-integrator controller ($\lambda = 0.15$), nor does it measure Lucia's specific $R_U$ operationalization.
- **Verdict:** SEMAINE provides valuable **quasi-experimental observational contrast across behavioral regimes**, but **does NOT establish direct parameter identification of Lucia's $w_{\text{fb}}$**.

---

## 6. Audit of Dataset Availability Claims

Sweeping claims such as *"No dataset exists"* are scientifically imprecise and unverifiable.

### 6.1 Authoritative Bounded Formulation
The repository strictly adopts the bounded standard:
> *"No identified dataset currently establishes full C2 parameter identification under the present formulation without supplementary identification design."*

### 6.2 Candidate Dataset Evaluation Matrix
| Dataset | Primary Observables | Interactive Manipulation | Identifiability Capability for Lucia C2 |
|---|---|---|---|
| **SEMAINE** | Audio-visual turn timing, prosody, facial expression | Persona-induced macro conversational shift | Provides multi-regime contrast; does **not** identify micro-timing gain $w_{\text{fb}}$. |
| **Candor Corpus** | High-resolution dyadic audio turn latency | Naturalistic open-ended human conversation | Provides normative human latency variance ($\sigma \approx 150\text{ ms}$); lacks agent actuator coupling. |
| **Switchboard** | Telephonic multi-turn speech intervals | Natural telephone dialogues | Pacing distribution baseline; zero closed-loop robotic/agent feedback. |

**Synthesis:** External corpora provide normative human conversational baselines and operating contrast, but identifying $w_{\text{fb}}$ directly requires a dedicated interaction protocol.

---

## 7. Prohibition on Inventing Excitation / Heuristic Signals

Identifiability cannot be declared solved by introducing unratified perturbation mechanisms.

### Explicit Prohibitions:
1. **No Arbitrary Dither:** Injecting random Gaussian noise into latency to "force" $\operatorname{rank}(\boldsymbol{\Phi}) = 2$ is an unratified heuristic.
2. **No Arbitrary User Gain ($\beta_U$):** Hardcoding $\beta_U = 0.2$ in the harness creates an artificial in-vitro resonance.
3. **No Arbitrary Controller Switching:** Oscillating between C1 and C2 modes during a trial to create contrast is unratified.
4. **Classification Rule:** Any requirement for active excitation, deliberate timing dither, or perturbation design must be classified as a:
   $$\textbf{FUTURE IDENTIFICATION REQUIREMENT / RESEARCH QUESTION}$$
   and **NOT** as an established architectural requirement or ratified experimental baseline.

---

## 8. Epistemic Classification Ledger

The master classification of all identifiability and calibration items is ratified as follows:

| Item | Prior Flawed Claim | Audited & Ratified Status | Epistemic Category |
|---|---|---|---|
| **`TBD-Q2-04` Overall** | "Structural unidentifiability" | **`PRACTICAL IDENTIFIABILITY PROBLEM`** | **`RATIFIED CLASSIFICATION`** |
| **Structural Identifiability** | "rank($\Phi$) = 2 almost surely" | **`PLAUSIBLE / NOT DEMONSTRATED`** | **`THEORETICAL PLENARY`** |
| **Practical Identifiability** | Confounded with structural | **`PROBLEMATIC / HIGH CONFOUNDING RISK`** | **`IDENTIFICATION RISK`** |
| **Empirical $w_{\text{fb}}$ Value** | Attempted point selection | **`NOT IDENTIFIED / NOT CALIBRATED`** | **`BLOCKED PARAMETER`** |
| **$w_{\text{obs}} = 1 - w_{\text{fb}}$** | Claimed as mathematical fact | **`UNRATIFIED DESIGN ASSUMPTION`** | **`UNRATIFIED ASSUMPTION`** |
| **Condition C2 Execution** | Blocked under TBD | **`STRICTLY BLOCKED (FAIL-FAST)`** | **`ENFORCED INVARIANT`** |
| **Hypothesis $\mathcal{H}$-B** | "Rejected / Falsified" | **`BLOCKED / INCONCLUSIVE`** | **`PRESERVED HYPOTHESIS`** |
| **SEMAINE Dataset** | "Purely passive" vs "Identifies w_fb"| **`QUASI-EXPERIMENTAL CONTRAST ONLY`** | **`METHODOLOGICAL BOUNDARY`** |

---

## 9. Governance Boundaries & Non-Collapsible Gates

To prevent epistemic boundary creep, all agents and researchers must strictly adhere to the non-collapsible gate hierarchy:

```
[ Primary Metric Ratified (Q2-05) ]
              ≠
[ Identifiability Established ]
              ≠
[ Identifiability Problem Classified (Q2-04) ]
              ≠
[ Feedback Gain w_fb Calibrated ]
              ≠
[ Condition C2 Unblocked ]
              ≠
[ Pre-Rerun Architecture Review Passed ]
              ≠
[ EXP-P25-Q2.1 Rerun Authorized ]
              ≠
[ Hypothesis H-B Validated ]
```

No gate in this hierarchy may be bypassed, merged, or automatically triggered by the resolution of a prior gate.

---

## 10. Final Decision & Ratification

In accordance with strict post-Phase 24 research-first governance and the complete elimination of overclaims:

### **`FINAL DECISION: Q2-04 IDENTIFIABILITY CLASSIFICATION RATIFIED`**

### Operational Summary:
1. **Classification Ratified:** `TBD-Q2-04` is formally classified as a **Practical Identifiability Problem** (structural identifiability remains plausible but undemonstrated; practical estimation faces severe collinearity and confounding risks).
2. **Parameter Status:** $w_{\text{fb}}$ remains **`NOT IDENTIFIED`**, **`NOT CALIBRATED`**, and **`NOT RATIFIED`**.
3. **C2 Gate Enforced:** Condition C2 remains strictly **`BLOCKED / FAIL-FAST WITH TBDGainUnestablishedError`** in [`tests/evaluation/phase25/exp_p25_q2_1.py`](file:///c:/Users/Lunafiah/Desktop/My_project/Lucia/tests/evaluation/phase25/exp_p25_q2_1.py).
4. **Hypothesis Status:** $\mathcal{H}$-B remains **`BLOCKED / INCONCLUSIVE`**.
5. **No Experiments Executed:** Zero trials run; zero new outcome numbers generated.
6. **No Production Modifications:** Production code (`src/`, `electron/`, `data/`, `config/`) diff is strictly **`0 files`**.
7. **Genesis Invariant Preserved:** [`data/profile.json`](file:///c:/Users/Lunafiah/Desktop/My_project/Lucia/data/profile.json) is bit-exact (`{"is_onboarded": false}`).
8. **Phase Horizon:** Phase 25 remains **`PLANNED`**.
