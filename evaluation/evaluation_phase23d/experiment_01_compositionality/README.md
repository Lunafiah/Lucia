# Experiment 01 — Compositionality & Recursion Depth

> **Track:** EXP-01  
> **Target Capability:** Compositional Propositional Embedding & Recursive Scoping  
> **Status:** `[EVALUATION PROTOCOL SPECIFICATION]`  
> **Governing Documents:** `candidate_spec.md`, `metrics.md`, `research_baseline.md`

---

## 1. Scientific Context & Hypothesis Formulation

In Phase 23-C, the hybrid baseline C4 achieved $RF_3 = 86.4\%$ at recursion depth $D=3$, but degraded to $RF_4 = 83.5\%$ at $D=4$. This degradation occurred because C4's global HDC hypervector suffered superposition crosstalk as role-filler bindings multiplied, pulling down the composite fidelity. Pure vector representations (C3 HDC and C5 TPR) collapsed completely at depth ($RF_4 \le 31.2\%$).

### 1.1 Testable Hypotheses

- **$H_1$ (UMR-TPG Recursion Invariance):**  
  Because UMR-TPG represents proposition embedding via directed pointer edges rather than dense vector superposition, its structural traversal fidelity will remain invariant across recursion depths $D \in \{1, 2, 3, 4\}$, achieving $RF_D \ge 90.0\%$ at all depths.
- **$H_0$ (Null Hypothesis):**  
  UMR-TPG exhibits structural degradation or cycle-induced failure at $D \ge 3$, failing to exceed C4's performance ($RF_4 \le 83.5\%$).
- **$H_2$ (V-UMR Dual Degradation Boundary):**  
  In V-UMR, while the graph structure maintains traversal fidelity, the localized vector unbinding metric will exhibit linear degradation as depth exceeds $D \ge 3$.
- **$H_3$ (DRS-Graph Scoping Precision):**  
  DRS-Graph maintains $100\%$ scoping fidelity through formal box containment, but incurs an exponential traversal time penalty as box depth increases.

---

## 2. Experimental Setup & Controls

### 2.1 Candidate Configurations
1. **Primary:** UMR-TPG (Pure Typed Property Graph)
2. **Secondary:** V-UMR (Graph + 32D Node Vectors + 1024D Subgraph Gestalt)
3. **Control:** DRS-Graph (Box-partitioned Discourse Representation Structure)
4. **Auxiliary Baseline:** C4 Hybrid Baseline (from Phase 23-C benchmark) & C3 Dense HDC

### 2.2 Recursion Depth Test Suite
Scenarios are generated across four depths using standardized predicate embedding:
- **Depth 1:** Single event: *"The user completed the task."*
- **Depth 2:** Nested event: *"Lucia noticed that the user completed the task."*
- **Depth 3:** Doubly nested: *"The user remembers that Lucia noticed that the user completed the task."*
- **Depth 4:** Triply nested: *"Lucia believes that the user remembers that Lucia noticed that the user completed the task."*

### 2.3 Adversarial Role Swap Suite
50 paired scenarios where Agent and Patient roles are inverted:
- Pair A: *"Entity X assisted Entity Y."*
- Pair B: *"Entity Y assisted Entity X."*

---

## 3. Manipulated & Measured Variables

| Variable | Type | Description / Range |
|---|---|---|
| **Recursion Depth ($D$)** | Independent | $D \in \{1, 2, 3, 4\}$ |
| **Role Inversion** | Independent | Permutation of `:ARG0` and `:ARG1` |
| **Negation Polarity** | Independent | Affirmative vs Negative modality scope |
| **Recursion Fidelity ($RF_D$)** | Dependent | Percentage of constituent propositions correctly extracted |
| **Role Swap Accuracy ($\text{RSA}$)** | Dependent | Percentage of inverted pairs correctly discriminated |
| **Negation Scope Fidelity ($\text{NSF}$)** | Dependent | Accuracy in binding negation strictly to targeted proposition |
| **CPU Traversal Latency** | Dependent | Microseconds ($\mu\text{s}$) to traverse depth-$D$ graph |

---

## 4. Falsification Criteria & Evaluation Boundaries

| Candidate | Metric | Passing Threshold | Falsification Boundary (Failure) | Epistemological Status |
|---|---|---|---|---|
| **UMR-TPG** | $RF_3$ | $\ge 90.0\%$ | $< 90.0\%$ | **Preregistered Gate** |
| **UMR-TPG** | $RF_4$ | $\ge 85.0\%$ | $< 85.0\%$ (Fails to beat C4) | **Preregistered Gate** |
| **UMR-TPG** | $\text{RSA}$ | $100.0\%$ | $< 100.0\%$ (Ambiguous role binding) | **Preregistered Gate** |
| **V-UMR** | $RF_4$ (Composite) | $\ge 85.0\%$ | $< 80.0\%$ | **Preregistered Gate** |
| **DRS-Graph** | Scoping Fidelity | $\ge 95.0\%$ | $< 90.0\%$ | **Preregistered Gate** |
| **All** | Single-core Latency | $\le 2.0\text{ ms}$ at $D=4$ | $> 5.0\text{ ms}$ | **Engineering Hypothesis** |

---

## 5. Execution Protocol & Safety Constraints

1. Scenarios must be evaluated over 5 distinct random seeds (`[42, 1337, 2026, 7113, 8421]`).
2. Graph extraction must be performed by deterministic graph traversal algorithms without querying any LLM or heuristic oracle.
3. Zero GPU VRAM must be allocated during execution.
