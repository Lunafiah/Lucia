# Phase 22 H1 — R3 Causal and Mechanistic Attribution Study

> **Status:** RESEARCH EVIDENCE RECORD — ARCHITECTURE GATE STRICTLY LOCKED  
> **Governance Invariants:** Phase 22 H1 is **INCONCLUSIVE** | Quality Gate 2 is **STRICTLY BLOCKED** ($\Delta_{\text{HM}} = 0.0685 < 0.1500$)  
> **ADR-029 Status:** **`DRAFT / RESEARCH RECORD ONLY / NOT RATIFIED`**  
> **Production Admission:** **NOT ADMITTED** (Zero mutations to `src/core/**`, `src/api/**`, `electron/**`)  
> **Genesis Gate:** `data/profile.json` preserved bit-exact `{"is_onboarded": false}`  
> **Scope:** Isolates causal attribution of R3 behavioral differentiation across 8 experimental conditions (C0–C7) and 4 downstream consumers  
> **Hardware Discipline:** 100% CPU Execution / 0.0 MB GPU VRAM Allocation  
> **Date:** September 2026  
> **Artifact Type:** Formal Research Specification & Evidence Report (Phase 22 H1)

---

## 1. Executive Summary

This specification establishes the **Phase 22 H1 R3 Causal and Mechanistic Attribution Study**. Having previously demonstrated that R3 ternary directional residual representation $\mathbf{d}_{\text{signs}} = \operatorname{sign}_\epsilon(\mathbf{r}_T) \in \{-1, 0, +1\}^3$ achieves behavioral differentiation in specific downstream consumers (notably Consumer C at $\gamma_C = 1.50$), this investigation addresses the central mechanistic question:

> **Which component of the R3 measurement representation is causally responsible for the observed behavioral differentiation in downstream consumers? Is differentiation driven by genuine directional correspondence, magnitude/direction coupling, non-linear consumer distortions, or low-dimensional artifacts reproducible by matched controls?**

To answer this question without confounding, this study deploys an **8-condition experimental protocol (C0 through C7)** evaluated across **4 downstream consumer models** (Primary Consumer C @ $\gamma_C = 1.50$, Reference Consumer A, Separable Consumer B, and Magnitude-Dominant Consumer D at its qualifying corner) under **5 robustness seeds** (42–46) on the canonical $N=270$ Candidate G1 stimulus corpus.

```
                         [R3 Causal Attribution Architecture]
                                          │
    ┌─────────────────────────────────────┴─────────────────────────────────────┐
    ▼                                                                           ▼
[Directional Attribution]                                           [Representation Ablation]
C2 (Canonical R3):   DiffRate = 79.89%                              C1 (Continuous R2): DiffRate = 79.89%
C3 (Shuffled Dir):   DiffRate = 29.16% (Δ = -50.73%)                C2 (Ternary R3):    DiffRate = 79.89%
C5 (Indep Random):   DiffRate = 24.53% (Δ = -55.36%)                C6 (Binary Sign):   DiffRate = 79.89%
Attribution: Sensitive to Stimulus Alignment (~63.5% Attenuation under C3)    Attribution: Sign Functional Equivalence Under Evaluated Diagnostic
```

### Key Empirical Findings:

1. **Evidence Consistent with Directional Contribution Under Evaluated Protocol**:
   - In Primary Consumer C ($\gamma_C = 1.50$), shuffling direction vectors across stimuli while strictly preserving their magnitude (Condition C3) reduces discordant pair differentiation from **$79.89\%$ down to $29.16\%$** (mean drop: **$-50.73$ percentage points**, $p < 10^{-6}$).
   - Supplying independent random directions that preserve empirical marginal frequencies (Condition C5) further reduces differentiation to **$24.53\%$** (mean drop: **$-55.36$ percentage points**).
   - Within the evaluated consumer, representation, and permutation protocol, this evidence is consistent with directional correspondence: shuffling direction vectors attenuates differentiation by ~63.5%, indicating that behavioral differentiation under this diagnostic is sensitive to the alignment of the direction vector with the stimulus rather than behaving purely as an unaligned perturbation.

2. **Magnitude Decoupling in Consumer C Under Evaluated Diagnostic**:
   - Shuffling scalar surprise magnitude while strictly preserving the directional vector (Condition C4) yields **$79.89\%$** differentiation in Consumer C ($\Delta_{\text{C2-C4}} = 0.0000$).
   - In Consumer C at $\gamma_C = 1.50$ and under this matched-pair diagnostic, directional valuation is multiplicative with respect to base utility ($U = U_{\text{base}} \odot (1 + \gamma_C \mathbf{M} \mathbf{v})$) while scalar surprise enters via an additive cost ($c_S \cdot S$); hence shuffling $S$ does not alter $\text{DiffRate}_{\text{disc}}$.
   - In contrast, in Consumer B ($\Delta_{\text{C2-C4}} = +0.0983$) and Consumer D ($\Delta_{\text{C2-C4}} = +0.0911$), magnitude scrambling induces modest disruption reflecting weak interaction in their non-linear/quadratic formulations.

3. **Binary Sign Representation Achieves Functional Equivalence Under Evaluated Diagnostics**:
   - Continuous normalized R2 residual ($\mathbf{u} = \mathbf{r}/\|\mathbf{r}\|_2$, Condition C1), canonical ternary R3 (Condition C2), and sign-only binary ablation ($d_j \in \{-1, +1\}$, Condition C6) all achieve identical discordant pair differentiation rates of **$79.89\%$** ($286 / 358$) across Consumers A, B, and C.
   - Because C6 preserves the exact same sign correspondence as C2 on non-zero coordinates, this provides evidence of functional equivalence under this diagnostic harness; it does not demonstrate that ternary deadband is universally redundant across unobserved architectures or task contexts ($C2 - C6 = 0.0000$).
   - Directional count / sparsity alone (Condition C7) yields **$0.0000$** differentiation in Consumers A, B, and C. The number of active non-zero dimensions does not differentiate pairs unless vector orientation is present.

4. **Consumer D Differentiation is Consistent with Scalar-Slope Collapse Hypothesis**:
   - At the isolated qualifying corner of Consumer D ($\mu_d = 1.00, \gamma_\kappa = 0.50$), Condition C7 (isotropic direction count without spatial orientation) produces **$100.00\%$** differentiation.
   - This empirical finding is consistent with the hypothesis that halving the scalar slope ($\gamma_\kappa = 0.50$) compresses scalar action utility margins, allowing generic positive vector offsets to alter action selection, rather than differentiation being driven uniquely by stimulus-specific directional sensitivity.

---

## 2. Research Questions & Hypotheses

This study formally investigates four mechanistic research questions:

- **RQ1 (Directional Specificity)**: Does R3 differentiation collapse when direction vectors are decoupled from their corresponding stimuli, or does any non-zero perturbation produce differentiation?
  - *Hypothesis $H_{\text{dir}}$*: If differentiation is causally driven by directional information, shuffling directions across stimuli ($C3$) will significantly reduce $D_{\text{pair\_action}}$ compared to canonical R3 ($C2$).
- **RQ2 (Magnitude Independence)**: Is directional differentiation dependent on precise scalar magnitude coupling, or does direction differentiate independently of scalar magnitude?
  - *Hypothesis $H_{\text{mag}}$*: If direction differentiates independently of magnitude, permuting scalar magnitudes ($C4$) while preserving directional vectors will preserve $D_{\text{pair\_action}}$.
- **RQ3 (Representation Granularity)**: Does ternary quantization ($\{-1, 0, +1\}^3$) provide functional benefits over continuous normalized residual ($R2$) or binary signs ($\{-1, +1\}^3$)?
  - *Hypothesis $H_{\text{gran}}$*: If ternary deadband is architecturally meaningful, $C2$ will outperform binary sign ablation $C6$, and continuous residual $C1$ will show distinct behavior.
- **RQ4 (Sparsity Artifact)**: Can observed differentiation be explained purely by the number of active residual dimensions (directional sparsity $k = \sum |d_j|$) without spatial orientation?
  - *Hypothesis $H_{\text{sparse}}$*: If directional sparsity explains differentiation, condition $C7$ will reproduce $C2$ differentiation.

---

## 3. Frozen Baseline & Governance Constraints

All experiments adhere strictly to canonical Lucia governance invariants:

| Constraint | Enforcement Rule | Verification Result |
|---|---|---|
| **Phase 22 H1 Status** | **`INCONCLUSIVE`** | Preserved (No hypothesis promotion) |
| **Quality Gate 2** | **`STRICTLY BLOCKED`** ($\Delta_{\text{HM}} = 0.0685 < 0.1500$) | Preserved |
| **ADR-029 Status** | **`DRAFT / RESEARCH RECORD ONLY / NOT RATIFIED`** | Preserved |
| **Architecture Gate** | **`STRICTLY LOCKED`** | Zero production diffs across `src/core/**` |
| **Genesis Gate** | `data/profile.json` bit-exact `{"is_onboarded": false}` | Verified bit-exact |
| **Hardware Discipline** | 100% CPU Execution / 0.0 MB GPU VRAM Allocation | Verified (NumPy/SciPy CPU) |
| **Corpus Immutability** | Candidate G1 Corpus ($N=270$, Seed 9999, SHA `d0061e8c...`) | Cryptographically verified |

---

## 4. Experimental Conditions Matrix (C0 through C7)

To isolate causal mechanisms, 8 conditions were constructed and applied to every probe $i \in \{1, \dots, 270\}$:

| Condition ID | Description | Scalar Input $S_i$ | Direction Vector $\mathbf{v}_{\text{dir}, i}$ | Mechanistic Role |
|---|---|---|---|---|
| **C0** | Scalar Baseline | $S_i$ | $\mathbf{0}$ | Negative Control 1: Canonical scalar reference |
| **C1** | R2 Continuous Residual | $S_i$ | $\frac{\mathbf{r}_{T, i}}{\|\mathbf{r}_{T, i}\|_2}$ if $\|\mathbf{r}_{T, i}\|_2 > 0$ else $\mathbf{0}$ | Continuous unquantized directional baseline |
| **C2** | Canonical R3 (Ternary) | $S_i$ | $\frac{1}{\sqrt{3}} \operatorname{sign}_\epsilon(\mathbf{r}_{T, i})$ | Historical R3 evaluated representation ($\epsilon=0.010$) |
| **C3** | Shuffled Direction | $S_i$ | $\frac{1}{\sqrt{3}} \mathbf{d}_{\pi(i)}$ ($\pi$ seeded permutation) | Isolates directional correspondence to stimulus |
| **C4** | Shuffled Magnitude | $S_{\sigma(i)}$ | $\frac{1}{\sqrt{3}} \operatorname{sign}_\epsilon(\mathbf{r}_{T, i})$ ($\sigma$ seeded perm) | Isolates magnitude-direction coupling |
| **C5** | Independent Direction | $S_i$ | $\frac{1}{\sqrt{3}} \mathbf{d}_{\text{indep}, i}$ (preserves marginals) | Negative Control 3: Empirical marginal preserving null |
| **C6** | Sign-Only Binary Ablation | $S_i$ | $\frac{1}{\sqrt{3}} \mathbf{b}_i$ ($b_{ij} = -1$ if $d_{ij} < 0$ else $+1$) | Removes ternary deadband zero states |
| **C7** | Direction-Count Control | $S_i$ | $\frac{\sum |d_{ij}|}{3\sqrt{3}} [1, 1, 1]^T$ | Controls for directional sparsity / non-zero count |

### Mathematical Specifications:

1. **C1 (R2 Continuous Residual Normalization)**:
   $$\mathbf{u}_i = \begin{cases} \frac{\mathbf{r}_{T, i}}{\|\mathbf{r}_{T, i}\|_2} & \text{if } \|\mathbf{r}_{T, i}\|_2 > 0 \\ \mathbf{0} & \text{if } \mathbf{r}_{T, i} = \mathbf{0} \end{cases}$$
   *Rule*: The $\epsilon = 0.010$ ternary deadband is strictly reserved for R3 and is NOT applied to R2 normalization. Only the exact zero vector maps to $\mathbf{0}$.

2. **C2 (Canonical R3 Ternary Quantization)**:
   $$d_{j, i} = \operatorname{sign}_\epsilon(r_{j, i}) = \begin{cases} +1 & \text{if } r_{j, i} > 0.010 \\ -1 & \text{if } r_{j, i} < -0.010 \\ 0 & \text{if } |r_{j, i}| \le 0.010 \end{cases}, \quad \mathbf{v}_{\text{dir}, i} = \frac{1}{\sqrt{3}}\mathbf{d}_i$$

3. **C6 (Binary Sign Ablation)**:
   $$b_{j, i} = \begin{cases} -1 & \text{if } d_{j, i} < 0 \\ +1 & \text{if } d_{j, i} \ge 0 \end{cases}, \quad \mathbf{v}_{\text{dir}, i} = \frac{1}{\sqrt{3}}\mathbf{b}_i$$

4. **C7 (Direction-Count Control)**:
   $$k_i = \sum_{j=1}^3 |d_{j, i}| \in \{0, 1, 2, 3\}, \quad \mathbf{v}_{\text{dir}, i} = \frac{k_i}{3\sqrt{3}}[1, 1, 1]^T$$

---

## 5. Evaluated Consumer Models & Parameter Regimes

Four consumer adapters were evaluated:

1. **Consumer C ($\gamma_C = 1.50$, Primary Evaluated Consumer)**:
   - Multiplicative Utility Model: $U(a) = U_{\text{base}}(a) \cdot [1 + \gamma_C \mathbf{M}_{a, \cdot} \mathbf{v}_{\text{dir}}] - c_S(a) \cdot S$
   - Parameter regime: $\gamma_C = 1.50$, identified in previous plausibility studies as behaviorally compatible.
2. **Consumer A ($\gamma_A = 1.00$, Historical Reference Control)**:
   - Expected Free Energy (EFE) Adapter: $G(a) = c_a - \beta_k(S) d_k(a) - \beta_m(S) d_m(a) - \mathbf{W}_{a, \cdot} \mathbf{v}_{\text{dir}}$
3. **Consumer B ($\gamma_B = 1.00$, Additive Separable Control)**:
   - Separable Utility: $G(a) = G_{\text{base}}(a) + \alpha_S(a) S + \beta_S(a) S^2 - \mathbf{W}_{a, \cdot} \mathbf{v}_{\text{dir}}$
4. **Consumer D ($\mu_d = 1.00, \gamma_\kappa = 0.50$, Qualifying Corner)**:
   - Magnitude-Dominant Model: $G(a) = G_{\text{base}}(a) + (\gamma_\kappa \boldsymbol{\kappa}_S(a)) \cdot S - \mu_d \mathbf{W}_{a, \cdot} \mathbf{v}_{\text{dir}}$

---

## 6. Matched-Pair Evaluation Protocol & Lineage

All evaluations were conducted strictly on the pre-registered Candidate G1 matched-pair partition:
- **Corpus**: $N=270$ probes (90 Low, 90 Medium, 90 High), Seed 9999.
- **Corpus SHA-256**: `d0061e8cfdd160f4ebccb7100e4fe3eeef9ff18a1a4c9c1b3f912a76f2ae82c0`.
- **Matched Pairs ($|\Delta S| \le 0.020$)**: 6,734 total pairs.
  - **Discordant Pairs ($\mathbf{d}_i \ne \mathbf{d}_j$)**: 358 pairs (16 greedy disjoint pairs).
  - **Same-Direction Pairs ($\mathbf{d}_i = \mathbf{d}_j$)**: 6,376 pairs.
- **Consumer Robustness Seeds**: 5 independent seeds: `[42, 43, 44, 45, 46]`.

---

## 7. Pre-Registered Metrics & Mechanistic Contrasts

For each consumer and condition, metrics were computed across discordant matched pairs:
- **Discordant Action Differentiation Rate**: $D_{\text{pair\_action}} = \frac{1}{|P_{\text{disc}}|} \sum_{(i, j) \in P_{\text{disc}}} \mathbb{I}(a_i \ne a_j)$
- **Directional Gain Above Scalar Baseline**: $\Delta_{\text{dir\_gain}} = D_{\text{pair\_action}}(C_k) - D_{\text{pair\_action}}(C0)$
- **Action Displacement From Scalar**: $\text{Disp} = \frac{1}{N} \sum_{i=1}^N \mathbb{I}(a_i(C_k) \ne a_i(C0))$

### Mechanistic Attribution Contrasts:

1. **Canonical R3 Gain**: $\Delta_{\text{C2-C0}} = D(C2) - D(C0)$
2. **Direction Correspondence Contribution**: $\Delta_{\text{dir}} = D(C2) - D(C3)$
3. **Magnitude Correspondence Contribution**: $\Delta_{\text{mag}} = D(C2) - D(C4)$
4. **Empirical Direction Structure Contribution**: $\Delta_{\text{struct}} = D(C2) - D(C5)$
5. **Reduced Sign Ablation Gain**: $\Delta_{\text{sign}} = D(C2) - D(C6)$
6. **Directional Sparsity Gain**: $\Delta_{\text{sparsity}} = D(C2) - D(C7)$

---

## 8. Negative Controls Results (NC1, NC2, NC3)

All three negative controls satisfied pre-registered acceptance criteria bit-exact:

| Negative Control | Target Invariant | Expected Outcome | Empirical Outcome | Status |
|---|---|---|---|---|
| **NC1: Canonical Scalar Baseline** | Bit-exact match against historical transferability artifact | $D_{\text{pair\_action}}(C0) = 0.0000$ | **$0.0000$** across all 4 consumers and 5 seeds | **PASSED (BIT-EXACT)** |
| **NC2: Hard Tuple Identity Parity** | Zero action difference for identical representation tuples | $\Delta_{\text{action}} = 0.0, D_{\text{JS}} = 0.0$ | **$\Delta_{\text{action}} = 0.0, D_{\text{JS}} = 0.0$** | **PASSED (100%)** |
| **NC3: Marginal Preserving Shuffles** | Directional decoupling collapses differentiation | $D(C3) \ll D(C2), D(C5) \ll D(C2)$ | $D(C3)=0.2916, D(C5)=0.2453$ | **PASSED ($p < 10^{-6}$)** |

---

## 9. Full Empirical Results by Condition

The table below reports mean values across all 5 robustness seeds (Seeds 42–46):

### Primary Evaluated Consumer: Consumer C ($\gamma_C = 1.50$)

| Cond | Description | $\text{DiffRate}_{\text{disc}}$ | $\sigma_{\text{disc}}$ | $\text{DiffRate}_{\text{greedy}}$ | $\Delta_{\text{dir\_gain}}$ | Action Disp | Urgency Dom | Tier Rank $\rho_s$ | Mean $\Delta V$ | Mean $D_{\text{JS}}$ | Mean $D_{\text{TV}}$ |
|---|---|---|---|---|---|---|---|---|---|---|---|
| **C0** | Scalar Baseline | 0.0000 | 0.0000 | 0.0000 | +0.0000 | 0.0000 | 100.0% | 1.0000 | 0.0132 | 0.0000 | 0.0010 |
| **C1** | Continuous R2 | 0.7989 | 0.0000 | 0.8125 | +0.7989 | 0.1704 | 100.0% | 0.6762 | 1.3038 | 0.0384 | 0.2416 |
| **C2** | Canonical R3 | 0.7989 | 0.0000 | 0.8125 | +0.7989 | 0.1704 | 100.0% | 0.6762 | 1.0954 | 0.0269 | 0.2038 |
| **C3** | Shuffled Dir | 0.2916 | 0.0551 | 0.3250 | +0.2916 | 0.1704 | 100.0% | 0.3143 | 0.3891 | 0.0066 | 0.0731 |
| **C4** | Shuffled Mag | 0.7989 | 0.0000 | 0.8125 | +0.7989 | 0.1704 | 100.0% | 0.6762 | 1.1153 | 0.0272 | 0.2041 |
| **C5** | Indep Dir | 0.2453 | 0.0181 | 0.2750 | +0.2453 | 0.1704 | 100.0% | 0.3143 | 0.3828 | 0.0064 | 0.0718 |
| **C6** | Binary Sign | 0.7989 | 0.0000 | 0.8125 | +0.7989 | 0.1704 | 100.0% | 0.6762 | 0.6879 | 0.0120 | 0.1315 |
| **C7** | Dir Count | 0.0000 | 0.0000 | 0.0000 | +0.0000 | 0.0000 | 100.0% | 1.0000 | 0.2447 | 0.0010 | 0.0366 |

### Cross-Consumer Comparison Table ($\text{DiffRate}_{\text{disc}}$)

| Consumer Adapter | C0 (Scalar) | C1 (R2 Cont) | C2 (R3 Ternary) | C3 (Shuff Dir) | C4 (Shuff Mag) | C5 (Indep Dir) | C6 (Binary Sign) | C7 (Dir Count) |
|---|---|---|---|---|---|---|---|---|
| **C ($\gamma_C = 1.50$)** | 0.0000 | 0.7989 | 0.7989 | 0.2916 | 0.7989 | 0.2453 | 0.7989 | 0.0000 |
| **A (Reference)** | 0.0000 | 0.7989 | 0.7989 | 0.2916 | 0.7989 | 0.2453 | 0.7989 | 0.0000 |
| **B (Separable)** | 0.0000 | 0.7989 | 0.7989 | 0.2916 | 0.7006 | 0.2453 | 0.7989 | 0.0000 |
| **D (Qual Corner)** | 0.0000 | 0.7989 | 0.7989 | 0.2916 | 0.7078 | 0.2453 | 0.7989 | 1.0000 |

> [!NOTE]
> **Shared Corpus- and Representation-Level Baseline for Shuffled Controls (C3 & C5):**  
> The identical mean values for C3 ($0.2916$) and C5 ($0.2453$) across Consumers A, B, C, and D reflect a shared corpus-level and representation-level property rather than independent numerical coincidences. Because all four consumer formulations share coordinate-aligned action weight matrices across the six canonical actions ($\mathbf{W}, \mathbf{M}$), each of the 27 discrete sign vectors $\{-1, 0, +1\}^3$ induces an identical argmax action ranking under directional dominance. When direction vectors $\mathbf{d}_{\pi(i)}$ are permuted across probes using fixed seeds, whether a discordant pair $(i, j)$ receives different actions depends on whether the permutation assigns two sign vectors from differing action partitions. Because this mapping is identical across the consumers, C3 and C5 establish a shared combinatorial null baseline of action discordance ($104.4 / 358 = 29.16\%$ for C3; $87.8 / 358 = 24.53\%$ for C5) inherent to the frozen G1 stimulus corpus multiset.

---

## 10. Mechanistic Attribution Matrix

| Mechanistic Contrast | Operational Formula | Consumer C | Consumer A | Consumer B | Consumer D |
|---|---|---|---|---|---|
| **Canonical R3 Gain** | $C2 - C0$ | **+0.7989** | **+0.7989** | **+0.7989** | **+0.7989** |
| **Direction Correspondence** | $C2 - C3$ | **+0.5073** | **+0.5073** | **+0.5073** | **+0.5073** |
| **Magnitude Correspondence** | $C2 - C4$ | **0.0000** | **0.0000** | **+0.0983** | **+0.0911** |
| **Empirical Structure** | $C2 - C5$ | **+0.5536** | **+0.5536** | **+0.5536** | **+0.5536** |
| **Reduced Sign Ablation** | $C2 - C6$ | **0.0000** | **0.0000** | **0.0000** | **0.0000** |
| **Directional Sparsity** | $C2 - C7$ | **+0.7989** | **+0.7989** | **+0.7989** | **-0.2011** |

---

## 11. Detailed Attribution Analysis for Primary Consumer C

1. **Evidence Consistent with Directional Contribution**:
   - $C2 = 0.7989$ vs $C3 = 0.2916$: Decoupling direction from stimuli reduces differentiation by $50.73$ percentage points.
   - The remaining $29.16\%$ in C3 represents the shared combinatorial baseline of unaligned direction pairs.
   - Within the evaluated protocol, this evidence is consistent with directional correspondence accounting for ~63.50% attenuation of the differentiation effect under directional shuffling.

2. **Magnitude Decoupling in Consumer C Under Evaluated Diagnostic ($C2 - C4 = 0.0000$)**:
   - Permuting scalar surprise magnitudes across the 270 probes does not alter discordant pair differentiation in Consumer C under this matched-pair diagnostic.
   - Because Consumer C modulates base utility multiplicatively by direction ($\mathbf{M} \mathbf{v}_{\text{dir}}$) while subtracting scalar surprise additively ($c_S \cdot S$), the directional ranking between actions under this diagnostic is invariant to $S$. This indicates magnitude decoupling under this specific formulation and diagnostic rather than general independence across all regimes or tasks.

3. **Directional Count is Ineffective Without Orientation ($C7 = 0.0000$)**:
   - The isotropic vector $\mathbf{v} = \frac{k}{3\sqrt{3}}[1, 1, 1]^T$ produces zero differentiation.
   - This indicates that directional differentiation requires asymmetric coordinate signs rather than an increase in non-zero limbic activity.

---

## 12. Comparative Analysis Across Consumers A, B, and D

1. **Consumer A (Reference EFE Adapter)**:
   - Mirrors Consumer C precisely in attribution contrasts: $C2 - C3 = +0.5073$, $C2 - C4 = 0.0000$, $C2 - C7 = +0.7989$.
   - In Consumer A, directional modulation $\mathbf{W} \mathbf{v}_{\text{dir}}$ is additive and decoupled from the non-linear hyperbolic tangent terms $\beta_k(S), \beta_m(S)$.

2. **Consumer B (Additive Separable Control)**:
   - $C2 - C4 = +0.0983$: Unlike Consumer C and A, scrambling magnitude in Consumer B reduces differentiation from $0.7989$ to $0.7006$.
   - Quadratic scalar terms ($\beta_S \cdot S^2$) interact weakly with directional offsets, demonstrating that non-linear scalar terms create minor magnitude dependence.

3. **Consumer D Qualifying Corner is Consistent with Scalar-Slope Collapse Hypothesis**:
   - $C7 = 1.0000$ ($C2 - C7 = -0.2011$): In Consumer D at its qualifying corner ($\mu_d = 1.00, \gamma_\kappa = 0.50$), isotropic direction-count produces $100\%$ differentiation.
   - This empirical finding is consistent with the hypothesis that halving the scalar slope compresses action utility differences, allowing any positive vector shift to dominate action selection, rather than differentiation being driven uniquely by stimulus-specific directional sensitivity.

---

## 13. Representation Fidelity Analysis: R2 vs R3 vs Binary Sign

| Metric | C1 (Continuous R2) | C2 (Canonical R3 Ternary) | C6 (Binary Sign) |
|---|---|---|---|
| **Discordant DiffRate** | 0.7989 | 0.7989 | 0.7989 |
| **Action Displacement** | 17.04% | 17.04% | 17.04% |
| **Mean Utility Shift $\Delta V$** | 1.3038 | 1.0954 | 0.6879 |
| **Mean Probability $D_{\text{JS}}$** | 0.0384 | 0.0269 | 0.0120 |
| **Mean Probability $D_{\text{TV}}$** | 0.2416 | 0.2038 | 0.1315 |

- **Conclusion**: Binary sign representation without deadband ($C6$) achieves the identical $\text{DiffRate}_{\text{disc}} = 0.7989$ as canonical ternary R3 ($C2$) across the evaluated consumers ($C2 - C6 = 0.0000$), while inducing less probability distribution distortion ($D_{\text{JS}} = 0.0120$ vs $0.0269$).
- Because C6 preserves the exact same sign correspondence as C2 on non-zero coordinates, this provides evidence of functional equivalence under this diagnostic harness; it does not demonstrate that ternary deadband is universally redundant across unobserved architectures or task contexts.

---

## 14. Scientific Conclusions & Answers to Research Questions

1. **Does R3 differentiation reflect directional contribution?**
   - **Evidence is consistent with directional contribution within the evaluated harness.** Across all evaluated consumers, shuffling directional vectors away from stimuli attenuates differentiation by 50.73 percentage points ($p < 10^{-6}$), indicating that differentiation in this setup is sensitive to stimulus-aligned orientation rather than behaving purely as an unaligned perturbation.
2. **Is R3 differentiation dependent on magnitude-direction interaction?**
   - **Within Consumer C at $\gamma_C = 1.50$ and under this diagnostic, shuffling $S$ does not alter $\text{DiffRate}_{\text{disc}}$ ($C2 - C4 = 0.0000$).** In Consumer B and D, magnitude scrambling induces modest disruption ($C2 - C4 \approx 0.09$), reflecting weak interaction in their non-linear/quadratic formulations.
3. **Does ternary quantization provide functional benefits over binary signs under evaluated diagnostics?**
   - **Not observed under evaluated diagnostics.** Binary sign representation ($C6$) achieves identical differentiation ($79.89\%$) with lower probability displacement ($D_{\text{JS}} = 0.0120$ vs $0.0269$). Under these consumers and diagnostics, ternary deadband provides no incremental differentiation gain over binary signs.
4. **Can differentiation be reproduced by low-dimensional sparsity controls?**
   - **NO in Consumers A, B, C** ($C7 = 0.0000$), where coordinate orientation is required.
   - **YES in Consumer D** ($C7 = 1.0000$), which is consistent with the hypothesis that Consumer D's qualifying corner is facilitated by scalar slope collapse rather than selective directional sensitivity alone.

---

## 15. Methodological Limitations & Grid-Bound Boundaries

1. **Diagnostic Synthetic Harness Only**: Evaluated consumers are stylized mathematical mappings, not production agents or biologically verified networks.
2. **Evaluated Parameter Regimes Only**: Findings apply strictly to the evaluated grid cells ($\gamma_C = 1.50$, Consumer D corner).
3. **Non-Equivalence to Architectural Promotion**: Proving directional causality within an evaluation harness does NOT satisfy Gate 2 ($\Delta_{\text{HM}} < 0.1500$) or justify modifying production code.

---

## 16. Governance Status & Invariant Ledger

- **Production Mutation Count**: Exactly `0` lines across `src/core/**`, `src/api/**`, `electron/**`.
- **Genesis Profile State**: `data/profile.json` remains bit-exact `{"is_onboarded": false}`.
- **ADR-029 Status**: Preserved as **`DRAFT / RESEARCH RECORD ONLY / NOT RATIFIED`**.
- **Phase 22 H1 Status**: Preserved as **`INCONCLUSIVE`**.
- **Quality Gate 2**: Preserved as **`STRICTLY BLOCKED`**.

---

## 17. Cryptographic Artifact Inventory & Manifest Ledger

| Artifact Path | SHA-256 Checksum | Size |
|---|---|---|
| `tests/evaluation_phase22/scripts/evaluate_r3_causal_attribution.py` | — | 43,090 bytes |
| `tests/evaluation_phase22/test_h1_r3_causal_attribution.py` | — | 11,280 bytes |
| `tests/evaluation_phase22/fixtures/manifest_h1_r3_causal_attribution.json` | — | 2,049 bytes |
| `tests/evaluation_phase22/results/h1_r3_causal_attribution/r3_causal_attribution_results.json` | `0395983d74a7ba36bfa5bb98e93802b6c0d8c817d5a235e7beb58c25036e61c4` | 1,455,797 bytes |
| `tests/evaluation_phase22/results/h1_r3_causal_attribution/r3_causal_attribution_summary.csv` | `965365c04925d4e589f6a39acb38efa164a73c35995fe9bf989efcdbe4e7d93d` | 3,827 bytes |

---

## 18. Automated Test Results & Suite Verification

- **Study Test Suite**: `tests/evaluation_phase22/test_h1_r3_causal_attribution.py`
  - **12 / 12 tests PASSED** in 0.55s.
- **Full Phase 22 Suite**: `tests/evaluation_phase22/`
  - **232 / 232 tests PASSED** in 14.20s.
  - Zero failures, zero warnings, zero regressions.

---

## 19. Production Diff & Genesis Invariant Verification

- `git diff --stat src/core/ src/api/ electron/ data/profile.json` $\to$ **0 files changed, 0 insertions, 0 deletions**.
- Genesis onboarding profile verification: `data/profile.json` content is exactly `{"is_onboarded": false}`.
