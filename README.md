# Lucia — Affective AI Companion

An embodied AI companion designed for emotional authenticity, continuous affective learning, and multi-device presence, built on a **Whole Brain Architecture** inspired by the human brain's efficient 20-watt processing model.

The core philosophy: **emotionally realistic behavior without reflective selfhood**. Emotion is not labeled or performed — it manifests as rhythm, tone, latency, and conversational depth through a continuous physiological-like state machine.

---

## Roadmap & Implementation Status

| Phase | Description | Status |
|---|---|---|
| **Phase 1: Core Pipeline** | Continuous Emotion ODE (`EmotionCore`), Homeostatic Engine, Stimulus Processing, Boundary Layer, GGUF LLM Backend | ✅ **Completed** |
| **Phase 2: Affective Memory** | Kanerva Sparse Distributed Memory (`SDMCore`), Affective Tagging (`AffectiveMemory`), Emotional Decay (`DecayEngine`), Synergistic Ecphory (`EcphoryEngine`) | ✅ **Completed** |
| **Phase 3: Desktop Interface** | Python FastAPI Backend (`POST /process`, `GET /state`), Native Electron Desktop App with Live 500ms Emotion Telemetry Panel, Adaptive Hardware Scaling | ✅ **Completed** |
| **Phase 4: Active Inference** | Short-horizon free energy minimization (`ActiveInferenceEngine`), Online backprop-through-ODE LNN plasticity (`LNNTrainer`, `torchdiffeq`), 10-step cognitive pipeline (`InferencePipelineOrchestrator`) | ✅ **Completed** |
| **Phase 5: Embodied Presence** | Screen & Camera Vision Perception (`Qwen2.5-VL 3B`), Voice Synthesis/Recognition (RVC / Kokoro), 2D/3D Avatar (Live2D / VRM), Desktop Agency | ⏳ *Next* |

---

## Emotional Foundation: *Philia* Friendship

Lucia is grounded in **Philia** ($\phi\iota\lambda\iota\alpha$)—the classical Greek concept of deep, affectionate, and egalitarian friendship based on mutual respect, intellectual curiosity, and shared growth:

* **Resting Baseline (Attractor)**: $P=+0.25$ (warmth), $A=-0.05$ (calm presence), $D=+0.05$ (equal peer).
* **Organic Emotional Growth**: Her internal state is never rigidly forced or scripted; her ODE dynamics freely shift in response to interactions, and her relationship crystallizes through accumulated emotional memory traces over time.

---

## 6-Layer Architecture

```
┌─────────────────────────────────────────────────────────────┐
│  LAYER 1: Sensors & Stimulus Processor                      │
│  Semantic valence, punctuation arousal & density encoding    │
├─────────────────────────────────────────────────────────────┤
│  LAYER 2: Limbic System — Fast Loop (EmotionCore ODE)       │
│  Liquid Neural Network for continuous emotional flow        │
│  Produces real-time 3D PAD state (Pleasure, Arousal, Dom.)  │
├─────────────────────────────────────────────────────────────┤
│  LAYER 3: Survival System — Mid Loop (Homeostasis)          │
│  Metabolic budgeting, cognitive load, energy & tension      │
│  Dynamically regulates token budget, temperature & latency  │
├─────────────────────────────────────────────────────────────┤
│  LAYER 4: Active Inference Engine (Phase 4)                 │
│  Short-horizon prediction error minimization                │
├─────────────────────────────────────────────────────────────┤
│  LAYER 5: Hippocampus — Slow Loop (SDM + Ecphory)           │
│  Sparse Distributed Memory co-encoded with PAD emotion tags │
│  Synergistic Ecphory for subconscious memory resonance      │
│  Slow-loop decay engine modulated by emotional intensity    │
├─────────────────────────────────────────────────────────────┤
│  LAYER 6: Expression & Safety Layer                         │
│  Local SLM (LFM2.5-1.2B GGUF with CUDA acceleration)        │
│  Pre-reflective PromptAssembler + BoundaryLayer filter      │
└─────────────────────────────────────────────────────────────┘
```

---

## Adaptive Hardware Scaling

Lucia automatically detects host hardware capabilities and adapts her resource footprint across tiers:

| Tier | Target Hardware | GPU Layers | Context Window | ODE Cadence | Memory Capacity |
|---|---|---|---|---|---|
| **Laptop Tier** | 4GB–6GB VRAM (e.g. RTX 3050 Ti) | 32 (Safe offload) | 4,096 tokens | 200 ms (5 Hz) | 10,000 traces (~5MB) |
| **Desktop Tier** | 8GB–12GB VRAM (e.g. RTX 4060/4070) | 45 (Full offload) | 8,192 tokens | 150 ms (6.7 Hz) | 50,000 traces |
| **High-End Tier** | 16GB+ VRAM (e.g. RTX 3090/4090) | 99 (Full offload) | 16,384 tokens | 100 ms (10 Hz) | 100,000+ traces |

---

## Quick Start & Installation

### 1. Environment Setup (Windows)

```bash
# Create and activate Python 3.12 virtual environment
py -3.12 -m venv .venv
.venv\Scripts\activate

# Install core dependencies
pip install fastapi "uvicorn[standard]" httpx numpy scipy pydantic

# Install CUDA-accelerated llama-cpp-python (RTX 3050 Ti / CUDA 12.4+)
.\build_llama_cuda.bat
```

### 2. Configure Desktop Settings & Assets

Ensure `config/ui.json` points to your local model and optional avatar/voice directories:

```json
{
  "port": 8765,
  "model_path": "models/LFM2.5-1.2B-Instruct-Q4_K_M.gguf",
  "voice_path": "models/voice/",
  "avatar_path": "assets/avatar/",
  "profile": "auto",
  "n_gpu_layers": 32,
  "log_level": "INFO"
}
```

### 3. Model & Avatar Assets Directory Layout

```
Lucia/
├── models/
│   ├── LFM2.5-1.2B-Instruct-Q4_K_M.gguf        # Active Language Model (GGUF)
│   └── voice/                                  # Local TTS Models (Kokoro / Piper ONNX)
└── assets/
    └── avatar/
        ├── live2d/                             # Live2D Cubism (*.model3.json, *.moc3)
        ├── vrm/                                # 3D VRM / VRoid (*.vrm)
        └── sprites/                            # 2D Emotion Sprite Sheets (*.png)
```

### 4. Launch Desktop Application

```bash
cd electron
npm install
npm start
```

*The application will automatically spawn the Python backend, awaken her continuous Fast Loop and Slow Loop, and display the Chat Window along with the Live 500ms Emotion Debug Panel.*

---

## Running Test Suites

```bash
# Run all Python Unit, Property (Hypothesis P1-P30), and Integration tests:
.venv\Scripts\pytest tests/unit tests/property tests/integration -v

# Run Electron desktop unit tests:
cd electron && npm test
```

---

## License

Private repository.