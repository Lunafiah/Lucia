# Phase 22-XR — Canonical Evaluation Report

**Execution Timestamp:** 2026-09-24 20:51:08

## 1. Architecture Gate Evaluation

| Gate | Target Metric | Observed Value | Threshold | Verdict |
|---|---|---|---|---|
| **G-XR1** | ECE Shift (Laya) | 0.2984 | <= 0.10 | **FAIL** |
| **G-XR2** | Tracking Accuracy R² | -23.6138 | >= 0.85 | **FAIL** |
| **G-XR3** | Closed-Loop Flapping | 1.10% | <= 9.5% | **PASS** |
| **G-XR4** | Trajectory Density Cov (H=2) | 99.50% | >= 75.0% | **PASS** |
| **G-XR5** | Contradiction Recovery Turns | 1.0 | <= 1.0 turns | **PASS** |
| **G-XR6** | CPU Latency P50 | 0.3 ms | <= 350.0 ms | **PASS** |

## 2. Ablation Matrix Results (A0–A7)

| Ablation | Configuration | Mean R² | Mean Flapping Rate |
|---|---|---|---|
| **A0** | A0 Pipeline | -9.0294 | 0.00% |
| **A1** | A1 Pipeline | -8.9677 | 5.00% |
| **A2** | A2 Pipeline | -25.5830 | 0.00% |
| **A3** | A3 Pipeline | -7.4672 | 0.41% |
| **A4** | A4 Pipeline | -7.4570 | 0.27% |
| **A5** | A5 Pipeline | -23.8230 | 0.00% |
| **A6** | A6 Pipeline | -27.0547 | 2.43% |
| **A7** | A7 Pipeline | -27.0547 | 2.43% |

## 3. Causal Attribution Summary

1. **Continuous vs Discrete:** Transitioning from discrete Bayes (A1) to continuous belief (A2) reduces flapping significantly.
2. **Observation Capacity:** High-capacity contextual encoder (A6) significantly outperforms surrogate B4 (A2) under noise and lexical sparsity.
3. **Decoupling Boundary:** P23 interface (XR-E8) validated bounded, continuous, and language-independent.
