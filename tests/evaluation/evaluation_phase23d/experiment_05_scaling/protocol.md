# Phase 23-D — EXP-05: Scaling & Hardware Feasibility Protocol

> **Experiment ID:** EXP-05  
> **Status:** `[EVALUATION PROTOCOL SPECIFICATION / AUDITED]`  
> **Governance Authority:** `AGENTS.md` §0, §6, §7; Phase 23-D Evaluation Scaffold  
> **Target Subsystems:** Semantic Substrates (UMR-TPG, V-UMR, DRS-Graph)  
> **Production Boundary:** Evaluation experiment only. Zero modifications to `src/core/**`.

---

## 1. Experimental Objective

The objective of **EXP-05** is to empirically test whether candidate semantic substrates can maintain predictable linear memory scaling, sub-millisecond query latency, and sub-2ms non-monotonic belief revision under realistic knowledge accumulation from 1,000 to 100,000 facts on consumer CPU hardware.

Specifically, EXP-05 evaluates:
1. **Memory Footprint Scaling:** Resident Set Size (RSS), Working Set, and Python heap byte-efficiency per fact across $N \in \{1\text{k}, 5\text{k}, 10\text{k}, 25\text{k}, 50\text{k}, 100\text{k}\}$.
2. **Lookup Latency:** Single-core CPU 1-hop role query latency (p50, p95, p99).
3. **Multi-Hop Traversal Latency:** Relational path traversal up to 3 hops.
4. **Belief Revision Latency:** Wall-clock time for contradiction detection and JTMS dependency retraction across 3-hop downstream chains.
5. **20-Watt Hardware Hypothesis:** Evaluating whether execution complies with CPU-only edge constraints without GPU VRAM allocation.

---

## 2. Testable Hypotheses

- **$H_1$ (Linear Memory Scaling in UMR-TPG):**  
  UMR-TPG heap allocation scales strictly linearly $\mathcal{O}(N)$ with an average footprint $\le 500\text{ bytes}$ per asserted fact, remaining within $\le 200\text{ MB}$ total Working Set at $N = 100,000$ facts.
- **$H_0$ (Pointer Fragmentation & Bloat Null Hypothesis):**  
  Adjacency lists and Python heap fragmentation cause Working Set memory usage to exceed $500\text{ MB}$ at $N=100\text{k}$ or query latency to exceed $15.0\text{ ms}$.
- **$H_2$ (V-UMR Memory-Compute Trade-Off Falsification):**  
  In V-UMR, storing dense 32D float vectors and 1024-bit hypervectors increases memory consumption beyond the $\le 350\text{ MB}$ target (~$660\text{ MB}$ measured), demonstrating empirical memory bloat under dual-layer representations.
- **$H_3$ (DRS-Graph Nesting Indirection):**  
  In DRS-Graph, box universe condition encapsulation introduces structural indirection, resulting in slightly higher memory footprint than flat UMR (~$210\text{ MB}$ vs $189\text{ MB}$ at $100\text{k}$).

---

## 3. Evaluated Scaling Points & Workload Profile

### Scaling Points ($N$)
- $N = 1,000$ facts (baseline)
- $N = 5,000$ facts (session scale)
- $N = 10,000$ facts (intermediate)
- $N = 25,000$ facts (monthly companion scale)
- $N = 50,000$ facts (long-term companion scale)
- $N = 100,000$ facts (stress horizon)

### Workload Probes
- **1-Hop Lookups:** 100 sampled (subject, predicate) queries measuring exact O(1) index retrieval.
- **3-Hop Traversals:** 50 sampled multi-hop relational path expansions.
- **Belief Revision:** 20 contradiction injections targeting root premises with 3-hop downstream dependencies.

---

## 4. Software SLA Gates & Falsification Boundaries

| Candidate | Metric | Engineering Target | Falsification Boundary (Failure) | Status |
|---|---|---|---|---|
| **UMR-TPG** | Total RSS at $N=100\text{k}$ | $\le 200\text{ MB}$ | $> 500\text{ MB}$ | **Engineering Gate** |
| **UMR-TPG** | 1-Hop Lookup Latency ($p95$) | $\le 5.0\text{ ms}$ | $> 15.0\text{ ms}$ | **Engineering Gate** |
| **UMR-TPG** | Belief Revision Latency ($p95$) | $\le 2.0\text{ ms}$ | $> 10.0\text{ ms}$ | **Engineering Gate** |
| **V-UMR** | Total RSS at $N=100\text{k}$ | $\le 350\text{ MB}$ | $> 800\text{ MB}$ | **Engineering Gate** |
| **DRS-Graph** | Total RSS at $N=100\text{k}$ | $\le 250\text{ MB}$ | $> 600\text{ MB}$ | **Engineering Gate** |
| **All** | GPU VRAM Allocated | **$0.0\text{ MB}$** | $> 0.0\text{ MB}$ | **Canonical Invariant** |

---

## 5. Hardware & Environmental Limitations

- **Physical 20W TDP Measurement:** Direct CPU package wattage measurement is unavailable without dedicated hardware power monitoring tools. This aspect is explicitly classified as **`UNVERIFIED`**.
- **Platform:** Windows (measured via Windows `GetProcessMemoryInfo` for WorkingSetSize and PrivateUsage, and `tracemalloc` for Python heap allocation).
