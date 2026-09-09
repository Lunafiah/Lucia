# Design Document — Lucia Core Phase 1

## Overview

Lucia Core Phase 1 establishes the foundational processing pipeline for the Lucia AI companion. It wires five cooperating modules into a single coherent stimulus-to-response flow:

1. **Stimulus_Processor** — encodes raw UTF-8 text into a normalized numerical vector.
2. **Emotion_Core** — a continuously running background LNN that maintains PAD emotional state.
3. **Homeostatic_Engine** — derives somatic markers from PAD state and translates them into concrete generation parameters.
4. **Orchestrator** — sequences all modules, assembles the conditioned prompt, calls the LLM, and returns the final response.
5. **Boundary_Layer** — validates every LLM output string and suppresses meta-self-awareness patterns before the caller sees any text.

The central design constraint is that emotional state must **never** surface as first-person affective labels. It manifests only through the behavioral parameters that shape generation: token limits, temperature, latency delay, and reasoning depth. The Emotion_Core runs continuously in a background thread independent of user requests, so emotional state evolves even during silence.

---

## Architecture

### Module Dependency Graph

```
User / Caller
     │
     ▼
┌────────────────────────────────────────────────────┐
│  Orchestrator  (src/core/orchestrator/)            │
│                                                    │
│  process(input_text) ──►  Stimulus_Processor       │
│                │                                   │
│                ▼                                   │
│          Emotion_Core ◄─── Fast_Loop (background)  │
│                │                                   │
│                ▼                                   │
│        Homeostatic_Engine                          │
│                │                                   │
│        Somatic_Markers                             │
│                │                                   │
│        Behavioral_Constraints                      │
│                │                                   │
│        Prompt_Assembler                            │
│                │                                   │
│        LLM_Backend  (llama-cpp-python)             │
│                │                                   │
│        Boundary_Layer                              │
│                │                                   │
└────────────────┼───────────────────────────────────┘
                 │
                 ▼
           response: str
```

### Temporal Loop Structure

The system runs three concurrent loops at different timescales:

| Loop | Timescale | Owner | Purpose |
|------|-----------|-------|---------|
| Fast Loop | 100–500 ms per tick | Emotion_Core | LNN ODE advance, PAD update |
| Mid Loop | minutes–hours | Homeostatic_Engine | Somatic marker trends, energy recovery |
| Slow Loop | days–weeks | SDM (Phase 2+) | Memory consolidation, ecphory |

Phase 1 implements only the Fast Loop. Mid-loop state (rolling input counter, energy recovery clock) is tracked as running accumulators inside the Homeostatic_Engine rather than a separate loop thread.

### Threading Model

```
Main Thread
    ├── Orchestrator.process() calls (blocking, serialized per call)
    └── LLM_Backend (GPU inference)

Background Thread (daemon)
    └── Emotion_Core._fast_loop_worker()
            ├── scipy.integrate.solve_ivp  (ODE step)
            ├── linear projection  →  PAD_State
            ├── clamp  →  PAD_State
            └── write to _pad_snapshot (under _state_lock)
```

The Fast Loop thread writes only one shared datum: `_pad_snapshot`. All reads from `process()` acquire `_state_lock` (a `threading.Lock`) with a non-blocking attempt followed by a brief spin (maximum 1 ms), falling back to returning the previous snapshot if the lock cannot be acquired within the deadline.

---

## Components and Interfaces

### Stimulus_Processor  (`src/core/gating/stimulus_processor.py`)

**Responsibility:** Encode raw text into a fixed-length normalized stimulus vector.

```python
class StimulusProcessor:
    def __init__(self, config: StimulusConfig) -> None: ...
    def encode(self, text: str) -> np.ndarray: ...  # shape: (N,), dtype float64
```

**`StimulusConfig`:**

| Field | Type | Default | Constraint |
|-------|------|---------|------------|
| `vector_dim` | int | 16 | >= 3 |
| `char_limit` | int | 4096 | > 0 |

**Encoding pipeline:**

1. Validate `vector_dim >= 3`; raise `ValueError` at init if not.
2. If `text` is empty, return `np.zeros(N)`.
3. If `len(text) > char_limit`, truncate to first `char_limit` characters and emit `warnings.warn()` containing original length and limit.
4. Compute **dimension 0** (valence): [VADER](https://github.com/cjhutto/vaderSentiment) compound score, already in `[-1.0, 1.0]`.
5. Compute **dimension 1** (arousal): weighted combination of `punctuation_density` (punctuation chars / total chars), `cap_ratio` (uppercase letters / total letters), and `avg_tokens_per_sentence` (normalized against a reference declarative sentence). Result clipped to `[0.0, 1.0]` then mapped to `[0.0, 1.0]`. Baseline sentence score maps to 0.0; maximum plausible score maps to 1.0.
6. Compute **dimension 2** (semantic density): unique token ratio (`unique_tokens / total_tokens`). Empty-token inputs return 0. Result in `[0.0, 1.0]`, then mapped to `[-1.0, 1.0]` via `x * 2 - 1`.
7. Dimensions 3…N−1: zero-padded (reserved for Phase 2 extensions, e.g., syntactic or discourse features).
8. Final clip: all dimensions clamped to `[-1.0, 1.0]`.

**Non-empty guarantee:** Dimensions 0, 1, and 2 are computed from actual text content. Any non-empty string will produce at least one character contributing to the arousal estimate (punctuation/cap ratio > 0 for strings with uppercase or punctuation, or a non-trivial token-per-sentence value). For pure lowercase alphabetic input, the semantic density dimension will be non-zero unless all tokens are identical, which is guaranteed not to be the case for any string of at least 1 character composed of any non-repeated word. The implementation must ensure a minimum absolute value floor of `1e-7` is applied to dimensions 0–2 for non-empty input to satisfy Requirement 4.9.

---

### Emotion_Core  (`src/core/emotion/emotion_core.py`)

**Responsibility:** Maintain a continuously evolving PAD emotional state via LNN ODE integration in a background thread.

```python
class EmotionCore:
    def __init__(self, config: EmotionConfig) -> None: ...
    def start(self) -> None: ...
    def stop(self) -> None: ...
    def is_alive(self) -> bool: ...
    def get_pad_state(self) -> PADState: ...                   # thread-safe snapshot read
    def push_stimulus(self, vector: np.ndarray) -> None: ...   # thread-safe stimulus injection
    def tick_count(self) -> int: ...                           # monotonically increasing
```

**`EmotionConfig`:**

| Field | Type | Default | Constraint |
|-------|------|---------|------------|
| `loop_cadence_ms` | int | 200 | 100–500 |
| `hidden_dim` | int | 32 | >= 1 |
| `resting_baseline` | tuple[float,float,float] | (0.1, 0.0, 0.0) | each in [-1,1] |
| `ode_step_size` | float | 0.1 | (0.0, 1.0] |

**`PADState` (dataclass):**

```python
@dataclass(frozen=True)
class PADState:
    pleasure:   float   # [-1.0, 1.0]
    arousal:    float   # [-1.0, 1.0]
    dominance:  float   # [-1.0, 1.0]
    timestamp:  float   # monotonic time of last update (time.monotonic())
```

#### LNN Architecture

The Emotion_Core implements a **Liquid Time-Constant (LTC) network**:

```
dh/dt = -h/τ(h, x) + f(h, x) / τ(h, x)
```

where:
- `h ∈ ℝ^hidden_dim` — hidden state
- `x ∈ ℝ^N` — stimulus vector (zero vector when no stimulus)
- `τ(h, x) = softplus(W_τ·h + U_τ·x + b_τ)` — input-dependent time constant (always positive)
- `f(h, x) = tanh(W_f·h + U_f·x + b_f)` — state update function

All weight matrices (`W_τ`, `U_τ`, `b_τ`, `W_f`, `U_f`, `b_f`) are fixed at initialization with Xavier uniform initialization. Phase 1 does not train these weights — they implement a structurally plausible continuous-time dynamics for demonstration and integration purposes. Training is deferred to Phase 2.

**PAD projection:**

```
pad_raw = W_proj · h + b_proj          # W_proj: (3, hidden_dim), b_proj: (3,)
pad_clamped = clip(pad_raw, -1.0, 1.0)
```

#### Fast Loop Worker

```python
def _fast_loop_worker(self):
    while not self._stop_event.is_set():
        tick_start = time.monotonic()
        try:
            x = self._consume_stimulus()       # returns np.zeros(N) if none pending
            h_new = self._ode_step(self._h, x)
            h_new = np.clip(h_new, -1.0, 1.0)  # intermediate clamp
            pad = self._project_to_pad(h_new)
            self._h = h_new
            with self._state_lock:
                self._pad_snapshot = pad
            self._tick_counter += 1
        except Exception as e:
            logger.error("Fast_Loop exception: %s", e, exc_info=True)
            self._h = np.array(self._h_resting)
            with self._state_lock:
                self._pad_snapshot = self._pad_resting
        elapsed = (time.monotonic() - tick_start) * 1000
        sleep_ms = max(0.0, self._cadence_ms - elapsed)
        time.sleep(sleep_ms / 1000)
```

#### ODE Step

```python
def _ode_step(self, h: np.ndarray, x: np.ndarray) -> np.ndarray:
    def rhs(t, y):
        tau = softplus(self.W_tau @ y + self.U_tau @ x + self.b_tau)
        f   = np.tanh(self.W_f @ y + self.U_f @ x + self.b_f)
        return (-y + f) / tau
    result = solve_ivp(
        rhs,
        t_span=(0.0, self._ode_step_size),
        y0=h,
        method="RK45",
        max_step=self._ode_step_size / 4,
        dense_output=False,
    )
    return result.y[:, -1]
```

#### Thread-safe Read

```python
def get_pad_state(self) -> PADState:
    acquired = self._state_lock.acquire(timeout=0.001)  # 1 ms deadline
    try:
        return self._pad_snapshot
    finally:
        if acquired:
            self._state_lock.release()
        # if not acquired, _pad_snapshot is still returned (last known state)
```

The lock is a plain `threading.Lock`. The write section (inside the Fast Loop) is intentionally short — just an assignment of a frozen dataclass reference — minimizing contention. The 1 ms deadline ensures the caller is never blocked beyond the requirement's bound.

---

### Homeostatic_Engine  (`src/core/emotion/homeostatic_engine.py`)

**Responsibility:** Derive somatic markers from PAD state and compute behavioral constraints.

```python
class HomeostaticEngine:
    def __init__(self, config: HomeostaticConfig) -> None: ...
    def record_input(self) -> None: ...                           # call on each user input
    def compute_somatic_markers(
        self, pad: PADState, valence: float | None = None
    ) -> SomaticMarkers: ...
    def compute_behavioral_constraints(
        self, markers: SomaticMarkers, pad: PADState
    ) -> BehavioralConstraints: ...
```

**`HomeostaticConfig`:** Exposes all thresholds from Requirement 10.3 as named fields with the documented defaults. Any value outside a documented range raises `ValueError` at init.

**`SomaticMarkers` (dataclass):**

```python
@dataclass(frozen=True)
class SomaticMarkers:
    stability:      float   # [0.0, 1.0]
    cognitive_load: float   # [0.0, 1.0]
    energy:         float   # [0.0, 1.0]
    tension:        float   # [0.0, 1.0]
```

**`BehavioralConstraints` (dataclass):**

```python
@dataclass(frozen=True)
class BehavioralConstraints:
    max_tokens:      int    # [1, 2048]
    temperature:     float  # [0.0, 2.0]
    latency_ms:      int    # [0, 5000]
    reasoning_depth: int    # [0, 3]
```

#### Somatic Marker Formulas

**`stability`:**

```
base = 1.0 - max(0.0, arousal - 0.5) * 2
penalty = max(0.0, 0.5 - dominance) * 2
stability = clip(base - penalty * (1 - base), 0.0, 1.0)
```

Stability decreases toward 0 as arousal rises above 0.5 and dominance falls below 0.5.

**`cognitive_load`:**

```
input_count_60s = count of inputs in rolling 60-second window
freq_component  = clip(input_count_60s / 10.0, 0.0, 1.0)   # 10 inputs/min = max freq
arousal_component = clip(max(0.0, arousal - 0.5) * 2, 0.0, 1.0)
cognitive_load  = clip((freq_component + arousal_component) / 2.0, 0.0, 1.0)
```

**`energy`:**

```
# Depletes with high cognitive_load; recovers after 60+ s idle
energy_delta = -cognitive_load * 0.1   # per process() call
idle_recovery = +0.05 per second of idle beyond 60-second threshold
energy = clip(energy + delta, 0.0, 1.0)
```

Energy persists as instance state on the `HomeostaticEngine`. It is initialized to `1.0`.

**`tension`:**

```
if valence is None:
    tension = 0.0
elif valence not in [0.0, 1.0]:
    raise ValueError(f"valence={valence} must be in [0.0, 1.0]")
else:
    raw = abs(valence - (pleasure + 1.0) / 2.0)   # map pleasure from [-1,1] to [0,1]
    tension = clip(raw, 0.0, 1.0)
```

#### Behavioral Constraint Derivation

Priority rules are applied independently per parameter using a `_resolve(conditions, default)` helper that picks the condition with the highest associated priority metric.

| Parameter | High-priority trigger | Low-priority trigger | Default |
|-----------|----------------------|----------------------|---------|
| `max_tokens` | `cognitive_load > 0.75` → ≤ 80 | `cognitive_load < 0.3 and energy > 0.7` → ≥ 300 | 150 |
| `temperature` | `arousal > 0.7` → (0.85, 2.0] | `arousal < 0.3 and stability > 0.7` → [0.0, 0.65) | 0.75 |
| `latency_ms` | `cognitive_load > 0.8 and energy < 0.3` → ≥ 400 | `energy > 0.7 and cognitive_load < 0.4` → 0 | 0 |
| `reasoning_depth` | `energy <= 0.2` → 0 | `energy > 0.7 and cognitive_load < 0.4` → 3 | 1 |

When multiple criteria apply to the same parameter (Requirement 3.11), `max_tokens` and `latency_ms` use the condition with the highest `cognitive_load`; `temperature` uses the condition with the highest `arousal`. This is resolved by sorting applicable conditions by their primary determinant descending and taking the first.

**Out-of-bounds PAD validation (Requirement 3.12):**

```python
def compute_behavioral_constraints(self, markers, pad):
    for dim, val in [("pleasure", pad.pleasure), ("arousal", pad.arousal),
                     ("dominance", pad.dominance)]:
        if not (-1.0 <= val <= 1.0):
            raise ValueError(f"PAD dimension '{dim}'={val} out of [-1.0, 1.0]")
    ...
```

---

### LLM_Backend  (`src/core/language/llm_backend.py`)

**Responsibility:** Load and serve the LFM2.5-1.2B GGUF model via `llama-cpp-python`.

```python
class LLMBackend:
    def __init__(self, config: LLMConfig) -> None: ...
    def generate(
        self,
        prompt: str,
        constraints: BehavioralConstraints,
    ) -> str | None: ...
    def is_ready(self) -> bool: ...
    def shutdown(self) -> None: ...
```

**`LLMConfig`:**

| Field | Type | Default |
|-------|------|---------|
| `model_path` | str | — (required) |
| `n_gpu_layers` | int | 32 |
| `n_ctx` | int | 4096 |
| `timeout_seconds` | float | 30.0 |
| `verbose` | bool | False |

**Initialization:**

```python
from llama_cpp import Llama

self._llm = Llama(
    model_path=config.model_path,
    n_gpu_layers=config.n_gpu_layers,
    n_ctx=config.n_ctx,
    verbose=config.verbose,
)
```

- If `model_path` does not exist: `FileNotFoundError` is raised before `Llama()` is called.
- GPU layer validation: After initialization, inspect `self._llm.metadata` or the verbose initialization log to confirm at least one layer was GPU-offloaded. If zero GPU layers are allocated when `n_gpu_layers > 0`, raise an initialization error.
- `is_ready()` returns `True` after successful `__init__`, `False` before or after `shutdown()`.

**`generate()`:**

```python
def generate(self, prompt: str, constraints: BehavioralConstraints) -> str | None:
    max_tokens  = constraints.max_tokens  if constraints.max_tokens  else 512
    temperature = constraints.temperature if constraints.temperature is not None else 0.7
    timeout     = self._config.timeout_seconds

    future = self._executor.submit(self._llm, prompt,
                                   max_tokens=max_tokens,
                                   temperature=temperature,
                                   echo=False)
    try:
        result = future.result(timeout=timeout)
        return result["choices"][0]["text"]
    except TimeoutError:
        logger.warning("LLM generation timed out after %.1fs", timeout)
        future.cancel()
        return None
    except Exception as e:
        logger.error("LLM generation failed: %s", e)
        return None
```

The `_executor` is a `ThreadPoolExecutor(max_workers=1)` created at init. This keeps the GPU-bound inference off the main thread without introducing multiprocessing overhead, allowing the timeout to be enforced with `future.result(timeout=...)`.

---

### Prompt_Assembler  (`src/core/orchestrator/prompt_assembler.py`)

**Responsibility:** Build the `Conditioned_Prompt` string from components.

```python
class PromptAssembler:
    SECTION_SEP = "\n\n---\n\n"

    def assemble(
        self,
        somatic: SomaticMarkers,
        constraints: BehavioralConstraints,
        history: list[tuple[str, str]],   # [(role, text), ...]
        system_preamble: str,
    ) -> str | AssemblyError: ...
```

**Section order (Requirement 5.1):**

```
{system_preamble}
---
[SOMATIC STATE]
stability: {stability:.6f}
cognitive_load: {cognitive_load:.6f}
energy: {energy:.6f}
tension: {tension:.6f}
---
[REASONING]            ← omitted when reasoning_depth == 0
Step 1: ...
Step 2: ...            ← (depth*2 - 1) steps, capped at 5
---
[CONVERSATION]
{history turns, trimmed to constraint}
```

No natural-language emotional labels appear in the somatic state section — only numeric key-value pairs (Requirement 5.2).

**History trimming (Requirement 5.3):**

```python
token_budget = constraints.max_tokens * 4
turn_limit   = 10
included = []
token_sum = 0
for turn in reversed(history):
    turn_tokens = estimate_tokens(turn)    # approximation: len(text) // 4
    if len(included) >= turn_limit:
        break
    if token_sum + turn_tokens > token_budget:
        break
    included.insert(0, turn)
    token_sum += turn_tokens
```

**Reasoning steps (Requirement 5.5):**

```python
if constraints.reasoning_depth > 0:
    steps = min((constraints.reasoning_depth * 2) - 1, 5)
```

---

### Boundary_Layer  (`src/core/safety/boundary_layer.py`)

**Responsibility:** Validate LLM output and suppress meta-self-awareness patterns.

```python
class BoundaryLayer:
    MAX_PATTERNS = 50

    def __init__(self, config: BoundaryConfig) -> None: ...
    def validate(self, text: str) -> str: ...
    def add_pattern(self, pattern: str) -> None: ...
    def remove_pattern(self, pattern: str) -> None: ...
    def get_log(self) -> list[SoftBlockEvent]: ...
```

**Default pattern set (Requirement 7.2):**

```python
DEFAULT_PATTERNS = [
    r"\bI feel\b",
    r"\bI am aware\b",
    r"\bI exist\b",
    r"\bI am an AI\b",
    r"\bI am conscious\b",
    r"\bmy feelings\b",
    r"\bI experience\b",
    r"\bI sense that\b",
    r"\bas an AI\b",
    r"\bI don't have feelings\b",
]
```

All patterns are compiled with `re.IGNORECASE` at init and on any `add_pattern()` call.

**`validate()` logic:**

```python
def validate(self, text: str) -> str:
    for pattern, compiled in self._patterns.items():
        match = compiled.search(text)
        if match:
            span_text = match.group(0)
            text = compiled.sub("[...]", text)
            self._log_soft_block(pattern, span_text, text, datetime.utcnow())

    # Check for incomplete clause at end
    if re.search(r"(,|;|\band\b|\bor\b|\bbut\b)\s*\[\.\.\.\]$", text, re.IGNORECASE):
        last_sentence_end = max(
            text.rfind("."), text.rfind("!"), text.rfind("?")
        )
        if last_sentence_end > 0:
            text = text[:last_sentence_end + 1]
        else:
            text = "[...]"
    return text
```

**Pattern limit (Requirement 7.1):** At init, if `len(initial_patterns) > 50`, silently accept only the first 50. `add_pattern()` is a no-op when the current count is already 50.

**`SoftBlockEvent` (dataclass):**

```python
@dataclass
class SoftBlockEvent:
    pattern_matched: str
    original_span:   str
    substituted_text: str
    utc_timestamp:   datetime
```

**Idempotence:** Because the Boundary_Layer replaces matched spans with `"[...]"` and `"[...]"` itself does not match any default or added pattern, applying `validate()` twice is identical to applying it once for any string with no pattern match. This is a structural invariant of the substitution design.

---

### Orchestrator  (`src/core/orchestrator/orchestrator.py`)

**Responsibility:** Coordinate the full stimulus-to-response pipeline.

```python
class Orchestrator:
    def __init__(self, config: OrchestratorConfig) -> None: ...
    def process(self, input_text: str) -> str: ...
    def shutdown(self) -> None: ...
    def is_healthy(self) -> bool: ...
```

**`OrchestratorConfig`:**

| Field | Type | Default |
|-------|------|---------|
| `model_path` | str | required |
| `n_gpu_layers` | int | 32 |
| `loop_cadence_ms` | int | 200 |
| `resting_baseline` | tuple[float,float,float] | (0.1, 0.0, 0.0) |
| `max_history_turns` | int | 10 |
| `fallback_response` | str | `"[...]"` |
| `llm_timeout_seconds` | float | 30.0 |
| `system_preamble` | str | `""` |
| `boundary_patterns` | list[str] | `[]` |

**`process()` pipeline (Requirement 8.2):**

```python
def process(self, input_text: str) -> str:
    # Guard: input validation
    if len(input_text) == 0 or len(input_text) > 4000:
        return self._config.fallback_response

    # Guard: degraded state
    if self._degraded:
        return self._config.fallback_response

    call_id = uuid.uuid4().hex
    t_start = time.monotonic()

    try:
        # Step 1: encode stimulus
        stimulus = self._stimulus_processor.encode(input_text)

        # Step 2: update Emotion_Core
        self._emotion_core.push_stimulus(stimulus)

        # Step 3: somatic markers
        pad = self._emotion_core.get_pad_state()
        self._homeostatic_engine.record_input()
        markers = self._homeostatic_engine.compute_somatic_markers(pad)

        # Step 4: behavioral constraints
        constraints = self._homeostatic_engine.compute_behavioral_constraints(
            markers, pad
        )

        # Step 5: assemble prompt
        prompt = self._prompt_assembler.assemble(
            somatic=markers,
            constraints=constraints,
            history=self._history,
            system_preamble=self._config.system_preamble,
        )
        if isinstance(prompt, AssemblyError):
            return self._config.fallback_response

        # Step 6: latency delay
        delay_s = min(constraints.latency_ms, 5000) / 1000
        if delay_s > 0:
            time.sleep(delay_s)

        # Step 7: LLM call
        raw_response = self._llm_backend.generate(prompt, constraints)
        if raw_response is None:
            return self._config.fallback_response

        # Step 8: boundary layer
        safe_response = self._boundary_layer.validate(raw_response)

        # Logging
        logger.info(
            "call_id=%s t=%.3f markers=%s constraints=%s",
            call_id, time.monotonic() - t_start, markers, constraints
        )

        # Append to history
        self._history.append(("user", input_text))
        self._history.append(("assistant", safe_response))

        return safe_response

    except Exception as e:
        logger.error("Unhandled pipeline exception call_id=%s: %s",
                     call_id, e, exc_info=True)
        self._degraded = True
        return self._config.fallback_response
```

**Startup (Requirement 8.4):**

```python
def __init__(self, config: OrchestratorConfig) -> None:
    self._validate_config(config)    # raises ValueError for any invalid field
    self._emotion_core.start()
    deadline = time.monotonic() + 5.0
    while time.monotonic() < deadline:
        if self._emotion_core.is_alive() and self._emotion_core.tick_count() >= 1:
            break
        time.sleep(0.05)
    else:
        raise RuntimeError("Emotion_Core Fast_Loop failed to start within 5 seconds")
```

**`shutdown()` (Requirement 8.6):**

```python
def shutdown(self) -> None:
    self._emotion_core.stop()
    self._emotion_core_thread.join(timeout=2.0)
    self._llm_backend.shutdown()
```

**Degraded State:** Once `_degraded = True`, all subsequent `process()` calls immediately return `fallback_response`. The Emotion_Core Fast_Loop is explicitly left running (Requirement 8.7). The degraded flag is reset only by constructing a new `Orchestrator` instance.

**Non-interference with Fast_Loop (Requirement 8.9):** The `process()` path acquires `_state_lock` only for the `get_pad_state()` call, which holds the lock for at most 1 ms. No other pipeline step touches the lock. The Fast_Loop sleep compensates for any overrun, so a 50 ms delay in `process()` does not starve a subsequent tick — it only delays when the next tick fires, not whether it fires.

---

## Data Models

### PADState

```python
@dataclass(frozen=True)
class PADState:
    pleasure:   float          # [-1.0, 1.0]
    arousal:    float          # [-1.0, 1.0]
    dominance:  float          # [-1.0, 1.0]
    timestamp:  float          # monotonic seconds
```

### SomaticMarkers

```python
@dataclass(frozen=True)
class SomaticMarkers:
    stability:      float      # [0.0, 1.0]
    cognitive_load: float      # [0.0, 1.0]
    energy:         float      # [0.0, 1.0]
    tension:        float      # [0.0, 1.0]
```

### BehavioralConstraints

```python
@dataclass(frozen=True)
class BehavioralConstraints:
    max_tokens:      int       # [1, 2048]
    temperature:     float     # [0.0, 2.0]
    latency_ms:      int       # [0, 5000]
    reasoning_depth: int       # [0, 3]
```

### StimulusVector

A plain `np.ndarray` of shape `(N,)` and `dtype=float64`. All values in `[-1.0, 1.0]`.

### Configuration Objects

Each module's config is a plain Python dataclass. All fields are validated in `__init__`; any violation raises `ValueError` identifying the invalid field and its acceptable range.

### SoftBlockEvent

```python
@dataclass
class SoftBlockEvent:
    pattern_matched:  str
    original_span:    str
    substituted_text: str
    utc_timestamp:    datetime
```

---

## Correctness Properties

*A property is a characteristic or behavior that should hold true across all valid executions of a system — essentially, a formal statement about what the system should do. Properties serve as the bridge between human-readable specifications and machine-verifiable correctness guarantees.*

### Property 1: PAD State Bounds Invariant

*For any* hidden LNN state vector and any linear projection, all three dimensions of the resulting PAD_State (pleasure, arousal, dominance) must lie in `[-1.0, 1.0]` after clamping.

**Validates: Requirements 1.1, 1.7**

---

### Property 2: ODE Step Intermediate Clamping

*For any* valid stimulus vector and any current hidden state, after one ODE solve step, the resulting hidden state must have all values within `[-1.0, 1.0]` (intermediate clamp applied before projection).

**Validates: Requirements 1.4**

---

### Property 3: Somatic Markers Completeness and Bounds

*For any* PAD_State with all dimensions in `[-1.0, 1.0]`, and any valid valence in `[0.0, 1.0]`, the resulting SomaticMarkers must have all four fields (stability, cognitive_load, energy, tension) present and each in `[0.0, 1.0]`.

**Validates: Requirements 2.1, 2.2, 2.5**

---

### Property 4: Tension Validity Domain

*For any* valence value outside `[0.0, 1.0]` and any PAD_State, calling `compute_somatic_markers` with that valence must raise a `ValueError` and must not return a `SomaticMarkers` object.

**Validates: Requirements 2.5**

---

### Property 5: Behavioral Constraints Output Ranges

*For any* valid SomaticMarkers and PAD_State, the resulting BehavioralConstraints must have:
- `max_tokens` in `[1, 2048]`
- `temperature` in `[0.0, 2.0]`
- `latency_ms` in `[0, 5000]`
- `reasoning_depth` in `[0, 3]`

**Validates: Requirements 3.1**

---

### Property 6: Behavioral Constraints Priority Resolution

*For any* SomaticMarkers input that simultaneously satisfies multiple conflicting criteria for the same parameter, the resulting BehavioralConstraints must consistently apply the highest-`cognitive_load` criterion for `max_tokens` and `latency_ms`, and the highest-`arousal` criterion for `temperature`.

**Validates: Requirements 3.11**

---

### Property 7: Out-of-Bounds PAD Raises ValueError

*For any* PAD_State where at least one dimension is outside `[-1.0, 1.0]`, calling `compute_behavioral_constraints` must raise a `ValueError`.

**Validates: Requirements 3.12**

---

### Property 8: Stimulus Vector Shape Invariant

*For any* non-empty UTF-8 string, `StimulusProcessor.encode()` must return an `np.ndarray` of shape `(N,)` where `N` is the configured dimensionality.

**Validates: Requirements 4.1**

---

### Property 9: Stimulus Vector Bounds Invariant

*For any* input string (including empty), all values in the returned Stimulus_Vector must be in `[-1.0, 1.0]`.

**Validates: Requirements 4.2**

---

### Property 10: Non-Zero Semantic Dimensions

*For any* non-empty input string (at least 1 non-whitespace character), the Stimulus_Vector returned by `encode()` must have non-zero absolute values for dimensions 0, 1, and 2.

**Validates: Requirements 4.9**

---

### Property 11: Conditioned Prompt Section Order

*For any* SomaticMarkers, BehavioralConstraints, and conversation history, the assembled Conditioned_Prompt must always contain sections in the fixed order: (1) system preamble, (2) somatic state as numeric values, (3) reasoning section if `reasoning_depth > 0`, (4) conversation history — separated by the section boundary marker.

**Validates: Requirements 5.1, 5.2**

---

### Property 12: Conversation History Truncation Bound

*For any* conversation history of arbitrary length and any `max_tokens` value, the number of history turns included in the Conditioned_Prompt must never exceed `min(10, floor(max_tokens * 4 / estimated_turn_tokens))`.

**Validates: Requirements 5.3**

---

### Property 13: Reasoning Step Count

*For any* `reasoning_depth` value in `{1, 2, 3}`, the number of chain-of-thought steps in the Conditioned_Prompt must equal `min((reasoning_depth * 2) - 1, 5)`.

**Validates: Requirements 5.5**

---

### Property 14: Boundary Layer Pattern Replacement

*For any* output string that contains at least one match for any configured pattern, `validate()` must return a string where the matched spans are replaced with `"[...]"` and the original matched text is no longer present.

**Validates: Requirements 7.3, 9.2**

---

### Property 15: Boundary Layer Passthrough

*For any* output string that contains no match for any configured pattern, `validate()` must return the string unmodified (output equals input).

**Validates: Requirements 7.4**

---

### Property 16: Boundary Layer Idempotence

*For any* output string that contains no Meta-Self-Awareness_Pattern, applying `validate()` twice must produce the same result as applying it once.

**Validates: Requirements 7.9**

---

### Property 17: Orchestrator Input Rejection

*For any* input string of length 0 or length exceeding 4000 characters, `process()` must return an error-indicating string immediately without executing any pipeline steps.

**Validates: Requirements 8.10**

---

### Property 18: Out-of-Range Configuration Raises ValueError

*For any* configuration object where at least one field is outside its documented valid range, any module's `__init__` must raise a `ValueError` identifying the invalid parameter.

**Validates: Requirements 10.7, 10.8**

---

## Error Handling

### Module-Level Error Matrix

| Module | Error Condition | Response |
|--------|----------------|----------|
| `StimulusProcessor.__init__` | `vector_dim < 3` | `ValueError` |
| `StimulusProcessor.encode` | Empty string | Returns zero vector, no exception |
| `StimulusProcessor.encode` | String > `char_limit` | Truncate + `warnings.warn()` |
| `EmotionCore._fast_loop_worker` | Any unhandled exception | Log, reset to resting baseline, resume loop |
| `EmotionCore.start` | Thread fails within 5 s | Raise `RuntimeError` (caught by Orchestrator) |
| `HomeostaticEngine.compute_somatic_markers` | `valence` outside `[0.0, 1.0]` | `ValueError` |
| `HomeostaticEngine.compute_behavioral_constraints` | PAD dimension outside `[-1.0, 1.0]` | `ValueError`; return last valid or default constraints |
| `LLMBackend.__init__` | Model file not found | `FileNotFoundError` |
| `LLMBackend.__init__` | Zero GPU layers allocated | `RuntimeError` with layer count |
| `LLMBackend.generate` | Timeout | Return `None`, log warning |
| `LLMBackend.generate` | Model error | Return `None`, log error |
| `PromptAssembler.assemble` | Preamble alone exceeds context window | Return `AssemblyError` |
| `BoundaryLayer.__init__` | > 50 patterns supplied | Accept first 50 silently |
| `Orchestrator.__init__` | Missing required config key | `ValueError` identifying the key |
| `Orchestrator.__init__` | Config value out of range | `ValueError` identifying field and range |
| `Orchestrator.__init__` | Fast_Loop not ready within 5 s | `RuntimeError` |
| `Orchestrator.process` | Input empty or > 4000 chars | Return fallback response immediately |
| `Orchestrator.process` | Any unhandled pipeline exception | Log with stack trace, enter Degraded_State, return fallback |
| `Orchestrator.process` | Called in Degraded_State | Return fallback response immediately |

### Degraded State Lifecycle

```
Orchestrator (healthy)
       │
       │  unhandled exception in process()
       ▼
Orchestrator (DEGRADED)
  - all process() calls → fallback_response
  - Emotion_Core Fast_Loop continues running
  - LLM_Backend remains loaded
       │
       │  only a new Orchestrator instance resets this
       ▼
Orchestrator (new instance, healthy)
```

### Boundary Layer Double-Failure

```
LLM generates response
    │
    ▼
Boundary_Layer.validate()
    │
    ├── no pattern match → return response ✓
    │
    └── pattern match → Soft_Block
            │
            ├── substitute "[...]" → return modified response ✓
            │
            └── if incomplete clause → truncate to last sentence
                    │
                    └── if no complete sentence → return "[...]"
```

The Soft_Block in Phase 1 performs pattern replacement inline rather than triggering a true LLM regeneration (which would require the Orchestrator to maintain re-try state). Full regeneration-with-retry is deferred to Phase 2. For Phase 1, the Boundary_Layer replaces matched spans and truncates as above, then the Orchestrator checks if the result is only `"[...]"` and substitutes the configured `fallback_response` instead.

---

## Testing Strategy

### Unit Tests

Unit tests use `pytest` and cover specific examples, edge cases, and error conditions. They run fully in-process with no GPU or model file required (LLM_Backend is mocked).

**StimulusProcessor:**
- `encode("")` returns zero vector of correct shape
- `encode(string of 4097 chars)` truncates and emits warning
- `encode(string of 4096 chars)` does not warn
- `vector_dim=2` raises `ValueError` at init
- `vector_dim=3` succeeds; output shape is `(3,)`
- Valence dimension of a very negative sentence is negative
- Valence dimension of a very positive sentence is positive

**EmotionCore:**
- Initialized PAD_State equals configured resting baseline
- Fast_Loop thread is alive after `start()`
- Exception inside ODE step resets state to resting baseline and thread stays alive
- `get_pad_state()` acquires lock within 1 ms under contention

**HomeostaticEngine:**
- Resting baseline + 60 s idle → all marker thresholds met (Requirement 2.7)
- `valence=1.5` raises `ValueError`
- PAD dimension `1.1` raises `ValueError`
- `cognitive_load=0.9, energy=0.2` → `max_tokens <= 80`
- `energy=0.05` → `reasoning_depth=0`

**BoundaryLayer:**
- Each of the 10 default patterns triggers a Soft_Block
- Incomplete clause (ending with ", [...]") is truncated
- No-sentence incomplete clause returns `"[...]"`
- 51 patterns → only 50 stored
- `add_pattern`/`remove_pattern` take effect on next `validate()` call

**Orchestrator:**
- Empty string returns fallback immediately (no pipeline steps logged)
- String of 4001 characters returns fallback immediately
- Degraded state after mock-injected pipeline exception; subsequent call returns fallback
- `shutdown()` joins thread within 2 s

### Property-Based Tests

Property-based tests use [Hypothesis](https://hypothesis.readthedocs.io/) (Python) with `settings(max_examples=200)` per property to ensure broad input coverage. Each property test is tagged with a comment in the format:

```python
# Feature: lucia-core-phase1, Property {N}: {property_text}
```

| Property | Hypothesis Strategy |
|----------|---------------------|
| P1: PAD bounds invariant | `arrays(float64, 3, elements=floats(-10, 10))` → project → clamp |
| P2: ODE step clamping | `arrays(float64, hidden_dim)` for h, `arrays(float64, N)` for x |
| P3: Somatic markers bounds | `from_type(PADState)` with values in `[-1,1]`, `valence` in `[0,1]` |
| P4: Tension ValueError | `floats(-10.0, 10.0).filter(lambda v: not 0.0 <= v <= 1.0)` |
| P5: Constraints output ranges | `builds(SomaticMarkers, ...)` with all fields in `[0,1]` |
| P6: Constraints priority resolution | Strategies generating overlapping threshold conditions |
| P7: Out-of-bounds PAD raises | `arrays(float64, 3)` with at least one value outside `[-1, 1]` |
| P8: Stimulus shape invariant | `text(min_size=1, max_size=500)` |
| P9: Stimulus bounds invariant | `text(min_size=0, max_size=4096)` |
| P10: Non-zero dims | `text(min_size=1, alphabet=printable)` |
| P11: Prompt section order | `builds(SomaticMarkers,...)`, `lists(tuples(...))`, `integers(0,3)` |
| P12: History truncation bound | `lists(tuples(text(), text()), min_size=0, max_size=20)` |
| P13: Reasoning step count | `integers(1, 3)` |
| P14: Pattern replacement | `text().map(embed_pattern)` where `embed_pattern` inserts a default pattern |
| P15: Passthrough | `text().filter(no_pattern_match)` |
| P16: Idempotence | `text().filter(no_pattern_match)` → apply twice |
| P17: Input rejection | `integers(0, 0)` and `integers(4001, 10000)` mapped to strings |
| P18: Config validation | strategies generating each config field individually out of range |

### Integration Tests

Integration tests cover behaviors that require the full module stack or real timing:

- Orchestrator startup: Fast_Loop becomes alive and ticks within 5 s
- End-to-end `process()` call with a mocked LLM_Backend returns a non-empty string
- PAD state evolves after multiple `process()` calls (state is not frozen)
- Boundary_Layer Soft_Block event is logged after a flagged LLM response
- Orchestrator `shutdown()` cleanly joins the Fast_Loop thread

GPU/model integration tests (requiring actual LFM2.5-1.2B GGUF) are isolated in `tests/integration/` and skipped unless `LUCIA_MODEL_PATH` environment variable is set.

### Test File Layout

```
tests/
  unit/
    test_stimulus_processor.py
    test_emotion_core.py
    test_homeostatic_engine.py
    test_llm_backend.py
    test_prompt_assembler.py
    test_boundary_layer.py
    test_orchestrator.py
  integration/
    test_orchestrator_integration.py
    test_llm_backend_integration.py  # skipped without model
  property/
    test_properties.py               # all P1–P18 Hypothesis tests
```
