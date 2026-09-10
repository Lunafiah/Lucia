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

## 6. Status & Implementation Staging

- **Maturity Level in Repository**: `SPECIFICATION & RESEARCH HARNESS ONLY`.
- **Production Integration**: Deferred to Phase 12 milestone after Phase 11 Affective Memory empirical coupling is resolved.
- **Evidence Label**: `HYPOTHESIS` / `ARCHITECTURAL BLUEPRINT`.
