# ARCHITECTURE DECISION RECORD: PHASE 22-XR RESEARCH CLOSURE & DIRECTION

> **Decision Record:** ADR-P22XR-01  
> **Status:** APPROVED AS RESEARCH DIRECTIVE (NON-PRODUCTION)  
> **Date:** September 2026  
> **Scope:** Lucia Cognitive Architecture — Layer 4 / User Belief Modeling  

---

## 1. Context & Problem Statement

Phase 22-XR investigated continuous user-belief dynamics, multi-step trajectory density forecasting, and empirical evaluation of the **Real Laya** (`convaiinnovations/laya`, ModernBERT-large 421M params) neural backbone.

The empirical findings from genuine CPU inference established that:
1. **Continuous dynamics are highly effective:** Kalman-filtered belief tracking reduced flapping from $23.80\%$ to $0.40\%$ and achieved $1.0\text{ turn}$ contradiction recovery.
2. **Real Laya is unviable for edge execution:** ModernBERT-large requires $607.67\text{ ms}$ (P50) on CPU and exhibits an $ECE$ of $0.2232$, violating edge latency ($\le 350\text{ ms}$) and calibration ($\le 0.15$) constraints.
3. **Alignment requires dedicated projection:** Mapping observation outputs to latent states achieved $R^2 = +0.4051$ with log-odds mapping, but fell short of the $0.85$ target.

A formal architectural decision is required to dictate what elements are retained, what components are rejected from promotion, and where future research must focus.

---

## 2. Decision Summary

```text
+-----------------------------------------------------------------------------+
|                               WHAT WE RETAIN                                |
|  - Continuous User State Representation (z in R^6)                          |
|  - Continuous Temporal Belief Dynamics (ODE / Continuous-Discrete Filter)   |
|  - Principled Epistemic Uncertainty Representation (Covariance Sigma)       |
|  - Multi-Step Trajectory Density Forecasting (Lyapunov-Matched Diffusion)   |
|  - Expected Information Gain (EIG) / Epistemic Action Selection Logic       |
|  - 12D User-State Interface Concept: psi_user = [mu_z, diag(Sigma_z)] in R^12 |
|  - Language-Independent Downstream Latent Representation                    |
+-----------------------------------------------------------------------------+
                                       |
                                       v
+-----------------------------------------------------------------------------+
|                            WHAT WE DO NOT PROMOTE                           |
|  - Real Laya / ModernBERT-large as a mandatory observation encoder          |
|  - ModernBERT-large CPU inference as the required production path           |
|  - Raw Laya classification simplex directly as user-state coordinates       |
|  - Any production modification to src/core/** or electron/**                |
+-----------------------------------------------------------------------------+
                                       |
                                       v
+-----------------------------------------------------------------------------+
|                                RESEARCH NEXT                                |
|  - Initiate: OBSERVATION LAYER REPLACEMENT STUDY                            |
|  - Investigate alternative, lightweight, calibrated observation encoders    |
|  - Decouple Observation Encoder from Continuous Dynamics                    |
|  - Maintain strict separation: Observation != Cognition != Language         |
+-----------------------------------------------------------------------------+
```

---

## 3. Detailed Architectural Principles

### 3.1 Retained Core Concepts (Research Validated)
1. **Continuous Latent Representation:**
   The user's relational, cognitive, and communicative state is fundamentally continuous. Discretizing user traits into categorical buckets creates boundary oscillation and high flapping. The continuous formulation $\mathbf{z}(t) \in \mathbb{R}^6$ is retained as a permanent research foundation.
2. **Dynamical Temporal Filtering:**
   Belief tracking must proceed via continuous prior integration ($\dot{\mathbf{z}} = \mathbf{F}\mathbf{z} + \mathbf{w}$) and discrete observation updates ($\mathbf{K}_k = \mathbf{P}_k \mathbf{H}^T (\mathbf{H}\mathbf{P}_k \mathbf{H}^T + \mathbf{R})^{-1}$). This architecture guarantees mathematical stability and rapid contradiction recovery.
3. **Trajectory Density Forecasting:**
   Propagating future user trajectories using Lyapunov-matched diffusion yields $100\%$ calibrated coverage without covariance explosion ($\log \det$ ratio $= 0.53$). This provides a sound basis for proactive conversational planning.
4. **Decoupled Interface Contract:**
   The user belief state exposes an invariant contract:
   $$\boldsymbol{\psi}_{\text{user}}(t) = \begin{bmatrix} \boldsymbol{\mu}_{\mathbf{z}}(t) \\ \text{diag}(\boldsymbol{\Sigma}_{\mathbf{z}}(t)) \end{bmatrix} \in \mathbb{R}^{12}$$
   Downstream components (dialogue policy, epistemic action selection, avatar non-verbal expressions) consume $\boldsymbol{\psi}_{\text{user}}$ without knowledge of the upstream observation encoder.

### 3.2 Non-Promoted Components (Rejected for Production)
1. **Real Laya / ModernBERT-Large:**
   At 421 million parameters, the computational footprint ($607.67\text{ ms}$ on CPU) consumes over $75\%$ of the total conversational budget. Furthermore, uncalibrated softmax logits ($ECE = 0.2232$) induce erratic observation updates. It is permanently excluded from mandatory production deployment.
2. **Direct Simplex Mapping:**
   Directly treating observation probabilities $\mathbf{y} \in \Delta^K$ as latent coordinates $\mathbf{z}$ is an architectural anti-pattern ($R^2 = -25.13$). Any future observation layer must incorporate an explicit forward/inverse measurement operator $g(\mathbf{z})$ or calibration projection.

---

## 4. Next Research Mandate: Observation Layer Replacement Study

The next research phase is designated as the **Observation Layer Replacement Study**.

The primary question is defined as:
> **"What observation layer can transform multimodal/language input into sufficiently informative, calibrated, temporally stable semantic evidence for Lucia's continuous user-state dynamics while satisfying realistic latency and resource constraints?"**

This study will evaluate candidate observation classes (small multilingual sentence encoders, distilled representations, acoustic prosody, structured semantic representations, and learned projection layers) against pre-registered benchmarks. No candidate will be declared a winner until empirical evaluation is complete.

---

## 5. Architectural Invariants Maintained

- **One Continuous Life:** The user state is an evolving continuum, never reset by UI actions.
- **Strict Concurrency Discipline:** All belief filtering updates execute in $\le 0.2\text{ ms}$, safely within thread lock bounds.
- **Zero Cloud Dependencies:** All candidate observation architectures must be capable of $100\%$ local edge execution on standard consumer CPU/GPU hardware.
- **Genesis Gate Integrity:** `data/profile.json` remains strictly untouched.
