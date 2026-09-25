# Phase 23-D — EXP-01: Compositionality & Recursion Protocol

> **Experiment ID:** EXP-01  
> **Status:** `[EXPERIMENTAL PROTOCOL / AUDITED]`  
> **Governance Authority:** `AGENTS.md` §0, §6, §7; Phase 23-D Evaluation Scaffold  
> **Research Boundary:** Evaluation experiment only. No production runtime changes.

---

## 1. Experimental Objective

The objective of **EXP-01** is to empirically test whether candidate semantic substrates can maintain:
1. **Variable/Role Binding:** Exact mapping between semantic roles (`:ARG0`, `:ARG1`, `:ARG2`) and entity fillers.
2. **Recursive Proposition Nesting:** Deep proposition embedding across recursion depths $D \in \{1, 2, 3, 4\}$.
3. **Role Preservation under Adversarial Swaps:** Resistance to argument reversal ($ARG0(A) \to ARG1(B)$ vs $ARG0(B) \to ARG1(A)$).
4. **Negation & Modal Scope Isolation:** Exact bounding of negation and modal operators to targeted subgraphs.
5. **Path Reconstruction & Zero Cross-Talk:** Deterministic query path recovery without mutating independent assertions.

---

## 2. Experimental Candidates & Roles

| Candidate | Architecture Paradigm | Primary Substrate Role | Evaluation Focus |
|---|---|---|---|
| **UMR-TPG** | Universal Meaning Representation on Typed Property Graph | **Primary Candidate** | Graph traversal, pointer stability, role binding, cyclic immunity |
| **V-UMR** | Vector-Augmented UMR (Graph + Metric Vectors + HDC Gestalt) | **Secondary Candidate** | Graph-vector dual tracking, metric unbinding degradation at depth |
| **DRS-Graph** | Discourse Representation Structure Graph (DRT Box Model) | **Control Candidate** | Formal universe containment, box-subordinated negation & modal scoping |
| **HDC-Pure** | 1024D Dense Bipolar Hypervector Superposition (C3 Baseline) | **Auxiliary Baseline** | Quantifying superposition unbinding collapse under identical inputs |

---

## 3. Dataset Architecture & Test Cases

The test corpus consists of deterministic abstract semantic structures covering depths $D \in \{1, 2, 3, 4\}$. No natural-language parser is used; input is delivered directly as structured semantic specifications to isolate substrate capability.

### 3.1 Depth Categories
- **Depth 1 ($D=1$):** Simple event frame (e.g. $e_1: \text{SEE}(x_1: \text{USER}, x_2: \text{TASK})$).
- **Depth 2 ($D=2$):** Single nesting (e.g. $e_2: \text{BELIEVE}(x_3: \text{LUCIA}, e_1)$).
- **Depth 3 ($D=3$):** Double nesting (e.g. $e_3: \text{INFORM}(x_4: \text{ADMIN}, x_3, e_2)$).
- **Depth 4 ($D=4$):** Triple nesting (e.g. $e_4: \text{CONFIRM}(x_1, e_3)$).

### 3.2 Six Test Suites per Depth
For every depth $D \in \{1, 2, 3, 4\}$, the generator creates:
1. `simple_role_binding`: Baseline predicate-argument mapping.
2. `nested_proposition`: Recursive propositional embedding without arguments.
3. `nested_with_role_binding`: Recursive propositions with distinct arguments at each nesting level.
4. `negated_proposition`: Direct event negation ($\text{NOT } P$).
5. `nested_negation_scope`: Complex scoping ($\text{BELIEVE}(A, \text{NOT } P)$ vs $\text{NOT BELIEVE}(A, P)$).
6. `adversarial_role_swap`: Inverted argument pairs ($A \to B$ vs $B \to A$, repeated entities across depths).

### 3.3 Core Invariants Checked
- **Binding Preservation:** $\text{Role}(e) \to \text{Entity}$ remains invariant after subsequent nestings.
- **Identity Preservation:** $\text{EntityID}$ remains immutable across the entire recursive chain.
- **Scope Preservation:** $\text{Negation}(e_k)$ affects only $e_k$ and its subordinate scope, never parent $e_{k-1}$ or independent $e_{\text{indep}}$.
- **Path Preservation:** Retrieval query traversing depth-$D$ returns the original terminal entity.
- **No Cross-Talk:** Adding recursive structure $S_{\text{new}}$ causes $0$ mutations to pre-existing independent proposition $S_{\text{indep}}$.

---

## 4. Quantitative Metrics

1. **Structural Path Reconstruction Rate (SPRR):**
   $$\text{SPRR}_D = \frac{\text{Successfully Reconstructed Expected Paths at Depth } D}{\text{Total Expected Paths at Depth } D}$$
2. **Binding Error Rate (BER):**
   $$\text{BER} = \frac{\text{Incorrect Role-Filler Bindings}}{\text{Total Tested Bindings}}$$
3. **Scope Preservation Rate (SPR):**
   $$\text{SPR} = \frac{\text{Propositions with Correct Negation / Modal Scoping}}{\text{Total Scoped Propositions}}$$
4. **Cross-Talk Rate (CTR):**
   $$\text{CTR} = \frac{\text{Independent Assertions Modified Post-Ingestion}}{\text{Total Independent Assertions}}$$

---

## 5. Falsification Protocol & Thresholds

| Metric | Target Standard | Failure Signal (Falsification) | Classification |
|---|---|---|---|
| **SPRR ($D=4$)** | $\ge 0.95$ | $< 0.95$ | **Falsification Gate** |
| **Binding Error Rate (BER)** | $\le 0.02$ | $> 0.02$ | **Falsification Gate** |
| **Scope Preservation Rate (SPR)** | $\ge 0.98$ | $< 0.95$ | **Falsification Gate** |
| **Cross-Talk Rate (CTR)** | **$0.000$** | $> 0.000$ | **Invariant Gate** |
| **Role Swap Accuracy (RSA)** | **$100.0\%$** | $< 100.0\%$ | **Invariant Gate** |

### Status Classification Rules
- **`PASS`**: Meets or exceeds all target standards.
- **`FAIL`**: Violates one or more falsification boundaries.
- **`NOT_SUPPORTED`**: Candidate explicitly does not support the structural operation.
- **`UNVERIFIED`**: Empirical evidence is incomplete or inconclusive.
