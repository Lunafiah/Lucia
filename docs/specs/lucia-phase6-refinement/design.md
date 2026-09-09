# Design Document — Lucia Refinement, QoL & Stability Telemetry (Phase 6)

## Overview

Phase 6 implements the final polish, packaging, desktop quality-of-life features, and continuous stability evaluation for Lucia.

---

## Architecture & Module Map

```
src/core/telemetry/
    __init__.py
    stability_evaluator.py   [NEW] — StabilityEvaluator (computes LSI, jitter, ODE variance)

src/core/storage/
    __init__.py
    history_store.py         [NEW] — ChatHistoryStore (JSON/SQLite conversation persistence)

src/api/
    server.py                [MODIFY] — add /telemetry/stability, /history/* endpoints

electron/
    main/
        tray-manager.js      [NEW] — System Tray icon, context menu, minimize-to-tray
        mascot-window.js     [NEW] — Floating Always-on-Top mascot window controller
        hotkey-manager.js    [NEW] — Global shortcuts (Ctrl+Shift+L)
        ipc-bridge.js        [MODIFY] — IPC handlers for tray, mascot, audio devices, history
    renderer/
        journal/
            journal.js       [NEW] — Companion Journal & affective trajectory charts
            journal.css      [NEW] — Journal styling
        audio/
            audio-router.js  [NEW] — Web Audio output device selector & volume manager
        chat/
            chat.js          [MODIFY] — History persistence, clear screen, export
        debug/
            panel.js         [MODIFY] — Stability telemetry meter integrations
    build/
        icon.ico             [NEW] — Application icon
    package.json             [MODIFY] — electron-builder packaging configuration
```

---

## 1. Stability Evaluator (`src/core/telemetry/stability_evaluator.py`)

### Mathematical Metrics

1. **Fast-Loop Tick Jitter**:
   Given tick timestamps $\{t_1, t_2, \dots, t_N\}$ over a rolling window of $N=100$ ticks and nominal cadence $\Delta t_{nom} = 200\text{ms}$:
   $$\Delta t_k = t_k - t_{k-1}$$
   $$\text{Jitter}_{mean} = \frac{1}{N-1} \sum_{k=2}^N |\Delta t_k - \Delta t_{nom}|, \quad \text{Jitter}_{max} = \max_k |\Delta t_k - \Delta t_{nom}|$$

2. **ODE State Velocity & Variance**:
   Tracks the rate of change of hidden state vector $h(t)$:
   $$v_k = \frac{\|h_k - h_{k-1}\|_2}{\Delta t_k}$$
   $$\sigma_v^2 = \text{Var}(v_{1\dots N})$$
   A near-zero $\sigma_v^2$ indicates steady convergence to baseline; high spikes indicate rapid emotional reactions.

3. **Free Energy / Surprise Entropy**:
   Mean and standard deviation of prediction errors $\delta_k = \|A p_k + b - q_k\|_2$ from the Active Inference Engine.

4. **Limbic Stability Index (LSI)**:
   A composite score in $[0.0, 1.0]$:
   $$\text{LSI} = \alpha \cdot \exp\left(-\frac{\text{Jitter}_{mean}}{50\text{ms}}\right) + \beta \cdot \exp\left(-\sigma_v^2\right) + \gamma \cdot (1.0 - \text{Saturation}_{SDM})$$
   where $\alpha=0.4, \beta=0.4, \gamma=0.2$.

---

## 2. Standalone Packaging with `electron-builder`

### `package.json` Configuration
```json
{
  "name": "lucia-desktop",
  "version": "1.0.0",
  "main": "main/main.js",
  "scripts": {
    "start": "electron .",
    "test": "jest",
    "build:win": "electron-builder --win --x64"
  },
  "build": {
    "appId": "com.lucia.companion",
    "productName": "Lucia",
    "directories": {
      "output": "dist"
    },
    "win": {
      "target": ["nsis", "portable"],
      "icon": "build/icon.ico"
    },
    "nsis": {
      "oneClick": true,
      "allowToChangeInstallationDirectory": false,
      "createDesktopShortcut": true,
      "createStartMenuShortcut": true
    }
  }
}
```

---

## 3. Desktop Companion Modes (System Tray & Mascot Mode)

### Window State Transitions
```
┌─────────────────────────────────────────────────────────────┐
│                       FULL APP WINDOW                       │
│             (Chat Window + Live Avatar + Telemetry)          │
└──────────────┬───────────────────────────────▲──────────────┘
               │                               │
       Minimize to Tray /               Restore / Hotkey
       Close Button                      (Ctrl+Shift+L)
               │                               │
               ▼                               │
┌──────────────────────────────┐ ┌─────────────┴────────────────┐
│         SYSTEM TRAY          │ │       FLOATING MASCOT        │
│    (Limbic Fast Loop active) │ │   (Compact Always-on-Top)    │
└──────────────────────────────┘ └──────────────────────────────┘
```

---

## 5. Extensibility & Modular Hook Architecture

### 5.1. Cognitive Lifecycle Hook Bus (`src/core/plugins/hook_bus.py`)

```python
class HookBus:
    def __init__(self):
        self._hooks = defaultdict(list)

    def register(self, event_name: str, callback: Callable):
        self._hooks[event_name].append(callback)

    def emit(self, event_name: str, *args, **kwargs):
        for cb in self._hooks[event_name]:
            try:
                cb(*args, **kwargs)
            except Exception:
                logger.exception("Plugin hook %s failed", event_name)
```

### 5.2. Modular Avatar Engine Registry (`electron/renderer/avatar/avatar-registry.js`)

```javascript
class BaseAvatarEngine {
  init(containerElement) {}
  updateEmotion(padState) {}
  speak(audioBlob, onComplete) {}
  resize(width, height) {}
  destroy() {}
}

class AvatarRegistry {
  constructor() {
    this.engines = new Map();
    this.activeEngine = null;
  }
  register(name, engineClass) {
    this.engines.set(name, engineClass);
  }
  use(name, container) {
    if (this.activeEngine) this.activeEngine.destroy();
    const EngineClass = this.engines.get(name);
    this.activeEngine = new EngineClass();
    this.activeEngine.init(container);
    return this.activeEngine;
  }
}
```

### 5.3. Modular Voice Provider Registry (`src/core/voice/provider.py`)

```python
class BaseVoiceProvider(ABC):
    @abstractmethod
    async def synthesize(self, text: str, **kwargs) -> bytes:
        pass

    @abstractmethod
    def list_models(self) -> List[Dict[str, Any]]:
        pass
```
