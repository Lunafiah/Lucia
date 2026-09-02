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

    // Initialize Canvas Avatar
    const canvas = document.getElementById('avatar-canvas');
    if (canvas && typeof AvatarRenderer !== 'undefined') {
      window.avatarRenderer = new AvatarRenderer(canvas);
    }

    this._setupEventListeners();
    this._setupVoiceControls();
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
      const res = await fetch('http://127.0.0.1:8765/voice/models');
      if (res.ok) {
        const data = await res.json();
        if (data.models && data.models.length > 0) {
          this.voiceModelSelect.innerHTML = '';
          data.models.forEach((m) => {
            const opt = document.createElement('option');
            opt.value = m.name;
            opt.textContent = m.name === 'default' ? 'Lucia Base Voice' : `RVC: ${m.name}`;
            if (m.is_active) opt.selected = true;
            this.voiceModelSelect.appendChild(opt);
          });
        }
      }
    } catch (err) {
      console.warn('[voice] Could not load voice models:', err);
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
        this.statusDot.className = 'status-dot';
        this.stateLabel.textContent = 'Awakening core...';
        break;

      case State.READY:
        if (this.splashOverlay) {
          this.splashOverlay.classList.add('hidden');
        }
        this.inputArea.disabled = false;
        this.statusDot.className = 'status-dot active';
        this.stateLabel.textContent = 'Active & Mindful';
        this._updateSendButtonState();
        this.inputArea.focus();
        break;

      case State.SENDING:
        this.inputArea.disabled = true;
        this.sendBtn.disabled = true;
        this.stateLabel.textContent = 'Reflecting...';
        break;

      case State.ERROR:
        this.inputArea.disabled = true;
        this.sendBtn.disabled = true;
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
              window.avatarRenderer.speak(audioBlob);
            }
          } catch (vErr) {
            console.warn('[voice] Voice synthesis playback error:', vErr);
          }
        }
      } else {
        this.appendMessage('error', 'Received empty response from companion.');
      }
      this.transitionTo(State.READY);
    } catch (err) {
      console.error('[chat] Send error:', err);
      this.removeTypingIndicator(typingIndicator);
      const errMsg = err.message || err.code || 'Failed to communicate with Lucia.';
      this.appendMessage('error', `Connection error: ${errMsg}`);
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
