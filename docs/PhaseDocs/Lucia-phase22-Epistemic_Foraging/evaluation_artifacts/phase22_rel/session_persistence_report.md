# Phase 22-REL — Session Persistence Report

## 1. Overview

This report evaluates the long-horizon session-to-session persistence of Layer B variables ($m_0$: Metabolic Fatigue, $m_1$: Relational Warmth) across multiple simulated sessions.

---

## 2. Retention Metrics

Session-to-session retention is measured as the ratio of post-dormancy persistent state to pre-dormancy session state:
$$\rho_{\text{retention}} = \frac{m_{\text{persistent}}}{m_{\text{pre-sleep}}}$$

| Candidate | Relational Warmth Retention | Fatigue Homeostatic Reset | Longitudinal Trend |
| :--- | :---: | :---: | :---: |
| **O1 (Legacy 6D)** | 1.0000 (Static memoryless) | 1.0000 (No reset) | Stationary surface regression |
| **O2 (Open-Loop)** | 1.0000 (No consolidation) | 1.0000 (Runaway accumulation) | Monotonic diverging drift |
| **O3 (Episodic)** | **0.9856** (98.6% retained) | **0.2000** (Full reset to rested) | Bounded homeostatic cycle |
| **O4 (Episodic Corrected)** | **0.9840** (98.4% retained) | **0.2000** (Full reset to rested) | Bounded error-damped cycle |
| **Oracle** | 1.0000 | 0.2000 | Ground truth exact |

---

## 3. Structural Comparison of Retention Behaviors

### 3.1. Fatigue ($m_0$)
- In O1, fatigue is predicted purely from immediate turn features, leading to erratic jumps between turns and zero cumulative fatigue tracking.
- In O2, fatigue accumulates linearly turn-after-turn without ever resetting, reaching extreme values and collapsing $R^2$ to $-30.1787$.
- In O3 and O4, fatigue accurately accumulates during the session, and resets back to the physiological rested baseline ($0.20$) during inter-session dormancy, matching biological homeostatic restoration.

### 3.2. Relational Warmth ($m_1$)
- High retention (>98%) is successfully achieved in O3 and O4, meeting Gate **G_REL3** ($\ge 0.80$).
- However, high retention of an unanchored path integral preserves and compounds earlier errors across multiple sessions. In the absence of an explicit relational grounding mechanism (e.g., explicit user confirmations or episodic autobiographical milestones), synaptic consolidation preserves drift rather than truth.
