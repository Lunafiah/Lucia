# AGENTS.md — Instructions & Invariants for AI Coding Agents

> **Mandatory Guidelines, Architectural Invariants, and Operating Procedures for AI Agents Working on Lucia**

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
│       ├── emotion/                            # Layer 2: Continuous Fast-Loop LNN ODE solver
│       ├── homeostasis/                        # Layer 3: Metabolic budgeting & generation constraints
│       ├── inference/                          # Layer 4: Active Inference & CPU LNNTrainer
│       ├── memory/                             # Layer 5: Kanerva SDM, DecayEngine, Ecphory
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
   * Always acquire `_train_lock` before `_state_lock`. **Never** acquire `_state_lock` and then attempt to acquire `_train_lock` (deadlock risk).
   * Keep critical sections under `_state_lock` under $1\text{ms}$.
   * Keep weight copy swaps under `_train_lock` under $2\text{ms}$.
2. **Asynchronous Non-Blocking Endpoints**:
   * `GET /state` and `GET /telemetry/stability` must respond within $10-15\text{ms}$. They must read memory snapshots under the microsecond lock and return immediately without awaiting model inference.
3. **CPU vs. GPU Discipline**:
   * The GPU is reserved exclusively for the active LLM GGUF model and avatar WebGL rendering.
   * All continuous background loops (`EmotionCore-FastLoop`, `DecayEngine-SlowLoop`, `LNN-Trainer`) must run on the CPU with zero GPU VRAM contention.

---

## 6. Testing & Quality Assurance Protocols

Before submitting code changes or completing tasks, agents must execute the appropriate test suites:

### Python Backend Tests
```powershell
# Run all unit tests
.venv\Scripts\pytest tests/unit -v

# Run property-based Hypothesis tests (P1 - P30 invariants)
.venv\Scripts\pytest tests/property -v

# Run end-to-end integration tests
.venv\Scripts\pytest tests/integration -v
```

### Electron Desktop Tests
```powershell
cd electron
npm test
```

### Verification Checklist for Agents:
- [ ] No introspective or meta-self-awareness patterns introduced into prompts or outputs.
- [ ] No character switchers or multiple persona presets created.
- [ ] Historical phase specifications in `.kiro/specs/` remain untouched.
- [ ] All new documentation follows the authority matrix in `docs/DOCUMENTATION_INDEX.md`.
- [ ] Any architectural trade-off or pivot is recorded in `docs/DESIGN_DECISIONS.md`.
- [ ] All tests pass without regression.
