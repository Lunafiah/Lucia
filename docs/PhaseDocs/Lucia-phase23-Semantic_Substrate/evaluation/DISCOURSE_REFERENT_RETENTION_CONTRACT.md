# Discourse Referent Retention Contract & Specification (Phase 23)

> **Document Type**: Architectural Contract & Specification Document  
> **Status**: [ARCHITECTURALLY RATIFIED] (Formal Architectural Decision Record Embedded)  
> **Target Subsystem**: Semantic Substrate / Turn Lifecycle Coordinator (Cross-Turn Discourse Context)  
> **Phase**: Phase 23 — Semantic Substrate & Non-Generative Communication  
> **Date**: 2026-10-14  
> **Author**: Antigravity (Lucia Architectural Copilot)  
> **Execution Mode**: Research Specification & Isolated Empirical Benchmark (Zero Production Mutations)  

---

## 1. Scope & Governance

### 1.1 Objective
This specification formalizes the **minimal architectural contract** required to retain, decay, and resolve active discourse referents across conversational turns in the Lucia architecture without dependency on Large Language Models (LLM) or Small Language Models (SLM). 

It directly addresses the single blocking gap identified in the CAPS Implementation Readiness Gate (R3):
$$\text{Production Runtime Context: Raw Text Tuples } \longrightarrow \text{Bounded Semantic Discourse Referent Cache}$$

### 1.2 Strict Governance Constraints
In strict accordance with [`AGENTS.md`](file:///c:/Users/Lunafiah/Desktop/My_project/Lucia/AGENTS.md) and project invariants:
- **Zero Production Mutations**: No code in `src/core/**`, `electron/**`, or `data/**` is modified.
- **Genesis Lock Invariant**: [`data/profile.json`](file:///c:/Users/Lunafiah/Desktop/My_project/Lucia/data/profile.json) remains bit-exact (`{"is_onboarded": false}`). Zero live activation.
- **Contract Boundary Integrity**: Does NOT modify [`docs/PhaseDocs/Lucia-phase23-Semantic_Substrate/P23_CAPS_BOUNDARY_CONTRACT_DESIGN.md`](file:///c:/Users/Lunafiah/Desktop/My_project/Lucia/docs/PhaseDocs/Lucia-phase23-Semantic_Substrate/P23_CAPS_BOUNDARY_CONTRACT_DESIGN.md); preserves all ratified decisions S1–S16.
- **No Monolithic Subsystem**: This contract defines a lightweight, bounded state container. It does NOT introduce a `DiscourseContextManager` or a new monolithic cognitive subsystem.
- **Anti-Memory Guard**: Discourse retention is strictly bounded working context for anaphora resolution; it is **NOT** episodic memory, **NOT** long-term memory, and **NOT** a conversation transcript model.

---

## 2. Existing Architecture Evidence

A forensic audit of the active repository reveals the exact divide between current production history handling and Phase 23 semantic capabilities:

| Component / Subsystem | Repository Location | Current State & Behavior | Proven Architectural Property |
|---|---|---|---|
| **Production Context History** | [`src/core/orchestrator/cognitive_orchestrator.py:108–115, 737–741`](file:///c:/Users/Lunafiah/Desktop/My_project/Lucia/src/core/orchestrator/cognitive_orchestrator.py#L108-L115) | `self._history: List[Tuple[str, str]] = []`. Stores only raw strings `("user", text)`, `("assistant", text)`. | Proves production runtime has **zero semantic entity tracking** across conversational turns. Context exists purely as text prompts for SLM. |
| **Phase 23-D Coreference Evaluation** | [`tests/evaluation/evaluation_phase23d/experiment_03_coreference/models/umr_coreference.py`](file:///c:/Users/Lunafiah/Desktop/My_project/Lucia/tests/evaluation/evaluation_phase23d/experiment_03_coreference/models/umr_coreference.py#L8-L170) | `UMRCoreferenceSubstrate`: Deterministic resolution using discourse salience, syntactic roles, gender/animacy filters, and fail-closed non-hallucinatory boundaries. | Verified in [`test_exp03_coreference.py`](file:///c:/Users/Lunafiah/Desktop/My_project/Lucia/tests/evaluation/phase23d/test_exp03_coreference.py): achieve $\text{CEAF-e } F_1 \ge 0.82$, zero-anaphora non-hallucination (`UNKNOWN_ENTITY`), and ambiguity preservation (`AMBIGUOUS_UNRESOLVED`). |
| **Semantic Graph Structures** | [`src/core/knowledge/fortification.py:194–298`](file:///c:/Users/Lunafiah/Desktop/My_project/Lucia/src/core/knowledge/fortification.py#L194-L298) | `SemanticNode`, `SemanticEdge`, `EpistemicState` (`FACT`, `INFERRED`, `AMBIGUOUS`, `UNKNOWN`). | Discrete language-independent semantic representation with formal epistemic typing and scope boundaries. |
| **Term Arena & Symbol Table** | [`src/core/cognition/contract/projection.py:45–75`](file:///c:/Users/Lunafiah/Desktop/My_project/Lucia/src/core/cognition/contract/projection.py#L45-L75), [`arena.py:33–100`](file:///c:/Users/Lunafiah/Desktop/My_project/Lucia/src/core/cognition/contract/arena.py#L33-L100) | `SymbolTable` maps string symbols to integers. `TermArena` uses static preallocated memory (`max_terms=4096, max_entities=2048`). | Demonstrates established repository invariant: zero dynamic reallocation in cognitive inner loops. |

---

## 3. Problem Statement

Under the current generative pipeline, when a user says:
- **Turn $N$**: *"Lucia, con mèo hàng xóm lại sang chơi."* (Mentions entity `ent:cat_neighbor`)
- **Turn $N+1$**: *"Nó có đói không?"* (Uses pronoun *"Nó"*)

The generative SLM implicitly resolves *"Nó"* using internal attention over previous text strings in `_history`. 

However, in a **Zero-LLM/SLM non-generative communication pipeline**, Turn $N+1$ is parsed directly into a language-independent `SemanticGraph`:
```text
(s01 / hungry-01
     :ARG0 (m01 / ?PRONOUN_UNRESOLVED))
```
Without an active discourse referent cache:
1. The parser cannot resolve `m01` to `ent:cat_neighbor`.
2. Downstream CAPS cannot ground the interrogative query against `KnowledgeStore`.
3. The system is forced to fail-closed into `UNKNOWN` or ask redundant clarification questions.

**Goal**: Formulate a deterministic, bounded, and inspectable discourse state that bridges Turn $N$ and Turn $N+1$ at the semantic layer without expanding into an unconstrained memory system.

---

## 4. Discourse Referent Definition

### 4.1 Strict Conceptual Boundaries
To prevent architectural mission creep, an active discourse referent is strictly distinguished from all other repository memory types:

```text
┌─────────────────────────────────────────────────────────────────────────────┐
│                       REPOSITORY MEMORY TAXONOMY                            │
├───────────────────────┬─────────────────────────────────────────────────────┤
│ World Knowledge       │ Permanent, verified encyclopedic facts in           │
│                       │ KnowledgeStore (e.g., "Cats are felines").           │
├───────────────────────┼─────────────────────────────────────────────────────┤
│ Episodic Memory       │ Long-term relational traces in SDM / AffectiveMemory│
│                       │ and chat_history.json (e.g., past conversations).   │
├───────────────────────┼─────────────────────────────────────────────────────┤
│ Conversation History  │ Raw sequential transcript of dialogue turns.       │
├───────────────────────┼─────────────────────────────────────────────────────┤
│ Active Discourse      │ TEMPORARY, bounded working set of entities/events   │
│ Referent (THIS SPEC)  │ currently prominent in the active dialogue focus,    │
│                       │ used solely to resolve anaphora and ellipses.       │
└───────────────────────┴─────────────────────────────────────────────────────┘
```

### 4.2 Minimal Referent Schema
A discourse referent MUST only contain attributes required for reference resolution and salience ranking. Non-essential metadata (such as full utterances, emotional embeddings, or long-term weights) is strictly excluded.

```python
@dataclass(frozen=True)
class DiscourseReferent:
    """Minimal language-independent active discourse referent."""
    entity_id: str                      # Canonical semantic entity ID (e.g. "ent:cat_01")
    concept_id: str                     # Ontological category (e.g. "c:FELINE")
    salience: float                     # Prominence in active focus [0.0, 1.0]
    turn_introduced: int                # Turn number when introduced into discourse
    last_referenced_turn: int           # Turn number when most recently mentioned
    grammatical_role: str = ":ARG0"     # Syntactic role in last mention (:ARG0, :ARG1, :TOPIC)
    gender: Optional[str] = None        # "MASCULINE", "FEMININE", "NEUTER" (for overt pronouns)
    animacy: Optional[str] = None       # "ANIMATE", "INANIMATE" (for animacy filters)
```

---

## 5. Minimal State Representation

The active discourse context is represented as a single bounded collection:

```python
class DiscourseContextCache:
    """
    Bounded, inspectable active referent set for conversational turn linking.
    O(1) memory bound, deterministic LRU/salience eviction.
    """
    def __init__(
        self,
        max_capacity: int = 16,
        decay_gamma: float = 0.60,
        eviction_threshold: float = 0.15,
    ) -> None:
        self.max_capacity: int = max_capacity
        self.decay_gamma: float = decay_gamma
        self.eviction_threshold: float = eviction_threshold
        self._referents: Dict[str, DiscourseReferent] = {}
```

---

## 6. Lifecycle & Turn Boundary Execution

### 6.1 Pipeline Execution Flow
The discourse cache interacts with the cognitive turn at two explicit, non-overlapping boundaries:

```text
TURN N+1 INGRESS
  │
  ├─ 1. User Input Received
  │
  ├─ 2. Semantic Parsing / Mention Extraction
  │       Unresolved pronouns & zero-anaphora detected
  │
  ├─ 3. Discourse Lookup & Resolution (READ-ONLY)
  │       Query: DiscourseContextCache.resolve_reference(...)
  │       Result: Entity bound to SemanticGraph node OR EpistemicState set
  │
  └─ 4. Ingress SemanticGraph Formed & Fortified
        │
        ▼
COGNITIVE CORE EXECUTION
  │ (Homeostasis, Coupled MT-LNN Emotion, Active Inference, Reasoning Kernel)
  │ Downstream CAPS selects Communicative Act & Outgoing Grounded Proposition
        │
        ▼
TURN N+1 EGRESS
  │
  ├─ 5. Surface Realization / Output Emitted
  │
  └─ 6. Discourse Cache Turn Update (MUTATION)
          - All existing referents decayed: S_{t+1} = S_t * gamma
          - Entities mentioned in Turn N+1 (user + agent) refreshed or inserted: S = 1.0
          - Pruning: Evict S < eviction_threshold
          - Bounding: If count > max_capacity, evict lowest salience
```

### 6.2 Strict Invariants
1. **No Mutation During Ingress**: `DiscourseContextCache` is strictly read-only during reference resolution.
2. **Atomic Egress Update**: Cache mutation occurs exactly once per turn at the end of `CognitiveOrchestrator.process()`.
3. **No Dynamic Growth**: Preallocated or strictly bounded dictionary ($|R| \le N_{\text{max}}$).

---

## 7. Reference Resolution Semantics

When resolving an anaphoric mention, the resolution algorithm evaluates candidates through a deterministic filter pipeline:

$$\text{All Active Referents} \xrightarrow{\text{Concept/Type Filter}} \xrightarrow{\text{Animacy Filter}} \xrightarrow{\text{Gender Filter}} \text{Candidate Pool}$$

### Ranking Function
If multiple candidates pass the filters, they are ranked lexicographically by the deterministic score tuple:

$$\text{Score}(r) = \big(\text{round}(\text{salience}, 4),\; \mathbb{I}(\text{role} == \text{target\_role}),\; \text{last\_referenced\_turn}\big)$$

1. **Salience Score**: Prominence decaying over unmentioned turns.
2. **Syntactic Role Match**: Subject preference for subject pronouns; object preference for object pronouns.
3. **Recency**: Most recently referenced candidate breaks ties.

---

## 8. Ambiguity, Failure Semantics & Epistemic Orthogonality

### 8.1 Critical Principle: Reference Resolution State $\ne$ Epistemic State
A fundamental architectural invariant governs the interface between discourse reference resolution and cognitive truth maintenance:

> **Reference resolution determines whether a discourse referent can be identified.**  
> **Epistemic state determines the epistemic status of the proposition associated with that referent.**

These two dimensions are strictly orthogonal and MUST NOT be conflated into a single enum or semantic dimension:
- **Reference Resolution Status** (Discourse / Linguistic Interface):
  - `RESOLVED`: The discourse referent is uniquely identified in the active context.
  - `AMBIGUOUS`: Multiple competing referents pass filters with equal top score.
  - `UNKNOWN / UNRESOLVED`: No candidate referent exists in active context (or all were evicted).
  - `TYPE_MISMATCH`: Referents exist, but all fail ontological concept, animacy, or gender constraints.
- **Epistemic State** (Epistemic / Knowledge Layer, [`src/core/knowledge/fortification.py`](file:///c:/Users/Lunafiah/Desktop/My_project/Lucia/src/core/knowledge/fortification.py#L59-L68)):
  - `FACT`: Verified empirical ground truth in `KnowledgeStore`.
  - `INFERRED`: Derived knowledge supported by formal derivation rules and active premises.
  - `AMBIGUOUS`: Multiple conflicting interpretations or hypotheses.
  - `UNKNOWN`: Missing or ungrounded proposition.

### 8.2 Non-Equivalence Invariants
1. $\mathbf{RESOLVED \neq FACT}$: Successfully identifying who or what an utterance refers to (e.g. resolving pronoun *"he"* to `ent:user_brother`) does NOT make the statement about that entity factual.
2. $\mathbf{USER\_STATED\ provenance \neq FACT\ epistemic\ status}$: When a user states *"He is a doctor"*, reference resolution is `RESOLVED`, but the proposition carries `provenance = USER_STATED` and enters epistemic state `ASSERTED` or `HYPOTHETICAL` ($C \le 0.70$). It is strictly forbidden from automatic promotion to `FACT`.

### 8.3 Mapping Matrix: Discourse Resolution $\longrightarrow$ SemanticGraph & Downstream Action

```text
┌───────────────────────────────┬─────────────────────────────┬───────────────────────────┬────────────────────────────────────────────────────────┐
│ Case Condition                │ Reference Resolution Status │ Node Ingress Binding      │ Epistemic State & Downstream CAPS Act                  │
├───────────────────────────────┼─────────────────────────────┼───────────────────────────┼────────────────────────────────────────────────────────┤
│ Exactly 1 candidate matches   │ RESOLVED                    │ Bound to canonical        │ EpistemicState determined by proposition provenance:   │
│ filters and top rank          │                             │ entity_id                 │ - USER_STATED  → ASSERTED / HYPOTHETICAL (C ≤ 0.70)    │
│                               │                             │                           │ - INFERRED     → INFERRED (with derivation rule/audit) │
│                               │                             │                           │ - VERIFIED     → FACT (from KnowledgeStore)            │
│                               │                             │                           │ (RESOLVED NEVER automatically promotes to FACT)        │
├───────────────────────────────┼─────────────────────────────┼───────────────────────────┼────────────────────────────────────────────────────────┤
│ ≥ 2 candidates share identical│ AMBIGUOUS                   │ Unbound variable (?X)     │ EpistemicState = AMBIGUOUS.                            │
│ top score tuple               │                             │                           │ Downstream CAPS triggers CommunicativeAct.CLARIFY.     │
├───────────────────────────────┼─────────────────────────────┼───────────────────────────┼────────────────────────────────────────────────────────┤
│ Zero candidates match (cache  │ UNKNOWN / UNRESOLVED        │ Unbound variable (?X)     │ EpistemicState = UNKNOWN.                              │
│ empty or referents evicted)   │                             │                           │ Downstream CAPS triggers CommunicativeAct.INQUIRE.     │
├───────────────────────────────┼─────────────────────────────┼───────────────────────────┼────────────────────────────────────────────────────────┤
│ Referents exist, but all fail │ TYPE_MISMATCH               │ Candidate rejected;       │ EpistemicState = UNKNOWN.                              │
│ concept/animacy/gender check  │                             │ unbound variable (?X)     │ Downstream CAPS triggers CommunicativeAct.INQUIRE.     │
└───────────────────────────────┴─────────────────────────────┴───────────────────────────┴────────────────────────────────────────────────────────┘
```

---

## 9. Determinism Specification

### 9.1 Isolated Cache Determinism Scope
Determinism in this contract applies strictly to the **isolated discourse cache resolution algorithm given an identical frozen snapshot**, NOT to global runtime determinism:

$$\text{Resolve}\big(\text{Cache}_t,\; \text{Query}\big) \equiv \text{Resolve}\big(\text{Cache}_t,\; \text{Query}\big)$$
$$\text{Update}\big(\text{Cache}_t,\; \text{Mentions}_{t+1}\big) \equiv \text{Update}\big(\text{Cache}_t,\; \text{Mentions}_{t+1}\big)$$

1. **Float Stability**: Salience scores rounded to 4–6 decimal places to prevent platform-dependent floating point drift.
2. **No Stochasticity**: Zero temperature, zero probabilistic sampling, zero hidden heuristics.
3. **Canonical Hash Verification**: Bit-exact state hashes verified across executions in benchmark suite ([`test_discourse_retention_contract.py:183–193`](file:///c:/Users/Lunafiah/Desktop/My_project/Lucia/tests/evaluation/phase23_caps/test_discourse_retention_contract.py#L183-L193)).

---

## 10. Memory Boundedness & Complexity

### 10.1 Architectural Property: Bounded Active Referent Set
The architectural contract mandates that the active discourse set MUST have a strictly bounded capacity ($N_{\text{max}}$). It is strictly forbidden from growing linearly with conversation length ($O(T)$).

- **Time Complexity**:
  - Resolution: $O(N_{\text{max}})$ where $N_{\text{max}} \le 16 \implies \le 16\text{ operations} \approx 0.01\text{ ms}$.
  - Turn Update: $O(N_{\text{max}} \log N_{\text{max}}) \implies \le 64\text{ operations} \approx 0.02\text{ ms}$.
- **Space Complexity**:
  - Theoretical upper bound: $O(N_{\text{max}})$ constant working memory.
  - Zero dynamic memory accumulation regardless of dialogue duration ($T \to \infty$).

### 10.2 Empirical Benchmark Observations (Isolated Prototype)
Measured via [`tests/evaluation/phase23_caps/test_discourse_retention_contract.py`](file:///c:/Users/Lunafiah/Desktop/My_project/Lucia/tests/evaluation/phase23_caps/test_discourse_retention_contract.py):
- **Turns Simulated**: 100 consecutive turns with continuous entity injection.
- **Max Observed Cache Size**: 8 items (well below capacity cap of 16).
- **Observed Heap Footprint**: $\le 2\text{ KB}$ heap usage (evaluation observation, not an unalterable production invariant).
- **Execution Overhead**: 3.01 ms total for 100 turns ($\approx 0.03\text{ ms / turn}$).

---

## 11. Ownership & Integration Point

### 11.1 Anti-Ownership Principle: CAPS Does NOT Own Discourse Memory
- **CAPS Responsibility**: CAPS is exclusively the boundary for *Communicative Act & Proposition Selection* (deciding what communicative intent and propositional graph to emit).
- **Discourse Memory Responsibility**: Discourse state must be available at **turn ingress** to parse the user's input before cognition runs. If CAPS owned the cache, discourse memory would only be accessible at cognitive egress, breaking user anaphora resolution.

### 11.2 Integration Location
The `DiscourseContextCache` MUST be owned by the turn lifecycle coordinator:
- **Owner**: [`src/core/orchestrator/cognitive_orchestrator.py`](file:///c:/Users/Lunafiah/Desktop/My_project/Lucia/src/core/orchestrator/cognitive_orchestrator.py) (alongside other per-session turn state objects).
- **Lifecycle Injection**: Instantiated during orchestrator setup, cleared on session reset (`clear_history()`), and passed to the semantic formation layer during ingress and egress.

---

## 12. Parameter Analysis & Status

### 12.1 Distinction: Architectural Property vs. Provisional Parameters
- **Architectural Invariant**: The requirement that discourse memory is a **bounded active referent set** with exponential decay and threshold eviction is an architectural invariant.
- **Provisional Parameters**: The specific values ($N=16$, $\gamma=0.60$, $\theta=0.15$) are **PROVISIONAL CONFIGURATION PARAMETERS**, not ratified invariants.

| Parameter | Proposed Value | Empirical & Theoretical Rationale | Governance Status |
|---|---:|---|---|
| **Max Capacity ($N_{\text{max}}$)** | `16` | Psycholinguistic focus span (Centering Theory; Cowan 2001 $4 \pm 1$ working items). Bounded prototype test over 100 turns stabilized at 8 items. | **PROVISIONAL** (Safe upper bound; needs conversational tuning) |
| **Decay Factor ($\gamma$)** | `0.60` | Half-life of $\approx 1.5$ turns. Unmentioned entity decays: $1.0 \to 0.6 \to 0.36 \to 0.216 \to 0.129$. Retains prominence across 3 turns of dialogue. | **PROVISIONAL** (Justified by prototype; not yet production invariant) |
| **Eviction Threshold ($\theta_{\text{evict}}$)** | `0.15` | Ensures that entities unmentioned for $> 3$ consecutive turns are cleanly evicted, preventing ghost referents. | **PROVISIONAL** (Justified by prototype; not yet production invariant) |

---

## 13. Evidence Matrix

| Evidence ID | Source File / Test Artifact | Symbol / Line Range | Verified Property |
|---|---|---|---|
| **E-D0** | [`data/profile.json`](file:///c:/Users/Lunafiah/Desktop/My_project/Lucia/data/profile.json#L1) | Genesis State | `{"is_onboarded": false}`. Intact bit-exact. Zero activation. |
| **E-D1** | [`src/core/orchestrator/cognitive_orchestrator.py:108–115, 737–741`](file:///c:/Users/Lunafiah/Desktop/My_project/Lucia/src/core/orchestrator/cognitive_orchestrator.py#L108-L115) | `CognitiveOrchestrator._history` | Proves text-only context history in production; zero semantic entity cache. |
| **E-D2** | [`tests/evaluation/evaluation_phase23d/experiment_03_coreference/models/umr_coreference.py`](file:///c:/Users/Lunafiah/Desktop/My_project/Lucia/tests/evaluation/evaluation_phase23d/experiment_03_coreference/models/umr_coreference.py#L8-L170) | `UMRCoreferenceSubstrate` | Proves deterministic resolution algorithm using syntactic roles, animacy, and gender filters. |
| **E-D3** | [`tests/evaluation/phase23d/test_exp03_coreference.py:53–140`](file:///c:/Users/Lunafiah/Desktop/My_project/Lucia/tests/evaluation/phase23d/test_exp03_coreference.py#L53-L140) | Test Suite EXP-03 | Proves CEAF-e F1 $\ge 0.82$, B-cubed F1 $\ge 0.85$, zero-anaphora non-hallucination. |
| **E-D4** | [`tests/evaluation/phase23_caps/test_discourse_retention_contract.py`](file:///c:/Users/Lunafiah/Desktop/My_project/Lucia/tests/evaluation/phase23_caps/test_discourse_retention_contract.py) | Benchmark Runner | Proves $O(1)$ memory bound across 100 turns, exact decay/eviction, failure semantics, isolated determinism. |
| **E-D5** | [`docs/PhaseDocs/Lucia-phase23-Semantic_Substrate/evaluation_artifacts/caps_readiness/discourse_cache_benchmark.json`](file:///c:/Users/Lunafiah/Desktop/My_project/Lucia/docs/PhaseDocs/Lucia-phase23-Semantic_Substrate/evaluation_artifacts/caps_readiness/discourse_cache_benchmark.json) | Raw Benchmark Output | Persisted execution telemetry confirming 3.016 ms latency and 100% test pass. |

---

## 14. Open Questions

1. **Compound Discourse Referents (Plural Anaphora)**:
   - When a turn mentions two individuals (*"Nam and Lan went to school"*), should the cache create an aggregated set entity `ent:nam_lan_group` with `:has_member` links, or retain them purely as individual referents?
   - *Status*: Deferred to post-P23 semantic expansion; current contract handles atomic referents.
2. **Vietnamese Kinship Perspective Inversion**:
   - In Vietnamese conversation, the honorific pronoun *"em"* refers to Lucia when spoken by the User, but refers to the User when spoken by an older sibling.
   - *Resolution*: EXP-03 ([`test_exp03_vietnamese_perspective_no_spurious_merger`](file:///c:/Users/Lunafiah/Desktop/My_project/Lucia/tests/evaluation/phase23d/test_exp03_coreference.py#L97-L119)) demonstrated that indexing referents by `speaker_id` prevents spurious merges.

---

## 15. Architectural Ratification Record

$$\mathbf{DISCOURSE\ REFERENT\ RETENTION\ CONTRACT\ \text{—}\ ARCHITECTURALLY\ RATIFIED}$$

### 15.1 Formal Ratification Ledger
On 2026-10-14, the **Discourse Referent Retention Contract** is formally ratified under Phase 23 Semantic Substrate research governance:

1. **Ownership**: Formally ratified that discourse referent retention belongs strictly to the turn coordination layer ([`src/core/orchestrator/cognitive_orchestrator.py`](file:///c:/Users/Lunafiah/Desktop/My_project/Lucia/src/core/orchestrator/cognitive_orchestrator.py)). CAPS does NOT own discourse memory.
2. **Purpose Boundary**: Formally ratified that the cache exists solely to maintain a bounded active referent set for cross-turn anaphoric resolution. It MUST NOT serve as a transcript store, world model, user model, or long-term episodic memory.
3. **Orthogonality & Invariants**:
   - Reference Resolution Status (`RESOLVED`, `AMBIGUOUS`, `UNKNOWN/UNRESOLVED`, `TYPE_MISMATCH`) is strictly orthogonal to Epistemic State (`FACT`, `INFERRED`, `AMBIGUOUS`, `UNKNOWN`).
   - Explicit Invariants Ratified:
     $$\mathbf{RESOLVED \neq FACT}$$
     $$\mathbf{USER\_STATED\ provenance \neq FACT\ epistemic\ status}$$
4. **Boundedness**:
   - The architectural requirement of a **bounded active referent set** with decay and threshold eviction is formally ratified.
   - Specific configuration values ($N_{\text{max}} = 16$, $\gamma = 0.60$, $\theta_{\text{evict}} = 0.15$) remain **PROVISIONAL CONFIGURATION PARAMETERS** pending multi-turn conversational tuning.
   - Memory observation ($\le 2\text{ KB}$ heap) remains an empirical benchmark observation, NOT an unalterable production invariant.
5. **Determinism Boundary**: Isolated resolver determinism with frozen/fully specified input snapshots and fixed contract version is formally verified and ratified. No claim of global runtime determinism is made.
6. **Failure Semantics**: Fail-closed resolution is ratified: `AMBIGUOUS` is never promoted to certainty; `UNKNOWN` and `TYPE_MISMATCH` fail closed to interrogative acts (`INQUIRE`/`DECLINE`). Resolution failure does not generate epistemic facts.
7. **CAPS Precondition Boundary**: This ratification resolves Research Gate **R3** of the CAPS Implementation Readiness Gate. It constitutes a ratified prerequisite for a future CAPS implementation contract, **NOT authorization for CAPS production implementation**.

### 15.2 Governance Status Summary
- **Discourse Referent Retention Contract**: `[ARCHITECTURALLY RATIFIED]`
- **CAPS Implementation Contract**: `[NOT YET RATIFIED]`
- **CAPS Production Implementation**: `[NOT AUTHORIZED]`
