# Phase 23-D — Evaluation Metrics & Mathematical Formulations

> **Document Type:** Metric Definitions, Verification Protocols & Falsification Standards  
> **Status:** `[CANONICAL METRICS LEDGER]`  
> **Authority:** `AGENTS.md` §0; Phase 23-D Evaluation Scaffold  
> **Methodological Mandate:** Strict rejection of graph isomorphism; Functional equivalence & SQI primary.

---

## 1. Methodological Foundations: Why Graph Isomorphism Is Rejected

A critical defect of naive semantic graph evaluations is the use of **graph isomorphism** (or exact subgraph matching) as a test of semantic equivalence. In natural language and cognitive semantics, **graph isomorphism is fundamentally invalid**:

```text
┌────────────────────────────────────────────────────────────────────────────────────────┐
│ WHY GRAPH ISOMORPHISM FAILS AS A SEMANTIC METRIC                                       │
├────────────────────────────────────────────────────────────────────────────────────────┤
│                                                                                        │
│  Expression A (Active):  "The user gave Lucia a book."                                 │
│  Expression B (Passive): "A book was given to Lucia by the user."                      │
│  Expression C (VI):      "Người dùng tặng cuốn sách cho Lucia."                       │
│  Expression D (JA):      "ユーザーはルシアに本をあげた。"                              │
│                                                                                        │
│  • Surface variations alter dependency root orders and node generation sequences.      │
│  • Topicalization and focus particles create ancillary modifier nodes.                 │
│  • Requiring isomorphic graph adjacency falsely classifies valid semantic              │
│    paraphrases and cross-lingual convergences as failures.                             │
│                                                                                        │
│  RULE: Semantic equivalence MUST be evaluated via:                                     │
│  1. Functional Equivalence (Identical answers to semantic probes).                     │
│  2. Thematic Role Parity (Invariant predicate-argument binding).                       │
│  3. Semantic Quality Index (SQI) (Multi-attribute structural score).                    │
│                                                                                        │
└────────────────────────────────────────────────────────────────────────────────────────┘
```

---

## 2. Core Quantitative Metrics

### 2.1 Semantic Quality Index (SQI)
The **Semantic Quality Index (SQI)** is a unified composite metric evaluating structural and semantic integrity without relying on topological isomorphism:

$$\text{SQI} = w_1 \cdot \text{TRA} + w_2 \cdot \text{TPA} + w_3 \cdot \text{NPA} + w_4 \cdot \text{SCA}$$

where the canonical weights are pre-registered as:

$$w_1 = 0.35, \quad w_2 = 0.25, \quad w_3 = 0.25, \quad w_4 = 0.15 \quad \left(\sum w_i = 1.0\right)$$

#### Component Formulations:
1. **Thematic Role Accuracy (TRA):**
   Measures the exact binding of core participants to predicates across reified events:
   $$\text{TRA} = \frac{1}{|E_{\text{event}}|} \sum_{e \in E_{\text{event}}} \mathbb{I}\left(\text{Arg}_0(e) == \text{Gold}_0 \land \text{Arg}_1(e) == \text{Gold}_1 \land \text{Arg}_2(e) == \text{Gold}_2\right)$$
2. **Taxonomic Placement Accuracy (TPA):**
   Measures whether concepts are correctly grounded into the relational ontology:
   $$\text{TPA} = \frac{1}{|C|} \sum_{c \in C} \mathbb{I}\left(\text{OntologyCategory}(c) == \text{GoldCategory}(c)\right)$$
3. **Negation Polarity Accuracy (NPA):**
   Measures whether truth polarity ($\text{Pol} \in \{+1, -1\}$) and scope are preserved:
   $$\text{NPA} = \frac{1}{|P|} \sum_{p \in P} \mathbb{I}\left(\text{Polarity}(p) == \text{GoldPolarity}(p)\right)$$
4. **Structural Connectivity Alignment (SCA):**
   Evaluates path reachability between core arguments without requiring isomorphic edge counts:
   $$\text{SCA} = \frac{|\text{ReachablePairs}(G_{\text{cand}}) \cap \text{ReachablePairs}(G_{\text{gold}})|}{|\text{ReachablePairs}(G_{\text{gold}})|}$$

---

### 2.2 Functional Equivalence & Probe Query Parity ($\text{FEP}$)
Two semantic representations $G_A$ and $G_B$ (e.g. formed from English and Vietnamese inputs) are evaluated against a standardized probe query suite $\mathcal{Q} = \{q_1, q_2, \dots, q_K\}$:

$$\text{FEP}(G_A, G_B) = \frac{1}{K} \sum_{k=1}^K \mathbb{I}\left(\text{Query}(G_A, q_k) == \text{Query}(G_B, q_k)\right)$$

Standard probe queries test:
- **Agent Probe:** *"Who performed action $X$?"*
- **Patient Probe:** *"Who/what was affected by action $X$?"*
- **Polarity Probe:** *"Did action $X$ take place, or was it negated?"*
- **Temporal Order Probe:** *"Did event $A$ precede event $B$?"*
- **Causal Probe:** *"What was the stated cause of event $C$?"*

A candidate passes Functional Equivalence if $\text{FEP} \ge 0.95$.

---

### 2.3 Cross-Lingual Concept Alignment ($\text{CLCA}$)
Evaluates the language-independence of concept nodes when exposed to multilingual parallel dialogue:

$$\text{CLCA} = \frac{1}{|C_{\text{shared}}|} \sum_{c \in C} \text{Sim}_{\text{concept}}\left(\text{Node}_{\text{EN}}(c), \text{Node}_{\text{VI}}(c), \text{Node}_{\text{JA}}(c)\right)$$

In UMR-TPG, concept identity is validated by verifying that instances across all three languages link to the same root concept identifier `CONCEPT_UUID` and share identical relational edge types.

---

### 2.4 Anaphora Resolution & Pro-Drop Recall ($\text{ARR}$)
In Vietnamese and Japanese, subjects and objects are frequently omitted (zero-anaphora / pro-drop). The representation must bind omitted arguments to the active discourse referent:

$$\text{ARR} = \frac{|\text{RecoveredZeroAnaphors} \cap \text{GoldZeroAnaphors}|}{|\text{GoldZeroAnaphors}|}$$

Coreference F1 is evaluated standardly via MUC / B-cubed protocols.

---

### 2.5 Retained Unaffected Facts ($\text{RUF}$) in Belief Revision
When an existing premise $P_{\text{old}}$ is explicitly contradicted and retracted, the system must prune all deductive dependents while retaining all logically independent facts:

$$\text{RUF} = \frac{|\text{Facts}_{\text{retained}} \cap \text{Facts}_{\text{unaffected}}|}{|\text{Facts}_{\text{unaffected}}|}$$

$$\text{Soundness}_{\text{retraction}} = \frac{|\text{Facts}_{\text{invalidated}} \setminus \text{ActiveMemory}|}{|\text{Facts}_{\text{invalidated}}|}$$

Target: $\text{RUF} \ge 0.98$ and $\text{Soundness}_{\text{retraction}} = 1.00$ (no stale contradicted inferences remain in active reasoning).

---

## 3. Hardware & Execution Benchmarking Metrics

> [!WARNING]
> **Engineering Hypotheses Notice:**  
> All thresholds in this section are **engineering hypotheses to be empirically benchmarked** on consumer hardware under a 20W TDP envelope. They are not assumed to be true prior to measurement.

| Metric | Measurement Method | Hypothesis Target | Falsification Boundary |
|---|---|---|---|
| **Query Latency (p50)** | Single-core CPU query time | $\le 1.0\text{ ms}$ | $> 3.0\text{ ms}$ |
| **Query Latency (p95)** | Single-core CPU query time under 100k facts | $\le 5.0\text{ ms}$ | $> 15.0\text{ ms}$ |
| **Memory per Concept Node** | Heap allocation per reified concept | $\le 350\text{ bytes}$ | $> 1,000\text{ bytes}$ |
| **Total Memory at $N=100\text{k}$** | Resident Set Size (RSS) delta | $\le 200\text{ MB}$ | $> 500\text{ MB}$ |
| **GPU VRAM Impact** | CUDA allocated memory | **$0.0\text{ MB}$** | $> 0.0\text{ MB}$ |
| **Contradiction Retraction Time** | Time to propagate JTMS retraction DAG | $\le 2.0\text{ ms}$ | $> 10.0\text{ ms}$ |

---

## 4. Epistemological Classification of Evaluation Metrics

| Metric | Symbol | Prior Empirical Basis | Classification |
|---|---|---|---|
| Thematic Role Accuracy | $\text{TRA}$ | Verified in C4 benchmark ($100\%$ at $D=1$) | **Validated Metric** |
| Recursion Fidelity | $RF_D$ | Audited in Microbenchmark v0.2 ($RF_3 = 86.4\%$) | **Validated Metric** |
| Negation Polarity Accuracy | $\text{NPA}$ | Demonstrated in C4 benchmark ($100\%$) | **Validated Metric** |
| Retained Unaffected Facts | $\text{RUF}$ | Demonstrated in C4 benchmark ($100\%$) | **Validated Metric** |
| Semantic Quality Index | $\text{SQI}$ | Composite formulation based on audited components | **Proposed Protocol Metric** |
| Functional Equivalence Parity | $\text{FEP}$ | Standard semantic probe protocol | **Proposed Protocol Metric** |
| Cross-Lingual Concept Alignment | $\text{CLCA}$ | Dependent on cross-lingual UMR parser availability | **`[Open / Unverified]`** |
| Zero-Anaphora Recovery Rate | $\text{ARR}$ | Tested in NLP literature; not yet verified in Lucia | **`[Open / Unverified]`** |
| 100k-Fact RSS $\le 200\text{ MB}$ | $\text{RSS}_{100k}$ | Extrapolated from graph node byte count | **Engineering Hypothesis** |
