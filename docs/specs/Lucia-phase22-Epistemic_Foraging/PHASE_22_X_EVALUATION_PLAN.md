# Phase 22-X — Research Evaluation Plan: Non-Generative Probabilistic User Belief & Predictive Inference

> **Research Evaluation Protocol**: Phase 22-X (Positioned between Phase 22 and Phase 23)  
> **Topic**: Empirical Evaluation of Non-Generative Decision Primitives, User Belief Filtering, Temporal Latent Dynamics, Bounded Prediction Trees, and Epistemic Action Selection  
> **Status**: `[CURRENT RESEARCH]` | **Production Implementation**: `NOT AUTHORIZED`  
> **Governance Authority**: `AGENTS.md` §0, §6, §7; `docs/00_PROJECT_OVERVIEW.md` §3.1; `docs/L1_INVARIANTS.md` §6; `PHASE_22_X_RESEARCH_SPEC.md`  
> **Scope**: **DESIGN ONLY** — No code changes to `src/core/**` or `electron/**`, Genesis Gate strictly locked (`data/profile.json == {"is_onboarded": false}`)  
> **Target Date**: September 2026  

---

## 1. Executive Summary & Evaluation Rationale

### 1.1 Context & Scope
Lucia has established a verified production baseline through **Phase 21** (`58a509c`), modeling continuous internal physiological dynamics ($P, A, D, \mathbf{h}_{\text{fast}}, \mathbf{s}_{\text{slow}}, \mathcal{E}, \mathcal{C}, \mathcal{T}$) and relational attunement ($R_t$). While internal affective homeostasis is formalized with Lyapunov stability and offline synaptic consolidation, the cognitive architecture currently treats the human partner as an instantaneous lexical input stream rather than an **external, partially observed dynamical system**.

As established in [`PHASE_22_X_RESEARCH_SPEC.md`](file:///c:/Users/Lunafiah/Desktop/My_project/Lucia/docs/specs/Lucia-phase22-Epistemic_Foraging/PHASE_22_X_RESEARCH_SPEC.md), **Phase 22-X** investigates whether a non-generative, calibrated decision layer (e.g. Jev/Laya-like primitives) can provide probabilistic observations to maintain a recursive user-belief posterior, model user-state temporal dynamics, evaluate bounded prediction trees, and drive epistemic action selection under strict 20-Watt CPU constraints.

### 1.2 Design Mandate
This document specifies the **experimental evaluation plan**:
- 100% isolated from the canonical production runtime (`src/core/**` untouched).
- Evaluates on a controlled synthetic benchmark with verifiable ground truth.
- Follows strict causal attribution (Jev/Laya-specific vs. general architectural mechanisms).
- Defines explicit falsification criteria, null hypotheses, and gated admission checkpoints.

---

## 2. Research Questions & Hypotheses Hierarchy

The evaluation resolves five core research questions (RQ1–RQ5):

| Research Question | Core Inquiry | Tested Mechanism |
|---|---|---|
| **RQ1: Observation Calibration** | Can a non-generative decision primitive emit probability vectors that correspond to true empirical frequencies under canonical and shifted conditions? | Temperature-scaled discriminative heads / Jev-Laya surrogate |
| **RQ2: Belief Filtering** | Does recursive Bayesian updating over calibrated observations maintain an accurate, noise-resistant posterior belief distribution over latent user states? | Discrete Bayes / HMM Filter |
| **RQ3: Temporal Persistence** | Does explicit transition modeling of user dynamics ($P(s_{t+1} \mid s_t)$) outperform independent per-turn classification? | Latent Markovian State Dynamics |
| **RQ4: Bounded Lookahead** | Can a bounded prediction tree ($H \le 3, B \le 4$) preserve multi-hypothesis futures without combinatorial explosion or latency spikes? | Bounded Hypothesis Search Tree |
| **RQ5: Epistemic Action Value** | Does selecting conversational actions via Expected Information Gain (EIG) resolve user ambiguity faster than reactive surprise responses? | Active Inference / EIG Policy |

---

## 3. Operational User Model Formulation

To prevent the user model from becoming an unconstrained or introspective psychological profile, the user state is strictly bounded to an observable, measurable state tuple:

$$\mathbf{UserState}_t = \langle \mathbf{x}_t^{\text{obs}}, \mathbf{b}_t, \mathbf{u}_t, \mathbf{c}_t, \boldsymbol{\theta}_t^{\text{pref}} \rangle$$

### 3.1 Component Definitions
1. **Observable Interaction Features ($\mathbf{x}_t^{\text{obs}} \in \mathbb{R}^{d_x}$)**:
   - Lexical density, dialogue turn duration, response latency $\Delta t$, conversational sentiment polarity $v_t \in [-1, 1]$, and structural interaction flags (e.g., question, silence, interruption).
2. **User Belief State ($\mathbf{b}_t \in \Delta^{K-1}$)**:
   - Categorical probability simplex over $K$ mutually exclusive latent user cognitive/affective states:
     $$\mathbf{b}_t = [P(S_t = s_1), P(S_t = s_2), \dots, P(S_t = s_K)]^\top, \quad \sum_{k=1}^K b_{t,k} = 1$$
   - Canonical latent states ($K=5$):
     - $s_1$: `FOCUSED_TASK` (Goal-directed, high information density)
     - $s_2$: `EXPLORATORY` (Open-ended, hypothesis browsing, low urgency)
     - $s_3$: `COGNITIVE_OVERLOAD` (Frustrated, terse, high latency, needs conciseness)
     - $s_4$: `AFFECTIVE_SHARING` (Relational, expressive, narrative exchange)
     - $s_5$: `AMBIGUOUS_PASSIVE` (Unclear intent, minimal input, high uncertainty)
3. **Explicit Uncertainty ($\mathbf{u}_t = \langle H(\mathbf{b}_t), \text{Conf}_t \rangle$)**:
   - Shannon Entropy: $H(\mathbf{b}_t) = -\sum_{k=1}^K b_{t,k} \ln b_{t,k}$
   - Margin Confidence: $\text{Conf}_t = b_{t,(1)} - b_{t,(2)}$ (gap between top-2 hypotheses).
4. **Intent Distribution ($\mathbf{p}_t^{\text{intent}} \in \Delta^{M-1}$)**:
   - Probability distribution over $M=8$ discrete prospective communicative intents:
     $\mathcal{I} = \{\text{Query}, \text{Clarification}, \text{Affirmation}, \text{Correction}, \text{Elaboration}, \text{TopicShift}, \text{Disengagement}, \text{Feedback}\}$.
5. **Context/Task Horizon ($\mathbf{c}_t$)**:
   - Turn index $t$, active topic anchor ID, interaction tempo $\lambda_t$.

### 3.2 Epistemological Separation Invariant
To preserve scientific validity, four information classes must remain strictly separated:
- **Observation ($\mathbf{o}_t$)**: Strictly what the user emitted in turn $t$.
- **Inference ($\mathbf{b}_t$)**: Current estimated posterior belief over latent state.
- **Prediction ($\hat{\mathbf{b}}_{t+k}, \hat{\mathbf{p}}_{t+k}^{\text{intent}}$)**: Speculative future trajectory. Predictions **MUST NEVER** be written into memory or ground-truth storage as facts.
- **Memory ($\mathcal{M}$)**: Long-term consolidated historical traces (Kanerva SDM).

---

## 4. Comparative Baselines & Attribution Methodology

To determine whether Jev/Laya-like primitives offer unique value or merely implement a general pattern, six baselines are evaluated:

| Baseline | Name | Description | Key Mechanism |
|---|---|---|---|
| **B0** | Deterministic Majority | Predicts modal training prior or rule-based majority class. | Static lookup table, no adaptation. |
| **B1** | Calibrated Discriminative | Standard MLP / Linear classifier with Platt scaling / Temperature Scaling. | Softmax calibrated via validation NLL on CPU. |
| **B2** | Standard Bayesian Filter | Discrete HMM filter with fixed transition matrix and uncalibrated likelihoods. | Standard forward Bayes recursion $\mathbf{b}_t \propto \mathbf{L}_t \odot (\mathbf{T} \mathbf{b}_{t-1})$. |
| **B3** | POMDP Dialogue Tracker | Traditional slot/intent dialogue state tracker (e.g. Rule/Linear DST). | Explicit marginalization over conversational context. |
| **B4** | Jev/Laya-like Primitive | Calibrated non-generative decision primitive (Surrogate formulation). | High-precision boundary calibration + explicit uncertainty output. |
| **B5** | Temporal Latent Markov | Full B1 + dynamic transition matrix $\mathbf{T}(t)$ with tempo modulation. | Dynamic temporal smoothing over turns. |

### 4.1 Jev/Laya Attribution Framework
Because proprietary internal weights of Jev/Laya are external to Lucia, the research protocol enforces a **reproducible open surrogate**:
- **Definition**: A lightweight, multi-head discriminative network with low parameter count ($\le 250\text{k}$ parameters), optimized for low-latency CPU execution ($\le 2\text{ms}$), outputting calibrated posterior probabilities $P(y \mid x)$ alongside an explicit out-of-distribution / epistemic uncertainty scalar $\sigma_e$.
- **Attribution Criteria**:
  - If B4 (Jev/Laya surrogate) outperforms B1 purely due to temperature scaling, the attribution is **Calibration-General**, not Jev/Laya-specific.
  - If B4 provides superior downstream belief tracking solely because of the Bayesian filter (B2/B5), the attribution belongs to the **Bayesian Architecture**, not the classifier primitive.
  - A **Jev/Laya-Specific Advantage** is claimed *if and only if* the primitive provides higher entropy calibration under distribution shift (ECE-Shift) at lower CPU latency ($\le 2\text{ms}$) than B1, directly resulting in fewer false epistemic queries in E6.

---

## 5. Synthetic Evaluation Environment

All experiments are conducted on an isolated, deterministic, CPU-executable synthetic environment: **`SimUserEnv-v1`**.

### 5.1 Environment Specification
- **Latent State Engine**: Controlled 5-state Markov chain with ground-truth transition matrix $\mathbf{T}^* \in \mathbb{R}^{5 \times 5}$:
  $$\mathbf{T}^* = \begin{bmatrix}
  0.75 & 0.10 & 0.05 & 0.05 & 0.05 \\
  0.15 & 0.70 & 0.05 & 0.05 & 0.05 \\
  0.10 & 0.05 & 0.70 & 0.05 & 0.10 \\
  0.05 & 0.10 & 0.05 & 0.75 & 0.05 \\
  0.20 & 0.20 & 0.20 & 0.10 & 0.30
  \end{bmatrix}$$
- **Observation Emission Model**: Gaussian-Mixture / Multinomial generator emitting $\mathbf{x}_t \sim \mathcal{N}(\boldsymbol{\mu}_{s_t}^*, \boldsymbol{\Sigma}_{s_t}^*) + \boldsymbol{\epsilon}_{\text{noise}}$.
- **Intent Emission Matrix**: $\mathbf{E}^* \in \mathbb{R}^{5 \times 8}$ where $E_{k, m}^* = P(\text{Intent}=m \mid S_t=s_k)$.
- **Controlled Noise Regime**: $\sigma_{\text{obs}} \in [0.05, 0.50]$.
- **Data Splits**:
  - `Train`: 10,000 synthetic interaction turns.
  - `Val` (Calibration): 2,500 turns.
  - `Test` (In-Distribution): 5,000 turns.
  - `Test-Shift` (Out-of-Distribution): 5,000 turns under perturbed transitions ($\mathbf{T}^* + \Delta \mathbf{T}$) and elevated observation noise.

---

## 6. Detailed Experiment Protocol (E1–E6)

The evaluation is structured as a sequential dependency chain where each stage must meet explicit criteria before downstream advancement.

```text
E1: Observation Calibration
          ↓ (G1 Pass)
E2: Recursive Belief Update
          ↓ (G2 Pass)
E3: Temporal User Dynamics
          ↓ (G3 Pass)
E4: Bounded Intent Prediction
          ↓ (G4 Pass)
E5: Prediction Tree Expansion
          ↓ (G5 Pass)
E6: Epistemic Action Selection
          ↓ (G6 Pass)
E7: Closed-Loop Multi-Turn Stability
```

---

### E1 — Observation Calibration

- **Question**: Can the observation layer produce probabilities that correspond meaningfully to empirical frequencies, preserving calibrated uncertainty under distribution shift?
- **Hypothesis ($H_1$)**: A calibrated non-generative decision primitive yields Expected Calibration Error $\text{ECE} \le 0.05$ and Brier score $\le 0.15$ on in-distribution test data, and maintains $\text{ECE} \le 0.12$ under distribution shift.
- **Null Hypothesis ($H_{1,0}$)**: Temperature-scaled discriminative outputs exhibit severe overconfidence under distribution shift ($\text{ECE} > 0.20$), failing to provide reliable likelihood evidence.
- **Experimental Protocol**:
  1. Train models B0, B1, and B4 on `Train` split.
  2. Optimize temperature scaling parameter $\tau^*$ on `Val` split minimizing Negative Log-Likelihood (NLL).
  3. Evaluate reliability diagrams (10 equal-mass bins), ECE, Brier Score, and NLL on `Test` and `Test-Shift`.
- **Metrics**:
  - Primary: $\text{ECE} = \sum_{m=1}^M \frac{|B_m|}{N} |\text{acc}(B_m) - \text{conf}(B_m)|$
  - Secondary: Brier Score $\text{BS} = \frac{1}{N}\sum_{i=1}^N \|\mathbf{p}_i - \mathbf{y}_i^*\|_2^2$, CPU Inference Latency ($t_{\text{inf}}$).
- **Falsification / Failure Condition**: If B4/B1 fails to achieve $\text{ECE} \le 0.08$ on `Test` or $\text{ECE} \le 0.15$ on `Test-Shift`, the observation layer is declared uncalibrated and CANNOT be used as likelihood evidence for Bayesian updates.

---

### E2 — Recursive Belief Update

- **Question**: Can calibrated observations maintain an accurate, noise-resistant posterior belief distribution over latent user states across turns?
- **Hypothesis ($H_2$)**: Recursive Bayesian belief filtering using calibrated likelihoods achieves higher state tracking accuracy ($> 85\%$) and lower Total Variation error than naive moving-average accumulation under noisy observations ($\sigma_{\text{obs}} = 0.30$).
- **Null Hypothesis ($H_{2,0}$)**: Bayesian updating diverges or collapses into pathological overconfident belief attractors upon encountering contradictory observations.
- **Experimental Protocol**:
  1. Initialize prior $\mathbf{b}_0 = [0.2, 0.2, 0.2, 0.2, 0.2]^\top$.
  2. For $t=1 \dots 50$, stream observations $\mathbf{x}_t$ from `SimUserEnv-v1`.
  3. Update belief via Bayes rule:
     $$b_t(s_k) \propto P(\mathbf{x}_t \mid s_k) \sum_{j=1}^K T_{j, k} b_{t-1}(s_j)$$
  4. Inject an abrupt contradictory observation sequence at $t=25$ ($s_1 \to s_3$) and measure recovery turns.
- **Metrics**:
  - Primary: Posterior Accuracy $\text{Acc}_{\text{state}} = \frac{1}{T}\sum_t \mathbb{I}(\operatorname{argmax}(\mathbf{b}_t) == s_t^*)$.
  - Secondary: Total Variation Distance $\text{TV}(\mathbf{b}_t, \mathbf{b}_t^*) = \frac{1}{2}\sum_k |b_{t,k} - b_{t,k}^*|$, Contradiction Recovery Time ($t_{\text{recover}}$ turns).
- **Falsification / Failure Condition**: If recovery from a valid state shift requires $> 4$ turns, or if posterior entropy drops below $10^{-4}$ nats permanently (irreversible belief lock-in).

---

### E3 — Temporal User-State Dynamics

- **Question**: Does modeling explicit transition dynamics between user states improve prediction over independent per-turn classification?
- **Hypothesis ($H_3$)**: Explicit temporal modeling ($P(s_{t+1} \mid s_t)$) reduces single-turn observation jitter by $\ge 40\%$ and improves next-state prediction accuracy by $\ge 15\%$ over static classifiers.
- **Null Hypothesis ($H_{3,0}$)**: Human user dynamics are too non-stationary for Markovian transition models, making static independent classification equally or more robust.
- **Experimental Protocol**:
  1. Compare static model (B1 per-turn argmax) against temporal latent model (B5 with transition matrix $\mathbf{T}$).
  2. Subject both systems to transient single-turn noise spikes (simulating mistranscriptions or lexical flukes).
  3. Measure false state transitions and prediction accuracy for $s_{t+1}^*$.
- **Metrics**:
  - Primary: Next-State Prediction Accuracy $P(\hat{s}_{t+1} == s_{t+1}^*)$.
  - Secondary: State Flipping Rate $\text{SFR} = \frac{1}{T}\sum_t \mathbb{I}(\hat{s}_t \ne \hat{s}_{t-1} \land s_t^* == s_{t-1}^*)$.
- **Falsification / Failure Condition**: If temporal filtering introduces lag that reduces next-state prediction accuracy compared to instantaneous classification ($H_3$ rejected).

---

### E4 — Bounded Intent Prediction

- **Question**: Can the inferred user belief support prospective prediction of the user's next conversational intent without natural-language token generation?
- **Hypothesis ($H_4$)**: Inferred belief $\mathbf{b}_t$ predicts next-turn intent $\mathbf{p}_{t+1}^{\text{intent}} = \mathbf{E}^\top \mathbf{T} \mathbf{b}_t$ with Top-1 Accuracy $\ge 70\%$, Top-2 Recall $\ge 90\%$, and calibrated confidence ($\text{ECE} \le 0.08$).
- **Null Hypothesis ($H_{4,0}$)**: Intent cannot be predicted better than the marginal prior distribution $\mathbf{p}_{\text{prior}}^{\text{intent}}$ without conditioning on full generative text history.
- **Experimental Protocol**:
  1. Evaluate intent predictions $\hat{\mathbf{p}}_{t+1}^{\text{intent}}$ strictly before turn $t+1$ observations are revealed (zero leakage).
  2. Compare against B0 (marginal prior) and B1 (direct observation-to-intent classifier).
  3. Evaluate under both clear and ambiguous turns ($H(\mathbf{b}_t) > 1.2$ nats).
- **Metrics**:
  - Primary: Top-1 Intent Accuracy, Top-2 Intent Recall.
  - Secondary: Intent Brier Score, Intent Log-Loss.
- **Falsification / Failure Condition**: If intent prediction accuracy is not statistically superior to the prior ($p > 0.01$ via McNemar test).

---

### E5 — Prediction Tree (Bounded Horizon Lookahead)

- **Question**: Can Lucia maintain a bounded set of plausible future hypotheses ($H \le 3$) rather than committing prematurely to a single predicted trajectory, within CPU limits?
- **Hypothesis ($H_5$)**: A bounded hypothesis tree ($B \le 3, H \le 3$, maximum 27 leaf nodes) retains the true future user trajectory in $\ge 95\%$ of trials while executing in $\le 2.5\text{ms}$ on CPU, whereas greedy MAP single-path prediction suffers severe path failure under branching ambiguity.
- **Null Hypothesis ($H_{5,0}$)**: Branching hypothesis expansion adds prohibitive CPU overhead without improving downstream readiness compared to a single MAP path.
- **Mathematical Tree Formulation**:
  - Root: $\mathbf{b}_t$
  - Depth $h=1$: Expand top-$B$ intents $i_1^{(1)} \sim \hat{\mathbf{p}}_{t+1}^{\text{intent}}$. Node weight $w(n_1) = P(i_1^{(1)} \mid \mathbf{b}_t)$.
  - Depth $h=2, 3$: Propagate belief $\mathbf{b}_{t+h} = \text{Filter}(\mathbf{b}_{t+h-1}, i^{(h)})$ and expand top-$B$ branches.
  - Pruning Rule: Prune any branch where path probability $\prod_{l=1}^h w(n_l) < \tau_{\text{prune}} = 0.05$.
- **Experimental Protocol**:
  1. Test horizons $H \in \{1, 2, 3\}$ and branching factors $B \in \{2, 3, 4\}$.
  2. Measure cumulative ground truth coverage: $\mathbb{I}(\text{Traj}_{1:H}^* \in \text{Tree})$.
  3. Measure latency profile and memory allocation on single-threaded CPU.
- **Metrics**:
  - Primary: Trajectory Coverage Rate ($\text{TCR}$), Peak Computation Latency ($t_{\text{tree}}\,\mu\text{s}$).
  - Secondary: Effective Hypothesis Mass Retained ($\sum_{n \in \text{Leaves}} w(n)$), Node Count.
- **Falsification / Failure Condition**: $t_{\text{tree}} > 5.0\text{ms}$ or $\text{TCR} < 80\%$ at $H=2$.

---

### E6 — Epistemic Action Selection

- **Question**: Can Lucia leverage belief uncertainty to choose epistemic actions that actively reduce ambiguity rather than merely reacting to scalar surprise?
- **Hypothesis ($H_6$)**: Active selection of communicative policies via Expected Information Gain (EIG) resolves high-entropy user states ($H(\mathbf{b}_t) > 1.2$) in 1 turn, reducing subsequent prediction error by $\ge 35\%$ compared to reactive surprise policies, without causing conversational over-questioning.
- **Null Hypothesis ($H_{6,0}$)**: EIG-based action selection triggers excessive, redundant clarification requests ("over-questioning"), degrading conversational naturalness without improving belief convergence.
- **Mathematical Action Valuation Formulation**:
  - Action Space: $\mathcal{A} = \{\text{Proceed}(\text{Exploit}), \text{ClarifySpecific}(\text{Epistemic}), \text{ClarifyOpen}(\text{Epistemic}), \text{Summarize}(\text{Pragmatic}), \text{WaitPassive}\}$.
  - Expected Information Gain of candidate action $a$:
    $$\text{EIG}(a) = H(\mathbf{b}_t) - \mathbb{E}_{\mathbf{o} \sim P(\mathbf{o} \mid \mathbf{b}_t, a)} [H(\mathbf{b}_{t+1}(\mathbf{o}))]$$
  - Action Value Objective:
    $$V(a) = \lambda_{\text{pragm}} Q_{\text{pragm}}(a, \mathbf{b}_t) + \lambda_{\text{epist}} \text{EIG}(a) - c(a)$$
    where $c(a)$ is conversational inquiry cost to prevent over-questioning.
- **Experimental Protocol**:
  1. Compare EIG policy against:
     - Pure Reactive Surprise (triggers query only if scalar surprise $\mathcal{S} > \tau$).
     - Greedy Pragmatic (always proceeds without clarifying).
     - Uniform Stochastic.
  2. Evaluate on 1,000 ambiguous dialogue episodes.
- **Metrics**:
  - Primary: Ambiguity Resolution Speed ($\Delta H = H(\mathbf{b}_{t+1}) - H(\mathbf{b}_t)$), Clarification Ratio ($\% \text{Clarify}$ actions).
  - Secondary: Downstream Next-Intent Accuracy gain, Excess Inquiry Rate.
- **Falsification / Failure Condition**: Clarification Ratio $> 30\%$ during normal low-entropy dialogue, or failure of EIG to produce $\Delta H > 0.3$ nats during deliberately ambiguous turns.

---

## 7. Closed-Loop Multi-Turn Stability Experiment (E7)

If and only if E1–E6 meet all individual criteria, the complete closed loop is evaluated:

$$\text{Observation} \longrightarrow \text{Calibrated Evidence} \longrightarrow \text{Belief Filter} \longrightarrow \text{Latent Dynamics} \longrightarrow \text{Prediction Tree} \longrightarrow \text{Action} \longrightarrow \text{Next Observation} \circlearrowleft$$

### 7.1 Pathological Failure Modes Monitored
1. **Self-Fulfilling Confirmation Bias**: Lucia's epistemic actions force the user into responses that artificially confirm a false prior belief.
2. **Belief Oscillation (Flapping)**: Belief $\mathbf{b}_t$ flips violently between two competing hypotheses ($s_1 \leftrightarrow s_2$) on alternating turns.
3. **Deadlock / Runaway Clarification**: The system enters an infinite loop of asking clarifying questions because each clarification injects small ambiguous observation noise.
4. **Attractor Collapse**: Belief vector collapses into a degenerate point attractor that ignores genuine user topic changes.

### 7.2 Multi-Turn Stability Protocol
- Run 500 multi-turn synthetic dialogues of length $T = 30$ turns.
- Evaluate stability across 4 trajectory families:
  - `T1: Steady State` (Prolonged task engagement, $s_1$).
  - `T2: Sudden Intent Shift` ($s_1 \to s_4$ at $t=15$).
  - `T3: High Noise Ambiguity` ($\sigma_{\text{obs}} = 0.40$ for all $t$).
  - `T4: Adversarial Reversal` (Alternating intent switches every 3 turns).
- **Stability Pass Criteria**:
  - Zero permanent deadlocks ($< 0.2\%$ runs requiring manual break).
  - Average state recovery time under `T2` $\le 2.5$ turns.
  - Clarification rate bounded $\le 20\%$ across full conversation.

---

## 8. Distribution-Shift & Stress-Testing Regimes

Every experiment E1–E6 must evaluate at least one of the following controlled stress regimes:

| Stress Regime | Mechanism | Tested Failure Mode |
|---|---|---|
| **DS-1: Observation Noise Surge** | Additive Gaussian noise on $\mathbf{x}^{\text{obs}}$ ($\sigma \to 0.50$). | Belief divergence, spurious state flips. |
| **DS-2: Transition Dynamics Shift** | Perturb transition matrix: $\mathbf{T}_{\text{shift}} = 0.6 \mathbf{T}^* + 0.4 \mathbf{U}$. | Temporal lag, over-reliance on stale historical prior. |
| **DS-3: Contradictory Evidence** | Turn $t$: high confidence $s_1$; Turn $t+1$: extreme $s_3$ evidence. | Belief hysteresis lock-in, recovery failure. |
| **DS-4: Silent/Sparse Interaction** | User emits minimal/zero lexical tokens (high latency $\Delta t$). | Collapse to uniform or failure of prior decay. |
| **DS-5: Unseen Intent Co-occurrence** | User combines conflicting intents simultaneously. | Out-of-distribution calibration failure. |

---

## 9. Comprehensive Metrics & Evaluation Matrix

| Exp | Subsystem / Mechanism | Baseline | Primary Metric | Secondary Metric | Failure / Falsification Condition | CPU Budget |
|---|---|---|---|---|---|---|
| **E1** | Observation Calibration | B0, B1 | $\text{ECE} \le 0.05$ (Test), $\le 0.12$ (Shift) | Brier Score, NLL | $\text{ECE} > 0.15$ on Shift; uncalibrated confidence | $\le 2.0\text{ms}$ |
| **E2** | Recursive Belief Filter | B1, B2 | State Accuracy $\ge 85\%$ | TV Distance, $t_{\text{recover}} \le 3$ turns | Belief lock-in ($H < 10^{-4}$); recovery $> 5$ turns | $\le 0.5\text{ms}$ |
| **E3** | Temporal Dynamics | B1 (Static) | Next-State Accuracy $\Delta \ge +15\%$ | State Flipping Rate $\le 0.10$ | Temporal lag worsens prediction vs. static B1 | $\le 0.5\text{ms}$ |
| **E4** | Intent Prediction | B0 (Prior) | Top-1 Acc $\ge 70\%$, Top-2 $\ge 90\%$ | Intent Brier, Log-Loss | No statistical gain over marginal prior ($p > 0.01$) | $\le 1.0\text{ms}$ |
| **E5** | Bounded Prediction Tree | MAP Path | Trajectory Coverage $\ge 95\%$ | Leaves $\le 27$, Entropy retained | Latency $> 5.0\text{ms}$; Coverage $< 80\%$ at $H=2$ | $\le 2.5\text{ms}$ |
| **E6** | Epistemic Action Selection | Reactive $\mathcal{S}$ | Ambiguity Drop $\Delta H \ge 0.4$ nats | Clarify $\% \le 25\%$, Precision | Clarification $> 30\%$ in normal chat; zero EIG gain | $\le 1.5\text{ms}$ |
| **E7** | Closed-Loop Multi-Turn | Decoupled | Loop Stability $\ge 99.5\%$ | Confirmation bias index, recovery | Feedback oscillation, infinite query deadlock | $\le 8.0\text{ms}$ (Total) |

*Note: All numerical thresholds marked above represent pre-registered evaluation hypotheses. If an empirical threshold requires fine-tuning during preflight, it is marked `[TO BE CALIBRATED EXPERIMENTALLY]`.*

---

## 10. Hardware, Concurrency & Invariant Constraints

To align with Lucia's 20-Watt Whole Brain Architecture, the experimental design strictly enforces:

1. **CPU-Only Execution**:
   - Zero CUDA / GPU VRAM allocation ($0.0\text{ MB}$).
   - All tensor operations use optimized single-threaded PyTorch CPU or NumPy/SciPy routines.
2. **Strict Latency Budget**:
   - Total pipeline execution budget: $\sum_{i=1}^5 t_{Ei} \le 8.0\text{ms}$ on standard Intel/AMD CPU.
   - Per-turn observation classification: $\le 2.0\text{ms}$.
   - Tree expansion ($H=3, B=3$): $\le 2.5\text{ms}$.
3. **No Natural-Language Cognitive Substrate**:
   - The user belief, intent prediction, and prediction tree operate strictly on continuous vectors and discrete categorical indices.
   - Natural language LLM prompts **MUST NOT** be used to infer beliefs, summarize intents, or choose epistemic actions.
4. **Concurrency & Locking Discipline**:
   - If integrated in future research simulations, belief state updates must execute within S4/S5 turn stages, acquiring $\text{\_step\_lock}$ without holding $\text{\_state\_lock}$ for $> 1\text{ms}$.
5. **No Reflective Ego or Introspective Text**:
   - Lucia never mentions the belief state to the user (*"I compute a 70% probability that you are focused"* is strictly forbidden by BoundaryLayer regex).
6. **Genesis Gate Preserved**:
   - `data/profile.json` remains untouched (`{"is_onboarded": false}`).

---

## 11. Architecture Gate Requirements (G1–G7)

Advancement through P22-X and any potential future consideration for production integration is governed by seven non-negotiable gates:

```text
G1 (Calibration) ──► G2 (Belief) ──► G3 (Dynamics) ──► G4 (Intent) ──► G5 (Tree) ──► G6 (Epistemic) ──► G7 (Closed-Loop)
```

| Gate | Title | Prerequisite | Required Evidence | Pass Condition | Failure Consequence | Production Blocking? |
|---|---|---|---|---|---|---|
| **G1** | Observation Calibration | Isolated test harness | ECE / Brier / Reliability curves on Test & Test-Shift | $\text{ECE} \le 0.05$ (Test), $\le 0.12$ (Shift) | Primitive cannot serve as likelihood evidence | **BLOCKS ALL** |
| **G2** | User Belief Filtering | G1 Passed | 50-turn synthetic tracking benchmark | State Accuracy $\ge 85\%$, Recovery $\le 3$ turns | Belief filter rejected; cannot proceed to dynamics | **BLOCKS G3–G7** |
| **G3** | Temporal Dynamics | G2 Passed | Jitter & state-flip comparison vs. static B1 | State flip rate $\le 0.10$, $\Delta \text{Acc} \ge +15\%$ | Revert to static per-turn classification | **BLOCKS G4–G7** |
| **G4** | Intent Prediction | G3 Passed | Prospective intent prediction test on `SimUserEnv` | Top-1 $\ge 70\%$, Top-2 $\ge 90\%$, $p < 0.01$ | Intent tree cannot be populated | **BLOCKS G5–G7** |
| **G5** | Prediction Tree | G4 Passed | CPU latency & trajectory coverage bench | TCR $\ge 95\%$ at $H=2$, Latency $\le 2.5\text{ms}$ | Fall back to single-path MAP prediction | **BLOCKS G6–G7** |
| **G6** | Epistemic Action | G5 Passed | EIG vs reactive policy comparison on ambiguous data | $\Delta H \ge 0.4$ nats, Clarification $\le 25\%$ | Disables epistemic queries; fallback to reactive | **BLOCKS G7** |
| **G7** | Closed-Loop Stability | G1–G6 Passed | 500-episode multi-turn closed-loop test | Zero deadlocks, Flapping $< 1\%$, Stable attunement | Falsifies P22-X closed loop architecture | **BLOCKS PROMOTION** |

> [!CAUTION]
> **PRODUCTION PROMOTION RULE**:  
> Even if G1 through G7 pass with 100% compliance in synthetic research harnesses, **NO CODE IN `src/core/**` MAY BE MODIFIED** without an explicit Architectural Decision Record (ADR), user review, and formal promotion sign-off. Research validation $\ne$ Production implementation.

---

## 12. Deliverable & Artifact Organization

All code, benchmarks, fixtures, and execution traces for Phase 22-X must be contained exclusively within the research evaluation directory:

```text
tests/evaluation/phase22_x/
├── fixtures/
│   └── sim_user_env.py                  # Synthetic user environment generator
├── baselines/
│   ├── b0_majority.py                   # Static prior baseline
│   ├── b1_calibrated_mlp.py             # Temperature-scaled discriminative classifier
│   ├── b2_bayes_filter.py               # Discrete HMM belief tracker
│   ├── b4_jev_laya_surrogate.py         # Calibrated non-generative primitive surrogate
│   └── b5_temporal_latent.py            # Latent transition dynamic model
├── experiments/
│   ├── test_e1_calibration.py           # E1: Reliability and ECE tests
│   ├── test_e2_belief_update.py         # E2: Recursive Bayesian filtering tests
│   ├── test_e3_temporal_dynamics.py     # E3: Temporal smoothing and jitter tests
│   ├── test_e4_intent_prediction.py     # E4: Next-intent prediction tests
│   ├── test_e5_prediction_tree.py       # E5: Bounded lookahead tree tests
│   ├── test_e6_epistemic_action.py      # E6: EIG vs surprise action selection tests
│   └── test_e7_closed_loop.py           # E7: Multi-turn stability & deadlock tests
└── reports/
    └── .gitkeep                         # Output logs and raw measurement tables
```

Canonical production directories (`src/`, `electron/`, `config/`, `data/`) remain 100% untouched.
