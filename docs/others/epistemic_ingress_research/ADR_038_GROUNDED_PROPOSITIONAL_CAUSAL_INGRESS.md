# ADR-038: Grounded Propositional Causal Ingress Contract (P23-H E3)

> **Document ID:** DOC-ADR-038 (ARCH-038 / DOC-P23H-E3-ADR-001)  
> **Status:** `[IMPLEMENTED & VERIFIED]`  
> **Date:** 2026-10-20  
> **Target Subsystem:** `src/core/language/adapter/` (Perimeter Ingress Gate) & `src/core/cognition/contract/` (`ProvenanceRecord`)  
> **Preserved Frozen Kernel:** Phase 23-H Reasoning Kernel (`src/core/cognition/kernel/`, commit `3eef803`)  
> **Canonical Location:** `docs/others/epistemic_ingress_research/ADR_038_GROUNDED_PROPOSITIONAL_CAUSAL_INGRESS.md`  
> **Preceding Evidence Chain:**  
> - E3-R1 Feasibility Audit (`EP_REAS_FORMATION_FEASIBILITY_AUDIT.md`)  
> - E3-R2 Falsification Report (`DOC-P23H-E3-R2-FALSIFICATION-001`)  
> - E3-R3 Contract Boundary Review (`DOC-P23H-E3-R3-BOUNDARY-REVIEW-001`)  
> - E3-R4 F15 Causal Boundary Report (`DOC-P23H-E3-R4-CAUSAL-BOUNDARY-001`)  

---

## 1. Context

Lucia's cognitive architecture operates a strictly bounded, deterministic, backward goal-directed reasoning kernel with Strong Kleene three-valued logic ($TRUE, FALSE, UNKNOWN$) and Justification-Based Truth Maintenance (JTMS) in **Phase 23-H** (`src/core/cognition/kernel/`), frozen at commit `3eef803`. In Phase 23-G (ARCH-030.1), the boundary between the continuous semantic substrate (`SemanticGraph`) and the discrete reasoning engine was formalized as numeric arrays in `TermArena` (`LogicalTerm`, `ScopeTerm`, `ProvenanceRecord`).

However, upstream perceptual, conversational, and memory sources in the broader architecture operate on continuous signals, ungrounded natural language strings, heuristic confidence scores ($c \in [0.0, 1.0]$ in `KnowledgeStore`), and multi-turn conversational dialogue. 

In the research track **Phase 23-H E3 (Epistemic Ingress Research)**, iterations E3-R1 through E3-R4 evaluated the foundational requirements for admitting upstream assertions as axiomatic premises into P23-H. Without principled qualification at the perimeter, conversational feedback loops and perceptual approximations risk corrupting Strong Kleene K3 semantics. Most critically, the system is exposed to the **F15 Conversational Echo Attack**, where the companion asks a speculative question or posits an ungrounded hallucination, the user passively assents or echoes, and the cognitive pipeline treats the user's turn as independent external testimony, promoting self-generated assumptions into immutable symbolic `FACT`.

---

## 2. Problem Statement

Three interconnected architectural vulnerabilities exist at the boundary between conversational perception and symbolic reasoning:

1. **Continuous Uncertainty vs. Discrete Certainty**: Naive mapping of scalar confidence scores ($c \ge \theta$) to discrete premises asserts ungrounded hypotheses as axiomatic truths, violating the core epistemic invariant that *UNKNOWN must never silently become certainty*.
2. **Untrusted Epistemic Self-Assertion**: Upstream components or language parsers cannot be trusted to self-declare their own epistemic validity or assert `epistemic_status = FACT`. Epistemic qualification must be an authoritative gate verdict certified by an invariant boundary.
3. **The F15 Conversational Echo Trap**: An assertion elicited from the user during conversation may be causally dependent on an assistant-seeded hypothesis. If conversational origin is unmodeled or collapsed into a coarse turn-level flag, the system either:
   - Silently incorporates self-generated hallucinations as confirmed facts (false positive), or
   - Downgrades authoritative user testimony and corrections simply because they were prompted by the assistant (false negative).

---

## 3. Primary Research Question & Foundational Finding

### Research Question
> *What is the smallest structurally sufficient epistemic qualification and causal attribution primitive that allows the perimeter ingress boundary to filter ungrounded hypotheses and distinguish assistant-prompted confirmation from spontaneous user testimony, without requiring a full pragmatic discourse parser or mutating the frozen P23-H reasoning kernel?*

### The Core Architectural Axiom
> **PROMPTED $\ne$ EPISTEMICALLY DEPENDENT.**

Conversational elicitation (whether an utterance was prompted by the assistant) is completely orthogonal to epistemic authority (whether the semantic content originates from the user or the assistant). 

A turn-level boolean `is_assistant_prompted: bool` is mathematically and epistemically broken. Causal origin and evidential independence reside at the **propositional (clause) level**, not at the conversational turn level.

---

## 4. Evidence Chain: Evolution from E3-R1 through E3-R4

The epistemic ingress specification was developed through four rigorous research and falsification iterations:

```text
E3-R1: Feasibility Audit
  • Result: Generic upstream premise promotion is NO-GO.
  • Finding: Continuous confidence cannot become symbolic FACT; K3 is an internal calculus, not an ingress filter.
  • Output: Candidate 5-field struct proposed for formal falsification.
       ↓
E3-R2: Falsification Study (DOC-P23H-E3-R2-FALSIFICATION-001)
  • Result: Candidate 5-field contract FALSIFIED & REJECTED.
  • Finding: Scalar thresholding (c ≥ θ ⇒ FACT) rejected under NEG-02; INFERRED requires recursive acyclic provenance.
  • Finding: 'validity' is redundant; modal scope, source authority, and F15 echo vulnerability identified.
       ↓
E3-R3: Boundary Review (DOC-P23H-E3-R3-BOUNDARY-REVIEW-001)
  • Result: R2 revision FALSIFIED (CONDITIONAL — ONE UNRESOLVED QUESTION).
  • Finding: Temporal validity (valid_from/until) is wrong layer (P23-H has no clock).
  • Finding: scope_type_id denormalizes ScopeTerm; epistemic_status must be gate output, not untrusted input.
  • Finding: Proposed turn-level is_assistant_prompted: bool fails multi-claim turns and corrections (F15).
       ↓
E3-R4: F15 Causal Boundary Resolution (DOC-P23H-E3-R4-CAUSAL-BOUNDARY-001)
  • Result: STRUCTURAL SPECIFICATION VALIDATED (10/10 Attack Matrix PASS).
  • Finding: Boolean flag, flat enum, and bare pointer all conclusively rejected.
  • Finding: Full pragmatic discourse parser is computationally unnecessary for F15 defense.
  • Discovery: Grounded Propositional Causal Link <antecedent_term_id, CausalRelation> is minimal and sufficient.
```

---

## 5. Rejected Alternatives Ledger

The following candidate mechanisms were experimentally or theoretically tested and formally **REJECTED**:

| Candidate Mechanism | Formulation / Architecture | Primary Failure Mode & Falsification Rationale | Status |
|---|---|---|:---:|
| **Naive Scalar Confidence Threshold** | $c \ge \theta \implies \text{Assert}(\text{FACT})$ | **Corrupts Strong Kleene K3 Semantics**: High confidence measures sensor SNR or model calibration, not ontological ground truth. Transforms continuous uncertainty into unretractable binary certainty. Permanently rejected under **NEG-02**. | **REJECTED** (R1/R2) |
| **Five-Field Candidate Contract** | `(proposition, epistemic_status, provenance, scope, validity)` | **Simultaneously Non-Minimal & Insufficient**: `validity` is redundant runtime state. Lacks modal scope containers, lacks source authority classes, lacks temporal freshness, and permits untrusted self-declaration of `FACT`. | **REJECTED** (R2) |
| **Ungrounded `INFERRED` Promotion** | Promoting derived facts as axioms without supporting premise DAG | **Destroys Non-Monotonic Invalidation**: If an upstream inferred proposition is admitted without its premise tree, retracting an underlying premise cannot cascade invalidation in JTMS, leaving orphaned contradictory beliefs. | **REJECTED** (R2) |
| **Temporal Horizon in Logic Kernel** | `valid_from`, `valid_until` inside `LogicalTerm` | **Wrong Layer Denormalization**: P23-H is a bounded, static Horn-chainer with no internal clock. Temporal expiration belongs upstream in memory caching or episodic decay engines. | **REJECTED** (R3) |
| **Denormalized Scope Type** | Storing `scope_type_id` on every proposition | **Denormalization Defect**: Scope type is an invariant property of `ScopeTerm` in `TermArena`, allocated once. Attaching it to every term creates inconsistent duplicate declarations for the same scope. | **REJECTED** (R3) |
| **Untrusted Input Epistemic Status** | Upstream caller passes `epistemic_status = FACT` | **Untrusted Self-Assertion Loophole**: Allows untrusted perception or language drivers to arbitrarily declare ungrounded tokens to be ground truth. `epistemic_status` must be certified by the gate. | **REJECTED** (R3) |
| **Turn-Level Prompting Boolean** | `is_assistant_prompted: bool` | **Fails 8/10 Attack Cases**: Commits the *Open-Question Blunder* (downgrades direct user answers like "Hanoi" to UNKNOWN), commits the *Correction Inversion* (downgrades user corrections like "No, I hate it"), and collapses on mixed turns. | **REJECTED** (R3/R4) |
| **Flat Causal Enum** | `CausalOrigin` enum without antecedent pointer | **Target Blindness**: In multi-claim turns (e.g., agreeing with claim A but correcting claim B), a flat enum cannot indicate which antecedent hypothesis was confirmed and which was refuted. | **REJECTED** (R4) |
| **Bare Antecedent Pointer** | `causal_antecedent_id: int` without relation | **Stance Blindness**: Provides a referential target but cannot indicate whether the user confirmed, elaborated, or refuted the referenced seed without natural language parsing inside the core. | **REJECTED** (R4) |
| **Full Pragmatic Discourse Parser** | Heavy computational NLP speech-act tracking | **Violates 20W Edge Resource Budget**: Unbounded computational complexity and high latency ($>50\text{ ms}$). Proved structurally unnecessary for defending the F15 boundary. | **REJECTED** (R4) |

---

## 6. Ratification of Invariant NEG-02

This ADR formally ratifies non-negotiable architectural invariant **NEG-02**:

> ### INVARIANT NEG-02: Universal Rejection of Scalar Confidence Thresholding
> 
> **No continuous scalar confidence, similarity score, activation potential, or heuristic probability ($c \in [0.0, 1.0]$) may, by exceeding any static or dynamic threshold $\theta$, directly assert or promote a proposition to epistemic status `FACT` within the discrete cognitive reasoning substrate.**
> 
> *RATIONALE*: Scalar confidence represents measurement reliability, acoustic signal-to-noise ratio, or model certainty; it does not constitute a valid logical justification or axiomatic ground truth. Converting continuous uncertainty into discrete certainty without formal derivation or external user testimony corrupts Strong Kleene K3 three-valued logic and paralyzes non-monotonic truth maintenance. Under all conditions:
> $$\forall c \in [0.0, 1.0], \quad (c \ge \theta) \centernot\implies \text{Assert}(\text{FACT})$$
> Continuous propositions with $c < 1.0$ entering reasoning must enter as modal, intensional, or `UNKNOWN` terms emitting an `InformationSubgoal` (Quadrant 1), never as ungrounded extensional facts.

---

## 7. Accepted Architectural Contract

The ratified research-derived specification establishes the **Grounded Propositional Causal Ingress Contract**:

### 7.1 Causal Link Definition
Every admitted candidate assertion derived from conversational interaction carries a two-element grounded causal link:

$$\text{CausalLink} = \langle \text{antecedent\_term\_id: int}, \text{causal\_relation: CausalRelation} \rangle$$

### 7.2 Bounded `CausalRelation` Vocabulary
The vocabulary consists of exactly five validated discrete relations:

```python
class CausalRelation(IntEnum):
    SPONTANEOUS = 1
    """User-authored content initiated without assistant prompt or topical seed."""

    SUPPLIED_ANSWER = 2
    """User-authored content providing novel information in response to an open assistant question (e.g. 'Where do you live?' -> 'Hanoi')."""

    CONFIRMED_ECHO = 3
    """User passively assenting to or repeating an assistant-seeded closed hypothesis (e.g. 'You like jazz, right?' -> 'Yeah'). F15 Risk: Must be downgraded to UNKNOWN."""

    CORRECTED_NEGATION = 4
    """User explicitly denying, correcting, or refuting an assistant-seeded closed hypothesis (e.g. 'You like jazz, right?' -> 'No, I hate it'). Triggers polarity=False and JTMS retraction."""

    ELABORATED = 5
    """User confirming an assistant topic while supplying independent, novel evidential propositions within the same turn."""
```

### 7.3 Candidate Ingress Assertion Contract
The authoritative candidate structure evaluated by the perimeter Ingress Gate prior to interning into `TermArena`:

```python
@dataclass(frozen=True)
class IngressCandidateAssertion:
    """
    R4 Validated Minimal Epistemic Ingress Candidate Contract.
    Evaluated by Language Ingress Gate BEFORE admission into P23-H TermArena.
    """
    # 1. Semantic Relational Core (Numeric IDs in SymbolTable)
    predicate_id: int
    arg0_id: int
    arg1_id: int = 0
    arg2_id: int = 0
    polarity: bool = True

    # 2. Structural Scope Anchor
    scope_id: int = 1               # Points to preallocated ScopeTerm in TermArena

    # 3. Source Origin & Epistemic Authority Class
    source_class: IngressSourceClass # USER_DISCOURSE, PERCEPTUAL, DERIVED, MEMORY

    # 4. Grounded Causal Link (F15 Anti-Echo Defense)
    causal_relation: CausalRelation = CausalRelation.SPONTANEOUS
    antecedent_term_id: int = 0     # 0 if spontaneous/supplied; assistant term ID if echo/correction

    # 5. Derivation Provenance Tree (Mandatory if source_class == DERIVED)
    rule_id: int = 0
    supporting_premise_ids: Tuple[int, ...] = () # Must form an acyclic DAG in TermArena
```

---

## 8. Epistemic Qualification Rules & Non-Escalation Lattice

The perimeter Ingress Gate certifies the output `epistemic_status` and `polarity` according to the following deterministic qualification mapping:

```text
Candidate Ingress Assertion
       │
       ├── source_class == USER_DISCOURSE
       │     ├── causal_relation == SPONTANEOUS
       │     │     └── Output: epistemic_status = FACT (in User Modal Scope)
       │     │
       │     ├── causal_relation == SUPPLIED_ANSWER
       │     │     └── Output: epistemic_status = FACT (in User Modal Scope)
       │     │
       │     ├── causal_relation == CONFIRMED_ECHO  [F15 DEFENSE]
       │     │     ├── Output: epistemic_status = UNKNOWN
       │     │     └── Action: Emit InformationSubgoal; suppress extensional FACT promotion
       │     │
       │     └── causal_relation == CORRECTED_NEGATION
       │           ├── Output: epistemic_status = FACT, polarity = False
       │           └── Action: JTMS cascade invalidation / premise retraction on antecedent_term_id
       │
       ├── source_class == PERCEPTUAL
       │     └── Output: epistemic_status = UNKNOWN (in Perceptual Modal Scope)
       │           (Confidence stored in ProvenanceRecord; never asserts root FACT)
       │
       ├── source_class == DERIVED
       │     ├── Condition: All supporting_premise_ids valid, acyclic, and admitted
       │     └── Output: epistemic_status = INFERRED
       │
       └── source_class == MEMORY
             └── Output: Inherits verified historical epistemic_status from snapshot
```

### The Ingress Non-Escalation Invariant
The Ingress Gate strictly enforces the non-escalation lattice:

$$\mathcal{E}(\text{AdmittedTerm}) \le \mathcal{E}(\text{CandidateSource})$$

Under no circumstances may the ingress boundary output an epistemic status with higher ontological commitment than the source justifies. In particular:
- `UNKNOWN` $\to$ `FACT` is **PROHIBITED**.
- `AMBIGUOUS` $\to$ `FACT` is **PROHIBITED** without explicit disambiguation.
- Assistant Echo $\to$ `FACT` is **PROHIBITED**.

---

## 9. Layer Ownership & Subsystem Boundaries

The research chain clearly delineates architectural responsibilities. Epistemic causality is owned at the perimeter; P23-H remains a pure, non-conversational reasoning kernel.

```text
+--------------------------------------------------------------------------+
|                        PERIMETER / LANGUAGE LAYER                        |
|                                                                          |
|   1. Language Ingress Gate (`src/core/language/adapter/`)                 |
|      - Parses natural language into semantic arguments.                  |
|      - Inspects `DyadicDiscourseState` (previous assistant act).         |
|      - Computes CausalLink <antecedent_term_id, CausalRelation>.         |
|      - Evaluates IngressCandidateAssertion against Ingress Gate.         |
|      - Certifies output: epistemic_status, polarity, scope_id.           |
+------------------------------------+-------------------------------------+
                                     |
                                     | Interms qualified term into TermArena
                                     v
+--------------------------------------------------------------------------+
|                       P23-G CONTRACT & PROVENANCE                        |
|                                                                          |
|   2. TermArena & Provenance (`src/core/cognition/contract/`)             |
|      - Allocates `LogicalTerm` with certified `epistemic_status`.        |
|      - Stores `antecedent_term_id` and `causal_relation` as integers    |
|        within numeric `ProvenanceRecord.metadata`.                       |
|      - ZERO heap allocations; ZERO string leakage.                       |
+------------------------------------+-------------------------------------+
                                     |
                                     | Passes static term arrays
                                     v
+--------------------------------------------------------------------------+
|                        FROZEN P23-H REASONING KERNEL                     |
|                                                                          |
|   3. Bounded Goal-Directed Reasoning (`src/core/cognition/kernel/`)       |
|      - Operates strictly on numeric IDs and Strong Kleene K3 logic.      |
|      - Evaluates goals against admitted premises.                        |
|      - Manages premise retractions via JTMS.                             |
|      - Has NO knowledge of natural language, turns, or discourse state.  |
+--------------------------------------------------------------------------+
```

### Key Ownership Principles:
1. **P23-H Does Not Parse Discourse**: P23-H is a deductive reasoning kernel. It does not inspect conversational history, does not parse dialogic acts, and does not reconstruct causal antecedents.
2. **Ingress Gate Owns Causal Attribution**: The `LanguageIngressGate` (working in concert with Stage S10 `DyadicDiscourseState`) is the sole subsystem responsible for determining `CausalRelation` and identifying `antecedent_term_id`.
3. **P23-G `ProvenanceRecord` Stores the Link**: The causal link is persisted numerically in `ProvenanceRecord` metadata, requiring zero new schema classes or heap-allocated structures.

---

## 10. Scope Boundary & Bounded Research Vocabulary

This ADR establishes explicit limits on the scope and interpretation of this contract:

1. **Targeted to the F15 Boundary**: This contract specifically solves the **F15 clause-level causal-ingress boundary** (preventing conversational echo fortification while preserving direct user testimony and corrections).
2. **Not a Universal Dialogue Ontology**: The five `CausalRelation` values do not constitute a universal or exhaustive ontology of human conversational pragmatics, rhetoric, sarcasm, or multi-party conversation. They represent a **bounded research vocabulary** formally verified against the 10 canonical attack vectors of the F15 matrix.
3. **Meaning of "10/10 PASS"**: The "10/10 PASS" result achieved in E3-R4 means specifically that the contract successfully resolved all 10 defined scenarios in the F15 attack matrix. It does **not** constitute a formal mathematical proof of empirical conversational infallibility across open-ended natural dialogue.
4. **No Semantic Infiltration into Core**: The strings `"SPONTANEOUS"`, `"CONFIRMED_ECHO"`, etc., exist solely in the Python enum definition. Across the substrate boundary, they are represented exclusively as 64-bit integer discriminators (`1..5`).

---

## 11. Epistemic Safety Implications

1. **Preservation of Strong Kleene K3**: By intercepting assistant echoes and mapping them to `UNKNOWN`, the ingress contract prevents ungrounded assumptions from collapsing into $TRUE$ or $FALSE$. They cleanly map to Quadrant 1, emitting an `InformationSubgoal` to seek external verification.
2. **Non-Monotonic Retraction of Shared Falsehoods**: When the user utters a correction (`CORRECTED_NEGATION`), the contract uses `antecedent_term_id` to directly target the seed proposition and execute `JTMS.retract_premise()`, cascading invalidation to all downstream inferences that relied on the hallucination.
3. **Modal Isolation**: Speculative propositions and perceptual hypotheses are assigned distinct `scope_id` containers, preventing them from unifying with root extensional facts during backward chaining.

---

## 12. P23-H Kernel Freeze Preservation

This ADR **strictly preserves the frozen baseline of Phase 23-H**:

- **Zero Modifications to `src/core/cognition/kernel/`**: `engine.py`, `jtms.py`, `conflict.py`, `rules.py`, and `subgoals.py` remain frozen bit-exact at commit `3eef803`.
- **Reasoning Limits Untouched**: `MAX_SEARCH_DEPTH = 8`, `MAX_INFERENCE_STEPS = 256` remain unchanged.
- **Data Structures Untouched**: `TermArena`, `SymbolTable`, `BindingFrame`, and `ConflictRecord` remain bit-exact.
- **Zero Production Mutations**: No runtime code in `src/core/` is modified as part of this decision.
- **Zero Genesis Contamination**: `data/profile.json` remains `{"is_onboarded": false}`.

---

## 13. Consequences

### Positive Consequences
- **Eliminates Conversational Echo Hallucination**: Lucia will no longer convert her own speculative questions into permanent beliefs merely because a user says "yes" or "right".
- **Preserves Active Intersubjective Learning**: By recognizing `SUPPLIED_ANSWER`, the companion can ask open questions ("Where do you live?") and legitimately store the user's answer as an authoritative fact.
- **Guarantees Correction Authority**: By recognizing `CORRECTED_NEGATION`, user refutations immediately invalidate assistant assumptions rather than being silenced by a crude prompting filter.
- **Zero Computational Overhead**: Operates entirely in $O(1)$ time with integer lookups, requiring 0 MB additional GPU VRAM and zero dynamic memory allocations in the inner reasoning loop.

### Negative Consequences & Technical Debt
- **Dependency on Upstream Discourse State**: The Ingress Gate requires `DyadicDiscourseState` (Stage S10) to accurately record whether the assistant's previous turn was an open question, closed question, or statement. If upstream discourse tracking misclassifies an open question as a closed hypothesis, user testimony may be improperly downgraded.
- **Inter-Turn Proposition Memory Gap**: Because the assistant's prior-turn semantic terms are currently stored only as raw text strings in `_history` (rather than indexed `LogicalTerm` IDs in `TermArena`), runtime realization of `antecedent_term_id` will require a lightweight semantic cache of recent assistant claims.

---

## 14. Implementation Status & Governance

- **Architectural Status**: `[ARCHITECTURE APPROVED / SPECIFICATION FROZEN / IMPLEMENTATION DEFERRED]`.
- **Runtime Implementation**: **DEFERRED**. This ADR authorizes the specification and ratifies its mathematical soundness. It does **NOT** authorize immediate code implementation or premature wiring into `src/core/`.
- **Future Realization**: Implementation shall occur only when formal project governance schedules the conversational ingress integration milestone under post-activation developmental roadmaps.

---

## 15. Source Document References

1. **E3-R1 Feasibility Audit**: `docs/others/epistemic_ingress_research/EP_REAS_FORMATION_FEASIBILITY_AUDIT.md` (Initial premise promotion audit).
2. **E3-R2 Falsification Report**: `docs/others/epistemic_ingress_research/P23H_E3_R2_EPISTEMIC_INGRESS_FALSIFICATION_REPORT.md` (`DOC-P23H-E3-R2-FALSIFICATION-001`).
3. **E3-R3 Contract Boundary Review**: `docs/others/epistemic_ingress_research/P23H_E3_R3_CONTRACT_BOUNDARY_REVIEW.md` (`DOC-P23H-E3-R3-BOUNDARY-REVIEW-001`).
4. **E3-R4 F15 Causal Boundary Report**: `docs/others/epistemic_ingress_research/P23H_E3_R4_F15_CAUSAL_BOUNDARY_RESEARCH.md` (`DOC-P23H-E3-R4-CAUSAL-BOUNDARY-001`).
5. **Phase 23-G Substrate-Core Contract**: `docs/PhaseDocs/Lucia-phase23-Semantic_Substrate/` (ADR-030.1 / ARCH-030.1).
6. **Phase 23-H Final State Specification**: `docs/PhaseDocs/Lucia-phase23-Semantic_Substrate/P23-H_FINAL_STATE.md` (Commit `3eef803`).
7. **Production Realization Boundary ADR**: `docs/others/PRODUCTION_REALIZATION_BOUNDARY_ADR/ADR_035_PRODUCTION_REALIZATION_BOUNDARY.md` (ADR-035).
