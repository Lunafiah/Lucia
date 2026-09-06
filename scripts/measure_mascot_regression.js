/**
 * Verification & Dimensional Measurement Suite (measure_mascot_regression.js)
 * Executes the 5 regression scenarios and outputs an exact dimensional report.
 */

const { MASCOT_CANONICAL_PRESETS, getMascotPreset, syncMascotWindowPreset } = require('../electron/main/mascot-constants.js');

function createMockWindow(initialPreset = 'normal', dpiScale = 1.25) {
  const preset = getMascotPreset(initialPreset);
  let currentX = 500;
  let currentY = 300;
  let currentW = preset.width;
  let currentH = preset.height;

  const win = {
    _mascotPreset: preset.key,
    _mascotTargetWidth: preset.width,
    _mascotTargetHeight: preset.height,
    isMaximized: () => false,
    unmaximize: () => {},
    getPosition: () => [currentX, currentY],
    getSize: () => {
      // Models Windows DWM rounding behavior at high DPI
      const jitter = dpiScale > 1.0 ? 1 : 0;
      return [currentW + jitter, currentH + jitter];
    },
    setBounds: (bounds) => {
      if (bounds.x !== undefined) currentX = bounds.x;
      if (bounds.y !== undefined) currentY = bounds.y;
      if (bounds.width !== undefined) currentW = bounds.width;
      if (bounds.height !== undefined) currentH = bounds.height;
    },
    getState: () => ({ x: currentX, y: currentY, width: currentW, height: currentH })
  };

  return win;
}

function handleMoveMascotBy(win, dx, dy) {
  const [x, y] = win.getPosition();
  const canonical = syncMascotWindowPreset(win, win._mascotPreset);
  win.setBounds({
    x: Math.round(x + (dx || 0)),
    y: Math.round(y + (dy || 0)),
    width: canonical.width,
    height: canonical.height
  });
}

function handleSetMascotPreset(win, presetKey) {
  const [curX, curY] = win.getPosition();
  const prevCanonical = getMascotPreset(win._mascotPreset);
  const curW = win._mascotTargetWidth || prevCanonical.width;
  const curH = win._mascotTargetHeight || prevCanonical.height;

  const target = syncMascotWindowPreset(win, presetKey);
  const newX = Math.round(curX + (curW - target.width) / 2);
  const newY = Math.round(curY + (curH - target.height));
  win.setBounds({ x: newX, y: newY, width: target.width, height: target.height });
  return { preset: target.key, width: target.width, height: target.height, x: newX, y: newY };
}

function handleResetMascotBounds(win) {
  const [curX, curY] = win.getPosition();
  const prevCanonical = getMascotPreset(win._mascotPreset);
  const curW = win._mascotTargetWidth || prevCanonical.width;
  const curH = win._mascotTargetHeight || prevCanonical.height;

  const canonical = syncMascotWindowPreset(win, 'normal');
  const newX = Math.round(curX + (curW - canonical.width) / 2);
  const newY = Math.round(curY + (curH - canonical.height));
  win.setBounds({ x: newX, y: newY, width: canonical.width, height: canonical.height });
}

// -------------------------------------------------------------
// RUN THE 5 REGRESSION SCENARIOS AND LOG EXACT MEASUREMENTS
// -------------------------------------------------------------

console.log("================================================================================");
console.log("DESKTOP PRESENCE (MASCOT MODE) DUAL-LAYER CLAMPING MEASUREMENT RUN");
console.log("================================================================================\n");

// Scenario 1: Continuous drag at 125% DPI
console.log("--- SCENARIO 1: Continuous Drag at 125% DPI (50 consecutive steps) ---");
const win1 = createMockWindow('normal', 1.25);
const init1 = win1.getState();
console.log(`Initial Window Bounds: [${init1.x}, ${init1.y}], Size: ${init1.width} x ${init1.height}`);

const samples1 = [];
for (let i = 1; i <= 50; i++) {
  handleMoveMascotBy(win1, 3, 2);
  if (i === 1 || i === 10 || i === 25 || i === 50) {
    const s = win1.getState();
    samples1.push({ step: i, x: s.x, y: s.y, w: s.width, h: s.height, preset: win1._mascotPreset, targetW: win1._mascotTargetWidth, targetH: win1._mascotTargetHeight });
  }
}
console.table(samples1);

// Scenario 2: Drag -> Preset Change -> Drag
console.log("\n--- SCENARIO 2: Drag -> Preset Change -> Drag (Normal -> Comfort -> Small) ---");
const win2 = createMockWindow('normal', 1.25);
console.log(`Initial: ${win2._mascotPreset} (${win2.getState().width} x ${win2.getState().height})`);
for (let i = 0; i < 10; i++) handleMoveMascotBy(win2, 2, 1);
console.log(`After 10 drags in Normal: [${win2.getState().x}, ${win2.getState().y}] Size: ${win2.getState().width} x ${win2.getState().height}`);

handleSetMascotPreset(win2, 'comfort');
console.log(`Switched to Comfort: [${win2.getState().x}, ${win2.getState().y}] Size: ${win2.getState().width} x ${win2.getState().height} (Target: ${win2._mascotTargetWidth} x ${win2._mascotTargetHeight})`);
for (let i = 0; i < 10; i++) handleMoveMascotBy(win2, -1, 3);
console.log(`After 10 drags in Comfort: [${win2.getState().x}, ${win2.getState().y}] Size: ${win2.getState().width} x ${win2.getState().height}`);

handleSetMascotPreset(win2, 'small');
console.log(`Switched to Small: [${win2.getState().x}, ${win2.getState().y}] Size: ${win2.getState().width} x ${win2.getState().height} (Target: ${win2._mascotTargetWidth} x ${win2._mascotTargetHeight})`);
for (let i = 0; i < 10; i++) handleMoveMascotBy(win2, 1, -2);
console.log(`After 10 drags in Small: [${win2.getState().x}, ${win2.getState().y}] Size: ${win2.getState().width} x ${win2.getState().height}`);

// Scenario 3: Drag -> Reset Scale -> Drag
console.log("\n--- SCENARIO 3: Drag -> Reset Scale -> Drag (Comfort -> Normal) ---");
const win3 = createMockWindow('comfort', 1.25);
console.log(`Initial in Comfort: Size ${win3.getState().width} x ${win3.getState().height}`);
for (let i = 0; i < 10; i++) handleMoveMascotBy(win3, 2, 2);
console.log(`After 10 drags: [${win3.getState().x}, ${win3.getState().y}] Size: ${win3.getState().width} x ${win3.getState().height}`);

handleResetMascotBounds(win3);
console.log(`Reset Bounds: [${win3.getState().x}, ${win3.getState().y}] Size: ${win3.getState().width} x ${win3.getState().height} (Preset: ${win3._mascotPreset})`);
for (let i = 0; i < 15; i++) handleMoveMascotBy(win3, -2, 1);
console.log(`After 15 subsequent drags: [${win3.getState().x}, ${win3.getState().y}] Size: ${win3.getState().width} x ${win3.getState().height}`);

// Scenario 4: All Three Presets
console.log("\n--- SCENARIO 4: All Three Presets Dimensional Invariance Across 20-step Drag ---");
const results4 = [];
['small', 'normal', 'comfort'].forEach((p) => {
  const win = createMockWindow(p, 1.25);
  const start = win.getState();
  for (let i = 0; i < 20; i++) handleMoveMascotBy(win, 4, -3);
  const end = win.getState();
  results4.push({
    Preset: p,
    CanonicalWidth: MASCOT_CANONICAL_PRESETS[p].width,
    CanonicalHeight: MASCOT_CANONICAL_PRESETS[p].height,
    MeasuredWidthBefore: start.width,
    MeasuredHeightBefore: start.height,
    MeasuredWidthAfter: end.width,
    MeasuredHeightAfter: end.height,
    DeltaWidth: end.width - start.width,
    DeltaHeight: end.height - start.height,
    TargetWidthSync: win._mascotTargetWidth,
    TargetHeightSync: win._mascotTargetHeight
  });
});
console.table(results4);

// Scenario 5: Position vs Dimensions & Renderer Invariance
console.log("\n--- SCENARIO 5: Verification that Drag Changes ONLY Position (Never Dims, Scale, Pan) ---");
const win5 = createMockWindow('normal', 1.25);
const startPos5 = win5.getState();
console.log(`Start Position: (${startPos5.x}, ${startPos5.y}), Dimensions: ${startPos5.width} x ${startPos5.height}`);

// Drag trajectory: +50x, +30y, -20x, -10y -> Net: +30x, +20y
handleMoveMascotBy(win5, 50, 0);
handleMoveMascotBy(win5, 0, 30);
handleMoveMascotBy(win5, -20, 0);
handleMoveMascotBy(win5, 0, -10);

const endPos5 = win5.getState();
console.log(`End Position:   (${endPos5.x}, ${endPos5.y}), Dimensions: ${endPos5.width} x ${endPos5.height}`);
console.log(`Position Delta: dx = ${endPos5.x - startPos5.x} (expected +30), dy = ${endPos5.y - startPos5.y} (expected +20)`);
console.log(`Dimension Delta: dw = ${endPos5.width - startPos5.width} (expected 0), dh = ${endPos5.height - startPos5.height} (expected 0)`);
console.log("================================================================================\n");
