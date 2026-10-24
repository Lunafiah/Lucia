# ADR-039: Epistemic Admission Contract — Bounded Schema & Ingress Wiring Extension

> **Document ID:** DOC-ADR-039 (ARCH-039 / ADR-039)  
> **Status:** `[ACCEPTED / PRODUCTION IMPLEMENTED / VERIFIED]`  
> **Authority:** Architectural Decision Record (Outcome B)  
> **Canonical Target:** `docs/others/epistemic_admission_contract/ADR_039_EPISTEMIC_ADMISSION_CONTRACT.md`  
> **Verifying Suite:** `tests/unit/test_epistemic_admission_contract.py` (11/11 PASS; 163/163 regression PASS)  
> **Phase Context:** Post-P27 Baseline / Pre-Genesis Developmental Gate  

---

## 1. Context & Architectural Problem

Prior to ADR-039, an epistemic admission boundary gap existed between the external sensory perimeter and internal symbolic knowledge:
1. **Modal Scope Flattening**: `EpistemicReasoningService.project_propositions()` hardcoded all incoming propositions into root scope (`scope_id=1`), collapsing modal/unverified assertions into universal reasoning premises.
2. **Schema Incompleteness**: `Proposition` lacked persistent tracking for `scope_id`, `causal_relation`, `antecedent_id`, `rule_id`, and `supporting_premise_ids`, losing causal and justification context upon serialization.
3. **Detached Ingress Wiring**: `LanguageIngressGate` (ADR-038) and dyadic anti-echo checks existed in isolation and were not wired into the live conversational turn pipeline (`_execute_pipeline()`).
4. **Knowledge Revision Disconnect**: Non-destructive revisions in `KnowledgeStore.revise()` did not propagate to the Justification-Based Truth Maintenance System (`JTMS`), leaving derived consequences active even when their foundational premises had been contradicted.

An audit rejected speculative architectural expansions (Outcome A contract-only and Outcome C new acquisition subsystems / Phase 28). The project governance locked:

> **Outcome B — Bounded Schema/Wiring Extension**

ADR-039 implements this locked decision without adding cognitive subsystems, without new epistemic states, without reopening P23-D/P23-I, and without modifying the First Activation Gate.

---

## 2. Decision & Architectural Specifications

### 2.1 Scope-Relative Epistemic Truth
- `scope:root` denotes the **primary reasoning namespace** of the companion, **not universally verified objective truth**.
- Epistemic status is scope-relative. A proposition asserted by the user or inferred internally is qualified strictly with respect to its scope.
- Non-root propositions reside in modal containers (e.g. `scope:modal:user_claim`, `scope:modal:unclassified`).
- **Modal Isolation Invariant**: Projections from `scope:modal:*` allocate terms with distinct numeric scope IDs ($\ge 2$). In `ReasoningKernel`, goals evaluated in root scope (`scope_id=1`) strictly evaluate to `KleeneValue.UNKNOWN` against modal terms and cannot unify with or leak into root reasoning.

### 2.2 Authority × Domain Deterministic Admission Policy
Admission is governed by a pure deterministic policy distinguishing source authority and subject domain:

| Source Authority | Domain Classification | Admission Disposition | Target Scope |
|---|---|---|---|
| User (`USER_DISCOURSE`) | Current affect / somatic self-report | `ROOT_ADMIT` | `scope:root` |
| User (`USER_DISCOURSE`) | User preference | `ROOT_ADMIT` | `scope:root` |
| User (`USER_DISCOURSE`) | User biography | `ROOT_ADMIT` | `scope:root` |
| User (`USER_DISCOURSE`) | Unsupported external-world claim | `MODAL_ADMIT` | `scope:modal:user_claim` |
| User (`USER_DISCOURSE`) | Third-party attribution | `MODAL_ADMIT` | `scope:modal:user_claim` |
| Assistant / LLM | Any generated claim | `REJECT` | N/A |
| Deduction engine (`DERIVED`) | Sound derivation | `ROOT_ADMIT` | `scope:root` |
| Any | Unknown predicate/domain | `STAGE` | `scope:modal:unclassified` |
| Any | Contradiction with active root | `STAGE` | `scope:modal:unclassified` |

- **`USER_STATED ≠ BELIEVES`**: User-originated root admissions retain `ProvenanceType.USER_STATED` and preserve the asserted predicate (e.g. `c:prefers`). The system strictly forbids synthesizing or converting `USER_STATED(p) → BELIEVES(user, p)` unless explicitly expressed in input text.
- **LLM/Assistant Output Has Zero Epistemic Authority**: LLM text output is never treated as factual testimony.
- **Anti-Echo Rejection (F15)**: Passive user assent (`"Yes"`, `"Đúng rồi"`) to assistant-seeded closed hypotheses attributes `CausalRelation.CONFIRMED_ECHO`, resulting in `status=UNKNOWN`, `disposition=REJECT`, zero `KnowledgeStore` mutation, and zero candidate staging.

### 2.3 Ephemeral Candidate Staging
- Pre-admission ingress assertions that cannot be immediately admitted fail closed to in-memory staging (`KnowledgeStore.stage_candidate()`).
- Staged candidates are ephemeral: they are never persisted to disk (`to_json()` excludes staging) and are cleared on lifecycle/session reset (`reset_lifecycle()`).
- No arbitrary TTL (e.g. 5 turns) is hardcoded into the architecture. Retention and pruning remain implementation details.

### 2.4 KnowledgeStore → JTMS Revision Bridge
- `KnowledgeStore.revise()` invalidates the previous proposition (`valid=False`, `provenance=CONTRADICTED`), records historical lineage, and notifies registered observer callbacks.
- Hexagonal boundary discipline is strictly preserved: `KnowledgeStore` does not import or depend on `CognitiveOrchestrator`.
- `CognitiveOrchestrator._handle_knowledge_store_revision()` resolves the revised proposition symbol to its numeric `term_id` via `SymbolTable` and dispatches a typed `RetractionDirective` to `JTMS.retract_premise()`.
- JTMS cascades recursive invalidation to dependent inferences while preserving inferences with independent alternative justifications.
- **Bootstrap Immutability**: Revising immutable architecture bootstrap knowledge raises `PermissionError`.

### 2.5 Invariant NEG-02 Preservation
- Continuous confidence represents measurement reliability or sensor SNR, not ontological proof.
- Continuous confidence $< 1.0$ (e.g. `0.999`) never independently promotes to discrete `EpistemicStatus.FACT`.

### 2.6 Live Turn Ingress Orchestration (Hooks S1b & S1c)
The canonical 16-stage cognitive turn sequence is preserved without renumbering:

```text
Stage S1 — Sensory Encoding
    ↓
[Hook S1b] — Propositional Ingress / Anti-Echo & Dyadic Seed Analysis
    ↓
[Hook S1c] — Epistemic Admission (Authority × Domain Evaluation & Staging)
    ↓
Stage S2 — Generative Prior Expectation
    ↓
Stage S3..S7 — Affective & Somatic Integration
    ↓
Stage S8 — Structured Knowledge Retrieval (Grounding from Admitted KnowledgeStore)
    ↓
Stage S9..S16 — Inference, Realization, and Expression
```

Hooks S1b and S1c operate strictly as internal orchestration sub-routines, **not as new canonical cognitive stages**.

---

## 3. Schema & Persistence Changes

`Proposition` dataclass in `src/core/knowledge/proposition.py` is extended with 5 backwards-compatible fields:

```python
scope_id: str = "scope:root"
causal_relation: Optional[str] = None
antecedent_id: Optional[str] = None
rule_id: Optional[str] = None
supporting_premise_ids: List[str] = field(default_factory=list)
```

`KnowledgeStore` indexes propositions using the 4-tuple key:

```python
key = (prop.scope_id.strip().lower(), prop.subject.strip().lower(), prop.predicate.strip().lower(), prop.object.strip().lower())
```

This prevents deduplication collisions between propositions sharing identical (S, P, O) across root and modal scopes.

---

## 4. Verification Evidence

All 11 formal contract invariants are verified in `tests/unit/test_epistemic_admission_contract.py`:

| Test | Description | Result |
|---|---|---|
| `test_01` | Modal $\rightarrow$ Root Leakage Isolation across reload and projection | **PASS** |
| `test_02` | `USER_STATED ≠ BELIEVES` preservation | **PASS** |
| `test_03` | Assistant Confirmed Echo Rejection (zero store mutation) | **PASS** |
| `test_04` | Unsupported World Claim admitted to `scope:modal:user_claim` | **PASS** |
| `test_05` | User Self-Report admitted to `scope:root` with `USER_STATED` | **PASS** |
| `test_06` | Unknown Predicate fail-closed ephemeral staging | **PASS** |
| `test_07` | Contradiction non-destructive staging without root overwrite | **PASS** |
| `test_08` | KnowledgeStore $\rightarrow$ JTMS non-monotonic cascade invalidation | **PASS** |
| `test_09` | Multi-justification consequence survival under premise retraction | **PASS** |
| `test_10` | Bootstrap Technical Architecture Immutability (`PermissionError`) | **PASS** |
| `test_11` | Invariant NEG-02: continuous confidence $< 1.0$ cannot yield `FACT` | **PASS** |

**Regression Test Suite Status**: **163 / 163 PASS** (0 failures).  
**First Activation Gate**: Unmodified and bit-exact (`data/profile.json == {"is_onboarded": false}`).
