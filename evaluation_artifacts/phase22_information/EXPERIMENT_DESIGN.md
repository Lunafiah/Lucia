# Experiment Design & Methodological Protocol — Phase 22-INF

## 1. Context & Research Scope

Phase 22-AL demonstrated that applying learned linear remapping, temporal windowing, and recursive state estimation to turn-level observation representations C1–C6 plateaued at a held-out generalization of $R^2 = +0.2548$ ($A_5$ on C4), failing the preregistered threshold ($R^2 \ge 0.85$) and falling into the falsification region ($R^2 < 0.70$).

Phase 22-INF systematically investigates:
> **"What observable information is actually required to construct a continuous, language-independent semantic/user state for Lucia?"**

The independent variable in this study is **Information Content**, not network parameter count or transformer size.

---

## 2. Information Stream Architecture

We construct five orthogonal perceptual information streams plus controls:

1. **Text Semantic Intent ($e_{\text{text}} \in \mathbb{R}^7$):** One-hot/logit categorical dialogue acts across high load, agency, negative valence, positive valence, urgency, sparse, and neutral.
2. **Instantaneous Acoustic DSP ($e_{\text{acoust}} \in \mathbb{R}^6$):** Pitch jitter, acoustic energy, formant dispersion, speaking rate, spectral flux, harmonicity.
3. **Continuous Temporal Micro-Dynamics ($e_{\text{temp}} \in \mathbb{R}^6$):** Sub-turn trajectory derivatives, local velocity ($\dot{z}$), acceleration ($\ddot{z}$), pause duration ratio, and syllable cadence.
4. **Interaction Dynamics ($e_{\text{inter}} \in \mathbb{R}^4$):** Reciprocal coupling signals: inter-turn response latency ($\Delta t_{\text{resp}}$), interruption flag, turn synchrony, and engagement density.
5. **Persistent Relational Context ($e_{\text{rel}} \in \mathbb{R}^4$):** Structured exponentially decaying somatic state tracking historical trajectory without unbounded token concatenation.

---

## 3. Preregistered Ablation Configurations (E0–E6)

- **E0 — Baseline:** $e_{\text{text}} \oplus e_{\text{acoust}}$ (dim=13). Emulates canonical C4 multimodal baseline.
- **E1 — Temporal Micro-Dynamics:** $e_{\text{text}} \oplus e_{\text{acoust}} \oplus e_{\text{temp}}$ (dim=19). Isolates H-INF1.
- **E2 — Prosodic Contours:** $e_{\text{acoust}} \oplus e_{\text{temp}} \oplus e_{\text{inter[:2]}}$ (dim=14). Isolates H-INF2.
- **E3 — Interaction Dynamics:** $e_{\text{text}} \oplus e_{\text{acoust}} \oplus e_{\text{inter}}$ (dim=17). Isolates H-INF3.
- **E4 — Persistent Relational Context:** $e_{\text{text}} \oplus e_{\text{acoust}} \oplus e_{\text{rel}}$ (dim=17). Isolates H-INF4.
- **E5 — Full Multimodal Integration:** $e_{\text{text}} \oplus e_{\text{acoust}} \oplus e_{\text{temp}} \oplus e_{\text{inter}} \oplus e_{\text{rel}}$ (dim=27). Tests H-INF5.
- **E6 — Oracle Control:** $z_{\text{true}} + \epsilon$, where $\epsilon \sim \mathcal{N}(0, 0.05)$ (dim=6). Tests H-INF6 upper bound.

---

## 4. Anti-Cheating & Split Discipline

- **Training Seeds:** 42, 137, 618
- **Held-Out Generalization Seeds:** 1024, 2026
- **Stress Regimes (6):** ID, NoiseSurge, LexicalSparsity, ContradictionShock, TemporalDrift, CombinedStress
- **Languages (3):** English, Vietnamese, Japanese
- **Execution Target:** 100% CPU-native edge execution, 0 MB GPU VRAM.
