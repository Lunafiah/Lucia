# Phase 23-D — Language-Independent Semantic Architecture Evaluation Scaffold

> **Document Type:** Research Evaluation Scaffold & Falsifiable Testing Protocol  
> **Status:** `[RESEARCH SPECIFICATION / PRE-IMPLEMENTATION]`  
> **Governance:** Isolated under `evaluation/evaluation_phase23d/`; Zero production mutation; Genesis onboarding locked (`data/profile.json` invariant preserved).  
> **Predecessor Milestones:** Phase 22-SC (`[RESEARCH VALIDATED]`), Phase 23-C Master Monograph (`PHASE23_C_RAW_INPUT_CONCEPT_FORMATION_v0.1.md`)  
> **Primary Objective:** Convert Phase 23-D research proposals into an empirically falsifiable evaluation protocol without modifying production code.

---

## 1. Executive Summary & Purpose

Phase 23-D investigates the language-independent conceptual substrate for Lucia. The goal of this phase is to establish whether a structured, grounded semantic representation can support continuous cognitive coupling, cross-lingual equivalence across English (EN), Vietnamese (VI), and Japanese (JA), discourse reference with zero-anaphora, non-monotonic belief revision, and long-term memory scaling on edge hardware—all without requiring a Large Language Model (LLM) or natural-language token sequence as a cognitive substrate.

This directory (`evaluation/evaluation_phase23d/`) contains the complete **evaluation scaffold and protocol** for Phase 23-D. In strict adherence to `AGENTS.md` §0, §6, and §7, **no production code is modified in this stage**. All architectural candidates, performance envelopes, and structural properties are treated as **falsifiable hypotheses**, not established facts.

```text
┌────────────────────────────────────────────────────────────────────────────────────────┐
│                        PHASE 23-D EVALUATION PIPELINE GOVERNANCE                       │
├────────────────────────────────────────────────────────────────────────────────────────┤
│                                                                                        │
│   Phase 23-C Working Baseline (C4: Graph + HDC Gestalt)                                │
│                     │                                                                  │
│                     ▼                                                                  │
│   Phase 23-D Evaluation Scaffold (evaluation/evaluation_phase23d/)                     │
│   ├── Candidate Architectural Specifications (UMR-TPG, V-UMR, DRS-Graph)               │
│   ├── Formal Experiment Matrix (6 Scientific Tracks)                                   │
│   └── Multi-Metric Evaluation Framework (SQI, Functional Equivalence, Latency SLA)     │
│                     │                                                                  │
│                     ▼                                                                  │
│   Empirical Benchmarking & Falsification (Isolated in Test Harness)                    │
│   ├── [PASS] -> Architecture Gate Proposal (docs/specs/...)                            │
│   └── [FAIL / REJECT] -> Hypothesis Falsification & Architectural Boundary Preserved  │
│                                                                                        │
│   PRODUCTION RUNTIME (src/core/**) IS UNTOUCHED DURING THIS STAGE                      │
└────────────────────────────────────────────────────────────────────────────────────────┘
```

---

## 2. Directory Structure & Document Navigation

The evaluation scaffold is organized into the following modular documents and experiment protocols:

```text
evaluation/evaluation_phase23d/
├── README.md                                  # This document: Executive overview and governance
├── research_baseline.md                       # Synthesis of P22-SC and P23-C findings and empirical constraints
├── candidate_spec.md                          # Detailed formal specs for UMR-TPG, V-UMR, and DRS-Graph
├── experiment_matrix.md                       # Comprehensive 6-experiment comparative matrix
├── metrics.md                                 # Mathematical definitions of metrics (SQI, alignment, scaling)
├── experiment_01_compositionality/            # Track 1: Compositionality & Recursion Depth
│   └── README.md
├── experiment_02_cross_lingual/               # Track 2: Cross-Lingual Convergence (EN, VI, JA)
│   └── README.md
├── experiment_03_coreference/                 # Track 3: Reference & Zero Anaphora Resolution
│   └── README.md
├── experiment_04_belief_revision/             # Track 4: Contradiction & Non-Monotonic Belief Revision
│   └── README.md
├── experiment_05_scaling/                     # Track 5: Long-Term Memory Scaling & 20W Hardware Feasibility
│   └── README.md
└── experiment_06_multimodal_grounding/        # Track 6: Multimodal Sensor Grounding & Embodiment
    └── README.md
```

---

## 3. Evaluated Candidate Architectures

Three core architectures are evaluated under identical conditions across all tracks:

| Role | Candidate Name | Core Substrate Paradigm | Hypothesized Strengths | Primary Hypothesized Risk |
|---|---|---|---|---|
| **Primary** | **UMR-TPG** | Universal Meaning Representation over Typed Property Graph | Deep recursion, language-independent roles, deterministic graph navigation | Pointer chasing overhead; lack of intrinsic metric similarity |
| **Secondary** | **V-UMR** | Vector-Augmented Universal Meaning Representation | Native metric distance for associative search coupled with structured graph | Dual-state synchronization overhead; memory footprint |
| **Control** | **DRS-Graph** | Discourse Representation Structure Graph (DRT-based) | Classical logical scoping, well-defined truth conditions | Clunky representation for continuous relational nuance; parsing complexity |

> [!IMPORTANT]
> **Auxiliary Associative Substrates (HDC/VSA & TPR):**  
> Hyperdimensional Computing (HDC/VSA) and compressed Tensor Product Representations (TPR) **are NOT primary persistent substrates**. Phase 22-SC and Phase 23-C proved that pure dense hypervectors collapse under nested recursion ($N > 4, D > 2$). They are retained strictly as **auxiliary associative indexing mechanisms** or short-term binding baselines.

---

## 4. Methodological Invariants & Guardrails

When executing or developing evaluations within this scaffold, the following rules are non-negotiable:

1. **Rejection of Graph Isomorphism:**  
   Natural language paraphrases, syntactic variations, and cross-lingual realizations do not produce isomorphic graph topologies. Semantic equivalence **must never be evaluated via graph isomorphism**. Equivalence is evaluated strictly via **Functional Equivalence**, **Thematic Role Parity**, and the **Semantic Quality Index (SQI)**.
2. **Engineering Claims Are Hypotheses, Not Facts:**  
   Any claims regarding RAM budgets (e.g. $\le 200\text{ MB}$), throughput, query latency (e.g. $\le 5.0\text{ ms}$), or suitability for 20W edge CPU execution are **engineering hypotheses to be benchmarked**, not verified constants.
3. **No Speculative Threshold Inflation:**  
   If a research finding lacks an established empirical threshold, it must be explicitly marked as **`[Open / Unverified]`**. Agents and researchers must not invent arbitrary numerical gates without prior empirical justification.
4. **Absolute Production Isolation:**  
   No files in `src/core/`, `electron/`, `config/`, or `data/` may be altered. The Genesis Onboarding Gate (`data/profile.json` with `is_onboarded: false`) remains locked.
