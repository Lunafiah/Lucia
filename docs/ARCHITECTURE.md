# Lucia — System Architecture Specification

> **A Whole-Brain Architecture for an Embodied, Continuously Affective AI Companion**

---

## 1. Executive Summary & Design Philosophy

Lucia is an embodied AI companion built on a **Whole Brain Architecture** inspired by the human brain's 20-watt efficiency model. Unlike conventional chatbots that simply "roleplay" emotion through prompt engineering, Lucia's emotional state is a **continuous, physiological-like dynamic system** governed by differential equations, subconscious memory resonance, active inference, and real-time multimodal presence.

### The Foundational Tenet: *Philia* Friendship
Lucia's internal limbic state is centered around **Philia** ($\phi\iota\lambda\iota\alpha$)—the classical egalitarian friendship rooted in mutual respect, curiosity, and authentic growth:
* **Resting Baseline (Attractor)**: $P = +0.25$ (warmth), $A = -0.05$ (calm presence), $D = +0.05$ (equal peer).
* **Non-Compelled Growth**: Her internal state is never rigidly forced or scripted. Her differential equations freely react to conversations, and her bond with the user crystallizes organically over time through subconscious memory traces.

---

## 2. 6-Layer Cognitive Architecture

```
┌─────────────────────────────────────────────────────────────────────────┐
│  LAYER 1: SENSORS & STIMULUS PROCESSOR                                  │
│  • Extracts text valence, punctuation arousal & semantic density        │
│  • Produces a 16-dimensional continuous Stimulus Vector                 │
├─────────────────────────────────────────────────────────────────────────┤
│  LAYER 2: LIMBIC SYSTEM — FAST LOOP (Liquid Neural Network ODE)         │
│  • Continuous 200ms background ODE integration (solve_ivp)              │
│  • Maintains 32-dim hidden state h and projects to 3D PAD Space:        │
│    Pleasure (P), Arousal (A), Dominance (D) in [-1.0, 1.0]              │
├─────────────────────────────────────────────────────────────────────────┤
│  LAYER 3: SURVIVAL SYSTEM — MID LOOP (Homeostatic Engine)               │
│  • Tracks Cognitive Load, Energy, Metabolic Budget, and Tension         │
│  • Computes Behavioral Constraints (Token budget, Temperature, Latency) │
├─────────────────────────────────────────────────────────────────────────┤
│  LAYER 4: ACTIVE INFERENCE ENGINE (Free Energy Minimization)            │
│  • 3x3 linear generative model predicting upcoming PAD trajectories     │
│  • Online backprop-through-ODE LNN trainer (torchdiffeq on CPU)         │
├─────────────────────────────────────────────────────────────────────────┤
│  LAYER 5: HIPPOCAMPUS — SLOW LOOP (SDM + Affective Memory)              │
│  • Kanerva Sparse Distributed Memory (SDMCore) with PAD emotion tagging │
│  • Synergistic Ecphory Engine (subconscious memory resonance echo)      │
│  • Slow-loop decay engine with emotional intensity resistance           │
├─────────────────────────────────────────────────────────────────────────┤
│  LAYER 6: MULTIMODAL EXPRESSION & EMBODIED PRESENCE                     │
│  • Local SLM (LFM2.5-1.2B GGUF with CUDA GPU acceleration)              │
│  • Self-contained RVC Voice Synthesis Engine (models/voice/rvc/)        │
│  • Self-contained Offline faster-whisper STT Engine (POST /voice/transcribe) │
│  • 60 FPS Interactive Canvas/Live2D/VRM Avatar with Web Audio Lip-Sync  │
└─────────────────────────────────────────────────────────────────────────┘
```

---

## 3. Detailed Component Deep-Dive

### 3.1. Layer 1: Stimulus Processor (`src/core/gating/stimulus_processor.py`)
*Historical path: `src/core/sensors/` (retained in historical Phase 1 specs).*
* **Valence Extraction**: Lexical affinity analysis scoring sentiment in $[-1.0, 1.0]$.
* **Arousal Extraction**: Punctuation cadence, capitalization bursts, and urgency scoring in $[0.0, 1.0]$.
* **Semantic Density**: Information-to-token ratio across the input message.
* Outputs a 16-dimensional continuous floating-point vector injected into the limbic system.

### 3.2. Layer 2: Fast-Loop Limbic ODE (`src/core/emotion/`)
The emotional core runs a continuous **Liquid Time-Constant (LTC)** differential equation:
$$\frac{dh}{dt} = \frac{-h + \tanh(W_f h + U_f x + b_f)}{\text{softplus}(W_\tau h + U_\tau x + b_\tau)}$$
* **Cadence**: 200ms background daemon thread.
* **Projection**: Linear projection $W_{proj} h + b_{proj}$ mapped and clamped to the 3D PAD space $[-1.0, 1.0]^3$.
* **Thread Safety**: Protected by `_state_lock` (read deadline $\le 1\text{ms}$) and `_train_lock` for atomic weight swapping.

### 3.3. Layer 3: Homeostatic Engine (`src/core/emotion/homeostatic_engine.py`)
*Historical path: `src/core/homeostasis/` (retained in historical Phase 1 specs).*
Prevents emotional burnout, runaway anxiety, or manic states:
* **Metabolic Budgeting**: Depletes energy on heavy turns; recovers during idle periods.
* **Somatic Markers**: Computes Stability, Cognitive Load, Energy, and Tension.
* **Dynamic Parameter Conditioning**:
  * High Arousal $\rightarrow$ Shorter token budget (brisk replies), higher temperature.
  * High Tension $\rightarrow$ Increased reasoning depth ($k=2$).
  * Low Energy $\rightarrow$ Simulated conversational latency delay.

### 3.4. Layer 4: Active Inference & LNN Plasticity (`src/core/inference/`)
* **Active Inference Engine**: Maintains belief state matrices $A \in \mathbb{R}^{3 \times 3}, b \in \mathbb{R}^3$ predicting emotional transitions. Before stimulus integration, projects expectation $\hat{p} = A \cdot p_{before} + b$. After integration, computes Free Energy Prediction Surprise:
  $$\mathcal{S} = \|A \cdot p_{before} + b - p_{after}\|_2$$
  Updates belief state via analytic gradient descent with KL regularization toward identity.
  **Causal Coupling**: Surprise $\mathcal{S}$ directly modulates `HomeostaticEngine` Cognitive Load and Tension, shifting reasoning depth to $k=2$ when $\mathcal{S} > 0.60$ or Tension $> 0.70$.
* **Two-Stage LNN Plasticity**: Online salience tagging flags transitions where $\text{Salience} > 0.35$. A dedicated background CPU thread executes backpropagation-through-ODE (`torchdiffeq.odeint`) during idle rest periods ($T_{\text{idle}} \ge 45\text{s}$) or salient batch overflow ($\ge 8$), adapting weights without competing for GPU VRAM or interrupting active conversation.

### 3.5. Layer 5: Affective Memory & Ecphory (`src/core/memory/`)
* **Kanerva Sparse Distributed Memory (SDM)**: $N=1,000$ distributed locations with 64-bit Hamming addresses and 16-bit content vectors.
* **Emotional Decay**: Traces decay exponentially; high-intensity emotional moments ($|PAD| \gg 0$) resist decay up to $4\times$ longer.
* **Synergistic Ecphory**: When Lucia enters an emotional state, the engine queries past traces and generates a subconscious **Echo Vector** that softly primes her prompt without quoting past memories mechanically.

### 3.6. Layer 6: Voice, Avatar & Embodied Presence

#### 1. Direct RVC Voice Engine (`src/core/voice/`)
* Loads `.pth` weights and `.index` feature files directly from `models/voice/rvc/`.
* Synthesizes character speech on-demand with PAD-aware emotional pitch/speed modulation.
* High-frequency phrase cache ensures zero-latency playback for conversational acknowledgments.

#### 2. Quad-Engine Electron Desktop Avatar (`electron/renderer/avatar/`)
Lucia features a unified polymorphic avatar architecture supporting four rendering engines:
* **🎨 2D Procedural Canvas**: Pure HTML5 Canvas vector rig calculating real-time quadratic bezier curves, eye openness, blush gradients, and procedural mouth articulation. Zero VRAM overhead.
* **🖼️ 2D Expression Sprites**: High-performance PNG sprite sequencer (`idle`, `smile`, `blush`, `speaking`, `thinking`) switching based on live PAD valence/arousal thresholds and Web Audio amplitude.
* **🎬 Live2D Cubism 4 Engine**: WebGL rendering via PixiJS and Official Cubism 4 Core (`live2dcubismcore.min.js`). Maps PAD coordinates to standard Live2D parameter IDs (`ParamEyeLOpen`, `ParamEyeROpen`, `ParamMouthOpenY`, `ParamCheek`, `ParamAngleX`, `ParamAngleY`).
* **🌐 3D Humanoid VRM Engine**: WebGL rendering via Three.js and `@pixiv/three-vrm` with full skeletal hierarchy, natural blinking, eye gaze direction, and VRM blendshape morph targets (`happy`, `blink`, `aa`, `relaxed`). Includes a holographic procedural fallback rig when no model file is loaded.

#### 3. Avatar Physics & Web Audio Lip-Sync
* **Expression Mapper (`expression-mapper.js`)**: Maps 500ms PAD telemetry into continuous blendshape weights with smooth exponential damping ($\tau \approx 120\text{ms}$).
* **Web Audio Lip-Sync (`lip-sync.js`)**: Real-time FFT spectrum analysis across vocal formants (200Hz–2500Hz) computing mouth aperture height and vowel width at target framerates.
* **Smart Framerate Limiter**: Supports both 60 FPS (high fluid dynamic) and 30 FPS (energy-saving / battery mode, 50% CPU/GPU reduction).

---

## 4. Desktop & Mascot Window IPC Architecture

Lucia provides two presentation contexts managed by Electron:

```
┌────────────────────────────────────────────────────────────────────────┐
│                        ELECTRON MAIN PROCESS                           │
│  • HotkeyManager (Ctrl+Shift+L)   • TrayManager (Always running core)  │
│  • ProcessManager (FastAPI subproc) • MascotWindowManager              │
└───────────────────────────────────┬────────────────────────────────────┘
                                    │ IPC Bridge
           ┌────────────────────────┴────────────────────────┐
           ▼                                                 ▼
┌──────────────────────────────┐          ┌──────────────────────────────┐
│     MAIN APP WINDOW (STUDIO) │          │   ALWAYS-ON-TOP MASCOT MODE  │
│ • Personal Digital Room      │          │ • Transparent, frameless     │
│ • Progressive Disclosure Nav │          │ • Zero-chrome desktop avatar │
│ • Interactive Chat Feed      │          │ • Model-anchored dock toolbar│
│ • Full-Height Avatar Stage   │          │ • Mouse window drag via IPC  │
│ • Settings, Journal, Diag    │          │ • Smart hover-bounded zoom   │
└──────────────────────────────┘          └──────────────────────────────┘
```

* **Smooth Mascot Window Dragging**: Window translation is handled by `window.lucia.window.moveMascotBy(dx, dy)` communicating directly with the main process. This eliminates Chromium's native `-webkit-app-region: drag` bug on Windows where touchpad dragging floods mouse wheel events and unintentionally resizes content.
* **Trackpad Inertia Cooldown (800ms)**: When releasing the model after dragging, an 800ms cooldown suppresses residual touchpad momentum wheel events, preventing the avatar from blowing up in size after dragging.
* **Aero Snap Prevention & Window Reset**: The Mascot BrowserWindow sets `maximizable: false`, `fullscreenable: false`, and `resizable: false` to prevent Windows Aero Snap from accidentally maximizing the transparent window to 1920×1080 when dragged near screen edges. Double-clicking or clicking Reset triggers `window:reset-mascot-bounds` to unmaximize and reset dimensions to standard 380×540.
* **Model-Anchored Dynamic Dock**: The Mascot Toolbar dock mathematically binds to `getModelBounds()`, positioning itself at `centerX` and `bottomY + 8px` directly beneath the character's geometry.
* **Hit-Tested Hover Zoom**: The wheel zoom event strictly validates `isCursorOverModel(clientX, clientY)`, ensuring zoom only occurs when the user explicitly hovers over the model itself.
* **Offline Speech-to-Text (`faster-whisper`)**: Continuous voice recording utilizes frontend `MediaRecorder` + Web Audio VAD with local transcription via `POST /voice/transcribe`, eliminating Chromium's chunked upload pipe errors (`webkitSpeechRecognition`) and operating with zero third-party cloud keys.

---

## 5. Concurrency & Threading Model

Lucia operates with non-blocking concurrent daemon threads coordinated by strict thread-safe locks and turn serialization:

| Thread / Worker Name | Module | Cadence | Purpose | Lock Discipline |
| **`Cognitive Turn Mutex`** | Brain Core (`server.py`) | Per Turn | Serializes cognitive turn execution | Holds `asyncio.Lock` & `_turn_lock` during `process()` |
| **`EmotionCore-FastLoop`** | Limbic Engine | 200ms | Solves continuous Coupled MT-LNN ODE ($\mathbf{h}_{\text{fast}} \in \mathbb{R}^{32}, \mathbf{s}_{\text{slow}} \in \mathbb{R}^{16}$) with auxiliary slow-field recollection forcing | Holds `_step_lock`, `_state_lock` ($\le 1\text{ms}$), copies weights via `_train_lock` |
| **`DecayEngine-SlowLoop`** | Memory Store | 60s | Applies emotional memory decay | Holds `_index_lock` |
| **`LNN-Trainer`** | Offline Plasticity | Idle / Salience | CPU Backpropagation-through-ODE | Holds `_train_lock` during weight swap ($\le 2\text{ms}$) |
| **`SimClock Background`** | Simulation | Configurable | Virtual clock advancement when resumed | Dispatches synchronous callbacks; no autonomous loops |
| **`Uvicorn Async Loop`** | FastAPI Server | Event-driven | Serves `/process`, `/state`, `/sim/*`, `/voice/*` | Async non-blocking I/O (`/state` reads under `_state_lock`) |
| **`Electron Render Thread`**| UI / Avatar | 60 / 30 FPS | WebGL & Canvas avatar rendering | RequestAnimationFrame loop |

### 5.1. Temporal Synchronization Contract & Lock Hierarchy

To prevent asynchronous race conditions where `CognitiveOrchestrator` reads `PAD_final` before `EmotionCore` has integrated the turn's stimulus, Lucia enforces an explicit **Temporal Synchronization Barrier**:

1. **Architectural Invariants & Epistemic Status**:
   * **[PROVEN INVARIANT]**: A cognitive turn MUST integrate its stimulus into L2 and commit the state transition deterministically before L4 Active Inference reads `PAD_final`.
   * **[PROVEN INVARIANT]**: Intra-turn stimulus processing follows strict exactly-once FIFO execution (`collections.deque`), guaranteed under `_step_lock`. Idle ticks never advance `_committed_stimulus_seq`.
   * **[IMPLEMENTED CONTRACT]**: `push_stimulus(vector)` assigns a monotonically increasing sequence token `_stimulus_seq`. `CognitiveOrchestrator._execute_pipeline()` captures `token = push_stimulus(stimulus)`, invokes `commit_stimulus(token)`, and directly binds `pad_final = pad_committed`, completely eliminating the possibility of background idle ticks interleaving between Stage 3 limbic integration and Stage 4 surprise evaluation.
   * **[IMPLEMENTED CONTRACT]**: The background `FastLoop` worker (200ms) governs continuous autonomous limbic relaxation towards the Philia resting attractor ($P=+0.25, A=-0.05, D=+0.05$). The synchronous `commit_stimulus(token)` barrier governs deterministic stimulus-caused state transition. These two mechanisms never contend destructively.
2. **Implementation Mechanism (`commit_stimulus()`)**:
   * `commit_stimulus(target_seq)` acts as an idempotent barrier:
     * **Case A (Pending)**: If `_committed_stimulus_seq < target_seq`, drains pending stimuli in FIFO order under `_step_lock` via `_step_once_unlocked()`, updates `self._h`, publishes the new `PADState` snapshot under `_state_lock`, and marks `_committed_stimulus_seq = target_seq`. Includes a defensive break if the queue is emptied externally to prevent infinite loops.
     * **Case B (Already Committed)**: If the 200ms background thread already consumed and integrated the stimulus, `commit_stimulus()` observes `_committed_stimulus_seq >= target_seq` and immediately returns without duplicating the ODE step (strictly exactly-once semantics).
3. **Lock Hierarchy (Verified Call Graph)**:
   $$\text{Orchestrator } \_turn\_lock \longrightarrow \_step\_lock \longrightarrow \_train\_lock \longrightarrow \_stimulus\_lock \longrightarrow \_state\_lock$$
   * `_turn_lock`: Serializes single-turn execution in `CognitiveOrchestrator`. Held during turn pipeline including local LLM generation to preserve Lucia's single continuous train of thought. Never blocks `/state` or telemetry polling.
   * `_step_lock`: Serializes ODE step calculation between turn threads and the background `FastLoop` worker. Held during `solve_ivp` ($\sim 0.5 - 2\text{ms}$) to serialize LNN hidden state mutation.
   * `_train_lock`: Protects LNN weight arrays during parameter copy or plasticity weight swap ($\le 2\text{ms}$). Released before `solve_ivp`.
   * `_stimulus_lock`: Protects pending stimulus FIFO buffer and sequence token counters ($\le 0.1\text{ms}$).
   * `_state_lock`: Protects `_pad_snapshot` reads/writes ($\le 1\text{ms}$).
   * **Lock Order Invariant**: Locks must always be acquired in descending order of this hierarchy. Zero inverted acquisitions, nested deadlocks, or lock leaks exist in any execution or exception path.

### 5.2. Temporal Affect Dynamics & Three State Categories

Temporal synchronization validation and subsequent Temporal Ablation v2 experiments establish a clear formal taxonomy of temporal variables within Lucia's architecture:

#### 1. Taxonomy of Three Temporal State Categories

| Category | State Variables | Update Mechanism | Lifetime & Persistence | Downstream Causal Influence |
|---|---|---|---|---|
| **A. Persistent Dynamical State** | Coupled MT-LNN states ($\mathbf{h}_{\text{fast}} \in \mathbb{R}^{32}, \mathbf{s}_{\text{slow}} \in \mathbb{R}^{16}$), committed $PAD \in [-1, 1]^3$, Kanerva SDM traces (Content 64D + PAD 3D + Slow 16D) | Continuous Coupled MT-LNN ODE integration (`solve_ivp`), background FastLoop (200ms) | **Continuous & Permanent across turns**. Decays smoothly toward Philia attractor ($+0.25, -0.05, +0.05$) under background ODE relaxation. | Directly sets the initial conditions for subsequent ODE steps, determines Active Inference expectation $\hat{p} = A \cdot p + b$, and cues SDM Synergistic Ecphory retrieval. |
| **B. Accumulated Physiological State** | Energy $\mathcal{E}$, Cognitive Load $\mathcal{C}$, Input frequency window | Discrete turn depletion/recovery; 60-second rolling sliding window in `HomeostaticEngine` | **Multi-turn temporal integration**. Depletes with turns ($\Delta \mathcal{E} = -0.05$ per turn) and compounds with rapid conversational frequency. | Causal behavioral constraints: directly throttles generation token budget (`max_tokens`: $350 \to 150 \to 80$), modulates sampling temperature, and injects conversational latency. |
| **C. Instantaneous Derived Affect** | Free Energy Surprise $\mathcal{S}$, Per-turn Somatic Tension $\mathcal{T}$, $\Delta\text{PAD}$ transition | Single-step evaluation per cognitive turn | **Instantaneous (Zero inter-turn persistence)**. Evaluated strictly on the current transition $(p_{before} \to p_{after})$. Cleared each turn. | Triggers deliberative reasoning depth ($k=2$) if single-step surprise $\mathcal{S} \ge 0.60$ or tension $\mathcal{T} \ge 0.70$. Modulates online salience tagging. |

#### 2. Somatic Tension Audit & Semantics

In earlier ablation pilots, Tension was observed at $0.0000$ across consecutive emergency turns even as Cognitive Load rose to $0.5891$ and Pleasure dropped to $-0.1825$. Code-level audit reveals the precise architectural semantics:
- **Instantaneous Threshold Excess**: In `HomeostaticEngine._compute_tension()`, tension is defined as $|v - P_{01}|$ (where $v$ is lexical valence and $P_{01}$ is normalized pleasure). In `SurpriseModulationPolicy.modulate_somatic()`, tension modulation is:
  $$\Delta\mathcal{T} = 0.5 \cdot \max(0.0, \mathcal{S} - \theta_{\text{tension}})$$
  where $\theta_{\text{tension}} = 0.40$.
- **Absence of Multi-Turn Leaky Accumulation**: Tension is an **acute threat / mismatch signal**, NOT a persistent physiological reservoir. Because single-step surprise $\mathcal{S} \approx 0.06 - 0.10$ remains below the onset threshold ($0.40$), and because `_execute_pipeline()` evaluates baseline markers with $v=\text{None}$, single-turn tension remains $0.0000$.
- **Architectural Policy**: Tension is intentionally not equipped with an ad-hoc leaky integrator without explicit design requirements. Lucia models physiological fatigue via **Cognitive Load** (which *does* accumulate across turns to $0.5891$) and metabolic stamina via **Energy** (which drains to $0.50$).

#### 3. Temporal Ablation v2 Empirical Findings (Real GGUF on CUDA)

Executed via `tests/ablation/run_temporal_ablation_v2.py` using `LFM2.5-1.2B-Instruct-Q4_K_M.gguf` (Seed: 43):

* **[PROVEN INVARIANT] State Reset Control (C1 vs. C2)**:
  * In **C1 (Persistent)**, repeated stimuli drive cumulative limbic displacement monotonically ($0.2259 \to 0.2580 \to 0.2605 \to 0.3011 \to 0.3205$), causing Cognitive Load to compound to $0.3370$ and throttling `max_tokens` from 350 to 150.
  * In **C2 (Turn-by-Turn Reset)**, resetting L2 state before each turn clamps displacement at exactly $0.2259$ every turn. This proves conclusively that multi-turn affective trajectory is driven strictly by L2 hidden state persistence.
* **[PROVEN INVARIANT] Same-Probe Hysteresis (Exp D)**:
  * Presenting the **exact identical probe text** (`"What is the current status report on system operations?"`) under different prior histories produces divergent mathematical states:
    * **D1 (Neutral Baseline)**: Post-PAD $= (+0.0607, +0.0443, +0.0608)$, Surprise $= 0.0000$, Cognitive Load $= 0.0721$, `max_tokens` $= 350$.
    * **D2 (Post-Stress)**: Post-PAD $= (-0.0278, +0.0955, +0.1154)$, Surprise $= 0.0711$, Cognitive Load $= 0.3155$, `max_tokens` $= 150$.
    * **D3 (Post-Relaxation)**: Post-PAD $= (-0.0251, +0.0803, -0.0025)$, Surprise $= 0.0962$, Cognitive Load $= 0.3142$, `max_tokens` $= 150$.
  * **Causal Proof**: Prior affective history directly and causally alters the post-probe limbic state, prediction error, and generation constraints for identical sensory input.
* **[EMPIRICAL RESULT] Active Inference Online Adaptation (Exp E)**:
  * Prediction surprise $\mathcal{S}$ decreases monotonically under repeated identical stimuli ($0.0927 \to 0.0750 \to 0.0712 \to 0.0699$).
  * The belief bias vector $b$ continuously adapts online ($\|\Delta b\| \approx 1.5 \times 10^{-4}$ per step, cumulative $\|b\| = 6.17 \times 10^{-4}$), demonstrating that Active Inference learns environmental regularities.
* **[EMPIRICAL RESULT] Background Autonomous Relaxation (Exp F)**:
  * Following acute stress displacement ($0.3159$ from resting attractor), idle FastLoop ODE integration smoothly relaxes limbic coordinates back toward Philia ($0.3159 \to 0.3087 \to 0.3049 \to 0.2979$ across $t = 0 \dots 12\text{s}$), verifying continuous pre-reflective recovery.

### 5.3. Memory-Affect Coupling: From Open-Loop Retrieval to Closed-Loop Recollection

Lucia's memory-affect integration has evolved through three distinct evolutionary milestones:

#### 1. Historical Evolution: Open-Loop Memory Sink (Phase 9–19 Baseline)
In early architectural stages (Phases 2 through 19), memory retrieval operated strictly as an open-loop textual context injection:
- Stored traces in Kanerva SDM were queried via PAD cosine similarity, synthesizing an `echo_vector`.
- In early prototypes, `echo_vector` was forwarded exclusively to `PromptAssembler`, printed as numeric context lines `[MEMORY ECHO]\necho_i: ...` for LLM generation.
- The internal dynamical systems (Limbic ODE $\mathbf{h}_{\text{fast}}$, Homeostasis $\mathcal{C}, \mathcal{E}, \mathcal{T}$, and Active Inference $\mathcal{S}$) were deaf to retrieved memories.

#### 2. Canonical S1–S16 Cognitive Pipeline Realization (Phase 16)
Phase 16 formalized the unified, non-reentrant 16-stage cognitive execution pipeline (`CognitiveOrchestrator._execute_pipeline`), establishing clear ownership boundaries across all subsystems:
- **S1**: Sensory Gating (`StimulusProcessor`)
- **S2**: Limbic Fast Loop Integration (`EmotionCore`)
- **S3**: Homeostatic Assessment (`HomeostaticEngine`)
- **S4**: Active Inference Prediction & Surprise ($\mathcal{S}$)
- **S5**: Homeostatic Generation Constraints
- **S6**: Affective Ecphory & Recollection Analysis
- **S7**: Episodic Memory Contextualization
- **S8**: Conceptual Knowledge Retrieval (`KnowledgeStore`)
- **S9**: Interpersonal Relationship Read (`RelationshipStore`)
- **S10**: Affective Communication Policy (`CommunicationPolicy`)
- **S11**: Local CUDA GGUF SLM Language Generation
- **S12**: Boundary Safety Filtering & Pacing Modulation ($\Delta\tau_{\text{pace}}$)
- **S13**: Multimodal Expression Policy (`ExpressionPolicy`, 15-dim state)
- **S14**: Epistemic & SDM Storage (Stage 16.1: Live slow-field co-encoding)
- **S15**: Plasticity Salience Tagging (`LNNTrainer`)
- **S16**: Post-Turn Relationship State Update (`RelationshipUpdater`)

#### 3. Closed-Loop Affective Recollection via Slow-Field Latent Forcing (Phase 20 Production)
Phase 20 resolved the open-loop boundary limitation by realizing **Closed-Loop Affective Recollection** coupled into the Coupled MT-LNN slow latent field ($\mathbf{s}_{\text{slow}} \in \mathbb{R}^{16}$):
1. **Episodic Co-Encoding (Stage 16.1)**: `CognitiveOrchestrator` captures the live physiological slow latent state $\mathbf{s}_{\text{slow}}(t)$ from `EmotionCore.get_slow_latent_state()` and embeds it in `MemoryTrace.slow_latent_trace`. Pre-Phase-20 traces utilize a deterministic 3-case legacy fallback approximation (`synthesize_legacy_latent`).
2. **Multi-Modal Retrieval Scoring & Competitive Softmax Gating (Stage 6)**: `EcphoryEngine.query_recollection()` evaluates composite salience $S_i = 0.60 S_{\text{sem}} + 0.25 S_{\text{aff}} + 0.15 w_{\text{decay}}$ with competitive softmax temperature ($\tau_{\text{comp}} = 0.20$) above threshold $\theta_{\text{gate}} = 0.50$, synthesizing bounded forcing $\mathbf{r}_{\text{slow}}^{\text{bounded}} \in [-0.85, 0.85]^{16}$.
3. **Continuous ODE Slow-Field Forcing**: `CognitiveOrchestrator` invokes `EmotionCore.inject_recollection(r_slow, duration_sec=4.0)`. Auxiliary forcing couples into the continuous slow ODE under diagonal coupling $\mathbf{W}_{\text{rec}} = 0.35 \mathbf{I}_{16}$ for a 4.0-second pulse (tracked in simulation integration time across step boundaries).
4. **Pre-Reflective Downstream Pacing Modulation (Stage 12)**: Somatic pacing latency delta $\Delta\tau_{\text{pace}} = w_{\text{pace}} \cdot \|\mathbf{r}_{\text{slow}}^{\text{bounded}}\|$ ($+111.8\text{ms}$ observed) modulates response rhythm without introspective roleplay.
5. **Decoupled Subsystem Discipline**: `EcphoryEngine` emits `RecollectionResult` with zero dependency on `EmotionCore`. `CognitiveOrchestrator` owns actuation. Feature flag `enable_affective_recollection` provides instant fail-safe rollback to Phase-19 dynamics.

#### 4. Four-Tier Classification of Affective Memory

| Memory Level | Definition | Status in Lucia | Architectural Evidence |
|---|---|:---:|---|
| **Level A: Storage** | Discrete event representations co-stored with affective snapshots. | **PROVEN** | `AffectiveMemory.store(content, pad_final)` writes to SDMCore and index. |
| **Level B: Associative Retrieval** | Cue similarity reactivates resonant traces based on current limbic state. | **PROVEN** | `EcphoryEngine.query(pad_final, traces)` computes PAD cosine resonance ($r > 0.6$). |
| **Level C: Affective Recollection** | Retrieved memory feeds back to modify current internal mathematical state ($\mathbf{s}_{\text{slow}}, p, \tau_{\text{pace}}$). | **PROVEN & PRODUCTION IMPLEMENTED** | Phase 20: Stage 6 `inject_recollection()`, Stage 12 $\Delta\tau_{\text{pace}}$, Stage 16.1 slow trace co-encoding (`f20420a`). |
| **Level D: Autobiographical Continuity** | Causal history of interrelated events shaping an enduring self-model. | **PLANNED RESEARCH** | Past dialogues exist as structured transcripts and SDM vectors; interconnected causal graph remains future research. |

---

## 6. Hardware Scalability & Dynamic Profiling

Lucia features automated hardware detection (`HardwareTier`) with real-time runtime reconfiguration via `POST /system/profile`:

| Hardware Tier | Detected Specs | Model Offload | Context Size | SDM Capacity | Loop Cadence | Target VRAM |
|---|---|---|---|---|---|---|
| **`CPU_ONLY`** | No GPU / Battery Saver | 0 layers (CPU only) | 1,024 tokens | 250 traces | 500ms | $0\text{ MB}$ |
| **`LAPTOP`** | $< 6\text{GB}$ VRAM (e.g. RTX 3050 Ti) | 32 GPU Layers (1.2B/3B) | 2,048 tokens | 500 traces | 200ms | $\approx 1.5\text{GB}$ |
| **`DESKTOP`** | $6\text{GB} - 12\text{GB}$ VRAM (e.g. RTX 3060/4060) | Full GPU (3B/7B) | 4,096 tokens | 2,000 traces | 150ms | $\approx 4.0\text{GB}$ |
| **`HIGH_END`** | $> 12\text{GB}$ VRAM (e.g. RTX 3090/4090) | Full GPU (7B/14B) | 8,192 tokens | 10,000 traces | 100ms | $\approx 8.0\text{GB}$ |

* **Live Dynamic Profiling**: Users can switch tiers on-the-fly from the `⚙️ Settings` UI modal, adjusting memory parameters, context windows, and compute cadence without restarting the backend process.

---

## 7. Phase 8 Runtime Isolation & Simulation Architecture

Phase 8 introduces a deterministic, inspectable simulation runtime executing under the invariant:

$$\text{Development / Simulation Environment} \neq \text{Lucia Activation}$$

```
┌────────────────────────────────────────────────────────────────────────┐
│                        RUNTIME BIFURCATION                             │
│                                                                        │
│   LIVE RUNTIME (Default)               SIMULATION RUNTIME (--mode sim) │
│   • Starts background daemon threads   • Zero background daemon loops  │
│   • Binds to disk storage (data/)      • Ephemeral in-memory storage   │
│   • Live companion activation enabled  • Hard-blocked activation (403) │
│   • Normal turns via POST /process     • Isolated turns via POST /sim/chat │
└────────────────────────────────────────────────────────────────────────┘
```

* **Virtual Clock (`SimClock`)**: Replaces autonomous wall-clock loops with controllable, step-driven virtual time (`step`, `pause`, `resume`, `set_speed`, `reset`). Dispatches registered fast-tick callbacks (`EmotionCore.step_once`) and slow-tick callbacks (`DecayEngine.apply_decay_tick`).
* **Ephemeral Storage Policy (`StoragePolicy`)**: Replaces `data/chat_history.json` and `data/profile.json` with `InMemoryChatHistoryStore` and `InMemoryProfileStore`. `assert_write_permitted()` actively intercepts any attempt to write into protected directories.
* **Dual Stimulus Pathways**:
  1. *Sensory Pathway*: Text $\rightarrow$ `StimulusProcessor.encode()` $\rightarrow$ 16D vector $\rightarrow$ `EmotionCore` (labeled `pathway: "sensory_text"`).
  2. *Debug Vector Probe*: Raw 16D vector injected directly into `EmotionCore` bypassing the sensory processor (labeled `pathway: "debug_vector_probe"`).
* **Canonical Body UI Integration**: Simulation Canopy (`#simulation-canopy`) and Console drawer (`#simulation-console-drawer`) mount conditionally within the existing Phase 7 Personal Digital Room (`index.html`). No secondary companion interface is created.
