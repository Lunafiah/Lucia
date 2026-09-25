# Temporal Continuity & Stability Report — Phase 22-SSF

## 1. Overview & Downstream Metrics

This experiment evaluates whether the Decoupled SSF architecture preserves the downstream continuous dynamical properties established in Phase 22-XR:
- **Flapping Rate:** Sign inversions in acceleration vectors ($\le 5.0\%$).
- **Contradiction Recovery Velocity:** Turns required to re-converge after an emotional contradiction shock at $t=15$ ($\le 2.0$ turns).
- **Trajectory Forecast Horizon Coverage ($H=1, H=2$):** Empirical coverage of future state trajectory cones ($\ge 90.0\%$).

---

## 2. Empirical Results (Held-Out Seeds 1024, 2026)

| Downstream Metric | Raw Baseline | Decoupled SSF | Preregistered Requirement | Gate Verdict |
| :--- | :---: | :---: | :---: | :---: |
| **Mean Flapping Rate** | 81.8% | **68.8%** | $\le 5.0\%$ | **FAIL** |
| **Contradiction Recovery Velocity** | **2.0 turns** | 4.75 turns | $\le 2.0$ turns | **FAIL** |
| **Horizon $H=1$ Trajectory Coverage** | **81.4%** | 75.3% | $\ge 90.0\%$ | **FAIL** |
| **Horizon $H=2$ Trajectory Coverage** | **80.3%** | 77.2% | $\ge 90.0\%$ | **FAIL** |

---

## 3. Analysis of Dynamical Behavior

1. **Flapping Attenuation vs Latency:**
   - The decoupled leaky accumulation in SSF damped high-frequency jitter, reducing the raw flapping rate from 81.8% down to 68.8%.
   - However, in this discrete turn-level simulation, inter-turn acceleration sign changes remain substantially higher than the 5.0% threshold, reflecting turn-level prompt variation under stress regimes.

2. **Inertia Squeeze During Contradiction Recovery:**
   - While the raw baseline re-converged rapidly (2.0 turns), the decoupled SSF model required **4.75 turns** to re-converge.
   - The slow integration constant ($\beta_{\text{slow}} = 0.12$) introduced excessive inertia into the relational warmth coordinate ($z_5$), causing it to lag behind the abrupt valence inversion introduced during ContradictionShock at $t=15$.

3. **Key Finding:**
   - Excessive reliance on autonomous slow accumulation without observation-driven reset mechanisms harms agility and slows down shock recovery.
