# P23-D Implementation Specification v1: Endogenous Cognition & Cognitive Continuity

**Document Identifier**: `DOC-P23D-IMP-SPEC-V1-001`  
**Milestone Scope**: Phase 23-D Implementation Specification (Revision 1.0)  
**Parent Authorities**:
- [`docs/others/p23d_endogenous_cognition/P23D_ARCHITECTURE_CONTRACT_R2.md`](file:///c:/Users/Lunafiah/Desktop/My_project/Lucia/docs/others/p23d_endogenous_cognition/P23D_ARCHITECTURE_CONTRACT_R2.md) (`DOC-P23D-ARCH-CONTRACT-R2-001`)
- [`docs/others/p23d_endogenous_cognition/P23D_R2_DECISION_ADDENDUM.md`](file:///c:/Users/Lunafiah/Desktop/My_project/Lucia/docs/others/p23d_endogenous_cognition/P23D_R2_DECISION_ADDENDUM.md) (`DOC-P23D-R2-ADDENDUM-001`)  
**Operating Mode**: Specification Only. Zero production code modifications (`src/`), zero test alterations (`tests/`), zero Genesis alterations (`data/profile.json`).  
**Authority**: Technical Implementation Specification  
**Date**: 2026-10-21  

---

## 1. Implementation Surface Audit

Every module, component, and data structure participating in the implementation surface is audited and classified below:

| Component / Subsystem | Repository Location | Architectural Classification | Role & Implementation Responsibility |
|---|---|---|---|
| `CognitiveOrchestrator` | `src/core/orchestrator/cognitive_orchestrator.py` | `[EXISTING / EXTENDED ENTRY]` | Owns `_condition_ledger`, manages `_turn_lock`, coordinates Stage 16.5 condition persistence, hosts `process_endogenous()` entry point. |
| Cognitive Pipeline Stages | `src/core/orchestrator/cognitive_orchestrator.py:650-1490` | `[EXISTING / SELECTIVELY BYPASSED]` | Stages S0, S2, S5, S8, S10b, S16.5 executed for endogenous cycle; Stages S1 (external string parsing) and S11–S15 (surface language realization) bypassed by default. |
| `_turn_lock` | `src/core/orchestrator/cognitive_orchestrator.py:330, 531` | `[EXISTING]` | Non-reentrant threading lock (`threading.Lock()`). Enforces turn serialization; endogenous cycle acquires with `blocking=False` or priority yielding to user turns. |
| `KnowledgeStore` | `src/core/knowledge/store.py` | `[EXISTING / MINIMAL EXTENSION]` | Epistemic proposition repository. Extended with internal `_spo_index` to guarantee idempotent $(S, P, O)$ deduplication. |
| `Proposition` | `src/core/knowledge/proposition.py:31-62` | `[NO CHANGE]` | Canonical triple dataclass. Fields and methods preserved 100% as-is. |
| `SymbolTable` | `src/core/cognition/contract/projection.py:45-120` | `[EXISTING / REUSED AS ADAPTER]` | Bidirectional string $\leftrightarrow$ integer ID mapper. Reused to translate numeric `InformationSubgoal` terms into string tokens for canonical referent keying. |
| `InformationSubgoal` | `src/core/cognition/kernel/engine.py:75-102` | `[NO CHANGE / FROZEN]` | P23-H numeric subgoal dataclass (`target_predicate_id`, `arg0_id`, `arg1_id`, `scope_id`, `reason_code`). Preserved 100% frozen. |
| `CAPS` | `src/core/communication/caps.py` | `[NO CHANGE / REUSED]` | Evaluates communicative authorization, dyadic stance, and Priority 5 fail-closed grounding. Reused without mutation. |
| `LanguageIngressGate` | `src/core/language/adapter/gate.py` | `[NO CHANGE / REUSED]` | Enforces ADR-038 epistemic admission and F15 echo-escalation firewall. Reused without mutation. |
| P23-H / JTMS / K3 | `src/core/cognition/kernel/` | `[NO CHANGE / FROZEN]` | Strong Kleene 3-valued engine (`engine.py`) and non-monotonic truth maintenance (`jtms.py`). 100% frozen baseline. |
| Condition Persistence | `src/core/cognition/condition_persistence.py` | `[NEW MINIMAL PRIMITIVE]` | Atomic JSON serialization and crash-safe recovery for `data/cognitive_conditions.json` and `.json.bak`. |
| `UnresolvedCondition` | `src/core/cognition/contract/condition.py` | `[NEW MINIMAL PRIMITIVE]` | Minimal frozen dataclass holding condition identity, type, referent key, and lifecycle status. |
| Referent Key Adapter | `src/core/cognition/referent_adapter.py` | `[NEW MINIMAL PRIMITIVE]` | Pure deterministic encoder computing canonical referent strings and SHA-256 condition IDs from subgoals. |
| Trigger Qualification Boundary | `src/core/cognition/qualification.py` | `[NEW MINIMAL PRIMITIVE]` | Stateless qualification filter implementing Level 1–4 taxonomy and anti-cascading depth $= 1$. |

---

## 2. `UnresolvedCondition` Implementation Specification

### 2.1 Module & Package Location [ARCHITECTURE CONTRACT]

```text
src/core/cognition/contract/condition.py
```

### 2.2 Immutability & Copy-on-Write Semantics [ARCHITECTURE CONTRACT]

To guarantee deterministic concurrency and thread safety, `UnresolvedCondition` instances are implemented as **immutable dataclasses** (`frozen=True`).  
State transitions return a fresh instance via a copy-on-write transition method (`transition_to(...)`), ensuring that no shared condition instance is mutated concurrently across thread boundaries:

```python
@dataclass(frozen=True)
class UnresolvedCondition:
    condition_id: str             # Deterministic SHA-256 hex digest
    condition_type: ConditionType # MISSING_PREMISE | CONTRADICTION | RELATIONAL_RUPTURE
    referent_key: str             # Canonical encoded referent string
    status: ConditionStatus       # ACTIVE | DEFERRED | SUPPRESSED | RESOLVED
    resolution_source: SourceType # INTERNAL_SEARCH | EXTERNAL_USER | SYSTEM_ENVIRONMENT
    epoch_created: int            # Logical epoch ID of creation
```

### 2.3 Strict Field Prohibition [ARCHITECTURE CONTRACT]

The schema is frozen strictly to the 6 fields above.  
The following speculative fields are **STRICTLY PROHIBITED** from `UnresolvedCondition` and its persistent schema:
- `tension_weight`: Rejected.
- `retry_count`: Rejected as persistent schema (belongs in ephemeral execution tracer if measured).
- `priority`: Rejected (arbitrary float weights forbidden; lexicographic order governs).
- `confidence`: Rejected under ADR-038 `NEG-02` (scalar confidence corrupts K3 truth values).
- `backoff_seconds` / `cooldown_ms`: Rejected as persistent schema (evaluation parameters).

### 2.4 Condition Types & Enums [ARCHITECTURE CONTRACT]

```python
class ConditionType(str, Enum):
    MISSING_PREMISE = "MISSING_PREMISE"
    CONTRADICTION = "CONTRADICTION"
    RELATIONAL_RUPTURE = "RELATIONAL_RUPTURE"

class ConditionStatus(str, Enum):
    ACTIVE = "ACTIVE"
    DEFERRED = "DEFERRED"
    SUPPRESSED = "SUPPRESSED"
    RESOLVED = "RESOLVED"

class ResolutionSource(str, Enum):
    INTERNAL_SEARCH = "INTERNAL_SEARCH"
    EXTERNAL_USER = "EXTERNAL_USER"
    SYSTEM_ENVIRONMENT = "SYSTEM_ENVIRONMENT"
```

### 2.5 Serialization & Deserialization Validation [ARCHITECTURE CONTRACT]

- `to_dict() -> Dict[str, Any]`:
  Exports primitive JSON-safe types. Enum values converted via `.value`.
- `from_dict(d: Dict[str, Any]) -> UnresolvedCondition`:
  Validates that:
  1. All 6 fields are present and non-null.
  2. `condition_id` matches regex `^[a-f0-9]{64}$` (SHA-256 hex digest).
  3. Enum values belong to defined enumerations.
  4. `epoch_created >= 0`.
  Malformed or partial records raise `ValueError` and are quarantined.

---

## 3. Durable Persistence Implementation Specification

### 3.1 File Locations & Ownership [ARCHITECTURE CONTRACT]

- **Primary Target File**: `data/cognitive_conditions.json`
- **Backup File**: `data/cognitive_conditions.json.bak`
- **Ownership**: `CognitiveOrchestrator` owns `_condition_ledger: Dict[str, UnresolvedCondition]`.
- **Implementation Module**: `src/core/cognition/condition_persistence.py`.

### 3.2 Load & Save Timing [ARCHITECTURE CONTRACT]

1. **Load Timing**:
   Executed synchronously once during `CognitiveOrchestrator.__init__` before background daemons are started.
2. **Save Timing**:
   - Committed atomically during Stage S16.5 commit barrier alongside `EpochManifest`.
   - Committed immediately at the conclusion of an endogenous cycle if and only if one or more condition statuses have changed.
   - If zero condition mutations occurred, disk I/O is skipped.

### 3.3 Atomic Write & Backup Protocol [ARCHITECTURE CONTRACT]

Following the verified, crash-safe pattern in `src/core/relationship/persistence.py:48-65`:

```python
def save_conditions(
    conditions: Sequence[UnresolvedCondition],
    filepath: Optional[Path] = None,
) -> Path:
    target = filepath or DEFAULT_CONDITIONS_PATH
    target.parent.mkdir(parents=True, exist_ok=True)
    backup_path = target.with_suffix(".json.bak")

    payload = {
        "version": "1.0",
        "conditions": [c.to_dict() for c in conditions],
    }

    # 1. Write to temporary file in same directory
    temp_fd, temp_path = tempfile.mkstemp(
        dir=str(target.parent),
        prefix="conditions_",
        suffix=".tmp",
    )
    try:
        with os.fdopen(temp_fd, "w", encoding="utf-8") as f:
            json.dump(payload, f, indent=2, ensure_ascii=False)
        
        # 2. Backup existing valid file before replacing
        if target.exists():
            try:
                shutil.copy2(target, backup_path)
            except Exception as e:
                logger.warning("Could not backup cognitive conditions: %s", e)

        # 3. Atomic replacement
        os.replace(temp_path, target)
    except Exception as e:
        if os.path.exists(temp_path):
            try:
                os.remove(temp_path)
            except OSError:
                pass
        raise e
    return target
```

### 3.4 Recovery Order & Fail-Closed Quarantine [ARCHITECTURE CONTRACT]

```text
Step 1: Attempt to parse data/cognitive_conditions.json
        ├── Valid JSON & Valid Schema ──> Return List[UnresolvedCondition]
        └── File Missing ──> Return empty list [] (First-run bootstrap)
        └── Corrupted / Invalid Schema ──> Proceed to Step 2

Step 2: Attempt to parse data/cognitive_conditions.json.bak
        ├── Valid JSON & Valid Schema ──> Log WARNING, Return List[UnresolvedCondition]
        └── Backup Missing or Corrupted ──> Proceed to Step 3

Step 3: Fail-Closed Quarantine
        ├── Move corrupted file to data/cognitive_conditions.json.corrupt_{timestamp}
        ├── Log ERROR (auditable diagnostic alert)
        └── Return empty list [] (Boot proceeds safely without crashing)
```

### 3.5 Genesis Safeguard (`INV-8`) [ARCHITECTURE CONTRACT]

- `data/cognitive_conditions.json` resides strictly outside `data/profile.json`.
- A missing `cognitive_conditions.json` initializes an empty ledger without modifying `data/profile.json` (`{"is_onboarded": false}`).
- Zero Genesis activation or onboarding mutations occur during condition storage or recovery.

---

## 4. Canonical Referent Adapter Implementation Specification

### 4.1 Collision Resistance & Delimiter Escaping Analysis [ARCHITECTURE CONTRACT]

Under R2 audit findings, naive string concatenation `f"{scope}:{subject}:{predicate}:{object}"` is **vulnerable to delimiter collision** because concept and entity identifiers in Lucia already contain colons (e.g., `scope:root`, `ent:lucia`, `c:IS_FIRST_CONVERSATION`). Naive splitting on `:` yields undefined token lengths.

To guarantee 100% collision resistance, deterministic tokenization, and unambiguous parsing, the canonical encoding rule is specified as **Canonical Structured JSON Tuple Serialization**:

$$\text{canonical\_payload} = \text{json.dumps}([scope, subject, predicate, object], separators=(',', ':'), ensure\_ascii=False)$$

```python
def encode_referent_key(
    scope: str,
    subject: str,
    predicate: str,
    object_: str,
) -> str:
    """
    Encode an epistemic referent into a collision-free canonical string.
    Normalizes all tokens to lowercase and strips extraneous whitespace.
    """
    s_norm = subject.strip().lower()
    p_norm = predicate.strip().lower()
    o_norm = object_.strip().lower()
    sc_norm = scope.strip().lower() if scope else "scope:root"
    
    # Deterministic compact JSON list guarantees zero delimiter ambiguity
    return json.dumps([sc_norm, s_norm, p_norm, o_norm], separators=(",", ":"), ensure_ascii=False)
```

### 4.2 Numeric Subgoal Adapter Boundary [ARCHITECTURE CONTRACT]

Translating a P23-H numeric `InformationSubgoal` into an `UnresolvedCondition`:

```text
┌─────────────────────────────┐
│    InformationSubgoal       │  (target_predicate_id, arg0_id, arg1_id, scope_id)
└──────────────┬──────────────┘
               │
               ▼
┌─────────────────────────────┐
│        SymbolTable          │  (Existing bidirectional projection adapter)
│   id_to_concept(id)         │  (Maps integer IDs -> canonical string tokens)
└──────────────┬──────────────┘
               │
               ▼
┌─────────────────────────────┐
│    encode_referent_key()    │  (Collision-free canonical JSON tuple)
└──────────────┬──────────────┘
               │
               ▼
┌─────────────────────────────┐
│   SHA-256 Hash Digest       │  condition_id = sha256(f"{type}:{referent_key}")
└─────────────────────────────┘
```

Implementation method:
```python
def subgoal_to_condition(
    subgoal: InformationSubgoal,
    symbol_table: SymbolTable,
    epoch: int,
) -> UnresolvedCondition:
    pred_str = symbol_table.id_to_concept(subgoal.target_predicate_id)
    a0_str = symbol_table.id_to_concept(subgoal.arg0_id)
    a1_str = symbol_table.id_to_concept(subgoal.arg1_id) if subgoal.arg1_id != 0 else ""
    scope_str = f"scope:{subgoal.scope_id}" if subgoal.scope_id != 0 else "scope:root"

    ref_key = encode_referent_key(scope_str, a0_str, pred_str, a1_str)
    cond_id = hashlib.sha256(f"{ConditionType.MISSING_PREMISE.value}:{ref_key}".encode("utf-8")).hexdigest()

    return UnresolvedCondition(
        condition_id=cond_id,
        condition_type=ConditionType.MISSING_PREMISE,
        referent_key=ref_key,
        status=ConditionStatus.ACTIVE,
        resolution_source=ResolutionSource.INTERNAL_SEARCH,
        epoch_created=epoch,
    )
```

### 4.3 Reverse Mapping Contract [ARCHITECTURE CONTRACT]

Reverse mapping from `referent_key` back to query parameters:
```python
def decode_referent_key(referent_key: str) -> Tuple[str, str, str, str]:
    tokens = json.loads(referent_key)
    if not isinstance(tokens, list) or len(tokens) != 4:
        raise ValueError(f"Malformed referent key: {referent_key}")
    return (tokens[0], tokens[1], tokens[2], tokens[3])  # (scope, subject, predicate, object)
```
This cleanly enables querying `KnowledgeStore.query(subject=s, predicate=p, object_=o)`.

---

## 5. KnowledgeStore SPO Deduplication Implementation Specification

### 5.1 Internal `_spo_index` Architecture [ARCHITECTURE CONTRACT]

In [`src/core/knowledge/store.py`](file:///c:/Users/Lunafiah/Desktop/My_project/Lucia/src/core/knowledge/store.py), `KnowledgeStore` is augmented with an internal secondary index mapping normalized triples to canonical proposition IDs:

```python
self._spo_index: Dict[Tuple[str, str, str], str] = {}
```

### 5.2 Deduplication & Storage Semantics [ARCHITECTURE CONTRACT]

When `store_proposition(prop: Proposition)` is called:

```text
┌──────────────────────────────────────────────┐
│  store_proposition(prop)                     │
└──────────────────────┬───────────────────────┘
                       │
                       ▼
         Is prop.valid == True?
         ├── NO ──> Store in _propositions[prop.id]; DO NOT index in _spo_index; Return prop.id
         │
         └── YES
              │
              ▼
    Compute key = (prop.subject.lower(), prop.predicate.lower(), prop.object.lower())
              │
              ▼
    Does key exist in _spo_index?
    ├── YES ──> existing_id = _spo_index[key]
    │           existing_prop = _propositions[existing_id]
    │           
    │           If prop.provenance == existing_prop.provenance:
    │               Return existing_id (IDEMPOTENT NO-OP; zero duplicate stored)
    │           
    │           If prop has higher epistemic authority:
    │               Execute revise(existing_id, prop)
    │               Update _spo_index[key] = prop.id
    │               Return prop.id
    │
    └── NO ───> Store _propositions[prop.id] = prop
                Index _spo_index[key] = prop.id
                Return prop.id
```

### 5.3 Backward Compatibility & Rebuilding [ARCHITECTURE CONTRACT]

1. **Rebuild on Boot / Deserialization**:
   In `KnowledgeStore.from_json(json_str)`:
   As propositions are iterated from JSON, for every `prop` where `prop.valid == True`:
   `store._spo_index[(prop.subject.lower(), prop.predicate.lower(), prop.object.lower())] = prop.id`
2. **Existing Caller IDs Preserved**:
   Pre-existing proposition IDs (e.g., `"prop:turn_count"`, `"prop:first_conversation"`) are **100% preserved**. `_spo_index` simply stores a reference mapping the triple to the existing ID.
3. **Deterministic Derivation**:
   In [`src/core/knowledge/derivation.py:57`](file:///c:/Users/Lunafiah/Desktop/My_project/Lucia/src/core/knowledge/derivation.py#L57):
   Replace `uuid.uuid4().hex[:8]` with deterministic hash ID:
   ```python
   derived_id = f"derived:{hashlib.sha256(f'{p1.subject}:{transitive_predicate}:{p2.object}'.encode()).hexdigest()[:12]}"
   ```
   This guarantees that re-running transitive derivation produces identical proposition IDs across process restarts.

---

## 6. Endogenous Trigger Implementation Boundary

### 6.1 Data Structures [ARCHITECTURE CONTRACT]

```python
@dataclass(frozen=True)
class CandidateTrigger:
    """Raw, unqualified candidate trigger emitted by an internal substrate."""
    source_subsystem: str         # "ReasoningKernel" | "KnowledgeStore" | "RelationshipUpdater"
    taxonomy_level: int           # 1 (Maintenance) | 2 (Latent) | 3 (Epistemic) | 4 (Comm)
    referent_key: str             # Canonical encoded referent string
    condition_type: ConditionType # MISSING_PREMISE | CONTRADICTION | RELATIONAL_RUPTURE
    epoch: int
    payload: Dict[str, Any] = field(default_factory=dict)

@dataclass(frozen=True)
class QualifiedEndogenousTrigger:
    """Vetted, authorized trigger permitted to enter process_endogenous()."""
    trigger_id: str               # Deterministic SHA-256 hash
    condition_id: str             # Linked UnresolvedCondition ID
    condition_type: ConditionType
    referent_key: str
    resolution_source: ResolutionSource
    epoch: int
```

### 6.2 The `TriggerQualificationBoundary` Filter [ARCHITECTURE CONTRACT]

Located in `src/core/cognition/qualification.py`:

```python
class TriggerQualificationBoundary:
    """
    Pure, stateless qualification filter.
    NOT an event bus or scheduler daemon.
    """

    @staticmethod
    def qualify(
        candidate: CandidateTrigger,
        condition_ledger: Dict[str, UnresolvedCondition],
        is_orchestrator_busy: bool,
        active_endogenous_depth: int,
    ) -> Tuple[bool, Optional[QualifiedEndogenousTrigger], str]:
        # 1. Level-1 Rejection Invariant (Maintenance dynamics NEVER wake cognition)
        if candidate.taxonomy_level == 1:
            return False, None, "REJECTED_LEVEL_1_MAINTENANCE_DYNAMICS"

        # 2. Level-2 Rejection Invariant (Latent transformation is context-only)
        if candidate.taxonomy_level == 2:
            return False, None, "REJECTED_LEVEL_2_CONTEXT_MODULATION_ONLY"

        # 3. Concurrency Check (User turn takes absolute priority)
        if is_orchestrator_busy:
            return False, None, "DEFERRED_ORCHESTRATOR_BUSY"

        # 4. Anti-Cascading Invariant (Max endogenous depth = 1)
        if active_endogenous_depth >= 1:
            return False, None, "DEFERRED_MAX_CASCADE_DEPTH_REACHED"

        # 5. Condition Reference Verification
        expected_cond_id = hashlib.sha256(
            f"{candidate.condition_type.value}:{candidate.referent_key}".encode("utf-8")
        ).hexdigest()
        
        condition = condition_ledger.get(expected_cond_id)
        if condition is None:
            # Condition not yet registered; auto-register in ACTIVE state
            res_source = (
                ResolutionSource.INTERNAL_SEARCH 
                if candidate.condition_type != ConditionType.RELATIONAL_RUPTURE 
                else ResolutionSource.EXTERNAL_USER
            )
        elif condition.status == ConditionStatus.SUPPRESSED:
            return False, None, "REJECTED_CONDITION_SUPPRESSED"
        elif condition.status == ConditionStatus.RESOLVED:
            return False, None, "REJECTED_CONDITION_ALREADY_RESOLVED"
        else:
            res_source = condition.resolution_source

        # Qualified
        trig_id = hashlib.sha256(
            f"trigger:{candidate.epoch}:{expected_cond_id}".encode("utf-8")
        ).hexdigest()
        
        qualified = QualifiedEndogenousTrigger(
            trigger_id=trig_id,
            condition_id=expected_cond_id,
            condition_type=candidate.condition_type,
            referent_key=candidate.referent_key,
            resolution_source=res_source,
            epoch=candidate.epoch,
        )
        return True, qualified, "QUALIFIED"
```

---

## 7. `process_endogenous()` Contract Specification

### 7.1 Method Signature & Return Type [ARCHITECTURE CONTRACT]

In [`src/core/orchestrator/cognitive_orchestrator.py`](file:///c:/Users/Lunafiah/Desktop/My_project/Lucia/src/core/orchestrator/cognitive_orchestrator.py):

```python
def process_endogenous(
    self,
    trigger: QualifiedEndogenousTrigger,
) -> EndogenousTurnResult:
    """
    Execute a bounded endogenous cognitive cycle.
    Operates without external natural language input (u_input = empty).
    Completes silently by default; never emits autonomous speech.
    """
```

```python
@dataclass(frozen=True)
class EndogenousTurnResult:
    success: bool
    condition_id: str
    final_status: ConditionStatus
    execution_time_s: float
    communicative_affordance: Optional[CommunicativeAffordance] = None
    detail: str = ""
```

### 7.2 Non-Blocking Lock Protocol & User Priority [ARCHITECTURE CONTRACT]

```python
# Acquire turn lock with blocking=False
acquired = self._turn_lock.acquire(blocking=False)
if not acquired:
    # User turn or higher priority process holds lock; defer condition immediately
    self._defer_condition(trigger.condition_id, reason="turn_lock_contention")
    return EndogenousTurnResult(
        success=False,
        condition_id=trigger.condition_id,
        final_status=ConditionStatus.DEFERRED,
        execution_time_s=0.0,
        detail="Deferred due to lock contention",
    )
```

### 7.3 Stage Execution vs. Bypassing Trace [ARCHITECTURE CONTRACT]

```text
====================================================================================================
Stage               Action in process_endogenous()             Justification
====================================================================================================
Stage S0            EXECUTED                                   Advances temporal coordinator baseline;
                                                               user_text="" passed.
Stage S1            BYPASSED                                   Zero external text; no stimulus token.
Stage S2            EXECUTED                                   Reads current limbic PAD prior.
Stage S3            BYPASSED                                   Zero stimulus injected into LNN queue.
Stage S4            BYPASSED                                   No sensory prediction error computed.
Stage S5            EXECUTED                                   Homeostatic check: verifies energy >= 0.20;
                                                               if energy depleted, defers condition.
Stage S6 / S7       EXECUTED (Conditional)                     Queries AffectiveMemory if referent has
                                                               emotional valence.
Stage S8            EXECUTED                                   KnowledgeStore query matching referent key.
P23-H Bounded       EXECUTED                                   Executes verify_candidate_goal() via
Reasoning                                                      EpistemicReasoningService / ReasoningKernel.
Stage S10b (CAPS)   EXECUTED (Conditional)                     If condition produces communicative candidate,
                                                               evaluates CAPS Priority 5 fail-closed check.
Stage S11           BYPASSED BY DEFAULT                        No prompt assembly (silent completion).
Stage S12           BYPASSED                                   Zero conversational pacing sleep.
Stage S13           BYPASSED                                   Zero SLM token generation. Zero GPU compute.
Stage S14           BYPASSED BY DEFAULT                        Fidelity gate skipped when no surface text.
Stage S15           BYPASSED                                   Zero audio playback or Live2D speech actuation.
Stage S16.5         EXECUTED                                   Persists updated data/cognitive_conditions.json.
====================================================================================================
```

### 7.4 Epistemic Resolution & State Mutation [ARCHITECTURE CONTRACT]

- When `ReasoningKernel.backward_chain()` evaluates the referent:
  - If $K3 = \text{TRUE}$ or $K3 = \text{FALSE}$: Condition transitions to `ConditionStatus.RESOLVED`.
  - If $K3 = \text{UNKNOWN}$ and resolution source is `INTERNAL_SEARCH`: Condition transitions to `ConditionStatus.DEFERRED`.
- If an unhandled exception occurs: Fail-closed; transaction aborts; condition preserved in `DEFERRED` state; zero corruption of persistent knowledge or relationships.

---

## 8. Lifecycle & State Transition Matrix

The 4-state lifecycle of `UnresolvedCondition` is governed strictly by the transition table below:

| Current State | Transition Event | Next State | Permitted Authority | Persistence Consequence |
|---|---|---|---|---|
| *(Non-existent)* | Candidate qualified from missing premise or contradiction | `ACTIVE` | `TriggerQualificationBoundary` | In-memory registered in `_condition_ledger`. |
| `ACTIVE` | User turn arrives or `_turn_lock` is busy | `DEFERRED` | `CognitiveOrchestrator` | Preserved in memory; committed at S16.5. |
| `ACTIVE` | Compute budget reached without resolution ($k \ge 2$) | `DEFERRED` | `ReasoningKernel` | Preserved in memory; committed at S16.5. |
| `ACTIVE` | K3 evaluates to `TRUE` or `FALSE` | `RESOLVED` | `EpistemicReasoningService` | Marked resolved; purged on next disk sync. |
| `ACTIVE` | Contradicting premise retracted via JTMS cascade | `RESOLVED` | `JTMS` | Marked resolved; purged on next disk sync. |
| `ACTIVE` | Repeated failed qualification / refractory trigger | `SUPPRESSED` | `CognitiveOrchestrator` | Written as `SUPPRESSED` to disk. |
| `DEFERRED` | Next endogenous cycle wakes and qualifies condition | `ACTIVE` | `CognitiveOrchestrator` | In-memory status update. |
| `DEFERRED` | Root term invalidated by external user input | `RESOLVED` | `LanguageIngressGate` | Marked resolved; purged on next disk sync. |
| `SUPPRESSED` | Refractory timeout elapses or new evidence admitted | `DEFERRED` | `CognitiveOrchestrator` | In-memory status update. |
| `RESOLVED` | Cleanup sweep post-commit | *(Pruned)* | `CognitiveOrchestrator` | Removed from active memory and disk. |

### Forbidden Transitions:
- `RESOLVED` $\to$ `ACTIVE`: Forbidden. Terminal state.
- `SUPPRESSED` $\to$ `ACTIVE`: Forbidden. Must transition to `DEFERRED` first to pass qualification.
- Unauthenticated mutation: Any code outside `CognitiveOrchestrator` or `EpistemicReasoningService` attempting to mutate status raises `PermissionError`.

---

## 9. Communication Boundary Specification

### 9.1 The Epistemic Non-Equivalence Invariant [ARCHITECTURE CONTRACT]

$$\mathbf{P23\text{-}H\ TRUE \neq ASSERT}$$
$$\mathbf{UnresolvedCondition \neq Permission\ to\ Speak}$$
$$\mathbf{Confidence \neq Warrant\ to\ Utter}$$

1. Bounded deduction proving that a proposition is logically true within the closed symbolic world of `TermArena` provides **deductive validity**, NOT epistemic entitlement or social appropriateness to interrupt the user.
2. A missing premise under an `UnresolvedCondition` indicates an epistemic gap, NOT an obligation or authorization to vocalize a question.

### 9.2 Communicative Affordance vs. Output Emission [ARCHITECTURE CONTRACT]

If `process_endogenous()` produces a communicative affordance (e.g. an inquiry for a missing premise with `resolution_source = EXTERNAL_USER`):
1. **CAPS Priority 5 Enforcement**:
   - The candidate predicate and argument concepts are checked against `AdmissibleEvidencePool`.
   - If not admissible, CAPS produces `CommunicativeAct.SILENCE`.
2. **Quarantine Enforcement (`[RESEARCH / QUARANTINED]`)**:
   - The affordance is stored internally in `CognitiveOrchestrator._pending_communicative_affordance`.
   - It is **NEVER** dispatched to `LLMBackend`, `PromptAssembler`, `PiperTTS`, or Live2D audio playback.
   - When the user next initiates an external turn ($t+1$), `_pending_communicative_affordance` is passed to CAPS as a **contextual dialogue bias**, allowing natural dyadic integration during the normal user-initiated turn.

---

## 10. Test Specification (Verification Requirements Only)

> [!IMPORTANT]
> **NO TEST CODE AUTHORED IN THIS TASK**:  
> The specifications below define the verification contracts and expected assertions for the subsequent implementation phase.

### 10.1 Unit Test Specifications

| Test Case Identifier | Target Module | Test Scenario & Verification Contract | Expected Invariant / Assertion |
|---|---|---|---|
| `TEST-P23D-COND-001` | `condition.py` | Instantiation and deterministic ID computation. | Given identical type and referent key, `condition_id` is bit-exact SHA-256 digest. Exactly 6 fields exist. |
| `TEST-P23D-COND-002` | `condition.py` | Immutability and copy-on-write transition. | Direct attribute assignment on `UnresolvedCondition` raises `FrozenInstanceError`. `transition_to()` returns fresh instance. |
| `TEST-P23D-COND-003` | `condition.py` | Deserialization validation of malformed records. | Missing fields or invalid enum strings raise `ValueError`. Corrupted records fail-closed. |
| `TEST-P23D-PERS-001` | `condition_persistence.py` | Atomic persistence and backup creation. | `save_conditions()` writes `.tmp` then replaces target. Existing target is preserved in `.json.bak`. |
| `TEST-P23D-PERS-002` | `condition_persistence.py` | Crash-safe recovery and fallback order. | Corrupting primary file triggers automatic fallback to `.json.bak`. Corrupting both triggers `.corrupt` quarantine and returns `[]`. |
| `TEST-P23D-ADPT-001` | `referent_adapter.py` | Collision resistance with colon-containing tokens. | Referent tokens containing `:` (e.g. `c:has_color`, `ent:lucia`) encode into compact JSON tuple; decoded tokens match originals 100%. |
| `TEST-P23D-DEDUP-001`| `store.py` | Idempotent proposition deduplication. | Storing identical $(S, P, O)$ twice returns the original `prop.id`. `len(_propositions)` does not increment. |
| `TEST-P23D-DEDUP-002`| `derivation.py` | Deterministic transitive derivation. | Re-running transitive derivation produces identical `derived:` IDs; zero duplicate propositions created in `KnowledgeStore`. |

### 10.2 Integration Test Specifications

| Test Case Identifier | Integration Boundary | Test Scenario & Verification Contract | Expected Invariant / Assertion |
|---|---|---|---|
| `TEST-P23D-INT-001` | Subgoal $\to$ Condition | `InformationSubgoal` emitted by `ReasoningKernel` converted via `subgoal_to_condition()`. | Produced `UnresolvedCondition` contains canonical referent string and status `ACTIVE`. |
| `TEST-P23D-INT-002` | Qualification Filter | Level 1 maintenance dynamics (ODE, decay) injected into `TriggerQualificationBoundary`. | `qualify()` returns `False` with `REJECTED_LEVEL_1_MAINTENANCE_DYNAMICS`. |
| `TEST-P23D-INT-003` | Qualification Filter | Level 3 missing premise candidate injected into `TriggerQualificationBoundary`. | `qualify()` returns `True` and emits `QualifiedEndogenousTrigger`. |
| `TEST-P23D-INT-004` | Orchestrator Cycle | `process_endogenous()` invoked with qualified trigger. | Stages S1, S11–S15 skipped; S0, S2, S5, S8 executed; P23-H backward chain resolves condition to `RESOLVED`. |
| `TEST-P23D-INT-005` | Turn Lock Contention | User turn holds `_turn_lock`; `process_endogenous()` invoked concurrently. | Endogenous cycle immediately defers (`blocking=False`); user turn completes unhindered. |
| `TEST-P23D-INT-006` | Communication Quarantine | Endogenous cycle produces communicative candidate. | Candidate buffered in `_pending_communicative_affordance`; zero audio playback or surface text output emitted. |

### 10.3 Safety & Invariant Tests

| Test Case Identifier | Governing Invariant | Test Scenario & Verification Contract | Expected Invariant / Assertion |
|---|---|---|---|
| `TEST-P23D-SAFE-001` | `INV-8` Genesis Gate | Execute full endogenous lifecycle test suite. | `data/profile.json` remains bit-exact (`{"is_onboarded": false}`). Zero Genesis state change. |
| `TEST-P23D-SAFE-002` | Anti-Cascade Invariant | Trigger emitted during active endogenous cycle. | `active_endogenous_depth >= 1` blocks qualification; secondary trigger saved as `DEFERRED`. Depth strictly $\le 1$. |
| `TEST-P23D-SAFE-003` | F15 Anti-Self-Echo | Assistant-derived condition presented to ingress gate. | Origin tagged as `INTERNAL_GAP`; prevented from escalating to `USER_STATED` or `FACT`. |
| `TEST-P23D-SAFE-004` | P23-H Frozen Purity | Audit P23-H kernel files post-test. | P23-H files (`engine.py`, `jtms.py`, `rules.py`) have zero git modifications. |

---

## 11. Migration & Backward Compatibility Specification

### 11.1 First-Run Bootstrap [ARCHITECTURE CONTRACT]

```text
On system startup:
├── Check if data/cognitive_conditions.json exists
│   ├── EXISTS ──> Load via condition_persistence.load_conditions()
│   └── DOES NOT EXIST ──> Initialize self._condition_ledger = {}
└── No error logged; zero artificial files created until first commit barrier.
```

### 11.2 KnowledgeStore Compatibility [ARCHITECTURE CONTRACT]

- Existing `KnowledgeStore` JSON schemas and serialized `data/knowledge.json` files are **100% backward compatible**.
- When loading an existing store, `_spo_index` is constructed on the fly from valid propositions.
- Any existing proposition IDs (`"prop:..."`, `"peano:..."`) remain unchanged.

---

## 12. Performance & 20-Watt Whole Brain Architecture Boundary

To preserve Lucia's 20-Watt execution envelope on local edge hardware, the specification distinguishes three performance tiers:

```text
====================================================================================================
Tier                  Specification Scope              Mandatory Enforcement Rule
====================================================================================================
ARCHITECTURE          Non-negotiable invariants        1. Zero GPU SLM compute during silent endogenous cycles.
INVARIANTS            enforced in code.                2. Memory lock hold time <= 1 ms.
                                                       3. Non-blocking lock acquisition (blocking=False).
                                                       4. Maximum call stack depth = 1 (no recursive cycles).
----------------------------------------------------------------------------------------------------
IMPLEMENTATION        Target performance thresholds    1. Trigger qualification latency < 0.1 ms (CPU).
TARGETS               for unit/integration benchmarks. 2. Full endogenous cognitive pass < 2.0 ms (CPU).
                                                       3. Atomic condition serialization < 5.0 ms (Disk I/O).
----------------------------------------------------------------------------------------------------
TUNING & EVALUATION   Tuning parameters reserved       1. Idle wait cooldown: 120s (Evaluation only).
PARAMETERS            for experimental harnesses       2. Max condition retries: 3 (Evaluation only).
                      (NOT hard architecture).         3. Metabolic energy threshold: 0.20 (Evaluation only).
====================================================================================================
```

---

## 13. Exact Implementation File Map

This authoritative map defines every file to be touched, created, or reused during the subsequent implementation phase:

| File Path | Component Status | Subsystem Responsibility | Permitted Change Type |
|---|---|---|---|
| `src/core/cognition/contract/condition.py` | `NEW MINIMAL PRIMITIVE` | Defines `UnresolvedCondition`, `ConditionType`, `ConditionStatus`, `ResolutionSource`. | New file implementation. |
| `src/core/cognition/condition_persistence.py` | `NEW MINIMAL PRIMITIVE` | Implements `save_conditions()`, `load_conditions()`, atomic rename, `.bak` fallback. | New file implementation. |
| `src/core/cognition/referent_adapter.py` | `NEW MINIMAL PRIMITIVE` | Implements `encode_referent_key()`, `decode_referent_key()`, `subgoal_to_condition()`. | New file implementation. |
| `src/core/cognition/qualification.py` | `NEW MINIMAL PRIMITIVE` | Implements `TriggerQualificationBoundary.qualify()` and candidate trigger structures. | New file implementation. |
| `src/core/knowledge/store.py` | `EXISTING` | Adds internal `_spo_index` and dedup logic in `store_proposition()`. | Surgical additive extension. |
| `src/core/knowledge/derivation.py` | `EXISTING` | Replaces random `uuid.uuid4()` with deterministic hash ID in transitive derivation. | Deterministic ID replacement. |
| `src/core/orchestrator/cognitive_orchestrator.py` | `EXISTING` | Adds `_condition_ledger`, wires boot load/S16.5 save, implements `process_endogenous()`. | Additive method & lifecycle wiring. |
| `tests/unit/test_p23d_condition.py` | `NEW TEST SUITE` | Unit tests for `UnresolvedCondition` schema, hashing, immutability, and validation. | New test file. |
| `tests/unit/test_p23d_persistence.py` | `NEW TEST SUITE` | Unit tests for atomic writing, backup recovery, and fail-closed quarantine. | New test file. |
| `tests/unit/test_p23d_spo_dedup.py` | `NEW TEST SUITE` | Unit tests for `KnowledgeStore` deduplication, `_spo_index`, and deterministic derivation. | New test file. |
| `tests/unit/test_p23d_endogenous_orchestration.py` | `NEW TEST SUITE` | Integration tests for trigger qualification, `process_endogenous()`, and quarantine. | New test file. |

---

## 14. Explicit Non-Goals & Prohibitions

During the implementation phase, the implementing agent is **STRICTLY PROHIBITED** from:
- Creating a background Scheduler, Cron, or timer thread loop.
- Creating an Event Bus, Pub/Sub broker, or central message dispatcher.
- Creating an Autonomous Agent loop or continuous-thinking daemon.
- Creating a Goal Manager or ACT-R/SOAR Goal Buffer subsystem.
- Creating a Candidate Arbitration Engine or utility auction system.
- Creating a Global Identity or Persona synthesizer (`INV-2`).
- Emitting unprompted synthetic audio or natural-language text.
- Reopening or modifying P23-H kernel files (`src/core/cognition/kernel/`).
- Introducing cloud dependencies or external API calls (`INV-5`).
- Mutating or initializing Genesis onboarding in `data/profile.json` (`INV-8`).

---

## 15. Implementation Readiness Matrix & Verdict

### Implementation Readiness Matrix

| Architectural Contract Requirement | Fully Specified? | Concrete Repository Mapping? | Deterministically Testable? | Implementation Status |
|---|:---:|:---:|:---:|:---:|
| **UnresolvedCondition Primitive** | **YES** (§2) | `src/core/cognition/contract/condition.py` | **YES** (`TEST-P23D-COND-001..003`) | **`FROZEN & READY`** |
| **Durable Persistence Authority** | **YES** (§3) | `src/core/cognition/condition_persistence.py` | **YES** (`TEST-P23D-PERS-001..002`) | **`FROZEN & READY`** |
| **Collision-Free Canonical Referent**| **YES** (§4) | `src/core/cognition/referent_adapter.py` | **YES** (`TEST-P23D-ADPT-001`) | **`FROZEN & READY`** |
| **KnowledgeStore SPO Deduplication** | **YES** (§5) | `src/core/knowledge/store.py`, `derivation.py` | **YES** (`TEST-P23D-DEDUP-001..002`) | **`FROZEN & READY`** |
| **Trigger Qualification Boundary** | **YES** (§6) | `src/core/cognition/qualification.py` | **YES** (`TEST-P23D-INT-002..003`) | **`FROZEN & READY`** |
| **`process_endogenous()` Entry Point**| **YES** (§7) | `src/core/orchestrator/cognitive_orchestrator.py` | **YES** (`TEST-P23D-INT-004..005`) | **`FROZEN & READY`** |
| **Lifecycle State Machine** | **YES** (§8) | Condition & Orchestrator transition table | **YES** (`TEST-P23D-COND-002`) | **`FROZEN & READY`** |
| **Communication Quarantine Boundary**| **YES** (§9) | CAPS & Orchestrator pending affordance | **YES** (`TEST-P23D-INT-006`) | **`FROZEN & READY`** |
| **Safety & Genesis Invariants** | **YES** (§10.3) | `INV-8`, F15, Anti-cascade depth $\le 1$ | **YES** (`TEST-P23D-SAFE-001..004`) | **`FROZEN & READY`** |

---

### Final Implementation Readiness Verdict

```text
================================================================================
               P23-D IMPLEMENTATION SPECIFICATION V1 VERDICT:
                         READY FOR IMPLEMENTATION
================================================================================
```

### Verdict Justification:
1. **Zero Architectural Ambiguity**: Every component, field, method signature, lock interaction, and transition table is explicitly mapped to concrete files in `src/`.
2. **Deterministic & Inspectable**: No speculative subsystems (Scheduler, Event Bus, Agent Loop) are introduced.
3. **Repository Preservation**: P23-H reasoning kernel remains 100% frozen; Genesis onboarding gate (`data/profile.json`) remains strictly untouched; 20-Watt execution envelope is strictly enforced.
4. **Complete Implementation Roadmap**: The implementing agent has a complete, file-by-file blueprint with exact signatures and required invariants, requiring zero spontaneous architectural decision-making during coding.
