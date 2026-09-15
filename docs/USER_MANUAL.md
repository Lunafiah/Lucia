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

Lucia includes four distinct avatar rendering engines out-of-the-box:
1. **🎨 2D Procedural Canvas**: Built-in 60 FPS interactive vector face (zero dependencies, 0 MB disk, runs on any PC).
2. **🖼️ 2D Expression Sprites**: PNG sprite sets reacting to emotion, thinking, and lip-sync.
3. **🎬 Live2D Cubism 4**: Full WebGL Live2D interactive models with parameter-driven expressions and physics.
4. **🌐 3D VRM Humanoid**: Full 3D humanoid avatars with skeletal rigging, morph targets, and cursor-tracking gaze.

### Directory Structure for Custom Models:
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

> [!NOTE]
> All necessary WebGL libraries (`live2dcubismcore.min.js`, `pixi.min.js`, `cubism4.min.js`, `three.min.js`, `GLTFLoader.js`, `three-vrm.js`) are pre-installed in [`electron/renderer/libs/`](file:///c:/Users/Lunafiah/Desktop/My_project/Lucia/electron/renderer/libs/). Lucia scans these directories on launch and dynamically populates the Model selector.

---

## 4. Launching & Packaging Lucia

### Option A: Direct Double-Click Launcher (`Start-Lucia.bat`) (Recommended)
Simply double-click **`Start-Lucia.bat`** in the project root. It will automatically check dependencies, start the background core, and launch the companion window.

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
* **Floating Mascot Mode (`🐾 Mascot`)**: Click the Mascot button in the top header (or right-click the tray icon) to switch into a transparent, frameless, Always-on-Top desktop companion.

---

## 6. Desktop Interface Guide: Personal Digital Room

Lucia uses a **Personal Digital Room** interface designed with progressive disclosure. Rather than cluttering the screen with dense diagnostic gauges, the primary interface prioritizes warmth, embodiment, and natural conversation, while engineering telemetry is accessible via dedicated modals.

### Window Layout Structure

```
┌────────────────────────────────────────────────────────────────────────────────────────────────────────┐
│ ✦ Lucia  [🎂 Day 1]               [💬 Talk]  [🧠 Memories]  [📖 Journal]  [⚙️ Settings]       [🐾 Mascot] ✕ │
├─────────────────────────────────────────────────┬──────────────────────────────────────────────────────┤
│               AVATAR STAGE                      │                  CONVERSATION PANE                   │
│  ┌───────────────────────────────────────────┐  │  ┌────────────────────────────────────────────────┐  │
│  │                                           │  │  │ ✨ Welcome to Lucia                            │  │
│  │            🎭 [AVATAR MODEL]              │  │  └────────────────────────────────────────────────┘  │
│  │         (Canvas / Sprites / Live2D / VRM) │  │                                                      │
│  │                                           │  │  [You]: Hello Lucia!                                 │
│  │   • Autonomous micro-gaze & blinking      │  │                                                      │
│  │   • Real-time Web Audio lip-sync          │  │  [Lucia]: Hi! It's so nice to see you.               │
│  │   • Emotionally responsive blendshapes    │  │           🔊 [Local RVC Voice Synthesis]             │
│  │                                           │  │                                                      │
│  └───────────────────────────────────────────┘  │  ┌─────────────────────────────────────────────┬─┬─┐  │
│  [Engine ▼] [Model ▼] [Voice ▼] [━●━] [🔊 Mute] │  │ Type a message... (Shift+Enter for newline) │🎙│➤│  │
│  • Drag to Pan • Scroll to Zoom • Double-click  │  └─────────────────────────────────────────────┴─┴─┘  │
└─────────────────────────────────────────────────┴──────────────────────────────────────────────────────┘
```

### 1. Navigation Header & Companion Status
* **Companion Identity**: Displays friendship age (`🎂 Day N`), current conversation mode, and connection status.
* **Views**:
  * **💬 Talk**: The primary conversational room and live avatar stage.
  * **🧠 Memories**: Browse long-term episodic memories co-encoded with affective states.
  * **📖 Journal**: Inspect relationship milestones, interaction history, and developmental trajectory.
  * **⚙️ Settings**: Hardware tier selection, model configuration, audio devices, and display options.
  * **🐾 Mascot Mode**: Switch immediately to the transparent floating desktop mascot.

### 2. Avatar Stage (Embodied Presence)
* **Multi-Engine Rendering**: Seamlessly toggle between `🎨 2D Canvas`, `🖼️ 2D Sprites`, `🎬 Live2D`, and `🌐 3D VRM`.
* **Voice & Audio Controls**: Choose local RVC voice profile, adjust master volume, or mute.
* **Stage Manipulation**:
  * **Pan**: Click and drag to reposition the avatar.
  * **Zoom**: Scroll wheel directly over the avatar to zoom in or out.
  * **Reset**: Double-click the stage to restore default zoom and alignment.

### 3. Conversation Pane & Voice Input
* **Natural Dialogue Flow**: Chat history displays Lucia's responses alongside subtle prosody and voice playback.
* **Continuous Microphone Input (`🎙️`)**: Hands-free voice chat powered by local Web Audio VAD and `faster-whisper`. Speech is transcribed offline with zero cloud API keys.

### 4. Diagnostics & Telemetry Modal (`Ctrl + Shift + D`)
To maintain a natural companion atmosphere, raw mathematical diagnostics are cleanly separated from the daily chat feed. Press **`Ctrl + Shift + D`** (or click *Diagnostics* in Settings) to open the real-time engineering telemetry panel:
* **Limbic ODE State**: Fast reactive latent vector $\mathbf{h}_{\text{fast}} \in \mathbb{R}^{32}$, slow affective latent state $\mathbf{s}_{\text{slow}} \in \mathbb{R}^{16}$, and 3D PAD coordinates.
* **Limbic Stability Index (LSI)** & Numerical ODE step jitter ($< 2\text{ms}$).
* **Relational State Vector**: $\mathbf{R} = [\text{Affinity}, \text{Familiarity}, \text{Trust}, \text{Depth}] \in [0, 1]^4$ and Tier 2 attractor displacement.
* **Consolidation Status**: Replay buffer size, offline BPTT loss, homeostatic anchor distance, and parameter swap latency.
* **Memory & Storage Metrics**: Active SDM trace count and decay sweep statistics.

---

## 7. Floating Mascot Mode Guide

In Mascot Mode, Lucia becomes a frameless, transparent, Always-on-Top companion that lives directly on your desktop:

```
          (\_/)
         ( •‿• )   <-- Model (Click & drag to move window anywhere)
        / >❤️< \
       (______)
   ┌───────────────────────┐
   │ 💬  🎬  🔊  🎙️  ⚙️  │ ✕ │  <-- Model-Anchored Toolbar Dock
   └───────────────────────┘      (Follows character bottom center)
```

### Key Mascot Features:
1. **Direct Model Dragging**: Click and drag the character model with your mouse to move the mascot window anywhere across your screens.
2. **Dynamic Model-Anchored Toolbar**: The floating toolbar dock automatically sticks directly beneath the character's feet (`getModelBounds()`), adjusting smoothly regardless of how you zoom or position the character.
3. **Smart Hover Zoom**: Scroll wheel to zoom in or out **only functions when your cursor is positioned directly over the avatar model**, with an 800ms cooldown after dragging to prevent touchpad inertial momentum from blowing up character size.
4. **Shift-Drag to Pan**: Hold `Shift` while left-clicking (or use middle-click) to freely pan the avatar within the mascot frame.
5. **Double-Click Reset**: Double-click the avatar (or click Reset Avatar in Settings) to instantly restore default 1.0× scale, center pan position, and reset mascot window boundaries back to standard 380×540 unmaximized bounds.

### Mascot Toolbar Controls:
* **💬 Quick Chat**: Opens an inline chat popup allowing you to type messages and receive spoken answers without opening the main window.
* **🎬 Model Switcher**: Swap avatar engine (Canvas, Sprites, Live2D, VRM) and model directly on your desktop.
* **🔊 Audio & Voice**: Select your microphone and speaker devices, adjust master volume, and choose RVC voice models.
* **🎙️ Toggle Mic**: Turn hands-free continuous voice input on or off (powered by local faster-whisper STT).
* **⚙️ UI Settings**: Adjust avatar scale slider (30%–400%), mascot window opacity (30%–100%), reset model & window bounds, open journal, or return to the main window.
* **✕ Exit**: Close mascot mode and return to main window.

---

## 8. System Settings & Hardware Scalability

Open the Settings modal via the **`⚙️ Settings`** button in the main window header:

### 1. Hardware Scalability & Optimization Profile
Dynamically adjusts model offloading, context length, and memory capacity to match your system hardware:
* **Auto-Detect**: Automatically selects the optimal tier based on detected GPU VRAM and compute capabilities.
* **High-End Tier (16GB+ VRAM)**: Full GPU layer offloading, 8,192 token context, 10,000 SDM traces.
* **Desktop Performance (8–12GB VRAM)**: Full GPU offloading for 3B/7B models, 4,096 token context.
* **Laptop Balanced (4–6GB VRAM)**: 32 GPU layers offloaded, 2,048 token context (ideal for RTX 3050 Ti Laptop).
* **Low-Power / Battery Saver (CPU-Only)**: Zero GPU VRAM usage, minimal RAM footprint, energy-efficient background tick rate.

### 2. Avatar Graphics & Energy Optimization
* **Target Framerate**:
  * **60 FPS**: Ultra-fluid animation, ideal when plugged into AC power.
  * **30 FPS**: Reduces avatar CPU/GPU rendering usage by up to 50%, maximizing laptop battery life.
* **Default Mascot Opacity**: Adjust transparency of the mascot window from 30% to 100%.

### 3. Audio & Voice Hardware
* **Microphone (Input)**: Select your preferred input microphone.
* **Speaker (Output)**: Select your preferred output device (headphones or speakers).

---

## 9. Frequently Asked Questions (FAQ)

**Q: Can Lucia run completely offline without internet?**  
**A:** Yes! The LLM, continuous emotion ODE, memory decay, active inference, RVC voice conversion, and avatar rendering run 100% locally on your PC.

**Q: Does voice synthesis slow down text generation or overload my GPU?**  
**A:** No. Voice synthesis executes in quick, lightweight bursts ($\sim 150\text{MB}$ memory) that never compete with your LLM token generation.

**Q: Why doesn't zooming work when scrolling outside the character?**  
**A:** This is an intentional safeguard! To prevent accidental zooming when dragging windows with a laptop touchpad, zoom only activates when your mouse cursor is directly hovering over the character model.

**Q: How do I backup Lucia’s memories?**  
**A:** Her memory traces, learned LNN plasticity, and companion profile are saved in `data/`. You can copy the workspace or commit changes to Git to preserve her developmental journey.
