const { contextBridge, ipcRenderer } = require('electron');

/**
 * Preload script exposing a secure, sandboxed API to the renderer process.
 *
 * Requirements: Phase 3 (5.3, 10.1, 10.4); Phase 9 (ADR-019)
 *
 * Phase 9 additions: voice.*, system.getHardwareProfile/setHardwareProfile,
 *   chat.getHistory — eliminating all direct fetch() calls in chat.js (ADR-019).
 */

const ALLOWED_CHANNELS = ['backend:ready', 'backend:error', 'voice:mute-toggled'];

contextBridge.exposeInMainWorld('lucia', {
  chat: {
    send: (input) => {
      if (typeof input !== 'string') {
        return Promise.reject(new Error('Input must be a string'));
      }
      return ipcRenderer.invoke('chat:send', { input });
    },
    getHistory: (limit = 50) => ipcRenderer.invoke('chat:get-history', { limit })
  },
  state: {
    get: () => ipcRenderer.invoke('state:get')
  },
  voice: {
    /**
     * Synthesize speech and return an ArrayBuffer of audio/mpeg bytes.
     * @param {string} text
     * @param {{ rate?: string, volume?: string, pitch?: string }} [opts]
     * @returns {Promise<ArrayBuffer>}
     */
    synthesize: (text, opts = {}) =>
      ipcRenderer.invoke('voice:synthesize', { text, ...opts }),

    /**
     * Transcribe an audio blob to text.
     * @param {Blob} blob
     * @returns {Promise<{ status: string, text: string }>}
     */
    transcribe: (blob) =>
      ipcRenderer.invoke('voice:transcribe', blob),

    /**
     * Return discovered RVC models and active model.
     * @returns {Promise<{ models: Array, active_model: string }>}
     */
    getModels: () => ipcRenderer.invoke('voice:get-models'),

    /**
     * Select active RVC model by name (or 'default').
     * @param {string} modelName
     * @returns {Promise<{ status: string, active_model: string }>}
     */
    selectModel: (modelName) =>
      ipcRenderer.invoke('voice:select-model', { modelName })
  },
  system: {
    /**
     * Return factual host hardware and compute capabilities (device, CUDA, VRAM, CPU threads).
     * @returns {Promise<object>}
     */
    getHardwareCapabilities: () => ipcRenderer.invoke('system:get-hardware'),
    getHardwareProfile: () => ipcRenderer.invoke('system:get-hardware'),
    getProfile: () => ipcRenderer.invoke('system:get-hardware'),
    /**
     * Fetch the user/companion profile (user_name, companion_name, etc.)
     * @returns {Promise<object>}
     */
    getUserProfile: () => ipcRenderer.invoke('system:get-user-profile'),
    /**
     * Save user/companion profile fields.
     * @param {object} data
     * @returns {Promise<object>}
     */
    setUserProfile: (data) =>
      ipcRenderer.invoke('system:set-user-profile', { data })
  },
  runtime: {
    getDescriptor: () => ipcRenderer.invoke('runtime:descriptor'),
    getSnapshot: () => ipcRenderer.invoke('runtime:snapshot')
  },
  sim: {
    clock: {
      step: (delta_ms) => ipcRenderer.invoke('sim:clock:step', { delta_ms }),
      pause: () => ipcRenderer.invoke('sim:clock:pause'),
      resume: () => ipcRenderer.invoke('sim:clock:resume'),
      setSpeed: (multiplier) => ipcRenderer.invoke('sim:clock:speed', { multiplier }),
      reset: (reset_time_s) => ipcRenderer.invoke('sim:clock:reset', { reset_time_s })
    },
    stimulus: {
      injectText: (text, source) => ipcRenderer.invoke('sim:stimulus:inject-text', { text, source }),
      injectVector: (vector, source) => ipcRenderer.invoke('sim:stimulus:inject-vector', { vector, source }),
      getPresets: () => ipcRenderer.invoke('sim:stimulus:presets'),
      injectPreset: (preset, pathway) => ipcRenderer.invoke('sim:stimulus:preset', { preset, pathway }),
      getHistory: (limit) => ipcRenderer.invoke('sim:stimulus:history', { limit })
    },
    scenarios: {
      list: () => ipcRenderer.invoke('sim:scenarios:list'),
      run: (scenario_id) => ipcRenderer.invoke('sim:scenarios:run', { scenario_id }),
      getResults: () => ipcRenderer.invoke('sim:scenarios:results')
    },
    chat: (input) => ipcRenderer.invoke('sim:chat', { input })
  },
  models: {
    getAvatars: () => ipcRenderer.invoke('models:get-avatars'),
    getVoices: () => ipcRenderer.invoke('models:get-voices')
  },
  window: {
    toggleMascot: () => ipcRenderer.invoke('window:toggle-mascot'),
    moveMascotBy: (dx, dy) => ipcRenderer.invoke('window:move-mascot-by', { dx, dy }),
    setMascotPreset: (preset) => ipcRenderer.invoke('window:set-mascot-preset', { preset }),
    resetMascotBounds: () => ipcRenderer.invoke('window:reset-mascot-bounds'),
    setIgnoreMouseEvents: (ignore, options) =>
      ipcRenderer.invoke('window:set-ignore-mouse-events', { ignore, forward: options?.forward })
  },
  on: (channel, listener) => {
    if (!ALLOWED_CHANNELS.includes(channel)) {
      console.warn(`[preload] Ignored subscription to unauthorized channel: ${channel}`);
      return () => {};
    }

    const wrapped = (_event, data) => listener(data);
    ipcRenderer.on(channel, wrapped);

    // Return unsubscribe function
    return () => {
      ipcRenderer.removeListener(channel, wrapped);
    };
  }
});
