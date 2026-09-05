# Lucia — Architectural Design Decisions & ADR Ledger

> **Formal Architectural Decision Records (ADRs), Trade-Off Analyses, and Reconciliation of Historical Contradictions**

---

## 1. Introduction & Governance

This document serves as the **authoritative register of design decisions** for the Lucia project. Over seven development phases, Lucia evolved from a theoretical neurocomputational concept into a production-grade embodied desktop companion. 

This document captures:
1. The **Architectural Decision Records (ADRs)** that govern system architecture.
2. The **pivots and trade-offs** made when engineering realities diverged from initial conceptual specs.
3. The **explicit reconciliation** of outdated specifications and conflicting decisions across historical phase documents.

---

## 2. Architectural Decision Records (ADRs)

### ADR-001: Pre-Reflective Continuous Affect vs. Prompted Emotional Roleplay
* **Status**: **ACCEPTED** (Phase 1, reaffirmed in all subsequent phases)
* **Context**: Traditional LLM chatbots simulate emotion by prepending system instructions (e.g. *"You are cheerful"*, *"You are feeling sad"*). This produces superficial roleplay, hallucinated emotional shifts, and breaks character consistency under adversarial prompts.
* **Decision**: Emotion is modeled as a continuous dynamical system in 3-dimensional PAD space (Pleasure, Arousal, Dominance) governed by a Liquid Neural Network (LNN) differential equation solved every 200 ms. Emotion is **pre-reflective**—it never expresses itself as self-reported labels (*"I feel happy"*). Instead, it mechanically conditions generation through physical consequences: token length, sampling temperature, reasoning depth ($k$), and response latency. A strict `BoundaryLayer` regex filter blocks any introspective self-awareness output.
* **Consequences**:
  * *Positive*: Emotion feels authentic, organic, and physically grounded in time; zero emotional amnesia between turns.
  * *Trade-off*: Requires strict conditioning rules and a post-generation safety layer to eliminate introspective meta-commentary.

---

### ADR-002: Local GGUF Small Language Model (SLM) + Boundary Layer vs. Theoretical SNN/HDC
* **Status**: **ACCEPTED** (Phase 1 / Pragmatic Implementation)
* **Context**: The foundational concept whitepaper (*Triết lý thiết kế AI cảm xúc.md*) proposed a completely "token-free" language core using Hyperdimensional Computing (HDC) and Spiking Neural Networks (SNNs) for Broca-area expression.
* **Decision**: Because production-ready general conversational generation via HDC/SNN does not yet exist for edge consumer hardware, Lucia pragmatically adopts a local GGUF Small Language Model (**LFM2.5-1.2B Instruct** or **Qwen2.5-3B**) accelerated via CUDA on consumer GPUs (e.g. RTX 3050 Ti Laptop, 4GB VRAM). The theoretical "non-reflective" goal is enforced deterministically by placing the rule-based `BoundaryLayer` validator directly downstream of the LLM before any token is emitted to voice or UI.
* **Consequences**:
  * *Positive*: Fluent, highly coherent conversational generation achievable immediately on 4GB VRAM.
  * *Trade-off*: Language generation remains token-based rather than biologically spiking; non-reflective behavior relies on prompt assembly structure and post-filtering.

---

### ADR-003: Kanerva Sparse Distributed Memory (SDM) with Emotional Resonance vs. Vector RAG
* **Status**: **ACCEPTED** (Phase 2)
* **Context**: Standard Retrieval-Augmented Generation (RAG) relies on dense vector databases (e.g. Chroma, Pinecone) that perform literal search queries and inject past snippets as verbatim quotes (*"On Tuesday you told me X"*). This feels robotic and breaks conversational immersion.
* **Decision**: Lucia implements **Pentti Kanerva's Sparse Distributed Memory (SDM)** (1,000 hard locations, 1,000-bit Hamming address space, 64-dim content vectors) augmented with **Affective Tagging** and **Synergistic Ecphory**:
  1. Every interaction trace is stored with a frozen 3D PAD emotional tag.
  2. Memory decay is salience-resistant: emotionally intense moments ($|PAD| \gg 0$) resist forgetting up to $4\times$ longer.
  3. Recall is associative: current emotional states resonate with past traces via cosine similarity, synthesizing an **Echo Vector** that subtly primes the LLM prompt without quoting verbatim text.
* **Consequences**:
  * *Positive*: Past interactions color Lucia's mood and conversational texture without robotic verbatim quoting.
  * *Trade-off*: Cannot be queried like a SQL database for exact factual lookups; intended strictly for affective bonding.

---

### ADR-004: CPU-Only LNN Plasticity (`torchdiffeq`) Without GPU VRAM Contention
* **Status**: **ACCEPTED** (Phase 4)
* **Context**: To adapt Lucia's emotional dynamics over time, the LNN ODE weights must be trainable via online gradient descent. However, consumer laptop GPUs (e.g. RTX 3050 Ti, 4GB VRAM) are already heavily occupied by the LLM GGUF model.
* **Decision**: Implement `LNNTrainer` entirely on the CPU. Experience tuples `(stimulus, h_before, h_after)` are buffered in a ring buffer. When a batch of 16 turns accumulates, a background CPU thread runs backpropagation-through-ODE using `torchdiffeq.odeint`. Updated weights are swapped into `EmotionCore` inside a sub-2ms `_train_lock`.
* **Consequences**:
  * *Positive*: Absolutely **0 MB GPU VRAM contention**; online learning runs in the background without stuttering LLM generation or avatar WebGL rendering.
  * *Trade-off*: CPU backprop is limited to small batch sizes ($B=16$) and small hidden states ($H=32$), which is ideal for limbic ODE dynamics.

---

### ADR-005: Phase 5 Pivot: Vocal & Visual Multimodal Presence over Desktop Agency
* **Status**: **SUPERSEDED SPEC / PIVOT IMPLEMENTED** (Phase 5)
* **Context**: The Phase 5 specification in `.kiro/specs/lucia-presence-phase5/` originally proposed an agentic desktop automation system: screen capture via Qwen2.5-VL 3B, webcam capture, Windows UIAutomation grounding, and PyAutoGUI click/type execution. During implementation, this was determined to deviate sharply from Lucia's primary identity as an intimate, emotional companion, while introducing extreme VRAM pressure on 4GB systems.
* **Decision**: **Pivot Phase 5 to Embodied Multimodal Presence**. Implement:
  1. Direct, self-contained RVC (Retrieval-based Voice Conversion) voice synthesis engine with Edge-TTS base voice.
  2. Complete offline Speech-to-Text via `faster-whisper` and local Web Audio VAD.
  3. Real-time quad-engine avatar stage (2D Canvas, Sprites, Live2D, 3D VRM) with 60 FPS Web Audio lip-syncing.
* **Status of Original Spec**: The contents of `.kiro/specs/lucia-presence-phase5/` are preserved as historical artifacts for potential future agentic features, but are explicitly superseded for Phase 5.
* **Consequences**:
  * *Positive*: Lucia achieved true multi-sensory embodiment (voice, face, gaze, speech recognition) on consumer hardware.
  * *Trade-off*: Desktop automation and VLM screen reading remain deferred to future exploratory phases.

---

### ADR-006: Phase 7 Paradigm Shift: Personal Digital Room vs. Technical AI Dashboard
* **Status**: **ACCEPTED** (Phase 7, Active Implementation)
* **Context**: Phases 3 and 6 implemented a 3-column desktop layout that prominently displayed technical telemetry: live PAD coordinate numbers, tick jitter in milliseconds, somatic load percentages, and memory trace counters. This framed Lucia as a "machine to be operated" rather than a companion.
* **Decision**: Refactor the desktop interface around **Progressive Disclosure** and the **"Personal Digital Room"** aesthetic:
  1. **Primary Interface (Everyday Interaction)**: The avatar stage and dialogue feed inhabit an ethereal, nighttime room with dark velvet surfaces and moonlight violet accents. Lucia's emotional state is expressed through posture, facial blendshapes, voice cadence, and subtle qualitative cues (*"Lucia feels serene and warm"*).
  2. **Secondary Interface (Settings)**: Appearance (outfit/avatar), Voice, Presence, and Hardware profiles.
  3. **Tertiary Interface (Diagnostics)**: Raw numeric telemetry (PAD meters, LSI, Jitter) is relocated to a dedicated Diagnostics modal, accessible only when explicitly requested.
* **Consequences**:
  * *Positive*: Restores the core companion philosophy; eliminates user cognitive overload.
  * *Trade-off*: Developers must open the Diagnostics modal to view raw mathematical variables.

---

### ADR-007: Ontology of "One Continuous Life" vs. Character Presets
* **Status**: **ACCEPTED** (Phase 7)
* **Context**: Traditional desktop AI apps feature "character switchers" where users switch between completely different personas (e.g. "Columbina", "Hoshino Ai", "Anime Maid").
* **Decision**: Lucia has **One Continuous Life**. She is a single, continuous individual whose emotional trajectory, affective memory traces, and relationship with the user persist indefinitely. Avatar models (Live2D Hoshino Ai, Columbina sprites, 3D VRM) represent Lucia's **Appearance** (her physical attire/embodiment), not different people.
* **Consequences**:
  * *Positive*: Preserves emotional continuity and long-term attachment.
  * *Rule for Agents*: Agents must **never** create character preset selectors, profile switchers, or multiple Lucia personalities.

---

### ADR-008: Dual Presentation Architecture: Studio Window & Always-on-Top Mascot Mode
* **Status**: **ACCEPTED** (Phase 6 & 7)
* **Context**: Users alternate between deep conversational sessions (writing, journaling) and working on other tasks (coding, gaming) where a full application window is intrusive.
* **Decision**: Deliver two complementary presentation modes via Electron:
  1. **Studio Mode**: Full-window experience with rich chat feed, journal, and appearance stage.
  2. **Floating Mascot Mode**: A transparent, frameless, click-through-capable, Always-on-Top desktop avatar with an anchored toolbar dock that automatically follows the character's feet (`getModelBounds()`).
* **Consequences**:
  * *Positive*: Lucia can stay present on the desktop during everyday work without blocking the user's workflow.

---

### ADR-009: Fully Offline Audio Pipeline vs. Third-Party Cloud APIs
* **Status**: **ACCEPTED** (Phase 5 & 6)
* **Context**: Cloud TTS/STT services (OpenAI Whisper API, ElevenLabs) introduce ongoing costs, cloud telemetry, latency, and fail when offline. Electron's native `webkitSpeechRecognition` fails on Windows with chunked data pipe upload stream errors.
* **Decision**:
  1. **STT**: Continuous microphone capture streamed via frontend `MediaRecorder` + Web Audio VAD to local `POST /voice/transcribe`, running local CTranslate2 `faster-whisper` (FP16 on CUDA, INT8 on CPU).
  2. **TTS**: Local synthesis via Edge-TTS / RVC model pipeline running entirely on the host machine.
  3. **Echo Prevention**: Voice input automatically pauses during Lucia's speech playback and resumes on completion.
* **Consequences**:
  * *Positive*: 100% private, zero cloud keys, zero subscription fees, functional without internet connectivity.

---

## 3. Reconciliation of Outdated Specs & Conflicting Decisions

| Dimension | Outdated / Preliminary Spec | Authoritative Implemented Reality | Resolution & Rationale |
|---|---|---|---|
| **SDM Dimension** | 64-bit address, 16-bit content (early conceptual notes in Architecture/Mechanism). | 1,000-bit address (`D=1000`), 64-dim content (`M=64`), $N=1,000$ locations (`src/core/memory/sdm.py`). | The 64-bit mention was an introductory mathematical simplification. The 1000-bit address is the true Kanerva Hamming space implemented in code and tested by Hypothesis property tests. |
| **Resting Baseline** | $P=0.1, A=0.0, D=0.0$ (Phase 1 spec default). | Philia Attractor: $P=+0.25, A=-0.05, D=+0.05$ (`EmotionCore`). | Shifted during Phase 6 limbic tuning to provide a warmer, slightly calmer, egalitarian peer baseline. |
| **Decay Cadence** | 3,600 seconds / 1 hour (Phase 2 spec glossary). | 60 seconds continuous background daemon tick (`DecayEngine`). | A 60-second tick with scaled effective decay rate ($\lambda_{eff}$) ensures smooth mathematical forgetting rather than hourly chunk drops. |
| **Voice Backend** | Piper / Kokoro ONNX (`models/voice/README.md`). | Direct RVC engine (`.pth` + `.index`) with Edge-TTS (`src/core/voice/voice_engine.py`). | RVC provides superior character timbre customization and emotional pitch modulation. |
| **UI Telemetry Focus** | Front-page telemetry meters (Phase 3 & 6). | Progressive disclosure; telemetry relegated to Diagnostics modal (Phase 7). | Aligns with companion-first philosophy: interact with Lucia first, inspect systems second. |
| **Chat Session Reset** | "Clear Screen" perceived as data loss. | Visual reset only; long-term SDM memory and friendship bond remain untouched. | Architectural separation between ephemeral chat history (`data/chat_history.json`) and subconscious memory (`SDMCore`). |

---

## 4. Concurrency & Lock Invariants

All future contributions and modifications must strictly observe the following locking order to prevent deadlocks:

```
┌────────────────────────────────────────────────────────────────────────┐
│                        LOCK HIERARCHY DISCIPLINE                       │
│                                                                        │
│   1. _state_lock  (Held ≤ 1ms for PAD state snapshot read/write)       │
│   2. _train_lock  (Held ≤ 2ms for atomic LNN weight swaps)             │
│   3. _index_lock  (Held for SDM trace insert & decay sweep)            │
│                                                                        │
│   RULE: Never acquire _state_lock while holding _train_lock.           │
│   RULE: Never perform disk I/O or network requests while holding locks.│
└────────────────────────────────────────────────────────────────────────┘
```
