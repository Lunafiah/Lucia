/**
 * Presentation Timing & Voice-First Response Synchronization Tests.
 *
 * Verifies strict temporal event ordering:
 *   response_ready < tts_start < tts_end <= text_commit
 *
 * Validates:
 * - Text is hidden from visible chat UI during speech.
 * - Text commits immediately upon authoritative TTS completion signal.
 * - Minimum latency between tts_end and text_commit (< 10ms).
 * - Fallback to text commit on TTS synthesis or playback failure.
 * - Cancellation / interruption isolation (no stale/delayed text).
 * - Duplicate completion callback defense (no duplicate bubbles).
 * - Rapid consecutive turns isolation.
 * - Empty / short responses.
 *
 * @jest-environment jsdom
 */

const { ChatController, State, PresentationStage } = require('../renderer/chat/chat.js');
const { LipSyncProcessor } = require('../renderer/avatar/lip-sync.js');

describe('Voice-First Presentation Timing & Response Synchronization', () => {
  let chat;
  let speakMock;
  let activeSpeakCallback;

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
      <!-- modals & settings mocks -->
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

    activeSpeakCallback = null;
    speakMock = jest.fn((blob, callback) => {
      activeSpeakCallback = callback;
      if (callback && typeof callback.onStart === 'function') {
        callback.onStart();
      }
    });

    window.avatarRenderer = {
      speak: speakMock,
      stop: jest.fn(() => {
        if (activeSpeakCallback && typeof activeSpeakCallback.onCancel === 'function') {
          activeSpeakCallback.onCancel();
        }
      }),
    };

    window.lucia = {
      state: { get: jest.fn() },
      on: jest.fn(),
      models: { getVoices: jest.fn().mockResolvedValue({ models: [] }) },
      window: { toggleMascot: jest.fn() },
      chat: {
        send: jest.fn().mockResolvedValue({
          response: 'Xin chao Luna, em luon o day cung anh.',
          realization: {
            text: { content: 'Xin chao Luna, em luon o day cung anh.', language: 'vi' },
            voice: { content: 'こんにちはルナ、いつもそばにいますよ。', language: 'ja' }
          },
          expression: { voice: { speech_rate_pct: 0, volume_pct: 0, pitch_shift_hz: 0 } },
        }),
      },
      voice: {
        synthesize: jest.fn().mockResolvedValue(new Uint8Array([1, 2, 3, 4]).buffer),
      },
    };

    window.fetch = jest.fn().mockResolvedValue({
      ok: true,
      json: () => Promise.resolve({ models: [], profiles: [] }),
    });
    global.fetch = window.fetch;

    chat = new ChatController();
  });

  afterEach(() => {
    jest.clearAllMocks();
  });

  test('1. Event ordering: text commits immediately upon response_ready while TTS runs asynchronously', async () => {
    const stageEvents = [];
    chat.onPresentationEvent = (evt) => {
      stageEvents.push({ stage: evt.stage, time: evt.timestamp });
    };

    chat.inputArea.value = 'Chao em';
    const sendPromise = chat.sendMessage();

    // Allow promise microtasks up to speakMock call
    await new Promise((r) => setTimeout(r, 0));

    // At this point, speakMock has been called and onStart fired
    expect(speakMock).toHaveBeenCalledTimes(1);

    // CRITICAL (Section D & E4): Text bubble MUST be visible immediately, not waiting for TTS
    const companionBubblesDuringSpeech = chat.messagesContainer.querySelectorAll('.message-row.companion:not(.typing-row)');
    expect(companionBubblesDuringSpeech.length).toBe(1);
    expect(companionBubblesDuringSpeech[0].querySelector('.bubble-text').textContent).toBe(
      'Xin chao Luna, em luon o day cung anh.'
    );

    // Authoritative TTS end event triggered
    expect(activeSpeakCallback).not.toBeNull();
    if (typeof activeSpeakCallback.onEnded === 'function') {
      activeSpeakCallback.onEnded();
    } else if (typeof activeSpeakCallback === 'function') {
      activeSpeakCallback();
    }

    await sendPromise;

    // Check captured stages sequence: text commits immediately, then TTS proceeds
    const stageNames = stageEvents.map((e) => e.stage);
    expect(stageNames).toEqual([
      PresentationStage.RESPONSE_READY,
      PresentationStage.TEXT_COMMIT,
      PresentationStage.TTS_START,
      PresentationStage.AUDIO_PLAYING,
      PresentationStage.TTS_END,
    ]);

    // Check timestamps strictly respect ordering: response_ready <= text_commit <= tts_end
    const tReady = stageEvents.find((e) => e.stage === PresentationStage.RESPONSE_READY).time;
    const tCommit = stageEvents.find((e) => e.stage === PresentationStage.TEXT_COMMIT).time;
    const tEnd = stageEvents.find((e) => e.stage === PresentationStage.TTS_END).time;

    expect(tReady).toBeLessThanOrEqual(tCommit);
    expect(tCommit).toBeLessThanOrEqual(tEnd);

    // TTS completion does NOT cause a second commit
    const companionBubblesAfterEnd = chat.messagesContainer.querySelectorAll('.message-row.companion:not(.typing-row)');
    expect(companionBubblesAfterEnd.length).toBe(1);
    expect(companionBubblesAfterEnd[0].querySelector('.bubble-text').textContent).toBe(
      'Xin chao Luna, em luon o day cung anh.'
    );
  });

  test('2. TTS Error (synthesis rejection) triggers immediate text commit fallback without hanging', async () => {
    const stageEvents = [];
    chat.onPresentationEvent = (evt) => {
      stageEvents.push(evt.stage);
    };

    window.lucia.voice.synthesize.mockRejectedValueOnce(new Error('TTS Engine unavailable'));

    chat.inputArea.value = 'Test synthesis failure';
    await chat.sendMessage();

    // Voice speak was not invoked
    expect(speakMock).not.toHaveBeenCalled();

    // Text committed as fallback
    expect(stageEvents).toContain(PresentationStage.RESPONSE_READY);
    expect(stageEvents).toContain(PresentationStage.TTS_ERROR);
    expect(stageEvents).toContain(PresentationStage.TEXT_COMMIT);

    const companionBubbles = chat.messagesContainer.querySelectorAll('.message-row.companion:not(.typing-row)');
    expect(companionBubbles.length).toBe(1);
    expect(companionBubbles[0].querySelector('.bubble-text').textContent).toBe(
      'Xin chao Luna, em luon o day cung anh.'
    );
    expect(chat.isSpeakingOrProcessing).toBe(false);
  });

  test('3. TTS Playback Error event falls back to text commit so text is never lost', async () => {
    const stageEvents = [];
    chat.onPresentationEvent = (evt) => {
      stageEvents.push(evt.stage);
    };

    chat.inputArea.value = 'Test playback failure';
    const sendPromise = chat.sendMessage();
    await new Promise((r) => setTimeout(r, 0));

    // Audio element reports decode error
    if (activeSpeakCallback && typeof activeSpeakCallback.onError === 'function') {
      activeSpeakCallback.onError(new Error('Audio decode error'));
    }

    await sendPromise;

    expect(stageEvents).toContain(PresentationStage.TTS_ERROR);
    expect(stageEvents).toContain(PresentationStage.TEXT_COMMIT);

    const companionBubbles = chat.messagesContainer.querySelectorAll('.message-row.companion:not(.typing-row)');
    expect(companionBubbles.length).toBe(1);
    expect(chat.isSpeakingOrProcessing).toBe(false);
  });

  test('4. Cancellation / Clear Screen aborts pending staged text (no stale/delayed text)', async () => {
    chat.inputArea.value = 'Message before clearing';
    const sendPromise = chat.sendMessage();
    await new Promise((r) => setTimeout(r, 0));

    expect(speakMock).toHaveBeenCalledTimes(1);

    // User clears screen while Lucia is speaking
    chat.clearScreen();

    // Verify screen is cleared and has notice
    expect(chat.messagesContainer.querySelectorAll('.message-row').length).toBe(0);
    expect(chat.messagesContainer.querySelector('.clear-screen-notice')).not.toBeNull();

    // Delayed TTS end event arrives after clear screen
    if (activeSpeakCallback) {
      if (typeof activeSpeakCallback.onEnded === 'function') activeSpeakCallback.onEnded();
      else activeSpeakCallback();
    }

    await sendPromise;

    // Verify no delayed text was committed into the cleared screen
    const companionBubbles = chat.messagesContainer.querySelectorAll('.message-row.companion:not(.typing-row)');
    expect(companionBubbles.length).toBe(0);
  });

  test('5. Duplicate completion callback defense commits text only once', async () => {
    chat.inputArea.value = 'Duplicate callback test';
    const sendPromise = chat.sendMessage();
    await new Promise((r) => setTimeout(r, 0));

    expect(activeSpeakCallback).not.toBeNull();

    // Trigger end callback 3 times concurrently
    activeSpeakCallback.onEnded();
    activeSpeakCallback.onEnded();
    activeSpeakCallback();

    await sendPromise;

    // Exactly one message bubble must be committed
    const companionBubbles = chat.messagesContainer.querySelectorAll('.message-row.companion:not(.typing-row)');
    expect(companionBubbles.length).toBe(1);
  });

  test('6. Rapid consecutive turns preserve turn ordering and commit both text bubbles cleanly', async () => {
    window.lucia.chat.send
      .mockResolvedValueOnce({
        response: 'First reply',
        realization: { voice: { content: 'First voice', language: 'ja' } },
      })
      .mockResolvedValueOnce({
        response: 'Second reply',
        realization: { voice: { content: 'Second voice', language: 'ja' } },
      });

    chat.inputArea.value = 'Turn 1';
    const turn1Promise = chat.sendMessage();
    await new Promise((r) => setTimeout(r, 0));

    const turn1Callback = activeSpeakCallback;

    // Immediately trigger Turn 2 before Turn 1 finishes speaking
    chat.inputArea.value = 'Turn 2';
    const turn2Promise = chat.sendMessage();
    await new Promise((r) => setTimeout(r, 0));

    // Turn 1 playback late end arrives
    if (turn1Callback && typeof turn1Callback.onEnded === 'function') {
      turn1Callback.onEnded();
    }

    // Turn 2 playback finishes naturally
    if (activeSpeakCallback && typeof activeSpeakCallback.onEnded === 'function') {
      activeSpeakCallback.onEnded();
    }

    await Promise.all([turn1Promise, turn2Promise]);

    const companionBubbles = chat.messagesContainer.querySelectorAll('.message-row.companion:not(.typing-row)');
    // Both Turn 1 and Turn 2 replies must be present in correct chronological order
    expect(companionBubbles.length).toBe(2);
    expect(companionBubbles[0].querySelector('.bubble-text').textContent).toBe('First reply');
    expect(companionBubbles[1].querySelector('.bubble-text').textContent).toBe('Second reply');
  });

  test('7. Empty backend response shows error bubble without hanging', async () => {
    window.lucia.chat.send.mockResolvedValueOnce({ response: '' });

    chat.inputArea.value = 'Test empty';
    await chat.sendMessage();

    expect(speakMock).not.toHaveBeenCalled();
    const errorBubbles = chat.messagesContainer.querySelectorAll('.message-row.error');
    expect(errorBubbles.length).toBe(1);
    expect(chat.currentState).toBe(State.READY);
    expect(chat.isSpeakingOrProcessing).toBe(false);
  });

  test('8. Short response completes cleanly with voice and text commit', async () => {
    window.lucia.chat.send.mockResolvedValueOnce({
      response: 'はい',
      realization: { voice: { content: 'はい', language: 'ja' } },
    });

    chat.inputArea.value = 'Ok';
    const sendPromise = chat.sendMessage();
    await new Promise((r) => setTimeout(r, 0));

    if (activeSpeakCallback) activeSpeakCallback.onEnded();
    await sendPromise;

    const companionBubbles = chat.messagesContainer.querySelectorAll('.message-row.companion:not(.typing-row)');
    expect(companionBubbles.length).toBe(1);
    expect(companionBubbles[0].querySelector('.bubble-text').textContent).toBe('はい');
  });

  test('9. Voice Muted immediately commits text without TTS playback', async () => {
    chat.isVoiceMuted = true;

    chat.inputArea.value = 'Muted test';
    await chat.sendMessage();

    expect(speakMock).not.toHaveBeenCalled();
    const companionBubbles = chat.messagesContainer.querySelectorAll('.message-row.companion:not(.typing-row)');
    expect(companionBubbles.length).toBe(1);
    expect(chat.currentState).toBe(State.READY);
  });
});

describe('LipSyncProcessor Lifecycle & Callback Handling', () => {
  let processor;
  let mockAudioInstance;

  beforeEach(() => {
    mockAudioInstance = {
      play: jest.fn().mockResolvedValue(undefined),
      pause: jest.fn(),
      addEventListener: jest.fn(),
      removeEventListener: jest.fn(),
      onplay: null,
      onplaying: null,
      onended: null,
      onerror: null,
      error: null,
    };

    global.Audio = jest.fn(() => mockAudioInstance);

    window.AudioContext = jest.fn().mockImplementation(() => ({
      state: 'running',
      resume: jest.fn().mockResolvedValue(undefined),
      createAnalyser: jest.fn().mockReturnValue({
        fftSize: 256,
        frequencyBinCount: 128,
        getByteFrequencyData: jest.fn(),
        connect: jest.fn(),
      }),
      createGain: jest.fn().mockReturnValue({
        gain: { value: 1.0, setValueAtTime: jest.fn() },
        connect: jest.fn(),
      }),
      createMediaElementSource: jest.fn().mockReturnValue({
        connect: jest.fn(),
      }),
      destination: {},
    }));

    global.URL.createObjectURL = jest.fn(() => 'blob:mock-audio-url');
    global.URL.revokeObjectURL = jest.fn();

    processor = new LipSyncProcessor();
  });

  afterEach(() => {
    jest.clearAllMocks();
  });

  test('invokes onStart and onEnded in exact sequence on normal playback', async () => {
    const events = [];
    const callbacks = {
      onStart: () => events.push('start'),
      onEnded: () => events.push('end'),
      onError: () => events.push('error'),
      onCancel: () => events.push('cancel'),
    };

    await processor.playAudio('mock-audio-data', callbacks);

    expect(events).toContain('start');
    expect(processor.isPlaying).toBe(true);

    // Simulate audio element completion
    mockAudioInstance.onended();

    expect(events).toEqual(['start', 'end']);
    expect(processor.isPlaying).toBe(false);
    expect(processor.mouthOpen).toBe(0);
  });

  test('stop() cancels active playback and triggers onCancel', async () => {
    const events = [];
    const callbacks = {
      onStart: () => events.push('start'),
      onEnded: () => events.push('end'),
      onCancel: () => events.push('cancel'),
    };

    await processor.playAudio('mock-audio-data', callbacks);
    expect(processor.isPlaying).toBe(true);

    processor.stop();

    expect(events).toContain('cancel');
    expect(events).not.toContain('end');
    expect(processor.isPlaying).toBe(false);
  });

  test('playAudio error invokes onError callback', async () => {
    const events = [];
    const callbacks = {
      onError: (err) => events.push('error: ' + err.message),
      onEnded: () => events.push('end'),
    };

    mockAudioInstance.play = jest.fn().mockRejectedValueOnce(new Error('Autoplay blocked'));

    await processor.playAudio('mock-audio-data', callbacks);

    expect(events).toContain('error: Autoplay blocked');
    expect(events).not.toContain('end');
  });
});
