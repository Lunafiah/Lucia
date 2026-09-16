# Design Document -- Lucia Embodied Desktop Presence (Phase 5)

## Overview

Phase 5 adds Perception (VisionBackend, ScreenObserver, CameraObserver) and Agency
(UIGrounding, ActionExecutor, SafetyGuard, ReactLoop) coordinated by a new
`PresenceOrchestrator`. Phase 1-4 code is unchanged except for one backward-compatible
addition to `PromptAssembler.assemble()`.

---

## Module Map

```
src/core/perception/
    __init__.py
    vision_backend.py      [NEW] -- VisionBackend (Qwen2.5-VL 3B GGUF)
    screen_observer.py     [NEW] -- ScreenObserver (mss, pixel-diff, VLM queue)
    camera_observer.py     [NEW] -- CameraObserver (cv2 webcam)

src/core/agency/
    __init__.py
    errors.py              [NEW] -- ActionBlockedError, EmergencyStopError
    action_token.py        [NEW] -- ActionToken dataclass, action type enum
    ui_grounding.py        [NEW] -- UIGrounding (Windows UIA + VLM fallback)
    action_executor.py     [NEW] -- ActionExecutor (pyautogui dispatch)
    safety_guard.py        [NEW] -- SafetyGuard (ControlState, EmergencyStop)
    react_loop.py          [NEW] -- ReactLoop (Observe-Think-Act-Verify)

src/core/presence/
    __init__.py
    orchestrator.py        [NEW] -- PresenceOrchestrator (extends Phase 2)

src/platform/
    screen.py              [NEW] -- get_focused_window() via psutil + win32gui
    input_controller.py    [NEW] -- thin pyautogui wrappers (used by ActionExecutor)

src/core/orchestrator/
    prompt_assembler.py    [MODIFY] -- add screen_context param to assemble()

src/api/
    server.py              [MODIFY] -- add /presence/* endpoints, extend /state

electron/renderer/presence/
    presence.js            [NEW] -- mode buttons, task input, narration feed
    presence.css           [NEW] -- mode styling, narration feed
    control-overlay.js     [NEW] -- "Lucia is in control" banner + Take Back button
```

---

## Architecture

```
Electron Renderer
  |-- chat/            unchanged (Phase 3)
  |-- avatar/          PAD -> Live2D expressions (Phase 3.5)
  |-- debug/           PAD bars (Phase 3)
  `-- presence/        mode buttons, task input, narration feed, control overlay

Electron Main / IPC Bridge
  |-- chat:send / state:get      Phase 3 unchanged
  |-- presence:mode              set ControlState
  |-- presence:act               start ReactLoop task
  |-- presence:stop-task         interrupt task
  |-- presence:comment (push)    ObservationComment / step narration -> renderer
  |-- presence:control-state     ACTIVE/not-ACTIVE overlay toggle
  `-- camera:active / camera:error

FastAPI (Python)
  |-- POST /process              Phase 3 unchanged
  |-- GET  /state                extended with "presence" field
  |-- POST /presence/mode
  |-- POST /presence/act
  |-- POST /presence/stop-task
  |-- POST /presence/emergency-stop
  |-- POST /presence/camera
  `-- GET  /presence/status

PresenceOrchestrator (extends MemoryAugmentedOrchestrator)
  |-- _vision_backend : VisionBackend
  |-- _screen_obs     : ScreenObserver  (Thread 4, daemon)
  |-- _camera_obs     : CameraObserver  (Thread 5, daemon, optional)
  |-- _safety         : SafetyGuard
  |     `-- _stop_listener  (Thread 6, daemon -- EmergencyStop, started in __init__)
  |-- _executor       : ActionExecutor
  |-- _ui_grounding   : UIGrounding
  `-- _react_loop     : ReactLoop  (Thread 7, task thread, when active)
```

---

## VisionBackend (`src/core/perception/vision_backend.py`)

Uses existing llama-cpp-python dependency (already in requirements.txt):

```python
from llama_cpp import Llama
from llama_cpp.llama_chat_format import Qwen2VLChatHandler
import base64, io, re, concurrent.futures
from PIL import Image

class VisionBackend:
    def __init__(self, config: VisionConfig) -> None:
        if not config.model_path.exists():
            raise FileNotFoundError(f"vision model not found: {config.model_path}")
        if not config.mmproj_path.exists():
            raise FileNotFoundError(f"mmproj not found: {config.mmproj_path}")
        handler = Qwen2VLChatHandler(clip_model_path=str(config.mmproj_path))
        self._llm = Llama(
            model_path=str(config.model_path),
            chat_handler=handler,
            n_ctx=config.n_ctx,
            n_gpu_layers=config.n_gpu_layers,
            verbose=False,
        )
        self._executor = concurrent.futures.ThreadPoolExecutor(max_workers=1)
        self._timeout = config.vision_timeout_seconds

    def describe(self, image: Image.Image, prompt: str, max_tokens: int = 256) -> str:
        data_url = self._to_data_url(image)
        def _call():
            resp = self._llm.create_chat_completion(
                messages=[{"role": "user", "content": [
                    {"type": "image_url", "image_url": {"url": data_url}},
                    {"type": "text",      "text": prompt},
                ]}],
                max_tokens=max_tokens,
            )
            return resp["choices"][0]["message"]["content"] or ""
        try:
            return self._executor.submit(_call).result(timeout=self._timeout)
        except concurrent.futures.TimeoutError:
            logger.warning("VisionBackend.describe() timed out after %ss", self._timeout)
            return ""

    def ground(self, image: Image.Image, target: str) -> tuple[int, int] | None:
        prompt = (
            f'Where is "{target}" in this screenshot? '
            'Reply with ONLY the pixel coordinates in the format (x, y). '
            'Example: (523, 145)'
        )
        text = self.describe(image, prompt, max_tokens=32)
        m = re.search(r'\((\d+),\s*(\d+)\)', text)
        return (int(m.group(1)), int(m.group(2))) if m else None

    @staticmethod
    def _to_data_url(image: Image.Image) -> str:
        buf = io.BytesIO()
        image.save(buf, format="PNG")
        return "data:image/png;base64," + base64.b64encode(buf.getvalue()).decode()
```

**VRAM budget:** Qwen2.5-VL 3B Q4_K_M at n_gpu_layers=28 uses ~1.8-2.0 GB.
LFM2.5-1.2B uses ~1.2 GB. Total: ~3.0-3.2 GB on a 4 GB card (0.8 GB headroom).
If `pynvml` reports usage > 3.2 GB, `n_gpu_layers` is set to 0 for CPU-only fallback.

---

## ScreenObserver (`src/core/perception/screen_observer.py`)

```python
import mss, numpy as np, threading, time
from PIL import Image

class ScreenObserver:
    def _capture_loop(self):
        with mss.mss() as sct:
            monitor = sct.monitors[1]          # primary monitor
            last_stale_time = time.monotonic()
            while not self._stop.wait(timeout=self._interval()):
                raw = sct.grab(monitor)
                frame = np.array(Image.frombytes("RGB", raw.size, raw.rgb))
                gray  = frame.mean(axis=2) / 255.0   # float32, shape (H, W)

                # Change detection
                changed = True
                if self._prev is not None:
                    diff = np.abs(gray - self._prev).mean()
                    elapsed_stale = time.monotonic() - last_stale_time
                    changed = (diff > self._cfg.change_threshold
                               or elapsed_stale > self._cfg.stale_timeout_seconds)

                if changed:
                    last_stale_time = time.monotonic()
                    self._prev = gray
                    pil = Image.fromarray(frame)
                    try:
                        desc = self._vision.describe(
                            pil,
                            "Describe what is on this computer screen. "
                            "Mention the active app, what the user appears to be doing, "
                            "and any important visible content. Be brief (2-3 sentences).",
                            max_tokens=200,
                        )
                        proc, title = get_focused_window()
                        ctx = ScreenContext(
                            description=desc, app_name=proc,
                            window_title=title, timestamp=time.monotonic(),
                        )
                        with self._lock:
                            self._latest = ctx
                    except Exception:
                        logger.error("ScreenObserver VisionBackend call failed", exc_info=True)
```

Mean-absolute-difference on grayscale is O(W*H) ~5 ms for 1920x1080 in numpy.
VisionBackend is called ONLY on meaningful change (saves GPU/CPU significantly).

---

## SafetyGuard (`src/core/agency/safety_guard.py`)

The EmergencyStop listener is the FIRST thing created -- inside `__init__`, before
any other Phase 5 component, and it lives for the entire application session.

```python
from pynput import keyboard
from fnmatch import fnmatch
import threading, time
from collections import deque
from enum import Enum

class ControlState(Enum):
    IDLE   = "idle"
    WATCH  = "watch"
    ASSIST = "assist"
    ACTIVE = "active"

class SafetyGuard:
    def __init__(self, config, on_state_change=None):
        self._cfg = config
        self._state = ControlState.IDLE
        self._lock  = threading.Lock()
        self._stop_event = threading.Event()
        self._action_times: deque[float] = deque()
        self._on_state_change = on_state_change

        # EmergencyStop -- FIRST, runs forever
        hotkeys = {config.emergency_stop_hotkey: self._on_emergency_stop}
        self._hotkey_listener = keyboard.GlobalHotKeys(hotkeys)
        t = threading.Thread(target=self._hotkey_listener.start,
                             name="EmergencyStop-Listener", daemon=True)
        t.start()

    def _on_emergency_stop(self):
        self._stop_event.set()
        self.set_state(ControlState.WATCH)
        if self._on_state_change:
            self._on_state_change("emergency_stop")

    def set_state(self, new_state: ControlState) -> None:
        # Clear stop_event when explicitly transitioning TO ACTIVE
        if new_state == ControlState.ACTIVE:
            self._stop_event.clear()
        with self._lock:
            self._state = new_state
        if self._on_state_change:
            self._on_state_change(new_state.value)

    def is_permitted(self, action_type: str) -> tuple[bool, str]:
        if self._stop_event.is_set():
            return False, "emergency_stop_active"
        with self._lock:
            if self._state != ControlState.ACTIVE:
                return False, f"control_state_is_{self._state.value}"
        # Rate limit (rolling 60s window)
        now = time.monotonic()
        self._action_times = deque(t for t in self._action_times if now - t < 60.0)
        if len(self._action_times) >= self._cfg.max_actions_per_minute:
            return False, "rate_limit_exceeded"
        # ForbiddenZone
        proc, title = get_focused_window()
        for pat in self._cfg.forbidden_zones:
            if fnmatch(proc.lower(), pat) or fnmatch(title.lower(), pat):
                self.set_state(ControlState.WATCH)
                logger.warning("ForbiddenZone intervention: proc=%s title=%s", proc, title)
                return False, "forbidden_zone"
        self._action_times.append(now)
        return True, "ok"
```

Note: `_stop_event` is cleared ONLY when the user explicitly transitions to ACTIVE.
This prevents a runaway loop from silently clearing the emergency stop.

---

## ActionExecutor (`src/core/agency/action_executor.py`)

```python
import pyautogui, time
pyautogui.FAILSAFE = True   # set at module import, cannot be disabled by config

class ActionExecutor:
    def execute(self, token: ActionToken, guard: SafetyGuard) -> None:
        permitted, reason = guard.is_permitted(token.action)
        if not permitted:
            raise ActionBlockedError(reason)

        try:
            match token.action:
                case "click":
                    pyautogui.click(token.x, token.y, button=token.button or "left")
                case "double_click":
                    pyautogui.doubleClick(token.x, token.y)
                case "right_click":
                    pyautogui.rightClick(token.x, token.y)
                case "type":
                    pyautogui.typewrite(token.text,
                                        interval=self._cfg.typing_delay_ms / 1000.0)
                case "hotkey":
                    pyautogui.hotkey(*token.keys)
                case "key_press":
                    pyautogui.press(token.key)
                case "scroll":
                    pyautogui.scroll(token.amount, x=token.x, y=token.y)
                case "drag":
                    pyautogui.moveTo(token.x1, token.y1)
                    pyautogui.dragTo(token.x2, token.y2, duration=0.3, button="left")
                case "focus_window":
                    _focus_window_by_title(token.title_pattern)
                case "wait":
                    time.sleep(min(float(token.seconds), 10.0))
                case "observe":
                    pass    # ReactLoop handles the actual observe step
        except pyautogui.FailSafeException:
            raise EmergencyStopError("pyautogui failsafe (top-left corner) triggered")
        finally:
            time.sleep(self._cfg.min_action_delay_ms / 1000.0)
```

---

## ReactLoop (`src/core/agency/react_loop.py`)

The Think prompt uses line-split to separate structured JSON from narration
(simpler and more reliable than regex extraction on free-form LLM output):

```python
THINK_SYSTEM = (
    "You are controlling a Windows computer on behalf of the user. "
    "Output a JSON action object on LINE 1, then your narration on LINE 2+. "
    "Available actions: click, double_click, right_click, type, hotkey, "
    "key_press, scroll, drag, focus_window, wait, observe, done. "
    "JSON examples:\n"
    '  Line1: {"action": "click", "x": 523, "y": 145}\n'
    '  Line1: {"action": "type", "text": "hello"}\n'
    '  Line1: {"action": "hotkey", "keys": ["ctrl", "c"]}\n'
    '  Line1: {"action": "done", "summary": "Task finished"}\n'
    "Narration should be natural and brief (1-2 sentences)."
)

class ReactLoop:
    def __init__(self):
        self._interrupt = threading.Event()

    def stop(self):
        self._interrupt.set()

    def run(self, goal, screen_obs, llm, executor, guard, on_narration,
            max_steps=20):
        history = []
        for step in range(max_steps):
            if self._interrupt.is_set():
                on_narration("Okay, I've stopped.")
                break

            # OBSERVE
            ctx = screen_obs.get_latest_context()
            desc = ctx.description if ctx else "(screen not available)"
            app  = ctx.app_name if ctx else "Unknown"

            # THINK
            user_content = (
                f"Goal: {goal}\n"
                f"Screen: {desc}\n"
                f"App: {app}\n"
                f"History (last 5): {json.dumps(history[-5:])}\n"
                "What do you do next?"
            )
            raw = llm.generate_with_system(THINK_SYSTEM, user_content,
                                           constraints=_presence_constraints())
            if not raw:
                break

            # Parse: first line = JSON, rest = narration
            parts = raw.strip().split("\n", 1)
            try:
                token_dict = json.loads(parts[0].strip())
            except (json.JSONDecodeError, IndexError):
                token_dict = {"action": "observe"}
            narration = parts[1].strip() if len(parts) > 1 else ""

            if narration:
                on_narration(narration)
            history.append({"step": step, "action": token_dict, "narration": narration})

            # DONE check
            if token_dict.get("action") == "done":
                break

            # ACT
            if token_dict.get("action") == "observe":
                continue

            try:
                token = ActionToken(**token_dict)
                executor.execute(token, guard)
            except ActionBlockedError as e:
                on_narration(f"I was blocked from doing that. ({e})")
                break
            except EmergencyStopError:
                on_narration("Emergency stop -- I've stepped back.")
                break
        else:
            on_narration(
                "I've reached my step limit and wasn't able to finish. "
                "Want me to keep going?"
            )
```

---

## PromptAssembler Extension (Phase 1 file, backward-compatible change)

```python
# In prompt_assembler.py -- add keyword arg, insert section

def assemble(self, ..., screen_context: "ScreenContext | None" = None) -> str | AssemblyError:
    # ... existing section building ...
    if screen_context is not None:
        screen_section = (
            "[SCREEN CONTEXT]\n"
            f"app: {screen_context.app_name}\n"
            f"title: {screen_context.window_title}\n"
            f"description: {screen_context.description}\n"
        )
        _validate_no_recall(screen_section)   # same 8-phrase check as echo section
        # Insert after [SOMATIC STATE], before [MEMORY ECHO] / [REASONING]
        sections.insert(screen_context_insert_index, screen_section)
    # ... rest unchanged ...
```

Default `None` means existing tests are completely unaffected.

---

## Electron UI -- Presence Layer

### New renderer components

```
electron/renderer/presence/
    presence.js          -- mode toggle buttons, task input, narration feed
    presence.css         -- styling
    control-overlay.js   -- "Lucia is in control" banner + Take Back button
```

### Control Overlay (always visible when ACTIVE)

```css
#control-overlay {
  position: fixed; top: 0; left: 0; right: 0; z-index: 9999;
  background: rgba(220, 50, 50, 0.90);
  color: #fff; padding: 8px 20px;
  display: flex; align-items: center; gap: 12px;
  font-family: 'Inter', sans-serif; font-size: 14px;
}
.pulse-dot {
  width: 10px; height: 10px; border-radius: 50%;
  background: #fff; animation: pulse 1.2s ease-in-out infinite;
}
@keyframes pulse { 0%,100%{opacity:1} 50%{opacity:0.3} }
#take-back-btn {
  margin-left: auto; padding: 4px 14px; border: 1.5px solid #fff;
  border-radius: 4px; background: transparent; color: #fff; cursor: pointer;
}
```

### IPC Channels (Phase 5 additions)

| Channel             | Direction      | Payload                             |
|---------------------|----------------|-------------------------------------|
| presence:mode       | renderer->main | {mode: string}                      |
| presence:act        | renderer->main | {command: string}                   |
| presence:stop-task  | renderer->main | --                                  |
| presence:comment    | main->renderer | {task_id?, step?, text: string}     |
| presence:control-state | main->renderer | {active: bool}                   |
| presence:emergency-stop | main->renderer | --                              |
| camera:active       | main->renderer | {capturing: bool}                   |
| camera:error        | main->renderer | {reason: string}                    |

---

## Startup Sequence (Phase 5 additions after LUCIA_BACKEND_READY)

```
1. SafetyGuard.__init__() -> EmergencyStop listener starts FIRST (always)
2. VisionBackend loads Qwen2.5-VL 3B in background thread (10-30s for GPU offload)
3. Electron shows "Vision: loading..." indicator
4. VisionBackend.is_ready() -> Electron shows "Vision: ready"
5. ScreenObserver starts (IDLE mode -- no captures yet)
6. User enables WATCH -> ScreenObserver begins capture loop at passive_interval
7. [optional] User enables camera -> CameraObserver starts
```

The chat window is fully usable while the vision model loads.
A subtle badge in the debug panel shows: Vision: loading... -> Vision: ready.

---

## Correctness Properties

### P5-1: Emergency Stop Priority
Once `_stop_event` is set, ALL ActionExecutor calls return ActionBlockedError
regardless of ControlState, until the user explicitly re-enables ACTIVE mode
(which is the only operation that calls `_stop_event.clear()`).

### P5-2: ForbiddenZone Invariant
No ActionToken is ever executed against a window matching a ForbiddenZone pattern,
regardless of ControlState. ForbiddenZone check runs in `is_permitted()` which is
called before EVERY action.

### P5-3: ReactLoop Non-Blocking
The ReactLoop runs in a dedicated daemon thread. `POST /process` calls run in
uvicorn's thread pool executor and are never blocked by ReactLoop activity.

### P5-4: Screen Context No-Recall Invariant
The [SCREEN CONTEXT] prompt section is validated by the same 8-phrase recall check
used for Phase 2 echo sections before it is inserted into the prompt.

### P5-5: VRAM Budget
VisionBackend + LLMBackend combined GPU memory remains under 3.5 GB under normal
operation. Runtime monitoring reduces n_gpu_layers to 0 if 3.2 GB is exceeded.
