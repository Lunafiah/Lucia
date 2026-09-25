# Phase 22-RI — Inference & Anti-Over-Inference Report

## 1. The Over-Inference Problem in Companion AI

A fatal failure mode in current commercial companion AI systems is **premature over-familiarity**:
When a user merely says *"Nice job"* or *"Thanks for the snippet"*, the system immediately assumes deep emotional intimacy, declaring love, friendship, or personal bonding.

Phase 22-RI explicitly tested candidate resilience against over-inference on weak/polite small-talk turns.

---

## 2. Quantitative Evidence on Over-Inference and Classification

| Candidate | Trust Tier Accuracy (%) | Over-Inference Rate on Weak Evidence (%) | Rupture Sensitivity (%) | Repair Verification (%) |
| :--- | :---: | :---: | :---: | :---: |
| **A0 (Scalar Warmth Baseline)** | 25.1% | **62.5% (Fatal failure)** | 0.0% (Failed) | 100.0% |
| **A1 (Episodic Anchors Only)** | 17.2% | **0.0%** | 100.0% | 100.0% |
| **A2 (Relational Event Graph)** | 25.0% | **0.0%** | 100.0% | 100.0% |
| **A3 (Typed Stance Evidence-Gated)** | **78.3%** | **0.0%** | 100.0% | 100.0% |
| **A4 (Hybrid Architecture)** | **78.3%** | **0.0% (Passed Gate G_RI2)** | **100.0% (Passed Gate G_RI3)** | **100.0% (Passed Gate G_RI4)** |
| **Oracle Control** | 100.0% | 0.0% | 100.0% | 100.0% |

---

## 3. How Anti-Over-Inference Works in Candidate A4

Candidate A4 employs a **Strict Evidence Gating Hierarchy**:
1. **Weak Evidence (`weak_positive`, `weak_negative`):**
   Superficial praise (e.g. *"Thanks for the fast answer"*) or minor critique is categorized as **insufficient evidence**. It is logged as interaction count but possesses **zero promotion power**.
2. **Pattern Evidence (`pattern_collaborative`):**
   Requires a minimum streak of verified successful collaborative turns ($N \ge 2$) before allowing transition from $T_1$ `ACQUAINTANCE` to $T_2$ `COLLABORATOR`.
3. **Milestone Evidence (`milestone_bonding`):**
   Personal autobiographical vulnerability explicitly shared by the user is required to unlock $T_3$ `COMPANION` or $T_4$ `CONFIDANT`.
4. **Result:** Over-inference rate is strictly **0.0%** in Candidate A4, completely eliminating false intimacy.
