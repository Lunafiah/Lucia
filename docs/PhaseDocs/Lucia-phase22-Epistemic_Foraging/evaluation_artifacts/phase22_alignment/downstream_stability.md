# Downstream Stability Evaluation — Phase 22-AL

## 1. Overview & Downstream Metrics

Even though candidates failed the direct continuous latent alignment gate ($R^2 < 0.70$), this experiment investigates whether aligned observations preserve the downstream dynamical properties established in Phase 22-XR:
1. **Flapping Rate:** Frequency of oscillatory sign changes in latent acceleration ($\le 5.0\%$).
2. **Contradiction Recovery:** Number of turns required to re-converge after an abrupt emotional contradiction ($\le 2.0$ turns).
3. **Trajectory Forecasting Coverage ($H=1, H=2$):** Empirical coverage of downstream trajectory forecast cones ($\ge 90.0\%$).

---

## 2. Empirical Results (Held-Out Seeds 1024, 2026)

Evaluated under aligned state formation ($A_5$ Leaky State Estimator):

| Candidate | Mean Flapping Rate | Contradiction Recovery | Horizon $H=1$ Coverage | Horizon $H=2$ Coverage | Stability Verdict |
| :--- | :---: | :---: | :---: | :---: | :---: |
| **C2** (DistilBERT Logits) | 3.75% | 1.33 turns | 100.0% | 100.0% | **PASS** |
| **C4** (Hybrid Multimodal) | **0.80%** | **1.42 turns** | **100.0%** | **100.0%** | **PASS** |

---

## 3. Analysis & Key Insights

1. **Downstream Stability is Fully Preserved:**
   - **Flapping Rate:** Candidate C4 achieves a flapping rate of **0.80%**, easily satisfying the $\le 5.0\%$ gate (and approaching the canonical Phase 22-XR benchmark of 0.40%). Candidate C2 achieves 3.75%.
   - **Contradiction Recovery:** Both candidates re-converge in under 1.5 turns (C2: 1.33 turns; C4: 1.42 turns), satisfying the $\le 2.0$ turn gate.
   - **Forecast Coverage:** Both $H=1$ and $H=2$ empirical coverage remain at **100.0%**, satisfying the $\ge 90.0\%$ gate.

2. **Decoupling of Stability from Absolute Coordinate Alignment:**
   - A vital theoretical insight emerges: **Continuous dynamical stability does NOT require high-fidelity coordinate alignment ($R^2 \ge 0.85$).**
   - Even when observations provide weak or noisy coordinate alignment ($R^2 \approx 0.25$), the continuous integration mechanics of the Coupled MT-LNN and Ornstein-Uhlenbeck drift filter out high-frequency noise, preventing flapping and maintaining trajectory calibration.
   - However, because coordinate alignment remains low, the inferred latent coordinates are smoothed approximations rather than true representations of fine-grained user state.
