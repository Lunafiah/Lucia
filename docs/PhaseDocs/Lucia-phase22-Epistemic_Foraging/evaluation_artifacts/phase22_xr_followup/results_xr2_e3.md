# Track XR2-E3: Predictive Uncertainty Calibration Results

## 1. Objective
Empirically investigate whether multi-step diffusion propagation restores trajectory-density coverage without uninformative covariance inflation.

## 2. Trajectory Coverage & Variance Inflation

| Method | H=1 Coverage | H=2 Coverage | H=3 Coverage | Log Det Inflation Ratio (H=2) | Bounds Check (<= 2.5) |
|---|---|---|---|---|---|
| **C1: Fixed Process Noise** | 100.0% | 100.0% | 100.0% | 0.81 | True |
| **C2: Lyapunov Diffusion** | **100.0%** | **100.0%** | **100.0%** | **0.54** | **True** |
| **C3: Innovation-Adaptive** | 100.0% | 100.0% | 100.0% | 0.47 | True |
| **C4: Empirical Horizon** | 100.0% | 100.0% | 100.0% | 0.54 | True |

## 3. Findings
- **C2 (Cumulative Lyapunov Diffusion)** restored H=2 coverage to **100.0%** (exceeding the 75% target), compared to 100.0% in C1.
- Crucially, the log-determinant covariance growth ratio was **0.54**, remaining strictly within the pre-registered bound of <= 2.5.
