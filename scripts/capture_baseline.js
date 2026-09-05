/**
 * Visual Baseline Capture Script for Phase 7.1
 * Launches headless Electron, captures Companion and Diagnostics views, and exits.
 */
const { app, BrowserWindow } = require('electron');
const path = require('path');
const fs = require('fs');

const ARTIFACT_DIR = 'C:\\Users\\Lunafiah\\.gemini\\antigravity-ide\\brain\\f19551b2-1938-46f3-ac31-8ca8acb1cd8c';
const DOCS_DIR = path.join(__dirname, '..', 'docs', 'screenshots');

if (!fs.existsSync(DOCS_DIR)) {
  fs.mkdirSync(DOCS_DIR, { recursive: true });
}

app.whenReady().then(async () => {
  const win = new BrowserWindow({
    width: 1280,
    height: 800,
    show: false,
    webPreferences: {
      preload: path.join(__dirname, '..', 'electron', 'preload', 'preload.js'),
      contextIsolation: true,
      nodeIntegration: false
    }
  });

  const indexPath = path.join(__dirname, '..', 'electron', 'renderer', 'index.html');
  await win.loadFile(indexPath);

  // 1. Cleanly remove splash and disable animations for reliable capture
  await win.webContents.executeJavaScript(`
    (() => {
      const splash = document.getElementById('splash');
      if (splash) splash.remove();

      const style = document.createElement('style');
      style.id = 'disable-anim-for-test';
      style.innerHTML = '* { transition: none !important; animation: none !important; }';
      document.head.appendChild(style);
    })()
  `);

  // Discard initial frame buffer, wait brief tick, then capture Companion Baseline
  await win.webContents.capturePage();
  await new Promise(r => setTimeout(r, 300));
  const img1 = await win.webContents.capturePage();
  const png1 = img1.toPNG();
  fs.writeFileSync(path.join(ARTIFACT_DIR, 'phase_7_1_baseline_companion.png'), png1);
  fs.writeFileSync(path.join(DOCS_DIR, 'phase_7_1_baseline_companion.png'), png1);
  console.log('[screenshot] Saved phase_7_1_baseline_companion.png');

  // 2. Open Diagnostics Drawer
  await win.webContents.executeJavaScript(`
    (() => {
      const pane = document.getElementById('debug-pane');
      const backdrop = document.getElementById('diagnostics-backdrop');
      const toggleBtn = document.getElementById('toggle-diagnostics-btn');
      if (pane) pane.classList.add('open');
      if (backdrop) backdrop.classList.add('open');
      if (toggleBtn) toggleBtn.classList.add('active');
    })()
  `);

  // Discard stale frame buffer, wait brief tick, then capture Diagnostics Drawer Baseline
  await win.webContents.capturePage();
  await new Promise(r => setTimeout(r, 300));
  const img2 = await win.webContents.capturePage();
  const png2 = img2.toPNG();
  fs.writeFileSync(path.join(ARTIFACT_DIR, 'phase_7_1_baseline_diagnostics.png'), png2);
  fs.writeFileSync(path.join(DOCS_DIR, 'phase_7_1_baseline_diagnostics.png'), png2);
  console.log('[screenshot] Saved phase_7_1_baseline_diagnostics.png');

  app.quit();
});
