# Phase 12 — Knowledge Learning Research Specification

> **Authoritative Specification: Memory vs. Knowledge Ontology, K0–K9 Knowledge Maturity Ladder, Provenance Architecture, and the LLM-as-Teacher Boundary**  
> **Status:** Active Research Specification (Phase 12 Track)  
> **Directory:** `docs/specs/lucia-phase12-Knowledge_Learning/KNOWLEDGE_LEARNING_SPEC.md`  
> **Authority Level:** Authoritative Specification

---

## 1. Executive Summary & Research Foundation

This specification formalizes the research architecture for **Phase 12 — Knowledge Learning**. In the Lucia companion architecture, Knowledge Learning represents a fundamental cognitive expansion beyond episodic memory:

```text
                    EXPERIENCE
                        │
          ┌─────────────┼─────────────┐
          ▼             ▼             ▼
   Affective Memory  Knowledge   Relationship
    / Recollection    Learning    Development
          │             │             │
          └─────────────┼─────────────┘
                        ▼
                    Cognition
```

### 1.1 Fundamental Ontological Distinction: Memory vs. Knowledge

```text
┌────────────────────────────────────────────────────────────────────────┐
│                        MEMORY vs. KNOWLEDGE                            │
├────────────────────────────────────────────────────────────────────────┤
│  EPISODIC MEMORY ("What happened?")                                    │
│    - Nature: Time-stamped, context-bound records of specific events.   │
│    - Storage: Kanerva Sparse Distributed Memory (SDM) + PAD tags.      │
│    - Retrieval: Ecphory resonance query keyed on current affect.       │
│    - Characteristic: Episodic, perceptual, transient, decaying.        │
├────────────────────────────────────────────────────────────────────────┤
│  CONCEPTUAL KNOWLEDGE ("What has Lucia learned from what happened?")   │
│    - Nature: Structured, reusable, generalized abstractions.           │
│    - Elements: Concepts, relations, propositions, rules, properties.   │
│    - Retrieval: Deductive, associative, relational, queryable.         │
│    - Characteristic: Semantic, compositional, persistent, verifiable.  │
└────────────────────────────────────────────────────────────────────────┘
```

> [!CAUTION]
> Storing conversational transcripts or LLM answers in a database is **not** Knowledge Learning. Knowledge requires explicit structured representations, confidence scores, provenance attribution, and the ability to derive new conclusions without repeating the original text.

---

## 2. The Critical LLM Boundary

The Small Language Model (LLM) is an external reasoning instrument, not Lucia's internal knowledge store:

```text
Experience / Question
        ↓
LLM Backend
        ↓
Candidate Explanation / Claim
        ↓
Structured Knowledge Extraction
        ↓
Consistency / Provenance Check
        ↓
Confidence Assignment
        ↓
Lucia Knowledge Store
```

### 2.1 Roles of the LLM vs. Roles of Lucia

| System | Permitted Roles | Forbidden Roles |
|---|---|---|
| **LLM Backend** | • Teacher / Explanatory instrument<br>• Candidate hypothesis generator<br>• Natural language parsing interface<br>• Scaffolding assistant | • Lucia's ground-truth memory<br>• Lucia's knowledge repository<br>• Autonomous decision authority |
| **Lucia Knowledge Engine** | • Explicit concept & proposition storage<br>• Provenance & evidence tracking<br>• Neuro-symbolic & relational derivation<br>• Contradiction detection & belief revision | • Unquestioned acceptance of LLM output<br>• Opaque black-box memorization |

### 2.2 The Epistemic Inequality

$$\text{LLM Output} \neq \text{Lucia's Knowledge}$$
$$\text{Correct Answer} \neq \text{Internal Understanding}$$
$$\text{Memory Retrieval} \neq \text{Learning}$$

---

## 3. The K0–K9 Knowledge Maturity Ladder

To rigorously benchmark knowledge capabilities without circular reasoning, Lucia evaluates learning across ten distinct maturity gates:

```text
K0: EXPOSURE
    └── System is exposed to input data; no retention claim.
K1: MEMORIZATION
    └── Literal reproduction of a stated fact on identical cue.
K2: RETRIEVAL
    └── Independent retrieval of the proposition from a dedicated store.
K3: STRUCTURED REPRESENTATION
    └── Proposition decomposed into explicit Concept-Relation-Value tuples.
K4: ASSOCIATION
    └── Structured link formed between concepts (e.g. addition ↔ arithmetic).
K5: GENERALIZATION
    └── Abstraction of a general rule across multiple distinct observations.
K6: DEDUCTION / DERIVATION
    └── Derivation of a novel, unstated proposition from existing knowledge.
K7: TRANSFER
    └── Application of the learned rule to an isomorphic, previously unseen domain.
K8: REVISION
    └── Detection of contradiction; lowering confidence or marking conflicting claims.
K9: SYNTHESIS
    └── Merging multiple domain models into a novel higher-order cognitive model.
```

---

## 4. Structured Knowledge Schema

Every unit of knowledge in Lucia consists of explicit, verifiable data structures:

### 4.1 Concept
- `concept_id`: Unique identifier (e.g. `concept:addition`).
- `name`: Human-readable label.
- `domain`: Academic or operational domain (e.g. `mathematics.arithmetic`).
- `definition`: Formal or operational specification.
- `relations`: Map of typed edges to other concepts.

### 4.2 Proposition
- `proposition_id`: Unique identifier.
- `subject`: Source concept or entity.
- `predicate`: Relation or property (e.g. `equals`, `greater_than`, `causes`).
- `object`: Target concept, value, or state.
- `confidence`: Calibrated float $\in [0.0, 1.0]$.
- `provenance`: Detailed attribution metadata.

### 4.3 Provenance Taxonomy

Every proposition must record its origin:

```text
USER_STATED   — Stated directly by the user during interaction.
LLM_PROPOSED  — Generated by the language model; unverified candidate.
OBSERVED      — Sensed directly from system or environment telemetry.
INFERRED      — Inferred via probabilistic or associative reasoning.
DERIVED       — Formally deduced via rule-based symbolic derivation.
VERIFIED      — Confirmed through external ground truth or proof.
UNCERTAIN     — Insufficient evidence or conflicting support.
CONTRADICTED  — Refuted by counterexample or conflicting verified fact.
```

---

## 5. Bounded Academic Domains for Initial Research

To prevent confounding, initial Knowledge Learning experiments are restricted to domains with indisputable ground truth:

1. **Integer Arithmetic**:
   - Concepts: `Number`, `Addition`, `Equality`, `Successor`.
   - Facts: $2 + 2 = 4$, $3 + 2 = 5$.
   - Test: Can Lucia derive $4 + 2 = 6$ via successive application of rules without querying the LLM?
2. **Propositional Logic**:
   - Concepts: `Implication`, `ModusPonens`, `Negation`.
   - Facts: $P \implies Q$, $P$ is true.
   - Test: Can Lucia deduce $Q$ and record the proof step in provenance?

---

## 6. Phase 12 Empirical Experiments (K-EXP-1 to K-EXP-12)

The dedicated test harness `tests/unit/test_knowledge_learning.py` benchmarks the Knowledge Learning subsystem across 12 empirical experiments:

| Experiment | Target Capability | Empirical Result & Invariant Verified | Evidence Status |
|---|---|---|:---:|
| **K-EXP-1** | Structured Storage | Verified storage and exact-match retrieval of propositions and concepts by key. | `IMPLEMENTED & TESTED` |
| **K-EXP-2** | Provenance Tracking | Validated differentiation of all 8 provenance types and antecedent evidence tracking. | `IMPLEMENTED & TESTED` |
| **K-EXP-3** | Retrieval Without LLM | Pure symbolic query execution on `(Subject, Predicate, Object)` without LLM participation. | `CAUSALLY SUPPORTED` |
| **K-EXP-4** | Structured Representation | Represented relational knowledge as typed tuples and graph edges rather than raw text. | `IMPLEMENTED & TESTED` |
| **K-EXP-5** | Association | Navigated multi-hop relational chains (Canary $\to$ Bird $\to$ Animal) without LLM. | `IMPLEMENTED & TESTED` |
| **K-EXP-6** | Deterministic Derivation | Deduced novel proposition ($4 + 2 = 6$) from Peano addition rules and transitive relations ($A \to C$). | `CAUSALLY SUPPORTED` |
| **K-EXP-7** | LLM Boundary Distinction | Distinguished Lucia stored knowledge from external LLM parametric memory. | `CAUSALLY SUPPORTED` |
| **K-EXP-8** | Generalization | Applied learned successor rule to novel unseen integers ($10 + 2 = 12$). | `OBSERVED & TESTED` |
| **K-EXP-9** | Contradiction Representation | Detected conflicting assertions on single-valued predicates (`Earth spherical` vs `Earth flat`). | `IMPLEMENTED & TESTED` |
| **K-EXP-10**| Non-Destructive Revision | Invalidated obsolete belief (`Pluto planet`), preserved history, and linked new verified fact. | `CAUSALLY SUPPORTED` |
| **K-EXP-11**| Four-Condition Ablation | Benchmarked Conditions A (LLM only), B (Store lookup), C (Store + Derivation), D (Store + LLM). | `CAUSALLY SUPPORTED` |
| **K-EXP-12**| Persistence Round-Trip | Exported knowledge graph to JSON and reconstructed full graph with zero data loss. | `TESTED` |

---

## 7. Knowledge Maturity Evaluation (K0–K9)

Based on empirical evidence from the Phase 12 research harness:

| Level | Maturity Gate | Current Status | Empirical Basis |
|---|---|:---:|---|
| **K0** | Exposure | **ACHIEVED** | System ingests propositions and concepts. |
| **K1** | Memorization | **ACHIEVED** | Literal storage and recall of facts ($2 + 2 = 4$). |
| **K2** | Retrieval | **ACHIEVED** | Independent symbolic retrieval without LLM involvement. |
| **K3** | Structured Representation | **ACHIEVED** | Explicit `(Subject, Predicate, Object)` tuples with confidence and provenance. |
| **K4** | Association | **ACHIEVED** | Multi-hop conceptual graph traversal (`is_a`, `located_in`). |
| **K5** | Generalization | **ACHIEVED (Narrow)** | Peano addition rule generalized to novel integers ($10 + 2 = 12$). |
| **K6** | Deduction / Derivation | **ACHIEVED (Narrow)** | Transitive relation deduction and arithmetic deduction without LLM. |
| **K7** | Transfer | **OPEN RESEARCH** | Cross-domain structural transfer unvalidated. |
| **K8** | Knowledge Revision | **ACHIEVED (Local)** | Non-destructive revision with audit log and provenance invalidation. |
| **K9** | Knowledge Synthesis | **OPEN RESEARCH** | Higher-order hypothesis synthesis from disparate domains unvalidated. |

---

## 8. Production Promotion Gate Evaluation

Promotion of the Knowledge Learning subsystem into canonical Lucia cognition requires satisfying all 12 criteria:

| # | Promotion Criterion | Evaluation Result | Gate Status |
|---|---|:---:|:---:|
| **1** | Independent Storage | **PASS** (`KnowledgeStore` operates independently of LLM and SDM) | PASS |
| **2** | Retrieval Without LLM | **PASS** (Pure symbolic query verified in K-EXP-3) | PASS |
| **3** | Provenance Tracking | **PASS** (8 provenance types verified in K-EXP-2) | PASS |
| **4** | Structured Representation | **PASS** (Explicit tuples and concept graphs verified in K-EXP-4) | PASS |
| **5** | Deterministic Derivation | **PASS** (Peano and transitivity rules verified in K-EXP-6) | PASS |
| **6** | LLM Ablation Verification | **PASS** (Conditions A–D clearly differentiated in K-EXP-11) | PASS |
| **7** | Generalization | **PARTIAL** (Demonstrated on narrow arithmetic; broad generalization open) | **RESEARCH ONLY** |
| **8** | Contradiction Handling | **PASS** (Conflict detection verified in K-EXP-9) | PASS |
| **9** | Non-Destructive Revision | **PASS** (History preserved verified in K-EXP-10) | PASS |
| **10**| Persistence Round-Trip | **PASS** (JSON serialization verified in K-EXP-12) | PASS |
| **11**| Reproducibility & Stability | **PASS** (Deterministic execution in `test_knowledge_learning.py`) | PASS |
| **12**| Canonical Architecture Integration | **UNTESTED / DEFERRED** (No wiring into `CognitiveOrchestrator`) | **BLOCKING** |

---

## 9. Status & Definitive Decision

$$\Large\mathbf{PHASE\ 12\ RESEARCH\ CONTINUES}$$
$$\mathbf{Production\ Baseline:\ Unaltered\ Canonical\ Cognition}$$

* **Production Boundary**: The Knowledge Learning subsystem remains strictly isolated within `tests/unit/test_knowledge_learning.py`.
* **Zero Production Mutation**: No files in `src/core/` are modified. Canonical `CognitiveOrchestrator`, `EmotionCore`, and `PromptAssembler` remain untouched.
* **No Promotion ADR**: As Criterion 12 (Canonical Architecture Integration) is deferred and general transfer (K7, K9) remains open, no promotion ADR is authored.

