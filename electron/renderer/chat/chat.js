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

    this._setupEventListeners();
    this._setupBackendListeners();
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
