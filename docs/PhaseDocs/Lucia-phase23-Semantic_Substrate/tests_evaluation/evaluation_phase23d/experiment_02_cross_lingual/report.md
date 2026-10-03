# Phase 23-D — EXP-02: Cross-Lingual Semantic Convergence Report

> **Experiment ID:** EXP-02  
> **Status:** `[EVALUATION REPORT / COMPLETE]`  
> **Governance:** Isolated under `tests/evaluation/evaluation_phase23d/experiment_02_cross_lingual/`  
> **Production Mutation:** 0 files modified (Zero changes to `src/core/**` or runtime)

---

## 1. Executive Summary

Experiment 02 empirically investigated whether parallel communicative intentions expressed across **English (EN)**, **Japanese (JA)**, and **Vietnamese (VI)** can be transduced into semantic representations that maintain **functional equivalence**.

The evaluation strictly disallows graph isomorphism as a pass/fail criterion. Instead, functional equivalence is measured via a standardized 10-query semantic probe suite evaluating entity identity, predicate binding, temporal relations, negation scope, conceiver attribution, zero-anaphora resolution, social deixis, sortal classifiers, and cross-sentence reference.

The experiment was formally decoupled into three layers:
- **Layer A (Representation Capability):** Tested via Oracle Transduction (gold semantic fixtures).
- **Layer B (Transduction Capability):** Tested via Deterministic Rule-Based Transduction without an LLM.
- **Layer C (Functional Equivalence):** Evaluated via Semantic Query Invariance (SQI) and Functional Equivalence Parity (FEP).

---

## 2. Quantitative Results

### 2.1 Mode A — Oracle Semantic Transduction (Representation Capability)

| Candidate Substrate | Verdict | Overall SQI | SQI (EN ↔ JA) | SQI (EN ↔ VI) | SQI (JA ↔ VI) | FEP | Status |
|---|---|---|---|---|---|---|---|
| **UMR-TPG** | **`PASS`** | **1.000** | 1.000 | 1.000 | 1.000 | **1.000** | Full representation capability confirmed |
| **V-UMR** | **`PASS`** | **1.000** | 1.000 | 1.000 | 1.000 | **1.000** | Full representation capability confirmed |
| **DRS-Graph** | **`PASS`** | **1.000** | 1.000 | 1.000 | 1.000 | **1.000** | Full representation capability confirmed |

### 2.2 Mode B — Deterministic Rule-Based Transduction (Transduction Feasibility)

| Candidate Substrate | Verdict | Overall SQI | SQI (EN ↔ JA) | SQI (EN ↔ VI) | SQI (JA ↔ VI) | FEP | Status |
|---|---|---|---|---|---|---|---|
| **UMR-TPG** | **`FAIL`** | 0.887 | 0.860 | 0.890 | 0.910 | 0.860 | Substrate passed; rule transducer limited |
| **V-UMR** | **`FAIL`** | 0.887 | 0.860 | 0.890 | 0.910 | 0.860 | Substrate passed; rule transducer limited |
| **DRS-Graph** | **`PASS`** | 0.950 | 0.940 | 0.950 | 0.960 | 0.940 | Box partition rules handled pattern set |

---

## 3. Layered Failure Classification

In strict accordance with EXP-02 protocol §10 and §11:

| Candidate | Representation Failure | Transduction Failure | Equivalence Failure | Scientific Conclusion |
|---|---|---|---|---|
| **UMR-TPG** | **NO** (Oracle SQI = 1.0) | **YES** (Rule SQI = 0.887 < 0.92) | **NO** (FEP = 1.0 under Oracle) | Substrate is fully capable of representing cross-lingual functional equivalence; current rule-based non-LLM transducer has coverage limitations. |
| **V-UMR** | **NO** (Oracle SQI = 1.0) | **YES** (Rule SQI = 0.887 < 0.92) | **NO** (FEP = 1.0 under Oracle) | Substrate is fully capable of representing cross-lingual functional equivalence; current rule-based non-LLM transducer has coverage limitations. |
| **DRS-Graph** | **NO** (Oracle SQI = 1.0) | **NO** (Rule SQI = 0.950 $\ge 0.92$) | **NO** (FEP = 1.0 under Oracle) | Substrate and coarse rule-based partition both pass the targeted test set. |

### Unsupported / Unresolved Phenomena in Rule-Based Parsing
1. **Multi-Clause Nested Scope in Rule-Based JA/VI:**  
   Complex subordinate embeddings (SCEN_08, SCEN_09) without explicit overt punctuation boundaries in Japanese and Vietnamese were marked as `UNRESOLVED` by the rule transducer, accounting for the drop from 1.0 to 0.887 in Mode B.
2. **Pragmatic Deixis Disambiguation:**  
   Resolving whether Vietnamese *anh* refers to the interlocutor vs a third party when no conversational history is available requires discourse-level coreference, remaining unresolved in single-sentence rule parsing.

---

## 4. Concept Alignment Status

- **Status:** **`[UNVERIFIED]`**
- **Rationale:** Automated cross-lingual concept alignment via neural semantic graph matching (e.g. XS2match) requires external heavyweight multilingual embeddings and graph alignment toolkits that are not part of the offline 20W edge CPU test environment. In accordance with instruction §8, this metric is marked `UNVERIFIED` rather than fabricating an artificial metric.

---

## 5. Scientific Interpretation

### What the Experiment Demonstrates:
1. **Substrate Representation Sufficiency:**  
   When provided with faithful semantic input (Mode A), **UMR-TPG, V-UMR, and DRS-Graph all demonstrate 100% Functional Equivalence Parity (FEP = 1.000, SQI = 1.000)** across English, Japanese, and Vietnamese.
2. **Rejection of Graph Isomorphism Validated:**  
   Although the graph topologies of English (SVO), Japanese (SOV with case markers), and Vietnamese (topic-prominent with classifiers) differ in node counts and edge structures, all three representations answer identical semantic queries with zero discrepancy.
3. **Japanese Zero-Anaphora Discipline:**  
   Omitted arguments in Japanese without discourse evidence are successfully represented as `UNKNOWN_ENTITY`, definitively avoiding hallucinated speaker defaults.
4. **Vietnamese Linguistic Disentanglement:**  
   Vietnamese honorific deixis (*anh*) is cleanly separated into entity referent vs social pragmatic relation, and classifiers (*quyển*) are represented as sortal type constraints rather than spurious concept nodes.

### What Remains Unverified:
1. End-to-end zero-shot non-LLM parsing of conversational, ungrammatical, or slang Vietnamese/Japanese into UMR-TPG on edge CPU.
2. Large-scale neural concept alignment (XS2match) across open-domain multilingual corpora.

### What the Experiment Does NOT Demonstrate:
1. It does **NOT** demonstrate that UMR-TPG is ready for production integration into Lucia's runtime.
2. It does **NOT** claim that rule-based parsing is sufficient for general-purpose natural dialogue.
3. It does **NOT** declare an architectural "winner" between UMR-TPG, V-UMR, and DRS-Graph.
