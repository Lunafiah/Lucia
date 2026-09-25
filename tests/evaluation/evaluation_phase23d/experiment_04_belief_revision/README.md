# Experiment 04 — Contradiction & Belief Revision

> **Track:** EXP-04  
> **Target Capability:** Non-Monotonic Belief Revision & Dependency-Directed Retraction  
> **Status:** `[EVALUATION PROTOCOL SPECIFICATION]`  
> **Governing Documents:** `candidate_spec.md`, `metrics.md`, `research_baseline.md`

---

## 1. Scientific Context & Hypothesis Formulation

In an evolving companionship relationship, the user frequently updates, qualifies, or directly contradicts previously asserted facts:
- Turn 1: *"I work remotely from Hanoi."*
- Turn 10: *"I recently moved to Da Nang for a new office role."*

A naive memory system simply overwrites the latest sentence, accumulating contradictory assertions in memory. A classical deductive system requires re-parsing the entire dialogue history from scratch.

Phase 23-D evaluates whether candidate semantic graphs can support **localized, dependency-directed non-monotonic belief revision** (e.g. via Justification-Based Truth Maintenance / JTMS) on edge hardware.

### 1.1 Testable Hypotheses

- **$H_1$ (Dependency-Directed Sound Retraction in UMR-TPG):**  
  When a premise is contradicted, UMR-TPG will traverse its directed justification DAG, retracting only the invalid premise and its deductive dependents, while retaining $\ge 98\%$ of unaffected facts ($\text{RUF} \ge 0.98$) in $\le 2.0\text{ ms}$ on CPU.
- **$H_0$ (Cascading Inconsistency Null Hypothesis):**  
  Without re-parsing the whole graph, localized retraction either leaves orphaned contradictory inferences (soundness $< 1.0$) or causes over-retraction of valid facts ($\text{RUF} < 0.90$).
- **$H_2$ (V-UMR Dual-State Synchronization Overhead):**  
  In V-UMR, updating the graph topology requires recomputing or unbinding corresponding node vectors and subgraph hypervectors, increasing revision latency by $\ge 50\%$ relative to UMR-TPG.
- **$H_3$ (DRS-Graph Consistency Check Cost):**  
  DRS-Graph guarantees zero contradictions via formal box consistency, but its verification time scales quadratically $\mathcal{O}(|C|^2)$ with the number of box conditions.

---

## 2. Experimental Setup & Contradiction Test Suite

### 2.1 Contradiction Scenarios
The benchmark evaluates 50 structured contradiction scenarios categorized into three types:
1. **Direct Property Negation:**
   Premise: `HAS_STATUS(User, TIRED)` $\to$ Update: `NOT(HAS_STATUS(User, TIRED))`.
2. **Mutually Exclusive Value Mutation:**
   Premise: `LOCATED_IN(User, City_A)` $\to$ Update: `LOCATED_IN(User, City_B)` (where `City_A != City_B` and `LOCATED_IN` has cardinality 1).
3. **Temporal Supersession:**
   Premise: `SCHEDULED_FOR(Meeting, 14:00)` $\to$ Update: `RESCHEDULED_TO(Meeting, 16:00)`.

### 2.2 Dependency Depth
For each contradicted premise, the scenario injects a chain of downstream dependent inferences of depth $D_{\text{dep}} \in \{1, 3, 5\}$:
- Premise: *User lives in Da Nang.*
- Dep 1: $\to$ *User is in Vietnam timezone.*
- Dep 2: $\to$ *User's local time is UTC+7.*
- Dep 3: $\to$ *Lucia schedules reminders according to UTC+7.*

---

## 3. Manipulated & Measured Variables

| Variable | Type | Description |
|---|---|---|
| **Contradiction Type** | Independent | Direct Negation, Value Mutation, Temporal Supersession |
| **Dependency Chain Depth ($D_{\text{dep}}$)** | Independent | $D_{\text{dep}} \in \{1, 3, 5\}$ |
| **Background Fact Count ($N_{\text{bg}}$)** | Independent | $100, 1,000, 5,000$ independent uncontradicted facts |
| **Retained Unaffected Facts ($\text{RUF}$)** | Dependent | Ratio of valid unaffected facts retained post-revision |
| **Invalidation Soundness** | Dependent | Ratio of invalidated dependent facts successfully retracted |
| **Revision Latency ($\Delta t_{\text{rev}}$)** | Dependent | Wall-clock execution time for belief revision (ms) |

---

## 4. Falsification Criteria & Thresholds

| Candidate | Metric | Passing Threshold | Falsification Boundary (Failure) | Epistemological Status |
|---|---|---|---|---|
| **UMR-TPG** | $\text{RUF}$ | $\ge 0.98$ | $< 0.95$ | **Preregistered Gate** |
| **UMR-TPG** | Invalidation Soundness | **$1.00$** ($100\%$) | $< 1.00$ (Leaves contradiction) | **Formal Logical Axiom** |
| **UMR-TPG** | Revision Latency | $\le 2.0\text{ ms}$ (CPU) | $> 5.0\text{ ms}$ | **Engineering Hypothesis** |
| **V-UMR** | $\text{RUF}$ | $\ge 0.98$ | $< 0.95$ | **Preregistered Gate** |
| **DRS-Graph** | Invalidation Soundness | **$1.00$** | $< 1.00$ | **Formal Logical Axiom** |

> [!IMPORTANT]
> **Production Boundary:**  
> The JTMS algorithms evaluated in this experiment are self-contained test harnesses located strictly in the evaluation folder. No JTMS engine is added to `src/core/` during this phase.
