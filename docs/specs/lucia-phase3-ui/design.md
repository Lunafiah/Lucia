# Design Document — Lucia UI Phase 3

## Overview

Phase 3 wraps the Phase 1+2 Python pipeline in a minimal but complete Electron desktop application. Two new layers are introduced:

1. **Python API layer** (`src/api/server.py`) — a FastAPI application that exposes the existing `MemoryAugmentedOrchestrator` over HTTP on localhost. It adds zero new AI logic and only two endpoints: `POST /process` and `GET /state`.
2. **Electron shell** (`electron/`) — a Node.js/Electron host that spawns the Python backend as a child process, proxies all renderer communication via IPC, and renders the Chat_Window and Emotion_Debug_Panel.

The Phase 1+2 Python code is unchanged. The Electron shell is a standalone JavaScript application under `electron/`.

---

## Architecture

### Component Map

```
Electron Main Process (Node.js)
  ├── Process_Manager (process-manager.js)
  │     spawn/monitor/kill Backend_Process
  └── IPC_Bridge (ipc-bridge.js)
        chat:send → POST http://127.0.0.1:8765/process
        state:get → GET  http://127.0.0.1:8765/state

Backend_Process (Python child)
  └── FastAPI_Server (src/api/server.py)
        POST /process  → MemoryAugmentedOrchestrator.process()
        GET  /state    → EmotionCore.get_pad_state() + cached somatic/constraints
        GET  /health   → orchestrator.is_healthy()

Electron Renderer Process
  ├── preload.js         — contextBridge: window.lucia.chat.send / window.lucia.state.get
  ├── Chat_Window        — conversation UI (chat/chat.js)
  └── Emotion_Debug_Panel — 500 ms polling debug sidebar (debug/panel.js)
```

### Key Design Decisions

**No streaming.** The FastAPI server calls `orchestrator.process()` synchronously and returns the complete response as a single JSON object. This is sufficient given LFM2.5-1.2B typical response latency (2–8 s on RTX 3050 Ti).

**IPC proxy pattern.** The renderer never makes direct HTTP calls. All network access goes through `ipcMain` handlers in the main process, satisfying contextIsolation + no-nodeIntegration security requirements.

**FastAPI with run_in_executor.** The `MemoryAugmentedOrchestrator.process()` call is blocking but runs via `asyncio.get_event_loop().run_in_executor(None, ...)`, preventing the uvicorn event loop from stalling while `GET /state` polls are still served concurrently.

**StateSnapshot is a read-only snapshot.** `GET /state` reads the PAD snapshot (non-blocking, 1 ms lock bound), the last-stored somatic markers and behavioral constraints from instance variables updated after each `process()` call, and `len(affective_memory._index)`. No new locks are introduced.

---

## Directory Structure

```
Lucia/
├── src/
│   ├── api/
│   │   └── server.py              # FastAPI application [NEW]
│   └── core/                      # Phase 1+2 unchanged
├── electron/
│   ├── package.json               # electron, electron-builder deps
│   ├── main/
│   │   ├── main.js                # BrowserWindow creation, app lifecycle
│   │   ├── process-manager.js     # Backend_Process spawn/monitor/kill
│   │   └── ipc-bridge.js          # ipcMain handlers
│   ├── preload/
│   │   └── preload.js             # contextBridge window.lucia API
│   └── renderer/
│       ├── index.html             # root layout: chat (70%) + debug (30%)
│       ├── chat/
│       │   ├── chat.js
│       │   └── chat.css
│       └── debug/
│           ├── panel.js
│           └── panel.css
├── config/
│   ├── ui.json                    # port, model_path, n_gpu_layers, log_level
│   └── window-state.json          # persisted bounds (auto-generated)
```

---

## Components and Interfaces

### FastAPI_Server (`src/api/server.py`)

**Responsibility:** Expose the `MemoryAugmentedOrchestrator` over HTTP. Manage lifecycle (init before bind, ready signal, graceful shutdown).

#### Pydantic models and module-level state

```python
from fastapi import FastAPI
from fastapi.responses import JSONResponse
from pydantic import BaseModel
import uuid, asyncio, logging, sys, signal, threading

app = FastAPI()
logger = logging.getLogger("lucia.api")

_orchestrator = None   # InstrumentedOrchestrator instance
_last_somatic = None   # SomaticMarkers, updated after each process() step 3
_last_constraints = None  # BehavioralConstraints, updated after each process() step 4

class ProcessRequest(BaseModel):
    input: str
```

#### POST /process

```python
@app.post("/process")
async def process_endpoint(req: ProcessRequest):
    call_id = uuid.uuid4().hex
    if not req.input or len(req.input) > 4000:
        return JSONResponse({"error": "invalid_input", "call_id": call_id}, status_code=422)
    if _orchestrator._degraded:
        return JSONResponse({"error": "orchestrator_degraded", "call_id": call_id}, status_code=503)
    try:
        loop = asyncio.get_event_loop()
        response = await loop.run_in_executor(None, _orchestrator.process, req.input)
        return {"response": response, "call_id": call_id}
    except Exception as e:
        logger.error("process() failed: %s", e, exc_info=True)
        return JSONResponse({"error": "internal_error", "call_id": call_id}, status_code=500)
```

#### GET /state

```python
@app.get("/state")
async def state_endpoint():
    pad = _orchestrator._emotion_core.get_pad_state()
    s = _last_somatic
    c = _last_constraints
    tc = len(_orchestrator._affective_memory._index)
    return JSONResponse({
        "pad": {"pleasure": pad.pleasure, "arousal": pad.arousal, "dominance": pad.dominance},
        "somatic": {
            "stability":      s.stability      if s else 0.0,
            "cognitive_load": s.cognitive_load if s else 0.0,
            "energy":         s.energy         if s else 0.0,
            "tension":        s.tension        if s else 0.0,
        },
        "constraints": {
            "max_tokens":      c.max_tokens      if c else 150,
            "temperature":     c.temperature     if c else 0.75,
            "latency_ms":      c.latency_ms      if c else 0,
            "reasoning_depth": c.reasoning_depth if c else 1,
        },
        "memory_trace_count": tc,
        "timestamp": pad.timestamp,
    }, headers={"Cache-Control": "no-store"})
```

#### GET /health

```python
@app.get("/health")
async def health_endpoint():
    if _orchestrator and not _orchestrator._degraded:
        return {"status": "ok"}
    return JSONResponse({"status": "degraded"}, status_code=503)
```

#### InstrumentedOrchestrator

A thin subclass that overrides `process()` to cache somatic markers and behavioral constraints after step 4:

```python
class InstrumentedOrchestrator(MemoryAugmentedOrchestrator):
    def process(self, input_text: str) -> str:
        result = super().process(input_text)
        # somatic and constraints were computed in the last call; read from homeostatic state
        global _last_somatic, _last_constraints
        try:
            pad = self._emotion_core.get_pad_state()
            _last_somatic = self._homeostatic_engine.compute_somatic_markers(pad)
            _last_constraints = self._homeostatic_engine.compute_behavioral_constraints(_last_somatic, pad)
        except Exception:
            pass
        return result
```

#### Lifecycle / main()

```python
def main():
    args = _parse_args()   # --port, --model-path, --log-level
    try:
        global _orchestrator
        _orchestrator = InstrumentedOrchestrator(_build_config(args))
    except Exception as e:
        print(f"LUCIA_BACKEND_ERROR: {e}", flush=True)
        sys.exit(1)
    print("LUCIA_BACKEND_READY", flush=True)
    signal.signal(signal.SIGTERM, lambda *_: threading.Thread(target=_graceful_shutdown, daemon=True).start())
    signal.signal(signal.SIGINT,  lambda *_: threading.Thread(target=_graceful_shutdown, daemon=True).start())
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=args.port, log_level=args.log_level.lower())

def _graceful_shutdown():
    if _orchestrator:
        _orchestrator.shutdown()
    sys.exit(0)
```

---

### Process_Manager (`electron/main/process-manager.js`)

**Responsibility:** Spawn and supervise the Python backend child process. Translate stdout signals into IPC messages to the renderer.

```javascript
const { spawn } = require('child_process');
const path = require('path');

class ProcessManager {
    constructor(config, mainWindow) {
        this.config = config;   // {port, modelPath, nGpuLayers, logLevel}
        this.mainWindow = mainWindow;
        this._proc = null;
        this._readyTimeout = null;
        this._ready = false;
    }

    start() {
        const args = ['-m', 'src.api.server',
                      '--port', String(this.config.port),
                      '--model-path', this.config.modelPath];
        this._proc = spawn('python', args, {
            cwd: path.resolve(__dirname, '../../..'),
            detached: false,
            stdio: ['pipe', 'pipe', 'pipe'],
        });

        this._readyTimeout = setTimeout(() => {
            if (!this._ready) {
                this._proc.kill();
                this._dispatch('backend:error', { code: 'startup_timeout' });
            }
        }, 60_000);

        this._proc.stdout.on('data', (chunk) => {
            chunk.toString().split('\n').forEach(line => {
                console.log('[python]', line);
                if (line.trim() === 'LUCIA_BACKEND_READY' && !this._ready) {
                    this._ready = true;
                    clearTimeout(this._readyTimeout);
                    this._dispatch('backend:ready', {});
                } else if (line.startsWith('LUCIA_BACKEND_ERROR:')) {
                    clearTimeout(this._readyTimeout);
                    this._dispatch('backend:error', { code: line.replace('LUCIA_BACKEND_ERROR:', '').trim() });
                }
            });
        });

        this._proc.stderr.on('data', chunk => console.error('[python]', chunk.toString()));
        this._proc.on('exit', code => {
            if (code !== 0) this._dispatch('backend:error', { code: 'process_exited', exitCode: code });
        });
    }

    stop() {
        return new Promise(resolve => {
            if (!this._proc) return resolve();
            const t = setTimeout(() => { this._proc.kill('SIGKILL'); resolve(); }, 10_000);
            this._proc.once('exit', () => { clearTimeout(t); resolve(); });
            this._proc.kill('SIGTERM');
        });
    }

    _dispatch(channel, payload) {
        if (this.mainWindow && !this.mainWindow.isDestroyed())
            this.mainWindow.webContents.send(channel, payload);
    }
}

module.exports = ProcessManager;
```

---

### IPC_Bridge (`electron/main/ipc-bridge.js`)

**Responsibility:** Relay renderer IPC calls to FastAPI HTTP endpoints. Serialize `chat:send` calls.

```javascript
const { ipcMain } = require('electron');

let _pendingChat = null;

function registerHandlers(port) {
    const BASE = `http://127.0.0.1:${port}`;

    ipcMain.handle('chat:send', async (_event, { input }) => {
        if (_pendingChat) await _pendingChat;
        let resolve;
        _pendingChat = new Promise(r => { resolve = r; });
        try {
            const res = await fetch(`${BASE}/process`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ input }),
                signal: AbortSignal.timeout(35_000),
            });
            const data = await res.json();
            if (!res.ok) throw Object.assign(new Error(JSON.stringify(data)), { code: data.error });
            return data;
        } catch (err) {
            throw { code: err.code || 'network_error', message: err.message };
        } finally {
            resolve();
            _pendingChat = null;
        }
    });

    ipcMain.handle('state:get', async () => {
        const res = await fetch(`${BASE}/state`, { signal: AbortSignal.timeout(2_000) });
        return res.json();
    });
}

module.exports = { registerHandlers };
```

---

### Preload Script (`electron/preload/preload.js`)

```javascript
const { contextBridge, ipcRenderer } = require('electron');

contextBridge.exposeInMainWorld('lucia', {
    chat:  { send: input  => ipcRenderer.invoke('chat:send',  { input }) },
    state: { get:  ()     => ipcRenderer.invoke('state:get') },
    on: (channel, cb) => {
        if (['backend:ready', 'backend:error'].includes(channel))
            ipcRenderer.on(channel, (_, payload) => cb(payload));
    },
});
```

No `require`, `process`, `eval`, or Node.js built-ins are exposed.

---

### Chat_Window (`electron/renderer/chat/chat.js`)

State machine: `WAITING_BACKEND → READY → SENDING → READY | ERROR`

```javascript
async function sendMessage() {
    const input = inputEl.value.trim();
    if (!input || state !== 'READY') return;
    setState('SENDING');
    appendBubble('user', input);
    inputEl.value = '';
    showTypingIndicator();
    try {
        const { response } = await window.lucia.chat.send(input);
        appendBubble('lucia', response);
        scrollToBottom();
    } catch (err) {
        appendErrorBubble(err.message || 'Failed to get response');
    } finally {
        hideTypingIndicator();
        setState('READY');
    }
}
```

User bubbles are appended immediately on submit before the IPC call resolves, giving instant visual feedback.

---

### Emotion_Debug_Panel (`electron/renderer/debug/panel.js`)

```javascript
let _pollInterval = null;

function startPolling() {
    _pollInterval = setInterval(async () => {
        try {
            const snap = await window.lucia.state.get();
            renderSnapshot(snap);
        } catch {
            showStaleIndicator();
        }
    }, 500);
}

function updatePADBar(dim, value) {
    // value in [-1.0, 1.0]; center at 50%
    const pct = (value + 1.0) / 2.0;
    const fill = document.getElementById(`pad-fill-${dim}`);
    if (pct >= 0.5) {
        fill.style.left = '50%';
        fill.style.width = `${(pct - 0.5) * 100}%`;
        fill.style.background = '#4caf50';
    } else {
        fill.style.left = `${pct * 100}%`;
        fill.style.width = `${(0.5 - pct) * 100}%`;
        fill.style.background = '#f44336';
    }
    document.getElementById(`pad-label-${dim}`).textContent = value.toFixed(1);
}
```

CSS transitions (`0.3 s ease-out`) are applied to `.pad-bar-fill` for smooth value changes without layout reflow.

---

## IPC Channel Summary

| Channel         | Direction        | Payload                                        |
|-----------------|------------------|------------------------------------------------|
| `chat:send`     | renderer → main  | `{input: string}`                              |
| `chat:send`     | main → renderer  | `{response: string, call_id: string}` or error |
| `state:get`     | renderer → main  | none                                           |
| `state:get`     | main → renderer  | `StateSnapshot` or error                       |
| `backend:ready` | main → renderer  | `{}`                                           |
| `backend:error` | main → renderer  | `{code: string, exitCode?: number}`            |

---

## Startup Sequence

```
1.  app.ready fires in main process
2.  Process_Manager reads config/ui.json
3.  Process_Manager spawns: python -m src.api.server --port 8765 --model-path ...
4.  BrowserWindow opens → loads index.html → Splash_Screen shown
5.  Python: MemoryAugmentedOrchestrator.__init__() (Fast_Loop + Slow_Loop start)
6.  Python: LFM2.5-1.2B GGUF loads to GPU (2–15 s)
7.  Python: uvicorn binds 127.0.0.1:8765
8.  Python: prints "LUCIA_BACKEND_READY"
9.  Process_Manager dispatches backend:ready to renderer
10. Renderer: Splash_Screen dismissed, input enabled, debug polling starts (500 ms)
```

---

## Correctness Properties

### Property UI-1: IPC Serialization for chat:send

*For any sequence of N concurrent chat:send IPC calls, the IPC_Bridge processes exactly one at a time in FIFO order.*

**Validates: Requirement 5.5**

### Property UI-2: Debug Panel Non-Interference

*While the renderer awaits a chat IPC resolve, the Emotion_Debug_Panel setInterval timer continues to fire and call state:get without blocking.*

**Validates: Requirements 2.4, 2.6, 7.1**

### Property UI-3: PAD Bar Bounds Invariant

*For any PAD value in [-1.0, 1.0], the rendered PAD_Bar fill region never exceeds the track bounds.*

**Validates: Requirement 7.3**

### Property UI-4: Backend Signal Idempotence

*Receiving LUCIA_BACKEND_READY more than once is a no-op after the first reception.*

**Validates: Requirement 4.3**
