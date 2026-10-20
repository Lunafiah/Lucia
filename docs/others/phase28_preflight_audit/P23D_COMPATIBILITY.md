# P23-D Realization & Safety Compatibility Audit

**Audit Reference**: `EXP-ENDOGENOUS-COMM-PREFLIGHT-001`  
**Governing Invariants**: ADR-035 (P23-D Realization Boundary), ADR-032 (Affective Communication Adaptation), Invariant INV-2 (No Reflective Ego), Invariant INV-5 (Edge Execution)  
**Target Architecture**: Cognitive Pipeline Stages S10 $\to$ S11 $\to$ S12 $\to$ S14  

---

## 1. The P23-D Production Realization Pipeline

In Phase 23-D, Lucia ratified and froze the production realization boundary. The ratified dataflow is strictly unidirectional and contract-enforced:

```text
┌──────────────────────────────────────────────┐
│  Stage S10b: CAPS (Communicative Planning)   │
│  - Selects CommunicativeAct & Predicate      │
│  - Evaluates Grounding Invariant Fail-Closed │
└──────────────────────┬───────────────────────┘
                       │
                       ▼
┌──────────────────────────────────────────────┐
│  RealizationInputContract (ADR-035)          │
│  - Immutable typed contract                  │
│  - Explicit target language, act, polarity   │
│  - Semantic role bindings & forbidden tokens │
└──────────────────────┬───────────────────────┘
                       │
                       ▼
┌──────────────────────────────────────────────┐
│  Stage S11: PromptAssembler                  │
│  - Compiles instructions strictly from       │
│    RealizationInputContract                  │
└──────────────────────┬───────────────────────┘
                       │
                       ▼
┌──────────────────────────────────────────────┐
│  Stage S12: Local Edge SLM (GGUF on CUDA)    │
│  - Untrusted text renderer                   │
└──────────────────────┬───────────────────────┘
                       │
                       ▼
┌──────────────────────────────────────────────┐
│  Stage S14: SemanticFidelityGate             │
│  - Deterministic regex & constraint checks   │
│  - Enforces honorifics, polarity, concepts   │
│  - Drops introspective ego-talk regexes      │
└──────────────────────┬───────────────────────┘
                       │
                       ▼
┌──────────────────────────────────────────────┐
│  Stage S15: Verified Actuation               │
└──────────────────────────────────────────────┘
```

---

## 2. Safe Architectural Insertion Boundary Analysis

### Q1: Should endogenous reasoning occur before CAPS?
**YES.**  
Endogenous candidate generation and reason formation MUST occur upstream of CAPS (between Stage S9 and Stage S10).
- Reason: CAPS was designed in Phase 23 as the *Communicative Act & Proposition Selection* compiler. It translates cognitive goals into a `CAPSResult`.
- If endogenous candidates are generated before CAPS, CAPS does not need to be rewritten; it simply receives candidate goals as part of its cognitive snapshot.

### Q2: Should CAPS consume candidates?
**YES.**  
`CognitiveStateSnapshot` in `caps.py` already contains fields designed to receive an active candidate:
```python
candidate_predicate: Optional[str] = None
candidate_subject: Optional[str] = None
candidate_object: Optional[str] = None
active_goal_id: Optional[str] = None
```
Currently, `CognitiveOrchestrator` merely populates these fields by taking `known_propositions[0]` from user-text retrieval. If an upstream Reason Formation engine populates these fields from an authorized endogenous candidate, CAPS can process it using its existing fail-closed Priority 5 grounding logic.

### Q3: Should `CommunicativeIntent` / `CAPSResult` remain downstream?
**YES.**  
`CAPSResult` and `RealizationInputContract` must remain strictly downstream of candidate generation and authorization.
- The realization pipeline must never decide *why* to communicate or *whether* to communicate now.
- It only receives the authorized communicative obligation.

### Q4: Can autonomous communication reuse P23-D?
**YES, 100%.**  
Once an endogenous candidate is authorized and compiled by CAPS into a `RealizationInputContract`, the entire downstream realization pipeline (Stage S11 PromptAssembler, Stage S12 Local SLM, Stage S14 SemanticFidelityGate) can be reused without a single line of modification.
- S14 SemanticFidelityGate will automatically protect against ego-hallucinations (*"As an AI, I feel..."*).
- Realization will respect speaker/addressee honorifics (`em/anh` in Vietnamese).
- Zero cloud dependencies are introduced.

### Q5: Where must Turn Authorization occur?
**BEFORE CAPS AND BEFORE INFERENCE.**  
Turn Authorization (the decision whether to `ALLOW`, `MERGE`, `DEFER`, `SUPPRESS`, or `SILENCE`) MUST execute *before* calling `RealizationInputContract` or the SLM.
- If authorization decides `SILENCE`, `DEFER`, or `SUPPRESS`, execution halts immediately.
- Zero GPU compute or SLM tokens are consumed.
- This preserves the 20-Watt Whole Brain Architecture constraint.

### Q6: Can autonomous communication bypass the user-input pathway?
**YES, but it requires an explicit entry point in `CognitiveOrchestrator`.**  
Currently, `CognitiveOrchestrator.process()` begins with:
```python
def process(self, input_text: str, ...)
```
Autonomous communication requires an asynchronous background entry point (e.g. `process_endogenous_turn(candidate: CommunicativeCandidate)` or a background tick listener). This entry point must feed directly into Stage S10b, completely bypassing Stage S1 (`PerceptionLexicalEncoder`).

### Q7: What must remain strictly unchanged?
1. `src/core/language/contract.py` (`RealizationInputContract`).
2. `src/core/language/gate.py` (`SemanticFidelityGate` / S14).
3. `src/core/orchestrator/prompt_assembler.py` (`PromptAssembler` / S11).
4. `src/core/inference/engine.py` (Local GGUF SLM execution).
5. All Genesis gate safeguards (`data/profile.json`).

---

## 3. P23-D Architectural Compatibility Verdict

| Requirement | Compatible? | Notes |
|---|:---:|---|
| **Downstream Pipeline Reuse** | **YES** | S11, S12, S14 can be reused 100% as-is. |
| **Fail-Closed Grounding Enforcement** | **YES** | CAPS Priority 5 already refuses ungrounded candidate predicates. |
| **20-Watt Compute Budget** | **YES** | Pre-inference authorization guarantees 0 tokens for silence/deferral. |
| **Upstream Substrate Coupling** | **BLOCKED** | Upstream substrates currently do not provide the required grounded candidates. |

**Conclusion**: The P23-D realization boundary is fully compatible with Endogenous Communication. The bottleneck is 100% upstream (the lack of a Reason Formation Substrate).
