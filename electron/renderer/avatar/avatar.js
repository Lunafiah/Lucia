/**
 * AvatarRenderer — 60 FPS Interactive Canvas Avatar for Lucia.
 * Connects live PAD emotion telemetry, Web Audio lip-syncing, natural blinking,
 * breathing cycles, and cursor gaze following.
 * Supports 2D Canvas procedural face, 2D Sprites (Columbina), and Live2D Cubism 4 (Hoshino Ai).
 */

const MASCOT_PRESETS = {
  small: { key: "small", scale: 0.75, width: 285, height: 405, label: "Small" },
  normal: { key: "normal", scale: 1.0, width: 380, height: 540, label: "Normal" },
  comfort: { key: "comfort", scale: 1.25, width: 475, height: 675, label: "Comfort" }
};
const MASCOT_PRESET_ORDER = ["small", "normal", "comfort"];

class AvatarRenderer {
  constructor(canvasElement) {
    this.canvas = canvasElement;
    this.ctx = canvasElement ? canvasElement.getContext("2d") : null;
    this.live2dCanvas = typeof document !== "undefined" ? document.getElementById("avatar-live2d-canvas") : null;
    this.vrmCanvas = typeof document !== "undefined" ? document.getElementById("avatar-vrm-canvas") : null;
    this.lipSync = new LipSyncProcessor();
    this.pixiApp = null;
    this.currentLive2DModel = null;
    this.baseModelsPath = null;
    this.mascotScale = 1.0;
    this.currentPreset = "normal";
    this.mascotInteractionState = 0; // 0: PASS_THROUGH, 1: HOVER_MODEL, 2: HOVER_UI, 3: ACTIVE_INTERACTION
    this._lastIgnoreState = null;
    this.pan = { x: 0, y: 0 };
    this.isDraggingModel = false;
    this.dragStart = { x: 0, y: 0 };
    this.isDraggingWindow = false;
    this.windowDragStart = { screenX: 0, screenY: 0 };
    this.lastWindowDragEndTime = 0;
    this.activeEngine = "canvas";
    this.activeModel = "default";
    this.sprites = null;
    this.targetFps = 60;
    this.lastFrameTime = 0;

    // Three.js 3D VRM State
    this.threeRenderer = null;
    this.threeScene = null;
    this.threeCamera = null;
    this.currentVRM = null;
    this.vrmProceduralRig = null;
    this.threeClock = null;

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

  /**
   * Set discrete interaction state (0: PASS_THROUGH, 1: HOVER_MODEL, 2: HOVER_UI, 3: ACTIVE_INTERACTION)
   * Only triggers IPC window:set-ignore-mouse-events when crossing the boundary between pass-through and interactive.
   */
  _setInteractionState(newState) {
    if (this.mascotInteractionState === newState) return;
    this.mascotInteractionState = newState;

    const isMascot = typeof document !== "undefined" && document.body.classList.contains("mascot-mode");
    if (!isMascot) {
      if (this._lastIgnoreState !== false) {
        this._lastIgnoreState = false;
        if (window.lucia && window.lucia.window && window.lucia.window.setIgnoreMouseEvents) {
          window.lucia.window.setIgnoreMouseEvents(false);
        }
      }
      return;
    }

    const shouldIgnore = (newState === 0);
    if (this._lastIgnoreState !== shouldIgnore) {
      this._lastIgnoreState = shouldIgnore;
      if (window.lucia && window.lucia.window && window.lucia.window.setIgnoreMouseEvents) {
        window.lucia.window.setIgnoreMouseEvents(shouldIgnore, { forward: true });
      }
    }
  }

  /**
   * Set discrete zoom preset (small, normal, comfort) preserving feet anchor.
   */
  setZoomPreset(presetKey) {
    if (!MASCOT_PRESETS[presetKey]) return;
    this.currentPreset = presetKey;
    const preset = MASCOT_PRESETS[presetKey];
    this.mascotScale = preset.scale;

    if (typeof document !== "undefined") {
      ["small", "normal", "comfort"].forEach((k) => {
        const btn = document.getElementById(`btn-scale-${k}`);
        if (btn) btn.classList.toggle("active", k === presetKey);
      });
    }

    // Immediately synchronize and clamp renderer dimensions to the canonical preset
    this.resize();

    if (this.activeEngine === "live2d") {
      this._repositionLive2DModel();
    }
    this._updateToolbarPosition();

    if (window.lucia && window.lucia.window && window.lucia.window.setMascotPreset) {
      window.lucia.window.setMascotPreset(presetKey);
    }
  }

  _bindEvents() {
    const onGazeMove = (e) => {
      if (this.gazeEnabled === false) {
        this.mouse.targetX = 0;
        this.mouse.targetY = 0;
        return;
      }
      const activeEl =
        this.activeEngine === "live2d"
          ? this.live2dCanvas
          : this.activeEngine === "vrm"
          ? this.vrmCanvas
          : this.canvas;
      if (!activeEl) return;
      const rect = activeEl.getBoundingClientRect();
      const centerX = rect.left + rect.width / 2;
      const centerY = rect.top + rect.height / 2;

      // Normalized gaze in [-1, 1]
      this.mouse.targetX = Math.max(-1, Math.min(1, (e.clientX - centerX) / (rect.width / 2 || 1)));
      this.mouse.targetY = Math.max(-1, Math.min(1, (e.clientY - centerY) / (rect.height / 2 || 1)));
    };

    const onResize = () => this.resize();

    const getActiveWrapper = () =>
      (this.canvas && this.canvas.parentElement) ||
      (this.live2dCanvas && this.live2dCanvas.parentElement) ||
      (this.vrmCanvas && this.vrmCanvas.parentElement);

    const onWheel = (e) => {
      // REQUIRE Ctrl + Wheel to prevent accidental trackpad zoom
      if (!e.ctrlKey) return;

      // Prevent zoom during dragging or during 800ms trackpad inertia cooldown after dragging
      if (
        this.isDraggingModel ||
        this.isDraggingWindow ||
        (Date.now() - (this.lastWindowDragEndTime || 0) < 800)
      ) {
        return;
      }

      // Ignore zoom when scrolling inside mascot toolbar, flyout, or popover
      if (
        e.target &&
        typeof e.target.closest === "function" &&
        (e.target.closest("#mascot-toolbar") ||
          e.target.closest("#mascot-quick-talk-flyout") ||
          e.target.closest("#mascot-presence-popover"))
      ) {
        return;
      }

      const wrapper = getActiveWrapper();
      if (!wrapper || !e.target || !(e.target instanceof Node) || !wrapper.contains(e.target)) return;

      // STRICT REQUIREMENT: Cursor must be positioned directly on the avatar model to zoom!
      if (!this.isCursorOverModel(e.clientX, e.clientY)) return;

      e.preventDefault();

      const isMascot = typeof document !== "undefined" && document.body.classList.contains("mascot-mode");
      if (isMascot) {
        const currentIndex = MASCOT_PRESET_ORDER.indexOf(this.currentPreset);
        if (e.deltaY < 0) {
          // Zoom in
          if (currentIndex < MASCOT_PRESET_ORDER.length - 1) {
            this.setZoomPreset(MASCOT_PRESET_ORDER[currentIndex + 1]);
          }
        } else if (e.deltaY > 0) {
          // Zoom out
          if (currentIndex > 0) {
            this.setZoomPreset(MASCOT_PRESET_ORDER[currentIndex - 1]);
          }
        }
      } else {
        const delta = e.deltaY < 0 ? 0.08 : -0.08;
        this.mascotScale = Math.max(0.3, Math.min(4.0, (this.mascotScale || 1.0) + delta));
        if (this.activeEngine === "live2d") {
          this._repositionLive2DModel();
        }
        this._updateToolbarPosition();
      }
    };

    const onMouseDown = (e) => {
      const isMascot = typeof document !== "undefined" && document.body.classList.contains("mascot-mode");
      const wrapper = getActiveWrapper();
      if (!wrapper || !e.target || !(e.target instanceof Node) || !wrapper.contains(e.target)) return;

      // Ignore toolbar and header clicks
      if (
        e.target &&
        typeof e.target.closest === "function" &&
        (e.target.closest("#mascot-toolbar") ||
          e.target.closest(".avatar-top-bar") ||
          e.target.closest("#mascot-quick-talk-flyout") ||
          e.target.closest("#mascot-presence-popover"))
      ) {
        return;
      }

      if (isMascot) {
        if (e.button === 0) {
          e.preventDefault();
          this._setInteractionState(3); // ACTIVE_INTERACTION
          this.isDraggingWindow = true;
          this.isDraggingModel = false;
          this.windowDragStart = { screenX: e.screenX, screenY: e.screenY };
          if (wrapper) wrapper.style.cursor = "grabbing";
        }
        return;
      } else {
        if (e.button === 0 || e.button === 1) {
          this.isDraggingModel = true;
          this.dragStart = {
            x: e.clientX - this.pan.x,
            y: e.clientY - this.pan.y,
          };
          if (wrapper) wrapper.style.cursor = "grabbing";
        }
      }
    };

    const onMouseMove = (e) => {
      const isMascot = typeof document !== "undefined" && document.body.classList.contains("mascot-mode");

      // Update interaction state machine
      if (isMascot) {
        if (this.isDraggingWindow || this.isDraggingModel) {
          this._setInteractionState(3); // ACTIVE_INTERACTION
        } else if (
          e.target &&
          typeof e.target.closest === "function" &&
          (e.target.closest("#mascot-toolbar") ||
            e.target.closest("#mascot-quick-talk-flyout") ||
            e.target.closest("#mascot-presence-popover"))
        ) {
          this._setInteractionState(2); // HOVER_UI
        } else if (this.isCursorOverModel(e.clientX, e.clientY)) {
          this._setInteractionState(1); // HOVER_MODEL
        } else {
          this._setInteractionState(0); // PASS_THROUGH
        }
      }

      const wrapper = getActiveWrapper();
      if (this.isDraggingWindow) {
        const dx = e.screenX - this.windowDragStart.screenX;
        const dy = e.screenY - this.windowDragStart.screenY;
        this.windowDragStart.screenX = e.screenX;
        this.windowDragStart.screenY = e.screenY;
        if (window.lucia && window.lucia.window && window.lucia.window.moveMascotBy) {
          window.lucia.window.moveMascotBy(dx, dy);
        }
        return;
      } else if (this.isDraggingModel) {
        const clampX = (this.width || 400) * 0.75;
        const clampY = (this.height || 600) * 0.75;
        this.pan.x = Math.max(-clampX, Math.min(clampX, e.clientX - this.dragStart.x));
        this.pan.y = Math.max(-clampY, Math.min(clampY, e.clientY - this.dragStart.y));
        if (this.activeEngine === "live2d") {
          this._repositionLive2DModel();
        }
        this._updateToolbarPosition();
      }
    };

    const onMouseUp = (e) => {
      const wrapper = getActiveWrapper();
      if (this.isDraggingWindow) {
        this.lastWindowDragEndTime = Date.now();
      }
      this.isDraggingWindow = false;
      this.isDraggingModel = false;
      if (wrapper) wrapper.style.cursor = "grab";

      const isMascot = typeof document !== "undefined" && document.body.classList.contains("mascot-mode");
      if (isMascot) {
        if (
          e.target &&
          typeof e.target.closest === "function" &&
          (e.target.closest("#mascot-toolbar") ||
            e.target.closest("#mascot-quick-talk-flyout") ||
            e.target.closest("#mascot-presence-popover"))
        ) {
          this._setInteractionState(2);
        } else if (this.isCursorOverModel(e.clientX, e.clientY)) {
          this._setInteractionState(1);
        } else {
          this._setInteractionState(0);
        }
      }
    };

    const onMouseLeave = () => {
      const isMascot = typeof document !== "undefined" && document.body.classList.contains("mascot-mode");
      if (isMascot && !this.isDraggingWindow && !this.isDraggingModel) {
        this._setInteractionState(0);
      }
    };

    const onContextMenu = (e) => {
      const wrapper = getActiveWrapper();
      if (!wrapper || !e.target || !(e.target instanceof Node) || !wrapper.contains(e.target)) return;
      if (e.target && typeof e.target.closest === "function" && e.target.closest("#mascot-toolbar")) {
        e.preventDefault();
      }
    };

    const onDblClick = (e) => {
      const wrapper = getActiveWrapper();
      if (!wrapper || !e.target || !(e.target instanceof Node) || !wrapper.contains(e.target)) return;
      if (
        e.target &&
        typeof e.target.closest === "function" &&
        (e.target.closest("#mascot-toolbar") ||
          e.target.closest(".avatar-top-bar") ||
          e.target.closest("#mascot-quick-talk-flyout") ||
          e.target.closest("#mascot-presence-popover"))
      ) {
        return;
      }

      // STRICT HIT TEST: must double-click avatar body
      if (!this.isCursorOverModel(e.clientX, e.clientY)) return;

      this.pan = { x: 0, y: 0 };
      this.setZoomPreset("normal");

      // Close open overlays
      const flyout = document.getElementById("mascot-quick-talk-flyout");
      const popover = document.getElementById("mascot-presence-popover");
      if (flyout) flyout.style.display = "none";
      if (popover) popover.style.display = "none";
      const toolbar = document.getElementById("mascot-toolbar");
      if (toolbar) toolbar.classList.remove("has-active-popup");
      const quickTalkBtn = document.getElementById("mascot-quick-talk-btn");
      if (quickTalkBtn) quickTalkBtn.classList.remove("active");
      const menuBtn = document.getElementById("mascot-presence-menu-btn");
      if (menuBtn) menuBtn.classList.remove("active");

      if (this.activeEngine === "live2d") {
        this._repositionLive2DModel();
      }
      this._updateToolbarPosition();
      if (window.lucia && window.lucia.window && window.lucia.window.resetMascotBounds) {
        window.lucia.window.resetMascotBounds();
      }
    };

    this._eventListeners = {
      gaze: onGazeMove,
      resize: onResize,
      wheel: onWheel,
      mousedown: onMouseDown,
      mousemove: onMouseMove,
      mouseup: onMouseUp,
      mouseleave: onMouseLeave,
      contextmenu: onContextMenu,
      dblclick: onDblClick,
    };

    window.addEventListener("mousemove", onGazeMove);
    window.addEventListener("resize", onResize);
    window.addEventListener("wheel", onWheel, { passive: false });
    window.addEventListener("mousedown", onMouseDown);
    window.addEventListener("mousemove", onMouseMove);
    window.addEventListener("mouseup", onMouseUp);
    window.addEventListener("mouseleave", onMouseLeave);
    window.addEventListener("contextmenu", onContextMenu);
    window.addEventListener("dblclick", onDblClick);
  }

  resize() {
    const isMascot = typeof document !== "undefined" && document.body.classList.contains("mascot-mode");
    const dpr = (typeof window !== "undefined" && window.devicePixelRatio) || 1;

    let targetWidth, targetHeight;
    if (isMascot) {
      const preset = MASCOT_PRESETS[this.currentPreset] || MASCOT_PRESETS.normal;
      targetWidth = preset.width;
      targetHeight = preset.height;
      this.pan = { x: 0, y: 0 };
    } else {
      const wrapper =
        (this.canvas && this.canvas.parentElement) ||
        (this.live2dCanvas && this.live2dCanvas.parentElement) ||
        (this.vrmCanvas && this.vrmCanvas.parentElement);
      if (!wrapper) return;

      const rect = wrapper.getBoundingClientRect();
      if (rect.width <= 0 || rect.height <= 0) return;
      targetWidth = rect.width;
      targetHeight = rect.height;
    }

    this.width = targetWidth;
    this.height = targetHeight;

    if (this.canvas) {
      this.canvas.width = Math.floor(targetWidth * dpr);
      this.canvas.height = Math.floor(targetHeight * dpr);
    }

    if (this.pixiApp && this.live2dCanvas) {
      this.pixiApp.renderer.resize(targetWidth, targetHeight);
      this._repositionLive2DModel();
    }

    if (this.threeRenderer && this.threeCamera && this.vrmCanvas) {
      this.threeCamera.aspect = targetWidth / (targetHeight || 1);
      this.threeCamera.updateProjectionMatrix();
      this.threeRenderer.setSize(targetWidth, targetHeight);
    }

    this._updateToolbarPosition();
  }

  /**
   * Calculate precise visual bounding box of the active model.
   */
  getModelBounds() {
    const isMascot = typeof document !== "undefined" && document.body.classList.contains("mascot-mode");
    const activeEl =
      this.activeEngine === "live2d"
        ? this.live2dCanvas
        : this.activeEngine === "vrm"
        ? this.vrmCanvas
        : this.canvas;
    const preset = isMascot ? (MASCOT_PRESETS[this.currentPreset] || MASCOT_PRESETS.normal) : null;
    const w = isMascot ? preset.width : (this.width || (activeEl ? activeEl.clientWidth : 380) || 380);
    const h = isMascot ? preset.height : (this.height || (activeEl ? activeEl.clientHeight : 540) || 540);
    const userZoom = isMascot ? 1.0 : Math.max(0.3, Math.min(4.0, this.mascotScale || 1.0));
    const panX = isMascot ? 0 : this.pan.x;
    const panY = isMascot ? 0 : this.pan.y;

    let centerX = w / 2 + panX;
    let bottomY = h + panY;
    let left = centerX - 100;
    let right = centerX + 100;
    let top = bottomY - 300;
    let bottom = bottomY;

    if (this.activeEngine === "sprites" && this._hasLoadedSprites()) {
      const activeSprite = this.sprites.idle;
      const naturalW = activeSprite.naturalWidth || 400;
      const naturalH = activeSprite.naturalHeight || 600;
      const baseScale = Math.min((w * 0.95) / naturalW, (h * 0.95) / naturalH);
      const scale = baseScale * userZoom;
      const drawW = naturalW * scale;
      const drawH = naturalH * scale;
      const drawX = (w - drawW) / 2 + panX;
      const drawY = h - drawH + panY;
      left = drawX;
      right = drawX + drawW;
      top = drawY;
      bottom = drawY + drawH;
      centerX = drawX + drawW / 2;
      bottomY = bottom;
    } else if (this.activeEngine === "live2d" && this.currentLive2DModel) {
      const m = this.currentLive2DModel;
      const mw = m.width || (m.internalModel ? m.internalModel.width * (m.scale ? m.scale.x : 1) : 400);
      const mh = m.height || (m.internalModel ? m.internalModel.height * (m.scale ? m.scale.y : 1) : 600);
      left = m.x;
      right = m.x + mw;
      top = m.y;
      bottom = m.y + mh;
      centerX = m.x + mw / 2;
      bottomY = bottom;
    } else if (this.activeEngine === "vrm") {
      const modelH = h * 0.75 * userZoom;
      const modelW = modelH * 0.55;
      centerX = w / 2 + panX;
      bottomY = h * 0.88 + panY;
      top = bottomY - modelH;
      left = centerX - modelW / 2;
      right = centerX + modelW / 2;
      bottom = bottomY;
    } else {
      // Procedural 2D Canvas
      const headRadius = Math.min(w, h) * 0.3 * userZoom;
      centerX = w / 2 + panX;
      const centerY = h / 2 + panY;
      top = centerY - headRadius * 1.3;
      bottom = centerY + headRadius * 1.8;
      left = centerX - headRadius * 1.5;
      right = centerX + headRadius * 1.5;
      bottomY = bottom;
    }

    return { centerX, bottomY, left, right, top, bottom };
  }

  /**
   * Hit test whether client coordinates are positioned over the active avatar model.
   */
  isCursorOverModel(clientX, clientY) {
    const activeEl =
      this.activeEngine === "live2d"
        ? this.live2dCanvas
        : this.activeEngine === "vrm"
        ? this.vrmCanvas
        : this.canvas;
    if (!activeEl) return false;

    const rect = activeEl.getBoundingClientRect();
    const relX = clientX - rect.left;
    const relY = clientY - rect.top;

    const bounds = this.getModelBounds();
    const buffer = 20; // 20px margin for easy targeting
    return (
      relX >= bounds.left - buffer &&
      relX <= bounds.right + buffer &&
      relY >= bounds.top - buffer &&
      relY <= bounds.bottom + buffer
    );
  }

  /**
   * Dynamically anchor mascot toolbar dock directly beneath the model.
   */
  _updateToolbarPosition() {
    const toolbar = document.getElementById("mascot-toolbar");
    if (!toolbar) return;
    const isMascot = typeof document !== "undefined" && document.body.classList.contains("mascot-mode");
    if (!isMascot) return;

    const bounds = this.getModelBounds();
    const preset = MASCOT_PRESETS[this.currentPreset] || MASCOT_PRESETS.normal;
    const winW = preset.width;
    const winH = preset.height;

    // Anchor toolbar directly underneath the model's bottom center
    const safeX = Math.max(120, Math.min(winW - 120, bounds.centerX));
    const dockHeight = 52;
    // Sit 8px below the model's bottom, clamped so dock never overflows window edge
    const safeY = Math.max(dockHeight, Math.min(winH - dockHeight - 6, bounds.bottomY + 8));

    toolbar.style.left = `${safeX}px`;
    toolbar.style.top = `${safeY}px`;
    toolbar.style.bottom = "auto";
  }

  /**
   * Set target rendering framerate (e.g. 60 vs 30 FPS for battery saving).
   */
  setTargetFps(fps) {
    const parsed = parseInt(fps, 10);
    if (isNaN(parsed)) {
      this.targetFps = 60;
      return;
    }
    this.targetFps = Math.max(15, Math.min(120, parsed));
  }

  /**
   * Toggle mouse cursor gaze tracking.
   */
  setGazeTracking(enabled) {
    this.gazeEnabled = !!enabled;
    if (!this.gazeEnabled) {
      this.mouse.targetX = 0;
      this.mouse.targetY = 0;
      this.mouse.x = 0;
      this.mouse.y = 0;
    }
  }

  /**
   * Toggle natural ambient eye blinking.
   */
  setAmbientBlinking(enabled) {
    this.blinkingEnabled = !!enabled;
    if (!this.blinkingEnabled) {
      this.isBlinking = false;
      this.blinkProgress = 0;
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
      this.animationFrameId = requestAnimationFrame(loop);
      if (this.targetFps && this.targetFps < 60) {
        const elapsed = now - this.lastFrameTime;
        if (elapsed < (1000 / this.targetFps) - 2) return;
        this.lastFrameTime = now;
      }
      this._updatePhysics(now);
      this._render(now);
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
    if (this.blinkingEnabled !== false && now >= this.nextBlinkTime && !this.isBlinking) {
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
    this._updateToolbarPosition();

    if (this.activeEngine === "vrm") {
      this._updateVRM(now);
      return;
    }

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

    // 2. Scale & Center Sprite (Honoring mascotScale zoom & mouse pan!)
    const userZoom = isMascot ? 1.0 : (this.mascotScale || 1.0);
    const panX = isMascot ? 0 : this.pan.x;
    const panY = isMascot ? 0 : this.pan.y;
    const naturalW = activeSprite.naturalWidth;
    const naturalH = activeSprite.naturalHeight;
    const baseScale = Math.min((w * 0.95) / naturalW, (h * 0.95) / naturalH);
    const scale = baseScale * userZoom;
    const drawW = naturalW * scale;
    const drawH = naturalH * scale;

    const drawX = (w - drawW) / 2 + this.mouse.x * 6 + panX;
    const drawY = h - drawH + breath + this.mouse.y * 4 + panY;

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

    const isMascot = typeof document !== "undefined" && document.body.classList.contains("mascot-mode");
    const userZoom = isMascot ? 1.0 : (this.mascotScale || 1.0);
    const panX = isMascot ? 0 : this.pan.x;
    const panY = isMascot ? 0 : this.pan.y;
    const centerX = w / 2 + this.mouse.x * 6 + panX;
    const centerY = h / 2 + breath + this.mouse.y * 4 + panY;
    const headRadius = Math.min(w, h) * 0.3 * userZoom;

    ctx.save();
    ctx.translate(centerX, centerY);
    ctx.rotate((this.currentExpression.headTilt * Math.PI) / 180);

    // 1. Ambient Background Halo
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

    if (!this.vrmCanvas && typeof document !== "undefined") {
      this.vrmCanvas = document.getElementById("avatar-vrm-canvas");
    }
    if (!this.live2dCanvas && typeof document !== "undefined") {
      this.live2dCanvas = document.getElementById("avatar-live2d-canvas");
    }

    if (this.canvas) this.canvas.style.display = "none";
    if (this.live2dCanvas) this.live2dCanvas.style.display = "none";
    if (this.vrmCanvas) this.vrmCanvas.style.display = "none";

    if (this.activeEngine === "live2d") {
      if (this.live2dCanvas) this.live2dCanvas.style.display = "block";
      this.resize();
      await this._loadLive2DModel(this.activeModel);
    } else if (this.activeEngine === "vrm") {
      if (this.vrmCanvas) this.vrmCanvas.style.display = "block";
      this.resize();
      await this._loadVRMModel(this.activeModel);
    } else {
      if (this.canvas) this.canvas.style.display = "block";
      this.resize();
      if (this.activeEngine === "sprites") {
        this._loadSpriteSet(this.activeModel);
      } else {
        this.sprites = null;
      }
    }
  }

  _initThreeVRM() {
    if (typeof THREE === "undefined") return;
    if (!this.vrmCanvas && typeof document !== "undefined") {
      this.vrmCanvas = document.getElementById("avatar-vrm-canvas");
    }
    if (!this.vrmCanvas || this.threeRenderer) return;

    const parent = this.vrmCanvas.parentElement;
    const w = parent ? parent.clientWidth : 400;
    const h = parent ? parent.clientHeight : 600;

    try {
      this.threeRenderer = new THREE.WebGLRenderer({
        canvas: this.vrmCanvas,
        alpha: true,
        antialias: true,
      });
      this.threeRenderer.setSize(w, h);
      this.threeRenderer.setPixelRatio(window.devicePixelRatio || 1);
      if (THREE.sRGBEncoding) {
        this.threeRenderer.outputEncoding = THREE.sRGBEncoding;
      }

      this.threeScene = new THREE.Scene();
      this.threeCamera = new THREE.PerspectiveCamera(30, w / (h || 1), 0.1, 20.0);
      this.threeCamera.position.set(0, 1.35, 1.8);

      const dirLight = new THREE.DirectionalLight(0xffffff, 1.2);
      dirLight.position.set(1.0, 2.0, 1.0).normalize();
      this.threeScene.add(dirLight);

      const ambientLight = new THREE.AmbientLight(0xffffff, 0.7);
      this.threeScene.add(ambientLight);

      const rimLight = new THREE.DirectionalLight(0xa855f7, 1.0);
      rimLight.position.set(-1.0, 1.5, -1.0).normalize();
      this.threeScene.add(rimLight);

      this.threeClock = new THREE.Clock();
    } catch (e) {
      console.warn("[vrm] Failed to initialize Three.js WebGL context:", e);
    }
  }

  _create3DProceduralRig() {
    if (!this.threeScene || typeof THREE === "undefined") return;
    if (this.vrmProceduralRig) {
      this.threeScene.remove(this.vrmProceduralRig);
      this.vrmProceduralRig = null;
    }

    const group = new THREE.Group();
    group.position.set(0, 1.35, 0);

    // Head sphere with glowing aura
    const headGeo = new THREE.SphereGeometry(0.28, 32, 32);
    const headMat = new THREE.MeshStandardMaterial({
      color: 0x1e1b4b,
      emissive: 0x581c87,
      emissiveIntensity: 0.35,
      roughness: 0.2,
      metalness: 0.1,
    });
    const head = new THREE.Mesh(headGeo, headMat);
    head.name = "head";
    group.add(head);

    // Glowing eyes
    const eyeGeo = new THREE.SphereGeometry(0.045, 16, 16);
    eyeGeo.scale(1, 1.3, 0.4);
    const eyeMat = new THREE.MeshStandardMaterial({
      color: 0x22d3ee,
      emissive: 0x38bdf8,
      emissiveIntensity: 0.9,
    });
    const leftEye = new THREE.Mesh(eyeGeo, eyeMat);
    leftEye.position.set(-0.095, 0.03, 0.25);
    leftEye.name = "leftEye";
    head.add(leftEye);

    const rightEye = new THREE.Mesh(eyeGeo, eyeMat);
    rightEye.position.set(0.095, 0.03, 0.25);
    rightEye.name = "rightEye";
    head.add(rightEye);

    // Mouth
    const mouthGeo = new THREE.TorusGeometry(0.04, 0.008, 8, 16, Math.PI);
    const mouthMat = new THREE.MeshBasicMaterial({ color: 0xf43f5e });
    const mouth = new THREE.Mesh(mouthGeo, mouthMat);
    mouth.rotation.x = Math.PI;
    mouth.position.set(0, -0.1, 0.26);
    mouth.name = "mouth";
    head.add(mouth);

    // Body
    const bodyGeo = new THREE.CylinderGeometry(0.18, 0.28, 0.45, 24);
    const bodyMat = new THREE.MeshStandardMaterial({
      color: 0x0f172a,
      roughness: 0.4,
      metalness: 0.2,
    });
    const body = new THREE.Mesh(bodyGeo, bodyMat);
    body.position.set(0, -0.42, 0);
    body.name = "body";
    group.add(body);

    // Orbital ring
    const ringGeo = new THREE.TorusGeometry(0.42, 0.006, 16, 64);
    const ringMat = new THREE.MeshBasicMaterial({
      color: 0xa855f7,
      transparent: true,
      opacity: 0.7,
    });
    const ring = new THREE.Mesh(ringGeo, ringMat);
    ring.rotation.x = Math.PI * 0.45;
    ring.name = "orbitalRing";
    group.add(ring);

    this.vrmProceduralRig = group;
    this.threeScene.add(group);
  }

  _animate3DProceduralRig(now, gazeX, gazeY) {
    if (!this.vrmProceduralRig) return;
    const time = (now - this.startTime) / 1000;
    const breath = Math.sin(time * 2.2) * 0.02;

    const head = this.vrmProceduralRig.getObjectByName("head");
    if (head) {
      head.rotation.y = gazeX * 0.35;
      head.rotation.x = -gazeY * 0.25;
      head.position.y = breath;

      // Blinking
      const leftEye = head.getObjectByName("leftEye");
      const rightEye = head.getObjectByName("rightEye");
      const eyeScaleY = this.isBlinking ? 0.1 : 1.0;
      if (leftEye) leftEye.scale.y = eyeScaleY * 1.3;
      if (rightEye) rightEye.scale.y = eyeScaleY * 1.3;

      // Lip sync mouth
      const mouth = head.getObjectByName("mouth");
      const lipMetrics = this.lipSync ? this.lipSync.update() : { mouthOpen: 0 };
      if (mouth) {
        mouth.scale.set(1.0 + lipMetrics.mouthOpen * 0.5, 1.0 + lipMetrics.mouthOpen * 2.5, 1.0);
      }
    }

    const ring = this.vrmProceduralRig.getObjectByName("orbitalRing");
    if (ring) {
      ring.rotation.z = time * 0.4;
    }
  }

  async _loadVRMModel(modelName) {
    this._initThreeVRM();
    if (!this.threeScene) return;

    if (this.currentVRM) {
      this.threeScene.remove(this.currentVRM.scene);
      if (typeof THREE_VRM !== "undefined" && THREE_VRM.VRMUtils) {
        THREE_VRM.VRMUtils.deepDispose(this.currentVRM.scene);
      }
      this.currentVRM = null;
    }
    if (this.vrmProceduralRig) {
      this.threeScene.remove(this.vrmProceduralRig);
      this.vrmProceduralRig = null;
    }

    if (!modelName || modelName === "default") {
      this._create3DProceduralRig();
      return;
    }

    if (typeof THREE === "undefined" || !THREE.GLTFLoader || typeof THREE_VRM === "undefined") {
      console.warn("[vrm] Three.js, GLTFLoader, or THREE_VRM not loaded yet");
      this._create3DProceduralRig();
      return;
    }

    let vrmPath = `../../models/avatar/vrm/${modelName}`;
    if (this.baseModelsPath) {
      vrmPath = `file:///${this.baseModelsPath}/models/avatar/vrm/${modelName}`;
    }

    const loader = new THREE.GLTFLoader();
    try {
      console.log(`[vrm] Loading VRM model from: ${vrmPath}`);
      loader.load(
        vrmPath,
        (gltf) => {
          THREE_VRM.VRM.from(gltf)
            .then((vrm) => {
              this.currentVRM = vrm;
              this.threeScene.add(vrm.scene);
              vrm.scene.rotation.y = Math.PI; // Face the camera
              console.log(`[vrm] Model ${modelName} loaded into 3D scene!`);
            })
            .catch((e) => {
              console.warn(`[vrm] VRM parsing failed, using 3D rig:`, e);
              this._create3DProceduralRig();
            });
        },
        undefined,
        (err) => {
          console.warn(`[vrm] Failed to load ${modelName}, using 3D rig:`, err);
          this._create3DProceduralRig();
        }
      );
    } catch (err) {
      console.error("[vrm] Load exception:", err);
      this._create3DProceduralRig();
    }
  }

  _updateVRM(now) {
    if (!this.threeRenderer || !this.threeCamera || !this.threeScene) return;

    const delta = this.threeClock ? this.threeClock.getDelta() : 0.016;
    const isMascot = typeof document !== "undefined" && document.body.classList.contains("mascot-mode");
    const userZoom = isMascot ? 1.0 : (this.mascotScale || 1.0);
    const panX = isMascot ? 0 : this.pan.x;
    const panY = isMascot ? 0 : this.pan.y;

    // Pan & Zoom controls in 3D:
    // - pan.x and pan.y shift camera position in world space
    // - mascotScale shifts camera distance along Z
    this.threeCamera.position.z = 1.8 / Math.max(0.2, userZoom);
    this.threeCamera.position.x = -panX * 0.0035;
    this.threeCamera.position.y = 1.35 + panY * 0.0035;
    this.threeCamera.lookAt(this.threeCamera.position.x, 1.35, 0);

    const gazeX = this.mouse.x * 0.3;
    const gazeY = this.mouse.y * 0.2;

    if (this.currentVRM) {
      this.currentVRM.update(delta);

      if (this.currentVRM.humanoid) {
        const head = this.currentVRM.humanoid.getBoneNode(THREE_VRM.VRMSchema.HumanoidBoneName.Head);
        if (head) {
          head.rotation.y = gazeX;
          head.rotation.x = -gazeY;
        }
      }

      const lipMetrics = this.lipSync ? this.lipSync.update() : { mouthOpen: 0 };
      if (this.currentVRM.blendShapeProxy) {
        this.currentVRM.blendShapeProxy.setValue(
          THREE_VRM.VRMSchema.BlendShapePresetName.A,
          Math.min(1.0, lipMetrics.mouthOpen * 2.0)
        );
        this.currentVRM.blendShapeProxy.setValue(
          THREE_VRM.VRMSchema.BlendShapePresetName.Blink,
          this.blinkProgress
        );
        this.currentVRM.blendShapeProxy.setValue(
          THREE_VRM.VRMSchema.BlendShapePresetName.Joy,
          this.currentExpression.smile
        );
      }
    } else if (this.vrmProceduralRig) {
      this._animate3DProceduralRig(now, gazeX, gazeY);
    }

    this.threeRenderer.render(this.threeScene, this.threeCamera);
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
    if (!this.currentLive2DModel) return;
    const isMascot = typeof document !== "undefined" && document.body.classList.contains("mascot-mode");
    let stageW, stageH;
    if (isMascot) {
      const preset = MASCOT_PRESETS[this.currentPreset] || MASCOT_PRESETS.normal;
      stageW = preset.width;
      stageH = preset.height;
    } else {
      if (!this.live2dCanvas || !this.live2dCanvas.parentElement) return;
      const parent = this.live2dCanvas.parentElement;
      stageW = parent.clientWidth || 400;
      stageH = parent.clientHeight || 600;
    }

    const model = this.currentLive2DModel;
    const naturalW = model.internalModel ? model.internalModel.width : model.width;
    const naturalH = model.internalModel ? model.internalModel.height : model.height;
    const userZoom = isMascot ? 1.0 : (this.mascotScale || 1.0);
    const panX = isMascot ? 0 : this.pan.x;
    const panY = isMascot ? 0 : this.pan.y;

    const baseScale = Math.min((stageW * 0.95) / (naturalW || 2000), (stageH * 0.95) / (naturalH || 2000));
    const scale = baseScale * userZoom;

    model.scale.set(scale);
    model.x = (stageW - (naturalW || 2000) * scale) / 2 + panX;
    model.y = (stageH - (naturalH || 2000) * scale) + panY;
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
    if (this._eventListeners) {
      window.removeEventListener("mousemove", this._eventListeners.gaze);
      window.removeEventListener("resize", this._eventListeners.resize);
      window.removeEventListener("wheel", this._eventListeners.wheel);
      window.removeEventListener("mousedown", this._eventListeners.mousedown);
      window.removeEventListener("mousemove", this._eventListeners.mousemove);
      window.removeEventListener("mouseup", this._eventListeners.mouseup);
      window.removeEventListener("mouseleave", this._eventListeners.mouseleave);
      window.removeEventListener("contextmenu", this._eventListeners.contextmenu);
      window.removeEventListener("dblclick", this._eventListeners.dblclick);
      this._eventListeners = null;
    }
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
    if (this.currentVRM) {
      if (typeof THREE_VRM !== "undefined" && THREE_VRM.VRMUtils) {
        THREE_VRM.VRMUtils.deepDispose(this.currentVRM.scene);
      }
      this.currentVRM = null;
    }
    if (this.threeRenderer) {
      this.threeRenderer.dispose();
      this.threeRenderer = null;
    }
  }

  /**
   * Wire mascot floating dock, Quick Talk flyout, and Presence popover.
   * Floating dock positioned underneath the model's feet.
   */
  _setupMascotToolbar() {
    if (typeof document === "undefined") return;
    if (this._mascotToolbarInitialized) return;
    this._mascotToolbarInitialized = true;
    const get = (id) => document.getElementById(id);

    const toolbar = get("mascot-toolbar");
    const quickTalkBtn = get("mascot-quick-talk-btn");
    const voiceMicBtn = get("mascot-voice-mic-btn");
    const presenceMenuBtn = get("mascot-presence-menu-btn");

    const quickTalkFlyout = get("mascot-quick-talk-flyout");
    const quickTalkClose = get("mascot-quick-talk-close");
    const quickTalkInput = get("mascot-quick-talk-input");
    const quickTalkSendBtn = get("mascot-quick-talk-send-btn");

    const presencePopover = get("mascot-presence-popover");
    const presenceClose = get("mascot-presence-close");
    const appearanceSelect = get("mascot-appearance-select");
    const btnScaleSmall = get("btn-scale-small");
    const btnScaleNormal = get("btn-scale-normal");
    const btnScaleComfort = get("btn-scale-comfort");
    const returnStudioBtn = get("mascot-return-studio-btn");
    const resetBoundsBtn = get("mascot-reset-bounds-btn");

    // Prevent clicks/drags in dock or overlays from bubbling to window drag
    [toolbar, quickTalkFlyout, presencePopover].forEach((el) => {
      if (el) {
        el.addEventListener("click", (e) => e.stopPropagation());
        el.addEventListener("dblclick", (e) => e.stopPropagation());
        el.addEventListener("mousedown", (e) => e.stopPropagation());
      }
    });

    const closeAllOverlays = () => {
      if (quickTalkFlyout) quickTalkFlyout.style.display = "none";
      if (presencePopover) presencePopover.style.display = "none";
      if (quickTalkBtn) quickTalkBtn.classList.remove("active");
      if (presenceMenuBtn) presenceMenuBtn.classList.remove("active");
      if (toolbar) toolbar.classList.remove("has-active-popup");
    };

    this._updateToolbarPosition();

    // --- 1. Quick Talk Speech Bubble Flyout ---
    if (quickTalkBtn && quickTalkFlyout) {
      quickTalkBtn.addEventListener("click", (e) => {
        e.stopPropagation();
        const isOpen = quickTalkFlyout.style.display === "flex" || quickTalkFlyout.style.display === "block";
        closeAllOverlays();
        if (!isOpen) {
          quickTalkFlyout.style.display = "flex";
          quickTalkBtn.classList.add("active");
          if (toolbar) toolbar.classList.add("has-active-popup");
          if (quickTalkInput) {
            setTimeout(() => quickTalkInput.focus(), 50);
          }
        }
      });
    }

    const sendQuickTalk = () => {
      if (!quickTalkInput) return;
      const text = quickTalkInput.value.trim();
      if (!text) return;
      if (window.chatController && typeof window.chatController.sendMessage === "function") {
        window.chatController.sendMessage(text);
      }
      quickTalkInput.value = "";
    };

    if (quickTalkSendBtn) {
      quickTalkSendBtn.addEventListener("click", (e) => {
        e.stopPropagation();
        sendQuickTalk();
      });
    }

    if (quickTalkInput) {
      quickTalkInput.addEventListener("keydown", (e) => {
        if (e.key === "Enter" && !e.shiftKey) {
          e.preventDefault();
          sendQuickTalk();
        }
      });
    }

    if (quickTalkClose) {
      quickTalkClose.addEventListener("click", (e) => {
        e.stopPropagation();
        closeAllOverlays();
      });
    }

    // --- 2. Voice Mic Button (Direct Discord-style toggle) ---
    if (voiceMicBtn) {
      voiceMicBtn.addEventListener("click", (e) => {
        e.stopPropagation();
        const mainMic = get("mic-btn");
        if (mainMic) {
          mainMic.click();
        }
      });
    }

    // --- 3. Presence Menu Popover ---
    if (presenceMenuBtn && presencePopover) {
      presenceMenuBtn.addEventListener("click", (e) => {
        e.stopPropagation();
        const isOpen = presencePopover.style.display === "flex" || presencePopover.style.display === "block";
        closeAllOverlays();
        if (!isOpen) {
          if (appearanceSelect) {
            appearanceSelect.value = this.activeEngine || "canvas";
          }
          ["small", "normal", "comfort"].forEach((k) => {
            const btn = get(`btn-scale-${k}`);
            if (btn) btn.classList.toggle("active", k === this.currentPreset);
          });
          presencePopover.style.display = "flex";
          presenceMenuBtn.classList.add("active");
          if (toolbar) toolbar.classList.add("has-active-popup");
        }
      });
    }

    if (presenceClose) {
      presenceClose.addEventListener("click", (e) => {
        e.stopPropagation();
        closeAllOverlays();
      });
    }

    // Appearance change (strictly renderer/clothing - Invariant 1)
    if (appearanceSelect) {
      appearanceSelect.addEventListener("change", (e) => {
        e.stopPropagation();
        const eng = appearanceSelect.value;
        const mainEngine = get("avatar-engine-select");
        if (mainEngine) {
          mainEngine.value = eng;
          mainEngine.dispatchEvent(new Event("change"));
        }
        localStorage.setItem("lucia_avatar_engine", eng);
        this.setEngine(eng, "default");
      });
    }

    // Segmented Scale Presets (Small 0.75x, Normal 1.00x, Comfort 1.25x)
    [
      { btn: btnScaleSmall, preset: "small" },
      { btn: btnScaleNormal, preset: "normal" },
      { btn: btnScaleComfort, preset: "comfort" },
    ].forEach(({ btn, preset }) => {
      if (btn) {
        btn.addEventListener("click", (e) => {
          e.stopPropagation();
          this.setZoomPreset(preset);
        });
      }
    });

    // Return to Studio action
    if (returnStudioBtn) {
      returnStudioBtn.addEventListener("click", (e) => {
        e.stopPropagation();
        closeAllOverlays();
        if (window.lucia && window.lucia.window && window.lucia.window.toggleMascot) {
          window.lucia.window.toggleMascot();
        }
      });
    }

    // Reset Scale action
    if (resetBoundsBtn) {
      resetBoundsBtn.addEventListener("click", (e) => {
        e.stopPropagation();
        this.pan = { x: 0, y: 0 };
        this.setZoomPreset("normal");
        if (this.activeEngine === "live2d") {
          this._repositionLive2DModel();
        }
        this._updateToolbarPosition();
        if (window.lucia && window.lucia.window && window.lucia.window.resetMascotBounds) {
          window.lucia.window.resetMascotBounds();
        }
        closeAllOverlays();
      });
    }

    // Outside click closes overlays
    window.addEventListener("click", (e) => {
      if (!e.target || typeof e.target.closest !== "function") return;
      if (
        !e.target.closest("#mascot-toolbar") &&
        !e.target.closest("#mascot-quick-talk-flyout") &&
        !e.target.closest("#mascot-presence-popover")
      ) {
        closeAllOverlays();
      }
    });
  }
}

if (typeof window !== "undefined" && window.avatarRegistry) {
  window.avatarRegistry.register("canvas", AvatarRenderer);
}

if (typeof module !== "undefined" && module.exports) {
  module.exports = { AvatarRenderer, MASCOT_PRESETS, MASCOT_PRESET_ORDER };
}
