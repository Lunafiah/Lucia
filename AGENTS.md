# AGENTS.md — Instructions & Invariants for AI Coding Agents

> **Mandatory Guidelines, Architectural Invariants, and Operating Procedures for AI Agents Working on Lucia**

---

## 0. Current Operating Mode — Research-First Governance (Post-Phase 21)

> **CURRENT STAGE: RESEARCH / EVIDENCE BUILDING — NOT ACTIVATION**

Lucia has completed the currently documented production and research milestones through **Phase 21 — Long-Term Relational Consolidation & Synaptic Homeostasis**. The repository currently treats the canonical cognitive architecture as an implemented and validated baseline, while the next research milestone is established through project governance and canonical documentation rather than inferred by an AI coding agent.

### Mandatory Research-First Rules

1. **Research is not production.** A research hypothesis, mathematical proposal, benchmark result, ablation, prototype, or evaluation harness MUST NOT be treated as a production capability merely because tests pass.
2. **Evidence before promotion.** New mechanisms must first be isolated, measurable, reproducible, and evaluated against explicit acceptance criteria before any production integration is proposed.
3. **Do not invent the next phase.** Agents MUST NOT create or assume a new numbered phase, roadmap milestone, subsystem, or activation prerequisite unless it is explicitly established by the authoritative project documentation or a user-approved research specification.
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

`Canonical docs → current status → research specification/evidence → architectural decision → implementation scope → tests → documentation`

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
   * It is integrated continuously in the background every 200 ms via an Ordinary Differential Equation (ODE) within a Liquid Neural Network (LNN).
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

---

## 3. Documentation Authority & Navigation Rules

Agents must respect the document hierarchy established in [`docs/DOCUMENTATION_INDEX.md`](file:///c:/Users/Lunafiah/Desktop/My_project/Lucia/docs/DOCUMENTATION_INDEX.md):

* **Source of Active Truth**:
  * [`docs/00_PROJECT_OVERVIEW.md`](file:///c:/Users/Lunafiah/Desktop/My_project/Lucia/docs/00_PROJECT_OVERVIEW.md) — System architecture and milestone roadmap.
  * [`docs/ARCHITECTURE.md`](file:///c:/Users/Lunafiah/Desktop/My_project/Lucia/docs/ARCHITECTURE.md) — Concurrency, threading, hardware tiers, and IPC protocols.
  * [`docs/MECHANISM.md`](file:///c:/Users/Lunafiah/Desktop/My_project/Lucia/docs/MECHANISM.md) — Mathematical formulas (ODE, SDM, LSI, Ecphory, VAD, Lip-sync).
  * [`docs/CURRENT_STATUS.md`](file:///c:/Users/Lunafiah/Desktop/My_project/Lucia/docs/CURRENT_STATUS.md) — Live implementation state, subsystem health, active API endpoints.
  * [`docs/DESIGN_DECISIONS.md`](file:///c:/Users/Lunafiah/Desktop/My_project/Lucia/docs/DESIGN_DECISIONS.md) — Architectural Decision Records and reconciled discrepancies.
  * [`.kiro/specs/lucia-UI_refractoring-phase7/PHASE_7_UI_REFACTORING_SPEC.md`](file:///c:/Users/Lunafiah/Desktop/My_project/Lucia/.kiro/specs/lucia-UI_refractoring-phase7/PHASE_7_UI_REFACTORING_SPEC.md) — Active UI Design System and token definitions.
* **Historical Phase Specifications**:
  * Directories under [`.kiro/specs/`](file:///c:/Users/Lunafiah/Desktop/My_project/Lucia/.kiro/specs/) are **immutable historical artifacts**. They document the phase-by-phase requirements, designs, and tasks from earlier milestones.
  * **DO NOT** modify, delete, or merge these files into `docs/`.
  * If a historical specification contradicts an authoritative document (e.g. Phase 5 desktop agency vs Phase 5 voice/avatar presence), the authoritative document and `docs/DESIGN_DECISIONS.md` govern.

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
│   └── chat_history.json                       # Conversation turns & session records
└── models/                                     # LOCAL ASSETS & WEIGHTS
    ├── avatar/                                 # 2D Sprites, Live2D models, 3D VRM files
    └── voice/rvc/                              # RVC voice models (.pth + .index)
```

---

## 5. Concurrency & Thread Safety Rules

1. **Lock Hierarchy**:
   * Follow the canonical lock sequence: `_turn_lock → _step_lock → _train_lock → _stimulus_lock → _state_lock`.
   * Always acquire `_train_lock` before `_state_lock`. **Never** acquire `_state_lock` and then attempt to acquire `_train_lock` (deadlock risk).
   * Keep critical sections under `_state_lock` under $1\text{ms}$.
   * Keep weight copy swaps under `_train_lock` under $2\text{ms}$ (measured $\le 0.1\text{ms}$).
   * **Never** perform ODE integration, backward passes, disk/network I/O, or LLM generation while holding locks.
2. **Asynchronous Non-Blocking Endpoints**:
   * `GET /state` and `GET /telemetry/stability` must respond within $10-15\text{ms}$. They must read memory snapshots under the microsecond lock and return immediately without awaiting model inference.
3. **CPU vs. GPU Discipline**:
   * The GPU is reserved exclusively for the active LLM GGUF model and avatar WebGL rendering.
   * All continuous background loops (`EmotionCore-FastLoop`, `DecayEngine-SlowLoop`, `ConsolidationEngine` offline BPTT) must run on the CPU with zero GPU VRAM contention.

---

## 6. Testing & Quality Assurance Protocols

Before submitting changes, agents must run the smallest relevant verification set and clearly distinguish **implementation correctness** from **research evidence**. Do not run unrelated expensive suites merely to manufacture a green status.

### Canonical Python Backend
```powershell
.venv\Scripts\pytest tests/unit -v
.venv\Scripts\pytest tests/property -v
.venv\Scripts\pytest tests/integration -v
```

### Research / Evaluation Harnesses
Run the evaluation suite specific to the research increment, for example:
```powershell
.venv\Scripts\pytest tests/evaluation_phase21 -v
.venv\Scripts\pytest tests/unit/test_phase21_production.py -v
```
Research results MUST be reported separately from production regression results.

### Electron Desktop
```powershell
cd electron
npm test
```

### Verification Checklist for Agents
- [ ] Research work is isolated unless production integration was explicitly authorized.
- [ ] Hypothesis, baseline/control, metrics, acceptance criteria, and falsification conditions are identifiable.
- [ ] Research evidence is not described as production capability unless the canonical docs explicitly promote it.
- [ ] No introspective or meta-self-awareness patterns introduced into prompts or outputs.
- [ ] No character switchers or multiple persona presets created.
- [ ] Historical phase specifications in `.kiro/specs/` remain untouched.
- [ ] First Activation remains blocked unless explicitly authorized by canonical governance.
- [ ] Canonical production data remains isolated from tests/simulation.
- [ ] All new documentation follows the authority matrix in `docs/DOCUMENTATION_INDEX.md`.
- [ ] Any architectural trade-off, promotion, rejection, or pivot is recorded in `docs/DESIGN_DECISIONS.md`.
- [ ] Test results identify exactly which suite was run and whether it proves correctness, stability, or research evidence.

## 7. Standard Agent Work Procedure — Mandatory Workflow

> **Every coding/research agent must follow this workflow by default.** A task prompt may narrow the scope, but should not need to repeat these baseline procedures.

### 7.1 Before Doing Any Work

1. **Read `AGENTS.md` first.** Treat it as the mandatory operating contract for the repository.
2. Read the relevant canonical documents before making architectural or implementation decisions:
   - `docs/00_PROJECT_OVERVIEW.md`
   - `docs/CURRENT_STATUS.md`
   - `docs/ARCHITECTURE.md`
   - `docs/MECHANISM.md`
   - `docs/DESIGN_DECISIONS.md`
   - `docs/DOCUMENTATION_INDEX.md` when documentation structure is involved.
3. Inspect the repository state before editing:
   - current branch
   - working tree status
   - recent commits
   - relevant existing implementation/tests
4. Identify the **current phase/stage, task boundary, invariants, affected components, and expected deliverables**.
5. If the task is research, identify the hypothesis, baseline/control, variables, metrics, falsification criteria, and evidence required **before implementing the experiment**.
6. Do not begin implementation merely because a requested idea sounds reasonable. Resolve its architectural status first: existing rule, approved decision, active research, or future proposal.

### 7.2 Plan Before Implementation

For non-trivial work, produce a short execution plan internally or in the agent report before modifying files. The plan should identify:

- files/components expected to change;
- files/components explicitly protected from change;
- implementation or experiment strategy;
- tests/evaluations to run;
- documentation that must be created or synchronized;
- git actions required at completion.

If the repository or canonical documents contradict the task request, **stop and resolve the contradiction rather than silently choosing one interpretation**.

### 7.3 Research Procedure

For research/evaluation tasks, use this sequence:

`Question → Hypothesis → Mechanism → Baseline/Control → Experimental Design → Implementation → Evaluation → Analysis → Decision → Documentation`

Mandatory rules:

- Separate **research code** from production code whenever possible.
- Prefer isolated evaluation harnesses, fixtures, simulation data, and disposable experiment modules.
- Use controlled comparisons and ablations when causal attribution matters.
- Record negative results, failed hypotheses, rejected mechanisms, and unexpected findings; do not delete them because they make the roadmap less elegant.
- Never infer psychological properties, consciousness, subjective feeling, or human-equivalent cognition from an engineering metric alone.
- A green test suite proves the tested software behavior; it does **not** by itself prove the scientific hypothesis.
- A research result may conclude **promote / revise / reject / insufficient evidence**. Only an explicit architectural decision can promote research into production.
- Do not optimize the experiment to obtain a preferred result. Preserve reproducibility and falsifiability.

### 7.4 Implementation Procedure

1. Inspect existing code before creating new abstractions.
2. Prefer the smallest change that satisfies the approved requirement.
3. Reuse existing interfaces, services, fixtures, and utilities when they already represent the correct architectural boundary.
4. Do not duplicate an existing responsibility merely because a new name or module appears convenient.
5. Keep production behavior unchanged during research unless production integration is explicitly authorized.
6. Do not mix unrelated refactors, formatting churn, dependency upgrades, or speculative cleanup into a focused task.
7. After implementation, inspect the final diff and verify that every changed file is intentional.

---

## 8. Documentation Creation & Persistence Rules

### 8.1 Documentation Is Part of the Work

If a task produces a new research result, architectural decision, implementation milestone, experiment, rejection, or material behavioral change, the corresponding documentation is part of the deliverable—not optional cleanup.

### 8.2 Where Documents Belong

- **Active/canonical project truth:** `docs/`
- **Historical phase specifications:** `.kiro/specs/` and immutable unless explicitly designated otherwise by project governance.
- **Research/evaluation artifacts:** use the established research/evaluation location defined by the current project structure; prefer a dedicated research document or `tests/evaluation_*` rather than burying scientific evidence in source-code comments.
- **Temporary notes / scratch output:** keep outside canonical documentation and do not present them as project truth.

Before creating a new document:

1. Search for an existing document that already owns the topic.
2. Prefer updating the existing canonical document over creating a duplicate.
3. If a new document is genuinely required, establish its role, authority level, and relationship to existing docs.
4. Do not create parallel "final", "final-v2", "latest", or duplicate truth documents.

### 8.3 Documentation Status & Evidence

Every research or milestone document should make clear, where applicable:

- status/classification (`[CURRENT RESEARCH]`, `[RESEARCH VALIDATED]`, `[ARCHITECTURE APPROVED]`, `[VALIDATED / PRODUCTION IMPLEMENTED]`, `[FUTURE GATE]`, etc.);
- date or commit when useful for traceability;
- hypothesis/question;
- method and baseline;
- results/evidence;
- limitations and unresolved questions;
- resulting architectural decision, if any.

Never upgrade a document's status simply because implementation exists or tests pass.

### 8.4 Documentation Synchronization

When implementation changes project truth, update the appropriate canonical documentation in the same task when authorized. At minimum, check whether these need synchronization:

- `docs/CURRENT_STATUS.md`
- `docs/00_PROJECT_OVERVIEW.md`
- `docs/DESIGN_DECISIONS.md`
- `docs/ARCHITECTURE.md`
- `docs/MECHANISM.md`
- `docs/DOCUMENTATION_INDEX.md`

Do not rewrite historical documents merely to make them agree with the latest state. Preserve history and reconcile it through canonical active documentation and ADRs.

---

## 9. Git & Version-Control Procedure

> **Git history is part of Lucia's engineering evidence. Keep it clean, traceable, and reversible.**

### 9.1 Before Editing

- Check `git status`.
- Check the current branch.
- Inspect recent commits relevant to the task.
- Do not discard or overwrite pre-existing user changes.
- If unrelated uncommitted changes exist, preserve them and avoid mixing them into the task.

### 9.2 During Work

- Keep changes logically scoped to the task.
- Do not use destructive commands (`reset --hard`, broad checkout/revert, force operations, history rewriting) unless explicitly authorized.
- Do not amend, squash, rebase, or rewrite existing commits unless explicitly requested/authorized.
- Do not commit generated caches, secrets, credentials, local model weights, environment files, or unrelated artifacts.
- Do not change `.gitignore` merely to hide files that should not be in the repository; determine whether the artifact belongs in version control first.

### 9.3 Before Commit

Run:

```powershell
git status
git diff --check
git diff --stat
git diff
```

Then verify:

- every changed file is intentional;
- no secrets or credentials are present;
- no unrelated changes are included;
- tests/evaluations correspond to the actual change;
- documentation reflects the resulting state when required.

### 9.4 Commit Rules

When the task is complete and the repository is in a coherent verified state:

- Make a focused commit for the completed task unless the user explicitly requests otherwise.
- Use a clear imperative commit message describing the actual change.
- Do not claim a commit exists until Git confirms it.
- After committing, verify with `git status` and `git log -1 --oneline`.
- If a remote push is explicitly part of the task, verify the push result; otherwise do not push merely for convenience.
- Never force-push by default.

### 9.5 Reporting Git State

The completion report should state, when applicable:

- files changed;
- tests/evaluations run and their exact result;
- documentation synchronized;
- commit hash/message;
- whether changes were committed or remain uncommitted;
- whether anything was intentionally left untouched or unresolved.

Never report "complete" if required tests, documentation, or Git verification remain unknown.

---

## 10. Completion & Agent Handoff Protocol

Before declaring a task complete, perform this final sequence:

`Diff Review → Tests/Evaluation → Documentation Sync → Git Verification → Final Report`

The final report should be concise and evidence-based. It should distinguish:

- **Implemented** — what changed in code/config;
- **Research result** — what the experiment actually established;
- **Not established** — what remains unknown or unproven;
- **Verified** — exact tests/evaluations run;
- **Git** — commit state/hash;
- **Next action** — only if explicitly determined by canonical governance.

Do not invent a next phase or recommend additional implementation merely to make the report feel complete.

