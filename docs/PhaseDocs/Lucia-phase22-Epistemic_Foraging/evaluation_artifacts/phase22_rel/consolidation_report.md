# Phase 22-REL — Consolidation Report

## 1. Executive Summary

Phase 22-REL investigates whether Layer B variables—specifically Metabolic Fatigue ($m_0$) and Relational Warmth ($m_1$)—can be accurately modeled as an **offline episodic memory consolidation process** rather than real-time continuous state estimation or open-loop numerical integration.

In this experiment, multi-session trajectories were evaluated across 5 candidates:
- **O1 (Legacy 6D Regression):** Direct turn-level joint regression of all 6 coordinates.
- **O2 (Open-Loop Decoupled Layer B):** 4D EKF + open-loop accumulation without consolidation.
- **O3 (Episodic Consolidation):** Fast 4D EKF + episodic memory buffer + offline inter-session synaptic consolidation and homeostatic sleep restoration.
- **O4 (Episodic Consolidation with Error Correction):** O3 augmented with epistemic uncertainty gating $\operatorname{Tr}(P_u)$ and dyadic synchrony innovation.
- **Oracle Control:** Ground truth filter with measurement noise floor.

---

## 2. Empirical Performance Comparison on Held-Out Seeds (1024, 2026)

| Candidate | Obs 4D $R^2$ | Fatigue $m_0$ $R^2$ | Warmth $m_1$ $R^2$ | Overall Layer B $R^2$ | Inter-Session Retention | Recovery Turns | Latency (P50) |
| :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| **O1 (Legacy 6D)** | 0.5536 | 0.3885 | 0.4009 | 0.3947 | 1.0000 | 1.80 turns | 0.0001 ms |
| **O2 (Open-Loop Decoupled)** | 0.5192 | -30.1787 | -2.1513 | -16.1650 | 1.0000 | 1.80 turns | 0.0001 ms |
| **O3 (Episodic Consolidation)** | 0.5192 | **0.5702** | **-4.4912** | -1.9605 | **0.9856** | 1.80 turns | 0.0001 ms |
| **O4 (Episodic Corrected)** | 0.5192 | **0.3781** | **-4.5120** | -2.0670 | **0.9840** | 1.80 turns | 0.0001 ms |
| **Oracle Control** | 0.9969 | 0.9756 | 0.9986 | 0.9871 | 1.0000 | 1.00 turns | 0.0001 ms |

---

## 3. Consolidation Mechanism Dynamics

### 3.1. Metabolic Fatigue ($m_0$): Successful Homeostatic Consolidation
In O3, introducing **inter-session sleep restoration** (homeostatic reset) successfully resolves the open-loop drift of fatigue observed in O2 ($R^2 = -30.1787 \to +0.5702$).
Because fatigue resets to a physiological resting baseline between sessions and accumulates monotonically with cognitive load and interaction urgency within a session, episodic buffer integration matches the ground-truth physical dynamics of fatigue ($R^2 = 0.5702$, passing the $0.50$ gate under O3).

### 3.2. Relational Warmth ($m_1$): The Integration Divergence Trap
In sharp contrast to fatigue, Relational Warmth accumulates across sessions without a full reset. In O3 and O4, summing or integrating episodic positive valence deltas ($\Delta \text{warmth} \propto u_1$) across multiple sessions still causes open-loop integral drift:
$$\hat{m}_1(S) = \hat{m}_1(0) + \sum_{s=1}^S \sum_{t=1}^T \Delta \text{warmth}_{s,t}$$
Because small estimation errors in turn-level valence $\hat{u}_1$ are accumulated without a continuous closed-loop feedback anchor, the accumulated estimate diverges from the ground truth trajectory over longitudinal sessions, resulting in negative held-out $R^2$ ($-4.4912$ in O3, $-4.5120$ in O4).

---

## 4. Architectural Implication
Consolidation alone cannot create information that was not observable. While homeostatic cycles naturally anchor somatic states (like fatigue), relational bonding cannot be accurately integrated as a scalar path-integral without external calibration anchors.
