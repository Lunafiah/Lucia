/**
 * ExpressionMapper — Translates 500ms PAD emotional telemetry into facial parameters.
 */

class ExpressionMapper {
  /**
   * Map PAD state to expressive face blend parameters.
   * @param {{pleasure: number, arousal: number, dominance: number}} pad
   * @returns {Object} Target blend parameters
   */
  static mapPADToExpression(pad) {
    const p = Math.max(-1, Math.min(1, pad?.pleasure ?? 0.25));
    const a = Math.max(-1, Math.min(1, pad?.arousal ?? -0.05));
    const d = Math.max(-1, Math.min(1, pad?.dominance ?? 0.05));

    // Smile: positive pleasure
    const smile = Math.max(0, p);
    // Frown / pouting: negative pleasure
    const frown = Math.max(0, -p);

    // Eye openness: higher arousal = more alert/wide eyes; low arousal = calm eyelids
    const eyeOpen = 0.8 + a * 0.25;

    // Eyebrow angle: positive pleasure = relaxed arched brows; low = concerned
    const browAngle = p * 0.3 - frown * 0.2;

    // Blush opacity: activates on warm, affectionate Philia state (p > 0.2)
    const blush = p > 0.15 ? Math.min(1.0, (p - 0.15) * 1.5) : 0.0;

    // Head tilt: dominance affects confident vs shy tilt
    const headTilt = -d * 6.0;

    // Breathing period: higher arousal = faster breathing (2.5s), low = slow calm (5s)
    const breathingPeriod = 4.0 - a * 1.5;

    // Mood color glow
    let glowColor = "rgba(168, 85, 247, 0.4)"; // Philia purple
    if (p > 0.4) {
      glowColor = "rgba(236, 72, 153, 0.5)"; // Warm pink
    } else if (p < -0.2) {
      glowColor = "rgba(59, 130, 246, 0.4)"; // Melancholic blue
    } else if (a > 0.3) {
      glowColor = "rgba(245, 158, 11, 0.5)"; // Energetic amber
    }

    return {
      smile,
      frown,
      eyeOpen: Math.max(0.3, Math.min(1.2, eyeOpen)),
      browAngle,
      blush,
      headTilt,
      breathingPeriod,
      glowColor,
    };
  }
}

if (typeof module !== "undefined" && module.exports) {
  module.exports = { ExpressionMapper };
}
