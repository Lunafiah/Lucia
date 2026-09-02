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
