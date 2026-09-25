# Raw Measurements Summary — Phase 22-X

> **Data Source**: [`raw_measurements.json`](file:///c:/Users/Lunafiah/Desktop/My_project/Lucia/evaluation_artifacts/phase22_x/raw_measurements.json)  
> **Timestamp**: 2026-09-24 18:04:44  
> **Hardware Profile**: Intel CPU-Only, 0.0 MB GPU VRAM  

---

## 1. Experiment E1: Observation Calibration

### In-Distribution Test (N = 5,000)
| Model | ECE | Brier Score | NLL | Top-1 Accuracy | Latency (ms/sample) |
|---|---|---|---|---|---|
| **B0 (Prior)** | 0.0284 | 0.7760 | 1.5407 | 29.12% | 0.00014 |
| **B1 (Calibrated MLP)** | 0.2219 | 0.4611 | 2.7187 | 75.08% | 0.00043 |
| **B4 (Jev/Laya Surrogate)** | **0.0149** | **0.2789** | **0.4873** | **80.36%** | 0.00072 |

### Distribution Shift Regimes (N = 3,000 per regime)
| Regime | Metric | B1 (Calibrated MLP) | B4 (Jev/Laya Surrogate) |
|---|---|---|---|
| **DS-1 (Noise Surge)** | ECE / Brier / Acc | 0.4729 / 0.9597 / 50.50% | **0.3077** / **0.7932** / 46.97% |
| **DS-2 (Dynamics Shift)** | ECE / Brier / Acc | 0.2754 / 0.5690 / 69.60% | **0.0176** / **0.3051** / **77.80%** |
| **DS-3 (Contradiction)** | ECE / Brier / Acc | 0.2205 / 0.4575 / 75.23% | **0.0196** / **0.2882** / **79.87%** |
| **DS-4 (Sparse/Silent)** | ECE / Brier / Acc | 0.7672 / 1.5526 / 19.40% | **0.5994** / **1.3023** / **20.40%** |
| **DS-5 (Intent Shift)** | ECE / Brier / Acc | 0.2290 / 0.4732 / 74.60% | **0.0203** / **0.2840** / **79.57%** |

---

## 2. Experiment E2: Recursive Belief Filtering

| Baseline / Model | Posterior State Accuracy | Mean TV Distance | Recovery Time (turns) |
|---|---|---|---|
| **Moving Average (Naive)** | 63.86% | — | — |
| **B1 + Bayes Filter** | 71.28% | 0.2883 | — |
| **B4 + Bayes Filter** | **77.38%** | **0.2807** | **0.23** |
| **B3 (POMDP Tracker)** | 71.20% | — | — |

---

## 3. Experiment E3: Temporal Dynamics & Jitter

| Metric | Static Model (B1 Argmax) | Temporal Latent Model (B5) | Delta |
|---|---|---|---|
| **State Flip Rate (Jitter)** | 0.4223 | **0.3266** | **-22.66% reduction** |
| **Next-State 1-Step Accuracy** | 49.67% | **52.63%** | **+2.96% gain** |

---

## 4. Experiment E4: Prospective Intent Prediction

| Metric | Baseline (B0 Prior) | Predictive Intent Model | Target Threshold |
|---|---|---|---|
| **Top-1 Intent Accuracy** | 32.15% | **34.15%** | $\ge 70.0\%$ (FAIL) |
| **Top-2 Intent Recall** | — | **52.51%** | $\ge 90.0\%$ (FAIL) |
| **Intent ECE** | — | 0.0235 | $\le 0.080$ |
| **Intent Brier Score** | — | 0.7871 | — |

---

## 5. Experiment E5: Bounded Prediction Tree

| Metric | Bounded Tree ($H=3, B=3$) | MAP Single Path | Target Threshold |
|---|---|---|---|
| **Trajectory Coverage $H=1$** | 64.00% | — | — |
| **Trajectory Coverage $H=2$** | **30.00%** | 10.00% | $\ge 95.0\%$ (FAIL) |
| **Trajectory Coverage $H=3$** | **6.50%** | — | — |
| **Mean Execution Latency** | **362.8 $\mu\text{s}$** | — | $\le 2500\,\mu\text{s}$ (PASS) |
| **p95 Execution Latency** | **559.3 $\mu\text{s}$** | — | — |
| **Max Execution Latency** | **1854.5 $\mu\text{s}$** | — | $\le 5000\,\mu\text{s}$ (PASS) |
| **Mean Node Count** | 9.67 nodes | 1.0 node | $\le 27$ nodes (PASS) |

---

## 6. Experiment E6: Epistemic Action Selection

| Metric | Reactive Surprise Policy | EIG Active Policy | Target Threshold |
|---|---|---|---|
| **Clarification Query Ratio** | 0.23% | **4.60%** | $\le 25.0\%$ (PASS) |
| **Mean Entropy Drop** | 0.6706 nats | 0.4378 nats | $\ge 0.40$ nats (PASS) |
| **Excess Question Ratio** | 28.57% | 30.43% | — |

---

## 7. Experiment E7: Closed-Loop Multi-Turn Stability

| Metric | Value | Target Threshold |
|---|---|---|
| **Total Closed-Loop Episodes** | 500 | — |
| **Total Dialogue Turns** | 15,000 | — |
| **Deadlock Episodes** | **0 (0.00%)** | 0 episodes (PASS) |
| **Belief Flapping Episodes** | **119 (23.80%)** | $< 1.0\%$ (FAIL) |
| **Attractor Collapse Episodes** | **0 (0.00%)** | 0 episodes (PASS) |
| **Overall Stability Rate** | **76.20%** | $\ge 99.5\%$ (FAIL) |
