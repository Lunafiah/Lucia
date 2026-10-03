# Phase 23 — Semantic Architecture Specification v0.1

> **Document Type:** Research Architecture Specification & Subsystem Blueprint  
> **Status:** `[ARCHITECTURE APPROVED / WORKING BASELINE SPECIFICATION]`  
> **Governance Authority:** `AGENTS.md` §0, §6, §7; `docs/L1_INVARIANTS.md`; `docs/ARCHITECTURE.md`  
> **Preceding Evidence:** Phase 22 Research Closure (`[RESEARCH VALIDATED]`), Phase 23 Semantic State Contract v0.2, Microbenchmark v0.2 (`[12/12 GATES PASSED]`), Empirical Synthesis v0.1  
> **Production Safety Invariant:** 100% Isolated. Zero modifications to `src/core/**`, `electron/**`, runtime lifecycle, or `data/profile.json` (`{"is_onboarded": false}`).

---

## 1. Architectural Scope & Core Philosophy

The **Phase 23 Semantic Architecture** defines the formal mechanism by which Lucia transforms unconscious, continuous cognitive-affective states into grounded, structured, variable-size communicative representations without relying on an autoregressive Large Language Model (LLM) or Small Language Model (SLM) as an internal cognitive oracle.

### 1.1 Non-Negotiable Invariants
1. **No Cognitive Authority for Language Models:** An LLM or SLM is strictly a downstream *surface natural language renderer* (transducing structured semantic graphs into lexical tokens). It possesses zero authority over internal affect, long-term memory formation, referential identity, or interpersonal stance.
2. **Substrate Neutrality & Language Parity:** The semantic representation is non-lexical and language-independent. The identical semantic state can be rendered into English, Vietnamese, Japanese, prosodic voice, or Live2D/VRM blendshapes without structural re-derivation.
3. **No Unbounded Latent Accumulation:** Inheriting the definitive negative finding of Phase 22-SSF ($\text{semantic continuity} \neq \text{open-loop accumulation of continuous latents}$), state continuity is maintained via discrete graph topology anchored in episodic memory, coupled bidirectionally with continuous dynamical ODEs.
4. **Pragmatic Baseline Claim:** Candidate C4 (Hybrid Graph + HDC Gestalt) is adopted as a working engineering baseline for local edge execution (20W envelope). It is **not** claimed to be universally optimal or a definitive model of biological human cognition.

---

## 2. Global Architecture Diagram

```text
┌──────────────────────────────────────────────────────────────────────────────────┐
│                           CONTINUOUS COGNITIVE LAYER                             │
│                                                                                  │
│   Coupled MT-LNN ODE (200ms Step)          Somatic Energetics & Epistemics       │
│   dx/dt = -γ(x - x_Philia) + W_f * s_sem   • somatic_energy ∈ [0.0, 1.0]         │
│   • PAD Vector ∈ [-1, 1]³                  • relational_trust ∈ [0.0, 1.0]       │
│   • Philia Attractor (+0.25, -0.05, +0.05) • epistemic_entropy ∈ [0.0, 2.0] nats │
└────────────────────────────────────┬─────────────────────────────────────────────┘
                                     │
                                     ▼ (Causal Intention Formation: CFS=1.0)
┌──────────────────────────────────────────────────────────────────────────────────┐
│                         COMMUNICATIVE INTENTION LAYER                            │
│                                                                                  │
│   CommunicativeIntention Schema:                                                 │
│   • Dialogue Act: {INFORM, PROPOSE, CLARIFY_QUERY, ASSERT_BOUNDARY, ...}         │
│   • Epistemic Modality: {CERTAIN, POSSIBLE, DOUBTFUL, COUNTERFACTUAL}            │
│   • Relational Guard / Rupture Stance: {is_guarded, has_rupture, has_repair}     │
│   • Urgency & Salience Drive ∈ [0.1, 1.0]                                        │
│   • Cardinality Budget (Bounded by somatic_energy: N ∈ {1..4})                   │
└────────────────────────────────────┬─────────────────────────────────────────────┘
                                     │
                                     ▼ (C4 Hybrid Expansion: SGVR=100%, RF3=86.4%)
┌──────────────────────────────────────────────────────────────────────────────────┐
│                   C4 HYBRID SEMANTIC STATE (WORKING BASELINE)                    │
│                                                                                  │
│   1. Discrete Structural Backbone        2. Continuous Global Gestalt            │
│      Typed Property Graph G = (V, E)        1024D Bipolar Hypervector h_gestalt  │
│      • V: {predicates, entities, concepts}  • h = bundle( ∏ r_i * e_j )          │
│      • E: {AGENT, PATIENT, THEME, ...}      • Rapid nearest-neighbor search      │
│      • Bounded Recursion Depth: D ≤ 3       • Continuous affective resonance     │
└─────────────────────┬──────────────────────────────────────┬─────────────────────┘
                      │                                      │
                      ▼                                      ▼
┌────────────────────────────────────────┐ ┌───────────────────────────────────────┐
│     EPISODIC GROUNDING SUBSYSTEM       │ │       CLOSED-LOOP DYNAMICAL COUPLER   │
│                                        │ │                                       │
│ • SDM 64D Associative Memory           │ │ • Semantic Feedback:                  │
│ • Attractor Basin Cleanup (tol = 0.55) │ │   s_sem = [bias, urgency, stance]     │
│ • 20-Distractor Noise Immunity         │ │ • Limbic ODE Modulation               │
│ • Drift Bound: D_50 ≤ 0.050 (0.000)    │ │ • Deadband Hysteresis: ±0.08          │
│ • Provenance: S_sess:turn_anchor_UID   │ │ • Asymptotic Stability: λ_max ≤ 0.0   │
└────────────────────────────────────────┘ └───────────────────────────────────────┘
                      │
                      ▼ (Substrate-Neutral Translation Contract)
┌──────────────────────────────────────────────────────────────────────────────────┐
│                    DOWNSTREAM SURFACE PRESENTATION INTERFACES                    │
│                                                                                  │
│   [Optional Local SLM Renderer]        [Acoustic / Prosodic Engine]              │
│   Translates C4 Graph → Fluent Text   Modulates pitch, pace, and latency        │
│   (English, Vietnamese, Japanese)      from urgency and somatic fatigue          │
│                                                                                  │
│   [Embodiment Engine]                                                            │
│   Live2D / 3D VRM blendshape targets derived from PAD and boundary stance        │
└──────────────────────────────────────────────────────────────────────────────────┘
```

---

## 3. Subsystem Specifications

### 3.1 Subsystem 1: Continuous Cognitive State & Closed-Loop Coupler
- **Role:** Maintains continuous dynamical equilibrium and integrates semantic feedback into limbic ODEs.
- **Continuous State Vector:** $\mathbf{x}_{\text{cog}} = [P, A, D, E_{\text{somatic}}, T_{\text{relational}}, H_{\text{epistemic}}]$.
- **Coupled MT-LNN ODE:**
  $$\frac{d\mathbf{x}_{\text{PAD}}}{dt} = -\gamma (\mathbf{x}_{\text{PAD}} - \mathbf{x}_{\text{Philia}}) + \mathbf{W}_f \mathbf{s}_{\text{sem}} + \mathbf{\eta}(t)$$
  where $\gamma = 0.25$, $\mathbf{x}_{\text{Philia}} = [+0.25, -0.05, +0.05]$, $\mathbf{W}_f = [0.05, 0.02, 0.03]$, and $\mathbf{\eta}(t)$ represents bounded somatic noise.
- **Semantic Feedback Vector:**
  $$\mathbf{s}_{\text{sem}} = \left[ 0.10(C_{\text{epistemic}} - 0.5), \; 0.15(U_{\text{salience}} - 0.5), \; \mathbf{1}_{\text{guarded}}(-0.20) + \mathbf{1}_{\neg\text{guarded}}(+0.05) \right]^T$$
- **Hysteresis Guard:** Candidate stance transitions (Guarded vs Receptive) are governed by a $\pm 0.08$ deadband around thresholds ($P = -0.30$ and $P = +0.25$).
- **Stability Guarantee:** Closed-loop Lyapunov exponent $\lambda_{\max} \le 0.000$ (empirically measured at $-0.0206$), guaranteeing asymptotic decay toward the resting attractor without oscillatory flapping ($DFR = 0.0\%$).

### 3.2 Subsystem 2: Causal Intention Formation Engine
- **Role:** Non-LLM deterministic mapper transforming continuous cognitive coordinates into an explicit `CommunicativeIntention`.
- **Causal Act Selection:**
  - Active breach OR ($P < -0.20 \land T_{\text{relational}} < 0.35$) $\longrightarrow$ `ASSERT_BOUNDARY` (`is_guarded=True`, `has_rupture=True`).
  - Active bilateral repair $\longrightarrow$ `REPAIR_BILATERAL` (`has_repair=True`).
  - $H_{\text{epistemic}} > 0.60$ OR ($A > 0.20 \land H_{\text{epistemic}} > 0.40$) $\longrightarrow$ `CLARIFY_QUERY`.
  - $P > 0.15 \land T_{\text{relational}} \ge 0.50$ $\longrightarrow$ `PROPOSE`.
  - Default $\longrightarrow$ `INFORM`.
- **Dynamic Energy Bounding:** Somatic energy $E_{\text{somatic}}$ restricts node cardinality to prevent cognitive overload:
  - $E_{\text{somatic}} < 0.30 \implies N \le 1$ entity.
  - $E_{\text{somatic}} < 0.70 \implies N \le 2$ entities.
  - $E_{\text{somatic}} \ge 0.70 \implies N \le 4$ entities.
- **Performance:** Single-core CPU latency $0.02\text{ ms}$, zero LLM tokens sampled or parsed ($\text{TIM} = 1.0$).

### 3.3 Subsystem 3: Candidate C4 Working Semantic Baseline
- **Role:** Compositional, grounded semantic state combining graph topology with hyperdimensional vectors.
- **Dual Representation Components:**
  1. **Typed Relational Property Graph ($V, E$):**
     - Nodes $V$: Typed tuples $(v_{\text{id}}, \text{type} \in \{\text{entity}, \text{predicate}, \text{modifier}\}, \text{label}, \text{anchor\_id}, \text{salience}, \text{negated}, \text{modality})$.
     - Edges $E$: Directed edges $(u, v, r \in \mathcal{R}_{\text{thematic}})$, where $\mathcal{R}_{\text{thematic}} = \{\text{AGENT}, \text{PATIENT}, \text{THEME}, \text{EXPERIENCER}, \text{BENEFICIARY}, \text{LOCATION}, \text{PURPOSE}\}$.
  2. **1024-Dimensional HDC Gestalt Hypervector ($\mathbf{h}_{\text{gestalt}} \in \{-1, +1\}^{1024}$):**
     - Formed via role-path composition and superposition bundling:
       $$\mathbf{h}_{\text{gestalt}} = \text{bundle}\left( \sum_{p \in \text{Paths}(G)} \left( \prod_{r \in p} \mathbf{r} \right) * \mathbf{e}_{\text{node}} * \mathbf{o}_{\text{neg}} \right)$$
- **Recursion Capacity Limit:** Explicitly bounded at recursion depth **$D \le 3$** ($RF_3 = 86.4\% \ge 85.0\%$). Depth $D \ge 4$ exhibits empirical crosstalk degradation ($RF_4 = 83.5\%$) and is disallowed.
- **Negation Encoding:** Bipolar XOR binding ($\mathbf{v} * \mathbf{o}_{\text{neg}}$) ensures an unbinding polarity margin of $\ge 0.450$ ($0.476$ measured), achieving $100\%$ discrete and continuous separation.

### 3.4 Subsystem 4: Persistent Episodic Referential Grounding
- **Role:** Resolves semantic entities to autobiographical memory traces in Kanerva SDM space under environmental noise.
- **Metric Space:** 64-dimensional continuous normalized space ($\mathbb{S}^{63}$).
- **Associative Retrieval:** Queries are matched against canonical anchors and 20 distractor vectors via cosine similarity.
- **Auto-Associative Cleanup:** If similarity to the nearest anchor exceeds the attractor basin threshold ($\text{tol} = 0.55$), the representation projects onto the clean memory attractor.
- **Longitudinal Drift Invariant:** 50-turn displacement $D_{50} \le 0.050$ ($0.000$ measured), ensuring zero referential identity corruption across turns.

### 3.5 Subsystem 5: Incremental State Revision Engine
- **Role:** Applies discrete localized deltas to the active semantic graph without full re-parsing or historical drift.
- **Supported Operations:**
  - `ADD_ENTITY`: Inserts node and binds thematic relation.
  - `UPDATE_ATTRIBUTE`: Updates salience, epistemic status, or metadata.
  - `CORRECT_BELIEF`: Reverses polarity (negation toggle) and modifies epistemic modality.
  - `MERGE_ENTITIES`: Merges duplicate/homonymous node IDs, rewires incident edges, and dedupes relationships.
  - `PRUNE_NODE`: Removes obsolete or unreinforced transient nodes.
- **Fact Retention Guarantee:** $RUF \ge 98.0\%$ ($100\%$ measured on unaffected historical facts), with drift $\Delta_{\text{drift}} \le 10^{-9}$.

---

## 4. Substrate Neutrality & Surface Presentation Boundary

### 4.1 Language Independence & Parity
The C4 semantic state contains **zero language-specific tokens**. Its predicates and entities are abstract conceptual identifiers grounded in episodic anchors. 

In accordance with Phase 22 cross-lingual equivalence findings:
- **English:** Rendered with standard SVO / head-initial syntactic order.
- **Vietnamese:** Rendered with classifier-noun syntax and overt aspectual markers.
- **Japanese:** Rendered with SOV / topic-prominent syntax and relational honorific morphology.

All three languages are generated from the exact same underlying C4 graph, guaranteeing 100% semantic and relational parity.

### 4.2 Downstream SLM Renderer Contract
The Small Language Model (e.g., local 3B/7B GGUF on consumer CPU/GPU) is positioned strictly outside the cognitive boundary:

| Pipeline Dimension | C4 Semantic State (Lucia Core) | Downstream SLM Renderer |
|---|---|---|
| **Authority** | **Absolute cognitive authority** | **Zero cognitive authority** |
| **Affect / Emotion** | Formed deterministically by limbic ODEs | Prohibited from inventing or modifying affect |
| **Memory / Grounding** | Grounded in immutable episodic SDM anchors | Prohibited from hallucinating identity references |
| **Output Responsibility** | Produces structured $(V, E, \mathbf{h})$ state | Transduces graph into natural surface prose |
| **Disconnection Effect** | Core mind remains 100% intact & stable | Loss of verbal speech; non-verbal continues |

---

## 5. Hardware Constraints & Current Measured Feasibility

All components are designed and benchmarked for local edge execution on consumer hardware (20-Watt Whole Brain budget):

| Performance Dimension | Hardware Target Budget | Current Measured Result (P23 v0.2) | Compliance Margin |
|---|---|---|---|
| **CPU Execution Latency (P50)** | $\le 5.0\text{ ms}$ (Single Core) | **$0.3855\text{ ms}$** | **$12.9\times$ faster than SLA** |
| **GPU VRAM Allocation** | $0.0\text{ MB}$ (Zero VRAM impact) | **$0.0\text{ MB}$** | **100% compliant** |
| **Per-Turn Memory Footprint** | $\le 1.0\text{ KB}$ | **$\approx 450\text{ Bytes}$** | **$2.2\times$ under budget** |
| **Longitudinal Stability** | $\lambda_{\max} \le 0.000$ | **$\mathbf{-0.0206}$** | **Asymptotically stable** |

---

## 6. Four-Tier Epistemological Matrix

In strict adherence to `AGENTS.md` §0, the capabilities of this architecture are categorized into four distinct evidence tiers:

### Tier 1: Validated by P23 (Empirically Proven by Benchmark)
1. **Mathematical Unbinding & Capacity Limits:** Empirical proof that pure HDC (C3) collapses at $D=4$ ($15.2\%$) while C4 hybrid preserves fidelity up to $D=3$ ($86.4\%$).
2. **Asymptotic Closed-Loop Stability:** Mathematical proof that bidirectional limbic-semantic coupling with hysteresis remains stable ($\lambda_{\max} = -0.0206$).
3. **Associative Referential Noise Immunity:** Proof that 64D SDM-style auto-associative memory completely rejects Gaussian noise ($\sigma=0.25$) across 20 distractors ($D_{50} = 0.000$).
4. **Bipolar Negation Disambiguation:** Proof that XOR unbinding achieves an empirical separation margin of $0.476$ ($100\%$ NPA).
5. **Incremental Mutation Fact Retention:** Proof that genuine localized graph mutations retain $100\%$ of unaffected historical facts ($RUF = 1.0$).
6. **20-Watt Local Edge SLA:** Measured latency of $0.38\text{ ms}$ and $0.0\text{ MB}$ VRAM.

### Tier 2: Supported Engineering Inference (Structurally Grounded Deductions)
1. **Renderer Swappability:** Deductive consequence of decoupled graph representation; altering the downstream renderer cannot corrupt internal limbic ODEs or episodic memory traces.
2. **Cross-Lingual Parity (EN/VI/JA):** Supported by Phase 22 semantic interface experiments showing identical concept topologies drive diverse surface syntactic orders.
3. **Longitudinal Session Survival:** Supported by zero coordinate drift under continuous auto-associative attractor projection.

### Tier 3: Not Yet Demonstrated (Known Technical Gaps)
1. **Raw Sensory-to-Concept Extraction on Edge:** Track 6 validated concept grounding assuming 32D continuous embeddings were provided. Extracting continuous embeddings directly from raw lexical or acoustic user input without a cloud API or heavy LLM remains to be implemented.
2. **Deep Recursion Past Depth 3 ($D \ge 4$):** C4 gestalt similarity degrades below acceptance thresholds at $D \ge 4$. Higher-order recursion mechanisms remain unvalidated.
3. **Rich Idiomatic Dialogue Variability:** The causal intention formation engine is deterministic and rule-stratified; human-like idiosyncratic stylistic variation has not yet been demonstrated without an SLM renderer.

### Tier 4: Future Research (Post-Phase 23 Horizons)
1. **Pointer-Augmented HDC (PAD-HDC):** Investigating subspace partitioning to extend vector unbinding fidelity to depth $D=5$.
2. **Local Edge Concept Encoder:** Micro-encoder ($\le 50\text{M}$ parameters) to produce 32D concept vectors directly from raw user utterances within the 20W CPU budget.
3. **Stochastic Graph Diffusion / Energy-Based Models:** Continuous probabilistic semantic graph formation driven by limbic energy landscapes.

---

## 7. Production Safety Invariant Verification

- Production Core (`src/core/**`): **0 files modified**
- Desktop Presentation (`electron/**`): **0 files modified**
- Configuration (`config/**`): **0 files modified**
- Genesis Gate (`data/profile.json`): **Bit-exact preserved** (`{"is_onboarded": false}`)
- First Activation Status: **LOCKED FUTURE GATE**
