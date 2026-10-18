/**
 * @jest-environment jsdom
 */
const { ExpressionMapper } = require("../renderer/avatar/expression-mapper.js");
const { LipSyncProcessor } = require("../renderer/avatar/lip-sync.js");

describe("ExpressionMapper", () => {
  test("maps warm philia PAD state to positive smile and blush", () => {
    const pad = { pleasure: 0.6, arousal: 0.1, dominance: 0.05 };
    const expr = ExpressionMapper.mapPADToExpression(pad);

    expect(expr.smile).toBeGreaterThan(0.5);
    expect(expr.frown).toBe(0);
    expect(expr.blush).toBeGreaterThan(0.5);
    expect(expr.eyeOpen).toBeGreaterThan(0.8);
  });

  test("maps negative pleasure to frown without blush", () => {
    const pad = { pleasure: -0.5, arousal: -0.2, dominance: -0.1 };
    const expr = ExpressionMapper.mapPADToExpression(pad);

    expect(expr.smile).toBe(0);
    expect(expr.frown).toBeGreaterThan(0.4);
    expect(expr.blush).toBe(0);
  });

  test("clamps values within valid physical bounds", () => {
    const pad = { pleasure: 2.0, arousal: -5.0, dominance: 3.0 };
    const expr = ExpressionMapper.mapPADToExpression(pad);

    expect(expr.eyeOpen).toBeGreaterThanOrEqual(0.3);
    expect(expr.eyeOpen).toBeLessThanOrEqual(1.2);
    expect(expr.smile).toBeLessThanOrEqual(1.0);
  });
});

describe("LipSyncProcessor", () => {
  test("initializes with closed mouth", () => {
    const processor = new LipSyncProcessor();
    expect(processor.mouthOpen).toBe(0);
    expect(processor.isPlaying).toBe(false);

    const metrics = processor.update();
    expect(metrics.open).toBe(0);
    expect(metrics.isSpeaking).toBe(false);
  });
});

describe("AvatarRenderer", () => {
  global.ExpressionMapper = ExpressionMapper;
  global.LipSyncProcessor = LipSyncProcessor;
  const { AvatarRenderer } = require("../renderer/avatar/avatar.js");

  const createMockCanvas = () => {
    const canvas = document.createElement("canvas");
    canvas.getContext = jest.fn().mockReturnValue({
      setTransform: jest.fn(),
      clearRect: jest.fn(),
      save: jest.fn(),
      restore: jest.fn(),
      translate: jest.fn(),
      rotate: jest.fn(),
      scale: jest.fn(),
      beginPath: jest.fn(),
      arc: jest.fn(),
      fill: jest.fn(),
      stroke: jest.fn(),
      moveTo: jest.fn(),
      lineTo: jest.fn(),
      quadraticCurveTo: jest.fn(),
      createRadialGradient: jest.fn().mockReturnValue({ addColorStop: jest.fn() })
    });
    return canvas;
  };

  test("initializes with default pan (0,0) and scale (1.0)", () => {
    const canvas = createMockCanvas();
    const renderer = new AvatarRenderer(canvas);

    expect(renderer.pan.x).toBe(0);
    expect(renderer.pan.y).toBe(0);
    expect(renderer.mascotScale).toBe(1.0);
    expect(renderer.activeEngine).toBe("canvas");
  });

  test("switches engine to vrm and sprites cleanly", async () => {
    const canvas = createMockCanvas();
    const renderer = new AvatarRenderer(canvas);

    await renderer.setEngine("sprites", "Columbina");
    expect(renderer.activeEngine).toBe("sprites");
    expect(renderer.activeModel).toBe("Columbina");

    await renderer.setEngine("vrm", "default");
    expect(renderer.activeEngine).toBe("vrm");
    expect(renderer.activeModel).toBe("default");
  });

  test("wheel event does not change scale while isDraggingModel is true", () => {
    const canvas = createMockCanvas();
    const stage = document.createElement("div");
    stage.className = "avatar-stage-container";
    stage.appendChild(canvas);
    document.body.appendChild(stage);

    const renderer = new AvatarRenderer(canvas);
    renderer.isDraggingModel = true;
    const initialScale = renderer.mascotScale;

    // Simulate wheel event
    const wheelEvent = new Event("wheel", { bubbles: true, cancelable: true });
    wheelEvent.deltaY = -100;
    canvas.dispatchEvent(wheelEvent);

    expect(renderer.mascotScale).toBe(initialScale);
  });

  test("pan position is clamped to safe boundary on drag", () => {
    const canvas = createMockCanvas();
    const stage = document.createElement("div");
    stage.className = "avatar-stage-container";
    stage.appendChild(canvas);
    document.body.appendChild(stage);

    const renderer = new AvatarRenderer(canvas);
    renderer.width = 400;
    renderer.height = 600;
    renderer.isDraggingModel = true;
    renderer.dragStart = { x: 0, y: 0 };

    // Move mouse far away (e.g. 5000px)
    const moveEvent = new MouseEvent("mousemove", { clientX: 5000, clientY: 5000 });
    window.dispatchEvent(moveEvent);

    const maxClampX = 400 * 0.75; // 300
    const maxClampY = 600 * 0.75; // 450
    expect(renderer.pan.x).toBeLessThanOrEqual(maxClampX);
    expect(renderer.pan.y).toBeLessThanOrEqual(maxClampY);
  });

  test("setTargetFps updates targetFps and clamps to valid range", () => {
    const canvas = createMockCanvas();
    const renderer = new AvatarRenderer(canvas);

    renderer.setTargetFps(30);
    expect(renderer.targetFps).toBe(30);

    renderer.setTargetFps(60);
    expect(renderer.targetFps).toBe(60);

    renderer.setTargetFps(5); // Clamps to minimum 15
    expect(renderer.targetFps).toBe(15);

    renderer.setTargetFps(240); // Clamps to maximum 120
    expect(renderer.targetFps).toBe(120);
  });

  test("getModelBounds returns valid bounds and centers on canvas", () => {
    const canvas = createMockCanvas();
    canvas.getBoundingClientRect = jest.fn().mockReturnValue({
      left: 0,
      top: 0,
      width: 400,
      height: 600
    });

    const renderer = new AvatarRenderer(canvas);
    renderer.width = 400;
    renderer.height = 600;

    const bounds = renderer.getModelBounds();
    expect(bounds).toHaveProperty("centerX");
    expect(bounds).toHaveProperty("bottomY");
    expect(bounds).toHaveProperty("left");
    expect(bounds).toHaveProperty("right");
    expect(bounds).toHaveProperty("top");
    expect(bounds).toHaveProperty("bottom");

    expect(bounds.centerX).toBeCloseTo(200, 0);
    expect(bounds.bottomY).toBeGreaterThan(bounds.top);
  });

  test("isCursorOverModel detects whether coordinates are inside model bounds", () => {
    const canvas = createMockCanvas();
    canvas.getBoundingClientRect = jest.fn().mockReturnValue({
      left: 0,
      top: 0,
      width: 400,
      height: 600
    });

    const renderer = new AvatarRenderer(canvas);
    renderer.width = 400;
    renderer.height = 600;

    // Center coordinates should be over the model
    expect(renderer.isCursorOverModel(200, 300)).toBe(true);

    // Far away coordinates should not be over the model
    expect(renderer.isCursorOverModel(1000, 1000)).toBe(false);
  });

  test("Live2D getModelBounds does not double-scale rendered dimensions", () => {
    const canvas = createMockCanvas();
    const renderer = new AvatarRenderer(canvas);
    renderer.live2dCanvas = canvas;
    renderer.activeEngine = "live2d";
    renderer.currentLive2DModel = {
      x: 20,
      y: 25,
      width: 340,   // Already scaled rendered dimension
      height: 480,  // Already scaled rendered dimension
      scale: { x: 0.25, y: 0.25 }
    };

    const bounds = renderer.getModelBounds();
    expect(bounds.left).toBe(20);
    expect(bounds.right).toBe(20 + 340);
    expect(bounds.top).toBe(25);
    expect(bounds.bottom).toBe(25 + 480);
    expect(bounds.bottomY).toBe(505);
    expect(bounds.centerX).toBe(20 + 170);

    // Hit testing works across the full rendered height
    canvas.getBoundingClientRect = jest.fn().mockReturnValue({ left: 0, top: 0, width: 380, height: 540 });
    expect(renderer.isCursorOverModel(190, 490)).toBe(true); // Near feet
    expect(renderer.isCursorOverModel(190, 100)).toBe(true); // Chest
    expect(renderer.isCursorOverModel(190, 530)).toBe(false); // Far below feet
  });

  test("Mascot toolbar positions below model across presets", () => {
    const canvas = createMockCanvas();
    const renderer = new AvatarRenderer(canvas);
    renderer.activeEngine = "live2d";

    // Setup mascot DOM
    document.body.classList.add("mascot-mode");
    const toolbar = document.createElement("div");
    toolbar.id = "mascot-toolbar";
    document.body.appendChild(toolbar);

    try {
      const presets = ["small", "normal", "comfort"];
      for (const presetKey of presets) {
        renderer.currentPreset = presetKey;
        const preset = { small: { width: 285, height: 405 }, normal: { width: 380, height: 540 }, comfort: { width: 475, height: 675 } }[presetKey];
        const modelH = preset.height * 0.85;
        renderer.currentLive2DModel = {
          x: 10,
          y: preset.height - modelH,
          width: preset.width - 20,
          height: modelH,
          scale: { x: 0.2, y: 0.2 }
        };

        renderer._updateToolbarPosition();
        const expectedBottom = preset.height - modelH + modelH; // preset.height
        const maxSafeY = preset.height - 52 - 6;
        const expectedSafeY = Math.max(52, Math.min(maxSafeY, expectedBottom + 8));
        expect(toolbar.style.top).toBe(`${expectedSafeY}px`);
        expect(parseFloat(toolbar.style.top)).toBeGreaterThan(preset.height * 0.7);
      }
    } finally {
      document.body.classList.remove("mascot-mode");
      toolbar.remove();
    }
  });
});

