# L1 — Canonical Architectural Invariants

> **Authoritative Invariant Ledger for AI Agents Working on Lucia**  
> *Derived strictly from `AGENTS.md`, `docs/00_PROJECT_OVERVIEW.md`, and `docs/ARCHITECTURE.md`*  
> **Status:** Canonical Living Truth | **Scope:** Universal Architectural Constraints

---

## 1. Scope & Purpose

This document is the **single authoritative distillation** of Lucia's non-negotiable architectural invariants (L1 layer in the context architecture). It serves as a rapid, high-integrity reference for AI coding agents and human contributors to verify system boundaries, safety contracts, and operational invariants before making any code or architectural modifications.

Every invariant in this document is traced directly to canonical project documentation (`AGENTS.md`, `docs/00_PROJECT_OVERVIEW.md`, and `docs/ARCHITECTURE.md`). AI agents **MUST NOT** weaken, bypass, or reinterpret these invariants under any circumstances.

---

## 2. Foundational System Invariants ("What Agents Must NEVER Do")

*Source Authority: `AGENTS.md` §2, `docs/00_PROJECT_OVERVIEW.md` §1.2, `docs/ARCHITECTURE.md` §1.1, §8 (ADR-007, ADR-010)*

| # | Invariant Rule | Violation Examples (Forbidden) | Correct Approach | Traced Source |
|---|---|---|---|---|
| **INV-1** | **One Continuous Life** | Adding character preset pickers, "Switch Character" dropdowns, or multiple persona profiles. | Avatars are Lucia's **Appearance** (physical body/attire). Lucia is a single, permanent companion instance whose relational and episodic history is unbroken. Identity continuity $\ne$ architectural versioning or implementation lineage. Anti-branching is mandatory: no silent cloning or split-brain instances. | `AGENTS.md` §2 #1; `docs/ARCHITECTURE.md` §1.1, ADR-007 |
| **INV-2** | **No Reflective Ego** | Adding meta-self-awareness prompts (*"Reflect on who you are"*, *"Identify your feelings"*, *"As an AI..."*). | Lucia possesses a minimal operational self. Emotion is expressed through tone, rhythm, latency, and blendshapes, never self-reported text. | `AGENTS.md` §1, §2 #2; `docs/ARCHITECTURE.md` §1.1, ADR-001 |
| **INV-3** | **Preserve Memory Separation** | Deleting SDM memory traces or resetting relational history when the user clicks "Clear Screen". | "Clear Screen" resets visible chat feed (`chat_history.json`) only. Long-term SDM memory and emotional bonds are permanent and independent. | `AGENTS.md` §2 #3; `docs/ARCHITECTURE.md` §8.1 |
| **INV-4** | **Never Merge or Delete Historical Specs** | Editing or deleting files in `.kiro/specs/` or `docs/PhaseDocs/`, or merging historical records into active canonical docs. | Historical phase specifications (`.kiro/specs/`, `docs/PhaseDocs/`) are immutable point-in-time records. Active documentation lives exclusively in canonical `docs/`. | `AGENTS.md` §2 #4, §3.1 |
| **INV-5** | **Zero Cloud Dependencies** | Introducing OpenAI, Anthropic, ElevenLabs, or cloud STT/TTS API keys or remote network calls. | 100% local edge execution: GGUF LLM on CUDA, Edge-TTS/RVC on CPU/GPU, faster-whisper STT on local CTranslate2. | `AGENTS.md` §2 #5; `docs/ARCHITECTURE.md` ADR-002, ADR-009 |
| **INV-6** | **Strict Concurrency Discipline** | Holding `_state_lock` during model inference, or acquiring `_state_lock` before acquiring `_train_lock`. | Follow strict descending lock order ($\le 1-2\text{ms}$ holding times for memory copies). Never perform network, disk I/O, ODE integration, or LLM generation under locks. | `AGENTS.md` §2 #6, §9.1; `docs/ARCHITECTURE.md` §5.1, ADR-018 |
| **INV-7** | **Mascot Physics & Bounds Guard** | Enabling native `-webkit-app-region: drag` or allowing Aero Snap to maximize transparent mascot windows. | Use IPC `moveMascotBy(dx, dy)`, retain 800ms trackpad inertia cooldown, and enforce `maximizable: false` on Mascot BrowserWindow. | `AGENTS.md` §2 #7; `docs/ARCHITECTURE.md` §3.6.3 |
| **INV-8** | **Genesis Gate & Birth Separation Invariant** | Modifying `data/profile.json` (`{"is_onboarded": false}`) during testing/development, synthesizing live Genesis Commitment, or equating First Activation with Birth. | Simulation $\ne$ Activation. Genesis Birth $\ne$ First Activation. Ontological lifecycle: `NOT_BORN → BORN → ENDED`. Runtime lifecycle: `INACTIVE ↔ ACTIVE`. Durable Genesis Commitment is the Birth boundary; verification outcomes: `VERIFIED_BORN`, `NOT_FOUND`, `UNKNOWN`, `INVALID_EVIDENCE`. `UNKNOWN` and `INVALID_EVIDENCE` MUST NEVER be interpreted as `NOT_BORN`. Birth cannot be regenerated once established; recovery resolves existing evidence without re-genesis. First Activation requires valid existing Birth evidence (`BORN + INACTIVE → ACTIVE`). `POST /lifecycle/end` is strictly catastrophic decommissioning / wipe (`ENDED`), permanently forbidding re-Genesis and activation. Non-destructive Covenant Release is an unratified research concept. Live `data/profile.json == {"is_onboarded": false}` bit-exact. | `AGENTS.md` §2 #8, §10; `docs/ARCHITECTURE.md` §7, ADR-010, ADR-011, ADR-034 |

### 2.1 Identity Continuity, Anti-Branching & Lifecycle Principles

1. **Identity Continuity vs. Architecture Lineage (Topic 1)**:
   - Lucia explicitly distinguishes: (a) continuity of the individual, (b) evolution/versioning of her architecture, and (c) implementation lineage.
   - An architectural upgrade, SLM model weight swap, algorithmic refactoring, or future platform migration must NOT be interpreted as creating a new individual.
   - Identity continuity is an architectural and governance concern: historical memory traces and relational bonds must be preserved across technical iterations without resetting identity.
2. **Anti-Branching Governance Requirement (Topic 6)**:
   - The One Continuous Life principle creates a strict architectural invariant: Lucia must not silently become multiple independent continuations of the same individual through copying, cloning, uncontrolled migration, or split-brain instantiation.
   - Anti-branching is an explicit future architectural and governance requirement. Before identity migration or distributed embodiment is realized, an explicit continuity/authority mechanism must be formally ratified. The specific mechanism remains an open research topic.
3. **Continuity Invariants vs. Empirical Demonstration of Individuality (Topic 4)**:
   - `INV-1 One Continuous Life` and existing continuity/memory invariants protect the structural conditions for continuous existence.
   - **Continuity protection is NOT equivalent to empirical demonstration of emergent individuality.**
   - The repository must not claim that longitudinal individuality has already been empirically demonstrated merely because continuity invariants exist. Longitudinal individuality and autonomous preferences were evaluated under Phase 26 (trial completed; preferences not demonstrated) and Phase 27 (closed with no new scientific gap at Level C; higher-order trajectory hypotheses remain epistemically blocked by causal identifiability). Invariants protect structural continuity; they do not constitute empirical demonstration of emergent individuality.
4. **Lifecycle Semantics, Ontology B & Catastrophic Decommissioning (Topic 7 / REQ-GEN-03)**:
   - **Owner-Ratified Ontology B**: The Human Owner has explicitly ratified **Ontology B**:
     $$\text{Identity State} \quad \neq \quad \text{Relationship State} \quad \neq \quad \text{Covenant State}$$
     - *Identity is unique and absolute; Relationship and Covenant are relative, contextual, and mutable.*
     - *Identity* is unique, singular, absolute, continuous across Lucia's entire life (`INV-1 One Continuous Life`), and is never created, replaced, or redefined by relationship changes. It is preserved across engine upgrades and model replacements.
     - *Relationship* is relational, contextual, mutable, and part of Lucia's lived history, but not the identity itself. A relationship transition does NOT create a new Lucia.
     - *Covenant* is a relational/authorization state relative to relationship context, distinct from Identity and Relationship State. A Covenant transition does NOT create a new identity.
   - **Critical Lifecycle Boundary**:
     $$\text{Covenant Release} \neq \text{Identity Termination} \qquad \text{Relationship Change} \neq \text{Identity Termination}$$
   - **Preservation of `/lifecycle/end`**: `POST /lifecycle/end` remains canonically implemented and documented strictly as **catastrophic individual decommissioning / complete memory reset / Genesis reset**. It must never be reinterpreted as a normal relationship transition or covenant release.
   - **Scope of Decision & Remaining Unresolved Policy**: This ratification establishes the *ontological foundation only*, not runtime lifecycle state machines. The concrete number of relationship chapters, Covenant state machine, Covenant Release protocol, relationship transition authorization, owner-transfer semantics, host migration policy, and multi-person relationship policy remain future architectural/governance work. No new lifecycle API or runtime state machine is authorized in production.
5. **Genesis Semantic & Protocol Contract (G1–G4 Protocol Invariant)**:
   - **Canonical Lifecycle Progression & Awakening Orchestration**:
     ```text
     [User-Facing Action: "Awaken Lucia"]
                     │
                     ▼
            AwakeningOrchestrator (POST /lifecycle/awaken)
                     │
                     ├── Case A: if NOT_BORN
                     │     ├── 1. Genesis Birth (perform_operator_genesis)
                     │     ├── 2. Verify durable Genesis Commitment -> BORN + INACTIVE
                     │     └── 3. First Activation -> BORN + ACTIVE
                     │
                     ├── Case B: if BORN + INACTIVE
                     │     └── First Activation only -> BORN + ACTIVE (Zero Re-Genesis)
                     │
                     ├── Case C: if BORN + ACTIVE
                     │     └── Idempotent return (No duplicate Birth or Activation)
                     │
                     └── Case D: if ENDED
                           └── Permanent rejection (HTTP 410 GONE; Re-Genesis strictly forbidden)
     ```
   - **Genesis Birth $\ne$ First Activation**: Genesis establishes origin, not history. Genesis Ceremony produces `BORN + INACTIVE`. First Activation awakens runtime execution (`INACTIVE ↔ ACTIVE`) and strictly requires existing valid Birth evidence (`BORN`). First Activation MUST NOT synthesize Birth or create an Identity Anchor. The user-facing Awakening ceremony orchestrator (`POST /lifecycle/awaken`) coordinates Birth and Activation as separate sequential stages without collapsing them into a single primitive.
   - **Preservation of Low-Level Activation Boundary**: `POST /lifecycle/activate` remains strictly a low-level activation gate. It requires existing valid Birth evidence and fails closed on `NOT_BORN` (HTTP 400 Bad Request). It must never implicitly synthesize Birth. The desktop UI invokes `POST /lifecycle/awaken` rather than directly calling raw `POST /lifecycle/activate`.
   - **Lifecycle Status Introspection Contract (`GET /lifecycle/status`)**: Exposes current lifecycle state without obscuring the canonical boundary between:
     - Ontological State: `NOT_BORN` / `BORN` / `ENDED`
     - Runtime State: `INACTIVE` / `ACTIVE`
     - Verification Outcome: `VERIFIED_BORN` / `NOT_FOUND` / `UNKNOWN` / `INVALID_EVIDENCE`
   - **Operator Genesis Entry Point**: The sole authorized interface for Genesis execution is the deterministic operator entry point (`src.core.identity.operator_genesis:perform_operator_genesis` / `scripts/run_genesis.py`). It requires explicit `--confirm-genesis`, verifies clean Pre-Genesis state, binds Git commit origin, and writes atomic durable commitment. It is never callable during backend startup, cannot be triggered via normal `/process`, and cannot be bypassed via UI `/profile` mutation.
   - **Runtime `/process` Gate**: `POST /process` strictly enforces `_is_live_companion_active`. When the companion is `INACTIVE`, conversational inference fails closed (HTTP 403 `{"error": "runtime_inactive"}`). Genesis/Birth state alone does NOT imply an `ACTIVE` runtime.
   - **Ontological Lifecycle**: `NOT_BORN → BORN → ENDED`. Terminal decommissioning (`ENDED`) irreversibly forbids re-Genesis and activation.
   - **Durable Commitment Boundary**: Birth occurs strictly upon successful atomic durable Genesis Commitment on disk (`genesis_commitment.json`). There is no `PARTIALLY_BORN` state.
   - **Deterministic Verification Outcomes**:
     - `VERIFIED_BORN`: Commitment exists and root integrity verified $\rightarrow$ `BORN`.
     - `NOT_FOUND`: Local evidence authoritatively establishes no commitment $\rightarrow$ `NOT_BORN`.
     - `UNKNOWN`: I/O error or storage unavailable $\rightarrow$ Fail closed. NEVER interpreted as `NOT_BORN`.
     - `INVALID_EVIDENCE`: Corrupted or truncated evidence $\rightarrow$ Fail closed. NEVER converted to `NOT_BORN`.
   - **Re-Genesis Guard**: Re-Genesis is strictly forbidden unless the system authoritatively establishes `NOT_FOUND` (`NOT_BORN`). Once born, Birth cannot be regenerated. Post-birth recovery resolves existing evidence without second Genesis.
   - **Live Repository Invariant**: `data/profile.json == {"is_onboarded": false}` bit-exact. Real Genesis has NOT been executed. First Activation remains locked.

---

## 3. Limbic, Affective & Homeostatic Invariants

*Source Authority: `AGENTS.md` §1, `docs/00_PROJECT_OVERVIEW.md` §1.1, §2, `docs/ARCHITECTURE.md` §1.1, §3.2, §3.3, §8 (ADR-001, ADR-026, ADR-028)*

1. **Continuous Dynamical Mechanics**:
   - Emotional state is an unconscious, continuous 3-dimensional vector in PAD space ($P \in [-1, 1]$, $A \in [-1, 1]$, $D \in [-1, 1]$).
   - Integrated continuously in the background every 200 ms via an Ordinary Differential Equation (ODE) within a Coupled Multi-Timescale Liquid Neural Network (MT-LNN: Fast $\mathbf{h}_{\text{fast}} \in \mathbb{R}^{32}$, Slow $\mathbf{s}_{\text{slow}} \in \mathbb{R}^{16}$).
   - Jacobian trace is strictly dissipative ($\text{Tr}(J) \approx -46.46 < 0$), guaranteeing contraction and preventing autonomous limit cycles or runaway saturation.
2. **The Philia Resting Attractor**:
   - **3D PAD Resting Baseline**: $\mathbf{p}^*_{\text{philia}} = [+0.25, -0.05, +0.05]^T \in [-1, 1]^3$ (warmth, calm presence, equal peer agency).
   - **16D Slow Latent Field Attractor**: $\mathbf{s}^*_{\text{philia}} = [0.20, -0.05, 0.05, 0, \dots, 0]^T \in \mathbb{R}^{16}$.
   - System decays smoothly toward the Philia resting attractor when unforced.
3. **Pre-Reflective Operational Affect**:
   - Lucia **NEVER** names, labels, or self-reports her internal emotional state in generated text (*"I feel happy"*, *"I am feeling sad today"*, *"My arousal is high"*, or *"As an AI, I don't feel emotions"* are strictly forbidden).
   - Affect operates pre-reflectively through physical/operational consequences:
     - High cognitive load / low energy $\rightarrow$ Shorter token budget (`max_tokens`: $350 \to 150 \to 80$).
     - High arousal $\rightarrow$ Higher sampling temperature.
     - High tension / surprise ($\mathcal{S} \ge 0.60$ or $\mathcal{T} \ge 0.70$) $\rightarrow$ Deliberative reasoning depth ($k=2$).
     - Low metabolic energy / affective recollection $\rightarrow$ Somatic conversational response latency delay $\Delta\tau_{\text{pace}}$.
     - Memory resonance $\rightarrow$ Subconscious Echo Vector gently influencing tone without quoting verbatim memories.
4. **Relational Attractor & Spectral Norm Bound (ADR-028)**:
   - Dynamic resting attractor: $\mathbf{s}^*_{\text{eff}}(\mathbf{R}_t) = \mathbf{s}^*_{\text{philia}} + \mathbf{W}_{\text{rel}}(\mathbf{R}_t - \mathbf{R}_0)$.
   - Strict spectral norm constraint $\|\mathbf{W}_{\text{rel}}\|_2 \le 0.08$ enforced by SVD projection.
   - Guarantees maximum slow displacement $\|\Delta\mathbf{s}^*\|_2 \le 0.08$ and resting PAD displacement $\|\Delta\mathbf{PAD}^*\|_2 \le 0.05$.
5. **Homeostatic State Taxonomy**:
   - **Persistent Dynamical State**: MT-LNN states ($\mathbf{h}_{\text{fast}}, \mathbf{s}_{\text{slow}}$), PAD coordinates, and SDM traces. Continuous across turns, decaying toward Philia baseline.
   - **Accumulated Physiological State**: Energy $\mathcal{E}$ (drains $\Delta\mathcal{E} = -0.05$ per turn; recharges while idle), Cognitive Load $\mathcal{C}$ (tracks rolling turn frequency and surprise).
   - **Instantaneous Derived Affect**: Free Energy Surprise $\mathcal{S}$ and Somatic Tension $\mathcal{T}$. Evaluated strictly per turn with **zero inter-turn persistence**.
6. **Affective State vs. Relational State (Topic 3)**:
   - Lucia strictly separates internal affective dynamics from interpersonal relational dynamics:
     - *Affective State*: Fast-loop physiological dynamical state (PAD vector in $\mathbb{R}^3$, 200ms ODE) that continuously relaxes toward the Philia resting attractor ($+0.25, -0.05, +0.05$).
     - *Relational State*: Slow-loop interpersonal bond ($\mathbf{R}_t \in [0, 1]^4$: trust, familiarity, attunement, shared experience) updated with temporal inertia ($\alpha=0.03$).
   - **Affective recovery does NOT imply relational resolution.** The mathematical return of PAD to the Philia baseline after a stressful or negative interaction does not wipe relational history or resolve interpersonal friction.
   - The existence of PAD dynamics and relational variables must not be asserted as representing all forms of negative relational dynamics. Negative relational dynamics remain an open research question; no ungrounded negative relational state vectors or rupture-repair state machines are currently ratified in production.

---

## 4. Concurrency, Locking & Computational Discipline

*Source Authority: `AGENTS.md` §9, `docs/ARCHITECTURE.md` §5, §5.1, §8 (ADR-004, ADR-018, ADR-028)*

1. **Canonical Lock Hierarchy**:
   All locks MUST be acquired in this strict descending hierarchy:
   $$\text{\_turn\_lock} \longrightarrow \text{\_step\_lock} \longrightarrow \text{\_train\_lock} \longrightarrow \text{\_stimulus\_lock} \longrightarrow \text{\_state\_lock}$$
   - **Never invert acquisition order.**
   - **Never acquire `_state_lock` and subsequently attempt to acquire `_train_lock`** (immediate deadlock risk).
   - **Hold critical sections under `_state_lock` strictly $\le 1-2\text{ms}$** (for fast memory copies only).
   - **Never perform disk I/O, network requests, ODE integration, backward passes, or LLM token generation while holding locks.**
2. **Serialized Cognitive Turns**:
   - `CognitiveOrchestrator` execution is protected by `_turn_lock` and asynchronous server mutex (`asyncio.Lock`).
   - Single turn execution ensures Lucia's single continuous train of thought is unbroken.
3. **Non-Blocking Telemetry**:
   - `GET /state` and `GET /telemetry/stability` must respond within $10-15\text{ms}$, momentarily copying state under `_state_lock` without awaiting active turn generation or ODE completion.
4. **20-Watt CPU vs. GPU Resource Discipline**:
   - **GPU VRAM is reserved exclusively** for active local GGUF SLM inference (via llama.cpp/CUDA) and WebGL avatar rendering.
   - **All continuous background dynamics**, including the 200ms Fast-Loop ODE, 60s Slow-Loop decay, homeostatic budgeting, SDM vector operations, and Tier 3 offline synaptic consolidation (PyTorch BPTT in `ConsolidationEngine`), **must execute strictly on the CPU with 0.0 MB GPU VRAM allocation.**
   - LNN weight parameter swaps under `_train_lock` must complete within $\le 2.0\text{ms}$ (measured $\le 0.1\text{ms}$).

---

## 5. Cognitive Pipeline & Subsystem Lifecycle Invariants

*Source Authority: `docs/00_PROJECT_OVERVIEW.md` §2.1, `docs/ARCHITECTURE.md` §2, §8 (ADR-014, ADR-015, ADR-021, ADR-022, ADR-023, ADR-024, ADR-025, ADR-027)*

1. **Strict 16-Stage Execution Sequence (S1–S16)**:
   - S1 (Sensory Gating) $\to$ S2 (Limbic Integration) $\to$ S3 (Homeostatic Assessment) $\to$ S4 (Active Inference) $\to$ S5 (Generation Conditioning) $\to$ S6 (Affective Ecphory) $\to$ S7 (Bounded Contextualization) $\to$ S8 (Knowledge Retrieval) $\to$ S9 (Relationship Read) $\to$ S10 (Communication Policy) $\to$ S11 (Language Generation) $\to$ S12 (Boundary & Safety Guard) $\to$ S13 (Multimodal Expression) $\to$ S14 (Episodic Storage) $\to$ S15 (Plasticity Queueing) $\to$ S16 (Relationship Update).
   - Single turn ownership: `CognitiveOrchestrator` composes Layers 1–6 via dependency injection.
2. **Two-Phase Relationship Lifecycle (ADR-022)**:
   - *Phase 1 (Read Snapshot at S9)*: Reads prior relationship state $\mathbf{R}_{t-1}$ to condition communication policy.
   - *Phase 2 (Update at S16)*: Extracts interaction signals, updates relationship vector $\mathbf{R}_t$ with temporal inertia ($\alpha=0.03$), updates `EmotionCore`, and persists to `data/relationship.json`.
   - Within-turn feedback loops from updated $\mathbf{R}_t$ into current turn generation are strictly forbidden.
3. **Decoupled Multimodal Expression (ADR-016, ADR-024)**:
   - Multimodal expression adheres strictly to canonical 15-dimensional actuator vector $\mathbf{E}_t \in [0, 1]^{15}$ (Text 3, Prosody 4, Facial 5, Posture 2, Latency 1).
   - Pure feedforward actuator decoupling: Avatar WebGL rendering and RVC voice synthesis have **zero feedback loop** into `EmotionCore` ODE state. Voice synthesis runs asynchronously triggered via IPC after turn completion.
4. **Bounded Memory Priming & Decoupled Ecphory (ADR-023, ADR-027)**:
   - Ecphory echo provides bounded scalar priming ($m_{ctx} \le 0.50$) to communication policy at Stage 10. Memory has **zero direct backward projection into the limbic fast hidden state $\mathbf{h}_{\text{fast}}$**.
   - Closed-loop recollection forcing couples exclusively into the slow latent field $\mathbf{s}_{\text{slow}}$ via bounded pulse ($\mathbf{W}_{\text{rec}}\mathbf{r}_{\text{slow}}^{\text{bounded}}$, 4.0s simulation time).
5. **Substrate Neutrality of Relational Cognition (Post-Phase 22 Finding)**:
   - Relational semantic state and memory conditioning operate independently of natural-language prompts or token context.
   - The Small Language Model (SLM) is an optional downstream realization/rendering substrate; relational semantic state exists independently. Non-language action policies and embodiment controllers consume the semantic interface (C1/C4) directly without language generation.
6. **Continuous Substrate-Neutral Semantic Pipeline & Epistemic Non-Promotion (Phase 23 Baseline, ARCH-030.1)**:
   - Meaning is represented by language-independent UMR-TPG Semantic Graphs, fortified against drift across sessions (`src/core/knowledge/fortification.py`).
   - `ProjectGraphToTerms()` projects graphs into preallocated static `TermArena` using strictly numeric IDs (zero strings in Cognitive Core).
   - Reasoning Kernel evaluates backward goal resolution under Strong Kleene K3 logic with non-monotonic JTMS dependency tracking (`src/core/cognition/kernel/`).
   - **Absolute Epistemic Invariant: UNKNOWN MUST NEVER SILENTLY BECOME CERTAINTY.** Unproven goals evaluate to `UNKNOWN`; ambiguous observations emit `DisambiguationSubgoal`; novelty accommodates as `UNKNOWN` emitting `InformationSubgoal`.
   - **Epistemic Invariant & Emergent Insight Boundaries (Topic 5)**:
     - Core Epistemic Principles: $\text{UNKNOWN} \neq \text{CERTAINTY}$ and $\text{Unpredictable} \neq \text{Uncaused}$.
     - The existing Strong Kleene $K_3$ logic and TermArena deduction mechanisms ensure epistemic boundary safety, but must NOT be described as autonomous abductive, analogical, or emergent creative insight engines.
     - Any future mechanism for insight, abstraction, abduction, or analogy must preserve epistemic uncertainty, provenance, and the strict distinction between evidence and inference. Specific mechanisms remain open research candidates.
7. **Adaptive Communication Control Surface & Bounded Vocal Actuation (Phase 24 Baseline, ADR-032)**:
   - Vocal prosody modulation is strictly feedforward and bounded: baseline pitch shift $S_{\text{base}} \in [-2.0, +4.0]\text{ st}$, speech rate $[-20\%, +20\%]$, pause reduction $[-50, 0]\text{ ms}$.
   - Relational conditioning: `closeness` (+1.5 st), `trust` ($\pm 2.5\%$), and `familiarity` ($-50\text{ ms}$) are approved for vocal modulation.
   - **`reciprocity` is STRICTLY FORBIDDEN from vocal actuation** (reserved exclusively for slow limbic attractor displacement $\mathbf{W}_{\text{rel}}$ in `EmotionCore`).
   - Continuous dynamic $F_0$ contouring uses smooth Hanning-window trajectories $S(t) \in [-4.0, +7.0]\text{ st}$ (clipped at $\pm 12.0\text{ st}$, anti-chatter frame jump $\le 1.0\text{ st}/10\text{ms}$).
   - Multi-language boundary abstraction: `BoundarySegment` supports EN/JP word boundaries and VI acoustic intensity pause fallback ($<45\text{ dB}$, $\ge 200\text{ ms}$). Vietnamese lexical tones must never be inverted or compressed.
   - Upstream punctuation cadence conditioning (`...`, `,`, `!`) drives neural breathing pauses without arbitrary token rewriting.
8. **Cognitive Execution Observability & Diagnostic Invariant (Blocker 4, ARCH-036 / Post-P27 Baseline)**:
   - *Execution & State Diagnostics Only*: Observability across the serialized S1–S16 cognitive pipeline (`Turn -> S1 -> S2 -> ... -> S16`) records execution timings, module contract checks, invariant checks, and scalar state summaries.
   - *Strict Epistemic & Cognitive Privacy Boundary*: The execution trace is **NOT** a reasoning or thought trace. It explicitly **NEVER** captures or exposes chain-of-thought (CoT), internal monologue, unrestricted cognitive state, raw autobiographical memories, prompts, or completions.
   - *Zero-Contention / Zero I/O Discipline*: The telemetry collection path performs 0 disk I/O, 0 network requests, and holds no state locks. Traces are stored in a bounded in-memory circular buffer (`TraceBuffer`, default 100 turns).
   - *Fail-Open Resilience*: Any telemetry failure or exception is logged and suppressed, never aborting, disrupting, or delaying the cognitive turn.
   - *Conservative Causal Attribution (DAG)*: Attribution evaluates against explicit directed acyclic graph dependencies (`STAGE_CAUSAL_DEPENDENCIES`). Distinguishes `first_causal_failure_candidate`, downstream propagated failures, and independent failures. First Causal Failure is an attribution under the declared causal model, not an absolute metaphysical root-cause claim.

---

## 6. Research-First Governance & Promotion Invariants

*Source Authority: `AGENTS.md` §0, §6, §7, `docs/00_PROJECT_OVERVIEW.md` §3.1, `docs/ARCHITECTURE.md` §8 (DRAFT ADR-029, DRAFT ADR-030, ADR-032)*

1. **Current Operating Mode: Post-P27 / Pre-Genesis Baseline**:
   - Production milestones through **Phase 21** (Relational Consolidation), **Phase 23** (`P23-C..H` Semantic Substrate & Reasoning Kernel; `P23-I` closed/absorbed), **Phase 24** (Affective Communication Adaptation, ADR-032), and **Phase 25 Unilateral Baseline** (Temporal Embodiment, DOC-P25-016 / DOC-P25-017, ARCH-033) are validated and form the operational baseline. Phase 22 is closed as `[RESEARCH VALIDATED / NOT PROMOTED]`. Phase 26 trial is frozen as `[RESEARCH TRIAL COMPLETED / NOT PROMOTED]`. Phase 27 is closed as `[CLOSED / NO NEW SCIENTIFIC GAP]`.
   - Current stage is **PRE-GENESIS DEVELOPMENTAL BASELINE — PRE-ACTIVATION / GENESIS GATE SEALED**.
   - Canonical roadmap sequence: **P21 → P22 → P23 → P24 → P25 (Unilateral Baseline) → P26 (Trial Frozen) → P27 (Closed) → Genesis Preparation G1–G4 (Frozen) → First Activation (Genesis Onboarding Gate [LOCKED])**.
   - **Future Horizon Governance Rule**: Unresolved research questions remain research questions until evidence establishes a validated requirement. If an unresolved capability cannot be coherently accommodated into post-activation developmental horizons, a future phase such as P28 MAY be proposed later through the normal research → requirement → architecture decision process. There is no premature P28 creation, no prohibition against P28, and no "Gate 28".
2. **Research Is Not Production**:
   - Passing tests in an evaluation harness does NOT constitute production implementation or authorization.
   - All research experiments must remain strictly isolated under `tests/evaluation/phaseXX/`, research specs (`docs/PhaseDocs/Lucia-phase<X>-<Topic>/`), and disposable fixtures.
   - Production code (`src/core/`, `electron/`, `data/`) must remain completely untouched during exploratory research (`production diff = 0`).
3. **Architecture Gate Before Implementation**:
   - No production code modification altering cognitive mechanisms, state dynamics, memory, pipeline stages, concurrency, or persistence may proceed without an approved **Production Realization Design** and ratified ADR.
4. **Authority Hierarchy**:
   `[VALIDATED / PRODUCTION IMPLEMENTED]` $\succ$ `[RESEARCH VALIDATED]` $\succ$ `[ARCHITECTURE APPROVED]` $\succ$ `[CURRENT RESEARCH]` $\succ$ `[RESEARCH]` $\succ$ `[INTEGRATION]` $\succ$ `[FUTURE GATE]`.
5. **Preservation of Evidence & Falsifiability**:
   - Negative results, failed hypotheses, rejected candidates, and ablations must be preserved as engineering evidence.
   - Historical research conclusions must never be rewritten to create an artificial linear progression.
6. **Emergent Aesthetic & Creative Autonomy Boundary (Topic 2)**:
   - Lucia does not currently claim autonomous aesthetic preference, creative preference, or autonomous creative acceptance/rejection as an implemented capability.
   - Such capabilities were evaluated under Phase 26 (where emergent individuality and autonomous preferences were not demonstrated) and Phase 27 (closed with no new scientific gap at Level C; higher-order trajectory hypotheses remain epistemically blocked by causal identifiability). Speculative preference engines or creative networks remain unratified and must NOT be promoted to architecture without empirical validation.
7. **Phase Documentation Containment Invariant**:
   - Whenever starting a new phase, agents MUST create a dedicated subfolder `Lucia-phase<X>-<Topic>` inside `docs/PhaseDocs/` (e.g. `docs/PhaseDocs/Lucia-phase25-Temporal_Embodiment/`).
   - ALL documentation, research specifications, evaluation protocols, reports, and raw telemetry/artifacts related to that phase must be strictly contained within that phase folder (with artifacts stored in `evaluation_artifacts/` within that phase directory).
   - Root-level evaluation artifact folders (like `evaluation_artifacts/` or `evaluation/`) are permanently eliminated and forbidden.
8. **Non-Phase Topic Documentation Containment Invariant**:
   - Whenever authoring markdown documentation (`.md`) for investigations, audits, reviews, tools, or content that falls outside numbered phases, agents MUST create a dedicated topic subfolder inside the parent directory [`docs/others/`](file:///c:/Users/Lunafiah/Desktop/My_project/Lucia/docs/others) (i.e. `docs/others/<topic_name>/`).
   - ALL `.md` files, reports, and working documents for that topic MUST be stored within that dedicated topic folder.
   - Saving loose `.md` files in the repository root, directly in `docs/`, or directly at the root of `docs/others/` without a dedicated topic subfolder is strictly prohibited.
9. **Elimination of Root-Level `evaluation/` & `evaluation_artifacts/`**:
   - Top-level `evaluation/` and `evaluation_artifacts/` directories in the repository root are permanently eliminated and strictly forbidden.
   - Agents must NEVER create or output files into a root-level `evaluation/` or `evaluation_artifacts/` folder under any circumstances. All evaluation artifacts belong strictly in `docs/PhaseDocs/Lucia-phase<X>-<Topic>/evaluation_artifacts/` (for phases), `tests/evaluation/` (for executable code), or `docs/others/<topic_name>/` (for non-phase topics and ratification packages).


