# Requirements Document

## Introduction

This document defines the requirements for **Lucia UI Phase 3**: an Electron-based desktop chat application that wraps the Phase 1+2 Python backend in a native Windows GUI. Phase 3 covers four cooperating components:

1. **FastAPI_Server** - A lightweight HTTP server wrapping the `MemoryAugmentedOrchestrator` with two endpoints: `POST /process` for chat turns and `GET /state` for live emotional state polling.
2. **Process_Manager** - The Electron main-process component that spawns the Python backend as a child process on startup, monitors its health, and terminates it cleanly on app exit.
3. **Chat_Window** - The Electron renderer-process chat UI that sends messages to `POST /process` and renders full (non-streamed) responses in a conversation view.
4. **Emotion_Debug_Panel** - A live sidebar panel that polls `GET /state` every 500 ms and renders PAD bars, somatic markers, behavioral constraints, and memory trace count as a real-time debug display.

The guiding constraint is **localhost-only, Windows-first, no cloud dependencies**. All communication is over `127.0.0.1` on a configurable port. The Electron renderer communicates only through Electron's IPC bridge to the main process, which proxies to the FastAPI server — no direct renderer-to-network calls are permitted.

---

## Glossary

- **FastAPI_Server**: The Python HTTP server (`src/api/server.py`) exposing `POST /process` and `GET /state` over localhost. Runs inside the Python backend process, initialized with a `MemoryAugmentedOrchestrator` instance.
- **Process_Manager**: The Electron main-process module (`electron/main/process-manager.js`) responsible for spawning, monitoring, and terminating the Python backend child process.
- **Chat_Window**: The Electron renderer component (`electron/renderer/chat/`) that manages the conversation history DOM, input field, and send flow.
- **Emotion_Debug_Panel**: The Electron renderer component (`electron/renderer/debug/`) that polls `GET /state` at 500 ms intervals and renders PAD, somatic markers, behavioral constraints, and memory trace count.
- **IPC_Bridge**: Electron's `ipcMain`/`ipcRenderer` channel pair used to relay all renderer requests through the main process to the FastAPI_Server, avoiding direct renderer network access.
- **Backend_Process**: The Python 3.12 child process spawned by Process_Manager, running `python -m src.api.server` with the model path and port passed as arguments.
- **StateSnapshot**: The JSON object returned by `GET /state`, containing: `pad` (`{pleasure, arousal, dominance}`), `somatic` (`{stability, cognitive_load, energy, tension}`), `constraints` (`{max_tokens, temperature, latency_ms, reasoning_depth}`), `memory_trace_count` (integer), and `timestamp` (monotonic float from the backend).
- **ProcessResponse**: The JSON object returned by `POST /process`, containing: `response` (string) and `call_id` (string UUID).
- **PAD_Bar**: A visual bar element in the Emotion_Debug_Panel rendering a single PAD dimension value in `[-1.0, 1.0]`. The bar midpoint represents `0.0`; positive values extend right, negative values extend left.
- **Degraded_State**: Inherited from Phase 1/2. When the Orchestrator enters Degraded_State, `GET /state` continues to return a valid StateSnapshot but `POST /process` returns HTTP 503.
- **Backend_Ready_Signal**: The exact token `LUCIA_BACKEND_READY` emitted by the FastAPI_Server on stdout once fully initialized. The Process_Manager waits for this signal before enabling the Chat_Window's send controls.
- **Port**: The localhost TCP port on which the FastAPI_Server listens. Default: `8765`. Configurable via `config/ui.json`.
- **Splash_Screen**: A minimal loading overlay displayed while the Backend_Process is starting up, replaced by the main UI once Backend_Ready_Signal is received.

---

## Requirements

### Requirement 1: FastAPI Server — Process Endpoint

**User Story:** As the Chat_Window, I want to send a user message to the Python backend and receive the Orchestrator's full response, so that Lucia can reply to conversation turns without streaming.

#### Acceptance Criteria

1. THE FastAPI_Server SHALL expose a `POST /process` endpoint that accepts a JSON body `{"input": "<string>"}` and returns a JSON body `{"response": "<string>", "call_id": "<uuid>"}`.
2. WHEN `POST /process` receives a valid request, THE FastAPI_Server SHALL call `MemoryAugmentedOrchestrator.process(input)` synchronously and return the full response string as the `response` field. No partial or streaming chunks SHALL be emitted.
3. IF the `input` field is missing or is not a string, THEN THE FastAPI_Server SHALL return HTTP 422 with a JSON error body identifying the invalid field, without calling the Orchestrator.
4. IF the `input` string is empty or exceeds 4000 characters, THEN THE FastAPI_Server SHALL return HTTP 422 with a descriptive error message, without calling the Orchestrator.
5. IF the Orchestrator is in Degraded_State, THEN THE FastAPI_Server SHALL return HTTP 503 with the JSON body `{"error": "orchestrator_degraded", "call_id": "<uuid>"}` and SHALL NOT call the Orchestrator's `process()` method.
6. IF the Orchestrator raises an unhandled exception during `process()`, THEN THE FastAPI_Server SHALL catch the exception, log it with a full stack trace, and return HTTP 500 with the JSON body `{"error": "internal_error", "call_id": "<uuid>"}`.
7. THE FastAPI_Server SHALL complete the `POST /process` response within the Orchestrator's own pipeline latency plus no more than 20 ms of server-side overhead for JSON serialization and routing.
8. THE FastAPI_Server SHALL bind exclusively to `127.0.0.1` on the configured port and SHALL NOT bind to `0.0.0.0` or any external interface.

---

### Requirement 2: FastAPI Server — State Endpoint

**User Story:** As the Emotion_Debug_Panel, I want to poll the backend for the current PAD state, somatic markers, behavioral constraints, and memory trace count at high frequency, so that the debug panel always reflects the system's live internal state.

#### Acceptance Criteria

1. THE FastAPI_Server SHALL expose a `GET /state` endpoint that returns a JSON StateSnapshot with no required request parameters.
2. WHEN `GET /state` is called, THE FastAPI_Server SHALL read the current `PAD_State` from `EmotionCore.get_pad_state()`, the latest `SomaticMarkers` from the last completed pipeline step, the latest `BehavioralConstraints`, and `AffectiveMemory.trace_count` from the Orchestrator's memory subsystem.
3. THE StateSnapshot JSON SHALL have the following structure:
   ```
   {
     "pad": {"pleasure": float, "arousal": float, "dominance": float},
     "somatic": {"stability": float, "cognitive_load": float, "energy": float, "tension": float},
     "constraints": {"max_tokens": int, "temperature": float, "latency_ms": int, "reasoning_depth": int},
     "memory_trace_count": int,
     "timestamp": float
   }
   ```
4. THE `GET /state` endpoint SHALL respond within 10 ms from request receipt to response sent, regardless of whether the Orchestrator is processing a chat turn at the same moment.
5. IF `GET /state` is called before any chat turn has been processed, THE FastAPI_Server SHALL return the resting baseline PAD state, zero-valued somatic markers, default behavioral constraints, and `memory_trace_count: 0`.
6. THE FastAPI_Server SHALL serve `GET /state` concurrently with `POST /process` without blocking either endpoint; the state read SHALL NOT acquire any lock held by the `process()` pipeline for longer than the 1 ms PAD lock acquisition bound inherited from Phase 1.
7. THE FastAPI_Server SHALL include `Cache-Control: no-store` in `GET /state` responses to prevent any intermediate caching.

---

### Requirement 3: FastAPI Server — Lifecycle and Configuration

**User Story:** As the Process_Manager, I want the FastAPI_Server to emit a machine-readable ready signal on stdout once it is fully initialized, and to shut down cleanly when its process receives a termination signal.

#### Acceptance Criteria

1. WHEN the FastAPI_Server starts, it SHALL initialize the `MemoryAugmentedOrchestrator` (including starting the Emotion_Core Fast_Loop and DecayEngine Slow_Loop) before binding the HTTP port.
2. ONCE the Orchestrator is initialized and the HTTP port is bound with both background threads confirmed alive, THE FastAPI_Server SHALL emit the exact token `LUCIA_BACKEND_READY` to stdout as a standalone line.
3. THE FastAPI_Server SHALL accept the listening port as a command-line argument `--port <int>` or as the `LUCIA_PORT` environment variable; the command-line argument SHALL take precedence when both are present.
4. THE FastAPI_Server SHALL accept the LFM model path as a command-line argument `--model-path <path>` or as the `LUCIA_MODEL_PATH` environment variable.
5. WHEN the FastAPI_Server process receives `SIGTERM` or `SIGINT` (on Windows: `CTRL_C_EVENT` or `CTRL_BREAK_EVENT`), THE FastAPI_Server SHALL call `MemoryAugmentedOrchestrator.shutdown()`, wait for background threads to join (up to 10 seconds total), and then exit with code 0.
6. IF the `MemoryAugmentedOrchestrator` fails to initialize, THE FastAPI_Server SHALL emit `LUCIA_BACKEND_ERROR: <reason>` to stdout, log the full exception to stderr, and exit with a non-zero exit code within 30 seconds of startup.
7. THE FastAPI_Server SHALL expose a `GET /health` endpoint returning `{"status": "ok"}` with HTTP 200 when the Orchestrator is healthy, and `{"status": "degraded"}` with HTTP 503 when it is in Degraded_State.

---

### Requirement 4: Process Manager — Backend Spawning

**User Story:** As the Electron application, I want the Python backend to be launched automatically when the app opens and terminated when it closes, so that the user never has to manage the backend process manually.

#### Acceptance Criteria

1. THE Process_Manager SHALL spawn the Backend_Process as a child process using Node.js `child_process.spawn` with `detached: false` and `stdio: ['pipe', 'pipe', 'pipe']` immediately after the Electron `app.ready` event fires.
2. THE Process_Manager SHALL pass the model path and port to the Backend_Process as command-line arguments, reading both values from `config/ui.json` at startup.
3. WHEN the Backend_Process emits `LUCIA_BACKEND_READY` on stdout, THE Process_Manager SHALL dispatch an IPC message `backend:ready` to all renderer windows.
4. WHEN the Backend_Process emits `LUCIA_BACKEND_ERROR: <reason>` on stdout, THE Process_Manager SHALL dispatch an IPC message `backend:error` with the reason string to all renderer windows and SHALL NOT attempt to restart the process automatically.
5. THE Process_Manager SHALL set a startup timeout of 60 seconds; IF `LUCIA_BACKEND_READY` is not received within 60 seconds of spawn, THE Process_Manager SHALL terminate the Backend_Process and dispatch `backend:error` with the message `"startup_timeout"`.
6. WHEN the Electron `app.before-quit` event fires, THE Process_Manager SHALL send `SIGTERM` (on Windows: terminate the process) to the Backend_Process, wait up to 10 seconds for it to exit, and then force-kill it if it has not exited within that window.
7. IF the Backend_Process exits unexpectedly while the app is running, THE Process_Manager SHALL dispatch `backend:error` with the message `"process_exited"` and the exit code to all renderer windows.
8. THE Process_Manager SHALL prefix all Backend_Process stdout and stderr lines with `[python]` and route them to the Electron devtools console for developer debugging.

---

### Requirement 5: IPC Bridge — Renderer-to-Main Communication

**User Story:** As the renderer process, I want all network communication to the FastAPI_Server to be proxied through the Electron main process via IPC, so that the renderer never opens direct TCP connections to the backend.

#### Acceptance Criteria

1. THE IPC_Bridge SHALL expose a `chat:send` IPC channel in the main process that accepts `{input: string}`, forwards it to `POST /process` via an HTTP call on the main process side, and resolves with `{response: string, call_id: string}` to the renderer.
2. THE IPC_Bridge SHALL expose a `state:get` IPC channel in the main process that accepts no arguments, calls `GET /state`, and resolves with a StateSnapshot object.
3. THE renderer preload script SHALL expose `window.lucia.chat.send(input: string): Promise<{response, call_id}>` and `window.lucia.state.get(): Promise<StateSnapshot>` as the only network-adjacent APIs available to renderer code; direct `fetch()` or `XMLHttpRequest` calls to the backend SHALL NOT be required or used.
4. IF the main process HTTP call to the FastAPI_Server fails, THE IPC_Bridge SHALL reject the IPC promise with a structured error object `{code: string, message: string}` rather than throwing an unhandled exception.
5. THE IPC_Bridge SHALL serialize all `chat:send` requests; if a `chat:send` IPC call arrives while a previous one is still awaiting the HTTP response, THE IPC_Bridge SHALL queue the new call and process it after the current one resolves.
6. THE `state:get` IPC channel SHALL NOT be subject to the same serialization constraint as `chat:send`; concurrent `state:get` calls are permitted.

---

### Requirement 6: Chat Window — Conversation UI

**User Story:** As the user, I want to type a message, press Enter or click Send, and see Lucia's response appear in the conversation history, so that I can have a natural text-based conversation.

#### Acceptance Criteria

1. THE Chat_Window SHALL render a vertically scrolling conversation history area displaying alternating user messages and Lucia response bubbles.
2. WHEN the user submits a message (Enter key or Send button click), THE Chat_Window SHALL immediately append the user's message to the conversation history, disable the input field and Send button, and call `window.lucia.chat.send()`.
3. WHEN `window.lucia.chat.send()` resolves, THE Chat_Window SHALL append Lucia's response to the conversation history, re-enable the input field, clear the input text, and scroll the history to the bottom.
4. THE Chat_Window SHALL display a loading indicator (e.g., animated ellipsis) in the conversation area while awaiting the response; the indicator SHALL be removed when the response arrives or when an error occurs.
5. IF `window.lucia.chat.send()` rejects, THE Chat_Window SHALL display an inline error message in the conversation history and re-enable the input field, allowing the user to retry.
6. THE Send button SHALL be disabled while a response is pending, while the backend is not ready, and while the input field is empty.
7. THE Chat_Window SHALL preserve the full conversation history in memory for the duration of the session and SHALL NOT persist it to disk automatically.
8. THE input field SHALL accept multi-line text via Shift+Enter; the Enter key alone SHALL submit the message.
9. THE Chat_Window SHALL NOT allow the user to edit or delete prior conversation turns.

---

### Requirement 7: Emotion Debug Panel — Live State Display

**User Story:** As a developer or curious user, I want to see Lucia's current PAD state, somatic markers, behavioral constraints, and memory trace count updating in real time, so that I can observe how the internal emotional state evolves during conversation.

#### Acceptance Criteria

1. THE Emotion_Debug_Panel SHALL poll `window.lucia.state.get()` every 500 ms while the backend is ready, using `setInterval` or equivalent browser-compatible timer.
2. EACH poll result SHALL update the following visual elements without causing layout reflow of the Chat_Window: PAD bars for `pleasure`, `arousal`, and `dominance`; somatic marker value readouts for `stability`, `cognitive_load`, `energy`, and `tension`; constraint value readouts for `max_tokens`, `temperature`, `latency_ms`, and `reasoning_depth`; and a numeric `memory_trace_count` display.
3. THE PAD_Bar for each dimension SHALL render as a horizontal bar centered at zero. The filled portion SHALL extend rightward for positive values and leftward for negative values, with the full bar width representing `[-1.0, 1.0]`. The current numeric value SHALL be displayed as a label to one decimal place.
4. WHEN a PAD dimension, somatic marker, or constraint value changes relative to the previous poll, THE Emotion_Debug_Panel SHALL apply a brief CSS transition (300 ms ease-out) to the bar or readout to visually signal the change.
5. THE somatic marker values (`stability`, `cognitive_load`, `energy`, `tension`) SHALL each be rendered as a labeled progress bar in the range `[0.0, 1.0]`.
6. IF `window.lucia.state.get()` rejects during polling, THE Emotion_Debug_Panel SHALL display a stale-data indicator without resetting the previously displayed values, and SHALL continue polling.
7. THE Emotion_Debug_Panel SHALL stop polling when the `backend:error` IPC message is received and SHALL display a disconnected state indicator.
8. THE Emotion_Debug_Panel SHALL be rendered as a fixed-width sidebar panel (minimum 280 px) that does not obscure the Chat_Window's message input area at any supported window size.

---

### Requirement 8: Application Layout and Window Management

**User Story:** As the user, I want the application window to open in a well-proportioned layout with the chat area and debug panel visible, and to remember my preferred window size between sessions.

#### Acceptance Criteria

1. THE Electron window SHALL open with a default size of 1200 x 750 pixels and a minimum size of 800 x 500 pixels.
2. THE main layout SHALL divide the window into two regions: a Chat_Window region occupying the left portion (70%) and an Emotion_Debug_Panel region occupying the right portion (30%).
3. THE Electron window SHALL display the Splash_Screen overlay (with a spinner and "Starting Lucia..." text) immediately on open, before the Backend_Process is confirmed ready.
4. WHEN `backend:ready` IPC message is received, THE Splash_Screen SHALL be dismissed and the Chat_Window input field SHALL become active.
5. THE Electron window SHALL NOT have a title bar menu (set `autoHideMenuBar: true`), but SHALL retain the native OS window controls (minimize, maximize, close).
6. THE window size and position SHALL be persisted to `config/window-state.json` on close and restored on the next launch; IF the persisted position is off-screen, THE Electron window SHALL fall back to the default centered position.
7. THE application SHALL use a dark color scheme as its default visual theme.

---

### Requirement 9: Backend Configuration

**User Story:** As a developer deploying Phase 3, I want all backend and UI parameters to be configurable from a single JSON file without code changes.

#### Acceptance Criteria

1. A `config/ui.json` file SHALL be read by both the Process_Manager at startup and exposed to the FastAPI_Server via command-line arguments; it SHALL contain at minimum: `port` (integer, default 8765), `model_path` (string, no default), `n_gpu_layers` (integer, default 32), and `log_level` (string, default `"INFO"`).
2. IF `config/ui.json` is missing at application startup, THE Process_Manager SHALL log a warning and use all default values, EXCEPT for `model_path`, which has no default and SHALL cause the Process_Manager to dispatch `backend:error` with `"model_path_not_configured"` immediately.
3. THE FastAPI_Server SHALL validate the `port` field at startup; IF `port` is less than 1024 or greater than 65535, THE FastAPI_Server SHALL emit `LUCIA_BACKEND_ERROR: invalid_port` and exit.
4. Changes to `config/ui.json` SHALL NOT take effect until the application is restarted; no hot-reload of configuration is required.

---

### Requirement 10: Security and Isolation

**User Story:** As a system operator, I want the Electron application to follow security best practices for local AI applications, so that the renderer is isolated from Node.js APIs and the backend is unreachable from external networks.

#### Acceptance Criteria

1. THE Electron renderer SHALL run with `nodeIntegration: false` and `contextIsolation: true`; all Node.js APIs SHALL be accessible to renderer code only through the preload script's explicitly defined `window.lucia` API surface.
2. THE FastAPI_Server SHALL bind exclusively to `127.0.0.1`; any configuration value that would cause it to bind to a non-loopback address SHALL be rejected with `LUCIA_BACKEND_ERROR: external_bind_rejected`.
3. THE CORS configuration on the FastAPI_Server SHALL allow requests from `null` origin (Electron file:// context) only; requests from any other origin SHALL receive HTTP 403.
4. THE preload script SHALL NOT expose `eval`, `require`, `process`, or any other Node.js built-in except through controlled wrappers that provide only the explicitly defined `window.lucia.*` methods.
5. THE content security policy (CSP) for the Electron renderer SHALL include `default-src 'self'; script-src 'self'; connect-src 'none'`; no inline scripts or external resource loads SHALL be permitted.

---

### Requirement 11: Error Handling and Resilience

**User Story:** As the user, I want the application to gracefully handle backend failures and connection errors without crashing or leaving the UI in an unusable state.

#### Acceptance Criteria

1. WHEN the `backend:error` IPC message is received at any time, THE Chat_Window AND Emotion_Debug_Panel SHALL both enter a disabled error state, displaying a human-readable error message that includes the error code.
2. THE Chat_Window SHALL display the text "Lucia is unavailable - please restart the application." when the backend is in an error state, and SHALL NOT allow the user to submit messages.
3. IF the FastAPI_Server fails to respond to a `GET /state` poll within 2 seconds, THE Emotion_Debug_Panel SHALL treat the poll as failed and follow stale-data behavior without resetting the previously displayed values.
4. IF the FastAPI_Server fails to respond to a `POST /process` call within the LLM timeout (default 30 seconds) plus 5 seconds of network overhead, THE IPC_Bridge SHALL reject the IPC promise with `{code: "timeout", message: "Response timed out"}`.
5. THE application SHALL NOT crash or display an unhandled promise rejection dialog under any combination of backend failure, network timeout, and concurrent user interaction.
