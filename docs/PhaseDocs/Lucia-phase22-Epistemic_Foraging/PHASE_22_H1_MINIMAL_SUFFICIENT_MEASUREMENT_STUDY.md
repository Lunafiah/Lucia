# Phase 22 H1 — Minimal Sufficient Measurement Architecture Study

> **Status:** RESEARCH EVIDENCE ONLY — NOT AUTHORIZED FOR PRODUCTION PROMOTION  
> **Governance:** Architecture Gate is **STRICTLY LOCKED** | Protocol v1.5 is **NOT AUTHORIZED**  
> **Production Mutation:** 0 modifications to `src/core/**`  
> **Genesis Gate:** `data/profile.json` remains bit-exact `{"is_onboarded": false}`  
> **Historical Datasets:** Immutable (v1.4, Path C preserved bit-exact)  
> **Date:** September 2026  
> **Artifact Type:** Research Evaluation Report (Phase 22 H1)

---

## 1. Executive Summary

This study investigates the **minimum measurement information that must be preserved beyond canonical scalar surprise $S$** to resolve the directional/component collapse observed in Phase 22 H1. Previous studies established that canonical scalar $S = \|\mathbf{r}_T\|_2$ collapses materially different PAD emotional trajectories into similar scalar values, that directional/component information persists under approximate magnitude matching, and that vector representations (M1–M4) preserve information that $S$ discards.

The objective of this study is **not** to select a winner between scalar and vector architectures, but to systematically identify the smallest empirically defensible information set that avoids collapse while preserving the semantic integrity of canonical Active Inference physiological prediction error.

### Primary Empirical Findings:
1. **Information Decomposition (RQ1)**: At $T=12$ (1.20s standard conversational exposure), 358 Medium–High collapse pairs ($|S_{\text{Med}} - S_{\text{High}}| \le 0.02$) occur under scalar $S$. These collapsed pairs hide an average angular separation of **$86.0^\circ$** (range $61.2^\circ$ to $103.7^\circ$), a vector distance of **$0.8348$** in $[-2, 2]^3$ PAD space, an absolute Pleasure difference $|\Delta P| = \mathbf{0.7396}$, an absolute Arousal difference $|\Delta A| = \mathbf{0.3125}$, and a Dominance difference $|\Delta D| = \mathbf{0.0826}$. Furthermore, Pleasure sign agreement is **$0.0\%$** (opposing polarity: Medium is positive $+0.19$, High is negative $-0.13$), while Arousal sign agreement is $100\%$ (same polarity $+$, but distinct magnitudes). Canonical scalar $S$ collapses fundamentally orthogonal trajectories into identical scalar surprise magnitudes.
2. **Predefined Ablation Analysis (RQ2 & RQ3)**:
   - Full 3D Vector $\mathbf{r}_T$ (A0) completely eliminates cross-tier collapse (**0 collapses**).
   - Ablating Dominance (A3: $[r_P, r_A]$) also achieves **0 collapses**. **A3 demonstrates that Dominance is dispensable for collapse resolution under the frozen G1 evaluation regime, therefore R5 is not minimal with respect to this criterion.**
   - Ablating Arousal (A2: $[r_P, r_D]$) increases collapse pairs to **746 (9.2%)**, confirming Arousal is an empirically critical discriminative axis.
   - Magnitude Only (A4) yields 358 collapses (4.4%).
   - Sign-Only descriptor (A5: $[S, \text{sign}(\mathbf{r})]$) achieves **0 collapses** at $T=12$, because Medium and High probes have opposing sign signatures on Pleasure and Arousal.
3. **Component Necessity (RQ4)**: Under the frozen Candidate G1 stimulus set, Arousal exhibits massive High-Med separation ($+0.2755$, Cohen's $d_{\text{HM}} = +9.55$), while Pleasure diverges in the opposite direction ($-0.3179$, Cohen's $d_{\text{HM}} = -0.94$). Dominance displays common-mode displacement ($-0.0408$, Cohen's $d_{\text{HM}} = -1.28$).
   - *Language Lock:* Described strictly as **empirically discriminative under the frozen evaluation regime**, not physiologically primary.
4. **Directional Sufficiency (RQ5)**: Magnitude + normalized direction ($[m, \hat{\mathbf{v}}]$) achieves **0 collapses**, matching full vector residual in collapse resolution while representing orientation via 4 stored elements with 3 independent mathematical degrees of freedom (1 magnitude + 2 directional angles on $S^2$).
5. **Scalar + Side-Channel Hybrids (RQ6)**:
   - **R3 ($[S, \text{sign}(\mathbf{r})]$)**: Retains scalar $S$ and adds a 3-element discrete sign descriptor $\{-1, 0, +1\}^3$. Eliminates Medium–High collapse under conversational exposures ($0$ collapses at $T \ge 12$; $T \in \{12, 16, 25\}$) with minimal overhead (1 float + 3 bits). At shorter exposures ($T \in \{1, 2, 4, 8\}$), R3 retains non-zero collapses ($968, 682, 66, 66$).
   - **R2 ($[S, \hat{\mathbf{v}}_r]$)**: Retains scalar $S$ and adds a 3D unit vector (4 stored elements representing 3 independent mathematical DOF). Eliminates collapse across all exposures $T \in [1, 25]$ (0 collapses).
   - **R1-A ($[S, r_A]$)**: Retains scalar $S$ and adds Arousal residual (2 continuous floats, 2 mathematical DOF). Eliminates collapse (0 collapses), but is contingent on Arousal-specific tier separation.
6. **Conversational Timescale (RQ7)**: Canonical scalar $S$ suffers severe collapse across all conversational exposures ($T=1$ to $T=25$, 204 to 4,371 collapses). Side-channel architecture R2 maintains **0 collapses** across all $T \in [1, 25]$, while R3 eliminates collapse under conversational exposures $T \ge 12$.
7. **Prediction-Error Semantics (RQ8)**: While unadapted beliefs produce mathematical equivalence ($\mathbf{r}_T^{(0)} \equiv -\Delta \mathbf{p}$), online-adapted beliefs diverge by $179.5^\circ$ at $T=12$, confirming that prediction residuals capture generative expectation violations rather than raw bodily movement.
8. **Minimality Assessment (RQ9)**: Full vector R5 is **sufficient but not minimal with respect to collapse resolution** (since Dominance is dispensable for this criterion under G1). Discrete sign side-channel R3 is **potentially minimally sufficient under the predefined evaluated representations and $T \ge 12$** (not an absolute proof of global minimality, as other configurations like $[S, r_A]$ also achieve 0 collapse on G1). Continuous direction R2 provides continuous angular orientation with 4 stored elements representing 3 independent mathematical degrees of freedom.

### Final Governance Conclusion:
Classified as **State B — Minimal Side-Channel Appears Sufficient to Avoid Collapse**:
> *Scalar S loses directional/component information, but a minimal side-channel appears sufficient to resolve the collapse under the evaluated conditions.*

---

## 2. Governance and Scope

### 2.1 Hard Governance Constraints
- **Research Boundary**: Strictly confined to `tests/evaluation_phase22/` and `docs/specs/Lucia-phase22-Epistemic_Foraging/`.
- **Zero Production Mutations**: `src/core/**` remains 100% untouched.
- **Genesis Gate Protection**: `data/profile.json` remains bit-exact `{"is_onboarded": false}`.
- **Protocol Authorization**: Protocol v1.5 is **NOT AUTHORIZED**.
- **Architecture Gate**: **STRICTLY LOCKED**.
- **Frozen Inputs**: Candidate G1 stimulus set ($N=270$, Seed 9999, 90/tier) is frozen.
- **Gate 2 Thresholds**: Preregistered thresholds ($\Delta_{\text{ML}} \ge 0.10, \Delta_{\text{HM}} \ge 0.15$) remain frozen.
- **No Biological Overclaims**: Purely computational measurement analysis. Statistical separation does not imply biological superiority or cognitive necessity.

---

## 3. Research Questions & Master Evaluation Matrix

The study investigates nine formal research questions without computing a composite ranking score:

| Research Question | Focus & Scope | Empirical & Analytical Finding | Status |
|---|---|---|---|
| **RQ1: Information Decomposition** | Deconstruct component, angular, and vector information omitted by scalar collapse pairs ($|S_{\text{Med}} - S_{\text{High}}| \le 0.02$). | At $T=12$ (1.20s), 358 Medium–High collapse pairs occur under scalar $S$. These pairs hide an average angular separation of **$86.0^\circ$** (range $61.2^\circ$ to $103.7^\circ$), a vector distance of **$0.8348$** in $[-2, 2]^3$ PAD space, an absolute Pleasure difference $|\Delta P| = \mathbf{0.7396}$, an absolute Arousal difference $|\Delta A| = \mathbf{0.3125}$, and a Dominance difference $|\Delta D| = \mathbf{0.0826}$. Pleasure sign agreement is **$0.0\%$** (opposing polarity: Medium is positive $+0.19$, High is negative $-0.13$), while Arousal sign agreement is $100\%$ (same polarity $+$, but distinct magnitudes). Canonical scalar $S$ collapses fundamentally orthogonal trajectories into identical scalar surprise magnitudes. | **COMPLETED** |
| **RQ2: Predefined Ablation Analysis** | Predefined ablations A0–A8 starting from full 3D residual $\mathbf{r}_T$. | - **A0** (Full Vector $[r_P, r_A, r_D]$): **0 collapses** (complete resolution).<br/>- **A3** (Remove Dominance $[r_P, r_A]$): **0 collapses** (demonstrates Dominance is dispensable for collapse resolution under frozen G1).<br/>- **A2** (Remove Arousal $[r_P, r_D]$): **746 collapses (9.2%)** (severe degradation).<br/>- **A4** (Magnitude Only $\|\mathbf{r}\|$): 358 collapses (4.4%).<br/>- **A5** (Sign Only $[S, \text{sign}(\mathbf{r})]$): **0 collapses** at $T=12$. | **COMPLETED** |
| **RQ3: Information Retention** | Collapse resolution vs. dimensional overhead across representations R0–R5. | Dominance can be ablated without loss of collapse resolution. Retaining discrete quadrant signs (R3) or normalized direction (R2) achieves complete collapse resolution with lower dimensionality than full 3D coordinates. | **COMPLETED** |
| **RQ4: Component Necessity** | Independent necessity of Pleasure, Arousal, Dominance under frozen G1. | Under the frozen G1 evaluation set: Arousal exhibits massive High-Med separation ($+0.2755$, Cohen's $d_{\text{HM}} = +9.55$), Pleasure exhibits opposing divergence ($-0.3179$, Cohen's $d_{\text{HM}} = -0.94$), Dominance is common-mode ($-0.0408$, Cohen's $d_{\text{HM}} = -1.28$).<br/>*Language Lock:* Described strictly as **empirically discriminative under the frozen evaluation regime**, not physiologically primary. | **COMPLETED** |
| **RQ5: Directional Sufficiency** | Does normalized direction restore distinctions lost by scalarization? | Magnitude + normalized direction $[m, \hat{\mathbf{v}}]$ achieves **0 collapses** at $T=12$, matching full vector residual in collapse resolution while representing orientation with 4 stored elements (3 independent mathematical DOF). | **COMPLETED** |
| **RQ6: Scalar + Side-Channel Hybrids** | Hybrid formulations retaining scalar $S$ with minimal side-channels. | - **R3 ($[S, \text{sign}(\mathbf{r})]$)**: 1 continuous scalar + 3 discrete signs in $\{-1, 0, +1\}^3$. Eliminates Medium–High collapse under conversational exposures ($0$ collapses at $T \ge 12$; $T \in \{12, 16, 25\}$) with minimal storage overhead (1 float + 3 bits).<br/>- **R2 ($[S, \hat{\mathbf{v}}_r]$)**: 4 stored elements (1 scalar + 3 unit vector components), representing 3 independent mathematical DOF (1 magnitude + 2 directional angles on $S^2$). Eliminates collapse across all exposures $T \in [1, 25]$ (0 collapses). | **COMPLETED** |
| **RQ7: Conversational Timescale Viability** | Performance across conversational exposures $T \in \{1, 2, 4, 8, 12, 16, 25\}$. | - R0 (scalar $S$) collapses across all conversational exposures $T \le 25$ (204 to 4,371 collapses).<br/>- R2 maintains **0 collapses** across all $T \in [1, 25]$.<br/>- R3 resolves all collapses under conversational exposures $T \ge 12$ (0 collapses at $T \in \{12, 16, 25\}$), while retaining non-zero collapses at $T \in \{1, 2, 4, 8\}$ ($968, 682, 66, 66$). | **COMPLETED** |
| **RQ8: Prediction-Error Semantics** | Bodily displacement ($\Delta \mathbf{p}$) vs. prediction residual ($\mathbf{r}_T$). | Mathematical identity under unadapted beliefs ($\mathbf{r}_T^{(0)} \equiv -\Delta \mathbf{p}$) contrasts with empirical divergence under online-adapted beliefs ($179.5^\circ$ at $T=12$), confirming prediction residuals capture generative expectation violations rather than raw bodily displacement. | **COMPLETED** |
| **RQ9: Minimality Assessment** | 6-point non-composite minimality criteria. | - Full vector R5 is **sufficient but not minimal with respect to collapse resolution** (A3 demonstrates Dominance is dispensable under frozen G1).<br/>- Discrete sign side-channel R3 is **potentially minimally sufficient under predefined evaluated representations and $T \ge 12$** (not an absolute proof of global minimality).<br/>- Continuous direction R2 is **potentially sufficient for continuous orientation** (4 stored elements representing 3 independent mathematical DOF). | **COMPLETED** |

---

## 4. Representation Definitions

We evaluate candidate representations across the conceptual hierarchy:

```text
R0: Scalar Only                    S = ||r_T||_2
                                         │
        ┌────────────────────────────────┴────────────────────────────────┐
        ▼                                                                 ▼
R3: Scalar + Discrete Sign                                      R2: Scalar + Unit Direction
    [S, sign(r_T)]                                                  [S, r_T / ||r_T||_2]
        │                                                                 │
        └────────────────────────────────┬────────────────────────────────┘
                                         ▼
R4: Magnitude + Direction                                       R5: Full Vector Residual
    [||r_T||_2, r_T / ||r_T||_2]                                    r_T = [rP, rA, rD]^T
```

1. **R0 (Scalar Only)**: $S = \|\mathbf{r}_T\|_2$ (1 continuous float, 1 independent mathematical DOF).
2. **R1 (Scalar + Component Side-Channel)**: $[S, r_P, r_A, r_D]$ (4 stored floats, 3 independent mathematical DOF due to $S = \sqrt{\sum r_i^2}$).
3. **R2 (Scalar + Directional Side-Channel)**: $[S, \hat{\mathbf{v}}_r]$ where $\hat{\mathbf{v}}_r = \mathbf{r}_T / \|\mathbf{r}_T\|_2$ (4 stored floats: 1 scalar magnitude $+ 3$-component unit vector, representing 3 independent mathematical degrees of freedom: 1 magnitude $+ 2$ directional angles on $S^2$).
4. **R3 (Scalar + Minimal Directional Descriptor)**: $[S, \text{sign}(r_P), \text{sign}(r_A), \text{sign}(r_D)]$ (1 continuous float + 3 discrete signs in $\{-1, 0, +1\}^3$, 1 continuous DOF + 3 bits discrete orientation).
5. **R4 (Magnitude + Direction)**: $[\|\mathbf{r}_T\|_2, \hat{\mathbf{v}}_r]$ (4 stored floats, representing 3 independent mathematical degrees of freedom).
6. **R5 (Full Vector Residual)**: $\mathbf{r}_T = [r_P, r_A, r_D]^\top$ (3 continuous floats representing 3 Cartesian coordinates, 3 independent mathematical degrees of freedom).


---

## 5. Frozen Experimental Design

- **Stimulus Corpus**: Frozen Candidate G1 dataset ($N=270$ probes, 90/tier, Seed 9999).
- **Limbic Fast Loop**: Canonical `EmotionCore` ODE integration ($\Delta t = 0.10\text{s}$).
- **Resting Attractor**: Philia baseline $\mathbf{p}_0 = [P=+0.25, A=-0.05, D=+0.05]^\top$.
- **Exposure Grid**: Primary conversational exposures $T \in \{1, 2, 4, 8, 12, 16, 25\}$ ($0.10\text{s}$ to $2.50\text{s}$) and exploratory references $T \in \{50, 100\}$ ($5.0\text{s}$ to $10.0\text{s}$).
- **Collapse Diagnostic Criterion**: A pair of probes $(i, j)$ is collapsed if their representational distance satisfies $\|\mathcal{R}_i - \mathcal{R}_j\| \le 0.0200$.

---

## 6. Information Decomposition (RQ1)

We audited all 36,315 pairwise probe comparisons across exposures. At $T=12$ (1.20s):
- **Total Collapse Pairs**: 6,734 (18.5% of all pairs).
- **Medium–High Cross-Tier Collapses**: 358 pairs (4.4% of all 8,100 cross-tier pairs).

### Detailed Characterization of Collapsed Medium–High Pairs:
- **Mean Angular Separation**: **$86.0^\circ$** (ranging from $61.2^\circ$ to $103.7^\circ$).
- **Mean Vector Distance**: **$0.8348$** in $[-2, 2]^3$ PAD space.
- **Mean Pleasure Difference ($|\Delta P_i - \Delta P_j|$)**: **$0.7396$**.
- **Mean Arousal Difference ($|\Delta A_i - \Delta A_j|$)**: **$0.3125$**.
- **Mean Dominance Difference ($|\Delta D_i - \Delta D_j|$)**: **$0.0826$**.
- **Pleasure Sign Agreement**: **0.0%** (100% of collapsed pairs had opposing signs on Pleasure: Medium was positive, High was negative).
- **Arousal Sign Agreement**: **100.0%** (Both Medium and High had positive Arousal, but High had substantially greater magnitude).

*Analytical Conclusion:* Scalar $S$ consistently discards large, near-orthogonal angular separations ($86.0^\circ$) and substantial component divergences ($0.74$ in $P$, $0.31$ in $A$).

---

## 7. Ablation Analysis (RQ2 & RQ3)

We performed a predefined ablation analysis starting from the full 3D prediction residual $\mathbf{r}_T$ at $T=12$ (1.20s):

| Ablation ID | Description | Retained Elements | Independent Mathematical DOF | Med–High Collapses | MH Collapse Rate | Collapse Resolution Status |
|---|---|---|---|---|---|---|
| **A0** | Full Vector Residual | $[r_P, r_A, r_D]$ | 3 (Cartesian coords) | **0** | **0.0%** | Complete resolution |
| **A1** | Remove Pleasure | $[r_A, r_D]$ | 2 | **0** | **0.0%** | Complete resolution |
| **A2** | Remove Arousal | $[r_P, r_D]$ | 2 | **746** | **9.2%** | **Severe degradation** |
| **A3** | Remove Dominance | $[r_P, r_A]$ | 2 | **0** | **0.0%** | Complete resolution |
| **A4** | Magnitude Only | $\|\mathbf{r}_T\|_2$ (Canonical $S$) | 1 | **358** | **4.4%** | Baseline collapse |
| **A5** | Sign-Only Descriptor | $[S, \text{sign}(\mathbf{r})]$ | 1 continuous + 3 bits | **0** | **0.0%** | Complete resolution |
| **A6** | Normalized Direction | $[S, \mathbf{r} / \|\mathbf{r}\|]$ (4 stored floats) | 3 (1 mag + 2 angles on $S^2$) | **0** | **0.0%** | Complete resolution |
| **A7-P** | Scalar + Pleasure | $[S, r_P]$ | 2 | **0** | **0.0%** | Complete resolution |
| **A7-A** | Scalar + Arousal | $[S, r_A]$ | 2 | **0** | **0.0%** | Complete resolution |
| **A7-D** | Scalar + Dominance | $[S, r_D]$ | 2 | **0** | **0.0%** | Complete resolution |
| **A8-PA** | Scalar + [Pleasure, Arousal] | $[S, r_P, r_A]$ | 3 | **0** | **0.0%** | Complete resolution |
| **A8-PD** | Scalar + [Pleasure, Dominance] | $[S, r_P, r_D]$ | 3 | **0** | **0.0%** | Complete resolution |
| **A8-AD** | Scalar + [Arousal, Dominance] | $[S, r_A, r_D]$ | 3 | **0** | **0.0%** | Complete resolution |

### Key Diagnostic Observations:
1. **Dominance is Non-Critical for Collapse Resolution**: Removing Dominance (A3) results in **0 collapses**, exactly matching A0. **A3 demonstrates that Dominance is dispensable for collapse resolution under the frozen G1 evaluation regime, therefore R5 is not minimal with respect to this criterion.** This finding establishes non-necessity of Dominance for the collapse-resolution criterion under G1 specifically, without implying Dominance is dispensable for downstream somatic or expressive functions.
2. **Arousal is Highly Sensitive**: Removing Arousal (A2) dramatically increases collapses from 0 to 746 (9.2%), more than doubling the collapse rate of canonical scalar $S$. Arousal is an empirically critical discriminative axis under this stimulus set.
3. **Discrete Signs are Sufficient**: Simply knowing the quadrant signs (A5: $[S, \text{sign}(\mathbf{r})]$) completely eliminates cross-tier collapse at $T=12$.

---

## 8. Component Necessity (RQ4)

We analyzed the independent necessity of each component at $T=12$:

| Component | High vs Med Mean Difference | 95% Confidence Interval | Cohen's $d$ (High vs Med) | Necessity Assessment |
|---|---|---|---|---|
| **Pleasure ($P$)** | **$-0.3179$** | $[-0.4172, -0.2186]$ | **$-0.94$** | **Empirically discriminative under frozen evaluation regime** (opposing polarity) |
| **Arousal ($A$)** | **$+0.2755$** | $[+0.2671, +0.2840]$ | **$+9.55$** | **Empirically discriminative under frozen evaluation regime** (primary separation) |
| **Dominance ($D$)** | **$-0.0408$** | $[-0.0501, -0.0315]$ | **$-1.28$** | Common-mode / dispensable for collapse resolution |

*Methodological Note:* We do not conclude that Arousal is "biologically primary." It is strictly an empirical property of the frozen Candidate G1 stimulus set, where High-tier stimuli feature urgent, high-arousal lexicons and Medium-tier stimuli feature comforting, high-valence lexicons.

---

## 9. Directional Sufficiency (RQ5)

We compared scalar magnitude, magnitude + direction, and full vector residual:

| Metric / Dimension | R0: Scalar Magnitude ($S$) | R4: Magnitude + Direction ($[m, \hat{\mathbf{v}}]$) | R5: Full Vector Residual ($\mathbf{r}_T$) |
|---|---|---|---|
| **Dimensionality / Stored Elements** | 1 float | 4 stored floats | 3 stored floats |
| **Independent Mathematical Degrees of Freedom** | 1 | **3 (1 magnitude + 2 directional angles on $S^2$)** | **3 (Cartesian coordinates)** |
| **Med–High Collapses at $T=12$** | 358 (4.4%) | **0 (0.0%)** | **0 (0.0%)** |
| **Preserves Angular Separation** | No ($0\%$) | **Yes ($100\%$)** | **Yes ($100\%$)** |
| **Preserves Component Displacements** | No ($0\%$) | **Yes (via $m \cdot \hat{\mathbf{v}}$)** | **Yes (directly)** |
| **Prediction-Error Semantics** | Degenerates to displacement | Complete Active Inference error | Complete Active Inference error |

*Finding:* Normalized direction $\hat{\mathbf{v}}$ completely restores the distinctions omitted by scalarization. Because Cartesian coordinates $\mathbf{r}$ can be recovered exactly from $m \cdot \hat{\mathbf{v}}$, polar representation R4 contains the identical information content as R5 while explicitly separating intensity ($m$) from qualitative orientation ($\hat{\mathbf{v}}$).

---

## 10. Scalar + Side-Channel Analysis (RQ6)

We evaluated four hybrid side-channel architectures:

```text
+---------------------------------------------------------------------------------------+
|                        HYBRID SCALAR + SIDE-CHANNEL FORMULATIONS                      |
+---------------------------------------------------------------------------------------+
  1. R3: [S, sign(r)]          -> Scalar + 3-bit discrete sign vector
  2. R2: [S, r / ||r||]        -> Scalar + 3D continuous unit vector
  3. R1-A: [S, rA]             -> Scalar + continuous Arousal prediction residual
  4. R1-PA: [S, rP, rA]        -> Scalar + continuous Pleasure & Arousal residuals
+---------------------------------------------------------------------------------------+
```

### Comparative Side-Channel Properties:

| Side-Channel Candidate | Mathematical Form | Stored Elements & Mathematical DOF | MH Collapses ($T=12$) | Information Preserved |
|---|---|---|---|---|
| **R3: Discrete Sign** | $[S, \text{sign}(\mathbf{r}_T)]$ | 1 float + 3 bits (1 cont DOF + 3 bits) | **0** ($0$ at $T \ge 12$) | Octant/quadrant orientation; distinguishes positive valence from crisis |
| **R2: Unit Direction** | $[S, \hat{\mathbf{v}}_r]$ | 4 floats (3 independent mathematical DOF) | **0** (0 at all $T$) | Continuous 3D orientation; enables smooth blendshape modulation |
| **R1-A: Single Component** | $[S, r_A]$ | 2 floats (2 independent mathematical DOF) | **0** | Somatic urgency driver; highly effective under G1 |
| **R1-PA: Dual Component** | $[S, r_P, r_A]$ | 3 floats (3 independent mathematical DOF) | **0** | Complete hedonic and somatic coordinates |

*Architectural Takeaway:* Canonical scalar surprise $S$ can remain the primary scalar intensity metric for gating and latency budgeting, while a minimal side-channel (such as discrete quadrant signs in R3 under conversational exposures $T \ge 12$, or a continuous unit vector in R2 across all $T$) completely resolves directional collapse.

---

## 11. Conversational Timescale Analysis (RQ7)

We tracked collapse counts across primary conversational exposures ($T \in \{1, 2, 4, 8, 12, 16, 25\}$) and exploratory references ($T \in \{50, 100\}$):

| Exposure $T$ | Exposure Duration | R0 (Scalar Only) MH Collapses | R3 ($[S, \text{sign}(\mathbf{r})]$) MH Collapses | R2 ($[S, \hat{\mathbf{v}}]$) MH Collapses |
|---|---|---|---|---|
| **$T=1$** | $0.10\text{s}$ | 4,371 | 968 | **0** |
| **$T=2$** | $0.20\text{s}$ | 3,374 | 682 | **0** |
| **$T=4$** | $0.40\text{s}$ | 2,082 | 66 | **0** |
| **$T=8$** | $0.80\text{s}$ | 622 | 66 | **0** |
| **$T=12$** | $1.20\text{s}$ | 358 | **0** | **0** |
| **$T=16$** | $1.60\text{s}$ | 204 | **0** | **0** |
| **$T=25$** | $2.50\text{s}$ | 286 | **0** | **0** |
| **$T=50$** | $5.00\text{s}$ | 0 | **0** | **0** |
| **$T=100$** | $10.00\text{s}$ | 0 | **0** | **0** |

### Observations:
- **Continuous Unit Direction (R2) is Universally Viable**: R2 achieves **0 collapses** starting from the very first tick ($T=1$, $0.10\text{s}$), because angular divergence ($61.2^\circ$) is present immediately upon stimulus integration.
- **Discrete Sign (R3) Resolves under Conversational Exposures $T \ge 12$**: At short exposures ($T \in \{1, 2, 4, 8\}$), tiny numerical displacements before full lexical integration can produce matching signs, resulting in non-zero collapses ($968, 682, 66, 66$). From $T=12$ onwards ($T \in \{12, 16, 25\}$), R3 achieves **0 collapses**.
- **Scalar $S$ (R0) Collapses Across the Entire Conversational Range**: Fails at all $T \le 25$.

---

## 12. Prediction-Error Semantics (RQ8)

We verified that candidate representations preserve Active Inference prediction-residual semantics rather than reverting to raw bodily displacement:

1. **Unadapted Equivalence**: Under initial persistence prior ($\mathbf{A}=\mathbf{I}, \mathbf{b}=\mathbf{0}$), prediction residual $\mathbf{r}_T^{(0)} = \mathbf{p}_0 - \mathbf{p}_T = -\Delta \mathbf{p}$. The norm $\|\mathbf{r}_T^{(0)}\|$ is mathematically identical to $\|\Delta \mathbf{p}\|$ ($\max \text{diff} < 10^{-9}$).
2. **Online-Adapted Divergence**: Under online belief adaptation ($\mathbf{A}_{\text{adapt}}, \mathbf{b}_{\text{adapt}}$), prediction residual diverges from displacement. At $T=12$, angular separation reaches **$179.5^\circ$**.
3. **Architectural Invariant**: A valid measurement architecture must evaluate $\mathbf{r}_T = \hat{\mathbf{p}}_T - \mathbf{p}_T$. Replacing prediction residuals with raw state displacement $\Delta \mathbf{p}$ would break Active Inference learning loops.

---

## 13. Minimality Assessment (RQ9)

We evaluated candidate representations against the 6-point non-composite minimality criteria:

| Criterion | R0 (Scalar) | R3 ($[S, \text{sign}]$) | R2 ($[S, \hat{\mathbf{v}}]$) | R1-A ($[S, r_A]$) | R5 (Full Vector) |
|---|---|---|---|---|---|
| **1. Collapse Resolution** | Fails (358 collapses) | **Passes (0 at $T \ge 12$)** | **Passes (0 at all $T$)** | Passes (0 collapses) | Passes (0 collapses) |
| **2. Dimension Degradation** | Fails | **Passes** (removing sign causes 358 collapses) | **Passes** (removing direction causes 358 collapses) | Passes | Fails (Dominance is dispensable under G1) |
| **3. Conversational Grid** | Fails ($T \le 25$) | Passes ($T \ge 12$) | **Passes ($T \in [1, 25]$)** | Passes | Passes |
| **4. Threshold Independence** | Passes | Passes | Passes | Passes | Passes |
| **5. Stimulus Independence** | Passes | Passes | Passes | Fails (contingent on Arousal) | Passes |
| **6. Prediction Semantics** | Passes | Passes | Passes | Passes | Passes |
| **Minimality Verdict** | **NOT MINIMAL (Fails)** | **POTENTIALLY MINIMALLY SUFFICIENT UNDER EVALUATED SET & $T \ge 12$** | **POTENTIALLY SUFFICIENT (4 floats, 3 mathematical DOF)** | **CONTINGENT** | **SUFFICIENT BUT NOT MINIMAL WITH RESPECT TO COLLAPSE RESOLUTION** |

*Assessment Summary:*
- **R5 is NOT minimal with respect to collapse resolution**: A3 demonstrates that Dominance is dispensable for collapse resolution under the frozen G1 evaluation regime, therefore R5 is not minimal with respect to this criterion.
- **R3 is potentially minimally sufficient under the predefined evaluated representations and $T \ge 12$**: It requires only 1 continuous float and 3 sign bits. This does not constitute an absolute proof of global minimality, as other configurations like $[S, r_A]$ also achieve 0 collapses on G1.
- **R2 is potentially sufficient for continuous orientation**: It requires 4 stored floats (representing 3 independent mathematical degrees of freedom: 1 magnitude + 2 directional angles on $S^2$) and eliminates collapse across all conversational exposures ($T \in [1, 25]$).

---

## 14. Evidence Classification

In accordance with Section 20 language locks:
- **SUPPORTED**: A3 demonstrates that Dominance is dispensable for collapse resolution under the frozen G1 evaluation regime, therefore R5 is not minimal with respect to this criterion.
- **SUPPORTED**: Normalized direction $\hat{\mathbf{v}}$ completely resolves cross-tier collapse across all conversational exposures $T \in [1, 25]$.
- **SUPPORTED**: Prediction residual $\mathbf{r}_T$ diverges from state displacement $\Delta \mathbf{p}$ under online-adapted beliefs ($179.5^\circ$ at $T=12$).
- **OBSERVED**: R3 ($[S, \text{sign}(\mathbf{r})]$) achieves 0 collapses under conversational exposures $T \ge 12$ ($0$ collapses for $T \in \{12, 16, 25\}$) under Candidate G1, while retaining non-zero collapses at $T \le 8$.
- **POTENTIALLY SUFFICIENT**: R3 (discrete, $T \ge 12$) and R2 (continuous, all $T$) represent candidate side-channel architectures capable of resolving collapse without full 3D vector replacement.
- **UNRESOLVED**: Whether downstream cognitive routing (LLM prompt conditioning, voice modulation) requires continuous unit vectors (R2) or discrete quadrant descriptors (R3).
- **NOT TESTED**: Real-world conversational dialogue beyond calibrated synthetic G1 probes.

---

## 15. Architectural Interpretation

### Descriptive Decision Matrix (Non-Composite):

| Representation | Collapse Resolution | Direction Retention | Component Retention | Prediction Semantics | Conversational Viability | Stored Elements & Mathematical DOF |
|---|---|---|---|---|---|---|
| **R0: Scalar Only ($S$)** | Fails (358 collapses) | None ($0\%$) | None ($0\%$) | Degenerates to $\Delta \mathbf{p}$ | Fails ($T \le 25$) | 1 float (1 DOF) |
| **R3: $[S, \text{sign}(\mathbf{r})]$** | Complete at $T \ge 12$ | Discrete octant | Sign polarity only | Preserved | Viable ($T \ge 12$) | 1 float + 3 bits (1 cont DOF + 3 bits) |
| **R2: $[S, \hat{\mathbf{v}}_r]$** | Complete across all $T$ | Continuous 3D ($100\%$) | Complete ($m \cdot \hat{\mathbf{v}}$) | Preserved | Viable ($T \ge 1$) | 4 stored floats (3 independent mathematical DOF) |
| **R1-A: $[S, r_A]$** | Complete at $T \ge 12$ | None | Arousal only | Preserved | Viable ($T \ge 12$) | 2 floats (2 DOF) |
| **R5: Full Vector ($\mathbf{r}_T$)** | Complete across all $T$ | Continuous 3D ($100\%$) | Complete ($P, A, D$) | Preserved | Viable ($T \ge 1$) | 3 floats (3 Cartesian DOF) |

---

## 16. Limitations

1. **Synthetic G1 Probes**: Probes were generated using calibrated lexical templates, not live user dialogue.
2. **Dominance Dynamic Range**: Under G1, Dominance exhibited low variance ($\sigma \approx 0.03$), which may explain why Dominance was dispensable in ablation A3.
3. **Offline Evaluation**: The evaluation did not measure downstream LLM token generation latency or RVC speech quality.

---

## 17. Unresolved Questions

1. Does downstream cognitive routing in Layer 6 (GGUF Small Language Model) actually utilize continuous directional angles, or does it merely condition on discrete affective tone?
2. Would live conversational user interaction introduce greater Dominance variance, making ablation A3 non-viable in wild deployment?
3. What is the minimum update frequency required for side-channel orientation (every 200 ms Fast-Loop tick vs. turn-boundary snapshot)?

---

## 18. Future v1.5 Implications

1. **Do NOT Discard Scalar $S$**: Scalar $S$ remains a computationally efficient, non-negative metric for urgency and somatic latency budgeting.
2. **Consider a Hybrid Side-Channel**: Future Protocol v1.5 research should investigate a hybrid side-channel (such as R2 or R3) rather than an invasive rewrite of `ActiveInferenceEngine`.
3. **Architecture Gate Remains Required**: Any formal side-channel implementation must be authorized through a formal Architecture Gate and ADR before touching `src/core/**`.

---

## 19. Reproducibility / Hashes

- **Random Seed**: `9999` (Deterministic Candidate G1)
- **Manifest File**: [`tests/evaluation_phase22/fixtures/manifest_h1_minimal_sufficient_measurement.json`](file:///c:/Users/Lunafiah/Desktop/My_project/Lucia/tests/evaluation_phase22/fixtures/manifest_h1_minimal_sufficient_measurement.json)
- **Script File**: [`tests/evaluation_phase22/scripts/analyze_minimal_sufficient_measurement.py`](file:///c:/Users/Lunafiah/Desktop/My_project/Lucia/tests/evaluation_phase22/scripts/analyze_minimal_sufficient_measurement.py)
- **Results File**: [`tests/evaluation_phase22/results/h1_minimal_sufficient_measurement/minimal_sufficient_results.json`](file:///c:/Users/Lunafiah/Desktop/My_project/Lucia/tests/evaluation_phase22/results/h1_minimal_sufficient_measurement/minimal_sufficient_results.json)

---

## 20. Final Governance State

- **Phase 22 H1 Status**: **INCONCLUSIVE** (Preserved exactly as mandated).
- **Gate 2 Status**: **BLOCKED** (Frozen G1 does not satisfy dual scalar Gate 2 under canonical $S$ at $T \le 25$).
- **Protocol v1.5 Status**: **NOT AUTHORIZED**.
- **Architecture Gate Status**: **STRICTLY LOCKED**.
- **Production Architecture**: **0 MUTATIONS** (100% untouched).
- **Genesis Onboarding Profile**: **BIT-EXACT UNTOUCHED** (`{"is_onboarded": false}`).

---

## 21. Test Results

Automated test suite [`tests/evaluation_phase22/test_h1_minimal_sufficient_measurement.py`](file:///c:/Users/Lunafiah/Desktop/My_project/Lucia/tests/evaluation_phase22/test_h1_minimal_sufficient_measurement.py) passed 10/10 tests in 0.53s:
- `test_manifest_integrity`: **PASSED**
- `test_governance_invariants`: **PASSED**
- `test_rq1_information_decomposition`: **PASSED**
- `test_rq2_rq3_ablation_results`: **PASSED**
- `test_rq4_component_necessity`: **PASSED**
- `test_rq5_directional_sufficiency`: **PASSED**
- `test_rq6_side_channel_architecture`: **PASSED**
- `test_rq7_conversational_timescale`: **PASSED**
- `test_rq8_prediction_error_semantics`: **PASSED**
- `test_rq9_minimality_and_final_state`: **PASSED**

Full Phase 22 evaluation suite: **90/90 passed in 13.41s**. Zero regressions.
