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
| **INV-1** | **One Continuous Life** | Adding character preset pickers, "Switch Character" dropdowns, or multiple persona profiles. | Avatars are Lucia's **Appearance** (physical body/attire). Lucia is a single, permanent companion instance whose relational and episodic history is unbroken. | `AGENTS.md` §2 #1; `docs/ARCHITECTURE.md` §1.1, ADR-007 |
| **INV-2** | **No Reflective Ego** | Adding meta-self-awareness prompts (*"Reflect on who you are"*, *"Identify your feelings"*, *"As an AI..."*). | Lucia possesses a minimal operational self. Emotion is expressed through tone, rhythm, latency, and blendshapes, never self-reported text. | `AGENTS.md` §1, §2 #2; `docs/ARCHITECTURE.md` §1.1, ADR-001 |
| **INV-3** | **Preserve Memory Separation** | Deleting SDM memory traces or resetting relational history when the user clicks "Clear Screen". | "Clear Screen" resets visible chat feed (`chat_history.json`) only. Long-term SDM memory and emotional bonds are permanent and independent. | `AGENTS.md` §2 #3; `docs/ARCHITECTURE.md` §8.1 |
| **INV-4** | **Never Merge or Delete Historical Specs** | Editing or deleting files in `.kiro/specs/` or `docs/specs/`, or merging historical records into active canonical docs. | Historical phase specifications (`.kiro/specs/`, `docs/specs/`) are immutable point-in-time records. Active documentation lives exclusively in canonical `docs/`. | `AGENTS.md` §2 #4, §3.1 |
| **INV-5** | **Zero Cloud Dependencies** | Introducing OpenAI, Anthropic, ElevenLabs, or cloud STT/TTS API keys or remote network calls. | 100% local edge execution: GGUF LLM on CUDA, Edge-TTS/RVC on CPU/GPU, faster-whisper STT on local CTranslate2. | `AGENTS.md` §2 #5; `docs/ARCHITECTURE.md` ADR-002, ADR-009 |
| **INV-6** | **Strict Concurrency Discipline** | Holding `_state_lock` during model inference, or acquiring `_state_lock` before acquiring `_train_lock`. | Follow strict descending lock order ($\le 1-2\text{ms}$ holding times for memory copies). Never perform network, disk I/O, ODE integration, or LLM generation under locks. | `AGENTS.md` §2 #6, §9.1; `docs/ARCHITECTURE.md` §5.1, ADR-018 |
| **INV-7** | **Mascot Physics & Bounds Guard** | Enabling native `-webkit-app-region: drag` or allowing Aero Snap to maximize transparent mascot windows. | Use IPC `moveMascotBy(dx, dy)`, retain 800ms trackpad inertia cooldown, and enforce `maximizable: false` on Mascot BrowserWindow. | `AGENTS.md` §2 #7; `docs/ARCHITECTURE.md` §3.6.3 |
| **INV-8** | **Genesis Gate Invariant** | Modifying `data/profile.json` (`{"is_onboarded": false}`) during testing, simulation, or development. | Simulation $\ne$ Activation. The onboarding ceremony is a locked future gate preserved bit-exact. | `AGENTS.md` §2 #8, §10; `docs/ARCHITECTURE.md` §7, ADR-010, ADR-011 |

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
   - SLM/LLM là một downstream realization/rendering substrate tùy chọn; relational semantic state phải tồn tại độc lập với nó. Non-language action policies và embodiment controllers có thể trực tiếp tiêu thụ semantic interface (C1/C4) mà không cần SLM.

---

## 6. Research-First Governance & Promotion Invariants

*Source Authority: `AGENTS.md` §0, §6, §7, `docs/00_PROJECT_OVERVIEW.md` §3.1, `docs/ARCHITECTURE.md` §8 (DRAFT ADR-029)*

1. **Current Operating Mode: Post-Phase 21 Baseline**:
   - Production milestones through **Phase 21** are validated and baseline.
   - Current stage is **RESEARCH / EVIDENCE BUILDING — NOT ACTIVATION**.
   - Agents MUST NOT invent a new phase, roadmap milestone, or activation prerequisite without authoritative documentation or explicit user approval.
2. **Research Is Not Production**:
   - Passing tests in an evaluation harness does NOT constitute production implementation or authorization.
   - All research experiments must remain strictly isolated under `tests/evaluation/phaseXX/`, research specs (`docs/specs/`), and disposable fixtures.
   - Production code (`src/core/`, `electron/`, `data/`) must remain completely untouched during exploratory research (`production diff = 0`).
3. **Architecture Gate Before Implementation**:
   - No production code modification altering cognitive mechanisms, state dynamics, memory, pipeline stages, concurrency, or persistence may proceed without an approved **Production Realization Design** and ratified ADR.
4. **Authority Hierarchy**:
   `[VALIDATED / PRODUCTION IMPLEMENTED]` $\succ$ `[RESEARCH VALIDATED]` $\succ$ `[ARCHITECTURE APPROVED]` $\succ$ `[CURRENT RESEARCH]` $\succ$ `[RESEARCH]` $\succ$ `[INTEGRATION]` $\succ$ `[FUTURE GATE]`.
5. **Preservation of Evidence & Falsifiability**:
   - Negative results, failed hypotheses, rejected candidates, and ablations must be preserved as engineering evidence.
   - Historical research conclusions must never be rewritten to create an artificial linear progression.
