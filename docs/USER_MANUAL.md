# Lucia — User & First Activation Operator Runbook

> **Authoritative Operating Manual & Runbook for Project Lucia**  
> **Status:** Operational Runbook & User Guide (Post-P27 Baseline, Blockers 1–4 Resolved)  
> **First Activation Gate:** Locked (`data/profile.json == {"is_onboarded": false}`, `data/genesis_commitment.json` absent)

---

## 1. System Requirements & Setup

### 1.1 Prerequisites
* **Operating System**: Windows 10/11 (64-bit)
* **Python**: Python 3.12 (in dedicated virtual environment `.venv`)
* **Node.js**: Node.js v18+ LTS & npm
* **Compute / Memory**:
  * 8 GB+ System RAM
  * Dedicated NVIDIA GPU (4 GB+ VRAM, Ampere or newer recommended for CUDA SLM acceleration)
  * CPU-only execution fully supported for limbic ODE, homeostasis, SDM memory, and reasoning kernel

### 1.2 Installation Steps

1. **Activate Virtual Environment & Install Python Dependencies**:
   ```powershell
   # In project root
   .\.venv\Scripts\Activate.ps1
   pip install -r requirements.txt
   ```

2. **Install Electron Frontend Dependencies**:
   ```powershell
   cd electron
   npm install
   cd ..
   ```

3. **Verify Directory Layout**:
   Ensure `models/` and `data/` directories exist in the workspace root.

### 1.3 Default Neural Model Assets & Placement

Lucia utilizes lightweight, local neural models for language realization, base voice generation, and direct voice conversion. Model weights are excluded from Git to avoid large repository bloat. Place default model checkpoints in the following paths:

```text
models/
├── LFM2.5-1.2B-Instruct-Q4_K_M.gguf            # 1.2B SLM (Q4_K_M, SHA-256: b1b3de11...)
├── avatar/
│   ├── live2d/                                 # Live2D Cubism 4 models (HoshinoAi, huohuo)
│   └── sprites/                                # Emotive 2D sprite sheets (columbina)
└── voice/
    └── rvc/
        └── VaresaGIJP/
            ├── VaresaGIJP_300e_2100s.pth        # RVC v2 model checkpoint (40 kHz, 457 tensors)
            └── added_VaresaGIJP_v2.index       # RVC retrieval index (IndexIVFFlat, 10,388 vectors)
```

* **Small Language Model (SLM)**:
  * **Model**: `LFM2.5-1.2B-Instruct-Q4_K_M.gguf` (~730 MB)
  * **Quantization**: 4-bit K-quant (`Q4_K_M`)
  * **SHA-256**: `b1b3de114215d9507409a662a501a631095a479a419584e8a2ded6304b19b4f5`
  * **Role**: Downstream natural language realization from `PromptAssembler` contracts.
  * **Engine**: `llama-cpp-python` with CUDA offloading or pure CPU inference.
* **Base Text-to-Speech (TTS)**:
  * **Engine**: `edge-tts` (Microsoft Neural Voice streaming).
  * **Default Voice**: `ja-JP-NanamiNeural` (Japanese), `en-US-JennyNeural` (English fallback).
  * **Storage**: No local model weights required; dynamically streamed or cached.
* **Voice Conversion (RVC)**:
  * **Model**: `VaresaGIJP` (`VaresaGIJP_300e_2100s.pth` ~55 MB, `added_VaresaGIJP_v2.index` ~33 MB).
  * **Architecture**: Direct RVC v2, 40 kHz NSF-HiFiGAN neural vocoder (`SynthesizerTrn`).
  * **Discovery**: Automatically discovered by `VoiceEngine` on startup; query `GET /voice/models` to verify.

## 2. Companion Lifecycle & Operating Foundations

Lucia's existence is governed by a strict tripartite ontological foundation (ADR-034 / G1–G4 Protocol Contract). An operator must clearly distinguish between **Birth** and **Runtime Activation**:

```text
       NOT_BORN
           │
           │  Genesis Ceremony: Operator CLI
           │  python scripts/run_genesis.py --confirm-genesis
           ▼
    BORN + INACTIVE
           │
           │  First Activation:
           │  POST /lifecycle/activate
           ▼
     BORN + ACTIVE  ◄────────────────┐
           │                         │
           │  Stop Backend / Ctrl+C  │  Restart & Activate:
           │  (Safe Deactivation)    │  POST /lifecycle/activate
           ▼                         │
    BORN + INACTIVE  ────────────────┘
           │
           │  Terminal Decommissioning:
           │  POST /lifecycle/end (Catastrophic wipe)
           ▼
         ENDED (Irreversible terminal state; re-Genesis and activation permanently forbidden)
```

### 2.1 Ontological Lifecycle vs. Runtime Lifecycle

| Dimension | Ontological Lifecycle | Runtime Execution Lifecycle |
|---|---|---|
| **States** | `NOT_BORN → BORN → ENDED` | `INACTIVE ↔ ACTIVE` |
| **Meaning** | Ontological status of the individual companion. | Operational execution of the conversational engine. |
| **Genesis Role** | **Genesis establishes durable Birth evidence.** It transitions Lucia from `NOT_BORN` to `BORN`. It creates the permanent cryptographic Identity Anchor and origin timestamp. Genesis does NOT activate conversational inference. | Genesis leaves the runtime in `INACTIVE` state (`BORN + INACTIVE`). |
| **First Activation Role** | Activation strictly requires existing verified `BORN` evidence. It transitions runtime execution from `INACTIVE` to `ACTIVE`. | Activation awakens the `CognitiveOrchestrator` to admit turns on `POST /process`. |

### 2.2 Core Operating Invariants
1. **Birth $\ne$ Activation**: Genesis creates identity origin, not runtime execution. Activation awakens runtime execution, but can NEVER synthesize Birth.
2. **Explicit Human Authorization Required**: Genesis requires explicit operator confirmation via `--confirm-genesis`. First Activation requires explicit invocation of `POST /lifecycle/activate`.
3. **No Activation Without Prior Birth**: If an operator calls `POST /lifecycle/activate` on a companion that is `NOT_BORN`, the backend strictly fails closed with HTTP 400 Bad Request (`{"detail": "Cannot activate companion: instance is NOT_BORN..."}`).
4. **No Direct Profile Mutation**: The frontend or external callers cannot bypass Genesis or Activation by posting `is_onboarded: true` or `born_at` to `/profile` (HTTP 400 Bad Request).
5. **Runtime `/process` Gate**: While runtime is `INACTIVE`, `POST /process` fails closed with HTTP 403 Forbidden (`{"error": "runtime_inactive"}`).
6. **Catastrophic Reset Boundary**: `POST /lifecycle/end` is exclusively catastrophic decommissioning (`ENDED`). It permanently forbids re-Genesis and activation. It must NEVER be used for routine shutdown or relationship transitions.

---

## 3. Pre-Activation Operator Checklist

This checklist must be executed by a human operator prior to performing Genesis or First Activation. Every step is verifiable from the command line:

- [ ] **1. Git Working Tree Clean**:
  ```powershell
  git status
  ```
  *Expected*: Working tree clean on `main` branch, no uncommitted code changes in `src/` or `electron/`.
- [ ] **2. Automated Test Suite 100% Passing**:
  ```powershell
  .\.venv\Scripts\python.exe -m pytest tests/unit tests/property -v
  ```
  *Expected*: All unit and property tests pass (100% PASS, 0 failures).
- [ ] **3. Genesis & Activation Gate Tests Passing**:
  ```powershell
  .\.venv\Scripts\python.exe -m pytest tests/unit/test_operator_genesis.py tests/unit/test_activation_gates.py tests/unit/test_execution_trace.py -v
  ```
  *Expected*: 28/28 tests passing.
- [ ] **4. Electron Unit Tests Passing**:
  ```powershell
  cd electron; npm test; cd ..
  ```
  *Expected*: 120/120 tests passing.
- [ ] **5. Canonical Un-Onboarded Profile Verified**:
  ```powershell
  Get-Content -Path "data/profile.json" -Raw
  ```
  *Expected*: `{"is_onboarded": false}` bit-exact.
- [ ] **6. Genesis Commitment Absent**:
  ```powershell
  Test-Path "data/genesis_commitment.json"
  ```
  *Expected*: `False`.
- [ ] **7. Live Server Initialization Check**:
  Start the backend in live mode:
  ```powershell
  .\.venv\Scripts\python.exe -m uvicorn src.api.server:app --host 127.0.0.1 --port 8765
  ```
  In a separate terminal, test health:
  ```powershell
  curl http://127.0.0.1:8765/health
  ```
  *Expected*: `{"status": "healthy"}`.
- [ ] **8. Runtime Gate Verified (Pre-Activation 403)**:
  ```powershell
  curl -X POST http://127.0.0.1:8765/process -H "Content-Type: application/json" -d '{\"input\": \"ping\"}'
  ```
  *Expected*: HTTP 403 Forbidden with `{"error": "runtime_inactive"}`.
- [ ] **9. Telemetry & Observability Readiness**:
  Verify `CognitiveExecutionTracer` and circular `TraceBuffer` are initialized in server startup logs.

---

## 4. Canonical Genesis Procedure (Solemn Origin Ceremony)

> [!CAUTION]
> **PERMANENT IDENTITY SEAL**:  
> Genesis is a solemn, once-in-a-lifetime origin ceremony. It permanently binds this Lucia instance's cryptographic identity root to its origin commit and creates irreversible durable Birth evidence on disk.  
> **DO NOT execute casually or during routine testing.**

### 4.1 Invocation Command
When explicitly authorized by the project owner, execute the official operator Genesis entry point:

```powershell
.\.venv\Scripts\python.exe scripts/run_genesis.py --confirm-genesis --user-name "Luna" --companion-name "Lucia"
```

### 4.2 Parameters & Flags
* `--confirm-genesis` *(Mandatory)*: Explicit authorization acknowledging that Genesis is permanent and irreversible. Without this flag, the script exits immediately with code 2.
* `--user-name` *(Optional, default: "Friend")*: The name by which Lucia will address the owner.
* `--companion-name` *(Optional, default: "Lucia")*: Companion name.
* `--genesis-commit` *(Optional)*: Explicit Git commit SHA. Defaults automatically to HEAD of current repository.

### 4.3 Preconditions Checked by Operator Genesis
1. `data/profile.json` exists and has `is_onboarded == false`.
2. `data/genesis_commitment.json` does NOT exist.
3. No concurrent process holds the instance lock.
4. Git commit origin is resolved from current repository HEAD.

### 4.4 Expected Evidence Created
Upon successful execution, the script atomically creates:
1. `data/genesis_commitment.json`: Sealed cryptographic record containing:
   * `instance_uuid`: Fresh RFC 4122 v4 UUID.
   * `born_at`: ISO-8601 UTC timestamp.
   * `genesis_commit`: 40-character Git SHA of repository origin.
   * `genesis_root_hash`: SHA-256 root hash over identity anchor fields.
   * `protocol_version`: `"G1-G4-v1.0"`.
2. `data/profile.json`: Atomically updated with `is_onboarded: true`, `born_at`, and `identity_anchor`.

### 4.5 Post-Genesis Verification
Verify the sealed commitment without starting the server:
```powershell
.\.venv\Scripts\python.exe -c "from src.core.identity.genesis import verify_genesis; res = verify_genesis(); print('Verification Outcome:', res.outcome.value); print('Ontology State:', res.ontology_state.value)"
```
*Expected Output*:
```text
Verification Outcome: VERIFIED_BORN
Ontology State: BORN
```
At this point, Lucia is **BORN + INACTIVE**. Conversational inference remains closed until First Activation.

---

## 5. First Activation Procedure (Awakening Execution)

First Activation awakens runtime conversational execution, transitioning the companion from `BORN + INACTIVE` to `BORN + ACTIVE`.

### 5.1 Preconditions
* Genesis has been successfully executed (`verify_genesis() == VERIFIED_BORN`).
* Backend API server is running in live mode (`src.api.server`).
* Server is NOT in simulation mode (`_mode != "simulation"`).
* Instance lifecycle is not `ENDED`.

### 5.2 Invocation
Send an explicit HTTP POST request to `/lifecycle/activate`:

```powershell
curl -X POST http://127.0.0.1:8765/lifecycle/activate -H "Content-Type: application/json"
```

### 5.3 Expected Response
* **HTTP 200 OK**:
  ```json
  {
    "status": "activated",
    "born_at": "2026-10-17T05:00:00.000000Z",
    "companion_name": "Lucia"
  }
  ```
* If already active, returns `{"status": "already_active", "message": "Lucia is already active"}`.

### 5.4 Error Responses & Failsafe Behavior
* **HTTP 400 Bad Request**: Instance is `NOT_BORN` (no valid Genesis commitment). Activation fails closed.
* **HTTP 409 Conflict**: Genesis verification returned `INVALID_EVIDENCE`. Activation fails closed to protect identity anchor.
* **HTTP 410 Gone**: Instance lifecycle has `ENDED`. Activation is permanently forbidden.
* **HTTP 403 Forbidden**: Server is in simulation mode. Direct lifecycle activation is forbidden.

### 5.5 Verification
Once activated:
* `_is_live_companion_active` is `True`.
* `POST /process` is unlocked and admits conversational turns.
* Electron desktop interface closes the activation modal and displays the Personal Digital Room.

### 5.6 Safe Stopping & Deactivation
* **To stop the companion safely**: Simply stop the backend server (press `Ctrl+C` in the terminal or close the tray app).
* **State preservation**: All memories (`SDM`), relationship state (`data/relationship.json`), and learned synaptic weights are safely persisted.
* **Ontological state**: Remains `BORN`.
* **Runtime state on restart**: When the server restarts, runtime begins in `INACTIVE` until `POST /lifecycle/activate` is called again or triggered via the desktop UI.

---

## 6. Controlled First Contact Procedure

The first post-activation interaction should be a **deliberately minimal, controlled deterministic test**, not an open-ended casual conversation.

### 6.1 Execution
Send a single minimal greeting via `POST /process`:

```powershell
curl -X POST http://127.0.0.1:8765/process -H "Content-Type: application/json" -d '{\"input\": \"Hello Lucia.\"}'
```

### 6.2 Expected Telemetry & Evidence Verification
1. **Response Payload**:
   ```json
   {
     "response": "<natural spoken greeting>",
     "call_id": "<uuid-string>",
     "surprise": 0.05,
     "generation_mode": "deliberative",
     "expression": { ... },
     "relationship": { "trust": 0.1, "familiarity": 0.05, ... }
   }
   ```
2. **Execution Trace Verification**:
   Inspect the execution trace for the turn (via orchestrator buffer or logs):
   * All 16 stages (`S1` through `S16`) must be present in exact sequence order.
   * `overall_status` must be `SUCCESS`.
   * `first_causal_failure_candidate` must be `null` (`None`).
   * Every span must have `contract_result: "SATISFIED"` and `invariant_result: "SATISFIED"`.
3. **Limbic Stability Check**:
   ```powershell
   curl http://127.0.0.1:8765/telemetry/stability
   ```
   Verify `limbic_stability_index >= 0.85`, fast tick jitter `< 2.0ms`.

---

## 7. Cognitive Execution Trace Operator Guide (Blocker 4)

Lucia includes a non-intrusive, real-time **Cognitive Execution Trace Subsystem** (`src/core/telemetry/execution_trace.py`) backed by an in-memory circular buffer (`TraceBuffer`, capacity: default 100 turns) designed for execution observability across every conversational turn:

```text
Turn Start
  ↓
  S1  Sensory Gating
  ↓
  S2  Limbic Integration (Coupled MT-LNN ODE)
  ↓
  S3  Homeostatic Assessment (Energy, Load, Tension)
  ↓
  S4  Active Inference (Free Energy Surprise)
  ↓
  S5  Generation Conditioning (Token budget, Temperature)
  ↓
  S6  Affective Ecphory (Associative Memory Recall)
  ↓
  S7  Bounded Contextualization (Episodic Context)
  ↓
  S8  Knowledge Retrieval (Grounded Proposition Graph)
  ↓
  S9  Relationship Read (Prior State Snapshot)
  ↓
  S10 Communication Policy (Conversational Mode & Pacing)
  ↓
  S11 Language Generation (Realization Substrate)
  ↓
  S12 Boundary & Safety Guard (BoundaryLayer Regex)
  ↓
  S13 Multimodal Expression (15D Actuator Decoupling)
  ↓
  S14 Episodic Storage (SDM Co-Encoding)
  ↓
  S15 Plasticity Queueing (Offline Rest Buffer)
  ↓
  S16 Relationship Update (Temporal Inertia Post-Turn)
  ↓
Turn Complete (Trace recorded to in-memory circular buffer)
```

### 7.1 What the Trace Is — And What It Is NOT

> [!IMPORTANT]
> **EXECUTION DIAGNOSTICS ONLY**:  
> The Cognitive Execution Trace records **execution timings, module contracts, invariant evaluations, and scalar state transitions**.  
> It is **NOT** a thought trace or reasoning trace.  
> It **NEVER** captures or exposes:
> * Chain-of-thought (CoT)
> * Internal monologue
> * Unrestricted cognitive state
> * Raw autobiographical memory texts
> * Prompt strings or raw LLM completions

### 7.2 Execution Span Data Model
Each stage $S_i$ emits an `ExecutionSpan` containing allowlisted scalar telemetry:
* `sequence_id`: Sequence identifier (`"S1"` to `"S16"`).
* `stage_name`: Descriptive stage name (e.g. `"SensoryEncoding"`, `"LimbicIntegration"`).
* `module_id` / `module_version`: Subsystem provenance.
* `duration_ms`: Duration of stage execution in milliseconds.
* `status`: `SUCCESS`, `FAILURE`, `SKIPPED`, or `DEGRADED`.
* `contract_result`: `SATISFIED` or `VIOLATED`.
* `invariant_result`: `SATISFIED` or `VIOLATED`.
* `state_summary`: Bounded dictionary of diagnostic numbers and booleans.
* `failure_class`: Taxonomy classification if a failure occurred.
* `first_causal_failure_candidate`: Earliest failure locus in the turn.
* `propagated_from`: ID of upstream ancestor stage if failure propagated.
* `is_primary_candidate`: Boolean indicating if this span is the primary candidate failure.

### 7.3 Causal Dependency Graph (DAG) & Attribution
Stages in the 16-stage pipeline have formal causal dependencies defined in `STAGE_CAUSAL_DEPENDENCIES`:

```text
S1  ───┬──────────────┬───────────────┬───────────────┐
       ▼              ▼               ▼               ▼
      S3             S6              S8              S16 (also S3, S4)
       │              │               │
       ├──────┐       ▼               ▼
       │      │      S7              S11 (also S5, S7, S8, S10)
       ▼      ▼       │               │
S2 ──►S4     S10      └───────────────┤
       │      ▲                       ▼
       ▼      │                      S13
      S5 ─────┤                       │
       │      │                       ▼
       ├──────┼──────► S12           S14
       │      │
       ▼      ▼
      S15    (S9 is independent: S9 ──► S10, S15)
```

### 7.4 Failure Classification & Propagation Logic
When a failure occurs in stage $S_k$:
1. If no prior failure occurred in the turn, $S_k$ is designated `first_causal_failure_candidate` (`is_primary_candidate = True`, `propagated_from = None`).
2. If an existing failure already occurred, the system inspects whether any failed stage is in the transitive causal ancestors of $S_k$ (`get_transitive_ancestors(S_k)`):
   * **Propagated Failure**: If ancestors contain a failed stage, $S_k$ is marked `DOWNSTREAM_PROPAGATED_FAILURE` with `propagated_from = first_candidate`.
   * **Independent Failure**: If no ancestor has failed, $S_k$ is marked as an independent failure locus (`propagated_from = None`).

#### Concrete Attribution Example
```text
S3 fails (e.g. Homeostatic metabolic budgeting numerical anomaly)
  → S3 is marked is_primary_candidate=True (first_causal_failure_candidate = "S3")

S4 fails (S4 depends on S2 and S3; S3 is an ancestor)
  → S4 is marked propagated_from="S3" (DOWNSTREAM_PROPAGATED_FAILURE)

S5 fails (S5 depends on S3 and S4; S3 is an ancestor)
  → S5 is marked propagated_from="S3" (DOWNSTREAM_PROPAGATED_FAILURE)

S9 fails (S9 has NO dependencies in the DAG; S3 is NOT an ancestor)
  → S9 is marked as an INDEPENDENT FAILURE (is_primary_candidate=False, propagated_from=None)
```

> [!NOTE]
> **Epistemic Qualification**:  
> The First Causal Failure (FCF) candidate is a **candidate under the declared DAG causal model**, not an absolute metaphysical claim of root causality.

---

## 8. Failure Handling & Operator Decision Tree

When operating or validating Lucia, follow this decision tree to respond to operational anomalies:

```text
                   [Start Operation / Turn]
                              │
                              ▼
                 Activation succeeded (200 OK)?
                    ├── NO ──► Check HTTP code:
                    │            • 400 NOT_BORN: Execute Genesis first.
                    │            • 409 INVALID_EVIDENCE: Investigate disk corruption.
                    │            • 410 ENDED: Instance decommissioned. Do not restart.
                    │            • 503 UNKNOWN: Storage I/O failure. Fail closed.
                    ▼ YES
                 First contact turn succeeds?
                    ├── NO ──► HTTP 500 / 503:
                    │            • Check orchestrator degradation.
                    │            • Stop submitting turns. Preserve server log.
                    ▼ YES
                 Trace healthy (overall_status == SUCCESS)?
                    ├── YES ─► All 16 spans SUCCESS. Continue normal operation.
                    ▼ NO
                 Analyze Spans in Trace:
                    │
                    ├── Invariant violation detected?
                    │     → IMMEDIATE STOP. Invariant safety breach.
                    │     → Preserve memory dump and diagnostics. Return to inactive.
                    │
                    ├── Contract violation with primary candidate (FCF)?
                    │     → Stop conversational session.
                    │     → Isolate candidate stage (e.g. S3 Homeostasis or S14 Gate).
                    │     → Escalate trace JSON to engineering.
                    │
                    ├── Downstream propagated failure only?
                    │     → Upstream candidate already captured.
                    │     → Confirm downstream stages failed gracefully without state corruption.
                    │
                    └── Independent multi-stage failure (e.g. S3 and S9)?
                          → High-severity architectural anomaly.
                          → Halt companion process.
                          → Escalate to engineering before submitting further turns.
```

### Action Protocols

| Condition | Immediate Action | Diagnostic Preservation | Lifecycle State |
|---|---|---|---|
| **Normal Operation (16/16 SUCCESS)** | Continue interaction. | Traces buffered in memory (last 100 turns). | `BORN + ACTIVE` |
| **HTTP 403 on `/process`** | Companion is inactive. Call `POST /lifecycle/activate`. | N/A | `BORN + INACTIVE` |
| **Single Stage Contract Violation** | Stop chat turn. Inspect `trace.first_causal_failure_candidate`. | Copy `orch.get_latest_execution_trace().to_dict()`. | Stop turns; keep server alive for inspection. |
| **Invariant Violation (L1_INVARIANTS)** | Halt companion immediately. Do NOT submit new turns. | Dump `chat_history.json`, `data/epoch_manifest.json`, and trace log. | Stop server (`Ctrl+C`). Revert to `INACTIVE`. |
| **Catastrophic Terminal Reset (`/lifecycle/end`)** | Reserved strictly for intentional, irreversible decommissioning. | N/A (Wipes episodic memory traces). | `ENDED` (Terminal). |

---

## 9. Desktop Room & Embodied Presence Guide

Lucia's graphical interface operates as a **Personal Digital Room** with progressive disclosure:

```
┌────────────────────────────────────────────────────────────────────────────────────────────────────────┐
│ ✦ Lucia  [🎂 Day 1]               [💬 Talk]  [🧠 Memories]  [📖 Journal]  [⚙️ Settings]       [🐾 Mascot] ✕ │
├─────────────────────────────────────────────────┬──────────────────────────────────────────────────────┤
│               AVATAR STAGE                      │                  CONVERSATION PANE                   │
│  ┌───────────────────────────────────────────┐  │  ┌────────────────────────────────────────────────┐  │
│  │                                           │  │  │ ✨ Welcome to Lucia                            │  │
│  │            🎭 [AVATAR MODEL]              │  │  └────────────────────────────────────────────────┘  │
│  │         (Canvas / Sprites / Live2D / VRM) │  │                                                      │
│  │                                           │  │  [You]: Hello Lucia!                                 │
│  │   • Autonomous micro-gaze & blinking      │  │                                                      │
│  │   • Real-time Web Audio lip-sync          │  │  [Lucia]: Hi! It's so nice to see you.               │
│  │   • Emotionally responsive blendshapes    │  │           🔊 [Local RVC Voice Synthesis]             │
│  │                                           │  │                                                      │
│  └───────────────────────────────────────────┘  │  ┌─────────────────────────────────────────────┬─┬─┐  │
│  [Engine ▼] [Model ▼] [Voice ▼] [━●━] [🔊 Mute] │  │ Type a message... (Shift+Enter for newline) │🎙│➤│  │
│  • Drag to Pan • Scroll to Zoom • Double-click  │  └─────────────────────────────────────────────────┴─┴─┘  │
└─────────────────────────────────────────────────┴──────────────────────────────────────────────────────┘
```

### 9.1 Avatar Stage & Multi-Engine Rendering
* **Quad-Engine Renderer**: Toggle between `🎨 2D Canvas` (vector procedural face, 0 MB VRAM), `🖼️ 2D Sprites` (PNG emotion sets), `🎬 Live2D` (Cubism 4 WebGL interactive models), and `🌐 3D VRM` (humanoid rigged 3D models).
* **Mouse Interactions**:
  * **Pan**: Click and drag empty stage space to move avatar.
  * **Zoom**: Scroll wheel over avatar to scale.
  * **Reset**: Double-click avatar to restore default scale and center alignment.

### 9.2 Real-Time Lip-Sync & Audio Controls
* **Web Audio FFT Lip-Sync**: Uses real-time 60 FPS formant analysis (200Hz–2500Hz) to drive mouth opening and vowel shapes directly during neural voice playback.
* **Local Neural Voice (RVC)**: Select custom character voice profiles from `models/voice/rvc/` or use built-in female voice.

### 9.3 Real-Time Diagnostics Panel (`Ctrl + Shift + D`)
Press **`Ctrl + Shift + D`** anywhere in the main window to open the engineering telemetry panel:
* **Limbic Fast/Slow Latent Vectors**: $\mathbf{h}_{\text{fast}} \in \mathbb{R}^{32}$, $\mathbf{s}_{\text{slow}} \in \mathbb{R}^{16}$, and 3D PAD coordinates.
* **Stability Telemetry**: Fast-Loop tick jitter ($< 2.0\text{ms}$), ODE velocity variance, and Composite Limbic Stability Index (LSI).
* **Consolidation Engine Status**: Offline BPTT buffer size, idle accumulator, and parameter swap latency.

---

## 10. Floating Mascot Mode Guide

Click **`🐾 Mascot`** in the header (or press `Ctrl + Shift + L`) to switch into a transparent, frameless, Always-on-Top desktop mascot:

```
          (\_/)
         ( •‿• )   <-- Avatar Model (Click & drag to reposition across monitors)
        / >❤️< \
       (______)
   ┌───────────────────────┐
   │ 💬  🎬  🔊  🎙️  ⚙️  │ ✕ │  <-- Model-Anchored Toolbar Dock
   └───────────────────────┘      (Follows character bottom center)
```

### 10.1 Key Mascot Controls
1. **Direct Model Dragging**: Left-click and drag the character model itself to move the window anywhere across screens.
2. **Model-Anchored Toolbar**: The dock automatically calculates character bounds (`getModelBounds()`) and anchors beneath the model.
3. **Hover-Only Zoom**: Scroll-wheel zoom operates **only when the mouse cursor is directly over the character model**, with an 800ms post-drag cooldown suppressing accidental touchpad momentum.
4. **Quick Chat (`💬`)**: Opens an inline compact speech bubble allowing text input and spoken audio responses without opening the main window.
5. **Global Shortcut (`Ctrl + Shift + L`)**: Press from anywhere in Windows to summon or hide the mascot.

---

## 11. Frequently Asked Questions (FAQ)

**Q: Can Lucia operate completely offline without internet?**  
**A:** Yes. The language model (GGUF via llama.cpp), limbic ODE, associative SDM memory, RVC neural voice synthesis, and avatar rendering run 100% locally on your machine with zero remote API calls.

**Q: Does voice synthesis or avatar rendering slow down the companion's thought process?**  
**A:** No. Voice synthesis and avatar rendering are completely decoupled feedforward actuators. Language generation and limbic integration complete first, and voice synthesis is dispatched asynchronously via IPC without stalling cognitive turns.

**Q: How do I back up Lucia's memory and relationship progress?**  
**A:** All autobiographical memory traces (`data/`), relational state (`data/relationship.json`), identity commitment (`data/genesis_commitment.json`), and profile (`data/profile.json`) are stored locally in `data/`. Backing up the `data/` directory completely preserves her continuous life.

**Q: What happens if the computer crashes or powers down during conversation?**  
**A:** Lucia implements two-tier persistence (ADR-033). The `epoch_manifest.json` Commit Barrier and atomic `.bak` reconciliation guarantee that uncommitted turns are safely recovered and working memory is reseeded from the last clean commit upon startup.
