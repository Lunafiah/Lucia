/**
 * Companion Settings Controller (settings.js)
 * Sub-Phase 7.5: Categorized Settings System
 *
 * Core UX Philosophy: "How I want Lucia to live with me on this machine."
 *
 * Architectural Invariants & Governance:
 * 1. Appearance vs. Identity: Controls visual rendering engine and attire asset pack.
 *    No character switchers, persona dropdowns, or alternate profiles.
 * 2. Philia Non-Gamified: Zero personality, mood, affection, or relationship sliders.
 * 3. Ephemerality vs. Permanence: Clearing chat view only refreshes the Talk feed;
 *    persistent SDM traces, Journal milestones, and affective bond are untouched.
 * 4. Zero Cloud Dependencies: 100% local edge execution (GGUF LLM, faster-whisper STT, RVC).
 * 5. Instant Live Preview with Auto-Persistence: Changes apply immediately and save to storage.
 */

class CompanionSettings {
  constructor() {
    // Modal & Structural Elements
    this.modal = document.getElementById('settings-modal');
    this.openBtn = document.getElementById('open-settings-btn');
    this.closeBtn = document.getElementById('close-settings-btn');
    this.doneBtn = document.getElementById('done-settings-btn');
    this.syncStatusText = document.getElementById('settings-sync-status-text');

    // Transient UI State (In-Memory Only, never stored in localStorage)
    this.activeTab = 'appearance';
    this.syncTimer = null;
    this.cachedAvatarData = null;
    this.cachedVoiceData = null;

    // Sidebar Tab Buttons
    this.tabButtons = {
      appearance: document.getElementById('settings-tab-btn-appearance'),
      voice: document.getElementById('settings-tab-btn-voice'),
      presence: document.getElementById('settings-tab-btn-presence'),
      privacy: document.getElementById('settings-tab-btn-privacy'),
      performance: document.getElementById('settings-tab-btn-performance'),
      advanced: document.getElementById('settings-tab-btn-advanced'),
    };

    // Tab Panes
    this.panes = {
      appearance: document.getElementById('settings-pane-appearance'),
      voice: document.getElementById('settings-pane-voice'),
      presence: document.getElementById('settings-pane-presence'),
      privacy: document.getElementById('settings-pane-privacy'),
      performance: document.getElementById('settings-pane-performance'),
      advanced: document.getElementById('settings-pane-advanced'),
    };

    // Appearance Controls
    this.engineSelect = document.getElementById('settings-avatar-engine-select');
    this.attireAssetSelect = document.getElementById('settings-avatar-model-select');
    this.gazeToggle = document.getElementById('settings-gaze-tracking-toggle');
    this.blinkToggle = document.getElementById('settings-ambient-blinking-toggle');

    // Voice & Audio Controls
    this.outputDeviceSelect = document.getElementById('settings-output-device-select');
    this.volumeSlider = document.getElementById('settings-volume-slider');
    this.volumeVal = document.getElementById('settings-volume-val');
    this.voiceTimbreSelect = document.getElementById('settings-voice-model-select');
    this.inputDeviceSelect = document.getElementById('settings-input-device-select');
    this.vadSlider = document.getElementById('settings-vad-sensitivity');
    this.vadVal = document.getElementById('settings-vad-val');

    // Desktop Presence Controls
    this.mascotStartupToggle = document.getElementById('settings-mascot-startup-toggle');
    this.mascotOpacitySlider = document.getElementById('settings-mascot-opacity');
    this.opacityVal = document.getElementById('settings-opacity-val');
    this.mascotPresetSelect = document.getElementById('settings-mascot-preset-select');
    this.mascotAutohideToggle = document.getElementById('settings-mascot-autohide-toggle');
    this.launchMascotBtn = document.getElementById('settings-launch-mascot-btn');

    // Privacy & Life Controls
    this.exportDataBtn = document.getElementById('settings-export-data-btn');
    this.clearChatBtn = document.getElementById('settings-clear-chat-btn');
    this.endLifeBtn = document.getElementById('settings-end-life-btn');

    // End-of-Life Solemn Confirmation Modal (Phase 7.7 Step 3)
    this.endLifeModal = document.getElementById('end-life-modal');
    this.endLifeConfirmInput = document.getElementById('end-life-confirm-input');
    this.endLifeDestroyBtn = document.getElementById('end-life-destroy-btn');
    this.endLifeCancelBtn = document.getElementById('end-life-cancel-btn');

    // Performance Controls
    this.autodetectBtn = document.getElementById('settings-autodetect-btn');
    this.profileSelect = document.getElementById('settings-profile-select');
    this.activeTierDisplay = document.getElementById('settings-active-tier');
    this.vramBudgetDisplay = document.getElementById('settings-vram-budget');
    this.ctxLengthDisplay = document.getElementById('settings-ctx-length');
    this.loopCadenceDisplay = document.getElementById('settings-loop-cadence');
    this.fpsSelect = document.getElementById('settings-fps-select');
    this.throttleBgToggle = document.getElementById('settings-throttle-bg-toggle');

    // Advanced Controls
    this.devModeToggle = document.getElementById('settings-dev-mode-toggle');
    this.apiStatusText = document.getElementById('settings-api-status-text');
    this.openDiagnosticsBtn = document.getElementById('settings-open-diagnostics-btn');

    this._bindEvents();
    this.loadInitialPreferences();
  }

  // ------------------------------------------------------------------------
  // Lifecycle & Tab Switching
  // ------------------------------------------------------------------------

  openSettings(tab = 'appearance') {
    if (!this.modal) return;
    this.modal.classList.add('active');
    this.switchTab(tab);
    this.refreshDynamicData();
  }

  closeSettings() {
    if (!this.modal) return;
    this.modal.classList.remove('active');
  }

  openEndLifeModal() {
    if (!this.endLifeModal) return;
    this.endLifeModal.classList.add('active');
    if (this.endLifeConfirmInput) {
      this.endLifeConfirmInput.value = '';
      this.endLifeConfirmInput.focus();
    }
    if (this.endLifeDestroyBtn) {
      this.endLifeDestroyBtn.disabled = true;
    }
  }

  closeEndLifeModal() {
    if (!this.endLifeModal) return;
    this.endLifeModal.classList.remove('active');
    if (this.endLifeConfirmInput) {
      this.endLifeConfirmInput.value = '';
    }
    if (this.endLifeDestroyBtn) {
      this.endLifeDestroyBtn.disabled = true;
    }
  }

  _validateEndLifeConfirmation() {
    if (!this.endLifeConfirmInput || !this.endLifeDestroyBtn) return;
    const val = this.endLifeConfirmInput.value.trim();
    // Strict confirmation guard: exact match "END LUCIA"
    const isValid = val === 'END LUCIA';
    this.endLifeDestroyBtn.disabled = !isValid;
  }

  _cleanupLuciaRendererState() {
    const identityKeys = [
      'lucia_profile',
      'lucia_user_name',
      'lucia_companion_name',
      'lucia_is_onboarded',
      'lucia_onboarded',
      'lucia_born_at',
      'lucia_chat_history',
      'lucia_recent_turns',
      'lucia_session_history',
      'lucia_memories_cache',
      'lucia_journal_cache',
    ];

    identityKeys.forEach((k) => {
      try {
        localStorage.removeItem(k);
      } catch (e) {}
    });
  }

  async executeEndLife() {
    if (this._isEndingLife) return;
    this._isEndingLife = true;

    // Concurrency / duplicate-submission protection & transitional state
    const destroyBtn = this.endLifeDestroyBtn;
    const cancelBtn = this.endLifeCancelBtn;
    const confirmInput = this.endLifeConfirmInput;

    const originalText = destroyBtn ? destroyBtn.textContent : "End Lucia's Life";
    if (destroyBtn) {
      destroyBtn.disabled = true;
      destroyBtn.textContent = "Ending Lucia's life...";
      destroyBtn.classList.add('destroying');
    }
    if (cancelBtn) cancelBtn.disabled = true;
    if (confirmInput) confirmInput.disabled = true;

    try {
      // Dispatch lifecycle end to backend
      const res = await fetch('http://127.0.0.1:8765/lifecycle/end', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
      });

      if (!res.ok) {
        throw new Error(`Lifecycle reset returned HTTP ${res.status}`);
      }

      const data = await res.json();
      console.log('[lifecycle] End-of-Life confirmed by backend:', data);

      // Clean up Lucia-specific client identity/memory state (preserving preferences)
      this._cleanupLuciaRendererState();

      // Clear presentation surfaces
      if (window.chatController && typeof window.chatController.clearPresentation === 'function') {
        window.chatController.clearPresentation();
      } else if (window.chatController && window.chatController.messagesContainer) {
        window.chatController.messagesContainer.innerHTML = '';
      }

      if (window.companionJournal && typeof window.companionJournal.clearPresentation === 'function') {
        window.companionJournal.clearPresentation();
      }

      // Close End-of-Life modal and Settings modal
      this.closeEndLifeModal();
      this.closeSettings();

      // Transition into Genesis Awakening by reloading profile
      if (window.chatController && typeof window.chatController._loadProfile === 'function') {
        await window.chatController._loadProfile();
      } else {
        const genesisModal = document.getElementById('genesis-modal');
        if (genesisModal) genesisModal.classList.add('active');
      }

      if (typeof this._onEndLifeConfirmed === 'function') {
        this._onEndLifeConfirmed();
      }
    } catch (err) {
      console.error('[lifecycle] End-of-Life reset failed:', err);
      // Critical failure boundary: leave current Lucia session intact
      if (typeof window.alert === 'function') {
        window.alert(`Could not complete End-of-Life reset: ${err.message || err}. Lucia's memory and state remain protected.`);
      }
      if (destroyBtn) {
        destroyBtn.disabled = false;
        destroyBtn.textContent = originalText;
        destroyBtn.classList.remove('destroying');
      }
      if (cancelBtn) cancelBtn.disabled = false;
      if (confirmInput) confirmInput.disabled = false;
    } finally {
      this._isEndingLife = false;
    }
  }

  switchTab(tabKey) {
    if (!this.panes[tabKey]) return;
    this.activeTab = tabKey;

    Object.keys(this.tabButtons).forEach((k) => {
      const btn = this.tabButtons[k];
      if (btn) btn.classList.toggle('active', k === tabKey);
    });

    Object.keys(this.panes).forEach((k) => {
      const pane = this.panes[k];
      if (pane) pane.classList.toggle('active', k === tabKey);
    });
  }

  notifySynchronized(message = 'Settings synchronized with local runtime') {
    if (!this.syncStatusText) return;
    this.syncStatusText.textContent = message;
    if (this.syncTimer) clearTimeout(this.syncTimer);
    this.syncTimer = setTimeout(() => {
      if (this.syncStatusText) {
        this.syncStatusText.textContent = 'All settings synchronized with local runtime';
      }
    }, 2000);
  }

  // ------------------------------------------------------------------------
  // Event Binding
  // ------------------------------------------------------------------------

  _bindEvents() {
    // Modal Open / Close
    if (this.openBtn) {
      this.openBtn.addEventListener('click', () => this.openSettings());
    }
    if (this.closeBtn) {
      this.closeBtn.addEventListener('click', () => this.closeSettings());
    }
    if (this.doneBtn) {
      this.doneBtn.addEventListener('click', () => this.closeSettings());
    }
    if (this.modal) {
      this.modal.addEventListener('click', (e) => {
        if (e.target === this.modal) this.closeSettings();
      });
    }

    // Global ESC dismiss
    window.addEventListener('keydown', (e) => {
      if (e.key === 'Escape') {
        if (this.endLifeModal && this.endLifeModal.classList.contains('active')) {
          this.closeEndLifeModal();
          e.stopPropagation();
          return;
        }
        if (this.modal && this.modal.classList.contains('active')) {
          this.closeSettings();
        }
      }
    });

    // Sidebar Tab Buttons
    Object.keys(this.tabButtons).forEach((key) => {
      const btn = this.tabButtons[key];
      if (btn) {
        btn.addEventListener('click', () => this.switchTab(key));
      }
    });

    // 1. Appearance Events
    if (this.engineSelect) {
      this.engineSelect.addEventListener('change', (e) => {
        const engine = e.target.value;
        localStorage.setItem('lucia_avatar_engine', engine);
        this._updateAttireOptions(engine);
        const activeModel = this.attireAssetSelect ? this.attireAssetSelect.value : 'default';
        if (window.avatarRenderer && window.avatarRenderer.setEngine) {
          window.avatarRenderer.setEngine(engine, activeModel);
        }
        this.notifySynchronized(`Switched to ${engine.toUpperCase()} engine`);
      });
    }

    if (this.attireAssetSelect) {
      this.attireAssetSelect.addEventListener('change', (e) => {
        const model = e.target.value;
        const engine = this.engineSelect ? this.engineSelect.value : 'canvas';
        localStorage.setItem('lucia_avatar_model', model);
        if (window.avatarRenderer && window.avatarRenderer.setEngine) {
          window.avatarRenderer.setEngine(engine, model);
        }
        this.notifySynchronized(`Loaded attire asset: ${model}`);
      });
    }

    if (this.gazeToggle) {
      this.gazeToggle.addEventListener('change', (e) => {
        const enabled = e.target.checked;
        localStorage.setItem('lucia_gaze_enabled', enabled ? 'true' : 'false');
        if (window.avatarRenderer && window.avatarRenderer.setGazeTracking) {
          window.avatarRenderer.setGazeTracking(enabled);
        }
        this.notifySynchronized(enabled ? 'Gaze tracking enabled' : 'Gaze tracking disabled');
      });
    }

    if (this.blinkToggle) {
      this.blinkToggle.addEventListener('change', (e) => {
        const enabled = e.target.checked;
        localStorage.setItem('lucia_blinking_enabled', enabled ? 'true' : 'false');
        if (window.avatarRenderer && window.avatarRenderer.setAmbientBlinking) {
          window.avatarRenderer.setAmbientBlinking(enabled);
        }
        this.notifySynchronized(enabled ? 'Natural blinking enabled' : 'Blinking disabled');
      });
    }

    // 2. Voice & Audio Events
    if (this.volumeSlider) {
      this.volumeSlider.addEventListener('input', (e) => {
        const vol = parseInt(e.target.value, 10);
        if (this.volumeVal) this.volumeVal.textContent = `${vol}%`;
        localStorage.setItem('lucia_master_volume', vol.toString());
        if (window.chatController && window.chatController.volumeSlider) {
          window.chatController.volumeSlider.value = (vol / 100).toString();
        }
        this.notifySynchronized();
      });
    }

    if (this.voiceTimbreSelect) {
      this.voiceTimbreSelect.addEventListener('change', async (e) => {
        const timbre = e.target.value;
        localStorage.setItem('lucia_voice_timbre', timbre);
        try {
          await fetch('http://127.0.0.1:8765/voice/select-model', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ model_name: timbre }),
          });
        } catch (err) {
          console.warn('[settings] Voice timbre selection API unavailable:', err);
        }
        this.notifySynchronized(`Acoustic timbre: ${timbre}`);
      });
    }

    if (this.outputDeviceSelect) {
      this.outputDeviceSelect.addEventListener('change', (e) => {
        const devId = e.target.value;
        localStorage.setItem('lucia_audio_output_device', devId);
        if (window.avatarRenderer && window.avatarRenderer.lipSync && window.avatarRenderer.lipSync.currentAudio) {
          const aud = window.avatarRenderer.lipSync.currentAudio;
          if (typeof aud.setSinkId === 'function') {
            aud.setSinkId(devId).catch((err) => console.warn('[audio] setSinkId failed:', err));
          }
        }
        this.notifySynchronized();
      });
    }

    if (this.inputDeviceSelect) {
      this.inputDeviceSelect.addEventListener('change', (e) => {
        const devId = e.target.value;
        localStorage.setItem('lucia_audio_input_device', devId);
        this.notifySynchronized();
      });
    }

    if (this.vadSlider) {
      this.vadSlider.addEventListener('input', (e) => {
        const val = parseInt(e.target.value, 10);
        if (this.vadVal) this.vadVal.textContent = val.toString();
        localStorage.setItem('lucia_vad_sensitivity', val.toString());
        this.notifySynchronized();
      });
    }

    // 3. Desktop Presence Events
    if (this.mascotStartupToggle) {
      this.mascotStartupToggle.addEventListener('change', (e) => {
        const enabled = e.target.checked;
        localStorage.setItem('lucia_startup_mascot', enabled ? 'true' : 'false');
        this.notifySynchronized();
      });
    }

    if (this.mascotOpacitySlider) {
      this.mascotOpacitySlider.addEventListener('input', (e) => {
        const val = e.target.value;
        if (this.opacityVal) this.opacityVal.textContent = `${Math.round(parseFloat(val) * 100)}%`;
        localStorage.setItem('lucia_mascot_opacity', val);

        if (document.body.classList.contains('mascot-mode')) {
          document.body.style.opacity = val;
        }
        this.notifySynchronized();
      });
    }

    if (this.mascotPresetSelect) {
      this.mascotPresetSelect.addEventListener('change', (e) => {
        const preset = e.target.value;
        localStorage.setItem('lucia_mascot_default_preset', preset);
        if (document.body.classList.contains('mascot-mode') && window.avatarRenderer && window.avatarRenderer.setZoomPreset) {
          window.avatarRenderer.setZoomPreset(preset);
        }
        this.notifySynchronized(`Default scale: ${preset}`);
      });
    }

    if (this.mascotAutohideToggle) {
      this.mascotAutohideToggle.addEventListener('change', (e) => {
        const enabled = e.target.checked;
        localStorage.setItem('lucia_mascot_autohide', enabled ? 'true' : 'false');
        this.notifySynchronized();
      });
    }

    if (this.launchMascotBtn) {
      this.launchMascotBtn.addEventListener('click', () => {
        this.closeSettings();
        if (window.lucia && window.lucia.window && window.lucia.window.toggleMascot) {
          window.lucia.window.toggleMascot();
        }
      });
    }

    // 4. Privacy & Life Events
    if (this.exportDataBtn) {
      this.exportDataBtn.addEventListener('click', () => {
        if (window.companionJournal && window.companionJournal.exportJournal) {
          window.companionJournal.exportJournal();
        }
      });
    }

    if (this.clearChatBtn) {
      this.clearChatBtn.addEventListener('click', () => {
        if (window.chatController && window.chatController.clearScreen) {
          window.chatController.clearScreen();
        }
        this.notifySynchronized('Active conversation view refreshed (Memories preserved)');
      });
    }

    if (this.endLifeBtn) {
      this.endLifeBtn.addEventListener('click', () => {
        this.openEndLifeModal();
      });
    }

    if (this.endLifeConfirmInput) {
      this.endLifeConfirmInput.addEventListener('input', () => {
        this._validateEndLifeConfirmation();
      });
      this.endLifeConfirmInput.addEventListener('keydown', (e) => {
        if (e.key === 'Escape') {
          this.closeEndLifeModal();
        }
      });
    }

    if (this.endLifeCancelBtn) {
      this.endLifeCancelBtn.addEventListener('click', () => {
        this.closeEndLifeModal();
      });
    }

    if (this.endLifeModal) {
      this.endLifeModal.addEventListener('click', (e) => {
        if (e.target === this.endLifeModal || e.target.classList.contains('end-life-backdrop-solemn')) {
          this.closeEndLifeModal();
        }
      });
    }

    if (this.endLifeDestroyBtn) {
      this.endLifeDestroyBtn.addEventListener('click', async () => {
        if (this.endLifeDestroyBtn.disabled || this._isEndingLife) return;
        await this.executeEndLife();
      });
    }

    // 5. Performance Events
    if (this.profileSelect) {
      this.profileSelect.addEventListener('change', async (e) => {
        const tier = e.target.value;
        await this._applySystemProfile(tier);
      });
    }

    if (this.autodetectBtn) {
      this.autodetectBtn.addEventListener('click', async () => {
        if (this.profileSelect) this.profileSelect.value = 'auto';
        await this._applySystemProfile('auto');
      });
    }

    if (this.fpsSelect) {
      this.fpsSelect.addEventListener('change', (e) => {
        const fps = parseInt(e.target.value, 10);
        localStorage.setItem('lucia_target_fps', fps.toString());
        if (window.avatarRenderer && window.avatarRenderer.setTargetFps) {
          window.avatarRenderer.setTargetFps(fps);
        }
        this.notifySynchronized(`Framerate set to ${fps} FPS`);
      });
    }

    if (this.throttleBgToggle) {
      this.throttleBgToggle.addEventListener('change', (e) => {
        const enabled = e.target.checked;
        localStorage.setItem('lucia_throttle_bg', enabled ? 'true' : 'false');
        this.notifySynchronized();
      });
    }

    // 6. Advanced Events
    if (this.devModeToggle) {
      this.devModeToggle.addEventListener('change', (e) => {
        const enabled = e.target.checked;
        localStorage.setItem('lucia_developer_mode', enabled ? 'true' : 'false');
        this.notifySynchronized(enabled ? 'Developer mode enabled' : 'Developer mode disabled');
      });
    }

    if (this.openDiagnosticsBtn) {
      this.openDiagnosticsBtn.addEventListener('click', () => {
        this.closeSettings();
        if (window.emotionDebugPanel && typeof window.emotionDebugPanel.openDrawer === 'function') {
          window.emotionDebugPanel.openDrawer();
        } else {
          const diagBtn = document.getElementById('toggle-diagnostics-btn');
          if (diagBtn) diagBtn.click();
        }
      });
    }
  }

  // ------------------------------------------------------------------------
  // Preferences Initialization & Loading
  // ------------------------------------------------------------------------

  loadInitialPreferences() {
    // 1. Appearance
    const savedEngine = localStorage.getItem('lucia_avatar_engine') || 'canvas';
    if (this.engineSelect) this.engineSelect.value = savedEngine;

    const gazeEnabled = localStorage.getItem('lucia_gaze_enabled') !== 'false';
    if (this.gazeToggle) this.gazeToggle.checked = gazeEnabled;
    if (window.avatarRenderer && window.avatarRenderer.setGazeTracking) {
      window.avatarRenderer.setGazeTracking(gazeEnabled);
    }

    const blinkEnabled = localStorage.getItem('lucia_blinking_enabled') !== 'false';
    if (this.blinkToggle) this.blinkToggle.checked = blinkEnabled;
    if (window.avatarRenderer && window.avatarRenderer.setAmbientBlinking) {
      window.avatarRenderer.setAmbientBlinking(blinkEnabled);
    }

    // 2. Voice & Audio
    const savedVol = parseInt(localStorage.getItem('lucia_master_volume') || '85', 10);
    if (this.volumeSlider) this.volumeSlider.value = savedVol.toString();
    if (this.volumeVal) this.volumeVal.textContent = `${savedVol}%`;

    const savedVad = parseInt(localStorage.getItem('lucia_vad_sensitivity') || '14', 10);
    if (this.vadSlider) this.vadSlider.value = savedVad.toString();
    if (this.vadVal) this.vadVal.textContent = savedVad.toString();

    // 3. Desktop Presence
    const startupMascot = localStorage.getItem('lucia_startup_mascot') === 'true';
    if (this.mascotStartupToggle) this.mascotStartupToggle.checked = startupMascot;

    const savedOpacity = localStorage.getItem('lucia_mascot_opacity') || '1';
    if (this.mascotOpacitySlider) this.mascotOpacitySlider.value = savedOpacity;
    if (this.opacityVal) this.opacityVal.textContent = `${Math.round(parseFloat(savedOpacity) * 100)}%`;

    const savedPreset = localStorage.getItem('lucia_mascot_default_preset') || 'normal';
    if (this.mascotPresetSelect) this.mascotPresetSelect.value = savedPreset;

    const autohide = localStorage.getItem('lucia_mascot_autohide') === 'true';
    if (this.mascotAutohideToggle) this.mascotAutohideToggle.checked = autohide;

    // 4. Performance
    const savedFps = parseInt(localStorage.getItem('lucia_target_fps') || '60', 10);
    if (this.fpsSelect) this.fpsSelect.value = savedFps.toString();
    if (window.avatarRenderer && window.avatarRenderer.setTargetFps) {
      window.avatarRenderer.setTargetFps(savedFps);
    }

    const throttleBg = localStorage.getItem('lucia_throttle_bg') !== 'false';
    if (this.throttleBgToggle) this.throttleBgToggle.checked = throttleBg;

    // 5. Advanced
    const devMode = localStorage.getItem('lucia_developer_mode') === 'true';
    if (this.devModeToggle) this.devModeToggle.checked = devMode;
  }

  async refreshDynamicData() {
    await Promise.all([
      this.loadAvatarAssets(),
      this.loadVoiceTimbres(),
      this.populateAudioDevices(),
      this.loadSystemProfile(),
      this.checkApiStatus(),
    ]);
  }

  async loadAvatarAssets() {
    try {
      let data = null;
      if (window.lucia && window.lucia.models && window.lucia.models.getAvatars) {
        data = await window.lucia.models.getAvatars();
      } else {
        const res = await fetch('http://127.0.0.1:8765/models/avatar');
        if (res.ok) data = await res.json();
      }

      if (data) {
        this.cachedAvatarData = data;
        const currentEngine = this.engineSelect ? this.engineSelect.value : 'canvas';
        this._updateAttireOptions(currentEngine);
      }
    } catch (err) {
      console.warn('[settings] Failed to load avatar assets:', err);
    }
  }

  _updateAttireOptions(engine) {
    if (!this.attireAssetSelect) return;
    this.attireAssetSelect.innerHTML = '';

    let list = [];
    if (this.cachedAvatarData) {
      if (engine === 'sprites') list = this.cachedAvatarData.sprites || [];
      else if (engine === 'live2d') list = this.cachedAvatarData.live2d || [];
      else if (engine === 'vrm') list = this.cachedAvatarData.vrm || [];
    }

    if (list.length === 0) {
      const opt = document.createElement('option');
      opt.value = 'default';
      opt.textContent = 'Default Lucia Attire';
      this.attireAssetSelect.appendChild(opt);
    } else {
      const savedModel = localStorage.getItem('lucia_avatar_model');
      list.forEach((m) => {
        const opt = document.createElement('option');
        opt.value = m;
        opt.textContent = m;
        if (savedModel && m === savedModel) opt.selected = true;
        this.attireAssetSelect.appendChild(opt);
      });
    }
  }

  async loadVoiceTimbres() {
    try {
      let data = null;
      if (window.lucia && window.lucia.models && window.lucia.models.getVoices) {
        data = await window.lucia.models.getVoices();
      } else {
        const res = await fetch('http://127.0.0.1:8765/voice/models');
        if (res.ok) data = await res.json();
      }

      if (data && this.voiceTimbreSelect) {
        this.cachedVoiceData = data;
        this.voiceTimbreSelect.innerHTML = '';

        const models = data.models || [];
        const activeTimbre = localStorage.getItem('lucia_voice_timbre') || data.active_model || 'default';

        if (models.length === 0) {
          const opt = document.createElement('option');
          opt.value = 'default';
          opt.textContent = 'Default (Edge Neural Base)';
          this.voiceTimbreSelect.appendChild(opt);
        } else {
          models.forEach((m) => {
            const opt = document.createElement('option');
            opt.value = m.name;
            opt.textContent = m.name === 'default' ? 'Default (Natural Speech)' : `RVC Filter: ${m.name}`;
            if (m.name === activeTimbre) opt.selected = true;
            this.voiceTimbreSelect.appendChild(opt);
          });
        }
      }
    } catch (err) {
      console.warn('[settings] Failed to load voice timbres:', err);
    }
  }

  async populateAudioDevices() {
    if (!navigator.mediaDevices || !navigator.mediaDevices.enumerateDevices) return;
    try {
      const devices = await navigator.mediaDevices.enumerateDevices();
      const savedOut = localStorage.getItem('lucia_audio_output_device') || 'default';
      const savedIn = localStorage.getItem('lucia_audio_input_device') || 'default';

      if (this.outputDeviceSelect) {
        this.outputDeviceSelect.innerHTML = '<option value="default">Default Speaker</option>';
        devices
          .filter((d) => d.kind === 'audiooutput')
          .forEach((d) => {
            const opt = document.createElement('option');
            opt.value = d.deviceId;
            opt.textContent = d.label || `Speaker ${d.deviceId.slice(0, 5)}...`;
            if (d.deviceId === savedOut) opt.selected = true;
            this.outputDeviceSelect.appendChild(opt);
          });
      }

      if (this.inputDeviceSelect) {
        this.inputDeviceSelect.innerHTML = '<option value="default">Default Microphone</option>';
        devices
          .filter((d) => d.kind === 'audioinput')
          .forEach((d) => {
            const opt = document.createElement('option');
            opt.value = d.deviceId;
            opt.textContent = d.label || `Microphone ${d.deviceId.slice(0, 5)}...`;
            if (d.deviceId === savedIn) opt.selected = true;
            this.inputDeviceSelect.appendChild(opt);
          });
      }
    } catch (err) {
      console.warn('[settings] Device enumeration failed:', err);
    }
  }

  async loadSystemProfile() {
    try {
      let data = null;
      if (window.lucia && window.lucia.system && window.lucia.system.getProfile) {
        data = await window.lucia.system.getProfile();
      } else {
        const res = await fetch('http://127.0.0.1:8765/system/profile');
        if (res.ok) data = await res.json();
      }

      if (data) {
        if (this.activeTierDisplay && data.name) this.activeTierDisplay.textContent = data.name;
        if (this.vramBudgetDisplay && data.vram_mb !== undefined) {
          this.vramBudgetDisplay.textContent = data.vram_mb > 0 ? `~${data.vram_mb} MB` : 'CPU Only';
        }
        if (this.ctxLengthDisplay && data.n_ctx) {
          this.ctxLengthDisplay.textContent = `${data.n_ctx.toLocaleString()} tokens`;
        }
        if (this.loopCadenceDisplay && data.loop_cadence_ms) {
          this.loopCadenceDisplay.textContent = `${data.loop_cadence_ms} ms`;
        }
        if (this.profileSelect && data.tier) {
          const match = Array.from(this.profileSelect.options).find((o) => o.value === data.tier);
          if (match) match.selected = true;
        }
      }
    } catch (err) {
      console.warn('[settings] Failed to load system profile:', err);
    }
  }

  async _applySystemProfile(tier) {
    localStorage.setItem('lucia_hardware_profile', tier);
    try {
      let data = null;
      if (window.lucia && window.lucia.system && window.lucia.system.setProfile) {
        data = await window.lucia.system.setProfile(tier);
      } else {
        const res = await fetch('http://127.0.0.1:8765/system/profile', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ profile: tier }),
        });
        if (res.ok) data = await res.json();
      }

      if (data) {
        if (this.activeTierDisplay && data.name) this.activeTierDisplay.textContent = data.name;
        if (this.vramBudgetDisplay && data.vram_mb !== undefined) {
          this.vramBudgetDisplay.textContent = data.vram_mb > 0 ? `~${data.vram_mb} MB` : 'CPU Only';
        }
        if (this.ctxLengthDisplay && data.n_ctx) {
          this.ctxLengthDisplay.textContent = `${data.n_ctx.toLocaleString()} tokens`;
        }
        if (this.loopCadenceDisplay && data.loop_cadence_ms) {
          this.loopCadenceDisplay.textContent = `${data.loop_cadence_ms} ms`;
        }
      }
      this.notifySynchronized(`Profile applied: ${tier}`);
    } catch (err) {
      console.warn('[settings] Failed to apply profile:', err);
    }
  }

  async checkApiStatus() {
    if (!this.apiStatusText) return;
    try {
      const res = await fetch('http://127.0.0.1:8765/health', { signal: AbortSignal.timeout(1500) });
      if (res.ok) {
        this.apiStatusText.textContent = '127.0.0.1:8765 (Connected)';
        this.apiStatusText.style.color = '#10b981';
      } else {
        this.apiStatusText.textContent = '127.0.0.1:8765 (Degraded)';
        this.apiStatusText.style.color = '#f59e0b';
      }
    } catch (err) {
      this.apiStatusText.textContent = '127.0.0.1:8765 (Offline / Standalone Preview)';
      this.apiStatusText.style.color = '#94a3b8';
    }
  }
}

// Global Export
if (typeof window !== 'undefined') {
  window.CompanionSettings = CompanionSettings;
}

if (typeof module !== 'undefined' && module.exports) {
  module.exports = { CompanionSettings };
}
