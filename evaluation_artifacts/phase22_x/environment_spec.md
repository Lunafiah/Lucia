# SimUserEnv-v1: Synthetic Environment Specification

> **Environment Designation**: `SimUserEnv-v1`  
> **Purpose**: Deterministic, reproducible, ground-truth generator for Phase 22-X evaluation.  
> **Source Module**: [`tests/evaluation/evaluation_phase22_x/sim_user_env.py`](file:///c:/Users/Lunafiah/Desktop/My_project/Lucia/tests/evaluation/evaluation_phase22_x/sim_user_env.py)  

---

## 1. Latent State Space

The environment models $K=5$ mutually exclusive latent user cognitive/affective states:
1. `FOCUSED_TASK` (Index 0): High goal-directed attention, high lexical density, low latency.
2. `EXPLORATORY` (Index 1): Hypothesis browsing, open-ended ideation, moderate duration.
3. `COGNITIVE_OVERLOAD` (Index 2): Negative sentiment polarity, high response latency, terseness.
4. `AFFECTIVE_SHARING` (Index 3): Expressive narrative, positive sentiment, high elaboration.
5. `AMBIGUOUS_PASSIVE` (Index 4): High uncertainty, sparse input, unclear intent.

---

## 2. Intent Class Space

The prospective intent space consists of $M=8$ discrete communicative intents:
`Query` (0), `Clarification` (1), `Affirmation` (2), `Correction` (3), `Elaboration` (4), `TopicShift` (5), `Disengagement` (6), `Feedback` (7).

---

## 3. Mathematical Parameters & Matrices

### 3.1 Ground-Truth Transition Matrix $\mathbf{T}^* \in \mathbb{R}^{5 \times 5}$
$$T_{j, k}^* = P(S_{t+1} = s_k \mid S_t = s_j)$$

$$\mathbf{T}^* = \begin{bmatrix}
0.75 & 0.10 & 0.05 & 0.05 & 0.05 \\
0.15 & 0.70 & 0.05 & 0.05 & 0.05 \\
0.10 & 0.05 & 0.70 & 0.05 & 0.10 \\
0.05 & 0.10 & 0.05 & 0.75 & 0.05 \\
0.20 & 0.20 & 0.20 & 0.10 & 0.30
\end{bmatrix}$$

### 3.2 Intent Emission Matrix $\mathbf{E}^* \in \mathbb{R}^{5 \times 8}$
$$E_{k, m}^* = P(\text{Intent} = m \mid S_t = s_k)$$

$$\mathbf{E}^* = \begin{bmatrix}
0.60 & 0.05 & 0.15 & 0.05 & 0.10 & 0.02 & 0.01 & 0.02 \\
0.35 & 0.10 & 0.10 & 0.05 & 0.25 & 0.10 & 0.02 & 0.03 \\
0.10 & 0.30 & 0.05 & 0.25 & 0.05 & 0.05 & 0.15 & 0.05 \\
0.10 & 0.05 & 0.25 & 0.02 & 0.35 & 0.05 & 0.03 & 0.15 \\
0.20 & 0.30 & 0.10 & 0.05 & 0.05 & 0.15 & 0.10 & 0.05
\end{bmatrix}$$

### 3.3 Observation Emission Feature Means ($\boldsymbol{\mu} \in \mathbb{R}^{5 \times 6}$)
Features: `[lexical_density, duration_norm, latency_norm, sentiment_val, question_flag, silence_flag]`
- $s_0$: $[0.85, 0.60, 0.20,  0.10, 0.80, 0.05]$
- $s_1$: $[0.55, 0.75, 0.40,  0.40, 0.60, 0.10]$
- $s_2$: $[0.25, 0.20, 0.85, -0.60, 0.30, 0.50]$
- $s_3$: $[0.70, 0.85, 0.30,  0.75, 0.40, 0.05]$
- $s_4$: $[0.30, 0.25, 0.65, -0.10, 0.50, 0.40]$

---

## 4. Distribution Shift Regimes

- **DS-1 (Noise Surge)**: Gaussian noise on continuous features increases from $\sigma=0.10 \to 0.50$.
- **DS-2 (Transition Dynamics Shift)**: Transition matrix perturbed: $\mathbf{T}_{\text{shift}} = 0.6 \mathbf{T}^* + 0.4 \mathbf{U}$.
- **DS-3 (Contradictory Evidence)**: Abrupt state shift injected at turn $t=25$ ($s_1 \to s_2$).
- **DS-4 (Silent/Sparse Input)**: Lexical density drops to 0.05, latency surges to 0.95, silence flag 0.90.
- **DS-5 (Intent Co-occurrence)**: Intent emission matrix rotated by 2 classes.
