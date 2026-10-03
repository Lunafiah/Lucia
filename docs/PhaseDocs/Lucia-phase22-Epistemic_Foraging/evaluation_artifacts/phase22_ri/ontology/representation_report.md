# Phase 22-RI — Ontology & Representation Report

## 1. Overview & Structural Motivation

Phase 22-RI investigates how Lucia can infer, maintain, and structure relational stance from episodic autobiographical memory anchors without falling back to a continuous scalar path-integral or real-time surface observable.

---

## 2. Comparative Matrix of Candidate Representations

| Candidate | Structural Ontology | Representation Format | Handling of Weak Praise | Handling of Rupture |
| :--- | :--- | :--- | :--- | :--- |
| **A0 (Scalar Warmth)** | 1D Real Continuum $m_1 \in [-1, 1]$ | Continuous float binned into arbitrary tiers | **Severe Over-Inference (62.5%)** | Fails to guard (Sensitivity 0%) |
| **A1 (Episodic Anchors)** | Unstructured Event List | Flat log of events $[(e_1, t_1), (e_2, t_2)]$ | No over-inference | Instant drop |
| **A2 (Event Graph)** | Temporal Directed Graph | Nodes: Events, Edges: Temporal decay | No over-inference | Graph-weighted penalty |
| **A3 (Typed Stance)** | Typed Predicate State Machine | Discrete state: $\{T_0..T_4\} \times \{\text{guarded}\}$ | No over-inference (0.0%) | Instant guarded lock |
| **A4 (Hybrid Architecture)** | **Episodic Graph + Trust Tiers + Epistemic Uncertainty** | **Autobiographical Memory Graph in Kanerva SDM + Asymmetric State Machine** | **Zero Over-Inference (0.0%)** | **100% Guarded Sensitivity & Verified Repair** |

---

## 3. Structural Definition of Candidate A4

Candidate A4 synthesizes the strengths of graphs and state machines:

1. **Discrete Trust Tiers ($T_0$ to $T_4$):**
   - $T_0$ `STRANGER`: Onboarding baseline. Strict boundary.
   - $T_1$ `ACQUAINTANCE`: Established polite interaction history.
   - $T_2$ `COLLABORATOR`: Proven task alignment and mutual reliability across streaks.
   - $T_3$ `COMPANION`: Personal autobiographical milestone sharing.
   - $T_4$ `CONFIDANT`: Deep reciprocal trust resilient to minor frictions.
2. **Episodic Event Graph:**
   Anchored directly into **Kanerva Sparse Distributed Memory (SDM)** (ADR-011). Each event node stores:
   - `Event_Type`: `milestone`, `rupture`, `repair`, `collaborative_streak`
   - `Salience`: Calibrated emotional weight
   - `Timestamp`: Session index & turn index
   - `Verbatim_Utterance`: Autobiographical memory snippet
3. **Epistemic Uncertainty Tensor:**
   Outputs confidence interval rather than a deterministic single score, reflecting empirical evidence density.
