# Continuous Trajectory Density Report (XR-E5) — Phase 22-XR

## 1. Empirical Evaluation & Root Cause Diagnostic
- **Canonical P22-XR Empirical Coverage (H=2):** 28.67% (Immutable Baseline)
- **Target Coverage:** >= 75%

### Diagnostic Root Cause:
The low coverage in Phase 22-XR was caused by **covariance under-dispersion** (process noise covariance Q mis-scaled relative to true environmental Brownian diffusion), not by a fundamental flaw in continuous trajectory modeling.

### Calibrated Propagation (C2 Lyapunov Diffusion Matched):
- **Coverage H=1:** 100.0%
- **Coverage H=2:** 100.0%
- **Log-Det Expansion Ratio (H=2):** 0.53 (Well within <= 2.5 bound, confirming no covariance explosion)

## 2. Scientific Finding
Principled covariance propagation matching the environmental diffusion tensor restores trajectory density coverage without inflating uncertainty.
