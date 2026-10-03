# Temporal Ablation Study — Phase 22-AL

## 1. Objective

The Temporal Ablation experiment tests Hypothesis **H-AL2 (Temporal Integration Hypothesis)**: Does recovering the 6-dimensional continuous latent user state require temporal context, and does increasing the context window $k \in \{1, 3, 5, 10\}$ resolve the alignment failure?

---

## 2. Experimental Setup

- **Candidates Evaluated:**
  - **C2:** DistilBERT Logits (Text-only baseline representation)
  - **C4:** Hybrid Multimodal Representation (Text logits + Audio acoustic features)
- **Window Configurations Tested:**
  - $k=1$: Instantaneous observation ($e_t \to z_t$)
  - $k=3$: Short temporal window ($[e_{t-2}, e_{t-1}, e_t] \to z_t$)
  - $k=5$: Medium temporal window ($[e_{t-4}, \dots, e_t] \to z_t$)
  - $k=10$: Long temporal window ($[e_{t-9}, \dots, e_t] \to z_t$)
- **Evaluation Split:** Held-out seeds (1024, 2026) across all 6 stress regimes.

---

## 3. Empirical Measurements

### Candidate C2 (Text Representation)

| Window ($k$) | $R^2$ Score | MAE | MSE | Trend / Observation |
| :---: | :---: | :---: | :---: | :--- |
| **$k=1$** | **+0.0365** | **0.1077** | **0.0243** | Instantaneous optimal baseline |
| **$k=3$** | +0.0181 | 0.1082 | 0.0248 | Slight degradation ($\Delta R^2 = -0.0184$) |
| **$k=5$** | -0.1199 | 0.1124 | 0.0283 | Negative generalization under stress |
| **$k=10$** | -0.2723 | 0.1179 | 0.0321 | Severe overparameterization drift |

### Candidate C4 (Hybrid Multimodal Representation)

| Window ($k$) | $R^2$ Score | MAE | MSE | Trend / Observation |
| :---: | :---: | :---: | :---: | :--- |
| **$k=1$** | **+0.2240** | **0.0961** | **0.0196** | Peak instantaneous alignment |
| **$k=3$** | +0.1907 | 0.0959 | 0.0204 | Comparable accuracy, slight $R^2$ loss |
| **$k=5$** | +0.0826 | 0.1009 | 0.0231 | Pronounced degradation ($\Delta R^2 = -0.1414$) |
| **$k=10$** | -0.0533 | 0.1060 | 0.0266 | Degrades into negative alignment |

---

## 4. Analysis & Scientific Takeaways

1. **Context Window Expansion Does NOT Solve Alignment:**
   - As context length expands from $k=1$ to $k=10$, held-out out-of-distribution performance monotonically degrades for both C2 and C4.
   - For C4, $R^2$ plummets from $+0.2240$ at $k=1$ down to $-0.0533$ at $k=10$.
   - For C2, $R^2$ drops from $+0.0365$ at $k=1$ down to $-0.2723$ at $k=10$.

2. **Causal Mechanism of Window Degradation:**
   - Concatenating historical observation vectors linearly expands input dimensionality (from $\dim(e)$ to $k \cdot \dim(e)$).
   - In noisy conversational environments (NoiseSurge, LexicalSparsity, ContradictionShock), stale observation history introduces spurious cross-correlations that destabilize linear projection weights.
   - Contrast with $A_5$ (Leaky Integrator): Exponential leaky filtering on the *state space* achieved $+0.2548$ for C4, whereas concatenating *observation vectors* degraded performance. State-space recurrence is structurally superior to raw observation windowing, but neither bridges the gap to $R^2 \ge 0.85$.

3. **Hypothesis Verdict:**
   - **H-AL2 (Temporal Integration Hypothesis) is REJECTED as an independent resolution.** Temporal windowing on raw observation representations is insufficient to rescue the alignment gate.
