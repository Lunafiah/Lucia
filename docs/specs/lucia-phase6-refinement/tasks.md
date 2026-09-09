# Implementation Plan: Lucia Refinement, QoL & Stability Telemetry (Phase 6)

## Overview

Implement standalone packaging (`Lucia.exe`), desktop presence modes (System Tray, Floating Mascot, Global Hotkey), chat persistence, audio routing, and continuous limbic stability telemetry.

---

## Tasks

- [ ] 1. Stability Evaluator & Telemetry Subsystem
  - [ ] 1.1 Implement `StabilityEvaluator` in `src/core/telemetry/stability_evaluator.py`
    - Rolling window calculation of Fast-Loop tick jitter (mean and max over trailing 100 ticks).
    - Velocity variance calculation $\sigma_v^2$ of hidden state transitions.
    - Free Energy surprise distribution tracking (mean, std, min, max).
    - Composite Limbic Stability Index (LSI) calculation.
  - [ ] 1.2 Add `GET /telemetry/stability` endpoint to `src/api/server.py`
  - [ ] 1.3 Write unit tests in `tests/unit/test_stability_evaluator.py`
  - [ ] 1.4 Integrate live stability metrics into `electron/renderer/debug/panel.js`

- [ ] 2. Chat Persistence & Session Store
  - [ ] 2.1 Implement `ChatHistoryStore` in `src/core/storage/history_store.py`
    - JSON persistence in `data/chat_history.json`.
    - Session appending, turn retrieval, and markdown export formatting.
  - [ ] 2.2 Add `GET /history`, `POST /history/append`, `DELETE /history`, `GET /history/export` in `src/api/server.py`
  - [ ] 2.3 Update `electron/renderer/chat/chat.js` to restore history on startup and add "Clear Screen" & "Export" buttons
  - [ ] 2.4 Write unit tests in `tests/unit/test_history_store.py`

- [ ] 3. Audio Hardware Routing & Volume Controls
  - [ ] 3.1 Implement master volume slider in `electron/renderer/avatar/avatar.js` and `lip-sync.js`
  - [ ] 3.2 Implement audio device output enumeration and switching in `electron/renderer/audio/audio-router.js`
  - [ ] 3.3 Add in-memory short-phrase audio cache in `src/core/voice/voice_engine.py`

- [ ] 4. Desktop Companion Modes & Hotkeys
  - [ ] 4.1 Implement `TrayManager` in `electron/main/tray-manager.js` (tray icon, context menu, minimize to tray)
  - [ ] 4.2 Implement `HotkeyManager` in `electron/main/hotkey-manager.js` (global `Ctrl+Shift+L` toggle)
  - [ ] 4.3 Implement `MascotWindowManager` in `electron/main/mascot-window.js` (Always-on-Top floating avatar mode)
  - [ ] 4.4 Wire IPC channels in `electron/main/ipc-bridge.js` and `electron/preload/preload.js`

- [ ] 5. Companion Journal & Affective Analytics
  - [ ] 5.1 Implement Companion Journal modal in `electron/renderer/journal/journal.js` & `journal.css`
  - [ ] 5.2 Render longitudinal PAD trajectory chart and intimacy maturity scoring
  - [ ] 5.3 Render SDM memory resonance highlights

- [ ] 6. Standalone Packaging Configuration
  - [ ] 6.1 Configure `electron-builder` in `electron/package.json` with NSIS and portable targets
  - [ ] 6.2 Add Windows application icon in `electron/build/icon.ico`
  - [ ] 6.3 Create one-click root launcher script `Start-Lucia.bat`
  - [ ] 6.4 Document packaging workflow in `docs/USER_MANUAL.md`

- [ ] 7. Verification & Checkpoint
  - [ ] 7.1 Run full Python test suite: `pytest tests/unit tests/property tests/integration -v`
  - [ ] 7.2 Run full Electron Jest suite: `npm test` inside `electron/`
  - [ ] 7.3 Commit and push Phase 6 specs and code to GitHub
