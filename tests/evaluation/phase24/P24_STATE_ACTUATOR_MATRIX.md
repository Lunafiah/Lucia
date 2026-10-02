# Phase 24 — State-to-Actuator Mapping Matrix

**Document Status:** Formal Architectural Specification (Design Gate Only — Not Promoted to Production)  
**Governing ADR:** ADR-032 (tests/evaluation/phase24/P24_ADR_ADAPTIVE_COMMUNICATION.md)  
**Governing Contract:** P24 Adaptive Communication Contract (tests/evaluation/phase24/P24_ADAPTIVE_COMMUNICATION_CONTRACT.md)  
**Production Invariant:** `production diff = 0` (Zero modifications to `src/core/`, `electron/`, or `data/`)

---

## 1. Master State-to-Actuator Mapping Matrix

Every actuator output in Lucia must have an explicit, mathematically bounded transfer function grounded in empirical evidence.

| Internal State Variable | Input Domain | Actuator Output | Output Domain | Channel | Mathematical Transfer Function | Bounds Enforcement | Timescale | Evidence Level | Production Status |
|:---|:---:|:---|:---:|:---:|:---|:---|:---:|:---:|:---:|
| **$R_{\text{close}}$ (Closeness)** | $[0.0, 1.0]$ | `formality_score` | $[0.0, 1.0]$ | Verbal | $-0.25 \cdot R_{\text{close}}$ | `np.clip(..., 0.0, 1.0)` | Turn ($\tau \approx 3\text{s}$) | `CANONICAL / VERIFIED` | Implemented (`comm_policy.py:112`) |
| **$R_{\text{close}}$ (Closeness)** | $[0.0, 1.0]$ | `supportiveness` | $[0.0, 1.0]$ | Verbal | $+0.20 \cdot R_{\text{close}}$ | `np.clip(..., 0.0, 1.0)` | Turn ($\tau \approx 3\text{s}$) | `CANONICAL / VERIFIED` | Implemented (`comm_policy.py:109`) |
| **$R_{\text{close}}$ (Closeness)** | $[0.0, 1.0]$ | `directness` | $[0.10, 0.95]$ | Verbal | $-0.15 \cdot R_{\text{close}}$ | `np.clip(..., 0.10, 0.95)` | Turn ($\tau \approx 3\text{s}$) | `CANONICAL / VERIFIED` | Implemented (`comm_policy.py:103`) |
| **$R_{\text{close}}$ (Closeness)** | $[0.0, 1.0]$ | $S_{\text{base}}$ (RVC pitch) | $[-2.0, +4.0]\text{ st}$ | Vocal | $+1.50 \cdot R_{\text{close}}\text{ st}$ | `np.clip(..., -2.0, 4.0)` | Turn ($\tau \approx 3\text{s}$) | `EXPERIMENTALLY SUPPORTED` | Proposed (ADR-032.1) |
| **$R_{\text{trust}}$ (Trust)** | $[0.0, 1.0]$ | `formality_score` | $[0.0, 1.0]$ | Verbal | $-0.20 \cdot (R_{\text{trust}} - 0.50)$ | `np.clip(..., 0.0, 1.0)` | Turn ($\tau \approx 3\text{s}$) | `CANONICAL / VERIFIED` | Implemented (`comm_policy.py:112`) |
| **$R_{\text{trust}}$ (Trust)** | $[0.0, 1.0]$ | `supportiveness` | $[0.0, 1.0]$ | Verbal | $+0.25 \cdot (R_{\text{trust}} - 0.50)$ | `np.clip(..., 0.0, 1.0)` | Turn ($\tau \approx 3\text{s}$) | `CANONICAL / VERIFIED` | Implemented (`comm_policy.py:109`) |
| **$R_{\text{trust}}$ (Trust)** | $[0.0, 1.0]$ | `directness` | $[0.10, 0.95]$ | Verbal | $-0.10 \cdot (R_{\text{trust}} - 0.50)$ | `np.clip(..., 0.10, 0.95)` | Turn ($\tau \approx 3\text{s}$) | `CANONICAL / VERIFIED` | Implemented (`comm_policy.py:103`) |
| **$R_{\text{trust}}$ (Trust)** | $[0.0, 1.0]$ | `question_frequency` | $[0.0, 1.0]$ | Verbal | $+0.25 \cdot (R_{\text{trust}} - 0.50)$ | `np.clip(..., 0.0, 1.0)` | Turn ($\tau \approx 3\text{s}$) | `CANONICAL / VERIFIED` | Implemented, dropped at S11 |
| **$R_{\text{trust}}$ (Trust)** | $[0.0, 1.0]$ | `speech_rate_pct` | $[-20.0, +20.0]\%$ | Vocal | $+5.0 \cdot (R_{\text{trust}} - 0.50)\%$ | `np.clip(..., -20.0, 20.0)`| Turn ($\tau \approx 3\text{s}$) | `EXPERIMENTALLY SUPPORTED` | Proposed (ADR-032.1) |
| **$R_{\text{trust}}$ (Trust)** | $[0.0, 1.0]$ | `gaze_aversion_prob` | $[0.0, 1.0]$ | Avatar | $-0.10 \cdot R_{\text{trust}}$ | `np.clip(..., 0.0, 1.0)` | Turn ($\tau \approx 3\text{s}$) | `CANONICAL / VERIFIED` | Implemented (`expression_policy.py:130`) |
| **$R_{\text{fam}}$ (Familiarity)** | $[0.0, 1.0]$ | `acknowledgement_level`| $[0.10, 1.00]$ | Verbal | $+0.25 \cdot R_{\text{fam}}$ | `np.clip(..., 0.10, 1.00)` | Turn ($\tau \approx 3\text{s}$) | `CANONICAL / VERIFIED` | Implemented, dropped at S11 |
| **$R_{\text{fam}}$ (Familiarity)** | $[0.0, 1.0]$ | $\Delta \tau_{\text{pause}}$ | $[-50.0, 0.0]\text{ ms}$| Vocal | $-50.0 \cdot R_{\text{fam}}\text{ ms}$ | `np.clip(..., -50.0, 0.0)` | Turn ($\tau \approx 3\text{s}$) | `EXPERIMENTALLY SUPPORTED` | Proposed (ADR-032.1) |
| **$R_{\text{rec}}$ (Reciprocity)** | $[0.0, 1.0]$ | $s^*_{\text{eff}}(R)$ | $\mathbb{R}^{16}$ | Limbic | $W_{\text{rel}} (R_t - R_0)$ | $\sigma_{\max}(W_{\text{rel}}) \le 0.08$ | Slow ($\tau \ge 24\text{h}$) | `CANONICAL / VERIFIED` | Implemented (`emotion_core.py:855`) |
| **$R_{\text{rec}}$ (Reciprocity)** | $[0.0, 1.0]$ | Verbal / Vocal Outputs | N/A | Any | None (Strictly severed) | Prohibited | N/A | `BLOCKED` | Blocked (ADR-032.1) |
| **$p$ (Pleasure/Valence)** | $[-1.0, 1.0]$ | `supportiveness` | $[0.0, 1.0]$ | Verbal | $+0.35 \cdot p$ | `np.clip(..., 0.0, 1.0)` | Turn ($\tau \approx 3\text{s}$) | `CANONICAL / VERIFIED` | Implemented (`comm_policy.py:109`) |
| **$p$ (Pleasure/Valence)** | $[-1.0, 1.0]$ | `formality_score` | $[0.0, 1.0]$ | Verbal | $-0.30 \cdot p$ | `np.clip(..., 0.0, 1.0)` | Turn ($\tau \approx 3\text{s}$) | `CANONICAL / VERIFIED` | Implemented (`comm_policy.py:112`) |
| **$p$ (Pleasure/Valence)** | $[-1.0, 1.0]$ | $S_{\text{base}}$ (RVC pitch) | $[-2.0, +4.0]\text{ st}$ | Vocal | $+2.00 \cdot p\text{ st}$ | `np.clip(..., -2.0, 4.0)` | Turn ($\tau \approx 3\text{s}$) | `EXPERIMENTALLY SUPPORTED` | Proposed (ADR-032.4) |
| **$p$ (Pleasure/Valence)** | $[-1.0, 1.0]$ | `smile` blendshape | $[0.0, 1.0]$ | Avatar | $\max(0.0, p)$ | `np.clip(..., 0.0, 1.0)` | Turn ($\tau \approx 3\text{s}$) | `CANONICAL / VERIFIED` | Implemented (`expression_policy.py:124`) |
| **$a$ (Arousal/Vitality)** | $[-1.0, 1.0]$ | `speech_rate_pct` | $[-20.0, +20.0]\%$ | Vocal | $+15.0 \cdot a\%$ | `np.clip(..., -20.0, 20.0)`| Turn ($\tau \approx 3\text{s}$) | `CANONICAL / VERIFIED` | Implemented (`expression_policy.py:110`) |
| **$a$ (Arousal/Vitality)** | $[-1.0, 1.0]$ | `question_frequency` | $[0.0, 1.0]$ | Verbal | $+0.20 \cdot a$ | `np.clip(..., 0.0, 1.0)` | Turn ($\tau \approx 3\text{s}$) | `CANONICAL / VERIFIED` | Implemented, dropped at S11 |
| **$a$ (Arousal/Vitality)** | $[-1.0, 1.0]$ | `volume_pct` | $[-20.0, +20.0]\%$ | Vocal | $+5.0 \cdot a\%$ | `np.clip(..., -20.0, 20.0)`| Turn ($\tau \approx 3\text{s}$) | `CANONICAL / VERIFIED` | Implemented (`expression_policy.py:111`) |
| **$d$ (Dominance/Agency)** | $[-1.0, 1.0]$ | `directness` | $[0.10, 0.95]$ | Verbal | $+0.25 \cdot d$ | `np.clip(..., 0.10, 0.95)` | Turn ($\tau \approx 3\text{s}$) | `CANONICAL / VERIFIED` | Implemented (`comm_policy.py:103`) |
| **$d$ (Dominance/Agency)** | $[-1.0, 1.0]$ | `volume_pct` | $[-20.0, +20.0]\%$ | Vocal | $+10.0 \cdot d\%$ | `np.clip(..., -20.0, 20.0)`| Turn ($\tau \approx 3\text{s}$) | `CANONICAL / VERIFIED` | Implemented (`expression_policy.py:111`) |
| **$S_{\text{tension}}$ (Tension)**| $[0.0, 1.0]$ | `formality_score` | $[0.0, 1.0]$ | Verbal | $+0.15 \cdot \text{tension}$ | `np.clip(..., 0.0, 1.0)` | Turn ($\tau \approx 3\text{s}$) | `CANONICAL / VERIFIED` | Implemented (`comm_policy.py:112`) |
| **$S_{\text{tension}}$ (Tension)**| $[0.0, 1.0]$ | `directness` | $[0.10, 0.95]$ | Verbal | $-0.20 \cdot \text{tension}$ | `np.clip(..., 0.10, 0.95)` | Turn ($\tau \approx 3\text{s}$) | `CANONICAL / VERIFIED` | Implemented (`comm_policy.py:103`) |
| **$S_{\text{tension}}$ (Tension)**| $[0.0, 1.0]$ | `pacing_latency_ms` | $[0, 1000]\text{ ms}$ | Verbal | $+150.0 \cdot \text{tension}\text{ ms}$ | `min(..., 1000.0)` | Turn ($\tau \approx 3\text{s}$) | `CANONICAL / VERIFIED` | Implemented (`comm_policy.py:123`) |
| **$S_{\text{energy}}$ (Energy)** | $[0.0, 1.0]$ | `speech_rate_pct` | $[-20.0, +20.0]\%$ | Vocal | $-10.0 \cdot (1.0 - \text{energy})\%$ | `np.clip(..., -20.0, 20.0)`| Turn ($\tau \approx 3\text{s}$) | `CANONICAL / VERIFIED` | Implemented (`expression_policy.py:110`) |
| **$S_{\text{energy}}$ (Energy)** | $[0.0, 1.0]$ | `pacing_latency_ms` | $[0, 1000]\text{ ms}$ | Verbal | $+400.0 \cdot (1.0 - \text{energy})\text{ ms}$| `min(..., 1000.0)` | Turn ($\tau \approx 3\text{s}$) | `CANONICAL / VERIFIED` | Implemented (`comm_policy.py:123`) |
| **$S_{\text{load}}$ (Cognitive Load)**| $[0.0, 1.0]$ | `elaboration_depth` | $[0.10, 1.00]$ | Verbal | $-0.35 \cdot \text{load}$ | `np.clip(..., 0.10, 1.00)` | Turn ($\tau \approx 3\text{s}$) | `CANONICAL / VERIFIED` | Implemented (`comm_policy.py:106`) |
| **$S_{\text{load}}$ (Cognitive Load)**| $[0.0, 1.0]$ | `pacing_latency_ms` | $[0, 1000]\text{ ms}$ | Verbal | $+200.0 \cdot \text{load}\text{ ms}$ | `min(..., 1000.0)` | Turn ($\tau \approx 3\text{s}$) | `CANONICAL / VERIFIED` | Implemented (`comm_policy.py:123`) |
| **Focal Words** | Text tokens | $S(t)$ trajectory | $[0.0, +2.5]\text{ st}$ | Vocal | $+2.50 \cdot w_{\text{hanning}}(t)\text{ st}$| Smooth Hanning window | Frame ($\tau \approx 10\text{ms}$)| `EXPERIMENTALLY SUPPORTED` | Proposed (ADR-032.2) |
| **Orthography (`...`, `!`)**| Text tokens | Neural TTS Cadence | $[800, 900]\text{ ms}$ | Cadence | Edge-TTS prosody synthesis | Orthographic parsing | Phrase ($\tau \approx 1\text{s}$) | `EXPERIMENTALLY SUPPORTED` | Proposed (ADR-032.2) |

---

## 2. Interaction & Interference Analysis

To verify that multiple internal signals cannot destructively interfere, cancel each other, or cause runaway:

1. **Formality Equilibrium:**
   $$\text{Formality} = 0.60 - 0.30 p - 0.25 R_{\text{close}} - 0.20 (R_{\text{trust}} - 0.50) + 0.15 \text{tension}$$
   - *Worst-case Maximum (Stranger under extreme stress):* $p = -1.0, R_{\text{close}} = 0.0, R_{\text{trust}} = 0.0, \text{tension} = 1.0 \rightarrow 0.60 + 0.30 - 0.0 + 0.10 + 0.15 = 1.15 \rightarrow \mathbf{1.00}$ (Clamped).
   - *Worst-case Minimum (Intimate bond under high joy):* $p = +1.0, R_{\text{close}} = 1.0, R_{\text{trust}} = 1.0, \text{tension} = 0.0 \rightarrow 0.60 - 0.30 - 0.25 - 0.10 + 0.0 = -0.05 \rightarrow \mathbf{0.00}$ (Clamped).
   - *Interference Verdict:* Bounded convex behavior across the entire hypercube $[0, 1]^4 \times [-1, 1] \times [0, 1]$.

2. **Vocal Pitch Equilibrium:**
   $$S_{\text{base}} = 2.0 \cdot p + 1.5 \cdot R_{\text{close}}$$
   - *Worst-case Maximum:* $p = +1.0, R_{\text{close}} = 1.0 \rightarrow +3.5\text{ semitones} \le +4.0\text{ st}$ limit.
   - *Worst-case Minimum:* $p = -1.0, R_{\text{close}} = 0.0 \rightarrow -2.0\text{ semitones} \ge -2.0\text{ st}$ limit.
   - *Interference Verdict:* Naturally bounded; adding $+2.5\text{ st}$ focal accents yields a maximum possible peak of $+6.0\text{ st}$, safely below the $+12.0\text{ st}$ vocoder ceiling.
