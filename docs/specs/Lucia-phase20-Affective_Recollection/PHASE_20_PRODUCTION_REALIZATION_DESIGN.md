# PHASE 20 PRODUCTION REALIZATION ARCHITECTURE DESIGN
## Closed-Loop Affective Recollection via Slow-Field Latent Forcing ($\mathbf{r}_{\text{slow}}^{\text{bounded}}$)

> **Authoritative Architectural Design & Production Integration Blueprint for Lucia Phase 20**  
> **Status**: ARCHITECTURE GATE SPECIFICATION (REVISED) — SUBMITTED FOR HUMAN ARCHITECTURAL REVIEW  
> **Lifecycle Governance**: Foundation-First Research Cycle -> Production Realization  
> **Author**: Antigravity Implementation Architect  
> **Governing ADR**: ADR-027  
> **Pre-Implementation Git Baseline**: `c23fe7e`  
> **Production Code Status**: STRICTLY ZERO MODIFICATIONS UNTIL GATE APPROVAL (`src/core/**` UNTOUCHED)  
> **Date**: September 2026  

---

## 1. Executive Decision & Promotion Scope

### 1.1 Decision Statement
Following empirical validation in the Phase 20 Foundation-First Research Cycle (`tests/evaluation_phase20/`), the achievement of a 100% pass rate across all 10 pre-registered research criteria, the empirical resolution of Phase 11's vector-dependence vulnerability (EXP20.6), and formal research promotion sign-off in **ADR-027** and [`PHASE_20_ACCEPTANCE_REPORT.md`](file:///c:/Users/Lunafiah/Desktop/My_project/Lucia/docs/specs/Lucia-phase20-Affective_Recollection/PHASE_20_ACCEPTANCE_REPORT.md), this document defines the production realization architecture for **Affective Recollection & Memory Reactivation** in the Lucia Companion.

### 1.2 Promotion Boundary: Promoted vs. Strictly Forbidden Invariants

```text
┌────────────────────────────────────────────────────────────────────────────────────────┐
│                                 PROMOTION BOUNDARY                                     │
│                                                                                        │
│  PROMOTED TO PRODUCTION ARCHITECTURE:                                                  │
│  [+] Episodic Latent Trace Co-Encoding (s_enc in R^16 embedded in MemoryTrace)         │
│  [+] Multi-Modal Retrieval Scoring (0.60 S_sem + 0.25 S_aff + 0.15 S_sigma)           │
│  [+] Competitive Softmax Gating (theta_gate = 0.50, tau_comp = 0.20, noise rejection)  │
│  [+] Closed-Loop ODE Slow-Field Forcing (W_rec * r_slow^bounded in R^16)               │
│  [+] Diagonal Dissipative Coupling (W_rec = 0.35 * I_16)                              │
│  [+] Pre-Reflective Downstream Pacing Modulation (Delta_tau_pace in Stage 12)          │
│  [+] Asymptotic Recollection Dissipation (t_1/2 ~ 32.1s under tau_slow_decay = 28.0s)  │
│  [+] Deterministic Legacy Compatibility Approximation (PAD -> slow projection fallback)│
│  [+] Architectural Decoupling: Memory produces RecollectionResult; Orchestrator decides│
│  [+] Feature Flag Instant Rollback (enable_affective_recollection = true/false)        │
│                                                                                        │
│  STRICTLY FORBIDDEN INVARIANTS (NEVER PROMOTED):                                       │
│  [-] Subjective conscious remembering, nostalgic roleplay, or psychological sentience  │
│  [-] Self-reported emotional declarations ("I recall feeling...", "I feel nostalgic") │
│  [-] Introspective reflective self-models or ego identity constructs                  │
│  [-] Arbitrary fast-layer vector injection (Phase 11 failure mode)                     │
│  [-] Direct limbic actuation by memory subsystem (bypassing CognitiveOrchestrator)    │
│  [-] Direct modification of canonical storage (data/profile.json is_onboarded: false)  │
│  [-] Cloud-based inference, cloud STT/TTS, or external telemetry dependencies          │
│  [-] Synchronous disk I/O or network calls under concurrency locks                     │
└────────────────────────────────────────────────────────────────────────────────────────┘
```

### 1.3 Target Production Subsystems
Production integration modifies strictly the following core components:
1. **Limbic Subsystem ([`src/core/emotion/emotion_core.py`](file:///c:/Users/Lunafiah/Desktop/My_project/Lucia/src/core/emotion/emotion_core.py), [`src/core/config.py`](file:///c:/Users/Lunafiah/Desktop/My_project/Lucia/src/core/config.py))**:
   - Extend the coupled MT-LNN ODE solver to accept auxiliary bounded slow-field forcing $\mathbf{W}_{\text{rec}} \mathbf{r}_{\text{slow}}^{\text{bounded}}(t)$.
   - Provide thread-safe public accessors: `inject_recollection(r_slow: np.ndarray, duration_sec: float)` and `get_slow_latent_state() -> np.ndarray`.
2. **Affective Memory Subsystem ([`src/core/memory/affective_memory.py`](file:///c:/Users/Lunafiah/Desktop/My_project/Lucia/src/core/memory/affective_memory.py), [`src/core/memory/ecphory.py`](file:///c:/Users/Lunafiah/Desktop/My_project/Lucia/src/core/memory/ecphory.py))**:
   - Extend `MemoryTrace` dataclass to serialize `slow_latent_trace: Optional[np.ndarray]` ($\mathbb{R}^{16}$, float32).
   - Implement multi-modal retrieval scoring and competitive softmax gating.
   - Implement deterministic legacy compatibility approximation synthesizing $\mathbf{s}_{\text{fallback}}$ from 3D PAD for pre-Phase-20 memories.
   - Return structured, typed `RecollectionResult` to `CognitiveOrchestrator`. Memory does NOT directly actuate `EmotionCore`.
3. **Cognitive Orchestrator ([`src/core/orchestrator/cognitive_orchestrator.py`](file:///c:/Users/Lunafiah/Desktop/My_project/Lucia/src/core/orchestrator/cognitive_orchestrator.py))**:
   - Map all integration points to the locked, canonical 16-stage pipeline (S1–S16) without renumbering or redefining stages.
   - In Stage 6: Receive `RecollectionResult`, evaluate execution policy, and dispatch `inject_recollection()` to `EmotionCore`.
   - In Stage 12: Apply somatic pacing delta $\Delta\tau_{\text{pace}}$ derived from recollection state.
   - In Stage 16.1: Snapshot $\mathbf{s}_{\text{slow}}$ and pass to `AffectiveMemory.store()`.
4. **Configuration & Safety ([`src/core/config.py`](file:///c:/Users/Lunafiah/Desktop/My_project/Lucia/src/core/config.py), [`src/core/safety/boundary_layer.py`](file:///c:/Users/Lunafiah/Desktop/My_project/Lucia/src/core/safety/boundary_layer.py))**:
   - Add configuration parameters and instant feature flag `enable_affective_recollection: bool = True`.
   - Verify boundary layer regex filters catch any introspective recollection phrasing.

---

## 2. Actual Phase 19 Production Baseline Parameters (Audited from `src/core`)

All parameters in this specification are audited directly from active production code ([`src/core/config.py`](file:///c:/Users/Lunafiah/Desktop/My_project/Lucia/src/core/config.py) and [`src/core/emotion/emotion_core.py`](file:///c:/Users/Lunafiah/Desktop/My_project/Lucia/src/core/emotion/emotion_core.py)), eliminating research-only trajectory constants:

### 2.1 Audited Canonical Production Parameters

| Parameter Symbol | Production Attribute Name | Production Canonical Value | Subsystem Source |
|---|---|---|---|
| $H$ | `EmotionConfig.hidden_dim` | `32` | `src/core/config.py:69` |
| $H_s$ | `EmotionConfig.hidden_slow_dim` | `16` | `src/core/config.py:73` |
| $N_{\text{in}}$ | Stimulus Vector dimension | `16` | `src/core/emotion/emotion_core.py:74` |
| $N_m$ | Homeostatic context dimension | `4` (`[energy, load, tension, stability]`) | `src/core/emotion/emotion_core.py:75` |
| $\mathbf{p}^*_{\text{philia}}$ | `EmotionConfig.resting_baseline` | `(0.25, -0.05, 0.05)` (P, A, D) | `src/core/config.py:70` |
| $\mathbf{s}^*_{\text{philia}}$ | `EmotionConfig.philia_slow_baseline` | `(0.20, -0.05, 0.05)` (first 3 dims of $\mathbb{R}^{16}$) | `src/core/config.py:81` |
| $\tau_{\text{fast, min}}$ | `EmotionConfig.tau_fast_min` | `0.10` seconds | `src/core/config.py:74` |
| $\tau_{\text{fast, max}}$ | `EmotionConfig.tau_fast_max` | `1.50` seconds | `src/core/config.py:75` |
| $\tau_{\text{slow, charge}}$ | `EmotionConfig.tau_slow_charge` | **`3.50` seconds** | `src/core/config.py:76` |
| $\tau_{\text{slow, decay}}$ | `EmotionConfig.tau_slow_decay` | **`28.00` seconds** | `src/core/config.py:77` |
| $\mathbf{W}_{fs}$ gain | `EmotionConfig.w_fs_coupling` | `0.05` | `src/core/config.py:78` |
| $\mathbf{W}_{sf}$ gain | `EmotionConfig.w_sf_coupling` | `1.00` | `src/core/config.py:79` |
| $\mathbf{W}_{sh}$ gain | `EmotionConfig.w_homeo_coupling` | `0.40` | `src/core/config.py:80` |
| $\Delta t_{\text{cadence}}$ | `EmotionConfig.loop_cadence_ms` | `200` ms ($5\text{ Hz}$) | `src/core/config.py:68` |
| $\Delta t_{\text{step}}$ | `EmotionConfig.ode_step_size` | `0.1` seconds | `src/core/config.py:71` |
| $M$ | `AffectiveMemoryConfig.m` | `64` | `src/core/memory/affective_memory.py:52` |
| $D$ | `SDMConfig.address_dim` | `1000` | `src/core/config.py:403` |

### 2.2 Audited Production Differential Equations (Pre-Phase-20 Baseline)

In active production (`src/core/emotion/emotion_core.py:11-16`):

$$\frac{d\mathbf{h}_f}{dt} = \frac{-\mathbf{h}_f + \tanh\Big(\mathbf{W}_{ff} \mathbf{h}_f + \mathbf{W}_{fs}(\mathbf{s}_s - \mathbf{s}^*_{\text{philia}}) + \mathbf{U}_f \mathbf{x} + \mathbf{b}_f\Big)}{\tau_{\text{fast}}(\mathbf{h}_f, \mathbf{x})}$$

$$\frac{d\mathbf{s}_s}{dt} = -\frac{\mathbf{s}_s - \mathbf{s}^*_{\text{philia}}}{\tau_{\text{slow, decay}}} + \frac{\tanh\Big(\mathbf{W}_{sf} \mathbf{h}_f + \mathbf{W}_{sh} \Delta\mathbf{m}\Big)}{\tau_{\text{slow, charge}}}$$

$$\mathbf{PAD}(t) = \text{clip}\Big(\mathbf{W}_{\text{proj}, f} \mathbf{h}_f + \mathbf{W}_{\text{proj}, s}(\mathbf{s}_s - \mathbf{s}^*_{\text{philia}}) + \mathbf{p}^*_{\text{philia}} + \mathbf{b}_{\text{proj}}, -1.0, 1.0\Big)$$

Where:
- $\tau_{\text{fast}}(\mathbf{h}_f, \mathbf{x}) = \text{clip}(\text{softplus}(\mathbf{W}_\tau \mathbf{h}_f + \mathbf{U}_\tau \mathbf{x} + \mathbf{b}_\tau), \tau_{\text{fast, min}}, \tau_{\text{fast, max}})$.
- $\Delta\mathbf{m} = \mathbf{m} - [1.0, 0.0, 0.0, 1.0]^T \in \mathbb{R}^4$ representing deviations from nominal homeostatic equilibrium.
- At resting state ($\mathbf{h}_f = \mathbf{0}, \mathbf{s}_s = \mathbf{s}^*_{\text{philia}}$), $\mathbf{PAD}^* = \mathbf{p}^*_{\text{philia}} = [+0.25, -0.05, +0.05]$ bit-exact.

---

## 3. Mapping to Canonical Locked S1–S16 Cognitive Pipeline

The Lucia architecture strictly forbids redefining or renumbering the 16 cognitive stages locked in Phase 16 ([`src/core/orchestrator/cognitive_orchestrator.py:321-570`](file:///c:/Users/Lunafiah/Desktop/My_project/Lucia/src/core/orchestrator/cognitive_orchestrator.py)). All Phase 20 integration hooks map cleanly into the existing stages:

```text
┌────────────────────────────────────────────────────────────────────────────────────────┐
│              CANONICAL S1–S16 PIPELINE WITH PHASE 20 RECOLLECTION HOOKS                │
├───────┬───────────────────────────────────┬────────────────────────────────────────────┤
│ Stage │ Canonical Stage Name & Ownership  │ Phase 20 Production Behavior               │
├───────┼───────────────────────────────────┼────────────────────────────────────────────┤
│ S1    │ Sensory Encoding                  │ Standard lexical/sensory encoding -> x.    │
│ S2    │ Generative Prior Expectation      │ ActiveInference captures pad_initial.      │
│ S3    │ Limbic Integration                │ EmotionCore.push_stimulus & commit_stimulus│
│ S4    │ Prediction Surprise Update        │ ActiveInference.step -> prediction_error.  │
│ S5    │ Homeostatic Modulation            │ Modulates somatic markers & updates homeo  │
│       │                                   │ context in EmotionCore.                    │
│ S6    │ Affective Ecphory & Recollection  │ [PHASE 20 PRIMARY ACTUATION]:              │
│       │ (Memory Retrieval Subsystem)      │ 1. EcphoryEngine evaluates multi-modal     │
│       │                                   │    affinity S_i across MemoryTraces.       │
│       │                                   │ 2. Competitive softmax gating synthesizes  │
│       │                                   │    RecollectionResult (typed dataclass).   │
│       │                                   │ 3. CognitiveOrchestrator inspects result:  │
│       │                                   │    if active and enabled, dispatches       │
│       │                                   │    EmotionCore.inject_recollection().      │
│       │                                   │ 4. Synthesizes standard Echo_Vector.       │
│ S7    │ Memory Context Extraction         │ Evaluates m_avail from echo/recollection.  │
│ S8    │ Structured Knowledge Retrieval    │ KnowledgeStore queries relevant facts.     │
│ S9    │ Relationship Read (Pre-Turn)      │ RelationshipUpdater reads R_{t-1}.         │
│ S10   │ Communication Policy Evaluation   │ Computes comm_state; incorporates          │
│       │                                   │ recollection presence flag in k_dict.      │
│ S11   │ Contextual Prompt Assembly        │ Assembles prompt text; strictly forbids    │
│       │                                   │ self-reported affective declarations.      │
│ S12   │ Conversational Pacing             │ [PHASE 20 PACING MODULATION]:              │
│       │                                   │ pacing_delay_ms += Delta_tau_pace derived  │
│       │                                   │ from recollection forcing magnitude.       │
│ S13   │ LLM Generation & Boundary Layer   │ LLM generation; BoundaryLayer regex blocks │
│       │                                   │ any introspective memory declarations.     │
│ S14   │ Semantic Consistency Guard        │ Validates fact preservation.               │
│ S15   │ Expression Policy & Actuation     │ ExpressionPolicy generates 15D vector.     │
│ S16   │ Post-Turn Persistence & Adapt     │ [PHASE 20 CO-ENCODING]:                    │
│       │ 16.1 Affective Memory Store       │ Snapshot s_slow in R^16 from EmotionCore;  │
│       │                                   │ store (content, pad_final, s_slow) into    │
│       │                                   │ MemoryTrace.                               │
│       │ 16.2 Plasticity Tagging           │ LNNTrainer salience queueing.              │
│       │ 16.3 Knowledge Extraction         │ Structured fact extraction.                │
│       │ 16.4 Relationship Update          │ Update R_t with turn signals.              │
│       │ 16.5 Dialog History Append        │ Save turn to ephemeral chat history.       │
└───────┴───────────────────────────────────┴────────────────────────────────────────────┘
```

---

## 4. Detailed Mathematical Formulation & Contraction Bounds

### 4.1 Production Slow-Field State Equation with Recollection Forcing

The continuous slow differential equation in production becomes:

$$\frac{d\mathbf{s}_s}{dt} = -\frac{\mathbf{s}_s - \mathbf{s}^*_{\text{philia}}}{\tau_{\text{slow, decay}}} + \frac{\tanh\Big(\mathbf{W}_{sf} \mathbf{h}_f + \mathbf{W}_{sh} \Delta\mathbf{m} + \mathbf{W}_{\text{rec}} \mathbf{r}_{\text{slow}}^{\text{bounded}}(t)\Big)}{\tau_{\text{slow, charge}}}$$

With canonical production parameters:
- $\tau_{\text{slow, decay}} = 28.00\text{ s}$
- $\tau_{\text{slow, charge}} = 3.50\text{ s}$
- $\mathbf{W}_{\text{rec}} = 0.35 \cdot \mathbf{I}_{16} \in \mathbb{R}^{16 \times 16}$ (diagonal, non-mixing recollection coupling)
- $\mathbf{s}^*_{\text{philia}} = [0.20, -0.05, 0.05, 0, \dots, 0]^T \in \mathbb{R}^{16}$

### 4.2 Multi-Modal Scoring & Competitive Softmax Gating (Stage 6)

For stored traces $i \in \{1, \dots, K\}$ in `AffectiveMemory`:
1. **Multi-Modal Affinity Score**:
   $$S_i = 0.60 S_{\text{sem}}^{(i)} + 0.25 S_{\text{aff}}^{(i)} + 0.15 S_\sigma^{(i)}$$
   - $S_{\text{sem}}^{(i)} = \cos(\mathbf{e}_{\text{cue}}, \mathbf{e}_{\text{content}}^{(i)}) \in [-1, 1]$: Semantic cosine similarity between current stimulus content vector and stored trace content.
   - $S_{\text{aff}}^{(i)} = \cos(\mathbf{p}_{\text{final}}, \mathbf{p}_{\text{tag}}^{(i)}) \in [-1, 1]$: Affective cosine similarity between current committed PAD and trace PAD tag.
   - $S_\sigma^{(i)} = \text{decay\_weight}^{(i)} \cdot \exp\left(-\frac{\Delta t^{(i)}}{\tau_{\text{recency}}}\right)$: Salience-decay viability from `DecayEngine`.
2. **Competitive Activation Gating**:
   Candidates exceeding pre-registered threshold $\theta_{\text{gate}} = 0.50$ compete via softmax with temperature $\tau_{\text{comp}} = 0.20$:
   $$\alpha_i = \begin{cases} \frac{\exp\left(\frac{S_i - \theta_{\text{gate}}}{\tau_{\text{comp}}}\right)}{\sum_{j \in \mathcal{A}} \exp\left(\frac{S_j - \theta_{\text{gate}}}{\tau_{\text{comp}}}\right)} & \text{if } i \in \mathcal{A} = \{k \mid S_k \ge \theta_{\text{gate}}\} \\ 0 & \text{if } i \notin \mathcal{A} \end{cases}$$
3. **Bounded Forcing Synthesis**:
   $$\mathbf{r}_{\text{slow}} = \sum_{i \in \mathcal{A}} \alpha_i \mathbf{s}_{\text{enc}}^{(i)}$$
   $$\mathbf{r}_{\text{slow}}^{\text{bounded}} = \text{clip}(\mathbf{r}_{\text{slow}}, -0.85, +0.85)$$
   If $\mathcal{A} = \emptyset$ (no candidate meets $\theta_{\text{gate}} = 0.50$), $\mathbf{r}_{\text{slow}}^{\text{bounded}} \equiv \mathbf{0} \in \mathbb{R}^{16}$.

### 4.3 Rectangular Pulse Window vs. Temporal Persistence (Clarification)

> [!IMPORTANT]
> **External Forcing Window vs. Affective Dynamics**:  
> The parameter `recollection_pulse_duration_sec = 4.0` specifies **strictly the active rectangular time window during which exogenous forcing is applied**:
> $$\mathbf{r}_{\text{slow}}^{\text{bounded}}(t) = \begin{cases} \mathbf{r}_{\text{slow}}^{\text{bounded}} & \text{for } t_{\text{inject}} \le t < t_{\text{inject}} + T_{\text{pulse}} \\ \mathbf{0} & \text{for } t \ge t_{\text{inject}} + T_{\text{pulse}} \end{cases}$$
> **This does NOT mean the affective consequence expires after 4.0 seconds.**  
> - During $T_{\text{pulse}} = 4.0\text{ s}$, the slow field is charged through the attack time-constant $\tau_{\text{slow, charge}} = 3.50\text{ s}$.
> - Once $t \ge t_{\text{inject}} + T_{\text{pulse}}$, exogenous forcing drops to zero, but the internal latent displacement $\mathbf{s}_s(t) - \mathbf{s}^*_{\text{philia}}$ persists autonomously within the slow field.
> - The displacement dissipates smoothly under the natural unforced slow relaxation time-constant $\tau_{\text{slow, decay}} = 28.00\text{ s}$, yielding an observed half-life of $t_{1/2} \approx 32.1\text{ s}$ and perceptible retention exceeding $50.0\text{ s}$.
> - Persistence is an emergent property of the MT-LNN slow dynamical layer, not an artificial timer hold.

### 4.4 Bounded Scientific Statement on Contraction Invariant

> [!NOTE]
> **Bounded Dissipative/Contraction Invariant (Scientific Scope)**:  
> In the unforced coupled MT-LNN, the system Jacobian $J \in \mathbb{R}^{48 \times 48}$ satisfies $\text{Tr}(J) \le -40.0$, indicating strong local volume contraction.  
> Because the recollection forcing term $\mathbf{W}_{\text{rec}} \mathbf{r}_{\text{slow}}^{\text{bounded}}(t)$ is an **exogenous time-dependent input** (i.e. $\mathbf{r}_{\text{slow}}$ does not depend on current $\mathbf{s}_s$ or $\mathbf{h}_f$), its partial derivative with respect to internal state is zero: $\frac{\partial (\mathbf{W}_{\text{rec}} \mathbf{r}_{\text{slow}})}{\partial \mathbf{s}_s} = \mathbf{0}$.  
> Therefore, recollection forcing **does not add positive diagonal feedback to the system Jacobian**, supporting the experimentally validated dissipative and contractive regime under tested parameter bounds.  
> **Scientific Boundary**: This property guarantees strong dissipative damping and rapid asymptotic return to the Philia attractor under tested operating conditions. **It does not constitute a global mathematical proof excluding all limit cycles, strange attractors, or chaotic behavior across unconstrained parameter space or extreme out-of-distribution inputs.** Boundedness is guaranteed deterministically by the explicit $\tanh$ and $\text{clip}$ operators.

---

## 5. Architectural Decoupling: Memory Provider vs. Orchestrator Actuator

To maintain Lucia's strict architectural separation of concerns, the memory subsystem is strictly prohibited from directly actuating or modifying `EmotionCore`:

```text
┌────────────────────────────────────────────────────────────────────────────────────────┐
│                        ARCHITECTURAL DECOUPLING CONTRACT                               │
│                                                                                        │
│   [Stage 6: EcphoryEngine / AffectiveMemory]                                           │
│       │                                                                                │
│       │ Evaluates similarity, applies gating, packages state                           │
│       ▼                                                                                │
│   RecollectionResult (Immutable Frozen Dataclass)                                      │
│     ├─ is_active: bool                                                                 │
│     ├─ affinity_score: float                                                           │
│     ├─ matched_trace_id: Optional[int]                                                 │
│     ├─ r_slow_bounded: np.ndarray (shape 16, float32)                                  │
│     └─ echo_vector: Optional[np.ndarray] (shape M, float32)                             │
│       │                                                                                │
│       ▼                                                                                │
│   [CognitiveOrchestrator (Stage 6 Execution Authority)]                                │
│       │                                                                                │
│       ├─ Evaluates system state: is feature enabled? Is system degraded?               │
│       ├─ If active & healthy: calls self._emotion_core.inject_recollection(...)        │
│       └─ Passes echo_vector to Stage 7 & 11; passes pacing delta to Stage 12           │
│                                                                                        │
│   RULE: AffectiveMemory NEVER imports or references EmotionCore.                       │
│   RULE: EcphoryEngine NEVER actuates limbic state directly.                            │
│   RULE: CognitiveOrchestrator owns all inter-subsystem control decisions.              │
└────────────────────────────────────────────────────────────────────────────────────────┘
```

### Typed Data Contract:
```python
@dataclass(frozen=True)
class RecollectionResult:
    """Structured result emitted by memory retrieval in Stage 6."""
    is_active: bool
    affinity_score: float
    matched_trace_id: Optional[int]
    r_slow_bounded: np.ndarray  # shape (16,), float32, bounded in [-0.85, 0.85]
    echo_vector: Optional[np.ndarray]  # shape (M,), float32
```

---

## 6. Legacy Compatibility Approximation (PAD $\to$ Slow Fallback)

### 6.1 Nature of the Fallback
Memories recorded prior to Phase 20 contain 3D PAD tags but lack the 16-dimensional slow-field latent vector $\mathbf{s}_{\text{enc}}$.
When loading or querying such a legacy trace, the memory subsystem computes a deterministic fallback vector:

$$\mathbf{s}_{\text{fallback}} = \text{clip}\Big(\mathbf{W}_{\text{pad}\to\text{slow}} (\mathbf{p}_{\text{tag}} - \mathbf{p}^*_{\text{philia}}) + \mathbf{s}^*_{\text{philia}}, -0.85, +0.85\Big)$$

Where $\mathbf{W}_{\text{pad}\to\text{slow}} \in \mathbb{R}^{16 \times 3}$ is a fixed orthogonal pseudo-inverse mapping:
$$\mathbf{W}_{\text{pad}\to\text{slow}}[0, 0] = 0.60, \quad \mathbf{W}_{\text{pad}\to\text{slow}}[1, 1] = 0.60, \quad \mathbf{W}_{\text{pad}\to\text{slow}}[2, 2] = 0.50$$
All other elements are zero.

### 6.2 Explicit Classification & Acceptance Requirements

> [!WARNING]
> **Deterministic Compatibility Approximation, NOT Equivalent Reconstruction**:  
> As demonstrated in Phase 20 Ablation A4, linear projection from 3D PAD coordinates recovers only a coarse projection of the 16-dimensional slow manifold ($L_2\text{ reconstruction error} = 0.428 > 0.05$).  
> **This fallback is explicitly classified as a deterministic compatibility approximation, not equivalent affective reconstruction.**  
> It exists solely to provide graceful degradation for historical traces without triggering database schema crashes or state corruption.

### Fallback Acceptance & Safety Requirements:
1. **Boundedness**: For all $\mathbf{p}_{\text{tag}} \in [-1.0, 1.0]^3$, $\|\mathbf{s}_{\text{fallback}}\|_\infty \le 0.85$ strictly.
2. **Determinism**: For identical $\mathbf{p}_{\text{tag}}$, the function returns bit-exact identical vectors ($\Delta < 10^{-12}$).
3. **Philia Resting Invariance**: For $\mathbf{p}_{\text{tag}} = \mathbf{p}^*_{\text{philia}} = [0.25, -0.05, 0.05]$, $\mathbf{s}_{\text{fallback}} = \mathbf{s}^*_{\text{philia}}$ bit-exact (zero spurious energy injected into resting state).
4. **Safety Under NaN / Inf**: If $\mathbf{p}_{\text{tag}}$ contains non-finite values, fallback returns $\mathbf{s}^*_{\text{philia}}$ defensively.

---

## 7. Concurrency, Lock Hierarchy & Thread Safety

All threads must adhere strictly to the audited production lock hierarchy ([`src/core/emotion/emotion_core.py:19-24`](file:///c:/Users/Lunafiah/Desktop/My_project/Lucia/src/core/emotion/emotion_core.py)):

```text
┌────────────────────────────────────────────────────────────────────────────────────────┐
│                        CANONICAL PRODUCTION LOCK HIERARCHY                             │
│                                                                                        │
│   1. _turn_lock      (Non-reentrant Lock; serializes S1–S16 cognitive turn execution)  │
│   2. _index_lock     (RLock in AffectiveMemory; protects trace index reads/writes)     │
│   3. _step_lock      (Lock in EmotionCore; serializes ODE numerical integration ticks) │
│   4. _train_lock     (Lock in EmotionCore; protects atomic LNN weight swaps <= 2ms)    │
│   5. _stimulus_lock  (Lock in EmotionCore; protects FIFO pending stimulus queue)       │
│   6. _state_lock     (Lock in EmotionCore; protects ephemeral PAD/slow state <= 1ms)   │
│                                                                                        │
│   CRITICAL CONCURRENCY INVARIANTS:                                                     │
│   - Never acquire _train_lock while holding _state_lock.                               │
│   - Never acquire _index_lock while holding _state_lock.                               │
│   - Hold times under _state_lock must remain strictly <= 1.0 ms (fast array copy).    │
│   - Never perform disk I/O, LLM inference, or IPC calls while holding ANY lock.      │
│   - Multi-modal retrieval scoring (Stage 6) runs under _index_lock, NOT _state_lock.  │
└────────────────────────────────────────────────────────────────────────────────────────┘
```

### Accessor Latencies:
- `EmotionCore.inject_recollection(r_slow, duration)`: Holds `_state_lock` for $< 0.1\text{ ms}$ to update `_recollection_forcing` array and expiry timestamp.
- `EmotionCore.get_slow_latent_state()`: Holds `_state_lock` for $< 0.1\text{ ms}$ to copy `np.array(self._s_slow, copy=True)`.

---

## 8. Data Persistence, Storage Overhead & Storage Integrity

### 8.1 In-Memory & On-Disk Trace Schema
- `MemoryTrace` dataclass extended with: `slow_latent_trace: Optional[np.ndarray] = None` (shape (16,), dtype `float32`).
- Storage footprint: $16 \times 4\text{ bytes} = 64\text{ bytes}$ per episode.
- 1,000 interaction episodes require strictly **$64\text{ KB}$** in memory.
- **Zero GPU VRAM impact**: All memory traces reside in CPU RAM.

### 8.2 Canonical Storage Isolation
- Canonical runtime file [`data/profile.json`](file:///c:/Users/Lunafiah/Desktop/My_project/Lucia/data/profile.json) remains permanently bit-exact `{"is_onboarded": false}`.
- Automated tests are strictly prohibited from touching `data/` runtime files. All test fixtures execute in ephemeral in-memory stores or temporary directories (`tmp_path`).

---

## 9. Rollback & Fail-Safe Strategy

### 9.1 Pre-Implementation Git Baseline
- The exact pre-implementation baseline commit is **`c23fe7e`** (`feat(core): implement Phase 19 Multi-Timescale Affective Life & Temporal Continuity (MT-LNN)`).
- In the event of an unrecoverable architectural defect, executing `git reset --hard c23fe7e` restores the clean, fully validated Phase 19 production state.

### 9.2 Instant Feature Flag Rollback
To eliminate deployment risk, a runtime feature flag is added to `EmotionConfig` and `config/ui.json`:
```json
{
  "enable_affective_recollection": false
}
```
When `enable_affective_recollection` is `false`:
1. Stage 6 evaluates `RecollectionResult` but `CognitiveOrchestrator` skips dispatching `inject_recollection()`.
2. `EmotionCore` maintains $\mathbf{r}_{\text{slow}} \equiv \mathbf{0}$.
3. Stage 12 pacing latency delta $\Delta\tau_{\text{pace}} \equiv 0.0\text{ ms}$.
4. The system operates identically to the baseline Phase 19 MT-LNN with zero code changes required.

---

## 10. Verification Gates & Acceptance Protocol

Following Architecture Gate approval, production implementation must pass four sequential gates before completion:

```powershell
# Gate 1: Unit Test Suite (Subsystem Level)
.venv\Scripts\pytest tests/unit/test_emotion_core.py -v
.venv\Scripts\pytest tests/unit/test_affective_memory.py -v
.venv\Scripts\pytest tests/unit/test_cognitive_orchestrator.py -v

# Gate 2: Invariant & Concurrency Verification
.venv\Scripts\pytest tests/property -v

# Gate 3: Experimental Suite Regression Verification
.venv\Scripts\pytest tests/evaluation_phase19 tests/evaluation_phase20 -v

# Gate 4: Full System Production Regression
.venv\Scripts\pytest tests/unit -v
powershell -Command "Get-Content data/profile.json -Raw"
# Must return bit-exact: {"is_onboarded": false}
```

---

## 11. Architecture Gate Readiness & Sign-Off Statement

### Implementation Readiness Declaration:
- **Phase 19 Parameters**: 100% audited and aligned with `src/core/config.py` ($\tau_{\text{charge}} = 3.50\text{ s}, \tau_{\text{decay}} = 28.00\text{ s}$).
- **Pipeline Mapping**: 100% mapped to locked S1–S16 stages without renumbering or redefining.
- **Scientific Claims**: Jacobian volume contraction scoped to validated parameter domain; no unverified claims of global chaos exclusion.
- **Fallback Classification**: Explicitly classified as a deterministic compatibility approximation with strict safety/boundedness criteria.
- **Architectural Decoupling**: Memory produces typed `RecollectionResult`; CognitiveOrchestrator owns actuation.
- **Pulse Duration**: Clarified as rectangular forcing window (4.0s) distinct from emergent multi-minute persistence ($t_{1/2} \approx 32.1\text{ s}$).
- **Production Code Freeze**: Strictly zero modifications made to `src/core/**` or `electron/**`.

**The revised Phase 20 Production Realization Architecture Design is submitted for final Architecture Gate review.**
