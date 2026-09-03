/**
 * AvatarRenderer — 60 FPS Interactive Canvas Avatar for Lucia.
 * Connects live PAD emotion telemetry, Web Audio lip-syncing, natural blinking,
 * breathing cycles, and cursor gaze following.
 * Supports 2D Canvas procedural face, 2D Sprites (Columbina), and Live2D Cubism 4 (Hoshino Ai).
 */

class AvatarRenderer {
  constructor(canvasElement) {
    this.canvas = canvasElement;
    this.ctx = canvasElement ? canvasElement.getContext("2d") : null;
    this.live2dCanvas = typeof document !== "undefined" ? document.getElementById("avatar-live2d-canvas") : null;
    this.lipSync = new LipSyncProcessor();
    this.pixiApp = null;
    this.currentLive2DModel = null;
    this.baseModelsPath = null;
    this.mascotScale = 1.0;
    // Zoom pivot in normalized [0..1] coords relative to canvas size
    this.zoomOrigin = { nx: 0.5, ny: 0.4 }; // default: center-upper (near face)
    this.activeEngine = "canvas";
    this.activeModel = "default";
    this.sprites = null;

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
      setTimeout(() => this.resize(), 50);
      this.start();
    }
    // Mascot toolbar wired up after DOM is ready
    if (typeof document !== "undefined") {
      document.addEventListener("DOMContentLoaded", () => this._setupMascotToolbar(), { once: true });
      // Also try immediately in case DOM already loaded
      if (document.readyState !== "loading") this._setupMascotToolbar();
    }
  }

  _bindEvents() {
    window.addEventListener("mousemove", (e) => {
      const activeEl = this.activeEngine === "live2d" ? this.live2dCanvas : this.canvas;
      if (!activeEl) return;
      const rect = activeEl.getBoundingClientRect();
      const centerX = rect.left + rect.width / 2;
      const centerY = rect.top + rect.height / 2;

      // Normalized gaze in [-1, 1]
      this.mouse.targetX = Math.max(-1, Math.min(1, (e.clientX - centerX) / (rect.width / 2 || 1)));
      this.mouse.targetY = Math.max(-1, Math.min(1, (e.clientY - centerY) / (rect.height / 2 || 1)));
    });

    window.addEventListener("resize", () => this.resize());

    // Cursor-anchored Zoom — zoom pivots around where the mouse pointer is
    const wrapper = (this.canvas && this.canvas.parentElement) || (this.live2dCanvas && this.live2dCanvas.parentElement);
    if (wrapper) {
      wrapper.addEventListener(
        "wheel",
        (e) => {
          e.preventDefault();

          // Record zoom pivot from current mouse position inside the wrapper
          const rect = wrapper.getBoundingClientRect();
          const relX = (e.clientX - rect.left) / (rect.width || 1);
          const relY = (e.clientY - rect.top) / (rect.height || 1);
          this.zoomOrigin = {
            nx: Math.max(0, Math.min(1, relX)),
            ny: Math.max(0, Math.min(1, relY)),
          };

          const delta = e.deltaY < 0 ? 0.08 : -0.08;
          this.mascotScale = Math.max(0.25, Math.min(4.0, (this.mascotScale || 1.0) + delta));

          // For Live2D: reposition immediately
          if (this.activeEngine === "live2d") {
            this._repositionLive2DModel();
          }
          // 2D canvas: handled per-frame in _render
        },
        { passive: false }
      );
    }
  }

  resize() {
    const wrapper = (this.canvas && this.canvas.parentElement) || (this.live2dCanvas && this.live2dCanvas.parentElement);
    if (!wrapper) return;

    const rect = wrapper.getBoundingClientRect();
    if (rect.width <= 0 || rect.height <= 0) return;

    const dpr = window.devicePixelRatio || 1;
    this.width = rect.width;
    this.height = rect.height;

    if (this.canvas) {
      this.canvas.width = Math.floor(rect.width * dpr);
      this.canvas.height = Math.floor(rect.height * dpr);
    }

    if (this.pixiApp && this.live2dCanvas) {
      this.pixiApp.renderer.resize(rect.width, rect.height);
      this._repositionLive2DModel();
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
    this.mouse.x += (this.mouse.targetX - this.mouse.x) * 0.06;
    this.mouse.y += (this.mouse.targetY - this.mouse.y) * 0.06;

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
        if (typeof this.currentLive2DModel.focus === "function") {
          this.currentLive2DModel.focus(this.mouse.x, -this.mouse.y);
        }

        const core = this.currentLive2DModel.internalModel.coreModel;
        if (core && typeof core.setParameterValueById === "function") {
          const mouthOpen = this.lipSync ? this.lipSync.getMouthOpen() : 0;
          if (mouthOpen > 0.04) {
            core.setParameterValueById("ParamMouthOpenY", Math.min(1.0, mouthOpen * 2.0));
          }
        }
      } catch (e) {
        // ignore tick errors
      }
    }
  }

  _render(now) {
    if (!this.ctx) return;
    if (!this.width || !this.height) {
      this.resize();
      if (!this.width || !this.height) return;
    }
    const ctx = this.ctx;
    const w = this.width;
    const h = this.height;
    const dpr = window.devicePixelRatio || 1;

    // Reset canvas transform every frame to prevent accumulation or drift
    ctx.setTransform(dpr, 0, 0, dpr, 0, 0);
    ctx.clearRect(0, 0, w, h);

    if (this.activeEngine === "sprites") {
      if (this._hasLoadedSprites()) {
        this._renderSprite(now);
      } else {
        this._renderLoadingSprite(now);
      }
    } else if (this.activeEngine === "live2d") {
      // Live2D is rendered via PIXI WebGL on #avatar-live2d-canvas
    } else {
      this._renderProcedural(now);
    }
  }

  _renderLoadingSprite(now) {
    const ctx = this.ctx;
    const w = this.width;
    const h = this.height;
    const time = (now - this.startTime) / 1000;
    const pulse = 0.5 + 0.5 * Math.sin(time * 3);

    ctx.save();
    ctx.fillStyle = `rgba(148, 163, 184, ${0.4 + pulse * 0.4})`;
    ctx.font = "bold 14px system-ui, sans-serif";
    ctx.textAlign = "center";
    ctx.fillText(`🖼️ Loading ${this.activeModel || "Sprite"}...`, w / 2, h / 2);
    ctx.restore();
  }

  _hasLoadedSprites() {
    return !!(
      this.sprites &&
      this.sprites.idle &&
      (this.sprites.idle.complete || this.sprites.idle._isLoaded) &&
      this.sprites.idle.naturalWidth > 0
    );
  }

  _renderSprite(now) {
    const ctx = this.ctx;
    const w = this.width;
    const h = this.height;
    const time = (now - this.startTime) / 1000;
    const breath = Math.sin((time * Math.PI * 2) / (this.currentExpression.breathingPeriod || 3.5)) * 4;
    const lipMetrics = this.lipSync.update();

    let activeSprite = this.sprites.idle;
    if (lipMetrics.mouthOpen > 0.12 && this.sprites.speaking && (this.sprites.speaking.complete || this.sprites.speaking._isLoaded)) {
      activeSprite = this.sprites.speaking;
    } else if (this.currentExpression.blush > 0.35 && this.sprites.blush && (this.sprites.blush.complete || this.sprites.blush._isLoaded)) {
      activeSprite = this.sprites.blush;
    } else if (this.currentExpression.smile > 0.35 && this.sprites.smile && (this.sprites.smile.complete || this.sprites.smile._isLoaded)) {
      activeSprite = this.sprites.smile;
    } else if (this.currentExpression.frown > 0.35 && this.sprites.sad && (this.sprites.sad.complete || this.sprites.sad._isLoaded)) {
      activeSprite = this.sprites.sad;
    } else if (this.currentExpression.browAngle < -0.3 && this.sprites.angry && (this.sprites.angry.complete || this.sprites.angry._isLoaded)) {
      activeSprite = this.sprites.angry;
    } else if (this.currentExpression.eyeOpen < 0.6 && this.sprites.relaxed && (this.sprites.relaxed.complete || this.sprites.relaxed._isLoaded)) {
      activeSprite = this.sprites.relaxed;
    }

    if (!activeSprite || (!activeSprite.complete && !activeSprite._isLoaded) || activeSprite.naturalWidth === 0) {
      activeSprite = this.sprites.idle;
    }

    if (!activeSprite || activeSprite.naturalWidth === 0) return;

    // 1. Ambient Background Halo (subtle, only in normal window mode)
    const isMascot = typeof document !== "undefined" && document.body.classList.contains("mascot-mode");
    if (!isMascot) {
      const halo = ctx.createRadialGradient(w / 2, h * 0.45, w * 0.1, w / 2, h * 0.45, w * 0.55);
      halo.addColorStop(0, this.currentExpression.glowColor || "rgba(168, 85, 247, 0.2)");
      halo.addColorStop(1, "rgba(0, 0, 0, 0)");
      ctx.fillStyle = halo;
      ctx.beginPath();
      ctx.arc(w / 2, h * 0.45, w * 0.55, 0, Math.PI * 2);
      ctx.fill();
    }

    // 2. Cursor-anchored scale & center
    const userZoom = this.mascotScale || 1.0;
    const naturalW = activeSprite.naturalWidth;
    const naturalH = activeSprite.naturalHeight;

    // Base scale so sprite fills the stage at zoom=1
    const baseScale = Math.min((w * 0.95) / naturalW, (h * 0.95) / naturalH);

    // Pivot point in canvas pixels
    const pivotX = (this.zoomOrigin.nx || 0.5) * w;
    const pivotY = (this.zoomOrigin.ny || 0.4) * h;

    // Unzoomed draw position (centered horizontally, bottom-anchored vertically)
    const baseDrawX = (w - naturalW * baseScale) / 2 + this.mouse.x * 6;
    const baseDrawY = h - naturalH * baseScale + breath + this.mouse.y * 4;

    // Apply zoom around pivot
    ctx.save();
    ctx.translate(pivotX, pivotY);
    ctx.scale(userZoom, userZoom);
    ctx.translate(-pivotX, -pivotY);
    ctx.drawImage(activeSprite, baseDrawX, baseDrawY, naturalW * baseScale, naturalH * baseScale);
    ctx.restore();
  }

  _renderProcedural(now) {
    const ctx = this.ctx;
    const w = this.width;
    const h = this.height;

    const time = (now - this.startTime) / 1000;
    const breath = Math.sin((time * Math.PI * 2) / this.currentExpression.breathingPeriod) * 4;
    const lipMetrics = this.lipSync.update();

    const userZoom = this.mascotScale || 1.0;

    // Cursor-anchored zoom pivot
    const pivotX = (this.zoomOrigin.nx || 0.5) * w;
    const pivotY = (this.zoomOrigin.ny || 0.4) * h;

    // Base center of the face at zoom=1
    const baseCenterX = w / 2 + this.mouse.x * 6;
    const baseCenterY = h / 2 + breath + this.mouse.y * 4;
    const headRadius = Math.min(w, h) * 0.3;

    ctx.save();
    // Zoom around pivot
    ctx.translate(pivotX, pivotY);
    ctx.scale(userZoom, userZoom);
    ctx.translate(-pivotX, -pivotY);

    ctx.translate(baseCenterX, baseCenterY);
    ctx.rotate((this.currentExpression.headTilt * Math.PI) / 180);

    // 1. Ambient Background Halo
    const isMascot = typeof document !== "undefined" && document.body.classList.contains("mascot-mode");
    if (!isMascot) {
      const halo = ctx.createRadialGradient(0, 0, headRadius * 0.4, 0, 0, headRadius * 1.5);
      halo.addColorStop(0, this.currentExpression.glowColor);
      halo.addColorStop(1, "rgba(0, 0, 0, 0)");
      ctx.fillStyle = halo;
      ctx.beginPath();
      ctx.arc(0, 0, headRadius * 1.5, 0, Math.PI * 2);
      ctx.fill();
    }

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

      // Sclera
      ctx.fillStyle = "#ffffff";
      ctx.beginPath();
      ctx.ellipse(0, 0, eyeWidth, eyeHeight * blinkMul, 0, 0, Math.PI * 2);
      ctx.fill();
      ctx.strokeStyle = "#475569";
      ctx.lineWidth = 1.5;
      ctx.stroke();

      // Iris & Pupil (Follows Mouse Gaze)
      if (blinkMul > 0.3) {
        const pupilRadius = eyeWidth * 0.6;
        const gazeOffsetX = this.mouse.x * (eyeWidth - pupilRadius) * 0.8;
        const gazeOffsetY = this.mouse.y * (eyeHeight * blinkMul - pupilRadius) * 0.8;

        const irisGrad = ctx.createRadialGradient(
          gazeOffsetX, gazeOffsetY, pupilRadius * 0.2,
          gazeOffsetX, gazeOffsetY, pupilRadius
        );
        irisGrad.addColorStop(0, "#818cf8");
        irisGrad.addColorStop(0.7, "#4338ca");
        irisGrad.addColorStop(1, "#312e81");

        ctx.fillStyle = irisGrad;
        ctx.beginPath();
        ctx.arc(gazeOffsetX, gazeOffsetY, pupilRadius, 0, Math.PI * 2);
        ctx.fill();

        // Catchlight (anime eye sparkle)
        ctx.fillStyle = "rgba(255, 255, 255, 0.9)";
        ctx.beginPath();
        ctx.arc(gazeOffsetX - pupilRadius * 0.35, gazeOffsetY - pupilRadius * 0.35, pupilRadius * 0.3, 0, Math.PI * 2);
        ctx.fill();
      }

      ctx.restore();

      // Eyebrow
      const browY = eyeY - eyeHeight * 1.1;
      const browAngle = this.currentExpression.browAngle * side;
      ctx.save();
      ctx.translate(eyeX, browY);
      ctx.rotate(browAngle);
      ctx.strokeStyle = "#78350f";
      ctx.lineWidth = 2.5;
      ctx.lineCap = "round";
      ctx.beginPath();
      ctx.moveTo(-eyeWidth * 0.9, 0);
      ctx.quadraticCurveTo(0, -eyeHeight * 0.25, eyeWidth * 0.9, 0);
      ctx.stroke();
      ctx.restore();
    });

    // 6. Mouth & Lip-sync
    const mouthY = headRadius * 0.45;
    const mouthWidth = headRadius * 0.35;
    const mouthOpen = Math.max(lipMetrics.mouthOpen, 0.05);

    ctx.strokeStyle = "#991b1b";
    ctx.fillStyle = "#991b1b";
    ctx.lineWidth = 2.5;
    ctx.lineCap = "round";

    if (mouthOpen > 0.15) {
      // Open Speaking Mouth
      ctx.beginPath();
      ctx.ellipse(0, mouthY, mouthWidth * (0.8 + mouthOpen * 0.4), headRadius * 0.18 * mouthOpen, 0, 0, Math.PI * 2);
      ctx.fill();

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

    if (this.activeEngine === "live2d") {
      if (this.canvas) this.canvas.style.display = "none";
      if (this.live2dCanvas) {
        this.live2dCanvas.style.display = "block";
      }
      this.resize();
      await this._loadLive2DModel(this.activeModel);
    } else {
      if (this.live2dCanvas) this.live2dCanvas.style.display = "none";
      if (this.canvas) {
        this.canvas.style.display = "block";
      }
      this.resize();

      if (this.activeEngine === "sprites") {
        this._loadSpriteSet(this.activeModel);
      } else {
        this.sprites = null;
      }
    }
  }

  async _loadLive2DModel(modelName) {
    if (!modelName || modelName === "default") {
      if (this.currentLive2DModel && this.pixiApp) {
        this.pixiApp.stage.removeChild(this.currentLive2DModel);
        this.currentLive2DModel.destroy();
        this.currentLive2DModel = null;
      }
      return;
    }

    if (typeof PIXI === "undefined" || !PIXI.live2d || !PIXI.live2d.Live2DModel) {
      console.warn("[live2d] Pixi.js or Live2D Cubism runtime not loaded yet");
      return;
    }

    if (!this.live2dCanvas && typeof document !== "undefined") {
      this.live2dCanvas = document.getElementById("avatar-live2d-canvas");
    }

    const parent = this.live2dCanvas ? this.live2dCanvas.parentElement : null;
    const initialW = parent ? parent.clientWidth : 400;
    const initialH = parent ? parent.clientHeight : 600;

    if (!this.pixiApp && this.live2dCanvas) {
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
    if (modelName === "HoshinoAi") {
      modelPath = `../../models/avatar/live2d/HoshinoAi/Hoshino_Ai.model3.json`;
    }
    if (this.baseModelsPath) {
      if (modelName === "HoshinoAi") {
        modelPath = `file:///${this.baseModelsPath}/models/avatar/live2d/HoshinoAi/Hoshino_Ai.model3.json`;
      } else {
        modelPath = `file:///${this.baseModelsPath}/models/avatar/live2d/${modelName}/${modelName}.model3.json`;
      }
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
      this._repositionLive2DModel();
      this.pixiApp.stage.addChild(model);
      console.log(`[live2d] Model ${modelName} successfully loaded into Pixi stage!`);
    } catch (err) {
      console.error(`[live2d] Failed to load model ${modelName}:`, err);
    }
  }

  _repositionLive2DModel() {
    if (!this.currentLive2DModel || !this.live2dCanvas || !this.live2dCanvas.parentElement) return;
    const parent = this.live2dCanvas.parentElement;
    const stageW = parent.clientWidth || 400;
    const stageH = parent.clientHeight || 600;

    const model = this.currentLive2DModel;
    const naturalW = model.internalModel ? model.internalModel.width : model.width;
    const naturalH = model.internalModel ? model.internalModel.height : model.height;
    const userZoom = this.mascotScale || 1.0;

    const baseScale = Math.min((stageW * 0.95) / (naturalW || 2000), (stageH * 0.95) / (naturalH || 2000));
    const scale = baseScale * userZoom;

    // Cursor-anchored pivot in stage pixels
    const pivotX = (this.zoomOrigin.nx || 0.5) * stageW;
    const pivotY = (this.zoomOrigin.ny || 0.4) * stageH;

    // Base position at zoom=1 (centered horizontally, bottom-anchored vertically)
    const baseX = (stageW - (naturalW || 2000) * baseScale) / 2;
    const baseY = stageH - (naturalH || 2000) * baseScale;

    // Zoomed position: zoom around pivot
    model.scale.set(scale);
    model.x = pivotX + (baseX - pivotX) * userZoom;
    model.y = pivotY + (baseY - pivotY) * userZoom;
  }

  _loadSpriteSet(model) {
    if (!model || model === "default") {
      this.sprites = null;
      return;
    }
    this.sprites = {};
    const emotionKeys = [
      "idle", "speaking", "smile", "blush", "excited",
      "relaxed", "thinking", "concerned", "sad", "angry",
    ];
    emotionKeys.forEach((key) => {
      const img = new Image();
      img.onload = () => {
        img._isLoaded = true;
      };
      img.onerror = (e) => {
        console.warn(`[avatar] Failed to load sprite ${key} for ${model}:`, e);
      };
      if (this.baseModelsPath) {
        img.src = `file:///${this.baseModelsPath}/models/avatar/sprites/${model}/${key}.png`;
      } else {
        img.src = `../../models/avatar/sprites/${model}/${key}.png`;
      }
      this.sprites[key] = img;
    });
  }

  destroy() {
    this.stop();
    if (this.lipSync && this.lipSync.currentAudio) {
      this.lipSync.currentAudio.pause();
    }
    if (this.currentLive2DModel) {
      this.currentLive2DModel.destroy();
      this.currentLive2DModel = null;
    }
    if (this.pixiApp) {
      this.pixiApp.destroy(true, { children: true });
      this.pixiApp = null;
    }
  }

  /**
   * Wire mascot toolbar button events.
   * Called once after DOM is ready.
   */
  _setupMascotToolbar() {
    const get = (id) => document.getElementById(id);
    let _activePopup = null;

    const togglePopup = (popupEl) => {
      if (!popupEl) return;
      if (_activePopup && _activePopup !== popupEl) {
        _activePopup.style.display = "none";
      }
      const showing = popupEl.style.display !== "none";
      popupEl.style.display = showing ? "none" : "block";
      _activePopup = showing ? null : popupEl;
    };

    // --- Chat button ---
    const chatBtn = get("mascot-chat-btn");
    const chatPopup = get("mascot-chat-popup");
    if (chatBtn && chatPopup) {
      chatBtn.addEventListener("click", (e) => { e.stopPropagation(); togglePopup(chatPopup); });
    }

    const sendBtn = get("mascot-chat-send-btn");
    const chatInput = get("mascot-chat-input");
    if (sendBtn && chatInput) {
      const sendMsg = () => {
        const text = (chatInput.value || "").trim();
        if (!text) return;
        // Relay to main window chat via IPC
        if (window.lucia && window.lucia.window && window.lucia.window.sendMessage) {
          window.lucia.window.sendMessage(text);
        }
        chatInput.value = "";
        if (chatPopup) chatPopup.style.display = "none";
        _activePopup = null;
      };
      sendBtn.addEventListener("click", sendMsg);
      chatInput.addEventListener("keydown", (e) => {
        if (e.key === "Enter" && !e.shiftKey) { e.preventDefault(); sendMsg(); }
      });
    }

    // --- Model button ---
    const modelBtn = get("mascot-model-btn");
    const modelPopup = get("mascot-model-popup");
    const mascotEngineSelect = get("mascot-engine-select");
    const mascotAvatarSelect = get("mascot-avatar-select");
    if (modelBtn && modelPopup) {
      modelBtn.addEventListener("click", (e) => {
        e.stopPropagation();
        // Sync options from main selects
        const mainEngine = get("avatar-engine-select");
        const mainModel = get("avatar-model-select");
        if (mainEngine && mascotEngineSelect) mascotEngineSelect.value = mainEngine.value;
        if (mainModel && mascotAvatarSelect) {
          mascotAvatarSelect.innerHTML = mainModel.innerHTML;
          mascotAvatarSelect.value = mainModel.value;
        }
        togglePopup(modelPopup);
      });
    }
    if (mascotEngineSelect) {
      mascotEngineSelect.addEventListener("change", () => {
        const mainEngine = get("avatar-engine-select");
        if (mainEngine) {
          mainEngine.value = mascotEngineSelect.value;
          mainEngine.dispatchEvent(new Event("change"));
        }
      });
    }
    if (mascotAvatarSelect) {
      mascotAvatarSelect.addEventListener("change", () => {
        const mainModel = get("avatar-model-select");
        if (mainModel) {
          mainModel.value = mascotAvatarSelect.value;
          mainModel.dispatchEvent(new Event("change"));
        }
      });
    }

    // --- Voice button ---
    const voiceBtn = get("mascot-voice-btn");
    const voicePopup = get("mascot-voice-popup");
    const mascotVoiceSelect = get("mascot-voice-select");
    if (voiceBtn && voicePopup) {
      voiceBtn.addEventListener("click", (e) => {
        e.stopPropagation();
        const mainVoice = get("voice-model-select");
        if (mainVoice && mascotVoiceSelect) {
          mascotVoiceSelect.innerHTML = mainVoice.innerHTML;
          mascotVoiceSelect.value = mainVoice.value;
        }
        togglePopup(voicePopup);
      });
    }
    if (mascotVoiceSelect) {
      mascotVoiceSelect.addEventListener("change", () => {
        const mainVoice = get("voice-model-select");
        if (mainVoice) {
          mainVoice.value = mascotVoiceSelect.value;
          mainVoice.dispatchEvent(new Event("change"));
        }
      });
    }

    // --- Mic button ---
    const micBtn = get("mascot-mic-btn");
    if (micBtn) {
      micBtn.addEventListener("click", (e) => {
        e.stopPropagation();
        const mainMic = get("mic-btn");
        if (mainMic) mainMic.click();
        micBtn.classList.toggle("mascot-tool-btn--danger");
      });
    }

    // --- Close button ---
    const closeBtn = get("mascot-close-btn");
    if (closeBtn) {
      closeBtn.addEventListener("click", (e) => {
        e.stopPropagation();
        if (window.lucia && window.lucia.window && window.lucia.window.toggleMascot) {
          window.lucia.window.toggleMascot();
        }
      });
    }

    // Dismiss popups when clicking on canvas
    document.addEventListener("click", () => {
      if (_activePopup) {
        _activePopup.style.display = "none";
        _activePopup = null;
      }
    });
  }
}

if (typeof window !== "undefined" && window.avatarRegistry) {
  window.avatarRegistry.register("canvas", AvatarRenderer);
}

if (typeof module !== "undefined" && module.exports) {
  module.exports = { AvatarRenderer };
}
