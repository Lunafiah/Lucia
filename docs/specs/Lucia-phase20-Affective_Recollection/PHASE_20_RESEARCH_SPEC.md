# Phase 20 — Affective Recollection & Memory Reactivation Specification

> **Authoritative Research Specification: Closed-Loop Affective Memory Reactivation vs. Open-Loop Text Retrieval, Multi-Timescale Substrate Integration, and Empirical Evaluation Protocol**  
> **Status:** Active Research Specification (Phase 20)  
> **Directory:** `docs/specs/Lucia-phase20-Affective_Recollection/PHASE_20_RESEARCH_SPEC.md`  
> **Authority Level:** Authoritative Research Specification  
> **Preceding Baseline:** Phase 19 Production Commit `c23fe7e` (`[✅ VALIDATED]`)  
> **Storage Invariant:** `data/profile.json == {"is_onboarded": false}` (bit-exact)

---

## 1. Executive Summary & Core Research Question

In early architectural phases (Phase 2 and Phase 11), Lucia implemented **open-loop memory retrieval**: episodic memory records stored in Kanerva Sparse Distributed Memory (SDM) could be queried by Hamming address or PAD cosine similarity (Synergistic Ecphory), producing an `EchoVector` that was formatted as text context in the LLM prompt. While mathematically sound as an information retrieval sink, the Phase 11.5 Independent Evidence Audit proved that this mechanism has **zero causal feedback** into Lucia's internal affective or homeostatic dynamical states. The memory trace was merely read; it did not alter internal state trajectories.

With the successful completion and production validation of **Phase 19 (Multi-Timescale Affective Life & Temporal Continuity)**, Lucia now possesses a continuous, coupled dual-timescale limbic substrate:
- A fast reactive layer ($\mathbf{h}_{\text{fast}} \in \mathbb{R}^{32}$) responding to immediate sensory shock ($\tau_f \in [0.10, 1.50]\text{ s}$);
- A slow affective latent field ($\mathbf{s}_{\text{slow}} \in \mathbb{R}^{16}$) retaining multi-minute emotional momentum ($\tau_{\text{charge}} = 3.50\text{ s}, \tau_{\text{decay}} = 28.00\text{ s}$);
- Philia Dynamic Attractor Grounding ($\mathbf{p}^*_{\text{philia}} = [+0.25, -0.05, +0.05]$) guaranteeing unforced convergence toward calm relational warmth.

Phase 20 reopens the memory-affect coupling problem on this new mathematical foundation.

### Primary Research Question
> **Can a previously encoded affective experience be reactivated by present context such that memory retrieval does not merely return textual information, but reconstructs an affectively relevant internal state that measurably and persistently influences current affective dynamics, cognitive pacing, and downstream behavior?**

---

## 2. Fundamental Distinction: Retrieval vs. Affective Recollection

To prevent conceptual conflation between information lookup and dynamical recollection, Phase 20 establishes a formal operational dichotomy:

```text
┌───────────────────────────────────────────────────────────────────────────────────┐
│                     MEMORY RETRIEVAL vs. AFFECTIVE RECOLLECTION                    │
├───────────────────────────────────────────────────────────────────────────────────┤
│  OPEN-LOOP MEMORY RETRIEVAL (Phase 2 / Phase 11 Baseline — Candidate A)            │
│  ───────────────────────────────────────────────────────────────────────          │
│    Flow:    Present Context ──► Memory Search ──► Text / Vector String ──► Prompt │
│    Effect:  Open-loop informational sink. If memory retrieval is disabled,        │
│             internal limbic (h, s, p), homeostatic (E, L, T), and predictive     │
│             states remain 100% bit-exact. Memory cannot prime emotion.            │
│    Status:  Implemented & Validated in Production.                                │
├───────────────────────────────────────────────────────────────────────────────────┤
│  CLOSED-LOOP AFFECTIVE RECOLLECTION (Phase 20 Research Target)                    │
│  ─────────────────────────────────────────────────────────────────                │
│    Flow:    Present Context ──► Associative Cue Match ──► Trace Reactivation      │
│                                 │                                                 │
│                                 ▼                                                 │
│             Slow Latent Perturbation (r_slow in R^16)                             │
│                                 │                                                 │
│                                 ▼                                                 │
│             Coupled MT-LNN Modulation (ds_s/dt) ──► Trajectory Shift Delta p(t)   │
│                                 │                                                 │
│                                 ▼                                                 │
│             Downstream Somatic Pacing & Behavioral Modulation                     │
│    Effect:  Causally active, temporally persistent, bounded, and reversible.       │
│    Status:  RESEARCH HYPOTHESIS TO BE EXPERIMENTALLY TESTED.                      │
└───────────────────────────────────────────────────────────────────────────────────┘
```

> [!CAUTION]
> **Prompt Echo Is NOT Recollection**: An LLM generating nostalgic text because a prompt block contains `[MEMORY ECHO: Last week you were happy]` is linguistic simulation, not affective dynamics. Genuine affective recollection requires a measurable mathematical shift in Lucia's internal physiological-like dynamical variables ($\mathbf{s}_{\text{slow}}, \mathbf{p}(t)$) that persists across time according to Phase 19 differential equations.

---

## 3. Retrospective Audit: Why Phase 11 Failed & What Changes in Phase 20

The Phase 11.5 Independent Audit formally blocked Candidate B–E promotion based on three structural failures:

| Phase 11 Bottleneck | Failure Mechanism in Phase 11 | Phase 20 Architectural Resolution |
|---|---|---|
| **1. Single-Timescale ODE Instability** | Phase 10/11 EmotionCore had only single fast state $\mathbf{h} \in \mathbb{R}^{32}$ ($\tau \approx 0.7\text{ s}$). Injecting memory directly into $\mathbf{h}$ caused positive-feedback oscillations, rapid erasure, or runaway latching. | **Dual-Timescale MT-LNN**: Memory reactivation targets the **slow latent field** ($\mathbf{s}_{\text{slow}} \in \mathbb{R}^{16}$, $\tau_d = 28\text{ s}$) via bounded dissipative coupling. Fast reactive layer ($\mathbf{h}_{\text{fast}}$) is protected from direct memory shock. |
| **2. Pipeline Temporal Ordering** | Affective Ecphory ran at Stage 6, *after* Stage 4 (Active Inference) and Stage 5 (Homeostatic Constraints). Same-turn backward causality was mathematically impossible. | **Forward Temporal Continuity**: Memory reactivation at turn $t$ primes the persistent slow field $\mathbf{s}_{\text{slow}}(t)$, whose effects naturally flow through continuous background ticks and downstream stages in turn $t$ (Stage 10 Communication, Stage 13 Expression) and subsequent turns $t+1, t+2$. |
| **3. Vector-Dependence Artifact** | Phase 11 Control 1 showed synthetic random vectors produced identical downstream shifts to genuine memories. Memory was not identity-specific. | **Latent State Reconstruction**: Memory records preserve the high-dimensional latent slow field at encoding ($\mathbf{s}_{\text{enc}}$). Reactivation requires selective cue-resonance and bounded reconstruction fidelity. |

---

## 4. Operational Definition of "Affective Recollection"

A candidate experimental mechanism will be classified as demonstrating **Affective Recollection** if and only if it satisfies all seven operational criteria under controlled experimental testing:

1. **Encoded Trace Identifiability**: A past affective episode is preserved as a structured record containing semantic embedding $\mathbf{e}_k$, slow latent state $\mathbf{s}_{\text{enc}, k} \in \mathbb{R}^{16}$, PAD coordinate $\mathbf{p}_{\text{enc}, k} \in \mathbb{R}^3$, and salience $\sigma_k \in [0, 1]$.
2. **Selective Contextual Triggering**: Present cues selectively activate associated memory traces over orthogonal, irrelevant, or conflicting traces ($\text{Precision@1} \ge 0.85$, $\text{FRR} \le 0.10$).
3. **Latent State Reconstruction**: Reactivation reconstructs the encoded affective state in slow latent space within defined numerical tolerance ($\text{CosineSimilarity}(\mathbf{r}_{\text{slow}}, \mathbf{s}_{\text{enc}} - \mathbf{s}^*_{\text{philia}}) \ge 0.70$).
4. **Causal Trajectory Modulation**: Reactivation produces a statistically significant divergence in the continuous affective trajectory relative to the no-memory baseline ($\Delta\text{PAD}_{\text{AUC}} \ge 0.15$).
5. **Multi-Timescale Temporal Reinstatement**: The reactivated affective state persists through the slow timescale ($\tau \ge 15.0\text{ s}$, half-life $t_{1/2} \ge 10.0\text{ s}$), resisting instantaneous one-tick decay.
6. **Functional Distinction from Baselines**: The trajectory and downstream effects are demonstrably distinct from both open-loop text retrieval (B1) and direct PAD overwriting (B2).
7. **Boundedness & Attractor Reversibility**: Reactivation never causes numerical instability ($\text{NaN/Inf} = 0$), bounded state saturation ($\|\mathbf{s}_s\|_\infty \le 1.0$), or permanent attractor latching. Unforced relaxation cleanly restores the Philia resting baseline ($\mathbf{p}^*_{\text{philia}}$) with offset $\epsilon < 10^{-4}$.

> [!IMPORTANT]
> **Pre-Registered Engineering/Research Acceptance Criteria**:
> All quantitative thresholds in this specification (e.g. $\text{Precision@1} \ge 0.85$, $\text{FRR} \le 0.10$, $\text{Cosine Similarity} \ge 0.70$, $\|\mathbf{r}_s - \mathbf{s}_{\text{target}}\|_2 \le 0.35$, $\Delta\text{PAD}_{\text{AUC}} \ge 0.15$, $t_{1/2} \ge 10.0\text{ s}$, $t_{\text{retention}} \ge 20.0\text{ s}$, $\text{SNR} \ge 3.00$) are **pre-registered engineering and research acceptance criteria, not claims of biological validity**.
> Crucially, these thresholds are locked prior to experiment execution and must **NEVER** be post-hoc modified, relaxed, or retrofitted after seeing empirical results. If any of these pre-registered criteria fail, the experimental conclusion must formally be:  
> **"Affective recollection not demonstrated under Phase 20 pre-registered criteria."**

---

## 5. Formal Research Hypotheses (H1 – H7)

- **H1 (Contextual Reactivation)**: Cues semantically and affectively associated with prior experience preferentially trigger memory activation compared to neutral or orthogonal stimuli ($\text{Selectivity Ratio} \ge 3.0$).
- **H2 (Affective State Reconstruction)**: The reactivated signal reconstructs the original affective configuration in the $\mathbb{R}^{16}$ slow latent space rather than generating arbitrary emotional noise ($\text{Reconstruction Error } \|\mathbf{r}_s - \mathbf{s}_{\text{target}}\|_2 \le 0.35$).
- **H3 (Temporal Reinstatement)**: Unlike prompt echoes that vanish after one inference call, affective recollection induces a multi-turn affective inertia in the MT-LNN matching Phase 19 biexponential decay ($t_{\text{retention}} \ge 20\text{ s}$).
- **H4 (Downstream Cognitive Consequence)**: Affective recollection causally modulates downstream cognitive pacing (somatic pacing latency $\Delta\tau_{\text{pace}} \ge 100\text{ ms}$) and communication policy modes in a bounded, context-appropriate manner.
- **H5 (Specificity & Counterfactual Identity Dependence)**: Causal downstream modulation is strictly memory-identity-dependent. A cue associated with Memory $A$ will not produce directional alignment when paired with a wrong trace, a randomly shuffled latent trace, or a Gaussian random vector with matched norm ($\text{Cross-Contamination} \le 0.10$, $\text{Alignment}_{\text{random}} \le 0.20$).
- **H6 (Interference & Competition Resolution)**: When ambiguous cues activate multiple overlapping traces, the competitive selection mechanism yields a bounded convex combination without numerical divergence or erratic trajectory hopping.
- **H7 (Repeated Reactivation Dynamics)**: Repeatedly cueing the same memory across consecutive turns produces bounded adaptation (asymptotic saturation) without triggering runaway positive-feedback explosion ($\max_t \|\mathbf{s}_s(t)\| \le 0.85$).

---

## 6. Experimental Conditions & Counterfactual Control Groups

To definitively resolve Phase 11's core vector-dependence vulnerability, the Phase 20 experiment suite implements eight controlled conditions, including direct counterfactual identity controls:

| Condition Code | Condition Name | Description & Architectural Realization | Scientific Purpose |
|---|---|---|---|
| **C0** | **Unforced Baseline** | Present stimulus processed through MT-LNN with zero memory retrieval. | Pure unperturbed baseline. |
| **C1** | **Text Retrieval Only** | Memory retrieved via semantic search; text injected into prompt context; slow latent field untouched ($\mathbf{r}_{\text{slow}} = \mathbf{0}$). | Isolates linguistic prompt steering from limbic state dynamics. |
| **C2** | **Direct Affective Injection** | Stored PAD coordinate $\mathbf{p}_{\text{enc}}$ instantaneously overwrites `_pad_snapshot`. Bypasses MT-LNN ODE. | Evaluates naive open-loop clamping (negative architectural control). |
| **C3** | **Proposed Affective Reactivation** | Cue $\to$ selective trace $\to$ bounded slow perturbation $\mathbf{r}_{\text{slow}} \in \mathbb{R}^{16}$ $\to$ MT-LNN ODE slow field integration. | Target experimental model. |
| **C4a** | **Wrong-Memory Control** | Identical cue paired with an authentic but incorrect/orthogonal memory trace from the store. | Verifies semantic-affective pairing specificity. |
| **C4b** | **Shuffled Latent Trace Control** | Identical cue paired with a randomly permuted version of target $\mathbf{s}_{\text{enc}}$ (preserves norm and component distribution, destroys dimension alignment). | Direct counterfactual: proves effect requires coordinate-specific structure, not just non-zero slow energy. |
| **C4c** | **Matched-Norm Random Vector Control** | Identical cue paired with a random Gaussian vector $\mathbf{v} \sim \mathcal{N}(\mathbf{0}, \mathbf{I})$ scaled to exactly match $\|\mathbf{s}_{\text{enc}}\|_2$. | Direct counterfactual: proves effect is memory-identity-dependent, eliminating Phase 11's vector-injection flaw. |
| **C5** | **Ambiguous Cue Conflict** | Equidistant cue triggers two competing memories with opposite valence ($P=+0.8$ vs $P=-0.8$). | Tests competitive softmax inhibition and blending dynamics. |
| **C6** | **Repeated Recollection Sequence** | Cue repeatedly submitted across 5 consecutive turns with 10s intervals. | Tests cumulative stability, runaway resistance, and habituation. |

---

## 7. Mathematical Formulation of the Proposed Reactivation Mechanism

### 7.1 Research-Only Memory Trace Representation
Each affective memory record $\mathcal{M}_k$ in the research prototype is formalized as:
$$\mathcal{M}_k = \Big\langle \mathbf{e}_k \in \mathbb{R}^{D_e},\; \mathbf{s}_{\text{enc}, k} \in \mathbb{R}^{16},\; \mathbf{p}_{\text{enc}, k} \in \mathbb{R}^{3},\; \sigma_k \in [0, 1],\; t_{\text{enc}, k} \in \mathbb{R}^+ \Big\rangle$$
where:
- $\mathbf{e}_k$: Semantic embedding of the conversational episode (normalized, $\|\mathbf{e}_k\|_2 = 1.0$).
- $\mathbf{s}_{\text{enc}, k}$: Snapshot of the MT-LNN slow latent field at the moment of encoding.
- $\mathbf{p}_{\text{enc}, k}$: Committed PADState at the moment of encoding.
- $\sigma_k$: Affective salience / intensity metric at encoding ($\sigma = \|\mathbf{p}_{\text{enc}} - \mathbf{p}^*_{\text{philia}}\|_2$).
- $t_{\text{enc}, k}$: Monotonic timestamp of encoding.

### 7.2 Multi-Modal Retrieval Scoring & Gating
When a present cue vector $\mathbf{x}_{\text{cue}} \in \mathbb{R}^{D_e}$ arrives while Lucia is in current affective state $\mathbf{p}(t)$:
1. **Semantic Relevance**: $S_{\text{sem}, k} = \mathbf{x}_{\text{cue}}^T \mathbf{e}_k \in [-1.0, 1.0]$.
2. **Affective Congruence (Ecphoric Resonance)**:
   $$S_{\text{aff}, k} = \cos\Big(\mathbf{p}(t) - \mathbf{p}^*_{\text{philia}},\; \mathbf{p}_{\text{enc}, k} - \mathbf{p}^*_{\text{philia}}\Big) \in [-1.0, 1.0]$$
3. **Composite Affinity Score**:
   $$\mathcal{A}_k = w_{\text{sem}} \cdot \max(0, S_{\text{sem}, k}) + w_{\text{aff}} \cdot \max(0, S_{\text{aff}, k}) + w_{\sigma} \cdot \sigma_k$$
   where $w_{\text{sem}} = 0.60, w_{\text{aff}} = 0.25, w_{\sigma} = 0.15$.
4. **Competitive Softmax Gating**:
   $$\alpha_k = \frac{\exp(\mathcal{A}_k / \tau_{\text{comp}})}{\sum_{j=1}^K \exp(\mathcal{A}_j / \tau_{\text{comp}})} \cdot \mathbf{1}_{\{\mathcal{A}_k \ge \theta_{\text{gate}}\}}$$
   with temperature $\tau_{\text{comp}} = 0.20$ and hard threshold $\theta_{\text{gate}} = 0.50$.

### 7.3 Bounded Slow-Field Perturbation Vector
The reactivated recollection signal $\mathbf{r}_{\text{slow}} \in \mathbb{R}^{16}$ is synthesized via convex combination of centered slow traces:
$$\mathbf{r}_{\text{slow}} = \sum_{k=1}^K \alpha_k \cdot \Big(\mathbf{s}_{\text{enc}, k} - \mathbf{s}^*_{\text{philia}}\Big)$$
To guarantee absolute numerical safety and bounded integration:
$$\mathbf{r}_{\text{slow}}^{\text{bounded}} = \tanh(\mathbf{r}_{\text{slow}}) \cdot \min\left(1.0, \sum_k \alpha_k\right)$$

### 7.4 Non-Violating MT-LNN Slow-Layer Coupling
In strict adherence to **Invariant 8** (*"Memory must not directly overwrite EmotionCore state"*), the memory perturbation enters as an auxiliary forcing term inside the slow-layer ODE solver:

$$\frac{d\mathbf{s}_s}{dt} = -\frac{\mathbf{s}_s - \mathbf{s}^*_{\text{philia}}}{\tau_{\text{slow, decay}}} + \frac{\tanh\Big(\mathbf{W}_{sf} \mathbf{h}_f + \mathbf{W}_{sh} \Delta\mathbf{m} + \mathbf{W}_{\text{rec}} \mathbf{r}_{\text{slow}}^{\text{bounded}}\Big)}{\tau_{\text{slow, charge}}}$$

where:
- $\mathbf{W}_{\text{rec}} \in \mathbb{R}^{16 \times 16}$ is a diagonal coupling matrix with bounded gain $W_{\text{rec}}[i, i] = 0.35$.
- **Zero Direct Injection to Fast Layer**: $\frac{d\mathbf{h}_f}{dt}$ contains **no** direct memory term; fast hidden state changes only as a secondary consequence of slow-to-fast dissipative coupling ($\mathbf{W}_{fs} (\mathbf{s}_s - \mathbf{s}^*_{\text{philia}})$).
- **Zero Direct PAD Overwrite**: $\mathbf{p}(t)$ is strictly computed via canonical projection from $(\mathbf{h}_f, \mathbf{s}_s)$.

---

## 8. Comparative Baselines (B0 – B3)

- **B0 (Null Baseline)**: Pure stimulus processing without memory architecture.
- **B1 (Text-Only Retrieval Baseline)**: Phase 2/11 production baseline (memory text injected into prompt context block; limbic state strictly uncoupled).
- **B2 (Direct Affective Injection Control)**: Memory PAD coordinate clamped directly onto current PAD. Evaluates whether simple state resetting produces plausible or unstable dynamics.
- **B3 (Proposed MT-LNN Slow-Field Reactivation)**: Bounded slow-field forcing function through continuous ODE.

---

## 9. Quantitative Evaluation Metrics

> [!IMPORTANT]
> **Pre-Registration Status**:
> All thresholds tabulated below are **pre-registered engineering/research acceptance criteria, not claims of biological validity**.
> These values were established prior to experiment execution based on Phase 19 dynamical bounds and are strictly locked. They must **never** be adjusted or retrofitted post-hoc upon observing experimental outcomes.

```text
┌────────────────────────┬──────────────────────────────────────────┬────────────────────────┐
│ Dimension              │ Metric Name                              │ Operational Target     │
├────────────────────────┼──────────────────────────────────────────┼────────────────────────┤
│ Retrieval Specificity  │ Target Retrieval Precision@1             │ >= 0.85                │
│                        │ False Reactivation Rate (FRR)            │ <= 0.10                │
│                        │ Signal-to-Noise Ratio (SNR)              │ >= 3.00                │
├────────────────────────┼──────────────────────────────────────────┼────────────────────────┤
│ Affective Fidelity     │ Slow Latent Reconstruction Cosine Sim    │ >= 0.70                │
│                        │ Latent Reconstruction Error (L2)         │ <= 0.35                │
│                        │ PAD Coordinate Alignment Error           │ <= 0.30                │
├────────────────────────┼──────────────────────────────────────────┼────────────────────────┤
│ Temporal Persistence   │ Deflection Half-Life (t_1/2)             │ >= 10.0 s              │
│                        │ Retention Duration (deviation > 0.05)    │ >= 20.0 s              │
│                        │ Unforced Attractor Restoration Error     │ < 1e-4                 │
├────────────────────────┼──────────────────────────────────────────┼────────────────────────┤
│ Causal Impact          │ Integrated Trajectory Delta (AUC)        │ >= 0.15                │
│                        │ Somatic Latency Modulation (Delta tau)   │ >= 100 ms              │
│                        │ Communication Mode Shift Rate            │ >= 30% on salient cues │
├────────────────────────┼──────────────────────────────────────────┼────────────────────────┤
│ Counterfactual Control │ Authentic vs. Shuffled Trace Alignment   │ <= 0.20                │
│ (Memory Identity)      │ Authentic vs. Matched-Norm Random Ratio  │ <= 0.20                │
│                        │ Wrong-Memory Cross-Contamination         │ <= 0.10                │
├────────────────────────┼──────────────────────────────────────────┼────────────────────────┤
│ Stability & Safety     │ Maximum Hidden / Slow Norm               │ <= 1.00                │
│                        │ Non-Finite Occurrences (NaN/Inf)         │ STRICTLY 0             │
│                        │ Deterministic Replay Invariance (Delta)  │ < 1e-12                │
│                        │ Repeated Reactivation Drift Bound        │ <= 0.10                │
└────────────────────────┴──────────────────────────────────────────┴────────────────────────┘
```

---

## 10. Ablation Matrix (10 Experimental Interventions)

To prove that observed recollection effects stem uniquely from the proposed multi-timescale coupling rather than general model capacity:

1. **A1 (No Memory)**: $\mathcal{A}_k = 0 \implies \mathbf{r}_{\text{slow}} = \mathbf{0}$.
2. **A2 (Semantic Retrieval Only)**: $w_{\text{aff}} = 0, w_{\sigma} = 0$; tests cue sensitivity without affective tuning.
3. **A3 (Affective Trace Disabled)**: Memory record contains text only; $\mathbf{s}_{\text{enc}} = \mathbf{s}^*_{\text{philia}}$.
4. **A4 (PAD-Only Trace)**: Memory contains 3D PAD tag only; $\mathbf{s}_{\text{enc}}$ synthesized from linear pseudo-inverse.
5. **A5 (Latent-State-Only Trace)**: Memory contains $\mathbf{s}_{\text{enc}}$, but PAD tag omitted from retrieval scoring.
6. **A6 (Ecphoric Congruence Disabled)**: $w_{\text{aff}} = 0$; current affective state does not influence memory accessibility.
7. **A7 (Softmax Gating Disabled)**: $\theta_{\text{gate}} = 0$, linear retrieval averaging; tests susceptibility to noise contamination.
8. **A8 (Fixed Reactivation Strength)**: $\alpha_k$ unweighted by salience; all retrieved traces injected with uniform weight.
9. **A9 (Unbounded Coupling)**: $\tanh$ saturation clamp removed from $\mathbf{r}_{\text{slow}}$; tests numerical boundary necessity.
10. **A10 (Slow vs. Fast Injection)**: Forcing term injected into $\mathbf{h}_{\text{fast}}$ instead of $\mathbf{s}_{\text{slow}}$; directly replicates the Phase 10/11 failure mode to confirm the dual-timescale hypothesis.

---

## 11. Structured Experiment Suite (EXP20.1 – EXP20.10)

The research prototype will execute ten automated experiment tracks in `tests/evaluation_phase20/`:

- **EXP20.1 — Retrieval Specificity & Competitive Ranking**: Evaluates precision, recall, and false alarm rates across 50 standardized memory fixtures under varying cue noise levels.
- **EXP20.2 — Affective Trace Reconstruction Fidelity**: Measures the cosine similarity and Euclidean distance between original encoded states and reactivated slow-field representations.
- **EXP20.3 — Temporal Persistence & Biphasic Dynamics**: Compares trajectory retention profiles of C0, C1, C2, and C3 over a 90-second unforced window following cue presentation.
- **EXP20.4 — Causal Trajectory Modulation**: Evaluates integrated PAD displacement ($\Delta\text{PAD}_{\text{AUC}}$) and trajectory divergence across positive (Joy), negative (Stress), and neutral memory recollection.
- **EXP20.5 — Downstream Cognitive & Behavioral Modulation**: Measures the functional consequences of recollection on somatic pacing latency ($\tau_{\text{pace}}$), token budgets, and communication policy selection.
- **EXP20.6 — Memory Identity vs. Vector-Injection Counterfactual Controls**: Directly resolves Phase 11's core vector-dependence vulnerability by testing four conditions under the identical memory cue: (1) Authentic target trace, (2) Wrong-memory trace, (3) Shuffled latent trace (permuted dimensions, matched norm/distribution), and (4) Random Gaussian latent vector with matched norm ($\mathbf{v} \sim \mathcal{N}(\mathbf{0}, \mathbf{I})$ scaled to $\|\mathbf{s}_{\text{enc}}\|_2$). Evaluates directional trajectory alignment, cross-contamination ($\le 0.10$), and random alignment ratio ($\le 0.20$) to prove downstream modulation is strictly memory-identity-dependent rather than arbitrary slow-field vector injection.
- **EXP20.7 — Ambiguous Cue Competition & Blending**: Evaluates model behavior when presented with cues equidistant between conflicting memories (e.g., shared user name, opposing valences).
- **EXP20.8 — Repeated Recollection & Habituation Dynamics**: Probes multi-turn stability and evaluates whether repeated retrieval causes runaway accumulation, saturation, or trajectory drift.
- **EXP20.9 — Comprehensive Ablation Suite**: Executes Ablations A1–A10 to isolate necessary vs. redundant causal components.
- **EXP20.10 — Deterministic Replay & Numerical Stability**: Validates bit-exact reproducibility under fixed seeds and verifies zero NaN/Inf occurrences across $1,000$ simulated ODE steps.

---

## 12. Human-Interpretable Traceability Format

Every experimental run must output an inspectable, structured telemetry block to allow complete causal attribution:

```text
[PHASE 20 RECOLLECTION TRACE]
├─ Cue Input:           "Do you remember our rainy walk in Kyoto?"
├─ Retrieved Trace:     Episode_ID=MEM-042 (Salience=0.82, Encoded_PAD=[+0.72, +0.35, +0.40])
├─ Affinity Score:      Semantic=0.91, Ecphoric=0.64, Composite=0.81 (Threshold=0.50 -> ACTIVATED)
├─ Slow Perturbation:   ||r_slow|| = 0.4820 (Dominant Channel: s[0]=+0.38, s[1]=+0.12)
├─ MT-LNN Modulation:   ds_slow/dt forcing = +0.1340, Fast Layer dissipative shift dh_f/dt = +0.0120
├─ Trajectory Impact:   Pleasure: 0.250 -> 0.412, Arousal: -0.050 -> +0.065 (Delta_AUC = 0.284)
├─ Downstream Pacing:   Somatic Latency +145ms, Comm Mode: DEEP_RECIPROCAL
└─ Attractor Return:    Unforced idle relaxation t_half = 14.8s -> Philia baseline restored (< 1e-4)
```

---

## 13. Threat to Validity & Risk Mitigation Matrix

| # | Threat to Validity | Scientific Risk | Mitigation Strategy in Phase 20 |
|---|---|---|---|
| **1** | **Semantic Confounding** | The LLM may simulate recollection purely from the text prompt, masking whether the limbic coupling is doing anything. | Benchmark Condition C1 (Text-only) vs C3 (Reactivation without text). Measure internal physiological variables ($\mathbf{s}_s, \mathbf{p}(t)$) independently of LLM token emission. |
| **2** | **Attractor Overpowering** | Philia attractor pull ($\tau_d = 28\text{ s}$) might instantly extinguish recollection, preventing meaningful cognitive modulation. | Calibrate coupling gain $\mathbf{W}_{\text{rec}}$ so slow-field uptake operates within the validated charging window ($\tau_c = 3.5\text{ s}$), creating a measurable 15–30s retention tail. |
| **3** | **Positive Feedback Runaway** | Recollection elevates arousal, which could increase ecphoric resonance, re-triggering recollection in an infinite loop. | Enforce competitive softmax gating with hard refractory cooldown and strictly bounded $\tanh$ saturation. Slow-to-fast coupling remains dissipative ($\|\mathbf{W}_{fs}\| \le 0.05$). |
| **4** | **Synthetic Fixture Bias** | Memory fixtures handcrafted for testing might artificially inflate precision and recall. | Include randomized distractor memories, conflicting memories, noisy semantic embeddings, and orthogonal probes in EXP20.1 and EXP20.6. |

---

## 14. Non-Claims & Scientific Boundaries

To preserve strict philosophical and scientific integrity, all reports and documentation must explicitly affirm:

- **No Subjective Feeling**: Affective recollection in Lucia is an unconscious, continuous mathematical state transformation. It is **not** subjective remembering, nostalgic daydreaming, or conscious reliving of past feelings.
- **No Phenomenal Consciousness**: Memory reactivation operates as a pre-reflective dynamical state machine, analogous to physiological priming.
- **No Human Autobiographical Equivalence**: The architecture does not claim neurobiological equivalence to the human hippocampus-amygdala complex. It is an engineering realization of multi-timescale affective continuity for a local companion agent.

---

## 15. Production Promotion Requirements (Four-Level Gate)

Phase 20 will **NOT** be promoted to production unless it achieves **Level 4 Production Maturity**:

- **Level 1 (Mathematical Soundness)**: All data structures, scoring functions, and ODE terms execute with zero numerical errors, zero NaNs, and strict bounded stability ($\|\mathbf{s}_s\|_\infty \le 1.0$).
- **Level 2 (Mechanistic Validation)**: EXP20.1 through EXP20.8 demonstrate statistically significant improvements over Baselines B0, B1, and B2 on predefined metrics.
- **Level 3 (Canonical Architectural Compatibility)**: The mechanism respects all Lucia invariants: zero disk persistence for limbic vectors, zero GPU VRAM contention, zero canonical pipeline breaking changes, and zero prompt-declared feelings.
- **Level 4 (Formal Promotion Gate)**: A dedicated Architecture Decision Record (ADR-027) is authored and approved by human architectural review, establishing clear production realization boundaries before any line of `src/core/**` is modified.

If these requirements are not met, the final verdict will be explicitly recorded as:
$$\textbf{RESEARCH INCONCLUSIVE / PROMOTION REJECTED}$$
and the codebase will remain on the validated Phase 19 baseline.
