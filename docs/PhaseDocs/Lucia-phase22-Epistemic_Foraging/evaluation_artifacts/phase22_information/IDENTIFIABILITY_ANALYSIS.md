# Latent-State Identifiability Analysis — Phase 22-INF

## 1. Overview & Research Question

Hypothesis **H-INF6 (Latent-State Identifiability)** investigates:
> *Are all six dimensions of the synthetic Ornstein-Uhlenbeck user state ($z_0$ to $z_5$) mathematically identifiable from non-invasive conversational observation, or do fundamental unidentifiability boundaries exist?*

---

## 2. Dimension-Wise $R^2$ Decomposition

Measured on held-out seeds (1024, 2026) across all 6 stress regimes under Full Multimodal Integration ($E_5$) vs Oracle ($E_6$):

| Latent Dimension Name | Coordinate Semantic | $E_0$ Baseline $R^2$ | $E_5$ Multimodal $R^2$ | $E_6$ Oracle $R^2$ | Identifiability Classification | Primary Observational Signal |
| :--- | :--- | :---: | :---: | :---: | :--- | :--- |
| **$z_0$ Cognitive Load** | Working memory load | **0.6946** | **0.6128** | 0.7906 | **HIGHLY IDENTIFIABLE** | Dialogue complexity, pitch jitter |
| **$z_1$ Valence** | Affective polarity | **0.6500** | **0.5451** | 0.7873 | **HIGHLY IDENTIFIABLE** | Lexical sentiment, acoustic harmonics |
| **$z_2$ Agency** | Autonomy & dominance | 0.4266 | 0.4326 | 0.7686 | **MODERATELY IDENTIFIABLE** | Formant dispersion, interruption |
| **$z_3$ Urgency** | Temporal task pressure | 0.3489 | **0.5088** | 0.6455 | **MODERATELY IDENTIFIABLE** | Turn latency, acoustic energy |
| **$z_4$ Fatigue** | Metabolic exhaustion | **-0.2031** | **0.5120** | 0.7096 | **CONDITIONALLY IDENTIFIABLE** | Pause duration, response latency |
| **$z_5$ Warmth** | Interpersonal affinity | **0.0569** | **0.3124** | 0.7429 | **WEAKLY IDENTIFIABLE** | Interaction synchrony, somatic history |

---

## 3. Structural Identifiability Findings

1. **The Core Observable Subspace ($z_0, z_1$):**
   - Cognitive load ($z_0$) and affective valence ($z_1$) exhibit high intrinsic identifiability ($R^2 > 0.60$) even from simple baseline observations. They are strongly reflected in surface vocabulary and vocal prosody.

2. **The Dynamic Interaction Subspace ($z_2, z_3$):**
   - Agency ($z_2$) and urgency ($z_3$) achieve moderate identifiability ($R^2 \approx 0.43 \sim 0.51$).
   - They require interaction timing and pitch contours to resolve ambiguous lexical tokens.

3. **The Hidden State Dilemma ($z_4, z_5$):**
   - **Metabolic Fatigue ($z_4$):** Completely unobservable in text ($R^2 = -0.2031$). Can only be identified when sub-turn pause ratios and turn latencies are captured ($R^2 \to 0.5120$).
   - **Relational Warmth ($z_5$):** The most difficult dimension to observe ($R^2 = 0.3124$ under $E_5$). Warmth is an internal interpersonal stance that manifests subtle conversational synchrony over extended dialogue, making instantaneous or short-window inference inherently noisy.

---

## 4. Architectural Implication for P23

The 6-dimensional state is **non-uniformly identifiable**:
- A single unified linear or shallow neural estimator attempting to assign equal weight to all 6 coordinates inevitably under-fits the core observable subspace while over-fitting noisy proxies for $z_5$.
- For Phase 23, the semantic user state $\boldsymbol{\psi}_{\text{user}} \in \mathbb{R}^{12}$ should decouple:
  1. Fast, highly observable surface dimensions (valence, cognitive load, urgency).
  2. Slow, accumulating relational and physiological dimensions (warmth, fatigue) tracked via autonomous somatic integration rather than instantaneous observation inversion.
