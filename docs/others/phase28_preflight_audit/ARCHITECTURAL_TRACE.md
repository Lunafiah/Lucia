# Architectural Trace of Production Cognitive Substrates

**Audit Reference**: `EXP-ENDOGENOUS-COMM-PREFLIGHT-001`  
**Target Repository**: `src/core/`  
**Analysis Type**: Read-Only Substrate Inspection  

---

## 1. Affective & Bodily Substrate (`src/core/emotion/`)

### Subsystem Architecture
The emotional engine is implemented in [emotion_core.py](file:///c:/Users/Lunafiah/Desktop/My_project/Lucia/src/core/emotion/emotion_core.py) as a Coupled Multi-Timescale Liquid Neural Network (Coupled MT-LNN). It solves a non-linear ordinary differential equation (ODE) every 200 ms:
$$\frac{dh_f}{dt} = \frac{-h_f + \tanh(W_{ff} h_f + W_{fs}(s_s - s^*_{\text{philia}}) + U_f x + b_f)}{\tau_{\text{fast}}}$$
$$\frac{ds_s}{dt} = \frac{-(s_s - s^*_{\text{philia}})}{\tau_{\text{decay}}} + \frac{\tanh(W_{sf} h_f + W_{sh} \Delta m)}{\tau_{\text{charge}}}$$
where:
- $h_f \in \mathbb{R}^{32}$ is the fast reactive layer.
- $s_s \in \mathbb{R}^{16}$ is the slow latent mood field.
- $m \in \mathbb{R}^4$ is the homeostatic somatic state: `[energy, cognitive_load, tension, stability]`.
- $\text{PAD} \in [-1.0, 1.0]^3$ is the projected pleasure, arousal, dominance vector.

### Data Inspection & Audit Findings
1. **Available Data**:
   - `PADState`: `pleasure` (float), `arousal` (float), `dominance` (float), `timestamp` (monotonic float).
   - `_m_homeo`: 4D float vector `[energy, cognitive_load, tension, stability]`.
   - `_h`, `_s_slow`: 32D and 16D continuous activation vectors.
2. **Is it purely numeric?**: **YES.** 100% of internal state consists of floating-point scalars and NumPy arrays.
3. **Does it contain provenance?**: **NO.** The only historical metadata is an internal monotonic integer token `_stimulus_seq` used to track causal FIFO consumption.
4. **Does it reference a specific event/entity/proposition?**: **NO.** A state where $\text{tension} = 0.88$ contains zero information regarding *why* tension is high, *who* or *what* provoked it, or what conversational entity it relates to.
5. **Can it independently identify WHAT happened?**: **NO.**
6. **Classification**: **TYPE 0 (Raw Continuous State)**.

---

## 2. Active Inference & Epistemic Substrate (`src/core/inference/active_inference.py`)

### Subsystem Architecture
`ActiveInferenceEngine` implements an online generative linear transition model predicting affective PAD trajectories:
$$\hat{q} = A p + b$$
where $p \in [-1, 1]^3$ is prior PAD and $q \in [-1, 1]^3$ is observed posterior PAD. It updates parameters $A \in \mathbb{R}^{3 \times 3}$ and $b \in \mathbb{R}^3$ via gradient descent minimizing Free Energy with KL-regularization toward identity.

### Data Inspection & Audit Findings
1. **Available Data**:
   - `step(pad_before, pad_after) -> float`: Returns `pred_error = float(np.linalg.norm(predicted - q))`.
   - `get_belief_state()`: Returns `{"A_matrix": self._A, "b_vector": self._b}`.
2. **Is it purely numeric?**: **YES.** Consists entirely of $3 \times 3$ transformation matrices, bias vectors, and a scalar Euclidean prediction error.
3. **Does it contain provenance?**: **NO.**
4. **Does it reference an unresolved proposition or belief?**: **NO.** Despite the name "Active Inference", this module does not perform epistemic foraging over facts, propositions, or dialogue statements. It is strictly a mathematical predictor of continuous 3D PAD transitions.
5. **Can it produce a communicative inquiry?**: **NO.** A high prediction error ($0.95$) indicates unexpected emotional change, not an identifiable factual ambiguity or conversational question.
6. **Classification**: **TYPE 0 (Raw Predictive Gradient)**.

---

## 3. Ecphory & Affective Memory Substrate (`src/core/memory/`)

### Subsystem Architecture
Implemented across [affective_memory.py](file:///c:/Users/Lunafiah/Desktop/My_project/Lucia/src/core/memory/affective_memory.py) and [ecphory.py](file:///c:/Users/Lunafiah/Desktop/My_project/Lucia/src/core/memory/ecphory.py).
Traces are stored in a Sparse Distributed Memory (SDMCore). Co-encodes an address vector ($D=256$ bits) and content vector ($M=64$ floats) with a snapshot of the current 3D PAD tag.

### Data Inspection & Audit Findings
1. **MemoryTrace Definition**:
   ```python
   @dataclass
   class MemoryTrace:
       trace_id: int
       address_vec: np.ndarray    # uint8 (D,)
       content_vec: np.ndarray    # float32 (M=64,)
       pad_tag: PADState          # 3D float
       timestamp: float
       decay_weight: float
       slow_latent_trace: Optional[np.ndarray] # 16D float
   ```
2. **Available Retrieval Data**:
   - `RecollectionResult`: `salience` (float), `r_slow_bounded` (16D float), `winning_trace_id` (int), `active` (bool).
   - `echo_vector`: 64D float vector synthesized by weighted summation of top-$K$ resonant traces.
3. **Is it purely numeric?**: **YES.** The content vector is an ungrounded 64D floating-point embedding.
4. **Does retrieved information retain proposition/event identity?**: **NO.** While `winning_trace_id` identifies the memory slot, `MemoryTrace` has no natural-language sentence, proposition reference, entity tag, or relational label stored inside it.
5. **How is it consumed in production?**:
   - In [cognitive_orchestrator.py](file:///c:/Users/Lunafiah/Desktop/My_project/Lucia/src/core/orchestrator/cognitive_orchestrator.py#L655), `r_slow_bounded` is injected as a numeric forcing current into `EmotionCore._s_slow`.
   - In S7, `m_avail = 1.0 if norm(echo_vector) > 0.01 else 0.0`.
   - In S10 `comm_policy`, it simply triggers an extra 150 ms response pacing delay.
   - **All semantic provenance is non-existent at encoding time.**
6. **Classification**: **TYPE 1 (Salient Continuous Echo)**.

---

## 4. Knowledge Store & Epistemic Logic (`src/core/knowledge/`, `src/core/cognition/kernel/`)

### Subsystem Architecture
Implemented in [proposition.py](file:///c:/Users/Lunafiah/Desktop/My_project/Lucia/src/core/knowledge/proposition.py), [store.py](file:///c:/Users/Lunafiah/Desktop/My_project/Lucia/src/core/knowledge/store.py), [derivation.py](file:///c:/Users/Lunafiah/Desktop/My_project/Lucia/src/core/knowledge/derivation.py), and [jtms.py](file:///c:/Users/Lunafiah/Desktop/My_project/Lucia/src/core/cognition/kernel/jtms.py).
Contains structured symbolic knowledge represented as explicit $(S, P, O)$ propositions with formal provenance and belief maintenance.

### Data Inspection & Audit Findings
1. **Proposition Definition**:
   ```python
   @dataclass
   class Proposition:
       id: str
       subject: str                      # e.g., "ent:user"
       predicate: str                    # e.g., "c:PREFERS"
       object: str                       # e.g., "tea"
       confidence: float                 # [0.0, 1.0]
       provenance: ProvenanceType        # USER_STATED, INFERRED, DERIVED, CONTRADICTED, etc.
       evidence_ids: List[str]
       created_at: float
       valid: bool
       superseded_by: Optional[str]
   ```
2. **JTMS Justification Definition**:
   ```python
   @dataclass
   class Justification:
       justification_id: int
       rule_id: int
       consequence_id: int
       premise_ids: Tuple[int, ...]
       premise_count: int
       is_valid: bool
   ```
3. **Is it semantic and grounded?**: **YES.** This is a genuine, inspectable, symbolic knowledge substrate. Propositions have clear entity referents, explicit predicates, confidence scores, and dependency DAGs in JTMS.
4. **Can it identify WHAT happened?**: **YES**, for propositions stored within it.
5. **Critical Limitation — Current Wiring Gap**:
   - In `CognitiveOrchestrator` Stage S8, `KnowledgeStore` is queried via:
     ```python
     known_propositions = self._knowledge_store.query_relevant(input_text, max_results=5)
     ```
   - It is queried **exclusively using substring matching against the incoming user text**.
   - There is NO background process or query method evaluating endogenous epistemic gaps (e.g. checking for `CONTRADICTED` propositions, stale premises in JTMS, or unresolved information subgoals) in the absence of user input.
6. **Classification**: **TYPE 2 (Grounded Symbolic Proposition)** — fully grounded, but currently strictly passive and user-query slave.

---

## 5. Relational State (`src/core/relationship/`)

### Subsystem Architecture
Implemented in [state.py](file:///c:/Users/Lunafiah/Desktop/My_project/Lucia/src/core/relationship/state.py), [signals.py](file:///c:/Users/Lunafiah/Desktop/My_project/Lucia/src/core/relationship/signals.py), and [updater.py](file:///c:/Users/Lunafiah/Desktop/My_project/Lucia/src/core/relationship/updater.py).
Maintains a 4-dimensional interpersonal vector $R_t \in [0.0, 1.0]^4$:
- `familiarity`: Accumulated interaction volume.
- `trust`: Reliability of interaction expectations.
- `closeness`: Relational proximity and shared depth.
- `reciprocity`: Mutually sustained conversational balance.

### Data Inspection & Audit Findings
1. **Available State**:
   - `RelationshipState.to_array()`: 4D float array $[F, T, C, R]$.
   - `updater.history`: List of `RelationshipHistoryEntry` audit objects containing `signal_type` (`CONFLICT_DISMISSAL`, `REPAIR_ATTEMPT`, `EMOTIONAL_DISCLOSURE`, `COLLABORATIVE_SUCCESS`).
2. **Is it purely numeric?**: The active state $R_t$ is purely a 4D float vector.
3. **Does it contain provenance?**: In the audit history, each step records `timestamp` and `signal_type`.
4. **Does it reference a specific event or unresolved relational obligation?**: **NO.**
   - While `RelationshipSignalType.CONFLICT_DISMISSAL` exists as a category, the entry records only that a conflict occurred at turn $t$.
   - It maintains no lifecycle status (e.g. `UNRESOLVED_CONFLICT`, `PENDING_REPAIR`, `RESOLVED`).
   - `updater.get_state()` returns ONLY the 4D float snapshot. The audit history is never inspected by the conversational planner or communication policy.
5. **Classification**: **TYPE 0 (Continuous State) with unindexed TYPE 2 historical audit log**.
