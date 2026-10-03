# Phase 22-X — Research Specification: Non-Generative Probabilistic User Belief & Predictive Inference

> **Research Branch Specification**: Phase 22-X (Positioned between Phase 22 and Phase 23)  
> **Topic**: Non-Generative Probabilistic Decision Layer, User Belief State Dynamics & Predictive Inference  
> **Status**: `[CURRENT RESEARCH]` | **Production Implementation**: `NOT AUTHORIZED`  
> **Governance Authority**: `AGENTS.md` §0, §6, §7; `docs/00_PROJECT_OVERVIEW.md` §3.1; `docs/L1_INVARIANTS.md` §6  
> **Production Code Mutations**: Exactly 0 (`src/core/**` and `electron/**` strictly untouched)  
> **Genesis Gate**: Preserved bit-exact (`data/profile.json == {"is_onboarded": false}`)  
> **Date**: September 2026

---

## 1. Executive Summary & Context

Lucia has established a verified production baseline through **Phase 21 — Long-Term Relational Consolidation & Synaptic Homeostasis** (commit `58a509c`). Within Lucia's canonical architecture, the companion's continuous internal limbic, homeostatic, and affective dynamics are modeled with mathematical rigor (Coupled MT-LNN ODE, Kanerva SDM, and offline CPU BPTT).

However, current architecture lacks an explicit dynamical formulation of the **user as an external, partially observed dynamical system**. 

To bridge this gap, a dedicated research branch—**Phase 22-X**—is recognized between Phase 22 (Active Inference & Epistemic Foraging) and Phase 23 (Continuous Semantic State). 

> [!IMPORTANT]
> **P22-X GOVERNANCE STATUS**:  
> Phase 22-X is classified as **`[CURRENT RESEARCH]`** and is **STRICTLY NOT APPROVED FOR PRODUCTION IMPLEMENTATION**.  
> It does NOT modify `src/core/`, the canonical 16-stage cognitive pipeline (S1–S16), or the Genesis onboarding gate.

---

## 2. Central Research Question & Non-Generative Primitive Hypothesis

### The Central Hypothesis
The research question of Phase 22-X is **NOT**:
> *"Jev/Laya is Lucia's brain."* (Strictly rejected).

Rather, the question is:
> **"Can a calibrated non-generative decision layer provide reliable observations, uncertainty estimates, and semantic hypotheses that can feed a persistent user-belief and predictive inference system?"**

### Observed Cognitive Pipeline Gap
While Lucia possesses an internal physiological state space ($P, A, D, \mathbf{h}_{\text{fast}}, \mathbf{s}_{\text{slow}}, \mathcal{E}, \mathcal{C}, \mathcal{T}$), the system currently lacks formal mechanisms for modeling the user's latent cognitive and communicative trajectory:
1. **User Belief State ($\mathbf{b}_{\text{user}}$)**: A principled probability distribution over latent user states.
2. **Persistent User Belief**: Beliefs that persist, update, and decay across turns with temporal consistency.
3. **Recursive Bayesian / Probabilistic Updating**: Exact or variational belief updates given noisy evidence.
4. **User-State Temporal Dynamics**: State transition models capturing user intention drift and affective momentum.
5. **Multi-Step Intent Prediction**: Lookahead modeling of prospective conversational goals.
6. **Prediction Tree / Bounded Hypothesis Expansion**: Branching hypothesis trees evaluated over short horizons ($H \in [1, 3]$).
7. **Explicit Uncertainty Representation**: Information-theoretic entropy ($H(\mathbf{b}_{\text{user}})$) and confidence intervals.
8. **Prospective Epistemic Action Selection**: Connecting information gain directly to conversational policy.

### Role of Jev/Laya-like Primitives
In this architecture, Jev/Laya is conceptualized as a **calibrated non-generative decision sensor**, rather than an autonomous cognitive agent:
- Fast, low-latency CPU-compatible classification ($\le 2\text{ms}$).
- Calibrated probability distributions over predefined pragmatic/semantic hypotheses.
- Explicit decision uncertainty (entropy / margins).
- Strictly non-generative: operates without sampling natural-language LLM tokens.

---

## 3. Evidence Hierarchy & Epistemological Boundaries

To ensure scientific rigor, claims regarding P22-X are classified across three strict epistemological tiers:

### 3.1 Tier 1: Proven / Empirically Supported (Literature & Existing Harnesses)
- Calibrated discriminative models can emit well-calibrated posterior probabilities over structured decision spaces.
- Recursive Bayesian filtering (e.g. discrete filters, Kalman/particle approximations) maintains stable belief distributions over partially observed latent states.
- Active inference and Expected Free Energy (EFE) provide formal mathematical criteria for trading off pragmatic value against epistemic information gain.
- Non-generative decision primitives operate on CPU with minimal resource footprints and zero token-generation overhead.

### 3.2 Tier 2: Plausible but Not Yet Validated for Lucia
- Probabilistic outputs from a Jev/Laya-like model can serve as clean sensory likelihood evidence $P(y \mid x_{\text{user}})$ for a Bayesian User Belief filter.
- A language-independent decision representation can cleanly interface with Lucia's future semantic state representations.
- A bounded short-horizon prediction tree ($H \le 3$, branching factor $\le 4$) can execute within Lucia's strict 20-Watt CPU computational budget ($\le 10\text{ms}$).

### 3.3 Tier 3: Speculative / High-Risk Hypotheses
- A full closed loop (`Observation → Jev/Laya Primitive → Belief Update → Latent Dynamics → EFE Selection → Action → New Observation`) remains dynamically stable across multi-turn interactions without pathological feedback oscillations or deadlocks.
- A discrete decision ontology is sufficiently expressive to capture nuanced, open-ended human intention without artificial communicative distortion.

---

## 4. Architectural Boundaries: Independence of P22-X and P23

Phase 22-X and Phase 23 address complementary but distinct architectural questions:

| Dimension | Phase 22-X (User Belief & Predictive Inference) | Phase 23 (Continuous Semantic State) |
|---|---|---|
| **Core Question** | *How can Lucia infer, maintain uncertainty over, and predict latent user state and intent?* | *How can Lucia represent semantic state in a continuous, language-independent substrate?* |
| **Domain** | External agent modeling, POMDP belief updates, intent lookahead. | Internal representation, continuous vector embeddings, non-token conceptual state. |
| **Status** | `[CURRENT RESEARCH]` | `[CONCEPTUAL HORIZON]` |

### Decoupled Interface Boundary
The hypothesized research pipeline decouples P22-X from P23:

```text
User Multimodal Observation
            ↓
Jev/Laya-like Calibrated Decision Layer  (Sensor / Calibrated Primitive)
            ↓
Probabilistic Likelihood Evidence
            ↓
User Belief State (Recursive Bayesian Filter)
            ↓
Temporal / Latent User Dynamics
            ↓
Prediction / Hypothesis Tree (Bounded Horizon)
            ↓
Intent / Future-State Prediction
            ↓
Semantic State Interface
            ↓
[Phase 23 Continuous Semantic State]
```

> [!CAUTION]
> **ARCHITECTURAL INDEPENDENCE DIRECTIVE**:  
> Phase 23 **MUST NOT** be made dependent on Jev/Laya or P22-X.  
> If P22-X succeeds, its calibrated intent predictions may serve as an upstream input to Phase 23.  
> If P22-X is rejected or fails stability criteria, Phase 23 remains viable using alternative continuous representation mechanisms.

---

## 5. Research Discipline & Comparative Baseline Architecture

Agents and researchers investigating Phase 22-X must not assume Jev/Laya is the sole or necessary solution. Evaluation protocols must benchmark Jev/Laya against established alternative primitives:

1. **Standard Calibrated Discriminative Classifiers**: Temperature-scaled logistic / MLP heads.
2. **Bayesian Filtering / POMDP Dialogue-State Trackers**: Classical particle/histogram belief trackers.
3. **Reward / Preference Estimators**: Bradley-Terry / DPO-style scalar preference heads.
4. **Probabilistic State Estimators**: Linear Gaussian / unscented estimators over continuous user vectors.
5. **Non-Generative Heuristic Primitives**: Structured rule-based classifiers with calibrated softmax outputs.

The primary objective is to evaluate whether Jev/Laya offers a uniquely beneficial trade-off in calibration, CPU latency, and entropy estimation, or merely serves as one instance of a general non-generative decision primitive.

---

## 6. Immediate Research Priority

The immediate research focus for Phase 22-X is not tuning classifier architectures in isolation, but investigating the foundational cognitive bridge:

$$\text{\bf Calibrated Observation} \longrightarrow \text{\bf User Belief Filter} \longrightarrow \text{\bf Latent Temporal Dynamics} \longrightarrow \text{\bf Intent Prediction Tree}$$

All experimental investigations must be executed in isolated research harnesses under `tests/evaluation/phase22/` or designated P22-X fixtures, preserving complete production code isolation (`production diff = 0`) and the locked Genesis gate.
