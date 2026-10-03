# Phase 24 — Production Integration Validation Plan
## Adaptive Communication Control Verification Suite

**Document ID:** P24-VAL-001  
**Status:** FORMAL VALIDATION SPECIFICATION (Design Gate Only — Deferred to Future Implementation Phase)  
**Governing ADR:** ADR-032 (tests/evaluation/phase24/P24_ADR_ADAPTIVE_COMMUNICATION.md)  
**Governing Contract:** P24 Adaptive Communication Contract (tests/evaluation/phase24/P24_ADAPTIVE_COMMUNICATION_CONTRACT.md)  
**Evidence Grounding:** P24 Gate 1, Gate 2, Gate 3 Audits  
**Production Invariant:** `production diff = 0` (Zero modifications to `src/core/`, `electron/`, or `data/` during current gate)

---

## 1. Executive Summary & Validation Objective

This validation plan specifies the comprehensive automated verification framework that must be executed **after** an authorized engineering task implements the Phase 24 Adaptive Communication Control Contract in production.

Its primary objectives are:
1. **Mathematical Invariant Verification:** Prove that all actuator outputs are strictly bounded, continuous, and free from runaway or overflow.
2. **Severed Actuator-to-Limbic Feedback:** Formally verify that voice, cadence, and communication actuators do not feed back into the limbic ODE hidden state ($h(t)$) or long-term relational dynamics ($R_t$).
3. **Multi-Turn Stability:** Prove that continuous multi-turn dialogue ($N \ge 50$ turns) maintains stable prosodic and verbal trajectories without parameter drift, chatter, or accumulation.
4. **Cross-Language Acoustic Integrity:** Verify that English, Japanese, and Northern Vietnamese synthesize without error, that Vietnamese lexical tones are strictly preserved, and that provider telemetries map reliably to canonical boundaries.
5. **End-to-End Client IPC Integrity:** Guarantee that `response.expression.voice` is fully forwarded from the FastAPI backend through Electron IPC to the voice synthesis pipeline without silent parameter dropping.

---

## 2. Test Hierarchy & Test Suites

The validation plan defines five mandatory test suites comprising unit, property, multi-turn, acoustic, and end-to-end integration tests:

```text
                               [ Post-Implementation Validation ]
                                                │
         ┌──────────────────┬───────────────────┼───────────────────┬──────────────────┐
         ▼                  ▼                   ▼                   ▼                  ▼
    [ Suite 1 ]        [ Suite 2 ]         [ Suite 3 ]         [ Suite 4 ]        [ Suite 5 ]
     Unit Tests        Multi-Turn          Cross-Language      Property-Based     End-to-End
  (Actuator Logic)     Stability            Acoustic & Tones   Fuzzing Invariants   Client IPC
```

---

### Suite 1: Unit Tests for New & Modified Components

**Target Test File:** `tests/unit/test_p24_adaptive_communication.py`

#### 1.1 `test_relational_voice_conditioning()`
* **Objective:** Verify that `closeness`, `trust`, and `familiarity` modulate `VoiceProsody` according to ADR-032.1, while `reciprocity` is strictly ignored.
* **Assertions:**
  - When $R_{\text{close}}$ varies from $0.0$ to $1.0$, $S_{\text{base}}$ increases by exactly $+1.50\text{ st}$ (monotonic positive correlation).
  - When $R_{\text{trust}}$ varies from $0.0$ to $1.0$, speech rate delta varies smoothly from $-2.5\%$ to $+2.5\%$.
  - When $R_{\text{fam}}$ varies from $0.0$ to $1.0$, clause pause delta varies from $0\text{ ms}$ to $-50\text{ ms}$.
  - When $R_{\text{rec}}$ varies from $0.0$ to $1.0$ (with all other parameters held constant), all `VoiceProsody` outputs remain bit-exact identical:
    $$\frac{\partial (\text{pitch})}{\partial R_{\text{rec}}} \equiv 0, \quad \frac{\partial (\text{rate})}{\partial R_{\text{rec}}} \equiv 0, \quad \frac{\partial (\text{pause})}{\partial R_{\text{rec}}} \equiv 0$$

#### 1.2 `test_dynamic_f0_hanning_contour()`
* **Objective:** Verify that dynamic $F_0$ trajectory generation adheres to ADR-032.2.
* **Assertions:**
  - $C^\infty$ smoothness: $\lim_{t \to t_{\text{start}}^+} S'(t) = 0$ and $\lim_{t \to t_{\text{end}}^-} S'(t) = 0$.
  - Boundedness: $S(t) \in [-4.0, +7.0]\text{ st}$ under any legal input combination.
  - Hard safety clamp: $\text{clip}(S(t), -12.0, +12.0)\text{ st}$ cannot be breached even with synthetic out-of-bounds focal shifts.
  - Maximum frame-to-frame jump: $|\Delta S / \Delta t| \le 1.0\text{ st / } 10\text{ ms}$ across all sampled intervals.

#### 1.3 `test_canonical_boundary_abstraction()`
* **Objective:** Verify boundary parsing across supported languages per ADR-032.3.
* **Assertions:**
  - For English (`en-US-JennyNeural`): Ingests `WordBoundary` events and produces valid `BoundarySegment` instances with non-overlapping timestamps.
  - For Japanese (`ja-JP-NanamiNeural`): Ingests `WordBoundary` events and produces valid `BoundarySegment` instances matching Japanese token boundaries.
  - For Vietnamese (`vi-VN-HoaiMyNeural`): Requests with `SentenceBoundary` (default) bypass `WordBoundary` without raising `NoAudioReceived`. The acoustic intensity parser detects clause pauses ($< 45\text{ dB}$ for $\ge 200\text{ ms}$) and returns valid `BoundarySegment` instances.

#### 1.4 `test_cadence_formatting_bounds()`
* **Objective:** Verify that text cadence orthography adheres to Section 3.2 of the contract.
* **Assertions:**
  - Punctuation insertion produces valid trailing ellipsis (`...`), clause commas (`,`), or exclamation marks (`!`).
  - No interior word splitting (e.g. `hel...lo` is forbidden).
  - Maximum punctuation count per response $\le 3$.
  - Zero XML / SSML tags injected into text passed to TTS.

---

### Suite 2: Multi-Turn Stability & Anti-Chatter Tests

**Target Test File:** `tests/evaluation/phase24/test_p24_multiturn_stability.py`

#### 2.1 `test_parameter_drift_free_over_50_turns()`
* **Objective:** Verify that repeated conversational turns under stationary limbic/relational conditions do not accumulate pitch or rate.
* **Methodology:**
  - Initialize system with fixed state: $R = [0.4, 0.6, 0.3, 0.5]^T$, $E = [0.2, -0.1, 0.0]^T$, $S = [0.8, 0.2, 0.7, 0.1]^T$.
  - Execute 50 sequential synthetic turns through `CommunicationPolicy` and `ExpressionPolicy`.
  - Record verbal parameters, cadence punctuation, and vocal prosody parameters at each turn.
* **Assertions:**
  - Standard deviation of computed $S_{\text{base}}$ across 50 turns = $0.0\text{ st}$ (strict determinism).
  - Rate, directness, and formality remain stationary without drift: $\max |x_t - x_0| = 0.0$.

#### 2.2 `test_limbic_feedforward_isolation()`
* **Objective:** Formally prove the Feed-Forward Invariant: actuator outputs cannot mutate limbic or relational state.
* **Methodology:**
  - Record full internal state snapshots of `EmotionCore` (hidden vector $h \in \mathbb{R}^{16}$, slow state $s_{\text{slow}} \in \mathbb{R}^{16}$) and `RelationshipEngine` ($R_t$).
  - Execute speech synthesis with extreme actuator values (e.g. $+12\text{ st}$, $+20\%$ rate, multiple focal accents).
  - Inspect internal state snapshots after execution.
* **Assertions:**
  - $h_{\text{after}} \equiv h_{\text{before}}$ (zero modification to limbic ODE hidden state).
  - $s_{\text{slow, after}} \equiv s_{\text{slow, before}}$ (zero modification to slow limbic state).
  - $R_{\text{after}} \equiv R_{\text{before}}$ (zero modification to relational state).

---

### Suite 3: Cross-Language Acoustic & Tone Preservation Tests

**Target Test File:** `tests/evaluation/phase24/test_p24_acoustic_cross_language.py`

#### 3.1 `test_vietnamese_lexical_tone_preservation()`
* **Objective:** Prove that dynamic F0 modulation does not invert or flatten Northern Vietnamese lexical tones.
* **Methodology:**
  - Synthesize Vietnamese phonetically rich test sentences containing all 6 tones:
    * *Ngang* (level, e.g. "ba")
    * *Huyền* (falling, e.g. "bà")
    * *Sắc* (rising, e.g. "bá")
    * *Hỏi* (dipping-rising, e.g. "bả")
    * *Ngã* (glottalized rising, e.g. "bã")
    * *Nặng* (glottalized falling, e.g. "bạ")
  - Extract pitch contour via Parselmouth/Praat before and after RVC semitone shift ($S_{\text{base}} = +2.0\text{ st}$).
* **Assertions:**
  - Monotonicity preservation: The relative slope sign ($\text{sign}(\frac{d F_0}{dt})$) for falling tones (*huyền, nặng*) remains negative.
  - Rising tone preservation: The slope sign for rising tones (*sắc, ngã*) remains positive.
  - Dipping-rising contour: Dipping tones (*hỏi*) retain minimum pitch inflection points.
  - Zero glottal drop corruption: Glottal closure in *nặng* and *ngã* is preserved without synthetic clicks.

#### 3.2 `test_japanese_mora_and_pitch_accent()`
* **Objective:** Prove that Japanese character voice synthesis with `ja-JP-NanamiNeural` + Varesa RVC maintains natural pitch accents.
* **Methodology:**
  - Synthesize standard Japanese test utterances (e.g. 「こんにちは、調子はどうですか？」).
  - Measure fundamental frequency curve, formant frequencies ($F_1, F_2, F_3$), and subjective clarity.
* **Assertions:**
  - Pitch accent drops (e.g. *atamadaka* / *nakadaka* accent falls) are preserved within $\pm 10\%$.
  - RVC index retrieval prevents synthetic buzzing or robotic flattening.

---

### Suite 4: Property-Based Fuzzing & Invariant Tests

**Target Test File:** `tests/property/test_p24_adaptive_communication_properties.py`

Using `hypothesis` to fuzz the entire input hypercube:

#### 4.1 `test_actuator_output_bounds_property()`
* **Hypothesis Strategy:**
  - $R_t \sim \text{st.floats}(0.0, 1.0)$ for each dimension.
  - $E_t \sim \text{st.floats}(-1.0, 1.0)$ for each dimension.
  - $S_t \sim \text{st.floats}(0.0, 1.0)$ for each dimension.
* **Invariants Checked:**
  - Directness $\in [0.10, 0.95]$.
  - Formality $\in [0.00, 1.00]$.
  - Supportiveness $\in [0.00, 1.00]$.
  - Acknowledgement $\in [0.10, 1.00]$.
  - Question Frequency $\in [0.00, 1.00]$.
  - Elaboration Depth $\in [0.10, 1.00]$.
  - Speech Rate Delta $\in [-20.0, +20.0]\%$.
  - Volume Delta $\in [-20.0, +20.0]\%$.
  - Base Semitone Shift $\in [-2.0, +4.0]\text{ st}$.
  - Instantaneous Semitone Shift $S(t) \in [-4.0, +7.0]\text{ st}$.
  - Clause Pause Delta $\in [-50.0, 0.0]\text{ ms}$.
  - Zero `NaN`, zero `Inf`, zero Python exceptions raised.

---

### Suite 5: End-to-End Client IPC Integration Tests

**Target Test File:** `tests/integration/test_p24_client_actuation_bridge.py`

#### 5.1 `test_fastapi_to_renderer_ipc_passthrough()`
* **Objective:** Verify that `response.expression.voice` travels from `CognitiveTurnResult` through FastAPI, Electron IPC, and into `VoiceEngine` without loss.
* **Methodology:**
  - Dispatch a simulated `/chat` query with high closeness ($R_{\text{close}} = 0.90$) and joyful affect ($p = +0.70$).
  - Intercept the FastAPI response JSON: verify presence of `expression.voice.pitch_shift_hz`, `speech_rate_pct`, `volume_pct`.
  - Simulate the Electron renderer execution (`chat.js` logic): verify that `window.lucia.voice.synthesize` receives `options` populated with `{ pitch_hz, rate, volume, closeness }`.
  - Intercept IPC call to backend `/voice/synthesize`: verify that parameters match the original cognitive output.
* **Assertions:**
  - Zero parameters dropped across process boundaries.
  - Client fallback: If `response.expression` is missing or null, default options `{ rate: "+0%", volume: "+0%", pitch_hz: 0.0 }` are safely applied.

---

## 3. Pass/Fail Acceptance Criteria Matrix

| Criterion | Target Metric | Hard Failure Threshold | Verification Suite |
|:---|:---:|:---:|:---:|
| **Actuator Boundedness** | 100% within contract bounds | $>0$ violations in $10^5$ fuzz samples | Suite 4 |
| **Reciprocity Isolation** | $\frac{\partial \text{actuator}}{\partial R_{\text{rec}}} \equiv 0.0$ | Any non-zero derivative | Suite 1, Suite 4 |
| **Multi-Turn Drift** | Max parameter drift $= 0.0$ | $|\Delta x| > 10^{-5}$ across 50 turns | Suite 2 |
| **Limbic Feedforward Isolation** | $\Delta h = 0.0, \Delta R_t = 0.0$ | Any modification to ODE state | Suite 2 |
| **Vietnamese Tone Fidelity** | 100% slope sign consistency | Any inverted contour | Suite 3 |
| **Boundary Telemetry Reliability** | 100% valid `BoundarySegment` | Any unhandled exception / crash | Suite 1, Suite 3 |
| **End-to-End IPC Delivery** | 100% parameter transmission | Any dropped parameter in `chat.js` | Suite 5 |
| **Synthesis Latency Overhead** | $\le 15\text{ ms}$ over baseline | $> 50\text{ ms}$ additional latency | Suite 3, Suite 5 |

---

## 4. Execution Sequence for Future Implementation Task

When the project lead authorizes implementation of Phase 24 Adaptive Communication, the executing agent MUST adhere to this strict sequential procedure:

```text
Step 1: Backend Domain Models & Invariants
        - Add BoundarySegment dataclass to src/core/voice/
        - Update VoiceProsody dataclass to store semitone parameters
        │
        ▼
Step 2: Actuator Logic in Core
        - Implement relational terms in ExpressionPolicy (src/core/expression/expression_policy.py)
        - Implement dynamic F0 Hanning trajectory in Direct RVC (src/core/voice/rvc_synthesizer.py)
        - Wire provider-agnostic boundary extractor with VI acoustic fallback
        │
        ▼
Step 3: API & Protocol Updates
        - Update /voice/synthesize request schema in src/api/server.py
        - Update /chat response schema validation
        │
        ▼
Step 4: Electron Client Bridge
        - Update chat.js:1287 to forward response.expression.voice to window.lucia.voice.synthesize
        - Update preload.js if IPC channel signature requires modification
        │
        ▼
Step 5: Execute Validation Plan
        - Run Suite 1 (Unit Tests)
        - Run Suite 2 (Multi-Turn Stability)
        - Run Suite 3 (Cross-Language Acoustic)
        - Run Suite 4 (Property-Based Fuzzing)
        - Run Suite 5 (End-to-End IPC)
        │
        ▼
Step 6: Regression & Invariant Audit
        - Run full regression suite (tests/unit/, tests/property/)
        - Confirm zero violations of L1 Invariants
```

---

## 5. Governance Freezes & Authority Statement

- **Design Gate Authority:** This validation plan establishes the definitive acceptance criteria for Phase 24 Adaptive Communication.
- **Implementation Lock:** No tests from this plan may be committed to `tests/unit/` or run against production code until the implementation task is explicitly authorized by the user.
- **Production Invariant Preservation:** At the conclusion of this Design / ADR Gate, production diff remains exactly `0`.
