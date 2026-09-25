# Phase 22-ANCHOR — Relational Memory Retrieval Report

## 1. Overview

This report evaluates the accuracy and consistency of retrieving relational stance ($m_1$: Relational Warmth) from episodic autobiographical memory across longitudinal sessions.

---

## 2. Retrieval Metrics

| Candidate | Retrieval / Detection Recall | Consistency Under Noise | False Retrieval Rate | Gating Mechanism |
| :--- | :---: | :---: | :---: | :--- |
| **A0 (Continuous)** | N/A | Low (Fluctuates) | High | None |
| **A1 (Episodic Only)** | **1.0000 (100%)** | High | 0.0000 | Text-only classification |
| **A2 (Confidence-Gated)** | 0.7013 (70.1%) | Very High | 0.0000 | Multimodal EKF valence consistency |
| **A3 (Decay & Consolidation)** | **0.7662 (76.6%)** | Very High | 0.0000 | Multimodal + Philia attractor decay |

---

## 3. Analysis

1. **A1 Sensitivity vs A2 Specificity:**
   - Candidate A1 achieves 100% recall on ground-truth relational anchors because it triggers directly on linguistic anchor intent.
   - Candidate A2 and A3 enforce a multimodal consistency check (requiring that observable valence $\hat{u}_1$ aligns with the anchor direction). Under high noise regimes (`NoiseSurge`), noisy acoustic features attenuate estimated valence, causing A2 and A3 to conservatively suppress anchor creation in ~23-30% of ambiguous events to prevent corrupted memory entries.
2. **Zero Inversion Errors:**
   No rupture was ever misclassified as a milestone, and no milestone was ever misclassified as a rupture.
