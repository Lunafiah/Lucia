# Requirements Document

## Introduction

This document defines the requirements for **Lucia Embodied Desktop Presence — Phase 5**.
Phase 5 gives Lucia two intertwined capabilities:

1. **Perception** — Lucia can see the user's screen via periodic screenshots processed by a local
   Vision Language Model (Qwen2.5-VL 3B GGUF), and optionally observe the user's physical
   environment via a webcam. Visual context feeds into emotional state and conversation prompts.
2. **Agency** — Lucia can interact with the desktop: clicking, typing, scrolling, focusing windows,
   and executing multi-step tasks via a ReAct (Reason + Act) agent loop. The user retains
   unconditional override via a hardware-level Emergency Stop hotkey.

Phase 5 extends the Phase 2 `MemoryAugmentedOrchestrator` through a new `PresenceOrchestrator`.
The only change to Phase 1-4 code is an optional `screen_context` parameter on `PromptAssembler.assemble()`.

Constraint: **Windows-first, localhost only, no cloud.**

---

## Glossary

- **VisionBackend**: `src/core/perception/vision_backend.py` — wraps Qwen2.5-VL 3B GGUF via llama-cpp-python multimodal interface.
- **ScreenObserver**: `src/core/perception/screen_observer.py` — background thread for periodic screenshot capture with pixel-diff change detection.
- **CameraObserver**: `src/core/perception/camera_observer.py` — background thread for webcam frame capture.
- **ScreenContext**: Dataclass: `description` (str), `app_name` (str), `window_title` (str), `timestamp` (float).
- **CameraContext**: Dataclass: `description` (str), `timestamp` (float).
- **UIGrounding**: `src/core/agency/ui_grounding.py` — locates UI elements via Windows UIA first, VLM coordinate prediction as fallback.
- **ActionToken**: Typed dataclass for one atomic desktop action (click, type, scroll, etc.).
- **ActionExecutor**: `src/core/agency/action_executor.py` — dispatches ActionTokens via `pyautogui`.
- **SafetyGuard**: `src/core/agency/safety_guard.py` — manages ControlState, EmergencyStop, ForbiddenZones, rate limiting.
- **ControlState**: Enum: `IDLE | WATCH | ASSIST | ACTIVE`.
- **EmergencyStop**: Global hotkey `Ctrl+Shift+Space` — sets a `threading.Event`, transitions ControlState to WATCH.
- **ReactLoop**: `src/core/agency/react_loop.py` — Observe -> Think -> Act -> Verify agent loop.
- **PresenceOrchestrator**: `src/core/presence/orchestrator.py` — subclass of MemoryAugmentedOrchestrator coordinating all Phase 5 components.
- **ObservationComment**: Natural-language remark from Lucia triggered by significant screen change.
- **ForbiddenZone**: Process name or window title pattern that blocks all agency actions.
- **mmproj**: The CLIP vision encoder projection GGUF required by Qwen2.5-VL for multimodal inference.

---

## Requirements

### Requirement 1: Vision Backend

**User Story:** As the PresenceOrchestrator, I want to submit screenshots and camera frames to a local
vision model and receive semantic descriptions, so that Lucia understands visual context without cloud services.

#### Acceptance Criteria

1. THE VisionBackend SHALL load Qwen2.5-VL-3B GGUF via `llama_cpp.Llama` with a `Qwen2VLChatHandler(clip_model_path=mmproj_path)`, using configurable `vision_model_path`, `vision_mmproj_path`, `vision_n_gpu_layers` (default 28, range [0,99]), and `vision_n_ctx` (default 4096, range [512,8192]).
2. THE VisionBackend SHALL expose `describe(image: PIL.Image.Image, prompt: str, max_tokens: int = 256) -> str` that encodes the image as a base64 PNG data URL, submits it via `create_chat_completion`, and returns the model's text response.
3. THE VisionBackend SHALL expose `ground(image: PIL.Image.Image, target: str) -> tuple[int, int] | None` that prompts the model for pixel coordinates of `target`; parses a `(x, y)` pair via regex; returns None if parsing fails.
4. IF `vision_model_path` or `vision_mmproj_path` are missing at init, THE VisionBackend SHALL raise `FileNotFoundError` identifying the missing file.
5. IF `describe()` does not receive a response within `vision_timeout_seconds` (default 30, range [5,120]), THE VisionBackend SHALL return `""` and log a timeout warning.
6. THE VisionBackend SHALL use a separate `llama_cpp.Llama` instance from `LLMBackend`; they SHALL NOT share instances.
7. THE VisionBackend SHALL expose `is_ready() -> bool` and `shutdown()` (releases the Llama instance).
8. IF total GPU VRAM usage exceeds 3.2 GB (detected via `pynvml` or nvidia-smi poll), THE VisionBackend SHALL log a warning and reduce `n_gpu_layers` to 0 (CPU fallback) for subsequent calls.

---

### Requirement 2: Screen Observer

**User Story:** As the PresenceOrchestrator, I want screenshots captured automatically with change detection,
so that VisionBackend is only called when the screen meaningfully changes.

#### Acceptance Criteria

1. THE ScreenObserver SHALL capture full-screen screenshots with `mss` at a configurable interval: `passive_interval_seconds` (default 5.0, range [1.0,60.0]) in WATCH/ASSIST mode; `active_interval_seconds` (default 0.5, range [0.1,5.0]) in ACTIVE mode.
2. THE ScreenObserver SHALL compute mean absolute pixel difference (grayscale numpy arrays) between consecutive frames; IF difference > `change_threshold` (default 0.05, range [0.0,1.0]), enqueue frame for VisionBackend processing.
3. IF no significant change has occurred for > `stale_timeout_seconds` (default 30.0), THE ScreenObserver SHALL enqueue the current frame regardless of pixel difference.
4. THE ScreenObserver SHALL expose `get_latest_context() -> ScreenContext | None` returning the most recent VisionBackend result without blocking.
5. THE ScreenObserver SHALL run in a daemon thread named `"ScreenObserver"` and SHALL NOT block the conversation pipeline.
6. THE ScreenObserver SHALL read the focused window's process name and title (via `psutil` + Windows API) and include them in each ScreenContext.
7. THE ScreenObserver SHALL expose `start()`, `stop()`, `is_alive() -> bool`.

---

### Requirement 3: Camera Observer

**User Story:** As the user, I want Lucia to optionally observe me via webcam to inform her emotional
responses with my real-world state.

#### Acceptance Criteria

1. THE CameraObserver SHALL be disabled by default; it activates only via explicit user action.
2. WHEN enabled, THE CameraObserver SHALL capture one frame via `cv2.VideoCapture(0)` every `camera_interval_seconds` (default 10.0, range [2.0,60.0]).
3. Captured frames SHALL be passed to VisionBackend with the prompt: "Describe the person in this image. Note their apparent mood, energy level, focus, and physical environment."
4. IF no webcam is found at enable time, THE CameraObserver SHALL log an error, remain disabled, and dispatch `camera:error` IPC; it SHALL NOT raise an exception.
5. THE CameraObserver SHALL release `cv2.VideoCapture` on `stop()`.
6. THE CameraObserver SHALL dispatch `camera:active {capturing: bool}` IPC to the renderer.

---

### Requirement 4: Screen Context — Pipeline Integration

**User Story:** As Lucia, I want to reference what I see on screen in conversation and react to it emotionally.

#### Acceptance Criteria

1. THE `PresenceOrchestrator.process()` SHALL inject a `[SCREEN CONTEXT]` section into the assembled prompt (when `screen_awareness_enabled=True` and ScreenContext is available) containing `app`, `title`, and `description` fields.
2. THE ScreenContext description SHALL be appended to the user's input text fed into `StimulusProcessor.encode()`, allowing screen content to influence PAD state.
3. WHEN a significant screen change triggers a new ScreenContext while ControlState is WATCH or ASSIST, AND at least `min_comment_interval_seconds` (default 15.0) has elapsed since the last ObservationComment, THE PresenceOrchestrator SHALL generate an ObservationComment via `LLMBackend.generate()` with a presence-specific natural-language prompt.
4. THE ObservationComment SHALL pass through `BoundaryLayer.validate()` before being dispatched to the renderer as `presence:comment` IPC.
5. THE `[SCREEN CONTEXT]` section SHALL NOT contain any of the 8 Phase 2 forbidden recall phrases; `PromptAssembler` SHALL validate this with the same check applied to echo sections.

---

### Requirement 5: UI Grounding

**User Story:** As the ReactLoop, I want to find the screen location of a described UI element so
Lucia can interact with it without hardcoded coordinates.

#### Acceptance Criteria

1. THE `UIGrounding.locate(target: str, screenshot: PIL.Image.Image) -> tuple[int, int] | None` SHALL first query Windows UIA via `comtypes` for an element whose Name, AutomationId, or LocalizedControlType contains `target` (case-insensitive); IF found, return the center of its BoundingRectangle.
2. IF UIA fails, THE UIGrounding SHALL fall back to `VisionBackend.ground(screenshot, target)`.
3. IF both fail, THE UIGrounding SHALL return None.
4. Returned coordinates SHALL be verified to lie within screen bounds; IF out of bounds, return None.
5. THE UIGrounding SHALL cache the UIA element tree for the focused window for up to `uia_cache_ttl_seconds` (default 1.0).

---

### Requirement 6: Action Executor

**User Story:** As the ReactLoop, I want to execute typed ActionTokens as real desktop inputs,
with configurable pacing and mandatory safety pre-checks before every action.

#### Acceptance Criteria

1. THE ActionExecutor SHALL support: `click(x,y,button)`, `double_click(x,y)`, `right_click(x,y)`, `drag(x1,y1,x2,y2)`, `scroll(x,y,amount)`, `type(text)`, `hotkey(*keys)`, `key_press(key)`, `focus_window(title_pattern)`, `wait(seconds, max=10.0)`, `observe()`.
2. BEFORE any action, THE ActionExecutor SHALL call `SafetyGuard.is_permitted()` and raise `ActionBlockedError` if it returns False.
3. THE ActionExecutor SHALL use `pyautogui` with `pyautogui.FAILSAFE = True` (set at module import).
4. A minimum inter-action delay of `min_action_delay_ms` (default 200, range [50,2000]) SHALL be enforced.
5. The `type()` action SHALL use a per-character delay of `typing_delay_ms` (default 50, range [10,500]).
6. THE ActionExecutor SHALL log every action attempt: timestamp, action_type, parameters, outcome.
7. IF `pyautogui.FailSafeException` is raised, THE ActionExecutor SHALL re-raise it as `EmergencyStopError`.

---

### Requirement 7: Safety Guard and Control State

**User Story:** As the user, I want complete confidence that Lucia cannot act on my computer without
explicit permission, that I can stop her instantly at any moment, and that she will never touch
sensitive applications.

#### Acceptance Criteria

1. THE SafetyGuard SHALL maintain ControlState with valid transitions: IDLE->WATCH, WATCH->ASSIST, WATCH/ASSIST->ACTIVE, ACTIVE->WATCH, ANY->IDLE.
2. THE ActionExecutor SHALL only execute actions when ControlState == ACTIVE; all other states raise ActionBlockedError.
3. THE EmergencyStop hotkey (default `Ctrl+Shift+Space`) SHALL be registered via `pynput.keyboard.GlobalHotKeys` in a dedicated daemon thread named `"EmergencyStop-Listener"` started INSIDE `SafetyGuard.__init__()`.
4. THE EmergencyStop listener SHALL be started as the FIRST Phase 5 component and remain alive for the entire application session.
5. THE `_stop_event` (threading.Event) SHALL be checked at the START of every ActionExecutor action call BEFORE any input is sent.
6. WHEN EmergencyStop triggers: set `_stop_event`, set ControlState to WATCH, dispatch `presence:emergency-stop` IPC.
7. `SafetyGuard.is_permitted()` SHALL check in order: (a) _stop_event not set, (b) ControlState == ACTIVE, (c) focused window does not match ForbiddenZone, (d) rate limit not exceeded.
8. DEFAULT ForbiddenZones (process name patterns, case-insensitive): `*keepass*`, `*bitwarden*`, `*1password*`, `*lastpass*`, `*dashlane*`. DEFAULT ForbiddenZones (window title patterns): `*Task Manager*`, `*Windows Security*`, `*Windows Defender*`, `*Sign in*`.
9. Rate limit: `max_actions_per_minute` (default 30, range [1,120]); rolling 60-second window; exceeded -> return False with `"rate_limit_exceeded"`.
10. WHEN ControlState becomes ACTIVE, dispatch `presence:control-state {active: true}` IPC. WHEN leaving ACTIVE, dispatch `{active: false}`.
11. WHEN a ForbiddenZone window is focused while ControlState is ACTIVE, auto-transition to WATCH and log `forbidden_zone_intervention`.

---

### Requirement 8: ReAct Loop

**User Story:** As the user, I want to ask Lucia to perform a multi-step desktop task and have her
execute it step-by-step while telling me what she's doing.

#### Acceptance Criteria

1. WHEN `PresenceOrchestrator.start_task(command: str)` is called, a ReactLoop SHALL start in a background thread; a `task_id` (UUID hex) SHALL be returned immediately.
2. THE ReactLoop SHALL execute: **Observe** (get ScreenContext), **Think** (LLM generates ActionToken JSON + narration), **Act** (execute ActionToken), **Verify** (new ScreenContext; check for `done` token).
3. THE Think step SHALL prompt the LLM to output a JSON action on the FIRST line, then natural narration on the NEXT line; these are split by line, not regex.
4. Each narration SHALL be dispatched as `presence:comment` IPC with `{task_id, step, text}`.
5. THE ReactLoop SHALL enforce `max_react_steps` (default 20, range [3,100]); on exceed, dispatch step-limit narration.
6. THE user MAY interrupt via `PresenceOrchestrator.stop_task()`; the loop stops after the current action completes; dispatches `"Okay, I've stopped."` narration.
7. IF EmergencyStop triggers during ReactLoop, loop halts immediately after current action raises `EmergencyStopError`; dispatches `"Emergency stop - I've stepped back."` narration.
8. THE `action_history` (last 5 steps) SHALL be included in each Think prompt to prevent repeating failed actions.
9. THE ReactLoop thread SHALL NOT block `POST /process` conversation requests.

---

### Requirement 9: Experience Modes

**User Story:** As the user, I want to choose how Lucia is present so we can watch, play, and work together.

#### Acceptance Criteria

1. **IDLE**: No screen capture, no camera, no comments. Identical to Phase 1-4 behavior.
2. **WATCH**: ScreenObserver runs; ObservationComments generated on significant changes; NO desktop actions.
3. **ASSIST**: Same as WATCH plus Lucia can answer screen-specific questions using live ScreenContext; NO desktop actions.
4. **ACTIVE**: Full agency. ReactLoop can execute. "Lucia is in control" overlay shown.
5. Modes SHALL be settable from Electron UI buttons AND natural-language commands recognized by a keyword classifier (no LLM call):
   - WATCH: `"watch"`, `"observe"`, `"pay attention"`, `"look at what i'm doing"`
   - ASSIST: `"help me"`, `"assist me"`, `"what is"`, `"can you see"`
   - ACTIVE: `"take over"`, `"you do it"`, `"go ahead"`, `"you control"`
   - IDLE: `"stop watching"`, `"stop"`, `"go away"`, `"disable"`
6. ObservationComments SHALL be in Lucia's natural voice (curious, emotionally present, playful) not robotic screen-reader output.

---

### Requirement 10: Presence API Endpoints

**User Story:** As the Electron UI, I want API endpoints to control Lucia's presence, query status,
trigger tasks, and manage the camera.

#### Acceptance Criteria

1. `POST /presence/mode` — body `{"mode": "idle"|"watch"|"assist"|"active"}` — sets ControlState; returns `{"mode": str, "ok": bool}`.
2. `POST /presence/act` — body `{"command": str}` — starts ReactLoop task; returns `{"task_id": str}`; 409 if task already active.
3. `POST /presence/stop-task` — halts active ReactLoop; returns `{"ok": bool}`.
4. `POST /presence/emergency-stop` — software equivalent of hotkey; transitions to WATCH.
5. `POST /presence/camera` — body `{"enabled": bool}` — enables/disables camera.
6. `GET /presence/status` — returns `{"mode": str, "screen_context": ScreenContext|null, "camera_enabled": bool, "task_active": bool, "task_id": str|null, "last_comment": str|null}`.
7. `GET /state` (Phase 3 endpoint) SHALL be extended with `"presence": {"mode": str, "task_active": bool}`.

---

### Requirement 11: Resource Budget

**User Story:** As a developer on RTX 3050 Ti (4 GB VRAM), I want Phase 5 to stay within resource limits
so the conversation pipeline remains responsive.

#### Acceptance Criteria

1. Qwen2.5-VL 3B Q4_K_M at `n_gpu_layers=28` SHALL use no more than 2.0 GB VRAM. Combined with LFM2.5-1.2B (~1.2 GB), total SHALL remain under 3.5 GB.
2. ScreenObserver pixel-difference computation SHALL complete within 50 ms per frame on CPU.
3. ONE `VisionBackend.describe()` call SHALL complete within 30 seconds.
4. `mss` screenshot capture SHALL complete within 100 ms per frame.
5. CameraObserver SHALL release `cv2.VideoCapture` on stop().
6. ReactLoop thread SHALL NOT block `POST /process`; conversation and ReactLoop run concurrently.
