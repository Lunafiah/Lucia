# Requirements Document — Lucia Refinement, QoL & Stability Telemetry (Phase 6)

## Introduction

This document defines the requirements for **Lucia Phase 6: Refinement, Packaging, Quality-of-Life (QoL), and Long-Term Stability Telemetry**. Phase 6 transitions Lucia from a development workspace into a production-grade, single-executable Windows companion application with rich desktop presence modes, session persistence, and comprehensive limbic stability monitoring.

Phase 6 encompasses five major functional subsystems:
1. **Standalone Application Packaging (`Lucia.exe`)** — Zero-terminal one-click launcher and installer using `electron-builder` with an automated background process lifecycle.
2. **Desktop Companion Modes & Hotkeys** — System Tray integration, Always-on-Top floating mascot mode, and global keyboard shortcuts.
3. **Session Persistence & Conversation History** — Local storage for conversation turns, session archiving, and Markdown chat export.
4. **Audio Routing & Hardware Controls** — Speaker output device selection, master volume control, and phrase audio caching.
5. **Stability Telemetry & Health Evaluator** — Continuous statistical evaluation of ODE divergence, Fast-Loop jitter, Free Energy surprise distributions, and limbic stability scoring.
6. **Companion Journal & Relationship Analytics** — Longitudinal visualization of affective trajectory, intimacy maturation, and memory resonance graphs.

---

## Glossary

- **`Lucia.exe`**: The standalone Windows desktop executable that launches the user interface and coordinates backend lifecycle invisibly.
- **ProcessManager**: The Electron main process module managing the background Python API server.
- **System_Tray**: The Windows notification area taskbar tray where Lucia minimizes without terminating her limbic clock.
- **Mascot_Mode**: A compact, frameless, Always-on-Top floating avatar window mode.
- **Global_Hotkey**: An OS-wide keyboard shortcut (`Ctrl+Shift+L` or `Alt+Space`) that summons or minimizes the application from any active window.
- **Chat_History_Store**: A JSON/SQLite persistent local store (`data/chat_history.json`) preserving turns between restarts.
- **Stability_Evaluator**: An internal diagnostic engine computing the **Limbic Stability Index (LSI)**, ODE variance, Fast-Loop tick jitter, and prediction error entropy.
- **Fast_Loop_Jitter**: The deviation in milliseconds from the configured 200ms ODE integration cadence.
- **Limbic_Stability_Index (LSI)**: A composite score in $[0.0, 1.0]$ evaluating ODE numerical stability, homeostatic recovery time, and bounded belief divergence.

---

## Functional Requirements

### Requirement 1: Standalone Application Packaging (`Lucia.exe`)

**User Story:** As a user, I want to launch Lucia simply by clicking `Lucia.exe` or a desktop shortcut without seeing terminal windows or manually managing Python environments.

#### Acceptance Criteria
1. THE Build_System SHALL generate a standalone Windows executable (`Lucia.exe`) and an optional installer (`Lucia-Setup.exe`) via `electron-builder`.
2. WHEN `Lucia.exe` is launched, THE Process_Manager SHALL automatically spawn the Python limbic backend in a hidden, windowless background process.
3. THE Application SHALL display the splash screen with live hardware initialization diagnostics (GPU VRAM detection, CUDA availability, Model verification, Audio engine status).
4. WHEN the user exits the application, THE Process_Manager SHALL send clean termination signals (`SIGTERM`/`SIGINT`), wait up to 5.0 seconds for all daemon loops to join, and ensure no orphaned Python processes remain.
5. IF the required GGUF model is missing, THEN the application SHALL display a clear, user-friendly setup modal indicating the required model directory path instead of crashing.

---

### Requirement 2: Desktop Companion Presence Modes & Hotkeys

**User Story:** As a user, I want Lucia to sit in my system tray or float on my desktop while I work, and be summonable instantly via a keyboard shortcut.

#### Acceptance Criteria
1. THE Application SHALL create a native Windows System Tray icon with a context menu (`Show/Hide`, `Mascot Mode`, `Mute Voice`, `Quit`).
2. WHEN the user closes the main window (and "Minimize to Tray" is enabled), THE Application SHALL hide the window to the System Tray while keeping the limbic Fast Loop active in the background.
3. THE Application SHALL support **Mascot Mode (Floating Avatar)**: a compact, Always-on-Top, draggable window displaying only the live avatar and compact voice status.
4. THE Application SHALL register a configurable Global Hotkey (default: `Ctrl + Shift + L`) to instantly toggle visibility from anywhere in Windows.
5. WHEN the window gains focus via the hotkey, THE Chat_Input field SHALL be focused automatically.

---

### Requirement 3: Chat Persistence, Session Management & Export

**User Story:** As a user, I want my conversation history with Lucia to persist between app restarts, with the ability to clear the screen or export conversations.

#### Acceptance Criteria
1. THE Application SHALL automatically persist conversation history to `data/chat_history.json` on every completed turn.
2. WHEN the application is launched, THE Chat_Window SHALL restore the most recent conversation turns from local storage.
3. THE Chat_Header SHALL provide a **"New Topic / Clear Screen"** action that resets the visible chat feed without erasing Lucia's long-term Sparse Distributed Memory traces or affective bond.
4. THE Application SHALL provide an **"Export Chat"** feature that saves the conversation history into a formatted Markdown (`.md`) or plain text (`.txt`) file.

---

### Requirement 4: Audio Hardware Routing & Volume Control

**User Story:** As a user, I want to adjust Lucia's voice volume and choose my preferred audio output device (e.g. Headphones vs Speakers).

#### Acceptance Criteria
1. THE Avatar_Top_Bar SHALL feature an interactive **Volume Slider** controlling audio playback gain from `0%` to `100%`.
2. THE Application Settings SHALL list all available audio output devices (via Web Audio API `navigator.mediaDevices.enumerateDevices`) and allow the user to select the active speaker/headphone device.
3. THE Voice_Engine SHALL implement an in-memory short-phrase audio cache to eliminate latency for repeated acknowledgments (e.g., "I see", "Understood", "Hello").

---

### Requirement 5: Stability Telemetry & Health Monitoring Engine

**User Story:** As a developer and companion guardian, I want continuous statistical telemetry evaluating the stability of Lucia's emotional ODE, tick drift, and memory saturation over long operational periods.

#### Acceptance Criteria
1. THE FastAPI_Server SHALL expose a `GET /telemetry/stability` endpoint returning comprehensive health metrics.
2. THE Stability_Evaluator SHALL compute:
   * **Fast_Loop Tick Jitter**: Mean and maximum deviation from the 200ms cadence over the trailing 100 ticks.
   * **ODE Divergence Variance**: Variance of hidden state velocity $\|\frac{dh}{dt}\|_2$.
   * **Free Energy Surprise Histogram**: Mean and standard deviation of prediction errors from the Active Inference Engine.
   * **Limbic Stability Index (LSI)**: A composite normalized score in $[0.0, 1.0]$.
   * **SDM Saturation Rate**: Percentage of Sparse Distributed Memory capacity utilized.
3. IF the Fast_Loop fails to tick for $> 2.0$ seconds or encounters numerical NaN/Inf states, THE Stability_Evaluator SHALL record a recovery event and automatically reset state to the Philia resting baseline attractor without crashing the application.

---

### Requirement 6: Companion Journal & Affective Evolution Analytics

**User Story:** As a user, I want to view a visual journal showing how Lucia's emotional state and our relationship have matured over days and weeks.

#### Acceptance Criteria
1. THE UI SHALL provide a **Companion Journal** modal/view accessible from the navigation bar.
2. THE Journal SHALL display:
   * **Time Spent Together**: Total interaction days and completed conversation turns.
   * **Affective Evolution Graph**: A time-series chart showing Pleasure ($P$), Arousal ($A$), and Dominance ($D$) trajectory over time.
   * **Memory Resonance Topography**: Visualization of top resonant emotional memory clusters stored in Kanerva SDM.

---

### Requirement 7: Extensibility, Lifecycle Hooks & Modular Provider Architecture

**User Story:** As a developer, I want modular extension interfaces and lifecycle hooks so that future features (e.g. 3D VRM/Live2D models, screen vision, external tools, mobile sync) can be plugged in seamlessly without refactoring existing core pipelines.

#### Acceptance Criteria
1. THE Orchestrator SHALL provide a non-blocking **Plugin Hook Bus** (`src/core/plugins/`) exposing lifecycle events:
   * `on_turn_start(input_text, context)`
   * `on_stimulus_encoded(stimulus_vector)`
   * `on_somatic_updated(pad_state, somatic_markers)`
   * `on_prompt_assembled(prompt_text)`
   * `on_response_generated(response_text)`
   * `on_turn_completed(turn_record)`
2. THE Electron Avatar Subsystem SHALL define a standard **`BaseAvatarEngine`** interface allowing hot-swapping between `CanvasAvatarEngine`, `Live2DAvatarEngine`, and `VRMAvatarEngine`.
3. THE Voice Engine SHALL define a standard **`BaseVoiceProvider`** interface supporting direct RVC, Kokoro/Piper, or future custom synthesizers.
4. ALL Persistent Schemas (chat history, telemetry logs) SHALL include a schema version tag (`"version": 1`) and open-ended `metadata: {}` dictionary to allow backward-compatible forward extensions.
