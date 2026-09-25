# Latency and Computational Budget Report — Phase 22-AL

## 1. Objective & Hardware Constraints

Lucia operates under strict local consumer edge execution invariants:
- **Execution Target:** 100% CPU-native edge execution.
- **VRAM Budget:** 0 MB GPU allocation for observation alignment (preserving VRAM for LLM inference).
- **Latency SLA:** Sub-millisecond execution ($\le 1.0\text{ ms}$ P50, $\le 5.0\text{ ms}$ P95).
- **Parameter Footprint:** Minimal memory footprint ($\le 100\text{k}$ parameters).

---

## 2. Empirical Benchmark Measurements (Intel/AMD x86_64 CPU)

Benchmarked over 1,000 forward passes per model:

| Alignment Model Code | Model Description | Parameter Count | CPU P50 Latency | CPU P95 Latency | Memory Footprint (RAM) | SLA Budget Verdict |
| :--- | :--- | :---: | :---: | :---: | :---: | :---: |
| **A1_Linear** | Linear Ridge Projection ($W e_t + b$) | 42 | **0.0031 ms** | **0.0031 ms** | < 0.1 MB | **PASS** |
| **A2_Constrained** | Bounded Nonlinear Projection ($\tanh$) | 42 | 0.0122 ms | 0.0305 ms | < 0.1 MB | **PASS** |
| **A3_SmallMLP** | 2-Layer MLP (32 units, ReLU) | 422 | 0.0240 ms | 0.0383 ms | < 0.1 MB | **PASS** |
| **A4_Temporal_k3** | Multi-frame Linear Window ($k=3$) | 114 | 0.0187 ms | 0.0190 ms | < 0.1 MB | **PASS** |
| **A5_Leaky** | Leaky State Estimator ($\alpha=0.35$) | 43 | **0.0031 ms** | **0.0032 ms** | < 0.1 MB | **PASS** |
| **A6_ObsLikelihood** | Empirical Bayesian Likelihood Inversion | 42 | 0.0446 ms | 0.0529 ms | < 0.1 MB | **PASS** |
| **A7_Hybrid** | Windowed Bounded MLP + Leaky Filter | 808 | 0.0239 ms | 0.0266 ms | < 0.1 MB | **PASS** |

---

## 3. Findings & Efficiency Verification

1. **Near-Zero Latency Overhead:**
   - Every evaluated alignment architecture (A1–A7) executes in well under **0.05 ms** on standard CPU hardware.
   - The best-performing model ($A_5$ Leaky State Estimator) requires only **0.0031 ms** (3.1 microseconds), which is essentially zero computational overhead relative to the conversational turn cycle.
   - Even the most computationally involved model ($A_6$ with empirical covariance matrix inversion) completes in **0.0446 ms**, satisfying the sub-millisecond SLA by an order of magnitude.

2. **Parameter Discipline:**
   - Maximum parameter count across all models is 808 parameters ($A_7$), and only 43 parameters for the optimal $A_5$ estimator.
   - Zero GPU VRAM is utilized.

3. **Gate Status:**
   - **G_AL5 (Alignment Latency Gate): PASS** (All models $< 1.0\text{ ms}$).
