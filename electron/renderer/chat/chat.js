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

    // Discord-style Continuous Mic Mode
    this.micBtn = document.getElementById('mic-btn');
    this.isMicMode = false;
    this.isSpeakingOrProcessing = false;
    this.silenceTimer = null;
    this.recognition = null;

    // Profile & Awakening Modal
    this.openProfileBtn = document.getElementById('open-profile-btn');
    this.closeProfileBtn = document.getElementById('close-profile-btn');
    this.saveProfileBtn = document.getElementById('save-profile-btn');
    this.profileModal = document.getElementById('profile-modal');
    this.userNameInput = document.getElementById('profile-user-name-input');
    this.companionNameInput = document.getElementById('profile-companion-name-input');
    this.birthdayBadgeText = document.getElementById('birthday-badge-text');
    this.profileBornDateDisplay = document.getElementById('profile-born-date-display');
    this.profileDaysCountDisplay = document.getElementById('profile-days-count-display');

    // Initialize Canvas Avatar
    const canvas = document.getElementById('avatar-canvas');
    if (canvas && typeof AvatarRenderer !== 'undefined') {
      window.avatarRenderer = new AvatarRenderer(canvas);
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
      if (canvas) {
        canvas.addEventListener('dblclick', () => {
          if (window.lucia && window.lucia.window && window.lucia.window.toggleMascot) {
            window.lucia.window.toggleMascot();
          }
        });
      }
    }

    this._setupEventListeners();
    this._setupVoiceControls();
    this._setupAvatarControls();
    this._setupSpeechRecognition();
    this._setupProfileControls();
    this._setupBackendListeners();
  }

  _setupVoiceControls() {
    if (this.volumeSlider) {
      this.volumeSlider.addEventListener('input', (e) => {
        const vol = parseFloat(e.target.value);
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
        try {
          await fetch('http://127.0.0.1:8765/voice/select-model', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ model_name: modelName }),
          });
          console.log(`[voice] Selected model: ${modelName}`);
        } catch (err) {
          console.error('[voice] Failed to select voice model:', err);
        }
      });
    }
  }

  async _loadVoiceModels() {
    if (!this.voiceModelSelect) return;
    try {
      let data = null;
      if (window.lucia && window.lucia.models && window.lucia.models.getVoices) {
        data = await window.lucia.models.getVoices();
      } else {
        const res = await fetch('http://127.0.0.1:8765/voice/models');
        if (res.ok) data = await res.json();
      }

      if (data && data.models && data.models.length > 0) {
        this.voiceModelSelect.innerHTML = '';
        data.models.forEach((m) => {
          const opt = document.createElement('option');
          opt.value = m.name;
          opt.textContent = m.name === 'default' ? '🎙️ Base Voice (Default)' : `🎙️ ${m.name} (RVC)`;
          if (m.is_active) opt.selected = true;
          this.voiceModelSelect.appendChild(opt);
        });
      }
    } catch (err) {
      console.warn('[voice] Could not load voice models:', err);
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
      } else {
        const res = await fetch('http://127.0.0.1:8765/models/avatar');
        if (res.ok) data = await res.json();
      }

      if (data) {
        this.avatarModelsData = data;
        const currentEngine = this.avatarEngineSelect ? this.avatarEngineSelect.value : 'canvas';
        this._updateAvatarModelDropdown(currentEngine);
      }
    } catch (err) {
      console.warn('[avatar] Could not load avatar models:', err);
    }
  }

  _updateAvatarModelDropdown(engine) {
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
        if (idx === 0) opt.selected = true;
        this.avatarModelSelect.appendChild(opt);
      });
    }

    // Trigger engine/model switch on avatarRenderer immediately
    if (window.avatarRenderer && window.avatarRenderer.setEngine) {
      const selectedModel = this.avatarModelSelect.value;
      window.avatarRenderer.setEngine(engine, selectedModel);
    }
  }

  _setupSpeechRecognition() {
    const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
    if (SpeechRecognition) {
      this.recognition = new SpeechRecognition();
      this.recognition.continuous = true;
      this.recognition.interimResults = true;
      this.recognition.lang = 'vi-VN';

      this.recognition.onstart = () => {
        if (this.micBtn && this.isMicMode) {
          this.micBtn.classList.add('active-call');
          this.micBtn.classList.remove('paused');
          this.micBtn.title = 'Discord Voice Mode: Connected (Listening). Click to Mute';
        }
      };

      this.recognition.onresult = (event) => {
        if (!this.isMicMode || this.isSpeakingOrProcessing) return;

        let interimTranscript = '';
        let finalTranscript = '';

        for (let i = event.resultIndex; i < event.results.length; ++i) {
          const transcript = event.results[i][0].transcript;
          if (event.results[i].isFinal) {
            finalTranscript += transcript;
          } else {
            interimTranscript += transcript;
          }
        }

        const currentText = (finalTranscript || interimTranscript).trim();
        if (currentText) {
          this.inputArea.value = currentText;
          this._autoResizeInput();
          this._updateSendButtonState();

          // Voice Activity Detection: auto-send after 1.3s pause of silence
          if (this.silenceTimer) clearTimeout(this.silenceTimer);
          this.silenceTimer = setTimeout(() => {
            if (this.isMicMode && !this.isSpeakingOrProcessing && this._canSend()) {
              console.log('[speech] Natural pause detected, sending voice turn automatically');
              this.sendMessage();
            }
          }, 1300);
        }
      };

      this.recognition.onerror = (err) => {
        if (err.error !== 'no-speech') {
          console.warn('[speech] Recognition error:', err.error);
        }
      };

      this.recognition.onend = () => {
        // Continuous voice connection: automatically keep listening if call mode is active
        if (this.isMicMode && !this.isSpeakingOrProcessing) {
          setTimeout(() => {
            if (this.isMicMode && !this.isSpeakingOrProcessing) {
              this._startListening();
            }
          }, 200);
        }
      };

      if (this.micBtn) {
        this.micBtn.addEventListener('click', () => {
          this.isMicMode = !this.isMicMode;
          if (this.isMicMode) {
            this.micBtn.classList.add('active-call');
            this.micBtn.title = 'Discord Voice Mode: ON (Click to Mute / Leave Call)';
            this._startListening();
          } else {
            this.micBtn.classList.remove('active-call', 'paused');
            this.micBtn.title = 'Discord Voice Mode: OFF (Click to Join Voice Chat)';
            if (this.silenceTimer) clearTimeout(this.silenceTimer);
            this._pauseListening();
          }
        });
      }
    } else {
      if (this.micBtn) {
        this.micBtn.title = 'Speech recognition not supported in this environment';
      }
    }
  }

  _startListening() {
    if (!this.recognition || this.currentState !== State.READY || this.isSpeakingOrProcessing) return;
    try {
      this.recognition.start();
    } catch (e) {
      // Ignore if already active
    }
  }

  _pauseListening() {
    if (this.micBtn && this.isMicMode) {
      this.micBtn.classList.add('paused');
    }
    if (this.recognition) {
      try {
        this.recognition.abort();
      } catch (e) {}
    }
  }

  _resumeListening() {
    if (this.isMicMode && !this.isSpeakingOrProcessing) {
      if (this.micBtn) {
        this.micBtn.classList.remove('paused');
      }
      setTimeout(() => {
        this._startListening();
      }, 300);
    }
  }

  _setupProfileControls() {
    if (this.openProfileBtn && this.profileModal) {
      this.openProfileBtn.addEventListener('click', () => {
        this.profileModal.classList.add('active');
      });
    }

    if (this.closeProfileBtn && this.profileModal) {
      this.closeProfileBtn.addEventListener('click', () => {
        this.profileModal.classList.remove('active');
      });
    }

    if (this.saveProfileBtn) {
      this.saveProfileBtn.addEventListener('click', async () => {
        const userName = this.userNameInput ? this.userNameInput.value.trim() : '';
        const companionName = this.companionNameInput ? this.companionNameInput.value.trim() : '';
        try {
          const res = await fetch('http://127.0.0.1:8765/profile', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
              user_name: userName || 'Friend',
              companion_name: companionName || 'Lucia',
              is_onboarded: true,
            }),
          });
          if (res.ok) {
            const data = await res.json();
            this._renderProfile(data.profile);
            if (this.profileModal) this.profileModal.classList.remove('active');
          }
        } catch (e) {
          console.error('[profile] Failed to save profile:', e);
        }
      });
    }
  }

  async _loadProfile() {
    try {
      const res = await fetch('http://127.0.0.1:8765/profile');
      if (res.ok) {
        const profile = await res.json();
        this._renderProfile(profile);
        if (!profile.is_onboarded && this.profileModal) {
          // First Awakening onboarding popup
          this.profileModal.classList.add('active');
        }
      }
    } catch (e) {
      console.warn('[profile] Could not load profile:', e);
    }
  }

  _renderProfile(profile) {
    if (!profile) return;
    if (this.userNameInput) this.userNameInput.value = profile.user_name || '';
    if (this.companionNameInput) this.companionNameInput.value = profile.companion_name || 'Lucia';

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

  async _restoreHistory() {
    try {
      const res = await fetch('http://127.0.0.1:8765/history');
      if (res.ok) {
        const data = await res.json();
        const turns = data.turns || [];
        if (turns.length > 0) {
          // Clear default welcome card if history exists
          this.messagesContainer.innerHTML = '';
          turns.forEach((t) => {
            this.appendMessage(t.role, t.content);
          });
        }
      }
    } catch (err) {
      console.warn('[chat] Could not restore chat history:', err);
    }
  }

  clearMessages() {
    this.messagesContainer.innerHTML = `
      <div class="system-welcome-card">
        <div class="welcome-icon">✨</div>
        <h3>Welcome to Lucia</h3>
        <p>Her emotional state and memories evolve dynamically with every turn.</p>
      </div>
    `;
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

        // Fetch hardware profile info for the badge
        try {
          if (window.lucia.system && window.lucia.system.getProfile) {
            const profile = await window.lucia.system.getProfile();
            if (profile && profile.name) {
              this.hardwareBadge.textContent = profile.name;
            }
          }
        } catch (e) {}
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
        this.stateLabel.textContent = 'Awakening core...';
        break;

      case State.READY:
        if (this.splashOverlay) {
          this.splashOverlay.classList.add('hidden');
        }
        this.inputArea.disabled = false;
        if (this.micBtn) this.micBtn.disabled = false;
        this.statusDot.className = 'status-dot active';
        this.stateLabel.textContent = 'Active & Mindful';
        this._updateSendButtonState();
        this.inputArea.focus();
        break;

      case State.SENDING:
        this.inputArea.disabled = true;
        this.sendBtn.disabled = true;
        if (this.micBtn) this.micBtn.disabled = true;
        this.stateLabel.textContent = 'Reflecting...';
        break;

      case State.ERROR:
        this.inputArea.disabled = true;
        this.sendBtn.disabled = true;
        if (this.micBtn) this.micBtn.disabled = true;
        this.statusDot.className = 'status-dot error';
        this.stateLabel.textContent = `Offline (${errorDetail})`;
        if (this.splashOverlay) {
          document.getElementById('splash-status').textContent = `Startup error: ${errorDetail}`;
        }
        break;
    }
  }

  async sendMessage() {
    const text = this.inputArea.value.trim();
    if (!text) return;

    // Discord Mode: pause recognition while processing & speaking to avoid speaker-to-mic feedback loop
    this.isSpeakingOrProcessing = true;
    this._pauseListening();

    // Append user message bubble
    this.appendMessage('user', text);
    this.inputArea.value = '';
    this._autoResizeInput();

    this.transitionTo(State.SENDING);

    // Show loading typing indicator
    const typingIndicator = this.showTypingIndicator();

    try {
      const response = await window.lucia.chat.send(text);
      this.removeTypingIndicator(typingIndicator);

      if (response && response.response) {
        this.appendMessage('companion', response.response);

        // Synthesize and play voice if not muted
        if (!this.isVoiceMuted && window.avatarRenderer) {
          try {
            const voiceRes = await fetch('http://127.0.0.1:8765/voice/synthesize', {
              method: 'POST',
              headers: { 'Content-Type': 'application/json' },
              body: JSON.stringify({ text: response.response }),
            });
            if (voiceRes.ok) {
              const audioBlob = await voiceRes.blob();
              window.avatarRenderer.speak(audioBlob, () => {
                // Audio ended callback: resume listening in Discord mode
                this.isSpeakingOrProcessing = false;
                if (this.isMicMode) {
                  this._resumeListening();
                }
              });
            } else {
              this.isSpeakingOrProcessing = false;
              if (this.isMicMode) this._resumeListening();
            }
          } catch (vErr) {
            console.warn('[voice] Voice synthesis playback error:', vErr);
            this.isSpeakingOrProcessing = false;
            if (this.isMicMode) this._resumeListening();
          }
        } else {
          this.isSpeakingOrProcessing = false;
          if (this.isMicMode) this._resumeListening();
        }
      } else {
        this.appendMessage('error', 'Received empty response from companion.');
        this.isSpeakingOrProcessing = false;
        if (this.isMicMode) this._resumeListening();
      }
      this.transitionTo(State.READY);
    } catch (err) {
      console.error('[chat] Send error:', err);
      this.removeTypingIndicator(typingIndicator);
      const errMsg = err.message || err.code || 'Failed to communicate with Lucia.';
      this.appendMessage('error', `Connection error: ${errMsg}`);
      this.isSpeakingOrProcessing = false;
      if (this.isMicMode) this._resumeListening();
      this.transitionTo(State.READY);
    }
  }

  appendMessage(type, content) {
    const row = document.createElement('div');
    row.className = `message-row ${type}`;

    const bubble = document.createElement('div');
    bubble.className = 'message-bubble';
    bubble.textContent = content;

    row.appendChild(bubble);
    this.messagesContainer.appendChild(row);
    this.scrollToBottom();
  }

  showTypingIndicator() {
    const row = document.createElement('div');
    row.className = 'message-row companion typing-row';

    const bubble = document.createElement('div');
    bubble.className = 'message-bubble';

    const dots = document.createElement('div');
    dots.className = 'typing-dots';
    dots.innerHTML = '<span></span><span></span><span></span>';

    bubble.appendChild(dots);
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
