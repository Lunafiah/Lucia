# PHASE 22 OBSERVATION LAYER REPLACEMENT STUDY: COMPARISON MATRIX

> **Evaluation Cycle:** Phase 22 Observation Layer Replacement Study  
> **Environment:** `SimUserEnvV2Observation` (EN, VI, JA across 6 Stress Regimes)  
> **Hardware Constraint:** Single-Process CPU Execution, 0 MB GPU VRAM  
> **Governance:** Pre-Registered Thresholds Kept Frozen (No Post-Hoc Threshold Modification)  

---

## 1. Comprehensive Empirical Comparison Matrix

| Candidate Class | Parameter Count | CPU P50 Latency (ms) | Peak RAM (MB) | ECE | Latent $R^2$ Score | Latent MAE | Flapping Rate (%) | Contradiction Recovery (turns) | Trajectory $H=2$ Coverage | Multilingual Status | Overall Gate Status |
|:---|:---:|:---:|:---:|:---:|:---:|:---:|:---:|:---:|:---:|:---:|:---:|
| **Target Requirement** | $\le 40\text{M}$ | $\le 50.0\text{ ms}$ | $\le 500\text{ MB}$ | $\le 0.10$ | $\ge 0.85$ | $\le 0.20$ | $\le 2.0\%$ | $\le 1.0\text{ turn}$ | $\ge 90.0\%$ | Ratio $\ge 0.85$ | **TARGET** |
| **Preregistered Gate** | $\le 100\text{M}$ | $\le 100.0\text{ ms}$ | $\le 1000\text{ MB}$ | $\le 0.15$ | $\ge 0.70$ | $\le 0.30$ | $\le 9.5\%$ | $\le 1.0\text{ turn}$ | $\ge 90.0\%$ | Ratio $\ge 0.75$ | **HARD GATE** |
| **Historical Real Laya** | **421.4M** | **607.67 ms** | **~1,600 MB** | **0.2232** | **+0.4051** | — | **0.40%** | **1.0 turn** | **100.0%** | — | **FAILED REQUIREMENTS** |
| **C1: MiniLM Sentence Enc** | 22.7M | **22.67 ms** | **180 MB** | 0.2517 | -0.9706 | 0.1872 | 59.11% | 1.17 turns | **100.0%** | FAIL | **FAIL** |
| **C2: Distilled ModernBERT**| 28.4M | **28.70 ms** | **220 MB** | 0.2171 | -0.5750 | 0.1568 | 41.67% | 3.03 turns | **100.0%** | FAIL | **FAIL** |
| **C3: Audio Prosodic DSP** | **0.125M** | **3.82 ms** | **45 MB** | **0.0783** | -3.6096 | 0.2943 | 64.65% | 5.00 turns | **100.0%** | Invariant | **FAIL** |
| **C4: Hybrid Multimodal** | 22.8M | **27.09 ms** | **250 MB** | **0.1448** | -0.7606 | 0.1869 | 67.48% | 2.63 turns | **100.0%** | FAIL | **FAIL** |
| **C5: Structured Semantic** | 18.2M | **20.14 ms** | **250 MB** | 0.8122 | -2.2530 | 0.2520 | 19.07% | 5.00 turns | **100.0%** | FAIL | **FAIL** |
| **C6: Decoupled Projector** | 28.4M | **28.70 ms** | **220 MB** | 0.2171 | -0.5750 | 0.1568 | 67.65% | 3.10 turns | **100.0%** | FAIL | **FAIL** |

---

## 2. Gate Verification Ledger Across 8 Preregistered Gates

| Gate ID | Evaluation Metric | Threshold | C1 | C2 | C3 | C4 | C5 | C6 |
|:---|:---|:---:|:---:|:---:|:---:|:---:|:---:|:---:|
| `G_OBS1_CALIB_ECE` | Expected Calibration Error | $\le 0.15$ | FAIL | FAIL | **PASS** | **PASS** | FAIL | FAIL |
| `G_OBS1_CALIB_BRIER` | Brier Score | $< 0.0842$ | FAIL | FAIL | FAIL | FAIL | FAIL | FAIL |
| `G_OBS2_ALIGN_R2` | Continuous Latent $R^2$ | $\ge 0.70$ | **FALSIFIED** | **FALSIFIED** | **FALSIFIED** | **FALSIFIED** | **FALSIFIED** | **FALSIFIED** |
| `G_OBS3_STAB_FLAPPING` | Belief Flapping Rate | $\le 9.5\%$ | FAIL | FAIL | FAIL | FAIL | FAIL | FAIL |
| `G_OBS3_STAB_RECOVERY` | Contradiction Recovery | $\le 1.0\text{ turn}$ | FAIL | FAIL | FAIL | FAIL | FAIL | FAIL |
| `G_OBS4_TRAJ_COVERAGE` | Trajectory Coverage ($H=2$) | $\ge 90.0\%$ | **PASS** | **PASS** | **PASS** | **PASS** | **PASS** | **PASS** |
| `G_OBS5_LATENCY_CPU_P50` | Neural CPU Latency | $\le 100.0\text{ ms}$ | **PASS** | **PASS** | **PASS** | **PASS** | **PASS** | **PASS** |
| `G_OBS6_RES_RAM` | Peak RAM Usage | $\le 1000\text{ MB}$ | **PASS** | **PASS** | **PASS** | **PASS** | **PASS** | **PASS** |
| `G_OBS7_MULTILINGUAL` | Cross-Language Transfer | $\ge 0.75$ | FAIL | FAIL | FAIL | FAIL | FAIL | FAIL |
| `G_OBS8_INTERFACE` | $\boldsymbol{\psi}_{\text{user}} \in \mathbb{R}^{12}$ Integrity | 12D Finite Bounded | **PASS** | **PASS** | **PASS** | **PASS** | **PASS** | **PASS** |
| **OVERALL STATUS** | **All 10 Gates Satisfied** | **Concurrently** | **FAIL** | **FAIL** | **FAIL** | **FAIL** | **FAIL** | **FAIL** |

---

## 3. Core Architectural Conclusions

1. **Zero Production Promotion Authorized:** No candidate passed all preregistered acceptance gates.
2. **Definitive Separation of Compute from Alignment:** Edge CPU latency ($\le 29\text{ ms}$) and calibration ($ECE \le 0.10$ in C3) are solved, but continuous latent alignment remains unresolved.
