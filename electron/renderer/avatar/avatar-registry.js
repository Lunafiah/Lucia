/**
 * Modular Avatar Engine Registry (avatar-registry.js)
 * Enables hot-swapping between Canvas, Live2D, and 3D VRM rendering engines.
 */

class BaseAvatarEngine {
  /**
   * Initialize the avatar engine on the target DOM container or canvas element.
   * @param {HTMLElement|HTMLCanvasElement} container
   */
  init(container) {
    this.container = container;
  }

  /**
   * Update the emotional state of the avatar.
   * @param {{ pleasure: number, arousal: number, dominance: number }} padState
   */
  updateEmotion(padState) {}

  /**
   * Play speech audio through the avatar's lip-sync analyzer.
   * @param {Blob|ArrayBuffer} audioData
   * @param {Function} [onComplete]
   */
  speak(audioData, onComplete) {}

  /**
   * Set the master audio volume (0.0 to 1.0).
   * @param {number} volume
   */
  setVolume(volume) {}

  /**
   * Resize the renderer.
   * @param {number} width
   * @param {number} height
   */
  resize(width, height) {}

  /**
   * Clean up resources, animation loops, and audio contexts.
   */
  destroy() {}
}

class AvatarRegistry {
  constructor() {
    this._engines = new Map();
    this._activeEngine = null;
    this._activeName = null;
  }

  /**
   * Register a new avatar engine class.
   * @param {string} name
   * @param {typeof BaseAvatarEngine} engineClass
   */
  register(name, engineClass) {
    this._engines.set(name, engineClass);
    console.log(`[avatar-registry] Registered engine: ${name}`);
  }

  /**
   * Activate an engine on the given container.
   * @param {string} name
   * @param {HTMLElement|HTMLCanvasElement} container
   * @returns {BaseAvatarEngine}
   */
  use(name, container) {
    if (this._activeEngine) {
      this._activeEngine.destroy();
      this._activeEngine = null;
    }

    const EngineClass = this._engines.get(name);
    if (!EngineClass) {
      console.warn(`[avatar-registry] Engine '${name}' not found, falling back to default.`);
      return null;
    }

    this._activeEngine = new EngineClass();
    this._activeEngine.init(container);
    this._activeName = name;
    console.log(`[avatar-registry] Activated engine: ${name}`);
    return this._activeEngine;
  }

  getActiveEngine() {
    return this._activeEngine;
  }

  getActiveEngineName() {
    return this._activeName;
  }

  getAvailableEngines() {
    return Array.from(this._engines.keys());
  }
}

if (typeof window !== 'undefined') {
  window.BaseAvatarEngine = BaseAvatarEngine;
  window.AvatarRegistry = AvatarRegistry;
  window.avatarRegistry = new AvatarRegistry();
}

if (typeof module !== 'undefined' && module.exports) {
  module.exports = { BaseAvatarEngine, AvatarRegistry };
}
