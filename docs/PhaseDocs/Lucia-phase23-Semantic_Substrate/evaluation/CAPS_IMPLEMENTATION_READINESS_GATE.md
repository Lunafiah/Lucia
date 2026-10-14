# CAPS Implementation Readiness / Research Gate Report (Phase 23)

> **Document Type**: Research Evaluation & Implementation Readiness Gate Report  
> **Status**: COMPLETED / ARCHITECTURAL AUDIT RATIFIED  
> **Target Subsystem**: Communicative Act & Proposition Selection (CAPS Boundary)  
> **Phase**: Phase 23 — Semantic Substrate & Non-Generative Communication  
> **Date**: 2026-10-14  
> **Author**: Antigravity (Lucia Architectural Copilot)  
> **Execution Mode**: Forensic Read-Only Audit & Isolated Research Evaluation (Zero Production Changes)  

---

## 1. Scope & Governance

### 1.1 Objective
This research report executes the formal **CAPS Implementation Readiness / Research Gate** to evaluate whether the Communicative Act & Proposition Selection (CAPS) boundary contract—initially architecturally ratified in [`docs/PhaseDocs/Lucia-phase23-Semantic_Substrate/P23_CAPS_BOUNDARY_CONTRACT_DESIGN.md`](file:///c:/Users/Lunafiah/Desktop/My_project/Lucia/docs/PhaseDocs/Lucia-phase23-Semantic_Substrate/P23_CAPS_BOUNDARY_CONTRACT_DESIGN.md)—has accumulated sufficient empirical and architectural evidence to advance from:

$$\mathbf{ARCHITECTURE\ APPROVED\ /\ IMPLEMENTATION\ GATED} \longrightarrow \mathbf{IMPLEMENTATION\ CONTRACT\ READY}$$

or whether it remains:

$$\mathbf{IMPLEMENTATION\ STILL\ GATED}$$

### 1.2 Strict Governance Adherence
In accordance with [`AGENTS.md`](file:///c:/Users/Lunafiah/Desktop/My_project/Lucia/AGENTS.md) and project invariants:
- **Zero Production Mutations**: No modifications made to `src/core/**`, `electron/**`, or `data/**`.
- **Genesis Lock Invariant**: Verified bit-exact preservation of [`data/profile.json`](file:///c:/Users/Lunafiah/Desktop/My_project/Lucia/data/profile.json) (`{"is_onboarded": false}`). No Genesis onboarding or activation permitted.
- **Contract Integrity**: [`P23_CAPS_BOUNDARY_CONTRACT_DESIGN.md`](file:///c:/Users/Lunafiah/Desktop/My_project/Lucia/docs/PhaseDocs/Lucia-phase23-Semantic_Substrate/P23_CAPS_BOUNDARY_CONTRACT_DESIGN.md) is not modified; previously ratified boundary decisions are preserved.
- **No Monolithic Subsystem**: CAPS remains a functional boundary contract; no `CAPSManager` or monolithic class is introduced.
- **Anti-LLM Guard**: All evaluations and isolated prototypes are strictly deterministic, symbolic, and rule/evidence-grounded with **zero LLM/SLM dependency**.

---

## 2. Current Architectural State

### 2.1 Baseline Summary
- **Phase Status**: Phases 21 through 24 are completed/closed baselines. Phase 23 semantic substrate kernel (`P23-C..H`) is frozen in [`docs/PhaseDocs/Lucia-phase23-Semantic_Substrate/P23-H_FINAL_STATE.md`](file:///c:/Users/Lunafiah/Desktop/My_project/Lucia/docs/PhaseDocs/Lucia-phase23-Semantic_Substrate/P23-H_FINAL_STATE.md).
- **CAPS Boundary**: Architecturally ratified as a decoupled functional boundary separating cognitive goal formation, proposition selection, and downstream surface realization.
- **Production Reality**: The active runtime pipeline ([`src/core/orchestrator/cognitive_orchestrator.py`](file:///c:/Users/Lunafiah/Desktop/My_project/Lucia/src/core/orchestrator/cognitive_orchestrator.py#L412-L435)) continues to generate responses via the local SLM (`LLMBackend.generate()`). CAPS has **not** been implemented in production.
- **Implementation Status**: `IMPLEMENTATION GATED` pending verification of the four core research gates ($R_1, R_2, R_3, R_4$).

---

## 3. Detailed Research Gate Findings

### 3.1 R1 — InformationSubgoal → Inquire Compiler

#### 3.1.1 Production Code Forensic Audit
- **File**: [`src/core/cognition/kernel/engine.py`](file:///c:/Users/Lunafiah/Desktop/My_project/Lucia/src/core/cognition/kernel/engine.py#L75-L102)
- **Symbol**: `InformationSubgoal`
- **Fields Present**:
  ```python
  @dataclass
  class InformationSubgoal:
      target_predicate_id: int
      arg0_id: int = 0
      arg1_id: int = 0
      arg2_id: int = 0
      polarity: bool = True
      scope_id: int = 1
      rule_id: int = 0
      reason_code: int = 0
  ```
- **Related Inference Subgoals**: [`src/core/cognition/contract/inference.py`](file:///c:/Users/Lunafiah/Desktop/My_project/Lucia/src/core/cognition/contract/inference.py#L59-L77) defines `DisambiguationSubgoal` carrying `ambiguous_term_ids`, `candidate_concept_ids`, and `context_scope_id`.

#### 3.1.2 Analysis & Compilation Mechanics
1. **Semantic Sufficiency**: `InformationSubgoal` carries the target relation (`target_predicate_id`), known arguments (`arg0_id`, etc.), and specifies the missing argument by setting the corresponding slot to `0` (unbound/variable).
2. **Determinism**: The mapping from `InformationSubgoal` to `CommunicativeAct.INQUIRE` is strictly deterministic. The unbound slot compiles into an open interrogative variable node (`?X`) in a `SemanticGraph` with role edge `:ARG1` (or `:ARG0`), while the predicate binds the relational edge.
3. **Ambiguity Handling**: When `reason_code == INFO_REASON_AMBIGUOUS_REFERENT` (or when a `DisambiguationSubgoal` is active), the compiler deterministically maps to `CommunicativeAct.CLARIFY` instead of `INQUIRE`.
4. **Schema Requirements**: Positional arguments (`arg0_id`, `arg1_id`, `arg2_id`) currently rely on implicit role conventions (`:ARG0`, `:ARG1`, `:ARG2`). For a production implementation contract, the relation ontology schema should formally specify role labels for each argument position.

#### 3.1.3 Isolated Prototype Telemetry
- **Test Harness**: [`tests/evaluation/phase23_caps/run_caps_readiness_benchmark.py`](file:///c:/Users/Lunafiah/Desktop/My_project/Lucia/tests/evaluation/phase23_caps/run_caps_readiness_benchmark.py#L65-L135)
- **Execution Result**:
  - Missing premise subgoal $\rightarrow$ Emitted `CommunicativeAct.INQUIRE`, 2 nodes (`ent:user`, `?X`), 1 edge (`c:CANINE`).
  - Ambiguous referent subgoal $\rightarrow$ Emitted `CommunicativeAct.CLARIFY`.
- **Verdict**: **PASS (Architecturally feasible & prototype verified; production role convention formalization needed)**
- **Blocking Status**: **NO**

---

### 3.2 R2 — Internal Goal → Grounded Outgoing SemanticGraph

#### 3.2.1 Architectural Taxonomy of Proposition Operations
To avoid confounding retrieval with generation, the investigation establishes clear functional distinctions:
1. **Graph Retrieval**: Querying verified epistemic propositions from [`src/core/knowledge/store.py`](file:///c:/Users/Lunafiah/Desktop/My_project/Lucia/src/core/knowledge/store.py#L68-L120) matching predicate and argument filters.
2. **Graph Selection**: Filtering and ranking retrieved propositions according to communicative utility and affective relevance.
3. **Graph Binding**: Instantiating selected proposition triples into typed `SemanticNode` and `SemanticEdge` structures with explicit provenance metadata.
4. **Graph Composition**: Deriving novel composite proposition graphs by joining existing relations via forward/backward deductive chaining in [`ReasoningKernel`](file:///c:/Users/Lunafiah/Desktop/My_project/Lucia/src/core/cognition/kernel/engine.py#L125-L250).

> [!CAUTION]
> **Anti-Creativity Invariant**: Bounded proposition selection and deductive relation binding are fully demonstrated without LLM. However, **unconstrained open-vocabulary novel proposition generation without ontological grounding is NOT demonstrated and MUST NOT be claimed as "autonomous creativity."**

#### 3.2.2 Grounding Invariant & Epistemic Preservation
- **Assertion Refusal**: An outgoing `ASSERT` or `ANSWER` communicative act **MUST NOT** be emitted unless supported by admissible grounding (`confidence >= threshold` and provenance in `[VERIFIED, INFERRED, USER_STATED]`).
- **Fail-Closed Fallback**: If an internal goal cannot be grounded in existing knowledge or deductive inference, the compiler strictly refuses assertion, falling closed to `CommunicativeAct.INQUIRE` or `CommunicativeAct.DECLINE`.
- **Epistemic Preservation**: `UNKNOWN` and `AMBIGUOUS` epistemic states are preserved bit-exact and never silently promoted to certainty.

#### 3.2.3 Isolated Prototype Telemetry
- **Test Harness**: [`tests/evaluation/phase23_caps/run_caps_readiness_benchmark.py`](file:///c:/Users/Lunafiah/Desktop/My_project/Lucia/tests/evaluation/phase23_caps/run_caps_readiness_benchmark.py#L137-L215)
- **Execution Result**:
  - Grounded goal (`ent:user`, `c:PREFERS`) $\rightarrow$ Emitted `CommunicativeAct.ANSWER`, 3 nodes, Grounded: `True`, Confidence: `1.0`.
  - Ungrounded goal (`ent:user`, `c:SECRET`) $\rightarrow$ Refused assertion: `True`, Fallback Act: `CommunicativeAct.INQUIRE`.
- **Verdict**: **PARTIAL (PASS for bounded proposition selection and grounding enforcement; open-ended creative generation is unproven and bounded)**
- **Blocking Status**: **NO (Bounded selection satisfies deterministic realization requirements)**

---

### 3.3 R3 — Turn-Level Discourse Entity Retention

#### 3.3.1 Production Forensic Audit
- **File**: [`src/core/orchestrator/cognitive_orchestrator.py`](file:///c:/Users/Lunafiah/Desktop/My_project/Lucia/src/core/orchestrator/cognitive_orchestrator.py#L108-L115)
- **Symbol**: `CognitiveOrchestrator._history`
- **Code Inspection**:
  ```python
  # History is maintained strictly as raw text tuples:
  self._history: List[Tuple[str, str]] = []
  ```
- **Findings**:
  1. The production runtime maintains conversational history **strictly as raw text strings** `(user_text, assistant_text)`.
  2. There is **ZERO semantic entity tracking or discourse referent retention** across conversational turns in production.
  3. In [`src/core/cognition/contract/projection.py`](file:///c:/Users/Lunafiah/Desktop/My_project/Lucia/src/core/cognition/contract/projection.py#L45-L75), `SymbolTable` and `TermArena` are created per-turn or tied to local ephemeral scopes without cross-turn salience decay.
  4. If Turn $N$ introduces `Luna mentioned X`, and Turn $N+1$ asks `"What about that?"`, the current semantic pipeline has no mechanism to resolve `"that"` to entity $X$ without an external LLM resolving anaphora in raw text.

#### 3.3.2 Proposed Minimal Bounded Contract: `DiscourseContextCache`
To enable multi-turn semantic realization without monolithic state bloat, a minimal contract must be ratified:
- **Capacity**: Bounded fixed capacity $N_{\text{max}} = 16$ active referents.
- **Referent Schema**:
  ```python
  @dataclass
  class DiscourseReferent:
      entity_id: str
      concept_id: str
      salience_score: float  # [0.0, 1.0]
      turn_introduced: int
      last_referenced_turn: int
  ```
- **Decay & Eviction**:
  - Exponential decay per turn: $\text{salience}_{t+1} = \text{salience}_t \times \gamma$ ($\gamma = 0.60$).
  - Eviction threshold: referents with $\text{salience} < 0.15$ or beyond capacity $N_{\text{max}}$ are pruned.
- **Prototype Telemetry**: [`tests/evaluation/phase23_caps/run_caps_readiness_benchmark.py`](file:///c:/Users/Lunafiah/Desktop/My_project/Lucia/tests/evaluation/phase23_caps/run_caps_readiness_benchmark.py#L217-L270) verified that Turn 1 and Turn 2 entities were successfully retained, while inactive Turn 1 entities decayed below 0.15 and were cleanly evicted by Turn 3.
- **Verdict**: **PARTIAL (Prototype verified; Production Implementation is COMPLETELY ABSENT)**
- **Blocking Status**: **YES (CRITICAL BLOCKING GAP: Multi-turn communicative grounding cannot function without an active discourse referent contract)**

---

### 3.4 R4 — User Assertion Conflict / Provenance Policy

#### 3.4.1 Production Code Forensic Audit
- **Files**:
  - [`src/core/knowledge/store.py`](file:///c:/Users/Lunafiah/Desktop/My_project/Lucia/src/core/knowledge/store.py#L21-L45) (`ProvenanceType.USER_STATED`)
  - [`src/core/knowledge/fortification.py`](file:///c:/Users/Lunafiah/Desktop/My_project/Lucia/src/core/knowledge/fortification.py#L34-L45) (`EpistemicState`)
  - [`src/core/cognition/kernel/conflict.py`](file:///c:/Users/Lunafiah/Desktop/My_project/Lucia/src/core/cognition/kernel/conflict.py#L22-L50) (`ConflictRecord`)
- **Fundamental Invariant**:
  $$\mathbf{provenance/source \neq epistemic\ truth\ status}$$
- **Audit Findings**:
  1. `USER_STATED` is an explicit provenance source, distinct from epistemic status. A user assertion enters the system with epistemic state `ASSERTED` or `HYPOTHETICAL` and confidence $\le 0.70$. It is **NEVER** automatically promoted to `VERIFIED` (`FACT`).
  2. Contradiction detection in [`KnowledgeStore.detect_contradiction()`](file:///c:/Users/Lunafiah/Desktop/My_project/Lucia/src/core/knowledge/store.py#L150-L185) successfully identifies opposing polarities (`True` vs `False`) or value mismatches.
  3. When a user assertion conflicts with established knowledge, the system preserves both hypotheses in a `ConflictRecord` without silent overwrite.
  4. CAPS responsibility: CAPS **does NOT own knowledge revision or conflict resolution** (which belongs to `KnowledgeStore` and `ReasoningKernel` / JTMS). CAPS merely reads the resulting epistemic conflict state to select `CommunicativeAct.CLARIFY` or qualified assertion.

#### 3.4.2 Isolated Prototype Telemetry
- **Test Harness**: [`tests/evaluation/phase23_caps/run_caps_readiness_benchmark.py`](file:///c:/Users/Lunafiah/Desktop/My_project/Lucia/tests/evaluation/phase23_caps/run_caps_readiness_benchmark.py#L272-L343)
- **Execution Result**:
  - Conflicting assertion (`ent:user`, `c:CANINE`, `False` vs existing `True`) $\rightarrow$ Emitted `CommunicativeAct.CLARIFY`, silent overwrite prevented: `True`.
  - Non-conflicting assertion $\rightarrow$ Epistemic state remained `INFERRED`, automatic promotion to `FACT` prevented: `True`.
- **Verdict**: **PASS (Separation of provenance from truth is structurally verified; conflict policy correctly decoupled from CAPS)**
- **Blocking Status**: **NO**

---

### 3.5 Determinism Validation

- **Test Harness**: [`tests/evaluation/phase23_caps/run_caps_readiness_benchmark.py`](file:///c:/Users/Lunafiah/Desktop/My_project/Lucia/tests/evaluation/phase23_caps/run_caps_readiness_benchmark.py#L500-L512)
- **Measurement**: Two separate executions over identical frozen input snapshots:
  - Hash 1: `65605b865829f40d3e1bd7d068a29398549227166e87d8dcb3b4dbaaa034d60c`
  - Hash 2: `65605b865829f40d3e1bd7d068a29398549227166e87d8dcb3b4dbaaa034d60c`
  - Output equality: `Identical == True` (0.00% drift).
- **Execution Latency**: 2.02 ms total for all gate evaluations on CPU.

---

## 4. Evidence Matrix

| Evidence ID | Repository File / Line Range | Component / Symbol | Verified Property |
|---|---|---|---|
| **E0** | [`data/profile.json`](file:///c:/Users/Lunafiah/Desktop/My_project/Lucia/data/profile.json#L1-L3) | Genesis Gate | Invariant bit-exact: `{"is_onboarded": false}`. Zero live activation. |
| **E1** | [`src/core/cognition/kernel/engine.py:75-102`](file:///c:/Users/Lunafiah/Desktop/My_project/Lucia/src/core/cognition/kernel/engine.py#L75-L102) | `InformationSubgoal` | Contains predicate, argument slots (0 = unbound), scope, and reason codes. |
| **E2** | [`src/core/cognition/contract/inference.py:59-77`](file:///c:/Users/Lunafiah/Desktop/My_project/Lucia/src/core/cognition/contract/inference.py#L59-L77) | `DisambiguationSubgoal` | Defines disambiguation candidates and scope context for clarification acts. |
| **E3** | [`src/core/knowledge/store.py:21-45`](file:///c:/Users/Lunafiah/Desktop/My_project/Lucia/src/core/knowledge/store.py#L21-L45) | `ProvenanceType` | Defines `USER_STATED` as provenance distinct from epistemic `EpistemicState`. |
| **E4** | [`src/core/orchestrator/cognitive_orchestrator.py:108-115`](file:///c:/Users/Lunafiah/Desktop/My_project/Lucia/src/core/orchestrator/cognitive_orchestrator.py#L108-L115) | `CognitiveOrchestrator._history` | Proves discourse history in production is exclusively string tuples with zero entity retention. |
| **E5** | [`tests/evaluation/phase23_caps/run_caps_readiness_benchmark.py`](file:///c:/Users/Lunafiah/Desktop/My_project/Lucia/tests/evaluation/phase23_caps/run_caps_readiness_benchmark.py) | Benchmark Suite | Standalone test runner evaluating R1–R4 and determinism in 2.02 ms. |
| **E6** | [`docs/PhaseDocs/Lucia-phase23-Semantic_Substrate/evaluation_artifacts/caps_readiness/caps_benchmark_telemetry.json`](file:///c:/Users/Lunafiah/Desktop/My_project/Lucia/docs/PhaseDocs/Lucia-phase23-Semantic_Substrate/evaluation_artifacts/caps_readiness/caps_benchmark_telemetry.json) | Benchmark Telemetry | Persisted JSON telemetry capturing execution outcomes and serialization hashes. |

---

## 5. Blocking Gaps & Minimal Contract Specifications

### 5.1 Blocking Gap 1: Cross-Turn Discourse Referent Retention (R3)
- **Description**: The production runtime currently lacks any semantic entity tracking across turns. Without a discourse cache contract, CAPS cannot resolve cross-turn anaphora or maintain interrogative focus across successive user inputs.
- **Required Action**: Ratify a minimal `DiscourseContextCache` contract specifying capacity ($N \le 16$), salience decay rate ($\gamma = 0.60$), and lookup resolution before authorizing production implementation.

### 5.2 Blocking Gap 2: Formal Argument Role Mapping for Subgoals (R1)
- **Description**: `InformationSubgoal` uses numeric indices (`arg0_id`, `arg1_id`, `arg2_id`). While mapping to `:ARG0` and `:ARG1` is deterministic by convention, the relationship between predicate definitions and their required semantic roles is not formally contracted.
- **Required Action**: Define an argument role binding table or schema convention mapping predicate ontology definitions to semantic role labels.

---

## 6. Research Gates Summary Table

| Gate | Result | Supporting Evidence | Blocking Implementation? |
|---|---|---|---|
| **R1 — InformationSubgoal → Inquire compiler** | **PASS** | E1, E2, E5 (`tests/evaluation/phase23_caps/run_caps_readiness_benchmark.py:361-394`). Deterministically compiles open slots to `INQUIRE` and ambiguous codes to `CLARIFY`. | **NO** |
| **R2 — Internal goal → grounded SemanticGraph** | **PARTIAL** | E3, E5 (`run_caps_readiness_benchmark.py:395-430`). Bounded selection, binding, and assertion refusal verified without LLM. Autonomous open-ended creative generation is unproven and bounded. | **NO** |
| **R3 — Turn-level discourse entity retention** | **PARTIAL** | E4 (`CognitiveOrchestrator._history` string tuples audit), E5. Production code has zero cross-turn entity cache. Prototype cache verified. | **YES** |
| **R4 — User assertion conflict / provenance policy** | **PASS** | E3 (`KnowledgeStore`), E5 (`run_caps_readiness_benchmark.py:465-498`). Provenance is decoupled from epistemic truth. Conflicts trigger `CLARIFY` without silent overwrite. | **NO** |

---

## 7. Architectural Recommendation

$$\mathbf{IMPLEMENTATION\ STILL\ GATED}$$

### Rationale
While **R1**, **R2**, and **R4** have demonstrated clear architectural feasibility and isolated prototype validation:
1. **R3 remains a critical blocking gap**: In the absence of an operational discourse entity cache contract in the cognitive turn interface, an implementation of CAPS in the runtime would be incapable of handling multi-turn conversational referents and anaphoric resolution.
2. Moving directly from boundary ratification to production implementation without first formalizing:
   - (a) The **Discourse Referent Retention Contract** (R3), and
   - (b) The **Predicate Role Binding Convention** (R1),  
   would violate the governance invariant: `research/evidence → architecture decision → implementation contract → implementation`.

### Next Minimal Steps
1. Author an architectural contract specification for `DiscourseContextCache` (defining bounded $N=16$ capacity, salience decay, and integration with `CognitiveOrchestrator`).
2. Update the CAPS Implementation Contract draft with the explicit `InformationSubgoal` role mapping table.
3. Once those two contracts are reviewed and ratified, transition the milestone to `IMPLEMENTATION CONTRACT READY`.
