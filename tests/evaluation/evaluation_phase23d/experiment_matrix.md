# Phase 23-D — Experiment Matrix & Capability Mapping

> **Document Type:** Multi-Track Evaluation Matrix & Falsification Criteria  
> **Status:** `[EVALUATION MATRIX / PRE-EXECUTION]`  
> **Authority:** `AGENTS.md` §0, §6, §7; Phase 23-D Evaluation Scaffold  
> **Scope:** 6 Empirical Tracks across UMR-TPG, V-UMR, and DRS-Graph

---

## 1. Matrix Overview

The Phase 23-D evaluation matrix systematically contrasts the three candidate architectures across six core capabilities. In accordance with the governance rules:
- **No graph isomorphism:** Structural equivalence is rejected in favor of functional equivalence and Semantic Quality Index (SQI).
- **Engineering hypotheses clearly demarcated:** Latency, RAM, and throughput boundaries are marked as engineering targets requiring benchmark validation.
- **Strict falsification thresholds:** Defined where mathematically justified; marked as `[Open / Unverified]` where empirical baselines do not yet exist.

```text
┌────────────────────────────────────────────────────────────────────────────────────────┐
│                        PHASE 23-D EXPERIMENT SUITE MAP                                 │
├────────────────────────────────────────────────────────────────────────────────────────┤
│                                                                                        │
│  EXP-01: Compositionality & Recursion        -> Depth D ∈ {1, 2, 3, 4}, Role Swap      │
│  EXP-02: Cross-Lingual Convergence          -> EN, VI, JA Functional Equivalence, SQI  │
│  EXP-03: Reference & Zero Anaphora           -> Multi-Turn Coreference & Pro-Drop      │
│  EXP-04: Contradiction & Belief Revision     -> Non-Monotonic Dependency Retraction    │
│  EXP-05: Long-Term Memory Scaling            -> 1k to 100k Facts, Latency, RAM Budget │
│  EXP-06: Multimodal Grounding                -> Sensor Ingestion & Embodiment Coupling │
│                                                                                        │
└────────────────────────────────────────────────────────────────────────────────────────┘
```

---

## 2. Comparative Experiment Matrix

| Exp ID | Target Capability | Primary Candidate (UMR-TPG) | Secondary Candidate (V-UMR) | Control (DRS-Graph) | Auxiliary Baseline | Primary Metric | Target / Falsification Criterion | Epistemological Classification |
|---|---|---|---|---|---|---|---|---|
| **EXP-01** | **Compositionality & Recursion** | Deep edge pointer traversal | Graph traversal + vector unbinding | Box-containment scoping | HDC/TPR binding | Recursion Fidelity ($RF_D$), Role Swap Accuracy (RSA) | $RF_3 \ge 90.0\%$, $RF_4 \ge 85.0\%$, $\text{RSA} = 100\%$ | **Testable Benchmark** |
| **EXP-02** | **Cross-Lingual Convergence** | Universal thematic role normalization | Thematic normalization + shared metric embedding | Discourse referent unification | Multilingual Sentence Transformer | Semantic Quality Index ($\text{SQI}_{\text{cross}}$), Concept Alignment | $\text{SQI}_{\text{cross}} \ge 0.88$ across EN/VI/JA; zero role drift | **Testable Benchmark** |
| **EXP-03** | **Reference & Zero Anaphora** | Discourse graph coreference edges | Coreference edges + entity vector continuity | DRS accessible referent universe | Recency buffer baseline | Anaphora Resolution F1 ($\text{AR-F1}$), Pro-Drop Recall | $\text{AR-F1} \ge 0.85$ on VI/JA zero-anaphora | **Engineering Hypothesis** |
| **EXP-04** | **Contradiction & Belief Revision** | JTMS dependency DAG retraction | JTMS retraction + vector re-weighting | First-order consistency check | Last-in overwrite | Retracted Unaffected Fact ($\text{RUF}$), Revision Time | $\text{RUF} \ge 0.98$, $\text{Latency}_{\text{rev}} \le 2.0\text{ ms}$ | **Testable Benchmark** |
| **EXP-05** | **Long-Term Memory Scaling** | Indexed adjacency graph | HNSW vector index + graph | Partitioned DRS boxes | Flat SDM hypervectors | Query Latency ($p95$), RAM Footprint at $N=100\text{k}$ | $p95 \le 5.0\text{ ms}$, $\text{RAM} \le 200\text{ MB}$ (20W edge CPU) | **Engineering Hypothesis** |
| **EXP-06** | **Multimodal Grounding** | Continuous sensor $\to$ reified concept | Continuous $\to$ metric vector centroid | Continuous $\to$ logical predicate | Raw sensor lookup | Centroid Placement Accuracy ($\text{CPA}$), Stability ($\lambda_{\max}$) | $\text{CPA} \ge 0.90$, $\lambda_{\max} \le 0.0$ (Lyapunov stable) | **Testable Benchmark** |

---

## 3. Detailed Experiment Summaries

### 3.1 EXP-01: Compositionality & Recursion
- **Objective:** Evaluate structural retention, negation scope, and role preservation across deep proposition nesting ($D=1, 2, 3, 4$).
- **Key Test:** Break the $D \le 3$ degradation boundary of Candidate C4 ($83.5\%$ at $D=4$) by proving that pure topological pointer traversals in UMR-TPG retain structural fidelity without signal attenuation.
- **Falsification Threshold:** Candidate fails if $RF_3 < 90.0\%$ or $RF_4 < 85.0\%$.

### 3.2 EXP-02: Cross-Lingual Convergence (EN, VI, JA)
- **Objective:** Determine whether semantically identical inputs in English, Vietnamese, and Japanese converge to functionally equivalent semantic states.
- **Methodological Guard:** Graph isomorphism is explicitly prohibited. Evaluation relies on **Functional Equivalence** (identical probe responses) and **$\text{SQI}_{\text{cross}}$**.
- **Falsification Threshold:** Candidate fails if cross-lingual semantic divergence causes downstream query divergence ($> 12\%$ probe disagreement).

### 3.3 EXP-03: Reference & Zero Anaphora Resolution
- **Objective:** Test tracking of discourse referents across multi-turn dialogues, with specific emphasis on pro-drop phenomena in Vietnamese (*"Đi đâu đấy?"* $\to$ implicit *[Bạn]*) and Japanese (*"お腹が空いた"* $\to$ implicit *[私]*).
- **Falsification Threshold:** Candidate fails if zero-anaphora recall falls below $0.80$ across 5-turn dialog horizons.

### 3.4 EXP-04: Contradiction & Belief Revision
- **Objective:** Test non-monotonic updating when a premise is contradicted (*"The user is at home"* followed 3 turns later by *"The user is at the office"*).
- **Mechanism:** Retraction of dependent inferences via Justification-Based Truth Maintenance (JTMS) without historical re-parsing.
- **Falsification Threshold:** Candidate fails if unaffected facts are mutated ($\text{RUF} < 0.98$) or retraction latency exceeds $10.0\text{ ms}$ on CPU.

### 3.5 EXP-05: Long-Term Memory Scaling & 20W Hardware Budget
- **Objective:** Measure retrieval latency, throughput, and memory consumption scaling from $N=1,000$ to $N=100,000$ asserted facts.
- **Governance Notice:** The target memory footprint ($\le 200\text{ MB}$) and execution SLA ($p95 \le 5.0\text{ ms}$ on a single-core 20W CPU) are **engineering hypotheses to be benchmarked**, not confirmed facts.
- **Falsification Threshold:** Candidate fails if memory consumption exceeds $500\text{ MB}$ at $N=100\text{k}$ or single-query latency exceeds $15.0\text{ ms}$.

### 3.6 EXP-06: Multimodal Grounding & Embodiment
- **Objective:** Test bidirectional coupling between continuous limbic/sensor coordinates (PAD state, eGeMAPS acoustic prosody) and reified conceptual nodes.
- **Stability Requirement:** Bidirectional coupling must not induce limit cycles or unbounded drift (Lyapunov exponent $\lambda_{\max} \le 0.0$ with deadband).
- **Falsification Threshold:** Candidate fails if continuous state injection triggers decision flapping rate $\text{DFR} > 0.0\%$ under static input.
