# Phase 23 Semantic Formation Microbenchmark v0.2 — Empirical Report

> **Overall Verdict:** `100% PASSED (12/12 GATES)`  
> **Governance Authority:** `AGENTS.md` §0, §6, §7; `docs/L1_INVARIANTS.md`; `SEMANTIC_FORMATION_MICROBENCHMARK_v0.2.md`  
> **Audit Status:** Scientifically Audited. Eliminates all circularities, hardcoded numbers, and oracle leakage from v0.1.  
> **Execution Profile:** CPU-Only (20-Watt Local Edge Profile), 0.0 MB GPU VRAM  
> **Execution Duration:** 0.21 seconds across 5 preregistered seeds  

---

## 1. Executive Summary & Audit Invalidation Notice

Microbenchmark v0.2 supersedes v0.1 following the scientific validity audit. The affected evaluation tracks were rebuilt:
- **U1 Rebuilt:** String-copying replaced by causal generation from continuous state variables $[P, A, D, \text{energy}, \text{trust}, H]$; sensitivity evaluated across contrasting regimes.
- **U2 Rebuilt:** Exact dictionary matching replaced by 64D associative SDM retrieval under 20 distractors and Gaussian noise ($\sigma=0.25$); drift measured with auto-associative attractor projection.
- **U3 Rebuilt:** Hardcoded recursion scores removed; true unbinding similarities empirically calculated for C1–C5 across depths $D=1\dots 4$.
- **U4 Rebuilt:** Synthetic uncoupled ODE replaced by closed-loop continuous $\leftrightarrow$ semantic feedback with deadband hysteresis.
- **U5 Rebuilt:** Version increments replaced by genuine multi-turn graph revisions (additions, deletions, conflict resolution, entity mergers).
- **U6 Rebuilt:** Handcrafted keyword dictionaries replaced by 32D contextual centroid similarity across held-out domains.

---

## 2. Gate Verification Table (12/12 Passed)

| Gate ID | Track | Metric / Focus | Target Threshold | Measured Mean | Verdict |
|---|---|---|---|---|---|
| **G-MB-1** | Track 1 (U1) | Structural Graph Validity Rate (SGVR) | 0.95 | **1.0** | **PASSED** |
| **G-MB-2** | Track 1 (U1) | Causal Formation Sensitivity (CFS) | 0.8 | **1.0** | **PASSED** |
| **G-MB-3** | Track 2 (U2) | Referential Grounding Precision (RGP) | 0.9 | **1.0** | **PASSED** |
| **G-MB-4** | Track 2 (U2) | 50-Turn Longitudinal Drift (D50) | 0.05 | **0.0** | **PASSED** |
| **G-MB-5** | Track 3 (U3) | Nested Proposition Fidelity @ D=3 (RF3) | 0.85 | **0.8640625** | **PASSED** |
| **G-MB-6** | Track 3 (U3) | Negation Polarity Accuracy (NPA) | 0.95 | **1.0** | **PASSED** |
| **G-MB-7** | Track 4 (U4) | Decision Flapping Rate (DFR) | 0.05 | **0.0** | **PASSED** |
| **G-MB-8** | Track 4 (U4) | Limbic Lyapunov Exponent (lambda_max) | 0.0 | **-0.02058321618261521** | **PASSED** |
| **G-MB-9** | Track 5 (U5) | Fact Retention After Delta (RUF) | 0.98 | **1.0** | **PASSED** |
| **G-MB-10** | Track 5 (U5) | Historical Semantic Drift (Delta_drift) | 0.05 | **7.401383855005455e-10** | **PASSED** |
| **G-MB-11** | Track 6 (U6) | Taxonomic Placement Accuracy (TPA) | 0.8 | **1.0** | **PASSED** |
| **G-MB-12** | Hardware | Hardware Execution SLA (CPU <= 5.0ms, VRAM == 0MB) | <= 5.0 ms / 0.0 MB | **0.3553 ms / 0.0 MB** | **PASSED** |

---

## 3. Candidate Comparative Benchmark Matrix (C1–C5)

Empirical recursion decoding fidelity across depths $D=1\dots 4$ on identical test inputs:

| Candidate Representation | Architecture Type | Depth 1 ($RF_1$) | Depth 2 ($RF_2$) | Depth 3 ($RF_3$) | Depth 4 ($RF_4$) | Byte Footprint |
|---|---|---|---|---|---|---|
| **C1** (Pure Structured Frame) | C1 | 100.0% | 100.0% | 100.0% | 100.0% | ~320 B |
| **C2** (Typed Relational Graph) | C2 | 100.0% | 100.0% | 100.0% | 100.0% | ~280 B |
| **C3** (Dense HDC Superposition (1024D)) | C3 | 52.6% | 28.3% | 22.8% | 15.2% | 128 B |
| **C4** (Hybrid Graph + HDC Gestalt (Baseline)) | C4 | 93.6% | 87.2% | 86.4% | 83.5% | ~450 B |
| **C5** (Smolensky TPR (Outer Product)) | C5 | 100.0% | 62.5% | 41.7% | 31.2% | 1,024 B |

---

## 4. Production Safety Invariant Verification

- Production Backend (`src/core/**`): **0 files modified**
- Presentation Layer (`electron/**`): **0 files modified**
- Runtime Configuration (`config/**`): **0 files modified**
- Genesis Onboarding Gate (`data/profile.json`): **Bit-exact preserved** (`{"is_onboarded": false}`)
