# Requirements Document

## Introduction

This document defines the requirements for **Lucia Memory Phase 2**: the emotion-cued memory system that extends the Phase 1 pipeline with biologically-inspired, affect-driven recall. Phase 2 covers five cooperating components:

1. **SDM_Core** — Kanerva's Sparse Distributed Memory, backed by FAISS. Stores and retrieves distributed binary traces against a fixed-capacity hard-location address space using Hamming distance thresholding.
2. **Affective_Memory** — A wrapper around SDM_Core that co-encodes each stored trace with a PAD vector tag representing the emotional state at the moment of encoding.
3. **Decay_Engine** — A slow-loop background process that weakens memory traces over time at a rate inversely proportional to emotional intensity, and purges traces that fall below a viability threshold.
4. **Ecphory_Engine** — Given the current PAD state, computes cosine similarity between the active PAD vector and all stored affective tags, and returns the top-K resonant traces as echo vectors.
5. **Memory-Augmented_Orchestrator** — Extends the Phase 1 Orchestrator pipeline with a memory echo step that injects reawakened echo vectors into the Conditioned_Prompt as unlabeled contextual influence.

The guiding constraint is that memory must **never** surface as explicit recall. Reawakened traces influence generation through behavioral texture — tone, fragment density, associative content — never through first-person retrieval language. No identity timeline is formed; each trace decays independently with no narrative linking.

---

## Glossary

- **SDM_Core**: The Sparse Distributed Memory implementation. Maintains a fixed set of hard locations in binary address space and implements distributed read/write via Hamming distance activation. Maps to `src/core/memory/sdm.py`.
- **Affective_Memory**: The module that wraps SDM_Core to store and retrieve memory traces with PAD affective tags. Maps to `src/core/memory/affective_memory.py`.
- **Decay_Engine**: The background slow-loop module that applies time-based decay to all stored memory traces and removes traces that fall below the viability threshold. Maps to `src/core/memory/decay.py`.
- **Ecphory_Engine**: The module that computes PAD-space resonance between the current emotional state and stored affective tags, returning reawakened echo vectors. Maps to `src/core/memory/ecphory.py`.
- **Memory_Augmented_Orchestrator**: The extended Orchestrator that incorporates the memory echo step between behavioral constraint derivation and prompt assembly. Maps to `src/core/orchestrator/orchestrator.py` (extension of Phase 1).
- **Hard_Location**: A randomly initialized binary vector of fixed dimensionality `D` bits. Hard locations are fixed at initialization and serve as the address landmarks of the SDM address space.
- **Address_Vector**: A binary vector of dimensionality `D` used to identify and activate a subset of Hard_Locations via Hamming distance thresholding.
- **Content_Vector**: A real-valued vector of dimensionality `M` representing the semantic and contextual content of a memory trace, derived from the Stimulus_Vector and conversation context at the moment of encoding. All values are bounded to `[-1.0, 1.0]`.
- **PAD_Tag**: A frozen three-dimensional vector `(pleasure, arousal, dominance)` copied from the PAD_State at the moment a memory trace is written. All dimensions are bounded to `[-1.0, 1.0]`. The PAD_Tag is stored alongside the Content_Vector as part of the Memory_Trace.
- **Memory_Trace**: A single stored memory record consisting of: `(address_vector: binary ndarray, content_vector: float ndarray, pad_tag: PADState, timestamp: float, decay_weight: float)`. The `decay_weight` is initialized to `1.0` and decreases over time.
- **Emotional_Intensity**: A scalar computed from a PAD_Tag as `clip(|arousal| × (|pleasure| + 0.1), 0.0, 1.0)`. High emotional intensity corresponds to slow decay; low emotional intensity corresponds to fast decay.
- **Decay_Rate**: The per-second rate at which a trace's `decay_weight` decreases, computed as `base_decay_rate × (1.0 - Emotional_Intensity)`. `base_decay_rate` is a configurable parameter with default `0.0001` per second, giving a minimum-intensity trace a half-life of approximately 1.9 hours.
- **Viability_Threshold**: The `decay_weight` floor below which a Memory_Trace is removed from the SDM_Core during the next Decay_Engine pass. Default value: `0.05`.
- **Hamming_Radius**: The maximum Hamming distance between an Address_Vector and a Hard_Location at which the Hard_Location is considered activated. Default value: `D * 0.451`, where `D` is the address dimensionality.
- **Echo_Vector**: A weighted-sum real-valued vector of dimensionality `M` produced by the Ecphory_Engine, representing the blended Content_Vector content of the top-K resonant Memory_Traces. All values are bounded to `[-1.0, 1.0]`.
- **Resonance_Score**: The cosine similarity between the current PAD_State vector (as a 3D real vector) and a stored PAD_Tag vector, in the range `[-1.0, 1.0]`. Only traces with Resonance_Score above a configurable threshold are candidates for reawakening.
- **Echo_Section**: The optional section appended to the Conditioned_Prompt by the Memory_Augmented_Orchestrator when at least one resonant trace exists. It contains the Echo_Vector encoded as numeric values with no natural-language recall framing.
- **Slow_Loop**: The background thread managed by the Decay_Engine, operating at a configurable cadence (default 3600 seconds) to apply decay updates to all stored Memory_Traces.
- **SDM_Capacity**: The maximum number of Memory_Traces simultaneously held in SDM_Core. Default: 10,000 traces.
- **Ecphory_K**: The maximum number of resonant Memory_Traces returned by the Ecphory_Engine per query. Default: 5.
- **Resonance_Threshold**: The minimum Resonance_Score a trace must exceed to be eligible for reawakening. Default: `0.6`.
- **PAD_State**: Inherited from Phase 1. A three-dimensional vector `(pleasure, arousal, dominance)` with all values in `[-1.0, 1.0]`.
- **Conditioned_Prompt**: Inherited from Phase 1. The assembled prompt string passed to the LLM_Backend.
- **Orchestrator**: Inherited from Phase 1. The central pipeline coordinator, extended in Phase 2 with the memory echo step.

---

## Requirements

### Requirement 1: SDM Core — Hard Location Address Space

**User Story:** As the Affective_Memory module, I want SDM_Core to maintain a fixed set of randomly initialized binary hard locations, so that I can store and retrieve memory traces by distributed similarity rather than by exact address.

#### Acceptance Criteria

1. THE SDM_Core SHALL initialize a fixed set of `num_locations` Hard_Locations, each a randomly generated binary vector of dimensionality `D` bits, stored as a 2D boolean array of shape `(num_locations, D)`.
2. WHEN initialized, THE SDM_Core SHALL set `num_locations` to a configurable value with a default of 1,000 and SHALL set `D` to a configurable value with a default of 1,000 bits.
3. THE SDM_Core SHALL initialize a corresponding content accumulator matrix of shape `(num_locations, M)` with all values set to zero, where `M` is the configurable content vector dimensionality with a default of 64.
4. THE SDM_Core SHALL initialize a corresponding activation count vector of length `num_locations` with all values set to zero, tracking the total number of write activations received by each Hard_Location.
5. IF `num_locations` is less than 100, or `D` is less than 64, or `M` is less than 8, THEN THE SDM_Core SHALL raise a `ValueError` at initialization identifying the invalid parameter before any Hard_Locations are generated.
6. THE SDM_Core SHALL expose a `capacity` property returning the integer value of `SDM_Capacity` as configured at initialization.

---

### Requirement 2: SDM Core — Distributed Write

**User Story:** As the Affective_Memory module, I want to write a Content_Vector to all Hard_Locations activated by a given Address_Vector, so that the stored information is distributed across the address space in a noise-resistant manner.

#### Acceptance Criteria

1. WHEN an Address_Vector and a Content_Vector are provided to the write operation, THE SDM_Core SHALL compute the Hamming distance between the Address_Vector and every Hard_Location and activate all Hard_Locations whose Hamming distance is at or below the Hamming_Radius.
2. WHEN at least one Hard_Location is activated by a write operation, THE SDM_Core SHALL add the Content_Vector to the content accumulator row of each activated Hard_Location and increment the activation count of each activated Hard_Location by 1.
3. IF no Hard_Location is activated by a write operation because the Address_Vector is beyond Hamming_Radius of all Hard_Locations, THEN THE SDM_Core SHALL activate the single Hard_Location with the minimum Hamming distance from the Address_Vector as a fallback, ensuring the write is never silently dropped.
4. IF the provided Address_Vector has a dimensionality different from `D`, THEN THE SDM_Core SHALL raise a `ValueError` identifying the actual and expected dimensionalities.
5. IF the provided Content_Vector has a dimensionality different from `M`, THEN THE SDM_Core SHALL raise a `ValueError` identifying the actual and expected dimensionalities.
6. THE SDM_Core SHALL complete a single write operation against a store of up to 10,000 Hard_Locations within 50 milliseconds on the target CPU hardware.

---

### Requirement 3: SDM Core — Distributed Read

**User Story:** As the Affective_Memory module, I want to read a Content_Vector by providing an Address_Vector, so that I can reconstruct a distributed memory trace from the overlapping activations of nearby hard locations.

#### Acceptance Criteria

1. WHEN an Address_Vector is provided to the read operation, THE SDM_Core SHALL activate all Hard_Locations within Hamming_Radius of the Address_Vector using the same activation criterion as the write operation, including the fallback rule for empty activations.
2. WHEN at least one Hard_Location is activated by a read operation, THE SDM_Core SHALL compute the read result by dividing the sum of all activated content accumulator rows by the sum of their corresponding activation counts, producing a real-valued vector of dimensionality `M`.
3. IF all activated Hard_Locations have an activation count of zero, THEN THE SDM_Core SHALL return a zero vector of dimensionality `M` without raising an exception.
4. THE SDM_Core SHALL clip the read result vector to `[-1.0, 1.0]` before returning it.
5. THE SDM_Core SHALL complete a single read operation against a store of up to 10,000 Hard_Locations within 50 milliseconds on the target CPU hardware.

---

### Requirement 4: SDM Core — Capacity Management

**User Story:** As the Affective_Memory module, I want the SDM_Core to track its occupancy and signal when the store is full, so that the Affective_Memory module can enforce SDM_Capacity limits and trigger eviction before a write is attempted.

#### Acceptance Criteria

1. THE SDM_Core SHALL expose a `trace_count` property returning the current number of distinct Memory_Traces indexed in the store.
2. WHEN `trace_count` reaches `SDM_Capacity`, THE SDM_Core SHALL raise a `CapacityError` on any subsequent write attempt, containing the current capacity and the attempted write address.
3. THE SDM_Core SHALL expose a `delete(trace_id: int)` method that removes a specific Memory_Trace's address-to-accumulator mapping from the store, decrementing `trace_count` by 1.
4. IF `delete` is called with a `trace_id` that does not exist in the store, THEN THE SDM_Core SHALL raise a `KeyError` identifying the unknown trace ID.
5. FOR ALL sequences of write and delete operations that keep `trace_count` below `SDM_Capacity`, THE SDM_Core SHALL accept each write without raising a `CapacityError`.

---

### Requirement 5: Affective Memory — Trace Encoding and Storage

**User Story:** As the Ecphory_Engine and Decay_Engine, I want the Affective_Memory module to encode and store memory traces that pair semantic content with the emotional state at the moment of encoding, so that traces can later be reawakened by emotional resonance rather than semantic lookup.

#### Acceptance Criteria

1. THE Affective_Memory SHALL accept a `store(content_vector: np.ndarray, pad_state: PADState) -> int` call and return a unique integer `trace_id` for every successfully stored trace.
2. WHEN `store` is called, THE Affective_Memory SHALL write the `content_vector` to SDM_Core using a binary Address_Vector derived from the `content_vector` by thresholding each dimension at zero, store the PAD_Tag as a copy of the provided `pad_state`, set `timestamp` to `time.monotonic()`, and initialize `decay_weight` to `1.0`.
3. THE Affective_Memory SHALL maintain an in-process index mapping each `trace_id` to its corresponding `Memory_Trace` record for use by the Decay_Engine and Ecphory_Engine.
4. IF `store` is called when `SDM_Core.trace_count` equals `SDM_Capacity`, THEN THE Affective_Memory SHALL evict the Memory_Trace with the lowest `decay_weight` before writing the new trace, ensuring the store never exceeds `SDM_Capacity`.
5. IF the `content_vector` provided to `store` has a dimensionality different from the configured `M`, THEN THE Affective_Memory SHALL raise a `ValueError` identifying the actual and expected dimensionalities without writing to the SDM_Core.
6. IF any dimension of the `pad_state` provided to `store` is outside `[-1.0, 1.0]`, THEN THE Affective_Memory SHALL raise a `ValueError` identifying the invalid dimension without writing to the SDM_Core.
7. THE Affective_Memory SHALL complete the `store` operation, including SDM_Core write and index update, within 100 milliseconds on the target CPU hardware.
8. THE Affective_Memory SHALL support concurrent read access to the trace index from the Ecphory_Engine and write access from the `store` method using a thread-safe locking mechanism, acquiring any required lock within 5 milliseconds without blocking the Orchestrator pipeline for longer than that bound.

---

### Requirement 6: Affective Memory — Trace Retrieval Interface

**User Story:** As the Ecphory_Engine, I want to iterate over all stored Memory_Traces and their PAD_Tags without acquiring an exclusive write lock, so that resonance scoring can proceed concurrently with new trace storage.

#### Acceptance Criteria

1. THE Affective_Memory SHALL expose a `get_all_traces() -> list[Memory_Trace]` method that returns a snapshot of all currently stored Memory_Trace records.
2. WHEN `get_all_traces` is called, THE Affective_Memory SHALL return a list reflecting the state of the index at the moment the call is made, without blocking ongoing `store` operations for longer than the lock acquisition bound defined in Requirement 5.8.
3. WHEN `get_all_traces` is called and the index contains zero traces, THE Affective_Memory SHALL return an empty list without raising an exception.
4. THE Affective_Memory SHALL expose a `get_trace(trace_id: int) -> Memory_Trace` method that returns the Memory_Trace for the given `trace_id`.
5. IF `get_trace` is called with a `trace_id` that does not exist in the index, THEN THE Affective_Memory SHALL raise a `KeyError` identifying the unknown trace ID.

---

### Requirement 7: Soft Decay — Time-Based Trace Weakening

**User Story:** As the memory system, I want each Memory_Trace to have its `decay_weight` reduced over time at a rate proportional to its emotional intensity, so that low-intensity memories fade faster and high-intensity memories persist longer, without any explicit user action.

#### Acceptance Criteria

1. THE Decay_Engine SHALL compute the Decay_Rate for each Memory_Trace as `base_decay_rate × (1.0 - Emotional_Intensity)`, where `Emotional_Intensity = clip(|arousal| × (|pleasure| + 0.1), 0.0, 1.0)` is derived from the trace's PAD_Tag.
2. WHEN the Slow_Loop tick executes, THE Decay_Engine SHALL apply the formula `decay_weight = decay_weight - (Decay_Rate × elapsed_seconds)` to every stored Memory_Trace, where `elapsed_seconds` is the number of seconds since the last Slow_Loop tick, and SHALL clamp the result to `[0.0, 1.0]`.
3. THE Decay_Engine SHALL accept a configurable `base_decay_rate` with a default value of `0.0001` per second, giving a trace with `Emotional_Intensity = 0.0` a half-life of approximately 1.9 hours.
4. WHEN the Slow_Loop tick executes, THE Decay_Engine SHALL remove from the Affective_Memory index all Memory_Traces whose `decay_weight` has fallen at or below the `Viability_Threshold` after decay is applied.
5. THE Decay_Engine SHALL accept a configurable `Viability_Threshold` with a default value of `0.05`.
6. THE Decay_Engine SHALL accept a configurable Slow_Loop cadence in seconds with a default of 3600 seconds and a minimum of 60 seconds.
7. IF the configured Slow_Loop cadence is below 60 seconds, THEN THE Decay_Engine SHALL raise a `ValueError` at initialization identifying the invalid cadence and the minimum acceptable value.
8. WHEN a Memory_Trace is removed due to decay, THE Decay_Engine SHALL call `SDM_Core.delete(trace_id)` for that trace and remove the trace from the Affective_Memory index atomically within a single lock acquisition.
9. WHEN the Slow_Loop thread encounters an unhandled exception during a tick, THE Decay_Engine SHALL log the error with a full stack trace, leave the current trace index unchanged, and resume the loop at the next scheduled tick without terminating the thread.

---

### Requirement 8: Soft Decay — Slow Loop Lifecycle

**User Story:** As the Memory_Augmented_Orchestrator, I want the Decay_Engine's Slow_Loop to run as a managed background thread with clean startup and shutdown, so that decay processing does not interfere with foreground pipeline calls.

#### Acceptance Criteria

1. THE Decay_Engine SHALL expose a `start()` method that launches the Slow_Loop in a dedicated daemon background thread.
2. WHEN `start()` is called, THE Decay_Engine SHALL confirm the Slow_Loop thread is alive within 2 seconds before returning; IF the thread does not reach a running state within 2 seconds, THE Decay_Engine SHALL raise a `RuntimeError`.
3. THE Decay_Engine SHALL expose a `stop()` method that signals the Slow_Loop thread to terminate, waits for the thread to join with a timeout of 5 seconds, and sets the thread reference to `None`.
4. WHILE the Slow_Loop thread is sleeping between ticks, THE Decay_Engine SHALL respond to the stop signal within 1 second of `stop()` being called.
5. THE Decay_Engine SHALL expose an `is_alive() -> bool` method returning `True` when the Slow_Loop thread is running and `False` otherwise.
6. WHILE the Slow_Loop is executing a decay tick, THE Decay_Engine SHALL NOT block any concurrent Affective_Memory `store` call for longer than the lock acquisition bound defined in Requirement 5.8.

---

### Requirement 9: Synergistic Ecphory — Resonance Scoring

**User Story:** As the Memory_Augmented_Orchestrator, I want the Ecphory_Engine to identify Memory_Traces whose PAD_Tags are emotionally resonant with the current PAD_State, so that only affectively aligned memories are eligible for reawakening.

#### Acceptance Criteria

1. THE Ecphory_Engine SHALL compute the Resonance_Score for each candidate Memory_Trace as the cosine similarity between the current PAD_State vector `[pleasure, arousal, dominance]` and the trace's PAD_Tag vector `[pleasure, arousal, dominance]`, producing a value in `[-1.0, 1.0]`.
2. THE Ecphory_Engine SHALL accept a configurable `Resonance_Threshold` with a default value of `0.6` and a valid range of `[0.0, 1.0]`.
3. IF the configured `Resonance_Threshold` is outside `[0.0, 1.0]`, THEN THE Ecphory_Engine SHALL raise a `ValueError` at initialization identifying the invalid value.
4. WHEN the current PAD_State vector has a magnitude of zero (all dimensions exactly zero), THE Ecphory_Engine SHALL return an empty list without computing any resonance scores.
5. THE Ecphory_Engine SHALL filter all stored Memory_Traces to those whose Resonance_Score exceeds `Resonance_Threshold` AND whose `decay_weight` exceeds the `Viability_Threshold`, treating both conditions as required.
6. THE Ecphory_Engine SHALL weight each candidate trace's Content_Vector by the product of its `Resonance_Score` and its current `decay_weight` before combining traces into the Echo_Vector.
7. THE Ecphory_Engine SHALL accept a configurable `Ecphory_K` with a default of 5 and a valid range of `[1, 50]`.
8. IF the configured `Ecphory_K` is outside `[1, 50]`, THEN THE Ecphory_Engine SHALL raise a `ValueError` at initialization.
9. WHEN more than `Ecphory_K` traces exceed the Resonance_Threshold, THE Ecphory_Engine SHALL select the top-`Ecphory_K` traces by descending Resonance_Score before computing the Echo_Vector.

---

### Requirement 10: Synergistic Ecphory — Echo Vector Assembly

**User Story:** As the Memory_Augmented_Orchestrator, I want the Ecphory_Engine to produce a single Echo_Vector summarizing the reawakened memory content, so that the Orchestrator can append it to the Conditioned_Prompt without exposing individual memory traces to the LLM.

#### Acceptance Criteria

1. WHEN at least one Memory_Trace passes the resonance and viability filters, THE Ecphory_Engine SHALL produce the Echo_Vector as the weighted mean of the selected Content_Vectors, where each Content_Vector is weighted by `Resonance_Score × decay_weight`, normalized so that the weights sum to 1.0.
2. THE Ecphory_Engine SHALL clip the Echo_Vector to `[-1.0, 1.0]` after computing the weighted mean.
3. WHEN no Memory_Trace passes the resonance and viability filters, THE Ecphory_Engine SHALL return `None` rather than a zero vector, signaling the Orchestrator that no echo is available for this step.
4. THE Ecphory_Engine SHALL complete echo vector assembly for up to 10,000 candidate traces within 100 milliseconds on the target CPU hardware.
5. THE Ecphory_Engine SHALL expose a `query(pad_state: PADState, traces: list[Memory_Trace]) -> np.ndarray | None` interface as its primary public method, accepting the current PAD_State and the full trace list obtained from `Affective_Memory.get_all_traces()`.
6. IF any dimension of the `pad_state` passed to `query` is outside `[-1.0, 1.0]`, THEN THE Ecphory_Engine SHALL raise a `ValueError` identifying the invalid dimension.
7. FOR ALL valid inputs where the same trace list and PAD_State are provided, THE Ecphory_Engine SHALL return the same Echo_Vector, making the query deterministic given equivalent inputs.

---

### Requirement 11: Memory Echo — Conditioned Prompt Integration

**User Story:** As the Orchestrator, I want the reawakened Echo_Vector to be appended to the Conditioned_Prompt as a numeric contextual section, so that the LLM_Backend is influenced by emotional memory resonance without receiving any first-person retrieval framing.

#### Acceptance Criteria

1. THE Memory_Augmented_Orchestrator SHALL insert a memory echo step between pipeline step 4 (behavioral constraint derivation) and step 5 (prompt assembly), calling `Ecphory_Engine.query()` with the current PAD_State and the current trace list from `Affective_Memory.get_all_traces()`.
2. WHEN the Ecphory_Engine returns a non-`None` Echo_Vector, THE Memory_Augmented_Orchestrator SHALL pass the Echo_Vector to the PromptAssembler for inclusion in the Conditioned_Prompt as a distinct numeric section using the section boundary marker inherited from Phase 1.
3. THE PromptAssembler SHALL encode the Echo_Vector in the Conditioned_Prompt as a sequence of numeric key-value pairs in the format `echo_{i}: {value:.6f}` for each dimension `i`, with the section headed by the label `[MEMORY ECHO]`, and SHALL NOT include any natural-language text attributing memory, recollection, or prior experience to the system.
4. WHEN the Ecphory_Engine returns `None`, THE Memory_Augmented_Orchestrator SHALL omit the `[MEMORY ECHO]` section from the Conditioned_Prompt entirely, with no placeholder or empty section.
5. THE Memory_Augmented_Orchestrator SHALL store a new Memory_Trace after a successful LLM response is returned, calling `Affective_Memory.store()` with the current Stimulus_Vector (padded or truncated to dimensionality `M`) and the current PAD_State snapshot obtained in step 3 of the pipeline.
6. IF the Ecphory_Engine raises an exception during the memory echo step, THEN THE Memory_Augmented_Orchestrator SHALL log the error, omit the echo section from the prompt, and continue pipeline execution without entering a Degraded_State.
7. IF the Affective_Memory `store` call after LLM response raises an exception, THEN THE Memory_Augmented_Orchestrator SHALL log the error and return the LLM response to the caller without entering a Degraded_State.
8. THE Memory_Augmented_Orchestrator SHALL include the echo step timing and the Resonance_Score of the highest-scoring trace (or 0.0 if no echo) in the per-call structured log entry inherited from Phase 1.

---

### Requirement 12: Memory Does Not Produce First-Person Recall Language

**User Story:** As the designer of Lucia's character, I want to ensure that memory reawakening never surfaces as explicit recall language in the output, so that memory influence is felt as behavioral texture rather than described as recollection.

#### Acceptance Criteria

1. THE PromptAssembler SHALL NOT include any natural-language phrase that describes past interactions, references prior conversation turns as memories, or attributes recollection to the system in the `[MEMORY ECHO]` section or any other prompt section added by Phase 2.
2. THE Boundary_Layer SHALL extend its default detection set to include the following additional patterns for Phase 2: `\bI remember\b`, `\bI recall\b`, `\blast time\b`, `\byou mentioned\b`, `\byou said\b`, `\bI know from before\b`, `\bpreviously you\b`, `\bmy memory\b`.
3. WHEN any of the extended detection patterns is matched in LLM output, THE Boundary_Layer SHALL apply a Soft_Block as defined in Phase 1 Requirement 7.3, replacing the matched span with `"[...]"` and logging the event.
4. THE Ecphory_Engine SHALL return echo vectors exclusively as numeric arrays and SHALL NOT include any string field, label, or annotation that describes the source or nature of the memory content.
5. IF the assembled Conditioned_Prompt contains the literal substring `"I remember"`, `"I recall"`, `"last time"`, `"you mentioned"`, or `"you said"` within the `[MEMORY ECHO]` section, THEN THE PromptAssembler SHALL raise an `AssemblyError` identifying the offending substring and SHALL NOT return the prompt to the Orchestrator.

---

### Requirement 13: Memory System Configuration

**User Story:** As a developer deploying Phase 2, I want all memory module parameters to be configurable at initialization from a structured config object, so that capacity, decay rates, resonance thresholds, and loop cadences can be tuned for the target hardware without code changes.

#### Acceptance Criteria

1. THE Memory_Augmented_Orchestrator SHALL accept an extended configuration object that includes all Phase 1 fields plus: `sdm_num_locations`, `sdm_address_dim`, `sdm_content_dim`, `sdm_hamming_radius_fraction`, `sdm_capacity`, `decay_base_rate`, `decay_viability_threshold`, `decay_loop_cadence_seconds`, `ecphory_k`, `ecphory_resonance_threshold`.
2. THE SDM_Core SHALL accept configuration for: `num_locations`, address dimensionality `D`, content dimensionality `M`, and `hamming_radius_fraction` (fraction of `D` used to compute Hamming_Radius, valid range `(0.0, 1.0)`).
3. THE Affective_Memory SHALL accept configuration for: `sdm_capacity` and the content dimensionality `M` (must match the SDM_Core's configured `M`).
4. THE Decay_Engine SHALL accept configuration for: `base_decay_rate` (valid range `(0.0, 1.0)`), `viability_threshold` (valid range `(0.0, 1.0)`), and `loop_cadence_seconds` (valid range `[60, 86400]`).
5. THE Ecphory_Engine SHALL accept configuration for: `resonance_threshold` (valid range `[0.0, 1.0]`) and `ecphory_k` (valid range `[1, 50]`).
6. IF any required Phase 2 configuration value is missing from the configuration object, THEN THE Memory_Augmented_Orchestrator SHALL raise a `ValueError` at initialization identifying the missing key before any module is constructed.
7. IF any Phase 2 configuration value falls outside its documented valid range, THEN THE Memory_Augmented_Orchestrator SHALL raise a `ValueError` at initialization identifying the invalid parameter and its acceptable range.
8. IF the `sdm_content_dim` in the SDM_Core config does not equal the `M` value in the Affective_Memory config, THEN THE Memory_Augmented_Orchestrator SHALL raise a `ValueError` at initialization identifying the mismatch.

---

### Requirement 14: Memory System Lifecycle — Startup and Shutdown

**User Story:** As a developer deploying Phase 2, I want the memory system components to start and stop cleanly alongside the Orchestrator, so that no background threads are left running after the system is shut down.

#### Acceptance Criteria

1. WHEN the Memory_Augmented_Orchestrator is initialized, THE Memory_Augmented_Orchestrator SHALL start the Decay_Engine Slow_Loop thread after the Phase 1 Emotion_Core Fast_Loop thread has been confirmed alive, and SHALL confirm the Slow_Loop thread is alive within 2 seconds before accepting any `process` calls.
2. IF the Decay_Engine Slow_Loop thread fails to reach a running state within 2 seconds of initialization, THEN THE Memory_Augmented_Orchestrator SHALL raise an initialization error and reject all subsequent `process` calls until successfully re-initialized.
3. WHEN the Memory_Augmented_Orchestrator is shut down via `shutdown()`, THE Memory_Augmented_Orchestrator SHALL call `Decay_Engine.stop()` and wait for the Slow_Loop thread to join with a timeout of 5 seconds before releasing the LLM_Backend.
4. WHILE the Memory_Augmented_Orchestrator is processing a `process` call, THE Memory_Augmented_Orchestrator SHALL NOT delay any pending Decay_Engine Slow_Loop tick by more than 1 second due to lock contention on the Affective_Memory index.
5. THE Memory_Augmented_Orchestrator SHALL log the count of active Memory_Traces and the count of traces removed during the most recent Slow_Loop tick in the structured initialization log on startup.

---

### Requirement 15: Memory System — RAM Footprint Constraint

**User Story:** As a developer deploying Lucia on the target hardware (16 GB RAM), I want the SDM_Core and Affective_Memory index to stay within a defined RAM budget, so that the memory system does not crowd out the LLM inference and background loops.

#### Acceptance Criteria

1. THE SDM_Core SHALL maintain its hard location matrix and content accumulator in dense `numpy` arrays using `float32` precision for accumulator values and `bool` (1 bit per element, stored as `uint8`) for binary address vectors, limiting the RAM footprint of the accumulator matrix for 1,000 Hard_Locations × 64-dimensional content to no more than 256 KB.
2. THE SDM_Core SHALL report its current RAM footprint in bytes via a `memory_usage_bytes() -> int` method, computed as the sum of `nbytes` for all stored numpy arrays.
3. WHEN configured with `num_locations = 1000`, `D = 1000`, `M = 64`, and `SDM_Capacity = 10000`, THE SDM_Core RAM footprint as reported by `memory_usage_bytes()` SHALL be no greater than 2 GB at full capacity.
4. THE Affective_Memory SHALL report its trace index RAM footprint via a `index_memory_usage_bytes() -> int` method, computed as the sum of `sys.getsizeof` applied to each Memory_Trace object in the index.
5. WHEN the Affective_Memory index contains 10,000 Memory_Trace objects each with a 64-dimensional Content_Vector and a PAD_Tag, THE Affective_Memory `index_memory_usage_bytes()` SHALL return a value no greater than 20 MB.

---

### Requirement 16: No Identity Timeline

**User Story:** As the designer of Lucia's character, I want to ensure that the memory system does not link Memory_Traces into a narrative sequence or create any persistent self-timeline, so that memory reawakening produces associative resonance rather than autobiographical continuity.

#### Acceptance Criteria

1. THE Affective_Memory SHALL store each Memory_Trace as an independent record with no reference to any other Memory_Trace, no sequence index, and no ordering metadata beyond the individual `timestamp` field used for decay computation.
2. THE Ecphory_Engine SHALL select top-K traces by Resonance_Score only and SHALL NOT sort, group, or prioritize traces by `timestamp`, recency, or any ordering that implies a timeline.
3. THE PromptAssembler SHALL NOT include any structural indicator of the temporal ordering of reawakened traces in the `[MEMORY ECHO]` section; echo dimensions SHALL be presented as a flat numeric sequence without timestamps, sequence numbers, or labels suggesting chronological order.
4. THE Decay_Engine SHALL treat each Memory_Trace decay computation as independent; the Decay_Rate of one trace SHALL NOT be influenced by the age, content, or emotional intensity of any other trace.
5. THE Memory_Augmented_Orchestrator SHALL NOT maintain any session-level list or log of which Memory_Traces were reawakened during prior `process` calls in the current session.
