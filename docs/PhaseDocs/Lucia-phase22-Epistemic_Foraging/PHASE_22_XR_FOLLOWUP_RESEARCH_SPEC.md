# Phase 22-XR Follow-Up — Research Specification: Observation Alignment, Neural Backbone Verification & Predictive Calibration

> **Research Evolution Specification**: Phase 22-XR Follow-Up (Targeted Remediation of P22-XR G-XR1, G-XR2, G-XR4)  
> **Topic**: Formal Observation-to-Latent Forward Mapping, Standalone Laya Neural Backbone Verification, and Principled Predictive Uncertainty Calibration  
> **Status**: `[CURRENT RESEARCH — DESIGN ONLY]` | **Production Implementation**: `STRICTLY NOT AUTHORIZED`  
> **Governance Authority**: `AGENTS.md` §0, §6, §7; `docs/00_PROJECT_OVERVIEW.md` §3.1; `docs/L1_INVARIANTS.md` §6; `evaluation_artifacts/phase22_xr/post_evaluation_architectural_analysis.md`  
> **Production Code Mutations**: Exactly 0 (`src/core/**`, `electron/**`, `config/**`, and `data/**` strictly untouched)  
> **Genesis Gate**: Preserved bit-exact (`data/profile.json == {"is_onboarded": false}`)  
> **Date**: September 2026  

---

## 1. Status & Governance

This document establishes the controlled research design for the next iteration of **Lucia Phase 22-XR**. It is authored strictly in response to the empirical findings established in `evaluation_artifacts/phase22_xr/post_evaluation_architectural_analysis.md`:

1. **Research is Not Production (`AGENTS.md` §0):** This is a research specification only. No production implementation is authorized.
2. **Preservation of Canonical Results:** Previous empirical results from Phase 22-X (`Run B`) and Phase 22-XR (`raw_measurements.json`) remain immutable historical evidence.
3. **Threshold Discipline:** No pre-registered gate thresholds from Phase 22-XR are modified or relaxed to manufacture passing results.
4. **Zero Production Mutation:** `src/core/**`, `electron/**`, `config/**`, and `data/**` remain untouched.
5. **Decoupled Future Horizon:** Phase 23 (Continuous Semantic State) remains independent.

---

## 2. Context & Root Causes from Phase 22-XR

The canonical evaluation of Phase 22-XR demonstrated strong positive evidence for continuous dynamics, but identified three distinct, unresolved structural bottlenecks:

```text
┌────────────────────────────────────────────────────────────────────────┐
│ Phase 22-XR Canonical Findings                                         │
│ • G-XR3 (Flapping): 0.40% (vs P22-X 23.80%)                            │ -> VALIDATED: Continuous state relaxation suppresses flapping
│ • G-XR5 (Recovery): 1.0 turn                                           │ -> VALIDATED: Rapid adaptation without inertia lock-in
│ • G-XR6 (Downstream Latency): 0.12 ms P50                              │ -> DEMONSTRATED: Negligible mathematical filter overhead
│                                                                        │
│ • G-XR2 (Tracking R²): -34.88                                          │ -> FAILED: Naive mapping (y = 2p - 1, H = I) caused coordinate mismatch
│ • G-XR1 (Calibration ECE): 0.3349                                      │ -> UNVERIFIED: Fallback emulation evaluated, not real Laya backbone
│ • G-XR4 (Density Coverage): 28.67% at H=2                              │ -> FAILED: Predictive covariance under-dispersed relative to diffusion
└───────────────────────────────────┬────────────────────────────────────┘
                                    │ Target Remediation
                                    ▼
┌────────────────────────────────────────────────────────────────────────┐
│ Phase 22-XR Follow-Up Research Focus                                   │
│ 1. Problem R1: Observation → Latent Forward Mapping g(z)               │
│ 2. Problem R2: Standalone Laya Neural Backbone Verification Protocol   │
│ 3. Problem R3: Principled Predictive Uncertainty Calibration           │
└────────────────────────────────────────────────────────────────────────┘
```

---

## 3. Core Research Questions (R1–R3)

### Research Question 1 (RQ1 — Observation Alignment)
> **"Does replacing the naive linear heuristic ($y = 2p - 1, \mathbf{H} = \mathbf{I}$) with a mathematically aligned observation forward model $\mathbf{g}: \mathcal{Z} \to \Delta^{M-1}$ enable the continuous Bucy-Kalman filter to achieve non-negative tracking accuracy ($R^2 \ge 0.85$) against ground truth $\mathbf{z}^*(t) \in \mathbb{R}^6$ without leaking simulator state into the observer?"**

### Research Question 2 (RQ2 — Real Laya Backbone Verification)
> **"Does the actual pretrained Laya neural backbone (`ModernBERT-large` 421M / `mmBERT-base` 322M) maintain strictly proper calibration ($\text{ECE}_{\text{shift}} \le 0.10$) under conversational noise and lexical sparsity, or was the measured calibration collapse ($\text{ECE} = 0.3349$) an artifact of the keyword-based fallback emulation?"**

### Research Question 3 (RQ3 — Predictive Uncertainty Calibration)
> **"Can prospective trajectory density forecasting achieve $\ge 75\%$ empirical coverage at horizon $H=2$ through principled process noise scaling and horizon-dependent diffusion growth while maintaining forecast sharpness (bounding Mahalanobis volume)?"**

---

## 4. Formal Hypotheses & Falsification Conditions

### 4.1 Hypothesis H1 (Observation Alignment)
- **Null Hypothesis ($H_{1,0}$):** The negative tracking score ($R^2 = -34.88$) is intrinsic to continuous filtering in $\mathbb{R}^6$; no valid forward mapping $\mathbf{g}(\mathbf{z})$ can achieve $R^2 \ge 0.70$ from discrete probe observations.
- **Alternative Hypothesis ($H_{1,1}$):** Formulating an aligned observation model $\mathbf{g}(\mathbf{z}) = \text{softmax}(\mathbf{W}_{\text{obs}}\mathbf{z} + \mathbf{b}_{\text{obs}})$ enables the Bucy-Kalman filter to track $\mathbf{z}^*(t)$ with $R^2 \ge 0.85$ and $\text{MSE} \le 0.08$.
- **Falsification Condition:** If an optimally fitted, non-leaking forward model fails to achieve $R^2 \ge 0.70$ on held-out validation episodes, $H_{1,1}$ is rejected and continuous user belief modeling is falsified.

### 4.2 Hypothesis H2 (Real Laya Verification)
- **Null Hypothesis ($H_{2,0}$):** Bidirectional transformer encoders trained under RLCD still suffer calibration collapse ($\text{ECE} > 0.15$) when exposed to conversational speech disfluencies, noisy acoustic features, and lexical sparsity.
- **Alternative Hypothesis ($H_{2,1}$):** The real pretrained Laya checkpoint preserves calibration ($\text{ECE}_{\text{shift}} \le 0.10$) under distribution shifts where the heuristic fallback collapsed to $0.3349$.
- **Falsification Condition:** If the executed real Laya checkpoint exhibits $\text{ECE}_{\text{shift}} > 0.15$ under `NoiseSurge` (DS-1), $H_{2,1}$ is rejected and Laya is disqualified as Lucia's observation primitive.

### 4.3 Hypothesis H3 (Predictive Uncertainty Calibration)
- **Null Hypothesis ($H_{3,0}$):** Short-horizon trajectory density coverage cannot be elevated from $28.67\%$ to $\ge 75\%$ without inflating covariance ellipsoids to uninformative volumes (losing predictive sharpness).
- **Alternative Hypothesis ($H_{3,1}$):** Modeling multi-step diffusion growth ($\mathbf{Q}_k = \sum_{j=1}^k \mathbf{\Phi}^{k-j} \mathbf{Q} (\mathbf{\Phi}^{k-j})^\top$) achieves $\ge 75\%$ coverage at $H=2$ while bounding generalized variance ($\det(\mathbf{P}_{t+2}) \le \tau_{\text{sharp}}$).
- **Falsification Condition:** If coverage at $H=2$ remains $< 50.0\%$ under bounded sharpness, $H_{3,1}$ is rejected and continuous trajectory density forecasting is abandoned.

---

## 5. Candidate Models & Architectures

### 5.1 Observation Forward Models for R1
To avoid ad-hoc adjustments, four distinct candidate forward models $\mathbf{g}(\mathbf{z})$ are evaluated:

1. **M1 — Direct Affine Slicing (Minimal Baseline):**
   $$\mathbf{y}_{\text{pred}} = \mathbf{H} \mathbf{z}, \quad \mathbf{H} = \begin{bmatrix} \mathbf{I}_{6 \times 6} \end{bmatrix}$$
   Treats observations as continuous noisy projections bounded to $[-1, 1]$ (re-calibrating the heuristic).
2. **M2 — Softmax-Linear Observation Model (Generative Categorical):**
   $$\mathbf{g}(\mathbf{z}) = \text{softmax}\left(\frac{\mathbf{W}_{\text{obs}} \mathbf{z} + \mathbf{b}_{\text{obs}}}{T_{\text{obs}}}\right) \in \Delta^5$$
   Where $\mathbf{W}_{\text{obs}} \in \mathbb{R}^{6 \times 6}$ is fitted exclusively on an independent synthetic calibration split (never exposed to evaluation episodes). The extended Kalman innovation is computed as $\tilde{\mathbf{y}} = \mathbf{p}_{\text{obs}} - \mathbf{g}(\hat{\mathbf{z}}^-)$ with Jacobian $\mathbf{J}_g(\hat{\mathbf{z}}^-)$.
3. **M3 — Nonlinear MLP Inversion Map:**
   $$\hat{\mathbf{z}}_{\text{obs}} = \text{MLP}_{\text{inv}}(\mathbf{p}_{\text{obs}}) \in \mathbb{R}^6$$
   A 2-layer MLP (6 $\to$ 24 $\to$ 6) that projects probe probability vectors directly into continuous latent coordinates prior to linear Kalman innovation.
4. **M4 — Log-Odds / Dirichlet Likelihood Formulation:**
   $$\mathbf{y}_{\text{logit}} = \ln(\mathbf{p}_{\text{obs}} + \epsilon) - \frac{1}{M}\sum \ln(p_i + \epsilon)$$
   Maps simplex probabilities into unconstrained log-odds space where linear Gaussian assumptions are mathematically valid.

### 5.2 Real Laya Integration Architecture for R2
Treats Laya strictly as an external Python package via a verified boundary:
- **Checkpoint Variants:**
  - Variant A: `convaiinnovations/laya` (ModernBERT-large 421M, English Latin-script)
  - Variant B: `convaiinnovations/laya-multilingual` (mmBERT-base 322M, 51 languages)
- **Strict Provenance States:**
  - `VERIFIED_BY_EXECUTION`: Checkpoint loaded, forward pass executed on local PyTorch, weights audited.
  - `BLOCKED_OFFLINE_WEIGHTS`: Weights unavailable locally; test terminates as `BLOCKED` (zero emulator substitution permitted).

### 5.3 Uncertainty Propagation Formulations for R3
1. **C1 — Fixed Process Noise (P22-XR Baseline):**
   $$\mathbf{P}_{t+k} = \mathbf{\Phi}^k \mathbf{P}_t (\mathbf{\Phi}^k)^\top + k \mathbf{Q}$$
2. **C2 — Discrete-Time Cumulative Lyapunov Diffusion:**
   $$\mathbf{P}_{t+k} = \mathbf{\Phi}^k \mathbf{P}_t (\mathbf{\Phi}^k)^\top + \sum_{j=0}^{k-1} \mathbf{\Phi}^j \mathbf{Q} (\mathbf{\Phi}^j)^\top$$
3. **C3 — Innovation-Adaptive Covariance Scaling:**
   $$\mathbf{Q}_t = \alpha \mathbf{Q}_0 + (1 - \alpha) \mathbf{K}_t \tilde{\mathbf{y}}_t \tilde{\mathbf{y}}_t^\top \mathbf{K}_t^\top$$
4. **C4 — Empirical Coverage Calibration (Horizon-Dependent Temperature):**
   Scaling the critical Mahalanobis threshold $\chi^2_{\text{eff}}(k) = c(k) \cdot \chi^2_6(0.90)$ fitted on validation trajectories.

---

## 6. Information Leakage & Anti-Circularity Audit

To ensure scientific validity, the harness must eliminate all possible information leakage routes:

| Component | Potential Leakage Route | Enforced Architectural Guardrail | Verification Test |
|---|---|---|---|
| **Observation Model $\mathbf{g}(\mathbf{z})$** | Fitting $\mathbf{W}_{\text{obs}}$ on evaluation episodes. | Strict split separation: parameters $\mathbf{W}_{\text{obs}}$ are fitted on 2,000 independent calibration turns (seed 9999). Parameter weights are frozen before evaluation starts. | Verify parameter hash invariance during test runs. |
| **Bucy-Kalman Filter** | Accessing simulator state `step.true_latent_state`. | Encapsulation boundary: the filter receives ONLY `obs_result.probabilities` and `obs_result.confidence`. It has zero access to the `SimUserEnvV2` instance. | Python inspect audit verifying call signatures. |
| **Predictive Density** | Using future environment steps during covariance propagation. | Forward forecasting is computed strictly from $\mathbf{z}_t$ and model dynamics; future ground truth is queried ONLY by the evaluator after forecast emission. | Temporal ordering audit in harness runner. |
| **Real Laya Adapter** | Using true intent labels to guide probe answers. | Adapter accepts ONLY raw text string and acoustic features. Intent labels are inaccessible. | Black-box adapter test. |

---

## 7. Controlled Ablation Matrix (B0–B7)

To isolate causal attribution across R1, R2, and R3, eight explicit ablations are evaluated across identical seeds:

| Ablation ID | Observation Primitive | Forward Map $\mathbf{g}(\mathbf{z})$ | Belief Filter | Predictive Uncertainty | Active EIG | Causal Hypothesis Isolated |
|---|---|---|---|---|---|---|
| **B0** | Random Prior | None | None | None | None | Absolute bottom baseline |
| **B1** | B4 Surrogate | Heuristic ($2p - 1$) | Discrete Bayes | Discrete Tree ($H=2$) | None | Replicates Phase 22-X baseline |
| **B2** | B4 Surrogate | Heuristic ($2p - 1$) | Continuous Bucy-Kalman | Fixed Covariance (C1) | None | Replicates Phase 22-XR baseline |
| **B3** | B4 Surrogate | **Aligned Map (M2)** | **Continuous Bucy-Kalman** | Fixed Covariance (C1) | None | **Tests Observation Alignment (R1)** |
| **B4** | Lightweight Calibrated | **Aligned Map (M2)** | **Continuous Bucy-Kalman** | Fixed Covariance (C1) | None | Tests Model Capacity vs Alignment |
| **B5** | **Real Laya (Offline)** | **Aligned Map (M2)** | **Continuous Bucy-Kalman** | Fixed Covariance (C1) | None | **Tests Real Laya Backbone (R2)** |
| **B6** | Real Laya / LightCal | **Aligned Map (M2)** | **Continuous Bucy-Kalman** | **Calibrated Diffusion (C2)**| None | **Tests Uncertainty Calibration (R3)**|
| **B7** | Real Laya / LightCal | **Aligned Map (M2)** | **Continuous Bucy-Kalman** | **Calibrated Diffusion (C2)**| **Active EIG** | Full Closed-Loop Proposal |

---

## 8. Quantitative Evaluation Metrics

### 8.1 Observation Alignment (R1)
- **Tracking $R^2$**: $1 - \frac{\sum \|\mathbf{z}^* - \hat{\mathbf{z}}\|^2}{\sum \|\mathbf{z}^* - \bar{\mathbf{z}}^*\|^2}$ (Aggregate and per-dimension).
- **Mean Squared Error (MSE)** and **Mean Absolute Error (MAE)**.
- **Innovation Orthogonality**: Autocorrelation of innovation vector $\mathbb{E}[\tilde{\mathbf{y}}_t \tilde{\mathbf{y}}_{t-1}^\top] \approx \mathbf{0}$.

### 8.2 Real Laya Backbone Calibration (R2)
- **Expected Calibration Error (ECE)** across 15 bins.
- **Multi-Class Brier Score** and **Negative Log-Likelihood (NLL)**.
- **In-Distribution vs. Out-of-Domain Degradation Ratio**: $\text{ECE}_{\text{shift}} / \text{ECE}_{\text{ID}}$.

### 8.3 Predictive Uncertainty Calibration (R3)
- **Empirical Ellipsoid Coverage**: Percentage of ground-truth states falling within the 90% confidence ellipsoid at $H \in \{1, 2, 3\}$.
- **Forecast Sharpness (Log Generalized Variance)**: $\ln \det(\mathbf{P}_{t+k})$.
- **Coverage-Sharpness Trade-off Index (CSI)**: $\text{Coverage}(H) / \ln \det(\mathbf{P}_{t+H})$.

### 8.4 Execution Profiling
- **Component Breakdown Latency**: Measured independently for (1) observation pass, (2) forward mapping $\mathbf{g}(\mathbf{z})$, (3) Kalman update, and (4) trajectory lookahead.

---

## 9. Preregistered Architecture Gates

All gate thresholds remain strictly identical to Phase 22-XR. No thresholds are lowered:

| Gate ID | Target Metric | Required Gate Threshold | Pre-Registered Falsification Ceiling | Rationale & Preregistration Status |
|---|---|---|---|---|
| **G-XR1** | $\text{ECE}_{\text{shift}}$ (Real Laya) | $\le 0.10$ | $> 0.15$ | **Preserved:** Measures real Laya backbone calibration under noise surge. |
| **G-XR2** | Tracking Accuracy ($R^2$) | $\ge 0.85$ | $< 0.70$ | **Preserved:** Evaluates whether aligned observation model resolves coordinate mismatch. |
| **G-XR3** | Closed-Loop Flapping Rate | $\le 9.5\%$ | $> 15.0\%$ | **Preserved:** Confirms continuous relaxation keeps flapping near 0.40%. |
| **G-XR4** | Density Coverage ($H=2$) | $\ge 75.0\%$ | $< 50.0\%$ | **Preserved:** Tests whether calibrated covariance propagation resolves under-dispersion. |
| **G-XR5** | Contradiction Recovery | $\le 1.0\text{ turn}$ | $> 2.0\text{ turns}$ | **Preserved:** Ensures model does not suffer from inertia lock-in. |
| **G-XR6** | CPU Latency SLA | P50 $\le 350\,\text{ms}$ | P50 $> 500\,\text{ms}$ | **Preserved:** End-to-end cognitive turn loop SLA on desktop CPU. |

---

## 10. Execution Safeguards & Failure Modes

1. **Fail-Closed on Missing Weights:** If real Laya weights cannot be verified locally via SHA-256 hash or Hugging Face cache, Track XR-E1 must terminate immediately with state `BLOCKED_WEIGHTS_UNAVAILABLE`.
2. **Sharpness Guardrail:** If an uncertainty calibration technique achieves $\ge 75\%$ coverage but expands log generalized variance by $> 300\%$ over baseline, the technique is flagged as trivial over-inflation.
3. **Zero Production Mutation:** Verified before and after all experiments via `git diff -- src electron config data`.
