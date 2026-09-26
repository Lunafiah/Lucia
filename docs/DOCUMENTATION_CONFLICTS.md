# Lucia — Documentation & Knowledge Architecture Conflict Ledger

> **Canonical Ledger of Historical Contradictions, Topographical Discrepancies, and Epistemic Inconsistencies**  
> **Status:** `[CANONICAL REPOSITORY LEDGER]`  
> **Governing Invariant:** NEVER SILENTLY RESOLVE CONFLICTS — RECORD, CLASSIFY, AND MAP EXPLICITLY

---

## 1. Executive Summary & Conflict Management Protocol

During the comprehensive whole-repository documentation and knowledge architecture audit conducted in September 2026, nine substantive contradictions, topographical dislocations, and numbering discrepancies were identified across `docs/`, `docs/specs/`, `docs/research/`, `evaluation_artifacts/`, and `tests/evaluation/`.

Per the Core Epistemic Invariant:
> **UNKNOWN MUST NEVER SILENTLY BECOME CERTAINTY.**

This ledger records every discovered contradiction, traces its probable historical chronology, assesses its operational risk, and provides an authoritative recommended resolution without silently rewriting history.

```text
┌────────────────────────────────────────────────────────────────────────┐
│                        CONFLICT LEDGER SUMMARY                         │
├────────────────────────────────────────────────────────────────────────┤
│ CF-001: Roadmap Numbering & Milestone Naming Disparity                 │
│ CF-002: Location Header Disparity for Phase 22 Master Corpus           │
│ CF-003: Structural Absence of Phase 23 in docs/specs/                  │
│ CF-004: Parallel Dual Evaluation Trees (evaluation_artifacts vs tests) │
│ CF-005: High-Frequency Filename Collisions Across Sub-Study Branches  │
│ CF-006: Exact Point-to-Point Duplicate Files Across Directory Roots   │
│ CF-007: ADR Numbering Scheme vs Architecture Changelog Divergence      │
│ CF-008: Inconsistent Directory Casing & Typographic Error in specs/   │
│ CF-009: Stale Codebase Path Reference in AGENTS.md (sensors vs gating) │
└────────────────────────────────────────────────────────────────────────┘
```

---

## 2. Detailed Conflict Records

### CF-001: Roadmap Numbering & Milestone Naming Disparity
- **Conflict ID**: `CF-001`
- **Conflict Title**: Divergence in Post-Phase 23 Milestone Numbering and Phase 22/23 Titles
- **Sources**:
  1. *User Task Prompt (§2)*:
     - P22 — Active Inference & Epistemic Foraging
     - P23 — Feasible Asymmetric / Token-Free Continuous Communication Architecture
     - P24 — Affective Communication Adaptation
     - P25 — Temporal Embodiment & Social Feedback
     - P26 — Emergent Individuality & Autonomous Preferences
     - P27 — Personalized Individual Trajectory
  2. *Canonical Living Canon ([`docs/00_PROJECT_OVERVIEW.md`](file:///c:/Users/Lunafiah/Desktop/My_project/Lucia/docs/00_PROJECT_OVERVIEW.md) §7)*:
     - P22 — Substrate-Neutral Semantic Conditioning & Relational Cognition Study
     - P23 — Semantic Formation, Evaluation & Fortification
     - P24 — Temporal Embodiment & Social Feedback
     - P25 — Emergent Individuality & Autonomous Preferences
     - P26 — Personalized Individual Trajectory
  3. *Filesystem Names*:
     - `docs/specs/Lucia-phase22-Epistemic_Foraging/`
- **Nature of Contradiction**: 
  - There is a 1-index phase shift in future horizons: the User Prompt roadmap places *Affective Communication Adaptation* at P24 and shifts *Temporal Embodiment* to P25 (running through P27), whereas `docs/00_PROJECT_OVERVIEW.md` places *Temporal Embodiment* at P24 (running through P26).
  - Phase 22 has dual titles: "Active Inference & Epistemic Foraging" vs. "Substrate-Neutral Semantic Conditioning & Relational Cognition Study".
- **Likely Chronology**:
  - Phase 22 began as an investigation into Active Inference & Epistemic Foraging (H1). As the 20 sub-study branches unfolded, the investigation discovered that the primary cognitive bottleneck was *substrate-neutral relational conditioning* (22-SC). The folder retained the original title `Lucia-phase22-Epistemic_Foraging/`, while `00_PROJECT_OVERVIEW.md` was updated to reflect the scientific outcome.
  - The Prompt roadmap preserves the original long-term conceptual vision where an explicit "Affective Communication Adaptation" phase precedes embodiment.
- **Operational Risk**: Low for active code; moderate for cross-agent communication if an agent references P24 meaning "Communication Adaptation" while another references P24 meaning "Temporal Embodiment".
- **Resolution Status**: `RECOMMENDED_RESOLUTION`
- **Recommended Resolution**:
  - Formally harmonize the roadmap in [`docs/PHASE_REGISTRY.md`](file:///c:/Users/Lunafiah/Desktop/My_project/Lucia/docs/PHASE_REGISTRY.md) to explicitly map both nomenclatures:
    - Phase 22: "Substrate-Neutral Semantic Conditioning & Epistemic Foraging" (subsuming H1 and 22-SC).
    - Phase 23: "Continuous Substrate-Neutral Semantic Architecture" (subsuming concept formation and formal reasoning).
    - Phase 24: "Affective Communication Adaptation".
    - Phase 25: "Temporal Embodiment & Social Feedback".
    - Phase 26: "Emergent Individuality & Autonomous Preferences".
    - Phase 27: "Personalized Individual Trajectory".
    - Gate 28: First Activation (Genesis Onboarding).

---

### CF-002: Location Header Disparity for Phase 22 Master Corpus
- **Conflict ID**: `CF-002`
- **Conflict Title**: Internal Metadata Header Declares Incorrect File Location
- **Sources**:
  1. Header of [`docs/specs/Lucia-phase22-Epistemic_Foraging/PHASE_22_FINAL_REPORTS.md`](file:///c:/Users/Lunafiah/Desktop/My_project/Lucia/docs/specs/Lucia-phase22-Epistemic_Foraging/PHASE_22_FINAL_REPORTS.md) Line 4:
     ```markdown
     > **Permanent Location:** `evaluation_artifacts/PHASE_22_FINAL_REPORTS.md`
     ```
  2. Filesystem reality:
     - File exists at `docs/specs/Lucia-phase22-Epistemic_Foraging/PHASE_22_FINAL_REPORTS.md`.
     - File does NOT exist at `evaluation_artifacts/PHASE_22_FINAL_REPORTS.md`.
- **Nature of Contradiction**: Internal header contradicts actual physical path in repository.
- **Likely Chronology**: Authored during the closure of Phase 22 when the compilation was initially planned for `evaluation_artifacts/`, but governance rules dictated that specifications belong in `docs/specs/`.
- **Operational Risk**: Low; can mislead automated crawlers checking header metadata.
- **Resolution Status**: `RECOMMENDED_RESOLUTION`
- **Recommended Resolution**: Update line 4 of `docs/specs/Lucia-phase22-Epistemic_Foraging/PHASE_22_FINAL_REPORTS.md` to state its true location: `docs/specs/Lucia-phase22-Epistemic_Foraging/PHASE_22_FINAL_REPORTS.md`.

---

### CF-003: Structural Absence of Phase 23 in `docs/specs/`
- **Conflict ID**: `CF-003`
- **Conflict Title**: Phase 23 Has No Dedicated Milestone Directory Under `docs/specs/`
- **Sources**:
  1. `docs/specs/` contains directories for all prior milestones:
     - `lucia-phase1-core` through `lucia-phase18-Human_Longitudinal_Validation`
     - `Lucia-phase19-Multi_Timescale_Affective_Life` through `Lucia-phase22-Epistemic_Foraging`
  2. Phase 23 documents are scattered across:
     - `docs/research/` (9 files)
     - `evaluation_artifacts/phase23*` (12 files)
     - `tests/evaluation/phase23*` (26 files)
- **Nature of Contradiction**: Broken repository topology pattern. An engineer or agent inspecting `docs/specs/` would conclude that Phase 23 was never specified.
- **Likely Chronology**: In commit `3f6326a`, Phase 23 research history and reviewer packs were consolidated directly into `docs/research/` to prepare for Phase 23-I, without back-porting the Phase 23 milestone folder into `docs/specs/`.
- **Operational Risk**: High for navigation and discoverability.
- **Resolution Status**: `RECOMMENDED_RESOLUTION`
- **Recommended Resolution**: Schedule non-destructive migration in Stage 2 of `docs/DOCUMENTATION_MIGRATION_PLAN.md` to establish `docs/specs/lucia-phase23-Semantic_Architecture/` consolidating Phase 23 specifications, monographs, and acceptance reports.

---

### CF-004: Parallel Dual Evaluation Trees (`evaluation_artifacts/` vs `tests/evaluation/`)
- **Conflict ID**: `CF-004`
- **Conflict Title**: Disjoint Coexistence of Two Separate Evaluation Directory Trees
- **Sources**:
  1. `AGENTS.md` §3.3 (Line 157):
     ```markdown
     3. Put all phase evaluation artifacts in tests/evaluation/phaseXX/ under the shared tests/evaluation/ parent.
     ```
  2. Actual repository reality:
     - `evaluation_artifacts/` contains 186 markdown reports and diagnostic JSON dumps across 21 folders.
     - `tests/evaluation/` contains 40 markdown scaffolds and 300+ pytest experimental suites across 20+ folders.
- **Nature of Contradiction**: Direct violation of the written instruction in `AGENTS.md`. The repository has two parallel trees representing evaluation.
- **Likely Chronology**: When benchmark runs began generating large numbers of narrative markdown reports and raw telemetry dumps in Phase 22, engineers felt that cluttering `tests/evaluation/` with hundreds of non-test markdown files interfered with test runners and IDE navigators, creating `evaluation_artifacts/` as a parallel data store.
- **Operational Risk**: High. Agents are uncertain whether evaluation evidence lives in `tests/evaluation/` or `evaluation_artifacts/`.
- **Resolution Status**: `RECOMMENDED_RESOLUTION`
- **Recommended Resolution**: Formally ratify the functional separation in [`docs/DOCUMENTATION_ARCHITECTURE.md`](file:///c:/Users/Lunafiah/Desktop/My_project/Lucia/docs/DOCUMENTATION_ARCHITECTURE.md):
  - `tests/evaluation/`: Owns executable test code, pytest harnesses, simulation environments, and dataset fixtures.
  - `evaluation_artifacts/`: Owns persistent markdown evaluation reports, benchmark result JSONs, and diagnostic evidence dumps.
  - Update `AGENTS.md` §3.3 to explicitly reflect this ratified functional distinction.

---

### CF-005: High-Frequency Filename Collisions Across Sub-Study Branches
- **Conflict ID**: `CF-005`
- **Conflict Title**: Identical Filenames Repeated Across 14 Distinct Sub-Study Directories
- **Sources**:
  - `final_report.md` exists in 14 sub-directories of `evaluation_artifacts/` (e.g. `phase22_sc/final_report.md`, `phase22_cc/final_report.md`, `phase22_rg/final_report.md`, `phase22_anchor/final_report.md`, etc.).
  - `failure_analysis.md` exists in 11 sub-directories.
  - `language_report.md` exists in 6 sub-directories.
  - `stability_report.md` exists in 4 sub-directories.
  - In `docs/DOCUMENTATION_INDEX.md`, these were linked using the bare filename: `[`final_report.md`](file:///...)`.
- **Nature of Contradiction**: Ambiguous link text and search collisions. When an agent or human searches for `final_report.md`, 14 matches appear with zero contextual differentiation.
- **Likely Chronology**: A standardized document template was adopted for each sub-study in Phase 22, which worked well within isolated sub-directories but created severe repository-wide namespace pollution.
- **Operational Risk**: Moderate. Search tools and human readers cannot differentiate reports without inspecting full directory paths.
- **Resolution Status**: `RECOMMENDED_RESOLUTION`
- **Recommended Resolution**: In [`docs/DOCUMENTATION_INDEX.md`](file:///c:/Users/Lunafiah/Desktop/My_project/Lucia/docs/DOCUMENTATION_INDEX.md) and [`docs/DOCUMENT_REGISTRY.md`](file:///c:/Users/Lunafiah/Desktop/My_project/Lucia/docs/DOCUMENT_REGISTRY.md), always display qualified labels (e.g. `Phase 22-SC Final Report`) and avoid bare filename links.

---

### CF-006: Exact Point-to-Point Duplicate Files Across Directory Roots
- **Conflict ID**: `CF-006`
- **Conflict Title**: Exact SHA-256 Duplicate Markdown & JSON Files Maintained in Multiple Trees
- **Sources**:
  - `evaluation_artifacts/phase23/PHASE23_C_RAW_INPUT_CONCEPT_FORMATION_v0.1.md` == `tests/evaluation/phase23/PHASE23_C_RAW_INPUT_CONCEPT_FORMATION_v0.1.md` (`342825a762fe`)
  - `evaluation_artifacts/phase23/PHASE23_EMPIRICAL_SYNTHESIS_v0.1.md` == `tests/evaluation/phase23/PHASE23_EMPIRICAL_SYNTHESIS_v0.1.md` (`6293be100c88`)
  - `evaluation_artifacts/phase23/PHASE23_SEMANTIC_ARCHITECTURE_v0.1.md` == `tests/evaluation/phase23/PHASE23_SEMANTIC_ARCHITECTURE_v0.1.md` (`41c80f6f27f5`)
  - `docs/specs/Lucia-phase22-Epistemic_Foraging/PHASE_22_H1_R3_POLICY_MECHANISMS_STUDY.md` == `tests/evaluation/evaluation_phase22/results/h1_r3_policy_mechanisms/PHASE_22_H1_R3_POLICY_MECHANISMS_STUDY.md` (`f766aba86f8e`)
  - `docs/specs/Lucia-phase22-Epistemic_Foraging/PHASE_22_H1_R3_PROBABILISTIC_POLICY_STUDY.md` == `tests/evaluation/evaluation_phase22/results/h1_r3_probabilistic_policy/PHASE_22_H1_R3_PROBABILISTIC_POLICY_STUDY.md` (`c1048f16dd97`)
  - `docs/specs/lucia-phase18-Human_Longitudinal_Validation/results/audiovisual_manifest.json` == `evaluation_artifacts/phase18/manifests/audiovisual_manifest.json` (`2b7f12f65177`)
- **Nature of Contradiction**: Point-to-point duplication. Multiple copies of identical specifications and reports exist under different trees.
- **Likely Chronology**: During test suite execution, files were copied into test fixture directories so that local scripts could load them relative to their working directory.
- **Operational Risk**: High risk of silent drift if one copy is edited while the other remains stale.
- **Resolution Status**: `RECOMMENDED_RESOLUTION`
- **Recommended Resolution**: Explicitly designate canonical ownership in [`docs/DOCUMENT_REGISTRY.md`](file:///c:/Users/Lunafiah/Desktop/My_project/Lucia/docs/DOCUMENT_REGISTRY.md). In Stage 2 of the Migration Plan, replace copies in test trees with direct relative paths or read-only references.

---

### CF-007: ADR Numbering Scheme vs Architecture Changelog Divergence
- **Conflict ID**: `CF-007`
- **Conflict Title**: Collision Between Formal ADR Numbers and ARCH Numbers in Changelog
- **Sources**:
  1. `docs/ARCHITECTURE.md` §8 documents formal Architectural Decision Records as **ADR-001 through ADR-028**, followed by **DRAFT ADR-029** and **DRAFT ADR-030**.
  2. `docs/ARCHITECTURE.md` §8.2 documents the Architecture Change Log using **ARCH-001 through ARCH-031**, where:
     - `ARCH-028` = Phase 23-E Fortification Subsystem
     - `ARCH-029` = Phase 23-F Language Adapter Boundary
     - `ARCH-030` = Phase 23-G Cognitive Core Contract
     - `ARCH-031` = Phase 23-H Bounded Goal-Directed Reasoning Kernel & JTMS
  3. Notice the collision:
     - Formal `ADR-028` = Phase 21 Long-Term Relational Consolidation
     - Changelog `ARCH-028` = Phase 23-E Conservative Semantic Fortification
- **Nature of Contradiction**: High potential for confusion. An engineer citing "ADR-028" could mean Phase 21 Relational Consolidation or Phase 23-E Semantic Fortification depending on whether they look at §8.1 or §8.2.
- **Likely Chronology**: Formal narrative ADR writing paused after Phase 21/22. When Phase 23 implemented four critical subsystems (P23-E, P23-F, P23-G, P23-H), they were logged directly into the §8.2 Architecture Change Log as ARCH-028..031 instead of creating narrative ADR sections ADR-031..034.
- **Operational Risk**: Moderate; causes confusion during architectural reviews.
- **Resolution Status**: `RECOMMENDED_RESOLUTION`
- **Recommended Resolution**: In [`docs/ARCHITECTURE.md`](file:///c:/Users/Lunafiah/Desktop/My_project/Lucia/docs/ARCHITECTURE.md), expand Section 8 to formally promote ARCH-028 through ARCH-031 to narrative ADRs:
  - `ADR-031`: Conservative Semantic Fortification Across Session Boundaries (Phase 23-E)
  - `ADR-032`: Language Adapter Boundary & Semantic Substrate Contract (Phase 23-F)
  - `ADR-033`: Semantic Substrate → Cognitive Core Contract (Phase 23-G)
  - `ADR-034`: Bounded Goal-Directed Reasoning Kernel & JTMS (Phase 23-H)
  - Re-number the §8.2 change log table to match.

---

### CF-008: Inconsistent Directory Casing & Typographic Error in `docs/specs/`
- **Conflict ID**: `CF-008`
- **Conflict Title**: Inconsistent Directory Naming Conventions and Spelling Errors
- **Sources**:
  - `docs/specs/lucia-phase1-core` (lowercase)
  - `docs/specs/lucia-phase7-UI_refractoring` (spelling error: `refractoring` instead of `refactoring`)
  - `docs/specs/lucia-phase8-ISOLATION` (uppercase `ISOLATION`)
  - `docs/specs/Lucia-phase19-Multi_Timescale_Affective_Life` (capitalized `Lucia-`)
  - `docs/specs/Lucia-phase22-Epistemic_Foraging` (capitalized `Lucia-`)
- **Nature of Contradiction**: Inconsistent casing can cause breaking path failures on case-sensitive operating systems (Linux / CI/CD environments). The spelling error `refractoring` is visible and unprofessional.
- **Likely Chronology**: Organic creation by different contributors over months without path linting.
- **Operational Risk**: Moderate for Linux deployment / automated CI pipelines.
- **Resolution Status**: `RECOMMENDED_RESOLUTION`
- **Recommended Resolution**: Standardize directory naming under the Migration Plan (Stage 3): `lucia-phaseXX-<name>` with standard casing and correct spelling (`lucia-phase7-ui_refactoring`). Execute with `git mv` and comprehensive link updates.

---

### CF-009: Stale Codebase Path Reference in `AGENTS.md` (sensors vs gating)
- **Conflict ID**: `CF-009`
- **Conflict Title**: Ownership Map in `AGENTS.md` Cites Non-Existent Directory
- **Sources**:
  1. `AGENTS.md` §4 (Line 171):
     ```text
     ├── sensors/                            # Layer 1: Lexical valence & density encoding
     ```
  2. `docs/ARCHITECTURE.md` §8.1 (Reconciliation Table, Line 730):
     ```markdown
     | **Layer 1 Path** | src/core/sensors/ (early draft). | src/core/gating/stimulus_processor.py. | Directory renamed during Phase 1 restructuring; all active code lives in src/core/gating/. |
     ```
  3. Filesystem check:
     - `src/core/sensors/` does NOT exist.
     - `src/core/gating/` exists and contains `stimulus_processor.py`.
- **Nature of Contradiction**: `AGENTS.md` instructs coding agents to look in `src/core/sensors/`, which does not exist in the active codebase.
- **Likely Chronology**: When the early draft was restructured in Phase 1, `docs/ARCHITECTURE.md` recorded the reconciliation, but `AGENTS.md` Section 4 was never updated.
- **Operational Risk**: Low for seasoned developers; moderate for autonomous agents attempting to locate Layer 1 code.
- **Resolution Status**: `RECOMMENDED_RESOLUTION`
- **Recommended Resolution**: Update `AGENTS.md` §4 to show `gating/` instead of `sensors/`.
