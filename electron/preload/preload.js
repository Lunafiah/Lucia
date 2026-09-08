const { contextBridge, ipcRenderer } = require('electron');

/**
 * Preload script exposing a secure, sandboxed API to the renderer process.
 *
 * Requirements: Phase 3 (5.3, 10.1, 10.4)
 */

const ALLOWED_CHANNELS = ['backend:ready', 'backend:error', 'voice:mute-toggled'];

contextBridge.exposeInMainWorld('lucia', {
  chat: {
    send: (input) => {
      if (typeof input !== 'string') {
        return Promise.reject(new Error('Input must be a string'));
      }
      return ipcRenderer.invoke('chat:send', { input });
    }
  },
  state: {
    get: () => ipcRenderer.invoke('state:get')
  },
  system: {
    getProfile: () => ipcRenderer.invoke('profile:get'),
    setProfile: (profile) => ipcRenderer.invoke('profile:set', { profile })
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
