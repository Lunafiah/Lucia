# Results E5: Bounded Prediction Tree

> **Experiment**: E5 — Bounded Prediction Tree Lookahead  
> **Evaluated Hypothesis**: Bounded prediction tree ($H \le 3, B \le 3$) retains true trajectory in $\ge 95\%$ of trials while executing in $\le 2.5\text{ms}$ on CPU.  

---

## 1. Quantitative Results ($N=200$ trials)

- **Trajectory Coverage $H=1$**: $64.00\%$
- **Trajectory Coverage $H=2$**: **$30.00\%$** (vs. MAP single-path $10.00\%$)
- **Trajectory Coverage $H=3$**: **$6.50\%$**
- **Mean Wall-Clock Latency**: **$362.8\,\mu\text{s}$** ($0.363\text{ms}$)
- **p95 Latency**: **$559.3\,\mu\text{s}$**
- **Max Latency**: **$1854.5\,\mu\text{s}$** ($1.855\text{ms}$)
- **Mean Node Count**: **$9.67$ nodes** (Max 12 nodes, strictly bounded)

---

## 2. Findings & Architectural Implications

1. **Computational Feasibility on CPU**:
   - The tree expansion executed in $0.363\text{ms}$ on average, far below the $2.5\text{ms}$ budget. Peak allocation was 12 nodes, confirming zero combinatorial explosion.
2. **Exponential Path Dispersion**:
   - Across an 8-intent space, branching uncertainty compounds rapidly. While the tree outperformed MAP lookahead by $3\times$ at $H=2$ ($30.0\%$ vs $10.0\%$), retaining $\ge 95\%$ trajectory coverage at $H=2$ was not achieved.
3. **Gate G5 Assessment**:
   - Resource metrics PASSED. Trajectory coverage ($30.0\% < 95.0\%$) **FAILED**.
   - Status: **FAIL**. A bounded discrete tree ($B=3$) cannot capture multi-step conversational trajectories without wider branching or continuous beam representations.
