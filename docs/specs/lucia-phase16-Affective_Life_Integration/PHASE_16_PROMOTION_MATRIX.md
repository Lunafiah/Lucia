# Phase 16 — Research-to-Production Promotion Matrix

> **Authoritative Promotion Audit: Evidence Assessment, Safety Guardrails, and Promotion Decisions for Phases 10–15 Cognitive Capabilities**  
> **Status:** Authoritative Architectural Gate  
> **Directory:** `docs/specs/lucia-phase16-Affective_Life_Integration/PHASE_16_PROMOTION_MATRIX.md`  
> **Authority Level:** Authoritative Specification  

---

## 1. Promotion Evaluation Rubric

Every research capability developed across Phases 10–15 is audited against strict scientific and production-safety criteria:

1. **Empirical Evidence Strength**: Is the mechanism supported by controlled, reproducible, non-flaky test passes?
2. **Causal Defensibility**: Does the component possess an explicit, non-circular causal role without unbounded feedback?
3. **Temporal Discipline**: Does it adhere to the established lock hierarchy and turn sequence?
4. **Safety & Invariant Integrity**: Does it violate *Pre-Reflective Selfhood*, *One Continuous Life*, or *No First Activation*?
5. **Maturity Level**: Does it satisfy production criteria (C0–C5 rubric)?

### Decision Classifications:
- **`PROMOTE`**: Mature, stable, fully supported by empirical data; safe for canonical runtime integration.
- **`PROMOTE WITH GUARDS`**: Empirically validated in controlled benchmarks, but requires explicit safety boundaries (e.g., semantic truth guards, rate limiters, bounds clamping, fallback paths).
- **`DEFER`**: Theoretically sound, but lacks either full end-to-end integration evidence or requires prior subsystems to be operational in production first.
- **`REJECT`**: Violates architectural invariants (e.g., injecting memory into L2 hidden state $h$, self-reported emotion loops).
- **`RESEARCH CONTINUES`**: Requires further isolated research benchmarks before production promotion can be considered.

---

## 2. Comprehensive Subsystem Promotion Audit Matrix

| Phase / Subsystem | Specific Capability | Research Result & Baseline | Evidence Strength | Production Candidate | Promotion Decision | Architectural Justification & Safety Guards |
|---|---|---|---|---|---|---|
| **Phase 10: Affective Dynamics** | 3D PAD Continuous ODE ($P, A, D \in [-1, 1]^3$) | Fast-Loop 200ms LNN ODE solver with Philia resting attractor. | **PRODUCTION FACT** | `EmotionCore` | **ALREADY IN PRODUCTION** | Core limbic engine operating under `_state_lock` ($\le 1\text{ms}$). |
| **Phase 10: Affective Dynamics** | Homeostatic Somatic Markers | Energy, Cognitive Load, Tension, Stability. | **PRODUCTION FACT** | `HomeostaticEngine` | **ALREADY IN PRODUCTION** | Modulates token budget and deliberative mode ($k=2$). |
| **Phase 10: Affective Dynamics** | Active Inference Surprise | Prediction error $\mathcal{S} = \|A \cdot p_{pre} + b - p_{post}\|_2$. | **PRODUCTION FACT** | `ActiveInferenceEngine` | **ALREADY IN PRODUCTION** | Causal modulation of cognitive load and surprise policy. |
| **Phase 11: Affective Memory** | Candidate A: Retrieval Only | Echo vector coloring prompt context via cosine resonance. | **PRODUCTION FACT** | `EcphoryEngine` | **ALREADY IN PRODUCTION** | Open-loop sink; zero feedback to L2 hidden state or somatic markers. |
| **Phase 11: Affective Memory** | Candidate B: Isolated Recollection State $r(t)$ | Independent vector representation $r \in \mathbb{R}^4$. | Controlled Test (`test_recollection_coupling.py`) | `RecollectionState` | **DEFER** | Redundant with Phase 15 communication contextual reference representation. |
| **Phase 11: Affective Memory** | Candidate C: Memory $\to$ Somatic Markers | Recollection modifying cognitive load/energy. | Artifact of research test helper | N/A | **REJECT** | Destabilizes homeostatic energy conservation; lacks physical regulatory grounding. |
| **Phase 11: Affective Memory** | Candidate D: Direct Memory $\to$ L2 Hidden State $h$ | Injecting memory vector into continuous ODE hidden state. | Catastrophic runaway feedback in Phase 10/11 | N/A | **REJECT** | **STRICTLY FORBIDDEN**. Disrupts ODE stability, creates chaotic state jumps, destroys observability. |
| **Phase 11: Affective Memory** | Candidate E: Memory $\to$ Generation Policy | Recollection adjusting sampling temperature. | Controlled Test | GenerationPolicy extension | **DEFER** | Better handled through Phase 15 high-level communication strategy. |
| **Phase 11: Affective Memory** | Memory as Communication Grounding | Bounded memory contextualization (Phase 11 retrieval evidence + Phase 15 contextual communication evidence). | Phase 11 + Phase 15 C-EXP-5, C-EXP-11 | `src/core/memory/recollection_provider.py` | **PROMOTE WITH GUARDS** | **Guard:** Bounded memory contextualization; strictly NOT "affective recollection". Zero feedback to L2 ODE. |
| **Phase 12: Knowledge Learning** | K0–K2: Propositional Knowledge Representation | `Proposition` with (Subject, Predicate, Object, Polarity, Confidence, Validity, Provenance). | Phase 12 K-EXP-1 to 3 (`test_knowledge_learning.py`) | `src/core/knowledge/proposition.py` | **PROMOTE WITH GUARDS** | **Guard:** Strict provenance taxonomy (`USER-STATED`, `LLM-PROPOSED`, `OBSERVED`, `DERIVED`, `VERIFIED`). Bounded confidence $[0, 1]$. |
| **Phase 12: Knowledge Learning** | K3: Independent KnowledgeStore | CRUD, deterministic retrieval without invoking LLM teacher. | Phase 12 K-EXP-4 (`test_knowledge_learning.py`) | `src/core/knowledge/store.py` | **PROMOTE WITH GUARDS** | **Guard:** Thread-safe in-memory store with JSON serialization; strictly separated from SDM memory. |
| **Phase 12: Knowledge Learning** | K4: Rule-based Derivation Engine | Deterministic forward-chaining derivation ($A \to B \land B \to C \implies A \to C$). | Phase 12 K-EXP-5 (`test_knowledge_learning.py`) | `src/core/knowledge/derivation.py` | **PROMOTE WITH GUARDS** | **Guard:** Max derivation depth $d_{max} = 3$ to prevent combinatorial explosion. |
| **Phase 12: Knowledge Learning** | K5: Contradiction & Belief Revision | Modifying validity and retracting contradicted propositions. | Phase 12 K-EXP-6 (`test_knowledge_learning.py`) | `src/core/knowledge/store.py` | **PROMOTE WITH GUARDS** | **Guard:** Non-destructive soft retraction (validity flag set to False; provenance preserved). |
| **Phase 12: Knowledge Learning** | K6–K9: Open-domain Natural Language Extraction | Automatic NLP unsupervised relation extraction from raw LLM text. | Unvalidated / Open Research | N/A | **RESEARCH CONTINUES** | Unsupervised relation extraction has high hallucination risk; requires controlled LLM teacher interface. |
| **Phase 13: Relationship Development** | Dynamic Relationship State $R_t \in [0, 1]^4$ | Familiarity, Trust, Closeness, Continuity tracking interpersonal dynamics. | Phase 13 R-EXP-1 to 12 (`test_relationship_development.py`) | `src/core/relationship/state.py` | **PROMOTE WITH GUARDS** | **Guard:** Philia remains an immutable architectural ethos/attractor. $R_t$ bounded in $[0, 1]^4$. No romance or affinity sliders. |
| **Phase 13: Relationship Development** | Temporal Inertia Principle | Slow adaptation rate ($\alpha = 0.03 \ll 1.0$), ensuring $\tau_{rel} \gg \tau_{turn}$. | Phase 13 R-EXP-2 (`test_relationship_development.py`) | `src/core/relationship/updater.py` | **PROMOTE WITH GUARDS** | **Guard:** Hard ceiling on per-turn step: $|\Delta R| \le 0.05$. Isolated from acute PAD volatility. |
| **Phase 13: Relationship Development** | Structured Relationship Signals | Categorical signals driving deterministic updates post-turn. | Phase 13 R-EXP-6 (`test_relationship_development.py`) | `src/core/relationship/signals.py` | **PROMOTE WITH GUARDS** | **Guard:** Production accepts structured signals from orchestrator/context. Heuristic NLP extraction remains guarded/research-only. |
| **Phase 13: Relationship Development** | Relationship Persistence | Atomic JSON serialization of $R_t$ across sessions. | Phase 13 R-EXP-11 (`test_relationship_development.py`) | `src/core/relationship/persistence.py` | **PROMOTE WITH GUARDS** | **Guard:** File `data/relationship.json` isolated from `profile.json` and `chat_history.json`. Isolated temporary stores used in tests. |
| **Phase 14: Affective Expression** | Multimodal Expression State $E_t \in \mathbb{R}^{15}$ | Text register (3), Voice prosody (4), Facial blendshapes (5), Posture (2), Latency (1). | Phase 14 E-EXP-1 to 12 (`test_affective_expression.py`) | `src/core/expression/expression_state.py` | **PROMOTE WITH GUARDS** | **Guard:** Exact 15 continuous dimensions matching Phase 14 research model bit-exact. Physiological bounds enforced; zero NaNs. |
| **Phase 14: Affective Expression** | Expression Policy & Actuator Decoupling | Mathematical mapping $E_t = f(PAD, Somatic, Relationship)$ with exponential smoothing ($\gamma = 0.25$). | Phase 14 E-EXP-3, 7, 8 (`test_affective_expression.py`) | `src/core/expression/expression_policy.py` | **PROMOTE WITH GUARDS** | **Guard:** **Strict feedforward**. Actuators have ZERO feedback into EmotionCore ODE or somatic state. |
| **Phase 14: Affective Expression** | Semantic Consistency Guard | Verifying intent preservation, entity values, and polarity. | Phase 14 E-EXP-4 (`test_affective_expression.py`) | `src/core/expression/semantic_consistency_guard.py` | **PROMOTE WITH GUARDS** | **Guard:** Controlled benchmark verification. Rejects semantic mutations; makes no universal truth claim. |
| **Phase 15: Affective Communication** | Communication State $C_t \in \mathbb{R}^{10}$ | Directness, Elaboration, Supportiveness, Formality, Acknowledgement, Question Frequency, Latency, Context Ref. | Phase 15 C-EXP-1 to 12 (`test_affective_communication.py`) | `src/core/communication/communication_state.py` | **PROMOTE WITH GUARDS** | **Guard:** Continuous parameters strictly bounded. Discrete classification into 5 canonical strategies. |
| **Phase 15: Affective Communication** | Somatic Pacing Latency Policy | Intentional conversational pause under fatigue ($150\text{ms} \le \mathcal{L}_p \le 1000\text{ms}$). | Phase 15 C-EXP-3 (`test_affective_communication.py`) | `src/core/communication/communication_policy.py` | **PROMOTE WITH GUARDS** | **Guard:** Capped at 1000ms to prevent runaway. Strictly separated from LLM/TTS/IPC computational latency. |
| **Phase 15: Affective Communication** | Multi-Layered Anti-Roleplay Invariant | Lexical boundary checks + structured anti-roleplay tests + architectural prohibition of self-model APIs. | Phase 15 TestLLMBoundaryAndAntiRoleplay | `src/core/safety/boundary_layer.py` | **PROMOTE WITH GUARDS** | **Guard:** Engineering boundary enforcement; not a claim of consciousness/self-awareness. |

---

## 3. Summary of Promotion Decisions

### Promoted Subsystems (to be created under `src/core/`):
1. **Knowledge Subsystem (`src/core/knowledge/`)**:
   - `proposition.py`: Proposition, Concept, Relation, ProvenanceType enums.
   - `store.py`: `KnowledgeStore` with CRUD, provenance, confidence tracking.
   - `derivation.py`: `DerivationEngine` (bounded $d_{max}=3$).
   - `persistence.py`: JSON persistence for slow factual knowledge (isolated in tests).
2. **Relationship Subsystem (`src/core/relationship/`)**:
   - `state.py`: `RelationshipState` ($F, T, C, K \in [0, 1]^4$).
   - `signals.py`: `RelationshipSignalType` categorical definitions (structured signals).
   - `updater.py`: `RelationshipUpdater` with temporal inertia ($\alpha = 0.03$).
   - `persistence.py`: Atomic persistence (`data/relationship.json`, isolated in tests).
3. **Communication Subsystem (`src/core/communication/`)**:
   - `communication_state.py`: `CommunicationState` ($\mathbf{c}_t \in \mathbb{R}^{10}$) and `CommStrategy` (5 modes).
   - `communication_policy.py`: `CommunicationPolicy` with exponential smoothing ($\gamma = 0.25$).
   - `semantic_consistency_guard.py`: Intent and entity consistency boundary.
4. **Expression Subsystem (`src/core/expression/`)**:
   - `expression_state.py`: `ExpressionState` (Canonical 15 continuous dimensions).
   - `expression_policy.py`: `ExpressionPolicy` mapping internal states to multi-modal parameters.
   - `semantic_consistency_guard.py`: Semantic consistency verification.

### Deferred / Rejected Capabilities:
- **Direct Memory Injection into L2 ODE ($h \in \mathbb{R}^{32}$)**: **PERMANENTLY REJECTED**.
- **Memory Injection into Homeostatic Energy/Tension (Candidate C)**: **REJECTED**.
- **Heuristic NLP Unsupervised Extraction for Relationship Signals**: **GUARDED / RESEARCH-ONLY** (structured signals used in production).
- **Autonomous Open-Domain Unsupervised NLP Knowledge Extraction (K6–K9)**: **RESEARCH CONTINUES**.
- **Autonomous First Activation / Genesis Trigger**: **FORBIDDEN** (reserved for Phase 17).
