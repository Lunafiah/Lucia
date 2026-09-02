/**
 * Unit tests for TrayManager, HotkeyManager, and MascotWindowManager.
 */

const TrayManager = require('../main/tray-manager');
const HotkeyManager = require('../main/hotkey-manager');

// Mock electron modules
jest.mock('electron', () => {
  const mockTrayInstance = {
    setToolTip: jest.fn(),
    setContextMenu: jest.fn(),
    on: jest.fn(),
    destroy: jest.fn(),
    isDestroyed: jest.fn().mockReturnValue(false),
  };

  return {
    app: {
      quit: jest.fn(),
      isQuitting: false,
    },
    Tray: jest.fn().mockImplementation(() => mockTrayInstance),
    Menu: {
      buildFromTemplate: jest.fn((template) => template),
    },
    nativeImage: {
      createFromPath: jest.fn().mockReturnValue({ isEmpty: () => true }),
      createEmpty: jest.fn().mockReturnValue({}),
    },
    globalShortcut: {
      register: jest.fn().mockReturnValue(true),
      unregister: jest.fn(),
    },
  };
});

describe('Phase 6: Desktop Presence Modes', () => {
  let mockWindow;

  beforeEach(() => {
    mockWindow = {
      isVisible: jest.fn().mockReturnValue(true),
      hide: jest.fn(),
      show: jest.fn(),
      focus: jest.fn(),
      isDestroyed: jest.fn().mockReturnValue(false),
    };
  });

  test('TrayManager toggles window visibility on action', () => {
    const tray = new TrayManager(mockWindow);
    tray.init();

    expect(tray.tray).toBeDefined();

    // Toggle window when visible -> should hide
    tray.toggleMainWindow();
    expect(mockWindow.hide).toHaveBeenCalled();

    // Toggle window when hidden -> should show & focus
    mockWindow.isVisible.mockReturnValue(false);
    tray.toggleMainWindow();
    expect(mockWindow.show).toHaveBeenCalled();
    expect(mockWindow.focus).toHaveBeenCalled();
  });

  test('HotkeyManager registers and unregisters global shortcut', () => {
    const { globalShortcut } = require('electron');
    const hotkey = new HotkeyManager(mockWindow, 'CommandOrControl+Shift+L');

    hotkey.register();
    expect(globalShortcut.register).toHaveBeenCalledWith(
      'CommandOrControl+Shift+L',
      expect.any(Function)
    );
    expect(hotkey.isRegistered).toBe(true);

    hotkey.unregister();
    expect(globalShortcut.unregister).toHaveBeenCalledWith('CommandOrControl+Shift+L');
    expect(hotkey.isRegistered).toBe(false);
  });
});
