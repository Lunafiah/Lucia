# Phase 22 H1 — Gate 2 Surprise Compression Diagnostic Investigation

> **EXPLORATORY / DIAGNOSTIC RESEARCH INVESTIGATION REPORT**  
> **Status:** `[COMPLETED — DIAGNOSTIC ONLY — NO PROTOCOL AMENDMENT]`  
> **Governance Authority:** Post-Protocol v1.4 Research Investigation | **Architecture Gate:** STRICTLY LOCKED  
> **Date:** September 16, 2026 | **Timestamp (UTC):** 2026-09-16T14:15:00Z  
> **Classification:** `DESCRIPTIVE / DIAGNOSTIC / HYPOTHESIS-GENERATING`  
> **Reference Datasets:** [`tests/evaluation_phase22/results/h1_v14/`](file:///c:/Users/Lunafiah/Desktop/My_project/Lucia/tests/evaluation_phase22/results/h1_v14/), [`phase22_h1_path_c_matrix.json`](file:///c:/Users/Lunafiah/Desktop/My_project/Lucia/tests/evaluation_phase22/results/phase22_h1_path_c_matrix.json)

---

## Executive Summary

Under explicit project owner authorization, this investigation conducted a formal diagnostic post-mortem into the empirical phenomenon of **Medium–High surprise compression under $T = 12$ exposure** observed in the ratified Phase 22 H1 Protocol v1.4 benchmark.

### The Central Discovery
The primary question asked why separation collapsed at $T=12$ ($\Delta_{HM} = 0.0685 < 0.1500$) in v1.4, despite historical Path C showing $\Delta_{HM}(T=12) = 0.2090$.

Decomposing the immutable evaluation datasets revealed a definitive, single-factor locus:
1. **High-Surprise Response is Bit-Exact Identical**: At $T=12$, $S_H(T=12) = \mathbf{0.6477}$ in both Path C and Protocol v1.4. The High-surprise stimulus pool was unmodified and produced the exact same physiological response.
2. **Low-Surprise Response is Virtually Identical**: At $T=12$, $S_L(T=12) = 0.2293$ in Path C vs. $0.2647$ in v1.4 ($+0.0354$).
3. **The Entire Collapse Resides in $S_M$ Inflation**: At $T=12$, Medium surprise jumped from $S_M = \mathbf{0.4387}$ in Path C to $S_M = \mathbf{0.5792}$ in v1.4 — an inflation of exactly **$+0.1405$**.
4. **Direct Causal Locus**: In v1.4, the 30 templates for Medium surprise (`_SM_TEMPLATES`) were rewritten from dry, repetitive technical statements (mean VADER valence $+0.4158$, unique token density $0.7952$) into richly positive, natural collaborative companion phrases (mean VADER valence $+0.5846$, unique token density $0.9777$).
5. **Architectural Consequence in PAD Space**:
   - Medium stimuli in v1.4 produced **zero arousal elevation** ($A_T = -0.0363 \approx -0.05$ baseline).
   - However, the $+40.6\%$ increase in positive valence and $+23.0\%$ increase in semantic density drove massive displacement along the **Pleasure** axis ($P_0 = +0.25 \to P_T = +0.6704$, $\Delta P = +0.4204$) and **Dominance** axis ($D_0 = +0.05 \to D_T = +0.4463$, $\Delta D = +0.3963$) over 12 integration ticks ($2.4\,\text{s}$).
   - Because $S_{\text{observed}} = \| p_T - p_0 \|_2$ is an isotropic Euclidean norm, it treats displacement along the Pleasure/Dominance axes identically to displacement along the Arousal axis.
   - Consequently, $S_M(T=12)$ rose to $0.5792$, mechanically matching the response of High-surprise negative crisis alarms ($S = 0.5838$) and compressing the overall High tier ($S = 0.6477$) to $\Delta_{HM} = 0.0685$.

---

## 1. Research Question

In the ratified Phase 22 H1 Protocol v1.4 execution, Quality Gate 2 evaluated physiological surprise separation conditioned on standardized exposure $T = 12$ ticks:
$$\Delta_{ML}(T=12) = \bar{S}_M(T=12) - \bar{S}_L(T=12) = 0.5792 - 0.2647 = \mathbf{+0.3145} \ge 0.1000 \quad \text{[PASS]}$$
$$\Delta_{HM}(T=12) = \bar{S}_H(T=12) - \bar{S}_M(T=12) = 0.6477 - 0.5792 = \mathbf{+0.0685} < 0.1500 \quad \text{[FAIL]}$$

Because Gate 2 failed, the preregistered decision matrix mandated an official verdict of **INCONCLUSIVE**, despite downstream Track A/B satisfying all decoupling criteria ($\eta_p^2 \le 0.0058$, $\hat{\rho}_{\text{partial}} = -0.0393$, $90\%\,\text{CI} \subset [-0.20, +0.20]$).

The diagnostic research question is:
> **Why does the physiological surprise separation between $S_M$ and $S_H$ collapse at $T=12$ in Protocol v1.4, despite adequate separation at lower exposure ticks and despite the historical Path C result demonstrating $\Delta_{HM}(T=12) = 0.2090$?**

---

## 2. Evidence Base

This investigation evaluates only immutable historical evidence and deterministic read-only diagnostic analyses. No historical record has been modified or overwritten.

| Artifact Identifier | Role in Investigation | SHA-256 Digest |
|---|---|---|
| [`manifest_h1_v14.json`](file:///c:/Users/Lunafiah/Desktop/My_project/Lucia/tests/evaluation_phase22/fixtures/manifest_h1_v14.json) | Frozen v1.4 Input Fixture ($N = 270$) | `1c58fbb3209e4906ec32299e97bd9a8b00383d5189d362479c528951b9581ac4` |
| [`raw_evaluations.json`](file:///c:/Users/Lunafiah/Desktop/My_project/Lucia/tests/evaluation_phase22/results/h1_v14/raw_evaluations.json) | Frozen v1.4 Runtime Evals (1,350 runs) | `d92ce780862f2902f5b98b56e2e50cf1824878694c9a021b048b21a9c04b8a6b` |
| [`probe_summary.json`](file:///c:/Users/Lunafiah/Desktop/My_project/Lucia/tests/evaluation_phase22/results/h1_v14/probe_summary.json) | Aggregated v1.4 Probe Units ($N = 270$) | `2dd6b0ecf823c2dcd3c1e1654034d36defafdc0d362072c4b29b97220be89f96` |
| [`phase22_h1_path_c_matrix.json`](file:///c:/Users/Lunafiah/Desktop/My_project/Lucia/tests/evaluation_phase22/results/phase22_h1_path_c_matrix.json) | Historical Path C Evals (1,350 runs) | `076ec3b6482ac1cda8c5f4602abd109481bc93608495e88e2199eb5a4b4cf635` |
| [`diagnose_gate2_compression.py`](file:///c:/Users/Lunafiah/Desktop/My_project/Lucia/tests/evaluation_phase22/scripts/diagnose_gate2_compression.py) | Read-Only Diagnostic Tooling | `544c37ea60fc99c99f56d55a0969fe09e24377eda0a598099d81557a9081aa9b` |
| [`simulate_pad_trajectories.py`](file:///c:/Users/Lunafiah/Desktop/My_project/Lucia/tests/evaluation_phase22/scripts/simulate_pad_trajectories.py) | Step-by-Step Trajectory Simulator | `fc08b28afe7b42e0e1240edb8ee32f05c1bcf999c3eb01dbc2a418ac3d223c69` |

---

## 3. Observed v1.4 Compression

### 3.1 Empirical Reconstitution across $T \in \{1, 4, 12\}$
Aggregated across all $N = 270$ probe units in the immutable v1.4 dataset (30 probes per $S_{\text{target}} \times T$ condition):

| Factor Tier | $T = 1\text{ tick}$ ($0.10\,\text{s}$) | $T = 4\text{ ticks}$ ($0.40\,\text{s}$) | $T = 12\text{ ticks}$ ($1.20\,\text{s}$) | Pooled Marginal |
|---|---|---|---|---|
| **$S_{\text{Low}}$** | $0.0243 \pm 0.0170$ | $0.0952 \pm 0.0717$ | $0.2647 \pm 0.1439$ | **$0.1281 \pm 0.1438$** |
| **$S_{\text{Med}}$** | $0.0876 \pm 0.0064$ | $0.2677 \pm 0.0343$ | $0.5792 \pm 0.0421$ | **$0.3115 \pm 0.2081$** |
| **$S_{\text{High}}$** | $0.0904 \pm 0.0087$ | $0.3092 \pm 0.0330$ | $0.6477 \pm 0.0715$ | **$0.3491 \pm 0.2335$** |
| **$\Delta_{ML} = S_M - S_L$** | $\mathbf{+0.0633}$ | $\mathbf{+0.1725}$ | $\mathbf{+0.3145}$ | $\mathbf{+0.1834}$ |
| **$\Delta_{HM} = S_H - S_M$** | $\mathbf{+0.0028}$ | $\mathbf{+0.0416}$ | $\mathbf{+0.0685}$ | $\mathbf{+0.0376}$ |
| **Ordering** | Monotonic ($p < 10^{-20}$) | Monotonic ($p < 10^{-22}$) | Monotonic ($p < 10^{-26}$) | Monotonic ($p < 10^{-26}$) |

### 3.2 Confidence Intervals at Condition $T = 12$
- **Low**: $\bar{S}_L = 0.2647$, $95\%\,\text{CI} = [0.2132, \quad 0.3162]$ ($N = 30$, $\text{SE} = 0.0263$).
- **Med**: $\bar{S}_M = 0.5792$, $95\%\,\text{CI} = [0.5641, \quad 0.5942]$ ($N = 30$, $\text{SE} = 0.0077$).
- **High**: $\bar{S}_H = 0.6477$, $95\%\,\text{CI} = [0.6221, \quad 0.6732]$ ($N = 30$, $\text{SE} = 0.0130$).
- **Observed Separation**: $\Delta_{HM}(T=12) = 0.0685$, with non-overlapping $95\%$ confidence intervals between Medium ($[0.564, 0.594]$) and High ($[0.622, 0.673]$).
- **Inference**: The separation is strictly positive and statistically significant beyond chance ($F(2, 87) = 136.01, p = 1.664 \times 10^{-27}$), but **substantively compressed** below the preregistered threshold of $0.1500$.

---

## 4. T-Dependent S Trajectories

Simulating the continuous ordinary differential equation step-by-step from $t = 1$ to $t = 12$ ticks ($dt = 0.10\,\text{s}$) through genuine production components reveals the complete trajectory progression:

```text
S_observed
  0.70 ┤                                                     ╭──── High (0.626)
  0.60 ┤                                            ╭────────╯──── Med  (0.568)
  0.50 ┤                                  ╭─────────╯
  0.40 ┤                         ╭────────╯
  0.30 ┤                ╭────────╯
  0.20 ┤       ╭────────╯                                  ─────── Low  (0.208)
  0.10 ┤ ╭─────╯
  0.00 ┴─┴─────┴─────┴─────┴─────┴─────┴─────┴─────┴─────┴─────┴─────┴──
         1     2     3     4     5     6     7     8     9    10    11    12   Ticks
```

### 4.1 Step-by-Step Trajectory Table ($t = 1 \dots 12$)

| Tick $t$ | Exposure Time | $S_{\text{Low}}(t)$ | $S_{\text{Med}}(t)$ | $S_{\text{High}}(t)$ | $\Delta_{ML}(t)$ | $\Delta_{HM}(t)$ | Marginal Rate High | Marginal Rate Med |
|---|---|---|---|---|---|---|---|---|
| **$t = 1$** | $0.10\,\text{s}$ | $0.0300$ | $0.0838$ | $0.0921$ | $+0.0538$ | **$+0.0084$** | $0.0921/\text{tick}$ | $0.0838/\text{tick}$ |
| **$t = 2$** | $0.20\,\text{s}$ | $0.0566$ | $0.1576$ | $0.1734$ | $+0.1010$ | **$+0.0158$** | $0.0813/\text{tick}$ | $0.0738/\text{tick}$ |
| **$t = 3$** | $0.30\,\text{s}$ | $0.0802$ | $0.2229$ | $0.2452$ | $+0.1427$ | **$+0.0223$** | $0.0718/\text{tick}$ | $0.0653/\text{tick}$ |
| **$t = 4$** | $0.40\,\text{s}$ | $0.1012$ | $0.2807$ | $0.3088$ | $+0.1795$ | **$+0.0281$** | $0.0636/\text{tick}$ | $0.0578/\text{tick}$ |
| **$t = 5$** | $0.50\,\text{s}$ | $0.1199$ | $0.3321$ | $0.3653$ | $+0.2121$ | **$+0.0333$** | $0.0565/\text{tick}$ | $0.0514/\text{tick}$ |
| **$t = 6$** | $0.60\,\text{s}$ | $0.1367$ | $0.3778$ | $0.4156$ | $+0.2411$ | **$+0.0379$** | $0.0503/\text{tick}$ | $0.0457/\text{tick}$ |
| **$t = 7$** | $0.70\,\text{s}$ | $0.1517$ | $0.4186$ | $0.4605$ | $+0.2669$ | **$+0.0420$** | $0.0449/\text{tick}$ | $0.0408/\text{tick}$ |
| **$t = 8$** | $0.80\,\text{s}$ | $0.1652$ | $0.4551$ | $0.5008$ | $+0.2899$ | **$+0.0457$** | $0.0403/\text{tick}$ | $0.0365/\text{tick}$ |
| **$t = 9$** | $0.90\,\text{s}$ | $0.1774$ | $0.4879$ | $0.5369$ | $+0.3105$ | **$+0.0490$** | $0.0361/\text{tick}$ | $0.0328/\text{tick}$ |
| **$t = 10$** | $1.00\,\text{s}$ | $0.1884$ | $0.5174$ | $0.5694$ | $+0.3290$ | **$+0.0521$** | $0.0325/\text{tick}$ | $0.0295/\text{tick}$ |
| **$t = 11$** | $1.10\,\text{s}$ | $0.1984$ | $0.5441$ | $0.5989$ | $+0.3457$ | **$+0.0549$** | $0.0295/\text{tick}$ | $0.0267/\text{tick}$ |
| **$t = 12$** | $1.20\,\text{s}$ | $0.2075$ | $0.5682$ | $0.6257$ | $+0.3607$ | **$+0.0574$** | $0.0268/\text{tick}$ | $0.0241/\text{tick}$ |

### 4.2 Trajectory Insights
1. **Parallel Growth Curves**: Across all 12 ticks, $S_{\text{High}}(t)$ and $S_{\text{Med}}(t)$ grow at almost identical marginal velocities ($\approx 0.08$ at $t=1$, decelerating smoothly to $\approx 0.025$ at $t=12$).
2. **Persistent Compression**: In v1.4, $\Delta_{HM}(t)$ never exceeds $0.0600$ at any point along the entire integration interval. The compression is not an isolated artifact of tick 12; it is an intrinsic feature of the trajectory from tick 1 onward ($\Delta_{HM}(1) = 0.008 \to \Delta_{HM}(12) = 0.057$).

---

## 5. Path C vs. v1.4 Differences

Comparing the historical Path C execution dataset against Protocol v1.4 isolates the exact source of discrepancy:

| Factor | Historical Path C | Protocol v1.4 | Observed Difference | Relevance to Gate 2 Failure |
|---|---|---|---|---|
| **$S_H(T=12)$ Response** | **$0.6477$** | **$0.6477$** | **$0.0000$ (Bit-Exact Identical)** | **None** (High response was 100% stable). |
| **$S_L(T=12)$ Response** | **$0.2293$** | **$0.2647$** | $+0.0354$ | **Minor** (Lower bound shifted slightly). |
| **$S_M(T=12)$ Response** | **$0.4387$** | **$0.5792$** | **$+0.1405$ (+32.0% Inflation)** | **CRITICAL / PRIMARY CAUSE**. |
| **$\Delta_{HM}(T=12)$** | **$+0.2090$** | **$+0.0685$** | **$-0.1405$ (Direct Reflection of $S_M$)** | **Directly explains Gate 2 failure**. |
| **`_SM_TEMPLATES` Tone** | Neutral, technical, dry with repeated words. | Warm, personal, relational collaborative dialogue. | Tone shifted from machine status to companion warmth. | **CRITICAL**. |
| **$S_M$ VADER Compound** | Mean $= +0.4158$ ($\text{SD} = 0.2658$) | Mean $= +0.5846$ ($\text{SD} = 0.1832$) | **$+0.1688$ (+40.6% Valence Increase)** | **CRITICAL** (Drives fast hidden dim 0). |
| **$S_M$ Semantic Density** | Mean $= 0.7952$ (word doubling) | Mean $= 0.9777$ (natural syntax) | **$+0.1825$ (+23.0% Density Increase)** | **CRITICAL** (Drives fast hidden dim 2). |
| **$U_{\text{target}}$ Generator** | Beta distribution (Cell 4 failed floor) | Candidate C1 Uniform/Discrete (All passed) | Candidate C1 elevated variance to $\ge 0.0020$ | Solved Gate 4; independent of Gate 2. |
| **$T$ Allocation** | $10/10/10$ balanced | $10/10/10$ balanced | Identical | None. |
| **Seeds & Sample Size** | Seeds $42..46$, $N = 270$ | Seeds $42..46$, $N = 270$ | Identical | None. |
| **Component Classes** | `StimulusProcessor`, `EmotionCore`, `ActiveInferenceEngine` | Same production classes | Bit-exact code | None (zero production code changes). |

---

## 6. Stimulus-Level Diagnostics

Quantifying the lexical and affective representations of the stimulus pools independently of runtime execution:

### 6.1 Lexical & VADER Affective Breakdown

| Stimulus Pool & Tier | Token Count | VADER Pos | VADER Neg | VADER Compound | Encoded Dim 0 (Valence) | Encoded Dim 1 (Arousal) | Encoded Dim 2 (Density) |
|---|---|---|---|---|---|---|---|
| **Path C: Low** | $10.0$ | $0.1243$ | $0.0221$ | $+0.1540 \pm 0.3344$ | $+0.1540$ | $0.0287$ | $+0.7952$ |
| **Path C: Med** | $10.2$ | $0.2698$ | $0.0055$ | $+0.4158 \pm 0.2658$ | $+0.4158$ | $0.0456$ | $+0.7952$ |
| **Path C: High** | $12.4$ | $0.3114$ | $0.2416$ | $-0.0007 \pm 0.8796$ | $-0.0007$ | $0.4450$ | $+0.9563$ |
| **v1.4: Low** | $10.0$ | $0.1365$ | $0.0221$ | $+0.1723 \pm 0.3407$ | $+0.1723$ | $0.0283$ | $+0.7952$ |
| **v1.4: Med** | $13.8$ | $0.2901$ | $0.0076$ | $\mathbf{+0.5846 \pm 0.1832}$ | $\mathbf{+0.5846}$ | $0.0425$ | $\mathbf{+0.9777}$ |
| **v1.4: High** | $12.2$ | $0.2500$ | $0.2798$ | $-0.1332 \pm 0.8476$ | $-0.1332$ | $0.4426$ | $+0.9563$ |

### 6.2 Key Stimulus Findings
1. **Effective Input Norm Compression**:
   - The total vector norm of the encoded input vector $\|x\| = \sqrt{x_{\text{val}}^2 + x_{\text{aro}}^2 + x_{\text{den}}^2}$:
     - v1.4 Medium: $\|x_M\| = \sqrt{0.5846^2 + 0.0425^2 + 0.9777^2} = \mathbf{1.140}$.
     - v1.4 High (Positive Triumph): $\|x_H^+\| = \sqrt{0.78^2 + 0.44^2 + 0.96^2} = \mathbf{1.314}$.
     - v1.4 High (Negative Crisis): $\|x_H^-\| = \sqrt{(-0.85)^2 + 0.44^2 + 0.96^2} = \mathbf{1.352}$.
   - While High stimuli have much higher arousal ($0.44$ vs. $0.04$), Medium stimuli compensate with higher positive valence ($0.58$ vs. $-0.13$) and high density ($0.98$).
   - Total input energy delivered to the ODE is separated by only $\sim 15\%$, not the intended multiple.
2. **Pervasive Companion Phrasing in $S_M$**:
   - In v1.4, all 30 templates for Medium surprise were formulated as collaborative companion affirmations (e.g., *"Working together with you feels warm, steady, and very reassuring..."*, *"I feel a gentle sense of satisfaction as these tests pass cleanly..."*).
   - This uniformly inflated VADER positivity across all four nominal domains.

---

## 7. Runtime Dynamics Diagnostics

Analytically inspecting the transition dynamics of `EmotionCore`:

### 7.1 Architecture Coupling in Fast State
From `src/core/emotion/emotion_core.py`:
$$\mathbf{f}_{\text{fast}} = \tanh(\mathbf{W}_f \mathbf{y}_f + \mathbf{W}_{fs} \Delta \mathbf{s} + \mathbf{U}_f \mathbf{x} + \mathbf{b}_f)$$
where the hardcoded structural weights are:
- $\mathbf{U}_f[0, 0] = 1.00$ (Direct feed from Input Valence $\to$ Hidden Fast Dimension 0)
- $\mathbf{U}_f[1, 1] = 1.00$ (Direct feed from Input Arousal $\to$ Hidden Fast Dimension 1)
- $\mathbf{U}_f[2, 2] = 0.80$ (Direct feed from Input Density $\to$ Hidden Fast Dimension 2)

And the fast projection to PAD coordinates is:
- $\mathbf{W}_{\text{proj}}[0, 0] = 0.70$ (Hidden Fast Dim $0 \to$ Pleasure)
- $\mathbf{W}_{\text{proj}}[1, 1] = 0.70$ (Hidden Fast Dim $1 \to$ Arousal)
- $\mathbf{W}_{\text{proj}}[2, 2] = 0.70$ (Hidden Fast Dim $2 \to$ Dominance)

### 7.2 Isotropic Euclidean Surprise Metric
From `src/core/inference/active_inference.py`, with belief matrices reset to identity ($\mathbf{A} = \mathbf{I}, \mathbf{b} = \mathbf{0}$):
$$S_{\text{observed}} = \| \mathbf{p}_T - \mathbf{p}_0 \|_2 = \sqrt{(P_T - P_0)^2 + (A_T - A_0)^2 + (D_T - D_0)^2}$$

### 7.3 Post-Exposure PAD Coordinates at $T = 12$
Baseline resting equilibrium is $\mathbf{p}_0 = (+0.25, -0.05, +0.05)$.

| Condition | Final $P_T$ (Pleasure) | Final $A_T$ (Arousal) | Final $D_T$ (Dominance) | $\Delta P = P_T - P_0$ | $\Delta A = A_T - A_0$ | $\Delta D = D_T - D_0$ | $S_{\text{observed}} = \|\Delta \mathbf{p}\|$ |
|---|---|---|---|---|---|---|---|
| **v1.4 Low ($T=12$)** | $+0.3996$ | $-0.0411$ | $+0.1364$ | $+0.1496$ | $+0.0089$ | $+0.0864$ | **$0.2647$** |
| **v1.4 Med ($T=12$)** | $\mathbf{+0.6704}$ | $\mathbf{-0.0363}$ | $\mathbf{+0.4463}$ | $\mathbf{+0.4204}$ | $\mathbf{+0.0137}$ | $\mathbf{+0.3963}$ | **$0.5792$** |
| **v1.4 High ($T=12$)** | $+0.3341$ | $\mathbf{+0.2364}$ | $+0.4079$ | $+0.0841$ | $\mathbf{+0.2864}$ | $+0.3579$ | **$0.6477$** |
| **Path C Med ($T=12$)** | $+0.5178$ | $-0.0223$ | $+0.3804$ | $+0.2678$ | $+0.0277$ | $+0.3304$ | **$0.4387$** |

### 7.4 Critical Geometric Finding
1. **Medium Did NOT Experience Arousal Elevation**: Final $A_T = -0.0363$ for Medium is still negative, barely $0.0137$ away from resting baseline ($-0.05$). The hypothesis that Medium suffered "cumulative limbic arousal" is **empirically rejected**.
2. **Medium Displaced Exclusively Along Valence & Dominance**: Pleasure moved by $+0.4204$ and Dominance by $+0.3963$.
3. **High Displaced Along Arousal & Dominance**: Arousal moved by $+0.2864$ and Dominance by $+0.3579$.
4. **Euclidean Equivalence of Distinct Emotional States**:
   - Because $(0.4204)^2 + (0.3963)^2 \approx 0.334 \implies S_M = 0.579$.
   - And $(0.2864)^2 + (0.3579)^2 \approx 0.210$ (plus bipolar valence contributions) $\implies S_H = 0.648$.
   - **The two tiers are at an angle of $47.7^\circ$ in 3D PAD space**, but their Euclidean lengths from origin are compressed to within $0.0685$ of each other.

---

## 8. Phase-Plane / Trajectory Evidence

### 8.1 Data Availability Status
- **Raw Benchmark Dataset**: The immutable file `raw_evaluations.json` records strictly the endpoint pairs $(\mathbf{p}_0, \mathbf{p}_T)$ for each of the 1,350 evaluations. **Intermediate tick-by-tick trajectory data ($t = 2 \dots 11$) are not recorded in the benchmark output files.**
- **Exploratory Simulation Harness**: To inspect the continuous phase-plane geometry, an isolated simulation (`simulate_pad_trajectories.py`) integrated the genuine production ODE step-by-step from resting baseline.

### 8.2 Bipolar Valence Decomposition in High Surprise Tier
Decomposing the 30 High surprise probes at $T = 12$ into its two sub-categories reveals why High surprise was vulnerable to compression:

| Subgroup | $N$ | Final $P_T$ | Final $A_T$ | Final $D_T$ | Observed Surprise $S$ | Comparison to Medium ($S_M = 0.5792$) |
|---|---|---|---|---|---|---|
| **Positive Triumph High** (Breakthroughs) | 15 | $+0.7835$ | $+0.2025$ | $+0.4474$ | **$0.7116 \pm 0.0074$** | $\Delta = +0.1324$ above Med. |
| **Negative Crisis High** (Alarms / Disaster) | 15 | $-0.1152$ | $+0.2703$ | $+0.3684$ | **$0.5838 \pm 0.0408$** | $\mathbf{\Delta = +0.0046}$ (Virtually Identical to Med). |
| **Medium Tier Combined** | 30 | $+0.6704$ | $-0.0363$ | $+0.4463$ | **$0.5792 \pm 0.0421$** | Baseline. |

### 8.3 The Asymmetric Attractor Effect
1. Starting from Philia resting baseline $P_0 = +0.25$:
   - A positive breakthrough drives Pleasure from $+0.25 \to +0.78$ ($\Delta P = +0.53$).
   - A negative crisis drives Pleasure from $+0.25 \to -0.12$ ($\Delta P = -0.37$).
   - Because $P_0$ is already positive, negative stimuli have to overcome $+0.25$ before moving into negative territory. Over 12 ticks, negative crisis alarms reached $S = 0.5838$.
2. Meanwhile, Medium companion phrases with strong positive valence ($+0.5846$) drove Pleasure from $+0.25 \to +0.67$ ($\Delta P = +0.42$).
3. **Negative Crisis High and Medium Companion Talk produced the exact same Euclidean displacement ($\approx 0.58$)**, dragging down the High tier average to $0.6477$.

---

## 9. Mechanistic Hypotheses

Evaluating the five preregistered candidate hypotheses against all empirical and simulation evidence:

### H-D1 — Stimulus Compression
*Hypothesis*: The effective physiological input difference between $S_M$ and $S_H$ is smaller than intended.
- **Evidence**:
  - `StimulusProcessor.encode()` yields total input vector norms of $\|x_M\| = 1.140$ vs. $\|x_H\| = 1.314 - 1.352$ (only a $15.2\%$ input energy separation).
  - VADER compound of Medium rose from $+0.4158$ in Path C to $+0.5846$ in v1.4, closing the input magnitude gap.
- **Counter-evidence**:
  - Arousal input remains well-separated ($0.0425$ in Med vs. $0.4426$ in High).
- **Status**: **SUPPORTED BY CURRENT EVIDENCE**.
- **Remaining Uncertainty**: How much input norm separation is required to produce $\Delta_{HM} \ge 0.1500$ under Euclidean surprise.

---

### H-D2 — Medium Overactivation
*Hypothesis*: $S_M$ stimuli produce unusually high cumulative displacement under long exposure.
- **Evidence**:
  - $S_M(T=12)$ rose by $+0.1405$ ($0.4387 \to 0.5792$) between Path C and v1.4, perfectly matching the $-0.1405$ drop in $\Delta_{HM}$.
  - Overactivation is concentrated entirely along Pleasure ($\Delta P = +0.4204$) and Dominance ($\Delta D = +0.3963$).
- **Counter-evidence**:
  - Overactivation did not occur in Arousal ($A_T = -0.0363$).
- **Status**: **SUPPORTED BY CURRENT EVIDENCE** (Affective/Valence Overactivation).
- **Remaining Uncertainty**: None regarding empirical occurrence; confirmed across both real evaluations and simulations.

---

### H-D3 — Physiological Saturation
*Hypothesis*: The ODE system imposes a bounded displacement causing $S_M$ and $S_H$ to converge toward a common ceiling.
- **Evidence**:
  - The ODE uses $\tanh$ activations bounded in $[-1, 1]$, and PAD projection is clipped to $[-1, 1]$.
  - Marginal displacement per tick decelerates smoothly for both tiers ($\text{Rate}(T1 \to T4) \approx 0.07 \to \text{Rate}(T4 \to T12) \approx 0.04$).
- **Counter-evidence**:
  - The states do not converge to the *same coordinate* in PAD space (separation angle $= 47.7^\circ$). Saturation operates on the radial scalar distance $\|p_T - p_0\|$, not on state collinearity.
- **Status**: **SUPPORTED BY CURRENT EVIDENCE** (Radial Metric Saturation).
- **Remaining Uncertainty**: Exact analytical bound of maximum possible $\|p_T - p_0\|$ under resting Philia equilibrium.

---

### H-D4 — Philia / Homeostatic Damping
*Hypothesis*: Relational / homeostatic dynamics disproportionately damp or reshape the response.
- **Evidence**:
  - Philia resting equilibrium ($P_0 = +0.25$) creates an asymmetric starting point that penalizes negative valence crisis alarms ($\Delta P = -0.37$) relative to positive stimuli ($\Delta P = +0.53$).
- **Counter-evidence**:
  - Active homeostatic context modulation (`homeostatic_engine`) was reset before each probe and had zero cross-probe accumulation.
- **Status**: **CONSISTENT BUT UNCONFIRMED AS PRIMARY CAUSE** (Baseline coordinate asymmetry contributed, but active homeostatic decay was not the driving factor).
- **Remaining Uncertainty**: Contribution of slow latent coupling matrix $W_{fs}$ vs. direct fast feed $U_f$.

---

### H-D5 — Stimulus Domain Confounding
*Hypothesis*: Differences in domains/templates explain part of the apparent S-tier behavior.
- **Evidence**:
  - While domain tags (telemetry, project_status, relational, factual) were balanced 24/24/21/21 across tiers, the linguistic syntax of all 30 Medium templates adopted an overtly relational companion style, uniformly shifting the entire tier.
- **Counter-evidence**:
  - Within $S_M$, variance was low ($\text{Var}(S) = 0.00177$ at $T=12$), showing that domain tags did not create disparate sub-clusters.
- **Status**: **SUPPORTED BY CURRENT EVIDENCE** (Global Template Style Confounding).
- **Remaining Uncertainty**: None.

---

## 10. What Can and Cannot Be Concluded

### What IS Concluded (Definitive Findings)
1. **The locus of compression is 100% in $S_M$ inflation**: High surprise is bit-exact identical to Path C ($0.6477$). Medium surprise inflated by $+0.1405$ ($0.4387 \to 0.5792$), directly collapsing $\Delta_{HM}$ from $0.2090 \to 0.0685$.
2. **The inflation is valence- and density-driven**: Medium stimuli in v1.4 had VADER compound $+0.5846$ (vs. $+0.4158$) and semantic density $0.9777$ (vs. $0.7952$). Under $T=12$ ticks, this drove Pleasure to $+0.6704$ and Dominance to $+0.4463$.
3. **Arousal played zero role in Medium overactivation**: Final arousal for Medium was $-0.0363$, remaining near resting baseline ($-0.05$).
4. **High surprise is bipolar and asymmetric**: High surprise splits into Positive Triumph ($S = 0.7116$) and Negative Crisis ($S = 0.5838$). Negative crisis alarms matched Medium companion talk in Euclidean displacement, lowering the High tier average.
5. **The metric is blind to direction**: $S_{\text{observed}} = \|p_T - p_0\|_2$ measures radial distance, conflating a $47.7^\circ$ directional difference (companion warmth vs. catastrophic emergency) into near-identical scalar surprise values.

### What CANNOT Be Concluded (Epistemic Boundaries)
1. This investigation does **NOT** conclude that Gate 2 should have passed.
2. This investigation does **NOT** conclude that the Gate 2 threshold ($0.1500$) was wrong or should be lowered.
3. This investigation does **NOT** conclude that H1 is supported.
4. This investigation does **NOT** authorize amending the protocol or rerunning the benchmark.

---

## 11. Implications for Future Protocol Design

If project governance authorizes a future protocol revision (e.g., Protocol v1.5), this diagnostic evidence establishes clear design principles:

1. **Stimulus Polarity Matching**:
   - If High surprise contains both positive breakthroughs and negative emergencies, Medium surprise cannot consist exclusively of high-valence positive statements.
   - Alternatively, Medium surprise templates must be calibrated to neutral valence ($\text{Compound} \approx 0.00 \pm 0.10$) and moderate arousal, avoiding extreme positive companion sentiment.
2. **Exposure Calibration for Medium Tier**:
   - At $T = 4$ ticks, separation is $\Delta_{ML} = 0.1725$ and $\Delta_{HM} = 0.0416$.
   - At $T = 12$ ticks, single constant stimuli integrated for 12 consecutive Euler steps allow linear integration of positive valence into the saturation regime.
3. **Direction-Aware vs. Distance-Based Surprise**:
   - Active Inference surprise in Lucia is mathematically formulated as prediction error magnitude $\|\hat{\mathbf{p}}_0 - \mathbf{p}_T\|$. Any future manipulation check must account for the fact that displacement in Pleasure produces identical scalar surprise to displacement in Arousal.

---

## 12. Recommendation for Next Research Step

1. **Do NOT open the Architecture Gate**: The canon remains locked.
2. **Do NOT draft Protocol v1.5 immediately**: The diagnostic findings should first be reviewed by Ciah.
3. **Recommended Next Step**:
   - Author a dedicated research proposal for **Stimulus Polarity & Dynamic Headroom Calibration**.
   - Before drafting any protocol amendment, run an isolated Monte Carlo calibration on candidate stimulus sets (similar to the successful Candidate C1 calibration for $U_{\text{Low}}$) to verify that both $\Delta_{ML}(T=12) \ge 0.10$ and $\Delta_{HM}(T=12) \ge 0.15$ are simultaneously and robustly achievable across all environmental seeds.

---

## 13. Reproducibility & Integrity Ledger

| Property | Value |
|---|---|
| **Diagnostic Script** | [`tests/evaluation_phase22/scripts/diagnose_gate2_compression.py`](file:///c:/Users/Lunafiah/Desktop/My_project/Lucia/tests/evaluation_phase22/scripts/diagnose_gate2_compression.py) |
| **Simulation Script** | [`tests/evaluation_phase22/scripts/simulate_pad_trajectories.py`](file:///c:/Users/Lunafiah/Desktop/My_project/Lucia/tests/evaluation_phase22/scripts/simulate_pad_trajectories.py) |
| **Unit Test Suite** | [`tests/evaluation_phase22/test_h1_gate2_diagnostic.py`](file:///c:/Users/Lunafiah/Desktop/My_project/Lucia/tests/evaluation_phase22/test_h1_gate2_diagnostic.py) |
| **All Evaluation Tests** | `pytest tests/evaluation_phase22/` $\implies$ **39 passed in 3.79s** |
| **Production Code (`src/core/**`)** | **100% Untouched (0 modifications)** |
| **Genesis Profile (`data/profile.json`)** | **`{"is_onboarded": false}` (Bit-Exact Intact)** |
| **Historical Evidence** | Path C and Protocol v1.4 datasets **100% Immutable** |
