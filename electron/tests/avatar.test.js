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
});
