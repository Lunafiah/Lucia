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
|---|---|---|---|---|
| **`Cognitive Turn Mutex`** | Brain Core (`server.py`) | Per Turn | Serializes cognitive turn execution | Holds `asyncio.Lock` & `_turn_lock` during `process()` |
| **`EmotionCore-FastLoop`** | Limbic Engine | 200ms | Solves continuous emotion ODE | Holds `_state_lock` ($\le 1\text{ms}$), copies weights via `_train_lock` |
| **`DecayEngine-SlowLoop`** | Memory Store | 60s | Applies emotional memory decay | Holds `_index_lock` |
| **`LNN-Trainer`** | Offline Plasticity | Idle / Salience | CPU Backpropagation-through-ODE | Holds `_train_lock` during weight swap ($\le 2\text{ms}$) |
| **`SimClock Background`** | Simulation | Configurable | Virtual clock advancement when resumed | Dispatches synchronous callbacks; no autonomous loops |
| **`Uvicorn Async Loop`** | FastAPI Server | Event-driven | Serves `/process`, `/state`, `/sim/*`, `/voice/*` | Async non-blocking I/O (`/state` reads under `_state_lock`) |
| **`Electron Render Thread`**| UI / Avatar | 60 / 30 FPS | WebGL & Canvas avatar rendering | RequestAnimationFrame loop |


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
