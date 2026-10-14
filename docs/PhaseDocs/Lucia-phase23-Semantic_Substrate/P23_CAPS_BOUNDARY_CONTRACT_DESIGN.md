# P23 — CAPS Boundary Contract Design

> **Document Type:** Research & Architecture Contract Specification  
> **Status:** `[PROPOSED ARCHITECTURAL CONTRACT / READY FOR ARCHITECTURAL REVIEW]`  
> **Target Horizon:** Post-P23 / Pre-Activation Zero-LLM/SLM Runtime Architecture  
> **Execution Mode:** Read-Only Design • Zero Production Modifications (`src/core/**` diff = 0) • Genesis Locked (`data/profile.json` bit-exact `{"is_onboarded": false}`)  
> **Evidence Standard:** E0 (Unobserved) → E1 (Documentary) → E2 (Static Implementation) → E3 (Execution Verified) → E4 (Reproducible Empirical)

---

## 1. Executive Summary

In [`P23_CAPS_IDENTIFICATION_AND_CONTRACT_INVESTIGATION.md`](file:///c:/Users/Lunafiah/Desktop/My_project/Lucia/docs/PhaseDocs/Lucia-phase23-Semantic_Substrate/P23_CAPS_IDENTIFICATION_AND_CONTRACT_INVESTIGATION.md), forensic analysis established the definitive architectural verdict:

> **CAPS BOUNDARY JUSTIFIED — Confidence: HIGH**

That investigation demonstrated that while Lucia's internal cognitive core (coupled MT-LNN affect ODE, homeostatic drives, Kanerva SDM associative memory, relational updates, and deductive reasoning) is already **100% token-free**, and downstream deterministic language drivers can realize surface text in **0.0085 ms** with **0.0 MB GPU VRAM**, **zero existing components in the production runtime currently decide what proposition Lucia communicates**. Currently, Stage 13 of [`CognitiveOrchestrator.process()`](file:///c:/Users/Lunafiah/Desktop/My_project/Lucia/src/core/orchestrator/cognitive_orchestrator.py#L568-L577) delegates both semantic decision ("What to Say": communicative act & proposition selection) and surface realization ("How to Say It": lexicalization, syntax, and morphology) to an autoregressive SLM (`LLMBackend` / `llama_cpp`).

The investigation further established that **CAPS is a functional boundary contract, NOT a new monolithic subsystem**. Creating a centralized `CAPSManager` or `CAPSEngine` would arbitrarily duplicate reasoning, memory retrieval, policy evaluation, and expression adaptation.

### Purpose of this Revised Specification

This revised document defines the formal, implementation-neutral **CAPS Boundary Contract**. Incorporating architectural review findings, it strictly enforces:
1. **Purity of the Semantic Boundary:** Language choice, egress gating, and surface syntax are classified as downstream transport/egress concerns and are **completely excluded** from the language-independent semantic CAPS contract.
2. **Downstream Isolation of P24 Expression Adaptation:** CAPS does not own `ExpressionState`, acoustic prosody, facial blendshapes, or affective adaptation. P24 operates downstream of CAPS.
3. **Rigorous Input Scoping:** Transient actuation variables (such as `pacing_delay_ms`) are removed from CAPS inputs, retaining strictly the information necessary to determine communicative acts, proposition construction, grounding, and epistemic evaluation.
4. **Scoped Determinism:** Scopes determinism strictly to the **CAPS transformation** given a frozen input snapshot, avoiding over-generalized system-wide claims.
5. **Enforceable Grounding Invariant:** Replaces absolute "zero hallucination" claims with the enforceable invariant: *CAPS SHALL NOT emit an ASSERT/ANSWER proposition as an asserted claim unless the proposition has admissible grounding.*
6. **Separation of Provenance Source from Epistemic Truth:** Establishes that user assertions (`USER_SESSION_ASSERTION`) function as grounding provenance, but do not automatically grant epistemic `FACT` status.

---

## 2. Governance

This specification adheres strictly to project governance mandated in [`AGENTS.md`](file:///c:/Users/Lunafiah/Desktop/My_project/Lucia/AGENTS.md) and [`L1_INVARIANTS.md`](file:///c:/Users/Lunafiah/Desktop/My_project/Lucia/docs/L1_INVARIANTS.md):

- **Research / Architecture-Contract Design Only:** This document is an architectural contract proposal. It does **not** authorize production code modification (`src/core/**`, `electron/**`, `data/**`).
- **Genesis Lock Invariant (INV-8):** Genesis Onboarding gate remains bit-exact:
  ```json
  {"is_onboarded": false}
  ```
  `data/genesis_commitment.json` does not exist (`False`). First Activation remains locked.
- **No Premature Implementation:** No new classes (`CAPSManager`, `CAPSEngine`, `DialogueActPolicy`, `GraphCompiler`) are created. No runtime imports, interfaces, or unit tests executing production code are added.
- **Zero Phase / ADR Mutation:** No new canonical roadmap phase (e.g. P23-J) is created. `PHASE_REGISTRY.md` remains unchanged.
- **Target Invariant:** The long-term architectural target remains absolute: **eventual complete elimination of the runtime LLM/SLM dependency** ($\text{SLM Dependency} = 0$, $\text{LLM Dependency} = 0$). This document specifies an architectural stepping stone, not a claim that zero-SLM runtime has already been achieved.

---

## 3. Evidence Baseline

All contractual definitions are grounded upon established repository evidence:

| Aspect | Established Reality (Repository Evidence) | Non-Claims & Explicit Boundaries |
|---|---|---|
| **Cognitive Core** | Internal state transitions (PAD ODE, somatic markers, SDM ecphory, relationship updates) execute entirely on continuous vectors with zero tokens (**E3/E4**). | Does not claim cognition currently autonomously emits outgoing speech acts. |
| **Surface Realization** | Deterministic language drivers realize text from `SemanticGraph` in **0.0085 ms** on local CPU with 0.0 MB VRAM (**E4**). | Does not claim drivers currently have open-vocabulary coverage beyond canonical benchmark frames. |
| **Propositional Substrate** | `SemanticGraph` formally represents nodes, relations, 4 epistemic states, and logical scopes (**E3**). | Does not claim `SemanticGraph` currently contains dialogue act headers. |
| **Pragmatic Modulation** | `CommunicationPolicy` computes 10D $C_t$ via closed-form linear algebra (**E3**). | Does not claim `CommunicationPolicy` generates proposition content. |
| **Deductive Reasoning** | `ReasoningKernel` performs bounded Strong Kleene backward chaining over integer terms (**E3**). | Does not claim `ReasoningKernel` currently executes on the production `/chat` loop. |

---

## 4. Architectural Boundary

The CAPS contract defines the precise boundary separating **Internal Cognition**, **Semantic Communication**, **P24 Expression Adaptation**, and **Language Realization**:

```text
┌────────────────────────────────────────────────────────────────────────┐
│                        COGNITIVE DOMAIN                                │
│  • EmotionCore: Coupled MT-LNN ODE (PAD continuous vector)             │
│  • HomeostaticEngine: Somatic markers (stability, load, energy, tension)│
│  • RelationshipUpdater: Relational state R_t (familiarity, trust, etc.) │
│  • EcphoryEngine: Associative memory recall (echo vector, r_slow)       │
│  • KnowledgeStore: Factual proposition repository & keyword indexing    │
│  • ReasoningKernel: Goal-directed Strong Kleene deduction & subgoals    │
│  • CommunicationPolicy: 10D Pragmatic modulation vector C_t             │
└───────────────────────────────────┬────────────────────────────────────┘
                                    │
                         CAPS BOUNDARY CONTRACT
                                    │
                                    ▼
┌────────────────────────────────────────────────────────────────────────┐
│                        CAPS OUTPUT PAYLOAD                             │
│  (Language-Independent Semantic & Grounding Representation)            │
│  • Communicative Act                                                   │
│  • Grounded SemanticGraph / Proposition Payload                        │
│  • Epistemic Status (FACT | INFERRED | AMBIGUOUS | UNKNOWN)            │
│  • Provenance / Grounding Metadata                                     │
│  • Semantic Constraints (derived from C_t for downstream modulation)   │
└───────────────────────────────────┬────────────────────────────────────┘
                                    │
                                    ▼
┌────────────────────────────────────────────────────────────────────────┐
│               P24 AFFECTIVE EXPRESSION ADAPTATION                      │
│  • ExpressionPolicy: Computes Multimodal ExpressionState E_t           │
│    (Voice prosody: pitch, rate, pause; Facial blendshapes: smile, etc.)│
└───────────────────────────────────┬────────────────────────────────────┘
                                    │
                                    ▼
┌────────────────────────────────────────────────────────────────────────┐
│                 LANGUAGE EGRESS & SURFACE REALIZATION                  │
│  • LanguageEgressGate: Perimeter firewall admitting {en, vi, ja}        │
│  • Deterministic Language Drivers: SVO/SOV, morphology, kinship, keigo  │
│  • BoundaryLayer: Pre-reflective regex audit (INV-2 validation)         │
│  • Multimodal Actuation: Text feed, Edge-TTS audio, avatar blendshapes  │
└────────────────────────────────────────────────────────────────────────┘
```

---

## 5. Responsibilities

The functional scope of the CAPS boundary contract is strictly delineated:

1. **Communicative Act Declaration:** Identifies the high-level functional purpose of the turn (`ASSERT`, `ANSWER`, `INQUIRE`, `CLARIFY`, `ACKNOWLEDGE`, `GREET`, `FAREWELL`, `REFUSE`).
2. **Proposition Formulation:** Assembles the language-independent conceptual payload (`predicate_symbol`, typed argument roles `:ARG0`, `:ARG1`, logical polarity, and modal attitude).
3. **SemanticGraph Packaging:** Compiles the proposition into an immutable, validated `SemanticGraph` conforming to P23-E Fortification invariants.
4. **Epistemic Commitment Auditing:** Evaluates the certainty level (`FACT`, `INFERRED`, `AMBIGUOUS`, `UNKNOWN`) and enforces that unverified assumptions are never promoted to factual claims.
5. **Provenance Chain Attachment:** Attaches explicit derivation and grounding metadata (`rule_id`, `premise_ids`, source identifiers, session timestamps) to every emitted proposition node.
6. **Semantic Constraint Forwarding:** Extracts semantic realization constraints (directness, elaboration guidance, formality targets) derived from $C_t$ to guide downstream drivers.

---

## 6. Non-Responsibilities

To preserve modularity and prevent architectural bloat, CAPS explicitly **does NOT own**:

- **Affect / Homeostasis:** CAPS does not own, compute, or mutate emotional states. `EmotionCore` and `HomeostaticEngine` own affect dynamics.
- **Relational Dynamics:** CAPS does not own, update, or store relational bonds. `RelationshipUpdater` owns $R_t$.
- **Memory Storage & Indexing:** CAPS is not a secondary memory database. `KnowledgeStore` and `EcphoryEngine` own memory persistence and retrieval.
- **Deductive Inference Execution:** CAPS does not perform backward-chaining proof search. `ReasoningKernel` owns formal theorem proving.
- **Multimodal Expression State ($E_t$):** CAPS does not generate voice prosody parameters (pitch shift, speech rate, pause duration) or facial blendshapes (smile, brow angle). P24 `ExpressionPolicy` owns multimodal expression adaptation.
- **Language Selection / Egress Gating:** CAPS contains zero knowledge of target natural languages. Target language hints and admittance checks belong to transport/egress session configuration (`LanguageEgressGate`).
- **Surface Realization:** CAPS contains zero vocabulary strings, inflection tables, or syntax rules. Downstream drivers (`EnglishLanguageDriver`, etc.) own natural language realization.
- **Reward / Engagement Optimization:** CAPS contains zero scalar rewards, user-retention heuristics, or clickbait mechanisms.

---

## 7. Provisional Communicative-Act Taxonomy

To replace the SLM's unconstrained generation without losing conversational utility, the contract defines a **provisional minimal taxonomy for architectural validation**:

```text
CommunicativeAct (PROVISIONAL MINIMAL TAXONOMY)
├── ASSERT       : State a verified fact, internal state, or derived inference
├── ANSWER       : Provide a direct propositional response satisfying an inquiry
├── INQUIRE      : Solicit missing information when reasoning halts at UNKNOWN
├── CLARIFY      : Request user disambiguation between divergent hypotheses
├── ACKNOWLEDGE  : Confirm receipt, attend, or provide grounded active listening
├── GREET        : Initiate interaction / conversational contact
├── FAREWELL     : Conclude interaction / conversational parting
└── REFUSE       : Explicitly reject an action that violates an architectural invariant
```

### Rationale & Functional Scope

| Act Class | Distinct Pragmatic Function | Surface Realization Consequence | Grounding Prerequisite |
|---|---|---|---|
| **`ASSERT`** | Proactively communicates a verified fact or cognitive status. | Declarative sentence structure (indicative mood). | Requires verified `ProvenanceRecord` in `KnowledgeStore` or internal state. |
| **`ANSWER`** | Directly answers a user query turn. | Focused responsive proposition resolving the user's question. | Requires direct alignment with query referent. |
| **`INQUIRE`** | Solicits missing data when an epistemic gap halts deduction. | Interrogative question syntax (wh-question or polar question). | Triggered exclusively by `InformationSubgoal` under `EpistemicState.UNKNOWN`. |
| **`CLARIFY`** | Resolves ambiguous referents or divergent rule paths. | Disambiguation query listing alternative referent hypotheses. | Triggered exclusively by `DisambiguationSubgoal` under `EpistemicState.AMBIGUOUS`. |
| **`ACKNOWLEDGE`**| Signals active listening, grounding, or receipt confirmation. | Short grounded feedback (*"Understood"*, *"I see"*). | Triggered when cognitive processing succeeds without asserting new facts. |
| **`GREET`** | Establishes conversational contact. | Phatic opening matching relational familiarity ($R_t$). | Triggered by session initiation / arrival. |
| **`FAREWELL`** | Concludes conversational contact. | Phatic closing matching relational closeness ($R_t$). | Triggered by session end request. |
| **`REFUSE`** | Refuses an invalid request (e.g. Genesis trigger, reflective prompt).| Firm, polite boundary statement without introspection. | Triggered by boundary layer / invariant violation detection. |

*Taxonomy Status:* **PROVISIONAL FOR VALIDATION**. This taxonomy is **NOT** claimed to be proven complete, minimal, or permanently closed. It represents the smallest defensible set required to validate non-generative companion interaction. All ungrounded, theatrical, or creative roleplay acts (e.g. `JOKE`, `STORY`, `DEBATE`, `ROLEPLAY`) are explicitly excluded from the product contract.

---

## 8. Proposition & SemanticGraph Contract

The proposition contract defines the minimal semantic payload representing *what* Lucia communicates. It is strictly non-lexical and language-independent.

### Formal Proposition Schema (Pseudostructure)

```text
PropositionPayload
├── predicate_symbol     : ConceptSymbol        [REQUIRED]  (e.g. c:SOLVE_PROBLEM, c:ASSIST, c:STATUS)
├── argument_bindings    : Map<Role, EntityID>  [REQUIRED]  (e.g. :ARG0 -> ent:lucia, :ARG1 -> ent:task_01)
├── polarity             : Boolean              [REQUIRED]  (True = asserted, False = negated)
├── modality             : ModalityType         [REQUIRED]  (ACTUAL | POSSIBLE | OBLIGATORY | PERMISSIBLE)
├── temporal_anchor      : TemporalScope        [REQUIRED]  (PAST | PRESENT | FUTURE | PERSISTENT)
├── epistemic_status     : EpistemicState       [REQUIRED]  (FACT | INFERRED | AMBIGUOUS | UNKNOWN)
├── provenance           : ProvenanceRecord     [REQUIRED]  (rule_id, premise_ids, source_id, timestamp)
├── certainty_score      : Float [0.0, 1.0]     [OPTIONAL]  (Degree of deductive/associative confidence)
└── focus_topic          : ConceptSymbol        [OPTIONAL]  (Information structure: topic/comment distinction)
```

### SemanticGraph Relationship (Option B)

CAPS emits an abstract `CommunicativeIntent` record containing act metadata and an embedded, fully compliant `SemanticGraph`:

$$\text{CommunicativeIntent} = \langle \text{Act}, \mathcal{G}_{\text{semantic}}, \mathcal{E}_{\text{epistemic}}, \Pi_{\text{provenance}}, \mathcal{S}_{\text{constraints}} \rangle$$

Where:
- $\text{Act} \in \text{CommunicativeAct}$
- $\mathcal{G}_{\text{semantic}} \in \text{SemanticGraph}$ (Language-independent concept topology satisfying P23-E Fortification invariants)
- $\mathcal{E}_{\text{epistemic}} \in \text{EpistemicState}$
- $\Pi_{\text{provenance}} \in \text{ProvenanceRecord}$
- $\mathcal{S}_{\text{constraints}}$ represents semantic constraints derived from $C_t$ (directness, formality, elaboration) for downstream driver realization.

*Critical Invariant:* `CommunicativeIntent` contains **zero** language codes (`target_language_hint`) and **zero** multimodal actuation states (`ExpressionState`).

---

## 9. Grounding and Provenance Contract

### Enforceable Grounding Invariant

Rather than relying on vague, system-level "zero hallucination" claims, the contract establishes an exact, testable invariant:

> **Grounding Invariant:**  
> **CAPS SHALL NOT emit an ASSERT or ANSWER proposition as an asserted claim unless the proposition has admissible grounding.**

### Admissible Grounding Sources

Every asserted node in `SemanticGraph` must trace directly to an admissible grounding source:

```text
GroundingSource
├── CURRENT_COGNITIVE_STATE : Direct reflection of internal PAD/Somatic/Relational vectors
├── VERIFIED_KNOWLEDGE      : Stored proposition in KnowledgeStore with valid=True
├── EPISODIC_TRACE          : Associative trace verified in Kanerva SDM memory
├── DEDUCTIVE_INFERENCE     : Logical lemma derived by ReasoningKernel with valid rule_id & premises
└── USER_SESSION_ASSERTION  : Proposition asserted by the user during the current interaction
```

### Separation of User Assertion from Epistemic Truth

A critical architectural distinction is enforced:

$$\text{Provenance / Source} \neq \text{Epistemic Truth Status}$$

1. **User Assertion is a Provenance Source:** Information provided by the user is recorded with source `USER_SESSION_ASSERTION`.
2. **User Assertion is NOT Automatically `FACT`:** When the user asserts a statement (e.g. *"The server crashed yesterday"*), it functions as an admissible grounding source for dialogue continuation, but it **must NOT** be automatically marked as an established epistemic `FACT` in persistent knowledge.
3. **Epistemic Classification:** Propositions grounded solely in user statements must be classified as `INFERRED` (contextual belief) or retain explicit user attribution metadata, preventing unverified user claims from contaminating Lucia's ground-truth knowledge base.

---

## 10. Epistemic Status Contract

The contract incorporates the 4-state epistemic classification established in P23-E (`src/core/knowledge/fortification.py`):

```text
EpistemicState
├── FACT      : Ground-truth verified fact or direct physiological state.
├── INFERRED  : Derived knowledge with explicit derivation rule_id and supporting premise links.
├── AMBIGUOUS : Multiple divergent hypotheses exist. Must NOT be prematurely resolved.
└── UNKNOWN   : Ungrounded or missing entity. Must NEVER be promoted to certainty.
```

### Epistemic Safety Rules

1. **Non-Escalation Invariant:** Downstream drivers are strictly prohibited from verbalizing an `INFERRED` node as an absolute fact, or an `UNKNOWN` node as a known entity.
2. **Ambiguity Preservation:** When `AMBIGUOUS` is present, the downstream driver must realize an explicit clarifying alternative (e.g. *"bank (financial institution or river bank)"*), rather than guessing.
3. **Impersonal / Passive Guard:** When `:ARG0` is `UNKNOWN`, the driver must realize via zero-anaphora (Japanese) or passive voice (English: *"The problem was solved"*).

---

## 11. Dialogue Context & Reference Handling

Pronouns and referents (*"it"*, *"that"*, *"he"*, *"she"*) are handled **symbolically at the concept level**, avoiding surface-word ambiguity:

1. **Symbolic Entity Tracking:** Salient entities in recent turns are assigned persistent symbolic identifiers (`ent:user`, `ent:lucia`, `ent:task_01`).
2. **Language-Independent Bindings:** CAPS argument bindings reference exact `EntityID` symbols:
   $$\text{SemanticEdge}(:ARG1 \to \text{ent:task_01})$$
3. **Downstream Realization Handoff:** Language drivers determine surface pronominalization based on typological rules:
   - *Japanese Driver:* Drops the referent completely via zero-anaphora.
   - *English Driver:* Realizes *"it"* if referenced in the immediately preceding turn; otherwise realizes *"the task"*.
   - *Vietnamese Driver:* Realizes an appropriate kinship term or classifier noun phrase.

---

## 12. Novel Proposition & Composition Boundary

Can Lucia communicate novel propositions that were never pre-authored in templates?

### Compositional Expressibility vs. Autonomous Demonstration

1. **Technically Expressible & Permitted:** Novel propositions are formed deterministically through typed relational graph unification:
   $$\mathcal{C} \times \mathcal{R} \times \mathcal{C} \implies \mathcal{E}$$
   Given an extensible vocabulary of verified concept symbols $\mathcal{C}$ (e.g. `c:BACKUP`, `c:COMPLETE`, `ent:database`) and typed relational roles $\mathcal{R}$ (`:ARG0`, `:ARG1`, `:time`), CAPS composes a novel `SemanticGraph` through typed role assignment.
2. **Empirical Boundary (Strict Governance):** While the architecture contract **permits and defines** compositional novelty, Project Lucia **does NOT claim that autonomous novel proposition composition has been empirically demonstrated in production**. Demonstrating autonomous composition remains an active research question for future evaluation phases.

---

## 13. Determinism Contract

Rather than asserting ungrounded system-wide determinism, the determinism contract is rigorously scoped:

> **Determinism Invariant:**  
> **Given a fully specified, frozen input snapshot $\langle \text{Context}, \text{Cognition}, \text{Evidence}, \mathcal{S}_{\text{constraints}} \rangle$ and a fixed contract version, the CAPS transformation SHALL be deterministic: identical inputs SHALL produce identical outputs.**

*Clarification:* This is a mathematical property of the **CAPS transformation function**, not a claim that the entire Lucia runtime (which includes asynchronous sensory ingress and background ODE integration) is globally static or deterministic.

---

## 14. Failure & Fail-Closed Behavior

The contract defines explicit failure modes that prevent undefined runtime states:

```text
CAPS_FailureCode (CLOSED ENUM)
├── NO_COMMUNICATIVE_ACTION     : Deliberate listening / silence state (valid non-emission)
├── INSUFFICIENT_GROUNDING      : Proposition lacks admissible evidence (degrades to INQUIRE)
├── UNRESOLVED_AMBIGUITY        : Multiple conflicting referents (degrades to CLARIFY)
├── UNREPRESENTABLE_INTENT      : Concepts exceed current ontology (degrades to ACKNOWLEDGE)
└── INSUFFICIENT_CONTEXT        : Critical turn context missing (degrades to INQUIRE)
```

**Fail-Closed Invariant:** Under **no** circumstance does a failure code trigger an ungrounded generative fallback. When failure occurs, CAPS emits a bounded fallback act (`ACKNOWLEDGE` or `INQUIRE`) or deliberate silence (`NO_COMMUNICATIVE_ACTION`).

---

## 15. P24 Expression Adaptation & P25 Compatibility

The contract strictly respects existing and future phase boundaries:

- **P24 Compatibility (Affective Communication Adaptation):**  
  CAPS does **not** own or generate `ExpressionState`. CAPS emits language-independent semantic intent and constraint hints. P24 `ExpressionPolicy` operates downstream, evaluating multimodal prosody, speech rate, pause duration, and facial blendshapes based on $PAD$ and $C_t$.
- **P25 Compatibility (Temporal Embodiment & Relational Dynamics):**  
  CAPS consumes relational state $R_t$ as read-only context to inform formality and kinship guidance. CAPS **never** mutates $R_t$ or owns temporal embodiment.

---

## 16. Language Independence

Every field in the CAPS contract must satisfy the **Language Independence Test**:

> *"Could this field exist if English, Vietnamese, and Japanese did not exist?"*

- **Permitted Fields:** `ASSERT`, `INQUIRE`, `c:SOLVE_PROBLEM`, `ent:user`, `:ARG0`, `:ARG1`, `FACT`, `UNKNOWN`, `ACTUAL`, `PAST`, `directness: 0.75`.
- **Strictly Prohibited Fields:** Natural language strings (`"please"`), language-specific pronouns (`"you"`, `"anh"`), word order markers (`"SVO"`, `"SOV"`), grammatical particles (`"です"`, `"đã"`), and language selection codes (`target_language_hint`).

---

## 17. Candidate Boundary Contract Schema

```text
[PROPOSED / NOT YET IMPLEMENTATION-RATIFIED]

SCHEMA CAPS_Boundary_Contract_v0.2:

  INPUT:
    context: DialogueContextRecord {
      turn_id: UUID,
      session_id: UUID,
      salient_entities: List[SymbolID],
      active_subgoal: Optional[SubgoalID]
    }
    cognition: CognitiveStateSnapshot {
      pad: Vector3D,
      somatic: SomaticVector4D,
      relationship: RelationalVector4D
      # Note: pacing_delay_ms removed; actuation concern handled downstream
    }
    evidence: AdmissibleEvidenceBundle {
      retrieved_facts: List[Proposition],
      derived_theorems: List[GoalResult],
      memory_echo_active: Boolean
    }
    constraints: SemanticConstraintVector {
      directness: Float,
      formality: Float,
      supportiveness: Float,
      elaboration: Float,
      acknowledgement_level: Float,
      question_frequency: Float
    }

  PROCESSING GUARANTEES:
    - Pure function: Zero side-effects, zero state mutation.
    - Deterministic: Given frozen input snapshot -> identical output.
    - Grounded: Every asserted node linked to admissible evidence.

  OUTPUT:
    verdict: Success | Failure
    failure_code: Optional[CAPS_FailureCode]
    payload: Optional[CommunicativeIntent {
      act: CommunicativeAct,
      graph: SemanticGraph,
      epistemic_status: EpistemicState,
      provenance: ProvenanceRecord,
      semantic_constraints: SemanticConstraintVector
      # Note: target_language_hint and expression_state removed;
      # handled downstream by LanguageEgressGate and P24 ExpressionPolicy
    }]
```

---

## 18. Contract Invariants

When implemented, the CAPS boundary contract must strictly adhere to seven mandatory invariants:

- **INV-C1 (Absolute Language Independence):** The contract schema and intermediate representations must contain zero natural language tokens, word strings, language selection codes, or syntax markers.
- **INV-C2 (Compulsory Grounded Provenance):** CAPS SHALL NOT emit an ASSERT or ANSWER proposition as an asserted claim unless the proposition has admissible grounding.
- **INV-C3 (Zero State Ownership):** The contract boundary owns zero cognitive, affective, homeostatic, or relational state, and must never mutate upstream subsystems.
- **INV-C4 (Strict Realization Separation):** The contract terminates at the boundary of language-independent semantic representation. Surface syntax, word order, and morphology belong strictly downstream.
- **INV-C5 (Determinism of Transformation):** Given a fully specified, frozen input snapshot and fixed contract version, the CAPS transformation SHALL be deterministic.
- **INV-C6 (Fail-Closed Epistemic Safety):** Missing or ungrounded evidence must never trigger speculative assertion. The system must fail closed to `UNKNOWN`, `INQUIRE`, or silence.
- **INV-C7 (Zero Hidden Reward Optimization):** The contract must never incorporate scalar reinforcement rewards, engagement heuristics, or conversational clickbait optimization.

---

## 19. Future Validation Requirements

Before any production code implementing this contract may be merged, it must satisfy seven preregistered validation protocols:

1. **Structural Schema Validation:** 100% compliance with non-lexical symbols; automated linters verify zero string token leakage into contract payloads.
2. **Grounding Traceability Audit:** In a test suite of 500 assertions, 100% must trace to valid `ProvenanceRecord` IDs.
3. **Epistemic Invariant Verification:** When presented with incomplete facts, 100% of test cases correctly emit `INQUIRE` or `UNKNOWN` without promotion to certainty.
4. **Deterministic Reproducibility:** 1,000 parallel executions with identical inputs produce identical intent hashes.
5. **Compositional Novelty Test:** Successfully compose valid, novel semantic graphs from unseen combinations of valid vocabulary concepts.
6. **Cross-Lingual Realization Parity:** An identical `CommunicativeIntent` payload must successfully realize into valid English, Vietnamese, and Japanese via downstream drivers without payload modification.
7. **INV-2 Pre-Reflective Invariant Audit:** Zero introspective affect statements across all realized utterances.

---

## 20. Open Research Questions

1. **Subgoal-to-Inquire Compiler:** What is the exact mathematical mapping from `ReasoningKernel.InformationSubgoal` to an interrogative `SemanticGraph`?
2. **Turn-Level Discourse Cache:** What is the optimal storage window for `active_referents` to prevent unbounded memory growth in long sessions?
3. **Lexicon Expansion Priority:** Which 500 core companion concepts should be codified first in the non-lexical vocabulary registry?
4. **User Assertion Confidence Weighting:** How should conflicting user assertions over time be reconciled without overwriting ground-truth facts?

---

## 21. Non-Goals

This specification explicitly does **NOT** define:
- A new Python class hierarchy or production implementation.
- A new standalone background daemon or subsystem (`CAPSManager`).
- A natural language parser (ASR / NLU).
- A generative creative writing engine.
- A replacement for the production SLM in current builds.
- A modification to the Genesis Onboarding gate.

---

## 22. Final Decision

```text
═══════════════════════════════════════════════════════════════════════════════
                           ARCHITECTURAL DECISION:
                   CONTRACT READY FOR ARCHITECTURAL REVIEW
═══════════════════════════════════════════════════════════════════════════════
```

### Statement of Decision
The revised **CAPS Boundary Contract** is fully specified at the conceptual and interface level. It cleanly separates semantic decision from affective expression adaptation and language realization, eliminates the generative SLM from the critical semantic path, enforces strict grounding invariants, and preserves 100% edge compatibility. It is **READY FOR FORMAL ARCHITECTURAL REVIEW**.

---

## 23. Implementation Boundary & Final Governance Statement

> [!CAUTION]
> **FINAL GOVERNANCE STATEMENT**:  
> **This document defines a proposed architectural boundary contract only. It does NOT authorize implementation, production integration, SLM removal, Genesis modification, or First Activation. Any implementation requires a separate architectural review and explicit Human Owner authorization.**

The long-term architectural target remains unchanged:

```text
┌───────────────────────────────────────────────────────┐
│                   LUCIA RUNTIME                       │
│                                                       │
│  Cognitive Domain (ODE Affect, SDM, Reasoning)        │
│       ↓                                               │
│  CAPS Boundary Contract                               │
│       ↓                                               │
│  Language-Independent Semantic Representation         │
│       ↓                                               │
│  P24 Affective Expression Adaptation                  │
│       ↓                                               │
│  Deterministic Language Realization (EN, VI, JA)      │
│       ↓                                               │
│  Text / Voice / Avatar                                │
│                                                       │
│  ZERO LLM                                             │
│  ZERO SLM                                             │
│  ZERO token-generation dependency                    │
└───────────────────────────────────────────────────────┘
```
