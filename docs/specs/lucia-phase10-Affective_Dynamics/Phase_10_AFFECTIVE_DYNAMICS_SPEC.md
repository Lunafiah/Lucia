# Lucia Phase 10 — Canonical Affective Dynamics Specification

> **Authoritative Specification: Mathematical Formulation, State Taxonomy, Temporal Execution Contract, Causal Mechanics, and Epistemic Foundation for Lucia's Affective System**  
> **Status:** Active Truth (Phase 10)  
> **Directory:** `docs/specs/lucia-phase10-Affective_Dynamics/Phase_10_AFFECTIVE_DYNAMICS_SPEC.md`  
> **Authority Level:** Authoritative Specification

---

## 1. Executive Summary & Epistemic Posture

This document provides the authoritative, implementation-faithful mathematical and computational specification of **Affective Dynamics** in Lucia (Phase 10). It formalizes the continuous dynamical state equations, regulatory mechanisms, temporal execution guarantees, causal influence pathways, and empirical boundaries governing Lucia's limbic, homeostatic, and cognitive systems.

### 1.1 Official System Roadmap

In accordance with architectural consensus, the research and development roadmap of Lucia is established as:

```text
Phase 10 — Affective Dynamics (Active / Current)
        ↓
Phase 11 — Affective Memory (Next Milestone)
        ↓
Phase 12 — Embodiment
        ↓
Phase 13 — Affective Life
        ↓
Phase 14 — First Activation
        ↓
Future Research — Self-Model / Self-Awareness
```

### 1.2 Scope Boundary & Invariants

Phase 10 is strictly bounded by the following negative invariants:
1. **NO Self-Model**: Lucia does not construct or maintain an explicit declarative representation of herself as an entity.
2. **NO Self-Awareness / Consciousness**: No psychological sentience, subjective phenomenology, or qualia are claimed or modeled.
3. **NO Anthropomorphic Self-Narratives**: Prompts and models are strictly forbidden from uttering introspective self-declarations (*"I feel sad"*, *"I am happy"*, *"As an AI, I have no feelings"*).
4. **NO Memory → Affect Feedback**: Memory remains an **open-loop sink**. Experience traces and PAD snapshots are consolidated into sparse distributed memory, and ecphory produces an echo vector that solely enters prompt context. Memory retrieval does **not** feed back into limbic hidden state $h$, homeostatic somatic markers, or active inference belief state.
5. **Phase 9.6 Invariant Preservation**: The temporal commit barrier (`commit_stimulus`), lock hierarchy, and deterministic state synchronization established in Phase 9.6 remain immutable.
6. **No Threshold Tampering**: Deliberative threshold $\theta_{\text{deliberative}} = 0.60$ and tension threshold $\theta_{\text{tension}} = 0.40$ are preserved without modification.

### 1.3 Epistemic Classification Scheme

Every equation, parameter, and theoretical claim in this document is labeled using the mandatory six-tier taxonomy:
- `ARCHITECTURAL INVARIANT`: Mandatory rule or structural design invariant that cannot be violated without breaking system correctness.
- `IMPLEMENTATION FACT`: Direct, verified behavior of active Python/NumPy/Scipy code in the current repository.
- `EMPIRICALLY SUPPORTED`: Demonstrated through controlled experimentation, pilot runs, or automated test suites.
- `EXPLORATORY OBSERVATION`: Preliminary empirical signal observed under small sample sizes ($N \le 10$) requiring cautious interpretation.
- `HYPOTHESIS`: Theoretical proposition or expected property awaiting experimental falsification.
- `UNKNOWN`: Quantities or dynamics whose properties cannot currently be determined from available code or data.

---

## 2. Computational Definitions of Affect

In Lucia, **affect** is defined strictly in operational, dynamical, and computational terms:

```text
Affect ≠ Subjective Feeling
Affect ≠ Consciousness
Affect ≠ Autobiographical Self
Memory ≠ Narrative Identity
```

Affect is a **continuous dynamical state vector** operating within a pre-reflective physiological-like state machine:
1. **Mathematical Nature**: Affect is an unobserved dynamical latent vector $h(t) \in [-1, 1]^{32}$ governed by a non-linear ordinary differential equation (Liquid Time-Constant network) and projected into a 3-dimensional bounded continuous space (Pleasure-Arousal-Dominance, $p(t) \in [-1, 1]^3$).
2. **Operational Role**: Affect acts as an intermediate regulator that couples sensory input encoding (Layer 1) to behavioral constraints and sampling parameters (Layer 6).
3. **Pre-Reflective Consequence**: Affect modulates computational resource allocation:
   - High cognitive load / depleted energy $\implies$ tight token budget (`max_tokens`), elevated response latency (`latency_ms`).
   - High prediction surprise / tension $\implies$ structured reasoning depth ($k=2$), lower temperature.
   - High vitality / arousal $\implies$ higher sampling entropy (higher temperature).

---

## 3. Three-Tier State Taxonomy

To prevent collapsing heterogeneous signals into a monolithic "emotion vector", the system formalizes three distinct state tiers:

```
┌────────────────────────────────────────────────────────────────────────┐
│                        THREE-TIER STATE TAXONOMY                       │
├────────────────────────────────────────────────────────────────────────┤
│  CATEGORY A: PERSISTENT DYNAMICAL STATE                                │
│    - Latent hidden vector: h(t) ∈ [-1, 1]³²                            │
│    - Projected PAD vector: p(t) ∈ [-1, 1]³                             │
│    - Update mechanism: Scipy solve_ivp (RK45) LTC ODE                  │
│    - Cadence: 200 ms FastLoop daemon + deterministic turn commit       │
│    - Persistence: Continuous across turns; decays toward equilibrium   │
├────────────────────────────────────────────────────────────────────────┤
│  CATEGORY B: ACCUMULATED PHYSIOLOGICAL / REGULATORY STATE              │
│    - Metabolic energy: E(t) ∈ [0.0, 1.0]                               │
│    - Cognitive load: C(t) ∈ [0.0, 1.0]                                 │
│    - Input timestamp window: W_{60s} (rolling deque)                   │
│    - Update mechanism: Monotonic drain on input; idle recovery timer   │
│    - Persistence: Persists across turns; recovers after 60s inactivity │
├────────────────────────────────────────────────────────────────────────┤
│  CATEGORY C: INSTANTANEOUS / DERIVED SIGNALS                           │
│    - Prediction surprise: S_t = ||A·p + b - q||_2                      │
│    - Acute tension: T_t = |v - P_{01}| + α_t · (S_t - θ_t)_+           │
│    - Somatic markers: Stability, modulated Load, Energy, Tension       │
│    - Generation policy: mode ∈ {fatigued, reflexive, deliberative}     │
│    - Lifetime: Ephemeral to turn t; zero inter-turn state carryover    │
└────────────────────────────────────────────────────────────────────────┘
```

### 3.1 Category A: Persistent Dynamical State
- **State Space**: $h(t) \in [-1.0, 1.0]^{32}$ (hidden state); $p(t) \in [-1.0, 1.0]^3$ (PAD snapshot).
- **Transition Function**: Governed by the Liquid Time-Constant (LTC) ODE:
  $$\frac{dh}{dt} = \frac{-y_c + \tanh(W_f y_c + U_f x + b_f)}{\text{softplus}(W_\tau y_c + U_\tau x + b_\tau)}$$
- **Persistence**: Persists continuously in memory. Evolves with physical time or virtual clock.
- **Stimulus Dependency**: Driven by stimulus vector $x(t) \in \mathbb{R}^{16}$. When $x = \mathbf{0}$, transitions autonomously via internal decay dynamics.
- **Cadence**: Integrated every `loop_cadence_ms` (200 ms) in `EmotionCore-FastLoop`, or advanced synchronously during a turn barrier via `commit_stimulus()`.
- **Classification**: `IMPLEMENTATION FACT`.

### 3.2 Category B: Accumulated Physiological/Regulatory State
- **State Space**: $\mathcal{E} \in [0.0, 1.0]$ (Energy); $\mathcal{C} \in [0.0, 1.0]$ (Cognitive Load); rolling input deque $W_{60s}$.
- **Transition Rules**:
  - $\mathcal{E}_{t} = \max(0.0, \mathcal{E}_{t-1} - 0.05)$ per received input turn.
  - Idle recovery: $+0.02/\text{second}$ when idle duration exceeds 60 seconds ($\Delta t_{\text{idle}} \ge 60.0$).
  - Cognitive load: Derived from input frequency in 60s window plus arousal magnitude.
- **Persistence**: Retained in `HomeostaticEngine` across conversation turns.
- **Classification**: `IMPLEMENTATION FACT`.

### 3.3 Category C: Instantaneous / Derived Signals
- **State Space**:
  - Prediction surprise $\mathcal{S}_t \in [0.0, \sqrt{12}] \approx [0.0, 3.464]$.
  - Acute tension $\mathcal{T}_t \in [0.0, 1.0]$.
  - Generation policy mode $M_t \in \{\text{fatigued}, \text{reflexive}, \text{deliberative}\}$.
  - Behavioral constraints: `max_tokens`, `temperature`, `latency_ms`, `reasoning_depth`.
- **Lifetime**: Derived strictly within turn $t$ and published in `CognitiveTurnResult`. No persistent internal memory across turns (e.g. Tension does not integrate across turns; it resets each turn based on input valence and instantaneous surprise).
- **Classification**: `IMPLEMENTATION FACT`.

---

## 4. Mathematical Specification

### 4.1 Liquid Time-Constant (LTC) Limbic ODE

The core limbic dynamics are modeled as a Liquid Time-Constant recurrent neural network implemented in `src/core/emotion/emotion_core.py`.

Given:
- Hidden state: $h \in \mathbb{R}^{32}$
- Input stimulus: $x \in \mathbb{R}^{16}$
- Weight matrices: $W_f \in \mathbb{R}^{32 \times 32}$, $U_f \in \mathbb{R}^{32 \times 16}$, $b_f \in \mathbb{R}^{32}$
- Time-constant parameters: $W_\tau \in \mathbb{R}^{32 \times 32}$, $U_\tau \in \mathbb{R}^{32 \times 16}$, $b_\tau \in \mathbb{R}^{32}$
- Step size: $\Delta t = \text{ode\_step\_size} = 0.05$ (configurable)

**Vector Differential Equation (Implementation-Faithful)**:
$$\frac{dy}{dt} = \frac{-y_c + \tanh(W_f y_c + U_f x + b_f)}{\text{softplus}(W_\tau y_c + U_\tau x + b_\tau)}$$
where:
$$y_c = \text{clip}(y, -1.0, 1.0)$$
$$\text{softplus}(z) = \ln(1 + e^z)$$

**Numerical Integration**:
Solved using `scipy.integrate.solve_ivp`:
- Method: Explicit Runge-Kutta of order 5(4) (`RK45`).
- Span: $t \in [0.0, \Delta t]$.
- Maximum internal step: $\Delta t / 4.0 = 0.0125$.
- Post-step clamp:
  $$h_{\text{new}} = \text{clip}(result.y[:, -1], -1.0, 1.0)$$

*Epistemic Status*: `IMPLEMENTATION FACT`.

### 4.2 Linear PAD Projection

The 32-dimensional latent state $h$ is projected into 3D Pleasure-Arousal-Dominance space:
$$p_{\text{raw}} = W_{\text{proj}} h + b_{\text{proj}}$$
$$p = \text{clip}(p_{\text{raw}}, -1.0, 1.0)$$
where $W_{\text{proj}} \in \mathbb{R}^{3 \times 32}$ is initialized via Xavier uniform distribution and $b_{\text{proj}} = \mathbf{0} \in \mathbb{R}^3$.

*Epistemic Status*: `IMPLEMENTATION FACT`.

### 4.3 Active Inference Free Energy & Belief Updating

`ActiveInferenceEngine` maintains an online linear generative model predicting PAD state transitions from $p_{\text{initial}}$ to $p_{\text{final}}$:
$$\hat{q} = A p_{\text{initial}} + b$$
where $A \in \mathbb{R}^{3 \times 3}$ is initialized to $I_3$ and $b \in \mathbb{R}^3$ is initialized to $\mathbf{0}$.

**Prediction Error / Surprise**:
$$\delta = \hat{q} - p_{\text{final}}$$
$$\mathcal{S} = \|\delta\|_2 = \sqrt{\sum_{i=1}^3 (\hat{q}_i - p_{\text{final}, i})^2}$$
*(If $\|p_{\text{initial}}\|_2 = 0.0$, the engine exits early with $\mathcal{S} = 0.0$ to prevent ill-conditioned updates).*

**Free Energy Objective**:
$$\mathcal{F}(A, b) = \|\hat{q} - p_{\text{final}}\|_2^2 + \lambda_{KL} \|A - I\|_F^2$$
where $\lambda_{KL} = \text{kl\_weight} = 0.01$.

**Analytic Gradients**:
$$\frac{\partial \mathcal{F}}{\partial A} = 2 \delta p_{\text{initial}}^T + 2 \lambda_{KL} (A - I)$$
$$\frac{\partial \mathcal{F}}{\partial b} = 2 \delta$$

**Parameter Update**:
$$A \leftarrow \text{clip}(A - \eta \frac{\partial \mathcal{F}}{\partial A}, -2.0, 2.0)$$
$$b \leftarrow b - \eta \frac{\partial \mathcal{F}}{\partial b}$$
where $\eta = \text{learning\_rate} = 10^{-3}$.

*Epistemic Status*: `IMPLEMENTATION FACT`.

### 4.4 Homeostatic Somatic Markers

Let normalized PAD coordinates be mapped from $[-1, 1]$ to $[0, 1]$:
$$P_{01} = \frac{P + 1}{2}, \quad A_{01} = \frac{A + 1}{2}, \quad D_{01} = \frac{D + 1}{2}$$

1. **Stability**:
   $$\text{base} = 1.0 - 2 \max(0, A_{01} - 0.5)$$
   $$\text{penalty} = 2 \max(0, 0.5 - D_{01})$$
   $$\text{Stability}_{\text{raw}} = \text{base} - \text{penalty} \cdot (1.0 - \text{base})$$
   $$\text{Stability} = \text{clip}(\text{Stability}_{\text{raw}}, 0.0, 1.0)$$

2. **Cognitive Load**:
   $$\text{freq\_comp} = \text{clip}\left(\frac{|W_{60s}|}{10.0}, 0.0, 1.0\right)$$
   $$\text{arousal\_comp} = \text{clip}(2 \max(0, A_{01} - 0.5), 0.0, 1.0)$$
   $$\text{Load}_{\text{base}} = \frac{\text{freq\_comp} + \text{arousal\_comp}}{2.0}$$

3. **Energy**:
   $$\mathcal{E}_t = \max(0.0, \mathcal{E}_{t-1} - 0.05)$$
   $$\mathcal{E}_{\text{idle}} = \min(1.0, \mathcal{E} + 0.02 \cdot \max(0, \Delta t_{\text{idle}} - 60.0))$$

4. **Tension (Base)**:
   $$\mathcal{T}_{\text{base}} = |v - P_{01}| \quad \text{if } v \text{ is provided, else } 0.0$$

*Epistemic Status*: `IMPLEMENTATION FACT`.

### 4.5 Surprise Coupling Policy

`SurpriseModulationPolicy` modulates base somatic markers via Active Inference prediction error $\mathcal{S}$:
$$\text{Cognitive Load}_{\text{final}} = \min(1.0, \text{Load}_{\text{base}} + \alpha_{cl} \cdot \mathcal{S})$$
$$\text{Tension}_{\text{final}} = \min(1.0, \mathcal{T}_{\text{base}} + \alpha_t \cdot \max(0, \mathcal{S} - \theta_{\text{tension}}))$$
with configured parameters:
- $\alpha_{cl} = 0.25$
- $\alpha_t = 0.35$
- $\theta_{\text{tension}} = 0.40$

*Epistemic Status*: `IMPLEMENTATION FACT`.

### 4.6 Generation Policy & Behavioral Constraints

1. **Policy Selection**:
   $$M_t = \begin{cases}
   \text{fatigued}, & \text{if } \mathcal{E} \le 0.20 \\
   \text{deliberative}, & \text{if } \mathcal{S} \ge \theta_{\text{deliberative}} \text{ or } \mathcal{T}_{\text{final}} \ge 0.70 \\
   \text{reflexive}, & \text{otherwise}
   \end{cases}$$
   where $\theta_{\text{deliberative}} = 0.60$.

2. **Base Constraints Mapping**:
   $$\text{max\_tokens}_{\text{base}} = \begin{cases}
   60, & \text{if } \text{Load} > 0.75 \\
   350, & \text{if } \text{Load} < 0.30 \text{ and } \mathcal{E} > 0.70 \\
   150, & \text{otherwise}
   \end{cases}$$
   $$\text{temperature}_{\text{base}} = \begin{cases}
   1.0, & \text{if } A_{01} > 0.70 \\
   0.5, & \text{if } A_{01} < 0.30 \text{ and } \text{Stability} > 0.70 \\
   0.75, & \text{otherwise}
   \end{cases}$$
   $$\text{latency\_ms}_{\text{base}} = \begin{cases}
   500, & \text{if } \text{Load} > 0.80 \text{ and } \mathcal{E} < 0.30 \\
   0, & \text{otherwise}
   \end{cases}$$

3. **Policy Adjustment**:
   $$\text{max\_tokens} = \max(1, \lfloor \text{max\_tokens}_{\text{base}} \cdot \mu_{\text{token}} \rfloor)$$
   $$\text{temperature} = \text{clip}(\text{temperature}_{\text{base}} + \Delta T, 0.01, 2.0)$$
   $$\text{reasoning\_depth} = k_{\text{policy}}$$
   where:
   - `fatigued`: $k=0, \Delta T = +0.10, \mu_{\text{token}} = 0.55, \text{scaffold} = 0$
   - `reflexive`: $k=1, \Delta T = 0.00, \mu_{\text{token}} = 1.00, \text{scaffold} = 1$
   - `deliberative`: $k=2, \Delta T = -0.10, \mu_{\text{token}} = 1.15, \text{scaffold} = 3$

*Epistemic Status*: `IMPLEMENTATION FACT`.

---

## 5. Temporal Execution Contract (Preserving Phase 9.6)

Phase 9.6 introduced a deterministic stimulus barrier preventing race conditions between background ODE integration and cognitive turn execution.

```text
Turn Entry (process(text))
   ↓ [Acquires _turn_lock]
Stage 1: Sensory Encoding (StimulusProcessor.encode)
   ↓
Stage 2: Generative Prior Expectation (pad_initial = EmotionCore.get_pad_state())
   ↓
Stage 3: Limbic Integration
   ├── token = push_stimulus(vector) [Acquires _stimulus_lock, queues FIFO]
   ├── pad_committed = commit_stimulus(token)
   │     ├── [Acquires _step_lock]
   │     ├── Drains pending queue up to token in FIFO order
   │     ├── Consumes vector, executes _ode_step(), updates self._h
   │     ├── Projects to pad_snapshot, marks _committed_stimulus_seq = token
   │     └── Releases _step_lock
   └── record_input() [Decrements Energy by 0.05, appends timestamp]
   ↓
Stage 4: Prediction Surprise & Belief Update
   ├── pad_final = pad_committed
   └── prediction_error = ActiveInference.step(pad_initial, pad_final)
   ↓
Stage 5: Homeostatic Modulation & Generation Policy
   ├── base_markers = compute_somatic_markers(pad_final)
   ├── markers = modulate_somatic(base_markers, prediction_error)
   └── select policy & derive final BehavioralConstraints
   ↓
Stage 6: Affective Ecphory (Query SDM with pad_final → echo_vector)
   ↓
Stage 7: Prompt Assembly & LLM Generation (PromptAssembler + LLMBackend)
   ↓
Stage 8: Affective Memory Consolidation (Store (stimulus, pad_final) into SDM)
   ↓
Stage 9: Plasticity Tagging (Queue sample if surprise ≥ 0.35)
   ↓
Stage 10: Construction & Emission of Frozen CognitiveTurnResult
   ↓ [Releases _turn_lock]
```

### 5.1 Lock Hierarchy

To prevent deadlocks and race conditions, all components must strictly adhere to the established lock ordering:
$$\_turn\_lock \implies \_step\_lock \implies \_train\_lock \implies \_stimulus\_lock \implies \_state\_lock$$

1. `_turn_lock` (`threading.Lock`, non-reentrant): Owned by `CognitiveOrchestrator.process()`. Serializes entire 10-stage pipeline.
2. `_step_lock` (`threading.Lock`): Serializes ODE stepping between the active turn thread and `FastLoop`.
3. `_train_lock` (`threading.Lock`): Serializes weight copies during ODE evaluation and weight swaps from offline training.
4. `_stimulus_lock` (`threading.Lock`): Protects `_pending_stimuli` FIFO deque and `_stimulus_seq` counter.
5. `_state_lock` (`threading.Lock`): Protects `_pad_snapshot` for microsecond-level non-blocking reads (`get_pad_state()`).

*Epistemic Status*: `ARCHITECTURAL INVARIANT`.

---

## 6. Causal Graph of the Active Subsystem

The causal graph formalizes how information flows through the system. We strictly distinguish between **causal influence**, **correlation**, **prompt context**, **body/UI expression**, and **telemetry only**.

```mermaid
graph TD
    User["User Input Text"] -->|Causal| L1["L1: StimulusProcessor"]
    L1 -->|Causal: 16D Vector| L2["L2: EmotionCore (LTC ODE)"]
    L2 -->|State Recurrence: h(t)| L2
    L2 -->|Causal: PAD Snapshot| L4["L4: Active Inference Engine"]
    L2 -->|Causal: PAD Snapshot| L3["L3: HomeostaticEngine"]
    
    L4 -->|Causal: Surprise S_t| L3Mod["SurpriseModulationPolicy"]
    L3 -->|Base Somatic Markers| L3Mod
    
    L3Mod -->|Causal: Somatic Markers| Pol["GenerationPolicy & Constraints"]
    Pol -->|Causal: max_tokens, k, temp| L6["L6: LLM Generation & Scaffolding"]
    
    L3Mod -->|Prompt Context: Numeric Values| PA["PromptAssembler"]
    PA -->|Prompt String| L6
    
    L2 -->|Query Key: pad_final| L5["L5: AffectiveMemory / Ecphory"]
    L5 -.->|Prompt Context: Echo Vector| PA
    
    L6 -->|Causal| Output["Assistant Response Text"]
    
    L2 -.->|Body Expression Only| UI["Electron Mascot / Avatar UI"]
    L3 -.->|Body Expression Only| UI
    
    L2 -.->|Telemetry Only| Stab["StabilityEvaluator / LSI"]
    L4 -.->|Telemetry Only| Stab
```

### Causal Classification Key:
- **Causal Influence**: A change in Variable A directly alters the mathematical or algorithmic trajectory of Component B.
- **Open-Loop Sink**: Information is stored or read out without feeding back into upstream limbic or homeostatic dynamics (e.g. L5 Memory consolidation and ecphory).
- **Prompt Context**: Values are serialized as static text strings and passed to the LLM prompt without altering sampling parameters directly.
- **Body / UI Expression**: Values are transmitted over IPC to Electron to drive sprite selection or lip-sync, with zero feedback to backend cognition.
- **Telemetry Only**: Values are logged or monitored by `StabilityEvaluator` (e.g. LSI) with zero influence on production generation.

*Epistemic Status*: `ARCHITECTURAL INVARIANT`.

---

## 7. Affect → Cognition Audit

Every path through which affective and homeostatic states influence cognition is cataloged below:

| Source Variable | Consumer Subsystem | Pipeline Stage | Mechanism | Measurable Computational Consequence | Causal Status |
|---|---|---|---|---|---|
| **Cognitive Load $\mathcal{C}$** | `HomeostaticEngine` | S5 | `_resolve_max_tokens` | $\mathcal{C} > 0.75 \implies \text{max\_tokens} \le 60$ | **Causal (Internal Modulation)** |
| **Cognitive Load $\mathcal{C}$ & Energy $\mathcal{E}$** | `HomeostaticEngine` | S5 | `_resolve_max_tokens` | $\mathcal{C} < 0.3 \land \mathcal{E} > 0.7 \implies \text{max\_tokens} \ge 350$ | **Causal (Internal Modulation)** |
| **Arousal $A_{01}$** | `HomeostaticEngine` | S5 | `_resolve_temperature` | $A_{01} > 0.7 \implies \text{temperature} = 1.0$ | **Causal (Internal Modulation)** |
| **Arousal $A_{01}$ & Stability** | `HomeostaticEngine` | S5 | `_resolve_temperature` | $A_{01} < 0.3 \land \text{Stab} > 0.7 \implies \text{temperature} = 0.5$ | **Causal (Internal Modulation)** |
| **Cognitive Load $\mathcal{C}$ & Energy $\mathcal{E}$** | `HomeostaticEngine` | S5 | `_resolve_latency_ms` | $\mathcal{C} > 0.8 \land \mathcal{E} < 0.3 \implies \text{latency} = 500\text{ms}$ | **Causal (Internal Modulation)** |
| **Energy $\mathcal{E}$** | `GenerationPolicy` | S5 | `select()` | $\mathcal{E} \le 0.20 \implies \text{mode} = \text{fatigued}, k=0, \text{scaffold}=0$ | **Causal (Internal Modulation)** |
| **Surprise $\mathcal{S}$ & Tension $\mathcal{T}$** | `GenerationPolicy` | S5 | `select()` | $\mathcal{S} \ge 0.60 \lor \mathcal{T} \ge 0.70 \implies \text{mode} = \text{deliberative}, k=2, \text{scaffold}=3$ | **Causal (Internal Modulation)** |
| **Somatic Markers** | `PromptAssembler` | S7 | String template | Formats `[SOMATIC STATE]` block in prompt | **Prompt Context** |
| **Echo Vector** | `PromptAssembler` | S7 | String template | Formats `[MEMORY ECHO]` block in prompt | **Prompt Context** |
| **PAD Snapshot** | Mascot Window | IPC | Electron IPC | Drives Avatar expression / blendshapes | **Body/UI Expression** |
| **Tick Jitter / Velocity** | `StabilityEvaluator` | Background | LSI formula | Generates `lsi` float in `/telemetry/stability` | **Telemetry Only** |

*Epistemic Status*: `IMPLEMENTATION FACT`.

---

## 8. Baseline and Relaxation Dynamics

### 8.1 Configured Baseline vs. Dynamical Equilibrium

A fundamental finding of the Phase 10 pre-implementation audit is the distinction between the **configured resting baseline** and the **mathematical dynamical equilibrium**:

1. **Configured Initial Baseline**:
   $$\text{resting\_baseline} = (P=+0.25, A=-0.05, D=+0.05)$$
   Configured in `EmotionConfig` and assigned to `_pad_resting` and `_pad_snapshot` at initialization or during `reset_to_resting()`.
2. **Dynamical Equilibrium Point**:
   In `EmotionCore`, the ODE RHS is:
   $$\frac{dh}{dt} = \frac{-y_c + \tanh(W_f y_c + U_f x + b_f)}{\text{softplus}(W_\tau y_c + U_\tau x + b_\tau)}$$
   Because $b_f = \mathbf{0}$ and $b_{\text{proj}} = \mathbf{0}$, when $x = \mathbf{0}$ and $h = \mathbf{0}$:
   $$\frac{dh}{dt}\Bigg|_{h=\mathbf{0}, x=\mathbf{0}} = \frac{-\mathbf{0} + \tanh(\mathbf{0})}{\text{softplus}(b_\tau)} = \mathbf{0}$$
   Furthermore, the projection is linear with zero bias:
   $$p = W_{\text{proj}} \cdot \mathbf{0} + \mathbf{0} = (0.0, 0.0, 0.0)$$

### 8.2 Empirical Relaxation Behavior

When a stimulus displaces $h$ from the origin, subsequent idle ticks ($x = \mathbf{0}$) cause the state to relax asymptotically toward $h^* = \mathbf{0}$ and $p^* = (0.0, 0.0, 0.0)$ (the neutral origin), rather than $(+0.25, -0.05, +0.05)$.

Key empirical observations:
- **Non-Monotonicity**: Due to cross-coupling terms in the random Xavier weight matrix $W_f$, individual PAD coordinates do **not** relax strictly monotonically. Transients may exhibit small damped oscillations before converging.
- **Absence of a Single Fixed $\tau$**: The decay rate is state-dependent because the denominator $\text{softplus}(W_\tau y_c + b_\tau)$ continuously adapts with $y_c$. Therefore, no single scalar time-constant $\tau$ describes the entire multidimensional relaxation.
- **Epistemic Classification**:
  - Configured baseline $(+0.25, -0.05, +0.05)$: `ARCHITECTURAL INVARIANT` (intended resting state).
  - Dynamical equilibrium at $(0, 0, 0)$: `IMPLEMENTATION FACT`.
  - Non-monotonic relaxation trajectories: `EMPIRICALLY SUPPORTED`.

---

## 9. Accumulation and Recovery Mechanics

### 9.1 Metabolic Energy

- **Depletion Rate**: $\Delta \mathcal{E} = -0.05$ per received input turn.
- **Exhaustion Horizon**: Starting from $\mathcal{E} = 1.0$, exactly 20 consecutive inputs without idle recovery will deplete energy to $\mathcal{E} = 0.0$.
- **Fatigue Threshold**: When $\mathcal{E} \le 0.20$ (after 16 consecutive inputs), `GenerationPolicy` enters `fatigued` mode, restricting $k=0$ and throttling tokens.
- **Recovery Dynamics**: Requires at least 60.0 seconds of continuous inactivity ($\Delta t_{\text{idle}} \ge 60.0$). Thereafter, recovers linearly at $+0.02/\text{second}$, requiring 50 additional seconds (110s total idle) to recover from $0.0$ to $1.0$.

*Epistemic Status*: `IMPLEMENTATION FACT`.

### 9.2 Cognitive Load

Cognitive load $\mathcal{C}$ is a composite metric reflecting environmental pace, internal arousal, and prediction surprise:
- **Frequency Saturation**: Saturated at 10 inputs within any sliding 60-second window ($|W_{60s}| \ge 10 \implies \text{freq\_comp} = 1.0$).
- **Arousal Coupling**: Increases linearly as normalized arousal exceeds $0.5$ ($A > 0.0$).
- **Surprise Coupling**: Instantly boosted by $+0.25 \cdot \mathcal{S}$ during cognitive turn processing.
- **Conditional Monotonicity**: Under controlled test conditions where inputs arrive rapidly ($\Delta t < 60\text{s}$) with constant non-negative arousal, $\text{freq\_comp}$ increases monotonically until saturation. Cognitive load is **conditionally monotonic** under zero-recovery regimes, but not unconditionally monotonic in general.

*Epistemic Status*: `IMPLEMENTATION FACT`.

---

## 10. Embodiment Boundary (Future Phase 12 Interface)

Phase 10 formalizes the boundary where internal affect will interface with external embodiment in Phase 12, without implementing Phase 12 features prematurely:

```text
┌───────────────────────────────────────────────┐
│            INTERNAL AFFECTIVE ENGINE          │
│   h(t) ∈ [-1, 1]³²  ──→  PAD p(t) ∈ [-1, 1]³  │
└───────────────────────┬───────────────────────┘
                        │
                        │ Outward Projection (IPC)
                        ▼
┌───────────────────────────────────────────────┐
│            EMBODIMENT BOUNDARY (PHASE 12)     │
├───────────────────────────────────────────────┤
│  1. Avatar Facial Geometry & Blendshapes      │
│     P (Pleasure)   ──→ MouthSmile / BrowUp    │
│     A (Arousal)    ──→ EyeWide / BlinkRate    │
│     D (Dominance)  ──→ HeadTilt / Posture     │
│                                               │
│  2. Voice Prosody (RVC Synthesis)             │
│     Arousal        ──→ Pitch scale / Tempo    │
│     Pleasure       ──→ Pitch contour offset   │
│                                               │
│  3. Physical Mascot Spatial Dynamics          │
│     Dominance      ──→ Mascot window inertia  │
│     Arousal        ──→ Micro-idle jitter      │
└───────────────────────────────────────────────┘
```

**Crucial Distinction**:
$$\text{Internal Causal Affect} \neq \text{Visual / Vocal Representation}$$
The avatar's visual render and RVC voice prosody are **downstream expressions** (actuators). They have zero backward causal authority over $h(t)$ or homeostatic regulation.

*Epistemic Status*: `ARCHITECTURAL INVARIANT` (Boundary Definition).

---

## 11. Affective History: Persistence vs. Hysteresis

To maintain rigorous scientific precision, Phase 10 distinguishes between **State Persistence** and **Historical Hysteresis**:

### 11.1 State Persistence (First-Order Recurrence)
$$State(t+1) = f(State(t), \text{Stimulus}(t+1))$$
Because $h(t)$ is continuous and integrated across turns, the hidden state at $t+1$ depends on the state at $t$. This is standard first-order stateful recurrence.

### 11.2 Historical Hysteresis (Path Dependence)
Given the identical probe stimulus $X$, injected into two systems that currently exhibit the same scalar metric or baseline, but arrived via different historical trajectories:
$$\text{Trajectory } A \neq \text{Trajectory } B \implies Response(X \mid H_A) \neq Response(X \mid H_B)$$
Path dependence arises because the 32-dimensional hidden vector retains multi-dimensional phase information that cannot be captured by a single scalar. Different prior emotional experiences leave residual activation patterns in orthogonal subspaces of $h$, causing identical subsequent stimuli to trigger divergent trajectories.

*Epistemic Status*: `EMPIRICALLY SUPPORTED` (Confirmed via Test F and Ablation v1 Exploratory Pilot).

---

## 12. Phase 11 Memory Boundary Evaluation

Phase 10 strictly maintains Memory as an **open-loop sink**. Experience traces and PAD states are stored in Kanerva Sparse Distributed Memory (SDM), and ecphory produces an echo vector injected into prompt context.

Before Phase 11 introduces any causal feedback from Memory to Affect, Phase 10 formally evaluates the four candidate destinations across nine architectural criteria:

```text
Candidate Destinations for Memory → Affect Feedback:
  Destination A: Memory → L2 (Limbic Hidden State h)
  Destination B: Memory → L3 (Homeostatic Somatic Markers)
  Destination C: Memory → L4 (Active Inference Belief State A, b)
  Destination D: Memory → Separate Recollection State r(t)
```

### 12.1 Evaluation Matrix (9 Architectural Criteria)

| Criterion | Destination A: Memory → L2 ($h$) | Destination B: Memory → L3 (Somatic) | Destination C: Memory → L4 (Beliefs) | Destination D: Memory → Separate State $r(t)$ |
|---|---|---|---|---|
| **1. Causal Clarity** | Moderate: Mixes external sensory stimulus with memory retrieval in continuous ODE. | High: Directly adjusts physiological markers without corrupting limbic ODE. | Low: Conflates generative transition priors with historical memory content. | **Highest**: Completely separates affective memory retrieval from limbic ODE dynamics. |
| **2. Temporal Correctness** | Risky: Feeding retrieved traces into $h$ during a turn risks ODE instability and race conditions. | Safe: Clean per-turn adjustment at Stage 5. | Safe: Clean per-turn adjustment at Stage 4. | **Safest**: Explicit recollection state updated synchronously with turn barrier. |
| **3. Architectural Coherence** | Low: Violates L2 role as pre-reflective raw limbic state machine. | Moderate: Somatic markers are physiological, not mnemonic. | Low: Active Inference models transitions, not episodic storage. | **Highest**: Preserves clean layering; recollection acts as Layer 5.5 bridge. |
| **4. Dynamical Stability** | **High Risk**: Positive feedback loop (L2 → Store → Query → L2) can trigger runaway ODE explosion. | Moderate: Somatic markers are strictly clamped to $[0, 1]$. | Moderate: Risk of destabilizing generative transition matrix $A$. | **High Stability**: Recollection state can be bounded and decayed independently. |
| **5. Observability** | Poor: Memory influence is buried inside 32D hidden vector $h$. | Moderate: Modulates visible somatic floats. | Poor: Concealed within $3 \times 3$ matrix $A$. | **Highest**: Dedicated vector $r(t)$ directly logged in `CognitiveTurnResult`. |
| **6. Controllability** | Low: Cannot easily decouple memory influence from sensory stimulus. | High: Scaled via dedicated gain parameter $\beta_{\text{mem}}$. | Low: Complex non-linear gradient interaction. | **High**: Gated via explicit recall weighting $\gamma \in [0, 1]$. |
| **7. Specificity** | Low: Diffuse projection across all 32 dimensions. | Moderate: Modulates load or tension specifically. | Low: Affects all transition predictions uniformly. | **High**: Can carry content-specific emotional resonance. |
| **8. Testability** | Hard: Disentangling stimulus response from memory echo in $h$ is mathematically difficult. | Easy: Unit tests can verify marker shifts with and without memory traces. | Moderate: Requires checking belief matrix convergence. | **Easiest**: Clean ablation possible by setting $r(t) = \mathbf{0}$. |
| **9. Feedback Runaway Risk** | **Severe**: High memory resonance could self-excite $h$ in a positive feedback loop. | Low: Somatic markers decay or are bounded. | Moderate: Belief drift over long sessions. | **Low**: Independent decay engine can isolate recollection decay. |

### 12.2 Research Recommendation for Phase 11

Based on this evaluation:
1. **Direct injection into L2 ($h$) is strongly discouraged** due to feedback runaway risk and loss of dynamical observability.
2. **Destination D (Separate Recollection State $r(t)$)** combined with controlled gating into **Destination B (L3 Somatic Modulation)** provides the optimal trade-off of causal clarity, stability, testability, and feedback safety.
3. This evaluation defines the **Phase 11 research boundary**. No implementation decisions are enacted in Phase 10.

*Epistemic Status*: `HYPOTHESIS` / `ARCHITECTURAL RECOMMENDATION`.

---

## 13. Summary Epistemic Classification Table

| System Property | Description | Epistemic Classification | Evidence Source |
|---|---|---|---|
| **Pre-Reflective Affect** | Affect operates as unconscious dynamical vector without declarative self-reports. | `ARCHITECTURAL INVARIANT` | `AGENTS.md`, `PHASE_9.md` |
| **One Continuous Life** | Single permanent companion instance without character switchers. | `ARCHITECTURAL INVARIANT` | `AGENTS.md` |
| **Phase 9.6 Synchronization** | Stimulus FIFO queue and commit barrier serialize L2 transitions before L4 reads. | `ARCHITECTURAL INVARIANT` | `test_temporal_synchronization.py` |
| **LTC ODE Formulation** | $dy/dt = (-y_c + \tanh(W_f y_c + U_f x + b_f)) / \text{softplus}(W_\tau y_c + U_\tau x + b_\tau)$ | `IMPLEMENTATION FACT` | `emotion_core.py` L246-251 |
| **Linear PAD Projection** | $p = \text{clip}(W_{\text{proj}} h + b_{\text{proj}}, -1.0, 1.0)$ | `IMPLEMENTATION FACT` | `emotion_core.py` L270-277 |
| **Active Inference Free Energy** | $\mathcal{S} = \|\hat{q} - q\|_2$, gradient descent updates $A, b$ with KL regularization. | `IMPLEMENTATION FACT` | `active_inference.py` L120-138 |
| **Metabolic Energy Drain** | $-0.05$ per turn; $+0.02/\text{s}$ idle recovery after 60s idle. | `IMPLEMENTATION FACT` | `homeostatic_engine.py` L89, L279 |
| **Acute Tension Signal** | $|v - P_{01}| + 0.35 \max(0, \mathcal{S} - 0.40)$; zero inter-turn carryover. | `IMPLEMENTATION FACT` | `policies.py` L77-78 |
| **Generation Policy Modes** | Three discrete modes (fatigued, reflexive, deliberative) modulating tokens, temp, $k$. | `IMPLEMENTATION FACT` | `policies.py` L183-234 |
| **Dynamical Equilibrium at Origin** | Unforced ODE ($x=0$) relaxes asymptotically to $h^*=0, p^*=(0,0,0)$, not Philia. | `IMPLEMENTATION FACT` | Pre-implementation ODE audit |
| **Non-Monotonic Relaxation** | Transients in PAD during idle decay show small non-monotonic oscillations. | `EMPIRICALLY SUPPORTED` | `test_affective_dynamics.py` Test E |
| **Affective Hysteresis** | Identical stimulus probe after different histories yields divergent states. | `EMPIRICALLY SUPPORTED` | `test_affective_dynamics.py` Test F |
| **Downstream Computational Modulation** | Somatic markers deterministically alter `max_tokens` and reasoning depth $k$. | `EMPIRICALLY SUPPORTED` | `test_affective_dynamics.py` Test G |
| **Recollection State $r(t)$ for Phase 11** | Destination D evaluated as superior candidate for Memory → Affect boundary. | `HYPOTHESIS` | Phase 10 Memory Boundary Audit |
| **Subjective Phenomenology** | Subjective experience, qualia, or conscious feelings in Lucia. | `UNKNOWN` / `STRICTLY UNCLAIMED` | `AGENTS.md` |

---

## 14. References & Documentation Authority

1. [`docs/00_PROJECT_OVERVIEW.md`](file:///c:/Users/Lunafiah/Desktop/My_project/Lucia/docs/00_PROJECT_OVERVIEW.md) — System architecture, Philia philosophy, milestone roadmap.
2. [`docs/ARCHITECTURE.md`](file:///c:/Users/Lunafiah/Desktop/My_project/Lucia/docs/ARCHITECTURE.md) — Concurrency model, lock hierarchy, process boundaries.
3. [`docs/MECHANISM.md`](file:///c:/Users/Lunafiah/Desktop/My_project/Lucia/docs/MECHANISM.md) — Mathematical formulations (ODE, SDM, LSI, Ecphory).
4. [`docs/CURRENT_STATUS.md`](file:///c:/Users/Lunafiah/Desktop/My_project/Lucia/docs/CURRENT_STATUS.md) — Subsystem status, active API routes, verification metrics.
5. [`docs/DESIGN_DECISIONS.md`](file:///c:/Users/Lunafiah/Desktop/My_project/Lucia/docs/DESIGN_DECISIONS.md) — ADRs (ADR-014 through ADR-021).
6. [`AGENTS.md`](file:///c:/Users/Lunafiah/Desktop/My_project/Lucia/AGENTS.md) — Mandatory agent rules, negative invariants, pre-reflective affect doctrine.
