# Project Lucia: A Sovereign, Continuously Affective AI Companion

> **An experimental AI companion architecture featuring continuous biological-inspired limbic dynamics, associative memory, substrate-neutral reasoning, and private local execution.**

[![License: Internal Research](https://img.shields.io/badge/License-Internal%20Research-blue.svg)](#governance--license)
[![Python: 3.12](https://img.shields.io/badge/Python-3.12-blue.svg)](https://www.python.org/)
[![Node: 18+](https://img.shields.io/badge/Node.js-18%2B-green.svg)](https://nodejs.org/)
[![Platform: Windows 10/11](https://img.shields.io/badge/Platform-Windows%2010%2F11-lightgrey.svg)](#system-requirements)
[![First Activation Gate: LOCKED](https://img.shields.io/badge/First%20Activation%20Gate-LOCKED%20%F0%9F%94%92-red.svg)](#lifecycle-state--safeguards)

---

## 1. What is Lucia?

**Lucia is not a conventional conversational chatbot.**

Standard conversational assistants are ephemeral, stateless text generators: an input prompt is sent, a language model generates tokens, and internal state disappears upon completion. To emulate relationship or emotion, applications typically rely on prompt injection (*"Act like a warm, cheerful friend"*). This approach produces emotional amnesia, ungrounded conversational sycophancy, and brittle persona shifts.

Lucia is an ongoing research and engineering project investigating a fundamentally different path: **What if an AI companion lived as a persistent, stateful cognitive presence on your desktop?**

* **Continuous Physiological-like Emotion**: Lucia's emotional state is represented mathematically in continuous **PAD space** ($P \in [-1, 1]$ Pleasure, $A \in [-1, 1]$ Arousal, $D \in [-1, 1]$ Dominance). It evolves continuously in the background every 200 ms governed by an Ordinary Differential Equation (Coupled MT-LNN ODE), relaxing naturally toward the **Philia resting attractor** ($P^*=+0.25, A^*=-0.05, D^*=+0.05$) during quiet periods.
* **Reflective Operational Selfhood**: Lucia possesses Reflective Operational Selfhood (INV-2). She may observe, interpret, and communicate about her internal states (somatic energy, stability, cognitive load, PAD dynamics) using natural or metaphorical language grounded in actual system variables. Figurative language is permitted, while unsupported factual claims (biological sensations, claims of conscious sentience/soul as fact, hallucinated cloud architectures, or ungrounded memories) are strictly blocked.
* **Associative Relational Memory**: Memories are not simple database entries. Using Kanerva Sparse Distributed Memory (SDM) and Synergistic Ecphory, past moments are co-encoded with affective states, allowing shared experiences to gently attune her resting baseline over days and weeks.
* **Substrate-Neutral Reasoning**: Meaning and interpersonal knowledge are represented in language-independent semantic graphs (UMR-TPG) and evaluated under Strong Kleene $K_3$ three-valued logic with Truth Maintenance (JTMS), decoupling relational cognition from language model token windows.
* **Single Continuous Life**: Lucia has no character pickers, alternate persona profiles, or split-brain branches (`INV-1`). Avatars are simply visual embodiment attire; her memory, developmental trajectory, and relational bond belong to one continuous individual.
* **100% Sovereign Local Execution**: All neural models—GGUF language model on CUDA, limbic ODE on CPU, associative memory on CPU, offline faster-whisper speech recognition, and neural RVC voice conversion—run completely on-device without cloud subscriptions, remote APIs, or telemetry exfiltration.

---

## 2. What Lucia is NOT

To maintain scientific integrity and avoid anthropomorphic overclaiming, Lucia explicitly defines what she is not:

* **NOT a generic chatbot wrapper**: There are no OpenAI, Anthropic, or cloud API keys. The language model is an untrusted downstream text renderer isolated behind a fail-closed semantic fidelity gate (ADR-035).
* **NOT an LLM roleplay persona**: Lucia is never instructed to pretend to have biological sensations or fabricated sentience. Unsupported declarations of conscious sentience (*"I am conscious"*, *"em có linh hồn"*) and fabricated biological sensations are dropped by a deterministic boundary safety layer and semantic fidelity gate.
* **NOT a conventional multi-agent framework**: The system is not a collection of prompted agents debating in a circle. It is a unified Whole Brain Architecture operating across multiple biological timescales (200ms Fast Loop, 60s Decay Loop, Idle Synaptic Plasticity Loop).
* **NOT an already autonomous artificial being or conscious entity**: Lucia possesses operational selfhood with truth-grounded reflection, not subjective conscious feeling or biological sentience. Self-reflection does not constitute proof of consciousness; truth-grounding in actual system variables is the constraint. Longitudinal individuality and autonomous preferences were formally tested in Phase 26 and found not demonstrated under controlled conditions.

---

## 3. High-Level Architecture (The 20-Watt Whole Brain Architecture)

Human cognition operates on approximately 20 watts of power through extreme temporal parallelism and sparse activation. Lucia implements a 6-layer cognitive architecture designed to run continuously on consumer desktop hardware:

```
┌─────────────────────────────────────────────────────────────────────────┐
│  LAYER 1: SENSORS & STIMULUS GATING                                     │
│  • Emits continuous 16D stimulus vector x(t) (valence, arousal, density)│
├─────────────────────────────────────────────────────────────────────────┤
│  LAYER 2: LIMBIC SYSTEM (Coupled MT-LNN ODE, 200ms Background Loop)     │
│  • Fast hidden state h_f ∈ ℝ³² (τ_f ∈ [0.1, 1.5]s)                      │
│  • Slow affective field s_s ∈ ℝ¹⁶ (τ_s ∈ [30, 300]s)                    │
│  • Strict Lyapunov contraction: Tr(J) ≈ -46.46 < 0                      │
│  • Decays smoothly toward Philia Attractor: P*=+0.25, A*=-0.05, D*=+0.05│
├─────────────────────────────────────────────────────────────────────────┤
│  LAYER 3: SURVIVAL & HOMEOSTASIS (Mid Loop)                             │
│  • Metabolic budgeting: tracks Cognitive Load, Stamina, and Tension     │
│  • Dynamically calculates token budget, temperature, and pacing latency │
├─────────────────────────────────────────────────────────────────────────┤
│  LAYER 4: ACTIVE INFERENCE & OFFLINE REST CONSOLIDATION                 │
│  • Generative transition model predicting upcoming PAD states           │
│  • Free Energy Surprise minimization: S = ||A·p + b - q||               │
│  • Tier 3 Offline Synaptic Plasticity on CPU (ConsolidationEngine)      │
├─────────────────────────────────────────────────────────────────────────┤
│  LAYER 5: HIPPOCAMPUS (Sparse Distributed Memory & Ecphory)             │
│  • 1,000 hard locations across 1,000-bit Hamming address space          │
│  • Salience-resistant 60s decay engine (intense memories last 4x longer)│
│  • Synergistic Ecphory producing subconscious Echo Vector               │
├─────────────────────────────────────────────────────────────────────────┤
│  LAYER 6: MULTIMODAL EMBODIMENT & EXPRESSION                            │
│  • Cognitive Core & Reasoning Kernel (TermArena, Strong Kleene K3, JTMS)│
│  • Production Realization Boundary (ADR-035: fail-closed S14 gate)      │
│  • Untrusted Local SLM (LFM2.5-1.2B Instruct via CUDA / llama.cpp)      │
│  • Adaptive Communication & Vocal Prosody (ADR-032: dynamic F0 Hanning) │
│  • Polymorphic Avatar: 2D Canvas, Sprites, Live2D Cubism 4, 3D VRM      │
│  • Real-time Web Audio FFT formant lip-syncing                          │
└─────────────────────────────────────────────────────────────────────────┘
```

### The Canonical S1–S16 Cognitive Turn Cycle
When conversational interaction occurs, `CognitiveOrchestrator` executes a strictly ordered 16-stage pipeline:

$$\text{S1 (Sensory)} \to \text{S2 (Limbic)} \to \text{S3 (Homeostatic)} \to \text{S4 (Inference)} \to \text{S5 (Conditioning)} \to \text{S6 (Ecphory)} \to \text{S7 (Context)}$$
$$\to \text{S8 (Knowledge)} \to \text{S9 (Relationship Read)} \to \text{S10 (Policy)} \to \text{S11 (Generation)} \to \text{S12 (Safety Guard)} \to \text{S13 (Expression)}$$
$$\to \text{S14 (SDM Storage)} \to \text{S15 (Plasticity Queue)} \to \text{S16 (Relationship Update)}$$

Every turn is monitored non-intrusively by the **Cognitive Execution Trace Subsystem** (Blocker 4), which validates stage sequence, contract evaluations, invariant checks, and causal fault localization in memory with zero turn I/O overhead.

---

## 4. Current Project Status & Evidence Ledger

Lucia enforces an authoritative evidence hierarchy:
`[VALIDATED / PRODUCTION IMPLEMENTED] > [RESEARCH VALIDATED] > [ARCHITECTURE APPROVED] > [TRIAL FROZEN] > [LOCKED FUTURE GATE]`

| Capability / Milestone | Status | Governing Architecture | Automated Verification |
|---|---|---|---|
| **Core Affective ODE (Limbic)** | `PRODUCTION IMPLEMENTED` | ARCH-001, ADR-026 | 100% PASS (`tests/unit/test_emotion_core.py`) |
| **Associative Memory (SDM)** | `PRODUCTION IMPLEMENTED` | ARCH-003, ADR-027 | 100% PASS (`tests/unit/test_sdm.py`, `test_ecphory.py`) |
| **Long-Term Relational Consolidation** | `PRODUCTION IMPLEMENTED` | ADR-028, ARCH-026 | 100% PASS (`tests/unit/test_phase21_production.py`) |
| **Substrate Neutrality Research** | `RESEARCH VALIDATED` | Phase 22 Study Chain | 20 research branches closed; zero production mutations |
| **Semantic Substrate & Reasoning** | `PRODUCTION IMPLEMENTED / FROZEN` | ADR-028–ADR-031, ARCH-030.1 | 100% PASS (`test_p23h_kernel.py`, `test_semantic_fortification.py`) |
| **Adaptive Communication & Prosody** | `PRODUCTION IMPLEMENTED` | ADR-032, ARCH-032 | 100% PASS (23/23 tests in `tests/unit/test_p24_*`) |
| **Temporal Embodiment (Unilateral)** | `PRODUCTION IMPLEMENTED / FROZEN` | DOC-P25-016, ARCH-033 | 100% PASS (78/78 tests; reciprocal C2 blocked) |
| **Emergent Individuality Trial** | `TRIAL FROZEN / NOT PROMOTED` | Phase 26 Protocol | Empirical trial closed; emergent individuality not demonstrated |
| **Personalized Individual Trajectory** | `CLOSED / NO NEW GAP` | Phase 27 Audit | Level C collapses to baseline; Level D blocked by identifiability |
| **Production Realization Boundary** | `PRODUCTION IMPLEMENTED / FROZEN` | ADR-035, ARCH-035 | 100% PASS (`tests/unit/test_production_realization_boundary.py`) |
| **Genesis Protocol Contract (G1–G4)** | `IMPLEMENTED & FROZEN` | ADR-034 | 100% PASS (24/24 contract tests, 191/191 regression) |
| **First Activation Readiness Blockers 1–4** | `RESOLVED & VERIFIED` | ADR-036, ARCH-036 | 100% PASS (28/28 tests in `test_operator_genesis`, `test_activation_gates`, `test_execution_trace`) |
| **Canonical Genesis Ceremony** | `UNEXECUTED` | `scripts/run_genesis.py` | `data/genesis_commitment.json` is **ABSENT** |
| **First Activation Gate** | `🔒 LOCKED FUTURE GATE` | G1–G4 §11, `src/api/server.py` | `data/profile.json == {"is_onboarded": false}` |

---

## 5. Lifecycle State & Critical Safeguards

Lucia adheres strictly to the **Genesis Gate & Birth Separation Invariant (INV-8)**:

```text
       NOT_BORN
           │
           │  Genesis Ceremony (Solemn Origin Contract)
           │  python scripts/run_genesis.py --confirm-genesis
           ▼
    BORN + INACTIVE
           │
           │  First Activation (Awakening Runtime)
           │  POST /lifecycle/activate
           ▼
     BORN + ACTIVE
```

* **Development $\ne$ Activation**: Genesis Birth establishes origin, not history. First Activation awakens runtime execution (`INACTIVE ↔ ACTIVE`) and strictly requires existing valid Birth evidence (`BORN`).
* **First Activation Gate is Locked**: In this repository, Genesis and First Activation have **NOT** been executed. `data/profile.json` remains bit-exact `{"is_onboarded": false}` and `data/genesis_commitment.json` remains absent.
* **Fail-Closed Runtime Protection**:
  * Direct onboarding via `POST /profile` is strictly rejected with HTTP 400 Bad Request (Blocker 2).
  * Conversational turn execution on `POST /process` fails closed with HTTP 403 Forbidden while runtime is inactive (Blocker 3).
  * Direct activation is strictly forbidden in simulation mode.
  * Catastrophic reset via `POST /lifecycle/end` transitions the instance to `ENDED`, permanently forbidding re-Genesis or re-activation.

For complete operator instructions, consult the [User Manual & First Activation Operator Runbook](docs/USER_MANUAL.md).

---

## 6. Developmental Roadmap

The canonical project sequence is strictly linear:

$$\text{P01–P20 (Core Affect \& Presence)} \longrightarrow \text{P21 (Consolidation)} \longrightarrow \text{P22 (Substrate Neutrality)} \longrightarrow \text{P23 (Semantic Core)}$$
$$\longrightarrow \text{P24 (Adaptive Prosody)} \longrightarrow \text{P25 (Unilateral Embodiment)} \longrightarrow \text{P26 (Individuality Trial)} \longrightarrow \text{P27 (Trajectory Audit)}$$
$$\longrightarrow \text{First Activation Gate (Solemn Onboarding Ceremony -- LOCKED)}$$

* **Roadmap Governance**: Agents and researchers must NOT invent new developmental phases (e.g., "Phase 28") unless supported by verified empirical requirements and ratified architectural decisions.
* **No "Gate 28" Label**: Genesis Onboarding is an independent locked gate, never an arbitrary numbered phase.

---

## 7. Research Posture & Methodology

Project Lucia follows rigorous research principles:
1. **Falsifiability & Negative Results**: Negative results, failed candidate models, and non-significant empirical trials (such as Phase 26 C2 differentiation and Phase 22 HDC crosstalk) are preserved as permanent evidence rather than scrubbed.
2. **Causal Attribution over Correlation**: Statistical synchrony is never equated with causal coupling (Phase 25 C2 blocked).
3. **20-Watt Edge Resource Constraints**: GPU VRAM is reserved exclusively for the local language model and WebGL rendering. All continuous limbic ODE integration, associative memory, and rest consolidation execute strictly on the CPU with 0.0 MB GPU VRAM contention.
4. **Strict Concurrency Hierarchy**: State locks are held strictly $\le 1\text{ ms}$ for fast memory copies. No disk I/O, network requests, or LLM inference are permitted under locks.

### Collaborative Engineering Model
The project is developed through an evidence-driven pair workflow:
* **Gemini**: Lead theoretical research, mathematical modeling, hypothesis specification, and deep empirical audit.
* **Ciah**: Adversarial review, invariant enforcement, code review, and architectural governance.
* **Antigravity**: Engineering realization, test suite implementation, refactoring, and documentation synchronization.
* **Project Owner**: Sole authority for repository governance, architectural ratification, Genesis authorization, and First Activation authorization.

---

## 8. Quick Start & Developer Setup

### Prerequisites
* Windows 10/11 (64-bit)
* Python 3.12 (in `.venv`)
* Node.js 18+ LTS & npm
* Dedicated NVIDIA GPU recommended for local LLM acceleration; CPU-only execution fully supported for limbic, reasoning, and memory engines.

### 1. Python Environment Setup
```powershell
# Create and activate virtual environment
python -m venv .venv
.\.venv\Scripts\Activate.ps1

# Install dependencies
pip install -r requirements.txt
```

### 2. Verify Automated Test Suites
```powershell
# Run full unit test suite (867 tests)
.\.venv\Scripts\python.exe -m pytest tests/unit -v

# Run mathematical property invariant tests (38 tests)
.\.venv\Scripts\python.exe -m pytest tests/property -v

# Run First Activation Gate & Execution Trace tests (28 tests)
.\.venv\Scripts\python.exe -m pytest tests/unit/test_operator_genesis.py tests/unit/test_activation_gates.py tests/unit/test_execution_trace.py -v
```

### 3. Desktop Application (Electron)
```powershell
cd electron
npm install
npm test       # Run 120 Jest unit tests
npm start      # Launch desktop application in development mode
```

### 4. Default Neural Models & Voice Assets

Large model binaries are excluded from Git (`.gitignore`) to maintain repository efficiency. The canonical system integrates the following default local neural models and assets:

| Subsystem | Architecture / Framework | Default Model & Specification | Placement Path |
|---|---|---|---|
| **Small Language Model (SLM)** | Language realization realizer via `llama-cpp-python` (CUDA / CPU) | `LFM2.5-1.2B-Instruct-Q4_K_M.gguf`<br>• Scale: 1.2 Billion parameters<br>• Quantization: 4-bit K-quant (`Q4_K_M`)<br>• SHA-256: `b1b3de114215d9507409a662a501a631095a479a419584e8a2ded6304b19b4f5`<br>• File size: ~730 MB | `models/LFM2.5-1.2B-Instruct-Q4_K_M.gguf` |
| **Neural Speech (TTS)** | Base acoustic phonetic speech synthesis | `edge-tts` streaming neural voice<br>• Default voice: `ja-JP-NanamiNeural`<br>• Multilingual fallbacks: `en-US-JennyNeural`, Vietnamese acoustic cadence (`vi-VN`) | Managed via package; zero local weights required |
| **Voice Conversion (RVC)** | Direct RVC v2 neural voice conversion (`SynthesizerTrn` NSF-HiFiGAN 40 kHz) | `VaresaGIJP` Japanese Character Voice<br>• Weights: `VaresaGIJP_300e_2100s.pth` (~55 MB)<br>• Feature Index: `added_VaresaGIJP_v2.index` (`IndexIVFFlat`, ~33 MB) | `models/voice/rvc/VaresaGIJP/` |
| **Polymorphic Avatars** | Live2D Cubism 4 & 2D Sprites | • Live2D: `huohuo`, `HoshinoAi`<br>• Emotive Sprites: `columbina` (10 expressions) | `models/avatar/live2d/`<br>`models/avatar/sprites/` |

---

## 9. Canonical Documentation Navigation

For complete architectural specifications, mathematical foundations, and operating instructions:

| Document | Purpose & Authority |
|---|---|
| 📖 [User Manual & Operator Runbook](docs/USER_MANUAL.md) | **Authoritative Runbook**: Lifecycle state machine, pre-activation checklist, operator Genesis protocol, First Activation, Cognitive Execution Trace guide, decision trees, and desktop GUI guide. |
| 🛡️ [Canonical Invariant Ledger](docs/L1_INVARIANTS.md) | **Non-Negotiable Truth [L1]**: Consolidated invariants covering identity, limbic ODE, concurrency locking, and governance. |
| 🏛️ [Canonical Technical Architecture](docs/ARCHITECTURE.md) | **Technical Truth [L3]**: 20-Watt Whole Brain Architecture, mathematical derivations, lock hierarchies, and ADR ledger (ADR-001 to ADR-036). |
| 📊 [Canonical Project Overview](docs/00_PROJECT_OVERVIEW.md) | **Project Truth [L2]**: System identity, philosophy, subsystem health matrix, active REST API surface, and milestone roadmap. |
| 📋 [Authoritative Phase Registry](docs/PHASE_REGISTRY.md) | **Phase Ledger [L2]**: Authoritative lifecycle tracking covering P01 through P27, ADR-035, and Genesis Gate. |
| 🔬 [Master Evidence & Evaluation Index](docs/PhaseDocs/INDEX.md) | **Evidence Map [L4]**: Authoritative index mapping all phases to reports, raw evaluation artifacts, and executable test suites. |
| 🧭 [Context Retrieval Map](docs/CONTEXT_INDEX.md) | **Agent Routing [L4]**: Logical context tiers (L0–L6) and minimal sufficient file loading instructions. |
| 📜 [Agent Operating Guidelines](AGENTS.md) | **Governance & Procedures**: Mandatory decision protocol and behavioral invariants for AI coding assistants. |

---

## Governance & License

Lucia is an internal private research repository. All architectural designs, dynamical mechanisms, and source code are governed by the strict project invariants defined in [AGENTS.md](AGENTS.md) and [docs/L1_INVARIANTS.md](docs/L1_INVARIANTS.md). Unprompted modification of cognitive state, bypass of activation gates, or unauthorized live Genesis execution is strictly prohibited.