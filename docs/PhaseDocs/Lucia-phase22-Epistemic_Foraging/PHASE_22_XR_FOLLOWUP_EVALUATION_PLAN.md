# Phase 22-XR Follow-Up — Research Evaluation Plan: Observation Alignment, Neural Backbone Verification & Predictive Calibration

> **Research Evaluation Protocol**: Phase 22-XR Follow-Up (Isolated Experimental Plan)  
> **Topic**: Empirical Protocols for Observation-to-Latent Forward Mapping, Standalone Laya Neural Verification, and Principled Uncertainty Calibration  
> **Status**: `[CURRENT RESEARCH — DESIGN ONLY]` | **Production Implementation**: `STRICTLY NOT AUTHORIZED`  
> **Governance Authority**: `AGENTS.md` §0, §6, §7; `docs/00_PROJECT_OVERVIEW.md` §3.1; `docs/L1_INVARIANTS.md` §6; `docs/specs/Lucia-phase22-Epistemic_Foraging/PHASE_22_XR_FOLLOWUP_RESEARCH_SPEC.md`  
> **Production Code Mutations**: Exactly 0 (`src/core/**`, `electron/**`, `config/**`, and `data/**` strictly untouched)  
> **Genesis Gate**: Preserved bit-exact (`data/profile.json == {"is_onboarded": false}`)  
> **Date**: September 2026  

---

## 1. Evaluation Objectives & Scope

This evaluation plan defines the precise experimental protocols required to address the three unresolved problems from Phase 22-XR:

1. **Track XR2-E1 (Observation Forward Model Calibration & Tracking Accuracy):** Compare candidate forward models M1–M4 to determine whether observation alignment restores tracking accuracy ($R^2 \ge 0.85$) without ground-truth leakage.
2. **Track XR2-E2 (Real Laya Neural Backbone Verification):** Execute standalone verification of `convaiinnovations/laya` weights on local PyTorch, measuring in-distribution vs out-of-domain ECE under fail-closed provenance guards.
3. **Track XR2-E3 (Predictive Covariance Propagation & Sharpness):** Evaluate diffusion formulations C1–C4 to determine whether prospective density forecasting achieves $\ge 75\%$ coverage at $H=2$ while bounding generalized variance.
4. **Track XR2-E4 (Continuous Belief Stability & Contradiction Replication):** Verify that continuous relaxation preserves low flapping ($\le 9.5\%$) and rapid contradiction recovery ($\le 1.0\text{ turn}$) under the aligned observation model.
5. **Track XR2-E5 (Ablation Matrix & Causal Attribution):** Execute the B0–B7 ablation matrix across 5 independent seeds.

---

## 2. Experimental Environment & Anti-Circularity Protocol

### 2.1 Simulation Environment (`SimUserEnv-v2.1`)
Extends `SimUserEnv-v2` with an explicit anti-leakage boundary:
- **Independent Calibration Split (Dataset $\mathcal{D}_{\text{cal}}$):** 2,500 turns generated using seed `9999`. Used strictly for fitting forward map parameters ($\mathbf{W}_{\text{obs}}, \mathbf{b}_{\text{obs}}$).
- **Evaluation Splits (Datasets $\mathcal{D}_{\text{eval}}$):** Evaluated across 5 fixed evaluation seeds (`42, 137, 618, 1024, 2026`) across 6 stress regimes (`ID`, `NoiseSurge`, `LexicalSparsity`, `ContradictionShock`, `TemporalDrift`, `CombinedStress`).
- **Strict Black-Box Boundary:** The evaluated model receives strictly the observation payload:
  $$\mathcal{O}_t = \{u_t, \mathbf{x}_t^{\text{obs}}\}$$
  Ground truth $\mathbf{z}^*(t)$ is completely inaccessible during filtering.

---

## 3. Detailed Experimental Protocols

### 3.1 Track XR2-E1 — Observation Forward Mapping & Coordinate Alignment
- **Objective:** Evaluate candidate forward mappings M1 (Direct Affine), M2 (Softmax-Linear), M3 (Nonlinear MLP), and M4 (Log-Odds Dirichlet) against ground truth tracking.
- **Protocol:**
  1. Fit parameters on $\mathcal{D}_{\text{cal}}$ (seed `9999`).
  2. Freeze observation model parameters $\boldsymbol{\theta}_{\text{obs}}$.
  3. Execute 500 multi-turn steps on $\mathcal{D}_{\text{eval}}$ across seeds `[42, 137, 618, 1024, 2026]`.
  4. Measure continuous Bucy-Kalman tracking: aggregate $R^2$, per-dimension $R_d^2$, and innovation autocorrelation $\rho_{\tilde{y}}(1)$.
- **Success Criteria:** Aggregate $R^2 \ge 0.85$, all per-dimension $R_d^2 \ge 0.70$, innovation autocorrelation $|\rho| \le 0.10$.

### 3.2 Track XR2-E2 — Standalone Real Laya Backbone Verification
- **Objective:** Measure empirical calibration of the genuine pretrained Laya transformer encoder.
- **Protocol:**
  1. Check for local presence of model weights under `C:\Users\Lunafiah\Desktop\My_project\laya\models\` or Hugging Face cache.
  2. If weights are missing, record status as `BLOCKED_OFFLINE_WEIGHTS` and terminate test cleanly (no synthetic emulation permitted).
  3. If weights are present, execute 1,000 forward passes across `ID`, `NoiseSurge` (DS-1), and `LexicalSparsity` (DS-4).
  4. Measure 15-bin ECE, Brier score, NLL, P50/P95 latency, and peak RAM/VRAM.
- **Falsification Threshold:** If $\text{ECE}_{\text{shift}} > 0.15$ on real weights, Laya is falsified.

### 3.3 Track XR2-E3 — Predictive Covariance Propagation & Sharpness
- **Objective:** Evaluate whether multi-step diffusion growth (C2) or innovation-adaptive scaling (C3) resolves predictive under-dispersion without over-inflating ellipsoids.
- **Protocol:**
  1. At turn $t$, project future belief densities $p(\mathbf{z}_{t+k} \mid \mathbf{z}_t)$ for $k \in \{1, 2, 3\}$.
  2. Measure empirical coverage: proportion of future states $\mathbf{z}^*(t+k)$ within the 90% Mahalanobis ellipsoid ($d_M^2 \le 10.64$).
  3. Measure forecast sharpness: log generalized variance $\ln \det(\mathbf{P}_{t+k})$.
  4. Measure Coverage-Sharpness Index: $\text{CSI} = \text{Coverage}(H) / \max(1.0, \ln \det(\mathbf{P}))$.
- **Success Criteria:** Horizon $H=2$ coverage $\ge 75.0\%$, Horizon $H=1$ coverage $\ge 80.0\%$, and $\ln \det(\mathbf{P}_{t+2}) \le 2.5 \cdot \ln \det(\mathbf{P}_t)$.

### 3.4 Track XR2-E4 — Flapping Suppression & Contradiction Replication
- **Objective:** Confirm that continuous belief dynamics maintain low flapping ($\le 9.5\%$) and rapid recovery ($\le 1.0\text{ turn}$) when combined with aligned forward model M2.
- **Protocol:**
  1. Execute 2,000 closed-loop interaction turns across boundary regions.
  2. Compute flapping rate: proportion of turn-to-turn sign reversals.
  3. Introduce contradiction shock at turn 15; measure turns required for $\hat{\mathbf{z}}$ to cross the decision hyperplane.
- **Success Criteria:** Flapping rate $\le 9.5\%$ (targeting preservation of the $0.40\%$ result), recovery turns $\le 1.0\text{ turn}$.

### 3.5 Track XR2-E5 — Causal Attribution via Ablation Matrix (B0–B7)
- **Objective:** Execute the complete B0–B7 ablation matrix to causally attribute performance improvements to specific architectural components.
- **Protocol:** Run all 8 configurations across all 5 seeds on identical episodes; apply paired Wilcoxon signed-rank tests with Holm-Bonferroni correction ($\alpha = 0.01$).

---

## 4. Hardware & Resource SLA Protocol

Measurements must isolate every processing stage:
1. **Backbone Forward Pass Latency:** $t_{\text{backbone}}$ (target: GPU $\le 35\,\text{ms}$, CPU $\le 300\,\text{ms}$).
2. **Observation Forward Map Latency:** $t_{\text{map}}$ (target: CPU $\le 0.05\,\text{ms}$).
3. **Bucy-Kalman Update Latency:** $t_{\text{kalman}}$ (target: CPU $\le 0.15\,\text{ms}$).
4. **Trajectory Lookahead Latency:** $t_{\text{forecast}}$ (target: CPU $\le 0.10\,\text{ms}$).
5. **Total End-to-End Latency:** $t_{\text{total}} = t_{\text{backbone}} + t_{\text{map}} + t_{\text{kalman}} + t_{\text{forecast}}$.
- **Hardware Isolation Invariant:** Zero VRAM footprint on Lucia's primary generation pipelines.

---

## 5. Preregistered Architecture Gates

| Gate ID | Target Metric | Required Gate Threshold | Pre-Registered Falsification Ceiling | Action if Failed |
|---|---|---|---|---|
| **G-XR1** | Real Laya $\text{ECE}_{\text{shift}}$ | $\le 0.10$ | $> 0.15$ | Disqualify Laya; evaluate alternative lightweight calibrated heads. |
| **G-XR2** | Aligned Tracking Accuracy ($R^2$) | $\ge 0.85$ | $< 0.70$ | Falsify continuous user state formulation in $\mathbb{R}^6$. |
| **G-XR3** | Closed-Loop Flapping Rate | $\le 9.5\%$ | $> 15.0\%$ | Increase boundary relaxation damping $\mathbf{\Gamma}$. |
| **G-XR4** | Trajectory Coverage ($H=2$) | $\ge 75.0\%$ | $< 50.0\%$ | Falsify continuous trajectory density forecasting. |
| **G-XR5** | Contradiction Recovery | $\le 1.0\text{ turn}$ | $> 2.0\text{ turns}$ | Inject process covariance floor $\mathbf{Q}_{\text{min}}$ to prevent lock-in. |
| **G-XR6** | Total Pipeline Latency SLA | P50 $\le 350.0\,\text{ms}$ | P50 $> 500.0\,\text{ms}$ | Reject architecture as incompatible with desktop real-time cycle. |

---

## 6. Provenance Reporting Standards

Every output artifact generated under this protocol must include:
```json
{
  "provenance": {
    "protocol_version": "P22-XR-FollowUp-v1.0",
    "observation_model": "M2_SoftmaxLinear",
    "weights_status": "VERIFIED_BY_EXECUTION | BLOCKED_OFFLINE_WEIGHTS",
    "weights_sha256": "...",
    "diffusion_formulation": "C2_LyapunovDiffusion",
    "seeds_evaluated": [42, 137, 618, 1024, 2026],
    "git_commit": "...",
    "execution_timestamp": "..."
  }
}
```
No evaluation result will be admitted to canonical documentation without verified provenance metadata.
