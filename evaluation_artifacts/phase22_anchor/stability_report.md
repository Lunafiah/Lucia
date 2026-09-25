# Phase 22-ANCHOR — Dynamical Stability & Contradiction Behavior Report

## 1. Dynamical Stability Evaluation

Because relational warmth is updated *only* at sparse anchor events, its stability profile is vastly superior to continuous estimation:

| Candidate | Inter-Anchor Volatility (Variance) | Contradiction Shock Behavior | Boundedness |
| :--- | :---: | :--- | :--- |
| **A0 (Continuous)** | High ($> 0.15$) | Fluctuates continuously with turn noise | Unbounded |
| **A1 (Episodic Only)** | **0.0000 (Completely stable)** | Discontinuous step drop (-0.35) | Bounded $[-1, 1]$ |
| **A2 (Confidence)** | **0.0000 (Completely stable)** | Confidence-weighted step drop | Bounded $[-1, 1]$ |
| **A3 (Decay & Consolidation)** | **0.0000 (Completely stable)** | Step drop followed by slow relaxation | Bounded $[-1, 1]$ |
| **Oracle** | Low ($< 0.01$) | Ground truth step transition | Bounded $[-1, 1]$ |

---

## 2. Contradiction and Rupture Repair

Under `ContradictionShock`:
- At turn 10, an explicit interpersonal rupture occurs ("Stop pretending to understand, you're just failing repeatedly").
- In Candidates A1, A2, and A3, the anchor detector immediately identifies the rupture event, depressing relational warmth by $\approx -0.35$.
- Crucially, subsequent neutral or technical turns do **NOT** induce runaway negative drift. The relationship remains in a guarded/ruptured state until a subsequent explicit repair or milestone occurs, exactly mirroring authentic interpersonal dynamics.
