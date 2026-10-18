const { ipcMain } = require('electron');
const fs = require('fs');
const path = require('path');
const { syncMascotWindowPreset, getMascotPreset } = require('./mascot-constants.js');

let pendingChat = Promise.resolve();

/**
 * Registers all IPC handlers in the Electron main process.
 * Proxies chat requests and state telemetry to the localhost FastAPI server,
 * or serves mock responses when in UI Preview Mode.
 *
 * Requirements: Phase 3 (5.1–5.6)
 */
function registerHandlers(port = 8765, isPreview = false, getMascotManager = null, mode = 'live') {
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

  // window:set-ignore-mouse-events IPC handler (transparent area click-through)
  ipcMain.handle('window:set-ignore-mouse-events', async (event, { ignore, forward }) => {
    const { BrowserWindow } = require('electron');
    const win = BrowserWindow.fromWebContents(event.sender);
    if (win && !win.isDestroyed()) {
      win.setIgnoreMouseEvents(Boolean(ignore), { forward: Boolean(forward) });
      return true;
    }
    return false;
  });

  // window:move-mascot-by IPC handler (smooth JS window dragging without -webkit-app-region: drag wheel bug)
  ipcMain.handle('window:move-mascot-by', async (event, { dx, dy }) => {
    const { BrowserWindow } = require('electron');
    const win = BrowserWindow.fromWebContents(event.sender);
    if (win && !win.isDestroyed()) {
      if (win.isMaximized()) {
        win.unmaximize();
      }
      const [x, y] = win.getPosition();
      // Ensure target dimensions are strictly anchored to canonical preset (never win.getSize() which suffers from Windows DPI rounding)
      const canonical = syncMascotWindowPreset(win, win._mascotPreset);
      win.setBounds({
        x: Math.round(x + (dx || 0)),
        y: Math.round(y + (dy || 0)),
        width: canonical.width,
        height: canonical.height
      });
      return true;
    }
    return false;
  });

  // window:set-mascot-preset IPC handler (discrete zoom with bottom-center/feet anchor preservation)
  ipcMain.handle('window:set-mascot-preset', async (event, { preset }) => {
    const { BrowserWindow } = require('electron');
    const win = BrowserWindow.fromWebContents(event.sender);
    if (win && !win.isDestroyed()) {
      if (win.isMaximized()) {
        win.unmaximize();
      }
      const [curX, curY] = win.getPosition();
      // Use previous target dimensions if available, falling back to canonical preset
      const prevCanonical = getMascotPreset(win._mascotPreset);
      const curW = win._mascotTargetWidth || prevCanonical.width;
      const curH = win._mascotTargetHeight || prevCanonical.height;

      // Atomically update win metadata to new preset so it never diverges
      const target = syncMascotWindowPreset(win, preset);

      // Calculate new position preserving the bottom-center (feet) screen coordinate:
      const newX = Math.round(curX + (curW - target.width) / 2);
      const newY = Math.round(curY + (curH - target.height));
      win.setBounds({ x: newX, y: newY, width: target.width, height: target.height });
      return { preset: target.key, width: target.width, height: target.height, x: newX, y: newY };
    }
    return null;
  });

  // window:reset-mascot-bounds IPC handler (restores standard 380x540 window with feet anchor and cancels any OS maximize)
  ipcMain.handle('window:reset-mascot-bounds', async (event) => {
    const { BrowserWindow } = require('electron');
    const win = BrowserWindow.fromWebContents(event.sender);
    if (win && !win.isDestroyed()) {
      if (win.isMaximized()) {
        win.unmaximize();
      }
      const [curX, curY] = win.getPosition();
      const prevCanonical = getMascotPreset(win._mascotPreset);
      const curW = win._mascotTargetWidth || prevCanonical.width;
      const curH = win._mascotTargetHeight || prevCanonical.height;

      // Atomically reset win metadata to canonical 'normal'
      const canonical = syncMascotWindowPreset(win, 'normal');

      const newX = Math.round(curX + (curW - canonical.width) / 2);
      const newY = Math.round(curY + (curH - canonical.height));
      win.setBounds({ x: newX, y: newY, width: canonical.width, height: canonical.height });
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
  ipcMain.handle('chat:send', async (_event, payload) => {
    const input = typeof payload === 'string' ? payload : (payload && payload.input);
    const language = (payload && payload.language) || null;
    if (isPreview) {
      // Mock response for UI Preview
      return {
        response: `[UI Preview]: Lucia's brain is sleeping (0% GPU/CPU). You typed: "${input}".`,
        call_id: 'preview_call'
      };
    }

    if (mode === 'simulation') {
      try {
        const response = await fetch(`${baseUrl}/sim/chat`, {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ input }),
          signal: AbortSignal.timeout(10000)
        });
        if (!response.ok) {
          const errData = await response.json().catch(() => ({}));
          throw { code: `http_${response.status}`, message: errData.detail || `HTTP ${response.status}` };
        }
        const data = await response.json();
        return {
          response: data.assistant_reply || data.response || "...",
          call_id: `sim_${Date.now()}`
        };
      } catch (err) {
        if (err.name === 'TimeoutError') {
          throw { code: 'timeout', message: 'Simulation chat timed out' };
        }
        if (err.code) throw err;
        throw { code: 'sim_error', message: err.message || 'Simulation chat failed' };
      }
    }

    // Chain onto pendingChat so only one chat request is in-flight at a time
    const execute = async () => {
      try {
        const reqBody = { input };
        if (language) reqBody.language = language;
        const response = await fetch(`${baseUrl}/process`, {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify(reqBody),
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
          call_id: data.call_id,
          expression: data.expression || null,
          relationship: data.relationship || null,
          communication: data.communication || null,
          realization: data.realization || null,
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

  // system:get-hardware / profile:get IPC handler — read factual host hardware capabilities
  const handleGetHardware = async () => {
    if (isPreview) {
      return {
        device_name: 'UI Preview Device',
        cuda_available: false,
        vram_mb: 0,
        backend: 'cpu',
        cpu_threads: 4,
        cpu_architecture: 'preview'
      };
    }

    try {
      const response = await fetch(`${baseUrl}/system/hardware`, {
        method: 'GET',
        signal: AbortSignal.timeout(2000)
      });
      if (response.ok) {
        return await response.json();
      }
    } catch (e) {
      // ignore
    }
    return {
      device_name: 'Unknown Host',
      cuda_available: false,
      vram_mb: 0,
      backend: 'cpu',
      cpu_threads: 1,
      cpu_architecture: 'unknown'
    };
  };

  ipcMain.handle('system:get-hardware', handleGetHardware);
  ipcMain.handle('profile:get', handleGetHardware);

  // ---------------------------------------------------------------------------
  // Phase 8: Runtime & Simulation IPC Handlers
  // ---------------------------------------------------------------------------

  ipcMain.handle('runtime:descriptor', async () => {
    if (isPreview) {
      return {
        mode: 'preview',
        is_live: false,
        is_simulated: false,
        state: 'PREVIEW',
        active_profile: 'preview',
        capabilities: ['mock_chat', 'canvas_avatar']
      };
    }
    try {
      const response = await fetch(`${baseUrl}/runtime/descriptor`, {
        signal: AbortSignal.timeout(3000)
      });
      return await response.json();
    } catch (e) {
      return { mode: mode || 'live', is_live: mode === 'live', error: e.message };
    }
  });

  ipcMain.handle('runtime:snapshot', async () => {
    if (isPreview) {
      return {
        runtime: { mode: 'preview', state: 'PREVIEW', is_live: false, is_simulated: false },
        clock: { virtual_time_s: 0, is_paused: true, speed_factor: 1.0 },
        pad: { pleasure: 0.25, arousal: -0.05, dominance: 0.05 },
        storage: { storage_type: 'preview_mock' }
      };
    }
    try {
      const response = await fetch(`${baseUrl}/runtime/snapshot`, {
        signal: AbortSignal.timeout(3000)
      });
      return await response.json();
    } catch (e) {
      return { error: e.message };
    }
  });

  ipcMain.handle('sim:clock:step', async (_event, { delta_ms = 200 }) => {
    const res = await fetch(`${baseUrl}/sim/clock/step`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ delta_ms }),
      signal: AbortSignal.timeout(5000)
    });
    return await res.json();
  });

  ipcMain.handle('sim:clock:pause', async () => {
    const res = await fetch(`${baseUrl}/sim/clock/pause`, {
      method: 'POST',
      signal: AbortSignal.timeout(3000)
    });
    return await res.json();
  });

  ipcMain.handle('sim:clock:resume', async () => {
    const res = await fetch(`${baseUrl}/sim/clock/resume`, {
      method: 'POST',
      signal: AbortSignal.timeout(3000)
    });
    return await res.json();
  });

  ipcMain.handle('sim:clock:speed', async (_event, { multiplier = 1.0 }) => {
    const res = await fetch(`${baseUrl}/sim/clock/speed`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ multiplier }),
      signal: AbortSignal.timeout(3000)
    });
    return await res.json();
  });

  ipcMain.handle('sim:clock:reset', async (_event, { reset_time_s = 0.0 }) => {
    const res = await fetch(`${baseUrl}/sim/clock/reset`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ reset_time_s }),
      signal: AbortSignal.timeout(3000)
    });
    return await res.json();
  });

  ipcMain.handle('sim:stimulus:inject-text', async (_event, { text, source = 'desktop_ui' }) => {
    const res = await fetch(`${baseUrl}/sim/stimulus/inject-text`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ text, source }),
      signal: AbortSignal.timeout(5000)
    });
    return await res.json();
  });

  ipcMain.handle('sim:stimulus:inject-vector', async (_event, { vector, source = 'debug_probe' }) => {
    const res = await fetch(`${baseUrl}/sim/stimulus/inject-vector`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ vector, source }),
      signal: AbortSignal.timeout(5000)
    });
    return await res.json();
  });

  ipcMain.handle('sim:stimulus:presets', async () => {
    const res = await fetch(`${baseUrl}/sim/stimulus/presets`, {
      signal: AbortSignal.timeout(3000)
    });
    return await res.json();
  });

  ipcMain.handle('sim:stimulus:preset', async (_event, { preset, pathway = 'sensory_text' }) => {
    const res = await fetch(`${baseUrl}/sim/stimulus/preset`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ preset, pathway }),
      signal: AbortSignal.timeout(5000)
    });
    return await res.json();
  });

  ipcMain.handle('sim:stimulus:history', async (_event, { limit = 50 }) => {
    const res = await fetch(`${baseUrl}/sim/stimulus/history?limit=${limit}`, {
      signal: AbortSignal.timeout(3000)
    });
    return await res.json();
  });

  ipcMain.handle('sim:scenarios:list', async () => {
    const res = await fetch(`${baseUrl}/sim/scenarios/list`, {
      signal: AbortSignal.timeout(3000)
    });
    return await res.json();
  });

  ipcMain.handle('sim:scenarios:run', async (_event, { scenario_id = 'all' }) => {
    const res = await fetch(`${baseUrl}/sim/scenarios/run`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ scenario_id }),
      signal: AbortSignal.timeout(30000)
    });
    return await res.json();
  });

  ipcMain.handle('sim:scenarios:results', async () => {
    const res = await fetch(`${baseUrl}/sim/scenarios/results`, {
      signal: AbortSignal.timeout(3000)
    });
    return await res.json();
  });

  ipcMain.handle('sim:chat', async (_event, { input }) => {
    const res = await fetch(`${baseUrl}/sim/chat`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ input }),
      signal: AbortSignal.timeout(10000)
    });
    return await res.json();
  });

  // ---------------------------------------------------------------------------
  // Phase 9: IPC handlers for voice, system profile, and chat history
  // These replace direct fetch() calls that previously lived in chat.js (ADR-019)
  // ---------------------------------------------------------------------------

  // voice:synthesize — synthesize speech and return audio Buffer
  ipcMain.handle('voice:synthesize', async (_event, payload) => {
    const { text, language, rate, volume, pitch, pitch_hz, closeness, focal_words } = payload || {};
    if (!text || !text.trim()) {
      return Buffer.alloc(0);
    }
    const body = { text, language: language || 'ja' };
    if (rate) body.rate = rate;
    if (volume) body.volume = volume;
    if (pitch) body.pitch = pitch;
    if (pitch_hz !== undefined && pitch_hz !== null) body.pitch_hz = pitch_hz;
    if (closeness !== undefined && closeness !== null) body.closeness = closeness;
    if (focal_words) body.focal_words = focal_words;
    try {
      const res = await fetch(`${baseUrl}/voice/synthesize`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(body),
        signal: AbortSignal.timeout(30000)
      });
      if (!res.ok) {
        throw new Error(`Voice synthesis HTTP ${res.status}`);
      }
      const arrayBuf = await res.arrayBuffer();
      return Buffer.from(arrayBuf);
    } catch (err) {
      console.warn('[ipc-bridge] voice:synthesize error:', err.message);
      throw err;
    }
  });

  // voice:transcribe — transcribe audio blob to text
  ipcMain.handle('voice:transcribe', async (_event, blobOrBuffer) => {
    try {
      let audioBuffer;
      if (Buffer.isBuffer(blobOrBuffer)) {
        audioBuffer = blobOrBuffer;
      } else if (blobOrBuffer instanceof Uint8Array) {
        audioBuffer = Buffer.from(blobOrBuffer);
      } else {
        return { status: 'error', text: '', error: 'Invalid audio data type' };
      }
      const res = await fetch(`${baseUrl}/voice/transcribe`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/octet-stream' },
        body: audioBuffer,
        signal: AbortSignal.timeout(15000)
      });
      if (!res.ok) {
        throw new Error(`Transcribe HTTP ${res.status}`);
      }
      return await res.json();
    } catch (err) {
      console.warn('[ipc-bridge] voice:transcribe error:', err.message);
      return { status: 'error', text: '', error: err.message };
    }
  });

  // voice:get-models — list available RVC voice models
  ipcMain.handle('voice:get-models', async () => {
    try {
      const res = await fetch(`${baseUrl}/voice/models`, {
        signal: AbortSignal.timeout(3000)
      });
      if (res.ok) return await res.json();
    } catch (err) {
      console.warn('[ipc-bridge] voice:get-models error:', err.message);
    }
    return { models: [{ name: 'default', is_active: true }], active_model: 'default' };
  });

  // voice:select-model — select active RVC model
  ipcMain.handle('voice:select-model', async (_event, { modelName }) => {
    try {
      const res = await fetch(`${baseUrl}/voice/select-model`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ model_name: modelName }),
        signal: AbortSignal.timeout(5000)
      });
      if (res.ok) return await res.json();
      throw new Error(`HTTP ${res.status}`);
    } catch (err) {
      console.warn('[ipc-bridge] voice:select-model error:', err.message);
      return { status: 'error', error: err.message };
    }
  });

  // system:get-hardware-profile — alias to system:get-hardware
  ipcMain.handle('system:get-hardware-profile', handleGetHardware);

  // system:get-user-profile — fetch user/companion profile
  ipcMain.handle('system:get-user-profile', async () => {
    if (isPreview) {
      return { user_name: 'Friend', companion_name: 'Lucia', is_onboarded: false };
    }
    try {
      const res = await fetch(`${baseUrl}/profile`, {
        signal: AbortSignal.timeout(2000)
      });
      if (res.ok) return await res.json();
    } catch (err) {
      console.warn('[ipc-bridge] system:get-user-profile error:', err.message);
    }
    return { user_name: 'Friend', companion_name: 'Lucia', is_onboarded: false };
  });

  // system:set-user-profile — save user/companion profile fields
  ipcMain.handle('system:set-user-profile', async (_event, { data }) => {
    if (isPreview) {
      return { status: 'ok', profile: data };
    }
    try {
      const res = await fetch(`${baseUrl}/profile`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(data),
        signal: AbortSignal.timeout(4000)
      });
      if (res.ok) return await res.json();
    } catch (err) {
      console.warn('[ipc-bridge] system:set-user-profile error:', err.message);
    }
    return { status: 'error' };
  });

  // chat:get-history — fetch recent conversation history
  ipcMain.handle('chat:get-history', async (_event, { limit = 50 } = {}) => {
    if (isPreview) {
      return { turns: [] };
    }
    try {
      const res = await fetch(`${baseUrl}/history?limit=${limit}`, {
        signal: AbortSignal.timeout(3000)
      });
      if (res.ok) return await res.json();
    } catch (err) {
      console.warn('[ipc-bridge] chat:get-history error:', err.message);
    }
    return { turns: [] };
  });
}

module.exports = { registerHandlers };
