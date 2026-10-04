# Lucia — Repository Documentation & Knowledge Architecture

> **Authoritative Information Architecture, Epistemic Hierarchy, and Context Projection System**  
> **Status:** `[CANONICAL REPOSITORY CANON]`  
> **Scope:** Repository-Wide Knowledge Architecture across All Historical, Active, and Future Phases  
> **Core Principle:** UNKNOWN MUST NEVER SILENTLY BECOME CERTAINTY

---

## 1. Executive Summary & Problem Formulation

### 1.1 The Knowledge Fragmentation Crisis
Across its developmental progression from Phase 1 (Core Affective Foundation) to Phase 23 (Continuous Substrate-Neutral Semantic Architecture), Lucia has accumulated extensive research specifications, mathematical proofs, experimental protocols, benchmark results, negative findings, architectural decision records (ADRs), and cognitive implementation code. 

As the complexity accelerated during Phase 22 (20 sub-study branches) and Phase 23 (sub-phases A through I, each spanning distinct research, contract, implementation, audit, fix, and regression cycles), the documentation topography fragmented across multiple disjoint roots:
- `docs/` (living canon, system overviews, and active ADR ledgers);
- `docs/PhaseDocs/` (historical phase specifications, evaluation reports, and research monographs);
- `docs/research/` (recently consolidated Phase 23 history, reviewer packs, and source maps);
- `evaluation_artifacts/` (186 markdown reports and diagnostic JSON dumps across 21 sub-phase folders);
- `tests/evaluation/` (40 markdown scaffolds and 300+ pytest experimental suites);
- `scratch/` (temporary synthesis notes, audit logs, and diagnostic scripts).

The operational defect is no longer simply:
> *"Where should this document go?"*

The fundamental architectural problem is:
> **How should Lucia manage knowledge, evidence, history, architecture, and AI-agent context as a continuously growing cognitive research system without losing provenance, canonical ownership, or epistemic integrity?**

### 1.2 Core Architectural Axiom: One Truth, Multiple Projections
Documentation is not a homogeneous pile of markdown files. A research hypothesis is not an architectural decision; an empirical benchmark measurement is not production runtime code; a 5-file reviewer context pack for an AI model is not an independent source of truth.

Lucia resolves fragmentation through a strict **Single-Source-of-Truth Projection Model**:
```text
                       ┌────────────────────────────┐
                       │     CANONICAL TRUTH        │
                       │   (Living System State)    │
                       └─────────────┬──────────────┘
                                     │
         ┌───────────────────────────┼───────────────────────────┐
         ▼                           ▼                           ▼
┌──────────────────┐       ┌──────────────────┐        ┌──────────────────┐
│ RESEARCH HISTORY │       │EVALUATION EVIDENCE│       │DECISION REGISTRY │
│  (Hypotheses &   │       │ (Raw Benchmarks, │        │   (Formal ADR    │
│ Negative Results)│       │  Ablations, Logs)│        │     Ledger)      │
└────────┬─────────┘       └─────────┬────────┘        └─────────┬────────┘
         │                           │                           │
         └───────────────────────────┼───────────────────────────┘
                                     │
                             CANONICAL INDEXES
                      (Phase & Document Registries,
                              Source Maps)
                                     │
                 ┌───────────────────┴───────────────────┐
                 ▼                                       ▼
       ┌───────────────────┐                   ┌───────────────────┐
       │  CIAH PROJECTION  │                   │  GEMINI / AGENTS  │
       │  (Curated ≤ 5     │                   │  (Complete Deep   │
       │   Review Files)   │                   │  Research Corpus) │
       └───────────────────┘                   └───────────────────┘
```
- **Different views are allowed.**
- **Different truths are strictly forbidden.**

---

## 2. The Seven Distinct Knowledge Classes

To establish clear ownership, every document and artifact in the repository belongs to exactly one primary **Knowledge Class**:

```text
┌────────────────────────────────────────────────────────────────────────┐
│                      LUCIA KNOWLEDGE TAXONOMY                          │
├────────────────────────────────────────────────────────────────────────┤
│ 1. Canonical Current Knowledge ── What is Lucia now?                   │
│ 2. Research History           ── What did Lucia investigate & learn?   │
│ 3. Evaluation Evidence        ── What empirical data was measured?     │
│ 4. Implementation History     ── What production code was committed?   │
│ 5. Architectural Decisions    ── Why were specific designs chosen?     │
│ 6. Historical / Superseded    ── What was historically believed/tried? │
│ 7. Agent / Research Context   ── Task-specific retrieval projections   │
└────────────────────────────────────────────────────────────────────────┘
```

### 2.1 Class 1: Canonical Current Knowledge
- **Core Question**: *What is Lucia now?*
- **Scope**: Authoritative living documents defining system identity, active cognitive architecture, runtime invariants, active REST API surface, and production component behaviors.
- **Canonical Files**:
  - [`docs/00_PROJECT_OVERVIEW.md`](file:///c:/Users/Lunafiah/Desktop/My_project/Lucia/docs/00_PROJECT_OVERVIEW.md) (System identity, 6-layer pipeline, subsystem health, milestone roadmap)
  - [`docs/ARCHITECTURE.md`](file:///c:/Users/Lunafiah/Desktop/My_project/Lucia/docs/ARCHITECTURE.md) (Technical architecture, mathematical mechanisms, concurrency rules)
  - [`docs/L1_INVARIANTS.md`](file:///c:/Users/Lunafiah/Desktop/My_project/Lucia/docs/L1_INVARIANTS.md) (Distilled non-negotiable invariant ledger)
  - [`AGENTS.md`](file:///c:/Users/Lunafiah/Desktop/My_project/Lucia/AGENTS.md) (Agent operational rules, lock discipline, epistemic boundaries)
  - [`README.md`](file:///c:/Users/Lunafiah/Desktop/My_project/Lucia/README.md) (Public front door)
  - [`docs/USER_MANUAL.md`](file:///c:/Users/Lunafiah/Desktop/My_project/Lucia/docs/USER_MANUAL.md) (User operations, setup guide)
- **Authority**: Highest active authority. Any statement in an older specification or research paper contradicting Class 1 is obsolete unless recorded in a formal conflict ledger.

### 2.2 Class 2: Research History
- **Core Question**: *What did Lucia investigate and learn?*
- **Scope**: Conceptual investigations, theoretical whitepapers, exploratory research proposals, mathematical derivations, literature analyses, and pre-registered hypotheses.
- **Mandatory Invariant**: **Preserve Uncertainty and Negative Evidence.**
  - Failed hypotheses (e.g., HDC pure dense vector superposition crosstalk in 22-SC, V-UMR memory degradation in 23-D, sentence embedding semantic loss in 23-C) are essential scientific evidence. They must **never** be deleted or rewritten to create a synthetic linear narrative.
- **Primary Locations**:
  - `docs/PhaseDocs/` (historical research specs Phase 1–22)
  - `docs/research/` (Phase 23 research specs, history consolidation)

### 2.3 Class 3: Evaluation Evidence
- **Core Question**: *What evidence exists?*
- **Scope**: Raw empirical outputs, benchmark results, falsification test runs, ablation comparisons, Monte Carlo parameter sweeps, latency profiling, and formal evaluation reports.
- **Mandatory Invariant**: **Evidence Must Not Be Flattened.**
  - A summary sentence (*"Candidate C4 was chosen"*) is not evidence. The underlying protocol, metrics, test fixtures, seeds, and quantitative tables must remain preserved and directly linkable.
- **Primary Locations**:
  - `evaluation_artifacts/` (formal evaluation reports, JSON benchmark manifests)
  - `tests/evaluation/` (executable evaluation scripts, experiment scaffolds, dataset fixtures)

### 2.4 Class 4: Implementation History
- **Core Question**: *What was actually built?*
- **Scope**: Production realization designs, implementation plans, task checklists, post-implementation audit reports, verification sign-offs, and commit ledgers.
- **Primary Locations**:
  - `docs/PhaseDocs/*/Phase_*_tasks.md`
  - `docs/PhaseDocs/*/*_PRODUCTION_REALIZATION_DESIGN.md`
  - `docs/PhaseDocs/*/*_ACCEPTANCE_REPORT.md`
  - Git commit history with SHA-256 commit hashes.

### 2.5 Class 5: Architectural Decisions
- **Core Question**: *Why did Lucia choose this?*
- **Scope**: Explicit, formal Architectural Decision Records (ADRs).
- **Mandatory Structure**:
  ```text
  Decision ID & Title
  ├── Status (ACCEPTED, PROMOTED, DRAFT, REJECTED, SUPERSEDED)
  ├── Context & Problem Statement
  ├── Evaluated Alternatives (Option A, Option B, etc.)
  ├── Empirical Evidence & Grounding
  ├── Rejected Alternatives & Rationales
  ├── Decision Statement
  └── Consequences & Verification Plan
  ```
- **Canonical Owner**: [`docs/ARCHITECTURE.md`](file:///c:/Users/Lunafiah/Desktop/My_project/Lucia/docs/ARCHITECTURE.md) §8 (ADR Ledger).

### 2.6 Class 6: Historical / Superseded Knowledge
- **Core Question**: *What was once valid or believed, but is no longer current?*
- **Scope**: Early draft specifications, superseded UI designs (Phase 3 desktop layout), obsolete parameter configurations (64-bit SDM pedagogical draft), replaced architectural frameworks.
- **Governance**: Historical artifacts must remain read-only and immutable. When superseded, they are explicitly tagged `[SUPERSEDED BY <Target>]` in registries rather than deleted.

### 2.7 Class 7: Agent & Research Context
- **Core Question**: *How should specific AI agents consume this knowledge efficiently?*
- **Scope**: Derived context packs, context routing indexes, summary projections, and reviewer digests.
- **Mandatory Invariant**: **Context Packs are Projections, Not Independent Truths.**
  - Context documents (e.g. Ciah reviewer pack files) must never introduce new facts or alter frozen decisions. They are read-only windows into Classes 1–5.
- **Primary Locations**:
  - [`docs/CONTEXT_INDEX.md`](file:///c:/Users/Lunafiah/Desktop/My_project/Lucia/docs/CONTEXT_INDEX.md) (Logical L0–L6 context routing)
  - `docs/research/P23_REVIEW_*.md` (5-file reviewer pack for Ciah)

---

## 3. Fundamental Architectural Invariants

The documentation and knowledge architecture strictly enforces four foundational invariants:

### 3.1 Invariant 1: Single Canonical Ownership
> **Every current architectural fact must have exactly one authoritative canonical owner.**

If a fact (e.g., *Coupled MT-LNN resting attractor coordinates*) appears in multiple places, all secondary instances must be direct markdown links, derived context projections, or explicitly marked historical quotes. When the canonical owner is updated, secondary references must not maintain an out-of-sync contradictory version.

### 3.2 Invariant 2: Unflattened Evidence Chains
> **Evidence must preserve its full provenance chain from claim to raw measurement.**

The architecture enforces the unbroken chain:
$$\text{Claim} \longrightarrow \text{Research Question} \longrightarrow \text{Experiment Protocol} \longrightarrow \text{Raw Measurements} \longrightarrow \text{Analysis} \longrightarrow \text{Decision (ADR)} \longrightarrow \text{Current State}$$
Where any link in the chain is missing or incomplete, the documentation must explicitly mark it as `MISSING PROVENANCE` or `UNPROVEN` rather than inventing a plausible link.

### 3.3 Invariant 3: Epistemic Integrity (`UNKNOWN != CERTAINTY`)
> **UNKNOWN MUST NEVER SILENTLY BECOME CERTAINTY.**

In both cognition and documentation:
- An unproven hypothesis must never be described as "validated" merely because unit tests pass.
- A failure of proof is an `UNKNOWN` state, not an affirmative `FALSE` or silent success.
- Negative results, inconclusive experiments (e.g., Phase 22 H1 Path C Gate 2 surprise compression), and unverified candidate boundaries must be prominently declared with formal epistemic status.

### 3.4 Invariant 4: Genesis Gate Immutability
> **Simulation != Activation. Development != Activation.**

`data/profile.json` (`{"is_onboarded": false}`) is a locked future gate. No documentation task, benchmark harness, simulation run, or test suite is ever authorized to modify onboarding status or treat the companion as activated during development.

---

## 4. Phase & Sub-Phase Topology Model

The documentation architecture natively supports four distinct phase organizational patterns without inventing ad-hoc directory conventions:

### Pattern A: Simple Linear Milestones (Phases 1–7, 10–15)
Phases that advanced directly from requirements to implementation:
```text
docs/PhaseDocs/lucia-phaseXX/
├── Phase_XX_requirements.md
├── Phase_XX_design.md
└── Phase_XX_tasks.md
```

### Pattern B: Multi-Artifact Integrated Milestones (Phases 8, 9, 16–21)
Phases featuring formal architecture decision gates, multi-stage integration, and rigorous promotion matrices:
```text
docs/PhaseDocs/lucia-phaseXX/
├── PHASE_XX_SPECIFICATION.md
├── PHASE_XX_EXPERIMENT_PLAN.md
├── PHASE_XX_RESULTS.md
├── PHASE_XX_PRODUCTION_REALIZATION_DESIGN.md
└── PHASE_XX_ACCEPTANCE_REPORT.md
```

### Pattern C: Massive Multi-Branch Exploratory Research (Phase 22)
A major research horizon encompassing 20 distinct sub-study tracks, parallel candidate evaluations, and extensive parameter sweeps:
- Master Synthesis: Single consolidated monograph (`PHASE_22_FINAL_REPORTS.md`).
- Sub-study Branches: Standardized sub-directories with uniform naming:
  ```text
  docs/PhaseDocs/Lucia-phase22-Epistemic_Foraging/evaluation_artifacts/phase22_<track>/
  ├── <track>_report.md
  ├── failure_analysis.md
  ├── language_report.md
  ├── stability_report.md
  └── final_report.md
  ```
- Executable Test Harnesses: Mirrored in `tests/evaluation/phase22_<track>/`.

### Pattern D: Multi-Stage Iterative Sub-Phase Cycle (Phase 23)
A complex phase decomposed into sequential sub-phases (P23-A through P23-I), where individual sub-phases undergo complete research, contract, production implementation, and freeze lifecycles:
```text
Phase 23 (Root Milestone)
├── P23-A: Semantic State Contract v0.2          [RESEARCH CONTRACT]
├── P23-B: Microbenchmark Spec & Baseline       [RESEARCH VALIDATED]
├── P23-C: Concept Formation Monograph          [RESEARCH VALIDATED]
├── P23-D: Substrate Evaluation Scaffold (EXP 01–06) [RESEARCH VALIDATED]
├── P23-E: Conservative Fortification Subsystem [VALIDATED / PRODUCTION IMPLEMENTED]
├── P23-F: Language Adapter Boundary Subsystem  [VALIDATED / PRODUCTION IMPLEMENTED]
├── P23-G: Cognitive Core Contract Subsystem    [VALIDATED / PRODUCTION IMPLEMENTED]
├── P23-H: Bounded Reasoning Kernel & JTMS      [VALIDATED / PRODUCTION IMPLEMENTED / FROZEN @ 3eef803]
└── P23-I: Concept-to-Reasoning Investigation   [RESEARCH & EVIDENCE CLOSURE COMPLETED — EVIDENCE STILL INSUFFICIENT — CONTRACT NOT FROZEN]
```

The transition from exploratory research to contract freeze strictly enforces the following gated progression:
```text
Research (Gemini)
      ↓
Gemini Final Research Report (Preliminary Recommendation: "Contract Transition Ready" [SUPERSEDED])
      ↓
Empirical Evidence Closure & Falsification Audit (P23-I_EVIDENCE_CLOSURE_AND_FALSIFICATION_REPORT.md)
      ↓
Research Completed + Evidence Closure Completed (Evidence Still Insufficient)
      ↓
Gate 23-I-EVAL (Tracks A, B, C: Referent Envelope, Concurrency Runtime, Epistemic Ingress)
      ↓
Ciah Epistemic & Architectural Review
      ↓
[Contract Freeze Decision]
      ↓
Implementation Authorization (User Gate)
```
A preliminary research recommendation such as "Contract Transition Ready" represents an **attributed research proposal (now superseded in P23-I by evidence closure)**, never an automatic authorization for production implementation or canonical freeze.

---

## 5. Universal Controlled Taxonomies

To eliminate ambiguous labels such as *"done"*, *"finished"*, *"final"*, and *"ready"*, Lucia mandates standardized status and authority vocabularies.

### 5.1 Standardized Document Status Taxonomy

| Status | Exact Definition | Permitted Mutations |
|---|---|---|
| `PLANNED` | Milestone or feature scheduled on the future roadmap. No specification or research underway. | Read/write planning |
| `RESEARCH` | Active theoretical, empirical, or benchmark investigation. No production code allowed. | Read/write research artifacts |
| `ACTIVE` | Currently being drafted, refined, or executed. | Read/write working artifacts |
| `IMPLEMENTED` | Production code has been authored in `src/core/` or `electron/`. | Scoped bug fixes & refactors |
| `VERIFIED` | Validated by comprehensive unit, property, regression, or falsification test suites. | Frozen; audited |
| `FROZEN` | Bit-exact freeze at a specific git commit (e.g. P23-H frozen at `3eef803`). No code mutations permitted. | Strictly Read-Only |
| `SUPERSEDED` | Previously accepted design that has been replaced by a newer ratified specification or ADR. | Read-Only with forward link |
| `REJECTED` | Proposed candidate or hypothesis disproven by evidence. Preserved as negative evidence. | Strictly Read-Only |
| `ARCHIVED` | Point-in-time snapshot preserved for historical provenance. | Strictly Read-Only |
| `LOCKED` | Gate intentionally locked until explicit governance authorization (e.g., Genesis Onboarding). | Strictly Read-Only |

### 5.2 Standardized Document Authority Taxonomy

| Authority Level | Definition | Representative Artifacts |
|---|---|---|
| `CANONICAL` | Authoritative active truth defining what Lucia currently considers true. | `00_PROJECT_OVERVIEW.md`, `ARCHITECTURE.md`, `L1_INVARIANTS.md` |
| `DECISION` | Formally ratified architectural decision record. | ADR-001 through ADR-028, ARCH-001 through ARCH-031 |
| `RESEARCH` | Research findings, literature monographs, and experimental interpretations. | `PHASE23_C_RAW_INPUT_CONCEPT_FORMATION_v0.1.md` |
| `EVIDENCE` | Direct empirical data, benchmark measurements, and falsification reports. | `P23H_CORE_REASONING_EVALUATION_REPORT.md` |
| `IMPLEMENTATION`| Detailed implementation designs and verification checklists. | `PHASE_21_PRODUCTION_REALIZATION_DESIGN.md` |
| `CONTEXT` | Derived retrieval artifacts and reviewer projection packs. | `docs/research/P23_REVIEW_*.md`, `CONTEXT_INDEX.md` |
| `HISTORICAL` | Preserved records of past milestones and legacy designs. | `docs/PhaseDocs/lucia-phase1-core/Phase_1_design.md` |

---

## 6. AI Agent Context Projections

Different AI agents have radically different context window sizes, cognitive roles, and operational mandates. Lucia rejects a "one-size-fits-all" context strategy in favor of **Role-Differentiated Projections**:

```text
                                CANONICAL KNOWLEDGE
                                         │
        ┌────────────────────────────────┼────────────────────────────────┐
        ▼                                ▼                                ▼
  CIAH PROJECTION               GEMINI / NOTEBOOKLM              ANTIGRAVITY CODING
  (Cognitive Reviewer)          (Deep Research Corpus)           (Execution Agent)
  • Strict ≤ 5 files            • Complete unflattened corpus    • Scoped L0–L6 routing
  • Executive context           • Raw benchmark outputs          • Targeted module focus
  • Evolution progression       • Full mathematical monographs   • Invariant verification
  • Epistemic boundaries        • Falsification histories        • Test execution suites
  • Preserved negatives         • Negative evidence archives     • Zero context saturation
```

### 6.1 Ciah Reviewer Pack (Strict $\le 5$ Files)
Ciah operates as the architectural auditor, reasoning challenger, and invariant reviewer. Ciah requires concise, high-density, authoritative synthesis without file flooding:
- **File 1: Executive Context**: System mission, roadmap position, current phase status, frozen commits.
- **File 2: Phase History**: Chronological progression, validated milestones, resolved pivots.
- **File 3: Architecture State & Boundaries**: 7-tier epistemic state of subsystems, active contracts, interface gaps.
- **File 4: Evidence & Negative Results**: Validated findings, falsified hypotheses, audit corrections.
- **File 5: Active Research Boundary**: Specific research question, falsification criteria, non-implementation boundary.

### 6.2 Gemini & NotebookLM (Deep Research Corpus)
Gemini and NotebookLM possess massive context windows capable of synthesizing thousands of pages. For these models:
- Provide the complete unflattened research corpus.
- Expose all sub-study final reports (`PHASE_22_FINAL_REPORTS.md`, `docs/PhaseDocs/**/evaluation_artifacts/**`).
- Retain complete raw benchmark JSON outputs, negative results, and multi-turn parameter sweeps.
- Preserve explicit links between hypotheses, experiment code, and empirical measurements.

### 6.3 Antigravity (Pair Programming & Execution Agent)
Antigravity executes disciplined, scoped code edits and test validation. Antigravity relies on **Minimal Sufficient Context Routing (L0–L6)** per [`docs/CONTEXT_INDEX.md`](file:///c:/Users/Lunafiah/Desktop/My_project/Lucia/docs/CONTEXT_INDEX.md):
- Never load historical specs during bug fixes.
- Load only target subsystem code + invariant ledger + relevant ADR section.
- Verify invariants before every commit.

---

## 7. The Documentation Lifecycle Pipeline

New concepts and mechanisms in Lucia must advance through a strictly gated, 8-stage documentation lifecycle:

```text
Stage 1: Research Hypothesis & Proposal
         (docs/research/ or docs/PhaseDocs/ — Status: RESEARCH)
                     │
                     ▼
Stage 2: Empirical Evaluation & Falsification
         (tests/evaluation/ & docs/PhaseDocs/**/evaluation_artifacts/ — Status: ACTIVE / EVIDENCE)
                     │
                     ▼
Stage 3: Evidence Synthesis & Candidate Disposition
         (Master Synthesis Report — Status: RESEARCH VALIDATED or REJECTED)
                     │
                     ▼
Stage 4: Architectural Decision Gate (ADR Drafting)
         (docs/ARCHITECTURE.md — Status: DRAFT / ARCHITECTURE APPROVED)
                     │
                     ▼
Stage 5: Production Realization Design & Authorization
         (Governance sign-off & User Authorization — Status: IMPLEMENTATION AUTHORIZED)
                     │
                     ▼
Stage 6: Scoped Production Implementation
         (src/core/** or electron/** — Status: IMPLEMENTED)
                     │
                     ▼
Stage 7: Audit, Epistemic Fix & Full Regression
         (tests/unit/, tests/property/, tests/evaluation/ — Status: VERIFIED)
                     │
                     ▼
Stage 8: Canonical State Synchronization & Freeze
         (docs/00_PROJECT_OVERVIEW.md, ARCHITECTURE.md, Registries — Status: FROZEN)
```

---

## 8. Scalability & Future Horizons (P24 through P30+)

The documentation architecture must scale seamlessly as Lucia expands across future milestones:
- **P24**: Affective Communication Adaptation
- **P25**: Temporal Embodiment & Social Feedback
- **P26**: Emergent Individuality & Autonomous Preferences
- **P27**: Personalized Individual Trajectory
- **Genesis Onboarding**: Solemn Awakening Ceremony (Locked Future Gate)

### 8.1 Scalability Guarantees
1. **Sub-Phase Uniformity**: Any future complex phase (e.g. Phase 24 having 20 sub-studies) will strictly utilize the Phase 22/23 sub-study directory structure and standardized report taxonomy, eliminating folder convention reinventing.
2. **Registry Decoupling**: All queries regarding phase status, document ownership, or component provenance resolve against centralized registries ([`docs/PHASE_REGISTRY.md`](file:///c:/Users/Lunafiah/Desktop/My_project/Lucia/docs/PHASE_REGISTRY.md), [`docs/DOCUMENT_REGISTRY.md`](file:///c:/Users/Lunafiah/Desktop/My_project/Lucia/docs/DOCUMENT_REGISTRY.md), [`docs/SOURCE_MAP.md`](file:///c:/Users/Lunafiah/Desktop/My_project/Lucia/docs/SOURCE_MAP.md)) rather than requiring whole-repository directory traversal.
3. **Epistemic Safety**: By keeping raw evaluation evidence strictly segregated from canonical living truths, the repository can ingest millions of data points without compromising the clarity of active system architecture.
