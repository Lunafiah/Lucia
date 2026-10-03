# Baseline Comparison Matrix — Phase 22-X

> **Comparative Evaluation**: Baselines B0 through B5  
> **Source**: Phase 22-X Experimental Evaluation  

---

## 1. Baseline Performance Matrix

| Metric / Dimension | B0 (Prior) | B1 (Calibrated MLP) | B2 (Bayes Filter) | B3 (POMDP Tracker) | B4 (Jev/Laya Surrogate) | B5 (Temporal Latent) |
|---|---|---|---|---|---|---|
| **In-Distribution ECE** | 0.0284 | 0.2219 | — | — | **0.0149** | — |
| **In-Distribution Acc** | 29.12% | 75.08% | — | — | **80.36%** | — |
| **DS-1 Noise ECE** | — | 0.4729 | — | — | **0.3077** | — |
| **DS-2 Shift ECE** | — | 0.2754 | — | — | **0.0176** | — |
| **DS-3 Contradiction ECE** | — | 0.2205 | — | — | **0.0196** | — |
| **State Tracking Acc** | 29.12% | 71.28% | 71.28% | 71.20% | **77.38%** | **77.38%** |
| **State Jitter Flip Rate** | 0.0000 | 0.4223 | 0.3540 | 0.3610 | — | **0.3266** |
| **Next-State Prediction** | 29.12% | 49.67% | — | — | — | **52.63%** |
| **CPU Latency / Turn** | $\le 0.1\mu\text{s}$ | $0.43\mu\text{s}$ | $1.2\mu\text{s}$ | $2.1\mu\text{s}$ | $0.72\mu\text{s}$ | $1.8\mu\text{s}$ |
| **Parameter Count** | 0 | 256 | 25 | 25 | 2,753 | 2,778 |

---

## 2. Mechanistic vs. Primitive Attribution

1. **Jev/Laya Surrogate (B4) Contribution**:
   - Outperformed B1 in calibration ($\text{ECE} = 0.0149$ vs $0.2219$) and state classification accuracy ($80.36\%$ vs $75.08\%$).
   - Robust to transition shifts (DS-2, DS-3, DS-5), but vulnerable to extreme noise (DS-1) and feature collapse (DS-4).
2. **Bayesian Filtering (B2) Contribution**:
   - Added $+13.52\%$ accuracy over naive moving-average tracking.
   - When combined with B4, reached $77.38\%$ tracking accuracy.
3. **Temporal Dynamics (B5) Contribution**:
   - Attenuated observation jitter by $22.66\%$, but provided modest 1-step prediction improvement ($+2.96\%$).
