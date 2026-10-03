# Phase 22-MR -- Final Research Report
## Memory Retrieval & Context Conditioning Study

---

## 1. Executive Summary

Phase 22-MR addresses the bottleneck identified by Phase 22-RI:

> **How can the Cognitive Orchestrator retrieve the correct episodic relational
> anchors from Kanerva SDM and convert them into a small, stable context conditioning
> signal for the SLM without causing context overflow or hallucination?**

Five retrieval candidates (M0-M4) plus Oracle were benchmarked across all 5 seeds,
6 stress regimes, and 3 languages (EN/VI/JA) against 9 preregistered acceptance gates.

**Key finding:** The bottleneck is NOT recall (M4 achieves 100% recall), NOT latency
(0.35 ms -- well within SLA), and NOT hallucination risk (0.00%). The bottleneck is
**retrieval precision and context injection quality**: M4 injects ~40% irrelevant memory
traces into the SLM context window, causing context dilution despite correct safety-critical
anchor recovery.

---

## 2. Gate Verification Summary (M4 -- Held-Out Seeds 1024 & 2026)

| Gate | Criterion | Threshold | M4_HybridFull | Oracle | Status |
| :--- | :--- | :---: | :---: | :---: | :---: |
| **G_MR1** | Relevant-Memory Recall | >= 0.90 | **1.0000** | **1.0000** | **PASSED** |
| **G_MR2** | Retrieval Precision@K | >= 0.80 | 0.3159 | 0.5380 | **FAILED** |
| **G_MR3** | Context Compression Ratio | >= 0.70 | 0.4115 | 0.5313 | **FAILED** |
| **G_MR4** | Context Token Budget P95 | <= 512 | **472** | **381** | **PASSED** |
| **G_MR5** | Irrelevant Injection Rate | <= 0.05 | 0.3999 | **0.0000** | **FAILED** |
| **G_MR6** | Hallucination Risk | <= 0.10 | **0.0000** | **0.0000** | **PASSED** |
| **G_MR7** | Relational Consistency | >= 0.85 | **0.9918** | **0.9869** | **PASSED** |
| **G_MR8** | CPU Latency P50 | <= 5.0 ms | **0.3548 ms** | **0.0319 ms** | **PASSED** |
| **G_MR9** | GPU VRAM Footprint | == 0 MB | **0.0 MB** | **0.0 MB** | **PASSED** |

**Gates Passed: 6/9.** Three gates failed -- all related to **context injection quality**.

---

## 3. Full Candidate Comparison (Held-Out Seeds, All Regimes, All Languages)

| Candidate | Recall | Precision@K | Mand.Recall | Inj.Rate | Hall.Risk | Rel.Cons | P50 (ms) |
| :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| M0_RawDump | 0.9902 | 0.1884 | 0.9834 | 0.6641 | 0.2977 | 0.9923 | 0.052 |
| M1_TopKCosine | 0.0974 | 0.0621 | 0.1893 | 0.8812 | 0.2772 | 0.6467 | 0.269 |
| M2_TemporalRelational | 0.3692 | 0.3418 | 0.5200 | 0.0368 | 0.0121 | 0.9877 | 0.346 |
| M3_GraphAware | 0.8416 | 0.4446 | 0.9958 | 0.2423 | 0.0000 | 0.9828 | 0.295 |
| **M4_HybridFull** | **1.0000** | 0.3159 | **1.0000** | 0.3999 | **0.0000** | **0.9918** | 0.355 |
| Oracle | **1.0000** | **0.5380** | **1.0000** | **0.0000** | **0.0000** | 0.9869 | 0.032 |

### Key Discriminants

1. **M1_TopKCosine fails catastrophically** on mandatory recall (0.19): pure embedding
   similarity cannot guarantee recovery of safety-critical rupture/repair/milestone anchors.
   This is an epistemic safety failure -- the SLM would condition on stale/neutral context
   during active rupture.

2. **M2_TemporalRelational** achieves the best injection rate (0.037) but has unacceptably
   low recall (0.37) and mandatory recall (0.52). It trades safety for precision.

3. **M3_GraphAware** provides a better balance: high mandatory recall (0.9958),
   zero hallucination risk, but still insufficient precision (0.44) and injection (0.24).

4. **M4_HybridFull** is the only candidate achieving simultaneous:
   - Perfect recall (1.0000) -- no relevant anchor is ever missed
   - Perfect mandatory recall (1.0000) -- safety-critical events always retrieved
   - Zero hallucination risk (0.0000) -- no contradiction co-injection
   - Strong relational consistency (0.9918) -- tier-coherent context

   Its failure is precision alone: it retrieves too many moderately-relevant traces
   alongside the mandatory anchors, diluting context quality.

---

## 4. Per-Regime Stress Analysis (M4, Held-Out Seeds)

| Regime | Recall | Precision | Mand.Recall | Inj.Rate | Hall.Risk | Rel.Cons |
| :--- | :---: | :---: | :---: | :---: | :---: | :---: |
| ID | 1.0000 | 0.3210 | 1.0000 | 0.4099 | 0.0000 | 1.0000 |
| NoiseSurge | 1.0000 | 0.3475 | 1.0000 | 0.3507 | 0.0000 | 0.9981 |
| LexicalSparsity | 1.0000 | 0.2000 | 1.0000 | 0.8000 | 0.0000 | 1.0000 |
| ContradictionShock | 1.0000 | 0.3422 | 1.0000 | 0.3634 | 0.0000 | 1.0000 |
| TemporalDrift | 1.0000 | 0.2862 | 1.0000 | 0.4378 | 0.0000 | 0.9805 |
| CombinedStress | 1.0000 | 0.3082 | 1.0000 | 0.3775 | 0.0000 | 0.9832 |

**Critical observation:** Injection rate peaks at 0.80 under LexicalSparsity -- when the SDM
contains very few anchors, even a small number of neutral_task traces dominates the context
window. This is a sparse-evidence edge case with significant architectural implications.

---

## 5. Root Cause Analysis -- The Precision-Recall Dilemma

M4's precision gap (0.3159 vs Oracle's 0.5380) arises from a structural tension:

1. Mandatory guarantee requires always retrieving rupture/repair/milestone traces.
2. Cosine + type-weight scoring also retrieves weak_positive and weak_negative traces
   that are moderately correlated in embedding space with high-relevance anchors.
3. The token budget (512) is generous enough that M4 fills the budget before hitting
   the precision wall -- resulting in over-retrieval.

Oracle achieves precision 0.5380 by selecting only traces with relevance >= 0.50,
excluding weak_positive (0.20) and weak_negative (0.20) anchors entirely.

---

## 6. Decisive Research Conclusions

`
========================================================
PHASE 22-MR RESEARCH CLASSIFICATION
========================================================
  STUDY:                Memory Retrieval & Context Conditioning
  GATES PASSED:         6 / 9
  PRODUCTION PROMOTION: STRICTLY NOT AUTHORIZED
  PHASE 23:             UNTOUCHED
  GENESIS GATE:         PRESERVED (is_onboarded=false)
========================================================
`

### What Is Resolved

| Claim | Evidence | Status |
| :--- | :--- | :---: |
| Safety-critical anchors can always be retrieved | Mandatory Recall = 1.00 (M4, all regimes) | VERIFIED |
| Retrieval is CPU-only, zero VRAM | 0.0 MB VRAM, P50=0.35ms | VERIFIED |
| Hallucination risk is eliminable | 0.0000 (M4, M3, Oracle) | VERIFIED |
| Relational consistency maintained | 0.9918 (M4) | VERIFIED |
| Context fits within 512-token SLM budget | P95=472 tokens | VERIFIED |
| Raw cosine similarity is insufficient | M1 mand.recall=0.19 | FALSIFIED (M1 rejected) |
| Precision-recall gap to Oracle | Gap = 0.5380 - 0.3159 = 0.2221 | MEASURED |

### What Remains Unresolved

| Open Question | Evidence Available |
| :--- | :---: |
| Can a learned relevance gate close the precision gap without sacrificing recall? | Not yet tested |
| Does injection rate drop below 0.05 with a dynamic k selection strategy? | Not yet tested |
| Is LexicalSparsity precision (0.20) recoverable with memory expansion heuristic? | Not yet tested |
| Is the Oracle ceiling (0.54) itself sufficient for SLM conditioning quality? | Requires SLM eval |

---

## 7. Next Bottleneck

> **Phase 22-MR identifies the next bottleneck as:**
>
> **Relevance Gating: how to distinguish high-evidential-value anchors from
> low-evidential-value anchors within the relational memory store, so that retrieval
> precision can approach Oracle (0.54) without sacrificing the mandatory anchor
> guarantee (1.00) or introducing hallucination risk (0.00).**

Proposed next research directions for Phase 22-RG (Relevance Gating):

1. Evidence-strength re-scoring gate: post-retrieval re-rank with strict relevance threshold
2. Dynamic k selection: adapt retrieved count to SDM density
3. Compression-first retrieval: retrieve large candidate set, compress to most informative subset
4. Learned relevance predictor: CPU-only logistic regression on anchor-type x tier x session-age

---

## 8. Invariant Compliance

| Invariant | Status |
| :--- | :---: |
| data/profile.json is_onboarded=false preserved | VERIFIED |
| No src/core/ production code touched | VERIFIED |
| No Phase 23 code touched | VERIFIED |
| Genesis onboarding gate untouched | VERIFIED |
| 100% CPU-only, 0 MB GPU VRAM | VERIFIED |
| Experiments isolated to tests/evaluation/phase22_mr/ | VERIFIED |
| Artifacts isolated to evaluation_artifacts/phase22_mr/ | VERIFIED |
