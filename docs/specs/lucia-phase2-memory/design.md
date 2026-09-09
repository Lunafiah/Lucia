# Design Document — Lucia Memory Phase 2

## Overview

Phase 2 extends the Phase 1 pipeline with a biologically-inspired, affect-driven memory system. Five cooperating modules are added:

1. **SDM_Core** (`src/core/memory/sdm.py`) — Kanerva's Sparse Distributed Memory backed by dense NumPy arrays. Fixed-capacity hard-location address space with distributed Hamming-distance read/write.
2. **Affective_Memory** (`src/core/memory/affective_memory.py`) — Wraps SDM_Core to co-encode each stored trace with a PAD affective tag representing emotional context at the moment of encoding.
3. **Decay_Engine** (`src/core/memory/decay.py`) — Background slow-loop thread that weakens trace `decay_weight` over time at a rate inversely proportional to emotional intensity, purging traces that fall below viability.
4. **Ecphory_Engine** (`src/core/memory/ecphory.py`) — Computes cosine similarity in 3D PAD space between the active emotional state and all stored PAD tags, then assembles an Echo_Vector from the top-K resonant traces.
5. **Memory_Augmented_Orchestrator** (`src/core/orchestrator/orchestrator.py`) — Extends the Phase 1 Orchestrator (by subclassing) with a memory echo step inserted between pipeline step 4 (behavioral constraint derivation) and step 5 (prompt assembly).

The central design constraint from the requirements is maintained throughout: memory **never** surfaces as first-person recall language. The Echo_Vector reaches the LLM only as a sequence of numeric key-value pairs under a `[MEMORY ECHO]` section header, influencing generation through behavioral texture, not through explicit recollection.

---

## Architecture

### Phase 2 Module Additions to Phase 1 Pipeline

```
User / Caller
     │
     ▼
┌────────────────────────────────────────────────────────────────┐
│  Memory_Augmented_Orchestrator  (extends Phase 1 Orchestrator) │
│                                                                │
│  process(input_text)                                           │
│       │                                                        │
│       ▼                                                        │
│  Step 1: Stimulus_Processor.encode(input_text)                 │
│       │                                                        │
│       ▼                                                        │
│  Step 2: Emotion_Core.push_stimulus(stimulus)                  │
│       │                                                        │
│       ▼                                                        │
│  Step 3: pad = Emotion_Core.get_pad_state()                    │
│          HomeostaticEngine.record_input()                      │
│          markers = HomeostaticEngine.compute_somatic_markers() │
│       │                                                        │
│       ▼                                                        │
│  Step 4: constraints = compute_behavioral_constraints()        │
│       │                                                        │
│       ▼  ◄─── NEW in Phase 2 ────────────────────────────────  │
│  Step 4b: traces = Affective_Memory.get_all_traces()           │
│           echo_vec = Ecphory_Engine.query(pad, traces)         │
│       │                                                        │
│       ▼                                                        │
│  Step 5: prompt = PromptAssembler.assemble(                    │
│                     somatic, constraints, history,             │
│                     system_preamble, echo_vector=echo_vec)     │
│       │                                                        │
│       ▼                                                        │
│  Step 6: latency delay                                         │
│       │                                                        │
│       ▼                                                        │
│  Step 7: raw = LLM_Backend.generate(prompt, constraints)       │
│       │                                                        │
│       ▼                                                        │
│  Step 8: safe = Boundary_Layer.validate(raw)                   │
│       │                                                        │
│       ▼  ◄─── NEW in Phase 2 ────────────────────────────────  │
│  Step 9: Affective_Memory.store(stimulus_padded, pad_snapshot) │
│       │                                                        │
└───────┼────────────────────────────────────────────────────────┘
        │
        ▼
   response: str
```

### Concurrent Loop Structure

Phase 2 adds one new background thread:

| Loop | Timescale | Owner | Purpose |
|------|-----------|-------|---------|
| Fast Loop | 100–500 ms | Emotion_Core | LNN ODE advance, PAD update |
| Slow Loop | 3600 s (default) | Decay_Engine | Trace decay + purge |

The Slow Loop is a daemon thread. It holds the Affective_Memory index lock only during the brief window when it applies decay updates and purges expired traces, then releases immediately.

### Threading Model

```
Main Thread
    ├── MemoryAugmentedOrchestrator.process() (serialized per call)
    └── LLM_Backend (GPU inference, ThreadPoolExecutor)

Background Thread 1 (daemon) — inherited from Phase 1
    └── Emotion_Core._fast_loop_worker()

Background Thread 2 (daemon) — new in Phase 2
    └── Decay_Engine._slow_loop_worker()
            ├── acquire Affective_Memory._index_lock (RLock)
            ├── apply decay to all traces
            ├── purge expired traces → SDM_Core.delete()
            └── release lock
```

**Lock discipline:**
- `Affective_Memory._index_lock` is a `threading.RLock`. This allows the `get_all_traces()` snapshot call from the Ecphory path and the `store()` call from the Orchestrator post-response step to reenter without deadlock if they ever share a call stack.
- The Decay_Engine acquires the same `_index_lock` during its tick. The lock hold time during a tick is bounded by the number of traces × O(1) per trace — for 10,000 traces this is expected to be well under 50 ms, satisfying the ≤ 5 ms acquisition bound for the Orchestrator only when the lock is already free.
- The Orchestrator's `process()` path acquires the lock only twice per call: once in `get_all_traces()` (read snapshot) and once in `store()` (write). Both are short critical sections.

---

## Components and Interfaces

### SDM_Core (`src/core/memory/sdm.py`)

**Responsibility:** Maintain the hard-location address space and perform distributed read/write via Hamming distance activation.

```python
class CapacityError(Exception):
    """Raised when a write is attempted on a full SDM store."""

@dataclass
class SDMConfig:
    num_locations: int = 1_000          # >= 100
    address_dim: int = 1_000            # D, >= 64
    content_dim: int = 64               # M, >= 8
    hamming_radius_fraction: float = 0.451  # (0.0, 1.0), radius = D * fraction
    capacity: int = 10_000              # SDM_Capacity

class SDMCore:
    def __init__(self, config: SDMConfig) -> None: ...
    def write(self, address: np.ndarray, content: np.ndarray) -> int: ...
    def read(self, address: np.ndarray) -> np.ndarray: ...
    def delete(self, trace_id: int) -> None: ...
    @property
    def trace_count(self) -> int: ...
    @property
    def capacity(self) -> int: ...
    def memory_usage_bytes(self) -> int: ...
```

**Internal state layout:**

| Array | Shape | dtype | Purpose |
|-------|-------|-------|---------|
| `_hard_locs` | `(num_locations, D)` | `uint8` | Binary hard-location address matrix (one bit per element, stored as 0/1 uint8) |
| `_accumulator` | `(num_locations, M)` | `float32` | Content accumulator — sum of all written content vectors per location |
| `_act_counts` | `(num_locations,)` | `int64` | Activation count per hard location |
| `_trace_addresses` | `dict[int, np.ndarray]` | — | Maps `trace_id` → `address_vector` (uint8, shape `(D,)`) for delete support |

`_hard_locs` is generated at `__init__` using `np.random.default_rng().integers(0, 2, size=(num_locations, D), dtype=np.uint8)`.

#### Hamming Distance (NumPy XOR + popcount)

```python
def _hamming_distances(self, address: np.ndarray) -> np.ndarray:
    # address: uint8 array of shape (D,)
    # _hard_locs: uint8 array of shape (num_locations, D)
    xor = self._hard_locs ^ address[np.newaxis, :]   # (num_locations, D)
    # np.unpackbits is not needed — values are already 0 or 1 per element
    # Hamming distance = number of differing bits = sum of XOR per row
    return xor.sum(axis=1)                            # (num_locations,)
```

Since `_hard_locs` stores individual bits as 0/1 `uint8` values (not packed bytes), the XOR result is also 0/1 per element, and `sum(axis=1)` gives the exact Hamming distance. This avoids the `np.unpackbits` pathway (which requires bit-packing to 8-bits-per-byte) and is vectorized over all locations in a single NumPy call.

**Hamming radius:** `self._hamming_radius = int(config.address_dim * config.hamming_radius_fraction)`

#### Activation Logic (shared by read and write)

```python
def _activate(self, address: np.ndarray) -> np.ndarray:
    """Return indices of activated hard locations (with fallback)."""
    distances = self._hamming_distances(address)
    mask = distances <= self._hamming_radius
    if mask.any():
        return np.where(mask)[0]
    else:
        # Fallback: single closest location
        return np.array([np.argmin(distances)])
```

#### Write

```python
def write(self, address: np.ndarray, content: np.ndarray) -> int:
    if address.shape != (self._D,):
        raise ValueError(f"address dim {address.shape[0]} != {self._D}")
    if content.shape != (self._M,):
        raise ValueError(f"content dim {content.shape[0]} != {self._M}")
    if self.trace_count >= self.capacity:
        raise CapacityError(
            f"SDM at capacity ({self.capacity}); attempted write at address {address[:8]}..."
        )
    activated = self._activate(address)
    self._accumulator[activated] += content.astype(np.float32)
    self._act_counts[activated] += 1
    trace_id = self._next_id
    self._next_id += 1
    self._trace_addresses[trace_id] = address.copy()
    return trace_id
```

#### Read

```python
def read(self, address: np.ndarray) -> np.ndarray:
    if address.shape != (self._D,):
        raise ValueError(f"address dim {address.shape[0]} != {self._D}")
    activated = self._activate(address)
    counts = self._act_counts[activated]
    total_count = counts.sum()
    if total_count == 0:
        return np.zeros(self._M, dtype=np.float32)
    rows = self._accumulator[activated]                    # (k, M)
    weighted_sum = (rows * counts[:, np.newaxis]).sum(axis=0)  # (M,)
    result = weighted_sum / total_count
    return np.clip(result, -1.0, 1.0).astype(np.float32)
```

#### Delete

```python
def delete(self, trace_id: int) -> None:
    if trace_id not in self._trace_addresses:
        raise KeyError(f"trace_id {trace_id} not found in SDM store")
    address = self._trace_addresses.pop(trace_id)
    # Note: accumulator rows are NOT zeroed on delete — distributed writes
    # cannot be cleanly reversed without per-location per-trace bookkeeping.
    # Delete affects only the capacity counter and trace_addresses index.
    # Decay purge is the primary removal path; the accumulator naturally
    # dilutes as new traces overwrite nearby locations.
```

**`memory_usage_bytes()`:**

```python
def memory_usage_bytes(self) -> int:
    return (self._hard_locs.nbytes
            + self._accumulator.nbytes
            + self._act_counts.nbytes)
```

---

### Affective_Memory (`src/core/memory/affective_memory.py`)

**Responsibility:** Encode and store memory traces pairing a semantic Content_Vector with the PAD emotional context at encoding time.

```python
@dataclass
class MemoryTrace:
    """Mutable: decay_weight is updated in-place by Decay_Engine."""
    trace_id:      int
    address_vec:   np.ndarray   # uint8, shape (D,)
    content_vec:   np.ndarray   # float32, shape (M,)
    pad_tag:       PADState     # frozen copy of PADState at encoding moment
    timestamp:     float        # time.monotonic() at store() call
    decay_weight:  float        # initialized to 1.0; mutated by Decay_Engine

@dataclass
class AffectiveMemoryConfig:
    sdm_config: SDMConfig
    m: int = 64                 # content dimensionality (must match sdm_config.content_dim)

class AffectiveMemory:
    def __init__(self, config: AffectiveMemoryConfig) -> None: ...
    def store(self, content_vector: np.ndarray, pad_state: PADState) -> int: ...
    def get_all_traces(self) -> list[MemoryTrace]: ...
    def get_trace(self, trace_id: int) -> MemoryTrace: ...
    def delete_trace(self, trace_id: int) -> None: ...
    def index_memory_usage_bytes(self) -> int: ...
```

**Internal state:**

```python
self._sdm: SDMCore
self._index: dict[int, MemoryTrace]   # trace_id → MemoryTrace
self._index_lock: threading.RLock     # reentrant — allows nested reads during snapshot
```

#### `store()`

```python
def store(self, content_vector: np.ndarray, pad_state: PADState) -> int:
    if content_vector.shape != (self._M,):
        raise ValueError(f"content_vector dim {content_vector.shape[0]} != {self._M}")
    for dim, val in [("pleasure", pad_state.pleasure),
                     ("arousal",  pad_state.arousal),
                     ("dominance",pad_state.dominance)]:
        if not (-1.0 <= val <= 1.0):
            raise ValueError(f"PAD dimension '{dim}'={val} outside [-1.0, 1.0]")

    with self._index_lock:
        # Evict lowest decay_weight trace if at capacity
        if self._sdm.trace_count >= self._sdm.capacity:
            victim_id = min(self._index, key=lambda tid: self._index[tid].decay_weight)
            self.delete_trace(victim_id)

        # Derive binary address by thresholding at zero
        address = (content_vector >= 0.0).astype(np.uint8)

        trace_id = self._sdm.write(address, content_vector.astype(np.float32))
        trace = MemoryTrace(
            trace_id=trace_id,
            address_vec=address,
            content_vec=content_vector.astype(np.float32).copy(),
            pad_tag=pad_state,       # PADState is frozen; no copy needed
            timestamp=time.monotonic(),
            decay_weight=1.0,
        )
        self._index[trace_id] = trace
        return trace_id
```

#### `get_all_traces()`

```python
def get_all_traces(self) -> list[MemoryTrace]:
    with self._index_lock:
        return list(self._index.values())
```

The returned list is a snapshot — it reflects the index state at call time. Callers (Ecphory_Engine) operate on this snapshot without holding the lock.

#### `delete_trace()` — called by Decay_Engine

```python
def delete_trace(self, trace_id: int) -> None:
    # Caller MUST hold _index_lock
    self._sdm.delete(trace_id)
    self._index.pop(trace_id, None)
```

Decay_Engine calls this while it already holds `_index_lock`, so no re-lock is needed. The `RLock` allows reentry from the same thread without deadlocking.

---

### Decay_Engine (`src/core/memory/decay.py`)

**Responsibility:** Background slow-loop that applies time-based decay to all stored Memory_Traces and purges expired ones.

```python
@dataclass
class DecayConfig:
    base_decay_rate: float = 0.0001      # per second, valid range (0.0, 1.0)
    viability_threshold: float = 0.05   # valid range (0.0, 1.0)
    loop_cadence_seconds: int = 3600    # valid range [60, 86400]

class DecayEngine:
    def __init__(self, memory: AffectiveMemory, config: DecayConfig) -> None: ...
    def start(self) -> None: ...
    def stop(self) -> None: ...
    def is_alive(self) -> bool: ...
```

#### Emotional Intensity Formula

```python
def _emotional_intensity(self, pad_tag: PADState) -> float:
    raw = abs(pad_tag.arousal) * (abs(pad_tag.pleasure) + 0.1)
    return float(np.clip(raw, 0.0, 1.0))
```

#### Decay Rate Per Trace

```python
def _decay_rate(self, pad_tag: PADState) -> float:
    return self._config.base_decay_rate * (1.0 - self._emotional_intensity(pad_tag))
```

A trace with `Emotional_Intensity = 0.0` decays at `base_decay_rate = 0.0001/s`, giving a half-life of approximately `ln(1/0.5) / 0.0001 ≈ 6931 s ≈ 1.9 hours`. A trace with maximum intensity (`1.0`) has a decay rate of `0.0`, persisting indefinitely until evicted.

#### Slow Loop Worker

```python
def _slow_loop_worker(self) -> None:
    last_tick = time.monotonic()
    while not self._stop_event.is_set():
        # Interruptible sleep using threading.Event
        self._stop_event.wait(timeout=self._config.loop_cadence_seconds)
        if self._stop_event.is_set():
            break

        now = time.monotonic()
        elapsed = now - last_tick
        last_tick = now

        try:
            self._apply_decay_tick(elapsed)
        except Exception:
            logger.error("Decay_Engine tick failed", exc_info=True)
            # Index is left unchanged; loop resumes next cycle

def _apply_decay_tick(self, elapsed_seconds: float) -> None:
    to_purge: list[int] = []

    with self._memory._index_lock:
        for trace_id, trace in self._memory._index.items():
            rate = self._decay_rate(trace.pad_tag)
            new_weight = trace.decay_weight - rate * elapsed_seconds
            trace.decay_weight = float(np.clip(new_weight, 0.0, 1.0))
            if trace.decay_weight <= self._config.viability_threshold:
                to_purge.append(trace_id)

        for trace_id in to_purge:
            self._memory.delete_trace(trace_id)

    logger.info(
        "Decay tick: elapsed=%.1fs traces_purged=%d traces_remaining=%d",
        elapsed_seconds, len(to_purge), len(self._memory._index),
    )
```

The entire tick — decay update + purge — is performed within a single `_index_lock` acquisition, satisfying the atomicity requirement (Req 7.8). Using `threading.Event.wait(timeout=cadence)` rather than `time.sleep(cadence)` means the loop responds to `stop()` within 1 second (Req 8.4).

#### Lifecycle

```python
def start(self) -> None:
    self._stop_event.clear()
    self._thread = threading.Thread(
        target=self._slow_loop_worker, daemon=True, name="DecayEngine-SlowLoop"
    )
    self._thread.start()
    deadline = time.monotonic() + 2.0
    while time.monotonic() < deadline:
        if self._thread.is_alive():
            return
        time.sleep(0.05)
    raise RuntimeError("Decay_Engine Slow_Loop failed to start within 2 seconds")

def stop(self) -> None:
    self._stop_event.set()
    if self._thread is not None:
        self._thread.join(timeout=5.0)
        self._thread = None

def is_alive(self) -> bool:
    return self._thread is not None and self._thread.is_alive()
```

---

### Ecphory_Engine (`src/core/memory/ecphory.py`)

**Responsibility:** Score all stored Memory_Traces by PAD-space resonance with the current emotional state, then assemble a weighted Echo_Vector from the top-K resonant traces.

```python
@dataclass
class EcphoryConfig:
    resonance_threshold: float = 0.6   # [0.0, 1.0]
    ecphory_k: int = 5                 # [1, 50]
    viability_threshold: float = 0.05  # must match Decay_Engine config

class EcphoryEngine:
    def __init__(self, config: EcphoryConfig) -> None: ...
    def query(
        self,
        pad_state: PADState,
        traces: list[MemoryTrace],
    ) -> np.ndarray | None: ...
```

#### Cosine Similarity (3D PAD space)

```python
def _resonance_score(self, pad_state: PADState, pad_tag: PADState) -> float:
    a = np.array([pad_state.pleasure, pad_state.arousal, pad_state.dominance],
                 dtype=np.float64)
    b = np.array([pad_tag.pleasure,   pad_tag.arousal,   pad_tag.dominance],
                 dtype=np.float64)
    norm_a = np.linalg.norm(a)
    norm_b = np.linalg.norm(b)
    if norm_a == 0.0 or norm_b == 0.0:
        return 0.0
    return float(np.dot(a, b) / (norm_a * norm_b))
```

Working in 3D means the entire computation is three multiplications, two square roots, and a dot product — effectively free at runtime.

#### `query()`

```python
def query(
    self,
    pad_state: PADState,
    traces: list[MemoryTrace],
) -> np.ndarray | None:
    for dim, val in [("pleasure", pad_state.pleasure),
                     ("arousal",  pad_state.arousal),
                     ("dominance",pad_state.dominance)]:
        if not (-1.0 <= val <= 1.0):
            raise ValueError(f"PAD dimension '{dim}'={val} outside [-1.0, 1.0]")

    # Early-exit: zero-magnitude PAD cannot produce meaningful cosine scores
    pad_vec = np.array([pad_state.pleasure, pad_state.arousal, pad_state.dominance])
    if np.linalg.norm(pad_vec) == 0.0:
        return None

    # Score and filter candidates
    scored: list[tuple[float, MemoryTrace]] = []
    for trace in traces:
        if trace.decay_weight <= self._config.viability_threshold:
            continue
        score = self._resonance_score(pad_state, trace.pad_tag)
        if score > self._config.resonance_threshold:
            scored.append((score, trace))

    if not scored:
        return None

    # Select top-K by descending resonance score
    scored.sort(key=lambda t: t[0], reverse=True)
    top_k = scored[: self._config.ecphory_k]

    # Weighted mean: weight = resonance_score × decay_weight
    weights = np.array(
        [score * trace.decay_weight for score, trace in top_k], dtype=np.float64
    )
    content_matrix = np.stack(
        [trace.content_vec.astype(np.float64) for _, trace in top_k], axis=0
    )  # shape: (k, M)

    weight_sum = weights.sum()
    if weight_sum == 0.0:
        return None

    echo = (content_matrix * weights[:, np.newaxis]).sum(axis=0) / weight_sum
    return np.clip(echo, -1.0, 1.0).astype(np.float32)
```

The result is a deterministic pure function of its inputs — given the same `traces` snapshot and `pad_state`, the output is always identical (Req 10.7). No randomness or global state is involved.

---

### PromptAssembler Extension (`src/core/orchestrator/prompt_assembler.py`)

**Responsibility:** Extend the Phase 1 `assemble()` method to accept an optional `echo_vector` parameter and, when provided, append a `[MEMORY ECHO]` section before returning the prompt.

```python
class PromptAssembler:
    SECTION_SEP = "\n\n---\n\n"

    # Phase 1 signature:
    # def assemble(self, somatic, constraints, history, system_preamble) -> str | AssemblyError

    def assemble(
        self,
        somatic: SomaticMarkers,
        constraints: BehavioralConstraints,
        history: list[tuple[str, str]],
        system_preamble: str,
        echo_vector: np.ndarray | None = None,    # NEW in Phase 2
    ) -> str | AssemblyError: ...
```

The `echo_vector` parameter is `None` by default, preserving full backward compatibility with Phase 1 call sites.

#### `[MEMORY ECHO]` Section Format

```python
def _encode_echo_section(self, echo_vector: np.ndarray) -> str:
    lines = ["[MEMORY ECHO]"]
    for i, val in enumerate(echo_vector):
        lines.append(f"echo_{i}: {float(val):.6f}")
    section = "\n".join(lines)

    # Safety check — no natural-language recall phrases may appear
    FORBIDDEN = [
        "I remember", "I recall", "last time", "you mentioned",
        "you said", "I know from before", "previously you", "my memory",
    ]
    for phrase in FORBIDDEN:
        if phrase.lower() in section.lower():
            raise AssemblyError(
                f"[MEMORY ECHO] section contains forbidden recall phrase: '{phrase}'"
            )
    return section
```

**Section order with echo:**

```
{system_preamble}
---
[SOMATIC STATE]
stability: 0.812345
cognitive_load: 0.234567
energy: 0.923456
tension: 0.045678
---
[MEMORY ECHO]
echo_0: 0.123456
echo_1: -0.234567
...
echo_63: 0.012345
---
[REASONING]           ← omitted when reasoning_depth == 0
Step 1: ...
---
[CONVERSATION]
{history turns}
```

The `[MEMORY ECHO]` section is inserted between `[SOMATIC STATE]` and `[REASONING]` (or `[CONVERSATION]` if reasoning is omitted). It contains only numeric key-value pairs. No string annotation describes the source, nature, or temporal origin of the echo values.

---

### Memory_Augmented_Orchestrator (`src/core/orchestrator/orchestrator.py`)

**Responsibility:** Extend the Phase 1 `Orchestrator` by subclassing it. Override `process()` to inject the memory echo step (step 4b) and the post-response store step (step 9). All Phase 1 behavior is inherited unchanged.

```python
@dataclass
class MemoryOrchestratorConfig:
    # All Phase 1 fields (inherited)
    model_path: str
    n_gpu_layers: int = 32
    loop_cadence_ms: int = 200
    resting_baseline: tuple[float, float, float] = (0.1, 0.0, 0.0)
    max_history_turns: int = 10
    fallback_response: str = "[...]"
    llm_timeout_seconds: float = 30.0
    system_preamble: str = ""
    boundary_patterns: list[str] = field(default_factory=list)

    # Phase 2 fields
    sdm_num_locations: int = 1_000
    sdm_address_dim: int = 1_000
    sdm_content_dim: int = 64
    sdm_hamming_radius_fraction: float = 0.451
    sdm_capacity: int = 10_000
    decay_base_rate: float = 0.0001
    decay_viability_threshold: float = 0.05
    decay_loop_cadence_seconds: int = 3600
    ecphory_k: int = 5
    ecphory_resonance_threshold: float = 0.6

class MemoryAugmentedOrchestrator(Orchestrator):
    def __init__(self, config: MemoryOrchestratorConfig) -> None: ...
    def process(self, input_text: str) -> str: ...
    def shutdown(self) -> None: ...
```

#### Initialization

```python
def __init__(self, config: MemoryOrchestratorConfig) -> None:
    self._validate_phase2_config(config)   # raises ValueError for any invalid field
    super().__init__(config)               # starts Emotion_Core Fast_Loop

    sdm_config = SDMConfig(
        num_locations=config.sdm_num_locations,
        address_dim=config.sdm_address_dim,
        content_dim=config.sdm_content_dim,
        hamming_radius_fraction=config.sdm_hamming_radius_fraction,
        capacity=config.sdm_capacity,
    )
    mem_config = AffectiveMemoryConfig(sdm_config=sdm_config, m=config.sdm_content_dim)
    self._affective_memory = AffectiveMemory(mem_config)

    decay_config = DecayConfig(
        base_decay_rate=config.decay_base_rate,
        viability_threshold=config.decay_viability_threshold,
        loop_cadence_seconds=config.decay_loop_cadence_seconds,
    )
    self._decay_engine = DecayEngine(self._affective_memory, decay_config)

    ecphory_config = EcphoryConfig(
        resonance_threshold=config.ecphory_resonance_threshold,
        ecphory_k=config.ecphory_k,
        viability_threshold=config.decay_viability_threshold,
    )
    self._ecphory_engine = EcphoryEngine(ecphory_config)

    # Start Decay_Engine after confirming Fast_Loop is alive (done in super().__init__)
    self._decay_engine.start()
    # Startup log
    logger.info(
        "Memory system initialized: traces=%d sdm_capacity=%d",
        len(self._affective_memory._index), config.sdm_capacity,
    )
```

#### 9-Step `process()` Pipeline

```python
def process(self, input_text: str) -> str:
    # Guards (inherited behavior)
    if len(input_text) == 0 or len(input_text) > 4000:
        return self._config.fallback_response
    if self._degraded:
        return self._config.fallback_response

    call_id = uuid.uuid4().hex
    t_start = time.monotonic()
    echo_top_resonance = 0.0

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

        # Step 4b: memory echo (NEW)
        echo_vec: np.ndarray | None = None
        t_echo_start = time.monotonic()
        try:
            traces = self._affective_memory.get_all_traces()
            echo_vec = self._ecphory_engine.query(pad, traces)
            if echo_vec is not None and traces:
                # Compute top resonance for logging
                pad_arr = np.array([pad.pleasure, pad.arousal, pad.dominance])
                if np.linalg.norm(pad_arr) > 0:
                    scores = [
                        self._ecphory_engine._resonance_score(pad, t.pad_tag)
                        for t in traces
                    ]
                    echo_top_resonance = max(scores) if scores else 0.0
        except Exception:
            logger.error("Ecphory step failed; omitting echo", exc_info=True)
            echo_vec = None
        t_echo_elapsed = time.monotonic() - t_echo_start

        # Step 5: assemble prompt (EXTENDED with echo_vector)
        prompt = self._prompt_assembler.assemble(
            somatic=markers,
            constraints=constraints,
            history=self._history,
            system_preamble=self._config.system_preamble,
            echo_vector=echo_vec,
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

        # Step 9: store new memory trace (NEW)
        try:
            # Pad/truncate stimulus to content dimensionality M
            M = self._affective_memory._M
            if stimulus.shape[0] >= M:
                content = stimulus[:M].astype(np.float32)
            else:
                content = np.zeros(M, dtype=np.float32)
                content[:stimulus.shape[0]] = stimulus.astype(np.float32)
            content = np.clip(content, -1.0, 1.0)
            self._affective_memory.store(content, pad)
        except Exception:
            logger.error("Memory store step failed; continuing", exc_info=True)

        # Structured log (extends Phase 1 log with echo fields)
        logger.info(
            "call_id=%s t=%.3f echo_elapsed=%.3f top_resonance=%.4f "
            "markers=%s constraints=%s",
            call_id,
            time.monotonic() - t_start,
            t_echo_elapsed,
            echo_top_resonance,
            markers,
            constraints,
        )

        self._history.append(("user", input_text))
        self._history.append(("assistant", safe_response))
        return safe_response

    except Exception as e:
        logger.error("Unhandled pipeline exception call_id=%s: %s",
                     call_id, e, exc_info=True)
        self._degraded = True
        return self._config.fallback_response
```

#### `shutdown()`

```python
def shutdown(self) -> None:
    self._decay_engine.stop()   # join with 5-second timeout
    super().shutdown()          # stops Emotion_Core, releases LLM_Backend
```

---

## Data Models

### MemoryTrace

```python
@dataclass
class MemoryTrace:
    trace_id:     int
    address_vec:  np.ndarray   # uint8, shape (D,)
    content_vec:  np.ndarray   # float32, shape (M,)
    pad_tag:      PADState     # frozen dataclass; copied from PADState at store() time
    timestamp:    float        # time.monotonic() at encoding
    decay_weight: float        # 1.0 at creation; mutated by Decay_Engine

    # NOTE: NOT frozen — Decay_Engine mutates decay_weight in place under the index lock
```

### SDMConfig / AffectiveMemoryConfig / DecayConfig / EcphoryConfig

All four are plain Python dataclasses. All fields are validated in the respective `__init__` before any allocation; any violation raises `ValueError` identifying the invalid field and its acceptable range.

### MemoryOrchestratorConfig

Flat dataclass combining all Phase 1 `OrchestratorConfig` fields plus the ten Phase 2 parameters. Validated during `__init__` of `MemoryAugmentedOrchestrator`.

### Echo_Vector

A plain `np.ndarray` of shape `(M,)` and `dtype=float32`. All values in `[-1.0, 1.0]`. Produced exclusively by `EcphoryEngine.query()`; consumed exclusively by `PromptAssembler.assemble()`.

---

## Correctness Properties

*A property is a characteristic or behavior that should hold true across all valid executions of a system — essentially, a formal statement about what the system should do. Properties serve as the bridge between human-readable specifications and machine-verifiable correctness guarantees.*

Properties P1–P18 are defined in the Phase 1 design document. Phase 2 adds P19–P30.

---

### Property 19: SDM Write/Read Approximate Inverse

*For any* valid Content_Vector written to a freshly initialized SDM_Core via a derived Address_Vector, reading back with the same Address_Vector must return a vector whose values are all within `[-1.0, 1.0]` and whose cosine similarity with the original Content_Vector is greater than 0.0 (i.e., read recovers a non-random approximation of the written content).

**Validates: Requirements 2.1, 2.2, 3.1, 3.2, 3.4**

---

### Property 20: SDM Read Bounds Invariant

*For any* SDM_Core state (including empty), and *for any* valid Address_Vector, the result of `read()` must be a vector of shape `(M,)` with all values in `[-1.0, 1.0]`.

**Validates: Requirements 3.4**

---

### Property 21: SDM Capacity Enforcement

*For any* sequence of `N` writes and `K` deletes where `N - K < SDM_Capacity` throughout, no `CapacityError` is raised. When `trace_count` reaches `SDM_Capacity` and an additional write is attempted, a `CapacityError` is raised.

**Validates: Requirements 4.2, 4.5**

---

### Property 22: Affective Memory Store/Retrieve Round Trip

*For any* valid `content_vector` and `pad_state`, after calling `store(content_vector, pad_state)`, calling `get_trace(returned_trace_id)` must return a `MemoryTrace` whose `pad_tag` equals the original `pad_state`, whose `decay_weight` is `1.0`, and whose `trace_id` matches the returned ID.

**Validates: Requirements 5.1, 5.2, 5.3**

---

### Property 23: Decay Monotonicity

*For any* initial `decay_weight` in `[0.0, 1.0]`, any `base_decay_rate` in `(0.0, 1.0)`, any PAD_Tag, and any non-negative `elapsed_seconds`, the post-decay `decay_weight` must be strictly less than or equal to the pre-decay `decay_weight`, and must remain in `[0.0, 1.0]`.

**Validates: Requirements 7.1, 7.2**

---

### Property 24: High-Intensity Traces Decay Slower Than Low-Intensity Traces

*For any* two PAD_Tags where `Emotional_Intensity(tag_a) > Emotional_Intensity(tag_b)`, and *for any* positive `elapsed_seconds`, a trace with `tag_a` loses less `decay_weight` per tick than a trace with `tag_b`, given the same `base_decay_rate` and initial `decay_weight`.

**Validates: Requirements 7.1**

---

### Property 25: Ecphory Determinism

*For any* `PADState` and *for any* list of `MemoryTrace` objects, calling `EcphoryEngine.query()` twice with identical inputs must return two arrays that are element-wise equal (or both `None`).

**Validates: Requirements 10.7**

---

### Property 26: Ecphory Echo Vector Bounds Invariant

*For any* non-empty set of qualifying `MemoryTrace` objects and *for any* valid `PADState`, the `Echo_Vector` returned by `query()` must be a `numpy.ndarray` of shape `(M,)` with all values in `[-1.0, 1.0]`.

**Validates: Requirements 10.1, 10.2**

---

### Property 27: Ecphory Top-K Constraint

*For any* trace list where more than `Ecphory_K` traces pass both the resonance and viability filters, the Echo_Vector must equal the result that would be produced by using only the top-`Ecphory_K` traces ranked by descending `Resonance_Score`, and the lower-ranked qualifying traces must not influence the output.

**Validates: Requirements 9.7, 9.9**

---

### Property 28: No-Recall Language in Echo Section

*For any* `echo_vector`, the encoded `[MEMORY ECHO]` section produced by `PromptAssembler._encode_echo_section()` must not contain any of the forbidden recall phrases (`"I remember"`, `"I recall"`, `"last time"`, `"you mentioned"`, `"you said"`, `"I know from before"`, `"previously you"`, `"my memory"`), and must consist solely of lines in the format `echo_{i}: {float_value}`.

**Validates: Requirements 12.1, 12.3, 12.5**

---

### Property 29: Echo Section Present ↔ Non-None Echo Vector

*For any* call to `PromptAssembler.assemble()`, the assembled prompt contains the `[MEMORY ECHO]` section if and only if the `echo_vector` parameter is not `None`. If `echo_vector` is `None`, no `[MEMORY ECHO]` header or `echo_*` keys appear anywhere in the prompt.

**Validates: Requirements 11.2, 11.4**

---

### Property 30: No-Timeline Invariant — Ecphory Timestamp Independence

*For any* list of `MemoryTrace` objects and *for any* `PADState`, permuting the `timestamp` fields of the traces (while keeping all other fields including `pad_tag`, `content_vec`, and `decay_weight` identical) must not change the result of `EcphoryEngine.query()`.

**Validates: Requirements 16.2, 16.4**

---

## Error Handling

### Phase 2 Error Matrix

| Module | Error Condition | Response |
|--------|----------------|----------|
| `SDMCore.__init__` | `num_locations < 100` or `D < 64` or `M < 8` | `ValueError` identifying invalid param |
| `SDMCore.write` | `address.shape != (D,)` | `ValueError` with actual/expected dims |
| `SDMCore.write` | `content.shape != (M,)` | `ValueError` with actual/expected dims |
| `SDMCore.write` | `trace_count >= capacity` | `CapacityError` with capacity and address |
| `SDMCore.delete` | Unknown `trace_id` | `KeyError` identifying ID |
| `AffectiveMemory.store` | `content_vector.shape != (M,)` | `ValueError` |
| `AffectiveMemory.store` | Any PAD dimension outside `[-1.0, 1.0]` | `ValueError` identifying dimension |
| `AffectiveMemory.get_trace` | Unknown `trace_id` | `KeyError` |
| `DecayEngine.__init__` | `loop_cadence_seconds < 60` | `ValueError` identifying cadence and minimum |
| `DecayEngine._slow_loop_worker` | Any exception during tick | Log + stack trace; resume next cycle |
| `DecayEngine.start` | Thread not alive within 2 s | `RuntimeError` |
| `EcphoryEngine.__init__` | `resonance_threshold` outside `[0.0, 1.0]` | `ValueError` |
| `EcphoryEngine.__init__` | `ecphory_k` outside `[1, 50]` | `ValueError` |
| `EcphoryEngine.query` | Any PAD dimension outside `[-1.0, 1.0]` | `ValueError` identifying dimension |
| `PromptAssembler._encode_echo_section` | Forbidden recall phrase in encoded section | `AssemblyError` identifying phrase |
| `MemoryAugmentedOrchestrator.__init__` | Missing Phase 2 config key | `ValueError` identifying missing key |
| `MemoryAugmentedOrchestrator.__init__` | Phase 2 config value out of range | `ValueError` identifying field and range |
| `MemoryAugmentedOrchestrator.__init__` | `sdm_content_dim != m` in Affective_Memory config | `ValueError` identifying mismatch |
| `MemoryAugmentedOrchestrator.__init__` | Decay_Engine Slow_Loop not alive within 2 s | Initialization error raised; `process()` blocked |
| `MemoryAugmentedOrchestrator.process` | Ecphory step raises exception | Log; omit echo; continue pipeline |
| `MemoryAugmentedOrchestrator.process` | Affective_Memory `store` raises exception | Log; return LLM response unchanged |

### Degraded State (Extended)

The Phase 2 `process()` path wraps both the echo step (4b) and the store step (9) in independent `try/except` blocks. Exceptions in either step are logged but do not set `_degraded = True`. Only an unhandled exception in the core pipeline steps (1–8) triggers the Degraded_State inherited from Phase 1. This ensures a malfunctioning memory system degrades gracefully without taking down the conversational pipeline.

---

## Testing Strategy

### Unit Tests

Unit tests use `pytest`. All Phase 2 unit tests run fully in-process with no GPU, no model file, and no real timing dependencies. Decay cadence is exercised with shortened intervals and mocked `time.monotonic()`.

**SDMCore:**
- `__init__` with `num_locations=99` raises `ValueError`
- `__init__` with `D=63` raises `ValueError`
- `_hard_locs` shape is `(num_locations, D)` at init
- `_accumulator` is all-zeros at init
- `write()` with wrong-dim address raises `ValueError`
- `write()` on full store raises `CapacityError`
- `delete()` with unknown ID raises `KeyError`
- `memory_usage_bytes()` returns sum of array `.nbytes`
- Fallback activation: address equidistant from all locations activates exactly one

**AffectiveMemory:**
- `store()` with wrong-dim `content_vector` raises `ValueError`
- `store()` with out-of-range PAD raises `ValueError`
- `store()` returns unique IDs for sequential calls
- `get_trace()` with unknown ID raises `KeyError`
- `get_all_traces()` on empty memory returns `[]`
- Eviction on overflow: store at capacity evicts the lowest-`decay_weight` trace

**DecayEngine:**
- Cadence < 60 raises `ValueError` at init
- `start()` + `is_alive()` returns `True`; `stop()` + `is_alive()` returns `False`
- Exception during `_apply_decay_tick` leaves index unchanged and loop resumes
- High-intensity trace loses less weight per tick than low-intensity trace
- Trace at exactly `viability_threshold` after decay is purged

**EcphoryEngine:**
- `resonance_threshold = 1.1` raises `ValueError`
- `ecphory_k = 0` raises `ValueError`
- `query()` with `PADState(0, 0, 0)` returns `None`
- `query()` with out-of-range PAD raises `ValueError`
- `query()` with no qualifying traces returns `None`
- `query()` result has shape `(M,)` and all values in `[-1.0, 1.0]`
- When 6 traces qualify and `ecphory_k=5`, only top-5 by resonance contribute

**PromptAssembler (Phase 2 extension):**
- `assemble()` with `echo_vector=None` produces no `[MEMORY ECHO]` section
- `assemble()` with a valid `echo_vector` includes `[MEMORY ECHO]` between somatic and reasoning sections
- Echo section format: each line matches `^echo_\d+: -?\d+\.\d{6}$`
- Echo section contains exactly `M` lines after the header
- Injected recall phrase in echo_vector encoding raises `AssemblyError` (not reachable in practice, but guard tested directly)

**Phase 2 Boundary_Layer patterns:**
- Each of the 8 new Phase 2 patterns triggers a Soft_Block
- Patterns are case-insensitive (e.g., `"I RECALL"` is blocked)

**MemoryAugmentedOrchestrator:**
- Missing `sdm_num_locations` raises `ValueError` at init
- `sdm_content_dim=32` with `m=64` raises `ValueError` at init
- Ecphory exception → prompt has no `[MEMORY ECHO]` section → response returned normally
- Affective_Memory store exception → response returned normally
- `shutdown()` joins Decay_Engine thread within 5 s

### Property-Based Tests

Property-based tests use [Hypothesis](https://hypothesis.readthedocs.io/) with `@settings(max_examples=200)` per property. Each test is tagged with a comment:

```python
# Feature: lucia-memory-phase2, Property {N}: {property_text}
```

| Property | Hypothesis Strategy |
|----------|---------------------|
| P19: SDM write/read approximate inverse | `arrays(float32, M, elements=floats(-1,1))` for content; derive address by thresholding; write to fresh SDM; read back; assert cosine_sim > 0 |
| P20: SDM read bounds | Arbitrary SDM state built by random writes; `arrays(uint8, D, elements=integers(0,1))` for address; assert read result in `[-1.0, 1.0]` |
| P21: SDM capacity enforcement | Sequences of write/delete ops via `stateful()` machine; assert no `CapacityError` below capacity, `CapacityError` at capacity |
| P22: Affective store/retrieve round trip | `arrays(float32, M, elements=floats(-1,1))` for content; `builds(PADState, floats(-1,1), floats(-1,1), floats(-1,1))` for pad; assert round-trip preserves `pad_tag` and `decay_weight=1.0` |
| P23: Decay monotonicity | `floats(0,1)` for initial weight, `floats(0,1)` for base_rate, arbitrary PAD_Tag, `floats(0,86400)` for elapsed; assert post-decay weight ≤ initial and in `[0.0, 1.0]` |
| P24: High-intensity traces decay slower | Two PAD_Tags constructed such that `intensity(a) > intensity(b)`; assert `decay_rate(a) < decay_rate(b)` |
| P25: Ecphory determinism | `lists(builds(MemoryTrace, ...))` + `builds(PADState, ...)`; call `query()` twice; assert equal outputs |
| P26: Echo vector bounds | Qualifying trace list via `lists(builds(MemoryTrace, ...), min_size=1)`; assert echo in `[-1.0, 1.0]` |
| P27: Ecphory top-K constraint | Build trace list with exactly `K+2` qualifying traces with distinct resonance scores; call `query()`; assert lowest-resonance two are absent from contribution |
| P28: No-recall language in echo section | `arrays(float32, M, elements=floats(-1,1))`; encode section; assert no forbidden phrase present |
| P29: Echo section present ↔ non-None echo vector | `one_of(none(), arrays(float32, M, elements=floats(-1,1)))` for echo; full `assemble()` call; assert `[MEMORY ECHO]` present iff echo is not `None` |
| P30: Timestamp independence | Fixed (pad, traces) pair; permute trace timestamps; assert `query()` outputs are equal |

### Integration Tests

Integration tests cover multi-module interactions and real threading:

- `MemoryAugmentedOrchestrator` startup confirms both Fast_Loop and Slow_Loop threads are alive within their respective deadlines
- End-to-end `process()` call (mocked LLM) stores a trace; second call with matching PAD injects echo into prompt
- Decay_Engine runs one shortened tick (cadence=60 s, mocked time); expired traces are purged from index and absent from subsequent `get_all_traces()`
- Concurrent stress test: 10 threads call `store()` and `get_all_traces()` simultaneously; assert `trace_count` stays consistent
- `shutdown()` cleanly joins both background threads
- Boundary_Layer Phase 2 patterns: `"I recall"` in LLM output is Soft_Blocked in end-to-end call

GPU/model integration tests (requiring actual LFM2.5-1.2B GGUF) are isolated in `tests/integration/` and skipped unless `LUCIA_MODEL_PATH` environment variable is set.

### Test File Layout

```
tests/
  unit/
    test_sdm_core.py
    test_affective_memory.py
    test_decay_engine.py
    test_ecphory_engine.py
    test_prompt_assembler_phase2.py
    test_boundary_layer_phase2.py
    test_memory_orchestrator.py
  integration/
    test_memory_orchestrator_integration.py
    test_llm_backend_integration.py     # skipped without model
  property/
    test_properties_phase2.py           # P19–P30 Hypothesis tests
```

### Hypothesis Configuration

```python
# tests/property/test_properties_phase2.py

from hypothesis import given, settings, HealthCheck
from hypothesis import strategies as st
import numpy as np

settings.register_profile(
    "phase2",
    max_examples=200,
    suppress_health_check=[HealthCheck.too_slow],
)
settings.load_profile("phase2")
```

Each property test carries the tagging comment convention from Phase 1:

```python
@given(content=st.arrays(np.float32, M, elements=st.floats(-1, 1, allow_nan=False)))
def test_p19_sdm_write_read_inverse(content):
    # Feature: lucia-memory-phase2, Property 19: SDM write/read approximate inverse
    sdm = SDMCore(SDMConfig(num_locations=200, address_dim=100, content_dim=len(content)))
    address = (content >= 0.0).astype(np.uint8)
    sdm.write(address, content)
    result = sdm.read(address)
    assert result.shape == content.shape
    assert np.all(result >= -1.0) and np.all(result <= 1.0)
    # Cosine similarity > 0 (recovered direction aligns with written content)
    norm_c, norm_r = np.linalg.norm(content), np.linalg.norm(result)
    if norm_c > 0 and norm_r > 0:
        assert np.dot(content, result) / (norm_c * norm_r) > 0.0
```
