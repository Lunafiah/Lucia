/**
 * Focused regression tests for Voice Synthesis, Error Propagation, and Playback Lifecycle.
 * @jest-environment jsdom
 */

describe('Voice Synthesis and Playback Lifecycle Tests', () => {
  let ChatController;
  let chat;
  let speakMock;

  beforeEach(() => {
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
          <textarea id="chat-input"></textarea>
          <button id="send-btn">Send</button>
          <button id="mic-btn">Mic</button>
        </div>
      </div>
      <!-- modals -->
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

    speakMock = jest.fn((blob, onEnded) => {
      if (typeof onEnded === 'function') onEnded();
    });

    window.avatarRenderer = {
      speak: speakMock,
    };

    window.lucia = {
      state: { get: jest.fn() },
      on: jest.fn(),
      models: { getVoices: jest.fn().mockResolvedValue({ models: [] }) },
      window: { toggleMascot: jest.fn() },
      chat: {
        send: jest.fn().mockResolvedValue({
          response: 'Hello Luna, I am here.',
          expression: { voice: { rate_pct: 0, volume_pct: 0, pitch_shift_hz: 0 } },
        }),
      },
      voice: {
        synthesize: jest.fn(),
      },
    };

    window.fetch = jest.fn().mockImplementation(() =>
      Promise.resolve({
        ok: true,
        json: () => Promise.resolve({ models: [], profiles: [] }),
      })
    );
    global.fetch = window.fetch;

    const chatModule = require('../renderer/chat/chat.js');
    ChatController = chatModule.ChatController;
    chat = new ChatController();
  });

  afterEach(() => {
    jest.clearAllMocks();
  });

  test('1. Successful voice synthesis produces audio and triggers avatar speak', async () => {
    const fakeAudioBuffer = new Uint8Array([0xFF, 0xFB, 0x90, 0x64]).buffer;
    window.lucia.voice.synthesize.mockResolvedValue(fakeAudioBuffer);

    // Mock fetch for send turn
    window.fetch = jest.fn().mockResolvedValue({
      ok: true,
      json: () =>
        Promise.resolve({
          response: 'Hello Luna, I am here.',
          expression: { voice: { rate_pct: 0, volume_pct: 0, pitch_shift_hz: 0 } },
        }),
    });
    global.fetch = window.fetch;

    chat.inputArea.value = 'Hello';
    await chat.sendMessage();

    expect(window.lucia.voice.synthesize).toHaveBeenCalledWith('Hello Luna, I am here.', expect.any(Object));
    expect(speakMock).toHaveBeenCalledTimes(1);
    expect(chat.audioCache.has('Hello Luna, I am here.')).toBe(true);
  });

  test('2. Replay voice reuses cached audio Blob without re-synthesizing', async () => {
    const fakeBlob = new Blob([new Uint8Array([1, 2, 3])], { type: 'audio/mpeg' });
    chat.audioCache = new Map();
    chat.audioCache.set('Cached utterance', fakeBlob);

    const replayBtn = document.createElement('button');
    await chat._replayVoice('Cached utterance', replayBtn);

    expect(speakMock).toHaveBeenCalledWith(fakeBlob, expect.any(Function));
    expect(window.lucia.voice.synthesize).not.toHaveBeenCalled();
    expect(replayBtn.classList.contains('playing')).toBe(false);
  });

  test('3. Replay synthesizes and caches audio if not previously cached', async () => {
    const fakeAudioBuffer = new Uint8Array([4, 5, 6]).buffer;
    window.lucia.voice.synthesize.mockResolvedValue(fakeAudioBuffer);

    const replayBtn = document.createElement('button');
    await chat._replayVoice('New utterance', replayBtn);

    expect(window.lucia.voice.synthesize).toHaveBeenCalledWith('New utterance');
    expect(speakMock).toHaveBeenCalledTimes(1);
    expect(chat.audioCache.has('New utterance')).toBe(true);
    expect(replayBtn.classList.contains('playing')).toBe(false);
  });

  test('4. Synthesis failure rejects and is observable without masking as success', async () => {
    const warnSpy = jest.spyOn(console, 'warn').mockImplementation(() => {});
    window.lucia.voice.synthesize.mockRejectedValue(new Error('Voice synthesis HTTP 500'));

    const replayBtn = document.createElement('button');
    await chat._replayVoice('Failing utterance', replayBtn);

    expect(speakMock).not.toHaveBeenCalled();
    expect(replayBtn.classList.contains('playing')).toBe(false);
    expect(chat.isSpeakingOrProcessing).toBe(false);
    expect(warnSpy).toHaveBeenCalledWith(
      expect.stringContaining('[voice]'),
      expect.any(Error)
    );
    warnSpy.mockRestore();
  });

  test('5. Realization decoupling: text is in user language while voice is Japanese with explicit language', async () => {
    const fakeAudioBuffer = new Uint8Array([10, 20, 30]).buffer;
    window.lucia.voice.synthesize.mockResolvedValue(fakeAudioBuffer);

    window.lucia.chat.send.mockResolvedValue({
      response: 'Hello Luna, I am here with you.',
      realization: {
        text: {
          content: 'Hello Luna, I am here with you.',
          language: 'en'
        },
        voice: {
          content: 'こんにちは、ルナ。一緒にいます。',
          language: 'ja'
        }
      },
      expression: { voice: { speech_rate_pct: 0, volume_pct: 0, pitch_shift_hz: 0 } },
    });

    chat.inputArea.value = 'Hello';
    await chat.sendMessage();

    // Text message rendered in chat pane is user language (en)
    const messages = chat.messagesContainer.querySelectorAll('.bubble-text');
    expect(messages[messages.length - 1].textContent).toBe('Hello Luna, I am here with you.');

    // Voice sent to synthesis is Japanese realization with explicit language = 'ja'
    expect(window.lucia.voice.synthesize).toHaveBeenCalledWith(
      'こんにちは、ルナ。一緒にいます。',
      expect.objectContaining({ language: 'ja' })
    );
    expect(speakMock).toHaveBeenCalledTimes(1);
    expect(chat.audioCache.has('Hello Luna, I am here with you.')).toBe(true);
    expect(chat.audioCache.has('こんにちは、ルナ。一緒にいます。')).toBe(true);
  });
});
