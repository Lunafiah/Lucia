# Phase 16 — Affective Life Integration Architecture

> **Authoritative System Architecture: End-to-End Cognitive Pipeline, Promoted Subsystem Boundaries, Causal Graph, and Concurrency Hierarchy**  
> **Status:** Authoritative Architectural Specification  
> **Directory:** `docs/specs/lucia-phase16-Affective_Life_Integration/PHASE_16_ARCHITECTURE.md`  
> **Authority Level:** Authoritative Specification  

---

## 1. System Vision & Integration Objective

Phase 16 establishes the production architecture for Lucia's emerging **Affective Life**. It unifies the validated capabilities from Phases 10–15 into a single, cohesive, pre-reflective cognitive architecture:

```text
Stimulus
   ↓
Affective Dynamics (Layer 2 ODE)
   ↓
Homeostasis / Active Inference (Layers 3 & 4)
   ↓
Memory (Layer 5 SDM) ──┐
   ↓                   │
Knowledge (Phase 12) ──┼──► Contextual Grounding
   ↓                   │
Relationship (Phase 13)┘
   ↓
Communication Policy (Phase 15)
   ↓
Prompt Assembly & LLM Generation (Layer 6)
   ↓
Semantic Guard
   ↓
Expression Policy (Phase 14)
   ↓
Embodiment & Body (Electron IPC / Voice / Avatar)
   ↓
Observable Interaction
```

---

## 2. Production Component Boundaries & Directory Layout

To maintain strict modularity and prevent combinatorial spaghetti, production components are organized into clear domain packages with clean public interfaces:

```text
src/core/
├── emotion/                                    # LAYER 2 & 3: Limbic ODE & Homeostasis (Existing)
│   ├── emotion_core.py                         # Fast-Loop LNN ODE solver (200ms)
│   └── homeostatic_engine.py                   # Metabolic budget (energy, load, tension)
├── gating/                                     # LAYER 1: Sensory Gating (Existing)
│   └── stimulus_processor.py                   # Lexical valence, punctuation, density
├── inference/                                  # LAYER 4: Active Inference & Plasticity (Existing)
│   ├── active_inference.py                     # Linear state transition generative model
│   └── lnn_trainer.py                          # CPU online plasticity consolidation
├── memory/                                     # LAYER 5: Episodic Memory (Existing)
│   ├── sdm.py                                  # Kanerva Sparse Distributed Memory
│   ├── decay.py                                # Salience-resistant slow decay daemon
│   └── ecphory.py                              # Subconscious echo vector resonance
├── knowledge/                                  # PHASE 12 PROMOTED: Conceptual Knowledge (New)
│   ├── proposition.py                          # Proposition, Concept, Relation, Provenance
│   ├── store.py                                # Thread-safe KnowledgeStore with CRUD
│   ├── derivation.py                           # Rule-based DerivationEngine (max depth 3)
│   └── persistence.py                          # JSON serialization (data/knowledge.json)
├── relationship/                               # PHASE 13 PROMOTED: Interpersonal Relationship (New)
│   ├── state.py                                # RelationshipState (F, T, C, K in [0, 1]^4)
│   ├── signals.py                              # RelationshipSignalType definitions (structured signals)
│   ├── updater.py                              # RelationshipUpdater with temporal inertia (α = 0.03)
│   └── persistence.py                          # Atomic persistence (data/relationship.json)
├── communication/                              # PHASE 15 PROMOTED: Communicative Strategy (New)
│   ├── communication_state.py                  # CommunicationState (10D vector) & CommStrategy (5 modes)
│   ├── communication_policy.py                 # Pure policy evaluation & temporal smoothing
│   └── semantic_consistency_guard.py           # Intent and entity consistency boundary
├── expression/                                 # PHASE 14 PROMOTED: Multimodal Actuation (New)
│   ├── expression_state.py                     # ExpressionState (Exact 15 continuous dimensions)
│   ├── expression_policy.py                    # Multi-modal mapping (Text, Prosody, Blendshapes)
│   └── semantic_consistency_guard.py           # Actuator consistency verification
└── orchestrator/                               # COGNITIVE COORDINATION (Expanded)
    ├── cognitive_orchestrator.py               # 16-stage composition coordinator
    ├── prompt_assembler.py                     # Contextual prompt formatting
    └── policies.py                             # GenerationPolicy, SurprisePolicy, PlasticityPolicy
```

### Canonical ExpressionState Schema (Phase 14 Alignment)
The production `ExpressionState` adheres strictly to the 15 continuous bounded parameters validated in Phase 14:
1. `temperature_mod`: $[-0.20, +0.20]$
2. `verbosity_factor`: $[0.50, 1.50]$
3. `formality_score`: $[0.00, 1.00]$ (plus discrete `cadence_style` $\in \{\text{"concise"}, \text{"balanced"}, \text{"expansive"}\}$)
4. `pitch_shift_hz`: $[-30.0, +30.0]\text{ Hz}$
5. `speech_rate_pct`: $[-25.0, +25.0]\%$
6. `volume_pct`: $[-20.0, +20.0]\%$
7. `pause_duration_ms`: $[100.0, 1000.0]\text{ ms}$
8. `smile`: $[0.00, 1.00]$
9. `frown`: $[0.00, 1.00]$
10. `eye_open`: $[0.30, 1.20]$
11. `brow_angle`: $[-0.50, +0.50]$
12. `blush`: $[0.00, 1.00]$
13. `head_tilt_deg`: $[-10.0, +10.0]^\circ$
14. `gaze_aversion_prob`: $[0.00, 1.00]$
15. `extra_latency_ms`: $[0.0, 500.0]\text{ ms}$

---

## 3. Causal Graph & Information Flow Audit

To guarantee stability, observability, and safety, every causal edge in the integrated cognitive life is strictly audited:

| Edge # | Source Subsystem | Destination Subsystem | Data Emitted | Direction | Cadence | Range / Bounds | Lock Required | Persistence | Ablation Mechanism | Failure Mode Behavior |
|---|---|---|---|---|---|---|---|---|---|---|
| **E1** | Input Text | `StimulusProcessor` | Raw string $\to$ 16D vector $\mathbf{x}(t)$ | Forward | Per turn | $[-1.0, 1.0]$ | None | Transient | Zero stimulus | Degrades to neutral text |
| **E2** | `StimulusProcessor` | `EmotionCore` | 16D stimulus vector | Forward | Per turn | $[-1.0, 1.0]$ | `_step_lock` | Transient | `push_stimulus` bypass | Core remains at Philia attractor |
| **E3** | `EmotionCore` | `ActiveInference` | Pre/Post PAD states | Forward | Per turn | $[-1.0, 1.0]^3$ | None (snapshot copy) | Transient | Pass error $= 0.0$ | No surprise feedback |
| **E4** | `ActiveInference` | `HomeostaticEngine` | Prediction error $\mathcal{S}$ | Forward | Per turn | $[0.0, 3.46]$ | None | Transient | Set $\mathcal{S} = 0.0$ | Default homeostatic baseline |
| **E5** | `EmotionCore` | `HomeostaticEngine` | Committed PAD state | Forward | Per turn | $[-1.0, 1.0]^3$ | None (snapshot copy) | Transient | Neutral PAD | Default baseline constraints |
| **E6** | `EmotionCore` | `EcphoryEngine` | Committed PAD state | Forward | Per turn | $[-1.0, 1.0]^3$ | None | Transient | Pass empty traces | Echo vector $= \mathbf{0}$ |
| **E7** | `SDM` | `EcphoryEngine` | Stored memory traces | Forward | Per turn | Traces with tags | None | Ephemeral RAM | Clear traces | Echo vector $= \mathbf{0}$ |
| **E8** | `EcphoryEngine` | `CommunicationPolicy` | Bounded memory context ($m_{avail}$) | Forward | Per turn | $\{0.0, 1.0\}$ | None | Transient | Force $m_{avail} = 0$ | Direct factual strategy |
| **E9** | `KnowledgeStore` | `CommunicationPolicy` | Known facts & $k_{avail}$ | Forward | Per turn | Dict & $\{0.0, 1.0\}$ | `_store_lock` | Persistent | Force $k_{avail} = 0$ | Omit knowledge context |
| **E10** | `RelationshipUpdater` (Read) | `CommunicationPolicy` | Prior relationship state $R_{t-1}$ | Forward | Per turn (Pre-gen) | $[0.0, 1.0]^4$ | `_rel_lock` | Persistent | Stranger baseline ($0, 0.5, 0, 0$) | Default neutral formality |
| **E11** | `EmotionCore` + Somatic | `CommunicationPolicy` | PAD + Somatic markers | Forward | Per turn | $[-1, 1]^3 + [0, 1]^4$ | None | Transient | Actuator baseline | Direct factual strategy |
| **E12** | `CommunicationPolicy` | `PromptAssembler` | CommState + Strategy | Forward | Per turn | 10D state + mode | None | Transient | Default strategy | Standard direct prompt |
| **E13** | `CommunicationPolicy` | Generation Delay | Injected Pacing Latency $\mathcal{L}_p$ | Forward | Per turn | $[0.0, 1000.0]\text{ ms}$ | None | Transient | Force $\mathcal{L}_p = 0.0$ | Zero artificial delay |
| **E14** | `PromptAssembler` | `LLMBackend` | Assembled prompt string | Forward | Per turn | Valid UTF-8 string | None | Transient | Fallback string | Returns fallback token |
| **E15** | `LLMBackend` | `BoundaryLayer` | Raw LLM output | Forward | Per turn | Text string | None | Transient | Bypass validator | Replaces with fallback if blocked |
| **E16** | `BoundaryLayer` | `SemanticConsistencyGuard` | Safe text candidate | Forward | Per turn | Text string | None | Transient | Bypass guard | Logs consistency error |
| **E17** | `EmotionCore` + Somatic | `ExpressionPolicy` | PAD + Somatic + CommState | Forward | Per turn | Multimodal inputs | None | Transient | Actuator baseline | Default voice/face parameters |
| **E18** | `ExpressionPolicy` | `Body / Electron IPC` | 15D ExpressionState ($E_t$) | Forward | Per turn | JSON IPC payload | None | Transient | Omit IPC payload | Desktop runs local defaults |
| **E19** | Turn Completion | `RelationshipUpdater` (Update)| Structured interaction signal $S_t$ | Forward | End of turn (Post-gen) | `RelationshipSignalType` | `_rel_lock` | Persistent | Skip update | State remains unchanged |
| **E20** | Turn Completion | `SDM` | Stimulus + committed PAD | Forward | End of turn (Post-gen) | Vector + tag | None | Ephemeral RAM | Skip store | No trace written |

### Strictly Forbidden / Disallowed Feedback Edges:
- ❌ **`Body → EmotionCore`**: Body actuation (vocal/avatar) NEVER feeds back into the continuous ODE or limbic hidden state.
- ❌ **`ExpressionPolicy → EmotionCore`**: Expression parameters are strictly feedforward outputs.
- ❌ **`Memory → EmotionCore.h`**: Episodic memory vectors are NEVER injected into L2 hidden state $h \in \mathbb{R}^{32}$.
- ❌ **`LLM Output → EmotionCore`**: Self-generated text cannot act as a direct emotional stimulus loop (prevents echo-chamber affective spirals).
- ❌ **`LLM Output → RelationshipState`**: The LLM cannot hallucinate or directly rewrite relationship variables; updates occur strictly via post-turn structured signal updates.
- ❌ **Within-Turn Relationship Feedback**: Relationship state is READ at Stage 9 and UPDATED at Stage 16; $R_t$ never updates mid-turn to influence the same turn's communication.

---

## 4. Canonical 16-Stage Cognitive Pipeline Sequence & Contracts

The production `CognitiveOrchestrator` executes the cognitive turn across 16 strictly sequenced stages:

| Stage # | Stage Name | Inputs | Outputs | Locks Held | Failure Mode & Recovery |
|---|---|---|---|---|---|
| **S1** | Sensory Encoding | `input_text: str` | $\mathbf{x}(t) \in \mathbb{R}^{16}$ | `_turn_lock` | Fallback to zero vector on error |
| **S2** | Generative Prior | `pad_initial: PADState` | $\hat{p} \in \mathbb{R}^3$ | `_turn_lock` | None (pure linear algebra) |
| **S3** | Limbic Integration | $\mathbf{x}(t)$ | $p_{committed}: \text{PADState}$ | `_turn_lock`, `_step_lock` ($\le 5\text{ms}$) | Catch exception; fallback to current PAD |
| **S4** | Prediction Surprise | $p_{initial}, p_{committed}$ | $\mathcal{S} \in \mathbb{R}$ | `_turn_lock` | Fallback to $\mathcal{S} = 0.0$ |
| **S5** | Homeostatic Modulation | $\mathcal{S}, p_{committed}$ | `SomaticMarkers`, `BehavioralConstraints` | `_turn_lock` | Baseline constraints |
| **S6** | Memory Retrieval | $p_{committed}$, traces | `echo_vector: np.ndarray` | `_turn_lock` | Fallback to None (omits echo) |
| **S7** | Memory Context Extraction | `echo_vector` | $m_{avail} \in \{0, 1\}$, memory cue | `_turn_lock` | Fallback to $m_{avail} = 0$ |
| **S8** | Knowledge Retrieval | `input_text`, keywords | `known_facts: Dict`, $k_{avail}$ | `_turn_lock`, `_store_lock` ($\le 1\text{ms}$) | Fallback to $k_{avail} = 0$ |
| **S9** | **Relationship Read (Read-Only)** | None | $R_{t-1} = (\mathcal{F}, \mathcal{T}, \mathcal{K}, \mathcal{C})$ snapshot | `_turn_lock`, `_rel_lock` ($\le 100\mu\text{s}$) | Fallback to stranger baseline |
| **S10** | Communication Policy | PAD, Somatic, $R_{t-1}$, $k_{avail}$, $m_{avail}$ | $\mathbf{c}_t \in \mathbb{R}^{10}$, `CommStrategy` | `_turn_lock` | Fallback to `DIRECT_FACTUAL` |
| **S11** | Prompt Assembly | History, Somatic, Echo, Knowledge, Comm | `prompt: str` | `_turn_lock` | Catch `AssemblyError` $\to$ fallback result |
| **S12** | Conversational Pacing | $\mathcal{L}_p = \mathbf{c}_t.\text{injected\_pacing\_latency\_ms}$ | Sleep duration $\le 1000\text{ms}$ | `_turn_lock` | Clamp to $[0, 1000]\text{ms}$ |
| **S13** | LLM Generation & Boundary | `prompt`, constraints | `safe_response: str` | `_turn_lock` (LLM holds no mutex) | LLM None $\to$ fallback response; Boundary regex filter |
| **S14** | Semantic Consistency Guard | `safe_response`, known facts | `verified_response: str` | `_turn_lock` | Consistency warning; retains safe response |
| **S15** | Expression Policy & IPC | PAD, Somatic, CommState, $R_{t-1}$ | $E_t \in \mathbb{R}^{15}$ | `_turn_lock` | Fallback to neutral actuator baseline |
| **S16** | **Post-Turn Persistence & Adaptation** | `input_text`, response, stimulus | SDM store, $R_t$ update, history append | `_turn_lock`, `_rel_lock` | Wrap each store in independent try/except |

---

## 5. Persistence Architecture & Concurrency Model

### 5.1 State Persistence Classification & Test Isolation
To prevent accidental state contamination, strict storage isolation is enforced:

| State Tier | Components | Production Medium | Simulation Mode | Integration & Unit Tests |
|---|---|---|---|---|
| **Fast Transient** | PAD, ODE hidden $h$, Somatic markers, CommState, ExpressionState | Volatile RAM only | Ephemeral RAM | Ephemeral RAM |
| **Slow Persistent** | Episodic Memory Traces (SDM) | `data/memory.bin` | Ephemeral RAM | Isolated `tmp_path` |
| **Slow Persistent** | Structured Knowledge Propositions | `data/knowledge.json` | Ephemeral in-memory | Isolated `tmp_path` / in-memory store |
| **Slow Persistent** | Interpersonal Relationship State | `data/relationship.json` | Ephemeral in-memory | Isolated `tmp_path` / in-memory store |
| **Slow Persistent** | Dialogue History | `data/chat_history.json` | Ephemeral in-memory | Isolated `tmp_path` |
| **Canonical / Immutable** | Profile & Genesis (`is_onboarded=False`) | `data/profile.json` | Read-only mock | Bit-exact verification |

> [!IMPORTANT]
> **Test Storage Isolation Policy**: All integration and unit tests are strictly prohibited from writing to canonical `data/*.json`. Tests must supply temporary directory paths (`tmp_path`) or initialize stores with persistence disabled.

### 5.2 Concurrency & Lock Discipline
The architecture strictly enforces the 5-tier non-reentrant lock hierarchy (ADR-018):

```text
Tier 1: Global Cognitive Turn Mutex (_turn_lock)
        - Held during process() turn execution (serializes callers).
        - Holds no locks across network or disk I/O.
   ↓
Tier 2: Fast-Loop ODE Step Barrier (_step_lock)
        - Enforces deterministic queue draining during commit_stimulus().
        - Held for ≤ 5ms.
   ↓
Tier 3: Weight Swap / Plasticity Lock (_train_lock)
        - Held during LNN weight pointer copy.
        - Held for ≤ 2ms.
   ↓
Tier 4: Stimulus FIFO Lock (_queue_lock)
        - Protects incoming stimulus queue.
        - Held for ≤ 100μs.
   ↓
Tier 5: Limbic Snapshot Lock (_state_lock)
        - Protects PAD read/write snapshots.
        - Held for ≤ 1ms.
```

Subsystem-specific locks:
- `KnowledgeStore._store_lock`: Protects in-memory proposition dictionary (held $\le 1\text{ms}$).
- `RelationshipUpdater._rel_lock`: Protects relationship state vector copy (held $\le 100\mu\text{s}$).

---

## 6. Architectural Safety Invariants

1. **Pre-Reflective Selfhood & Multi-Layered Boundary Model**:
   - Lexical boundary checks (`BoundaryLayer` regex scanner blocking introspective declarations).
   - Structured anti-roleplay tests (controlled probing verifying absence of self-narration).
   - Architectural prohibition of self-model APIs (zero subjective ego representation).
   - *Epistemic note:* These checks represent engineering boundary enforcement, not philosophical claims about consciousness.
2. **One Continuous Life**: A single permanent companion instance. No character switchers, persona dropdowns, or romance affinity mechanics.
3. **No First Activation**: Phase 16 establishes the production architecture in the codebase, but does NOT trigger First Activation.
4. **Feedforward Actuator Decoupling**: Body actuation (speech, blendshapes, mascot window physics) has zero feedback into EmotionCore ODE.
5. **Separation of Memory and Knowledge**: Episodic memory (SDM resonance) and conceptual knowledge (structured propositions) remain strictly decoupled.
**No First Activation**: Phase 16 establishes the production architecture in the codebase, but does NOT trigger First Activation.
4. **Feedforward Actuator Decoupling**: Body actuation (speech, blendshapes, mascot window physics) has zero feedback into EmotionCore ODE.
5. **Separation of Memory and Knowledge**: Episodic memory (SDM resonance) and conceptual knowledge (structured propositions) remain strictly decoupled.
