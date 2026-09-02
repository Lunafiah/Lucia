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
│  • 60 FPS Interactive Canvas Avatar with Web Audio Lip-Sync             │
└─────────────────────────────────────────────────────────────────────────┘
```

---

## 3. Detailed Component Deep-Dive

### 3.1. Layer 1: Stimulus Processor (`src/core/sensors/`)
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

### 3.3. Layer 3: Homeostatic Engine (`src/core/homeostasis/`)
Prevents emotional burnout, runaway anxiety, or manic states:
* **Metabolic Budgeting**: Depletes energy on heavy turns; recovers during idle periods.
* **Somatic Markers**: Computes Stability, Cognitive Load, Energy, and Tension.
* **Dynamic Parameter Conditioning**:
  * High Arousal $\rightarrow$ Shorter token budget (brisk replies), higher temperature.
  * High Tension $\rightarrow$ Increased reasoning depth ($k=2$).
  * Low Energy $\rightarrow$ Simulated conversational latency delay.

### 3.4. Layer 4: Active Inference & LNN Plasticity (`src/core/inference/`)
* **Active Inference Engine**: Maintains belief state matrices $A \in \mathbb{R}^{3 \times 3}, b \in \mathbb{R}^3$ predicting emotional transitions. Computes Free Energy / Prediction Surprise:
  $$\text{Surprise} = \|A \cdot p_{before} + b - p_{after}\|_2$$
* **LNN Trainer (CPU-only)**: Collects experience tuples `(stimulus, h_before, h_after)` in a ring buffer. A dedicated background CPU thread runs backpropagation-through-ODE (`torchdiffeq.odeint`) to adapt LNN weights without competing for GPU VRAM.

### 3.5. Layer 5: Affective Memory & Ecphory (`src/core/memory/`)
* **Kanerva Sparse Distributed Memory (SDM)**: $N=1,000$ distributed locations with 64-bit Hamming addresses and 16-bit content vectors.
* **Emotional Decay**: Traces decay exponentially; high-intensity emotional moments ($|PAD| \gg 0$) resist decay up to $4\times$ longer.
* **Synergistic Ecphory**: When Lucia enters an emotional state, the engine queries past traces and generates a subconscious **Echo Vector** that softly primes her prompt without quoting past memories mechanically.

### 3.6. Layer 6: Voice, Avatar & Embodied Presence
* **Direct RVC Voice Engine (`src/core/voice/`)**:
  * Loads `.pth` weights and `.index` feature files directly from `models/voice/rvc/`.
  * Synthesizes character speech on-demand with PAD-aware emotional pitch/speed modulation.
* **Electron Desktop Avatar (`electron/renderer/avatar/`)**:
  * **Expression Mapper**: Maps 500ms PAD telemetry to eyebrow angles, smile curves, eye openness, and cheek blushing.
  * **Web Audio LipSync**: Analyzes audio frequencies in real time at 60 FPS to open/close her mouth in sync with speech.
  * **Natural Physics**: Triple-frame eye blinks, gentle breathing idle loop, and cursor gaze tracking.

---

## 4. Concurrency & Threading Model

Lucia operates with 4 non-blocking concurrent daemon threads coordinated by thread-safe locks:

| Thread Name | Module | Cadence | Purpose | Lock Discipline |
|---|---|---|---|---|
| **`EmotionCore-FastLoop`** | Limbic Engine | 200ms | Solves continuous emotion ODE | Holds `_state_lock` (1ms), copies weights via `_train_lock` |
| **`DecayEngine-SlowLoop`** | Memory Store | 60s | Applies emotional memory decay | Holds `_index_lock` |
| **`LNN-Trainer`** | Online Plasticity | On Batch (16) | CPU Backpropagation-through-ODE | Holds `_train_lock` during weight swap ($\le 2\text{ms}$) |
| **`Uvicorn Async Loop`** | FastAPI Server | Event-driven | Serves `/process`, `/state`, `/voice/*` | Async non-blocking I/O |

---

## 5. Hardware Scalability & Optimization

Lucia features automated hardware detection (`HardwareTier`) to run smoothly across any PC specification:

| Hardware Tier | Detected Specs | Model Offload | Context Size | SDM Capacity | VRAM Usage |
|---|---|---|---|---|---|
| **`LAPTOP`** | $< 6\text{GB}$ VRAM (e.g. RTX 3050 Ti) | 32 GPU Layers (1.2B/3B) | 2,048 tokens | 500 traces | $\approx 1.5\text{GB}$ |
| **`DESKTOP`** | $6\text{GB} - 12\text{GB}$ VRAM (e.g. RTX 3060/4060) | Full GPU (3B/7B) | 4,096 tokens | 2,000 traces | $\approx 4.0\text{GB}$ |
| **`HIGH_END`** | $> 12\text{GB}$ VRAM (e.g. RTX 3090/4090) | Full GPU (7B/14B) | 8,192 tokens | 10,000 traces | $\approx 8.0\text{GB}$ |
