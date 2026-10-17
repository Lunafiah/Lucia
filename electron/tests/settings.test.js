/**
 * Sub-Phase 7.5: Categorized Settings System Test Suite
 *
 * Requirements & Invariants:
 * 1. "How I want Lucia to live with me on this machine": Environmental/acoustics/resource tuning.
 * 2. Appearance vs. Identity: Appearance Asset / Attire pack selection (zero character persona mutation).
 * 3. Clear Active Talk View Non-Mutation Chain (Talk DOM cleared, Journal/SDM/PAD untouched).
 * 4. Modal lifecycle, 6-tab navigation, live preview, and automatic persistence.
 * @jest-environment jsdom
 */

const { CompanionSettings } = require('../renderer/settings/settings');

describe('CompanionSettings Controller (Phase 7.5)', () => {
  let settings;
  let mockAvatarRenderer;
  let mockChatController;
  let mockCompanionJournal;
  let mockLuciaAPI;

  beforeEach(() => {
    // Setup localStorage mock
    let store = {};
    const mockStorage = {
      getItem: jest.fn((key) => store[key] || null),
      setItem: jest.fn((key, val) => {
        store[key] = String(val);
      }),
      removeItem: jest.fn((key) => {
        delete store[key];
      }),
      clear: jest.fn(() => {
        store = {};
      }),
    };
    Object.defineProperty(window, 'localStorage', {
      value: mockStorage,
      writable: true,
      configurable: true,
    });
    global.localStorage = mockStorage;

    // Construct full DOM representation matching index.html
    document.body.innerHTML = `
      <button id="open-settings-btn"></button>
      <button id="toggle-diagnostics-btn"></button>
      <div id="debug-pane" class="debug-pane diagnostics-drawer"></div>

      <div id="settings-modal" class="journal-modal">
        <div class="settings-modal-card">
          <div class="settings-modal-header">
            <h2>Settings</h2>
            <button id="close-settings-btn"></button>
          </div>

          <div class="settings-modal-layout">
            <nav class="settings-sidebar">
              <button id="settings-tab-btn-appearance" class="settings-tab-btn active" data-tab="appearance"></button>
              <button id="settings-tab-btn-voice" class="settings-tab-btn" data-tab="voice"></button>
              <button id="settings-tab-btn-presence" class="settings-tab-btn" data-tab="presence"></button>
              <button id="settings-tab-btn-privacy" class="settings-tab-btn" data-tab="privacy"></button>
              <button id="settings-tab-btn-performance" class="settings-tab-btn" data-tab="performance"></button>
              <button id="settings-tab-btn-advanced" class="settings-tab-btn" data-tab="advanced"></button>
            </nav>

            <main class="settings-content">
              <!-- Appearance -->
              <section id="settings-pane-appearance" class="settings-pane active">
                <select id="settings-avatar-engine-select">
                  <option value="canvas">Canvas</option>
                  <option value="sprites">Sprites</option>
                  <option value="live2d">Live2D</option>
                  <option value="vrm">VRM</option>
                </select>
                <select id="settings-avatar-model-select">
                  <option value="default">Default Lucia Attire</option>
                </select>
                <input type="checkbox" id="settings-gaze-tracking-toggle" checked />
                <input type="checkbox" id="settings-ambient-blinking-toggle" checked />
              </section>

              <!-- Voice -->
              <section id="settings-pane-voice" class="settings-pane">
                <input type="range" id="settings-volume-slider" min="0" max="100" value="85" />
                <span id="settings-volume-val">85%</span>
                <select id="settings-voice-model-select">
                  <option value="default">Default</option>
                </select>
                <select id="settings-output-device-select">
                  <option value="default">Default Speaker</option>
                </select>
                <select id="settings-input-device-select">
                  <option value="default">Default Mic</option>
                </select>
                <input type="range" id="settings-vad-sensitivity" min="8" max="30" value="14" />
                <span id="settings-vad-val">14</span>
              </section>

              <!-- Presence -->
              <section id="settings-pane-presence" class="settings-pane">
                <input type="checkbox" id="settings-mascot-startup-toggle" />
                <select id="settings-mascot-preset-select">
                  <option value="small">Small</option>
                  <option value="normal" selected>Normal</option>
                  <option value="comfort">Comfort</option>
                </select>
                <input type="range" id="settings-mascot-opacity" min="0.3" max="1" step="0.05" value="1" />
                <span id="settings-opacity-val">100%</span>
                <input type="checkbox" id="settings-mascot-autohide-toggle" />
                <button id="settings-launch-mascot-btn"></button>
              </section>

              <!-- Privacy & Life -->
              <section id="settings-pane-privacy" class="settings-pane">
                <button id="settings-export-data-btn"></button>
                <button id="settings-clear-chat-btn"></button>
                <button id="settings-end-life-btn"></button>
              </section>

              <!-- Performance -->
              <section id="settings-pane-performance" class="settings-pane">
                <div id="settings-host-device">Host CPU</div>
                <div id="settings-cuda-status">Disabled</div>
                <div id="settings-vram-detected">0 MB</div>
                <div id="settings-cpu-backend">CPU</div>
                <select id="settings-fps-select">
                  <option value="60">60 FPS</option>
                  <option value="30">30 FPS</option>
                  <option value="15">15 FPS</option>
                </select>
                <input type="checkbox" id="settings-throttle-bg-toggle" checked />
              </section>

              <!-- Advanced -->
              <section id="settings-pane-advanced" class="settings-pane">
                <input type="checkbox" id="settings-dev-mode-toggle" />
                <span id="settings-api-status-text">127.0.0.1:8765</span>
                <button id="settings-open-diagnostics-btn"></button>
              </section>
            </main>
          </div>

          <footer class="settings-modal-footer">
            <span id="settings-sync-status-text">All settings synchronized</span>
            <button id="done-settings-btn"></button>
          </footer>
        </div>
      </div>

      <!-- Talk stream feed for non-mutation testing -->
      <div id="talk-stream" class="talk-stream">
        <div class="message-bubble">Hello Lucia!</div>
        <div class="message-bubble">Peaceful evening.</div>
      </div>
    `;

    // Mocks for collaborating systems
    mockAvatarRenderer = {
      setEngine: jest.fn(),
      setGazeTracking: jest.fn(),
      setAmbientBlinking: jest.fn(),
      setTargetFps: jest.fn(),
      setZoomPreset: jest.fn(),
    };
    window.avatarRenderer = mockAvatarRenderer;

    mockChatController = {
      clearScreen: jest.fn(() => {
        const stream = document.getElementById('talk-stream');
        if (stream) stream.innerHTML = '';
      }),
      volumeSlider: { value: '0.85' },
    };
    window.chatController = mockChatController;

    mockCompanionJournal = {
      exportJournal: jest.fn(),
      historyMilestonesCount: 14,
    };
    window.companionJournal = mockCompanionJournal;

    mockLuciaAPI = {
      window: {
        toggleMascot: jest.fn(),
      },
      system: {
        getHardwareCapabilities: jest.fn().mockResolvedValue({
          device_name: 'NVIDIA RTX 4060',
          cuda_available: true,
          vram_mb: 8192,
          backend: 'cuda',
          cpu_threads: 16,
          cpu_architecture: 'AMD64',
        }),
        getProfile: jest.fn().mockResolvedValue({
          device_name: 'NVIDIA RTX 4060',
          cuda_available: true,
          vram_mb: 8192,
          backend: 'cuda',
          cpu_threads: 16,
          cpu_architecture: 'AMD64',
        }),
      },
      models: {
        getAvatars: jest.fn().mockResolvedValue({
          sprites: ['columbina'],
          live2d: ['HoshinoAi'],
          vrm: ['lucia.vrm'],
        }),
        getVoices: jest.fn().mockResolvedValue({
          models: [{ name: 'default' }, { name: 'VaresaGIJP' }],
          active_model: 'default',
        }),
      },
    };
    window.lucia = mockLuciaAPI;

    // Fetch mock for endpoints
    global.fetch = jest.fn().mockImplementation((url) => {
      if (url.includes('/health')) {
        return Promise.resolve({ ok: true });
      }
      if (url.includes('/voice/select-model')) {
        return Promise.resolve({ ok: true, json: () => Promise.resolve({ status: 'ok' }) });
      }
      return Promise.resolve({ ok: true, json: () => Promise.resolve({}) });
    });

    settings = new CompanionSettings();
  });

  afterEach(() => {
    jest.clearAllMocks();
  });

  test('Test 1: Modal Lifecycle & Accessibility (Open, Close, Escape)', () => {
    const modal = document.getElementById('settings-modal');
    expect(modal.classList.contains('active')).toBe(false);

    // Open via open button
    document.getElementById('open-settings-btn').click();
    expect(modal.classList.contains('active')).toBe(true);

    // Close via close button
    document.getElementById('close-settings-btn').click();
    expect(modal.classList.contains('active')).toBe(false);

    // Open and close via Done button
    settings.openSettings();
    expect(modal.classList.contains('active')).toBe(true);
    document.getElementById('done-settings-btn').click();
    expect(modal.classList.contains('active')).toBe(false);

    // Close via Escape key
    settings.openSettings();
    expect(modal.classList.contains('active')).toBe(true);
    window.dispatchEvent(new KeyboardEvent('keydown', { key: 'Escape' }));
    expect(modal.classList.contains('active')).toBe(false);
  });

  test('Test 2: Tab Navigation across all 6 categories', () => {
    settings.openSettings();

    const tabs = ['appearance', 'voice', 'presence', 'privacy', 'performance', 'advanced'];

    tabs.forEach((tabKey) => {
      const tabBtn = document.getElementById(`settings-tab-btn-${tabKey}`);
      tabBtn.click();

      expect(settings.activeTab).toBe(tabKey);
      expect(tabBtn.classList.contains('active')).toBe(true);

      const pane = document.getElementById(`settings-pane-${tabKey}`);
      expect(pane.classList.contains('active')).toBe(true);

      // Other panes should not be active
      tabs
        .filter((k) => k !== tabKey)
        .forEach((otherKey) => {
          const otherPane = document.getElementById(`settings-pane-${otherKey}`);
          expect(otherPane.classList.contains('active')).toBe(false);
        });
    });
  });

  test('Test 3: Appearance Controls & Asset Semantics (Zero Identity Mutation)', async () => {
    settings.openSettings('appearance');
    await settings.loadAvatarAssets();

    const engineSelect = document.getElementById('settings-avatar-engine-select');
    const assetSelect = document.getElementById('settings-avatar-model-select');
    const gazeToggle = document.getElementById('settings-gaze-tracking-toggle');
    const blinkToggle = document.getElementById('settings-ambient-blinking-toggle');

    // Switch engine to sprites
    engineSelect.value = 'sprites';
    engineSelect.dispatchEvent(new Event('change'));

    expect(localStorage.setItem).toHaveBeenCalledWith('lucia_avatar_engine', 'sprites');
    expect(mockAvatarRenderer.setEngine).toHaveBeenCalledWith('sprites', expect.any(String));

    // Select attire asset
    assetSelect.value = 'columbina';
    assetSelect.dispatchEvent(new Event('change'));
    expect(localStorage.setItem).toHaveBeenCalledWith('lucia_avatar_model', 'columbina');
    expect(mockAvatarRenderer.setEngine).toHaveBeenCalledWith('sprites', 'columbina');

    // Toggle Gaze Tracking
    gazeToggle.checked = false;
    gazeToggle.dispatchEvent(new Event('change'));
    expect(localStorage.setItem).toHaveBeenCalledWith('lucia_gaze_enabled', 'false');
    expect(mockAvatarRenderer.setGazeTracking).toHaveBeenCalledWith(false);

    // Toggle Ambient Blinking
    blinkToggle.checked = false;
    blinkToggle.dispatchEvent(new Event('change'));
    expect(localStorage.setItem).toHaveBeenCalledWith('lucia_blinking_enabled', 'false');
    expect(mockAvatarRenderer.setAmbientBlinking).toHaveBeenCalledWith(false);
  });

  test('Test 4: Voice & Audio Controls (Timbre Filter as Audio Asset)', async () => {
    settings.openSettings('voice');
    await settings.loadVoiceTimbres();

    const volSlider = document.getElementById('settings-volume-slider');
    const timbreSelect = document.getElementById('settings-voice-model-select');

    // Master volume slider
    volSlider.value = '70';
    volSlider.dispatchEvent(new Event('input'));
    expect(document.getElementById('settings-volume-val').textContent).toBe('70%');
    expect(localStorage.setItem).toHaveBeenCalledWith('lucia_master_volume', '70');

    // Vocal Timbre (RVC Audio Filter) selection
    timbreSelect.value = 'VaresaGIJP';
    timbreSelect.dispatchEvent(new Event('change'));
    expect(localStorage.setItem).toHaveBeenCalledWith('lucia_voice_timbre', 'VaresaGIJP');
    expect(global.fetch).toHaveBeenCalledWith(
      'http://127.0.0.1:8765/voice/select-model',
      expect.objectContaining({
        method: 'POST',
        body: JSON.stringify({ model_name: 'VaresaGIJP' }),
      })
    );
  });

  test('Test 5: Desktop Presence Opacity & Preset Sync', () => {
    settings.openSettings('presence');

    const opacitySlider = document.getElementById('settings-mascot-opacity');
    const presetSelect = document.getElementById('settings-mascot-preset-select');
    const startupToggle = document.getElementById('settings-mascot-startup-toggle');
    const launchBtn = document.getElementById('settings-launch-mascot-btn');

    // Opacity
    opacitySlider.value = '0.85';
    opacitySlider.dispatchEvent(new Event('input'));
    expect(document.getElementById('settings-opacity-val').textContent).toBe('85%');
    expect(localStorage.setItem).toHaveBeenCalledWith('lucia_mascot_opacity', '0.85');

    // Default Zoom Preset
    presetSelect.value = 'comfort';
    presetSelect.dispatchEvent(new Event('change'));
    expect(localStorage.setItem).toHaveBeenCalledWith('lucia_mascot_default_preset', 'comfort');

    // Startup Toggle
    startupToggle.checked = true;
    startupToggle.dispatchEvent(new Event('change'));
    expect(localStorage.setItem).toHaveBeenCalledWith('lucia_startup_mascot', 'true');

    // Launch Desktop Presence
    launchBtn.click();
    expect(mockLuciaAPI.window.toggleMascot).toHaveBeenCalled();
  });

  test('Test 6: Host Hardware Capability Rendering & Framerate Configuration', async () => {
    settings.openSettings('performance');

    const fpsSelect = document.getElementById('settings-fps-select');

    // Allow dynamic data resolution
    await new Promise((resolve) => setTimeout(resolve, 10));

    expect(mockLuciaAPI.system.getHardwareCapabilities).toHaveBeenCalled();
    expect(document.getElementById('settings-host-device').textContent).toBe('NVIDIA RTX 4060');
    expect(document.getElementById('settings-cuda-status').textContent).toBe('CUDA (Enabled)');
    expect(document.getElementById('settings-vram-detected').textContent).toBe('8,192 MB');
    expect(document.getElementById('settings-cpu-backend').textContent).toBe('CUDA (16T)');

    // Target FPS
    fpsSelect.value = '30';
    fpsSelect.dispatchEvent(new Event('change'));
    expect(localStorage.setItem).toHaveBeenCalledWith('lucia_target_fps', '30');
    expect(mockAvatarRenderer.setTargetFps).toHaveBeenCalledWith(30);
  });

  test('Test 7: Clear Active Talk View Non-Mutation Chain', () => {
    settings.openSettings('privacy');

    // Verify pre-clear state
    const talkStream = document.getElementById('talk-stream');
    expect(talkStream.children.length).toBe(2);
    const initialMilestones = mockCompanionJournal.historyMilestonesCount;

    // Trigger Clear Active View
    const clearBtn = document.getElementById('settings-clear-chat-btn');
    clearBtn.click();

    // Assertion 1: DOM talk view is cleared
    expect(talkStream.children.length).toBe(0);

    // Assertion 2: Journal milestones and stored turns remain untouched
    expect(mockCompanionJournal.historyMilestonesCount).toBe(initialMilestones);

    // Assertion 3: chatController.clearScreen was invoked without destroying memory
    expect(mockChatController.clearScreen).toHaveBeenCalled();

    // Assertion 4: Permanent memory/bond state invariant is communicated
    expect(document.getElementById('settings-sync-status-text').textContent).toContain(
      'Memories preserved'
    );
  });

  test('Test 8: Advanced Diagnostics Integration & Developer Mode', () => {
    settings.openSettings('advanced');

    const devToggle = document.getElementById('settings-dev-mode-toggle');
    const openDiagBtn = document.getElementById('settings-open-diagnostics-btn');
    const diagNavBtn = document.getElementById('toggle-diagnostics-btn');

    const clickSpy = jest.fn();
    diagNavBtn.addEventListener('click', clickSpy);

    // Developer mode toggle
    devToggle.checked = true;
    devToggle.dispatchEvent(new Event('change'));
    expect(localStorage.setItem).toHaveBeenCalledWith('lucia_developer_mode', 'true');

    // Open diagnostics triggers nav toggle and closes settings modal
    openDiagBtn.click();
    expect(clickSpy).toHaveBeenCalled();
    expect(document.getElementById('settings-modal').classList.contains('active')).toBe(false);
  });
});
