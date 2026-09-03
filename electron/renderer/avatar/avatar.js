/**
 * AvatarRenderer — 60 FPS Interactive Canvas Avatar for Lucia.
 * Connects live PAD emotion telemetry, Web Audio lip-syncing, natural blinking,
 * breathing cycles, and cursor gaze following.
 */

class AvatarRenderer {
  constructor(canvasElement) {
    this.canvas = canvasElement;
    this.ctx = canvasElement ? canvasElement.getContext("2d") : null;
    this.lipSync = new LipSyncProcessor();

    // Emotion & physics state
    this.currentExpression = ExpressionMapper.mapPADToExpression({
      pleasure: 0.25,
      arousal: -0.05,
      dominance: 0.05,
    });
    this.targetExpression = { ...this.currentExpression };

    // Mouse gaze tracking
    this.mouse = { x: 0, y: 0, targetX: 0, targetY: 0 };

    // Blinking animation
    this.blinkProgress = 0; // 0 = open, 1 = closed
    this.isBlinking = false;
    this.nextBlinkTime = performance.now() + 3000;

    // Animation loop
    this.animationFrameId = null;
    this.startTime = performance.now();

    this._bindEvents();
    if (this.canvas) {
      this.resize();
      this.start();
    }
  }

  _bindEvents() {
    window.addEventListener("mousemove", (e) => {
      if (!this.canvas) return;
      const rect = this.canvas.getBoundingClientRect();
      const centerX = rect.left + rect.width / 2;
      const centerY = rect.top + rect.height / 2;

      // Normalized gaze in [-1, 1]
      this.mouse.targetX = Math.max(-1, Math.min(1, (e.clientX - centerX) / (rect.width / 2)));
      this.mouse.targetY = Math.max(-1, Math.min(1, (e.clientY - centerY) / (rect.height / 2)));
    });

    window.addEventListener("resize", () => this.resize());
  }

  resize() {
    if (!this.canvas) return;
    const rect = this.canvas.parentElement.getBoundingClientRect();
    const dpr = window.devicePixelRatio || 1;
    this.canvas.width = rect.width * dpr;
    this.canvas.height = rect.height * dpr;
    this.ctx.scale(dpr, dpr);
    this.width = rect.width;
    this.height = rect.height;
  }

  /**
   * Update live PAD emotion state from telemetry polling.
   */
  updateEmotion(pad) {
    this.targetExpression = ExpressionMapper.mapPADToExpression(pad);
  }

  /**
   * Speak response text via synthesized voice audio.
   */
  async speak(audioBlob, onComplete = null) {
    await this.lipSync.playAudio(audioBlob, onComplete);
  }

  start() {
    const loop = (now) => {
      this._updatePhysics(now);
      this._render(now);
      this.animationFrameId = requestAnimationFrame(loop);
    };
    this.animationFrameId = requestAnimationFrame(loop);
  }

  stop() {
    if (this.animationFrameId) {
      cancelAnimationFrame(this.animationFrameId);
      this.animationFrameId = null;
    }
    this.lipSync.stop();
  }

  _updatePhysics(now) {
    // Smoothly interpolate expression parameters
    const exp = this.currentExpression;
    const target = this.targetExpression;
    const speed = 0.08;

    exp.smile += (target.smile - exp.smile) * speed;
    exp.frown += (target.frown - exp.frown) * speed;
    exp.eyeOpen += (target.eyeOpen - exp.eyeOpen) * speed;
    exp.browAngle += (target.browAngle - exp.browAngle) * speed;
    exp.blush += (target.blush - exp.blush) * speed;
    exp.headTilt += (target.headTilt - exp.headTilt) * speed;
    exp.glowColor = target.glowColor;

    // Smooth mouse gaze
    this.mouse.x += (this.mouse.targetX - this.mouse.x) * 0.05;
    this.mouse.y += (this.mouse.targetY - this.mouse.y) * 0.05;

    // Blink cycle
    if (now >= this.nextBlinkTime && !this.isBlinking) {
      this.isBlinking = true;
      this.blinkProgress = 0;
    }

    if (this.isBlinking) {
      this.blinkProgress += 0.12;
      if (this.blinkProgress >= 1.0) {
        this.blinkProgress = 0;
        this.isBlinking = false;
        this.nextBlinkTime = now + 2500 + Math.random() * 3500;
      }
    }
  }

  _render(now) {
    if (!this.ctx || !this.width) return;
    const ctx = this.ctx;
    const w = this.width;
    const h = this.height;

    ctx.clearRect(0, 0, w, h);

    const time = (now - this.startTime) / 1000;
    const breath = Math.sin((time * Math.PI * 2) / this.currentExpression.breathingPeriod) * 4;
    const lipMetrics = this.lipSync.update();

    const centerX = w / 2 + this.mouse.x * 6;
    const centerY = h / 2 - 10 + breath + this.mouse.y * 4;
    const headRadius = Math.min(w, h) * 0.32;

    ctx.save();
    ctx.translate(centerX, centerY);
    ctx.rotate((this.currentExpression.headTilt * Math.PI) / 180);

    // 1. Ambient Background Halo
    const halo = ctx.createRadialGradient(0, 0, headRadius * 0.4, 0, 0, headRadius * 1.5);
    halo.addColorStop(0, this.currentExpression.glowColor);
    halo.addColorStop(1, "rgba(0, 0, 0, 0)");
    ctx.fillStyle = halo;
    ctx.beginPath();
    ctx.arc(0, 0, headRadius * 1.5, 0, Math.PI * 2);
    ctx.fill();

    // 2. Neck & Shoulders
    ctx.fillStyle = "#1e1b4b";
    ctx.beginPath();
    ctx.moveTo(-headRadius * 0.4, headRadius * 0.8);
    ctx.lineTo(-headRadius * 0.8, headRadius * 1.6);
    ctx.lineTo(headRadius * 0.8, headRadius * 1.6);
    ctx.lineTo(headRadius * 0.4, headRadius * 0.8);
    ctx.closePath();
    ctx.fill();

    // 3. Face Base
    const faceGrad = ctx.createLinearGradient(0, -headRadius, 0, headRadius);
    faceGrad.addColorStop(0, "#fef3c7");
    faceGrad.addColorStop(1, "#fde68a");
    ctx.fillStyle = faceGrad;
    ctx.beginPath();
    ctx.ellipse(0, 0, headRadius * 0.9, headRadius, 0, 0, Math.PI * 2);
    ctx.fill();
    ctx.strokeStyle = "rgba(245, 158, 11, 0.3)";
    ctx.lineWidth = 2;
    ctx.stroke();

    // 4. Soft Blush
    if (this.currentExpression.blush > 0.05) {
      ctx.fillStyle = `rgba(244, 63, 94, ${this.currentExpression.blush * 0.4})`;
      ctx.beginPath();
      ctx.ellipse(-headRadius * 0.45, headRadius * 0.2, headRadius * 0.18, headRadius * 0.09, 0, 0, Math.PI * 2);
      ctx.ellipse(headRadius * 0.45, headRadius * 0.2, headRadius * 0.18, headRadius * 0.09, 0, 0, Math.PI * 2);
      ctx.fill();
    }

    // 5. Eyes & Gaze
    const eyeSpacing = headRadius * 0.38;
    const eyeY = -headRadius * 0.05;
    const eyeWidth = headRadius * 0.22;
    const eyeHeight = headRadius * 0.28 * this.currentExpression.eyeOpen;
    const blinkMul = this.isBlinking ? Math.max(0.05, 1.0 - Math.sin(this.blinkProgress * Math.PI)) : 1.0;

    [-1, 1].forEach((side) => {
      const eyeX = side * eyeSpacing;
      ctx.save();
      ctx.translate(eyeX, eyeY);

      // Sclera (Eye White)
      ctx.fillStyle = "#ffffff";
      ctx.beginPath();
      ctx.ellipse(0, 0, eyeWidth, eyeHeight * blinkMul, 0, 0, Math.PI * 2);
      ctx.fill();
      ctx.strokeStyle = "#475569";
      ctx.lineWidth = 1.5;
      ctx.stroke();

      if (blinkMul > 0.2) {
        // Iris
        const irisX = this.mouse.x * 4;
        const irisY = this.mouse.y * 3;
        const irisGrad = ctx.createRadialGradient(irisX, irisY, 2, irisX, irisY, eyeWidth * 0.8);
        irisGrad.addColorStop(0, "#c084fc");
        irisGrad.addColorStop(0.7, "#7c3aed");
        irisGrad.addColorStop(1, "#4c1d95");

        ctx.fillStyle = irisGrad;
        ctx.beginPath();
        ctx.arc(irisX, irisY, eyeWidth * 0.65 * blinkMul, 0, Math.PI * 2);
        ctx.fill();

        // Pupil
        ctx.fillStyle = "#1e1b4b";
        ctx.beginPath();
        ctx.arc(irisX, irisY, eyeWidth * 0.3 * blinkMul, 0, Math.PI * 2);
        ctx.fill();

        // Specular highlight
        ctx.fillStyle = "#ffffff";
        ctx.beginPath();
        ctx.arc(irisX - eyeWidth * 0.2, irisY - eyeHeight * 0.2 * blinkMul, eyeWidth * 0.18, 0, Math.PI * 2);
        ctx.fill();
      }

      // Eyelash Line
      ctx.strokeStyle = "#334155";
      ctx.lineWidth = 3;
      ctx.beginPath();
      ctx.arc(0, -eyeHeight * 0.5 * blinkMul, eyeWidth * 1.1, Math.PI * 0.85, Math.PI * 2.15);
      ctx.stroke();

      ctx.restore();
    });

    // 6. Eyebrows
    [-1, 1].forEach((side) => {
      const browX = side * eyeSpacing;
      const browY = eyeY - headRadius * 0.35 + side * this.currentExpression.browAngle * 8;
      ctx.strokeStyle = "#64748b";
      ctx.lineWidth = 3;
      ctx.beginPath();
      ctx.moveTo(browX - headRadius * 0.15, browY + 3);
      ctx.quadraticCurveTo(browX, browY - 4, browX + headRadius * 0.15, browY + (side === -1 ? 2 : 2));
      ctx.stroke();
    });

    // 7. Dynamic Mouth & Lip-Sync
    const mouthY = headRadius * 0.45;
    const mouthOpen = Math.max(lipMetrics.open, this.currentExpression.smile * 0.15);
    const mouthWidth = headRadius * 0.28 * lipMetrics.width;

    ctx.fillStyle = "#dc2626";
    ctx.strokeStyle = "#7f1d1d";
    ctx.lineWidth = 2;

    if (mouthOpen > 0.08) {
      // Speaking / Open Mouth
      ctx.beginPath();
      ctx.ellipse(0, mouthY, mouthWidth, headRadius * 0.22 * mouthOpen, 0, 0, Math.PI * 2);
      ctx.fill();
      ctx.stroke();

      // Teeth
      ctx.fillStyle = "#ffffff";
      ctx.beginPath();
      ctx.ellipse(0, mouthY - headRadius * 0.06 * mouthOpen, mouthWidth * 0.7, headRadius * 0.05 * mouthOpen, 0, 0, Math.PI);
      ctx.fill();
    } else {
      // Resting / Closed Mouth with Smile / Frown Curve
      const smileOffset = (this.currentExpression.smile - this.currentExpression.frown) * 8;
      ctx.beginPath();
      ctx.moveTo(-mouthWidth * 0.8, mouthY - smileOffset * 0.3);
      ctx.quadraticCurveTo(0, mouthY + smileOffset, mouthWidth * 0.8, mouthY - smileOffset * 0.3);
      ctx.stroke();
    }

    ctx.restore();
  }

  setVolume(vol) {
    if (this.lipSync) {
      this.lipSync.setVolume(vol);
    }
  }

  setEngine(engine, model = "default") {
    this.activeEngine = engine || "canvas";
    this.activeModel = model || "default";
    console.log(`[avatar] Switched engine to: ${this.activeEngine}, model: ${this.activeModel}`);
  }

  destroy() {
    this.stop();
    if (this.lipSync && this.lipSync.currentAudio) {
      this.lipSync.currentAudio.pause();
    }
  }
}

if (typeof window !== "undefined" && window.avatarRegistry) {
  window.avatarRegistry.register("canvas", AvatarRenderer);
}

if (typeof module !== "undefined" && module.exports) {
  module.exports = { AvatarRenderer };
}
