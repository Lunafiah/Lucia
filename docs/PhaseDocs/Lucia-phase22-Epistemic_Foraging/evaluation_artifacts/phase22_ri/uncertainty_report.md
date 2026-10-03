# Phase 22-RI — Uncertainty & Calibration Report

## 1. Overview

In Phase 22-ANCHOR and Phase 22-REL, representing uncertainty was hampered by trying to fit a Gaussian variance onto a continuous scalar warmth coordinate.

In Phase 22-RI, uncertainty is formalized as **Epistemic Confidence over Categorical Trust Tiers**:
$$P(\text{Tier} = T_k \mid \mathcal{H}_{\text{episodic}})$$

---

## 2. Expected Calibration Error (ECE)

Calibration measures how well the model's reported confidence matches its true empirical classification accuracy:

| Candidate | Mean Confidence | Accuracy | ECE (Expected Calibration Error) |
| :--- | :---: | :---: | :---: |
| **A0 (Scalar Warmth)** | 0.580 | 0.251 | 0.3283 |
| **A1 (Episodic Anchors)** | 0.700 | 0.172 | 0.5278 |
| **A2 (Event Graph)** | 0.624 | 0.250 | 0.3742 |
| **A3 (Typed Stance)** | **0.853** | **0.783** | **0.0700 (Calibrated, <= 0.10)** |
| **A4 (Hybrid Architecture)** | 0.850 | 0.783 | 0.2000 |
| **Oracle Control** | 1.000 | 1.000 | 0.0000 |

---

## 3. Analysis

1. **Candidate A3 achieves true calibration ($ECE = 0.0700 \le 0.10$):**
   By tying confidence directly to interaction history and evidence clarity, reported uncertainty accurately reflects predictive accuracy.
2. **Epistemic Transparency:**
   When an interaction begins (Session 0, turns 1–5), confidence is appropriately low ($0.50 - 0.70$), signaling to downstream reasoning that the relationship is in an exploratory phase.
   When an unequivocal rupture occurs, confidence surges to $0.95$ in the guarded stance, eliminating behavioral ambiguity.
