# Design Document — Lucia Inference Phase 4

## Overview

Phase 4 populates the currently empty `src/core/inference/` module with two new components:

1. **Active_Inference_Engine** (`src/core/inference/active_inference.py`) — A minimal per-turn prediction-error minimization loop. Maintains a 3×3 linear generative model of PAD transitions and updates it by gradient descent at each conversation turn.
2. **LNN_Trainer** (`src/core/inference/lnn_trainer.py`) — Online backpropagation-through-ODE training of the EmotionCore LNN weights. Uses `torchdiffeq` to make the ODE solver differentiable, accumulates experience in a ring buffer, and applies weight updates in a background thread.

Phase 1–3 code is unchanged. Phase 4 introduces the `Inference_Phase4_Orchestrator` as a subclass of the Phase 2 `MemoryAugmentedOrchestrator`, adding two new pipeline steps (2b and 4c) without modifying the base class.

No CUDA usage in Phase 4. All tensor operations run on CPU to avoid VRAM competition with LFM2.5-1.2B.

---

## Architecture

### Module Map

```
src/core/inference/
    __init__.py           (already exists, empty)
    active_inference.py   [NEW] — ActiveInferenceEngine
    lnn_trainer.py        [NEW] — LNNTrainer
    sync_server.py        [NEW, optional] — DeviceSyncServer
    orchestrator.py       [NEW] — InferencePipelineOrchestrator (subclass of MemoryAugmentedOrchestrator)
```

### Extended Pipeline (10 steps)

```
User input
  │
Step 1:  Stimulus_Processor.encode(input_text)              → stimulus: np.ndarray
Step 2:  EmotionCore.push_stimulus(stimulus)
Step 2b: h_before = EmotionCore._h.copy()                   [NEW Phase 4]
Step 3:  pad = EmotionCore.get_pad_state()
         HomeostaticEngine.record_input()
         markers = HomeostaticEngine.compute_somatic_markers(pad)
Step 4:  constraints = compute_behavioral_constraints(markers, pad)
Step 4c: pred_err = ActiveInferenceEngine.step(pad_before, pad) [NEW Phase 4]
         LNNTrainer.push_sample(stimulus, h_before, h_after)    [NEW Phase 4]
Step 4b: echo_vec = EcphoryEngine.query(pad, traces)         [Phase 2]
Step 5:  prompt = PromptAssembler.assemble(..., echo_vector=echo_vec)
Step 6:  latency delay
Step 7:  raw = LLMBackend.generate(prompt, constraints)
Step 8:  safe = BoundaryLayer.validate(raw)
Step 9:  AffectiveMemory.store(stimulus_padded, pad)
  │
response: str
```

Note: Step 2b captures `h_before` immediately after `push_stimulus` (which queues the stimulus for the next Fast_Loop tick) but before the Fast_Loop has processed it. This is an approximation — the actual `h_after` observed by the Emotion_Core is read after step 3 via `EmotionCore._h`. The timing approximation is acceptable because:
- The Fast_Loop cadence is 200 ms; the pipeline call is ~2–8 s (LLM-dominated)
- The training signal is a noisy online estimate anyway; sub-tick precision is unnecessary

### Concurrent Thread Structure (Phase 4 additions)

```
Background Thread 1 (daemon) — Phase 1: EmotionCore._fast_loop_worker()
Background Thread 2 (daemon) — Phase 2: DecayEngine._slow_loop_worker()
Background Thread 3 (daemon) — Phase 4: LNNTrainer._train_loop_worker()
```

**Lock discipline:**

| Lock | Owner | Held by | Max hold time |
|------|-------|---------|---------------|
| `EmotionCore._state_lock` | EmotionCore | Fast_Loop write, pipeline read | 1 ms |
| `AffectiveMemory._index_lock` | AffectiveMemory | DecayEngine, store, get_all_traces | 50 ms (decay tick) |
| `LNNTrainer._buffer_lock` | LNNTrainer ring buffer | push_sample, train loop read | 1 ms |
| `LNNTrainer._train_lock` | Weight_Swap | train loop, Fast_Loop ODE | 5 ms |

The `_train_lock` is shared between the LNN_Trainer (held during Weight_Swap) and the EmotionCore (held during ODE step when reading weight matrices). The EmotionCore's `_fast_loop_worker()` must be modified to acquire `_train_lock` before reading weight matrices:

```python
# EmotionCore._ode_step() modification (Phase 4):
def _ode_step(self, h, x):
    with self._train_lock:    # acquire before reading weights
        W_tau = self.W_tau.copy()
        U_tau = self.U_tau.copy()
        # ... copy all weights
    def rhs(t, y): ...        # use local copies; no lock held during ODE solve
```

This ensures Weight_Swap never races with an ODE solve reading stale partial weights. The lock hold during weight copy is O(weight_matrix_sizes) ≈ 32×32×5 floats ≈ 40 KB copy ≈ negligible μs.

---

## Components and Interfaces

### ActiveInferenceEngine (`src/core/inference/active_inference.py`)

**Responsibility:** One-step linear generative model of PAD dynamics. Minimizes prediction error by gradient descent on `A_matrix` and `b_vector`.

```python
@dataclass
class ActiveInferenceConfig:
    kl_weight:     float = 0.01   # [0.0, 1.0]
    learning_rate: float = 1e-3   # (0.0, 1.0]

class ActiveInferenceEngine:
    def __init__(self, config: ActiveInferenceConfig) -> None: ...
    def step(self, pad_before: PADState, pad_after: PADState) -> float: ...
    def reset(self) -> None: ...
    def get_belief_state(self) -> dict: ...
```

#### Internal State

```python
self._A = np.eye(3, dtype=np.float64)     # 3×3 identity
self._b = np.zeros(3, dtype=np.float64)   # bias
```

#### `step()` Implementation

```python
def step(self, pad_before: PADState, pad_after: PADState) -> float:
    for dim, val in [("pleasure", pad_before.pleasure), ...]:
        if not (-1.0 <= val <= 1.0):
            raise ValueError(f"pad_before.{dim}={val} outside [-1, 1]")
    # ... validate pad_after similarly

    p = np.array([pad_before.pleasure, pad_before.arousal, pad_before.dominance])
    q = np.array([pad_after.pleasure,  pad_after.arousal,  pad_after.dominance])

    # Early-exit: zero PAD cannot produce meaningful prediction
    if np.linalg.norm(p) == 0.0:
        return 0.0

    predicted = self._A @ p + self._b
    pred_error = np.linalg.norm(predicted - q)

    # Free energy: prediction error^2 + KL toward identity
    I = np.eye(3)
    free_energy = pred_error**2 + self._config.kl_weight * np.sum((self._A - I)**2)

    # Analytic gradients (all 3×3 matrix ops)
    dFE_dA = 2 * (predicted - q)[:, np.newaxis] @ p[np.newaxis, :] \
             + 2 * self._config.kl_weight * (self._A - I)
    dFE_db = 2 * (predicted - q)

    # Gradient descent update
    lr = self._config.learning_rate
    self._A -= lr * dFE_dA
    self._b -= lr * dFE_db
    np.clip(self._A, -2.0, 2.0, out=self._A)   # prevent unbounded growth

    return float(pred_error)
```

Analytic gradients are used (not autograd) because the model is a simple linear function — this keeps the implementation dependency-free (no PyTorch for this module) and sub-millisecond.

---

### LNNTrainer (`src/core/inference/lnn_trainer.py`)

**Responsibility:** Online backprop-through-ODE training of EmotionCore LNN weights.

```python
@dataclass
class LNNTrainerConfig:
    batch_size:         int   = 16      # [4, 256]; 0 = disabled
    learning_rate:      float = 1e-4    # (0, 1]
    gradient_clip_norm: float = 1.0     # (0, 100]
    weight_decay:       float = 1e-5    # [0, 0.1]
    ode_step_size:      float = 0.1     # must match EmotionCore config

class LNNTrainer:
    def __init__(self, emotion_core: EmotionCore, config: LNNTrainerConfig) -> None: ...
    def start(self) -> None: ...
    def stop(self) -> None: ...
    def push_sample(self, stimulus: np.ndarray, h_before: np.ndarray, h_after: np.ndarray) -> None: ...
    def is_training_active(self) -> bool: ...
    def training_step_count(self) -> int: ...
```

#### PyTorch Parameter Initialization

```python
import torch
import torch.nn as nn
from torchdiffeq import odeint

class _LNNModel(nn.Module):
    def __init__(self, hidden_dim: int, stimulus_dim: int):
        super().__init__()
        ec = emotion_core  # reference, not stored — weights copied at init
        self.W_tau = nn.Parameter(torch.from_numpy(ec.W_tau.copy()).float())
        self.U_tau = nn.Parameter(torch.from_numpy(ec.U_tau.copy()).float())
        self.b_tau = nn.Parameter(torch.from_numpy(ec.b_tau.copy()).float())
        self.W_f   = nn.Parameter(torch.from_numpy(ec.W_f.copy()).float())
        self.U_f   = nn.Parameter(torch.from_numpy(ec.U_f.copy()).float())
        self.b_f   = nn.Parameter(torch.from_numpy(ec.b_f.copy()).float())
        self.W_proj = nn.Parameter(torch.from_numpy(ec.W_proj.copy()).float())
        self.b_proj = nn.Parameter(torch.from_numpy(ec.b_proj.copy()).float())

    def forward(self, t, h):
        # h: (hidden_dim,) tensor
        # x: stored as self._x for the current ODE solve
        tau = torch.nn.functional.softplus(self.W_tau @ h + self.U_tau @ self._x + self.b_tau)
        f   = torch.tanh(self.W_f @ h + self.U_f @ self._x + self.b_f)
        return (-h + f) / tau
```

#### Ring Buffer

```python
from collections import deque
import threading

self._buffer: deque[tuple] = deque(maxlen=config.batch_size)
self._buffer_lock = threading.Lock()
self._batch_ready = threading.Event()

def push_sample(self, stimulus, h_before, h_after):
    if self._config.batch_size == 0:
        return
    with self._buffer_lock:                # hold < 1 ms
        self._buffer.append((
            stimulus.copy(), h_before.copy(), h_after.copy()
        ))
        if len(self._buffer) >= self._config.batch_size:
            self._batch_ready.set()
```

#### Training Loop

```python
def _train_loop_worker(self):
    while not self._stop_event.is_set():
        self._batch_ready.wait(timeout=10.0)
        if self._stop_event.is_set():
            break
        self._batch_ready.clear()

        with self._buffer_lock:
            batch = list(self._buffer)
        if len(batch) < self._config.batch_size:
            continue

        try:
            self._gradient_step(batch)
        except Exception:
            logger.error("LNN training step failed", exc_info=True)

def _gradient_step(self, batch):
    self._optimizer.zero_grad()
    total_loss = torch.tensor(0.0)

    for stimulus, h_before, h_after in batch:
        x = torch.from_numpy(stimulus[:self._model.W_f.shape[1]]).float()
        h0 = torch.from_numpy(h_before).float()
        h_obs = torch.from_numpy(h_after).float()

        self._model._x = x
        t_span = torch.tensor([0.0, self._config.ode_step_size])
        h_pred = odeint(self._model, h0, t_span, method='rk4')[-1]

        loss = torch.mean((h_pred - h_obs) ** 2)
        total_loss = total_loss + loss

    (total_loss / len(batch)).backward()

    # Safety check
    for name, p in self._model.named_parameters():
        if not torch.isfinite(p.grad).all():
            logger.warning("Non-finite gradient in %s; skipping update", name)
            self._consecutive_bad_updates += 1
            self._optimizer.zero_grad()
            if self._consecutive_bad_updates > 5:
                self._training_active = False
                logger.error("Training disabled after 5 consecutive bad updates")
            return

    torch.nn.utils.clip_grad_norm_(
        self._model.parameters(), self._config.gradient_clip_norm
    )
    self._optimizer.step()
    self._consecutive_bad_updates = 0
    self._step_count += 1

    # Weight_Swap
    self._weight_swap()

def _weight_swap(self):
    with self._train_lock:    # 5 ms max
        ec = self._emotion_core
        ec.W_tau = self._model.W_tau.detach().numpy().copy()
        ec.U_tau = self._model.U_tau.detach().numpy().copy()
        ec.b_tau = self._model.b_tau.detach().numpy().copy()
        ec.W_f   = self._model.W_f.detach().numpy().copy()
        ec.U_f   = self._model.U_f.detach().numpy().copy()
        ec.b_f   = self._model.b_f.detach().numpy().copy()
        ec.W_proj = self._model.W_proj.detach().numpy().copy()
        ec.b_proj = self._model.b_proj.detach().numpy().copy()
```

#### Optimizer

```python
self._optimizer = torch.optim.AdamW(
    self._model.parameters(),
    lr=config.learning_rate,
    weight_decay=config.weight_decay,
)
```

---

### InferencePipelineOrchestrator (`src/core/inference/orchestrator.py`)

**Responsibility:** Extend Phase 2 `MemoryAugmentedOrchestrator` with Active Inference step (4c) and LNN sample push (2b + 4c).

```python
@dataclass
class InferenceOrchestratorConfig:
    # All Phase 2 MemoryOrchestratorConfig fields (inherited)
    # ... [copy all Phase 2 fields] ...

    # Phase 4 fields
    ai_kl_weight:          float = 0.01
    ai_learning_rate:      float = 1e-3
    lnn_batch_size:        int   = 16
    lnn_learning_rate:     float = 1e-4
    lnn_gradient_clip_norm: float = 1.0
    lnn_weight_decay:      float = 1e-5

class InferencePipelineOrchestrator(MemoryAugmentedOrchestrator):
    def __init__(self, config: InferenceOrchestratorConfig) -> None:
        super().__init__(config)   # starts Fast_Loop + Slow_Loop

        ai_config = ActiveInferenceConfig(
            kl_weight=config.ai_kl_weight,
            learning_rate=config.ai_learning_rate,
        )
        self._ai_engine = ActiveInferenceEngine(ai_config)

        if config.lnn_batch_size > 0:
            trainer_config = LNNTrainerConfig(
                batch_size=config.lnn_batch_size,
                learning_rate=config.lnn_learning_rate,
                gradient_clip_norm=config.lnn_gradient_clip_norm,
                weight_decay=config.lnn_weight_decay,
                ode_step_size=config.ode_step_size,  # from Phase 1 EmotionConfig
            )
            self._lnn_trainer = LNNTrainer(self._emotion_core, trainer_config)
            self._lnn_trainer.start()
            # Confirm alive within 2 s
            deadline = time.monotonic() + 2.0
            while time.monotonic() < deadline:
                if self._lnn_trainer.is_training_active():
                    break
                time.sleep(0.05)
            else:
                raise RuntimeError("LNN_Trainer thread failed to start within 2 seconds")
        else:
            self._lnn_trainer = None

    def process(self, input_text: str) -> str:
        # Guards (inherited)
        if len(input_text) == 0 or len(input_text) > 4000:
            return self._config.fallback_response
        if self._degraded:
            return self._config.fallback_response

        call_id = uuid.uuid4().hex
        pred_error = 0.0

        try:
            # Step 1: encode
            stimulus = self._stimulus_processor.encode(input_text)

            # Step 2: push stimulus
            pad_before = self._emotion_core.get_pad_state()  # PAD before stimulus
            self._emotion_core.push_stimulus(stimulus)

            # Step 2b: capture h_before [NEW]
            h_before = self._emotion_core._h.copy()

            # Step 3: somatic
            pad = self._emotion_core.get_pad_state()
            self._homeostatic_engine.record_input()
            markers = self._homeostatic_engine.compute_somatic_markers(pad)

            # Step 4: behavioral constraints
            constraints = self._homeostatic_engine.compute_behavioral_constraints(markers, pad)

            # Step 4c: Active Inference + LNN sample [NEW]
            try:
                pred_error = self._ai_engine.step(pad_before, pad)
            except Exception:
                logger.error("ActiveInference step failed; continuing", exc_info=True)
            try:
                if self._lnn_trainer:
                    h_after = self._emotion_core._h.copy()
                    self._lnn_trainer.push_sample(stimulus, h_before, h_after)
            except Exception:
                logger.error("LNN push_sample failed; continuing", exc_info=True)

            # Step 4b: memory echo (Phase 2, unchanged)
            echo_vec = None
            try:
                traces = self._affective_memory.get_all_traces()
                echo_vec = self._ecphory_engine.query(pad, traces)
            except Exception:
                logger.error("Ecphory step failed; omitting echo", exc_info=True)

            # Steps 5–9: inherited Phase 2 behavior
            prompt = self._prompt_assembler.assemble(
                somatic=markers, constraints=constraints,
                history=self._history, system_preamble=self._config.system_preamble,
                echo_vector=echo_vec,
            )
            if isinstance(prompt, AssemblyError):
                return self._config.fallback_response

            delay_s = min(constraints.latency_ms, 5000) / 1000
            if delay_s > 0:
                time.sleep(delay_s)

            raw_response = self._llm_backend.generate(prompt, constraints)
            if raw_response is None:
                return self._config.fallback_response

            safe_response = self._boundary_layer.validate(raw_response)

            try:
                M = self._affective_memory._M
                content = stimulus[:M] if stimulus.shape[0] >= M else np.pad(stimulus, (0, M - stimulus.shape[0]))
                content = np.clip(content.astype(np.float32), -1.0, 1.0)
                self._affective_memory.store(content, pad)
            except Exception:
                logger.error("Memory store step failed; continuing", exc_info=True)

            logger.info(
                "call_id=%s pred_error=%.4f lnn_steps=%d",
                call_id, pred_error,
                self._lnn_trainer.training_step_count() if self._lnn_trainer else 0,
            )
            self._history.append(("user", input_text))
            self._history.append(("assistant", safe_response))
            return safe_response

        except Exception as e:
            logger.error("Unhandled exception call_id=%s: %s", call_id, e, exc_info=True)
            self._degraded = True
            return self._config.fallback_response

    def shutdown(self) -> None:
        if self._lnn_trainer:
            self._lnn_trainer.stop()
        super().shutdown()
```

---

### DeviceSyncServer (`src/core/inference/sync_server.py`) [Optional]

Implemented using only stdlib (`socket`, `json`, `threading`). Disabled unless `sync_enabled=True` in config.

```python
class DeviceSyncServer:
    def start(self) -> None: ...   # binds TCP server; falls back to connect-only on bind failure
    def stop(self) -> None: ...
    def broadcast_pad(self, pad: PADState) -> None: ...   # called every 1 s by a background thread
    def _on_remote_pad(self, remote_pad: PADState) -> None:
        # Blend and inject into EmotionCore as synthetic stimulus
        merged = blend(local_pad, remote_pad, self._config.sync_weight)
        synthetic_stimulus = np.zeros(N)
        synthetic_stimulus[:3] = [merged.pleasure, merged.arousal, merged.dominance]
        self._emotion_core.push_stimulus(synthetic_stimulus)
```

---

## Data Models

### ActiveInferenceConfig

```python
@dataclass
class ActiveInferenceConfig:
    kl_weight:     float = 0.01   # [0.0, 1.0]
    learning_rate: float = 1e-3   # (0.0, 1.0]
```

### LNNTrainerConfig

```python
@dataclass
class LNNTrainerConfig:
    batch_size:         int   = 16      # [4, 256]; 0 = disabled
    learning_rate:      float = 1e-4    # (0, 1]
    gradient_clip_norm: float = 1.0     # (0, 100]
    weight_decay:       float = 1e-5    # [0, 0.1]
    ode_step_size:      float = 0.1     # must match EmotionConfig.ode_step_size
```

### InferenceOrchestratorConfig additions over Phase 2

| Field | Type | Default | Constraint |
|-------|------|---------|------------|
| `ai_kl_weight` | float | 0.01 | [0.0, 1.0] |
| `ai_learning_rate` | float | 1e-3 | (0.0, 1.0] |
| `lnn_batch_size` | int | 16 | [4, 256] or 0 |
| `lnn_learning_rate` | float | 1e-4 | (0, 1] |
| `lnn_gradient_clip_norm` | float | 1.0 | (0, 100] |
| `lnn_weight_decay` | float | 1e-5 | [0, 0.1] |

---

## Correctness Properties

### Property P4-1: Active Inference Short-Horizon Constraint

*For any sequence of `step()` calls, the Belief_State (`A_matrix`, `b_vector`) depends ONLY on the sequence of `(pad_before, pad_after)` pairs and the initial config; it has no dependency on conversation history, timestamps, or any external reward signal.*

**Validates: Requirements 3.1–3.5**

### Property P4-2: Prediction Error Non-Negative

*For any valid `(pad_before, pad_after)` pair, `step()` returns a non-negative float.*

**Validates: Requirement 2.1, 2.5**

### Property P4-3: Free Energy Decreases on Repeated Identical Inputs

*For any fixed `(pad_before, pad_after)` pair applied repeatedly, the sequence of Free_Energy values is non-increasing (the gradient descent converges), assuming the learning rate is small enough.*

**Validates: Requirements 2.2, 2.3**

### Property P4-4: Weight_Swap Atomicity

*At any moment during an ODE solve in the EmotionCore Fast_Loop, all weight matrices read by the ODE RHS function are from the same gradient update step (either all pre-swap or all post-swap), never a mix of the two.*

**Validates: Requirement 6.3**

### Property P4-5: LNN Gradient Clipping Prevents Overflow

*For any batch of training samples, after gradient clipping the L2 norm of the concatenated gradient vector across all parameters is at most `gradient_clip_norm`.*

**Validates: Requirement 5.1**

### Property P4-6: Training Disabled on Instability

*If 6 or more consecutive gradient updates are discarded due to non-finite values, `is_training_active()` returns `False` and no further weight swaps occur.*

**Validates: Requirement 5.4**
