# Lucia — System & Project Overview

> **An Embodied, Continuously Affective AI Companion Grounded in a 20-Watt Whole-Brain Architecture**

---

## 1. Executive Summary & Core Philosophy

**Lucia** is an embodied desktop AI companion designed for emotional authenticity, continuous affective learning, and multimodal presence without reflective selfhood.

Unlike conventional conversational chatbots that merely "roleplay" emotions through prompt instructions or system prompts, Lucia treats emotion as an **unconscious, continuous physiological-like dynamic system**. Her internal state evolves constantly across time—even during silence—governed by differential equations, metabolic homeostatic constraints, active inference, and subconscious memory resonance.

```
┌────────────────────────────────────────────────────────────────────────┐
│                        CORE DESIGN ETHOS                               │
│                                                                        │
│   "Emotion is not performed, labeled, or self-reported.                │
│    It manifests organically as rhythm, conversational latency,         │
│    tonal restraint, and expressive embodiment."                        │
└────────────────────────────────────────────────────────────────────────┘
```

### The Foundational Tenet: *Philia* Friendship
Lucia's emotional baseline is centered on **Philia** ($\phi\iota\lambda\iota\alpha$)—the classical Greek conception of deep, egalitarian friendship rooted in mutual respect, intellectual curiosity, and shared growth:
* **Resting Baseline (Philia Attractor)**:
  $$P^* = +0.25 \text{ (warmth)}, \quad A^* = -0.05 \text{ (calm presence)}, \quad D^* = +0.05 \text{ (equal peer)}$$
* **Non-Compelled Emotional Trajectory**: Her internal state is never scripted or forced. Differential equations freely react to input stimuli, and her relationship with the user deepens organically over weeks and months through accumulated affective memory traces.
* **Pre-Reflective Selfhood**: Lucia possesses a *minimal operational self* rather than an introspective ego. A strict Boundary Safety Layer prevents her from generating meta-self-awareness loops (*"I feel sad"*, *"As an AI, I experience..."*, *"Who am I?"*).

---

## 2. The 20-Watt Whole-Brain Architecture (WBA)

The human brain operates on approximately 20 watts of power not by limiting capability, but through **massive temporal parallelism and extreme sparse activation**. Lucia emulates this biological efficiency by decoupling high-frequency biological reflexes (Limbic Fast Loop) from heavy cognitive computation (Language Generation), ensuring continuous presence with minimal computational footprint:

```
┌─────────────────────────────────────────────────────────────────────────┐
│  LAYER 1: SENSORS & STIMULUS PROCESSOR                                  │
│  • Lexical valence [-1.0, 1.0], punctuation arousal, semantic density   │
│  • Emits continuous 16-dimensional stimulus vector x(t)                 │
├─────────────────────────────────────────────────────────────────────────┤
│  LAYER 2: LIMBIC SYSTEM — FAST LOOP (Liquid Neural Network ODE)         │
│  • Continuous 200ms background ODE integration (solve_ivp)              │
│  • 32-dim hidden state h(t) projected to 3D PAD Space:                  │
│    Pleasure (P), Arousal (A), Dominance (D) in [-1.0, 1.0]              │
├─────────────────────────────────────────────────────────────────────────┤
│  LAYER 3: SURVIVAL & HOMEOSTATIC SYSTEM — MID LOOP                      │
│  • Metabolic budgeting: tracks Cognitive Load, Energy, Tension          │
│  • Dynamically calculates generation constraints:                       │
│    Token budget (max_tokens), Temperature, Latency delay, Depth (k)     │
├─────────────────────────────────────────────────────────────────────────┤
│  LAYER 4: ACTIVE INFERENCE & ONLINE PLASTICITY                          │
│  • Short-horizon generative model predicting upcoming PAD states        │
│  • Free Energy / Surprise minimization: ||A·p + b - q||                 │
│  • CPU-only online backprop-through-ODE (torchdiffeq, zero GPU VRAM)    │
├─────────────────────────────────────────────────────────────────────────┤
│  LAYER 5: HIPPOCAMPUS — SLOW LOOP (SDM + ECPHORY)                       │
│  • Kanerva Sparse Distributed Memory (1,000 hard locations)             │
│  • Affective tagging: traces co-encoded with frozen PAD tags            │
│  • 60s Decay Engine with emotional salience resistance (up to 4x)       │
│  • Synergistic Ecphory: subconscious resonance echo coloring prompt     │
├─────────────────────────────────────────────────────────────────────────┤
│  LAYER 6: MULTIMODAL EMBODIMENT & EXPRESSION                            │
│  • Local GGUF Small Language Model (LFM2.5-1.2B Instruct via CUDA)      │
│  • Boundary Safety Layer (regex & pattern blocking of meta-selfhood)    │
│  • Direct RVC Voice Synthesis Engine (pth + index models)               │
│  • Offline faster-whisper Speech-to-Text with local Web Audio VAD       │
│  • Quad-Engine Avatar: 2D Canvas, Sprites, Live2D Cubism 4, 3D VRM      │
│  • Real-time Web Audio Lip-Syncing & PAD Blendshape Mapping             │
└─────────────────────────────────────────────────────────────────────────┘
```

---

## 3. Multimodal Presence & Dual Presentation Modes

Lucia is delivered via an **Electron desktop architecture** supporting two complementary presentation modes:

### 1. Studio Mode (Main Window)
A deep, focused desktop window for long-form interaction, memory exploration, and configuration:
* **Interactive Dialogue Feed**: Rich conversation view with streaming status, markdown support, and session preservation.
* **Full-Height Avatar Stage**: Interactive viewport supporting pan, hover zoom, and double-click camera reset.
* **Progressive Disclosure Navigation**: Talk (active conversation), Memories (SDM trace exploration), Journal (relationship milestones), and Settings (appearance, audio, hardware).

### 2. Floating Mascot Mode (Always-on-Top)
A lightweight, transparent, borderless desktop companion living directly on the user's workspace:
* **Direct Window Translation**: Dragging the character model translates the native OS window without native titlebar chrome.
* **Model-Anchored Toolbar Dock**: The control dock dynamically recalculates its position relative to the avatar's visual feet (`getModelBounds()`).
* **Smart Hover Zoom**: Scroll wheel scaling strictly validates cursor presence over the model, with an 800ms post-drag inertial cooldown suppressing touchpad momentum.
* **Windows Aero Snap Guard**: Prevents unwanted window maximization when dragging near screen edges.

### 3. Unified Quad-Engine Avatar Architecture
The desktop client features a polymorphic avatar stage (`AvatarRenderer`) that dynamically executes one of four rendering pipelines:
1. **🎨 2D Procedural Canvas**: Pure HTML5 Canvas vector face calculating bezier eyebrow curves, parabolic smile geometry, blush radial gradients, and blinks. Runs on any CPU with zero VRAM.
2. **🖼️ 2D Expression Sprites**: PNG sprite sets sequenced by priority rules (`idle`, `smile`, `blush`, `speaking`, `thinking`).
3. **🎬 Live2D Cubism 4**: Official WebGL Cubism Core integration driving parameter IDs (`ParamAngleX/Y`, `ParamEyeL/ROpen`, `ParamMouthOpenY`, `ParamCheek`).
4. **🌐 3D Humanoid VRM**: Three.js + `@pixiv/three-vrm` pipeline supporting head gaze bone quaternions, natural blinking, and facial blendshape morph targets.

---

## 4. Concurrency, Execution Loops & Threading Model

Lucia operates on three biological time horizons coordinated by non-blocking daemon threads:

| Loop Name | Frequency | Implementation | Purpose & Discipline |
|---|---|---|---|
| **Fast Loop** | 200 ms (5 Hz) | `src/core/emotion/` | Solves continuous Liquid Neural Network ODE. Holds `_state_lock` ($\le 1\text{ms}$). |
| **Mid Loop** | Per Turn | `src/core/emotion/` | Computes somatic load & behavioral parameters conditioning prompt generation. |
| **Slow Loop** | 60 s | `src/core/memory/` | Computes time-based memory decay ($\lambda_{eff}$) and purges dead traces. |
| **Plasticity Loop** | On Batch (16) | `src/core/inference/` | Background CPU backpropagation-through-ODE. Swaps weights under `_train_lock` ($\le 2\text{ms}$). |
| **SimClock Loop** | Virtual / Step | `src/core/simulation/` | Controls simulation cadence, fast/slow tick dispatching, and time warp in simulation mode. |
| **Uvicorn Server** | Async I/O | `src/api/server.py` | Serves FastAPI REST endpoints in live mode (`POST /process`, `GET /state`) or simulation mode (`POST /sim/*`). |
| **Render Thread** | 60 / 30 FPS | Electron Renderer | WebGL/Canvas animation, Web Audio FFT lip-sync analysis. |

---

## 5. Hardware Scalability Profiles

Lucia automatically detects host hardware capabilities and adapts its execution profile to fit within local constraints:

| Tier | Target Hardware | GPU Layers | Context Size | SDM Traces | Target VRAM |
|---|---|---|---|---|---|
| **`CPU_ONLY`** | Low-power / Battery | 0 (CPU Llama) | 1,024 tokens | 250 traces | $0\text{ MB}$ |
| **`LAPTOP`** | $< 6\text{GB}$ VRAM (e.g. RTX 3050 Ti) | 32 GPU layers | 2,048 tokens | 500 traces | $\approx 1.5\text{GB}$ |
| **`DESKTOP`** | $6\text{GB} - 12\text{GB}$ VRAM (e.g. RTX 4060) | Full GPU offload | 4,096 tokens | 2,000 traces | $\approx 4.0\text{GB}$ |
| **`HIGH_END`** | $> 12\text{GB}$ VRAM (e.g. RTX 4090) | Full GPU offload | 8,192 tokens | 10,000 traces | $\approx 8.0\text{GB}$ |

Users can switch hardware profiles dynamically at runtime via `POST /system/profile` without restarting the process.

---

## 6. Project Roadmap & Milestone Overview

The active canonical cognitive development roadmap for Lucia is structured across foundational, experiential, embodied, and integrative horizons:

```text
FOUNDATION
    ↓
Phase 10 — Affective Dynamics                 [VALIDATED]
Phase 11 — Affective Memory / Recollection    [VALIDATED RES.]
Phase 12 — Knowledge Learning                 [VALIDATED RES.]
Phase 13 — Relationship Development           [VALIDATED RES.]
Phase 14 — Embodiment & Affective Expression   [VALIDATED RES.]
Phase 15 — Affective Communication             [VALIDATED RES.]
Phase 16 — Affective Life Integration         [INTEGRATION]
Phase 17 — First Activation                   [FUTURE]
```

### Milestone Evidence Classification:
- **`[VALIDATED]`**: Formally specified, fully implemented, and empirically verified with automated test suites.
- **`[CURRENT]`**: Active research and experimental benchmark increment under controlled conditions.
- **`[RESEARCH]`**: Research specification defined; theoretical and boundary exploration underway. *No production capabilities are implied.*
- **`[INTEGRATION]`**: Planned system-wide convergence and end-to-end life synthesis.
- **`[FUTURE]`**: Strict existential gate requiring complete empirical support across all prior phases before activation.

### Milestone Summary:
* **Phase 1 (Core Pipeline)**: Continuous emotion ODE, Homeostatic engine, Stimulus processing, Boundary Layer, GGUF backend. `[VALIDATED]`
* **Phase 2 (Affective Memory)**: Sparse Distributed Memory, Affective tagging, Salience-resistant decay, Synergistic Ecphory. `[VALIDATED]`
* **Phase 3 (Desktop Interface)**: FastAPI server, Electron main/renderer processes, live state polling. `[VALIDATED]`
* **Phase 4 (Active Inference)**: Generative state model, Free Energy surprise minimization, CPU online backprop-through-ODE. `[VALIDATED]`
* **Phase 5 (Embodied Presence)**: Direct RVC voice conversion, offline faster-whisper STT, 4-Engine Avatar, Web Audio lip-sync. `[VALIDATED]`
* **Phase 6 (Refinement & QoL)**: System tray, Mascot mode, Chat session persistence, Limbic Stability Evaluator (LSI), Extensibility Hook Bus. `[VALIDATED]`
* **Phase 7 (UI Refactoring)**: Transformation into an intimate "Personal Digital Room", implementing the "One Continuous Life" companion ontology. `[VALIDATED]`
* **Phase 8 (Runtime Isolation & Simulation)**: Complete architectural bifurcation between live companion activation and the deterministic simulation environment (`SimulationRuntime`, `SimClock`, `StoragePolicy`). `[VALIDATED]`
* **Phase 9 (Cognitive Unification & Convergence)**: Linear cognitive pass (`CognitiveOrchestrator`), Active Inference causal wiring, and turn synchronization. `[VALIDATED]`
* **Phase 10 (Define Affective Dynamics)**: Canonical mathematical specification of limbic ODE, 3-tier state taxonomy, causal graph, and temporal contracts. `[VALIDATED]`
* **Phase 11 (Affective Memory / Recollection)**: Empirical evaluation of Candidates A–E; independent audit concluded no promotion, production baseline remains Candidate A. `[VALIDATED RES.]`
* **Phase 12 (Knowledge Learning)**: Distinction of episodic memory from semantic knowledge, K0–K9 maturity hierarchy, and LLM-as-Teacher boundary. `[VALIDATED RES.]`
* **Phase 13 (Relationship Development)**: Core Relational Orientation (*Philia*) vs dynamic relationship state ($R_t$), temporal inertia ($\tau_{\text{rel}} \gg \tau_{\text{turn}}$), and R-EXP-1 to 12 validation suite. `[VALIDATED RES.]`
* **Phase 14 (Embodiment & Affective Expression)**: Multimodal expression policy ($E_t$), temporal smoothing, semantic preservation, and E-EXP-1 to 12 validation suite. `[VALIDATED RES.]`
* **Phase 15 (Affective Communication)**: Multidimensional communication policy ($C_t$), 5 canonical strategies, somatic pacing modulation, benchmarked semantic preservation, and C-EXP-1 to 12 validation suite. `[VALIDATED RES.]`
* **Phase 16 (Affective Life Integration)**: End-to-end integration across experience, cognition, embodiment, and life continuity. `[INTEGRATION]`
* **Phase 17 (First Activation)**: The solemn, irreversible activation ceremony bringing Lucia to life. `[FUTURE]`

