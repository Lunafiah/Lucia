# P25-Q2: TBD-Q2-04 Feedback Gain ($w_{\text{fb}}$) Scientific Calibration & Ratification Analysis

> **DOCUMENT ID:** `DOC-P25-009`  
> **DOCUMENT TYPE:** RESEARCH SPECIFICATION / PARAMETER CALIBRATION AUDIT  
> **PHASE:** PHASE 25 — TEMPORAL EMBODIMENT & SOCIAL FEEDBACK  
> **RESEARCH QUESTION:** P25-Q2 (Reciprocal Social Feedback & Temporal Embodiment Dynamics)  
> **TARGET PARAMETER:** `TBD-Q2-04` — Condition C2 Closed-Loop Feedback Gain Vector $\mathbf{w}_{\text{fb}}$  
> **FINAL DISPOSITION:** **`Q2-04 REMAINS OPEN`**  
> **C2 EXECUTION GATE:** **`STRICTLY BLOCKED / FAIL-FAST WITH TBDGainUnestablishedError`**  
> **ARCHITECTURE GATE:** **`LOCKED`** (No production mutation; no ADR authored)  
> **IMPLEMENTATION GATE:** **`LOCKED`** (Zero production code diff; `src/`, `electron/`, `data/`, `config/` untouched)  
> **GENESIS INVARIANT (`INV-8`):** **`PRESERVED BIT-EXACT`** (`data/profile.json == {"is_onboarded": false}`)  
> **GOVERNANCE DISCIPLINE:** `Q2-04 Evaluated ≠ Rerun Authorized ≠ Experiment Executed ≠ H-B Validated`

---

## 1. Executive Summary & Epistemic Verdict

This document provides the corrected and tightened scientific calibration analysis for **`TBD-Q2-04`**—the determination of the bidirectional feedback gain vector $\mathbf{w}_{\text{fb}}$ governing experimental **Condition C2** in `EXP-P25-Q2.1`.

Following architectural review, this revised document explicitly audits the epistemic validity of all mathematical, physical, and literature claims. It enforces strict epistemic taxonomy so that design heuristics, analogies, and unratified assumptions are never mischaracterized as proven mathematical consequences or established physical facts.

### Primary Epistemic Distinctions
Under post-Phase 24 research-first governance:
```text
Literature Candidate Range [0.10, 0.25]
    ≠ Validated Admissible Range
    ≠ Calibrated Point Value
    ≠ Experimental Sensitivity Grid
```

### Core Audit Outcomes
1. **`[0.10, 0.25]` Reclassified:** The interval $[0.10, 0.25]$ is strictly a **`PROVISIONAL / LITERATURE-INFORMED CANDIDATE RANGE — NOT RATIFIED`**. It is not a mathematically proven envelope, not a physically established bound for Lucia, and not a ratified admissible range.
2. **Literature Mapping ($\alpha \to w_{\text{fb}}$) Marked `NOT ESTABLISHED`:** Sensorimotor synchronization (SMS) phase correction literature models cycle-by-cycle inter-tap timing errors in periodic tasks, which cannot be assumed mathematically or topologically equivalent to Lucia's 3D aperiodic conversational leaky-integrator controller.
3. **`w_obs = 1 - w_fb` Classified as `UNRATIFIED DESIGN ASSUMPTION`:** This convex combination constraint is a proposed design choice; it does not exist in the ratified evaluation specification and contradicts the current harness implementation (`w_obs = 0.7`).
4. **C1 Continuity Claim Disproven Under Current Code:** Because current C1 uses $w_{\text{obs}} = 1.0$ while current C2 hardcodes $w_{\text{obs}} = 0.7$, $\lim_{w_{\text{fb}} \to 0} \mathbf{x}^{(\text{C2})} \ne \mathbf{x}^{(\text{C1})}$. Continuity does not follow from existing code/spec.
5. **`w_fb < 0.50` Downgraded:** The bound $w_{\text{fb}} < 0.50$ is strictly conditional on the unratified $w_{\text{obs}} = 1 - w_{\text{fb}}$ assumption, not an independent constraint.
6. **Actuator Headroom Across $[0, 1]$ Marked `NOT ESTABLISHED`:** Bounded steady-state input does not formally establish transient stability or dynamic headroom under turn perturbations.
7. **Sensitivity Analysis Strictly Decoupled from Calibration:** Future grid evaluation cannot be used to select $w_{\text{fb}}$ post-hoc based on outcome metrics ($r_1$, $\text{TE}$, recovery).
8. **Final Disposition:** **`Q2-04 REMAINS OPEN`** and Condition C2 remains fail-fast blocked with `TBDGainUnestablishedError`.

---

## 2. Epistemic Classification Standard

Every numerical parameter, bound, and mapping cited in this document is explicitly classified according to the following controlled taxonomy:

| Classification | Operational Meaning in Lucia Research |
|---|---|
| **`CANONICAL / ALREADY RATIFIED`** | Existing production constant or formally ratified specification requirement. |
| **`DERIVED FROM CURRENT EQUATIONS`** | Mathematically proven from existing code/spec without auxiliary assumptions. |
| **`SOURCE-SUPPORTED`** | Empirically documented in external literature, but not proven for Lucia's architecture. |
| **`PROVISIONAL / CANDIDATE`** | Plausible candidate value/range staged for investigation; unvalidated. |
| **`UNRATIFIED DESIGN ASSUMPTION`** | A new design proposal introduced during analysis, not yet adopted in architecture. |
| **`NOT ESTABLISHED`** | A claimed relation, equivalence, or bound that lacks formal mathematical or empirical proof. |
| **`FUTURE TBD`** | An acknowledged open parameter deferred to a future research specification. |

---

## 3. Exact Parameter Semantics & State-Space Modulation

To evaluate calibration bases rigorously, the exact mathematical role of $\mathbf{w}_{\text{fb}}$ within Lucia's temporal embodiment controller must be defined without ambiguity.

```
Incoming Turn t + Δ:
  User Feature U(t + Δ) ───────────┐
                                   ▼
                            [ Normalizer ] ──> o_k ∈ [-2, 2]³
                                   │
                                   ▼
                      [ Response Extractor ] ──> R_U(k) ∈ [-2, 2]³
                                   │
                                   ▼
                     Coupled Input Construction:
                     x_k = w_obs ⊙ o_k + w_fb ⊙ R_U(k)
                                   │
                                   ▼
                     Leaky Integrator State:
                     s_{k+1} = (1 - λ) s_k + λ x_k
                                   │
                                   ▼
                            Actuator Policy:
               ┌───────────────────┴───────────────────┐
               ▼                                       ▼
      Response Latency τ_L                    Speech Tempo Δv_L
  τ_L = 400 + s_k[2] * 40 ms             Δv_L = clip(s_k[1] * 0.05, ±0.15)
```

### 3.1 State-Space Representation
The controller is a 3-dimensional discrete-time leaky integrator operating at conversational turn boundary $k$:
$$\mathbf{s}_{k+1} = (1 - \lambda)\mathbf{s}_k + \lambda \mathbf{x}_k$$
- **Coordinates:** $\mathbf{s}_k = [s_k^{(0)}, s_k^{(1)}, s_k^{(2)}]^T \in \mathbb{R}^3$, representing normalized fundamental frequency ($f_0$), speech envelope energy, and pause latency cadence.
- **Leakage Parameter:** $\lambda = 0.15$ (`CANONICAL / ALREADY RATIFIED` in `EXP_P25_Q2_1_EVALUATION_SPECIFICATION.md` §3), establishing an effective discrete filter memory horizon of $\tau = 1/\lambda \approx 6.67$ turns.

### 3.2 Input Vector Composition in Condition C2
In Condition C2, the driving input vector $\mathbf{x}_k^{(\text{C2})}$ combines incoming user observation with the feedback increment:
$$\mathbf{x}_k^{(\text{C2})} = \mathbf{w}_{\text{obs}} \odot \mathbf{o}_k + \mathbf{w}_{\text{fb}} \odot \mathbf{R}_U(k)$$
- **Observation Vector ($\mathbf{o}_k$):** Normalized user turn features clamped to $[-2.0, +2.0]^3$ (`CANONICAL / ALREADY RATIFIED`):
  $$o_k^{(0)} = \frac{f_{0,\text{user}} - 180.0}{40.0}, \quad o_k^{(1)} = \frac{\text{env}_{\text{user}} - 0.65}{0.20}, \quad o_k^{(2)} = \frac{\tau_{\text{pause},\text{user}} - 400.0}{150.0}$$
- **User Response Increment ($\mathbf{R}_U(k)$):** Normalized deviation from running baseline clamped to $[-2.0, +2.0]^3$ (`CANONICAL / ALREADY RATIFIED`):
  $$\mathbf{R}_U(k) = \text{clip}\left(\frac{\mathbf{U}(k) - \mathbf{U}_{\text{baseline}}(k)}{\boldsymbol{\sigma}_U(k)}, -2.0, +2.0\right)$$
- **Observation Weight ($\mathbf{w}_{\text{obs}}$):** Direct sensory observation gain.
- **Feedback Gain ($\mathbf{w}_{\text{fb}}$):** Scaling gain governing user response feedback (`TBD-Q2-04`).

### 3.3 Actuator Mapping
Internal state coordinates map into physical expressive parameters:
1. **Response Latency ($\tau_L$):**
   $$\tau_L(k) = \text{clip}\big(400.0 + (s_k^{(2)} \times 40.0) + \delta_{\text{pert}}(k), \; 0.0, \; 1000.0\big)\text{ ms}$$
   where $\delta_{\text{pert}}(k) = +300.0\text{ ms}$ exclusively at turn $k = 18$ (`CANONICAL / ALREADY RATIFIED`).
2. **Speech Tempo Adjustment ($\Delta v_L$):**
   $$\Delta v_L(k) = \text{clip}\big(s_k^{(1)} \times 0.05, \; -0.15, \; +0.15\big)$$
   clamped to $[-0.15, +0.15]$ (`CANONICAL / ALREADY RATIFIED`).

---

## 4. Audit of C1/C2 Implementation & Specification Semantics

### 4.1 Specification vs Harness Implementation Audit
A rigorous comparison between `EXP_P25_Q2_1_EVALUATION_SPECIFICATION.md` §4.4 and `tests/evaluation/phase25/exp_p25_q2_1.py` reveals critical discrepancies:

| Property | Ratified Specification (§4.4) | Current Harness Code (`exp_p25_q2_1.py`) | Epistemic Status |
|---|---|---|---|
| **C1 State Update** | $\mathbf{s}_{k+1} = (1-\lambda)\mathbf{s}_k + \lambda \mathbf{o}_k$ | $\mathbf{s}_{k+1} = (1-0.15)\mathbf{s}_k + 0.15 \cdot \mathbf{o}_k$ | `MATCHED` ($w_{\text{obs}}^{(\text{C1})} = 1.0$) |
| **C2 State Update** | $\mathbf{x}_k = \mathbf{w}_{\text{obs}} \odot \mathbf{o}_k + \mathbf{w}_{\text{fb}} \odot \mathcal{F}(R_U, B_L)$ | $\mathbf{x}_k = \mathbf{w}_{\text{obs}} \odot \mathbf{o}_k + \mathbf{w}_{\text{fb}} \odot \mathbf{R}_U$ | `DISCREPANCY` ($\mathcal{F}$ omitted) |
| **C2 $w_{\text{obs}}$ Weight** | Unspecified vector $\mathbf{w}_{\text{obs}}$ | Hardcoded static `np.array([0.7, 0.7, 0.7])` | `UNRATIFIED CODE CONSTANT` |
| **C2 $w_{\text{fb}}$ Gain** | Locked as `TBD-Q2-04` | Raises `TBDGainUnestablishedError` if `None` | `MATCHED` (Fail-Fast Guard active) |

### 4.2 Rechecking the C1 Continuity Claim: `lim(w_fb -> 0) x_C2 = x_C1`
The prior calibration report argued that $\lim_{w_{\text{fb}} \to 0} \mathbf{x}_k^{(\text{C2})} = \mathbf{x}_k^{(\text{C1})}$ mathematically justifies setting $w_{\text{obs}} = 1 - w_{\text{fb}}$.

**Rigorous Audit:**
1. In the actual current harness code (`exp_p25_q2_1.py:322`):
   $$\mathbf{w}_{\text{obs}}^{(\text{C2})} = [0.7, 0.7, 0.7]^T, \quad \mathbf{w}_{\text{obs}}^{(\text{C1})} = [1.0, 1.0, 1.0]^T$$
2. If $w_{\text{fb}} \to 0$ in the current C2 controller:
   $$\lim_{\mathbf{w}_{\text{fb}} \to \mathbf{0}} \mathbf{x}_k^{(\text{C2})} = [0.7, 0.7, 0.7]^T \odot \mathbf{o}_k \ne \mathbf{o}_k = \mathbf{x}_k^{(\text{C1})}$$
3. Therefore, C1 continuity does **NOT** follow from the current implementation or specification.
4. Setting $w_{\text{obs}} = 1 - w_{\text{fb}}$ is **NOT** a mathematical consequence of the existing system; it is a **`NEW UNRATIFIED DESIGN ASSUMPTION`** that would require modifying C2 code.
5. In accordance with governance constraints, agents must **NOT** silently modify C1 or C2 to make the equations agree. This discrepancy is formally recorded as an unresolved specification issue.

---

## 5. Audit of Candidate Independent Calibration Bases

### 5.1 Audit of the Literature Mapping: $\alpha_{\text{SMS}} \to w_{\text{fb}}$
The prior draft imported $\alpha \in [0.10, 0.25]$ from sensorimotor synchronization (SMS) literature (e.g., Repp & Keller 2004; Vorberg & Wing 1996) and mapped it directly to Lucia's $w_{\text{fb}}$.

**Structural Equivalence Audit:**
- **Mathematical Role:** In SMS models, $\alpha$ is a cycle-by-cycle phase correction fraction in linear interval map: $t_{n+1} - t_n = T - \alpha e_n + \epsilon_n$, where $e_n$ is the millisecond asynchrony between tap and metronome. In Lucia, $w_{\text{fb}}$ is a spatial mixing gain in a 3D coupled vector input driving a continuous-time-equivalent leaky integrator.
- **Feedback Topology:** SMS literature models periodic sensorimotor synchronization with instantaneous acoustic feedback per cycle. Lucia operates over conversational turn boundaries with variable duration (1.5–5.0 s), pause latency, and aperiodic turn transitions.
- **Normalization:** SMS $\alpha$ operates directly on raw millisecond timing errors. Lucia's $\mathbf{R}_U(k)$ is a dimensionless z-score normalized by running moving-average standard deviation $\sigma_U$ and clipped to $[-2.0, +2.0]$.
- **State Update Semantics:** Classical SMS phase correction models maintain zero hidden dynamical state (pure autoregressive phase adjustment). Lucia maintains a 3D leaky integrator state $\mathbf{s}_k$ with filter pole $1-\lambda = 0.85$.
- **Dimensional Meaning:** SMS $\alpha$ is a 1D scalar for timing. Lucia's $\mathbf{w}_{\text{fb}}$ is a 3D vector simultaneously modulating pitch ($f_0$), energy (envelope), and pause cadence.
- **Actuator Relationship:** SMS phase correction directly adjusts the next tap event timing. In Lucia, state coordinate $s_k^{(2)}$ is scaled by $40\text{ ms}$ and added to nominal latency $400\text{ ms}$, with an independent tempo actuator on coordinate $s_k^{(1)}$.

**Classification:** The mapping $\alpha_{\text{SMS}} \to w_{\text{fb}}$ is **`NOT ESTABLISHED`**.  
The cited literature $[0.10, 0.25]$ remains a **`SOURCE-SUPPORTED`** range for human periodic finger-tapping, but treating it as a calibrated value or envelope for Lucia's conversational controller is an unvalidated conceptual leap.

### 5.2 Audit of Convex Combination: $w_{\text{obs}} = 1 - w_{\text{fb}}$
- **Origin:** Proposed during calibration analysis to enforce scale preservation.
- **Status:** **`UNRATIFIED DESIGN ASSUMPTION`**.
- **Assessment:** While mathematically clean as a convex combination on $[-2.0, +2.0]^3$, it does not exist in canonical architecture, is not in `EXP_P25_Q2_1_EVALUATION_SPECIFICATION.md`, and directly contradicts the current harness code (`w_obs = 0.7`). It cannot be cited as a validated mathematical constraint.

### 5.3 Audit of Sensory Dominance: $w_{\text{fb}} < 0.50$
- **Origin:** Derived from $w_{\text{obs}} > w_{\text{fb}}$ under $w_{\text{obs}} = 1 - w_{\text{fb}}$.
- **Status:** **`CONDITIONAL DESIGN HEURISTIC (DEPENDENT ON UNRATIFIED ASSUMPTION)`**.
- **Assessment:** Because $w_{\text{obs}} = 1 - w_{\text{fb}}$ is unratified, $w_{\text{fb}} < 0.50$ is not an independent scientific constraint. If $w_{\text{obs}}$ were set to $1.0$ (as in C1), $w_{\text{obs}} > w_{\text{fb}}$ would only imply $w_{\text{fb}} < 1.0$. The bound $<0.50$ cannot be cited as independent evidence supporting $[0.10, 0.25]$.

### 5.4 Audit of Actuator Headroom & Stability Across $[0, 1]$
The prior draft claimed actuator headroom and latency bounds are preserved across $w_{\text{fb}} \in [0, 1]$.

**Technical Audit:**
- **Bounded Input:** Inputs are strictly clamped: $\|\mathbf{o}_k\|_\infty \le 2.0$, $\|\mathbf{R}_U(k)\|_\infty \le 2.0$ (`CANONICAL / ALREADY RATIFIED`).
- **Steady-State State Bound:** For constant input $\mathbf{x}^*$, steady-state state is $\mathbf{s}_\infty = \mathbf{x}^*$. Under $w_{\text{obs}} + w_{\text{fb}} = 1.0$, $\|\mathbf{x}^*\|_\infty \le 2.0$.
- **Tempo Actuator:** $\Delta v_L = \text{clip}(s_k^{(1)} \times 0.05, -0.15, 0.15)$. Linear operating range requires $|s_k^{(1)}| \le 3.0$. At steady state, $|s_\infty^{(1)}| \le 2.0 < 3.0$, so steady-state tempo does not saturate.
- **Transient Response & Headroom Under Perturbation:**
  - At turn 18, a $+300\text{ ms}$ perturbation is injected.
  - The latency actuator formula is $\tau_L = 400.0 + (s_k^{(2)} \times 40.0) + \delta_{\text{pert}}$.
  - If $s_k^{(2)}$ experiences transient overshoot, or if inputs are dynamically correlated, transient peaks could exceed steady-state bounds.
  - Furthermore, if $w_{\text{obs}}$ and $w_{\text{fb}}$ are not constrained to sum to $1.0$ (e.g. current harness $w_{\text{obs}} = 0.7$), then for $w_{\text{fb}} = 1.0$, $\|\mathbf{x}_k\|_\infty \le 0.7(2.0) + 1.0(2.0) = 3.4$, which yields $|s_k^{(1)}| > 3.0$ and saturates the tempo actuator.
- **Classification:** The universal claim that headroom and stability are preserved across $w_{\text{fb}} \in [0, 1]$ is **`NOT ESTABLISHED / REQUIRES FORMAL DERIVATION`**.

---

## 6. Epistemic Classification Ledger of Numerical Claims

Every numerical claim in this calibration analysis is formally audited and categorized:

| Parameter / Claim | Value / Range | Context | Epistemic Classification |
|---|---|---|---|
| **Integrator Leakage ($\lambda$)** | $0.15$ | Filter pole in C1/C2 state update | **`CANONICAL / ALREADY RATIFIED`** (`SPEC §3`) |
| **Observation Clamping** | $[-2.0, +2.0]$ | Input normalization bounds | **`CANONICAL / ALREADY RATIFIED`** (`SPEC §4.3`) |
| **Response Clamping** | $[-2.0, +2.0]$ | User response increment bounds | **`CANONICAL / ALREADY RATIFIED`** (`SPEC §4.3`) |
| **Actuator Bounds ($\tau_L$)** | $[0.0, 1000.0]\text{ ms}$ | Clamping on response latency | **`CANONICAL / ALREADY RATIFIED`** (`SPEC §5`) |
| **Actuator Bounds ($\Delta v_L$)** | $[-0.15, +0.15]$ | Clamping on speech tempo | **`CANONICAL / ALREADY RATIFIED`** (`SPEC §5`) |
| **Perturbation Injection** | $+300.0\text{ ms}$ | Turn 18 injected delay | **`CANONICAL / ALREADY RATIFIED`** (`SPEC §8`) |
| **Current C2 $w_{\text{obs}}$** | $[0.7, 0.7, 0.7]^T$ | Hardcoded in `exp_p25_q2_1.py:322` | **`UNRATIFIED CODE CONSTANT`** |
| **Convex Observation Weight** | $w_{\text{obs}} = 1 - w_{\text{fb}}$ | Proposed scale-preservation constraint | **`UNRATIFIED DESIGN ASSUMPTION`** |
| **Sensory Dominance Bound** | $w_{\text{fb}} < 0.50$ | Derived from $w_{\text{obs}} > w_{\text{fb}}$ via convex assumption | **`UNRATIFIED DESIGN ASSUMPTION`** |
| **Headroom Preservation $[0, 1]$** | $w_{\text{fb}} \in [0.0, 1.0]$ | Claim of non-saturation | **`NOT ESTABLISHED`** |
| **Literature Phase Correction ($\alpha$)** | $[0.10, 0.25]$ | Human sensorimotor tapping studies | **`SOURCE-SUPPORTED (EXTERNAL)`** |
| **Mapping $\alpha \to w_{\text{fb}}$** | Direct equivalence | Mapping SMS $\alpha$ to Lucia's $w_{\text{fb}}$ | **`NOT ESTABLISHED`** |
| **Candidate $w_{\text{fb}}$ Interval** | $[0.10, 0.25]$ | Proposed candidate range for $w_{\text{fb}}$ | **`PROVISIONAL / CANDIDATE — NOT RATIFIED`** |
| **Point Value ($w_{\text{fb}}^*$)** | Single scalar | Required for deterministic execution | **`NOT ESTABLISHED / UNCALIBRATED`** |
| **Proposed Future Sensitivity Grid** | $\{0.10, 0.15, 0.20, 0.25\}$ | Proposed robustness sweep | **`PROVISIONAL SENSITIVITY PROPOSAL`** |
| **Proposed Future User Coupling ($\beta_U$)** | $[0.1, 0.3]$ | Proposed closed-loop user model parameter | **`PROPOSED FUTURE PARAMETER / UNCALIBRATED`** |

---

## 7. Decoupling Calibration from Future Sensitivity Analysis

The proposed future discrete grid:
$$\mathcal{G}_{w_{\text{fb}}} = \{0.10, \; 0.15, \; 0.20, \; 0.25\}$$
must **NOT** be described as an empirical calibration procedure that selects the "best" parameter by observing experimental outcomes.

### Methodological Safeguards:
1. **Sensitivity Analysis $\ne$ Calibration:** A sensitivity analysis evaluates whether an effect is robust across a candidate range; it does **not** calibrate the parameter.
2. **Prohibition on Post-Hoc Tuning:** The experimental protocol must **never** select $w_{\text{fb}}$ by maximizing $\mathcal{H}$-B, minimizing turn-gap variance, maximizing $r_1$, or maximizing Transfer Entropy ($\text{TE}$).
3. **No Retrospective Calibration:** Running a grid of $w_{\text{fb}}$ values and picking the one that passes a hypothesis cannot retrospectively convert an outcome-dependent choice into an *a priori* calibration.
4. **Preregistration Requirement:** Any future sensitivity study must pre-register that $\mathcal{H}$-B is supported **only if incrementality holds across the entire admissible grid** (or at a pre-hypothesized critical threshold derived prior to execution).

---

## 8. Audit of Proposed Future User Coupling Parameter ($\beta_U$)

The prior draft proposed an interactive user model:
$$\tau_U(k) = \mu_U + \beta_U \big(\tau_L(k-1) - \mu_L\big) + \epsilon_k$$
with $\beta_U \in [0.1, 0.3]$.

**Epistemic Correction:**
- The interval $\beta_U \in [0.1, 0.3]$ is **`PROPOSED FUTURE MODEL PARAMETER / UNCALIBRATED`**.
- It is not established by canonical repository documentation, not calibrated against human conversational data in Lucia, and not derived from validated user experiments.
- Under strict research governance: **Agents must not solve one uncalibrated parameter ($w_{\text{fb}}$) by introducing another uncalibrated numerical assumption ($\beta_U$).**
- If a closed-loop synthetic user model is developed in a future research specification, $\beta_U$ must itself undergo an independent calibration protocol or be treated as a manipulated independent variable across an explicit sensitivity range.

---

## 9. Outcome-Independence Audit

To verify that this calibration audit remains strictly outcome-independent, every metric and result from prior executions was audited:

| Evaluation Metric / Finding | Consulted or Used in Audit? | Verification Detail |
|---|---|---|
| **$r_1$ (Lagged Pearson Correlation)** | **NO** | Zero correlation values used to justify bounds. |
| **Transfer Entropy ($\text{TE}_{U\to L}, \text{TE}_{L\to U}$)** | **NO** | Zero information-flow metrics consulted. |
| **Net Asymmetry ($\Delta\text{TE}_{\text{net}}$)** | **NO** | Zero directional asymmetry data used. |
| **Turn-Gap Variance ($\sigma^2_{\text{gap}}$)** | **NO** | Variance outcomes completely excluded. |
| **Perturbation Recovery Time ($T_{\text{rec}}$)** | **NO** | Recovery speed not used to calibrate gain. |
| **Conversational Overlap Ratio** | **NO** | Overlap data completely excluded. |
| **Hypothesis Outcomes ($\mathcal{H}$-A, $\mathcal{H}$-B, $\mathcal{H}$-C)** | **NO** | Hypothesis status not used to tune parameter. |
| **Surrogate Exceedance ($\theta_{95}$, $p$-value)** | **NO** | Surrogate distributions completely excluded. |
| **Historical Invalidated Results** | **NO** | Discredited variance surrogate data played zero role. |

**Audit Conclusion:** The analysis is **100% outcome-independent**.

---

## 10. Confound & Architecture Ledger

```
Identified Architecture & Confound Ledger:
  [!] Confound 1: Current harness hardcodes w_obs = 0.7, breaking C1/C2 equivalence at w_fb = 0.
      --> Status: UNRESOLVED SPECIFICATION/HARNESS DISCREPANCY.
  [!] Confound 2: Synthetic user in harness is an open-loop script (OU process).
      --> Status: HARNESS DEFICIENT FOR C2 (tests user noise, not reciprocal feedback).
  [!] Confound 3: Mapping literature α to w_fb assumes equivalence across different dynamics.
      --> Status: NOT ESTABLISHED (analogical hypothesis only).
  [!] Confound 4: Selecting a point value from candidate interval [0.10, 0.25] without human data.
      --> Status: PROHIBITED (arbitrary guessing).
```

---

## 11. Final Disposition & Governance Decision

In accordance with strict research governance and the explicit criteria of this inquiry:

> **What value or admissible range of $w_{\text{fb}}$ is justified before observing EXP-P25-Q2.1 outcomes?**  
> 1. No outcome-independent point value for $w_{\text{fb}}$ has been established.  
> 2. The interval $[0.10, 0.25]$ is a **provisional, literature-informed candidate range**, but its formal equivalence to Lucia's controller is **not established**.  
> 3. The relation $w_{\text{obs}} = 1 - w_{\text{fb}}$ is an **unratified design assumption** that contradicts current harness code.  
> 4. The current synthetic user fixture is **open-loop**, precluding true reciprocal feedback testing.

Therefore, the final disposition is:

### **`FINAL DISPOSITION: Q2-04 REMAINS OPEN`**

### Operational & Gate Invariants:
1. **Condition C2 Strictly Blocked:** In [`tests/evaluation/phase25/exp_p25_q2_1.py`](file:///c:/Users/Lunafiah/Desktop/My_project/Lucia/tests/evaluation/phase25/exp_p25_q2_1.py), `C2BidirectionalController` must continue to raise `TBDGainUnestablishedError(Exception)`.
2. **Hypothesis $\mathcal{H}$-B Status Preserved:** $\mathcal{H}$-B (Reciprocal Incrementality) remains recorded as:
   `BLOCKED / INCONCLUSIVE — TBD-Q2-04`
3. **No Rerun Authorized:** This calibration correction does **NOT** authorize rerunning `EXP-P25-Q2.1`.
4. **Gates Preserved:**
   - Architecture Gate: **`LOCKED`**
   - Implementation Gate: **`LOCKED`**
   - Genesis Invariant (`INV-8`): **`BIT-EXACT`** (`data/profile.json == {"is_onboarded": false}`)
   - Production Codebase Diff: **`0 files changed`**
