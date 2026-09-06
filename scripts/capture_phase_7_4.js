/**
 * Visual Capture Script for Sub-Phase 7.4 (Desktop Presence & Mascot Mode)
 * Captures:
 * 1. phase_7_4_mascot_dock.png (Desktop Presence floating dock with Presence Menu popover)
 * 2. phase_7_4_quick_talk.png (Quick Talk flyout speech bubble with message input & latest reply)
 */
const { app, BrowserWindow } = require('electron');
const path = require('path');
const fs = require('fs');
const { registerHandlers } = require('../electron/main/ipc-bridge.js');

const ARTIFACT_DIR = 'C:\\Users\\Lunafiah\\.gemini\\antigravity-ide\\brain\\f19551b2-1938-46f3-ac31-8ca8acb1cd8c';
const DOCS_DIR = path.join(__dirname, '..', 'docs', 'screenshots');

if (!fs.existsSync(DOCS_DIR)) {
  fs.mkdirSync(DOCS_DIR, { recursive: true });
}

app.whenReady().then(async () => {
  registerHandlers(8765, true, null);

  const win = new BrowserWindow({
    width: 380,
    height: 540,
    frame: false,
    transparent: true,
    show: false,
    webPreferences: {
      preload: path.join(__dirname, '..', 'electron', 'preload', 'preload.js'),
      contextIsolation: true,
      nodeIntegration: false
    }
  });

  win.webContents.on('console-message', (event, level, message) => {
    console.log('[renderer]', message);
  });

  const indexPath = path.join(__dirname, '..', 'electron', 'renderer', 'index.html');
  await win.loadFile(indexPath, { query: { mode: 'mascot' } });

  // Wait for initial render and scripts initialization
  await new Promise(r => setTimeout(r, 600));

  // 1. Prepare Mascot Mode and open Presence Menu Popover
  await win.webContents.executeJavaScript(`
    (() => {
      try {
        const splash = document.getElementById('splash');
        if (splash) splash.remove();

        document.body.classList.add('mascot-mode');

        const style = document.createElement('style');
        style.id = 'snapshot-overrides';
        style.innerHTML = \`
          * { transition: none !important; animation: none !important; }
          body { background: rgba(14, 12, 28, 0.92) !important; }
          #chat-pane { display: none !important; }
          #avatar-pane { display: flex !important; width: 100vw !important; height: 100vh !important; }
        \`;
        document.head.appendChild(style);

        if (window.chatController) {
          window.chatController.transitionTo('READY');
        }

        if (window.avatarRenderer) {
          window.avatarRenderer.pan = { x: 0, y: 0 };
          window.avatarRenderer.mascotScale = 1.0;
          window.avatarRenderer.resize();
          window.avatarRenderer._updateToolbarPosition();
        }

        const tb = document.getElementById('mascot-toolbar');
        const popover = document.getElementById('mascot-presence-popover');
        const cv = document.getElementById('avatar-canvas');
        const st = document.querySelector('.avatar-stage-container');
        if (tb) console.log('[rect tb]', JSON.stringify(tb.getBoundingClientRect()));
        if (popover) console.log('[rect pop]', JSON.stringify(popover.getBoundingClientRect()));
        if (cv) console.log('[rect cv]', JSON.stringify(cv.getBoundingClientRect()));
        if (st) console.log('[rect st]', JSON.stringify(st.getBoundingClientRect()));

        const menuBtn = document.getElementById('mascot-presence-menu-btn');
        const toolbar = document.getElementById('mascot-toolbar');
        if (popover && menuBtn) {
          popover.style.display = 'flex';
          menuBtn.classList.add('active');
          if (toolbar) toolbar.classList.add('has-active-popup');
        }
        console.log('[snapshot] Presence menu opened successfully');
      } catch (e) {
        console.error('[snapshot error]', e);
      }
    })()
  `);

  // Discard initial frame, wait 400ms, capture Mascot Dock & Popover
  await win.webContents.capturePage();
  await new Promise(r => setTimeout(r, 400));
  const img1 = await win.webContents.capturePage();
  const png1 = img1.toPNG();
  fs.writeFileSync(path.join(ARTIFACT_DIR, 'phase_7_4_mascot_dock.png'), png1);
  fs.writeFileSync(path.join(DOCS_DIR, 'phase_7_4_mascot_dock.png'), png1);
  console.log('[screenshot] Saved phase_7_4_mascot_dock.png');

  // 2. Switch to Quick Talk Flyout Speech Bubble
  await win.webContents.executeJavaScript(`
    (() => {
      try {
        const popover = document.getElementById('mascot-presence-popover');
        const menuBtn = document.getElementById('mascot-presence-menu-btn');
        if (popover) popover.style.display = 'none';
        if (menuBtn) menuBtn.classList.remove('active');

        const flyout = document.getElementById('mascot-quick-talk-flyout');
        const quickTalkBtn = document.getElementById('mascot-quick-talk-btn');
        const toolbar = document.getElementById('mascot-toolbar');
        const replyBox = document.getElementById('mascot-quick-talk-latest');
        const replyText = document.getElementById('mascot-quick-talk-reply-text');
        const input = document.getElementById('mascot-quick-talk-input');

        if (flyout && quickTalkBtn) {
          flyout.style.display = 'flex';
          quickTalkBtn.classList.add('active');
          if (toolbar) toolbar.classList.add('has-active-popup');
        }

        if (replyBox && replyText) {
          replyText.textContent = "There is a gentle rhythm in the quiet tonight. I am right here with you.";
          replyBox.style.display = 'block';
        }

        if (input) {
          input.value = "How are you feeling right now?";
        }

        if (window.avatarRenderer) {
          window.avatarRenderer._updateToolbarPosition();
        }
        console.log('[snapshot] Quick talk flyout opened successfully');
      } catch (e) {
        console.error('[snapshot error 2]', e);
      }
    })()
  `);

  // Discard frame, wait 400ms, capture Quick Talk Flyout
  await win.webContents.capturePage();
  await new Promise(r => setTimeout(r, 400));
  const img2 = await win.webContents.capturePage();
  const png2 = img2.toPNG();
  fs.writeFileSync(path.join(ARTIFACT_DIR, 'phase_7_4_quick_talk.png'), png2);
  fs.writeFileSync(path.join(DOCS_DIR, 'phase_7_4_quick_talk.png'), png2);
  console.log('[screenshot] Saved phase_7_4_quick_talk.png');

  app.quit();
});
