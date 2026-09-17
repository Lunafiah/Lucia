# Phase 22 H1 — R3 Consumer Transferability & Adapter Dependence Study

> **Status:** RESEARCH EVIDENCE RECORD — ARCHITECTURE GATE STRICTLY LOCKED  
> **Governance Invariants:** Phase 22 H1 is **INCONCLUSIVE** | Quality Gate 2 is **STRICTLY BLOCKED** ($\Delta_{\text{HM}} = 0.0685 < 0.1500$)  
> **ADR-029 Status:** **DRAFT / ARCHIVAL RECORD ONLY / NOT RATIFIED**  
> **Production Admission:** **NOT ADMITTED** (Zero mutations to `src/core/**`, `src/api/**`, `electron/**`)  
> **Genesis Gate:** `data/profile.json` preserved bit-exact `{"is_onboarded": false}`  
> **Pre-Registered Transferability Metric:** $R_{\text{transfer}} = 1/3 = 0.3333$  
> **Scientific Outcome:** **PARTIAL_TRANSFERABILITY_PARTIAL_ADAPTER_DEPENDENCE**  
> **Hardware Discipline:** 100% CPU Execution / 0.0 MB GPU VRAM Allocation  
> **Date:** September 2026  
> **Artifact Type:** Formal Research Transferability & Robustness Report (Phase 22 H1)

---

## 1. Executive Summary

This study establishes the **Phase 22 H1 R3 Consumer Transferability & Adapter Dependence Evaluation**, determining whether the behavioral differentiation previously observed for candidate representation $R3 = \operatorname{sign}_\epsilon(\mathbf{r}_T) \in \{-1, 0, +1\}^3$ is:
1. **robust across independently formulated downstream consumer functional forms**, or
2. **materially dependent on the specific Expected Free Energy (EFE) linear adapter used in the initial behavioral utility study.**

Prior research demonstrated that under the historical reference adapter (`A_REFERENCE`), R3 differentiated $79.89\%$ ($286 / 358$) of canonical scalar-collapsed discordant matched pairs ($|S_i - S_j| \le 0.02, \mathbf{d}_i \ne \mathbf{d}_j$). To resolve the epistemic gap between *measurement evidence*, *single-consumer behavioral evidence*, and *potential architectural evidence*, this study preregistered and froze four distinct consumer formulations representing fundamentally different mathematical paradigms before primary evaluation on the frozen Candidate G1 stimulus corpus ($N=270$, master seed 9999).

### Core Empirical Findings:
1. **Transfer to Separable Cost Model (`B_DIRECTIONAL_SEPARABLE`)**:
   Under an independently formulated additive linear-quadratic cost model featuring convex scalar effort scaling ($S^2$) and an independent directional matrix $\mathbf{W}_B$, directional differentiation transferred cleanly:
   $$\text{DiffRate}_{\text{disc}}(C2) = 0.7989, \quad \Delta_{\text{dir\_gain}} = +0.7989, \quad D_{\text{condition\_action}}(C2, C4) = 0.2622$$
   All four preregistered transfer criteria were satisfied (`TRANSFER_SATISFIED`).
2. **Continuous Utility vs. Discrete Argmax Masking (`C_CONTINUOUS_UTILITY`)**:
   Under a multiplicative exponential utility model ($U = U_{\text{base}} \cdot \exp(\mathbf{M}_d \mathbf{d} / \sqrt{3}) - \mathbf{c} \cdot S$), directional R3 generated massive continuous utility divergence:
   $$\overline{\Delta V}_{\text{pair}}(C2) = 0.7123 \quad (>50\times \text{ higher than scalar baseline } \overline{\Delta V}_{\text{pair}}(C0) = 0.0132)$$
   However, due to the baseline action valuation margin, continuous utility shifts did not flip the discrete argmax action:
   $$\text{DiffRate}_{\text{disc}}(C2) = 0.0000, \quad D_{\text{condition\_action}}(C2, C4) = 0.0104$$
   This resolves **RQ5 (Special C5 Follow-up)**: scalar magnitude produces non-zero continuous utility variation within matched pairs ($\overline{\Delta V} = 0.0132$), but discrete argmax selection masks both scalar and directional continuous utility variation when baseline utility margins exceed directional perturbations.
3. **Magnitude-Dominant Suppression (`D_MAGNITUDE_DOMINANT`)**:
   When scalar slope was intentionally amplified (up to $5.5$) and directional coupling was attenuated ($\mu_d = 0.20$), directional action differentiation collapsed to zero:
   $$\text{DiffRate}_{\text{disc}}(C2) = 0.0000, \quad D_{\text{condition\_action}}(C2, C4) = 0.0000$$
4. **Pre-Registered Transferability Statistic**:
   Across the three independently formulated non-reference consumers $\{B, C, D\}$, exactly $1 / 3$ satisfied the preregistered discrete action differentiation thresholds:
   $$R_{\text{transfer}} = \frac{1}{3} \approx 0.3333 \implies \text{\textbf{PARTIAL\_TRANSFERABILITY\_PARTIAL\_ADAPTER\_DEPENDENCE}}$$
5. **Definitive Scientific Conclusion**:
   > *R3 behavioral differentiation transfers to some independently specified consumers but not others, indicating partial consumer robustness with unresolved adapter dependence. Further architectural interpretation remains premature. ADR-029 remains a research candidate, and Quality Gate 2 remains strictly blocked.*

---

## 2. Governance Status & Boundary Invariants

| Governance Metric | Current Status | Verification Mechanism |
|---|---|---|
| **Phase 22 H1 Status** | **INCONCLUSIVE** | Protocol v1.4 formal benchmark retained bit-exact |
| **Quality Gate 2 Status** | **STRICTLY BLOCKED** | Preregistered criterion unfulfilled ($\Delta_{\text{HM}} = 0.0685 < 0.1500$) |
| **Protocol v1.5** | **NOT AUTHORIZED** | Hard governance manifest assertion |
| **Production Architecture Gate** | **STRICTLY LOCKED** | Zero production commits authorized |
| **ADR-029 Status** | **`DRAFT / RESEARCH RECORD ONLY / NOT RATIFIED`** | Explicit status header in `docs/ARCHITECTURE.md` §8.0 |
| **Production Code Mutations** | **0 modifications** | `git diff --stat src/core/ src/api/ electron/` is empty |
| **Genesis Onboarding State** | Bit-exact `{"is_onboarded": false}` | Cryptographic check on `data/profile.json` |
| **Corpus Lineage** | **Single Immutable Root** | Frozen Candidate G1 Corpus ($N=270$, Master Seed 9999) |
| **Hardware Execution** | **100% CPU / 0.0 MB GPU VRAM** | Local edge execution; zero GPU VRAM allocation |

---

## 3. Epistemic Scope Clarification

To maintain rigorous epistemological discipline, the project establishes a strict semantic distinction:

```text
[Research Simulation Harness]
Independently Formulated Consumers (A, B, C, D)
Tested across varied mathematical functional forms
               │
               ▼
[Observation: R_transfer = 0.3333]
Demonstrates partial mathematical robustness across cost forms;
reveals argmax discretization masking in continuous utility space
               │
               ▼
[Epistemic Boundary: CANNOT CLAIM]
"Independent Production Validation"
"Architectural Proof of R3"
"Ground Truth Affective Recovery"
"Gate 2 Resolution"
```

The consumers evaluated in this study are **independently formulated research consumers**, developed to test whether the discrete action differentiation observed in the historical EFE adapter was an equation-specific mathematical artifact. While differentiation transferred to an additive linear-quadratic cost model (Consumer B), it was suppressed in multiplicative exponential utility (Consumer C) and magnitude-dominant regimes (Consumer D). Consequently, **adapter dependence remains partially unresolved**, and the findings must not be characterized as production or architectural validation.

---

## 4. Pre-Registered Frozen Consumer Specifications

All four consumers operate over the identical 6-action vocabulary:
$$\mathcal{A} = \{\text{answer (A1)}, \text{clarify (A2)}, \text{retrieve (A3)}, \text{derive (A4)}, \text{reason (A5)}, \text{wait (A6)}\}$$
using identical deadband parameters ($\epsilon = 0.010$), identical ternary directional coordinates $\mathbf{d} = \operatorname{sign}_\epsilon(\mathbf{r}_T) \in \{-1, 0, +1\}^3$, and normalized scale vector $\mathbf{d} / \sqrt{3}$.

### 4.1 Consumer A — Reference Consumer (`A_REFERENCE`)
- **Functional Paradigm**: Linear Multi-Objective Expected Free Energy with scalar-modulated epistemic weights.
- **Valuation Formulation**:
  $$G_A(a) = \text{BASE\_COSTS}(a) - \beta_k(S)\text{BASE\_DK}(a) - \beta_m(S)\text{BASE\_DM}(a) - \mathbf{W}_A(a, :) \cdot \frac{\mathbf{d}}{\sqrt{3}}$$
  where $\beta_k(S) = 1.0 + 0.50\tanh(2S)$, $\beta_m(S) = 1.0 + 0.30\tanh(2S)$.
- **Frozen Parameters**:
  - $\text{BASE\_COSTS} = [0.15, 0.45, 0.35, 0.40, 0.60, 0.10]^\top$
  - $\text{BASE\_DK} = [0.05, 0.70, 0.40, 0.50, 0.60, 0.00]^\top$
  - $\text{BASE\_DM} = [0.05, 0.20, 0.65, 0.30, 0.40, 0.00]^\top$
  - $\mathbf{W}_A$ ($6 \times 3$ matrix):
    $$\mathbf{W}_A = \begin{bmatrix}
     0.10 & -0.15 &  0.10 \\
    -0.25 &  0.15 & -0.10 \\
     0.20 & -0.10 &  0.15 \\
     0.10 &  0.15 &  0.10 \\
    -0.15 &  0.25 & -0.15 \\
    -0.10 & -0.20 & -0.20
    \end{bmatrix}$$
- **Action Selection**: $a^* = \operatorname{argmin}_a G_A(a)$, Boltzmann policy $P_A(a) = \operatorname{softmax}(-\gamma G_A(a)), \gamma = 1.0$.

### 4.2 Consumer B — Direction-Separable Cost (`B_DIRECTIONAL_SEPARABLE`)
- **Functional Paradigm**: Additive model with linear and convex quadratic scalar effort cost ($S^2$) and independent linear directional orientation.
- **Valuation Formulation**:
  $$G_B(a) = G_{\text{base}, B}(a) + \boldsymbol{\alpha}_B(a) \cdot S + \boldsymbol{\beta}_B(a) \cdot S^2 - \mathbf{W}_B(a, :) \cdot \frac{\mathbf{d}}{\sqrt{3}}$$
- **Frozen Parameters**:
  - $G_{\text{base}, B} = [0.25, 0.55, 0.45, 0.50, 0.70, 0.20]^\top$
  - $\boldsymbol{\alpha}_B = [-0.10, 0.25, 0.15, 0.20, 0.35, -0.20]^\top$
  - $\boldsymbol{\beta}_B = [0.30, 0.10, 0.20, 0.15, 0.40, 0.50]^\top$
  - $\mathbf{W}_B$ ($6 \times 3$ matrix):
    $$\mathbf{W}_B = \begin{bmatrix}
     0.15 & -0.20 &  0.05 \\
    -0.30 &  0.20 & -0.15 \\
     0.25 & -0.15 &  0.20 \\
     0.05 &  0.20 &  0.15 \\
    -0.20 &  0.30 & -0.10 \\
    -0.15 & -0.25 & -0.25
    \end{bmatrix}$$
- **Action Selection**: $a^* = \operatorname{argmin}_a G_B(a)$, Boltzmann policy $P_B(a) = \operatorname{softmax}(-\gamma G_B(a)), \gamma = 1.0$.

### 4.3 Consumer C — Multiplicative Exponential Utility (`C_CONTINUOUS_UTILITY`)
- **Functional Paradigm**: Multiplicative exponential utility model (microeconomic risk-sensitive utility scaling).
- **Valuation Formulation**:
  $$U_C(a) = U_{\text{base}, C}(a) \cdot \exp\left(\mathbf{M}_C(a, :) \cdot \frac{\mathbf{d}}{\sqrt{3}}\right) - \mathbf{c}_C(a) \cdot S$$
- **Frozen Parameters**:
  - $U_{\text{base}, C} = [1.20, 0.60, 0.80, 0.70, 0.50, 1.10]^\top$
  - $\mathbf{c}_C = [0.40, 0.15, 0.25, 0.30, 0.10, 0.50]^\top$
  - $\mathbf{M}_C$ ($6 \times 3$ matrix):
    $$\mathbf{M}_C = \begin{bmatrix}
     0.25 & -0.30 &  0.15 \\
    -0.35 &  0.30 & -0.20 \\
     0.30 & -0.20 &  0.25 \\
     0.15 &  0.25 &  0.10 \\
    -0.25 &  0.40 & -0.15 \\
    -0.15 & -0.35 & -0.30
    \end{bmatrix}$$
- **Action Selection**: $a^* = \operatorname{argmax}_a U_C(a)$, Boltzmann policy $P_C(a) = \operatorname{softmax}(\gamma U_C(a)), \gamma = 1.0$.
- **Continuous Distance**: $\Delta V_{\text{pair}} = \|\mathbf{U}_C(S_i, \mathbf{d}_i) - \mathbf{U}_C(S_j, \mathbf{d}_j)\|_2$.

### 4.4 Consumer D — Magnitude-Dominant Cost Control (`D_MAGNITUDE_DOMINANT`)
- **Functional Paradigm**: Strongly magnitude-dominant cost model with heavily attenuated directional bias ($\mu_d = 0.20$).
- **Valuation Formulation**:
  $$G_D(a) = G_{\text{base}, D}(a) + \boldsymbol{\kappa}_{S, D}(a) \cdot S - \mu_d \cdot \mathbf{W}_D(a, :) \cdot \frac{\mathbf{d}}{\sqrt{3}}$$
- **Frozen Parameters**:
  - $G_{\text{base}, D} = [0.10, 0.30, 0.20, 0.25, 0.40, 0.05]^\top$
  - $\boldsymbol{\kappa}_{S, D} = [1.50, 4.00, 2.50, 3.00, 5.50, 0.80]^\top$
  - $\mu_d = 0.20$
  - $\mathbf{W}_D$ ($6 \times 3$ matrix):
    $$\mathbf{W}_D = \begin{bmatrix}
     0.10 & -0.15 &  0.10 \\
    -0.20 &  0.15 & -0.10 \\
     0.20 & -0.10 &  0.15 \\
     0.10 &  0.15 &  0.10 \\
    -0.15 &  0.25 & -0.15 \\
    -0.10 & -0.20 & -0.20
    \end{bmatrix}$$
- **Action Selection**: $a^* = \operatorname{argmin}_a G_D(a)$, Boltzmann policy $P_D(a) = \operatorname{softmax}(-\gamma G_D(a)), \gamma = 1.0$.

---

## 5. Corpus Lineage & Matched-Pair Methodology

```text
Frozen Candidate G1 Stimulus Corpus
Master Seed = 9999 | N = 270 (90/tier)
Exposure T = 12 ticks
                 │
                 ▼
Exhaustive Pair Matching (|S_i - S_j| <= 0.02)
Total Matched Pairs = 6,734
                 │
        ┌────────┴────────┐
        ▼                 ▼
Same-Direction     Discordant-Direction
d_i == d_j         d_i != d_j
N = 6,376          N = 358 (Canonical Collapse Set)
```

- **Candidate G1 Corpus**: Master Seed `9999`, generated via `GeneratorG1` and encoded by `StimulusProcessor`.
- **Consumer Robustness Seeds**: Seeds `42, 43, 44, 45, 46` strictly govern consumer tie-breaking micro-noise $\mathcal{N}(0, 10^{-6})$ and C4 permutation ordering.
- **Matched-Pair Set**: Exactly 6,734 matched pairs with $|S_i - S_j| \le 0.02$, partitioned deterministically into:
  - $6,376$ same-direction pairs ($\mathbf{d}_i = \mathbf{d}_j$).
  - $358$ discordant-direction pairs ($\mathbf{d}_i \ne \mathbf{d}_j$).

---

## 6. Primary Evaluation Results across Consumers

All metrics represent the mean across consumer robustness seeds $42–46$ (with observed cross-seed $\text{std} = 0.0000$ on C0 and C2, and seed-dependent variance on C4):

| Consumer ID | C2 DiffRate ($\text{DiffRate}_{\text{disc}}$) | C0 Baseline ($D_{\text{pair\_action}}$) | Directional Gain ($\Delta_{\text{dir\_gain}}$) | Shuffled Shift ($D_{\text{condition}}(C2, C4)$) | Mean $\overline{\Delta V}(C2)$ | Mean $\overline{\Delta V}(C0)$ | Preregistered Status |
|---|---|---|---|---|---|---|---|
| **`A_REFERENCE`** | **0.7989** (286/358) | 0.0000 (0/358) | **+0.7989** | 0.2859 | 0.5315 | 0.0074 | **SATISFIED** |
| **`B_DIRECTIONAL_SEPARABLE`** | **0.7989** (286/358) | 0.0000 (0/358) | **+0.7989** | 0.2622 | 0.6901 | 0.0207 | **SATISFIED** |
| **`C_CONTINUOUS_UTILITY`** | **0.0000** (0/358) | 0.0000 (0/358) | **+0.0000** | 0.0104 | 0.7123 | 0.0132 | **NOT SATISFIED** |
| **`D_MAGNITUDE_DOMINANT`** | **0.0000** (0/358) | 0.0000 (0/358) | **+0.0000** | 0.0000 | 0.1934 | 0.1376 | **NOT SATISFIED** |

### Preregistered Transfer Criteria Evaluation (Independent Consumers B, C, D):

| Evaluation Criterion | Preregistered Threshold | Consumer B | Consumer C | Consumer D |
|---|---|---|---|---|
| **1. Primary Discordant Differentiation** | $\text{DiffRate}_{\text{disc}}(C2) \ge 0.2000$ | **0.7989** (`PASS`) | 0.0000 (`FAIL`) | 0.0000 (`FAIL`) |
| **2. Incremental Gain over Scalar Baseline** | $\Delta_{\text{dir\_gain}} \ge 0.1000$ | **+0.7989** (`PASS`) | +0.0000 (`FAIL`) | +0.0000 (`FAIL`) |
| **3. Condition-Level Shuffled Sensitivity** | $D_{\text{condition\_action}}(C2, C4) \ge 0.0500$ | **0.2622** (`PASS`) | 0.0104 (`FAIL`) | 0.0000 (`FAIL`) |
| **4. Hard Tuple Identity Parity Invariant** | $\Delta_{\text{action\_identity}} = 0.0, D_{\text{JS}} < 10^{-12}$ | **0.0000** (`PASS`) | **0.0000** (`PASS`) | **0.0000** (`PASS`) |
| **Individual Consumer Transfer Verdict** | All 4 Criteria Met | **TRANSFER SATISFIED** | **NOT SATISFIED** | **NOT SATISFIED** |

$$\mathbf{R_{\text{transfer}} = \frac{1 \text{ satisfied}}{3 \text{ evaluated}} = 0.3333 \quad (33.3\%)}$$

---

## 7. Deep Dive: Consumer C and Continuous Utility Space (RQ5 Resolution)

In the previous behavioral utility study, Condition C5 (fixed $S_0 = 0.50$) produced identical discrete argmax action divergence as C2 ($D_{\text{action}} = 0.0425$), prompting the question:
> *Did scalar magnitude fail to contribute behavioral differentiation, or did the discrete argmax threshold mask continuous scalar valuation differences?*

Consumer C's continuous utility evaluation provides an unambiguous empirical answer:

```text
[Continuous Utility Space]
- C0 (Scalar Only):      Mean Delta V = 0.0132 > 0.0000
  (Scalar variation |Delta S| <= 0.02 produces genuine continuous utility distance)
- C2 (Scalar + R3):      Mean Delta V = 0.7123 (>50x larger continuous separation)

[Discrete Action Space]
- C0 Argmax Divergence:  0.0000
- C2 Argmax Divergence:  0.0000
  (Both scalar and directional continuous shifts failed to alter discrete argmax)
```

### Empirical Insight:
1. **Scalar Continuous Contribution**: Scalar magnitude **does** contribute continuous valuation variance within matched pairs ($\overline{\Delta V} = 0.0132$). The previous C5 discrete argmax equivalence was an artifact of argmax thresholding over small scalar tolerances ($|\Delta S| \le 0.02$).
2. **Discrete Argmax Masking**: In Consumer C, the baseline utility separation between the top-ranked action (`answer`) and runner-up actions exceeded the directional exponent perturbation $\exp(\mathbf{M}_d \mathbf{d} / \sqrt{3})$. Consequently, despite massive continuous divergence ($\overline{\Delta V} = 0.7123$), zero discrete action switches occurred across the 358 matched pairs.
3. **Implication for Downstream Pipeline Design**: Directional information does not automatically guarantee discrete policy switches if the downstream consumer's prior action valuation margins are wide. Directional side-channels require balanced valuation scaling to exert downstream discrete behavioral consequences.

---

## 8. Deep Dive: Consumer D and Magnitude Dominance

Consumer D tested whether R3 remains behaviorally active when scalar magnitude is intentionally weighted heavily ($\kappa_S \in [0.8, 5.5]$) and directional coupling is attenuated ($\mu_d = 0.20$):
- **Result**: Zero discordant differentiation ($\text{DiffRate} = 0.0000$) and zero shuffled sensitivity ($D_{\text{condition\_action}} = 0.0000$).
- **Significance**: Proves that R3 directional influence is **not unconditional**. When downstream consumers assign overwhelming priority to metabolic intensity or urgency, directional residual error becomes completely inert.

---

## 9. Negative Controls & Methodological Verification

### NC1 — Empirical Scalar-Collapse Baseline Control
Under Condition C0 (scalar only, $\mathbf{d} = \mathbf{0}$):
- All four consumers exhibited $D_{\text{pair\_action}}(C0) = 0.0000$ across all 358 matched pairs.
- Confirms that scalar magnitude alone cannot differentiate discordant pairs within the $|\Delta S| \le 0.02$ tolerance band.

### NC2 — Condition-Level Shuffled Direction Control
Under Condition C4 (permuted direction):
- Reference Consumer A: $D_{\text{condition\_action}}(C2, C4) = 0.2859$ ($28.59\%$ of probes switched action).
- Consumer B: $D_{\text{condition\_action}}(C2, C4) = 0.2622$ ($26.22\%$ of probes switched action).
- Confirms that behavioral differentiation in A and B depends strictly on the *correspondence* between direction and source residual rather than marginal directional statistics.

### NC3 — Permutation Invariant Preservation
Permuting direction coordinates for C4 did not alter scalar $S$, probe textual content, or marginal coordinate counts.

### NC4 — Consumer Isolation Invariant
Consumers received strictly $(S, \mathbf{d})$; zero access was provided to probe labels, affective tiers, condition identity, or outputs from other consumers.

### NC5 — Pipeline Non-Feedback Invariant
Consumer evaluation executed strictly downstream without modifying `EmotionCore` ODE state, prediction residuals, or subsequent probe integration.

### NC6 — Hard Tuple Identity Invariant
Evaluated on synthetic identical $(S, \mathbf{d})$ tuples:
$$\Delta_{\text{action\_identity}} = 0.0000, \quad D_{\text{JS\_identity}} < 10^{-12}$$
100% deterministic reproducibility verified across all four consumers.

---

## 10. Cross-Seed Robustness Analysis

| Consumer | Seed 42 DiffRate | Seed 43 DiffRate | Seed 44 DiffRate | Seed 45 DiffRate | Seed 46 DiffRate | Mean | Std |
|---|---|---|---|---|---|---|---|
| **`A_REFERENCE`** | 0.7989 | 0.7989 | 0.7989 | 0.7989 | 0.7989 | **0.7989** | **0.0000** |
| **`B_DIRECTIONAL_SEPARABLE`** | 0.7989 | 0.7989 | 0.7989 | 0.7989 | 0.7989 | **0.7989** | **0.0000** |
| **`C_CONTINUOUS_UTILITY`** | 0.0000 | 0.0000 | 0.0000 | 0.0000 | 0.0000 | **0.0000** | **0.0000** |
| **`D_MAGNITUDE_DOMINANT`** | 0.0000 | 0.0000 | 0.0000 | 0.0000 | 0.0000 | **0.0000** | **0.0000** |

*Explanation*: As established in ADR-029 §8.0, consumer seeds govern tie-breaking micro-noise $\mathcal{N}(0, 10^{-6})$ and C4 permutation sequences. Because unpermuted action valuation margins $|G(a^*) - G(a')| \ge 0.010$ exceed micro-noise by $10^4\times$, unpermuted action selections are completely invariant across seeds ($\text{std} = 0.0000$). C4 condition shifts exhibit seed sensitivity ($\text{std} = 0.0142$) due to permutation variability.

---

## 11. Definitive Scientific Conclusion

Evaluated against preregistered decision rules, the transferability statistic yields:
$$R_{\text{transfer}} = \frac{1}{3} \approx 0.3333 \implies \text{\textbf{PARTIAL\_TRANSFERABILITY\_PARTIAL\_ADAPTER\_DEPENDENCE}}$$

Per mandatory governance guidelines (§25), the official conclusion is:

> **R3 behavioral differentiation transfers to some independently specified consumers but not others, indicating partial consumer robustness with unresolved adapter dependence. Further architectural interpretation remains premature. ADR-029 remains a research candidate, and Quality Gate 2 remains strictly blocked.**

---

## 12. Artifact Integrity & SHA-256 Manifest

All machine-readable result files, summaries, manifests, and test suites are cryptographically recorded:

| Artifact Path | SHA-256 Digest | Size (Bytes) | Role |
|---|---|---|---|
| [`evaluate_r3_consumer_transferability.py`](file:///c:/Users/Lunafiah/Desktop/My_project/Lucia/tests/evaluation_phase22/scripts/evaluate_r3_consumer_transferability.py) | `753ce8446b7a858ff408bcf7b2b2b14197db3c5d64ba61b17a15fa1d24c004dc` | 27,613 | Evaluation Engine Script |
| [`r3_consumer_transferability_results.json`](file:///c:/Users/Lunafiah/Desktop/My_project/Lucia/tests/evaluation_phase22/results/h1_r3_consumer_transferability/r3_consumer_transferability_results.json) | `da7c48964872caec410d5821e0071489c688d475199d70395a76af4c52446728` | 57,674 | Primary Machine-Readable Results |
| [`r3_consumer_transferability_summary.csv`](file:///c:/Users/Lunafiah/Desktop/My_project/Lucia/tests/evaluation_phase22/results/h1_r3_consumer_transferability/r3_consumer_transferability_summary.csv) | `ba9949646c24578b868bb2db13a17df3be03932cfad112a207ec14b3017ca12f` | 438 | Tabular Summary Metrics |
| [`manifest_h1_r3_consumer_transferability.json`](file:///c:/Users/Lunafiah/Desktop/My_project/Lucia/tests/evaluation_phase22/fixtures/manifest_h1_r3_consumer_transferability.json) | `6cce7d5d283c746e50ea6827052a6a0e6669919f6f698d2ec2c2a3733a41ef19` | 1,029 | Cryptographic Fixture Manifest |
| [`test_h1_r3_consumer_transferability.py`](file:///c:/Users/Lunafiah/Desktop/My_project/Lucia/tests/evaluation_phase22/test_h1_r3_consumer_transferability.py) | `b680376d49826a5c102a249fa6b2a47291a27e3d2ffb8a74c7cf4c1851b2723c` | 8,574 | 12-Suite Automated Verification Test |
