# Phase 23-D — EXP-05: Scaling & Hardware Feasibility Report

> **Experiment ID:** EXP-05  
> **Status:** `[EVALUATION COMPLETE / EMPIRICAL FALSIFICATION RECORDED]`  
> **Governance:** Isolated under `tests/evaluation/evaluation_phase23d/experiment_05_scaling/`  
> **Production Mutation:** 0 files modified (Zero modifications to `src/core/**` or runtime)

---

## 1. Status

- **Benchmark Name:** Phase 23-D EXP-05 (Scaling & Hardware Feasibility)
- **Status:** Complete. Empirical falsification recorded for V-UMR memory footprint gate at 100k facts. UMR-TPG and DRS-Graph passed all SLA gates.

---

## 2. Dataset & Scaling Levels

Deterministic seeded generation ($seed = 42$) evaluated across 6 scaling horizons:
- $N = 1,000$ facts
- $N = 5,000$ facts
- $N = 10,000$ facts
- $N = 25,000$ facts
- $N = 50,000$ facts
- $N = 100,000$ facts (stress horizon)

Every fact contained:
- Unique entity references (subjects, objects)
- Typed relational predicates
- Polarity, valid-time intervals, transaction sequence numbers
- Justification pointers forming multi-hop dependency chains ($A \to B \to C \to D$)

---

## 3. Candidates Evaluated

1. **UMR-TPG (Primary):** Universal Meaning Representation with Temporal-Predicate Graph.
2. **V-UMR (Secondary):** Vectorized UMR with auxiliary 32D metric coordinates and 1024-bit binary hypervectors.
3. **DRS-Graph (Control):** Discourse Representation Theory box-condition universe with subordinate implication links.

---

## 4. Hardware & Environment

- **Execution Profile:** Single-core CPU edge execution
- **GPU VRAM Allocation:** $0.0\text{ MB}$ (strictly enforced across all runs)
- **Host OS:** Windows (measured via Windows `GetProcessMemoryInfo` for WorkingSetSize and `tracemalloc` for Python heap)
- **20-Watt TDP Envelope:** Classified as **`UNVERIFIED`** due to absence of hardware package power meter in test environment.

---

## 5. Metric Table (100k Horizon Overview)

| Candidate | Verdict | Heap at 100k (MB) | WorkingSet at 100k (MB) | Bytes/Fact | Lookup p95 (ms) | Traversal p95 (ms) | Revision p95 (ms) |
|---|---|---|---|---|---|---|---|
| **UMR-TPG** | **`PASS`** | **43.0 MB** | **189.2 MB** | **450.8 B** | **0.007 ms** | **4.701 ms** | **0.033 ms** |
| **V-UMR** | **`FAIL`** | **167.2 MB** | **660.3 MB** | **1752.7 B** | **0.019 ms** | **6.563 ms** | **0.124 ms** |
| **DRS-Graph** | **`PASS`** | **51.0 MB** | **210.3 MB** | **534.7 B** | **0.005 ms** | **5.466 ms** | **0.036 ms** |

---

## 6. Results by Scaling Point

| Fact Scale ($N$) | Candidate | Heap (MB) | WorkingSet (MB) | Lookup p50 (ms) | Lookup p95 (ms) | Revision p95 (ms) |
|---|---|---|---|---|---|---|
| **1,000** | UMR-TPG | 0.4 MB | 19.4 MB | 0.0015 ms | 0.0029 ms | 0.0142 ms |
| | V-UMR | 1.6 MB | 77.6 MB | 0.0197 ms | 0.0304 ms | 0.1755 ms |
| | DRS-Graph | 0.5 MB | 80.2 MB | 0.0019 ms | 0.0034 ms | 0.0148 ms |
| **5,000** | UMR-TPG | 2.1 MB | 26.4 MB | 0.0021 ms | 0.0040 ms | 0.0247 ms |
| | V-UMR | 8.1 MB | 68.8 MB | 0.0141 ms | 0.0217 ms | 0.0726 ms |
| | DRS-Graph | 2.5 MB | 65.0 MB | 0.0026 ms | 0.0052 ms | 0.0322 ms |
| **10,000** | UMR-TPG | 4.2 MB | 35.0 MB | 0.0026 ms | 0.0045 ms | 0.0174 ms |
| | V-UMR | 16.2 MB | 89.0 MB | 0.0198 ms | 0.0240 ms | 0.0535 ms |
| | DRS-Graph | 5.0 MB | 69.1 MB | 0.0025 ms | 0.0041 ms | 0.0180 ms |
| **25,000** | UMR-TPG | 10.7 MB | 61.2 MB | 0.0033 ms | 0.0058 ms | 0.0349 ms |
| | V-UMR | 41.7 MB | 178.9 MB | 0.0148 ms | 0.0227 ms | 0.0665 ms |
| | DRS-Graph | 12.7 MB | 81.1 MB | 0.0026 ms | 0.0046 ms | 0.0344 ms |
| **50,000** | UMR-TPG | 21.4 MB | 103.9 MB | 0.0040 ms | 0.0127 ms | 0.0193 ms |
| | V-UMR | 83.5 MB | 339.4 MB | 0.0214 ms | 0.0390 ms | 0.0978 ms |
| | DRS-Graph | 25.4 MB | 116.4 MB | 0.0033 ms | 0.0057 ms | 0.0722 ms |
| **100,000** | UMR-TPG | 43.0 MB | 189.2 MB | 0.0037 ms | 0.0074 ms | 0.0325 ms |
| | V-UMR | 167.2 MB | 660.3 MB | 0.0149 ms | 0.0188 ms | 0.1238 ms |
| | DRS-Graph | 51.0 MB | 210.3 MB | 0.0030 ms | 0.0052 ms | 0.0364 ms |

---

## 7. SLA Gate Classification (PASS / FAIL / UNVERIFIED)

- **UMR-TPG:** **`PASS`**
  - WorkingSet at 100k: $189.2\text{ MB} \le 200.0\text{ MB}$ gate (`PASS`)
  - 1-Hop Lookup p95: $0.0074\text{ ms} \le 5.0\text{ ms}$ gate (`PASS`)
  - Belief Revision p95: $0.0325\text{ ms} \le 2.0\text{ ms}$ gate (`PASS`)
  - VRAM: $0.0\text{ MB}$ (`PASS`)
- **V-UMR:** **`FAIL`**
  - WorkingSet at 100k: $660.3\text{ MB} > 350.0\text{ MB}$ gate (**`FAIL`**)
  - 1-Hop Lookup p95: $0.0188\text{ ms} \le 5.0\text{ ms}$ (`PASS`)
  - Belief Revision p95: $0.1238\text{ ms} \le 2.0\text{ ms}$ (`PASS`)
  - VRAM: $0.0\text{ MB}$ (`PASS`)
- **DRS-Graph:** **`PASS`**
  - WorkingSet at 100k: $210.3\text{ MB} \le 250.0\text{ MB}$ gate (`PASS`)
  - 1-Hop Lookup p95: $0.0052\text{ ms} \le 5.0\text{ ms}$ gate (`PASS`)
  - Belief Revision p95: $0.0364\text{ ms} \le 2.0\text{ ms}$ gate (`PASS`)
  - VRAM: $0.0\text{ MB}$ (`PASS`)
- **Physical 20W TDP:** **`UNVERIFIED`** across all candidates (measurement tool limitation).

---

## 8. Bottlenecks & Failure Cases

- **V-UMR Memory Explosion ($H_2$ Falsification):**  
  While Python heap memory for V-UMR was $167.2\text{ MB}$, the underlying OS Working Set on Windows grew to $660.3\text{ MB}$. Allocating 100,000 distinct 32-float tuples and 128-byte hypervector byte objects triggered severe Windows page-allocation fragmentation. This empirical result falsifies the hypothesis that dual-layer representations can remain within a 350 MB footprint at 100k facts without specialized contiguous C-level memory arenas.
- **3-Hop Traversal Scaling:**  
  At 100k facts, 3-hop traversal latency grew to $4.70\text{ ms}$ (UMR-TPG), $6.56\text{ ms}$ (V-UMR), and $5.47\text{ ms}$ (DRS-Graph). While lookup and revision remain sub-millisecond, unconstrained multi-hop traversals require beam-search pruning or depth bounds in production.

---

## 9. Reproducibility

- The experiment was run twice with deterministic seed $42$.
- Fact generation, graph topologies, probe selections, and SLA verdicts were bit-exact across runs.
- Execution latencies exhibited typical minor timing variation ($\le 5\%$) while maintaining consistent ranking.

---

## 10. Regression Results

- **EXP-05 Suite:** 12 / 12 passed (`tests/evaluation/phase23d/test_exp05_scaling.py`).
- **Phase 23-D Full Suite:** 42 / 42 passed (`tests/evaluation/phase23d/`).
- **Phase 23 Full Suite:** 24 / 24 passed (`tests/evaluation/phase23/`).
- **Unit Regression Suite:** 605 / 605 passed (`tests/unit/`).

---

## 11. Production-Code Boundary

- **Files Modified in `src/core/**`:** 0
- **Files Modified in `electron/**`:** 0
- **Files Modified in `config/**`:** 0
- **Files Modified in `data/**`:** 0
- **Genesis Onboarding (`data/profile.json`):** Untouched (`is_onboarded: false` preserved).
- All changes are strictly confined to `tests/evaluation/evaluation_phase23d/experiment_05_scaling/` and `tests/evaluation/phase23d/`.

---

## 12. Commit Hash

- Committed under dedicated commit for EXP-05.

---

## 13. Scientific Interpretation

### Demonstrated:
1. **UMR-TPG Memory Viability:** UMR-TPG successfully stores 100,000 structured relational facts in $43.0\text{ MB}$ of Python heap and $189.2\text{ MB}$ of total Working Set, satisfying the $\le 200\text{ MB}$ 20W edge memory budget.
2. **Sub-Millisecond 1-Hop Retrieval:** Both UMR-TPG ($0.0074\text{ ms}$) and DRS-Graph ($0.0052\text{ ms}$) provide near-instantaneous 1-hop role lookups at 100k scale.
3. **Sub-Millisecond Belief Revision:** Localized JTMS dependency retraction scales gracefully, executing in $\le 0.036\text{ ms}$ for 3-hop downstream chains at 100k scale.
4. **V-UMR Memory Footprint Falsification:** Dual-representation overhead (vectors alongside symbolic graph) exceeds 660 MB under standard Python allocation, proving that persistent vector storage at scale requires dedicated contiguous memory engines.

### Falsified:
- $H_2$ is **falsified**: V-UMR cannot remain $\le 350\text{ MB}$ total Working Set at 100k facts in this environment ($660.3\text{ MB}$ measured).

### Unverified:
- Exact 20-Watt physical power draw remains **`UNVERIFIED`** due to lack of a physical hardware power meter.

---

## 14. What EXP-05 Does NOT Demonstrate

1. It does **NOT** prove that open-domain unstructured dialogue can be converted into these structured facts in real time.
2. It does **NOT** demonstrate production readiness or authorize promotion into `src/core/**`.
3. It does **NOT** declare an overall architectural winner.
4. It does **NOT** prove that the physical CPU power remained under 20 Watts during execution.
