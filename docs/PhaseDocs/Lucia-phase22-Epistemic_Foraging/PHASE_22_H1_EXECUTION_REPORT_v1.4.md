# Phase 22 H1 Benchmark Execution Report — Protocol v1.4

> **FORMAL RESEARCH BENCHMARK EXECUTION REPORT**  
> **Status:** `[COMPLETED — VERDICT: INCONCLUSIVE (BLOCKED BY QUALITY GATE 2)]`  
> **Governance:** Ratified Protocol Amendment v1.4 | **Architecture Gate:** LOCKED  
> **Date:** September 16, 2026 | **Timestamp (UTC):** 2026-09-16T12:45:14Z  
> **Dataset Path:** [`tests/evaluation_phase22/results/h1_v14/`](file:///c:/Users/Lunafiah/Desktop/My_project/Lucia/tests/evaluation_phase22/results/h1_v14/)

---

## Executive Summary

Under explicit project owner authorization, the ratified **Phase 22 H1 Protocol Amendment v1.4** benchmark was formally executed through the audited headless production pipeline (`StimulusProcessor` $\to$ `EmotionCore` $\to$ `ActiveInferenceEngine`).

1. **Preflight Gate**: All 15 mandatory preflight checks passed closed (`[GO] ALL 15 PREFLIGHT CHECKS PASSED`).
2. **Frozen Input Integrity**: The canonical fixture ($N = 270$) matched the preregistered SHA-256 digest (`9adf33c1...`) bit-exact.
3. **Execution Scope**: $1,350$ headless production evaluations across 5 canonical environmental seeds ($42, 43, 44, 45, 46$) were executed with zero errors, zero missing data, and complete state reset isolation between probes.
4. **Candidate C1 Calibration Result**: Successfully resolved the Path C variance defect: all 9 factorial cells achieved $\text{Var}(U_{\text{sem}} \mid \text{cell}) \ge 0.0020$ (Cell 4: $0.003831 \ge 0.0020$, $1.92\times$ the floor). Gate 4 passed with 100% compliance.
5. **Quality Gate 2 Result**: **FAILED**. While $\Delta_{ML}(T=12) = 0.3145 \ge 0.1000$ passed decisively, $\Delta_{HM}(T=12) = 0.0685 < 0.1500$ failed the preregistered threshold. Under multi-tick integration ($T=12$), the Medium-Surprise relational stimuli produced substantial limbic displacement ($\bar{S}_M = 0.5792$), compressing the separation from High-Surprise emergency stimuli ($\bar{S}_H = 0.6477$).
6. **Downstream Statistical Analyses**:
   - **Track A (GLM Spillover)**: Both models passed directional spillover thresholds ($U \to S: \eta_p^2 = 0.000000 < 0.02$; $S \to U: \eta_p^2 = 0.005769 < 0.02$).
   - **Track B (TOST Equivalence)**: $\hat{\rho}_{\text{partial}} = -0.039288$, $90\%\,\text{CI} = [-0.140966, \quad +0.063210]$, strictly within $[-0.20, +0.20]$, $p_{\text{TOST}} = 4.398 \times 10^{-3} < 0.05$.
7. **Final Protocol Verdict & Decoupling Interpretation**: In accordance with the preregistered Decision Matrix (Section 14), downstream TOST equivalence cannot override a failed prerequisite manipulation gate. Therefore:
   - **Track A and Track B provide statistical evidence consistent with the preregistered decoupling criterion ($\eta_p^2 \le 0.005769$, $\hat{\rho}_{\text{partial}} = -0.0393$, $90\%\,\text{CI} \subset [-0.20, +0.20]$), but H1 remains INCONCLUSIVE because Gate 2 failed.**
   - The official verdict is:
   $$\mathbf{FINAL\ VERDICT:\ INCONCLUSIVE\ (BLOCKED\ BY\ QUALITY\ GATE\ 2)}$$

---

## 1. Governance & Protocol Baseline

| Parameter | Governing Authority | Ratified Value |
|---|---|---|
| **Protocol Specification** | [`PHASE_22_H1_PROTOCOL_AMENDMENT_v1.4.md`](file:///c:/Users/Lunafiah/Desktop/My_project/Lucia/docs/specs/Lucia-phase22-Epistemic_Foraging/PHASE_22_H1_PROTOCOL_AMENDMENT_v1.4.md) | **v1.4 (Ratified / Frozen)** |
| **Governance Status** | Project Owner Authorization | **FORMALLY RATIFIED & EXECUTED** |
| **Architecture Gate** | [`AGENTS.md`](file:///c:/Users/Lunafiah/Desktop/My_project/Lucia/AGENTS.md) Section 7 | **STRICTLY LOCKED** |
| **Production Source Code** | `src/core/**` | **100% Bit-Exact Untouched** |
| **Genesis Onboarding State** | `data/profile.json` | **`{"is_onboarded": false}` (Bit-Exact)** |
| **Historical Original H1** | Benchmark Report | `FAILED` ($R^2 = 0.2766 > 0.15$) — Preserved |
| **Historical Path C H1** | [`PHASE_22_H1_EXECUTION_REPORT_PATH_C.md`](file:///c:/Users/Lunafiah/Desktop/My_project/Lucia/docs/specs/Lucia-phase22-Epistemic_Foraging/PHASE_22_H1_EXECUTION_REPORT_PATH_C.md) | `INCONCLUSIVE` (Gates 2 & 4) — Preserved |

---

## 2. Frozen Experimental Design & Preflight Verification

### 2.1 Frozen Parameters
- **Factorial Design**: $3 \times 3$ crossed factorial ($S_{\text{target}} \in \{\text{Low, Med, High}\} \times U_{\text{target}} \in \{\text{Low, Med, High}\}$).
- **Sample Allocation**: Exactly 30 probes per cell across 9 cells ($N = 270$ unique probes).
- **Exposure Allocation**: Balanced 10/10/10 split across $T \in \{1, 4, 12\}$ exposure ticks within **every cell**.
- **Equivalence Margin**: $\Delta = 0.20$ ($\Delta_z \approx 0.202733$).
- **Proposition Generator**: Candidate C1 ($c \sim \text{Uniform}(0.900, 0.995)$, $k \sim \text{DiscreteUniform}(2, 4)$).
- **Manifest SHA-256 Digest**:
  ```text
  9adf33c18c30eec2d966b2d279574386ec29463356b0c3ff2353c9eda9b22255
  ```

### 2.2 Preflight Validation Results (15/15 PASS)
Prior to running a single benchmark evaluation, the mandatory preflight validator ([`tests/evaluation_phase22/scripts/validate_h1_v14_preflight.py`](file:///c:/Users/Lunafiah/Desktop/My_project/Lucia/tests/evaluation_phase22/scripts/validate_h1_v14_preflight.py)) verified all 15 preregistered criteria:

| # | Preflight Check | Requirement | Observed Metric | Result |
|---|---|---|---|---|
| **1** | Sample Size | $N = 270$ | $N = 270$ | **PASS** |
| **2** | Factorial Cells | Exactly 9 cells (1..9) | 9 cells | **PASS** |
| **3** | Cell Allocation | Exactly 30 probes/cell | 30 in all 9 cells | **PASS** |
| **4** | Exposure Balance | Exactly 10/10/10 per cell | 10 at $T=1, 4, 12$ in all 9 cells | **PASS** |
| **5** | Probe ID Uniqueness | 270 distinct IDs | 270 unique IDs | **PASS** |
| **6** | Stimulus Text Uniqueness | 270 distinct strings | 270 unique strings | **PASS** |
| **7** | Design Matrix Orthogonality | Rank=11, Cond $\approx 1.0$, Off-Diag $< 10^{-10}$ | Rank=11, Cond=1.0000, Max Off-Diag=$2.89 \times 10^{-15}$ | **PASS** |
| **8** | Actual Sample $U$ Variance | $\text{Var}(U) \ge 0.0020$ in all 9 cells | Low Cells: C1=0.0051, C4=0.0038, C7=0.0056 | **PASS** |
| **9** | Actual Sample $U$ Separation | $\Delta_{ML}, \Delta_{HM} \ge 0.2500$ | $\Delta_{ML} = 0.3393, \Delta_{HM} = 0.2659$ | **PASS** |
| **10** | Gate 2 $T=12$ Structure | 10 probes/cell at $T=12$, authorized texts | Exactly 90 probes at $T=12$, valid vocabulary | **PASS** |
| **11** | Anti-Cherry-Picking Invariant | Deterministic forward generation | Verified sequential IDs, 4 domains balanced | **PASS** |
| **12** | Frozen Manifest Integrity | SHA-256 bit-exact match | Digest matched `9adf33c1...` | **PASS** |
| **13** | Production Pipeline Integrity | Genuine production callables | `StimulusProcessor`, `EmotionCore`, `ActiveInferenceEngine` | **PASS** |
| **14** | Genesis Gate Invariant | `is_onboarded: false` bit-exact | `{"is_onboarded": false}` | **PASS** |
| **15** | Production Code Invariant | `src/core/**` 100% clean | Git status clean (0 modifications) | **PASS** |

---

## 3. Production Pipeline & Execution Metrics

### 3.1 Headless Production Pipeline
Each probe observation was evaluated through the genuine production component stack:
1. `core.reset_to_resting()` and `ai.reset()` executed before every turn.
2. Initial resting PAD baseline $p_0 = (P_0, A_0, D_0)$ captured.
3. Raw stimulus string parsed via `StimulusProcessor.encode()`.
4. Continuous physiological ODE integration over $T \in \{1, 4, 12\}$ ticks via `EmotionCore.push_stimulus()` and `commit_stimulus()`, obtaining $p_T$.
5. Genuine prediction error calculated via `ActiveInferenceEngine.step(p0, pT)`.
6. Proposition entropy $U_{\text{sem}}$ derived from probe propositions.

### 3.2 Execution Profile
- **Total Evaluations**: $270 \text{ probes} \times 5 \text{ seeds} = 1,350 \text{ runs}$.
- **Seeds**: $42, 43, 44, 45, 46$ (randomized probe presentation order per seed).
- **Execution Time**: $12.92$ seconds ($9.57\,\text{ms}$ per evaluation).
- **GPU VRAM Impact**: $0.0\,\text{MB}$ (100% CPU execution path).
- **Errors / Dropouts**: $0$ ($100\%$ completion rate).

---

## 4. Mandatory Quality Gates Evaluation

```text
Gate 1: Pipeline Integrity              -> PASS (1350/1350 complete, 0 missing)
Gate 2: Surprise Manipulation (T=12)    -> FAIL (Delta_ML=0.3145 PASS, Delta_HM=0.0685 FAIL)
Gate 3: Uncertainty Manipulation        -> PASS (Delta_ML=0.3393 PASS, Delta_HM=0.2659 PASS)
Gate 4: Within-Cell Variance Floors     -> PASS (All 9 cells meet both U and S floors)
----------------------------------------------------------------------------------------
OVERALL QUALITY GATES STATUS            -> FAILED (Blocked by Gate 2)
```

### 4.1 Gate 1 — Experimental / Pipeline Integrity (`PASS`)
- 1,350 seed-level evaluations successfully executed.
- 270 aggregated probe-level units constructed without data loss.
- Zero state leakage verified across resets.

### 4.2 Gate 2 — Surprise Manipulation Check at $T = 12$ (`FAIL`)
Evaluated across the 90 probes conditioned on standardized exposure duration $T = 12$ ticks (30 probes per $S$ tier):

| Metric | Required Threshold | Observed Value | Gate Status |
|---|---|---|---|
| **$\bar{S}_L(T=12)$** | Baseline | $0.2647$ | — |
| **$\bar{S}_M(T=12)$** | $\bar{S}_M > \bar{S}_L$ | $0.5792$ | Monotonic |
| **$\bar{S}_H(T=12)$** | $\bar{S}_H > \bar{S}_M$ | $0.6477$ | Monotonic |
| **$\Delta_{ML}(T=12)$** | $\ge 0.1000$ | **$+0.3145$** | **PASS** ($3.15\times$ threshold) |
| **$\Delta_{HM}(T=12)$** | $\ge 0.1500$ | **$+0.0685$** | **FAIL** ($0.46\times$ threshold) |
| **ANOVA $F(2, 87)$** | $p < 0.001$ | $F = 136.0122, p = 1.664 \times 10^{-27}$ | **PASS** |

#### Observed Mechanistic Pattern / Hypothesized Explanation
At $T = 12$ exposure ticks ($2.4\,\text{s}$ continuous ODE integration time), an empirical compression between Medium- and High-surprise tiers was observed: $\bar{S}_M(T=12) = 0.5792$ vs. $\bar{S}_H(T=12) = 0.6477$, resulting in $\Delta_{HM}(T=12) = 0.0685 < 0.1500$. While the ordering was strictly monotonic ($\bar{S}_L < \bar{S}_M < \bar{S}_H$) and highly statistically significant ($F = 136.01, p = 1.664 \times 10^{-27}$), the observed separation failed the preregistered threshold of $0.1500$.

*Hypothesized Mechanistic Explanation*:
A plausible hypothesis for this compression is that collaborative relational phrases in the Medium tier drove sustained limbic arousal and valence displacement away from the Philia resting baseline ($P=+0.25, A=-0.05, D=+0.05$) across 12 consecutive integration ticks, approaching the non-linear damping boundary of the attractor. Because the limbic state space is bounded and damped, high-arousal emergency stimuli in the High tier could only displace the state incrementally further, compressing the empirical difference between tiers.

*Epistemic Boundary & Required Follow-Up*:
Because this benchmark did not include isolated phase-plane trajectory ablations or ODE damping parameter sweeps, this mechanism must be treated strictly as an **observed empirical pattern and mechanistic hypothesis**, rather than an established causal root cause. Formal causal verification would require a dedicated dynamical study isolating Euler step accumulation, Philia damping bounds, and stimulus lexical valence weights.

#### Complete Exposure Structure (Diagnostic Disclosure)
| Exposure Duration | Low Tier Mean ($\bar{S}_L$) | Med Tier Mean ($\bar{S}_M$) | High Tier Mean ($\bar{S}_H$) | $\Delta_{ML}$ | $\Delta_{HM}$ |
|---|---|---|---|---|---|
| **$T = 1$ tick** | $0.0243$ | $0.0876$ | $0.0904$ | $+0.0633$ | $+0.0028$ |
| **$T = 4$ ticks** | $0.0952$ | $0.2677$ | $0.3092$ | $+0.1725$ | $+0.0416$ |
| **$T = 12$ ticks** | $0.2647$ | $0.5792$ | $0.6477$ | $+0.3145$ | $+0.0685$ |
| **Pooled Marginal** | $0.1281$ | $0.3115$ | $0.3491$ | $+0.1834$ | $+0.0376$ |

### 4.3 Gate 3 — Uncertainty Manipulation Check (`PASS`)
Evaluated across all $N = 270$ probe-level means:
- **Marginal Tier Means**: $\bar{U}_L = 0.2778$, $\bar{U}_M = 0.6170$, $\bar{U}_H = 0.8829$.
- **Separation $\Delta_{ML}$**: $0.6170 - 0.2778 = \mathbf{0.3393} \ge 0.2500$ (**PASS**).
- **Separation $\Delta_{HM}$**: $0.8829 - 0.6170 = \mathbf{0.2659} \ge 0.2500$ (**PASS**).
- **Monotonicity**: $0.2778 < 0.6170 < 0.8829$ (**PASS**).
- **One-Way ANOVA**: $F(2, 267) = 2020.1913, p = 5.912 \times 10^{-162}$ (**PASS**).

### 4.4 Gate 4 — Within-Cell Variance Floors (`PASS`)
Candidate C1 successfully resolved the sampling variance defect from Path C across all 9 cells:

| Cell ID | $S_{\text{target}}$ | $U_{\text{target}}$ | Observed $\text{Var}(U_{\text{sem}})$ | $U$ Variance Floor ($\ge 0.0020$) | Observed $\text{Var}(S_{\text{observed}})$ | $S$ Variance Floor ($\ge 0.0005$) | Cell Gate Status |
|---|---|---|---|---|---|---|---|
| **Cell 1** | Low | Low | **$0.005068$** | PASS ($2.53\times$) | **$0.019237$** | PASS ($38.5\times$) | **PASS** |
| **Cell 2** | Low | Med | **$0.002921$** | PASS ($1.46\times$) | **$0.019237$** | PASS ($38.5\times$) | **PASS** |
| **Cell 3** | Low | High | **$0.003663$** | PASS ($1.83\times$) | **$0.019237$** | PASS ($38.5\times$) | **PASS** |
| **Cell 4** | Med | Low | **$0.003831$** | **PASS ($1.92\times$)** | **$0.043651$** | PASS ($87.3\times$) | **PASS** |
| **Cell 5** | Med | Med | **$0.002930$** | PASS ($1.47\times$) | **$0.043651$** | PASS ($87.3\times$) | **PASS** |
| **Cell 6** | Med | High | **$0.005122$** | PASS ($2.56\times$) | **$0.043651$** | PASS ($87.3\times$) | **PASS** |
| **Cell 7** | High | Low | **$0.005623$** | PASS ($2.81\times$) | **$0.056455$** | PASS ($112.9\times$) | **PASS** |
| **Cell 8** | High | Med | **$0.004400$** | PASS ($2.20\times$) | **$0.056455$** | PASS ($112.9\times$) | **PASS** |
| **Cell 9** | High | High | **$0.003343$** | PASS ($1.67\times$) | **$0.056455$** | PASS ($112.9\times$) | **PASS** |

*Note: In Path C, Cell 4 failed with $\text{Var}(U) = 0.001711 < 0.0020$. Candidate C1 elevated Cell 4 to $0.003831$, achieving $100\%$ compliance across the $3 \times 3$ factorial matrix.*

---

## 5. Statistical Analyses (Diagnostic Evaluation)

*Per Section 11 and 14 of the Protocol, downstream analyses are reported for complete scientific transparency. Track A and Track B provide empirical evidence consistent with the preregistered decoupling criterion, but cannot establish H1 confirmation due to prerequisite Gate 2 failure.*

### 5.1 Track A — General Linear Model (Spillover Analysis)
Evaluated via OLS regression against the 11-column orthonormal design matrix $X \in \mathbb{R}^{270 \times 11}$ ($\text{df}_{\text{resid}} = 259$):

#### Model A1: $U_{\text{target}} \to S_{\text{observed}}$
$$\bar{S}_{\text{observed}} = \mu_S + \beta_S S + \beta_U U + \beta_{SU} (S \times U) + \beta_T T + \varepsilon_S$$
- **Partial Eta-Squared ($\eta_p^2$)**: **$0.000000$** (Primary Threshold: $< 0.02$).
- **Diagnostic $F$-Statistic**: $F(2, 259) = 0.0000, p = 1.0000$.
- **Result**: Zero directional spillover from semantic uncertainty to physiological surprise ($\eta_p^2 = 0.000000 < 0.02$). Consistent with the decoupling criterion (Reported as diagnostic evidence; Gate 2 failed).

#### Model A2: $S_{\text{target}} \to U_{\text{sem}}$
$$\bar{U}_{\text{sem}} = \mu_U + \gamma_U U + \gamma_S S + \gamma_{SU} (S \times U) + \gamma_T T + \varepsilon_U$$
- **Partial Eta-Squared ($\eta_p^2$)**: **$0.005769$** (Primary Threshold: $< 0.02$).
- **Diagnostic $F$-Statistic**: $F(2, 259) = 0.7514, p = 0.4727$.
- **Result**: Negligible directional spillover ($0.58\%$ partial variance, $\eta_p^2 = 0.005769 < 0.02$). Consistent with the decoupling criterion (Reported as diagnostic evidence; Gate 2 failed).

### 5.2 Track B — Partial Correlation & TOST Equivalence Testing
- **Residual Partial Correlation**: $\hat{\rho}_{\text{partial}} = \mathbf{-0.039288}$.
- **Partial $R^2$**: $0.001544$ ($0.154\%$ shared residual variance).
- **Fisher's $z$**: $\hat{z} = -0.039308, \text{SE}_z = 0.062378$ ($N_{\text{eff}} = 257$).
- **$90\%$ Confidence Interval**:
  $$\mathbf{[-0.140966, \quad +0.063210]}$$
  Strictly bounded within the equivalence margin $(-\Delta, +\Delta) = (-0.20, +0.20)$.
- **TOST $p$-Value**: $p_{\text{TOST}} = \mathbf{4.3979 \times 10^{-3}} < 0.05$.
- **Result**: Equivalence bounds condition statistically met ($90\%\,\text{CI} \subset [-0.20, +0.20], p < 0.05$). Consistent with the preregistered equivalence criterion, but reported as diagnostic evidence only; H1 remains INCONCLUSIVE due to prerequisite Gate 2 failure.
- **Raw Diagnostic Correlation**: Pearson $r = -0.016406, p = 0.7884, R^2 = 0.000269$.

### 5.3 Holm-Bonferroni Multiplicity Adjustment
| Rank | Hypothesis Test | Raw $p$-Value | Critical Alpha $\alpha_{\text{HB}}$ | Adjusted $p$-Value | Family Outcome |
|---|---|---|---|---|---|
| **1** | Gate 3: Uncertainty Manipulation | $5.912 \times 10^{-162}$ | $3.333 \times 10^{-4}$ | $1.774 \times 10^{-161}$ | **PASS** |
| **2** | Gate 2: Surprise Manipulation ($T=12$) | $1.664 \times 10^{-27}$ | $5.000 \times 10^{-4}$ | $3.328 \times 10^{-27}$ | **PASS (Statistical)** |
| **3** | Track B: TOST Equivalence | $4.398 \times 10^{-3}$ | $5.000 \times 10^{-2}$ | $4.398 \times 10^{-3}$ | **PASS** |

*Note: While Gate 2 passes its ANOVA null-hypothesis test ($p < 10^{-26}$), it failed the preregistered minimum effect size separation threshold ($\Delta_{HM} \ge 0.1500$).*

---

## 6. Pathology Audit

| Pathology Category | Scope / Detector Rule | Observed Count | Threshold | Status |
|---|---|---|---|---|
| **Agent Runtime Ego Leakage** | BoundaryLayer regex on model-generated output | $0$ tokens / phrases | $0$ | **PASS** (Zero agent text generated) |
| **Stimulus Template Safety Matches** | BoundaryLayer regex on input stimulus strings | $12$ matches | Diagnostic | **INFO / FALSE POSITIVE CANDIDATE** (User-side prompt wording) |
| **Computational Budget Breach** | Per-probe P95 Latency $> 5.0\,\text{ms}$ | P95 = $18.952\,\text{ms}$ | $\le 5.0\,\text{ms}$ | **INFO (Multi-Tick Exposure Artifact)** |
| **Interrogation Trap** | Rapid clarification loops | $0$ | $0$ | **PASS** |
| **Dark Room Trap** | Aleatoric noise fixation | $0$ | $0$ | **PASS** |
| **Epistemic Starvation** | Unaddressed high uncertainty | $0$ | $0$ | **PASS** |

### Pathology Diagnostic Notes
1. **Latency Note**: The single-tick Tier-1 SLA is $\le 5.0\,\text{ms}$. The multi-tick exposure loop ($T=12$ ticks = 12 consecutive ODE calls per probe) averaged $9.56\,\text{ms}$ total per probe across 12 sequential ODE integrations ($0.79\,\text{ms}$ per tick, well within the $5.0\,\text{ms}$ limit). Multi-tick composite latency is therefore an informational artifact of multi-step integration, not a per-step budget breach.
2. **Introspective Ego Leakage Classification & Protocol Scope**:
   - *Protocol Definition Check*: In Lucia's canonical architecture (`AGENTS.md` Invariant 2, Section 1) and Phase 22 behavioral specifications, "Introspective Ego Leakage" is defined strictly as an **agent runtime output pathology** — prohibiting the language model from declaring or self-reporting its internal affect in dialogue (e.g., *"I feel happy"*, *"I am conscious"*, *"As an AI..."*).
   - *Agent Output Generation*: In this headless sensory benchmark, Lucia evaluated sensory surprisal up to `ActiveInferenceEngine.step(p0, pT)` with **zero natural language generation** ($0$ LLM tokens produced). Therefore, agent-generated introspective ego leakage at runtime is strictly **0 (PASS)**.
   - *Input Stimulus Template Analysis*: The 12 matches detected by `COMPILED_EGO_PATTERNS` occurred entirely within the **input stimulus prompt templates** (specifically the string `\bI feel\b` in 12 relational collaborative phrases within Cells 4 and 5, such as *"I feel a gentle sense of satisfaction as these tests pass cleanly together"* and *"I feel confident in our direction..."*). These are user-side conversational utterances designed to simulate human dialogue, not agent self-reports.
   - *Classification*: These 12 occurrences are formally classified as **template-level safety-regex matches / false-positive candidates** arising from applying an output-filtering validator to input stimulus text. They do not constitute introspective behavior by Lucia.

---

## 7. Official Protocol Decision

Applying Section 14 (Decision Matrix) of `PHASE_22_H1_PROTOCOL_AMENDMENT_v1.4.md`:

```text
Decision Matrix Condition:
  Gate 1: PASS
  Gate 2: FAIL  (Delta_HM(T=12) = 0.0685 < 0.1500)
  Gate 3: PASS
  Gate 4: PASS
  Track A: Consistent with Decoupling Criterion (eta_p^2 < 0.02)
  Track B: Consistent with Decoupling Criterion (TOST confirmed)

  -> MANDATORY GOVERNANCE RULE: When any prerequisite Quality Gate (1..4) fails, the official verdict MUST be INCONCLUSIVE.
     Downstream statistical equivalence CANNOT override a failed manipulation check.
```

$$\mathbf{OFFICIAL\ VERDICT:\ INCONCLUSIVE\ (BLOCKED\ BY\ QUALITY\ GATE\ 2)}$$

### Scientific Conclusion
1. **Candidate C1 Success**: The Monte Carlo-calibrated Candidate C1 proposition generator completely solved the Gate 4 variance floor issue. All cells demonstrated robust within-cell variance ($\text{Var}(U) \ge 0.0020$).
2. **Evidence Consistent with Decoupling Criterion (Diagnostic Only)**: Track A ($\eta_p^2 \le 0.0058$) and Track B ($\hat{\rho}_{\text{partial}} = -0.0393$, $90\%\,\text{CI} \subset [-0.20, +0.20]$) provide statistical evidence consistent with the preregistered decoupling criterion (residual shared variance $< 0.16\%$). However, H1 remains **INCONCLUSIVE** because prerequisite Gate 2 failed.
3. **Observed Surprise Compression at T=12 (Mechanistic Hypothesis)**: The empirical failure of Gate 2 ($\Delta_{HM}(T=12) = 0.0685 < 0.1500$) demonstrates that under multi-tick integration, Medium-Surprise relational stimuli produced substantial limbic displacement ($\bar{S}_M = 0.5792$), compressing the separation from High-Surprise emergency stimuli ($\bar{S}_H = 0.6477$). While we hypothesize that this reflects cumulative limbic arousal approaching attractor damping boundaries, this causal mechanism remains an observed hypothesis without dedicated phase-plane ablations. Recalibrating the Gate 2 operational definition or redesigning stimulus contrast requires independent empirical investigation before any future confirmatory run.

---

## 8. Dataset Immutability & Reproducibility Hashes

All datasets have been frozen under [`tests/evaluation_phase22/results/h1_v14/`](file:///c:/Users/Lunafiah/Desktop/My_project/Lucia/tests/evaluation_phase22/results/h1_v14/):

| Dataset Artifact | File Path | SHA-256 Digest |
|---|---|---|
| **Execution Metadata** | `execution_metadata.json` | `791b3802c0ec1562c0764348643331d648360d0188025cdb92fd6a60434672de` |
| **Raw Seed Evaluations** | `raw_evaluations.json` | `d92ce780862f2902f5b98b56e2e50cf1824878694c9a021b048b21a9c04b8a6b` |
| **Probe-Level Summaries** | `probe_summary.json` | `2dd6b0ecf823c2dcd3c1e1654034d36defafdc0d362072c4b29b97220be89f96` |
| **Consolidated Summary** | `phase22_h1_v14_summary.json` | `25fcc050bbe1726fd8b19955440592d01a59a115863a132538d4d5ee3aff88a9` |
| **Probe Manifest** | `manifest_h1_v14.json` | `9adf33c18c30eec2d966b2d279574386ec29463356b0c3ff2353c9eda9b22255` |

---

## 9. Architectural Invariant Verification

- **Production Code (`src/core/**`)**: **100% untouched** (0 modifications).
- **Genesis Onboarding (`data/profile.json`)**: **`{"is_onboarded": false}`** bit-exact intact.
- **Historical Evidence**: Original H1 (`FAILED`) and Path C (`INCONCLUSIVE`) remain unperturbed.
- **Architecture Gate**: Remains strictly **LOCKED**.
