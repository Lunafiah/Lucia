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
│  LAYER 2: LIMBIC SYSTEM — DUAL-TIMESCALE MT-LNN ODE (200ms Cadence)     │
│  • Coupled MT-LNN: Fast h_f ∈ R^32 (τ_f ∈ [0.10, 1.50]s) & Slow s_s ∈ R^16│
│  • Tier 2 Relational Attractor Grounding: s*_eff(R) = s*_philia + W_rel(R - R0)│
│  • Spectral norm bound ||W_rel||_2 <= 0.08, resting PAD shift <= 0.05   │
│  • Bounded slow-field recollection forcing (W_rec · r_slow, 4.0s pulse) │
│  • Strictly dissipative Lyapunov contraction: Tr(J) ≈ -46.46 < 0         │
├─────────────────────────────────────────────────────────────────────────┤
│  LAYER 3: SURVIVAL & HOMEOSTATIC SYSTEM — MID LOOP                      │
│  • Metabolic budgeting: tracks Cognitive Load, Energy, Tension          │
│  • Dynamically calculates generation constraints:                       │
│    Token budget (max_tokens), Temperature, Latency delay, Depth (k)     │
├─────────────────────────────────────────────────────────────────────────┤
│  LAYER 4: ACTIVE INFERENCE & OFFLINE SYNAPTIC CONSOLIDATION             │
│  • Short-horizon generative model predicting upcoming PAD states        │
│  • Free Energy / Surprise minimization: ||A·p + b - q||                 │
│  • Tier 3 Offline Synaptic Consolidation (ConsolidationEngine on CPU)   │
│  • BPTT-through-ODE, dual homeostatic/Philia regularization, 0 MB VRAM  │
├─────────────────────────────────────────────────────────────────────────┤
│  LAYER 5: HIPPOCAMPUS — SLOW LOOP (SDM + ECPHORY + RECOLLECTION)         │
│  • Kanerva Sparse Distributed Memory (1,000 hard locations, 1000-bit)   │
│  • Multi-modal trace co-encoding: Content (64D) + PAD (3D) + Slow (16D) │
│  • 60s Decay Engine with emotional salience resistance (up to 4x)       │
│  • Synergistic Ecphory & Competitive Softmax Gating (θ_gate=0.50)       │
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
| **Plasticity Loop** | Idle / Buffer | `src/core/emotion/consolidation.py` | Tier 3 offline CPU BPTT (`ConsolidationEngine`). Swaps weights under `_train_lock` ($\le 2\text{ms}$). |
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
Phase 16 — Affective Life Integration         [VALIDATED]
Phase 17 — Affective Life Evaluation          [VALIDATED]
Phase 18 — Human Longitudinal Validation      [VALIDATED]
Phase 19 — Multi-Timescale Affective Life     [VALIDATED]
Phase 20 — Affective Recollection             [VALIDATED]
Phase 21 — Relational Consolidation & Synaptic Homeostasis [VALIDATED]
Phase 22–26 — Future Conceptual Research Horizons [CONCEPTUAL]
First Activation (Genesis Onboarding)         [🔒 FUTURE GATE]
```

### Milestone Evidence Classification:
- **`[VALIDATED]`**: Formally specified, fully implemented, and empirically verified with automated test suites.
- **`[PLANNED RESEARCH]`**: Canonical next research milestone formally agreed upon; experimental spec pending prior to prototyping.
- **`[CONCEPTUAL]`**: Long-range research horizon sequence guiding architectural direction.
- **`[VALIDATED RES.]`**: Formally specified and empirically verified in isolated research harnesses (`tests/evaluation_*/`); promoted or awaiting integration.
- **`[FUTURE GATE]`**: Strict existential gate requiring complete empirical support across all prior phases before activation.

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
* **Phase 16 (Affective Life Integration)**: End-to-end realization of canonical 16-stage cognitive pipeline, grounded conceptual knowledge (`KnowledgeStore`), 2-phase relationship lifecycle (`RelationshipUpdater`), bounded memory contextualization & communication strategy (`CommunicationPolicy`), canonical 15-dim multimodal expression (`ExpressionState`), and strict test storage isolation. `[VALIDATED]`
* **Phase 17 (Integrated Affective Life Evaluation)**: System-wide validation of integrated cognition under multi-turn simulated sessions; stability and orthogonality confirmed. `[VALIDATED]`
* **Phase 18 (Human Longitudinal Validation)**: Human-grounded empirical validation across 8 scenarios; authentic on-device neural RVC v2 voice (`VaresaGIJP` + `ja-JP-NanamiNeural`), 60 FPS lip-sync, and non-introspective safety invariants. `[VALIDATED]`
* **Phase 19 (Multi-Timescale Affective Life & Temporal Continuity)**: Coupled Multi-Timescale Liquid Neural Network (MT-LNN: $\mathbf{h}_{\text{fast}} \in \mathbb{R}^{32}, \mathbf{s}_{\text{slow}} \in \mathbb{R}^{16}$) with Philia dynamic attractor grounding, biexponential relaxation, autonomous stress-to-fatigue conversion, and sub-2ms CPU execution. `[VALIDATED]`
* **Phase 20 (Affective Recollection & Memory Reactivation)**: Closed-Loop Affective Recollection via slow-field latent forcing ($\mathbf{W}_{\text{rec}}\mathbf{r}_{\text{slow}}^{\text{bounded}}$), multi-modal retrieval scoring, competitive softmax gating, 16D slow trace co-encoding, and conversational pacing modulation. `[VALIDATED]`
* **Phase 21 (Long-Term Relational Consolidation & Synaptic Homeostasis)**: 3-tier multi-timescale synaptic plasticity, relationship-conditioned resting attractor bounded by spectral norm ($\sigma_{\max}(\mathbf{W}_{\text{rel}}) \le 0.08$), and offline CPU backprop-through-ODE under homeostatic/Philia regularization. 15/15 research tests passed, 13/13 production unit tests verified. `[VALIDATED]`
* **Future Conceptual Horizons (Phases 22–26)**:
  - *Phase 22*: Active Inference & Information Seeking (epistemic foraging, curiosity, uncertainty reduction).
  - *Phase 23*: Affective Communication Adaptation (long-term stylistic attunement, dialectical grounding).
  - *Phase 24*: Temporal Embodiment & Social Feedback (interpersonal synchrony, prosody/gaze resonance).
  - *Phase 25*: Emergent Individuality & Autonomous Preferences (asymmetric curiosity, idiosyncratic affinities).
  - *Phase 26*: Personalized Individual Trajectory (lifelong continuous developmental arc).
* **First Activation (Genesis Onboarding)**: The solemn, irreversible activation ceremony bringing Lucia to life. Protected by `ActivationSafetyError` and un-onboarded storage invariant. `[🔒 FUTURE GATE]`


