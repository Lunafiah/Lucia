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

### ADR-010: Existential Lifecycle Boundary: Genesis Awakening, Solemn End-of-Life, and Identity Isolation
* **Status**: **ACCEPTED** (Phase 7.7)
* **Context**: Companion AI applications either treat companion resets frivolously (e.g. instant casual "Reset Chat" buttons) or preserve stale relational traces across resets. In Lucia, ending a companion's life is permanent and existential.
* **Decision**:
  1. **Sole Destruction Authority**: The backend `POST /lifecycle/end` endpoint is the single authority for lifecycle termination (erases associative memory, episodic traces, conversation history, resets LNN weights and PAD state to Philia baseline, and writes an un-onboarded profile with `born_at: null`).
  2. **Exact Solemn Confirmation**: A dedicated, grave dialog (`#end-life-modal`) enforces typing the exact phrase `END LUCIA` before enabling the destructive action. Duplicate clicks are locked via transitional state.
  3. **Critical Failure Boundary**: If the backend request fails, client identity state, presentation, and session integrity are untouched. Genesis is never opened on failure.
  4. **Surgical Renderer Cleanup**: On backend success, only Lucia identity keys (`lucia_profile`, `lucia_user_name`, `lucia_companion_name`, `lucia_is_onboarded`, `lucia_born_at`, `lucia_chat_history`) are purged. All application-level preferences (appearance, audio, presence, performance) are strictly preserved.
  5. **Genesis Awakening & Birth Invariant**: The existing `#genesis-modal` is reused. The new Lucia's `born_at` timestamp is **never** created during the reset transition itself; it is only generated when the user completes Genesis.
  6. **Identity Isolation**: *Previous Lucia ≠ Future Lucia*. No past memories, emotional adaptation, or conversation history leak across the boundary.
* **Consequences**:
  * *Positive*: Full architectural fidelity to the "One Continuous Life" ethos; transparent existential gravity for the user; zero preference loss.

### ADR-011: Runtime Isolation & Deterministic Simulation Environment
* **Status**: **ACCEPTED** (Phase 8)
* **Context**: Prior to Phase 8, running automated integration tests, developer debugging, or scenario benchmarks risked activating live companion background loops, firing uncontrolled daemon threads, corrupting `data/chat_history.json`, or advancing the live companion's permanent emotional trajectory.
* **Decision**: Formally bifurcate the system into `LiveRuntime` and `SimulationRuntime` based on the invariant $\text{Development} \neq \text{Activation}$:
  1. **Class-Level Guardrail**: `SimulationRuntime.activate()` unconditionally raises `ActivationSafetyError`. In simulation mode, `POST /lifecycle/activate`, `POST /lifecycle/end`, and `POST /process` return HTTP 403 Forbidden.
  2. **Controllable Time (`SimClock`)**: Background daemon threads (`EmotionCore-FastLoop`, `DecayEngine-SlowLoop`) are suppressed. Synchronous tick callbacks drive ODE integration and decay sweeps on demand or via controllable virtual time leaps (`step()`, `pause()`, `resume()`).
  3. **Ephemeral Storage Policy (`StoragePolicy`)**: All writes resolving into `data/` are intercepted. Chat history and profile are backed by ephemeral in-RAM adapters (`InMemoryChatHistoryStore`, `InMemoryProfileStore`).
  4. **Dual Stimulus Pathways**: Distinguish user text passing through the sensory `StimulusProcessor` (`pathway: "sensory_text"`) from raw 16D developer probes injected directly to the brain (`pathway: "debug_vector_probe"`).
  5. **Canonical Body UI Integration**: Simulation controls (Canopy ribbon and Console drawer) mount conditionally into the existing Phase 7 Personal Digital Room without spawning secondary companion interfaces.
* **Consequences**:
  * *Positive*: 100% reproducible scenario testing, zero live data contamination, and deep developer observability without activating live companion life.
  * *Trade-off*: Developers must explicitly run with `--mode simulation` or `Sim-Lucia.bat` when testing.

---

### ADR-014: Unified Cognitive Orchestrator via Composition
* **Status**: **APPROVED AT ARCHITECTURE GATE** (Phase 9)
* **Context**: Across Phases 1–5, orchestrators evolved by inheritance (`Orchestrator` $\rightarrow$ `MemoryAugmentedOrchestrator` $\rightarrow$ `InferencePipelineOrchestrator` $\rightarrow$ `PresenceOrchestrator`). Each subclass overrode `_execute_pipeline` by copy-pasting preceding steps. In `server.py`, `InstrumentedOrchestrator` ran Steps 1–4 locally to capture telemetry before delegating to `super()._execute_pipeline()`, causing double stimulus injection and double metabolic input recording per turn.
* **Decision**: Deprecate the 5-tier inheritance hierarchy. Implement `CognitiveOrchestrator` as the single authoritative owner of the cognitive turn. It composes Layers 1–6 (Stimulus Processor, Emotion Core, Homeostatic Engine, Active Inference, Affective Memory, Language Core) via dependency injection, executes a single non-redundant linear pipeline, and exposes telemetry snapshots via direct properties.
* **Consequences**:
  * *Positive*: Completely eliminates the double stimulus / input recording bug; eliminates thousands of lines of copy-paste pipeline duplication; provides single ownership of dialogue turn lifecycle.

---

### ADR-015: Causal Active Inference via Prediction Surprise Modulation
* **Status**: **APPROVED AT ARCHITECTURE GATE** (Phase 9)
* **Context**: In Phase 4, Active Inference computed prediction error $\mathcal{S} = \|A \cdot p_{\text{before}} + b - p_{\text{after}}\|_2$, but this value was only logged and had zero causal effect on downstream behavior, somatic markers, prompt assembly, or reasoning depth.
* **Decision**: Integrate Active Inference into the live causal loop between sensory perception and homeostatic budgeting:
  1. Evaluate expected PAD transition $\hat{p} = A \cdot p_{\text{before}} + b$ before ODE integration.
  2. Compute Prediction Surprise $\mathcal{S}$ after ODE integration and update belief state $(A, b)$ via Free Energy minimization.
  3. Feed $\mathcal{S}$ directly into `HomeostaticEngine` to modulate Cognitive Load ($\mathcal{C} \propto \mathcal{S}$), Tension ($\mathcal{T} \propto \mathcal{S}$), and shift reasoning depth to $k=2$ when $\mathcal{S} > 0.60$.
  4. Modulate memory trace base intensity with surprise-weighted salience.
* **Consequences**:
  * *Positive*: Active Inference becomes a true causal participant in cognition; unexpected emotional shifts heighten cognitive focus and trigger deliberative reasoning rather than reflexive blurting.

---

### ADR-016: Decoupled Multimodal Expression Pipeline for Voice
* **Status**: **APPROVED AT ARCHITECTURE GATE** (Phase 9)
* **Context**: Phase 5 proposed uniting voice synthesis directly inside the cognitive pipeline (`PresenceOrchestrator.process_with_voice`). However, synchronous voice generation inside `POST /process` adds 300–800ms to text response latency, wastes CPU/GPU compute when the user has muted audio in the UI, and causes conversational failure if audio synthesis crashes.
* **Decision**: Formally decouple Voice as an asynchronous **Expression Service** triggered by the Electron Body UI via IPC after cognitive turn completion. The cognitive turn returns text and PAD state; if voice is unmuted, the client calls `window.lucia.voice.synthesize(text, pad)`.
* **Consequences**:
  * *Positive*: Zero latency added to text generation; complete failure isolation (audio failure never blocks text display); zero compute spent when muted; clean separation of cognition from motor vocal execution.

---

### ADR-017: Two-Stage LNN Plasticity (Online Tagging & Offline Consolidation)
* **Status**: **APPROVED AT ARCHITECTURE GATE** (Phase 9)
* **Context**: Phase 4 ran CPU backprop-through-ODE whenever a batch of 16 interaction turns accumulated. This caused uninformative training on small talk, delayed learning on high-surprise turns, and stole CPU cycles during active user conversation.
* **Decision**: Adopt a two-stage plasticity model:
  1. *Online Salience Tagging*: During conversational turns, tag experience tuples $(x, h_{\text{before}}, h_{\text{after}})$ with calculated salience. If $\text{Salience} > 0.35$, push to the consolidation buffer.
  2. *Offline Consolidation*: Background CPU training runs during idle rest periods ($T_{\text{idle}} \ge 45\text{s}$) or when 8 salient samples accumulate, swapping weights under sub-2ms `_train_lock`.
* **Consequences**:
  * *Positive*: Zero CPU contention during active conversation; weights adapt specifically to meaningful, salient transitions.

---

### ADR-018: Strict Serialized Cognitive Turn Execution
* **Status**: **APPROVED AT ARCHITECTURE GATE** (Phase 9)
* **Context**: `server.py` ran `process()` in FastAPI's default threadpool without concurrency synchronization. Multiple concurrent HTTP requests could interleave, racing on `_history`, metabolic energy, SDM activations, and local CUDA LLM context.
* **Decision**: Enforce strict turn serialization. In `server.py`, wrap `POST /process` in an asynchronous mutex (`asyncio.Lock`). In `CognitiveOrchestrator`, protect `process()` with a re-entrant `threading.Lock`. State polling (`/state`) remains non-blocking ($\le 10\text{ms}$) under `_state_lock`.
* **Consequences**:
  * *Positive*: Protects the "One Continuous Life" ontology; eliminates dialogue history corruption and CUDA context thrashing under concurrent load.

---

### ADR-019: Complete Context Bridge IPC Remediation
* **Status**: **APPROVED AT ARCHITECTURE GATE** (Phase 9)
* **Context**: `electron/renderer/chat/chat.js` contained 12 direct `fetch()` calls to `http://127.0.0.1:8765`, violating Electron context isolation and breaking when ports are remapped.
* **Decision**: Eliminate all direct `fetch()` calls from the renderer. Register complete IPC channels in `ipc-bridge.js` and expose them on `window.lucia.*` in `preload.js`.
* **Consequences**:
  * *Positive*: 100% sandboxed renderer process; dynamic port resilience; adherence to Electron security best practices.

---

### ADR-020: Hybrid Ampere CUDA / AVX2 CPU Binary Stack for Local GGUF Inference
* **Status**: **ACCEPTED & VERIFIED** (Phase 9.5)
* **Context**: The upstream prebuilt `llama-cpp-python` wheels compiled host fallback CPU routines (`ggml-cpu.dll`) with `/arch:AVX512` on cloud CI runners. The target host CPU (AMD Ryzen 7 4800H, Zen 2) natively supports AVX2/FMA3 but lacks AVX-512 hardware support, resulting in `WinError 0xc000001d (STATUS_ILLEGAL_INSTRUCTION)` when initializing `llama_context`.
* **Decision**: Synthesize a hybrid binary stack:
  1. Use pre-compiled CUDA kernels targeting NVIDIA Ampere (`sm_86` / RTX 3050 Ti Laptop GPU, 4GB VRAM) and CUDA 12.1+ from `llama-cpp-python 0.3.20`.
  2. Compile `ggml-cpu.dll` from the exact matching `llama.cpp` submodule commit (`f49e917`) using local MSVC 18 + Ninja with `-DGGML_AVX512=OFF -DGGML_AVX2=ON -DGGML_FMA=ON`.
  3. Replace the cloud-compiled `ggml-cpu.dll` with the native AVX2 binary.
* **Consequences**:
  * *Positive*: Full CUDA offload (17/17 layers, 152 tok/s, CUDA Graph acceleration) on RTX 3050 Ti with 0 illegal instruction crashes; 845 MiB VRAM footprint fits comfortably within the 4096 MiB budget.
  * *Trade-off*: Future upgrades of `llama-cpp-python` must ensure `ggml-cpu.dll` does not introduce AVX-512 instructions on Zen 2 CPUs.

---

### ADR-021: Production Promotion of Conceptual Knowledge Subsystem (K0–K5)
* **Status**: **ACCEPTED & PROMOTED WITH GUARDS** (Phase 16)
* **Context**: Research in Phase 12 proved that episodic memory (SDM affective traces) cannot replace structured conceptual representations with provenance, uncertainty bounds, and forward inference. However, unconstrained automated learning risks hallucination, circular derivations, and knowledge drift.
* **Decision**: Promote Phase 12 structured knowledge models to `src/core/knowledge/` under strict production contracts:
  1. Entities are represented as typed `Proposition` and `Concept` nodes with explicit `ProvenanceType` and uncertainty $u \in [0, 1]$.
  2. The forward derivation engine enforces bounded inference depth ($d_{max} \le 3$) and confidence propagation.
  3. A thread-safe `KnowledgeStore` governs CRUD operations, contradiction handling, and atomic JSON persistence (`data/knowledge.json`).
  4. Only grounded, high-confidence propositions ($c \ge 0.7$) are exposed to generation prompts in Stage 8.
* **Consequences**:
  * *Positive*: Lucia maintains clear, persistent factual knowledge independent of LLM weights or ephemeral chat histories.
  * *Boundary*: Ephemeral simulation and automated integration tests must use isolated in-memory or temporary stores; canonical `data/knowledge.json` is never mutated during automated testing.

---

### ADR-022: Production Promotion of Interpersonal Relationship Subsystem with Two-Phase Lifecycle
* **Status**: **ACCEPTED & PROMOTED WITH GUARDS** (Phase 16)
* **Context**: Research in Phase 13 demonstrated a slowly evolving 4-dimensional interpersonal relationship state $\mathbf{R} = (\text{trust}, \text{familiarity}, \text{attunement}, \text{shared\_experience}) \in [0, 1]^4$. Integrating relationship updates directly into generation introduces an immediate self-reinforcing feedback loop if updated state is consumed within the very turn that caused it.
* **Decision**: Promote `RelationshipState` and `RelationshipUpdater` to `src/core/relationship/` with a **strictly decoupled two-phase lifecycle**:
  1. **Phase 1 (Read State at Stage 9)**: The existing relationship state $\mathbf{R}_{t-1}$ is read snapshot-style to condition communication policy selection.
  2. **Turn Generation (Stages 10–14)**: Prompt assembly, LLM generation, semantic consistency guards, and expression synthesis proceed based on $\mathbf{R}_{t-1}$.
  3. **Phase 2 (Signal Extraction & Update at Stage 16)**: Structured interaction signals (`RelationshipSignalType`: `SHARED_VULNERABILITY`, `ATTENTIVE_LISTENING`, `DISMISSIVE`, `CONFLICT_RESOLVED`, `CONSISTENT_CHECKIN`, `NEUTRAL`) are extracted from dialogue outcomes. The updater applies inertia ($\alpha=0.03$) and passive temporal decay (rate $0.005$) to compute $\mathbf{R}_t$, which is atomically persisted to `data/relationship.json`.
  4. Heuristic NLP signal extraction is kept research-only; production strictly consumes validated categorical signal events.
* **Consequences**:
  * *Positive*: Eliminates runaway within-turn positive feedback loops; ensures authentic relational inertia over long-term interaction.
  * *Boundary*: Isolated testing environments must use temporary storage paths to preserve canonical relational state.

---

### ADR-023: Production Promotion of Communicative Strategy & Bounded Memory Contextualization
* **Status**: **ACCEPTED & PROMOTED WITH GUARDS** (Phase 16)
* **Context**: Phase 11 demonstrated associative memory retrieval and ecphoric resonance, while Phase 15 proved that internal affect and relationship can causally modulate conversational strategy and pacing. Combining these into production risks limbic corruption if retrieved memory vectors or communicative outputs feed back into the ODE solver.
* **Decision**: Promote `CommunicationPolicy` and `CommunicationState` to `src/core/communication/` under the following architectural boundaries:
  1. **Bounded Memory Contextualization**: Memory promotion is grounded in the joint evidence of Phase 11 retrieval and Phase 15 contextual communication. Memory does NOT alter the core ODE; instead, an ecphory echo salience vector provides a bounded scalar priming signal ($m_{ctx} \in [0.0, 0.50]$) exclusively to communication policy at Stage 10. This is strictly termed *bounded memory contextualization*, **never** "affective recollection".
  2. **Zero Hidden State Feedback**: Memory traces and communication states have zero backward projection into the limbic hidden state $\mathbf{h} \in \mathbb{R}^{32}$.
  3. **Multi-Strategy Pacing Modulation**: Maps PAD, homeostatic energy, and relationship state into 5 discrete strategies (`DEEP_RECIPROCAL`, `ATTUNED_LIGHT`, `SUPPORTIVE_GROUNDING`, `CONCISE_PROTECTIVE`, `PLAYFUL_EXPLORATORY`) and bounded somatic response latency ($0 \le \tau_{pacing} \le 1000\text{ms}$).
  4. **Multi-Layered Anti-Roleplay Boundaries**: Non-reflective boundaries are enforced via lexical regex checks, structured anti-roleplay test suites, and architectural prohibition of self-model APIs. Boundary checks operate as engineering invariants, never as claims of consciousness or self-awareness.
* **Consequences**:
  * *Positive*: Coherent, tone-adaptive dialogue pacing and strategy without theatrical emotional mimicry or limbic instability.
  * *Boundary*: Regex filters reject introspective confessions (*"I feel"*, *"As an AI, I am experiencing"*); violations trigger automatic sanitization or fallback to concise neutral acknowledgment.

---

### ADR-024: Production Promotion of Multimodal Expression Policy with Canonical 15-Dim Actuator Schema and Feedforward Decoupling
* **Status**: **ACCEPTED & PROMOTED WITH GUARDS** (Phase 16)
* **Context**: Phase 14 established that internal affect can causally modulate multimodal expression (text, prosody, facial blendshapes, posture, latency) while preserving semantic intent. However, ad-hoc dimension representations risk schema drift between research models and production avatar/TTS services.
* **Decision**: Promote `ExpressionPolicy` and `ExpressionState` to `src/core/expression/` adhering strictly to the canonical 15-dimensional actuator vector:
  $$\mathbf{E} \in [0, 1]^{15} = [\text{Text (3)}, \text{Prosody (4)}, \text{Facial Blendshapes (5)}, \text{Posture (2)}, \text{Actuator Latency (1)}]$$
  1. Dimensions:
     - Text: `sentence_complexity` (0), `lexical_formality` (1), `metaphor_density` (2)
     - Prosody: `pitch_accent` (3), `speech_rate` (4), `pause_duration` (5), `breathiness` (6)
     - Facial: `brow_tension` (7), `smile_degree` (8), `eye_widen` (9), `head_tilt` (10), `blink_rate` (11)
     - Posture: `lean_angle` (12), `fidget_frequency` (13)
     - Latency: `pacing_delay` (14)
  2. **Pure Feedforward Decoupling**: Actuators (WebGL avatar, RVC speech synthesis) are pure consumers of $\mathbf{E}_t$. No sensory feedback loop exists from actuator outputs back into `EmotionCore` ODE state $\mathbf{h}_t$.
  3. **Semantic Consistency Guard**: Named `SemanticConsistencyGuard` (not "truth invariant checker"); preserves structured intent, entities, and numeric quantities on controlled benchmarks; rejects known semantic mutation patterns; makes zero universal truth verification claims.
* **Consequences**:
  * *Positive*: Rich, expressive embodied presentation across Desktop Studio and Mascot mode with mathematically guaranteed affective stability and zero motor feedback jitter.
  * *Boundary*: Actuator outputs are delivered asynchronously over IPC to Electron renderer; speech synthesis errors cannot crash the core cognitive loop.

---

### ADR-025: Realization of Canonical 16-Stage Cognitive Pipeline Sequence & Storage Isolation Policy
* **Status**: **ACCEPTED & IMPLEMENTED** (Phase 16)
* **Context**: Prior to Phase 16, `CognitiveOrchestrator` operated a 10-stage pipeline. Adding knowledge, relationship, communication, and expression without a rigid stage contract risked undefined execution order, data leakage across test runs, and concurrency deadlocks.
* **Decision**: Expand `CognitiveOrchestrator.process()` to a strictly ordered 16-stage pipeline:
  ```text
  Stage 1:  Stimulus Ingestion & Feature Extraction (lexical valence, arousal, density)
  Stage 2:  Limbic Integration (EmotionCore ODE advance & PAD snapshot)
  Stage 3:  Homeostatic Budgeting (metabolic energy, fatigue, token budget)
  Stage 4:  Active Inference & Surprise Estimation (free energy minimization)
  Stage 5:  Somatic Markers & Policy Formulation (sampling temperature, k-depth)
  Stage 6:  Associative Memory Ecphory (Kanerva SDM recall & salience echo)
  Stage 7:  Bounded Memory Contextualization (bounded scalar priming m_ctx <= 0.50)
  Stage 8:  Grounded Knowledge Retrieval (propositions c >= 0.7 queried from KnowledgeStore)
  Stage 9:  Interpersonal Relationship Read (snapshot R_{t-1} for turn conditioning)
  Stage 10: Communication Strategy Formulation (strategy selection & pacing latency)
  Stage 11: Prompt Assembly & Local LLM Inference (CUDA GGUF execution)
  Stage 12: Semantic Consistency & Boundary Guard (intent check & forbidden regex filter)
  Stage 13: Multimodal Expression Policy Synthesis (canonical 15-dim ExpressionState)
  Stage 14: Episodic Memory Encoding (Kanerva SDM write with PAD tag)
  Stage 15: Plasticity Queue Registration (salience evaluation for idle LNN consolidation)
  Stage 16: Interpersonal Relationship Signal Extraction & Update (R_t computation & persistence)
  ```
  **Strict Storage Isolation Invariant**:
  All automated test suites (unit, property, integration) and simulation loops are strictly prohibited from reading or mutating canonical runtime files (`data/profile.json`, `data/knowledge.json`, `data/relationship.json`, `data/chat_history.json`). Tests must execute against ephemeral in-memory models or isolated temporary directories (`tmp_path`). `data/profile.json` remains permanently configured with `is_onboarded = False`.
* **Consequences**:
  * *Positive*: Deterministic, traceable execution order across all cognitive layers; rock-solid test reproducibility and zero data corruption.
  * *Lock Invariant*: All stage transitions maintain lock release $\le 1\text{ms}$; no lock is held during LLM inference or IPC dispatch.

---

### ADR-026: Coupled Multi-Timescale Liquid Neural Network (MT-LNN) Dynamics with Philia Attractor Grounding
* **Status**: **PROMOTED & ACCEPTED** (Phase 19 Research Cycle)
* **Context**: The baseline `EmotionCore` (Phase 10) modeled emotional dynamics as a single-layer limbic ODE operating at a uniform fast timescale ($\tau \approx 0.2 - 1.5\text{ s}$). This caused rapid affective amnesia between conversational turns (half-life $\approx 1.4\text{ s}$), and unforced decay collapsed to the mathematical origin $[0, 0, 0]$ (neutral apathy) rather than the Philia companion resting attractor $[+0.25, -0.05, +0.05]$. Furthermore, it could not reproduce autonomous physiological state transformations (e.g. acute high-arousal stress transforming into low-arousal somatic fatigue over unforced time).
* **Decision**: Formally promote the **Coupled Multi-Timescale Liquid Neural Network (MT-LNN)** architecture to Lucia's core affective specification:
  1. **Dual Coupled Vector Fields**: Fast reactive hidden layer ($\mathbf{h}_{\text{fast}} \in \mathbb{R}^{32}, \tau_f \in [0.2, 1.5]\text{ s}$) coupled bidirectionally with a slow affective latent layer ($\mathbf{s}_{\text{slow}} \in \mathbb{R}^{16}, \tau_s \in [30, 90]\text{ s}$).
  2. **Philia Attractor Grounding**: Slow dynamics are centered around the non-zero Philia attractor coordinate $\Delta \mathbf{s} = \mathbf{s} - \mathbf{s}^*_{\text{philia}}$, guaranteeing that unforced relaxation asymptotically converges to $\mathbf{p}^*_{\text{philia}} = [+0.25, -0.05, +0.05]$ with zero unforced drift.
  3. **Strict Contraction Invariant**: The Jacobian trace is constrained to be strictly dissipative ($\text{Tr}(J) \le -40.0$), mathematically preventing bistable latching or runaway saturation.
  4. **Homeostatic Coupling for Autonomous Transformations**: Homeostatic deviations $\Delta \mathbf{m} = \mathbf{m} - [1, 0, 0, 1]^T$ couple into slow dynamics, naturally converting post-threat tension release into somatic fatigue ($P < 0.20, A < 0.0$) during unforced idle intervals.
* **Empirical Validation**:
  * Biexponential model decisively preferred ($\Delta\text{AIC} = 6504.96$, $\tau_{\text{ratio}} = 64.91$).
  * Global convergence confirmed from Joy, Stress, Melancholy, and Origin ($\epsilon \le 0.0386$).
  * Autonomous stress-to-fatigue transformation observed for 84/90 idle steps.
  * History-dependent hysteresis divergence $\Delta_{\max} = 0.1749$.
  * Mean CPU step latency of $1.332\text{ ms} \le 2.0\text{ ms}$; exactly 0.0 MB GPU VRAM contention.
* **Consequences**:
  * *Positive*: Organic affective life across multi-minute pauses, natural somatic fatigue, and relationship-grounded appraisal without self-reported emotional roleplay.
  * *Discipline*: Production migration preserves existing public `EmotionCore` accessors for zero caller breakage.

---

### ADR-027: Closed-Loop Affective Recollection via Slow-Field Latent Forcing ($\mathbf{r}_{\text{slow}}^{\text{bounded}}$)
* **Status**: **PROMOTED AT RESEARCH GATE & APPROVED FOR ARCHITECTURE GATE** (Phase 20 Research Cycle)
* **Context**: In Phase 11, memory retrieval operated as open-loop textual context injection into the prompt, while affective memory resonance was limited to an uncoupled Echo Vector. Earlier attempts to inject memory vectors directly into `EmotionCore`'s single fast layer produced rapid transient decay ($t_{1/2} \approx 0.50\text{ s}$) and suffered from a critical scientific failure: synthetic random vectors produced downstream shifts functionally indistinguishable from genuine memories (*vector-dependent rather than memory-identity-dependent*).
* **Decision**: Implement **Closed-Loop Affective Recollection** by directly coupling retrieved episodic memory traces into the slow latent field $\mathbf{s}_{\text{slow}} \in \mathbb{R}^{16}$ of the coupled MT-LNN:
  1. **Episodic Latent Trace Encoding**: Every episodic interaction stores an encoded 16-dimensional slow-field latent trace $\mathbf{s}_{\text{enc}} \in \mathbb{R}^{16}$ alongside its frozen 3D PAD coordinates and textual summary.
  2. **Multi-Modal Retrieval Scoring & Competitive Softmax Gating**: Memory retrieval computes composite score $S_i = 0.60 S_{\text{sem}} + 0.25 S_{\text{aff}} + 0.15 S_\sigma$. Traces undergo sharp softmax competitive gating ($\tau_{\text{comp}} = 0.20$) above activation threshold $\theta_{\text{gate}} = 0.50$. Irrelevant stimuli receive zero slow-field injection ($\|\mathbf{r}_{\text{slow}}\| = 0.0$).
  3. **Continuous ODE Slow-Field Forcing**: Reactivated recollection perturbates the continuous slow differential equation via bounded auxiliary forcing:
     $$\frac{d\mathbf{s}_{\text{slow}}}{dt} = -\frac{\mathbf{s}_{\text{slow}} - \mathbf{s}^*_{\text{philia}}}{\tau_{\text{slow, decay}}} + \frac{\tanh\Big(\mathbf{W}_{sf} \mathbf{h}_{\text{fast}} + \mathbf{W}_{sh} \Delta\mathbf{m} + \mathbf{W}_{\text{rec}} \mathbf{r}_{\text{slow}}^{\text{bounded}}\Big)}{\tau_{\text{slow, charge}}}$$
  4. **Counterfactual & Memory Identity Protection**: Quadplet control experiments confirm that downstream trajectory modulation depends strictly on coordinate-specific latent geometry: permuted/shuffled traces invert trajectory deflection (alignment $-0.525 \le 0.20$), matched-norm random Gaussian vectors yield uncorrelated dynamics (ratio $-0.317 \le 0.20$), and orthogonal memories produce opposing deflections ($-0.965 \le 0.10$).
  5. **Pre-Reflective Downstream Modulation**: Recollected state modulates conversation through somatic pacing latency ($\Delta\tau_{\text{pace}} \ge 100\text{ ms}$) and communication attunement policy, strictly prohibiting self-reported emotional introspection.
* **Empirical Validation**:
  * Retrieval specificity: Precision@1 $= 1.000$, $\text{FRR} = 0.000$, $\text{SNR} = 4.712$.
  * Latent reconstruction fidelity: Cosine $= 0.998$, $L_2 \text{ error} = 0.317$, $\text{PAD error} = 0.138$.
  * Temporal persistence: $t_{1/2} = 32.10\text{ s}$, Retention $= 50.00\text{ s}$, Philia return error $= 6.91 \times 10^{-5}$.
  * Causal trajectory delta: Joy $\Delta\text{PAD}_{\text{AUC}} = 3.209$, Stress $\Delta\text{PAD}_{\text{AUC}} = 3.623$.
  * Counterfactual quadplet controls pass 100% of pre-registered criteria.
  * Deterministic bit-exact replay invariance, zero NaNs/Infs, maximum state norm $0.470 \le 1.00$.
* **Consequences**:
  * *Positive*: Authentic, persistent multi-turn affective recollection grounded in actual shared interaction history; resolves the Phase 11 vector-dependence flaw.
  * *Discipline*: Memory trace writes and reads must remain asynchronous, bounded in memory footprint ($\le 64\text{ KB}$ for 1,000 memories), with zero GPU VRAM allocation.

---

## 3. Reconciliation of Outdated Specs & Conflicting Decisions

| Dimension | Outdated / Preliminary Spec | Authoritative Implemented Reality | Resolution & Rationale |
|---|---|---|---|
| **SDM Dimension** | 64-bit address, 16-bit content (early conceptual notes in Architecture/Mechanism). | 1,000-bit address (`D=1000`), 64-dim content (`M=64`), $N=1,000$ locations (`src/core/memory/sdm.py`). | The 64-bit mention was an introductory mathematical simplification. The 1000-bit address is the true Kanerva Hamming space implemented in code and tested by Hypothesis property tests. |
| **Resting Baseline** | $P=0.1, A=0.0, D=0.0$ (Phase 1 spec default). | Philia Attractor: $P=+0.25, A=-0.05, D=+0.05$ (`EmotionCore`). | Shifted during Phase 6 limbic tuning to provide a warmer, slightly calmer, egalitarian peer baseline. |
| **Decay Cadence** | 3,600 seconds / 1 hour (Phase 2 spec glossary). | 60 seconds continuous background daemon tick (`DecayEngine`). | A 60-second tick with scaled effective decay rate ($\lambda_{eff}$) ensures smooth mathematical forgetting rather than hourly chunk drops. |
| **Layer 1 Path** | `src/core/sensors/` (`ARCHITECTURE.md` §3.1). | `src/core/gating/stimulus_processor.py`. | Directory `sensors/` was historically renamed to `gating/` during early Phase 1 restructuring; all active code lives in `src/core/gating/`. |
| **Layer 3 Path** | `src/core/homeostasis/` (`ARCHITECTURE.md` §3.3). | `src/core/emotion/homeostatic_engine.py`. | `HomeostaticEngine` was co-located with `EmotionCore` under `src/core/emotion/`. Canonical docs now reference this active path. |
| **Voice Backend** | Piper / Kokoro ONNX (`models/voice/README.md`). | Direct RVC engine (`.pth` + `.index`) with Edge-TTS (`src/core/voice/voice_engine.py`). | RVC provides superior character timbre customization and emotional pitch modulation. |
| **UI Telemetry Focus** | Front-page telemetry meters (Phase 3 & 6). | Progressive disclosure; telemetry relegated to Diagnostics modal (Phase 7). | Aligns with companion-first philosophy: interact with Lucia first, inspect systems second. |
| **Chat Session Reset** | "Clear Screen" perceived as data loss. | Visual reset only; long-term SDM memory and friendship bond remain untouched. | Architectural separation between ephemeral chat history (`data/chat_history.json`) and subconscious memory (`SDMCore`). |
| **Runtime Authority** | Monolithic live execution on startup. | Dual runtime modes: `LiveRuntime` vs `SimulationRuntime` (`src/core/simulation/`). | Phase 8 introduced complete runtime isolation to prevent live companion contamination during simulation. |

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

---

## 5. Architecture Change Log

| Decision ID | Previous Architecture | Current Architecture | Reason | Phase | Status |
|---|---|---|---|---|---|
| **ARCH-001** | Prompted roleplay emotion | Pre-reflective continuous PAD LNN ODE ($5\text{ Hz}$) | Organic affect, eliminates amnesia and superficial roleplay | Phase 1 | Implementation Fact |
| **ARCH-002** | Theoretical HDC/SNN language core | Local GGUF SLM (LFM2.5-1.2B) + BoundaryLayer | Consumer edge hardware feasibility (4GB VRAM target) | Phase 1 | Implementation Fact |
| **ARCH-003** | RAG dense vector lookup | Kanerva SDM + Salience Decay + Synergistic Ecphory | Subconscious affective priming without robotic quotes | Phase 2 | Implementation Fact |
| **ARCH-004** | GPU ODE training | CPU `torchdiffeq.odeint` LNNTrainer | Zero VRAM contention with active GGUF LLM | Phase 4 | Implementation Fact (Isolated) |
| **ARCH-005** | Desktop ReAct screen agency | Embodied Multimodal Presence (RVC, STT, Quad-Avatar)| Preserves companion intimacy; fits 4GB VRAM ceiling | Phase 5 | Historical Decision / Pivot |
| **ARCH-006** | Technical 3-column UI | Personal Digital Room (Progressive Disclosure) | Transformed app from technical machine to intimate room | Phase 7 | Implementation Fact |
| **ARCH-007** | Character presets / pickers | Single Continuous Life ontology | Lifelong relational bond; avatars are attire, not personas | Phase 7 | Implementation Fact |
| **ARCH-008** | Single window mode | Dual Presentation: Studio Window & Mascot Mode | Unobtrusive presence on desktop during user work | Phase 6/7 | Implementation Fact |
| **ARCH-009** | Cloud STT/TTS | Fully offline local speech pipeline (`faster-whisper`, RVC)| 100% privacy, zero cloud costs, works offline | Phase 5/6 | Implementation Fact |
| **ARCH-010** | Casual chat wipes | Solemn End-of-Life boundary (`POST /lifecycle/end`) | Existential gravity; prevents relational contamination | Phase 7.7 | Implementation Fact |
| **ARCH-011** | Monolithic process startup | Runtime Isolation: `LiveRuntime` vs `SimulationRuntime` | Enforce Development $\neq$ Activation; zero live contamination | Phase 8 | Implementation Fact |
| **ARCH-012** | 5-tier inheritance (`Orchestrator` $\rightarrow$ `PresenceOrchestrator`) | `CognitiveOrchestrator` via composition (ADR-014) | Eliminates double stimulus/input bug; single turn ownership | Phase 9 | **Approved at Architecture Gate** |
| **ARCH-013** | Direct renderer `fetch()` calls in `chat.js` | Complete `window.lucia` IPC bridge mediation (ADR-019) | Security isolation and dynamic port resilience | Phase 9 | **Approved at Architecture Gate** |
| **ARCH-014** | Decorative Active Inference (logged only) | Causal Active Inference modulating Homeostasis & $k=2$ (ADR-015) | Free Energy minimization actively shapes behavior | Phase 9 | **Approved at Architecture Gate** |
| **ARCH-015** | Synchronous voice in cognitive pipeline | Decoupled Expression Service via IPC (ADR-016) | Zero text latency; failure isolation; zero compute when muted | Phase 9 | **Approved at Architecture Gate** |
| **ARCH-016** | Arbitrary 16-turn LNN batching | Two-stage plasticity: online salience + idle consolidation (ADR-017) | Zero CPU contention during conversation; salient learning | Phase 9 | **Approved at Architecture Gate** |
| **ARCH-017** | Unsynchronized cognitive turn execution | Serialized turn mutex (`asyncio.Lock` & `_turn_lock`) (ADR-018) | Single continuous life; prevents state corruption | Phase 9 | **Approved at Architecture Gate** |
| **ARCH-018** | Upstream AVX-512 `llama-cpp-python` wheel | Hybrid Ampere CUDA (`sm_86`) + Native AVX2 `ggml-cpu.dll` (ADR-020) | Resolves `0xc000001d` on Zen 2 CPUs; enables real CUDA inference | Phase 9.5 | Implementation Fact |
| **ARCH-019** | Unstructured episodic memory only | Grounded Conceptual Knowledge Subsystem (`KnowledgeStore`, ADR-021) | Distinguishes episodic memory from structured facts with provenance | Phase 16 | Implementation Fact |
| **ARCH-020** | Stateless relationship dynamics | Persistently evolving Interpersonal Relationship (`RelationshipState`, ADR-022) | Provides slow relational inertia without within-turn runaway feedback | Phase 16 | Implementation Fact |
| **ARCH-021** | Fixed conversational prompt style | Communicative Strategy & Bounded Memory Contextualization (ADR-023) | Affective and relational modulation of conversation and response pacing | Phase 16 | Implementation Fact |
| **ARCH-022** | Hardcoded blendshape/voice tags | Canonical 15-Dim Multimodal Expression Policy (`ExpressionState`, ADR-024) | Controlled, semantically consistent multimodal embodiment | Phase 16 | Implementation Fact |
| **ARCH-023** | 10-Stage Cognitive Pipeline | Canonical 16-Stage Unified Cognitive Pipeline & Isolated Stores (ADR-025) | Unified execution contract across all cognitive subsystems | Phase 16 | Implementation Fact |
| **ARCH-024** | Single-layer limbic ODE collapsing to origin | Coupled Multi-Timescale LNN (MT-LNN) + Philia Attractor Grounding (ADR-026) | Multi-minute affective continuity, autonomous stress-to-fatigue conversion, exact Philia attractor convergence | Phase 19 | Implementation Fact |
| **ARCH-025** | Open-loop text retrieval & uncoupled echo vector | Closed-Loop Affective Recollection via Slow-Field Latent Forcing ($\mathbf{r}_{\text{slow}}^{\text{bounded}}$, ADR-027) | Multi-turn affective reinstatement, memory-identity-dependent trajectory deflection, resolves Phase 11 flaw | Phase 20 | **Promoted at Research Gate & Approved for Architecture Gate** |

