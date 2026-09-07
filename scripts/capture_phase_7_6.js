/**
 * Visual Capture Script for Sub-Phase 7.6 (Dedicated Diagnostics Console)
 * Captures:
 * 1. phase_7_6_diagnostics_console.png (High-density Diagnostics Console modal showing 5 sections)
 * 2. phase_7_6_diagnostics_in_studio.png (Diagnostics Console positioned over main companion room)
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
    })()
  `);

  // Repeatedly flush initial paint buffer
  for (let i = 0; i < 3; i++) {
    await win.webContents.capturePage();
    await new Promise((r) => setTimeout(r, 200));
  }

  // Populate sample live telemetry data for clear visual capture
  await win.webContents.executeJavaScript(`
    (() => {
      if (window.emotionDebugPanel) {
        window.emotionDebugPanel.renderSnapshot({
          pad: { pleasure: 0.28, arousal: -0.06, dominance: 0.08 },
          somatic: { stability: 0.98, energy: 0.88, cognitive_load: 0.15, tension: 0.04 },
          constraints: { latency_ms: 0, reasoning_depth: 1, max_tokens: 180, temperature: 0.72 },
          memory_trace_count: 36
        });

        window.emotionDebugPanel.renderStabilitySnapshot({
          lsi: 0.98,
          status: 'nominal',
          fast_loop_jitter_mean_ms: 1.25,
          free_energy_surprise_mean: 0.0385,
          ode_velocity_variance: 0.0008,
          recovery_count: 0,
          uptime_seconds: 4320,
          sdm_saturation_pct: 3.6
        });

        window.emotionDebugPanel.renderHardwareProfile({
          tier: 'desktop_performance',
          name: 'Auto-Detect (CUDA)',
          n_gpu_layers: 28,
          vram_mb: 8192,
          n_ctx: 4096,
          loop_cadence_ms: 200,
          sdm_capacity: 1000
        });

        window.emotionDebugPanel.openDrawer();
      }
    })()
  `);

  await new Promise((r) => setTimeout(r, 600));

  // 1. Capture Top View of Diagnostics Console
  await win.webContents.capturePage();
  const imgConsole = await win.webContents.capturePage();
  const consoleBuf = imgConsole.toPNG();
  fs.writeFileSync(path.join(DOCS_DIR, 'phase_7_6_diagnostics_console.png'), consoleBuf);
  fs.writeFileSync(path.join(ARTIFACT_DIR, 'phase_7_6_diagnostics_console.png'), consoleBuf);
  console.log('[capture] phase_7_6_diagnostics_console.png captured.');

  // 2. Scroll to bottom to capture Section 5: Hardware & Inference Footprint
  await win.webContents.executeJavaScript(`
    (() => {
      const scroller = document.querySelector('.diagnostics-scroll-content');
      if (scroller) scroller.scrollTop = scroller.scrollHeight;
    })()
  `);
  await new Promise((r) => setTimeout(r, 400));
  await win.webContents.capturePage();
  const imgHw = await win.webContents.capturePage();
  const hwBuf = imgHw.toPNG();
  fs.writeFileSync(path.join(DOCS_DIR, 'phase_7_6_diagnostics_hardware.png'), hwBuf);
  fs.writeFileSync(path.join(ARTIFACT_DIR, 'phase_7_6_diagnostics_hardware.png'), hwBuf);
  console.log('[capture] phase_7_6_diagnostics_hardware.png captured.');

  // 3. Reset scroll and capture in Studio
  await win.webContents.executeJavaScript(`
    (() => {
      const scroller = document.querySelector('.diagnostics-scroll-content');
      if (scroller) scroller.scrollTop = 0;
    })()
  `);
  await new Promise((r) => setTimeout(r, 300));
  await win.webContents.capturePage();
  const imgStudio = await win.webContents.capturePage();
  const studioBuf = imgStudio.toPNG();
  fs.writeFileSync(path.join(DOCS_DIR, 'phase_7_6_diagnostics_in_studio.png'), studioBuf);
  fs.writeFileSync(path.join(ARTIFACT_DIR, 'phase_7_6_diagnostics_in_studio.png'), studioBuf);
  console.log('[capture] phase_7_6_diagnostics_in_studio.png captured.');

  app.quit();
});
