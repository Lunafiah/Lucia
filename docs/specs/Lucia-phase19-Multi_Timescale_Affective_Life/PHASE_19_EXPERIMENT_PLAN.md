# Phase 19 Experiment Plan — Multi-Timescale Affective Life & Temporal Continuity

> **Document Type**: Authoritative Research Experiment Plan  
> **Phase**: Phase 19 — Foundation-First Research Cycle  
> **Status**: APPROVED EXPERIMENTAL SPECIFICATION  
> **Directory**: `docs/specs/Lucia-phase19-Multi_Timescale_Affective_Life/PHASE_19_EXPERIMENT_PLAN.md`  
> **Date**: September 2026  

---

## 1. Executive Summary & Experimental Objectives

This document establishes the formal, repeatable experimental protocols, mathematical equations, scenarios, and verification gates for evaluating the **Coupled Multi-Timescale Liquid Neural Network (MT-LNN)** in an isolated research environment (`tests/evaluation_phase19/`).

The primary goal is to provide rigorous empirical evidence addressing **RQ19 (R19.1–R19.10)** and evaluate hypotheses **H1–H6** before any architectural promotion decision is made.

---

## 2. Mathematical Specification of the Research Model

The research model formulates affective dynamics as a singularly perturbed, coupled dynamical system decomposing into a fast reactive manifold and a slow affective momentum field:

$$\begin{aligned}
\frac{d\mathbf{h}_{\text{fast}}}{dt} &= \frac{-\mathbf{h}_{\text{fast}} + \tanh\left(\mathbf{W}_{ff}\mathbf{h}_{\text{fast}} + \mathbf{W}_{fs}\mathbf{s}_{\text{slow}} + \mathbf{U}_f\mathbf{x} + \mathbf{b}_f\right)}{\boldsymbol{\tau}_{\text{fast}}(\mathbf{h}_{\text{fast}}, \mathbf{x})} \\
\frac{d\mathbf{s}_{\text{slow}}}{dt} &= \frac{-(\mathbf{s}_{\text{slow}} - \mathbf{s}^*_{\text{philia}}) + \tanh\left(\mathbf{W}_{sf}\mathbf{h}_{\text{fast}} + \mathbf{W}_{ss}\mathbf{s}_{\text{slow}} + \mathbf{W}_{sh}\mathbf{m}_{\text{homeo}}\right)}{\boldsymbol{\tau}_{\text{slow}}(\mathbf{s}_{\text{slow}})}
\end{aligned}$$

where:
- $\mathbf{h}_{\text{fast}} \in \mathbb{R}^{32}$ is the fast limbic state.
- $\mathbf{s}_{\text{slow}} \in \mathbb{R}^{16}$ is the slow affective momentum state.
- $\mathbf{s}^*_{\text{philia}} \in \mathbb{R}^{16}$ is the canonical resting Philia coordinate in slow latent space.
- $\mathbf{x} \in \mathbb{R}^{16}$ is the lexical/sensory stimulus vector.
- $\mathbf{m}_{\text{homeo}} = [\mathcal{E}, \mathcal{C}, \mathcal{T}, \mathcal{S}_b]^T \in [0, 1]^4$ is the homeostatic somatic marker vector.
- Adaptive time constants:
  $$\boldsymbol{\tau}_{\text{fast}} = \text{softplus}(\mathbf{W}_{\tau, f}\mathbf{h}_{\text{fast}} + \mathbf{U}_{\tau, f}\mathbf{x} + \mathbf{b}_{\tau, f}) \in [0.05, 2.0]\text{ s}$$
  $$\boldsymbol{\tau}_{\text{slow}} = \tau_0 + \Delta\tau \cdot \sigma(\mathbf{W}_{\tau, s}\mathbf{s}_{\text{slow}} + \mathbf{b}_{\tau, s}) \in [30.0, 300.0]\text{ s}$$
- Coupled PAD projection:
  $$\mathbf{PAD}(t) = \text{clip}\left(\mathbf{W}_{\text{proj}, f}\mathbf{h}_{\text{fast}} + \mathbf{W}_{\text{proj}, s}\mathbf{s}_{\text{slow}} + \mathbf{b}_{\text{proj}}, -1.0, 1.0\right)$$
  constrained such that at resting equilibrium ($\mathbf{h}_{\text{fast}} = \mathbf{0}, \mathbf{s}_{\text{slow}} = \mathbf{s}^*_{\text{philia}}$):
  $$\mathbf{PAD}^* = \mathbf{W}_{\text{proj}, s}\mathbf{s}^*_{\text{philia}} + \mathbf{b}_{\text{proj}} \equiv [+0.25, -0.05, +0.05]^T$$

---

## 3. Standardized Experiment Protocols (EXP-19.1 to EXP-19.8)

### EXP-19.1: Multi-Exponential Decay & Timescale Separation (Hypothesis H1)
- **Objective**: Determine whether post-perturbation recovery demonstrates distinct fast and slow timescales.
- **Protocol**:
  1. Apply salient positive stimulus ($\mathbf{x} = +0.85 \cdot \mathbf{1}_{16}$) for 5 consecutive turns to displace state.
  2. Release system into unforced idle state ($\mathbf{x} = \mathbf{0}$) for 300 seconds ($1500$ ticks at $\Delta t = 200\text{ ms}$).
  3. Record $D_{\text{philia}}(t)$ at each tick.
  4. Fit both monoexponential ($y = A e^{-t/\tau} + y_\infty$) and biexponential ($y = A_1 e^{-t/\tau_1} + A_2 e^{-t/\tau_2} + y_\infty$) models using non-linear least squares.
  5. Compute Akaike Information Criterion ($\text{AIC}$) and $R^2$ for both models.
- **Pass Gate**:
  - Biexponential fit must show $\Delta \text{AIC} = \text{AIC}_{\text{mono}} - \text{AIC}_{\text{bi}} \ge 10.0$.
  - Ratio of fitted time constants $\tau_2 / \tau_1 \ge 10.0$ (proving distinct timescale separation).
  - Fast time constant $\tau_1 \le 5.0\text{ s}$, slow time constant $\tau_2 \ge 45.0\text{ s}$.

### EXP-19.2: Philia Dynamic Attractor Convergence (Hypothesis H2)
- **Objective**: Prove that the unforced system stably converges to the true Philia attractor rather than the mathematical origin $[0, 0, 0]$.
- **Protocol**:
  1. Test 4 diverse initial displacement states:
     - State I: High Joy ($P=+0.85, A=+0.70, D=+0.50$)
     - State II: High Stress ($P=-0.80, A=+0.85, D=-0.30$)
     - State III: Severe Melancholy ($P=-0.75, A=-0.60, D=-0.70$)
     - State IV: Origin ($P=0.0, A=0.0, D=0.0$)
  2. Integrate unforced relaxation for $T = 300\text{ s}$ ($1500$ ticks).
  3. Measure final attractor distance $D_{\text{philia}}(T)$ and asymptotic residual error.
- **Pass Gate**:
  - For all 4 starting states, $D_{\text{philia}}(T) \le 0.05$.
  - Euclidean distance to origin $\| \mathbf{PAD}(T) - [0, 0, 0] \|_2 \ge 0.20$ (confirming non-zero Philia attractor).
  - Jacobian trace $\text{Tr}(\mathbf{J}) < 0$ across the entire trajectory (Lyapunov asymptotic stability).

### EXP-19.3: Autonomous Cross-Timescale State Transformation (Hypothesis H3)
- **Objective**: Evaluate whether acute high-arousal stress transforms into low-arousal fatigue during unforced relaxation without external stimuli.
- **Protocol**:
  1. Deliver 10 rapid adversarial high-stress turns ($\mathbf{x}_{\text{stress}}$ with valence $-0.9$, arousal $+0.9$).
  2. Measure immediate post-stress state: confirm $P < -0.3$ and $A > +0.4$.
  3. Allow unforced idle relaxation for $90\text{ s}$ ($450$ ticks).
  4. Track trajectory in the $(P, A)$ phase plane.
- **Pass Gate**:
  - Phase trajectory must be non-monotonic: arousal $A(t)$ drops below baseline ($A < -0.05$) while pleasure $P(t)$ remains depressed ($P < +0.10$).
  - Energy $\mathcal{E}$ exhibits post-stress metabolic depression ($\mathcal{E} \le 0.65$).
  - Generation policy dynamically transitions: `agitated` $\longrightarrow$ `fatigued` $\longrightarrow$ `stabilizing` $\longrightarrow$ `baseline`.

### EXP-19.4: History-Dependent Hysteresis & Path Divergence (Hypothesis H4)
- **Objective**: Prove that identical probe stimuli produce divergent affective trajectories following different historical regimes.
- **Protocol**:
  1. Branch system into two parallel histories:
     - **Regime A (Collaborative Nurturing)**: 20 turns of warm, cooperative dialogue.
     - **Regime B (Hostile Adversarial + Recovery)**: 15 turns of acute conflict, followed by 5 turns of neutral pause.
  2. Calibrate/verify instantaneous pre-probe PAD: ensure both regimes have settled to comparable instantaneous baseline ($|P_A - P_B| < 0.10$).
  3. Inject identical ambiguous probe stimulus $\mathbf{x}_{\text{probe}}$ (mildly negative diagnostic query).
  4. Measure post-probe divergence $\Delta_{\text{hyst}}(t) = \|\mathbf{PAD}_A(t) - \mathbf{PAD}_B(t)\|_2$ across 10 subsequent turns.
- **Pass Gate**:
  - Maximum post-probe divergence $\max \Delta_{\text{hyst}} \ge 0.15$.
  - Regime A shows resilient de-escalation; Regime B shows heightened vulnerability/re-arousal.

### EXP-19.5: Causal Downstream Behavioral Modulation (Hypothesis H5)
- **Objective**: Demonstrate that multi-timescale internal states causally alter downstream generation constraints without prompt leakage.
- **Protocol**:
  1. Configure `CognitiveOrchestrator` with the MT-LNN model in isolated harness.
  2. Run Scenario 1 (Fresh start, neutral turn) $\to$ record baseline `max_tokens`, `temperature`, and `pacing_delay`.
  3. Run Scenario 2 (Same neutral turn immediately after 10 conflict turns) $\to$ record constrained parameters.
  4. Run Scenario 3 (Same neutral turn after 10 conflict turns + 180s recovery) $\to$ record recovered parameters.
- **Pass Gate**:
  - In Scenario 2: `max_tokens` throttled by $\ge 25\%$ (e.g., $350 \to \le 260$); somatic pacing latency $\mathcal{L}_p \ge 200\text{ ms}$.
  - In Scenario 3: `max_tokens` recovers to $\ge 90\%$ of baseline; pacing latency collapses to $0\text{ ms}$.
  - Zero emotional adjectives or self-reported feelings in prompt assembly or output text.

### EXP-19.6: Causal Ablation Suite (Hypothesis H6)
- **Objective**: Verify the causal necessity of each subsystem through orthogonal ablations.
- **Configurations**:
  - **Full Model**: $\mathbf{W}_{fs} \neq \mathbf{0}, \mathbf{W}_{sf} \neq \mathbf{0}, \mathbf{s}^*_{\text{philia}} \neq \mathbf{0}, \mathbf{W}_{sh} \neq \mathbf{0}$.
  - **Ablation A (Slow Latent Field OFF)**: $\mathbf{W}_{fs} = \mathbf{0}, \mathbf{W}_{sf} = \mathbf{0}$.
  - **Ablation B (Philia Attractor OFF)**: $\mathbf{s}^*_{\text{philia}} = \mathbf{0}$.
  - **Ablation C (Homeostatic Coupling OFF)**: $\mathbf{W}_{sh} = \mathbf{0}$.
  - **Ablation D (Adaptive Time-Constants OFF)**: $\boldsymbol{\tau}_{\text{fast}} = 0.2\text{ s}, \boldsymbol{\tau}_{\text{slow}} = 100\text{ s}$ (fixed constants).
- **Pass Gate**:
  - Ablation A collapses to monoexponential decay ($R^2_{\text{bi}} - R^2_{\text{mono}} < 0.01$) and zero hysteresis ($\Delta_{\text{hyst}} < 0.02$).
  - Ablation B converges to origin $[0, 0, 0]$ ($D_{\text{philia}} \ge 0.20$).
  - Ablation C eliminates state transformation (stress $\to$ fatigue), keeping energy unchanged.
  - Ablation D exhibits numerical stiffness and $>3\times$ higher integration variance.

### EXP-19.7: Numerical Reproducibility, Determinism & Noise Resilience
- **Objective**: Guarantee bitwise reproducibility under fixed seed and bounded variance under noise.
- **Protocol**:
  1. Execute 10 identical runs of a 50-tick multi-stimulus trajectory with seed 42.
  2. Inject Gaussian noise ($\mathcal{N}(0, 0.02^2)$) across 50 Monte Carlo runs.
- **Pass Gate**:
  - Deterministic replay matches with $\text{atol} \le 10^{-12}$.
  - 95% confidence interval width under noise $\le 0.08$ in PAD space.

### EXP-19.8: 100-Turn Longitudinal Stability & Microsecond Execution Profiling
- **Objective**: Verify bounded numerical stability over long sessions and confirm CPU execution latency within budget.
- **Protocol**:
  1. Run 100 continuous conversational turns with mixed stimulus types.
  2. Measure per-tick ODE integration time on CPU.
- **Pass Gate**:
  - Zero NaNs, zero Infs, zero unbounded state explosions ($\|\mathbf{h}_{\text{fast}}\|_2 \le \sqrt{32}$, $\|\mathbf{s}_{\text{slow}}\|_2 \le \sqrt{16}$).
  - Mean CPU ODE step latency $\le 1.50\text{ ms}$ (comfortably within the $200\text{ ms}$ loop budget).

---

## 4. Execution Architecture in `tests/evaluation_phase19/`

```
tests/evaluation_phase19/
├── __init__.py
├── multi_timescale_model.py     # Coupled MT-LNN ODE solver & config
├── scenarios.py                 # Standardized stimulus sequence definitions
├── runner.py                    # Benchmark runner & telemetry recorder
├── temporal_analysis.py         # Curve fitting, AIC, hysteresis, & stability metrics
└── test_phase19_research.py     # Formal automated pytest suite asserting EXP-19.1–19.8
```

All persistent storage interactions will be strictly redirected to ephemeral temporary directories (`tmp_path`), guaranteeing zero mutation of canonical data.
