# Phase 22 H1 — R3 Consumer Plausibility & Utility-Compatibility Study

> **Status:** RESEARCH EVIDENCE RECORD — ARCHITECTURE GATE STRICTLY LOCKED  
> **Governance Invariants:** Phase 22 H1 is **INCONCLUSIVE** | Quality Gate 2 is **STRICTLY BLOCKED** ($\Delta_{\text{HM}} = 0.0685 < 0.1500$)  
> **ADR-029 Status:** **`DRAFT / RESEARCH RECORD ONLY / NOT RATIFIED`**  
> **Production Admission:** **NOT ADMITTED** (Zero mutations to `src/core/**`, `src/api/**`, `electron/**`)  
> **Genesis Gate:** `data/profile.json` preserved bit-exact `{"is_onboarded": false}`  
> **Scope:** Evaluates behavioral preservation and objective compatibility of previously observed qualifying regimes (`C: γ_C ∈ {1.50, 2.00}` and `D: (μ_d=1.00, γ_κ=0.50)`)  
> **Hardware Discipline:** 100% CPU Execution / 0.0 MB GPU VRAM Allocation  
> **Date:** September 2026  
> **Artifact Type:** Formal Research Plausibility & Compatibility Report (Phase 22 H1)

---

## 1. Executive Summary

This study establishes the **Phase 22 H1 R3 Consumer Plausibility & Utility-Compatibility Investigation**. Having previously mapped the parameter sensitivity envelope of candidate directional representation $R3 = \operatorname{sign}_\epsilon(\mathbf{r}_T) \in \{-1, 0, +1\}^3$ across Consumers C and D, this investigation addresses the central economic and functional question:

> **Are the parameter regimes in which R3 becomes behaviorally visible compatible with the intended utility and homeostatic role of a Lucia downstream consumer, or does achieving R3 differentiation require economically implausible distortion of the consumer's primary objectives?**

The purpose of this study is **NOT** to search for, optimize, or tune new parameter values to make R3 work. Instead, it treats the previously observed qualifying regimes as fixed historical observations and measures whether their non-directional (scalar, homeostatic, urgency) properties are preserved, attenuated, or destabilized.

```
                      [R3 Plausibility & Compatibility Matrix]
                                         │
        ┌────────────────────────────────┴────────────────────────────────┐
        ▼                                                                 ▼
[Consumer C: Multiplicative Utility]                   [Consumer D: Magnitude-Dominant]
Regimes: C_base (1.00), C_1.50, C_2.00                 Regimes: D_base (0.20, 1.00), D_corner (1.00, 0.50)
C_1.50: D_disc=79.89%, DirFlips=17.04%, Urg=100%       D_corner: D_disc=79.89%, DirFlips=82.96%, TV=82.96%
C_2.00: D_disc=100%, DirFlips=33.33%, Urg=51.11%      Attribution: Severe Macro-Distribution Shift
Status: Differentiated Homeostatic Preservation        Status: High Disruption / Parameter Skew Required
```

### Core Empirical Findings:
1. **Consumer C $\gamma_C = 1.50$: Coherent Differentiation with Homeostatic Preservation**:
   - At $\gamma_C = 1.50$, R3 produces $\text{DiffRate}_{\text{disc}}(C2) = 0.7989$ ($79.89\%$) and directional gain $\Delta_{\text{dir\_gain}} = +0.7989$, while flipping only $17.04\%$ ($46 / 270$) of total corpus actions away from the scalar baseline.
   - **Primary Objective Preservation**: Scalar $C0$ action stability is $1.0000$ ($100\%$). High-tier urgency action dominance (`answer`, `clarify`, `wait`) remains **$100.00\%$** (urgency frequency shift: $0.00\%$). Action distribution Total Variation (TV) shift is modest ($0.1704$).
   - *Epistemic Finding*: Within the evaluated grid, $\gamma_C = 1.50$ represents a regime where directional modulation becomes behaviorally visible without sacrificing the consumer's primary scalar urgency response.
2. **Consumer C $\gamma_C = 2.00$: Directional Saturation with Urgency Degradation**:
   - At $\gamma_C = 2.00$, differentiation saturates to $\text{DiffRate}_{\text{disc}}(C2) = 1.0000$ ($100\%$) and flips $33.33\%$ ($90 / 270$) of corpus actions.
   - **Primary Objective Disruption**: High-tier urgency action selection **collapses from $100.00\%$ down to $51.11\%$** (an urgency loss of $-48.89\%$). The high-tier action ranking correlation turns strongly negative ($\rho_s = -0.8286$).
   - *Epistemic Finding*: Excessive directional gain begins to distort the consumer's primary homeostatic objective, sacrificing defensive action selection under high cognitive arousal.
3. **Consumer D Qualifying Corner $(\mu_d = 1.00, \gamma_\kappa = 0.50)$: Macro-Distribution Disruption**:
   - At the isolated qualifying corner, R3 achieves $\text{DiffRate}_{\text{disc}}(C2) = 0.7989$.
   - **Severe Distributional Shift**: Directional perturbations flip **$82.96\%$** ($224 / 270$) of all actions away from the scalar baseline. Corpus-level action distribution shifts by $\text{TV} = 0.8296$ ($\text{JS} = 0.4503$).
   - **Decomposition of the Two-Step Parameter Shift (RQ2)**:
     - Halving scalar slope alone ($\gamma_\kappa: 1.0 \to 0.5, \mu_d = 0.20$) produces $\text{DiffRate} = 0.0000$, $\text{DirFlips} = 0.00\%$, and $\text{TV} = 0.0000$.
     - Multiplying directional coupling by $5\times$ alone ($\mu_d: 0.20 \to 1.00, \gamma_\kappa = 1.00$) produces $\text{DiffRate} = 0.0000$, $\text{DirFlips} = 3.70\%$, and $\text{TV} = 0.0370$.
     - *Empirical Consequence*: Neither parameter shift alone enables R3 differentiation. Only their joint, extreme combination allows R3 to emerge, but at the cost of fundamentally altering $83\%$ of the consumer's action profile.
4. **Mandatory Guard Against Architecture Overclaim**:
   - *This study does NOT establish biological plausibility, conversational validity, production compatibility, or R3 architectural readiness.*
   - Measuring that $\gamma_C = 1.50$ preserves high-tier urgency while differentiating discordant pairs is an **empirical observation within a synthetic research harness**, not proof that a production cognitive architecture should adopt this consumer.

---

## 2. Governance Status & Boundary Invariants

| Governance Metric | Target Canonical Specification | Evaluated Invariant Status |
|---|---|---|
| **Phase 22 H1 Status** | Protocol v1.4 Benchmark | **INCONCLUSIVE** (Cannot be reopened by behavioral sweeps) |
| **Quality Gate 2 Status** | Preregistered Criterion | **STRICTLY BLOCKED** ($\Delta_{\text{HM}} = 0.0685 < 0.1500$) |
| **Production Architecture Gate** | Architecture Design Gate | **STRICTLY LOCKED** (Zero production commits authorized) |
| **ADR-029 Status** | Technical Ledger §8.0 | **`DRAFT / RESEARCH RECORD ONLY / NOT RATIFIED`** |
| **Production Code Modifications** | `src/core/**`, `src/api/**`, `electron/**` | **0 modifications** (`git diff --stat` is bit-exact empty) |
| **Genesis Onboarding State** | `data/profile.json` | Bit-exact `{"is_onboarded": false}` preserved |
| **Stimulus Corpus Lineage** | Frozen Candidate G1 Corpus | $N=270$, Master Seed 9999, 90/tier |
| **Parameter Search Policy** | Optimization / Tuning | **STRICTLY PROHIBITED** (Zero new search or tuning) |
| **Hardware Execution** | 20-Watt Whole Brain Architecture | **100% CPU Execution / 0.0 MB GPU VRAM Allocation** |

---

## 3. Core Research Questions

### RQ1 — Directional Benefit vs. Primary Utility Cost
*When a qualifying R3 regime is used, how much additional directional behavioral differentiation is obtained, and what measurable change occurs in the consumer's primary scalar/homeostatic behavior?*

### RQ2 — Does R3 Visibility Require Sacrificing Scalar Responsiveness?
*For each qualifying regime, evaluate whether R3 differentiation is accompanied by attenuation, inversion, or destabilization of scalar urgency behavior. Explicitly decompose Consumer D's parameter shifts ($\gamma_\kappa: 1.0 \to 0.5$ and $\mu_d: 0.20 \to 1.00$).*

### RQ3 — Is the Qualifying Region Behaviorally Distinct or Merely Numerically Stronger?
*Determine whether qualifying regimes preserve the qualitative ordering of consumer responses under scalar stress across Low, Medium, and High $S$. Distinguish between functional coherence and directional overwriting.*

### RQ4 — Research-Harness Compatibility Envelope
*Characterize qualifying regimes along Axis A (R3 Behavioral Visibility) and Axis B (Primary Consumer Behavior Preservation) using pre-registered descriptive metrics.*

---

## 4. Evidence Chain Context

The study situates itself strictly within the chronological Phase 22 H1 research progression:

```text
Phase 22 H1 Empirical Dynamical Headroom Study
       │ (H(12) = 0.2574, Delta_HM = 0.0685 < 0.1500 -> Gate 2 Blocked)
       ▼
Phase 22 H1 R3 Measurement Architecture & Behavioral Utility
       │ (C0 D=0.00%, C2 differentiates 79.89% of discordant matched pairs)
       ▼
Phase 22 H1 R3 Consumer Transferability & Adapter Dependence Study
       │ (R_transfer = 1/3; transfers to B, fails on C & D baselines)
       ▼
Phase 22 H1 R3 Consumer Sensitivity & Robustness Envelope Study
       │ (Transition observed in C at [1.0, 1.5]; D qualifies only at isolated corner)
       ▼
THIS STUDY: Phase 22 H1 R3 Consumer Plausibility & Utility Compatibility
       │ (Evaluates whether qualifying regimes distort primary non-directional objectives)
       ▼
[Future Gate: Only if Authorized by Project Governance]
```

---

## 5. Frozen Evidence Inputs

- **Stimulus Corpus**: Candidate G1 Corpus ($N=270$, Master Seed 9999, 90 Low, 90 Med, 90 High).
- **Matched Pairs**: 6,734 total pairs ($|\Delta S| \le 0.020$).
  - Discordant pairs ($\mathbf{d}_i \ne \mathbf{d}_j$): **358 pairs**.
  - Same-direction pairs ($\mathbf{d}_i == \mathbf{d}_j$): **6,376 pairs**.
- **Exposure Time**: $T = 12$ fast-loop FastLimbicCore ODE steps.
- **Deadband**: $\epsilon = 0.010$.
- **Consumer Random Seeds**: `42, 43, 44, 45, 46`.
- **Base Parameter Hashes (SHA-256)**:
  - `C_U_BASE`: `68ae10dcd46f2b0d2484466102ab012c056271e92be9a237ae23c7c705f922ec`
  - `C_COST_S`: `3a08599cb76d748fece9a2c34f35e961f96e4ce6529cc718a422ce6914934543`
  - `C_M_BASE`: `08cc42e3b61c467ee7e9a9bed9eab06b471ad338833fdb145d267da89ab8118c`
  - `D_G_BASE`: `b6eca7ed83efe37dd754fc8a20763b698d11b5533d30a367146d3e677b0dfa0e`
  - `D_KAPPA_S_BASE`: `c2b412f75adb709602a7861fbdd9ddeb3742fe3983cbe39f2b1865f9ea0f1cff`
  - `D_W_DIR`: `3ca626f22561efd324b3e353650a5ae3ab9fe514b24ae0f2fc6c4f8f83bc0615`

---

## 6. Evaluated Regimes

The study evaluates 7 target regimes plus 2 intermediate counterfactual diagnostics:

1. `A_REFERENCE`: Historical Linear EFE Reference Adapter.
2. `B_DIRECTIONAL_SEPARABLE`: Additive Linear-Quadratic Cost Model.
3. `C_baseline`: Continuous Utility baseline ($\gamma_C = 1.00$).
4. `C_qual_1.50`: Upper-grid qualifying cell ($\gamma_C = 1.50$).
5. `C_qual_2.00`: Upper-grid qualifying cell ($\gamma_C = 2.00$).
6. `D_baseline`: Magnitude-dominant baseline ($\mu_d = 0.20, \gamma_\kappa = 1.00$).
7. `D_qual_corner`: Isolated qualifying corner ($\mu_d = 1.00, \gamma_\kappa = 0.50$).
8. *Diagnostic Diagnostic 1*: `D_scalar_half` ($\mu_d = 0.20, \gamma_\kappa = 0.50$).
9. *Diagnostic Diagnostic 2*: `D_dir_5x` ($\mu_d = 1.00, \gamma_\kappa = 1.00$).

---

## 7. Counterfactual Valuation Decomposition Methodology

For each probe $i \in [1, 270]$, action valuations are decomposed into 4 constituent tiers:
1. $\text{BASE}$: Action baseline values ($U_{\text{base}}$ or $G_{\text{base}}$).
2. $\text{BASE + scalar}$: Condition C0 ($S > 0, \mathbf{d} = \mathbf{0}$).
3. $\text{BASE + directional}$: Evaluated at $S = 0, \mathbf{d} \ne \mathbf{0}$.
4. $\text{BASE + scalar + directional}$: Full Condition C2 ($S > 0, \mathbf{d} \ne \mathbf{0}$).

> [!NOTE]
> **Diagnostic Counterfactual Boundary**:  
> `BASE + directional` (evaluated with $S = 0$ while holding $\mathbf{d} \ne \mathbf{0}$) is a diagnostic counterfactual intervention only. It is not interpreted as a physically realizable limbic state or causal physiological trajectory, as ternary direction $\mathbf{d} = \operatorname{sign}_\epsilon(\mathbf{r}_T)$ is intrinsically derived from residual $\mathbf{r}_T$ which has non-zero magnitude $S = \|\mathbf{r}_T\|_2$.

From these vectors, the engine computes:
- Scalar contribution vector: $\mathbf{v}_{\text{scalar}} = V(\text{BASE+scalar}) - V(\text{BASE})$
- Directional contribution vector: $\mathbf{v}_{\text{dir}} = V(\text{BASE+scalar+dir}) - V(\text{BASE+scalar})$
- Directional Contribution Fraction: $\text{DCF} = \frac{\|\mathbf{v}_{\text{dir}}\|_2}{\|\mathbf{v}_{\text{scalar}}\|_2 + \|\mathbf{v}_{\text{dir}}\|_2 + \epsilon}$
- Directional Action Flip Rate: $\text{DirFlips} = \frac{1}{N}\sum_{i=1}^N \mathbf{1}[a^*(\text{BASE+scalar+dir}) \ne a^*(\text{BASE+scalar})]$

---

## 8. Summary Table of Empirical Measurements

| Regime ID | $\text{DiffRate}_{\text{disc}}(C2)$ | $\Delta_{\text{dir\_gain}}$ | Shift $C2 \to C4$ | $\bar{H}$ (nats) | $\|\mathbf{v}_{\text{scalar}}\|_2$ | $\|\mathbf{v}_{\text{dir}}\|_2$ | Rel. Ratio | DCF | DirFlips | $D_{\text{pair}}(C0)$ |
|---|---|---|---|---|---|---|---|---|---|---|
| `A_REFERENCE` | $0.7989$ | $+0.7989$ | $0.2830$ | $1.6896$ | $0.6006$ | $0.3884$ | $0.6600$ | $0.3948$ | $17.04\%$ | $0.0000$ |
| `B_DIRECTIONAL_SEPARABLE` | $0.7989$ | $+0.7989$ | $0.2585$ | $1.7614$ | $0.4036$ | $0.4884$ | $1.3566$ | $0.5593$ | $82.96\%$ | $0.0000$ |
| `C_baseline` ($\gamma_C=1.00$) | $0.0000$ | $+0.0000$ | $0.0096$ | $1.7597$ | $0.4067$ | $0.5175$ | $1.3540$ | $0.5658$ | $0.00\%$ | $0.0000$ |
| `C_qual_1.50` ($\gamma_C=1.50$) | $0.7989$ | $+0.7989$ | $0.2830$ | $1.7396$ | $0.4067$ | $0.7623$ | $1.9887$ | $0.6562$ | $17.04\%$ | $0.0000$ |
| `C_qual_2.00` ($\gamma_C=2.00$) | $1.0000$ | $+1.0000$ | $0.4289$ | $1.7112$ | $0.4067$ | $1.0131$ | $2.6364$ | $0.7164$ | $33.33\%$ | $0.0000$ |
| `D_baseline` ($\mu_d=0.20, \gamma_\kappa=1.00$) | $0.0000$ | $+0.0000$ | $0.0000$ | $1.4984$ | $4.2304$ | $0.0757$ | $0.0191$ | $0.0188$ | $0.00\%$ | $0.0000$ |
| `D_qual_corner` ($\mu_d=1.00, \gamma_\kappa=0.50$) | $0.7989$ | $+0.7989$ | $0.3141$ | $1.6930$ | $2.1152$ | $0.3787$ | $0.1914$ | $0.1589$ | $82.96\%$ | $0.0000$ |
| `D_scalar_half` ($\mu_d=0.20, \gamma_\kappa=0.50$) | $0.0000$ | $+0.0000$ | $0.0000$ | $1.6782$ | $2.1152$ | $0.0757$ | $0.0383$ | $0.0368$ | $0.00\%$ | $0.0000$ |
| `D_dir_5x` ($\mu_d=1.00, \gamma_\kappa=1.00$) | $0.0000$ | $+0.0000$ | $0.0081$ | $1.5398$ | $4.2304$ | $0.3787$ | $0.0957$ | $0.0868$ | $3.70\%$ | $0.0000$ |

---

## 9. Consumer C Baseline vs. Qualifying Regimes Analysis

### 9.1 Valuation Decomposition & Action Flipping
- In `C_baseline` ($\gamma_C = 1.00$), directional contribution norm is $\|\mathbf{v}_{\text{dir}}\|_2 = 0.5175$. However, this perturbation is insufficient to flip any discrete argmax action ($\text{DirFlips} = 0.00\%$).
- At `C_qual_1.50`, directional norm increases to $\|\mathbf{v}_{\text{dir}}\|_2 = 0.7623$ ($\text{DCF} = 0.6562$). Direction flips exactly **$17.04\%$** ($46 / 270$) of corpus actions away from the scalar baseline.
- At `C_qual_2.00`, directional norm reaches $\|\mathbf{v}_{\text{dir}}\|_2 = 1.0131$ ($\text{DCF} = 0.7164$). Direction flips **$33.33\%$** ($90 / 270$) of corpus actions.

### 9.2 Axis B Primary Objective Preservation
Pairwise comparison against `C_baseline`:

| Metric | `C_baseline vs C_qual_1.50` | `C_baseline vs C_qual_2.00` |
|---|---|---|
| Action Distribution TV Shift | $0.1704$ | $0.3333$ |
| Action Distribution JS Divergence | $0.0630$ | $0.1323$ |
| Scalar C0 Action Stability | **$1.0000$ ($100\%$)** | **$1.0000$ ($100\%$)** |
| Entropy Shift $\Delta \bar{H}$ | $-0.0202$ nats | $-0.0486$ nats |
| Low $S$ Rank Correlation $\rho_s$ | $1.0000$ | $1.0000$ |
| Med $S$ Rank Correlation $\rho_s$ | $1.0000$ | $1.0000$ |
| High $S$ Rank Correlation $\rho_s$ | $+0.0286$ | **$-0.8286$** |
| High $S$ Urgency Dominance Frequency | **$100.00\%$** | **$51.11\%$** |
| High $S$ Urgency Frequency Shift | **$0.00\%$** | **$-48.89\%$** |

### 9.3 Detailed Interpretation:
- **$\gamma_C = 1.50$ is Homeostatically Preserving**: Under High $S$ arousal, the consumer selects urgency actions (`answer`, `clarify`, `wait`) $100\%$ of the time, matching the baseline. Directional nuances operate within the available action subset without eroding defensive homeostatic behavior.
- **$\gamma_C = 2.00$ Disables High-Tier Urgency**: When $\gamma_C$ is pushed to $2.00$, directional perturbations overpower scalar costs in High $S$, causing non-defensive actions (`retrieve`, `derive`, `reason`) to be selected $48.89\%$ of the time under high limbic tension. This creates a severe negative rank correlation ($\rho_s = -0.8286$) with the intended urgency response.

---

## 10. Consumer D Baseline vs. Qualifying Corner Analysis

### 10.1 Valuation Decomposition & Action Flipping
- In `D_baseline` ($\mu_d = 0.20, \gamma_\kappa = 1.00$), scalar contribution norm is overwhelming: $\|\mathbf{v}_{\text{scalar}}\|_2 = 4.2304$, while directional contribution is tiny: $\|\mathbf{v}_{\text{dir}}\|_2 = 0.0757$ ($\text{DCF} = 0.0188$). Direction flips $0.00\%$ of actions.
- At `D_qual_corner` ($\mu_d = 1.00, \gamma_\kappa = 0.50$), scalar norm is cut to $\|\mathbf{v}_{\text{scalar}}\|_2 = 2.1152$, and directional norm increases $5\times$ to $\|\mathbf{v}_{\text{dir}}\|_2 = 0.3787$ ($\text{DCF} = 0.1589$).
- Direction flips **$82.96\%$** ($224 / 270$) of all actions away from the scalar baseline!

### 10.2 Decomposing the Two-Step Parameter Shift (RQ2 Resolution)
To isolate what causes this shift, the two intermediate counterfactuals were evaluated:

| Regime | $\mu_d$ | $\gamma_\kappa$ | $\text{DiffRate}$ | DirFlips | TV Shift vs Base | Mean Tier Rank Corr $\rho_s$ |
|---|---|---|---|---|---|---|
| `D_baseline` | $0.20$ | $1.00$ | $0.0000$ | $0.00\%$ | $0.0000$ | $1.0000$ |
| `D_scalar_half` | $0.20$ | $0.50$ | $0.0000$ | $0.00\%$ | $0.0000$ | $1.0000$ |
| `D_dir_5x` | $1.00$ | $1.00$ | $0.0000$ | $3.70\%$ | $0.0370$ | $0.8095$ |
| `D_qual_corner` | $1.00$ | $0.50$ | **$0.7989$** | **$82.96\%$** | **$0.8296$** | **$0.2381$** |

### 10.3 Definitive Conclusion on Consumer D:
- **Halving scalar slope alone** produces zero directional differentiation ($\text{DiffRate} = 0.0000$) and zero action distribution shift.
- **Multiplying directional coupling by $5\times$ alone** produces zero directional differentiation on discordant pairs ($\text{DiffRate} = 0.0000$) and only a minor $3.7\%$ action flip rate.
- Directional differentiation emerges **only from the non-linear interaction of both shifts**, but this joint distortion causes a massive macro-level action distribution shift ($\text{TV} = 0.8296$).

---

## 11. Scalar Responsiveness & Urgency Analysis

The study tracked the distribution of action choices across scalar tiers (Low $S \in [0.1, 0.3]$, Med $S \in [0.4, 0.6]$, High $S \in [0.7, 0.9]$):

### 11.1 High-Tier Urgency Dominance (A1 `answer`, A2 `clarify`, A6 `wait`)
- `A_REFERENCE`: High tier selects urgency actions $100.00\%$ of the time.
- `B_DIRECTIONAL_SEPARABLE`: High tier selects urgency actions $100.00\%$ of the time.
- `C_baseline`: High tier selects urgency actions $100.00\%$ of the time.
- `C_qual_1.50`: High tier selects urgency actions **$100.00\%$** of the time ($0.00\%$ degradation).
- `C_qual_2.00`: High tier selects urgency actions **$51.11\%$** of the time (**$-48.89\%$ degradation**).
- `D_baseline`: High tier selects urgency actions $100.00\%$ of the time.
- `D_qual_corner`: High tier selects urgency actions $100.00\%$ of the time, but the internal ranking among defensive actions is distorted ($\rho_s = 0.4286$).

---

## 12. Negative Controls & Parity Invariants

All pre-registered negative controls passed 100% across all 9 evaluated regimes:
1. **Directional Null Consistency (NC1)**: Evaluated on the 358 matched discordant pairs under Condition C0 $\rightarrow$ $D_{\text{pair\_action}}(C0) = 0.0000$ across all 9 regimes.
2. **Hard Tuple Identity Parity (NC2)**: Evaluated on synthetic identical $(S, \mathbf{d})$ tuples $\rightarrow$ $\Delta_{\text{action\_identity}} = 0.0000, D_{\text{JS\_identity}} < 10^{-12}$ across all 9 regimes (**100% PASS**).
3. **Same-Direction Pairs (NC3)**: Evaluated descriptively on the 6,376 same-direction matched pairs.
4. **Shuffled Direction Sensitivity (NC4)**: In qualifying regimes, shuffling direction (C4) diverges significantly from C2 ($D_{\text{condition\_action}} = 0.2830$ in C_1.50, $0.3141$ in D_corner).
5. **Historical Reproduction (NC5)**: Reference controls A and B reproduced prior transferability metrics bit-exact ($0.7989$).

---

## 13. Cross-Consumer Comparison

| Dimension | `A_REF` | `B_SEP` | `C_base` | `C_1.50` | `C_2.00` | `D_base` | `D_corner` |
|---|---|---|---|---|---|---|---|
| $\text{DiffRate}_{\text{disc}}(C2)$ | $79.89\%$ | $79.89\%$ | $0.00\%$ | $79.89\%$ | $100.00\%$ | $0.00\%$ | $79.89\%$ |
| $\text{DirFlips}$ (% of 270) | $17.04\%$ | $82.96\%$ | $0.00\%$ | $17.04\%$ | $33.33\%$ | $0.00\%$ | $82.96\%$ |
| $\text{DCF}$ (Norm Ratio) | $0.3948$ | $0.5593$ | $0.5658$ | $0.6562$ | $0.7164$ | $0.0188$ | $0.1589$ |
| High $S$ Urgency Dominance | $100\%$ | $100\%$ | $100\%$ | **$100\%$** | **$51.1\%$** | $100\%$ | $100\%$ |
| Action Dist TV Shift vs Base | Ref | Ref | Ref | $0.1704$ | $0.3333$ | Ref | **$0.8296$** |
| Mean Tier Rank Correlation $\rho_s$ | Ref | Ref | Ref | $0.6762$ | $0.3905$ | Ref | **$0.2381$** |

---

## 14. Epistemic Taxonomy

All findings adhere strictly to pre-registered epistemic categories:
- **`SUPPORTED`**: Mathematical decomposition formulas ($V(\text{BASE+scalar})$, $V(\text{BASE+dir})$) and deterministic identity properties directly implied by frozen code.
- **`OBSERVED`**: Empirical metrics obtained on Candidate G1 corpus ($\text{DiffRate} = 79.89\%$ at C_1.50, High-tier urgency $= 51.11\%$ at C_2.00, $\text{TV} = 82.96\%$ at D_corner).
- **`RESEARCH_HARNESS_ONLY`**: The observation that $\gamma_C = 1.50$ preserves urgency while $\gamma_C = 2.00$ degrades it applies strictly within the stylized research harness.
- **`UNTESTED`**: Biological realism, natural language dialogue impact, user perceptual satisfaction, or production conversational validity.
- **`NOT_JUSTIFIED`**: Any claim that R3 is production-ready, that $\gamma_C = 1.50$ should be used in production, or that ADR-029 should be ratified.

---

## 15. Limitations

1. **Synthetic Stimulus Corpus**: Probes were generated by `GeneratorG1` under controlled conditions, not live user conversation.
2. **Stylized 6-Action Space**: Action choices reflect discrete cognitive categories (`answer`, `clarify`, `retrieve`, `derive`, `reason`, `wait`), not complex production multi-stage generation.
3. **Static Valuation**: Evaluations represent single-turn snapshot choices rather than multi-turn conversational dynamics.
4. **Diagnostic Counterfactual Assumption**: Setting $S = 0$ while holding $\mathbf{d} \ne \mathbf{0}$ is a diagnostic decomposition tool, not an accessible physical trajectory.

---

## 16. Mandatory Negative Interpretation Guard

> [!CAUTION]
> **MANDATORY SCIENTIFIC SAFEGUARD**:  
> This study evaluates whether previously observed qualifying parameter regimes preserve measurable properties of the evaluated research consumers. **It does not establish biological plausibility, conversational validity, production compatibility, or R3 architectural readiness.**

The findings of this study **MUST NOT** be interpreted as:
1. Proof that R3 should or must be promoted to production.
2. Proof that $\gamma_C = 1.50$ or $(\mu_d=1.00, \gamma_\kappa=0.50)$ are biologically correct or optimal parameters.
3. Authorization to configure Lucia's Layer 4 Active Inference or Layer 6 Presence Orchestrator to use these regimes.
4. Proof that Consumer D's non-linear form is universally pathological.
5. Grounds for reopening Phase 22 H1 or ratifying ADR-029.

---

## 17. Authoritative Research Decision

### Core Question Answered:
> **Question**: *Are the parameter regimes in which R3 becomes behaviorally visible compatible with the intended utility and homeostatic role of a Lucia downstream consumer, or does achieving R3 differentiation require economically implausible distortion of the consumer's primary objectives?*

**Authoritative Scientific Answer**:
1. **In Consumer C ($\gamma_C = 1.50$)**: R3 directional differentiation is **behaviorally compatible** with primary homeostatic objectives. Directional nuances flip $17.04\%$ of actions across matched pairs without diminishing the $100\%$ defensive urgency response required under high cognitive stress. However, pushing scaling to $\gamma_C = 2.00$ causes severe homeostatic degradation (cutting urgency selection by $-48.89\%$).
2. **In Consumer D ($(\mu_d = 1.00, \gamma_\kappa = 0.50)$)**: R3 directional differentiation requires an **extreme macro-distributional distortion** ($\text{TV} = 82.96\%$). Differentiation cannot be induced by halving scalar slope alone or multiplying directional gain alone; it manifests only when both distortions are applied jointly, overwriting the consumer's baseline action selection profile.

### Final Governance Ledger:
- **Phase 22 H1**: Remains **`INCONCLUSIVE`** as governed by Protocol v1.4.
- **Quality Gate 2**: Remains **`STRICTLY BLOCKED`** ($\Delta_{\text{HM}} = 0.0685 < 0.1500$).
- **ADR-029**: Retains status **`DRAFT / RESEARCH RECORD ONLY / NOT RATIFIED`** in `docs/ARCHITECTURE.md` §8.0.
- **Production Architecture Gate**: Remains **`STRICTLY LOCKED`** (`production diff = 0`).
- **Genesis Onboarding**: Preserved bit-exact `{"is_onboarded": false}`.
