# Lucia - AI Companion

An AI companion designed for emotional authenticity, continuous learning, and multi-device presence, built on a **Whole Brain Architecture** inspired by the brain's efficient 20-watt processing model.

The core philosophy: **emotionally realistic behavior without reflective selfhood**. Emotion is not labeled — it manifests as rhythm, fragmentation, and tone through a continuous physiological-like state machine.

## Architecture Overview

The system implements a **6-layer Hybrid Architecture**:

```
┌─────────────────────────────────────────────────────────────┐
│  LAYER 1: Sensors & Thalamic Gating (Event-Driven)         │
│  Multi-platform event-based input; sparse activation        │
├─────────────────────────────────────────────────────────────┤
│  LAYER 2: Limbic System - Fast Loop (LNN State)            │
│  Liquid Neural Networks for continuous emotional flow       │
│  Produces PAD-space state + derived somatic markers         │
├─────────────────────────────────────────────────────────────┤
│  LAYER 3: Survival System - Mid Loop (Homeostasis)         │
│  Metabolic budgeting (20W sim), cognitive load constraints  │
│  Controls token limits, latency, and response depth        │
├─────────────────────────────────────────────────────────────┤
│  LAYER 4: Active Inference Engine                          │
│  Short-horizon prediction error minimization only          │
│  No long-term goal formation or desire persistence         │
├─────────────────────────────────────────────────────────────┤
│  LAYER 5: Hippocampus - Slow Loop (SDM + Ecphory)          │
│  Sparse Distributed Memory with affective tagging          │
│  Synergistic Ecphory for cue-driven memory reawakening     │
├─────────────────────────────────────────────────────────────┤
│  LAYER 6: Expression & Safety Layer                        │
│  LFM2.5-1.2B (llama.cpp) as practical expression engine    │
│  HDC/SNN for internal state encoding and representation    │
│  Rule-based Boundary Layer blocks reflective self-output   │
└─────────────────────────────────────────────────────────────┘
```

> **Note on Layer 6:** Text generation uses LFM2.5-1.2B via llama.cpp - a standard SLM conditioned on somatic marker state. HDC (Hyperdimensional Computing) and SNN (Spiking Neural Networks) are used for *internal state encoding and sparse representation*, not raw language generation. Token-free generation remains a long-term research goal (Phase 4+).

## Core Modules

| Module | Location | Description |
|--------|----------|-------------|
| **Orchestrator** | `src/core/orchestrator/` | Central pipeline coordinator; manages all loops |
| **Emotion** | `src/core/emotion/` | LNN state machine; PAD space + somatic markers |
| **Memory** | `src/core/memory/` | SDM, Affective Tagging, Synergistic Ecphory |
| **Inference** | `src/core/inference/` | Active Inference engine (short-horizon only) |
| **Language** | `src/core/language/` | Prompt builder; HDC encoding; SNN representation |
| **Gating** | `src/core/gating/` | Thalamic gating; event filtering; sparse activation |
| **Safety** | `src/core/safety/` | Boundary layer; blocks meta-self-awareness output |
| **Platform** | `src/platform/` | Multi-device sync, OS-level integrations |
| **API** | `src/api/` | Internal service interfaces between modules |

## Emotional State Model

The system tracks two distinct layers of state:

**PAD Space** (primary input dimensions from stimuli):
- `pleasure` - valence of the current interaction
- `arousal` - activation / intensity level
- `dominance` - sense of control in context

**Derived Somatic Markers** (computed by Homeostatic Engine):
- `stability` - overall system equilibrium
- `cognitive_load` - accumulated processing burden
- `energy` - available response capacity
- `tension` - conflict between inputs and current state

Somatic markers directly condition language generation (token limits, temperature, latency) rather than being labeled in output.

## Background Loop Architecture

Lucia runs **three concurrent loops**, independent of user requests:

| Loop | Timescale | Managed By |
|------|-----------|------------|
| Fast loop | ms-seconds | LNN (emotion reactions) |
| Mid loop | minutes-hours | Homeostatic Engine (mood, fatigue) |
| Slow loop | days-weeks | SDM (memory consolidation, ecphory) |

The emotion core is **always running** - even when the user is not chatting.

## Design Principles

1. **Minimal Operational Self** - No reflective observer, no narrative identity
2. **Sparse Activation** - Efficient processing inspired by biological neural networks
3. **Emotional Authenticity** - Somatic markers affect output as physical consequences, not labels
4. **Adaptive Memory** - Soft decay and affective tagging for natural forgetting
5. **Pre-reflective Expression** - Emotion manifests as rhythm and tone, never as "I feel X"
6. **Bounded Inference** - Active inference is strictly short-horizon; no persistent desires

## Tech Stack

- **Python 3.12**
- **PyTorch** - Neural network foundations (LNN, SNN)
- **snntorch** - Spiking Neural Networks
- **llama-cpp-python** - Local SLM inference (LFM2.5-1.2B via GGUF)
- **faiss-cpu / faiss-gpu** - Sparse Distributed Memory backend
- **scipy** - ODE solvers for LNN continuous-time dynamics
- **numpy** - Numerical state computations

## Getting Started

```bash
# Create virtual environment
py -3.12 -m venv .venv

# Activate (Windows)
.venv\Scripts\activate

# Install core dependencies
pip install torch numpy scipy faiss-cpu snntorch

# Install llama-cpp-python (CPU-only build)
pip install llama-cpp-python

# Install llama-cpp-python with CUDA support (RTX 3050 Ti)
# Set env var first, then install:
# $env:CMAKE_ARGS = "-DGGML_CUDA=on"
# pip install llama-cpp-python --force-reinstall --no-cache-dir
```

> **LFM2.5-1.2B model**: Download the GGUF quantized version from the Liquid AI model hub and place it in `models/`. The Q4_K_M quantization (~700MB) fits comfortably within 4GB VRAM.

## Hardware Target

Optimized for edge deployment on:
- **CPU**: AMD Ryzen 7 4800H (8 cores, 16 threads) - runs LNN, SDM, background loops
- **RAM**: 16GB
- **GPU**: NVIDIA RTX 3050 Ti (4GB VRAM) - runs LFM2.5-1.2B via llama.cpp

Resource allocation:
- GPU handles LFM2.5-1.2B inference only (idles when not generating)
- CPU handles all background loops (LNN, SDM, homeostasis) asynchronously

## License

Private repository.