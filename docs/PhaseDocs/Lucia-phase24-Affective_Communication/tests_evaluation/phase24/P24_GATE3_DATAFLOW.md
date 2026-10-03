# P24 Gate 3 — End-to-End Dataflow & Actuation Audit

**Document Status:** Evaluation Evidence & Architectural Audit  
**Target Milestone:** Phase 24 Gate 3 (Affective Communication Adaptation Integration Audit)  
**Authors / Auditors:** Antigravity Pairing Agent  
**Production Invariant:** `production diff = 0` (Zero modification to `src/core/`, `electron/`, or `data/`)

---

## 1. Executive Summary

This document traces the complete causal dataflow from internal relational state ($R_t$) and affective state ($E_t$) to physical verbal and vocal output in Lucia.

The audit proves a major architectural dichotomy:
1. **The Verbal Path is Intact:** $R_t \rightarrow \text{CommunicationPolicy} \rightarrow \text{PromptAssembler} \rightarrow \text{LLM}$ is fully wired in production.
2. **The Vocal Actuation Path is Severed at the Client Boundary:** While `ExpressionPolicy` mathematically computes vocal prosody (`pitch_shift_hz`, `speech_rate_pct`, `volume_pct`, `pause_duration_ms`) and returns it in `CognitiveTurnResult`, the Electron renderer (`electron/renderer/chat/chat.js:1287`) discards `response.expression` and calls `/voice/synthesize` with only the raw text string.

---

## 2. Canonical Production Dataflow Trace

```text
                                  ┌────────────────────────┐
                                  │   User Input String    │
                                  └───────────┬────────────┘
                                              │ Stage 1: Sensory Encoding
                                              ▼
                                  ┌────────────────────────┐
                                  │ Stimulus Vector (16D)  │
                                  └───────────┬────────────┘
                                              │ Stage 3: Limbic ODE Integration
                                              ▼
                                  ┌────────────────────────┐
                                  │ PAD State (P, A, D)    │
                                  └─────┬──────────────┬───┘
               Stage 5: Somatics        │              │ Stage 9: Read Relational State
                        ┌───────────────┘              └────────────────┐
                        ▼                                               ▼
             ┌─────────────────────┐                         ┌─────────────────────┐
             │   Somatic Markers   │                         │  RelationshipState  │
             │(load, energy, tens) │                         │ (fam, trust, close, │
             └──────────┬──────────┘                         │     reciprocity)    │
                        │                                    └──────────┬──────────┘
                        │           Stage 10: Communication Policy      │
                        └───────────────────────┬───────────────────────┘
                                                ▼
                                    ┌───────────────────────┐
                                    │  CommunicationState   │
                                    │ (direct, formal, etc) │
                                    └───────────┬───────────┘
                                                │ Stage 11: Prompt Assembler
                                                ▼
                                    ┌───────────────────────┐
                                    │   Conditioned Prompt  │
                                    │ [COMMUNICATION STRAT] │
                                    └───────────┬───────────┘
                                                │ Stage 13: Local Small Language Model
                                                ▼
                                    ┌───────────────────────┐
                                    │ Raw LLM Response Text │
                                    └───────────┬───────────┘
                                                │ Stage 13: BoundaryLayer Validator
                                                ▼
                                    ┌───────────────────────┐
                                    │ Safe Response Text    │
                                    └─────┬───────────┬─────┘
          Stage 15: Expression Policy     │           │
          (Post-generation evaluation)    │           │ Stage 16: Persistence & Learning
                  ┌───────────────────────┘           └───────────────┐
                  ▼                                                   ▼
       ┌─────────────────────┐                             ┌─────────────────────┐
       │   ExpressionState   │                             │ Updated R_{t+1}     │
       │• TextStyle          │                             │ Plasticity Queue    │
       │• VoiceProsody       │                             │ Affective Memory    │
       │• FacialExpression   │                             └─────────────────────┘
       │• PostureGaze        │
       └──────────┬──────────┘
                  │
                  ▼
       ┌────────────────────────────────────────────────────────┐
       │ CognitiveTurnResult (returned by Orchestrator.process) │
       │ { response, expression, relationship, communication }  │
       └──────────────────────────┬─────────────────────────────┘
                                  │ FastAPI HTTP POST /chat (server.py:278)
                                  ▼
       ┌────────────────────────────────────────────────────────┐
       │ HTTP Response JSON Payload                             │
       │ { "response": text, "expression": {...}, ... }         │
       └──────────────────────────┬─────────────────────────────┘
                                  │ IPC Bridge: chat:send (ipc-bridge.js:235)
                                  ▼
       ┌────────────────────────────────────────────────────────┐
       │ Electron Renderer Process (chat.js:1280)               │
       └──────────────────────────┬─────────────────────────────┘
                                  │
                                  ├─────────────────────────────────────────────────┐
       [ACTUATION PATH 1: VERBAL] │                                                 │ [ACTUATION PATH 2: VOCAL]
       appendMessage('companion', text)                                             │ Discards expr_dict!
       Directly displayed in chat UI.                                               │ Calls voice.synthesize(text)
       [VERIFIED WORKING]                                                           │ without passing options!
                                                                                    ▼
                                                               ┌─────────────────────────────────────────┐
                                                               │ POST /voice/synthesize                  │
                                                               │ Body: { "text": response.response }     │
                                                               │ (rate=None, volume=None, pitch=None)    │
                                                               └────────────────────┬────────────────────┘
                                                                                    │
                                                                                    ▼
                                                               ┌─────────────────────────────────────────┐
                                                               │ VoiceEngine.synthesize_speech           │
                                                               │ Falls back to static config:            │
                                                               │ pitch="+0Hz", rate="+0%", vol="+0%"     │
                                                               └────────────────────┬────────────────────┘
                                                                                    │
                                                                                    ▼
                                                               ┌─────────────────────────────────────────┐
                                                               │ Microsoft Edge-TTS Cloud Service        │
                                                               │ Synthesizes rigid baseline speech       │
                                                               └────────────────────┬────────────────────┘
                                                                                    │
                                                                                    ▼
                                                               ┌─────────────────────────────────────────┐
                                                               │ Direct RVC v2 Pipeline                  │
                                                               │ pitch_shift_semitones = 0 (static)      │
                                                               │ Zero dynamic F0 modulation              │
                                                               └────────────────────┬────────────────────┘
                                                                                    │
                                                                                    ▼
                                                               ┌─────────────────────────────────────────┐
                                                               │ Static, Unadapted Character Audio       │
                                                               └─────────────────────────────────────────┘
```

---

## 3. Step-by-Step Subsystem Inspection

### 3.1 Stage 9 & 10: Relational Conditioning of Communication Policy
- **Source File:** [`src/core/orchestrator/cognitive_orchestrator.py:427-463`](file:///c:/Users/Lunafiah/Desktop/My_project/Lucia/src/core/orchestrator/cognitive_orchestrator.py#L427-L463)
- **Data Read:** `rel_state = self._relationship_updater.get_state()`
- **Invocation:** `self._comm_policy.compute(pad=pad_final, somatic=markers, relationship=rel_state.to_dict(), ...)`
- **Mathematical Updates:** Inside [`src/core/communication/communication_policy.py:101-125`](file:///c:/Users/Lunafiah/Desktop/My_project/Lucia/src/core/communication/communication_policy.py#L101-L125):
  - `directness = clip(0.50 + 0.25*d - 0.20*tension - 0.15*closeness - 0.10*(trust - 0.50), 0.10, 0.95)`
  - `supportiveness = clip(0.30 + 0.35*p + 0.25*(trust - 0.50) + 0.20*closeness, 0.00, 1.00)`
  - `formality = clip(0.60 - 0.30*p - 0.25*closeness - 0.20*(trust - 0.50) + 0.15*tension, 0.00, 1.00)`
  - `acknowledgement = clip(0.40 + 0.25*familiarity + 0.20*m_avail - 0.15*tension, 0.10, 1.00)`
  - `question_freq = clip(0.10 + 0.25*(trust - 0.50) + 0.20*a - 0.25*tension, 0.00, 1.00)`
- **Verified Finding:** Causal path from `trust`, `closeness`, `familiarity` to `CommunicationState` is fully implemented and active.

### 3.2 Stage 11: Prompt Assembly & Conditioning
- **Source File:** [`src/core/orchestrator/prompt_assembler.py:125-136`](file:///c:/Users/Lunafiah/Desktop/My_project/Lucia/src/core/orchestrator/prompt_assembler.py#L125-L136)
- **Formatting:**
  ```text
  [COMMUNICATION STRATEGY]
  strategy: {comm_state.strategy.value}
  directness: {comm_state.directness:.2f}
  formality: {comm_state.formality_score:.2f}
  elaboration: {comm_state.elaboration_depth:.2f}
  supportiveness: {comm_state.supportiveness:.2f}
  ```
- **Verified Finding:** `directness`, `formality`, `elaboration`, `supportiveness` directly condition the LLM.
- **Architectural Gap:** `acknowledgement` and `question_frequency` are computed by `CommunicationPolicy` but dropped by `PromptAssembler`.

### 3.3 Stage 15: Expression Policy Evaluation
- **Source File:** [`src/core/orchestrator/cognitive_orchestrator.py:549-564`](file:///c:/Users/Lunafiah/Desktop/My_project/Lucia/src/core/orchestrator/cognitive_orchestrator.py#L549-L564)
- **Invocation:** `expr_state = self._expression_policy.compute(pad=pad_final, somatic=markers, relationship=rel_state.to_dict(), ...)`
- **Timing Anomaly:** Stage 15 executes **after** LLM text generation (Stage 13). Therefore, `ExpressionState.text` (`temperature_mod`, `verbosity_factor`, `cadence_style`) is retroactively computed and has zero causal impact on the generated text!
- **Voice Parameters Computed:**
  - `pitch_shift_hz = clip(15.0*p + 10.0*a, -30.0, 30.0)`
  - `speech_rate_pct = clip(15.0*a - 10.0*(1.0 - energy), -25.0, 25.0)`
  - `volume_pct = clip(10.0*d + 5.0*a, -20.0, 20.0)`
  - `pause_duration_ms = clip(200.0 + 300.0*(1.0 - energy) + 150.0*tension, 100.0, 1000.0)`
- **Architectural Finding:** Voice prosody depends **strictly on instantaneous affect ($E_t$) and somatic state ($S_t$)**. It has **zero conditioning on relational state ($R_t$)**.

### 3.4 The Client Actuation Breakage
- **Server Output:** [`src/api/server.py:278-286`](file:///c:/Users/Lunafiah/Desktop/My_project/Lucia/src/api/server.py#L278-L286) correctly serializes `result.expression.to_dict()`.
- **IPC Bridge:** [`electron/main/ipc-bridge.js:238`](file:///c:/Users/Lunafiah/Desktop/My_project/Lucia/electron/main/ipc-bridge.js#L238) forwards `data.expression`.
- **Renderer Breakage:** In [`electron/renderer/chat/chat.js:1287`](file:///c:/Users/Lunafiah/Desktop/My_project/Lucia/electron/renderer/chat/chat.js#L1287):
  ```javascript
  const audioBuffer = await window.lucia.voice.synthesize(response.response);
  ```
  The client ignores `response.expression`. It passes only the text string.
- **VoiceEngine Fallback:** In [`src/core/voice/voice_engine.py:177-179`](file:///c:/Users/Lunafiah/Desktop/My_project/Lucia/src/core/voice/voice_engine.py#L177-L179):
  ```python
  speech_rate = rate or self._config.speech_rate       # defaults to "+0%"
  speech_volume = volume or self._config.speech_volume # defaults to "+0%"
  pitch_str = pitch or "+0Hz"                         # defaults to "+0Hz"
  ```
  Because `rate`, `volume`, and `pitch` are `None`, `VoiceEngine` always synthesizes at static baseline.

---

## 4. Actuation Reality Matrix

| Subsystem Link | Intended Function | Code Implementation Status | Runtime Actuation Status |
|:---|:---|:---:|:---:|
| $R_t \rightarrow \text{CommunicationPolicy}$ | Relational conditioning of verbal style | **IMPLEMENTED** (`comm_policy.py:102`) | **ACTIVE** |
| $\text{CommunicationPolicy} \rightarrow \text{LLM}$ | Inject style parameters into prompt | **IMPLEMENTED** (`prompt_assembler.py:128`) | **ACTIVE** |
| $R_t \rightarrow \text{VoiceProsody}$ | Relational conditioning of vocal prosody | **ABSENT** (`expression_policy.py:108`) | **INACTIVE** |
| $E_t \rightarrow \text{VoiceProsody}$ | Affective conditioning of vocal prosody | **IMPLEMENTED** (`expression_policy.py:108`) | **INACTIVE** (Discarded by client) |
| $\text{ExpressionState} \rightarrow \text{Avatar}$ | Visual blendshapes & posture | **IMPLEMENTED** (`expression_state.py:54`) | **INACTIVE** (Ignored by renderer) |
| $\text{VoiceEngine} \rightarrow \text{Dynamic } F_0$ | Word-level melodic inflection | **UNSUPPORTED** in current production | **INACTIVE** (Static RVC convert only) |

---

## 5. Epistemic Summary

- **FACT:** `CommunicationPolicy` causally connects `trust`, `closeness`, and `familiarity` to LLM generation.
- **FACT:** `VoiceProsody` is computed on the backend but discarded by the frontend, resulting in static speech synthesis at runtime.
- **FACT:** `RelationshipState.reciprocity` is completely ignored by both `CommunicationPolicy` and `ExpressionPolicy`.
- **INTERPRETATION:** A working P24 Affective Communication Adaptation mechanism does not require inventing new state representations, but requires:
  1. Bridging the client IPC parameter drop.
  2. Coupling relational dimensions ($R_t$) into vocal prosody equations.
  3. Translating backend prosodic parameters into RVC semitone and dynamic $F_0$ contouring.
