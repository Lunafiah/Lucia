# Avatar Models Directory

Place your custom character avatar models in this directory. Lucia supports three custom model types via the `AvatarRegistry`:

## 1. 2D Sprite Avatars (`models/avatar/sprites/<character_name>/`)
Place expression PNG images in a subfolder:
```
models/avatar/sprites/my_character/
├── idle.png       (Default resting expression)
├── smile.png      (High pleasure / warmth)
├── blush.png      (High pleasure & high arousal)
├── speaking.png   (Open mouth / talking)
└── thinking.png   (High cognitive load / reflection)
```

## 2. Live2D Models (`models/avatar/live2d/<character_name>/`)
Place your exported Live2D Cubism model folder:
```
models/avatar/live2d/my_character/
├── my_character.model3.json
├── my_character.moc3
├── textures/
└── motions/
```

## 3. 3D VRM Avatars (`models/avatar/vrm/`)
Place your 3D humanoid `.vrm` files:
```
models/avatar/vrm/
└── my_character.vrm
```

---
*Note: If no custom model is placed, Lucia automatically renders her built-in 60 FPS interactive Canvas Rig.*
