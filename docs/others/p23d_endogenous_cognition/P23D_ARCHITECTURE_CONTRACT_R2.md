# P23-D Architecture Contract / R2: Endogenous Cognition & Internal Cognitive Continuity

**Document Identifier**: `DOC-P23D-ARCH-CONTRACT-R2-001`  
**Milestone Scope**: Phase 23-D Architecture Contract (Revision 2)  
**Topic**: Endogenous Cognition & Internal Cognitive Continuity  
**Preceding Baselines**:
- P23-H Bounded Reasoning Kernel & JTMS (`[IMPLEMENTED / FROZEN]`, commit `8e4871d`)
- ADR-035 Production Realization Boundary & S14 Gate (`[IMPLEMENTED / FROZEN]`, commit `3bbe907`)
- ADR-038 Grounded Propositional Causal Ingress Contract (`[SPECIFIED / READY]`)
- Master Research Report — Endogenous Cognitive Lifecycle (`DOC-ECL-RESEARCH-001`, `[RESEARCH VALIDATED]`)
- Endogenous Communication Experimental Harness (`EXP-ENDOGENOUS-COMM-PREFLIGHT-001`, `[RESEARCH VALIDATED]`)  
**Operating Mode**: Specification Only. Zero production runtime code modifications (`src/`), zero test alterations (`tests/`), zero Genesis mutations (`data/profile.json`).  
**Authority**: Architecture Contract Specification  
**Date**: 2026-10-20  

---

## 1. Scope & Non-Goals

### 1.1 Scope Boundaries [ARCHITECTURE CONTRACT]

Phase 23-D (Revision 2) establishes the minimal, rigorous, inspectable architecture contract for **Endogenous Cognition & Internal Cognitive Continuity** in Lucia.

P23-D solves strictly four architectural capabilities:
1. **Unresolved Cognitive Conditions**: Epistemic and cognitive discrepancies, missing premises, and relational conditions can persist across conversational turn boundaries and process boundaries without dying when the Python call stack unwinds.
2. **Qualified Internal Triggering**: Internal state transformations and epistemic developments can qualify to wake bounded cognition without requiring immediate external conversational input ($u_{\text{input}} = \emptyset$).
3. **Internal Cognitive Resolution**: Endogenous cognitive cycles can terminate cleanly in internal resolutions, belief graph revisions, or action affordances without producing surface communicative output.
4. **Decoupled Communicative Affordance**: Communication is treated as a strictly downstream, optional action affordance subject to existing epistemic and relational authorization, never as the default or mandatory completion condition of cognition.

### 1.2 Explicit Non-Goals & Prohibitions [ARCHITECTURE CONTRACT]

Under non-negotiable repository invariants (`INV-1` One Continuous Life, `INV-2` No Reflective Ego, `INV-5` Edge 20W Execution, `INV-8` Genesis Gate), P23-D **MUST NOT** be expanded into:
- **Autonomous Agent Daemon**: No unconstrained autonomous agent loop running in the background.
- **Continuous-Thinking Daemon / Cognitive Clock**: No periodic idle ticking loop that burns CPU/GPU while idle (LIDA/ACT-R clock cycle model is explicitly rejected).
- **Planner / Task Decomposer**: P23-D does not introduce HTN planners, STRIPS planners, or multi-step execution plans.
- **Scheduler / Event Bus**: No global message broker, pub/sub dispatcher, or event bus subsystem.
- **Goal Manager / Goal Buffer Subsystem**: No dedicated multi-level goal buffer subsystem; lifecycle semantics are embedded directly into unresolved conditions.
- **Candidate Arbitration Engine**: No multi-candidate economic auction, bid-weight engine, or speculative candidate scheduler.
- **Global Identity / Persona Layer**: No meta-reflective persona tracking or self-model synthesis (`INV-2`).
- **LLM Controller / Autonomous Prompt Loop**: The local SLM is never used to decide internal cognitive progression; SLM execution remains strictly downstream of realization contracts (ADR-035).
- **Reopening Phase 23-H**: The Phase 23-H Strong Kleene K3 Reasoning Kernel and JTMS remain **strictly frozen** (`[VALIDATED EXISTING CONTRACT]`). P23-D does not mutate or reopen P23-H mechanics.

---

## 2. Definitions & Nomenclature

| Term | Classification | Architectural Definition |
|---|---|---|
| **UnresolvedCondition** | `[ARCHITECTURE CONTRACT]` | A minimal, inspectable, non-volatile cognitive primitive representing a specific, grounded epistemic discrepancy, missing premise, or relational rupture that requires deductive resolution, internal verification, or external information. |
| **Candidate Trigger** | `[ARCHITECTURE CONTRACT]` | An internal state change or substrate discrepancy detected by a local module that possesses potential cognitive relevance, but has not yet met the qualification criteria for cognitive execution. |
| **Qualified Endogenous Trigger** | `[ARCHITECTURE CONTRACT]` | A candidate trigger that has passed deterministic perimeter qualification rules, uniquely references an active condition or discrete state shift, and is authorized to wake bounded cognition. |
| **Endogenous Entry Boundary** | `[ARCHITECTURE CONTRACT]` | A single, guarded entry point on `CognitiveOrchestrator` (`process_endogenous`) that executes a bounded cognitive pass through necessary pipeline invariants without an external sensory string. |
| **Endogenous Cycle** | `[ARCHITECTURE CONTRACT]` | A bounded, non-blocking, non-allocating execution pass through cognitive validation, deductive reasoning, and state adjustment. |
| **Internal Resolution** | `[ARCHITECTURE CONTRACT]` | The terminal state transition of an unresolved condition achieved via symbolic deduction, memory ecphory, or JTMS retraction that resolves the underlying condition without generating external speech. |
| **Action Affordance** | `[ARCHITECTURE CONTRACT]` | A structured, authorized downstream potentiality produced by cognition (e.g., preparing a communicative candidate, updating relationship state, or scheduling passive memory fortification). |
| **Ephemeral Cognitive Snapshot** | `[REPOSITORY FACT]` | Transient dataclass (e.g., `CognitiveStateSnapshot`, `GoalResult`) instantiated during a turn and discarded upon stack exit. |
| **Durable Cognitive State** | `[ARCHITECTURE CONTRACT]` | Epistemic facts in `KnowledgeStore`, relational scalars in `RelationshipState`, dynamical vectors in `EmotionCore`, and persistent `UnresolvedCondition` records surviving turn and process boundaries. |

---

## 3. Boundary A: `UnresolvedCondition` Contract

### 3.1 Ontological Nature [ARCHITECTURE CONTRACT]

An `UnresolvedCondition` is **NOT** a general task, a goal to be planned, a natural-language thought, or an introspective feeling.  
It represents strictly one of three grounded conditions:
1. **Epistemic Incompleteness (`MISSING_PREMISE`)**: A deduction in P23-H stalled because a leaf predicate evaluated to `UNKNOWN` ($K3$) during backward chaining.
2. **Epistemic Inconsistency (`CONTRADICTION`)**: A newly ingested or derived proposition conflicts with an existing verified premise in `KnowledgeStore`, triggering a JTMS conflict record.
3. **Relational Rupture (`RELATIONAL_RUPTURE`)**: A discrete relational discontinuity detected by `RelationshipUpdater` (e.g., trust deficit or conversational boundary violation) requiring relational repair affordance.

### 3.2 Canonical Identity & Reference Semantics [ARCHITECTURE CONTRACT]

- **No Random UUIDs**: Under `[RESEARCH-DERIVED]` findings (`DOC-ECL-RESEARCH-001`, F14), random UUIDs (`uuid4()`) cause catastrophic state duplication and defeat deduplication.
- **Deterministic Content Hash**: Every `UnresolvedCondition` must possess a canonical ID computed deterministically from its referent tuple:
  $$\text{condition\_id} = \text{SHA256}(\text{condition\_type} \parallel \text{canonical\_referent\_key})$$
- For `MISSING_PREMISE`: `canonical_referent_key = f"{predicate_id}:{arg0}:{arg1}:{scope_id}"`
- For `CONTRADICTION`: `canonical_referent_key = f"{term_id_a}:{term_id_b}"` (lexicographically ordered)
- For `RELATIONAL_RUPTURE`: `canonical_referent_key = f"rupture:{epoch_id}:{rupture_code}"`

### 3.3 Minimal Frozen Schema [ARCHITECTURE CONTRACT]

To prevent schema bloat and unverified implementation assumptions, the schema is frozen to the absolute minimal set of required fields:

```text
UnresolvedCondition:
  condition_id: str             # Deterministic SHA256 hex digest
  condition_type: ConditionType # MISSING_PREMISE | CONTRADICTION | RELATIONAL_RUPTURE
  referent_key: str             # Canonical predicate or conflict tuple
  status: ConditionStatus       # ACTIVE | DEFERRED | SUPPRESSED | RESOLVED
  resolution_source: SourceType # INTERNAL_SEARCH | EXTERNAL_USER | SYSTEM_ENVIRONMENT
  epoch_created: int            # Logical epoch ID of creation
```

> [!IMPORTANT]
> **Strict Field Prohibition**:
> The following speculative fields are **STRICTLY EXCLUDED** from the architecture contract and are classified as `[TUNING/EVALUATION]` only:
> - `tension_weight` (rejected: ungrounded scalar; violates continuous PAD dynamics)
> - `retry_count` / `max_retries` (evaluation parameter, not architecture)
> - `timestamps` (wall-clock timestamps are non-deterministic; logical epoch ID is used)
> - `priority_score` (arbitrary float weights rejected; lexicographic ordering governs)
> - `backoff_factor` / `cooldown_seconds` (tuning parameters)
> - `confidence` (rejected under ADR-038 `NEG-02`: scalar confidence corrupts K3 truth values)

### 3.4 Generation & Truth Authority [ARCHITECTURE CONTRACT]

- **Cannot Synthesize Facts**: An `UnresolvedCondition` has **ZERO authority to create or assert propositions, terms, or facts**.
- It is strictly a pointer to an epistemic gap or conflict.
- Any fact created as a consequence of investigating an `UnresolvedCondition` must be admitted through the frozen Phase 23-H / ADR-038 `LanguageIngressGate` or derived by `ReasoningKernel`.

### 3.5 Resolution Criteria [ARCHITECTURE CONTRACT]

An `UnresolvedCondition` transitions to `RESOLVED` if and only if:
1. For `MISSING_PREMISE`: A backward chaining pass in `ReasoningKernel` over the referent predicate returns $K3 \in \{\text{TRUE}, \text{FALSE}\}$ (no longer `UNKNOWN`).
2. For `CONTRADICTION`: One of the conflicting premises is retracted via JTMS dependency cascade, or an explicit override premise is certified by `LanguageIngressGate`.
3. For `RELATIONAL_RUPTURE`: An authorized relational repair action affordance is executed and acknowledged in `RelationshipUpdater`.
4. Epistemic Invalidation: The root query that generated the subgoal is retracted from the system.

---

## 4. Boundary B: Endogenous Entry Boundary

### 4.1 Boundary Contract [ARCHITECTURE CONTRACT]

The Endogenous Entry Boundary is a dedicated entry point on the primary orchestrator:

$$\text{CognitiveOrchestrator.process\_endogenous}(\text{trigger}: \text{QualifiedEndogenousTrigger}) \to \text{EndogenousResult}$$

### 4.2 Structural Invariants [ARCHITECTURE CONTRACT]

1. **Not a Parallel Pipeline**: `process_endogenous` is an **alternate entry boundary into the single canonical cognitive pipeline**, not a second orchestrator or secondary cognitive engine.
2. **Sensor Bypass with Epistemic Preservation**:
   - Stage S0 (`TemporalEmbodimentCoordinator.process_observation`) is executed with an internal tick observation ($u_{\text{text}} = \emptyset$).
   - Stage S1 (`StimulusProcessor` lexical parsing) is **bypassed** because there is no external natural-language utterance.
   - Stages S2 through S8 operate over the current committed internal state ($PAD$, $R$, memory traces, and structured knowledge).
3. **No Pipeline Jumping**: Endogenous execution **MUST NOT** jump directly into an arbitrary intermediate stage (e.g. directly into S10b CAPS or S13 LLM generation). It must traverse the pipeline sequentially, evaluating homeostatic constraints and ecphoric recall.
4. **Guards & Invariants Enforced**:
   - Must hold orchestrator turn lock (`_turn_lock`).
   - Must enforce 20W compute budget: non-blocking CPU operations only; zero GPU SLM generation unless an authorized communicative affordance is formally certified.
   - P23-H Strong Kleene K3 semantics and JTMS invariants cannot be bypassed.

---

## 5. Boundary C: Trigger Qualification Boundary

### 5.1 The 4-Stage Activation Chain [ARCHITECTURE CONTRACT]

To strictly prevent unconstrained spin-loops while allowing legitimate cognitive awakening, state transformations must pass through an explicit 4-stage qualification filter:

```text
┌────────────────────────────────┐
│   Internal State Change        │  (Level 1, Level 2, or Level 3 event)
└───────────────┬────────────────┘
                │
                ▼
┌────────────────────────────────┐
│   Candidate Trigger Detection  │  (Local module detects potential cognitive relevance)
└───────────────┬────────────────┘
                │
                ▼
┌────────────────────────────────┐
│ Trigger Qualification Boundary │  (Deterministic, stateless qualification rules)
└───────────────┬────────────────┘
                │ [QUALIFIED]
                ▼
┌────────────────────────────────┐
│ process_endogenous(trigger)    │  (Bounded cognitive execution)
└────────────────────────────────┘
```

### 5.2 Authority & Responsibilities [ARCHITECTURE CONTRACT]

- **Who Detects Candidate Triggers?**:
  Candidate triggers are detected locally at the boundary of substantive state mutations:
  - `KnowledgeStore`: on ingestion of a premise that produces an explicit JTMS conflict.
  - `ReasoningKernel`: on completion of a backward chaining query that emits an `InformationSubgoal` with status `UNKNOWN`.
  - `RelationshipUpdater`: on discrete transition into a relational rupture state.
- **Who Qualifies Candidate Triggers?**:
  `TriggerQualificationBoundary` (a pure, stateless, deterministic filter function embedded within orchestrator governance, **NOT** a background daemon or event bus).

### 5.3 Trigger Qualification Rules [ARCHITECTURE CONTRACT]

A candidate trigger is qualified into a `QualifiedEndogenousTrigger` if and only if **all** of the following conditions hold:
1. **Grounded Referent Requirement**: The trigger explicitly references an existing `UnresolvedCondition` in state `ACTIVE` or `REACTIVATABLE`, or references a certified discrete relational rupture.
2. **Non-Maintenance Invariant**: Maintenance dynamics (Level 1: continuous ODE integration, Philia relaxation, SDM trace weight decay) are **STRICTLY DISQUALIFIED**.
3. **Turn Non-Concurrency**: The orchestrator is not currently executing an external user turn.
4. **Anti-Cascading / Bounded Re-entrance**: An endogenous execution cycle **CANNOT** qualify a new trigger within the same cycle. Maximum endogenous cascade depth $= 1$. A secondary trigger generated during endogenous execution is saved as `DEFERRED` for evaluation in a subsequent epoch.

---

## 6. Boundary D: Internal Resolution vs. Communication Boundary

### 6.1 The Non-Communicative Completion Invariant [ARCHITECTURE CONTRACT]

$$\text{Endogenous Cognition} \to \text{Internal Resolution} \lor \text{Action Affordance} \to [\text{Optional Communication}]$$

1. **Communication is Downstream and Optional**: External natural-language communication is **NEVER** the default, required, or primary completion condition of an endogenous cycle.
2. **Silent Completion is Valid**: The vast majority of endogenous cycles must complete **silently**:
   - Updating JTMS term validity.
   - Retracting invalidated derived propositions.
   - Marking an `UnresolvedCondition` as `RESOLVED`.
   - Shifting relational or homeostatic parameters.

### 6.2 Communication Authorization Perimeter [ARCHITECTURE CONTRACT]

If an endogenous cycle yields a communicative affordance (e.g., an inquiry regarding a missing premise resolvable only by the user, or an essential relational repair):
1. **Epistemic Authorization Required**:
   - P23-H `TRUE` $\ne$ `ASSERT` (`[VALIDATED EXISTING CONTRACT]`, `DOC-P23H-RUNTIME-INTEGRATION-SPEC-R1-001`). Deriving a truth value or encountering a missing premise does **not** grant communicative warrant.
   - The proposition/subgoal must pass through `LanguageIngressGate` and CAPS.
2. **CAPS Grounding Enforcement**: CAPS Priority 5 fail-closed grounding must verify that the candidate predicate and arguments are fully grounded in `AdmissibleEvidencePool`. Ungrounded candidates trigger `SILENCE`.
3. **Turn Floor & Dyadic Stance**: Communication cannot proceed if the user currently holds the conversational floor, or if homeostatic behavioral constraints dictate low output volume.
4. **Quarantine of Unprompted Speech**:
   > [!CAUTION]
   > **UNPROMPTED INITIATION QUARANTINE**:  
   > Unprompted communicative speech acts remain classified as **`[RESEARCH / QUARANTINED]`**.  
   > In P23-D R2, an authorized communicative affordance resulting from endogenous cognition is buffered as a **deferred conversational bias for the NEXT user turn**, or silenced. The system **WILL NOT** autonomously transmit unprompted speech or synthetic audio to the user output device without explicit governance unlocking.

---

## 7. Persistence & Recovery Semantics

### 7.1 Cross-Turn Continuity [ARCHITECTURE CONTRACT]

- `UnresolvedCondition` records survive conversational turn boundaries in memory within `CognitiveOrchestrator`'s internal condition ledger.
- A user turn does not flush, reset, or corrupt existing unresolved conditions.

### 7.2 Persistence Boundary Audit & Verdict [REPOSITORY FACT & CONTRACT]

A rigorous codebase audit of Lucia's existing persistence subsystems was performed:
1. **`EpochManifest` (`src/core/emotion/persistence.py`)**:
   - `[REPOSITORY FACT]`: `EpochManifest` is strictly a synchronized commit barrier recording epoch integers across existing stores:
     ```python
     stores={"relationship": next_epoch, "dynamical_state": next_epoch}
     ```
   - It contains zero schema, data structures, or serializers for entities, subgoals, or cognitive conditions.
   - **Verdict**: Using `EpochManifest` as a condition store is an **architectural violation**. It is an epoch barrier, not an entity database.
2. **`KnowledgeStore` (`src/core/knowledge/`)**:
   - Stores propositions $(S, P, O)$ and rules.
   - Currently lacks $(S,P,O)$ canonical deduplication (generates random UUIDs on derivations; `store.py:37`).
   - Does not have a lifecycle state machine for condition tracking.
3. **`AffectiveMemory` (`src/core/memory/`)**:
   - SDM continuous vector store; completely unsuitable for discrete condition records.

### Authoritative Persistence Boundary Verdict:

$$\text{PERSISTENCE BOUNDARY} = \text{UNRESOLVED / REQUIRES REPOSITORY DECISION}$$

- In P23-D R2, durable cross-restart persistence of `UnresolvedCondition` is explicitly marked as **`[OPEN CONTRACT ITEM]`**.
- Conditions persist in-memory across turns during process lifetime.
- Durable disk serialization requires an explicit, dedicated JSON/atomic storage schema (`data/cognitive_conditions.json`) ratified under a future storage decision, without overloading `EpochManifest`.

### 7.3 Recovery & Corruption Semantics [ARCHITECTURE CONTRACT]

1. **Fail-Closed on Recovery**: If durable condition records are found corrupted, unparseable, or schema-invalid during boot:
   - The corrupted record is quarantined to a `.corrupt` diagnostic file.
   - Boot sequence **MUST NOT** crash.
   - Corrupted conditions are treated as non-existent (fail-closed); they are **NEVER** promoted into active memory or allowed to trigger cognition.
2. **Idempotent Recovery & Deduplication**: Recovery uses `condition_id` (SHA256 hash). If duplicate keys appear, the record with the most recent `epoch_created` is retained; duplicates are dropped.

---

## 8. Lifecycle & State Transitions

### 8.1 Minimal State Machine [ARCHITECTURE CONTRACT]

The lifecycle of an `UnresolvedCondition` is governed by a strictly minimal 4-state transition graph:

```text
       ┌──────────────┐
       │    ACTIVE    │◄──────────────┐
       └──────┬───────┘               │
              │                       │
      [Interrupt / Defer]      [Reactivate]
              │                       │
              ▼                       │
       ┌──────────────┐               │
       │   DEFERRED   │───────────────┤
       └──────┬───────┘               │
              │                       │
      [Suppress / Cooldown]           │
              │                       │
              ▼                       │
       ┌──────────────┐               │
       │  SUPPRESSED  │───────────────┘
       └──────┬───────┘
              │
         [Resolved]
              │
              ▼
       ┌──────────────┐
       │   RESOLVED   │ (Terminal -> Pruned)
       └──────────────┘
```

### 8.2 State Transition Matrix [ARCHITECTURE CONTRACT]

| Source State | Target State | Triggering Condition | Architectural Necessity |
|---|---|---|---|
| `ACTIVE` | `DEFERRED` | Orchestrator receives higher-priority user input, or compute budget reached. | Preserves condition across turns without losing progress. |
| `ACTIVE` | `RESOLVED` | Condition resolved internally (K3 value determined, contradiction cleared). | Terminal completion; releases cognitive load. |
| `ACTIVE` | `SUPPRESSED` | Qualification fails repeatedly, or candidate communication denied by CAPS. | Anti-repetition / refractory protection. |
| `DEFERRED` | `ACTIVE` | Endogenous cycle initiates and selects condition for evaluation. | Resumes bounded investigation. |
| `DEFERRED` | `RESOLVED` | Condition rendered moot by external user statement or premise retraction. | Passive resolution / garbage collection. |
| `SUPPRESSED` | `DEFERRED` | Refractory period elapses or new epistemic evidence arrives. | Allows eventual re-evaluation without spamming. |
| `SUPPRESSED` | `RESOLVED` | Invalidation of root term or explicit manual dismissal. | Prevents ghost conditions. |

### 8.3 Embedded Lifecycle Semantics [ARCHITECTURE CONTRACT]

- **No Separate Inhibition Ledger**: Candidate inhibition and suppression are **native state transitions** of `UnresolvedCondition` (`SUPPRESSED`), not a separate subsystem.
- **No Separate Goal Buffer**: Condition tracking is directly managed via a bounded collection (`max_active <= 4`) inside `CognitiveOrchestrator`.

---

## 9. Trigger Taxonomy & Architectural Mapping

The research trigger taxonomy (`DOC-ECL-RESEARCH-001`) is mapped to rigid architectural enforcement boundaries:

```text
====================================================================================================
Taxonomy Level       Physical Phenomenon              Architectural Boundary Action
====================================================================================================
Level 1:             ODE integration (200ms),        STRICTLY FORBIDDEN from triggering cognition.
Maintenance          Philia resting decay,           Executes in background maintenance threads.
Dynamics             SDM trace decay, LNN trainer.   Zero event emission. Zero cognitive wake-up.
----------------------------------------------------------------------------------------------------
Level 2:             Continuous PAD trajectory,      Passive context modulation only.
Latent / Internal    Homeostatic energy recovery,    Alters generation temperature, pacing, or
Transformation       Relational score drift.         lexical choice IF a turn occurs. Never wakes.
----------------------------------------------------------------------------------------------------
Level 3:             Missing premise (K3 UNKNOWN),   Candidate trigger evaluated by
Epistemic /          JTMS contradiction,             TriggerQualificationBoundary.
Cognitive Trigger    Discrete relational rupture.    MAY qualify to wake process_endogenous().
----------------------------------------------------------------------------------------------------
Level 4:             Subgoal requiring user input,   Downstream affordance only.
Communicative        Acute relational repair.        Subject to CAPS authorization.
Impulse                                              QUARANTINED from unprompted initiation.
====================================================================================================
```

---

## 10. Concurrency & Safety Invariants

### 10.1 Concurrency Invariants [ARCHITECTURE CONTRACT]

1. **Turn Lock Serialization**:
   - `CognitiveOrchestrator` maintains an exclusive execution lock (`_turn_lock`).
   - `process_endogenous` must acquire `_turn_lock` before executing.
   - If an external user turn arrives while `process_endogenous` is running:
     - The endogenous cycle must immediately abort at the next stage boundary.
     - Ephemeral intermediate states are discarded.
     - The active condition is safely reverted to `DEFERRED`.
     - The user turn acquires `_turn_lock` with strict priority.
2. **Lock Hierarchy & Concurrency Window**:
   - Memory copy / state read locks must be held $\le 1\text{ ms}$.
   - Never hold `_turn_lock` or internal state locks during disk I/O, audio playback, or SLM inference.

### 10.2 Safety & Epistemic Invariants [ARCHITECTURE CONTRACT]

1. **Non-Reentrant Execution**:
   - `process_endogenous` cannot recursively invoke `process_endogenous`. Maximum endogenous call stack depth $= 1$.
2. **Fail-Closed Execution**:
   - Any unhandled exception during endogenous execution aborts the cycle cleanly.
   - Durable state stores (`KnowledgeStore`, `RelationshipState`) remain unmodified.
3. **Anti-Self-Echo Invariant (F15 Protection)**:
   - Lucia cannot treat self-generated candidate subgoals or internal inferences as external user claims (`USER_STATED`).
   - Every condition and candidate carries explicit origin provenance (`ASSISTANT_INFERRED` or `INTERNAL_GAP`).
4. **Epistemic Non-Escalation**:
   - An endogenous cycle **NEVER** promotes an `INFERRED` proposition to `FACT`. Only external validation or foundational axiomatic rules can grant `FACT` status.

---

## 11. Existing Lucia Components Reused

P23-D maximizes architectural reuse of verified, frozen components without reinvention:

| Existing Component | Source File Path | Role in P23-D Endogenous Cognition | Status |
|---|---|---|---|
| `CognitiveOrchestrator` | `src/core/orchestrator/cognitive_orchestrator.py` | Hosts `process_endogenous` entry point, owns condition ledger, manages `_turn_lock`. | `[REUSED / EXTENDED ENTRY]` |
| `ReasoningKernel` | `src/core/cognition/kernel/engine.py` | Evaluates missing premises, backward chains over rules via Strong Kleene K3. | `[REUSED AS-IS / FROZEN]` |
| `JTMS` | `src/core/cognition/kernel/jtms.py` | Detects premise contradictions, executes non-monotonic downward invalidation. | `[REUSED AS-IS / FROZEN]` |
| `RuleIndex` | `src/core/cognition/kernel/rules.py` | Provides fast head-predicate indexing for Horn clause resolution. | `[REUSED AS-IS / FROZEN]` |
| `KnowledgeStore` | `src/core/knowledge/store.py` | Stores verified propositions $(S, P, O)$ and symbolic rules. | `[REUSED AS-IS]` |
| `CAPS` | `src/core/communication/caps.py` | Evaluates grounding and communicative authorization (Gate R1/R4, Priority 5). | `[REUSED AS-IS]` |
| `RealizationInputContract` | `src/core/language/contract.py` | Decoupled downstream contract boundary for surface language realization. | `[REUSED AS-IS / FROZEN]` |
| `SemanticFidelityGate` | `src/core/language/gate.py` | Enforces fail-closed linguistic safety and blocks introspective ego-talk regexes. | `[REUSED AS-IS / FROZEN]` |
| `LanguageIngressGate` | `src/core/language/adapter/gate.py` | Validates premise admissibility and blocks F15 echo escalation (ADR-038). | `[REUSED AS-IS]` |
| `RelationshipUpdater` | `src/core/relationship/updater.py` | Reads dyadic trust/familiarity and flags relational rupture conditions. | `[REUSED AS-IS]` |

---

## 12. Minimal Genuinely Missing Primitives

Only **three minimal primitives** are genuinely missing from the repository to satisfy this architecture contract:

1. **`UnresolvedCondition` Data Structure**:
   - Location: `src/core/cognition/contract/condition.py`
   - Purpose: Minimal frozen dataclass holding condition identity, type, referent key, and lifecycle status.
2. **`TriggerQualificationBoundary`**:
   - Location: `src/core/cognition/qualification.py` (or static method on orchestrator)
   - Purpose: Deterministic, pure filter validating candidate triggers against Level 1–4 taxonomy and anti-cascading rules.
3. **`process_endogenous` Entry Boundary**:
   - Location: `src/core/orchestrator/cognitive_orchestrator.py`
   - Purpose: Guarded execution boundary on orchestrator orchestrating S0, S2..S8, and S10b when $u_{\text{text}} = \emptyset$.

---

## 13. Explicit Rejected Architectures

The following architectural proposals were explicitly investigated and **REJECTED**:

| Rejected Architecture | Rationale for Rejection |
|---|---|
| **Autonomous Background Agent Daemon** | Violates 20W power envelope; risks split-brain state mutations (`INV-1`); creates illusion of reflective ego (`INV-2`). |
| **Periodic Clock Ticking (LIDA/ACT-R)** | Continuous idle ticking wastes CPU cycles, drains battery on edge hardware, and induces runaway repetition pathologies (F1, F11, F12). |
| **Global Event Bus / Message Broker** | Adds asynchronous indirection, race hazards, non-deterministic execution order, and difficult debugging without adding cognitive value. |
| **Dedicated Goal Buffer Subsystem** | Unnecessary architectural overhead. Lifecycle state transitions directly on `UnresolvedCondition` provide identical semantics with zero indirection. |
| **Candidate Arbitration Auction Engine** | CAPS Priority 1–5 already provides lexicographic, fail-closed authorization. Introducing a multi-agent utility auction engine is unwarranted complexity. |
| **Persistent Grounded Referent (PGR) Container** | Disproven in `DOC-ECL-RESEARCH-001`: PGR created a localized data container without an execution engine or resolution semantics. |
| **Autonomous Unprompted Speech Daemon** | Bypasses dyadic conversational etiquette; generates ungrounded conversational spam; violates F8 self-echo safety; quarantined. |
| **Using `EpochManifest` as Condition Store** | Confirmed by code audit to be an epoch commit barrier for consistency detection, not an entity/condition storage mechanism. |

---

## 14. Tuning & Evaluation Parameters (NOT Architecture Contract)

The following parameters are **NOT part of the architecture contract**. They are reserved strictly for experimental evaluation, tuning, and calibration in test harnesses:

| Parameter Category | Specific Parameters | Classification |
|---|---|---|
| **Temporal Cooldowns** | `120s` idle wait, `600s` communication cooldown, `300s` rupture refractory period | `[TUNING/EVALUATION]` |
| **Execution Budgets** | `max_retries = 3`, `max_derivation_depth k = 2`, `timeout = 5ms` | `[TUNING/EVALUATION]` |
| **Energy & Affect Thresholds** | `energy >= 0.70`, `familiarity >= 0.40`, `tension > 0.65` | `[TUNING/EVALUATION]` |
| **Buffer Capacities** | `max_active_conditions = 4`, `max_deferred_conditions = 16` | `[TUNING/EVALUATION]` |
| **Latency Tolerances** | `< 0.5ms` qualification latency, `< 2.0ms` endogenous cycle latency | `[TUNING/EVALUATION]` |

---

## 15. Open Research Questions (Pre-Implementation)

The following items are recognized as open research / design dependencies:

- **RQ-1 (Substrate Identity Deduplication)**: `KnowledgeStore` currently indexes by caller-supplied random UUIDs. A contract for deterministic $(S, P, O, \text{scope})$ hash indexing is required before multi-turn condition resolution can achieve 100% reliability.
- **RQ-2 (Durable Condition Storage Authority)**: Since `EpochManifest` is audited and rejected as a condition store, a formal storage authority (e.g. `data/conditions.json` with crash-safe atomic replace) must be ratified.
- **RQ-3 (Unprompted Communication Verification)**: Defining the formal verification protocol under which unprompted communicative affordances can ever be safely de-quarantined without violating dyadic social boundaries.

---

## 16. Implementation Readiness Verdict

### Final Verdict:
```text
================================================================================
                    P23-D R2 ARCHITECTURE CONTRACT VERDICT:
                       READY FOR IMPLEMENTATION SPEC
          (Open Items Resolved in DOC-P23D-R2-ADDENDUM-001)
================================================================================
```

### Resolution of Open Items (via `DOC-P23D-R2-ADDENDUM-001`):
1. **Durable Persistence Authority**: Ratified as `data/cognitive_conditions.json` with `.json.bak` and atomic temporary rename under `CognitiveOrchestrator` ownership.
2. **Substrate Deduplication & Referent Key**: Ratified canonical key format `"{scope}:{subject}:{predicate}:{object}"` mapped via verified `SymbolTable` adapter; `condition_id` computed via deterministic SHA-256 hash.
3. **Unprompted Communication Quarantine**: Affirmed as strictly quarantined (`[RESEARCH / QUARANTINED]`); implementation is limited to silent internal resolution and deferred candidate biasing.

---

## 17. Master Freeze Matrix

| Item | Status | Governing Authority | Notes |
|---|:---:|---|---|
| **UnresolvedCondition Contract** | **FROZEN** | §3, DOC-P23D-ARCH-CONTRACT-R2-001 | Minimal schema, deterministic hash ID, no speculative fields. |
| **Endogenous Entry Boundary** | **FROZEN** | §4, DOC-P23D-ARCH-CONTRACT-R2-001 | `process_endogenous` entry point; enforces pipeline invariants. |
| **Trigger Qualification Boundary** | **FROZEN** | §5, DOC-P23D-ARCH-CONTRACT-R2-001 | 4-stage filter; anti-cascading depth = 1; maintenance blocked. |
| **Internal vs. Communication Boundary** | **FROZEN** | §6, DOC-P23D-ARCH-CONTRACT-R2-001 | Communication is downstream/optional; silent resolution valid. |
| **Persistence Boundary** | **FROZEN** | DOC-P23D-R2-ADDENDUM-001 | Ratified `data/cognitive_conditions.json` with atomic replace & `.bak`. |
| **Lifecycle State Machine** | **FROZEN** | §8, DOC-P23D-ARCH-CONTRACT-R2-001 | 4-state machine (`ACTIVE`, `DEFERRED`, `SUPPRESSED`, `RESOLVED`). |
| **Thresholds / Backoff / Retries** | **EVALUATION ONLY** | §14, DOC-P23D-ARCH-CONTRACT-R2-001 | Strictly excluded from architecture contract. |
| **Unprompted Communication** | **QUARANTINED** | §6.2, ADR-035, INV-2 | Research quarantine; no autonomous audio/text output. |
| **Phase 23-H Bounded Reasoning** | **FROZEN / DO NOT REOPEN** | Commit `8e4871d`, P23-H Spec | K3 engine and JTMS remain 100% frozen. |
