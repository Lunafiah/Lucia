# P24 Gate 3 — Canonical Control-Surface Matrix

**Document Status:** Evaluation Evidence & Architectural Classification  
**Target Milestone:** Phase 24 Gate 3 (Affective Communication Adaptation Integration Audit)  
**Authors / Auditors:** Antigravity Pairing Agent  
**Production Invariant:** `production diff = 0` (Zero modification to `src/core/`, `electron/`, or `data/`)

---

## 1. Classification Taxonomy

Each control surface is evaluated under strict empirical criteria:
- **`IMPLEMENTED`**: Present in production source code (`src/core/`).
- **`VERIFIED`**: Implemented, verified by unit/property tests, and actively executing in the turn pipeline.
- **`PARTIALLY VERIFIED`**: Implemented in code, but either disconnected at subsystem boundaries, partially evaluated, or subject to technical limitations.
- **`EXPERIMENTAL`**: Empirically demonstrated in evaluation harnesses (`tests/evaluation/phase24/`), but not promoted to production contracts.
- **`UNRESOLVED`**: Conceptually defined, but lacking mathematical bounds, causal attribution, or empirical data.
- **`BLOCKED`**: Incapable of functioning without architectural decision records (ADR) or client interface modifications.

---

## 2. Master Control-Surface Matrix

| Internal Signal | Mathematical Domain | Signal Source Subsystem | Canonical Consumer Subsystem | Actuation Target | Control Transfer Function | Verification Evidence | Classification Status | Safe for P24? |
|:---|:---:|:---|:---|:---|:---|:---|:---:|:---:|
| **Familiarity** | $[0.0, 1.0]$ | `RelationshipState` (`state.py:24`) | `CommunicationPolicy` (`comm_policy.py:114`) | `acknowledgement_level` | Linear term: $+0.25 \cdot \text{fam}$ | Verified in Stage 10 & test harness | **VERIFIED** | **YES** (Bounded, no feedback) |
| **Trust** | $[0.0, 1.0]$ | `RelationshipState` (`state.py:25`) | `CommunicationPolicy`, `ExpressionPolicy` | `directness`, `supportiveness`, `formality`, `question_freq`, `gaze_aversion` | Linear offset: $\pm \alpha (\text{trust} - 0.50)$ | Verified in Stage 10 & 15 | **VERIFIED** | **YES** (Bounded, stable attractor) |
| **Closeness** | $[0.0, 1.0]$ | `RelationshipState` (`state.py:26`) | `CommunicationPolicy`, `ExpressionPolicy` | `directness`, `supportiveness`, `formality` | Linear term: $\pm \beta \cdot \text{close}$ | Verified in Stage 10 & 15 | **VERIFIED** | **YES** (Bounded, stable attractor) |
| **Reciprocity** | $[0.0, 1.0]$ | `RelationshipState` (`state.py:27`) | `EmotionCore` (`emotion_core.py:855`) | Limbic slow-layer displacement $s^*_{\text{eff}}(R)$ | Linear mapping: $W_{\text{rel}} (R_t - R_0)$, $\|W_{\text{rel}}\|_2 \le 0.08$ | Verified in Phase 21 consolidation | **PARTIALLY VERIFIED** | **YES** (Strictly bounded by spectral norm) |
| **Affective State (PAD)** | $[-1.0, 1.0]^3$ | `EmotionCore` (`emotion_core.py`) | `CommunicationPolicy`, `ExpressionPolicy`, `ActiveInference` | Style, prosody, facial, posture, prediction error | Linear/affine projection: $A \cdot \text{PAD} + b$ | Verified in Stage 3, 4, 10, 15 | **VERIFIED** | **YES** (ODE dissipative, Philia attractor) |
| **Somatic Markers** | $[0.0, 1.0]^4$ | `HomeostaticEngine` (`models.py:58`) | `CommunicationPolicy`, `ExpressionPolicy`, `PromptAssembler` | Pacing latency, elaboration, speech rate, pause duration | Linear clamp: $c_1 \cdot \text{load} + c_2 \cdot \text{tens}$ | Verified in Stage 5, 10, 12, 15 | **VERIFIED** | **YES** (Strictly bounded in $[0, 1]$) |
| **Verbal Formality** | $[0.0, 1.0]$ | `CommunicationPolicy` (`comm_policy.py:111`) | `PromptAssembler` (`prompt_assembler.py:128`) | LLM system prompt `[COMMUNICATION STRATEGY]` | Prompt string formatting | Verified in S11 prompt assembly | **VERIFIED** | **YES** (Direct conditioning) |
| **Verbal Directness** | $[0.10, 0.95]$ | `CommunicationPolicy` (`comm_policy.py:102`) | `PromptAssembler` (`prompt_assembler.py:128`) | LLM system prompt `[COMMUNICATION STRATEGY]` | Prompt string formatting | Verified in S11 prompt assembly | **VERIFIED** | **YES** (Direct conditioning) |
| **Verbal Supportiveness**| $[0.0, 1.0]$ | `CommunicationPolicy` (`comm_policy.py:108`) | `PromptAssembler` (`prompt_assembler.py:128`) | LLM system prompt `[COMMUNICATION STRATEGY]` | Prompt string formatting | Verified in S11 prompt assembly | **VERIFIED** | **YES** (Direct conditioning) |
| **Verbal Elaboration** | $[0.10, 1.0]$ | `CommunicationPolicy` (`comm_policy.py:105`) | `PromptAssembler` (`prompt_assembler.py:128`) | LLM system prompt `[COMMUNICATION STRATEGY]` | Prompt string formatting | Verified in S11 prompt assembly | **VERIFIED** | **YES** (Direct conditioning) |
| **Verbal Acknowledgement**| $[0.10, 1.0]$ | `CommunicationPolicy` (`comm_policy.py:114`) | None (Omitted from PromptAssembler) | None | Dropped at Stage 11 | Verified computed, but dropped | **PARTIALLY VERIFIED** | **YES** (Safe, but inactive) |
| **Verbal Question Freq**| $[0.0, 1.0]$ | `CommunicationPolicy` (`comm_policy.py:117`) | None (Omitted from PromptAssembler) | None | Dropped at Stage 11 | Verified computed, but dropped | **PARTIALLY VERIFIED** | **YES** (Safe, but inactive) |
| **Pacing Latency** | $[0, 1000]\text{ ms}$ | `CommunicationPolicy` (`comm_policy.py:122`) | `CognitiveOrchestrator` (`cognitive_orchestrator.py:503`)| Physical pre-generation delay | `time.sleep(pacing_ms / 1000.0)` | Verified in Stage 12 | **VERIFIED** | **YES** (Hard cap $\le 1000\text{ ms}$) |
| **Voice Pitch (SSML)** | $[-30, +30]\text{ Hz}$ | `VoiceProsody` (`expression_state.py:40`)| `VoiceEngine` (`voice_engine.py:146`) | Edge-TTS SSML `<prosody pitch>` | Affine offset in Hz | Discarded by client (`chat.js:1287`); clamps above $+80\text{ Hz}$ | **PARTIALLY VERIFIED** | **LIMITED** (Saturates at $+80\text{ Hz}$) |
| **Voice Rate (SSML)** | $[-25, +25]\%$ | `VoiceProsody` (`expression_state.py:41`)| `VoiceEngine` (`voice_engine.py:146`) | Edge-TTS SSML `<prosody rate>` | Affine percentage | Discarded by client; Gate 2 verified linear | **PARTIALLY VERIFIED** | **YES** (Linear acoustic response) |
| **Voice Volume (SSML)** | $[-20, +20]\%$ | `VoiceProsody` (`expression_state.py:42`)| `VoiceEngine` (`voice_engine.py:146`) | Edge-TTS SSML `<prosody volume>` | Affine percentage | Discarded by client (`chat.js:1287`) | **PARTIALLY VERIFIED** | **YES** |
| **Voice Pause Duration** | $[100, 1000]\text{ ms}$| `VoiceProsody` (`expression_state.py:43`)| None | None | Parameter has no consumer in `VoiceEngine` | Edge-TTS rejects inner `<break>` tags | **BLOCKED** | **NO** (Rejected by Edge-TTS server) |
| **Cadence (Punctuation)**| Orthographic | Prompt Formatting / LLM text | Edge-TTS Neural Text Front-End | Pause insertion & intonation reset | Orthographic parsing (`...`, `,`, `!`) | Gate 2 benchmark verified | **EXPERIMENTAL** | **YES** (No cloud or local risk) |
| **Dynamic F0 Trajectory**| Semitone array | Dynamic contour $S(t)$ | Direct RVC v2 (`rvc_pipeline.py:309`) | Excitation pitch in RVC vocoder | $F_0(t) \cdot 2^{S(t)/12}$ | Gate 2 & Gate 3 benchmark verified | **EXPERIMENTAL** | **YES** (Bounded $[-12, +12]\text{ st}$) |
| **Facial Expressions** | $[0.0, 1.0]^5$ | `FacialExpression` (`expression_state.py:54`)| Electron Avatar Renderer | Live2D / VRM blendshape weights | Discarded by client (`chat.js`) | Computed at S15, ignored by renderer | **BLOCKED** | **YES** (State bounded, consumer missing) |
| **Posture & Gaze** | $[-10^\circ, 10^\circ]$, $[0, 1]$| `PostureGaze` (`expression_state.py:71`) | Electron Avatar Renderer | Avatar head tilt & eye contact | Discarded by client (`chat.js`) | Computed at S15, ignored by renderer | **BLOCKED** | **YES** (State bounded, consumer missing) |

---

## 3. Key Architectural Observations

1. **The Verbal Surface is Active and Verified:**
   `familiarity`, `trust`, and `closeness` have direct mathematical and prompt-level pathways to influence LLM generation.
2. **The Vocal Surface is Fragmented:**
   - Vocal parameters are calculated in `ExpressionPolicy`, but discarded at the Electron IPC boundary.
   - Even if passed, `pause_duration_ms` cannot be actuated via Edge-TTS SSML because Edge-TTS rejects inner `<break>` tags.
   - Punctuation cadence and dynamic $F_0$ contouring provide the actual working acoustic control surface, but are currently classified as `EXPERIMENTAL` because they reside in evaluation harnesses rather than production contracts.
3. **Reciprocity is Limbic-Only:**
   `reciprocity` is safely coupled to the slow limbic attractor $W_{\text{rel}}$, but has zero direct connection to communicative or vocal parameters.
