# PHASE 22-OLR: OBSERVATION LAYER CANDIDATE COMPARISON MATRIX

> **Evaluation Phase:** Phase 22-OLR (Observation Layer Replacement Study)  
> **Environment:** `SimUserEnvOLR` (Multilingual: English, Vietnamese, Japanese)  
> **Evaluation Seeds:** 42, 137, 618, 1024, 2026 (1,800 turns per candidate, 10,800 total evaluations)  
> **Hardware Constraint:** CPU-Only Edge Execution, 0 MB GPU VRAM  
> **Governance:** Pre-Registered Thresholds from `OBSERVATION_LAYER_REQUIREMENTS.md`  

---

## 1. Primary Empirical Evidence Matrix

All candidate observation models were evaluated under identical continuous Bucy-Kalman user-state dynamics in $\mathbb{R}^6$.

| Architecture / Model | ECE | Brier | Latent $R^2$ | Latent MAE | Flapping Rate | Contradiction Recovery | CPU P50 Latency | Peak RAM | Multilingual Robustness | Overall Status |
|:---|:---:|:---:|:---:|:---:|:---:|:---:|:---:|:---:|:---:|:---:|
| **Target Requirement** | $\le 0.10$ | $\le 0.08$ | $\ge 0.85$ | $\le 0.20$ | $\le 2.0\%$ | $\le 1.0\text{ turn}$ | $\le 50.0\text{ ms}$ | $\le 500\text{ MB}$ | Ratio $\ge 0.85$ | **GATE TARGET** |
| **Acceptance Threshold**| $\le 0.15$ | $\le 0.12$ | $\ge 0.70$ | $\le 0.30$ | $\le 9.5\%$ | $\le 1.0\text{ turn}$ | $\le 100.0\text{ ms}$ | $\le 1000\text{ MB}$ | Ratio $\ge 0.75$ | **HARD GATE** |
| **Historical Real Laya** | **0.2232** | **0.0842** | **+0.4051** (M2) | — | **0.40%** | **1.0 turn** | **607.67 ms** | **~1600 MB** | — | **FAILED REQUIREMENTS** |
| **C1: MiniLM Sentence Enc** | 0.2367 | 1.4918 | -0.8507 | 0.1827 | 62.99% | 1.07 turns | **23.23 ms** | 180 MB | EN: -0.85, VI: -0.88, JA: -0.83 | **FAIL** |
| **C2: Distilled Semantic** | 0.2047 | 1.6548 | -0.5161 | 0.1535 | 40.58% | 3.30 turns | **29.28 ms** | 220 MB | EN: -0.53, VI: -0.53, JA: -0.49 | **FAIL** |
| **C3: Audio Prosodic DSP** | **0.0500** | 1.8941 | -3.4698 | 0.2918 | 66.75% | 5.00 turns | **3.82 ms** | 45 MB | EN: -3.47, VI: -3.47, JA: -3.47 | **FAIL** |
| **C4: Hybrid Multimodal** | **0.1284** | 1.6954 | -0.7523 | 0.1884 | 68.35% | 2.63 turns | **27.74 ms** | 250 MB | EN: -0.75, VI: -0.76, JA: -0.74 | **FAIL** |
| **C5: Structured Slots** | 0.8094 | 1.5464 | -2.2710 | 0.2520 | 19.07% | 5.00 turns | **20.72 ms** | 250 MB | EN: -2.15, VI: -2.31, JA: -2.36 | **FAIL** |
| **C6: Decoupled Projector** | 0.2047 | 1.6548 | -0.5161 | 0.1535 | 69.19% | 3.23 turns | **29.29 ms** | 220 MB | EN: -0.53, VI: -0.53, JA: -0.49 | **FAIL** |

---

## 2. Disentangled Latency Analysis (Separated Components)

As mandated by governance, observation encoder latency is strictly separated from calibration/projection and continuous belief filtering latency.

| Candidate | Observation Encoder P50 (ms) | Calibration / Projection P50 (ms) | Continuous Filter P50 (ms) | Total Pipeline P50 (ms) | CPU Target Compliance |
|:---|:---:|:---:|:---:|:---:|:---:|
| **Real Laya Baseline** | 607.67 | 0.00 | 0.16 | 607.83 | **VIOLATED (>10x target)** |
| **C1: MiniLM Bi-Encoder** | 23.23 | 0.088 | 0.174 | 23.52 | **PASS (25.8x faster than Laya)** |
| **C2: Distilled ModernBERT**| 29.28 | 0.056 | 0.166 | 29.51 | **PASS (20.6x faster than Laya)** |
| **C3: Audio Prosody DSP** | 3.82 | 0.008 | 0.111 | 3.94 | **PASS (154x faster than Laya)** |
| **C4: Hybrid Multimodal** | 27.74 | 0.006 | 0.164 | 27.92 | **PASS (21.8x faster than Laya)** |
| **C5: Structured Semantic** | 20.72 | 0.016 | 0.164 | 20.92 | **PASS (29.1x faster than Laya)** |
| **C6: Decoupled Projector** | 29.29 | 0.090 | 0.145 | 29.54 | **PASS (20.6x faster than Laya)** |

*Key Latency Takeaway:* Every single candidate class (C1–C6) overwhelmingly satisfied the CPU P50 latency target ($\le 50.0\text{ ms}$) and total pipeline budget ($\le 60.0\text{ ms}$), demonstrating that edge conversational speeds are easily achievable with compact architectures.

---

## 3. Disentangled Calibration & Alignment Analysis

While latency targets were solved across all candidate classes, calibration and continuous latent alignment revealed stark architectural divergences:

1. **Acoustic Calibration Success (C3 & C4):**
   - **Candidate C3 (Audio Prosody DSP)** achieved exceptional calibration ($ECE = 0.0500 \le 0.10$), easily passing the gate.
   - **Candidate C4 (Hybrid Multimodal)** achieved $ECE = 0.1284$, passing the $0.15$ threshold.
   - Text-only encoders (C1, C2, C5) suffered from overconfidence skew on conversational turns without explicit temperature fine-tuning.
2. **The Persistent Continuous Latent Alignment Barrier (All Candidates):**
   - No zero-shot candidate achieved a positive $R^2$ against the 6D continuous ground truth state $\mathbf{z}^* \in \mathbb{R}^6$.
   - **C2/C6 achieved the highest raw alignment** ($MAE = 0.1535$, $MSE = 0.0461$, $R^2 = -0.5161$). While MAE meets the acceptance threshold ($\le 0.30$), non-linear variance explanation remains below the $R^2 \ge 0.70$ admission gate.
   - C3 (Audio-only) suffered severe coordinate blindness on factual/topic dimensions ($R^2 = -3.4698$), demonstrating that audio alone cannot track cognitive user intent.
   - C5 (Structured slots) suffered severe quantization error ($R^2 = -2.2710$, $ECE = 0.8094$) due to discrete slot boundaries.

---

## 4. Multi-Step Predictive Trajectory Forecasting

Propagating multi-step trajectory densities via Lyapunov-matched diffusion retained high empirical coverage across all candidates:

| Candidate | Horizon $H=1$ Coverage | Horizon $H=2$ Coverage | Mahalanobis Ellipsoid Bounded |
|:---|:---:|:---:|:---:|
| **Real Laya (Original)** | 28.67% | 28.67% | Under-dispersed |
| **Real Laya (Calibrated C2)**| 100.0% | 100.0% | Calibrated diffusion |
| **C1** | 95.56% | 100.0% | **PASS** |
| **C2** | 95.56% | 100.0% | **PASS** |
| **C3** | 90.00% | 100.0% | **PASS** |
| **C4** | 94.44% | 100.0% | **PASS** |
| **C5** | 91.11% | 100.0% | **PASS** |
| **C6** | 93.33% | 100.0% | **PASS** |

The continuous trajectory forecaster is robustly model-agnostic: even when observation inputs have lower alignment, the Lyapunov diffusion matches empirical spread at $H=2$ with $100\%$ containment.
