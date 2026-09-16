# Implementation Plan: Lucia Inference Phase 4

## Overview

Implement the Active Inference engine and online LNN training system inside `src/core/inference/`. Phase 4 does NOT modify any Phase 1–3 files except for:
- `src/core/emotion/emotion_core.py`: add `_train_lock` acquisition in `_ode_step()` when reading weight matrices.
- `src/core/inference/orchestrator.py`: new file, subclasses `MemoryAugmentedOrchestrator`.

New Python dependencies: `torch`, `torchdiffeq`. No CUDA-specific code. All tensor ops on CPU.

Property-based tests use Hypothesis with `@settings(max_examples=200)`. Tasks marked `*` are optional.

---

## Tasks

- [ ] 1. Scaffolding and dependency setup
  - Add `torch` and `torchdiffeq` to `requirements.txt`
  - Create `src/core/inference/active_inference.py` stub (imports, `ActiveInferenceConfig`, `ActiveInferenceEngine` class skeleton)
  - Create `src/core/inference/lnn_trainer.py` stub (`LNNTrainerConfig`, `_LNNModel(nn.Module)`, `LNNTrainer` class skeleton)
  - Create `src/core/inference/orchestrator.py` stub (`InferenceOrchestratorConfig`, `InferencePipelineOrchestrator` subclass skeleton)
  - Create `src/core/inference/sync_server.py` stub (disabled by default, `DeviceSyncServer` skeleton)
  - Create test stubs: `tests/unit/test_active_inference.py`, `tests/unit/test_lnn_trainer.py`, `tests/unit/test_inference_orchestrator.py`, `tests/property/test_properties_phase4.py`
  - _Requirements: 1.1, 4.1, 8.1_

- [ ] 2. ActiveInferenceEngine — Belief_State init and step()
  - [ ] 2.1 Implement `ActiveInferenceEngine.__init__()` in `src/core/inference/active_inference.py`
    - Validate `kl_weight` in [0.0, 1.0] and `learning_rate` in (0.0, 1.0]; raise `ValueError` for invalid values
    - Initialize `_A = np.eye(3, dtype=np.float64)` and `_b = np.zeros(3, dtype=np.float64)`
    - Implement `reset()`: reset `_A` to identity, `_b` to zeros
    - Implement `get_belief_state()`: return `{"A_matrix": self._A, "b_vector": self._b}` (no copy — callers must not mutate)
    - _Requirements: 1.1–1.5_
  - [ ] 2.2 Implement `ActiveInferenceEngine.step()` in `src/core/inference/active_inference.py`
    - Validate all 6 PAD dimensions; raise `ValueError` if any is outside [-1.0, 1.0]; no Belief_State mutation on validation failure
    - Early-exit: return 0.0 and skip update when `norm(pad_before_vec) == 0.0`
    - Compute `predicted = A @ p + b`; `pred_error = norm(predicted - q)`
    - Compute analytic gradients: `dFE/dA = 2*(predicted - q)[:, newaxis] @ p[newaxis, :] + 2*kl*(A - I)`, `dFE/db = 2*(predicted - q)`
    - Update: `A -= lr * dFE_dA`; `b -= lr * dFE_db`; clip A to [-2.0, 2.0]
    - Return `pred_error` (pre-update value)
    - Complete within 5 ms
    - _Requirements: 2.1–2.8, 3.1–3.5_
  - [ ]* 2.3 Write unit tests for `ActiveInferenceEngine` in `tests/unit/test_active_inference.py`
    - `ActiveInferenceConfig(kl_weight=1.1)` raises `ValueError`
    - `ActiveInferenceConfig(learning_rate=0.0)` raises `ValueError`
    - `step()` with `pad_before` dim outside [-1, 1] raises `ValueError`; `_A` unchanged
    - `step()` with zero `pad_before` returns 0.0; `_A` unchanged
    - `reset()` restores `_A` to identity and `_b` to zeros
    - After 100 `step()` calls with fixed `(pad_before, pad_after)` pair, `pred_error` is strictly less than initial `pred_error` (convergence)
    - `_A` values always in [-2.0, 2.0] after any number of `step()` calls
    - _Requirements: 1.1–1.5, 2.1–2.8_
  - [ ]* 2.4 Write property tests P31–P33 in `tests/property/test_properties_phase4.py`
    - **Property P4-1: AI Step Non-Negative Error** — `builds(PADState, floats(-1,1), floats(-1,1), floats(-1,1))` for before/after (non-zero before); assert `step()` returns float >= 0.0
    - **Property P4-2: AI A_Matrix Bounds Invariant** — arbitrary sequence of valid `step()` calls; assert all `_A` values in [-2.0, 2.0] after each call
    - **Property P4-3: AI Convergence on Fixed Input** — repeated `step()` with same `(pad_before, pad_after)`; compute first and 50th pred_error; assert 50th <= first
    - _Requirements: 2.5, 2.6, 3.5_

- [ ] 3. LNN_Trainer — _LNNModel and ring buffer
  - [ ] 3.1 Implement `_LNNModel(nn.Module)` in `src/core/inference/lnn_trainer.py`
    - `__init__(emotion_core, hidden_dim, stimulus_dim)`: initialize `nn.Parameter` tensors from `emotion_core` numpy weight matrices (`.copy()`)
    - `forward(t, h)`: LTC RHS `(-h + tanh(W_f @ h + U_f @ x + b_f)) / softplus(W_tau @ h + U_tau @ x + b_tau)` where `x = self._x` (set before `odeint` call)
    - All operations on CPU (`torch.device('cpu')`)
    - _Requirements: 4.1, 4.2, 6.5_
  - [ ] 3.2 Implement `LNNTrainer.__init__()` and `push_sample()` in `src/core/inference/lnn_trainer.py`
    - Validate all config fields; raise `ValueError` for invalid values
    - If `batch_size == 0`: set `_training_active = False`; `push_sample()` is a no-op
    - Initialize `_buffer = deque(maxlen=batch_size)`, `_buffer_lock = threading.Lock()`, `_batch_ready = threading.Event()`, `_stop_event = threading.Event()`
    - `push_sample(stimulus, h_before, h_after)`: acquire `_buffer_lock`; append copies; set `_batch_ready` if `len(_buffer) >= batch_size`; release lock (< 1 ms)
    - `_train_lock = threading.Lock()` shared with `EmotionCore` (passed in or set on `emotion_core` as an attribute)
    - _Requirements: 4.3, 4.4, 6.3, 6.4_
  - [ ] 3.3 Implement `LNNTrainer._gradient_step()` and `_weight_swap()` in `src/core/inference/lnn_trainer.py`
    - `_gradient_step(batch)`: zero grad; for each sample, set `_model._x = torch.from_numpy(stimulus[:stim_dim]).float()`; `odeint(_model, h0_tensor, t_span, method='rk4')[-1]`; accumulate MSE loss; backprop; check finite grads; clip; step optimizer; increment `_step_count`; call `_weight_swap()`
    - Non-finite grad handling: increment `_consecutive_bad_updates`; skip weight swap; if > 5, set `_training_active = False`; log error
    - `_weight_swap()`: acquire `_train_lock`; copy all 8 `.detach().numpy().copy()` arrays to `emotion_core` weight attributes; release lock
    - _Requirements: 4.4–4.6, 5.1–5.6_
  - [ ] 3.4 Implement `LNNTrainer.start()`, `stop()`, `_train_loop_worker()` in `src/core/inference/lnn_trainer.py`
    - `start()`: clear stop event; launch daemon thread `"LNN-Trainer"`; confirm `is_training_active()` within 2 s or raise `RuntimeError`
    - `_train_loop_worker()`: `_batch_ready.wait(timeout=10.0)`; on stop event break; clear `_batch_ready`; read batch under lock; call `_gradient_step()`; on any exception log and continue
    - `stop()`: set stop event; join with `timeout=5.0`; set `_training_active = False`
    - _Requirements: 6.1, 6.2, 6.6_
  - [ ] 3.5 Modify `EmotionCore._ode_step()` in `src/core/emotion/emotion_core.py`
    - Add `_train_lock: threading.Lock = threading.Lock()` attribute to `EmotionCore.__init__()`
    - In `_ode_step()`, acquire `_train_lock` to copy weight matrices into local numpy arrays before the `solve_ivp` call; release lock before ODE integration begins; use local copies inside RHS function
    - This is the ONLY change to Phase 1 code in Phase 4
    - _Requirements: 6.3, Correctness Property P4-4_
  - [ ]* 3.6 Write unit tests for `LNNTrainer` in `tests/unit/test_lnn_trainer.py`
    - `LNNTrainerConfig(batch_size=3)` raises `ValueError`
    - `LNNTrainerConfig(batch_size=0)` → `push_sample()` no-ops; `is_training_active() == False`
    - `start()` → `is_training_active() == True`; `stop()` → `is_training_active() == False`
    - Push exactly `batch_size` samples → `_batch_ready` is set → training thread executes one step → `training_step_count() == 1`
    - Mock `_gradient_step` to raise 6 times → `is_training_active() == False` (disabled after instability)
    - `_weight_swap()`: after one gradient step, at least one weight matrix in `EmotionCore` differs from the Xavier init
    - _Requirements: 4.4–4.6, 5.4, 5.5, 6.1, 6.2_
  - [ ]* 3.7 Write property tests P34–P35 in `tests/property/test_properties_phase4.py`
    - **Property P4-4: Weight_Swap Atomicity** — concurrent thread reads EmotionCore weights during _weight_swap; assert all 8 matrices are either all pre-swap or all post-swap values (use a marker sentinel value trick)
    - **Property P4-5: Gradient Clip Norm Bound** — construct batch with extreme h_before/h_after values; run `_gradient_step()`; if training_step_count increments, verify gradient norms after clipping are <= `gradient_clip_norm` (instrument via hook)
    - _Requirements: 5.1, 6.3_

- [ ] 4. Checkpoint — core inference modules
  - Run `pytest tests/unit/test_active_inference.py tests/unit/test_lnn_trainer.py tests/property/test_properties_phase4.py --tb=short`
  - All non-skipped tests pass
  - Ask the user if any questions arise

- [ ] 5. InferencePipelineOrchestrator — integration
  - [ ] 5.1 Implement `InferencePipelineOrchestrator.__init__()` in `src/core/inference/orchestrator.py`
    - Define `InferenceOrchestratorConfig` as flat dataclass: all Phase 2 `MemoryOrchestratorConfig` fields + 6 Phase 4 fields
    - Validate Phase 4 fields; raise `ValueError` for invalid values or missing keys
    - Call `super().__init__(config)` to start Fast_Loop + Slow_Loop; then instantiate `ActiveInferenceEngine` and `LNNTrainer`; start `LNNTrainer`; confirm alive within 2 s
    - _Requirements: 7.5, 8.1–8.3_
  - [ ] 5.2 Implement `InferencePipelineOrchestrator.process()` in `src/core/inference/orchestrator.py`
    - Steps 1–4 identical to Phase 2 plus step 2b (capture `h_before`) and step 4c (AI step + LNN push), both wrapped in `try/except` that log and continue
    - Steps 4b, 5–9 identical to Phase 2
    - Log `pred_error` and `lnn_steps` in structured log
    - _Requirements: 7.1–7.4_
  - [ ] 5.3 Implement `InferencePipelineOrchestrator.shutdown()` in `src/core/inference/orchestrator.py`
    - Call `_lnn_trainer.stop()` before `super().shutdown()`
    - _Requirements: 7.6_
  - [ ]* 5.4 Write unit tests for `InferencePipelineOrchestrator` in `tests/unit/test_inference_orchestrator.py`
    - Config with missing Phase 4 field raises `ValueError` at init
    - `lnn_batch_size=0` → `_lnn_trainer` is None; `process()` does not call `push_sample()`
    - AI engine exception in step 4c → response still returned; no `_degraded` state set
    - LNN `push_sample()` exception → response still returned; no `_degraded` state set
    - `shutdown()` calls `_lnn_trainer.stop()` before Phase 2 `super().shutdown()`
    - `training_step_count()` increments after accumulating enough samples (mock LLM)
    - _Requirements: 7.1–7.6, 8.4_

- [ ] 6. DeviceSyncServer (optional, low priority)
  - [ ]* 6.1 Implement `DeviceSyncServer` in `src/core/inference/sync_server.py`
    - Stdlib only: `socket`, `json`, `threading`, `hmac`, `hashlib`
    - Server mode: bind TCP on configured port; on connection, verify `sync_secret` via HMAC; accept PAD JSON packets; blend with local PAD; inject as synthetic stimulus
    - Client/receive-only mode: on bind failure, connect to existing server on network
    - Broadcast loop: background thread emits current PAD JSON every 1 s to all connected peers
    - `stop()`: close all sockets; join threads
    - _Requirements: 9.1–9.7_
  - [ ]* 6.2 Write unit tests for `DeviceSyncServer` using localhost loopback
    - Server starts; client connects with correct secret → accepted
    - Client connects with wrong secret → connection refused
    - PAD packet received → `EmotionCore.push_stimulus()` called with blended PAD in first 3 dims
    - `sync_weight=0.0` → local PAD unchanged by remote; `sync_weight=1.0` → local PAD fully replaced by remote
    - _Requirements: 9.3, 9.5_

- [ ] 7. Final checkpoint — all tests green
  - Run `pytest tests/unit tests/property tests/integration --tb=short` (GPU tests skip without LUCIA_MODEL_PATH)
  - All non-skipped tests pass
  - Verify `LNN_Trainer.training_step_count()` > 0 after 16+ `push_sample()` calls in integration test
  - Ask the user if any questions arise

---

## Notes

- `torchdiffeq` must be installed: `pip install torchdiffeq`. It depends on PyTorch but not CUDA. Always import with `from torchdiffeq import odeint` and use `method='rk4'` (explicit, no autograd issues with adaptive step methods).
- The `_LNNModel.forward(t, h)` signature matches `torchdiffeq.odeint`'s expected ODE function signature `f(t, y)`.
- `_train_lock` is added to `EmotionCore` in Phase 4 as a new attribute. It is NOT used in Phase 1–3 code. The Phase 4 modification to `_ode_step()` is the only change to existing Phase 1 code.
- The `_consecutive_bad_updates` counter resets to 0 after a successful gradient step. It only reaches 5 if 5 updates in a row fail without any success in between.
- `lnn_batch_size=0` is the "training disabled" sentinel. It must be tested separately from `lnn_batch_size=4` (minimum valid non-zero value).
- `ActiveInferenceEngine` uses only NumPy (no PyTorch) — analytic gradients on a 3×3 matrix are trivial and dependency-free.
- DeviceSyncServer (task 6) is explicitly low-priority. It SHOULD be deferred until all other Phase 4 tasks are complete and tested.

## Task Dependency Graph

```json
{
  "waves": [
    {"id": 0, "tasks": ["1"]},
    {"id": 1, "tasks": ["2.1", "3.1"]},
    {"id": 2, "tasks": ["2.2", "3.2", "3.5"]},
    {"id": 3, "tasks": ["2.3", "2.4", "3.3"]},
    {"id": 4, "tasks": ["3.4", "3.6", "3.7"]},
    {"id": 5, "tasks": ["4"]},
    {"id": 6, "tasks": ["5.1"]},
    {"id": 7, "tasks": ["5.2", "5.3"]},
    {"id": 8, "tasks": ["5.4", "6.1"]},
    {"id": 9, "tasks": ["6.2", "7"]}
  ]
}
```
