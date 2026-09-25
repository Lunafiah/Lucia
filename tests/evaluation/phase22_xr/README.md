# Phase 22-XR Evaluation Harness: Jev/Laya Architectural Verification & Continuous User Belief Modeling

> **Status:** `[CURRENT RESEARCH]` | **Production Implementation:** `STRICTLY NOT AUTHORIZED`  
> **Governance Authority:** `AGENTS.md` §0, §6, §7; `docs/00_PROJECT_OVERVIEW.md` §3.1; `docs/L1_INVARIANTS.md` §6; `docs/specs/Lucia-phase22-Epistemic_Foraging/PHASE_22_XR_RESEARCH_SPEC.md`

---

## 1. Purpose

This isolated evaluation harness tests the core scientific hypotheses and falsification criteria defined in:
- `docs/specs/Lucia-phase22-Epistemic_Foraging/PHASE_22_XR_RESEARCH_SPEC.md`
- `docs/specs/Lucia-phase22-Epistemic_Foraging/PHASE_22_XR_EVALUATION_PLAN.md`

Specifically, it measures:
1. **Laya's Real Interface & Calibration (XR-E1, XR-E2):** Whether a real non-generative decision primitive maintains calibration under severe distribution shift where the B4 surrogate collapsed.
2. **Continuous User Belief Dynamics (XR-E3, XR-E4):** Whether a continuous Bucy-Kalman ODE formulation ($z_{\text{user}}(t) \in \mathbb{R}^6$) resolves the $23.8\%$ belief flapping rate seen in Phase 22-X.
3. **Continuous Trajectory Density (XR-E5):** Whether prospective covariance propagation over ODE drift replaces discrete branching trees without exponential path dispersion.
4. **Post-Observation Intent Interpretation (XR-E6):** Decoupling prospective continuous state forecasting from speech-act interpretation.
5. **Epistemic Action Selection (XR-E7):** Active inquiry over continuous covariance.
6. **Phase 23 Interface Contract (XR-E8):** Mathematical validation of the 12D observation forcing vector $\boldsymbol{\psi}_{\text{user}}(t)$.
7. **Ablation Matrix (A0–A7):** Causal attribution across 8 comparative conditions.

---

## 2. Directory Layout

```text
tests/evaluation/phase22_xr/
├── README.md                  # This file
├── __init__.py                # Package root
├── config.py                  # Core dimensions, probes, and gate thresholds
├── seeds.py                   # Evaluation seeds (42, 137, 618, 1024, 2026) and stress regimes
├── schemas.py                 # Dataclasses and contracts
├── metrics.py                 # ECE, Brier, NLL, R², flapping rate, ellipsoid coverage
├── statistics.py              # Bootstrap CI, paired t-tests, Holm-Bonferroni correction
├── resource_measurement.py    # Latency, RAM, and VRAM profiling
├── baselines/                 # A0, A1, A2, A5 baseline models
├── continuous/                # Continuous user state, ODE dynamics, Bucy-Kalman, density
├── laya/                      # External adapter for cloned Laya repository
├── intent/                    # Prospective prediction vs post-observation interpretation
├── epistemic/                 # Epistemic Action Selection policy (EIG)
├── interface/                 # P23 Interface contract verification
├── simulator/                 # SimUserEnv-v2 ground-truth continuous environment
├── experiments/               # XR-E1 through XR-E8 individual experiment runners
├── run_experiments.py         # Canonical CLI experiment runner
├── validate_results.py        # Automated auditor and gate validator
└── runner.py                  # Single-command end-to-end evaluation runner
```

---

## 3. Execution Commands

### Execute Full Evaluation Suite
```bash
python -m tests.evaluation.phase22_xr.run_experiments --experiment all
```

### Execute Specific Experiment Track
```bash
python -m tests.evaluation.phase22_xr.run_experiments --experiment xr_e1
python -m tests.evaluation.phase22_xr.run_experiments --experiment xr_e4
```

### Execute Ablation Matrix (A0–A7)
```bash
python -m tests.evaluation.phase22_xr.run_experiments --experiment ablations
```

### Validate Results & Gate Calculations
```bash
python tests/evaluation/phase22_xr/validate_results.py evaluation_artifacts/phase22_xr/raw_measurements.json
```

---

## 4. Hardware Constraints & Invariants

- **CPU Budget:** Desktop real-time loop ($\le 350\,\text{ms}$ P50 latency).
- **GPU Budget:** Zero impact on Lucia cognitive VRAM ($0.0\,\text{MB}$ GPU VRAM on CPU-only runs).
- **Production Isolation:** Zero modifications to `src/core/`, `electron/`, `config/`, or `data/`.
- **Genesis Onboarding:** Bit-exact preservation of `data/profile.json` (`{"is_onboarded": false}`).
