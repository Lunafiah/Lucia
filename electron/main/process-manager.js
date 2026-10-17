const { spawn } = require('child_process');
const path = require('path');
const fs = require('fs');

/**
 * ProcessManager manages the lifecycle of the Python FastAPI backend process.
 * Spawns, monitors ready/error signals, and cleanly terminates on exit.
 */
class ProcessManager {
  constructor(config = {}, getMainWindow = () => null) {
    this.config = config;
    this.getMainWindow = getMainWindow;
    this.process = null;
    this._ready = false;
    this._isShuttingDown = false;
    this._startupTimer = null;
  }

  /**
   * Determine the Python executable path (preferring project's .venv).
   */
  _getPythonPath() {
    const rootDir = path.resolve(__dirname, '../../');
    const winVenv = path.join(rootDir, '.venv', 'Scripts', 'python.exe');
    const unixVenv = path.join(rootDir, '.venv', 'bin', 'python');

    if (fs.existsSync(winVenv)) return winVenv;
    if (fs.existsSync(unixVenv)) return unixVenv;
    return process.platform === 'win32' ? 'python.exe' : 'python3';
  }

  _dispatch(channel, payload = {}) {
    const win = this.getMainWindow();
    if (win && !win.isDestroyed()) {
      win.webContents.send(channel, payload);
    }
  }

  /**
   * Start the Python backend child process.
   */
  start() {
    return new Promise((resolve, reject) => {
      const rootDir = path.resolve(__dirname, '../../');
      const pythonPath = this._getPythonPath();
      const port = this.config.port || 8765;
      const modelPath = this.config.model_path || '';
      const logLevel = this.config.log_level || 'INFO';
      const mode = this.config.mode || 'live';

      const args = [
        '-m', 'src.api.server',
        '--port', String(port),
        '--model-path', modelPath,
        '--log-level', logLevel,
        '--mode', mode
      ];

      console.log(`[ProcessManager] Spawning backend: ${pythonPath} ${args.join(' ')}`);

      this.process = spawn(pythonPath, args, {
        cwd: rootDir,
        detached: false,
        stdio: ['pipe', 'pipe', 'pipe'],
        env: { ...process.env, PYTHONUNBUFFERED: '1' }
      });

      // 60-second startup timeout watchdog
      this._startupTimer = setTimeout(() => {
        if (!this._ready) {
          console.error('[ProcessManager] Backend startup timed out after 60s');
          this._dispatch('backend:error', { code: 'startup_timeout' });
          this.stop();
          reject(new Error('startup_timeout'));
        }
      }, 60000);

      this.process.stdout.on('data', (data) => {
        const text = data.toString();
        const lines = text.split('\n');

        for (const rawLine of lines) {
          const line = rawLine.trim();
          if (!line) continue;
          console.log(`[python] ${line}`);

          if (line.includes('LUCIA_BACKEND_READY')) {
            if (!this._ready) {
              this._ready = true;
              clearTimeout(this._startupTimer);
              console.log('[ProcessManager] Backend signal received: READY');
              this._dispatch('backend:ready');
              resolve();
            }
          } else if (line.startsWith('LUCIA_BACKEND_ERROR:')) {
            const reason = line.replace('LUCIA_BACKEND_ERROR:', '').trim();
            console.error(`[ProcessManager] Backend error signal: ${reason}`);
            clearTimeout(this._startupTimer);
            this._dispatch('backend:error', { code: reason });
            reject(new Error(reason));
          }
        }
      });

      this.process.stderr.on('data', (data) => {
        const text = data.toString().trim();
        if (text) {
          console.error(`[python:err] ${text}`);
        }
      });

      this.process.on('exit', (code, signal) => {
        console.log(`[ProcessManager] Python backend exited with code ${code}, signal ${signal}`);
        clearTimeout(this._startupTimer);

        if (!this._isShuttingDown && !this._ready) {
          this._dispatch('backend:error', {
            code: 'startup_failed',
            exitCode: code
          });
          reject(new Error(`Process exited with code ${code}`));
        } else if (!this._isShuttingDown) {
          this._dispatch('backend:error', {
            code: 'process_exited',
            exitCode: code
          });
        }
      });
    });
  }

  /**
   * Stop the Python backend process gracefully.
   */
  async stop() {
    this._isShuttingDown = true;
    clearTimeout(this._startupTimer);

    if (!this.process) return;

    return new Promise((resolve) => {
      const pid = this.process.pid;
      console.log(`[ProcessManager] Stopping backend process (PID: ${pid})...`);

      const killTimeout = setTimeout(() => {
        if (this.process && !this.process.killed) {
          console.warn('[ProcessManager] Backend did not terminate within 10s, sending force kill');
          try {
            this.process.kill('SIGKILL');
          } catch (e) {
            // Process might already be dead
          }
        }
        resolve();
      }, 10000);

      this.process.on('exit', () => {
        clearTimeout(killTimeout);
        resolve();
      });

      try {
        if (process.platform === 'win32') {
          // On Windows, taskkill kills the process tree
          spawn('taskkill', ['/pid', String(pid), '/T', '/F']);
        } else {
          this.process.kill('SIGTERM');
        }
      } catch (err) {
        console.error('[ProcessManager] Error killing process:', err);
        resolve();
      }
    });
  }
}

module.exports = { ProcessManager };
