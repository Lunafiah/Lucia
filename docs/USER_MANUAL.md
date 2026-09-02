# Lucia — User & Operation Manual

> **Step-by-step guide to installing, configuring, running, and interacting with Lucia.**

---

## 1. Prerequisites & Installation

### System Requirements
* **OS**: Windows 10/11 (x64)
* **GPU**: NVIDIA GPU (e.g. RTX 3050 Ti Laptop or higher) with CUDA support
* **RAM**: 8GB+ RAM
* **Software**:
  * Python 3.10+ (Recommended: Python 3.12 in `.venv`)
  * Node.js 18+ & npm

### Setup Steps

1. **Activate Python Virtual Environment & Install Dependencies**:
   ```powershell
   # In project root
   .\.venv\Scripts\Activate.ps1
   pip install -r requirements.txt
   ```

2. **Install Electron Frontend Dependencies**:
   ```powershell
   cd electron
   npm install
   cd ..
   ```

3. **Check LLM Model Placement**:
   Place your GGUF model in the `models/` directory (e.g. `models/LFM2.5-1.2B-Instruct-Q4_K_M.gguf`).

---

## 2. Setting Up Your RVC Character Voice Models

Lucia features a **direct, self-contained RVC voice engine**—no third-party software or cloud subscriptions needed.

### Adding Your Voice Models:
Copy your character folder from `C:\Users\Lunafiah\ultimate-rvc\models\rvc\voice_models\` into `models/voice/rvc/`:

```
Lucia/
└── models/
    └── voice/
        └── rvc/
            ├── my_character/
            │   ├── my_character.pth
            │   └── my_character.index
            └── another_character/
                ├── voice.pth
                └── voice.index
```

* Each subfolder name will automatically appear as a selectable voice in the application's top-right voice dropdown.
* If no custom model is selected, Lucia automatically uses her high-quality built-in female base voice (`en-US-AnaNeural`).

---

## 3. Setting Up Avatar Models (2D Sprites, Live2D, 3D VRM)

Lucia includes a built-in 60 FPS interactive Canvas rig out-of-the-box. If you want to use custom 2D expressions, Live2D, or 3D VRM character models, place them in the **`models/avatar/`** directory:

### Structure:
```
Lucia/
└── models/
    └── avatar/
        ├── sprites/                 # 2D Expression PNG Sets
        │   └── my_character/
        │       ├── idle.png         (Default resting pose)
        │       ├── smile.png        (High pleasure / warmth)
        │       ├── blush.png        (Pleasure + high arousal)
        │       ├── speaking.png     (Open mouth for lip-sync)
        │       └── thinking.png     (Reflection / load)
        │
        ├── live2d/                  # Live2D Cubism Models
        │   └── my_character/
        │       ├── my_character.model3.json
        │       ├── my_character.moc3
        │       ├── textures/
        │       └── motions/
        │
        └── vrm/                     # 3D Humanoid VRM Models
            └── my_character.vrm
```

---

## 4. Launching & Packaging Lucia

### Option A: Direct Double-Click Launcher (`Start-Lucia.bat`) (Recommended)
Simply double-click **`Start-Lucia.bat`** in the project root. It will automatically check dependencies and launch the companion window.

### Option B: npm start (Developer Mode)
```powershell
cd electron
npm start
```

### Option C: Building Standalone `Lucia.exe`
To package Lucia into an installer (`Lucia-Setup.exe`) or portable `.exe` using `electron-builder`:
```powershell
cd electron
npm run build:win
```
The packaged binary will be generated in `electron/dist/`.

---

## 5. Desktop Presence Modes & Global Shortcuts

* **Minimize to System Tray**: Closing or minimizing the main window sends Lucia to your Windows notification tray. Her limbic Fast Loop keeps ticking continuously in the background!
* **Global Hotkey (`Ctrl + Shift + L`)**: Press `Ctrl + Shift + L` from anywhere in Windows (while coding, gaming, or browsing) to instantly summon or hide Lucia.
* **Floating Mascot Mode**: Right-click Lucia's system tray icon and select **Floating Mascot Mode** to switch to a compact Always-on-Top floating avatar window.

---

## 6. Desktop Interface Guide

```
┌───────────────────────────────────────────────┬──────────────────────────────────────────────┐
│                  CHAT PANE                    │            PRESENCE & TELEMETRY              │
├───────────────────────────────────────────────┼──────────────────────────────────────────────┤
│ ✦ Lucia (Active & Mindful) [📖 Journal][Auto] │  ┌────────────────────────────────────────┐  │
│                                               │  │ 🟢 Presence [Volume ━●━] [RVC ▼] 🔊   │  │
│ ┌───────────────────────────────────────────┐ │  │                                        │  │
│ │ ✨ Welcome to Lucia                       │ │  │          🎭 [LIVE CANVAS AVATAR]       │  │
│ └───────────────────────────────────────────┘ │  │     (Eye blinks, gaze, lip-sync, blush)│  │
│                                               │  └────────────────────────────────────────┘  │
│ [You]: Hello Lucia!                           │                                              │
│                                               │  EMOTIONAL TELEMETRY (LIVE 500ms)            │
│ [Lucia]: Hi! It's so nice to talk with you.   │  • Pleasure  (P) [=======|========] +0.32    │
│          🔊 [Speaks aloud in RVC voice]       │  • Arousal   (A) [===|============] -0.04    │
│          🎭 [Avatar lip-syncs & smiles]       │  • Dominance (D) [=======|========] +0.08    │
│                                               │                                              │
│ ┌───────────────────────────────────────┬───┐ │  LIMBIC STABILITY & HEALTH (LSI)             │
│ │ Type your message here...             │ ➤ │ │  • Stability Score: 100% (NOMINAL)           │
│ └───────────────────────────────────────┴───┘ │  • Fast-Loop Jitter: 0.2ms                   │
└───────────────────────────────────────────────┴──────────────────────────────────────────────┘
```

### 1. The Interactive Avatar Stage
* **Voice Model Selector**: Click the dropdown at the top right of the avatar to switch between the default voice and any discovered RVC models.
* **Mute Toggle**: Click the speaker icon (`🔊`) to instantly mute or unmute her spoken voice.
* **Cursor Gaze Tracking**: Move your mouse anywhere on screen—Lucia’s eyes and head subtly follow your cursor.
* **Dynamic Emotions**: As her internal Pleasure ($P$) increases, her cheeks softly blush pink and her mouth curves into a warm smile.
* **60 FPS Lip-Syncing**: When speaking, her mouth accurately opens and articulates matching the audio frequency formants.

### 2. The Chat Window
* **Sending Messages**: Type your message and press `Enter` (or click `➤`).
* **Multi-Line**: Press `Shift + Enter` to insert a new line without sending.
* **Typing Indicator**: Shows animated pulsing dots while her brain reflects and generates responses.

### 3. Emotional Telemetry Panel (Real-Time 500ms)
* **PAD Attractor State**:
  * **Pleasure ($P$)**: Mood valence from $-1.0$ (distressed) to $+1.0$ (joyful/warm).
  * **Arousal ($A$)**: Physiological energy from $-1.0$ (calm/sleepy) to $+1.0$ (excited/alert).
  * **Dominance ($D$)**: Social agency from $-1.0$ (submissive/shy) to $+1.0$ (confident/assertive).
* **Somatic Markers**:
  * **Stability**: Resistance against emotional turbulence.
  * **Energy**: Available conversational vitality (recharges during pauses).
  * **Cognitive Load & Tension**: Internal processing pressure.
* **Behavioral Conditioning**: Shows live adjustments to Token Budget, LLM Temperature, Simulated Latency, and Reasoning Depth.
* **Affective Memory**: Live counter of accumulated emotional memory traces stored in Sparse Distributed Memory.

---

## 7. Configuration & Customization

All primary options can be configured in [`config/ui.json`](file:///c:/Users/Lunafiah/Desktop/My_project/Lucia/config/ui.json):

```json
{
  "api": {
    "host": "127.0.0.1",
    "port": 8765,
    "startupTimeoutMs": 30000
  },
  "model": {
    "path": "models/LFM2.5-1.2B-Instruct-Q4_K_M.gguf",
    "profile": "auto"
  },
  "presence": {
    "voice": {
      "active_model": "default",
      "models_dir": "models/voice/rvc",
      "pitch_shift": 0
    }
  }
}
```

* **`model.profile`**: Set to `"laptop"` (optimized for 4GB VRAM), `"desktop"`, `"high_end"`, or `"auto"`.
* **`presence.voice.pitch_shift`**: Adjust pitch in semitones (e.g. `+2` for higher tone, `-2` for deeper tone, `0` for natural default).

---

## 8. Frequently Asked Questions (FAQ)

**Q: Can Lucia run completely offline without internet?**  
**A:** Yes! The LLM, continuous emotion ODE, memory decay, active inference, RVC voice conversion, and avatar rendering run 100% locally on your laptop.

**Q: Does voice synthesis slow down text generation or overload my GPU?**  
**A:** No. Voice synthesis executes in quick, lightweight bursts ($\sim 150\text{MB}$ memory) that never compete with your LLM token generation.

**Q: How do I backup Lucia’s memories?**  
**A:** Her memory traces and learned LNN plasticity are saved within the project. You can copy the workspace or commit changes to Git to preserve her developmental journey.
