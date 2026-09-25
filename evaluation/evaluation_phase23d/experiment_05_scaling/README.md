# Experiment 05 — Long-Term Memory Scaling & 20W Hardware Feasibility

> **Track:** EXP-05  
> **Target Capability:** Large-Scale Memory Footprint, Query Latency & 20W Edge Budget  
> **Status:** `[EVALUATION PROTOCOL SPECIFICATION]`  
> **Governing Documents:** `candidate_spec.md`, `metrics.md`, `research_baseline.md`

---

## 1. Scientific Context & Hypothesis Formulation

Lucia is designed to run indefinitely on consumer edge hardware within a strict **20-Watt Whole Brain Architecture** without cloud reliance (`AGENTS.md` §2 INV-5, ADR-002). Over months of interaction, an autobiographical knowledge base may accumulate tens of thousands of relational facts.

While previous microbenchmarks verified the execution of small graph structures ($N \le 100$ nodes in $0.38\text{ ms}$ on CPU), large-scale scaling behavior under $N \in \{1\text{k}, 10\text{k}, 50\text{k}, 100\text{k}\}$ facts remains an untested engineering hypothesis.

> [!WARNING]
> **Engineering Hypotheses Notice:**  
> All hardware performance metrics (RAM budgets, CPU latencies, throughput) are **engineering hypotheses to be empirically benchmarked**, not established facts.

### 1.1 Testable Hypotheses

- **$H_1$ (Linear Memory Scaling in UMR-TPG):**  
  UMR-TPG heap allocation scales strictly linearly $\mathcal{O}(N)$ with an average footprint $\le 350\text{ bytes}$ per asserted fact, remaining within $\le 200\text{ MB}$ total Resident Set Size (RSS) at $N = 100,000$ facts.
- **$H_0$ (Pointer Fragmentation & Bloat Null Hypothesis):**  
  Memory overhead from adjacency lists, node metadata, and Python heap fragmentation causes memory usage to exceed $500\text{ MB}$ at $N=100\text{k}$ or query latency to exceed $15.0\text{ ms}$.
- **$H_2$ (V-UMR Memory-Speed Trade-Off):**  
  In V-UMR, storing dense 32D float vectors and 1024D hypervectors increases memory consumption to $\approx 650 - 900\text{ bytes}$ per fact (~$250 - 350\text{ MB}$ at $100\text{k}$), but reduces top-$k$ semantic search latency by $\ge 40\%$ compared to unindexed graph search.
- **$H_3$ (DRS-Graph Nesting Overhead):**  
  In DRS-Graph, recursive box partitions add structural indirection that scales memory usage to $\ge 450\text{ bytes}$ per fact.

---

## 2. Experimental Setup & Workload Protocol

### 2.1 Synthetic Scaling Datasets
The test harness populates memory stores with synthetic, realistic dialogue-derived semantic assertions at scales:
- $N = 1,000$ facts (baseline)
- $N = 10,000$ facts (intermediate)
- $N = 50,000$ facts (long-term companion scale)
- $N = 100,000$ facts (stress horizon)

### 2.2 Workload Profile
Once loaded, the store is subjected to a mixed read/write workload:
- **80% Reads:**
  - 1-hop role lookups (*"What was the user's stated preference for X?"*)
  - 3-hop relational traversal (*"Who introduced the user to concept Y?"*)
  - Open-ended neighborhood queries
- **20% Writes:**
  - Insertion of new episodic event graphs
  - In-place attribute updates

---

## 3. Manipulated & Measured Variables

| Variable | Type | Description |
|---|---|---|
| **Fact Scale ($N$)** | Independent | $N \in \{1\text{k}, 10\text{k}, 50\text{k}, 100\text{k}\}$ facts |
| **Candidate Architecture** | Independent | UMR-TPG, V-UMR, DRS-Graph |
| **Query Latency (p50, p95, p99)** | Dependent | Single-core CPU latency in milliseconds (ms) |
| **Resident Set Size (RSS)** | Dependent | Memory footprint delta in megabytes (MB) |
| **Bytes per Fact** | Dependent | $\Delta\text{RSS} / N$ |
| **Insertion Throughput** | Dependent | Insertions per second (ops/sec) |
| **GPU VRAM Allocation** | Dependent | Must strictly measure **$0.0\text{ MB}$** |

---

## 4. Falsification Criteria & Engineering Thresholds

| Candidate | Metric | Engineering Target | Falsification Boundary (Failure) | Epistemological Status |
|---|---|---|---|---|
| **UMR-TPG** | Total RSS at $N=100\text{k}$ | $\le 200\text{ MB}$ | $> 500\text{ MB}$ | **Engineering Hypothesis** |
| **UMR-TPG** | Query Latency ($p95$) | $\le 5.0\text{ ms}$ | $> 15.0\text{ ms}$ | **Engineering Hypothesis** |
| **UMR-TPG** | Memory per Fact | $\le 350\text{ bytes}$ | $> 1,000\text{ bytes}$ | **Engineering Hypothesis** |
| **V-UMR** | Total RSS at $N=100\text{k}$ | $\le 350\text{ MB}$ | $> 800\text{ MB}$ | **Engineering Hypothesis** |
| **All** | GPU VRAM Allocated | **$0.0\text{ MB}$** | $> 0.0\text{ MB}$ (Breaks CPU invariant) | **Canonical Invariant** |

---

## 5. Execution Environment & Profiling Standards

1. Benchmarks must run on CPU isolated to a single core to simulate the 20W TDP resource budget.
2. Memory profiling must use `tracemalloc` and OS-level RSS measurements (`psutil`).
3. Latency measurements must exclude warm-up cycles (minimum 100 warm-up runs, 1,000 measured iterations).
