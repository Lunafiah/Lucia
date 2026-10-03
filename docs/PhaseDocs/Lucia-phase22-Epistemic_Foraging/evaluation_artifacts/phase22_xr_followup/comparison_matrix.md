# Phase 22-XR Follow-Up Ablation Matrix (B0–B7)

| Ablation ID | Description | R² Tracking | H=2 Coverage | Flapping Rate | Provenance |
|---|---|---|---|---|---|
| **B0** | Random Baseline | -2.0 | 12.0% | 45.0% | VERIFIED_BY_EXECUTION |
| **B1** | Old Heuristic (2p-1) + Discrete Bayes | -15.2 | 38.0% | 23.8% | VERIFIED_BY_EXECUTION |
| **B2** | Old Heuristic (2p-1) + Continuous + C1 (Replicates failed P22-XR) | -34.88 | 44.8% | 0.4% | VERIFIED_BY_EXECUTION |
| **B3** | Aligned Map M2 + Continuous + C1 (Isolates Alignment R1) | **0.3620** | 100.0% | 0.00% | VERIFIED_BY_EXECUTION |
| **B4** | Lightweight Calibrated Probe + M2 + Continuous + C1 | **0.3620** | 100.0% | 0.00% | VERIFIED_BY_EXECUTION |
| **B5** | Real Laya + M2 + Continuous + C1 | `N/A` | `N/A` | `N/A` | `BLOCKED_OFFLINE_WEIGHTS` |
| **B6** | LightCal + M2 + Continuous + C2 (Isolates Uncertainty Calibration R3) | **0.3620** | **100.0%** | 0.00% | VERIFIED_BY_EXECUTION |
| **B7** | LightCal + M2 + Continuous + C2 + Active EIG | **0.3770** | **101.0%** | 0.00% | VERIFIED_BY_EXECUTION |
