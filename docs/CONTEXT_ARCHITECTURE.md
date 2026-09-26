# Lucia — AI Agent Context Projection Architecture

> **Authoritative Specification for Multi-Agent Context Projections, Reviewer Packs, and Knowledge Ingestion**  
> **Status:** `[CANONICAL REPOSITORY CANON]`  
> **Target Personas:** Ciah (Cognitive Reviewer), Gemini / NotebookLM (Research Corpus), Antigravity (Execution Agent)  
> **Axiom:** One Source of Truth, Many Role-Differentiated Views

---

## 1. Architectural Motivation & Problem Statement

### 1.1 The Context Asymmetry Problem
Different AI agents collaborating on Lucia possess radically different cognitive profiles, operational constraints, and context capacities:

1. **Ciah (Reviewer / Prompt Layer / Architect)**:
   - *Operational Role*: Deep epistemic challenge, red-team auditing, invariant verification, and contract challenge.
   - *Constraint*: Performance degrades significantly when flooded with dozens of raw data files. Operates best with a **curated, high-density projection of at most 5 files**.
2. **Gemini & NotebookLM (Deep Research & Literature Arm)**:
   - *Operational Role*: Long-horizon synthesis, cross-study meta-analyses, hypothesis generation, and literature comparison.
   - *Capability*: Massive context capacity (>1M tokens). Requires access to the **complete unflattened source corpus**, raw benchmark JSONs, and historical negative findings.
3. **Antigravity (Coding & Execution Pair)**:
   - *Operational Role*: Scoped code modification, test authoring, invariant enforcement, and directory auditing.
   - *Constraint*: Must avoid context saturation during code generation. Relies on **minimal sufficient context routing (L0–L6)** to load only the specific subsystem under edit.

### 1.2 The Core Projection Model
To prevent agents from maintaining independent, conflicting versions of reality, context is generated as **read-only projections** derived from the single canonical knowledge base:

```text
                           LUCIA CANONICAL TRUTH
                                     │
           ┌─────────────────────────┼─────────────────────────┐
           ▼                         ▼                         ▼
   Living Canon (L1–L3)      Research & History       Evaluation Evidence
   (Overview, Architecture,   (Hypotheses, Specs,     (Raw Benchmarks, Logs,
    L1 Invariants, ADRs)       Negative Findings)      Falsification Suites)
           │                         │                         │
           └─────────────────────────┼─────────────────────────┘
                                     │
                             CANONICAL REGISTRIES
                         (Phase, Document, Source Map)
                                     │
               ┌─────────────────────┼─────────────────────┐
               ▼                     ▼                     ▼
        CIAH REVIEW PACK      GEMINI CORPUS        ANTIGRAVITY ROUTING
         (Strict ≤ 5 files)   (Complete Archive)     (Scoped L0–L6)
```

---

## 2. Ciah Reviewer Pack Architecture (Strict $\le 5$ Files)

For phase-level reviews, architectural gates, or contract audits, Ciah must never be handed raw repository dumps. Ciah receives an authoritative **5-File Reviewer Pack** that answers five fundamental questions:

```text
┌────────────────────────────────────────────────────────────────────────┐
│                      CIAH 5-FILE REVIEWER PACK                         │
├────────────────────────────────────────────────────────────────────────┤
│ File 1: Executive Context       ── What is Lucia / Current State?      │
│ File 2: Phase History           ── How did this phase evolve?          │
│ File 3: Architecture State      ── What is the active technical truth? │
│ File 4: Evidence & Negatives    ── What was proven, failed, or fixed?  │
│ File 5: Research Boundary       ── What is the current research edge?  │
└────────────────────────────────────────────────────────────────────────┘
```

### 2.1 File 1: Executive Context (`docs/research/P23_REVIEW_01_EXECUTIVE_CONTEXT.md`)
- **Question Answered**: *What is Lucia now, where are we on the roadmap, and what is the current milestone status?*
- **Contents**:
  - System identity: embodied companion without reflective ego, Philia resting attractor ($+0.25, -0.05, +0.05$), 20W WBA efficiency model.
  - Roadmap positioning: status from Phase 1 through current phase.
  - Strict declaration of current frozen commits (e.g. `P23-H = 3eef803`) and locked gates (Genesis `{"is_onboarded": false}`).

### 2.2 File 2: Phase History Progression (`docs/research/P23_REVIEW_02_PHASE_HISTORY.md`)
- **Question Answered**: *How did the phase evolve across its developmental sub-cycles?*
- **Contents**:
  - Unbroken chronological ledger of sub-phases.
  - Progression from initial contract, through benchmark scaffolds, monographs, fortification, adapter boundaries, and reasoning kernels.
  - Direct commit hashes and verification links.

### 2.3 File 3: Architecture State & Epistemic Boundaries (`docs/research/P23_REVIEW_03_ARCHITECTURE_STATE.md`)
- **Question Answered**: *What is the current technical architecture and what are the exact epistemic boundaries of all subsystems?*
- **Contents**:
  - 7-tier epistemic classification table (`SUPPORTED`, `OBSERVED`, `RESEARCH_HARNESS_ONLY`, `EVIDENCE_CONSISTENT`, `HYPOTHESIS`, `UNTESTED`, `NOT_JUSTIFIED`).
  - Active component ownership maps and hardware resource envelopes (CPU latency, RAM, 0.0 MB GPU VRAM).
  - Explicit delineation of unresolved architectural gaps.

### 2.4 File 4: Evidence Ledger & Negative Results (`docs/research/P23_REVIEW_04_EVIDENCE_AND_NEGATIVE_RESULTS.md`)
- **Question Answered**: *What evidence exists, what hypotheses failed, and what audit fixes occurred?*
- **Contents**:
  - Consolidated empirical measurements across all capability tracks.
  - **Preserved Negative Results**: Explicit documentation of disproven approaches (e.g., dense HDC vector crosstalk, V-UMR memory collapse, sentence embedding degradation).
  - **Audit Corrections**: Post-implementation defect discoveries and verified fixes (e.g. `FIX-23H-01` unproven goal epistemic safety).

### 2.5 File 5: Ciah Review Context & Epistemic Boundary (`docs/research/P23_REVIEW_05_P23-I_RESEARCH_BOUNDARY.md`)
- **Question Answered**: *What is the completed research outcome, what are the attributed claims to audit, and what are the strict non-implementation boundaries?*
- **Contents**:
  - P23-I research status (`RESEARCH COMPLETED`, `CONTRACT TRANSITION CANDIDATE`).
  - Immutable baseline: relationship to P23-H frozen state (`3eef803`).
  - Evaluation of Gemini Final Research Report ([`docs/research/P23-I_FINAL_RESEARCH_REPORT.md`](file:///c:/Users/Lunafiah/Desktop/My_project/Lucia/docs/research/P23-I_FINAL_RESEARCH_REPORT.md)) attributed claims (`FREEZE WITH PARAMETER`, `Contract Transition Ready`).
  - Epistemic invariants (Strong Kleene K3, UNKNOWN preservation).
  - Open challenge checklist for Ciah review.
  - Explicit non-authorization of implementation and pending freeze decision.

---

## 3. Gemini & NotebookLM Ingestion Architecture (Deep Corpus)

Gemini and NotebookLM require maximum information depth to conduct cross-phase meta-research and historical verification.

### 3.1 Corpus Completeness Standard
Never compress the Gemini corpus into 5 files. The Gemini ingestion set must include:
1. **Master Living Canon**: [`docs/00_PROJECT_OVERVIEW.md`](file:///c:/Users/Lunafiah/Desktop/My_project/Lucia/docs/00_PROJECT_OVERVIEW.md), [`docs/ARCHITECTURE.md`](file:///c:/Users/Lunafiah/Desktop/My_project/Lucia/docs/ARCHITECTURE.md), [`docs/L1_INVARIANTS.md`](file:///c:/Users/Lunafiah/Desktop/My_project/Lucia/docs/L1_INVARIANTS.md), [`AGENTS.md`](file:///c:/Users/Lunafiah/Desktop/My_project/Lucia/AGENTS.md).
2. **Master Corpus Syntheses**: [`docs/specs/Lucia-phase22-Epistemic_Foraging/PHASE_22_FINAL_REPORTS.md`](file:///c:/Users/Lunafiah/Desktop/My_project/Lucia/docs/specs/Lucia-phase22-Epistemic_Foraging/PHASE_22_FINAL_REPORTS.md), [`docs/research/P23_HISTORY_CONSOLIDATED.md`](file:///c:/Users/Lunafiah/Desktop/My_project/Lucia/docs/research/P23_HISTORY_CONSOLIDATED.md).
3. **Full Research Specs & Monographs**: All monographs in `docs/specs/**` and `evaluation_artifacts/**`.
4. **All Sub-Study Evaluation Reports**: All 20 Phase 22 reports, Phase 23 benchmark reports, and Phase 18 audio diagnostics.
5. **Raw Data Artifacts**: JSON benchmark dumps and experiment matrices in `evaluation_artifacts/**` and `tests/evaluation/**`.

### 3.2 Ingestion Provenance Anchoring
Gemini queries must trace conclusions back to canonical files via [`docs/SOURCE_MAP.md`](file:///c:/Users/Lunafiah/Desktop/My_project/Lucia/docs/SOURCE_MAP.md) and [`docs/PHASE_REGISTRY.md`](file:///c:/Users/Lunafiah/Desktop/My_project/Lucia/docs/PHASE_REGISTRY.md). If Gemini uncovers a contradiction between an older research report and `docs/ARCHITECTURE.md`, it must defer to `docs/ARCHITECTURE.md` as the living canonical truth.

### 3.3 Epistemic Corpus Stratification for Phase 23-I
When Gemini and NotebookLM ingest repository artifacts surrounding Phase 23-I, the corpus retrieval mechanism must strictly stratify artifacts into four distinct epistemic tiers:

```text
┌────────────────────────────────────────────────────────────────────────┐
│                   PHASE 23-I CORPUS STRATIFICATION                     │
├────────────────────────────────────────────────────────────────────────┤
│ Layer 1: PRE-P23-I GOVERNANCE CONTEXT (Commit bed9299)                 │
│          Repository-wide documentation architecture, registries,       │
│          and authority rules. GOVERNANCE ONLY — NOT TECHNICAL EVIDENCE.│
│                                  ≠                                     │
│ Layer 2: P23-I TECHNICAL RESEARCH EVIDENCE                             │
│          Simulation fixtures, binding benchmark measurements, and      │
│          negative results (e.g. rejection of dynamic rule compilation).│
│                                  ≠                                     │
│ Layer 3: P23-I FINAL RESEARCH CONCLUSION                               │
│          Gemini Final Research Report (docs/research/P23-I_FINAL_...); │
│          attributed research recommendation (Contract Transition Ready)│
│                                  ≠                                     │
│ Layer 4: CANONICAL FROZEN CONTRACT                                     │
│          [CURRENTLY PENDING CIAH REVIEW — NOT YET RATIFIED/FROZEN]      │
└────────────────────────────────────────────────────────────────────────┘
```

1. **Commit `bed9299` is Pre-P23-I Governance Context:**  
   The whole-repository documentation and knowledge architecture audit committed at `bed9299` established document authority, source-map registries, and projection structures. It must **NEVER** be represented as technical evidence validating P23-I research claims.
2. **Research Conclusions Remain Attributed:**  
   Gemini's final claims (`RESEARCH-VALIDATED`, `FREEZE WITH PARAMETER`, `Contract Transition Ready`) are preserved in [`docs/research/P23-I_FINAL_RESEARCH_REPORT.md`](file:///c:/Users/Lunafiah/Desktop/My_project/Lucia/docs/research/P23-I_FINAL_RESEARCH_REPORT.md) with explicit provenance. They remain research proposals until ratified by Ciah and governance.
3. **No Unilateral Promotion to Canonical Contract:**  
   Gemini corpus queries must not treat `Contract Transition Ready` as an implemented capability or ratified contract. Contract freeze remains strictly pending Ciah review.

---

## 4. Antigravity Context Architecture (Minimal Sufficient Routing)

Antigravity executes scoped, safe code modifications. Context bloat is the primary cause of hallucinated refactors and invariant violations.

### 4.1 Logical Context Tiers (L0–L6)

```text
L0: Public Mission & Overview  ──► README.md
L1: Non-Negotiable Invariants  ──► docs/L1_INVARIANTS.md, AGENTS.md §2
L2: Project Truth & Roadmap    ──► docs/00_PROJECT_OVERVIEW.md, AGENTS.md §0
L3: Technical Architecture     ──► docs/ARCHITECTURE.md, ADR Ledger
L4: Navigation & Registries    ──► docs/CONTEXT_INDEX.md, docs/PHASE_REGISTRY.md
L5: Historical & Evidence Docs ──► docs/specs/**, evaluation_artifacts/**
L6: Production Source Code     ──► src/core/**, electron/**, config/**
```

### 4.2 Mandatory Context Routing by Task Classification

| Task Classification | Mandatory Layers (Must Load) | Secondary Layers (On Demand) | Strictly Forbidden (Do Not Load) |
|---|---|---|---|
| **Core Bug Fix** | `L1` (Invariants), `L6` (Target module) | `L3` (Relevant ADR section) | `L5` (Historical specs), raw benchmark dumps |
| **Research Investigation**| `L1` (Invariants), `L2` (Roadmap), `L5` (Target spec) | `L4` (Source Map), evaluation fixtures | `L6` (`electron/**`), active persistent files |
| **Architecture Gate / ADR**| `L1` (Invariants), `L2` (Health matrix), `L3` (ADR ledger) | `L4` (Registries), `L5` (Synthesis) | Historical Phase 1–6 tasks, scratch files |
| **UI / Mascot Physics** | `L1` (Mascot bounds INV-7), `L6` (`electron/`) | `docs/specs/lucia-phase7-UI_refractoring/` | Math derivations of LNN ODE, BPTT consolidation |
| **Documentation / Registry**| `L1` (Invariants), `L4` (Registries & Maps) | Target documentation file | Unrelated test suites |

---

## 5. Derived View Synchronization & Freshness Invariants

To guarantee that derived context views never diverge from canonical truth:

1. **Snapshot Anchoring**: Every derived context pack must explicitly state its source commit or timestamp (e.g. `P23 Review Pack: Derived from commit 3f6326a`).
2. **Zero In-Context Mutation**: An AI reviewer or coding agent is strictly prohibited from mutating canonical facts inside a context pack. If an error is identified, the canonical owner must be edited directly.
3. **Automated Consistency Auditing**: Future documentation pipelines will verify that claims in `docs/research/P23_REVIEW_*.md` match bit-for-bit the canonical definitions in `docs/00_PROJECT_OVERVIEW.md` and `docs/ARCHITECTURE.md`.
