# Phase 22-REL — Failure Analysis & Scientific Root Cause

## 1. Executive Failure Summary

In Phase 22-REL, candidate O4 achieved:
- **G_REL1 (Warmth $R^2 \ge 0.50$):** **FAILED** ($R^2 = -4.5120$)
- **G_REL2 (Fatigue $R^2 \ge 0.50$):** **FAILED** in O4 ($R^2 = 0.3781$), but **PASSED** in O3 ($R^2 = 0.5702$)
- **G_REL3 (Session Retention $\ge 0.80$):** **PASSED** ($98.4\%$)
- **G_REL4 (Contradiction Recovery $\le 1.0\text{ turn}$):** **FAILED** ($1.80\text{ turns}$)
- **G_REL5 (CPU P50 $\le 2.0\text{ ms}$):** **PASSED** ($0.0001\text{ ms}$)
- **G_REL6 (Zero VRAM):** **PASSED** ($0.0\text{ MB}$)

---

## 2. Root Cause Dissection

### 2.1. The Integral Drift of Unanchored Relational Warmth
The fundamental empirical failure of candidates O2, O3, and O4 on Relational Warmth ($m_1$) is attributed to the **Unanchored Path Integral Problem**:
- In the simulation, ground-truth warmth $m_1$ evolves as a continuous stochastic process driven by both positive valence and interpersonal rapport, plus a small Brownian diffusion component $\mathrm{d}W_t$.
- In candidates O2, O3, and O4, the agent accumulates estimated positive valence without direct observation of $m_1$:
  $$\hat{m}_1(t) = m_0 + \sum_{\tau=1}^t \Delta \hat{w}(\tau)$$
- Even if $\Delta \hat{w}(\tau)$ is unbiased on average, the variance of the accumulated estimation error grows monotonically with session length $T$:
  $$\operatorname{Var}(\hat{m}_1(t) - m_1(t)) = \sigma_{\text{accum}}^2 \cdot t$$
- As $t$ increases across multiple sessions, the mean squared error (MSE) inevitably exceeds the total variance of the ground-truth state:
  $$\text{MSE} > \operatorname{Var}(m_{1,\text{true}}) \implies R^2 = 1 - \frac{\text{MSE}}{\operatorname{Var}} < 0$$
- This explains why $R^2$ is negative across all accumulation-based candidates ($-2.15$ in O2, $-4.49$ in O3, $-4.51$ in O4).

### 2.2. Why Legacy O1 Reached $R^2 = 0.40$
In O1 (Legacy 6D), warmth is directly regressed from current turn features (e.g. lexical tokens like "Thanks Lucia" and dyadic synchrony). Because it does not accumulate state over time, it suffers no variance growth over long sessions.
However, this violates the user's explicit architectural requirement: **"Warmth và Fatigue không được ép hồi quy trực tiếp từ surface observation mỗi turn"** and ADR-011 / ADR-028, because warmth is a slow relational property, not a turn-by-turn sentiment label.

### 2.3. Why Fatigue Succeeded under O3 ($R^2 = 0.5702$)
Fatigue exhibits a physiological reset mechanism (sleep/restoration). Because fatigue is reset back to basal $0.20$ after every session, the error accumulation horizon is bounded strictly to $T \le 15$ turns. Within that short horizon, acoustic pauses and turn latency provide sufficient closed-loop feedback to prevent drift.

---

## 3. Scientific Bottleneck Identified

> **Layer B is fundamentally NOT an open-loop accumulation problem, nor is it a turn-level surface regression problem. It is a CALIBRATED EPISODIC RETRIEVAL problem.**

To track relational bonding longitudinally without path-integral drift, a system must either:
1. Ground the relational bond in **episodic autobiographical memories (Kanerva SDM memory traces)** where specific shared experiences and milestones are retrieved and anchor the relational stance.
2. Rely on **sparse conversational calibration anchors** (e.g., explicit relationship check-ins or explicit user feedback) that reset or clamp the continuous state.
