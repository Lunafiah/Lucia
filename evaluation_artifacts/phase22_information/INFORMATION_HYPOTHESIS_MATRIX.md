# Information Bottleneck Hypothesis Matrix — Phase 22-INF

## 1. Overview & Evaluation Scope

Phase 22-INF tests six orthogonal hypothesis families to systematically isolate why turn-level observation representations C1–C6 failed the preregistered continuous alignment gate ($R^2_{\max} = 0.2548 \ll 0.85$).

---

## 2. Preregistered Hypothesis Matrix

| ID | Hypothesis Name | Proposed Causal Mechanism | Operational Manipulation / Signal Stream | Preregistered Success Criteria | Falsification / Rejection Criteria |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **H-INF1** | **Temporal Micro-Dynamics** | Turn-level snapshots discard continuous velocity and acceleration; sub-turn trajectories contain essential OU drift signal. | Frame-level acoustic pitch/energy trajectories ($F0, RMS$), local temporal derivatives ($\dot{e}_t, \ddot{e}_t$), pause duration, speaking rate. | Adding continuous temporal derivatives yields $\Delta R^2 \ge +0.20$ over turn snapshots. | $\Delta R^2 < +0.05$ or temporal features degrade under stress. |
| **H-INF2** | **Prosodic / Affective Dynamics** | Rich continuous prosody carries affective arousal and dominance coordinates missing from lexical semantic tokens. | Micro-prosodic contours: pitch variability ($\sigma_{F0}$), spectral flux, harmonics-to-noise ratio, local jitter/shimmer. | Prosodic features isolate arousal/agency recovery ($R^2_{z_0, z_2} \ge 0.70$). | Prosody only affects calibration without improving coordinate reconstruction. |
| **H-INF3** | **Interaction Dynamics** | User state cannot be determined from user actions in isolation; the reciprocal coupling between user and Lucia contains the diagnostic signal. | Inter-turn response latency ($\Delta t_{\text{resp}}$), interruption markers, conversational synchrony, turn overlap, dialogue tempo. | Interaction features differentiate interpersonal agency and warmth ($\Delta R^2_{z_2, z_5} \ge +0.15$). | Interaction metrics provide redundant signal with lexical intent ($\Delta R^2 < +0.03$). |
| **H-INF4** | **Persistent Relational Context** | A single instantaneous observation cannot identify continuous state; a structured persistent state vector captures historical accumulation without token explosion. | Structured exponentially decaying relational state vector $s_t = \lambda s_{t-1} + (1-\lambda) \phi(e_t)$ vs raw token history concatenation. | Structured relational context strictly outperforms raw window concatenation ($R^2_{\text{struct}} > R^2_{\text{raw\_k10}} + 0.15$). | Structured state adds no incremental variance beyond instantaneous $e_t$. |
| **H-INF5** | **Multimodal Complementarity** | Text, audio, temporal, interaction, and relational signals are mutually orthogonal; full state reconstruction requires full multimodal fusion. | Nested ablation ladder: $E_0$ (Text only) $\to$ $E_1$ (+Temporal) $\to$ $E_2$ (+Prosodic) $\to$ $E_3$ (+Interaction) $\to$ $E_4$ (+Relational) $\to$ $E_5$ (Full Fusion). | Full multimodal integration achieves $R^2 \ge 0.85$ on held-out seeds. | Full multimodal integration fails to achieve $R^2 \ge 0.70$ (falsifying the information sufficiency of non-invasive cues). |
| **H-INF6** | **Latent-State Identifiability** | Certain latent dimensions of the synthetic 6D OU state are fundamentally unobservable from external conversational observations. | Dimension-wise $R^2$ decomposition across all 6 latent axes ($z_0$ load, $z_1$ valence, $z_2$ agency, $z_3$ urgency, $z_4$ fatigue, $z_5$ warmth). | Clear bifurcation between observable ($R^2_i \ge 0.60$) and unidentifiable ($R^2_j \le 0.10$) latent dimensions. | All dimensions have uniform, non-distinguishable error distributions. |

---

## 3. Decision Boundary Mapping

Based on the empirical outcomes across H-INF1 through H-INF6, the study will classify the architecture status into one of five predefined outcomes:

- **Classification A — Information Sufficiency Demonstrated:** Full multimodal/interaction configuration $E_5$ achieves $R^2 \ge 0.85$ on held-out seeds.
- **Classification B — Partial Information Recovery:** Alignment improves substantially ($0.50 \le R^2 < 0.85$), proving multimodal synergy, but remains below the target.
- **Classification C — Information Bottleneck Persists:** Even enriched temporal, prosodic, interaction, and relational features fail to reach $R^2 \ge 0.50$.
- **Classification D — Target Latent Not Identifiable:** Identification analysis confirms that specific latent coordinates (e.g., fatigue $z_4$) have near-zero mutual information with conversational observations.
- **Classification E — Experimental Insufficiency:** Methodological artifacts prevent clear attribution.
