/**
 * Emotion Debug Panel Controller (panel.js)
 * High-frequency 500ms telemetry visualizer for PAD, somatic markers, constraints, SDM memory traces, and hardware profile.
 *
 * Requirements: Phase 7.6 (Dedicated Diagnostics Console)
 */

class EmotionDebugPanel {
  constructor() {
    this.pollInterval = null;
    this.pollRateMs = 500;
    this.debugPane = document.getElementById('debug-pane');
    this.modal = document.getElementById('diagnostics-modal');
    this.backdrop = document.getElementById('diagnostics-backdrop');

    // PAD elements
    this.pFill = document.getElementById('pad-p-fill');
    this.aFill = document.getElementById('pad-a-fill');
    this.dFill = document.getElementById('pad-d-fill');
    this.pVal = document.getElementById('pad-p-val');
    this.aVal = document.getElementById('pad-a-val');
    this.dVal = document.getElementById('pad-d-val');
    this.philiaDist = document.getElementById('pad-philia-dist');

    // Somatic elements
    this.stabilityFill = document.getElementById('somatic-stability-fill');
    this.energyFill = document.getElementById('somatic-energy-fill');
    this.loadFill = document.getElementById('somatic-load-fill');
    this.tensionFill = document.getElementById('somatic-tension-fill');
    this.stabilityVal = document.getElementById('somatic-stability-val');
    this.energyVal = document.getElementById('somatic-energy-val');
    this.loadVal = document.getElementById('somatic-load-val');
    this.tensionVal = document.getElementById('somatic-tension-val');

    // Conversational State & Dynamic Constraints elements
    this.convMood = document.getElementById('conv-mood-val');
    this.convVoice = document.getElementById('conv-voice-val');
    this.convLatency = document.getElementById('conv-latency-val');
    this.convDepth = document.getElementById('conv-depth-val');
    this.constraintTokens = document.getElementById('constraint-tokens-val');
    this.constraintTemp = document.getElementById('constraint-temp-val');

    // Memory elements
    this.memoryTraceCount = document.getElementById('memory-trace-count');
    this.sdmCapacity = document.getElementById('sdm-capacity-val');
    this.sdmSaturation = document.getElementById('sdm-saturation-val');
    this.sdmDecay = document.getElementById('sdm-decay-val');

    // Stability Telemetry elements (LNN / Active Inference)
    this.lsiVal = document.getElementById('telemetry-lsi-val');
    this.jitterVal = document.getElementById('telemetry-jitter-val');
    this.feVal = document.getElementById('telemetry-fe-val');
    this.varianceVal = document.getElementById('telemetry-variance-val');
    this.recoveryVal = document.getElementById('telemetry-recovery-val');
    this.uptimeVal = document.getElementById('telemetry-uptime-val');
    this.statusBadge = document.getElementById('stability-status-badge');
    this.tickCounter = 0;

    // Hardware & Inference profile elements
    this.hwTier = document.getElementById('hw-tier-val');
    this.hwGpuLayers = document.getElementById('hw-gpu-layers-val');
    this.hwVram = document.getElementById('hw-vram-val');
    this.hwCtx = document.getElementById('hw-ctx-val');
    this.hwCadence = document.getElementById('hw-cadence-val');

    // Track voice activity via lipSync polling
    this._voiceActivityTimer = null;
    this._hwProfileTimer = null;

    this._setupBackendListeners();
    this._startVoiceActivityMonitor();
    this._setupDrawerControls();
    this.fetchHardwareProfile();

    // Periodic hardware profile refresh (~10s)
    this._hwProfileTimer = setInterval(() => {
      if (this.isDrawerOpen()) {
        this.fetchHardwareProfile();
      }
    }, 10000);
  }

  _setupBackendListeners() {
    if (window.lucia && window.lucia.on) {
      window.lucia.on('backend:ready', () => {
        this.startPolling();
        this.fetchHardwareProfile();
      });

      window.lucia.on('backend:error', () => {
        this.stopPolling();
        this.showStaleIndicator(true);
      });
    }
  }

  startPolling() {
    if (this.pollInterval) clearInterval(this.pollInterval);

    this.showStaleIndicator(false);
    this.pollOnce();

    this.pollInterval = setInterval(() => {
      this.pollOnce();
    }, this.pollRateMs);
  }

  stopPolling() {
    if (this.pollInterval) {
      clearInterval(this.pollInterval);
      this.pollInterval = null;
    }
    if (this._hwProfileTimer) {
      clearInterval(this._hwProfileTimer);
      this._hwProfileTimer = null;
    }
    if (this._voiceActivityTimer) {
      clearInterval(this._voiceActivityTimer);
      this._voiceActivityTimer = null;
    }
  }

  async pollOnce() {
    if (!window.lucia || !window.lucia.state) return;

    try {
      const snapshot = await window.lucia.state.get();
      this.renderSnapshot(snapshot);

      // Poll stability telemetry every 4 ticks (~2.0 seconds)
      this.tickCounter = (this.tickCounter + 1) % 4;
      if (this.tickCounter === 0) {
        try {
          const res = await fetch('http://127.0.0.1:8765/telemetry/stability');
          if (res.ok) {
            const sData = await res.json();
            this.renderStabilitySnapshot(sData);
          }
        } catch (sErr) {}
      }

      this.showStaleIndicator(false);
    } catch (err) {
      // Show subtle stale indicator without wiping out existing values
      this.showStaleIndicator(true);
    }
  }

  renderSnapshot(snap) {
    if (!snap) return;

    // 1. PAD Bars & Avatar Expression & Distance
    if (snap.pad) {
      this._updatePADBar(this.pFill, this.pVal, snap.pad.pleasure);
      this._updatePADBar(this.aFill, this.aVal, snap.pad.arousal);
      this._updatePADBar(this.dFill, this.dVal, snap.pad.dominance);

      if (window.avatarRenderer && typeof window.avatarRenderer.updateEmotion === 'function') {
        window.avatarRenderer.updateEmotion(snap.pad);
      }

      // Mathematical Euclidean distance to Philia resting attractor (+0.25, -0.05, +0.05)
      if (this.philiaDist) {
        const dist = this.computePhiliaDistance(snap.pad.pleasure, snap.pad.arousal, snap.pad.dominance);
        this.philiaDist.textContent = `Δ = ${dist.toFixed(3)}`;
      }

      // Affective classification via Russell's 2D circumplex model (not self-report)
      const moodLabel = this._deriveMood(snap.pad);
      if (this.convMood) {
        this.convMood.textContent = moodLabel;
      }
    }

    // 2. Somatic Markers
    if (snap.somatic) {
      this._updateProgressBar(this.stabilityFill, this.stabilityVal, snap.somatic.stability);
      this._updateProgressBar(this.energyFill, this.energyVal, snap.somatic.energy);
      this._updateProgressBar(this.loadFill, this.loadVal, snap.somatic.cognitive_load);
      this._updateProgressBar(this.tensionFill, this.tensionVal, snap.somatic.tension);
    }

    // 3. Conversational Constraints
    if (snap.constraints) {
      if (this.convLatency) this.convLatency.textContent = snap.constraints.latency_ms > 0 ? `+${snap.constraints.latency_ms} ms` : '+0 ms';
      if (this.convDepth) this.convDepth.textContent = `k=${snap.constraints.reasoning_depth || 1}`;
      if (this.constraintTokens) this.constraintTokens.textContent = String(snap.constraints.max_tokens || 150);
      if (this.constraintTemp) this.constraintTemp.textContent = (snap.constraints.temperature !== undefined) ? snap.constraints.temperature.toFixed(2) : '0.75';
    }

    // 4. Memory Traces
    if (typeof snap.memory_trace_count === 'number' && this.memoryTraceCount) {
      this.memoryTraceCount.textContent = String(snap.memory_trace_count);
    }
  }

  renderStabilitySnapshot(sData) {
    if (!sData) return;

    if (this.lsiVal) this.lsiVal.textContent = `${Math.round((sData.lsi || 0) * 100)}%`;
    if (this.jitterVal) this.jitterVal.textContent = `${(sData.fast_loop_jitter_mean_ms || 0).toFixed(1)} ms`;
    if (this.statusBadge) {
      const st = (sData.status || 'nominal').toUpperCase();
      this.statusBadge.textContent = st;
      this.statusBadge.style.color = st === 'NOMINAL' ? '#34d399' : (st === 'RECOVERING' ? '#f59e0b' : '#ef4444');
    }
    if (this.feVal) {
      this.feVal.textContent = (sData.free_energy_surprise_mean || 0).toFixed(4);
    }
    if (this.varianceVal) {
      this.varianceVal.textContent = (sData.ode_velocity_variance || 0).toFixed(4);
    }
    if (this.recoveryVal) {
      this.recoveryVal.textContent = String(sData.recovery_count || 0);
    }
    if (this.uptimeVal) {
      const uptimeSec = Math.floor(sData.uptime_seconds || 0);
      if (uptimeSec >= 3600) {
        this.uptimeVal.textContent = `${Math.floor(uptimeSec / 3600)}h ${Math.floor((uptimeSec % 3600) / 60)}m`;
      } else if (uptimeSec >= 60) {
        this.uptimeVal.textContent = `${Math.floor(uptimeSec / 60)}m ${uptimeSec % 60}s`;
      } else {
        this.uptimeVal.textContent = `${uptimeSec}s`;
      }
    }
    if (this.sdmSaturation && sData.sdm_saturation_pct !== undefined) {
      this.sdmSaturation.textContent = `${(sData.sdm_saturation_pct || 0).toFixed(1)}%`;
    }
  }

  async fetchHardwareProfile() {
    try {
      let prof = null;
      if (window.lucia && window.lucia.system && typeof window.lucia.system.getHardwareCapabilities === 'function') {
        prof = await window.lucia.system.getHardwareCapabilities();
      } else if (window.lucia && window.lucia.system && typeof window.lucia.system.getProfile === 'function') {
        prof = await window.lucia.system.getProfile();
      } else {
        const res = await fetch('http://127.0.0.1:8765/system/hardware');
        if (res.ok) prof = await res.json();
      }
      if (prof) {
        this.renderHardwareProfile(prof);
      }
    } catch (e) {}
  }

  renderHardwareProfile(prof) {
    if (!prof) return;
    if (this.hwTier) this.hwTier.textContent = prof.device_name || (prof.cuda_available ? 'CUDA' : 'Host CPU');
    if (this.hwGpuLayers) {
      this.hwGpuLayers.textContent = prof.cuda_available ? 'CUDA Accelerated' : 'CPU Execution';
    }
    if (this.hwVram) this.hwVram.textContent = `${(prof.vram_mb || 0).toLocaleString()} MB`;
    if (this.hwCtx) this.hwCtx.textContent = `${prof.cpu_threads || 1} CPU threads`;
    if (this.hwCadence) this.hwCadence.textContent = '200 ms';
    if (this.sdmCapacity && prof.sdm_capacity) {
      this.sdmCapacity.textContent = (prof.sdm_capacity).toLocaleString();
    }
  }

  /**
   * Computes Euclidean distance to Philia resting attractor (P=+0.25, A=-0.05, D=+0.05).
   * Strictly a mathematical Euclidean distance metric, not a relationship or affinity score.
   */
  computePhiliaDistance(p, a, d) {
    const dp = (p || 0) - 0.25;
    const da = (a || 0) - (-0.05);
    const dd = (d || 0) - 0.05;
    return Math.sqrt(dp * dp + da * da + dd * dd);
  }

  /**
   * Maps PAD coordinates onto Russell's 2D circumplex model quadrant.
   * Strictly a mathematical affective classification, avoiding subjective emotional self-report.
   */
  _deriveMood(pad) {
    const p = pad.pleasure || 0;
    const a = pad.arousal || 0;
    const d = pad.dominance || 0;
    if (p > 0.4 && a > 0.3) return 'Vigorous / High Valence';
    if (p > 0.4 && a < -0.1) return 'Content / Low Arousal';
    if (p > 0.15 && Math.abs(a) < 0.2) return 'Calm / Pleasant';
    if (p < -0.3 && a > 0.3) return 'Tense / High Arousal';
    if (p < -0.3 && a < -0.1) return 'Subdued / Low Valence';
    if (p < -0.2 && d > 0.2) return 'Agitated / High Dominance';
    if (a > 0.5) return 'Alert / Elevated Arousal';
    if (a < -0.4) return 'Quiet / Restful';
    return 'Neutral / Basal';
  }

  /**
   * Monitors lipSync voice activity every 250ms to update Voice Activity badge.
   */
  _startVoiceActivityMonitor() {
    setInterval(() => {
      if (!this.convVoice) return;
      const renderer = window.avatarRenderer;
      if (renderer && renderer.lipSync && typeof renderer.lipSync.getMouthOpen === 'function') {
        const mo = renderer.lipSync.getMouthOpen();
        if (mo > 0.08) {
          this.convVoice.textContent = 'Speaking 🔊';
          this.convVoice.style.color = '#34d399';
        } else {
          this.convVoice.textContent = 'Quiet';
          this.convVoice.style.color = '';
        }
      }
    }, 250);
  }

  _updatePADBar(fillElem, valElem, value) {
    if (!fillElem || !valElem) return;

    const clamped = Math.max(-1.0, Math.min(1.0, value));
    const sign = clamped >= 0 ? '+' : '';
    valElem.textContent = `${sign}${clamped.toFixed(2)}`;

    const widthPercent = Math.abs(clamped) * 50;

    if (clamped >= 0) {
      fillElem.style.left = '50%';
      fillElem.style.width = `${widthPercent}%`;
      fillElem.style.backgroundColor = '#10b981'; // Positive emerald
    } else {
      fillElem.style.left = `${50 - widthPercent}%`;
      fillElem.style.width = `${widthPercent}%`;
      fillElem.style.backgroundColor = '#ef4444'; // Negative crimson
    }
  }

  _updateProgressBar(fillElem, valElem, value) {
    if (!fillElem || !valElem) return;

    const clamped = Math.max(0.0, Math.min(1.0, value));
    valElem.textContent = `${Math.round(clamped * 100)}%`;
    fillElem.style.width = `${clamped * 100}%`;
  }

  _setupDrawerControls() {
    this.toggleBtn = document.getElementById('toggle-diagnostics-btn');
    this.closeBtn = document.getElementById('close-diagnostics-btn');
    this.doneBtn = document.getElementById('done-diagnostics-btn');
    this.backdrop = document.getElementById('diagnostics-backdrop');

    if (this.toggleBtn) {
      this.toggleBtn.addEventListener('click', () => this.toggleDrawer());
    }
    if (this.closeBtn) {
      this.closeBtn.addEventListener('click', () => this.closeDrawer());
    }
    if (this.doneBtn) {
      this.doneBtn.addEventListener('click', () => this.closeDrawer());
    }
    if (this.backdrop) {
      this.backdrop.addEventListener('click', () => this.closeDrawer());
    }
    if (this.modal) {
      this.modal.addEventListener('click', (e) => {
        if (e.target === this.modal) this.closeDrawer();
      });
    }

    // Shortcut: Ctrl+Shift+D or Cmd+Shift+D toggles diagnostics; Escape closes if open
    window.addEventListener('keydown', (e) => {
      if ((e.ctrlKey || e.metaKey) && e.shiftKey && (e.key === 'D' || e.key === 'd')) {
        e.preventDefault();
        this.toggleDrawer();
      } else if (e.key === 'Escape' && this.isDrawerOpen()) {
        this.closeDrawer();
      }
    });
  }

  isDrawerOpen() {
    const isModalOpen = this.modal && this.modal.classList.contains('open');
    const isPaneOpen = this.debugPane && this.debugPane.classList.contains('open');
    return Boolean(isModalOpen || isPaneOpen);
  }

  openDrawer() {
    if (this.modal) {
      this.modal.classList.add('open');
      this.modal.classList.add('active');
    }
    if (this.debugPane) {
      this.debugPane.classList.add('open');
      this.debugPane.classList.add('active');
    }
    if (this.backdrop) {
      this.backdrop.classList.add('open');
      this.backdrop.classList.add('active');
    }
    if (this.toggleBtn) this.toggleBtn.classList.add('active');
    this.pollOnce();
    this.fetchHardwareProfile();
  }

  closeDrawer() {
    if (this.modal) {
      this.modal.classList.remove('open');
      this.modal.classList.remove('active');
    }
    if (this.debugPane) {
      this.debugPane.classList.remove('open');
      this.debugPane.classList.remove('active');
    }
    if (this.backdrop) {
      this.backdrop.classList.remove('open');
      this.backdrop.classList.remove('active');
    }
    if (this.toggleBtn) this.toggleBtn.classList.remove('active');
  }

  toggleDrawer() {
    if (this.isDrawerOpen()) {
      this.closeDrawer();
    } else {
      this.openDrawer();
    }
  }

  showStaleIndicator(isStale) {
    if (this.debugPane) {
      if (isStale) {
        this.debugPane.classList.add('stale-overlay');
      } else {
        this.debugPane.classList.remove('stale-overlay');
      }
    }
    const dot = document.getElementById('diagnostics-status-dot');
    const label = document.getElementById('diagnostics-status-label');
    if (dot) {
      dot.className = isStale ? 'runtime-dot stale' : 'runtime-dot live';
    }
    if (label) {
      label.textContent = isStale ? '⚠ STALE' : '● LIVE';
      label.className = isStale ? 'diagnostics-status-label stale' : 'diagnostics-status-label live';
    }
  }
}

// Instantiate on DOM ready if document exists
if (typeof document !== 'undefined') {
  document.addEventListener('DOMContentLoaded', () => {
    window.emotionDebugPanel = new EmotionDebugPanel();
  });
}

if (typeof window !== 'undefined') {
  window.EmotionDebugPanel = EmotionDebugPanel;
}

if (typeof module !== 'undefined' && module.exports) {
  module.exports = { EmotionDebugPanel };
}

