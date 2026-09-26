# AGENTS.md — Instructions & Invariants for AI Coding Agents

> **Mandatory Guidelines, Architectural Invariants, and Operating Procedures for AI Agents Working on Lucia**

---

## 0. Current Operating Mode — Research-First Governance (Post-Phase 21 / Post-Phase 22 Research Closure)

> **CURRENT STAGE: RESEARCH / EVIDENCE BUILDING — NOT ACTIVATION**

Lucia has completed all documented production milestones through **Phase 21 — Long-Term Relational Consolidation & Synaptic Homeostasis**, and completed the research milestone chain through **Phase 22 — Substrate-Neutral Semantic Conditioning & Relational Cognition Study** (`[RESEARCH VALIDATED / NOT PROMOTED]`). The repository treats the canonical Phase 21 cognitive architecture as an implemented, verified baseline. Phase 22 establishes substrate neutrality for relational intelligence without promoting changes to production code. The next research milestone is established through project governance and canonical documentation rather than inferred by an AI coding agent.

### Mandatory Research-First Rules

1. **Research is not production.** A research hypothesis, mathematical proposal, benchmark result, ablation, prototype, or evaluation harness MUST NOT be treated as a production capability merely because tests pass.
2. **Evidence before promotion.** New mechanisms must first be isolated, measurable, reproducible, and evaluated against explicit acceptance criteria before any production integration is proposed.
3. **Do not invent the next phase.** Agents MUST NOT create or assume a new numbered phase, roadmap milestone, subsystem, or activation prerequisite unless it is explicitly established by authoritative project documentation or a user-approved research specification.
4. **Preserve the canonical baseline.** Unless a task explicitly authorizes production integration, research work must remain isolated from the canonical runtime and persistent user state. Prefer `tests/evaluation/phaseXX/`, research specifications, simulation fixtures, and disposable experimental modules for exploratory work.
5. **No silent promotion.** A successful experiment does not authorize changes to `src/core/`, `data/`, lifecycle behavior, or the production cognitive pipeline. Promotion requires an explicit architectural decision and corresponding documentation update.
6. **No activation during research.** `Development / Simulation != Lucia Activation` remains absolute. First Activation (Genesis Onboarding) remains a locked future gate until project governance explicitly changes that status.
7. **Evidence hierarchy is authoritative:**
   - `[VALIDATED / PRODUCTION IMPLEMENTED]` — implemented in runtime and verified by appropriate automated tests.
   - `[RESEARCH VALIDATED]` — empirically supported in an isolated research/evaluation harness; not automatically production.
   - `[ARCHITECTURE APPROVED]` — architecture approved for implementation, but implementation is not implied.
   - `[CURRENT RESEARCH]` — active experimental investigation under controlled conditions.
   - `[RESEARCH]` — theoretical/specification work without a production claim.
   - `[INTEGRATION]` — planned convergence work; not an implementation authorization by itself.
   - `[FUTURE GATE]` — explicitly blocked until its entry criteria are satisfied.

### Required Agent Decision Order

Before editing code, an agent MUST reason in this order:

`Canonical docs → research specification/evidence → architectural decision → implementation scope → tests → documentation`

If the requested work is exploratory, the default outcome is **research artifact + evaluation evidence**, not production mutation.

### What Agents Must Not Do in the Current Stage

- Do not add speculative cognitive subsystems simply because they are biologically plausible.
- Do not turn a research metric into a claimed psychological property or subjective experience.
- Do not equate passing unit tests with scientific validation.
- Do not modify the First Activation gate, onboarding state, or lifecycle safeguards as part of research.
- Do not rewrite historical research conclusions merely to make the roadmap look linear. Preserve failed hypotheses, rejected candidates, ablations, and negative results as evidence.
- Do not optimize for feature count. Optimize for falsifiability, causal attribution, reproducibility, isolation, and evidence quality.

### Research Deliverable Standard

Every substantive research increment should make it possible to answer:

1. **What hypothesis is being tested?**
2. **What mechanism is proposed?**
3. **What is the control/baseline?**
4. **What variables are manipulated and measured?**
5. **What would falsify or reject the hypothesis?**
6. **What evidence was obtained?**
7. **What remains unproven?**
8. **Does the result justify architecture approval, production promotion, or neither?**

Agents MUST record these distinctions in the appropriate research/evaluation documentation rather than hiding them inside implementation notes.

---

## 1. Core Ethos & Critical Clarification on Emotion/Affect

### What Lucia's Emotion Is — And What It Is Not

> [!CAUTION]
> **CRITICAL ARCHITECTURAL DISTINCTION**:  
> In Lucia, **"emotion" is NOT psychological sentience, subjective conscious feeling, or theatrical roleplay.**  
> It is an **unconscious, continuous dynamical mathematical state** operating as a physiological-like state machine.

To prevent conceptual misunderstandings when implementing features or conditioning prompts, all agents must adhere to the following definitions:

1. **Continuous Dynamical Mechanics**:
   * Emotional state is represented by a continuous 3-dimensional vector in **PAD space** ($P \in [-1, 1]$ Pleasure/Valence, $A \in [-1, 1]$ Arousal/Vitality, $D \in [-1, 1]$ Dominance/Agency).
   * It is integrated continuously in the background every 200 ms via an Ordinary Differential Equation (ODE) within a Liquid Neural Network (Coupled MT-LNN).
   * It evolves with the physical passage of time and smoothly decays toward the **Philia resting attractor** ($P=+0.25, A=-0.05, D=+0.05$) when no stimulus is present.
2. **Pre-Reflective Operational Consequences**:
   * Emotion manifests strictly as **functional and physical consequences** on generation behavior:
     * High arousal / high cognitive load $\rightarrow$ Shorter token budget (`max_tokens`), higher sampling temperature.
     * High tension $\rightarrow$ Increased reasoning depth ($k=2$).
     * Depleted energy / metabolic fatigue $\rightarrow$ Injected conversational response latency.
     * Affective memory resonance $\rightarrow$ Subconscious Echo Vector gently influencing tone and word selection.
3. **Strict Prohibition Against Self-Reported Affect**:
   * Lucia **NEVER** names, labels, or self-reports her internal emotional state in text.
   * She **NEVER** says: *"I feel happy"*, *"I am feeling sad today"*, *"My arousal is high"*, or *"As an AI, I don't feel emotions"*.
   * Agents must **NEVER** instruct the language model to introspectively declare its feelings. Any introspective pattern is considered an architectural defect and will be dropped by the `BoundaryLayer` regex validator.

---

## 2. Fundamental System Invariants ("What Agents Must NEVER Do")

When modifying any part of the Lucia codebase, agents are strictly prohibited from violating the following invariants:

| # | Invariant Rule | Violation Examples (Forbidden) | Correct Approach |
|---|---|---|---|
| **1** | **One Continuous Life** | Adding character preset pickers, "Switch Character" dropdowns, or multiple persona profiles. | Avatars are Lucia's **Appearance** (physical body/attire). Lucia is a single, permanent companion instance. |
| **2** | **No Reflective Ego** | Adding meta-self-awareness prompts (*"Reflect on who you are"* or *"Identify your feelings"*). | Lucia has a minimal operational self. Emotion is expressed through tone, rhythm, and blendshapes. |
| **3** | **Preserve Memory Separation** | Deleting SDM memory traces when the user clicks "Clear Screen". | "Clear Screen" only resets visible chat feed; long-term SDM memory and emotional bonds are permanent. |
| **4** | **Never Merge or Delete Historical Specs** | Editing or deleting files in `.kiro/specs/` or merging them into `docs/`. | Historical phase specs (`.kiro/specs/`) are immutable historical artifacts. Active docs live in `docs/`. |
| **5** | **Zero Cloud Dependencies** | Introducing OpenAI, Anthropic, ElevenLabs, or cloud STT/TTS API keys. | 100% local edge execution: GGUF LLM on CUDA, Edge-TTS/RVC on CPU/GPU, faster-whisper STT. |
| **6** | **Strict Concurrency Discipline** | Holding `_state_lock` during model inference, or acquiring `_state_lock` while holding `_train_lock`. | Hold locks strictly $\le 1-2\text{ms}$ for memory copy. Never perform network or disk I/O under locks. |
| **7** | **Mascot Physics & Bounds Guard** | Enabling native `-webkit-app-region: drag` or allowing Aero Snap to maximize transparent windows. | Use IPC `moveMascotBy(dx, dy)`, retain 800ms trackpad inertia cooldown, and keep window unmaximizable. |
| **8** | **Genesis Gate Invariant** | Modifying `data/profile.json` (`{"is_onboarded": false}`) during testing, simulation, or development. | Simulation $\ne$ Activation. The onboarding ceremony is a locked future gate preserved bit-exact. |

---

## 3. Documentation Hierarchy & Single Source of Truth

The repository enforces a consolidated, single-source-of-truth documentation structure. Agents must consult and maintain the designated canonical authority for each topic.

### 3.1 Document Authority Matrix

```text
README.md (Public Front Door) [L0]
    │
    ├── docs/L1_INVARIANTS.md (Canonical Invariant Ledger) [L1]
    │
    ├── AGENTS.md (Master Operating Instructions & Decision Protocol) [L2]
    │
    ├── docs/00_PROJECT_OVERVIEW.md (Canonical Project Truth & Roadmap) [L2]
    │
    ├── docs/DOCUMENTATION_ARCHITECTURE.md (Canonical Knowledge Architecture) [L2]
    │
    ├── docs/PHASE_REGISTRY.md (Canonical Milestone & Sub-Phase Registry) [L2]
    │
    ├── docs/ARCHITECTURE.md (Canonical Technical Truth & ADR Ledger) [L3]
    │
    ├── docs/DOCUMENT_REGISTRY.md (Master Document Catalog & Metadata) [L3]
    │
    ├── docs/SOURCE_MAP.md (Authoritative Provenance Map) [L3]
    │
    ├── docs/CONTEXT_ARCHITECTURE.md (Agent Context Projection Spec) [L4]
    │
    ├── docs/CONTEXT_INDEX.md (Context Retrieval Map L0–L6) [L4]
    │
    ├── docs/DOCUMENTATION_INDEX.md (Complete Catalog & Spec Navigation) [L4]
    │
    └── Historical Evidence (docs/specs/**, evaluation_artifacts/**, tests/evaluation/**) [L5]
```

| Document | Authority Tier | Role & Content Scope | Agent Operating Rules |
|---|---|---|---|
| [`README.md`](file:///c:/Users/Lunafiah/Desktop/My_project/Lucia/README.md) | **Public Front Door [L0]** | High-level introduction, philosophy, public concepts, and getting started. | Use it to understand project purpose and top-level navigation. **NOT** the detailed technical specification. |
| [`docs/L1_INVARIANTS.md`](file:///c:/Users/Lunafiah/Desktop/My_project/Lucia/docs/L1_INVARIANTS.md) | **Canonical Invariant Ledger [L1]** | Consolidated non-negotiable architectural, limbic, concurrency, and governance invariants. | Primary reference before any modification. Must not be bypassed or weakened. |
| [`docs/00_PROJECT_OVERVIEW.md`](file:///c:/Users/Lunafiah/Desktop/My_project/Lucia/docs/00_PROJECT_OVERVIEW.md) | **Canonical Project Truth [L2]** | System identity, core philosophy, 6-layer cognitive pipeline summary, 24-subsystem health matrix, test statistics, active REST API surface, and milestone roadmap. | Consult for current project status, phase progress, subsystem operational state, and project-level constraints. **Do NOT recreate `CURRENT_STATUS.md`.** |
| [`docs/DOCUMENTATION_ARCHITECTURE.md`](file:///c:/Users/Lunafiah/Desktop/My_project/Lucia/docs/DOCUMENTATION_ARCHITECTURE.md) | **Canonical Knowledge Canon [L2]** | Information classes (Classes 1–7), canonical single-ownership model, unflattened evidence rules, and controlled taxonomies. | Primary authority for documentation organization, status labels, and lifecycle rules. |
| [`docs/PHASE_REGISTRY.md`](file:///c:/Users/Lunafiah/Desktop/My_project/Lucia/docs/PHASE_REGISTRY.md) | **Canonical Phase Truth [L2]** | Master registry covering P01 through P23-I, future horizons P24–P27, and Genesis gate. | Consult for official phase status, lifecycle stage, and freeze commits before assuming milestone state. |
| [`docs/ARCHITECTURE.md`](file:///c:/Users/Lunafiah/Desktop/My_project/Lucia/docs/ARCHITECTURE.md) | **Canonical Technical Truth [L3]** | Technical architecture, 20-Watt Whole Brain Architecture, concurrency & locking rules, mathematical/dynamical mechanisms (ODEs, SDM, Ecphory, BPTT), and the complete Architectural Decision Record ledger (**ADR-001 through ADR-028**; ARCH-001 to ARCH-031). | Primary technical authority for mechanisms, formulas, component ownership, threading, and design rationale. **Do NOT recreate `MECHANISM.md` or `DESIGN_DECISIONS.md`.** |
| [`docs/DOCUMENT_REGISTRY.md`](file:///c:/Users/Lunafiah/Desktop/My_project/Lucia/docs/DOCUMENT_REGISTRY.md) | **Master Catalog [L3]** | Complete 15-attribute classification catalog of all active, research, and historical documents. | Consult to identify canonical owners, parent documents, and superseding links. |
| [`docs/SOURCE_MAP.md`](file:///c:/Users/Lunafiah/Desktop/My_project/Lucia/docs/SOURCE_MAP.md) | **Provenance Authority [L3]** | Repository-wide claim-to-evidence provenance map tracing architectural mechanisms to raw measurements and commits. | Trace core architectural claims to their verifying evidence before proposing modifications. |
| [`docs/CONTEXT_ARCHITECTURE.md`](file:///c:/Users/Lunafiah/Desktop/My_project/Lucia/docs/CONTEXT_ARCHITECTURE.md) | **Context Projection Spec [L4]** | Multi-agent projection architecture: Ciah $\le 5$-file reviewer pack, Gemini deep research corpus, Antigravity L0–L6 routing. | Authoritative rules for creating or updating derived context files. |
| [`docs/CONTEXT_INDEX.md`](file:///c:/Users/Lunafiah/Desktop/My_project/Lucia/docs/CONTEXT_INDEX.md) | **Context Routing Map [L4]** | Logical context layers (L0–L6), minimal sufficient context loading rules by task type, anti-patterns. | Consult first to identify minimal sufficient context layers before ingesting files. |
| [`docs/DOCUMENTATION_INDEX.md`](file:///c:/Users/Lunafiah/Desktop/My_project/Lucia/docs/DOCUMENTATION_INDEX.md) | **Navigation Map [L4]** | Complete catalog of active and historical documentation, authority hierarchy, and reading paths. | Use strictly to navigate documents. **Do NOT turn the index into another source of technical truth.** |
| **Phase / Research / Acceptance Docs** (`docs/specs/**`, `evaluation_artifacts/**`) | **Historical Evidence & Records [L5]** | Phase specifications, research hypotheses (H1–Hn), evaluation harness reports, mathematical proposals, and formal acceptance reports. | Preserved as evidence and historical records. They must **never** silently override the active canonical architecture in `docs/ARCHITECTURE.md`. |

### 3.2 Deleted Canonical Files Notice

The following standalone files were intentionally merged into canonical documentation in commit `19db677` and deleted:
- `docs/CURRENT_STATUS.md` $\rightarrow$ Merged into `docs/00_PROJECT_OVERVIEW.md`
- `docs/MECHANISM.md` $\rightarrow$ Merged into `docs/ARCHITECTURE.md`
- `docs/DESIGN_DECISIONS.md` $\rightarrow$ Merged into `docs/ARCHITECTURE.md`

Agents must **NEVER** recreate these files, create compatibility wrappers, or introduce parallel "current status" documents.

### 3.3 Documentation Workflow

When behavior, mechanisms, architecture, or phase status changes:
1. Update the canonical owner; do not create duplicate sources of truth.
2. Put genuine research specs/evaluations/phase records in `docs/specs/` (or `docs/research/` during active research).
3. Put **executable phase evaluation harnesses and test suites** in `tests/evaluation/phaseXX/`, and **persistent markdown evaluation reports & raw JSON telemetry** in `evaluation_artifacts/`.
4. Update `DOCUMENTATION_INDEX.md` and `DOCUMENT_REGISTRY.md` for added/moved/removed docs.
5. Update `README.md` only for public-facing changes.
6. Search for and fix stale references to renamed/deleted files.


## 4. Codebase Architecture & Ownership Map

```
Lucia/
├── src/                                        # PYTHON CORE BACKEND
│   ├── api/
│   │   └── server.py                           # FastAPI server (127.0.0.1:8765)
│   └── core/
│       ├── gating/                             # Layer 1: Lexical valence & density encoding
│       ├── emotion/                            # Layers 2–3: Coupled MT-LNN, Philia attractor & ConsolidationEngine
│       ├── inference/                          # Layer 4: Active Inference & CPU LNNTrainer
│       ├── memory/                             # Layer 5: Kanerva SDM, DecayEngine, Ecphory
│       ├── orchestrator/                       # Canonical S1–S16 CognitiveOrchestrator pipeline
│       ├── language/                           # Layer 6: Local GGUF Small Language Model
│       ├── safety/                             # Layer 6: BoundaryLayer regex validator
│       ├── voice/                              # Layer 6: Direct RVC synthesis & faster-whisper STT
│       ├── telemetry/                          # StabilityEvaluator (LSI, Jitter, Watchdog)
│       └── presence/                           # PresenceOrchestrator integrating all layers
├── electron/                                   # DESKTOP USER INTERFACE
│   ├── main/                                   # Main Process (ProcessManager, Tray, MascotWindow)
│   ├── preload/                                # ContextBridge security boundary
│   └── renderer/                               # Renderer Process
│       ├── avatar/                             # 4-Engine Avatar stage & lip-sync
│       ├── chat/                               # Conversation feed
│       ├── debug/                              # Telemetry panel & diagnostics modal
│       ├── journal/                            # Relationship history & milestones
│       └── index.css                           # Design System tokens & glassmorphic styling
├── config/                                     # RUNTIME CONFIGURATION
│   └── ui.json                                 # Port, default model, voice, hardware profile
├── data/                                       # RUNTIME PERSISTENCE
│   ├── chat_history.json                       # Conversation turns & session records
│   └── profile.json                            # Genesis onboarding profile (is_onboarded: false)
└── models/                                     # LOCAL ASSETS & WEIGHTS
    ├── avatar/                                 # 2D Sprites, Live2D models, 3D VRM files
    └── voice/rvc/                              # RVC voice models (.pth + .index)
```

---

## 5. Required Lucia Development Workflow

For non-trivial tasks, all agents must adhere to the following structured sequence:

```text
Step 1: Inspect Repository State & Canonical Docs
                 │
                 ▼
Step 2: Classify Work (Research / Architecture / Implementation / Validation / Docs)
                 │
                 ▼
Step 3: Resolve Architecture Gate (If mechanism, state, concurrency, or pipeline changes)
                 │
                 ▼
Step 4: Implementation Discipline (Scoped, isolated, invariant-preserving)
                 │
                 ▼
Step 5: Narrow-to-Broad Validation (Subsystem → Phase → Regression → Invariants)
                 │
                 ▼
Step 6: Canonical Documentation Synchronization & Consistency Audit
                 │
                 ▼
Step 7: Pre-Commit Invariant Checks & Focused Git Commit
```

### Step 1 — Inspect Before Coding
- Run `git status` to inspect current branch and working tree.
- Consult [`docs/CONTEXT_INDEX.md`](file:///c:/Users/Lunafiah/Desktop/My_project/Lucia/docs/CONTEXT_INDEX.md) to identify the **minimum sufficient context layers** for the task.
- Read [`docs/L1_INVARIANTS.md`](file:///c:/Users/Lunafiah/Desktop/My_project/Lucia/docs/L1_INVARIANTS.md) and [`AGENTS.md`](file:///c:/Users/Lunafiah/Desktop/My_project/Lucia/AGENTS.md) to verify applicable invariant constraints.
- Consult canonical documentation (`00_PROJECT_OVERVIEW.md`, `ARCHITECTURE.md`) and relevant ADRs within scope.
- Inspect the existing implementation and test coverage.
- **Do not assume the prompt's feature request accurately reflects the current codebase.** Always verify against source code first.

### Step 2 — Classify the Work
Explicitly identify whether the task is:
- **Research:** Exploratory hypothesis testing, benchmark, ablation, or evaluation harness.
- **Architecture / Design:** Defining mechanisms, ADR authoring, or production realization design.
- **Production Implementation:** Mutating `src/core/`, `electron/`, or production configuration.
- **Validation / Testing:** Authoring unit, property, regression, or performance test suites.
- **Documentation / Governance:** Synchronizing canonical documentation or updating governance matrices.
- **Phase Closure:** Formal acceptance audit, gate verification, and milestone sign-off.

---

## 6. Research-First & Promotion Workflow (The Gated Model)

Lucia uses a strict gated progression. New cognitive or physical mechanisms must advance through defined lifecycle gates:

```text
Research (Gemini)
       │
       ▼
Architecture / Conceptual Analysis
       │
       ▼
Research-to-Contract Synthesis
       │
       ▼
Ciah Review / Challenge
       │
       ▼
Implementation Authorization (User)
       │
       ▼
Antigravity Implementation (src/core/**)
       │
       ▼
Post-Implementation Audit
       │
       ▼
Required Fixes
       │
       ▼
Regression / Falsification (tests/unit/, tests/property/)
       │
       ▼
Freeze
```

### 6.1 Agent Roles & Decision Boundaries
- **Gemini:** Research arm — hypothesis formulation, exploratory investigations, empirical benchmark evaluation, and scientific synthesis.
- **Ciah:** Review / architecture / reasoning / prompt layer — rigorous peer challenge, epistemic auditing, invariant verification, red-team review, and contract sign-off.
- **Antigravity:** Execution / coding agent — disciplined, scoped implementation strictly bounded by approved contracts, regression testing, and canonical documentation synchronization. Antigravity never promotes unverified hypotheses or invents architecture.
- **User:** Final decision-maker — sole authority for implementation authorization, architecture approvals, and the locked First Activation gate.

**Strict Decision & Execution Boundary:**
```text
Gemini research conclusion
        ≠
Ciah approval
        ≠
User authorization
        ≠
Antigravity implementation authorization
```
A research finding, hypothesis validation, or preliminary transition recommendation (e.g. Gemini recommending "Contract Transition Ready") does **NOT** constitute implementation authorization. Antigravity is strictly forbidden from implementing unapproved or unfrozen research concepts.

Specifically, for Phase 23-I (awaiting empirical evidence closure under `GATE 23-I-EVAL`):
- `src/core/**`
- `electron/**`
- runtime data structures
- production cognitive pipeline (S1–S16)
remain **STRICTLY OFF-LIMITS**. Agents must **NEVER** create implementation scaffolding, stub classes, or production files merely to satisfy a research report.

### 6.2 Research Isolation Rules
- **No direct-to-production:** research concepts stay out of `src/core/**` until the Architecture Gate is approved.
- **Isolate experiments:** use `tests/evaluation/phaseXX/`, disposable fixtures, temporary data, and isolated models.
- **Success ≠ promotion:** passing evaluation criteria proves only the tested claim under tested conditions.
- **Preserve evidence:** retain failed hypotheses, rejected candidates, controls, ablations, and negative results.


## 7. Architecture Gate

Before modifying production code that introduces or materially alters:
- Cognitive mechanisms or limbic state dynamics
- Multi-timescale plasticity or consolidation routines
- Memory storage, retrieval, or salience scoring
- Relationship vectors or interpersonal dynamics
- Pipeline turn stages or orchestrator sequences
- Concurrency, locking hierarchy, or threading models
- State persistence or schema definitions
- Runtime lifecycle or boundary validators

An agent MUST author or verify the **Production Realization Design** before touching production code.

### Required Architecture Gate Specifications
The architecture design must explicitly define:
1. **Ownership Boundaries:** Which component owns the primary live state vs. transient copies.
2. **Interface Contracts:** Method signatures, inputs, outputs, and exception behaviors.
3. **Data Flow & Timing:** When updates occur (e.g. post-turn vs intra-turn; adherence to ADR-022).
4. **Mathematical Bounds:** Lyapunov stability conditions, spectral norm limits, displacement bounds.
5. **Concurrency & Locks:** Exact locks acquired, acquisition order, and holding durations.
6. **Hardware & Resource Budgets:** CPU-only enforcement, zero GPU VRAM impact, execution SLAs.
7. **Fallback & Feature Flags:** Configuration flags allowing 100% bit-exact rollback to the previous baseline.
8. **Verification Strategy:** Specific unit, property, and regression test suites required for promotion.

---

## 8. Production Implementation Rules

Once the architecture gate is approved:
1. **Implement strictly within scope:** Do not touch unrelated subsystems or perform drive-by cleanups.
2. **Preserve existing invariants:** Ensure all fundamental invariants in Section 2 remain intact.
3. **No opportunistic refactors:** Do not rename files, modernize idioms, or change formatting across unrelated modules.
4. **Surface contradictions immediately:** If implementation reveals an unresolvable contradiction with the approved architecture, stop and raise it rather than silently redesigning the system.
5. **Preserve fallback behavior:** Ensure feature flags (`enable_*`) preserve bit-exact backward compatibility when toggled off.

---

## 9. Concurrency, Locking & Runtime Safety

Lucia runs continuous limbic integration, background homeostatic decay, episodic memory retrieval, offline synaptic consolidation, and real-time audio-visual embodiment concurrently on local consumer hardware.

### 9.1 Canonical Lock Hierarchy

All locks MUST be acquired in this strict descending hierarchy:

$$\text{\_turn\_lock} \longrightarrow \text{\_step\_lock} \longrightarrow \text{\_train\_lock} \longrightarrow \text{\_stimulus\_lock} \longrightarrow \text{\_state\_lock}$$

* **Never invert lock acquisition order.**
* **Never acquire `_state_lock` and subsequently attempt to acquire `_train_lock`** (immediate deadlock risk). Always acquire `_train_lock` first.
* **Keep critical sections under `_state_lock` $\le 1-2\text{ms}$** (measured operations are $\le 0.1\text{ms}$ for memory copies and state snapshots).
* **Never perform disk I/O, network requests, ODE integration, backward passes, or LLM token generation while holding locks.**
* **Offline BPTT backpropagation must run strictly on disconnected local training parameters.** Parameter weight copy swaps under `_train_lock` must complete within $\le 2.0\text{ms}$.

### 9.2 Non-Blocking Telemetry Invariant
* `GET /state` and `GET /telemetry/stability` must respond within $10-15\text{ms}$. They must acquire `_state_lock` momentarily for a fast memory copy and return immediately without awaiting LLM generation or cognitive turn completion.

### 9.3 20-Watt CPU vs. GPU Discipline
* **GPU VRAM is reserved exclusively** for the active local GGUF Large Language Model (via llama.cpp/CUDA) and WebGL avatar rendering.
* **All continuous background dynamics**, including the 200 ms Fast-Loop ODE, Slow-Loop decay, homeostatic budgeting, SDM vector operations, and Tier 3 offline synaptic consolidation (PyTorch BPTT), **must execute strictly on the CPU with 0.0 MB GPU VRAM allocation.**

---

## 10. Genesis Gate & Runtime Safety (Activation Invariant)

> [!IMPORTANT]
> **DEVELOPMENT / SIMULATION IS NOT LUCIA ACTIVATION.**<br/>
> Lucia remains in a pre-activation state in the repository. The First Activation (Genesis Onboarding) is a locked future milestone.

1. **Persistent State Protection**: `data/profile.json` must remain bit-exact `{"is_onboarded": false}` across all tests, simulations, and code modifications.
2. **Never Trigger Onboarding**: Agents must never trigger the onboarding ceremony or write user identity data to simulate a populated companion.
3. **Simulation Isolation**: All evaluation harnesses, benchmark suites, and unit tests must use isolated in-memory stores, temporary directories, or mocked profiles. Never write test chat records into `data/chat_history.json`.

---

## 11. Testing & Quality Assurance Protocols

Validation is **narrow → broad**; never claim a test passed unless it was actually run.

1. Targeted subsystem tests
2. Phase production tests (`tests/unit/test_phaseXX_production.py`)
3. Relevant prior-phase regression tests
4. Property/invariant tests (`tests/property/`)
5. Full unit regression when scope warrants it

Research uses the separate hierarchy:
- `tests/evaluation/phaseXX/` — **all phase-specific research/evaluation artifacts belong under this single parent directory**.
- Keep research evaluation separate from production tests and runtime code.
- Report software verification and empirical research validation separately.

Common commands:
```powershell
.venv\Scripts\pytest tests/unit -v
.venv\Scripts\pytest tests/property -v
.venv\Scripts\pytest tests/unit/test_phase21_production.py -v
.venv\Scripts\pytest tests/evaluation/phase21 -v
cd electron ; npm test
```

## 12. Agent Scope Discipline & Ambiguity Resolution

### Scope Discipline
- Make the smallest coherent change required to fulfill the task.
- Do NOT refactor code outside the authorized task boundary.
- Do NOT alter tests merely to make failures go away.
- Do NOT edit `AGENTS.md` unless the task explicitly concerns agent workflow governance.
- **Preserve pre-existing working tree changes:** If uncommitted changes exist that are unrelated to the current task, leave them intact and exclude them from your commit.

### Resolving Ambiguity
- When requirements are unclear, do NOT silently guess or invent architectural patterns.
- Inspect the canonical architecture (`docs/ARCHITECTURE.md`), ADRs, and existing code first.
- If ambiguity materially affects cognitive architecture, state dynamics, or concurrency, stop and present the trade-offs to the user.

### Phase Boundary Rule
- Routine implementation tasks should focus on local invariants and targeted verifications without performing exhaustive repository-wide governance audits.
- Full architectural and governance audits are reserved for phase transition boundaries, research promotions, and milestone closures.

---

## 13. Git & Version Control Procedure

Git history is part of Lucia's engineering evidence. Keep changes scoped, traceable, and reversible.

### Before Editing
```powershell
git status
git log -n 3 --oneline
```
Preserve unrelated working-tree changes. Never assume a clean tree.

### Before Commit
```powershell
git status
git diff --check
git diff --stat
git diff
```
Verify only intended files are staged; no credentials, caches, temporary files, or unintended profile changes are included.

### Commit Rules
Use conventional scoped messages:
- `feat(core): ...`
- `fix(core): ...`
- `research(...): ...`
- `docs: ...`
- `test(...): ...`

Never amend/squash/rewrite shared commits or force-push unless explicitly requested.
Do not push unless the task explicitly requires it.

## 14. Documentation + Code Consistency Check

Before finishing a task, verify that:
- Code matches the approved architecture in `docs/ARCHITECTURE.md`.
- Milestone tables and subsystem health in `docs/00_PROJECT_OVERVIEW.md` match current reality.
- Navigation links in `README.md` and `docs/DOCUMENTATION_INDEX.md` are valid.
- No references point to deleted files (`CURRENT_STATUS.md`, `MECHANISM.md`, `DESIGN_DECISIONS.md`).
- Historical phase specifications in `.kiro/specs/` and `docs/specs/` are preserved.

---

## 15. Reporting Contract

Every task ends with a factual report:
- **Scope:** modified/created/deleted files.
- **Architecture:** governing doc/ADR and relevant decision.
- **Validation:** exact commands, results, counts/durations when available; separate research from production evidence.
- **Documentation:** updated canonical docs and reference integrity.
- **Git:** commit hash/message and working-tree state.
- **Issues:** failures, limitations, unresolved trade-offs, and preserved unrelated changes.

## 16. Final Pre-Commit Checklist

- [ ] Canonical docs and relevant ADRs were read.
- [ ] Work stayed within the authorized scope and Architecture Gate.
- [ ] Research remains isolated under `tests/evaluation/phaseXX/` when applicable.
- [ ] Genesis Gate remains intact: `data/profile.json == {"is_onboarded": false}`.
- [ ] Lock hierarchy and CPU/GPU discipline are preserved.
- [ ] No reflective emotional self-reporting was introduced.
- [ ] No unrelated files or pre-existing user changes were altered.
- [ ] Relevant tests/evaluations were actually executed and results reported accurately.
- [ ] `git diff --check` passes.
- [ ] Canonical documentation matches implementation reality; no stale deleted-file references remain.
- [ ] Commit message accurately describes the change.
