# PHASE_9.md — Cognitive Unification & System Convergence Specification

> **Authoritative Phase 9 Specification: Unifying the 6-Layer Cognitive Pipeline, Completing Brain ↔ Body IPC Mediation, and Hardening Concurrency**  
> **Status**: APPROVED ARCHITECTURAL SPECIFICATION (Implementation Pending)  
> **Baseline Review**: [`PHASE_8_ARCHITECTURE_REVIEW.md`](file:///c:/Users/Lunafiah/Desktop/My_project/Lucia/PHASE_8_ARCHITECTURE_REVIEW.md)  
> **Target Release**: Phase 9 Milestone

---

## 1. Phase 9 Objective

The objective of **Phase 9** is **Cognitive Unification & System Convergence**.

Phase 9 does not add speculative end-user features (such as vision models or external agent toolbars). Instead, Phase 9 resolves the architectural debts identified in the Post-Phase-8 Architecture Review by:
1. Connecting the complete 6-layer cognitive pipeline into the live production turn loop (`server.py`), activating **Active Inference Free Energy Minimization** and **Online CPU LNN Plasticity** (Layer 4).
2. Eliminating redundant stimulus pushes and homeostatic double-recordings in `InstrumentedOrchestrator`.
3. Completing the **Brain ↔ Body IPC Bridge**, migrating all remaining direct `fetch()` calls in `chat.js` to secure `window.lucia` IPC channels with dynamic port resilience.
4. Implementing turn-level concurrency protection for dialogue history and inference pipelines.

---

## 2. Architectural Motivation

During Phases 1 through 8, subsystems were developed and validated in milestone increments:
- Phase 2 created `MemoryAugmentedOrchestrator` (SDM + Ecphory + Decay).
- Phase 4 created `InferencePipelineOrchestrator` (Active Inference + LNN Plasticity).
- Phase 5 created `PresenceOrchestrator` (coupling VoiceEngine to the cognitive pipeline).
- Phase 8 created `SimulationRuntime` and `SimClock`.

However, `src/api/server.py` remained frozen on `InstrumentedOrchestrator` (inheriting directly from Phase 2's `MemoryAugmentedOrchestrator`). As a result, the live companion in production has been executing without Layer 4 active inference or CPU plasticity, while voice synthesis remained an out-of-band asynchronous client request.

Phase 9 converges these separated modules into a single, unified, production-grade cognitive presence.

---

## 3. Problems Inherited from Phase 8

As documented in `PHASE_8_ARCHITECTURE_REVIEW.md`, Phase 9 inherits four specific structural defects:

1. **Layer 4 Cognitive Bypassing (Critical)**:
   - `ActiveInferenceEngine` and `LNNTrainer` are fully tested in unit suites but completely bypassed in `POST /process` live turns because `server.py` does not instantiate `InferencePipelineOrchestrator`.
2. **Double Homeostatic Accounting (High)**:
   - `InstrumentedOrchestrator._execute_pipeline()` in `server.py` calls `push_stimulus()` and `record_input()` to capture telemetry, and then delegates to `super()._execute_pipeline()`, which calls both methods a second time. This causes metabolic energy to deplete at $2\times$ the specified rate.
3. **Brain ↔ Body IPC Incompleteness (Medium)**:
   - Eight auxiliary endpoints in `electron/renderer/chat/chat.js` (`/voice/synthesize`, `/profile`, `/history`, `/system/profile`, etc.) still make unmediated `window.fetch()` calls to `127.0.0.1:8765`, violating process isolation and breaking if the backend port changes.
4. **Unprotected Turn Concurrency (High)**:
   - `Orchestrator.process()` mutates `self._history` and sub-module buffers without a pipeline execution mutex, creating race-condition vulnerabilities if multiple requests arrive concurrently.

---

## 4. Approved Architectural Direction

Phase 9 establishes the following architectural solutions:

```
┌────────────────────────────────────────────────────────────────────────────────────────┐
│                          PHASE 9 CONVERGED ARCHITECTURE                                │
│                                                                                        │
│   FastAPI Server (server.py)                                                           │
│   └── UnifiedPresenceOrchestrator                                                      │
│       └── PresenceOrchestrator (Phase 5 VoiceEngine coupling)                          │
│           └── InferencePipelineOrchestrator (Phase 4 Active Inference & LNN Plasticity)│
│               └── MemoryAugmentedOrchestrator (Phase 2 SDM, Ecphory & Decay)           │
│                   └── Base Orchestrator (Phase 1 Gating, ODE, Homeostasis, LLM)        │
│                                                                                        │
│   Execution Guarantees:                                                                │
│   • Single-pass stimulus encoding and homeostatic accounting per turn.                 │
│   • Asynchronous turn-level queue/mutex protecting conversation history and state.     │
│   • Real-time Active Inference surprise calculation recorded in StabilityEvaluator.   │
│   • 100% IPC mediation via window.lucia bridge; zero raw fetch() in renderer.         │
│   • Dynamic port negotiation between ProcessManager and Renderer.                      │
└────────────────────────────────────────────────────────────────────────────────────────┘
```

1. **Unified Orchestration Hierarchy**:
   - Create `UnifiedPresenceOrchestrator` in `src/core/orchestrator/unified_orchestrator.py` (or promote `src/core/presence/orchestrator.py`), ensuring that `server.py` runs the entire 10-step cognitive pipeline (Sensors $\rightarrow$ Limbic ODE $\rightarrow$ Somatic Budgeting $\rightarrow$ Active Inference $\rightarrow$ Memory Echo $\rightarrow$ Prompt Assembly $\rightarrow$ LLM $\rightarrow$ Boundary Filter $\rightarrow$ SDM Store $\rightarrow$ LNN Experience Buffer).
2. **Surgical Telemetry Tap**:
   - Rather than re-executing steps 1-4, telemetry snapshotting (`_last_somatic`, `_last_constraints`) will be tapped via pipeline callbacks or hook bus events (`on_somatic_updated`).
3. **Complete IPC Channel Coverage**:
   - Implement Electron main handlers for:
     `voice:synthesize`, `voice:transcribe`, `voice:models`, `voice:select-model`, `profile:get`, `profile:set`, `history:get`, `models:avatar:get`.
   - Update `chat.js` to call exclusively `window.lucia.*`.

---

## 5. Scope

### Phase 9.1: Cognitive Pipeline Convergence
- [ ] Implement `UnifiedPresenceOrchestrator` inheriting from `InferencePipelineOrchestrator` and composing `VoiceEngine`.
- [ ] Connect Active Inference belief state ($A, b$) and prediction surprise to the live turn cycle.
- [ ] Enqueue experience tuples into `LNNTrainer` ring buffer during live turns for background CPU plasticity.
- [ ] Fix double-stimulus and double-homeostatic execution in `server.py`.
- [ ] Add turn-level concurrency lock (`asyncio.Lock`) in `server.py` wrapping turn processing.

### Phase 9.2: Complete IPC Mediation & Port Resilience
- [ ] Implement missing IPC channels in `electron/main/ipc-bridge.js`:
  - `voice:synthesize`
  - `voice:transcribe`
  - `voice:get-models`
  - `voice:select-model`
  - `profile:get`
  - `profile:set`
  - `history:get`
  - `models:avatar:get`
- [ ] Expose all new channels cleanly via `electron/preload/preload.js` under `window.lucia`.
- [ ] Refactor `electron/renderer/chat/chat.js` to eliminate all 8 remaining direct `fetch()` calls.
- [ ] Implement dynamic port handoff from `process-manager.js` to `ipc-bridge.js` and renderer.

### Phase 9.3: Stability & Telemetry Integration
- [ ] Feed Active Inference prediction surprise directly into `StabilityEvaluator.record_surprise()`.
- [ ] Update `GET /telemetry/stability` and `GET /state` to reflect live active inference metrics.
- [ ] Expose active inference surprise and LNN trainer batch progress in the Diagnostics modal.

### Phase 9.4: Verification & Regression Testing
- [ ] Write integration test verifying that `POST /process` updates Active Inference belief matrix $A$.
- [ ] Write integration test verifying that `POST /process` enqueues tuples to `LNNTrainer`.
- [ ] Write test verifying energy depletes by exactly $0.05$ on a single turn (confirming double-depletion fix).
- [ ] Write Jest tests verifying zero direct `fetch()` calls in `chat.js` and full IPC coverage.
- [ ] Re-run full test suite ensuring $\ge 604$ tests pass without regression.

---

## 6. Non-Goals

The following items are explicitly out of scope for Phase 9:
- **No Desktop Vision / Screen Reading (VLM)**: ReAct desktop automation and Qwen2.5-VL screen reading remain deferred (Phase 10+).
- **No Cloud API Integrations**: Zero cloud dependencies invariant remains absolute (100% local edge execution).
- **No Persona Switchers**: Single Continuous Life ontology remains invariant; avatars are Appearance only.
- **No Introspective LLM Prompts**: Strict boundary layer invariants against self-reported affect remain absolute.
- **No Production Code Refactoring of Solvers**: Core ODE equations (`solve_ivp` RK45) and SDM Hamming mathematics remain unchanged.

---

## 7. Dependencies

- Python 3.10+ / 3.12+ virtual environment with `torch`, `torchdiffeq`, `scipy`, `numpy`, `fastapi`, `uvicorn`.
- Electron 33+ desktop runtime with `jest` testing framework.
- Pre-existing verified test suite: 450 Python unit/integration tests + 35 property tests + 119 Jest tests.

---

## 8. Implementation Sequence

```
Step 1: Cognitive Pipeline Unification (Python Core)
  ├── 1.1 Create UnifiedPresenceOrchestrator in src/core/orchestrator/
  ├── 1.2 Eliminate double-execution bug in InstrumentedOrchestrator
  ├── 1.3 Wire Active Inference & LNNTrainer into server.py
  └── 1.4 Add turn-level concurrency mutex

Step 2: Stability & Telemetry Fusion
  ├── 2.1 Connect Active Inference surprise to StabilityEvaluator
  └── 2.2 Expose Layer 4 metrics in GET /state and GET /telemetry/stability

Step 3: Brain ↔ Body IPC Bridge Completion (Electron)
  ├── 3.1 Add IPC handlers in electron/main/ipc-bridge.js
  ├── 3.2 Expose IPC bridge in electron/preload/preload.js
  └── 3.3 Migrate electron/renderer/chat/chat.js to eliminate all fetch() calls

Step 4: Comprehensive Validation
  ├── 4.1 Execute new unit and integration tests for Layer 4 live turn integration
  ├── 4.2 Execute Jest tests for IPC bridge and chat.js fetch elimination
  └── 4.3 Full regression run across Python, Property, and Jest suites
```

---

## 9. Validation Requirements

To be accepted, Phase 9 implementation must satisfy the following automated validation criteria:

1. **VAL-1: Active Inference Live Verification**:
   - A test must execute 5 conversational turns via `POST /process` and assert that the generative transition model matrix $A$ in `ActiveInferenceEngine` has shifted from its initial identity state ($A \neq I_3$).
2. **VAL-2: Single Energy Depletion Verification**:
   - A test must call `POST /process` with an initial energy of $1.0$ and assert that post-turn energy is exactly $0.95 \pm 0.001$ (confirming the fix for the double-depletion bug R-02).
3. **VAL-3: LNN Plasticity Enqueue Verification**:
   - A test must assert that after 16 conversational turns via `POST /process`, `LNNTrainer` has accumulated a batch of 16 experience tuples.
4. **VAL-4: Zero Direct Fetch in Renderer**:
   - A static analysis / Jest test must assert that `grep -n "fetch(" electron/renderer/chat/chat.js` returns zero matches outside comments.
5. **VAL-5: Zero Regression Baseline**:
   - All 450 existing Python unit/integration tests, 35 property tests, and 119 Jest tests must pass.

---

## 10. Acceptance Criteria

| Criteria ID | Target Requirement | Acceptance Condition |
|---|---|---|
| **AC-01** | Layer 4 Live Integration | `POST /process` updates Active Inference belief state and records Free Energy surprise. |
| **AC-02** | Energy Depletion Fidelity | Energy decreases by exactly $0.05$ per turn without duplicate stimulus processing. |
| **AC-03** | Turn Concurrency Safety | Concurrent requests to `POST /process` are serialized safely without history corruption. |
| **AC-04** | Complete IPC Mediation | 100% of renderer communication with backend is routed via `window.lucia` IPC channels. |
| **AC-05** | Test Suite Health | 100% test pass rate across all suites ($\ge 610$ total automated tests). |
| **AC-06** | Invariant Preservation | All AGENTS.md invariants (No introspection, One Continuous Life, 0 cloud keys) preserved. |

---

## 11. Deferred Work

The following items are explicitly deferred to Phase 10 and beyond:
1. **Multimodal Visual Perception**: Screen capture, VLM grounding, and visual environmental awareness.
2. **Long-Term Episodic Knowledge Graph**: Structured relational entity consolidation beyond SDM 64-dim content vectors.
3. **Sleep-Wake Decay Consolidation**: Deep offline memory consolidation algorithms executing during system idle/sleep states.
