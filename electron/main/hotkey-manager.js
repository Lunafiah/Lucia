/**
 * Global Hotkey Manager (hotkey-manager.js)
 * Registers OS-wide shortcuts to summon or minimize Lucia from any application.
 */

const { globalShortcut } = require('electron');

class HotkeyManager {
  /**
   * @param {import('electron').BrowserWindow} mainWindow
   * @param {string} [shortcut='CommandOrControl+Shift+L']
   */
  constructor(mainWindow, shortcut = 'CommandOrControl+Shift+L') {
    this.mainWindow = mainWindow;
    this.shortcut = shortcut;
    this.isRegistered = false;
  }

  register() {
    try {
      this.isRegistered = globalShortcut.register(this.shortcut, () => {
        if (!this.mainWindow || this.mainWindow.isDestroyed()) return;

        if (this.mainWindow.isVisible()) {
          this.mainWindow.hide();
        } else {
          this.mainWindow.show();
          this.mainWindow.focus();
        }
      });
      console.log(`[hotkey] Registered global shortcut: ${this.shortcut} (success: ${this.isRegistered})`);
    } catch (e) {
      console.warn(`[hotkey] Failed to register global shortcut ${this.shortcut}:`, e);
    }
  }

  unregister() {
    if (this.isRegistered) {
      globalShortcut.unregister(this.shortcut);
      this.isRegistered = false;
    }
  }
}

module.exports = HotkeyManager;
