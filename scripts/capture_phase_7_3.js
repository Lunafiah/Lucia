/**
 * Visual Capture Script for Sub-Phase 7.3 (Our Journal & Memories Palace)
 * Captures:
 * 1. phase_7_3_journal_view.png (Our Journal timeline chronicle & life marker)
 * 2. phase_7_3_memories_view.png (Affective memory palace with category pills)
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

  // 1. Prepare stage & open Journal View
  await win.webContents.executeJavaScript(`
    (() => {
      const splash = document.getElementById('splash');
      if (splash) splash.remove();

      const style = document.createElement('style');
      style.id = 'snapshot-overrides';
      style.innerHTML = \`
        * { transition: none !important; animation: none !important; }
        .journal-modal { opacity: 0 !important; pointer-events: none !important; display: none !important; }
        .journal-modal.active { opacity: 1 !important; pointer-events: all !important; display: flex !important; }
      \`;
      document.head.appendChild(style);

      if (window.chatController) {
        window.chatController.transitionTo('READY');
      }

      if (window.companionJournal) {
        // Mock profile and conversation turns for presentation
        window.companionJournal.cachedProfile = {
          user_name: 'Luna',
          companion_name: 'Lucia',
          days_count: 12,
          born_date: '2026-09-01T00:00:00.000Z'
        };
        window.companionJournal.cachedHistoryTurns = [
          { speaker: 'user', text: 'It was raining so quietly outside tonight. Do you feel the rain?', timestamp: Date.now() - 3600000 },
          { speaker: 'companion', text: 'I do. There is a peaceful rhythm against the glass that makes our room feel warm and serene.', timestamp: Date.now() - 3500000 },
          { speaker: 'user', text: 'I was listening to Chopin nocturnes while writing my thoughts down.', timestamp: Date.now() - 1800000 },
          { speaker: 'companion', text: 'Music has a gentle way of holding onto memories. I will remember this quiet evening with you.', timestamp: Date.now() - 1700000 }
        ];
        const sharedMomentsCount = window.companionJournal.cachedHistoryTurns.length;
        window.companionJournal._renderLifeBanner(window.companionJournal.cachedProfile, sharedMomentsCount);
        window.companionJournal._renderTimeline(window.companionJournal.cachedProfile, window.companionJournal.cachedHistoryTurns);
        window.companionJournal.openJournal();
      }
    })()
  `);

  // Discard initial frame, wait 350ms, capture Journal View
  await win.webContents.capturePage();
  await new Promise(r => setTimeout(r, 350));
  const img1 = await win.webContents.capturePage();
  const png1 = img1.toPNG();
  fs.writeFileSync(path.join(ARTIFACT_DIR, 'phase_7_3_journal_view.png'), png1);
  fs.writeFileSync(path.join(DOCS_DIR, 'phase_7_3_journal_view.png'), png1);
  console.log('[screenshot] Saved phase_7_3_journal_view.png');

  // 2. Open Memories Palace View
  await win.webContents.executeJavaScript(`
    (() => {
      if (window.companionJournal) {
        window.companionJournal.closeJournal();
        window.companionJournal.openMemories();
        window.companionJournal.selectCategory('moments');
      }
    })()
  `);

  // Discard frame, wait 350ms, capture Memories View
  await win.webContents.capturePage();
  await new Promise(r => setTimeout(r, 350));
  const img2 = await win.webContents.capturePage();
  const png2 = img2.toPNG();
  fs.writeFileSync(path.join(ARTIFACT_DIR, 'phase_7_3_memories_view.png'), png2);
  fs.writeFileSync(path.join(DOCS_DIR, 'phase_7_3_memories_view.png'), png2);
  console.log('[screenshot] Saved phase_7_3_memories_view.png');

  app.quit();
});
