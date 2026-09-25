# Stream Ablation Report — Phase 22-SSF

## 1. Overview & Evaluation Setup

Phase 22-SSF tests whether **Semantic State Formation (SSF)** with decoupled fast and slow dynamics can bridge raw conversational observations into a continuous user state.

All metrics are evaluated across **held-out generalization seeds (1024, 2026)** and 6 stress regimes:
- **Full Stream:** Text Intent (7D) + Acoustic DSP (6D) + Temporal Micro-Dynamics (6D) + Interaction Dynamics (4D) = 23D.
- **No Interaction:** Without reciprocal turn latency, synchrony, and interruption (19D).
- **No Temporal:** Without sub-turn pause ratios, velocity, and cadence (17D).
- **Text Only:** Isolated categorical dialogue acts (7D).
- **Acoustics Only:** Isolated acoustic DSP (6D).

---

## 2. Quantitative Stream Ablation Matrix

| Stream Ablation | Feature Dim | Total Held-Out $R^2$ | Fast States $R^2$ ($z_0–z_3$) | Slow States $R^2$ ($z_4–z_5$) | MAE | MSE | Impact vs Full Stream |
| :--- | :---: | :---: | :---: | :---: | :---: | :---: | :--- |
| **Full Multimodal SSF** | 23 | **0.4767** | **0.5716** | **-0.9446** | **0.1072** | **0.0272** | Full Decoupled Baseline |
| **No Interaction** | 19 | 0.4689 | 0.5348 | -0.9469 | 0.1074 | 0.0276 | Fast $R^2$ drops $-0.0368$ (agency/urgency loss) |
| **No Temporal** | 17 | 0.4750 | 0.5617 | -0.9434 | 0.1074 | 0.0273 | Fast $R^2$ drops $-0.0099$ |
| **Text Only** | 7 | 0.3426 | 0.2537 | -0.9397 | 0.1227 | 0.0341 | Severe collapse ($\Delta R^2_{\text{fast}} = -0.3179$) |
| **Acoustics Only** | 6 | 0.4731 | 0.5165 | -0.9212 | 0.1066 | 0.0274 | Retains physical load/valence, loses agency |

---

## 3. Findings & Information Attribution

1. **Acoustic + Temporal + Interaction Synergy:**
   - Text alone only achieves $R^2_{\text{fast}} = 0.2537$.
   - Combining text with acoustic prosody, temporal cadence, and interaction latency lifts fast state reconstruction to **$R^2_{\text{fast}} = 0.5716$** ($\Delta R^2 = +0.3179$).
   - This reconfirms the Phase 22-INF finding: non-verbal interaction timing is indispensable for observing conversational urgency and agency.

2. **Ablation Bottleneck:**
   - Stripping interaction dynamics causes immediate degradation in user agency ($z_2: 0.4638 \to 0.4046$) and urgency ($z_3: 0.5127 \to 0.3885$).
   - However, even with the complete 23D feature stream, fast state alignment plateaus at $R^2_{\text{fast}} = 0.5716$, failing the $R^2 \ge 0.70$ threshold.
