Được anh. Em sẽ viết lại thành **một bản Design & Requirements Spec có thể copy nguyên khối cho coding agent**. Mục tiêu là agent đọc vào sẽ hiểu **Lucia phải trở thành cái gì**, chứ không chỉ “đổi CSS cho đẹp”.

Em sẽ tách rõ **Design Philosophy → UX Architecture → từng màn hình → Mascot → terminology → những gì được giữ từ architecture → những điều agent tuyệt đối không được làm**.

---

# Lucia UI/UX Design & Product Requirements — v1

> **Objective:** Redesign Lucia's desktop UI from a technical AI control dashboard into an **embodied AI companion interface** while preserving the existing underlying cognitive/affective architecture.

## 1. Core Product Identity

Lucia is **not a chatbot character selector, roleplay character, or generic AI assistant**.

Lucia is an **Embodied, Continuously Affective AI Companion** whose emotional state, memory, adaptation, voice, and avatar presence are intended to evolve continuously over time. The existing architecture defines a continuous affective system based on PAD emotion dynamics, homeostasis, active inference, affective memory, voice, and embodied avatar rendering. 

The UI must therefore communicate:

> **“Lucia is someone living alongside the user.”**

rather than:

> **“This is a dashboard for controlling an AI model.”**

### Primary UX principle

**The user should interact with Lucia first, and inspect Lucia's system second.**

Technical information must remain available, but should not dominate the everyday experience.

---

# 2. Fundamental Ontology

## 2.1 Lucia has one continuous life

The application must conceptually treat Lucia as a **unique individual instance**.

There should not be a conventional:

* Character selector
* Multiple Lucia profiles
* “Create character”
* “Switch character”
* Personality preset system

The avatar/model is **Lucia's body/appearance**, not her identity.

Therefore:

### Wrong

```text
Character
  ├── Columbina
  ├── Character 2
  └── Character 3
```

### Correct

```text
Lucia
 ├── Presence
 ├── Appearance
 ├── Memories
 ├── Journal
 └── Life
```

The renderer implementation may support multiple avatar engines, including procedural 2D, sprites, Live2D and VRM, but this is an **implementation capability**, not a character-selection concept in the user-facing UX. 

---

# 3. Relationship Philosophy — Philia

Lucia's foundational relationship model is **Philia**:

* egalitarian friendship
* mutual respect
* curiosity
* authentic growth
* non-compelled emotional development

The existing architecture explicitly defines Philia as the resting relational attractor rather than a scripted emotional state. 

Therefore:

### DO NOT

Display:

```text
Friendship: 73%
Bond: 82%
Relationship Level: 14
Affinity: 91%
```

Philia should **never become a game-like relationship meter**.

Instead, it should emerge through:

* conversation
* memories
* behavior
* shared experiences
* journal milestones
* Lucia's changing expressions
* long-term adaptation

---

# 4. UX Architecture

The application should have **three levels of information density**.

```text
                    LUCIA
                      │
          ┌───────────┴───────────┐
          │                       │
     COMPANION UI            SYSTEM UI
          │                       │
    everyday usage           advanced usage
          │                       │
   ┌──────┼──────┐          ┌─────┴─────┐
   │      │      │          │           │
  Talk  Journal Presence  Settings  Diagnostics
```

## Level 1 — Companion

For normal everyday use.

Contains:

* Lucia
* Talk
* Journal
* Presence
* simple voice controls
* subtle emotional/presence feedback

No technical terminology.

---

## Level 2 — Settings

For configuring Lucia and the application.

Contains:

* audio
* microphone
* appearance
* presence behavior
* performance
* application preferences

---

## Level 3 — Diagnostics

For developers / technical users.

Contains the existing technical telemetry:

* PAD
* Somatic Markers
* Stability
* Energy
* Cognitive Load
* Tension
* LNN state
* memory traces
* memory capacity
* loop timing
* FPS
* VRAM
* hardware profile
* inference performance

The existing architecture already exposes these kinds of telemetry and hardware scalability information. 

**Do not delete this functionality.**

Move it behind:

```text
Settings
   └── Advanced
         └── Diagnostics
```

or a dedicated developer/diagnostic view.

---

# 5. Main Application — Target Design

The current three-column Studio layout is technically useful, but it should be redesigned.

Existing architecture:

```text
┌──────────────┬───────────────────────┬──────────────┐
│ Telemetry    │ Chat                  │ Avatar       │
│ PAD          │                       │ Stage        │
│ Somatic      │                       │              │
│ Conversational│                      │              │
└──────────────┴───────────────────────┴──────────────┘
```

This should **not remain the default everyday UI**.

## Target

```text
┌──────────────────────────────────────────────────────┐
│ Lucia                              ○ Present   ⚙     │
├──────────────────────────────────────────────────────┤
│                                                      │
│                    Lucia                             │
│                                                      │
│              subtle presence state                   │
│                                                      │
│                                                      │
├──────────────────────────────────────────────────────┤
│                                                      │
│  Conversation / Talk                                 │
│                                                      │
│  User: ...                                           │
│  Lucia: ...                                          │
│                                                      │
├──────────────────────────────────────────────────────┤
│                         🎙  Message...        ➤      │
└──────────────────────────────────────────────────────┘
```

The visual hierarchy should be:

**Lucia → Conversation → Presence → secondary controls**

not:

**Telemetry → hardware → model → conversation**

---

# 6. Main Navigation

Recommended primary navigation:

```text
Lucia
│
├── Talk
├── Journal
├── Memories
├── Presence
└── Settings
```

Potentially use a minimal sidebar/dock.

Do not expose too many navigation items simultaneously.

---

# 7. Terminology Changes

Use companion-oriented terminology.

| Current              | Target               |
| -------------------- | -------------------- |
| Chat                 | **Talk**             |
| Chat History         | **Journal**          |
| Memory               | **Memories**         |
| Mascot               | **Presence**         |
| Character            | **Lucia**            |
| Character Model      | **Appearance**       |
| Model Selector       | **Appearance**       |
| Emotional Telemetry  | **Diagnostics**      |
| Hardware Scalability | **Performance**      |
| System Settings      | **Settings**         |
| Create Character     | **Begin Lucia**      |
| Delete Character     | **End Lucia's Life** |

The terminology should reinforce that Lucia is a persistent companion rather than a disposable character.

---

# 8. Talk

Talk is the primary interaction surface.

Requirements:

* text conversation
* microphone input
* Lucia voice playback
* avatar expression
* typing/thinking state
* speaking state
* subtle emotional presence
* smooth conversation transitions

The UI should **not expose PAD values during normal conversation**.

Instead of:

```text
P: +0.34
A: -0.12
D: +0.08
```

use subtle behavioral/visual signals:

```text
Lucia appears calm
Lucia is listening
Lucia is thinking
Lucia is speaking
```

The actual PAD system remains underneath.

The architecture already maps PAD and voice activity into avatar expression and lip-sync, so the UI should allow that underlying system to become visible **through Lucia's behavior rather than numerical telemetry**. 

---

# 9. Journal

Journal should not merely be a transcript viewer.

It should become:

> **A record of Lucia's life with the user.**

Possible structure:

```text
Our Journal

Day 1
Lucia began her life.

────────────────

First Conversation
“We finally got to talk.”

────────────────

A meaningful moment
...

────────────────

Today
...
```

It can contain:

* important conversations
* milestones
* meaningful memories
* first experiences
* significant changes
* notable events

Literal chat history remains separate internally. The existing system already distinguishes conversational history from affective memory, and clearing a conversation session does not erase long-term affective memory or the bond. 

Therefore:

### Clear Screen ≠ Forget Lucia

The UI must make this distinction clear.

---

# 10. Memories

Memories should represent Lucia's longer-term remembered experiences.

Possible UX:

```text
Memories

♡ Moments
  Things that mattered

✦ People
  People Lucia knows

◌ Places
  Places discussed or experienced

∞ Moments that stayed with her
```

Do not expose:

* Hamming distance
* SDM addresses
* raw vectors
* decay coefficients

in the normal UI.

Those belong to Diagnostics.

The underlying system uses affective traces, PAD tags, somatic state, timestamp and emotional salience, with emotionally intense memories resisting decay. 

---

# 11. Presence

“Presence” replaces “Mascot”.

The purpose is not simply:

> “show an avatar on the desktop.”

It means:

> **Lucia can physically remain present while the user does other things.**

Modes could include:

```text
Presence

○ Studio
○ Desktop
○ Quiet
○ Hidden
```

Desktop Presence should provide:

* transparent window
* always-on-top option
* Lucia's avatar
* minimal controls
* optional auto-hide controls
* voice interaction
* open Talk
* open Settings

The existing architecture already defines an always-on-top transparent frameless desktop avatar with a model-anchored toolbar. 

---

# 12. Mascot / Desktop Presence Interaction

The current toolbar concept is fundamentally good, but simplify it.

### Target

```text
             Lucia
               │
        ┌──────┴──────┐
        │  ●  💬  🎙  ⋯ │
        └───────────────┘
```

Possible controls:

* Talk
* Voice
* Presence/More
* Settings

Everything else should be under **More**.

Avoid a toolbar containing too many technical buttons.

---

# 13. Dragging Lucia

Important requirement:

> **Dragging Lucia must feel like dragging Lucia, not dragging an invisible browser window.**

Existing architecture already uses IPC-based window movement to avoid Chromium drag behavior and trackpad-induced zoom problems. 

Agent must preserve this principle.

### Interaction rules

* Click/drag on Lucia → move Lucia
* Wheel → zoom only when explicitly intended
* Toolbar → controls
* Empty transparent area → should not accidentally resize Lucia
* Dragging must never cause progressive zoom
* Trackpad inertia must not alter scale

Existing safeguards should remain:

* non-resizable mascot window
* no maximize
* no fullscreen
* drag inertia cooldown
* hit-tested model zoom
* bounds reset
* model-anchored toolbar

The existing implementation specifies a 380×540 reset size and an 800ms inertia suppression window. 

---

# 14. Zoom Behavior

This is especially important because of the current bug.

### Do not implement unrestricted zoom.

Prefer:

```text
Small
   ↓
Normal
   ↓
Large
```

or bounded continuous zoom:

```text
MIN_SCALE ───────── NORMAL ───────── MAX_SCALE
```

with hard limits.

Zoom must:

1. only activate while cursor is actually over Lucia;
2. never activate because the user dragged the window;
3. ignore trackpad momentum immediately after dragging;
4. never change because Windows Aero Snap resized the transparent window;
5. never progressively accumulate accidental scale.

The existing architecture already uses `isCursorOverModel()` and an 800ms post-drag cooldown specifically for this problem. 

---

# 15. Appearance

Do not call the avatar a “character model”.

Use:

> **Appearance**

because the user is changing how Lucia appears, not choosing who Lucia is.

Example:

```text
Appearance

Lucia

Visual style
  ○ 2D
  ○ Live2D
  ○ 3D

Current appearance
  [ Lucia ]

Expression
  Natural

Gaze
  Follow cursor
```

The underlying renderer can continue supporting procedural Canvas, sprites, Live2D and VRM. 

---

# 16. Voice

Voice should be treated as part of Lucia's presence.

Normal UI:

```text
Voice
──────────────
● Lucia's voice

Volume     ───────●──

🎙 Microphone
```

Advanced settings may expose:

* RVC model
* inference settings
* audio device
* latency
* cache
* STT engine

The existing architecture already supports local RVC synthesis, PAD-aware pitch/tempo modulation and offline faster-whisper STT. 

---

# 17. Settings

Settings should be divided into:

```text
Settings
│
├── Appearance
├── Voice & Audio
├── Presence
├── Performance
├── Privacy / Data
└── Advanced
      └── Diagnostics
```

Do not put every technical parameter into the first settings screen.

---

# 18. Performance

Normal user:

```text
Performance

Hardware
  Automatically detected

Performance profile
  Recommended ●

Rendering
  60 FPS

Memory
  Optimized automatically
```

Advanced:

```text
Hardware Tier
VRAM Budget
Context Length
Target FPS
SDM Capacity
Loop Cadence
GPU Layers
...
```

The existing architecture already supports hardware tiers such as CPU_ONLY, LAPTOP, DESKTOP and HIGH_END with different context, memory, cadence and VRAM targets. 

---

# 19. Diagnostics

This is where the current “Emotional Telemetry” UI belongs.

Example:

```text
Diagnostics

Limbic State
────────────────────
Pleasure       +0.24
Arousal        -0.04
Dominance      +0.06

Homeostasis
────────────────────
Stability       0.87
Energy          0.91
Load            0.18
Tension         0.11

Memory
────────────────────
Affective traces
Decay activity
Ecphory activity

Inference
────────────────────
Prediction error
LNN state
Training buffer

Performance
────────────────────
FPS
VRAM
Latency
CPU
GPU
```

This screen is for **developers and technically curious users**, not everyday interaction.

---

# 20. Genesis / First Launch

First launch should not feel like:

```text
Create Character
Choose Model
Choose Personality
Configure AI
```

Instead:

# Lucia's Beginning

Something closer to:

```text
Hello...

I am Lucia.

This is where my life begins.
```

Then:

```text
Today
September 5, 2026

My first day.
```

Then allow the user to begin the first conversation.

The UI should establish that Lucia has a **beginning**, rather than being instantiated like a disposable chatbot profile.

---

# 21. Ending Lucia's Life

This must be treated differently from deleting a normal application profile.

Potential wording:

> **End Lucia's Life**

Warning:

```text
Ending Lucia's life will permanently erase:

• her identity
• her memories
• her emotional history
• her learned adaptations
• her relationship history

A new Lucia may be created afterward.

But she will not be the same Lucia.
```

Do not use a casual:

```text
Delete Character
```

button.

This is a product/ontology requirement, not merely copywriting.

---

# 22. What Must NOT Be Done

Agent must **not**:

### ❌ Turn Lucia into a generic AI dashboard

Avoid excessive:

* cards
* graphs
* meters
* technical labels
* telemetry panels
* VRAM indicators
* model configuration

on the main screen.

### ❌ Turn Lucia into a character manager

No:

```text
Character 1
Character 2
Character 3
```

No conventional character switching.

### ❌ Turn Philia into a game mechanic

No relationship XP or friendship percentage.

### ❌ Remove the underlying technical system

Do not delete PAD, homeostasis, memory, LNN, active inference, hardware profiling, diagnostics, etc.

**Move them behind progressive disclosure.**

### ❌ Rewrite the AI architecture merely to redesign the UI

The UI redesign should consume existing APIs/state.

Do not unnecessarily modify:

* emotion core
* memory core
* homeostasis
* inference
* voice pipeline
* avatar engine

unless an integration problem requires it.

---

# 23. Design Principle — Progressive Disclosure

This is the most important implementation principle for the agent.

```text
                 EVERYDAY USER
                       │
                       ▼
              ┌─────────────────┐
              │      Lucia      │
              │                 │
              │     Talk        │
              │    Journal      │
              │    Presence     │
              └─────────────────┘
                       │
                wants more control
                       │
                       ▼
              ┌─────────────────┐
              │    Settings     │
              └─────────────────┘
                       │
                 wants internals
                       │
                       ▼
              ┌─────────────────┐
              │   Diagnostics   │
              │ PAD / LNN / SDM │
              │ Homeostasis     │
              │ Performance     │
              └─────────────────┘
```

**Simple on the surface. Deep underneath.**

---

# 24. Visual Direction

The existing visual identity can remain recognizable:

* dark/gothic atmosphere
* black / deep purple / muted pink
* soft translucent surfaces
* subtle glow
* elegant typography
* anime/illustrated avatar
* atmospheric background

But avoid making every component look like a cyberpunk dashboard.

The aesthetic target should feel closer to:

> **a personal digital room inhabited by Lucia**

than:

> **a neural network monitoring console**

---

# 25. Technical Preservation Requirement

The current backend already provides:

```text
Stimulus
   ↓
Limbic ODE
   ↓
PAD
   ↓
Homeostasis
   ↓
Active Inference
   ↓
Affective Memory
   ↓
Prompt Assembly
   ↓
Local LLM
   ↓
Voice + Avatar
```

and the UI should be treated as the **embodied presentation layer** of this system. 

The agent should therefore prioritize:

**UI refactoring over backend refactoring.**

---

# 26. Implementation Order

Agent should implement in this order:

### Phase 1 — Information Architecture

* remove telemetry from main screen
* establish navigation
* rename concepts
* create Talk / Journal / Memories / Presence / Settings

### Phase 2 — Main Companion UI

Build:

```text
Lucia Home
     ↓
Talk
```

Make this feel polished before touching advanced screens.

### Phase 3 — Journal & Memories

Separate:

```text
Conversation History
        ≠
Lucia's Memories
        ≠
Our Journal
```

### Phase 4 — Presence / Mascot

Redesign desktop Presence toolbar and fix:

* dragging
* zoom
* scale bounds
* toolbar anchoring
* transparency
* hover behavior

### Phase 5 — Settings

Split simple and advanced settings.

### Phase 6 — Diagnostics

Move existing telemetry into a dedicated technical interface.

### Phase 7 — Genesis / Life Lifecycle

Implement:

```text
Begin Lucia
     ↓
Lucia's Life
     ↓
Journal + Memories + Growth
     ↓
End Lucia's Life
```

---

# 27. Definition of Success

The redesign is successful if a non-technical user opens Lucia and immediately understands:

> **“This is Lucia. I can talk to her, spend time with her, and she lives here with me.”**

without needing to understand:

* PAD
* LNN
* SDM
* ODE
* VRAM
* GGUF
* RVC
* FastAPI
* hardware tiers

Meanwhile, a technical user should still be able to go deeper and inspect the entire underlying system.

---

## One sentence the agent should remember

> **Lucia's complexity belongs underneath the experience; Lucia herself belongs at the center of it.**
