# P23-D R2 Decision Addendum: Resolution of Open Contract Items

**Document Identifier**: `DOC-P23D-R2-ADDENDUM-001`  
**Milestone Scope**: Phase 23-D Architecture Contract / Revision 2 (Resolution Addendum)  
**Parent Contract**: [`docs/others/p23d_endogenous_cognition/P23D_ARCHITECTURE_CONTRACT_R2.md`](file:///c:/Users/Lunafiah/Desktop/My_project/Lucia/docs/others/p23d_endogenous_cognition/P23D_ARCHITECTURE_CONTRACT_R2.md) (`DOC-P23D-ARCH-CONTRACT-R2-001`)  
**Topic**: Formal Closure of Durable Persistence Authority & Substrate SPO Deduplication  
**Operating Mode**: Specification Only. Zero production code changes (`src/`), zero test changes (`tests/`), zero Genesis alterations (`data/profile.json`).  
**Authority**: Architecture Decision Addendum  
**Date**: 2026-10-21  

---

## 1. Executive Summary

This decision addendum formally investigates, evaluates, and closes the two open contract items identified in the **P23-D Architecture Contract / R2**:
1. **Durable Persistence Authority**: Determining the canonical, crash-safe, fail-closed storage authority for `UnresolvedCondition`.
2. **Substrate SPO Deduplication & Canonical Referent Key**: Auditing `KnowledgeStore`, proposition producers/consumers, and specifying the minimal deduplication and adapter contract for `UnresolvedCondition.referent_key`.

Through comprehensive, empirical codebase auditing, both items are conclusively resolved. With these resolutions established without expanding scope or violating repository invariants, the P23-D Architecture Contract advances from `READY WITH OPEN CONTRACT ITEMS` to:

$$\mathbf{READY\ FOR\ IMPLEMENTATION\ SPEC}$$

---

## 2. Item 1: Durable Persistence Authority Audit & Decision

### 2.1 Repository Store Audit [REPOSITORY FACT]

An exhaustive inspection of all existing persistent storage implementations in `src/` and persistent data files in `data/` was conducted:

| Existing Store / File | Code Owner | Schema & Domain Scope | Lifecycle & Write Triggers | Evaluation for `UnresolvedCondition` | Verdict |
|---|---|---|---|---|---|
| `data/profile.json` | `src/core/profile/` | Host identity, onboarding status, Genesis record. | Written once at Genesis onboarding ceremony. Read-only thereafter. | Forbidden. Invariant `INV-8` strictly locks `data/profile.json` (`{"is_onboarded": false}`). Modifying it during development/simulation violates Genesis. | **`[REJECTED]`** |
| `data/genesis_commitment.json` | `src/core/lifecycle/` | Cryptographic SHA-256 birth commitment hash and signature. | Immutable post-Genesis birth artifact. | Non-modifiable cryptographic anchor. Not a cognitive store. | **`[REJECTED]`** |
| `data/epoch_manifest.json` | `src/core/emotion/persistence.py` | Multi-store logical epoch synchronization barrier (`stores={"relationship": N, "dynamical_state": N}`). | Written at Stage S16.5 commit barrier. Atomic replace via temporary file. | Incompatible domain. Contains zero schema or data structures for cognitive conditions. Overloading it breaks its single responsibility as a rollback barrier. | **`[REJECTED]`** |
| `data/dynamical_state.json` | `src/core/emotion/persistence.py` | Continuous hidden state vectors ($h_{\text{fast}} \in \mathbb{R}^{32}$, $s_{\text{slow}} \in \mathbb{R}^{16}$) and ODE parameters. | Saved at turn commit barrier or shutdown. Has `.json.bak`. | Incompatible domain. Continuous tensor states cannot store discrete symbolic condition state machines. | **`[REJECTED]`** |
| `data/relationship.json` | `src/core/relationship/persistence.py` | Dyadic relationship scalars (`trust`, `familiarity`, `closeness`, `reciprocity`) and update log. | Updated at Stage S16.3. Atomic replace via temporary file with `.json.bak`. | Incompatible domain. Cognitive conditions (missing premises, contradictions) are orthogonal to relational attachment metrics. | **`[REJECTED]`** |
| `data/chat_history.json` | `src/core/orchestrator/` | Surface conversational transcript entries (`user`, `assistant`). | Appended at Stage S16.4. | Incompatible domain. Internal cognitive conditions must never be serialized into visible chat feeds (`INV-2` No Reflective Ego). | **`[REJECTED]`** |
| `data/knowledge.json` | `src/core/knowledge/persistence.py` | Epistemic proposition triples $(S, P, O)$, concepts, and symbolic inference rules. | `save_knowledge()` exists in `persistence.py` but is **never invoked** in `CognitiveOrchestrator`. | Incompatible lifecycle. `KnowledgeStore` is an epistemic belief repository (facts + non-monotonic retraction). Dynamic condition lifecycles (`ACTIVE` $\to$ `DEFERRED` $\to$ `SUPPRESSED` $\to$ `RESOLVED`) belong in working memory orchestration, not long-term semantic knowledge. | **`[REJECTED]`** |

### 2.2 Authoritative Persistence Decision [ARCHITECTURE CONTRACT]

Because every existing repository store is architecturally orthogonal, specialized, and domain-incompatible, storing `UnresolvedCondition` records inside any existing store represents an architectural anti-pattern and a separation-of-concerns violation.

Therefore, the persistence authority is formally ratified as a dedicated, lightweight, crash-safe store:

$$\text{Canonical File Target}: \mathbf{data/cognitive\_conditions.json}$$
$$\text{Backup Recovery File}: \mathbf{data/cognitive\_conditions.json.bak}$$

### 2.3 Detailed Persistence & Recovery Specification [ARCHITECTURE CONTRACT]

1. **Subsystem Ownership**:
   - `CognitiveOrchestrator` owns `_condition_ledger: Dict[str, UnresolvedCondition]`.
   - Persistence logic is encapsulated in `src/core/cognition/condition_persistence.py`.
2. **Lifecycle & Read-Write Semantics**:
   - **Boot / Recovery**: Loaded once during `CognitiveOrchestrator.__init__`. If file does not exist, initialize empty ledger (`{}`).
   - **In-Memory Operation**: All condition mutations during turns and endogenous cycles operate purely in-memory in `_condition_ledger`.
   - **Persistence Barrier**: Committed to disk atomically at Stage S16.5 commit barrier alongside `EpochManifest`, or upon completion of an endogenous cycle if condition states have mutated.
3. **Atomic Crash-Safe Write Protocol**:
   - Step 1: Serialize `_condition_ledger` to JSON formatting (`{"version": "1.0", "conditions": [...]}`).
   - Step 2: Write payload to a unique temporary file in `data/` using `tempfile.mkstemp(prefix="conditions_", suffix=".tmp")`.
   - Step 3: If `data/cognitive_conditions.json` exists, copy it to `data/cognitive_conditions.json.bak` via `shutil.copy2`.
   - Step 4: Perform atomic filesystem replace via `os.replace(temp_path, target)`.
   - This exact protocol mirrors the verified pattern in `src/core/relationship/persistence.py:48-65`.
4. **Startup Recovery & Corruption Handling (Fail-Closed)**:
   - Primary Attempt: Load and parse `data/cognitive_conditions.json`. Verify schema structure and condition hashes.
   - Fallback Attempt: If primary file is corrupted, half-written, or schema-invalid, attempt to load `data/cognitive_conditions.json.bak`.
   - Safe Fallback: If both files fail or are missing, quarantine corrupted file to `.corrupt` diagnostic log, log error, and initialize empty ledger (`{}`).
   - Boot sequence **NEVER crashes**. Corrupted records are **NEVER promoted** into active memory.
5. **Genesis Invariant Compatibility (`INV-8`)**:
   - In the clean pre-activation developmental baseline, `data/cognitive_conditions.json` does not exist (or contains `{"version": "1.0", "conditions": []}`).
   - It has zero dependency on `data/profile.json` and does not mutate onboarding state (`{"is_onboarded": false}`).

---

## 3. Item 2: Substrate SPO Deduplication Audit & Decision

### 3.1 Substrate & Consumer Audit [REPOSITORY FACT]

A comprehensive audit of proposition representation, equality, and indexing across `KnowledgeStore`, `ReasoningKernel`, `TermArena`, and `CAPS` revealed:

1. **Current Proposition Representation in `KnowledgeStore`**:
   - Defined in `src/core/knowledge/proposition.py:31-61`.
   - Fields: `id: str`, `subject: str`, `predicate: str`, `object: str`, `confidence: float`, `provenance: ProvenanceType`, `evidence_ids: List[str]`, `created_at: float`, `valid: bool`, `superseded_by: Optional[str]`.
   - Identity: Stored in `KnowledgeStore._propositions: Dict[str, Proposition]`, keyed **strictly by caller-assigned `prop.id`**.
   - Scope: `Proposition` possesses **zero scope semantics**. It implicitly assumes a global or root scope.
2. **Current Deduplication & Equality Semantics**:
   - `Proposition` has no custom `__eq__` or `__hash__`; it uses dataclass field-by-field equality.
   - `KnowledgeStore.store_proposition(prop)` merely inserts `self._propositions[prop.id] = prop`. It performs **zero deduplication** over $(S, P, O)$.
   - Transitive derivation in `src/core/knowledge/derivation.py:57` generates random UUIDs:
     ```python
     new_prop = Proposition(
         id=f"derived:{uuid.uuid4().hex[:8]}",
         subject=p1.subject,
         predicate=transitive_predicate,
         object=p2.object, ...
     )
     ```
   - Running derivation repeatedly produces redundant duplicate entries with identical $(S, P, O)$ triples but different UUIDs.
3. **Representation in Bounded Reasoning Kernel (Phase 23-H)**:
   - Operates in pure numeric space (`LogicalTerm`, `TermArena`, `engine.py`).
   - Terms are indexed by numeric `(predicate_id, arg0_id, arg1_id, scope_id, polarity, epistemic_status)`.
   - `InformationSubgoal` emits numeric IDs: `target_predicate_id: int`, `arg0_id: int`, `arg1_id: int`, `scope_id: int`.
4. **Existing Canonical Key `(S, P, O, scope)`**:
   - `[REPOSITORY FACT]`: **NO canonical `(S, P, O, scope)` key exists in `KnowledgeStore`.** Only `Proposition.to_tuple() -> (subject, predicate, object)` exists, which is unindexed.
5. **Can `UnresolvedCondition.referent_key` Reuse Existing Identity Directly?**:
   - **NO.** An `UnresolvedCondition` for a `MISSING_PREMISE` cannot reuse `Proposition.id` because the proposition does not exist in `KnowledgeStore` yet.
   - Furthermore, `ReasoningKernel` emits integer IDs, whereas `KnowledgeStore` stores strings. Direct reuse without an adapter is impossible.

### 3.2 Canonical Referent Key & Adapter Contract [ARCHITECTURE CONTRACT]

To guarantee deterministic condition identity without modifying `KnowledgeStore` prior to implementation authorization:

1. **Canonical Symbolic Referent Key Formulation**:
   Every relational proposition and epistemic condition is uniquely identified by the canonical tuple string:
   $$\text{canonical\_referent\_key} = \text{f"\{scope\}:\{subject\}:\{predicate\}:\{object\}"}$$
   - When scope is unspecified (as in `KnowledgeStore`), it defaults to `"scope:root"`.
   - All string tokens are normalized: lowercase, stripped of whitespace.
2. **Bidirectional Adapter via Existing `SymbolTable`**:
   The existing `SymbolTable` (`src/core/cognition/contract/projection.py:45-120`) is the ratified, verified bidirectional translator between string symbols and numeric term IDs:
   - Translating an `InformationSubgoal` (numeric) into an `UnresolvedCondition.referent_key`:
     ```python
     pred_str = symbol_table.id_to_concept(subgoal.target_predicate_id)
     a0_str = symbol_table.id_to_concept(subgoal.arg0_id)
     a1_str = symbol_table.id_to_concept(subgoal.arg1_id) if subgoal.arg1_id else ""
     scope_str = f"scope:{subgoal.scope_id}"
     referent_key = f"{scope_str}:{a0_str}:{pred_str}:{a1_str}"
     ```
   - Translating an `UnresolvedCondition.referent_key` into a `KnowledgeStore` query:
     ```python
     _, a0_str, pred_str, a1_str = referent_key.split(":")
     matching_props = knowledge_store.query(subject=a0_str, predicate=pred_str, object_=a1_str, valid_only=True)
     ```
3. **Deterministic Condition ID**:
   $$\text{condition\_id} = \text{SHA256}(\text{f"\{condition\_type\}:\{referent\_key\}"})$$
   Guarantees that identical missing subgoals always map to the exact same `condition_id`, preventing duplicate condition instantiation across turns.

### 3.3 Minimal Missing Contract for `KnowledgeStore` (Implementation Prerequisite) [PROPOSED CONTRACT]

During the subsequent implementation phase, `KnowledgeStore` requires only one minimal non-invasive enhancement:
- Add a internal index: `_spo_index: Dict[Tuple[str, str, str], str]` mapping `(subject.lower(), predicate.lower(), object.lower())` to `prop.id`.
- In `store_proposition(prop)`: If a valid proposition with the identical triple exists, return the existing `prop.id` instead of inserting a duplicate; if derivation runs, derive deterministically without random UUIDs.

---

## 4. Summary of Decisions on Open Contract Items

| Open Contract Item | Audit Finding | Ratified Decision | Contract Status |
|---|---|---|:---:|
| **1. Durable Persistence Authority** | All existing stores (`profile.json`, `epoch_manifest.json`, `dynamical_state.json`, `relationship.json`, `knowledge.json`, `chat_history.json`) are domain-incompatible or violate invariants. | Ratify **`data/cognitive_conditions.json`** with atomic rename (`.tmp` $\to$ `.json`), backup file (`.json.bak`), and fail-closed boot recovery under `CognitiveOrchestrator` ownership. | **`FROZEN / CLOSED`** |
| **2. Substrate SPO Deduplication** | `KnowledgeStore` lacks deduplication, generates random UUIDs, and has no scope. `Proposition.id` cannot be reused directly for missing subgoals. | Ratify canonical key format `"{scope}:{subject}:{predicate}:{object}"` mapped via verified `SymbolTable` adapter. `condition_id` computed via deterministic SHA-256 hash. | **`FROZEN / CLOSED`** |

---

## 5. Remaining Blockers

There are **zero remaining architectural blockers** within the scope of P23-D R2.

- Scope boundaries: strictly preserved.
- 4 mandatory boundaries: frozen.
- Concurrency & safety invariants: frozen.
- 2 open contract items: closed with empirical repository evidence.
- Zero production code modified; Genesis onboarding gate bit-exact.

---

## 6. Final Gate Verdict

```text
================================================================================
                    FINAL P23-D R2 CONTRACT GATE VERDICT:
                       READY FOR IMPLEMENTATION SPEC
================================================================================
```

Both open contract items have been fully resolved with verified repository evidence. P23-D R2 is now complete, frozen, and officially qualified to advance to the **Implementation Specification** phase. Zero implementation code has been authored in this turn.
