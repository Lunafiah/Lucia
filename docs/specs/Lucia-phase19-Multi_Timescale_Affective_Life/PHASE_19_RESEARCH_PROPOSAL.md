# Phase 19 Research Proposal — Multi-Timescale Affective Life & Temporal Continuity

> **Document Type**: Authoritative Research Proposal & Experimental Foundation  
> **Phase**: Phase 19 — Foundation-First Research Cycle  
> **Target Subsystem**: Limbic Dynamics, Homeostatic Regulation & Multi-Timescale Continuity  
> **Status**: SUBMITTED FOR REVIEW & APPROVAL  
> **Directory**: `docs/specs/Lucia-phase19-Multi_Timescale_Affective_Life/PHASE_19_RESEARCH_PROPOSAL.md`  
> **Date**: September 2026  

---

## 1. Current Research Landscape

Lucia is a local, desktop-first, pre-reflective AI companion operating with zero cloud dependencies. Across Phases 1 through 18, the system evolved from isolated foundational algorithms into a fully integrated, verified 16-stage cognitive production architecture (`src/core/orchestrator/cognitive_orchestrator.py`), supported by 575 passing automated unit tests, 39 integration tests, 11 Electron desktop tests, and formal human longitudinal validation (Phase 18).

The current production system orchestrates:
- **Layer 1 (Sensory Gating)**: Lexical valence ($[-1, 1]$), arousal, and semantic density encoding emitting a 16-dimensional continuous stimulus vector $\mathbf{x}(t) \in \mathbb{R}^{16}$.
- **Layer 2 (Limbic Fast Loop)**: Liquid Time-Constant (LTC) Liquid Neural Network (LNN) ordinary differential equation (ODE) solver running on a 200 ms background thread:
  $$\frac{d\mathbf{h}}{dt} = \frac{-\mathbf{h} + \tanh(\mathbf{W}_f \mathbf{h} + \mathbf{U}_f \mathbf{x} + \mathbf{b}_f)}{\text{softplus}(\mathbf{W}_\tau \mathbf{h} + \mathbf{U}_\tau \mathbf{x} + \mathbf{b}_\tau)}$$
  projecting hidden state $\mathbf{h} \in \mathbb{R}^{32}$ onto the 3D PAD manifold ($P, A, D \in [-1, 1]^3$).
- **Layer 3 (Homeostatic Engine)**: Somatic marker tracking ($\text{energy}, \text{cognitive\_load}, \text{tension}, \text{stability}$), imposing metabolic constraints on language generation (token budgets, sampling temperature).
- **Layer 4 (Active Inference)**: Short-horizon $3 \times 3$ generative transition model computing Free Energy prediction surprise $\mathcal{S} = \|\mathbf{A}\mathbf{p}_{pre} + \mathbf{b} - \mathbf{p}_{post}\|_2$, causally triggering deliberative reasoning depth ($k=2$) when $\mathcal{S} > 0.60$.
- **Layer 5 (Affective Memory & Knowledge)**: Kanerva Sparse Distributed Memory (SDM) with salience-resistant decay ($\lambda_{eff}$) and Synergistic Ecphory, alongside a thread-safe propositional Knowledge Graph (`KnowledgeStore`) with bounded forward derivation ($d_{max} \le 3$).
- **Layer 6 (Embodied Presence & Communication)**: Bounded multidimensional communication strategy selection ($C_t \in \mathbb{R}^{10}$), somatic pacing delays ($0 \le \tau \le 1000\text{ ms}$), local GGUF Small Language Model inference on NVIDIA CUDA GPU, BoundaryLayer regex protection, canonical 15-dimensional expression state ($E_t \in \mathbb{R}^{15}$), and authentic on-device neural RVC v2 Japanese speech synthesis.

However, despite these achievements, a critical structural limitation persists at the very base of the cognitive stack: **the temporal disconnect between fast-loop physiology and long-term continuity.**

---

## 2. Evidence from Phases 10–18

A comprehensive audit of historical milestones reveals the empirical boundaries established by previous research:

1. **Phase 10 (Affective Dynamics)**:
   - *Confirmed*: The LNN ODE exhibits short-term state persistence ($\mathbf{h}(t+1)$ depends on $\mathbf{h}(t)$) and historical hysteresis under rapid perturbations (`tests/unit/test_affective_dynamics.py`).
   - *Audit Discovery*: The mathematical fixed point of the unforced ODE ($\mathbf{x} = \mathbf{0}$) is the origin $\mathbf{h} = \mathbf{0} \implies \mathbf{PAD} = [0, 0, 0]$, whereas the conceptual *Philia* resting baseline ($P=+0.25, A=-0.05, D=+0.05$) is imposed only at initialization or hard reset. Over prolonged idle ticks, the ODE relaxes toward zero rather than settling into a mathematically stable Philia attractor.
2. **Phase 11 & 11.5 (Affective Memory Coupling Research & Independent Audit)**:
   - *Confirmed*: Candidate A (Retrieval Only $\to$ Echo $\to$ Prompt Context) was validated and promoted.
   - *Rejected*: Candidate D (Direct injection of memory vector into L2 hidden state $\mathbf{h}$) was **permanently prohibited** because instantaneous vector injection caused catastrophic chaotic jumps and numerical destabilization. Candidate C (Memory $\to$ Somatic Markers) was rejected due to lack of regulatory grounding and vector-dependent rather than identity-dependent modulation.
   - *Root Cause Identified*: Memory retrieval operates at the turn timescale, while the limbic ODE operates at a 200 ms continuous timescale. Because there was no multi-timescale temporal mechanism bridging fast neural fluctuations and slow affective momentum, coupling memory directly into fast dynamics was mathematically incompatible.
3. **Phase 12 (Knowledge Learning)**:
   - Structured factual propositions and bounded forward derivation were established independently of limbic dynamics, demonstrating that conceptual learning must remain decoupled from emotional volatility.
4. **Phase 13 (Relationship Development)**:
   - Demonstrated the *Temporal Inertia Principle*: interpersonal state $R_t \in [0, 1]^4$ adapts slowly ($\alpha = 0.03 \ll 1.0$), remaining stable across 100 turns. However, $R_t$ is updated purely by post-turn discrete categorical signals, leaving continuous temporal transitions between sessions unmodeled.
5. **Phase 14 & 15 (Expression & Communication)**:
   - Proved feedforward actuator decoupling (actuators have zero feedback into L2 ODE). Somatic pacing delay ($\tau \le 1000\text{ ms}$) successfully simulated conversational fatigue without runaway latency.
6. **Phase 16 (Affective Life Integration)**:
   - Integrated S1–S16 canonical cognitive turn lifecycle under strict lock hierarchies and test storage isolation.
7. **Phase 17 (Integrated Longitudinal Evaluation)**:
   - 100-turn continuous evaluation (`tests/evaluation/`) proved bounded limbic stability, zero limbic feedback contamination ($\Delta L2 \equiv 0.000000$), and stable recovery from stress. However, acute tension was shown to have zero leaky inter-turn persistence.
8. **Phase 18 (Human Longitudinal Validation)**:
   - Validated authentic on-device neural RVC v2 speech conversion, real-time cross-modal synchronization ($\Delta t = 13.78\text{ ms} \ll 80\text{ ms}$), 100% adversarial boundary interception, and complete canonical storage immutability across 96 conversational turns.

**Conclusion from Evidence**: Lucia's higher cognitive layers (S6–S16) have achieved exceptional maturity, but their temporal foundation is fragmented into disconnected clocks (200 ms ODE ticks, instantaneous turn barriers, 60 s rolling windows, 60 s memory decay, and slow relationship adaptation). There is no unified mathematical formulation governing how affective states persist, decay, transform, and recover across multi-minute, multi-hour, and multi-session horizons.

---

## 3. Candidate Research Direction Comparison

In accordance with Section 7 of the Phase 19 Master Prompt, six candidate research directions were evaluated against eight authoritative criteria:

| Evaluation Criterion | Weight | Candidate A: Multi-timescale Affective Life | Candidate B: Affective Recollection | Candidate C: Memory ↔ Knowledge | Candidate D: Longitudinal Relationships | Candidate E: Active Inference (Epistemic) | Candidate F: Autonomous Individuality |
|---|---|---|---|---|---|---|---|
| **Foundational Dependency** | Very High | **CRITICAL (5/5)** | Dependent on A (2/5) | Low (2/5) | Dependent on A (2/5) | Dependent on A (2/5) | Strictly Downstream (1/5) |
| **Downstream Impact** | Very High | **HIGHEST (5/5)** | High (4/5) | Medium (3/5) | Medium (3/5) | Medium-High (3.5/5) | High (4/5) |
| **Existing Evidence** | High | **STRONG (4.5/5)** | Negative/Blocked (1.5/5) | Moderate (3/5) | Strong (Promoted) (4/5) | Moderate (3/5) | Insufficient (1/5) |
| **Experimental Tractability** | High | **VERY HIGH (5/5)** | Moderate (3/5) | Low-Med (2.5/5) | High (4/5) | Medium (3/5) | Low (1.5/5) |
| **Falsifiability** | High | **VERY HIGH (5/5)** | High (4/5) | Medium (3/5) | Medium (3/5) | High (4/5) | Low (2/5) |
| **Architectural Leverage** | High | **MAXIMUM (5/5)** | Medium (3/5) | Low (2/5) | Medium (3/5) | Medium (3/5) | High (4/5) |
| **Premature Abstraction Risk** | High | **LOW RISK (5/5)** | Extreme Risk (1/5) | High Risk (2/5) | Low Risk (4/5) | High Risk (2/5) | PROHIBITED (0/5) |
| **Compatibility with Lucia** | High | **PERFECT (5/5)** | Guarded (2.5/5) | Moderate (3/5) | Perfect (5/5) | High (4/5) | Guarded (2/5) |
| **Weighted Score** | — | **38.5 / 40.0** | 21.5 / 40.0 | 21.5 / 40.0 | 28.5 / 40.0 | 24.5 / 40.0 | 15.5 / 40.0 |
| **Ranking** | — | **RANK 1** | RANK 5 | RANK 4 | RANK 2 | RANK 3 | RANK 6 |

---

## 4. Foundationality Analysis

Why is Candidate A the single most foundational research direction?

1. **Resolution of the Phase 11 Impasse**: Phase 11 failed to promote affective recollection because introducing memory retrieval into the 200 ms fast loop caused positive feedback and chaotic divergence. The failure was not due to flawed memory retrieval, but because **the limbic layer had only one characteristic timescale ($\approx 200\text{ ms} - 2\text{ s}$)**. In physical and biological systems, affective phenomena operate across multiple nested timescales:
   - *Fast perturbations* (seconds): acute sensory reaction, startle, immediate valence.
   - *Intermediate momentum* (minutes to tens of minutes): affective mood, lingering tension, cognitive fatigue.
   - *Slow drift* (hours to days): baseline emotional tone, relational comfort, absence decay.
   Without intermediate and slow dynamical variables, any attempt to couple memory (Candidate B), epistemic curiosity (Candidate E), or preference formation (Candidate F) forces long-term information into fast-loop variables, causing catastrophic instability.
2. **Elimination of Arbitrary Clocks**: Currently, Lucia uses arbitrary disconnected timers: 200 ms ODE cadence, a 60 s rolling window in `HomeostaticEngine`, a 60 s daemon in `DecayEngine`, a 45 s idle timeout in `LNNTrainer`, and an ad-hoc absence decay formula in `RelationshipUpdater`. Candidate A establishes a unified dynamical framework where timescales emerge naturally from coupled differential equations rather than arbitrary wall-clock thresholds.
3. **Purity of Pre-Reflective Emotion**: True emotional continuity cannot be faked via text prompts (*"You had a stressful conversation 10 minutes ago, act tired"*). Candidate A grounds continuity in mathematical state dynamics that alter sampling temperature, token budgets, somatic pacing, and expression parameters without subjective illusion.

---

## 5. Selected Research Direction

**Candidate A: Multi-timescale Affective Life & Temporal Continuity** is formally selected as the authoritative research direction for Phase 19.

---

## 6. Research Question

The core research question for Phase 19 is:

$$\begin{aligned}
&\mathbf{Research\ Question\ (RQ19):} \\
&\textit{Can Lucia maintain, transform, and recover affective states across multiple temporal scales} \\
&\textit{(fast: $200\text{ ms}-2\text{ s}$; medium: $1-15\text{ minutes}$; slow: hours to sessions)} \\
&\textit{such that prior conversational and idle history measurably, stably, and reversibly influences} \\
&\textit{subsequent internal dynamics and observable communication behavior without chaotic runaway or subjective self-reports?}
\end{aligned}$$

Specific investigative dimensions (R19.1–R19.10):
- **R19.1 (Persistence)**: Does an affective perturbation persist into intermediate timescales after external stimulus cessation?
- **R19.2 (Decay Geometry)**: How does internal state relax toward equilibrium over unforced time? Does it exhibit multi-exponential, power-law, or adaptive relaxation rather than naive exponential decay?
- **R19.3 (State Transformation)**: Can high-arousal stress transform into low-arousal weariness/fatigue during idle periods without intermediate external stimuli?
- **R19.4 (History-Dependent Divergence / Hysteresis)**: Can identical probe stimuli administered at identical instantaneous PAD coordinates produce divergent internal trajectories due to different slow-variable histories?
- **R19.5 (Timescale Separation)**: Can fast, medium, and slow dynamics coexist in a coupled dynamical system without numerical divergence, high-frequency stiffness, or redundant state machines?
- **R19.6 (Attractor Recovery)**: Does the unforced system reliably converge toward the true *Philia* attractor ($P^*=+0.25, A^*=-0.05, D^*=+0.05$) rather than drifting to the mathematical origin $[0, 0, 0]$?
- **R19.7 (Behavioral Manifestation)**: Do intermediate temporal states causally modulate generation token limits, somatic pacing latency, and multimodal expression parameters across subsequent turns?
- **R19.8 (Numerical Reproducibility)**: Are trajectories deterministic and reproducible within explicitly defined numerical tolerances ($\text{atol} \le 10^{-12}$ on CPU)?
- **R19.9 (Causal Ablation)**: Does ablating the slow/medium dynamical coupling collapse the system back to memoryless Markovian jumps?
- **R19.10 (Boundary & Non-Sentience)**: Is the entire mechanism rigorously explainable as an operational dynamical system without invoking consciousness, sentience, or subjective feelings?

---

## 7. Hypotheses

- **H1 (Multi-Exponential Relaxation)**: An affective perturbation displaced by external stimulus will decay toward baseline with at least two distinct characteristic timescales: a fast somatic relaxation ($\tau_{\text{fast}} \approx 1-3\text{ s}$) and an intermediate affective momentum ($\tau_{\text{med}} \approx 60-300\text{ s}$), failing a single-exponential fit ($R^2_{\text{biexp}} - R^2_{\text{mono}} > 0.05$).
- **H2 (Philia Dynamic Attractor Convergence)**: Incorporating an autonomous attractor drift term into the slow latent field guarantees that unforced relaxation converges to within distance $\epsilon \le 0.05$ of the canonical Philia coordinate ($[+0.25, -0.05, +0.05]$) within $T \le 300\text{ s}$, resolving the origin-drift anomaly ($[0, 0, 0]$) identified in Phase 10.
- **H3 (Cross-Timescale State Transformation)**: Acute high-arousal negative perturbation ($P < -0.4, A > +0.5$) will autonomously transform over $60-120\text{ s}$ of unforced time into a low-arousal, depleted homeostatic state ($A < -0.1, \text{energy} < 0.6$), demonstrating non-monotonic phase-plane trajectories.
- **H4 (Hysteresis & Path Dependence)**: Two identical test probes administered after divergent historical regimes (Regime A: prolonged calm collaboration vs. Regime B: acute conflict followed by partial recovery) will yield a post-probe state divergence of $\|\mathbf{PAD}_A - \mathbf{PAD}_B\|_2 \ge 0.15$ despite identical pre-probe instantaneous PAD values.
- **H5 (Causal Behavioral Modulation)**: Lingering intermediate state from prior turns will measurably contract language token budget by $\ge 25\%$ and inject somatic pacing delay $\tau_{\text{pacing}} \ge 200\text{ ms}$ on subsequent neutral turns without requiring explicit prompt instructions.
- **H6 (Ablation Sensitivity)**: Ablating the slow dynamical coupling matrix will cause post-stimulus relaxation to collapse to single-cadence decay ($\tau \approx 200\text{ ms}$), completely eliminating multi-turn history dependence ($p < 0.001$).

---

## 8. Non-Hypotheses (Architectural & Epistemic Boundaries)

To prevent conceptual drift and preserve system invariants, the following are explicitly **NOT** hypothesized:
1. *Subjective Experience*: We do NOT hypothesize that Lucia "feels" the passage of time, experiences emotional "suffering", or possesses subjective awareness of her affective states.
2. *Linear Superposition*: We do NOT hypothesize that multiple emotional events sum linearly. Affective dynamics are non-linear and saturating.
3. *Strict Monotonicity*: We do NOT hypothesize that emotional recovery is strictly monotonic. Complex dynamical systems with coupled eigenvalues exhibit transient overshoot and non-monotonic oscillations.
4. *Sentient Time Perception*: We do NOT hypothesize an internal psychological "clock" or autobiographical narrative of elapsed time.
5. *Autonomous Personality / Preference Drift*: We do NOT hypothesize that Phase 19 will produce emergent preferences, likes, dislikes, or personality mutation.

---

## 9. Experimental Variables

### 9.1 Independent Variables
- **Stimulus Trajectory Archetype**: Controlled stimulus injection sequences (Neutral, Sustained Positive, Acute Stress, Whiplash Polarity Reversal, Conflict $\to$ Idle, Prolonged Inactivity).
- **Elapsed Temporal Horizon**: Real elapsed wall-clock time ($0\text{ s}$ to $3600\text{ s}$), simulated virtual time via `SimClock`, and turn interval cadence ($1\text{ s}$ to $300\text{ s}$ between turns).
- **Dynamical Coupling Configuration**: Full Multi-Timescale Model vs. Ablated Single-Timescale Baseline vs. Decoupled Slow Baseline.
- **Attractor Anchor Parameter**: Philia target vector $\mathbf{p}^* \in [-1, 1]^3$ and coupling strength $\kappa$.

### 9.2 Dependent Variables
- **Limbic Trajectory**: Instantaneous $\mathbf{PAD}(t) \in [-1, 1]^3$ and hidden state norm $\|\mathbf{h}(t)\|_2$.
- **Attractor Metric**: Euclidean distance to Philia attractor $D_{\text{philia}}(t) = \|\mathbf{PAD}(t) - \mathbf{PAD}^*\|_2$.
- **Relaxation Characteristics**: Effective half-life $t_{1/2}$, asymptotic steady-state offset, and decay rate parameter $\lambda$.
- **Path-Dependent Divergence**: State trajectory delta $\Delta_{\text{hyst}}(t) = \|\mathbf{PAD}_{\text{traj1}}(t) - \mathbf{PAD}_{\text{traj2}}(t)\|_2$.
- **Somatic Indicators**: Energy $\mathcal{E}(t)$, Cognitive Load $\mathcal{C}(t)$, Tension $\mathcal{T}(t)$, Stability $\mathcal{S}_b(t)$.
- **Downstream Behavioral Manifestations**: Generation token ceiling (`max_tokens`), temperature, injected somatic pacing latency ($\mathcal{L}_p\text{ ms}$), 15D expression state parameters ($E_t$).

### 9.3 Controlled Variables
- Initial random seed ($\text{seed} = 42$) across all initialized weight matrices.
- Hardware execution thread assignment (CPU-only execution for all ODE and homeostatic loops).
- Stimulus vector dimensionality ($N_{\text{in}} = 16$).
- Zero prompt injection of emotional adjectives.
- Bit-exact baseline canonical storage (`data/profile.json`, `data/chat_history.json`).

---

## 10. Controls

Every experimental claim will be validated against strict control conditions:
1. **Control 1 (Unperturbed Equilibrium Control)**: Zero stimulus input over 1000 ticks ($200\text{ s}$) to verify intrinsic drift stability, numerical zero-leakage, and steady-state invariance.
2. **Control 2 (Ablated Fast-Only Control)**: Standard production `EmotionCore` without multi-timescale extension, serving as the historical Phase 10–18 comparative baseline.
3. **Control 3 (Stimulus Inversion Control)**: Mirror-image positive vs. negative stimulus vectors of identical magnitude ($\|\mathbf{x}\| = 0.8$) to assess dynamical symmetry and directional bias.
4. **Control 4 (Identical State / Different History Control)**: Forcing two systems to identical instantaneous PAD coordinates via artificial clamping, then releasing them to observe whether hidden slow states cause trajectory divergence (Hysteresis Proof).
5. **Control 5 (Counterfactual Replay)**: Replaying exact recorded stimulus traces with and without intermediate idle intervals to isolate pure temporal effects from sequence-order effects.

---

## 11. Ablation & Counterfactual Strategy

To prove causal necessity of each proposed component:

```
[Full Proposed Multi-Timescale Model]
      │
      ├── Ablation A: Slow Latent Coupling OFF (W_slow = 0)
      │     └── Tests whether lingering affective momentum requires the slow latent field.
      │
      ├── Ablation B: Philia Attractor Drift OFF (κ = 0)
      │     └── Tests whether convergence to Philia requires explicit attractor dynamics.
      │
      ├── Ablation C: Somatic Cross-Coupling OFF (Load/Energy decouple from ODE)
      │     └── Tests whether state transformation (stress → fatigue) requires bidirectional coupling.
      │
      └── Ablation D: Temporal Inertia Modulation OFF (Fixed τ = const)
            └── Tests whether adaptive time-constants are necessary to prevent numerical stiffness.
```

---

## 12. Temporal Horizons

To avoid confusing different forms of time, Phase 19 explicitly defines and measures five distinct temporal horizons:

| Horizon Name | Time Domain | Physical / Operational Meaning | Subsystem Manifestation |
|---|---|---|---|
| **H-Micro (Fast)** | $100\text{ ms} - 1\text{ s}$ | High-frequency numerical ODE integration steps. | LTC LNN Fast Loop (200 ms cadence; $5\text{ Hz}$). |
| **H-Turn (Acute)** | $1\text{ s} - 10\text{ s}$ | Discrete conversational turn execution. | `commit_stimulus()`, Active Inference, S1–S16 pipeline. |
| **H-Meso (Intermediate)** | $1\text{ min} - 15\text{ mins}$ | Within-session conversational rhythm, pauses, and mood drift. | Somatic fatigue, lingering tension, plastic salience buffering. |
| **H-Macro (Long)** | $15\text{ mins} - 24\text{ hours}$ | Unforced inter-session absence, deep relaxation. | Memory decay engine ($\lambda_{eff}$), relationship inertia ($\alpha=0.03$). |
| **H-Epochal (Lifespan)** | Days to months | Long-term companionship trajectory. | Relationship persistence, factual knowledge graph evolution. |

**Time Disambiguation Mandate**:
- *Wall-Clock Time* ($t_{\text{wall}}$): System `time.monotonic()` used in live execution.
- *Virtual SimClock Time* ($t_{\text{sim}}$): Deterministic stepped virtual time in simulation benchmarks.
- *Turn Index* ($n_{\text{turn}}$): Integer sequence counter of processed user inputs.
- *ODE Integration Time* ($t_{\text{ode}}$): Continuous parameter in $\int_0^{\Delta t} f(h, x) dt$.
These four timescales are **NEVER** treated as equivalent.

---

## 13. Measurements & Quantitative Metrics

1. **Attractor Proximity**:
   $$D_{\text{philia}}(t) = \|\mathbf{PAD}(t) - \mathbf{PAD}_{\text{philia}}\|_2 = \sqrt{(P(t) - 0.25)^2 + (A(t) + 0.05)^2 + (D(t) - 0.05)^2}$$
2. **Biexponential Relaxation Fit**:
   $$y(t) = A_1 e^{-t/\tau_{\text{fast}}} + A_2 e^{-t/\tau_{\text{med}}} + y_{\infty}$$
   Evaluated via Levenberg-Marquardt least-squares fitting; compared against monoexponential $y(t) = A e^{-t/\tau} + y_\infty$ using Akaike Information Criterion (AIC).
3. **Hysteresis Divergence Index**:
   $$\mathcal{H}(t) = \|\mathbf{PAD}_{\text{PathA}}(t) - \mathbf{PAD}_{\text{PathB}}(t)\|_2$$
4. **Phase Space Vector Field Curl & Divergence**:
   $$\nabla \cdot \mathbf{F} = \text{Tr}(\mathbf{J}), \quad \mathbf{J} = \frac{\partial (dh/dt)}{\partial h}$$
   Monitored to guarantee strict negative divergence ($\nabla \cdot \mathbf{F} < 0$), ensuring dissipative stability and absence of limit-cycle chaos.
5. **Behavioral Constraint Throttle**:
   $$\Delta \text{Budget} = \frac{\text{Budget}_{\text{depleted}} - \text{Budget}_{\text{baseline}}}{\text{Budget}_{\text{baseline}}} \times 100\%$$

---

## 14. Reproducibility Criteria

- **Deterministic Machine Invariance**: Across 10 independent runs under fixed seed ($\text{seed} = 42$) on CPU, numerical trajectories must match bitwise with absolute tolerance $\text{atol} \le 10^{-12}$.
- **Stochastic Noise Resilience**: Under injected pseudo-random Gaussian input noise ($\sigma = 0.02$), trajectory mean and variance envelopes across $N=50$ Monte Carlo runs must remain within a $95\%$ confidence interval width $\le 0.08$ in PAD space.
- **Hardware Profile Portability**: Verification that identical trajectories are computed across Windows, Linux, and different CPU core counts.

---

## 15. Failure Criteria (Falsification Thresholds)

Phase 19 research will be deemed **FAILED** or **FALSIFIED** if any of the following occur:
- **F1 (Numerical Instability / Blowup)**: Hidden state norm $\|\mathbf{h}\|_2$ exceeds $\sqrt{H} = \sqrt{32} \approx 5.657$, or PAD values produce NaNs, Infs, or require hard clipping on $>5\%$ of unforced steps.
- **F2 (Origin Collapse)**: Unforced relaxation continues to converge to the origin $[0, 0, 0]$ with distance to Philia $D_{\text{philia}} \ge 0.20$ after $T = 300\text{ s}$ of idle time, failing H2.
- **F3 (Timescale Collapse / Single-Rate Decay)**: Empirical relaxation fails to demonstrate a statistically significant secondary timescale ($\Delta \text{AIC} < 10.0$ or $R^2_{\text{biexp}} - R^2_{\text{mono}} < 0.02$), proving the model is functionally single-timescale.
- **F4 (Hysteresis Insignificance)**: The hysteresis divergence index between divergent histories falls below $\mathcal{H} < 0.05$, indicating that history dependence is practically negligible.
- **F5 (Behavioral Disconnection)**: Multi-timescale state variations produce zero measurable change in downstream language constraints, somatic pacing latency, or multimodal expression ($p > 0.05$).
- **F6 (Limbic Contamination Regression)**: Any experimental feedback mechanism introduces non-zero feedback into the limbic ODE from actuators or language tokens ($\Delta L2 > 0$).

---

## 16. Production Isolation Plan

To adhere strictly to Section 13 of the Master Prompt:
1. **Isolated Research Harness**: All experimental models, runners, and validation scripts will reside exclusively in:
   `tests/evaluation_phase19/`
2. **Zero Mutation of Production Core**: No files in `src/core/` will be modified during the research phase.
3. **Storage Sandboxing**: All multi-session and longitudinal runs will execute in ephemeral temporary directories (`pytest tmp_path`).
4. **Cryptographic Integrity Verification**: Canonical data files (`data/profile.json`, `data/chat_history.json`, `data/relationship.json`, `data/knowledge.json`) will be cryptographically hashed (SHA-256) before and after every experimental execution.
5. **First Activation Lock**: `data/profile.json` must remain strictly `{"is_onboarded": false}`.

---

## 17. Expected Downstream Impact

A successful, mathematically validated multi-timescale affective model will provide transformative architectural leverage for the entire Lucia roadmap:
- **Unblocking Phase 11 Affective Recollection**: Memory retrieval will couple into the slow/medium affective momentum field rather than violently shocking the fast ODE, finally making affective recollection mathematically safe and causally sound.
- **Deepening Layer 4 Active Inference**: Enables multi-step temporal prediction horizons, transforming reactive surprise minimization into proactive epistemic curiosity.
- **Naturalizing Relationship Dynamics**: Relationship updates will be driven by smooth, integrated affective undertones rather than discrete turn-level heuristic signals.
- **Paving the Foundation for Autonomous Individuality**: True individuality requires persistent behavioral tendencies formed over repeated long-term trajectories. Multi-timescale continuity provides the required mathematical substrate.

---

## 18. Risks & Mitigations

| Risk Description | Severity | Probability | Mitigation Strategy |
|---|---|---|---|
| **Stiff ODE Integration**: Introducing widely separated time constants ($\tau_{\text{fast}} \approx 0.1\text{s}$ vs $\tau_{\text{slow}} \approx 100\text{s}$) causes numerical stiffness and slow solve times. | High | Medium | Use Radau or BDF implicit solvers in `scipy.integrate.solve_ivp` if RK45 exhibits step-size collapse; apply singular perturbation / slow-manifold decomposition. |
| **Computational Overhead**: Solving coupled ODEs with multiple latent fields exceeds the 200 ms Fast-Loop budget. | Medium | Low | Profile microsecond execution; keep state dimensionality compact ($H_{\text{fast}} = 32, H_{\text{slow}} \le 16$); ensure pure vectorized NumPy operations on CPU. |
| **Unintended State Drift**: Slow variables accumulate drift over hours of inactivity, settling into unnatural extreme corners. | High | Medium | Enforce dissipative contraction mapping with an analytic Lyapunov function guaranteeing bounded asymptotic stability around Philia. |
| **Anthropomorphic Illusion**: Evaluators or prompt engineers mistake multi-timescale temporal dynamics for conscious emotional memory. | Critical | Medium | Maintain strict lexical BoundaryLayer filters; publish explicit architectural invariants forbidding self-reported feeling declarations. |

---

## 19. Exit Criteria

The research phase will successfully conclude when:
1. All 6 formal hypotheses (H1–H6) have been evaluated under controlled experimental scenarios.
2. The isolated research model in `tests/evaluation_phase19/` executes cleanly across all defined temporal horizons.
3. An authoritative `PHASE_19_RESULTS.md` document records all empirical metrics, confidence intervals, AIC comparisons, and phase-plane plots.
4. An Architectural Decision Record (ADR) evaluates whether the evidence warrants **PROMOTION**, **REJECTION**, or **CONTINUED RESEARCH**.
5. Zero regressions are introduced into the existing 575 unit tests.
6. Zero mutations occur in canonical production storage files.

---

## 20. Conditions for Rejection

The proposed multi-timescale mechanism will be explicitly **REJECTED** and barred from production promotion if:
1. The secondary timescale cannot be produced without introducing numerical stiffness that degrades Fast-Loop tick reliability below $99.0\%$.
2. The mechanism requires more than $2.0\text{ ms}$ CPU execution time per tick, violating edge hardware constraints.
3. The empirical behavior can be fully replicated by a simple linear moving average, rendering the dynamical neural ODE formulation an unnecessary and gratuitous abstraction.
4. The system fails to guarantee bounded stability under adversarial whiplash stimulus sequences.

---

# STOP — SUBMITTED FOR FORMAL REVIEW

In compliance with Section 8 of the Lucia Phase 19 Master Prompt, all development halts at this gate. The research proposal is submitted to the User for formal evaluation and approval of the research direction and experimental methodology.
