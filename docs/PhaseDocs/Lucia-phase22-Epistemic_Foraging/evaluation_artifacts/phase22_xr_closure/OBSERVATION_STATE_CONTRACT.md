# OBSERVATION-TO-CONTINUOUS STATE CONTRACT & INTERFACE SPECIFICATION

> **Document Type:** System Architectural Contract  
> **Status:** APPROVED AS RESEARCH SPECIFICATION  
> **Interface Target:** Observation Layer $\to$ Continuous Cognitive Dynamics $\to$ P23 Interface  
> **Mathematical Domain:** $\mathbf{u}_t \to \mathbf{y}_t \to \mathbf{z}(t) \to \boldsymbol{\psi}_{\text{user}}(t)$  

---

## 1. System Separation of Concerns

A fundamental architectural finding of Phase 22-XR is that **collapsing perceptual observation, cognitive belief dynamics, and natural language generation into a single monolithic model causes compounding failures**.

To guarantee maintainability, interchangeable models, and deterministic verification, the architecture enforces strict boundaries:

```text
┌─────────────────────────────────────────────────────────────────────────────┐
│                           PERCEPTUAL OBSERVATION                            │
│                        Observation != Cognitive State                       │
│  - Raw utterance tokens & prosodic acoustic features                        │
│  - Stateless forward encoding                                               │
│  - Emits: Semantic Evidence vector y_t and noise covariance R_t             │
└──────────────────────────────────────┬──────────────────────────────────────┘
                                       │
                                       ▼ (Contract 1: IObservationEvidence)
┌─────────────────────────────────────────────────────────────────────────────┐
│                         CONTINUOUS BELIEF DYNAMICS                          │
│                          Cognitive State != Language                        │
│  - Continuous ODE prior integration (dot{z} = F z + w)                      │
│  - Discrete observation update via Kalman / Bayesian filter                 │
│  - Multi-step predictive trajectory forecasting                             │
│  - Owns: Latent state z(t) in R^6 and epistemic covariance Sigma(t)         │
└──────────────────────────────────────┬──────────────────────────────────────┘
                                       │
                                       ▼ (Contract 2: IP23UserBeliefInterface)
┌─────────────────────────────────────────────────────────────────────────────┐
│                         PHASE 23 LANGUAGE RENDERING                         │
│                           User State != Surface Text                        │
│  - Conditioned on psi_user = [mu_z, diag(Sigma_z)] in R^12                 │
│  - Local GGUF language model with prompt conditioning                       │
│  - Generates conversational response and non-verbal blendshape cues         │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## 2. End-to-End Conceptual Pipeline

The full mathematical flow from raw user input to downstream action follows this sequence:

```text
User Input: u_t = (tokens_t, audio_features_t, timing_t)
    │
    ▼
[Step 1: Observation Encoder]
    Outputs raw high-dimensional perceptual representation:
    h_t = f_enc(u_t; theta_enc)
    │
    ▼
[Step 2: Semantic Evidence Extraction]
    Extracts semantic features or dialogue act logits:
    s_t = f_sem(h_t)
    │
    ▼
[Step 3: Calibration & Measurement Projection]
    Applies temperature scaling / isotonic calibration and inverse measurement map:
    y_t = Calibrate(s_t),  z_obs = g^-1(y_t),  R_t = Cov(Residuals)
    │
    ▼
[Step 4: Continuous Prior Integration (ODE)]
    Evolves belief across physical inter-turn interval Delta t:
    z_prior = exp(F * Delta t) * z_{t-1}
    Sigma_prior = exp(F * Delta t) * Sigma_{t-1} * exp(F^T * Delta t) + Q_continuous
    │
    ▼
[Step 5: Observation Forcing & Filter Update]
    Fuses prior with new observation evidence:
    K_t = Sigma_prior * H^T * (H * Sigma_prior * H^T + R_t)^-1
    z_t = z_prior + K_t * (z_obs - H * z_prior)
    Sigma_t = (I - K_t * H) * Sigma_prior
    │
    ▼
[Step 6: Trajectory Density Forecasting]
    Generates multi-step predictive trajectories for planning:
    z_pred(t + tau),  Sigma_pred(t + tau)  via Lyapunov diffusion
    │
    ▼
[Step 7: P23 Downstream Interface]
    Constructs language-independent continuous belief vector:
    psi_user(t) = [z_t^T,  diag(Sigma_t)^T]^T in R^12
```

---

## 3. Mathematical Contract Specifications

### 3.1 Contract 1: Observation Evidence Interface (`IObservationEvidence`)
Any observation encoder must output an evidence tuple $(\mathbf{y}_t, \mathbf{R}_t)$:

- **Semantic Evidence Vector $\mathbf{y}_t \in \mathbb{R}^{d_y}$:**
  Normalized representation of conversational cues. Coordinates are bounded in $[-1, 1]$ or represented as a calibrated probability distribution on the simplex $\Delta^K$.
- **Observation Noise Covariance $\mathbf{R}_t \in \mathbb{R}^{d_y \times d_y}$:**
  Symmetric positive-definite matrix representing measurement uncertainty:
  $$\mathbf{R}_t \succ 0, \quad \mathbf{R}_t = \mathbf{R}_t^T$$
  When inputs are ambiguous, noisy, or sparse, the encoder increases $\text{Tr}(\mathbf{R}_t)$, automatically instructing the filter to trust its continuous prior over the noisy observation.

### 3.2 Contract 2: Continuous Latent State Space ($\mathbf{z} \in \mathbb{R}^6$)
The continuous user-state vector $\mathbf{z}(t)$ models six persistent orthogonal dimensions:
1. $z_1$: **Cognitive Load / Urgency** ($-1$: relaxed/spacious $\to +1$: overwhelmed/urgent)
2. $z_2$: **Relational Valence** ($-1$: cold/hostile $\to +1$: warm/affectionate)
3. $z_3$: **Dominance / Agency** ($-1$: passive/yielding $\to +1$: assertive/directive)
4. $z_4$: **Communicative Intimacy** ($-1$: transactional/distant $\to +1$: deeply personal)
5. $z_5$: **Epistemic Openness** ($-1$: closed/skeptical $\to +1$: curious/receptive)
6. $z_6$: **Attentional Focus** ($-1$: distracted/fragmented $\to +1$: deeply engaged)

### 3.3 Contract 3: Downstream Phase 23 Interface ($\boldsymbol{\psi}_{\text{user}} \in \mathbb{R}^{12}$)
The continuous belief state exposes an immutable research interface to downstream components:

$$\boldsymbol{\psi}_{\text{user}}(t) = \begin{bmatrix} \boldsymbol{\mu}_{\mathbf{z}}(t) \\ \text{diag}(\boldsymbol{\Sigma}_{\mathbf{z}}(t)) \end{bmatrix} \in \mathbb{R}^{12}$$

Where:
- $\boldsymbol{\mu}_{\mathbf{z}}(t) \in [-1, 1]^6$ represents the point estimate of user belief.
- $\text{diag}(\boldsymbol{\Sigma}_{\mathbf{z}}(t)) \in (0, 1]^6$ represents the associated marginal epistemic uncertainty.

Downstream systems (dialogue policy, response generation, avatar expression drivers) consume $\boldsymbol{\psi}_{\text{user}}(t)$ without any coupling to the upstream encoder architecture.

---

## 4. Preservation of Architectural Invariants

1. **Replaceability:** Upstream observation encoders can be swapped, upgraded, or re-trained without altering the continuous ODE filter or downstream generation logic.
2. **Deterministic Fallback:** If an observation encoder fails or timeouts ($> 150\text{ ms}$), the filter executes a prior-only ODE step ($\mathbf{K}_t = 0$), preserving temporal continuity without crashing.
3. **Language Invariance:** Downstream components operate on continuous semantic coordinates, not raw language tokens, ensuring seamless operation across English, Vietnamese, and Japanese.
