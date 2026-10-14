# CAPS Implementation Contract & Technical Specification (Phase 23)

> **Document Type**: Technical Implementation Contract & Interface Specification  
> **Status**: [ARCHITECTURALLY RATIFIED] (Pre-Production Implementation Specification; Production Implementation NOT Authorized)  
> **Target Subsystem**: Communicative Act & Proposition Selection (CAPS Functional Boundary)  
> **Phase**: Phase 23 — Semantic Substrate & Non-Generative Communication  
> **Date**: 2026-10-14  
> **Author**: Antigravity (Lucia Architectural Copilot)  
> **Execution Governance**: Specification-Only (Strictly Zero Production Mutations, Zero Implementation Authorization)  

---

## 1. Scope & Governance Authority

### 1.1 Objective
This specification establishes the **formal implementation contract** for the Communicative Act & Proposition Selection (CAPS) boundary. It defines the exact input schemas, output data structures, transformation rules, grounding invariants, and fail-closed failure semantics necessary to transition CAPS from:

$$\mathbf{ARCHITECTURE\ APPROVED\ /\ IMPLEMENTATION\ GATED} \longrightarrow \mathbf{IMPLEMENTATION\ CONTRACT\ ARCHITECTURALLY\ RATIFIED\ (IMPLEMENTATION\ NOT\ AUTHORIZED)}$$

This document is a **specification-only artifact**. It does NOT authorize production code modifications, does NOT create a new subsystem class (`CAPSManager`), and does NOT remove the active SLM fallback.

### 1.2 Canonical Evidence Baseline
This contract directly synthesizes and strictly adheres to the following ratified and verified repository baselines:
1. [`docs/PhaseDocs/Lucia-phase23-Semantic_Substrate/P23_CAPS_BOUNDARY_CONTRACT_DESIGN.md`](file:///c:/Users/Lunafiah/Desktop/My_project/Lucia/docs/PhaseDocs/Lucia-phase23-Semantic_Substrate/P23_CAPS_BOUNDARY_CONTRACT_DESIGN.md) (`[ARCHITECTURALLY RATIFIED]`, decisions S1–S16).
2. [`docs/PhaseDocs/Lucia-phase23-Semantic_Substrate/evaluation/CAPS_IMPLEMENTATION_READINESS_GATE.md`](file:///c:/Users/Lunafiah/Desktop/My_project/Lucia/docs/PhaseDocs/Lucia-phase23-Semantic_Substrate/evaluation/CAPS_IMPLEMENTATION_READINESS_GATE.md) (`[COMPLETED / AUDIT RATIFIED]`, Gates R1, R2, R4 PASS; R3 identified as prerequisite).
3. [`docs/PhaseDocs/Lucia-phase23-Semantic_Substrate/evaluation/DISCOURSE_REFERENT_RETENTION_CONTRACT.md`](file:///c:/Users/Lunafiah/Desktop/My_project/Lucia/docs/PhaseDocs/Lucia-phase23-Semantic_Substrate/evaluation/DISCOURSE_REFERENT_RETENTION_CONTRACT.md) (`[ARCHITECTURALLY RATIFIED]`).
4. [`docs/PhaseDocs/Lucia-phase23-Semantic_Substrate/evaluation/DISCOURSE_REFERENT_RETENTION_RATIFICATION.md`](file:///c:/Users/Lunafiah/Desktop/My_project/Lucia/docs/PhaseDocs/Lucia-phase23-Semantic_Substrate/evaluation/DISCOURSE_REFERENT_RETENTION_RATIFICATION.md) (`[FORMALLY RATIFIED RECORD]`).
5. Canonical repository invariants: [`AGENTS.md`](file:///c:/Users/Lunafiah/Desktop/My_project/Lucia/AGENTS.md), [`docs/L1_INVARIANTS.md`](file:///c:/Users/Lunafiah/Desktop/My_project/Lucia/docs/L1_INVARIANTS.md).

### 1.3 Governance Invariants
- **No Production Mutation**: `src/core/**`, `electron/**`, and `data/**` diff MUST remain strictly **0**.
- **Genesis Lock Invariant**: [`data/profile.json`](file:///c:/Users/Lunafiah/Desktop/My_project/Lucia/data/profile.json) remains bit-exact `{"is_onboarded": false}`.
- **Functional Boundary, Not Monolith**: CAPS is a decoupled architectural transformation boundary, NOT a monolithic `CAPSManager` class.

---

## 2. Canonical CAPS Transformation

The CAPS functional contract specifies a bounded, deterministic, inspectable mapping from cognitive and discourse context into a grounded communicative output:

$$\mathbf{CAPS}\Big(\mathcal{D}_{\text{snap}},\; \mathcal{S}_{\text{cog}},\; \mathcal{E}_{\text{adm}},\; \mathcal{I}_{\text{sub}},\; \mathcal{P}_{\text{snap}},\; \mathcal{R}_{\text{disc}}\Big) \longrightarrow \Big(\mathcal{A}_{\text{comm}},\; \mathcal{G}_{\text{sem}},\; \mathcal{M}_{\text{epi}},\; \mathcal{M}_{\text{prov}},\; \mathcal{M}_{\text{adm}}\Big)$$

```text
┌─────────────────────────────────────────────────────────────────────────────┐
│                              CAPS BOUNDARY                                  │
├──────────────────────────────────────┬──────────────────────────────────────┤
│ INPUTS (Consumed from Cognitive Core)│ OUTPUTS (Emitted to Downstream Path) │
├──────────────────────────────────────┼──────────────────────────────────────┤
│ 1. Dialogue Context Snapshot         │ 1. Communicative Act                 │
│ 2. Cognitive State Snapshot          │ 2. Grounded SemanticGraph            │
│ 3. Admissible Evidence Pool          │ 3. Epistemic Metadata                │
│ 4. Active Information Subgoals       │ 4. Provenance Metadata               │
│ 5. Communication Policy Snapshot     │ 5. Resolution & Admissibility Metad. │
│ 6. Discourse Resolution Context      │                                      │
└──────────────────────────────────────┴──────────────────────────────────────┘
```

---

## 3. Input Contract Specifications

### 3.1 Dialogue Context Snapshot (`DialogueContextSnapshot`)
Provided by [`src/core/orchestrator/cognitive_orchestrator.py`](file:///c:/Users/Lunafiah/Desktop/My_project/Lucia/src/core/orchestrator/cognitive_orchestrator.py) turn coordination layer:
- `turn_id`: Monotonically increasing turn integer ($t \ge 1$).
- `active_referents`: Bounded dictionary of active discourse referents (`Dict[str, DiscourseReferent]`).
- `resolution_context`: Reference resolution outcome from Turn Ingress (`ResolutionStatus`, `candidate_entity_ids`).
- **Ownership Invariant**: CAPS **DOES NOT OWN** discourse memory. It consumes a frozen snapshot provided at turn execution.

### 3.2 Cognitive State Snapshot (`CognitiveStateSnapshot`)
Contains pre-reflective dynamical values necessary for communicative framing:
- `pad_vector`: Continuous 3D vector $(P \in [-1, 1], A \in [-1, 1], D \in [-1, 1])$ from [`EmotionCore`](file:///c:/Users/Lunafiah/Desktop/My_project/Lucia/src/core/emotion/core.py).
- `tension_level`: Internal cognitive tension / metabolic urgency $[0.0, 1.0]$.
- `relationship_bond`: Relational bond status (`philia`, trust, familiarity) from [`RelationshipUpdater`](file:///c:/Users/Lunafiah/Desktop/My_project/Lucia/src/core/relationship/updater.py).
- **Boundary Invariant**: CAPS is a consumer of cognitive state; it **DOES NOT OWN** or mutate limbic, homeostatic, or active inference ODEs.

### 3.3 Admissible Evidence Pool (`AdmissibleEvidencePool`)
Propositions retrieved from [`KnowledgeStore`](file:///c:/Users/Lunafiah/Desktop/My_project/Lucia/src/core/knowledge/store.py) or derived by [`ReasoningKernel`](file:///c:/Users/Lunafiah/Desktop/My_project/Lucia/src/core/cognition/kernel/engine.py):
- `evidence_id`: Canonical proposition identifier.
- `subject`: Canonical entity ID (e.g. `"ent:user"`).
- `predicate`: Canonical concept symbol (e.g. `"c:PREFERS"`).
- `object`: Entity or concept value (e.g. `"c:READING"`).
- `provenance`: Originating source enum (`VERIFIED`, `INFERRED`, `USER_STATED`, `OBSERVED`).
- `epistemic_state`: `EpistemicState` (`FACT`, `INFERRED`, `AMBIGUOUS`, `UNKNOWN`).
- `confidence`: Calibrated confidence score $[0.0, 1.0]$.
- **Invariance Rule**: $\mathbf{USER\_STATED\ provenance \neq FACT\ epistemic\ status}$.

### 3.4 Active Information Subgoals (`ActiveInformationSubgoals`)
Subgoals originating from [`ReasoningKernel`](file:///c:/Users/Lunafiah/Desktop/My_project/Lucia/src/core/cognition/kernel/engine.py#L75-L102):
- `target_predicate_id`: Concept symbol ID representing the unresolved relation.
- `known_arguments`: Dict mapping semantic roles to bound entity IDs (e.g. `{":ARG0": "ent:user"}`).
- `open_variable_role`: The semantic role of the missing argument slot to be queried (e.g. `":ARG1"`).
- `reason_code`: Numeric reason code (`INFO_REASON_MISSING_PREMISE`, `INFO_REASON_AMBIGUOUS_REFERENT`).

### 3.5 Communication Policy Snapshot (`CommunicationPolicySnapshot`)
High-level communicative framing constraints from [`CommunicationPolicy`](file:///c:/Users/Lunafiah/Desktop/My_project/Lucia/src/core/communication/policy.py):
- `verbosity_budget`: Maximum proposition depth / node count allowed for this turn.
- `inquiry_tendency`: Propensity to ask follow-up questions vs assert observations.
- **Boundary Invariant**: CAPS consumes communication constraints; downstream P24 owns final affective expression and surface pacing.

---

## 4. Output Contract Specifications

### 4.1 Communicative Act (`CommunicativeAct`)
Provisional closed taxonomy representing the illocutionary intent:

```python
class CommunicativeAct(str, Enum):
    """Provisional illocutionary act taxonomy for CAPS output."""
    ASSERT = "ASSERT"              # Asserting a grounded, verified proposition
    ANSWER = "ANSWER"              # Providing a grounded answer to user inquiry
    INQUIRE = "INQUIRE"            # Asking an information-seeking question (?X)
    CLARIFY = "CLARIFY"            # Requesting disambiguation among competing referents
    ACKNOWLEDGE = "ACKNOWLEDGE"    # Conversational receipt confirmation
    GREET = "GREET"                # Conversational opening
    FAREWELL = "FAREWELL"          # Conversational closing
    REFUSE = "REFUSE"              # Refusing to assert ungrounded / out-of-scope claim
```
*Governance Status*: `PROVISIONAL TAXONOMY`. It satisfies current benchmark scenarios but is not claimed to be a complete or universal speech act model.

### 4.2 Grounded SemanticGraph (`SemanticGraph`)
Language-independent discrete graph conforming to [`src/core/knowledge/fortification.py`](file:///c:/Users/Lunafiah/Desktop/My_project/Lucia/src/core/knowledge/fortification.py#L352-L400):
- `session_id`: Turn session identifier.
- `nodes`: Dict mapping node ID to `SemanticNode` (carrying `concept_symbol`, `epistemic_state`, `polarity`).
- `edges`: List of typed `SemanticEdge` (carrying `source_id`, `target_id`, `relation_role` such as `:ARG0`, `:ARG1`, `:mod`).
- `unbound_variables`: List of open query variables (e.g. `?X`) present when act is `INQUIRE` or `CLARIFY`.
- `grounding_linkage`: Exact proposition IDs and premise derivation IDs binding the graph to evidence.

### 4.3 Epistemic Metadata (`EpistemicMetadata`)
Independent epistemic status classification:
- `proposition_status`: Strictly one of `FACT`, `INFERRED`, `AMBIGUOUS`, `UNKNOWN`.
- `confidence`: Bounded numeric confidence $[0.0, 1.0]$.
- **Orthogonality Requirement**: Must NOT be conflated with Reference Resolution Status.

### 4.4 Provenance Metadata (`ProvenanceMetadata`)
Historical derivation and source attribution:
- `derivation_rule_id`: Identifier of inference rule utilized, or `None` if atomic premise.
- `source_subsystems`: Set of contributing subsystems (`KNOWLEDGE_STORE`, `REASONING_KERNEL`, `USER_STATED`).
- `timestamp`: Monotonic turn timestamp.

### 4.5 Resolution & Admissibility Metadata (`ResolutionAdmissibilityMetadata`)
Separation of verification layers:
- `reference_resolution_status`: `RESOLVED`, `AMBIGUOUS`, `UNKNOWN`, `TYPE_MISMATCH`.
- `evidence_admissibility`: `ADMISSIBLE`, `INADMISSIBLE_CONFIDENCE_BELOW_THRESHOLD`, `INADMISSIBLE_MISSING_PROVENANCE`.
- **Anti-Collapsing Invariant**: The contract strictly prohibits collapsing reference resolution, evidence admissibility, and epistemic certainty into a single heuristic score.

---

## 5. Grounding & Fail-Closed Contract

### 5.1 The Grounding Invariant
$$\mathbf{CAPS\ SHALL\ NOT\ emit\ ASSERT\ or\ ANSWER\ without\ Admissible\ Evidence}$$

An outgoing proposition $\mathcal{P}$ is **Admissible** for assertive emission if and only if:
1. $\text{confidence}(\mathcal{P}) \ge \theta_{\text{assert}}$ (where $\theta_{\text{assert}}$ is an uncalibrated threshold; see Open Implementation Question 9.5.3).
2. $\text{provenance}(\mathcal{P}) \in \{\text{VERIFIED}, \text{INFERRED}\}$.
3. $\text{epistemic\_state}(\mathcal{P}) \neq \text{UNKNOWN} \land \text{epistemic\_state}(\mathcal{P}) \neq \text{AMBIGUOUS}$.

If $\text{provenance}(\mathcal{P}) == \text{USER\_STATED}$, the proposition enters as an assertion attribution (e.g. *"You mentioned X"*), NOT as Lucia's own factual knowledge.

### 5.2 Fail-Closed Repair Matrix
When grounding is insufficient or referents are defective, CAPS strictly fails closed:

```text
┌─────────────────────────────────┬──────────────────────┬──────────────────────┬──────────────────────────────────────────────────┐
│ Ingress Defect / State          │ Admissibility Status │ Outgoing Act Emitted │ Outgoing SemanticGraph State                     │
├─────────────────────────────────┼──────────────────────┼──────────────────────┼──────────────────────────────────────────────────┤
│ Missing premise for goal        │ INADMISSIBLE         │ INQUIRE              │ Open variable node (?X) on missing slot.         │
├─────────────────────────────────┼──────────────────────┼──────────────────────┼──────────────────────────────────────────────────┤
│ Ambiguous referent (≥2 matches) │ INADMISSIBLE         │ CLARIFY              │ Disjunction of candidate nodes (?X: [e1, e2]).   │
├─────────────────────────────────┼──────────────────────┼──────────────────────┼──────────────────────────────────────────────────┤
│ Unresolved referent / Evicted   │ INADMISSIBLE         │ INQUIRE              │ Open variable node (?X); Epistemic = UNKNOWN.    │
├─────────────────────────────────┼──────────────────────┼──────────────────────┼──────────────────────────────────────────────────┤
│ Type mismatch on referent       │ INADMISSIBLE         │ INQUIRE              │ Open variable node (?X); candidate rejected.     │
├─────────────────────────────────┼──────────────────────┼──────────────────────┼──────────────────────────────────────────────────┤
│ Contradictory evidence in store │ INADMISSIBLE         │ CLARIFY              │ Explicit representation of conflicting branches. │
├─────────────────────────────────┼──────────────────────┼──────────────────────┼──────────────────────────────────────────────────┤
│ Confidence < threshold          │ INADMISSIBLE         │ REFUSE / INQUIRE     │ Refusal to assert or inquiry for confirmation.   │
└─────────────────────────────────┴──────────────────────┴──────────────────────┴──────────────────────────────────────────────────┘
```

---

## 6. Research Gate Integration Specifications

### 6.1 Gate R1: InformationSubgoal → INQUIRE Compiler
- **Mechanism**: The compiler consumes `InformationSubgoal` (`target_predicate_id`, `arg0_id`, etc.).
- **Semantic Role Mapping Convention**:
  - `arg0_id` maps to semantic role `:ARG0` (Subject / Agent).
  - `arg1_id` maps to semantic role `:ARG1` (Patient / Theme).
  - `arg2_id` maps to semantic role `:ARG2` (Recipient / Instrument).
  - *Open Slot Identification*: Whichever argument slot holds integer `0` (or unbound symbol) is assigned the open query variable `?X`.
- **Reason Code Routing**:
  - `INFO_REASON_MISSING_PREMISE` $\longrightarrow$ `CommunicativeAct.INQUIRE`.
  - `INFO_REASON_AMBIGUOUS_REFERENT` $\longrightarrow$ `CommunicativeAct.CLARIFY`.
- *Status*: `[VERIFIED BY ISOLATED BENCHMARK / CONTRACT SPECIFIED]`.

### 6.2 Gate R2: Grounded Outgoing SemanticGraph
- **Mechanism**: CAPS queries `KnowledgeStore` for propositions matching the predicate and known entity of the cognitive goal.
- **Binding Rule**: Selected proposition triples are mapped to `SemanticNode` and `SemanticEdge` with strict provenance linkages.
- **Deductive Chaining**: Forward/backward inference chaining via `ReasoningKernel` (JTMS / K3 logic) is supported.
- **Empirical Boundary Statement**:
  > **Novel proposition construction is technically expressible / architecturally permitted, but autonomous outgoing SemanticGraph construction has not yet been empirically demonstrated.**
- CAPS does NOT possess unconstrained creative generation; all outgoing propositions must be anchored in verified relations or formal derivations.
- *Status*: `[BOUNDED RETRIEVAL & BINDING VERIFIED / NOVEL AUTONOMOUS GENERATION NOT DEMONSTRATED]`.

### 6.3 Gate R3: Discourse Referent Retention Integration
- **Mechanism**: Formally integrates [`DISCOURSE_REFERENT_RETENTION_CONTRACT.md`](file:///c:/Users/Lunafiah/Desktop/My_project/Lucia/docs/PhaseDocs/Lucia-phase23-Semantic_Substrate/evaluation/DISCOURSE_REFERENT_RETENTION_CONTRACT.md).
- **Ownership**: Turn lifecycle coordinator (`CognitiveOrchestrator`). CAPS consumes active discourse context read-only at turn ingress and emits referent updates at turn egress.
- **Orthogonality Invariants**:
  $$\mathbf{RESOLVED \neq FACT}$$
  $$\mathbf{USER\_STATED\ provenance \neq FACT\ epistemic\ status}$$
- **Provisional Parameters**: Capacity $N_{\text{max}} = 16$, decay $\gamma = 0.60$, eviction threshold $\theta = 0.15$ remain provisional. Heap footprint $\le 2\text{ KB}$ is an evaluation observation.
- *Status*: `[ARCHITECTURALLY RATIFIED]`.

### 6.4 Gate R4: User Assertion & Conflict Policy
- **Mechanism**: User assertions enter with `provenance = USER_STATED` and `epistemic_state = ASSERTED` ($C \le 0.70$).
- **Conflict Handling**: Contradictions are detected in `KnowledgeStore.detect_contradiction()` and recorded as `ConflictRecord`. CAPS **DOES NOT OWN** truth maintenance or belief revision. CAPS merely reflects the conflict by emitting `CommunicativeAct.CLARIFY`.
- *Status*: `[VERIFIED / CONTRACT SPECIFIED]`.

---

## 7. Bounded Cognitive Communication Boundary (Anti-LLM Guard)

To prevent CAPS from evolving into a hidden generative language model or monolithic agent, strict boundaries are contracted:

```text
┌─────────────────────────────────────────────────────────────────────────────┐
│                 STRICT ARCHITECTURAL BOUNDARY ENFORCEMENT                   │
├──────────────────────────────────────┬──────────────────────────────────────┤
│ WHAT CAPS OWNS                       │ WHAT CAPS MUST NEVER OWN             │
├──────────────────────────────────────┼──────────────────────────────────────┤
│ 1. Communicative Act Selection       │ 1. Natural language token prediction │
│ 2. Proposition Selection / Binding   │ 2. Lexical choice & surface syntax   │
│ 3. Admissibility & Grounding Gating  │ 3. Probabilistic language generation │
│ 4. Epistemic Metadata Attribution    │ 4. Long-term memory / transcript store│
│ 5. Provenance Metadata Preservation  │ 5. Facial expressions & prosody      │
│ 6. Subgoal-to-Inquiry Compilation    │ 6. Voice actuation & pacing (P24)    │
└──────────────────────────────────────┴──────────────────────────────────────┘
```

- **Separation of Concerns**:
  - CAPS owns **WHAT TO COMMUNICATE** (Intent, Proposition, Epistemic Commitment).
  - Downstream language realization and P24 affective adaptation own **HOW TO EXPRESS IT** (Vocabulary, Tone, Phrasing, Rhythm, Prosody).
- **No Language Choice in CAPS**: CAPS output contains zero natural language strings, zero ISO language codes, and zero lexical templates.

---

## 8. Determinism Specification

$$\mathbf{CAPS}(\text{Snapshot}_t,\; \text{Version}_k) \equiv \mathbf{CAPS}(\text{Snapshot}_t,\; \text{Version}_k)$$

- **Deterministic Scope**: Given a fully specified, frozen input snapshot and a fixed contract version, the CAPS transformation **SHALL BE DETERMINISTIC**.
- **No Global Determinism Claim**: CAPS does NOT claim that the entire runtime pipeline (which includes clock updates, audio threads, and asynchronous background ODEs) is globally deterministic.
- **Canonical Serialization**: Two identical executions of the CAPS transformation on identical input data MUST produce identical canonical SHA-256 serialization hashes.

---

## 9. Implementation Constraints: MUST, MAY, MUST NOT

### 9.1 MUST (Architectural Invariants)
1. **MUST** enforce the Grounding Invariant: refuse `ASSERT`/`ANSWER` without admissible grounding.
2. **MUST** preserve $\mathbf{RESOLVED \neq FACT}$ and $\mathbf{USER\_STATED \neq FACT}$.
3. **MUST** fail closed to `INQUIRE` or `CLARIFY` when referents are missing or ambiguous.
4. **MUST** maintain discrete language-independent `SemanticGraph` output without natural language strings.
5. **MUST** decouple reference resolution status, evidence admissibility, and epistemic state into separate metadata fields.

### 9.2 MAY (Implementation Freedoms)
1. **MAY** be implemented as a set of pure functional transformation functions across existing packages (`src/core/cognition/`, `src/core/knowledge/`) rather than a single monolithic class.
2. **MAY** utilize fast typed integer lookups via `SymbolTable` to accelerate relation matching.
3. **MAY** cache compiled subgoal-to-query graphs within a single turn scratchpad.

### 9.3 MUST NOT (Strict Prohibitions)
1. **MUST NOT** import or invoke any LLM, SLM, or probabilistic token generator.
2. **MUST NOT** create a monolithic `CAPSManager` owning limbic or discourse memory.
3. **MUST NOT** alter `data/profile.json` or touch Genesis onboarding status.
4. **MUST NOT** perform natural language realization, translation, or syntax generation.
5. **MUST NOT** silently overwrite conflicting user assertions or promote `UNKNOWN` to certainty.

### 9.4 PROVISIONAL (Requires Conversational Tuning)
1. Specific discourse cache capacity $N_{\text{max}} = 16$, decay $\gamma = 0.60$, eviction threshold $\theta = 0.15$.
2. Closed illocutionary act taxonomy (8 provisional acts).

### 9.5 OPEN IMPLEMENTATION QUESTIONS
1. **Predicate Schema Role Registry**: Currently, positional arguments (`arg0`, `arg1`, `arg2`) map to `:ARG0`, `:ARG1`, `:ARG2` by implicit convention. Should the ontology schema formalize explicit named semantic roles (e.g. `:AGENT`, `:PATIENT`, `:DESTINATION`) for all registered predicates prior to production integration?
2. **Multi-Proposition Turn Budgeting**: When multiple independent communicative goals are active simultaneously, what exact priority ranking function (e.g. Tension vs Relational Bond vs Information Need) resolves which single proposition graph is emitted first?
3. **Assertion Confidence Threshold Calibration ($\theta_{\text{assert}}$)**: No canonical evidence or benchmark in the active repository currently establishes an empirical numeric cutoff for assertive emission. The assertion threshold must be formally established through calibration across verified vs inferred vs user-stated knowledge corpora rather than adopting an ungrounded heuristic.

---

## 10. Verification & Test Obligations

Any candidate implementation of this contract MUST pass the following 15 automated test suites prior to production promotion:

| Test ID | Test Obligation | Pass Criterion |
|---|---|---|
| **TEST-01** | **Deterministic Replay** | Identical SHA-256 serialization hashes across two executions on frozen snapshot. |
| **TEST-02** | **Grounding Gate Assertion** | Attempted `ASSERT` on verified knowledge succeeds with `EpistemicState = FACT`. |
| **TEST-03** | **Fail-Closed Ungrounded Refusal** | Attempted `ASSERT` on ungrounded goal strictly emits `REFUSE` or `INQUIRE`. |
| **TEST-04** | **USER_STATED != FACT** | User assertion enters as `ASSERTED` / `HYPOTHETICAL` ($C \le 0.70$); never promotes to `FACT`. |
| **TEST-05** | **RESOLVED != FACT** | Anaphoric pronoun resolved to entity ID preserves original proposition epistemic status. |
| **TEST-06** | **Ambiguity to CLARIFY** | Competing referents with identical score emit `CommunicativeAct.CLARIFY`. |
| **TEST-07** | **Unresolved to INQUIRE** | Query referencing missing/evicted entity emits `CommunicativeAct.INQUIRE` with `?X`. |
| **TEST-08** | **Type Mismatch Rejection** | Incompatible semantic category rejects candidate and fails closed to `INQUIRE`. |
| **TEST-09** | **InformationSubgoal Compilation** | `InformationSubgoal` with open slot compiles deterministically to interrogative `SemanticGraph`. |
| **TEST-10** | **Discourse Cache Boundedness** | 100-turn simulation enforces capacity cap with zero unbounded memory growth. |
| **TEST-11** | **Bounded Graph Composition** | Composed deductive graphs link all derivation premises with zero cyclic loops. |
| **TEST-12** | **Zero Language Realization** | Output graph verified to contain 0 natural language tokens, tokens, or strings. |
| **TEST-13** | **Zero LLM/SLM Dependency** | Module execution verifies 0 calls to `LLMBackend` or external generative APIs. |
| **TEST-14** | **No Hidden Long-Term Memory** | Verifies zero disk writes or database side-effects within CAPS transformation. |
| **TEST-15** | **Genesis Gate Integrity** | Verifies `data/profile.json` remains bit-exact `{"is_onboarded": false}` throughout tests. |

---

## 11. Integration Boundary with Canonical Cognitive Pipeline (S1–S16)

In [`docs/ARCHITECTURE.md`](file:///c:/Users/Lunafiah/Desktop/My_project/Lucia/docs/ARCHITECTURE.md), the canonical cognitive turn is organized into a 16-stage pipeline (S1–S16). Within the current generative baseline, Stage 11 executes prompt assembly and Stage 13 invokes `LLMBackend.generate()`.

### 11.1 Architectural Relationship & S11 Responsibility Transition
> **No contradiction identified with the ratified S1–S16 architectural boundaries; implementation will require the previously identified S11 responsibility transition.**

- **Strict Functional Decoupling**:
  - CAPS determines **WHAT TO COMMUNICATE** (illocutionary act, proposition selection, epistemic status, provenance).
  - Downstream language realization and P24 expression adaptation determine **HOW TO EXPRESS IT** (vocabulary, syntax, rhythm, prosody).
- **S11 Responsibility Transition**:
  - In the current production runtime, Stage 11 formats a text prompt for generative SLM completion.
  - In a future SLM-free architecture, Stage 11 must transition from text prompt assembly to consuming semantic conditioning derived from CAPS.
  - This responsibility transition has NOT yet been implemented in production.
- **Governance & Non-Mutation Invariants**:
  - [`docs/ARCHITECTURE.md`](file:///c:/Users/Lunafiah/Desktop/My_project/Lucia/docs/ARCHITECTURE.md) is **NOT MODIFIED** by this contract.
  - Runtime stages S1–S16 remain in their canonical baseline state.
  - End-to-end integration of CAPS with production S1–S16 has **NOT YET BEEN EMPIRICALLY DEMONSTRATED** and remains gated until implementation authorization.

---

## 12. Research Claim Classification Matrix

| Claim Item | Classification | Verifying Evidence / Location |
|---|---|---|
| **CAPS Functional Boundary Justification** | `[ARCHITECTURALLY RATIFIED]` | [`P23_CAPS_BOUNDARY_CONTRACT_DESIGN.md`](file:///c:/Users/Lunafiah/Desktop/My_project/Lucia/docs/PhaseDocs/Lucia-phase23-Semantic_Substrate/P23_CAPS_BOUNDARY_CONTRACT_DESIGN.md) |
| **Discourse Referent Retention Contract** | `[ARCHITECTURALLY RATIFIED]` | [`DISCOURSE_REFERENT_RETENTION_CONTRACT.md`](file:///c:/Users/Lunafiah/Desktop/My_project/Lucia/docs/PhaseDocs/Lucia-phase23-Semantic_Substrate/evaluation/DISCOURSE_REFERENT_RETENTION_CONTRACT.md) |
| **InformationSubgoal Compiler (R1)** | `[VERIFIED BY PROTOTYPE]` | [`test_discourse_retention_contract.py`](file:///c:/Users/Lunafiah/Desktop/My_project/Lucia/tests/evaluation/phase23_caps/run_caps_readiness_benchmark.py:361–394) |
| **Grounded Selection & Refusal (R2)** | `[VERIFIED BY PROTOTYPE]` | [`run_caps_readiness_benchmark.py:395–430`](file:///c:/Users/Lunafiah/Desktop/My_project/Lucia/tests/evaluation/phase23_caps/run_caps_readiness_benchmark.py#L395-L430) |
| **Autonomous Novel Proposition Generation** | `[NOT YET EMPIRICALLY DEMONSTRATED]` | Open research; bounded composition verified, unconstrained generation unproven |
| **USER_STATED != FACT Invariant (R4)** | `[ARCHITECTURALLY RATIFIED]` | [`DISCOURSE_REFERENT_RETENTION_RATIFICATION.md`](file:///c:/Users/Lunafiah/Desktop/My_project/Lucia/docs/PhaseDocs/Lucia-phase23-Semantic_Substrate/evaluation/DISCOURSE_REFERENT_RETENTION_RATIFICATION.md) |
| **Provisional Parameters ($N=16, \gamma=0.60, \theta=0.15$)**| `[PROVISIONAL]` | Section 9.4 of this document |
| **Predicate Schema Role Registry** | `[OPEN IMPLEMENTATION QUESTION]` | Section 9.5 of this document |
| **Assertion Confidence Threshold Calibration ($\theta_{\text{assert}}$)** | `[OPEN IMPLEMENTATION QUESTION]` | Section 9.5 of this document; no canonical evidence exists for a hardcoded numeric cutoff |

---

## 13. Governance Status & Safety Check

```text
================================================================================
                    CAPS ARCHITECTURAL GOVERNANCE LEDGER
================================================================================
CAPS Boundary Contract             : [ARCHITECTURALLY RATIFIED]
Discourse Referent Retention       : [ARCHITECTURALLY RATIFIED]
CAPS Implementation Contract       : [ARCHITECTURALLY RATIFIED]
                                     (Pre-Production Implementation Specification)
CAPS Production Implementation     : [NOT AUTHORIZED / ZERO CODE MUTATION]
Genesis Onboarding State           : [LOCKED / {"is_onboarded": false}]
================================================================================
```

This specification document is formally **ARCHITECTURALLY RATIFIED** as a pre-production technical interface contract. **Formal architectural ratification does NOT constitute production implementation authorization.** CAPS production implementation remains strictly locked and unauthorized. Zero production code is modified or executed.
