# Requirements Document

## Introduction

This document defines the requirements for **Lucia Inference Phase 4**: the Active Inference engine and online LNN training system. Phase 4 covers two cooperating components:

1. **Active_Inference_Engine** — A short-horizon prediction-error minimization system that maintains a generative model of the current conversation context and updates it at each interaction step to reduce surprise. It operates on an intermittent (per-turn) basis, NOT as a long-running planner with goals or desires.
2. **LNN_Trainer** — An online backpropagation-through-ODE training loop that adjusts the Liquid Time-Constant network weights in `EmotionCore` based on accumulated prediction errors. Uses `torchdiffeq` for differentiable ODE solving. The Phase 1 weights are currently fixed Xavier-init; Phase 4 makes them learnable and continuously updated.

The target module is `src/core/inference/` which is currently empty. No new neural network libraries beyond PyTorch and `torchdiffeq` are introduced. No cloud dependencies.

---

## Glossary

- **Active_Inference_Engine**: The module (`src/core/inference/active_inference.py`) implementing short-horizon free energy minimization over the current PAD state and conversation context. Maps to the "Lõi Động lực" (Active Inference Engine) layer in the design philosophy document.
- **LNN_Trainer**: The module (`src/core/inference/lnn_trainer.py`) that performs online gradient-based training of the LNN weight matrices (`W_tau`, `U_tau`, `b_tau`, `W_f`, `U_f`, `b_f`, `W_proj`, `b_proj`) using backpropagation through the `torchdiffeq` ODE solver.
- **Generative_Model**: A lightweight internal model maintained by the Active_Inference_Engine that predicts the next PAD state given the current PAD state and the current stimulus. Parameterized as a linear transition `A_matrix` (3×3) and bias `b_vector` (3,).
- **Prediction_Error**: The L2 distance between the Generative_Model's predicted PAD state and the observed PAD state after an ODE step. Computed as `||predicted_pad - observed_pad||_2`.
- **Free_Energy**: The scalar loss used by the Active_Inference_Engine, computed as `Prediction_Error^2 + KL_regularization`. The KL term is a lightweight L2 penalty on the `A_matrix` toward the identity matrix, preventing unbounded model drift.
- **Belief_State**: The current `A_matrix` and `b_vector` representing the Active_Inference_Engine's internal model of emotional dynamics. Updated by gradient descent at each inference step.
- **Inference_Step**: One call to `Active_Inference_Engine.step(pad_before, stimulus, pad_after)`, which computes prediction error, updates the Belief_State, and returns the prediction error scalar as a signal.
- **Training_Batch**: A fixed-size ring buffer of `(stimulus_vector, hidden_state_before, hidden_state_after)` tuples accumulated by the LNN_Trainer. When the buffer is full, one gradient update step is executed.
- **ODE_Params**: The set of LNN weight tensors (`W_tau`, `U_tau`, `b_tau`, `W_f`, `U_f`, `b_f`) managed as PyTorch `nn.Parameter` objects in the LNN_Trainer.
- **Projection_Params**: The projection weights (`W_proj`, `b_proj`) in `LNN_Trainer` that map hidden state to PAD space.
- **Train_Lock**: A `threading.Lock` held briefly by the LNN_Trainer during a weight update to swap updated weights atomically into the `EmotionCore`'s weight matrices.
- **Weight_Swap**: The operation by which the LNN_Trainer copies its updated `nn.Parameter` tensors (as numpy arrays) into the `EmotionCore`'s live weight matrices (`W_tau`, etc.). Performed under `Train_Lock`.
- **Gradient_Clip_Norm**: The maximum L2 norm of the gradient vector before clipping. Default: `1.0`. Prevents gradient explosions during online learning.
- **Learning_Rate**: The AdamW optimizer learning rate for LNN weight updates. Default: `1e-4`.
- **KL_Weight**: The scalar coefficient on the L2 regularization term in the Free_Energy loss. Default: `0.01`.
- **Batch_Size**: The number of ODE steps accumulated before one gradient update. Default: `16`.
- **Device_Sync_Server**: The optional multi-device PAD sync server (`src/core/inference/sync_server.py`). Low-priority, disabled by default. Runs as a TCP server on the local network, broadcasting the latest PAD state to registered peers.

---

## Requirements

### Requirement 1: Active Inference Engine — Generative Model Initialization

**User Story:** As the Inference_Phase4_Orchestrator, I want the Active_Inference_Engine to maintain a simple linear generative model of PAD dynamics, so that prediction errors can be computed at each turn as a measure of surprise.

#### Acceptance Criteria

1. THE Active_Inference_Engine SHALL initialize a Belief_State consisting of `A_matrix` (3×3 numpy float64, initialized to the identity matrix) and `b_vector` (3-dimensional numpy float64, initialized to zeros), representing the generative model `predicted_pad = A_matrix @ current_pad + b_vector`.
2. THE Active_Inference_Engine SHALL accept a configurable `kl_weight` (float, default `0.01`, valid range `[0.0, 1.0]`) and `learning_rate` (float, default `1e-3`, valid range `(0.0, 1.0]`) for Belief_State gradient updates.
3. IF `kl_weight` is outside `[0.0, 1.0]` or `learning_rate` is outside `(0.0, 1.0]`, THEN THE Active_Inference_Engine SHALL raise a `ValueError` at initialization identifying the invalid parameter.
4. THE Active_Inference_Engine SHALL expose a `reset()` method that resets `A_matrix` to the identity matrix and `b_vector` to zeros, restoring the Belief_State to its initialized state.
5. THE Active_Inference_Engine SHALL expose a `get_belief_state() -> dict` method returning `{"A_matrix": np.ndarray, "b_vector": np.ndarray}` as a snapshot of the current Belief_State without copying internal state.

---

### Requirement 2: Active Inference Engine — Prediction and Error Computation

**User Story:** As the Inference_Phase4_Orchestrator, I want the Active_Inference_Engine to compute prediction error after each Emotion_Core ODE step, so that the discrepancy between the generative model and observed reality can be measured and used to update the Belief_State.

#### Acceptance Criteria

1. THE Active_Inference_Engine SHALL expose a `step(pad_before: PADState, pad_after: PADState) -> float` method that computes the Prediction_Error as `||A_matrix @ pad_before_vec - pad_after_vec||_2` where `pad_before_vec` and `pad_after_vec` are 3D numpy float64 arrays.
2. THE `step()` method SHALL compute the Free_Energy as `Prediction_Error^2 + kl_weight * ||A_matrix - I||_F^2`, where `I` is the 3×3 identity matrix and `||.||_F` is the Frobenius norm.
3. THE `step()` method SHALL update the Belief_State by one gradient descent step on the Free_Energy with respect to `A_matrix` and `b_vector` using the learning rate from configuration.
4. THE `step()` method SHALL clip `A_matrix` values to `[-2.0, 2.0]` after the gradient update to prevent unbounded growth.
5. THE `step()` method SHALL return the Prediction_Error scalar (float) before the gradient update, so that callers observe the pre-update error.
6. IF any dimension of `pad_before` or `pad_after` is outside `[-1.0, 1.0]`, THEN THE Active_Inference_Engine SHALL raise a `ValueError` identifying the invalid dimension without modifying the Belief_State.
7. THE `step()` method SHALL complete within 5 ms on the target CPU hardware (3×3 matrix operations are computationally trivial; this bound is a guard against implementation errors).
8. WHEN the PAD state has zero magnitude before the step (all three dimensions exactly zero), THE Active_Inference_Engine SHALL return `0.0` as the Prediction_Error and SHALL NOT update the Belief_State.

---

### Requirement 3: Active Inference Engine — Short-Horizon Constraint

**User Story:** As the designer of Lucia's character, I want Active Inference to minimize short-term prediction error only, with no long-term goals, desires, or planning horizons, so that the engine provides local adaptability without creating a goal-directed agent.

#### Acceptance Criteria

1. THE Active_Inference_Engine SHALL NOT maintain any goal state, target state, or reference trajectory beyond the current Belief_State's one-step linear model.
2. THE Active_Inference_Engine SHALL NOT perform multi-step lookahead, tree search, or any planning that evaluates consequences beyond the immediate next PAD state.
3. THE Active_Inference_Engine SHALL NOT store or use conversation history for Belief_State updates; each `step()` call is self-contained with respect to the current PAD transition.
4. THE Belief_State update SHALL be driven exclusively by observed PAD transitions, with no external reward signal, user preference model, or optimization target other than prediction error minimization.
5. THE Free_Energy loss function SHALL include ONLY the Prediction_Error squared term and the KL regularization toward identity; no additional terms (e.g., expected utility, information gain) SHALL be included.

---

### Requirement 4: LNN Trainer — ODE-Based Online Training

**User Story:** As the Emotion_Core, I want my LNN weights to be trained online via backpropagation through the ODE solver after each batch of experience, so that the liquid dynamics adapt to Lucia's typical interaction patterns over time.

#### Acceptance Criteria

1. THE LNN_Trainer SHALL maintain the LNN weight matrices (`W_tau`, `U_tau`, `b_tau`, `W_f`, `U_f`, `b_f`, `W_proj`, `b_proj`) as PyTorch `nn.Parameter` objects initialized from the current values of the corresponding numpy arrays in the `EmotionCore`.
2. THE LNN_Trainer SHALL use `torchdiffeq.odeint` (or `odeint_adjoint`) to solve the LNN ODE differentiably over a fixed time interval `[0, dt]` where `dt` is the Emotion_Core's `ode_step_size`, enabling gradient computation through the ODE solution.
3. THE LNN_Trainer SHALL accumulate `(stimulus_vector, h_before, h_after_observed)` tuples in a ring buffer of size `Batch_Size` after each successful Emotion_Core ODE step.
4. WHEN the ring buffer contains `Batch_Size` tuples, THE LNN_Trainer SHALL execute one gradient update step: compute the ODE-predicted `h_after_predicted` from `h_before` and `stimulus_vector` using the current `nn.Parameter` weights; compute MSE loss `||h_after_predicted - h_after_observed||^2`; backpropagate; clip gradients to `Gradient_Clip_Norm`; step the optimizer.
5. THE LNN_Trainer SHALL use AdamW as the optimizer, with `learning_rate` and `weight_decay=1e-5`.
6. AFTER each gradient update step, THE LNN_Trainer SHALL perform a Weight_Swap: copy the updated `nn.Parameter` tensors (`.detach().numpy()`) into the `EmotionCore`'s live weight matrices under the `Train_Lock`.
7. THE Weight_Swap SHALL hold the `Train_Lock` for no longer than 5 ms; the lock is a plain `threading.Lock` shared between the LNN_Trainer and the EmotionCore's `_fast_loop_worker`.
8. THE LNN_Trainer SHALL accept configurable: `batch_size` (int, default 16, valid range [4, 256]), `learning_rate` (float, default 1e-4, valid range (0, 1]), `gradient_clip_norm` (float, default 1.0, valid range (0, 100]), `weight_decay` (float, default 1e-5, valid range [0, 0.1]).
9. IF any training configuration value falls outside its valid range, THE LNN_Trainer SHALL raise a `ValueError` at initialization identifying the invalid parameter.

---

### Requirement 5: LNN Trainer — Training Safety and Stability

**User Story:** As a developer deploying Phase 4, I want the LNN training loop to be robust against gradient instability and weight divergence, so that online learning does not destabilize the Emotion_Core's continuous emotional state.

#### Acceptance Criteria

1. THE LNN_Trainer SHALL clip the gradient of the training loss with respect to all parameters to a maximum L2 norm of `Gradient_Clip_Norm` before applying the optimizer step, using `torch.nn.utils.clip_grad_norm_`.
2. AFTER each gradient update, THE LNN_Trainer SHALL verify that all weight tensors are finite (no NaN or Inf values); IF any non-finite value is detected, THE LNN_Trainer SHALL discard the update, reinitialize the affected weight tensors to their last known-good values, log a warning, and NOT perform a Weight_Swap.
3. THE LNN_Trainer SHALL maintain a snapshot of the last-known-good weight tensors updated only after a verified finite gradient step, so that rollback to the last-good state is always possible.
4. IF more than 5 consecutive gradient updates are discarded due to non-finite values, THE LNN_Trainer SHALL disable training (stop executing gradient updates), log an error, and emit a `training_disabled` event to the InferencePipelineOrchestrator.
5. THE LNN_Trainer SHALL expose an `is_training_active() -> bool` method returning `True` when training is enabled and `False` when disabled (either never started or disabled due to instability).
6. THE LNN_Trainer SHALL expose a `training_step_count() -> int` method returning the total number of successfully applied gradient updates since initialization.

---

### Requirement 6: LNN Trainer — Lifecycle and Thread Safety

**User Story:** As the InferencePipelineOrchestrator, I want the LNN_Trainer to run gradient updates in a background thread without blocking the Emotion_Core Fast_Loop or the Orchestrator pipeline, so that training never introduces latency into the user-facing response path.

#### Acceptance Criteria

1. THE LNN_Trainer SHALL expose a `start()` method that launches a background daemon thread named `"LNN-Trainer"` that blocks on a `threading.Event` until a full batch is available, then runs one gradient update step, then blocks again.
2. THE LNN_Trainer SHALL expose a `stop()` method that signals the training thread to terminate and joins it with a `timeout=5.0`; after `stop()`, `is_training_active()` SHALL return `False`.
3. THE training thread SHALL NOT hold any lock during the forward ODE pass or the backward pass; it SHALL only acquire locks for buffer read (`_buffer_lock`) and for Weight_Swap (`Train_Lock`), each for the minimum necessary duration.
4. THE buffer accumulation path (called from the Emotion_Core Fast_Loop or Orchestrator pipeline) SHALL be non-blocking: `push_sample(stimulus, h_before, h_after)` SHALL acquire `_buffer_lock` for no longer than 1 ms to append to the ring buffer.
5. THE LNN_Trainer SHALL NOT import or use any CUDA-specific code paths; all tensor operations SHALL run on CPU to avoid VRAM competition with the LFM2.5-1.2B inference.
6. WHEN the training thread encounters an unhandled exception during a gradient step, THE LNN_Trainer SHALL log the full stack trace and continue the training loop at the next batch without terminating the thread.

---

### Requirement 7: Phase 4 Pipeline Integration

**User Story:** As the Inference_Phase4_Orchestrator, I want the Active_Inference_Engine and LNN_Trainer to be integrated into the processing pipeline so that each conversation turn contributes to both active inference and LNN adaptation.

#### Acceptance Criteria

1. THE `Inference_Phase4_Orchestrator` SHALL be a subclass of `MemoryAugmentedOrchestrator` (Phase 2), overriding `process()` to insert two new steps:
   - **Step 2b** (after `push_stimulus`, before `get_pad_state`): capture `h_before = EmotionCore._h.copy()` for the LNN_Trainer.
   - **Step 4c** (after behavioral constraints, before memory echo): call `Active_Inference_Engine.step(pad_before, pad_now)` to compute and log the Prediction_Error; call `LNN_Trainer.push_sample(stimulus, h_before, h_after)` where `h_after = EmotionCore._h`.
2. THE Prediction_Error returned by `Active_Inference_Engine.step()` SHALL be included in the per-call structured log entry alongside the existing Phase 2 log fields.
3. IF `Active_Inference_Engine.step()` raises an exception, THE `Inference_Phase4_Orchestrator` SHALL log the error and continue pipeline execution without entering Degraded_State.
4. IF `LNN_Trainer.push_sample()` raises an exception, THE `Inference_Phase4_Orchestrator` SHALL log the error and continue pipeline execution without entering Degraded_State.
5. THE `Inference_Phase4_Orchestrator` SHALL start both the `LNN_Trainer` background thread and confirm it is alive within 2 seconds during `__init__()`, AFTER the Phase 2 `Decay_Engine` Slow_Loop has been confirmed alive.
6. WHEN the `Inference_Phase4_Orchestrator` is shut down via `shutdown()`, THE `Inference_Phase4_Orchestrator` SHALL call `LNN_Trainer.stop()` before calling `super().shutdown()`.

---

### Requirement 8: Phase 4 Configuration

**User Story:** As a developer deploying Phase 4, I want all Active Inference and LNN training parameters to be configurable at initialization from a structured config object.

#### Acceptance Criteria

1. THE `Inference_Phase4_Orchestrator` SHALL accept an extended configuration object that includes all Phase 2 fields plus: `ai_kl_weight`, `ai_learning_rate`, `lnn_batch_size`, `lnn_learning_rate`, `lnn_gradient_clip_norm`, `lnn_weight_decay`.
2. IF any Phase 4 configuration value is missing from the configuration object, THE `Inference_Phase4_Orchestrator` SHALL raise a `ValueError` at initialization identifying the missing key.
3. IF any Phase 4 configuration value falls outside its documented valid range, THE `Inference_Phase4_Orchestrator` SHALL raise a `ValueError` at initialization identifying the invalid parameter.
4. THE LNN training SHALL be enabled by default. It SHALL be possible to disable it by setting `lnn_batch_size` to `0` (zero), causing `push_sample()` to be a no-op and `is_training_active()` to return `False` without starting the training thread.

---

### Requirement 9: Multi-Device Sync (Optional, Low Priority)

**User Story:** As a user running Lucia on multiple local machines, I want the PAD state to synchronize across devices via the local network, so that switching devices preserves emotional continuity.

#### Acceptance Criteria

1. THE Device_Sync_Server SHALL be disabled by default and SHALL only start if `sync_enabled: true` is set in the configuration.
2. WHEN enabled, THE Device_Sync_Server SHALL bind a TCP server to `0.0.0.0` on a configurable port (default `9100`) and SHALL broadcast the latest PAD state (as a JSON packet `{"pad": {...}, "timestamp": float}`) to all registered peer connections every 1 second.
3. WHEN a peer PAD state packet is received, THE Device_Sync_Server SHALL blend the received PAD with the local PAD using a configurable `sync_weight` (float, default `0.1`, range `[0.0, 1.0]`) as: `merged_pad = local_pad * (1 - sync_weight) + remote_pad * sync_weight`.
4. THE merged PAD SHALL be injected into the `EmotionCore` as a synthetic stimulus vector (mapping the 3D merged PAD to the first 3 dimensions of a zero-padded stimulus vector of dimensionality N).
5. THE Device_Sync_Server SHALL authenticate peers by a configurable shared secret (`sync_secret`, a string) verified on connection; connections with an incorrect secret SHALL be refused immediately.
6. IF the Device_Sync_Server cannot bind the configured port (e.g., port already in use), IT SHALL log an error and start in receive-only mode (connecting to an existing server on the network) rather than failing the entire application startup.
7. THE multi-device sync feature SHALL be implemented entirely within `src/core/inference/sync_server.py` and SHALL NOT introduce any new Python package dependencies beyond the standard library (`socket`, `json`, `threading`).

---

### Requirement 10: RAM and CPU Budget

**User Story:** As a developer deploying Phase 4 on the target hardware (16 GB RAM, CPU-only for inference subsystem), I want the Active Inference engine and LNN training to stay within a defined resource budget, so that Phase 4 does not degrade the existing system's responsiveness.

#### Acceptance Criteria

1. THE `Active_Inference_Engine` Belief_State (`A_matrix` 3×3 float64 + `b_vector` 3×float64) SHALL occupy no more than 1 KB of RAM.
2. THE `LNN_Trainer` ring buffer with `batch_size = 16` samples, each consisting of a stimulus vector (N=16 float64), `h_before` (hidden_dim=32 float64), and `h_after` (hidden_dim=32 float64), SHALL occupy no more than 100 KB of RAM.
3. THE `LNN_Trainer` PyTorch parameter tensors for the LNN weight matrices (with `hidden_dim=32` and `stimulus_dim=16`) SHALL occupy no more than 200 KB of RAM.
4. ONE `Active_Inference_Engine.step()` call SHALL complete within 5 ms on the target CPU hardware.
5. ONE `LNN_Trainer` gradient update step (forward ODE pass + backward + optimizer step) SHALL complete within 500 ms on the target CPU hardware with `batch_size=16` and `hidden_dim=32`.
6. THE `LNN_Trainer` training thread SHALL NOT consume more than 20% of one CPU core on average over any 60-second window, measured as CPU time used divided by wall clock time elapsed.
