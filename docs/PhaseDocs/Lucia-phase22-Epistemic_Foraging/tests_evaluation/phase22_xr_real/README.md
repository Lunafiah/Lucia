# Phase 22-XR-L: Real Laya Observation Verification Harness

## Overview
This harness executes a narrow, fail-closed research verification pass for the **Real Laya neural backbone** (`convaiinnovations/laya`, ModernBERT-large 421M parameters) and evaluates observation-to-latent alignment (A0 naive, A1 linear, A2 nonlinear MLP).

## Governance Invariants
- **Fail-Closed**: If physical weights (`model.safetensors`) are missing, the harness enters `BLOCKED_OFFLINE_WEIGHTS`. No emulator is substituted.
- **Zero Production Modification**: `src/core/**`, `electron/**`, `config/**`, and `data/**` remain untouched.
- **Genesis Onboarding**: `data/profile.json` remains bit-exact `{"is_onboarded": false}`.

## Modules
- `provenance.py`: Inspects repository and HF cache for genuine weights, generates `model_manifest.json` and `provenance.json`.
- `adapter.py`: Strict fail-closed wrapper for ModernBERT-large inference.
- `corpus.py`: Multi-regime deterministic test dataset (clean, perturbations, typos, sparsity, multilingual EN/VI/JA).
- `observation_alignment/models.py`: Implements A0 (naive heuristic), A1 (Ridge regression), and A2 (bounded MLP).
- `metrics.py`: Computes ECE, Brier score, NLL, $R^2$, MSE, MAE, flapping rate.
- `resource_measurement.py`: Captures hardware specs, OS, CPU, RAM, CUDA, PyTorch versions.
- `run_experiments.py`: Master runner executing matrix B0–B5, generating `raw_measurements.json` and markdown reports.
- `validate_results.py`: Independent schema and governance auditor.
