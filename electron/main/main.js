const { app, BrowserWindow } = require('electron');
const path = require('path');
const fs = require('fs');
const { ProcessManager } = require('./process-manager');
const { registerHandlers } = require('./ipc-bridge');
const TrayManager = require('./tray-manager');
const HotkeyManager = require('./hotkey-manager');
const MascotWindowManager = require('./mascot-window');

let mainWindow = null;
let processManager = null;
let trayManager = null;
let hotkeyManager = null;
let mascotManager = null;

const rootDir = path.resolve(__dirname, '../../');
const configPath = path.join(rootDir, 'config', 'ui.json');
const windowStatePath = path.join(rootDir, 'config', 'window-state.json');

/**
 * Load desktop UI configuration.
 */
function loadConfig() {
  const defaults = {
    port: 8765,
    model_path: '',
    profile: 'auto',
    n_gpu_layers: 32,
    log_level: 'INFO',
    minimize_to_tray: true,
  };

  try {
    if (fs.existsSync(configPath)) {
      const data = JSON.parse(fs.readFileSync(configPath, 'utf8'));
      return { ...defaults, ...data };
    }
  } catch (err) {
    console.error('[main] Error reading ui.json, using defaults:', err);
  }
  return defaults;
}

/**
 * Restore window bounds or provide defaults.
 */
function loadWindowState() {
  try {
    if (fs.existsSync(windowStatePath)) {
      return JSON.parse(fs.readFileSync(windowStatePath, 'utf8'));
    }
  } catch (e) {
    // fallback
  }
  return { width: 1200, height: 780 };
}

/**
 * Persist window bounds on exit.
 */
function saveWindowState() {
  if (!mainWindow || mainWindow.isDestroyed()) return;
  try {
    const bounds = mainWindow.getBounds();
    fs.writeFileSync(windowStatePath, JSON.stringify(bounds, null, 2), 'utf8');
  } catch (err) {
    console.error('[main] Failed to save window state:', err);
  }
}

function createWindow() {
  const state = loadWindowState();

  mainWindow = new BrowserWindow({
    width: state.width || 1200,
    height: state.height || 780,
    x: state.x,
    y: state.y,
    minWidth: 850,
    minHeight: 550,
    backgroundColor: '#12121e',
    autoHideMenuBar: true,
    title: 'Lucia — AI Companion',
    webPreferences: {
      nodeIntegration: false,
      contextIsolation: true,
      preload: path.join(__dirname, '../preload/preload.js'),
    },
  });

  const rendererHtml = path.join(__dirname, '../renderer/index.html');
  mainWindow.loadFile(rendererHtml);

  mainWindow.on('close', (e) => {
    if (!app.isQuitting) {
      e.preventDefault();
      saveWindowState();
      mainWindow.hide();
    } else {
      saveWindowState();
    }
  });

  mainWindow.on('closed', () => {
    mainWindow = null;
  });
}

app.whenReady().then(async () => {
  const config = loadConfig();
  const isPreview = process.argv.includes('--preview') || process.env.LUCIA_PREVIEW === 'true';

  // Register main IPC handlers
  registerHandlers(config.port, isPreview);

  // Create renderer window
  createWindow();

  if (isPreview) {
    console.log('[main] Running in UI PREVIEW MODE (Python backend skipped, 0% GPU/CPU used)');
    if (mainWindow) {
      mainWindow.setTitle('Lucia — UI Preview Mode (Offline)');
      mainWindow.webContents.on('did-finish-load', () => {
        setTimeout(() => {
          if (mainWindow && !mainWindow.isDestroyed()) {
            mainWindow.webContents.send('backend:ready');
          }
        }, 500);
      });
    }
  }

  // Initialize Desktop Presence Modes
  mascotManager = new MascotWindowManager(mainWindow);

  trayManager = new TrayManager(mainWindow, {
    onToggleMascot: () => mascotManager.toggle(),
    onToggleMute: (isMuted) => {
      if (mainWindow && !mainWindow.isDestroyed()) {
        mainWindow.webContents.send('voice:mute-toggled', { isMuted });
      }
    },
  });
  trayManager.init();

  hotkeyManager = new HotkeyManager(mainWindow, 'CommandOrControl+Shift+L');
  hotkeyManager.register();

  if (!isPreview) {
    // Start the Python backend process
    processManager = new ProcessManager(config, () => mainWindow);
    try {
      await processManager.start();
    } catch (err) {
      console.error('[main] Failed to start backend process:', err);
    }
  }
});

app.on('before-quit', async (e) => {
  app.isQuitting = true;
  if (hotkeyManager) hotkeyManager.unregister();
  if (trayManager) trayManager.destroy();
  if (mascotManager) mascotManager.destroy();

  if (processManager) {
    e.preventDefault();
    await processManager.stop();
    processManager = null;
    app.quit();
  }
});

app.on('window-all-closed', () => {
  if (process.platform !== 'darwin' && app.isQuitting) {
    app.quit();
  }
});
