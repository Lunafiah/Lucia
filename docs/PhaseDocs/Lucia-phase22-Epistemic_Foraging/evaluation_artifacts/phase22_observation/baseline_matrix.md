# BASELINE MATRIX: PHASE 22-XR REAL LAYA REFERENCE

> **Reference Target:** Real Laya Neural Backbone (`convaiinnovations/laya`)  
> **Model Architecture:** ModernBERT-large (421,438,464 parameters)  
> **Evaluation Mode:** 100% Local CPU Execution (PyTorch CPU, zero emulation)  
> **Status:** Canonical Historical Reference Baseline (Immutable)  

---

## 1. Canonical Measured Baseline Ledger

All numerical values below represent the historical reference baseline established during Phase 22-XR and its formal closure. They serve as the fixed point of comparison for Candidate Classes C1 through C6.

```text
Model:
convaiinnovations/laya
ModernBERT-large
421,438,464 parameters

Real neural inference:
CPU P50 = 607.67 ms
Total P50 = 607.83 ms

Calibration:
ECE = 0.2232
Brier = 0.0842

Continuous dynamics:
Flapping = 0.40%
Contradiction recovery = 1.0 turn

Naive observation alignment:
R² = -25.13

M2 log-odds projection:
R² = +0.4051

Trajectory density:
Original coverage = 28.67%
Calibrated C2 coverage = 100.0%
```

---

## 2. Thresholds Inherited by Observation Study

| Metric | Historical Real Laya | Replacement Study Target | Preregistered Hard Gate |
|:---|:---:|:---:|:---:|
| **Calibration ECE** | **0.2232** | $\le 0.10$ | $\le 0.15$ |
| **Brier Score** | **0.0842** | Lower than baseline ($< 0.0842$) | $\le 0.12$ |
| **Latent Alignment $R^2$** | **+0.4051** (M2) | $\ge 0.85$ | $\ge 0.70$ (Falsify: $< 0.70$) |
| **Belief Flapping** | **0.40%** | $\le 2.0\%$ | $\le 9.5\%$ |
| **Contradiction Recovery** | **1.0 turn** | $\le 1.0\text{ turn}$ | $\le 1.0\text{ turn}$ |
| **Neural CPU Latency (P50)** | **607.67 ms** | $\le 50.0\text{ ms}$ | $\le 100.0\text{ ms}$ |
| **Total Pipeline Latency (P50)** | **607.83 ms** | $\le 60.0\text{ ms}$ | $\le 120.0\text{ ms}$ |
| **Parameter Footprint** | **421.4M** | $\le 40\text{M}$ | $\le 100\text{M}$ |
| **Host RAM Usage** | **~1.6 GB** | $\le 250\text{ MB}$ | $\le 500\text{ MB}$ |
| **GPU VRAM Impact** | **0 MB** (CPU) | $0\text{ MB}$ | $0\text{ MB}$ |
| **Downstream Interface Shape** | **$\boldsymbol{\psi}_{\text{user}} \in \mathbb{R}^{12}$** | $\mathbb{R}^{12}$ (Invariant) | $\mathbb{R}^{12}$ (Invariant) |
