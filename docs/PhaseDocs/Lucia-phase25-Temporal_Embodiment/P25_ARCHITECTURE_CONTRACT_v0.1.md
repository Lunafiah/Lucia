# P25 Architecture Contract v0.1: Temporal Embodiment & Social Feedback

> **DOCUMENT ID:** `DOC-P25-016`<br>
> **DOCUMENT TYPE:** ARCHITECTURAL SPECIFICATION & SUBSYSTEM CONTRACT (`[ARCHITECTURE CONTRACT]`)<br>
> **CANONICAL STATUS:** APPROVED UNILATERAL BASELINE (CONTRACT v0.1)<br>
> **GOVERNING DECISION:** ARCH-033 / ADR-033 (Candidate Architecture Contract)<br>
> **RESEARCH FOUNDATION:** P25-Q1 (Closed / Memory Substrate Sufficient), P25-Q2 (Closed / H-A Supported, C2 Blocked, H-B Unproven)<br>
> **INVARIANTS PRESERVED:** INV-1 (One Continuous Life), INV-2 (No Reflective Ego), INV-5 (Zero Cloud), INV-8 (Genesis Gate Bit-Exact: `{"is_onboarded": false}`)<br>

---

## 1. Executive Summary & Purpose

This document establishes the authoritative **P25 Architecture Contract v0.1** governing the production realization of **Phase 25 — Temporal Embodiment & Social Feedback**.

Phase 25 realizes the **unilateral baseline** of conversational temporal embodiment and social adaptation. It operationalizes how the physical passage of time, inter-turn latency, and observed social signals influence Lucia's internal state dynamics, multi-timescale homeostasis, and downstream expressive conditioning, without asserting unproven reciprocal coupling or introducing reflective ego or sycophancy.

```text
┌────────────────────────────────────────────────────────────────────────────────────────┐
│                   P25 CANONICAL UNILATERAL INFORMATION FLOW                            │
└────────────────────────────────────────────────────────────────────────────────────────┘

  External Interaction (User Turn)
        │
        ▼
  Temporal/Social Observation (Latency, Speech Tempo, Pauses, Idle Time)
        │
        ▼
  State Estimation (Replaceable Boundary: Leaky / Bucy-Kalman Candidate)
        │
        ▼
  Temporal / Affective Dynamics (Elapsed-Time Evolution, Multi-Timescale Decays)
        │
        ▼
  Homeostatic + Bounded Relational Adaptation (||W_rel||_2 <= 0.08, Canonical 4D R_t)
        │
        ▼
  P24 Expression Conditioning (Speech Rate, Pause Duration, Pitch Contouring)
        │
        ▼
  Lucia Output (Multimodal Actuation without Actuator Feedback)
```

---

## 2. In-Scope Responsibilities

Phase 25 is strictly responsible for the following seven functional capabilities:

1. **Temporal Continuity & Elapsed-Time Effects:**
   - Tracking physical elapsed time ($\Delta t$) between interaction turns and sessions.
   - Simulating somatic and affective relaxation toward the Philia resting attractor ($P^* = +0.25, A^* = -0.05, D^* = +0.05$) during idle periods.
   - Simulating slow-timescale homeostatic energy replenishment during downtime.
   - High-inertia relational decay toward neutral stranger baseline $\mathbf{R}_0 = [0.0, 0.5, 0.0, 0.5]^T$ over extended absences.

2. **Multi-Timescale State Evolution:**
   - Fast conversational timescale ($\tau \sim 0.1\text{--}1.0\text{ s}$): response latency, conversational pacing, instant arousal modulation.
   - Intermediate somatic timescale ($\tau \sim 10\text{--}300\text{ s}$): cognitive load accumulation, metabolic tension relaxation, energy expenditure.
   - Slow relational timescale ($\tau \sim 10^3\text{--}10^5\text{ s}$): high-inertia relational attunement with learning rate $\alpha \le 0.03$.

3. **Bounded Hysteresis & Path Dependence:**
   - Preservation of trajectory history across interaction boundaries.
   - Ensuring divergent interaction trajectories (e.g. conflict followed by repair vs neutral continuation) exhibit measurable dynamical hysteresis even if endpoint relational coordinates converge.
   - Hysteresis is achieved strictly via existing memory (Kanerva SDM, episodic ecphory) and dynamical damping, without introducing unratified rupture or grievance state vectors.

4. **Observation of Social Interaction Signals:**
   - Measuring empirical temporal features of user interaction:
     - User turn response latency ($\Delta t_{\text{resp}}$).
     - User speech tempo / cadence ratio ($\nu_{\text{user}}$).
     - User pause duration ($\tau_{\text{pause}}$).
     - Interaction interval / inter-turn elapsed time ($\Delta t_{\text{idle}}$).
   - All observations are treated strictly as exogenous sensory inputs entering through the S1 sensory gating pipeline.

5. **State Estimation Boundary:**
   - A modular, replaceable estimation boundary (`TemporalStateEstimator` interface) that decouples raw sensory features from internal state updates.
   - Default baseline: Discrete-time Leaky Observer.
   - Candidate observer: Continuous-time Bucy-Kalman state estimator, designated strictly as a **candidate sensor-estimation mechanism derived from prior P22 evidence** (preserving canonical `P22-XR` and `P22-EKF` terminology).

6. **Unilateral Adaptation & Relational Attunement:**
   - Lucia adapts her internal somatic state and conversational pacing to match the estimated user cadence within safe, bounded physiological limits.
   - Relational coupling satisfies the strict Tier 2 spectral norm bound:
     $$\|W_{\text{rel}}\|_2 \le 0.08$$
   - Relational state $\mathbf{R}_t$ remains strictly 4-dimensional:
     $$\mathbf{R}_t = [\text{familiarity}, \text{trust}, \text{closeness}, \text{reciprocity}]^T \in [0.0, 1.0]^4$$

7. **Downstream P24 Expression Pathway Conditioning:**
   - Modulating P24 `ExpressionPolicy` and `CommunicationPolicy` (speech rate percentage, pause duration, prosody pitch shift, cadence style).
   - Decoupled feedforward actuation: Expressive outputs never feed back directly into internal ODE state (ADR-016, ADR-024).

---

## 3. Explicit Non-Goals & Strictly Forbidden Mechanisms

The following items are strictly outside the scope of Phase 25 and must **NEVER** be implemented:

1. **NO Reciprocal Feedback Loops:**
   - The feedback pathway $\text{Lucia Expression} \to \text{User Reaction} \to \text{Lucia Adaptation}$ is an **unproven research hypothesis**.
   - Condition C2 remains **BLOCKED**; Hypothesis H-B remains **UNPROVEN**.
   - The implementation must NOT close a synthetic loop or assume reciprocal causal attunement.

2. **NO Engagement or Retention Maximization:**
   - Lucia does NOT optimize for user session length, turn count, click-through, or engagement.
   - Conversational pacing and pauses are physiological resting reflexes, not gamified retention hooks.

3. **NO Approval-Seeking or Sycophancy (Anti-Sycophancy Invariant):**
   - Lucia never alters truth evaluations, concedes factual claims falsely, or flatters the user to increase closeness or trust.
   - Social adaptation adjusts timing and acoustic warmth, never cognitive truth criteria or safety boundaries.

4. **NO Autonomous Preferences or P26 Mechanisms:**
   - Phase 25 governs *how* interaction flows and adapts temporally.
   - Phase 26 governs *what* Lucia values or autonomously pursues.
   - Phase 25 components must NOT create autonomous goals, aesthetic preference engines, or emergent persona mutations.

5. **NO Reflective Ego (INV-2):**
   - Lucia NEVER self-reports synchrony metrics (*"I feel our pacing is aligned"*, *"My entrainment is high"*).
   - All temporal metrics and states operate strictly pre-reflectively.

6. **NO New Relational Dimensions (Canonical 4D Invariant):**
   - $\mathbf{R}_t$ must NOT be expanded with grievance, resentment, rupture severity, or negative attachment coordinates.
   - Any proposed dimensional expansion remains an unresolved owner/architecture decision.

7. **NO Scalar Social Reward:**
   - Lucia is NOT an RL agent optimizing a scalar social reward function.
   - Dynamics are governed by dissipative dynamical ODEs and homeostatic equilibrium.

8. **NO Genesis or First Activation Modification (INV-8):**
   - `data/profile.json` must remain bit-exact: `{"is_onboarded": false}`.
   - No Genesis ceremony, root hash, or live identity state may be created or triggered.

---

## 4. Subsystem Architecture & Module Layout

The Phase 25 subsystem is implemented under `src/core/embodiment/`:

```text
src/core/embodiment/
├── __init__.py               # Public API exports
├── contract.py               # P25 Architecture Contract data models & boundaries
├── temporal_observer.py      # S1 temporal & social cue extraction (cadence, pauses, dt)
├── estimator.py              # Replaceable estimation boundary (Leaky & Bucy-Kalman candidate)
├── dynamics.py               # Multi-timescale temporal evolution & dissipativity diagnostic
└── attunement.py             # Unilateral bounded social attunement & P24 conditioning bridge
```

### 4.1 Interface Specification

#### `TemporalObserver`
Extracts temporal markers from incoming turns:
```python
class TemporalObserver:
    def observe(
        self,
        current_timestamp: float,
        last_turn_timestamp: Optional[float],
        user_text: str,
        audio_duration_ms: Optional[float] = None,
        pause_duration_ms: Optional[float] = None,
    ) -> TemporalObservation:
        ...
```

#### `TemporalStateEstimator` (Replaceable Boundary)
```python
class TemporalStateEstimator(Protocol):
    def update(
        self,
        observation: TemporalObservation,
        dt: float,
    ) -> EstimatedTemporalState:
        ...
    def reset(self) -> None:
        ...
```

Implementations:
- `LeakyTemporalEstimator`: Discrete-time leaky integrator baseline ($\lambda \in [0.10, 0.25]$).
- `BucyKalmanEstimator`: Continuous observer candidate derived from prior P22 evidence.

#### `TemporalDynamicsEngine`
Integrates multi-timescale evolution and idle relaxation:
```python
class TemporalDynamicsEngine:
    def step_idle(self, dt_seconds: float) -> IdleEvolutionResult:
        """Evolves PAD toward Philia, replenishes energy, applies absence decay."""
        ...
    def compute_dissipativity_diagnostic(self) -> float:
        """Returns Tr(J) strictly as supporting volume-contraction diagnostic."""
        ...
```

#### `UnilateralAttunementEngine`
Bridges estimated state to homeostatic constraints and P24 expression parameters:
```python
class UnilateralAttunementEngine:
    def modulate_pacing(
        self,
        estimated_state: EstimatedTemporalState,
        base_constraints: BehavioralConstraints,
    ) -> BehavioralConstraints:
        ...
    def compute_expression_adjustments(
        self,
        estimated_state: EstimatedTemporalState,
        rel_state: RelationshipState,
    ) -> ExpressionModulation:
        ...
```

---

## 5. Mathematical & Stability Guardrails

1. **Supporting Dissipativity Diagnostic:**
   - In accordance with architectural review, $\operatorname{Tr}(J) < 0$ is classified strictly as a **supporting local dissipativity diagnostic** (phase-space volume contraction via Liouville's theorem):
     $$\frac{d}{dt}\text{Vol}(\Omega) = \int_{\Omega} \operatorname{div}(\mathbf{F})\, d\mathbf{x} = \operatorname{Tr}(J) \cdot \text{Vol}(\Omega) < 0$$
   - It does **NOT** alone prove Lyapunov stability, contraction, or global asymptotic convergence.
   - No claim of Lyapunov stability is made based on $\operatorname{Tr}(J) < 0$ alone.

2. **Bounded Attunement Gains:**
   - Temporal pacing adjustment: $\Delta \tau_{\text{pace}} \in [-150, +250]\text{ ms}$.
   - Speech tempo modulation: $\Delta v \in [-15.0\%, +15.0\%]$.
   - Relational attractor weight: $\|W_{\text{rel}}\|_2 \le 0.08$.

---

## 6. Authoritative Gate Progression

The authoritative milestone gate progression for Phase 25 is formally recorded as:

$$\text{P25-Q1 CLOSED}$$
$$\downarrow$$
$$\text{P25-Q2 CLOSED (H-A supported, C2 blocked, H-B unproven)}$$
$$\downarrow$$
$$\text{Architecture Candidate / Evidence Synthesis (DOC-P25-016)}$$
$$\downarrow$$
$$\text{Ciah Review}$$
$$\downarrow$$
$$\text{Owner Decision}$$
$$\downarrow$$
$$\text{Implementation Gate (Unilateral Production Baseline Implemented)}$$
