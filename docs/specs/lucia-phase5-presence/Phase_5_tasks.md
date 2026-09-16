# Implementation Plan: Lucia Embodied Desktop Presence (Phase 5)

## Overview

Phase 5 introduces Perception (VisionBackend, ScreenObserver, CameraObserver) and Agency
(UIGrounding, ActionExecutor, SafetyGuard, ReactLoop) coordinated by PresenceOrchestrator.

The ONLY change to existing Phase 1-4 code: add `screen_context=None` optional kwarg
to `PromptAssembler.assemble()` (backward compatible -- existing tests unaffected).

New Python dependencies: `mss`, `pyautogui`, `pynput`, `psutil`, `opencv-python`, `comtypes`, `pynvml`.
New Electron dependencies: `pixi.js`, `pixi-live2d-display` (for avatar in Phase 3.5).
Tasks marked `*` are optional for MVP.

---

## Tasks

- [ ] 1. Scaffolding and dependencies
  - Create `src/core/perception/__init__.py`, `src/core/agency/__init__.py`, `src/core/presence/__init__.py`
  - Create stub source files for all new modules
  - Create `src/core/agency/errors.py`: `ActionBlockedError(Exception)`, `EmergencyStopError(Exception)`
  - Create `src/core/agency/action_token.py`: `ActionToken` dataclass with all action fields optional
  - Add to `requirements.txt`: `mss>=9.0`, `pyautogui>=0.9`, `pynput>=1.7`, `psutil>=5.9`, `opencv-python>=4.8`, `comtypes>=1.4`, `pynvml>=11.5`
  - Create test stub files for each new module
  - Download `Qwen2.5-VL-3B-Instruct-Q4_K_M.gguf` and `qwen2vl-3b-mmproj.gguf` to `models/`; add paths to `config/ui.json`
  - _Requirements: 1.1, 1.6, 11.1_

- [ ] 2. VisionBackend
  - [ ] 2.1 Implement `VisionBackend.__init__()` in `src/core/perception/vision_backend.py`
    - Validate both model paths exist; raise `FileNotFoundError` identifying missing file
    - Create `Qwen2VLChatHandler` + `Llama` instance with config params
    - Create internal `ThreadPoolExecutor(max_workers=1)` for timeout-safe calls
    - Expose `is_ready() -> bool`, `shutdown()` (releases Llama)
    - _Requirements: 1.1, 1.4, 1.6, 1.7_
  - [ ] 2.2 Implement `VisionBackend.describe()` and `VisionBackend.ground()`
    - `describe()`: encode PIL.Image to data URL; `create_chat_completion` via executor with `result(timeout=vision_timeout_seconds)`; return text or `""` on timeout/error
    - `ground()`: call describe() with coordinate-extraction prompt; parse `(x, y)` via `re.search`; return tuple or None
    - _Requirements: 1.2, 1.3, 1.5_
  - [ ]* 2.3 Write unit tests `tests/unit/test_vision_backend.py`
    - Missing model_path -> FileNotFoundError; missing mmproj_path -> FileNotFoundError
    - Mock Llama.create_chat_completion returning text -> describe() returns that text
    - Mock returning "(523, 145)" -> ground() returns (523, 145)
    - Mock returning "no coordinates" -> ground() returns None
    - Timeout (mock delays > vision_timeout_seconds) -> describe() returns "" / ground() returns None
    - _Requirements: 1.2-1.5_

- [ ] 3. Screen and Camera Observation
  - [ ] 3.1 Implement `src/platform/screen.py`
    - `get_focused_window() -> tuple[str, str]`: use `win32gui.GetForegroundWindow()`, `win32gui.GetWindowText()`, `win32process.GetWindowThreadProcessId()`, `psutil.Process()` to return (process_name, window_title)
    - Return ("", "") on any Win32 or psutil error
    - _Requirements: 2.6_
  - [ ] 3.2 Implement `ScreenObserver` in `src/core/perception/screen_observer.py`
    - `__init__()`: validate config; init `_stop: threading.Event`, `_lock: threading.Lock`, `_latest: ScreenContext|None`, `_prev: np.ndarray|None`
    - `_capture_loop()`: mss capture loop; grayscale diff; stale timeout; VisionBackend.describe() on change; store ScreenContext under lock
    - `_interval()`: returns `passive_interval_seconds` or `active_interval_seconds` based on current ControlState (provided via callback)
    - `start()`, `stop()`, `is_alive()`, `get_latest_context()` (lock-guarded, non-blocking)
    - _Requirements: 2.1-2.7_
  - [ ] 3.3 Implement `CameraObserver` in `src/core/perception/camera_observer.py`
    - `enable()`: open cv2.VideoCapture(0); dispatch camera:active IPC; start capture thread; return False if not opened
    - `disable()` / `stop()`: release VideoCapture; stop thread; dispatch camera:active {capturing: false}
    - Capture loop: read frame every camera_interval_seconds; VisionBackend.describe() with user-state prompt; store CameraContext
    - _Requirements: 3.1-3.6_
  - [ ]* 3.4 Write unit tests `tests/unit/test_screen_observer.py`
    - `get_latest_context()` returns None before first capture
    - Mock mss + VisionBackend -> after one loop tick, `get_latest_context()` returns ScreenContext with correct fields
    - Two identical frames -> describe() NOT called (below threshold); after stale_timeout, describe() IS called
    - `stop()` terminates thread within 2s
    - _Requirements: 2.1-2.5_

- [ ] 4. Safety Guard -- EmergencyStop FIRST
  - [ ] 4.1 Implement `SafetyGuard.__init__()` and EmergencyStop in `src/core/agency/safety_guard.py`
    - Start `pynput.keyboard.GlobalHotKeys` daemon thread `"EmergencyStop-Listener"` INSIDE `__init__()` before returning
    - `_on_emergency_stop()`: set `_stop_event`; call `set_state(WATCH)`; invoke `_on_state_change` callback
    - `set_state()`: validate transition; acquire lock; set; clear `_stop_event` when transitioning to ACTIVE; invoke callback
    - `state` property: returns current ControlState (lock-guarded)
    - _Requirements: 7.3, 7.4, 7.6_
  - [ ] 4.2 Implement `SafetyGuard.is_permitted()` and ForbiddenZone checks
    - Check order: (a) _stop_event, (b) ControlState == ACTIVE, (c) rate limit, (d) ForbiddenZone
    - ForbiddenZone auto-transitions to WATCH and logs `forbidden_zone_intervention`
    - Rate limit: rolling 60s deque; `max_actions_per_minute` threshold
    - Returns `(bool, reason_str)` tuple
    - _Requirements: 7.7-7.11_
  - [ ]* 4.3 Write unit tests `tests/unit/test_safety_guard.py`
    - is_permitted() returns (False, "control_state_is_watch") when ControlState is WATCH
    - is_permitted() returns (False, "emergency_stop_active") when _stop_event is set
    - ForbiddenZone match -> (False, "forbidden_zone"); ControlState auto-transitions to WATCH
    - Rate limit exceeded -> (False, "rate_limit_exceeded")
    - Mock hotkey trigger -> _stop_event set, state == WATCH
    - clear via set_state(ACTIVE) -> _stop_event cleared -> is_permitted() returns (True, "ok")
    - _Requirements: 7.1-7.11_

- [ ] 5. Action Executor and UI Grounding
  - [ ] 5.1 Implement `ActionExecutor.execute()` in `src/core/agency/action_executor.py`
    - `import pyautogui; pyautogui.FAILSAFE = True` at module top (not in __init__)
    - `execute(token, guard)`: call guard.is_permitted(); raise ActionBlockedError if False; dispatch via match/case; catch FailSafeException -> raise EmergencyStopError; enforce min_action_delay in finally; log every action
    - _Requirements: 6.1-6.7_
  - [ ] 5.2 Implement `UIGrounding.locate()` in `src/core/agency/ui_grounding.py`
    - Try UIA via comtypes: `IUIAutomation.ElementFromHandle(foreground_window)` -> walk tree -> substring match name/automationId -> center of BoundingRectangle
    - On failure: VisionBackend.ground(screenshot, target)
    - On both fail: return None
    - Validate coords within screen bounds
    - Cache UIA result for uia_cache_ttl_seconds (1.0s default)
    - _Requirements: 5.1-5.5_
  - [ ]* 5.3 Write unit tests `tests/unit/test_action_executor.py`
    - Mock is_permitted() returning (False, "blocked") -> ActionBlockedError raised; pyautogui NOT called
    - Mock pyautogui.click -> verify called with correct (x, y, button)
    - Mock pyautogui.FailSafeException -> EmergencyStopError raised
    - Verify min_action_delay_ms enforced (mock time.sleep, assert called with value >= min/1000)
    - type action: mock pyautogui.typewrite; verify interval=typing_delay_ms/1000.0
    - _Requirements: 6.1-6.7_

- [ ] 6. Checkpoint -- safety and action layer
  - Run `pytest tests/unit/test_safety_guard.py tests/unit/test_action_executor.py --tb=short`
  - All non-skipped tests pass
  - Manually verify: SafetyGuard init -> "EmergencyStop-Listener" thread visible in thread list
  - Ask the user if any questions arise

- [ ] 7. ReactLoop
  - [ ] 7.1 Implement `ReactLoop.run()` in `src/core/agency/react_loop.py`
    - Define THINK_SYSTEM constant (the action-generation system prompt)
    - Loop: check _interrupt_event; OBSERVE (get_latest_context); THINK (llm.generate_with_system); parse line 1 = JSON, rest = narration; on_narration(narration); check "done"; ACT (executor.execute); catch ActionBlockedError/EmergencyStopError
    - Maintain action_history list (last 5 as JSON in prompt)
    - max_steps enforcement with step-limit narration
    - `stop()`: set `_interrupt_event`; loop exits after current action
    - _Requirements: 8.1-8.9_
  - [ ]* 7.2 Write unit tests `tests/unit/test_react_loop.py`
    - Mock LLM returning done token on step 1 -> loop terminates; on_narration called once
    - Mock LLM returning click action -> executor.execute called with correct token
    - stop() during loop -> exits after current action; on_narration("Okay, I've stopped.") called
    - ActionBlockedError from executor -> loop terminates; narration contains "blocked"
    - max_steps exceeded -> step-limit narration emitted
    - _Requirements: 8.1-8.9_

- [ ] 8. PresenceOrchestrator and PromptAssembler extension
  - [ ] 8.1 Extend `PromptAssembler.assemble()` in `src/core/orchestrator/prompt_assembler.py`
    - Add `screen_context=None` keyword-only parameter (backward compatible default)
    - IF not None: build [SCREEN CONTEXT] section; validate no-recall (same 8-phrase check); insert after [SOMATIC STATE]
    - _Requirements: 4.1, 4.5_
  - [ ] 8.2 Implement `PresenceOrchestrator.__init__()` in `src/core/presence/orchestrator.py`
    - Validate all Phase 5 config fields; raise ValueError for invalid/missing
    - call super().__init__(config) (Phase 2 init)
    - Instantiate SafetyGuard FIRST (starts EmergencyStop listener)
    - Instantiate VisionBackend (in background thread for async load)
    - Instantiate ScreenObserver, CameraObserver, ActionExecutor, UIGrounding, ReactLoop
    - _Requirements: 7.3, 7.4_
  - [ ] 8.3 Implement `PresenceOrchestrator.process()` in `src/core/presence/orchestrator.py`
    - Keyword classifier for mode-switch commands (no LLM call); return mode confirmation if matched
    - Augment input_text with screen context for StimulusProcessor.encode()
    - Pass screen_context=self._screen_obs.get_latest_context() to super()._process_with_screen_context()
    - Check if screen change warrants ObservationComment (time-gated, WATCH/ASSIST mode only)
    - _Requirements: 4.1, 4.2, 4.3, 9.1-9.6_
  - [ ] 8.4 Implement lifecycle methods in `src/core/presence/orchestrator.py`
    - `set_mode(mode)`: SafetyGuard.set_state(); start/stop ScreenObserver; dispatch IPC callback
    - `start_task(command)`: raise RuntimeError if task active; set ACTIVE; start task thread
    - `stop_task()`: ReactLoop.stop(); join with timeout=10s; set WATCH
    - `shutdown()`: stop ReactLoop, ScreenObserver, CameraObserver, VisionBackend; super().shutdown()
    - _Requirements: 8.1, 8.6, 9.5, 10.1-10.7_
  - [ ]* 8.5 Write unit tests `tests/unit/test_presence_orchestrator.py`
    - Mode-switch command -> set_mode() called; response is mode confirmation
    - process() with ScreenContext -> prompt contains [SCREEN CONTEXT]
    - [SCREEN CONTEXT] section fails no-recall validation -> AssemblyError (not raised to user but logged)
    - start_task() while active -> RuntimeError
    - stop_task() -> ReactLoop.stop() called; state returns to WATCH
    - shutdown() -> all threads joined; super().shutdown() called
    - _Requirements: 8.1-8.6, 9.5_

- [ ] 9. FastAPI and Electron UI
  - [ ] 9.1 Extend `src/api/server.py`
    - Use PresenceOrchestrator instead of InstrumentedOrchestrator
    - Add all 6 presence endpoints; extend GET /state with "presence" field
    - Endpoint `POST /presence/act`: 409 if task already active
    - _Requirements: 10.1-10.7_
  - [ ] 9.2 Extend `electron/main/ipc-bridge.js` with presence channels
    - Outbound handlers: presence:mode, presence:act, presence:stop-task, presence:emergency-stop, presence:camera
    - Inbound push (from Python stdout/IPC): presence:comment, presence:control-state, presence:emergency-stop, camera:active, camera:error
    - _Requirements: 10.1-10.7_
  - [ ] 9.3 Create `electron/renderer/presence/presence.js` + `presence.css`
    - Mode toggle buttons (IDLE / WATCH / ASSIST / ACTIVE) with active state styling
    - Task input field + "Do it!" button
    - Narration feed: scrolling list; listen presence:comment IPC -> append with step number
    - Camera toggle button; listen camera:active / camera:error
    - _Requirements: 9.5_
  - [ ] 9.4 Create `electron/renderer/presence/control-overlay.js`
    - Fixed red banner at z-index:9999 when presence:control-state {active:true} received
    - "Take Back Control" button: calls window.lucia.presence.stopTask() + setMode("watch")
    - Pulsing dot animation; banner dismissed on {active:false} or presence:emergency-stop
    - _Requirements: 7.10_

- [ ] 10. Checkpoint -- full presence pipeline
  - Run `pytest tests/unit tests/property --tb=short`
  - Manual: enable WATCH, open browser -> verify ObservationComment appears in ~30s
  - Manual safety: enable ACTIVE, start task, trigger Ctrl+Shift+Space -> overlay dismisses immediately
  - Check VRAM: `nvidia-smi` shows combined usage < 3.5 GB with both models loaded
  - Ask the user if any questions arise

- [ ]* 11. Integration tests `tests/integration/test_presence_integration.py`
  - VisionBackend.describe() returns non-empty string for a test screenshot (requires model)
  - ScreenObserver produces ScreenContext within 60s of start
  - SafetyGuard blocks ActionExecutor when ControlState is WATCH (no model needed)
  - ReactLoop completes a simple "open Notepad" task end-to-end (requires ACTIVE + real system)
  - _Requirements: 1.2, 2.4, 7.2, 8.2_

- [ ] 12. Final checkpoint
  - `pytest tests/ --tb=short`
  - All non-skipped tests pass
  - VRAM < 3.5 GB confirmed
  - Ask the user if any questions arise

---

## Task Dependency Graph

```json
{
  "waves": [
    {"id": 0, "tasks": ["1"]},
    {"id": 1, "tasks": ["2.1", "3.1", "4.1"]},
    {"id": 2, "tasks": ["2.2", "3.2", "4.2"]},
    {"id": 3, "tasks": ["2.3", "3.3", "3.4", "4.3", "5.1", "5.2"]},
    {"id": 4, "tasks": ["5.3", "6"]},
    {"id": 5, "tasks": ["7.1", "8.1"]},
    {"id": 6, "tasks": ["7.2", "8.2"]},
    {"id": 7, "tasks": ["8.3", "8.4"]},
    {"id": 8, "tasks": ["8.5", "9.1", "9.2"]},
    {"id": 9, "tasks": ["9.3", "9.4", "10"]},
    {"id": 10, "tasks": ["11", "12"]}
  ]
}
```

## Notes

- `pyautogui.FAILSAFE = True` is set at MODULE IMPORT in action_executor.py, not in __init__.
  This guarantees it is always active regardless of configuration.
- EmergencyStop `_stop_event` is cleared ONLY when the user explicitly transitions to ACTIVE.
  This prevents any accidental re-enabling by code logic.
- VisionBackend loads asynchronously -- the chat interface is usable before vision is ready.
- `comtypes` is available on Windows without pip install on Python 3.12 (bundled).
  If not present: `pip install comtypes`.
- `mss` is 3-5x faster than PIL.ImageGrab on Windows and is preferred.
- The [SCREEN CONTEXT] PromptAssembler change defaults to None, keeping all Phase 1-4
  tests completely unaffected.
- action_history is capped at last 5 steps in Think prompts to stay within n_ctx budget.
