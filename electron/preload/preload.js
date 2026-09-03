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
    getProfile: () => ipcRenderer.invoke('profile:get')
  },
  models: {
    getAvatars: () => ipcRenderer.invoke('models:get-avatars'),
    getVoices: () => ipcRenderer.invoke('models:get-voices')
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
