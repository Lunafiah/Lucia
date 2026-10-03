# Phase 22-ANCHOR — Multi-Session Persistence Report

## 1. Overview

In episodic relational memory, long-term persistence across sessions must satisfy two competing constraints:
1. **High retention** of positive rapport and interpersonal milestones across days/sessions.
2. **Smooth, biologically plausible homeostatic decay** toward the Philia resting baseline ($+0.30$) over extended dormancy (ADR-028).

---

## 2. Multi-Session Retention Comparison

| Candidate | Inter-Session Consolidation Model | Warmth Retention Behavior | Homeostatic Reset |
| :--- | :--- | :--- | :--- |
| **A0 (Continuous)** | Open-loop accumulation | Diverges without baseline | Full fatigue reset |
| **A1 (Episodic Only)** | Step-function memory without decay | Static step state preserved | Full fatigue reset |
| **A2 (Confidence)** | Gated step-function memory | Clean step state preserved | Full fatigue reset |
| **A3 (Decay & Consolidation)** | **Synaptic consolidation + Philia relaxation** | **98% retention + 2% relaxation toward +0.30** | **Full fatigue reset (0.20)** |
| **Oracle** | True ground truth | Exact ground truth tracking | Exact ground truth |

---

## 3. Structural Behavior

- When no new relational events occur in subsequent sessions, Candidate A1 and A2 maintain the exact relational stance established in earlier sessions.
- Candidate A3 realistically models memory consolidation: if a user leaves the interaction in a state of extreme warmth (e.g. $+0.80$), during weeks/sessions of neutral interaction, the warmth smoothly decays toward the resting Philia attractor ($+0.30$) rather than remaining frozen permanently at artificial highs.
