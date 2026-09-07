/**
 * Visual Capture Script for Phase 7.7 Step 3 (Solemn End-of-Life Confirmation Modal)
 * Captures:
 * 1. phase_7_7_end_life_modal.png (Solemn End-of-Life confirmation modal over Settings/Companion room)
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
    width: 1280,
    height: 900,
    show: false,
    webPreferences: {
      preload: path.join(__dirname, '..', 'electron', 'preload', 'preload.js'),
      contextIsolation: true,
      nodeIntegration: false,
    },
  });

  const indexPath = path.join(__dirname, '..', 'electron', 'renderer', 'index.html');
  await win.loadFile(indexPath);

  // Wait 1s for initial scripts
  await new Promise((r) => setTimeout(r, 1000));

  // Disable CSS transitions/animations for crisp deterministic captures & remove splash
  const check = await win.webContents.executeJavaScript(`
    (() => {
      const splash = document.getElementById('splash');
      if (splash) splash.remove();

      const style = document.createElement('style');
      style.id = 'snapshot-overrides';
      style.innerHTML = '* { transition: none !important; animation: none !important; }';
      document.head.appendChild(style);

      if (window.companionSettings) {
        window.companionSettings.openSettings('privacy');
        window.companionSettings.openEndLifeModal();
      } else {
        const modal = document.getElementById('end-life-modal');
        if (modal) modal.classList.add('active');
      }
    })()
  `);

  // Flush paint buffer
  for (let i = 0; i < 3; i++) {
    await win.webContents.capturePage();
    await new Promise((r) => setTimeout(r, 200));
  }

  // Capture End-of-Life Solemn Confirmation interface
  const imgEndLife = await win.webContents.capturePage();
  const endLifeBuf = imgEndLife.toPNG();
  fs.writeFileSync(path.join(DOCS_DIR, 'phase_7_7_end_life_modal.png'), endLifeBuf);
  fs.writeFileSync(path.join(ARTIFACT_DIR, 'phase_7_7_end_life_modal.png'), endLifeBuf);
  console.log('[capture] phase_7_7_end_life_modal.png captured successfully.');

  app.quit();
});
