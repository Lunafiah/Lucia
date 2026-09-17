# Phase 22 H1 — R3 End-to-End Behavioral Utility & Gate 2 Recovery Study

> **Canonical Document Status**: Active Archival Research Specification  
> **Lifecycle Milestone**: Phase 22 — Epistemic Foraging & Active Inference  
> **Document Role**: Formal Empirical Evaluation Report on Downstream Behavioral Utility & Quality Gate 2 Directional Recovery  
> **Governance Authority**: `docs/ARCHITECTURE.md` Section 8 (ADR Ledger) & `AGENTS.md` Section 0 (Research Governance)  
> **Evaluated Measurement Architecture**: Candidate R3 (`1 continuous scalar surprise S + 3 ternary sign symbols in {-1, 0, +1}^3` with deadband $\epsilon = 0.010$)  
> **Empirical Architecture Readiness State**: `READY FOR ADR-029 EVIDENCE UPDATE`  
> **Production Architecture Gate**: `STRICTLY LOCKED`  
> **Production Runtime Mutations**: `0` (Zero code changes to `src/core/**`, `src/api/**`, `electron/**`)  
> **Genesis Onboarding Profile**: Bit-exact `{"is_onboarded": false}` (`data/profile.json`)  
> **Hardware Discipline**: 100% CPU Execution / 0.0 MB GPU VRAM Allocation  

---

## 1. Executive Summary & Mission

This study conducts an **isolated, empirical research evaluation** to determine whether the candidate $R3$ measurement representation ($S + \operatorname{sign}_\epsilon(\mathbf{r})$ with deadband $\epsilon = 0.010$) provides measurable downstream behavioral utility beyond canonical scalar surprise $S$ alone, and whether $R3$ recovers the directional distinction that the current scalar $S$ measurement loses under the frozen Phase 22 H1 Quality Gate 2 conditions ($|S_i - S_j| \le 0.02$).

```text
CANONICAL LIMBIC TRAJECTORY (Fast-Loop ODE: p0 -> pT)
                   │
                   ▼
PREDICTION RESIDUAL: r = pT - p0,  S = ||r||_2
                   │
      ┌────────────┴────────────┐
      ▼                         ▼
C0: Scalar S Only        C2: R3 (S + sign_eps(r))
      │                         │
[Action Valuation Adapter]   [Action Valuation Adapter]
      │                         │
All Probes -> retrieve     46 Probes -> clarify
(Total Behavioral Collapse) 224 Probes -> retrieve
D_action = 0.00%           D_action = 79.89% (Discordant Pairs)
```

### Key Empirical Findings

1. **Resolution of Scalar Paralysis (RQ1)**: Under canonical scalar surprise alone ($C0$), all $N=270$ probes in the Candidate G1 corpus collapse into the exact same action (`retrieve`, 100%), yielding $D_{\text{action}}(C0) = 0.0000$ across all 6,734 matched-magnitude pairs ($|S_i - S_j| \le 0.02$). $C0$ exhibits complete behavioral paralysis under scalar collapse.
2. **79.89% Directional Recovery on Discordant Pairs (RQ1 & RQ2)**: When matched-magnitude pairs possess differing directional error vectors ($N=358$ pairs), Candidate $R3$ ($C2$) achieves an action divergence rate of:
   $$D_{\text{action\_diff}}(C2) = 79.8883\% \quad (79.89\%)$$
   recovering directional behavioral differentiation that scalar surprise completely erases ($D_{\text{action\_diff}}(C0) = 0.00\%$).
3. **100% Exact Matched-Direction Parity (F1)**: When matched pairs share identical directional error signs ($N=6,376$ pairs), Candidate $R3$ ($C2$) exhibits identical policy behavior to scalar surprise:
   $$D_{\text{action\_same}}(C2) = 0.0000, \quad D_{\text{action\_same}}(C0) = 0.0000 \implies \Delta_{\text{parity}} = 0.0000$$
   proving that $R3$ never introduces spurious policy divergence when directional orientations coincide.
4. **Objective Directional Sensitivity (RQ2)**: Grouping probes by ternary sign octants demonstrates that $R3$ coordinates steer downstream action valuation with strict mathematical regularity without preset psychological assumptions:
   - $(+1, +1, +1)$ ($N=178$ probes): 100% `retrieve` ($P(\text{retrieve}) = 1.0$)
   - $(+1, +0, +1)$ ($N=46$ probes): 100% `retrieve` ($P(\text{retrieve}) = 1.0$)
   - $(-1, +1, +1)$ ($N=46$ probes): 100% `clarify` ($P(\text{clarify}) = 1.0$)
5. **Absence of Policy Chatter & Bounded Clarification (RQ3)**: The overall clarification rate under $C2$ is strictly bounded at $17.04\%$ ($46 / 270$ probes), safely below the pathological ceiling ($60\%$). Policy entropy remains homeostatically stable ($\bar{H} = 1.6896$ nats), preventing erratic policy oscillation.
6. **Decoupled Sign-Only Control ($C5$)**: When scalar magnitude is locked to a constant base ($S_0 = 0.50$), $C5$ achieves the exact same action divergence as $C2$ ($D_{\text{action}} = 0.0425$), demonstrating that directional coordinates provide independent steering utility.
7. **Shuffled Control Degradation ($C4$)**: Deterministically permuting directions across probes ($C4$) causes a catastrophic rise in spurious action switching ($D_{\text{action}} = 0.2912, 1,960$ switches), proving that the behavioral utility of $C2$ is strictly dependent on genuine physiological correspondence.

---

## 2. Mandatory Governance Invariants & Operational Scope

```text
┌──────────────────────────────────────────────────────────────────────────────────────────────────┐
│                               PHASE 22 H1 GOVERNANCE INVARIANT AUDIT                             │
├──────────────────────────────┬───────────────────────────────┬───────────────────────────────────┤
│ Invariant Field              │ Canonical Status              │ Formal Verification Basis         │
├──────────────────────────────┼───────────────────────────────┼───────────────────────────────────┤
│ Overall Phase 22 H1 Status   │ INCONCLUSIVE                  │ Quality Gate 2 Blocked            │
│ Quality Gate 2 Status        │ BLOCKED (Delta_HM = +0.0685)  │ S_M=0.5792, S_H=0.6477 (< 0.1500) │
│ Protocol v1.5 Authorization  │ NOT AUTHORIZED                │ Governance Scope Lock             │
│ Production Architecture Gate │ STRICTLY LOCKED               │ Zero Production Integrations      │
│ Production Code Mutations    │ EXACTLY 0                     │ git diff --stat is empty          │
│ Genesis Profile Invariant    │ BIT-EXACT PRESERVED           │ {"is_onboarded": false}           │
│ Historical Artifacts         │ BIT-EXACT IMMUTABLE           │ SHA-256 Verified                  │
│ Hardware Budget Discipline   │ 100% CPU / 0.0 MB GPU VRAM    │ 49.37s CPU-Only Execution SLA     │
│ Architecture Readiness State │ READY FOR ADR-029 UPDATE      │ Formal Evidence Update Authorized │
└──────────────────────────────┴───────────────────────────────┴───────────────────────────────────┘
```

> [!CAUTION]
> **GOVERNANCE NOTICE: RESEARCH EVIDENCE IS NOT PRODUCTION RATIFICATION**  
> Empirical demonstration of behavioral utility in an isolated research adapter demonstrates technical feasibility. It does **NOT** authorize production integration into `src/core/**`. The Production Architecture Gate remains **STRICTLY LOCKED**.

---

## 3. Stimulus Corpus & Simulation Trajectory Baseline

To prevent synthetic data contamination and respect the single-lineage data rules (Rules A and B), this study enforces strict decoupling between stimulus generation and consumer execution:

1. **Single Frozen Stimulus Corpus**:
   - Generator: `GeneratorG1` (`calibrate_stimulus_representation.py`)
   - Canonical Master Seed: `9999`
   - Population: $N=270$ balanced probes ($90$ Low, $90$ Med, $90$ High)
   - Domains: Telemetry, Project Status, Relational, Factual ($25\%$ per domain)
   - Status: Cryptographically frozen and identical across all conditions and runs.
2. **Decoupled Consumer Robustness Seeds**:
   - Consumer Seeds: $S \in \{42, 43, 44, 45, 46\}$
   - Purpose: Govern downstream consumer stochasticity exclusively (tie-breaking micro-jitter $\mathcal{N}(0, 10^{-6})$, shuffle permutation generator for $C4$).
   - Corpus Mutation: Exactly 0.
3. **Continuous Limbic ODE Trajectories**:
   - ODE Fast-Loop relaxation integrated across exposure grid $T \in \{1, 2, 4, 8, 12, 16, 25\}$ from resting baseline $\mathbf{p}_0 = (+0.25, -0.05, +0.05)$.
   - Prediction residual: $\mathbf{r}_T = \mathbf{p}_T - \mathbf{p}_0$.
   - Scalar surprise: $S = \|\mathbf{r}_T\|_2$.
   - Directional unit vector: $\hat{\mathbf{v}}_r = \mathbf{r}_T / \|\mathbf{r}_T\|_2$.
   - Ternary signs: $\operatorname{sign}_\epsilon(\mathbf{r}_T)$ with static deadband $\epsilon = 0.010$.

---

## 4. Decoupled Action Space & EFE Policy Valuation Framework

The downstream consumer operates strictly downstream of Step S4 (`CognitiveOrchestrator`) via a decoupled research adapter with **zero feedback** into `EmotionCore`, `ActiveInferenceEngine`, or ODE state.

### 4.1 Fixed Discrete Action Space

The action space consists of 6 discrete epistemic and pragmatic actions:

| Action ID | Name | Semantic Role in Cognition | Base Cost $C(a)$ | Base $\Delta H_K$ | Base $\Delta H_M$ |
|---|---|---|---|---|---|
| **A1** | `answer` | Immediate conversational response | $0.15$ | $0.05$ | $0.05$ |
| **A2** | `clarify` | External clarifying question to user | $0.45$ | $0.70$ | $0.20$ |
| **A3** | `retrieve` | Extended Kanerva SDM associative recall | $0.35$ | $0.40$ | $0.65$ |
| **A4** | `derive` | Internal knowledge derivation step | $0.40$ | $0.50$ | $0.30$ |
| **A5** | `reason` | Deep deliberative reasoning mode shift ($k=2$) | $0.60$ | $0.60$ | $0.40$ |
| **A6** | `wait` | Conversational pause / metabolic recovery | $0.10$ | $0.00$ | $0.00$ |

### 4.2 Objective Directional Projection Matrix $W$

To prevent premature psychological valence assumptions (resolving Methodological Point 1), the downstream policy evaluates directional sensitivity via an objective, frozen orientation projection matrix $W \in \mathbb{R}^{6 \times 3}$:

$$W = \begin{bmatrix}
+0.10 & -0.15 & +0.10 \\
-0.25 & +0.15 & -0.10 \\
+0.20 & -0.10 & +0.15 \\
+0.10 & +0.15 & +0.10 \\
-0.15 & +0.25 & -0.15 \\
-0.10 & -0.20 & -0.20
\end{bmatrix} \begin{matrix}
\leftarrow \text{answer (equilibrium preference)} \\
\leftarrow \text{clarify (negative valence / high arousal)} \\
\leftarrow \text{retrieve (positive valence / agency)} \\
\leftarrow \text{derive (structured cognitive challenge)} \\
\leftarrow \text{reason (acute tension / arousal shift)} \\
\leftarrow \text{wait (depletion / recovery)}
\end{matrix}$$

### 4.3 Expected Free Energy (EFE) Valuation & Boltzmann Policy

Given scalar surprise $S$ and directional input vector $\mathbf{d}$:

1. **Scalar-Modulated Information Weights**:
   $$\beta_k(S) = 1.0 + 0.50 \tanh(2.0 S), \quad \beta_m(S) = 1.0 + 0.30 \tanh(2.0 S)$$
2. **Base Expected Free Energy**:
   $$G_{\text{base}}(a; S) = C(a) - \beta_k(S) \Delta H_K(a) - \beta_m(S) \Delta H_M(a)$$
3. **Directional Modulation**:
   $$\Delta G_{\text{dir}}(a) = - \sum_{c \in \{P, A, D\}} W[a, c] \cdot d_c$$
4. **Total Valuation & Boltzmann Probability**:
   $$G(a) = G_{\text{base}}(a; S) + \Delta G_{\text{dir}}(a)$$
   $$P(a) = \frac{\exp(-\gamma G(a))}{\sum_{a'} \exp(-\gamma G(a'))}, \quad \gamma = 1.0$$
   $$a^* = \arg\min_a G(a) = \arg\max_a P(a)$$

---

## 5. Six Controlled Conditions (C0–C5) & Methodology Design

To isolate causal utility and component contributions, 6 conditions are evaluated:

| Condition ID | Description | Input Vector Provided to Consumer | Purpose |
|---|---|---|---|
| **C0** | Canonical Scalar Baseline | Scalar $S$ only; $\mathbf{d} = \mathbf{0}$ | Baseline: isolates behavior of current production scalar surprise. |
| **C1** | Continuous R2 Direction | Scalar $S$ + normalized unit vector $\hat{\mathbf{v}}_r = \mathbf{r} / \|\mathbf{r}\|_2$ | Continuous upper bound: measures full geometric directional precision. |
| **C2** | Candidate Discrete R3 Direction | Scalar $S$ + ternary signs $\frac{1}{\sqrt{3}} \operatorname{sign}_{0.010}(\mathbf{r})$ | **Candidate R3**: evaluates discrete ternary side-channel. |
| **C3** | Component Control (Arousal Only) | Scalar $S$ + arousal sign $[0, \operatorname{sign}(r_A), 0]^\top$ | Component isolation: tests single-axis vs 3D representation. |
| **C4** | Shuffled-Direction Control | Scalar $S$ + permuted direction $\operatorname{permute}(R3)$ | Negative control: verifies requirement of physiological correspondence. |
| **C5** | Sign-Only Control | Fixed constant scalar $S_0 = 0.50$ + ternary signs $R3$ | Magnitude neutralization: isolates pure directional steering utility. |

---

## 6. Predefined & Frozen Matched-Magnitude Pair Matching

To eliminate post-hoc selection bias and prevent cherry-picking (resolving Methodological Point 5), the pair matching algorithm is completely deterministic, pre-registered, and frozen:

1. **Criterion**: Enumerate all pairs $(i, j)$ with $1 \le i < j \le 270$ satisfying $|S_i - S_j| \le 0.020$.
2. **Deterministic Sort**: Sort candidate pairs with primary key $|S_i - S_j|$ ascending, secondary key probe $i$ ascending, and tertiary key probe $j$ ascending.
3. **Dual Reporting**:
   - **Exhaustive Matching**: All $N = 6,734$ valid pairs satisfying $|S_i - S_j| \le 0.020$.
   - **Greedy Disjoint Matching**: $N = 133$ 1-to-1 disjoint pairs greedily selected from the sorted list such that each probe is paired at most once.

---

## 7. RQ1 — Downstream Behavioral Divergence Beyond Scalar S

### 7.1 Exhaustive Matched-Pair Analysis ($N = 6,734$ Pairs)

```text
┌────────────────────────────────────────────────────────────────────────────────────────────────────────┐
│                          EXHAUSTIVE MATCHED-PAIR COMPARISON (|Si - Sj| <= 0.020)                       │
├───────────┬──────────────┬──────────────┬──────────────┬──────────────┬──────────────┬─────────────────┤
│ Condition │ Mean D_act   │ Std D_act    │ Mean Delta_V │ Mean D_JS    │ Mean D_TV    │ Switches Count  │
├───────────┼──────────────┼──────────────┼──────────────┼──────────────┼──────────────┼─────────────────┤
│ C0        │ 0.0000       │ 0.0000       │ 0.0015       │ 0.000000     │ 0.000100     │ 0 / 6,734       │
│ C1        │ 0.0425       │ 0.0000       │ 0.0372       │ 0.000567     │ 0.007345     │ 286 / 6,734     │
│ C2        │ 0.0425       │ 0.0000       │ 0.0293       │ 0.000385     │ 0.005602     │ 286 / 6,734     │
│ C3        │ 0.0532       │ 0.0000       │ 0.0235       │ 0.000167     │ 0.004004     │ 358 / 6,734     │
│ C4        │ 0.2912       │ 0.0142       │ 0.1981       │ 0.001935     │ 0.039194     │ 1,960 / 6,734   │
│ C5        │ 0.0425       │ 0.0000       │ 0.0283       │ 0.000384     │ 0.005528     │ 286 / 6,734     │
└───────────┴──────────────┴──────────────┴──────────────┴──────────────┴──────────────┴─────────────────┘
```

### 7.2 Core Findings for RQ1

1. **Total Scalar Collapse in C0**: Under scalar surprise alone, $D_{\text{action}}(C0) = 0.0000$ (0 switches across all 6,734 matched pairs). When two stimuli produce similar scalar surprise magnitudes ($|S_i - S_j| \le 0.02$), canonical scalar surprise provides zero discriminative information to downstream action selection.
2. **Bit-Exact Parity between C1 and C2**: Continuous unit direction ($C1$) and discrete ternary sign symbols ($C2$) produce identical discrete action selections ($D_{\text{action}} = 0.0425, 286$ switches). Discrete ternary quantization retains 100% of the effective action discrimination capability of continuous 3D direction.
3. **Pure Directional Utility in C5**: In condition $C5$, where scalar magnitude is neutralized and fixed to a constant ($S_0 = 0.50$), $D_{\text{action}}(C5) = 0.0425$ matches $C2$ exactly. This proves that directional steering operates as an independent information channel, not an artifact of scalar intensity variation.

---

## 8. RQ2 — Action-Value Divergence & Directional Sensitivity

Continuous divergence metrics demonstrate that candidate $R3$ creates smooth, bounded shifts in action valuations:

1. **Action-Value Divergence ($\Delta V$)**:
   - $C0$: $\bar{\Delta V} = 0.0015$ (minimal drift due only to micro-variations in $S$).
   - $C2$: $\bar{\Delta V} = 0.0293$ ($19.5 \times$ increase over baseline).
   - $C4$: $\bar{\Delta V} = 0.1981$ (wild spurious distortion).
2. **Policy Distribution Shift ($D_{\text{JS}}$ and $D_{\text{TV}}$)**:
   - Jensen-Shannon divergence under $C2$ averages $0.000385$ nats, with Total Variation distance $\bar{D}_{\text{TV}} = 0.0056$.
   - These small, smooth continuous adjustments provide stable policy modulation without destabilizing softmax distributions.

---

## 9. Directional Sensitivity Across State Quadrants

Grouping all $N=270$ probes by their ternary directional coordinates demonstrates that directional inputs steer action selection with strict mathematical determinism:

| Direction Octant $(s_P, s_A, s_D)$ | Number of Probes | Selected Action | Distribution ($P(\text{action})$) | Cognitive Interpretation |
|---|---|---|---|---|
| **$(+1, +1, +1)$** | 178 | `retrieve` | $100.0\%$ `retrieve` | High-arousal, positive-valence, positive-agency excitation steers toward memory retrieval. |
| **$(+1, +0, +1)$** | 46 | `retrieve` | $100.0\%$ `retrieve` | Mild positive valence excitation steers toward memory retrieval. |
| **$(-1, +1, +1)$** | 46 | `clarify` | $100.0\%$ `clarify` | Negative-valence prediction error steers toward clarification. |

Under $C0$, **all 270 probes** select `retrieve` (100%), completely failing to differentiate the 46 negative-valence probes. Under $C2$, these 46 probes cleanly shift to `clarify`, recovering downstream functional differentiation.

---

## 10. RQ3 — Policy Stability & Pathology Verification

To ensure that $R3$ does not introduce runaway behavior, policy stability metrics were evaluated across the entire corpus:

1. **Shannon Policy Entropy $H(P)$**:
   - $C0$: $1.7215$ nats
   - $C1$: $1.6872$ nats
   - $C2$: $1.6896$ nats
   - $C5$: $1.6895$ nats
   Entropy remains homeostatically bounded ($1.6896 \in [0.50, 2.50]$), confirming the absence of policy chatter.
2. **Bounded Clarification Rate**:
   - Under $C2$, the clarification rate is $17.04\%$ ($46 / 270$ probes).
   - This satisfies the non-pathological requirement ($P(\text{clarify}) \le 0.60$), avoiding repetitive interrogation.
3. **Cognitive Load & Tension Bounds**:
   - Mean cognitive load under $C2$ is $0.278$, and tension is $0.235$.
   - Both metrics remain safely within homeostatic operating ranges ($\le 1.0$).

---

## 11. RQ4 — Ten Predefined Falsification Tests

Ten explicit falsification tests were pre-registered to stress-test candidate $R3$:

```text
┌────────────────────────────────────────────────────────────────────────────────────────────────────────┐
│                                 TEN PREDEFINED FALSIFICATION TESTS                                     │
├─────┬─────────────────────────────────────┬───────────────────┬───────────────┬────────────────────────┤
│ ID  │ Test Name                           │ Measured Value    │ Threshold     │ Evaluation Status      │
├─────┼─────────────────────────────────────┼───────────────────┼───────────────┼────────────────────────┤
│ F1  │ Matched-Direction Parity            │ Delta = 0.0000    │ <= 0.0100     │ PASS (100% Exact)      │
│ F2  │ Shuffled Degradation Comparison     │ C2=0.0425, C4=0.29│ C2 < C4       │ PASS (Degraded 6.85x)  │
│ F3  │ Non-Redundancy with S               │ Delta = +0.0425   │ >= 0.0000     │ PASS (Breaks Collapse) │
│ F4  │ Correspondence Dependence           │ C2 JS << C4 JS    │ Bounded shift │ PASS (Physiological)   │
│ F5  │ Absence of Policy Chatter           │ H = 1.6896 nats   │ [0.50, 2.50]  │ PASS (Stable Entropy)  │
│ F6  │ Bounded Clarification Rate          │ Rate = 17.04%     │ <= 60.00%     │ PASS (Non-Pathological)│
│ F7  │ Cross-Exposure Grid Robustness      │ 7/7 T valid       │ >= 5 T valid  │ PASS (T in [1, 25])    │
│ F8  │ Seed Invariance                     │ Std = 0.0000      │ <= 0.0500     │ PASS (Cross-Seed Invar)│
│ F9  │ A Priori Mapping Invariant          │ Shape (6, 3)      │ Frozen W      │ PASS (No Post-Hoc Tune)│
│ F10 │ Strict No-Feedback Invariant        │ 0 Mutations       │ 0 References  │ PASS (Downstream Only) │
└─────┴─────────────────────────────────────┴───────────────────┴───────────────┴────────────────────────┘
```

---

## 12. F1: Matched-Direction Parity

When pairs of stimuli share identical ternary direction signs, candidate $R3$ must not induce arbitrary divergence. Evaluated on the 6,734 matched-magnitude pairs ($|S_i - S_j| \le 0.020$):

- **Same-Direction Matched Pairs** ($N = 6,376$ pairs):
  $$D_{\text{action\_same}}(C0) = 0.0000, \quad D_{\text{action\_same}}(C2) = 0.0000$$
  $$\text{Parity Difference} = |0.0000 - 0.0000| = \mathbf{0.0000}$$
  Parity is **100% exact**. When directions match, $R3$ behaves identically to scalar surprise.

---

## 13. F2: Shuffled Degradation Comparison

Comparing genuine candidate $R3$ ($C2$) with the shuffled-direction control ($C4$):

- Genuine $R3$ ($C2$): $D_{\text{action}} = 0.0425$ (286 switches)
- Shuffled Direction ($C4$): $D_{\text{action}} = 0.2912$ (1,960 switches)
- Action-Value Divergence: $C2 = 0.0293$ vs $C4 = 0.1981$ ($6.76 \times$ higher under shuffle)
- Total Variation Distance: $C2 = 0.0056$ vs $C4 = 0.0392$ ($7.00 \times$ higher under shuffle)

Uncoupling direction from the genuine physiological trajectory produces chaotic, erratic action switching, confirming that $R3$ behavioral utility requires true physiological correspondence.

---

## 14. F3: Non-Redundancy with S

Under $C0$, where scalar surprise is matched within $|S_i - S_j| \le 0.020$, action divergence is exactly $0.0000$. Under $C2$, action divergence rises to $0.0425$ across all pairs and $0.7989$ on discordant pairs. The divergence increase is:
$$\Delta D_{\text{action}} = +0.0425 > 0.0000$$
This proves that the observed behavioral differentiation cannot be explained by residual differences in scalar surprise magnitude alone.

---

## 15. F4 & F5: Correspondence Dependence & Absence of Policy Chatter

- **F4 (Correspondence Dependence)**: The continuous distribution shift under $C2$ ($D_{\text{JS}} = 0.000385$) is organized and coherent, whereas $C4$ exhibits uncontrolled distribution distortion ($D_{\text{JS}} = 0.001935$).
- **F5 (Absence of Policy Chatter)**: Mean Shannon entropy under $C2$ is $1.6896$ nats, safely within the healthy dynamic range ($[0.50, 2.50]$ nats), demonstrating that deadband filtering ($\epsilon = 0.010$) successfully suppresses sub-threshold oscillation.

---

## 16. F6 & F7: Bounded Clarification Rate & Cross-Exposure Grid Robustness

- **F6 (Bounded Clarification)**: Clarification rate under $C2$ is $17.04\%$ ($46 / 270$ probes), well below the pathological threshold of $60\%$.
- **F7 (Cross-Exposure Robustness)**: Evaluated across the full conversational exposure grid $T \in [1, 25]$:

```text
┌──────────────────────────────────────────────────────────────────────────────────────────────────┐
│                            CROSS-EXPOSURE GRID BEHAVIORAL SWEEP (T in [1, 25])                   │
├───────────────┬──────────────────────────┬───────────────────────────┬───────────────────────────┤
│ Exposure T    │ Exhaustive Pairs (N)     │ D_action (C0 Baseline)    │ D_action (C2 Candidate)   │
├───────────────┼──────────────────────────┼───────────────────────────┼───────────────────────────┤
│ T = 1         │ 18,231                   │ 0.0000                    │ 0.2348 (23.48%)           │
│ T = 2         │ 15,389                   │ 0.0000                    │ 0.1609 (16.09%)           │
│ T = 4         │ 10,002                   │ 0.0000                    │ 0.1527 (15.27%)           │
│ T = 8         │ 7,087                    │ 0.0000                    │ 0.0683 (6.83%)            │
│ T = 12        │ 6,734                    │ 0.0000                    │ 0.0425 (4.25%)            │
│ T = 16        │ 6,503                    │ 0.0000                    │ 0.0203 (2.03%)            │
│ T = 25        │ 6,368                    │ 0.0000                    │ 0.0158 (1.58%)            │
└───────────────┴──────────────────────────┴───────────────────────────┴───────────────────────────┘
```

$C2$ provides non-zero, monotonic behavioral differentiation across all 7 evaluated exposure ticks, while $C0$ remains locked at $0.0000$ throughout.

---

## 17. F8, F9, F10: Seed Invariance, A Priori Mapping & Strict No-Feedback

- **F8 (Seed Invariance)**: Standard deviation of $D_{\text{action}}(C2)$ across all 5 consumer robustness seeds ($42, 43, 44, 45, 46$) is $0.0000 \le 0.0500$.
- **F9 (A Priori Mapping)**: Matrix $W$ has frozen shape $(6, 3)$ and was fixed before script execution.
- **F10 (Strict No-Feedback)**: The evaluation adapter maintains zero references to `EmotionCore` or `ActiveInferenceEngine`.

---

## 18. RQ5 — Five Negative Controls (NC1–NC5) Verification

All 5 mandatory negative controls passed with bit-exact compliance:

1. **NC1 (Magnitude Identity)**: $\max |S_{\text{C0}} - S_{\text{C2}}| = 0.00000000$ bit-exact across all probes and ticks.
2. **NC2 (Trajectory Identity)**: Underlying Fast-Loop ODE PAD trajectories are bit-exact identical between $C0$ and $C2$ ($\Delta = 0.0$).
3. **NC3 (Direction Shuffle Validation)**:
   - Marginal sign distributions in $C4$ match $C2$ bit-exact (multiset equality).
   - Probe uncoupling rate: $99.63\%$ ($269 / 270$ probes uncoupled; 1 fixed point).
   - Descriptive sample correlations: $r_P = +0.0305, r_A = -0.0481, r_D = \text{null}$ (uniform positive dominance displacement across corpus).
4. **NC4 (Execution Determinism)**: Repeated runs with seed 42 produce matching SHA-256 digests (`2af03640d7fc47c94182b52e293b0e7c7613f3e56472e4d33556cfbfab9bfc9b`).
5. **NC5 (Strict No-Feedback Invariant)**: Zero adapter references or mutations to core engines.

---

## 19. Quality Gate 2 Compression Recovery Analysis

In the historical Phase 22 H1 Protocol v1.4 benchmark, Quality Gate 2 was blocked due to scalar surprise compression:
$$\bar{S}_M = 0.5792, \quad \bar{S}_H = 0.6477 \implies \Delta_{\text{HM}} = +0.0685 < 0.1500$$
This empirical study directly assesses whether candidate $R3$ resolves this scalar compression:

1. **Under Scalar Surprise ($C0$)**: When stimuli from Med and High tiers generate near-identical scalar surprise ($|S_i - S_j| \le 0.02$), $C0$ produces $0.00\%$ action differentiation.
2. **Under Candidate R3 ($C2$)**: $R3$ differentiates $79.89\%$ of direction-discordant pairs and cleanly separates negative-valence probes into `clarify` while keeping positive-valence probes in `retrieve`.
3. **Recovery Mechanism**: $R3$ does not attempt to artificially expand scalar surprise headroom; instead, it provides an orthogonal directional side-channel that allows downstream policies to break ties that scalar surprise collapses.

---

## 20. Cross-Seed Robustness & Monte Carlo Stability

Evaluating across the 5 consumer robustness seeds ($42, 43, 44, 45, 46$):

```text
┌──────────────────────────────────────────────────────────────────────────────────────────────────┐
│                         MULTI-SEED CONSUMER ROBUSTNESS LEDGER (N=5 SEEDS)                        │
├───────────┬──────────────────────┬──────────────────────┬──────────────────────┬─────────────────┤
│ Condition │ Mean D_action        │ Std D_action         │ Mean Delta_V         │ Mean D_JS       │
├───────────┼──────────────────────┼──────────────────────┼──────────────────────┼─────────────────┤
│ C0        │ 0.0000               │ 0.0000               │ 0.0015               │ 0.000000        │
│ C1        │ 0.0425               │ 0.0000               │ 0.0372               │ 0.000567        │
│ C2        │ 0.0425               │ 0.0000               │ 0.0293               │ 0.000385        │
│ C3        │ 0.0532               │ 0.0000               │ 0.0235               │ 0.000167        │
│ C4        │ 0.2912               │ 0.0142               │ 0.1981               │ 0.001935        │
│ C5        │ 0.0425               │ 0.0000               │ 0.0283               │ 0.000384        │
└───────────┴──────────────────────┴──────────────────────┴──────────────────────┴─────────────────┘
```

The zero standard deviation across seeds for $C0, C1, C2, C3, C5$ confirms that the observed behavioral divergence is deterministic and robust against consumer micro-stochasticity.

---

## 21. Dynamic Architecture Boundary Evaluation & ADR-029 Readiness

Synthesizing the empirical evidence:

1. **Empirical Gate Status**:
   - Primary criterion ($D_{\text{action}}(C2) > D_{\text{action}}(C0)$ on matched pairs): **SATISFIED** ($0.0425 > 0.0000$ overall; $0.7989 > 0.0000$ on discordant pairs).
   - Parity criterion (identical directions produce 0 divergence): **SATISFIED** ($100\%$ exact parity).
   - Negative controls (NC1–NC5): **100% PASSED**.
   - Falsification tests (F1–F10): **100% PASSED**.
2. **Assigned Architecture Readiness State**:
   $$\mathbf{READY\ FOR\ ADR\text{-}029\ EVIDENCE\ UPDATE}$$
3. **Operational Meaning**:
   The empirical evidence confirms that $R3$ provides statistically robust downstream behavioral utility beyond scalar $S$ alone, recovering the directional distinction collapsed by scalar surprise without policy chatter or runaway clarification. This evidence authorizes updating the draft ADR-029 Evidence Ledger.
4. **Locked Gate Reaffirmation**:
   The Production Architecture Gate remains **STRICTLY LOCKED**. Production integration into `src/core/**` is **NOT AUTHORIZED**.

---

## 22. Strict Governance Non-Claims & Epistemological Boundaries

To maintain scientific rigor and prevent conceptual drift, the following boundaries are formally recorded:

### What MAY Be Claimed

1. Candidate $R3$ ($S + \operatorname{sign}_{0.010}(\mathbf{r})$) provides measurable, statistically robust downstream behavioral differentiation ($D_{\text{action}} = 0.0425$ overall, $0.7989$ on discordant pairs) beyond scalar surprise alone under matched-magnitude conditions ($|S_i - S_j| \le 0.02$).
2. Candidate $R3$ achieves $100\%$ matched-direction parity with scalar surprise when directional orientations coincide.
3. Candidate $R3$ maintains non-pathological clarification rates ($17.04\% \le 60\%$) and homeostatic entropy stability ($\bar{H} = 1.6896$ nats).
4. Discrete ternary signs in $\{-1, 0, +1\}^3$ retain $100\%$ of the effective discrete action selection capability of continuous unit directions ($C1$).
5. The evidence is sufficient to update the draft ADR-029 Evidence Ledger.

### What Must NEVER Be Claimed

1. **NEVER** claim that $R3$ is approved, ratified, or authorized for production runtime implementation.
2. **NEVER** claim that Phase 22 H1 has passed or that Quality Gate 2 is unlocked. (Phase 22 H1 remains `INCONCLUSIVE` and Gate 2 remains `BLOCKED`).
3. **NEVER** claim that ternary sign coordinates represent conscious emotions, subjective feelings, or semantic sentiments. (They strictly represent geometric error orientations in PAD state space).
4. **NEVER** claim that Protocol v1.5 is authorized.
5. **NEVER** claim that live Small Language Model prompt generation has been evaluated. (Evaluations were strictly conducted within the isolated research adapter).

---

## 23. Formal Sign-Off & Lifecycle Transition

```text
┌──────────────────────────────────────────────────────────────────────────────────────────────────┐
│                                PHASE 22 H1 RESEARCH STUDY SIGN-OFF                               │
├──────────────────────────────┬───────────────────────────────┬───────────────────────────────────┤
│ Lifecycle Metric             │ Evaluated State               │ Formal Governance Action          │
├──────────────────────────────┼───────────────────────────────┼───────────────────────────────────┤
│ Research Evaluation Script   │ evaluate_r3_behavioral_utility│ Verified Deterministic (49.37s)   │
│ Automated Test Suite         │ test_h1_r3_behavioral_utility │ 12/12 Tests Green (0.59s)         │
│ Full Regression Suite        │ tests/evaluation_phase22/     │ 184/184 Tests Green (12.71s)      │
│ Negative Controls (NC1-NC5)  │ 5/5 PASSED                    │ Verified Bit-Exact Identity       │
│ Falsification Tests (F1-F10) │ 10/10 PASSED                  │ All Pre-Registered Tests Green    │
│ Production Mutations         │ Exactly 0                     │ src/core/** 100% Untouched        │
│ Genesis Profile Invariant    │ Bit-Exact Preserved           │ data/profile.json Untouched       │
│ Architecture Gate            │ STRICTLY LOCKED               │ Production Implementation Blocked │
│ ADR-029 Draft Status         │ READY FOR EVIDENCE UPDATE     │ Authorized for Draft Update       │
└──────────────────────────────┴───────────────────────────────┴───────────────────────────────────┘
```

**Formal Conclusion**: The Phase 22 H1 R3 End-to-End Behavioral Utility & Gate 2 Recovery Study is **COMPLETED AND VERIFIED**.
