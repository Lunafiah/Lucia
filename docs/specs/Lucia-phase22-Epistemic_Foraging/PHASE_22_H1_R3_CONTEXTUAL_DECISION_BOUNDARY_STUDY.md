# Phase 22 H1 — Contextual Decision Boundary & Action Selection Study

**Study ID**: `PHASE_22_H1_CONTEXTUAL_DECISION_BOUNDARY_ACTION_SELECTION_STUDY`  
**Authority Tier**: Phase Research Specification & Empirical Evidence Record  
**Master Seed**: `9999` | **Shuffle Seed (C2)**: `7113` | **Independent Model Seed (C3)**: `6180`  
**Bootstrap Seed**: `54321` ($B = 10,000$ iterations)  
**Corpus SHA-256**: `d0061e8cfdd160f4ebccb7100e4fe3eeef9ff18a1a4c9c1b3f912a76f2ae82c0`  
**Corpus**: $N=270$ Candidate G1 probes (90/tier), 358 matched discordant pairs ($|S_i - S_j| \le 0.020$, discordant R3 ternary direction signs)  
**Status**: `[RESEARCH VALIDATED / HARNESS ONLY / NOT FOR PRODUCTION PROMOTION]`

---

## 1. Executive Summary & Research Motivation

The preceding **R3 Epistemic-to-Policy Translation & Gate 2 Sensitivity Study** (`cf26c4c`) conclusively identified the primary architectural bottleneck in Phase 22 H1:
1. Continuous R3 directional information propagates through Bayesian inference and action valuation with fidelity ($r = +1.0000$, action-specific variance $= 91.14\%$, $\|\Delta\mathbf{V}_{\text{dir}}\| = 0.093653$ nats).
2. However, discrete policy divergence under the canonical additive EFE policy remained strictly zero ($D_{\text{pol}} = 0.0000$) across all 358 matched discordant pairs.
3. The root cause was identified as **argmax discretization loss under high pragmatic certainty**: the baseline static advantage of the default action `answer` ($V_{\text{pragm}} = 1.0, C = 0.05 \implies V_{\text{base}} = +0.95$) over informative non-answer actions (`retrieve`: $V_{\text{base}} = -0.35$; `clarify`: $V_{\text{base}} = -0.40$) creates a static pragmatic gap ($\Delta_{\text{gap}} = 1.30$ to $1.35$ nats) that dwarfs the continuous directional displacement ($\|\Delta\mathbf{V}_{\text{dir}}\| \sim 0.094$ nats).

This study tests the preregistered **Contextual Decision Boundary Hypothesis**:
> **If pragmatic certainty is contextually reduced ($V_{\text{pragm}}(\text{"answer"}) \in \{1.00, 0.80, 0.60, 0.40, 0.20, 0.00\}$), does the continuous directional action-value displacement ($\|\Delta\mathbf{V}_{\text{dir}}\| \sim 0.094$ nats) cross the analytical decision boundary ($B = V_{\text{best\_nonanswer}} - V_{\text{answer}}$) to produce discrete action divergence ($D_{\text{pol}} > 0$), or does the deterministic argmax operator enforce lockstep discretization even when pragmatic dominance is eliminated?**

---

## 2. Pre-Registered Experimental Design & Boundary Formulation

All parameters, context levels, numerical tolerances, and hypothesis interpretation criteria were pre-registered and committed in [`manifest_h1_r3_contextual_decision_boundary.json`](file:///c:/Users/Lunafiah/Desktop/My_project/Lucia/tests/evaluation_phase22/fixtures/manifest_h1_r3_contextual_decision_boundary.json) prior to benchmark execution.

### 2.1 6-Level Contextual Certainty Grid
The pragmatic certainty of `answer` was varied across 6 discrete levels representing contexts ranging from complete factual certainty down to complete pragmatic neutrality:

| Context ID | $V_{\text{pragm}}(\text{"answer"})$ | $C(\text{"answer"})$ | Baseline $V_{\text{base}}(\text{"answer"})$ | Baseline Non-Answer Competitors |
|---|---|---|---|---|
| **CTX_0** | $1.00$ | $0.05$ | $+0.95$ | `wait`: $-0.02$, `retrieve`: $-0.35$, `clarify`: $-0.40$ |
| **CTX_1** | $0.80$ | $0.05$ | $+0.75$ | `wait`: $-0.02$, `retrieve`: $-0.35$, `clarify`: $-0.40$ |
| **CTX_2** | $0.60$ | $0.05$ | $+0.55$ | `wait`: $-0.02$, `retrieve`: $-0.35$, `clarify`: $-0.40$ |
| **CTX_3** | $0.40$ | $0.05$ | $+0.35$ | `wait`: $-0.02$, `retrieve`: $-0.35$, `clarify`: $-0.40$ |
| **CTX_4** | $0.20$ | $0.05$ | $+0.15$ | `wait`: $-0.02$, `retrieve`: $-0.35$, `clarify`: $-0.40$ |
| **CTX_5** | $0.00$ | $0.05$ | $-0.05$ | `wait`: $-0.02$, `retrieve`: $-0.35$, `clarify`: $-0.40$ |

Non-answer actions retain fixed costs:
`clarify`: $0.40$, `retrieve`: $0.35$, `derive`: $0.40$, `reason`: $0.50$, `wait`: $0.02$.

### 2.2 Analytical Decision Boundary & Discretization Mechanics
For any probe $k$ under context $c$:
$$V(a) = \alpha_{\text{pragm}} V_{\text{pragm}}(a) + \beta_0 \text{EIG}(a) - C(a), \quad \alpha_{\text{pragm}} = 1.0, \beta_0 = 2.0$$
$$V_{\text{answer}} = V(\text{"answer"})$$
$$V_{\text{best\_nonanswer}} = \max_{a \ne \text{"answer"}} V(a)$$
$$\text{Boundary Distance } B = V_{\text{best\_nonanswer}} - V_{\text{answer}}$$

The analytical decision boundary defines three regimes:
1. $B < -\tau_{\text{tie}}$: `answer` strictly dominates ($a^* = \text{"answer"}$).
2. $B > +\tau_{\text{tie}}$: non-answer strictly dominates ($a^* \ne \text{"answer"}$).
3. $|B| \le \tau_{\text{tie}}$: decision boundary tie ($\tau_{\text{tie}} = 1.0 \times 10^{-6}$).

For a matched discordant pair $(i, j)$:
- Directional boundary shift: $\Delta B_{\text{dir}} = (B_i - B_j) - (B_{0,i} - B_{0,j})$
- Action divergence: $D_{\text{pol}} = \mathbb{I}[a_i^* \ne a_j^*]$
- Separate diagnostic probabilistic branch: $P(a) = \text{softmax}(\mathbf{V}, \gamma = 1.0) \implies D_{\text{TV}}, D_{\text{JS}}$

---

## 3. Factorial Conditions & Control Architecture

The study evaluated all 358 matched discordant pairs across 6 contexts $\times$ 4 conditions ($8,592$ probe-pair evaluations):

1. **Condition C0 (Scalar Null Control)**: Directional weight $W_{\text{dir}} = \mathbf{0}$. Isolates scalar limbic magnitude dynamics.
2. **Condition C1 (Canonical R3)**: Full canonical observation model ($M_{\text{canon}}$).
3. **Condition C2 (Direction-Shuffled Control)**: Probe directions randomized across the corpus via frozen permutation seed `7113`.
4. **Condition C3 (Independent Observation Model)**: Independently generated parameters ($M_{\text{indep}}$, seed `6180`).

### 3.1 Pre-Registered Invariants & Verification Suite
- **NC1 (Scalar Null Control)**: Under C0, $\|\Delta\mathbf{V}_{\text{dir}}\| \le \tau_{\text{val}}$ ($10^{-4}$) and $D_{\text{pol}} = 0.0$ across all 6 contexts.
- **NC2 (Direction-Shuffled Correspondence)**: Pearson correlation between C2 and C1 value displacement must be degraded ($r \le 0.50$).
- **NC3 (Zero Directional Weighting Identity)**: $W_{\text{dir}} = \mathbf{0}$ yields bit-exact C0 values.
- **NC4 (Deterministic Repeatability)**: Bit-exact repeatability across identical evaluations.
- **NC5 (Anti-Tuning Invariance)**: Parameter and permutation SHA-256 hashes bit-exact with manifest.
- **NC6 (Production Code Isolation)**: Zero diff in `src/core/**`.
- **NC7 (Genesis Gate Invariant)**: `data/profile.json` bit-exact `{"is_onboarded": false}`.
- **NC8 (Context Monotonicity Control)**: Boundary distance $B$ must strictly increase monotonically as $V_{\text{pragm}}(\text{"answer"})$ decreases (exact $+0.2000$ per step).
- **RC1 (Cross-Model Replication Control)**: Under C3, directional value displacement $\|\Delta\mathbf{V}_{\text{dir}}\| > \tau_{\text{val}}$ across all 6 contexts.

---

## 4. Empirical Results

### 4.1 Full Factorial Evaluation Across Contexts and Conditions

| Context | $V_{\text{pragm}}(\text{ans})$ | Cond | Mean Boundary $B$ (nats) | Bootstrap 95% CI ($B$) | Mean $\|\Delta\mathbf{V}_{\text{dir}}\|$ | Bootstrap 95% CI ($\|\Delta V\|$) | Mean $\Delta B_{\text{dir}}$ | $D_{\text{pol}}$ | Ranking Change Rate | Mean $D_{\text{TV}}$ | Mean $D_{\text{JS}}$ |
|---|---|---|---|---|---|---|---|---|---|---|---|
| **CTX_0** | $1.00$ | C0 | $-0.949869$ | $[-0.949946, -0.949790]$ | $0.000000$ | $[0.000000, 0.000000]$ | $0.000000$ | $0.0000$ | $0.0000$ | $0.000253$ | $0.000000$ |
| | | **C1** | **$-0.887944$** | **$[-0.889024, -0.886861]$** | **$0.093653$** | **$[0.090910, 0.096395]$** | **$0.029858$** | **$0.0000$** | **$0.0000$** | **$0.010833$** | **$0.000156$** |
| | | C2 | $-0.875506$ | $[-0.876745, -0.874305]$ | $0.039067$ | $[0.035305, 0.042810]$ | $0.003250$ | $0.0000$ | $0.0000$ | $0.004486$ | $0.000047$ |
| | | C3 | $-0.842205$ | $[-0.843087, -0.841323]$ | $0.090408$ | $[0.086393, 0.094423]$ | $0.040513$ | $0.0000$ | $0.0000$ | $0.012150$ | $0.000121$ |
| **CTX_1** | $0.80$ | C0 | $-0.749869$ | $[-0.749946, -0.749790]$ | $0.000000$ | $[0.000000, 0.000000]$ | $0.000000$ | $0.0000$ | $0.0000$ | $0.000264$ | $0.000000$ |
| | | **C1** | **$-0.687944$** | **$[-0.689024, -0.686861]$** | **$0.093653$** | **$[0.090910, 0.096395]$** | **$0.029858$** | **$0.0000$** | **$0.0000$** | **$0.011541$** | **$0.000167$** |
| | | C2 | $-0.675506$ | $[-0.676745, -0.674305]$ | $0.039067$ | $[0.035305, 0.042810]$ | $0.003250$ | $0.0000$ | $0.0000$ | $0.004749$ | $0.000050$ |
| | | C3 | $-0.642205$ | $[-0.643087, -0.641323]$ | $0.090408$ | $[0.086393, 0.094423]$ | $0.040513$ | $0.0000$ | $0.0000$ | $0.012637$ | $0.000126$ |
| **CTX_2** | $0.60$ | C0 | $-0.549869$ | $[-0.549946, -0.549790]$ | $0.000000$ | $[0.000000, 0.000000]$ | $0.000000$ | $0.0000$ | $0.0000$ | $0.000273$ | $0.000000$ |
| | | **C1** | **$-0.487944$** | **$[-0.489024, -0.486861]$** | **$0.093653$** | **$[0.090910, 0.096395]$** | **$0.029858$** | **$0.0000$** | **$0.0000$** | **$0.012192$** | **$0.000177$** |
| | | C2 | $-0.475506$ | $[-0.476745, -0.474305]$ | $0.039067$ | $[0.035305, 0.042810]$ | $0.003250$ | $0.0000$ | $0.0000$ | $0.004990$ | $0.000053$ |
| | | C3 | $-0.442205$ | $[-0.443087, -0.441323]$ | $0.090408$ | $[0.086393, 0.094423]$ | $0.040513$ | $0.0000$ | $0.0000$ | $0.013042$ | $0.000131$ |
| **CTX_3** | $0.40$ | C0 | $-0.349869$ | $[-0.349946, -0.349790]$ | $0.000000$ | $[0.000000, 0.000000]$ | $0.000000$ | $0.0000$ | $0.0000$ | $0.000281$ | $0.000000$ |
| | | **C1** | **$-0.287944$** | **$[-0.289024, -0.286861]$** | **$0.093653$** | **$[0.090910, 0.096395]$** | **$0.029858$** | **$0.0000$** | **$0.0000$** | **$0.012780$** | **$0.000186$** |
| | | C2 | $-0.275506$ | $[-0.276745, -0.274305]$ | $0.039067$ | $[0.035305, 0.042810]$ | $0.003250$ | $0.0000$ | $0.0000$ | $0.005211$ | $0.000056$ |
| | | C3 | $-0.242205$ | $[-0.243087, -0.241323]$ | $0.090408$ | $[0.086393, 0.094423]$ | $0.040513$ | $0.0000$ | $0.0000$ | $0.013373$ | $0.000135$ |
| **CTX_4** | $0.20$ | C0 | $-0.149869$ | $[-0.149946, -0.149790]$ | $0.000000$ | $[0.000000, 0.000000]$ | $0.000000$ | $0.0000$ | $0.0000$ | $0.000287$ | $0.000000$ |
| | | **C1** | **$-0.087944$** | **$[-0.089024, -0.086861]$** | **$0.093653$** | **$[0.090910, 0.096395]$** | **$0.029858$** | **$0.0000$** | **$0.0000$** | **$0.013305$** | **$0.000195$** |
| | | C2 | $-0.075506$ | $[-0.076745, -0.074305]$ | $0.039067$ | $[0.035305, 0.042810]$ | $0.003250$ | $0.0000$ | $0.0000$ | $0.005407$ | $0.000058$ |
| | | C3 | $-0.042205$ | $[-0.043087, -0.041323]$ | $0.090408$ | $[0.086393, 0.094423]$ | $0.040513$ | $0.0000$ | $0.0000$ | $0.013637$ | $0.000138$ |
| **CTX_5** | $0.00$ | C0 | $+0.050131$ | $[+0.050054, +0.050210]$ | $0.000000$ | $[0.000000, 0.000000]$ | $0.000000$ | $0.0000$ | $0.0000$ | $0.000292$ | $0.000000$ |
| | | **C1** | **$+0.112056$** | **$[+0.110976, +0.113139]$** | **$0.093653$** | **$[0.090910, 0.096395]$** | **$0.029858$** | **$0.0000$** | **$0.7989$** | **$0.013767$** | **$0.000202$** |
| | | C2 | $+0.124494$ | $[+0.123255, +0.125695]$ | $0.039067$ | $[0.035305, 0.042810]$ | $0.003250$ | $0.0000$ | $0.0000$ | $0.005579$ | $0.000060$ |
| | | C3 | $+0.157795$ | $[+0.156913, +0.158677]$ | $0.090408$ | $[0.086393, 0.094423]$ | $0.040513$ | $0.0000$ | $0.7989$ | $0.013845$ | $0.000140$ |

---

## 5. Architectural & Mathematical Analysis of Empirical Findings

### 5.1 The Boundary Sign Flip ($B < 0 \rightarrow B > 0$)
As predicted by NC8 (Context Monotonicity), boundary distance $B = V_{\text{best\_nonanswer}} - V_{\text{answer}}$ increases by exactly $+0.2000$ nats at each context reduction step:
- In CTX_0..CTX_4, $B < 0$. The default action `answer` strictly dominates ($V_{\text{answer}} > V_{\text{best\_nonanswer}}$).
- In CTX_5, $V_{\text{pragm}}(\text{"answer"}) = 0.00 \implies V_{\text{answer}} = -0.05$.
- For informative action `retrieve`, $V(\text{"retrieve"}) = 2.0 \times \text{EIG} - 0.35$.
- Because mean EIG is $\sim 0.20$ to $0.25$ nats for informative probes, $V(\text{"retrieve"}) > 0.0$ (mean $+0.062$ nats), easily surpassing $V_{\text{answer}} = -0.05$.
- Consequently, in CTX_5, $B = +0.112056 > 0$ (Bootstrap 95% CI: $[+0.110976, +0.113139]$). The analytical decision boundary is unambiguously crossed.

### 5.2 The Lockstep Transition Phenomenon
Despite crossing the decision boundary, **$D_{\text{pol}}$ remained strictly $0.0000$ in CTX_5**.

Why?
- In CTX_0..CTX_4: $100\%$ (716/716) of probes in the 358 pairs select $a^* = \text{"answer"}$. Within-pair action divergence is $0$.
- In CTX_5: $100\%$ (716/716) of probes in the 358 pairs select $a^* = \text{"retrieve"}$.
- Because the epistemic utility of `retrieve` exceeds `clarify` ($C = 0.40$), `derive` ($C = 0.40$), `reason` ($C = 0.50$), and `wait` ($C = 0.02, \text{EIG} = 0 \implies V = -0.02$) for *both* probes in every matched pair, the entire ensemble transitions **in lockstep** from 100% `answer` to 100% `retrieve`.
- For any discordant pair $(i, j)$:
  $$a_i^* = \text{"retrieve"}, \quad a_j^* = \text{"retrieve"} \implies D_{\text{pol}}(i, j) = 0$$

### 5.3 Sub-Action Ranking Permutation and Probabilistic Differentiation
While the top argmax action $a^*$ transitions in lockstep, the continuous R3 directional signal is vigorously active underneath:
1. **Sub-Action Ranking Reorganizations**: In CTX_5, **$79.89\%$ of pairs (286 of 358 pairs)** undergo action ranking permutations. The order of secondary and tertiary actions (`clarify`, `wait`, `derive`) swaps between discordant probes based on their directional sign.
2. **Probabilistic Policy Shift**: The diagnostic softmax branch ($P(a) = \text{softmax}(\mathbf{V}, \gamma = 1.0)$) exhibits statistically significant continuous divergence:
   - Total Variation distance $D_{\text{TV}}$ rises monotonically from $0.010833$ (CTX_0) to $0.013767$ (CTX_5), strictly exceeding $\tau_{\text{TV}} = 1.0 \times 10^{-4}$.
   - Jensen-Shannon divergence $D_{\text{JS}}$ rises monotonically from $0.000156$ (CTX_0) to $0.000202$ (CTX_5), strictly exceeding $\tau_{\text{JS}} = 1.0 \times 10^{-5}$.
3. **Continuous Displacement Invariance**: Across all 6 contexts, the continuous action-value displacement remains invariant at $\|\Delta\mathbf{V}_{\text{dir}}\| = 0.093653$ nats (95% CI: $[0.090910, 0.096395]$), and the directional boundary shift remains invariant at $\Delta B_{\text{dir}} = 0.029858$ nats (95% CI: $[0.027850, 0.031867]$).

---

## 6. Pre-Registered Decision Hierarchy Outcome

Following Section 2 of the pre-registered protocol, the top-down decision hierarchy resolves as follows:

| Level | Condition | Evaluation Result | Status |
|---|---|---|---|
| **Level 1** | Any Negative Control (NC1–NC8, RC1) fails | All 8 NCs + RC1 passed ($100\%$) | **PASSED** |
| **Level 2** | Contextual Boundary Crossing: $D_{\text{pol}} > 0$ for any context | $D_{\text{pol}} \equiv 0.0000$ across all 6 contexts | **NOT SATISFIED** |
| **Level 3** | **Persistent Deterministic Discretization**: $D_{\text{pol}} = 0.0000$ across all contexts, $\|\Delta\mathbf{V}_{\text{dir}}\| > \tau_{\text{val}}$, and $D_{\text{TV}} > \tau_{\text{TV}}$ | $D_{\text{pol}} = 0.0000$, $\|\Delta V\| = 0.0937 > 10^{-4}$, $D_{\text{TV}} = 0.0138 > 10^{-4}$ | **CONFIRMED (RESULT_B)** |
| **Level 4** | Probabilistic Policy Signal Only | Pre-empted by Level 3 | N/A |
| **Level 5** | Inconclusive | Pre-empted by Level 3 | N/A |

### Formal Classification
**Classification**: `RESULT_B — PERSISTENT_DETERMINISTIC_DISCRETIZATION`  
**Rationale**: Deterministic argmax action divergence remained $D_{\text{pol}} = 0.0000$ across all 6 contexts, even at CTX_5 where pragmatic certainty was zero. The continuous R3 directional displacement ($\|\Delta\mathbf{V}_{\text{dir}}\| \sim 0.094$ nats) remains compressed inside the deterministic boundary discretization step, while the diagnostic probabilistic branch exhibits clear continuous shift ($\max D_{\text{TV}} = 0.0138 > 0.0001$).

---

## 7. Quality Gate 2 & Governance Invariants

1. **Gate 2 Status**: **`STRICTLY BLOCKED`**.
   $$\Delta_{\text{HM}} = 0.0685 < 0.1500$$
   Because discrete action divergence remains $D_{\text{pol}} = 0.0000$, Gate 2 cannot be unlocked.
2. **Phase 22 H1 Status**: **`INCONCLUSIVE`**.
3. **ADR-029 Ledger Status**: **`DRAFT / RESEARCH RECORD ONLY / NOT RATIFIED`**.
4. **Zero Production Mutation Invariant**: `src/core/**` git diff $= 0$.
5. **Genesis Onboarding Gate**: `data/profile.json` remains bit-exact `{"is_onboarded": false}`.
6. **20-Watt Hardware Constraint**: All simulations and evaluations executed strictly on CPU with 0.0 MB GPU VRAM.

---

## 8. Artifact Ledger & Reproducibility Verification

| Artifact | Location | SHA-256 / Checksum Status |
|---|---|---|
| Manifest | [`manifest_h1_r3_contextual_decision_boundary.json`](file:///c:/Users/Lunafiah/Desktop/My_project/Lucia/tests/evaluation_phase22/fixtures/manifest_h1_r3_contextual_decision_boundary.json) | Committed prior to benchmark execution |
| Evaluation Harness | [`evaluate_h1_r3_contextual_decision_boundary.py`](file:///c:/Users/Lunafiah/Desktop/My_project/Lucia/tests/evaluation_phase22/scripts/evaluate_h1_r3_contextual_decision_boundary.py) | Verified executable ($36.95\text{s}$) |
| Dedicated Test Suite | [`test_h1_r3_contextual_decision_boundary.py`](file:///c:/Users/Lunafiah/Desktop/My_project/Lucia/tests/evaluation_phase22/test_h1_r3_contextual_decision_boundary.py) | 29/29 tests passing ($11.55\text{s}$) |
| Full Regression Suite | `tests/evaluation_phase22/` | 430/430 tests passing ($90.53\text{s}$) |
| Empirical Results Fixture | [`results_h1_r3_contextual_decision_boundary.json`](file:///c:/Users/Lunafiah/Desktop/My_project/Lucia/tests/evaluation_phase22/fixtures/results_h1_r3_contextual_decision_boundary.json) | Full factorial 358-pair data across 6 contexts $\times$ 4 conditions |
| Negative Controls Fixture | [`nc_h1_r3_contextual_decision_boundary.json`](file:///c:/Users/Lunafiah/Desktop/My_project/Lucia/tests/evaluation_phase22/fixtures/nc_h1_r3_contextual_decision_boundary.json) | 8 NCs + RC1 all passed |
| 15-Point Formal Report | [`report_h1_r3_contextual_decision_boundary.json`](file:///c:/Users/Lunafiah/Desktop/My_project/Lucia/tests/evaluation_phase22/fixtures/report_h1_r3_contextual_decision_boundary.json) | Complete pre-registered schema |
| CSV Summary | [`summary_h1_r3_contextual_decision_boundary.csv`](file:///c:/Users/Lunafiah/Desktop/My_project/Lucia/tests/evaluation_phase22/fixtures/summary_h1_r3_contextual_decision_boundary.csv) | 24 condition rows with bootstrap CIs |
