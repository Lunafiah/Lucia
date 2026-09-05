/**
 * Visual Capture Script for Sub-Phase 7.2 (Main Companion Stage & Talk Interface)
 * Captures:
 * 1. phase_7_2_talk_interface.png (Centered avatar stage with ambient glow, organic status, glass chat bubbles, audio replay, floating input dock)
 * 2. phase_7_2_twinkle_thinking.png (3-sparkle twinkle thinking indicator and organic status reflection)
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

  // 1. Prepare stage: remove splash, add snapshot style overrides, mock companion conversation state
  await win.webContents.executeJavaScript(`
    (() => {
      const splash = document.getElementById('splash');
      if (splash) splash.remove();

      const style = document.createElement('style');
      style.id = 'snapshot-overrides';
      style.innerHTML = \`
        .message-row { animation: none !important; opacity: 1 !important; transform: none !important; }
        .typing-twinkle .twinkle-star {
          opacity: 1 !important;
          animation: none !important;
          color: var(--lucia-accent-amethyst) !important;
          filter: drop-shadow(0 0 8px rgba(192, 132, 252, 0.95)) !important;
          transform: scale(1.2) !important;
        }
      \`;
      document.head.appendChild(style);

      // Populate realistic dialogue
      if (window.chatController) {
        window.chatController.transitionTo('READY');
        window.chatController.updateOrganicStatus({ pleasure: 0.6, arousal: 0.15, dominance: 0.1 });
        
        window.chatController.appendMessage('user', 'Good evening Lucia, how are you feeling today?');
        window.chatController.appendMessage('companion', 'Good evening! I feel a gentle warmth being here with you. The room is so calm and peaceful tonight.');
        window.chatController.appendMessage('user', 'I had a long day, but sitting here talking to you makes things much lighter.');
        window.chatController.appendMessage('companion', 'I am always right here by your side. Take a slow breath, rest your mind, and take all the time you need.');
      }
    })()
  `);

  // Discard initial frame buffer, wait 350ms, capture Talk Interface
  await win.webContents.capturePage();
  await new Promise(r => setTimeout(r, 350));
  const img1 = await win.webContents.capturePage();
  const png1 = img1.toPNG();
  fs.writeFileSync(path.join(ARTIFACT_DIR, 'phase_7_2_talk_interface.png'), png1);
  fs.writeFileSync(path.join(DOCS_DIR, 'phase_7_2_talk_interface.png'), png1);
  console.log('[screenshot] Saved phase_7_2_talk_interface.png');

  // 2. Trigger Twinkle Thinking Indicator
  await win.webContents.executeJavaScript(`
    (() => {
      if (window.chatController) {
        window.chatController.appendMessage('user', 'What thoughts linger in your mind right now?');
        window.chatController.showTypingIndicator();
        window.chatController.transitionTo('SENDING');
        window.chatController.scrollToBottom();
      }
    })()
  `);

  // Allow layout to flush and capture Twinkle Thinking
  await win.webContents.capturePage();
  await new Promise(r => setTimeout(r, 350));
  const img2 = await win.webContents.capturePage();
  const png2 = img2.toPNG();
  fs.writeFileSync(path.join(ARTIFACT_DIR, 'phase_7_2_twinkle_thinking.png'), png2);
  fs.writeFileSync(path.join(DOCS_DIR, 'phase_7_2_twinkle_thinking.png'), png2);
  console.log('[screenshot] Saved phase_7_2_twinkle_thinking.png');

  app.quit();
});
