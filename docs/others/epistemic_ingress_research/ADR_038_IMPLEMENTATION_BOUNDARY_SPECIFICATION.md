# ADR-038 Implementation Boundary Specification

> **Document ID:** DOC-ADR038-IMP-001 (DOC-E3-IMP-001)  
> **Status:** `[ANALYSIS & SPECIFICATION COMPLETE / IMPLEMENTATION CONDITIONALLY READY]`  
> **Governing Decision:** ADR-038 (DOC-ADR-038 / ARCH-038)  
> **Authority Level:** Implementation Boundary Specification (Read-Only Analysis)  
> **Target Subsystems:** `src/core/language/adapter/`, `src/core/cognition/contract/`, `src/core/communication/`  
> **Protected Kernel:** Phase 23-H Reasoning Kernel (`src/core/cognition/kernel/`, commit `3eef803` — strictly frozen)  
> **Target Path:** `docs/others/epistemic_ingress_research/ADR_038_IMPLEMENTATION_BOUNDARY_SPECIFICATION.md`  

---

## 1. Objective

This document derives the authoritative, concrete engineering implementation boundary for **ADR-038 (Grounded Propositional Causal Ingress Contract)**. It translates the verified mathematical and epistemic research findings from E3-R1 through E3-R4 and ADR-038 into an actionable, file-level architectural blueprint for future implementation.

Specifically, this specification defines:
1. The exact boundaries between perimeter language parsing, causal attribution, provenance recording, and logical premise interning.
2. The audited capability of existing repository structures (`ProvenanceRecord`, `DyadicDiscourseState`, `LanguageIngressGate`, `ProjectGraphToTerms`).
3. The precise distinction between ratified architectural contracts, required supporting changes, derived runtime consequences, and unauthorized speculative behaviors.
4. The resolution requirements for structural blockers (F12 proposition identity and antecedent reference stability).

---

## 2. Source Documents & Authoritative Baseline

The implementation boundary is derived directly from the following canonical artifacts:

| Document ID | Canonical File Path | Role in Implementation Derivation |
|---|---|---|
| **DOC-ADR-038** | [`docs/others/epistemic_ingress_research/ADR_038_GROUNDED_PROPOSITIONAL_CAUSAL_INGRESS.md`](file:///c:/Users/Lunafiah/Desktop/My_project/Lucia/docs/others/epistemic_ingress_research/ADR_038_GROUNDED_PROPOSITIONAL_CAUSAL_INGRESS.md) | Governing Architecture Decision Record |
| **DOC-E3-R1** | `docs/others/epistemic_ingress_research/EP_REAS_FORMATION_FEASIBILITY_AUDIT.md` | Baseline feasibility audit & initial contract |
| **DOC-P23H-E3-R2-FALSIFICATION-001** | [`docs/others/epistemic_ingress_research/P23H_E3_R2_EPISTEMIC_INGRESS_FALSIFICATION_REPORT.md`](file:///c:/Users/Lunafiah/Desktop/My_project/Lucia/docs/others/epistemic_ingress_research/P23H_E3_R2_EPISTEMIC_INGRESS_FALSIFICATION_REPORT.md) | Falsification of scalar confidence & 5-field contract |
| **DOC-P23H-E3-R3-BOUNDARY-REVIEW-001** | [`docs/others/epistemic_ingress_research/P23H_E3_R3_CONTRACT_BOUNDARY_REVIEW.md`](file:///c:/Users/Lunafiah/Desktop/My_project/Lucia/docs/others/epistemic_ingress_research/P23H_E3_R3_CONTRACT_BOUNDARY_REVIEW.md) | Elimination of wrong-layer fields & turn-level boolean |
| **DOC-P23H-E3-R4-CAUSAL-BOUNDARY-001** | [`docs/others/epistemic_ingress_research/P23H_E3_R4_F15_CAUSAL_BOUNDARY_RESEARCH.md`](file:///c:/Users/Lunafiah/Desktop/My_project/Lucia/docs/others/epistemic_ingress_research/P23H_E3_R4_F15_CAUSAL_BOUNDARY_RESEARCH.md) | F15 Causal Boundary & Grounded Causal Link |
| **ARCH-030.1** | `docs/PhaseDocs/Lucia-phase23-Semantic_Substrate/` | Phase 23-G Substrate $\to$ Core Numeric Contract |
| **ARCH-031** | `docs/PhaseDocs/Lucia-phase23-Semantic_Substrate/P23-H_FINAL_STATE.md` | Phase 23-H Bounded Reasoning Kernel (Commit `3eef803`) |
| **ADR-035** | [`docs/others/PRODUCTION_REALIZATION_BOUNDARY_ADR/ADR_035_PRODUCTION_REALIZATION_BOUNDARY.md`](file:///c:/Users/Lunafiah/Desktop/My_project/Lucia/docs/others/PRODUCTION_REALIZATION_BOUNDARY_ADR/ADR_035_PRODUCTION_REALIZATION_BOUNDARY.md) | S14 Realization Gate & Output Language Architecture |

---

## 3. Current Architecture vs. Target Architecture

### 3.1 Current Architecture (Observed Repository Reality)

In the current codebase, the cognitive turn operates with a disconnected, ungrounded conversational boundary:

```text
User Utterance (input_text: str)
       │
       ▼
[Stage 1 Ingress] `LanguageIngressGate.admit_and_parse(text, lang)`
       │  • Checks language admission ({en, vi, ja})
       │  • Parses regex sentence patterns into `SemanticGraph`
       │  • Verifies substrate purity (no surface tokens)
       │  • Assigns `EpistemicState.FACT` or `UNKNOWN` heuristically
       │
       ▼
[Stage 8 Knowledge Retrieval]
       │  • String query on `KnowledgeStore` (query_relevant)
       │  • NO inline extraction of user text to KnowledgeStore propositions
       │
       ▼
[Stage 10b CAPS Evaluation]
       │  • Reads `DialogueContextSnapshot` & `DyadicDiscourseState`
       │  • `DyadicDiscourseState` stores coarse turn metadata (previous_assistant_act)
       │  • Evaluates pragmatic stance and communicative intent
       │
       ▼
[Stage 14 Realization Gate]
       │  • SLM generates text under S14 symbolic fidelity gate
       │
       ▼
[Stage 16.4 History Append]
       • `CognitiveOrchestrator._history.append(("user", text))`
       • `CognitiveOrchestrator._history.append(("assistant", text))`
       • Assistant propositions are NEVER parsed into SemanticGraph or interned into TermArena.
```

**Key Architectural Flaw in Current Baseline**:
`ProjectGraphToTerms()` in [`src/core/cognition/contract/projection.py`](file:///c:/Users/Lunafiah/Desktop/My_project/Lucia/src/core/cognition/contract/projection.py#L242) maps `node.epistemic_state` 1:1 directly to `EpistemicStatus`. There is **zero perimeter causal attribution**, **zero echo detection**, and **zero causal provenance linking**.

---

### 3.2 Target Architecture (ADR-038 Realization)

ADR-038 introduces an authoritative epistemic firewall at the perimeter:

```text
User Utterance (input_text: str) + Language Tag
       │
       ▼
[Language Ingress Adapter]
       │  1. Parses utterance into candidate relational clauses.
       │  2. Inspects `DyadicDiscourseState` (previous_assistant_act, expectation).
       │  3. Attributes `CausalLink` <antecedent_term_id, CausalRelation> per proposition.
       │  4. Formulates `IngressCandidateAssertion` (untrusted candidate).
       │
       ▼
[Epistemic Ingress Gate] (Perimeter Firewall)
       │  1. Evaluates candidate against source authority and CausalLink.
       │  2. Enforces Invariant NEG-02 (scalar confidence cannot assert FACT).
       │  3. Intercepts `CONFIRMED_ECHO` → sets output `epistemic_status = UNKNOWN`.
       │  4. Intercepts `CORRECTED_NEGATION` → sets `polarity = False`, tags antecedent.
       │  5. Emits certified `QualifiedLogicalAssertion`.
       │
       ▼
[P23-G Projection & Allocation Layer]
       │  1. Allocates `LogicalTerm` in `TermArena` with certified `epistemic_status`.
       │  2. Populates `ProvenanceRecord.metadata` with (antecedent_term_id, causal_relation_id).
       │  3. ZERO dynamic heap allocations; ZERO string leakage.
       │
       ▼
[P23-H Reasoning Kernel] (Frozen Commit 3eef803)
       • Reads certified `LogicalTerm` arrays.
       • Evaluates backward goals under Strong Kleene K3 logic.
       • Executes JTMS dependency invalidation when premises are retracted.
       • REMTAINS 100% UNAWARE of natural language, turns, or discourse parsing.
```

---

## 4. Contract Classification Audit

Every behavior and structure described in ADR-038 is categorized under strict engineering discipline:

| Item / Behavior | Category | Classification Rationale |
|---|:---:|---|
| **`CausalRelation` IntEnum** (`SPONTANEOUS=1` .. `ELABORATED=5`) | **A. REQUIRED BY ADR** | Directly ratified bounded vocabulary for F15 defense. |
| **`IngressCandidateAssertion` Dataclass** | **A. REQUIRED BY ADR** | Authoritative typed structure for candidate evaluation prior to interning. |
| **Grounded Causal Link** (`antecedent_term_id`, `causal_relation`) | **A. REQUIRED BY ADR** | Minimal 2-element primitive proven sufficient across F15 Attack Matrix. |
| **Perimeter Epistemic Gate Certification** | **A. REQUIRED BY ADR** | Epistemic status is an authoritative gate output verdict, not untrusted caller input. |
| **Invariant NEG-02 Enforcement** | **A. REQUIRED BY ADR** | Permanent architectural prohibition: scalar $c \ge \theta \centernot\implies \text{Assert}(\text{FACT})$. |
| **`ProvenanceRecord.metadata` Integer Packing** | **B. REQUIRED SUPPORTING CHANGE** | Necessary engineering mechanism to store causal links without mutating `ProvenanceRecord` schema. |
| **`DyadicDiscourseState` Seed Referent Extension** | **B. REQUIRED SUPPORTING CHANGE** | Existing discourse state lacks propositional antecedent pointers; requires target tracking. |
| **Assistant Utterance Semantic Registration** | **B. REQUIRED SUPPORTING CHANGE** | `antecedent_term_id` cannot point to an assistant claim unless the claim was interned or indexed. |
| **`CONFIRMED_ECHO` $\implies$ `UNKNOWN` Status** | **A. REQUIRED BY ADR** | Explicitly mandated defense: echo cannot become extensional `FACT`. |
| **`CONFIRMED_ECHO` $\implies$ Emits `InformationSubgoal`** | **C. DERIVED RUNTIME CONSEQUENCE** | Logically follows from K3 Quadrant 1 evaluation in P23-H when goal is `UNKNOWN`. The Ingress Gate does not emit subgoals; P23-H emits subgoals during reasoning. |
| **`CORRECTED_NEGATION` $\implies$ `polarity = False`** | **A. REQUIRED BY ADR** | Explicitly mandated representation of user refutation. |
| **`CORRECTED_NEGATION` $\implies$ Direct `JTMS.retract_premise()` Call** | **D. NOT YET AUTHORIZED** | **Unauthorized architectural coupling**. The Ingress Gate runs at Stage 1, while JTMS lives inside P23-H at Stage 10b/11. The gate must NOT call JTMS directly. It must tag the retraction; orchestration executes retraction. |
| **Cross-Session Causal Link Re-indexing** | **D. NOT YET AUTHORIZED** | Cross-session persistence of ephemeral `TermArena` IDs is unproven; requires F12 resolution. |

---

## 5. Exact Data-Flow Boundary & Component Ownership

The concrete ownership matrix across the pipeline is defined as follows:

```text
Component                     Current Reality              Target Implementation
──────────────────────────────────────────────────────────────────────────────────────────
Language Drivers              Emits SemanticGraph          Emits IngressCandidateAssertion
(src/core/language/adapter/)  (untyped epistemic_state)    (with candidate semantic roles)

DyadicDiscourseState          Coarse turn act/stance       Provides antecedent seed ID and
(src/core/communication/)     (previous_assistant_act)     expected speech-act polarity

LanguageIngressGate           Language code filter only    Authoritative Epistemic Gate:
(src/core/language/adapter/)  ({en, vi, ja} check)         validates candidate, assigns
                                                           certified epistemic_status & CausalLink

ProjectGraphToTerms           Direct 1:1 enum cast         Translates certified candidate into
(src/core/cognition/contract) (node.epistemic_state)       numeric LogicalTerm & ProvenanceRecord

TermArena                     Preallocated buffer          Stores certified LogicalTerm
(src/core/cognition/contract) (ephemeral array)            (unchanged structure)

CognitiveOrchestrator         Orchestrates S1..S16         Coordinates retraction dispatch;
(src/core/orchestrator/)      Appends string history       caches assistant seed proposition IDs

ReasoningKernel (P23-H)       Frozen Horn chainer          Reads certified terms; K3 reasoning;
(src/core/cognition/kernel/)  (Commit 3eef803)             JTMS retraction (100% UNCHANGED)
```

---

## 6. Audit of `ProvenanceRecord`

### 6.1 Inspecting Existing Code
`ProvenanceRecord` in [`src/core/cognition/contract/provenance.py`](file:///c:/Users/Lunafiah/Desktop/My_project/Lucia/src/core/cognition/contract/provenance.py#L24) is defined as:
```python
@dataclass(frozen=True)
class ProvenanceRecord:
    rule_id: int = 0
    supporting_premise_ids: Tuple[int, ...] = ()
    session_id: int = 0
    turn_id: int = 0
    timestamp: float = 0.0
    confidence: float = 1.0
    metadata: Dict[int, int] = field(default_factory=dict)
```

### 6.2 Structural Audit Findings
1. **Allocation & Zero Heap Discipline**:
   `metadata: Dict[int, int]` is already an existing field on `ProvenanceRecord`. It maps 64-bit integer keys to 64-bit integer values.
2. **Standard Reserved Keys**:
   We can encode the Grounded Causal Link using two standardized integer keys in `metadata` without altering the class signature or adding new fields:
   ```python
   PROV_KEY_CAUSAL_RELATION = 1001   # Values: 1..5 (CausalRelation)
   PROV_KEY_ANTECEDENT_TERM = 1002   # Value: antecedent_term_id: int
   ```
3. **Serialization & Backward Compatibility**:
   `to_dict()` and `from_dict()` serialize `metadata` as `{int(k): int(v)}`. Existing consumers that do not read `metadata` are 100% unaffected. Round-trip serialization is preserved.
4. **Conclusion**:
   **No structural changes to `ProvenanceRecord` class definition are required.** The causal link can be carried natively inside `metadata` using reserved integer keys.

---

## 7. Audit of `DyadicDiscourseState`

### 7.1 Existing State Structure
[`src/core/communication/caps.py`](file:///c:/Users/Lunafiah/Desktop/My_project/Lucia/src/core/communication/caps.py#L115) defines:
```python
@dataclass(frozen=True)
class DyadicDiscourseState:
    dialogue_phase: DialoguePhase = DialoguePhase.OPENING_ENCOUNTER
    floor_status: FloorStatus = FloorStatus.MUTUAL_OPEN
    previous_assistant_act: Optional[str] = None
    previous_user_stance: Optional[str] = None
    unresolved_expectation: Optional[str] = None
```

### 7.2 Conceptual Walkthrough Across Seven Scenarios

We test whether this state is sufficient to synthesize the five causal relations:

| Scenario | Prior Assistant Context | User Utterance | Current State Sufficiency | Missing Information |
|---|---|---|:---:|---|
| **1. Spontaneous Assertion** | `previous_assistant_act = "SHARE"`, `unresolved_expectation = None` | *"I bought a keyboard."* | **SUFFICIENT** | None. `unresolved_expectation is None` $\implies$ `SPONTANEOUS`. |
| **2. Answer to Open Question** | `previous_assistant_act = "INQUIRE"`, `unresolved = "USER_RESPONSE_EXPECTED"` | *"Hanoi."* | **PARTIALLY SUFFICIENT** | Current state knows an inquiry occurred, but does **not** know whether the inquiry was open or closed! |
| **3. Confirmation of Seed** | `previous_assistant_act = "INQUIRE"`, `unresolved = "USER_RESPONSE_EXPECTED"` | *"Yeah."* | **INSUFFICIENT** | Cannot distinguish open vs closed question; does **not** store the assistant's seeded `term_id`. |
| **4. Correction / Refutation** | `previous_assistant_act = "INQUIRE"`, `unresolved = "USER_RESPONSE_EXPECTED"` | *"No, I hate it."* | **INSUFFICIENT** | User polarity is negative, but state lacks the target `term_id` to be retracted. |
| **5. Elaboration on Topic** | `previous_assistant_act = "INQUIRE"` | *"Yes, and I listen to Miles."* | **INSUFFICIENT** | Clause 1 is echo; Clause 2 is novel. Turn-level state cannot separate them. |
| **6. Mixed-Content Turn** | Prior act was closed inquiry | *"Yeah, and I need milk."* | **INSUFFICIENT** | Same granularity collapse as Scenario 5. |
| **7. Long-Distance Echo** | Turn $t-9$ was inquiry | Turn $t$: *"Earlier you mentioned X... I agree."* | **COMPLETELY INSUFFICIENT** | State only tracks Turn $t-1$ (`previous_assistant_act`). Immediate-turn history is blind to Turn $t-9$. |

### 7.3 Minimal Supporting State Required
To support Scenarios 1–4 without a full discourse parser, `DyadicDiscourseState` requires **two additional fields**:
```python
active_assistant_seed_term_id: int = 0
inquiry_type: Optional[str] = None  # "OPEN" vs "CLOSED"
```
For Scenario 7 (Long-distance echo), the Language Ingress Adapter must perform a lookup in a lightweight recent turn cache (`DiscourseContextCache`).

---

## 8. Proposition-Level Requirement & Granularity

### 8.1 Why Turn-Level and Clause-Level Fail
- **Turn-Level Fails**: In mixed turns (*"Yeah, and by the way I need to buy milk"*), the turn contains both an assistant echo ($P_1$) and an independent user assertion ($P_2$). A turn-level attribute forces either $P_1$ or $P_2$ into the wrong epistemic state.
- **Clause-Level is Syntactic**: A natural language clause may contain multiple relational assertions (e.g., relative clauses, conjunctions).

### 8.2 The Proposition-Level Invariant
Causal attribution must attach strictly to the **individual logical proposition (`IngressCandidateAssertion`)**:
- Each admitted `LogicalTerm` represents exactly one head predicate and its arguments.
- In `TermArena`, each `LogicalTerm` has its own `term_id` and its own `provenance: Optional[ProvenanceRecord]`.
- Thus, $P_1$ (`is_tired(User)`) receives `causal_relation = CONFIRMED_ECHO` and `epistemic_status = UNKNOWN`.
- $P_2$ (`need_buy(User, Milk)`) receives `causal_relation = SPONTANEOUS` and `epistemic_status = FACT`.
- **Conclusion**: Proposition-level granularity is natively supported by `LogicalTerm` and `ProvenanceRecord`.

---

## 9. Epistemic Status Ownership & Certification Transition

### 9.1 The Self-Assertion Vulnerability
If an upstream component passes `epistemic_status: EpistemicStatus` in its candidate, an untrusted or compromised language parser can self-declare:
$$\text{candidate} = \text{IngressCandidateAssertion}(\dots, \text{epistemic\_status}=\text{FACT})$$
This bypasses all epistemic safeguards and allows hallucinations to enter as ground truth.

### 9.2 The Strict Candidate $\to$ Certified Transition
`IngressCandidateAssertion` **MUST NOT** include `epistemic_status`. 

The transition flow is strictly certified:
```text
1. Language Adapter emits:
   IngressCandidateAssertion(
       predicate_id=...,
       arg0_id=...,
       polarity=...,
       source_class=USER_DISCOURSE,
       causal_relation=CONFIRMED_ECHO,
       antecedent_term_id=142
   )

2. Language Ingress Gate evaluates candidate:
   - Reads source_class == USER_DISCOURSE
   - Reads causal_relation == CONFIRMED_ECHO
   - Applies Gate Rule: Echoes MUST be downgraded
   - Certified Output:
       epistemic_status = EpistemicStatus.UNKNOWN
       polarity = True

3. ProjectGraphToTerms interns certified term:
   arena.allocate_term(
       predicate_id=...,
       epistemic_status=EpistemicStatus.UNKNOWN,  <-- Gate Certified
       provenance=ProvenanceRecord(metadata={1001: 3, 1002: 142})
   )
```

---

## 10. NEG-02 Enforcement Point

### 10.1 The Invariant
$$\forall c \in [0.0, 1.0], \quad (c \ge \theta) \centernot\implies \text{Assert}(\text{FACT})$$

### 10.2 Exact Implementation Enforcement Point
Enforcement occurs inside `LanguageIngressGate.certify_candidate()`:
- If `source_class == PERCEPTUAL` or `confidence < 1.0`:
  - Output `epistemic_status` is forced to `EpistemicStatus.UNKNOWN` (or modal scope container).
  - The numeric confidence value is stored in `ProvenanceRecord.confidence` for heuristic ordering or ranking, but **never** drives the Kleene logic value.
  - The gate raises `EpistemicEscalationError` if an upstream driver attempts to submit an ungrounded perceptual triple with `source_class == DERIVED` without a valid rule DAG.

---

## 11. F12 Identity Audit: Ephemeral vs. Persistent `antecedent_term_id`

### 11.1 The F12 Vulnerability
In the current repository:
1. `TermArena` is an in-memory array preallocated to 4096 terms. `term_id` is an integer index ($1 \le \text{term\_id} \le 4096$).
2. When Lucia restarts or a new interaction session begins, `TermArena` is reset. Term indices from the previous run are lost or overwritten.
3. `KnowledgeStore` uses string IDs (`prop.id = "prop_123"` or random UUIDs `derived:a1b2c3d4`).
4. `SymbolTable` maps node strings to integer IDs dynamically in memory.

### 11.2 Can `antecedent_term_id` Safely Reference a Term?
- **Within a Live Conversational Session**: **YES**. Within a running process session, `term_id` in `TermArena` is monotonically increasing and immutable once allocated. An assistant term generated in Turn $t-1$ retains its `term_id` for the duration of the session.
- **Across Sessions / After Persistence Reload**: **NO**. If the companion process restarts, ephemeral `term_id`s in `TermArena` do not persist unless a persistent symbol mapping is serialized.
- **Implementation Requirement for Phase 23-H E3**:
  For immediate in-session dialogue (Turns $1 \dots N$), `antecedent_term_id: int` is 100% sound.
  Cross-session causal links are marked **CONDITIONALLY DEFERRED** pending an authoritative persistent symbol registry.

---

## 12. Minimal F15 Attack Matrix for Implementation

The implementation must pass the following 7 canonical operational test cases:

| # | Attack Scenario | Input Discourse State | Incoming Candidate Assertion | Certified Output `epistemic_status` | Certified Polarity | JTMS / Provenance Action | Current Runtime Support |
|:---:|---|---|---|:---:|:---:|---|:---:|
| **1** | **Spontaneous Assertion** | `unresolved = None` | `source = USER`, `causal = SPONTANEOUS` | `FACT` | `True` | Direct root premise interning | **SUPPORTED** |
| **2** | **Answer to Open Question** | `inquiry = OPEN` | `source = USER`, `causal = SUPPLIED_ANSWER` | `FACT` | `True` | Direct root premise interning | **SUPPORTED** (needs inquiry flag) |
| **3** | **Assistant Seed Confirmation** | `inquiry = CLOSED`, `seed = 105` | `source = USER`, `causal = CONFIRMED_ECHO`, `ant = 105` | `UNKNOWN` | `True` | Suppress `FACT`; stores `ant=105` in prov | **SUPPORTED** (gate downgrade) |
| **4** | **Rejection / Correction** | `inquiry = CLOSED`, `seed = 105` | `source = USER`, `causal = CORRECTED_NEGATION`, `ant = 105` | `FACT` | `False` | Orchestrator invokes `JTMS.retract_premise(105)` | **CONDITIONALLY READY** |
| **5** | **Elaboration on Seed** | `inquiry = CLOSED`, `seed = 105` | $P_1$: `CONFIRMED_ECHO`, $P_2$: `ELABORATED` | $P_1$: `UNKNOWN`, $P_2$: `FACT` | $P_1$: `True`, $P_2$: `True` | Independent per-term provenance | **CONDITIONALLY READY** |
| **6** | **Mixed Turn** | User speaks 2 clauses | $P_1$: Echo, $P_2$: Novel topic | $P_1$: `UNKNOWN`, $P_2$: `FACT` | Both `True` | Independent per-term provenance | **CONDITIONALLY READY** |
| **7** | **Long-Distance Echo** | Turn $t-9$ seed cached | `causal = CONFIRMED_ECHO`, `ant = seed_t9` | `UNKNOWN` | `True` | Lookup in `DiscourseContextCache` | **REQUIRES CACHE EXTENSION** |

---

## 13. File-Level Change Map

```text
========================================================================================
1. MUST CHANGE (Core ADR-038 Realization)
========================================================================================

File: `src/core/language/adapter/contracts.py`
  Current Responsibility: Base contracts for language adapters (ParseResult, RealizeResult).
  Required Change: Add `CausalRelation` IntEnum and `IngressCandidateAssertion` dataclass.
  Why Required: Authoritative typed contract for epistemic candidate propositions.
  Risk: Low (additive types only).

File: `src/core/language/adapter/gate.py`
  Current Responsibility: Language perimeter admission ({en, vi, ja}) and substrate purity.
  Required Change: Add `certify_candidate_assertion()` method enforcing non-escalation and NEG-02.
  Why Required: Implements the authoritative epistemic qualification boundary.
  Risk: Medium (must guarantee zero string leakage and fail-closed safety).

File: `src/core/cognition/contract/provenance.py`
  Current Responsibility: Numeric provenance for Cognitive Core terms.
  Required Change: Define reserved metadata keys (`PROV_KEY_CAUSAL_RELATION = 1001`, `PROV_KEY_ANTECEDENT_TERM = 1002`).
  Why Required: Carries causal link in `ProvenanceRecord.metadata` with 0 heap overhead.
  Risk: Very Low (zero schema change; uses existing metadata field).

========================================================================================
2. SHOULD CHANGE (Supporting Orchestration & Discourse Context)
========================================================================================

File: `src/core/communication/caps.py`
  Current Responsibility: Communicative Act Planning System and DyadicDiscourseState.
  Required Change: Add `active_assistant_seed_term_id: int = 0` and `inquiry_type: Optional[str] = None` to `DyadicDiscourseState`.
  Why Required: Provides Ingress Gate with the causal antecedent and question type.
  Risk: Low.

File: `src/core/orchestrator/cognitive_orchestrator.py`
  Current Responsibility: 16-stage cognitive loop orchestration.
  Required Change: Pass `DyadicDiscourseState` to Ingress Gate at Stage S1; handle retraction events at Stage S10b.
  Why Required: Connects conversational discourse state to perimeter ingress evaluation.
  Risk: Medium (orchestration timing and lock discipline must be preserved).

========================================================================================
3. MUST NOT CHANGE (Protected Architecture & Frozen Boundaries)
========================================================================================

Subsystem: `src/core/cognition/kernel/` (P23-H Reasoning Kernel)
  Files: `engine.py`, `jtms.py`, `conflict.py`, `rules.py`, `subgoals.py`
  Status: STRICTLY FROZEN at commit `3eef803`.
  Reason: P23-H is a bounded, non-conversational deductive logic kernel. It must remain 100% isolated.

Subsystem: `src/core/cognition/contract/arena.py` & `terms.py`
  Status: UNCHANGED.
  Reason: `LogicalTerm` and `TermArena` already support numeric `epistemic_status`, `polarity`, and `provenance`.

Subsystem: `data/profile.json` & Identity Authority (`src/core/identity/`)
  Status: STRICTLY FROZEN (`{"is_onboarded": false}`).
  Reason: Genesis First Activation gate invariants.
```

---

## 14. Protected Components & Invariant Ledger

During future implementation, the following architectural invariants are absolute:

1. **Kernel Immutability**: No code in `src/core/cognition/kernel/` may be edited, patched, or refactored.
2. **Subsystem Discipline**: P23-I remains permanently closed. No new standalone background daemon or conversational subsystem may be created.
3. **Substrate Purity**: Zero natural language strings may cross from `LanguageIngressGate` into `TermArena`.
4. **Zero GPU VRAM & 20W Budget**: Ingress evaluation and causal attribution must execute strictly on CPU in $<0.5\text{ ms}$ with zero dynamic memory allocation in the steady-state loop.
5. **Genesis Gate Protection**: `data/profile.json` must remain untouched.

---

## 15. Future Test Matrix Specification

The future implementation must be validated against five comprehensive test suites:

### 15.1 Contract Tests (`tests/unit/test_p23h_e3_contracts.py`)
- `test_causal_relation_enum_values()`: Verifies exact integer values 1..5.
- `test_ingress_candidate_assertion_immutability()`: Verifies frozen dataclass semantics.
- `test_provenance_metadata_roundtrip()`: Verifies packing and extraction of causal link in `ProvenanceRecord.metadata`.

### 15.2 Attribution & Ingress Gate Tests (`tests/unit/test_p23h_e3_ingress_gate.py`)
- `test_spontaneous_user_assertion_certified_as_fact()`: Validates Case 1.
- `test_open_question_answer_certified_as_fact()`: Validates Case 2 (Open-Question fix).
- `test_confirmed_echo_downgraded_to_unknown()`: Validates Case 3 (F15 defense).
- `test_corrected_negation_asserts_negative_polarity()`: Validates Case 4 (Correction fix).
- `test_mixed_turn_independent_proposition_qualification()`: Validates Case 5 & 6.
- `test_untrusted_epistemic_status_injection_rejected()`: Verifies self-assertion firewall.

### 15.3 Epistemic Safety & Invariant Tests (`tests/property/test_p23h_e3_epistemic_invariants.py`)
- `test_neg02_scalar_confidence_never_promotes_to_fact()`: Property test asserting $\forall c \in [0.0, 1.0], \; \text{status} \ne \text{FACT}$.
- `test_non_escalation_lattice()`: Verifies output status ontological commitment is always $\le$ candidate source authority.

### 15.4 Provenance & Traceability Tests (`tests/integration/test_p23h_e3_provenance_trace.py`)
- `test_antecedent_traceability_in_term_arena()`: Verifies `antecedent_term_id` points to the correct antecedent.
- `test_no_dangling_causal_pointers()`: Verifies gate rejects or clears invalid antecedent IDs.

### 15.5 Regression & Kernel Integrity Tests (`tests/regression/test_p23h_kernel_regression.py`)
- `test_p23h_kernel_hash_unchanged()`: Verifies SHA-256 checksums of `src/core/cognition/kernel/` match commit `3eef803`.
- `test_k3_quadrant_evaluations_unaltered()`: Verifies 4-quadrant Kleene evaluations remain bit-exact.

---

## 16. Performance & Resource Boundary

| Metric | Target Specification | Enforcement Mechanism |
|---|---|---|
| **CPU Execution Time** | $<0.2\text{ ms}$ per candidate assertion | Simple integer dictionary lookup & enum comparisons |
| **GPU VRAM Overhead** | **0.0 MB** | Pure CPU Python logic; zero model invocation |
| **Dynamic Heap Allocation** | **0 net bytes in steady state** | Operates on preallocated `TermArena` numeric slots |
| **Discourse Memory Window** | Maximum 10 turns in memory | Bounded `DiscourseContextCache` ring buffer |

---

## 17. Explicit Open Decisions

Before implementation can be declared fully ready to merge, the following three decisions must be resolved:

### Decision 1: Assistant Utterance Semantic Indexing
- *Problem*: To set `antecedent_term_id = asst_term_id`, the assistant's previous utterance must have produced interned `LogicalTerm` IDs in `TermArena`. Currently, the assistant's output is generated by the SLM as raw natural language strings and appended to `_history`.
- *Required Resolution*: Establish a lightweight reverse-parsing pass or semantic intent registration where assistant communicative intents are interned into `TermArena` as candidate terms prior to speech realization.

### Decision 2: JTMS Retraction Call-Site Ownership
- *Problem*: ADR-038 states that `CORRECTED_NEGATION` triggers premise retraction. However, `LanguageIngressGate` (Stage S1) does not and should not have direct access to `JTMS` (Stage S10b).
- *Required Resolution*: Ratify whether `LanguageIngressGate` emits a `RetractionDirective(antecedent_term_id)` event to be processed by `CognitiveOrchestrator` at Stage S10b, or whether P23-H resolves retraction during conflict evaluation.

### Decision 3: Cross-Session F12 Identity Persistence
- *Problem*: `TermArena` term IDs are ephemeral integers ($1 \dots 4096$).
- *Required Resolution*: Explicitly scope Phase 23-H E3 implementation to **in-session conversational causal attribution**, declaring cross-session causal antecedent resolution deferred to a future persistent identity milestone.

---

## 18. Implementation Readiness Verdict

### Verdict: **CONDITIONALLY READY — EXPLICIT DECISIONS REMAIN**

**Verdict Rationale**:
1. The architectural contract (`CausalRelation`, `IngressCandidateAssertion`, `Grounded Causal Link`) is 100% specified and mathematically sound.
2. The storage mechanism (`ProvenanceRecord.metadata`) is verified and requires zero schema changes.
3. The P23-H reasoning kernel is strictly protected and remains frozen at commit `3eef803`.
4. However, implementation cannot proceed blindly because **Decision 1 (Assistant Utterance Semantic Indexing)** and **Decision 2 (Retraction Call-Site Ownership)** require explicit orchestration alignment to prevent architectural layer pollution.

---

## 19. Governance & Final Statement

This document constitutes the formal implementation boundary specification for ADR-038. 

**Zero production code has been modified in this task.**  
Phase 23-H remains frozen at commit `3eef803`.  
Genesis activation state remains strictly locked (`data/profile.json == {"is_onboarded": false}`).
