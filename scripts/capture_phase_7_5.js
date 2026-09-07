/**
 * Visual Capture Script for Sub-Phase 7.5 (Categorized Settings System)
 * Captures:
 * 1. phase_7_5_settings_appearance.png (Appearance & Attire Asset Pack tab)
 * 2. phase_7_5_settings_performance.png (Performance & Hardware Profile tab)
 * 3. phase_7_5_settings_privacy.png (Privacy & Life with Local Edge Notice)
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
    width: 1240,
    height: 860,
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
  await win.webContents.executeJavaScript(`
    (() => {
      const splash = document.getElementById('splash');
      if (splash) splash.remove();

      const style = document.createElement('style');
      style.id = 'snapshot-overrides';
      style.innerHTML = '* { transition: none !important; animation: none !important; }';
      document.head.appendChild(style);
    })()
  `);
  
  // Repeatedly flush initial paint buffer
  for (let i = 0; i < 3; i++) {
    await win.webContents.capturePage();
    await new Promise((r) => setTimeout(r, 200));
  }

  // 1. Appearance Tab
  await win.webContents.executeJavaScript(`
    (() => {
      if (window.companionSettings) {
        window.companionSettings.openSettings('appearance');
      }
    })()
  `);
  await new Promise((r) => setTimeout(r, 500));
  await win.webContents.capturePage(); // flush
  const imgAppearance = await win.webContents.capturePage();
  const appearanceBuf = imgAppearance.toPNG();
  fs.writeFileSync(path.join(DOCS_DIR, 'phase_7_5_settings_appearance.png'), appearanceBuf);
  fs.writeFileSync(path.join(ARTIFACT_DIR, 'phase_7_5_settings_appearance.png'), appearanceBuf);
  console.log('[capture] phase_7_5_settings_appearance.png captured.');

  // 2. Performance Tab
  await win.webContents.executeJavaScript(`
    (() => {
      if (window.companionSettings) {
        window.companionSettings.switchTab('performance');
      }
    })()
  `);
  await new Promise((r) => setTimeout(r, 500));
  await win.webContents.capturePage(); // flush
  const imgPerformance = await win.webContents.capturePage();
  const perfBuf = imgPerformance.toPNG();
  fs.writeFileSync(path.join(DOCS_DIR, 'phase_7_5_settings_performance.png'), perfBuf);
  fs.writeFileSync(path.join(ARTIFACT_DIR, 'phase_7_5_settings_performance.png'), perfBuf);
  console.log('[capture] phase_7_5_settings_performance.png captured.');

  // 3. Privacy & Life Tab
  await win.webContents.executeJavaScript(`
    (() => {
      if (window.companionSettings) {
        window.companionSettings.switchTab('privacy');
      }
    })()
  `);
  await new Promise((r) => setTimeout(r, 500));
  await win.webContents.capturePage(); // flush
  const imgPrivacy = await win.webContents.capturePage();
  const privacyBuf = imgPrivacy.toPNG();
  fs.writeFileSync(path.join(DOCS_DIR, 'phase_7_5_settings_privacy.png'), privacyBuf);
  fs.writeFileSync(path.join(ARTIFACT_DIR, 'phase_7_5_settings_privacy.png'), privacyBuf);
  console.log('[capture] phase_7_5_settings_privacy.png captured.');

  app.quit();
});
