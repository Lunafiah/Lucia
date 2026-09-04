const { ipcMain } = require('electron');
const fs = require('fs');
const path = require('path');

let pendingChat = Promise.resolve();

/**
 * Registers all IPC handlers in the Electron main process.
 * Proxies chat requests and state telemetry to the localhost FastAPI server,
 * or serves mock responses when in UI Preview Mode.
 *
 * Requirements: Phase 3 (5.1–5.6)
 */
function registerHandlers(port = 8765, isPreview = false, getMascotManager = null) {
  const baseUrl = `http://127.0.0.1:${port}`;

  // window:toggle-mascot IPC handler
  ipcMain.handle('window:toggle-mascot', async () => {
    if (getMascotManager) {
      const manager = typeof getMascotManager === 'function' ? getMascotManager() : getMascotManager;
      if (manager && manager.toggle) {
        manager.toggle();
        return true;
      }
    }
    return false;
  });

  // window:move-mascot-by IPC handler (smooth JS window dragging without -webkit-app-region: drag wheel bug)
  ipcMain.handle('window:move-mascot-by', async (event, { dx, dy }) => {
    const { BrowserWindow } = require('electron');
    const win = BrowserWindow.fromWebContents(event.sender);
    if (win && !win.isDestroyed()) {
      const [x, y] = win.getPosition();
      win.setPosition(Math.round(x + (dx || 0)), Math.round(y + (dy || 0)));
      return true;
    }
    return false;
  });

  // models:get-avatars IPC handler (direct fs scan, works in both live and preview)
  ipcMain.handle('models:get-avatars', async () => {
    const rootDir = path.resolve(__dirname, '../../');
    const baseDir = path.join(rootDir, 'models', 'avatar');
    const result = {
      basePath: rootDir.replace(/\\/g, '/'),
      engines: ['canvas', 'sprites', 'live2d', 'vrm'],
      sprites: [],
      live2d: [],
      vrm: []
    };

    try {
      const spritesDir = path.join(baseDir, 'sprites');
      if (fs.existsSync(spritesDir)) {
        result.sprites = fs.readdirSync(spritesDir, { withFileTypes: true })
          .filter(d => d.isDirectory() && !d.name.startsWith('.') && d.name !== '__pycache__')
          .map(d => d.name);
      }

      const live2dDir = path.join(baseDir, 'live2d');
      if (fs.existsSync(live2dDir)) {
        result.live2d = fs.readdirSync(live2dDir, { withFileTypes: true })
          .filter(d => d.isDirectory() && !d.name.startsWith('.'))
          .map(d => d.name);
      }

      const vrmDir = path.join(baseDir, 'vrm');
      if (fs.existsSync(vrmDir)) {
        result.vrm = fs.readdirSync(vrmDir, { withFileTypes: true })
          .filter(f => f.isFile() && f.name.toLowerCase().endsWith('.vrm'))
          .map(f => f.name);
      }
    } catch (err) {
      console.warn('[ipc-bridge] Failed to scan avatar models:', err);
    }

    return result;
  });

  // models:get-voices IPC handler
  ipcMain.handle('models:get-voices', async () => {
    const rootDir = path.resolve(__dirname, '../../');
    const rvcDir = path.join(rootDir, 'models', 'voice', 'rvc');
    const models = [
      { name: 'default', is_active: true, description: 'Lucia Base Voice (en-US-AnaNeural)' }
    ];

    try {
      if (fs.existsSync(rvcDir)) {
        const subdirs = fs.readdirSync(rvcDir, { withFileTypes: true })
          .filter(d => d.isDirectory() && !d.name.startsWith('.'));
        subdirs.forEach(d => {
          models.push({
            name: d.name,
            is_active: false,
            description: `RVC: ${d.name}`
          });
        });
      }
    } catch (err) {
      console.warn('[ipc-bridge] Failed to scan voice models:', err);
    }

    return { models, active_model: 'default' };
  });

  // chat:send IPC handler (serialized queue)
  ipcMain.handle('chat:send', async (_event, { input }) => {
    if (isPreview) {
      // Mock response for UI Preview
      return {
        response: `[UI Preview]: Lucia's brain is sleeping (0% GPU/CPU). You typed: "${input}".`,
        call_id: 'preview_call'
      };
    }

    // Chain onto pendingChat so only one chat request is in-flight at a time
    const execute = async () => {
      try {
        const response = await fetch(`${baseUrl}/process`, {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ input }),
          signal: AbortSignal.timeout(35000)
        });

        if (!response.ok) {
          const errData = await response.json().catch(() => ({}));
          const errCode = errData.error || `http_${response.status}`;
          throw {
            code: errCode,
            message: `Server returned HTTP ${response.status}`,
            status: response.status
          };
        }

        const data = await response.json();
        return {
          response: data.response,
          call_id: data.call_id
        };
      } catch (err) {
        if (err.name === 'TimeoutError') {
          throw { code: 'timeout', message: 'Request to Lucia timed out after 35s' };
        }
        if (err.code) throw err;
        throw { code: 'network_error', message: err.message || 'Failed to reach Lucia backend' };
      }
    };

    const currentPromise = pendingChat.then(execute, execute);
    pendingChat = currentPromise.catch(() => {});
    return currentPromise;
  });

  // state:get IPC handler (concurrent allowed, 2s timeout)
  ipcMain.handle('state:get', async () => {
    if (isPreview) {
      return {
        pad: { pleasure: 0.25, arousal: -0.05, dominance: 0.05 },
        somatic: { stability: 0.95, cognitive_load: 0.1, energy: 1.0, tension: 0.05 },
        constraints: { max_tokens: 150, temperature: 0.75, latency_ms: 0, reasoning_depth: 1 },
        memory_trace_count: 14,
        timestamp: Date.now(),
        profile: 'Preview Mode'
      };
    }

    try {
      const response = await fetch(`${baseUrl}/state`, {
        method: 'GET',
        headers: { 'Cache-Control': 'no-store' },
        signal: AbortSignal.timeout(2000)
      });

      if (!response.ok) {
        throw { code: 'state_error', message: `HTTP ${response.status}` };
      }

      return await response.json();
    } catch (err) {
      if (err.name === 'TimeoutError') {
        throw { code: 'state_timeout', message: 'State poll timed out' };
      }
      if (err.code) throw err;
      throw { code: 'state_error', message: err.message || 'Failed to get state' };
    }
  });

  // profile:get IPC handler
  ipcMain.handle('profile:get', async () => {
    if (isPreview) {
      return {
        tier: 'preview',
        name: 'UI Preview',
        description: 'Stand-alone UI Design & Mock Preview Mode',
        vram_mb: 0,
        n_gpu_layers: 0
      };
    }

    try {
      const response = await fetch(`${baseUrl}/system/profile`, {
        method: 'GET',
        signal: AbortSignal.timeout(2000)
      });
      if (response.ok) {
        return await response.json();
      }
    } catch (e) {
      // ignore
    }
    return { tier: 'unknown' };
  });

  // profile:set IPC handler
  ipcMain.handle('profile:set', async (_event, { profile }) => {
    if (isPreview) {
      return {
        status: 'ok',
        tier: profile,
        name: `Preview (${profile})`,
        description: 'Simulated Profile in UI Preview Mode',
        vram_mb: 4096,
        n_ctx: 2048
      };
    }

    try {
      const response = await fetch(`${baseUrl}/system/profile`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ profile }),
        signal: AbortSignal.timeout(4000)
      });
      if (response.ok) {
        return await response.json();
      }
    } catch (e) {
      console.warn('[ipc-bridge] Failed to set profile:', e);
    }
    return { status: 'error' };
  });
}

module.exports = { registerHandlers };
