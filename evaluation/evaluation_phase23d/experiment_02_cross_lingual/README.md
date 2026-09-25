# Experiment 02 — Cross-Lingual Convergence (EN, VI, JA)

> **Track:** EXP-02  
> **Target Capability:** Language-Independent Concept Realization & Functional Convergence  
> **Status:** `[EVALUATION PROTOCOL SPECIFICATION]`  
> **Governing Documents:** `candidate_spec.md`, `metrics.md`, `research_baseline.md`

---

## 1. Scientific Context & Hypothesis Formulation

Natural language manifestations differ sharply in syntactic typology:
- **English (EN):** Rigid SVO word order, explicit pronominal subjects.
- **Vietnamese (VI):** Isolating SVO, topic-prominent, classifier-heavy, zero-anaphoric pro-drop.
- **Japanese (JA):** Agglutinative SOV, postpositional case markers (*ga, o, ni*), extensive subject/object omission, honorific morphology.

A language-independent cognitive substrate must abstract away surface typological differences such that identical propositions in EN, VI, and JA instantiate functionally equivalent semantic states.

> [!CAUTION]
> **Evaluation Invariant:**  
> Cross-lingual equivalence **MUST NOT** be measured by graph isomorphism. Topological node counts and auxiliary edge structures naturally vary across languages. Equivalence is measured strictly by **Functional Equivalence Parity ($\text{FEP}$)**, **Thematic Role Parity**, and **$\text{SQI}_{\text{cross}}$**.

### 1.1 Testable Hypotheses

- **$H_1$ (Cross-Lingual Functional Invariance in UMR-TPG):**  
  Parallel inputs in EN, VI, and JA representing the same communicative intention will instantiate UMR-TPG semantic states that yield $\text{FEP} \ge 0.95$ across a standardized probe query suite $\mathcal{Q}$.
- **$H_0$ (Typological Leakage Null Hypothesis):**  
  Typological differences between SVO (EN/VI) and SOV (JA) leak into the semantic graph structure, producing divergent role bindings ($\text{FEP} < 0.85$).
- **$H_2$ (V-UMR Cross-Lingual Metric Alignment):**  
  In V-UMR, node-level metric vectors $\mathbf{z}_v \in \mathbb{R}^{32}$ for shared concepts across EN, VI, and JA will exhibit cosine similarity $\ge 0.85$ without requiring multilingual string tokens.

---

## 2. Experimental Setup & Datasets

### 2.1 Parallel Semantic Corpus
The benchmark employs a parallel evaluation corpus of 100 tripartite dialogue propositions translated and aligned across EN, VI, and JA:
1. **Direct Transitive Actions:** (e.g. *"The user explained the problem"* / *"Người dùng giải thích vấn đề"* / *"ユーザーが問題を説明した"*).
2. **Topicalized / Passive Variants:** (e.g. *"As for the problem, the user explained it"* / *"Về vấn đề này, người dùng đã giải thích"* / *"問題については、ユーザーが説明した"*).
3. **Causal & Conditional Relations:** (e.g. *"If the user is tired, Lucia should remain quiet"*).
4. **Epistemic Modality:** (e.g. *"Lucia believes that the user might succeed"*).

### 2.2 Probe Query Suite ($\mathcal{Q}$)
Each parallel triple is subjected to 5 standard probe queries:
1. `Probe_Agent`: Identifies the reified entity initiating the event.
2. `Probe_Patient`: Identifies the recipient/patient of the event.
3. `Probe_Modality`: Probes necessity, possibility, or belief status.
4. `Probe_Polarity`: Probes affirmative vs negated truth value.
5. `Probe_Condition`: Probes conditional prerequisites.

---

## 3. Manipulated & Measured Variables

| Variable | Type | Description |
|---|---|---|
| **Input Language** | Independent | English (EN), Vietnamese (VI), Japanese (JA) |
| **Syntactic Construction** | Independent | Canonical order, Passive, Topicalized |
| **Functional Equivalence Parity ($\text{FEP}$)** | Dependent | Fraction of probe queries returning identical answers across EN, VI, JA |
| **Cross-Lingual SQI ($\text{SQI}_{\text{cross}}$)** | Dependent | Minimum SQI across all three languages |
| **Thematic Role Parity ($\text{TRP}$)** | Dependent | Accuracy of `:ARG0`, `:ARG1`, `:ARG2` alignment |
| **Graph Generation Latency** | Dependent | Time to generate semantic graph from structured input |

---

## 4. Falsification Criteria & Thresholds

| Candidate | Metric | Passing Threshold | Falsification Boundary (Failure) | Epistemological Status |
|---|---|---|---|---|
| **UMR-TPG** | $\text{FEP}(\text{EN}, \text{VI}, \text{JA})$ | $\ge 0.95$ | $< 0.88$ | **Preregistered Gate** |
| **UMR-TPG** | $\text{SQI}_{\text{cross}}$ | $\ge 0.88$ across all 3 | $< 0.80$ in any language | **Preregistered Gate** |
| **UMR-TPG** | Role Swap Resistance | $100.0\%$ | $< 100.0\%$ | **Preregistered Gate** |
| **V-UMR** | Concept Vector Alignment | $\text{Sim} \ge 0.85$ | $< 0.70$ | **Engineering Hypothesis** |
| **DRS-Graph** | $\text{FEP}$ | $\ge 0.90$ | $< 0.80$ | **Preregistered Gate** |

> [!NOTE]
> **Open / Unverified Boundary:**  
> The automatic transformation of raw unstructured Vietnamese and Japanese text into UMR-TPG without an LLM remains an active NLP research area. In this benchmark, evaluation is performed using **standardized dependency/thematic transducers**; full zero-shot edge parsing is marked as **`[Open / Unverified]`**.
