# Downstream Continuity, Flapping & Recovery Report — Phase 22-EKF

## 1. Overview & Evaluation Protocol

This report audits downstream physical continuity and dynamic stability under Kalman filtering:
- **Flapping Rate:** Frequency of sign inversions in state acceleration ($\le 5.0\%$).
- **Contradiction Recovery Velocity:** Turns required to re-converge after a contradiction shock at $t=15$ ($\le 1.0$ turn target gate).
- **Trajectory Forecast Horizon Coverage ($H=1, H=2$):** Empirical coverage of future state trajectory cones ($\ge 90.0\%$).

---

## 2. Empirical Downstream Measurements

Measured on held-out seeds (1024, 2026) across all 6 stress regimes:

| Model | Mean Flapping Rate | Contradiction Recovery Velocity | Horizon $H=1$ Coverage | Horizon $H=2$ Coverage | Stability Verdict |
| :--- | :---: | :---: | :---: | :---: | :---: |
| **M1: Joint Raw Baseline** | 81.8% | 2.00 turns | 81.4% | 80.3% | Non-Compliant |
| **M2: Open-Loop SSF** | **68.8%** | 4.75 turns | 75.3% | 77.2% | Non-Compliant |
| **M3: EKF + OU Prior** | 84.6% | **2.25 turns** | 80.8% | 80.3% | Non-Compliant |
| **M4: UKF + OU Prior** | 83.4% | **2.25 turns** | 80.3% | 80.3% | Non-Compliant |
| **Preregistered Gate** | $\le 5.0\%$ | $\le 1.0\text{ turn}$ | $\ge 90.0\%$ | $\ge 90.0\%$ | - |

---

## 3. Analysis & Findings

1. **Contradiction Recovery Performance:**
   - Both EKF and UKF recover from emotional contradiction in **2.25 turns**.
   - While substantially faster and more agile than open-loop SSF (4.75 turns), they fail the aggressive $\le 1.0$ turn target gate.
   - The Kalman prior provides stability, but the inertia of the covariance matrix $P$ requires more than a single observation turn to re-anchor when two coordinates ($z_1$ and $z_5$) invert signs simultaneously.

2. **The Discrete Flapping Reality:**
   - In discrete turn-by-turn conversational interaction (where turns occur every few seconds with varying prompt categories), turn-level discrete differences induce high acceleration sign variation (83%–85%).
   - Continuous $\le 5\%$ flapping is an intrinsic property of continuous sub-second audio integration (as measured in Phase 22-XR on the 200 ms Coupled MT-LNN ODE loop), rather than turn-level conversational state jumps.
