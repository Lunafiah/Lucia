# P23-H E3-R2 — Epistemic Ingress Contract Falsification

**Document ID**: DOC-P23H-E3-R2-FALSIFICATION-001  
**Authority**: Research Read-Only Falsification Report  
**Status**: `[RESEARCH / FALSIFICATION COMPLETED / NO PRODUCTION CHANGES]`  
**Date**: 2026-10-20  
**Target Path**: `docs/others/epistemic_ingress_research/P23H_E3_R2_EPISTEMIC_INGRESS_FALSIFICATION_REPORT.md`  

---

## 1. Executive Verdict

### **CONDITIONAL GO** (Candidate Contract Falsified; Principled Boundary Feasible Under Strict Epistemic Qualifications)

**Verdict Summary**:
1. **Candidate Contract Falsified**: The proposed 5-field candidate contract (`EpistemicallyQualifiedProposition`) is **FALSIFIED**. It is simultaneously *non-minimal* (contains redundant implementation-level state `validity`) and *epistemically insufficient* (lacks modal scope qualification, lacks source authority classes, lacks temporal freshness boundaries, and is vulnerable to F15 conversational echo loops).
2. **Scalar Confidence Promotion Rejected**: Naive and qualified confidence-to-premise thresholds ($c \ge \theta \implies \text{FACT}$) are unconditionally **REJECTED** [REPOSITORY FACT, NEG-02]. No scalar threshold can universally justify symbolic certainty without corrupting Strong Kleene K3 semantics.
3. **INFERRED Premise Grounding**: Upstream `INFERRED` propositions may enter P23-H **ONLY** under *Recursive Admissibility with Unbroken Provenance* (Model D). Inferred propositions entering as ungrounded axioms (Model A) or without premise trees are strictly rejected.
4. **Universal Contract Feasibility**: A single, flat, universal contract across all upstream source classes is **IMPOSSIBLE** (Outcome B/C). Different source classes possess irreducibly distinct epistemic authorities, modal scopes, and causal liabilities.
5. **No Immediate Implementation Authorization**: While a principled boundary contract can be formulated conceptually, runtime implementation remains blocked by upstream repository gaps (unstable proposition identity in KnowledgeStore, missing conversational provenance, and absence of endogenous reasoning goal dispatch).

---

## 2. Research Scope

This research study evaluates the epistemic ingress boundary of **Phase 23-H** (`src/core/cognition/kernel/`), a bounded, deterministic, backward goal-directed reasoning kernel with Strong Kleene three-valued logic ($TRUE, FALSE, UNKNOWN$) and Justification-Based Truth Maintenance (JTMS), frozen at commit `3eef803`.

The study investigates the fundamental question:
> *What epistemic guarantees are irreducibly required before ANY upstream representation may cross the symbolic premise boundary into P23-H without converting continuous uncertainty, source assertions, stale information, ambiguity, contradiction, or assistant-generated content into unjustified binary certainty?*

### Constraints & Invariants
- **Read-Only**: Zero production code modifications, zero runtime modifications, zero database schema mutations.
- **Subsystem Boundary**: P23-I remains permanently closed as an independent subsystem [REPOSITORY FACT, PHASE_REGISTRY.md].
- **Preserved Invariants**:
  - `INV-1`: One Continuous Life & Anti-Branching.
  - `INV-2`: No Reflective Ego.
  - `INV-5`: 100% Edge Execution (0.0 MB GPU VRAM, 20W Whole Brain Architecture).
  - `INV-8`: Genesis Gate Locked (`data/profile.json == {"is_onboarded": false}`).
  - `EPISTEMIC INVARIANT`: **UNKNOWN MUST NEVER SILENTLY BECOME CERTAINTY.**

---

## 3. Existing Repository Evidence

Every finding is classified strictly under repository evidence discipline:

### 3.1 Phase 23-C & Phase 23-F (Semantic Substrate & Adapter)
- [REPOSITORY FACT] `src/core/language/adapter/` isolates natural language parsing from cognitive core terms, supporting strictly `{en, vi, ja}` with zero string leakage into the core.
- [VALIDATED EXISTING CONTRACT] Japanese zero-anaphora and ungrounded syntactic arguments are mapped strictly to `EpistemicState.UNKNOWN` rather than hallucinated entities [SOURCE_MAP.md §7.2].

### 3.2 Phase 23-G (Semantic Substrate → Cognitive Core Contract)
- [REPOSITORY FACT] `src/core/cognition/contract/` implements numeric representations:
  - `arena.py`: `TermArena` preallocates static buffers (4096 terms, 1024 entities, 256 scopes). Zero dynamic heap allocations in steady-state reasoning.
  - `epistemic.py`: `EpistemicStatus` (IntEnum: `FACT=1`, `INFERRED=2`, `AMBIGUOUS=3`, `UNKNOWN=4`). Strong Kleene three-valued logic `KleeneValue` (`FALSE=0`, `TRUE=1`, `UNKNOWN=2`).
  - `terms.py`: `LogicalTerm` represents n-ary relations with numeric concept/argument/role IDs, `epistemic_status`, `polarity: bool`, `rule_id: int`, `premise_ids: Tuple[int, ...]`, and `provenance: Optional[ProvenanceRecord]`.
  - `provenance.py`: `ProvenanceRecord` tracks `rule_id`, `supporting_premise_ids`, `session_id`, `turn_id`, `timestamp`, and `confidence`.
  - `projection.py`: `ProjectGraphToTerms(graph, arena, symbol_table)` projects `SemanticGraph` into `TermArena`.
- [VALIDATED EXISTING CONTRACT] `ProjectGraphToTerms` performs a 1:1 mapping of `node.epistemic_state` to `EpistemicStatus`. It performs no epistemic filtration or validity validation; it assumes upstream nodes have been fortified [src/core/cognition/contract/projection.py:242].

### 3.3 Phase 23-H (Reasoning Kernel)
- [REPOSITORY FACT] `src/core/cognition/kernel/` implements:
  - `engine.py`: Backward goal chaining with `MAX_SEARCH_DEPTH = 8`, `MAX_INFERENCE_STEPS = 256`.
  - `jtms.py`: Multi-justification non-monotonic truth maintenance. Premise retraction cascades invalidation via static queue buffer ($12\text{--}19\,\mu\text{s}$).
  - `conflict.py`: Polar contradiction check ($P(e) \land \neg P(e)$) generating `ConflictRecord`.
  - `rules.py`: Static Horn rules with $O(1)$ head-predicate index.
- [VALIDATED EXISTING CONTRACT] `FIX-23H-01` (commit `3eef803`) corrected denying the antecedent: unproven goals evaluate strictly to `KleeneValue.UNKNOWN` and emit `InformationSubgoal` (Quadrant 1), never `KleeneValue.FALSE` [P23-H_FINAL_STATE.md].

### 3.4 ARCH-030 / ARCH-030.1 & Phase 23-I Evidence Closure
- [REPOSITORY FACT] Phase 23-I was rejected as an independent runtime subsystem. Its requirements were absorbed into ARCH-030.1 as a contract boundary [PHASE_REGISTRY.md].
- [VALIDATED EXISTING CONTRACT] `NEG-02` formally rejected naive confidence thresholding ($c \ge \theta \implies \text{Assert}(\text{Fact})$). Perceptual uncertainty cannot be converted to propositional certainty [P23-I_EVIDENCE_CLOSURE_AND_FALSIFICATION_REPORT.md §3].

### 3.5 KnowledgeStore (Phase 16)
- [REPOSITORY FACT] `src/core/knowledge/store.py` stores `Proposition(id, subject, predicate, object, confidence, provenance, evidence_ids, created_at, valid, superseded_by)`.
- [REPOSITORY FACT] Storage uses an unindexed dict keyed by arbitrary caller ID. Transitive derivation generates random UUIDs (`derived:{uuid.uuid4().hex[:8]}`). No semantic deduplication exists [EP_REAS_FORMATION_FEASIBILITY_AUDIT.md §A, §C].
- [REPOSITORY FACT] Contradiction detection is limited to 6 single-valued predicates (`equals`, `has_shape`, `has_color`, `capital_of`, `successor_of`, `father_of`). All other relational contradictions are ignored.

### 3.6 Fortification (Phase 23-E)
- [VALIDATED EXISTING CONTRACT] `src/core/knowledge/fortification.py` enforces:
  - `UNKNOWN -> FACT / INFERRED` is strictly forbidden.
  - `AMBIGUOUS -> FACT / INFERRED` is forbidden without explicit upstream `disambiguation_event`.
  - Zero novel entity insertion during fortification [fortification.py:775-785].

---

## 4. Candidate Contract Under Test

The candidate contract under test is formulated as:

```text
EpistemicallyQualifiedProposition:
  - proposition: Relational triple or logical assertion
  - epistemic_status: {FACT, INFERRED, AMBIGUOUS, UNKNOWN, REJECT}
  - provenance: Source citation / derivation metadata
  - scope: Structural / modal container
  - validity: Boolean active / retracted flag

Candidate Invariant:
  INGRESS MUST NOT INCREASE EPISTEMIC COMMITMENT.

Candidate Projection:
  - qualified FACT      → FACT premise
  - qualified INFERRED  → symbolic information with traceable support
  - AMBIGUOUS           → UNKNOWN / disambiguation
  - UNKNOWN             → UNKNOWN / information-subgoal
  - invalid / unproven  → REJECT
```

---

## 5. Field-by-Field Minimality Analysis

We evaluate each candidate field against four formal criteria:
- **A. Logically Necessary?**
- **B. Removable without Unsoundness?**
- **C. Safely Derivable from Another Field?**
- **D. Implementation Concern vs Epistemic Requirement?**

### Minimality Table

| Field | A. Logically Necessary? | B. Removable? | C. Derivable? | D. Nature | Minimality Verdict |
|---|:---:|:---:|:---:|---|:---:|
| **`proposition`** | **YES** | **NO** | **NO** | Core Semantic Requirement | **RETAIN** (Required) |
| **`epistemic_status`** | **YES** | **NO** | **NO** | Core Epistemic Requirement | **RETAIN** (Required) |
| **`provenance`** | **YES** | **NO** | **NO** | Core Epistemic Requirement | **RETAIN** (Required) |
| **`scope`** | **YES** | **NO** | **NO** | Core Epistemic Requirement | **RETAIN** (Required) |
| **`validity`** | **NO** | **YES** | **YES** (from lifecycle/status) | Storage Implementation Concern | **ELIMINATE** (Redundant) |

### Detailed Field Rationale

1. **`proposition`**:
   - *Necessity*: Without semantic content (predicate, arguments, roles, polarity), reasoning has no terms to bind or unify.
   - *Verdict*: Irreducible.

2. **`epistemic_status`**:
   - *Necessity*: P23-H is a three-valued Strong Kleene engine. Without explicit epistemic qualification, the engine cannot distinguish an observational ground truth from an ungrounded variable or an active hypothesis.
   - *Verdict*: Irreducible.

3. **`provenance`**:
   - *Necessity*: JTMS non-monotonic retraction relies strictly on dependency tracking. If a supporting premise is invalidated upstream, P23-H must know which terms depend on it. Furthermore, provenance identifies causal origin (preventing self-echo loops).
   - *Verdict*: Irreducible.

4. **`scope`**:
   - *Necessity*: Ingesting propositions without structural scope bounds commits modal collapse. For example, "User believes $X$" cannot enter `SCOPE_TYPE_ROOT` as "$X$ is true". Scopes (`ROOT`, `NEGATION`, `MODAL`, `INTENSIONAL`) prevent intensional propositions from corrupting extensional facts.
   - *Verdict*: Irreducible.

5. **`validity`**:
   - *Redundancy Analysis*: In the candidate contract, `validity` is a separate boolean (`True`/`False`). This introduces an ungrounded product state space:
     $$\text{validity} = \text{False} \land \text{epistemic_status} = \text{FACT}$$
     What does an "invalid FACT" mean at the ingress boundary? It is a contradiction in terms.
   - *Derivability*: If a proposition is invalid, its epistemic status is `REJECT` (or it triggers a retraction event). `validity` is a storage record artifact from `KnowledgeStore` (soft-deletion via `prop.valid = False`), NOT an independent epistemic primitive.
   - *Verdict*: **ELIMINATE**. Ingress evaluates only valid candidate propositions; invalidated ones are mapped to `REJECT` or retract existing terms.

### Missing Essential Fields Discovered During Minimality Analysis
While `validity` is redundant, the candidate contract is **epistemically incomplete** because it omits two indispensable fields:
1. **`temporal_validity` (Freshness / Validity Window)**: Without a temporal timestamp and validity horizon ($[t_{start}, t_{end}]$), transient observations become immortal facts.
2. **`source_class` (Authority Type)**: Provenance as a flat identifier fails to distinguish user direct statements from perceptual sensor readings or assistant self-generation.

---

## 6. Confidence Promotion Falsification

We explicitly test whether scalar confidence can be mapped to symbolic truth:

### 6.1 Test: `confidence -> FACT` ($c \ge \theta \implies \text{FACT}$)
- **Hypothesis**: A proposition with confidence above a calibrated threshold (e.g. $\theta = 0.95$) is epistemically entitled to enter P23-H as a `FACT`.
- **Falsification Counterexample (Acoustic Homophone)**:
  An ASR acoustic sensor transcribes user speech as *"I hate you"* with acoustic confidence $c = 0.992$. In reality, the user said *"I ate, thank you"*, obscured by background noise.
  Under $c \ge 0.95 \implies \text{FACT}$, P23-H asserts `LogicalTerm(predicate=hate, arg0=User, arg1=Lucia)` as an absolute positive ground fact.
  Because P23-H treats `FACT` as unassailable ground truth, it triggers interpersonal defense mechanisms.
- **Epistemic Flaw**: High perceptual confidence measures *signal-to-noise ratio in sensor feature space*, NOT *ontological truth in reality*.
- **Verdict**: **FALSIFIED & REJECTED** [NEG-02].

### 6.2 Test: `confidence + source type -> FACT` ($c \ge \theta \land \text{source} \in \mathcal{S}_{trusted} \implies \text{FACT}$)
- **Hypothesis**: Restricting high confidence to trusted sources (e.g. direct user statements or calibrated sensors) justifies symbolic certainty.
- **Falsification Counterexample (Delusional or Metaphorical User Statement)**:
  The user states: *"I have been awake for 400 years."*
  Source type = `USER_STATED`, confidence = $1.0$ (direct, unambiguous lexical match).
  Under the rule, P23-H asserts `LogicalTerm(predicate=awake_duration, arg0=User, arg1=400_years)` as an extensional `FACT` in `SCOPE_TYPE_ROOT`.
  Downstream, this premise conflicts with biological reality, generating unresolvable contradictions in world-knowledge inference.
- **Epistemic Flaw**: A user statement is an authoritative fact regarding *the user's utterance act*, but NOT an authoritative fact regarding *objective world state*. Conflating pragmatic source reliability with domain factuality violates modal separation.
- **Verdict**: **FALSIFIED & REJECTED**.

### 6.3 Test: `confidence + provenance -> FACT`
- **Hypothesis**: Combining high confidence with a complete derivation provenance justifies symbolic truth.
- **Falsification Counterexample (Correlated Common-Cause Failure)**:
  Three independent sensors (Camera 1, Camera 2, Optical Flow) report *"Person in room"* with $c = 0.92, 0.88, 0.91$.
  Bayesian updating aggregates these into $c_{agg} = 0.999$, with explicit multi-sensor provenance records.
  However, all three optical sensors were blinded by a single strobe light flash (common-cause sensor correlation).
  Asserting `FACT` permanently installs the term in `TermArena`. When the strobe clears, none of the sensors retract (they merely report absence in new turns), leaving an unretracted phantom fact.
- **Verdict**: **FALSIFIED & REJECTED**.

### Universal Law of Ingress Falsification
> **NO SCALAR CONFIDENCE THRESHOLD CAN TRANSFORM CONTINUOUS UNCERTAINTY INTO DEDUCTIVE PROPOSITIONAL CERTAINTY.**  
> Continuous confidence belongs to the observation/probabilistic substrate. Crossing into symbolic P23-H requires discrete, defeasible, modal qualification.

---

## 7. INFERRED Premise Analysis

We evaluate five competing models for admitting `INFERRED` propositions into P23-H:

### Evaluation Matrix

| Model | Epistemic Consequence | Logical Soundness | Retraction Behavior | Provenance Overhead | Contradiction Behavior | Verdict |
|---|---|---|---|---|---|:---:|
| **Model A: INFERRED treated exactly like FACT** | Severe flattening; fallible inference treated as foundational axiom. | Soundness collapse; masks defeasibility. | **Catastrophic**: Upstream retraction leaves immortal zombie facts in P23-H. | Low (zero tracking). | P23-H cannot identify which assumption caused conflict. | **REJECTED** |
| **Model B: INFERRED admitted with local provenance** | Defeasible admission; tracks rule ID and premise IDs. | Sound if upstream provenance is fully verifiable. | Partial: Retracts only if upstream explicitly notifies P23-H. | Medium: Requires TermArena provenance records. | Traceable to local rule, but blind to upstream roots. | **CONDITIONAL** |
| **Model C: INFERRED mapped to UNKNOWN** | Hyper-skeptical collapse; discards all upstream derivation. | Sound, but vacuous; eliminates all multi-step inference. | Trivial (no state created). | Zero. | Trivial. | **REJECTED** (Too Restrictive) |
| **Model D: Recursive Admissibility with Unbroken Provenance** | Sound: Inferred term is valid iff all upstream supporting premises are admissible. | Fully sound; preserves truth-preservation across boundary. | **Exact**: Upstream invalidation cascades through JTMS queue cleanly. | High: Requires full dependency tree interning. | Full causal attribution; isolates faulty premise. | **ACCEPTED / REQUIRED** |
| **Model E: INFERRED rejected entirely** | P23-H restricted strictly to atomic ground observations. | Sound, but forces P23-H to re-derive all knowledge locally. | Trivial. | Zero. | Trivial. | **REJECTED** (Overly Constrained) |

### Formal Resolution of the INFERRED Question
`INFERRED` propositions may legitimately become P23-H premises **IF AND ONLY IF** they satisfy **Model D (Recursive Admissibility)**:
1. The inference rule is registered in P23-H `RuleIndex` or a verified upstream rule contract.
2. Every supporting premise in the justification tree is already interned and active in `TermArena`.
3. JTMS registers an explicit `Justification` record binding the consequence to its premises.
4. If an upstream premise is retracted, JTMS cascade invalidation recursively revokes the inferred premise.

If an upstream inference arrives as a pre-computed conclusion without its supporting premise tree, it **MUST NOT** enter P23-H as `INFERRED` or `FACT`. It must be treated as `UNKNOWN` (emitting an `InformationSubgoal` to verify premises) or `REJECT`.

---

## 8. Counterfactual Test Matrix

We test the candidate contract against the 12 mandatory edge cases:

| Case | Scenario Description | Candidate Contract Action | Epistemic Soundness Evaluation | Pass / Fail |
|:---:|---|---|---|:---:|
| **1** | High confidence + ambiguous semantic identity | Status = `AMBIGUOUS`. Emits `DisambiguationSubgoal` or maps to `UNKNOWN`. | **SOUND**: Prevents premature collapse to arbitrary sense. | **PASS** |
| **2** | Low confidence + independently verified proposition | Independent verification enters via verified provenance (`FACT`); low-confidence trace is superseded. | **SOUND**: Grounded verification dominates sensor noise without ad-hoc averaging. | **PASS** |
| **3** | Two high-confidence contradictory sources ($A \land \neg A$) | Candidate emits `ConflictRecord`; both blocked from entering as simultaneous `FACT`s in root scope. | **SOUND**: Preserves contradiction; prevents explosive inconsistency. | **PASS** |
| **4** | Old / stale proposition with high confidence | Candidate contract **lacks temporal field**; admits stale fact as current `FACT`. | **UNSOUND**: Temporal decay ignored; dead facts persist indefinitely. | **FAIL** (Contract Incomplete) |
| **5** | User statement with high confidence | Candidate asserts `FACT` in `SCOPE_TYPE_ROOT` without modal wrapping. | **UNSOUND**: Confuses user assertion with objective truth. Must be scoped to `SCOPE_TYPE_MODAL`. | **FAIL** (Modal Collapse) |
| **6** | Assistant-generated statement repeated later | Candidate lacks communication provenance; treats user repeating assistant suggestion as new user evidence. | **UNSOUND**: F15 Echo Loop. System validates its own hallucination. | **FAIL** (Echo Vulnerability) |
| **7** | Inference supported by valid premises | Evaluates under Model D; registers `Justification` in JTMS. | **SOUND**: Bounded non-monotonic deduction preserved. | **PASS** |
| **8** | Inference supported by an UNKNOWN premise | Under Strong Kleene K3: $\text{UNKNOWN} \land (P \to Q) \implies \text{UNKNOWN}$. Candidate rejects premise or maps to `InformationSubgoal`. | **SOUND**: Prevents epistemic leakage through incomplete inference. | **PASS** |
| **9** | UNKNOWN proposition with valid semantic identity | Status = `UNKNOWN`. Mapped to `InformationSubgoal` (Quadrant 1). | **SOUND**: Preserves ignorance without asserting falsity (`FIX-23H-01`). | **PASS** |
| **10** | Same proposition & confidence, different source semantics | Candidate has no source-class authority hierarchy; treats user and assistant outputs identically. | **UNSOUND**: Symmetric treatment of asymmetric sources. | **FAIL** (Source Blindness) |
| **11** | Repeated weak evidence producing high aggregate confidence | Aggregation without causal independence verification asserts `FACT`. | **UNSOUND**: Correlated noise accumulation treated as certainty. | **FAIL** (Causal Blindness) |
| **12** | Proposition whose source later retracts evidence | JTMS cascades retraction across boundary, invalidating consequence terms. | **SOUND**: Multi-justification non-monotonic maintenance functions correctly. | **PASS** |

### Test Matrix Summary
- **Passed**: 7 / 12 cases.
- **Failed**: 5 / 12 cases (Cases 4, 5, 6, 10, 11).
- **Primary Failure Modes**:
  1. Lack of temporal validity horizon (Case 4).
  2. Modal scope collapse (Case 5).
  3. F15 Conversational echo loop vulnerability (Case 6).
  4. Source authority blindness (Case 10).
  5. Causal independence violation in evidence accumulation (Case 11).

---

## 9. Non-Escalation Invariant Analysis

### Formal Definition
The candidate invariant states:
> *INGRESS MUST NOT INCREASE EPISTEMIC COMMITMENT.*

Formally, epistemic commitments form a bounded partial order (lattice):
$$\text{REJECT} \prec \text{UNKNOWN} \prec \text{AMBIGUOUS} \prec \text{INFERRED} \prec \text{FACT}$$

Non-escalation requires that for any upstream representation $U$ projected into symbolic term $T$:
$$\text{Commitment}(T) \preceq \text{Commitment}(U)$$

### Falsification: Subtle Escalation Counterexamples
Even when `epistemic_status` is nominally preserved, epistemic commitment can be silently escalated through structural transformations:

1. **Modal Stripping (Scope Elevation)**:
   - Upstream: *"User says she might travel to Tokyo"* $\rightarrow$ Modal scope `MODAL(User, MIGHT(travel(Tokyo)))`.
   - Ingress: Normalizes to `LogicalTerm(predicate=travel, arg0=User, arg1=Tokyo, epistemic_status=FACT)`.
   - *Escalation*: A hypothetical modal attitude was stripped into an unconditioned physical fact in root scope.

2. **Proposition Merging (Unification Escalation)**:
   - Upstream has two separate references: $U_1$: *"A cat was seen"* ($UNKNOWN$ identity) and $U_2$: *"A black animal was seen"* ($UNKNOWN$ identity).
   - Ingress merges both into `Entity(concept=BlackCat, epistemic_status=FACT)`.
   - *Escalation*: Synthesizing two ungrounded observations into a single specific entity creates unearned semantic commitment.

3. **Assistant Self-Ingestion (Echo Escalation)**:
   - Upstream turn $t$: Assistant outputs *"You seem tired today."*
   - Turn $t+1$: User says *"Yeah."*
   - Ingress creates `FACT(User, is_tired)`.
   - *Escalation*: The assistant's own speculative probe is validated as factual truth through conversational agreement.

4. **Persistence Escalation (Temporal Immortality)**:
   - Upstream: *"User is currently drinking coffee"* ($t = 10:00$, duration $\approx 15\text{ min}$).
   - Ingress enters `FACT(User, drinking, Coffee)` without expiration.
   - At $t = 16:00$, P23-H still reasons over the active premise that the user is drinking coffee.
   - *Escalation*: Ephemeral state escalated to static, eternal truth.

### Verdict on Candidate Invariant
The invariant sentence *"Ingress must not increase epistemic commitment"* is **NECESSARY BUT INSUFFICIENT**. To be operational, it must explicitly govern:
- Modal Scope Containment (no scope elevation).
- Temporal Expiration (no persistence escalation).
- Causal Origin Tracking (no self-echo escalation).
- Term Separation (no unverified entity merging).

---

## 10. K3 Boundary Analysis

### What Strong Kleene K3 Guarantees
Strong Kleene K3 truth tables govern logical evaluation over $\{0 (\text{FALSE}), 1 (\text{TRUE}), 2 (\text{UNKNOWN})\}$:
- Conjunction: $\text{FALSE} \land \text{UNKNOWN} = \text{FALSE}$; $\text{TRUE} \land \text{UNKNOWN} = \text{UNKNOWN}$.
- Disjunction: $\text{TRUE} \lor \text{UNKNOWN} = \text{TRUE}$; $\text{FALSE} \lor \text{UNKNOWN} = \text{UNKNOWN}$.
- Negation: $\neg \text{UNKNOWN} = \text{UNKNOWN}$.

K3 guarantees that:
1. Conjoining an unknown premise with a true premise never produces truth ($\text{TRUE} \land \text{UNKNOWN} \not\vdash \text{TRUE}$).
2. Missing evidence does not equal falsity (`FIX-23H-01`).
3. Internal deduction never fabricates truth out of incomplete premises.

### What Strong Kleene K3 Does NOT Guarantee
**K3 provides ZERO protection against bad premises.**
- K3 is an *internal evaluation calculus*, NOT an *ingress filter*.
- If an upstream ingress adapter asserts an unjustified proposition with `is_active = True, polarity = True`, P23-H assigns it $v = \text{TRUE}$.
- Once an unjustified premise is labeled $\text{TRUE}$, K3 deterministically propagates it to all downstream conclusions.

### What MUST Happen Before K3
Before any term is assigned truth in P23-H, the following checks must execute outside and prior to the K3 engine:
1. **Modal Scope Tagging**: Ensure proposition is bounded to its proper scope.
2. **Polar Contradiction Check**: Verify against existing active terms in `TermArena`.
3. **Temporal Freshness Validation**: Verify current timestamp falls within the proposition's validity window.
4. **Source Qualification**: Verify source authority matches the target predicate domain.

---

## 11. Contradiction Analysis

When two contradictory assertions arrive ($A$ and $\neg A$), what must occur?

### Existing Repository Contract
In P23-H (`src/core/cognition/kernel/conflict.py`), `check_polar_contradiction()` inspects `TermArena`:
- If an incoming proposition has identical `(predicate_id, arg0_id, arg1_id)` but opposite `polarity` against an existing active term:
  - It triggers a `ConflictRecord`.
  - It does **NOT** overwrite the existing premise.
  - It does **NOT** activate the new premise alongside the old one.

### Mathematical & Epistemic Evaluation
Evaluating possible contradiction behaviors:
1. **Both Admitted as Premises**:
   - In classical logic: Principle of Explosion ($A \land \neg A \vdash \bot \implies$ everything derivable).
   - In P23-H: Destroys goal-directed backward chaining; backward chainer would prove both goal and its negation depending on traversal order.
   - *Verdict*: **FORBIDDEN**.
2. **Becomes UNKNOWN**:
   - Sound in epistemic logic, but loses the critical information that a contradiction was detected.
   - *Verdict*: **INSUFFICIENT**.
3. **Source-Qualified Contradiction**:
   - Term $A$ is held under `scope:source_1`, Term $\neg A$ is held under `scope:source_2`.
   - Root scope remains uncommitted (`UNKNOWN`).
   - P23-H emits an epistemic conflict record, which CAPS compiles into a conversational `CommunicativeAct.CLARIFY` directed to the user.
   - *Verdict*: **CORRECT & ARCHITECTURALLY COMPLIANT**.

---

## 12. Source-Class Analysis

We evaluate eight distinct upstream source classes to determine their epistemic profile:

| Source Class | Nature of Representation | Epistemic Authority | Permitted Ingress Target | Modal Scope Requirement |
|---|---|---|---|---|
| **Raw Perception** | Continuous signals (audio FFT, video tensors). | High noise, low semantic structure. | **STRICTLY REJECTED** from P23-H. Must be processed by perceptual layers. | N/A |
| **Extracted Perception** | Categorical entities with continuous confidence. | Bounded physical presence; acoustic/visual hypothesis. | `EpistemicStatus.UNKNOWN` or low-level perceptual frame; never direct root `FACT`. | `SCOPE_TYPE_INTENSIONAL` (Perceptual hypothesis) |
| **KnowledgeStore (P16)** | Stored string triples `(S, P, O)`. | Historical record; lacks semantic deduplication and entity indexing. | **BLOCKED** until entity canonicalization and deduplication are resolved. | `SCOPE_TYPE_ROOT` (if verified) |
| **User Direct Statement** | Natural language utterance from user. | Absolute authority on *user state/preference*; fallible on *objective world facts*. | `EpistemicStatus.FACT` inside user-attitude scope; `UNKNOWN` or unverified in root world scope. | `SCOPE_TYPE_MODAL` (User asserts / User prefers) |
| **Assistant Generated** | Prior utterances/propositions from Lucia. | **ZERO external evidential authority**. | **STRICTLY FORBIDDEN** from asserting external facts. Usable only to verify conversational coherence. | `SCOPE_TYPE_MODAL` (Assistant hypothesized) |
| **Derived Inference** | Upstream rule/heuristic derivation. | Defeasible; conditionally sound. | `EpistemicStatus.INFERRED` under Model D only (full premise tree registered in JTMS). | Inherited from premises |
| **Persistent History** | Long-term memory records (SDM/Episodic). | Decaying temporal validity. | Admissible only with active temporal validity filter. | Root with historical timestamp |
| **External / Unknown** | Web lookup, third-party API. | Untrusted / unverified. | `EpistemicStatus.UNKNOWN` (candidate hypothesis); emits verification subgoal. | `SCOPE_TYPE_INTENSIONAL` |

### Irreducible Distinction
The irreducible distinction among source classes is **Domain-Specific Authority vs Evidential Independence**:
- A source may be 100% authoritative in one domain (User on own preferences) and 0% authoritative in another (User on laws of physics).
- An assistant output is 0% authoritative as evidence for the truth of what it proposed (anti-echo boundary).

---

## 13. Universal Contract Feasibility

### Outcome Evaluation
- **Outcome A (Universal Single Contract)**: A single flat contract universally handles all upstream sources.
  - *Feasibility*: **FALSIFIED & IMPOSSIBLE**. A single flat contract that treats user input, assistant output, perceptual hypotheses, and database records identically collapses under Cases 5, 6, and 10.
- **Outcome B (Core Contract with Source-Specific Qualifications)**: One structural schema exists, but it requires explicit source-class typing and modal scoping to parameterize admissibility.
  - *Feasibility*: **ARCHITECTURALLY VALIDATED**.
- **Outcome C (Separate Non-Unifiable Contracts)**: Source classes require completely different runtime subsystems.
  - *Feasibility*: Unnecessary fragmentation; violates Invariant 6 and ARCH-030.1.

### Feasibility Conclusion
**Outcome B is the correct architecture**:
A single core structural schema is possible **ONLY IF** it carries:
1. Typed Source Classification (`source_class`).
2. Structural Modal Scoping (`scope_type`, `scope_id`).
3. Explicit Validity Horizon (`valid_from`, `valid_until`).

---

## 14. Revised Minimal Contract

*This contract is proposed strictly as a research specification to replace the falsified candidate contract. No production code is modified.*

### Structural Definition

```python
@dataclass(frozen=True)
class EpistemicallyQualifiedProposition:
    """
    Revised Minimal Epistemic Ingress Contract for P23-H Reasoning Kernel.
    Language-independent, numerically interned, modal-scope-protected.
    """
    # 1. Semantic Core (Numeric IDs)
    predicate_id: int               # Interned numeric concept ID
    arg0_id: int                     # Subject / Primary entity ID
    arg1_id: int = 0                 # Object / Secondary entity ID (0 if unary)
    arg2_id: int = 0                 # Tertiary entity ID (0 if binary)
    polarity: bool = True            # True = Positive affirmation, False = Polar negation

    # 2. Epistemic Classification
    epistemic_status: EpistemicStatus # FACT, INFERRED, AMBIGUOUS, UNKNOWN

    # 3. Modal & Structural Scope
    scope_id: int = 1                # Numeric scope ID (1 = root)
    scope_type_id: int = 1           # 1=ROOT, 2=NEGATION, 3=MODAL, 4=INTENSIONAL

    # 4. Source & Provenance Ledger
    source_class: IngressSourceClass # USER_DISCOURSE, PERCEPTUAL_HYPOTHESIS, 
                                     # DERIVED_INFERENCE, MEMORY_TRACE, EXTERNAL
    session_id: int = 0              # Originating session ID
    turn_id: int = 0                 # Originating turn ID
    rule_id: int = 0                 # Derivation rule ID (if INFERRED)
    supporting_premise_ids: Tuple[int, ...] = () # Must be active in TermArena if INFERRED

    # 5. Temporal Horizon
    valid_from: float = 0.0          # Timestamp of assertion
    valid_until: float = float("inf")# Expiration timestamp (prevents persistence escalation)
```

### Justification of Fields

| Field | Why It Exists | Unsoundness Without It | Nature |
|---|---|---|---|
| `predicate_id`, `arg0..2`, `polarity` | Defines relational semantic truth. | No propositional content to evaluate. | Semantic Core |
| `epistemic_status` | Maps to Strong Kleene K3 values. | Epistemic flattening; UNKNOWN becomes certainty. | Epistemic |
| `scope_id`, `scope_type_id` | Enforces modal containment. | Modal collapse: beliefs become extensional facts. | Semantic / Modal |
| `source_class` | Enforces authority boundaries. | Echo loops (F15); assistant validates own output. | Epistemic Provenance |
| `rule_id`, `supporting_premise_ids`| Enables JTMS cascade retraction. | Zombie facts survive upstream retraction. | Truth Maintenance |
| `valid_from`, `valid_until` | Bounds proposition to its temporal lifespan. | Stale, ephemeral states become immortal facts. | Temporal Epistemic |

---

## 15. Responsibilities Outside P23-H

To preserve P23-H as a bounded, deterministic reasoning kernel ($O(1)$ rule lookup, $\le 10\,\mu\text{s}$ goal chaining, $0.0\text{ MB}$ GPU VRAM, AMD/Intel CPU edge execution), the following responsibilities **MUST REMAIN OUTSIDE P23-H**:

1. **Perceptual Uncertainty & Confidence Calibration**:
   P23-H does not calibrate sensory probabilities or execute Kalman filters. Perceptual evidence must be converted to discrete modal hypotheses before ingress.
2. **Natural Language Semantic Parsing**:
   P23-H operates strictly on 64-bit integer IDs. All lexical parsing, zero-anaphora resolution, and syntactic dependency tagging belong in `LanguageIngressGate` (P23-F).
3. **Truth Verification & Fact Checking**:
   P23-H is a deductive reasoning kernel, not an oracle. It checks internal logical consistency, not external metaphysical truth.
4. **Source Reliability Estimation**:
   P23-H does not maintain dynamic Bayesian trust models over conversational participants.
5. **Freshness & Decay Policy**:
   P23-H checks whether `now() <= valid_until`; it does not calculate exponential decay curves or schedule background memory eviction.
6. **Conversational Turn Management & CAPS Speech Act Selection**:
   P23-H emits subgoals (`InformationSubgoal`, `DisambiguationSubgoal`) and conflict records (`ConflictRecord`). Compiling these into communicative acts (`INQUIRE`, `CLARIFY`) is the strict domain of CAPS (P24).
7. **Entity Deduplication & Canonicalization**:
   P23-H assumes entity IDs provided by `SymbolTable` are coherent. Deduplicating raw text strings into stable entity IDs is an upstream substrate responsibility.

---

## 16. Remaining Unresolved Questions

Before the Revised Minimal Contract can proceed from research specification to contract freeze, five critical engineering prerequisites remain unresolved:

1. **Unstable Upstream Proposition Identity (F12)**:
   `KnowledgeStore` (P16) does not deduplicate identical relational triples and generates random UUIDs upon derivation. Ingressing from KnowledgeStore will flood `TermArena` with duplicate terms.
2. **Missing Conversational Provenance Ledger (F15)**:
   Lucia's dialogue orchestrator stores history as raw text tuples `(role, text)`. Assistant utterances are never interned as logical terms. Preventing the F15 Echo Loop requires a bidirectional conversational provenance ledger.
3. **Absence of Endogenous Goal Dispatch (F2)**:
   Lucia has zero background reasoning loops. P23-H is invoked strictly on reactive user turns. Ingress cannot execute autonomously while the system is idle.
4. **Addressee Dependency in Subgoals**:
   `InformationSubgoal` does not currently specify whether missing information requires user inquiry, internal memory lookup, or environmental observation.
5. **Concurrency Under Coupled MT-LNN Load**:
   `TermArena` allocation and projection latency under active 200ms ODE integration has not been benchmarked under heavy CPU contention (`GATE 23-I-EVAL` Track B).

---

## 17. Final GO / CONDITIONAL GO / NO-GO

### Selected Verdict: **CONDITIONAL GO**

### Definition
> **CONDITIONAL GO**: A principled epistemic boundary exists and its minimal contract has been rigorously formulated, but critical upstream epistemic distinctions (modal scope isolation, source authority typing, and conversational provenance) remain unresolved at the architectural implementation level and must be specified and resolved before any production implementation is authorized.

### Decision Rationale
1. **Falsification Complete**: The naive candidate contract (`EpistemicallyQualifiedProposition` with scalar confidence and `validity`) is conclusively falsified and rejected.
2. **Boundary Soundness Established**: A sound boundary is mathematically and epistemically feasible under the *Revised Minimal Contract* (Section 14).
3. **Implementation Blocked**: Production implementation of adapters or runtime wiring is **STRICTLY PROHIBITED** until the five unresolved prerequisites (Section 16) are ratified through formal ADRs.

---

## 18. Recommended Next Step

The next research and governance actions should proceed in strict sequence:

1. **Formalize ADR for Revised Ingress Contract**:
   Draft an Architectural Decision Record defining the *Revised Minimal Epistemic Ingress Contract* (Section 14) and ratifying `NEG-02` permanent enforcement.
2. **Resolve Upstream Proposition Identity (F12 Audit)**:
   Execute a targeted investigation into `KnowledgeStore` deduplication to establish deterministic, content-addressable proposition IDs (`hash(S, P, O)`) prior to ingress coupling.
3. **Specify Conversational Provenance Protocol (F15)**:
   Design a lightweight turn-anchored provenance ledger that tags incoming user assertions with causal parentage to eliminate self-echo feedback loops.
4. **Preserve P23-H Kernel Freeze**:
   Maintain `src/core/cognition/kernel/` strictly frozen at commit `3eef803`. Under no circumstances modify kernel internals to accommodate unfortified upstream ingress.
