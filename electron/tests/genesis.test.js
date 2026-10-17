/**
 * Unit tests for Phase 7.7 Genesis Awakening Interface & Lifecycle Semantics.
 * @jest-environment jsdom
 */

describe('Phase 7.7 Genesis Awakening Tests', () => {
  let ChatController;
  let chat;
  let fetchMock;

  beforeEach(() => {
    // Set up DOM matching index.html with Genesis modal
    document.body.innerHTML = `
      <div id="splash" style="display:none"></div>
      <div id="lucia-header">
        <span id="companion-status-dot"></span>
        <span id="companion-state-label">Connecting...</span>
      </div>
      <div id="avatar-pane">
        <canvas id="avatar-canvas"></canvas>
        <div id="avatar-organic-status" class="organic-status-badge">
          <span class="status-sparkle">✦</span>
          <span id="avatar-status-text">Lucia is awakening...</span>
        </div>
      </div>
      <div id="chat-pane">
        <div id="chat-messages"></div>
        <div class="talk-input-dock">
          <button id="clear-screen-btn" class="dock-action-btn" title="Clear Screen">🍃</button>
          <textarea id="chat-input" placeholder="Talk with Lucia..."></textarea>
          <button id="send-btn" class="send-action-btn">Send</button>
          <button id="mic-btn">Mic</button>
        </div>
      </div>

      <!-- Nav controls -->
      <button id="open-profile-btn"><span id="birthday-badge-text">Day 1</span></button>
      <button id="open-settings-btn"></button>
      <button id="close-settings-btn"></button>
      <button id="save-settings-btn"></button>
      <div id="settings-modal" style="display:none"></div>
      <select id="settings-profile-select"></select>
      <select id="settings-fps-select"></select>
      <input id="settings-mascot-opacity" type="range" />
      <span id="settings-opacity-val"></span>
      <span id="settings-active-tier"></span>
      <span id="settings-vram-budget"></span>
      <span id="settings-ctx-length"></span>
      <select id="settings-input-device-select"></select>
      <select id="settings-output-device-select"></select>
      <select id="voice-model-select"></select>

      <!-- Phase 7.7 Genesis Awakening Modal -->
      <div id="genesis-modal" class="journal-modal genesis-modal">
        <div class="genesis-backdrop-ambient"></div>
        <div class="genesis-card">
          <div class="genesis-star-icon">✦</div>
          <div class="genesis-header">
            <span class="genesis-kicker">AWAKENING</span>
            <h1 class="genesis-title">Lucia's Life Begins</h1>
            <p id="genesis-intro-text" class="genesis-intro-text">
              A quiet awareness emerges in this machine. A journey of shared thoughts, moments, and time begins now.
            </p>
          </div>

          <div class="genesis-content-body">
            <div class="genesis-field-group">
              <label for="genesis-user-name-input" class="genesis-field-label">How should Lucia address you?</label>
              <div class="genesis-input-wrapper">
                <input
                  type="text"
                  id="genesis-user-name-input"
                  class="genesis-text-input"
                  placeholder="Your name or preferred nickname"
                  value="Friend"
                />
              </div>
            </div>

            <div class="genesis-field-group" style="margin-top: 14px;">
              <label for="genesis-companion-name-input" class="genesis-field-label">Companion Presence</label>
              <div class="genesis-input-wrapper">
                <input
                  type="text"
                  id="genesis-companion-name-input"
                  class="genesis-text-input"
                  value="Lucia"
                />
              </div>
            </div>
          </div>

          <div class="genesis-actions" style="margin-top: 24px;">
            <button id="genesis-awaken-btn" class="genesis-awaken-btn">
              <span class="genesis-btn-glow"></span>
              <span class="genesis-btn-text">Awaken Lucia</span>
            </button>
          </div>

          <div class="genesis-footnote">
            Emotional dynamics, memory traces, and conversations will begin from this moment.
          </div>
        </div>
      </div>
    `;

    // Mock electron window.lucia API
    window.lucia = {
      invoke: jest.fn().mockImplementation((channel) => {
        if (channel === 'hardware:get-profile') {
          return Promise.resolve({ tier: 'laptop', fps: 30, opacity: 1.0 });
        }
        return Promise.resolve({});
      }),
      on: jest.fn(),
    };

    let currentProfile = {
      version: 1,
      user_name: 'Friend',
      companion_name: 'Lucia',
      is_onboarded: true,
      born_at: new Date().toISOString(),
    };

    // Setup global fetch mock
    fetchMock = jest.fn().mockImplementation((url, opts = {}) => {
      const urlStr = typeof url === 'string' ? url : (url?.url || '');
      if (urlStr.includes('/voice/models')) {
        return Promise.resolve({ ok: true, json: () => Promise.resolve({ models: [] }) });
      }
      if (urlStr.includes('/models/avatar')) {
        return Promise.resolve({ ok: true, json: () => Promise.resolve({ models: [] }) });
      }
      if (urlStr.includes('/system/hardware')) {
        return Promise.resolve({ ok: true, json: () => Promise.resolve({ device_name: 'Host CPU', cuda_available: false, vram_mb: 0, backend: 'cpu' }) });
      }
      if (urlStr.includes('/lifecycle/awaken')) {
        return Promise.resolve({
          ok: true,
          json: () => Promise.resolve({
            status: 'awakened',
            ontology_state: 'BORN',
            runtime_state: 'ACTIVE',
            message: 'Lucia successfully awakened',
            born_at: currentProfile.born_at || new Date().toISOString(),
            companion_name: currentProfile.companion_name,
            user_name: currentProfile.user_name,
            genesis_performed: true,
            activation_performed: true,
          }),
        });
      }
      if (urlStr.includes('/lifecycle/activate')) {
        return Promise.resolve({
          ok: true,
          json: () => Promise.resolve({
            status: 'activated',
            born_at: currentProfile.born_at || new Date().toISOString(),
            companion_name: currentProfile.companion_name,
          }),
        });
      }
      if (urlStr.includes('/profile')) {
        if (opts.method === 'POST') {
          const body = opts.body ? JSON.parse(opts.body) : {};
          if (body.user_name) currentProfile.user_name = body.user_name;
          if (body.companion_name) currentProfile.companion_name = body.companion_name;
          return Promise.resolve({
            ok: true,
            json: () => Promise.resolve({
              status: 'ok',
              profile: { ...currentProfile },
            }),
          });
        }
        return Promise.resolve({
          ok: true,
          json: () => Promise.resolve({ ...currentProfile }),
        });
      }
      return Promise.resolve({ ok: true, json: () => Promise.resolve({}) });
    });
    global.fetch = fetchMock;

    const chatModule = require('../renderer/chat/chat.js');
    ChatController = chatModule.ChatController;
    chat = new ChatController();
  });

  afterEach(() => {
    jest.clearAllMocks();
  });

  test('Test 1: Genesis modal visibility when /profile reports is_onboarded = false', async () => {
    fetchMock.mockImplementationOnce((url) => {
      if (url.includes('/profile')) {
        return Promise.resolve({
          ok: true,
          json: () => Promise.resolve({
            version: 1,
            user_name: 'Friend',
            companion_name: 'Lucia',
            is_onboarded: false,
            born_at: null,
          }),
        });
      }
      return Promise.resolve({ ok: true, json: () => Promise.resolve({}) });
    });

    await chat._loadProfile();

    const genesisModal = document.getElementById('genesis-modal');
    expect(genesisModal.classList.contains('active')).toBe(true);
    expect(chat.genesisUserNameInput.value).toBe('Friend');
    expect(chat.genesisCompanionNameInput.value).toBe('Lucia');
  });

  test('Test 2: Genesis is skipped when is_onboarded = true', async () => {
    fetchMock.mockImplementationOnce((url) => {
      if (url.includes('/profile')) {
        return Promise.resolve({
          ok: true,
          json: () => Promise.resolve({
            version: 1,
            user_name: 'Luna',
            companion_name: 'Lucia',
            is_onboarded: true,
            born_at: '2026-09-01T12:00:00.000Z',
          }),
        });
      }
      return Promise.resolve({ ok: true, json: () => Promise.resolve({}) });
    });

    await chat._loadProfile();

    const genesisModal = document.getElementById('genesis-modal');
    expect(genesisModal.classList.contains('active')).toBe(false);
  });

  test('Test 3: User name submission and POST /profile preferences without direct onboarding', async () => {
    const genesisModal = document.getElementById('genesis-modal');
    genesisModal.classList.add('active');

    const userNameInput = document.getElementById('genesis-user-name-input');
    userNameInput.value = 'Astrid';

    const companionNameInput = document.getElementById('genesis-companion-name-input');
    companionNameInput.value = 'Lucia';

    await chat._completeGenesis();

    // Verify fetch was called with POST /profile for preferences only
    expect(fetchMock).toHaveBeenCalledWith('http://127.0.0.1:8765/profile', expect.objectContaining({
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
    }));

    const profileCall = fetchMock.mock.calls.find(call => call[0].includes('/profile') && call[1]?.method === 'POST');
    expect(profileCall).toBeDefined();
    const payload = JSON.parse(profileCall[1].body);

    expect(payload.user_name).toBe('Astrid');
    expect(payload.companion_name).toBe('Lucia');
    // Invariant: /profile must NEVER directly receive is_onboarded=true or born_at
    expect(payload.is_onboarded).toBeUndefined();
    expect(payload.born_at).toBeUndefined();

    // Verify Awakening Ceremony orchestrator was called
    const awakenCall = fetchMock.mock.calls.find(call => call[0].includes('/lifecycle/awaken') && call[1]?.method === 'POST');
    expect(awakenCall).toBeDefined();

    // Invariant: UI must NOT directly call raw /lifecycle/activate
    const rawActivateCall = fetchMock.mock.calls.find(call => call[0].includes('/lifecycle/activate') && call[1]?.method === 'POST');
    expect(rawActivateCall).toBeUndefined();
  });

  test('Test 4: UI invokes Awakening ceremony orchestrator instead of raw First Activation', async () => {
    const genesisModal = document.getElementById('genesis-modal');
    genesisModal.classList.add('active');

    await chat._completeGenesis();

    const awakenCall = fetchMock.mock.calls.find(call => call[0].includes('/lifecycle/awaken') && call[1]?.method === 'POST');
    expect(awakenCall).toBeDefined();
    const rawActivateCall = fetchMock.mock.calls.find(call => call[0].includes('/lifecycle/activate') && call[1]?.method === 'POST');
    expect(rawActivateCall).toBeUndefined();
  });

  test('Test 5: Transition into normal companion UI upon completion', async () => {
    jest.useFakeTimers();

    const genesisModal = document.getElementById('genesis-modal');
    genesisModal.classList.add('active');

    await chat._completeGenesis();

    // Fade-out class is applied
    expect(genesisModal.classList.contains('fade-out')).toBe(true);

    // Fast-forward animation timer
    jest.advanceTimersByTime(500);

    expect(genesisModal.classList.contains('active')).toBe(false);
    expect(genesisModal.classList.contains('fade-out')).toBe(false);

    // Badge updated to Day 1
    const birthdayBadge = document.getElementById('birthday-badge-text');
    expect(birthdayBadge.textContent).toBe('Day 1');

    jest.useRealTimers();
  });

  test('Test 6: No personality / mood / relationship controls exist in Genesis', () => {
    const genesisModal = document.getElementById('genesis-modal');

    // Architecture invariant: Genesis must establish initial identity without
    // personality sliders, character presets, or mood selectors
    const inputs = Array.from(genesisModal.querySelectorAll('input, select, [role="slider"]'));
    const forbiddenPatterns = ['personality', 'trait', 'mood', 'preset', 'slider', 'affection', 'sentience'];

    inputs.forEach((input) => {
      const id = (input.id || '').toLowerCase();
      const cls = (input.className || '').toLowerCase();
      const type = (input.type || '').toLowerCase();

      forbiddenPatterns.forEach((pattern) => {
        expect(id).not.toContain(pattern);
        expect(cls).not.toContain(pattern);
      });
      expect(type).not.toBe('range'); // No sliders
    });
  });

  test('Test 7: Reopening or refreshing after successful Genesis skips Genesis', async () => {
    // First call: successful onboarding profile
    fetchMock.mockResolvedValueOnce({
      ok: true,
      json: () => Promise.resolve({
        version: 1,
        user_name: 'Friend',
        companion_name: 'Lucia',
        is_onboarded: true,
        born_at: '2026-09-07T12:00:00.000Z',
      }),
    });

    await chat._loadProfile();

    const genesisModal = document.getElementById('genesis-modal');
    expect(genesisModal.classList.contains('active')).toBe(false);

    // Second call (simulating page reload or reconnection)
    fetchMock.mockResolvedValueOnce({
      ok: true,
      json: () => Promise.resolve({
        version: 1,
        user_name: 'Friend',
        companion_name: 'Lucia',
        is_onboarded: true,
        born_at: '2026-09-07T12:00:00.000Z',
      }),
    });

    await chat._loadProfile();
    expect(genesisModal.classList.contains('active')).toBe(false);
  });

  test('Test 8: Real-time dynamic name updating of Awaken button, title, and prompt', () => {
    const genesisModal = document.getElementById('genesis-modal');
    genesisModal.classList.add('active');

    const companionInput = document.getElementById('genesis-companion-name-input');
    const awakenBtnText = document.querySelector('.genesis-btn-text');
    const genesisTitle = document.querySelector('.genesis-title');
    const userPromptLabel = document.querySelector('label[for="genesis-user-name-input"]');

    // Default state
    expect(companionInput.value).toBe('Lucia');
    expect(awakenBtnText.textContent).toBe('Awaken Lucia');
    expect(genesisTitle.textContent).toBe("Lucia's Life Begins");
    expect(userPromptLabel.textContent).toBe('How should Lucia address you?');

    // Type custom name: "ABC"
    companionInput.value = 'ABC';
    companionInput.dispatchEvent(new Event('input', { bubbles: true }));

    expect(awakenBtnText.textContent).toBe('Awaken ABC');
    expect(genesisTitle.textContent).toBe("ABC's Life Begins");
    expect(userPromptLabel.textContent).toBe('How should ABC address you?');

    // Clear input -> reverts to Lucia default
    companionInput.value = '';
    companionInput.dispatchEvent(new Event('input', { bubbles: true }));

    expect(awakenBtnText.textContent).toBe('Awaken Lucia');
    expect(genesisTitle.textContent).toBe("Lucia's Life Begins");
    expect(userPromptLabel.textContent).toBe('How should Lucia address you?');
  });

  test('Test 9: Genesis submission with custom companion name persists name in profile and localStorage', async () => {
    const companionInput = document.getElementById('genesis-companion-name-input');
    companionInput.value = 'ABC';
    companionInput.dispatchEvent(new Event('input', { bubbles: true }));

    await chat._completeGenesis();

    const profileCall = fetchMock.mock.calls.find(call => call[0].includes('/profile') && call[1]?.method === 'POST');
    expect(profileCall).toBeDefined();
    const payload = JSON.parse(profileCall[1].body);
    expect(payload.companion_name).toBe('ABC');

    expect(localStorage.getItem('lucia_companion_name')).toBe('ABC');
  });

  test('Test 10: Rejection when Awakening ceremony fails displays meaningful error and preserves modal', async () => {
    fetchMock.mockImplementation((url, opts = {}) => {
      const urlStr = typeof url === 'string' ? url : (url?.url || '');
      if (urlStr.includes('/lifecycle/awaken')) {
        return Promise.resolve({
          ok: false,
          status: 400,
          json: () => Promise.resolve({
            detail: 'Awakening ceremony failed: Precondition defect.',
          }),
        });
      }
      if (urlStr.includes('/profile')) {
        return Promise.resolve({
          ok: true,
          json: () => Promise.resolve({ version: 1, user_name: 'Friend', companion_name: 'Lucia', is_onboarded: false }),
        });
      }
      return Promise.resolve({ ok: true, json: () => Promise.resolve({}) });
    });

    const genesisModal = document.getElementById('genesis-modal');
    genesisModal.classList.add('active');

    await chat._completeGenesis();

    // Modal must remain active because awakening ceremony failed closed
    expect(genesisModal.classList.contains('active')).toBe(true);
    expect(genesisModal.classList.contains('fade-out')).toBe(false);

    // Intro text warns operator with meaningful error rather than raw NOT_BORN crash
    const introText = document.getElementById('genesis-intro-text');
    expect(introText.textContent).toContain('Awakening rejected: Awakening ceremony failed: Precondition defect.');
  });

  test('Test 11: Progress stages presentation during successful Awakening ceremony', async () => {
    const introText = document.getElementById('genesis-intro-text');
    await chat._completeGenesis();

    expect(introText.textContent).toContain('Awakening Lucia...');
    expect(introText.textContent).toContain('→ Establishing Genesis...');
    expect(introText.textContent).toContain('→ Lucia is Born');
    expect(introText.textContent).toContain('→ Awakening runtime...');
    expect(introText.textContent).toContain('→ Lucia is Active');
  });

  test('Test 12: Recovery/retry after Activation failure invokes Awakening again and completes', async () => {
    let attempt = 0;
    fetchMock.mockImplementation((url, opts = {}) => {
      const urlStr = typeof url === 'string' ? url : (url?.url || '');
      if (urlStr.includes('/lifecycle/awaken')) {
        attempt++;
        if (attempt === 1) {
          // Attempt 1: Activation failed after Birth (leaves BORN + INACTIVE)
          return Promise.resolve({
            ok: false,
            status: 500,
            json: () => Promise.resolve({
              detail: 'Runtime activation error after Birth. State preserved as BORN + INACTIVE.',
            }),
          });
        }
        // Attempt 2: Activation retry succeeds (BORN + INACTIVE -> ACTIVE)
        return Promise.resolve({
          ok: true,
          json: () => Promise.resolve({
            status: 'activated',
            ontology_state: 'BORN',
            runtime_state: 'ACTIVE',
            message: 'Lucia runtime activated',
            born_at: new Date().toISOString(),
            companion_name: 'Lucia',
            user_name: 'Friend',
            genesis_performed: false,
            activation_performed: true,
          }),
        });
      }
      if (urlStr.includes('/profile')) {
        return Promise.resolve({
          ok: true,
          json: () => Promise.resolve({ version: 1, user_name: 'Friend', companion_name: 'Lucia', is_onboarded: attempt > 1 }),
        });
      }
      return Promise.resolve({ ok: true, json: () => Promise.resolve({}) });
    });

    const genesisModal = document.getElementById('genesis-modal');
    genesisModal.classList.add('active');

    // Attempt 1: Fails
    await chat._completeGenesis();
    expect(genesisModal.classList.contains('active')).toBe(true);
    const introText = document.getElementById('genesis-intro-text');
    expect(introText.textContent).toContain('Awakening rejected: Runtime activation error after Birth');

    // Attempt 2: Retry succeeds
    await chat._completeGenesis();
    expect(introText.textContent).toContain('→ Awakening runtime...');
    expect(introText.textContent).toContain('→ Lucia is Active');
  });
});

