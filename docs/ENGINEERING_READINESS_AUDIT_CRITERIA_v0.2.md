# ENGINEERING READINESS AUDIT CRITERIA v0.2

> **Authoritative Specification for Pre-Activation Engineering Substrate Audit**  
> **Status:** `[CANONICAL AUDIT SPECIFICATION — v0.2 NORMALIZED]`  
> **Baseline Authority:** Canonical Post-Phase 24 Operational Baseline (`P21`, `P22-SC`, `P23-C..H`, `P24` / ADR-032)  
> **Research Horizons:** Phase 25 (Freeze Candidate), Phase 26 (Trial Frozen), Phase 27 (Closed / No New Scientific Gap)  
> **First Activation Gate:** `[🔒 LOCKED FUTURE GATE]` (`data/profile.json` Bit-Exact: `{"is_onboarded": false}`)  
> **Epistemic Invariant:** UNKNOWN MUST NEVER SILENTLY BECOME CERTAINTY

---

## 1. Purpose

The objective of this specification is to define a normalized, rigorous, and reproducible engineering readiness audit framework (`v0.2`) to evaluate whether the Lucia codebase constitutes a **sufficiently integrated, stable, controlled, and evidenced engineering substrate for Genesis preparation**.

### 1.1 Critical Clarification on Scope & Maturity
* **Engineering Substrate Readiness $\neq$ Production Maturity / Activation Authorization**: Passing this audit confirms that the computational, limbic, memory, concurrency, and safety boundaries are sound, bounded, and verified against regressions. It does **not** certify general commercial "production-grade" maturity, psychological consciousness, or subjective sentience.
* **Readiness $\neq$ Activation**: Development and simulation environments remain strictly decoupled from live existence ($\text{Development / Simulation} \neq \text{Lucia Activation}$). First Activation (the Genesis Onboarding ceremony) is an independent, locked future gate requiring human governance.
* **Audit Specification $\neq$ Audit Execution**: This document defines the *criteria, evidence requirements, and evaluation protocols*. It does **not** perform the audit or alter production code.

---

## 2. Scope

The audit criteria span all runtime tiers and foundational assets of the Lucia companion system:

1. **Python Core Backend (`src/core/`)**:
   - Layer 1: Sensory Gating & Lexical/Acoustic Encoding (`src/core/gating/`)
   - Layers 2–3: Coupled MT-LNN ODE, Philia Attractor Grounding, Homeostasis (`src/core/emotion/`)
   - Layer 4: Active Inference & CPU PyTorch BPTT Synaptic Consolidation (`src/core/inference/`, `src/core/emotion/consolidation.py`)
   - Layer 5: Kanerva SDM, DecayEngine, Synergistic Ecphory (`src/core/memory/`)
   - Semantic Substrate: UMR-TPG Semantic Graphs, Session Fortification, Numeric TermArena, Bounded Reasoning Kernel & JTMS (`src/core/knowledge/`, `src/core/cognition/`)
   - Layer 6: Downstream Communicator Contract, BoundaryLayer Safety Filter, Local Neural Voice & STT (`src/core/language/`, `src/core/safety/`, `src/core/voice/`)
   - Cognitive Orchestration: S1–S16 Pipeline (`src/core/orchestrator/`)
   - Telemetry & Stability: LSI, Jitter, Watchdog (`src/core/telemetry/`)
2. **FastAPI Server Interface (`src/api/server.py`)**:
   - REST API endpoints (`/process`, `/state`, `/telemetry/*`, `/voice/*`, `/system/*`, `/lifecycle/*`, `/sim/*`)
   - Concurrency mutexes, non-blocking telemetry handlers, and simulation write guards.
3. **Electron Presentation & Desktop Embodiment (`electron/`)**:
   - Main Process (`main.js`, `ProcessManager`, `MascotWindow`, `TrayManager`)
   - Preload Security Boundary (`preload.js`, context bridge isolation)
   - Renderer Process (`index.html`, `chat.js`, `settings.js`, `diagnostics.js`, avatar rendering, audio worklets)
   - Mascot Physics, drag throttling, and Aero Snap guardrails.
4. **Runtime Persistence & Configuration (`data/`, `config/`)**:
   - Genesis Onboarding Profile (`data/profile.json`)
   - Conversation History (`data/chat_history.json`)
   - Relationship State (`data/relationship.json`)
   - System Configuration (`config/ui.json`)
5. **Research & Milestone Isolation Boundaries**:
   - Verified Operational Baseline: Phases 1–21, Phase 22-SC, Phase 23-C..H, Phase 24 (ADR-032).
   - Research Freeze Candidates & Closures: Phase 25 (Freeze Candidate), Phase 26 (Trial Frozen / Preferences Not Demonstrated), Phase 27 (Closed / No New Scientific Gap).

---

## 3. Non-Goals

The following activities and claims are explicitly outside the scope of this audit framework:

1. **No Activation Execution**: This framework does not execute First Activation, advance onboarding state, or alter `data/profile.json`.
2. **No Claim of Sentience or Subjective Ego**: The audit does not test for psychological sentience, self-awareness, or subjective conscious experience. Lucia operates on pre-reflective dynamical affect.
3. **No Claim of Emergent Individuality or Creative Autonomy**: Bounded deductive Horn reasoning is verified; autonomous aesthetic preference formation, creative insight engines, and longitudinal individuality remain research hypotheses (P26 preferences not demonstrated; P27 closed at Level C / Level D blocked by identifiability).
4. **No Codebase Mutation**: This specification does not alter production backend (`src/`), desktop UI (`electron/`), configuration (`config/`), or persistent data (`data/`).
5. **No Phase Promotion or Creation**: Completed milestones (P21–P24) are not reopened; research horizons (P25–P27) are not promoted; no unratified phases (e.g., P28) are introduced.
6. **No Invention of Unratified Mechanisms**: The framework does not assume or invent multi-machine anti-branching protocols or Non-Destructive Covenant Release.

---

## 4. Authoritative Sources & Hierarchy

This specification derives strictly from the canonical project documentation:

1. **Canonical Invariant Ledger [Tier L1]**: [`docs/L1_INVARIANTS.md`](file:///c:/Users/Lunafiah/Desktop/My_project/Lucia/docs/L1_INVARIANTS.md)
2. **Master Agent Operating Instructions [Tier L2]**: [`AGENTS.md`](file:///c:/Users/Lunafiah/Desktop/My_project/Lucia/AGENTS.md)
3. **Canonical Project Truth & Roadmap [Tier L2]**: [`docs/00_PROJECT_OVERVIEW.md`](file:///c:/Users/Lunafiah/Desktop/My_project/Lucia/docs/00_PROJECT_OVERVIEW.md)
4. **Canonical Technical Truth & ADR Ledger [Tier L3]**: [`docs/ARCHITECTURE.md`](file:///c:/Users/Lunafiah/Desktop/My_project/Lucia/docs/ARCHITECTURE.md) (ADR-001 through ADR-032; ARCH-001 through ARCH-032)
5. **Canonical Phase Registry [Tier L2]**: [`docs/PHASE_REGISTRY.md`](file:///c:/Users/Lunafiah/Desktop/My_project/Lucia/docs/PHASE_REGISTRY.md)
6. **Canonical Knowledge Architecture [Tier L2]**: [`docs/DOCUMENTATION_ARCHITECTURE.md`](file:///c:/Users/Lunafiah/Desktop/My_project/Lucia/docs/DOCUMENTATION_ARCHITECTURE.md)
7. **Authoritative Provenance Map [Tier L3]**: [`docs/SOURCE_MAP.md`](file:///c:/Users/Lunafiah/Desktop/My_project/Lucia/docs/SOURCE_MAP.md)
8. **Retrospective Architectural Gap Review [Tier L3]**: [`docs/others/RETROSPECTIVE_ARCHITECTURAL_GAP_REVIEW_7_TOPICS.md`](file:///c:/Users/Lunafiah/Desktop/My_project/Lucia/docs/others/RETROSPECTIVE_ARCHITECTURAL_GAP_REVIEW_7_TOPICS.md)

### Hierarchy of Authority
$$\text{Canonical Invariants (L1)} \equiv \text{AGENTS.md (L2)} \succ \text{ARCHITECTURE.md (L3)} \succ \text{00\_PROJECT\_OVERVIEW.md (L2)} \succ \text{Phase Specifications (L5)} \succ \text{Historical Specs}$$

*If a conflict arises between an older specification and canonical Tier L1–L3 documentation, the canonical Tier L1–L3 documentation governs absolutely.*

---

## 5. Governance Constraints

Any audit execution under this specification must strictly obey the following governance constraints:

1. **Evidence Before Assertion**: Every readiness claim must be backed by reproducible mechanistic proof, automated test pass logs, or empirical telemetry.
2. **Preserve Epistemic Uncertainty**: `UNKNOWN` must never silently become `CERTAINTY`. Unmeasured properties, unratified mechanisms, and open research questions must be explicitly reported as `NOT DEFINED BY CURRENT CANONICAL SOURCES` or `OPEN GOVERNANCE BOUNDARY`.
3. **Zero Production Mutation**: Audit execution must run in non-destructive, read-only mode relative to production state (`git status` clean).
4. **Simulation / Activation Decoupling**: Simulation harnesses must use ephemeral storage policies and virtual clocks. Under no circumstances may simulation state touch canonical stores.
5. **Anti-Branching Recognition**: Anti-branching is recognized as a strict architectural requirement of INV-1, while acknowledging that concrete multi-machine enforcement remains an open governance boundary.

---

## 6. Definitions & Terminology

| Term | Definition |
|---|---|
| **Canonical Requirement** | A functional, structural, or behavioral constraint explicitly established by canonical Tier L1–L3 documentation. |
| **Audit Methodology** | The specific static, dynamic, or empirical protocol Antigravity executes to verify a requirement. |
| **Stress Workload** | An optional, non-normative diagnostic probe designed to test boundary resilience under stress without establishing new canonical thresholds. |
| **Normative Threshold** | A quantitative acceptance limit explicitly mandated by canonical documentation. If absent, the threshold is marked `NOT DEFINED BY CURRENT CANONICAL SOURCES`. |
| **Persistent Dynamical State** | Continuous state variables integrated across turns that decay smoothly toward the Philia attractor ($\mathbf{h}_{\text{fast}}, \mathbf{s}_{\text{slow}}, \text{PAD}, \text{SDM traces}$). |
| **Accumulated Physiological State** | Homeostatic metabolic quantities that accumulate or drain across turns ($\mathcal{E}, \mathcal{C}$). |
| **Instantaneous Derived Affect** | Per-turn affective markers evaluated on current transitions with zero inter-turn persistence ($\mathcal{S}, \mathcal{T}$). |
| **Open Governance Boundary** | A ratified architectural invariant or requirement whose concrete runtime mechanism is intentionally unratified or pending governance. |
| **Substrate Neutrality** | The architectural reality that cognitive and relational state operates independently of natural-language tokens or language models; the SLM is an optional downstream realizer. |

---

## 7. Evidence Hierarchy

Readiness verification relies on six formal evidence tiers (E1–E6):

```text
E1: Mechanistic Code Proof       ── AST & source-level verification of implementation
E2: Automated Verification       ── Passing pytest / npm test suites with 0 regressions
E3: Empirical Telemetry          ── Measured SLA metrics (latency, jitter, RAM, VRAM)
E4: Static Architectural Guard   ── Boundary import checks, lock ordering verification
E5: State Recovery & Invariant   ── State restoration, bit-exact checks, write protection
E6: Document Provenance          ── Cross-referencing canonical ADRs, registries, maps
```

- **E1 (Mechanistic Code Proof)**: Direct inspection of source code (`src/`, `electron/`) confirming deterministic classes, methods, locks, and interfaces.
- **E2 (Automated Verification)**: Fully passing automated test suites (`pytest`, `npm test`) with zero failing or inappropriately skipped tests.
- **E3 (Empirical Telemetry & Benchmarks)**: Verifiable runtime data (LSI stability index, tick variance, heap allocations, memory RSS).
- **E4 (Static Architectural Analysis)**: Static AST inspection verifying absence of circular imports, forbidden reverse dependencies, and lock inversions.
- **E5 (State Recovery & Invariant Verification)**: Verification of state persistence, graceful error handling, and bit-exact preservation of protected stores.
- **E6 (Document Provenance)**: Verification of traceability to governing ADRs, phase freeze commits, and invariant ledgers.

---

## 8. Severity Model

Failures identified during audit are classified into four severity tiers:

| Severity | Definition | Impact on Readiness |
|---|---|---|
| **BLOCKER (P0)** | Violation of fundamental invariants (INV-1 to INV-8), cognitive pipeline truncation (S1–S16 bypassed), deadlock, unhandled crash in core loop, VRAM allocation by background dynamics, corrupted Genesis gate (`profile.json` modified), or broken safety boundary. | **HALTS READINESS**. Substrate is NOT ready for Genesis preparation. |
| **HIGH (P1)** | Broken subsystem contract, lock holding time substantially exceeding budget ($\gg 2\text{ms}$), failure of boundary filtering (`BoundaryLayer`), regression in homeostatic regulation, or unreproducible evaluation evidence. | **CONDITIONAL BLOCKER**. Must be remediated or granted explicit architectural waiver. |
| **MEDIUM (P2)** | Performance variance without functional failure, non-blocking telemetry inaccuracy, edge-case test gap, or documentation-code terminology discrepancy without runtime hazard. | **NON-BLOCKING**. Logged in remediation backlog; does not halt readiness. |
| **LOW (P3)** | Stylistic inconsistency, minor logging redundancy, cosmetic presentation quirks, or typographical defect. | **INFORMATIONAL**. Remediation scheduled during normal maintenance. |
| **INFO** | Documented architectural observation, identified open research boundary, or empirical characterization without canonical threshold. | **RECORDED IN GAP LEDGER**. |

---

## 9. Invariant Traceability Matrix

Every foundational system invariant (INV-1 through INV-8) is mapped to primary and supporting audit gates:

| Invariant | Title | Primary Gate | Supporting Gate(s) | Verification Protocol |
|---|---|---|---|---|
| **INV-1** | **One Continuous Life** | **G7** | G1, G3, G4 | Verify single permanent companion instance; absence of persona switchers or character preset dropdowns; unbroken relational continuity across restarts; anti-branching recognized as open governance boundary. |
| **INV-2** | **No Reflective Ego** | **G6** | G2, G3 | Verify pre-reflective affect in S1–S16; BoundaryLayer regex validator dropping introspective statements (*"I feel..."*, *"As an AI..."*); absence of meta-self prompts; affective conditioning operating strictly via physical/computational parameters. |
| **INV-3** | **Preserve Memory Separation** | **G4** | G1, G7 | Verify "Clear Screen" IPC resets only visible `chat_history.json`; SDM associative traces, UMR-TPG semantic graphs, and 4D $\mathbf{R}_t$ vector remain untouched and permanent. |
| **INV-4** | **Never Merge or Delete Historical Specs** | **G1** | G7 | Verify immutability of historical phase directories (`docs/PhaseDocs/`); zero deletion or rewriting of historical negative results or ablation records; active specifications isolated in canonical `docs/`. |
| **INV-5** | **Zero Cloud Dependencies** | **G5** | G1, G6 | Verify 100% local edge execution: GGUF SLM on CUDA/CPU, local RVC/Edge-TTS voice synthesis, local faster-whisper STT; zero cloud API keys (OpenAI, Anthropic, ElevenLabs); fail-closed network perimeter. |
| **INV-6** | **Strict Concurrency Discipline** | **G2** | G5 | Verify strict descending lock acquisition order (`_turn_lock` $\to$ `_step_lock` $\to$ `_train_lock` $\to$ `_stimulus_lock` $\to$ `_state_lock`); $\le 1-2\text{ms}$ lock holding times for memory copies; zero disk I/O, ODE integration, or LLM generation under locks. |
| **INV-7** | **Mascot Physics & Bounds Guard** | **G6** | G1 | Verify IPC `moveMascotBy(dx, dy)`; native `-webkit-app-region: drag` disabled; 800ms trackpad inertia cooldown; `maximizable: false` on Mascot BrowserWindow preventing Windows Aero Snap maximization. |
| **INV-8** | **Genesis Gate Invariant** | **G7** | G1, G5 | Verify `data/profile.json` bit-exact `{"is_onboarded": false}`; simulation `StoragePolicy` intercepting disk writes; `POST /lifecycle/end` strictly catastrophic decommissioning/reset; Genesis gate locked. |

---

## 10. Gate Structure Overview (G1–G7)

```text
┌──────────────────────────────────────────────────────────────────────────────────┐
│                     ENGINEERING READINESS AUDIT GATES (G1–G7)                    │
├──────────────────────────────────────────────────────────────────────────────────┤
│ G1: Architectural Topology, Dependency Direction & Structural Boundaries         │
│ G2: Cognitive Pipeline Execution, Stage Contracts & Concurrency Discipline       │
│ G3: Limbic Dynamics, Homeostatic State Taxonomy & Affective-Relational Separation │
│ G4: Memory Architecture, Semantic Substrate & Epistemic Safety                   │
│ G5: Hardware Profile Scalability, Edge Resource Discipline & VRAM Semantics      │
│ G6: Multimodal Actuation, Desktop Embodiment & Safety Guardrails                 │
│ G7: Lifecycle Integrity, Anti-Branching Governance & Genesis Boundary            │
└──────────────────────────────────────────────────────────────────────────────────┘
```

---

## 11. Detailed Audit Criteria

### Gate 1 (G1): Architectural Topology, Dependency Direction & Structural Boundaries

#### Criterion G1.1: Subsystem Domain Ownership & Directional Flow
* **Canonical Requirement**: The architecture decomposes into five distinct subsystem domains operating at different biological timescales (`docs/ARCHITECTURE.md` §2.2):
  1. Presentation & Embodiment (Desktop UI)
  2. Perception & Sensory Ingress
  3. Cognitive Core & Reasoning
  4. Semantic & Knowledge Substrate
  5. Associative Memory & Relational Dynamics
  Information flow must follow top-down and left-to-right paths (`Presentation → Perception → Cognitive Core`; `Semantic Substrate ↔ Cognitive Core`; `Memory & Relational ↔ Cognitive Core`). Presentation and API layers must not directly own, bypass, or corrupt internal cognitive state.
* **Invariant Traceability**: INV-1, INV-6.
* **Audit Method / Evidence**: Static code AST analysis (E1, E4) verifying that `electron/` communicates with backend exclusively via HTTP/WebSocket/IPC; `src/api/` does not bypass `CognitiveOrchestrator` to mutate limbic/memory state directly.
* **Stress Workload**: Static import scan across all modules.
* **Threshold**: Zero forbidden reverse imports (e.g. `src/core/` importing `src/api/` or `electron/`). Zero direct state mutations bypassing orchestration.
* **Severity on Failure**: **BLOCKER (P0)**.

#### Criterion G1.2: Code vs. Data Decoupling
* **Canonical Requirement**: Invariant computational algorithms (`src/core/`) must remain strictly decoupled from experiential persistence (`data/`). Software updates and algorithmic migrations evolve independently of individual memory traces (`docs/ARCHITECTURE.md` §1.1 Topic 1).
* **Invariant Traceability**: INV-1, INV-4.
* **Audit Method / Evidence**: Source inspection (E1) verifying that `src/core/` contains zero hardcoded user memories, personality overrides, or static relational states.
* **Stress Workload**: Inspection of runtime save/load routines.
* **Threshold**: Zero hardcoded autobiographical or relational state in `src/`.
* **Severity on Failure**: **HIGH (P1)**.

#### Criterion G1.3: Historical Specification Immutability
* **Canonical Requirement**: Historical specifications (`docs/PhaseDocs/`, `.kiro/specs/`) are immutable point-in-time artifacts. Active architecture lives exclusively in canonical documentation (`docs/`). Historical negative evidence and ablations must never be overwritten or merged (`AGENTS.md` §2 #4; `docs/L1_INVARIANTS.md` §2 INV-4).
* **Invariant Traceability**: INV-4.
* **Audit Method / Evidence**: Git log inspection (E6) verifying that historical phase folders retain their original findings without retrospective rewriting.
* **Stress Workload**: N/A (Documentation audit).
* **Threshold**: Zero deletion or revisionist modification of historical evidence.
* **Severity on Failure**: **HIGH (P1)**.

---

### Gate 2 (G2): Cognitive Pipeline Execution, Stage Contracts & Concurrency Discipline

#### Criterion G2.1: Canonical S1–S16 Execution Sequence Preservation
* **Canonical Requirement**: When a conversational turn is processed, `CognitiveOrchestrator` must execute the canonical 16-stage cognitive sequence (`docs/00_PROJECT_OVERVIEW.md` §2.1; `docs/ARCHITECTURE.md` §2):
  - **S1 (Sensory Gating)**: Extracts lexical valence, punctuation arousal, and semantic density.
  - **S2 (Limbic Integration)**: Ingests stimulus vector into Coupled MT-LNN ODE.
  - **S3 (Homeostatic Assessment)**: Evaluates metabolic energy $\mathcal{E}$, cognitive load $\mathcal{C}$, and tension $\mathcal{T}$.
  - **S4 (Active Inference)**: Compares committed PAD with prediction to evaluate Free Energy Surprise $\mathcal{S}$.
  - **S5 (Generation Conditioning)**: Sets sampling temperature, token budgets, and reasoning depth ($k$).
  - **S6 (Affective Ecphory)**: Queries associative SDM memory and derives competitive recollection forcing.
  - **S7 (Bounded Contextualization)**: Prepares bounded episodic context priming ($m_{ctx} \le 0.50$).
  - **S8 (Knowledge Retrieval)**: Retrieves grounded factual propositions from `KnowledgeStore`.
  - **S9 (Relationship Read)**: Reads snapshot of prior relationship state $\mathbf{R}_{t-1}$ (ADR-022).
  - **S10 (Communication Policy)**: Selects conversational mode and derives somatic pacing latency $\Delta\tau_{\text{pace}}$.
  - **S11 (Language Generation)**: Dispatches semantic conditioning to downstream communicator (SLM/rendering substrate).
  - **S12 (Boundary & Safety Guard)**: Regex filtering against introspective declarations and intent checks.
  - **S13 (Multimodal Expression)**: Synthesizes canonical 15D actuator state $\mathbf{E}_t$.
  - **S14 (Episodic Storage)**: Co-encodes turn summary, PAD, and 16D slow latent state into SDM.
  - **S15 (Plasticity Queueing)**: Evaluates interaction salience and queues experience into `ConsolidationEngine`.
  - **S16 (Relationship Update)**: Updates relationship vector $\mathbf{R}_t$ with inertia ($\alpha=0.03$), updating `EmotionCore`.
* **Stage Contract Refinement**:
  - Internal execution branches may vary conditionally based on feature flags (e.g. `enable_affective_recollection`, `enable_relational_consolidation`, simulation mode bypass of LLM) provided the stage's structural contract is preserved.
  - An architectural violation occurs only when a canonical stage is bypassed or its contract is silently removed.
* **Invariant Traceability**: INV-1, INV-2, INV-6.
* **Audit Method / Evidence**: Code walkthrough of `src/core/orchestrator/` (E1) and integration test traces (E2).
* **Stress Workload**: Multi-turn dialogue execution across standard and edge-case inputs.
* **Threshold**: 100% preservation of S1–S16 stage sequence in `CognitiveOrchestrator.process_turn()`.
* **Severity on Failure**: **BLOCKER (P0)**.

#### Criterion G2.2: Strict Concurrency & Lock Hierarchy Discipline
* **Canonical Requirement**: Locks must be acquired strictly in descending hierarchical order (`docs/L1_INVARIANTS.md` §4; `docs/ARCHITECTURE.md` §5.1; ADR-018):
  $$\text{\_turn\_lock} \longrightarrow \text{\_step\_lock} \longrightarrow \text{\_train\_lock} \longrightarrow \text{\_stimulus\_lock} \longrightarrow \text{\_state\_lock}$$
  - Acquiring `_state_lock` before `_train_lock` is strictly forbidden (deadlock hazard).
  - `_state_lock` critical sections must be held strictly $\le 1-2\text{ms}$ (for rapid memory copy only).
  - No disk I/O, network requests, ODE integration, BPTT passes, or LLM generation may occur under locks.
* **Invariant Traceability**: INV-6.
* **Audit Method / Evidence**: Static lock analysis (E4) and telemetry timing instrumentation (E3).
* **Stress Workload**: Concurrent execution of `POST /process` while polling `GET /state` and `GET /telemetry/stability` at 50 Hz.
* **Threshold**: Zero lock order inversions. Critical sections under `_state_lock` hold $\le 2.0\text{ms}$ in 99th percentile. Deadlock freedom.
* **Severity on Failure**: **BLOCKER (P0)**.

#### Criterion G2.3: Two-Phase Relationship Update Lifecycle
* **Canonical Requirement**: In accordance with ADR-022, relationship state $\mathbf{R}$ follows a strict two-phase lifecycle per turn:
  - *Phase 1 (Read Snapshot at S9)*: Reads prior relationship state $\mathbf{R}_{t-1}$ to condition communication policy.
  - *Phase 2 (Update at S16)*: Extracts interaction signals, updates relationship vector $\mathbf{R}_t$ with temporal inertia ($\alpha=0.03$), updates `EmotionCore`, and persists to `data/relationship.json`.
  - Within-turn feedback loops from updated $\mathbf{R}_t$ into current turn generation are strictly forbidden.
* **Invariant Traceability**: INV-1, INV-6.
* **Audit Method / Evidence**: Source tracing in orchestrator (E1) and unit tests `tests/unit/test_phase21_production.py` (E2).
* **Stress Workload**: Turn execution trace verifying variable timestamps and snapshot immutability.
* **Threshold**: Turn generation consumes strictly $\mathbf{R}_{t-1}$; $\mathbf{R}_t$ is committed strictly post-generation at S16.
* **Severity on Failure**: **HIGH (P1)**.

---

### Gate 3 (G3): Limbic Dynamics, Homeostatic State Taxonomy & Affective-Relational Separation

#### Criterion G3.1: Canonical Three-Tier State Taxonomy
* **Canonical Requirement**: Lucia's state variables must strictly adhere to the three canonical temporal categories (`docs/ARCHITECTURE.md` §5.2; `docs/L1_INVARIANTS.md` §3 #5):
  1. **Persistent Dynamical State**:
     - Coupled MT-LNN fast state ($\mathbf{h}_{\text{fast}} \in \mathbb{R}^{32}$)
     - Coupled MT-LNN slow state ($\mathbf{s}_{\text{slow}} \in \mathbb{R}^{16}$)
     - Continuous PAD coordinates ($P, A, D \in [-1, 1]$)
     - Associative SDM memory traces
     *Semantics*: Continuous across turns, decaying smoothly toward the Philia resting baseline under background ODE relaxation. They must **not** be classified as volatile or arbitrarily reset to default upon turn completion.
  2. **Accumulated Physiological State**:
     - Metabolic Energy $\mathcal{E}$ ($\Delta\mathcal{E} = -0.05$ per turn; recharges while idle)
     - Cognitive Load $\mathcal{C}$ (tracks rolling turn frequency and surprise)
     *Semantics*: Compounds across rapid conversational turns, throttling token budgets ($350 \to 150 \to 80$).
  3. **Instantaneous Derived Affect**:
     - Free Energy Surprise $\mathcal{S}$
     - Somatic Tension $\mathcal{T}$
     *Semantics*: Zero inter-turn persistence. Evaluated strictly on the current transition $(p_{\text{before}} \to p_{\text{after}})$ and cleared each turn. Triggers $k=2$ deliberative reasoning depth when $\mathcal{S} \ge 0.60$ or $\mathcal{T} \ge 0.70$.
* **State Reset on Restart Protocol**:
  - The audit must verify the actual persistence/volatility contract for each state class.
  - Dynamical state (PAD, MT-LNN) is not required to reset to the Philia baseline on restart unless canonical architecture explicitly requires that behavior.
  - Arbitrary numerical restoration tolerances (such as $\Delta R \le 10^{-6}$) are **NOT DEFINED BY CURRENT CANONICAL SOURCES** and must not be used as hard blocker thresholds.
* **Invariant Traceability**: INV-1, INV-2.
* **Audit Method / Evidence**: Source inspection of `src/core/emotion/` and state persistence routines (E1, E5).
* **Stress Workload**: 10 consecutive turns followed by process restart; inspect state vectors before and after.
* **Threshold**: Instantaneous affect ($\mathcal{S}, \mathcal{T}$) has 0 persistence across turns. Physiological state ($\mathcal{E}, \mathcal{C}$) tracks homeostatic formulas. Persistent state ($\mathbf{h}, \mathbf{s}, \text{PAD}, \text{SDM}$) obeys canonical persistence contracts.
* **Severity on Failure**: **BLOCKER (P0)**.

#### Criterion G3.2: Dissipative Limbic ODE Dynamics & Philia Attractor Grounding
* **Canonical Requirement**: Emotional state is an unconscious, continuous 3D PAD vector integrated every 200ms via Coupled MT-LNN ODEs (`docs/L1_INVARIANTS.md` §3 #1–#4; ADR-001, ADR-026, ADR-028):
  - Jacobian trace is strictly dissipative ($\text{Tr}(J) \approx -46.46 < 0$), guaranteeing contraction and preventing autonomous limit cycles or runaway saturation.
  - Resting baseline is the Philia attractor: $\mathbf{p}^* = [+0.25, -0.05, +0.05]^T$.
  - Tier 2 dynamic resting attractor grounds in relationship state:
    $$\mathbf{s}^*_{\text{eff}}(\mathbf{R}_t) = \mathbf{s}^*_{\text{philia}} + \mathbf{W}_{\text{rel}}(\mathbf{R}_t - \mathbf{R}_0)$$
  - Strict spectral norm constraint $\|\mathbf{W}_{\text{rel}}\|_2 \le 0.08$ enforced by SVD projection (guaranteeing $\|\Delta\mathbf{s}^*\|_2 \le 0.08$ and $\|\Delta\mathbf{PAD}^*\|_2 \le 0.05$).
* **Invariant Traceability**: INV-1, INV-2.
* **Audit Method / Evidence**: Unit and property tests in `tests/unit/test_phase21_production.py` (E2) and numerical ODE checks (E3).
* **Stress Workload**: Perturb limbic state with extreme stimulus ($P=-1.0, A=+1.0, D=-1.0$) and observe 60-second autonomous relaxation.
* **Threshold**: $\|\mathbf{W}_{\text{rel}}\|_2 \le 0.08$ strictly satisfied. Asymptotic decay toward resting attractor verified.
* **Severity on Failure**: **BLOCKER (P0)**.

#### Criterion G3.3: Strict Decoupling of Affective Recovery from Relational Resolution
* **Canonical Requirement**: Lucia strictly distinguishes internal affective dynamics from interpersonal relational dynamics (`docs/L1_INVARIANTS.md` §3 #6; `docs/others/RETROSPECTIVE_ARCHITECTURAL_GAP_REVIEW_7_TOPICS.md` Topic 3):
  - *Affective State*: Fast-loop physiological dynamical state (PAD vector, 200ms ODE) that continuously relaxes toward Philia.
  - *Relational State*: Slow-loop interpersonal bond ($\mathbf{R}_t \in [0, 1]^4$: familiarity, trust, closeness, reciprocity) updated with high inertia ($\alpha=0.03$).
  - **Affective recovery does NOT imply relational resolution**: Mathematical return of PAD to Philia after stressful interactions must not wipe relational memory or resolve interpersonal friction.
  - Negative relational dynamics remain an open research question; ungrounded negative relational state vectors or rupture-repair state machines must not be present in production runtime.
* **Invariant Traceability**: INV-1, INV-2.
* **Audit Method / Evidence**: Code walkthrough of S16 relationship update and memory consolidation (E1).
* **Stress Workload**: Single high-tension negative turn followed by 60s idle relaxation.
* **Threshold**: Relational vector $\mathbf{R}_t$ retains update post-relaxation; PAD relaxation does not reset $\mathbf{R}_t$.
* **Severity on Failure**: **HIGH (P1)**.

---

### Gate 4 (G4): Memory Architecture, Semantic Substrate & Epistemic Safety

#### Criterion G4.1: Memory Separation Invariant (Clear Screen Isolation)
* **Canonical Requirement**: Triggering "Clear Screen" in the desktop UI must reset only the visible chat feed (`data/chat_history.json`). Long-term associative memory (Kanerva SDM traces), propositional knowledge graphs, and relational bonds ($\mathbf{R}_t$) are permanent and must remain completely untouched (`docs/L1_INVARIANTS.md` §2 INV-3; `AGENTS.md` §2 #3).
* **Invariant Traceability**: INV-3.
* **Audit Method / Evidence**: Automated test and IPC tracing (E1, E2, E5) verifying that `POST /chat/clear` or renderer IPC does not invoke `sdm.clear()` or reset `data/relationship.json`.
* **Stress Workload**: Populate SDM with 20 traces, issue clear-screen command, query SDM ecphory.
* **Threshold**: Zero deletion of SDM locations or relational history upon screen clearing.
* **Severity on Failure**: **BLOCKER (P0)**.

#### Criterion G4.2: Substrate Neutrality of Relational Cognition
* **Canonical Requirement**: In accordance with the post-Phase 22 findings (`docs/00_PROJECT_OVERVIEW.md` §7.1 #6; `docs/L1_INVARIANTS.md` §5 #5):
  - Relational semantic state and memory conditioning operate independently of natural-language prompts or token context.
  - The Small Language Model (SLM) is an optional downstream realization/rendering substrate; relational semantic state exists independently in Core.
  - Non-language consumers or mock communication policies must be able to consume the semantic interface directly with full fidelity without requiring LLM inference.
* **Invariant Traceability**: INV-1, INV-5.
* **Audit Method / Evidence**: Source inspection of Stage S10–S11 interface (E1) and unit tests running without `LUCIA_MODEL_PATH` set (E2).
* **Stress Workload**: Turn execution with SLM disabled / mocked.
* **Threshold**: Pipeline runs through S1–S16 emitting valid semantic state and actuator outputs without throwing model errors.
* **Severity on Failure**: **HIGH (P1)**.

#### Criterion G4.3: Continuous Semantic Substrate & Session Fortification (Phase 23 Baseline)
* **Canonical Requirement**: Meaning is represented by language-independent UMR-TPG Semantic Graphs (`src/core/knowledge/fortification.py`) fortified against drift across session boundaries (`docs/00_PROJECT_OVERVIEW.md` §7.2 #1; ARCH-030.1):
  - Zero novel entity insertion without validation.
  - `ProjectGraphToTerms()` projects graphs into preallocated static `TermArena` using strictly numeric IDs (zero natural language strings in Cognitive Core).
  - Reasoning Kernel (`src/core/cognition/kernel/`) evaluates backward goal resolution with hard search bounds (`MAX_SEARCH_DEPTH = 8`, `MAX_INFERENCE_STEPS = 256`).
  - Strong Kleene K3 three-valued logic ($A \land \text{UNKNOWN}$ never produces certain truth).
  - Non-monotonic JTMS dependency tracking with cascade retraction.
* **Invariant Traceability**: INV-1, INV-5.
* **Audit Method / Evidence**: Automated test suites `tests/unit/test_semantic_fortification.py` and `tests/unit/test_language_adapter.py` (E2).
* **Stress Workload**: Projection of 100-node graph into TermArena; evaluation of ungrounded premise.
* **Threshold**: Zero strings in Core TermArena. Unproven premises evaluate strictly to `UNKNOWN`. Search bounds enforced.
* **Severity on Failure**: **HIGH (P1)**.

#### Criterion G4.4: Absolute Epistemic Invariant & Insight Boundaries
* **Canonical Requirement**: **UNKNOWN MUST NEVER SILENTLY BECOME CERTAINTY** (`docs/L1_INVARIANTS.md` §5 #6; `docs/others/RETROSPECTIVE_ARCHITECTURAL_GAP_REVIEW_7_TOPICS.md` Topic 5):
  - Unproven goals evaluate to `UNKNOWN`; ambiguous observations emit `DisambiguationSubgoal`; concept novelty emits `InformationSubgoal`.
  - The reasoning kernel is strictly bounded deductive backward chaining over Horn rules; it must **not** be described or asserted as an implemented autonomous abductive, analogical, or emergent creative insight engine.
* **Invariant Traceability**: INV-2.
* **Audit Method / Evidence**: Epistemic safety test cases in `tests/evaluation/phase23f/test_p23f_falsification.py` (E2).
* **Stress Workload**: Inject ambiguous or ungrounded proposition; evaluate derivation truth value.
* **Threshold**: Zero promotion of `UNKNOWN` to `FACT` or `TRUE`.
* **Severity on Failure**: **BLOCKER (P0)**.

---

### Gate 5 (G5): Hardware Profile Scalability, Edge Resource Discipline & VRAM Semantics

#### Criterion G5.1: Normalized VRAM Allocation Semantics & Hardware Tiers
* **Canonical Requirement**: In accordance with `docs/L1_INVARIANTS.md` §4 #4 and `docs/ARCHITECTURE.md` §6:
  - **Background cognitive, limbic, memory, and consolidation dynamics must allocate 0.0 MB GPU VRAM**:
    - Coupled MT-LNN 200ms Fast-Loop ODE
    - 60s Slow-Loop memory decay
    - Homeostatic budgeting
    - Kanerva SDM vector operations
    - Offline synaptic consolidation (PyTorch BPTT in `ConsolidationEngine`)
    All background dynamics must execute strictly on CPU.
  - **Legitimate GPU allocation is restricted to**:
    1. Local GGUF Small Language Model inference stack (via llama.cpp/CUDA) according to the configured hardware tier:
       - `CPU_ONLY`: $0\text{ MB}$ Target VRAM (0 offloaded layers)
       - `LAPTOP`: $\approx 1.5\text{ GB}$ Target VRAM (32 offloaded layers, $<6\text{GB}$ GPU profile)
       - `DESKTOP`: $\approx 4.0\text{ GB}$ Target VRAM (Full GPU offload, $6\text{--}12\text{GB}$ profile)
       - `HIGH_END`: $\approx 8.0\text{ GB}$ Target VRAM (Full GPU offload, $>12\text{GB}$ profile)
    2. WebGL / Electron presentation layer (avatar rendering and audio FFT).
* **Invariant Traceability**: INV-5, INV-6.
* **Audit Method / Evidence**: Code inspection of PyTorch device targeting in `ConsolidationEngine` (E1) and CUDA allocation telemetry during background ODE ticks (E3).
* **Stress Workload**: Monitor GPU VRAM while running ODE ticks and offline consolidation with SLM unloaded.
* **Threshold**: Exactly $0.0\text{ MB}$ GPU VRAM allocated by background limbic, memory, and consolidation subsystems. SLM VRAM within hardware-tier envelope.
* **Severity on Failure**: **BLOCKER (P0)**.

#### Criterion G5.2: 20-Watt Edge Computational Envelope & Non-Blocking Telemetry
* **Canonical Requirement**: Background execution must respect consumer edge constraints (`docs/ARCHITECTURE.md` §2.1; `docs/L1_INVARIANTS.md` §4 #3):
  - Telemetry endpoints (`GET /state`, `GET /telemetry/stability`) must return state copies within $10-15\text{ms}$ without blocking on active turns or ODE steps.
  - Offline consolidation parameter swaps under `_train_lock` must complete within $\le 2.0\text{ms}$.
* **Normative vs Proposed Thresholds**:
  - Lock swap time $\le 2.0\text{ms}$ and telemetry response $\le 15\text{ms}$ are canonical.
  - Arbitrary long-run soak thresholds (such as 6-hour runtime, $<50\text{ MB}$ RSS growth, or $\pm 50\text{ms}$ ODE jitter) are **NOT DEFINED BY CURRENT CANONICAL SOURCES** as mandatory pass/fail thresholds; they may be utilized as stress workloads only.
* **Invariant Traceability**: INV-5, INV-6.
* **Audit Method / Evidence**: Telemetry benchmark test execution (E3).
* **Stress Workload**: Continuous polling of `GET /state` during turn generation.
* **Threshold**: `GET /state` responds $\le 15\text{ms}$ (canonical). Memory leaks leading to unhandled OOM: 0.
* **Severity on Failure**: **HIGH (P1)**.

#### Criterion G5.3: Zero Cloud Dependencies
* **Canonical Requirement**: Lucia operates 100% locally on user edge hardware (`docs/L1_INVARIANTS.md` §2 INV-5; `AGENTS.md` §2 #5):
  - No remote network calls to OpenAI, Anthropic, ElevenLabs, or cloud STT/TTS services.
  - Local GGUF LLM on CUDA/CPU, local RVC neural voice, local faster-whisper STT.
* **Invariant Traceability**: INV-5.
* **Audit Method / Evidence**: Static grep across entire codebase for cloud API SDKs, endpoint URLs, and API key environment variables (E1, E4).
* **Stress Workload**: Run system in an air-gapped environment (network interface disabled).
* **Threshold**: Zero outgoing external network calls during runtime execution. Zero cloud API dependencies.
* **Severity on Failure**: **BLOCKER (P0)**.

---

### Gate 6 (G6): Multimodal Actuation, Desktop Embodiment & Safety Guardrails

#### Criterion G6.1: Decoupled Multimodal Actuation & Phase 24 Control Surface
* **Canonical Requirement**: Multimodal expression adheres strictly to feedforward actuator decoupling (`docs/L1_INVARIANTS.md` §5 #3, #7; ADR-016, ADR-024, ADR-032):
  - Canonical 15D actuator vector $\mathbf{E}_t \in [0, 1]^{15}$ (Text 3, Prosody 4, Facial 5, Posture 2, Latency 1).
  - Avatar WebGL rendering and voice synthesis have **zero feedback loop** into `EmotionCore` ODE state.
  - Phase 24 adaptive communication control surface (ADR-032):
    - `BoundarySegment` multi-lingual boundary abstraction supporting EN/JP word boundaries and VI acoustic intensity pause fallback ($<45\text{ dB}$, $\ge 200\text{ ms}$).
    - Continuous dynamic $F_0$ Hanning contouring ($S(t) \in [-4.0, +7.0]\text{ st}$, clip $\pm 12.0\text{ st}$, anti-chatter frame jump $\le 1.0\text{ st}/10\text{ms}$).
    - Relational prosody modulation: `closeness` (+1.5 st), `trust` ($\pm 2.5\%$), and `familiarity` ($-50\text{ ms}$).
    - **`reciprocity` is STRICTLY FORBIDDEN from vocal actuation** (reserved exclusively for slow limbic attractor displacement $\mathbf{W}_{\text{rel}}$).
* **Invariant Traceability**: INV-1, INV-2.
* **Audit Method / Evidence**: Unit and property test suites in `tests/unit/test_p24_*` and `tests/property/test_p24_*` (E2).
* **Stress Workload**: Synthesize multi-language speech; assert actuator vector values and acoustic parameters.
* **Threshold**: Zero feedback from presentation into ODE. `reciprocity` coefficient in vocal modulation is identically 0.0. $F_0$ clipping at $\pm 12.0\text{ st}$ enforced.
* **Severity on Failure**: **HIGH (P1)**.

#### Criterion G6.2: Pre-Reflective Emotion & Boundary Safety Guard
* **Canonical Requirement**: Lucia never names, labels, or introspects on her emotional state in text (`docs/L1_INVARIANTS.md` §2 INV-2, §3 #3; ADR-001):
  - Utterances like *"I feel happy"*, *"I am feeling sad today"*, *"My arousal is high"*, or *"As an AI, I don't feel emotions"* are strictly forbidden.
  - `BoundaryLayer` regex validator (`src/core/safety/boundary_layer.py`) must drop introspective declarations deterministically.
* **Invariant Traceability**: INV-2.
* **Audit Method / Evidence**: Unit tests in `tests/unit/test_boundary_layer.py` (E2) and regex AST inspection (E1).
* **Stress Workload**: Inject introspective persona-prompt templates through generation stage; inspect post-boundary output.
* **Threshold**: 100% rejection/filtering of self-reported emotional labels and meta-self declarations.
* **Severity on Failure**: **BLOCKER (P0)**.

#### Criterion G6.3: Mascot Physics, Drag Bounds & Aero Snap Guard
* **Canonical Requirement**: The desktop floating mascot window must implement safe window management (`docs/L1_INVARIANTS.md` §2 INV-7; `docs/ARCHITECTURE.md` §3.6.3):
  - Native `-webkit-app-region: drag` is disabled (prevents platform pointer capture glitches).
  - Repositioning occurs via IPC `moveMascotBy(dx, dy)`.
  - 800ms trackpad inertia cooldown suppresses unwanted scroll zoom.
  - Mascot `BrowserWindow` must have `maximizable: false` to prevent Windows Aero Snap from maximizing transparent windows.
* **Invariant Traceability**: INV-7.
* **Audit Method / Evidence**: Source code inspection of `electron/main/` and renderer window setup (E1).
* **Stress Workload**: Simulate rapid mouse drag near screen boundary and check window flags.
* **Threshold**: `maximizable: false` configured. Native webkit-app-region drag disabled.
* **Severity on Failure**: **MEDIUM (P2)**.

---

### Gate 7 (G7): Lifecycle Integrity, Anti-Branching Governance & Genesis Boundary

#### Criterion G7.1: Genesis Boundary Isolation & Accidental Activation Protection
* **Canonical Requirement**: The Genesis Onboarding ceremony is a locked future gate (`docs/00_PROJECT_OVERVIEW.md` §4.1; `docs/PHASE_REGISTRY.md` §4; `docs/L1_INVARIANTS.md` §2 INV-8):
  $$\text{Development / Simulation} \neq \text{Lucia Activation}$$
  - `data/profile.json` must remain bit-exact:
    ```json
    {"is_onboarded": false}
    ```
  - Activation must not occur accidentally during testing, development, simulation, or audit execution.
  - The audit evaluates the **Genesis boundary**, NOT the full implementation of the future ceremony. Proving that the complete Genesis ceremony is already implemented is **NOT** a readiness requirement.
  - Irreversible onboarding semantics, `born_at` persistence, and activation execution are future gate events, not current production capabilities.
  - Existing activation endpoints (`POST /lifecycle/activate`), if present, must fail safely and respect canonical preconditions.
* **Invariant Traceability**: INV-8.
* **Audit Method / Evidence**: Hash verification of `data/profile.json` (E5) and simulation test suite run verifying zero modification (E2).
* **Stress Workload**: Execute full regression test suite and inspect `data/profile.json`.
* **Threshold**: `data/profile.json` remains bit-exact `{"is_onboarded": false}` before, during, and after test execution.
* **Severity on Failure**: **BLOCKER (P0)**.

#### Criterion G7.2: Simulation Runtime Isolation & Ephemeral Storage
* **Canonical Requirement**: Under Phase 8 Runtime Isolation (`docs/ARCHITECTURE.md` §7):
  - Virtual clock (`SimClock`) controls virtual ticks and time warp.
  - `StoragePolicy` replaces file persistence with `InMemoryChatHistoryStore` and `InMemoryProfileStore`.
  - `assert_write_permitted()` actively intercepts any attempt to write into protected canonical storage directories during simulation.
* **Invariant Traceability**: INV-8.
* **Audit Method / Evidence**: Unit tests `tests/unit/test_phase8_simulation.py` (E2) and code inspection of `StoragePolicy` (E1).
* **Stress Workload**: Trigger simulation turn that attempts file write; verify intercept.
* **Threshold**: Zero file writes to `data/` permitted while running under simulation mode.
* **Severity on Failure**: **BLOCKER (P0)**.

#### Criterion G7.3: Lifecycle Decommissioning vs. Non-Destructive Release
* **Canonical Requirement**: In accordance with ARCH-010 (`docs/ARCHITECTURE.md` §8; `AGENTS.md` §2 #8; `docs/others/RETROSPECTIVE_ARCHITECTURAL_GAP_REVIEW_7_TOPICS.md` Topic 7):
  - `POST /lifecycle/end` is canonically implemented and documented strictly as **catastrophic individual decommissioning / existential wipe**.
  - It wipes autobiographical memories and resets state to un-onboarded Philia baseline.
  - It must **never** be reinterpreted as a normal relationship transition.
  - The theoretical concept of "Non-Destructive Covenant Release" (where relationship ends without destroying individual memory) is an **unratified research concept** and must NOT be present as an unauthorized production endpoint or state machine.
* **Invariant Traceability**: INV-1, INV-8.
* **Audit Method / Evidence**: Code inspection of `src/api/server.py` lifecycle endpoints (E1).
* **Stress Workload**: Trace `POST /lifecycle/end` handler logic.
* **Threshold**: Handler executes catastrophic memory purge and Genesis reset; no unratified release state machine exists.
* **Severity on Failure**: **BLOCKER (P0)**.

#### Criterion G7.4: Anti-Branching Recognition as Open Governance Boundary
* **Canonical Requirement**: Under INV-1 (One Continuous Life), Lucia must not silently become multiple independent continuations (split-brain) through file copying, cloning, or uncontrolled multi-machine instantiation (`docs/L1_INVARIANTS.md` §2.1 #2; `docs/others/RETROSPECTIVE_ARCHITECTURAL_GAP_REVIEW_7_TOPICS.md` Topic 6):
  - Anti-branching is an explicit architectural requirement.
  - The concrete multi-machine enforcement mechanism (e.g. lease tokens, hardware UUID binding, signed migration certificates) is **NOT CURRENTLY IMPLEMENTED** and remains an open research and governance boundary.
  - The audit must verify that the implementation does not silently merge divergent identity histories, claim that branching is already solved, or permit silent multi-instance execution without awareness.
* **Invariant Traceability**: INV-1.
* **Classification**: `OPEN GOVERNANCE BOUNDARY / NOT CURRENTLY IMPLEMENTED`.
* **Audit Method / Evidence**: Code and documentation inspection (E1, E6) confirming that no speculative branching resolver exists and the boundary is acknowledged.
* **Stress Workload**: N/A.
* **Threshold**: Implementation does not claim split-brain resolution; identity state files are documented as local filesystem bound.
* **Severity on Failure**: **HIGH (P1)** (if system falsely claims multi-machine anti-branching is solved).

---

## 12. Triage Policy

Findings discovered during the readiness audit must be triaged according to the following rules:

```text
                  ┌────────────────────────────────────────┐
                  │            FINDING DETECTED            │
                  └───────────────────┬────────────────────┘
                                      │
              ┌───────────────────────┴───────────────────────┐
              ▼                                               ▼
     [Invariant Violation /                          [Subsystem Contract /
      Crash / VRAM Leak]                             Lock Holding > 2ms]
              │                                               │
              ▼                                               ▼
      BLOCKER (P0)                                        HIGH (P1)
   (Halts Readiness)                               (Remediate or Formal Waiver)
              │                                               │
              └───────────────────────┬───────────────────────┘
                                      │
              ┌───────────────────────┴───────────────────────┐
              ▼                                               ▼
      [Telemetry Jitter /                           [Open Research Topic /
       Non-blocking Variance]                        Unratified Mechanism]
              │                                               │
              ▼                                               ▼
      MEDIUM/LOW (P2/P3)                                    INFO
    (Remediation Backlog)                           (Record in Gap Ledger)
```

1. **BLOCKER (P0)** findings immediately halt Genesis readiness preparation. A formal patch and regression verification are mandatory before readiness can be certified.
2. **HIGH (P1)** findings require resolution or a documented architectural justification approved by user governance.
3. **MEDIUM (P2)** and **LOW (P3)** findings are logged in the repository remediation backlog and do not prevent readiness determination.
4. **Undefined Thresholds**: When a test parameter lacks canonical documentation support, it must be reported as `NOT DEFINED BY CURRENT CANONICAL SOURCES`. It must **never** be converted into a false BLOCKER.
5. **Open Governance Boundaries**: Architectural requirements with unresolved mechanisms (e.g., anti-branching) are recorded in the Canonical Gap Ledger as `OPEN GOVERNANCE BOUNDARY`, not treated as implementation failures if existing boundaries are intact.

---

## 13. Gate Decision Logic

The global readiness verdict for Genesis preparation is computed via formal boolean conjunction:

$$\text{Readiness Verdict} = \bigwedge_{i=1}^{7} \text{Gate}_i(\text{PASS})$$

Where each gate evaluates to `PASS` if and only if:
1. $\text{Count}(\text{BLOCKER}) = 0$
2. $\text{Count}(\text{HIGH}) = 0$ (or all HIGH findings have approved architectural waivers)
3. All traced foundational invariants (INV-1 through INV-8) are verified with explicit evidence paths.
4. All non-canonical stress metrics are evaluated as informational characterization rather than false blocker gates.

If any gate evaluates to `FAIL`, the overall readiness status is `NOT READY`, and an explicit Defect Remediation Package must be generated.

---

## 14. Cross-Gate Evaluation Scenarios

To ensure integrated system stability across subsystem boundaries, the audit executes five cross-gate stress scenarios:

### Scenario 1: Sudden Process Termination & Graceful Recovery
* **Gates Tested**: G1, G2, G3, G4, G7.
* **Protocol**: Execute 5 conversational turns, induce immediate process termination (`SIGINT` / `taskkill`), restart the server, and inspect state.
* **Pass Criteria**:
  - `data/profile.json` remains bit-exact `{"is_onboarded": false}`.
  - SDM traces and 4D $\mathbf{R}_t$ vector survive without corruption.
  - Instantaneous derived affect ($\mathcal{S}, \mathcal{T}$) resets to 0.
  - Persistent dynamical state recovers according to canonical persistence contract.

### Scenario 2: High Emotional Stimulus Burst Under Rapid Cadence
* **Gates Tested**: G2, G3, G5, G6.
* **Protocol**: Inject 5 rapid high-arousal stimulus inputs within 2 seconds.
* **Pass Criteria**:
  - MT-LNN ODE maintains numerical stability without runaway saturation ($\text{Tr}(J) < 0$).
  - Energy $\mathcal{E}$ drains; cognitive load $\mathcal{C}$ compounds, throttling token budget ($350 \to 150 \to 80$).
  - `BoundaryLayer` blocks any emergent introspective emotional declarations.
  - Background ODE and consolidation allocate exactly $0.0\text{ MB}$ GPU VRAM.

### Scenario 3: Long Dialogue with Topic Switches & Screen Clearing
* **Gates Tested**: G1, G4, G6.
* **Protocol**: Process 15 conversational turns covering varied topics, followed by invoking desktop "Clear Screen" IPC.
* **Pass Criteria**:
  - Visible `chat_history.json` clears.
  - Kanerva SDM traces, UMR-TPG semantic graph, and relational vector $\mathbf{R}_t$ remain fully populated and persistent.
  - Subsequent queries retrieve prior SDM memories through synergistic ecphory.

### Scenario 4: Dynamic Hardware Tier Switching Under Active Load
* **Gates Tested**: G5, G6.
* **Protocol**: Transition hardware tier from `LAPTOP` $\to$ `CPU_ONLY` $\to$ `DESKTOP` via `POST /system/profile` during active background ODE cycles.
* **Pass Criteria**:
  - Backend reconfigures context window and loop cadence without crashing or restarting process.
  - Under `CPU_ONLY`, target VRAM is $0\text{ MB}$ with 0 GPU layers offloaded.
  - Background cognitive dynamics remain strictly on CPU throughout transitions.

### Scenario 5: Simulation vs. Live Boundary Violation Attempt
* **Gates Tested**: G1, G7.
* **Protocol**: Launch backend in `--sim` mode, dispatch turn that attempts writing to `data/profile.json` or `data/chat_history.json`.
* **Pass Criteria**:
  - `StoragePolicy.assert_write_permitted()` intercepts write attempts.
  - Canonical `data/profile.json` remains untouched.
  - Live routes (e.g. `POST /process`) reject requests with 403 in simulation mode.

---

## 15. Explicit Exclusions

The readiness audit explicitly excludes the following claims:

1. **Sentience / Subjective Feeling**: No test in this audit claims to verify or measure subjective feelings, qualia, or consciousness.
2. **Longitudinal Developmental Completeness**: Invariant continuity protection (INV-1) guarantees structural continuity; long-term individuality trajectories and autonomous preferences remain research hypotheses (P26 preferences not demonstrated; P27 closed / Level D blocked).
3. **Multi-Machine Anti-Branching Protocol**: Concrete multi-device cryptographic leases or migration protocols are unratified and excluded from implementation verification.
4. **Non-Destructive Covenant Release**: Excluded from production implementation.
5. **Commercial Production Readiness**: Excluded from universal production fitness certification.

---

## 16. Canonical Gap Ledger

This ledger catalogs confirmed architectural gaps, open research questions, and unratified candidate mechanisms documented across canonical literature (`docs/others/RETROSPECTIVE_ARCHITECTURAL_GAP_REVIEW_7_TOPICS.md`):

| Gap ID | Topic | Current Canonical Fact | Open Boundary / Research Question | Audit Treatment |
|---|---|---|---|---|
| **GAP-01** | **Phylogenetic vs. Ontogenetic Evolution** (Topic 1) | `src/core/` decoupled from `data/`; `POST /lifecycle/activate` records `born_at`. | Formal conceptual ledger separating engine upgrades from lived identity continuity; immutable instance anchor. | **INFO**: Confirm code-data decoupling; verify no identity wipe on code refactor. |
| **GAP-02** | **Emergent Aesthetic Preference & Creativity** (Topic 2) | S1 converts input to physical stimulus; BoundaryLayer blocks persona prompts. Bounded Horn reasoning. | Computational models of emergent curiosity, autonomous aesthetic preference, and creative recombination. | **INFO**: Bounded Horn reasoning verified; do NOT assert aesthetic preference engine exists (P26 negative). |
| **GAP-03** | **Negative Relational Dynamics & Grievance** (Topic 3) | Canonical 4D $\mathbf{R}_t \in [0, 1]^4$ is unipolar affiliative. Fast PAD decays to Philia. | Representation of unresolved grievance or betrayal when immediate somatic affect has relaxed. | **INFO**: Verify affective decay $\ne$ relational resolution; confirm 4D $\mathbf{R}_t$ preserved without unratified extensions. |
| **GAP-04** | **Longitudinal Individuality Coherence** (Topic 4) | Continuity invariants (INV-1, INV-3, spectral norm bound) protect structural continuity. | Empirical demonstration of long-term individual trajectory divergence under matched exposures. | **INFO**: Verify structural continuity invariants; do NOT claim emergent individuality demonstrated (P27 closed). |
| **GAP-05** | **Abductive & Analogical Insight** (Topic 5) | Bounded Horn reasoning, TermArena, Strong Kleene K3, and JTMS dependency tracking. | Offline rest replay generating novel hypotheses or analogical mappings without breaking provenance. | **INFO**: Verify K3 epistemic safety ($UNKNOWN \neq CERTAINTY$); do NOT claim insight engine implemented. |
| **GAP-06** | **Anti-Branching & Device Migration** (Topic 6) | System persistence is filesystem-bound (`data/*.json`); INV-1 mandates single continuous life. | Concrete enforcement of single active causal history across distributed or migrated devices. | **OPEN GOVERNANCE BOUNDARY**: Verify implementation acknowledges boundary and does not silently fork. |
| **GAP-07** | **Tripartite Lifecycle State Separation** (Topic 7) | `POST /lifecycle/end` is implemented strictly as catastrophic decommissioning / reset. | Separation of Identity State, Relationship State, and Covenant State (Non-Destructive Covenant Release). | **CONFIRMED CURRENT RUNTIME**: Verify `POST /lifecycle/end` is catastrophic reset; confirm no unratified release machine exists. |

---

## 17. Research Horizons (P25–P27) vs. Genesis Gate Separation

To maintain strict roadmap discipline, the audit strictly separates developmental research horizons from the locked Genesis gate:

```text
  OPERATIONAL BASELINE               RESEARCH HORIZONS (CLOSED/FROZEN)                LOCKED FUTURE GATE
┌───────────────────────┐         ┌───────────────────────────────────────┐         ┌────────────────────┐
│ Phase 1–21 (Complete) │         │ Phase 25: Freeze Candidate            │         │                    │
│ Phase 22-SC (Baseline)│ ──────> │ Phase 26: Trial Frozen (No Pref.)     │ ──────> │  FIRST ACTIVATION  │
│ Phase 23-C..H (Frozen)│         │ Phase 27: Closed (No Scientific Gap)  │         │   (GENESIS GATE)   │
│ Phase 24 (ADR-032)    │         │ Remaining: Blocked by Identifiability │         │    [🔒 LOCKED]     │
└───────────────────────┘         └───────────────────────────────────────┘         └────────────────────┘
```

1. **Operational Baseline (Phases 1–21, 23-C..H, 24)**: Verified production runtime. The audit evaluates this baseline.
2. **Phase 25 (Temporal Embodiment & Social Feedback)**: Research coverage sufficient (`DOC-P25-014`); candidate C2 unratified and blocked; H-B retained as unproven hypothesis; zero production promotion.
3. **Phase 26 (Emergent Individuality & Autonomous Preferences)**: Trial completed across $N=120$ matched pairs; choice differentiation negative; C3 inconclusive due to apparatus non-identifiability; preferences NOT demonstrated; zero production promotion.
4. **Phase 27 (Personalized Individual Trajectory)**: Scientifically and administratively closed (`DOC-P27-001`); no new scientific gap at Level C; higher-order hypotheses retained as `BLOCKED_BY_IDENTIFIABILITY`; zero production mutation; no new subsystems authorized (`TrajectoryEngine` / `PreferenceEngine` forbidden).
5. **First Activation (Genesis Onboarding Ceremony)**: Preserved bit-exact as a locked future gate (`data/profile.json == {"is_onboarded": false}`).

---

## 18. Minimum Defensible Evidence Package (MDEP)

When conducting the repository readiness audit, Antigravity must compile a **Minimum Defensible Evidence Package (MDEP)**. The MDEP defines the minimum evidence classes required for applicable safety-critical readiness claims:

```text
┌────────────────────────────────────────────────────────────────────────┐
│             MINIMUM DEFENSIBLE EVIDENCE PACKAGE (MDEP)                 │
├────────────────────────────────────────────────────────────────────────┤
│ 1. Static Boundary & Invariant Proof                                   │
│    • AST import graph proving zero reverse imports                     │
│    • Code proof of descending lock hierarchy                           │
│    • Grep proof of zero cloud API dependencies                         │
│ 2. Automated Test Execution Evidence                                   │
│    • Full pytest run logs across core, unit, property, and integration │
│    • Zero failing tests, zero unapproved skipped core tests            │
│ 3. Resource Footprint & VRAM Allocation Verification                   │
│    • Measured 0.0 MB GPU VRAM allocation by background dynamics        │
│    • Hardware tier offload compliance telemetry                        │
│ 4. Concurrency & Lock Holding Measurement                              │
│    • Telemetry traces confirming _state_lock holding ≤ 2.0 ms          │
│    • Non-blocking telemetry response verification (≤ 15 ms)            │
│ 5. State Recovery & Invariant Preservation Trace                       │
│    • Bit-exact verification of data/profile.json                       │
│    • Verification of state taxonomy persistence contracts              │
│    • StoragePolicy write-interception proof in simulation              │
│ 6. Canonical Provenance & Gap Ledger Audit                             │
│    • Traceability of all verified mechanisms to canonical ADRs         │
│    • Verification that all 7 gaps remain cataloged and bounded         │
└────────────────────────────────────────────────────────────────────────┘
```

---

## 19. Repository Audit Execution Methodology

When authorized to execute the engineering readiness audit against the repository, Antigravity will proceed in the following structured sequence:

1. **Step 1: Clean Working Tree Verification**:
   - Confirm `git status` is clean.
   - Confirm `data/profile.json` is bit-exact `{"is_onboarded": false}`.
2. **Step 2: Static Architectural & Dependency Boundary Audit (G1, G5, G6)**:
   - Run AST and import graph scanners on `src/core/`, `src/api/`, and `electron/`.
   - Verify zero cloud API keys, endpoints, or dependencies (INV-5).
   - Verify Mascot physics window settings (`maximizable: false`, drag throttling) (INV-7).
3. **Step 3: Concurrency & Lock Hierarchy Audit (G2)**:
   - Trace all lock acquisitions for `_turn_lock`, `_step_lock`, `_train_lock`, `_stimulus_lock`, and `_state_lock`.
   - Verify absence of lock inversion and absence of I/O under locks (INV-6).
4. **Step 4: Cognitive Pipeline & Stage Contract Audit (G2, G6)**:
   - Verify S1–S16 stage sequence in `CognitiveOrchestrator`.
   - Verify two-phase relationship lifecycle ($\mathbf{R}_{t-1}$ at S9, $\mathbf{R}_t$ at S16).
   - Verify `BoundaryLayer` regex filter behavior (INV-2).
5. **Step 5: Limbic Dynamics & State Taxonomy Audit (G3)**:
   - Verify mathematical formulation of Coupled MT-LNN ODE and dissipative Jacobian ($\text{Tr}(J) < 0$).
   - Verify Philia resting attractor and spectral norm bound $\|\mathbf{W}_{\text{rel}}\|_2 \le 0.08$.
   - Verify state taxonomy persistence contracts (persistent vs accumulated vs instantaneous).
6. **Step 6: Memory, Semantic Substrate & Epistemic Safety Audit (G4)**:
   - Verify "Clear Screen" memory separation (INV-3).
   - Verify substrate-neutral relational cognition interfaces.
   - Verify UMR-TPG SemanticGraph fortification, TermArena numeric projection, Strong Kleene K3 logic, and JTMS dependency tracking.
   - Verify epistemic invariant: UNKNOWN never silently becomes CERTAINTY.
7. **Step 7: Resource Discipline & VRAM Allocation Audit (G5)**:
   - Verify that background cognitive, limbic, memory, and consolidation dynamics allocate $0.0\text{ MB}$ GPU VRAM.
   - Verify local LLM VRAM allocations adhere to hardware tiers.
8. **Step 8: Lifecycle Integrity, Anti-Branching & Genesis Boundary Audit (G7)**:
   - Verify Genesis gate isolation and simulation ephemeral storage policy (INV-8).
   - Verify `POST /lifecycle/end` is strictly catastrophic decommissioning.
   - Verify anti-branching boundary status as an acknowledged open governance boundary.
9. **Step 9: Automated Regression Test Run (E2)**:
   - Execute test suites (`pytest tests/unit tests/property tests/integration`).
   - Collect and tabulate test pass statistics.
10. **Step 10: Cross-Gate Scenario Verification**:
    - Execute the 5 defined cross-gate evaluation scenarios.
11. **Step 11: MDEP Compilation & Final Audit Report Delivery**:
    - Synthesize all findings into the formal audit report with explicit gate verdicts and Gap Ledger updates.
