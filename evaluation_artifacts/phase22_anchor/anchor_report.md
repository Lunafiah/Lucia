# Phase 22-ANCHOR — Anchor Report

## 1. Executive Summary

Phase 22-ANCHOR investigates whether Relational Warmth can be modeled stably as **episodic/autobiographical relational memory grounded by meaningful anchors**, rather than an unanchored continuous scalar path integral or turn-level surface observable.

An anchor is defined as an **explicit relational event** (e.g. a collaborative milestone, heartfelt gratitude, explicit trust affirmation, or interpersonal rupture). Between anchors, relational warmth remains stationary in autobiographical memory.

---

## 2. Anchor Precision and False-Anchor Evaluation

| Candidate | Anchor Recall / Precision | False-Anchor Rate | Non-Anchor Turn Drift | Warmth MAE | Warmth $R^2$ |
| :--- | :---: | :---: | :---: | :---: | :---: |
| **A0 (Continuous Accumulation)** | 0.0000 (No anchors) | 0.0000 | 0.00215 / turn | 0.5751 | -2.9071 |
| **A1 (Episodic Anchors Only)** | **1.0000 (100%)** | **0.0000 (0.0%)** | **0.00000 (Zero drift)** | **0.4115** | -1.2655 |
| **A2 (Anchors + Confidence)** | 0.7013 (70.1%) | **0.0000 (0.0%)** | **0.00000 (Zero drift)** | 0.5026 | -1.9861 |
| **A3 (Anchors + Consolidation)** | **0.7662 (76.6%)** | **0.0000 (0.0%)** | **0.00000 (Zero drift)** | **0.4148** | **-1.1375** |
| **Oracle Control** | 0.0000 | 0.0000 | 0.01130 | 0.0080 | 0.9991 |

---

## 3. Key Observations

1. **Drift Is 100% Eliminated on Non-Anchor Turns:**
   In A1, A2, and A3, because warmth updates *only* when an explicit relational event occurs, the per-turn drift is strictly **0.00000** (passing Gate **G_ANC2**). This fundamentally terminates the runaway stochastic diffusion that crippled Phase 22-ONT and Phase 22-REL.
2. **Zero False-Anchor Triggering:**
   Across all neutral, technical, sparse, and procedural turns, the false anchor creation rate is strictly **0.0%** (passing Gate **G_ANC4** $\le 10\%$).
3. **Substantial MAE Reduction:**
   MAE on warmth drops from 0.5751 in continuous accumulation (A0) down to **0.4115** in A1 and 0.4148 in A3, representing a ~28% reduction in tracking error.
