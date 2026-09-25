# Failure & Root-Cause Analysis — Phase 22-X

> **Evaluation Defect & Failure Log**: Pre-registered Gates G2, G3, G4, G5, and G7  
> **Status**: Scientific Dissection of Empirical Failure Modes  

---

## 1. Inventory of Gate Failures

| Gate | Criterion Expected | Observed Value | Evaluation Status | Primary Root Cause |
|---|---|---|---|---|
| **G1 (Calibration)** | $\text{ECE} \le 0.05$ (ID), $\le 0.12$ (Shift) | $\text{ECE} = 0.0149$ (ID), $0.3077$ (DS-1) | **PARTIALLY PASSED** | Feature distribution overlap under noise |
| **G2 (Belief Tracking)** | State Accuracy $\ge 85\%$ | $77.38\%$ | **FAIL** | Single-turn observation noise ceiling |
| **G3 (Dynamics Gain)** | Flip Rate $\le 0.10$, $\Delta \text{Acc} \ge +15\%$ | Flip = $0.3266$, $\Delta \text{Acc} = +2.96\%$ | **FAIL** | Markov transition lag under non-stationarity |
| **G4 (Intent Prediction)**| Top-1 $\ge 70\%$, Top-2 $\ge 90\%$ | Top-1 = $34.15\%$, Top-2 = $52.51\%$ | **FAIL** | Prospective intent entropy / zero lookahead cues |
| **G5 (Prediction Tree)** | Coverage $\ge 95\%$ at $H=2$ | Coverage = $30.00\%$ | **FAIL** | Branching dispersion in discrete intent space |
| **G6 (Epistemic Action)**| $\Delta H \ge 0.40$ nats, Clarify $\le 25\%$ | $\Delta H = 0.4378$, Clarify = $4.60\%$ | **PASS** | Bounded action penalty prevents over-querying |
| **G7 (Closed Loop)** | Stability $\ge 99.5\%$ | $76.20\%$ (Flapping $23.80\%$) | **FAIL** | Alternating state hysteresis across turns |

---

## 2. In-Depth Root-Cause Analyses

### 2.1 Failure of Prospective Intent Prediction (G4)
- **Observed**: Prospective intent accuracy ($34.15\%$) barely beat the static prior ($32.15\%$).
- **Root Cause**: Human conversational intents in an 8-state space are weakly conditioned on broad cognitive user states. While knowing a user is `FOCUSED_TASK` biases probability towards `Query`, the user is still free to emit `Clarification`, `Correction`, or `TopicShift`. Prospective lookahead *without current lexical evidence* exhibits an information-theoretic entropy floor that cannot be bypassed by non-generative classification alone.

### 2.2 Failure of Bounded Prediction Tree Coverage (G5)
- **Observed**: Trajectory coverage collapsed from $64.0\%$ at $H=1$ to $30.0\%$ at $H=2$ and $6.5\%$ at $H=3$.
- **Root Cause**: With $M=8$ discrete intents and branching factor $B=3$, the tree covers only $3/8 = 37.5\%$ of 1-step outcomes, and $(3/8)^2 = 14.1\%$ of 2-step outcomes. Even with belief-conditioned probability weighting, path dispersion exceeds the capacity of a 3-branch discrete tree.

### 2.3 Failure of Closed-Loop Multi-Turn Stability (G7)
- **Observed**: $23.8\%$ of episodes exhibited belief flapping ($s_A \leftrightarrow s_B$).
- **Root Cause**: The recursive Bayes update lacks an explicit inertia/hysteresis band. When observations fluctuate near decision boundaries, the argmax state flips alternately on successive turns, failing the $\ge 99.5\%$ stability invariant.
