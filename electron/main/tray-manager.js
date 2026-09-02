/**
 * System Tray Manager (tray-manager.js)
 * Manages Windows notification area icon, context menu, and background persistence.
 */

const { Tray, Menu, nativeImage, app } = require('electron');
const path = require('path');

class TrayManager {
  /**
   * @param {import('electron').BrowserWindow} mainWindow
   * @param {Object} options
   */
  constructor(mainWindow, options = {}) {
    this.mainWindow = mainWindow;
    this.tray = null;
    this.isMuted = false;
    this.onToggleMascot = options.onToggleMascot || (() => {});
    this.onToggleMute = options.onToggleMute || (() => {});
  }

  init() {
    // Create simple 16x16 icon or load from assets
    const iconPath = path.join(__dirname, '../renderer/assets/icon.png');
    let icon;
    try {
      icon = nativeImage.createFromPath(iconPath);
      if (icon.isEmpty()) {
        icon = nativeImage.createEmpty();
      }
    } catch (e) {
      icon = nativeImage.createEmpty();
    }

    this.tray = new Tray(icon);
    this.tray.setToolTip('Lucia — Affective AI Companion');

    this.updateContextMenu();

    this.tray.on('double-click', () => {
      this.toggleMainWindow();
    });
  }

  toggleMainWindow() {
    if (!this.mainWindow || this.mainWindow.isDestroyed()) return;
    if (this.mainWindow.isVisible()) {
      this.mainWindow.hide();
    } else {
      this.mainWindow.show();
      this.mainWindow.focus();
    }
  }

  updateContextMenu() {
    if (!this.tray) return;

    const contextMenu = Menu.buildFromTemplate([
      {
        label: 'Show / Hide Lucia',
        click: () => this.toggleMainWindow(),
      },
      {
        label: 'Floating Mascot Mode',
        click: () => this.onToggleMascot(),
      },
      {
        label: this.isMuted ? 'Unmute Voice' : 'Mute Voice',
        click: () => {
          this.isMuted = !this.isMuted;
          this.onToggleMute(this.isMuted);
          this.updateContextMenu();
        },
      },
      { type: 'separator' },
      {
        label: 'Quit Lucia',
        click: () => {
          app.isQuitting = true;
          app.quit();
        },
      },
    ]);

    this.tray.setContextMenu(contextMenu);
  }

  destroy() {
    if (this.tray && !this.tray.isDestroyed()) {
      this.tray.destroy();
      this.tray = null;
    }
  }
}

module.exports = TrayManager;
