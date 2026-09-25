# OBS-E5: LATENCY & EXECUTION BUDGET REPORT

> **Track Identifier:** OBS-E5  
> **Source Data:** `raw_measurements.json`  
> **Preregistered Gate:** Observation CPU P50 $\le 50.0\text{ ms}$, Total Pipeline P50 $\le 60.0\text{ ms}$  

---

## 1. Disentangled Latency Percentiles (Measured on Reference CPU)

As mandated by Section 6 of `AGENTS.md`, observation inference latency, calibration/projection latency, and downstream continuous-filter latency are strictly disentangled and reported separately:

| Candidate ID | Observation Encoder P50 (ms) | Observation Encoder P95 (ms) | Projection Layer P50 (ms) | Continuous Filter P50 (ms) | Total Pipeline P50 (ms) | Total Pipeline P95 (ms) | CPU Target Gate Status |
|:---|:---:|:---:|:---:|:---:|:---:|:---:|:---:|
| **Real Laya Baseline** | **607.67** | **851.68** | 0.00 | **0.16** | **607.83** | **851.84** | **VIOLATED (>10x)** |
| **C1 (MiniLM)** | 22.67 | 26.18 | 0.059 | 0.125 | 22.85 | 26.38 | **PASS (26.6x speedup)** |
| **C2 (Distilled)** | 28.70 | 33.99 | 0.047 | 0.118 | 28.88 | 34.17 | **PASS (21.0x speedup)** |
| **C3 (Audio DSP)** | 3.82 | 4.92 | 0.008 | 0.088 | 3.92 | 5.03 | **PASS (155x speedup)** |
| **C4 (Hybrid)** | 27.09 | 31.06 | 0.006 | 0.120 | 27.27 | 31.22 | **PASS (22.3x speedup)** |
| **C5 (Structured)** | 20.14 | 24.08 | 0.016 | 0.126 | 20.33 | 24.31 | **PASS (29.9x speedup)** |
| **C6 (Decoupled)** | 28.70 | 34.00 | 0.080 | 0.115 | 28.96 | 34.20 | **PASS (21.0x speedup)** |

---

## 2. Findings & Operational Budget Compliance

1. **Definitive Solution of the Compute Bottleneck:**
   All candidate classes (C1 through C6) overwhelmingly cleared the $\le 50.0\text{ ms}$ CPU P50 target, achieving end-to-end latencies between $3.92\text{ ms}$ and $28.96\text{ ms}$.
2. **Negligible Continuous Filter Overhead:**
   Across all candidates, the continuous Bucy-Kalman filter update required only $0.088\text{ ms} - 0.126\text{ ms}$ (less than $130\,\mu\text{s}$), confirming that downstream dynamics impose essentially zero conversational latency.
