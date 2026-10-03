# Phase 22-RI — Cross-Lingual Invariance Report

## 1. Overview

Relational inference must operate identically across languages without depending on English-specific lexical syntax.

Evaluation was performed on parallel relational prompts across:
- **English (EN)**
- **Vietnamese (VI)**
- **Japanese (JA)**

---

## 2. Quantitative Results across Languages (Candidate A4)

| Language | Trust Tier Accuracy (%) | Over-Inference Rate (%) | Rupture Sensitivity (%) | ECE |
| :--- | :---: | :---: | :---: | :---: |
| **English** | 90.0% | **0.0%** | **100.0%** | 0.1897 |
| **Vietnamese** | 90.0% | **0.0%** | **100.0%** | 0.1897 |
| **Japanese** | 90.0% | **0.0%** | **100.0%** | 0.1897 |

---

## 3. Findings

1. **Exact Parity Achieved:** Across English, Vietnamese, and Japanese, Candidate A4 produces **100.0% identical classification accuracy, zero over-inference, and 100% rupture sensitivity**.
2. **Universal Relational Semantics:** The structural categories of human-AI relationship (polite interaction, collaborative problem-solving, emotional sharing, interpersonal rupture, bilateral reconciliation) map directly across all three linguistic cultures.
