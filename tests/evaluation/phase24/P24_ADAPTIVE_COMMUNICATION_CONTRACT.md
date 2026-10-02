# Phase 24 — Adaptive Communication Control Contract

**Contract Status:** Formal Architecture Specification (Design Gate Only — Not Promoted to Production)  
**Governing ADR:** ADR-032 (tests/evaluation/phase24/P24_ADR_ADAPTIVE_COMMUNICATION.md)  
**Evidence Grounding:** P24 Gate 1, Gate 2, Gate 3 Audits  
**Production Invariant:** `production diff = 0` (Zero modifications to `src/core/`, `electron/`, or `data/`)

---

## 1. Scope & Architectural Purpose

This contract defines the exact interfaces, mathematical transfer functions, data types, and temporal execution constraints governing **Adaptive Communication** in Lucia. It specifies how internal relational state ($R_t$), affective state ($E_t$), and somatic state ($S_t$) modulate verbal output, orthographic cadence, and acoustic voice prosody.

---

## 2. Canonical State Definitions & Freezes

### 2.1 Relational State Vector ($R_t$)
The canonical relational state vector is frozen as:

$$R_t = \begin{bmatrix} \text{familiarity} \\ \text{trust} \\ \text{closeness} \\ \text{reciprocity} \end{bmatrix} \in [0.0, 1.0]^4$$

- **`familiarity` ($R_{\text{fam}} \in [0.0, 1.0]$):** Accumulated interaction volume and exposure depth. Initial stranger baseline = $0.0$.
- **`trust` ($R_{\text{trust}} \in [0.0, 1.0]$):** Predictability, reliability, and cognitive expectation fulfillment. Initial baseline = $0.50$.
- **`closeness` ($R_{\text{close}} \in [0.0, 1.0]$):** Emotional proximity and shared context depth. Initial stranger baseline = $0.0$.
- **`reciprocity` ($R_{\text{rec}} \in [0.0, 1.0]$):** Degree of balanced mutual conversational engagement. Initial baseline = $0.50$.
- **Historical Nomenclature Rejection:** All historical alternatives (e.g. `[trust, familiarity, depth, alignment]`, `[trust, familiarity, attunement, shared_experience]`, `[affinity, familiarity, trust, depth]`) are classified as documentation drift and are explicitly forbidden from code and contracts.

### 2.2 Affective State Vector ($E_t$)
- Defined strictly by the canonical 3-dimensional continuous PAD vector in `PADState`:
  $$E_t = \begin{bmatrix} p \\ a \\ d \end{bmatrix} \in [-1.0, 1.0]^3$$
- Continuous background integration via Coupled MT-LNN ODE every 200 ms, smoothly decaying toward the Philia resting attractor ($p=+0.25, a=-0.05, d=+0.05$).
- Strictly decoupled from reflective ego: Lucia never self-reports affect in text.

### 2.3 Somatic Marker Vector ($S_t$)
- Defined strictly by `SomaticMarkers` ($[0.0, 1.0]^4$):
  $$S_t = \begin{bmatrix} \text{stability} \\ \text{cognitive\_load} \\ \text{energy} \\ \text{tension} \end{bmatrix} \in [0.0, 1.0]^4$$
- Derived mathematically by `HomeostaticEngine` from PAD and prediction surprise. Somatic markers represent physiological/metabolic load, not subjective emotions.

---

## 3. The Three Output Domains

```text
               (R_t, E_t, S_t)
                      │
       ┌──────────────┼──────────────┐
       ▼              ▼              ▼
[ Domain A ]    [ Domain B ]    [ Domain C ]
Verbal Style      Cadence        Voice Prosody
(LLM Strategy)  (Punctuation)   (Edge-TTS + RVC)
```

---

### Domain A: Verbal Adaptation Contract

Verbal adaptation is executed in `CommunicationPolicy` (Stage 10) and formatted into prompt tokens by `PromptAssembler` (Stage 11).

#### Parameter Transfer Equations:
1. **Directness ($D_{\text{verbal}} \in [0.10, 0.95]$):**
   $$D_{\text{verbal}} = \text{clip}\left(0.50 + 0.25 d - 0.20 \text{tension} - 0.15 R_{\text{close}} - 0.10(R_{\text{trust}} - 0.50), 0.10, 0.95\right)$$
   *Semantic Interpretation:* Dominance increases directness; high closeness, trust, and tension cushion delivery.
2. **Supportiveness ($S_{\text{verbal}} \in [0.00, 1.00]$):**
   $$S_{\text{verbal}} = \text{clip}\left(0.30 + 0.35 p + 0.25(R_{\text{trust}} - 0.50) + 0.20 R_{\text{close}}, 0.00, 1.00\right)$$
   *Semantic Interpretation:* Positive valence, high trust, and closeness foster warm, validating responses.
3. **Formality ($F_{\text{verbal}} \in [0.00, 1.00]$):**
   $$F_{\text{verbal}} = \text{clip}\left(0.60 - 0.30 p - 0.25 R_{\text{close}} - 0.20(R_{\text{trust}} - 0.50) + 0.15 \text{tension}, 0.00, 1.00\right)$$
   *Semantic Interpretation:* Intimacy and trust reduce formality; tension and stranger baselines maintain polite reserve.
4. **Acknowledgement Level ($A_{\text{verbal}} \in [0.10, 1.00]$):**
   $$A_{\text{verbal}} = \text{clip}\left(0.40 + 0.25 R_{\text{fam}} + 0.20 m_{\text{avail}} - 0.15 \text{tension}, 0.10, 1.00\right)$$
   *Semantic Interpretation:* Familiarity and retrieved memory traces heighten explicit conversational grounding.
5. **Question Frequency ($Q_{\text{verbal}} \in [0.00, 1.00]$):**
   $$Q_{\text{verbal}} = \text{clip}\left(0.10 + 0.25(R_{\text{trust}} - 0.50) + 0.20 a - 0.25 \text{tension}, 0.00, 1.00\right)$$
   *Semantic Interpretation:* Trust and arousal foster collaborative inquiries; high tension suppresses questioning.
6. **Elaboration Depth ($E_{\text{verbal}} \in [0.10, 1.00]$):**
   $$E_{\text{verbal}} = \text{clip}\left(0.50 + 0.30 k_{\text{avail}} - 0.35 \text{load} - 0.30(1.0 - \text{energy}), 0.10, 1.00\right)$$
   *Semantic Interpretation:* Grounded knowledge increases explanation depth; cognitive fatigue enforces conciseness.

#### Prompt Ingestion Contract:
`PromptAssembler` (Stage 11) must inject all active verbal dimensions into the conditioned system prompt:
```text
[COMMUNICATION STRATEGY]
strategy: {strategy}
directness: {directness:.2f}
formality: {formality:.2f}
elaboration: {elaboration:.2f}
supportiveness: {supportiveness:.2f}
acknowledgement: {acknowledgement:.2f}
question_frequency: {question_freq:.2f}
```

---

### Domain B: Cadence Adaptation Contract

Cadence adaptation governs the temporal rhythm, respiratory pausing, and phrasing of the generated response.

#### Orthographic Punctuation Rules:
1. **Semantic Separation Invariant:** Cadence conditioning operates strictly on orthographic prosodic markers (`...`, `,`, `!`). It MUST NOT rewrite, delete, or alter semantic content propositions, named entities, or numerical values.
2. **Formality-Governed Punctuation:**
   - **High Formality ($F_{\text{verbal}} \ge 0.65$):** Standard grammatical punctuation. Clean clause boundaries, standard periods and commas. Zero ellipses.
   - **Low Formality / High Warmth ($F_{\text{verbal}} \le 0.35$):** Conversational breathing cadence. Injects `...` after introductory phrases or before emotional climaxes (generating ~800–900ms respiratory pauses in neural TTS). Injects `!` on empathetic peaks.
3. **Fallback Behavior:** If the LLM generates plain text without expressive punctuation, the downstream boundary segmenter falls back to grammatical clause-level chunking based on comma/period detection.

---

### Domain C: Vocal Prosody Adaptation Contract

Vocal prosody controls the acoustic speech waveform synthesized by Edge-TTS and converted by Direct RVC v2.

#### Upstream Speech Synthesis (Edge-TTS):
- **Base Voice:** Selected from local hardware profile (e.g. `en-US-JennyNeural`, `vi-VN-HoaiMyNeural`, `ja-JP-NanamiNeural`).
- **Base Pitch:** Fixed at `pitch="+60Hz"` in SSML. Clamping invariant: SSML pitch must never be requested above $+60\text{ Hz}$ to avoid cloud saturation.
- **Speech Rate:** Pass `VoiceProsody.speech_rate_pct` directly to SSML `<prosody rate="+X%">`:
  $$\Delta v = \text{clip}\left(15.0 \cdot a - 10.0 \cdot (1.0 - \text{energy}) + 5.0 \cdot (R_{\text{trust}} - 0.50), -20.0, +20.0\right)\%$$
- **Inner XML Invariant:** Zero `<break>` or nested `<prosody>` tags shall be injected into Edge-TTS text (avoids `NoAudioReceived`).

#### Downstream Neural Voice Conversion (Direct RVC v2):
- **Base Semitone Shift ($S_{\text{base}}$):**
  $$S_{\text{base}} = \text{clip}\left(2.0 \cdot p + 1.5 \cdot R_{\text{close}}, -2.0, +4.0\right)\text{ semitones}$$
- **Time-Varying Trajectory ($S(t)$):**
  $$S(t) = S_{\text{base}} + \sum_{k=1}^{K} \Delta S_{\text{focal}, k} \cdot w_{\text{hanning}, k}(t)$$
  where $\Delta S_{\text{focal}} = +2.0\text{ to }+2.5\text{ semitones}$ on designated focal emotional content words.
- **Excitation Scaling:** Continuous fundamental frequency $F_0(t)$ extracted by Parselmouth/pyin is modulated as:
  $$F_0(t) = F_0(t) \cdot 2^{\frac{S(t)}{12}}$$
- **Anti-Aliasing Resampling:** 40 kHz generator output is normalized to $0.90$ (-0.91 dBFS) and resampled to 24 kHz via polyphase filtering (`signal.resample_poly(out, 3, 5)`), guarding against sinc filter overshoot.

---

## 4. Provider-Agnostic Boundary Contract

To support English, Vietnamese, and Japanese uniformly without breaking when a provider lacks word-level timestamps:

```python
@dataclass(frozen=True)
class BoundarySegment:
    text: str
    start_sec: float
    end_sec: float
    is_focal: bool
    segment_type: str  # 'word', 'clause', 'pause'
```

### Language-Specific Ingestion Rules:
1. **English (`en-US`) & Japanese (`ja-JP`):**
   - Ingest Edge-TTS `WordBoundary` events (`offset`, `duration` in 100ns ticks).
   - Convert to seconds: $t_{\text{start}} = \text{offset} / 10^7$, $t_{\text{end}} = (\text{offset} + \text{duration}) / 10^7$.
   - Flag focal words matching key sentiment/action tokens.
2. **Northern Vietnamese (`vi-VN`):**
   - Synthesize using `SentenceBoundary` (avoids `NoAudioReceived`).
   - Run acoustic intensity silence segmentation on decoded `audio_16k` ($<45\text{ dB}$ for $\ge 200\text{ ms}$) to identify clause pauses.
   - Map focal pitch accents to phrase-final content syllables immediately preceding major pauses.
   - **Tonal Invariant:** Northern Vietnamese lexical tones (*sắc, huyền, hỏi, ngã, nặng, ngang*) must preserve their relative pitch profiles without distortion or inversion.

---

## 5. Stability & Multi-Turn Invariants

1. **Feedforward Decoupling Invariant:**
   Vocal audio output, speech rate, and pitch trajectories MUST NEVER feed back into the limbic ODE hidden state ($h$), the slow latent state ($s_{\text{slow}}$), or the relationship state ($R_t$).
2. **Anti-Accumulation Invariant:**
   Actuator values must be computed as instantaneous stateless functions of $(R_t, E_t, S_t)$. Under no circumstances shall pitch or rate accumulate across turns.
3. **Chatter Protection Invariant:**
   All vocal parameter transitions must maintain $C^1$ continuity. Discrete semitone steps across adjacent frames ($\Delta t = 10\text{ ms}$) must not exceed $1.0\text{ semitone}$.
4. **Relational Inertia Invariant:**
   Relational updates in Stage 16 are bounded by $\alpha = 0.03$, guaranteeing that $R_t$ cannot change by more than $3\%$ in a single turn.

---

## 6. Client Actuation Bridge Contract (IPC)

The IPC payload between Electron and the Python FastAPI backend must be explicitly typed:

### Request to `/voice/synthesize`:
```json
{
  "text": "String content to synthesize",
  "rate": "+5%",
  "volume": "+0%",
  "pitch_semitones": 2.5,
  "focal_words": ["morning", "really", "wonderfully"],
  "language": "en"
}
```

### Electron Client Binding (`chat.js`):
When `/chat` returns `response.expression.voice`, `chat.js` MUST NOT discard it. It must forward `response.expression.voice` and `response.relationship` directly into the `window.lucia.voice.synthesize()` call.
