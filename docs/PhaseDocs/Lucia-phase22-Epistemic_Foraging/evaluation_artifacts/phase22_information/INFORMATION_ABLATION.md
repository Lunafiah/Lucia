# Information Ablation Study — Phase 22-INF

## 1. Overview & Evaluation Table

This experiment evaluates the progressive addition of orthogonal information streams to isolate where information gains occur and whether the continuous alignment gate ($R^2 \ge 0.85$) is reachable.

All results are measured on **held-out seeds (1024, 2026)** across all 6 stress regimes:

| Stream Code | Stream Name | Feature Dim | Held-Out $R^2$ | Held-Out MAE | Held-Out MSE | $\Delta R^2$ vs Baseline | CPU P50 Latency | Gate Status ($R^2 \ge 0.85$) |
| :--- | :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| **E0** | Baseline (Text + Acoustics) | 13 | 0.6087 | 0.0933 | 0.0203 | Baseline | 0.0228 ms | **FAIL** |
| **E1** | + Temporal Micro-Dynamics | 19 | 0.6380 | 0.0887 | 0.0188 | +0.0293 | 0.0231 ms | **FAIL** |
| **E2** | Prosodic Trajectory | 14 | 0.6553 | 0.0859 | 0.0179 | +0.0466 | 0.0337 ms | **FAIL** |
| **E3** | + Interaction Dynamics | 17 | **0.6988** | **0.0812** | **0.0156** | **+0.0901** | 0.0233 ms | **FAIL** |
| **E4** | + Relational Context | 17 | 0.6293 | 0.0891 | 0.0193 | +0.0206 | 0.0232 ms | **FAIL** |
| **E5** | Full Multimodal Integration | 27 | 0.6726 | 0.0821 | 0.0170 | +0.0639 | 0.0229 ms | **FAIL** |
| **E6** | Oracle Control | 6 | 0.8423 | 0.0562 | 0.0080 | +0.2336 | 0.0230 ms | **PASS** |

---

## 2. Key Empirical Findings

1. **Interaction Dynamics (E3) Provides the Strongest Information Gain:**
   - Adding reciprocal interaction metrics (inter-turn response latency, interruption events, conversational synchrony) yields the single largest individual improvement: **$\Delta R^2 = +0.0901$**, lifting alignment to **$R^2 = 0.6988$**.
   - Interaction signals directly unlock relational warmth ($z_5$) and agency ($z_2$), which were virtually unobservable from text/acoustic baselines.

2. **Temporal Micro-Dynamics (E1) vs Turn Snapshots:**
   - Incorporating continuous velocity, cadence, and pause duration raises $R^2$ from $0.6087$ to $0.6380$ ($\Delta R^2 = +0.0293$).
   - Most notably, temporal pause metrics dramatically improve the identification of metabolic fatigue ($z_4$), moving it from negative alignment ($-0.2031$) to positive ($+0.3174$).

3. **Multimodal Fusion Ceiling (E5):**
   - Full multimodal combination (E5) achieves $R^2 = 0.6726$.
   - While representing a marked improvement over raw turn-level baselines, it falls just short of the $0.70$ falsification threshold and well below the $0.85$ target gate.
   - The primary limiting factor is dimensionality saturation under stress: combining 27 non-linearly coupled features introduces slight variance inflation in low-density regimes (LexicalSparsity).

4. **Verdict on Hypothesis H-INF5:**
   - Multimodal integration demonstrates positive complementarity, but non-invasive conversational cues alone **do not satisfy the $R^2 \ge 0.85$ target gate**.
