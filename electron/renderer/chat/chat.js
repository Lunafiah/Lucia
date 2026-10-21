/**
 * Chat Window Controller (chat.js)
 * Manages message feed, input interaction, typing indicators, and backend readiness.
 *
 * Requirements: Phase 3 (6.1–6.9, 11.1, 11.2)
 */

const State = {
  WAITING_BACKEND: 'WAITING_BACKEND',
  READY: 'READY',
  SENDING: 'SENDING',
  ERROR: 'ERROR'
};

const PresentationStage = {
  RESPONSE_READY: 'RESPONSE_READY',
  TTS_START: 'TTS_START',
  AUDIO_PLAYING: 'AUDIO_PLAYING',
  TTS_END: 'TTS_END',
  TEXT_COMMIT: 'TEXT_COMMIT',
  TTS_ERROR: 'TTS_ERROR',
  TTS_CANCEL: 'TTS_CANCEL',
};

class ChatController {
  constructor() {
    this.currentState = State.WAITING_BACKEND;
    this.messagesContainer = document.getElementById('chat-messages');
    this.inputArea = document.getElementById('chat-input');
    this.sendBtn = document.getElementById('send-btn');
    this.splashOverlay = document.getElementById('splash');
    this.statusDot = document.getElementById('companion-status-dot');
    this.stateLabel = document.getElementById('companion-state-label');
    this.hardwareBadge = document.getElementById('hardware-badge');

    // Voice & Avatar Presence
    this.voiceModelSelect = document.getElementById('voice-model-select');
    this.voiceMuteBtn = document.getElementById('voice-mute-btn');
    this.volumeSlider = document.getElementById('voice-volume-slider');
    this.isVoiceMuted = false;

    // Avatar Controls
    this.avatarEngineSelect = document.getElementById('avatar-engine-select');
    this.avatarModelSelect = document.getElementById('avatar-model-select');
    this.avatarModelsData = { engines: ['canvas', 'sprites', 'live2d', 'vrm'], sprites: [], live2d: [], vrm: [] };

    // Discord-style Continuous Mic Mode (Local Whisper STT + MediaRecorder + Web Audio VAD)
    this.micBtn = document.getElementById('mic-btn');
    this.isMicMode = false;
    this.isSpeakingOrProcessing = false;
    this.silenceTimer = null;
    this.mediaRecorder = null;
    this.audioStream = null;
    this.audioChunks = [];
    this.audioContext = null;
    this.analyser = null;
    this.vadInterval = null;
    this.hasSpoken = false;
    this.silenceStartTime = 0;

    // Genesis Awakening Modal (Phase 7.7) & Profile references
    this.genesisModal = document.getElementById('genesis-modal') || document.getElementById('profile-modal');
    this.profileModal = this.genesisModal;
    this.genesisUserNameInput = document.getElementById('genesis-user-name-input') || document.getElementById('profile-user-name-input');
    this.userNameInput = this.genesisUserNameInput;
    this.genesisCompanionNameInput = document.getElementById('genesis-companion-name-input') || document.getElementById('profile-companion-name-input');
    this.companionNameInput = this.genesisCompanionNameInput;
    this.genesisAwakenBtn = document.getElementById('genesis-awaken-btn') || document.getElementById('save-profile-btn');
    this.saveProfileBtn = this.genesisAwakenBtn;
    this.genesisIntroText = document.getElementById('genesis-intro-text');
    this.openProfileBtn = document.getElementById('open-profile-btn');
    this.closeProfileBtn = document.getElementById('close-profile-btn');
    this.birthdayBadgeText = document.getElementById('birthday-badge-text');
    this.profileBornDateDisplay = document.getElementById('profile-born-date-display');
    this.profileDaysCountDisplay = document.getElementById('profile-days-count-display');

    // System Settings & Hardware Scalability Modal
    this.openSettingsBtn = document.getElementById('open-settings-btn');
    this.closeSettingsBtn = document.getElementById('close-settings-btn');
    this.settingsModal = document.getElementById('settings-modal');
    this.settingsProfileSelect = document.getElementById('settings-profile-select');
    this.settingsFpsSelect = document.getElementById('settings-fps-select');
    this.settingsMascotOpacity = document.getElementById('settings-mascot-opacity');
    this.settingsOpacityVal = document.getElementById('settings-opacity-val');
    this.settingsActiveTier = document.getElementById('settings-active-tier');
    this.settingsVramBudget = document.getElementById('settings-vram-budget');
    this.settingsCtxLength = document.getElementById('settings-ctx-length');
    this.settingsInputDeviceSelect = document.getElementById('settings-input-device-select');
    this.settingsOutputDeviceSelect = document.getElementById('settings-output-device-select');
    this.saveSettingsBtn = document.getElementById('save-settings-btn');

    this.clearScreenBtn = document.getElementById('clear-screen-btn');
    this.organicStatusLabel = document.getElementById('avatar-status-text');
    this.audioCache = new Map();
    this.currentPAD = { pleasure: 0.2, arousal: 0, dominance: 0.05 };

    // Presentation / Voice-First Response Lifecycle (Stage Tracking & Turn Isolation)
    this._turnSeq = 0;
    this._activeTurnId = 0;
    this._stagedTurn = null;
    this._lastPresentationStage = null;
    this.onPresentationEvent = null;

    window.chatController = this;

    // Initialize Companion Settings Controller (Phase 7.5)
    if (typeof CompanionSettings !== 'undefined') {
      window.companionSettings = new CompanionSettings();
    }

    // Initialize Canvas Avatar
    const canvas = document.getElementById('avatar-canvas');
    if (canvas && typeof AvatarRenderer !== 'undefined') {
      window.avatarRenderer = new AvatarRenderer(canvas);
      const savedFps = parseInt(localStorage.getItem('lucia_target_fps') || '60', 10);
      if (window.avatarRenderer.setTargetFps) {
        window.avatarRenderer.setTargetFps(savedFps);
      }
      if (this.settingsFpsSelect) {
        this.settingsFpsSelect.value = savedFps.toString();
      }
    }

    // Mascot Mode Toggle Button
    const mascotBtn = document.getElementById('toggle-mascot-btn');
    if (mascotBtn) {
      mascotBtn.addEventListener('click', () => {
        if (window.lucia && window.lucia.window && window.lucia.window.toggleMascot) {
          window.lucia.window.toggleMascot();
        }
      });
    }

    // Mascot Mode Window Detection (e.g. ?mode=mascot)
    const urlParams = new URLSearchParams(window.location.search);
    if (urlParams.get('mode') === 'mascot') {
      document.body.classList.add('mascot-mode');
      if (this.splashOverlay) this.splashOverlay.style.display = 'none';
      this.transitionTo(State.READY);
      const wrapper = document.querySelector('.avatar-canvas-wrapper') || document.body;
      if (wrapper) {
        wrapper.addEventListener('dblclick', () => {
          if (window.lucia && window.lucia.window && window.lucia.window.toggleMascot) {
            window.lucia.window.toggleMascot();
          }
        });
      }
    }

    this._setupEventListeners();
    this._setupVoiceControls();
    this._setupAvatarControls();
    this._setupAudioRecording();
    this._setupProfileControls();
    this._setupSettingsControls();
    this._setupBackendListeners();

    // Immediately scan and load models (does not require waiting for python backend)
    this._loadAvatarModels();
    this._loadVoiceModels();
    this.populateAudioDevices();
    this._loadSystemProfile();
  }

  _setupVoiceControls() {
    if (this.volumeSlider) {
      this.volumeSlider.addEventListener('input', (e) => {
        const vol = parseFloat(e.target.value);
        const mascotVol = document.getElementById('mascot-volume-slider');
        if (mascotVol) mascotVol.value = vol;
        if (window.audioRouter) {
          window.audioRouter.setVolume(vol);
        } else if (window.avatarRenderer) {
          window.avatarRenderer.setVolume(vol);
        }
      });
    }

    const mascotVol = document.getElementById('mascot-volume-slider');
    if (mascotVol) {
      mascotVol.addEventListener('input', (e) => {
        const vol = parseFloat(e.target.value);
        if (this.volumeSlider) this.volumeSlider.value = vol;
        if (window.audioRouter) {
          window.audioRouter.setVolume(vol);
        } else if (window.avatarRenderer) {
          window.avatarRenderer.setVolume(vol);
        }
      });
    }

    if (this.voiceMuteBtn) {
      this.voiceMuteBtn.addEventListener('click', () => {
        this.isVoiceMuted = !this.isVoiceMuted;
        this.voiceMuteBtn.classList.toggle('muted', this.isVoiceMuted);
        if (this.isVoiceMuted && window.avatarRenderer) {
          window.avatarRenderer.lipSync.stop();
        }
      });
    }

    if (this.voiceModelSelect) {
      this.voiceModelSelect.addEventListener('change', async (e) => {
        const modelName = e.target.value;
        const mascotVoice = document.getElementById('mascot-voice-select');
        if (mascotVoice) mascotVoice.value = modelName;
        try {
          await window.lucia.voice.selectModel(modelName);
          console.log(`[voice] Selected model: ${modelName}`);
        } catch (err) {
          console.error('[voice] Failed to select voice model:', err);
        }
      });
    }

    const mascotVoice = document.getElementById('mascot-voice-select');
    if (mascotVoice) {
      mascotVoice.addEventListener('change', async (e) => {
        const modelName = e.target.value;
        if (this.voiceModelSelect) this.voiceModelSelect.value = modelName;
        try {
          await window.lucia.voice.selectModel(modelName);
          console.log(`[voice] Selected mascot model: ${modelName}`);
        } catch (err) {
          console.error('[voice] Failed to select voice model from mascot toolbar:', err);
        }
      });
    }
  }

  async _loadVoiceModels() {
    try {
      let data = null;
      if (window.lucia && window.lucia.voice && window.lucia.voice.getModels) {
        data = await window.lucia.voice.getModels();
      }

      if (data && data.models && data.models.length > 0) {
        const fillOptions = (selectEl) => {
          if (!selectEl) return;
          selectEl.innerHTML = '';
          data.models.forEach((m) => {
            const opt = document.createElement('option');
            opt.value = m.name;
            opt.textContent = m.name === 'default' ? '🎙️ Base Voice (Default)' : `🎙️ ${m.name} (RVC)`;
            if (m.is_active) opt.selected = true;
            selectEl.appendChild(opt);
          });
        };

        if (this.voiceModelSelect) fillOptions(this.voiceModelSelect);
        const mascotVoice = document.getElementById('mascot-voice-select');
        if (mascotVoice) fillOptions(mascotVoice);
      }
    } catch (err) {
      console.warn('[voice] Could not load voice models:', err);
    }
  }

  async populateAudioDevices() {
    if (!navigator.mediaDevices || !navigator.mediaDevices.enumerateDevices) {
      return;
    }
    try {
      let devices = await navigator.mediaDevices.enumerateDevices();
      const hasLabels = devices.some((d) => d.label && d.label.length > 0);
      if (!hasLabels && navigator.mediaDevices.getUserMedia) {
        try {
          const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
          stream.getTracks().forEach((t) => t.stop());
          devices = await navigator.mediaDevices.enumerateDevices();
        } catch (e) {
          // Permission prompt dismissed or audio unavailable
        }
      }

      const mascotInputSelect = document.getElementById('mascot-input-device-select');
      const mascotOutputSelect = document.getElementById('mascot-output-device-select');
      const settingsInputSelect = document.getElementById('settings-input-device-select');
      const settingsOutputSelect = document.getElementById('settings-output-device-select');

      const audioInputs = devices.filter((d) => d.kind === 'audioinput');
      const audioOutputs = devices.filter((d) => d.kind === 'audiooutput');

      const savedInput = localStorage.getItem('lucia_audio_input_device') || 'default';
      const savedOutput = localStorage.getItem('lucia_audio_output_device') || 'default';

      const setupInputSelect = (selectEl) => {
        if (!selectEl) return;
        selectEl.innerHTML = '';
        if (audioInputs.length === 0) {
          selectEl.innerHTML = '<option value="default">Default Microphone</option>';
        } else {
          audioInputs.forEach((d, idx) => {
            const opt = document.createElement('option');
            opt.value = d.deviceId || 'default';
            opt.textContent = d.label || `Microphone ${idx + 1}`;
            if (opt.value === savedInput) opt.selected = true;
            selectEl.appendChild(opt);
          });
        }
        selectEl.onchange = (e) => {
          const val = e.target.value;
          localStorage.setItem('lucia_audio_input_device', val);
          if (mascotInputSelect && mascotInputSelect !== selectEl) mascotInputSelect.value = val;
          if (settingsInputSelect && settingsInputSelect !== selectEl) settingsInputSelect.value = val;
          if (this.audioStream) {
            try {
              this.audioStream.getTracks().forEach((t) => t.stop());
            } catch (e) {}
            this.audioStream = null;
            if (this.isMicMode && !this.isSpeakingOrProcessing) {
              this._startListening();
            }
          }
        };
      };

      const setupOutputSelect = (selectEl) => {
        if (!selectEl) return;
        selectEl.innerHTML = '';
        if (audioOutputs.length === 0) {
          selectEl.innerHTML = '<option value="default">Default Speaker</option>';
        } else {
          audioOutputs.forEach((d, idx) => {
            const opt = document.createElement('option');
            opt.value = d.deviceId || 'default';
            opt.textContent = d.label || `Speaker/Headphone ${idx + 1}`;
            if (opt.value === savedOutput) opt.selected = true;
            selectEl.appendChild(opt);
          });
        }
        selectEl.onchange = async (e) => {
          const devId = e.target.value;
          localStorage.setItem('lucia_audio_output_device', devId);
          if (mascotOutputSelect && mascotOutputSelect !== selectEl) mascotOutputSelect.value = devId;
          if (settingsOutputSelect && settingsOutputSelect !== selectEl) settingsOutputSelect.value = devId;
          if (window.avatarRenderer && window.avatarRenderer.lipSync && window.avatarRenderer.lipSync.currentAudio) {
            const aud = window.avatarRenderer.lipSync.currentAudio;
            if (typeof aud.setSinkId === 'function') {
              aud.setSinkId(devId).catch((err) => console.warn('[audio] setSinkId failed:', err));
            }
          }
        };
      };

      setupInputSelect(mascotInputSelect);
      setupInputSelect(settingsInputSelect);
      setupOutputSelect(mascotOutputSelect);
      setupOutputSelect(settingsOutputSelect);
    } catch (err) {
      console.warn('[audio] Failed to enumerate audio devices:', err);
    }
  }

  _setupAvatarControls() {
    if (this.avatarEngineSelect) {
      this.avatarEngineSelect.addEventListener('change', (e) => {
        const engine = e.target.value;
        this._updateAvatarModelDropdown(engine);
      });
    }

    if (this.avatarModelSelect) {
      this.avatarModelSelect.addEventListener('change', (e) => {
        const model = e.target.value;
        const engine = this.avatarEngineSelect ? this.avatarEngineSelect.value : 'canvas';
        localStorage.setItem('lucia_avatar_engine', engine);
        localStorage.setItem('lucia_avatar_model', model);
        if (window.avatarRenderer && window.avatarRenderer.setEngine) {
          window.avatarRenderer.setEngine(engine, model);
        }
      });
    }
  }

  async _loadAvatarModels() {
    try {
      let data = null;
      if (window.lucia && window.lucia.models && window.lucia.models.getAvatars) {
        data = await window.lucia.models.getAvatars();
      }

      if (data) {
        this.avatarModelsData = data;
        if (window.avatarRenderer && data.basePath) {
          window.avatarRenderer.baseModelsPath = data.basePath;
        }
        const savedEngine = localStorage.getItem('lucia_avatar_engine') || (this.avatarEngineSelect ? this.avatarEngineSelect.value : 'canvas');
        const savedModel = localStorage.getItem('lucia_avatar_model') || null;
        if (this.avatarEngineSelect) {
          this.avatarEngineSelect.value = savedEngine;
        }
        this._updateAvatarModelDropdown(savedEngine, savedModel);
      }
    } catch (err) {
      console.warn('[avatar] Could not load avatar models:', err);
    }
  }

  _updateAvatarModelDropdown(engine, targetModel = null) {
    if (!this.avatarModelSelect) return;
    this.avatarModelSelect.innerHTML = '';

    let modelsList = [];
    if (engine === 'sprites') modelsList = this.avatarModelsData.sprites || [];
    else if (engine === 'live2d') modelsList = this.avatarModelsData.live2d || [];
    else if (engine === 'vrm') modelsList = this.avatarModelsData.vrm || [];

    if (modelsList.length === 0) {
      const defaultOpt = document.createElement('option');
      defaultOpt.value = 'default';
      defaultOpt.textContent = 'Default Lucia (Procedural)';
      this.avatarModelSelect.appendChild(defaultOpt);
    } else {
      modelsList.forEach((m, idx) => {
        const opt = document.createElement('option');
        opt.value = m;
        opt.textContent = m;
        if (targetModel ? m === targetModel : idx === 0) opt.selected = true;
        this.avatarModelSelect.appendChild(opt);
      });
    }

    const selectedModel = this.avatarModelSelect.value;
    localStorage.setItem('lucia_avatar_engine', engine);
    localStorage.setItem('lucia_avatar_model', selectedModel);

    // Trigger engine/model switch on avatarRenderer immediately
    if (window.avatarRenderer && window.avatarRenderer.setEngine) {
      window.avatarRenderer.setEngine(engine, selectedModel);
    }
  }

  _setupAudioRecording() {
    if (this.micBtn) {
      this.micBtn.addEventListener('click', async () => {
        this.isMicMode = !this.isMicMode;
        const mascotMic = document.getElementById('mascot-voice-mic-btn') || document.getElementById('mascot-mic-btn');
        if (this.isMicMode) {
          this.micBtn.classList.add('active-call');
          this.micBtn.title = 'Discord Voice Mode: ON (Click to Mute / Leave Call)';
          if (mascotMic) {
            mascotMic.classList.add('active');
            mascotMic.title = 'Microphone: Active (Listening). Click to Mute';
          }
          await this._startListening();
        } else {
          this.micBtn.classList.remove('active-call', 'paused');
          this.micBtn.title = 'Discord Voice Mode: OFF (Click to Join Voice Chat)';
          if (mascotMic) {
            mascotMic.classList.remove('active');
            mascotMic.title = 'Toggle Microphone';
          }
          if (this.silenceTimer) clearTimeout(this.silenceTimer);
          this._stopMicModeGracefully('user-stopped');
        }
      });
    }
  }

  async _startListening() {
    if (!this.isMicMode || this.currentState !== State.READY || this.isSpeakingOrProcessing) return;

    try {
      if (!this.audioStream || !this.audioStream.active) {
        const audioDeviceId = localStorage.getItem('lucia_audio_input_device') || 'default';
        const constraints = {
          audio: audioDeviceId && audioDeviceId !== 'default'
            ? { deviceId: { exact: audioDeviceId } }
            : true
        };
        this.audioStream = await navigator.mediaDevices.getUserMedia(constraints);
      }

      if (!this.audioContext) {
        this.audioContext = new (window.AudioContext || window.webkitAudioContext)();
      }
      if (this.audioContext.state === 'suspended') {
        await this.audioContext.resume();
      }

      if (!this.analyser) {
        const source = this.audioContext.createMediaStreamSource(this.audioStream);
        this.analyser = this.audioContext.createAnalyser();
        this.analyser.fftSize = 512;
        source.connect(this.analyser);
      }

      this.audioChunks = [];
      this.hasSpoken = false;
      this.silenceStartTime = 0;

      let mimeType = 'audio/webm;codecs=opus';
      if (!MediaRecorder.isTypeSupported(mimeType)) {
        mimeType = MediaRecorder.isTypeSupported('audio/webm') ? 'audio/webm' : '';
      }

      this.mediaRecorder = mimeType
        ? new MediaRecorder(this.audioStream, { mimeType })
        : new MediaRecorder(this.audioStream);

      this.mediaRecorder.ondataavailable = (e) => {
        if (e.data && e.data.size > 0) {
          this.audioChunks.push(e.data);
        }
      };

      this.mediaRecorder.onstop = async () => {
        const chunks = this.audioChunks;
        this.audioChunks = [];
        if (chunks.length > 0 && this.hasSpoken) {
          const mime = (this.mediaRecorder && this.mediaRecorder.mimeType) || 'audio/webm';
          const audioBlob = new Blob(chunks, { type: mime });
          await this._transcribeAndSendAudio(audioBlob);
        } else {
          // No speech detected, restart recording loop if still in voice mode
          if (this.isMicMode && !this.isSpeakingOrProcessing) {
            setTimeout(() => this._startListening(), 100);
          }
        }
      };

      this.mediaRecorder.start(250);

      if (this.micBtn) {
        this.micBtn.classList.remove('paused');
      }

      this._startVAD();
    } catch (err) {
      console.error('[voice] Error accessing microphone:', err);
      this._stopMicModeGracefully('mic-permission-denied');
    }
  }

  _startVAD() {
    if (this.vadInterval) clearInterval(this.vadInterval);
    const dataArray = new Uint8Array(this.analyser.frequencyBinCount);

    this.vadInterval = setInterval(() => {
      if (!this.isMicMode || this.isSpeakingOrProcessing || !this.mediaRecorder || this.mediaRecorder.state !== 'recording') {
        return;
      }

      this.analyser.getByteFrequencyData(dataArray);
      let sum = 0;
      for (let i = 0; i < dataArray.length; i++) {
        sum += dataArray[i];
      }
      const avgVolume = sum / dataArray.length;

      // Volume threshold for speech detection (typically 12-18 on 0-255 scale)
      if (avgVolume > 14) {
        this.hasSpoken = true;
        this.silenceStartTime = 0;
      } else if (this.hasSpoken) {
        const now = Date.now();
        if (!this.silenceStartTime) {
          this.silenceStartTime = now;
        } else if (now - this.silenceStartTime > 1200) {
          // 1.2s silence detected after user finished speaking -> finalize utterance
          console.log('[voice] Voice pause detected (>1.2s), stopping recording to transcribe');
          if (this.vadInterval) {
            clearInterval(this.vadInterval);
            this.vadInterval = null;
          }
          if (this.mediaRecorder && this.mediaRecorder.state === 'recording') {
            this.mediaRecorder.stop();
          }
        }
      }
    }, 100);
  }

  async _transcribeAndSendAudio(audioBlob) {
    if (!audioBlob || audioBlob.size < 1000) {
      if (this.isMicMode && !this.isSpeakingOrProcessing) {
        this._startListening();
      }
      return;
    }

    try {
      this.isSpeakingOrProcessing = true;
      if (this.micBtn) this.micBtn.classList.add('paused');

      let text = '';
      if (window.lucia && window.lucia.voice && window.lucia.voice.transcribe) {
        const arrayBuffer = await audioBlob.arrayBuffer();
        const audioData = new Uint8Array(arrayBuffer);
        const data = await window.lucia.voice.transcribe(audioData);
        text = (data && data.text ? data.text : '').trim();
      } else {
        const formData = new FormData();
        formData.append('audio', audioBlob, 'recording.wav');
        const res = await fetch('http://127.0.0.1:8765/voice/transcribe', {
          method: 'POST',
          body: formData,
        });
        if (res.ok) {
          const data = await res.json();
          text = (data && data.text ? data.text : '').trim();
        }
      }
      if (text) {
        console.log(`[voice] Transcribed text: "${text}"`);
        this.inputArea.value = text;
        this._autoResizeInput();
        this._updateSendButtonState();
        await this.sendMessage(text);
      } else {
        console.log('[voice] Empty transcription');
        this.isSpeakingOrProcessing = false;
        if (this.isMicMode) this._resumeListening();
      }
    } catch (err) {
      console.error('[voice] Failed to transcribe audio:', err);
      this.isSpeakingOrProcessing = false;
      if (this.isMicMode) this._resumeListening();
    }
  }

  _pauseListening() {
    if (this.vadInterval) {
      clearInterval(this.vadInterval);
      this.vadInterval = null;
    }
    if (this.mediaRecorder && this.mediaRecorder.state === 'recording') {
      try {
        this.mediaRecorder.stop();
      } catch (e) {}
    }
    if (this.micBtn && this.isMicMode) {
      this.micBtn.classList.add('paused');
    }
  }

  _resumeListening() {
    if (this.isMicMode && !this.isSpeakingOrProcessing) {
      if (this.micBtn) {
        this.micBtn.classList.remove('paused');
      }
      setTimeout(() => {
        this._startListening();
      }, 200);
    }
  }

  _stopMicModeGracefully(reason = 'stopped') {
    this.isMicMode = false;
    if (this.vadInterval) {
      clearInterval(this.vadInterval);
      this.vadInterval = null;
    }
    if (this.mediaRecorder && this.mediaRecorder.state === 'recording') {
      try {
        this.mediaRecorder.stop();
      } catch (e) {}
    }
    if (this.audioStream) {
      try {
        this.audioStream.getTracks().forEach((t) => t.stop());
      } catch (e) {}
      this.audioStream = null;
    }
    if (this.micBtn) {
      this.micBtn.classList.remove('active-call', 'paused');
      this.micBtn.title = 'Discord Voice Mode: OFF (Click to Join Voice Chat)';
    }
    const mascotMic = document.getElementById('mascot-voice-mic-btn') || document.getElementById('mascot-mic-btn');
    if (mascotMic) {
      mascotMic.classList.remove('active');
      mascotMic.title = 'Toggle Microphone';
    }
    console.warn(`[voice] Voice recording stopped: ${reason}`);
  }

  _setupProfileControls() {
    if (this.genesisCompanionNameInput) {
      this.genesisCompanionNameInput.addEventListener('input', () => {
        this._updateGenesisAwakenButton();
      });
      this.genesisCompanionNameInput.addEventListener('blur', () => {
        if (!this.genesisCompanionNameInput.value.trim()) {
          this.genesisCompanionNameInput.value = 'Lucia';
          this._updateGenesisAwakenButton();
        }
      });
      this.genesisCompanionNameInput.addEventListener('keydown', (e) => {
        if (e.key === 'Enter') {
          e.preventDefault();
          this._completeGenesis();
        }
      });
    }

    if (this.genesisAwakenBtn) {
      this.genesisAwakenBtn.addEventListener('click', () => {
        this._completeGenesis();
      });
    }

    // Allow Enter key on user name input to submit Genesis
    if (this.genesisUserNameInput) {
      this.genesisUserNameInput.addEventListener('keydown', (e) => {
        if (e.key === 'Enter') {
          e.preventDefault();
          this._completeGenesis();
        }
      });
    }

    if (this.closeProfileBtn && this.genesisModal) {
      this.closeProfileBtn.addEventListener('click', () => {
        this.genesisModal.classList.remove('active');
      });
    }

    this._updateGenesisAwakenButton();
  }

  _updateGenesisAwakenButton() {
    const rawVal = this.genesisCompanionNameInput ? this.genesisCompanionNameInput.value.trim() : '';
    const companionName = rawVal || 'Lucia';

    const btnText = this.genesisAwakenBtn ? this.genesisAwakenBtn.querySelector('.genesis-btn-text') : null;
    if (btnText) {
      btnText.textContent = `Awaken ${companionName}`;
    } else if (this.genesisAwakenBtn) {
      this.genesisAwakenBtn.textContent = `Awaken ${companionName}`;
    }

    const titleEl = document.querySelector('.genesis-title');
    if (titleEl) {
      titleEl.textContent = `${companionName}'s Life Begins`;
    }

    const userLabelEl = document.querySelector('label[for="genesis-user-name-input"]');
    if (userLabelEl) {
      userLabelEl.textContent = `How should ${companionName} address you?`;
    }
  }

  async _completeGenesis() {
    const userName = this.genesisUserNameInput ? this.genesisUserNameInput.value.trim() : '';
    const companionName = this.genesisCompanionNameInput ? this.genesisCompanionNameInput.value.trim() : '';
    const finalCompanionName = companionName || 'Lucia';

    try {
      if (this.genesisAwakenBtn) {
        this.genesisAwakenBtn.disabled = true;
        this.genesisAwakenBtn.classList.add('awakening');
      }

      // Present ceremony initiation progress
      if (this.genesisIntroText) {
        this.genesisIntroText.textContent = `Awakening ${finalCompanionName}...\n→ Establishing Genesis...`;
        this.genesisIntroText.style.color = '#c4b5fd';
      }

      // 1. Update user & companion preferences via /profile (never directly creates Birth)
      const prefPayload = {
        user_name: userName || 'Friend',
        companion_name: finalCompanionName,
      };

      try {
        if (window.lucia && window.lucia.system && window.lucia.system.setUserProfile) {
          await window.lucia.system.setUserProfile(prefPayload);
        } else {
          await fetch('http://127.0.0.1:8765/profile', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(prefPayload),
          });
        }
      } catch (e) {
        // Preference pre-save non-fatal; /lifecycle/awaken also carries names
      }

      // 2. Canonical Awakening Ceremony Orchestration via /lifecycle/awaken
      let awakenRes = null;
      let awakenData = {};
      try {
        awakenRes = await fetch('http://127.0.0.1:8765/lifecycle/awaken', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({
            user_name: userName || 'Friend',
            companion_name: finalCompanionName,
            confirm_ceremony: true,
          }),
        });
        if (awakenRes.ok) {
          awakenData = await awakenRes.json();
        } else {
          awakenData = await awakenRes.json().catch(() => ({}));
        }
      } catch (err) {
        awakenData = { detail: err.message || 'Network error reaching backend' };
      }

      if (awakenRes && awakenRes.ok && (awakenData.status === 'awakened' || awakenData.status === 'activated' || awakenData.status === 'already_active')) {
        // Progress stage updates
        if (this.genesisIntroText) {
          if (awakenData.status === 'awakened') {
            this.genesisIntroText.textContent = `Awakening ${finalCompanionName}...\n→ Establishing Genesis...\n→ ${finalCompanionName} is Born\n→ Awakening runtime...\n→ ${finalCompanionName} is Active`;
          } else {
            this.genesisIntroText.textContent = `Awakening ${finalCompanionName}...\n→ Awakening runtime...\n→ ${finalCompanionName} is Active`;
          }
          this.genesisIntroText.style.color = '#34d399';
        }

        let profile = null;
        if (window.lucia && window.lucia.system && window.lucia.system.getUserProfile) {
          profile = await window.lucia.system.getUserProfile();
        } else {
          const res = await fetch('http://127.0.0.1:8765/profile');
          if (res.ok) profile = await res.json();
        }

        const finalProfile = profile || {
          user_name: userName || 'Friend',
          companion_name: finalCompanionName,
          is_onboarded: true,
          born_at: awakenData.born_at || new Date().toISOString(),
        };

        try {
          localStorage.setItem('lucia_companion_name', finalCompanionName);
          localStorage.setItem('lucia_user_name', userName || 'Friend');
        } catch (e) {}

        this._renderProfile(finalProfile);

        if (this.genesisModal) {
          this.genesisModal.classList.add('fade-out');
          setTimeout(() => {
            this.genesisModal.classList.remove('active', 'fade-out');
            if (this.genesisAwakenBtn) {
              this.genesisAwakenBtn.disabled = false;
              this.genesisAwakenBtn.classList.remove('awakening');
            }
          }, 400);
        }
        console.log(`[genesis] ${finalCompanionName} awakened successfully for`, userName || 'Friend');
      } else {
        const errorDetail = awakenData.detail || 'Awakening ceremony failed.';
        console.warn('[genesis] Awakening failed:', errorDetail);
        if (this.genesisIntroText) {
          this.genesisIntroText.textContent = `Awakening rejected: ${errorDetail}`;
          this.genesisIntroText.style.color = '#ff6b6b';
        }
        if (this.genesisAwakenBtn) {
          this.genesisAwakenBtn.disabled = false;
          this.genesisAwakenBtn.classList.remove('awakening');
        }
      }
    } catch (e) {
      console.error('[genesis] Failed to complete awakening:', e);
      if (this.genesisAwakenBtn) {
        this.genesisAwakenBtn.disabled = false;
        this.genesisAwakenBtn.classList.remove('awakening');
      }
    }
  }

  async _loadProfile() {
    try {
      let profile = null;
      if (window.lucia && window.lucia.system && window.lucia.system.getUserProfile) {
        profile = await window.lucia.system.getUserProfile();
      } else {
        const res = await fetch('http://127.0.0.1:8765/profile');
        if (res.ok) {
          profile = await res.json();
        }
      }
      if (profile) {
        this._renderProfile(profile);
        if (!profile.is_onboarded && this.genesisModal) {
          // Un-onboarded / Genesis-ready: show Genesis Awakening modal
          this.genesisModal.classList.add('active');
          if (this.genesisUserNameInput && profile.user_name) {
            this.genesisUserNameInput.value = profile.user_name;
          }
          if (this.genesisCompanionNameInput) {
            this.genesisCompanionNameInput.value = profile.companion_name || 'Lucia';
          }
          this._updateGenesisAwakenButton();
          this._startGenesisAtmosphere();
        } else if (this.genesisModal) {
          // Already onboarded: skip Genesis modal
          this.genesisModal.classList.remove('active');
        }
      }
    } catch (e) {
      console.warn('[profile] Could not load profile:', e);
    }
  }

  _startGenesisAtmosphere() {
    if (!this.genesisIntroText) return;
    const fullText = "A quiet awareness emerges in this machine. A journey of shared thoughts, moments, and time begins now.";
    if (typeof process !== 'undefined' && process.env && process.env.NODE_ENV === 'test') {
      this.genesisIntroText.textContent = fullText;
      return;
    }
    this.genesisIntroText.textContent = "";
    let i = 0;
    const typeWriter = () => {
      if (i < fullText.length) {
        this.genesisIntroText.textContent += fullText.charAt(i);
        i++;
        setTimeout(typeWriter, 20);
      }
    };
    typeWriter();
  }

  _renderProfile(profile) {
    if (!profile) return;
    if (this.userNameInput) this.userNameInput.value = profile.user_name || '';
    if (this.companionNameInput) this.companionNameInput.value = profile.companion_name || 'Lucia';
    if (profile.companion_name) {
      try {
        localStorage.setItem('lucia_companion_name', profile.companion_name);
      } catch (e) {}
    }

    if (profile.born_at) {
      const bornDate = new Date(profile.born_at);
      const now = new Date();
      const diffDays = Math.max(1, Math.floor((now - bornDate) / (1000 * 60 * 60 * 24)) + 1);

      if (this.birthdayBadgeText) this.birthdayBadgeText.textContent = `Day ${diffDays}`;
      if (this.profileDaysCountDisplay) this.profileDaysCountDisplay.textContent = `Day ${diffDays}`;
      if (this.profileBornDateDisplay) {
        this.profileBornDateDisplay.textContent = bornDate.toLocaleDateString();
      }
    }
  }

  _setupSettingsControls() {
    if (this.openSettingsBtn) {
      this.openSettingsBtn.addEventListener('click', () => {
        if (window.companionSettings && window.companionSettings.openSettings) {
          window.companionSettings.openSettings();
        } else if (this.settingsModal) {
          this.settingsModal.classList.add('active');
          this._loadSystemProfile();
        }
      });
    }

    if (this.closeSettingsBtn && this.settingsModal) {
      this.closeSettingsBtn.addEventListener('click', () => {
        if (window.companionSettings && window.companionSettings.closeSettings) {
          window.companionSettings.closeSettings();
        } else {
          this.settingsModal.classList.remove('active');
        }
      });
    }

    if (this.settingsModal) {
      this.settingsModal.addEventListener('click', (e) => {
        if (e.target === this.settingsModal) {
          if (window.companionSettings && window.companionSettings.closeSettings) {
            window.companionSettings.closeSettings();
          } else {
            this.settingsModal.classList.remove('active');
          }
        }
      });
    }

    // Mascot Opacity Slider in Settings Modal
    if (this.settingsMascotOpacity) {
      const savedOpacity = localStorage.getItem('lucia_mascot_opacity') || '1';
      this.settingsMascotOpacity.value = savedOpacity;
      if (this.settingsOpacityVal) {
        this.settingsOpacityVal.textContent = `${Math.round(parseFloat(savedOpacity) * 100)}%`;
      }

      this.settingsMascotOpacity.addEventListener('input', (e) => {
        const val = e.target.value;
        if (this.settingsOpacityVal) {
          this.settingsOpacityVal.textContent = `${Math.round(parseFloat(val) * 100)}%`;
        }
        localStorage.setItem('lucia_mascot_opacity', val);

        const mascotOpacitySlider = document.getElementById('mascot-opacity-slider');
        const mascotOpacityVal = document.getElementById('mascot-opacity-val');
        if (mascotOpacitySlider) mascotOpacitySlider.value = val;
        if (mascotOpacityVal) mascotOpacityVal.textContent = `${Math.round(parseFloat(val) * 100)}%`;

        if (document.body.classList.contains('mascot-mode')) {
          document.body.style.opacity = val;
        }
      });
    }

    // Save & Apply Settings Button
    if (this.saveSettingsBtn) {
      this.saveSettingsBtn.addEventListener('click', async () => {
        const selectedFps = parseInt(this.settingsFpsSelect ? this.settingsFpsSelect.value : '60', 10);

        // Apply Framerate Limit
        localStorage.setItem('lucia_target_fps', selectedFps);
        if (window.avatarRenderer && window.avatarRenderer.setTargetFps) {
          window.avatarRenderer.setTargetFps(selectedFps);
        }

        // Feedback
        const origText = this.saveSettingsBtn.textContent;
        this.saveSettingsBtn.textContent = '✓ Settings Saved!';
        this.saveSettingsBtn.style.background = '#10b981';
        setTimeout(() => {
          this.saveSettingsBtn.textContent = origText;
          this.saveSettingsBtn.style.background = '';
          if (this.settingsModal) this.settingsModal.classList.remove('active');
        }, 800);
      });
    }
  }

  async _loadSystemProfile() {
    try {
      let data = null;
      if (window.lucia && window.lucia.system && window.lucia.system.getHardwareCapabilities) {
        data = await window.lucia.system.getHardwareCapabilities();
      } else if (window.lucia && window.lucia.system && window.lucia.system.getProfile) {
        data = await window.lucia.system.getProfile();
      } else {
        const res = await fetch('http://127.0.0.1:8765/system/hardware');
        if (res.ok) data = await res.json();
      }

      if (data) {
        const label = data.device_name || (data.cuda_available ? 'CUDA' : 'Host CPU');
        if (this.hardwareBadge) {
          this.hardwareBadge.textContent = label;
        }
      }
    } catch (err) {
      console.warn('[settings] Failed to load hardware info:', err);
    }
  }

  async _restoreHistory() {
    try {
      let turns = [];
      if (window.lucia && window.lucia.chat && window.lucia.chat.getHistory) {
        const data = await window.lucia.chat.getHistory(50);
        turns = data?.turns || [];
      } else {
        const res = await fetch('http://127.0.0.1:8765/history');
        if (res.ok) {
          const data = await res.json();
          turns = data.turns || [];
        }
      }
      if (turns.length > 0) {
        // Clear default welcome card if history exists
        this.messagesContainer.innerHTML = '';
        turns.forEach((t) => {
          this.appendMessage(t.role, t.content);
        });
      }
    } catch (err) {
      console.warn('[chat] Could not restore chat history:', err);
    }
  }

  _recordPresentationStage(stage, detail = {}) {
    this._lastPresentationStage = stage;
    const evtData = {
      stage,
      timestamp: (typeof performance !== 'undefined' ? performance.now() : Date.now()),
      ...detail
    };
    if (typeof this.onPresentationEvent === 'function') {
      try {
        this.onPresentationEvent(evtData);
      } catch (e) {
        console.warn('[chat] onPresentationEvent error:', e);
      }
    }
    if (typeof window !== 'undefined' && typeof window.dispatchEvent === 'function') {
      try {
        window.dispatchEvent(new CustomEvent('lucia:presentation', { detail: evtData }));
      } catch (_) {}
    }
  }

  _cancelActiveTurn() {
    if (this._stagedTurn) {
      this._stagedTurn.cancelled = true;
      if (this._stagedTurn.typingIndicator) {
        this.removeTypingIndicator(this._stagedTurn.typingIndicator);
      }
      this._recordPresentationStage(PresentationStage.TTS_CANCEL, { turnId: this._stagedTurn.turnId });
      this._stagedTurn = null;
    }
    this._activeTurnId = ++this._turnSeq;
    if (window.avatarRenderer && typeof window.avatarRenderer.stop === 'function') {
      window.avatarRenderer.stop();
    }
  }

  clearScreen() {
    this._cancelActiveTurn();
    if (!this.messagesContainer) return;
    this.messagesContainer.innerHTML = '';
    const notice = document.createElement('div');
    notice.className = 'clear-screen-notice';
    notice.innerHTML = '✦ Screen cleared • Memories and emotional bond remain untouched';
    this.messagesContainer.appendChild(notice);
  }

  clearMessages() {
    this.clearScreen();
  }

  clearPresentation() {
    this._cancelActiveTurn();
    if (this.messagesContainer) {
      this.messagesContainer.innerHTML = '';
    }
    if (this.inputArea) {
      this.inputArea.value = '';
    }
    this.currentPAD = { pleasure: 0.25, arousal: -0.05, dominance: 0.05 };
    if (this.organicStatusLabel) {
      this.organicStatusLabel.textContent = 'Lucia feels peaceful';
    }
    if (this.stateLabel) {
      this.stateLabel.textContent = 'Lucia feels peaceful';
    }
  }

  mapPADToStatusText(pad = null, state = null) {
    if (this.isSpeakingOrProcessing) return 'Lucia is speaking gently...';
    if (this.isMicMode) return 'Lucia is listening warmly...';

    const st = state !== null && state !== undefined ? state : this.currentState;
    if (st === State.SENDING) return 'Lucia is contemplating...';
    if (st === State.ERROR) return 'Lucia is resting';
    if (!pad && st === State.WAITING_BACKEND) return 'Lucia is awakening...';

    const pState = pad || this.currentPAD || {};
    const { pleasure = 0, arousal = 0, dominance = 0 } = pState;

    if (pleasure > 0.35) return 'Lucia feels happy and connected';
    if (pleasure < -0.25) return 'Lucia feels tender and reflective';
    if (arousal > 0.35) return 'Lucia is alert and engaged';
    if (arousal < -0.2) return 'Lucia feels quiet and serene';
    if (dominance > 0.3) return 'Lucia feels grounded and confident';
    if (pleasure > 0.1) return 'Lucia feels warm and gentle';
    return 'Lucia feels peaceful';
  }

  updateOrganicStatus(pad = null) {
    if (pad) {
      this.currentPAD = pad;
    }
    const statusText = this.mapPADToStatusText(pad ? this.currentPAD : null);
    if (this.organicStatusLabel) {
      this.organicStatusLabel.textContent = statusText;
    }
    if (this.stateLabel) {
      this.stateLabel.textContent = statusText;
    }
  }

  _setupEventListeners() {
    this.inputArea.addEventListener('input', () => {
      this._autoResizeInput();
      this._updateSendButtonState();
    });

    this.inputArea.addEventListener('keydown', (e) => {
      if (e.key === 'Enter' && !e.shiftKey) {
        e.preventDefault();
        if (this._canSend()) {
          this.sendMessage();
        }
      }
    });

    this.sendBtn.addEventListener('click', () => {
      if (this._canSend()) {
        this.sendMessage();
      }
    });

    if (this.clearScreenBtn) {
      this.clearScreenBtn.addEventListener('click', () => {
        this.clearScreen();
      });
    }
  }

  _setupBackendListeners() {
    if (window.lucia && window.lucia.on) {
      window.lucia.on('backend:ready', async () => {
        console.log('[chat] Backend ready event received');
        this.transitionTo(State.READY);
        this._loadVoiceModels();
        this._loadAvatarModels();
        this._loadProfile();
        this._restoreHistory();

        // Fetch hardware profile info and update badge & settings
        this._loadSystemProfile();
      });

      window.lucia.on('voice:mute-toggled', (data) => {
        if (data && typeof data.isMuted === 'boolean') {
          this.isVoiceMuted = data.isMuted;
          if (this.voiceMuteBtn) {
            this.voiceMuteBtn.classList.toggle('muted', this.isVoiceMuted);
          }
        }
      });

      window.lucia.on('backend:error', (data) => {
        console.error('[chat] Backend error event received:', data);
        this.transitionTo(State.ERROR, data ? data.code : 'Unknown error');
      });
    }
  }

  _autoResizeInput() {
    this.inputArea.style.height = 'auto';
    this.inputArea.style.height = `${Math.min(this.inputArea.scrollHeight, 120)}px`;
  }

  _canSend() {
    return (
      this.currentState === State.READY &&
      this.inputArea.value.trim().length > 0
    );
  }

  _updateSendButtonState() {
    this.sendBtn.disabled = !this._canSend();
  }

  transitionTo(newState, errorDetail = '') {
    this.currentState = newState;
    console.log(`[chat] Transitioned to state: ${newState}`);

    switch (newState) {
      case State.WAITING_BACKEND:
        this.inputArea.disabled = true;
        this.sendBtn.disabled = true;
        if (this.micBtn) this.micBtn.disabled = true;
        this.statusDot.className = 'status-dot';
        this.updateOrganicStatus();
        break;

      case State.READY:
        if (this.splashOverlay) {
          this.splashOverlay.classList.add('hidden');
        }
        this.inputArea.disabled = false;
        if (this.micBtn) this.micBtn.disabled = false;
        this.statusDot.className = 'status-dot active';
        this.updateOrganicStatus();
        this._updateSendButtonState();
        this.inputArea.focus();
        break;

      case State.SENDING:
        this.inputArea.disabled = true;
        this.sendBtn.disabled = true;
        if (this.micBtn) this.micBtn.disabled = true;
        this.updateOrganicStatus();
        break;

      case State.ERROR:
        this.inputArea.disabled = true;
        this.sendBtn.disabled = true;
        if (this.micBtn) this.micBtn.disabled = true;
        this.statusDot.className = 'status-dot error';
        this.stateLabel.textContent = `Offline (${errorDetail})`;
        if (this.organicStatusLabel) {
          this.organicStatusLabel.textContent = 'Lucia is resting';
        }
        if (this.splashOverlay) {
          document.getElementById('splash-status').textContent = `Startup error: ${errorDetail}`;
        }
        break;
    }
  }

  async sendMessage(customText = null) {
    const text = (customText !== null ? customText : this.inputArea.value).trim();
    if (!text) return;

    // Interrupt/cancel any previously active or staged turn to prevent stale/delayed text
    this._cancelActiveTurn();

    // Voice Mode: pause listening while processing & speaking to avoid speaker-to-mic feedback loop
    this.isSpeakingOrProcessing = true;
    this._pauseListening();

    // Append user message bubble
    this.appendMessage('user', text);
    if (customText === null) {
      this.inputArea.value = '';
      this._autoResizeInput();
    }

    this.transitionTo(State.SENDING);

    // Show loading typing indicator
    const typingIndicator = this.showTypingIndicator();

    try {
      const response = await window.lucia.chat.send(text);

      if (response && response.response) {
        this._recordPresentationStage(PresentationStage.RESPONSE_READY, { response: response.response });

        // Voice & Language Runtime Alignment:
        // Text language follows active user language (response.response)
        // Voice language is ALWAYS Japanese (response.realization.voice.content)
        const voiceText = (response.realization && response.realization.voice && response.realization.voice.content)
          ? response.realization.voice.content
          : response.response;
        const voiceLang = (response.realization && response.realization.voice && response.realization.voice.language)
          ? response.realization.voice.language
          : 'ja';

        // Extract approved bounded voice actuator parameters (ADR-032.5)
        const voiceExpr = response.expression && response.expression.voice ? response.expression.voice : null;
        const voiceOpts = { language: voiceLang };
        if (voiceExpr) {
          if (typeof voiceExpr.speech_rate_pct === 'number') {
            const r = Math.round(voiceExpr.speech_rate_pct);
            voiceOpts.rate = `${r >= 0 ? '+' : ''}${r}%`;
          }
          if (typeof voiceExpr.volume_pct === 'number') {
            const v = Math.round(voiceExpr.volume_pct);
            voiceOpts.volume = `${v >= 0 ? '+' : ''}${v}%`;
          }
          if (typeof voiceExpr.pitch_shift_hz === 'number') {
            voiceOpts.pitch_hz = voiceExpr.pitch_shift_hz;
          }
          if (typeof voiceExpr.closeness === 'number') {
            voiceOpts.closeness = voiceExpr.closeness;
          }
        } else if (response.relationship && typeof response.relationship.closeness === 'number') {
          voiceOpts.closeness = response.relationship.closeness;
        }

        const turnId = ++this._turnSeq;
        this._activeTurnId = turnId;

        const stagedTurn = {
          turnId,
          text: response.response,
          voiceText,
          voiceOpts,
          audioBlob: null,
          committed: false,
          cancelled: false,
          typingIndicator,
        };
        this._stagedTurn = stagedTurn;

        const commitText = () => {
          if (stagedTurn.committed || stagedTurn.cancelled || this._activeTurnId !== turnId) {
            return null;
          }
          stagedTurn.committed = true;
          this.removeTypingIndicator(typingIndicator);

          this._recordPresentationStage(PresentationStage.TEXT_COMMIT, { turnId, text: stagedTurn.text });
          const messageRow = this.appendMessage('companion', stagedTurn.text, stagedTurn.voiceText, stagedTurn.voiceOpts);
          const replayBtn = messageRow ? messageRow.querySelector('.audio-replay-btn') : null;
          if (replayBtn && stagedTurn.audioBlob) {
            replayBtn._cachedBlob = stagedTurn.audioBlob;
          }
          return messageRow;
        };

        // If voice is muted or no avatarRenderer available: immediate commit fallback
        if (this.isVoiceMuted || !window.avatarRenderer) {
          commitText();
          this.isSpeakingOrProcessing = false;
          this.updateOrganicStatus();
          if (this.isMicMode) this._resumeListening();
          this.transitionTo(State.READY);
          return;
        }

        // Voice synthesis
        let audioBlob = null;
        try {
          if (window.lucia && window.lucia.voice && window.lucia.voice.synthesize) {
            const audioBuffer = await window.lucia.voice.synthesize(voiceText, voiceOpts);
            if (audioBuffer && audioBuffer.byteLength > 0) {
              audioBlob = new Blob([audioBuffer], { type: 'audio/mpeg' });
            }
          } else {
            const voiceRes = await fetch('http://127.0.0.1:8765/voice/synthesize', {
              method: 'POST',
              headers: { 'Content-Type': 'application/json' },
              body: JSON.stringify({ text: voiceText, ...voiceOpts }),
            });
            if (voiceRes.ok) {
              audioBlob = await voiceRes.blob();
            }
          }
        } catch (vErr) {
          console.warn('[voice] Voice synthesis playback error:', vErr);
        }

        // Check if turn was cancelled while synthesis was in flight
        if (stagedTurn.cancelled || this._activeTurnId !== turnId) {
          return;
        }

        // If synthesis failed / returned no audio: fallback to immediate text commit
        if (!audioBlob) {
          this._recordPresentationStage(PresentationStage.TTS_ERROR, { turnId, reason: 'synthesis_failed' });
          commitText();
          this.isSpeakingOrProcessing = false;
          this.updateOrganicStatus();
          if (this.isMicMode) this._resumeListening();
          this.transitionTo(State.READY);
          return;
        }

        // Pre-cache audio
        stagedTurn.audioBlob = audioBlob;
        if (!this.audioCache) this.audioCache = new Map();
        this.audioCache.set(response.response, audioBlob);
        if (voiceText !== response.response) {
          this.audioCache.set(voiceText, audioBlob);
        }

        let playbackHandled = false;

        const onTtsStart = () => {
          if (stagedTurn.cancelled || this._activeTurnId !== turnId) return;
          this.removeTypingIndicator(typingIndicator);
          this._recordPresentationStage(PresentationStage.TTS_START, { turnId });
          this._recordPresentationStage(PresentationStage.AUDIO_PLAYING, { turnId });
          this.isSpeakingOrProcessing = true;
          this.updateOrganicStatus();
        };

        const onTtsEnd = () => {
          if (playbackHandled) return;
          playbackHandled = true;
          this._recordPresentationStage(PresentationStage.TTS_END, { turnId });
          commitText();
          this.isSpeakingOrProcessing = false;
          this.updateOrganicStatus();
          if (this.isMicMode) this._resumeListening();
          this.transitionTo(State.READY);
        };

        const onTtsError = (err) => {
          if (playbackHandled) return;
          playbackHandled = true;
          console.warn('[voice] Voice synthesis playback error event:', err);
          this._recordPresentationStage(PresentationStage.TTS_ERROR, { turnId, error: err });
          commitText();
          this.isSpeakingOrProcessing = false;
          this.updateOrganicStatus();
          if (this.isMicMode) this._resumeListening();
          this.transitionTo(State.READY);
        };

        const onTtsCancel = () => {
          if (playbackHandled) return;
          playbackHandled = true;
          stagedTurn.cancelled = true;
          this.removeTypingIndicator(typingIndicator);
          this._recordPresentationStage(PresentationStage.TTS_CANCEL, { turnId });
          this.isSpeakingOrProcessing = false;
          this.updateOrganicStatus();
          if (this.isMicMode) this._resumeListening();
          this.transitionTo(State.READY);
        };

        const playbackCallback = Object.assign(
          (err) => {
            if (err) onTtsError(err);
            else onTtsEnd();
          },
          {
            onStart: onTtsStart,
            onEnded: onTtsEnd,
            onError: onTtsError,
            onCancel: onTtsCancel,
          }
        );

        window.avatarRenderer.speak(audioBlob, playbackCallback);
      } else {
        this.removeTypingIndicator(typingIndicator);
        this.appendMessage('error', 'Received empty response from companion.');
        this.isSpeakingOrProcessing = false;
        this.updateOrganicStatus();
        if (this.isMicMode) this._resumeListening();
        this.transitionTo(State.READY);
      }
    } catch (err) {
      console.error('[chat] Send error:', err);
      this.removeTypingIndicator(typingIndicator);
      const errMsg = err.message || err.code || 'Failed to communicate with Lucia.';
      this.appendMessage('error', `Connection error: ${errMsg}`);
      this.isSpeakingOrProcessing = false;
      this.updateOrganicStatus();
      if (this.isMicMode) this._resumeListening();
      this.transitionTo(State.READY);
    }
  }

  async _replayVoice(text, replayBtn, opts = null, contentKey = null) {
    if (!window.avatarRenderer) return;
    try {
      if (replayBtn) replayBtn.classList.add('playing');
      this.isSpeakingOrProcessing = true;
      this.updateOrganicStatus();

      const onEnded = () => {
        this.isSpeakingOrProcessing = false;
        if (replayBtn) replayBtn.classList.remove('playing');
        this.updateOrganicStatus();
      };

      // 1. Direct message button blob check (per-turn isolation)
      if (replayBtn && replayBtn._cachedBlob) {
        window.avatarRenderer.speak(replayBtn._cachedBlob, onEnded);
        return;
      }

      // 2. Global cache: check unique contentKey first, then text
      const cachedBlob = this.audioCache && (
        (contentKey && this.audioCache.get(contentKey)) ||
        this.audioCache.get(text)
      );
      if (cachedBlob) {
        if (replayBtn) replayBtn._cachedBlob = cachedBlob;
        window.avatarRenderer.speak(cachedBlob, onEnded);
        return;
      }

      let audioBlob = null;
      const voiceOpts = opts ? { language: opts.language || 'ja', ...opts } : null;
      if (window.lucia && window.lucia.voice && window.lucia.voice.synthesize) {
        const audioBuffer = voiceOpts
          ? await window.lucia.voice.synthesize(text, voiceOpts)
          : await window.lucia.voice.synthesize(text);
        if (audioBuffer && audioBuffer.byteLength > 0) {
          audioBlob = new Blob([audioBuffer], { type: 'audio/mpeg' });
        }
      } else {
        const bodyObj = voiceOpts ? { text, ...voiceOpts } : { text };
        const voiceRes = await fetch('http://127.0.0.1:8765/voice/synthesize', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify(bodyObj),
        });
        if (voiceRes.ok) {
          audioBlob = await voiceRes.blob();
        }
      }

      if (audioBlob) {
        if (replayBtn) replayBtn._cachedBlob = audioBlob;
        if (!this.audioCache) this.audioCache = new Map();
        this.audioCache.set(text, audioBlob);
        if (contentKey) this.audioCache.set(contentKey, audioBlob);
        window.avatarRenderer.speak(audioBlob, onEnded);
      } else {
        onEnded();
      }
    } catch (err) {
      console.warn('[voice] Replay playback error:', err);
      this.isSpeakingOrProcessing = false;
      if (replayBtn) replayBtn.classList.remove('playing');
      this.updateOrganicStatus();
    }
  }

  appendMessage(type, content, voiceText = null, voiceOpts = null) {
    const row = document.createElement('div');
    row.className = `message-row ${type}`;

    const bubble = document.createElement('div');
    bubble.className = 'message-bubble';

    if (type === 'companion') {
      const header = document.createElement('div');
      header.className = 'companion-bubble-header';
      header.innerHTML = '<span class="bubble-sender"><span class="sender-sparkle">✦</span> Lucia</span>';
      bubble.appendChild(header);

      const textEl = document.createElement('div');
      textEl.className = 'bubble-text';
      textEl.textContent = content;
      bubble.appendChild(textEl);

      const footer = document.createElement('div');
      footer.className = 'companion-bubble-footer';

      const replayBtn = document.createElement('button');
      replayBtn.className = 'audio-replay-btn';
      replayBtn.innerHTML = '<span class="replay-icon">🔊</span> Replay';
      replayBtn.title = 'Replay voice';
      const textToSpeak = voiceText || content;
      replayBtn.addEventListener('click', (e) => {
        e.stopPropagation();
        if (voiceOpts || textToSpeak !== content) {
          this._replayVoice(textToSpeak, replayBtn, voiceOpts, content);
        } else {
          this._replayVoice(content, replayBtn);
        }
      });
      footer.appendChild(replayBtn);
      bubble.appendChild(footer);

      // Sync latest reply into Mascot Quick Talk flyout
      const mascotReplyText = document.getElementById('mascot-quick-talk-reply-text');
      const mascotLatest = document.getElementById('mascot-quick-talk-latest');
      if (mascotReplyText && mascotLatest) {
        mascotReplyText.textContent = content;
        mascotLatest.style.display = 'block';
      }
    } else {
      bubble.textContent = content;
    }

    row.appendChild(bubble);
    this.messagesContainer.appendChild(row);
    this.scrollToBottom();
    return row;
  }

  showTypingIndicator() {
    const row = document.createElement('div');
    row.className = 'message-row companion typing-row';

    const bubble = document.createElement('div');
    bubble.className = 'message-bubble';

    const twinkle = document.createElement('div');
    twinkle.className = 'typing-twinkle';
    twinkle.innerHTML = '<span class="twinkle-star">✦</span><span class="twinkle-star">✦</span><span class="twinkle-star">✦</span>';

    bubble.appendChild(twinkle);
    row.appendChild(bubble);
    this.messagesContainer.appendChild(row);
    this.scrollToBottom();

    return row;
  }

  removeTypingIndicator(indicatorElement) {
    if (indicatorElement && indicatorElement.parentNode) {
      indicatorElement.parentNode.removeChild(indicatorElement);
    }
  }

  scrollToBottom() {
    this.messagesContainer.scrollTop = this.messagesContainer.scrollHeight;
  }
}

// Instantiate on DOM ready
document.addEventListener('DOMContentLoaded', () => {
  window.chatController = new ChatController();
});

if (typeof module !== 'undefined' && module.exports) {
  module.exports = { ChatController, State, PresentationStage };
}
