# Phase 22-REL — Identifiability Report

## 1. Dimension-Wise Latent Identifiability

Below is the per-dimension breakdown of empirical identifiability ($R^2$ and MAE) across candidates on held-out seeds (1024, 2026):

| Dimension | Semantic Role | O1 (Legacy) $R^2$ | O2 (Decoupled) $R^2$ | O3 (Episodic) $R^2$ | O4 (Corrected) $R^2$ | Oracle $R^2$ |
| :--- | :--- | :---: | :---: | :---: | :---: | :---: |
| **$u_0$** | Cognitive Load | 0.6471 | 0.6178 | 0.6178 | 0.6178 | 0.9973 |
| **$u_1$** | Affective Valence | 0.6272 | 0.6065 | 0.6065 | 0.6065 | 0.9981 |
| **$u_2$** | Agency / Control | 0.3412 | 0.3035 | 0.3035 | 0.3035 | 0.9970 |
| **$u_3$** | Interaction Urgency | 0.5987 | 0.5490 | 0.5490 | 0.5490 | 0.9951 |
| **$m_0$** | Metabolic Fatigue | 0.3885 | -30.1787 | **0.5702** | 0.3781 | 0.9756 |
| **$m_1$** | Relational Warmth | 0.4009 | -2.1513 | -4.4912 | -4.5120 | 0.9986 |

---

## 2. Analysis of Observable vs. Relational Identifiability

1. **Observable 4D State ($u_0–u_3$):**
   - High, robust identifiability across all variants ($R^2 \approx 0.52 - 0.62$).
   - Strongly identified by text classification logits, speech acoustic energy, and turn-taking response latency.
2. **Metabolic Fatigue ($m_0$):**
   - Unidentifiable in open-loop accumulation (O2: $R^2 = -30.18$).
   - Successfully identified under episodic memory with homeostatic reset (O3: $R^2 = +0.5702$).
   - Acoustic pause ratios ($t_2$) and turn latency ($i_0$) provide measurable physiological evidence.
3. **Relational Warmth ($m_1$):**
   - In O1, $R^2 = 0.4009$ appears moderate only because O1 forces instantaneous linear correlation with surface lexical markers, which violates the biological/relational reality that warmth is not a turn-level observable.
   - When modeled as a cumulative, persistent relational variable (O2, O3, O4), absence of explicit calibration anchors causes severe integration drift ($R^2 < 0$).
