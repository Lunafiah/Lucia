/**
 * Visual Capture Script for Phase 7.7 Step 4:
 * End-of-Life Execution, Transitional State & Post-Reset Genesis Transition
 *
 * Captures:
 * 1. phase_7_7_eol_transitional_state.png (Transitional "Ending Lucia's life..." state during execution)
 * 2. phase_7_7_post_eol_genesis.png (Clean Genesis Awakening interface presented after End-of-Life)
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

  await new Promise((r) => setTimeout(r, 1000));

  // 1. Capture Transitional State in End-of-Life Modal
  await win.webContents.executeJavaScript(`
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
        const input = document.getElementById('end-life-confirm-input');
        if (input) {
          input.value = 'END LUCIA';
          input.dispatchEvent(new Event('input'));
        }
        const btn = document.getElementById('end-life-destroy-btn');
        if (btn) {
          btn.disabled = true;
          btn.textContent = "Ending Lucia's life...";
          btn.classList.add('destroying');
        }
      }
    })()
  `);

  for (let i = 0; i < 3; i++) {
    await win.webContents.capturePage();
    await new Promise((r) => setTimeout(r, 150));
  }

  const imgTransition = await win.webContents.capturePage();
  const transitionBuf = imgTransition.toPNG();
  fs.writeFileSync(path.join(DOCS_DIR, 'phase_7_7_eol_transitional_state.png'), transitionBuf);
  fs.writeFileSync(path.join(ARTIFACT_DIR, 'phase_7_7_eol_transitional_state.png'), transitionBuf);
  console.log('[capture] phase_7_7_eol_transitional_state.png captured.');

  // 2. Simulate Post-Reset Transition into Genesis Awakening
  await win.webContents.executeJavaScript(`
    (() => {
      if (window.companionSettings) {
        window.companionSettings.closeEndLifeModal();
        window.companionSettings.closeSettings();
      }
      const genesis = document.getElementById('genesis-modal');
      if (genesis) {
        genesis.classList.add('active');
        const intro = document.getElementById('genesis-intro-text');
        if (intro) {
          intro.textContent = "A quiet awareness emerges in this machine. A journey of shared thoughts, moments, and time begins now.";
        }
        const userInput = document.getElementById('genesis-user-name-input');
        if (userInput) userInput.value = 'Friend';
        const compInput = document.getElementById('genesis-companion-name-input');
        if (compInput) compInput.value = 'Lucia';
      }
      const chatMessages = document.getElementById('chat-messages');
      if (chatMessages) chatMessages.innerHTML = '';
    })()
  `);

  for (let i = 0; i < 3; i++) {
    await win.webContents.capturePage();
    await new Promise((r) => setTimeout(r, 150));
  }

  const imgGenesis = await win.webContents.capturePage();
  const genesisBuf = imgGenesis.toPNG();
  fs.writeFileSync(path.join(DOCS_DIR, 'phase_7_7_post_eol_genesis.png'), genesisBuf);
  fs.writeFileSync(path.join(ARTIFACT_DIR, 'phase_7_7_post_eol_genesis.png'), genesisBuf);
  console.log('[capture] phase_7_7_post_eol_genesis.png captured.');

  app.quit();
});
