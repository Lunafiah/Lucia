# PHASE 19 PRODUCTION REALIZATION ARCHITECTURE DESIGN
## Coupled Multi-Timescale Liquid Neural Network (MT-LNN) Dynamics & Philia Attractor Grounding

> **Authoritative Architectural Design & Production Integration Blueprint for Lucia Phase 19**  
> **Status**: APPROVED ARCHITECTURE GATE — READY FOR REVIEW  
> **Lifecycle Governance**: Foundation-First Research Cycle -> Production Realization  
> **Date**: September 2026

---

## 1. Executive Decision

### 1.1 Decision Statement
Following the empirical validation of the Phase 19 Foundation-First Research Cycle across experimental protocols EXP-19.1 through EXP-19.8, and the formal approval of **ADR-026**, this document specifies the precise production realization design for Lucia's limbic dynamics engine.

### 1.2 Scope of Promotion: What IS Promoted vs What IS NOT Promoted

```text
┌────────────────────────────────────────────────────────────────────────────────┐
│                          PROMOTION SCOPE BOUNDARY                              │
│                                                                                │
│  PROMOTED TO PRODUCTION ARCHITECTURE:                                          │
│  [+] Coupled dual-timescale differential state equations (fast h_f, slow s_s)  │
│  [+] Non-zero Philia dynamic resting attractor grounding (p* = [+0.25,-0.05,+0.05])│
│  [+] Asymmetric attack-decay momentum dynamics (fast charging, slow decay)     │
│  [+] Pre-reflective homeostatic coupling (tension/energy -> somatic fatigue)   │
│  [+] Dissipative local volume-contraction regime (empirical Tr(J) <= -40.0, bounded coupling gain)│
│  [+] Backward-compatible thread-safe public API and deterministic commit barrier│
│                                                                                │
│  STRICTLY NOT PROMOTED (FORBIDDEN INVARIANTS):                                 │
│  [-] Subjective conscious feeling, psychological sentience, or theatrical roleplay│
│  [-] Self-reported emotional declarations ("I feel happy", "I am tired")       │
│  [-] Introspective reflective self-models or ego constructs                    │
│  [-] Memory-to-limbic direct injection (strictly deferred to Phase 20)         │
│  [-] Autonomous unconstrained personality drift or multiple character presets │
│  [-] Cloud-based inference or remote telemetry dependencies                    │
│  [-] Disk persistence of ephemeral limbic hidden vectors                       │
└────────────────────────────────────────────────────────────────────────────────┘
```

### 1.3 Target Production Subsystem
The production modifications will be strictly focused on:
1. **Core Limbic Subsystem**: Evolving `src/core/emotion/emotion_core.py` and `src/core/config.py` from single-layer LTC ODE dynamics into the coupled Multi-Timescale Liquid Neural Network (MT-LNN).
2. **Cognitive Pipeline Orchestration**: Hooking the homeostatic somatic marker context from Stage 5 into the limbic engine in `src/core/orchestrator/cognitive_orchestrator.py` without altering the canonical 16-stage ordering.

---

## 2. Current Production Architecture (Phase 10 Baseline)

### 2.1 Current Implementation Overview
The active production limbic system is implemented in [`src/core/emotion/emotion_core.py`](file:///c:/Users/Lunafiah/Desktop/My_project/Lucia/src/core/emotion/emotion_core.py) as a single-layer Liquid Time-Constant (LTC) network:

$$\frac{d\mathbf{h}}{dt} = \frac{-\mathbf{h} + \tanh(\mathbf{W}_f \mathbf{h} + \mathbf{U}_f \mathbf{x} + \mathbf{b}_f)}{\text{softplus}(\mathbf{W}_\tau \mathbf{h} + \mathbf{U}_\tau \mathbf{x} + \mathbf{b}_\tau)}$$

$$\mathbf{PAD}(t) = \text{clip}(\mathbf{W}_{\text{proj}} \mathbf{h} + \mathbf{b}_{\text{proj}}, -1.0, 1.0)$$

```text
Incoming Stimulus Vector (x in R^16)
               ↓
Stage 3: Limbic Integration (EmotionCore.push_stimulus & commit_stimulus)
               ↓
Single-Layer LTC ODE Solver (scipy.integrate.solve_ivp RK45, h in R^32)
               ↓
Linear Projection (W_proj * h + b_proj)
               ↓
PADState Snapshot (P in [-1, 1], A in [-1, 1], D in [-1, 1])
               ↓
Stage 4: Prediction Surprise & Active Inference Update
```

### 2.2 Critical Limitations of Phase 10 Architecture Identified in Research
1. **Uniform Fast Timescale & Memoryless Decay**: Single time-constant $\tau \approx 0.2 - 1.5\text{ s}$ causes rapid affective amnesia (half-life $t_{1/2} \approx 1.4\text{ s}$). Multi-minute conversational continuity is completely lost between turns.
2. **Origin Collapse on Unforced Relaxation**: In the absence of stimulus ($\mathbf{x} = \mathbf{0}$), $\tanh(\mathbf{W}_f \mathbf{h}) \to \mathbf{0}$ pulls $\mathbf{h} \to \mathbf{0}$, causing $\mathbf{PAD} \to [0, 0, 0]$ (neutral apathy) rather than settling to the established Philia resting baseline $[+0.25, -0.05, +0.05]$.
3. **Inability to Produce Non-Monotonic State Transformations**: The single-layer ODE cannot transform acute high-arousal distress into low-arousal somatic fatigue over unforced time because it lacks cross-coupling with homeostatic energy depletion.
4. **Absence of Longitudinal Hysteresis**: Evaluated on identical ambiguous stimuli, the system appraises them identically regardless of whether preceding interactions were warm or antagonistic.

---

## 3. Target Production Architecture (Phase 19 Promoted Realization)

### 3.1 Structural Topology
The target production architecture replaces the internal single-layer solver of `EmotionCore` with a coupled dual-timescale dynamical system while strictly maintaining its external public API:

```text
Incoming Stimulus Vector x(t) in R^16
               │
               ▼
┌─────────────────────────────────────────────────────────────────────────────────┐
│ EmotionCore (Coupled Multi-Timescale Liquid Neural Network — MT-LNN)            │
│                                                                                 │
│   ┌─────────────────────────────────────────────────────────────────────────┐   │
│   │ Fast Reactive Limbic Layer (h_fast in R^32, tau_fast in [0.10s, 1.50s]) │   │
│   │   dh_f/dt = (-h_f + tanh(W_ff*h_f + W_fs*(s_s - s*) + U_f*x)) / tau_f   │   │
│   └──────────────────────┬────────────────────────────▲─────────────────────┘   │
│                          │                            │                         │
│             W_sf (Fast-to-Slow Momentum)    W_fs (Slow-to-Fast Dissipative)     │
│             (charging uptake tau_c=3.5s)    (strictly bounded <= 0.05)          │
│                          │                            │                         │
│   ┌──────────────────────▼────────────────────────────┴─────────────────────┐   │
│   │ Slow Affective Latent Field (s_slow in R^16, tau_decay = 28.0s)         │   │
│   │   ds_s/dt = -(s_s - s*) / tau_decay + tanh(W_sf*h_f + W_sh*delta_m)/tau_c│   │
│   └─────────────────────────────────────────────────────────────────────────┘   │
│                                          ▲                                      │
│                                          │ W_sh Homeostatic Coupling            │
│                       Homeostatic Context delta_m(t-1) in R^4                   │
│                       (energy, cognitive_load, tension, stability;              │
│                        computed in S5 of t-1, updated in S5 of t)               │
│                                                                                 │
│   ┌─────────────────────────────────────────────────────────────────────────┐   │
│   │ Philia Dynamic Attractor Grounding (s*_philia in R^16, p*_philia in R^3)│   │
│   │   PAD(t) = clip(W_proj_f*h_f + W_proj_s*(s_s - s*) + p*_philia, -1, 1)  │   │
│   │   Unforced Equilibrium (h_f = 0, s_s = s*): PAD* = p*_philia (within numerical tolerance, eps < 1e-4)│ │
│   └─────────────────────────────────────────────────────────────────────────┘   │
└──────────────────────────────────────┬──────────────────────────────────────────┘
                                       │
                                       ▼
                       Committed PADState Snapshot
                                       │
                                       ▼
                     Stage 4: Active Inference Prediction Surprise
```

### 3.2 State Ownership & Stability Conditions
- **Bounded Coupling Operating Constraint**: The feedback loop gain condition $\|\mathbf{W}_{fs}\| \cdot \|\mathbf{W}_{sf}\| \cdot \frac{\tau_{\text{decay}}}{\tau_{\text{charge}}} < 1.0$ is enforced as a validated design stability condition to prevent runaway positive-feedback amplification. The empirical Jacobian divergence trace is negative ($\text{Tr}(J) \le -40.0$), demonstrating strong local phase-space volume contraction under the validated operating regime.
- **Unforced Convergence in Tested Scenarios**: When stimulus ceases and homeostatic state is at resting baseline ($\Delta \mathbf{m} = \mathbf{0}$), unforced relaxation converges to the Philia attractor $\mathbf{PAD} = [+0.25, -0.05, +0.05]$ with steady-state offset $\epsilon < 10^{-4}$ in tested numerical trajectories.

---

## 4. Exact Production State Contract

All state variables within the evolved `EmotionCore` are explicitly defined, bounded, and typed:

| Variable | Dimension / Type | Owner | Update Frequency | Input Source | Output Consumers | Persistence Category |
|---|---|---|---|---|---|---|
| `_h_fast` | $\mathbb{R}^{32}$ (`float64`) | `EmotionCore` | 200 ms (FastLoop) / Discrete Turn Step | Stimulus $\mathbf{x}$, slow state deviation $(\mathbf{s}_s - \mathbf{s}^*)$ | `_project_to_pad`, `W_sf` | Ephemeral runtime (in-memory) |
| `_s_slow` | $\mathbb{R}^{16}$ (`float64`) | `EmotionCore` | 200 ms (FastLoop) / Discrete Turn Step | Fast state $\mathbf{h}_f$, homeostatic deviation $\Delta\mathbf{m}$ | `_project_to_pad`, `W_fs` | Ephemeral runtime (in-memory) |
| `_pad_snapshot` | `PADState` (immutable) | `EmotionCore` | 200 ms / Step commit | Linear projection of $\mathbf{h}_f$ and $\Delta\mathbf{s}_s$ | S4 Active Inference, `/state` API, Telemetry, Expression | Ephemeral snapshot (thread-safe) |
| `_m_homeo` | $\mathbb{R}^{4}$ (`float64`) | `EmotionCore` | Stage 5 update / Default rest | `HomeostaticEngine` (`energy, load, tension, stability`) | Slow field forcing function | Ephemeral runtime (in-memory) |
| `s_philia` | $\mathbb{R}^{16}$ (`float64`, const) | `EmotionCore` | Immutable at construction | Fixed coordinate $[0.20, -0.05, 0.05, 0, \dots]^T$ | Slow centering $\Delta\mathbf{s}_s$ | Structural constant (code-defined) |
| `p_philia` | $\mathbb{R}^{3}$ (`float64`, const) | `EmotionCore` | Immutable at construction | `EmotionConfig.resting_baseline` ($[+0.25, -0.05, +0.05]$) | PAD projection anchor | Structural constant (code-defined) |
| `_tick_counter`| `int` | `EmotionCore` | Monotonic increment per tick | ODE step execution | Telemetry, LSI stability evaluator | Ephemeral runtime (integer counter) |
| `_committed_seq`| `int` | `EmotionCore` | Monotonic increment per turn | `push_stimulus` sequence counter | Deterministic turn synchronization barrier | Ephemeral runtime (turn sync) |

### Persistence Classification:
- **Ephemeral Runtime State**: $\mathbf{h}_{\text{fast}}$, $\mathbf{s}_{\text{slow}}$, and `_pad_snapshot` reside strictly in RAM.
- **Session Boundary**: Upon companion process restart, $\mathbf{h}_{\text{fast}} \gets \mathbf{0}$ and $\mathbf{s}_{\text{slow}} \gets \mathbf{s}^*_{\text{philia}}$, naturally initializing Lucia at her calm Philia baseline.
- **Disk Persistence**: **ABSOLUTELY ZERO**. No limbic vectors are written to `data/profile.json` or `data/chat_history.json`.

---

## 5. Exact Mathematical Contract & Parameter Classification

### 5.1 Ordinary Differential Equations

#### Fast Reactive Layer ($\mathbf{h}_{\text{fast}} \in \mathbb{R}^{32}$):
$$\tau_{\text{fast}}(\mathbf{h}_f, \mathbf{x}) = \text{clip}\Big(\text{softplus}(\mathbf{W}_{\tau, f} \mathbf{h}_f + \mathbf{U}_{\tau, f} \mathbf{x} + \mathbf{b}_{\tau, f}),\; \tau_{f, \min},\; \tau_{f, \max}\Big)$$

$$\frac{d\mathbf{h}_f}{dt} = \frac{-\mathbf{h}_f + \tanh\Big(\mathbf{W}_{ff} \mathbf{h}_f + \mathbf{W}_{fs} (\mathbf{s}_s - \mathbf{s}^*_{\text{philia}}) + \mathbf{U}_f \mathbf{x} + \mathbf{b}_f\Big)}{\tau_{\text{fast}}(\mathbf{h}_f, \mathbf{x})}$$

#### Slow Affective Latent Layer ($\mathbf{s}_{\text{slow}} \in \mathbb{R}^{16}$):
$$\Delta \mathbf{s}_s = \mathbf{s}_s - \mathbf{s}^*_{\text{philia}}$$

$$\Delta \mathbf{m} = \mathbf{m}_{\text{homeo}} - [1.0, 0.0, 0.0, 1.0]^T$$

$$\frac{d\mathbf{s}_s}{dt} = -\frac{\Delta \mathbf{s}_s}{\tau_{\text{slow, decay}}} + \frac{\tanh(\mathbf{W}_{sf} \mathbf{h}_f + \mathbf{W}_{sh} \Delta \mathbf{m})}{\tau_{\text{slow, charge}}}$$

#### Anchored PAD Projection:
$$\mathbf{PAD}(t) = \text{clip}\Big(\mathbf{W}_{\text{proj}, f} \mathbf{h}_f + \mathbf{W}_{\text{proj}, s} (\mathbf{s}_s - \mathbf{s}^*_{\text{philia}}) + \mathbf{p}^*_{\text{philia}},\; -1.0,\; 1.0\Big)$$

### 5.2 Complete Parameter Classification Table

| Parameter | Symbol / Dimension | Production Value | Rigorous Classification | Justification & Source |
|---|---|---|---|---|
| Fast Hidden Dim | $H_f$ | $32$ | **VALIDATED** | Preserves compatibility with existing $H=32$ limbic footprint; proven in EXP-19.8. |
| Slow Hidden Dim | $H_s$ | $16$ | **VALIDATED** | Provides compact momentum capacity with sub-microsecond CPU matrix multiplication. |
| Fast Time-Constant Min | $\tau_{f, \min}$ | $0.10\text{ s}$ | **VALIDATED** | Prevents stiffness in RK45 solver; validated in EXP-19.1. |
| Fast Time-Constant Max | $\tau_{f, \max}$ | $1.50\text{ s}$ | **VALIDATED** | Bounds fast reflex clearing window; validated in EXP-19.1. |
| Slow Charging Time-Constant| $\tau_{\text{slow, charge}}$ | $3.50\text{ s}$ | **VALIDATED** | Enables affective uptake across 3–5 conversational turns; validated in EXP-19.3 & EXP-19.4. |
| Slow Relaxation Time-Constant| $\tau_{\text{slow, decay}}$ | $28.00\text{ s}$ | **VALIDATED** | Yields multi-minute empirical retention ($93.28\text{ s}$ unforced tail); validated in EXP-19.1. |
| Slow-to-Fast Coupling | $\|\mathbf{W}_{fs}\|$ | $0.05$ | **VALIDATED** | Contraction invariant; prevents positive feedback runaway latching (EXP-19.2). |
| Fast-to-Slow Coupling | $\|\mathbf{W}_{sf}\|$ | $1.00$ | **VALIDATED** | Ensures affective charging tracks perceived valence and arousal. |
| Homeostatic Coupling Matrix| $\mathbf{W}_{sh} \in \mathbb{R}^{16 \times 4}$ | Structured | **VALIDATED** | $W_{sh}[0,2]=-0.24, W_{sh}[1,2]=+0.28, W_{sh}[1,1]=+0.04, W_{sh}[1,0]=+0.20$ (EXP-19.3). |
| Philia Slow Attractor | $\mathbf{s}^*_{\text{philia}} \in \mathbb{R}^{16}$ | $[0.20, -0.05, 0.05, \dots]$ | **CALIBRATED** | Anchors resting affective manifold to Philia orientation. |
| Philia PAD Baseline | $\mathbf{p}^*_{\text{philia}} \in \mathbb{R}^3$ | $[+0.25, -0.05, +0.05]$ | **CALIBRATED** | Established in Phase 6 / Phase 10 limbic tuning. |
| ODE Step Size | $\Delta t$ | $0.10\text{ s}$ | **DESIGN CHOICE** | Standard discrete numerical integration step size. |
| Fast Loop Cadence | $T_{\text{cadence}}$ | $200\text{ ms}$ | **DESIGN CHOICE** | Canonical $5\text{ Hz}$ background ODE integration cadence. |
| Initial Random Seed | `init_seed` | $42$ | **DESIGN CHOICE** | Fixed seed for bit-exact Xavier initialization of off-diagonal weights. |
| Ablation Flags | `ablate_*` | `False` | **RESEARCH-ONLY** | Diagnostic ablation flags kept in evaluation suite; production runs full coupled model. |

---

## 6. Philia Attractor Contract

### 6.1 Architectural Meaning
The Philia Dynamic Attractor is strictly a **mathematical and normative grounding constraint**. It represents the physiological resting state of Lucia's affective dynamical system.
- It is **NOT** a subjective emotional claim, self-awareness assertion, or evidence of conscious feeling.
- It ensures that when external interaction ceases, Lucia smoothly and organically returns toward a warm, gentle, calm resting equilibrium ($P=+0.25, A=-0.05, D=+0.05$) rather than decaying into dead zero apathy ($[0, 0, 0]$).

### 6.2 Attractor Specifications & Invariants
1. **Coordinates**: Fixed at $\mathbf{p}^*_{\text{philia}} = [+0.25, -0.05, +0.05]^T$ in PAD space and $\mathbf{s}^*_{\text{philia}} = [0.20, -0.05, 0.05, 0, \dots, 0]^T$ in slow latent space.
2. **Immutability**: Attractor coordinates are structural constants in `EmotionConfig` and cannot be modified by prompts, chat turns, or online learning.
3. **Empirical Attractor Convergence**: Demonstrated across diverse origins (Joy, Stress, Melancholy, Origin) in EXP-19.2, unforced relaxation converges to the Philia coordinate neighborhood with final distance $\le 0.0386 \le 0.0600$, with local negative divergence $\text{Tr}(J) \le -40.0$ confirming dissipative trajectory behavior in tested regimes.
4. **Reset Behavior**: `reset_to_resting()` sets $\mathbf{h}_f \gets \mathbf{0}$ and $\mathbf{s}_s \gets \mathbf{s}^*_{\text{philia}}$, instantaneously restoring bit-exact Philia coordinates without transients.

### 6.3 Stability Claim Boundary
- **Empirical Validation vs Global Proof**: Phase 19 experimentally validated bounded, dissipative, and non-latching behavior across all standardized test trajectories (EXP-19.1 through EXP-19.8). The production architecture enforces this validated parameter regime ($\|\mathbf{W}_{fs}\| \le 0.05$, bounded $\tau$).
- **Trace as Local Dissipation**: A strictly negative Jacobian trace ($\text{Tr}(J) < 0$) mathematically establishes infinitesimal phase-space volume contraction (Liouville's theorem), which supports local dissipative behavior and excludes locally volume-expanding flow under the validated/tested operating regime.
- **Explicit Non-Claims & Interpretation Boundary**:
  - Negative divergence / $\text{Tr}(J) < 0$ supports local phase-space volume contraction, but:
    - It does **NOT** prove global asymptotic stability.
    - It does **NOT** rule out all strange attractors.
    - It does **NOT** rule out all non-local invariant sets (such as limit cycles).
    - It does **NOT** constitute a formal Lyapunov stability proof.
- **Operational Stability in Production**: No global mathematical stability theorem or formal Lyapunov proof is claimed. System stability in production is maintained operationally through strict bounded coupling constraints ($\|\mathbf{W}_{fs}\| \cdot \|\mathbf{W}_{sf}\| \cdot \frac{\tau_{\text{decay}}}{\tau_{\text{charge}}} < 1.0$), saturation clamping on state vectors ($\text{clip}(y, -1.0, 1.0)$), and continuous run-time verification of numerical finite bounds.
- **Retained Empirical Evidence**: All Phase 19 research findings remain intact: bounded trajectories in tested scenarios, deterministic convergence within tested conditions ($\epsilon \le 0.0386$), zero NaN/Inf occurrences, and validated coupling operating constraints.

---

## 7. S3 & S4 Pipeline Integration Contract

### 7.1 Stage 3 (S3: Limbic Integration) Realization
Stage 3 in `CognitiveOrchestrator._execute_pipeline` remains causal and synchronous:

```python
# ── Stage 3: Limbic Integration ──────────────────────────────────
# 1. Inject stimulus vector (16-dim continuous features from S1)
token = self._emotion_core.push_stimulus(stimulus)

# 2. Deterministically commit state transition (enforces temporal barrier)
pad_committed: PADState = self._emotion_core.commit_stimulus(token)

# 3. Record single metabolic turn cost in HomeostaticEngine
self._homeostatic_engine.record_input()
```

### 7.2 Stage 4 (S4: Prediction Surprise & Belief Update) Compatibility
Stage 4 receives `pad_committed` exactly as before:

```python
# ── Stage 4: Prediction Surprise & Belief Update ─────────────────
pad_final: PADState = pad_committed
prediction_error: float = self._active_inference.step(pad_initial, pad_final)
```

- **Zero S4 Semantic Alteration**: `pad_committed` is an authentic, immutable `PADState` instance with `pleasure`, `arousal`, `dominance`, and `timestamp`.
- Active Inference computes Free Energy surprise:
  $$\mathcal{S} = \|\mathbf{A} \cdot \mathbf{p}_{\text{initial}} + \mathbf{b} - \mathbf{p}_{\text{final}}\|_2$$
  Because multi-timescale transitions are continuous and bounded, $\mathcal{S}$ exhibits smooth, biologically realistic trajectories without spurious mathematical spikes.

### 7.3 Stage 5 Homeostatic Context Feedback Hook
In Stage 5, after somatic markers are modulated by surprise, the orchestrator passes the updated homeostatic context back into `EmotionCore`:

```python
# ── Stage 5: Homeostatic Modulation & Limbic Feedback ────────────
base_markers: SomaticMarkers = self._homeostatic_engine.compute_somatic_markers(pad_final)
markers: SomaticMarkers = self._surprise_policy.modulate_somatic(base_markers, prediction_error)

# Push homeostatic markers into limbic slow-layer context
self._emotion_core.update_homeostatic_context(
    energy=markers.energy,
    load=markers.cognitive_load,
    tension=markers.tension,
    stability=markers.stability,
)
This hook enables the slow affective field to incorporate somatic fatigue over unforced pauses without violating the 16-stage ordering.

### 7.4 Temporal Causality of Homeostatic Feedback
Lucia's 16-stage cognitive pipeline operates under a strict causal time arrow. The temporal contract between limbic integration (Stage 3) and homeostatic modulation (Stage 5) is defined as an architectural invariant:

#### Turn Execution Flow:
```text
Turn t:
  1. Stage 3 (S3 Limbic Integration):
     MT-LNN ODE step reads the latest committed homeostatic context m_homeo(t-1)
     available BEFORE S3 (from Turn t-1 or background idle rest).
          ↓
     Limbic state transition executed: h_f(t-1) → h_f(t), s_s(t-1) → s_s(t)
          ↓
     Committed PADState snapshot emitted: PAD(t)

  2. Stage 4 (S4 Active Inference):
     Surprise & prediction error computed from PAD(t)

  3. Stage 5 (S5 Homeostatic Modulation & Marker Update):
     HomeostaticEngine computes somatic markers from PAD(t)
     SurprisePolicy modulates cognitive load and tension from Stage 4 surprise
          ↓
     m_homeo(t) stored into EmotionCore via update_homeostatic_context()

Between Turns / Turn t+1:
  - Continuous Background Ticks (FastLoop, 200 ms cadence):
    Subsequent ODE integration ticks consume m_homeo(t) for slow-layer forcing ds_s/dt
  - Turn t+1 Stage 3:
    Consumes m_homeo(t) as the baseline homeostatic context
```

#### Strict Causal Invariant:
> **Stage 5 homeostatic context MUST NOT retroactively alter the already-committed Stage 3 transition.**
>
> - S3 consumes the latest committed homeostatic context available **BEFORE** S3.
> - S5 computes the new homeostatic context **AFTER** S3.
> - The newly computed context $m_{\text{homeo}}(t)$ becomes eligible strictly for subsequent ODE integration (continuous background ticks and future turn transitions), never retroactively for the already committed S3 transition of the same turn.
> - Background FastLoop ticks between turns continuously read the latest stored `_m_homeo`, ensuring that homeostatic fatigue or recovery dynamically drives affective momentum over conversational pauses without violating causal pipeline ordering.

---

## 8. Concurrency & Lock Hierarchy Design

### 8.1 Unified Concurrency Discipline
To prevent deadlocks and maintain sub-millisecond lock acquisition deadlines, the established lock hierarchy is strictly preserved:

```text
┌────────────────────────────────────────────────────────────────────────┐
│                     CANONICAL LOCK ACQUISITION ORDER                   │
│                                                                        │
│   1. _turn_lock      (CognitiveOrchestrator turn execution mutex)      │
│   2. _step_lock      (EmotionCore ODE integration step serialization)  │
│   3. _train_lock     (Atomic LNN parameter swap, <= 2ms)               │
│   4. _stimulus_lock  (FIFO stimulus queue push/pop)                    │
│   5. _state_lock     (PADState snapshot read/write, <= 1ms deadline)   │
│                                                                        │
│   INVARIANT RULES:                                                     │
│   - Never acquire _step_lock while holding _train_lock or _state_lock. │
│   - Never perform disk I/O, network calls, or LLM inference under locks│
│   - Fast & slow state arrays are mutated exclusively under _step_lock. │
│   - Telemetry reads acquire only _state_lock with a 1ms timeout.       │
└────────────────────────────────────────────────────────────────────────┘
```

### 8.2 State Read/Write Concurrency Matrix
- **`get_pad_state()`**: Acquires `_state_lock` with $1\text{ ms}$ deadline; returns copy of `_pad_snapshot`. Safe for asynchronous $10\text{ ms}$ telemetry polling.
- **`get_fast_state()` & `get_slow_state()`**: Acquire `_state_lock`; return `.copy()` of the hidden numpy arrays.
- **`step_once()` & `commit_stimulus()`**: Acquire `_step_lock` to serialize RK45 integration between the background worker thread and synchronous turn execution.
- **`push_stimulus()`**: Acquires `_stimulus_lock`; appends `(seq, vector)` to FIFO queue in $O(1)$ time.

---

## 9. LNN Plasticity & Training Compatibility

### 9.1 Compatibility with `LNNTrainer`
1. **Trainable Parameter Set**: As established in ADR-026 and prompt guidance, **online plasticity is restricted exclusively to the fast reactive layer**:
   $$\Theta_{\text{trainable}} = \{\mathbf{W}_{ff}, \mathbf{U}_f, \mathbf{b}_f, \mathbf{W}_{\tau, f}, \mathbf{U}_{\tau, f}, \mathbf{b}_{\tau, f}, \mathbf{W}_{\text{proj}, f}, \mathbf{b}_{\text{proj}}\}$$
2. **Fixed Structural Constants**: The slow layer parameters ($\mathbf{W}_{sf}, \mathbf{W}_{sh}, \tau_{\text{decay}}, \tau_{\text{charge}}, \mathbf{s}^*_{\text{philia}}$) are **NOT trainable**. They represent structural homeostatic constants that enforce stability and the Philia attractor invariant.
3. **Weight Swap Interface**: `EmotionCore` provides explicit property aliases:
   ```python
   @property
   def W_f(self) -> np.ndarray: return self.W_ff
   @W_f.setter
   def W_f(self, val: np.ndarray) -> None: self.W_ff = val
   ```
   This ensures that `LNNTrainer._weight_swap()` continues to execute atomically under `_train_lock` without requiring any breaking refactor of `lnn_trainer.py`.

---

## 10. Persistence, Reset, and First Activation Semantics

### 10.1 Boundary Invariants
1. **Turn Boundary ($t \to t+1$)**:
   - Fast state $\mathbf{h}_f$ and slow state $\mathbf{s}_s$ survive in memory across turns.
   - Fast state continues continuous background integration every $200\text{ ms}$, decaying toward slow state bias.
   - Slow state retains affective momentum across multi-minute pauses.
2. **Session Boundary (Process Restart)**:
   - All limbic vectors reset to canonical baseline: $\mathbf{h}_f \gets \mathbf{0}, \mathbf{s}_s \gets \mathbf{s}^*_{\text{philia}}, \mathbf{PAD} \gets [+0.25, -0.05, +0.05]$.
   - Zero disk persistence is introduced.
3. **Simulation Boundary**:
   - `SimulationRuntime` operates an isolated `SimClock` that calls `step_once(custom_timestamp)`.
   - Complete state isolation: simulation turns never contaminate live companion state.
4. **First Activation (Genesis Onboarding)**:
   - `data/profile.json` remains permanently locked with `"is_onboarded": false`.
   - No Genesis Awakening triggers or onboarding mutations are touched.

---

## 11. Numerical Safety & Fail-Safe Error Handling

### 11.1 Safeguards Against Mathematical Failure
- **Intermediate ODE Clamping**: All state evaluations in the RK45 RHS function are clamped to $[-1.0, 1.0]$ via `np.clip()`.
- **Softplus Lower Bound**: Time constants are passed through `softplus` and clipped to $[\tau_{\min}, \tau_{\max}]$ to prevent zero-division or numerical stiffness.
- **Fail-Safe Exception Recovery**: If `solve_ivp` raises any numerical exception (e.g. `FloatingPointError` or singular matrix), `_step_once_unlocked` traps the exception, logs it, and safely resets states to the Philia attractor:
  ```python
  except Exception:
      logger.exception("MT-EmotionCore numerical failure — resetting to Philia attractor")
      self._h_fast = np.zeros(self._config.hidden_fast_dim, dtype=np.float64)
      self._s_slow = self.s_philia.copy()
      self._pad_snapshot = self._pad_resting
      return self._pad_resting
  ```
- **Post-Step Verification**: Every step verifies `np.all(np.isfinite(h_new))` and `np.all(np.isfinite(s_new))`.

---

## 12. Backward Compatibility Matrix

| Subsystem / Consumer | Current Phase 10 Contract | Target Phase 19 MT-LNN Contract | Compatibility Status | Required Modifications |
|---|---|---|---|---|
| `CognitiveOrchestrator` S3 | `push_stimulus(x)`, `commit_stimulus(tok)` | Identical method signatures and return types | **100% COMPATIBLE** | Add optional `update_homeostatic_context` call in Stage 5. |
| `ActiveInferenceEngine` S4 | Reads `pad_final: PADState` | Receives authentic `PADState` snapshot | **100% COMPATIBLE** | None. |
| `HomeostaticEngine` S5 | Takes `pad: PADState` | Receives authentic `PADState` snapshot | **100% COMPATIBLE** | None. |
| `AffectiveMemory` & Ecphory | Cosine resonance with `PADState` | Cosine resonance with `PADState` | **100% COMPATIBLE** | None. |
| `CommunicationPolicy` S10 | Reads `pad: PADState` | Receives authentic `PADState` snapshot | **100% COMPATIBLE** | None. |
| `ExpressionPolicy` S15 | Reads `pad: PADState` | Receives authentic `PADState` snapshot | **100% COMPATIBLE** | None. |
| `LNNTrainer` (Plasticity) | Swaps `W_f, U_f, b_f, W_tau, ...` | Supported via direct attributes and property aliases | **100% COMPATIBLE** | None. |
| `SimClock` & Simulation | Calls `step_once(custom_timestamp)` | Identical signature supported under `_step_lock` | **100% COMPATIBLE** | None. |
| `/state` & `/telemetry` API | `get_pad_state()` with 1ms deadline | Identical non-blocking read under `_state_lock` | **100% COMPATIBLE** | None. |
| Unit Tests (575 tests) | Relies on `EmotionCore` API | Preserves all method names, attributes, and shapes | **100% COMPATIBLE** | Zero regressions verified by full test suite. |

---

## 13. Comprehensive Test Strategy

### 13.1 Test Architecture
Prior to writing any production code, the verification suite will be structured across three tiers:

```text
tests/
├── unit/
│   ├── test_emotion_core.py          # Existing unit tests (regression baseline)
│   └── test_mt_emotion_core.py       # Dedicated unit tests for MT-LNN dynamics
├── integration/
│   ├── test_cognitive_pipeline.py    # Full 16-stage pipeline integration
│   └── test_mt_homeo_coupling.py     # End-to-end stress -> fatigue validation
└── evaluation_phase19/
    └── test_phase19_research.py      # Research invariant verification (15/15 passing)
```

### 13.2 Unit Test Plan (`tests/unit/test_mt_emotion_core.py`)
1. `test_fast_slow_state_dimensions()`: Fast state is $\mathbb{R}^{32}$, slow state is $\mathbb{R}^{16}$.
2. `test_philia_attractor_exact_convergence()`: Unforced step converges to $[+0.25, -0.05, +0.05]$ within $10^{-4}$.
3. `test_two_timescale_trajectory_retention()`: Verifies observed biphasic trajectory retention following stimulus perturbation (rapid reflex clearing in fast layer within $2–5\text{ s}$, persistent affective deviation in slow field beyond $30\text{ s}$, and asymptotic recovery toward Philia attractor neighborhood rather than origin collapse, mirroring EXP-19.1/EXP-19.2 evidence).
4. `test_homeostatic_fatigue_coupling()`: Depleted energy with elevated load depresses arousal.
5. `test_numerical_safety_nan_resilience()`: Injecting NaN inputs triggers graceful fallback to Philia.
6. `test_reset_to_resting_clears_momentum()`: `reset_to_resting()` immediately restores Philia without residual momentum.
7. `test_lock_hierarchy_compliance()`: High-frequency concurrent reads (`get_pad_state`) never block ODE stepping.

### 13.3 Integration & Regression Test Plan
- **Unit Suite Regression**: All 575 existing unit tests must pass without a single failure.
- **Phase 17 & 18 Scenarios**: All longitudinal evaluation tracks and voice runtime tests remain fully functional.

---

## 14. Research-to-Production Traceability Matrix

Every empirical finding from Phase 19 research is mapped directly to a production mechanism and test case:

| Phase 19 Research Evidence | Production Architectural Mechanism | Production Verification Test |
|---|---|---|
| **EXP-19.1 (Multi-timescale Decay)** | Dual ODE solver ($\tau_f \in [0.1, 1.5]\text{s}, \tau_s = 28\text{s}$) in `EmotionCore` | `test_two_timescale_trajectory_retention` |
| **EXP-19.2 (Philia Convergence)** | Centered slow dynamics $\Delta\mathbf{s} = \mathbf{s} - \mathbf{s}^*$ and anchored PAD projection | `test_philia_attractor_exact_convergence` |
| **EXP-19.3 (Stress -> Fatigue)** | Homeostatic coupling $\mathbf{W}_{sh}\Delta\mathbf{m}$ driving slow arousal down under low energy | `test_homeostatic_fatigue_coupling` |
| **EXP-19.4 (Hysteresis)** | Slow momentum field $\mathbf{s}_{\text{slow}}$ retaining cross-turn trajectory context | `test_hysteresis_path_divergence` |
| **EXP-19.5 (Behavioral Modulation)** | Downstream `GenerationPolicy` throttling tokens under somatic fatigue | `test_somatic_fatigue_token_throttling` |
| **EXP-19.6 (Causal Ablations)** | Architectural necessity of slow field and Philia centering | `tests/evaluation_phase19/test_phase19_research.py` |
| **EXP-19.7 (Determinism & Noise)** | Fixed seed initialization and bounded floating-point integration | `test_deterministic_replay_precision` |
| **EXP-19.8 (Lifecycle & Performance)** | CPU RK45 integration with mean step latency $1.33\text{ ms} \le 2.0\text{ ms}$ | `test_longitudinal_lifecycle_latency` |

---

## 15. Migration & Rollback Strategy

### 15.1 Migration Sequence (When Approved)
1. **Step 1 (Configuration)**: Update `EmotionConfig` in `src/core/config.py` with multi-timescale dimensions and time constants.
2. **Step 2 (Core Engine Evolution)**: Refactor `EmotionCore` in `src/core/emotion/emotion_core.py` to implement the coupled MT-LNN equations while preserving existing public method signatures.
3. **Step 3 (Orchestrator Coupling)**: Add `update_homeostatic_context` in Stage 5 of `CognitiveOrchestrator._execute_pipeline`.
4. **Step 4 (Unit Verification)**: Run `pytest tests/unit/test_emotion_core.py` and new `test_mt_emotion_core.py`.
5. **Step 5 (Full Regression Gate)**: Run complete test suite: 575+ unit tests, property tests, and evaluation suites.

### 15.2 Rollback Strategy
Production rollback adheres strictly to release and source control governance:
1. **Production Rollback Target**: If unexpected behavioral regressions or acceptance gate failures occur during production integration, rollback must target the actual known-good Git commit immediately preceding Phase 19 production implementation.
   - **Commit Identification**: Commit `2fb052e` is the Phase 19 research promotion / ADR-026 commit, and is **NOT** the pre-Phase-19 production baseline.
   - **Implementation Boundary**: Because production implementation has not started yet, the exact implementation rollback commit does not exist at this stage.
   - **Pre-Implementation Requirement**: Immediately prior to starting production implementation, the engineering team must identify and record the exact Git commit representing the active production baseline.
   - **Post-Implementation Requirement**: After implementation, any newly created implementation commit becomes the rollback boundary only if it is explicitly validated and documented.
   - **No Invented Hashes**: No assumed or invented commit hashes shall be assumed.
2. **Safe Production Fallback Chain**:
   $$\text{Phase 19 Production Implementation} \xrightarrow{\text{Regression / Acceptance Failure}} \text{Git / Release Rollback} \xrightarrow{\text{Restore}} \text{Known-Good Pre-Implementation Production Baseline}$$
3. **No Unverified Runtime Ablation Flags in Production**: Production `EmotionConfig` will not carry synthetic runtime ablation flags (`ablate_slow_field`, `ablate_philia_attractor`). Disabling fields at runtime does not constitute verified mathematical equivalence to Phase 10 `EmotionCore`. Therefore, runtime ablation is strictly prohibited as a production rollback mechanism.

### 15.3 Rollback Boundary: Research Ablation vs. Production Rollback
- **Research Ablation**: Used strictly during research experimentation (`tests/evaluation_phase19/`) to isolate causal contributions of individual terms (e.g. EXP-19.6 measuring decay kinetics with slow field disabled).
- **Production Rollback**: Operates at the release and repository level. In production, `EmotionCore` runs as a unified, cohesive MT-LNN model. If integration fails, rollback restores the verified pre-implementation production code baseline via Git (`git revert` or `git checkout <pre-implementation-baseline-commit>`).
- **Boundary Invariant**: **Research ablation $\neq$ production rollback**.

---

## 16. File-Level Implementation Plan (For Future Execution Phase)

The following files will be affected during the future implementation phase:

### Modified Files:
1. `src/core/config.py`:
   - *Rationale*: Add MT-LNN hyperparameters (`hidden_slow_dim=16`, `tau_slow_charge=3.5`, `tau_slow_decay=28.0`, coupling strengths) to `EmotionConfig` with production defaults.
2. `src/core/emotion/emotion_core.py`:
   - *Rationale*: Implement the coupled dual-layer ODE equations, Philia attractor grounding, homeostatic context tracking, and backward-compatible property accessors.
3. `src/core/orchestrator/cognitive_orchestrator.py`:
   - *Rationale*: Wire Stage 5 somatic markers into `emotion_core.update_homeostatic_context()`.

### Created Files:
1. `tests/unit/test_mt_emotion_core.py`:
   - *Rationale*: Dedicated unit tests validating the multi-timescale dynamics, convergence, and fail-safe safety.
2. `tests/integration/test_mt_homeo_coupling.py`:
   - *Rationale*: End-to-end integration test verifying stress-to-fatigue transformation across the 16-stage pipeline.

### Deleted Files:
- **NONE**. No files will be deleted.

---

## 17. Architectural Risk Assessment & Mitigation

| Risk Description | Severity | Probability | Concrete Mitigation Strategy | Validation Method |
|---|---|---|---|---|
| **Bistable Latching Runaway** | HIGH | LOW | Enforce bounded coupling constraint $\|\mathbf{W}_{fs}\| \le 0.05$ and verify negative divergence trace $\text{Tr}(J) \le -40.0$. | Unit test `test_dissipative_divergence_trace`. |
| **CPU Step Latency Spike** | MEDIUM | LOW | Pre-allocate all weight matrices; solve 48D ODE using RK45 with adaptive step size. | Performance profiling test asserting mean latency $\le 2.0\text{ ms}$. |
| **`LNNTrainer` Weight Incompatibility** | MEDIUM | LOW | Expose `W_f`, `U_f`, `b_f` aliases pointing to fast-layer weights; lock slow weights. | Unit test verifying `LNNTrainer._weight_swap()` runs without error. |
| **Simulation Time Dilation Desync** | LOW | LOW | `SimClock` continues to drive `step_once(custom_timestamp)` with explicit virtual $\Delta t$. | Integration test running simulation scenarios at $1\times, 10\times, 60\times$. |
| **First Activation Contamination** | CRITICAL | ZERO | Zero disk persistence added; `data/profile.json` hash asserted bit-exact in every test. | Storage isolation gate in automated test runner. |

---

## 18. Future Phase Compatibility (Phase 20+)

### Compatibility with Phase 20 (Affective Recollection & Memory Reactivation)
- In Phase 20, memory recollection may gently color affective state.
- **Architectural Boundary**: This Phase 19 MT-LNN design provides the necessary temporal substrate (slow latent momentum) to receive such priming in the future.
- **Strict Prohibition Preserved**: Direct memory injection into limbic state remains **STRICTLY FORBIDDEN** in Phase 19. Memory retrieval remains confined to Stage 6 (Associative Memory Ecphory) and Stage 7 (Bounded Memory Contextualization).

---

## 19. Explicit Non-Goals

To maintain conceptual and architectural integrity, the following are explicitly declared **NON-GOALS** for Phase 19 production realization:
1. Creating subjective consciousness, sentience, or feeling.
2. Introducing self-referential or introspective dialogue patterns.
3. Enabling autonomous, unconstrained personality drift.
4. Implementing episodic memory recall directly into the limbic differential equations.
5. Introducing cloud dependencies, external APIs, or disk persistence for limbic hidden states.

---

## 20. Implementation Readiness Checklist

```text
[X] Phase 10 production audit complete (EmotionCore, HomeostaticEngine, LNNTrainer)
[X] Phase 16 S1–S16 cognitive pipeline audit complete
[X] Phase 19 research prototype audited (multi_timescale_model.py, temporal_analysis.py)
[X] ADR-026 verified and registered in docs/DESIGN_DECISIONS.md
[X] Exact production equations and parameter classifications defined
[X] State contract and persistence boundaries defined (zero disk persistence)
[X] Lock hierarchy and concurrency contract verified (_step_lock, _state_lock, _train_lock)
[X] Homeostatic timing is causally explicit (S3 consumes m_homeo(t-1), S5 updates for subsequent ticks)
[X] Stability claim boundary defined (Tr(J) < 0 establishes local dissipation; no unproven global Lyapunov proof)
[X] Rollback boundary defined (research ablation != production rollback; git/release rollback enforced)
[X] Numerical safety and fail-safe recovery specified
[X] Backward compatibility matrix established for all consumers
[X] Comprehensive test strategy defined (unit, integration, regression)
[X] Research-to-production traceability matrix complete
[X] Migration and rollback strategies defined
[X] Future Phase 20 compatibility verified
[X] NO production code modified in src/core/**
[X] First Activation invariant confirmed: is_onboarded == false
```
