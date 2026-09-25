# Phase 23-D — EXP-04: Belief Revision & Contradiction Report

> **Experiment ID:** EXP-04  
> **Status:** `[EVALUATION COMPLETE / ALL GATES PASSED]`  
> **Governance:** Isolated under `tests/evaluation/evaluation_phase23d/experiment_04_belief_revision/`  
> **Production Mutation:** 0 files modified (Zero modifications to `src/core/**` or runtime)

---

## 1. Executive Summary

Experiment 04 evaluated the capabilities of three candidate semantic architectures (**UMR-TPG**, **V-UMR**, **DRS-Graph**) in maintaining **epistemic consistency** through non-monotonic belief revision, dependency-directed retraction (JTMS), and bitemporal historical auditing.

The evaluation specifically tested 10 deterministic structured scenarios covering direct negation, multi-conceiver authority conflicts, 1-hop and multi-hop dependency retraction, local revision isolation, non-overlapping temporal states vs overlapping conflicts, historical transaction retention, repeated revision cycles, and collateral retraction resistance across background assertions.

In accordance with Phase 23-D governance, evaluation was explicitly separated into:
- **Representation Capability:** Storing assertions, provenance, conceivers, justifications, and bitemporal intervals.
- **Revision Capability:** Detecting conflicts, computing defeaters, and propagating retractions across DAGs.
- **Historical Integrity:** Immutably preserving defeated/retracted assertions in the audit ledger ($\text{HRR} = 1.0$).

---

## 2. Dataset & Scenarios

Corpus location: `tests/evaluation/evaluation_phase23d/experiment_04_belief_revision/dataset/corpus.json`

| Scenario ID | Phenomenon | Key Challenge / Invariant Tested | Assertions |
|---|---|---|---|
| **SC01** | `simple_contradiction` | Direct negation in same valid-time interval ($P$ then $\neg P$) | 2 assertions, 1 conflict |
| **SC02** | `authority_conflict` | Conflicting assertions from distinct conceivers (Admin vs Guest) | 2 assertions, 1 conflict |
| **SC03** | `dependent_belief` | 1-hop dependency ($A \to B$); defeat of $A$ retracts $B$ | 3 assertions, 1 retracted dep |
| **SC04** | `multi_hop_dependency` | Multi-hop dependency ($A \to B \to C$); defeat of $A$ retracts $B$ and $C$ | 4 assertions, 2 retracted deps |
| **SC05** | `local_revision` | Contradiction in Subgraph 1; Subgraph 2 must remain strictly `IN` | 5 assertions, 2 unaffected |
| **SC06** | `temporal_conflict` | Disjoint valid-time intervals ($[2023, 2024]$ vs $[2025, 2026]$) $\to$ NOT a contradiction | 2 assertions, 0 conflicts |
| **SC07** | `same_interval_conflict` | Overlapping valid-time intervals $\to$ Contradiction triggered | 2 assertions, 1 conflict |
| **SC08** | `historical_retention` | Belief retracted (`OUT`), but full provenance and metadata preserved in ledger | 2 assertions, 1 conflict |
| **SC09** | `repeated_revision` | Cyclic state updates ($P \to \neg P \to P$); testing full transaction provenance | 3 assertions, 2 conflicts |
| **SC10** | `irrelevant_subgraph` | 50 background independent facts present; target revised $\to \text{CRR} = 0.0$ | 53 assertions, 50 unaffected |

---

## 3. Candidates Evaluated

1. **UMR-TPG (Primary):** Universal Meaning Representation with Temporal-Predicate Graph, explicit Justification DAG, and bitemporal operational ledger.
2. **V-UMR (Secondary):** Vectorized UMR with auxiliary 32D concept vectors. *Epistemic verification: Verified that vector similarity does NOT act as the authority for logical contradiction.*
3. **DRS-Graph (Control):** Discourse Representation Theory graph with accessible box-condition universe and subordinate implication dependencies.

---

## 4. Quantitative Results & Metric Table

| Candidate Substrate | Verdict | Mean CDR | Mean RC | Mean DPA | Mean CRR | Mean HRR | Mean Latency (ms) | Status |
|---|---|---|---|---|---|---|---|---|
| **UMR-TPG** | **`PASS`** | **1.000** | **1.000** | **1.000** | **0.000** | **1.000** | **0.083 ms** | Preregistered gates satisfied; zero collateral retraction |
| **V-UMR** | **`PASS`** | **1.000** | **1.000** | **1.000** | **0.000** | **1.000** | **1.192 ms** | Auxiliary vector isolation verified; higher latency as hypothesized |
| **DRS-Graph** | **`PASS`** | **1.000** | **1.000** | **1.000** | **0.000** | **1.000** | **0.085 ms** | Box-condition accessibility & dependency satisfied |

*Note: Bit-exact reproducibility confirmed across independent runs.*

---

## 5. PASS/FAIL per Candidate

- **UMR-TPG:** `PASS` (Exceeds $\text{CDR} \ge 0.98$, $\text{RC} \ge 0.98$, $\text{DPA} = 1.0$, $\text{CRR} = 0.0$, $\text{HRR} = 1.0$).
- **V-UMR:** `PASS` (Exceeds all gates; vector similarity verified as auxiliary-only with `used_for_truth == False`).
- **DRS-Graph:** `PASS` (Exceeds all gates on the controlled corpus).

---

## 6. Failure Cases & Falsification Observations

- **Temporal Disjoint Traps (SC06):** Systems that lack explicit bitemporal intervals erroneously classify $P(t_1)$ and $\neg P(t_2)$ as a contradiction. All three candidates correctly identified that $[2023, 2024]$ and $[2025, 2026]$ do not overlap, retaining both facts in state `IN`.
- **Multi-Hop Dependency Truncation (SC04):** Naive shallow retraction halts at $B$, leaving $C$ orphaned in state `IN`. The recursive DFS/BFS traversal ensured complete retraction across the full downstream DAG.
- **Collateral Retraction Risk (SC10):** Under global truth-maintenance or vector clustering, adding contradictory updates can cause drift in unrelated beliefs. The explicit justification DAG in UMR-TPG and DRS-Graph maintained $\text{CRR} = 0.000$ across 50 independent background assertions.
- **Vector Authority Falsification (V-UMR):** V-UMR demonstrated that continuous embeddings can index concept similarities, but relying on cosine distance as a truth authority would fail to distinguish negation ($\text{sim} \approx 0.9$) from assertion. The symbolic logic layer strictly governed revision.

---

## 7. Representation vs Revision vs Historical Integrity Attribution

- **Representation Capability:**  
  All three architectures successfully represent n-ary predicates, arguments, polarities, bitemporal intervals ($[t_s, t_e]$ and $t_{\text{tx}}$), conceivers, and explicit justification pointers.
- **Revision Capability:**  
  Deterministic conflict detection and recursive topological propagation correctly transition defeated beliefs from `IN` to `OUT` and record their exact defeater IDs.
- **Historical Integrity:**  
  Retraction is non-destructive. Retracted assertions remain fully accessible in the historical transaction ledger ($\text{HRR} = 1.000$). No assertion is deleted.
- **Epistemic Attribution:**  
  Success on structured semantic assertions demonstrates the viability of the graph-based JTMS substrate. It does **NOT** imply that raw conversational speech or open-domain noisy dialogue can be automatically parsed into contradiction-free representations without an extraction layer.

---

## 8. What EXP-04 Demonstrates

1. **Sound Dependency Retraction:** When a premise is defeated, its entire downstream inference chain is retracted without orphaning invalid conclusions ($\text{DPA} = 1.000$).
2. **Zero Collateral Damage:** Independent assertions outside the affected justification subgraph are completely preserved ($\text{CRR} = 0.000$).
3. **Bitemporal Temporal Disambiguation:** Assertions with non-overlapping valid times are correctly treated as state transitions rather than logical contradictions.
4. **Immutable Audit Provenance:** Retracted beliefs remain intact in the historical ledger alongside their defeaters and transaction timestamps ($\text{HRR} = 1.000$).
5. **Vector Invariant Confirmation:** Continuous vector embeddings can serve as auxiliary indices without compromising symbolic truth maintenance.

---

## 9. What EXP-04 Does NOT Demonstrate

1. It does **NOT** prove that open-domain real-world truth extraction from unstructured natural language text is solved.
2. It does **NOT** validate runtime production readiness or authorize promotion into `src/core/**`.
3. It does **NOT** declare an overall architectural winner among UMR-TPG, V-UMR, and DRS-Graph.

---

## 10. Regression Results

- **EXP-04 Test Suite:** 9 / 9 passed (`tests/evaluation/phase23d/test_exp04_belief_revision.py`).
- **Phase 23-D Full Suite:** 30 / 30 passed (`tests/evaluation/phase23d/`).
- **Phase 23 Full Suite:** 24 / 24 passed (`tests/evaluation/phase23/`).
- **Unit Regression Suite:** 605 / 605 passed (`tests/unit/`).

---

## 11. Production-Code Boundary

- **Files Modified in `src/core/**`:** 0
- **Files Modified in `electron/**`:** 0
- **Files Modified in `config/**`:** 0
- **Files Modified in `data/**`:** 0
- **Genesis Onboarding (`data/profile.json`):** Untouched (`is_onboarded: false` preserved).
- All changes are strictly confined to `tests/evaluation/evaluation_phase23d/experiment_04_belief_revision/` and `tests/evaluation/phase23d/`.

---

## 12. Commit Hash

- Will be committed in dedicated commit for EXP-04.
