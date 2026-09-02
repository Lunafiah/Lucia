# Lucia Avatar & VTuber Model Directory

Place your 2D / 3D visual avatar assets here to give Lucia an embodied visual form.

---

## Supported Avatar Formats & Directory Layout

```
assets/avatar/
├── live2d/                 # Live2D Cubism Models (2D)
│   ├── lucia.model3.json
│   ├── lucia.moc3
│   ├── textures/
│   ├── motions/
│   └── physics3.json
│
├── vrm/                    # 3D VRoid / VRM Models
│   └── lucia.vrm
│
└── sprites/                # 2D Sprite Sheets / PNGtuber States
    ├── idle.png
    ├── speaking.png
    ├── pleased.png         (High Pleasure state)
    ├── thoughtful.png      (High Cognitive Load / Thinking)
    └── calm.png            (Philia Resting Baseline)
```

---

## How Lucia Drives Her Avatar

Lucia's internal cognitive-emotional engines dynamically drive her avatar expressions in real time:

1. **Emotional Expressions (PAD Attractor)**:
   - **Pleasure ($P > 0.3$)**: Gentle warm smile, softened eye blendshapes.
   - **Arousal ($A > 0.4$)**: Alert posture, widened gaze.
   - **Tension ($T > 0.5$)**: Subtly furrowed brows, contemplative tilt.
2. **Speech Lip-Sync (Visemes)**:
   - Synchronized mouth opening (`A, I, U, E, O` visemes) driven by audio output.
3. **Autonomic Micro-Movements**:
   - Natural periodic eye blinking, breathing oscillation, and subtle head sways.
