# Phase 22 H1 — R3 Consumer Sensitivity & Robustness Envelope Study

> **Status:** RESEARCH EVIDENCE RECORD — ARCHITECTURE GATE STRICTLY LOCKED  
> **Governance Invariants:** Phase 22 H1 is **INCONCLUSIVE** | Quality Gate 2 is **STRICTLY BLOCKED** ($\Delta_{\text{HM}} = 0.0685 < 0.1500$)  
> **ADR-029 Status:** **`DRAFT / RESEARCH RECORD ONLY / NOT RATIFIED`**  
> **Production Admission:** **NOT ADMITTED** (Zero mutations to `src/core/**`, `src/api/**`, `electron/**`)  
> **Genesis Gate:** `data/profile.json` preserved bit-exact `{"is_onboarded": false}`  
> **Consumer C Transition Outcome:** **`TRANSITION_INTERVAL_OBSERVED`** ($[1.0, 1.5]$)  
> **Consumer D Transition Outcome:** **`DISCRETE_QUALIFYING_REGIME_OBSERVED`** ($1 / 30$ cells: $\{(\mu_d = 1.00, \gamma_\kappa = 0.50)\}$)  
> **Hardware Discipline:** 100% CPU Execution / 0.0 MB GPU VRAM Allocation  
> **Date:** September 2026  
> **Artifact Type:** Formal Research Sensitivity & Robustness Envelope Report (Phase 22 H1)

---

## 1. Executive Summary

This study establishes the **Phase 22 H1 R3 Consumer Sensitivity & Robustness Envelope Investigation**, resolving whether the downstream adapter dependence observed in the completed *R3 Consumer Transferability & Adapter Dependence Study* is:
1. a **robust, fundamental property of the evaluated mathematical functional forms**, or
2. **primarily an artifact of the specific frozen parameter regimes** selected for Consumers C and D.

In the previous transferability study, candidate directional representation $R3 = \operatorname{sign}_\epsilon(\mathbf{r}_T) \in \{-1, 0, +1\}^3$ transferred cleanly to the linear-quadratic separable cost model (`B_DIRECTIONAL_SEPARABLE`, $\text{DiffRate} = 79.89\%$), but failed to produce discrete action differentiation under the baseline parameterizations of the continuous multiplicative utility model (`C_CONTINUOUS_UTILITY`, $\gamma_C = 1.0$, $\text{DiffRate} = 0.00\%$) and the non-linear magnitude-dominant model (`D_MAGNITUDE_DOMINANT`, $\mu_d = 0.20, \gamma_\kappa = 1.0$, $\text{DiffRate} = 0.00\%$).

To systematically map the boundary between functional form constraints and parameter regime selection, this study pre-registered, froze, and evaluated a **38-regime parameter sensitivity sweep** (8 levels for Consumer C, 30 cells for Consumer D) alongside bit-exact historical controls (`A_REFERENCE` and `B_DIRECTIONAL_SEPARABLE`) on the frozen Candidate G1 stimulus corpus ($N=270$, Master Seed 9999).

```
                      [R3 Sensitivity & Robustness Matrix]
                                       │
        ┌──────────────────────────────┴──────────────────────────────┐
        ▼                                                             ▼
[Consumer C: Multiplicative Utility]               [Consumer D: Magnitude-Dominant]
1D Sweep: \gamma_C \in [0.10, 2.00] (8 levels)     2D Sweep: \mu_d \times \gamma_\kappa (30 cells)
Transition Interval: [1.0, 1.5]                    Qualifying Count: 1 / 30 (3.33%)
Qualifying Region: \gamma_C \in \{1.50, 2.00\}     Qualifying Cell: Strictly {(\mu_d=1.00, \gamma_\kappa=0.50)}
Regime-Dependent Activation                        Grid-Bound Directional Suppression
```

### Core Empirical Findings:
1. **Consumer C Parameter Sensitivity & Transition Envelope (`TRANSITION_INTERVAL_OBSERVED`)**:
   - For $\gamma_C \le 1.00$, discrete action differentiation is completely suppressed ($\text{DiffRate}_{\text{disc}} = 0.0000$) because the linear scalar cost $\mathbf{c}_C S$ dominates the continuous valuation utility across matched pairs ($|\Delta S| \le 0.02$).
   - Between $\gamma_C = 1.00$ and $\gamma_C = 1.50$, directional utility perturbation overtakes the scalar cost differential.
   - At $\gamma_C = 1.50$, differentiation abruptly manifests at $\text{DiffRate}_{\text{disc}}(C2) = 0.7989$ ($79.89\%$, identical to Controls A and B) with directional gain $\Delta_{\text{dir\_gain}} = +0.7989$.
   - At $\gamma_C = 2.00$, differentiation saturates to $1.0000$ ($100.00\%$).
   - The transition threshold is pre-registered and bounded within the interval **$[1.0, 1.5]$**.
2. **Consumer D 2D Parameter Sensitivity & Extreme Brittleness (`DISCRETE_QUALIFYING_REGIME_OBSERVED`)**:
   - Across 29 of the 30 evaluated parameter cells ($96.67\%$), directional differentiation remains strictly zero ($\text{DiffRate}_{\text{disc}} = 0.0000$).
   - Exactly **one discrete parameter cell** qualifies:
     $$\mu_d = 1.00, \quad \gamma_\kappa = 0.50 \implies \text{DiffRate}_{\text{disc}}(C2) = 0.7989, \quad \Delta_{\text{dir\_gain}} = +0.7989$$
   - This single qualifying cell represents an extreme corner where directional coupling is maximized ($\mu_d = 1.00$, a $5\times$ amplification over baseline) and scalar non-linear sensitivity is halved ($\gamma_\kappa = 0.50$).
   - In all other regimes—even at $\mu_d = 1.00$ with baseline scalar slope ($\gamma_\kappa = 1.00$)—the steep non-linear scalar baseline overwhelms directional separation.
3. **Attribution Analysis (Functional Form vs. Parameter Regime)**:
   - For **Consumer C**, the failure of transfer in the previous study was **parameter-regime dependent**: the functional form accommodates directional differentiation once directional scaling exceeds $\gamma_C \approx 1.25$.
   - For **Consumer D**, evidence within the evaluated parameter grid indicates that the magnitude-dominant formulation strongly suppresses directional differentiation across 96.7% of surveyed parameter cells, qualifying only under an extreme joint parameter setting ($\mu_d = 1.00, \gamma_\kappa = 0.50$).
4. **Epistemological Guard Against Invalid Architecture Inference**:
   - **Crucial Principle**: *Observing a parameter region where R3 produces downstream behavioral differentiation does NOT prove that a real Lucia production consumer should operate in that region.*
   - Artificially amplifying directional gain or dampening scalar urgency to force downstream differentiation would invert cognitive architecture governance. Production action valuation must serve genuine homeostatic and communicative utility, not act as an amplifier fixture to validate an upstream research representation.
5. **Governance & Milestone Assertion**:
   - The Architecture Gate remains **`STRICTLY LOCKED`** (`production diff = 0`).
   - Quality Gate 2 remains **`STRICTLY BLOCKED`** ($\Delta_{\text{HM}} = 0.0685 < 0.1500$).
   - ADR-029 remains **`DRAFT / RESEARCH RECORD ONLY / NOT RATIFIED`**.
   - Phase 22 H1 remains **`INCONCLUSIVE`**.

---

## 2. Governance Status & Boundary Invariants

| Governance Metric | Canonical Specification | Evaluated Invariant Status |
|---|---|---|
| **Phase 22 H1 Status** | Protocol v1.4 Benchmark | **INCONCLUSIVE** (Cannot be reopened by behavioral sweeps) |
| **Quality Gate 2 Status** | Preregistered Criterion | **STRICTLY BLOCKED** ($\Delta_{\text{HM}} = 0.0685 < 0.1500$) |
| **Production Architecture Gate** | Architecture Design Gate | **STRICTLY LOCKED** (Zero production commits authorized) |
| **ADR-029 Status** | Technical Ledger §8.0 | **`DRAFT / RESEARCH RECORD ONLY / NOT RATIFIED`** |
| **Production Code Mutations** | `src/core/**`, `src/api/**`, `electron/**` | **0 modifications** (`git diff --stat` is bit-exact empty) |
| **Genesis Onboarding State** | `data/profile.json` | Bit-exact `{"is_onboarded": false}` preserved |
| **Stimulus Corpus Lineage** | Frozen Candidate G1 Corpus | $N=270$, Master Seed 9999, 90/tier |
| **Hardware Execution** | 20-Watt Whole Brain Architecture | **100% CPU Execution / 0.0 MB GPU VRAM Allocation** |

---

## 3. Epistemic Scope Clarification

To prevent conceptual drift and adhere to `AGENTS.md` research governance, the project enforces a strict taxonomy:

```text
[Research Simulation Harness]
38-Regime Parameter Sensitivity Sweep (C: 8 levels, D: 30 cells)
Tested across systematic directional/scalar gain variations
               │
               ▼
[Empirical Observation]
Consumer C: Transitions in [1.0, 1.5]; qualifies for \gamma_C \ge 1.50
Consumer D: Qualifies strictly at 1 / 30 cells (\mu_d = 1.00, \gamma_\kappa = 0.50)
               │
               ▼
[Epistemic Boundary: CANNOT CLAIM]
"Universal Robustness of R3"
"Proof that Production Consumer Should Use \gamma_C = 1.50 or \mu_d = 1.00"
"Resolution of ADR-029 or Admission into Production"
"Override of Quality Gate 2"
```

The mathematical behavior observed in these sweeps characterizes the **transferability envelope** of R3 within synthetic research formulations. It demonstrates that R3 differentiation is not a unique mathematical fluke of the historical EFE adapter, but is instead achievable within varied functional structures—provided directional valuation is given sufficient relative economic weight. However, this finding is **strictly a property of the evaluated research harness** and does not constitute evidence of production viability.

---

## 4. Pre-Registered Parameter Grids & Frozen Base Parameters

All sweep regimes operate over the canonical 6-action vocabulary:
$$\mathcal{A} = \{\text{answer (A1)}, \text{clarify (A2)}, \text{retrieve (A3)}, \text{derive (A4)}, \text{reason (A5)}, \text{wait (A6)}\}$$
with deadband $\epsilon = 0.010$, ternary coordinates $\mathbf{d} = \operatorname{sign}_\epsilon(\mathbf{r}_T) \in \{-1, 0, +1\}^3$, and unit-scaled direction $\mathbf{d} / \sqrt{3}$.

### 4.1 Cryptographic Parameter Hashes (SHA-256)
All base parameter tensors and matrices were frozen and cryptographically recorded prior to running the sweep:

| Parameter Object | Target Component | SHA-256 Digest |
|---|---|---|
| `C_U_BASE` | Consumer C Base Multiplicative Utility | `68ae10dcd46f2b0d2484466102ab012c056271e92be9a237ae23c7c705f922ec` |
| `C_COST_S` | Consumer C Linear Scalar Cost Vector | `3a08599cb76d748fece9a2c34f35e961f96e4ce6529cc718a422ce6914934543` |
| `C_M_BASE` | Consumer C Base Directional Coupling Matrix | `08cc42e3b61c467ee7e9a9bed9eab06b471ad338833fdb145d267da89ab8118c` |
| `D_G_BASE` | Consumer D Base Action Cost Baseline | `b6eca7ed83efe37dd754fc8a20763b698d11b5533d30a367146d3e677b0dfa0e` |
| `D_KAPPA_S_BASE` | Consumer D Base Scalar Slope Multipliers | `c2b412f75adb709602a7861fbdd9ddeb3742fe3983cbe39f2b1865f9ea0f1cff` |
| `D_W_DIR` | Consumer D Base Directional Coupling Matrix | `3ca626f22561efd324b3e353650a5ae3ab9fe514b24ae0f2fc6c4f8f83bc0615` |

### 4.2 Pre-Registered Parameter Grids
1. **Consumer C (Continuous Multiplicative Utility)**:
   - Valuation: $U(a) = U_{\text{base}}(a) \cdot \exp\left(\gamma_C \cdot \mathbf{M}_{C, \text{base}}(a, :) \cdot \frac{\mathbf{d}}{\sqrt{3}}\right) - c_{S}(a) \cdot S$
   - Parameter sweep: $\gamma_C \in \{0.10, 0.20, 0.35, 0.50, 0.75, 1.00, 1.50, 2.00\}$ (8 levels).
   - Historical baseline: $\gamma_C = 1.00$.
2. **Consumer D (Magnitude-Dominant Non-Linear Form)**:
   - Valuation: $G_D(a) = G_{\text{base}}(a) + \gamma_\kappa \cdot \boldsymbol{\kappa}_{S, \text{base}}(a) \cdot \tanh(3S) - \mu_d \cdot \mathbf{W}_D(a, :) \cdot \frac{\mathbf{d}}{\sqrt{3}}$
   - Directional coupling sweep: $\mu_d \in \{0.20, 0.30, 0.40, 0.50, 0.70, 1.00\}$ (6 levels).
   - Scalar slope multiplier sweep: $\gamma_\kappa \in \{0.50, 0.75, 1.00, 1.25, 1.50\}$ (5 levels).
   - Total 2D parameter grid: $6 \times 5 = 30$ cells.
   - Historical baseline: $\mu_d = 0.20, \gamma_\kappa = 1.00$.
3. **Reference Controls**:
   - `A_REFERENCE` (Historical EFE Adapter, lower is better).
   - `B_DIRECTIONAL_SEPARABLE` (Additive linear-quadratic cost, lower is better).
   - Total evaluated regimes: $8 + 30 + 2 = 40$ regimes.

---

## 5. Evaluation Methodology, Dataset Lineage & Null Invariants

### 5.1 Dataset Lineage & Matched Pairs
The study utilizes the single immutable frozen Candidate G1 stimulus corpus ($N=270$, Master Seed 9999):
- Low Tier ($S \in [0.10, 0.30]$): 90 probes.
- Medium Tier ($S \in [0.40, 0.60]$): 90 probes.
- High Tier ($S \in [0.70, 0.90]$): 90 probes.
- Total matched pairs ($|S_i - S_j| \le 0.02$): **6,734 pairs**.
- **Discordant matched pairs** ($|S_i - S_j| \le 0.02, \mathbf{d}_i \ne \mathbf{d}_j$): **358 pairs** (primary evaluation set).
- **Same-direction matched pairs** ($|S_i - S_j| \le 0.02, \mathbf{d}_i == \mathbf{d}_j$): **6,376 pairs** (control set).

### 5.2 Deterministic Null Controls & Parity Invariants
1. **Directional Null Consistency (NC1)**:
   NC1 is an empirical scalar-control baseline evaluated on the pre-registered matched-pair partition ($|S_i - S_j| \le 0.02$ under Condition C0); identical-$S$ cases are additionally reported as a descriptive null check ($D_{\text{pair\_action}}(C0) = 0.0000$). Hard invariant remains strictly identical $(S, \mathbf{d})$ tuple parity (NC2).
2. **Hard Tuple Identity Parity (NC2)**:
   For any synthetic identical tuple $(S, \mathbf{d})$, deterministic evaluation must produce bit-exact action identity:
   $$\Delta_{\text{action\_identity}} = 0.0000, \quad D_{\text{JS\_identity}} < 10^{-12}$$
   *Result*: Evaluated across all 38 sweep regimes and both controls $\rightarrow$ **100% PASS** ($0 / 38$ violations).
3. **Same-Direction Parity Scope (NC3)**:
   NC3 hard parity is evaluated strictly on matched pairs with identical $(S, \mathbf{d})$ tuples ($\Delta_{\text{action}} = 0.0000$). Pairs sharing direction but differing in scalar magnitude ($0 < |S_i - S_j| \le 0.02$) are reported descriptively, as valid scalar-dependent cost shifts can legitimately alter discrete action selection.

### 5.3 Pre-Registered Transfer Criteria
A parameter regime is classified as **`QUALIFIES`** if and only if both primary criteria are satisfied simultaneously:
1. **Primary Criterion 1**: $\text{DiffRate}_{\text{disc}}(C2) \ge 0.2000$ ($20.00\%$ differentiation on discordant matched pairs).
2. **Primary Criterion 2**: $\Delta_{\text{dir\_gain}} = \text{DiffRate}_{\text{disc}}(C2) - D_{\text{pair\_action}}(C0) \ge 0.1000$ ($10.00\%$ incremental gain above scalar baseline).

---

## 6. Control Baseline Historical Reproduction

Both reference controls reproduced their historical transferability metrics bit-exact:

| Control Baseline | $\text{DiffRate}_{\text{disc}}(C2)$ | $\Delta_{\text{dir\_gain}}$ | $D_{\text{pair\_action}}(C0)$ | Condition Shift $C2 \to C4$ | Verdict |
|---|---|---|---|---|---|
| `A_REFERENCE` | $0.7989$ | $+0.7989$ | $0.0000$ | $0.2859$ | **QUALIFIES (Bit-exact match)** |
| `B_DIRECTIONAL_SEPARABLE` | $0.7989$ | $+0.7989$ | $0.0000$ | $0.2622$ | **QUALIFIES (Bit-exact match)** |

---

## 7. Consumer C Parameter Sensitivity Sweep Results

Consumer C was evaluated across 8 pre-registered levels of directional gain $\gamma_C \in [0.10, 2.00]$:

| Regime ID | $\gamma_C$ | Is Hist. Ref. | $\text{DiffRate}_{\text{disc}}(C2)$ | $\Delta_{\text{dir\_gain}}$ | $D_{\text{pair}}(C0)$ | Shift $C2 \to C4$ | $\overline{\Delta V}(C2)$ | $\overline{\Delta V}(C0)$ | Status |
|---|---|---|---|---|---|---|---|---|---|
| `C_gamma_0.10` | $0.10$ | False | $0.0000$ | $+0.0000$ | $0.0000$ | $0.0000$ | $0.0674$ | $0.0132$ | **NO** |
| `C_gamma_0.20` | $0.20$ | False | $0.0000$ | $+0.0000$ | $0.0000$ | $0.0000$ | $0.1370$ | $0.0132$ | **NO** |
| `C_gamma_0.35` | $0.35$ | False | $0.0000$ | $+0.0000$ | $0.0000$ | $0.0000$ | $0.2425$ | $0.0132$ | **NO** |
| `C_gamma_0.50` | $0.50$ | False | $0.0000$ | $+0.0000$ | $0.0000$ | $0.0000$ | $0.3489$ | $0.0132$ | **NO** |
| `C_gamma_0.75` | $0.75$ | False | $0.0000$ | $+0.0000$ | $0.0000$ | $0.0000$ | $0.5287$ | $0.0132$ | **NO** |
| `C_gamma_1.00` | $1.00$ | **True** | $0.0000$ | $+0.0000$ | $0.0000$ | $0.0104$ | $0.7123$ | $0.0132$ | **NO** |
| `C_gamma_1.50` | $1.50$ | False | **$0.7989$** | **$+0.7989$** | $0.0000$ | $0.2859$ | $1.0954$ | $0.0132$ | **QUALIFIES** |
| `C_gamma_2.00` | $2.00$ | False | **$1.0000$** | **$+1.0000$** | $0.0000$ | $0.4207$ | $1.5069$ | $0.0132$ | **QUALIFIES** |

### Transition Boundary Analysis:
- **Pre-Registered Transition Extraction Rule**: First adjacent interval $[\gamma_k, \gamma_{k+1}]$ where criteria transition from unfulfilled $\to$ fulfilled.
- **Observed Transition Status**: **`TRANSITION_INTERVAL_OBSERVED`**
- **Transition Interval**: **$[1.00, 1.50]$**
- **Mechanistic Explanation**:
  In Consumer C, continuous utility divergence $\overline{\Delta V}(C2)$ scales monotonically with $\gamma_C$, from $0.0674$ at $\gamma_C = 0.10$ to $0.7123$ at $\gamma_C = 1.00$. However, discrete action selection operates via $\operatorname{argmax}_a U(a)$. Because baseline utility gaps between candidate actions are on the order of $0.80 - 1.00$, continuous utility perturbations cannot flip the argmax action when $\gamma_C \le 1.00$.
  Once $\gamma_C$ reaches $1.50$, $\overline{\Delta V}(C2)$ reaches $1.0954$, exceeding the inter-action baseline utility margins. Directional perturbations begin flipping the dominant action, cleanly recovering $79.89\%$ differentiation. At $\gamma_C = 2.00$, $\overline{\Delta V}(C2) = 1.5069$, and differentiation reaches $100.00\%$.

---

## 8. Consumer D 2D Parameter Sensitivity Surface

Consumer D was evaluated across a full $6 \times 5 = 30$ cell grid spanning directional coupling $\mu_d \in [0.20, 1.00]$ and scalar slope multiplier $\gamma_\kappa \in [0.50, 1.50]$.

### 8.1 Primary Metric Surface ($\text{DiffRate}_{\text{disc}}(C2)$)

| $\mu_d$ \ $\gamma_\kappa$ | $\gamma_\kappa = 0.50$ | $\gamma_\kappa = 0.75$ | $\gamma_\kappa = 1.00$ | $\gamma_\kappa = 1.25$ | $\gamma_\kappa = 1.50$ |
|---|---|---|---|---|---|
| **$\mu_d = 0.20$** | $0.0000$ | $0.0000$ | $0.0000$ (Ref) | $0.0000$ | $0.0000$ |
| **$\mu_d = 0.30$** | $0.0000$ | $0.0000$ | $0.0000$ | $0.0000$ | $0.0000$ |
| **$\mu_d = 0.40$** | $0.0000$ | $0.0000$ | $0.0000$ | $0.0000$ | $0.0000$ |
| **$\mu_d = 0.50$** | $0.0000$ | $0.0000$ | $0.0000$ | $0.0000$ | $0.0000$ |
| **$\mu_d = 0.70$** | $0.0000$ | $0.0000$ | $0.0000$ | $0.0000$ | $0.0000$ |
| **$\mu_d = 1.00$** | **$0.7989$** ★ | $0.0000$ | $0.0000$ | $0.0000$ | $0.0000$ |

★ **Discrete Qualifying Cell**: Exactly **1 of 30 cells** ($3.33\%$) satisfies the pre-registered transfer criteria.

### 8.2 Secondary Metric Surface: Condition Shift ($C2 \to C4$)

While discrete pair differentiation is zero across 29 cells, inspecting the secondary condition-shift metric reveals an underlying continuous sensitivity gradient:

| $\mu_d$ \ $\gamma_\kappa$ | $\gamma_\kappa = 0.50$ | $\gamma_\kappa = 0.75$ | $\gamma_\kappa = 1.00$ | $\gamma_\kappa = 1.25$ | $\gamma_\kappa = 1.50$ |
|---|---|---|---|---|---|
| **$\mu_d = 0.20$** | $0.0000$ | $0.0000$ | $0.0000$ | $0.0000$ | $0.0000$ |
| **$\mu_d = 0.30$** | $0.0000$ | $0.0000$ | $0.0000$ | $0.0000$ | $0.0000$ |
| **$\mu_d = 0.40$** | $0.0000$ | $0.0000$ | $0.0000$ | $0.0000$ | $0.0000$ |
| **$\mu_d = 0.50$** | $0.0000$ | $0.0000$ | $0.0000$ | $0.0000$ | $0.0000$ |
| **$\mu_d = 0.70$** | $0.1185$ | $0.0000$ | $0.0000$ | $0.0000$ | $0.0000$ |
| **$\mu_d = 1.00$** | **$0.3067$** | $0.0852$ | $0.0148$ | $0.0000$ | $0.0000$ |

### 8.3 Transition Outcome & Discrete Qualifying Regime
- **Pre-Registered Transition Extraction Rule**: Report all discrete qualifying grid cells $(\mu_d, \gamma_\kappa)$; do not fit parametric curves or interpolate across unobserved continuous regions.
- **Observed Transition Status**: **`DISCRETE_QUALIFYING_REGIME_OBSERVED`**
- **Qualifying Cells Count**: **1 / 30 cells** ($3.33\%$)
- **Qualifying Cell Set**:
  $$\mathcal{Q}_D = \left\{ (\mu_d = 1.00, \, \gamma_\kappa = 0.50) \right\}$$
- **Detailed Metrics for Qualifying Cell (`D_mu_1.00_gk_0.50`)**:
  - $\text{DiffRate}_{\text{disc}}(C2) = 0.7989$ (PASS $\ge 0.2000$)
  - $\Delta_{\text{dir\_gain}} = +0.7989$ (PASS $\ge 0.1000$)
  - $D_{\text{pair\_action}}(C0) = 0.0000$ (Exact null control preservation)
  - Condition Shift $C2 \to C4 = 0.3067$ (Significant sensitivity to directional coordinate shuffling)
  - Hard Tuple Identity Parity: $\Delta_{\text{action\_identity}} = 0.0000, D_{\text{JS\_identity}} < 10^{-12}$ (PASS)
- **Mechanistic Interpretation of Consumer D Brittleness**:
  In Consumer D, action costs are driven by a steep non-linear hyperbolic tangent term:
  $$G_{\text{scalar}}(a) = \gamma_\kappa \cdot \boldsymbol{\kappa}_{S, \text{base}}(a) \cdot \tanh(3S)$$
  Because $\boldsymbol{\kappa}_{S, \text{base}}$ ranges up to $5.50$ across actions, even small differences in $S$ within the matched-pair tolerance ($|\Delta S| \le 0.02$) generate cost variations that overwhelm linear directional shifts $-\mu_d \mathbf{W}_D \mathbf{d}$.
  Directional differentiation emerges **only when two simultaneous conditions are met**:
  1. Directional coupling $\mu_d$ is forced to its upper boundary ($1.00$, a $5\times$ increase over the baseline specification).
  2. Scalar slope multiplier $\gamma_\kappa$ is halved ($0.50$), suppressing the steepness of the non-linear barrier.
  If scalar slope is maintained at its baseline ($\gamma_\kappa = 1.00$), even $\mu_d = 1.00$ fails to produce differentiation ($\text{DiffRate} = 0.0000$, condition shift $= 0.0148$).

---

## 9. Robustness Envelope Characterization

The empirical results define explicit parameter boundaries for R3 directional differentiation across the evaluated formulations:

```
[Parameter Robustness Envelopes]

Consumer C (Continuous Utility):
  Unfulfilled Grid Cells: \gamma_C \in \{0.10, 0.20, 0.35, 0.50, 0.75, 1.00\} (0.00% differentiation)
  Transition Interval:    \gamma_C \in [1.00, 1.50]
  Qualifying Grid Region: \gamma_C \in \{1.50, 2.00\} (79.89% - 100.00% differentiation)

Consumer D (Magnitude-Dominant Non-Linear):
  Unfulfilled Grid Cells: 29 / 30 cells (0.00% differentiation)
  Qualifying Grid Cell:   Strictly {(\mu_d = 1.00, \gamma_\kappa = 0.50)} (Single isolated corner)
```

### Contrast Between Robustness Envelope and Universal Robustness
- **Universal Robustness (REJECTED)**:
  R3 directional differentiation is **not universally robust**. An agent or consumer cannot simply plug in R3 with arbitrary scaling and expect downstream behavioral differentiation. Under low directional weights ($\gamma_C \le 1.00$) or moderate-to-high scalar damping ($\gamma_\kappa \ge 0.75$), directional information is completely swallowed by discrete argmax selection.
- **Robustness Envelope (CHARACTERIZED)**:
  R3 differentiation is a **regime-conditional property**. It exists within a well-defined parametric subspace where the ratio of directional valuation power to inter-action baseline margins is sufficiently large ($\Delta V_{\text{dir}} / \Delta V_{\text{base}} \ge 1.0$).

---

## 10. Attribution: Functional-Form vs. Parameter-Regime Dependence

By systematically testing sweeps across both consumers, the study resolves the attribution question posed in the mission:

| Consumer | Primary Dependence Type | Attribution Evidence |
|---|---|---|
| **Consumer C** | **Parameter-Regime Dependent** | The functional form (multiplicative exponential utility) is receptive to directional modulation within the evaluated grid. Differentiation failed in the previous study solely because the frozen parameter $\gamma_C = 1.00$ fell below the discrete argmax transition interval ($[1.0, 1.5]$). Within the evaluated grid, differentiation qualifies at $\gamma_C = 1.50$ and $2.00$, defining an observed upper-grid qualifying region. |
| **Consumer D** | **Grid-Bound / Regime-Bound Evidence** | The non-linear hyperbolic magnitude-dominant formulation strongly suppresses directional modulation across 96.7% of the evaluated grid (29/30 cells). Differentiation emerges only under an extreme joint parameter setting ($\mu_d = 1.00, \gamma_\kappa = 0.50$), providing evidence, within the evaluated parameter grid, that the magnitude-dominant formulation strongly suppresses directional differentiation. |

---

## 11. Crucial Guard Against Invalid Architecture Inference

> [!CAUTION]
> **CRITICAL ARCHITECTURAL WARNING**:  
> Finding a parameter region where R3 produces downstream behavioral differentiation **DOES NOT** prove that a real Lucia production consumer should operate in that region.

An agent or developer reviewing these results might be tempted to argue:
> *"Consumer C differentiates at $\gamma_C = 1.50$ and Consumer D differentiates at $(\mu_d=1.00, \gamma_\kappa=0.50)$, so we should simply configure Lucia's downstream action selection to use those parameter regimes!"*

This deduction is **epistemologically fallacious and architecturally forbidden**:
1. **Inversion of Architectural Priority (Tail Wagging the Dog)**:
   A downstream consumer in Lucia (such as Active Inference action selection in Layer 4 or Presence Orchestration in Layer 6) exists to achieve conversational coherence, emotional homeostasis, and task utility. Tuning consumer parameters to hyper-magnify directional sensitivity merely to force an upstream limbic representation to manifest downstream is an artificial distortion of system purpose.
2. **Distortion of Cognitive Economics**:
   In Consumer D, reducing $\gamma_\kappa$ to $0.50$ and setting $\mu_d = 1.00$ cripples the consumer's ability to respond urgently to extreme scalar metabolic arousal, sacrificing homeostatic protection solely to permit subtle directional nuances to register. In a live system, such parameter skew could lead to catastrophic conversational perseveration under cognitive overload.
3. **Research Harness vs. Production Reality**:
   The evaluated consumers are stylized mathematical probes designed to characterize parameter boundaries. They are not calibrated against human perceptual satisfaction, conversational turn-taking SLAs, or affective resonance.

---

## 12. Final Synthesis & Authoritative Research Decision

### Core Question Answered:
> **Question**: *Does empirical evidence indicate that the adapter dependence observed in the transferability study is primarily functional-form-dependent, parameter-regime-dependent, or unresolved under the evaluated grid?*

**Authoritative Scientific Answer**:
The empirical evidence indicates that adapter dependence is **bifurcated across functional archetypes**:
1. In **smooth continuous utility formulations (Consumer C)**, adapter dependence is **parameter-regime dependent**: within the evaluated grid, directional differentiation qualifies at $\gamma_C = 1.50$ and $2.00$, defining an observed upper-grid qualifying region once directional scaling crosses the transition interval ($[1.0, 1.5]$).
2. In **steep non-linear magnitude-dominant formulations (Consumer D)**, adapter dependence is supported by **grid-bound evidence of strong directional suppression**: the formulation suppresses directional differentiation across 96.7% of the evaluated grid (29 of 30 cells), qualifying only under an extreme joint parameter setting ($\mu_d = 1.00, \gamma_\kappa = 0.50$).

### Final Governance Ledger:
- **Phase 22 H1**: Remains **`INCONCLUSIVE`** as governed by Protocol v1.4.
- **Quality Gate 2**: Remains **`STRICTLY BLOCKED`** ($\Delta_{\text{HM}} = 0.0685 < 0.1500$).
- **ADR-029**: Retains status **`DRAFT / RESEARCH RECORD ONLY / NOT RATIFIED`** in `docs/ARCHITECTURE.md` §8.0.
- **Production Architecture Gate**: Remains **`STRICTLY LOCKED`** (`production diff = 0`).
- **Genesis Onboarding**: Preserved bit-exact `{"is_onboarded": false}`.
- **Next Research Milestone**: Any future investigation of R3 must address whether biologically plausible or conversational consumers legitimately inhabit parameter regimes where directional valuation is economically viable, rather than assuming that downstream consumers can be arbitrarily tuned to accommodate upstream representations.
