# Comparison Matrix — Phase 22-XR-L Configurations (B0 - B5)

| Config | Laya Backbone | Alignment Model | Continuous Filter | Tracking $R^2$ | Flapping Rate | Execution Status |
|---|---|---|---|---|---|---|
| **B0** | Real Laya | None | No | N/A | N/A | `BLOCKED_OFFLINE_WEIGHTS` |
| **B1** | Real Laya | Naive ($2p - 1$) | No | -1.58 | N/A | Coordinate Mismatch |
| **B2** | Real Laya | Linear (A1) | No | 0.55 | N/A | Aligned (Linear) |
| **B3** | Real Laya | Nonlinear (A2) | No | 0.43 | N/A | Aligned (Nonlinear) |
| **B4** | Real Laya | Linear (A1) | Yes | 0.55 | 4.0% | Continuous Dynamic |
| **B5** | Real Laya | Nonlinear (A2) | Yes | 0.43 | 3.0% | Continuous Dynamic |
