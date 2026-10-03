# Phase 22-XR — Research Evaluation Plan: Jev/Laya Architectural Verification & Continuous User Belief Modeling

> **Research Evaluation Protocol**: Phase 22-XR (Targeted Evolution of Phase 22-X, Pre-Phase 23)  
> **Topic**: Empirical Evaluation of Calibrated Non-Generative Decision Primitives (Laya/Jev), Continuous User Belief Dynamics, Trajectory Density Forecasting, and Epistemic Action Selection  
> **Status**: `[CURRENT RESEARCH]` | **Production Implementation**: `STRICTLY NOT AUTHORIZED`  
> **Governance Authority**: `AGENTS.md` §0, §6, §7; `docs/00_PROJECT_OVERVIEW.md` §3.1; `docs/L1_INVARIANTS.md` §6; `docs/specs/Lucia-phase22-Epistemic_Foraging/PHASE_22_XR_RESEARCH_SPEC.md`  
> **Production Code Mutations**: Exactly 0 (`src/core/**`, `electron/**`, `config/**`, and `data/**` strictly untouched)  
> **Genesis Gate**: Preserved bit-exact (`data/profile.json == {"is_onboarded": false}`)  
> **Date**: September 2026  

---

## 1. Evaluation Objectives & Scope

### 1.1 Context
Phase 22-X demonstrated that while a non-generative discriminative surrogate (B4, 2,753 params) provided fast inference and high in-distribution calibration, the discrete categorical pipeline failed 5 of 7 gates due to representation collapse under noise, belief flapping ($23.8\%$), and prediction-tree dispersion ($30.0\%$ coverage at $H=2$).

This evaluation plan specifies the empirical validation protocol for **Phase 22-XR**, testing whether:
1. **Real Laya** (ModernBERT-large 421M / mmBERT-base 322M) provides robust observation calibration that survives noise and distribution shift where B4 collapsed.
2. A **continuous dynamical user belief model** ($\mathbf{z}_{\text{user}}(t) \in \mathbb{R}^6$) eliminates discrete belief flapping.
3. **Continuous trajectory density forecasting** replaces failed discrete prediction trees.
4. **Epistemic action selection (EIG)** over continuous uncertainty maintains disciplined conversational inquiry.
5. An observation forcing signal $\boldsymbol{\psi}_{\text{user}}(t)$ can interface cleanly with Phase 23.

### 1.2 Isolation & Safety Invariants
- 100% executed in isolated harnesses under `tests/evaluation/phase22_xr/`.
- Zero mutations to Lucia canonical production backend (`src/core/**`) or Electron frontend (`electron/**`).
- Genesis onboarding gate bit-exact preservation (`data/profile.json == {"is_onboarded": false}`).

---

## 2. Experimental Environment: `SimUserEnv-v2`

All experiments are conducted in an isolated, reproducible simulation environment extending Phase 22-X's `SimUserEnv-v1` to continuous latent dynamics:

### 2.1 Latent Continuous User Dynamics (Ground Truth Engine)
The synthetic user maintains an internal continuous cognitive/interaction state $\mathbf{z}^*(t) \in \mathbb{R}^6$:
$$\mathbf{z}^*(t) = [z_{\text{load}}^*, z_{\text{agency}}^*, z_{\text{valence}}^*, z_{\text{urgency}}^*, z_{\text{receptive}}^*, z_{\text{alignment}}^*]^\top$$

The true state evolves via a continuous Ornstein-Uhlenbeck (OU) process with non-linear conversational momentum:
$$\frac{d\mathbf{z}^*(t)}{dt} = -\mathbf{\Gamma}^* (\mathbf{z}^*(t) - \mathbf{z}_0^*) + \mathbf{f}_{\text{topic}}(t) + \mathbf{w}^*(t)$$
Where:
- $\mathbf{\Gamma}^* = \text{diag}(0.15, 0.10, 0.20, 0.25, 0.10, 0.15)$ governs relaxation rates.
- $\mathbf{f}_{\text{topic}}(t)$ represents exogenous topic momentum.
- $\mathbf{w}^*(t) \sim \mathcal{N}(\mathbf{0}, \mathbf{Q}^*)$ is continuous Brownian perturbation.

### 2.2 Epistemological Information Boundaries
Ground truth $\mathbf{z}^*(t)$ is strictly accessible to the evaluation harness for metric computation, but is completely hidden from the evaluated model. The environment strictly enforces:
```text
Ground Truth z*(t) → Utterance & Acoustic Emission → Observation o_t → Likelihood p_t → Belief z_user(t) → Prediction z_hat(t+k)
```
Predictions are evaluated against future ground truth $\mathbf{z}^*(t+k)$ and immediately discarded; they are never written to memory or used as inputs to the belief filter.

---

## 3. Comparative Baselines

| Baseline ID | Name | Observation Head | Belief State Model | Predictive Model |
|---|---|---|---|---|
| **B0** | Static Prior | Static lookup prior | None | Static prior |
| **B1** | Standard Calibrated MLP | 2,753-param MLP + Temp Scaling | Categorical Bayes Filter ($\Delta^4$) | Markov Transition $\mathbf{T}^*$ |
| **B4** | P22-X Surrogate | 2,753-param dual-head surrogate | Categorical Bayes Filter ($\Delta^4$) | Discrete Prediction Tree ($H=2$) |
| **B5** | Laya + Discrete Bayes | Real Laya Checkpoint (ModernBERT) | Categorical Bayes Filter ($\Delta^4$) | Discrete Prediction Tree ($H=2$) |
| **B6 (XR)** | **Full Phase 22-XR** | **Real Laya Checkpoint (ModernBERT)** | **Continuous Bucy-Kalman ODE ($\mathbb{R}^6$)** | **Continuous Trajectory Density** |

---

## 4. Required Ablation Matrix (A0–A7)

To ensure strict causal attribution and prevent assigning credit to Laya when the gain originates from continuous filtering, eight explicit ablations are evaluated across identical seeds:

| Ablation | Observation Primitive | Calibration Mechanism | Belief Filter Formulation | Temporal Forecasting | Epistemic Action (EIG) | Target Hypothesis Tested |
|---|---|---|---|---|---|---|
| **A0** | None (Random Prior) | None | None | None | None | Absolute bottom baseline |
| **A1** | B4 Surrogate (2.7k MLP) | Post-hoc Temp Scaling | Discrete Categorical Bayes ($\Delta^4$) | Discrete Tree ($H=2$) | None | Replicates P22-X Run B |
| **A2** | B4 Surrogate (2.7k MLP) | Post-hoc Temp Scaling | **Continuous ODE ($\mathbb{R}^6$)** | None | None | Tests Continuous Belief without Laya |
| **A3** | **Real Laya (421M)** | Uncalibrated ($T=1.0$) | Discrete Categorical Bayes ($\Delta^4$) | Discrete Tree ($H=2$) | None | Tests Laya without calibration |
| **A4** | **Real Laya (421M)** | **Bucketed Clamped Temp** | Discrete Categorical Bayes ($\Delta^4$) | Discrete Tree ($H=2$) | None | Tests Laya Calibration on Discrete Belief |
| **A5** | Lightweight Calibrated (B1) | Post-hoc Temp Scaling | **Continuous ODE ($\mathbb{R}^6$)** | **Continuous Density** | None | Tests Continuous Pipeline with cheap model |
| **A6** | **Real Laya (421M)** | **Bucketed Clamped Temp** | **Continuous ODE ($\mathbb{R}^6$)** | **Continuous Density** | None | Tests Full Proposed Architecture (Passive) |
| **A7** | **Real Laya (421M)** | **Bucketed Clamped Temp** | **Continuous ODE ($\mathbb{R}^6$)** | **Continuous Density** | **Active EIG Policy** | **Full Proposed Architecture (Closed-Loop)**|

### Causal Attribution Rules
1. **If A2 $\approx$ A6:** Continuous belief dynamics—not Laya—drives the improvement. Laya is not necessary.
2. **If A6 $\gg$ A2:** Laya's deep bidirectional semantic representation is essential to overcome observation noise.
3. **If A5 $\approx$ A6:** A lightweight CPU-friendly classifier is sufficient; Laya can be dropped to save CPU/memory.
4. **If A4 $\gg$ A3:** Strict proper scoring calibration is causally responsible for downstream stability.

---

## 5. Detailed Experimental Tracks (XR-E1 to XR-E8)

### Track XR-E1 — Real Laya Interface & Determinism Verification
- **Objective:** Empirically verify the runtime contract, execution latency, determinism, and memory footprint of the cloned Laya repository.
- **Protocol:**
  1. Load `convaiinnovations/laya` (ModernBERT-large 421M) and `convaiinnovations/laya-multilingual` (mmBERT-base 322M).
  2. Execute 1,000 forward passes over synthetic conversation turns with varying question counts ($M \in \{1, 3, 5, 10\}$).
  3. Measure latency across CPU (Ryzen 9, 8 intra-op threads) and GPU (CUDA, if available).
  4. Test output determinism under identical inputs: verify $\max |p_i^{(1)} - p_i^{(2)}| \le 10^{-7}$.
- **Metrics:** P50/P95 latency, peak RAM (MB), peak VRAM (MB), probability simplex invariant ($\sum p_i = 1.0$).
- **Success Criteria:** 100% deterministic output; zero memory leaks across 1,000 calls; valid probability simplex vectors.

### Track XR-E2 — Calibration & Distribution Shift Audit
- **Objective:** Compare observation calibration of Real Laya, B4 surrogate, and B1 under severe distribution shift.
- **Protocol:**
  1. Evaluate models on `SimUserEnv-v2` splits: `Canonical`, `Noise-Surge` (DS-1), `Contradiction-Shock` (DS-3), and `Lexical-Sparsity` (DS-4).
  2. Compute 15-bin Expected Calibration Error (ECE), Brier Score, and Negative Log-Likelihood (NLL).
  3. Test whether Laya's clamped temperature scaling preserves calibration on single-word and noisy utterances where B4 collapsed to $\text{ECE} = 0.5994$.
- **Metrics:** $\text{ECE}_{\text{canonical}}$, $\text{ECE}_{\text{shift}}$, Brier Score, AUROC of confidence gating.
- **Falsification Threshold:** If Laya fails to achieve $\text{ECE}_{\text{shift}} \le 0.10$ under noise surge and lexical sparsity, Gate XR-1 fails.

### Track XR-E3 — Continuous User Belief Tracking
- **Objective:** Measure tracking accuracy of the continuous Bucy-Kalman ODE filter relative to ground truth $\mathbf{z}^*(t) \in \mathbb{R}^6$.
- **Protocol:**
  1. Run 100 multi-turn trajectories ($T = 50$ turns each) in `SimUserEnv-v2`.
  2. Track state via continuous ODE innovation using Laya observation likelihoods.
  3. Compare against P22-X's discrete Bayes filter (mapped onto continuous coordinates via expectation).
- **Metrics:** Coefficient of determination $R^2 = 1 - \frac{\sum \|\mathbf{z}^* - \hat{\mathbf{z}}\|^2}{\sum \|\mathbf{z}^* - \bar{\mathbf{z}}^*\|^2}$, Mean Squared Error (MSE), Mean Absolute Error (MAE).
- **Falsification Threshold:** Gate XR-2 requires $R^2 \ge 0.85$ (MSE $\le 0.08$) across all 6 latent dimensions.

### Track XR-E4 — Belief Stability & Flapping Suppression
- **Objective:** Determine whether continuous belief dynamics eliminate the $23.80\%$ belief flapping rate observed in P22-X Run B.
- **Protocol:**
  1. Evaluate 15,000 turns of closed-loop interaction across ambiguous boundary regions.
  2. Measure flip rate: proportion of turns where the dominant interaction posture alternates across adjacent turns.
  3. Measure contradiction recovery turns: upon introducing ground-truth state reversal at $T=15$, count turns required for $\hat{\mathbf{z}}$ to cross the zero hyperplane.
- **Metrics:** Flapping Rate ($\% < 1$ turn reversals), Stability ($\%$ non-flapping episodes), Recovery Turns ($N_{\text{rec}}$).
- **Falsification Threshold:** Gate XR-3 requires Flapping Rate $\le 9.5\%$ (a $60\%$ reduction from P22-X baseline of $23.80\%$). Gate XR-5 requires recovery $\le 1.0\text{ turns}$.

### Track XR-E5 — Continuous Trajectory Density Forecasting
- **Objective:** Replace discrete prediction trees ($H=2, 3$) with continuous trajectory density forecasting and evaluate future-state coverage.
- **Protocol:**
  1. At turn $t$, forecast user belief density $p(\mathbf{z}_{t+k} \mid \mathbf{z}_t)$ for $k \in \{1, 2, 3\}$ using forward ODE drift and covariance propagation.
  2. Measure whether ground truth $\mathbf{z}^*(t+k)$ falls within the 90% confidence ellipsoid of the forecast density.
  3. Compare coverage against P22-X discrete prediction tree ($30.0\%$ at $H=2$).
- **Metrics:** Ellipsoid Trajectory Coverage ($\%$), Forecast NLL, Horizon Degradation Slope, Forecasting Latency ($\mu\text{s}$).
- **Falsification Threshold:** Gate XR-4 requires Trajectory Coverage $\ge 75.0\%$ at $H=2$.

### Track XR-E6 — Prospective Intent as Derived Variable
- **Objective:** Test whether reformulating intent as an observation-conditioned interpretation over continuous belief trajectories outperforms pre-turn intent prediction.
- **Protocol:**
  1. Model prospective intent via the two-stage formulation:
     $$P(\text{intent}_{t+1} \mid u_{t+1}, \hat{\mathbf{z}}_{t+1}) \propto P(u_{t+1} \mid \text{intent}_{t+1}) \cdot P(\text{intent}_{t+1} \mid \hat{\mathbf{z}}_{t+1})$$
  2. Compare Top-1 and Top-2 intent classification accuracy against P22-X pre-turn prospective baseline ($34.15\%$ Top-1).
- **Metrics:** Top-1 Intent Accuracy, Top-2 Accuracy, Macro-F1 across 8 intent classes.
- **Success Criteria:** Top-1 accuracy $\ge 70.0\%$ (resolving the P22-X failure mode).

### Track XR-E7 — Epistemic Action Selection (EIG)
- **Objective:** Evaluate active inquiry policy over continuous belief covariance.
- **Protocol:**
  1. Execute closed-loop interaction across 5,000 turns.
  2. Trigger epistemic queries (`clarify`, `probe`, `reflect`) when total belief entropy $H(\mathbf{z}_t)$ exceeds threshold $\tau_{\text{amb}}$.
  3. Measure whether clarification significantly reduces posterior entropy without exceeding the disciplined query ratio.
- **Metrics:** Clarification Ratio ($\% \text{ of turns}$), Mean Entropy Reduction ($\Delta H$ nats), False Query Rate ($\%$ queries during clear states).
- **Success Criteria:** Clarification ratio $\le 10.0\%$, Entropy reduction $\ge 0.35$ nats, False query rate $\le 2.0\%$.

### Track XR-E8 — P23 Continuous Semantic State Interface Contract
- **Objective:** Verify the mathematical and structural integrity of the interface vector $\boldsymbol{\psi}_{\text{user}}(t) = [\mathbf{z}_{\text{user}}(t), \text{diag}(\mathbf{P}_t)] \in \mathbb{R}^{12}$ connecting Phase 22-XR to Phase 23.
- **Protocol:**
  1. Mock Phase 23 continuous semantic state manifold.
  2. Pass $\boldsymbol{\psi}_{\text{user}}(t)$ across 1,000 simulation turns.
  3. Verify that the observation vector is bounded ($\|\boldsymbol{\psi}\|_\infty \le 1.0$), continuous ($C^0$), language-independent, and introduces zero token-generation dependencies.
- **Success Criteria:** Complete interface decoupling; zero NaN/inf propagation; execution time $\le 0.01\,\text{ms}$. Track XR-E8 is strictly an interface validation experiment, not Phase 23 implementation.

---

## 6. Architecture Gates & Threshold Discipline

| Gate ID | Target Metric | Required Gate Threshold | Falsification Threshold | Threshold Rationale & Classification | Action if Failed |
|---|---|---|---|---|---|
| **G-XR1** | $\text{ECE}_{\text{shift}}$ | $\le 0.10$ | $> 0.15$ | **Engineering constraint:** ensures covariance $\mathbf{R}_k$ reflects true observation error. Inherited from P22-X. | Reject Laya as observation primitive; evaluate alternative heads. |
| **G-XR2** | Tracking Accuracy ($R^2$) | $\ge 0.85$ (MSE $\le 0.08$) | $< 0.70$ | **Research target:** continuous filter must significantly beat discrete accuracy ($77.38\%$). | Re-tune observation map $\mathbf{g}(\mathbf{z})$ or increase state dimension. |
| **G-XR3** | Flapping Rate | $\le 9.5\%$ | $> 15.0\%$ | **Core research hypothesis:** requires a $60\%$ drop from P22-X baseline ($23.80\%$). | Increase boundary inertia $\mathbf{\Gamma}$ or add hysteresis band. |
| **G-XR4** | Density Coverage ($H=2$) | $\ge 75.0\%$ | $< 50.0\%$ | **Engineering usability:** replaces failed discrete tree coverage ($30.0\%$). | Expand covariance growth rate $\mathbf{Q}$ or switch to mixture density. |
| **G-XR5** | Contradiction Recovery | $\le 1.0\text{ turns}$ | $> 2.0\text{ turns}$ | **Safety constraint:** prevents inertial filtering from locking into stale states. Inherited from P22-X. | Inject covariance floor $\mathbf{P}_{\text{min}}$ to prevent lock-in. |
| **G-XR6** | Execution Latency | GPU $\le 50\text{ms}$, CPU $\le 350\text{ms}$ | CPU $> 500\text{ms}$ | **Hardware SLA constraint:** matches Lucia 20-Watt Whole Brain budget. | Reject ModernBERT on CPU; mandate GPU or ONNX quantization. |

---

## 7. Resource & Hardware Measurement Protocol

All measurements must report the exact execution platform and configuration:
- **Processor:** Physical CPU core count, thread allocation (`torch.set_num_threads(8)`, `torch.set_num_interop_threads(1)`).
- **RAM / VRAM:** Peak memory allocated via `tracemalloc` (CPU) and `torch.cuda.max_memory_allocated()` (GPU).
- **Sampling:** 100 warm-up runs, 1,000 timed evaluations.
- **Reporting:** Mean, median, P50, P95, and P99 latency.
- **Token Accounting:** Report exact input prompt tokens used; note that Laya generates exactly 0 text output tokens.

---

## 8. Statistical Methodology & Avoidance of Inappropriate Tests

1. **Random Seeds:** 5 fixed seeds (`42`, `137`, `618`, `1024`, `2026`) evaluated across all ablations and tracks.
2. **Confidence Intervals:** 95% non-parametric bootstrap confidence intervals ($B = 10,000$ resamples) reported for all primary metrics.
3. **Hypothesis Testing:**
   - **Normality Check:** Test metric distributions for normality using Shapiro-Wilk before applying parametric tests.
   - **Paired Comparisons:** Use Wilcoxon signed-rank tests for paired multi-turn comparisons when distributions are non-normal.
   - **Correction for Multiplicity:** Apply Holm-Bonferroni correction across the 8 ablation comparisons ($\alpha = 0.01$).
4. **Avoided Statistical Traps:**
   - Do **NOT** pool non-independent dialogue turns across episodes into a single t-test (violates i.i.d. assumption). Evaluate episode-level summary statistics.
   - Do **NOT** use standard error on bounded calibration metrics (ECE); report bootstrap percentiles instead.

---

## 9. Expected Artifacts

Upon completion of the evaluation, the harness must generate:
1. `evaluation_artifacts/phase22_xr/raw_measurements.json`: Machine-readable per-turn metrics.
2. `evaluation_artifacts/phase22_xr/ablation_matrix_results.md`: Complete A0–A7 comparative data.
3. `evaluation_artifacts/phase22_xr/calibration_shift_report.md`: Track XR-E2 reliability diagrams and ECE tables.
4. `evaluation_artifacts/phase22_xr/final_evaluation_report.md`: Gate G-XR1 to G-XR6 verdict and recommendations.

---
