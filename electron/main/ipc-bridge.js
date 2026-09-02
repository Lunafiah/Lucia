const { ipcMain } = require('electron');

let pendingChat = Promise.resolve();

/**
 * Registers all IPC handlers in the Electron main process.
 * Proxies chat requests and state telemetry to the localhost FastAPI server.
 *
 * Requirements: Phase 3 (5.1–5.6)
 */
function registerHandlers(port = 8765) {
  const baseUrl = `http://127.0.0.1:${port}`;

  // chat:send IPC handler (serialized queue)
  ipcMain.handle('chat:send', async (_event, { input }) => {
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
}

module.exports = { registerHandlers };
