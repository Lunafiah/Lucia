# PHASE_9.md — Unified Cognitive Architecture Specification (v2.0)

> **Authoritative Phase 9 Specification: Unified Cognitive Orchestrator, Causal Active Inference, Decoupled Voice Expression, and Complete IPC Mediation**  
> **Status**: ARCHITECTURE GATE — REVISED / AWAITING USER SIGN-OFF  
> **Architecture Gate Reference**: [`PHASE_9_ARCHITECTURE_GATE.md`](file:///c:/Users/Lunafiah/Desktop/My_project/Lucia/PHASE_9_ARCHITECTURE_GATE.md)  
> **Baseline Review**: [`PHASE_8_ARCHITECTURE_REVIEW.md`](file:///c:/Users/Lunafiah/Desktop/My_project/Lucia/PHASE_8_ARCHITECTURE_REVIEW.md)  
> **Target Milestone**: Phase 9 (System Convergence & Cognitive Unification)  
> **Invariant**: ZERO PRODUCTION CODE MODIFICATIONS UNTIL FORMALLY APPROVED

---

## 1. Executive Summary & Core Objective

The objective of **Phase 9** is **Cognitive Unification & Architectural Convergence**.

During the Phase 9 Architectural Decision Gate (Revision v2.0), the theoretical Russian-doll inheritance model (`UnifiedPresenceOrchestrator`) was formally rejected. In its place, Phase 9 establishes a **clean, composition-based cognitive architecture** that resolves all architectural findings from Phase 8:

1. **Unified Cognitive Orchestrator (`CognitiveOrchestrator`)**: Deprecates the fragile 5-tier inheritance ladder (`Orchestrator` $\rightarrow$ `MemoryAugmentedOrchestrator` $\rightarrow$ `InferencePipelineOrchestrator` $\rightarrow$ `PresenceOrchestrator` + `InstrumentedOrchestrator`). Implements a single, cohesive orchestrator composing Layers 1–6 in a linear, non-redundant execution flow.
2. **Causal Active Inference (Layer 4 Integration)**: Integrates `ActiveInferenceEngine` into every live turn. Evaluates pre-stimulus prediction expectations ($\hat{p} = A \cdot p_{t-1} + b$), measures Prediction Surprise $\mathcal{S}_t = \|\hat{p} - p_t\|_2$, and causally modulates Homeostatic Cognitive Load, Tension, and Deliberative Generation Mode ($k=2$ when $\mathcal{S}_t > 0.60$ or $\mathcal{T}_t > 0.70$).
3. **Decoupled Expression Pipeline for Voice**: Voice synthesis remains an independent multimodal expression service triggered asynchronously by the Body UI via IPC. It is decoupled from the synchronous cognitive return, guaranteeing zero text latency, complete failure isolation, and zero compute waste when muted.
4. **Two-Stage LNN Plasticity with Decoupled Policy**: Replaces arbitrary "every 16 turns" batch training with online salience tagging during turns ($< 0.1\text{ms}$) and offline consolidation on CPU during idle rest periods ($T_{\text{idle}} \ge 45\text{s}$) or salience threshold overflows, governed by `PlasticityPolicy`.
5. **5-Tier Concurrency Architecture**: Enforces request admission serialization (`asyncio.Lock()`, max queue depth 1 with HTTP 429) in `server.py`, thread pool worker dispatch, and a non-reentrant `threading.Lock()` in `CognitiveOrchestrator` to prevent concurrent turn corruption while preserving non-blocking sub-millisecond `/state` polling.
6. **State Ownership Discipline & Immutable `CognitiveTurnResult`**: Establishes that `CognitiveOrchestrator` owns the turn lifecycle, not the persistent state. Subsystems maintain their own state. Turns return a frozen, immutable `CognitiveTurnResult` data carrier.
7. **Complete Brain ↔ Body IPC Remediation**: Eliminates all 12 direct `fetch()` calls in `chat.js`, routing all voice, history, profile, and asset queries through `window.lucia.*` via `preload.js` and `ipc-bridge.js`.

---

## 2. Canonical Cognitive Turn Flow

```mermaid
flowchart TD
    UserMsg([User Input Text]) --> L1[Layer 1: StimulusProcessor]
    L1 -->|16D Stimulus Vector x_t| L4a[Layer 4a: Active Inference Prediction p̂ = A · p_t-1 + b]
    L4a -->|Expected p̂| L2[Layer 2: Limbic ODE solve_ivp]
    L2 -->|Observed PAD p_t| L4b[Layer 4b: Active Inference Surprise S_t & Belief Update]
    L4b -->|Surprise S_t & Belief Update| L3[Layer 3: Homeostatic Engine via SurpriseModulationPolicy]
    L3 -->|Somatic Markers & Constraints [k, temp, latency]| L5a[Layer 5a: Ecphory Query]
    L5a -->|Subconscious Echo Vector| L6a[Layer 6a: Prompt Assembler via GenerationPolicy]
    L6a -->|Conditioned Prompt with [REASONING]| L6b[Layer 6b: Local SLM Generate]
    L6b -->|Raw Text| L6c[Layer 6c: BoundaryLayer Filter]
    L6c -->|Safe Response| MemoryStore[Layer 5b: SDM Trace Store with Surprise Salience]
    MemoryStore --> HistAppend[Append Working Context Pair]
    HistAppend --> PlasticityTag[Layer 4c: Tag Salient Experience for Idle Consolidation via PlasticityPolicy]
    PlasticityTag --> TurnReturn([Return Frozen CognitiveTurnResult: Text + PAD + Somatic + Surprise])
```

---

## 3. Subsystem Specifications

### 3.1. Unified Cognitive Orchestrator (`src/core/orchestrator/cognitive_orchestrator.py`)
- **Pattern**: Composition and Dependency Injection.
- **Collaborators**:
  - `StimulusProcessor` (Layer 1)
  - `EmotionCore` (Layer 2)
  - `HomeostaticEngine` (Layer 3)
  - `ActiveInferenceEngine` (Layer 4)
  - `AffectiveMemory` & `EcphoryEngine` (Layer 5)
  - `PromptAssembler`, `LLMBackend`, `BoundaryLayer` (Layer 6)
  - `SurpriseModulationPolicy`, `PlasticityPolicy`, `GenerationPolicy`
  - `LNNTrainer` (Layer 4 Plasticity, optional)
- **Turn Method**: `process(input_text: str) -> CognitiveTurnResult`:
  - Enforces `self._turn_lock` (non-reentrant `threading.Lock`).
  - Executes the 10 stages in exact causal order.
  - Updates atomic reference `_latest_result: Optional[CognitiveTurnResult]`.
  - Guarantees **exactly one** `push_stimulus()` and **exactly one** `record_input()` call per turn.

### 3.2. Causal Active Inference Integration
- Generative prior before stimulus integration:
  $$\hat{p}_t = A \cdot p_{t-1} + b$$
- Prediction Surprise after limbic integration:
  $$\mathcal{S}_t = \|\hat{p}_t - p_t\|_2$$
- Analytic belief parameter adaptation:
  $$\Delta A = \eta (p_t - \hat{p}_t) p_{t-1}^T - \lambda (A - I)$$
  $$\Delta b = \eta (p_t - \hat{p}_t)$$
- Homeostatic modulation via `SurpriseModulationPolicy`:
  - $\text{CognitiveLoad} = \text{clip}(\text{base} + 0.35 \cdot \mathcal{S}_t, 0.0, 1.0)$
  - $\text{Tension} = \text{clip}(\text{base} + 0.25 \cdot (\mathcal{S}_t - 0.40), 0.0, 1.0)$
  - If $\mathcal{S}_t > 0.60$ or $\text{Tension} > 0.70 \implies \text{GenerationPolicy shifts to Deliberative Mode } (k=2)$.

### 3.3. Two-Stage LNN Plasticity Model (`PlasticityPolicy`)
- **Turn Time**: Fast online tagging ($< 0.1\text{ms}$). Compute $\text{Salience} = 0.6 \cdot \mathcal{S}_t + 0.4 \cdot \|p_t - p_{\text{philia}}\|_2$. If $\text{Salience} > \text{threshold}$, push tuple $(x_t, h_{t-1}, h_t, \text{Salience})$ to consolidation buffer.
- **Idle Time**: Background worker runs during idle rest ($T_{\text{idle}} \ge 45\text{s}$) or when buffer reaches overflow threshold. Runs `torchdiffeq.odeint` on CPU with AdamW, clips gradient norm to 1.0, and executes atomic weight swap under `_train_lock` ($\le 2\text{ms}$).

### 3.4. Backend Server Concurrency & Serialization (`src/api/server.py`)
- Instantiates `CognitiveOrchestrator` directly from configuration.
- Protects `POST /process` with `_turn_lock = asyncio.Lock()` with queue depth bounded to 1 (HTTP 429 for excess requests).
- Dispatches blocking execution to thread pool via `await loop.run_in_executor(None, orch.process, req.input)`.
- Returns cognitive payload:
  ```json
  {
    "response": "...",
    "call_id": "...",
    "pad": { "pleasure": 0.25, "arousal": -0.04, "dominance": 0.05 },
    "somatic": { "stability": 0.96, "cognitive_load": 0.12, "energy": 0.85, "tension": 0.04 },
    "surprise": 0.082
  }
  ```
- `GET /state` reads directly from `EmotionCore._state_lock` and the atomic reference `CognitiveOrchestrator.latest_result` without blocking on the turn lock ($\le 10\text{ms}$ response time).

### 3.5. Electron Body IPC Remediation (`electron/`)
- In `electron/preload/preload.js`: Expose complete API:
  - `window.lucia.chat.send(text)`
  - `window.lucia.chat.getHistory(limit)`
  - `window.lucia.voice.synthesize(text, pad)`
  - `window.lucia.voice.transcribe(audioBlob)`
  - `window.lucia.voice.getModels()`
  - `window.lucia.voice.selectModel(modelName)`
  - `window.lucia.system.getProfile()`
  - `window.lucia.system.setProfile(profile)`
  - `window.lucia.system.getHardwareProfile()`
  - `window.lucia.system.setHardwareProfile(tier)`
  - `window.lucia.models.getAvatars()`
- In `electron/main/ipc-bridge.js`: Implement main process proxy handlers for dynamic port routing.
- In `electron/renderer/chat/chat.js`: Replace all 12 direct `fetch()` calls with their corresponding `window.lucia.*` invocations.

---

## 4. Phase 9 Implementation Roadmap

```
Phase 9 Implementation Steps
├── Step 1: CognitiveOrchestrator & Layer 4 Causal Wiring (Python Core)
│   ├── 1.1 Create src/core/orchestrator/cognitive_orchestrator.py
│   ├── 1.2 Implement CognitiveTurnResult and Policy data classes
│   ├── 1.3 Wire Active Inference surprise into HomeostaticEngine
│   ├── 1.4 Refactor LNNTrainer to support idle-time consolidation
│   └── 1.5 Add unit tests in tests/unit/test_cognitive_orchestrator.py
├── Step 2: Backend Server Convergence (server.py)
│   ├── 2.1 Replace InstrumentedOrchestrator with CognitiveOrchestrator
│   ├── 2.2 Add asyncio.Lock turn mutex with HTTP 429 rejection to POST /process
│   ├── 2.3 Expose surprise and telemetry in /process and /state
│   └── 2.4 Add concurrency tests in tests/integration/test_turn_concurrency.py
├── Step 3: Simulation Cognitive Harness
│   ├── 3.1 Integrate CognitiveOrchestrator validation harness in SimulationRuntime
│   └── 3.2 Add tests in tests/unit/test_simulation_cognitive_turn.py
├── Step 4: Electron Brain ↔ Body IPC Mediation
│   ├── 4.1 Register missing IPC handlers in electron/main/ipc-bridge.js
│   ├── 4.2 Expose typed methods in electron/preload/preload.js
│   ├── 4.3 Migrate all 12 fetch calls in electron/renderer/chat/chat.js
│   └── 4.4 Verify with npm test in electron/
└── Step 5: Verification & Regression Gate
    ├── 5.1 Run full Python test suite (Unit, Property, Integration)
    ├── 5.2 Run Electron test suite
    └── 5.3 Verify zero direct fetch() calls in renderer
```

---

## 5. Non-Goals

- **NO Visual Redesign**: Personal Digital Room layout and Avatar stage remain visually unchanged.
- **NO Cloud Dependencies**: 100% local edge execution remains invariant.
- **NO Synchronous Voice Coupling in `/process`**: Voice remains in the decoupled Expression pipeline.
- **NO Multi-Persona / Character Switching**: Single continuous companion ontology preserved.
- **NO Agentic Desktop Automation**: Desktop clicking/typing remains out of scope.
