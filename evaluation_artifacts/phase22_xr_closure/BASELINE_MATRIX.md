# BASELINE COMPARISON MATRIX: REAL LAYA AS REFERENCE BENCHMARK

> **Document Type:** Reference Benchmark Ledger  
> **Status:** PERMANENT HISTORICAL BASELINE  
> **Reference Model:** `convaiinnovations/laya` (ModernBERT-large, 421M parameters)  
> **Execution Mode:** 100% Local CPU Forward Pass (No Emulation, No GPU)  

---

## 1. Architectural Baseline Role

In the upcoming **Observation Layer Replacement Study**, the Real Laya neural model serves as the **immutable empirical reference baseline**. 

It is neither discarded nor erased. Its measured characteristics define the exact quantitative boundaries that any prospective replacement architecture must overcome to justify adoption.

---

## 2. Canonical Real Laya Baseline Metrics

All values below reflect genuine CPU forward execution on reference hardware running the cryptographically verified checkpoint (`SHA-256: 891102d372688fc2a094dac56a384bc537b87c63f21f9f3dac0be2b7cbc8d86c`).

```text
Real Laya:
Model: convaiinnovations/laya
Architecture: ModernBERT-large
Parameters: 421,438,464

ECE: 0.2232
Brier: 0.0842

Neural CPU P50: 607.67 ms
Total CPU P50: 607.83 ms

Continuous flapping: 0.40%
Contradiction recovery: 1.0 turn

M0 R²: -25.13
M2 R²: +0.4051
M4 R²: +0.4049

Original trajectory coverage H=2:
28.67%

Calibrated C2 coverage:
100.0%
```

---

## 3. Detailed Baseline Comparison Table

This matrix establishes the benchmark target for evaluating Candidate Classes C1 through C6:

| Evaluation Dimension | Metric | Real Laya Baseline (Reference) | Replacement Study Target | Baseline Compliance | Rationale for Target |
|:---|:---|:---:|:---:|:---:|:---|
| **Calibration** | Expected Calibration Error ($ECE$) | **0.2232** | $\le 0.10$ | **VIOLATED** | Laya logits are overconfident; induces Kalman observation shock |
| | Brier Score | **0.0842** | $\le 0.08$ | **MARGINAL** | Acceptable variance, but calibration error remains high |
| | Mean Confidence | **0.7768** | $\sim 0.60 - 0.70$ | High Skew | Zero-shot confidence distribution is heavily skewed toward extremes |
| **Latency (CPU)** | Neural Inference ($P50$) | **607.67 ms** | $\le 50.0\text{ ms}$ | **VIOLATED** | Consumes $>75\%$ of Lucia's total turn latency budget |
| | Neural Inference ($P95$) | **851.68 ms** | $\le 100.0\text{ ms}$ | **VIOLATED** | Tail latency introduces noticeable conversational stutter |
| | Neural Inference ($P99$) | **899.56 ms** | $\le 150.0\text{ ms}$ | **VIOLATED** | Extreme outlier spikes under background thread contention |
| | Continuous Filter ($P50$) | **0.16 ms** | $\le 1.0\text{ ms}$ | **SATISFIED** | Filter arithmetic is essentially instantaneous |
| | Total Pipeline ($P50$) | **607.83 ms** | $\le 60.0\text{ ms}$ | **VIOLATED** | Dominated entirely by the heavy neural backbone |
| **Alignment** | M0: Naive Linear ($R^2$) | **-25.13** | $\ge 0.70$ | **VIOLATED** | Direct simplex mapping suffers severe coordinate mismatch |
| | M2: Log-Odds ($R^2$) | **+0.4051** | $\ge 0.85$ | **PARTIAL** | Log-odds restores positive correlation, but misses $0.85$ gate |
| | M4: Synthetic Oracle ($R^2$) | **+0.4049** | $\ge 0.85$ | **PARTIAL** | Even oracle projection plateaued around $0.40$ on categorical probes |
| **Stability** | Continuous Flapping | **0.40%** | $\le 2.0\%$ | **SATISFIED** | Continuous filter successfully suppresses belief oscillation |
| | Contradiction Recovery | **1.0 turn** | $\le 1.0\text{ turn}$ | **SATISFIED** | Kalman gain adapts to sharp shifts in a single turn |
| **Trajectory** | Baseline $H=2$ Coverage | **28.67%** | $\ge 90.0\%$ | **VIOLATED** | Uncalibrated baseline severely under-forecasts trajectory spread |
| | Calibrated C2 Coverage | **100.0%** | $\ge 90.0\%$ | **SATISFIED** | Lyapunov-matched diffusion provides optimal coverage |
| | Covariance Inflation ($\log \det$) | **0.53** | $\le 1.0$ | **SATISFIED** | Uncertainty remains informative without explosive collapse |
| **Resources** | Parameter Count | **421.4M** | $\le 60\text{M}$ | **HEAVY** | Overkill for a perceptual evidence extraction frontend |
| | RAM Footprint | **$\sim 1.6\text{ GB}$** | $\le 400\text{ MB}$ | **HIGH** | Exceeds edge memory allocation target |
| | GPU Requirement | **CPU capable** | $0\text{ MB}$ (CPU native) | **SATISFIED** | Successfully runs on CPU, but with prohibitive latency |

---

## 4. Key Takeaways for Replacement Candidates

1. **The Core Defect is Compute & Calibration, Not the Filter:**
   The continuous belief filter and trajectory forecaster are sound (flapping $0.40\%$, recovery $1.0\text{ turn}$, coverage $100\%$). The defect is strictly in the observation frontend (421M params, $607\text{ ms}$ latency, $ECE = 0.2232$).
2. **Replacement Objective:**
   A successful replacement candidate must preserve the high stability of the continuous filter while achieving a **$10\times$ latency reduction** ($< 60\text{ ms}$) and a **$2\times$ calibration improvement** ($ECE \le 0.10$).
