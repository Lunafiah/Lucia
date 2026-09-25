# Phase 22-XR — Research Specification: Jev/Laya Architectural Verification & Continuous User Belief Modeling

> **Research Branch Specification**: Phase 22-XR (Targeted Evolution of Phase 22-X, Pre-Phase 23)  
> **Topic**: Empirical Verification of Calibrated Non-Generative Decision Primitives (Laya/Jev), Continuous User Belief State Dynamics, and Non-Generative Intent Formulation  
> **Status**: `[CURRENT RESEARCH]` | **Production Implementation**: `STRICTLY NOT AUTHORIZED`  
> **Governance Authority**: `AGENTS.md` §0, §6, §7; `docs/00_PROJECT_OVERVIEW.md` §3.1; `docs/L1_INVARIANTS.md` §6; `docs/specs/Lucia-phase22-Epistemic_Foraging/PHASE_22_X_RESEARCH_SPEC.md`  
> **Production Code Mutations**: Exactly 0 (`src/core/**`, `electron/**`, `config/**`, and `data/**` strictly untouched)  
> **Genesis Gate**: Preserved bit-exact (`data/profile.json == {"is_onboarded": false}`)  
> **Date**: September 2026  

---

## 1. Status & Governance

Phase 22-XR is an isolated research branch established to investigate the empirical failures and structural limitations discovered during **Phase 22-X**. It operates strictly under the post-Phase-21 Research-First Governance framework:

1. **Research is Not Production (`AGENTS.md` §0):** A research hypothesis, benchmark result, or evaluation harness MUST NOT be treated as a production capability. Approval of this specification authorizes ONLY isolated simulation and benchmark experiments under `tests/evaluation/phase22_xr/` and `evaluation_artifacts/phase22_xr/`.
2. **Zero Production Mutation:** Neither `src/core/`, `electron/`, `config/`, nor `data/` may be altered in any way.
3. **Locked Genesis Gate:** First Activation (Genesis Onboarding) remains a locked future gate preserved bit-exact (`data/profile.json == {"is_onboarded": false}`).
4. **Phase 21 Baseline:** Phase 21 (Long-Term Relational Consolidation & Synaptic Homeostasis) remains the immutable canonical production baseline.
5. **Phase 22-X Research Status:** Phase 22-X remains an architecturally blocked research result (5 of 7 gates failed in canonical Run B). Phase 22-XR is an isolated branch derived from its failure analysis.
6. **Decoupling from Phase 23:** Phase 23 (Continuous Semantic State) remains independent. Phase 22-XR validates only an upstream observation-forcing interface toward Phase 23; it does not implement, mutate, or redefine Phase 23.

---

## 2. Motivation: Empirical Findings of Phase 22-X

The canonical evaluation of Phase 22-X (Run B, `task-306`) confirmed that a lightweight, non-generative discriminative primitive executing on CPU ($\le 0.72\,\mu\text{s}$) could achieve high in-distribution calibration ($\text{ECE} = 0.0149$), support rapid Bayesian recovery ($0.23$ turns), and drive disciplined epistemic action selection ($4.60\%$ clarification ratio, $0.4378$ nats entropy reduction).

However, the architecture **failed 5 of 7 pre-registered gates (G2, G3, G4, G5, G7)**. As detailed in the post-evaluation architecture analysis (`evaluation_artifacts/phase22_x/post_evaluation_architecture_analysis.md`), the failures stemmed from fundamental structural causes:

1. **Observation Representation Poverty (G1):** The surrogate B4 relied on a 6D hand-engineered feature vector that collapsed under noise surges ($\text{ECE} = 0.3077$) and lexical sparsity ($\text{ECE} = 0.5994$).
2. **Bayes Error Floor on State Tracking (G2):** Ambient feature noise set a single-turn state discriminability ceiling at $77.38\%$.
3. **Stationary Markov Dynamics (G3):** A 1st-order transition matrix $\mathbf{T}^* \in \mathbb{R}^{5 \times 5}$ could not predict prospective trajectory shifts ($+2.96\%$ gain over prior).
4. **Ill-Posed Prospective Intent Prediction (G4):** Forcing intent to be predicted *strictly prior* to user utterance yielded only $34.15\%$ Top-1 accuracy (near the $32.15\%$ static prior).
5. **Discrete Prediction-Tree Dispersion (G5):** In a discrete 8-intent space, 2-step branching collapsed coverage to $30.0\%$ ($H=2$) and $6.5\%$ ($H=3$).
6. **Belief Flapping (G7):** Recursive Bayesian updating over discrete argmax states near ambiguous decision hyperplanes caused severe temporal oscillation ($23.80\%$ flapping rate).

> [!CAUTION]
> **THE B4 SURROGATE BOUNDARY**:  
> Baseline B4 was an isolated, 2,753-parameter MLP surrogate. **B4 WAS NOT LAYA OR JEV.**  
> Phase 22-XR investigates whether actual Laya (ModernBERT-large 421M / mmBERT-base 322M) resolves observation representation poverty, and whether a **continuous dynamical user belief formulation** resolves discrete flapping and tree dispersion.

---

## 3. Relationship to P22-X and P23

The cognitive architecture treats these phases as distinct evolutionary milestones:

```text
┌────────────────────────────────────────────────────────────────────────┐
│ Phase 22-X (Completed Benchmark Baseline)                              │
│ • Discrete 5-state categorical simplex: b_t ∈ Δ⁴                       │
│ • 1st-order stationary Markov transition: T* ∈ R⁵ˣ⁵                    │
│ • Prospective discrete intent prediction: P(intent_{t+1})              │
│ • Explicit discrete prediction trees (B=3, H=2,3)                      │
│ • Finding: Discrete pipeline decomposed pathologically (Flapping 23.8%)│
└───────────────────────────────────┬────────────────────────────────────┘
                                    │ Evolution (Failure Analysis)
                                    ▼
┌────────────────────────────────────────────────────────────────────────┐
│ Phase 22-XR (Current Research Specification)                           │
│ • Real Laya verification (ModernBERT/mmBERT backbones)                 │
│ • Calibrated likelihood field: p_t ∈ [0, 1]^M over psychological probes│
│ • Continuous User Belief Dynamics: z_user(t) ∈ R⁶ (Bucy-Kalman / ODE)  │
│ • Non-generative post-observation intent interpretation: P(intent_t|u_t│
│ • Continuous density prediction replacing discrete trees               │
│ • Epistemic Action Selection (EIG) over continuous uncertainty         │
└───────────────────────────────────┬────────────────────────────────────┘
                                    │ Provisional Interface Horizon
                                    ▼
┌────────────────────────────────────────────────────────────────────────┐
│ Phase 23 (Continuous Semantic State)                                   │
│ • Language-independent continuous semantic state manifold              │
│ • Non-token conceptual dynamics & relational vector fields             │
│ • Strictly decoupled from Laya; XR provides observation forcing only   │
└────────────────────────────────────────────────────────────────────────┘
```

---

## 4. Central Research Question

Phase 22-XR is organized around this foundational question:

> **"Can a real non-generative decision system such as Laya/Jev provide a useful calibrated observation / decision interface that, when coupled to a continuous uncertainty-aware user-state model, enables Lucia to infer, maintain, and forecast latent user interaction state without making language generation or discrete intent trees the cognitive substrate?"**

This specification does **NOT** assume the answer is yes. The research protocol is designed specifically to test and potentially falsify each link of this chain.

---

## 5. Architectural Decomposition & Information Boundaries

To prevent conceptual conflation, Phase 22-XR strictly separates the system into distinct operational layers:

```text
Observed interaction (u_t, Δt, audio features)
        ↓
Laya/Jev observation / decision primitive
        ↓
Calibrated evidence / likelihood field (p_t ∈ [0, 1]^M, R_t)
        ↓
Continuous user belief state (z_user(t) ∈ R^6, P_t)
        ↓
Temporal state dynamics (ODE drift / covariance propagation)
        ↓
Future-state / trajectory density (p(z_{t+k} | z_t))
        ↓
Epistemic action selection (EIG over covariance)
        ↓
Semantic-state interface (ψ_user(t) ∈ R^12)
        ↓
Phase 23 (Continuous Semantic State Manifold)
```

### Information Boundaries & Invariants

| Category | Mathematical Space | Update Cadence | Storage Rule | Invariant Rule |
|---|---|---|---|---|
| **Observation ($\mathbf{o}_t$)** | Unstructured text, audio features, timing $\Delta t$ | Episodic per turn | Transient / Chat log | Ground truth of what the user emitted. |
| **Evidence / Likelihood ($\mathbf{p}_t$)** | Probability simplex $\Delta^{k-1}$ or hypercube $[0, 1]^M$ | Instantaneous forward pass | Transient | Calibrated conditional probabilities emitted by Laya. |
| **Inference / Belief ($\mathbf{z}_{\text{user}}(t)$)** | Continuous manifold $\mathbb{R}^6$ or bounded hypercube | Continuous time $\dot{\mathbf{z}} = f(\mathbf{z}, t)$ | Active session state | Lucia's internal estimate of user interaction state. |
| **Prediction ($\hat{\mathbf{z}}_{t+k}$)** | Density distribution over $\mathbb{R}^6$ | Prospective lookahead | Evaluated & discarded | **MUST NEVER** be stored in memory or treated as facts. |
| **Memory ($\mathcal{M}$)** | Sparse distributed representations | Offline consolidation | Permanent SDM | Historical traces; strictly separated from active state. |

> [!WARNING]
> **WHAT LAYA/JEV IS NOT**:  
> Laya/Jev is **NOT** Lucia's brain, **NOT** a user model, **NOT** a predictive engine, **NOT** an intent planner, **NOT** a language generator, and **NOT** an autonomous cognitive architecture. It is treated strictly as an **experimentally replaceable observation primitive**.

---

## 6. What We Actually Know About Laya

Based on the exhaustive reverse-engineering audit of the cloned repository `C:\Users\Lunafiah\Desktop\My_project\laya` (v0.3.20), we enforce a strict 4-way separation of knowledge:

### 6.1 Verified from Repository `[VERIFIED]`
1. **Backbone Architecture:** Bidirectional Masked Language Model encoder (`ModernBERT-large` 421M for English Latin-script, `mmBERT-base` 322M for Multilingual).
2. **Decision Head:** A 2-layer `TransformerEncoder` head on top of gathered `[MASK]` embeddings, followed by a shared linear marker scoring layer (`laya/common.py`).
3. **Execution Paradigm:** Evaluates multiple discrete questions in a **single parallel non-autoregressive forward pass** over prepended `[MASK] opt_i` tokens. Zero text tokens are generated; zero KV caches are maintained.
4. **Question Types Supported:** Exactly three typed decision formats: `choice` (categorical, $k \le 32$), `score` (ordinal integer, $k \le 10$), and `noul` (binary null verification, $k=2$). Free-form text, nested objects, and arrays are rejected by `laya/structured.py`.
5. **Training Mechanism:** Trained via RLCD (Reinforcement Learning from Calibrated Decisions) with Group Relative Policy Optimization (GRPO) directly optimizing `proper_reward` (a strictly proper scoring rule: Logarithmic + Spherical - Ranked Probability Score). Verified in source (`laya/common.py`) and passing 61/61 unit checks (`tests/test_training.py`).
6. **Calibration Implementation:** Output probabilities are scaled by post-hoc bucketed temperatures $T(qtype, k) \in [0.5, 5.0]$. Reports mode probability `answer_confidence` = $\max_i p_i$ and normalized entropy `confidence` = $1 - H(p)/\ln k$.
7. **Statelessness:** **100% memoryless**. Zero recurrent connections, zero temporal modeling, zero user belief accumulation, zero predictive transitions.
8. **Inference APIs & Routing:** Pure PyTorch `Agent`, GPU-accelerated `FastLaya` (TileLang/Triton), CPU `ONNXAgent`, dynamic script-based `Router`, and FastAPI HTTP microservice (`laya/serve.py`) exposing `POST /v1/systemone`.
9. **Hardware Footprint:** On local CPU (Ryzen 9, 8 threads), single forward pass latency is $329\,\text{ms}$ ($1.5\,\text{GB}$ RAM). On GPU (CUDA), latency is $15 - 35\,\text{ms}$ ($0.9 - 1.8\,\text{GB}$ VRAM).

### 6.2 Claimed by Upstream Authors `[CLAIMED]`
1. **RLCD Sample Efficiency:** Upstream claims RLCD matches or exceeds supervised fine-tuning accuracy with $10\times$ fewer calibration examples.
2. **Jev Wire Equivalence:** Upstream claims `POST /v1/systemone` in `laya/serve.py` is a drop-in wire-compatible replacement for TypeSafe Jev.
3. **Cross-Domain Generalization:** Upstream benchmarks report robust calibration across diverse tasks (AG News, Email Spam, Phishing, Guardrails).

### 6.3 Assumed by Lucia Research `[ASSUMED]`
1. **Observation Noise Robustness:** We hypothesize that Laya's 421M-parameter contextual representation will maintain low ECE ($\le 0.10$) under the noise surges and lexical sparsity that caused the 2,753-parameter B4 surrogate to collapse.
2. **Continuous Innovation Utility:** We hypothesize that mapping Laya's output probability simplex $\mathbf{p}_t$ into continuous innovation vectors $\mathbf{K}_t (\mathbf{p}_t - \mathbf{g}(\mathbf{z}_t))$ will accurately track latent user interaction states.
3. **Probe Sufficiency:** We hypothesize that a fixed bank of $M=6$ psychological probes is sufficient to span the relevant user interaction manifold.

### 6.4 Unknown / Unverified `[UNKNOWN]`
1. **Actual Jev Weights:** Laya does **not** contain or share TypeSafe Jev weights. Performance differences between Laya and proprietary Jev remain unknown.
2. **Behavior on Real Conversational Noise:** Laya has been evaluated on structured classification benchmarks; its calibration under conversational speech disfluencies, filler words, and rapid tone shifts has not been verified.
3. **Long-Session Memory Drift:** Because Laya is memoryless, its behavior over a 1,000-turn continuous session depends entirely on the stability of the external filtering harness.

---

## 7. Continuous User Belief Formulation

Phase 22-XR replaces the discrete 5-state categorical simplex ($\mathbf{b}_t \in \Delta^4$) with a **continuous latent user belief state**:

$$\mathbf{z}_{\text{user}}(t) \in \mathbb{R}^D \quad (D = 6)$$

> [!NOTE]
> **RESEARCH LATENT VARIABLES DISCLAIMER**:  
> The dimensions of $\mathbf{z}_{\text{user}}(t)$ represent operational research latent variables designed to parameterize interaction dynamics. **They are NOT claims of reading subjective human consciousness or actual psychological states.**

### 7.1 Latent Research Dimensions
$$\mathbf{z}_{\text{user}}(t) = \begin{bmatrix}
z_{\text{load}}(t) & \text{Estimated cognitive processing load / strain} \in [-1, 1] \\
z_{\text{agency}}(t) & \text{Goal-directed agency vs exploratory drift} \in [-1, 1] \\
z_{\text{valence}}(t) & \text{Conversational affective alignment} \in [-1, 1] \\
z_{\text{urgency}}(t) & \text{Time pressure / deadline sensitivity} \in [0, 1] \\
z_{\text{receptive}}(t) & \text{Openness to epistemic clarification} \in [0, 1] \\
z_{\text{alignment}}(t) & \text{Agreement vs contradiction with Lucia} \in [-1, 1]
\end{bmatrix}$$

### 7.2 Continuous-Time Dynamical Filter (Bucy-Kalman / Neural ODE)
Between turns ($t_{k-1} < t < t_k$), user belief evolves according to a continuous drift process pulling gently toward a conversational baseline attractor $\mathbf{z}_0$:
$$\frac{d\mathbf{z}_{\text{user}}(t)}{dt} = -\mathbf{\Gamma} (\mathbf{z}_{\text{user}}(t) - \mathbf{z}_0) + \mathbf{w}(t)$$
Where:
- $\mathbf{\Gamma} = \text{diag}(\gamma_1, \dots, \gamma_6)$ represents component relaxation rates (leaky integration).
- $\mathbf{w}(t) \sim \mathcal{N}(\mathbf{0}, \mathbf{Q})$ represents continuous process noise.

At turn arrival $t = t_k$, Laya emits calibrated probability observations $\mathbf{p}_k = [p_1, \dots, p_M]^\top$ over $M$ pre-registered probes. The belief state updates via continuous-discrete Kalman innovation:
$$\mathbf{z}_{\text{user}}(t_k^+) = \mathbf{z}_{\text{user}}(t_k^-) + \mathbf{K}_k \Big( \mathbf{p}_k - \mathbf{g}(\mathbf{z}_{\text{user}}(t_k^-)) \Big)$$
Where:
- $\mathbf{g}(\mathbf{z})$ is the non-linear observation forward map.
- $\mathbf{K}_k = \mathbf{P}_k^- \mathbf{H}_k^\top (\mathbf{H}_k \mathbf{P}_k^- \mathbf{H}_k^\top + \mathbf{R}_k)^{-1}$ is the Kalman gain.
- $\mathbf{R}_k = \text{diag}(\sigma_1^2, \dots, \sigma_M^2)$ is the measurement covariance, derived directly from Laya's reported `answer_confidence` and empirical calibration bounds.

---

## 8. Continuous Trajectory Density Forecasting (Replacing Discrete Trees)

Phase 22-X demonstrated that discrete prediction trees decompose pathologically due to exponential path dispersion:
```text
Categorical user state → Discrete intent → Branching prediction tree (Coverage: 30% at H=2, 6.5% at H=3)
```

Phase 22-XR replaces discrete tree rollouts with **continuous trajectory density forecasting**:
```text
Continuous belief distribution → Temporal ODE dynamics → Future-state probability density
```

### Mathematical Formulation
At turn $t$, prospective forecasting over horizon $k \in \{1, 2, 3\}$ is evaluated via mean drift and covariance propagation:
$$\hat{\mathbf{z}}_{t+k} = \mathbf{z}_t + \int_t^{t+k} f(\mathbf{z}(\tau), \tau) d\tau$$
$$\mathbf{P}_{t+k} = \mathbf{\Phi}_k \mathbf{P}_t \mathbf{\Phi}_k^\top + \mathbf{Q}_k$$
Where $\mathbf{\Phi}_k = \exp(-\mathbf{\Gamma} \cdot k \Delta t)$ is the state transition matrix.

The output is a smooth, continuous Gaussian density:
$$p(\mathbf{z}_{t+k} \mid \mathbf{z}_t) = \mathcal{N}\left(\hat{\mathbf{z}}_{t+k}, \mathbf{P}_{t+k}\right)$$
This replaces combinatorial branch exploration with a bounded, evaluate-on-demand density ellipsoid.

---

## 9. Non-Generative Intent Formulation (Post-Observation Interpretation)

Phase 22-X failed prospective intent prediction ($34.15\%$ accuracy vs $32.15\%$ prior) because predicting fine-grained speech acts *prior to user utterance* is fundamentally ill-posed.

Phase 22-XR reformulates intent:
1. **Prospective Trajectory:** Lucia forecasts the user's **continuous state trajectory** $\hat{\mathbf{z}}_{\text{user}}(t+1)$ based on conversational context and topic momentum.
2. **Intent Interpretation:** Upon receiving utterance $u_{t+1}$, intent is classified as an observation-conditioned variable:
   $$P(\text{intent}_{t+1} \mid u_{t+1}, \hat{\mathbf{z}}_{\text{user}}(t+1)) \propto P(u_{t+1} \mid \text{intent}_{t+1}) \cdot P(\text{intent}_{t+1} \mid \hat{\mathbf{z}}_{\text{user}}(t+1))$$
This decouples cognitive state forecasting from speech-act token generation.

---

## 10. Epistemic Action Selection (EIG)

Phase 22-X proved that Expected Information Gain (EIG) is highly effective ($4.60\%$ query ratio, $0.4378$ nats entropy reduction). Phase 22-XR adapts EIG to continuous belief distributions:

$$a^* = \arg\max_{a \in \mathcal{A}} \Big( \alpha \cdot \text{EIG}(a) + (1 - \alpha) \cdot V_{\text{pragmatic}}(a) \Big)$$

Where:
$$\text{EIG}(a) = \frac{1}{2} \ln |\mathbf{P}_t| - \frac{1}{2} \mathbb{E}_{\mathbf{o} \sim P(\mathbf{o} \mid a)} \left[ \ln |\mathbf{P}_{t \mid \mathbf{o}}| \right]$$
Epistemic clarification (`clarify`, `probe`, `reflect`) is triggered *only* when total belief covariance $|\mathbf{P}_t|$ exceeds an ambiguity threshold $\tau_{\text{amb}}$, preventing communicative over-questioning.

---

## 11. Candidate Architectures & Ablation Strategy

To ensure strict causal attribution and prevent assigning credit to Laya when the gain originates from continuous filtering, eight explicit ablations are evaluated across identical seeds:

| Ablation ID | Observation Primitive | Calibration Mechanism | Belief Filter Formulation | Temporal Forecasting | Epistemic Action (EIG) | Target Hypothesis Tested |
|---|---|---|---|---|---|---|
| **A0** | None (Random Prior) | None | None | None | None | Absolute bottom baseline |
| **A1** | B4 Surrogate (2.7k MLP) | Post-hoc Temp Scaling | Discrete Categorical Bayes ($\Delta^4$) | Discrete Tree ($H=2$) | None | Replicates P22-X Run B |
| **A2** | B4 Surrogate (2.7k MLP) | Post-hoc Temp Scaling | **Continuous ODE ($\mathbb{R}^6$)** | None | None | Tests Continuous Belief without Laya |
| **A3** | **Real Laya (421M)** | Uncalibrated ($T=1.0$) | Discrete Categorical Bayes ($\Delta^4$) | Discrete Tree ($H=2$) | None | Tests Laya without calibration |
| **A4** | **Real Laya (421M)** | **Bucketed Clamped Temp** | Discrete Categorical Bayes ($\Delta^4$) | Discrete Tree ($H=2$) | None | Tests Laya Calibration on Discrete Belief |
| **A5** | Lightweight Calibrated (B1) | Post-hoc Temp Scaling | **Continuous ODE ($\mathbb{R}^6$)** | **Continuous Density** | None | Tests Continuous Pipeline with cheap model |
| **A6** | **Real Laya (421M)** | **Bucketed Clamped Temp** | **Continuous ODE ($\mathbb{R}^6$)** | **Continuous Density** | None | Tests Full Proposed Architecture (Passive) |
| **A7** | **Real Laya (421M)** | **Bucketed Clamped Temp** | **Continuous ODE ($\mathbb{R}^6$)** | **Continuous Density** | **Active EIG Policy** | **Full Proposed Architecture (Closed-Loop)**|

### Causal Attribution Decision Logic
1. **If A2 $\approx$ A6:** Continuous belief dynamics—not Laya—drives the improvement. Laya is not necessary.
2. **If A6 $\gg$ A2:** Laya's deep bidirectional semantic representation is essential to overcome observation noise.
3. **If A5 $\approx$ A6:** A lightweight CPU-friendly classifier is sufficient; Laya can be dropped to save CPU/memory.
4. **If A4 $\gg$ A3:** Strict proper scoring calibration is causally responsible for downstream stability.

---

## 12. Resource Constraints & Execution Budgets

Phase 22-XR enforces strict execution budgets matching Lucia's 20-Watt Whole Brain Architecture:

- **CPU Latency SLA:** Per-turn observation forward pass must complete within $\le 350\,\text{ms}$ on standard desktop CPU (Ryzen 9, 8 threads).
- **GPU Latency SLA:** When CUDA is available, forward pass must complete within $\le 50\,\text{ms}$.
- **Core Cognitive Loop Isolation:** Zero GPU VRAM impact on core LLM/generation pipelines ($\le 2.0\,\text{GB}$ dedicated or resident in CPU RAM).
- **Filtering Overhead:** Continuous Bucy-Kalman update step must complete within $\le 0.5\,\text{ms}$ on CPU.

---

## 13. Failure Modes & Taxonomy

| Failure Mode | Trigger Mechanism | Observable Symptom | Measurement Metric | Falsification / Safety Action |
|---|---|---|---|---|
| **FM-1: Belief Inertia / Lock-in** | Kalman gain $\mathbf{K}_k \to 0$ or covariance collapse | Model fails to adapt when user contradicts prior state | Recovery turns after contradiction $> 2.0$ | Inject covariance floor $\mathbf{Q}_{\text{min}} > 0$ |
| **FM-2: Over-Smoothing / Under-Reactivity** | Leaky decay $\mathbf{\Gamma}$ too aggressive | Rapid user mood/intent shifts are smoothed away | Next-turn prediction latency $> 3$ turns | Tune timescale separation; alert on lag |
| **FM-3: OOD Calibration Drift** | Zero-shot transfer to novel conversational domain | Laya outputs high confidence on erroneous observations | Out-of-domain ECE $> 0.15$ | Dynamic temperature refit; fallback to uniform |
| **FM-4: Confirmation Inquiry Loops** | EIG policy repeatedly queries ambiguous state | Conversation locks into repetitive clarifying loops | Clarification ratio $> 20.0\%$ | Hard cap on epistemic query frequency |
| **FM-5: Discrete Projection Artifacts** | Converting continuous $\mathbf{z}$ back to discrete decisions | Jitter on boundary hyperplanes | Flapping rate $> 10.0\%$ | Enforce hysteresis margins on discrete readouts |
| **FM-6: Prediction Contamination** | Speculative trajectory $\hat{\mathbf{z}}_{t+k}$ leaks into memory | Lucia remembers imagined user actions as real history | Memory trace audit detects ungrounded events | Strict read-only isolation of predictive buffers |
| **FM-7: Computational SLA Breach** | Forward passes exceed hardware time limits | CPU latency exceeds $350\,\text{ms}$ or blocks event loop | Per-turn latency $t_{\text{turn}}$ | Fallback to lightweight calibrated baseline (B1) |

---

## 14. Architecture Gates & Threshold Discipline

Phase 22-XR establishes six strict, pre-registered architecture gates.

### Threshold Rationale Classification
1. **Gate XR-1 (ECE $\le 0.10$):** Inherited from P22-X. Engineering constraint to ensure measurement covariance $\mathbf{R}_k$ reflects true likelihood errors.
2. **Gate XR-2 ($R^2 \ge 0.85$):** Inherited from P22-X (G2 was $75\%$). Raised to $85\%$ because continuous filtering incorporates temporal smoothing.
3. **Gate XR-3 (Flapping $\le 9.5\%$):** Represents a $60\%$ reduction from P22-X's failed baseline ($23.80\%$). Core research hypothesis threshold.
4. **Gate XR-4 (Coverage $\ge 75\%$ at $H=2$):** Replaces P22-X discrete tree failure ($30.0\%$). Engineering usability threshold for prospective anticipation.
5. **Gate XR-5 (Recovery $\le 1.0$ turns):** Inherited from P22-X (B4 achieved $0.23$ turns). Ensures inertial filtering does not cause lock-in.
6. **Gate XR-6 (Latency $\le 350\text{ms}$ CPU, $\le 50\text{ms}$ GPU):** Practical runtime SLA to prevent blocking Lucia's conversational turn loop.

| Gate ID | Target Metric | Required Gate Threshold | Falsification Threshold | Action if Failed |
|---|---|---|---|---|
| **Gate XR-1** | $\text{ECE}_{\text{shift}}$ (Observation Calibration) | $\le 0.10$ | $> 0.15$ | Reject Laya as observation primitive; evaluate alternative calibrated heads. |
| **Gate XR-2** | Continuous Tracking Accuracy ($R^2$) | $\ge 0.85$ (MSE $\le 0.08$) | $< 0.70$ | Re-tune observation map $\mathbf{g}(\mathbf{z})$ or increase state dimensionality. |
| **Gate XR-3** | Closed-Loop Flapping Rate | $\le 9.5\%$ (60% drop from P22-X) | $> 15.0\%$ | Increase boundary inertia $\mathbf{\Gamma}$ or add hysteresis band. |
| **Gate XR-4** | Trajectory Density Coverage ($H=2$) | $\ge 75.0\%$ | $< 50.0\%$ | Expand covariance growth rate $\mathbf{Q}$ or switch to mixture density. |
| **Gate XR-5** | Contradiction Recovery Turns | $\le 1.0\text{ turns}$ | $> 2.0\text{ turns}$ | Inject covariance floor $\mathbf{P}_{\text{min}}$ to prevent filter lock-in. |
| **Gate XR-6** | Execution Latency | GPU $\le 50\text{ms}$, CPU $\le 350\text{ms}$ | CPU $> 500\text{ms}$ | Reject ModernBERT on CPU; mandate GPU or ONNX quantization. |

---

## 15. Falsification Criteria

The evaluation protocol explicitly defines seven falsification boundaries:

1. **Reject Laya:** If Laya fails Gate XR-1 ($\text{ECE}_{\text{shift}} > 0.15$) or Gate XR-6 (CPU latency $> 500\,\text{ms}$), Laya is rejected as an observation primitive.
2. **Reject Discrete Belief Formulation:** If discrete Bayesian filters consistently exhibit flapping $> 15.0\%$ across all observation primitives (A1, A3, A4), the discrete formulation is permanently abandoned.
3. **Reject Continuous Belief Formulation:** If the continuous Bucy-Kalman filter fails Gate XR-2 ($R^2 < 0.70$) or Gate XR-5 (recovery $> 2.0$ turns), the continuous formulation is rejected.
4. **Reject Trajectory Density Forecasting:** If continuous density forecasting fails Gate XR-4 (coverage $< 50.0\%$), prospective trajectory density is rejected.
5. **Reject Epistemic Action Selection (EIG):** If EIG yields a clarification ratio $> 15.0\%$ without achieving $\ge 0.25$ nats entropy reduction, active inquiry is rejected.
6. **Reject XR $\rightarrow$ P23 Interface:** If the interface vector $\boldsymbol{\psi}_{\text{user}}(t)$ exhibits unbounded growth, instability, or language dependence, the proposed interface contract is rejected.
7. **Architectural Decoupling Separation:**
   - **Case A: Laya Rejected, Continuous Belief Retained:** If Laya is rejected due to hardware SLA breach or OOD drift, but continuous belief dynamics (A5) succeed with a lightweight model, continuous user belief modeling is retained while Laya is dropped.
   - **Case B: Laya Retained as Interchangeable Primitive:** If Laya passes all gates, it is retained strictly as an interchangeable sensor primitive without granting it cognition or memory status.

---

## 16. P23 Interface Boundary

Phase 23 specifies Lucia's future language-independent continuous semantic state. Phase 22-XR establishes an explicit upstream boundary:

```text
┌──────────────────────────────────────────────┐
│ Phase 22-XR: External User Belief Dynamics   │
│ - Continuous user state z_user(t) ∈ R⁶       │
│ - Belief covariance P_t ∈ R⁶ˣ⁶               │
└──────────────────────┬───────────────────────┘
                       │
                       │ Observation Forcing Vector:
                       │ ψ_user(t) = [z_user(t), diag(P_t)] ∈ R¹²
                       ▼
┌──────────────────────────────────────────────┐
│ Phase 23: Continuous Semantic State Manifold │
│ - Relational vector field dynamics           │
│ - S6 Language-Independent Semantic Core      │
└──────────────────────────────────────────────┘
```

**Interface Invariants:**
- XR supplies an observation forcing signal $\boldsymbol{\psi}_{\text{user}}(t)$ to P23.
- XR **does NOT** define P23's internal semantic representations, coordinate charts, or topological metrics.
- Track XR-E8 is strictly an **interface validation experiment**, NOT Phase 23 implementation.
- If XR is rejected, P23 operates using alternative sensory features without architectural disruption.

---

## 17. Non-Goals

Phase 22-XR explicitly declares the following out of scope:
1. **No Psychological Sentience Claims:** The user model is an estimated interaction state, not a claim of reading human subjective consciousness.
2. **No Natural Language Generation:** Laya will not be modified to generate conversational replies.
3. **No Production Integration:** No modifications to `src/core/` cognitive pipelines or REST APIs.
4. **No Premature Redefinition of P23:** P23's continuous semantic manifold is not dictated by XR.
5. **No Cloud Dependencies:** Zero cloud APIs (OpenAI, Anthropic, ElevenLabs). 100% local execution.

---

## 18. Open Questions

1. **Optimal Probe Set:** Does the initial 6-probe bank span all salient user interaction modes, or are additional dimensions required?
2. **OOD Temperature Adaptation:** Can online temperature scaling be performed dynamically without full retraining?
3. **ONNX / Quantization Trade-offs:** Does INT8 quantization of ModernBERT preserve strict proper scoring calibration?

---
