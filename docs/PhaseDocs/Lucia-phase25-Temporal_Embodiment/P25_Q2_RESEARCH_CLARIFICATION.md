# P25: Research Clarification Pass After Q2-04 Closure

> **DOCUMENT ID:** `DOC-P25-010`  
> **DOCUMENT TYPE:** RESEARCH SPECIFICATION / METHODOLOGICAL CLARIFICATION  
> **PHASE:** PHASE 25 — TEMPORAL EMBODIMENT & SOCIAL FEEDBACK  
> **RESEARCH HORIZON:** P25-Q2 (Reciprocal Social Feedback Dynamics)  
> **STATUS:** **`NEXT RESEARCH QUESTION IDENTIFIED`**  
> **CONDITION C2 STATUS:** **`STRICTLY BLOCKED / FAIL-FAST WITH TBDGainUnestablishedError`**  
> **ARCHITECTURE GATE:** **`LOCKED`** (No production mutation; zero ADRs)  
> **IMPLEMENTATION GATE:** **`LOCKED`** (Zero production diff; `src/`, `electron/`, `data/`, `config/` untouched)  
> **GENESIS INVARIANT (`INV-8`):** **`PRESERVED BIT-EXACT`** (`data/profile.json == {"is_onboarded": false}`)  
> **GOVERNANCE DISCIPLINE:** `Research Clarification ≠ Experiment Authorization ≠ Architecture Approval ≠ Implementation Authorization`

---

## 1. Scope & Purpose

This document provides a formal **research clarification pass** following the methodological audit and closure of **`TBD-Q2-04`** in [`P25_Q2_Q2-04_WFB_CALIBRATION.md`](file:///c:/Users/Lunafiah/Desktop/My_project/Lucia/docs/PhaseDocs/Lucia-phase25-Temporal_Embodiment/P25_Q2_Q2-04_WFB_CALIBRATION.md) (`DOC-P25-009`).

The objective is to:
1. Formally close the current `P25-Q2.1` investigative increment epistemically, preventing an endless cycle of attempting to invent or force an uncalibrated feedback gain $w_{\text{fb}}$ merely to permit Condition C2 to run.
2. Identify the **actual, fundamental scientific bottleneck** in the causal dependency chain required to evaluate reciprocal temporal embodiment.
3. Determine whether the synthetic user fixture is fundamentally open-loop and whether an interactive user model is required.
4. Formulate the **minimum necessary next research question** strictly within the authorized scope of Phase 25.
5. Prevent premature experiment design, ungrounded threshold authoring, or unauthorized sub-phase creation.

---

## 2. Q2.1 Epistemic Closure Status

The investigative increment designated as `EXP-P25-Q2.1` is formally closed under the following ratified statuses:

```
┌────────────────────────────────────────────────────────────────────────┐
│                        Q2.1 CLOSURE LEDGER                             │
├───────────────────┬────────────────────────────────────────────────────┤
│ Q2-05             │ RATIFIED: Primary coupling statistic r₁            │
│                   │ (Not experimentally validated; rerun unauthorized) │
├───────────────────┼────────────────────────────────────────────────────┤
│ Q2-04             │ REMAINS OPEN: Gain w_fb uncalibrated               │
│                   │ (Literature [0.10, 0.25] = provisional candidate)  │
├───────────────────┼────────────────────────────────────────────────────┤
│ Hypothesis H-B    │ BLOCKED / INCONCLUSIVE (Not rejected, not proven)  │
├───────────────────┼────────────────────────────────────────────────────┤
│ Condition C2      │ BLOCKED / FAIL-FAST (TBDGainUnestablishedError)    │
├───────────────────┼────────────────────────────────────────────────────┤
│ Experiment Run    │ NOT EXECUTED (Zero new outcome numbers generated)  │
├───────────────────┼────────────────────────────────────────────────────┤
│ Production Diff   │ ZERO (0 files modified under src/, electron/, etc) │
└───────────────────┴────────────────────────────────────────────────────┘
```

### 2.1 Metric Ratification Preservation (`Q2-05`)
- **Status:** **`RATIFIED`**
- **Definition:** Lagged turn-taking cross-correlation $r_1 = \operatorname{Corr}\big(g_{UL}(k), \; g_{LU}(k-1)\big)$ is established as the primary coupling statistic over Transfer Entropy.
- **Empirical Boundary:** Ratification is methodological; the metric has **not** been experimentally validated in a certified rerun, because the rerun has not been authorized.

### 2.2 Calibration Parameter Status (`Q2-04`)
- **Status:** **`REMAINS OPEN`**
- **State:** No outcome-independent point value for $w_{\text{fb}}$ exists. The interval $[0.10, 0.25]$ is a provisional literature candidate, the mapping $\alpha_{\text{SMS}} \to w_{\text{fb}}$ is not established, and $w_{\text{obs}} = 1 - w_{\text{fb}}$ is an unratified design assumption.
- **Enforcement:** Condition C2 remains fail-fast with `TBDGainUnestablishedError`.

### 2.3 Hypothesis Status (`H-B`)
- **Status:** **`BLOCKED / INCONCLUSIVE — TBD-Q2-04`**
- **Epistemic Rule:** $\mathcal{H}$-B (Reciprocal Incrementality) must **never** be labeled as "falsified" or "rejected" merely because Condition C2 was unable to execute due to uncalibrated gain. It remains strictly inconclusive.

---

## 3. Confirmed Findings & Established Baseline

Through the Q2.1 evaluation and subsequent audits, the following scientific facts are confirmed:

1. **Unilateral Baseline (C1) Functionality:** Condition C1 operates cleanly as a deterministic leaky-integrator tracker ($\lambda = 0.15$) adapting Lucia's speech tempo ($\Delta v_L$) and response latency ($\tau_L$) to measured incoming user features.
2. **Transfer Entropy Metric Demotion:** Directed Transfer Entropy ($\text{TE}_{U\to L}, \text{TE}_{L\to U}$) and net asymmetry ($\Delta\text{TE}_{\text{net}}$) are directional diagnostic indicators, not coupling-sensitive synchrony metrics for short turn series ($N \approx 40$).
3. **Surrogate Null Methodology:** The historical arithmetic-mean gap surrogate was invalid. Valid surrogate construction requires ordered cross-session pairing of interlocutor streams under a matched collaborative script ($N \ge 100$ realizations, upper-tail exceedance against $\theta_{95}$ reference).
4. **Controller Scale Separation:** In C1, $w_{\text{obs}} = 1.0$. In C2, the observation weight $w_{\text{obs}}$ and feedback gain $w_{\text{fb}}$ must be explicitly reconciled with C1 before comparative testing can be valid.

---

## 4. Invalidated Assumptions & Discredited Hypotheses

The Q2.1 line of inquiry falsified or discredited several premature assumptions:

| Prior Assumption | Audit Outcome | Scientific Reason |
|---|---|---|
| **Arithmetic Gap Surrogate** | **`INVALIDATED / DISCREDITED`** | Arithmetic mean of uncoupled pauses created an artificial floor confounded with session variance. |
| **Direct Literature Mapping ($\alpha \to w_{\text{fb}}$)** | **`NOT ESTABLISHED`** | Periodic tapping phase correction cannot be equated to a 3D aperiodic conversational leaky integrator. |
| **Mathematical Derivation of $w_{\text{obs}} = 1 - w_{\text{fb}}$** | **`UNRATIFIED DESIGN ASSUMPTION`** | Not derived from architecture or spec; directly contradicts current harness code ($w_{\text{obs}} = 0.7$). |
| **C1 Continuity Under Current C2 Code** | **`DISPROVEN`** | Current C2 code hardcodes $w_{\text{obs}} = 0.7$, so $\lim_{w_{\text{fb}}\to 0} \mathbf{x}^{(\text{C2})} \ne \mathbf{x}^{(\text{C1})}$. |
| **Universal Headroom Preservation Across $[0, 1]$** | **`NOT ESTABLISHED`** | Steady-state boundedness does not guarantee transient non-saturation under perturbation. |
| **Selecting $w_{\text{fb}}$ via Future Grid Search** | **`PROHIBITED AS CIRCULAR`** | Tuning a gain to maximize synchrony outcomes converts hypothesis testing into post-hoc parameter fitting. |

---

## 5. Current Blockers

Two distinct blockers currently prevent meaningful testing of reciprocal feedback:

```
┌────────────────────────────────────────────────────────────────────────┐
│                      CURRENT BLOCKER TAXONOMY                          │
├──────────────────────────────────┬─────────────────────────────────────┤
│ LOCAL BLOCKER:                   │ SYSTEMIC BLOCKER:                   │
│ TBD-Q2-04 (Gain w_fb)            │ Open-Loop Synthetic User Fixture    │
│                                  │                                     │
│ No justified scalar point value  │ The synthetic user never responds   │
│ exists for w_fb.                 │ to Lucia's preceding actions.       │
│ Controller fails fast.           │ Loop Lucia -> User -> Lucia is open.│
└──────────────────────────────────┴─────────────────────────────────────┘
```

The calibration audit in `P25_Q2_Q2-04_WFB_CALIBRATION.md` revealed that **the local blocker (`TBD-Q2-04`) cannot be resolved in isolation because it is downstream of the systemic blocker**. Attempting to tune $w_{\text{fb}}$ without an interlocutor who actually reacts to Lucia is mathematically circular.

---

## 6. Dependency Graph for Meaningful H-B Evaluation

The causal loop required for a scientifically meaningful test of reciprocal temporal embodiment ($\mathcal{H}$-B) has a strict topological dependency:

```
[1. Actuator Dynamics]
      │  (Latency τ_L, Tempo Δv_L)
      ▼
[2. Lucia Actuation B_L(t)]
      │
      ▼  MISSING FORWARD LINK:
======│=====================================================================
      │  How does Lucia's action measurably modulate the user?
      ▼  (Currently OPEN-LOOP in synthetic harness)
[3. User Response U(t+Δ)]
============================================================================
      │
      ▼  (Extracted via UserResponseSignalExtractor)
[4. Response Increment R_U(t+Δ)]
      │
      ▼  REQUIRES USER COUPLING MAGNITUDE:
      │  Feedback gain w_fb cannot be calibrated without knowing user responsiveness
[5. Calibrated Feedback Gain w_fb]
      │
      ▼
[6. C2 Closed-Loop State Update s_{t+2Δ}]
      │
      ▼
[7. Dynamic Trajectory g_UL(k), g_LU(k)]
      │
      ▼
[8. Ratified Dyadic Coupling Metric r₁]
      │
      ▼
[9. Cross-Session Surrogate Null Reference θ₉₅]
      │
      ▼
[10. Statistical Hypothesis Decision on H-B]
```

### Analysis of the Dependency Chain
- **Steps 7–10 (Evaluation & Inference):** Fully ratified conceptually (Metric $r_1$, Surrogate Null, Exceedance test).
- **Steps 1 & 6 (Actuators & State Update):** Fully specified mathematically, pending resolution of $w_{\text{obs}}$ matching.
- **Step 5 (Feedback Gain $w_{\text{fb}}$):** Blocked because it is downstream of Steps 2–4.
- **Step 3 (User Response Link):** **`COMPLETELY MISSING / OPEN CIRCUIT`**.

In the current harness (`exp_p25_q2_1.py:188-223`), `FixtureGenerator.generate_script(seed)` creates the user's turns, durations, and pauses statically using an Ornstein-Uhlenbeck process before the session starts. **The user's actions at $t+\Delta$ are statistically independent of Lucia's actions at $t$.**

---

## 7. Open Methodological Questions: Synthetic User Dilemma

The realization that the current synthetic user is open-loop raises a fundamental methodological question:

### Option A: Harness-Internal Synthetic Coupling
- **Concept:** Add a simple coupling equation directly inside the test harness fixture:
  $$\tau_{\text{pause},\text{user}}(k) = \text{base\_pause} + \beta_U \big(\tau_L(k-1) - 400.0\big) + \epsilon_k$$
- **Methodological Evaluation:**
  - If an engineer introduces $\beta_U = 0.2$ in the harness, where does $0.2$ come from? It is an ungrounded assumption.
  - If Lucia's controller is then tuned to track this synthetic user ($w_{\text{fb}} = 0.2$), the harness merely tests two synthetic algorithms co-designed to resonate in the same script.
  - **Verdict:** Option A produces an **in-vitro circular artifact**. It demonstrates that two coupled Python functions couple, but provides zero scientific evidence regarding Lucia's capacity for embodied social attunement with a human interlocutor.

### Option B: Separately Validated Interactive User Model or Live Human Protocol
- **Concept:** Recognize that testing reciprocal embodiment requires either:
  1. An interactive user response model whose coupling parameters are empirically derived from human conversational data, OR
  2. A live human-in-the-loop evaluation protocol where human reactive timing provides genuine, un-simulated closed-loop feedback.
- **Methodological Evaluation:**
  - Scientifically defensible and free from circular self-validation.
  - Requires explicit research into human conversational entrainment parameters in Lucia's operational environment before claiming $\mathcal{H}$-B validation.
  - **Verdict:** Option B is the **only methodologically sound path** under research-first governance.

---

## 8. Candidate Next Research Questions

Inside the authorized scope of Phase 25 (Temporal Embodiment & Social Feedback), three candidate research directions exist:

### Candidate 1: Controller Reconciliation Study
- *Question:* "How should the observation weight $w_{\text{obs}}$, alignment operator $\mathcal{F}(R_U, B_L)$, and feedback gain $w_{\text{fb}}$ be formally formulated in the C2 controller specification to guarantee mathematical continuity with C1 ($\lim_{w_{\text{fb}}\to 0} \mathbf{x}^{(\text{C2})} \equiv \mathbf{x}^{(\text{C1})}$) and provable transient stability?"
- *Scope:* Pure control-theoretic and architectural specification.
- *Evidence:* Resolves Harness Defect 1 ($w_{\text{obs}} = 0.7$) and unratified convex assumption ($w_{\text{obs}} = 1 - w_{\text{fb}}$).

### Candidate 2: Forward Causal Coupling & Interactive User Modeling
- *Question:* "What empirical relationship characterizes human conversational cadence adjustment in response to agent response-latency shifts ($\text{Lucia}(t) \to \text{User}(t+\Delta)$), and what is the minimum validated model required to simulate this interaction without circularity?"
- *Scope:* Psycholinguistic / human-interaction empirical calibration.
- *Evidence:* Solves the open-loop fixture bottleneck identified in Section 6.

### Candidate 3: Multi-Session Persistence Protocol (P3 / $\mathcal{H}$-C)
- *Question:* "How does conversational attunement decay or persist across discrete session boundaries and resting Philia relaxation?"
- *Scope:* Long-horizon relational dynamics.
- *Evidence:* Untested, but depends entirely on having a functional intra-session coupling loop first.

---

## 9. Evaluation of Candidates & Bottleneck Identification

| Candidate | Solves Root Bottleneck? | Depends on Unresolved Items? | Risk of Circularity? | Priority Rank |
|---|---|---|---|---|
| **Candidate 1 (Controller Spec)** | Partially (Structural only) | No | Low | Secondary |
| **Candidate 2 (Forward Coupling)** | **YES (Causal loop closure)** | No | Low (if empirically grounded) | **PRIMARY** |
| **Candidate 3 (Persistence P3)** | No (Premature) | Yes (Depends on C2 loop) | High | Tertiary |

### The Root Bottleneck
Candidate 1 (controller reconciliation) is necessary, but trivial: setting $\mathbf{w}_{\text{obs}} = (1 - w_{\text{fb}})\mathbf{1}$ in the specification can be done analytically. However, even with a reconciled controller, **C2 cannot be evaluated without Candidate 2**.

Without a responsive interlocutor:
$$\text{Lucia}(t) \xrightarrow{\Delta} \text{User}(t+\Delta)$$
does not exist. Condition C2 remains an echo chamber feeding back user noise.

---

## 10. Minimum Necessary Next Research Question

Based on the evidence, the smallest next research question necessary to unblock reciprocal temporal embodiment research in Phase 25 is:

```text
===============================================================================
                    MINIMUM NECESSARY NEXT RESEARCH QUESTION
===============================================================================

"Under what operational model or empirical interaction protocol can the 
 forward causal link Lucia(t) → User(t+Δ) be instantiated such that user 
 behavioral responses are measurably conditioned on Lucia's preceding 
 expressive output, thereby providing an independent, non-circular basis 
 for calibrating closed-loop feedback in Condition C2?"

===============================================================================
```

---

## 11. Questions That Must NOT Yet Be Answered

To maintain strict epistemic hygiene, researchers and agents are explicitly prohibited from addressing the following questions at this stage:

1. **Do NOT ask: "What numerical value of $w_{\text{fb}}$ should we pick?"**  
   *(Gain cannot be chosen before the interlocutor's coupling gain is established.)*
2. **Do NOT ask: "What value of $\beta_U$ should we hardcode in the harness?"**  
   *(Inventing a synthetic coupling constant produces a circular self-fulfilling simulation.)*
3. **Do NOT ask: "Does C2 outperform C1 on $r_1$ or recovery?"**  
   *(C2 is blocked; asking comparative performance questions is premature.)*
4. **Do NOT ask: "How should Phase 26 preferences be structured?"**  
   *(Phase 26 is a future horizon dependent on Phase 25 resolution.)*
5. **Do NOT author a new experimental rerun protocol or execution script.**

---

## 12. Governance & Isolation Status

- **Phase 25 Status:** `PLANNED` (Active Future Horizon).
- **Sub-Inquiry P25-Q1:** `RESEARCH COMPLETE / ARCHIVED AS EVIDENCE`.
- **Sub-Inquiry P25-Q2.1:** `EVALUATION HARNESS AUDITED / Q2-05 RATIFIED / Q2-04 OPEN / HARNESS DISPOSITION CLOSED`.
- **Condition C2:** `STRICTLY BLOCKED / FAIL-FAST WITH TBDGainUnestablishedError`.
- **Architecture Gate:** `LOCKED` (No ADR authorized or adopted).
- **Implementation Gate:** `LOCKED` (Production diff = 0 files changed).
- **Genesis Onboarding (`INV-8`):** `BIT-EXACT` (`data/profile.json == {"is_onboarded": false}`).

---

## 13. Final Decision

In accordance with the evidence and required decision taxonomy:

### **`FINAL DECISION: NEXT RESEARCH QUESTION IDENTIFIED`**

### Summary of Rationale:
The evidence across Q2.1 evaluation audits demonstrated that attempting to calibrate the C2 feedback gain vector $w_{\text{fb}}$ in a vacuum is an ill-posed problem. The true blocker is the absence of the forward causal link $\text{Lucia}(t) \to \text{User}(t+\Delta)$ in the evaluation fixture. The minimum necessary research question is formally identified in Section 10. Condition C2 remains blocked until that question is addressed.
