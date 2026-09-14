# Lucia — Current System Status & Implementation State

> **Live Implementation Snapshot, Subsystem Health Matrix, and Active Development State**  
> *Last Updated: September 2026*

---

## 1. Executive Status Overview

Lucia has successfully completed **Phase 8 (Runtime Isolation & Simulation Environment)**, **Phase 9 (Cognitive Unification & Convergence)**, **Phase 9.5 (Real LLM Backend Recovery)**, **Phase 9.6 (Corrective Temporal Synchronization)**, **Post-Phase-9.6 Architectural Validation**, **Temporal Affect Dynamics Deepening (Temporal Ablation v2)**, **Architectural Boundary Audit & Self-Model Readiness**, **Phase 10 (Define Affective Dynamics)**, **Phase 11 (Affective Memory Coupling Research)**, **Phase 11.5 (Independent Evidence Audit)**, **Phase 12 (Knowledge Learning Research)**, **Phase 13 (Relationship Development Research)**, **Phase 14 (Embodiment & Affective Expression Research)**, **Phase 15 (Affective Communication Research)**, **Phase 16 (Affective Life Integration & Production Architecture Realization)**, **Phase 17 (Integrated Affective Life Evaluation & Longitudinal Validation)**, **Phase 18 (Human Longitudinal Interaction & Real-World Validation)**, **Phase 19 (Multi-Timescale Affective Life & Temporal Continuity)**, and **Phase 20 (Affective Recollection & Memory Reactivation)**. All foundational limbic, cognitive, memory, presence, simulation, temporal synchronization, integrated affective life, multi-timescale affective dynamics, and closed-loop affective recollection subsystems are fully operational and validated by 10/10 Phase 20 research experiments, 9/9 production unit tests, and comprehensive automated regression suites.

The repository realizes a unified 16-stage cognitive pipeline orchestrating grounded knowledge, two-phase relationship development, bounded memory contextualization, closed-loop affective recollection, affective communication strategy, canonical 15-dim multimodal expression, Japanese canonical voice realization, and strict test storage isolation.

```
┌────────────────────────────────────────────────────────────────────────┐
│                   CANONICAL COGNITIVE DEVELOPMENT ROADMAP              │
│                                                                        │
│   COMPLETED & PRODUCTION VALIDATED                                     │
│   ├── Phase 10: Affective Dynamics                 [✅ VALIDATED]       │
│   ├── Phase 11: Affective Memory (Baseline A)      [🔬 VALIDATED RES.] │
│   ├── Phase 12: Knowledge Learning (K0–K9)         [🔬 VALIDATED RES.] │
│   ├── Phase 13: Relationship Development           [🔬 VALIDATED RES.] │
│   ├── Phase 14: Embodiment & Affective Expression  [🔬 VALIDATED RES.] │
│   ├── Phase 15: Affective Communication            [🔬 VALIDATED RES.] │
│   ├── Phase 16: Affective Life Integration         [✅ VALIDATED]       │
│   ├── Phase 17: Affective Life Evaluation          [✅ VALIDATED]       │
│   ├── Phase 18: Human Longitudinal Validation      [✅ VALIDATED]       │
│   ├── Phase 19: Multi-Timescale Affective Life     [✅ VALIDATED]       │
│   ├── Phase 20: Affective Recollection             [✅ VALIDATED]       │
│                                                                        │
│   NEXT RESEARCH MILESTONE                                              │
│   └── Phase 21: Relational Consolidation & Synaptic Homeostasis        │
│                                                    [🔬 PLANNED RES.]   │
│                                                                        │
│   FUTURE CONCEPTUAL RESEARCH HORIZONS                                  │
│   ├── Phase 22: Active Inference & Information Seeking                 │
│   ├── Phase 23: Affective Communication Adaptation                     │
│   ├── Phase 24: Temporal Embodiment & Social Feedback                  │
│   ├── Phase 25: Emergent Individuality & Preferences                   │
│   ├── Phase 26: Personalized Individual Trajectory                     │
│   └── First Activation (Genesis Onboarding)        [🔒 FUTURE GATE]     │
└────────────────────────────────────────────────────────────────────────┘
```

> **Roadmap Evidence Hierarchy:**  
> - `[VALIDATED / PRODUCTION IMPLEMENTED]`: Formally specified, fully implemented in `src/core/`, and verified with automated unit, property, and integration test suites.  
> - `[RESEARCH VALIDATED]`: Formally specified and empirically verified in isolated research harnesses (`tests/evaluation_*/`); promoted or awaiting integration.  
> - `[ARCHITECTURE APPROVED]`: Architecture design formally reviewed and approved by architectural governance prior to production implementation.  
> - `[FUTURE GATE]`: Strict existential boundary preventing activation until all prior stages are empirically proven.

---

## 2. Subsystem Health & Implementation Matrix

| Subsystem / Layer | Module Path | Status | Operational Capabilities & Integration Reality |
|---|---|---|---|
| **Stimulus Processor** | `src/core/gating/` | **STABLE** | Lexical valence scoring ($[-1, 1]$), punctuation cadence, semantic density. Emits 16-dim continuous vector. *(Historical doc: `src/core/sensors/`)* |
| **Limbic Fast Loop** | `src/core/emotion/` | **STABLE** | Continuous 200ms background thread (live) or discrete virtual tick step (sim). Liquid Neural Network ODE integration. Enforces deterministic barrier `commit_stimulus(token)` with FIFO queue draining under `_step_lock` before post-turn PAD evaluation. Continuous multi-turn accumulation empirically proven. |
| **Multi-Timescale Dynamics (Phase 19)** | `src/core/emotion/` / `tests/evaluation_phase19/` | **STABLE (Production Validated)** | Coupled Multi-Timescale LNN ($\mathbf{h}_{\text{fast}} \in \mathbb{R}^{32}, \mathbf{s}_{\text{slow}} \in \mathbb{R}^{16}$) with Philia dynamic attractor grounding ($\mathbf{p}^* = [+0.25, -0.05, +0.05]$). Biexponential relaxation ($\tau_f = 1.44\text{s}, \tau_s = 93.28\text{s}, \Delta\text{AIC}=6504.96$), autonomous stress-to-fatigue state transformation, historical hysteresis ($\Delta_{\max}=0.1749$), strictly dissipative Lyapunov contraction ($\text{Tr}(J) \approx -46.46 < 0$ in tested domain), and microsecond CPU execution ($1.33\text{ms}$). Stage 5 homeostatic context modulation verified. Verified by 15/15 Phase 19 research evaluation tests (`tests/evaluation_phase19/`), 35/35 property invariants, and full unit regression suite. |
| **Affective Recollection (Phase 20)** | `src/core/emotion/` / `src/core/memory/` / `tests/unit/test_phase20_production.py` | **STABLE (Production Validated)** | Closed-Loop Affective Recollection via Slow-Field Latent Forcing ($\mathbf{r}_{\text{slow}}^{\text{bounded}}$). Multi-modal salience scoring ($S_i = 0.60 S_{\text{sem}} + 0.25 S_{\text{aff}} + 0.15 w_{\text{decay}}$), competitive softmax gating ($\theta_{\text{gate}}=0.50, \tau_{\text{comp}}=0.20$), simulation-time bounded rectangular forcing pulse ($\mathbf{W}_{\text{rec}}=0.35\mathbf{I}_{16}$), 3-case legacy fallback approximation, Stage 12 conversational pacing modulation ($\Delta\tau_{\text{pace}}$), and Stage 16.1 live physiological state co-encoding. Fully verified by 9/9 production unit tests, 10/10 research evaluation tests, 35/35 property tests, and 592/592 full unit test suite. |
| **Homeostatic Engine** | `src/core/emotion/` | **STABLE** | Tracks cognitive load, metabolic stamina (energy), tension, and stability. Modulates behavioral constraints: multi-turn input accumulation throttles token budget from 350 to 150. *(Historical doc: `src/core/homeostasis/`)* |
| **Active Inference** | `src/core/inference/` | **STABLE (Causal)** | $3 \times 3$ linear generative transition model predicting PAD state. Computes Free Energy surprise $\mathcal{S} = \|A \cdot p_{before} + b - p_{after}\|_2$ evaluated on deterministically committed post-stimulus PAD. Causal: modulates cognitive load/tension and triggers $k=2$ when $\mathcal{S} > 0.60$. Online belief adaptation verified. |
| **LNN Plasticity** | `src/core/inference/` | **STABLE** | Two-stage plasticity: online turn salience tagging + idle consolidation ($T_{\text{idle}} \ge 45\text{s}$) on CPU thread. Swaps weights into `EmotionCore` under 2ms `_train_lock`. |
| **Sparse Distributed Memory** | `src/core/memory/sdm.py` | **STABLE** | 1,000 hard locations across 1,000-bit Hamming address space with 64-dim content vectors. Distributed read/write within activation radius. |
| **Affective Tagging & Decay** | `src/core/memory/decay.py` | **STABLE** | 60-second slow-loop daemon (live) or virtual clock decay tick (sim). Salience-resistant decay ($\lambda_{eff}$) gives intense emotional memories up to $4\times$ longer lifetime. |
| **Synergistic Ecphory** | `src/core/memory/ecphory.py` | **STABLE** | Cosine similarity resonance between current PAD state and stored tags. Synthesizes subconscious Echo Vector to softly color prompt context. |
| **Conceptual Knowledge** | `src/core/knowledge/` | **STABLE (Promoted P16)** | Typed `Proposition` & `Concept` graph with provenance tracking (`DIRECT_EXPERIENCE`, `USER_STATED`, `INFERRED`, `CORE_AXIOM`). Bounded forward inference engine ($d_{max} \le 3$), contradiction resolution, thread-safe `KnowledgeStore`, atomic persistence. |
| **Interpersonal Relationship** | `src/core/relationship/` | **STABLE (Promoted P16)** | Slowly evolving 4D state $\mathbf{R} = (\text{trust}, \text{familiarity}, \text{attunement}, \text{shared\_experience})$. Strictly decoupled two-phase lifecycle: Stage 9 read snapshot vs Stage 16 post-response categorical signal update with inertia ($\alpha=0.03$) and temporal decay ($0.005$). |
| **Affective Communication** | `src/core/communication/` | **STABLE (Promoted P16)** | 10D `CommunicationState`, 5 discrete modes (`DEEP_RECIPROCAL`, `ATTUNED_LIGHT`, `SUPPORTIVE_GROUNDING`, `CONCISE_PROTECTIVE`, `PLAYFUL_EXPLORATORY`), bounded memory contextualization ($m_{ctx} \le 0.50$, zero limbic feedback), somatic pacing latency ($0 \le \tau \le 1000\text{ms}$), and `SemanticConsistencyGuard`. |
| **Multimodal Expression** | `src/core/expression/` | **STABLE (Promoted P16)** | Canonical 15-dim `ExpressionState` (3 text, 4 prosody, 5 facial blendshapes, 2 posture, 1 latency). Pure feedforward actuator decoupling (zero feedback into ODE $\mathbf{h} \in \mathbb{R}^{32}$), temporal smoothing ($\gamma=0.25$), and `SemanticConsistencyGuard`. |
| **Cognitive Orchestrator** | `src/core/orchestrator/` | **STABLE (16 Stages)** | Canonical 16-stage cognitive processing pipeline (S1–S16) integrating sensory gating, limbic ODE, homeostasis, active inference, somatic markers, ecphory, memory contextualization, knowledge retrieval, relationship read, communication policy, CUDA LLM inference, semantic guard, expression policy, episodic storage, plasticity salience, and post-turn relationship update. |
| **Language Generation** | `src/core/language/` | **STABLE (CUDA Verified)** | Local GGUF Small Language Model (LFM2.5-1.2B Instruct) running via `llama-cpp-python` with CUDA acceleration on NVIDIA RTX 3050 Ti Laptop GPU (17/17 layers offloaded, 152 tok/s, 845 MiB VRAM). Pre-reflective prompt conditioning. |
| **Boundary Safety Layer** | `src/core/safety/boundary_layer.py` | **STABLE** | Regex and pattern validator blocking introspective meta-selfhood statements (*"I feel"*, *"I exist as"*, *"As an AI"*). Multi-layered anti-roleplay defense (lexical boundary checks + structured anti-roleplay tests + architectural prohibition of self-model APIs). |
| **RVC Voice Synthesis** | `src/core/voice/` | **STABLE (Regenerated & Accepted)** | Direct on-device RVC v2 neural inference (`RVCPipeline` + `SynthesizerTrn`, 457 tensors) with canonical `ja-JP-NanamiNeural` base voice and `VaresaGIJP` target timbre (`.pth` + `.index`). Controlled signal path diagnosis audited harmonic generator, Parselmouth F0 unvoiced interpolation, pre-interpolation FAISS k=8 retrieval, and headroom normalization; verified clean, intelligible Japanese speech (100% Whisper ASR match, 0 clipping, HF energy 5.64%, index_rate=0.25). All Phase 18 longitudinal audiovisual artifacts across Scenarios A–G successfully regenerated, verified, and accepted under `PASS WITH LIMITATIONS`. Documented in `PHASE_18_LONGITUDINAL_AUDIOVISUAL_REGENERATION_REPORT.md`. Zero cloud dependencies. |
| **Offline STT & VAD** | `src/core/voice/stt_engine.py` | **STABLE** | Continuous local microphone capture via Web Audio VAD with transcription via `faster-whisper` (CTranslate2). Fully offline; no cloud keys required. |
| **Polymorphic Avatar Stage** | `electron/renderer/avatar/` | **STABLE** | Dynamic Quad-Engine: 2D Procedural Canvas, 2D Expression Sprites, Live2D Cubism 4 WebGL, and 3D Humanoid VRM (Three.js). Consumes 15D ExpressionState. |
| **Lip-Sync Engine** | `electron/renderer/avatar/lip-sync.js` | **STABLE** | 60 FPS real-time FFT formant analysis (200Hz–2500Hz) computing mouth aperture height and vowel width during vocal playback. |
| **Simulation Runtime** | `src/core/simulation/runtime.py` | **STABLE** | Deterministic simulation state machine (`CREATED` $\rightarrow$ `SIMULATING`). Unconditionally raises `ActivationSafetyError` on `activate()`. Ephemeral stores protect canonical `data/*.json`. |
| **Virtual SimClock** | `src/core/simulation/sim_clock.py` | **STABLE** | Virtual time controller supporting `step()`, `pause()`, `resume()`, `set_speed()`, `reset()`. Dispatches fast/slow callbacks synchronously with `max_fast_ticks=50` guard. |
| **Storage Policy Isolation** | `src/core/simulation/storage_policy.py` | **STABLE** | Intercepts disk write attempts to `data/`. In-memory ephemeral replacements for chat history, relationship, knowledge, and profile. Bit-exact SHA-256 zero contamination verified. |
| **Scenario Runner** | `src/core/simulation/scenario_runner.py` | **STABLE** | Automated test scenarios: Scenario A (Sensory Gating), B (Emotional Recovery & Decay), C (Somatic Depletion), D (Safety Invariants). |
| **Stability Telemetry** | `src/core/telemetry/stability_evaluator.py` | **STABLE** | Computes Fast-Loop tick jitter, ODE velocity variance, Free Energy surprise entropy, and Composite Limbic Stability Index (LSI). Watchdog auto-recovers from numerical stalls. |
| **Desktop Process & IPC** | `electron/main/` | **STABLE** | Native Electron lifecycle management (`ProcessManager`), global hotkey (`Ctrl+Shift+L`), System Tray, context isolation (`ContextBridge`), model-anchored mascot physics, and 15D expression/relationship forwarding. |
| **UI Design & UX System** | `electron/renderer/` | **STABLE** | Personal Digital Room: progressive disclosure navigation, subtle qualitative status, settings, dedicated read-only diagnostics console, Genesis Awakening, solemn End-of-Life boundary, and Simulation Canopy/Drawer. |
| **Existential Lifecycle** | `src/api/server.py` | **STABLE** | Atomic `POST /lifecycle/end`, profile persistence, Genesis un-onboarded state transition (`is_onboarded = False`), and clean birth timestamp generation on awakening. |

---

## 3. Active REST API Surface & Local Endpoints

The Python backend (`src/api/server.py`) binds exclusively to `127.0.0.1:8765` (configurable via `config/ui.json`). Operating mode (`live` vs `simulation`) strictly dictates route availability:

| Method | Route | Mode Guard | Description | Response Time SLA |
|---|---|---|---|---|
| `POST` | `/process` | Live only (403 in sim) | Dispatches user chat turn through 16-stage cognitive pipeline; returns response text, PAD, behavioral constraints, 15D expression, relationship, and communication payloads. | $\le$ Model inference $+ 20\text{ms}$ |
| `GET` | `/state` | Universal | Returns non-blocking real-time state snapshot (PAD, somatic, and current expression, relationship, communication states). | $\le 10\text{ms}$ (non-blocking) |
| `GET` | `/telemetry/stability` | Universal | Returns Limbic Stability Index (LSI), tick jitter, and ODE variance. | $\le 15\text{ms}$ |
| `POST` | `/system/profile` | Universal | Dynamically reconfigures hardware scalability tier (`CPU_ONLY`, `LAPTOP`, `DESKTOP`, `HIGH_END`). | $\le 50\text{ms}$ |
| `POST` | `/voice/transcribe` | Universal | Transcribes audio bytes using local `faster-whisper` model. | Streamed / Chunked |
| `POST` | `/voice/synthesize` | Universal | Synthesizes character speech audio from text via RVC / Edge-TTS. | $\approx 150 - 350\text{ms}$ |
| `GET` | `/voice/models` | Universal | Discovers available RVC voice model folders in `models/voice/rvc/`. | $\le 10\text{ms}$ |
| `GET` | `/profile` | Universal | Returns current profile and awakening status (`is_onboarded`). | $\le 10\text{ms}$ |
| `POST` | `/profile` | Universal | Updates profile, completes Genesis, generates canonical `born_at`. | $\le 20\text{ms}$ |
| `POST` | `/lifecycle/end` | Live only (403 in sim) | Atomic existential lifecycle reset: wipes memory/state to baseline. | $\le 20\text{ms}$ |
| `GET` | `/runtime/descriptor` | Universal | Returns runtime mode (`live`, `simulation`, `preview`) and capabilities. | $\le 5\text{ms}$ |
| `GET` | `/runtime/snapshot` | Universal | Full IPC-ready snapshot (PAD, somatic, storage type, clock state). | $\le 10\text{ms}$ |
| `POST` | `/sim/stimulus/inject-text` | Sim only (403 in live) | Injects text stimulus via sensory `StimulusProcessor` pathway. | $\le 20\text{ms}$ |
| `POST` | `/sim/stimulus/inject-vector`| Sim only (403 in live) | Developer debug probe: injects raw 16D vector directly to Brain. | $\le 10\text{ms}$ |
| `GET` | `/sim/stimulus/presets` | Sim only (403 in live) | Lists standard stimulus presets (joy, calm, tension, affection, etc.).| $\le 5\text{ms}$ |
| `POST` | `/sim/stimulus/preset` | Sim only (403 in live) | Injects standard preset by name and pathway. | $\le 20\text{ms}$ |
| `POST` | `/sim/clock/step` | Sim only (403 in live) | Steps virtual clock by discrete $\Delta t$ ms, dispatching callbacks. | $\le 15\text{ms}$ |
| `POST` | `/sim/clock/pause` / `resume`| Sim only (403 in live)| Pauses or resumes the virtual simulation clock. | $\le 5\text{ms}$ |
| `POST` | `/sim/clock/speed` | Sim only (403 in live) | Sets virtual clock speed multiplier ($0.1\times$ to $10.0\times$). | $\le 5\text{ms}$ |
| `POST` | `/sim/clock/reset` | Sim only (403 in live) | Resets virtual clock time to zero. | $\le 5\text{ms}$ |
| `POST` | `/sim/scenarios/run` | Sim only (403 in live) | Executes named scenario (A, B, C, D) or all scenarios sequentially. | Duration of scenario |
| `GET` | `/sim/scenarios/results` | Sim only (403 in live) | Retrieves latest scenario execution results and assertions. | $\le 5\text{ms}$ |
| `POST` | `/sim/chat` | Sim only (403 in live) | Executes simulated conversational turn into ephemeral RAM store. | $\le$ Model inference $+ 20\text{ms}$ |

---

## 4. Active File Inventory & Component Locations

```
Lucia/
├── config/
│   ├── ui.json                                 # Runtime configuration (Port: 8765, GPU layers: 32)
│   └── window-state.json                       # Saved window bounds and mascot position
├── data/
│   ├── chat_history.json                       # Persistent conversation history (Live runtime only)
│   └── profile.json                            # Companion identity & born_at status (Live runtime only)
├── electron/
│   ├── main/
│   │   ├── index.js                            # Electron application entrypoint
│   │   ├── ipc-bridge.js                       # IPC routing for chat, window, models, and simulation
│   │   ├── mascot-window.js                    # Frameless transparent Always-on-Top mascot manager
│   │   ├── process-manager.js                  # Background Python child process lifecycle coordinator
│   │   └── tray-manager.js                     # Windows notification area system tray integration
│   ├── preload/
│   │   └── preload.js                          # Context isolation exposing window.lucia bridge
│   └── renderer/
│       ├── avatar/                             # Avatar engines (canvas, sprites, live2d, vrm, lip-sync)
│       ├── chat/                               # Conversation feed & interactive input UI
│       ├── debug/                              # Emotion telemetry panel & diagnostics modal
│       ├── journal/                            # Relationship history & affective milestones
│       ├── settings/                           # Categorized settings modal & End-of-Life confirmation
│       ├── simulation/                         # Simulation canopy ribbon & console drawer controller
│       ├── index.html                          # Main desktop window markup (Personal Digital Room)
│       └── index.css                           # Design System tokens & glassmorphic styles
├── models/
│   ├── LFM2.5-1.2B-Instruct-Q4_K_M.gguf        # Active GGUF Small Language Model
│   ├── avatar/                                 # Avatar models (live2d/HoshinoAi, sprites/columbina, vrm/)
│   └── voice/rvc/                              # Installed RVC character voice models
└── src/
    ├── api/server.py                           # FastAPI application entrypoint & mode router
    └── core/
        ├── emotion/emotion_core.py             # Fast-Loop Liquid Neural Network ODE solver
        ├── emotion/homeostatic_engine.py       # Somatic markers & behavioral constraints
        ├── gating/stimulus_processor.py        # Lexical & syntactic stimulus encoder (16D)
        ├── inference/active_inference.py       # Active inference & short-horizon surprise minimization
        ├── inference/lnn_trainer.py            # CPU online backprop-through-ODE plasticity
        ├── inference/orchestrator.py           # InferencePipelineOrchestrator integrating Layer 4
        ├── memory/sdm.py                       # Kanerva Sparse Distributed Memory
        ├── memory/decay.py                     # Emotional decay engine
        ├── memory/ecphory.py                   # Synergistic ecphory resonance engine
        ├── presence/orchestrator.py            # PresenceOrchestrator integrating VoiceEngine
        ├── safety/boundary_layer.py            # Rule-based filter eliminating meta-selfhood patterns
        ├── simulation/runtime.py               # SimulationRuntime state machine & activation guard
        ├── simulation/sim_clock.py             # Virtual simulation clock & tick dispatcher
        ├── simulation/storage_policy.py        # Ephemeral storage policy & disk write interceptor
        ├── simulation/stimulus_service.py      # Sensory text vs debug vector probe injection
        ├── simulation/scenario_runner.py       # Automated validation scenarios A, B, C, D
        ├── telemetry/stability_evaluator.py    # Limbic Stability Index (LSI) computation
        └── voice/voice_engine.py               # Direct RVC & neural voice synthesis
```

---

## 5. Active Phase 9 Preparation & Approved Architecture Gate

Following the comprehensive post-Phase-8 architectural review (`PHASE_8_ARCHITECTURE_REVIEW.md`) and formal **Architecture Decision Gate** (`PHASE_9_ARCHITECTURE_GATE.md`), the architecture for **Phase 9: Cognitive Unification & Convergence** has been verified and approved:

1. **Unified Cognitive Orchestrator (`CognitiveOrchestrator`)**:
   - Deprecate 5-tier inheritance hierarchy (`Orchestrator` $\rightarrow$ `MemoryAugmentedOrchestrator` $\rightarrow$ `InferencePipelineOrchestrator` $\rightarrow$ `PresenceOrchestrator`).
   - Implement `CognitiveOrchestrator` composing Layers 1–6 in a single linear pass with property telemetry (ADR-014).
   - Completely eliminate double-stimulus push and double-homeostatic recording.
2. **Causal Active Inference**:
   - Wire `ActiveInferenceEngine` into every live turn before stimulus integration (ADR-015).
   - Evaluate Prediction Surprise $\mathcal{S}$; modulate Homeostatic Cognitive Load, Tension, and trigger reasoning depth $k=2$ when $\mathcal{S} > 0.60$.
3. **Decoupled Expression Pipeline for Voice**:
   - Voice synthesis remains an asynchronous service triggered via IPC by the Electron Body UI after cognitive turn completion (ADR-016).
   - Guarantees zero latency penalty for text, failure isolation, and zero compute when muted.
4. **Two-Stage LNN Plasticity**:
   - Online salience tagging during turns; offline CPU backprop consolidation during idle periods ($T_{\text{idle}} \ge 45\text{s}$) or salient batch overflow ($\ge 8$) (ADR-017).
5. **Turn-Level Concurrency Protection**:
   - Wrap `POST /process` in an asynchronous turn mutex (`asyncio.Lock()`) in `server.py` and a re-entrant lock in `CognitiveOrchestrator` (ADR-018).
6. **Complete Brain ↔ Body IPC Remediation**:
   - Migrate all 12 remaining direct `fetch()` calls in `chat.js` to secure `window.lucia.*` IPC channels with dynamic port resilience (ADR-019).

---

## 6. Phase 11: Affective Memory Coupling Research (Active Increment)

The repository is actively investigating whether episodic memory retrieval can become a causally active, bounded, and reversible component of Lucia's affective dynamics (`docs/specs/lucia-phase11-Affective_Memory/AFFECTIVE_MEMORY_SPEC.md`).

### Competing Research Candidates:
1. **Candidate A (Retrieval Only — Control)**:
   - Memory echo enters prompt context only. Internal dynamics (L2, L3, L4) are 100% equivalent to no-retrieval control.
2. **Candidate B (Isolated Recollection State $r(t)$)**:
   - Evaluates whether an internal recollection vector $r(t) = (r_{\text{pad}}, r_{\text{intensity}}, r_{\text{content}})$ can maintain bounded temporal persistence ($\|r(t)\| \le 1.0$) and autonomous decay without mutating production L2/L3/L4.
3. **Candidate C (Recollection $\to$ Layer 3 Somatic Markers)**:
   - Recollection resonance modulates tension ($\Delta \mathcal{T}$) and cognitive load ($\Delta \mathcal{C}$), constraining generation budget without corrupting the continuous LNN ODE.
4. **Candidate D (Recollection $\to$ Layer 4 Active Inference Prior)**:
   - Recollection shifts the predictive prior $\hat{q}_{\text{biased}}$, testing whether Free Energy surprise and belief adaptation occur without generative matrix $A$ destabilization.
5. **Candidate E (Recollection $\to$ Layer 6 Generation Policy Threshold)**:
   - Recollection lowers the deliberative threshold $\theta_{\text{deliberative}}^{\text{eff}}$ without modifying underlying physiological state variables.

### Strict Architectural Boundaries:
- **No Direct Injection into L2 ODE ($h \in \mathbb{R}^{32}$)**: Prevent positive-feedback limbic runaway.
- **Phase 9.6 Synchronization Invariance**: Commit barrier and lock hierarchy are strictly preserved.
- **Production Isolation**: Candidates are evaluated via the dedicated research test harness `tests/unit/test_recollection_coupling.py`.
- **Bit-Exact Production Data**: `data/chat_history.json` and `data/profile.json` remain untouched.

---

## 7. Phase 11.5: Independent Evidence Audit & Production Promotion Decision

### 7.1 Audit Findings Summary
An independent scientific and architectural audit was performed on the Phase 11 research harness and canonical pipeline implementation:
1. **Four-Level Causal Hierarchy**:
   - **Level 1 (Mathematical Implementability)**: PASSED for Candidates A–E.
   - **Level 2 (Mechanistic Support in Isolation)**: PASSED for Candidates A, B, C, E; PARTIAL for D.
   - **Level 3 (Canonical End-to-End Causality)**: PASSED for Candidate A (Retrieval Only). **FAILED / NOT SUPPORTED for Candidates C, D, E**.
   - **Level 4 (Production Promotion Maturity)**: Only Candidate A qualifies. Candidates B–E fail promotion gates.
2. **Canonical Pipeline Execution Ordering**:
   - In `CognitiveOrchestrator._execute_pipeline`, execution strictly follows:
     $$\text{Stage 4 (Surprise)} \longrightarrow \text{Stage 5 (Somatic Markers \& Policy Selection)} \longrightarrow \text{Stage 6 (Affective Ecphory)}$$
   - Memory retrieval at Stage 6 cannot causally affect Stage 4 or Stage 5 within the same turn under canonical architecture.
3. **Negative Controls & Vector Dependence**:
   - Control 1 (Fake Recollection) proved that downstream somatic/policy modulation in Candidates C and E is **vector-dependent rather than memory-identity-dependent**: a synthetic vector produces the exact same modulation as a memory-derived vector.
   - Specificity gradient verified that within the Level 2 helper framework, resonance tracks affective relevance (Relevant $\gg$ Irrelevant $==$ None).

### 7.2 Production Promotion Decision

$$\textbf{NO PROMOTION — CONTINUE RESEARCH}$$
$$\textbf{Production Baseline: Candidate A (Retrieval Only)}$$

- **Candidate A** remains the sole active production architecture (Memory Retrieval $\to$ Echo $\to$ Prompt Context).
- **Candidates C and E** remain **research-only candidates** evaluated in `tests/unit/test_recollection_coupling.py`.
- No promotion ADR is created, as no candidate satisfies the production promotion gate.
- Production cognitive code (`src/core/orchestrator/`, `src/core/emotion/`) and persistent data (`data/`) remain 100% unaltered.

---

## 8. Phase 12: Knowledge Learning Research Increment

The repository has established the initial research architecture and empirical benchmark suite for **Phase 12 — Knowledge Learning** (`docs/specs/lucia-phase12-Knowledge_Learning/KNOWLEDGE_LEARNING_SPEC.md`, `tests/unit/test_knowledge_learning.py`).

### 8.1 Empirical Findings Summary (K-EXP-1 to K-EXP-12)
1. **Memory vs. Knowledge Distinction**:
   - Verified that structured conceptual knowledge (propositions, concepts, rules) can be stored and retrieved independently of Layer 5 Kanerva SDM episodic vectors.
2. **LLM-as-Teacher Boundary**:
   - Benchmarked 4 distinct operational conditions in K-EXP-11:
     - *Condition A* (LLM only): Answers via external parametric memory; zero Lucia internal provenance.
     - *Condition B* (Store lookup only): Answers explicitly memorized facts without LLM.
     - *Condition C* (Store + Derivation): Autonomously deduces unstated conclusions ($4 + 2 = 6$) via deterministic Peano addition rules without LLM involvement.
     - *Condition D* (Store + LLM): External teacher verifies internal derivation.
3. **Maturity Evaluation**:
   - Maturity levels K0 (Exposure), K1 (Memorization), K2 (Retrieval), K3 (Structured Representation), K4 (Association), K5 (Generalization), K6 (Deduction), and K8 (Revision) are **ACHIEVED** within the isolated research harness.
   - Levels K7 (Cross-domain Transfer) and K9 (High-order Synthesis) remain open research questions.

### 8.2 Production Promotion Gate & Decision

$$\Large\mathbf{PHASE\ 12\ RESEARCH\ CONTINUES}$$
$$\mathbf{Production\ Baseline:\ Unaltered\ Canonical\ Cognition}$$

- **Production Isolation**: The Knowledge Learning subsystem is strictly contained within `tests/unit/test_knowledge_learning.py`.
- **Zero Production Mutation**: No files in `src/core/` are modified.
- **Gate Evaluation**: While local storage, derivation, and revision pass all criteria, canonical runtime integration into `CognitiveOrchestrator` is deferred. No promotion ADR is created.

---

## 9. Phase 13: Relationship Development Research Increment

The repository has formalized and empirically validated the research architecture for **Phase 13 — Relationship Development** (`docs/specs/lucia-phase13-Relationship_Development/RELATIONSHIP_DEVELOPMENT_SPEC.md`, `tests/unit/test_relationship_development.py`).

### 9.1 Empirical Findings Summary (R-EXP-1 to R-EXP-12)
1. **Core Relational Orientation vs. Dynamic Relationship State**:
   - *Philia* remains an invariant resting attractor ($P=+0.25, A=-0.05, D=+0.05$) providing unconditional benevolence.
   - Dynamic Relationship State $R_t = (\mathcal{F}, \mathcal{T}, \mathcal{K}, \mathcal{C}) \in [0, 1]^4$ tracks per-user familiarity, trust, closeness, and continuity.
2. **Temporal Inertia Principle ($\tau_{\text{rel}} \gg \tau_{\text{turn}}$)**:
   - Validated in R-EXP-2: an acute negative stimulus shifts limbic pleasure by $\Delta P = -0.193$, while relationship trust moves by at most $\Delta \mathcal{T} = -0.015$ under adaptation rate $\alpha = 0.03$.
3. **Multi-Turn Accumulation & Absence Decay**:
   - 20 collaborative turns elevated trust from $0.50$ to $0.672$ and closeness from $0.10$ to $0.263$ monotonically (R-EXP-3).
   - 60-day unforced absence decayed familiarity by $0.076$ and continuity by $0.118$ while preserving baseline trust (R-EXP-4).
4. **History-Dependent Divergence (Hysteresis)**:
   - Identical neutral probe yields divergent trust states ($\Delta \mathcal{T} = 0.443$) after divergent historical trajectories (supportive vs. hostile, R-EXP-5).
5. **Architectural Orthogonality**:
   - SDM memory clearing leaves $R_t$ bit-exact (R-EXP-8).
   - Instantaneous PAD volatility is completely decoupled from $R_t$ (R-EXP-9).
   - Knowledge acquisition leaves $R_t$ untouched (R-EXP-10).
6. **Deterministic Reproducibility & 100-Turn Longitudinal Stability**:
   - Exact replay matches with $\text{atol} \le 10^{-12}$ (R-EXP-11).
   - 100-turn stochastic stress test with mixed noise, conflict, and repair proved bounded stability in $[0, 1]^4$ with zero NaNs and healthy dynamic range (R-EXP-12).

### 9.2 Production Promotion Gate & Decision

$$\Large\mathbf{PHASE\ 13\ RESEARCH\ CONTINUES}$$
$$\mathbf{Production\ Baseline:\ Unaltered\ Canonical\ Cognition}$$

- **Production Isolation**: The Relationship Development research framework is strictly isolated to `tests/unit/test_relationship_development.py` and canonical research specifications.
- **Zero Production Mutation**: Core runtime files (`src/core/`) and persistent data (`data/chat_history.json`, `data/profile.json`) remain bit-exact.
- **Decision Rationale**: While mathematical formulation and empirical stability across 12 experiments are fully proven, direct integration into `CognitiveOrchestrator` is deferred until Phase 16 (Affective Life Integration). No promotion ADR is authored.

---

## 10. Phase 14: Embodiment & Affective Expression Research Increment

The repository has formalized and empirically validated the research architecture for **Phase 14 — Embodiment & Affective Expression** (`docs/specs/lucia-phase14-Embodiment_Affective_Expression/AFFECTIVE_EXPRESSION_SPEC.md`, `tests/unit/test_affective_expression.py`).

### 10.1 Empirical Findings Summary (E-EXP-1 to E-EXP-12)
1. **Multimodal State Representation & Bounding**:
   - $E_t = (\text{Text}, \text{Voice}, \text{Facial}, \text{Posture}, \text{Latency})$ strictly clamped within physiological bounds; extreme inputs ($\pm 999.0$) safely handled without overflow or NaNs (E-EXP-1).
2. **PAD $\to$ Expression Sensitivity Gradients**:
   - Slopes verified for $\frac{\partial \text{smile}}{\partial P}$, $\frac{\partial \text{rate}}{\partial A}$, $\frac{\partial \text{vol}}{\partial D}$; non-linear blush threshold confirmed at $P > 0.15$ (E-EXP-2).
3. **Temporal Coherence & Smoothing**:
   - Trajectories under $\gamma_{\text{expr}} = 0.25$ converge monotonically without discontinuous jumps or overshoot (E-EXP-3).
4. **Hard Semantic Preservation Invariant**:
   - 100% preservation of propositions, entities, and numbers across 4 challenging affective regimes (Warm, Neutral, Melancholic, Agitated) with 0.0% polarity flips (E-EXP-4).
5. **Modality Specificity & Cross-Modal Consistency**:
   - $P$ preferentially drives facial warmth/smile, $A$ preferentially drives voice rate/alertness (E-EXP-5).
   - Predefined cross-modal coherence $\ge 0.85$ achieved on harmonious states ($0.91$); engineered contradictory states rejected with $\mathcal{A} = 0.28$ (E-EXP-6).
6. **Actuator Decoupling & Pure Feedforward Directionality**:
   - Disabling affect collapses expression to predefined neutral actuator baseline without zeroing Philia attractor ($P=+0.25, A=-0.05, D=+0.05$) (E-EXP-7).
   - Expression actuator has zero feedback into internal L2 ODE hidden state or PAD (E-EXP-8).
7. **Policy Computation Latency vs. Pipeline Scope**:
   - Mean policy computation latency measured at $0.05\text{ms}$ on CPU, well within the predefined $\le 5.0\text{ms}$ threshold, strictly distinguished from the multi-second asynchronous TTS/LLM pipeline (E-EXP-12).

### 10.2 Production Promotion Gate & Decision

$$\Large\mathbf{PHASE\ 14\ RESEARCH\ CONTINUES}$$
$$\mathbf{Production\ Baseline:\ Unaltered\ Canonical\ Cognition}$$

- **Production Isolation**: Expression policy is maintained strictly inside `tests/unit/test_affective_expression.py` and canonical specifications.
- **Zero Production Mutation**: Core runtime files (`src/core/`) and persistent data (`data/`) remain 100% bit-exact.
- **Decision Rationale**: While mathematical policy, semantic preservation, and cross-modal consistency are fully demonstrated in the research harness, canonical production integration into `CognitiveOrchestrator` and turn-synchronous IPC push to Electron are deferred to Phase 16 (Affective Life Integration). No promotion ADR is authored.

---

## 11. Phase 15: Affective Communication Research Increment

The repository has formalized and empirically validated the research architecture for **Phase 15 — Affective Communication** (`docs/specs/lucia-phase15-Affective_Communication/AFFECTIVE_COMMUNICATION_SPEC.md`, `tests/unit/test_affective_communication.py`).

### 11.1 Empirical Findings Summary (C-EXP-1 to C-EXP-12)
1. **Multidimensional State Representation & Bounding**:
   - $C_t \in \mathbb{R}^{10}$ (directness, elaboration, supportiveness, formality, acknowledgement, question frequency, injected pacing latency, memory context, knowledge context, safety flag) strictly clamped within physiological bounds under normal and extreme inputs ($\pm 10.0$) (C-EXP-1).
2. **Affect-to-Communication Strategy Modulation**:
   - High pleasure elevates supportiveness by $\Delta \mathcal{S}_u \ge 0.20$; dominance variation modulates directness by $|\Delta \mathcal{D}_r| \ge 0.15$ holding semantic intent constant (C-EXP-2).
3. **Somatic & Homeostatic Pacing Modulation**:
   - Metabolic energy depletion throttles elaboration depth ($\Delta \mathcal{E}_l \le -0.20$) and actively injects somatic pacing latency ($150\text{ms} \le \mathcal{L}_p \le 1000\text{ms}$) to model conversational fatigue without latency runaway, strictly distinct from LLM/TTS hardware latency (C-EXP-3).
4. **Interpersonal Relational Framing**:
   - Relationship development (trust and closeness) elevates supportiveness ($\Delta \mathcal{S}_u \ge 0.15$) and reduces formality ($\Delta \mathcal{F}_s \le -0.15$) holding acute PAD at Philia baseline (C-EXP-4).
5. **Episodic Recollection Grounding**:
   - SDM memory availability elevates conversational acknowledgement ($\Delta \mathcal{A}_k \ge 0.15$) and memory context weight ($\Delta \mathcal{C}_{x, M} = 0.50$) (C-EXP-5).
6. **Knowledge Contextual Grounding**:
   - Structured knowledge availability elevates elaboration depth ($\Delta \mathcal{E}_l \ge 0.20$) while maintaining 100% semantic grounding across known vs unknown facts without fabrication (C-EXP-6).
7. **Subsystem Specificity & Orthogonal Ablations**:
   - Subsystem specificity verified: energy modulates elaboration, not support; affect modulates support, not elaboration (C-EXP-8).
   - Ablation A (Affect OFF) collapses supportiveness toward actuator neutral baseline without zeroing Core Philia in EmotionCore (C-EXP-9).
   - Ablation B (Relationship OFF) resets supportiveness and formality to stranger baseline (C-EXP-10).
   - Ablation C (Memory OFF) collapses memory context referencing ($\mathcal{C}_{x, M} \to 0.0$) while knowledge-derived contextual grounding ($\mathcal{C}_{x, K} = 0.50$) remains fully active, strictly preserving Memory vs Knowledge separation (C-EXP-11).
8. **Multimodal Alignment & Policy Latency**:
   - Communication strategy and expression parameters achieve cross-modal alignment $\ge 0.85$. Policy computation latency executes in $< 0.10\text{ms}$ on CPU, well within the predefined $\le 5.0\text{ms}$ limit (C-EXP-12).

### 11.2 Semantic Preservation Evidence Under the Controlled Benchmark
Across all 5 canonical communication strategies (`DIRECT_FACTUAL`, `REASSURING_WARM`, `CONCISE_RESERVED`, `ELABORATIVE_EXPLANATORY`, `COLLABORATIVE_INQUIRING`), core propositional truth $(S, P, O, \text{polarity})$ and all numerical/entity values are 100% preserved under the controlled benchmark evaluation. Zero introspective emotion labels (*"I feel"*, *"I am happy"*) were emitted across any test case.

### 11.3 Production Promotion Gate & Decision

$$\Large\mathbf{PHASE\ 15\ RESEARCH\ CONTINUES}$$
$$\mathbf{Production\ Baseline:\ Unaltered\ Canonical\ Cognition}$$

- **Production Isolation**: Communication policy is strictly contained within `tests/unit/test_affective_communication.py` and canonical specifications.
- **Zero Production Mutation**: Core runtime files (`src/core/`) and persistent data files (`data/`) remain 100% bit-exact.
- **Decision Rationale**: While mathematical formulation, strategy classification, pacing modulation, and benchmarked semantic preservation are fully proven, live full-pipeline synchronization (`Brain → Orchestrator → LLM → Voice → Avatar → synchronized Body`) requires end-to-end integration architecture, which is deferred to **Phase 16 (Unified Embodied Interaction / Affective Life Integration)**. No production promotion ADR is authored.

*(Historical Record: The research frameworks of Phase 12, 13, 14, and 15 were subsequently promoted and unified into the production codebase in Phase 16 via ADR-021, ADR-022, ADR-023, ADR-024, and ADR-025).*

---

## 12. Phase 16: Affective Life Integration & Canonical 16-Stage Pipeline Realization

Phase 16 (`docs/specs/lucia-phase16-Affective_Life_Integration/PHASE_16_ARCHITECTURE.md`) formally promoted and integrated the individual research modules of Phases 12–15 into a unified, end-to-end cognitive architecture.

### 12.1 Promoted Production Subsystems:
1. **Conceptual Knowledge Subsystem (`src/core/knowledge/`, ADR-021)**:
   - Typed `Proposition` & `Concept` graph with provenance tracking (`DIRECT_EXPERIENCE`, `USER_STATED`, `INFERRED`, `CORE_AXIOM`).
   - Forward inference engine ($d_{\max} \le 3$), thread-safe `KnowledgeStore`, atomic persistence.
2. **Interpersonal Relationship Subsystem (`src/core/relationship/`, ADR-022)**:
   - Persistent 4D state $\mathbf{R} = (\text{trust}, \text{familiarity}, \text{attunement}, \text{shared\_experience})$.
   - Decoupled two-phase lifecycle: Stage 9 read snapshot vs. Stage 16 post-turn categorical signal update with inertia ($\alpha=0.03$) and absence decay ($0.005$).
3. **Affective Communication & Contextual Grounding (`src/core/communication/`, ADR-023)**:
   - 10D `CommunicationState`, 5 discrete modes (`DEEP_RECIPROCAL`, `ATTUNED_LIGHT`, `SUPPORTIVE_GROUNDING`, `CONCISE_PROTECTIVE`, `PLAYFUL_EXPLORATORY`).
   - Bounded memory contextualization ($m_{ctx} \le 0.50$, zero limbic feedback), somatic pacing latency ($0 \le \tau \le 1000\text{ms}$).
4. **Multimodal Expression Policy (`src/core/expression/`, ADR-024)**:
   - Canonical 15-dim `ExpressionState` (3 text, 4 prosody, 5 facial blendshapes, 2 posture, 1 latency).
   - Pure feedforward actuator decoupling (zero feedback into ODE $\mathbf{h} \in \mathbb{R}^{32}$), temporal smoothing ($\gamma=0.25$).
5. **Storage Policy Isolation (`src/core/simulation/storage_policy.py`, ADR-025)**:
   - Strict ephemeral RAM interception for test fixtures, guaranteeing bit-exact zero contamination of `data/` runtime files.

### 12.2 Canonical Locked S1–S16 Cognitive Pipeline Execution Order:
`CognitiveOrchestrator._execute_pipeline` executes strictly in linear sequence:
- **S1: Sensory Gating**: Raw text encoded to 16D continuous stimulus vector $\mathbf{x}(t)$ via `StimulusProcessor`.
- **S2: Limbic Fast Loop**: Injects stimulus and commits ODE step under deterministic synchronization barrier.
- **S3: Homeostatic Assessment**: Evaluates metabolic energy, cognitive load, stability, and acute tension.
- **S4: Active Inference**: Computes prediction surprise $\mathcal{S} = \|A \cdot p_{\text{before}} + b - p_{\text{after}}\|_2$; updates belief vector $b$.
- **S5: Homeostatic Policy Selection**: Translates homeostatic and surprise state into generation constraints (token budget, temperature, reasoning depth $k$).
- **S6: Affective Ecphory & Recollection**: Performs associative cosine resonance; in Phase 20, evaluates multi-modal salience and triggers bounded slow-field forcing.
- **S7: Memory Contextualization**: Formats echo vector and bounded episodic context into prompt context lines.
- **S8: Conceptual Knowledge Retrieval**: Queries `KnowledgeStore` for relevant structured propositions and concepts.
- **S9: Interpersonal Relationship Snapshot**: Reads current immutable 4D relationship state $\mathbf{R}_t$.
- **S10: Affective Communication Policy**: Determines communication strategy, formality, and directness from affect, relationship, and somatic state.
- **S11: Language Generation**: Assembles pre-reflective prompt and executes local CUDA GGUF SLM inference.
- **S12: Boundary Safety & Pacing**: Validates output through `BoundaryLayer` regex filters; computes somatic + recollection pacing latency ($\Delta\tau_{\text{pace}}$).
- **S13: Multimodal Expression Policy**: Derives canonical 15D `ExpressionState` for avatar blendshapes, prosody, and posture.
- **S14: Epistemic & SDM Storage**: Stores interaction trace in Kanerva SDM; in Phase 20 (Stage 16.1), co-encodes live slow latent field $\mathbf{s}_{\text{slow}}(t)$.
- **S15: Plasticity Salience Tagging**: Evaluates turn salience; queues high-salience transitions for offline CPU consolidation.
- **S16: Post-Turn Relationship Update**: Applies slow relational updates ($\alpha=0.03$) with temporal inertia based on turn interaction signals.

---

## 13. Phase 17: Integrated Affective Life Evaluation & Longitudinal Validation

Phase 17 executed comprehensive end-to-end evaluation of the integrated cognitive architecture under multi-turn simulated sessions.
- **System Stability**: Verified absence of numerical stalls, drift, or state saturation across 100+ simulated turns.
- **Subsystem Orthogonality**: Confirmed that memory decay, relationship inertia, knowledge updates, and limbic ODE operate orthogonally without uncontrolled cross-talk.
- **Cognitive Coherence**: Verified that generation constraints, communication policy, and multimodal expression remain synchronized with internal physiological state.

---

## 14. Phase 18: Human Longitudinal Interaction & Real-World Validation

Phase 18 (`docs/specs/lucia-phase18-Human_Longitudinal_Validation/`) established human-grounded empirical validation across 8 longitudinal interaction scenarios (Scenarios A through G).
- **Japanese Canonical Voice Realization**: Direct on-device neural RVC v2 synthesis (`RVCPipeline` + `SynthesizerTrn`) using canonical `ja-JP-NanamiNeural` base voice and `VaresaGIJP` target timbre.
- **Controlled Signal Path Diagnosis**: Audited harmonic generator, Parselmouth F0 unvoiced interpolation, pre-interpolation FAISS $k=8$ retrieval, and headroom normalization; verified 100% Whisper ASR match, zero clipping, and clean intelligibility.
- **Audiovisual Synchronization**: Validated 60 FPS Web Audio FFT formant analysis driving quad-engine avatar blendshapes and mouth aperture height.
- **Adversarial & Boundary Verification**: 100% compliance with non-introspective safety invariants across challenging conversational probes.

---

## 15. Phase 19: Multi-Timescale Affective Life & Temporal Continuity (MT-LNN)

Phase 19 (`docs/specs/Lucia-phase19-Multi_Timescale_Affective_Life/`) resolved the single-timescale affective amnesia limitation of earlier limbic ODE architectures by implementing the Coupled Multi-Timescale Liquid Neural Network.

### 15.1 Production Architecture & Canonical Parameters:
- **Coupled Dual-Timescale State Space**:
  - Fast reactive layer: $\mathbf{h}_{\text{fast}} \in \mathbb{R}^{32}$ with $\tau_f \in [0.10, 1.50]\text{ s}$ (`hidden_dim = 32`, `tau_fast_min = 0.10`, `tau_fast_max = 1.50`).
  - Slow affective latent field: $\mathbf{s}_{\text{slow}} \in \mathbb{R}^{16}$ (`hidden_slow_dim = 16`).
  - Charging time-constant: $\tau_{\text{slow, charge}} = 3.50\text{ s}$ (`tau_slow_charge = 3.50`).
  - Relaxation time-constant: $\tau_{\text{slow, decay}} = 28.00\text{ s}$ (`tau_slow_decay = 28.00`).
  - Coupling strengths: $\mathbf{W}_{fs} = 0.05$ (`w_fs_coupling = 0.05`), $\mathbf{W}_{sf} = 1.00$ (`w_sf_coupling = 1.00`), $\mathbf{W}_{sh} = 0.40$ (`w_homeo_coupling = 0.40`).
- **Philia Attractor Grounding (State Space Distinction)**:
  - **3D PAD Resting Baseline**: $\mathbf{p}^*_{\text{philia}} = (+0.25, -0.05, +0.05) \in [-1, 1]^3$ (`resting_baseline = (0.25, -0.05, 0.05)`). Defines the emotional output equilibrium in Pleasure, Arousal, Dominance.
  - **16D Slow Latent Field Attractor**: $\mathbf{s}^*_{\text{philia}} = (0.20, -0.05, 0.05, 0, \dots, 0) \in \mathbb{R}^{16}$ (`philia_slow_baseline = (0.20, -0.05, 0.05)`). Defines the resting coordinates centering the slow latent manifold ($\Delta\mathbf{s} = \mathbf{s}_{\text{slow}} - \mathbf{s}^*_{\text{philia}}$).
  - *Distinction*: These are two distinct vectors in different state spaces. Unforced idle decay relaxes $\mathbf{s}_{\text{slow}} \to \mathbf{s}^*_{\text{philia}}$, which through linear projection readout restores the output $\mathbf{PAD} \to \mathbf{p}^*_{\text{philia}} = (+0.25, -0.05, +0.05)$ bit-exact. Legacy Case 1 uses $\mathbf{p}^*_{\text{philia}}$ to detect resting state and reconstructs $\mathbf{s}^*_{\text{philia}}$.
- **Mathematical Invariants & Empirical Validation**:
  - Strictly dissipative Lyapunov contraction ($\text{Tr}(J) \approx -46.46 < 0$ across tested domain), preventing runaway saturation.
  - Autonomous stress-to-fatigue transformation verified across unforced idle intervals (84/90 steps in fatigue quadrant).
  - Path-dependent historical hysteresis divergence ($\Delta_{\max} = 0.1749$).
  - Mean CPU step latency: $1.332\text{ ms}$; 0.0 MB GPU VRAM contention.
  - Validated by 15/15 passing tests in `tests/evaluation_phase19/`.
  - Production commit: `c23fe7e`.

---

## 16. Phase 20: Affective Recollection & Memory Reactivation (Production Realization)

Phase 20 (`docs/specs/Lucia-phase20-Affective_Recollection/`) resolved the open-loop limitation of memory retrieval by implementing Closed-Loop Affective Recollection via Slow-Field Latent Forcing.

### 16.1 Architectural Mechanism:
1. **Episodic Latent Trace Co-Encoding (Stage 16.1)**:
   - In Stage 16.1, `CognitiveOrchestrator` queries the live physiological slow latent state $\mathbf{s}_{\text{slow}}(t) \in \mathbb{R}^{16}$ via `EmotionCore.get_slow_latent_state()` and passes it to `AffectiveMemory.store()`.
   - Stored in `MemoryTrace.slow_latent_trace` ($\mathbb{R}^{16}$, float32, 64 bytes per episode).
2. **Multi-Modal Retrieval Scoring & Competitive Softmax Gating (Stage 6)**:
   - Composite salience score: $S_i = 0.60 S_{\text{sem}} + 0.25 S_{\text{aff}} + 0.15 w_{\text{decay}}$.
   - Traces filtered by activation threshold $\theta_{\text{gate}} = 0.50$ (`recollection_gate_threshold = 0.50`) and weighted by competitive temperature $\tau_{\text{comp}} = 0.20$ (`recollection_softmax_temp = 0.20`).
   - Synthesizes bounded forcing vector: $\mathbf{r}_{\text{slow}}^{\text{bounded}} = \text{clip}(\tanh(\mathbf{r}_{\text{slow}}) \cdot 0.85, -0.85, 0.85)$.
3. **Continuous ODE Slow-Field Forcing**:
   - `CognitiveOrchestrator` dispatches `EmotionCore.inject_recollection(r_slow, duration_sec=4.0)`.
   - Injected into slow differential equation under diagonal coupling $\mathbf{W}_{\text{rec}} = 0.35 \mathbf{I}_{16}$ (`recollection_coupling_weight = 0.35`):
     $$\frac{d\mathbf{s}_{\text{slow}}}{dt} = -\frac{\mathbf{s}_{\text{slow}} - \mathbf{s}^*_{\text{philia}}}{\tau_{\text{slow, decay}}} + \frac{\tanh\Big(\mathbf{W}_{sf} \mathbf{h}_{\text{fast}} + \mathbf{W}_{sh} \Delta\mathbf{m} + \mathbf{W}_{\text{rec}} \mathbf{r}_{\text{slow}}^{\text{bounded}}\Big)}{\tau_{\text{slow, charge}}}$$
   - Forcing window is tracked strictly in **simulation integration time** across step boundaries; wall-clock `time.monotonic()` is strictly prohibited inside the numerical ODE derivatives.
4. **Deterministic Legacy Compatibility Approximation**:
   - For pre-Phase-20 memories lacking a slow latent trace, `AffectiveMemory.synthesize_legacy_latent()` enforces a strict 3-case contract:
     - Case 1 (Baseline PAD): Returns bit-exact $\mathbf{s}^*_{\text{philia}}$.
     - Case 2 (Non-baseline valid PAD): Bounded linear projection $\mathbf{s}_{\text{approx}} = (\mathbf{W}_{\text{pad}\to\text{slow}} \Delta\mathbf{p}) + \mathbf{s}^*_{\text{philia}}$ clipped to $[-0.85, 0.85]$.
     - Case 3 (Non-finite/NaN/Inf): Safe defensive fallback to $\mathbf{s}^*_{\text{philia}}$.
5. **Pre-Reflective Downstream Pacing Modulation (Stage 12)**:
   - Somatic pacing latency delta: $\Delta\tau_{\text{pace}} = w_{\text{pace}} \cdot \|\mathbf{r}_{\text{slow}}^{\text{bounded}}\|$ (`recollection_pacing_weight = 120.0`).
   - Modulates conversational cadence organically without introspective roleplay.
6. **Subsystem Decoupling & Feature Flag**:
   - `EcphoryEngine` emits `RecollectionResult` and has ZERO dependency on `EmotionCore`.
   - `CognitiveOrchestrator` owns actuation.
   - Runtime feature flag `enable_affective_recollection: bool = True` allows instant rollback to Phase-19 affective execution path while preserving data schemas.

### 16.2 Production Validation:
- Production implementation commit: **`f20420a`**.
- 9/9 production tests passing in `tests/unit/test_phase20_production.py`.
- 10/10 research evaluation tests passing in `tests/evaluation_phase20/`.
- 592/592 full unit test suite passing.
- 35/35 property invariants passing.
- Storage invariant verified bit-exact: `data/profile.json == {"is_onboarded": false}`.

---

## 17. Concurrency, Thread Safety & Verified Lock Hierarchy

All components strictly observe the verified repository lock hierarchy:

```
┌────────────────────────────────────────────────────────────────────────┐
│                   CANONICAL LOCK HIERARCHY DISCIPLINE                  │
│                                                                        │
│   1. _turn_lock     (CognitiveOrchestrator: non-reentrant mutex)       │
│   2. _step_lock     (EmotionCore: serializes ODE numerical ticks)      │
│   3. _train_lock    (EmotionCore: atomic weight swaps, held ≤ 2ms)     │
│   4. _stimulus_lock (EmotionCore: FIFO pending stimuli queue, ≤ 0.1ms) │
│   5. _state_lock    (EmotionCore: PAD & slow latent snapshot, ≤ 1ms)   │
│                                                                        │
│   Auxiliary:                                                           │
│   • _index_lock     (AffectiveMemory: SDM trace insert & decay sweep)  │
│                                                                        │
│   RULES:                                                               │
│   - Always acquire _train_lock BEFORE _state_lock.                     │
│   - NEVER acquire _state_lock and then attempt to acquire _train_lock. │
│   - Hold locks strictly for bounded in-memory copies (≤ 1–2ms).        │
│   - NEVER perform disk I/O, network requests, or LLM calls under locks.│
└────────────────────────────────────────────────────────────────────────┘
```

---

## 18. Quality Assurance, Automated Test Suite & Storage Invariant Verification

Authoritative test suite results as of commit `f20420a`:

| Test Suite | Path | Total | Passed | Skipped | Notes |
|---|---|---|---|---|---|
| **Unit Test Suite** | `tests/unit/` | 592 | **592** | 0 | Comprehensive coverage across all subsystems |
| **Property Tests** | `tests/property/` | 35 | **35** | 0 | Hypothesis property invariants (P1–P35) |
| **Phase 19 Research** | `tests/evaluation_phase19/` | 15 | **15** | 0 | Multi-timescale empirical evaluation (EXP19.1–8) |
| **Phase 20 Research** | `tests/evaluation_phase20/` | 10 | **10** | 0 | Recollection empirical evaluation (EXP20.1–10) |
| **Phase 20 Production** | `tests/unit/test_phase20_production.py` | 9 | **9** | 0 | Black-box causal, fallback, gating & orchestrator tests |
| **Integration Tests** | `tests/integration/` | 47 | **40** | 7 | 7 skipped in `test_llm_backend_integration.py` (`LUCIA_MODEL_PATH` unset) |

### Canonical Storage Invariant:
- `data/profile.json` SHA-256 / content check:
  ```json
  {"is_onboarded": false}
  ```
  Verified bit-exact. Zero test-state or simulation contamination of production runtime files.

---

## 19. Canonical Research Roadmap & Next Milestone Status

```
┌────────────────────────────────────────────────────────────────────────┐
│                      LUCIA MILESTONE STATUS MATRIX                     │
├────────────────────────────────────────────────────────────────────────┤
│ Phase 1–10: Core Limbic & Dynamics               [✅ VALIDATED]        │
│ Phase 11–15: Cognitive & Embodiment Research     [🔬 VALIDATED RES.]   │
│ Phase 16: Affective Life Integration             [✅ VALIDATED]        │
│ Phase 17: Integrated Affective Life Evaluation   [✅ VALIDATED]        │
│ Phase 18: Human Longitudinal Validation          [✅ VALIDATED]        │
│ Phase 19: Multi-Timescale Affective Life         [✅ VALIDATED]        │
│ Phase 20: Affective Recollection                 [✅ VALIDATED]        │
│ Phase 21: Relational Consolidation & Synaptic    [🔬 PLANNED RESEARCH] │
│           Homeostasis (Next Research Milestone)                        │
│ Phase 22–26: Future Conceptual Horizons          [🔬 CONCEPTUAL]       │
│ First Activation (Genesis Onboarding)            [🔒 FUTURE GATE]      │
└────────────────────────────────────────────────────────────────────────┘
```

### 19.1 Current Completed Baseline:
- **Phase 19 (Multi-Timescale Affective Life & Temporal Continuity)**:
  - Status: Research Validated $\to$ Architecture Approved $\to$ Production Implemented (`c23fe7e`).
  - Realization: Coupled Multi-Timescale Liquid Neural Network (MT-LNN: $\mathbf{h}_{\text{fast}} \in \mathbb{R}^{32}, \mathbf{s}_{\text{slow}} \in \mathbb{R}^{16}$) with Philia dynamic attractor grounding and biexponential relaxation.
- **Phase 20 (Affective Recollection & Memory Reactivation)**:
  - Status: Research Validated $\to$ Architecture Approved $\to$ Production Implemented (`f20420a`).
  - Realization: Closed-loop slow-field latent forcing ($\mathbf{W}_{\text{rec}}\mathbf{r}_{\text{slow}}^{\text{bounded}}$), multi-modal retrieval scoring, competitive softmax gating, 16D slow trace co-encoding, and somatic pacing latency modulation.
  - Core Invariant: *Memory provides information; CognitiveOrchestrator decides actuation.* Affective recollection does not directly call or own `EmotionCore`.

### 19.2 Canonical Next Research Milestone: Phase 21
- **Phase Name**: **Phase 21 — Long-Term Relational Consolidation & Synaptic Homeostasis**
- **Lifecycle Status**: **`[🔬 PLANNED RESEARCH — NOT IMPLEMENTED]`**
- **Research Question & Objective**:
  Investigate how repeated interaction, accumulated shared history, and episodic recollection produce longer-term relational consolidation and adaptive homeostatic/synaptic plasticity without violating Lucia's fundamental architectural invariants.
- **Scope & Boundaries**:
  - *Research-Only Phase*: Operates strictly in the research/experimentation cycle before any architecture gate or production realization.
  - *Strict Non-Implementation*: Zero production code (`src/core/**`), zero runtime configuration changes, and zero permanent storage mutations.
  - *Pre-Reflective Dynamical Discipline*: Relational consolidation manifests as unconscious parameter/weight attunement and baseline inertia, strictly prohibiting self-reported emotional declarations (*"We are closer now"*).
  - *Storage Invariant*: Canonical `data/profile.json` remains permanently untouched (`{"is_onboarded": false}`).

### 19.3 Future Conceptual Research Horizons (Phases 22–26):
Beyond Phase 21, the agreed long-range research sequence spans five progressive conceptual horizons:
1. **Phase 22 — Active Inference & Information Seeking**: Epistemic foraging, curiosity-driven question selection, and uncertainty reduction within conversational turns.
2. **Phase 23 — Affective Communication Adaptation**: Long-term stylistic attunement, conversational rhythm adaptation, and shared dialectical grounding.
3. **Phase 24 — Temporal Embodiment & Social Feedback**: Interpersonal synchrony, micromovement resonance, and reciprocal gaze/prosody dynamics.
4. **Phase 25 — Emergent Individuality & Autonomous Preferences**: Asymmetric curiosity, idiosyncratic topical affinities, and authentic aesthetic preferences grounded in shared history.
5. **Phase 26 — Personalized Individual Trajectory**: Coherent lifelong developmental trajectory unique to Lucia's single continuous relationship with the user.

### 19.4 First Activation Guard:
- `Development / Simulation != Lucia Activation`.
- `data/profile.json` remains `{"is_onboarded": false}` bit-exact.
- First Activation ceremony remains an immutable future gate (`[🔒 FUTURE GATE]`) requiring complete empirical verification of all prior research horizons before authorization.






