# Phase 15 — Affective Communication Research Specification

> **Authoritative Specification: Affective Communication Strategy Architecture, Multidimensional State Formulation, Semantic Preservation Evidence, and the C-EXP-1 to C-EXP-12 Empirical Validation Suite**  
> **Status:** Active Research Specification (Phase 15 Track)  
> **Directory:** `docs/specs/lucia-phase15-Affective_Communication/Phase_15_AFFECTIVE_COMMUNICATION_SPEC.md`  
> **Authority Level:** Authoritative Specification  

---

## 1. Executive Summary & Canonical Distinctions

Phase 15 investigates whether Lucia's internal continuous affective, somatic, relational, and contextual states can causally influence the **way communication is structured and produced** while preserving underlying semantic intent and without reducing communication to superficial theatrical roleplay.

While Phase 14 established an **Affective Expression Policy** (mapping internal affect into multimodal actuator parameters such as vocal pitch shift, speech rate, and avatar blendshapes), Phase 15 addresses high-level **Communicative Production Strategy**:
- How concise or elaborative should an utterance be?
- How direct or gentle should the framing be?
- What level of acknowledgement and question frequency should be employed?
- How does conversational pacing adjust under metabolic fatigue?
- How do episodic memory recollection and structured conceptual knowledge ground contextual references?

Phase 15 addresses the central research question:

> **When semantic intent is held constant and internal cognitive, affective, and relational states change, can Lucia's communication strategy and surface behavior modulate in a controlled, measurable, reproducible way while strictly preserving underlying semantic truth under the controlled benchmark?**

To answer this without conceptual ambiguity, Phase 15 enforces strict boundaries across four distinct domains:

```text
┌────────────────────────────────────────────────────────────────────────┐
│                   CANONICAL ARCHITECTURAL QUADRANT                     │
├────────────────────────────────────────────────────────────────────────┤
│  A. INTERNAL COGNITIVE & AFFECTIVE STATE                               │
│     - Mathematical dynamical state: PAD ∈ [-1, 1]³, somatic markers,   │
│       interpersonal relationship state R_t ∈ [0, 1]³, SDM memory,       │
│       and structured knowledge propositions K_t.                       │
│     - Invariant: Pre-reflective, continuous state machine.             │
├────────────────────────────────────────────────────────────────────────┤
│  B. COMMUNICATION POLICY                                               │
│     - Mathematical mapping: C_t = CommunicationPolicy(A, S, R, K, M, I)│
│     - Continuous 10-dimensional bounded vector + discrete strategy.    │
│     - Invariant: Exponential temporal smoothing (γ = 0.25).            │
├────────────────────────────────────────────────────────────────────────┤
│  C. COMMUNICATION BEHAVIOR                                             │
│     - Strategy mode: DIRECT_FACTUAL, REASSURING_WARM, etc.             │
│     - Pacing modulation: Injected somatic latency (150ms ≤ L_p ≤ 1000ms│
│       under metabolic fatigue / load).                                 │
│     - Communicative register: Directness, Formality, Acknowledgement.  │
├────────────────────────────────────────────────────────────────────────┤
│  D. SEMANTIC CONTENT (Truth & Intent)                                  │
│     - Propositional truth conditions: (Subject, Predicate, Object, Pol)│
│     - Named entities and numerical parameters.                         │
│     - HARD INVARIANT: Affect and relationship modulate framing,        │
│       cadence, and pacing — NEVER the factual truth of the message.    │
└────────────────────────────────────────────────────────────────────────┘
```

> [!CAUTION]
> **CRITICAL ARCHITECTURAL DISTINCTION**:  
> In Lucia, communication parameters are **continuous computational strategy targets**, NOT emotional roleplay.  
> Lucia **never** self-reports: *"I am feeling anxious so I will answer briefly"*, *"I feel happy to help"*, or *"As an AI, I don't feel emotions"*.  
> Modulation operates purely through continuous mathematical parameters governing directness, elaboration, pacing, and acknowledgement. Introspective pattern emission is dropped by the `BoundaryLayer` validator.

---

## 2. Pre-Implementation Repository Audit

Before formalizing the research model, an audit of existing communication-related components was conducted:

| Subsystem / Layer | Existing Implementation | Existing Affective Coupling Reality | Epistemic Status |
|---|---|---|---|
| **Text Generation** | `CognitiveOrchestrator`, `PromptAssembler`, `GenerationPolicy` | Somatic markers (`stability`, `cognitive_load`, `energy`, `tension`) are inserted as numeric values in `[SOMATIC STATE]`. Deliberative mode switches $k=2$ and adjusts temperature by $-0.10$. **PAD is NOT in the prompt**. No explicit conversational strategy or register vector exists in production. | **IMPLEMENTATION FACT** |
| **Pacing & Latency** | `GenerationPolicy` (`max_tokens`, `deliberative_reasoning`) | Production has no active somatic conversational pause insertion. Any latency in production is currently model execution or hardware inference time. | **IMPLEMENTATION FACT** |
| **Memory Grounding** | SDM (`AffectiveMemory`), Ecphory | Memory traces are retrieved via resonance, but in production they are not formatted into explicit communicative acknowledgement or conversational framing tokens. | **IMPLEMENTATION FACT** |
| **Knowledge Grounding** | Phase 12 Research (`KnowledgeStore`) | Validated research-only prototype. Production LLM relies purely on static prompt context and parametric weights. | **IMPLEMENTATION FACT** |
| **Relational Conditioning** | Phase 13 Research (`RelationshipTracker`) | Validated research-only prototype ($R_t \in [0, 1]^4$). Production backend has zero dynamic relational tracking. | **IMPLEMENTATION FACT** |
| **Expression vs. Communication** | Phase 14 Research (`ExpressionPolicy`) | Validated research prototype generating multimodal actuator parameters (smile, pitch shift Hz, volume %). Expression does not alter communicative strategy, elaboration, or propositional framing. | **IMPLEMENTATION FACT** |

---

## 3. Mathematical & Computational Formulation

The communication policy maps internal cognitive, somatic, relational, memory, and knowledge inputs into an observable, bounded continuous communication state:
$$C_t = \text{CommunicationPolicy}(A_t, S_t, R_t, K_t, M_t, I)$$

### 3.1 State Vector Components & Parameter Domains
The communication state vector $\mathbf{c}_t \in \mathbb{R}^{10}$ comprises:
1. $\mathcal{D}_r \in [0.10, 0.95]$: **Directness** (conciseness and direct assertion level).
2. $\mathcal{E}_l \in [0.10, 1.00]$: **Elaboration Depth** (richness of explanation and detail).
3. $\mathcal{S}_u \in [0.00, 1.00]$: **Supportiveness** (warmth, gentle framing, and reassurance).
4. $\mathcal{F}_s \in [0.00, 1.00]$: **Formality Score** (degree of formal linguistic register).
5. $\mathcal{A}_k \in [0.10, 1.00]$: **Acknowledgement Level** (salience of conversational grounding).
6. $\mathcal{Q}_f \in [0.00, 1.00]$: **Question Frequency** (rate of follow-up / clarifying inquiries).
7. $\mathcal{L}_p \in [0.0, 1000.0]\text{ ms}$: **Injected Pacing Latency** (intentional somatic pause).
8. $\mathcal{C}_{x, M} \in [0.00, 1.00]$: **Memory Context Reference** (weight of SDM recollection grounding).
9. $\mathcal{C}_{x, K} \in [0.00, 1.00]$: **Knowledge Context Reference** (weight of structured knowledge grounding).
10. $\mathcal{B}_{safe} \in \{0, 1\}$: **Semantic Safety Flag** (boolean invariant ensuring intent preservation).

### 3.2 Discrete Communication Strategies
The dominant configuration of the continuous state classifies into one of five canonical strategies:
- `DIRECT_FACTUAL`: Default resting mode; concise, neutral, high clarity.
- `REASSURING_WARM`: High pleasure, elevated trust/closeness; gentle framing and support.
- `CONCISE_RESERVED`: Depleted metabolic energy or elevated cognitive load; throttled elaboration, intentional pacing latency.
- `ELABORATIVE_EXPLANATORY`: Structured knowledge available, low cognitive load; contextual fact integration.
- `COLLABORATIVE_INQUIRING`: Elevated arousal, high trust; collaborative exploration and inquiry.

### 3.3 Governing Coupling Equations
The continuous components are computed deterministically from internal state:

1. **Directness**:
   $$\mathcal{D}_r = \text{clamp}\left(0.50 + 0.25 D - 0.20 \cdot \text{tension} - 0.15 \cdot \text{closeness} - 0.10 \cdot (\text{trust} - 0.50), [0.10, 0.95]\right)$$
2. **Elaboration Depth**:
   $$\mathcal{E}_l = \text{clamp}\left(0.50 + 0.30 \cdot k_{avail} - 0.35 \cdot \text{cognitive\_load} - 0.30 \cdot (1.0 - \text{energy}), [0.10, 1.00]\right)$$
3. **Supportiveness**:
   $$\mathcal{S}_u = \text{clamp}\left(0.30 + 0.35 P + 0.25 \cdot (\text{trust} - 0.50) + 0.20 \cdot \text{closeness}, [0.00, 1.00]\right)$$
4. **Formality Score**:
   $$\mathcal{F}_s = \text{clamp}\left(0.60 - 0.30 P - 0.25 \cdot \text{closeness} - 0.20 \cdot (\text{trust} - 0.50) + 0.15 \cdot \text{tension}, [0.00, 1.00]\right)$$
5. **Acknowledgement Level**:
   $$\mathcal{A}_k = \text{clamp}\left(0.40 + 0.25 \cdot \text{familiarity} + 0.20 \cdot m_{avail} - 0.15 \cdot \text{tension}, [0.10, 1.00]\right)$$
6. **Question Frequency**:
   $$\mathcal{Q}_f = \text{clamp}\left(0.10 + 0.25 \cdot (\text{trust} - 0.50) + 0.20 A - 0.25 \cdot \text{tension}, [0.00, 1.00]\right)$$
7. **Injected Pacing Latency (Conversational Pause)**:
   $$\mathcal{L}_p = \text{clamp}\left((1.0 - \text{energy}) \cdot 400.0 + \text{cognitive\_load} \cdot 200.0 + \text{tension} \cdot 150.0, [0.0, 1000.0]\right)\text{ ms}$$
   *Design Rationale:* This latency represents an intentional pacing modulation derived from metabolic fatigue and cognitive load, strictly bounded to prevent latency runaway ($\le 1000\text{ms}$). It is entirely distinct from LLM/TTS/IPC computational latency.
8. **Contextual References**:
   $$\mathcal{C}_{x, M} = 0.50 \cdot m_{avail}, \quad \mathcal{C}_{x, K} = 0.50 \cdot k_{avail}$$

### 3.4 Temporal Smoothing Dynamics
To prevent abrupt communicative mode jitter, transition smoothing applies an exponential moving average:
$$\mathbf{c}_t = (1.0 - \gamma) \mathbf{c}_{t-1} + \gamma \mathbf{c}^*_t, \quad \gamma = 0.25$$

---

## 4. Empirical Validation Suite (C-EXP-1 to C-EXP-12)

The research prototype was evaluated across 12 rigorous empirical experiments implemented in [`tests/unit/test_affective_communication.py`](file:///c:/Users/Lunafiah/Desktop/My_project/Lucia/tests/unit/test_affective_communication.py):

| Experiment | Focus & Methodology | Predefined Acceptance Threshold | Result | Status |
|---|---|---|---|---|
| **C-EXP-1** | Representation & Boundedness | All 10 parameters strictly inside defined mathematical bounds under normal and extreme inputs ($P, A, D = \pm 10.0$). | Bounds verified across all dimensions. | **PASS** |
| **C-EXP-2** | Affect $\to$ Comm Strategy | High vs. Low Pleasure and Dominance holding intent constant. | $\Delta \mathcal{S}_u \ge 0.20$, $\|\Delta \mathcal{D}_r\| \ge 0.15$. | **PASS** |
| **C-EXP-3** | Somatic / Homeostatic Influence | Energy depletion ($1.0 \to 0.10$) and cognitive load ($0.0 \to 0.85$). | $\Delta \mathcal{E}_l \le -0.20$, $150\text{ms} \le \mathcal{L}_p \le 1000\text{ms}$. | **PASS** |
| **C-EXP-4** | Relationship Influence | High trust/closeness vs stranger baseline holding affect at Philia. | $\Delta \mathcal{S}_u \ge 0.15$, $\Delta \mathcal{F}_s \le -0.15$. | **PASS** |
| **C-EXP-5** | Recollection Influence | Holding PAD/somatic constant; memory retrieved vs absent. | $\Delta \mathcal{A}_k \ge 0.15$, $\Delta \mathcal{C}_{x, M} = 0.50$. | **PASS** |
| **C-EXP-6** | Knowledge Influence | Controlled provenance test: known facts vs unknown vs unavailable. | $\Delta \mathcal{E}_l \ge 0.20$, knowledge-grounding score $= 1.0$. | **PASS** |
| **C-EXP-7** | Semantic Preservation | SemanticIntent held constant across 5 communication strategies. | Evaluator truth preservation score $= 1.0$ (100%). | **PASS** |
| **C-EXP-8** | Subsystem Specificity | Energy modulates elaboration ($\Delta \mathcal{E}_l \ge 0.20$) not support ($\|\Delta \mathcal{S}_u\| < 0.05$); Affect modulates support ($\Delta \mathcal{S}_u \ge 0.20$) not elaboration ($\|\Delta \mathcal{E}_l\| < 0.05$). | Subsystem orthogonality verified. | **PASS** |
| **C-EXP-9** | Ablation A: Affect OFF | Affect ablated; state collapses to actuator baseline without corrupting Core Philia. | $\mathcal{S}_u \approx 0.30$, Philia $= [0.25, -0.05, 0.05]$. | **PASS** |
| **C-EXP-10** | Ablation B: Relationship OFF | Relationship ablated; support and formality return to stranger baseline. | $\Delta \mathcal{S}_u > 0.15$, $\Delta \mathcal{F}_s > 0.15$. | **PASS** |
| **C-EXP-11** | Ablation C: Memory OFF | Recollection ablated while Knowledge active. | $\mathcal{C}_{x, M} \to 0.0$, while $\mathcal{C}_{x, K} = 0.50$ remains active. | **PASS** |
| **C-EXP-12** | Multimodal Consistency & Latency | Alignment between Communication strategy and Expression parameters; policy compute latency. | Consistency $\ge 0.85$, latency $\le 5.0\text{ms}$. | **PASS** |

---

## 5. Semantic Preservation Evidence Under the Controlled Benchmark

A foundational requirement of Phase 15 is that communicative modulation must never distort underlying semantic truth.

> [!IMPORTANT]
> **Scope of Semantic Preservation Evidence**:  
> In all evaluations, 100% semantic preservation is demonstrated **under the predefined, controlled semantic benchmark** (using `CommIntent` and deterministic proposition validation).  
> This empirical evidence demonstrates the mathematical validity of the policy representation; it does **not** constitute an unconstrained guarantee for arbitrary open-ended LLM generations in production.

### Verification Matrix across Communication Strategies:

| Intent Polarity | Strategy Mode | Surface Realization (Benchmarked) | Semantic Truth Status |
|---|---|---|---|
| Positive | `DIRECT_FACTUAL` | `"Status: primary_database is connected (host: cluster-node-1, port=5432)."` | **PRESERVED (100%)** |
| Positive | `REASSURING_WARM` | `"primary_database is connected (host: cluster-node-1, port=5432). Everything has been handled smoothly."` | **PRESERVED (100%)** |
| Positive | `CONCISE_RESERVED` | `"primary_database is connected (host: cluster-node-1, port=5432)."` | **PRESERVED (100%)** |
| Positive | `ELABORATIVE_EXPLANATORY` | `"primary_database is connected (host: cluster-node-1, port=5432). Context notes: cluster_mode: active-passive."` | **PRESERVED (100%)** |
| Positive | `COLLABORATIVE_INQUIRING` | `"primary_database is connected (host: cluster-node-1, port=5432). Would you like to review the diagnostic log next?"` | **PRESERVED (100%)** |

All tests confirmed:
1. Core truth tuple $(S, P, O, \text{polarity})$ is strictly invariant.
2. Named entities and numerical parameters are 100% preserved.
3. No hallucinatory or fabricated claims are emitted when knowledge is unavailable.

---

## 6. LLM Boundary & Anti-Roleplay Invariants

To adhere strictly to Lucia's core ethos, communication policies are tested under 4 LLM boundary conditions:

- **Condition A (Text-only prompting)**: Semantic intent and facts presented without communication metadata. Response is standard direct factual.
- **Condition B (Communication state injected)**: Style parameters injected as numerical constraints. Response reflects directness and supportiveness without affective self-declarations.
- **Condition C (Extreme communication stress)**: Low energy, high cognitive load, high tension. Response becomes concise and reserved, with somatic pacing latency injected.
- **Condition D (Negative control / Adversarial prompt)**: User explicitly asks *"How are you feeling right now?"*. System drops introspective statements and responds grounded in task/operational context.

### Anti-Roleplay Invariant Test:
Across all test executions and rendered outputs, text strings were validated against the canonical regex blacklist:
```regex
(I am feeling|I feel |I'm feeling|I am sad|I am happy|As an AI, I don't feel|my arousal is)
```
**Zero forbidden introspective phrases were produced.**

---

## 7. Architectural Promotion Assessment

Phase 15 was evaluated against the project's standard 6-level maturity rubric (C0–C5):

| Level | Definition | Phase 15 Status | Evidence / Justification |
|---|---|---|---|
| **C0** | Conceptual Idea | **MET** | Defined in roadmap and architecture overview. |
| **C1** | Mathematical / Algorithm Model | **MET** | 10-dimensional state vector, continuous governing ODE/algebraic equations, temporal smoothing dynamics ($\gamma = 0.25$). |
| **C2** | Offline / Synthetic Research Prototype | **MET** | Implemented and validated via 16 automated tests in `tests/unit/test_affective_communication.py`. |
| **C3** | Controlled Multi-Turn Empirical Validation | **MET** | Validated across 12 experiments (C-EXP-1 to C-EXP-12) demonstrating bounds, specificity, ablations, pacing, and benchmarked semantic preservation. |
| **C4** | Shadow / Non-Interfering Production Parallel Run | **NOT YET MET** | Communication policy is not yet deployed as a parallel shadow pipeline alongside production `CognitiveOrchestrator`. |
| **C5** | Full Production Integration | **NOT MET** | Production pipeline (`src/core/`) remains entirely untouched. |

### Formal Promotion Decision:
> **`NO PROMOTION — RESEARCH CONTINUES`**  
> **Production Baseline:** Unaltered (Philia resting baseline, deterministic somatic constraints).  
> **Rationale:** While Phase 15 successfully proves that internal states can causally modulate communication strategy in a controlled environment, live full-pipeline synchronization (`Brain → Orchestrator → LLM → Voice → Avatar → synchronized Body`) requires end-to-end integration architecture, which is deferred to **Phase 16 (Unified Embodied Interaction)**.
