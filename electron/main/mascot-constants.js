/**
 * Canonical Mascot Presets & Window Synchronization (mascot-constants.js)
 * Single source of truth for Desktop Presence / Mascot Mode dimensions and scaling.
 */

const MASCOT_CANONICAL_PRESETS = Object.freeze({
  small: Object.freeze({
    key: 'small',
    width: 285,
    height: 405,
    scale: 0.75,
    label: 'Small'
  }),
  normal: Object.freeze({
    key: 'normal',
    width: 380,
    height: 540,
    scale: 1.0,
    label: 'Normal'
  }),
  comfort: Object.freeze({
    key: 'comfort',
    width: 475,
    height: 675,
    scale: 1.25,
    label: 'Comfort'
  })
});

const MASCOT_PRESET_KEYS = Object.freeze(['small', 'normal', 'comfort']);

/**
 * Returns canonical preset object, safely defaulting to 'normal'.
 * @param {string} [key]
 * @returns {{ key: string, width: number, height: number, scale: number, label: string }}
 */
function getMascotPreset(key) {
  if (key && MASCOT_CANONICAL_PRESETS[key]) {
    return MASCOT_CANONICAL_PRESETS[key];
  }
  return MASCOT_CANONICAL_PRESETS.normal;
}

/**
 * Synchronizes window instance mascot metadata to canonical preset values.
 * Guarantees _mascotPreset, _mascotTargetWidth, and _mascotTargetHeight never diverge or become stale.
 * @param {import('electron').BrowserWindow} win
 * @param {string} [presetKey]
 * @returns {{ key: string, width: number, height: number, scale: number, label: string }}
 */
function syncMascotWindowPreset(win, presetKey) {
  const resolvedKey = presetKey || (win && win._mascotPreset) || 'normal';
  const canonical = getMascotPreset(resolvedKey);
  if (win) {
    win._mascotPreset = canonical.key;
    win._mascotTargetWidth = canonical.width;
    win._mascotTargetHeight = canonical.height;
  }
  return canonical;
}

module.exports = {
  MASCOT_CANONICAL_PRESETS,
  MASCOT_PRESET_KEYS,
  getMascotPreset,
  syncMascotWindowPreset
};
