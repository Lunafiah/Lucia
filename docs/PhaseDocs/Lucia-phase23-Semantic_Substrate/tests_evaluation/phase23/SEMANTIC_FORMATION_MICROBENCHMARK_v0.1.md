# P23 Semantic Formation Microbenchmark v0.1

> **Preregistered Evaluation Specification & Benchmark Protocol for Phase 23**  
> **Status:** `[RESEARCH BENCHMARK SPECIFICATION / PREREGISTERED]`  
> **Governance Authority:** `AGENTS.md` §0, §6, §7; `docs/L1_INVARIANTS.md`; `tests/evaluation/phase23/SEMANTIC_STATE_CONTRACT_v0.2.md`  
> **Evaluation Harness Path:** `tests/evaluation/phase23/`  
> **Artifacts Destination:** `evaluation_artifacts/phase23/`  
> **Production Safety Invariant:** 100% Isolated. Zero modifications to `src/core/**`, `electron/**`, runtime lifecycle, or `data/profile.json` (`{"is_onboarded": false}`).

---

## 1. Executive Summary & Benchmark Purpose

This document preregisters the benchmark protocol, metric definitions, test suites, negative controls, and falsification criteria for **Phase 23 Semantic Formation Microbenchmark v0.1**.

The benchmark isolates and evaluates the central unresolved gap established in `SEMANTIC_STATE_CONTRACT_v0.2.md`:

```text
Continuous Cognitive State
          │ (PAD ODE + Somatic Load + Relational Tier)
          ▼
Communicative Intention
          │ (Goal, Stance, Epistemic Drive)
          ▼
Semantic Formation Layer [BENCHMARK TARGET]
          │
          ▼
Grounded Variable-Size Semantic State
          │ (Referents, Roles, Negation, Nested Propositions)
          ▼
Downstream Renderers (Symbolic / Somatic / Acoustic / Linguistic)
```

The benchmark empirically evaluates the **six core Phase 23 unknowns (U1–U6)** without modifying production architecture, without deploying an LLM as a hidden cognitive oracle, and keeping surface natural-language rendering strictly decoupled from semantic-state evaluation.

---

## 2. Benchmark Architecture & Candidate Matrix

### 2.1 Evaluated Candidate Representations

The benchmark compares the inherited Phase 22 baseline against structured and symbolic alternatives. No representation is assumed to be universally optimal:

| Candidate ID | Representation Family | Description | Historical / Theoretical Basis |
|---|---|---|---|
| **C1** | Pure Structured Frame | Flat dataclass / JSON slot-value frame | P22-SC validated baseline (~120–180 bytes) |
| **C2** | Typed Relational Graph | Directed labeled graph ($V, E$) with typed semantic relations | P22-RI / P22-SC relational graph |
| **C3** | Dense HDC Hypervector | Single $D=1024$ continuous hypervector superposition | P22-SC historical negative control (crosstalk for $N > 5$) |
| **C4** | **Hybrid Graph + HDC Gestalt** | **Inherited P22 baseline**: Typed Graph nodes bound to HDC hypervector | **P22-SC validated optimal relational baseline** |
| **C5** | Tensor Product Representation (TPR) | Role/filler tensor outer-product binding matrix | Smolensky classical compositional connectionist baseline |
| **C6** | Grammar-Constrained State Machine | Deterministic transition network over discrete semantic types | Non-neural symbolic reference control |

### 2.2 Decoupled Downstream Evaluation Consumers

Semantic state validity is evaluated across three decoupled consumers without generating conversational text:
- **D0 (Symbolic Structural Validator):** Graph isomorphism, schema conformance, and referential integrity checker.
- **D1 (Embodiment Policy Consumer):** Direct mapping to non-verbal parameters (Live2D blendshape weights, somatic reaction latencies, vocal prosody F0/energy shifts).
- **D2 (Surface Realization Diagnostic):** Multi-language template/token decoder evaluated strictly as a readout probe, never as a cognitive authority.

---

## 3. Preregistered Evaluation Tracks (U1–U6)

```text
┌─────────────────────────────────────────────────────────────────────────────┐
│ TRACK 1 (U1): Intention → Variable-Size Semantic Structure Without LLM     │
│ TRACK 2 (U2): Persistent Entity & Event Referential Grounding               │
│ TRACK 3 (U3): C4 Representation Scalability (Recursion, Nesting, Negation)  │
│ TRACK 4 (U4): Continuous Cognitive State → Structured State Coupling       │
│ TRACK 5 (U5): Incremental State Updates, Delta Stability & Drift            │
│ TRACK 6 (U6): Autonomous Open-Domain Concept Grounding on 20W Edge          │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

### Track 1 (U1): Communicative Intention $\to$ Semantic Structure Without LLM

#### 1.1 Objective & Hypothesis
Test whether an explicit Communicative Intention vector can be deterministically expanded into a structurally valid, variable-size semantic structure without prompting or invoking an autoregressive language model.

#### 1.2 Test Cases
- **TC-U1.1 (Atomic Inform):** Direct expression of a single cognitive perception (e.g., high task cognitive load).
- **TC-U1.2 (Dyadic Collaboration):** Multi-clause communicative goal (e.g., proposing next action while acknowledging user suggestion).
- **TC-U1.3 (Epistemic Clarification):** Generating a targeted disambiguation query triggered by high internal entropy ($H > 1.2\text{ nats}$).
- **TC-U1.4 (Boundary Assertion under Rupture):** Defensively conditioned stance transition asserting relationship boundaries.

#### 1.3 Inputs & Outputs
- **Input:** Intention Tuple:
  $$\mathcal{I} = \langle \text{act\_type} \in \mathcal{A}_{\text{dialogue}}, \text{target\_entities} \subset \mathcal{E}, \text{affective\_drive} \in [-1, 1]^3, \text{relational\_tier} \in \{T_0..T_4\}, \text{epistemic\_confidence} \in [0, 1] \rangle$$
- **Output:** Formed Semantic Graph $\mathcal{S} = (V, E, \mathbf{h}_{\text{gestalt}})$.

#### 1.4 Measurable Metrics
1. **Structural Graph Validity Rate (SGVR):** Percentage of outputs satisfying formal syntactic and type constraints.
2. **Intention-Semantic Alignment Accuracy (ISAA):** F1 score of target roles and entities correctly mapped from $\mathcal{I}$ to $\mathcal{S}$.
3. **Token Independence Metric (TIM):** Verification that exactly $0$ LLM tokens were sampled or parsed ($1.0 = \text{pure non-LLM}$).
4. **Formation Latency P50 / P95:** Execution time on single CPU core.

#### 1.5 Acceptance & Falsification Criteria
- **PASS:** $\text{SGVR} \ge 95.0\%$, $\text{ISAA} \ge 85.0\%$, $\text{TIM} = 1.0$, $\text{CPU P50} \le 5.0\text{ ms}$.
- **FALSIFY U1:** If non-LLM formation produces $\text{ISAA} < 70.0\%$ or requires heuristic rules exceeding $\mathcal{O}(2^N)$ combinatorial complexity.

#### 1.6 Negative Controls
- **NC-U1.1 (Shuffled Intention):** Randomly permuting input intention attributes; must yield disjoint semantic topology.
- **NC-U1.2 (Null Affective Drive):** Zeroing affective/relational vector; semantic formation must preserve informational payload while dropping somatic modifiers.

---

### Track 2 (U2): Persistent Entity & Event Referential Grounding

#### 2.1 Objective & Hypothesis
Verify that semantic nodes generated during conversational turns remain persistently grounded to unique autobiographical episodic anchors in SDM memory and do not suffer referential collision or phantom drift.

#### 2.2 Test Cases
- **TC-U2.1 (50-Turn Longitudinal Tracking):** Tracking 5 distinct user-introduced entities across 50 conversational turns with intervening distractor turns.
- **TC-U2.2 (Multi-Session Cross-Boundary Recall):** Re-referencing an entity introduced in Session 1 during Session 3 after simulated homeostatic rest.
- **TC-U2.3 (Referential Disambiguation):** Resolving between two entities sharing surface lexical labels but possessing distinct episodic provenances.
- **TC-U2.4 (Rupture/Repair Episodic Anchoring):** Grounding relational stance changes in explicit, immutable rupture/repair memory IDs.

#### 2.3 Inputs & Outputs
- **Input:** Dialogue context with entity mentions and associated persistent memory pointer candidates $\mathcal{M}_{\text{SDM}}$.
- **Output:** Grounded semantic entities with verified provenance hashes $e_i \mapsto \text{UID}_{\text{anchor}}$.

#### 2.4 Measurable Metrics
1. **Referential Grounding Precision (RGP):** Fraction of bound entity references correctly mapped to ground-truth memory traces.
2. **Referential Grounding Recall (RGR):** Fraction of active persistent entities correctly retrieved and bound.
3. **Longitudinal Grounding Drift ($D_{50}$):** Euclidean displacement of entity coordinate representations between turn 1 and turn 50.
4. **Disambiguation Accuracy:** Correct separation of homonymous entities.

#### 2.5 Acceptance & Falsification Criteria
- **PASS:** $\text{RGP} \ge 90.0\%$, $\text{RGR} \ge 90.0\%$, $D_{50} \le 0.0500$, Disambiguation $\ge 95.0\%$.
- **FALSIFY U2:** If entity lookup error exceeds $5.0\%$ over 50 turns or across session boundaries.

#### 2.6 Negative Controls
- **NC-U2.1 (Phantom Entity Injection):** Introducing ungrounded entities without episodic provenance; system must flag as ungrounded ($\text{epistemic\_confidence} \le 0.20$).
- **NC-U2.2 (Shuffled Memory Hash):** Corrupting memory trace references; validator must reject binding rather than silently hallucinating a link.

---

### Track 3 (U3): C4 Representation Scalability Under Recursion, Nesting & Negation

#### 3.1 Objective & Hypothesis
Determine the empirical breaking point of the inherited C4 Hybrid Graph + HDC representation when subjected to recursive proposition embedding, complex role binding, and explicit negation.

#### 3.2 Test Cases
- **TC-U3.1 (Recursive Proposition Nesting, $D=1 \dots 4$):**
  - $D=1$: *"The user loves coding."*
  - $D=2$: *"Lucia notices that the user loves coding."*
  - $D=3$: *"The user realizes that Lucia understands they love coding."*
  - $D=4$: *"Lucia reflects that the user was surprised that Lucia remembered they love coding."*
- **TC-U3.2 (Complex Role/Filler Bindings):** Binding 8 distinct semantic roles simultaneously (Agent, Experiencer, Theme, Beneficiary, Instrument, Location, TemporalAnchor, Purpose).
- **TC-U3.3 (Explicit Negation & Denial):** Encoding negated propositions (*"The user did NOT request task completion"*) alongside affirmative counterparts.
- **TC-U3.4 (Modality & Uncertainty Operators):** Propositions modalized by doubt, possibility, and counterfactuals.

#### 3.3 Inputs & Outputs
- **Input:** Standardized proposition trees of varying depth $D$, role count $K$, and polarity $P \in \{+1, -1\}$.
- **Output:** Encoded candidate state vector/graph $\mathcal{S}_C$, followed by exact unbinding/decoding probe.

#### 3.4 Measurable Metrics
1. **Retrieval Fidelity by Depth ($RF_D$):** Exact match decoding accuracy for propositions at recursion depth $D$.
2. **Role/Filler Crosstalk Rate ($CR$):** Rate of attribute leaking between bound semantic slots.
3. **Negation Polarity Accuracy ($NPA$):** Correct separation between $P(X)$ and $\neg P(X)$ (must not cancel into zero vector).
4. **Superposition Signal-to-Noise Ratio (SNR):** Decoded similarity margin between target constituent and nearest distractor.

#### 3.5 Acceptance & Falsification Criteria
- **PASS for C4 Baseline:** $RF_{D=1..2} \ge 95.0\%$, $RF_{D=3} \ge 85.0\%$, $CR \le 10.0\%$, $NPA \ge 95.0\%$.
- **FALSIFY C4 Scalability (U3 Target):** If $RF_{D=3} < 80.0\%$ or if negation cancellation collapses HDC hypervector magnitude by $> 80\%$, C4 is **formally rejected** as a universal semantic representation and must be restricted or superseded.

#### 3.6 Negative Controls & Ablations
- **Ablation A-U3.1 (Standalone HDC C3):** Validates reproduction of Phase 22-SC superposition collapse ($N > 5$).
- **Ablation A-U3.2 (Pure Graph C2):** Graph without HDC gestalt; checks if graph handles recursion without vector capacity limits.

---

### Track 4 (U4): Continuous Cognitive State $\to$ Structured State Coupling

#### 4.1 Objective & Hypothesis
Benchmark the dynamical interface between the continuous Coupled MT-LNN limbic ODE ($\mathbf{x}_{\text{PAD}}(t) \in [-1, 1]^3$) and the discrete topology of the semantic graph, ensuring coupling does not induce state flapping or ODE instability.

#### 4.2 Test Cases
- **TC-U4.1 (Acute Stress Perturbation):** Injecting sudden negative valence/arousal shock into the ODE and observing semantic priority reallocation.
- **TC-U4.2 (Somatic Fatigue Drain):** Decreasing metabolic energy $e(t)$ to observe conversational latency injection and semantic compression.
- **TC-U4.3 (Hysteresis & State Transition Deadband):** Oscillating input stimuli near classification thresholds ($P \approx 0.0, A \approx 0.5$).
- **TC-U4.4 (Lyapunov Stability Verification):** 1,000-turn continuous integration verifying that semantic feedback does not destabilize limbic eigenvalues.

#### 4.3 Inputs & Outputs
- **Input:** Continuous limbic trajectory $\mathbf{x}_{\text{PAD}}(t)$ and homeostatic state vector $\mathbf{s}_{\text{homeo}}(t)$.
- **Output:** Modulated semantic graph with continuous node activation weights $\mathbf{w}_V \in [0, 1]^{|V|}$ and execution latencies.

#### 4.4 Measurable Metrics
1. **Downstream Decision Flapping Rate ($DFR$):** Rapid oscillation of semantic stance across adjacent turns under steady or slowly drifting input.
2. **Maximal Lyapunov Exponent ($\lambda_{\max}$):** Mathematical stability check of limbic fast loop under semantic coupling (must be $\le 0.0$).
3. **Contradiction Recovery Turns:** Time required to adapt semantic structure upon genuine environmental reversal.
4. **Coupling Latency:** Time consumed by the continuous-to-discrete modulation function.

#### 4.5 Acceptance & Falsification Criteria
- **PASS:** $DFR \le 5.0\%$, $\lambda_{\max} \le 0.0000$, Contradiction Recovery $\le 1.0\text{ turn}$, Latency $\le 0.5\text{ ms}$.
- **FALSIFY U4:** If continuous modulation induces $DFR > 10.0\%$ or drives limbic variance unbounded ($\text{Var}(\text{PAD}) \to \infty$).

#### 4.6 Negative Controls
- **NC-U4.1 (Uncoupled Open-Loop Control):** Disconnecting limbic feedback; confirms semantic structure operates stably without emotion (baseline neutrality).
- **NC-U4.2 (Zero-Deadband Raw Injection):** Coupling raw PAD without hysteresis; demonstrates baseline flapping vulnerability.

---

### Track 5 (U5): Incremental State Updates, Delta Stability & Drift

#### 5.1 Objective & Hypothesis
Benchmark whether an existing semantic state can be updated incrementally via localized graph deltas ($\Delta \mathcal{S}_t$) across 100 conversational turns without causing semantic drift, fact corruption, or unbounded memory growth.

#### 5.2 Test Cases
- **TC-U5.1 (Single-Attribute Delta):** Modifying a single node attribute (e.g., updating user's current project status) while keeping all other relationships static.
- **TC-U5.2 (Belief Correction & Rupture Repair):** Overwriting an outdated belief with an explicit contradictory observation.
- **TC-U5.3 (100-Turn Longitudinal Accumulation):** Continuously updating the state graph over 100 turns with alternating information density.
- **TC-U5.4 (Memory Compaction Under Budget SLA):** Pruning weak/unreinforced transient nodes when state memory exceeds budget limit.

#### 5.3 Inputs & Outputs
- **Input:** Prior Semantic State $\mathcal{S}_t$ and incoming delta observation $\Delta O_{t+1}$.
- **Output:** Updated Semantic State $\mathcal{S}_{t+1} = \text{ApplyUpdate}(\mathcal{S}_t, \Delta O_{t+1})$.

#### 5.4 Measurable Metrics
1. **Retention of Unchanged Facts ($RUF$):** Percentage of un-modified nodes/edges remaining strictly invariant after delta application.
2. **Historical Semantic Drift ($\Delta_{\text{drift}}$):** Cosine/graph edit distance divergence on historical facts over 100 turns.
3. **Structural Graph Bloat Ratio ($SGBR$):** Ratio of total node/edge count growth relative to actual information volume introduced.
4. **Delta Application CPU Latency:** Time required to apply localized graph transformation.

#### 5.5 Acceptance & Falsification Criteria
- **PASS:** $RUF \ge 98.0\%$, $\Delta_{\text{drift}} \le 0.0500$, $SGBR \le 1.20\times$, Latency $\le 2.0\text{ ms}$.
- **FALSIFY U5:** If incremental updating yields $RUF < 90.0\%$ or exhibits runaway memory bloat ($\mathcal{O}(T^2)$).

#### 5.6 Negative Controls
- **NC-U5.1 (Rebuild From Scratch):** Reconstructing the entire semantic state from raw dialogue history every turn; records computational and token cost for baseline comparison.
- **NC-U5.2 (Open-Loop Latent Addition):** Accumulating continuous float vectors without graph structure (reproducing Phase 22-SSF failure).

---

### Track 6 (U6): Autonomous Open-Domain Concept Grounding on 20W Edge

#### 6.1 Objective & Hypothesis
Evaluate whether novel, open-domain concepts can be inserted into the structured semantic state and bound to existing conceptual hierarchies without calling an LLM API or running large autoregressive decoders on the 20W edge CPU.

#### 6.2 Test Cases
- **TC-U6.1 (Out-of-Vocabulary Concept Insertion):** Introducing a novel domain term (e.g., specific software library, rare hobby) with contextual usage clues.
- **TC-U6.2 (Taxonomic Placement):** Inferring the correct parent category and semantic relations for the novel concept.
- **TC-U6.3 (Property Inheritance):** Verifying that the newly inserted concept inherits default attributes from its parent category.
- **TC-U6.4 (Hardware SLA Constraint):** Executing all concept parsing and insertion operations within the strict $\le 30\text{ ms}$ CPU budget.

#### 6.3 Inputs & Outputs
- **Input:** Dialogue turn containing novel concept $C_{\text{new}}$ and minimal syntactic context.
- **Output:** Updated Concept Hierarchy Graph $\mathcal{G}_{\text{concept}} \cup \{C_{\text{new}}\}$ with typed categorical edges.

#### 6.4 Measurable Metrics
1. **Taxonomic Placement Accuracy ($TPA$):** Percentage of novel concepts correctly attached to their nearest valid ontology node.
2. **Zero-LLM Autonomy Ratio ($ZAR$):** Fraction of concept acquisitions completed without calling external or local LLMs ($1.0 = 100\%$).
3. **Peak CPU Execution Latency:** Milliseconds spent on single CPU core.
4. **VRAM Allocation Invariant:** GPU memory consumed ($0.0\text{ MB}$ required).

#### 6.5 Acceptance & Falsification Criteria
- **PASS:** $TPA \ge 80.0\%$, $ZAR = 1.000$, $\text{Latency} \le 30.0\text{ ms}$, $\text{VRAM} = 0.0\text{ MB}$.
- **FALSIFY U6:** If novel concept grounding requires an LLM for semantic validity or exceeds 50 ms CPU latency.

#### 6.6 Negative Controls
- **NC-U6.1 (Random Concept Insertion):** Randomly attaching novel concepts to ontology nodes; establishes statistical lower-bound for $TPA$.
- **NC-U6.2 (LLM Oracle Reference):** Running a 7B local SLM to perform concept classification strictly as an empirical upper-bound benchmark, not an active subsystem.

---

## 4. Master Acceptance & Falsification Gate Matrix

| Gate ID | Track | Focus Metric | Preregistered Requirement | Falsification Boundary |
|---|---|---|---|---|
| **G-MB-1** | Track 1 (U1) | Structural Graph Validity Rate (SGVR) | $\ge 95.0\%$ | $< 80.0\%$ |
| **G-MB-2** | Track 1 (U1) | Intention-Semantic Alignment (ISAA) | $\ge 85.0\%$ | $< 70.0\%$ |
| **G-MB-3** | Track 2 (U2) | Referential Grounding Precision (RGP) | $\ge 90.0\%$ | $< 80.0\%$ |
| **G-MB-4** | Track 2 (U2) | 50-Turn Longitudinal Drift ($D_{50}$) | $\le 0.0500$ | $> 0.1500$ |
| **G-MB-5** | Track 3 (U3) | Nested Proposition Fidelity @ $D=3$ ($RF_3$) | $\ge 85.0\%$ | $< 70.0\%$ (Rejects C4) |
| **G-MB-6** | Track 3 (U3) | Negation Polarity Accuracy ($NPA$) | $\ge 95.0\%$ | $< 85.0\%$ |
| **G-MB-7** | Track 4 (U4) | Decision Flapping Rate ($DFR$) | $\le 5.0\%$ | $> 10.0\%$ |
| **G-MB-8** | Track 4 (U4) | Limbic Lyapunov Exponent ($\lambda_{\max}$) | $\le 0.0000$ (Stable) | $> 0.0000$ (Divergent) |
| **G-MB-9** | Track 5 (U5) | Fact Retention After Delta ($RUF$) | $\ge 98.0\%$ | $< 90.0\%$ |
| **G-MB-10**| Track 5 (U5) | Historical Semantic Drift ($\Delta_{\text{drift}}$) | $\le 0.0500$ | $> 0.1500$ |
| **G-MB-11**| Track 6 (U6) | Taxonomic Placement Accuracy ($TPA$) | $\ge 80.0\%$ | $< 65.0\%$ |
| **G-MB-12**| Hardware | CPU Latency P50 / GPU VRAM Allocation | $\le 5.0\text{ ms}$ / $0.0\text{ MB}$ | $> 30.0\text{ ms}$ / $> 0.0\text{ MB}$ |

---

## 5. Hardware Constraints, Reproducibility & Governance Discipline

### 5.1 Hardware Discipline (20-Watt Local Edge Profile)
- **Execution Target:** Single local CPU thread (Intel i7 / AMD Ryzen laptop class).
- **GPU Invariant:** **Strictly $0.0\text{ MB}$ VRAM allocated.** CUDA contexts must not be initialized during microbenchmark runs.
- **Total Compute Budget:** Entire 6-track benchmark evaluation must execute in $\le 60\text{ seconds}$ on CPU.

### 5.2 Deterministic Reproducibility
- **Fixed Random Seeds:** All stochastic evaluations and synthetic test generators must execute across five preregistered seeds:
  $$\mathcal{S}_{\text{seeds}} = \{42, 1337, 2026, 7113, 8421\}$$
- **Zero Internet Access:** The benchmark harness operates 100% offline with zero network socket binding.

### 5.3 Production Safety Guarantees (`AGENTS.md` §0, §6, §8)
- Zero lines in `src/core/**` or `electron/**` are imported with mutation rights.
- All evaluation scripts and test runners reside exclusively under `tests/evaluation/phase23/`.
- All benchmark artifacts, JSON logs, and telemetry are output strictly to `evaluation_artifacts/phase23/`.
- Canonical state persistence in `data/profile.json` remains bit-exact: `{"is_onboarded": false}`.
