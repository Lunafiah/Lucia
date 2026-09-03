/**
 * Emotion Debug Panel Controller (panel.js)
 * High-frequency 500ms telemetry visualizer for PAD, somatic markers, constraints, and SDM memory traces.
 *
 * Requirements: Phase 3 (7.1–7.8)
 */

class EmotionDebugPanel {
  constructor() {
    this.pollInterval = null;
    this.pollRateMs = 500;
    this.debugPane = document.getElementById('debug-pane');

    // PAD elements
    this.pFill = document.getElementById('pad-p-fill');
    this.aFill = document.getElementById('pad-a-fill');
    this.dFill = document.getElementById('pad-d-fill');
    this.pVal = document.getElementById('pad-p-val');
    this.aVal = document.getElementById('pad-a-val');
    this.dVal = document.getElementById('pad-d-val');

    // Somatic elements
    this.stabilityFill = document.getElementById('somatic-stability-fill');
    this.energyFill = document.getElementById('somatic-energy-fill');
    this.loadFill = document.getElementById('somatic-load-fill');
    this.tensionFill = document.getElementById('somatic-tension-fill');
    this.stabilityVal = document.getElementById('somatic-stability-val');
    this.energyVal = document.getElementById('somatic-energy-val');
    this.loadVal = document.getElementById('somatic-load-val');
    this.tensionVal = document.getElementById('somatic-tension-val');

    // Conversational State elements
    this.convMood = document.getElementById('conv-mood-val');
    this.convVoice = document.getElementById('conv-voice-val');
    this.convLatency = document.getElementById('conv-latency-val');
    this.convDepth = document.getElementById('conv-depth-val');

    // Memory elements
    this.memoryTraceCount = document.getElementById('memory-trace-count');

    // Stability Telemetry elements
    this.lsiVal = document.getElementById('telemetry-lsi-val');
    this.jitterVal = document.getElementById('telemetry-jitter-val');
    this.statusBadge = document.getElementById('stability-status-badge');
    this.tickCounter = 0;

    // Track voice activity via lipSync polling
    this._voiceActivityTimer = null;

    this._setupBackendListeners();
    this._startVoiceActivityMonitor();
  }

  _setupBackendListeners() {
    if (window.lucia && window.lucia.on) {
      window.lucia.on('backend:ready', () => {
        this.startPolling();
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
            if (this.lsiVal) this.lsiVal.textContent = `${Math.round((sData.lsi || 0) * 100)}%`;
            if (this.jitterVal) this.jitterVal.textContent = `${sData.fast_loop_jitter_mean_ms || 0}ms`;
            if (this.statusBadge) {
              const st = (sData.status || 'nominal').toUpperCase();
              this.statusBadge.textContent = st;
              this.statusBadge.style.color = st === 'NOMINAL' ? '#10b981' : (st === 'RECOVERING' ? '#f59e0b' : '#ef4444');
            }
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

    // 1. PAD Bars & Avatar Expression
    if (snap.pad) {
      this._updatePADBar(this.pFill, this.pVal, snap.pad.pleasure);
      this._updatePADBar(this.aFill, this.aVal, snap.pad.arousal);
      this._updatePADBar(this.dFill, this.dVal, snap.pad.dominance);

      if (window.avatarRenderer && typeof window.avatarRenderer.updateEmotion === 'function') {
        window.avatarRenderer.updateEmotion(snap.pad);
      }

      // Update Conversational State — Mood
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

    // 3. Conversational State — Latency & Depth
    if (snap.constraints) {
      if (this.convLatency) this.convLatency.textContent = snap.constraints.latency_ms > 0 ? `${snap.constraints.latency_ms} ms` : '— ms';
      if (this.convDepth) this.convDepth.textContent = `k=${snap.constraints.reasoning_depth || 1}`;
    }

    // 4. Memory Traces
    if (typeof snap.memory_trace_count === 'number' && this.memoryTraceCount) {
      this.memoryTraceCount.textContent = String(snap.memory_trace_count);
    }
  }

  /**
   * Maps PAD triplet to a human-readable mood label.
   * Based on Russell's Circumplex Model of affect.
   */
  _deriveMood(pad) {
    const p = pad.pleasure || 0;
    const a = pad.arousal || 0;
    const d = pad.dominance || 0;
    if (p > 0.4 && a > 0.3) return 'Excited ✨';
    if (p > 0.4 && a < -0.1) return 'Content 😌';
    if (p > 0.15 && Math.abs(a) < 0.2) return 'Calm 🌿';
    if (p < -0.3 && a > 0.3) return 'Anxious 😟';
    if (p < -0.3 && a < -0.1) return 'Sad 😔';
    if (p < -0.2 && d > 0.2) return 'Irritated 😤';
    if (a > 0.5) return 'Alert ⚡';
    if (a < -0.4) return 'Drowsy 😴';
    return 'Neutral 😶';
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
          this.convVoice.textContent = 'Silent';
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
      fillElem.style.backgroundColor = '#00e676'; // Positive green
    } else {
      fillElem.style.left = `${50 - widthPercent}%`;
      fillElem.style.width = `${widthPercent}%`;
      fillElem.style.backgroundColor = '#ff5252'; // Negative red
    }
  }

  _updateProgressBar(fillElem, valElem, value) {
    if (!fillElem || !valElem) return;

    const clamped = Math.max(0.0, Math.min(1.0, value));
    valElem.textContent = clamped.toFixed(2);
    fillElem.style.width = `${clamped * 100}%`;
  }

  showStaleIndicator(isStale) {
    if (this.debugPane) {
      if (isStale) {
        this.debugPane.classList.add('stale-overlay');
      } else {
        this.debugPane.classList.remove('stale-overlay');
      }
    }
  }
}

// Instantiate on DOM ready
document.addEventListener('DOMContentLoaded', () => {
  window.emotionDebugPanel = new EmotionDebugPanel();
});
