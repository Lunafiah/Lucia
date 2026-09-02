/**
 * Floating Mascot Window Controller (mascot-window.js)
 * Creates a compact Always-on-Top floating avatar window.
 */

const { BrowserWindow } = require('electron');
const path = require('path');

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

    this.mascotWindow = new BrowserWindow({
      width: 240,
      height: 300,
      frame: false,
      transparent: true,
      alwaysOnTop: true,
      resizable: false,
      skipTaskbar: true,
      webPreferences: {
        preload: path.join(__dirname, '../preload/preload.js'),
        contextIsolation: true,
        nodeIntegration: false,
      },
    });

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
