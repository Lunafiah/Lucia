# Implementation Plan: Lucia Core Phase 1

## Overview

Implement the five-module stimulus-to-response pipeline that forms the foundation of the Lucia AI companion: StimulusProcessor, EmotionCore (LNN + PAD), HomeostaticEngine (somatic markers + behavioral constraints), Orchestrator (pipeline coordinator + prompt assembler), LLMBackend (llama-cpp-python), and BoundaryLayer (meta-self-awareness filter). The implementation is in Python 3.12 and targets AMD Ryzen 7 4800H + NVIDIA RTX 3050 Ti (4 GB VRAM).

Property-based tests use [Hypothesis](https://hypothesis.readthedocs.io/) with `settings(max_examples=200)`. Tasks marked `*` are optional and can be skipped for a faster MVP iteration.

---

## Tasks

- [ ] 1. Project scaffolding and shared data models
  - Create `src/core/orchestrator/` directory with `__init__.py`
  - Create `src/core/orchestrator/prompt_assembler.py` (stub only at this stage)
  - Create `src/core/orchestrator/orchestrator.py` (stub only at this stage)
  - Create `tests/unit/` and `tests/property/` directories with `__init__.py` files if they do not exist; confirm `tests/integration/` exists
  - Create `src/core/models.py` defining all shared frozen dataclasses: `PADState`, `SomaticMarkers`, `BehavioralConstraints`, `SoftBlockEvent`
  - Create `src/core/config.py` defining all config dataclasses: `StimulusConfig`, `EmotionConfig`, `HomeostaticConfig`, `LLMConfig`, `BoundaryConfig`, `OrchestratorConfig`; each `__init__` validates fields and raises `ValueError` for out-of-range values
  - Create `src/core/errors.py` defining `AssemblyError`
  - _Requirements: 1.1, 2.1, 3.1, 4.1, 10.1–10.8_

- [ ] 2. StimulusProcessor
  - [ ] 2.1 Implement `StimulusProcessor` in `src/core/gating/stimulus_processor.py`
    - Accept `StimulusConfig`; raise `ValueError` at init if `vector_dim < 3` or not a positive integer
    - `encode(text: str) -> np.ndarray`: return zero vector for empty string; truncate + `warnings.warn()` for strings over `char_limit`; compute dim-0 (VADER valence), dim-1 (arousal from punctuation density, cap ratio, avg tokens/sentence), dim-2 (unique-token ratio mapped to `[-1,1]`); zero-pad dims 3…N−1; apply `1e-7` floor to |dim 0–2| for non-empty input; final clip to `[-1.0, 1.0]`
    - _Requirements: 4.1–4.10_
  - [ ]* 2.2 Write unit tests for `StimulusProcessor` in `tests/unit/test_stimulus_processor.py`
    - Empty string → zero vector of correct shape
    - 4097-char string → truncation warning; 4096-char string → no warning
    - `vector_dim=2` raises `ValueError`; `vector_dim=3` succeeds with shape `(3,)`
    - Strongly negative sentence → dim-0 negative; strongly positive → dim-0 positive
    - _Requirements: 4.1, 4.2, 4.6, 4.7, 4.10_
  - [ ]* 2.3 Write property tests for `StimulusProcessor` in `tests/property/test_properties.py`
    - **Property 8: Stimulus Vector Shape Invariant** — `text(min_size=1, max_size=500)` → shape is `(N,)`
    - **Property 9: Stimulus Vector Bounds Invariant** — `text(min_size=0, max_size=4096)` → all values in `[-1.0, 1.0]`
    - **Property 10: Non-Zero Semantic Dimensions** — `text(min_size=1, alphabet=printable)` → |dim 0|, |dim 1|, |dim 2| all > 0
    - _Requirements: 4.1, 4.2, 4.9_

- [ ] 3. EmotionCore
  - [ ] 3.1 Implement `PADState` projection and LTC network weights in `src/core/emotion/emotion_core.py`
    - Xavier-uniform initialize weight matrices `W_tau`, `U_tau`, `b_tau`, `W_f`, `U_f`, `b_f`, `W_proj`, `b_proj` at init; validate `EmotionConfig` fields
    - Implement `_ode_step(h, x) -> np.ndarray` using `scipy.integrate.solve_ivp` with LTC RHS `dh/dt = (-h + tanh(W_f·h + U_f·x + b_f)) / softplus(W_tau·h + U_tau·x + b_tau)`; clip result to `[-1.0, 1.0]`
    - Implement `_project_to_pad(h) -> PADState` using `W_proj·h + b_proj`; clamp to `[-1.0, 1.0]`; record `time.monotonic()` timestamp
    - _Requirements: 1.1, 1.4, 1.6, 1.7_
  - [ ]* 3.2 Write property tests for EmotionCore ODE and projection
    - **Property 1: PAD State Bounds Invariant** — `arrays(float64, (3,), elements=floats(-10, 10))` projected and clamped → all dims in `[-1.0, 1.0]`
    - **Property 2: ODE Step Intermediate Clamping** — random `h` and `x` → `_ode_step` result all values in `[-1.0, 1.0]`
    - _Requirements: 1.4, 1.7_
  - [ ] 3.3 Implement the `EmotionCore` background loop in `src/core/emotion/emotion_core.py`
    - Implement `start()`, `stop()`, `is_alive()`, `tick_count()` using a daemon `threading.Thread` and `threading.Event`
    - Implement `_fast_loop_worker()`: consume stimulus (`_consume_stimulus()` returns zero vector if none pending), ODE step, intermediate clamp, project to PAD, acquire `_state_lock`, write `_pad_snapshot`, increment `_tick_counter`; on any exception log, reset `_h` and `_pad_snapshot` to resting baseline, and continue loop (do not terminate thread)
    - Implement `push_stimulus(vector)`: thread-safe write to `_pending_stimulus` using a `threading.Lock`
    - Implement `get_pad_state()`: attempt `_state_lock.acquire(timeout=0.001)`; return `_pad_snapshot` regardless of whether lock was acquired
    - Respect `loop_cadence_ms`: sleep `max(0, cadence_ms - elapsed_ms) / 1000` after each tick
    - _Requirements: 1.2, 1.3, 1.5, 1.8, 1.9, 1.10_
  - [ ]* 3.4 Write unit tests for `EmotionCore` in `tests/unit/test_emotion_core.py`
    - Initialized PAD equals configured resting baseline before `start()`
    - Thread is alive after `start()`; `tick_count() >= 1` within 2 s
    - Injected exception in ODE step → state resets to resting baseline and thread stays alive
    - `get_pad_state()` returns within 2 ms under lock contention
    - _Requirements: 1.2, 1.3, 1.8, 1.9_

- [ ] 4. HomeostaticEngine — somatic markers
  - [ ] 4.1 Implement `HomeostaticEngine.compute_somatic_markers()` in `src/core/emotion/homeostatic_engine.py`
    - Accept `HomeostaticConfig`; validate all threshold fields at init
    - Maintain instance state: `_energy` (init 1.0), `_input_timestamps` (deque for rolling 60 s window), `_last_input_time`
    - Implement `record_input()`: append `time.monotonic()` to `_input_timestamps`; prune entries older than 60 s; update `_last_input_time`
    - Implement somatic marker formulas per design: `stability`, `cognitive_load`, `freq_component`, `arousal_component`, `energy` (depletion per call + idle recovery), `tension` (raise `ValueError` for `valence` outside `[0.0, 1.0]`; return 0.0 when `valence` is `None`)
    - Validate incoming `PADState` dimensions in `compute_somatic_markers`; raise `ValueError` for any dim outside `[-1.0, 1.0]`
    - Return completed `SomaticMarkers` within 5 ms
    - _Requirements: 2.1–2.7_
  - [ ]* 4.2 Write property tests for somatic markers
    - **Property 3: Somatic Markers Completeness and Bounds** — `builds(PADState, ...)` with all dims in `[-1,1]`, `valence` in `[0,1]` → all four fields present and in `[0.0, 1.0]`
    - **Property 4: Tension Validity Domain** — `floats(-10.0, 10.0).filter(lambda v: not 0.0 <= v <= 1.0)` as valence → `ValueError` raised
    - _Requirements: 2.1, 2.5_
  - [ ]* 4.3 Write unit tests for `HomeostaticEngine` somatic markers in `tests/unit/test_homeostatic_engine.py`
    - Resting baseline PAD + 60 s idle → `stability >= 0.8`, `cognitive_load <= 0.2`, `energy >= 0.8`, `tension <= 0.2`
    - `valence=1.5` raises `ValueError`; `valence=0.5` succeeds
    - PAD dimension `1.1` raises `ValueError`
    - _Requirements: 2.5, 2.7_

- [ ] 5. HomeostaticEngine — behavioral constraints
  - [ ] 5.1 Implement `HomeostaticEngine.compute_behavioral_constraints()` in `src/core/emotion/homeostatic_engine.py`
    - Implement `_resolve(conditions, default)` helper: select the active condition with the highest priority metric (highest `cognitive_load` for `max_tokens`/`latency_ms`; highest `arousal` for `temperature`)
    - Apply all threshold rules from Requirements 3.2–3.9 to derive `max_tokens`, `temperature`, `latency_ms`, `reasoning_depth`
    - Fall back to defaults (150, 0.75, 0, 1) when no threshold condition applies (Requirement 3.10)
    - Validate incoming `PADState`; raise `ValueError` for out-of-bounds dim; return last valid `BehavioralConstraints` or defaults when raising (Requirement 3.12)
    - _Requirements: 3.1–3.12_
  - [ ]* 5.2 Write property tests for behavioral constraints
    - **Property 5: Behavioral Constraints Output Ranges** — `builds(SomaticMarkers, ...)` with all fields in `[0,1]`, any valid PADState → `max_tokens` in `[1,2048]`, `temperature` in `[0.0,2.0]`, `latency_ms` in `[0,5000]`, `reasoning_depth` in `[0,3]`
    - **Property 6: Behavioral Constraints Priority Resolution** — strategies generating simultaneous overlapping threshold conditions → priority rule consistently applied
    - **Property 7: Out-of-Bounds PAD Raises ValueError** — `arrays(float64, 3)` with at least one value outside `[-1,1]` → `ValueError`
    - _Requirements: 3.1, 3.11, 3.12_
  - [ ]* 5.3 Write unit tests for behavioral constraints in `tests/unit/test_homeostatic_engine.py`
    - `cognitive_load=0.9, energy=0.2` → `max_tokens <= 80`
    - `cognitive_load=0.2, energy=0.8` → `max_tokens >= 300`
    - `arousal=0.8` → `temperature > 0.85`
    - `arousal=0.2, stability=0.8` → `temperature < 0.65`
    - `energy=0.05` → `reasoning_depth == 0`
    - `energy=0.8, cognitive_load=0.3` → `reasoning_depth == 3` and `latency_ms == 0`
    - _Requirements: 3.2–3.9_

- [ ] 6. Checkpoint — core state pipeline
  - Ensure all tests pass for tasks 2–5. Verify that `StimulusProcessor.encode()`, `EmotionCore.get_pad_state()`, `HomeostaticEngine.compute_somatic_markers()`, and `HomeostaticEngine.compute_behavioral_constraints()` can be exercised end-to-end in a short script (no LLM required). Ask the user if any questions arise.

- [ ] 7. LLMBackend
  - [ ] 7.1 Implement `LLMBackend` in `src/core/language/llm_backend.py`
    - Validate `model_path` existence before calling `Llama()`; raise `FileNotFoundError` if missing
    - Initialize `llama_cpp.Llama` with `n_gpu_layers`, `n_ctx`, `verbose` from `LLMConfig`; after init, verify at least one GPU layer was allocated when `n_gpu_layers > 0`, raise `RuntimeError` if zero layers
    - Implement `generate(prompt, constraints) -> str | None` using a `ThreadPoolExecutor(max_workers=1)`; apply `max_tokens` and `temperature` from constraints (fallback: 512 / 0.7); enforce `timeout_seconds` via `future.result(timeout=...)`; return `None` and log on timeout or model error
    - Implement `is_ready() -> bool` and `shutdown()` (releases executor and sets internal ready flag to False)
    - _Requirements: 6.1–6.7_
  - [ ]* 7.2 Write unit tests for `LLMBackend` in `tests/unit/test_llm_backend.py`
    - Non-existent model path raises `FileNotFoundError` at init
    - Mock `Llama` returning a valid response → `generate()` returns expected text
    - Mock `Llama` raising an exception → `generate()` returns `None`
    - Mock `Llama` timing out → `generate()` returns `None` within `timeout + 0.5 s`
    - `is_ready()` returns `True` after init, `False` after `shutdown()`
    - _Requirements: 6.4–6.7_

- [ ] 8. PromptAssembler
  - [ ] 8.1 Implement `PromptAssembler` in `src/core/orchestrator/prompt_assembler.py`
    - `assemble(somatic, constraints, history, system_preamble) -> str | AssemblyError`
    - Section order: preamble → `[SOMATIC STATE]` (numeric key-value, no prose emotional labels) → `[REASONING]` (omit when `reasoning_depth == 0`; include `min((depth*2)-1, 5)` steps when > 0) → `[CONVERSATION]`; sections separated by `"\n\n---\n\n"`
    - Trim conversation history: include most-recent turns up to `min(10, ...)` using token budget `max_tokens * 4` with `estimate_tokens = len(text) // 4`
    - Truncate oldest turns one at a time if assembled prompt exceeds `n_ctx`; return `AssemblyError` if preamble alone exceeds context window
    - Complete assembly within 20 ms
    - _Requirements: 5.1–5.8_
  - [ ]* 8.2 Write unit tests for `PromptAssembler` in `tests/unit/test_prompt_assembler.py`
    - `reasoning_depth=0` → no `[REASONING]` section in output
    - `reasoning_depth=1` → 1 step; `reasoning_depth=2` → 3 steps; `reasoning_depth=3` → 5 steps (capped)
    - History of 15 turns → at most 10 turns included
    - Somatic state section contains no natural-language emotional labels
    - Preamble larger than `n_ctx` → `AssemblyError`
    - _Requirements: 5.1–5.5, 5.8_
  - [ ]* 8.3 Write property tests for `PromptAssembler`
    - **Property 11: Conditioned Prompt Section Order** — `builds(SomaticMarkers,...)`, arbitrary history list, `integers(0,3)` for `reasoning_depth` → section order invariant holds
    - **Property 12: Conversation History Truncation Bound** — `lists(tuples(text(), text()), min_size=0, max_size=20)` → included turns ≤ `min(10, floor(max_tokens * 4 / avg_turn_tokens))`
    - **Property 13: Reasoning Step Count** — `integers(1, 3)` for `reasoning_depth` → step count equals `min((depth*2)-1, 5)`
    - _Requirements: 5.1, 5.3, 5.5_

- [ ] 9. BoundaryLayer
  - [ ] 9.1 Implement `BoundaryLayer` in `src/core/safety/boundary_layer.py`
    - Accept `BoundaryConfig`; at init, load provided patterns (cap at first 50, silently discard excess); compile all patterns with `re.IGNORECASE`; include all 10 default patterns
    - `validate(text: str) -> str`: iterate compiled patterns; for each match perform Soft_Block (replace span with `"[...]"`, log `SoftBlockEvent` with pattern, original span, substituted text, `datetime.utcnow()`); after all substitutions, check for incomplete clause ending `(,|;|\band\b|\bor\b|\bbut\b)\s*\[\.\.\.\]$`; truncate to last sentence boundary or return `"[...]"` if none
    - `add_pattern(pattern)` / `remove_pattern(pattern)`: update compiled dict; `add_pattern` is a no-op when count is already 50; changes take effect on next `validate()` call
    - `get_log() -> list[SoftBlockEvent]`
    - Complete matching + substitution on ≤ 2000-char string within 5 ms
    - _Requirements: 7.1–7.9, 9.2, 9.3_
  - [ ]* 9.2 Write unit tests for `BoundaryLayer` in `tests/unit/test_boundary_layer.py`
    - Each of the 10 default patterns triggers a Soft_Block and the matched text is absent from output
    - String ending `, [...]` is truncated at last sentence boundary
    - String with no preceding sentence boundary returns `"[...]"`
    - 51 patterns at init → only 50 stored
    - `add_pattern` / `remove_pattern` take effect on next `validate()` call
    - `validate()` on a clean string returns the string unmodified
    - _Requirements: 7.1–7.5, 7.7_
  - [ ]* 9.3 Write property tests for `BoundaryLayer`
    - **Property 14: Boundary Layer Pattern Replacement** — `text().map(embed_default_pattern)` → matched spans replaced with `"[...]"`, original text absent
    - **Property 15: Boundary Layer Passthrough** — `text().filter(no_default_pattern_match)` → `validate()` output equals input
    - **Property 16: Boundary Layer Idempotence** — `text().filter(no_default_pattern_match)` → `validate(validate(t)) == validate(t)`
    - _Requirements: 7.3, 7.4, 7.9_

- [ ] 10. Orchestrator
  - [ ] 10.1 Implement `Orchestrator.__init__()` and startup in `src/core/orchestrator/orchestrator.py`
    - Validate `OrchestratorConfig` (all required fields present; all values in documented ranges); raise `ValueError` identifying the missing or invalid key
    - Instantiate `StimulusProcessor`, `EmotionCore`, `HomeostaticEngine`, `LLMBackend`, `PromptAssembler`, `BoundaryLayer` from config
    - Call `EmotionCore.start()`; poll until `is_alive() and tick_count() >= 1` within 5 s deadline; raise `RuntimeError` if not ready in time
    - _Requirements: 8.4, 8.5, 10.1–10.8_
  - [ ] 10.2 Implement `Orchestrator.process()` pipeline in `src/core/orchestrator/orchestrator.py`
    - Input guard: return `fallback_response` immediately for empty string or string > 4000 chars (no pipeline steps executed)
    - Degraded-state guard: return `fallback_response` immediately
    - Execute pipeline steps 1–8 in order per Requirement 8.2; apply `latency_ms` sleep before LLM call (capped at 5000 ms); apply `BoundaryLayer.validate()`; if result is `"[...]"` substitute `fallback_response`
    - Append `("user", input_text)` and `("assistant", safe_response)` to `_history` after successful call
    - Log `call_id`, monotonic timestamp, `SomaticMarkers`, `BehavioralConstraints` for every call
    - On any unhandled exception: log full stack trace, set `_degraded = True`, leave `EmotionCore` running, return `fallback_response`
    - _Requirements: 8.1–8.3, 8.7, 8.8, 8.9, 9.1, 9.4–9.6_
  - [ ] 10.3 Implement `Orchestrator.shutdown()` in `src/core/orchestrator/orchestrator.py`
    - Signal `EmotionCore.stop()`; join the Fast_Loop thread with `timeout=2.0`; call `LLMBackend.shutdown()`
    - _Requirements: 8.6_
  - [ ]* 10.4 Write unit tests for `Orchestrator` in `tests/unit/test_orchestrator.py`
    - Empty string returns `fallback_response`; no pipeline step is logged
    - String of 4001 characters returns `fallback_response`; no pipeline step is logged
    - Mock-injected exception in any pipeline step → `_degraded == True`; subsequent `process()` returns `fallback_response`
    - `shutdown()` joins thread within 3 s and `LLMBackend.is_ready()` returns `False` afterward
    - `OrchestratorConfig` with missing required field raises `ValueError`
    - `OrchestratorConfig` with out-of-range `loop_cadence_ms` (e.g., 50) raises `ValueError`
    - _Requirements: 8.4–8.7, 8.10, 10.1, 10.6, 10.7_
  - [ ]* 10.5 Write property tests for `Orchestrator`
    - **Property 17: Orchestrator Input Rejection** — `integers(0, 0)` and `integers(4001, 10000)` mapped to strings → `process()` returns error-indicating string immediately
    - **Property 18: Out-of-Range Configuration Raises ValueError** — strategies generating each config field individually out of valid range → `__init__` raises `ValueError`
    - _Requirements: 8.10, 10.7, 10.8_

- [ ] 11. Checkpoint — full pipeline dry run
  - Ensure all unit and property tests pass (with `LLMBackend` mocked). Run `pytest tests/unit tests/property --tb=short`. Ask the user if any questions arise.

- [ ] 12. Integration tests and wiring validation
  - [ ] 12.1 Write integration tests in `tests/integration/test_orchestrator_integration.py`
    - Orchestrator startup: `EmotionCore` becomes alive and `tick_count() >= 1` within 5 s (mocked LLM)
    - End-to-end `process()` with mocked `LLMBackend` returning clean text → non-empty response string
    - `process()` with mocked `LLMBackend` returning a default-pattern phrase → response contains `"[...]"` or `fallback_response`
    - PAD state changes after 3 consecutive `process()` calls (state is not frozen)
    - `BoundaryLayer` log contains a `SoftBlockEvent` after a flagged mock LLM response
    - `shutdown()` joins Fast_Loop thread cleanly and `is_healthy()` returns `False`
    - _Requirements: 8.2–8.7_
  - [ ] 12.2 Write GPU/model integration test stubs in `tests/integration/test_llm_backend_integration.py`
    - All tests in this file are skipped unless `LUCIA_MODEL_PATH` env var is set
    - When model is present: `LLMBackend.__init__()` succeeds; `generate()` returns a non-empty string; `is_ready()` returns `True`; GPU layer count logged at init is ≥ 1
    - _Requirements: 6.1–6.3_

- [ ] 13. Final checkpoint — all tests green
  - Run `pytest tests/unit tests/property tests/integration --tb=short` (GPU tests will skip automatically without `LUCIA_MODEL_PATH`). Ensure all non-skipped tests pass. Ask the user if any questions arise.

---

## Notes

- Tasks marked with `*` are optional and can be skipped for a faster MVP iteration.
- Each task references specific requirements from `requirements.md` for full traceability.
- The Hypothesis property tests should be placed together in `tests/property/test_properties.py` with `@settings(max_examples=200)` on each test and tagged with the comment format `# Feature: lucia-core-phase1, Property N: <property_text>`.
- `LLMBackend` should always be mocked in unit and property tests. Real GPU/model tests live exclusively in `tests/integration/test_llm_backend_integration.py` behind the `LUCIA_MODEL_PATH` env-var skip guard.
- The `src/core/orchestrator/` directory must be created manually or by the first task; no `__init__.py` exists there yet.
- Energy state in `HomeostaticEngine` is persistent instance state (initialized to `1.0`); it depletes per `record_input()` call and recovers during idle periods. Tests that depend on specific energy values should construct a fresh `HomeostaticEngine` instance.
- The `AssemblyError` sentinel is distinct from `None`; `Orchestrator.process()` checks `isinstance(prompt, AssemblyError)` rather than truthiness, to avoid ambiguity with empty strings.

---

## Task Dependency Graph

```json
{
  "waves": [
    { "id": 0, "tasks": ["1"] },
    { "id": 1, "tasks": ["2.1", "3.1"] },
    { "id": 2, "tasks": ["2.2", "2.3", "3.2", "3.3"] },
    { "id": 3, "tasks": ["3.4", "4.1", "7.1"] },
    { "id": 4, "tasks": ["4.2", "4.3", "5.1", "7.2", "8.1"] },
    { "id": 5, "tasks": ["5.2", "5.3", "8.2", "8.3", "9.1"] },
    { "id": 6, "tasks": ["9.2", "9.3", "10.1"] },
    { "id": 7, "tasks": ["10.2", "10.3"] },
    { "id": 8, "tasks": ["10.4", "10.5"] },
    { "id": 9, "tasks": ["12.1", "12.2"] }
  ]
}
```
