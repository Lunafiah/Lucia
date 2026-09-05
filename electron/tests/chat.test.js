/**
 * Unit tests for ChatController (chat.js) - Phase 7.2 Talk Interface & Stage.
 * @jest-environment jsdom
 */

describe('ChatController Sub-Phase 7.2 Tests', () => {
  let ChatController;
  let State;
  let chat;

  beforeEach(() => {
    // Setup minimal DOM required for ChatController
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
          <button id="clear-screen-btn" class="dock-action-btn" title="Clear Screen (Keeps Memories)">🍃</button>
          <textarea id="chat-input" placeholder="Talk with Lucia..."></textarea>
          <button id="send-btn" class="send-action-btn">Send</button>
          <button id="mic-btn">Mic</button>
        </div>
      </div>
      <!-- Modals and controls -->
      <button id="open-profile-btn"></button>
      <button id="close-profile-btn"></button>
      <button id="save-profile-btn"></button>
      <div id="profile-modal" style="display:none"></div>
      <input id="profile-user-name-input" />
      <input id="profile-companion-name-input" />
      <span id="birthday-badge-text"></span>
      <span id="profile-born-date-display"></span>
      <span id="profile-days-count-display"></span>

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
      <button id="voice-mute-btn"></button>
      <input id="voice-volume-slider" type="range" />

      <select id="avatar-engine-select"></select>
      <select id="avatar-model-select"></select>
      <button id="toggle-mascot-btn"></button>
    `;

    // Mock global window objects
    window.fetch = jest.fn().mockImplementation(() =>
      Promise.resolve({
        ok: true,
        json: () => Promise.resolve({ models: [], profiles: [] }),
      })
    );

    window.lucia = {
      state: { get: jest.fn() },
      on: jest.fn(),
      models: { getVoices: jest.fn().mockResolvedValue({ models: [] }) },
      window: { toggleMascot: jest.fn() },
    };

    // Require ChatController module
    const chatModule = require('../renderer/chat/chat.js');
    ChatController = chatModule.ChatController;
    State = chatModule.State;

    chat = new ChatController();
  });

  afterEach(() => {
    jest.clearAllMocks();
  });

  test('initializes with WAITING_BACKEND state and references DOM elements', () => {
    expect(chat.currentState).toBe(State.WAITING_BACKEND);
    expect(chat.messagesContainer).not.toBeNull();
    expect(chat.inputArea).not.toBeNull();
    expect(chat.clearScreenBtn).not.toBeNull();
    expect(chat.organicStatusLabel).not.toBeNull();
  });

  describe('clearScreen()', () => {
    test('clears visible chat bubbles and inserts memory safety notice', () => {
      // Add mock messages
      chat.appendMessage('user', 'Hello Lucia!');
      chat.appendMessage('companion', 'Hello there, friend.');
      expect(chat.messagesContainer.children.length).toBe(2);

      // Execute clearScreen
      chat.clearScreen();

      // Container should now only have the safety notice
      expect(chat.messagesContainer.children.length).toBe(1);
      const notice = chat.messagesContainer.querySelector('.clear-screen-notice');
      expect(notice).not.toBeNull();
      expect(notice.textContent).toContain('Screen cleared • Memories and emotional bond remain untouched');
    });

    test('is invoked when clear-screen-btn is clicked', () => {
      const clearSpy = jest.spyOn(chat, 'clearScreen');
      chat.clearScreenBtn.click();
      expect(clearSpy).toHaveBeenCalled();
    });
  });

  describe('appendMessage()', () => {
    test('renders user message bubble with correct classes and text', () => {
      const row = chat.appendMessage('user', 'How are you feeling today?');
      expect(row.classList.contains('message-row')).toBe(true);
      expect(row.classList.contains('user')).toBe(true);

      const bubble = row.querySelector('.message-bubble');
      expect(bubble).not.toBeNull();
      expect(bubble.textContent).toBe('How are you feeling today?');
    });

    test('renders companion message bubble with header, text, and voice replay button', () => {
      const row = chat.appendMessage('companion', 'I feel serene and happy to be with you.');
      expect(row.classList.contains('message-row')).toBe(true);
      expect(row.classList.contains('companion')).toBe(true);

      const header = row.querySelector('.companion-bubble-header');
      expect(header).not.toBeNull();
      expect(header.textContent).toContain('Lucia');

      const text = row.querySelector('.bubble-text');
      expect(text).not.toBeNull();
      expect(text.textContent).toBe('I feel serene and happy to be with you.');

      const replayBtn = row.querySelector('.audio-replay-btn');
      expect(replayBtn).not.toBeNull();
      expect(replayBtn.textContent).toContain('Replay');
    });

    test('clicking audio-replay-btn calls _replayVoice', () => {
      const replaySpy = jest.spyOn(chat, '_replayVoice').mockImplementation(() => {});
      const row = chat.appendMessage('companion', 'Testing voice replay click.');
      const replayBtn = row.querySelector('.audio-replay-btn');

      replayBtn.click();
      expect(replaySpy).toHaveBeenCalledWith('Testing voice replay click.', replayBtn);
    });
  });

  describe('Twinkle Typing Indicator', () => {
    test('showTypingIndicator renders 3 sparkle stars ✦ ✦ ✦', () => {
      const row = chat.showTypingIndicator();
      expect(row.classList.contains('typing-row')).toBe(true);
      expect(row.classList.contains('companion')).toBe(true);

      const twinkle = row.querySelector('.typing-twinkle');
      expect(twinkle).not.toBeNull();

      const stars = row.querySelectorAll('.twinkle-star');
      expect(stars.length).toBe(3);
      stars.forEach((star) => {
        expect(star.textContent).toBe('✦');
      });
    });

    test('removeTypingIndicator removes indicator from container', () => {
      const row = chat.showTypingIndicator();
      expect(chat.messagesContainer.contains(row)).toBe(true);

      chat.removeTypingIndicator(row);
      expect(chat.messagesContainer.contains(row)).toBe(false);
    });
  });

  describe('Organic Status Mapping & Updates', () => {
    test('maps lifecycle and conversation states to descriptive strings', () => {
      expect(chat.mapPADToStatusText(null, State.SENDING)).toBe('Lucia is contemplating...');
      expect(chat.mapPADToStatusText(null, State.WAITING_BACKEND)).toBe('Lucia is awakening...');
      expect(chat.mapPADToStatusText(null, State.ERROR)).toBe('Lucia is resting');

      chat.isSpeakingOrProcessing = true;
      expect(chat.mapPADToStatusText()).toBe('Lucia is speaking gently...');
      chat.isSpeakingOrProcessing = false;

      chat.isMicMode = true;
      expect(chat.mapPADToStatusText()).toBe('Lucia is listening warmly...');
      chat.isMicMode = false;
    });

    test('maps PAD coordinates to emotional status expressions', () => {
      // High pleasure
      expect(chat.mapPADToStatusText({ pleasure: 0.6, arousal: 0, dominance: 0 })).toBe('Lucia feels happy and connected');
      // Low pleasure
      expect(chat.mapPADToStatusText({ pleasure: -0.4, arousal: 0, dominance: 0 })).toBe('Lucia feels tender and reflective');
      // High arousal
      expect(chat.mapPADToStatusText({ pleasure: 0, arousal: 0.5, dominance: 0 })).toBe('Lucia is alert and engaged');
      // Low arousal
      expect(chat.mapPADToStatusText({ pleasure: 0, arousal: -0.3, dominance: 0 })).toBe('Lucia feels quiet and serene');
      // High dominance
      expect(chat.mapPADToStatusText({ pleasure: 0, arousal: 0, dominance: 0.5 })).toBe('Lucia feels grounded and confident');
      // Gentle pleasure
      expect(chat.mapPADToStatusText({ pleasure: 0.2, arousal: 0, dominance: 0 })).toBe('Lucia feels warm and gentle');
      // Neutral
      expect(chat.mapPADToStatusText({ pleasure: 0, arousal: 0, dominance: 0 })).toBe('Lucia feels peaceful');
    });

    test('updateOrganicStatus updates both avatar status text and header state label', () => {
      chat.updateOrganicStatus({ pleasure: 0.5, arousal: 0.1, dominance: 0.1 });

      const expected = 'Lucia feels happy and connected';
      expect(chat.organicStatusLabel.textContent).toBe(expected);
      expect(chat.stateLabel.textContent).toBe(expected);
      expect(chat.currentPAD.pleasure).toBe(0.5);
    });
  });
});
