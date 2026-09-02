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

    // Constraints elements
    this.constraintTokens = document.getElementById('constraint-tokens');
    this.constraintTemp = document.getElementById('constraint-temp');
    this.constraintLatency = document.getElementById('constraint-latency');
    this.constraintDepth = document.getElementById('constraint-depth');

    // Memory elements
    this.memoryTraceCount = document.getElementById('memory-trace-count');

    this._setupBackendListeners();
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
      this.showStaleIndicator(false);
    } catch (err) {
      // Show subtle stale indicator without wiping out existing values
      this.showStaleIndicator(true);
    }
  }

  renderSnapshot(snap) {
    if (!snap) return;

    // 1. PAD Bars
    if (snap.pad) {
      this._updatePADBar(this.pFill, this.pVal, snap.pad.pleasure);
      this._updatePADBar(this.aFill, this.aVal, snap.pad.arousal);
      this._updatePADBar(this.dFill, this.dVal, snap.pad.dominance);
    }

    // 2. Somatic Markers
    if (snap.somatic) {
      this._updateProgressBar(this.stabilityFill, this.stabilityVal, snap.somatic.stability);
      this._updateProgressBar(this.energyFill, this.energyVal, snap.somatic.energy);
      this._updateProgressBar(this.loadFill, this.loadVal, snap.somatic.cognitive_load);
      this._updateProgressBar(this.tensionFill, this.tensionVal, snap.somatic.tension);
    }

    // 3. Behavioral Constraints
    if (snap.constraints) {
      if (this.constraintTokens) this.constraintTokens.textContent = `${snap.constraints.max_tokens}`;
      if (this.constraintTemp) this.constraintTemp.textContent = snap.constraints.temperature.toFixed(2);
      if (this.constraintLatency) this.constraintLatency.textContent = `${snap.constraints.latency_ms} ms`;
      if (this.constraintDepth) this.constraintDepth.textContent = `k = ${snap.constraints.reasoning_depth}`;
    }

    // 4. Memory Traces
    if (typeof snap.memory_trace_count === 'number' && this.memoryTraceCount) {
      this.memoryTraceCount.textContent = String(snap.memory_trace_count);
    }
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
