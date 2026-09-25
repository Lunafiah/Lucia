# Phase 23-D — EXP-02: Cross-Lingual Semantic Convergence Protocol

> **Experiment ID:** EXP-02  
> **Status:** `[EXPERIMENTAL PROTOCOL / AUDITED]`  
> **Governance Authority:** `AGENTS.md` §0, §6, §7; Phase 23-D Evaluation Scaffold  
> **Research Boundary:** Evaluation experiment only. No production runtime changes.

---

## 1. Experimental Objective

The objective of **EXP-02** is to determine whether parallel communicative expressions in **English (EN)**, **Japanese (JA)**, and **Vietnamese (VI)** can be transduced into semantic representations that achieve **functional equivalence**.

EXP-02 explicitly rejects graph isomorphism as an evaluation metric. Structural and topological variations (e.g. node counts, intermediate modifier edges, lexical tags) are permitted; the central evaluation criterion is whether representations derived from distinct languages yield identical answers to standardized semantic probes.

---

## 2. Experimental Separation of Layers

To prevent confounding substrate capability with parsing limitations, EXP-02 enforces strict architectural decoupling:

```text
Language Input (EN, JA, VI)
         │
         ▼
[LAYER B: Transduction Mode]
├── Mode A: Oracle Semantic Transduction (Gold fixtures -> Isolate substrate representation)
└── Mode B: Rule-Based Transduction (Deterministic rules -> Feasibility of edge non-LLM parsing)
         │
         ▼
[LAYER A: Candidate Substrate Execution]
├── Primary: UMR-TPG (Universal Meaning Representation on Typed Property Graph)
├── Secondary: V-UMR (Vector-Augmented Universal Meaning Representation)
└── Control: DRS-Graph (Discourse Representation Structure Box-Partition Graph)
         │
         ▼
[LAYER C: Functional Equivalence & Probe Query Execution]
└── Standardized Multilingual Probe Suite (Q1 through Q10)
         │
         ▼
Evaluation & Metric Computation (SQI, FEP, Layered Failure Partition)
```

### Result Attribution Discipline
Results are separately categorized into:
- **Layer A (Representation Capability):** Can the substrate preserve the required concepts and relations?
- **Layer B (Transduction Capability):** Did the transducer correctly map linguistic surface forms into semantic graph nodes/edges?
- **Layer C (Functional Equivalence):** Do the resulting graphs produce identical answers to queries across EN, JA, and VI?

---

## 3. Dataset Architecture & Linguistic Phenomena

The test corpus consists of 10 controlled, auditable parallel scenarios translated and aligned across EN, JA, and VI:

1. `simple_predicate_args`: Base transitive frame (*"Lucia solved the problem"*).
2. `zero_anaphora_omission`: Omitted arguments in JA/VI; requiring explicit resolution or `UNKNOWN/UNRESOLVED`.
3. `vietnamese_kinship_deixis`: Social deixis (*anh, chị, em, bác*) mapped to social relations distinct from identity.
4. `vietnamese_classifier`: Noun classifiers (*con, cái, quyển*) mapped to semantic sortals, not mistaken for ordinary concepts.
5. `japanese_aspect`: Aspectual morphology (*-te iru* progressive/stative, *-te shimatta* completive/regret).
6. `temporal_ordering`: Sequential and overlapping events (*"before", "after", "while"*).
7. `negation_scoping`: Direct event negation vs modal scope negation.
8. `modal_attribution`: Epistemic attribution and conceiver tracking (*"X believes Y"*).
9. `nested_proposition`: Multi-level proposition embedding.
10. `cross_sentence_reference`: Discourse entity continuity across adjacent sentences.

---

## 4. Language-Specific Processing Constraints

### Japanese (JA)
- **Zero-Anaphora Handling:** When an argument is dropped without surrounding discourse evidence, the representation must set the filler to **`UNKNOWN_ENTITY`** or **`UNRESOLVED`**. It is strictly forbidden to default omitted arguments to the speaker (*"I"*) without textual justification.
- **Postpositional Roles:** Case markers (*ga* -> `:ARG0`, *o* -> `:ARG1`, *ni* -> `:ARG2`/goal) are mapped into canonical semantic roles.

### Vietnamese (VI)
- **Social Deixis:** Honorifics and pronouns (*anh, chị, em*) are partitioned into:
  - `entity_identity`: The referent ID.
  - `social_relation`: Pragmatic metadata (e.g. `SENIOR_MALE`, `PEER_FEMALE`).
- **Classifiers:** Words like *con* (animate) or *cuốn/quyển* (book/volume) are treated as sortal/type constraints, avoiding spurious concept node pollution.

### English (EN)
- Functions as the overt argument reference baseline.

---

## 5. Evaluation Query Suite (Q1–Q10)

For every scenario, ten standardized semantic probes evaluate functional equivalence:
- **Q1 (Entity Identity):** Which discourse entities exist in the event universe?
- **Q2 (Predicate Identity):** What is the core predicate or action?
- **Q3 (Thematic Binding):** Which entity is bound to `:ARG0` and `:ARG1`?
- **Q4 (Temporal Ordering):** What is the temporal relation between events?
- **Q5 (Negation Scope):** Is the event affirmed, negated, or conditionally scoped?
- **Q6 (Modality & Conceiver):** Who is the epistemic conceiver / belief holder?
- **Q7 (Omitted Argument Resolution):** Is the omitted argument correctly resolved or marked `UNKNOWN`?
- **Q8 (Social / Pragmatic Relation):** What is the recorded social/pragmatic relation?
- **Q9 (Sortal / Classifier Constraint):** What type/sortal restriction is applied?
- **Q10 (Cross-Sentence Reference):** Does the entity link correctly across sentences?

---

## 6. Metrics & Falsification Criteria

### 6.1 Semantic Query Invariance (SQI)
$$\text{SQI}_{L_1 \leftrightarrow L_2} = \frac{\text{Queries with Identical Answers between } L_1 \text{ and } L_2}{\text{Total Queries Evaluated}}$$

$$\text{SQI}_{\text{overall}} = \frac{1}{3} \left(\text{SQI}_{\text{EN} \leftrightarrow \text{JA}} + \text{SQI}_{\text{EN} \leftrightarrow \text{VI}} + \text{SQI}_{\text{JA} \leftrightarrow \text{VI}}\right)$$

### 6.2 Functional Equivalence Parity (FEP)
$$\text{FEP} = \frac{\text{Queries where } \text{Ans}(EN) == \text{Ans}(JA) == \text{Ans}(VI)}{\text{Total Queries Evaluated}}$$

### 6.3 Concept Alignment
Evaluated via formal semantic schema overlap. If neural multilingual alignment tooling (XS2match) is not installed in the local environment, this metric is formally designated as **`[UNVERIFIED]`**.

### 6.4 Falsification Boundaries
- **Oracle Transduction Mode:** Falsification signal if $\text{SQI}_{\text{overall}} < 0.92$ or $\text{FEP} < 0.90$. Failure in Oracle mode proves representation inadequacy.
- **Rule-Based Transduction Mode:** Evaluates current deterministic pipeline capabilities. If rule-based mode achieves $\text{SQI} < 0.92$ while Oracle mode passes, this indicates a **transduction limitation**, not a substrate failure.
