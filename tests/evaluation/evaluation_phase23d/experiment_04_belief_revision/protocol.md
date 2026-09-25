# Phase 23-D — EXP-04: Belief Revision & Contradiction Protocol

> **Experiment ID:** EXP-04  
> **Status:** `[EVALUATION PROTOCOL SPECIFICATION]`  
> **Governing Documents:** `candidate_spec.md`, `metrics.md`, `research_baseline.md`, `AGENTS.md` §0, §6, §7  
> **Target Subsystems:** Semantic Substrates (UMR-TPG, V-UMR, DRS-Graph)  
> **Production Boundary:** Isolated under `tests/evaluation/evaluation_phase23d/experiment_04_belief_revision/`. Zero mutations to `src/core/**`.

---

## 1. Scientific Objective

Experiment 04 evaluates the capacity of candidate semantic substrates to maintain **epistemic consistency** through non-monotonic belief revision and dependency-directed retraction. 

Specifically, this benchmark tests:
1. Detecting logical and functional contradictions between assertions.
2. Managing bitemporal dimensions: **valid time** (world state interval $[t_s, t_e]$) vs. **transaction time** (system assertion timestamp $t_{\text{tx}}$).
3. Maintaining operational belief states: `IN` (currently believed) vs. `OUT` (retracted or defeated).
4. Constructing directed justification graphs (Justification DAGs) linking premise beliefs to derived beliefs.
5. Propagating retractions across multi-hop inference chains ($A \to B \to C$) upon defeat of a premise.
6. Isolating revisions to affected subgraphs while avoiding collateral retraction of independent beliefs ($\text{CRR} = 0$).
7. Preserving full immutable transaction provenance and audit history ($\text{HRR} = 1.0$).

---

## 2. Experimental Boundary & Candidate Scope

### Experimental Boundary
EXP-04 is strictly a **belief-management substrate evaluation**. It does NOT evaluate:
- Open-domain truth discovery or external commonsense knowledge.
- Natural language parsing or text tokenization.
- Emotional state, subjective consciousness, or conversational persona.
- Production runtime execution or Genesis onboarding.

Input data consists of **deterministic, structured semantic assertions**.

### Candidate Architectures
1. **UMR-TPG (Primary):** Universal Meaning Representation with Temporal-Predicate Graph and explicit Justification DAG.
2. **V-UMR (Secondary):** Vectorized UMR with auxiliary 32D concept vectors. *Rule: Continuous vector similarity must NEVER act as the authority for logical contradiction; vectors serve solely as auxiliary indexing.*
3. **DRS-Graph (Control):** Discourse Representation Theory graph with box-universe conditions and formal accessibility paths.

---

## 3. Mathematical State Model

Each assertion $A_i$ is modeled as a tuple:
$$A_i = \langle \text{id}, \text{predicate}, \text{args}, \text{polarity}, \text{conceiver}, \mathcal{T}_{\text{valid}}, t_{\text{tx}}, \mathcal{S}_{\text{op}}, \mathcal{J}, \delta \rangle$$

Where:
- $\text{id} \in \Sigma^*$: Unique assertion identifier.
- $\text{predicate} \in \mathcal{P}$: Relational or property predicate (e.g. `LOCATED_IN`, `HAS_STATUS`).
- $\text{args} \in \mathcal{E}^k$: Ordered tuple of entity and value arguments.
- $\text{polarity} \in \{\text{True}, \text{False}\}$: Positive assertion vs. logical negation.
- $\text{conceiver} \in \mathcal{C}$: Epistemic agent asserting the proposition (e.g. `User`, `Admin`, `LuciaInference`).
- $\mathcal{T}_{\text{valid}} = [t_s, t_e] \subset \mathbb{R}$: Valid-time interval during which the assertion holds in the world.
- $t_{\text{tx}} \in \mathbb{N}$: Monotonically increasing transaction sequence step.
- $\mathcal{S}_{\text{op}} \in \{\text{IN}, \text{OUT}\}$: Current operational epistemic status.
- $\mathcal{J} \subseteq \text{ID}$: Set of justification premise IDs ($A_j \in \mathcal{J} \implies A_j \text{ entails } A_i$). If $\mathcal{J} = \emptyset$, $A_i$ is a primitive assumption.
- $\delta \in \text{ID} \cup \{\text{None}\}$: Defeater identifier (the assertion or retraction causing $A_i$ to become `OUT`).

### Contradiction Rule
Two assertions $A_1$ and $A_2$ are in formal contradiction if and only if:
1. $A_1.\text{predicate} == A_2.\text{predicate}$
2. $A_1.\text{args}[0] == A_2.\text{args}[0]$ (same subject/entity)
3. Either:
   - $A_1.\text{args} == A_2.\text{args}$ and $A_1.\text{polarity} \ne A_2.\text{polarity}$ (Direct Negation).
   - $A_1.\text{args}[1] \ne A_2.\text{args}[1]$ for single-valued functional relations (Mutually Exclusive Values).
4. $\mathcal{T}_{\text{valid}}(A_1) \cap \mathcal{T}_{\text{valid}}(A_2) \ne \emptyset$ (Valid-Time Overlap).

*Crucial Boundary:* If $\mathcal{T}_{\text{valid}}(A_1) \cap \mathcal{T}_{\text{valid}}(A_2) = \emptyset$, the assertions represent sequential historical states and do NOT contradict.

---

## 4. Evaluation Metrics

### 1. Contradiction Detection Recall (CDR)
$$\text{CDR} = \frac{|\mathcal{C}_{\text{detected}} \cap \mathcal{C}_{\text{oracle}}|}{|\mathcal{C}_{\text{oracle}}|}$$
Proportion of true contradictions identified by the substrate.

### 2. Revision Correctness (RC)
$$\text{RC} = \frac{1}{|A|} \sum_{a \in A} \mathbb{I}(\mathcal{S}_{\text{op}}(a) == \mathcal{S}_{\text{oracle}}(a))$$
Accuracy of the final operational belief status (`IN` vs `OUT`) across all assertions.

### 3. Dependency Propagation Accuracy (DPA)
$$\text{DPA} = \frac{1}{|\mathcal{D}_{\text{oracle}}|} \sum_{d \in \mathcal{D}_{\text{oracle}}} \mathbb{I}(\mathcal{S}_{\text{op}}(d) == \text{OUT})$$
Proportion of dependent beliefs in the downstream justification DAG that are successfully retracted when their premise is defeated.

### 4. Collateral Retraction Rate (CRR)
$$\text{CRR} = \frac{|\{u \in \mathcal{U}_{\text{oracle}} \mid \mathcal{S}_{\text{op}}(u) == \text{OUT}\}|}{|\mathcal{U}_{\text{oracle}}|}$$
Proportion of uncontradicted, independent assertions erroneously retracted during belief revision. Target: $\text{CRR} = 0.0$.

### 5. Historical Retention Rate (HRR)
$$\text{HRR} = \frac{|\text{Retrievable Historical Assertions}|}{|\text{Total Assertions Introduced}|}$$
Guarantee that defeated or retracted assertions are preserved immutably in the transaction ledger rather than destructively deleted. Target: $\text{HRR} = 1.0$.

### 6. Revision Latency ($\Delta t_{\text{rev}}$)
Wall-clock elapsed execution time (ms) for contradiction detection and JTMS dependency propagation.

---

## 5. Preregistered Gates & Falsification Boundaries

| Metric | Target Gate | Falsification Boundary (Failure) |
|---|---|---|
| **Contradiction Detection Recall (CDR)** | $\ge 0.98$ | $< 0.95$ |
| **Conflicting Co-existence in `IN`** | **0 assertions** | $> 0$ (Leaves unresolved contradiction) |
| **Historical Retention Rate (HRR)** | **$1.000$** | $< 1.000$ (Destructive deletion) |
| **Collateral Retraction Rate (CRR)** | **$0.000$** | $> 0.000$ (Over-retraction) |
| **Dependency Propagation Accuracy (DPA)** | **$1.000$** | $< 1.000$ (Orphaned invalid inferences) |

---

## 6. Critical Falsification Invariants

A candidate substrate is declared **FAILED** if any of the following occur:
1. Two contradictory assertions within the same valid interval both remain in operational state `IN`.
2. Retraction of premise $A$ causes an independent assertion $X$ ($X \notin \text{Descendants}(A)$) to become `OUT`.
3. An assertion is permanently deleted from the repository upon being defeated.
4. Repeated revision ($P \to \neg P \to P$) erases transaction history or previous provenance.
5. Non-overlapping temporal intervals are erroneously flagged as logical contradictions.
6. Downstream dependency propagation halts prematurely before reaching all leaves of the justification DAG.
7. Continuous vector distance is used to override symbolic contradiction rules.
