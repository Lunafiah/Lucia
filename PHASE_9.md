# PHASE_9.md — Unified Cognitive Architecture Specification

> **Authoritative Phase 9 Specification: Unified Cognitive Orchestrator, Causal Active Inference, Decoupled Voice Expression, and Complete IPC Mediation**  
> **Status**: APPROVED AT ARCHITECTURE GATE (Implementation Pending Sign-Off)  
> **Architecture Gate Reference**: [`PHASE_9_ARCHITECTURE_GATE.md`](file:///c:/Users/Lunafiah/Desktop/My_project/Lucia/PHASE_9_ARCHITECTURE_GATE.md)  
> **Baseline Review**: [`PHASE_8_ARCHITECTURE_REVIEW.md`](file:///c:/Users/Lunafiah/Desktop/My_project/Lucia/PHASE_8_ARCHITECTURE_REVIEW.md)  
> **Target Milestone**: Phase 9 (System Convergence & Cognitive Unification)

---

## 1. Executive Summary & Core Objective

The objective of **Phase 9** is **Cognitive Unification & Architectural Convergence**.

During the Phase 9 Architectural Decision Gate, the theoretical Russian-doll inheritance model (`UnifiedPresenceOrchestrator`) was formally rejected. In its place, Phase 9 establishes a **clean, composition-based cognitive architecture** that resolves all architectural findings from Phase 8:

1. **Unified Cognitive Orchestrator (`CognitiveOrchestrator`)**: Deprecates the fragile 5-tier inheritance ladder (`Orchestrator` $\rightarrow$ `MemoryAugmentedOrchestrator` $\rightarrow$ `InferencePipelineOrchestrator` $\rightarrow$ `PresenceOrchestrator` + `InstrumentedOrchestrator`). Implements a single, cohesive orchestrator composing Layers 1–6 in a linear, non-redundant execution flow.
2. **Causal Active Inference (Layer 4 Integration)**: Integrates `ActiveInferenceEngine` into every live turn. Evaluates pre-stimulus prediction expectations, measures Prediction Surprise $\mathcal{S}_t = \|A \cdot p_{t-1} + b - p_t\|_2$, and causally modulates Homeostatic Cognitive Load, Tension, and Reasoning Depth ($k=2$ when $\mathcal{S}_t > 0.60$).
3. **Decoupled Expression Pipeline for Voice**: Voice synthesis remains an independent multimodal expression service triggered asynchronously by the Body UI via IPC. It is decoupled from the synchronous cognitive return, guaranteeing zero text latency, complete failure isolation, and zero compute waste when muted.
4. **Two-Stage LNN Plasticity**: Replaces arbitrary "every 16 turns" batch training with online salience tagging during turns and offline consolidation on CPU during idle rest periods ($T_{\text{idle}} \ge 45\text{s}$) or salience threshold overflows.
5. **Strict Serialized Cognitive Turns**: Enforces an asynchronous turn mutex (`asyncio.Lock()`) in `server.py` and a threading lock in `CognitiveOrchestrator` to prevent concurrent turn corruption.
6. **Complete Brain ↔ Body IPC Remediation**: Eliminates all 12 direct `fetch()` calls in `chat.js`, routing all voice, history, profile, and asset queries through `window.lucia.*` via `preload.js` and `ipc-bridge.js`.

---

## 2. Canonical Cognitive Turn Flow

```mermaid
flowchart TD
    UserMsg([User Input Text]) --> L1[Layer 1: StimulusProcessor]
    L1 -->|16D Stimulus Vector x| L4a[Layer 4a: Active Inference Prediction]
    L4a -->|Expected p̂| L2[Layer 2: Limbic ODE solve_ivp]
    L2 -->|Observed PAD p_t| L4b[Layer 4b: Active Inference Surprise]
    L4b -->|Surprise S & Belief Update| L3[Layer 3: Homeostatic Engine]
    L3 -->|Somatic Markers & Constraints [k, temp, latency]| L5a[Layer 5a: Ecphory Query]
    L5a -->|Subconscious Echo Vector| L6a[Layer 6a: Prompt Assembler]
    L6a -->|Conditioned Prompt| L6b[Layer 6b: Local SLM Generate]
    L6b -->|Raw Text| L6c[Layer 6c: BoundaryLayer Filter]
    L6c -->|Safe Response| MemoryStore[Layer 5b: SDM Trace Store with Surprise Salience]
    MemoryStore --> HistAppend[Append Working History Pair]
    HistAppend --> PlasticityTag[Layer 4c: Tag Salient Experience for Idle Consolidation]
    PlasticityTag --> TurnReturn([Return Text + PAD + Somatic Snapshot])
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
  - `LNNTrainer` (Layer 4 Plasticity, optional)
- **Turn Method**: `process(input_text: str) -> TurnResult`:
  - Enforces `self._turn_lock`.
  - Executes the 10 stages in exact causal order.
  - Updates direct telemetry properties: `last_somatic`, `last_constraints`, `last_pred_error`, `last_echo_resonance`.
  - Guarantees **exactly one** `push_stimulus()` and **exactly one** `record_input()` call per turn.

### 3.2. Causal Active Inference Integration
- Before pushing stimulus:
  $$\hat{p} = A \cdot p_{\text{before}} + b$$
- After ODE integration:
  $$\mathcal{S} = \|A \cdot p_{\text{before}} + b - p_{\text{after}}\|_2$$
- Update belief state:
  $$\Delta A = -2\eta (\hat{p} - p_{\text{after}}) p_{\text{before}}^T - 2\eta \lambda_{KL} (A - I)$$
  $$\Delta b = -2\eta (\hat{p} - p_{\text{after}})$$
- Somatic Modulation:
  - $\text{CognitiveLoad} = \text{clip}(\text{base} + 0.35 \cdot \mathcal{S}, 0.0, 1.0)$
  - $\text{Tension} = \text{clip}(\text{base} + 0.25 \cdot \mathcal{S}, 0.0, 1.0)$
  - If $\mathcal{S} > 0.60$ or $\text{Tension} > 0.70 \implies \text{reasoning\_depth} = 2$.
  - $\Delta T = +0.05 \cdot \mathcal{S}$.

### 3.3. Two-Stage LNN Plasticity Model
- **Turn Time**: Fast online tagging. Compute $\text{Salience} = 0.6 \cdot \mathcal{S} + 0.4 \cdot \|PAD - PAD_{\text{philia}}\|_2$. If $\text{Salience} > 0.35$, push tuple $(x, h_{\text{before}}, h_{\text{after}}, \text{Salience})$ to consolidation buffer.
- **Idle Time**: Background worker runs when $T_{\text{idle}} \ge 45\text{s}$ and buffer count $\ge 4$, or if buffer reaches 8 samples. Runs `torchdiffeq.odeint` on CPU with AdamW, clips gradient norm to 1.0, and executes atomic weight swap under `_train_lock` ($\le 2\text{ms}$).

### 3.4. Backend Server Concurrency & Serialization (`src/api/server.py`)
- Instantiates `CognitiveOrchestrator` directly from configuration.
- Protects `POST /process` with `_turn_lock = asyncio.Lock()`.
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
- `GET /state` reads directly from `_emotion_core` and `CognitiveOrchestrator` properties under `_state_lock` without blocking on the turn lock ($\le 10\text{ms}$ response time).

### 3.5. Electron Body IPC Remediation (`electron/`)
- In `electron/preload/preload.js`: Expose complete API:
  - `window.lucia.chat.send(text)`
  - `window.lucia.chat.getHistory()`
  - `window.lucia.voice.synthesize(text, pad)`
  - `window.lucia.voice.transcribe(audioBlob)`
  - `window.lucia.voice.getModels()`
  - `window.lucia.voice.selectModel(modelName)`
  - `window.lucia.system.getProfile()`
  - `window.lucia.system.setProfile(profile)`
  - `window.lucia.models.getAvatars()`
- In `electron/main/ipc-bridge.js`: Implement main process proxy handlers for dynamic port routing.
- In `electron/renderer/chat/chat.js`: Replace all 12 direct `fetch()` calls with their corresponding `window.lucia.*` invocations.

---

## 4. Phase 9 Implementation Roadmap

```
Phase 9 Implementation Steps
├── Step 1: CognitiveOrchestrator & Layer 4 Causal Wiring (Python Core)
│   ├── 1.1 Create src/core/orchestrator/cognitive_orchestrator.py
│   ├── 1.2 Wire Active Inference surprise into HomeostaticEngine
│   ├── 1.3 Refactor LNNTrainer to support idle-time consolidation
│   └── 1.4 Add unit tests in tests/unit/test_cognitive_orchestrator.py
├── Step 2: Backend Server Convergence (server.py)
│   ├── 2.1 Replace InstrumentedOrchestrator with CognitiveOrchestrator
│   ├── 2.2 Add asyncio.Lock turn mutex to POST /process
│   ├── 2.3 Expose surprise and telemetry in /process and /state
│   └── 2.4 Add concurrency tests in tests/integration/test_turn_concurrency.py
├── Step 3: Electron Brain ↔ Body IPC Mediation
│   ├── 3.1 Register missing IPC handlers in electron/main/ipc-bridge.js
│   ├── 3.2 Expose typed methods in electron/preload/preload.js
│   ├── 3.3 Migrate all 12 fetch calls in electron/renderer/chat/chat.js
│   └── 3.4 Verify with npm test in electron/
└── Step 4: Verification & Regression Gate
    ├── 4.1 Run full Python test suite (Unit, Property, Integration)
    ├── 4.2 Run Electron test suite
    └── 4.3 Verify zero direct fetch() calls in renderer
```

---

## 5. Non-Goals

- **NO Visual Redesign**: Personal Digital Room layout and Avatar stage remain visually unchanged.
- **NO Cloud Dependencies**: 100% local edge execution remains invariant.
- **NO Synchronous Voice Coupling in `/process`**: Voice remains in the decoupled Expression pipeline.
- **NO Multi-Persona / Character Switching**: Single continuous companion ontology preserved.
