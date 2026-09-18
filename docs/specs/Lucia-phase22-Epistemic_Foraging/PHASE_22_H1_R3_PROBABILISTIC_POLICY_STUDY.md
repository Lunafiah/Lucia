# Phase 22 H1 — Probabilistic Policy Recovery & Decision-Temperature Study

**Study ID**: `PHASE_22_H1_R3_PROBABILISTIC_POLICY_STUDY`  
**Authority Tier**: Phase Research Specification & Empirical Evidence Record  
**Master Seed**: `9999` | **Shuffle Seed (C2)**: `7113` | **Independent Model Seed (C3)**: `6180`  
**Sampling Seed**: `7113` ($K = 10,000$ Common Random Number Monte Carlo samples per pair)  
**Bootstrap Seed**: `54321` ($B = 10,000$ iterations)  
**Corpus SHA-256**: `d0061e8cfdd160f4ebccb7100e4fe3eeef9ff18a1a4c9c1b3f912a76f2ae82c0`  
**Corpus**: $N=270$ Candidate G1 probes (90/tier), 358 matched discordant pairs ($|S_i - S_j| \le 0.020$, discordant R3 ternary direction signs)  
**Fixed Context**: **CTX_5 only** ($V_{\text{pragm}}(\text{"answer"}) = 0.00, C(\text{"answer"}) = 0.05 \implies V_{\text{base}}(\text{"answer"}) = -0.05$)  
**Temperature Grid**: $\gamma \in \{0.25, 0.50, 1.00, 2.00, 4.00\}$  
**Status**: `[RESEARCH VALIDATED / HARNESS ONLY / NOT FOR PRODUCTION PROMOTION]`

---

## 1. Executive Summary & Research Motivation

The immediately preceding study, **Contextual Decision Boundary & Action Selection Study** (`9dcc611`, `RESULT_B — PERSISTENT_DETERMINISTIC_DISCRETIZATION`), revealed a pivotal paradox in Lucia's Phase 22 H1 epistemic foraging architecture:
1. Under pragmatic neutrality (**CTX_5**, $V_{\text{pragm}}(\text{"answer"}) = 0.00$), the decision boundary is crossed ($B = +0.112056 > 0$) as epistemic foraging actions surpass static answering.
2. The continuous R3 directional signal remains active and unaltered ($\|\Delta\mathbf{V}_{\text{dir}}\| = 0.093653$ nats), and reorganizes secondary and tertiary sub-action rankings in **$79.89\%$ (286 of 358)** of matched discordant probe pairs.
3. Yet, deterministic argmax action divergence remained strictly zero ($D_{\text{pol}} = 0.0000$) across the entire corpus because both probes in every discordant pair transitioned from `answer` to `retrieve` in lockstep.
4. Softmax probability distributions exhibited continuous divergence ($D_{\text{TV}} = 0.013767, D_{\text{JS}} = 0.000202$), but were evaluated only diagnostically at $\gamma = 1.00$.

This study addresses the preregistered research question:
> **Does probabilistic policy selection recover the continuous R3 directional signal that deterministic argmax discards, and how does this depend on decision temperature $\gamma \in \{0.25, 0.50, 1.00, 2.00, 4.00\}$?**

### Key Distinctions Enforced
This study strictly distinguishes:
- **Deterministic policy**: $\pi_{\text{det}} = \operatorname{argmax}(\mathbf{V})$
- **Probabilistic policy**: $\pi_{\text{prob}} = \operatorname{softmax}(\gamma \mathbf{V})$
- **Sampled policy**: $a \sim \pi_{\text{prob}}$ (evaluated via $K = 10,000$ Common Random Number Monte Carlo simulation and analytical exact integration)

> [!CAUTION]
> **GOVERNANCE NOTICE**: Observation of sampled action divergence is an empirical finding regarding information recovery under stochastic sampling. It does **NOT** constitute an architectural recommendation that Lucia should adopt stochastic action selection in production.

---

## 2. Experimental Design & Pre-Registered Protocol

All experimental parameters, temperature grids, seeds, tolerances, and the decision hierarchy were pre-registered and locked in [`manifest_h1_r3_probabilistic_policy.json`](file:///c:/Users/Lunafiah/Desktop/My_project/Lucia/tests/evaluation_phase22/fixtures/manifest_h1_r3_probabilistic_policy.json) prior to execution.

### 2.1 Fixed Context: CTX_5 Only
Pragmatic value and action costs are held constant:
- $V_{\text{pragm}}(\text{"answer"}) = 0.00, C(\text{"answer"}) = 0.05 \implies V_{\text{base}}(\text{"answer"}) = -0.05$
- $V_{\text{pragm}}(a) = 0.00$ for all other actions $a \in \{\text{clarify}, \text{retrieve}, \text{derive}, \text{reason}, \text{wait}\}$
- Action costs: `clarify`: $0.40$, `retrieve`: $0.35$, `derive`: $0.40$, `reason`: $0.50$, `wait`: $0.02$
- EFE weightings: $\alpha_{\text{pragm}} = 1.0, \beta_0 = 2.0$

### 2.2 Temperature Grid & Softmax Formulation
Probabilistic action distributions are defined by:
$$P(a) = \frac{\exp(\gamma V(a))}{\sum_{b} \exp(\gamma V(b))}, \quad \gamma \in \{0.25, 0.50, 1.00, 2.00, 4.00\}$$

No temperature tuning or post-hoc parameter selection was permitted.

### 2.3 Factorial Conditions
All 358 matched discordant pairs ($N = 270$ G1 candidate probes, master seed `9999`) were evaluated across 5 temperatures $\times$ 4 conditions ($7,160$ probe-pair evaluations):
1. **Condition C0 (Scalar Null Baseline)**: Directional weight $W_{\text{dir}} = \mathbf{0}$. Isolates scalar limbic magnitude dynamics.
2. **Condition C1 (Canonical R3)**: Full canonical observation model ($M_{\text{canon}}$) with stimulus-contingent directional gating.
3. **Condition C2 (Direction-Shuffled Control)**: Probe directions randomized across the corpus via frozen permutation seed `7113`.
4. **Condition C3 (Independent Observation Model)**: Independently generated observation parameters ($M_{\text{indep}}$, seed `6180`).

### 2.4 Pre-Registered Negative Controls (NC1–NC8)
- **NC1 (Scalar Null Control)**: Under C0, $\|\Delta\mathbf{V}_{\text{dir}}\| \le \tau_{\text{val}}$ ($10^{-4}$), $D_{\text{TV, dir}} \le \tau_{\text{TV}}$ ($10^{-4}$), $D_{\text{JS}} \le \tau_{\text{JS}}$ ($10^{-5}$), and $D_{\text{pol}} = 0.0$ across all 5 temperatures.
- **NC2 (Direction-Shuffled Correspondence)**: Pearson correlation between C2 and C1 probability divergence must be degraded ($r \le 0.50$).
- **NC3 (Zero Directional Weighting Identity)**: $W_{\text{dir}} = \mathbf{0}$ yields bit-exact C0 scalar baseline.
- **NC4 (Deterministic Repeatability)**: Bit-exact numerical equality across repeat executions.
- **NC5 (Anti-Tuning Invariance)**: Frozen parameter and permutation SHA-256 hashes match manifest.
- **NC6 (Production Code Isolation)**: Zero diff in `src/core/**`, `src/api/**`, `electron/**`.
- **NC7 (Genesis Gate Invariant)**: `data/profile.json` remains bit-exact `{"is_onboarded": false}`.
- **NC8 (Softmax Argmax Equivalence)**: Bit-exact identity $\operatorname{argmax}(P) \equiv \operatorname{argmax}(V)$ across 100% of probes, conditions, and temperatures.

---

## 3. Empirical Results Across Temperature Grid

### 3.1 Complete Factorial Results Table (5 Temperatures $\times$ 4 Conditions)

| $\gamma$ | Cond | Mean $\|\Delta\mathbf{V}_{\text{dir}}\|$ | Bootstrap 95% CI ($\|\Delta V\|$) | Mean $D_{\text{TV}}$ (Raw) | Mean $D_{\text{TV, dir}}$ | Bootstrap 95% CI ($D_{\text{TV}}$) | Mean $D_{\text{JS}}$ | Bootstrap 95% CI ($D_{\text{JS}}$) | $D_{\text{pol}}$ | Ranking Change Rate | Empirical $D_{\text{samp}}$ ($K=10^4$) | Analytical $D_{\text{samp}}$ (CRN) | Analytical $D_{\text{samp}}$ (Indep) |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| **0.25** | C0 | $0.000000$ | $[0.0000, 0.0000]$ | $0.000070$ | $0.000000$ | $[0.000067, 0.000074]$ | $0.000000$ | $[0.0000, 0.0000]$ | $0.0000$ | $0.0000$ | $0.000140$ | $0.000141$ | $0.669818$ |
| | **C1** | **$0.093653$** | **$[0.0909, 0.0964]$** | **$0.003291$** | **$0.003290$** | **$[0.003183, 0.003403]$** | **$0.000012$** | **$[0.000011, 0.000013]$** | **$0.0000$** | **$0.7989$** | **$0.005586$** | **$0.005588$** | **$0.670570$** |
| | C2 | $0.039067$ | $[0.0353, 0.0428]$ | $0.001375$ | $0.001372$ | $[0.001244, 0.001509]$ | $0.000004$ | $[0.000003, 0.000004]$ | $0.0000$ | $0.0000$ | $0.002447$ | $0.002449$ | $0.670399$ |
| | C3 | $0.090408$ | $[0.0864, 0.0944]$ | $0.003310$ | $0.003309$ | $[0.003175, 0.003450]$ | $0.000009$ | $[0.000008, 0.000009]$ | $0.0000$ | $0.7989$ | $0.005615$ | $0.005618$ | $0.670845$ |
| **0.50** | C0 | $0.000000$ | $[0.0000, 0.0000]$ | $0.000142$ | $0.000000$ | $[0.000135, 0.000150]$ | $0.000000$ | $[0.0000, 0.0000]$ | $0.0000$ | $0.0000$ | $0.000287$ | $0.000284$ | $0.686884$ |
| | **C1** | **$0.093653$** | **$[0.0909, 0.0964]$** | **$0.006695$** | **$0.006692$** | **$[0.006473, 0.006922]$** | **$0.000049$** | **$[0.000046, 0.000052]$** | **$0.0000$** | **$0.7989$** | **$0.011118$** | **$0.011117$** | **$0.689620$** |
| | C2 | $0.039067$ | $[0.0353, 0.0428]$ | $0.002796$ | $0.002789$ | $[0.002530, 0.003068]$ | $0.000015$ | $[0.000012, 0.000018]$ | $0.0000$ | $0.0000$ | $0.004868$ | $0.004869$ | $0.689037$ |
| | C3 | $0.090408$ | $[0.0864, 0.0944]$ | $0.006734$ | $0.006732$ | $[0.006459, 0.007020]$ | $0.000035$ | $[0.000032, 0.000037]$ | $0.0000$ | $0.7989$ | $0.011172$ | $0.011175$ | $0.690855$ |
| **1.00** | C0 | $0.000000$ | $[0.0000, 0.0000]$ | $0.000292$ | $0.000000$ | $[0.000277, 0.000307]$ | $0.000000$ | $[0.0000, 0.0000]$ | $0.0000$ | $0.0000$ | $0.000574$ | $0.000574$ | $0.718817$ |
| | **C1** | **$0.093653$** | **$[0.0909, 0.0964]$** | **$0.013767$** | **$0.013763$** | **$[0.013313, 0.014234]$** | **$0.000202$** | **$[0.000188, 0.000216]$** | **$0.0000$** | **$0.7989$** | **$0.022082$** | **$0.022081$** | **$0.725917$** |
| | C2 | $0.039067$ | $[0.0353, 0.0428]$ | $0.005747$ | $0.005734$ | $[0.005204, 0.006307]$ | $0.000060$ | $[0.000049, 0.000072]$ | $0.0000$ | $0.0000$ | $0.009710$ | $0.009710$ | $0.724838$ |
| | C3 | $0.090408$ | $[0.0864, 0.0944]$ | $0.013845$ | $0.013841$ | $[0.013279, 0.014431]$ | $0.000140$ | $[0.000129, 0.000151]$ | $0.0000$ | $0.7989$ | $0.022197$ | $0.022194$ | $0.729731$ |
| **2.00** | C0 | $0.000000$ | $[0.0000, 0.0000]$ | $0.000609$ | $0.000000$ | $[0.000577, 0.000642]$ | $0.000000$ | $[0.0000, 0.0000]$ | $0.0000$ | $0.0000$ | $0.001150$ | $0.001149$ | $0.769970$ |
| | **C1** | **$0.093653$** | **$[0.0909, 0.0964]$** | **$0.028511$** | **$0.028504$** | **$[0.027585, 0.029471]$** | **$0.000859$** | **$[0.000800, 0.000918]$** | **$0.0000$** | **$0.7989$** | **$0.042992$** | **$0.042992$** | **$0.785461$** |
| | C2 | $0.039067$ | $[0.0353, 0.0428]$ | $0.011883$ | $0.011855$ | $[0.010775, 0.013038]$ | $0.000253$ | $[0.000207, 0.000304]$ | $0.0000$ | $0.0000$ | $0.019183$ | $0.019179$ | $0.784405$ |
| | C3 | $0.090408$ | $[0.0864, 0.0944]$ | $0.028669$ | $0.028662$ | $[0.027508, 0.029871]$ | $0.000572$ | $[0.000527, 0.000618]$ | $0.0000$ | $0.7989$ | $0.043232$ | $0.043231$ | $0.792342$ |
| **4.00** | C0 | $0.000000$ | $[0.0000, 0.0000]$ | $0.001248$ | $0.000000$ | $[0.001179, 0.001317]$ | $0.000001$ | $[0.0000, 0.0000]$ | $0.0000$ | $0.0000$ | $0.002281$ | $0.002279$ | $0.829141$ |
| | **C1** | **$0.093653$** | **$[0.0909, 0.0964]$** | **$0.057267$** | **$0.057256$** | **$[0.055452, 0.059173]$** | **$0.003602$** | **$[0.003362, 0.003848]$** | **$0.0000$** | **$0.7989$** | **$0.075798$** | **$0.075797$** | **$0.849187$** |
| | C2 | $0.039067$ | $[0.0353, 0.0428]$ | $0.023812$ | $0.023758$ | $[0.021644, 0.026090]$ | $0.001052$ | $[0.000865, 0.001264]$ | $0.0000$ | $0.0000$ | $0.036056$ | $0.036053$ | $0.850444$ |
| | C3 | $0.090408$ | $[0.0864, 0.0944]$ | $0.057530$ | $0.057520$ | $[0.055243, 0.059885]$ | $0.002341$ | $[0.002160, 0.002528]$ | $0.0000$ | $0.7989$ | $0.076241$ | $0.076239$ | $0.857642$ |

---

## 4. Key Hypotheses & Mathematical Findings

### 4.1 H1-P — Probabilistic Policy Signal (CONFIRMED)
Under C1 (Canonical R3), the directional signal produces substantial, statistically significant probability divergence across every evaluated temperature:
- At $\gamma = 0.25$: $D_{\text{TV}} = 0.003291 > 1.0 \times 10^{-4}$ ($33\times$ threshold); $D_{\text{JS}} = 0.000012 > 1.0 \times 10^{-5}$.
- At $\gamma = 1.00$: $D_{\text{TV}} = 0.013767 > 1.0 \times 10^{-4}$ ($138\times$ threshold); $D_{\text{JS}} = 0.000202 > 1.0 \times 10^{-5}$ ($20\times$ threshold).
- At $\gamma = 4.00$: $D_{\text{TV}} = 0.057267 > 1.0 \times 10^{-4}$ ($573\times$ threshold); $D_{\text{JS}} = 0.003602 > 1.0 \times 10^{-5}$ ($360\times$ threshold).

Under C0 (Scalar Null), the directional probability displacement is identically zero ($D_{\text{TV, dir}} \equiv 0.000000$), and scalar noise remains negligible ($D_{\text{JS}} \le 8.1 \times 10^{-7} \ll \tau_{\text{JS}}$).

### 4.2 H1-T — Temperature Sensitivity & Monotonicity (CONFIRMED)
The empirical probability divergence curves under C1 demonstrate **strict monotonic growth**:
$$\gamma = 0.25 \longrightarrow 0.50 \longrightarrow 1.00 \longrightarrow 2.00 \longrightarrow 4.00$$
$$D_{\text{TV}}: 0.003291 \longrightarrow 0.006695 \longrightarrow 0.013767 \longrightarrow 0.028511 \longrightarrow 0.057267$$
$$D_{\text{JS}}: 0.000012 \longrightarrow 0.000049 \longrightarrow 0.000202 \longrightarrow 0.000859 \longrightarrow 0.003602$$

Higher decision temperature $\gamma$ exponentially amplifies value differences into large probability separations.

### 4.3 H1-S — Sampled Action Divergence (CONFIRMED)
Under Common Random Numbers (seed `7113`), empirical Monte Carlo action sampling ($K = 10,000$ per pair) reveals reproducible action divergence that is completely absent under deterministic argmax:
- At $\gamma = 0.25$: $D_{\text{samp}} = 0.005586$ ($0.56\%$ of sampled turns select discordant actions).
- At $\gamma = 1.00$: $D_{\text{samp}} = 0.022082$ ($2.21\%$ of sampled turns select discordant actions, $38\times$ C0 baseline $0.000574$).
- At $\gamma = 4.00$: $D_{\text{samp}} = 0.075798$ (**$7.58\%$ of sampled turns select discordant actions**).

### 4.4 Sampler Cross-Validation
Empirical Monte Carlo divergence matches analytical CRN divergence within machine tolerance:
$$\max |D_{\text{samp, emp}} - D_{\text{samp, anal}}| < 0.000010 \quad (\text{mean discrepancy } < 0.000002)$$
This confirms the integrity and reproducibility of the pseudo-random sampling harness.

---

## 5. Pre-Registered Decision Hierarchy Outcome

Following Section 13 of the pre-registered protocol:

| Level | Condition | Evaluation Result | Status |
|---|---|---|---|
| **NC Check** | Any Negative Control (NC1–NC8) fails | All 8 NCs passed ($100\%$) | **PASSED** |
| **RESULT-P0** | No probabilistic signal ($D_{\text{TV}} \le \tau_{\text{TV}}$) | $D_{\text{TV}} \gg \tau_{\text{TV}}$ across all $\gamma$ | **REJECTED** |
| **RESULT-P1** | Probabilistic signal holds, argmax identical | Confirmed ($D_{\text{pol}} = 0.0000$) | **SATISFIED** |
| **RESULT-P2** | Temperature monotonic amplification | Confirmed (strict monotonic increase) | **SATISFIED** |
| **RESULT-P3** | **Sampling-Level Action Differentiation** | $D_{\text{samp}} > \tau_{\text{TV}}$ across all $\gamma$, rising to $7.58\%$ at $\gamma = 4.00$ | **CONFIRMED (RESULT_P3)** |

### Formal Classification
**Classification**: `RESULT_P3 — SAMPLING_LEVEL_ACTION_DIFFERENTIATION`  
**Rationale**: Probabilistic policy representation preserves continuous R3 directional signal ($D_{\text{TV}} = 0.013767$ at $\gamma = 1.00 > 10^{-4}$), probability divergence strictly increases monotonically with temperature $\gamma$ ($0.003291 \to 0.057267$), and reproducible sampled-action divergence is observed under common random numbers ($\max D_{\text{samp}} = 0.075798 > 10^{-4}$) while deterministic argmax remains locked at $D_{\text{pol}} = 0.0000$.

---

## 6. Answers to Core Research Questions

### Primary Question Answered
> **When deterministic argmax collapses R3 directional value differences into identical actions, does a fixed-temperature probabilistic policy preserve those differences, and can those differences produce reproducible sampled-action differentiation?**

**Direct Answer (Preregistered Empirical Findings)**:
1. **Yes, probabilistic policies preserve R3 directional differences with high fidelity.** Across all five temperatures $\gamma \in [0.25, 4.00]$, Total Variation distance ($D_{\text{TV}} = 0.0033$ to $0.0573$) and Jensen-Shannon divergence ($D_{\text{JS}} = 1.2 \times 10^{-5}$ to $3.6 \times 10^{-3}$) strictly exceed pre-registered thresholds by up to $573\times$, while the scalar null baseline C0 directional shift remains identically zero.
2. **Yes, increasing decision temperature monotonically amplifies the probability separation.** The relation $\gamma \mapsto D_{\text{TV}}$ is strictly monotonic increasing ($0.0033 \to 0.0067 \to 0.0138 \to 0.0285 \to 0.0573$).
3. **Yes, this preserved difference translates into empirical sampled-action differentiation.** When actions are sampled from the softmax distribution using common random numbers, discordant probe pairs produce divergent actions in $0.56\%$ ($\gamma = 0.25$) to $7.58\%$ ($\gamma = 4.00$) of sampled encounters ($2.21\%$ at canonical $\gamma = 1.00$), despite deterministic argmax selecting `retrieve` for 100% of probes in lockstep ($D_{\text{pol}} \equiv 0.0000$).
4. **Argmax equivalence is invariant.** In 100% of probes (716/716) and across all temperatures, the modal action of the softmax distribution remains mathematically identical to the deterministic winner ($\operatorname{argmax}(P) \equiv \operatorname{argmax}(V)$).

---

## 7. Quality Gate 2 & Governance Invariants

1. **Gate 2 Status**: **`STRICTLY BLOCKED`**.
   $$\Delta_{\text{HM}} = 0.0685 < 0.1500$$
   Because deterministic argmax action divergence remains $D_{\text{pol}} = 0.0000$, Quality Gate 2 cannot be unlocked.
2. **Phase 22 H1 Status**: **`INCONCLUSIVE`**.
3. **ADR-029 Ledger Status**: **`DRAFT / RESEARCH RECORD ONLY / NOT RATIFIED`**.
4. **Zero Production Mutation Invariant**: `src/core/**` git diff $= 0$, `src/api/**` git diff $= 0$, `electron/**` git diff $= 0$.
5. **Genesis Onboarding Gate**: `data/profile.json` remains bit-exact `{"is_onboarded": false}`.
6. **20-Watt Hardware Constraint**: All simulations and evaluations executed strictly on CPU with 0.0 MB GPU VRAM.

---

## 8. Artifact Ledger & Verification

| Artifact | Location | SHA-256 / Checksum Status |
|---|---|---|
| Manifest | [`manifest_h1_r3_probabilistic_policy.json`](file:///c:/Users/Lunafiah/Desktop/My_project/Lucia/tests/evaluation_phase22/fixtures/manifest_h1_r3_probabilistic_policy.json) | Pre-registered & committed |
| Evaluation Harness | [`evaluate_h1_r3_probabilistic_policy.py`](file:///c:/Users/Lunafiah/Desktop/My_project/Lucia/tests/evaluation_phase22/scripts/evaluate_h1_r3_probabilistic_policy.py) | Verified executable |
| Dedicated Test Suite | [`test_h1_r3_probabilistic_policy.py`](file:///c:/Users/Lunafiah/Desktop/My_project/Lucia/tests/evaluation_phase22/test_h1_r3_probabilistic_policy.py) | 28/28 tests passing |
| Empirical Results Fixture | [`results_h1_r3_probabilistic_policy.json`](file:///c:/Users/Lunafiah/Desktop/My_project/Lucia/tests/evaluation_phase22/fixtures/results_h1_r3_probabilistic_policy.json) | Complete 358-pair data across 5 temperatures $\times$ 4 conditions |
| Negative Controls Fixture | [`nc_h1_r3_probabilistic_policy.json`](file:///c:/Users/Lunafiah/Desktop/My_project/Lucia/tests/evaluation_phase22/fixtures/nc_h1_r3_probabilistic_policy.json) | NC1–NC8 all passed ($100\%$) |
| 15-Point Formal Report | [`report_h1_r3_probabilistic_policy.json`](file:///c:/Users/Lunafiah/Desktop/My_project/Lucia/tests/evaluation_phase22/fixtures/report_h1_r3_probabilistic_policy.json) | Complete pre-registered schema |
| CSV Summary | [`summary_h1_r3_probabilistic_policy.csv`](file:///c:/Users/Lunafiah/Desktop/My_project/Lucia/tests/evaluation_phase22/fixtures/summary_h1_r3_probabilistic_policy.csv) | 20 condition-temperature rows with bootstrap CIs |
