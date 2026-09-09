# Implementation Plan: Lucia Memory Phase 2

## Overview

Extend the Phase 1 pipeline with five new modules: SDMCore (Kanerva's Sparse Distributed Memory), AffectiveMemory (PAD-tagged trace store), DecayEngine (slow-loop background decay), EcphoryEngine (resonance-based echo assembly), and MemoryAugmentedOrchestrator (Phase 1 subclass). PromptAssembler and BoundaryLayer receive backward-compatible extensions. All code is Python 3.12 with NumPy; no FAISS calls are needed for the SDM address-space path (pure NumPy XOR + sum). GPU/LLM tests remain isolated behind the `LUCIA_MODEL_PATH` env-var guard inherited from Phase 1.

Property-based tests use [Hypothesis](https://hypothesis.readthedocs.io/) with `@settings(max_examples=200)`. Tasks marked `*` are optional and can be skipped for a faster MVP iteration.

---

## Tasks

- [ ] 1. Memory module scaffolding — errors, configs, and shared data models
  - Add `CapacityError` to `src/core/errors.py` with a constructor that accepts `capacity: int` and `address_preview: str`; include both values in the message string
  - Create `src/core/memory/sdm.py` stub (imports, `SDMConfig` dataclass, `SDMCore` class skeleton)
  - Create `src/core/memory/affective_memory.py` stub (`AffectiveMemoryConfig`, `MemoryTrace` dataclass, `AffectiveMemory` class skeleton)
  - Create `src/core/memory/decay.py` stub (`DecayConfig` dataclass, `DecayEngine` class skeleton)
  - Create `src/core/memory/ecphory.py` stub (`EcphoryConfig` dataclass, `EcphoryEngine` class skeleton)
  - Confirm `tests/unit/`, `tests/property/`, and `tests/integration/` directories exist (they do from Phase 1); create `tests/unit/test_sdm_core.py`, `tests/unit/test_affective_memory.py`, `tests/unit/test_decay_engine.py`, `tests/unit/test_ecphory_engine.py`, `tests/unit/test_prompt_assembler_phase2.py`, `tests/unit/test_boundary_layer_phase2.py`, `tests/unit/test_memory_orchestrator.py` as empty stubs
  - Create `tests/property/test_properties_phase2.py` stub with Hypothesis profile registration:
    ```python
    from hypothesis import settings, HealthCheck
    settings.register_profile("phase2", max_examples=200, suppress_health_check=[HealthCheck.too_slow])
    settings.load_profile("phase2")
    ```
  - _Requirements: 1.5, 2.4, 2.5, 4.2, 4.4, 5.5, 5.6, 7.6, 7.7, 9.3, 9.8, 10.6, 13.1–13.8_

- [ ] 2. SDMCore — hard locations, distributed read/write, capacity management
  - [ ] 2.1 Implement `SDMCore.__init__()` in `src/core/memory/sdm.py`
    - Validate `SDMConfig`: raise `ValueError` for `num_locations < 100`, `address_dim < 64`, `content_dim < 8`, `hamming_radius_fraction` outside `(0.0, 1.0)` — identify the invalid field in the message
    - Allocate `_hard_locs` as `np.random.default_rng().integers(0, 2, (num_locations, D), dtype=np.uint8)`, `_accumulator` as `np.zeros((num_locations, M), dtype=np.float32)`, `_act_counts` as `np.zeros(num_locations, dtype=np.int64)`
    - Set `_hamming_radius = int(D * hamming_radius_fraction)`, initialize `_trace_addresses: dict[int, np.ndarray] = {}`, `_next_id: int = 0`
    - Expose `capacity` property (returns `config.capacity`), `trace_count` property (returns `len(_trace_addresses)`)
    - _Requirements: 1.1–1.6_
  - [ ] 2.2 Implement `SDMCore._hamming_distances()`, `_activate()`, `write()`, `read()`, `delete()`, `memory_usage_bytes()` in `src/core/memory/sdm.py`
    - `_hamming_distances(address)`: XOR `_hard_locs` against `address[np.newaxis, :]`, sum axis=1 — values are 0/1 uint8 so XOR sum = Hamming distance; no `np.unpackbits` required
    - `_activate(address)`: return `np.where(distances <= radius)[0]`; fallback to `np.array([np.argmin(distances)])` when mask is empty
    - `write(address, content)`: validate shapes; raise `CapacityError` when `trace_count >= capacity`; call `_activate`; accumulate content and increment counts; store `address.copy()` in `_trace_addresses`; return `trace_id`
    - `read(address)`: validate shape; activate; compute weighted mean of accumulator rows; return zero vector when all activation counts are zero; clip result to `[-1.0, 1.0]` as `float32`
    - `delete(trace_id)`: pop from `_trace_addresses`; raise `KeyError` for unknown ID (accumulator rows are intentionally NOT zeroed — see design)
    - `memory_usage_bytes()`: return `_hard_locs.nbytes + _accumulator.nbytes + _act_counts.nbytes`
    - _Requirements: 2.1–2.6, 3.1–3.5, 4.1–4.5, 15.1–15.3_
  - [ ]* 2.3 Write unit tests for `SDMCore` in `tests/unit/test_sdm_core.py`
    - `SDMConfig(num_locations=99)` raises `ValueError`; `SDMConfig(address_dim=63)` raises `ValueError`; `SDMConfig(content_dim=7)` raises `ValueError`
    - `_hard_locs.shape == (num_locations, D)` and `_accumulator` all-zeros at init
    - `write()` with `address.shape != (D,)` raises `ValueError`; `write()` with `content.shape != (M,)` raises `ValueError`
    - `write()` on a store already at capacity raises `CapacityError`
    - `delete()` with unknown `trace_id` raises `KeyError`
    - `trace_count` increments on write, decrements on delete
    - `memory_usage_bytes()` returns `_hard_locs.nbytes + _accumulator.nbytes + _act_counts.nbytes`
    - Fallback activation: construct address maximally distant from all hard locations; verify `_activate()` returns exactly one index
    - _Requirements: 1.1–1.6, 2.4, 2.5, 4.1–4.4_
  - [ ]* 2.4 Write property tests P19–P21 for `SDMCore` in `tests/property/test_properties_phase2.py`
    - **Property 19: SDM Write/Read Approximate Inverse** — `arrays(np.float32, M, elements=floats(-1, 1, allow_nan=False))` for content; derive address by thresholding at 0; write to fresh `SDMCore`; read back; assert shape `(M,)`, values in `[-1.0, 1.0]`, cosine_sim > 0 when both norms > 0
    - **Property 20: SDM Read Bounds Invariant** — arbitrary SDM state built by ≥1 random writes; `arrays(np.uint8, D, elements=integers(0, 1))` for address; assert `read()` result shape `(M,)` and all values in `[-1.0, 1.0]`
    - **Property 21: SDM Capacity Enforcement** — stateful `RuleBasedStateMachine` alternating writes and deletes; assert no `CapacityError` while `trace_count < capacity`; assert `CapacityError` raised on write when `trace_count == capacity`
    - _Requirements: 2.1, 2.2, 3.1, 3.2, 3.4, 4.2, 4.5_

- [ ] 3. AffectiveMemory — trace encoding, storage, and retrieval
  - [ ] 3.1 Implement `AffectiveMemory` in `src/core/memory/affective_memory.py`
    - `__init__(config: AffectiveMemoryConfig)`: instantiate `SDMCore` from `config.sdm_config`; set `self._M = config.m`; initialize `self._index: dict[int, MemoryTrace] = {}`; initialize `self._index_lock = threading.RLock()`
    - `store(content_vector, pad_state) -> int`: validate `content_vector.shape == (M,)`; validate all PAD dims in `[-1.0, 1.0]`; acquire `_index_lock`; evict lowest `decay_weight` trace when at capacity (call `delete_trace`); derive binary address by `(content_vector >= 0.0).astype(np.uint8)`; call `_sdm.write`; build and index `MemoryTrace(trace_id, address_vec, content_vec copy, pad_state copy, time.monotonic(), 1.0)`; return `trace_id`
    - `get_all_traces() -> list[MemoryTrace]`: acquire lock; return `list(self._index.values())`
    - `get_trace(trace_id) -> MemoryTrace`: return from `_index`; raise `KeyError` for unknown ID
    - `delete_trace(trace_id)`: caller MUST hold `_index_lock`; call `_sdm.delete(trace_id)`; pop from `_index`
    - `index_memory_usage_bytes() -> int`: return `sum(sys.getsizeof(t) for t in self._index.values())`
    - _Requirements: 5.1–5.8, 6.1–6.5, 15.4, 15.5_
  - [ ]* 3.2 Write unit tests for `AffectiveMemory` in `tests/unit/test_affective_memory.py`
    - `store()` with wrong-dim `content_vector` raises `ValueError`
    - `store()` with out-of-range PAD dimension raises `ValueError`
    - `store()` returns unique monotonically increasing IDs for sequential calls
    - `get_trace()` returns trace whose `pad_tag`, `decay_weight=1.0`, and `trace_id` match the stored values
    - `get_trace()` with unknown ID raises `KeyError`
    - `get_all_traces()` on empty memory returns `[]`
    - Eviction on overflow: fill to capacity, artificially lower one trace's `decay_weight`, call `store()` again; assert evicted trace is the lowest-weight one and `trace_count == capacity`
    - _Requirements: 5.1–5.6, 6.1–6.5_
  - [ ]* 3.3 Write property test P22 for `AffectiveMemory` in `tests/property/test_properties_phase2.py`
    - **Property 22: Affective Memory Store/Retrieve Round Trip** — `arrays(np.float32, M, elements=floats(-1, 1, allow_nan=False))` for content; `builds(PADState, floats(-1, 1), floats(-1, 1), floats(-1, 1))` for pad; call `store()`; assert `get_trace(id).pad_tag == pad`, `get_trace(id).decay_weight == 1.0`, `get_trace(id).trace_id == id`
    - _Requirements: 5.1, 5.2, 5.3_

- [ ] 4. Checkpoint — memory storage layer
  - Ensure all tests in `tests/unit/test_sdm_core.py` and `tests/unit/test_affective_memory.py` pass. Run `pytest tests/unit/test_sdm_core.py tests/unit/test_affective_memory.py tests/property/test_properties_phase2.py -k "p19 or p20 or p21 or p22" --tb=short`. Ask the user if any questions arise.

- [ ] 5. DecayEngine — time-based trace weakening and slow loop lifecycle
  - [ ] 5.1 Implement `DecayEngine` in `src/core/memory/decay.py`
    - `__init__(memory: AffectiveMemory, config: DecayConfig)`: validate `loop_cadence_seconds >= 60` (raise `ValueError` with cadence and minimum); validate `base_decay_rate` in `(0.0, 1.0)` and `viability_threshold` in `(0.0, 1.0)`; store refs; initialize `_stop_event = threading.Event()`, `_thread: threading.Thread | None = None`
    - `_emotional_intensity(pad_tag) -> float`: `clip(|arousal| × (|pleasure| + 0.1), 0.0, 1.0)`
    - `_decay_rate(pad_tag) -> float`: `base_decay_rate × (1.0 - emotional_intensity)`
    - `_apply_decay_tick(elapsed_seconds)`: acquire `memory._index_lock`; iterate index; compute new weight per trace; clamp to `[0.0, 1.0]`; collect traces at or below `viability_threshold`; call `memory.delete_trace()` for each — all within single lock acquisition; log purge count
    - `_slow_loop_worker()`: interruptible sleep via `_stop_event.wait(timeout=cadence)`; track elapsed with `time.monotonic()`; call `_apply_decay_tick`; on any exception log full stack trace and continue loop without terminating
    - `start()`: clear stop event; launch daemon thread named `"DecayEngine-SlowLoop"`; poll `is_alive()` with 50 ms intervals up to 2 s; raise `RuntimeError` if thread not alive in time
    - `stop()`: set stop event; join thread with `timeout=5.0`; set `_thread = None`
    - `is_alive() -> bool`: return `self._thread is not None and self._thread.is_alive()`
    - _Requirements: 7.1–7.9, 8.1–8.6_
  - [ ]* 5.2 Write unit tests for `DecayEngine` in `tests/unit/test_decay_engine.py`
    - `DecayConfig(loop_cadence_seconds=59)` raises `ValueError` at init
    - `start()` → `is_alive()` returns `True`; `stop()` → `is_alive()` returns `False`
    - Exception during `_apply_decay_tick` leaves index unchanged and loop continues (mock tick to raise once, verify thread stays alive and subsequent tick runs)
    - A trace with high emotional intensity loses strictly less `decay_weight` per tick than a trace with low intensity, given the same `base_decay_rate` and `elapsed_seconds`
    - A trace whose weight falls to exactly `viability_threshold` after decay is purged from the index
    - _Requirements: 7.1–7.9, 8.1–8.5_
  - [ ]* 5.3 Write property tests P23–P24 for `DecayEngine` in `tests/property/test_properties_phase2.py`
    - **Property 23: Decay Monotonicity** — `floats(0, 1)` for initial weight, `floats(min_value=1e-6, max_value=0.9999)` for base_rate, `builds(PADState, ...)`, `floats(0, 86400)` for elapsed; compute `_decay_rate()` and new weight; assert `new_weight <= initial_weight` and `new_weight in [0.0, 1.0]`
    - **Property 24: High-Intensity Traces Decay Slower** — construct two PAD_Tags `a`, `b` such that `emotional_intensity(a) > emotional_intensity(b)` via strategy; same `base_decay_rate` and `elapsed`; assert `decay_rate(a) < decay_rate(b)` (strictly less — not just ≤)
    - _Requirements: 7.1, 7.2_

- [ ] 6. EcphoryEngine — resonance scoring and echo vector assembly
  - [ ] 6.1 Implement `EcphoryEngine` in `src/core/memory/ecphory.py`
    - `__init__(config: EcphoryConfig)`: validate `resonance_threshold` in `[0.0, 1.0]` (raise `ValueError`); validate `ecphory_k` in `[1, 50]` (raise `ValueError`)
    - `_resonance_score(pad_state, pad_tag) -> float`: build 3D float64 arrays; return 0.0 when either norm is 0; otherwise return `dot(a, b) / (norm_a × norm_b)`
    - `query(pad_state, traces) -> np.ndarray | None`: validate all PAD dims in `[-1.0, 1.0]`; return `None` when PAD magnitude is 0; filter traces by `decay_weight > viability_threshold` AND `resonance_score > resonance_threshold`; return `None` when no traces qualify; sort by descending resonance score; take top `ecphory_k`; compute weighted mean `weights = resonance_score × decay_weight`; clip result to `[-1.0, 1.0]`; return `float32` ndarray of shape `(M,)` — or `None` if `weight_sum == 0`
    - _Requirements: 9.1–9.9, 10.1–10.7, 16.2_
  - [ ]* 6.2 Write unit tests for `EcphoryEngine` in `tests/unit/test_ecphory_engine.py`
    - `EcphoryConfig(resonance_threshold=1.1)` raises `ValueError`
    - `EcphoryConfig(ecphory_k=0)` raises `ValueError`
    - `query()` with `PADState(0, 0, 0)` returns `None`
    - `query()` with any PAD dim outside `[-1.0, 1.0]` raises `ValueError`
    - `query()` with an empty trace list returns `None`
    - `query()` with all traces below `viability_threshold` returns `None`
    - `query()` with qualifying traces returns array of correct shape `(M,)` with all values in `[-1.0, 1.0]`
    - When 6 traces qualify and `ecphory_k=5`: the 6th-ranked trace (by resonance) does NOT influence the echo vector — verify by building a known trace set with controlled scores and checking the weighted mean manually
    - _Requirements: 9.1–9.9, 10.1–10.7_
  - [ ]* 6.3 Write property tests P25–P27 and P30 for `EcphoryEngine` in `tests/property/test_properties_phase2.py`
    - **Property 25: Ecphory Determinism** — `lists(builds(MemoryTrace, ...))` + `builds(PADState, ...)`; call `query()` twice with identical inputs; assert outputs are element-wise equal or both `None`
    - **Property 26: Echo Vector Bounds Invariant** — construct at least one qualifying trace (above both thresholds); call `query()`; assert result shape `(M,)` and all values in `[-1.0, 1.0]`
    - **Property 27: Ecphory Top-K Constraint** — build trace list with exactly `K+2` qualifying traces with distinct resonance scores; call `query()`; reconstruct the expected echo using only top-K; assert element-wise equality with actual output
    - **Property 30: No-Timeline Invariant — Ecphory Timestamp Independence** — fixed `(pad_state, traces)` pair; permute `timestamp` fields only; assert `query()` outputs are element-wise equal
    - _Requirements: 9.7, 9.9, 10.7, 16.2, 16.4_

- [ ] 7. Checkpoint — retrieval pipeline
  - Ensure all tests for tasks 5–6 pass. Run `pytest tests/unit/test_decay_engine.py tests/unit/test_ecphory_engine.py tests/property/test_properties_phase2.py -k "p23 or p24 or p25 or p26 or p27 or p30" --tb=short`. Ask the user if any questions arise.

- [ ] 8. PromptAssembler Phase 2 extension — echo vector integration
  - [ ] 8.1 Extend `PromptAssembler.assemble()` in `src/core/orchestrator/prompt_assembler.py`
    - Add `echo_vector: np.ndarray | None = None` as a keyword-only parameter (default `None` preserves full backward compatibility with all Phase 1 call sites)
    - Implement `_encode_echo_section(echo_vector: np.ndarray) -> str`: build `[MEMORY ECHO]` header + lines in format `echo_{i}: {float(val):.6f}`; scan the encoded section string for each forbidden phrase (`"I remember"`, `"I recall"`, `"last time"`, `"you mentioned"`, `"you said"`, `"I know from before"`, `"previously you"`, `"my memory"`) case-insensitively; raise `AssemblyError` identifying the offending phrase if any is found
    - Insert the echo section between `[SOMATIC STATE]` and `[REASONING]` (or between `[SOMATIC STATE]` and `[CONVERSATION]` when `reasoning_depth == 0`) when `echo_vector is not None`; omit the section entirely when `echo_vector is None`
    - _Requirements: 11.2, 11.3, 11.4, 12.1, 12.5, 16.3_
  - [ ]* 8.2 Write unit tests for `PromptAssembler` Phase 2 extension in `tests/unit/test_prompt_assembler_phase2.py`
    - `assemble()` with `echo_vector=None` produces no `[MEMORY ECHO]` header and no `echo_` keys anywhere in the output
    - `assemble()` with a valid 64-dim `echo_vector` includes `[MEMORY ECHO]` section positioned between `[SOMATIC STATE]` and `[REASONING]` (or `[CONVERSATION]` if reasoning_depth=0)
    - Each echo line matches the regex `^echo_\d+: -?\d+\.\d{6}$`
    - Echo section contains exactly `M=64` lines after the `[MEMORY ECHO]` header
    - A manually constructed `echo_vector` that would encode `"I remember"` is rejected with `AssemblyError` — test `_encode_echo_section()` directly with an injected string to verify the guard (not reachable via numeric arrays in practice, but the guard must be exercised)
    - Phase 1 call sites (no `echo_vector` argument) produce identical output to before the extension
    - _Requirements: 11.2–11.4, 12.1, 12.5_
  - [ ]* 8.3 Write property tests P28–P29 for `PromptAssembler` in `tests/property/test_properties_phase2.py`
    - **Property 28: No-Recall Language in Echo Section** — `arrays(np.float32, 64, elements=floats(-1, 1, allow_nan=False))` as echo vector; call `_encode_echo_section()`; assert none of the 8 forbidden phrases appear in the output (case-insensitive)
    - **Property 29: Echo Section Present ↔ Non-None Echo Vector** — `one_of(none(), arrays(np.float32, 64, elements=floats(-1, 1, allow_nan=False)))` for echo; full `assemble()` call with valid somatic/constraints; assert `"[MEMORY ECHO]"` present iff `echo is not None`; assert no `echo_` keys present when `echo is None`
    - _Requirements: 11.2, 11.4, 12.1, 12.3, 12.5_

- [ ] 9. BoundaryLayer Phase 2 pattern extension
  - [ ] 9.1 Extend `BoundaryLayer` in `src/core/safety/boundary_layer.py` with Phase 2 recall patterns
    - Add 8 new default patterns to the compiled pattern set: `\bI remember\b`, `\bI recall\b`, `\blast time\b`, `\byou mentioned\b`, `\byou said\b`, `\bI know from before\b`, `\bpreviously you\b`, `\bmy memory\b`
    - Patterns are case-insensitive (use `re.IGNORECASE` as already applied to all patterns)
    - Each match triggers a Soft_Block (replace span with `"[...]"`, log `SoftBlockEvent`) following the same mechanism as Phase 1 patterns
    - _Requirements: 12.2, 12.3_
  - [ ]* 9.2 Write unit tests for the Phase 2 patterns in `tests/unit/test_boundary_layer_phase2.py`
    - Each of the 8 new patterns triggers a Soft_Block and the matched text is absent from the output
    - Patterns are case-insensitive: `"I RECALL"` and `"i recall"` and `"I Recall"` all trigger a block
    - A clean response with no recall language passes through `validate()` unmodified
    - _Requirements: 12.2, 12.3_

- [ ] 10. MemoryAugmentedOrchestrator — subclass wiring and 9-step pipeline
  - [ ] 10.1 Implement `MemoryAugmentedOrchestrator.__init__()` in `src/core/orchestrator/orchestrator.py`
    - Define `MemoryOrchestratorConfig` as a flat dataclass extending all Phase 1 `OrchestratorConfig` fields with the 10 Phase 2 fields: `sdm_num_locations`, `sdm_address_dim`, `sdm_content_dim`, `sdm_hamming_radius_fraction`, `sdm_capacity`, `decay_base_rate`, `decay_viability_threshold`, `decay_loop_cadence_seconds`, `ecphory_k`, `ecphory_resonance_threshold`
    - Implement `_validate_phase2_config(config)`: raise `ValueError` for any Phase 2 field outside its documented range (identifying the field and range); raise `ValueError` when `sdm_content_dim != m` in `AffectiveMemoryConfig`
    - Subclass `Orchestrator`; call `super().__init__(config)` to start Fast_Loop; instantiate `SDMCore`, `AffectiveMemory`, `DecayEngine`, `EcphoryEngine` from config; call `_decay_engine.start()`; log trace count and sdm capacity on startup
    - _Requirements: 13.1–13.8, 14.1, 14.2, 14.5_
  - [ ] 10.2 Implement `MemoryAugmentedOrchestrator.process()` in `src/core/orchestrator/orchestrator.py`
    - Override `process(input_text)`: inherit input and degraded-state guards from Phase 1 (via `super()` or direct reimplementation)
    - Execute steps 1–4 identically to Phase 1 (stimulus encode, emotion push, PAD + somatic markers, behavioral constraints)
    - Step 4b (memory echo): call `_affective_memory.get_all_traces()`; call `_ecphory_engine.query(pad, traces)`; wrap the entire step in `try/except` — on exception log and set `echo_vec = None`; record `echo_top_resonance` for the log
    - Step 5: call `_prompt_assembler.assemble(..., echo_vector=echo_vec)` — passing the optional echo through
    - Steps 6–8: identical to Phase 1 (latency delay, LLM generate, boundary validate)
    - Step 9 (memory store): `try/except` wrapper; pad/truncate stimulus to `M` dims; clip to `[-1.0, 1.0]`; call `_affective_memory.store(content, pad)` — exception logs and continues; response already returned
    - Log `call_id`, total time, `echo_elapsed`, `echo_top_resonance`, somatic markers, constraints
    - Append `("user", input_text)` and `("assistant", safe_response)` to `_history`
    - _Requirements: 11.1–11.8, 14.4_
  - [ ] 10.3 Implement `MemoryAugmentedOrchestrator.shutdown()` in `src/core/orchestrator/orchestrator.py`
    - Call `_decay_engine.stop()` (joins Slow_Loop with 5 s timeout)
    - Call `super().shutdown()` (stops Fast_Loop, releases LLM_Backend)
    - _Requirements: 14.3_
  - [ ]* 10.4 Write unit tests for `MemoryAugmentedOrchestrator` in `tests/unit/test_memory_orchestrator.py`
    - `MemoryOrchestratorConfig` with missing Phase 2 field raises `ValueError` at init
    - `sdm_content_dim=32` when `m=64` raises `ValueError` at init
    - Ecphory exception in step 4b → prompt has no `[MEMORY ECHO]` section → response is returned normally (mock LLM)
    - `AffectiveMemory.store()` exception in step 9 → LLM response is still returned to caller (mock LLM)
    - `shutdown()` joins `DecayEngine` thread within 5 s and `is_alive()` returns `False` afterward
    - After a successful `process()` call: `trace_count == 1` (one trace stored in memory index)
    - _Requirements: 11.1, 11.5–11.7, 13.6, 13.7, 13.8, 14.1–14.3_

- [ ] 11. Checkpoint — full Phase 2 pipeline dry run
  - Run `pytest tests/unit tests/property --tb=short` (all unit + property tests, LLM mocked). Verify all non-skipped tests pass. Ask the user if any questions arise.

- [ ] 12. Integration tests
  - [ ] 12.1 Write integration tests in `tests/integration/test_memory_orchestrator_integration.py`
    - `MemoryAugmentedOrchestrator` startup: both `EmotionCore` Fast_Loop and `DecayEngine` Slow_Loop threads are alive within their respective deadlines (mocked LLM)
    - End-to-end `process()` call (mocked LLM) → one trace stored; second `process()` call with matching PAD state → `[MEMORY ECHO]` section present in the prompt received by the mocked LLM
    - `DecayEngine` runs one shortened tick (cadence=60 s, patched `time.monotonic()` to simulate elapsed time); traces below `viability_threshold` are purged from `get_all_traces()`
    - Concurrent stress test: 10 threads simultaneously call `store()` and `get_all_traces()` on a shared `AffectiveMemory` instance; after all threads complete, assert `trace_count` equals the number of successful stores (no data corruption)
    - `shutdown()` cleanly joins both background threads; `DecayEngine.is_alive()` returns `False`
    - `BoundaryLayer` Phase 2 pattern: mocked LLM returning `"I recall everything"` → response contains `"[...]"` (Soft_Block applied)
    - _Requirements: 11.1–11.8, 12.2, 12.3, 14.1–14.4_
  - [ ] 12.2 Add GPU/model integration test stubs in `tests/integration/test_llm_backend_integration.py`
    - Extend existing file with a Phase 2 smoke test: if `LUCIA_MODEL_PATH` is set, `MemoryAugmentedOrchestrator` initializes, calls `process()` once with a real LLM, and stores one trace
    - Skipped when `LUCIA_MODEL_PATH` is not set
    - _Requirements: 14.1, 14.5_

- [ ] 13. Final checkpoint — all tests green
  - Run `pytest tests/unit tests/property tests/integration --tb=short` (GPU/model tests skip automatically without `LUCIA_MODEL_PATH`). Ensure all non-skipped tests pass. Ask the user if any questions arise.

---

## Notes

- Tasks marked with `*` are optional and can be skipped for a faster MVP iteration.
- Each task references specific requirements from `requirements.md` for full traceability.
- All Hypothesis property tests go in `tests/property/test_properties_phase2.py` with the `@settings(max_examples=200)` decorator and the tagging comment `# Feature: lucia-memory-phase2, Property N: <property_text>`.
- `CapacityError` is added to the existing `src/core/errors.py` — do NOT create a separate `src/core/memory/errors.py`.
- `MemoryAugmentedOrchestrator` and `MemoryOrchestratorConfig` are defined in the existing `src/core/orchestrator/orchestrator.py` file alongside the Phase 1 `Orchestrator` class — do NOT create a separate file.
- `PromptAssembler.assemble()` must remain backward compatible — the new `echo_vector` parameter is keyword-only with default `None`. All Phase 1 callers continue to work without modification.
- `AffectiveMemory._index_lock` is a `threading.RLock` (reentrant), allowing `DecayEngine` to call `delete_trace()` while already holding the lock without deadlocking.
- `SDMCore.delete()` intentionally does NOT zero accumulator rows — the design documents this as a deliberate tradeoff. Do not add zeroing logic.
- LLM_Backend must always be mocked in unit and property tests. Real GPU/model tests live exclusively in `tests/integration/test_llm_backend_integration.py` behind the `LUCIA_MODEL_PATH` env-var skip guard.
- The `MemoryTrace` dataclass is NOT frozen — `DecayEngine` mutates `decay_weight` in place under the index lock. Do not add `frozen=True`.
- For property test P21 (SDM capacity enforcement), use Hypothesis `RuleBasedStateMachine` from `hypothesis.stateful`.

## Task Dependency Graph

```json
{
  "waves": [
    { "id": 0, "tasks": ["1"] },
    { "id": 1, "tasks": ["2.1"] },
    { "id": 2, "tasks": ["2.2"] },
    { "id": 3, "tasks": ["2.3", "2.4", "3.1"] },
    { "id": 4, "tasks": ["3.2", "3.3", "5.1"] },
    { "id": 5, "tasks": ["5.2", "5.3", "6.1"] },
    { "id": 6, "tasks": ["6.2", "6.3", "8.1"] },
    { "id": 7, "tasks": ["8.2", "8.3", "9.1"] },
    { "id": 8, "tasks": ["9.2", "10.1"] },
    { "id": 9, "tasks": ["10.2", "10.3"] },
    { "id": 10, "tasks": ["10.4", "12.1", "12.2"] }
  ]
}
```
