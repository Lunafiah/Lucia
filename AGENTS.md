# AGENTS.md — Instructions & Invariants for AI Coding Agents

> **Mandatory Guidelines, Architectural Invariants, and Operating Procedures for AI Agents Working on Lucia**

---

## 0. Current Operating Mode — Research-First Governance (Post-Phase 21)

> **CURRENT STAGE: RESEARCH / EVIDENCE BUILDING — NOT ACTIVATION**

Lucia has completed all documented production and research milestones through **Phase 21 — Long-Term Relational Consolidation & Synaptic Homeostasis**. The repository treats the canonical cognitive architecture as an implemented, verified baseline. The next research milestone is established through project governance and canonical documentation rather than inferred by an AI coding agent.

### Mandatory Research-First Rules

1. **Research is not production.** A research hypothesis, mathematical proposal, benchmark result, ablation, prototype, or evaluation harness MUST NOT be treated as a production capability merely because tests pass.
2. **Evidence before promotion.** New mechanisms must first be isolated, measurable, reproducible, and evaluated against explicit acceptance criteria before any production integration is proposed.
3. **Do not invent the next phase.** Agents MUST NOT create or assume a new numbered phase, roadmap milestone, subsystem, or activation prerequisite unless it is explicitly established by authoritative project documentation or a user-approved research specification.
4. **Preserve the canonical baseline.** Unless a task explicitly authorizes production integration, research work must remain isolated from the canonical runtime and persistent user state. Prefer `tests/evaluation_*`, research specifications, simulation fixtures, and disposable experimental modules for exploratory work.
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
README.md (Public Front Door)
    │
    ├── docs/00_PROJECT_OVERVIEW.md (Canonical Project Truth)
    │
    ├── docs/ARCHITECTURE.md (Canonical Technical Truth & ADR Ledger)
    │
    ├── docs/DOCUMENTATION_INDEX.md (Navigation Map Only)
    │
    └── Historical Evidence (docs/specs/**, .kiro/specs/**, docs/reports/**)
```

| Document | Authority Tier | Role & Content Scope | Agent Operating Rules |
|---|---|---|---|
| [`README.md`](file:///c:/Users/Lunafiah/Desktop/My_project/Lucia/README.md) | **Public Front Door** | High-level introduction, philosophy, public concepts, and getting started. | Use it to understand project purpose and top-level navigation. **NOT** the detailed technical specification. |
| [`docs/00_PROJECT_OVERVIEW.md`](file:///c:/Users/Lunafiah/Desktop/My_project/Lucia/docs/00_PROJECT_OVERVIEW.md) | **Canonical Project Truth** | System identity, core philosophy, 6-layer cognitive pipeline summary, 24-subsystem health matrix, test statistics, active REST API surface, and milestone roadmap. | Consult for current project status, phase progress, subsystem operational state, and project-level constraints. **Do NOT recreate `CURRENT_STATUS.md`.** |
| [`docs/ARCHITECTURE.md`](file:///c:/Users/Lunafiah/Desktop/My_project/Lucia/docs/ARCHITECTURE.md) | **Canonical Technical Truth** | Technical architecture, 20-Watt Whole Brain Architecture, concurrency & locking rules, mathematical/dynamical mechanisms (ODEs, SDM, Ecphory, BPTT), and the complete Architectural Decision Record ledger (**ADR-001 through ADR-028**). | Primary technical authority for mechanisms, formulas, component ownership, threading, and design rationale. **Do NOT recreate `MECHANISM.md` or `DESIGN_DECISIONS.md`.** |
| [`docs/DOCUMENTATION_INDEX.md`](file:///c:/Users/Lunafiah/Desktop/My_project/Lucia/docs/DOCUMENTATION_INDEX.md) | **Navigation Map** | Complete catalog of active and historical documentation, authority hierarchy, and reading paths. | Use strictly to navigate documents. **Do NOT turn the index into another source of technical truth.** |
| **Phase / Research / Acceptance Docs** (`docs/specs/**`, `.kiro/specs/**`) | **Historical Evidence & Records** | Phase specifications, research hypotheses (H1–Hn), evaluation harness reports, mathematical proposals, and formal acceptance reports. | Preserved as evidence and historical records. They must **never** silently override the active canonical architecture in `docs/ARCHITECTURE.md`. |

### 3.2 Deleted Canonical Files Notice

The following standalone files were intentionally merged into canonical documentation in commit `19db677` and deleted:
- `docs/CURRENT_STATUS.md` $\rightarrow$ Merged into `docs/00_PROJECT_OVERVIEW.md`
- `docs/MECHANISM.md` $\rightarrow$ Merged into `docs/ARCHITECTURE.md`
- `docs/DESIGN_DECISIONS.md` $\rightarrow$ Merged into `docs/ARCHITECTURE.md`

Agents must **NEVER** recreate these files, create compatibility wrappers, or introduce parallel "current status" documents.

### 3.3 Documentation Workflow

Whenever work alters system behavior, mechanisms, phase status, or architecture:
1. **Identify the canonical owner:** Project status belongs in `00_PROJECT_OVERVIEW.md`; technical mechanisms and ADRs belong in `ARCHITECTURE.md`.
2. **Update the canonical source:** Edit the living document directly rather than creating a secondary file.
3. **Phase-specific records:** Create a new document in `docs/specs/` only when the artifact represents a genuine research specification, evaluation report, or phase closure report.
4. **Synchronize navigation:** Update `DOCUMENTATION_INDEX.md` whenever adding, moving, or removing documentation.
5. **Update README sparingly:** Modify `README.md` only when the public-facing description, quickstart, or primary navigation links change.
6. **Audit references:** Always search for and resolve stale or broken references to old file names.

---

## 4. Codebase Architecture & Ownership Map

```
Lucia/
├── src/                                        # PYTHON CORE BACKEND
│   ├── api/
│   │   └── server.py                           # FastAPI server (127.0.0.1:8765)
│   └── core/
│       ├── sensors/                            # Layer 1: Lexical valence & density encoding
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
- Read `AGENTS.md` and check relevant canonical documentation (`00_PROJECT_OVERVIEW.md`, `ARCHITECTURE.md`).
- Read the governing ADRs and phase specifications.
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
Research Hypothesis (H1–Hn)
       │
       ▼
Isolated Evaluation Harness (tests/evaluation_phaseXX/)
       │
       ▼
Deterministic Empirical Verification (100% Pre-registered criteria satisfied)
       │
       ▼
Architecture Gate & Production Realization Design (docs/specs/...)
       │
       ▼
Formal Architectural Approval (ADR in docs/ARCHITECTURE.md)
       │
       ▼
Production Implementation (src/core/**)
       │
       ▼
Full Regression & Invariant Test Suite (tests/unit/, tests/property/)
       │
       ▼
Promotion, Acceptance & Phase Closure Sign-Off
```

### Research Isolation Rules
- **No Direct-to-Production:** Do NOT skip from a research concept directly into production code.
- **Keep Research Code Isolated:** Prefer dedicated evaluation directories (`tests/evaluation_*`), disposable simulation fixtures, and isolated test models.
- **Experimental Success $\ne$ Production Promotion:** A successful experiment in an evaluation harness demonstrates empirical feasibility; it does NOT authorize changing `src/core/` without an explicit Architecture Gate.
- **Preserve Falsifiability:** Negative results, failed candidate models, and ablations must be documented as evidence rather than erased.

---

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

Validation proceeds from narrow to broad. Agents must execute the relevant test suites before declaring work complete.

### Narrow-to-Broad Testing Order:
1. **Targeted Subsystem Tests:** Run unit tests for the specific module modified.
2. **Phase Production Tests:** Run phase-specific production suites (`tests/unit/test_phaseXX_production.py`).
3. **Regression Suites:** Run previous phase regression tests (e.g. `test_phase20_production.py`).
4. **Property Invariant Tests:** Run Hypothesis invariant tests (`tests/property/`).
5. **Full Unit Regression:** Run `pytest tests/unit -v`.

### Common Test Commands:
```powershell
# Production unit tests
.venv\Scripts\pytest tests/unit -v

# Mathematical property invariants (Hypothesis)
.venv\Scripts\pytest tests/property -v

# Phase 21 production realization tests
.venv\Scripts\pytest tests/unit/test_phase21_production.py -v

# Isolated research evaluation suites
.venv\Scripts\pytest tests/evaluation_phase21 -v

# Electron desktop tests
cd electron ; npm test
```

* **Never report tests as passed unless actually executed.**
* Distinguish software verification (unit/property test passes) from empirical research validation (hypothesis verification in evaluation harnesses).

---

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

Git history is part of Lucia's engineering evidence. Keep it clean, traceable, and reversible.

### 13.1 Before Editing
- Run `git status` to verify the working tree and current branch.
- Inspect recent commits with `git log -n 3 --oneline`.
- Identify any pre-existing uncommitted modifications and preserve them.

### 13.2 Before Committing
Always run:
```powershell
git status
git diff --check
git diff --stat
git diff
```
Verify that:
- Only intended files are staged.
- Zero whitespace errors are reported by `git diff --check`.
- `data/profile.json` remains `{"is_onboarded": false}`.
- No temporary files, caches, or credentials are included.
- Pre-existing unrelated modifications are preserved and unstaged.

### 13.3 Commit Rules
- Use clear, conventional commit messages:
  - `feat(core): ...` — production feature implementation
  - `fix(core): ...` — bug fixes
  - `research(...): ...` — research specs, evaluations, or test harnesses
  - `docs: ...` — canonical documentation updates
  - `test(...): ...` — unit or property tests
- Never amend, squash, or rewrite shared commits unless explicitly requested.
- Never force-push.

---

## 14. Documentation + Code Consistency Check

Before finishing a task, verify that:
- Code matches the approved architecture in `docs/ARCHITECTURE.md`.
- Milestone tables and subsystem health in `docs/00_PROJECT_OVERVIEW.md` match current reality.
- Navigation links in `README.md` and `docs/DOCUMENTATION_INDEX.md` are valid.
- No references point to deleted files (`CURRENT_STATUS.md`, `MECHANISM.md`, `DESIGN_DECISIONS.md`).
- Historical phase specifications in `.kiro/specs/` and `docs/specs/` are preserved.

---

## 15. Reporting Contract

Every task must conclude with a structured, factual report:

### Scope
State precisely which files were modified, created, or deleted.

### Architecture / Design
Cite the governing design document or ADR followed during the task.

### Validation
Report the exact commands executed, test counts, execution durations, and results. Mention any observed performance metrics (e.g. lock holding times, memory usage).

### Documentation
List canonical documents updated and verify reference integrity.

### Git Status
Report the commit hash, commit message, and working tree state.

### Issues / Deviations
Report any known limitations, unresolved trade-offs, or preserved unrelated changes. Never hide test failures or make unverified claims.

---

## 16. Final Pre-Commit Checklist

Before declaring work complete, verify every item:

- [ ] I read the relevant canonical documentation before making decisions.
- [ ] I followed the established architecture and governing ADRs.
- [ ] I did not bypass an Architecture Gate for new cognitive mechanisms.
- [ ] Research code remains isolated from production runtime.
- [ ] Genesis Gate invariant is verified (`data/profile.json == {"is_onboarded": false}`).
- [ ] Lock hierarchy is preserved (`_turn_lock → _step_lock → _train_lock → _stimulus_lock → _state_lock`).
- [ ] CPU vs. GPU discipline is preserved (0 MB GPU VRAM for limbic/memory/consolidation).
- [ ] Pre-reflective emotional discipline is preserved (no self-reported feelings in prompts/outputs).
- [ ] No unrelated production or test files were modified.
- [ ] Pre-existing unrelated working-tree modifications were preserved.
- [ ] All relevant tests were actually executed and passed.
- [ ] `git diff --check` reported 0 whitespace errors.
- [ ] Canonical documentation reflects the implemented reality.
- [ ] Commit message accurately describes the task.
