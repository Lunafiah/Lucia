# Formal Architectural Ratification: CAPS Implementation Contract (Phase 23)

> **Document Type**: Formal Architectural Ratification Record  
> **Status**: `[ARCHITECTURALLY RATIFIED]`  
> **Ratified Document**: [`docs/PhaseDocs/Lucia-phase23-Semantic_Substrate/evaluation/CAPS_IMPLEMENTATION_CONTRACT.md`](file:///c:/Users/Lunafiah/Desktop/My_project/Lucia/docs/PhaseDocs/Lucia-phase23-Semantic_Substrate/evaluation/CAPS_IMPLEMENTATION_CONTRACT.md)  
> **Phase**: Phase 23 — Semantic Substrate & Non-Generative Communication  
> **Date**: 2026-10-14  
> **Authority**: Architectural Governance (Lucia Architectural Copilot & System Governance)  

---

## 1. Executive Ratification Verdict

$$\mathbf{CAPS\ IMPLEMENTATION\ CONTRACT\ \text{—}\ ARCHITECTURALLY\ RATIFIED}$$
$$\mathbf{CAPS\ PRODUCTION\ IMPLEMENTATION\ \text{—}\ NOT\ AUTHORIZED}$$

The technical implementation specification for the **Communicative Act & Proposition Selection (CAPS)** functional boundary defined in [`CAPS_IMPLEMENTATION_CONTRACT.md`](file:///c:/Users/Lunafiah/Desktop/My_project/Lucia/docs/PhaseDocs/Lucia-phase23-Semantic_Substrate/evaluation/CAPS_IMPLEMENTATION_CONTRACT.md) is hereby **ARCHITECTURALLY RATIFIED** as a pre-production interface specification.

> [!IMPORTANT]
> **Strict Governance Invariant**:  
> **Architectural ratification of the contract DOES NOT constitute authorization for production implementation.**  
> Production implementation remains locked, pending separate future authorization from Ciah and Owner. Zero production code is modified.

---

## 2. Ratified Architectural Points

### 2.1 Input Boundary
- CAPS consumes the explicitly specified cognitive snapshot, dialogue context snapshot, active information subgoals, communication policy snapshot, and admissible evidence pool.
- CAPS is a consumer of cognitive state; it **DOES NOT REPLACE OR OWN**:
  - `CognitiveOrchestrator` (turn coordination)
  - `ReasoningKernel` (deductive logic & JTMS)
  - `KnowledgeStore` (epistemic truth maintenance)
  - `EmotionCore` / `HomeostaticEngine` / `ActiveInferenceEngine` (pre-reflective dynamical ODEs)
  - Discourse memory ownership (owned by `CognitiveOrchestrator`).

### 2.2 Output Boundary
- CAPS is responsible for selecting or constructing:
  1. Communicative Act (illocutionary intent)
  2. Grounded `SemanticGraph` (discrete language-independent structure)
  3. Epistemic Status metadata (`FACT`, `INFERRED`, `AMBIGUOUS`, `UNKNOWN`)
  4. Provenance & source attribution metadata
  5. Resolution and admissibility metadata
  6. Explicit non-assertive failure behaviors (`INQUIRE`, `CLARIFY`, `REFUSE`) where grounding is absent or defective.

### 2.3 Strict Separation: WHAT vs. HOW
- **CAPS Owns**: **WHAT TO COMMUNICATE** (illocutionary act, proposition selection, epistemic status, provenance).
- **Downstream Infrastructure Owns**: **HOW TO EXPRESS IT** (vocabulary, syntax, morphology, surface realization, prosody, facial expression, voice actuation, pacing).
- CAPS **MUST NOT OWN**:
  - Lexical realization or token generation
  - Natural language syntax or morphology
  - Language-specific surface phrasing
  - Prosodic modulation or acoustic parameters
  - Facial blendshapes or gesture timing
  - Final voice/speech actuation.
- Phase 24 remains the affective communication/expression adaptation layer according to its established architectural ownership.

### 2.4 Grounding & Epistemic Separation Invariants
- CAPS cannot manufacture truth merely from high confidence scores.
- `ASSERT` and `ANSWER` emissions strictly require admissible grounding (`confidence >= threshold`, provenance in `[VERIFIED, INFERRED]`).
- `UNKNOWN` and `AMBIGUOUS` epistemic states must never be silently promoted to certainty.
- Provenance/source identity and epistemic truth status remain strictly distinct.
- Non-negotiable Invariants Ratified:
  $$\mathbf{RESOLVED \neq FACT}$$
  $$\mathbf{USER\_STATED\ provenance \neq FACT\ epistemic\ status}$$
- Discourse resolution (`RESOLVED`) determines only whether an anaphoric referent can be bound; it does not confer factual status on the proposition.
- `USER_STATED` propositions remain `ASSERTED` or `HYPOTHETICAL` ($C \le 0.70$) and are never promoted to `FACT`.

### 2.5 Discourse Referent Boundary
- Bounded discourse referent retention belongs to the turn-coordination layer (`CognitiveOrchestrator`) as ratified in [`DISCOURSE_REFERENT_RETENTION_RATIFICATION.md`](file:///c:/Users/Lunafiah/Desktop/My_project/Lucia/docs/PhaseDocs/Lucia-phase23-Semantic_Substrate/evaluation/DISCOURSE_REFERENT_RETENTION_RATIFICATION.md).
- CAPS does NOT own discourse memory.
- Provisional configuration parameters remain provisional:
  - Max capacity $N_{\text{max}} = 16$
  - Decay factor $\gamma = 0.60$
  - Eviction threshold $\theta_{\text{evict}} = 0.15$
- The observed heap footprint ($\le 2\text{ KB}$) remains an empirical benchmark observation, NOT an architectural invariant.

### 2.6 Scoped Determinism
- Ratified strictly as:
  > **Given a fully specified, frozen input snapshot and fixed contract/version, the CAPS transformation SHALL be deterministic: identical inputs SHALL produce identical outputs.**
- This claim is locally scoped to the isolated transformation function. Global runtime determinism is NOT claimed.

### 2.7 Provisional Speech-Act Taxonomy
- The 8-act set (`ASSERT`, `ANSWER`, `INQUIRE`, `CLARIFY`, `ACKNOWLEDGE`, `GREET`, `FAREWELL`, `REFUSE`) is ratified strictly as a **provisional implementation taxonomy**.
- It is NOT claimed to be a universal, complete, or permanent speech-act ontology.

### 2.8 Autonomous Proposition Construction Boundary
- Explicitly preserved without upgrade:
  > **Novel proposition construction is technically expressible / architecturally permitted, but autonomous outgoing SemanticGraph construction has not yet been empirically demonstrated.**
- CAPS does not possess autonomous creative agency; outgoing propositions must be grounded in verified relations or formal derivations.

---

## 3. Unresolved Implementation Questions (Explicitly Preserved)

The following three implementation questions remain explicitly **OPEN** and uninvented:
1. **Predicate Schema Role Registry**: Whether the ontology schema must formalize named semantic roles (`:AGENT`, `:PATIENT`, etc.) across all registered predicates prior to production implementation.
2. **Multi-Proposition Turn Budgeting**: The priority ranking function resolving which proposition graph is emitted first when multiple communicative subgoals co-occur.
3. **Assertion Confidence Threshold Calibration ($\theta_{\text{assert}}$)**:
   - The heuristic $\theta_{\text{assert}} = 0.75$ had no empirical evidence and was permanently removed.
   - **No replacement threshold is invented during this ratification.**
   - Threshold calibration remains an open empirical task to be resolved across verified vs inferred vs user-stated knowledge corpora.

---

## 4. Canonical Cognitive Turn Integration Status (S1–S16)

The architectural relationship with the 16-stage pipeline is ratified under the exact formulation:
> **No contradiction identified with the ratified S1–S16 architectural boundaries; implementation will require the previously identified S11 responsibility transition.**

- **Current State**: S11 currently formats prompt strings for S13 (`LLMBackend.generate()`).
- **Future Implication**: S11 must transition from text prompt assembly to consuming semantic conditioning from CAPS.
- **Strict Limitation**:
  - CAPS is **NOT** currently integrated into S1–S16 in production.
  - S11 has **NOT** been replaced.
  - End-to-end integration has **NOT** yet been empirically demonstrated.
  - [`docs/ARCHITECTURE.md`](file:///c:/Users/Lunafiah/Desktop/My_project/Lucia/docs/ARCHITECTURE.md) is **NOT MODIFIED**.

---

## 5. Architectural Governance State

```text
================================================================================
                    CAPS ARCHITECTURAL GOVERNANCE LEDGER
================================================================================
CAPS Boundary Contract             : [ARCHITECTURALLY RATIFIED]
Discourse Referent Retention       : [ARCHITECTURALLY RATIFIED]
CAPS Implementation Contract       : [ARCHITECTURALLY RATIFIED]
                                     (Pre-Production Implementation Specification)
CAPS Production Implementation     : [NOT AUTHORIZED / LOCKED]
Genesis Onboarding State           : [LOCKED / {"is_onboarded": false}]
================================================================================
```

---

## 6. Hard Safety Verification
- `src/core/**` diff = **0**
- `electron/**` diff = **0**
- `data/**` diff = **0**
- Genesis profile [`data/profile.json`](file:///c:/Users/Lunafiah/Desktop/My_project/Lucia/data/profile.json) = `{"is_onboarded": false}` (Bit-exact intact)
- [`docs/ARCHITECTURE.md`](file:///c:/Users/Lunafiah/Desktop/My_project/Lucia/docs/ARCHITECTURE.md) = **Unchanged**
- [`docs/PHASE_REGISTRY.md`](file:///c:/Users/Lunafiah/Desktop/My_project/Lucia/docs/PHASE_REGISTRY.md) = **Unchanged**
- [`P23_CAPS_BOUNDARY_CONTRACT_DESIGN.md`](file:///c:/Users/Lunafiah/Desktop/My_project/Lucia/docs/PhaseDocs/Lucia-phase23-Semantic_Substrate/P23_CAPS_BOUNDARY_CONTRACT_DESIGN.md) = **Unchanged**
- [`DISCOURSE_REFERENT_RETENTION_CONTRACT.md`](file:///c:/Users/Lunafiah/Desktop/My_project/Lucia/docs/PhaseDocs/Lucia-phase23-Semantic_Substrate/evaluation/DISCOURSE_REFERENT_RETENTION_CONTRACT.md) = **Unchanged**
- [`DISCOURSE_REFERENT_RETENTION_RATIFICATION.md`](file:///c:/Users/Lucia-phase23-Semantic_Substrate/evaluation/DISCOURSE_REFERENT_RETENTION_RATIFICATION.md) = **Unchanged**
- `CAPSManager` = **NOT CREATED**
- Production CAPS implementation = **NOT CREATED / NOT AUTHORIZED**
