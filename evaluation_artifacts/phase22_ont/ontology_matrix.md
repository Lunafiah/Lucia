# Target Ontology Matrix & Comparative Analysis — Phase 22-ONT

## 1. Overview & Research Scope

Phase 22-ONT directly addresses the root-cause diagnosis from Phase 22-EKF:
> **"Does redesigning the target ontology from a monolithic 6D state into multi-timescale decoupled layers solve the continuous state alignment bottleneck?"**

We evaluated three explicit ontology variants across **held-out generalization seeds (1024, 2026)** and 6 stress regimes:
- **Ontology 1 (O1 — Legacy 6D):** Monolithic 6D state ($z_0..z_5$) regressed jointly at single turn timescale.
- **Ontology 2 (O2 — Decoupled 4D+2D):** Layer A: 4D Observable Interaction State ($\mathbf{u} \in \mathbb{R}^4$) regressed from turn features + Layer B: 2D Slow Memory ($\mathbf{m} \in \mathbb{R}^2$) accumulated via open-loop heuristic rules.
- **Ontology 3 (O3 — Multi-Timescale Consolidation):** Layer A: 4D Observable Interaction State ($\mathbf{u} \in \mathbb{R}^4$) tracked via EKF with continuous OU prior + Layer B: Relational Memory Consolidation via continuous attractor dynamics toward resting equilibrium (+0.30).

---

## 2. Comparative Ontology Matrix

| Ontology Variant | Layer A: Observable 4D $R^2$ | Layer B: Slow Memory $R^2$ | Overall Combined $R^2$ | 4D MAE | Contradiction Recovery Velocity | CPU P50 Latency |
| :--- | :---: | :---: | :---: | :---: | :---: | :---: |
| **O1: Legacy 6D** | 0.6308 | **+0.7704** | **0.8242** | 0.0757 | 1.00 turn | **0.0239 ms** |
| **O2: Decoupled 4D+2D** | 0.6308 | -1.8236 | -0.1168 | 0.0757 | 1.00 turn | 0.0353 ms |
| **O3: Multi-Timescale** | **0.6385** | -0.0957 | 0.5119 | **0.0763** | **1.00 turn** | **0.0785 ms** |
| **Oracle Control** | **0.9355** | 0.9355 | 0.9355 | **0.0393** | 1.00 turn | 0.0230 ms |

---

## 3. Key Findings

1. **Layer A Observable 4D State is Resilient and Fast:**
   - Across all variants, the 4D Observable Interaction State ($\mathbf{u} = [\text{Load}, \text{Valence}, \text{Agency}, \text{Urgency}]$) achieves stable held-out tracking ($R^2 \approx 0.63 \sim 0.64$) with rapid **1.00-turn contradiction recovery**.
   - Cognitive load ($u_0 = 0.7278$) and valence ($u_1 = 0.6348$) are reliably reconstructed across all stress regimes.
2. **The Relational Memory Dynamics Dilemma:**
   - When slow relational memory ($m_1$ warmth, $m_0$ fatigue) is simulated as coupled to slow somatic drift, attempting to maintain it via open-loop forward integration (O2) suffers severe phase drift ($R^2 = -1.8236$).
   - In O3, introducing continuous attractor relaxation toward a Philia resting attractor damped the drift significantly (improving slow $R^2$ by $+1.73$ points over O2 to $-0.0957$), but still fell short of positive correlation because slow drift without sensory feedback cannot anticipate stochastic diffusion.
3. **The Empirical Truth of Joint Measurement:**
   - In O1, where slow states were jointly regressed with observation cues, the model achieved $R^2 = 0.8242$, demonstrating that surface interaction cues (turn latency, pause ratios) contain valuable empirical constraints that must not be disconnected from slow state maintenance.
