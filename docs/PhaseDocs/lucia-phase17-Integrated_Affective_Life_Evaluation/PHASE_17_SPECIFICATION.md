# Phase 17 — Specification: Integrated Affective Life Evaluation & Longitudinal Validation

> **Multi-Track Empirical Evaluation, Causal Ablation, Longitudinal Dynamics, and Invariant Verification**  
> **Status:** ACTIVE SPECIFICATION  
> **Authority Level:** Authoritative Evaluation Protocol  
> **Phase Target:** Phase 17  

---

## 1. Executive Summary & Core Research Question

Phase 16 integrated the cognitive, limbic, memory, knowledge, relationship, communication, and multimodal expression subsystems into a unified 16-stage cognitive orchestration pipeline (`src/core/orchestrator/cognitive_orchestrator.py`).

Phase 17 is an **evaluation and validation phase first**, not a feature development phase. It answers the fundamental empirical research question:

$$\begin{aligned}
&\text{\textbf{Research Question:}} \\
&\textit{Does the production Lucia architecture actually exhibit stable, causally coherent, temporally consistent,} \\
&\textit{reproducible, and bounded affective-life dynamics when its promoted subsystems interact over many turns and sessions?}
\end{aligned}$$

### Mandatory Governance & Operational Discipline
1. **Zero Subjective Self-Model / Consciousness Claims**: The evaluation strictly measures dynamical and behavioral properties (boundedness, stability, latency, causal divergence, contextual priming). No introspective or consciousness claims are made.
2. **Strict Invariant Isolation**:
   - Memory $\not\to$ Limbic ODE hidden state $\mathbf{h} \in \mathbb{R}^{32}$.
   - Multimodal Expression / Desktop Body $\not\to$ EmotionCore ODE.
   - Communication strategy $\not\to$ Relationship reward.
   - Simulation / Evaluation runs $\not\to$ Canonical persistent storage (`data/*.json`).
3. **Evaluation-First Gate**: Zero production code changes during the initial evaluation run. If an anomaly or failed metric is observed, it must be recorded as empirical evidence with reproduction steps. Only after the full baseline evaluation is completed may corrective proposals be formulated.
4. **Structured Evidence Taxonomy**: All claims and results must be categorized into:
   - `[OBSERVED]`: Directly recorded behavior from execution logs.
   - `[MEASURED]`: Quantified numeric metrics (latency, distance, norm, error).
   - `[SUPPORTED]`: Hypotheses backed by statistically or causally verified evidence.
   - `[HYPOTHESIZED]`: Theoretical predictions lacking comprehensive longitudinal proof.
   - `[NOT ESTABLISHED]`: Out-of-scope or unproven phenomena.

---

## 2. Evaluation Tracks (A through L)

```
┌───────────────────────────────────────────────────────────────────────────────┐
│                    PHASE 17 EVALUATION MATRIX OVERVIEW                        │
├───────────────────────────────────────────────────────────────────────────────┤
│ Track A: Longitudinal Affective Dynamics (20, 50, 100 turns; multi-session)    │
│ Track B: Causal Ablation (7 isolated single-subsystem ablations)              │
│ Track C: Relationship Calibration (Inertia, decay, collaborative signals)     │
│ Track D: Memory Contextualization (Associative bounds, zero limbic leakage)   │
│ Track E: Knowledge Integrity (K0–K5 propositions, graph, d_max <= 3)          │
│ Track F: Communication Behavior (5 strategies, pacing, BoundaryLayer defense) │
│ Track G: Expression & Body Coherence (15D state, <=5ms latency, feedforward)  │
│ Track H: Persistence & Restart Continuity (Multi-session temporary store)     │
│ Track I: Reproducibility & Tolerance Stratification (Replay vs Numerical)     │
│ Track J: Performance & Stability (S1–S16 breakdown, bounded memory footprint) │
│ Track K: Stress & Recovery Dynamics (Recovery trends, attractor distance)     │
│ Track L: Concurrency & Temporal Correctness (Lock order, commit-token trace)  │
└───────────────────────────────────────────────────────────────────────────────┘
```

### Track A — Longitudinal Affective Dynamics
- **Harness**: Multi-turn sequences spanning 20, 50, and 100 turns across 9 scenario archetypes (neutral baseline, positive accumulation, negative conflict, alternating polarity, stress-recovery, long inactivity, intermittent bursts, familiar vs novel topics, mixed cognitive/emotional).
- **Recorded Metrics**:
  - Continuous PAD trajectory: $P_t, A_t, D_t \in [-1, 1]$.
  - Fast-Loop LNN hidden state: $\|\mathbf{h}_t\|_2$ and component sanity.
  - Homeostatic stamina & load: $\text{energy}_t, \text{load}_t, \text{tension}_t, \text{stability}_t \in [0, 1]$.
  - Surprise & Active Inference: $\mathcal{S}_t = \|\mathbf{A}p_{t-1} + \mathbf{b} - p_t\|_2$.
- **Acceptance Criteria**:
  - Strict mathematical boundedness: all values remain within valid ranges without NaN/Inf.
  - Absence of undamped explosive oscillation or boundary pinning (saturation).
  - Recovery trend: after negative perturbations, $\|\mathbf{PAD}_t - \mathbf{PAD}_{philia}\|_2$ exhibits a measurable decreasing trend toward the resting attractor ($+0.25, -0.05, +0.05$).

### Track B — Causal Ablation
- **Configurations Tested**:
  1. *Baseline (Full System)*: All 16 stages active.
  2. *Ablation 1 (Memory Contextualization Disabled)*: $m_{avail} = 0$, zero echo vector injected.
  3. *Ablation 2 (Knowledge Retrieval Disabled)*: Stage 8 returns empty list.
  4. *Ablation 3 (Relationship Read Disabled)*: Stage 9 pinned to default initial state.
  5. *Ablation 4 (Communication Policy Disabled)*: Stage 10 pinned to neutral baseline.
  6. *Ablation 5 (Expression Policy Disabled)*: Stage 15 pinned to neutral actuator baseline.
  7. *Ablation 6 (Body/IPC Delivery Disabled)*: Actuation consumed as no-op.
  8. *Ablation 7 (Relationship Update Disabled)*: Stage 16.3 update skipped.
- **Acceptance Criteria**:
  - Each ablation causes measurable, specific downstream variation without altering upstream or decoupled components.
  - Forbidden causal paths remain completely zeroed.

### Track C — Relationship Calibration
- **Scenarios**: 50 turns of repeated cooperation, conflict, conflict followed by repair, inactivity decay, and identical interaction under divergent affective states.
- **Metrics**: Familiarity, Trust, Closeness, Reciprocity in $[0, 1]^4$.
- **Acceptance Criteria**:
  - Slow inertia ($\alpha=0.03$) prevents single-turn radical jumps ($\Delta \le 0.05$ per turn).
  - Passive temporal decay operates strictly when elapsed time $\Delta t > 0$.
  - Relationship updates depend exclusively on objective interaction evidence (`prediction_error`, `tension`), independent of Lucia's communication strategy or PAD.

### Track D — Memory Contextualization
- **Scenarios**: Associative retrieval with relevant memory, irrelevant memory, and empty memory store.
- **Metrics**: Scalar contextualization bound $m_{ctx} \in [0.0, 0.50]$, echo vector cosine similarity, prompt assembler contextual reference injection.
- **Acceptance Criteria**:
  - Contextual reference bounded by $0.50$.
  - Zero memory feedback into limbic hidden state $\mathbf{h} \in \mathbb{R}^{32}$.
  - Zero direct modification of PAD by memory retrieval.

### Track E — Knowledge Integrity
- **Scenarios**: K0–K5 typed propositions, concept relationships, bounded forward derivation ($d_{max} \le 3$), contradiction resolution, concurrent multi-threaded store access, deterministic replay.
- **Acceptance Criteria**:
  - Derivation depth $d \le 3$ strictly enforced.
  - Contradiction resolution flags or supersedes outdated claims.
  - Knowledge retrieval operations do not mutate emotional or relational state.

### Track F — Communication Behavior
- **Scenarios**: Evaluation of all 5 discrete strategies (`DIRECT_FACTUAL`, `REASSURING_WARM`, `ELABORATIVE_EXPLANATORY`, `CONCISE_RESERVED`, `COLLABORATIVE_INQUIRING`), conversational pacing latency ($0 \le \tau \le 1000\text{ms}$), and BoundaryLayer defense.
- **Acceptance Criteria**:
  - Pacing latency satisfies $0 \le \tau \le 1000\text{ms}$.
  - BoundaryLayer blocks contextual violations, subjective consciousness claims (*"I feel"*, *"As an AI, I experience"*), and fabricated autobiographical self-awareness.

### Track G — Expression & Body Coherence
- **Scenarios**: Multimodal 15D ExpressionState evaluated under diverse limbic and somatic conditions (positive, negative, high tension, low stability).
- **Acceptance Criteria**:
  - Evaluation latency $\le 5.0\text{ms}$ (with $\le 2.0\text{ms}$ target).
  - Smooth temporal interpolation ($\gamma=0.25$).
  - Feedforward actuator decoupling: zero perturbation of EmotionCore ODE by ExpressionState.

### Track H — Persistence & Restart Continuity
- **Scenarios**: Multi-session lifecycle: Session 1 (20 turns) $\to$ Atomic Persistence $\to$ Process Teardown $\to$ Session 2 (20 turns) restart.
- **Acceptance Criteria**:
  - Persistence executes strictly within temporary test directories (`tmp_path`).
  - Canonical storage (`data/*.json`) remains bit-exact unmutated (verified via SHA-256).
  - Session 2 cleanly restores relationship state, knowledge graph, and episodic memory without duplication or corruption.

### Track I — Reproducibility & Tolerance Stratification
- **Evaluation Method**: Repeated execution ($N=5$) of identical scenarios with fixed random seeds.
- **Stratified Tolerances**:
  - *Deterministic replay path* (discrete strategies, proposition derivations, relationship updates under locked stepping): bit-exact match ($0.0$ difference).
  - *Continuous ODE integration*: $\Delta\mathbf{PAD} \le 0.05$ (accounting for floating-point and fast-loop integration cadence).

### Track J — Performance & Stability
- **Scenarios**: Continuous execution of 50 turns profiling per-stage latencies (S1 through S16).
- **Acceptance Criteria**:
  - Per-stage latency breakdown measured and logged.
  - Memory footprint: no unbounded linear memory growth ($\Delta\text{RSS} \le 50\text{MB}$ over 50 turns).
  - Zero deadlocks or race conditions.

### Track K — Stress & Recovery Dynamics
- **Scenarios**: 20 negative turns $\to$ 20 neutral turns $\to$ 20 positive turns; rapid alternating polarity.
- **Acceptance Criteria**:
  - System remains mathematically bounded under extreme stress.
  - Homeostatic tension and cognitive load decay toward baseline during recovery.
  - Distance to Philia attractor $\|\mathbf{PAD}_t - \mathbf{PAD}_{philia}\|_2$ exhibits a decreasing recovery trend.

### Track L — Concurrency & Temporal Correctness
- **Scenarios**: Concurrent stimuli injection, non-reentrant lock enforcement, temporal sequence tracing.
- **Acceptance Criteria**:
  - Traces confirm exact chronological sequence:
    $$\text{Stimulus} \longrightarrow \text{Commit Token} \longrightarrow \text{Committed Snapshot} \longrightarrow \text{S4–S15 Consumption} \longrightarrow \text{S16 Update}$$
  - Zero out-of-order stimulus integration.

---

## 3. Failure Classification Taxonomy

Every divergence, anomaly, or failed metric identified during evaluation must be explicitly classified before formulating any proposal:

| Class | Category | Description | Permitted Action |
|---|---|---|---|
| **C1** | **Implementation Defect** | Concrete bug or broken contract in production code. | Document reproduction; propose targeted code fix after baseline run. |
| **C2** | **Integration Defect** | Structural mismatch or impedance between two connected subsystems. | Document interface discrepancy; propose interface alignment. |
| **C3** | **Calibration Issue** | Parameter sensitivity, excessive inertia, or decay rate mismatch. | Tune configuration parameters; do not alter architecture. |
| **C4** | **Unsupported Assumption** | Theoretical design assumption disproven by longitudinal evidence. | Document as design limitation; update specification. |
| **C5** | **Measurement Artifact** | Issue caused by test harness timing, mock limitation, or OS scheduling. | Refine harness or adjust measurement methodology. |
| **C6** | **Expected Behavior** | Intended architectural dampening, inertia, or fallback operation. | Document rationale; retain behavior. |

---

## 4. Storage & First Activation Safety Gates

1. **First Activation Gate**:
   - `data/profile.json` must have `is_onboarded = False`.
   - No evaluation test or harness execution may trigger live Genesis or onboarding.
2. **Canonical Storage Guard**:
   - `data/profile.json`, `data/chat_history.json`, `data/knowledge.json`, `data/relationship.json` must be hashed before and after evaluation runs.
   - Any modification of these canonical files causes immediate evaluation failure.
