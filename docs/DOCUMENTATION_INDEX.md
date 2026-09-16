# Lucia — Documentation Index & Hierarchy System

> **A Comprehensive Navigation System and Document Authority Hierarchy for Lucia**<br/>
> *Consolidated Documentation Hierarchy — Post-Phase 21*

---

## 1. Documentation Organization & Authority Principles

To prevent confusion across development phases, Lucia maintains a strict documentation classification model:

```text
┌────────────────────────────────────────────────────────────────────────┐
│                     DOCUMENTATION CATEGORIES                           │
│                                                                        │
│  1. CONSOLIDATED AUTHORITATIVE LIVING CANON (docs/)                    │
│     • docs/00_PROJECT_OVERVIEW.md: Project identity, philosophy,       │
│       current system status, subsystem health, and roadmap.            │
│     • docs/ARCHITECTURE.md: Full technical architecture, dynamical     │
│       mechanisms, mathematical models, and the complete ADR ledger.    │
│     • docs/USER_MANUAL.md: Operating guide, mascot controls, setup.    │
│                                                                        │
│  2. HISTORICAL RESEARCH & PHASE SPECIFICATIONS (docs/specs/)           │
│     Preserved immutable point-in-time specs, evaluation reports, and   │
│     acceptance sign-offs across milestones (Phases 1–21).              │
│                                                                        │
│  3. SUPERSEDED SPECIFICATIONS                                          │
│     Specifications that pivoted during engineering implementation.     │
│                                                                        │
│  4. DOMAIN & ASSET GUIDES (models/)                                    │
│     Specialized asset layout guides for 3D VRM, Live2D, and sprites.   │
└────────────────────────────────────────────────────────────────────────┘
```

---

## 2. Document Classification Matrix

| Category | File Path | Status | Primary Purpose / Scope |
|---|---|---|---|
| **Authoritative Living Canon** | [`docs/00_PROJECT_OVERVIEW.md`](file:///c:/Users/Lunafiah/Desktop/My_project/Lucia/docs/00_PROJECT_OVERVIEW.md) | **Active Truth** | Canonical project overview: Executive summary, *Philia* philosophy, current subsystem health matrix, test statistics, and roadmap. |
| **Authoritative Living Canon** | [`docs/ARCHITECTURE.md`](file:///c:/Users/Lunafiah/Desktop/My_project/Lucia/docs/ARCHITECTURE.md) | **Active Truth** | Canonical technical architecture: 6-layer pipeline, mathematical mechanisms (MT-LNN ODE, SDM, Lip-sync), concurrency locks, and ADR Ledger (ADR-001 to ADR-028). |
| **Authoritative Living Canon** | [`docs/USER_MANUAL.md`](file:///c:/Users/Lunafiah/Desktop/My_project/Lucia/docs/USER_MANUAL.md) | **Active Truth** | User guide: Personal Digital Room interface, Mascot shortcuts, audio/graphics hardware profiles, and local voice setup. |
| **Authoritative Living Canon** | [`README.md`](file:///c:/Users/Lunafiah/Desktop/My_project/Lucia/README.md) | **Active Truth** | Public front door, quick start commands, repository structure, and newcomer orientation. |
| **Authoritative** | [`PHASE_8_ARCHITECTURE_REVIEW.md`](file:///c:/Users/Lunafiah/Desktop/My_project/Lucia/docs/specs/lucia-phase8-ISOLATION/PHASE_8_ARCHITECTURE_REVIEW.md) | **Active Truth** | Authoritative post-Phase-8 architectural audit, state map, and simulation baseline. |
| **Authoritative** | [`PHASE_8.md`](file:///c:/Users/Lunafiah/Desktop/My_project/Lucia/docs/specs/lucia-phase8-ISOLATION/PHASE_8.md) | **Active Truth** | Phase 8 Runtime Isolation & Simulation Environment specification and invariants. |
| **Authoritative** | [`PHASE_9_ARCHITECTURE_GATE.md`](file:///c:/Users/Lunafiah/Desktop/My_project/Lucia/docs/specs/lucia-phase9-Cognition_Unifying/PHASE_9_ARCHITECTURE_GATE.md) | **Active Truth** | Formal Phase 9 Architectural Decision Gate (Revision v2.0): F-01 to F-04, 5-tier concurrency, state ownership. |
| **Authoritative** | [`PHASE_9.md`](file:///c:/Users/Lunafiah/Desktop/My_project/Lucia/docs/specs/lucia-phase9-Cognition_Unifying/PHASE_9.md) | **Active Truth** | Canonical Phase 9 specification: Unified Cognitive Architecture & System Convergence. |
| **Authoritative** | [`PHASE_7_UI_REFACTORING_SPEC.md`](file:///c:/Users/Lunafiah/Desktop/My_project/Lucia/docs/specs/lucia-phase7-UI_refractoring/PHASE_7_UI_REFACTORING_SPEC.md) | **Active Truth** | Phase 7 UI Design System: CSS tokens, component layouts, and Mascot physics. |
| **Authoritative** | [`Phase_7_new_UI_requirement.md`](file:///c:/Users/Lunafiah/Desktop/My_project/Lucia/docs/specs/lucia-phase7-UI_refractoring/Phase_7_new_UI_requirement.md) | **Active Truth** | Product brief for Phase 7: Personal Digital Room, One Continuous Life companion ontology. |
| **Governance** | [`AGENTS.md`](file:///c:/Users/Lunafiah/Desktop/My_project/Lucia/AGENTS.md) | **Active Truth** | Operational instructions, lock discipline, and strict invariants for AI coding agents. |
| **Historical Seed** | [`docs/Triết lý thiết kế AI cảm xúc.md`](file:///c:/Users/Lunafiah/Desktop/My_project/Lucia/docs/Triết lý thiết kế AI cảm xúc.md) | **Historical** | Original research whitepaper (Vietnamese) founding the 20W WBA paradigm. |
| **Historical Spec** | [`lucia-phase1-core`](file:///c:/Users/Lunafiah/Desktop/My_project/Lucia/docs/specs/lucia-phase1-core/) | **Historical** | Phase 1 milestone specification (EmotionCore, Homeostasis, BoundaryLayer). |
| **Historical Spec** | [`lucia-phase2-memory`](file:///c:/Users/Lunafiah/Desktop/My_project/Lucia/docs/specs/lucia-phase2-memory/) | **Historical** | Phase 2 milestone specification (SDMCore, AffectiveMemory, Decay, Ecphory). |
| **Historical Spec** | [`lucia-phase3-ui`](file:///c:/Users/Lunafiah/Desktop/My_project/Lucia/docs/specs/lucia-phase3-ui/) | **Historical** | Phase 3 milestone specification (FastAPI server, Electron IPC, debug panel). |
| **Historical Spec** | [`lucia-phase4-inference`](file:///c:/Users/Lunafiah/Desktop/My_project/Lucia/docs/specs/lucia-phase4-inference/) | **Historical** | Phase 4 milestone specification (ActiveInference, LNNTrainer, torchdiffeq). |
| **Historical Spec** | [`lucia-phase5-presence`](file:///c:/Users/Lunafiah/Desktop/My_project/Lucia/docs/specs/lucia-phase5-presence/) | **Historical** | Phase 5 milestone specification (PresenceOrchestrator, multimodal synchronization). |
| **Historical Spec** | [`lucia-phase6-refinement`](file:///c:/Users/Lunafiah/Desktop/My_project/Lucia/docs/specs/lucia-phase6-refinement/) | **Historical** | Phase 6 milestone specification (Packaging, System Tray, Mascot, LSI). |
| **Active Spec** | [`Phase_10_AFFECTIVE_DYNAMICS_SPEC.md`](file:///c:/Users/Lunafiah/Desktop/My_project/Lucia/docs/specs/lucia-phase10-Affective_Dynamics/Phase_10_AFFECTIVE_DYNAMICS_SPEC.md) | **Active Truth** | Phase 10 canonical specification: Mathematical formulation, state taxonomy, temporal contract. |
| **Active Spec** | [`Phase_11_AFFECTIVE_MEMORY_SPEC.md`](file:///c:/Users/Lunafiah/Desktop/My_project/Lucia/docs/specs/lucia-phase11-Affective_Memory/Phase_11_AFFECTIVE_MEMORY_SPEC.md) | **Active Truth** | Phase 11 canonical specification: Retrieval vs. Recollection, Candidate Hypotheses A–E. |
| **Active Spec** | [`Phase_12_KNOWLEDGE_LEARNING_SPEC.md`](file:///c:/Users/Lunafiah/Desktop/My_project/Lucia/docs/specs/lucia-phase12-Knowledge_Learning/Phase_12_KNOWLEDGE_LEARNING_SPEC.md) | **Active Truth** | Phase 12 canonical specification: Memory vs. Knowledge ontology, K0–K9 maturity ladder. |
| **Active Spec** | [`Phase_13_RELATIONSHIP_DEVELOPMENT_SPEC.md`](file:///c:/Users/Lunafiah/Desktop/My_project/Lucia/docs/specs/lucia-phase13-Relationship_Development/Phase_13_RELATIONSHIP_DEVELOPMENT_SPEC.md) | **Active Truth** | Phase 13 canonical specification: Philia core, relationship dynamics & inertia. |
| **Active Spec** | [`Phase_14_AFFECTIVE_EXPRESSION_SPEC.md`](file:///c:/Users/Lunafiah/Desktop/My_project/Lucia/docs/specs/lucia-phase14-Embodiment_Affective_Expression/Phase_14_AFFECTIVE_EXPRESSION_SPEC.md) | **Active Truth** | Phase 14 canonical specification: 15-dim expression state, blendshapes, prosody. |
| **Active Spec** | [`Phase_15_AFFECTIVE_COMMUNICATION_SPEC.md`](file:///c:/Users/Lunafiah/Desktop/My_project/Lucia/docs/specs/lucia-phase15-Affective_Communication/Phase_15_AFFECTIVE_COMMUNICATION_SPEC.md) | **Active Truth** | Phase 15 canonical specification: Affective communication policy, pragmatic framing. |
| **Active Spec** | [`PHASE_16_ARCHITECTURE.md`](file:///c:/Users/Lunafiah/Desktop/My_project/Lucia/docs/specs/lucia-phase16-Affective_Life_Integration/PHASE_16_ARCHITECTURE.md) | **Active Truth** | Phase 16 canonical architecture: 16-stage cognitive pipeline, promoted subsystems, two-phase lifecycle. |
| **Active Spec** | [`PHASE_18_SPECIFICATION.md`](file:///c:/Users/Lunafiah/Desktop/My_project/Lucia/docs/specs/lucia-phase18-Human_Longitudinal_Validation/PHASE_18_SPECIFICATION.md) | **Active Truth** | Phase 18 canonical specification: Human Longitudinal Interaction & Real-World Validation. |
| **Validation Report** | [`PHASE_18_EVALUATION_REPORT.md`](file:///c:/Users/Lunafiah/Desktop/My_project/Lucia/docs/specs/lucia-phase18-Human_Longitudinal_Validation/PHASE_18_EVALUATION_REPORT.md) | **Active Truth** | Comprehensive Phase 18 evaluation report: 9 invariant gates, audiovisual synchronization matrix. |
| **Acceptance Report** | [`PHASE_19_ACCEPTANCE_REPORT.md`](file:///c:/Users/Lunafiah/Desktop/My_project/Lucia/docs/specs/Lucia-phase19-Multi_Timescale_Affective_Life/PHASE_19_ACCEPTANCE_REPORT.md) | **Active Truth** | Phase 19 formal acceptance report: MT-LNN biexponential separation, Philia attractor sign-off. |
| **Production Design** | [`PHASE_20_PRODUCTION_REALIZATION_DESIGN.md`](file:///c:/Users/Lunafiah/Desktop/My_project/Lucia/docs/specs/Lucia-phase20-Affective_Recollection/PHASE_20_PRODUCTION_REALIZATION_DESIGN.md) | **Active Truth** | Phase 20 production architecture design: Closed-loop slow-field forcing, competitive softmax gating. |
| **Acceptance Report** | [`PHASE_20_ACCEPTANCE_REPORT.md`](file:///c:/Users/Lunafiah/Desktop/My_project/Lucia/docs/specs/Lucia-phase20-Affective_Recollection/PHASE_20_ACCEPTANCE_REPORT.md) | **Active Truth** | Phase 20 formal acceptance report: Closed-loop recollection sign-off (Commit `f20420a`). |
| **Production Design** | [`PHASE_21_PRODUCTION_REALIZATION_DESIGN.md`](file:///c:/Users/Lunafiah/Desktop/My_project/Lucia/docs/specs/Lucia-phase21-Relational_Consolidation/PHASE_21_PRODUCTION_REALIZATION_DESIGN.md) | **Active Truth** | Phase 21 production architecture design: Standalone ConsolidationEngine, spectral norm bound $\le 0.08$. |
| **Acceptance Report** | [`PHASE_21_ACCEPTANCE_REPORT.md`](file:///c:/Users/Lunafiah/Desktop/My_project/Lucia/docs/specs/Lucia-phase21-Relational_Consolidation/PHASE_21_ACCEPTANCE_REPORT.md) | **Active Truth** | Phase 21 formal acceptance report: 13/13 production unit tests, 15/15 research tests, sign-off (Commit `58a509c`). |
| **Research Protocol** | [`PHASE_22_H1_PROTOCOL_AMENDMENT_v1.4.md`](file:///c:/Users/Lunafiah/Desktop/My_project/Lucia/docs/specs/Lucia-phase22-Epistemic_Foraging/PHASE_22_H1_PROTOCOL_AMENDMENT_v1.4.md) | **Ratified & Executed** | Phase 22 H1 Protocol Amendment v1.4: Synchronized $N=270$, conditioned surprise check ($T=12$), calibrated $U_{\text{Low}}$ variance, 15-point preflight harness. |
| **Calibration Report**| [`PHASE_22_H1_U_LOW_CALIBRATION_REPORT.md`](file:///c:/Users/Lunafiah/Desktop/My_project/Lucia/docs/specs/Lucia-phase22-Epistemic_Foraging/PHASE_22_H1_U_LOW_CALIBRATION_REPORT.md) | **Research Truth** | Phase 22 H1 Monte Carlo calibration report: 20,000-cell evaluation of $U_{\text{Low}}$ proposition generator candidates. |
| **Compliance Audit** | [`PHASE_22_H1_POST_EXECUTION_COMPLIANCE_AUDIT.md`](file:///c:/Users/Lunafiah/Desktop/My_project/Lucia/docs/specs/Lucia-phase22-Epistemic_Foraging/PHASE_22_H1_POST_EXECUTION_COMPLIANCE_AUDIT.md) | **Research Truth** | Phase 22 H1 Path C post-execution protocol compliance audit & defect root-cause analysis. |
| **Execution Report**  | [`PHASE_22_H1_EXECUTION_REPORT_PATH_C.md`](file:///c:/Users/Lunafiah/Desktop/My_project/Lucia/docs/specs/Lucia-phase22-Epistemic_Foraging/PHASE_22_H1_EXECUTION_REPORT_PATH_C.md) | **Historical Truth** | Phase 22 H1 Path C execution report: INCONCLUSIVE (Blocked by Gate 2 & Gate 4). |
| **Execution Report**  | [`PHASE_22_H1_EXECUTION_REPORT_v1.4.md`](file:///c:/Users/Lunafiah/Desktop/My_project/Lucia/docs/specs/Lucia-phase22-Epistemic_Foraging/PHASE_22_H1_EXECUTION_REPORT_v1.4.md) | **Research Truth** | Phase 22 H1 Protocol v1.4 execution report: INCONCLUSIVE (Blocked by Quality Gate 2 $\Delta_{HM} < 0.15$). |
| **Diagnostic Report** | [`PHASE_22_H1_GATE2_COMPRESSION_DIAGNOSTIC.md`](file:///c:/Users/Lunafiah/Desktop/My_project/Lucia/docs/specs/Lucia-phase22-Epistemic_Foraging/PHASE_22_H1_GATE2_COMPRESSION_DIAGNOSTIC.md) | **Diagnostic Truth** | Phase 22 H1 Gate 2 surprise compression diagnostic investigation: empirical dissection of Medium-surprise valence inflation at $T=12$. |
| **Calibration Report** | [`PHASE_22_H1_STIMULUS_CALIBRATION_REPORT.md`](file:///c:/Users/Lunafiah/Desktop/My_project/Lucia/docs/specs/Lucia-phase22-Epistemic_Foraging/PHASE_22_H1_STIMULUS_CALIBRATION_REPORT.md) | **Calibration Truth** | Phase 22 H1 Independent Stimulus Calibration Report: 120,000-sample Monte Carlo characterization, basal semantic density floor analysis, and candidate generator evaluation (G0–G3). |
| **Research Report** | [`PHASE_22_H1_DYNAMICAL_HEADROOM_RESEARCH_REPORT.md`](file:///c:/Users/Lunafiah/Desktop/My_project/Lucia/docs/specs/Lucia-phase22-Epistemic_Foraging/PHASE_22_H1_DYNAMICAL_HEADROOM_RESEARCH_REPORT.md) | **Research Truth** | Phase 22 H1 Empirical Dynamical Headroom & Directional Geometry Research Report: 9-point exposure grid ($T \in [1, 100]$), empirical headroom squeeze ($H(12)=0.2574$), isotropic metric blindness, and magnitude collapse analysis. |
| **Resolution Report** | [`PHASE_22_H1_GATE2_RESOLUTION_RESEARCH.md`](file:///c:/Users/Lunafiah/Desktop/My_project/Lucia/docs/specs/Lucia-phase22-Epistemic_Foraging/PHASE_22_H1_GATE2_RESOLUTION_RESEARCH.md) | **Research Truth** | Phase 22 H1 Gate 2 Resolution Research Report: Directional information loss (RQ1), component-wise PAD effect sizes (RQ2, Arousal $d>9.5$), conversational exposure feasibility (RQ3, $T \le 25$), and 6 candidate diagnostics evaluation (RQ4). |
| **Measurement Architecture Study** | [`PHASE_22_H1_MEASUREMENT_ARCHITECTURE_STUDY.md`](file:///c:/Users/Lunafiah/Desktop/My_project/Lucia/docs/specs/Lucia-phase22-Epistemic_Foraging/PHASE_22_H1_MEASUREMENT_ARCHITECTURE_STUDY.md) | **Research Truth** | Phase 22 H1 Measurement Architecture Study: Semantic audit of canonical $S$ vs. prediction residual $r_T$ (RQ1), scalar collapse analysis (RQ2), magnitude-controlled directional information (RQ3), displacement vs. residual (RQ4), representation hierarchy M0–M4 (RQ5), and conversational viability $T \le 25$ (RQ6). |
| **Precision Measurement Study** | [`PHASE_22_H1_PRECISION_DIRECTIONAL_MEASUREMENT_STUDY.md`](file:///c:/Users/Lunafiah/Desktop/My_project/Lucia/docs/specs/Lucia-phase22-Epistemic_Foraging/PHASE_22_H1_PRECISION_DIRECTIONAL_MEASUREMENT_STUDY.md) | **Research Truth** | Phase 22 H1 Precision-Weighted & Directional Measurement Architecture Research: M0–M5 representation matrix (RQ1), non-data-fitted precision structures $\boldsymbol{\Pi}_0–\boldsymbol{\Pi}_3$ (RQ2), component-wise separation (RQ3), magnitude-matched directional persistence (RQ4), displacement vs. residual (RQ5), homeostatic inventory (RQ6), conversational timescales $T \le 25$ (RQ7), and architectural surprise vs. uncertainty semantics (RQ8). |

---

## 3. Directory Map & Repository Structure

```text
Lucia/
├── AGENTS.md                                   # Master operating guide & invariants for AI agents
├── README.md                                   # Public front-door & newcomer overview
├── config/
│   ├── ui.json                                 # Port, default model, voice, and log settings
│   └── window-state.json                       # Saved window coordinates and bounds
├── data/
│   ├── chat_history.json                       # Persistent conversation sessions & turns
│   └── profile.json                            # Companion identity & onboarding status
├── docs/
│   ├── 00_PROJECT_OVERVIEW.md                  # Canonical Executive Summary, Current Status & Roadmap
│   ├── ARCHITECTURE.md                         # Canonical Technical Architecture, Mechanisms & ADR Ledger
│   ├── DOCUMENTATION_INDEX.md                  # This file: navigation, hierarchy & authority index
│   ├── USER_MANUAL.md                          # Complete user, configuration & operating manual
│   ├── Triết lý thiết kế AI cảm xúc.md         # Foundational concept paper (Vietnamese)
│   ├── specs/                                  # Specifications & realization designs (Phases 1–21)
│   └── screenshots/                            # Architectural UI & telemetry captures
├── electron/                                   # Native Electron desktop application
│   ├── main/                                   # Main process: ProcessManager, IPC, Mascot window
│   ├── preload/                                # ContextBridge security isolation
│   └── renderer/                               # Web client: Personal Digital Room, 4-Engine Avatar
├── models/                                     # Model weights & character assets
│   ├── avatar/                                 # Avatar assets (live2d/, sprites/, vrm/)
│   └── voice/rvc/                              # Voice models (.pth + .index)
├── src/                                        # Python core backend
│   ├── api/                                    # FastAPI server & endpoints
│   └── core/                                   # Cognitive layers (emotion, gating, memory, simulation, voice)
└── tests/                                      # Comprehensive test suites
    ├── unit/                                   # Isolated unit tests (605 passing)
    ├── property/                               # Hypothesis property-based tests (35 passing)
    ├── evaluation_phase*/                      # Research evaluation harnesses
    └── integration/                            # Multi-component pipeline tests
```

---

## 4. Reading Pathways by Persona

### Path A: Core AI & Backend Engineers
*Goal: Understand mathematical models, concurrency locks, and cognitive pipelines.*
1. [`docs/00_PROJECT_OVERVIEW.md`](file:///c:/Users/Lunafiah/Desktop/My_project/Lucia/docs/00_PROJECT_OVERVIEW.md) — Grasp the 6-layer cognitive flow and active status.
2. [`docs/ARCHITECTURE.md`](file:///c:/Users/Lunafiah/Desktop/My_project/Lucia/docs/ARCHITECTURE.md) — Deep-dive into Coupled MT-LNN ODE, SDM Hamming space, offline BPTT consolidation, lock hierarchy, and ADR ledger.
3. [`AGENTS.md`](file:///c:/Users/Lunafiah/Desktop/My_project/Lucia/AGENTS.md) — Review coding invariants, CPU/GPU discipline, and lock disciplines.

### Path B: Frontend & UI/UX Engineers
*Goal: Build interfaces adhering to the Personal Digital Room and avatar animation pipelines.*
1. [`docs/specs/lucia-phase7-UI_refractoring/Phase_7_new_UI_requirement.md`](file:///c:/Users/Lunafiah/Desktop/My_project/Lucia/docs/specs/lucia-phase7-UI_refractoring/Phase_7_new_UI_requirement.md) — Read the product brief and companion ontology.
2. [`docs/specs/lucia-phase7-UI_refractoring/PHASE_7_UI_REFACTORING_SPEC.md`](file:///c:/Users/Lunafiah/Desktop/My_project/Lucia/docs/specs/lucia-phase7-UI_refractoring/PHASE_7_UI_REFACTORING_SPEC.md) — Study CSS tokens, component layouts, and Mascot rules.
3. [`docs/ARCHITECTURE.md`](file:///c:/Users/Lunafiah/Desktop/My_project/Lucia/docs/ARCHITECTURE.md) (§3.6) — Review `getModelBounds()` and hover zoom mathematics.

### Path C: AI Coding Agents
*Goal: Implement features or fix bugs safely without violating architectural invariants.*
1. [`AGENTS.md`](file:///c:/Users/Lunafiah/Desktop/My_project/Lucia/AGENTS.md) — **MANDATORY**: Rules on pre-reflective emotion, one life ontology, and forbidden actions.
2. [`docs/00_PROJECT_OVERVIEW.md`](file:///c:/Users/Lunafiah/Desktop/My_project/Lucia/docs/00_PROJECT_OVERVIEW.md) — Check live subsystem health matrix and test status.
3. [`docs/ARCHITECTURE.md`](file:///c:/Users/Lunafiah/Desktop/My_project/Lucia/docs/ARCHITECTURE.md) (§8) — Review ADR Ledger and historical reconciliation before proposing changes.

### Path D: End Users & Companion Guardians
*Goal: Run, configure, and interact with Lucia.*
1. [`README.md`](file:///c:/Users/Lunafiah/Desktop/My_project/Lucia/README.md) — Quick start & dependencies.
2. [`docs/USER_MANUAL.md`](file:///c:/Users/Lunafiah/Desktop/My_project/Lucia/docs/USER_MANUAL.md) — Full operating instructions, shortcuts, RVC voice setup, and avatar installation.

---

## 5. Subject Cross-Reference Matrix

| Subject / Technical Topic | Canonical Section in `docs/ARCHITECTURE.md` | Primary Milestone Spec |
|---|---|---|
| **Limbic Fast Loop (Coupled MT-LNN ODE)** | `docs/ARCHITECTURE.md` §3.2 | `docs/specs/lucia-phase1-core/` |
| **Homeostasis & Somatic Markers** | `docs/ARCHITECTURE.md` §3.3 | `docs/specs/lucia-phase1-core/` |
| **Active Inference & Plasticity** | `docs/ARCHITECTURE.md` §3.4 | `docs/specs/lucia-phase4-inference/` |
| **Tier 3 Offline Synaptic Consolidation** | `docs/ARCHITECTURE.md` §3.4 | `docs/specs/Lucia-phase21-Relational_Consolidation/` |
| **Affective Memory & SDM Mechanics** | `docs/ARCHITECTURE.md` §3.5 | `docs/specs/lucia-phase2-memory/` |
| **Closed-Loop Affective Recollection** | `docs/ARCHITECTURE.md` §3.5 | `docs/specs/Lucia-phase20-Affective_Recollection/` |
| **Conceptual Knowledge Store** | `docs/ARCHITECTURE.md` §8 (ADR-021) | `docs/specs/lucia-phase12-Knowledge_Learning/` |
| **Interpersonal Relationship Lifecycle** | `docs/ARCHITECTURE.md` §8 (ADR-022) | `docs/specs/lucia-phase13-Relationship_Development/` |
| **Affective Communication Policy** | `docs/ARCHITECTURE.md` §8 (ADR-023) | `docs/specs/lucia-phase15-Affective_Communication/` |
| **Canonical 15-Dim Expression State** | `docs/ARCHITECTURE.md` §8 (ADR-024) | `docs/specs/lucia-phase14-Embodiment_Affective_Expression/` |
| **Direct RVC Voice Engine** | `docs/ARCHITECTURE.md` §3.6.1 | `docs/USER_MANUAL.md` §2 |
| **Quad-Engine Avatar Architecture** | `docs/ARCHITECTURE.md` §3.6.2 | `models/avatar/README.md` |
| **Mascot Physics & Hover Zoom Math** | `docs/ARCHITECTURE.md` §3.6.3 | `docs/specs/lucia-phase7-UI_refractoring/` |
| **Limbic Stability Evaluator (LSI)** | `docs/ARCHITECTURE.md` §5 | `docs/specs/lucia-phase6-refinement/` |
| **Simulation Runtime & SimClock** | `docs/ARCHITECTURE.md` §7 | `docs/specs/lucia-phase8-ISOLATION/PHASE_8.md` |
| **Verified Lock Hierarchy Discipline** | `docs/ARCHITECTURE.md` §5.1 | `docs/ARCHITECTURE.md` §8 (ADR-018, ADR-028) |
| **Full ADR Ledger (ADR-001 to ADR-028)** | `docs/ARCHITECTURE.md` §8 | `docs/ARCHITECTURE.md` §8.2 (Changelog) |
