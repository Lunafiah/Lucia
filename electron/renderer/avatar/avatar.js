/**
 * AvatarRenderer — 60 FPS Interactive Canvas Avatar for Lucia.
 * Connects live PAD emotion telemetry, Web Audio lip-syncing, natural blinking,
 * breathing cycles, and cursor gaze following.
 */

class AvatarRenderer {
  constructor(canvasElement) {
    this.canvas = canvasElement;
    this.ctx = canvasElement ? canvasElement.getContext("2d") : null;
    this.live2dCanvas = typeof document !== "undefined" ? document.getElementById("avatar-live2d-canvas") : null;
    this.lipSync = new LipSyncProcessor();
    this.pixiApp = null;
    this.currentLive2DModel = null;

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
    if (this.canvas && this.canvas.parentElement) {
      const rect = this.canvas.parentElement.getBoundingClientRect();
      const dpr = window.devicePixelRatio || 1;
      this.canvas.width = rect.width * dpr;
      this.canvas.height = rect.height * dpr;
      if (this.ctx) this.ctx.scale(dpr, dpr);
      this.width = rect.width;
      this.height = rect.height;
    }

    if (this.pixiApp && this.live2dCanvas && this.live2dCanvas.parentElement) {
      const pRect = this.live2dCanvas.parentElement.getBoundingClientRect();
      this.pixiApp.renderer.resize(pRect.width, pRect.height);

      if (this.currentLive2DModel) {
        const stageW = pRect.width || 300;
        const stageH = pRect.height || 250;
        const naturalW = this.currentLive2DModel.internalModel ? this.currentLive2DModel.internalModel.width : this.currentLive2DModel.width;
        const naturalH = this.currentLive2DModel.internalModel ? this.currentLive2DModel.internalModel.height : this.currentLive2DModel.height;
        const scale = Math.min((stageW * 0.92) / (naturalW || 2000), (stageH * 0.92) / (naturalH || 2000));
        this.currentLive2DModel.scale.set(scale);
        this.currentLive2DModel.x = (stageW - (naturalW || 2000) * scale) / 2;
        this.currentLive2DModel.y = stageH - (naturalH || 2000) * scale;
      }
    }
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

    // Live2D continuous parameter update (gaze & lipsync)
    if (this.currentLive2DModel && this.currentLive2DModel.internalModel) {
      try {
        if (typeof this.currentLive2DModel.focus === 'function') {
          this.currentLive2DModel.focus(this.mouse.x, -this.mouse.y);
        }

        const core = this.currentLive2DModel.internalModel.coreModel;
        if (core && typeof core.setParameterValueById === 'function') {
          const mouthOpen = this.lipSync ? this.lipSync.getMouthOpen() : 0;
          if (mouthOpen > 0.04) {
            core.setParameterValueById('ParamMouthOpenY', Math.min(1.0, mouthOpen * 2.0));
          }
        }
      } catch (e) {
        // ignore tick errors
      }
    }
  }

  _render(now) {
    if (!this.ctx || !this.width) return;
    const ctx = this.ctx;
    const w = this.width;
    const h = this.height;

    ctx.clearRect(0, 0, w, h);

    if (this.activeEngine === 'sprites' && this._hasLoadedSprites()) {
      this._renderSprite(now);
    } else if (this.activeEngine === 'live2d') {
      this._renderLive2D(now);
    } else {
      this._renderProcedural(now);
    }
  }

  _renderLive2D(now) {
    const ctx = this.ctx;
    const w = this.width;
    const h = this.height;
    const time = (now - this.startTime) / 1000;
    const pulse = 0.5 + 0.5 * Math.sin(time * 2.5);

    // Glowing stage background
    const bgGrad = ctx.createRadialGradient(w / 2, h / 2, 20, w / 2, h / 2, w * 0.6);
    bgGrad.addColorStop(0, "rgba(236, 72, 153, 0.25)"); // Hoshino Ai Magenta glow
    bgGrad.addColorStop(1, "rgba(0, 0, 0, 0)");
    ctx.fillStyle = bgGrad;
    ctx.beginPath();
    ctx.arc(w / 2, h / 2, w * 0.6, 0, Math.PI * 2);
    ctx.fill();

    // Live2D Holographic Card Box
    const cardW = Math.min(w * 0.88, 260);
    const cardH = 135;
    const cardX = (w - cardW) / 2;
    const cardY = (h - cardH) / 2;

    ctx.save();
    ctx.fillStyle = "rgba(15, 23, 42, 0.85)";
    ctx.strokeStyle = `rgba(236, 72, 153, ${0.4 + pulse * 0.4})`;
    ctx.lineWidth = 1.5;
    ctx.beginPath();
    ctx.roundRect(cardX, cardY, cardW, cardH, 12);
    ctx.fill();
    ctx.stroke();

    // Header badge
    ctx.fillStyle = "#ec4899";
    ctx.font = "bold 13px system-ui, sans-serif";
    ctx.textAlign = "center";
    ctx.fillText("🎬 Live2D Cubism 4 Detected", w / 2, cardY + 28);

    // Model name
    ctx.fillStyle = "#f8fafc";
    ctx.font = "bold 15px system-ui, sans-serif";
    ctx.fillText(this.activeModel || "HoshinoAi", w / 2, cardY + 54);

    // Subtitle / file info
    ctx.fillStyle = "#94a3b8";
    ctx.font = "11px system-ui, sans-serif";
    ctx.fillText("Hoshino_Ai.moc3 & 8192 Texture", w / 2, cardY + 76);

    // Status
    ctx.fillStyle = "#38bdf8";
    ctx.font = "italic 11px system-ui, sans-serif";
    ctx.fillText("⚡ WebGL Cubism Runtime Loading...", w / 2, cardY + 102);

    ctx.restore();
  }

  _hasLoadedSprites() {
    return !!(this.sprites && this.sprites.idle && this.sprites.idle.complete && this.sprites.idle.naturalWidth > 0);
  }

  _renderSprite(now) {
    const ctx = this.ctx;
    const w = this.width;
    const h = this.height;
    const time = (now - this.startTime) / 1000;
    const breath = Math.sin((time * Math.PI * 2) / (this.currentExpression.breathingPeriod || 3.5)) * 3;
    const lipMetrics = this.lipSync.update();

    let activeSprite = this.sprites.idle;
    if (lipMetrics.mouthOpen > 0.12 && this.sprites.speaking && this.sprites.speaking.complete) {
      activeSprite = this.sprites.speaking;
    } else if (this.currentExpression.blush > 0.35 && this.sprites.blush && this.sprites.blush.complete) {
      activeSprite = this.sprites.blush;
    } else if (this.currentExpression.smile > 0.35 && this.sprites.smile && this.sprites.smile.complete) {
      activeSprite = this.sprites.smile;
    } else if (this.currentExpression.frown > 0.35 && this.sprites.sad && this.sprites.sad.complete) {
      activeSprite = this.sprites.sad;
    } else if (this.currentExpression.browAngle < -0.3 && this.sprites.angry && this.sprites.angry.complete) {
      activeSprite = this.sprites.angry;
    } else if (this.currentExpression.eyeOpen < 0.6 && this.sprites.relaxed && this.sprites.relaxed.complete) {
      activeSprite = this.sprites.relaxed;
    }

    if (!activeSprite || !activeSprite.complete || activeSprite.naturalWidth === 0) {
      activeSprite = this.sprites.idle;
    }

    // 1. Ambient Background Halo
    const halo = ctx.createRadialGradient(w / 2, h / 2, w * 0.15, w / 2, h / 2, w * 0.6);
    halo.addColorStop(0, this.currentExpression.glowColor || "rgba(168, 85, 247, 0.25)");
    halo.addColorStop(1, "rgba(0, 0, 0, 0)");
    ctx.fillStyle = halo;
    ctx.beginPath();
    ctx.arc(w / 2, h / 2, w * 0.6, 0, Math.PI * 2);
    ctx.fill();

    // 2. Scale & Center Sprite
    const naturalW = activeSprite.naturalWidth;
    const naturalH = activeSprite.naturalHeight;
    const scale = Math.min((w * 0.92) / naturalW, (h * 0.92) / naturalH);
    const drawW = naturalW * scale;
    const drawH = naturalH * scale;

    const drawX = (w - drawW) / 2 + this.mouse.x * 6;
    const drawY = h - drawH + breath + this.mouse.y * 4;

    ctx.save();
    ctx.drawImage(activeSprite, drawX, drawY, drawW, drawH);
    ctx.restore();
  }

  _renderProcedural(now) {
    const ctx = this.ctx;
    const w = this.width;
    const h = this.height;

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

  async setEngine(engine, model = "default") {
    this.activeEngine = engine || "canvas";
    this.activeModel = model || "default";
    console.log(`[avatar] Switched engine to: ${this.activeEngine}, model: ${this.activeModel}`);

    if (this.activeEngine === 'live2d') {
      if (this.canvas) this.canvas.style.display = 'none';
      if (this.live2dCanvas) this.live2dCanvas.style.display = 'block';
      await this._loadLive2DModel(this.activeModel);
    } else {
      if (this.live2dCanvas) this.live2dCanvas.style.display = 'none';
      if (this.canvas) this.canvas.style.display = 'block';

      if (this.activeEngine === 'sprites') {
        this._loadSpriteSet(this.activeModel);
      } else {
        this.sprites = null;
      }
    }
  }

  async _loadLive2DModel(modelName) {
    if (!modelName || modelName === 'default') {
      if (this.currentLive2DModel && this.pixiApp) {
        this.pixiApp.stage.removeChild(this.currentLive2DModel);
        this.currentLive2DModel.destroy();
        this.currentLive2DModel = null;
      }
      return;
    }

    if (typeof PIXI === 'undefined' || !PIXI.live2d || !PIXI.live2d.Live2DModel) {
      console.warn('[live2d] Pixi.js or Live2D Cubism runtime not loaded yet');
      return;
    }

    if (!this.live2dCanvas && typeof document !== 'undefined') {
      this.live2dCanvas = document.getElementById("avatar-live2d-canvas");
    }

    if (!this.pixiApp && this.live2dCanvas && this.live2dCanvas.parentElement) {
      const parent = this.live2dCanvas.parentElement;
      const initialW = parent ? parent.clientWidth : 300;
      const initialH = parent ? parent.clientHeight : 250;

      this.pixiApp = new PIXI.Application({
        view: this.live2dCanvas,
        autoDensity: true,
        antialias: true,
        backgroundAlpha: 0,
        width: initialW,
        height: initialH,
      });
    }

    let modelPath = `../../models/avatar/live2d/${modelName}/${modelName}.model3.json`;
    if (modelName === 'HoshinoAi') {
      modelPath = `../../models/avatar/live2d/HoshinoAi/Hoshino_Ai.model3.json`;
    }

    try {
      console.log(`[live2d] Loading Cubism 4 model from: ${modelPath}`);
      if (this.currentLive2DModel && this.pixiApp) {
        this.pixiApp.stage.removeChild(this.currentLive2DModel);
        this.currentLive2DModel.destroy();
        this.currentLive2DModel = null;
      }

      const model = await PIXI.live2d.Live2DModel.from(modelPath, { autoInteract: true });
      this.currentLive2DModel = model;

      const parent = this.live2dCanvas.parentElement;
      const stageW = parent ? parent.clientWidth : 300;
      const stageH = parent ? parent.clientHeight : 250;

      const naturalW = model.internalModel ? model.internalModel.width : model.width;
      const naturalH = model.internalModel ? model.internalModel.height : model.height;
      const scale = Math.min((stageW * 0.92) / (naturalW || 2000), (stageH * 0.92) / (naturalH || 2000));

      model.scale.set(scale);
      model.x = (stageW - (naturalW || 2000) * scale) / 2;
      model.y = stageH - (naturalH || 2000) * scale;

      this.pixiApp.stage.addChild(model);
      console.log(`[live2d] Model ${modelName} successfully loaded into Pixi stage!`);
    } catch (err) {
      console.error(`[live2d] Failed to load model ${modelName}:`, err);
    }
  }

  _loadSpriteSet(model) {
    if (!model || model === 'default') {
      this.sprites = null;
      return;
    }
    this.sprites = {};
    const emotionKeys = [
      'idle', 'speaking', 'smile', 'blush', 'excited',
      'relaxed', 'thinking', 'concerned', 'sad', 'angry'
    ];
    emotionKeys.forEach((key) => {
      const img = new Image();
      // Relative path from index.html (electron/renderer/) to models/avatar/sprites/<model>/<key>.png
      img.src = `../../models/avatar/sprites/${model}/${key}.png`;
      this.sprites[key] = img;
    });
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
