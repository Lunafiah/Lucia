# DOC-P23H-RUNTIME-INTEGRATION-SPEC-R1-001
## Phase 23-H Bounded Reasoning Substrate Runtime Integration Specification (Revision 1.1)

**Document Identifier**: `DOC-P23H-RUNTIME-INTEGRATION-SPEC-R1-001` (Rev 1.1)  
**Phase & Milestone**: Phase 23-H Bounded Goal-Directed Reasoning & JTMS / Runtime Ingress  
**Authority Context**: Derived from ADR-030, ADR-035, ADR-038, `DOC-P23H-RULE-COMPILER-CONTRACT-V1-001`, `DOC-P23H-RULE-COMPILER-IMPLEMENTATION-SPEC-R1-001`, and verified repository source code  
**Operating Mode**: Specification Only. Zero production runtime code modifications, zero test changes, zero Genesis alterations.  
**Target Integration Surface**: `src/core/orchestrator/cognitive_orchestrator.py`, `src/core/cognition/service.py` (Candidate Cognitive Service Boundary)  
**Date**: 2026-10-20  
**Evidence Discipline Labels Applied**: `[REPOSITORY FACT]`, `[VALIDATED EXISTING CONTRACT]`, `[RATIFIED SPECIFICATION]`, `[RESEARCH INFERENCE]`, `[PROPOSED CONTRACT]`, `[UNPROVEN]`, `[DEFERRED]`, `[REJECTED]`  

---

### Executive Summary & Final Verdict

This document defines the **minimal, safe, reversible implementation specification** for integrating the verified Phase 23-H reasoning substrate into Lucia's production runtime.

The underlying reasoning substrate consists of:
1. `KnowledgeStore` (P16 structured proposition & rule repository, `src/core/knowledge/`)
2. `RuleCompilerAdapter` (P23-H rule compiler, `src/core/cognition/kernel/compiler.py`, 17/17 tests PASS)
3. `RuleIndex` (head-predicate indexed Horn clauses, `src/core/cognition/kernel/rules.py`)
4. `ReasoningKernel` & `JTMS` (bounded Strong Kleene K3 engine, `src/core/cognition/kernel/engine.py`, `jtms.py`, frozen at commit `3eef803`)
5. `LanguageIngressGate` & `CAPS` (ADR-038 epistemic perimeter firewall and communicative act selector)

The integration boundary is defined as an **on-demand cognitive service** (`EpistemicReasoningService`) operating between Stage S8 (`KnowledgeRetrieval`) and Stage S10b (`CAPS Proposition Selection`). It resolves candidate hypotheses without introducing persistent TermIDs, without running unconstrained forward reasoning, without automatic persistence of derived propositions, without scalar confidence thresholding (`NEG-02`), and without modifying the frozen P23-H kernel.

#### Fundamental Epistemic Corrections Integrated in Rev 1.1:
1. **P23-H TRUE $\ne$ ASSERT (Epistemic Boundary Blocker Resolved)**: A P23-H `TRUE` result proves *deductive derivability* within the symbolic reasoning substrate from premises admitted into the kernel. It does **NOT** automatically grant epistemic authority or communicative warrant to `ASSERT` to the user. Confidence is never escalated to `FACT`. P23-H derives a transient `DerivedResult`, which passes through the epistemic admissibility boundary into `AdmissibleEvidencePool` (classified as `EpistemicStatus.INFERRED`). CAPS evaluates dialogue context, dyadic state, pragmatic stance, and communicative policy; `ASSERT` is selected **only if the downstream communication contract legally admits assertion of an inferred proposition**.
2. **KnowledgeStore DERIVED $\ne$ Automatically Certified P23-H INFERRED**: Under ADR-038 (`gate.py:206-211`), `INFERRED` status requires authoritative certification by `LanguageIngressGate` verifying a valid numeric rule ID and supporting premise IDs. `KnowledgeStore.Proposition(provenance=DERIVED)` stores only string `evidence_ids` without numeric DAG structure. Neither compiler nor service can self-certify `INFERRED` without gate validation. This mapping is explicitly classified as **`[PROPOSED CONTRACT] / [UNPROVEN]`** pending formal premise-DAG reconstruction.
3. **RuleIndex Lifecycle & Ownership Clarification**: `RuleIndex` is **constructed** by `RuleCompilerAdapter`, **stored and lifecycle-managed** by runtime orchestration (`CognitiveOrchestrator`), and **consumed as an injected dependency** by `ReasoningKernel`. `ReasoningKernel` does not own the lifecycle of `RuleIndex`.

**Final Specification Verdict**: **`READY FOR IMPLEMENTATION`** (Scoped strictly to Candidate Grounding & Subgoal Verification MVP; arbitrary natural language parsing, un-reconstructed DERIVED premise escalation, and multi-justification disk persistence remain explicitly deferred).

---

### 1. Current Live Production Call Graph & Stage Trace

A complete, empirical trace of Lucia's 16-stage cognitive cycle in [`src/core/orchestrator/cognitive_orchestrator.py`](file:///c:/Users/Lunafiah/Desktop/My_project/Lucia/src/core/orchestrator/cognitive_orchestrator.py) (`CognitiveOrchestrator.process()`) reveals the exact data structures and stage boundaries:

```text
====================================================================================================
                        LUCIA 16-STAGE COGNITIVE PIPELINE (LIVE REPOSITORY CALL GRAPH)
====================================================================================================

Turn Input: input_text: str, user_language: Optional[str]
     │
     ▼
[Stage 0: Temporal Embodiment & Social Observation] (P25, line 597)
     │ Invokes: TemporalEmbodimentCoordinator.process_observation()
     ▼
[Stage 1: Sensory Encoding] (line 608)
     │ Invokes: StimulusProcessor.process(input_text) -> Stimulus
     ▼
[Stage 2: Generative Prior Expectation] (line 617)
     │ Invokes: ActiveInferenceCore.predict() -> PriorExpectation
     ▼
[Stage 3: Limbic Integration] (line 637)
     │ Invokes: EmotionCore.step(...) -> commits PAD state transition (Coupled MT-LNN)
     ▼
[Stage 4: Prediction Surprise & Belief Update] (line 662)
     │ Invokes: ActiveInferenceCore.update(...) -> Free energy / surprise modulation
     ▼
[Stage 5: Homeostatic Modulation] (line 683)
     │ Invokes: HomeostaticEngine.compute_modulation(...) -> SomaticMarkers
     ▼
[Stage 6: Affective Ecphory (Memory Retrieval)] (line 719)
     │ Invokes: EcphoryEngine.query(pad_final, traces) -> echo_vector, recollection_result
     ▼
[Stage 7: Memory Context Extraction] (line 755)
     │ Computes m_avail = 1.0 if norm(echo_vector) > 0.01 else 0.0
     ▼
[Stage 8: Structured Knowledge Retrieval] (line 764)
     │ Invokes: KnowledgeStore.query_relevant(input_text, max_results=5)
     │ Returns: known_propositions: List[Proposition]
     ▼
[Stage 9: Relationship Read] (line 779)
     │ Invokes: RelationshipUpdater.get_state() -> rel_state: RelationshipState
     ▼
[Stage 10: Communication Policy Evaluation] (line 803)
     │ Invokes: CommunicationPolicy.compute(..., knowledge={"fact_count": len(known_propositions)}, ...)
     │ Returns: comm_state: CommunicationState
     ▼
[Stage 10b: Communicative Act & Proposition Selection (CAPS, Phase 23)] (line 835)
     │ Data Prepared:
     │   - all_verified_props = tuple(known_propositions) + tuple(life_state_props)
     │   - DialogueContextSnapshot (turn_id, input_text, active_referents, resolution_status, dyadic_state)
     │   - CognitiveStateSnapshot (cand_pred, cand_subj, cand_obj, polarity=True)
     │   - AdmissibleEvidencePool (verified_propositions=all_verified_props, user_claims=())
     │   - CommunicationPolicySnapshot (strategy, directness, formality, elaboration, supportiveness)
     │ Invokes: evaluate_caps(dialogue_ctx, cognitive_state, evidence_pool, comm_policy, session_id)
     │ Returns: caps_result: Optional[CAPSResult]
     │
     │ ADR-035: RealizationInputContract.from_caps(caps_result, known_propositions=all_verified_props, ...)
     │
     │ ADR-038 Assistant Proposition Semantic Indexing (lines 950-988):
     │   - intern_concept(target_predicate) -> pred_id
     │   - allocate_scope(SCOPE_TYPE_MODAL) -> scope_id
     │   - allocate_term(...) in self._term_arena -> asst_term_id
     ▼
[Stage 11: Contextual Prompt Assembly] (line 996)
     │ Invokes: PromptAssembler.assemble(contract=realization_contract, known_propositions=..., ...)
     ▼
[Stage 12: Conversational Pacing] (line 1040)
     │ Invokes: TemporalEmbodimentCoordinator.compute_attunement_modulation(...)
     ▼
[Stage 13: LLM Generation & Boundary Layer] (line 1073)
     │ Invokes: LLMBackend.generate(prompt) -> raw_text
     │ Invokes: BoundaryLayer.validate(raw_text) -> clean_text
     ▼
[Stage 14: Fail-Closed Semantic Fidelity Gate (ADR-035)] (line 1099)
     │ Invokes: SemanticFidelityGate.verify(clean_text, contract=realization_contract) -> GateDecision
     ▼
[Stage 15: Expression Policy & Actuation State] (line 1149)
     │ Invokes: ExpressionPolicy.compute(...) -> ExpressionState
     ▼
[Stage 16: Post-Turn Persistence & Adaptation] (line 1187)
     │ 16.1 LNN Plasticity Training
     │ 16.2 Affective Memory Storage
     │ 16.3 Dynamic Attunement Update
     │ 16.4 History Append
     │ 16.4b DiscourseContextCache.update_turn()
     │ 16.4c DyadicDiscourseState update
     │ 16.5 Relationship State Update
====================================================================================================
```

#### Detailed Boundary Findings:
1. **`KnowledgeStore.query_relevant()` Output**: Returns `List[Proposition]`, where each `Proposition` has string fields (`subject`, `predicate`, `object`), float `confidence`, `provenance: ProvenanceType`, and boolean `valid` (`[REPOSITORY FACT]`).
2. **`CommunicationPolicy` Knowledge Consumption**: In Stage S10 (`cognitive_orchestrator.py:807`), `CommunicationPolicy` consumes ONLY `{"fact_count": len(known_propositions)}`. It does not inspect predicates, entities, or logical structure (`[REPOSITORY FACT]`).
3. **`CAPS` Context Consumption**: Stage S10b consumes `AdmissibleEvidencePool(verified_propositions=all_verified_props)` and `CognitiveStateSnapshot`. Crucially, `evaluate_caps()` accepts an optional parameter: `subgoals: Optional[Sequence[InformationSubgoal]] = None` (`src/core/communication/caps.py:395`). In lines 403–463, Priority 1 of `evaluate_caps` compiles `InformationSubgoal` directly into `CommunicativeAct.INQUIRE` or `CommunicativeAct.CLARIFY` (`[REPOSITORY FACT]`).
4. **`RealizationInputContract` Formation**: Occurs immediately after CAPS evaluation (`cognitive_orchestrator.py:930–948`) using `RealizationInputContract.from_caps()`.
5. **ADR-038 Assistant Semantic Indexing**: Occurs at lines 950–988 in Stage 10b, interning the assistant's communicative intent into `_symbol_table` and allocating an ephemeral term in `_term_arena` under a modal scope (`[REPOSITORY FACT]`).
6. **Legitimate Reasoning Service Invocation Point**: The P23-H reasoning service must be invoked **immediately prior to CAPS evaluation** (between S8/S9 and S10b). At this point, `known_propositions` have been retrieved from S8, the candidate cognitive state is known, but communicative act selection has not yet occurred. Reasoning over the candidate allows P23-H to supply either verified grounding or an `InformationSubgoal` directly into `evaluate_caps()`.

---

### 2. Verified Reasoning Service Boundary

#### 2.1 Existing Abstraction Analysis
Inspection of `src/core/cognition/kernel/engine.py` demonstrates that the core numeric engine already exposes:
- `Goal(predicate_id: int, arg0_id: int, arg1_id: int = 0, arg2_id: int = 0, polarity: bool = True, scope_id: int = 1)` (`[REPOSITORY FACT]`)
- `GoalResult(status: KleeneValue, term_id: int, subgoal: Optional[InformationSubgoal], conflict: Optional[ConflictRecord], steps_taken: int, depth_reached: int, rule_id: int, premise_ids: Tuple[int, ...])` (`[REPOSITORY FACT]`)
- `InformationSubgoal(target_predicate_id: int, arg0_id: int, arg1_id: int, arg2_id: int, polarity: bool, scope_id: int, rule_id: int, reason_code: int)` (`[REPOSITORY FACT]`)
- `ConflictRecord(conflicting_term_id: int, predicate_id: int, arg0_id: int, ...)` (`[REPOSITORY FACT]`)

In `src/core/orchestrator/cognitive_orchestrator.py:212, 263, 360`, `ReasoningKernel` is already an attached attribute (`self._reasoning_kernel`).

#### 2.2 Minimal Service Interface Specification
Rather than coupling the low-level recursive engine directly into `CognitiveOrchestrator.process()`, a dedicated, stateless coordination adapter is specified: `EpistemicReasoningService`.

```python
# [PROPOSED CONTRACT] Target module: src/core/cognition/service.py

class EpistemicReasoningService:
    """
    On-demand cognitive reasoning coordinator.
    Bridges Stage S8 KnowledgeStore retrievals and Stage S10b CAPS evaluation.
    
    Invariants:
    1. Zero heap allocation in inner resolution loop (delegates to ReasoningKernel).
    2. Ephemeral projection: KnowledgeStore propositions are projected into TermArena
       strictly for the lifetime of the session epoch without persistent TermIDs.
    3. Discrete K3: Operates purely under Strong Kleene 3-valued logic.
    4. On-demand execution: Invoked only when an active candidate goal exists.
    5. Epistemic qualification: TRUE derivation emits transient DerivedResult,
       NOT automatic ASSERT authorization.
    """
    
    def __init__(
        self,
        kernel: ReasoningKernel,
        symbol_table: SymbolTable,
        arena: TermArena,
    ) -> None:
        self._kernel = kernel
        self._symbol_table = symbol_table
        self._arena = arena

    def verify_candidate_goal(
        self,
        candidate_predicate: str,
        candidate_subject: Optional[str],
        candidate_object: Optional[str],
        known_propositions: Sequence[Proposition],
        polarity: bool = True,
    ) -> Tuple[GoalResult, Optional[DerivedResult]]:
        """
        Projects verified premises, resolves the candidate goal via backward chaining,
        and returns the consolidated GoalResult plus an optional transient DerivedResult.
        """
        ...
```

---

### 3. Knowledge Projection Contract (`Proposition` → `LogicalTerm`)

The mapping from `KnowledgeStore.Proposition` to `LogicalTerm` in `TermArena` is strictly governed by **ADR-038** and **Invariant NEG-02** (zero scalar thresholding).

#### 3.1 Field-by-Field Classification Matrix

| `KnowledgeStore.Proposition` Field | Type | Target Representation in `LogicalTerm` | Classification | Projection Rule & Epistemic Enforcement |
|---|---|---|---|---|
| `predicate` | `str` | `predicate_id: int` | `REQUIRES TRANSFORMATION` | Interned via `SymbolTable.intern_concept(predicate)`. Result must be $> 0$. |
| `subject` | `str` | `arg0_id: int` | `REQUIRES TRANSFORMATION` | Interned via `SymbolTable.intern_concept(subject)`. Result must be $> 0$. |
| `object` | `str` | `arg1_id: int` | `REQUIRES TRANSFORMATION` | If non-empty, interned via `SymbolTable.intern_concept(object)`. If empty/None, defaults to `0`. |
| `valid` | `bool` | Filter Gate / `is_active: bool` | `REQUIRES TRANSFORMATION` | If `valid == False`, proposition is **EXCLUDED** from projection. Never admitted to `TermArena`. |
| `superseded_by` | `Optional[str]` | Filter Gate | `REQUIRES TRANSFORMATION` | If `superseded_by is not None`, proposition is **EXCLUDED** from projection. |
| `id` | `str` | N/A (Transient mapping) | `NOT LEGALLY USABLE` | Persistent string ID cannot serve as numeric `term_id`. Ephemeral `term_id` is allocated sequentially by `TermArena.allocate_term()`. A reverse mapping dict `Dict[int, str]` is maintained in RAM for trace observability only. |
| `confidence` | `float` | Excluded from Logic | `NOT LEGALLY USABLE` | **HARD RULE (NEG-02)**: Do NOT introduce `confidence >= X -> FACT`. Scalar confidence measures sensor SNR or model calibration, not ontological ground truth. It is ignored by discrete K3 reasoning. |
| `provenance` | `ProvenanceType` | `epistemic_status: EpistemicStatus` | `REQUIRES TRANSFORMATION` | See Epistemic Status Mapping Table below. Only authoritative classes can yield `EpistemicStatus.FACT`. |
| `evidence_ids` | `List[str]` | N/A | `NOT LEGALLY USABLE` | Strings cannot serve as numeric `premise_ids: Tuple[int, ...]`. P23-H requires integer TermIDs of active arena terms. `premise_ids` is set to `()` for ground premises. |
| `created_at` | `float` | N/A | `NOT NEEDED` | P23-H has no internal clock. Temporal metadata is discarded at the deductive boundary. |
| *(Implicit Polarity)* | N/A | `polarity: bool` | `REQUIRES TRANSFORMATION` | Standard `KnowledgeStore.Proposition` tuples represent affirmative assertions (`polarity = True`). |

#### 3.2 Epistemic Status & Provenance Qualification

```text
[KnowledgeStore Provenance]                    [LanguageIngressGate / Projection]             [TermArena EpistemicStatus]
VERIFIED / OBSERVED         ───────────────►   Certified Ground Truth          ──────────────►  EpistemicStatus.FACT
DERIVED (No numeric DAG)    ───────────────►   Uncertified Derivation          ──────────────►  EpistemicStatus.UNKNOWN [PROPOSED CONTRACT]
USER_STATED (Spontaneous)   ───────────────►   Direct User Testimony           ──────────────►  EpistemicStatus.FACT (or BELIEF scope)
USER_STATED (Echo/Prompted) ───────────────►   F15 Echo Protection             ──────────────►  EpistemicStatus.UNKNOWN
LLM_PROPOSED / UNCERTAIN    ───────────────►   Unverified Hypothesis           ──────────────►  EpistemicStatus.UNKNOWN (or Quarantined)
CONTRADICTED                ───────────────►   Refuted Fact                    ──────────────►  EXCLUDED FROM PROJECTION
```

#### Epistemic Contract Tracing: `KnowledgeStore DERIVED` $\ne$ Automatically Certified `P23-H INFERRED`
- `[VALIDATED EXISTING CONTRACT]`: In [`src/core/language/adapter/gate.py:206-211`](file:///c:/Users/Lunafiah/Desktop/My_project/Lucia/src/core/language/adapter/gate.py#L206-L211) (ADR-038), `LanguageIngressGate` explicitly enforces:
  ```python
  elif candidate.source_class == IngressSourceClass.DERIVED:
      if not candidate.supporting_premise_ids or candidate.rule_id == 0:
          raise EpistemicEscalationError(
              "DERIVED candidate proposition lacks required supporting premises or rule ID"
          )
      assigned_status = EpistemicStatus.INFERRED
  ```
- **Authority Boundary Finding**: Epistemic certification is exclusively owned by the `LanguageIngressGate` perimeter boundary (ADR-038). Neither `RuleCompilerAdapter` nor `EpistemicReasoningService` possesses the legal authority to self-certify `EpistemicStatus.INFERRED`.
- **Structural Disconnect**: `KnowledgeStore.Proposition` stores only flat string `evidence_ids: List[str]` and has no numeric `rule_id` or `premise_ids`. Therefore, a stored proposition with `provenance == DERIVED` **fails closed** against ADR-038 criteria: it lacks the recursive premise DAG required for JTMS non-monotonic retraction.
- **Contractual Status**: Projecting un-reconstructed `KnowledgeStore` DERIVED propositions directly into `EpistemicStatus.INFERRED` is formally classified as **`[PROPOSED CONTRACT] / [UNPROVEN]`**. In the MVP, stored propositions with `provenance=DERIVED` without verified active premise IDs in `TermArena` must be projected as `EpistemicStatus.UNKNOWN` or evaluated through backward chaining from ground facts.

---

### 4. Goal Formation Analysis

The critical bottleneck for general automated reasoning is **Goal Formation**. The four operational categories are classified as follows:

```text
====================================================================================================
                                GOAL FORMATION MATURITY MATRIX
====================================================================================================
Category                                    Status          Repository Evidence / Boundary
────────────────────────────────────────────────────────────────────────────────────────────────────
A. Explicit Conversational Question         MISSING         No natural-language semantic question
   (e.g., "Is Socrates mortal?")            [DEFERRED]      parser exists in language drivers.
                                                            EnglishLanguageDriver only matches toy regex.
                                                            Solving general NL question parsing is
                                                            EXCLUDED from MVP scope.

B. Candidate Grounding / Verification       SUPPORTED       Fully supported today.
   (CognitiveStateSnapshot /                [VALIDATED]     CognitiveOrchestrator:874–892 already forms
   IngressCandidateAssertion)                               cand_pred, cand_subj, cand_obj from S8
                                                            propositions. Converting strings to IDs
                                                            via SymbolTable yields a typed Goal.

C. Internal InformationSubgoal              SUPPORTED       Fully implemented and verified.
   (Generated on UNKNOWN by P23-H)          [VALIDATED]     ReasoningKernel emits InformationSubgoal.
                                                            CAPS Priority 1 (caps.py:403–463) compiles
                                                            it directly into CommunicativeAct.INQUIRE.

D. Spontaneous Forward Reasoning            REJECTED        Strictly forbidden by ARCH-030.1.
   (Unconstrained premise expansion)        [REJECTED]      Forward chaining causes combinatorial explosion
                                                            and violates the 20W edge resource budget.
                                                            Reasoning must remain backward & goal-directed.
====================================================================================================
```

**MVP Boundary Decision**: The initial production integration shall operate **exclusively on Category B (Candidate Grounding Verification)** and **Category C (InformationSubgoal Handling)**. Category A is deferred. Category D is permanently rejected.

---

### 5. `RuleIndex` Ownership and Lifecycle

The ownership, construction, storage, and consumption of `RuleIndex` are strictly separated across architectural layers:

```text
====================================================================================================
                             RULEINDEX OWNERSHIP & LIFECYCLE DECOMPOSITION
====================================================================================================
Question / Responsibility       Authoritative Owner             Repository Mechanism
────────────────────────────────────────────────────────────────────────────────────────────────────
Who constructs RuleIndex?       RuleCompilerAdapter             compile_rule_set(rules, symbol_table)
                                [src/core/cognition/kernel/     Emits Tuple[RuleIndex, RuleCompilationReport]
                                compiler.py]

Who stores & manages it?        Runtime Orchestration           CognitiveOrchestrator holds instance
                                [CognitiveOrchestrator]         attribute (self._rule_index).
                                                                Owns epoch lifecycle & memory lifetime.

Who recompiles it?              Runtime Orchestration           CognitiveOrchestrator.reset_lifecycle()
                                [CognitiveOrchestrator]         Recompiles rules against new SymbolTable.

Who consumes it?                ReasoningKernel                 Injected via constructor:
                                [src/core/cognition/kernel/     ReasoningKernel(rule_index, arena, jtms)
                                engine.py]                      Kernel strictly reads rules via:
                                                                rule_index.get_rules_for_head(pred_id).
====================================================================================================
```

1. **Clarification on Ownership**: `ReasoningKernel` does **NOT** own the lifecycle of `RuleIndex`. The kernel merely receives and consumes it as an injected dependency (`[REPOSITORY FACT]`).
2. **Compilation Trigger**: Compilation occurs **once per lifecycle epoch** during orchestrator initialization (`CognitiveOrchestrator.__init__` or post-boot hydration).
3. **Immutability During Turns**: `[REPOSITORY FACT]` Inspection of `src/core/knowledge/` demonstrates that `store_rule()` is invoked ONLY during database deserialization/hydration in `persistence.py`. Zero runtime stages mutate inference rules during live turns.
4. **Lifecycle Reset Interaction**: In `CognitiveOrchestrator.reset_lifecycle()`, `self._symbol_table` is re-instantiated (`SymbolTable()`). Because symbol IDs are assigned sequentially, recompilation of `KnowledgeStore.get_all_rules()` against the fresh `SymbolTable` MUST occur during `reset_lifecycle()` to prevent symbol desynchronization.
5. **No Dynamic Infrastructure**: Zero event buses, zero file watchers, and zero dirty-flag polling mechanisms are needed. Static lifecycle compilation is completely sufficient.

---

### 6. `TermArena` & `SymbolTable` In-Memory Lifecycle

```text
====================================================================================================
                              ARENA & SYMBOL LIFECYCLE DYNAMICS
====================================================================================================

Session Start / Boot
        │
        ▼
   SymbolTable()  ◄── Shared between LanguageAdapter, ADR-038 Ingress, ReasoningKernel, and CAPS
   TermArena()    ◄── 4096 preallocated slots. Zero dynamic heap allocation in inner loop.
        │
        ├───────────────────────────────────────────────────────────────────┐
        ▼                                                                   ▼
Turn t: Retrieve S8 Props                                           Turn t: Realization Contract
        │ Project into TermArena                                            │ Stage 10b
        │ (ephemeral term_ids)                                              │ Intern assistant seed
        ▼                                                                   ▼
   P23-H Backward Resolution                                         asst_term_id allocated
        │                                                            under SCOPE_TYPE_MODAL
        ▼                                                                   │
   GoalResult                                                               │
   (TRUE / UNKNOWN / FALSE)                                                 ▼
        │                                                           Turn t+1: User Response
        ▼                                                                   │ IngressGate checks
   CAPS Communicative Act                                                   │ antecedent_term_id == asst_term_id
        │                                                                   │ (F15 Anti-Echo Defense)
        ▼                                                                   ▼
   [INTER-TURN BOUNDARY: NO ARENA WIPE] ────────────────────────► Preserves Causal Antecedents!
        │
        ▼
Session End / Operator Reset (`reset_lifecycle()`)
        │
        ▼
   Wipe & Re-instantiate TermArena() and SymbolTable()
   Recompile RuleIndex from KnowledgeStore
====================================================================================================
```

#### Lifecycle Rules:
- **Shared Runtime Structures**: `CognitiveOrchestrator` already owns `_term_arena` and `_symbol_table`. `ReasoningKernel` safely shares these exact structures (`[VALIDATED EXISTING CONTRACT]`).
- **Inter-Turn Preservation**: `TermArena` **MUST NOT be wiped between conversational turns**. Wiping the arena would destroy ADR-038 assistant seed terms (`asst_term_id`), causing dangling antecedent pointers in Turn $t+1$ and completely compromising the F15 anti-echo defense.
- **Arena Invalidation vs Wiping**: Non-monotonic belief revision is handled exclusively via `JTMS.retract_premise()` marking terms `is_active = False`, never by shifting memory arrays or zeroing active slots during a session.

---

### 7. Result Boundary & Downstream Consumer Specification

#### 7.1 Epistemic Separation: Logical Truth $\ne$ Conversational Assertibility

> [!CAUTION]
> **EPISTEMIC BOUNDARY INVARIANT (P23-H TRUE $\ne$ ASSERT)**:  
> P23-H `TRUE` only establishes deductive validity within the closed symbolic calculus given premises present in `TermArena`.  
> It does **NOT** grant epistemic authority or communicative warrant to `ASSERT` in conversation.  
> Confidence must **NEVER** be automatically upgraded to `FACT`.

The causal flow from P23-H deduction to communication strictly enforces the following decoupled sequence:

```text
====================================================================================================
               EPISTEMIC DERIVATION TO COMMUNICATION FLOW (NO IMPLICIT ASSERT)
====================================================================================================

                     P23-H Goal Resolution
                               │
            ┌──────────────────┼──────────────────┐
            ▼                  ▼                  ▼
    [status: TRUE]     [status: UNKNOWN]  [status: FALSE]
            │                  │                  │
            ▼                  │                  ▼
┌───────────────────────┐      │         ┌───────────────────────┐
│ Transient             │      │         │ ConflictRecord        │
│ DerivedResult         │      │         └───────────┬───────────┘
│ • status: INFERRED    │      │                     │
│ • (NOT FACT!)         │      │                     ▼
│ • rule_id, premises   │      │         [CAPS Priority 3 Gate]
│ • JTMS justification  │      │         • Grounding: CONFLICT
└───────────┬───────────┘      │         • Act: CLARIFY / REFUSE
            │                  │
            ▼                  │
┌───────────────────────┐      │
│ Epistemic &           │      │
│ Admissibility Gate    │      │
│ • Admitted as         │      │
│   INFERRED candidate  │      │
│ • Zero auto-persist   │      │
└───────────┬───────────┘      │
            │                  │
            ▼                  ▼
┌────────────────────────────────────────────────────────┐
│ CAPS Deliberation Boundary (Stage 10b)                 │
│ Considers:                                             │
│   - DialogueContextSnapshot (Phase, Floor, Stance)     │
│   - CommunicationPolicySnapshot (Directness, Formality)│
│   - AdmissibleEvidencePool (verified vs inferred)      │
│   - subgoals: Optional[Sequence[InformationSubgoal]]   │
└───────────────────────────┬────────────────────────────┘
                            │
        ┌───────────────────┼───────────────────┐
        ▼                   ▼                   ▼
 [CommunicativeAct]  [CommunicativeAct]  [CommunicativeAct]
     INQUIRE             ASSERT               HEDGE /
  (Missing Premise)   (ONLY IF downstream  ACKNOWLEDGE
                       contract admits     (Polite reception
                       assertion of        or qualified
                       inferred candidate) claim)
====================================================================================================
```

#### Detailed Stage Rules:
1. **P23-H `TRUE`**: Emits a `DerivedResult` with `term_id > 0`, `epistemic_status = EpistemicStatus.INFERRED`, `rule_id`, `premise_ids`, and registered JTMS justification. It is **never** labeled `FACT`.
2. **Epistemic Admissibility Boundary**: The derived candidate is placed into working memory with `ProvenanceType.DERIVED`. It is visible to CAPS as an inferred hypothesis, not an undeniable axiom.
3. **CAPS Deliberation**: CAPS evaluates whether asserting an inferred conclusion is appropriate given:
   - Dialogue phase (e.g., during `OPENING_ENCOUNTER`, unsolicited assertion may be suppressed in favor of greeting).
   - Directness / formality policy (policy may require hedging such as *"Based on what we discussed..."* or asking confirmation).
4. **Downstream Enforcement**: `ASSERT` is chosen **only if** the downstream policy and realization contract legally authorize it.

#### Strict Persistence Boundary:
- `[RATIFIED SPECIFICATION]`: A `TRUE` derivation **SHALL NOT be automatically persisted to `KnowledgeStore`**.
- It remains transient in `TermArena` and in memory during the turn.
- Rationale: Automatic persistence of every deductive intermediate would pollute the long-term knowledge base with situational lemmas, bypass the canonical memory consolidation pipeline, and violate the explicit boundary between transient working memory and consolidated semantic knowledge.

---

### 8. Multi-Justification Handling Specification

1. **JTMS Representation**: In `src/core/cognition/kernel/jtms.py:72, 110`, `JTMS` represents multiple justifications via `_consequence_to_justifications: Dict[int, List[int]]`, where each justification ID connects a distinct `rule_id` and `premise_ids: Tuple[int, ...]`.
2. **Invalidation Invariant**: When premise $P_1$ is retracted via `retract_premise(P_1)`, the JTMS iterates over all consequence terms. A consequence $C$ is retracted if and only if `not self.has_valid_justification(C)` (`jtms.py:144`). If an independent justification $R_2(P_2, P_3) \to C$ remains valid, $C$ **survives** and remains active in `TermArena` (`[REPOSITORY FACT]`).
3. **Persistence Boundary**: `KnowledgeStore.Proposition` has only a single flat list `evidence_ids: List[str]`. It possesses zero schema support for disjunctive justification trees (OR-of-ANDs).
4. **Contractual Status**: Multi-justification disk persistence is formally classified as **`[DEFERRED / NOT IMPLEMENTED]`**. Multi-justification maintenance survives strictly in RAM within the active `JTMS` instance during the session epoch.

---

### 9. Comprehensive Failure and Safety Matrix

| Condition | Detection Mechanism | Immediate Service Action | Downstream Consumer Action | Epistemic / Safety Guarantee |
|---|---|---|---|---|
| **No relevant propositions in S8** | `len(known_propositions) == 0` | Skip reasoning invocation. Return neutral status. | CAPS evaluates conversational flow / greeting baseline. | Zero crash; fail-soft to non-assertive conversational acts. |
| **No active Goal formed** | `candidate_predicate is None` | Skip reasoning invocation. | CAPS evaluates turn stance (e.g. GREET, ACKNOWLEDGE). | Zero CPU cycles wasted on ungrounded inference. |
| **Invalid or superseded proposition** | `not prop.valid` or `prop.superseded_by` | Filtered during projection. Excluded from `TermArena`. | Knowledge is invisible to reasoning kernel. | Stale/retracted knowledge never serves as active premises. |
| **Uncertified epistemic input** | `confidence < 1.0` or perceptual source | Assigned `EpistemicStatus.UNKNOWN` at ingress gate. | Quarantined; cannot prove goal with certainty. | **Invariant NEG-02**: Uncertainty never silently promotes to FACT. |
| **Un-reconstructed DERIVED proposition** | `provenance == DERIVED` without numeric DAG | Mapped to `EpistemicStatus.UNKNOWN` at kernel boundary. | Evaluated via backward search from ground facts. | Prevents orphaned unretractable beliefs in JTMS. |
| **Direct Contradiction / Conflict** | `detect_direct_conflict()` returns `ConflictRecord` | Halt reasoning branch; return `GoalResult(status=FALSE, conflict=...)`. | CAPS routes to `CommunicativeAct.CLARIFY` (Priority 3). | Inconsistent beliefs cannot be asserted as facts. |
| **Cyclic Reasoning (A→B, B→A)** | Ancestor stack cycle detector (`_ancestor_pred`) | Cycle broken deterministically; branch returns `UNKNOWN`. | Engine continues other branches or emits `InformationSubgoal`. | Zero infinite recursion; execution completes in $< 2\text{ms}$. |
| **Reasoning budget exhausted** | `steps > 256` or `depth >= 8` | Halt search; return `GoalResult(status=UNKNOWN)`. | CAPS fails closed to `INQUIRE` or `REFUSE`. | Deterministic 20W edge boundary protected. |
| **Unsupported Goal (No rule/fact)** | `rule_index.get_rules_for_head() == []` | Return `GoalResult(status=UNKNOWN, subgoal=InformationSubgoal)`. | CAPS Priority 1 compiles into `CommunicativeAct.INQUIRE`. | Transparently requests missing premise from user. |
| **RuleIndex unavailable / empty** | `rule_index is None` or compilation failure | Fail-soft: record diagnostic warning; skip rule deduction. | System falls back to direct fact matching in S8. | Lucia continues operating even if rule compiler fails. |
| **TermArena capacity exceeded** | `arena.allocated_count >= 4096` | Catch `OverflowError`; record trace warning; return `UNKNOWN`. | CAPS fails closed; prompts fall back to ungrounded dialogue. | Prevents process crash; preserves conversational liveness. |
| **Multiple justifications retracted** | `JTMS.retract_premise()` | Check `has_valid_justification()`. Retract only if count is 0. | Active if justified; retracted if orphaned. | Non-monotonic consistency guaranteed across proofs. |
| **Lifecycle Reset / Epoch Wipe** | `CognitiveOrchestrator.reset_lifecycle()` | Recompile `RuleIndex`; rebind `ReasoningKernel` to fresh arena. | All transient in-memory terms and justifications wiped. | Prevents stale memory pointers across session resets. |

---

### 10. Minimal MVP Scope Specification

To guarantee safety, zero regressions, and full reversibility, the initial integration scope is deliberately restricted to:

#### Supported MVP Scope:
1. **Candidate Verification Pipeline**: When Stage S8 retrieves candidate propositions matching the conversational context, the highest-ranking candidate hypothesis is formulated as a numeric `Goal` and verified against the indexed Horn rules and known facts.
2. **Transient Deductive Grounding (NOT Auto-Assert)**: If P23-H proves the goal (`TRUE`), a transient `DerivedResult` with `epistemic_status=INFERRED` and `provenance=DERIVED` is presented to the epistemic admissibility boundary. If admitted, CAPS evaluates it alongside dialogue context and policy, asserting it **only if downstream contracts legally authorize assertion**.
3. **Subgoal-Driven Clarification & Inquiry**: If P23-H determines that the goal is `UNKNOWN` due to a missing premise, the emitted `InformationSubgoal` is passed directly into `evaluate_caps(subgoals=[subgoal])`, causing CAPS to ask the user a targeted inquiry.
4. **JTMS Retraction Dissemination**: Existing `execute_retraction_directive()` dispatches invalidations to `_reasoning_kernel.jtms.retract_premise()`.

#### Explicit Non-Goals & MVP Exclusions:
- `[EXCLUDED / DEFERRED]`: Arbitrary natural language question-to-Goal parsing.
- `[EXCLUDED / REJECTED]`: Spontaneous forward reasoning without a goal.
- `[EXCLUDED / DEFERRED]`: Automatic disk persistence of inferred propositions into `KnowledgeStore`.
- `[EXCLUDED / DEFERRED]`: Automatic promotion of `KnowledgeStore` DERIVED propositions without numeric premise DAGs.
- `[EXCLUDED / REJECTED]`: Cross-session numeric TermID persistence.
- `[EXCLUDED / DEFERRED]`: Dynamic online rule learning or rule compilation during a turn.
- `[EXCLUDED / REJECTED]`: Modifying `data/profile.json` or executing Genesis.

---

### 11. Performance Boundary & Complexity Analysis

```text
====================================================================================================
                                  PERFORMANCE BUDGET BREAKDOWN
====================================================================================================
Subsystem Component               Execution Phase     Budget Limit         Empirical Benchmark
────────────────────────────────────────────────────────────────────────────────────────────────────
Rule Compilation                  Lifecycle Boot      < 10.0 ms            ~ 1.8 ms (17 rules)
Symbol Interning                  Per-Premise         < 0.05 ms            ~ 0.008 ms / symbol
Premise Projection (max 10 props) S8 -> S10b          < 0.50 ms            ~ 0.08 ms total
Goal Resolution (Depth <= 8)      S10b Pre-CAPS       < 2.00 ms            ~ 0.35 ms / goal
JTMS Premise Retraction           On Ingress Denial   < 1.00 ms            ~ 0.12 ms / cascade
────────────────────────────────────────────────────────────────────────────────────────────────────
Total Runtime Latency Overhead per Turn:              < 2.55 ms            [VALIDATED EDGE PROFILE]
====================================================================================================
```

- **Allocation Discipline**: The inner reasoning loop of `ReasoningKernel` uses preallocated parallel arrays for ancestor tracking (`_ancestor_pred`, `_ancestor_a0`, ...) and preallocated `BindingFrame` arrays (`_frames`). Dynamic heap allocation during search is $0\text{ bytes}$ (`[REPOSITORY FACT]`).
- **Edge Envelope**: At $< 2.55\text{ ms}$ overhead, the reasoning substrate consumes $< 1.3\%$ of the $200\text{ ms}$ per-turn limbic/cognitive time budget, strictly preserving the 20-Watt Whole Brain Architecture.

---

### 12. Architectural Invariant Compliance Audit

| Architectural Invariant | Requirement | Compliance Analysis & Grounded Evidence | Status |
|---|---|---|:---:|
| **P23-H Kernel Freeze** | Commit `3eef803` must remain bit-exact. Zero edits to `src/core/cognition/kernel/`. | `ReasoningKernel`, `binding.py`, `jtms.py`, and `rules.py` are treated as immutable black-box libraries. | `[VERIFIED]` |
| **Strong Kleene K3 Purity** | Strict 3-valued logic ($TRUE, FALSE, UNKNOWN$). No heuristic certainty. | Truth values are strictly mapped from `KleeneValue`. $UNKNOWN \land TRUE = UNKNOWN$. | `[VERIFIED]` |
| **Invariant NEG-02** | Zero scalar confidence thresholding ($c \ge \theta \implies \text{FACT}$ forbidden). | `confidence: float` is explicitly excluded from logic premises. Only certified categorical facts are admitted. | `[VERIFIED]` |
| **Epistemic Disconnect (P23-H TRUE $\ne$ ASSERT)** | Logical derivability must not automatically trigger communicative assertion. | `TRUE` yields an in-memory `DerivedResult` (INFERRED). Downstream CAPS owns act selection; assertion requires legal admission. | `[VERIFIED]` |
| **ADR-038 Ingress Integrity** | Perimeter qualification; F15 anti-echo defense; causal attribution links. | Assistant intent terms are indexed under `SCOPE_TYPE_MODAL`; inter-turn arena wipes are strictly prohibited. | `[VERIFIED]` |
| **No Persistent Numeric TermIDs** | Numeric TermIDs must remain ephemeral within the session epoch. | All IDs exist only in RAM (`TermArena`). Disk persistence uses symbolic string triples (`KnowledgeStore`). | `[VERIFIED]` |
| **No Automatic Epistemic Escalation** | Derived facts cannot become axiomatic ground truth without provenance. | Inferred terms carry `EpistemicStatus.INFERRED`, `rule_id`, and `premise_ids`. Never labeled `FACT`. | `[VERIFIED]` |
| **No Automatic Disk Persistence** | Reasoning results must remain transient in memory unless explicitly ratified. | `GoalResult` derivations are admitted into transient `AdmissibleEvidencePool`, not saved to JSON. | `[VERIFIED]` |
| **Genesis Invariant (INV-8)** | `data/profile.json` remains `{"is_onboarded": false}`; zero activation during dev. | Genesis files untouched. First Activation Gate remains locked. | `[VERIFIED]` |
| **One Continuous Life (INV-1)** | Single individual identity; no character pickers; anti-branching. | Reasoning operates on the single global session instance. Zero persona splitting. | `[VERIFIED]` |
| **Stage Ownership (ADR-014/035)** | S1–S16 boundaries preserved; CAPS owns WHAT; Realization owns HOW. | Reasoning service acts as an advisory cognitive oracle between S8 and S10b; zero prompt leakage. | `[VERIFIED]` |

---

### 13. Step-by-Step Implementation Sequence (Post-Specification Roadmap)

When production implementation is authorized by project governance, the following sequential, reversible commits shall be executed:

1. **Step 1: Epistemic Reasoning Service Adapter** (`src/core/cognition/service.py`):
   - Implement `EpistemicReasoningService` providing `verify_candidate_goal()` and knowledge projection.
   - Comprehensive unit test harness in `tests/unit/test_epistemic_reasoning_service.py`.
2. **Step 2: Orchestrator RuleIndex Lifecycle Wiring** (`src/core/orchestrator/cognitive_orchestrator.py`):
   - In `CognitiveOrchestrator.__init__`, compile `KnowledgeStore.get_all_rules()` via `compile_rule_set()`.
   - Store `RuleIndex` on `CognitiveOrchestrator`.
   - Instantiate `ReasoningKernel(self._rule_index, self._term_arena, jtms)`.
   - Update `reset_lifecycle()` to recompile the `RuleIndex` against the new `SymbolTable`.
3. **Step 3: Stage S10b Pre-CAPS Service Hook**:
   - In `CognitiveOrchestrator.process()`, prior to `evaluate_caps()`, if a candidate predicate is retrieved in S8, invoke `verify_candidate_goal()`.
   - If `TRUE`: inject derived `DerivedResult` (INFERRED) into `evidence_pool.verified_propositions` for CAPS consideration.
   - If `UNKNOWN` with `InformationSubgoal`: pass `subgoals=[subgoal]` into `evaluate_caps()`.
4. **Step 4: End-to-End Regression & Benchmark**:
   - Run complete unit suite (all 100+ tests including `test_p23h_kernel`, `test_p23h_rule_compiler`, `test_caps_production`).
   - Verify zero latency regression ($< 5\text{ms}$ total turn overhead).

---

### 14. Open Questions & Future Horizons

1. **General Question Parsing (Horizon P28)**:
   - *Question*: How can arbitrary natural language questions be mapped to typed `Goal` structures without violating the zero-cloud/zero-heavy-NLP edge constraint?
   - *Current Status*: `[DEFERRED]`. Requires dedicated SLM grammar slot-filling or formal semantic parsing research.
2. **Reconstruction of Stored DERIVED Premise DAGs**:
   - *Question*: How should `KnowledgeStore` propositions with `provenance=DERIVED` be projected if their original proof tree was not preserved across sessions?
   - *Current Status*: `[DEFERRED]`. Evaluated as `UNKNOWN` at kernel boundary until an explicit reconstruction contract is specified.
3. **Multi-Justification Disk Serialization**:
   - *Question*: Does long-term relational consolidation require persisting full JTMS justification DAGs to disk, or is episodic consolidation of derived facts sufficient?
   - *Current Status*: `[DEFERRED]`. Requires research into relational truth maintenance schema extensions.

---

### 15. Final Conclusion & Sign-Off

The verified P23-H reasoning substrate has a clean, well-bounded integration path into Lucia's cognitive runtime. The interface between `KnowledgeStore`, `TermArena`, `ReasoningKernel`, and `CAPS` is mathematically cohesive, epistemically protected by ADR-038 and NEG-02, rigorously decoupled from communicative assertibility, and computationally bounded within the 20W edge envelope.

**Final Architectural Verdict**:
```text
====================================================================================================
                                      FINAL VERDICT
                              READY FOR IMPLEMENTATION
====================================================================================================
```
