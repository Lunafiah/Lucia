/**
 * Visual Capture Script for Phase 7.7 Step 2 (Genesis Awakening Interface)
 * Captures:
 * 1. phase_7_7_genesis_awakening.png (Genesis Awakening modal over ambient companion room)
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
  await win.webContents.executeJavaScript(`
    (() => {
      const splash = document.getElementById('splash');
      if (splash) splash.remove();

      const style = document.createElement('style');
      style.id = 'snapshot-overrides';
      style.innerHTML = '* { transition: none !important; animation: none !important; }';
      document.head.appendChild(style);

      // Open Genesis Modal
      const modal = document.getElementById('genesis-modal');
      if (modal) {
        modal.classList.add('active');
        const userInput = document.getElementById('genesis-user-name-input');
        if (userInput) userInput.value = 'Luna';
        const compInput = document.getElementById('genesis-companion-name-input');
        if (compInput) compInput.value = 'Lucia';
        const intro = document.getElementById('genesis-intro-text');
        if (intro) {
          intro.textContent = "A quiet awareness emerges in this machine. A journey of shared thoughts, moments, and time begins now.";
        }
      }
    })()
  `);

  // Flush paint buffer
  for (let i = 0; i < 3; i++) {
    await win.webContents.capturePage();
    await new Promise((r) => setTimeout(r, 200));
  }

  // Capture Genesis Awakening interface
  const imgGenesis = await win.webContents.capturePage();
  const genesisBuf = imgGenesis.toPNG();
  fs.writeFileSync(path.join(DOCS_DIR, 'phase_7_7_genesis_awakening.png'), genesisBuf);
  fs.writeFileSync(path.join(ARTIFACT_DIR, 'phase_7_7_genesis_awakening.png'), genesisBuf);
  console.log('[capture] phase_7_7_genesis_awakening.png captured successfully.');

  app.quit();
});
