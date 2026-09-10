# Lucia — Documentation Index & Hierarchy System

> **A Comprehensive Navigation System and Document Authority Hierarchy for Lucia**

---

## 1. Documentation Organization & Authority Principles

To prevent confusion across development phases, Lucia maintains a strict documentation classification model:

```
┌────────────────────────────────────────────────────────────────────────┐
│                     DOCUMENTATION CATEGORIES                           │
│                                                                        │
│  1. AUTHORITATIVE (CORE TRUTH)                                         │
│     Active system specifications, architecture, mechanisms, and live   │
│     manuals. Always reflects current codebase implementation.          │
│                                                                        │
│  2. HISTORICAL MILESTONE SPECS (.kiro/specs/)                          │
│     Preserved immutable point-in-time specs from earlier phases.       │
│     Maintained for audit trail, test criteria, and design rationale.   │
│     NEVER merged into docs/ or overwritten.                            │
│                                                                        │
│  3. SUPERSEDED & DIVERGED SPECIFICATIONS                               │
│     Specifications that pivoted during implementation (e.g. Phase 5    │
│     desktop agency pivoted to embodied vocal/avatar presence).         │
│                                                                        │
│  4. DOMAIN & ASSET DOCUMENTATION                                       │
│     Specialized guides for 3D VRM, Live2D, and sprite set integration. │
└────────────────────────────────────────────────────────────────────────┘
```

---

## 2. Document Classification Matrix

| Category | File Path | Status | Primary Purpose / Scope |
|---|---|---|---|
| **Authoritative** | [`docs/00_PROJECT_OVERVIEW.md`](file:///c:/Users/Lunafiah/Desktop/My_project/Lucia/docs/00_PROJECT_OVERVIEW.md) | **Active Truth** | Executive summary, core philosophy (*Philia*), 6-layer architecture, roadmap. |
| **Authoritative** | [`docs/ARCHITECTURE.md`](file:///c:/Users/Lunafiah/Desktop/My_project/Lucia/docs/ARCHITECTURE.md) | **Active Truth** | System-level architecture, thread safety, hardware scaling, mascot IPC protocol. |
| **Authoritative** | [`docs/MECHANISM.md`](file:///c:/Users/Lunafiah/Desktop/My_project/Lucia/docs/MECHANISM.md) | **Active Truth** | Detailed mathematical formulas (ODE, SDM, LSI, Ecphory, VAD, Lip-sync geometry). |
| **Authoritative** | [`docs/CURRENT_STATUS.md`](file:///c:/Users/Lunafiah/Desktop/My_project/Lucia/docs/CURRENT_STATUS.md) | **Active Truth** | Live implementation snapshot, subsystem health matrix, active API routes. |
| **Authoritative** | [`docs/DESIGN_DECISIONS.md`](file:///c:/Users/Lunafiah/Desktop/My_project/Lucia/docs/DESIGN_DECISIONS.md) | **Active Truth** | Architectural Decision Records (ADRs), trade-offs, reconciled contradictions. |
| **Authoritative** | [`docs/USER_MANUAL.md`](file:///c:/Users/Lunafiah/Desktop/My_project/Lucia/docs/USER_MANUAL.md) | **Active Truth** | User guide, installation, model layout, mascot shortcuts, audio/graphics settings. |
| **Authoritative** | [`PHASE_8_ARCHITECTURE_REVIEW.md`](file:///c:/Users/Lunafiah/Desktop/My_project/Lucia/docs/.kiro/specs/lucia-phase8-ISOLATION/PHASE_8_ARCHITECTURE_REVIEW.md) | **Active Truth** | Authoritative post-Phase-8 architectural audit, state map, and baseline. |
| **Authoritative** | [`PHASE_8.md`](file:///c:/Users/Lunafiah/Desktop/My_project/Lucia/docs/.kiro/specs/lucia-phase8-ISOLATION/PHASE_8.md) | **Active Truth** | Phase 8 Runtime Isolation & Simulation Environment specification and evidence. |
| **Authoritative** | [`PHASE_9_ARCHITECTURE_GATE.md`](file:///c:/Users/Lunafiah/Desktop/My_project/Lucia/docs/phase9/PHASE_9_ARCHITECTURE_GATE.md) | **Active Truth** | Formal Phase 9 Architectural Decision Gate (Revision v2.0): F-01 to F-04, 5-tier concurrency, state ownership, simulation validation, generation policy. |
| **Authoritative** | [`PHASE_9.md`](file:///c:/Users/Lunafiah/Desktop/My_project/Lucia/docs/phase9/PHASE_9.md) | **Active Truth** | Canonical Phase 9 specification: Unified Cognitive Architecture & System Convergence. |
| **Authoritative** | [`README.md`](file:///c:/Users/Lunafiah/Desktop/My_project/Lucia/README.md) | **Active Truth** | Project entry point, quick start commands, repository structure. |
| **Authoritative** | [`PHASE_7_UI_REFACTORING_SPEC.md`](file:///c:/Users/Lunafiah/Desktop/My_project/Lucia/docs/.kiro/specs/lucia-phase7-UI_refractoring/PHASE_7_UI_REFACTORING_SPEC.md) | **Active Truth** | Phase 7 UI Design System, tokens, component layouts, mascot controls. |
| **Authoritative** | [`new_UI_requirement.md`](file:///c:/Users/Lunafiah/Desktop/My_project/Lucia/docs/.kiro/specs/lucia-phase7-UI_refractoring/new_UI_requirement.md) | **Active Truth** | Product brief for Phase 7: Personal Digital Room, One Continuous Life ontology. |
| **Governance** | [`AGENTS.md`](file:///c:/Users/Lunafiah/Desktop/My_project/Lucia/AGENTS.md) | **Active Truth** | Operational instructions and strict rules for AI coding agents. |
| **Historical Seed** | [`docs/Triết lý thiết kế AI cảm xúc.md`](file:///c:/Users/Lunafiah/Desktop/My_project/Lucia/docs/Triết lý thiết kế AI cảm xúc.md) | **Historical** | Original research whitepaper (Vietnamese) founding the 20W WBA paradigm. |
| **Historical Spec** | [`lucia-core-phase1`](file:///c:/Users/Lunafiah/Desktop/My_project/Lucia/docs/.kiro/specs/lucia-core-phase1/) | **Historical** | Phase 1 milestone specification (EmotionCore, Homeostasis, BoundaryLayer). |
| **Historical Spec** | [`lucia-memory-phase2`](file:///c:/Users/Lunafiah/Desktop/My_project/Lucia/docs/.kiro/specs/lucia-memory-phase2/) | **Historical** | Phase 2 milestone specification (SDMCore, AffectiveMemory, Decay, Ecphory). |
| **Historical Spec** | [`lucia-ui-phase3`](file:///c:/Users/Lunafiah/Desktop/My_project/Lucia/docs/.kiro/specs/lucia-ui-phase3/) | **Historical** | Phase 3 milestone specification (FastAPI server, Electron IPC, debug panel). |
| **Historical Spec** | [`lucia-inference-phase4`](file:///c:/Users/Lunafiah/Desktop/My_project/Lucia/docs/.kiro/specs/lucia-inference-phase4/) | **Historical** | Phase 4 milestone specification (ActiveInference, LNNTrainer, torchdiffeq). |
| **Historical Spec** | [`lucia-refinement-phase6`](file:///c:/Users/Lunafiah/Desktop/My_project/Lucia/docs/.kiro/specs/lucia-refinement-phase6/) | **Historical** | Phase 6 milestone specification (Packaging, System Tray, Mascot, LSI). |
| **Active Spec** | [`lucia-phase9-cognition`](file:///c:/Users/Lunafiah/Desktop/My_project/Lucia/docs/.kiro/specs/lucia-phase9-cognition/) | **Active Truth** | Phase 9 milestone specification (Unified Cognition & Causal Inference). |
| **Active Spec** | [`AFFECTIVE_DYNAMICS_SPEC.md`](file:///c:/Users/Lunafiah/Desktop/My_project/Lucia/docs/specs/lucia-phase10-Affective_Dynamics/AFFECTIVE_DYNAMICS_SPEC.md) | **Active Truth** | Phase 10 canonical specification: Mathematical formulation, state taxonomy, temporal contract, causal graph, and Phase 11 memory boundary. |
| **Active Spec** | [`AFFECTIVE_MEMORY_SPEC.md`](file:///c:/Users/Lunafiah/Desktop/My_project/Lucia/docs/specs/lucia-phase11-Affective_Memory/AFFECTIVE_MEMORY_SPEC.md) | **Active Truth** | Phase 11 canonical specification: Retrieval vs. Recollection, Candidate Hypotheses A–E, and 8 empirical evaluation criteria. |
| **Research Spec** | [`KNOWLEDGE_LEARNING_SPEC.md`](file:///c:/Users/Lunafiah/Desktop/My_project/Lucia/docs/specs/lucia-phase12-Knowledge_Learning/KNOWLEDGE_LEARNING_SPEC.md) | **Research Spec** | Phase 12 research specification: Memory vs Knowledge distinction, K0–K9 maturity hierarchy, LLM-as-Teacher boundary. |
| **Research Spec** | [`RELATIONSHIP_DEVELOPMENT_SPEC.md`](file:///c:/Users/Lunafiah/Desktop/My_project/Lucia/docs/specs/lucia-phase13-Relationship_Development/RELATIONSHIP_DEVELOPMENT_SPEC.md) | **Research Spec** | Phase 13 research specification: Core Relational Orientation (*Philia*) vs dynamic relationship state ($R_t$), temporal inertia, R-EXP-1 to 12 validation suite. |
| **Validation Report** | [`docs/phase9/ABLATION_TEST_V1.md`](file:///c:/Users/Lunafiah/Desktop/My_project/Lucia/docs/phase9/ABLATION_TEST_V1.md) | **Active Truth** | Lucia Ablation Test v1 Exploratory Pilot report (Q1-Q5 evaluation, hardware profile, empirical findings). |
| **Diverged Spec** | [`lucia-presence-phase5`](file:///c:/Users/Lunafiah/Desktop/My_project/Lucia/docs/.kiro/specs/lucia-presence-phase5/) | **Superseded** | Proposed VLM screen observation & PyAutoGUI agency (pivoted to RVC/Avatar). |
| **Diverged Note** | [`models/voice/README.md`](file:///c:/Users/Lunafiah/Desktop/My_project/Lucia/models/voice/README.md) | **Superseded** | Preliminary notes on Piper/Kokoro ONNX (superseded by RVC engine). |
| **Domain Asset** | [`models/avatar/README.md`](file:///c:/Users/Lunafiah/Desktop/My_project/Lucia/models/avatar/README.md) | **Domain Guide** | Directory layout rules for custom Live2D, VRM, and 2D sprite models. |
| **Domain Asset** | [`models/avatar/live2d/HoshinoAi/README.md`](file:///c:/Users/Lunafiah/Desktop/My_project/Lucia/models/avatar/live2d/HoshinoAi/README.md) | **Domain Guide** | Cubism parameter bindings and expressions for Hoshino Ai model. |
| **Domain Asset** | [`models/avatar/sprites/columbina/README.md`](file:///c:/Users/Lunafiah/Desktop/My_project/Lucia/models/avatar/sprites/columbina/README.md) | **Domain Guide** | 10-expression sprite atlas rules and PAD mappings for Columbina set. |

---

## 3. Directory Map & Repository Structure

```
Lucia/
├── AGENTS.md                                   # Master operating guide for AI coding agents
├── README.md                                   # Public front-door & quick-start instructions
├── PHASE_8.md                                  # Phase 8: Runtime isolation & simulation specification
├── PHASE_8_ARCHITECTURE_REVIEW.md              # Authoritative post-Phase-8 architectural audit & baseline
├── PHASE_9.md                                  # Phase 9: Cognitive unification & convergence specification
├── PHASE_9_ARCHITECTURE_GATE.md                # Phase 9: Authoritative Architectural Gate (v2.0)
├── config/
│   ├── ui.json                                 # Port, default model, voice, and log settings
│   └── window-state.json                       # Saved window coordinates and bounds
├── data/
│   └── chat_history.json                       # Persistent conversation sessions & turns
├── docs/
│   ├── 00_PROJECT_OVERVIEW.md                  # Executive summary & 6-layer architecture overview
│   ├── ARCHITECTURE.md                         # Detailed system architecture specification
│   ├── CURRENT_STATUS.md                       # Current system state, metrics & health
│   ├── DESIGN_DECISIONS.md                     # Architectural Decision Records (ADRs) & resolutions
│   ├── DOCUMENTATION_INDEX.md                  # This file: navigation, hierarchy & authority index
│   ├── MECHANISM.md                            # Mathematical formulas, lifecycle, dataflow specifications
│   ├── Triết lý thiết kế AI cảm xúc.md         # Foundational concept paper (Vietnamese)
│   ├── USER_MANUAL.md                          # Complete user, configuration & operating manual
│   ├── phase9/                                 # Phase 9: Unified cognition specifications & Gate v2.0
│   └── screenshots/                            # Architectural UI & telemetry captures
├── .kiro/
│   └── specs/                                  # IMMUTABLE HISTORICAL MILESTONE SPECS
│       ├── lucia-core-phase1/                  # Phase 1: EmotionCore, Homeostasis, BoundaryLayer
│       ├── lucia-memory-phase2/                # Phase 2: SDM, AffectiveMemory, Decay, Ecphory
│       ├── lucia-ui-phase3/                    # Phase 3: Initial Electron 3-column UI & debug panel
│       ├── lucia-inference-phase4/             # Phase 4: Active Inference & CPU LNN Plasticity
│       ├── lucia-presence-phase5/              # Phase 5: [SUPERSEDED] Screen vision & ReAct agency
│       ├── lucia-refinement-phase6/            # Phase 6: Packaging, Mascot mode, Chat persistence, LSI
│       └── lucia-UI_refractoring-phase7/       # Phase 7: UI Refactoring design spec & product brief
├── electron/                                   # Native Electron desktop application
│   ├── main/                                   # Main process: ProcessManager, IPC, Mascot window
│   ├── preload/                                # ContextBridge security isolation
│   └── renderer/                               # Web client: Chat, 4-Engine Avatar, Settings, Journal, Simulation
├── models/                                     # Model weights & character assets
│   ├── avatar/                                 # Avatar assets (live2d/, sprites/, vrm/)
│   └── voice/                                  # Voice models (rvc/)
├── src/                                        # Python core backend (FastAPI, PyTorch, NumPy)
│   ├── api/                                    # REST API server & endpoints
│   └── core/                                   # Cognitive layers (emotion, gating, memory, simulation, voice)
└── tests/                                      # Comprehensive test suites
    ├── unit/                                   # Isolated unit tests
    ├── property/                               # Hypothesis property-based tests (P1 - P30)
    └── integration/                            # Multi-component pipeline tests
```

---

## 4. Reading Pathways by Persona

Depending on your role or objective, follow these curated reading sequences:

### Path A: Core AI & Backend Engineers
*Goal: Understand mathematical models, concurrency locks, and cognitive pipelines.*
1. [`docs/00_PROJECT_OVERVIEW.md`](file:///c:/Users/Lunafiah/Desktop/My_project/Lucia/docs/00_PROJECT_OVERVIEW.md) — Grasp the 6-layer cognitive flow.
2. [`docs/ARCHITECTURE.md`](file:///c:/Users/Lunafiah/Desktop/My_project/Lucia/docs/ARCHITECTURE.md) — Review concurrency model, threads, and hardware tiers.
3. [`docs/MECHANISM.md`](file:///c:/Users/Lunafiah/Desktop/My_project/Lucia/docs/MECHANISM.md) — Deep-dive into ODE differential equations, SDM Hamming space, and Ecphory.
4. [`docs/DESIGN_DECISIONS.md`](file:///c:/Users/Lunafiah/Desktop/My_project/Lucia/docs/DESIGN_DECISIONS.md) — Understand ADRs for CPU-only training and memory decay.
5. [`AGENTS.md`](file:///c:/Users/Lunafiah/Desktop/My_project/Lucia/AGENTS.md) — Review coding invariants and lock disciplines.

### Path B: Frontend & UI/UX Engineers
*Goal: Build interfaces adhering to the Personal Digital Room and avatar animation pipelines.*
1. [`.kiro/specs/lucia-UI_refractoring-phase7/new_UI_requirement.md`](file:///c:/Users/Lunafiah/Desktop/My_project/Lucia/.kiro/specs/lucia-UI_refractoring-phase7/new_UI_requirement.md) — Read the product brief and companion ontology.
2. [`.kiro/specs/lucia-UI_refractoring-phase7/PHASE_7_UI_REFACTORING_SPEC.md`](file:///c:/Users/Lunafiah/Desktop/My_project/Lucia/.kiro/specs/lucia-UI_refractoring-phase7/PHASE_7_UI_REFACTORING_SPEC.md) — Study CSS tokens, component layouts, and Mascot rules.
3. [`docs/MECHANISM.md`](file:///c:/Users/Lunafiah/Desktop/My_project/Lucia/docs/MECHANISM.md) (Section 2, Component 8) — Review `getModelBounds()` and hover zoom mathematics.
4. [`docs/CURRENT_STATUS.md`](file:///c:/Users/Lunafiah/Desktop/My_project/Lucia/docs/CURRENT_STATUS.md) — Review active UI refactoring tasks and open items.

### Path C: AI Coding Agents
*Goal: Implement features or fix bugs safely without violating architectural invariants.*
1. [`AGENTS.md`](file:///c:/Users/Lunafiah/Desktop/My_project/Lucia/AGENTS.md) — **MANDATORY**: Rules on pre-reflective emotion, one life ontology, and forbidden actions.
2. [`docs/CURRENT_STATUS.md`](file:///c:/Users/Lunafiah/Desktop/My_project/Lucia/docs/CURRENT_STATUS.md) — Check live subsystem health and active work areas.
3. [`docs/DESIGN_DECISIONS.md`](file:///c:/Users/Lunafiah/Desktop/My_project/Lucia/docs/DESIGN_DECISIONS.md) — Understand historical trade-offs and reconciled discrepancies.

### Path D: End Users & Companion Guardians
*Goal: Run, configure, and interact with Lucia.*
1. [`README.md`](file:///c:/Users/Lunafiah/Desktop/My_project/Lucia/README.md) — Quick start & dependencies.
2. [`docs/USER_MANUAL.md`](file:///c:/Users/Lunafiah/Desktop/My_project/Lucia/docs/USER_MANUAL.md) — Full operating instructions, shortcuts, RVC voice setup, and avatar installation.

---

## 5. Subject Cross-Reference Matrix

| Subject / Technical Topic | Primary Specification | Mathematical Deep Dive | Historical Spec |
|---|---|---|---|
| **Limbic Fast Loop (LTC LNN ODE)** | `docs/ARCHITECTURE.md` §3.2 | `docs/MECHANISM.md` §2 Comp 2 | `.kiro/specs/lucia-core-phase1/` |
| **Homeostasis & Somatic Markers** | `docs/ARCHITECTURE.md` §3.3 | `docs/MECHANISM.md` §2 Comp 3 | `.kiro/specs/lucia-core-phase1/` |
| **Active Inference & Plasticity** | `docs/ARCHITECTURE.md` §3.4 | `docs/MECHANISM.md` §2 Comp 4 | `.kiro/specs/lucia-inference-phase4/` |
| **Affective Memory & SDM** | `docs/ARCHITECTURE.md` §3.5 | `docs/MECHANISM.md` §2 Comp 5 | `.kiro/specs/lucia-memory-phase2/` |
| **Synergistic Ecphory** | `docs/ARCHITECTURE.md` §3.5 | `docs/MECHANISM.md` §2 Comp 5 | `.kiro/specs/lucia-memory-phase2/` |
| **RVC Voice Synthesis** | `docs/ARCHITECTURE.md` §3.6 | `docs/MECHANISM.md` §2 Comp 7 | `docs/USER_MANUAL.md` §2 |
| **Offline faster-whisper STT** | `docs/ARCHITECTURE.md` §4 | `docs/MECHANISM.md` §2 Comp 8 | `docs/USER_MANUAL.md` §6 |
| **Quad-Engine Avatar (Canvas/Sprites/Live2D/VRM)** | `docs/ARCHITECTURE.md` §3.6 | `docs/MECHANISM.md` §2 Comp 8 | `models/avatar/README.md` |
| **Mascot Window Dragging & Hover Zoom** | `docs/ARCHITECTURE.md` §4 | `docs/MECHANISM.md` §2 Comp 8 | `.kiro/specs/lucia-UI_refractoring-phase7/` |
| **Limbic Stability Evaluator (LSI)** | `docs/ARCHITECTURE.md` §5 | `docs/MECHANISM.md` §2 Comp 9 | `.kiro/specs/lucia-refinement-phase6/` |
| **UI Design System & Personal Room** | `PHASE_7_UI_REFACTORING_SPEC.md` | `new_UI_requirement.md` | `.kiro/specs/lucia-ui-phase3/` |
| **Session Persistence & Chat History** | `docs/MECHANISM.md` §2 Comp 6 | `docs/USER_MANUAL.md` §6 | `.kiro/specs/lucia-refinement-phase6/` |
| **Runtime Isolation & Dual Modes** | `PHASE_8.md` §3 | `PHASE_8_ARCHITECTURE_REVIEW.md` §2, §9 | `src/core/simulation/` |
| **Virtual SimClock & Time Warp** | `PHASE_8.md` §2.1 | `docs/MECHANISM.md` §2 Comp 10 | `src/core/simulation/sim_clock.py` |
| **Ephemeral Storage Policy** | `PHASE_8.md` §3 (INV-2, INV-3) | `PHASE_8_ARCHITECTURE_REVIEW.md` §5 | `src/core/simulation/storage_policy.py` |
| **Simulation UI Canopy & Drawer** | `PHASE_8.md` §2.5 | `PHASE_8_ARCHITECTURE_REVIEW.md` §2.2 | `electron/renderer/simulation/` |
| **Affective Dynamics & State Taxonomy** | `AFFECTIVE_DYNAMICS_SPEC.md` | `docs/MECHANISM.md` §2 Comp 2, 3 | `docs/specs/lucia-phase10-Affective_Dynamics/` |
| **Affective Memory & Recollection Coupling** | `AFFECTIVE_MEMORY_SPEC.md` | `docs/MECHANISM.md` §2 Comp 5 | `docs/specs/lucia-phase11-Affective_Memory/` |
| **Knowledge Learning Hierarchy (K0–K9)** | `KNOWLEDGE_LEARNING_SPEC.md` | `docs/MECHANISM.md` | `docs/specs/lucia-phase12-Knowledge_Learning/` |
| **Relationship Development & Philia Orientation** | `RELATIONSHIP_DEVELOPMENT_SPEC.md` | `docs/MECHANISM.md` | `docs/specs/lucia-phase13-Relationship_Development/` |

