# Data-Lineage & Grounding Readiness Matrix

**Audit Reference**: `EXP-ENDOGENOUS-COMM-PREFLIGHT-001`  
**Target Repository**: `src/core/`  
**Purpose**: Map exact data lineage and evaluate compatibility against the `GroundedReason` contract.

---

## 1. Substrate Data-Lineage Map

| Subsystem Source | Actual Data Object | Numeric Only? | Provenance? | Entity / Event Referent? | Explicit Proposition? | Temporal Validity? | GroundedReason Ready? |
|---|---|:---:|:---:|:---:|:---:|:---:|:---:|
| **EmotionCore** | `PADState`, `_m_homeo`, `_h`, `_s_slow` | **YES** | Monotonic token only | **NO** | **NO** | Transient float | **NO** |
| **ActiveInferenceEngine** | Matrix $A$, Vector $b$, scalar `pred_error` | **YES** | **NO** | **NO** | **NO** | Per-tick scalar | **NO** |
| **AffectiveMemory** | `MemoryTrace.content_vec` (64D) | **YES** | Slot ID only | **NO** | **NO** | Decay weight | **NO** |
| **EcphoryEngine** | `RecollectionResult`, `echo_vector` (64D) | **YES** | Winning ID only | **NO** | **NO** | Transient float | **NO** |
| **RelationshipState** | `RelationshipState` $[F, T, C, R]$ | **YES** | **NO** | **NO** | **NO** | Timestamp float | **NO** |
| **RelationshipHistory**| `RelationshipHistoryEntry` | **NO** | Timestamp, step int | Categorical signal type | **NO** | Immutable audit | **NO** |
| **KnowledgeStore** | `Proposition` | **NO** | `ProvenanceType` | **YES** (`ent:X`) | **YES** $(S, P, O)$ | `valid: bool` | **PARTIAL** (Query-slave) |
| **JTMS** | `Justification` | **NO** | Rule ID, premise IDs | Internal term IDs | Logical rule DAG | `is_valid: bool` | **PARTIAL** (Truth-sync only) |
| **DiscourseCache** | `DiscourseReferent` | **NO** | Turn ID | Entity label / mention | Context binding | Salience decay | **PARTIAL** (User-input only) |

---

## 2. Lineage Breakdown for Individual Subsystems

### Subsystem 1: `EmotionCore`
```text
SOURCE:              src/core/emotion/emotion_core.py
ACTUAL TYPE:         PADState & np.ndarray
FIELDS AVAILABLE:    pleasure: float, arousal: float, dominance: float, timestamp: float
PROVENANCE:          _stimulus_seq (strictly sequential FIFO ordering)
SEMANTIC REFERENT:   None (pre-reflective dynamical activation)
CURRENT CONSUMER:    CognitiveOrchestrator Stage S10 (CommunicationPolicy actuation)
LOST INFORMATION:    What user utterance or environmental stimulus caused the current PAD state.
```

### Subsystem 2: `ActiveInferenceEngine`
```text
SOURCE:              src/core/inference/active_inference.py
ACTUAL TYPE:         float (prediction_error) & np.ndarray (A_matrix, b_vector)
FIELDS AVAILABLE:    norm(delta): float, A: (3, 3), b: (3,)
PROVENANCE:          None
SEMANTIC REFERENT:   None (continuous vector prediction)
CURRENT CONSUMER:    CognitiveOrchestrator Stage S4 trace summary
LOST INFORMATION:    None lost, because ActiveInferenceEngine operates purely over 3D PAD vectors.
```

### Subsystem 3: `EcphoryEngine` & `AffectiveMemory`
```text
SOURCE:              src/core/memory/ecphory.py, affective_memory.py
ACTUAL TYPE:         RecollectionResult & MemoryTrace
FIELDS AVAILABLE:    trace_id: int, address_vec: uint8(256,), content_vec: float32(64,), salience: float
PROVENANCE:          trace_id integer slot
SEMANTIC REFERENT:   None. Content vector is ungrounded numerical embedding.
CURRENT CONSUMER:    S6 (ODE slow-field injection), S7 (m_avail binary gate), S10 (150ms delay)
LOST INFORMATION:    Conversational meaning, original user text, dialogue epoch, and entity relationships.
```

### Subsystem 4: `RelationshipUpdater`
```text
SOURCE:              src/core/relationship/updater.py
ACTUAL TYPE:         RelationshipState & RelationshipHistoryEntry
FIELDS AVAILABLE:    familiarity: float, trust: float, closeness: float, reciprocity: float, signal_type: Enum
PROVENANCE:          Audit step counter and timestamp
SEMANTIC REFERENT:   Implicitly the primary user ("ent:user"), but no specific event or unresolved repair state.
CURRENT CONSUMER:    CognitiveOrchestrator Stage S9 (read into comm_policy)
LOST INFORMATION:    Whether a past CONFLICT_DISMISSAL was ever addressed or resolved in dialogue.
```

### Subsystem 5: `KnowledgeStore`
```text
SOURCE:              src/core/knowledge/store.py
ACTUAL TYPE:         Proposition
FIELDS AVAILABLE:    id: str, subject: str, predicate: str, object: str, confidence: float, provenance: ProvenanceType, valid: bool
PROVENANCE:          ProvenanceType (USER_STATED, OBSERVED, INFERRED, DERIVED, VERIFIED, CONTRADICTED)
SEMANTIC REFERENT:   Explicit entities, properties, and factual claims.
CURRENT CONSUMER:    Stage S8 query_relevant(input_text) -> Stage S10b CAPS
LOST INFORMATION:    Endogenous salience! Propositions have confidence, but no autonomous urgency or obligation score.
```

---

## 3. The `GroundedReason` Contract Test

Evaluating whether fields of the experimental `GroundedReason` contract can be legitimately sourced from existing production data without fabrication:

| Field Required by `GroundedReason` | Sourced from Existing Substrate? | Real Production Source | Assessment & Gap |
|---|:---:|---|---|
| `reason_type` | **PARTIAL** | `RelationshipSignalType`, `ProvenanceType` | Categories exist, but are not unified into a communicative reason taxonomy. |
| `source_id` | **YES** | `Proposition.id`, `Justification.justification_id`, `HistoryEntry.step` | Real unique identifiers exist in symbolic stores. |
| `subject` | **PARTIAL** | `Proposition.subject`, `DiscourseReferent.entity_id` | Exists in KnowledgeStore; completely absent in Emotion, Ecphory, Inference. |
| `predicate` | **PARTIAL** | `Proposition.predicate` | Exists in KnowledgeStore; absent in continuous engines. |
| `object_val` | **PARTIAL** | `Proposition.object` | Exists in KnowledgeStore; absent in continuous engines. |
| `salience` | **NO** | None for propositions | Emotion/Ecphory have salience, but no propositions. Knowledge has propositions, but no salience. |
| `is_valid` | **YES** | `Proposition.valid`, `Justification.is_valid` | High fidelity truth maintenance exists in JTMS and KnowledgeStore. |
| `target` | **NO** | Hardcoded to `"user"` | No dyadic recipient modeling in internal memory. |
| `intended_effect` | **NO** | None | Completely absent. No substrate computes the expected social or epistemic effect of communicating. |

---

## 4. Grounding Readiness Verdict

- **Can real Lucia cognitive state produce a `GroundedReason` right now?**: **NO.**
- **Why?**:
  - The continuous substrates (`EmotionCore`, `ActiveInferenceEngine`, `EcphoryEngine`) that track dynamic cognitive vitality contain **zero propositions or entities**.
  - The symbolic substrate (`KnowledgeStore`, `JTMS`) that contains rich propositions possesses **zero endogenous temporal vitality or communicative goals**, and is only ever activated when incoming user text contains matching words.
  - There is currently **no bridging layer** that binds a change in continuous state to a specific symbolic proposition.
