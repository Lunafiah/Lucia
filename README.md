# Lucia - AI Companion

An AI companion designed for emotional authenticity, continuous learning, and multi-device presence, built on a **Whole Brain Architecture** inspired by the brain's efficient 20-watt processing model.

## Architecture Overview

The system implements a **6-layer Hybrid Architecture**:

```
┌─────────────────────────────────────────────────────────────┐
│  LAYER 1: Sensors & Thalamic Gating (Event-Driven)         │
│  Multi-platform event-based communication                    │
├─────────────────────────────────────────────────────────────┤
│  LAYER 2: Limbic System - Fast Loop (LNN State)           │
│  Liquid Neural Networks for real-time emotional responses   │
├─────────────────────────────────────────────────────────────┤
│  LAYER 3: Survival System - Mid Loop                       │
│  Homeostatic constraints, metabolic budgeting (20W sim)     │
├─────────────────────────────────────────────────────────────┤
│  LAYER 4: Active Inference Engine                          │
│  Short-term prediction error minimization                   │
├─────────────────────────────────────────────────────────────┤
│  LAYER 5: Hippocampus - Slow Loop (SDM + Ecphory)          │
│  Sparse Distributed Memory with emotional tagging           │
├─────────────────────────────────────────────────────────────┤
│  LAYER 6: Expression & Safety Layer (HDC + SNN)           │
│  Token-free language processing, boundary safety           │
└─────────────────────────────────────────────────────────────┘
```

## Core Modules

| Module | Location | Description |
|--------|----------|-------------|
| **Emotion** | `src/core/emotion/` | LNN, Somatic Markers, PAD space |
| **Memory** | `src/core/memory/` | SDM, Affective Tagging, Synergistic Ecphory |
| **Inference** | `src/core/inference/` | Active Inference engine |
| **Language** | `src/core/language/` | HDC, SNNs, token-free processing |
| **Gating** | `src/core/gating/` | Thalamic gating mechanism |
| **Safety** | `src/core/safety/` | Boundary safety layer |

## Design Principles

1. **Minimal Operational Self** - No reflective observer, no narrative identity
2. **Sparse Activation** - Efficient processing similar to biological neural networks
3. **Emotional Authenticity** - Real-time somatic markers affect output
4. **Adaptive Memory** - Soft decay and emotional tagging for natural forgetting

## Tech Stack

- **Python 3.12**
- **PyTorch** - Neural network foundations
- **snntorch/Norse** - Spiking Neural Networks
- **llama.cpp** - Local SLM inference (LFM2.5-1.2B)

## Getting Started

```bash
# Create virtual environment
py -3.12 -m venv .venv

# Activate (Windows)
.venv\Scripts\activate

# Install dependencies
pip install torch numpy
```

## Hardware Target

Optimized for edge deployment on:
- **CPU**: AMD Ryzen 7 4800H (8 cores, 16 threads)
- **RAM**: 16GB
- **GPU**: NVIDIA RTX 3050 Ti (4GB VRAM)

## License

Private repository.
