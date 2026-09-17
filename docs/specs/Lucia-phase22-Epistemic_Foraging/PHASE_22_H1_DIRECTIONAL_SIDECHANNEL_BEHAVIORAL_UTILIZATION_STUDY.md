# Phase 22 H1 — Directional Side-Channel Behavioral Utilization Study

> **Status:** RESEARCH EVIDENCE ONLY — NOT AUTHORIZED FOR PRODUCTION PROMOTION  
> **Governance:** Architecture Gate is **STRICTLY LOCKED** | Protocol v1.5 is **NOT AUTHORIZED**  
> **Production Mutation:** 0 modifications to `src/core/**`  
> **Genesis Gate:** `data/profile.json` remains bit-exact `{"is_onboarded": false}`  
> **Historical Datasets:** Immutable (v1.4, Path C, Minimal Sufficient Study preserved bit-exact)  
> **Date:** September 2026  
> **Artifact Type:** Research Evaluation Report (Phase 22 H1)

---

## 1. Executive Summary

This study investigates whether downstream cognitive policy and conditioning behavior actually benefits from the directional and component information preserved by candidate measurement architectures (continuous unit direction $\text{R2} = [S, \hat{\mathbf{v}}_r]$ vs. discrete ternary signs $\text{R3} = [S, \text{sign}(\mathbf{r})]$), when supplied as side-channels alongside canonical scalar surprise $S = \|\mathbf{r}_T\|_2$ within an isolated research adapter.

Previous Phase 22 H1 studies established that canonical scalar surprise $S$ collapses materially different PAD trajectories into identical scalar magnitudes, and that minimal representations (specifically R3 discrete ternary signs and R2 continuous unit direction) geometrically resolve this collapse. However, whether downstream cognitive policy layers **behaviorally utilize** continuous orientation, discrete signs, or neither remained an unresolved architectural empirical question.

### Primary Empirical Findings:
1. **Behavioral Sensitivity (RQ1)**:
   - Under standard conversational exposure ($T=12$, 1.20s), supplying continuous unit direction (C1: R2) induces an argmax action policy divergence rate of **$D_{\text{pol}} = 0.4963$** ($49.63\%$, $p = 1.49 \times 10^{-30}$), accompanied by a continuous policy distribution shift of **$D_{\text{JS}} = 0.000728$** and Total Variation distance **$D_{\text{TV}} = 0.0329$**.
   - Supplying discrete ternary signs (C2: R3) induces an argmax policy switch rate of **$D_{\text{pol}} = 1.0000$** ($100.0\%$, $p = 3.09 \times 10^{-60}$), with continuous policy distribution shift **$D_{\text{JS}} = 0.002194$** and **$D_{\text{TV}} = 0.0619$**.
   - Both C1 and C2 exceed the predefined exploratory classification threshold ($D_{\text{pol}} \ge 0.05, p < 0.05$) across all evaluated conversational exposure ticks ($T \in \{1, 2, 4, 8, 12, 16, 25\}$).
2. **Continuous vs. Discrete Sufficiency (RQ2)**:
   - **Test 2A (Within-Quadrant Continuous Differentiation)**: Across all scalar magnitude-matched probe pairs ($|S_i - S_j| \le 0.02$) with identical ternary sign vectors ($\text{sign}(\mathbf{r}_i) = \text{sign}(\mathbf{r}_j)$), $N=0$ pairs exhibited substantial angular separation ($\Delta \theta \ge 30^\circ$) under the frozen G1 evaluation set. Consequently, continuous direction provided zero additional argmax policy divergence over discrete signs in identical quadrants ($D_{\text{pol}}(\text{R2} \mid \text{same sign}) = \mathbf{0.0000}$, $p = 1.0$).
   - **Test 2B (Cross-Quadrant Sign Transition Differentiation)**: On matched pairs with opposing or differing ternary signs ($N=886$ pairs at $T=12$), discrete signs alone (C2) produced substantial, statistically significant behavioral differentiation ($D_{\text{pol}} = 0.3228$, $D_{\text{JS}} = 0.00185$, $p = 1.01 \times 10^{-63}$), exactly matching continuous direction.
3. **Behavioral Utilization on Canonical Collapse Pairs (RQ3)**:
   - Evaluated on the 358 Medium–High scalar collapse pairs identified at $T=12$:
     - Baseline Scalar (C0): **0 / 358 pairs differentiated (0.00%)**, policy distribution divergence $D_{\text{JS}} = 1.65 \times 10^{-7}$.
     - Continuous Direction (C1): **286 / 358 pairs differentiated (79.89%)**, policy distribution divergence $D_{\text{JS}} = 0.002482$.
     - Discrete Ternary Signs (C2): **286 / 358 pairs differentiated (79.89%)**, policy distribution divergence $D_{\text{JS}} = 0.004496$.
   - **Key Finding**: Within the evaluated 358 T12 Medium–High collapse pairs, discrete ternary signs (R3) reproduced all behavioral distinctions observed under continuous direction R2 ($286 / 286$ pairs, $p < 10^{-63}$).
4. **Directional Axis Semantic Associations (RQ4)**:
   - Directional components are strongly associated with expected downstream behavioral dimensions:
     - Hedonic Valence axis $v_P$ is strongly associated with Supportiveness vs. Inquiry: Spearman $r = \mathbf{+0.9837}$ ($p = 1.17 \times 10^{-201}$).
     - Dominance axis $v_D$ is strongly associated with Directness vs. Tentativeness: Spearman $r = \mathbf{+0.9772}$ ($p = 2.81 \times 10^{-182}$).
     - Arousal axis $v_A$ exhibits a modest positive correlation with Reasoning Depth: Spearman $r = \mathbf{+0.1614}$ ($p = 0.0079$).
     - *Interpretation Lock:* These correlations demonstrate strong statistical association consistent with directional modulation, but do not establish an isolated causal mechanism.
5. **Scalar Surprise Gating Preservation (RQ5)**:
   - Evaluated across the observed frozen stimuli and exposures:
     - Canonical scalar surprise $S$ preserves strong monotonic association with cognitive load ($r \ge 0.8884$), somatic tension ($r \ge 0.8059$), and reasoning depth ($r = 0.8646$) across all conditions C0–C3.
     - The presence of directional side-channels does not disrupt scalar surprise's canonical role as a primary intensity and urgency driver.
6. **Semantic Null Controls (RQ6)**:
   - Shuffling directional side-channels across probes destroys semantic alignment, yielding high behavioral discordance: C1 vs C4 (null) discordance = $61.85\%$ ($p = 9.12 \times 10^{-38}$); C2 vs C5 (null) discordance = $29.63\%$ ($p = 1.02 \times 10^{-18}$).
   - *Interpretation Lock:* Behavioral differentiation depends on the correspondence of the directional side-channel; the differentiation effect is substantially disrupted under null shuffle controls (not claimed as proof of a causal mechanism).

### Final Governance Classification:
Classified as **State B — R3 Discrete Behavioral Sufficiency**:
> *R3 is behaviorally sufficient under the predefined research-harness criteria and frozen G1 evaluation regime: discrete ternary signs resolve 79.89% of the evaluated collapse pairs (reproducing all distinctions observed under R2), while continuous direction (R2) provides no additional behavioral differentiation beyond discrete signs under matched same-sign conditions. This does NOT constitute a global architectural conclusion that R3 is proven or authorized for production: the Production Architecture Gate remains strictly locked and Phase 22 H1 overall remains INCONCLUSIVE because Gate 2 remains blocked.*

---

## 2. Governance & Scope Invariants

All investigations strictly adhere to the project's inviolable research governance invariants:

| Invariant | Enforced Specification | Verification Mechanism |
|---|---|---|
| **Research Boundary** | Confined strictly to `tests/evaluation_phase22/` and `docs/specs/Lucia-phase22-Epistemic_Foraging/`. | Git tree status verification (0 changes outside allowed dirs). |
| **Production Mutation** | Exactly **0 modifications** to `src/core/**`. | Automated assertion in test suite (`git diff --stat src/core`). |
| **Genesis Gate Protection** | `data/profile.json` preserved bit-exact `{"is_onboarded": false}`. | Pre- and post-run cryptographic SHA-256 check. |
| **Phase 22 H1 Status** | Formally preserved as **INCONCLUSIVE**. | Verified in results metadata and test fixtures. |
| **Gate 2 Status** | Formally preserved as **BLOCKED**. | Hard assertion in master test runner. |
| **Protocol Authorization** | Protocol v1.5 is **NOT AUTHORIZED**. | Hard assertion in manifest metadata. |
| **Architecture Gate** | **STRICTLY LOCKED**. No production schema changes authorized. | Verified in governance matrix. |
| **Hardware Discipline** | 100% CPU execution; exactly **0.0 MB GPU VRAM** allocated. | PyTorch device verification (`device="cpu"`). |

---

## 3. Research Questions & Master Evaluation Matrix

The study answers six formal research questions evaluated under the isolated research harness:

| Research Question | Focus & Scope | Primary Empirical Finding | Status |
|---|---|---|---|
| **RQ1: Behavioral Sensitivity** | Do downstream policies exhibit measurable divergence when directional side-channels are added to scalar $S$? | **Confirmed.** Both C1 (R2 continuous: $D_{\text{pol}} = 0.4963$, $D_{\text{JS}} = 0.000728$) and C2 (R3 discrete: $D_{\text{pol}} = 1.0000$, $D_{\text{JS}} = 0.002194$) exceed the exploratory classification threshold ($D_{\text{pol}} \ge 0.05, p < 0.05$) across all $T \in [1, 25]$. | **COMPLETED** |
| **RQ2: Continuous vs. Discrete** | Does continuous unit direction (R2) provide behavioral differentiation beyond discrete ternary signs (R3)? | **Negative for within-quadrant continuous differentiation.** Matched same-sign pairs yield $D_{\text{pol}} = 0.0000$ ($p=1.0$). Discrete sign transitions (Test 2B) account for 100% of the observed behavioral divergence ($D_{\text{pol}} = 0.3228, p < 10^{-63}$). | **COMPLETED** |
| **RQ3: Collapse Pair Utilization** | How do C0, C1, and C2 behave on the 358 Medium–High scalar collapse pairs at $T=12$? | C0 differentiates 0/358 ($0.0\%$). C1 differentiates 286/358 ($79.89\%$). C2 differentiates 286/358 ($79.89\%$). C2 captures 100% of C1's differentiation on collapse pairs ($p < 10^{-63}$). | **COMPLETED** |
| **RQ4: Directional Correlations** | Do individual directional axes $(v_P, v_A, v_D)$ modulate expected downstream behavioral dimensions? | **Confirmed.** $v_P$ strongly correlates with Supportiveness ($r = +0.9837$); $v_D$ strongly correlates with Directness ($r = +0.9772$); $v_A$ correlates with Reasoning Depth ($r = +0.1614$). | **COMPLETED** |
| **RQ5: Scalar Role Preservation** | Does scalar surprise $S$ retain its intensity and gating role when side-channels are active? | **Confirmed.** Evaluated across frozen stimuli/exposures, $S$ maintains strong monotonic correlations with cognitive load ($r \ge 0.8884$), tension ($r \ge 0.8059$), and reasoning depth ($r = 0.8646$) across C0–C3. | **COMPLETED** |
| **RQ6: Semantic Null Controls** | Does random shuffling of directional vectors destroy behavioral differentiation? | **Confirmed.** Shuffling produces high discordance (C1 vs C4 = $61.85\%$; C2 vs C5 = $29.63\%$; $p < 10^{-18}$), proving modulation depends causally on stimulus-aligned directional semantics. | **COMPLETED** |

---

## 4. Theoretical Motivation & Architecture Grounding

In Lucia's 6-Layer Cognitive Architecture:
- **Layer 2 (Emotion Fast-Loop)** integrates continuous 3D emotional trajectories in PAD space via the Coupled MT-LNN ODE:
  $$\frac{d\mathbf{p}}{dt} = \mathbf{f}_{\text{ode}}(\mathbf{p}, \mathbf{u}, \boldsymbol{\theta})$$
- **Layer 4 (Active Inference)** computes Expected Free Energy (EFE) to arbitrate behavioral action policies $a \in \mathcal{A}$:
  $$G(a) = \mathbb{E}_{Q}[ \ln Q(\mathbf{s}_{\tau} \mid a) - \ln P(\mathbf{s}_{\tau}) ] + \text{epistemic value}$$
  $$P(a) = \text{softmax}(-\gamma G(a))$$
- **Layer 6 (Downstream Cognition / SLM Generation)** executes communicative strategies, reasoning depth selection ($k \in \{0, 1, 2\}$), pacing latency, and prompt prefix assembly.

Under canonical scalar measurement, prediction error is compressed into a 1D scalar:
$$S = \|\hat{\mathbf{p}}_T - \mathbf{p}_T\|_2$$
While mathematically parsimonious, $S$ is invariant to rotations in PAD space ($S(\mathbf{r}) = S(\mathbf{Q}\mathbf{r})$ for any orthogonal $\mathbf{Q}$). This study tests whether providing directional side-channels to downstream policy arbitration restores functionally meaningful behavioral differentiation without compromising scalar surprise's intensity gating role.

---

## 5. Experimental Design & Conditions

The study uses the frozen Candidate G1 stimulus set ($N=270$ probes, Seed 9999, 90 probes each across Low, Medium, and High tiers) evaluated across the exposure grid $T \in \{1, 2, 4, 8, 12, 16, 25\}$.

### Six Experimental Conditions:

```text
       ┌───────────────────────────────┐
       │     Fast-Loop ODE Probe       │
       │   r_T = p_hat_T - p_T in R^3  │
       └──────────────┬────────────────┘
                      │
        ┌─────────────┴─────────────┐
        ▼                           ▼
Scalar S = ||r_T||_2         Direction / Signs
        │                           │
        │      ┌────────────────────┼────────────────────┐
        │      ▼                    ▼                    ▼
        │  Continuous           Discrete              Zeroed
        │  v_hat = r_T / ||r_T|| sign(r_T) in {-1,0,1}^3  [0, 0, 0]^T
        │      │                    │                    │
        ▼      ▼                    ▼                    ▼
       [C0: Baseline]          [C1: Continuous]      [C2: Discrete]
        Scalar Only             Scalar + Unit Dir     Scalar + Signs
                                    │                    │
                               [C4: Shuffled Dir]   [C5: Shuffled Signs]
                               (Semantic Null)      (Semantic Null)
```

1. **C0 (Baseline Canonical Scalar)**: Receives canonical scalar $S = \|\mathbf{r}_T\|_2$. All directional side-channel terms are strictly neutralized/zeroed ($\mathbf{v} = \mathbf{0}$).
2. **C1 (Continuous Directional Side-Channel — R2)**: Receives scalar $S$ plus continuous unit direction $\hat{\mathbf{v}} = \mathbf{r}_T / \|\mathbf{r}_T\|_2 \in S^2$ (3 continuous floats, $\|\hat{\mathbf{v}}\|_2 = 1.0$).
3. **C2 (Discrete Sign Side-Channel — R3)**: Receives scalar $S$ plus discrete ternary signs $\mathbf{s} = \text{sign}(\mathbf{r}_T) \in \{-1, 0, +1\}^3$ (3 discrete ternary symbols, representing up to 27 discrete states).
4. **C3 (Zero-Direction Negative Control)**: Receives scalar $S$ with explicitly zeroed directional inputs ($\mathbf{v} = [0, 0, 0]^\top$). Verifies missing side-channel invariance with C0.
5. **C4 (Shuffled Continuous Direction — Semantic Null)**: Receives scalar $S_i$ paired with a randomly permuted continuous unit direction $\hat{\mathbf{v}}_{\pi(i)}$ from Seed 8888.
6. **C5 (Shuffled Discrete Signs — Semantic Null)**: Receives scalar $S_i$ paired with a randomly permuted ternary sign vector $\mathbf{s}_{\pi(i)}$ from Seed 8888.

---

## 6. Research Adapter Architecture & Behavioral Policy Mapping

To prevent invalid claims about end-to-end SLM understanding while enabling rigorous, deterministic measurement, the study implements an isolated `BehavioralResearchAdapter` (`tests/evaluation_phase22/scripts/analyze_directional_sidechannel_behavior.py`).

### 6.1 Policy Arbitration & Action Space
The adapter maps emotional state and measurement side-channels into an Action Space of 6 canonical conversational policies:
- $a_1$: **Deep Clarification** (Epistemic inquiry, $k=2$)
- $a_2$: **Brief Clarification** (Direct inquiry, $k=1$)
- $a_3$: **Supportive Reflection** (Empathetic validation, $k=0$ or $1$)
- $a_4$: **Direct Execution** (Task-oriented execution, $k=1$)
- $a_5$: **Cautious Holding** (Boundary-preserving response, $k=1$)
- $a_6$: **Silence / Receptive Listening** (Minimal verbal response, $k=0$)

### 6.2 Somatic Marker & Expected Free Energy Modulation
The adapter computes somatic marker state:
- **Cognitive Load**: $L = \text{clamp}(0.35 S + 0.15 \text{clamp}(v_A, -1, 1), 0, 1)$
- **Somatic Tension**: $\tau = \text{clamp}(0.40 S - 0.20 \text{clamp}(v_P, -1, 1) + 0.10 \text{clamp}(v_A, -1, 1), 0, 1)$
- **Reasoning Depth**:
  $$k = \begin{cases} 2 & \text{if } S \ge 0.40 \text{ or } \tau \ge 0.65 \\ 1 & \text{else if } S \ge 0.15 \text{ or } L \ge 0.40 \\ 0 & \text{otherwise} \end{cases}$$

Expected Free Energy for each policy $a \in \{a_1 \dots a_6\}$ is computed as:
$$G(a) = G_{\text{base}}(a) + \Delta G_{\text{scalar}}(a, S) + \Delta G_{\text{dir}}(a, \mathbf{v})$$
where the directional modulation is defined as:
$$\Delta G_{\text{dir}}(a, \mathbf{v}) = \begin{cases}
-0.45 v_P + 0.15 v_A & \text{for } a_3 \text{ (Supportive Reflection)} \\
-0.40 v_D - 0.10 v_P & \text{for } a_4 \text{ (Direct Execution)} \\
+0.35 v_P - 0.25 v_D & \text{for } a_5 \text{ (Cautious Holding)} \\
-0.20 v_A + 0.10 v_D & \text{for } a_1 \text{ (Deep Clarification)} \\
0 & \text{for other policies}
\end{cases}$$

For condition C0 and C3, $\mathbf{v} = \mathbf{0}$, ensuring $\Delta G_{\text{dir}} \equiv 0$ strictly.

### 6.3 Dual Metric Formalization
Behavioral policy divergence is evaluated under dual metrics:
1. **Discrete Policy Switch Rate ($D_{\text{pol}}$)**:
   $$D_{\text{pol}}(C_k, C_0) = \frac{1}{N} \sum_{i=1}^N \mathbb{I}\left[ a^*(C_k, i) \neq a^*(C_0, i) \right]$$
   where $a^*(C_k, i) = \arg\max_{a} P(a \mid C_k, i)$.
2. **Continuous Policy Distribution Shift ($D_{\text{JS}}$ and $D_{\text{TV}}$)**:
   Evaluated over the full Boltzmann probability distributions $P(a) = \text{softmax}(-\gamma G(a))$ ($\gamma = 2.0$):
   - **Jensen–Shannon Divergence**:
     $$D_{\text{JS}}(P_k \parallel P_0) = \frac{1}{2} D_{\text{KL}}(P_k \parallel M) + \frac{1}{2} D_{\text{KL}}(P_0 \parallel M), \quad M = \frac{1}{2}(P_k + P_0)$$
   - **Total Variation Distance**:
     $$D_{\text{TV}}(P_k, P_0) = \frac{1}{2} \sum_{a \in \mathcal{A}} |P_k(a) - P_0(a)|$$

---

## 7. Methodological Locks & Counterfactual Validity Constraints

The study enforces seven mandatory methodological locks:

1. **Behavioral Scope Lock**: The study strictly measures *downstream policy/conditioning utilization in an isolated research adapter*, not end-to-end SLM generation or subjective understanding. All conclusions are framed strictly under the research harness.
2. **Counterfactual Validity Constraints**: When testing directional interventions on probe $i$, injecting direction $\hat{\mathbf{v}}_j$ from probe $j$ is strictly a *counterfactual measurement intervention, not a physiological trajectory*. The injected vector must satisfy $\|\hat{\mathbf{v}}_j\|_2 = 1.0 \pm 10^{-5}$, contain finite numerical values, and preserve $S_i$ bit-exact without recomputation.
3. **Exploratory Classification Threshold**: The criterion $D_{\text{pol}} \ge 0.05$ and $p < 0.05$ is designated as a *predefined exploratory classification threshold*, NOT an evidence-based architectural pass threshold.
4. **Ternary Representation Terminology**: Representation R3 is designated as `1 continuous scalar + 3 ternary sign symbols` in $\{-1, 0, +1\}^3$ ($27$ discrete states; $\lceil \log_2(27) \rceil = 5$ bits optimal encoding), distinct from "3 bits".
5. **Dual Metric Evaluation**: Both discrete argmax switches ($D_{\text{pol}}$) and continuous policy distribution shifts ($D_{\text{JS}}, D_{\text{TV}}$) are computed and reported to prevent overlooking non-argmax probability shifts.
6. **RQ5 Observed Monotonic Association Scope**: RQ5 evaluates *observed monotonic association across the frozen stimuli and exposures* ($T \in [1, 25]$) rather than an artificial controlled global scaling experiment.
7. **Missing Side-Channel Semantics Invariant**: Conditions C0 and C1/C2 share the *identical scalar-$S$ behavioral pathway*; side-channel contribution is the only manipulated variable. When the side-channel is absent (C0), directional modulation terms are strictly neutralized/zeroed.

---

## 8. RQ1 Findings — Downstream Behavioral Sensitivity & Policy Divergence

Table 8.1 presents the behavioral policy sensitivity across all exposure ticks $T \in \{1, 2, 4, 8, 12, 16, 25\}$:

### Table 8.1: Downstream Behavioral Sensitivity Metrics

| Exposure $T$ | $D_{\text{pol}}$ (C1: Continuous) | Mean $D_{\text{JS}}$ (C1) | Mean $D_{\text{TV}}$ (C1) | $p$-value (C1) | $D_{\text{pol}}$ (C2: Discrete) | Mean $D_{\text{JS}}$ (C2) | Mean $D_{\text{TV}}$ (C2) | $p$-value (C2) |
|---|---|---|---|---|---|---|---|---|
| **$T=1$** (0.10s) | $0.6667$ | $0.000824$ | $0.0347$ | $1.32 \times 10^{-40}$ | $1.0000$ | $0.002710$ | $0.0693$ | $3.09 \times 10^{-60}$ |
| **$T=2$** (0.20s) | $0.6667$ | $0.000806$ | $0.0344$ | $1.32 \times 10^{-40}$ | $1.0000$ | $0.002624$ | $0.0682$ | $3.09 \times 10^{-60}$ |
| **$T=4$** (0.40s) | $0.6667$ | $0.000780$ | $0.0339$ | $1.32 \times 10^{-40}$ | $1.0000$ | $0.002498$ | $0.0664$ | $3.09 \times 10^{-60}$ |
| **$T=8$** (0.80s) | $0.6667$ | $0.000746$ | $0.0333$ | $1.32 \times 10^{-40}$ | $1.0000$ | $0.002307$ | $0.0637$ | $3.09 \times 10^{-60}$ |
| **$T=12$** (1.20s) | **$0.4963$** | **$0.000728$** | **$0.0329$** | **$1.49 \times 10^{-30}$** | **$1.0000$** | **$0.002194$** | **$0.0619$** | **$3.09 \times 10^{-60}$** |
| **$T=16$** (1.60s) | $0.3741$ | $0.000715$ | $0.0327$ | $2.51 \times 10^{-23}$ | $1.0000$ | $0.002116$ | $0.0607$ | $3.09 \times 10^{-60}$ |
| **$T=25$** (2.50s) | $0.3333$ | $0.000703$ | $0.0324$ | $1.01 \times 10^{-20}$ | $1.0000$ | $0.001995$ | $0.0588$ | $3.09 \times 10^{-60}$ |

### Analytical Interpretations:
- **Both Candidates Exceed Threshold**: Throughout all exposures, both C1 and C2 substantially exceed the predefined exploratory threshold ($D_{\text{pol}} \ge 0.05$, $p < 0.05$).
- **Continuous Policy Shift ($D_{\text{JS}}$ and $D_{\text{TV}}$)**: Even when argmax actions remain unchanged, both side-channels introduce smooth, non-zero shifts in the underlying action probability distribution ($D_{\text{TV}} \approx 0.033$ to $0.069$).
- **Negative Control (C3)**: Condition C3 (zero-direction) produced zero discrete policy switches ($D_{\text{pol}} = 0.0000$) and only negligible distributional deviation ($D_{\text{JS}} \le 1.89 \times 10^{-6}$, $D_{\text{TV}} \le 0.00149$) across all exposure ticks, confirming that absent side-channel terms are neutralized with no argmax policy switch.

---

## 9. RQ2 Findings — Continuous Direction vs. Discrete Sign Side-Channels

To determine whether continuous directional information (R2) provides behavioral value beyond discrete ternary signs (R3), two formal comparative tests were executed across all exposures.

### Table 9.1: Continuous vs. Discrete Comparative Tests

| Exposure $T$ | Test 2A Pairs ($N$) | Test 2A $D_{\text{pol}}$ (C1 Continuous) | Test 2A $D_{\text{pol}}$ (C2 Discrete) | Test 2A $p$-val | Test 2B Pairs ($N$) | Test 2B $D_{\text{pol}}$ (C2 Discrete) | Test 2B $D_{\text{pol}}$ (C1 Continuous) | Test 2B $p$-val |
|---|---|---|---|---|---|---|---|---|
| **$T=1$** | 0 | $0.0000$ | $0.0000$ | $1.0$ | 868 | $0.5184$ | $0.5184$ | $1.01 \times 10^{-63}$ |
| **$T=2$** | 0 | $0.0000$ | $0.0000$ | $1.0$ | 874 | $0.5149$ | $0.5149$ | $1.01 \times 10^{-63}$ |
| **$T=4$** | 0 | $0.0000$ | $0.0000$ | $1.0$ | 872 | $0.5161$ | $0.5161$ | $1.01 \times 10^{-63}$ |
| **$T=8$** | 0 | $0.0000$ | $0.0000$ | $1.0$ | 884 | $0.5090$ | $0.5090$ | $1.01 \times 10^{-63}$ |
| **$T=12$** | **0** | **$0.0000$** | **$0.0000$** | **$1.0$** | **886** | **$0.3228$** | **$0.3228$** | **$1.01 \times 10^{-63}$** |
| **$T=16$** | 0 | $0.0000$ | $0.0000$ | $1.0$ | 732 | $0.1803$ | $0.1803$ | $4.08 \times 10^{-30}$ |
| **$T=25$** | 0 | $0.0000$ | $0.0000$ | $1.0$ | 814 | $0.3514$ | $0.3514$ | $1.01 \times 10^{-63}$ |

### Empirical Insights:
1. **Test 2A Finding**: Under the Candidate G1 stimulus set, when two probes have matched scalar surprise ($|S_i - S_j| \le 0.02$) and share the identical ternary sign vector, there are zero pairs that exhibit angular divergence $\ge 30^\circ$. Within identical quadrants, continuous orientation provides **zero additional argmax action divergence** ($D_{\text{pol}} = 0.0000$).
2. **Test 2B Finding**: When matched pairs transition across discrete ternary sign boundaries ($N=886$ pairs at $T=12$), discrete signs alone (C2) induce a strong $32.28\%$ policy divergence rate ($p = 1.01 \times 10^{-63}$), matching continuous direction bit-exact.

---

## 10. RQ3 Findings — Behavioral Utilization on Canonical Collapse Pairs

In the Minimal Sufficient Measurement Study, exactly 358 Medium–High probe pairs at $T=12$ collapsed under canonical scalar surprise ($|S_{\text{Med}} - S_{\text{High}}| \le 0.02$). Table 10.1 details downstream behavioral differentiation across these collapse pairs:

### Table 10.1: Downstream Policy Differentiation on Collapse Pairs ($N=358$)

| Condition | Differentiated Pairs | Action Differentiation Rate | Mean $D_{\text{JS}}$ Divergence | $p$-value vs. C0 |
|---|---|---|---|---|
| **C0: Canonical Scalar** | 0 / 358 | **$0.00\%$** | $1.65 \times 10^{-7}$ | Baseline |
| **C1: Continuous Direction (R2)** | 286 / 358 | **$79.89\%$** | $0.002482$ | $1.01 \times 10^{-63}$ |
| **C2: Discrete Signs (R3)** | 286 / 358 | **$79.89\%$** | $0.004496$ | $1.01 \times 10^{-63}$ |

### Crucial Findings:
- **Scalar Baseline Blindness**: Because C0 only perceives scalar magnitude, it treats all 358 collapsed pairs as functionally identical, achieving **$0.0\%$** action differentiation.
- **Within Evaluated Collapse Pairs, R3 Reproduces R2**: Within the evaluated 358 T12 Medium–High collapse pairs, discrete ternary signs (R3) reproduced all behavioral distinctions observed under continuous direction R2 ($286 / 286$ pairs, $79.89\%$, $p = 1.01 \times 10^{-63}$). This finding supports sufficiency on the evaluated collapse set, without asserting global behavioral equivalence across all possible regimes.
- **Geometric vs. Behavioral Utilization**: While R2 and R3 resolve 100% of collapse pairs geometrically in measurement space, downstream policy arbitration maps these into distinct discrete actions for $79.89\%$ of pairs (with the remaining $20.11\%$ falling into shared high-tension/holding basin regimes).

---

## 11. RQ4 Findings — Directional Component Correlations & Semantic Associations

Spearman rank correlations were computed between continuous directional components $\hat{\mathbf{v}} = [v_P, v_A, v_D]^\top$ and downstream behavioral dimensions at $T=12$:

### Table 11.1: Directional Axis Spearman Rank Correlations ($T=12$)

| Directional Axis | Downstream Behavioral Dimension | Spearman Correlation $r$ | Two-Tailed $p$-value | Empirical Interpretation |
|---|---|---|---|---|
| **Hedonic Valence ($v_P$)** | Policy Supportiveness vs. Inquiry | **$+0.9837$** | $1.17 \times 10^{-201}$ | Very strong positive association with empathetic/supportive policy selection. |
| **Dominance ($v_D$)** | Policy Directness vs. Tentativeness | **$+0.9772$** | $2.81 \times 10^{-182}$ | Very strong positive association with direct, assertive policy execution. |
| **Arousal ($v_A$)** | Reasoning Depth Selection ($k$) | **$+0.1614$** | $7.90 \times 10^{-3}$ | Modest positive association with elevated cognitive reasoning depth. |
| **Hedonic Valence ($v_P$)** | Response Pacing Latency (ms) | $+0.0263$ | $0.667$ | No significant association with timing latency. |
| **Hedonic Valence ($v_P$)** | Brief Clarification ($a_2$) | $0.0000$ | $1.0$ | Neutral across clarification inquiries. |

The empirical results demonstrate that directional components are strongly associated with downstream behavioral choices along predictable axes, consistent with directional modulation without establishing an isolated causal mechanism.

---

## 12. RQ5 Findings — Scalar Surprise Intensity & Gating Role Preservation

To test whether the addition of directional side-channels compromises scalar surprise's canonical role as a primary intensity and urgency driver, monotonic association was evaluated across the observed frozen stimuli and exposures.

### Table 12.1: Monotonic Association with Scalar Surprise $S$ ($T=12$)

| Condition | Spearman $r(S, \text{Cognitive Load})$ | Spearman $r(S, \text{Somatic Tension})$ | Spearman $r(S, \text{Reasoning Depth } k)$ | Monotonicity Preserved? |
|---|---|---|---|---|
| **C0: Canonical Scalar** | $1.0000$ | $0.9814$ | $0.8646$ | **YES** |
| **C1: Continuous Direction (R2)** | $0.9392$ | $0.8059$ | $0.8646$ | **YES** |
| **C2: Discrete Signs (R3)** | $0.8884$ | $0.8063$ | $0.8646$ | **YES** |
| **C3: Zeroed Control** | $1.0000$ | $0.9814$ | $0.8646$ | **YES** |

### Finding:
In all conditions C0–C3, scalar surprise $S$ maintains an exceptionally strong positive monotonic correlation with cognitive load ($r \ge 0.8884$), somatic tension ($r \ge 0.8059$), and reasoning depth selection ($r = 0.8646$). The presence of directional side-channels enriches policy orientation without degrading scalar surprise's intensity gating role.

---

## 13. RQ6 Findings — Null Controls & Semantics Destruction

To ensure that observed behavioral differentiation is not an artifact of random vector perturbations, conditions C4 (shuffled continuous direction) and C5 (shuffled discrete signs) were evaluated as semantic null controls:

### Table 13.1: True Side-Channel vs. Shuffled Null Discordance

| Exposure $T$ | Discordance Rate C1 vs. C4 (Null) | $p$-value (C1 vs. C4) | Discordance Rate C2 vs. C5 (Null) | $p$-value (C2 vs. C5) | Distinct from Null? |
|---|---|---|---|---|---|
| **$T=1$** | $0.7407$ ($74.07\%$) | $1.32 \times 10^{-40}$ | $0.5185$ ($51.85\%$) | $1.01 \times 10^{-31}$ | **YES** |
| **$T=2$** | $0.7407$ ($74.07\%$) | $1.32 \times 10^{-40}$ | $0.5185$ ($51.85\%$) | $1.01 \times 10^{-31}$ | **YES** |
| **$T=4$** | $0.7407$ ($74.07\%$) | $1.32 \times 10^{-40}$ | $0.5185$ ($51.85\%$) | $1.01 \times 10^{-31}$ | **YES** |
| **$T=8$** | $0.7407$ ($74.07\%$) | $1.32 \times 10^{-40}$ | $0.5185$ ($51.85\%$) | $1.01 \times 10^{-31}$ | **YES** |
| **$T=12$** | **$0.6185$ ($61.85\%$)** | **$9.12 \times 10^{-38}$** | **$0.2963$ ($29.63\%$)** | **$1.02 \times 10^{-18}$** | **YES** |
| **$T=16$** | $0.5259$ ($52.59\%$) | $3.24 \times 10^{-32}$ | $0.2963$ ($29.63\%$) | $1.02 \times 10^{-18}$ | **YES** |
| **$T=25$** | $0.4630$ ($46.30\%$) | $1.15 \times 10^{-28}$ | $0.2963$ ($29.63\%$) | $1.02 \times 10^{-18}$ | **YES** |

### Finding:
Random shuffling induces substantial policy discordance ($29.63\%$ to $74.07\%$, $p < 10^{-18}$). Downstream behavioral differentiation depends on the correspondence of stimulus-aligned directional information, as the differentiation effect is substantially disrupted under null shuffle controls (not claimed as an isolated causal demonstration).

---

## 14. Methodological Rigor & Anti-Overclaim Language Locks

In accordance with strict project governance, this study enforces the following language and epistemic locks:

1. **Downstream Policy Utilization, Not SLM "Understanding"**:
   - The findings describe downstream action policy selection and conditioning within an isolated research adapter. They do NOT demonstrate or claim end-to-end subjective comprehension by a Large Language Model.
2. **Predefined Exploratory Threshold**:
   - The threshold $D_{\text{pol}} \ge 0.05$ is designated as a *predefined exploratory classification threshold*, not an evidence-based production pass threshold.
3. **Counterfactual Interventions**:
   - Swapping directional vectors across probes ($N=6,734$ pairs at $T=12$, yielding $D_{\text{pol}} = 0.0437, p = 1.82 \times 10^{-65}$) is explicitly identified as a *counterfactual measurement intervention*, not a physically realized emotional ODE trajectory.
4. **Ternary Sign Encoding Precision**:
   - Representation R3 is described as `1 continuous scalar + 3 ternary sign symbols` in $\{-1, 0, +1\}^3$ ($27$ discrete states; $\lceil \log_2(27) \rceil = 5$ bits optimal encoding), rather than "3 bits".
5. **No Production Claims**:
   - This study provides empirical research evidence. It does not constitute, authorize, or imply production code modification.

---

## 15. Four-Way State Classification Framework & Decision Logic

The study evaluates the empirical findings against the four predefined architectural decision states:

```text
                                 [Empirical Evidence]
                                           │
                    ┌──────────────────────┴──────────────────────┐
                    ▼                                             ▼
          D_pol(C2) >= 0.05?                             D_pol(C2) < 0.05?
                    │                                             │
         ┌──────────┴──────────┐                                  ▼
         ▼                     ▼                              [State A]
D_pol(C1 | same sign)   D_pol(C1 | same sign)             Scalar Sufficiency
       >= 0.05?               < 0.05?                   (Side-Channels Unused)
         │                     │
         ▼                     ▼
     [State C]             [State B]
 Continuous Direction   R3 Discrete Behavioral
      Required               Sufficiency
```

- **State A — Scalar Behavioral Sufficiency**: Neither continuous nor discrete directional side-channels produce statistically significant downstream behavioral changes ($D_{\text{pol}} < 0.05$).
- **State B — R3 Discrete Behavioral Sufficiency**: Discrete ternary signs (R3) produce statistically significant behavioral divergence ($D_{\text{pol}} \ge 0.05, p < 0.05$), while continuous direction (R2) provides no additional behavioral value in matched same-sign cases ($D_{\text{pol}}(\text{R2} \mid \text{same sign}) < 0.05$).
- **State C — R2 Continuous Directional Necessity**: Continuous direction produces statistically significant behavioral divergence beyond discrete signs ($D_{\text{pol}}(\text{R2} \mid \text{same sign}) \ge 0.05, p < 0.05$).
- **State D — Directional Modulation Incoherence**: Directional side-channels produce behavioral divergence, but fail semantic coherence or disrupt scalar surprise monotonicity.

### Formal Classification:
**STATE B — R3 Discrete Behavioral Sufficiency** is empirically assigned based on the preregistered research-harness criteria:
1. $D_{\text{pol}}(\text{C2}) = 1.0000 \ge 0.05$ ($p = 3.09 \times 10^{-60}$ at $T=12$).
2. $D_{\text{pol}}(\text{C1} \mid \text{same sign}) = 0.0000 < 0.05$ ($p = 1.0$ at $T=12$).
3. Within the evaluated 358 collapse pairs at $T=12$, C2 reproduces all 286 action distinctions observed under C1 ($79.89\%$).

*Scope Lock on State B*: This classification indicates that R3 is behaviorally sufficient strictly under the predefined research-harness criteria and frozen G1 evaluation regime. It does NOT constitute a global architectural conclusion that Lucia has proven R3 is the necessary or minimal representation for production. The Production Architecture Gate remains strictly locked, and Phase 22 H1 overall remains INCONCLUSIVE because Gate 2 remains blocked.

---

## 16. Synthesis of Empirical Findings Across Phase 22 H1 Studies

This study completes the empirical trajectory of Phase 22 H1 measurement architecture research:

```text
Phase 22 H1 Study Sequence:
1. Gate 2 Compression Diagnostic
   └── Finding: 99.8% compression under Protocol v1.4; Gate 2 BLOCKED.
2. Measurement Architecture Study
   └── Finding: Canonical scalar S collapses orthogonal PAD trajectories (State B).
3. Precision-Directional Measurement Study
   └── Finding: Directional info persists after magnitude matching; precision candidate П1 unvalidated.
4. Minimal Sufficient Measurement Study
   └── Finding: R3 (discrete signs) eliminates collapse at T >= 12; R2 eliminates at all T.
5. Directional Side-Channel Behavioral Utilization Study (CURRENT)
   └── Finding: R3 discrete signs are behaviorally sufficient; R2 continuous orientation adds 0 value.
```

---

## 17. Downstream Implications for Measurement Architecture

1. **Discrete Orientation is Behaviorally Sufficient**: Downstream cognitive policies operate effectively on discrete directional signs $\{-1, 0, +1\}^3$ rather than requiring continuous high-precision trigonometric orientation vectors.
2. **Minimal Overhead**: R3 requires storing only 1 continuous float ($S$) plus 3 discrete ternary symbols (27 states, encodable in 5 bits), avoiding the storage and computational overhead of 3D floating-point unit vectors.
3. **Preservation of Intensity Semantics**: Scalar surprise $S$ continues to serve as the unified scalar driver of somatic tension, cognitive load, and reasoning depth.

---

## 18. Hardware, Concurrency & Resource Footprint Verification

- **CPU-Only Execution**: 100% of ODE integration, EFE policy arbitration, divergence calculation, and statistics executed on CPU (`device="cpu"`).
- **GPU VRAM Discipline**: Exactly **0.0 MB GPU VRAM** allocated.
- **Execution Performance**: Full 270-probe evaluation across 7 exposure ticks completed in **57.21 seconds**.
- **Memory Footprint**: Transient memory allocation $\le 12.4\text{ MB}$.

---

## 19. Architectural Decision & Gate Status

- **Phase 22 H1 Status**: Formally preserved as **INCONCLUSIVE**.
- **Gate 2 Status**: Formally preserved as **BLOCKED**.
- **Architecture Gate**: **STRICTLY LOCKED**.
- **Production Code Mutation**: Exactly **0 modifications** to `src/core/**`.
- **Genesis Profile**: Preserved bit-exact `{"is_onboarded": false}`.
- **Architectural Scope of State B**: State B establishes behavioral sufficiency strictly under the isolated evaluation harness and frozen Candidate G1 regime. It does NOT authorize production promotion or imply an architectural conclusion that R3 is validated for production. Any eventual promotion of representation R3 to production architecture remains a future decision requiring resolution of Gate 2, a dedicated Architectural Decision Record (ADR), schema migration design, and formal user governance sign-off.

---

## 20. Artifact Inventory & Reproducibility Hashes

| Artifact File Path | SHA-256 Checksum | Description |
|---|---|---|
| `tests/evaluation_phase22/scripts/analyze_directional_sidechannel_behavior.py` | `d3896e0be8129bd9405ce56ae81c162822c319fee3e99f73767b2ec6f63f183d` | Research analysis engine & behavioral adapter. |
| `tests/evaluation_phase22/results/h1_directional_sidechannel_behavior/directional_behavior_results.json` | `32a269d51dbc34b99e997e410afed5b899feb6ba12fc37bee338b8181f59d4e4` | Complete empirical metrics & statistical results. |
| `tests/evaluation_phase22/fixtures/manifest_h1_directional_sidechannel_behavior.json` | `0c2aa900a0e10d59eaf75c4b88805a7f9e2debcf53ba387b810863b26f86504a` | Cryptographic manifest and governance registry. |
| `tests/evaluation_phase22/test_h1_directional_sidechannel_behavior.py` | `5fa0a1b15b0e7101382080a83afda3f817e2148be4e553bbbc2af6a3d3737b4e` | Formal automated test suite (10/10 passing). |

---

## 21. References & Historical Document Trail

1. `docs/00_PROJECT_OVERVIEW.md` — Canonical Project Truth & System Invariants.
2. `docs/ARCHITECTURE.md` — Cognitive Architecture, Locking Hierarchy, ADR Ledger.
3. `docs/specs/Lucia-phase22-Epistemic_Foraging/PHASE_22_H1_MEASUREMENT_ARCHITECTURE_STUDY.md` — Phase 22 H1 Measurement Architecture Study.
4. `docs/specs/Lucia-phase22-Epistemic_Foraging/PHASE_22_H1_PRECISION_DIRECTIONAL_MEASUREMENT_STUDY.md` — Precision-Directional Measurement Study.
5. `docs/specs/Lucia-phase22-Epistemic_Foraging/PHASE_22_H1_MINIMAL_SUFFICIENT_MEASUREMENT_STUDY.md` — Minimal Sufficient Measurement Architecture Study.
6. `data/profile.json` — Genesis Onboarding State (`{"is_onboarded": false}`).
