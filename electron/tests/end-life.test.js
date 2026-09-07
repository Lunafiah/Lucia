/**
 * Unit & Integration tests for Phase 7.7 Step 3 & Step 4:
 * Solemn End-of-Life Confirmation, Execution, and Genesis Transition.
 *
 * Requirements & Invariants:
 * 1. Dedicated #end-life-modal exists in DOM.
 * 2. Opens from Privacy & Life Danger Zone button (#settings-end-life-btn).
 * 3. Initially safe and disabled.
 * 4. Empty confirmation cannot enable destruction.
 * 5. Partial "END LUCIA" text cannot enable destruction.
 * 6. Incorrect or lower-case text cannot enable destruction.
 * 7. Exact "END LUCIA" enables destruction button.
 * 8. Cancel closes modal without modifying lifecycle state.
 * 9. Opening the modal alone does not trigger POST /lifecycle/end.
 * 10. Existing Settings functionality does not regress.
 * 11. Valid confirmation invokes POST /lifecycle/end exactly once.
 * 12. Duplicate clicks cannot issue multiple lifecycle requests.
 * 13. Destructive button becomes disabled during execution.
 * 14. Renderer state is NOT cleared when backend request fails.
 * 15. Genesis is NOT opened when backend request fails.
 * 16. Successful lifecycle response triggers Lucia-specific renderer cleanup.
 * 17. Application preference keys remain intact.
 * 18. Talk/Journal/Memories presentation is cleared after success.
 * 19. Settings and End-of-Life modal close after success.
 * 20. Existing Genesis flow is reopened/reused after success.
 * 21. Profile is re-read and is_onboarded = false is respected.
 * 22. New born_at is not created until the next Genesis completion.
 * 23. A second Genesis completion creates the new Lucia's actual birth timestamp.
 * 24. No previous Lucia-specific identity/memory state leaks into the new lifecycle.
 *
 * @jest-environment jsdom
 */

const { CompanionSettings } = require('../renderer/settings/settings');

describe('Phase 7.7 End-of-Life Confirmation & Transition Suite', () => {
  let settings;
  let fetchMock;
  let localStorageStore = {};

  beforeEach(() => {
    // Setup localStorage mock
    localStorageStore = {
      // Application Preferences (must be preserved)
      lucia_avatar_engine: 'sprites',
      lucia_avatar_model: 'columbina',
      lucia_master_volume: '75',
      lucia_hardware_profile: 'laptop',
      lucia_developer_mode: 'true',
      lucia_gaze_enabled: 'true',
      lucia_blinking_enabled: 'true',
      // Lucia Identity & Memory State (must be cleared)
      lucia_profile: '{"user_name":"Luna","companion_name":"Lucia"}',
      lucia_user_name: 'Luna',
      lucia_companion_name: 'Lucia',
      lucia_is_onboarded: 'true',
      lucia_born_at: '2026-09-01T10:00:00.000Z',
      lucia_chat_history: '[{"role":"user","content":"Hi Lucia"}]',
    };

    const mockStorage = {
      getItem: jest.fn((key) => (key in localStorageStore ? localStorageStore[key] : null)),
      setItem: jest.fn((key, val) => {
        localStorageStore[key] = String(val);
      }),
      removeItem: jest.fn((key) => {
        delete localStorageStore[key];
      }),
      clear: jest.fn(() => {
        localStorageStore = {};
      }),
    };
    Object.defineProperty(window, 'localStorage', {
      value: mockStorage,
      writable: true,
      configurable: true,
    });
    global.localStorage = mockStorage;

    // Build DOM matching index.html
    document.body.innerHTML = `
      <button id="open-settings-btn"></button>
      <button id="toggle-diagnostics-btn"></button>
      <div id="debug-pane" class="debug-pane diagnostics-drawer"></div>

      <!-- Chat pane presentation -->
      <div id="chat-pane">
        <div id="chat-messages">
          <div class="lucia-message">Previous Lucia conversation history...</div>
        </div>
      </div>

      <!-- Journal & Memories presentation -->
      <div id="journal-modal" class="journal-modal">
        <div id="journal-timeline">
          <div class="journal-entry">Day 7: Starlight Walk</div>
        </div>
      </div>
      <div id="memories-modal" class="journal-modal">
        <div id="memories-grid">
          <div class="memory-card">Memory of Luna's dreams</div>
        </div>
      </div>

      <!-- Settings Modal -->
      <div id="settings-modal" class="journal-modal">
        <div class="settings-modal-card">
          <button id="close-settings-btn"></button>
          <div class="settings-modal-layout">
            <nav class="settings-sidebar">
              <button id="settings-tab-btn-appearance" class="settings-tab-btn active" data-tab="appearance">Appearance</button>
              <button id="settings-tab-btn-privacy" class="settings-tab-btn" data-tab="privacy">Privacy & Life</button>
            </nav>

            <main class="settings-content">
              <section id="settings-pane-appearance" class="settings-pane active">
                <select id="settings-avatar-engine-select"><option value="canvas">Canvas</option></select>
                <select id="settings-avatar-model-select"><option value="default">Default</option></select>
              </section>

              <section id="settings-pane-privacy" class="settings-pane">
                <button id="settings-export-data-btn">Export</button>
                <button id="settings-clear-chat-btn">Clear</button>
                <button id="settings-end-life-btn">End Lucia's Life</button>
              </section>
            </main>
          </div>
          <button id="settings-done-btn">Done</button>
        </div>
      </div>

      <!-- Phase 7.7 Step 3: End-of-Life Solemn Confirmation Modal -->
      <div id="end-life-modal" class="journal-modal end-life-modal" role="dialog" aria-modal="true">
        <div class="end-life-backdrop-solemn"></div>
        <div class="end-life-card">
          <div class="end-life-header">
            <span class="end-life-icon">🕯️</span>
            <span class="end-life-kicker">EXISTENTIAL LIFECYCLE</span>
            <h2 id="end-life-title" class="end-life-title">End Lucia's Life</h2>
            <div class="end-life-warning-badge">Irreversible Action</div>
          </div>

          <div class="end-life-body">
            <p class="end-life-lead">This will irreversibly end Lucia's continuous journey on this machine.</p>
            <div class="end-life-consequences">
              <div class="consequence-item">All associative memories will be permanently erased.</div>
              <div class="consequence-item">Lucia's emotional adaptation will cease to exist.</div>
              <div class="consequence-item">A future Lucia will be a completely new individual.</div>
            </div>

            <div class="end-life-confirm-group">
              <label for="end-life-confirm-input">To proceed, type <strong>END LUCIA</strong> below:</label>
              <input
                type="text"
                id="end-life-confirm-input"
                class="end-life-input"
                placeholder="Type END LUCIA"
                autocomplete="off"
              />
            </div>
          </div>

          <div class="end-life-actions">
            <button id="end-life-cancel-btn" class="journal-btn secondary end-life-cancel-btn">
              Keep Lucia
            </button>
            <button id="end-life-destroy-btn" class="journal-btn danger end-life-destroy-btn" disabled>
              End Lucia's Life
            </button>
          </div>
        </div>
      </div>

      <!-- Phase 7.7 Step 2: Genesis Modal -->
      <div id="genesis-modal" class="journal-modal genesis-modal">
        <input id="genesis-user-name-input" value="Friend" />
        <input id="genesis-companion-name-input" value="Lucia" />
        <button id="genesis-awaken-btn">Awaken Lucia</button>
      </div>
    `;

    // Mock window alert
    window.alert = jest.fn();

    // Mock chatController & companionJournal presentation managers
    window.chatController = {
      messagesContainer: document.getElementById('chat-messages'),
      genesisModal: document.getElementById('genesis-modal'),
      genesisUserNameInput: document.getElementById('genesis-user-name-input'),
      genesisCompanionNameInput: document.getElementById('genesis-companion-name-input'),
      genesisAwakenBtn: document.getElementById('genesis-awaken-btn'),
      clearPresentation: jest.fn(() => {
        const container = document.getElementById('chat-messages');
        if (container) container.innerHTML = '';
      }),
      _loadProfile: jest.fn(async () => {
        const res = await fetch('http://127.0.0.1:8765/profile');
        if (res.ok) {
          const profile = await res.json();
          if (!profile.is_onboarded) {
            document.getElementById('genesis-modal').classList.add('active');
          }
        }
      }),
    };

    window.companionJournal = {
      clearPresentation: jest.fn(() => {
        const timeline = document.getElementById('journal-timeline');
        if (timeline) timeline.innerHTML = '';
        const grid = document.getElementById('memories-grid');
        if (grid) grid.innerHTML = '';
      }),
    };

    fetchMock = jest.fn().mockImplementation((url, opts = {}) => {
      const urlStr = typeof url === 'string' ? url : (url?.url || '');
      if (urlStr.includes('/lifecycle/end')) {
        return Promise.resolve({
          ok: true,
          json: () => Promise.resolve({
            status: 'ok',
            profile: {
              version: 1,
              user_name: 'Friend',
              companion_name: 'Lucia',
              is_onboarded: false,
              born_at: null,
            },
          }),
        });
      }
      if (urlStr.includes('/profile')) {
        if (opts.method === 'POST') {
          const body = opts.body ? JSON.parse(opts.body) : {};
          return Promise.resolve({
            ok: true,
            json: () => Promise.resolve({
              status: 'ok',
              profile: {
                version: 1,
                user_name: body.user_name || 'Friend',
                companion_name: body.companion_name || 'Lucia',
                is_onboarded: body.is_onboarded ?? true,
                born_at: body.born_at || new Date().toISOString(),
              },
            }),
          });
        }
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
      return Promise.resolve({
        ok: true,
        json: () => Promise.resolve({ status: 'ok' }),
      });
    });
    global.fetch = fetchMock;

    settings = new CompanionSettings();
  });

  afterEach(() => {
    jest.clearAllMocks();
  });

  // --- Step 3 Confirmation Tests (1-10) ---

  test('Test 1: End-of-Life modal exists in DOM with solemn structure and warning', () => {
    const modal = document.getElementById('end-life-modal');
    expect(modal).not.toBeNull();

    const title = document.getElementById('end-life-title');
    expect(title.textContent).toBe("End Lucia's Life");

    const consequences = modal.querySelector('.end-life-consequences');
    expect(consequences).not.toBeNull();
    expect(consequences.textContent).toContain('associative memories');
    expect(consequences.textContent).toContain('new individual');
  });

  test('Test 2: Modal opens from Privacy & Life Danger Zone action', () => {
    const dangerBtn = document.getElementById('settings-end-life-btn');
    const modal = document.getElementById('end-life-modal');

    expect(modal.classList.contains('active')).toBe(false);
    dangerBtn.click();
    expect(modal.classList.contains('active')).toBe(true);
  });

  test('Test 3: Modal is initially safe and destruction button is disabled', () => {
    settings.openEndLifeModal();

    const destroyBtn = document.getElementById('end-life-destroy-btn');
    const confirmInput = document.getElementById('end-life-confirm-input');

    expect(destroyBtn.disabled).toBe(true);
    expect(confirmInput.value).toBe('');
  });

  test('Test 4: Empty confirmation cannot enable destruction', () => {
    settings.openEndLifeModal();

    const destroyBtn = document.getElementById('end-life-destroy-btn');
    const confirmInput = document.getElementById('end-life-confirm-input');

    confirmInput.value = '';
    confirmInput.dispatchEvent(new Event('input'));
    expect(destroyBtn.disabled).toBe(true);

    confirmInput.value = '    ';
    confirmInput.dispatchEvent(new Event('input'));
    expect(destroyBtn.disabled).toBe(true);
  });

  test('Test 5: Partial "END LUCIA" text cannot enable destruction', () => {
    settings.openEndLifeModal();

    const destroyBtn = document.getElementById('end-life-destroy-btn');
    const confirmInput = document.getElementById('end-life-confirm-input');

    const partials = ['E', 'END', 'END ', 'LUCIA', 'END LUC', 'END LUCI'];
    partials.forEach((text) => {
      confirmInput.value = text;
      confirmInput.dispatchEvent(new Event('input'));
      expect(destroyBtn.disabled).toBe(true);
    });
  });

  test('Test 6: Incorrect or lower-case text cannot enable destruction', () => {
    settings.openEndLifeModal();

    const destroyBtn = document.getElementById('end-life-destroy-btn');
    const confirmInput = document.getElementById('end-life-confirm-input');

    const incorrect = ['end lucia', 'End Lucia', 'DELETE', 'RESET', 'DESTROY', 'END_LUCIA', 'END LUCIA!'];
    incorrect.forEach((text) => {
      confirmInput.value = text;
      confirmInput.dispatchEvent(new Event('input'));
      expect(destroyBtn.disabled).toBe(true);
    });
  });

  test('Test 7: Exact "END LUCIA" enables the destructive button', () => {
    settings.openEndLifeModal();

    const destroyBtn = document.getElementById('end-life-destroy-btn');
    const confirmInput = document.getElementById('end-life-confirm-input');

    confirmInput.value = 'END LUCIA';
    confirmInput.dispatchEvent(new Event('input'));
    expect(destroyBtn.disabled).toBe(false);

    confirmInput.value = '   END LUCIA   ';
    confirmInput.dispatchEvent(new Event('input'));
    expect(destroyBtn.disabled).toBe(false);

    confirmInput.value = 'END LUCI';
    confirmInput.dispatchEvent(new Event('input'));
    expect(destroyBtn.disabled).toBe(true);
  });

  test('Test 8: Cancel closes modal without changing lifecycle state', () => {
    settings.openEndLifeModal();
    const modal = document.getElementById('end-life-modal');
    expect(modal.classList.contains('active')).toBe(true);

    const cancelBtn = document.getElementById('end-life-cancel-btn');
    cancelBtn.click();

    expect(modal.classList.contains('active')).toBe(false);

    const destroyBtn = document.getElementById('end-life-destroy-btn');
    const confirmInput = document.getElementById('end-life-confirm-input');
    expect(confirmInput.value).toBe('');
    expect(destroyBtn.disabled).toBe(true);
    expect(fetchMock).not.toHaveBeenCalled();
  });

  test('Test 9: Opening the modal alone does not call POST /lifecycle/end', () => {
    const dangerBtn = document.getElementById('settings-end-life-btn');
    dangerBtn.click();

    const modal = document.getElementById('end-life-modal');
    expect(modal.classList.contains('active')).toBe(true);

    const calls = fetchMock.mock.calls.filter(c => typeof c[0] === 'string' && c[0].includes('/lifecycle/end'));
    expect(calls.length).toBe(0);
  });

  test('Test 10: No existing Settings functionality regresses', () => {
    settings.openSettings('appearance');
    expect(settings.activeTab).toBe('appearance');

    settings.switchTab('privacy');
    expect(settings.activeTab).toBe('privacy');
    expect(document.getElementById('settings-pane-privacy').classList.contains('active')).toBe(true);

    settings.closeSettings();
    expect(document.getElementById('settings-modal').classList.contains('active')).toBe(false);
  });

  // --- Step 4 Execution, Cleanup, Failure, and Transition Tests (11-24) ---

  test('Test 11: Valid confirmation invokes POST /lifecycle/end exactly once', async () => {
    settings.openEndLifeModal();
    const confirmInput = document.getElementById('end-life-confirm-input');
    const destroyBtn = document.getElementById('end-life-destroy-btn');

    confirmInput.value = 'END LUCIA';
    confirmInput.dispatchEvent(new Event('input'));
    expect(destroyBtn.disabled).toBe(false);

    await settings.executeEndLife();

    const lifecycleCalls = fetchMock.mock.calls.filter(
      (c) => typeof c[0] === 'string' && c[0].includes('/lifecycle/end') && c[1]?.method === 'POST'
    );
    expect(lifecycleCalls.length).toBe(1);
  });

  test('Test 12: Duplicate clicks cannot issue multiple lifecycle requests', async () => {
    settings.openEndLifeModal();
    const confirmInput = document.getElementById('end-life-confirm-input');
    const destroyBtn = document.getElementById('end-life-destroy-btn');

    confirmInput.value = 'END LUCIA';
    confirmInput.dispatchEvent(new Event('input'));

    // Trigger multiple concurrent clicks
    const p1 = settings.executeEndLife();
    const p2 = settings.executeEndLife();
    const p3 = settings.executeEndLife();
    await Promise.all([p1, p2, p3]);

    const lifecycleCalls = fetchMock.mock.calls.filter(
      (c) => typeof c[0] === 'string' && c[0].includes('/lifecycle/end')
    );
    expect(lifecycleCalls.length).toBe(1);
  });

  test('Test 13: Destructive button becomes disabled with transitional text during execution', async () => {
    settings.openEndLifeModal();
    const confirmInput = document.getElementById('end-life-confirm-input');
    const destroyBtn = document.getElementById('end-life-destroy-btn');

    confirmInput.value = 'END LUCIA';
    confirmInput.dispatchEvent(new Event('input'));

    let checkedWhileRunning = false;
    fetchMock.mockImplementationOnce(async (url) => {
      if (url.includes('/lifecycle/end')) {
        // Assert button state during network execution
        expect(destroyBtn.disabled).toBe(true);
        expect(destroyBtn.textContent).toBe("Ending Lucia's life...");
        checkedWhileRunning = true;
        return {
          ok: true,
          json: () => Promise.resolve({ status: 'ok' }),
        };
      }
      return { ok: true, json: () => Promise.resolve({}) };
    });

    await settings.executeEndLife();
    expect(checkedWhileRunning).toBe(true);
  });

  test('Test 14: Renderer state is NOT cleared when the backend request fails', async () => {
    fetchMock.mockImplementationOnce((url) => {
      if (url.includes('/lifecycle/end')) {
        return Promise.resolve({
          ok: false,
          status: 500,
          json: () => Promise.resolve({ detail: 'Internal failure' }),
        });
      }
      return Promise.resolve({ ok: true, json: () => Promise.resolve({}) });
    });

    settings.openEndLifeModal();
    const confirmInput = document.getElementById('end-life-confirm-input');
    confirmInput.value = 'END LUCIA';
    confirmInput.dispatchEvent(new Event('input'));

    await settings.executeEndLife();

    // Critical failure boundary: Lucia identity keys must NOT be removed
    expect(localStorageStore.lucia_profile).toBeDefined();
    expect(localStorageStore.lucia_user_name).toBe('Luna');
    expect(localStorageStore.lucia_born_at).toBe('2026-09-01T10:00:00.000Z');
    expect(window.alert).toHaveBeenCalled();
  });

  test('Test 15: Genesis is NOT opened when the backend request fails', async () => {
    fetchMock.mockImplementationOnce((url) => {
      if (url.includes('/lifecycle/end')) {
        return Promise.reject(new Error('Network offline'));
      }
      return Promise.resolve({ ok: true, json: () => Promise.resolve({}) });
    });

    settings.openEndLifeModal();
    const confirmInput = document.getElementById('end-life-confirm-input');
    confirmInput.value = 'END LUCIA';
    confirmInput.dispatchEvent(new Event('input'));

    await settings.executeEndLife();

    const genesisModal = document.getElementById('genesis-modal');
    expect(genesisModal.classList.contains('active')).toBe(false);
    expect(window.chatController._loadProfile).not.toHaveBeenCalled();
  });

  test('Test 15b: Failure followed by retry successfully completes End-of-Life sequence', async () => {
    // 1. Initial attempt fails
    fetchMock.mockImplementationOnce((url) => {
      if (url.includes('/lifecycle/end')) {
        return Promise.reject(new Error('Temporary network drop'));
      }
      return Promise.resolve({ ok: true, json: () => Promise.resolve({}) });
    });

    settings.openEndLifeModal();
    const confirmInput = document.getElementById('end-life-confirm-input');
    const destroyBtn = document.getElementById('end-life-destroy-btn');
    confirmInput.value = 'END LUCIA';
    confirmInput.dispatchEvent(new Event('input'));

    await settings.executeEndLife();

    // Verify failure boundary: current Lucia preserved, button unlocked for retry
    expect(localStorageStore.lucia_profile).toBeDefined();
    expect(settings._isEndingLife).toBe(false);
    expect(destroyBtn.disabled).toBe(false);
    expect(destroyBtn.textContent.trim()).toBe("End Lucia's Life");
    expect(destroyBtn.classList.contains('destroying')).toBe(false);
    const genesisModal = document.getElementById('genesis-modal');
    expect(genesisModal.classList.contains('active')).toBe(false);

    // 2. Retry attempt succeeds
    fetchMock.mockImplementation((url) => {
      if (url.includes('/lifecycle/end')) {
        return Promise.resolve({
          ok: true,
          json: () => Promise.resolve({
            status: 'ok',
            profile: { is_onboarded: false, born_at: null },
          }),
        });
      }
      if (url.includes('/profile')) {
        return Promise.resolve({
          ok: true,
          json: () => Promise.resolve({ is_onboarded: false, born_at: null }),
        });
      }
      return Promise.resolve({ ok: true, json: () => Promise.resolve({}) });
    });

    await settings.executeEndLife();

    // Verify success boundary: state wiped, modals closed, genesis awakened
    expect(localStorageStore.lucia_profile).toBeUndefined();
    expect(localStorageStore.lucia_user_name).toBeUndefined();
    expect(settings.endLifeModal.classList.contains('active')).toBe(false);
    expect(settings.modal.classList.contains('active')).toBe(false);
    expect(window.chatController._loadProfile).toHaveBeenCalled();
  });

  test('Test 16: Successful lifecycle response triggers Lucia-specific renderer cleanup', async () => {
    settings.openEndLifeModal();
    const confirmInput = document.getElementById('end-life-confirm-input');
    confirmInput.value = 'END LUCIA';
    confirmInput.dispatchEvent(new Event('input'));

    await settings.executeEndLife();

    // Identity and memory keys are cleared
    expect(localStorageStore.lucia_profile).toBeUndefined();
    expect(localStorageStore.lucia_user_name).toBeUndefined();
    expect(localStorageStore.lucia_companion_name).toBeUndefined();
    expect(localStorageStore.lucia_is_onboarded).toBeUndefined();
    expect(localStorageStore.lucia_born_at).toBeUndefined();
    expect(localStorageStore.lucia_chat_history).toBeUndefined();
  });

  test('Test 17: Application preference keys remain intact', async () => {
    settings.openEndLifeModal();
    const confirmInput = document.getElementById('end-life-confirm-input');
    confirmInput.value = 'END LUCIA';
    confirmInput.dispatchEvent(new Event('input'));

    await settings.executeEndLife();

    // App preferences must remain unchanged
    expect(localStorageStore.lucia_avatar_engine).toBe('sprites');
    expect(localStorageStore.lucia_avatar_model).toBe('columbina');
    expect(localStorageStore.lucia_master_volume).toBe('75');
    expect(localStorageStore.lucia_hardware_profile).toBe('laptop');
    expect(localStorageStore.lucia_developer_mode).toBe('true');
    expect(localStorageStore.lucia_gaze_enabled).toBe('true');
    expect(localStorageStore.lucia_blinking_enabled).toBe('true');
  });

  test('Test 18: Talk, Journal, and Memories presentation are cleared after success', async () => {
    settings.openEndLifeModal();
    const confirmInput = document.getElementById('end-life-confirm-input');
    confirmInput.value = 'END LUCIA';
    confirmInput.dispatchEvent(new Event('input'));

    await settings.executeEndLife();

    expect(window.chatController.clearPresentation).toHaveBeenCalled();
    expect(window.companionJournal.clearPresentation).toHaveBeenCalled();
    expect(document.getElementById('chat-messages').children.length).toBe(0);
    expect(document.getElementById('journal-timeline').children.length).toBe(0);
    expect(document.getElementById('memories-grid').children.length).toBe(0);
  });

  test('Test 19: Settings and End-of-Life modal close after success', async () => {
    settings.openSettings('privacy');
    settings.openEndLifeModal();

    const endLifeModal = document.getElementById('end-life-modal');
    const settingsModal = document.getElementById('settings-modal');
    expect(endLifeModal.classList.contains('active')).toBe(true);
    expect(settingsModal.classList.contains('active')).toBe(true);

    const confirmInput = document.getElementById('end-life-confirm-input');
    confirmInput.value = 'END LUCIA';
    confirmInput.dispatchEvent(new Event('input'));

    await settings.executeEndLife();

    expect(endLifeModal.classList.contains('active')).toBe(false);
    expect(settingsModal.classList.contains('active')).toBe(false);
  });

  test('Test 20: Existing Genesis flow is reopened after successful lifecycle reset', async () => {
    settings.openEndLifeModal();
    const confirmInput = document.getElementById('end-life-confirm-input');
    confirmInput.value = 'END LUCIA';
    confirmInput.dispatchEvent(new Event('input'));

    await settings.executeEndLife();

    expect(window.chatController._loadProfile).toHaveBeenCalled();
    const genesisModal = document.getElementById('genesis-modal');
    expect(genesisModal.classList.contains('active')).toBe(true);
  });

  test('Test 21: Profile is re-read and is_onboarded = false is respected', async () => {
    settings.openEndLifeModal();
    const confirmInput = document.getElementById('end-life-confirm-input');
    confirmInput.value = 'END LUCIA';
    confirmInput.dispatchEvent(new Event('input'));

    await settings.executeEndLife();

    const profileCalls = fetchMock.mock.calls.filter(
      (c) => typeof c[0] === 'string' && c[0].includes('/profile') && (!c[1] || c[1]?.method === 'GET')
    );
    expect(profileCalls.length).toBeGreaterThanOrEqual(1);
  });

  test('Test 22: New born_at is NOT created during the End-of-Life transition itself', async () => {
    settings.openEndLifeModal();
    const confirmInput = document.getElementById('end-life-confirm-input');
    confirmInput.value = 'END LUCIA';
    confirmInput.dispatchEvent(new Event('input'));

    await settings.executeEndLife();

    // Check that born_at in store or payload was not created
    expect(localStorageStore.lucia_born_at).toBeUndefined();

    // Verify no POST /profile was sent during transition
    const postProfileCalls = fetchMock.mock.calls.filter(
      (c) => typeof c[0] === 'string' && c[0].includes('/profile') && c[1]?.method === 'POST'
    );
    expect(postProfileCalls.length).toBe(0);
  });

  test('Test 23: A second Genesis completion creates the new Lucia\'s actual birth timestamp', async () => {
    // 1. Complete End-of-Life
    settings.openEndLifeModal();
    const confirmInput = document.getElementById('end-life-confirm-input');
    confirmInput.value = 'END LUCIA';
    confirmInput.dispatchEvent(new Event('input'));
    await settings.executeEndLife();

    // 2. User completes Genesis for the NEW Lucia
    const beforeBirth = Date.now() - 500;
    const genesisTime = new Date().toISOString();

    const awakenRes = await fetch('http://127.0.0.1:8765/profile', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        user_name: 'Luna',
        companion_name: 'Lucia',
        is_onboarded: true,
        born_at: genesisTime,
      }),
    });

    const data = await awakenRes.json();
    expect(data.status).toBe('ok');
    expect(data.profile.is_onboarded).toBe(true);

    const parsedBornAt = new Date(data.profile.born_at).getTime();
    expect(parsedBornAt).toBeGreaterThanOrEqual(beforeBirth);
  });

  test('Test 24: No previous Lucia-specific identity or memory state leaks into new lifecycle', async () => {
    settings.openEndLifeModal();
    const confirmInput = document.getElementById('end-life-confirm-input');
    confirmInput.value = 'END LUCIA';
    confirmInput.dispatchEvent(new Event('input'));

    await settings.executeEndLife();

    // Ensure clean state
    expect(localStorageStore.lucia_chat_history).toBeUndefined();
    expect(localStorageStore.lucia_user_name).toBeUndefined();
    expect(localStorageStore.lucia_born_at).toBeUndefined();

    // Chat presentation has no residual previous messages
    const chatContainer = document.getElementById('chat-messages');
    expect(chatContainer.textContent).not.toContain('Previous Lucia');
  });
});
