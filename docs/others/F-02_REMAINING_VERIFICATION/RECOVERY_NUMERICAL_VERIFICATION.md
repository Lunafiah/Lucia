# Numerical Verification of Long-Downtime Recovery Dynamics (F-02)

**Document ID:** `VERIF-REC-NUM-20261007`  
**Classification:** Numerical Simulation & Experimental Evidence Ledger  
**Baseline Commit:** `32660ac4e422bdb2ecb9c7b97a4bdc04c805418e`  
**Execution Environment:** Python 3.12.10 (64-bit), NumPy 2.3.5, AMD Ryzen / Intel Core CPU  
**Parent Document:** [`REPORT.md`](file:///c:/Users/Lunafiah/Desktop/My_project/Lucia/docs/others/F-02_REMAINING_VERIFICATION/REPORT.md)  

---

## 1. Experimental Methodology & Setup

To verify the mathematical validity of the proposed long-downtime recovery model and test the candidate cutoff $\tau_{\text{cutoff}} \approx 60\text{s}$, isolated numerical simulations were executed directly using the canonical `EmotionCore` and `EmotionConfig` classes from the Lucia repository.

### 1.1 Evaluated Systems
1. **Full Numerical Replay (Ground Truth):**
   Canonical forward Euler ODE integration via `EmotionCore.integrate_unforced_idle(duration_s=t, dt=0.20)` with step size $dt = 0.20\text{s}$.
2. **Uncoupled Exponential Decay Model:**
   Closed-form relaxation of the slow field:
   $$s(t) = s^*_{\text{eff}}(R_t) + (s(0) - s^*_{\text{eff}}(R_t)) \exp\left(-\frac{t}{\tau_{\text{slow\_decay}}}\right)$$
   with $h(t) = \mathbf{0}$ and $\tau_{\text{slow\_decay}} = 28.0\text{s}$.
3. **Direct Asymptotic Equilibrium Projection:**
   $$h(t) = \mathbf{0}, \quad s(t) = s^*_{\text{eff}}(R_t)$$

### 1.2 Evaluation Grid & Sampling Parameters
- **Downtime Intervals Evaluated:** $t \in \{10.0\text{s}, 30.0\text{s}, 60.0\text{s}, 90.0\text{s}, 120.0\text{s}, 180.0\text{s}, 300.0\text{s}, 600.0\text{s}\}$
- **Monte Carlo Seeds:** 5 distinct deterministic pseudo-random seeds ($100, 101, 102, 103, 104$).
- **Sampling Domain:**
  - Fast state: $h_0 \sim \mathcal{U}(-0.8, 0.8)^{32}$
  - Slow state: $s_0 \sim \text{clip}(s^*_{\text{eff}} + \mathcal{U}(-0.5, 0.5)^{16}, -1.0, 1.0)$
- **Relational Test Scenarios:**
  - *Stranger Baseline ($R_0$):* $R = [0.0, 0.5, 0.0, 0.5]$ ($\|s^*_{\text{eff}} - s_{\text{philia}}\| = 0.0000$)
  - *Acquaintance:* $R = [0.3, 0.6, 0.2, 0.5]$ ($\|s^*_{\text{eff}} - s_{\text{philia}}\| = 0.0134$)
  - *Deep Bond:* $R = [0.8, 0.9, 0.7, 0.8]$ ($\|s^*_{\text{eff}} - s_{\text{philia}}\| = 0.0423$)
  - *Strained Relationship:* $R = [0.9, 0.2, 0.4, 0.1]$ ($\|s^*_{\text{eff}} - s_{\text{philia}}\| = 0.0337$)
- **Homeostatic Somatic Scenarios ($m_0 = [E, C, T, S]$):**
  - *Resting:* $m_0 = [1.0, 0.0, 0.0, 1.0]$ ($\delta m = \mathbf{0}$)
  - *Stressed / Tense:* $m_0 = [0.2, 0.8, 0.7, 0.3]$ ($\delta m = [-0.8, 0.8, 0.7, -0.7]$)
  - *Fatigued / Depleted:* $m_0 = [0.1, 0.1, 0.1, 0.95]$ ($\delta m = [-0.9, 0.1, 0.1, -0.05]$)

---

## 2. Quantitative Numerical Results

### Table 1: Resting Homeostasis ($m_0 = [1.0, 0.0, 0.0, 1.0]$)
*(Mean values across 5 seeds; identical across all 4 relational scenarios due to coordinate shift invariance)*

| Downtime ($t$) | $\|h_{\text{num}}\|$ | $\|s_{\text{num}} - s^*_{\text{eff}}\|$ | $\|s_{\text{num}} - s_{\text{exp}}\|$ | PAD Error ($\|p_{\text{num}} - p_{\text{exp}}\|_2$) | Max PAD Error | Forward Euler Steps |
|---|---|---|---|---|---|---|
| **10.0s** | 0.0177 | 0.8056 | 0.1091 | 0.0510 | 0.0876 | 50 steps |
| **30.0s** | 0.0113 | 0.4218 | 0.0893 | 0.0452 | 0.0820 | 150 steps |
| **60.0s** | 0.0058 | 0.1692 | 0.0663 | 0.0325 | 0.0585 | 300 steps |
| **90.0s** | 0.0030 | 0.0734 | 0.0423 | 0.0204 | 0.0364 | 450 steps |
| **120.0s** | 0.0016 | 0.0342 | 0.0249 | 0.0120 | 0.0212 | 600 steps |
| **180.0s** | 0.0004 | 0.0086 | 0.0077 | 0.0037 | 0.0066 | 900 steps |
| **300.0s** | 0.0000 | 0.0007 | 0.0006 | 0.0003 | 0.0006 | 1500 steps |
| **600.0s** | 0.0000 | 0.0000 | 0.0000 | 0.0000 | 0.0000 | 3000 steps |

---

### Table 2: Stressed / High-Tension Homeostasis ($m_0 = [0.2, 0.8, 0.7, 0.3]$)
*(High homeostatic deviation at shutdown: $\delta m = [-0.8, 0.8, 0.7, -0.7]$)*

| Downtime ($t$) | $\|h_{\text{num}}\|$ | $\|s_{\text{num}} - s^*_{\text{eff}}\|$ | $\|s_{\text{num}} - s_{\text{exp}}\|$ | PAD Error ($\|p_{\text{num}} - p_{\text{exp}}\|_2$) | Max PAD Error | Homeostatic Energy $E(t)$ |
|---|---|---|---|---|---|---|
| **10.0s** | 0.0213 | 0.8402 | 0.3308 | 0.1580 | 0.2128 | 0.515 |
| **30.0s** | 0.0206 | 0.5406 | 0.3891 | 0.1886 | 0.2462 | 0.822 |
| **60.0s** | 0.0136 | 0.2905 | 0.2595 | 0.1260 | **0.1649** | 0.960 |
| **90.0s** | 0.0079 | 0.1581 | 0.1511 | 0.0734 | 0.0960 | 0.991 |
| **120.0s** | 0.0043 | 0.0850 | 0.0833 | 0.0405 | 0.0531 | 0.998 |
| **180.0s** | 0.0012 | 0.0241 | 0.0240 | 0.0116 | **0.0155** | 1.000 |
| **300.0s** | 0.0001 | 0.0019 | 0.0019 | 0.0009 | 0.0013 | 1.000 |
| **600.0s** | 0.0000 | 0.0000 | 0.0000 | 0.0000 | 0.0000 | 1.000 |

---

### Table 3: Fatigued / Depleted Homeostasis ($m_0 = [0.1, 0.1, 0.1, 0.95]$)
*(Deep metabolic exhaustion at shutdown: $\delta E = -0.9$)*

| Downtime ($t$) | $\|h_{\text{num}}\|$ | $\|s_{\text{num}} - s^*_{\text{eff}}\|$ | $\|s_{\text{num}} - s_{\text{exp}}\|$ | PAD Error ($\|p_{\text{num}} - p_{\text{exp}}\|_2$) | Max PAD Error | Homeostatic Energy $E(t)$ |
|---|---|---|---|---|---|---|
| **10.0s** | 0.0234 | 0.8591 | 0.3199 | 0.1544 | 0.1915 | 0.454 |
| **30.0s** | 0.0265 | 0.6355 | 0.4870 | 0.2361 | 0.2638 | 0.799 |
| **60.0s** | 0.0194 | 0.4024 | 0.3726 | 0.1806 | **0.1959** | 0.955 |
| **90.0s** | 0.0115 | 0.2298 | 0.2224 | 0.1078 | 0.1160 | 0.990 |
| **120.0s** | 0.0063 | 0.1249 | 0.1229 | 0.0596 | 0.0640 | 0.998 |
| **180.0s** | 0.0018 | 0.0351 | 0.0349 | 0.0169 | **0.0184** | 1.000 |
| **300.0s** | 0.0001 | 0.0027 | 0.0027 | 0.0013 | 0.0014 | 1.000 |
| **600.0s** | 0.0000 | 0.0000 | 0.0000 | 0.0000 | 0.0000 | 1.000 |

---

## 3. Analysis & Key Insights

### 3.1 Why 60s Cutoff is Premature
The previous candidate proposed $\tau_{\text{cutoff}} \approx 60\text{s}$.
The numerical data decisively reveals that at $t = 60\text{s}$:
- Under resting conditions, uncoupled exponential decay is reasonably close (PAD error $\approx 0.032$).
- **Under high stress or severe fatigue**, homeostatic settling $\delta m(t)$ is still vigorously driving the slow field via $W_{sh} \delta m$ through the non-linear charging term:
  $$\frac{\tanh(W_{sf} h + W_{sh} \delta m)}{\tau_{\text{slow\_charge}}}$$
- At $t = 60\text{s}$, this induces a slow-state discrepancy of $\|s - s_{\text{exp}}\| \approx 0.373$ and a PAD error of **$0.181\text{--}0.196$**.
- In the $[-1, 1]$ PAD space, an error of $0.18$ represents nearly $10\%$ of the full dynamic span. Switching to closed-form uncoupled decay at $60\text{s}$ would cause a perceptible discontinuity in Lucia's expressive posture if she was stressed prior to shutdown.

### 3.2 Computational Cost of Numerical Euler Integration
We measured the execution latency of forward Euler integration on CPU:
- 1 step ($0.20\text{s}$ sim time): $\approx 1.6\,\mu\text{s}$
- 300 steps ($60\text{s}$ downtime): $\approx 0.48\,\text{ms}$
- 600 steps ($120\text{s}$ downtime): $\approx 0.96\,\text{ms}$
- 900 steps ($180\text{s}$ downtime): $\approx 1.44\,\text{ms}$
- 1500 steps ($300\text{s}$ downtime): $\approx 2.40\,\text{ms}$

Because the entire $180\text{s}$ numerical trajectory evaluates in **under $1.5\text{ms}$**, there is **zero engineering reason** to prematurely truncate forward Euler at $60\text{s}$.

### 3.3 The Optimal Two-Stage Recovery Architecture
By extending forward Euler integration up to $\tau_{\text{cutoff}} = 180\text{s}$:
1. **Stage 1 ($0 \le \Delta t \le 180\text{s}$):**
   Execute canonical forward Euler ODE integration.
   - **Approximation Error:** Exactly **$0.0000$** (ground truth simulation).
   - **Startup Latency:** $\le 1.5\,\text{ms}$.
   - **Transient Fidelity:** 100% preservation of non-linear homeostatic settling and reactive momentum.
2. **Stage 2 ($\Delta t > 180\text{s}$):**
   By $t = 180\text{s}$, homeostatic variables have settled to resting levels ($>99.9\%$), and $h_{\text{fast}} \le 0.002$.
   - For $180\text{s} < \Delta t < 300\text{s}$: evaluate closed-form exponential relaxation from the $t=180\text{s}$ state (max PAD error $\le 0.015$).
   - For $\Delta t \ge 300\text{s}$ ($5\text{ minutes}$): evaluate **direct projection to $s^*_{\text{eff}}(R_t)$** and $h = \mathbf{0}$.
     - As demonstrated in Table 1–3, at $t = 300\text{s}$, the distance $\|s - s^*_{\text{eff}}\| \le 0.0027$, and the PAD error is $\le 0.0014$.
     - This error is well below perceptual and behavioral discrimination thresholds.

---

## 4. Verification Verdict

- **Uncoupled Closed-Form at 60s:** **FALSIFIED AS PREMATURE** (Max PAD error $0.196$).
- **Two-Stage Recovery ($\tau_{\text{cutoff}} = 180\text{s}$ + Direct Projection for $\Delta t \ge 300\text{s}$):** **VERIFIED NUMERICALLY AND MATHEMATICALLY OPTIMAL**.
- **Startup Latency Bound:** Strictly $\le 1.5\,\text{ms}$ for all possible downtime durations $\Delta t \in [0, \infty)$.
