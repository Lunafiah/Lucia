# Phase 22-REL — Stability & Contradiction Recovery Report

## 1. Dynamical Stability & Flapping Analysis

Dynamical stability is evaluated via acceleration sign transitions (flapping) on the 4D Observable state ($\mathbf{u} \in \mathbb{R}^4$) and trajectory smoothness on Layer B.

| Candidate | Flapping Rate (%) | Contradiction Recovery (turns) | Long-Horizon Boundedness |
| :--- | :---: | :---: | :---: |
| **O1 (Legacy 6D)** | 92.2% | 1.80 | Bounded by regression surface |
| **O2 (Open-Loop Decoupled)** | 94.1% | 1.80 | Unbounded drift on $m_0, m_1$ |
| **O3 (Episodic Consolidation)** | 94.1% | 1.80 | Strictly bounded by $[0, 1] \times [-1, 1]$ |
| **O4 (Episodic Corrected)** | 94.1% | 1.80 | Strictly bounded by $[0, 1] \times [-1, 1]$ |
| **Oracle Control** | 93.5% | 1.00 | Exact ground truth bound |

---

## 2. Contradiction Shock Recovery

Under the `ContradictionShock` regime, user valence abruptly inverts at turn 10 of a session ($u_1 \to -u_1$), accompanied by an interpersonal rupture ($\Delta m_1 = -0.25$).

- **Layer A (Observable Valence):**
  The EKF tracking loop detects the innovation shock and inverts the sign of $\hat{u}_1$ within **1.80 turns**, stabilizing cleanly without diverging.
- **Layer B (Relational Warmth):**
  In O3 and O4, the shock enters as negative episodic evidence ($\Delta \text{warmth} < 0$). However, because relational warmth is treated as a slow, high-inertia variable, it does not instantly flip to -1.0; instead, it exhibits realistic damping, avoiding artificial conversational whiplash.
