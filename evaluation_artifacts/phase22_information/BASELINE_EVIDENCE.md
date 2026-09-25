# BASELINE EVIDENCE RECONSTRUCTION — Phase 22-AL to Phase 22-INF

> **Document Type:** Canonical Baseline Evidence Ledger  
> **Status:** Authoritative Experimental Evidence  
> **Scope:** Phase 22-AL (Observation-to-Latent Alignment Study) Synthesis for Phase 22-INF (Information Sufficiency & Semantic State Formation Study)

---

## 1. Verified & Supported Experimental Findings

The following empirical measurements are mathematically verified in canonical JSON artifacts and preserved as immutable baselines:

| Metric / Finding | Measured Value | Evidentiary Status | Source Artifact |
| :--- | :---: | :---: | :--- |
| **Real Laya ModernBERT Parameters** | 421.4M params | `VERIFIED` | `evaluation_artifacts/phase22_xr_laya/` |
| **Real Laya CPU P50 Latency** | 607.67 ms | `VERIFIED` | `evaluation_artifacts/phase22_xr_laya/` |
| **Real Laya ECE Calibration** | 0.2232 | `VERIFIED` | `evaluation_artifacts/phase22_xr_laya/` |
| **Continuous Belief Flapping Rate** | 0.40% (vs discrete 23.8%) | `SUPPORTED` | `evaluation_artifacts/phase22_xr/` |
| **Contradiction Recovery Velocity** | 1.0 turn | `SUPPORTED` | `evaluation_artifacts/phase22_xr/` |
| **Calibrated Trajectory Coverage** | 100.0% | `SUPPORTED` | `evaluation_artifacts/phase22_xr/` |
| **A0 Naive Zero-Shot Alignment** | Deeply Negative ($R^2 \in [-4.2341, -0.6355]$) | `FAILED` | `evaluation_artifacts/phase22_alignment/` |
| **A1 Linear Learned Projection** | Rescues baseline ($R^2 \in [+0.0365, +0.2231]$) | `SUPPORTED` | `evaluation_artifacts/phase22_alignment/` |
| **A5 Leaky State Estimator** | Peak C4 Held-Out Alignment (**$R^2 = +0.2548$**) | `SUPPORTED` | `evaluation_artifacts/phase22_alignment/` |
| **Raw Window Concatenation ($k \in [1, 10]$)** | Monotonic degradation ($R^2 = +0.2240 \to -0.0533$) | `FAILED` | `evaluation_artifacts/phase22_alignment/` |
| **State Formation CPU Latency** | 0.0031 ms P50 (A5) to 0.0446 ms (A6) | `VERIFIED` | `evaluation_artifacts/phase22_alignment/` |
| **Oracle Sensor Alignment** | **$R^2 = +0.9018$**, MSE = 0.0025 | `VERIFIED` | `evaluation_artifacts/phase22_alignment/` |
| **G_AL1 Preregistered Gate ($R^2 \ge 0.85$)** | Failed across all candidates ($R^2_{\max} = 0.2548$) | `FAILED` | `evaluation_artifacts/phase22_alignment/` |
| **G_AL2 Falsification Gate ($R^2 < 0.70$)** | Triggered ($0.2548 < 0.70$) | `FALSIFIED` | `evaluation_artifacts/phase22_alignment/` |

---

## 2. Explicitly Unresolved Questions (Phase 22-INF Mandate)

The completion of Phase 22-AL established that the failure of C1–C6 representations is an **Information Bottleneck**, but left open the exact nature of the missing information.

The following questions are **UNKNOWN** and must be resolved by Phase 22-INF:

1. **What exact information is absent from turn-level observations?**
   - Is it continuous frame-level temporal dynamics (F0, RMS, pause duration, speaking rate)?
   - Is it conversational interaction dynamics (turn-taking latency, interruption, response timing)?
   - Is it cross-modal complementarity (synergy between acoustic energy and lexical semantics)?
   - Is it persistent relational memory/context (accumulated interaction state)?
2. **Is the 6-dimensional synthetic OU latent state itself identifiable?**
   - Are all 6 dimensions ($z_0$ cognitive load, $z_1$ valence, $z_2$ agency, $z_3$ urgency, $z_4$ fatigue, $z_5$ relational warmth) observable from non-invasive human cues?
   - Do certain dimensions suffer from structural unidentifiability (e.g., latent fatigue without physical exertion metrics)?
3. **What is the minimal sufficient perceptual stream for Semantic State Formation?**
   - Does adding multimodal, temporal, interaction, and relational features bridge the gap to $R^2 \ge 0.85$?
   - Or does the bottleneck require redefining the continuous semantic state $\boldsymbol{\psi}_{\text{user}} \in \mathbb{R}^{12}$ for P23?

---

## 3. Preregistered Epistemological Distinctions

- `VERIFIED`: Deterministically measured on held-out seeds with zero data leakage.
- `SUPPORTED`: Statistically validated across multiple seeds and stress regimes under controlled evaluation.
- `FAILED`: Explicitly failed a preregistered architecture or performance gate.
- `UNKNOWN`: Not yet experimentally isolated; requires hypothesis-driven ablation in Phase 22-INF.
- `HYPOTHESIS`: Theoretical conjecture to be tested without assumption of success.
