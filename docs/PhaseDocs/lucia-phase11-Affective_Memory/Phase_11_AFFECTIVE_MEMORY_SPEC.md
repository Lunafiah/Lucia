# Phase 11 — Affective Memory & Recollection Coupling Specification

> **Authoritative Specification: Memory Retrieval vs. Affective Recollection, Candidate Coupling Hypotheses, and Empirical Evaluation Framework**  
> **Status:** Active Research Specification (Phase 11)  
> **Directory:** `docs/specs/lucia-phase11-Affective_Memory/Phase_11_AFFECTIVE_MEMORY_SPEC.md`  
> **Authority Level:** Authoritative Specification

---

## 1. Executive Summary & Research Objective

This document defines the research and architectural framework for **Phase 11 — Affective Memory / Recollection**. The primary objective of Phase 11 is to answer:

> **Core Research Question:**  
> *Can episodic memory retrieval become a causally active component of Lucia's internal affective dynamics, and if so, which coupling mechanism is the most stable, temporally correct, bounded, reversible, and causally defensible?*

Phase 11 adheres strictly to the epistemic rule:
**Do not assume any candidate coupling as architectural truth beforehand.**  
Candidates A through E represent competing scientific hypotheses that must be empirically benchmarked under controlled conditions.

### 1.1 Canonical Cognitive Roadmap

```text
FOUNDATION
    ↓
Phase 10 — Affective Dynamics                 [VALIDATED]
Phase 11 — Affective Memory / Recollection    [CURRENT RESEARCH]
Phase 12 — Knowledge Learning                  [RESEARCH TRACK]
Phase 13 — Relationship Development            [RESEARCH TRACK]
Phase 14 — Embodiment & Affective Expression   [RESEARCH TRACK]
Phase 15 — Affective Communication             [RESEARCH TRACK]
Phase 16 — Affective Life Integration         [INTEGRATION]
Phase 17 — First Activation                   [FUTURE MILESTONE]
```

### 1.2 Mandatory Negative Invariants

- **No Sentience or Consciousness Claims**: Recollection is modeled as a mathematical vector transformation, not subjective remembering or conscious nostalgia.
- **No Direct Injection into Limbic ODE ($h \in \mathbb{R}^{32}$)**: Preserving the Phase 10 finding: injecting memory traces into the raw continuous ODE triggers severe runaway feedback risks and destroys observability.
- **Phase 9.6 Synchronization Invariance**: The FIFO sequence commit barrier (`commit_stimulus`) and lock hierarchy remain immutable.
- **Production Isolation**: Phase 11 experimental couplings are evaluated in isolated test harnesses without mutating production `CognitiveOrchestrator` execution paths.
- **Data File Immutability**: Production data (`data/chat_history.json`, `data/profile.json`) remains 100% bit-exact.

---

## 2. Fundamental Distinction: Retrieval vs. Recollection

A central source of conceptual confusion in cognitive agent design is collapsing retrieval into recollection. Phase 11 establishes a strict boundary:

```text
┌────────────────────────────────────────────────────────────────────────┐
│                        RETRIEVAL vs. RECOLLECTION                      │
├────────────────────────────────────────────────────────────────────────┤
│  MEMORY RETRIEVAL ("What was recorded?")                               │
│    - Operation: Querying Kanerva SDM by Hamming distance and PAD       │
│                 cosine similarity.                                     │
│    - Output: An Echo Vector or prompt string inserted into context.    │
│    - Internal Dynamic Effect: ZERO. Memory is an open-loop sink.       │
│    - Status in Lucia: IMPLEMENTED & TESTED (Phases 2 & 9).             │
├────────────────────────────────────────────────────────────────────────┤
│  AFFECTIVE RECOLLECTION ("How does recall alter internal state?")      │
│    - Operation: Synthesizing an internal, bounded recollection state   │
│                 that causally influences downstream affective or       │
│                 regulatory dynamics.                                   │
│    - Output: A measurable shift in internal state variables or policy. │
│    - Internal Dynamic Effect: CAUSALLY ACTIVE & TEMPORALLY BOUNDED.   │
│    - Status in Lucia: RESEARCH HYPOTHESIS (Phase 11).                  │
└────────────────────────────────────────────────────────────────────────┘
```

> [!CAUTION]
> A retrieved memory trace appearing in an LLM prompt string is **not** evidence of affective recollection. It is merely contextual prompt conditioning. True affective recollection requires a measurable, persistent, and bounded modification of internal state or policy.

---

## 3. Existing Open-Loop Baseline (Candidate A)

In the current validated architecture (Phase 9 & Phase 10):
1. **Stage 6 (Affective Ecphory)**: `EcphoryEngine.query(pad_final, traces)` computes cosine similarity in 3D PAD space between current emotional state and stored memory tags.
2. If similarity $> \theta_{\text{resonance}} = 0.60$, it computes a weighted average of content vectors:
   $$\text{echo\_vector} = \frac{\sum_k w_k \cdot c_k}{\sum_k w_k} \in [-1.0, 1.0]^M$$
3. **Stage 7 (Prompt Assembly)**: `PromptAssembler` formats `echo_vector` into a text block (`[MEMORY ECHO]`) within the prompt.
4. **Causal Impact**: Zero feedback into Layer 2 (Limbic ODE), Layer 3 (Homeostatic Somatic Markers), or Layer 4 (Active Inference Beliefs).
5. **Epistemic Status**: `IMPLEMENTATION FACT` / `CONTROL BASELINE`.

---

## 4. Competing Candidate Coupling Hypotheses

Phase 11 formulates five distinct candidate models to be empirically evaluated:

```mermaid
graph TD
    subgraph CandidateA ["Candidate A: Retrieval Only (Control)"]
        SDM_A["SDM Traces"] --> Echo_A["Echo Vector"]
        Echo_A --> Prompt_A["Prompt Context Only"]
    end

    subgraph CandidateB ["Candidate B: Isolated Recollection State"]
        SDM_B["SDM Traces"] --> r_B["Recollection State r(t)"]
        r_B --> Decay_B["Autonomous Decay dr/dt"]
    end

    subgraph CandidateC ["Candidate C: Recollection → Layer 3"]
        SDM_C["SDM Traces"] --> r_C["Recollection r(t)"]
        r_C --> L3["L3: Somatic Markers (ΔC, ΔT)"]
        L3 --> Policy_C["Generation Policy"]
    end

    subgraph CandidateD ["Candidate D: Recollection → Layer 4"]
        SDM_D["SDM Traces"] --> r_D["Recollection r(t)"]
        r_D --> L4["L4: Transition Prior q_hat"]
        L4 --> Surprise_D["Surprise S_t & Belief Update"]
    end

    subgraph CandidateE ["Candidate E: Recollection → Policy Threshold"]
        SDM_E["SDM Traces"] --> r_E["Recollection r(t)"]
        r_E --> Thresh_E["Deliberative Threshold θ_eff"]
    end
```

### 4.1 Candidate A — Memory Retrieval Only (Baseline Control)
- **Mechanism**: Current production behavior. Memory echo passes strictly to `PromptAssembler`.
- **Hypothesis**: Internal limbic ($h, p$), homeostatic ($\mathcal{C}, \mathcal{E}, \mathcal{T}$), and predictive ($A, b, \mathcal{S}$) states are 100% identical between memory-enabled and memory-disabled runs.
- **Risk**: Zero causal integration; memory remains an external prompt prompt-engineering artifact.

### 4.2 Candidate B — Isolated Recollection State $r(t)$
- **Mechanism**: Formulates a distinct internal state vector $r(t)$:
  $$r(t) = \left( r_{\text{pad}}, r_{\text{intensity}}, r_{\text{content}} \right)$$
  where:
  $$r_{\text{pad}} = \frac{\sum_k w_k \cdot p_{\text{tag}, k}}{\sum_k w_k} \in [-1, 1]^3, \quad r_{\text{intensity}} = \min\left(1.0, \sum_k w_k\right) \in [0, 1]$$
- **Decay Dynamics**: Leaky temporal decay over idle time:
  $$\frac{dr}{dt} = -\lambda_{\text{rec}} r(t)$$
- **Boundary**: Does **not** mutate L2, L3, or L4. Evaluates whether a persistent, decaying recollection representation can be cleanly maintained in memory.
- **Risk**: Self-contained state without downstream functional consequence unless coupled.

### 4.3 Candidate C — Recollection $\to$ Layer 3 (Somatic Modulation)
- **Mechanism**: Recollection state modulates homeostatic somatic markers at Stage 5:
  $$\Delta \mathcal{T}_{\text{rec}} = \beta_{\text{mem}} \cdot r_{\text{intensity}} \cdot |r_{\text{pleasure}} - P_{01}|$$
  $$\Delta \mathcal{C}_{\text{rec}} = \alpha_{\text{mem}} \cdot r_{\text{intensity}} \cdot \max(0, r_{\text{arousal}})$$
  $$\text{Tension}_{\text{final}} = \min(1.0, \mathcal{T}_{\text{base}} + \Delta \mathcal{T}_{\text{rec}})$$
  $$\text{Load}_{\text{final}} = \min(1.0, \mathcal{C}_{\text{base}} + \Delta \mathcal{C}_{\text{rec}})$$
- **Experimental Parameters**: $\alpha_{\text{mem}}, \beta_{\text{mem}} \in [0.0, 1.0]$.
- **Downstream Consequence**: Modulates token budget and generation policy without corrupting continuous ODE.
- **Risk**: Potential over-sensitization to historical trauma or stress.

### 4.4 Candidate D — Recollection $\to$ Layer 4 (Active Inference Prior)
- **Mechanism**: Recollection state injects an affective expectation bias into generative state model $\hat{q} = A p_{\text{initial}} + b$:
  $$\hat{q}_{\text{biased}} = A p_{\text{initial}} + b + \kappa_{\text{mem}} \cdot r_{\text{intensity}} \cdot (r_{\text{pad}} - p_{\text{initial}})$$
- **Downstream Consequence**: Changes prediction error $\delta = \hat{q}_{\text{biased}} - p_{\text{final}}$ and surprise $\mathcal{S} = \|\delta\|_2$, altering online gradient adaptation of $A$ and $b$.
- **Risk**: Generative model drift; potential instability in transition matrix $A$.

### 4.5 Candidate E — Recollection $\to$ Layer 6 (Generation Policy Threshold)
- **Mechanism**: Leaves all internal dynamical states ($h, \text{somatic}, A, b$) completely untouched. Dynamically modulates the deliberative mode threshold in `SurpriseModulationPolicy`:
  $$\theta_{\text{deliberative}}^{\text{eff}} = \max(0.20, \theta_{\text{deliberative}} - \gamma_{\text{mem}} \cdot r_{\text{intensity}})$$
- **Downstream Consequence**: Highly resonant memories lower the bar for activating deep reasoning ($k=2$, 3 scaffolding steps) without altering physiological markers.
- **Risk**: Policy-only effect; does not constitute physiological affect modification.

---

## 5. Eight Empirical Evaluation Criteria

Every candidate must be evaluated against the following criteria:

| # | Criterion | Operational Definition & Test Method |
|---|---|---|
| **1** | **Dynamical Stability** | State trajectories must not exhibit runaway explosion, numerical divergence, or infinite loops over $N \ge 20$ turns. |
| **2** | **Boundedness** | All state variables, modulations, and matrices must remain strictly within their mathematical domains ($[-1, 1]$, $[0, 1]$, or $[-2, 2]$). |
| **3** | **Causal Efficacy** | An explicit intervention ($\text{Memory}_{\text{ON}}$ vs $\text{Memory}_{\text{OFF}}$) must produce a statistically significant, deterministic change in downstream computational metrics. |
| **4** | **Temporal Correctness** | Memory influence must be synchronized with the Phase 9.6 turn commit barrier; zero race conditions with background daemons. |
| **5** | **Reversibility & Decay** | When the recalling stimulus ceases, recollection resonance must decay toward zero, returning the system toward baseline. |
| **6** | **Ablation Sensitivity** | Disabling recollection must cleanly revert system behavior to the Candidate A baseline without orphaned state. |
| **7** | **Cross-Stimulus Specificity** | Recalling a strong emotional memory must not inappropriately contaminate subsequent unrelated, orthogonal stimuli. |
| **8** | **Runaway Resistance** | Repeated retrieval of the same salient memory over multiple consecutive turns must not trigger an escalating positive-feedback spiral. |

---

## 6. Candidate Selection Rules

1. **Failure Rule**: If no candidate demonstrates stability, boundedness, and causal efficacy, Candidate A remains the production baseline and memory coupling is marked `NOT SUPPORTED`.
2. **Promotion Rule**: A candidate that passes all 8 criteria is classified as `CAUSALLY SUPPORTED — RESEARCH RESULT`. It is **not** automatically merged into production code; it awaits architectural decision and formal regression verification.
3. **Plurality Rule**: If multiple candidates remain viable with distinct trade-offs, all viable candidates are documented as competing architectural options.

---

## 7. Four-Level Evidence Taxonomy

To prevent confounding isolated research simulations with canonical production architecture, evidence is classified across four distinct levels:

- **Level 1 — Mathematical / Local Implementability**:
  The candidate's data structures and mathematical operations execute correctly without numerical divergence, syntax errors, or invalid states.
- **Level 2 — Mechanistic Support Under Controlled Intervention**:
  When the candidate coupling mechanism is explicitly invoked via research helpers, downstream variables change in the predicted direction. (Valid in research isolation; does not imply canonical reachability).
- **Level 3 — Canonical End-to-End Causal Demonstration**:
  The causal pathway operates autonomously through `CognitiveOrchestrator.process()` without an external test helper manually invoking the coupling. Memory retrieval occurring during turn $t$ must demonstrably affect downstream stages before those stages execute.
- **Level 4 — Production Promotion Maturity**:
  Satisfies all 12 production promotion gates (canonical integration, causal intervention, temporal ordering, reproducibility, ablation, specificity, boundedness, reversibility, multi-turn stability, no cross-stimulus interference, no runaway feedback, zero self-model/identity implications).

---

## 8. Phase 11.5 Independent Evidence Audit & Production Promotion Decision

### 8.1 Canonical Pipeline Ordering Finding
Direct source inspection of `CognitiveOrchestrator._execute_pipeline` establishes the invariant execution sequence:
$$\text{Stage 4: Prediction Surprise} \longrightarrow \text{Stage 5: Somatic Markers \& Policy Selection} \longrightarrow \text{Stage 6: Affective Ecphory} \longrightarrow \text{Stage 7: Prompt Assembly}$$

**Architectural Consequence**: Because Affective Ecphory (Memory Retrieval) executes at Stage 6, it strictly follows Stage 4 (Active Inference) and Stage 5 (Somatic Markers and Generation Policy Selection). Within a single canonical turn $t$, memory retrieval cannot causally influence Stage 4 or Stage 5 of turn $t$. 

### 8.2 Negative Controls & Causal Attribution Audit
Six independent negative controls were benchmarked in `TestPhase11_5_IndependentAuditAndNegativeControls`:
1. **Control 1 (Fake Recollection)**: A synthetic $r(t)$ vector fabricated without memory retrieval produces identical somatic and policy changes to genuine memory recollection. Downstream coupling is **vector-dependent rather than memory-identity-dependent**.
2. **Control 2 (Retrieval Without Recollection)**: Memory retrieval without recollection synthesis leaves somatic markers and policy thresholds at baseline.
3. **Control 3 (Recollection Without Coupling)**: Recollection exists, but with coupling disabled ($\alpha=0, \beta=0, \gamma=0$), downstream variables remain at baseline.
4. **Control 4 (Coupling Without Memory)**: Empty memory produces resting recollection, leaving downstream variables at baseline.
5. **Control 5 (Orthogonal Memory)**: Orthogonal memories produce sub-threshold resonance, resulting in zero/negligible downstream shift.
6. **Control 6 (Specificity Gradient)**: Relevant memory elevates tension and lowers deliberative threshold, whereas Irrelevant memory (opposing PAD) and No memory produce identical baseline responses ($\Delta \mathcal{T} = 0.0, \theta = 0.60$).

### 8.3 Candidate A–E Four-Level Evidence Matrix

| Candidate | Level 1 (Local) | Level 2 (Mechanistic) | Level 3 (End-to-End) | Level 4 (Production) | Evidence Basis | Status / Decision |
|---|:---:|:---:|:---:|:---:|---|---|
| **A: Retrieval Only** | **PASS** | **PASS** | **PASS** | **PASS** | Canonical Ecphory $\to$ Prompt Context | **PRODUCTION BASELINE** |
| **B: Isolated $r(t)$** | **PASS** | **PASS** | **N/A** (Passive) | **FAIL** | Standalone research dataclass; experimental clamp | **RESEARCH ONLY** |
| **C: Recollection $\to$ L3** | **PASS** | **PASS** | **FAIL** | **FAIL** | Helper `couple_recollection_to_l3`; blocked by Stage 6 ordering | **RESEARCH ONLY** |
| **D: Recollection $\to$ L4** | **PASS** | **PARTIAL** | **FAIL** | **FAIL** | Matrix drift risk; requires clipping safeguards | **RESEARCH ONLY** |
| **E: Recollection $\to$ Policy** | **PASS** | **PASS** | **FAIL** | **FAIL** | Helper `get_effective_deliberative_threshold`; blocked by Stage 6 ordering | **RESEARCH ONLY** |

### 8.4 Production Promotion Gate Evaluation
1. Level 3 Canonical End-to-End Causality: **FAIL** (Ecphory executes at Stage 6, after Stages 4 & 5).
2. Memory-Specific Attribution: **PARTIAL** (Specific in retrieval resonance, but downstream coupling helper is vector-dependent).
3. Temporal Ordering Correctness: **FAIL for same-turn coupling** (Requires pipeline reordering or inter-turn state persistence).
4. Production Promotion Maturity: **UNMET**.

### 8.5 Definitive Production Decision

$$\textbf{NO PROMOTION — CONTINUE RESEARCH}$$
$$\textbf{Active Production Baseline: Candidate A (Retrieval Only)}$$

No candidate satisfies the promotion gate. No promotion ADR will be created. Production cognition code (`CognitiveOrchestrator`, `EmotionCore`, `HomeostaticEngine`, `ActiveInferenceEngine`) remains strictly unaltered.

