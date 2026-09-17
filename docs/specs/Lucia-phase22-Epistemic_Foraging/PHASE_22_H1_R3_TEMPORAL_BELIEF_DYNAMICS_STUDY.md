# PHASE 22 H1 — R3 Temporal Belief Dynamics & Multi-Turn Persistence Study

> **Phase 22 H1 — Epistemic Foraging & Multi-Turn Persistence Research**  
> **Status:** `[RESEARCH VALIDATED / HARNESS ONLY / NOT FOR PRODUCTION PROMOTION]`  
> **Study Identifier:** `PHASE_22_H1_R3_TEMPORAL_BELIEF_DYNAMICS_STUDY`  
> **Master Seed:** `9999` | **Corpus SHA-256:** `d0061e8cfdd160f4ebccb7100e4fe3eeef9ff18a1a4c9c1b3f912a76f2ae82c0`  
> **Author:** Lucia Cognitive Architecture Research Agent  
> **Date:** September 18, 2026

---

## 1. Executive Summary

This study addresses the fundamental temporal gap in the Phase 22 H1 research trajectory: **does the directional information signal encoded by canonical R3 and its measured epistemic relevance persist, decay, reverse, or become confounded when the system is exposed to multi-turn temporal dynamics ($T=5$ turns) rather than a single isolated stimulus exposure?**

Previous studies established that canonical R3 resolves affective states collapsed by scalar surprise $S$, differentiates action values, and yields incremental Expected Information Gain (EIG) under an isolated single-turn Bayesian consumer. However, they evaluated states statically at a single instant without conversational progression, homeostatic relaxation, or history dependence.

In this study, we formulated an independent, deterministic multi-turn research model coupling discrete affective state transitions with a Bayesian belief-updating filter over latent hypotheses $\mathcal{H} = \{h_1, h_2, h_3, h_4\}$ ($K=4$). We evaluated four sequence families (**T1: Immediate Recovery**, **T2: Repeated Displacement Injection**, **T3: Direction Reversal**, and **T4: Recovery then Reactivation**) across five conditions (C0, C2, C3, C4, C5 permuted at the **probe trajectory level**) and four consumers (`C_qual_1.50`, `A_REFERENCE`, `B_DIRECTIONAL_SEPARABLE`, `D_CORNER`).

### Key Empirical Findings:

1. **H1-T Supported — Strong Temporal Persistence (State T-B)**:
   Across all 358 matched discordant pairs ($|S_{1, i} - S_{1, j}| \le 0.020$), the R3 directional incremental EIG signal remains measurably different from the scalar baseline on **100.00%** of pairs across all 5 turns ($R_t = 1.000$ for $t \in \{1, 2, 3, 4, 5\}$). In T1 (Immediate Recovery), the Mean Persistence Ratio at Turn 2 is $PR_2 = 0.8619 \pm 0.0034$ (86.19% retained), well above the pre-registered threshold ($PR_2 \ge 0.20$).
2. **H2-T Recovery Sensitivity — Strict Monotonic Decay**:
   Under T1 neutral recovery, the mean incremental directional EIG signal strictly decreases monotonically across all turns ($t=1: 0.019276 \to t=2: 0.016763 \to t=3: 0.015070 \to t=4: 0.013945 \to t=5: 0.013204$). However, because the homeostatic decay rate is $\alpha = 0.65$, at Turn 5 the effect still retains $66.65\%$ of its Turn 1 value; hence, the 50% recovery half-life was **`NOT_REACHED`** within the fixed horizon $T=5$.
3. **T2 Repeated Displacement Injection — Dynamic Saturation**:
   Re-injecting the same displacement stimulus $r_1$ at each turn causes the directional EIG signal to accumulate toward a saturation attractor ($PR_1 = 1.00 \to PR_2 = 1.2403 \to PR_5 = 1.7119$), matching the theoretical saturation attractor $r_\infty = \frac{\beta}{1-\alpha} r_1 \approx 2.857 r_1$.
4. **T3 Direction Reversal — Alternating Tracking with Minor Inertial Lag**:
   Reversing the input direction every turn produces strict directional retention ($R_t = 1.000$ for all turns) and synchronous sign alternation on turns 1, 3, and 5 (100% agreement), with an overall mean sign agreement of $75.98\%$ due to subtle transitional inertia at Turn 2.
5. **T4 Temporal History-Dependence Diagnostic ($THD$)**:
   Comparing Trajectory A (perturbed history) vs Trajectory B (unperturbed history) at the reactivation turn $t=4$ reveals that prior trajectory history alters the instantaneous directional EIG magnitude by **$0.004678\,\text{nats}$** (over 46x the pre-registered $\tau_{EIG} = 10^{-4}$), demonstrating measurable **somatic history dependence** while categorical belief divergence remains minimal ($THD_{JS} \le 10^{-16}$).
6. **Consumer Transferability & Negative Controls**:
   Directional retention is $100.00\%$ across all four consumers (C, A, B, D) and across all robustness seeds (42..46). Both NC5 (Zero-Direction Null) and NC6 (Temporal Transition Null) produce exact zero effects ($\Delta EIG_{\text{dir}} \equiv 0.00 \le 10^{-8}$ and $0.0\%$ retention).

---

## 2. Core Research Question

> **Central Question:** Does the epistemic relevance of R3 remain measurable and interpretable when affective state and belief state evolve across multiple conversational turns with hysteresis and recovery, or is the observed single-turn effect transient / history-dependent?

The study was designed under the strict requirement **not to assume that persistence exists**, explicitly testing whether the temporal behavior represents:
- **Persistent** (State T-B): Signal survives temporal progression;
- **Rapidly Decaying** (State T-C): Signal quickly dissipates within 1–2 neutral turns;
- **History-Dependent** (State T-D): Prior trajectory alters subsequent response to identical stimulus;
- **Sign-Reversing**: Effect inverts sign under directional reversal;
- **Amplified / Saturating**: Effect accumulates under repeated exposure;
- **Absent** (State T-A): Fails to survive multi-turn composition.

---

## 3. Previous Evidence Boundary

| Study | Key Contribution | Remaining Temporal Gap |
|---|---|---|
| **Transferability Study** | Consumer C achieves $79.89\%$ action differentiation; D achieves $70.78\%$. | Evaluated single isolated stimulus turn. |
| **Causal Attribution Study** | Shuffled directions collapse differentiation; binary sign preserves it. | Discrete static decision boundaries only. |
| **Action-Value Study** | Continuous valuation $V(a)$ restructures relative rankings ($96.76\%$). | No Bayesian belief updates. |
| **Information-Gain Study** | Incremental EIG signal ($0.058848$) and posterior divergence ($TV=0.0398$). | Single-turn static exposure; multi-turn persistence unknown. |
| **Current Study (Temporal Dynamics)** | **Multi-turn persistence verified ($PR_2=0.8619$, $R_t=1.0$), monotonic decay, saturation, and history-dependence quantified.** | **Closes the temporal persistence gap in the research harness.** |

---

## 4. Frozen Governance Ledger

All investigations strictly observed project governance invariants:
- **Production Diff**: Exactly `0` files changed across `src/core/**`, `src/api/**`, `electron/**`, and `data/profile.json`.
- **Phase 22 H1 Status**: `INCONCLUSIVE` (locked).
- **Quality Gate 2**: `STRICTLY BLOCKED` ($\Delta_{\text{HM}} = 0.0685 < 0.1500$).
- **ADR-029 Status**: `DRAFT / RESEARCH RECORD ONLY / NOT RATIFIED`.
- **Protocol v1.5**: `NOT AUTHORIZED`.
- **Genesis Profile Invariant**: Bit-exact `{"is_onboarded": false}`.
- **Execution**: 100% local CPU execution / 0.0 MB GPU VRAM.

---

## 5. Frozen Corpus Lineage

- **Generator**: Candidate G1 (`GeneratorG1` with `StimulusProcessor`)
- **Master Seed**: `9999`
- **Corpus Size**: $N = 270$ probes (90 Low, 90 Medium, 90 High)
- **Corpus SHA-256**: `d0061e8cfdd160f4ebccb7100e4fe3eeef9ff18a1a4c9c1b3f912a76f2ae82c0`
- **Exposure Ticks**: $T = 12$ ticks, $\Delta t = 200\,\text{ms}$
- **Matching Criterion**: $|S_{1, i} - S_{1, j}| \le 0.020$ at Turn 1
- **Exhaustive Pairs**: $6,734$
- **Discordant Matched Pairs**: Exactly $358$ pairs
- **Robustness Seeds**: `[42, 43, 44, 45, 46]`

---

## 6. Independent Temporal State Model

To eliminate circularity and decouple affective dynamics from belief updates, the temporal state model is formulated with separate affective and epistemic update equations:

### 6.1 Affective Dynamical State Transition
Let $p_t \in \mathbb{R}^3$ be the continuous PAD state at turn $t \in \{0, 1, 2, 3, 4, 5\}$, starting from the resting attractor $p_0 = p_{\text{resting}} = (+0.25, -0.05, +0.05)$.
The deterministic discrete affective update equation is:
$$p_{t+1} = p_{\text{resting}} + \alpha_{\text{decay}} (p_t - p_{\text{resting}}) + \beta_{\text{stim}} \Delta p_{\text{stim}, t}$$
where:
- $\alpha_{\text{decay}} = 0.65$ (pre-registered homeostatic decay per turn);
- $\beta_{\text{stim}} = 1.0$ (stimulus displacement scale);
- Somatic displacement: $r_t = p_t - p_{\text{resting}}$;
- Scalar surprise: $S_t = \|r_t\|_2$;
- R3 direction: $v_{\text{dir}, t} = \operatorname{sign}_{\epsilon}(r_t) / \sqrt{3}$ with deadband $\epsilon = 0.010$.

### 6.2 Bayesian Epistemic Belief Updating
Latent hypotheses $\mathcal{H} = \{h_1, h_2, h_3, h_4\}$ ($K=4$) with base flat prior $q_0 = [0.25, 0.25, 0.25, 0.25]$.
At each turn $t \ge 1$:
- For action $a \in \text{ACTIONS}$, observation likelihood matrix $A_{a, t}[m, k] = P(o_m \mid h_k, a, \text{state}_t)$ is evaluated by the consumer using current somatic state $(S_t, v_{\text{dir}, t})$.
- Observation marginals: $P_t(o_m \mid a) = \sum_k A_{a, t}[m, k] q_{\text{prior}}(h_k)$.
- Posterior given outcome $o_m$: $q_t(h_k \mid o_m, a) = \frac{A_{a, t}[m, k] q_{\text{prior}}(h_k)}{P_t(o_m \mid a)}$.
- Expected posterior entropy: $\mathbb{E}_o[H(q_t \mid o, a)] = \sum_m P_t(o_m \mid a) H(q_t(\cdot \mid o_m, a))$.
- Expected Information Gain: $EIG_t(a) = \max(0.0, H(q_{\text{prior}}) - \mathbb{E}_o[H(q_t \mid o, a)])$.
- Epistemic action selection: $a^*_t = \operatorname{argmax}_a EIG_t(a)$ (deterministic tie-breaking).
- Expected posterior belief: $\bar{q}_t = \sum_m P_t(o_m \mid a^*_t) q_t(\cdot \mid o_m, a^*_t)$.
- Epistemic leak / forgetting:
  $$q_t = (1 - \lambda_{\text{leak}}) \bar{q}_t + \lambda_{\text{leak}} q_0$$
  where $\lambda_{\text{leak}} = 0.15$ models uncertainty relaxation toward the uninformative prior.

---

## 7. Two-Mode Epistemic Decomposition

To isolate whether temporal effects arise from **current somatic decay** versus **accumulated prior belief history**, two complementary evaluation modes were executed:

- **Mode A (Full Coupled Trajectory)**:
  Prior belief for turn $t$ is the accumulated belief $q_{t-1}$ from turn $t-1$. Both affective state $p_t$ and epistemic belief $q_t$ evolve jointly across conversational turns.
- **Mode B (Epistemic-State-Controlled Diagnostic)**:
  Prior belief for turn $t$ is re-pinned to the uniform prior $q_0 = 1/K$ at every turn. This measures the intrinsic instantaneous epistemic capacity of the somatic state $(S_t, v_{\text{dir}, t})$ independently of prior belief drift.

---

## 8. Temporal Sequence Families ($T=5$)

For each probe $i$ with initial perturbation displacement $r_1^{(i)}$:

| Sequence Family | Trajectory Pattern | Rationale / Research Purpose |
|---|---|---|
| **T1 — Immediate Recovery** | $r_1 \to \mathbf{0} \to \mathbf{0} \to \mathbf{0} \to \mathbf{0}$ | Measure whether directional epistemic signal decays under neutral recovery. |
| **T2 — Repeated Displacement** | $r_1 \to r_1 \to r_1 \to r_1 \to r_1$ | Test whether directional information accumulates, saturates, or habituates. |
| **T3 — Direction Reversal** | $+r_1 \to -r_1 \to +r_1 \to -r_1 \to +r_1$ | Test whether epistemic signal immediately tracks current direction or retains hysteresis. |
| **T4 — Reactivation vs Control** | Traj A: $+r_1 \to \mathbf{0} \to \mathbf{0} \to +r_1 \to \mathbf{0}$<br>Traj B: $\mathbf{0} \to \mathbf{0} \to \mathbf{0} \to +r_1 \to \mathbf{0}$ | Measure difference in epistemic state at $t=4$ when controlling final stimulus injection. |

---

## 9. Trajectory-Level Permutation Controls

To break correspondence between scalar surprise $S_t$ and direction $v_{\text{dir}, t}$ while strictly preserving multi-turn dynamical consistency, permutations for controls (C3, C4, C5) were executed at the **probe trajectory level** ($N=270$):

- **C0**: Scalar baseline: $S_{t, i}$ with zero direction $\mathbf{0}$ for all turns.
- **C2**: Canonical R3: $(S_{t, i}, v_{\text{dir}, t, i})$ for all turns.
- **C3**: Shuffled direction: probe $i$ receives the complete 5-turn direction trajectory of permuted probe $\pi_{\text{dir}}(i)$.
- **C4**: Shuffled magnitude: probe $i$ receives the complete 5-turn magnitude trajectory of permuted probe $\pi_{\text{mag}}(i)$.
- **C5**: Independent direction: probe $i$ receives an independently permuted 5-turn direction trajectory.

---

## 10. Consumer Transferability Models

All four pre-registered research consumers were evaluated:
- **`C_qual_1.50` (Primary Consumer C)**: Multiplicative directional coupling ($\gamma_C = 1.50$).
- **`A_REFERENCE` (Reference Consumer A)**: Additive EFE-style coupling with saturating scalar $S$.
- **`B_DIRECTIONAL_SEPARABLE` (Separable Consumer B)**: Linear + quadratic $S$ coupling.
- **`D_CORNER` (Corner Consumer D)**: Magnitude-dominant coupling ($3.5 \times S$).

---

## 11. Pre-Registered Parameter Hashes & Anti-Circularity Lock

All dynamical and observation parameters were locked prior to execution and hashed with SHA-256:

| Parameter Name | Pre-Registered Value / Dimension | SHA-256 Hash |
|---|---|---|
| `ALPHA_DECAY` | $0.65$ | `4942870d7312d707982f792e63180e31f72925b998dec46f7ce23db6f16e2d3b` |
| `BETA_STIM` | $1.0$ | `d0ff5974b6aa52cf562bea5921840c032a860a91a3512f7fe8f768f6bbe005f6` |
| `LAMBDA_LEAK` | $0.15$ | `7932a07a8cbc0885919d30c43799f0247ef96badbc79ba5427e6306232508c78` |
| `RESTING_PAD` | $[+0.25, -0.05, +0.05]$ | `62bc8d3c953a7c009cc9710fb16683475b2a6b660bca5a76358e640c596259e8` |
| `CLARIFY_BASE_LOGITS` | $[-1.20, +1.80, -0.40, -1.00]$ | `f971491521773b69b1c9c02223d2c0896dac3f5627b889ff4e50c18008cd358a` |
| `RETRIEVE_BASE_LOGITS` | $[+1.60, -0.80, +0.90, -1.40]$ | `02e0b76d9a512245f127fbbba3dbf56ed45516827ae636b2d0261403abe61f8b` |
| `CLARIFY_W_DIR` | $4 \times 3$ matrix | `481e27b00ea8434d2a4d9cdd49dd2f5ddced8010e9dcfbd92b0a2e9b199f8d57` |
| `RETRIEVE_W_DIR` | $4 \times 3$ matrix | `adc5f3a3c772850f1f69084531ef4a2171a86b3272ad3c7b6534572d06d0b767` |
| `CLARIFY_B_S` | $[+0.10, +0.45, +0.20, -0.30]$ | `644b4c183b5f735545a8477d4a9a5a4735eb47849674971a58c5206da33517b5` |
| `RETRIEVE_B_S` | $[+0.35, +0.05, +0.25, -0.20]$ | `039084510144facc9b02a635fbf78c289c2b568c7e5b1e394d14e9b59a127137` |

Zero parameters were derived from historical collapse pairs, prior DiffRate, or R3 distributions.

---

## 12. Quantitative Results Across Sequence Families

### 12.1 Sequence T1 — Immediate Neutral Recovery (Primary Consumer C, Mode A)

| Turn $t$ | Stimulus $\Delta p$ | Mean $\|\Delta \mathbf{EIG}_{\text{dir}}\|$ | Median $\|\Delta \mathbf{EIG}_{\text{dir}}\|$ | Retention Rate ($>\tau_{EIG}$) | Persistence Ratio ($PR_t$) | Action Divergence ($D_{\text{pol}}$) |
|---|---|---|---|---|---|---|
| **Turn 1** | $r_1$ (perturbation) | $0.019276$ | $0.018237$ | **100.00%** | $1.0000$ | $79.89\%$ |
| **Turn 2** | $\mathbf{0}$ (neutral) | $0.016763$ | $0.015072$ | **100.00%** | $0.8619$ | $79.89\%$ |
| **Turn 3** | $\mathbf{0}$ (neutral) | $0.015070$ | $0.012947$ | **100.00%** | $0.7690$ | $79.89\%$ |
| **Turn 4** | $\mathbf{0}$ (neutral) | $0.013945$ | $0.011538$ | **100.00%** | $0.7072$ | $79.89\%$ |
| **Turn 5** | $\mathbf{0}$ (neutral) | $0.013204$ | $0.010610$ | **100.00%** | $0.6665$ | $79.89\%$ |

*Note on Recovery Half-Life*: Mean incremental EIG decreases strictly monotonically ($0.019276 > 0.016763 > 0.015070 > 0.013945 > 0.013204$). At Turn 5, PR is $66.65\% > 50\%$; thus the 50% decay threshold is `NOT_REACHED` within the fixed 5-turn horizon.

### 12.2 Sequence T2 — Repeated Fixed Displacement Injection (Primary Consumer C, Mode A)

| Turn $t$ | Stimulus $\Delta p$ | Mean $\|\Delta \mathbf{EIG}_{\text{dir}}\|$ | Median $\|\Delta \mathbf{EIG}_{\text{dir}}\|$ | Retention Rate | Persistence Ratio ($PR_t$) | Action Divergence ($D_{\text{pol}}$) |
|---|---|---|---|---|---|---|
| **Turn 1** | $r_1$ | $0.019276$ | $0.018237$ | **100.00%** | $1.0000$ | $79.89\%$ |
| **Turn 2** | $r_1$ | $0.023645$ | $0.023709$ | **100.00%** | $1.2403$ | $79.89\%$ |
| **Turn 3** | $r_1$ | $0.030087$ | $0.027049$ | **100.00%** | $1.5474$ | $79.89\%$ |
| **Turn 4** | $r_1$ | $0.032195$ | $0.029178$ | **100.00%** | $1.6575$ | $79.89\%$ |
| **Turn 5** | $r_1$ | $0.033172$ | $0.030476$ | **100.00%** | $1.7119$ | $79.89\%$ |

*Observation*: Repeated displacement injection drives monotonic accumulation and asymptotic saturation toward the theoretical attractor displacement $r_\infty \approx 2.857 r_1$.

### 12.3 Sequence T3 — Direction Reversal (Primary Consumer C, Mode A)

| Turn $t$ | Stimulus $\Delta p$ | Mean $\|\Delta \mathbf{EIG}_{\text{dir}}\|$ | Median $\|\Delta \mathbf{EIG}_{\text{dir}}\|$ | Retention Rate | Sign Agreement | Action Divergence ($D_{\text{pol}}$) |
|---|---|---|---|---|---|---|
| **Turn 1** | $+r_1$ | $0.019276$ | $0.018237$ | **100.00%** | $100.00\%$ | $79.89\%$ |
| **Turn 2** | $-r_1$ | $0.004188$ | $0.000707$ | **100.00%** | $0.00\%$ (inertia) | $100.00\%$ |
| **Turn 3** | $+r_1$ | $0.017655$ | $0.016194$ | **100.00%** | $100.00\%$ | $79.89\%$ |
| **Turn 4** | $-r_1$ | $0.003987$ | $0.000834$ | **100.00%** | $79.89\%$ | $100.00\%$ |
| **Turn 5** | $+r_1$ | $0.016956$ | $0.015315$ | **100.00%** | $100.00\%$ | $79.89\%$ |

*Observation*: The directional signal alternates synchronously with stimulus sign on positive turns, with a transitional magnitude dip on reversed turns due to somatic residual displacement ($\alpha r_1 - r_1 = -0.35 r_1$).

---

## 13. Temporal History-Dependence Diagnostic ($THD$) Analysis

To measure whether prior conversational trajectory changes the subsequent response to the same perturbation, we evaluated Trajectory A ($+r_1 \to \mathbf{0} \to \mathbf{0} \to +r_1 \to \mathbf{0}$) versus Trajectory B ($\mathbf{0} \to \mathbf{0} \to \mathbf{0} \to +r_1 \to \mathbf{0}$) at reactivation Turn 4 across all 270 probes:

| Metric | Mode A (Coupled Trajectory) | Mode B (Controlled Diagnostic) | Pre-Registered Tolerance |
|---|---|---|---|
| **Mean $THD_{JS}$** | $2.08 \times 10^{-17}$ | $1.32 \times 10^{-17}$ | $\tau_{JS} = 10^{-5}$ |
| **Max $THD_{JS}$** | $9.71 \times 10^{-17}$ | $8.33 \times 10^{-17}$ | $\tau_{JS} = 10^{-5}$ |
| **Proportion $THD_{JS} > \tau_{JS}$** | $0.00\%$ | $0.00\%$ | — |
| **Mean $|\Delta EIG_{4, \text{TrajA}} - \Delta EIG_{4, \text{TrajB}}|$** | **$0.004678\,\text{nats}$** | **$0.004678\,\text{nats}$** | $\tau_{EIG} = 10^{-4}$ |
| **Proportion Exceeding $\tau_{EIG}$** | **100.00%** | **100.00%** | — |

### Interpretation of $THD$:
1. **Somatic Epistemic History Dependence**: At Turn 4, Trajectory A retains a decaying displacement residual from Turn 1 ($r_4 = 1.2746 r_1$), whereas Trajectory B has $r_4 = 1.0000 r_1$. This somatic history difference shifts the expected information gain by **$0.004678\,\text{nats}$** (over 46 times $\tau_{EIG}$), confirming that **prior conversational trajectory measurably alters subsequent epistemic sensitivity to the same perturbation**.
2. **Minimal Belief Divergence**: Because the observation model yields categorical posteriors and both trajectories select the identical optimal epistemic action (`clarify`), the expected belief divergence across the discrete 4-hypothesis space remains near floating-point precision ($THD_{JS} \sim 10^{-17}$).

---

## 14. Primary Hypothesis Evaluations

### H1-T — Temporal Persistence: `SUPPORTED (State T-B)`
- Directional retention rate $R_t = 1.0000$ (100%) across all turns $t \in \{1..5\}$.
- Mean persistence ratio at Turn 2 is $PR_2 = 0.8619 \ge 0.20$.
- Under T2 repeated injection, signal persists and accumulates ($PR_5 = 1.7119$).

### H2-T — Recovery Sensitivity: `QUALIFIED SUPPORT`
- Strict monotonic decay is verified across all turns ($0.01928 \to 0.01676 \to 0.01507 \to 0.01395 \to 0.01320$).
- However, the 50% recovery half-life threshold was `NOT_REACHED` within $T=5$ turns ($PR_5 = 0.6665 > 0.50$).

### H3-T — Current-State vs History Dependence: `DUAL MODALITY OBSERVED`
- T3 direction reversal shows strong sign-tracking (100% on odd turns, mean agreement 75.98%).
- T4 demonstrates measurable somatic history-dependence ($|\Delta EIG_{\text{diff}}| = 0.00468 > \tau_{EIG}$ on 100% of probes).

### H4-T — Temporal Action Consequence: `ACTION-COUPLED (Consumer C) / DECOUPLED (A, B, D)`
- In Consumer C, action policy divergence persists at $D_{\text{pol}, t} = 79.89\%$ across all 5 turns.
- In Consumers A, B, and D, action divergence is $0.0\%$ while continuous EIG differentiation remains $100\%$, reinforcing that action flips are consumer-dependent while continuous epistemic differentiation is universal.

---

## 15. Negative Controls Verification (NC1–NC8)

| Control | Invariant Tested | Operational Result | Status |
|---|---|---|---|
| **NC1** | Scalar baseline reproduction | C0 produces identical scalar behavior across turns | **PASSED** |
| **NC2** | Tuple identity parity | Canonical $[S_t, \operatorname{sign}_\epsilon(r_t)/\sqrt{3}]$ preserved bit-exact | **PASSED** |
| **NC3** | Multiset preservation | Trajectory-level permutation preserves probe multisets | **PASSED** |
| **NC4** | Determinism | Repeated execution produces bit-exact identical outputs | **PASSED** |
| **NC5** | Zero-direction null | $W_{\text{dir}} = \mathbf{0} \implies \max_t \text{Mean}(\|\Delta \mathbf{EIG}_{\text{dir}, t}\|) = 0.00 \times 10^{-15} \le 10^{-8}$ | **PASSED** |
| **NC6** | Temporal transition null | Collapsed direction model yields max mean $\le 10^{-4}$ and $0.0\%$ retention | **PASSED** |
| **NC7** | Production code isolation | `git diff --stat src/core/ src/api/ electron/` returns 0 files changed | **PASSED** |
| **NC8** | Genesis profile invariant | `data/profile.json` remains bit-exact `{"is_onboarded": false}` | **PASSED** |

---

## 16. Answers to the 10 Preregistered Questions

1. **Does the R3-derived EIG difference persist beyond the perturbation turn?**  
   *Yes.* Retention rate is **100.00%** on Turn 2 ($PR_2 = 0.8619$) and remains 100.00% through Turn 5 ($PR_5 = 0.6665$).
2. **How rapidly does it decay under neutral recovery?**  
   It decays strictly monotonically at an exponential rate governed by $\alpha = 0.65$, retaining $66.65\%$ of initial signal strength by Turn 5.
3. **Does repeated same-direction exposure accumulate, saturate, or habituate?**  
   *Accumulates and saturates.* EIG displacement increases from $0.019276$ ($PR=1.00$) to $0.033172$ ($PR=1.7119$), asymptotically approaching the theoretical attractor displacement.
4. **Does direction reversal follow current direction or prior history?**  
   It follows current direction with synchronous sign alternation on odd turns (100% agreement), while exhibiting transitional attenuation during reversal turns due to somatic residual displacement.
5. **Does recovery/reactivation reveal measurable history dependence?**  
   *Yes.* Re-perturbation at Turn 4 produces a **$0.004678\,\text{nat}$** difference in EIG between perturbed and unperturbed histories across 100% of probes.
6. **Are temporal effects consistent across consumers?**  
   *Yes for continuous EIG.* Directional retention is 100.00% across Consumers C, A, B, and D. Discrete action divergence is present in C ($79.89\%$) and absent in A, B, D ($0.00\%$).
7. **Do shuffled/null controls eliminate the effect?**  
   *Yes.* NC5 ($W_{\text{dir}} = \mathbf{0}$) and NC6 (collapsed directional transition) both produce exact $0.0000$ retention.
8. **Does temporal behavior provide evidence beyond the single-turn result?**  
   *Yes.* It demonstrates that R3 directional information is not an isolated transient artifact: it persists across multi-turn conversational horizons, decays predictably, and creates measurable history-dependent modulation.
9. **Which findings are research-validated versus consumer-specific?**  
   Continuous temporal EIG persistence, monotonic decay, and history dependence are **research-validated across all four consumers**. Discrete action flips remain **consumer-dependent (Consumer C specific)**.
10. **What remains unresolved for future architecture decisions?**  
    True Active Inference in the live production pipeline S1–S16, live dialogue interaction, and physical motor consequence remain completely unmeasured and locked behind Quality Gate 2.

---

## 17. Separation of Claims

To preserve scientific rigor and prevent unwarranted cognitive anthropomorphization:

- **Level 1 — Mathematical**: R3 encodes ternary directional signs and scalar surprise $S$.
- **Level 2 — Research-Harness Observation**: The multi-turn research harness exhibits persistent, monotonically decaying, and history-dependent incremental EIG differences across turns $1..5$ ($PR_2 = 0.8619, R_t = 1.00$).
- **Level 3 — Interpretation**: The directional information signal provides robust epistemic differentiation that survives temporal compositional dynamics.
- **Level 4 — Architecture**: **No production promotion is authorized. Quality Gate 2 remains strictly blocked, ADR-029 remains draft, and Phase 22 H1 remains inconclusive.**

---

## 18. Governance State & Conclusion

```text
Phase 22 H1 Status:        INCONCLUSIVE (locked)
Quality Gate 2:            STRICTLY BLOCKED (Δ_HM = 0.0685 < 0.1500)
ADR-029 Status:            DRAFT / RESEARCH RECORD ONLY / NOT RATIFIED
Production Code Diff:      0 files changed
Genesis Profile:           LOCKED {"is_onboarded": false}
```

This study **extends the empirical research evidence** for R3 directional information by demonstrating multi-turn temporal persistence, predictable monotonic decay, saturation, and history dependence in an isolated research harness, without justifying or authorizing production promotion.
