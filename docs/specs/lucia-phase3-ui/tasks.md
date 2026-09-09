# Implementation Plan: Lucia UI Phase 3

## Overview

Build the Electron desktop chat UI that wraps the Phase 1+2 Python pipeline. Three tracks run in parallel after the scaffolding wave:

- **Track A — Python API**: `src/api/server.py` (FastAPI + InstrumentedOrchestrator)
- **Track B — Electron main process**: `Process_Manager` + `IPC_Bridge` + `main.js`
- **Track C — Electron renderer**: `Chat_Window` + `Emotion_Debug_Panel` + `preload.js`

All unit tests mock the FastAPI server via `nock` or `msw` (Node); no real Python process is started in unit tests. Integration tests use a real Python subprocess (requires `LUCIA_MODEL_PATH`).

---

## Tasks

- [ ] 1. Project scaffolding
  - Create `src/api/__init__.py` (already exists as empty stub — verify)
  - Create `electron/` directory tree: `main/`, `preload/`, `renderer/chat/`, `renderer/debug/`
  - Create `electron/package.json` with dependencies: `electron`, `electron-builder`; devDependencies: none required for unit tests
  - Create `config/ui.json` with defaults: `port=8765`, `model_path=""`, `n_gpu_layers=32`, `log_level="INFO"`
  - Add `fastapi`, `uvicorn[standard]` to `requirements.txt` (or `pyproject.toml` if used)
  - _Requirements: 3.3, 3.4, 9.1_

- [ ] 2. FastAPI server — skeleton and lifecycle
  - [ ] 2.1 Implement `src/api/server.py` module-level state, `ProcessRequest` Pydantic model, `_parse_args()`, `_build_config()`, `InstrumentedOrchestrator` subclass
    - `_parse_args()`: argparse with `--port` (default 8765), `--model-path`, `--log-level` (default INFO)
    - `_build_config(args)`: read env vars `LUCIA_PORT` and `LUCIA_MODEL_PATH` as fallbacks; validate port in [1024, 65535] or emit `LUCIA_BACKEND_ERROR: invalid_port`; validate model_path non-empty or emit `LUCIA_BACKEND_ERROR: model_path_not_configured`
    - `InstrumentedOrchestrator.process()`: call `super().process()`; update `_last_somatic` and `_last_constraints` from homeostatic engine; return result
    - `main()`: init orchestrator; print `LUCIA_BACKEND_READY`; install SIGTERM/SIGINT handlers; `uvicorn.run(app, host="127.0.0.1", ...)`
    - _Requirements: 3.1, 3.2, 3.3, 3.4, 3.5, 3.6, 9.3_
  - [ ] 2.2 Implement `POST /process` endpoint
    - Validate input: 422 for missing/non-string `input`; 422 for empty or >4000 chars
    - 503 when `_orchestrator._degraded`; 500 on unhandled exception
    - Use `loop.run_in_executor(None, _orchestrator.process, req.input)` to avoid blocking uvicorn event loop
    - Return `{"response": str, "call_id": uuid_hex}`
    - _Requirements: 1.1–1.8_
  - [ ] 2.3 Implement `GET /state` and `GET /health` endpoints
    - `GET /state`: read PAD from `EmotionCore.get_pad_state()`; read `_last_somatic`/`_last_constraints` (default zeros if None); read `len(_affective_memory._index)`; include `Cache-Control: no-store`
    - `GET /health`: return `{"status": "ok"}` / `{"status": "degraded"}` with appropriate HTTP codes
    - _Requirements: 2.1–2.7, 3.7_
  - [ ]* 2.4 Write unit tests for `src/api/server.py` using `httpx.AsyncClient` + `TestClient` (FastAPI test utilities)
    - `POST /process` with missing `input` → 422
    - `POST /process` with `input` > 4000 chars → 422
    - `POST /process` when `_orchestrator._degraded = True` → 503
    - `GET /state` before any `process()` call → all somatic fields 0.0, `memory_trace_count: 0`
    - `GET /state` after mock `process()` stores somatic → correct somatic values reflected
    - `GET /health` returns 200 when healthy, 503 when degraded
    - `GET /state` returns `Cache-Control: no-store` header
    - _Requirements: 1.3–1.6, 2.1–2.5, 2.7, 3.7_

- [ ] 3. Electron main process — Process_Manager
  - [ ] 3.1 Implement `electron/main/process-manager.js` with `ProcessManager` class
    - `start()`: spawn `python -m src.api.server --port ... --model-path ...` with `detached: false, stdio: ['pipe','pipe','pipe']`
    - Monitor stdout for `LUCIA_BACKEND_READY` (dispatch `backend:ready`) and `LUCIA_BACKEND_ERROR: *` (dispatch `backend:error`); set 60 s startup timeout
    - `stop()`: send SIGTERM, wait up to 10 s, then SIGKILL; return Promise
    - `_dispatch(channel, payload)`: send to mainWindow via `webContents.send`; guard for destroyed window
    - Idempotence: once `_ready = true`, additional `LUCIA_BACKEND_READY` lines are no-ops
    - _Requirements: 4.1–4.8_
  - [ ]* 3.2 Write unit tests for `ProcessManager` using jest + sinon stubs
    - Stub `child_process.spawn`; emit `LUCIA_BACKEND_READY` on mocked stdout → `backend:ready` dispatched
    - Emit `LUCIA_BACKEND_ERROR: some_reason` → `backend:error` dispatched with `{code: 'some_reason'}`
    - No `LUCIA_BACKEND_READY` within 60 s → `backend:error` with `{code: 'startup_timeout'}`; process killed
    - Unexpected exit with code 1 → `backend:error` with `{code: 'process_exited', exitCode: 1}`
    - `stop()`: sends SIGTERM; resolves within 10 s
    - Second `LUCIA_BACKEND_READY` is a no-op (dispatches nothing)
    - _Requirements: 4.3–4.7_

- [ ] 4. Electron main process — IPC_Bridge
  - [ ] 4.1 Implement `electron/main/ipc-bridge.js` with `registerHandlers(port)` function
    - `chat:send` handler: await `_pendingChat` to serialize; fetch `POST /process`; set `AbortSignal.timeout(35_000)`; on HTTP error throw `{code, message}`; resolve/finally to release pending lock
    - `state:get` handler: fetch `GET /state` with `AbortSignal.timeout(2_000)`; return JSON; throw `{code: 'state_error', message}` on failure
    - _Requirements: 5.1–5.6_
  - [ ]* 4.2 Write unit tests for IPC_Bridge using jest + nock (HTTP mocking)
    - Successful `chat:send` → returns `{response, call_id}` matching mock response
    - HTTP 503 from `/process` → rejects with `{code: 'orchestrator_degraded'}`
    - Two concurrent `chat:send` calls → second is queued and executed after first resolves; only one in-flight HTTP request at a time
    - `state:get` timeout (server delayed >2 s) → rejects with `{code: 'state_error'}`
    - Two concurrent `state:get` calls → both resolve independently (no serialization)
    - _Requirements: 5.1–5.6_

- [ ] 5. Electron preload and main window
  - [ ] 5.1 Implement `electron/preload/preload.js`
    - `contextBridge.exposeInMainWorld('lucia', {chat: {send}, state: {get}, on})`
    - `on()` allowlist: `['backend:ready', 'backend:error']` only
    - No `require`, `process`, `eval` exposed
    - _Requirements: 5.3, 10.1, 10.4_
  - [ ] 5.2 Implement `electron/main/main.js`
    - `BrowserWindow`: `width: 1200, height: 750, minWidth: 800, minHeight: 500, autoHideMenuBar: true, webPreferences: {nodeIntegration: false, contextIsolation: true, preload: '...'}`
    - Load `config/ui.json` (default values if missing; dispatch `backend:error` if `model_path` empty)
    - Restore window state from `config/window-state.json`; validate on-screen bounds
    - Instantiate `ProcessManager` and call `.start()` after `app.ready`
    - Register IPC handlers via `registerHandlers(config.port)`
    - On `app.before-quit`: call `processManager.stop()`, save window state to `config/window-state.json`
    - _Requirements: 4.1, 4.2, 8.1–8.6, 9.1, 9.2_

- [ ] 6. Electron renderer — layout and Chat_Window
  - [ ] 6.1 Create `electron/renderer/index.html`
    - Dark-mode CSS: `background: #1a1a2e`, layout: two-column flex — `#chat-pane` (flex: 7) + `#debug-pane` (flex: 3, min-width: 280px)
    - Splash screen overlay (`#splash`) shown on load, hidden on `backend:ready`
    - Include `chat/chat.js` and `debug/panel.js` as module scripts
    - CSP: `<meta http-equiv="Content-Security-Policy" content="default-src 'self'; script-src 'self'; connect-src 'none'">`
    - _Requirements: 8.1, 8.2, 8.3, 8.4, 8.7, 10.5_
  - [ ] 6.2 Implement `electron/renderer/chat/chat.js`
    - State machine: `WAITING_BACKEND | READY | SENDING | ERROR`
    - `sendMessage()`: append user bubble immediately; disable input + Send; call `window.lucia.chat.send()`; on resolve append Lucia bubble + scroll; on reject append error bubble; finally re-enable input
    - Input: Enter submits; Shift+Enter inserts newline
    - Loading indicator (CSS animated ellipsis `...`) shown while SENDING
    - Send button disabled when: SENDING, WAITING_BACKEND, or input is empty
    - Listen `window.lucia.on('backend:ready', ...)` to transition WAITING_BACKEND → READY
    - Listen `window.lucia.on('backend:error', ...)` to transition any → ERROR; show persistent error message
    - _Requirements: 6.1–6.9, 11.1, 11.2_
  - [ ]* 6.3 Write renderer unit tests for Chat_Window using jsdom + jest
    - Submitting empty input: `send()` not called
    - Submitting valid input while SENDING: queued (IPC bridge serializes, not chat.js)
    - On `backend:error` event: state becomes ERROR, input disabled, error message visible
    - Successful send: user bubble and Lucia bubble both appear in DOM; input cleared
    - Failed send: error bubble appears; input re-enabled
    - _Requirements: 6.2–6.6, 11.1, 11.2_

- [ ] 7. Electron renderer — Emotion_Debug_Panel
  - [ ] 7.1 Implement `electron/renderer/debug/panel.js`
    - `startPolling()`: `setInterval(async () => { try { const snap = await window.lucia.state.get(); renderSnapshot(snap); } catch { showStaleIndicator(); } }, 500)`
    - `renderSnapshot(snap)`: call `updatePADBar(dim, value)` for pleasure/arousal/dominance; `updateProgressBar(key, value)` for somatic markers; `updateLabel(key, value)` for constraints and `memory_trace_count`
    - `updatePADBar(dim, value)`: map `[-1, 1]` to `[0%, 100%]` center; extend fill right for positive, left for negative; CSS colors `#4caf50` / `#f44336`; CSS transition `0.3s ease-out` on width/left/background-color
    - `stopPolling()` + stale indicator on `backend:error` event
    - _Requirements: 7.1–7.8_
  - [ ] 7.2 Create `electron/renderer/debug/panel.css`
    - `.pad-bar-track`: `height: 8px`, dark background, relative positioning
    - `.pad-bar-fill`: absolute, `transition: left 0.3s ease-out, width 0.3s ease-out, background-color 0.3s ease-out`
    - `.progress-bar-track` / `.progress-bar-fill`: somatic markers (0–100%, accent color)
    - `.stale-overlay`: semi-transparent gray overlay on the panel when polling fails
    - _Requirements: 7.3–7.5, 7.8_
  - [ ]* 7.3 Write unit tests for Emotion_Debug_Panel using jsdom + jest
    - `updatePADBar('pleasure', 0.6)`: fill extends right from 50%; correct color (#4caf50)
    - `updatePADBar('arousal', -0.4)`: fill extends left; correct color (#f44336)
    - `updatePADBar('dominance', 0.0)`: fill width is 0%
    - Stale indicator shown when `state.get()` throws; values NOT reset
    - Polling stops on `backend:error` event
    - _Requirements: 7.2, 7.3, 7.6, 7.7_

- [ ] 8. Checkpoint — unit tests green
  - Run Python tests: `pytest tests/unit tests/property --tb=short` (no new Python tests needed; verifying existing tests still pass)
  - Run JS tests: `cd electron && npm test` (jest)
  - Verify: zero new test failures from Phase 3 additions
  - Ask the user if any questions arise

- [ ] 9. Integration test — end-to-end smoke (requires LUCIA_MODEL_PATH)
  - [ ] 9.1 Add `tests/integration/test_api_server_integration.py`
    - Start `InstrumentedOrchestrator` in-process (mocked LLM); start FastAPI test client
    - `POST /process` with valid input → 200, `response` non-empty, `call_id` UUID
    - `GET /state` after one `process()` call → `memory_trace_count == 1`; `pad` values in [-1, 1]
    - `GET /state` concurrent with `POST /process` (thread) → both return within respective timeouts
    - `GET /health` → 200 `{"status": "ok"}`
    - _Requirements: 1.1–1.7, 2.1–2.6, 3.7_
  - [ ] 9.2 Add Electron integration note: manual test checklist in `docs/phase3-test-checklist.md`
    - App launches; Splash_Screen shown; python process visible in Task Manager
    - `LUCIA_BACKEND_READY` appears in devtools console prefixed `[python]`
    - Splash dismissed; input field enabled; debug panel updates every ~500 ms
    - Send a message; loading indicator appears; response appears; trace count increments
    - Close app; python process terminates within 10 s

- [ ] 10. Final checkpoint
  - `pytest tests/ --tb=short` (GPU tests skip without LUCIA_MODEL_PATH)
  - `cd electron && npm test`
  - All non-skipped tests pass
  - Ask the user if any questions arise

---

## Notes

- `src/api/__init__.py` should already exist (empty) from Phase 1 scaffolding. If not, create it.
- `fastapi` and `uvicorn[standard]` must be added to the Python dependencies.
- The `InstrumentedOrchestrator` subclass lives inside `src/api/server.py`, not in `src/core/`. It is not part of the core module's public API.
- `GET /state` never calls `HomeostaticEngine.compute_somatic_markers()` directly — it reads `_last_somatic` from the cache set by `InstrumentedOrchestrator.process()`. This keeps the endpoint non-blocking.
- `electron/package.json` should set `"main": "main/main.js"` and include a `"start": "electron ."` script.
- Window state persistence writes to `config/window-state.json` which is gitignored.

## Task Dependency Graph

```json
{
  "waves": [
    {"id": 0, "tasks": ["1"]},
    {"id": 1, "tasks": ["2.1", "3.1", "5.1"]},
    {"id": 2, "tasks": ["2.2", "2.3", "3.2", "4.1", "5.2"]},
    {"id": 3, "tasks": ["2.4", "4.2", "6.1", "6.2", "7.1"]},
    {"id": 4, "tasks": ["6.3", "7.2", "7.3"]},
    {"id": 5, "tasks": ["8"]},
    {"id": 6, "tasks": ["9.1", "9.2"]},
    {"id": 7, "tasks": ["10"]}
  ]
}
```


---

## Avatar Extension (Phase 3.5)

The 2D avatar is a Live2D Cubism Web model rendered inside Electron, reacting to PAD values
from the existing 500ms GET /state polling loop. No backend changes are needed.

- [ ] A1. Avatar scaffolding
  - Add Live2D Cubism Web Framework bundles to `electron/renderer/vendor/live2d/`
    (cubism5.core.js + live2d.min.js from Cubism Web Samples, MIT non-commercial)
  - Add pixi.js v7 and pixi-live2d-display to `electron/package.json` dependencies
  - Obtain or create a .moc3 companion avatar model; place in `electron/renderer/assets/avatar/`
  - Create stub files: `electron/renderer/avatar/avatar.js`, `avatar.css`
  - _Validates: phase 3 Requirement 8.2 (layout)_

- [ ] A2. PAD-to-model parameter mapping
  - [ ] A2.1 Implement `electron/renderer/avatar/avatar.js`
    - Initialize `PIXI.Application` with transparent WebGL canvas; position over chat panel lower-left
    - Load model via `PIXI.live2d.Live2DModel.from(modelJsonPath)`
    - Implement `updateFromPAD({pleasure, arousal, dominance})`:
      - pleasure  -> ParamMouthForm (smile), ParamBrowLY/ParamBrowRY (brow angle)
      - arousal   -> idle animation speed multiplier, eye blink rate
      - dominance -> ParamAngleZ (head lean)
    - Use `model.internalModel.coreModel.setParameterValueById(id, val)` for each parameter
    - Set `canvas.style.pointerEvents = 'none'` so mouse events pass through to chat
  - [ ] A2.2 Hook into existing state polling
    - In `electron/renderer/debug/panel.js` (or a shared polling module), after `renderSnapshot(snap)`,
      call `window.avatarController.updateFromPAD(snap.pad)` if avatarController is initialized
    - No new IPC channels needed -- reuses the existing 500ms state poll
  - [ ] A2.3 Implement idle animation baseline
    - When no PAD updates received for > 2s: play gentle idle motion (breathing, natural blink ~6/min)
    - Use Live2D MotionManager or a simple setInterval-driven parameter oscillation as fallback

- [ ] A3. Layout integration in index.html
  - Add `<canvas id="avatar-canvas" style="pointer-events:none">` absolutely positioned
    over the bottom-left quadrant of `#chat-pane`
  - Add `<script src="avatar/avatar.js" type="module">` after debug panel scripts
  - Verify avatar canvas does NOT block clicks on the chat input area

- [ ]* A4. Lip-sync indicator
  - When a Lucia response bubble is appended to the DOM, briefly animate the mouth
    parameter open/close for ~2s (not true audio lip-sync -- just a timing cue)
  - Implement as a one-shot animation triggered by the chat bubble append event

- [ ]* A5. Avatar unit tests (jsdom + jest)
  - Mock PIXI.live2d.Live2DModel; verify updateFromPAD({pleasure:0.8,...}) calls
    setParameterValueById for each mapped parameter ID
  - Verify updateFromPAD is invoked on each 500ms state poll cycle
