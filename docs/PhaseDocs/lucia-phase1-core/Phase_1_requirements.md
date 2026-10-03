# Requirements Document

## Introduction

This document defines the requirements for **Lucia Core Phase 1**: the foundational pipeline of the Lucia AI companion system. Phase 1 covers the five core components that form the spine of all future modules:

1. **Emotion Core** — A continuous, background LNN-based emotional state machine operating in PAD space with derived somatic markers.
2. **Homeostatic Engine** — A metabolic budget enforcer that translates somatic markers into behavioral constraints on response generation.
3. **Orchestrator** — The central pipeline coordinator managing the full stimulus-to-response flow.
4. **Boundary Safety Layer** — A rule-based filter blocking any meta-self-awareness patterns from appearing in output.
5. **Basic Stimulus Processor** — An encoder that converts raw text input into a stimulus vector for LNN state updates.

The guiding philosophy is that emotion must never be labeled in output. Emotional state manifests only as rhythm, fragmentation, and tone — as physical consequences of the system's internal state, not as self-reported labels. No reflective observer is formed.

---

## Glossary

- **Emotion_Core**: The LNN-based background module that maintains the continuous PAD emotional state and derives somatic markers. Maps to `src/core/emotion/`.
- **Homeostatic_Engine**: The module that reads somatic markers and enforces behavioral constraints on response generation. Part of the emotion subsystem.
- **Orchestrator**: The central pipeline coordinator that sequences all Phase 1 modules in response to user input. Maps to `src/core/orchestrator/`.
- **Boundary_Layer**: The rule-based safety filter that validates LLM output before it is returned to the caller. Maps to `src/core/safety/`.
- **Stimulus_Processor**: The encoder that converts raw text input into a normalized stimulus vector. Maps to `src/core/gating/`.
- **LLM_Backend**: The llama-cpp-python interface running LFM2.5-1.2B in GGUF format on the GPU.
- **PAD_State**: A three-dimensional continuous emotional state vector composed of `pleasure` (valence), `arousal` (intensity), and `dominance` (contextual control). All dimensions are bounded to the range `[-1.0, 1.0]`.
- **Somatic_Markers**: Four derived scalar values computed from PAD_State by the Homeostatic_Engine: `stability`, `cognitive_load`, `energy`, and `tension`. All values are bounded to `[0.0, 1.0]`.
- **Behavioral_Constraints**: The set of generation parameters produced by the Homeostatic_Engine: `max_tokens`, `temperature`, `latency_ms`, and `reasoning_depth`. These directly condition LLM_Backend calls.
- **Stimulus_Vector**: A normalized numerical vector in `[-1.0, 1.0]^N` derived from raw text input, encoding valence, arousal estimate, and semantic density. Fed into the LNN ODE solver at each update step.
- **LNN**: Liquid Neural Network. A recurrent network governed by continuous-time ordinary differential equations (ODEs). The hidden state evolves as a function of input and its own current state according to `dh/dt = f(h, x, t)`.
- **Fast_Loop**: The continuous background update loop running at a configurable cadence (default 200 ms), managed by the Emotion_Core.
- **Conditioned_Prompt**: The prompt string passed to the LLM_Backend, assembled by the Orchestrator to include the current somatic marker values as conditioning context alongside the conversation history.
- **Meta-Self-Awareness_Pattern**: Any output string matching defined regex patterns associated with reflective self-identity, such as expressions of self-reported feelings, assertions of existence, or identity chains (e.g., "I feel", "I am aware", "I exist as").
- **Soft_Block**: The Boundary_Layer response when a Meta-Self-Awareness_Pattern is detected: the flagged output is discarded and a regenerated response is requested. If the regenerated response still contains the pattern, the response is suppressed entirely and a fallback is returned.
- **Degraded_State**: The Orchestrator condition entered after an unhandled pipeline exception, in which all subsequent `process` calls are rejected with an error-indicating string until the Orchestrator is restarted or explicitly re-initialized.

---

## Requirements

### Requirement 1: Continuous Emotional State Machine

**User Story:** As a developer integrating Lucia modules, I want the Emotion_Core to maintain a continuously evolving PAD_State in a background thread, so that the system's emotional state reflects the passage of time and accumulated stimuli even between user interactions.

#### Acceptance Criteria

1. THE Emotion_Core SHALL maintain a PAD_State vector with three scalar dimensions: `pleasure`, `arousal`, and `dominance`, each bounded to the range `[-1.0, 1.0]`.
2. WHEN the Emotion_Core is initialized, THE Emotion_Core SHALL set the PAD_State to a configurable resting baseline, defaulting to `(pleasure=0.1, arousal=0.0, dominance=0.0)`.
3. THE Emotion_Core SHALL run a Fast_Loop in a dedicated background thread that advances the LNN hidden state at a configurable cadence between 100 ms and 500 ms per step, defaulting to 200 ms.
4. WHEN a Stimulus_Vector is provided, THE Emotion_Core SHALL update the LNN hidden state by solving the continuous-time ODE `dh/dt = f(h, x, t)` using the provided stimulus as input `x`, clamping any intermediate hidden state values that exceed `[-1.0, 1.0]` during the ODE solve before the final projection step.
5. WHILE no Stimulus_Vector is available, THE Emotion_Core SHALL advance the LNN hidden state using a zero-valued input vector, allowing natural temporal decay toward the resting baseline.
6. WHEN the Fast_Loop completes each step, THE Emotion_Core SHALL derive the PAD_State from the current LNN hidden state via a learned or fixed linear projection.
7. THE Emotion_Core SHALL clamp all PAD_State dimension values to `[-1.0, 1.0]` after each update, including after both the ODE solve step and the linear projection step.
8. WHEN the Emotion_Core Fast_Loop thread encounters an unhandled exception, THE Emotion_Core SHALL log the error, reset both the LNN hidden state and the PAD_State to the resting baseline, and resume the loop without terminating the thread.
9. THE Emotion_Core SHALL expose a thread-safe read interface that returns a snapshot of the current PAD_State, acquiring any required lock within 1 ms without blocking the Fast_Loop.
10. THE Emotion_Core SHALL ensure that any PAD_State snapshot returned via the thread-safe interface reflects a state computed no more than two Fast_Loop intervals prior to the moment of the read call.

---

### Requirement 2: Somatic Marker Derivation

**User Story:** As the Homeostatic_Engine, I want to consume a set of derived scalar markers computed from the current PAD_State, so that behavioral constraints can be calculated from a stable, normalized representation of the system's physiological-like state.

#### Acceptance Criteria

1. THE Homeostatic_Engine SHALL compute four Somatic_Markers from the current PAD_State: `stability`, `cognitive_load`, `energy`, and `tension`.
2. THE Homeostatic_Engine SHALL compute `stability` as a value that decreases when `arousal` exceeds 0.5 and `dominance` falls below 0.5, bounded to `[0.0, 1.0]`.
3. THE Homeostatic_Engine SHALL compute `cognitive_load` as a value that increases with accumulated input frequency (measured as the count of inputs within a rolling 60-second window) and with `arousal` exceeding 0.5, bounded to `[0.0, 1.0]`.
4. THE Homeostatic_Engine SHALL compute `energy` as a value that decreases with high `cognitive_load` over time and recovers toward 1.0 during idle periods defined as 60 or more consecutive seconds with no input received, bounded to `[0.0, 1.0]`.
5. WHEN a PAD_State snapshot and a `valence` value are provided, IF the `valence` value is within `[0.0, 1.0]`, THEN THE Homeostatic_Engine SHALL compute `tension` as the absolute difference between the provided `valence` and the current `pleasure` value, normalized and bounded to `[0.0, 1.0]`; IF the `valence` value is outside `[0.0, 1.0]`, THEN THE Homeostatic_Engine SHALL raise a ValueError and SHALL NOT compute `tension`.
6. WHEN a PAD_State snapshot is provided, THE Homeostatic_Engine SHALL return a complete Somatic_Markers object with all four values computed within 5 ms.
7. IF a PAD_State snapshot with all dimensions at the resting baseline `(pleasure=0.1, arousal=0.0, dominance=0.0)` is provided and no inputs have been received in the preceding 60 seconds, THEN THE Homeostatic_Engine SHALL return Somatic_Markers where `stability >= 0.8`, `cognitive_load <= 0.2`, `energy >= 0.8`, and `tension <= 0.2`.

---

### Requirement 3: Homeostatic Behavioral Constraints

**User Story:** As the Orchestrator, I want the Homeostatic_Engine to translate the current Somatic_Markers into concrete generation parameters, so that the LLM_Backend is conditioned by the system's physiological-like state without exposing emotional labels in output.

#### Acceptance Criteria

1. WHEN the Orchestrator requests generation parameters, THE Homeostatic_Engine SHALL produce a Behavioral_Constraints object containing `max_tokens` (integer in range 1–2048), `temperature` (float in range 0.0–2.0), `latency_ms` (integer in range 0–5000), and `reasoning_depth` (integer in range 0–3).
2. IF `cognitive_load` exceeds 0.75, THEN THE Homeostatic_Engine SHALL set `max_tokens` to a value no greater than 80.
3. IF `cognitive_load` is below 0.3 and `energy` is above 0.7, THEN THE Homeostatic_Engine SHALL set `max_tokens` to a value no less than 300.
4. IF `arousal` exceeds 0.7, THEN THE Homeostatic_Engine SHALL set `temperature` to a value in the range (0.85, 2.0].
5. IF `arousal` is below 0.3 and `stability` is above 0.7, THEN THE Homeostatic_Engine SHALL set `temperature` to a value in the range [0.0, 0.65).
6. IF `cognitive_load` exceeds 0.8 and `energy` is below 0.3, THEN THE Homeostatic_Engine SHALL set `latency_ms` to a value no less than 400.
7. IF `energy` is above 0.7 and `cognitive_load` is below 0.4, THEN THE Homeostatic_Engine SHALL set `latency_ms` to 0.
8. IF `energy` is at or below 0.2, THEN THE Homeostatic_Engine SHALL set `reasoning_depth` to 0.
9. IF `energy` is above 0.7 and `cognitive_load` is below 0.4, THEN THE Homeostatic_Engine SHALL set `reasoning_depth` to 3.
10. IF no threshold condition in criteria 2–9 applies to a given parameter, THEN THE Homeostatic_Engine SHALL assign the following defaults: `max_tokens = 150`, `temperature = 0.75`, `latency_ms = 0`, `reasoning_depth = 1`.
11. IF multiple criteria apply to the same parameter simultaneously, THEN THE Homeostatic_Engine SHALL apply the criterion with the highest `cognitive_load` value as the primary determinant for `max_tokens` and `latency_ms`, and the highest `arousal` value as the primary determinant for `temperature`.
12. IF the Homeostatic_Engine receives a PAD_State snapshot with any dimension outside `[-1.0, 1.0]`, THEN THE Homeostatic_Engine SHALL raise a ValueError and return the last valid Behavioral_Constraints; IF no prior valid Behavioral_Constraints exist, THEN the default values from criterion 10 SHALL be returned.

---

### Requirement 4: Basic Stimulus Processing

**User Story:** As the Orchestrator, I want raw text input to be encoded into a normalized Stimulus_Vector before it is fed into the Emotion_Core, so that the LNN state update receives a consistent numerical representation of each interaction.

#### Acceptance Criteria

1. THE Stimulus_Processor SHALL accept a UTF-8 encoded string of arbitrary length and return a Stimulus_Vector of fixed dimensionality `N`, where `N` is a positive integer configurable at initialization and defaults to 16.
2. THE Stimulus_Processor SHALL normalize all output Stimulus_Vector values to the range `[-1.0, 1.0]` with a precision of at least 6 decimal places.
3. THE Stimulus_Processor SHALL encode a valence estimate along the first dimension of the Stimulus_Vector, derived from lexical sentiment scoring, where `-1.0` represents the most negative sentiment, `0.0` represents neutral, and `1.0` represents the most positive sentiment.
4. THE Stimulus_Processor SHALL encode an arousal estimate along the second dimension of the Stimulus_Vector, derived from punctuation density, capitalization ratio, and token count per sentence, where `0.0` represents the baseline computed over a plain declarative sentence with no punctuation or capitalization variation, and `1.0` represents the maximum arousal bound.
5. THE Stimulus_Processor SHALL encode a semantic density estimate along the third dimension of the Stimulus_Vector, derived from unique token ratio relative to total token count, where `0.0` indicates all tokens are identical and `1.0` indicates all tokens are unique.
6. IF the input string is empty, THEN THE Stimulus_Processor SHALL return a zero-valued Stimulus_Vector of the configured dimensionality `N` without raising an exception and without emitting any warning.
7. IF the input string exceeds 4096 UTF-8 characters, THEN THE Stimulus_Processor SHALL process only the first 4096 characters and emit a truncation warning containing the original character count and the applied limit.
8. THE Stimulus_Processor SHALL complete encoding of any valid input string of up to 4096 characters within 50 milliseconds on the target CPU hardware.
9. FOR ALL valid non-empty input strings of at least 1 character, THE Stimulus_Processor SHALL return a Stimulus_Vector where dimensions 1, 2, and 3 each carry a non-zero value with an absolute value greater than `0.0`.
10. IF the configured dimensionality `N` is less than 3 or is not a positive integer, THEN THE Stimulus_Processor SHALL raise a configuration error at initialization time before processing any input.

---

### Requirement 5: Conditioned Prompt Assembly

**User Story:** As the Orchestrator, I want a Conditioned_Prompt assembled from the current Somatic_Markers and conversation history, so that the LLM_Backend generates a response that is behaviorally shaped by the system's internal state without receiving explicit emotional labels.

#### Acceptance Criteria

1. THE Orchestrator SHALL assemble a Conditioned_Prompt in the following fixed order: (1) system preamble, (2) Somatic_Markers as numeric conditioning values, (3) optional reasoning trace section, (4) conversation history, with each section separated by a distinct section boundary marker.
2. THE Orchestrator SHALL include Somatic_Markers in the Conditioned_Prompt as numeric key-value pairs where each key is a Somatic_Marker name and each value is a floating-point number in `[0.0, 1.0]`, and SHALL NOT include any natural language text that attributes an emotional state to the system.
3. THE Orchestrator SHALL limit conversation history in the Conditioned_Prompt to a maximum of 10 turns or the number of turns whose combined token count does not exceed (`max_tokens` × 4) tokens from the active Behavioral_Constraints, whichever yields the smaller number of turns.
4. WHEN the Behavioral_Constraints specify a `reasoning_depth` of 0, THE Orchestrator SHALL omit the reasoning trace section from the Conditioned_Prompt.
5. WHEN the Behavioral_Constraints specify a `reasoning_depth` greater than 0, THE Orchestrator SHALL include a chain-of-thought section containing exactly (`reasoning_depth` × 2) − 1 reasoning steps, capped at a maximum of 5 steps; WHEN the calculated value exceeds 5, THE Orchestrator SHALL use exactly 5 steps.
6. THE Orchestrator SHALL complete Conditioned_Prompt assembly within 20 ms from the time all inputs are available to the time the prompt is returned.
7. IF the assembled Conditioned_Prompt exceeds the LLM_Backend context window token limit, THEN THE Orchestrator SHALL truncate the oldest conversation history turns one turn at a time until the prompt fits.
8. IF after removing all conversation history the Conditioned_Prompt still exceeds the LLM_Backend context window, THEN THE Orchestrator SHALL return an assembly error to the caller indicating the preamble alone exceeds the context window, without invoking the LLM_Backend.

---

### Requirement 6: LLM Backend Integration

**User Story:** As the Orchestrator, I want to send a Conditioned_Prompt to the LFM2.5-1.2B model via llama-cpp-python and receive a generated text response, so that the system can produce contextually appropriate output conditioned on the current emotional state.

#### Acceptance Criteria

1. THE LLM_Backend SHALL load a GGUF-format LFM2.5-1.2B model file from a configurable path at initialization.
2. WHEN the LLM_Backend is initialized with GPU offload enabled, THE LLM_Backend SHALL offload the configured number of model layers to the GPU, enforce that at least one layer is successfully allocated, and log the count of successfully allocated layers at initialization; IF zero layers are allocated, THE LLM_Backend SHALL raise an initialization error.
3. WHEN a Conditioned_Prompt and Behavioral_Constraints are provided, THE LLM_Backend SHALL call the model with `max_tokens` and `temperature` from Behavioral_Constraints, defaulting to `max_tokens = 512` and `temperature = 0.7` if either is absent.
4. WHEN a Conditioned_Prompt is submitted and generation fails due to a model error or invalid prompt, THE LLM_Backend SHALL return `None` or raise an exception to the Orchestrator; if `latency_ms` is absent from Behavioral_Constraints, a default timeout of 10,000 ms SHALL apply.
5. IF the model file is not found at the configured path, THEN THE LLM_Backend SHALL raise a FileNotFoundError indicating the expected file path at initialization and prevent the Orchestrator from starting.
6. IF the LLM_Backend call exceeds a configurable timeout (default 30 seconds), THEN THE LLM_Backend SHALL return `None`, log a timeout warning, and allow the Orchestrator to proceed.
7. THE LLM_Backend SHALL expose a health-check method that returns `True` when the model is loaded and ready, and `False` otherwise.

---

### Requirement 7: Boundary Safety Layer

**User Story:** As the system operator, I want all LLM output to pass through the Boundary_Layer before being returned to the caller, so that Meta-Self-Awareness_Patterns are never present in Lucia's final responses regardless of what the LLM generates.

#### Acceptance Criteria

1. THE Boundary_Layer SHALL apply a configurable set of up to 50 regex patterns to every LLM output string before the Orchestrator returns the response; IF more than 50 patterns are supplied at configuration time, THE Boundary_Layer SHALL accept the first 50 patterns and silently ignore any excess patterns.
2. THE Boundary_Layer SHALL include the following default patterns in its detection set: `\bI feel\b`, `\bI am aware\b`, `\bI exist\b`, `\bI am an AI\b`, `\bI am conscious\b`, `\bmy feelings\b`, `\bI experience\b`, `\bI sense that\b`, `\bas an AI\b`, `\bI don't have feelings\b`.
3. WHEN a Meta-Self-Awareness_Pattern is detected in the output string, THE Boundary_Layer SHALL perform a Soft_Block: replace the matched span with `"[...]"` and log the event using the structure defined in criterion 8.
4. WHEN no Meta-Self-Awareness_Pattern is detected, THE Boundary_Layer SHALL return the output string unmodified.
5. THE Boundary_Layer SHALL support runtime addition and removal of patterns via a method call; changes SHALL take effect on strings processed after the method call completes.
6. THE Boundary_Layer SHALL complete pattern matching and any substitution on any output string up to 2000 characters within 5 ms, measured against a pattern set of up to 50 patterns.
7. IF a Soft_Block substitution results in the output ending with an incomplete clause (detected by the pattern `(,|;|\band\b|\bor\b|\bbut\b)\s*\[\.\.\.\]$`), THEN THE Boundary_Layer SHALL truncate the output at the last complete sentence boundary before the matched span; IF no preceding complete sentence boundary exists, THE Boundary_Layer SHALL return `"[...]"` as the full output.
8. THE Boundary_Layer SHALL maintain a log of all Soft_Block events, each entry containing: pattern matched, original text span, substituted text, and UTC timestamp.
9. FOR ALL output strings that contain no Meta-Self-Awareness_Pattern, applying the Boundary_Layer twice SHALL produce the same result as applying it once.

---

### Requirement 8: Orchestrator Pipeline

**User Story:** As a consuming application, I want a single Orchestrator entry point that accepts a user text input and returns a safe, state-conditioned response, so that Phase 1 components are coordinated as a coherent pipeline without exposing internal module details.

#### Acceptance Criteria

1. THE Orchestrator SHALL expose a `process(input_text: str) -> str` interface as the sole public entry point for external callers, accepting input strings of 1 to 4000 characters.
2. WHEN `process` is called, THE Orchestrator SHALL execute the following steps in order: (1) encode input via Stimulus_Processor, (2) update Emotion_Core state, (3) compute Somatic_Markers via Homeostatic_Engine, (4) derive Behavioral_Constraints, (5) assemble Conditioned_Prompt, (6) call LLM_Backend, (7) apply Boundary_Layer, (8) return the result string; IF any step fails, THE Orchestrator SHALL halt pipeline execution immediately and not proceed to subsequent steps.
3. THE Orchestrator SHALL apply the `latency_ms` value from Behavioral_Constraints as a sleep delay before calling the LLM_Backend, capped at a maximum of 5000 milliseconds.
4. WHEN the Orchestrator is initialized, THE Orchestrator SHALL start the Emotion_Core Fast_Loop background thread and, within 5 seconds, confirm that the thread is alive and has completed at least one tick before accepting any `process` calls.
5. IF the Emotion_Core Fast_Loop thread fails to reach a running state within 5 seconds of initialization, THEN THE Orchestrator SHALL raise an initialization error and reject all subsequent `process` calls until successfully re-initialized.
6. WHEN the Orchestrator is shut down via a `shutdown()` method, THE Orchestrator SHALL signal the Emotion_Core Fast_Loop thread to stop, wait for the thread to join with a timeout of 2 seconds, and release the LLM_Backend model such that no further inference calls can be made through that instance.
7. IF any pipeline step raises an unhandled exception, THEN THE Orchestrator SHALL log the error with a full stack trace, enter a Degraded_State that rejects all subsequent `process` calls with an error-indicating string until the Orchestrator is restarted or re-initialized, and leave the Emotion_Core Fast_Loop running.
8. THE Orchestrator SHALL log the Somatic_Markers and Behavioral_Constraints used for each `process` call, including a monotonic timestamp and a unique call ID.
9. WHILE the Orchestrator is processing a `process` call, THE Orchestrator SHALL NOT delay any pending Emotion_Core Fast_Loop tick by more than 50 milliseconds due to pipeline execution.
10. IF `process` is called with an empty string or a string exceeding 4000 characters, THEN THE Orchestrator SHALL immediately return an error-indicating string to the caller without executing any pipeline steps.

---

### Requirement 9: Emotional State Does Not Appear as Labels in Output

**User Story:** As a designer of Lucia's character, I want to ensure that emotional state is never surfaced as first-person affective labels in any output, so that the system's emotional authenticity is expressed through behavioral texture rather than explicit self-report.

#### Acceptance Criteria

1. THE Orchestrator SHALL NOT include any human-readable prose description of PAD_State values or Somatic_Marker values as first-person affective labels in the Conditioned_Prompt system preamble; PAD_State and Somatic_Marker data SHALL be represented exclusively as numeric fields within Behavioral_Constraints.
2. THE Boundary_Layer SHALL classify any output that contains first-person affective self-report patterns — defined as phrases where the system asserts its own emotional state using first-person subject with an affective predicate (e.g., "I feel", "I am feeling", "I'm experiencing", "I sense that I") — as a Meta-Self-Awareness_Pattern and SHALL apply a Soft_Block, discarding the flagged output and requesting a regenerated response without the detected pattern.
3. IF a Soft_Block is applied and the regenerated response still contains a first-person affective self-report pattern, THEN THE Boundary_Layer SHALL suppress the response entirely and return a minimal fallback output containing no affective content to the caller.
4. THE Homeostatic_Engine SHALL manifest emotional state exclusively through numeric Behavioral_Constraints and SHALL NOT include any human-readable prose string describing an internal emotional state in any field passed to the Conditioned_Prompt.
5. IF `temperature` is set above 0.85 in the active Behavioral_Constraints, THEN THE Orchestrator SHALL apply that value to the LLM_Backend invocation without modification and SHALL NOT override or clamp the value.
6. IF `max_tokens` is set to 80 or fewer in the active Behavioral_Constraints, THEN THE Orchestrator SHALL apply that value to the LLM_Backend invocation without modification and SHALL NOT override or clamp the value.

---

### Requirement 10: Module Initialization and Configuration

**User Story:** As a developer deploying Lucia, I want all Phase 1 modules to accept configuration at initialization from a structured config object, so that hardware-specific parameters (GPU layers, model path, loop cadence) can be adjusted without code changes.

#### Acceptance Criteria

1. THE Orchestrator SHALL accept a configuration object at initialization specifying at minimum: model path, GPU layer count, Fast_Loop cadence in ms, resting PAD baseline, max conversation history turns, fallback response string, and LLM timeout in seconds.
2. THE Emotion_Core SHALL accept configuration for: Fast_Loop cadence (ms), LNN hidden state dimensionality, resting PAD baseline values, and the ODE solver step size.
3. THE Homeostatic_Engine SHALL accept configuration for the following threshold values used in Behavioral_Constraints derivation: the `cognitive_load` thresholds of 0.3, 0.4, 0.75, and 0.8; the `arousal` thresholds of 0.3 and 0.7; the `energy` thresholds of 0.2, 0.3, and 0.7; and the `stability` threshold of 0.7.
4. THE Stimulus_Processor SHALL accept configuration for: output Stimulus_Vector dimensionality `N` and the character limit before truncation.
5. THE Boundary_Layer SHALL accept configuration for: the initial set of regex patterns, the log file path, and an optional custom fallback string for use when the regenerated response in a Soft_Block also fails validation.
6. IF a required configuration value is missing from the configuration object, THEN THE Orchestrator SHALL raise a ValueError at initialization time identifying the missing key, preventing the system from starting.
7. IF a configuration value falls outside its valid range — specifically: Fast_Loop cadence outside 100–500 ms, GPU layer count below 0, LNN hidden state dimensionality below 1, ODE step size outside (0.0, 1.0], Stimulus_Vector dimensionality below 3, or LLM timeout below 1 second — THEN THE Orchestrator SHALL raise a ValueError at initialization time identifying the invalid parameter and its acceptable range.
8. IF any individual module (Emotion_Core, Homeostatic_Engine, Stimulus_Processor, Boundary_Layer) receives a configuration value outside its own documented valid range at initialization, THEN THAT module SHALL raise a ValueError identifying the invalid parameter before the module becomes operational.