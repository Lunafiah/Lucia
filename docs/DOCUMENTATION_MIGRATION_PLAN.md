# Lucia — Documentation & Knowledge Architecture Migration Plan

> **Authoritative, Phased, Non-Destructive Migration Plan for Repository-Wide Knowledge Architecture**  
> **Status:** `[CANONICAL REPOSITORY MIGRATION PLAN]`  
> **Guiding Principle:** DISCOVER AND REGISTER BEFORE RESTRUCTURING — ZERO LOSS OF PROVENANCE

---

## 1. Executive Summary & Purpose

Over 23 phases of development, Lucia's documentation and evaluation evidence have expanded across multiple disjoint directories: `docs/`, `docs/PhaseDocs/`, `docs/research/`, `evaluation_artifacts/`, and `tests/evaluation/`. 

This document defines the **Safe, Phased Migration Strategy** to transition the repository from its current fragmented topology into the durable, scalable information architecture defined in [`docs/DOCUMENTATION_ARCHITECTURE.md`](file:///c:/Users/Lunafiah/Desktop/My_project/Lucia/docs/DOCUMENTATION_ARCHITECTURE.md).

Per Section 24 and 27 of the master task guidelines:
> **Do NOT perform destructive restructuring without prior review. The migration must advance through disciplined, auditable stages: Inventory $\to$ Classify $\to$ Assign Owner $\to$ Build Indexes $\to$ Resolve Conflicts $\to$ Update References $\to$ Move Safely $\to$ Verify Links $\to$ Freeze.**

---

## 2. Current vs. Target Topology Comparison

### 2.1 Current Documentation Topology
```text
Lucia/
├── docs/                                       # Core Canon & ADRs
│   ├── 00_PROJECT_OVERVIEW.md                  # Canonical overview & roadmap
│   ├── ARCHITECTURE.md                         # Technical architecture & ADR ledger
│   ├── CONTEXT_INDEX.md                        # Context retrieval map
│   ├── DOCUMENTATION_INDEX.md                  # Spec catalog
│   ├── L1_INVARIANTS.md                        # Distilled invariants
│   ├── USER_MANUAL.md                          # User guide
│   ├── research/                               # Phase 23 consolidated history & reviewer pack
│   └── specs/                                  # Historical specs (Phases 1–22)
│       ├── lucia-phase1-core/ ... lucia-phase18/
│       ├── Lucia-phase19-Multi_Timescale_Affective_Life/
│       ├── Lucia-phase20-Affective_Recollection/
│       ├── Lucia-phase21-Relational_Consolidation/
│       └── Lucia-phase22-Epistemic_Foraging/    # 49 research files
├── evaluation_artifacts/                       # 186 markdown reports & JSON manifests
│   ├── phase18/                                # Audio manifests & diagnostics
│   ├── phase22_alignment/ ... phase22_xr_real/ # 19 sub-phase folders
│   ├── phase23/, phase23e/, phase23f/, ...     # Phase 23 sub-phase evaluation reports
│   └── phase_context_v1/                       # Early context evaluation
├── tests/evaluation/                           # 40 markdown scaffolds & 300+ pytest suites
│   ├── evaluation_phase17/ ... phase21/        # Phase evaluation test runners
│   ├── evaluation_phase22/ & phase22_*         # Phase 22 test suites & fixtures
│   ├── evaluation_phase23d/                    # P23-D experiment scaffold (EXP 01–06)
│   └── phase23d/, phase23e/, phase23f/, ...    # P23 test suites
└── scratch/                                    # Diagnostic dumps, build wheels, notes
```

### 2.2 Target Durable Topology
The target topology establishes clean separation of concerns while preserving every historical artifact and empirical data point:

```text
Lucia/
├── docs/                                       # Living Canon, Registries & Governance
│   ├── 00_PROJECT_OVERVIEW.md                  # Living Project Truth & Subsystem Health Matrix
│   ├── ARCHITECTURE.md                         # Technical Architecture & ADR Ledger (ADR-001..034)
│   ├── L1_INVARIANTS.md                        # Master Invariant Ledger
│   ├── USER_MANUAL.md                          # Companion Setup & Desktop Operating Guide
│   ├── DOCUMENTATION_ARCHITECTURE.md           # Information Architecture & Taxonomies
│   ├── CONTEXT_ARCHITECTURE.md                 # Agent Projection Specification
│   ├── CONTEXT_INDEX.md                        # Agent L0–L6 Minimal Sufficient Routing
│   ├── PHASE_REGISTRY.md                       # Canonical Milestone & Sub-Phase Registry
│   ├── DOCUMENT_REGISTRY.md                    # Master Document Classification Catalog
│   ├── SOURCE_MAP.md                           # Repository-Wide Claim-to-Evidence Map
│   ├── DOCUMENTATION_CONFLICTS.md              # Historical Contradiction Ledger
│   ├── DOCUMENTATION_MIGRATION_PLAN.md         # This Document: Safe Migration Roadmap
│   ├── research/                               # Cross-Phase Reviewer Packs & Active Research
│   │   ├── P23_REVIEW_01_EXECUTIVE_CONTEXT.md  # Ciah Reviewer Pack File 1
│   │   ├── P23_REVIEW_02_PHASE_HISTORY.md      # Ciah Reviewer Pack File 2
│   │   ├── P23_REVIEW_03_ARCHITECTURE_STATE.md # Ciah Reviewer Pack File 3
│   │   ├── P23_REVIEW_04_EVIDENCE_AND_RESULTS.md # Ciah Reviewer Pack File 4
│   │   ├── P23_REVIEW_05_RESEARCH_BOUNDARY.md  # Ciah Reviewer Pack File 5
│   │   └── active/                             # Active Research Horizons (P23-I, P24, etc.)
│   └── specs/                                  # Canonical Milestone Specifications & Plans
│       ├── phase01-core/ ... phase22-epistemic/
│       └── phase23-semantic_architecture/      # Consolidated Phase 23 specs & monographs
├── evaluation_artifacts/                       # Persistent Empirical Evidence Archive
│   ├── phase18/                                # Longitudinal audio quality verification
│   ├── phase22/                                # Phase 22 Sub-study Reports (AL, CC, EKF, etc.)
│   └── phase23/                                # Phase 23 Sub-study Reports (P23-A through P23-H)
└── tests/evaluation/                           # Executable Evaluation Harnesses & Tests
    ├── phase17/ ... phase21/                   # Executable milestone benchmarks
    ├── phase22/                                # Executable Phase 22 harnesses & suites
    └── phase23/                                # Executable Phase 23 harnesses & falsifications
```

---

## 3. Five-Stage Phased Migration Roadmap

```text
┌────────────────────────────────────────────────────────────────────────┐
│                      MIGRATION STAGE PROGRESSION                       │
├────────────────────────────────────────────────────────────────────────┤
│ STAGE 0: Audit & Architecture Design          [COMPLETED IN THIS TASK] │
│ STAGE 1: Centralized Registries & Source Maps  [COMPLETED IN THIS TASK] │
│ STAGE 2: Safe Deduplication & Header Fixes     [NEXT — USER REVIEW]     │
│ STAGE 3: Phased Specification Relocation      [FUTURE SCHEDULED]       │
│ STAGE 4: Link Synchronization & Final Freeze  [FUTURE SCHEDULED]       │
└────────────────────────────────────────────────────────────────────────┘
```

### Stage 0: Audit & Architecture Design (COMPLETED)
- Conducted whole-repository inventory of all markdown, JSON, and evaluation files.
- Defined the 7 Knowledge Classes and universal status/authority taxonomies.
- Authored [`docs/DOCUMENTATION_ARCHITECTURE.md`](file:///c:/Users/Lunafiah/Desktop/My_project/Lucia/docs/DOCUMENTATION_ARCHITECTURE.md).
- Authored [`docs/CONTEXT_ARCHITECTURE.md`](file:///c:/Users/Lunafiah/Desktop/My_project/Lucia/docs/CONTEXT_ARCHITECTURE.md).
- Cataloged all historical contradictions in [`docs/DOCUMENTATION_CONFLICTS.md`](file:///c:/Users/Lunafiah/Desktop/My_project/Lucia/docs/DOCUMENTATION_CONFLICTS.md).

### Stage 1: Centralized Registries & Source Maps (COMPLETED)
- Authored master [`docs/PHASE_REGISTRY.md`](file:///c:/Users/Lunafiah/Desktop/My_project/Lucia/docs/PHASE_REGISTRY.md) covering P01 through P23-I, future horizons P24–P27, and Genesis gate.
- Authored master [`docs/DOCUMENT_REGISTRY.md`](file:///c:/Users/Lunafiah/Desktop/My_project/Lucia/docs/DOCUMENT_REGISTRY.md) classifying repository documents with metadata.
- Authored master [`docs/SOURCE_MAP.md`](file:///c:/Users/Lunafiah/Desktop/My_project/Lucia/docs/SOURCE_MAP.md) establishing unbroken claim-to-evidence provenance chains.
- Synchronized `AGENTS.md` to reflect active directories (`gating/` instead of `sensors/`) and reference the new architecture.

### Stage 2: Safe Deduplication, Header Fixes & Reference Validation (Next Immediate Step)
*Actions requiring zero physical directory relocation:*
1. **Fix Header Discrepancies**:
   - Update line 4 of `docs/PhaseDocs/Lucia-phase22-Epistemic_Foraging/PHASE_22_FINAL_REPORTS.md` to declare its true canonical path (`docs/PhaseDocs/...`).
2. **Deduplicate Point-to-Point Copies**:
   - Verify that test runners in `tests/evaluation/phase23/` can reference the authoritative documents in `evaluation_artifacts/phase23/` rather than maintaining duplicate copies of `PHASE23_C_RAW_INPUT_CONCEPT_FORMATION_v0.1.md`, `PHASE23_EMPIRICAL_SYNTHESIS_v0.1.md`, and `PHASE23_SEMANTIC_ARCHITECTURE_v0.1.md`.
3. **Formalize ADR-031 through ADR-034**:
   - In [`docs/ARCHITECTURE.md`](file:///c:/Users/Lunafiah/Desktop/My_project/Lucia/docs/ARCHITECTURE.md) §8, expand the narrative ADR ledger to document Phase 23 subsystems (Fortification, Language Adapter, Cognitive Core Contract, Reasoning Kernel) as formal ADRs, resolving Conflict `CF-007`.

### Stage 3: Phased Relocation & Topographical Harmonization (Scheduled Post-Review)
*Physical file moves executed exclusively via `git mv` to preserve git history:*
1. **Establish Phase 23 Specification Root**:
   - Create `docs/PhaseDocs/lucia-phase23-Semantic_Architecture/`.
   - Relocate Phase 23 research specifications, monographs, and acceptance designs from `docs/research/` and `evaluation_artifacts/` into this canonical folder.
   - Maintain `docs/research/` strictly for active research (`active/`) and AI context reviewer packs (`P23_REVIEW_*.md`).
2. **Harmonize Specification Directory Naming**:
   - Normalize directory names under `docs/PhaseDocs/`:
     - `lucia-phase7-UI_refractoring` $\to$ `lucia-phase7-ui_refactoring` (fix typo and lowercase).
     - `lucia-phase8-ISOLATION` $\to$ `lucia-phase8-isolation`.
     - `Lucia-phase19-Multi_Timescale_Affective_Life` $\to$ `lucia-phase19-multi_timescale_affective_life`.
     - `Lucia-phase20-Affective_Recollection` $\to$ `lucia-phase20-affective_recollection`.
     - `Lucia-phase21-Relational_Consolidation` $\to$ `lucia-phase21-relational_consolidation`.
     - `Lucia-phase22-Epistemic_Foraging` $\to$ `lucia-phase22-epistemic_foraging`.
3. **Sub-Phase Folder Namespace Disambiguation**:
   - Inside `evaluation_artifacts/`, group the 20 Phase 22 folders under `evaluation_artifacts/phase22/<track>/` or add sub-phase prefixes to bare `final_report.md` files (e.g. `sc_final_report.md`).

### Stage 4: Link Synchronization & Final Documentation Freeze
1. **Automated Link Audit**:
   - Execute a repository-wide regex link verification script to ensure every relative markdown link `[...](file:///...)` and `[...](./...)` resolves to a valid, existing file.
2. **Documentation Freeze Sign-Off**:
   - Verify that all canonical documents, registries, and source maps are completely synchronized.
   - Tag git commit with formal documentation audit freeze.

---

## 4. Safe vs. Unsafe Move Classification Matrix

To protect ongoing development and avoid breaking test runners, all proposed moves are classified by operational risk:

| Operation | Risk Level | Rationale | Execution Rule |
|---|---|---|---|
| **Authoring new architecture & registries in `docs/`** | `SAFE` | Non-destructive; creates new canonical truth without mutating existing files. | Authorized & Completed. |
| **Updating metadata headers (e.g. CF-002)** | `SAFE` | In-place text fix; zero link breakage. | Authorized for Stage 2. |
| **Creating `docs/PhaseDocs/lucia-phase23-Semantic_Architecture/`** | `SAFE` | Fills an obvious structural void; consolidates Phase 23 specs. | Execute via `git mv` in Stage 3. |
| **Deduplicating Markdown files in `tests/evaluation/phase23/`** | `LOW RISK` | Must verify test runners do not open these markdown files at runtime. | Verify with pytest before removal. |
| **Renaming `docs/PhaseDocs/` directories (casing & typo fixes)** | `MODERATE RISK`| Renaming folders breaks relative markdown links across dozens of files. | Requires automated link update script. |
| **Renaming or moving folders inside `tests/evaluation/`** | `HIGH RISK` | Python test runners, import statements, and fixtures depend on exact paths. | **DO NOT MOVE** without complete test suite audit. |
| **Deleting historical scratch files or negative reports** | `UNSAFE / FORBIDDEN` | Violates core invariant: negative evidence and historical provenance must never be deleted. | **STRICTLY PROHIBITED**. |

---

## 5. Preservation Strategy for Historical & Negative Evidence

Lucia's scientific value rests heavily on its documented negative results and failed hypotheses. The migration plan guarantees that:

1. **Negative Results Are Permanently Preserved**:
   - Phase 22 H1 Path C inconclusive benchmark results (`PHASE_22_H1_EXECUTION_REPORT_PATH_C.md`).
   - Phase 22 Gate 2 surprise compression diagnostics (`PHASE_22_H1_GATE2_COMPRESSION_DIAGNOSTIC.md`).
   - Phase 22-SC Candidate C3 pure dense HDC superposition crosstalk failure (`failure_analysis.md`).
   - Phase 23-C sentence embedding loss monograph section.
   - Phase 23-D V-UMR memory degradation and grounding failure ledger.
   - These files will **never** be deleted, merged away, or softened.
2. **Archival Integrity**:
   - Historical milestone specifications in `docs/PhaseDocs/lucia-phase1-core` through `phase6-refinement` represent immutable records of past engineering stages. They will not be rewritten to match modern Phase 23 idioms.
   - Where a historical spec contains an obsolete statement (e.g. 64-bit SDM address), the canonical owner is updated in `docs/ARCHITECTURE.md` §8.1, and the historical spec remains tagged `HISTORICAL`.

---

## 6. Verification & Governance Sign-Off Gate

Before any Stage 3 physical moves are executed:
1. **User Governance Approval**: The User as final decision-maker must review and authorize this migration plan.
2. **Zero Production Mutation**: Confirm `src/core/**` and `electron/**` have zero changes.
3. **Genesis Invariant Verification**: Confirm `data/profile.json` remains bit-exact `{"is_onboarded": false}`.
4. **P23-H Frozen State Verification**: Confirm Phase 23-H reasoning kernel remains frozen at commit `3eef803`.
5. **P23-I Research Isolation**: Confirm Phase 23-I remains strictly research-only with zero implementation code.
