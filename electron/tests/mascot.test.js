/**
 * @jest-environment jsdom
 */

const { ExpressionMapper } = require("../renderer/avatar/expression-mapper.js");
const { LipSyncProcessor } = require("../renderer/avatar/lip-sync.js");

global.ExpressionMapper = ExpressionMapper;
global.LipSyncProcessor = LipSyncProcessor;

const createMock2DContext = () => ({
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
  closePath: jest.fn(),
  ellipse: jest.fn(),
  fillText: jest.fn(),
  createRadialGradient: jest.fn().mockReturnValue({ addColorStop: jest.fn() }),
  createLinearGradient: jest.fn().mockReturnValue({ addColorStop: jest.fn() })
});

HTMLCanvasElement.prototype.getContext = jest.fn().mockImplementation(createMock2DContext);

describe("Desktop Presence (Mascot Mode) — Phase 7.4 Unit Tests", () => {
  const { AvatarRenderer, MASCOT_PRESETS, MASCOT_PRESET_ORDER } = require("../renderer/avatar/avatar.js");

  const createMockCanvas = () => {
    const canvas = document.createElement("canvas");
    canvas.id = "avatar-canvas";
    canvas.getContext = jest.fn().mockImplementation(createMock2DContext);
    canvas.getBoundingClientRect = jest.fn().mockReturnValue({
      left: 0,
      top: 0,
      width: 380,
      height: 540
    });
    return canvas;
  };

  const setupMascotDOM = () => {
    document.body.className = "mascot-mode";
    document.body.innerHTML = `
      <div class="avatar-stage-container">
        <div class="avatar-stage-viewport">
          <div class="avatar-canvas-wrapper">
            <canvas id="avatar-canvas"></canvas>
            <canvas id="avatar-live2d-canvas" style="display: none;"></canvas>
            <canvas id="avatar-vrm-canvas" style="display: none;"></canvas>
          </div>
        </div>
      </div>
      <div id="mascot-toolbar" class="mascot-toolbar">
        <div id="mascot-quick-talk-flyout" class="mascot-flyout" style="display: none;">
          <button id="mascot-quick-talk-close">✕</button>
          <div id="mascot-quick-talk-latest" style="display: none;">
            <span id="mascot-quick-talk-reply-text"></span>
          </div>
          <textarea id="mascot-quick-talk-input"></textarea>
          <button id="mascot-quick-talk-send-btn">➤</button>
        </div>
        <div id="mascot-presence-popover" class="mascot-popover" style="display: none;">
          <button id="mascot-presence-close">✕</button>
          <select id="mascot-appearance-select">
            <option value="canvas">Canvas</option>
            <option value="sprites">Sprites</option>
            <option value="live2d">Live2D</option>
            <option value="vrm">VRM</option>
          </select>
          <div class="mascot-scale-presets">
            <button id="btn-scale-small" class="scale-preset-btn" data-preset="small">0.75×</button>
            <button id="btn-scale-normal" class="scale-preset-btn active" data-preset="normal">1.00×</button>
            <button id="btn-scale-comfort" class="scale-preset-btn" data-preset="comfort">1.25×</button>
          </div>
          <button id="mascot-return-studio-btn">Return</button>
          <button id="mascot-reset-bounds-btn">Reset</button>
        </div>
        <div class="mascot-toolbar-dock">
          <button id="mascot-quick-talk-btn">Talk</button>
          <button id="mascot-voice-mic-btn">Voice</button>
          <button id="mascot-presence-menu-btn">Menu</button>
        </div>
      </div>
      <button id="mic-btn" style="display:none;"></button>
      <select id="avatar-engine-select" style="display:none;"></select>
    `;
    const canvas = document.getElementById("avatar-canvas");
    if (canvas) {
      canvas.getBoundingClientRect = jest.fn().mockReturnValue({
        left: 0,
        top: 0,
        width: 380,
        height: 540
      });
    }
  };

  let mockWindowIpc;

  beforeEach(() => {
    mockWindowIpc = {
      setIgnoreMouseEvents: jest.fn(),
      setMascotPreset: jest.fn(),
      resetMascotBounds: jest.fn(),
      moveMascotBy: jest.fn(),
      toggleMascot: jest.fn()
    };
    window.lucia = { window: mockWindowIpc };
    window.chatController = {
      sendMessage: jest.fn()
    };
  });

  afterEach(() => {
    document.body.className = "";
    document.body.innerHTML = "";
    jest.clearAllMocks();
  });

  test("discrete presets define small (0.75x), normal (1.00x), and comfort (1.25x)", () => {
    expect(MASCOT_PRESETS.small).toEqual({ key: "small", scale: 0.75, width: 285, height: 405, label: "Small" });
    expect(MASCOT_PRESETS.normal).toEqual({ key: "normal", scale: 1.0, width: 380, height: 540, label: "Normal" });
    expect(MASCOT_PRESETS.comfort).toEqual({ key: "comfort", scale: 1.25, width: 475, height: 675, label: "Comfort" });
    expect(MASCOT_PRESET_ORDER).toEqual(["small", "normal", "comfort"]);
  });

  test("feet-anchor coordinate mathematics preserves bottom-center desktop point", () => {
    const curX = 500;
    const curY = 300;
    const curW = 380;
    const curH = 540;

    // Current bottom-center (feet) coordinate on desktop:
    const feetX = curX + curW / 2; // 500 + 190 = 690
    const feetY = curY + curH;     // 300 + 540 = 840

    // Switch to Comfort (475 x 675)
    const targetW = MASCOT_PRESETS.comfort.width;
    const targetH = MASCOT_PRESETS.comfort.height;
    const newX = Math.round(curX + (curW - targetW) / 2);
    const newY = Math.round(curY + (curH - targetH));

    const newFeetX = newX + targetW / 2;
    const newFeetY = newY + targetH;

    expect(Math.abs(newFeetX - feetX)).toBeLessThanOrEqual(0.5);
    expect(newFeetY).toBe(feetY);

    // Switch to Small (285 x 405)
    const smallW = MASCOT_PRESETS.small.width;
    const smallH = MASCOT_PRESETS.small.height;
    const smallX = Math.round(curX + (curW - smallW) / 2);
    const smallY = Math.round(curY + (curH - smallH));

    expect(Math.abs((smallX + smallW / 2) - feetX)).toBeLessThanOrEqual(0.5);
    expect(smallY + smallH).toBe(feetY);
  });

  test("click-through state machine transitions and prevents IPC flood", () => {
    setupMascotDOM();
    const canvas = document.getElementById("avatar-canvas");
    const renderer = new AvatarRenderer(canvas);

    // Initial state is 0 (PASS_THROUGH). Transitioning to 1 (HOVER_MODEL) captures events
    renderer._setInteractionState(1);
    expect(mockWindowIpc.setIgnoreMouseEvents).toHaveBeenCalledWith(false, { forward: true });

    // Subsequent transition within interactive states (HOVER_MODEL -> HOVER_UI)
    // should NOT trigger IPC again because shouldIgnore remains false!
    mockWindowIpc.setIgnoreMouseEvents.mockClear();
    renderer._setInteractionState(2);
    expect(mockWindowIpc.setIgnoreMouseEvents).not.toHaveBeenCalled();

    // Transition back to PASS_THROUGH (0) enables click-through
    renderer._setInteractionState(0);
    expect(mockWindowIpc.setIgnoreMouseEvents).toHaveBeenCalledWith(true, { forward: true });

    // Repeated call with same state (0) is idempotent and does NOT spam IPC
    mockWindowIpc.setIgnoreMouseEvents.mockClear();
    renderer._setInteractionState(0);
    expect(mockWindowIpc.setIgnoreMouseEvents).not.toHaveBeenCalled();
  });

  test("setZoomPreset updates scale, active CSS class, and invokes IPC", () => {
    setupMascotDOM();
    const canvas = document.getElementById("avatar-canvas");
    const renderer = new AvatarRenderer(canvas);

    renderer.setZoomPreset("comfort");
    expect(renderer.currentPreset).toBe("comfort");
    expect(renderer.mascotScale).toBe(1.25);
    expect(mockWindowIpc.setMascotPreset).toHaveBeenCalledWith("comfort");
    expect(document.getElementById("btn-scale-comfort").classList.contains("active")).toBe(true);
    expect(document.getElementById("btn-scale-normal").classList.contains("active")).toBe(false);

    renderer.setZoomPreset("small");
    expect(renderer.currentPreset).toBe("small");
    expect(renderer.mascotScale).toBe(0.75);
    expect(mockWindowIpc.setMascotPreset).toHaveBeenCalledWith("small");
    expect(document.getElementById("btn-scale-small").classList.contains("active")).toBe(true);
  });

  test("wheel zoom requires Ctrl key and hit-testing on avatar model", () => {
    setupMascotDOM();
    const canvas = document.getElementById("avatar-canvas");
    const renderer = new AvatarRenderer(canvas);
    renderer.width = 380;
    renderer.height = 540;

    // Spy on setZoomPreset
    const setZoomSpy = jest.spyOn(renderer, "setZoomPreset");

    // 1. Wheel WITHOUT ctrlKey must be ignored
    const wheelNoCtrl = new Event("wheel", { bubbles: true, cancelable: true });
    wheelNoCtrl.ctrlKey = false;
    wheelNoCtrl.deltaY = -100;
    wheelNoCtrl.clientX = 190;
    wheelNoCtrl.clientY = 270;
    canvas.dispatchEvent(wheelNoCtrl);
    expect(setZoomSpy).not.toHaveBeenCalled();

    // 2. Wheel with ctrlKey but OUTSIDE model bounds must be ignored
    const wheelOutside = new Event("wheel", { bubbles: true, cancelable: true });
    wheelOutside.ctrlKey = true;
    wheelOutside.deltaY = -100;
    wheelOutside.clientX = 5;
    wheelOutside.clientY = 5;
    canvas.dispatchEvent(wheelOutside);
    expect(setZoomSpy).not.toHaveBeenCalled();

    // 3. Wheel with ctrlKey AND inside model bounds zooms to next preset
    const wheelInside = new Event("wheel", { bubbles: true, cancelable: true });
    wheelInside.ctrlKey = true;
    wheelInside.deltaY = -100; // Zoom in
    wheelInside.clientX = 190;
    wheelInside.clientY = 270;
    canvas.dispatchEvent(wheelInside);
    expect(setZoomSpy).toHaveBeenCalledWith("comfort");
  });

  test("wheel zoom is suppressed during 800ms cooldown after drag", () => {
    setupMascotDOM();
    const canvas = document.getElementById("avatar-canvas");
    const renderer = new AvatarRenderer(canvas);
    renderer.width = 380;
    renderer.height = 540;

    const setZoomSpy = jest.spyOn(renderer, "setZoomPreset");

    // Simulate drag completion 200ms ago
    renderer.lastWindowDragEndTime = Date.now() - 200;

    const wheelInside = new Event("wheel", { bubbles: true, cancelable: true });
    wheelInside.ctrlKey = true;
    wheelInside.deltaY = -100;
    wheelInside.clientX = 190;
    wheelInside.clientY = 270;
    canvas.dispatchEvent(wheelInside);

    expect(setZoomSpy).not.toHaveBeenCalled();
  });

  test("double-click resets pan, scale, overlays, and calls resetMascotBounds", () => {
    setupMascotDOM();
    const canvas = document.getElementById("avatar-canvas");
    const renderer = new AvatarRenderer(canvas);
    renderer.width = 380;
    renderer.height = 540;
    renderer.pan = { x: 50, y: -40 };
    renderer.setZoomPreset("comfort");

    // Open an overlay
    const flyout = document.getElementById("mascot-quick-talk-flyout");
    flyout.style.display = "flex";

    // Double-click over avatar model
    const dblClick = new MouseEvent("dblclick", {
      bubbles: true,
      cancelable: true,
      clientX: 190,
      clientY: 270
    });
    canvas.dispatchEvent(dblClick);

    expect(renderer.pan.x).toBe(0);
    expect(renderer.pan.y).toBe(0);
    expect(renderer.currentPreset).toBe("normal");
    expect(renderer.mascotScale).toBe(1.0);
    expect(flyout.style.display).toBe("none");
    expect(mockWindowIpc.resetMascotBounds).toHaveBeenCalled();
  });

  test("double-click outside avatar does NOT reset bounds", () => {
    setupMascotDOM();
    const canvas = document.getElementById("avatar-canvas");
    const renderer = new AvatarRenderer(canvas);
    renderer.width = 380;
    renderer.height = 540;
    renderer.pan = { x: 50, y: -40 };

    const dblClickOutside = new MouseEvent("dblclick", {
      bubbles: true,
      cancelable: true,
      clientX: 5,
      clientY: 5
    });
    canvas.dispatchEvent(dblClickOutside);

    expect(renderer.pan.x).toBe(50);
    expect(mockWindowIpc.resetMascotBounds).not.toHaveBeenCalled();
  });

  test("Quick Talk flyout toggles, sends messages, and isolates clicks", () => {
    setupMascotDOM();
    const canvas = document.getElementById("avatar-canvas");
    const renderer = new AvatarRenderer(canvas);
    renderer._setupMascotToolbar();

    const quickTalkBtn = document.getElementById("mascot-quick-talk-btn");
    const flyout = document.getElementById("mascot-quick-talk-flyout");
    const input = document.getElementById("mascot-quick-talk-input");
    const sendBtn = document.getElementById("mascot-quick-talk-send-btn");

    expect(flyout.style.display).toBe("none");

    // Open flyout
    quickTalkBtn.click();
    expect(flyout.style.display).toBe("flex");
    expect(quickTalkBtn.classList.contains("active")).toBe(true);

    // Enter message and click send
    input.value = "Hello Lucia";
    sendBtn.click();
    expect(window.chatController.sendMessage).toHaveBeenCalledWith("Hello Lucia");
    expect(input.value).toBe("");

    // Enter with Return key
    input.value = "How are you?";
    input.dispatchEvent(new KeyboardEvent("keydown", { key: "Enter", bubbles: true }));
    expect(window.chatController.sendMessage).toHaveBeenCalledWith("How are you?");
    expect(input.value).toBe("");

    // Close flyout via close button
    const closeBtn = document.getElementById("mascot-quick-talk-close");
    closeBtn.click();
    expect(flyout.style.display).toBe("none");
    expect(quickTalkBtn.classList.contains("active")).toBe(false);
  });

  test("Presence Menu popover toggles appearance and scale presets", () => {
    setupMascotDOM();
    const canvas = document.getElementById("avatar-canvas");
    const renderer = new AvatarRenderer(canvas);
    renderer._setupMascotToolbar();

    const menuBtn = document.getElementById("mascot-presence-menu-btn");
    const popover = document.getElementById("mascot-presence-popover");
    const appearanceSelect = document.getElementById("mascot-appearance-select");
    const btnScaleSmall = document.getElementById("btn-scale-small");

    // Open popover
    menuBtn.click();
    expect(popover.style.display).toBe("flex");
    expect(menuBtn.classList.contains("active")).toBe(true);

    // Change appearance (strictly visual presentation - Invariant 1)
    const setEngineSpy = jest.spyOn(renderer, "setEngine");
    appearanceSelect.value = "sprites";
    appearanceSelect.dispatchEvent(new Event("change"));
    expect(setEngineSpy).toHaveBeenCalledWith("sprites", "default");

    // Click scale preset
    btnScaleSmall.click();
    expect(renderer.currentPreset).toBe("small");
    expect(mockWindowIpc.setMascotPreset).toHaveBeenCalledWith("small");
  });

  test("Voice mic button clicks main mic button for seamless voice", () => {
    setupMascotDOM();
    const canvas = document.getElementById("avatar-canvas");
    const renderer = new AvatarRenderer(canvas);
    renderer._setupMascotToolbar();

    const mainMic = document.getElementById("mic-btn");
    mainMic.click = jest.fn();

    const mascotMic = document.getElementById("mascot-voice-mic-btn");
    mascotMic.click();

    expect(mainMic.click).toHaveBeenCalled();
  });

  test("left-click dragging in mascot mode only calls moveMascotBy and leaves model pan=(0,0) and mascotScale unchanged", () => {
    setupMascotDOM();
    const canvas = document.getElementById("avatar-canvas");
    const renderer = new AvatarRenderer(canvas);
    renderer.width = 380;
    renderer.height = 540;
    renderer.mascotScale = 1.0;
    renderer.pan = { x: 0, y: 0 };

    // Initial mousedown (button 0, no shift)
    const mouseDown = new MouseEvent("mousedown", {
      bubbles: true,
      cancelable: true,
      button: 0,
      clientX: 190,
      clientY: 270,
      screenX: 100,
      screenY: 200
    });
    canvas.dispatchEvent(mouseDown);

    expect(renderer.isDraggingWindow).toBe(true);
    expect(renderer.isDraggingModel).toBe(false);

    // Mousemove drag
    const mouseMove = new MouseEvent("mousemove", {
      bubbles: true,
      cancelable: true,
      clientX: 230,
      clientY: 290,
      screenX: 140,
      screenY: 220
    });
    window.dispatchEvent(mouseMove);

    expect(mockWindowIpc.moveMascotBy).toHaveBeenCalledWith(40, 20);
    expect(renderer.pan.x).toBe(0);
    expect(renderer.pan.y).toBe(0);
    expect(renderer.mascotScale).toBe(1.0);

    // Mouseup
    const mouseUp = new MouseEvent("mouseup", { bubbles: true, cancelable: true });
    window.dispatchEvent(mouseUp);

    expect(renderer.isDraggingWindow).toBe(false);
    expect(renderer.isDraggingModel).toBe(false);
  });

  test("shift+click or middle-click in mascot mode does not initiate model pan", () => {
    setupMascotDOM();
    const canvas = document.getElementById("avatar-canvas");
    const renderer = new AvatarRenderer(canvas);
    renderer.width = 380;
    renderer.height = 540;
    renderer.pan = { x: 0, y: 0 };

    // Shift + Left Click
    const shiftClick = new MouseEvent("mousedown", {
      bubbles: true,
      cancelable: true,
      button: 0,
      shiftKey: true,
      clientX: 190,
      clientY: 270
    });
    canvas.dispatchEvent(shiftClick);

    expect(renderer.isDraggingModel).toBe(false);
    expect(renderer.isDraggingWindow).toBe(true);
    expect(renderer.pan.x).toBe(0);
    expect(renderer.pan.y).toBe(0);

    // Reset drag
    renderer.isDraggingWindow = false;

    // Middle Click
    const middleClick = new MouseEvent("mousedown", {
      bubbles: true,
      cancelable: true,
      button: 1,
      clientX: 190,
      clientY: 270
    });
    canvas.dispatchEvent(middleClick);

    expect(renderer.isDraggingModel).toBe(false);
    expect(renderer.isDraggingWindow).toBe(false);
    expect(renderer.pan.x).toBe(0);
    expect(renderer.pan.y).toBe(0);
  });

  test("Return to Studio button calls toggleMascot and closes popover", () => {
    setupMascotDOM();
    const canvas = document.getElementById("avatar-canvas");
    const renderer = new AvatarRenderer(canvas);
    renderer._setupMascotToolbar();

    const returnBtn = document.getElementById("mascot-return-studio-btn");
    const popover = document.getElementById("mascot-presence-popover");
    popover.style.display = "flex";

    returnBtn.click();

    expect(mockWindowIpc.toggleMascot).toHaveBeenCalled();
    expect(popover.style.display).toBe("none");
  });

  test("Reset Scale button resets zoom preset to normal, resets bounds, and closes popover", () => {
    setupMascotDOM();
    const canvas = document.getElementById("avatar-canvas");
    const renderer = new AvatarRenderer(canvas);
    renderer.setZoomPreset("comfort");
    renderer._setupMascotToolbar();

    const resetBtn = document.getElementById("mascot-reset-bounds-btn");
    const popover = document.getElementById("mascot-presence-popover");
    popover.style.display = "flex";

    resetBtn.click();

    expect(renderer.currentPreset).toBe("normal");
    expect(renderer.pan.x).toBe(0);
    expect(renderer.pan.y).toBe(0);
    expect(mockWindowIpc.resetMascotBounds).toHaveBeenCalled();
    expect(popover.style.display).toBe("none");
  });
});

describe("Desktop Presence — Dual-Layer Dimension Clamping & Drag Invariant Regressions", () => {
  const {
    MASCOT_CANONICAL_PRESETS,
    getMascotPreset,
    syncMascotWindowPreset
  } = require("../main/mascot-constants.js");

  /**
   * Simulates main-process window state under Windows high-DPI scaling.
   */
  function createMockMascotWindow(initialPreset = "normal", dpiScale = 1.25) {
    const preset = getMascotPreset(initialPreset);
    let currentX = 500;
    let currentY = 300;
    let currentW = preset.width;
    let currentH = preset.height;
    let isMax = false;

    const win = {
      _mascotPreset: preset.key,
      _mascotTargetWidth: preset.width,
      _mascotTargetHeight: preset.height,
      isMaximized: jest.fn(() => isMax),
      unmaximize: jest.fn(() => { isMax = false; }),
      getPosition: jest.fn(() => [currentX, currentY]),
      // Windows DWM high-DPI subpixel behavior: getSize returns DIP rounded by DWM
      // For instance at 125% DPI, subpixel boundaries round up (+1px)
      getSize: jest.fn(() => {
        const jitter = dpiScale > 1.0 ? 1 : 0;
        return [currentW + jitter, currentH + jitter];
      }),
      setBounds: jest.fn((bounds) => {
        if (bounds.x !== undefined) currentX = bounds.x;
        if (bounds.y !== undefined) currentY = bounds.y;
        if (bounds.width !== undefined) currentW = bounds.width;
        if (bounds.height !== undefined) currentH = bounds.height;
      }),
      getInternalState: () => ({ x: currentX, y: currentY, w: currentW, h: currentH })
    };

    return win;
  }

  function handleMoveMascotBy(win, { dx, dy }) {
    if (win.isMaximized()) win.unmaximize();
    const [x, y] = win.getPosition();
    const canonical = syncMascotWindowPreset(win, win._mascotPreset);
    win.setBounds({
      x: Math.round(x + (dx || 0)),
      y: Math.round(y + (dy || 0)),
      width: canonical.width,
      height: canonical.height
    });
    return true;
  }

  function handleSetMascotPreset(win, { preset }) {
    if (win.isMaximized()) win.unmaximize();
    const [curX, curY] = win.getPosition();
    const prevCanonical = getMascotPreset(win._mascotPreset);
    const curW = win._mascotTargetWidth || prevCanonical.width;
    const curH = win._mascotTargetHeight || prevCanonical.height;

    const target = syncMascotWindowPreset(win, preset);
    const newX = Math.round(curX + (curW - target.width) / 2);
    const newY = Math.round(curY + (curH - target.height));
    win.setBounds({ x: newX, y: newY, width: target.width, height: target.height });
    return { preset: target.key, width: target.width, height: target.height, x: newX, y: newY };
  }

  function handleResetMascotBounds(win) {
    if (win.isMaximized()) win.unmaximize();
    const [curX, curY] = win.getPosition();
    const prevCanonical = getMascotPreset(win._mascotPreset);
    const curW = win._mascotTargetWidth || prevCanonical.width;
    const curH = win._mascotTargetHeight || prevCanonical.height;

    const canonical = syncMascotWindowPreset(win, 'normal');
    const newX = Math.round(curX + (curW - canonical.width) / 2);
    const newY = Math.round(curY + (curH - canonical.height));
    win.setBounds({ x: newX, y: newY, width: canonical.width, height: canonical.height });
    return true;
  }

  let mockWindowIpc;

  beforeEach(() => {
    mockWindowIpc = {
      setIgnoreMouseEvents: jest.fn(),
      setMascotPreset: jest.fn(),
      resetMascotBounds: jest.fn(),
      moveMascotBy: jest.fn(),
      toggleMascot: jest.fn()
    };
    window.lucia = { window: mockWindowIpc };
  });

  const setupMascotDOM = () => {
    document.body.className = "mascot-mode";
    document.body.innerHTML = `
      <div class="avatar-stage-container">
        <div class="avatar-stage-viewport">
          <div class="avatar-canvas-wrapper">
            <canvas id="avatar-canvas"></canvas>
            <canvas id="avatar-live2d-canvas" style="display: none;"></canvas>
            <canvas id="avatar-vrm-canvas" style="display: none;"></canvas>
          </div>
        </div>
      </div>
      <div id="mascot-toolbar" class="mascot-toolbar">
        <div id="mascot-quick-talk-flyout" class="mascot-flyout" style="display: none;">
          <button id="mascot-quick-talk-close">✕</button>
          <div id="mascot-quick-talk-latest" style="display: none;">
            <span id="mascot-quick-talk-reply-text"></span>
          </div>
          <textarea id="mascot-quick-talk-input"></textarea>
          <button id="mascot-quick-talk-send-btn">➤</button>
        </div>
        <div id="mascot-presence-popover" class="mascot-popover" style="display: none;">
          <button id="mascot-presence-close">✕</button>
          <select id="mascot-appearance-select">
            <option value="canvas">Canvas</option>
            <option value="sprites">Sprites</option>
            <option value="live2d">Live2D</option>
            <option value="vrm">VRM</option>
          </select>
          <div class="mascot-scale-presets">
            <button id="btn-scale-small" class="scale-preset-btn" data-preset="small">0.75×</button>
            <button id="btn-scale-normal" class="scale-preset-btn active" data-preset="normal">1.00×</button>
            <button id="btn-scale-comfort" class="scale-preset-btn" data-preset="comfort">1.25×</button>
          </div>
          <button id="mascot-return-studio-btn">Return</button>
          <button id="mascot-reset-bounds-btn">Reset</button>
        </div>
        <div class="mascot-toolbar-dock">
          <button id="mascot-quick-talk-btn">Talk</button>
          <button id="mascot-voice-mic-btn">Voice</button>
          <button id="mascot-presence-menu-btn">Menu</button>
        </div>
      </div>
      <button id="mic-btn" style="display:none;"></button>
      <select id="avatar-engine-select" style="display:none;"></select>
    `;
    const canvas = document.getElementById("avatar-canvas");
    if (canvas) {
      canvas.getBoundingClientRect = jest.fn().mockReturnValue({
        left: 0,
        top: 0,
        width: 380,
        height: 540
      });
    }
  };

  test("Regression 1: continuous drag at 125% DPI maintains strictly constant dimensions without runaway expansion", () => {
    const win = createMockMascotWindow("normal", 1.25);
    setupMascotDOM();
    const canvas = document.getElementById("avatar-canvas");
    const { AvatarRenderer } = require("../renderer/avatar/avatar.js");
    const renderer = new AvatarRenderer(canvas);
    renderer.setZoomPreset("normal");

    // 50 continuous drag steps
    const recordedDims = [];
    for (let i = 1; i <= 50; i++) {
      handleMoveMascotBy(win, { dx: 3, dy: 2 });
      const state = win.getInternalState();
      recordedDims.push({ w: state.w, h: state.h });
      expect(state.w).toBe(380);
      expect(state.h).toBe(540);
      expect(win._mascotTargetWidth).toBe(380);
      expect(win._mascotTargetHeight).toBe(540);
      expect(win._mascotPreset).toBe("normal");
    }

    // Ensure all 50 steps recorded exactly 380x540
    expect(recordedDims.every(d => d.w === 380 && d.h === 540)).toBe(true);
    // Position must have incremented by 50 * 3 = 150, 50 * 2 = 100
    expect(win.getInternalState().x).toBe(500 + 150);
    expect(win.getInternalState().y).toBe(300 + 100);
  });

  test("Regression 2: drag -> preset change -> drag maintains exact dimensions across small, normal, and comfort", () => {
    const win = createMockMascotWindow("normal", 1.25);
    setupMascotDOM();
    const canvas = document.getElementById("avatar-canvas");
    const { AvatarRenderer } = require("../renderer/avatar/avatar.js");
    const renderer = new AvatarRenderer(canvas);
    renderer.setZoomPreset("normal");

    // Phase A: Drag in normal
    for (let i = 0; i < 10; i++) {
      handleMoveMascotBy(win, { dx: 2, dy: 1 });
    }
    expect(win.getInternalState().w).toBe(380);
    expect(win.getInternalState().h).toBe(540);

    // Phase B: Preset change to comfort
    handleSetMascotPreset(win, { preset: "comfort" });
    renderer.setZoomPreset("comfort");
    expect(win.getInternalState().w).toBe(475);
    expect(win.getInternalState().h).toBe(675);
    expect(win._mascotPreset).toBe("comfort");
    expect(win._mascotTargetWidth).toBe(475);
    expect(win._mascotTargetHeight).toBe(675);
    expect(renderer.width).toBe(475);
    expect(renderer.height).toBe(675);
    expect(renderer.mascotScale).toBe(1.25);

    // Phase C: Drag in comfort
    for (let i = 0; i < 10; i++) {
      handleMoveMascotBy(win, { dx: -1, dy: 3 });
      expect(win.getInternalState().w).toBe(475);
      expect(win.getInternalState().h).toBe(675);
    }
    expect(renderer.width).toBe(475);
    expect(renderer.height).toBe(675);
    expect(renderer.pan).toEqual({ x: 0, y: 0 });

    // Phase D: Preset change to small
    handleSetMascotPreset(win, { preset: "small" });
    renderer.setZoomPreset("small");
    expect(win.getInternalState().w).toBe(285);
    expect(win.getInternalState().h).toBe(405);
    expect(win._mascotPreset).toBe("small");
    expect(renderer.width).toBe(285);
    expect(renderer.height).toBe(405);
    expect(renderer.mascotScale).toBe(0.75);

    // Phase E: Drag in small
    for (let i = 0; i < 10; i++) {
      handleMoveMascotBy(win, { dx: 1, dy: -2 });
      expect(win.getInternalState().w).toBe(285);
      expect(win.getInternalState().h).toBe(405);
    }
  });

  test("Regression 3: drag -> reset scale -> drag cleanly resets to canonical normal (380x540) without divergence", () => {
    const win = createMockMascotWindow("comfort", 1.25);
    setupMascotDOM();
    const canvas = document.getElementById("avatar-canvas");
    const { AvatarRenderer } = require("../renderer/avatar/avatar.js");
    const renderer = new AvatarRenderer(canvas);
    renderer.setZoomPreset("comfort");

    // Phase A: Drag in comfort
    for (let i = 0; i < 10; i++) {
      handleMoveMascotBy(win, { dx: 2, dy: 2 });
    }
    expect(win.getInternalState().w).toBe(475);
    expect(win.getInternalState().h).toBe(675);

    // Phase B: Reset Scale
    handleResetMascotBounds(win);
    renderer.setZoomPreset("normal");
    renderer.pan = { x: 0, y: 0 };

    expect(win.getInternalState().w).toBe(380);
    expect(win.getInternalState().h).toBe(540);
    expect(win._mascotPreset).toBe("normal");
    expect(win._mascotTargetWidth).toBe(380);
    expect(win._mascotTargetHeight).toBe(540);
    expect(renderer.currentPreset).toBe("normal");
    expect(renderer.width).toBe(380);
    expect(renderer.height).toBe(540);
    expect(renderer.mascotScale).toBe(1.0);
    expect(renderer.pan).toEqual({ x: 0, y: 0 });

    // Phase C: Drag after reset
    for (let i = 0; i < 15; i++) {
      handleMoveMascotBy(win, { dx: -2, dy: 1 });
      expect(win.getInternalState().w).toBe(380);
      expect(win.getInternalState().h).toBe(540);
      expect(win._mascotTargetWidth).toBe(380);
      expect(win._mascotTargetHeight).toBe(540);
    }
  });

  test("Regression 4: all three presets maintain exact canonical dimensions and metadata during dragging", () => {
    const presets = ["small", "normal", "comfort"];
    setupMascotDOM();
    const canvas = document.getElementById("avatar-canvas");
    const { AvatarRenderer } = require("../renderer/avatar/avatar.js");
    const renderer = new AvatarRenderer(canvas);

    for (const p of presets) {
      const canonical = MASCOT_CANONICAL_PRESETS[p];
      const win = createMockMascotWindow(p, 1.25);
      renderer.setZoomPreset(p);

      expect(win._mascotPreset).toBe(p);
      expect(win._mascotTargetWidth).toBe(canonical.width);
      expect(win._mascotTargetHeight).toBe(canonical.height);
      expect(renderer.width).toBe(canonical.width);
      expect(renderer.height).toBe(canonical.height);
      expect(renderer.mascotScale).toBe(canonical.scale);

      for (let step = 0; step < 20; step++) {
        handleMoveMascotBy(win, { dx: 4, dy: -3 });
        const state = win.getInternalState();
        expect(state.w).toBe(canonical.width);
        expect(state.h).toBe(canonical.height);
        expect(win._mascotTargetWidth).toBe(canonical.width);
        expect(win._mascotTargetHeight).toBe(canonical.height);
        expect(win._mascotPreset).toBe(p);
        expect(renderer.width).toBe(canonical.width);
        expect(renderer.height).toBe(canonical.height);
        expect(renderer.mascotScale).toBe(canonical.scale);
        expect(renderer.pan).toEqual({ x: 0, y: 0 });
      }
    }
  });

  test("Regression 5: drag changes only window position and never dimensions, renderer scale, pan, or canvas transform", () => {
    setupMascotDOM();
    const canvas = document.getElementById("avatar-canvas");
    const { AvatarRenderer } = require("../renderer/avatar/avatar.js");
    const renderer = new AvatarRenderer(canvas);
    renderer.setZoomPreset("normal");
    const mockCtx = renderer.ctx;

    // Track initial values
    const initialPos = { x: 500, y: 300 };
    const win = createMockMascotWindow("normal", 1.25);
    win.setBounds(initialPos);

    mockWindowIpc.moveMascotBy.mockImplementation((dx, dy) => {
      handleMoveMascotBy(win, { dx, dy });
    });

    const initialRendererWidth = renderer.width; // 380
    const initialRendererHeight = renderer.height; // 540
    const initialMascotScale = renderer.mascotScale; // 1.0
    const initialPan = { ...renderer.pan }; // { x: 0, y: 0 }

    // Start drag gesture
    canvas.dispatchEvent(new MouseEvent("mousedown", {
      bubbles: true,
      cancelable: true,
      button: 0,
      clientX: 190,
      clientY: 270,
      screenX: 690,
      screenY: 570
    }));
    expect(renderer.isDraggingWindow).toBe(true);
    expect(renderer.isDraggingModel).toBe(false);

    // Multi-directional drag trajectory: Right (+50), Down (+30), Left (-20), Up (-10)
    const trajectory = [
      { screenX: 740, screenY: 570, expectedDx: 50, expectedDy: 0 },
      { screenX: 740, screenY: 600, expectedDx: 0, expectedDy: 30 },
      { screenX: 720, screenY: 600, expectedDx: -20, expectedDy: 0 },
      { screenX: 720, screenY: 590, expectedDx: 0, expectedDy: -10 }
    ];

    trajectory.forEach(pt => {
      window.dispatchEvent(new MouseEvent("mousemove", {
        bubbles: true,
        cancelable: true,
        clientX: 190,
        clientY: 270,
        screenX: pt.screenX,
        screenY: pt.screenY
      }));
    });

    // Render frame during drag to verify transform
    mockCtx.setTransform.mockClear();
    renderer._render(Date.now());

    // End drag gesture
    window.dispatchEvent(new MouseEvent("mouseup", { bubbles: true, cancelable: true }));
    expect(renderer.isDraggingWindow).toBe(false);

    // Assert: Window position changed by cumulative delta (+30, +20)
    const finalState = win.getInternalState();
    expect(finalState.x).toBe(initialPos.x + 30);
    expect(finalState.y).toBe(initialPos.y + 20);

    // Assert: Window dimensions changed by 0
    expect(finalState.w).toBe(initialRendererWidth);
    expect(finalState.h).toBe(initialRendererHeight);

    // Assert: Renderer dimensions unchanged
    expect(renderer.width).toBe(initialRendererWidth);
    expect(renderer.height).toBe(initialRendererHeight);

    // Assert: Renderer scale unchanged
    expect(renderer.mascotScale).toBe(initialMascotScale);

    // Assert: Model pan strictly unchanged at (0, 0)
    expect(renderer.pan).toEqual(initialPan);

    // Assert: Canvas setTransform called only with standard identity/DPR factors, no scale accumulation
    expect(mockCtx.setTransform).toHaveBeenCalledWith(1, 0, 0, 1, 0, 0);

    renderer.destroy();
  });
});
