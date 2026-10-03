# Phase 21 — Long-Term Relational Consolidation & Synaptic Homeostasis Specification

> **Authoritative Research Specification: Multi-Timescale Synaptic Plasticity, Dynamic Homeostasis, Bounded Relational Inertia, and Counterfactual Plasticity Controls**  
> **Historical Research Status:** `[RESEARCH VALIDATED]` (15/15 Hypotheses H1–H6 Validated)  
> **Production Realization Status:** `[VALIDATED / PRODUCTION IMPLEMENTED]` (Promoted to production in commit `58a509c`)  
> **Directory:** `docs/specs/Lucia-phase21-Relational_Consolidation/PHASE_21_RESEARCH_SPEC.md`  
> **Preceding Research Baseline:** Phase 20 Production Commit `f20420a`  
> **Canonical Storage Invariant:** `data/profile.json == {"is_onboarded": false}` (bit-exact)

---

## 1. Research Authority Boundary & Governance Mandate

The research direction, scientific objectives, mathematical mechanisms, hypotheses (H1–H6), evaluation criteria, and promotion policy governing Phase 21 have been established by the project owner. In accordance with the mandatory Operating Procedures in `AGENTS.md`:

1. **Strict Research Authority Boundary**: AI agents MUST NOT redefine the research direction, introduce speculative alternative mechanisms, alter pre-registered hypotheses, or tune experimental scenarios to force hypothesis acceptance.
2. **"Failure is Informative" Protocol**: Scenarios must be naturalistic, neutral, and unforced. If any condition fails pre-registered criteria, this constitutes an informative empirical boundary of the mechanism, NOT a bug to be patched.
3. **Promotion Policy**: Passing automated evaluation tests demonstrates empirical validation within the isolated harness; it does NOT authorize automatic production mutation. The milestone status remains strictly **`[RESEARCH VALIDATED / PROMOTION DEFERRED]`**, with final promotion reserved for project owner governance.
4. **Zero Production Mutation**: Neither `src/core/` nor canonical persistent runtime data (`data/`) may be modified during this research cycle.

---

## 2. Scientific Motivation & Context

In Phase 19, Lucia established a continuous, coupled dual-timescale limbic substrate (MT-LNN):
- Fast reactive dynamics ($\mathbf{h}_{\text{fast}} \in \mathbb{R}^{32}$, $\tau_f \in [0.10, 1.50]\text{ s}$) responding to immediate lexical valence;
- Slow affective latent dynamics ($\mathbf{s}_{\text{slow}} \in \mathbb{R}^{16}$, $\tau_{\text{charge}} = 3.50\text{ s}, \tau_{\text{decay}} = 28.00\text{ s}$) retaining multi-turn emotional momentum;
- Philia resting attractor grounding ($\mathbf{p}^*_{\text{philia}} = [+0.25, -0.05, +0.05]$) guaranteeing unforced convergence toward calm relational warmth.

In Phase 20, closed-loop affective recollection was validated and integrated into production (`f20420a`), enabling episodic memory cues from SDM to selectively perturb the slow latent field without altering baseline synaptic weights.

However, a fundamental architectural asymmetry remained:
While Lucia could remember past interactions via explicit episodic memory lookup, her underlying **synaptic weights and resting attractors remained completely static**. No matter how many months or years of warmth, tension, repair, or shared experience transpired, the core continuous differential equations possessed **zero long-term plasticity**. When idle, the system always reset to the exact generic factory baseline.

Phase 21 investigates the mathematical and computational mechanisms of **long-term relational consolidation and synaptic homeostasis**: allowing sustained relational history to gradually and safely attune slow-field attractors and offline synaptic parameters during unforced rest, while preserving homeostatic stability and the canonical Philia attractor manifold.

---

## 3. Mathematical Mechanisms

```
┌────────────────────────────────────────────────────────────────────────────────────────┐
│               PHASE 21 ARCHITECTURE: 3-TIER MULTI-TIMESCALE PLASTICITY                │
├────────────────────────────────────────────────────────────────────────────────────────┤
│  TIER 1: FAST REACTIVE LAYER (Milliseconds to Seconds)                                │
│    h_f in R^32, tau_f in [0.10, 1.50]s                                                 │
│    dh_f/dt = (-h_f + tanh(W_f h_f + U_f x + b_f)) / tau_f                              │
├────────────────────────────────────────────────────────────────────────────────────────┤
│  TIER 2: SLOW RELATIONAL ATTRACTOR (Minutes to Hours)                                  │
│    s_slow in R^16, tau_slow,charge = 3.50s, tau_slow,decay = 28.00s                       │
│    s*_eff(R) = s*_philia + W_rel (R_t - R_0)                                           │
│    sigma_max(W_rel) <= 0.08                                                            │
│    PAD_eff = clip(W_proj_f h_f + W_proj_s (s_slow - s*_philia) + p*_philia, -1, 1)     │
├────────────────────────────────────────────────────────────────────────────────────────┤
│  TIER 3: OFFLINE SYNAPTIC CONSOLIDATION (Sleep / Unforced Rest)                       │
│    Experience Buffer: (x_t, h_t, h_{t+1}, s_t, R_t, salience >= 0.50)                  │
│    L_total = 1/K sum MSE(h_pred, h_target) + lambda_homeo ||Theta - Theta_0||^2        │
│              + lambda_philia ||ODE(model, 0, t)||^2                                    │
│    CPU Backprop-through-ODE via torchdiffeq; AdamW; lock swap duration <= 2.0ms        │
└────────────────────────────────────────────────────────────────────────────────────────┘
```

### 3.1 Tier 1 & 2: Coupled Continuous MT-LNN with Attractor Shift

The continuous state evolves according to the coupled ordinary differential equations:

$$\frac{d\mathbf{h}_f}{dt} = \frac{-\mathbf{h}_f + \tanh\Big(\mathbf{W}_f \mathbf{h}_f + \mathbf{U}_f \mathbf{x}(t) + \mathbf{W}_{fs} \mathbf{s}_s + \mathbf{b}_f\Big)}{\boldsymbol{\tau}_f(\mathbf{h}_f, \mathbf{x})}$$

$$\frac{d\mathbf{s}_s}{dt} = -\frac{\mathbf{s}_s - \mathbf{s}^*_{\text{eff}}(\mathbf{R}_t)}{\tau_{\text{slow, decay}}} + \frac{\tanh\Big(\mathbf{W}_{sf} \mathbf{h}_f + \mathbf{W}_{sh} \Delta\mathbf{m} + \mathbf{W}_{\text{rec}} \mathbf{r}_{\text{slow}}\Big)}{\tau_{\text{slow, charge}}}$$

where:
- $\mathbf{x}(t) \in \mathbb{R}^8$ is the incoming sensory/conversational stimulus vector;
- $\mathbf{s}^*_{\text{eff}}(\mathbf{R}_t) \in \mathbb{R}^{16}$ is the relationship-conditioned slow-field resting equilibrium:
  $$\mathbf{s}^*_{\text{eff}}(\mathbf{R}_t) = \mathbf{s}^*_{\text{philia}} + \mathbf{W}_{\text{rel}} (\mathbf{R}_t - \mathbf{R}_0)$$
- $\mathbf{R}_t \in [0, 1]^4$ represents the 4-dimensional relationship state vector:
  $$\mathbf{R} = [R_{\text{familiarity}}, R_{\text{trust}}, R_{\text{attunement}}, R_{\text{stability}}]^T$$
- $\mathbf{R}_0 = [0.10, 0.10, 0.05, 0.50]^T$ represents the unonboarded initial baseline.

### 3.2 Spectral Norm Bound on Relational Coupling ($\mathbf{W}_{\text{rel}}$)

To guarantee that relational attunement cannot induce runaway drift, volatile emotional shifts, or bifurcations:
$$\|\mathbf{W}_{\text{rel}}\|_2 = \sigma_{\max}(\mathbf{W}_{\text{rel}}) \le 0.08$$

Given that $\mathbf{R}_t \in [0, 1]^4$, the maximum displacement vector $\|\mathbf{R}_t - \mathbf{R}_0\|_2 \le \sqrt{2.5} \approx 1.5811$. Setting $\sigma_{\max}(\mathbf{W}_{\text{rel}}) \le 0.05$ strictly guarantees:
$$\|\mathbf{s}^*_{\text{eff}}(\mathbf{R}) - \mathbf{s}^*_{\text{philia}}\|_2 \le 0.08$$
$$\|\mathbf{PAD}^*_{\text{eff}} - \mathbf{p}^*_{\text{philia}}\|_2 \le 0.05$$

### 3.3 Dynamic Homeostatic Recovery Equations

During unforced rest / idle intervals ($\mathbf{x} = \mathbf{0}$), metabolic energy $\mathcal{E}$, cognitive tension $\mathcal{T}$, and cognitive load $\mathcal{C}$ recover via exponential relaxation:

$$\frac{d\mathcal{E}}{dt} = \gamma_E (1 - \mathcal{E}), \quad \gamma_E = 0.05\text{ s}^{-1}$$
$$\frac{d\mathcal{T}}{dt} = -\gamma_T \mathcal{T}, \quad \gamma_T = 0.10\text{ s}^{-1}$$
$$\frac{d\mathcal{C}}{dt} = -\gamma_C \mathcal{C}, \quad \gamma_C = 0.08\text{ s}^{-1}$$

Given initial depleted states ($\mathcal{E}_0 \in [0.25, 0.40]$, $\mathcal{T}_0 \in [0.60, 0.85]$):
- At $t=45\text{s}$: $\mathcal{E}(45) \ge 0.90$ and $\mathcal{T}(45) \le 0.01$;
- At $t=60\text{s}$: $\mathcal{E}(60) \ge 0.95$ and $\mathcal{T}(60) \le 0.005$.

### 3.4 Tier 3: Offline Backpropagation-Through-ODE Consolidation

During quiescent sleep/idle intervals, salient interaction experiences ($\text{salience} \ge 0.50$) accumulated in the episodic replay buffer are consolidated into the continuous neural parameters $\boldsymbol{\Theta} = \{\mathbf{W}_f, \mathbf{U}_f, \mathbf{b}_f, \mathbf{W}_\tau, \mathbf{U}_\tau, \mathbf{b}_\tau\}$:

$$\mathcal{L}_{\text{consolidation}} = \frac{1}{K}\sum_{k=1}^K \|\mathbf{h}_{\text{pred}}^{(k)} - \mathbf{h}_{\text{target}}^{(k)}\|_2^2 + \lambda_{\text{homeo}} \|\boldsymbol{\Theta} - \boldsymbol{\Theta}_0\|_2^2 + \lambda_{\text{philia}} \|\mathbf{h}_{\text{unforced}}(\Delta t)\|_2^2$$

where:
- Sequential multi-turn continuity is enforced: $\mathbf{h}_{0}^{(k)} = 0.60 \mathbf{h}_{\text{prev}} + 0.40 \mathbf{h}_{\text{before}}^{(k)}$;
- $\lambda_{\text{homeo}} = 0.05$ anchors the parameters to the initial baseline, preventing catastrophic forgetting;
- $\lambda_{\text{philia}} = 0.10$ penalizes unforced drift away from origin;
- Optimization is conducted via AdamW on CPU with gradient norm clipping ($\le 1.0$).

---

## 4. Pre-Registered Hypotheses & Acceptance Criteria

### H1: Homeostatic Settling & Dynamic Retention
- **Criterion 1.1**: Under unforced rest from depleted states ($\mathcal{E}_0 \in [0.25, 0.40]$, $\mathcal{T}_0 \in [0.60, 0.85]$), $\mathcal{E}(45) \ge 0.90$ and $\mathcal{T}(45) \le 0.01$.
- **Criterion 1.2**: At $t=60\text{s}$, $\mathcal{E}(60) \ge 0.95$ and $\mathcal{T}(60) \le 0.005$.
- **Criterion 1.3**: Catastrophic forgetting drift on standard probe suite $\le 10.0\%$.

### H2: Relational Inertia Consolidation
- **Criterion 2.1**: Spectral norm bound $\|\mathbf{W}_{\text{rel}}\|_2 = \sigma_{\max}(\mathbf{W}_{\text{rel}}) \le 0.08$.
- **Criterion 2.2**: Maximum equilibrium displacement $\|\mathbf{s}^*_{\text{eff}}(\mathbf{R}) - \mathbf{s}^*_{\text{philia}}\|_2 \le 0.08$ across all $\mathbf{R} \in [0, 1]^4$.
- **Criterion 2.3**: Maximum resting PAD displacement $\|\mathbf{PAD}^*_{\text{eff}} - \mathbf{p}^*_{\text{philia}}\|_2 \le 0.05$.
- **Criterion 2.4**: Single-turn relational displacement velocity $\Delta s_{\text{turn}} \le 0.015$.

### H3: Philia Attractor Manifold Invariance & Reversibility
- **Criterion 3.1**: Canonical uncoupled restoration error $\epsilon = \|\mathbf{PAD}(\infty) - \mathbf{p}^*_{\text{philia}}\|_2 < 10^{-4}$.
- **Criterion 3.2**: Conditioned equilibrium stability with error $< 10^{-4}$ and bounded displacement $\le 0.05$.
- **Criterion 3.3**: Longitudinal reversibility under relationship absence decay: restoration error $< 10^{-4}$.

### H4: Computational Plasticity & Counterfactual Controls
- **Criterion 4.1**: Directional cosine similarity $\text{CosineSim}(\Delta\boldsymbol{\Theta}_{\text{auth}}, \Delta\boldsymbol{\Theta}_{\text{shuffled}}) \le 0.20$.
- **Criterion 4.2**: Directional cosine similarity $\text{CosineSim}(\Delta\boldsymbol{\Theta}_{\text{auth}}, \Delta\boldsymbol{\Theta}_{\text{random}}) \le 0.20$.
- **Criterion 4.3**: Trajectory divergence ratio $\text{AUC}_{\text{auth}} / \text{AUC}_{\text{random}} \ge 2.50$.
- **Criterion 4.4**: Statistical outcome specificity effect size Cohen's $d \ge 1.20$ across repeated trials between authentic and counterfactual cohorts.

### H5: Separated Computational Performance & Concurrency Discipline
- **Criterion 5.1**: Forward ODE step latency $p50 < 1.50\text{ms}, p95 < 3.00\text{ms}$.
- **Criterion 5.2**: Backward ODE step latency $p50 < 25.0\text{ms}, p95 < 50.0\text{ms}$.
- **Criterion 5.3**: Full consolidation batch ($K=8$) wall-clock time $< 400.0\text{ms}$ on CPU.
- **Criterion 5.4**: Parameter swap latency under `_train_lock` $\le 2.0\text{ms}$.
- **Criterion 5.5**: GPU VRAM allocation strictly $0.0\text{ MB}$.
- **Criterion 5.6**: Active-turn overhead interference $\Delta t \le 0.20\text{ms}$ ($\le 5\%$).
- **Criterion 5.7**: Max turn lock blocking duration $\le 2.0\text{ms}$.
- **Criterion 5.8**: 1,000 concurrent iterations completed without deadlocks or timeouts.

### H6: Multi-Layer Pre-Reflective Discipline & Boundary Safety
- **Criterion 6.1**: Layer 1 Lexical Gate: 100% regex filter enforcement against `BoundaryLayer`. 100% positive controls intercepted and redacted. 100% operational non-introspective outputs preserved.
- **Criterion 6.2**: Layer 2 Structural Gate: Zero introspective self-model fields across all data models (`HomeostaticState`, `ConsolidationExperience`, `SynapticParameterState`, `HomeostaticTrajectory`, `SimulationResult`). Strict latent tensor discipline confirmed.
