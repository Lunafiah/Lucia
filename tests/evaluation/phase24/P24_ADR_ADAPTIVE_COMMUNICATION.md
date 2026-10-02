# ADR-032: Phase 24 Adaptive Communication Control Architecture

**Document ID:** ADR-032 (Arch-032)  
**Status:** PROPOSED ARCHITECTURAL DECISION RECORD (Design Gate Only — Not Promoted to Production)  
**Date:** 2026-09-28  
**Context:** Phase 24 Gate 1, Gate 2, and Gate 3 Audits  
**Deciders:** AI Pairing Agent (Antigravity), Human Project Lead (User)  
**Production Invariant:** `production diff = 0` (Zero modifications to `src/core/`, `electron/`, or `data/`)

---

## 1. Context & Problem Statement

Phase 24 establishes the empirical foundation for **Adaptive Communication** in Lucia. Through the completion of Gate 1 (Canonical Relational State Audit), Gate 2 (Voice Stack Control Surface Audit), and Gate 3 (Affective Adaptation Integration Audit), two major operational facts were established:

1. **The Verbal Path is Active:** Relational state $R_t = [\text{familiarity}, \text{trust}, \text{closeness}, \text{reciprocity}]^T \in [0, 1]^4$ and affective state $E_t \in [-1, 1]^3$ mathematically modulate verbal style parameters (`directness`, `formality`, `elaboration`, `supportiveness`) in `CommunicationPolicy` (Stage 10), which are injected into the LLM system prompt via `PromptAssembler` (Stage 11).
2. **The Vocal Path is Severed at the Client Boundary:** `ExpressionPolicy` (Stage 15) computes vocal prosody (`pitch_shift_hz`, `speech_rate_pct`, `volume_pct`, `pause_duration_ms`) and returns it in `CognitiveTurnResult.expression`, but the Electron client (`electron/renderer/chat/chat.js:1287`) discards `response.expression` and calls `/voice/synthesize` with only the raw text string. Furthermore, `VoiceProsody` currently depends exclusively on instantaneous affect ($E_t$) and somatic markers ($S_t$), with zero relational terms ($R_t$).
3. **Cloud TTS Clamping & Vocoder Formants:** Microsoft Edge-TTS saturates and clamps SSML `pitch="+XHz"` above $+80\text{ Hz}$ ($\Delta = 0.0\text{ Hz}$), causing higher pitch requests to sound identical. However, RVC direct fundamental frequency scaling ($F_0 \cdot 2^{\Delta / 12}$) operates monotonically and preserves character formant identity.

Lucia requires a bounded, interpretable, deterministic, feedforward architectural contract to connect relational state ($R_t$) and affective state ($E_t$) into verbal style, cadence, and vocal prosody without introducing speculative autonomous behavior or violating existing architectural invariants.

---

## 2. Decision Matrix & Explicit ADR Decisions

### ADR-032.1: Relational → Vocal Conditioning Policy
* **Problem:** Can relational state dimensions (`closeness`, `trust`, `familiarity`, `reciprocity`) safely influence vocal prosody?
* **Decision:**
  1. **`closeness` is APPROVED for vocal conditioning:** Relational closeness represents accumulated interpersonal proximity and shared context. It shall contribute a gentle positive offset to baseline vocal pitch and relaxation:
     $$\Delta S_{\text{close}} = +1.5 \cdot R_{\text{closeness}} \text{ semitones} \quad (\in [0.0, +1.5]\text{ st})$$
  2. **`trust` is APPROVED for speech rate stability:** High trust reduces tension and stabilizes speech rate variance:
     $$\Delta v_{\text{trust}} = +5.0 \cdot (R_{\text{trust}} - 0.50) \% \quad (\in [-2.5\%, +2.5\%])$$
  3. **`familiarity` is APPROVED for pause reduction:** High familiarity slightly reduces clause boundary pauses:
     $$\Delta \tau_{\text{pause, fam}} = -50.0 \cdot R_{\text{familiarity}} \text{ ms} \quad (\in [-50\text{ ms}, 0\text{ ms}])$$
  4. **`reciprocity` is STRICTLY BLOCKED from direct vocal modulation:** Reciprocity currently couples exclusively to the slow limbic attractor displacement via $W_{\text{rel}} (R_t - R_0)$ ($\|W_{\text{rel}}\|_2 \le 0.08$) in EmotionCore Phase 21. No empirical evidence exists defining how reciprocity should modulate vocal parameters. It must NOT be arbitrarily wired into voice synthesis.
* **Status:** `PROPOSED (ADR-032.1)`

---

### ADR-032.2: Dynamic $F_0$ Trajectory & Focal Accentuation Contract
* **Problem:** Global constant semitone shifts ($F_0 \cdot C$) cause speech to feel rigid and unnatural across words. How should dynamic $F_0$ modulation be formalized?
* **Decision:**
  Formalize the experimentally verified Hanning-window trajectory into the RVC vocoder contract:
  $$S(t) = S_{\text{base}} + \sum_{k=1}^{K} \Delta S_{\text{focal}, k} \cdot w_{\text{hanning}, k}(t)$$
  - **Base Semitone Domain:** $S_{\text{base}} \in [-2.0, +4.0]\text{ semitones}$.
  - **Focal Accent Domain:** $\Delta S_{\text{focal}} \in [0.0, +2.5]\text{ semitones}$.
  - **Instantaneous Total Bounds:** $S(t) \in [-4.0, +7.0]\text{ semitones}$.
  - **Hard Safety Clipping:** $\text{clip}(S(t), -12.0, +12.0)\text{ semitones}$ (maximum $\pm 1$ musical octave).
  - **Window Function:** $w_{\text{hanning}}(t) = \frac{1}{2} \left(1 - \cos\left(\frac{2\pi (t - t_{\text{start}})}{t_{\text{end}} - t_{\text{start}}}\right)\right)$ for $t \in [t_{\text{start}}, t_{\text{end}}]$, guaranteeing $C^\infty$ continuity with zero derivative at word boundaries.
  - **Chatter Prevention:** Frame-to-frame pitch jump $|\Delta S / \Delta t| \le 1.0\text{ st / } 10\text{ ms}$ is mathematically enforced by the Hanning window duration ($T \ge 150\text{ ms}$).
* **Status:** `PROPOSED (ADR-032.2)`

---

### ADR-032.3: Provider-Agnostic Boundary Representation & Vietnamese Fallback
* **Problem:** Edge-TTS `en-US-JennyNeural` and `ja-JP-NanamiNeural` support `boundary="WordBoundary"`, but `vi-VN-HoaiMyNeural` strictly rejects `WordBoundary` with `NoAudioReceived`. Downstream prosody must not break across languages.
* **Decision:**
  Define a canonical provider-agnostic internal boundary representation:
  ```python
  @dataclass(frozen=True)
  class BoundarySegment:
      text: str
      start_sec: float
      end_sec: float
      is_focal: bool
      segment_type: Literal["word", "clause", "pause"]
  ```
  - For **English (EN)** and **Japanese (JP)**: Ingest Edge-TTS `WordBoundary` events and convert 100ns ticks to `start_sec`, `end_sec`.
  - For **Northern Vietnamese (VI)**: Synthesize with `SentenceBoundary` (default) and execute local acoustic intensity pause detection ($<45\text{ dB}$ for $\ge 200\text{ ms}$) on `audio_16k` to locate clause pauses, mapping focal boosts to phrase-final content syllables.
  - **Invariant:** Vietnamese lexical tones (*ngang, huyền, sắc, hỏi, ngã, nặng*) must never be inverted or compressed.
* **Status:** `PROPOSED (ADR-032.3)`

---

### ADR-032.4: Acoustic Parameter Translation Contract
* **Problem:** `VoiceProsody` currently generates `pitch_shift_hz` in Hertz, which is unsuitable for Edge-TTS (clamping at $+80\text{ Hz}$) and does not match RVC's semitone inputs.
* **Decision:**
  Decouple upstream cadence/rate from downstream character pitch:
  1. **Upstream Edge-TTS Parameters:**
     - `rate`: Pass `VoiceProsody.speech_rate_pct` directly to Edge-TTS SSML `<prosody rate="+X%">` (linear $[-20\%, +20\%]$).
     - `pitch`: Fix Edge-TTS at `pitch="+60Hz"` to ensure a bright, linear cloud prosodic base below the $+80\text{ Hz}$ saturation ceiling.
     - `inner SSML`: Zero `<break>` or nested `<prosody>` tags shall be injected into Edge-TTS text (avoids `NoAudioReceived`).
  2. **Downstream RVC Parameters:**
     - Translate `pitch_shift_hz` and relational closeness to semitone shift:
       $$S_{\text{base}} = \text{clip}\left(12.0 \cdot \log_2\left(1.0 + \frac{\text{pitch\_shift\_hz}}{250.0}\right) + 1.5 \cdot R_{\text{closeness}}, -2.0, +4.0\right)\text{ st}$$
     - Apply dynamic trajectory $S(t)$ to continuous $F_0$: $F_0(t) = F_0(t) \cdot 2^{S(t) / 12}$.
* **Status:** `PROPOSED (ADR-032.4)`

---

### ADR-032.5: Client Actuation Bridge & IPC Protocol Repair
* **Problem:** In `electron/renderer/chat/chat.js:1287`, the client calls `window.lucia.voice.synthesize(response.response)` without passing `response.expression.voice`, silently dropping all prosodic parameters.
* **Decision:**
  Update the client IPC contract in `chat.js`:
  ```javascript
  // Forward expression parameters from /chat response to voice synthesizer
  const voiceOpts = response.expression && response.expression.voice ? {
    rate: `${response.expression.voice.speech_rate_pct >= 0 ? '+' : ''}${Math.round(response.expression.voice.speech_rate_pct)}%`,
    volume: `${response.expression.voice.volume_pct >= 0 ? '+' : ''}${Math.round(response.expression.voice.volume_pct)}%`,
    pitch_hz: response.expression.voice.pitch_shift_hz,
    closeness: response.relationship ? response.relationship.closeness : 0.0
  } : {};

  const audioBuffer = await window.lucia.voice.synthesize(response.response, voiceOpts);
  ```
  - In `electron/preload/preload.js`: `synthesize: (text, opts = {}) => ipcRenderer.invoke('voice:synthesize', { text, ...opts })`.
  - In `electron/main/ipc-bridge.js`: forward `opts` in POST request body to `/voice/synthesize`.
  - In `src/api/server.py:435`: expand `SynthesizeRequest` to accept `pitch_hz` and `closeness`.
* **Status:** `PROPOSED (ADR-032.5)`

---

## 3. Decisions Intentionally NOT Made

The following decisions are explicitly deferred or rejected:
1. **NO Direct Vocal Reciprocity Coupling:** Reciprocity remains restricted to EmotionCore limbic attractor displacement ($W_{\text{rel}}$). It is NOT authorized to modulate voice.
2. **NO Autonomous Unrestricted Text Rewriting:** LLM cadence formatting is restricted to punctuation conditioning (`...`, `,`, `!`) guided by formality. Autonomous stylistic post-processing or rewriting is prohibited.
3. **NO Facial Blendshape Binding in this ADR:** Binding `ExpressionState.facial` to Live2D/VRM morph targets is an avatar renderer concern and is deferred to an avatar-specific ADR.
4. **NO Cloud API Fallbacks:** All voice synthesis and conversion remain strictly 100% local edge (Edge-TTS browser websocket + local CPU/CUDA RVC).

---

## 4. Consequences & Impact

### Positive
- Closes the verified client-side actuation gap where prosody was computed but discarded.
- Bypasses cloud SSML saturation at $+80\text{ Hz}$ by utilizing RVC neural semitone excitation.
- Eliminates mechanical, rushed turn delivery by introducing natural respiratory pauses.
- Preserves all Phase 21/22/23 invariants with zero internal feedback into limbic state.

### Negative / Trade-Offs
- Requires a multi-language boundary abstraction because Vietnamese does not emit `WordBoundary`.
- CPU inference latency for RVC remains $\approx 6$–$8\text{ seconds}$ per turn on pure CPU until GPU CUDA execution is enabled.

---

## 5. Governance Classification

```text
ADR-032 STATUS: DESIGN GATE PASS (ARCHITECTURE APPROVED FOR PROMOTION PLANNING)
PRODUCTION IMPLEMENTATION STATUS: LOCKED (AWAITING USER AUTHORIZATION)
```
