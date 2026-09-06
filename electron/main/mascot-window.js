/**
 * Floating Mascot Window Controller (mascot-window.js)
 * Creates a compact Always-on-Top floating avatar window.
 */

const { BrowserWindow } = require('electron');
const path = require('path');
const { syncMascotWindowPreset, getMascotPreset } = require('./mascot-constants.js');

class MascotWindowManager {
  /**
   * @param {import('electron').BrowserWindow} mainWindow
   */
  constructor(mainWindow) {
    this.mainWindow = mainWindow;
    this.mascotWindow = null;
  }

  show() {
    if (this.mascotWindow && !this.mascotWindow.isDestroyed()) {
      this.mascotWindow.show();
      this.mascotWindow.focus();
      return;
    }

    const initialPreset = getMascotPreset('normal');
    this.mascotWindow = new BrowserWindow({
      width: initialPreset.width,
      height: initialPreset.height,
      minWidth: 180,
      minHeight: 220,
      frame: false,
      transparent: true,
      alwaysOnTop: true,
      resizable: false,
      maximizable: false,
      fullscreenable: false,
      hasShadow: false,
      skipTaskbar: true,
      webPreferences: {
        preload: path.join(__dirname, '../preload/preload.js'),
        contextIsolation: true,
        nodeIntegration: false,
        webSecurity: false,
      },
    });

    syncMascotWindowPreset(this.mascotWindow, 'normal');

    // Load mascot html or index with query param
    this.mascotWindow.loadFile(path.join(__dirname, '../renderer/index.html'), {
      query: { mode: 'mascot' },
    });

    if (this.mainWindow && !this.mainWindow.isDestroyed()) {
      this.mainWindow.hide();
    }
  }

  hide() {
    if (this.mascotWindow && !this.mascotWindow.isDestroyed()) {
      this.mascotWindow.close();
      this.mascotWindow = null;
    }
    if (this.mainWindow && !this.mainWindow.isDestroyed()) {
      this.mainWindow.show();
      this.mainWindow.focus();
    }
  }

  toggle() {
    if (this.mascotWindow && !this.mascotWindow.isDestroyed() && this.mascotWindow.isVisible()) {
      this.hide();
    } else {
      this.show();
    }
  }

  destroy() {
    if (this.mascotWindow && !this.mascotWindow.isDestroyed()) {
      this.mascotWindow.destroy();
      this.mascotWindow = null;
    }
  }
}

module.exports = MascotWindowManager;
