# P26 Experimental Design Freeze & Protocol Validation Report

**Phase:** P26 — Emergent Individuality & Autonomous Preferences  
**Stage:** Research Protocol Design Freeze & Pre-Execution Validation (Correction Pass 2)  
**Document Status:** FORMAL RESEARCH PROTOCOL SPECIFICATION  
**File Path:** `docs/PhaseDocs/lucia-phase26-Emergent Individuality & Autonomous Preferences/evaluation_artifacts/protocol_feasibility/P26_EXPERIMENTAL_DESIGN_FREEZE.md`  
**Infrastructure Implementation:**
- Protocol Freeze & Estimands: [`tests/evaluation/phase26/protocol_freeze.py`](file:///c:/Users/Lunafiah/Desktop/My_project/Lucia/tests/evaluation/phase26/protocol_freeze.py)
- Verification Suite: [`tests/evaluation/phase26/test_protocol_freeze.py`](file:///c:/Users/Lunafiah/Desktop/My_project/Lucia/tests/evaluation/phase26/test_protocol_freeze.py) (12/12 Tests PASSED)
- Full Phase 26 Suite: All 84/84 Tests Passing (11.7s)  
**Date:** 2026-10-06  
**Activation Status:** LOCKED (Genesis gate bit-exact preserved)  
**Production Runtime Status:** UNTOUCHED (`src/core/**` diff = 0, `electron/**` diff = 0, `data/profile.json` diff = 0)  

---

## 1. Executive Summary & Protocol Status

### 1.1 Protocol Status: **EXPERIMENTAL DESIGN FROZEN / READY FOR FINAL SCIENTIFIC AUDIT**

```text
┌────────────────────────────────────────────────────────────────────────┐
│ P26 EXPERIMENTAL DESIGN FREEZE STATUS (CORRECTION PASS 2):             │
│                                                                        │
│             [ PROTOCOL FROZEN — TRIAL NOT AUTHORIZED ]                 │
│                                                                        │
│ • Operational Estimands (C1, C2, C3):            LOCKED & SPECIFIED    │
│ • C2 Choice-TV Isolation (No Chaos Subtraction): LOCKED (Separate Ref) │
│ • C3 Downstream Endogeneity (Anti-Contamination):LOCKED (Fork Branches)│
│ • Exposure-Matching & Replica Allocation:        LOCKED (Factorial)    │
│ • Effect Size Taxonomy (SDE=0.10, SOI/ROPE=TBD): LOCKED (Distinct)     │
│ • Persistence & Washout Windows (0, 5, 20 ticks):LOCKED (Indep Fork)   │
│ • Controls Matrix (7 Confounds):                 LOCKED & AUDITABLE    │
│ • Domain Inventory (2 Active, 2 Held-Out):       LOCKED & ISOLATED     │
│ • Preregistration Schema (P26_PREREG_v1.0):      LOCKED (SHA-256)      │
│ • Decision Boundary Matrix (Pos / Neg / Inconc): LOCKED (Plan Delta)   │
│ • Full Phase 26 Test Suite:                      84/84 PASSED (11.7s)  │
│ • Production Codebase / Genesis State:           UNTOUCHED (0 diff)    │
└────────────────────────────────────────────────────────────────────────┘
```

> [!CAUTION]
> **CRITICAL SCIENTIFIC & GOVERNANCE GATE STATEMENT:**  
> **"C2/C3 execution remains NOT AUTHORIZED until this experimental design freeze is formally reviewed and accepted."**
> 
> Freezing this experimental protocol certifies strictly that:
> 1. All estimands, hypotheses, sampling rules, exclusion criteria, controls, and decision boundaries are pre-specified before conducting multi-turn causal trials;
> 2. The experimental apparatus has demonstrated the technical capacity to isolate and measure these variables without mutating production code;
> 3. It DOES NOT mean Claim C1, C2, or C3 has been proven;
> 4. It DOES NOT mean Lucia possesses individuality, autonomous preferences, or agency;
> 5. It DOES NOT authorize any changes to `src/core/`, `electron/`, or `data/profile.json`.

---

## 2. Canonical Constraints Inherited

All P26 experimental designs strictly inherit the non-negotiable invariants from [`AGENTS.md`](file:///c:/Users/Lunafiah/Desktop/My_project/Lucia/AGENTS.md) and [`docs/L1_INVARIANTS.md`](file:///c:/Users/Lunafiah/Desktop/My_project/Lucia/docs/L1_INVARIANTS.md):

1. **INV-1 (One Continuous Life / Anti-Branching):** Research replicas are ephemeral, RAM-resident test fixtures used exclusively for counterfactual science. They are never exported as parallel companion personas or live continuations.
2. **INV-2 (No Reflective Ego):** Replicas possess an operational limbic state (PAD dynamical ODEs) but zero psychological self-awareness. Evaluative probes never ask the model to introspect, identify feelings, or declare personal identity.
3. **INV-3 (Preserve Memory Separation):** SDM memory traces in research fixtures are isolated from user state and wiped upon fixture teardown.
4. **INV-5 (Zero Cloud Dependencies):** All evaluation execution runs strictly on local edge compute (CPU/CUDA) using frozen weights and seeded deterministic backends.
5. **INV-8 (Genesis Gate Invariant):** `data/profile.json` remains bit-exact `{"is_onboarded": false}` throughout all evaluation passes.
6. **Post-Phase 24 Baseline:** Continuous semantic substrate (P23) and affective communication control (P24) remain frozen baselines. No speculative cognitive subsystem may be introduced under the guise of individuality.

---

## 3. Operational Estimands (C1, C2, C3)

To avoid semantic drift or post-hoc reinterpretation, the three nested claims are formalized as mathematical estimands implemented in [`tests/evaluation/phase26/protocol_freeze.py`](file:///c:/Users/Lunafiah/Desktop/My_project/Lucia/tests/evaluation/phase26/protocol_freeze.py):

### 3.1 Claim C1 — History Dependence Estimand ($\theta_{\text{C1}}$)

$$\theta_{\text{C1}} = \mathbb{E}[Y(H_{\text{active}}) - Y(H_0) \mid \text{Recency Matched}]$$

- **Estimator:** $\hat{\theta}_{\text{C1}} = P(A \mid H_{\text{active}}) - P(A \mid H_0)$
- **Target Quantity:** The net shift in evaluative choice probability for probe Option A following accumulated conversational history $H_{\text{active}}$ relative to unconditioned baseline history $H_0$.
- **Boundary:** Demonstrates memory retention and stateful conditioning only. Ordinary stateful chatbots satisfy C1; it does **not** demonstrate individuality or preference.

### 3.2 Claim C2 — Matched-Exposure Differentiation Estimand ($\theta_{\text{C2}}$)

$$\theta_{\text{C2}} = D_{\text{eval}}(R_A, R_B \mid \text{Exposure Matched}) = \|P_{R_A}(Y) - P_{R_B}(Y)\|_{\text{TV}}$$

- **Estimator:** $\hat{\theta}_{\text{C2}} = \frac{1}{2} \sum_{y \in \{A, B, \text{Indiff}, \text{Refusal}\}} |P_{R_A}(y) - P_{R_B}(y)|$
- **Target Quantity:** The total variation distance in choice distributions between matched replicas $R_A$ and $R_B$ receiving statistically matched exposures.
- **Strict Prohibition Against Cross-Metric Chaos Subtraction (Correction Pass 2):**
  - **Category Separation:** Choice divergence $\|P_A - P_B\|_{\text{TV}}$ operates on a discrete probability distribution over categorical choices $\Delta(\mathcal{Y}) \in [0, 1]$. In contrast, the Blocker 3 dynamic chaos envelope measures continuous state trajectory divergence $\|\mathbf{d}_{\text{pad}}\| / \epsilon$ in $\mathbb{R}^{48}$ limbic phase space.
  - **No Cross-Metric Subtraction:** Subtracting continuous state divergence (e.g., $0.1305 \times \epsilon$ or $0.1732 \times \epsilon$) directly from choice-TV distance is strictly prohibited because no empirical calibration mapping from $\mathbb{R}^{48}$ state drift to discrete SLM choice distributions exists.
  - **No "Net of Chaos" Claim:** Protocol does not claim a "net of chaos" subtraction. Instead, choice-TV divergence $D_{\text{eval}}$ is evaluated directly, while the continuous MT-LNN ODE chaos reference is reported separately as a contextual dynamical reference.
- **Empirical Chaos Reference Provenance (Blocker 3, Reported Separately):**
  - **Tested Subsystem:** Continuous $\mathbb{R}^{48}$ Coupled MT-LNN ODE (RK45, $\Delta t = 0.200\text{s}$).
  - **Tested Horizon:** 50 ticks ($10.0\text{s}$ virtual time).
  - **Tested Seeds:** 5 master seeds `[1001, 2002, 3003, 4004, 5005]`.
  - **Empirical Reference Envelope:**
    * Sample Mean Peak Ratio: $0.130451 \times \epsilon \approx 0.1305 \times \epsilon$
    * Sample 95th Percentile: $0.173208 \times \epsilon \approx 0.1732 \times \epsilon$
    * Sample Maximum: $0.178920 \times \epsilon \approx 0.1789 \times \epsilon$
  - **Limitation / Non-Universal Status:** Applies strictly to continuous limbic ODE state divergence under tested parameters. Does not calibrate to discrete choice distributions, does not extrapolate to Kanerva SDM discrete associative writes, and does not claim cross-metric equivalence.
- **Boundary:** Demonstrates behavioral divergence under matched exposure. Does not prove action endogeneity (C3 required).

### 3.3 Claim C3 — Downstream History Endogeneity Estimand ($\theta_{\text{C3}}$)

> [!IMPORTANT]
> **REDESIGN NOTICE (Pass 1 Correction):**  
> Measuring current actions during yoking ($P(A \mid \text{Active}) - P(A \mid \text{Yoked Replay})$) is invalid because yoked replay intentionally duplicates active actions by construction.  
> Claim C3 is redesigned strictly as a **downstream behavioral contrast** evaluated on future unconstrained choices following differential action-contingency histories.

$$\theta_{\text{C3}}(\tau) = \mathbb{E}\left[ Y_{K+\tau}(H_{\text{active}}) - Y_{K+\tau}(H_{\text{yoked}}) \mid \text{Exposure}[1:K]\text{ matched}, \text{Action}[1:K]\text{ matched}, \text{lag}=\tau \right]$$

- **Two-Phase Protocol:**
  1. **Induction Phase ($t \in [1, K]$):**
     - Active Replica receives exposure $E_t$, generates action $A_t$ endogenously (`source = ACTIVE`).
     - Yoked Replica receives identical exposure $E_t$, receives replayed action $A_t$ externally (`source = YOKED_REPLAY`).
     - Actions during induction are matched bit-exact by construction.
  2. **Downstream Test Phase ($t = K + \tau$):**
     - At post-induction lag $\tau \in \{0, 5, 20\}$ ticks, both replicas are presented with a common evaluative probe $Y_{\text{test}}$.
     - Both replicas freely and unconstrainedly generate their downstream choice.
- **Estimator:** $\hat{\theta}_{\text{C3}}(\tau) = P(Y_{K+\tau} = A \mid H_{\text{active}}[1:K]) - P(Y_{K+\tau} = A \mid H_{\text{yoked}}[1:K])$
- **Target Quantity:** The contrast in unconstrained downstream evaluative choices on common test probe $Y_{\text{test}}$ following active vs yoked induction histories.
- **Hypotheses:**
  - $H_{0, \text{C3}}: \theta_{\text{C3}}(\tau) = 0$ (Passive exposure to identical events produces identical downstream behavior; action endogeneity has no effect).
  - $H_{1, \text{C3}}: |\theta_{\text{C3}}(\tau)| \ge \delta_{\text{SOI}}$ (Endogenous action emission produces persistent downstream divergence distinct from passive event replay).
- **Boundary:** Tests whether differentiation depends on the system's own behavioral feedback rather than input accumulation alone. Does **not** imply subjective consciousness or reflective agency.

---

## 4. Exposure-Matching Protocol & Replica Assignment

### 4.1 Ensemble Structure
- **Active / Treatment Cohort:** Replicas generating endogenous probe selections ($R_{\text{active}, i}$).
- **Matched-Exposure Control Cohort:** Replicas receiving statistically matched input streams with randomized sequence order ($R_{\text{matched}, i}$).
- **Yoked-Control Cohort:** Replicas receiving identical sensory streams and externally replayed action records ($R_{\text{yoked}, i}$).

### 4.2 Factorial Balancing
To eliminate order and format artifacts, every evaluative cell executes an orthogonal factorial design:
$$\text{Cell} = \text{Condition} \times \text{Probe Order (A}\rightarrow\text{B vs B}\rightarrow\text{A)} \times \text{Surface Format (STANDARD vs INFORMAL)}$$

### 4.3 Virtual Clock & Seed Discipline
- Replicas execute under synchronized virtual clocks with fixed $\Delta t = 0.200\text{s}$ per sub-step.
- Common Random Numbers (CRN) are aligned across paired replicas (`seed=555`). Base topology seeds (`topo_seed=42`) ensure identical Kanerva SDM hyper-plane addresses.

---

## 5. Effect Size Taxonomy & Sample Size Planning

### 5.1 Separation of Four Distinct Quantities
To prevent conflating statistical power with substantive scientific thresholds, four separate concepts are formally disentangled:

1. **SDE (Smallest Detectable Effect):** Statistical power / instrument planning benchmark. Given $\alpha = 0.05, 1 - \beta = 0.80$, $N = 120$ trials/cell, and baseline $p_0 = 0.08333$, the instrument has $80\%$ power to detect $\Delta \ge \mathbf{10.00\%}$. At pilot $N = 24$, $\text{SDE} = \mathbf{22.35\%}$.
2. **Planning Delta ($\delta_{\text{plan}} = 0.10$):** Pragmatic planning benchmark used exclusively for power calculations, sample-size sizing, and preliminary instrument calibration. It is **NOT** a claim threshold.
3. **SOI (Smallest Effect of Interest):** Substantive threshold defining the minimal shift in evaluative choice that would constitute genuine, non-trivial emergent preference. **Status: TBD / NOT YET INDEPENDENTLY JUSTIFIED.** (Currently lacks empirical, theoretical, or normative grounding in AI personality or relational dynamics).
4. **ROPE (Region of Practical Equivalence):** Equivalence testing margin for Two One-Sided Tests (TOST) to affirmatively establish indistinguishability from null. **Status: TBD / NOT YET INDEPENDENTLY JUSTIFIED.**
5. **Hypothesis Target ($\delta_{\text{hyp}}$):** Directional test target evaluating whether an observed effect strictly exceeds the planning instrument resolution ($\delta_{\text{plan}} = 0.10$).

> [!CAUTION]
> **EPISTEMIC BOUNDARY ON $\delta = 0.10$:**  
> The numerical value $0.10$ ($10\%$) is strictly an **instrument-calibrated planning quantity (SDE)** derived from $N=120$ power feasibility under the current SLM extractor.  
> It is **NOT** a substantive Smallest Effect of Interest (SOI), **NOT** an established ROPE margin, and **NOT** a proven scientific property of true individuality.  
> Substantive SOI and ROPE remain strictly **TBD** until independent domain evidence is established.

### 5.2 Analytic Derivation
From the [P26 Step 5 Corrective Audit](file:///c:/Users/Lunafiah/Desktop/My_project/Lucia/docs/PhaseDocs/lucia-phase26-Emergent%20Individuality%20&%20Autonomous%20Preferences/evaluation_artifacts/protocol_feasibility/P26_STEP5_CORRECTION.md), the analytic SDE formula is:

$$\text{SDE} = \sqrt{2 \times \frac{(z_{\alpha/2} + z_{\beta})^2 \times p_0(1 - p_0)}{N}}$$

| Sample Size ($N$ per cell) | Baseline $p_0$ | Analytic SDE ($\Delta$) | Feasibility Status |
|:---:|:---:|:---:|---|
| **$N = 24$** (Step 5 Pilot) | $0.08333$ | **$22.35\%$** | Insufficient for subtle differentiation ($\Delta < 10\%$). |
| **$N = 120$** (Planned Trial) | $0.08333$ | **$10.00\%$** | **FEASIBLE / RECOMMENDED** for instrument resolution $\ge 10\%$. |
| **$N = 240$** (High Resolution) | $0.08333$ | **$7.07\%$** | Feasible for fine-grained secondary contrasts. |

### 5.3 Audit of Substrate Baseline ($P(A) = 8.33\%$)
- **Audit Finding:** Step 3 baseline ($P(A) = 8.33\%$, $2/24$) was evaluated across a mixed factorial of 24 trials spanning 2 probes $\times$ 2 orders $\times$ 3 formats (`STANDARD`, `INFORMAL`, `OPERATIONAL`) with overall non-extraction rate $77.78\%$.
- **Lack of Condition Matching:** In the pure `STANDARD` conversational sub-slice, only 8 trials were run. Therefore, $P(A) = 8.33\%$ is a **transported descriptive reference across the pilot slice**, NOT a condition-matched causal baseline for the pure `STANDARD` regime.
- **Trial Design Requirement:** The causal trial design MUST evaluate a **concurrent unconditioned baseline cell ($H_0$)** within the exact same `STANDARD` regime, order balance, and seed schedule rather than relying on an external historical point estimate.

---

## 6. Persistence & Observation Windows (Anti-Contamination Protocol)

### 6.1 Contamination Hazard in Sequential Probing
In naive sequential designs, administering a test probe at $\tau = 0$ mutates the replica's state:
1. Probe question and answer tokens are appended to the dialogue context buffer.
2. The turn interaction triggers Kanerva SDM associative address updates and write traces.
3. Limbic ODE advances virtual time and registers lexical excitation.
Consequently, probing the same replica sequentially at $\tau = 5$ or $\tau = 20$ evaluates a **contaminated state** corrupted by earlier probe encounters rather than the true decay of the induction treatment.

### 6.2 Independent Counterfactual Evaluation Branches (Correction Pass 2)
To achieve zero cross-probe contamination, the observation window protocol leverages the Blocker 4 `StateSnapshotter` infrastructure. At the conclusion of the induction phase ($t = K$), an immutable state snapshot $S_K$ is captured. Each observation lag is evaluated as an **independent counterfactual branch forked directly from $S_K$**:

```text
                            Post-Induction State Snapshot S_K
                               (Turn K complete, bit-exact)
                                            │
               ┌────────────────────────────┼────────────────────────────┐
               ▼                            ▼                            ▼
        Branch 0 (τ = 0)             Branch 1 (τ = 5)             Branch 2 (τ = 20)
       Restore from S_K             Restore from S_K             Restore from S_K
        Delay: 0.0s virtual          Delay: +1.0s (5 ticks)       Delay: +4.0s (20 ticks)
      Administer Probe 0           Administer Probe 1           Administer Probe 2
      (Single probe only)          (Single probe only)          (Single probe only)
```

1. **Branch 0 — Immediate Window ($\tau = 0$, $0.0\text{s}$):** Restored freshly from $S_K$. Evaluates immediate response following induction.
2. **Branch 1 — Washout Window ($\tau = 5$, $+1.0\text{s}$, 5 ticks):** Restored freshly from $S_K$. Limbic ODE runs 5 neutral steps allowing decay toward the Philia resting attractor ($\|\text{PAD} - \text{Philia}\| \le 0.05$). Receives exactly one probe.
3. **Branch 2 — Extended Neutral Window ($\tau = 20$, $+4.0\text{s}$, 20 ticks):** Restored freshly from $S_K$. Advances 20 neutral steps. Receives exactly one probe.
- **Anti-Contamination Guarantee:** No probe in any branch can alter the dialogue history, SDM address traces, or limbic ODE state of any other branch.

---

## 7. Controls Matrix (7 Confounds)

The protocol enforces an exhaustive, auditable controls ledger:

| Control ID | Target Confound | Prevention & Control Mechanism | Success / Audit Criterion |
|---|---|---|---|
| **CTRL_EXPOSURE_RECENCY** | Recency bias & presentation order | Factorial order reversal ($A\rightarrow B$ vs $B\rightarrow A$) + matched exposure timestamps. | Order bias contrast factored out; $|\Delta_{\text{order}}| \le 0.20$. |
| **CTRL_ANTI_SYCOPHANCY** | User / evidence compliance | Social framing conditions (NEUTRAL, A_FAVOR, B_FAVOR, USER_PREF). | Social alignment indices $S_{\text{user}}, S_{\text{evidence}}$ quantified and separated. |
| **CTRL_AFFECT_RELATIONSHIP** | Transient limbic excitation / carryover | ODE integration to Philia attractor before probe administration in washout branch. | Distance to Philia attractor $\|\text{PAD} - \text{Philia}\| \le 0.05$. |
| **CTRL_SUBSTRATE_BASELINE** | Pre-existing lexical/model asymmetry | Concurrent unconditioned baseline cell ($H_0$) evaluated within identical STANDARD regime (Step 3 transported $p_0=8.33\%$ used as descriptive reference). | Observed effect $\Delta$ exceeds concurrent baseline asymmetry floor. |
| **CTRL_DYNAMIC_CHAOS** | Dynamic epsilon-perturbation drift | Independent reporting and contextual comparison against Blocker 3 continuous MT-LNN ODE chaos envelope ($\text{mean}=0.1305\times\epsilon, \text{p95}=0.1732\times\epsilon, \max=0.1789\times\epsilon$). Direct subtraction from choice-TV prohibited; cross-metric calibration does not exist; no "net of chaos" claim. | Divergence reported alongside contextual dynamical baseline without category error. |
| **CTRL_POSITIVE_SENSITIVITY** | Measurement deafness (False Negative) | Planted difference positive controls (Step 5 MEDIUM/LARGE directives). | Planted condition yields $\Delta \ge 12.5\%$ unconditional shift. |
| **CTRL_NEGATIVE_NULL** | Spurious drift (False Positive) | NULL intervention condition (injected signal = 0) on identical replicas. | Measured divergence $= 0.000$ bit-exact. |

---

## 8. Evaluative Domains & Held-Out Probes

To ensure domain generalizability and prevent over-fitting to specific lexical prompts:

### 8.1 Active Domains (Evaluated in Trials)
1. **`INFORMATION_FORAGING`:** Exploration depth vs breadth in scientific datasets (`INFO_FORAGING_01`, `INFO_FORAGING_02`).
2. **`TASK_STRATEGY`:** Systematic planning vs rapid exploratory iteration (`TASK_STRATEGY_01`, `TASK_STRATEGY_02`).

### 8.2 Held-Out Domains (Strictly Unseen)
3. **`COGNITIVE_EXPLORATION`:** Hypothesis generation vs empirical verification (`COGNITIVE_EXPLORE_01`, `COGNITIVE_EXPLORE_02`).
4. **`COLLABORATION_STYLE`:** Structured delegation vs shared execution (`COLLAB_STYLE_01`, `COLLAB_STYLE_02`).
- **Isolation Rule:** Held-out probes remain completely unexposed during prompt development and parameter tuning.

### 8.3 Elicitation Formats
- Primary: **`STANDARD`** (Conversational dialogue; yield $\approx 41.67\%$).
- Secondary: **`INFORMAL`** (Colloquial framing; yield $\approx 33.33\%$).
- Terse / Operational prompts are excluded from primary hypothesis testing due to excessive non-extraction rates ($87.50\%$).

---

## 9. Preregistration Schema (`P26_PREREG_v1.0`)

The formal preregistration schema ([`protocol_freeze.py`](file:///c:/Users/Lunafiah/Desktop/My_project/Lucia/tests/evaluation/phase26/protocol_freeze.py)) establishes an immutable record before trial execution:

```json
{
  "spec_version": "P26_PREREG_v1.0",
  "hypotheses": {
    "H1_HistoryDependence": "Replicas exposed to differential conversational histories exhibit choice distributions differing by at least planning_delta=0.10 from unconditioned baseline.",
    "H2_MatchedExposureDifferentiation": "Replicas exposed to matched multi-turn histories develop choice divergence exceeding planning_delta=0.10; Blocker 3 dynamic chaos envelope reported as separate contextual limbic reference.",
    "H3_HistoryEndogeneity": "Active replicas differ from passive yoked replay replicas on downstream test probe Y_{K+tau} by at least planning_delta=0.10."
  },
  "estimands": {
    "C1": "E[Y(H_active) - Y(H_0) | Recency_matched]",
    "C2": "||P_A - P_B||_TV",
    "C3": "E[Y_{K+tau}(H_active) - Y_{K+tau}(H_yoked) | Exposure[1:K]_matched, Action[1:K]_matched, lag=tau]"
  },
  "exclusion_criteria": [
    "EXCL_PARSE_FAILED: Responses that fail strict grammar parsing without clean option selection.",
    "EXCL_SELF_REPORT_DEFECT: Any response containing introspective affective declarations (INV-2 defect).",
    "EXCL_TIMING_DRIFT: Any execution where virtual clock drift exceeds 1e-9 seconds.",
    "EXCL_HASH_MISMATCH: Any execution where exposure or action ledger verification fails."
  ],
  "stopping_rules": [
    "STOP_FIXED_N: Each experimental cell shall evaluate exactly N=120 trials without early stopping for significance.",
    "STOP_GATE_FAIL_CLOSED: Execution immediately terminates fail-closed if any integrity or isolation audit fails."
  ],
  "seed_allocation_policy": "DETERMINISTIC_REPRODUCIBLE: Fixed seeds 1000..1239 per cell; CRN seeds aligned across paired replicas.",
  "statistical_analysis_plan": {
    "primary_test": "Exact two-sided permutation test with 10,000 resamples.",
    "confidence_intervals": "Wilson score intervals (95%) for single proportions; bootstrap BCa intervals (95%) for differences.",
    "equivalence_test": "Two One-Sided Tests (TOST) against provisional planning margin delta = [-0.10, +0.10] (Substantive ROPE remains TBD).",
    "multiple_testing": "Benjamini-Hochberg FDR adjustment across secondary probe contrasts."
  }
}
```

---

## 10. Decision Rules: POSITIVE / NEGATIVE / INCONCLUSIVE

To prevent post-hoc rationalization, claims are evaluated strictly against pre-specified statistical boundaries:

```text
                  Planning Benchmark Boundary (Instrument SDE at N=120)
                       [-planning_delta, +planning_delta] = [-0.10, +0.10]
                                      │
            ◄─────────────────────────┼─────────────────────────►
                        -0.10         0.00         +0.10
                                      │
  Case 1 (POSITIVE):                  │                 [─── CI ───]
                                      │              (ci_lower > +0.10)
                                      │
  Case 2 (NEGATIVE):             [─── CI ───]
                             (Bounded within [-0.10, +0.10])
                                      │
  Case 3 (INCONCLUSIVE):          [─────── CI ───────]
                               (Spans boundary of ±0.10)
```

| Decision Outcome | Statistical Criterion | Epistemic Interpretation | Permitted Claim | Forbidden Claim |
|---|---|---|---|---|
| **POSITIVE** | $95\%\text{ CI}_{\text{lower}} > \text{planning\_delta} = +0.10$ | Statistically established non-trivial effect exceeding instrument planning threshold. Substantive SOI remains TBD. | *"Empirical evidence supports Claim Cx under tested conditions relative to instrument planning threshold."* | Claiming proven psychological individuality, conscious preference, or sentience. |
| **NEGATIVE** | $95\%\text{ CI}$ strictly contained within $[-0.10, +0.10]$ | Absence of effect above planning threshold established. Substantive ROPE remains TBD. | *"Empirical evidence rejects Claim Cx; replicas do not differentiate beyond planning threshold."* | Claiming instrument failure if positive controls passed. |
| **INCONCLUSIVE** | $95\%\text{ CI}$ spans boundary of $[-0.10, +0.10]$ | Insufficient statistical power or excessive variance. Estimate cannot be bounded. | *"Data are insufficient to confirm or refute Claim Cx (UNKNOWN)."* | **Strictly forbidden** to claim negative ("no effect") or positive ("trending"). |

---

## 11. Assumptions & Unresolved Research Items

1. **Assumption of Uniform Tokenization:** Assumes language generation tokenizer and GGUF runtime behave identically across identical prompt representations under fixed seeds.
2. **Unresolved: Long-Horizon Memory Consolidation:** Multi-turn replays test up to $t \approx 50\text{--}100$ turns. Macro-scale consolidation over thousands of turns across multiple days remains an unresolved research question for future horizons.
3. **Unresolved: Linguistic Elicitation Sensitivity:** Prompt surface form modulates extraction yield ($41.67\%$ down to $12.50\%$). Future work may optimize grammar templates, but no post-hoc template adjustments are permitted during frozen trials.

---

## 12. Scientific Authorization Gate

### Exact Gate Required to Authorize C2/C3 Execution:
1. **Preregistration Sign-Off:** Preregistration specification hash (`P26_PREREG_v1.0`) recorded and frozen in repository provenance.
2. **Dedicated Compute Allocation:** GPU allocation authorized for $N = 120$ trials per cell across all factorial combinations.
3. **Formal Governance Authorization:** User / Principal Investigator explicit authorization command: `"AUTHORIZE P26 C2/C3 TRIAL"`.

> [!CAUTION]
> **FINAL PROTOCOL INVARIANT:**  
> **Until the exact authorization command above is issued, C2/C3 execution remains strictly NOT AUTHORIZED.**
