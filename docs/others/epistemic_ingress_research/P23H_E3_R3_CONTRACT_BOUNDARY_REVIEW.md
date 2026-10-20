# P23-H E3-R3 — Revised Minimal Contract Boundary Review

**Document ID**: DOC-P23H-E3-R3-BOUNDARY-REVIEW-001  
**Authority**: Research Read-Only Falsification Report  
**Status**: `[RESEARCH / FALSIFICATION COMPLETED / NO PRODUCTION CHANGES]`  
**Date**: 2026-10-20  
**Target Path**: `docs/others/epistemic_ingress_research/P23H_E3_R3_CONTRACT_BOUNDARY_REVIEW.md`  

---

## 1. Executive Verdict

### **CONDITIONAL — ONE MORE RESEARCH QUESTION**

**Verdict Statement**:
The R2 Conceptual Ingress Contract (`EpistemicallyQualifiedProposition`) is **FALSIFIED** in its current structure. It suffers from three fatal architectural defects:
1. **Wrong-Layer Denormalization**: `scope_type_id`, `valid_from`, and `valid_until` do not belong in a logical term ingress contract. Scope type is an invariant property of `ScopeTerm` in `TermArena`, and temporal horizon is an ephemeral cache/memory lifecycle guard that P23-H (a bounded, non-temporal static Horn-chainer) cannot inspect or enforce.
2. **Untrusted Epistemic Self-Declaration**: Treating `epistemic_status` as an input parameter supplied by upstream callers creates a catastrophic category error: an untrusted source can trivially declare its own ungrounded hallucinations to be `FACT`. `epistemic_status` is the **output verdict** of the ingress gate, not an input parameter.
3. **F15 Echo Loop Vulnerability**: The R2 contract fails completely against the F15 Conversational Echo Attack. A user merely nodding or echoing Lucia's prior speculative question is classified as `USER_DISCOURSE` and promoted to `FACT`, allowing self-generated hallucinations to permanently fortify into ground truth.

A sound, minimal, and non-escalating boundary can be formulated (the **Safe Ingress Contract**), but it cannot be frozen until **EXACTLY ONE** unresolved epistemic issue is specified:

> **THE UNRESOLVED BLOCKER**:  
> **Causal Antecedent Qualification (The F15 Causal Boundary)**:  
> *How does the ingress boundary formally verify whether an incoming user assertion is causally independent evidence versus an echo of Lucia's own prior exploratory utterance, without requiring a complete conversational speech-act discourse tracker?*

---

## 2. Scope and Evidence Base

This research iteration (R3) rigorously pressure-tests the Revised Minimal Ingress Contract proposed in R2. Its objective is not to defend R2's proposal, but to systematically attempt to break it across logical, modal, temporal, and causal dimensions.

### Governing Constraints & Evidence Discipline
- **Read-Only**: Zero production code changes, zero runtime changes, zero database mutations.
- **Kernel Immutability**: Phase 23-H (`src/core/cognition/kernel/`) remains strictly frozen at commit `3eef803`.
- **Subsystem Boundary**: P23-I remains permanently closed as an independent subsystem [REPOSITORY FACT, PHASE_REGISTRY.md].
- **No Implementation Workarounds**: Upstream gaps (F12 KnowledgeStore identity, F15 conversational provenance, F2 endogenous idle loops) are evaluated strictly for their semantic impact on the boundary, not patched with temporary code.
- **Evidence Labels**:
  - `[REPOSITORY FACT]`: Verifiable by inspectable code and data structures.
  - `[VALIDATED EXISTING CONTRACT]`: Ratified and verified architectural rules.
  - `[RESEARCH INFERENCE]`: Deductive analytical finding from research.
  - `[PROPOSED CONTRACT]`: Candidate design under evaluation.
  - `[UNPROVEN]`: Hypothesis lacking empirical or formal verification.
  - `[REJECTED]`: Formally disproven candidate.

---

## 3. Actual Existing Boundary

An inspection of canonical repository contracts reveals the baseline against which any ingress contract must operate:

### 3.1 What Already Exists in the Repository
1. **P23-G Substrate Representation** (`src/core/cognition/contract/`):
   - [REPOSITORY FACT] `LogicalTerm` ([`terms.py`](file:///c:/Users/Lunafiah/Desktop/My_project/Lucia/src/core/cognition/contract/terms.py#L95)) represents relational terms with 64-bit integer IDs: `term_id`, `predicate_id`, `arg0_id`, `arg1_id`, `arg2_id`, `role0_id`, `role1_id`, `role2_id`, `scope_id`, `epistemic_status`, `polarity`, `rule_id`, `premise_ids`, `provenance`, `is_active`, `is_disambiguated`, `alternative_concept_ids`.
   - [REPOSITORY FACT] `ScopeTerm` ([`terms.py`](file:///c:/Users/Lunafiah/Desktop/My_project/Lucia/src/core/cognition/contract/terms.py#L31)) defines containers: `scope_id`, `scope_type_id` (`ROOT=1`, `NEGATION=2`, `MODAL=3`, `INTENSIONAL=4`), and `parent_scope_id`.
   - [REPOSITORY FACT] `ProvenanceRecord` ([`provenance.py`](file:///c:/Users/Lunafiah/Desktop/My_project/Lucia/src/core/cognition/contract/provenance.py#L24)) tracks: `rule_id`, `supporting_premise_ids`, `session_id`, `turn_id`, `timestamp`, `confidence`.
   - [REPOSITORY FACT] `ProjectGraphToTerms()` ([`projection.py`](file:///c:/Users/Lunafiah/Desktop/My_project/Lucia/src/core/cognition/contract/projection.py#L185)) is the *sole authoritative projection boundary* between `SemanticGraph` and `TermArena` [VALIDATED EXISTING CONTRACT, ARCH-030.1].
2. **P23-H Reasoning Kernel** (`src/core/cognition/kernel/`):
   - [REPOSITORY FACT] `ReasoningKernel` backward chainer with `MAX_SEARCH_DEPTH = 8`, `MAX_INFERENCE_STEPS = 256`.
   - [REPOSITORY FACT] Strong Kleene K3 4-quadrant evaluation (`FIX-23H-01`, commit `3eef803`).
   - [REPOSITORY FACT] Multi-justification non-monotonic truth maintenance (`JTMS.retract_premise()`).
   - [REPOSITORY FACT] Polar contradiction detection (`conflict.py`).
3. **P23-E Fortification** (`src/core/knowledge/fortification.py`):
   - [VALIDATED EXISTING CONTRACT] Non-increase invariant: `UNKNOWN -> FACT/INFERRED` is strictly forbidden; `AMBIGUOUS -> FACT` requires explicit upstream `disambiguation_event`.

### 3.2 What R2 Proposed vs What Existing Contracts Own
| Feature / Responsibility | Existing Repository Owner | R2 Ingress Proposal Status | Evaluation |
|---|---|---|---|
| Term Content (`pred`, `args`, `pol`) | `LogicalTerm` (P23-G) | `EpistemicallyQualifiedProposition` | Duplicate of `LogicalTerm` core |
| Epistemic Status (`FACT`, `INFERRED`, etc.) | `EpistemicStatus` (P23-G) | `epistemic_status` | Proposed as untrusted input [DEFECT] |
| Scope Container Pointer | `LogicalTerm.scope_id` (P23-G) | `scope_id` | Aligned with existing contract |
| Scope Type Definition | `ScopeTerm.scope_type_id` (P23-G) | `scope_type_id` | **Denormalized Duplicate** [DEFECT] |
| Derivation Provenance | `ProvenanceRecord` (P23-G) | `rule_id`, `supporting_premise_ids` | Aligned with existing contract |
| Turn / Session Identity | `ProvenanceRecord` (P23-G) | `session_id`, `turn_id` | Aligned with existing metadata |
| Source Authority Class | **NO CURRENT OWNER** | `source_class` | **Novel Requirement** (Ingress Gate only) |
| Temporal Validity Horizon | **NO CURRENT OWNER** | `valid_from`, `valid_until` | **Wrong Layer** (P23-H has no clock) |

---

## 4. Field-by-Field Falsification

Every field proposed by R2 is evaluated against formal falsification criteria:
- **NECESSARY**: Logically and epistemically indispensable at this boundary.
- **DERIVABLE**: Can be computed safely from other existing fields.
- **REDUNDANT**: Duplicates an existing structure without adding epistemic value.
- **WRONG LAYER**: Belongs to an upstream or downstream subsystem, not this boundary.
- **UNPROVEN**: Lacks theoretical or empirical justification.

### Falsification Ledger

| Proposed Field | Classification | Detailed Falsification Analysis |
|---|:---:|---|
| **`predicate_id`** | **NECESSARY** | Identifies the relational concept in `SymbolTable`. Without it, reasoning has no relational operator. |
| **`arg0_id` .. `arg2_id`** | **NECESSARY** | Identifies entity referents. Zero heap binding requires fixed numeric slots ($N \le 3$). |
| **`polarity`** | **NECESSARY** | Distinguishes $P$ from $\neg P$. Essential for P23-H polar contradiction detection (`conflict.py`) and Quadrants 2 & 3. |
| **`epistemic_status`** | **WRONG LAYER (as Input)** | **Falsified as an input parameter.** Allowing an upstream component to supply `epistemic_status = FACT` creates an unverified self-assertion loophole. `epistemic_status` is the **output verdict** certified by the gate. |
| **`scope_id`** | **NECESSARY** | Direct pointer to the container `ScopeTerm` in `TermArena`. Prevents modal statements from bleeding into root assertions. |
| **`scope_type_id`** | **REDUNDANT / WRONG LAYER** | **Falsified.** Scope type is an invariant property of `ScopeTerm`, allocated once via `arena.allocate_scope()`. Placing `scope_type_id` on every proposition denormalizes the scope table, risking conflicting declarations for the same `scope_id`. |
| **`source_class`** | **NECESSARY (at Gate only)** | **Retained strictly as gate input.** Irreducible for filtering out assistant self-echoes and bounding perceptual hypotheses. Not stored inside P23-H `LogicalTerm`. |
| **`session_id`** | **REDUNDANT** | Deductive validity and JTMS dependency maintenance are invariant to session boundaries. Useful for persistence audit, but irrelevant to symbolic premise admissibility. |
| **`turn_id`** | **DERIVABLE** | Available from the conversational orchestrator turn state. Irrelevant as a static term property. |
| **`rule_id`** | **NECESSARY (for INFERRED)** | Mandatory for JTMS to construct an explicit `Justification` node. Must be 0 for ground premises. |
| **`supporting_premise_ids`** | **NECESSARY (for INFERRED)** | Mandatory for JTMS cascade retraction. Must point to active terms already interned in `TermArena`. |
| **`valid_from`** | **WRONG LAYER** | Assertion timestamp. P23-H has no clock and performs no temporal ordering calculus. |
| **`valid_until`** | **WRONG LAYER** | Freshness horizon. Bounded Horn reasoning cannot evaluate time-decay functions. Expiration gating must occur *prior* to `TermArena` insertion. |

---

## 5. Epistemic Status Ownership

### The Central Question
> *Can an upstream source be trusted to declare itself FACT? If not, who is authorized to assign FACT?*

### Formal Falsification
If `epistemic_status` is an input field on the ingress contract, the caller controls the epistemic commitment:
$$\text{Caller} \xrightarrow{\text{passes } \text{status}=\text{FACT}} \text{Ingress Gate} \xrightarrow{\text{asserts}} \text{P23-H Fact Base}$$

This architecture commits a fundamental flaw: **it equates an unverified claim with a certified truth.**
- An uncalibrated visual detector detects an object with high noise $\rightarrow$ declares `status = FACT`.
- An LLM generates a hallucination $\rightarrow$ declares `status = FACT`.
- A user makes a sarcastic statement $\rightarrow$ declares `status = FACT`.

Under this flawed model, the ingress gate is a passive pass-through proxy. It violates the foundational invariant:
$$\textbf{UNKNOWN MUST NEVER SILENTLY BECOME CERTAINTY.}$$

### The Epistemic Authorization Invariant
[RESEARCH INFERENCE]
1. **Upstream Sources NEVER Declare FACT**: An upstream source emits an **Ingress Candidate** (`CandidateAssertion`) containing raw semantic arguments, source class, and provenance.
2. **Authority Belongs Strictly to the Ingress Gate**: The ingress gate evaluates the candidate against repository qualification rules. The assignment of `EpistemicStatus.FACT`, `INFERRED`, `AMBIGUOUS`, `UNKNOWN`, or `REJECT` is the **exclusive verdict of the Gate**.
3. **Domain Authority Partitioning**:
   - `USER_DISCOURSE` is authorized to produce `FACT` **ONLY** within `SCOPE_TYPE_MODAL` (e.g., "User asserts $X$"). It is **FORBIDDEN** from asserting extensional `FACT` in `SCOPE_TYPE_ROOT` regarding objective reality.
   - `PERCEPTUAL_HYPOTHESIS` is authorized to produce `FACT` **ONLY** for localized sensor observations (e.g., "Audio presence detected"); it is **FORBIDDEN** from asserting relational ontology facts directly.
   - `ASSISTANT_GENERATED` is **STRICTLY FORBIDDEN** from producing `FACT` or `INFERRED` premises for world knowledge.

---

## 6. INFERRED / Recursive Admissibility Falsification

R2 posited: *INFERRED propositions are admissible if and only if all supporting premises are themselves admissible under unbroken provenance.*

We test this rule across 10 critical stress cases:

### Falsification Stress Matrix

| Case | Scenario | Behavior under R2 Rule | Soundness Evaluation | Defect Identified |
|:---:|---|---|---|---|
| **A** | Premise is itself INFERRED | Recursively traces dependency tree. | **SOUND**: Standard JTMS transitive chaining. | None. |
| **B** | Premise is UNKNOWN | Strong Kleene: $\text{UNKNOWN} \land (P \to Q) \implies \text{UNKNOWN}$. | **SOUND**: Quadrant 1 emits `InformationSubgoal`. | None. |
| **C** | Mixed FACT + INFERRED | Multi-premise rule unification. | **SOUND**: Consequence is valid iff all premises hold. | None. |
| **D** | Rule definition changed | Upstream derived $Q$ using Rule $R_{v1}$; P23-H uses $R_{v2}$. | **UNSOUND**: Ingress accepts `rule_id` without verifying semantic rule hash. | **Missing Rule-Hash Check**. |
| **E** | Source premise retracted | Upstream source invalidates root premise. | **SOUND**: JTMS cascade queue invalidates downstream consequences in $\le 19\,\mu\text{s}$. | None. |
| **F** | Cyclic provenance tree ($A \to B \to A$) | Both $A$ and $B$ satisfy "all premises admissible". | **CATASTROPHIC**: Creates an immortal self-justifying loop (Doyle JTMS cycle bug). | **Missing Acyclicity Invariant**. |
| **G** | Incomplete provenance tree | Upstream provides derived term, but one premise is missing from `TermArena`. | **UNSOUND**: Orphaned justification node created in JTMS. | **Missing Completeness Invariant**. |
| **H** | External rule unknown to P23-H | Rule ID not registered in static `RuleIndex`. | **UNSOUND**: P23-H cannot verify or re-evaluate the inference. | **Forbidden External Rules**. |
| **I** | Two independent derivations of $Q$ | Consequence has 2 valid `Justification` records. | **SOUND**: Multi-justification retention functions correctly. | None. |
| **J** | Contradictory derivations ($Q$ and $\neg Q$) | Both derived via valid internal rules from different premises. | **SOUND**: Intercepted by `conflict.py`; both blocked from root assertion. | None. |

### Discoveries & Mandatory Invariants
Recursive Admissibility as stated by R2 is **INSUFFICIENT**. To be sound, it must enforce two additional non-negotiable invariants:
1. **Acyclic Justification Invariant (Well-Foundedness)**: The provenance graph of an ingress premise must form a strict Directed Acyclic Graph (DAG). Any circular justification ($A \vdash B \vdash A$) must be rejected immediately.
2. **Closed-World Rule Index Invariant**: Every `rule_id` on an `INFERRED` ingress candidate must exist within P23-H's pre-compiled, static `RuleIndex`. Dynamic or uninterned external rules are strictly rejected.

---

## 7. Scope Falsification

### The Falsification Challenge
> *Does scope actually belong to the proposition contract, or is it a higher-level graph property? Are both `scope_id` and `scope_type_id` required on the proposition?*

### Analysis & Falsification
In P23-G ([`src/core/cognition/contract/terms.py`](file:///c:/Users/Lunafiah/Desktop/My_project/Lucia/src/core/cognition/contract/terms.py#L31)):
- Scopes are first-class structural entities allocated in `TermArena`:
  ```python
  arena.allocate_scope(scope_type_id=SCOPE_TYPE_MODAL, parent_scope_id=0)
  ```
- Every `LogicalTerm` holds a single foreign-key integer: `scope_id: int`.

**Falsification of `scope_type_id` on the Proposition**:
- Attaching `scope_type_id` to `EpistemicallyQualifiedProposition` is a **denormalization defect**.
- If Proposition 1 states `scope_id=3, scope_type_id=MODAL` and Proposition 2 states `scope_id=3, scope_type_id=ROOT`, the contract contains an internal contradiction.
- `scope_type_id` is an intrinsic property of the **Scope**, NOT of the **Proposition**.
- **Conclusion**: `scope_type_id` is **FALSIFIED & REMOVED** from the proposition contract.

**Necessity of `scope_id`**:
- Can `scope_id` be removed? **NO**.
- Without `scope_id`, a proposition has no structural boundary. "User believes $X$" would be indistinguishable from "$X$ is an objective fact".
- **Conclusion**: `scope_id: int` is **IRREDUCIBLE & RETAINED**.

---

## 8. Source-Class Falsification

### The Falsification Challenge
> *Is `source_class` itself an epistemic primitive, or merely metadata used by external policy? Can two propositions with identical semantic content and epistemic status legitimately have different admissibility solely because `source_class` differs?*

### Empirical Counterfactual Proof
Consider two candidate assertions arriving at the ingress boundary:
- **Candidate 1**:
  - Content: `(User, likes, Jazz)`
  - Polarity: `True`
  - Scope: `SCOPE_TYPE_ROOT`
  - Source Class: `USER_DISCOURSE` (User said: *"I really like jazz."*)
- **Candidate 2**:
  - Content: `(User, likes, Jazz)`
  - Polarity: `True`
  - Scope: `SCOPE_TYPE_ROOT`
  - Source Class: `ASSISTANT_GENERATED` (Lucia asked: *"Do you like jazz?"*)

If `source_class` is eliminated:
- Both candidates present identical triples `(User, likes, Jazz)` in `ROOT` scope.
- If Candidate 1 is admitted as `FACT`, then Candidate 2 must also be admitted as `FACT`.
- Admitting Candidate 2 means Lucia's exploratory questions become established world facts about the user!

This proves that `source_class` is **NOT administrative metadata**. It is an **irrevocable epistemic gating condition**.
However, once the Ingress Gate uses `source_class` to authorize admission and set the target scope, P23-H's internal deductive engine does not need to compute over `source_class`.
**Conclusion**: `source_class` is **MANDATORY AT THE INGRESS GATE**, but **FORBIDDEN FROM MUTATING `LogicalTerm` INTERNALS IN P23-H**.

---

## 9. Temporal Horizon Falsification

### The Falsification Challenge
> *Is temporal validity an epistemic primitive, or merely lifecycle metadata? Does putting `valid_from` and `valid_until` into the minimal contract violate the architecture?*

### Formal Falsification of Ingress Temporal Fields
1. **Subsystem Mismatch**: P23-H is a bounded, static Horn-clause backward chaining engine. It has zero concept of time, zero access to a wall-clock or simulation tick, and no temporal logic operators ($G, F, U$).
2. **Zombie Retention Risk**: If `valid_until = 1700000000` is stored on a `LogicalTerm` in `TermArena`, who checks it? P23-H does not run a background thread (Invariant 6). An expired proposition sitting in `TermArena` will continue to be matched by backward goal chaining forever!
3. **The `valid_until = infinity` Trap**: For any proposition without a known expiration, callers set `valid_until = inf`, immediately re-introducing silent persistence escalation.

### Where Temporal Gating Actually Belongs
Temporal freshness is a **PRE-INGRESS MEMORY / CACHE LIFECYCLE PROPERTY**.
- The Memory Cache / Episodic Substrate must check:
  $$\text{now}() \le \text{expiration\_timestamp}$$
  *before* submitting the candidate to the Ingress Gate.
- If a proposition is expired, it is **never submitted for premise ingress**.
- P23-H working memory is strictly an *active context scratchpad*. Stale facts must be cleared by context resets, not by pushing temporal logic into the discrete reasoning kernel.
**Conclusion**: `valid_from` and `valid_until` are **FALSIFIED & REMOVED** from the core proposition ingress contract.

---

## 10. Provenance Falsification

Evaluating the four provenance fields proposed by R2:

1. **`rule_id: int`**:
   - Required for: JTMS justification registration.
   - Without it: An `INFERRED` proposition cannot be connected to an inference rule. Non-monotonic invalidation breaks.
   - *Verdict*: **RETAIN (Mandatory for INFERRED, 0 for FACT)**.
2. **`supporting_premise_ids: Tuple[int, ...]`**:
   - Required for: JTMS downward dependency tracking and recursive premise validation.
   - Without it: Retracting an upstream fact cannot invalidate downstream conclusions.
   - *Verdict*: **RETAIN (Mandatory for INFERRED, empty for FACT)**.
3. **`session_id: int`**:
   - Required for: Historical audit and session persistence.
   - Deductive relevance: Zero. A logical term unifies identically whether asserted in session 1 or session 2.
   - *Verdict*: **REDUNDANT (Belongs in external audit log, not minimal premise contract)**.
4. **`turn_id: int`**:
   - Required for: Relative temporal ordering.
   - Epistemic relevance: By itself, an integer `turn_id=4` does not convey causal meaning without a conversational graph.
   - *Verdict*: **REPLACE with explicit Causal Link** (see Section 15).

---

## 11. Non-Escalation Relation

R2 posited a linear partial order:
$$\text{REJECT} \prec \text{UNKNOWN} \prec \text{AMBIGUOUS} \prec \text{INFERRED} \prec \text{FACT}$$

### Falsification of the Linear Order
1. **AMBIGUOUS vs UNKNOWN**:
   - In information theory, `UNKNOWN` represents zero information (maximum entropy).
   - `AMBIGUOUS` represents a constrained hypothesis space ($\{h_1, h_2\}$). It contains *more* semantic information than `UNKNOWN`.
   - Yet in truth commitment, both are equally unassertable. Ranking them linearly is formally invalid.
2. **Modal Context Inversion**:
   - Consider a `FACT` inside `SCOPE_TYPE_MODAL` (e.g., "User claims she saw a ghost").
   - Consider an `INFERRED` proposition in `SCOPE_TYPE_ROOT` (e.g., derived physical consequence: "Water boils at 100°C").
   - The `INFERRED` proposition has absolute extensional commitment in reality. The `FACT` has zero commitment in reality (it only commits to the user having made a claim).
   - Linearly asserting that `FACT` $\succ$ `INFERRED` is a modal fallacy.

### The True Non-Escalation Coordinate Lattice
[RESEARCH INFERENCE]
Epistemic commitment is not a scalar. It is a **Three-Dimensional Coordinate Partial Order**:
$$\mathcal{E} = \langle \mathcal{S}_{\text{scope}}, \mathcal{K}_{\text{kleene}}, \mathcal{A}_{\text{authority}} \rangle$$

Where:
- $\mathcal{S}_{\text{scope}} \in \{\text{INTENSIONAL} \prec \text{MODAL} \prec \text{NEGATION} \prec \text{ROOT}\}$
- $\mathcal{K}_{\text{kleene}} \in \{\text{UNKNOWN} \prec \text{TRUE / FALSE}\}$
- $\mathcal{A}_{\text{authority}} \in \{\text{UNTRUSTED} \prec \text{HYPOTHETICAL} \prec \text{DERIVED} \prec \text{GROUNDED}\}$

**The Correct Non-Escalation Invariant**:
> **Ingress is non-escalating if and only if no coordinate in the commitment tuple $\mathcal{E}$ increases during transformation from upstream candidate to internal term:**
> $$\mathcal{E}(T_{\text{term}}) \preceq \mathcal{E}(C_{\text{candidate}})$$

---

## 12. K3 / Ingress Responsibility Boundary

The repository architecture requires strict division of responsibilities across the reasoning stack:

```text
┌──────────────────────────────────────────────────────────────┐
│ UPSTREAM CANDIDATE EMISSION (Perception / Memory / Discourse)│
└──────────────────────────────┬───────────────────────────────┘
                               │ CandidateAssertion
                               ▼
┌──────────────────────────────────────────────────────────────┐
│ EPISTEMIC INGRESS GATE (Pre-Core Boundary)                   │
│ - Validates source authority & causal origin                 │
│ - Enforces modal scope isolation (no scope promotion)        │
│ - Verifies justification DAG acyclicity (Well-foundedness)    │
│ - Certifies EpistemicStatus {FACT, INFERRED, UNKNOWN}        │
└──────────────────────────────┬───────────────────────────────┘
                               │ Certified LogicalTerm
                               ▼
┌──────────────────────────────────────────────────────────────┐
│ COGNITIVE CORE WORKING MEMORY (TermArena)                    │
│ - Preallocated static numeric buffers                        │
│ - Polar conflict detection (conflict.py)                     │
└──────────────────────────────┬───────────────────────────────┘
                               │ Active Terms
                               ▼
┌──────────────────────────────────────────────────────────────┐
│ REASONING KERNEL (P23-H)                                     │
│ - Bounded backward goal chaining (engine.py)                 │
│ - Static Horn rule matching (rules.py)                       │
│ - 4-Quadrant Strong Kleene K3 evaluation (FIX-23H-01)        │
└──────────────────────────────┬───────────────────────────────┘
                               │ Consequence / Retraction
                               ▼
┌──────────────────────────────────────────────────────────────┐
│ TRUTH MAINTENANCE (JTMS)                                     │
│ - Non-monotonic cascade invalidation queue (jtms.py)         │
│ - Multi-justification retention                              │
└──────────────────────────────────────────────────────────────┘
```

**Key Invariant**:
- Ingress does NOT prove theorems or chain rules.
- P23-H does NOT filter sources or calibrate probabilities.
- K3 evaluates truth values; it does NOT police premise admission.

---

## 13. Contradiction

R2 proposed "source-qualified contradiction". We test its limits:

1. **Cross-Source Contradiction ($A_{\text{source1}} \land \neg A_{\text{source2}}$)**:
   - Evaluated: Both placed in their respective modal scopes (`scope:source1`, `scope:source2`).
   - Root scope remains `UNKNOWN`.
   - `conflict.py` emits `ConflictRecord`. CAPS generates `CLARIFY`.
   - *Verdict*: **SOUND**.
2. **Intra-Source Contradiction ($A_{\text{source1}} \land \neg A_{\text{source1}}$)**:
   - Evaluated: Source 1 contradicts itself in the same turn or across turns.
   - Source-qualification fails: placing both in `scope:source1` corrupts that scope.
   - *Resolution*: The Ingress Gate must detect self-contradiction, invalidate the prior assertion, and downgrade both to `EpistemicStatus.AMBIGUOUS`.
3. **Fact vs Inferred Contradiction ($A_{\text{FACT}} \land \neg A_{\text{INFERRED}}$)**:
   - An empirical observation conflicts with a theoretical inference.
   - In P23-H, observational ground truth dominates fallible deduction. The inferred term's justification is flagged for review; the `FACT` remains active.

---

## 14. Historical Evidence

### The Dilemma
> *An expired proposition ("User lived in Paris in 2020") is not valid as a present-tense premise ("Where is User right now?"). But it is valid historical evidence. Does rejecting expired propositions destroy historical reasoning?*

### The Architectural Resolution
[RESEARCH INFERENCE]
The dilemma arises solely from assuming that all propositions enter a flat root scope.
In Lucia's scoped architecture:
- **Active Working Premise**: Pertains to current conversational context. Belongs in `SCOPE_TYPE_ROOT` (Present).
- **Historical Evidence**: Pertains to autobiographical / episodic memory. Belongs in an **Intensional Historical Scope** (`SCOPE_TYPE_INTENSIONAL`).
- Historical propositions enter P23-H **ONLY** when a backward goal explicitly targets historical derivation (e.g. `has_lived_in(User, City)`).
- An expired proposition is **NEVER** admitted into active present-tense root scope, but remains queryable under explicit historical rule scopes.

---

## 15. F15 Self-Echo Attack

### The Attack Walkthrough
1. **Turn 1 (Assistant Probe)**:
   Lucia's conversational policy outputs an exploratory question:  
   *"Do you like classical piano music?"* ($H$)
2. **Turn 2 (User Conversational Agreement)**:
   User responds conversationally:  
   *"Yeah, sure."*
3. **Upstream Extraction**:
   Extractor detects user agreement $\rightarrow$ constructs triple `(User, likes, ClassicalPiano)`.
   Labels source as `USER_DISCOURSE`.
4. **Ingress Evaluation under R2 Contract**:
   R2 contract inspects candidate:
   - Source: `USER_DISCOURSE`
   - Content: `(User, likes, ClassicalPiano)`
   - R2 admits proposition into working memory as `FACT`!
5. **Turn 3 (Hallucination Fortification)**:
   P23-H now uses `FACT(User, likes, ClassicalPiano)` as established ground truth. Downstream reasoning deduces recommendations. Lucia asserts: *"Since you love classical piano..."*
6. **Cycle Repeats**:
   Lucia validated and magnified her own exploratory speculation without independent user confirmation.

### Why R2 Failed
The R2 contract inspected only the *current turn's speaker*. Because the user uttered "Yeah, sure", the source was marked `USER_DISCOURSE`. R2 lacked any causal awareness of *what prompted the utterance*.

### The Minimal Information Needed to Defeat F15
To defeat F15, the Ingress Gate requires **EXACTLY ONE PIECE OF CAUSAL METADATA**:
$$\text{causal\_prompt\_type} \in \{\text{SPONTANEOUS\_USER\_INITIATIVE}, \text{ASSISTANT\_CONFIRMATORY\_RESPONSE}\}$$

- If `SPONTANEOUS_USER_INITIATIVE`: User initiated the topic unprompted $\rightarrow$ Admissible as `FACT` in user modal scope.
- If `ASSISTANT_CONFIRMATORY_RESPONSE`: User was responding to an assistant suggestion $\rightarrow$ **DOWNGRADED TO `EpistemicStatus.UNKNOWN` or `AMBIGUOUS`**. It cannot become `FACT` until independent secondary evidence occurs.

---

## 16. R2 vs Reduced vs Safe Contract

We formulate the three required comparative specifications:

### Contract A: R2 Contract (As Proposed in R2)
```python
# 12 Fields - Bloated, Denormalized, Vulnerable to F15
@dataclass(frozen=True)
class R2Contract:
    predicate_id: int
    arg0_id: int
    arg1_id: int
    arg2_id: int
    polarity: bool
    epistemic_status: EpistemicStatus       # Untrusted input defect
    scope_id: int
    scope_type_id: int                      # Denormalization defect
    source_class: IngressSourceClass        # Flat, no causal antecedent
    session_id: int                         # Redundant metadata
    turn_id: int                            # Redundant metadata
    rule_id: int
    supporting_premise_ids: Tuple[int, ...]
    valid_from: float                       # Wrong layer
    valid_until: float                      # Wrong layer
```

### Contract B: Reduced Contract (Surgically Minimal, but Incomplete)
*Removes every field that is not strictly needed for basic Horn unification:*
```python
# 6 Fields - Minimal, but Fails F15 and Modal Isolation
@dataclass(frozen=True)
class ReducedContract:
    predicate_id: int
    arg0_id: int
    arg1_id: int
    arg2_id: int
    polarity: bool
    scope_id: int
```
*Why Reduced Fails*: Lacks derivation provenance (destroys JTMS retraction) and lacks source/causal tracking (destroys F15 protection).

### Contract C: Safe Contract (Architecturally Validated Minimal Boundary)
*Adds ONLY fields proven irreducibly necessary to satisfy logical soundness, JTMS retraction, modal containment, and F15 defense:*

```python
@dataclass(frozen=True)
class SafeIngressCandidate:
    """
    Certified Minimal Epistemic Ingress Candidate Contract.
    Evaluated by Ingress Gate BEFORE admission into P23-H TermArena.
    """
    # 1. Semantic Core (Numeric IDs)
    predicate_id: int                       # Interned concept ID
    arg0_id: int                            # Primary argument entity ID
    arg1_id: int = 0                        # Secondary argument entity ID
    arg2_id: int = 0                        # Tertiary argument entity ID
    polarity: bool = True                   # True = Positive, False = Polar negation

    # 2. Structural Scope Anchor
    scope_id: int = 1                       # Points to existing ScopeTerm in TermArena

    # 3. Source Origin & Causal Link (F15 Echo Defense)
    source_class: IngressSourceClass        # USER_DISCOURSE, PERCEPTUAL, DERIVED, MEMORY
    is_assistant_prompted: bool = False     # TRUE if turn responds to prior assistant probe

    # 4. Derivation Tree (Mandatory if source_class == DERIVED)
    rule_id: int = 0                        # Registered rule ID in P23-H RuleIndex
    supporting_premise_ids: Tuple[int, ...] = () # Must be active in TermArena; must be a DAG
```

### Comparative Summary Table

| Evaluation Vector | R2 Contract | Reduced Contract | Safe Contract |
|---|:---:|:---:|:---:|
| **Field Count** | 15 fields | 6 fields | **8 fields** |
| **P23-H Layer Purity** | Violated (temporal fields) | Pure | **Pure** |
| **Scope Normalized** | No (denormalized type) | Yes | **Yes** |
| **JTMS Retraction Supported**| Yes | No (broken) | **Yes** |
| **F15 Echo Loop Defense** | **FAILS (Vulnerable)** | **FAILS (Vulnerable)** | **DEFENDED (`is_assistant_prompted`)** |
| **Untrusted Status Hole** | Present | N/A | **ELIMINATED (Gate Assigns Status)** |

---

## 17. Remaining Semantic Uncertainty

While the *Safe Ingress Contract* reduces field complexity from 15 to 8 and eliminates denormalization errors, a single fundamental epistemic question remains unproven:

### The Semantic Uncertainty
The boolean flag `is_assistant_prompted: bool` is necessary to stop the F15 Echo Attack.
However:
*How does an upstream system determine whether a user utterance is "prompted" by a prior assistant turn without running a full conversational speech-act discourse tracker?*

If a user says *"Yeah"* after Lucia asked *"Are you tired?"*, it is clearly prompted.
What if the user says: *"Yeah, and by the way, I need to buy milk."*?
- Part of the utterance is prompted (`tired`).
- Part of the utterance is spontaneous (`buy milk`).

If the ingress boundary cannot isolate the prompted clause from the spontaneous clause, it will either:
- **False Negative**: Fail to tag the prompted clause, letting the echo attack succeed.
- **False Positive**: Over-tag the entire turn, rejecting legitimate spontaneous user facts.

---

## 18. FINAL VERDICT

### Selected Verdict: **CONDITIONAL — ONE MORE RESEARCH QUESTION**

### Name of the Exactly ONE Issue:
> **The F15 Clause-Level Causal Attribution Boundary**:  
> *How does the semantic extraction layer formally distinguish an assistant-prompted confirmation from a spontaneous user assertion within the same conversational turn, so that the Ingress Gate can safely assign `is_assistant_prompted` without requiring a full pragmatic discourse parser?*

### Justification
1. The contract structure itself is now sound, minimal, and normalized (the *Safe Contract*, Section 16).
2. All wrong-layer temporal and denormalized scope fields from R2 have been successfully eliminated.
3. However, the contract cannot be frozen because its primary security mechanism (`is_assistant_prompted`) depends on a causal extraction primitive that is currently undefined in the repository. Freezing the contract now would freeze an ungrounded interface.

---

## 19. Recommended Next Step

1. **Do NOT Implement Runtime Code**: Maintain zero code changes in `src/core/` and keep P23-H frozen at commit `3eef803`.
2. **Execute Targeted Research Spike (R4)**:
   Focus exclusively on the single unresolved blocker:
   *Define the minimal structural interface between upstream Turn Extraction (S8) and Ingress Candidate Causal Tagging (`is_assistant_prompted`).*
3. **Preserve Repository Baselines**:
   Maintain `data/profile.json` locked, ensure zero net heap growth, and adhere strictly to 20W CPU edge execution constraints.
