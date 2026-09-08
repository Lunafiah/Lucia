/**
 * Lucia Simulation Environment Controller (Phase 8)
 *
 * Provides developers with complete observational and stimulus control over Lucia's
 * cognitive architecture in a fully isolated sandbox without waking her live continuous life
 * or mutating persistent data files (chat_history.json, profile.json).
 *
 * Invariants:
 * 1. Zero Live Contamination: All mutations are trapped in-memory.
 * 2. Sensory Pathway Distinction: Natural language text sensory injection is clearly separated
 *    from developer instrumented 16D vector probes.
 * 3. Canonical Body Preservation: Augments the existing Phase 7 desktop body via Canopy & Console Drawer.
 */

class SimulationController {
  constructor() {
    this.descriptor = null;
    this.isSimulationActive = false;
    this.pollInterval = null;
    this.activeTab = 'inspector';
    this.isPaused = false;
    this.currentSpeed = 1.0;

    // DOM Elements - Canopy
    this.canopy = document.getElementById('simulation-canopy');
    this.clockVal = document.getElementById('sim-clock-val');
    this.clockSpeedTag = document.getElementById('sim-clock-speed');
    this.pauseResumeBtn = document.getElementById('sim-pause-resume-btn');
    this.stepBtn = document.getElementById('sim-step-canopy-btn');
    this.toggleDrawerBtn = document.getElementById('sim-toggle-console-btn');

    // DOM Elements - Drawer
    this.drawer = document.getElementById('simulation-console-drawer');
    this.drawerCloseBtn = document.getElementById('sim-drawer-close-btn');

    // Tabs
    this.tabs = {
      inspector: document.getElementById('sim-tab-inspector'),
      stimulus: document.getElementById('sim-tab-stimulus'),
      timewarp: document.getElementById('sim-tab-timewarp'),
      scenarios: document.getElementById('sim-tab-scenarios')
    };

    this.panels = {
      inspector: document.getElementById('sim-panel-inspector'),
      stimulus: document.getElementById('sim-panel-stimulus'),
      timewarp: document.getElementById('sim-panel-timewarp'),
      scenarios: document.getElementById('sim-panel-scenarios')
    };

    // Tab 1: Inspector Elements
    this.inspectorStateBadge = document.getElementById('sim-state-badge');
    this.inspectorSafetyBadge = document.getElementById('sim-safety-badge');
    this.inspectorStorageBadge = document.getElementById('sim-storage-badge');
    this.meterPleasure = document.getElementById('sim-meter-pleasure');
    this.meterArousal = document.getElementById('sim-meter-arousal');
    this.meterDominance = document.getElementById('sim-meter-dominance');
    this.valPleasure = document.getElementById('sim-val-pleasure');
    this.valArousal = document.getElementById('sim-val-arousal');
    this.valDominance = document.getElementById('sim-val-dominance');
    this.valStability = document.getElementById('sim-val-stability');
    this.valTension = document.getElementById('sim-val-tension');
    this.valEnergy = document.getElementById('sim-val-energy');
    this.valCogLoad = document.getElementById('sim-val-cogload');
    this.valMaxTokens = document.getElementById('sim-val-maxtokens');
    this.valTemperature = document.getElementById('sim-val-temperature');
    this.valLatency = document.getElementById('sim-val-latency');
    this.valDepth = document.getElementById('sim-val-depth');
    this.valTraces = document.getElementById('sim-val-traces');

    // Tab 2: Stimulus Elements
    this.textInput = document.getElementById('sim-stimulus-text-input');
    this.textSourceSelect = document.getElementById('sim-stimulus-source-select');
    this.injectTextBtn = document.getElementById('sim-inject-text-btn');
    this.vectorInput = document.getElementById('sim-vector-input');
    this.injectVectorBtn = document.getElementById('sim-inject-vector-btn');
    this.historyList = document.getElementById('sim-stimulus-history-list');

    // Tab 3: Time Warp Elements
    this.virtualTimeDisplay = document.getElementById('sim-virtual-time-full');
    this.clockStatusDisplay = document.getElementById('sim-clock-status');

    // Tab 4: Scenarios Elements
    this.runAllScenariosBtn = document.getElementById('sim-run-all-scenarios-btn');
    this.scenariosContainer = document.getElementById('sim-scenarios-container');
  }

  async init() {
    if (!window.lucia || !window.lucia.runtime) {
      console.log('[Simulation] window.lucia.runtime not available.');
      return;
    }

    try {
      this.descriptor = await window.lucia.runtime.getDescriptor();
      console.log('[Simulation] Runtime descriptor:', this.descriptor);

      if (this.descriptor && (this.descriptor.mode === 'simulation' || this.descriptor.mode === 'preview')) {
        this.activateSimulationUI();
      } else {
        console.log('[Simulation] Running in Live mode. Simulation UI remains dormant.');
      }
    } catch (err) {
      console.warn('[Simulation] Failed to get runtime descriptor:', err);
    }
  }

  activateSimulationUI() {
    this.isSimulationActive = true;

    // Show canopy
    if (this.canopy) {
      this.canopy.classList.remove('hidden');
    }

    this.bindEvents();
    this.loadPresets();
    this.loadScenariosList();
    this.startSnapshotPolling();

    // Initial fetch
    this.updateSnapshot();
  }

  bindEvents() {
    // Canopy buttons
    if (this.toggleDrawerBtn) {
      this.toggleDrawerBtn.addEventListener('click', () => this.toggleConsoleDrawer());
    }
    if (this.pauseResumeBtn) {
      this.pauseResumeBtn.addEventListener('click', () => this.togglePauseResume());
    }
    if (this.stepBtn) {
      this.stepBtn.addEventListener('click', () => this.stepClock(200));
    }

    // Drawer close
    if (this.drawerCloseBtn) {
      this.drawerCloseBtn.addEventListener('click', () => this.toggleConsoleDrawer(false));
    }

    // Tabs switching
    Object.keys(this.tabs).forEach(tabKey => {
      const btn = this.tabs[tabKey];
      if (btn) {
        btn.addEventListener('click', () => this.switchTab(tabKey));
      }
    });

    // Tab 2: Sensory Text Injection
    if (this.injectTextBtn && this.textInput) {
      this.injectTextBtn.addEventListener('click', async () => {
        const text = this.textInput.value.trim();
        if (!text) return;
        const source = this.textSourceSelect ? this.textSourceSelect.value : 'desktop_ui';
        try {
          this.injectTextBtn.disabled = true;
          await window.lucia.sim.stimulus.injectText(text, source);
          this.textInput.value = '';
          await this.updateSnapshot();
          await this.refreshStimulusHistory();
        } catch (e) {
          console.error('[Simulation] Failed to inject text:', e);
        } finally {
          this.injectTextBtn.disabled = false;
        }
      });
    }

    // Tab 2: Direct Vector Injection (Developer Probe)
    if (this.injectVectorBtn && this.vectorInput) {
      this.injectVectorBtn.addEventListener('click', async () => {
        try {
          const raw = this.vectorInput.value.trim();
          let vector = JSON.parse(raw);
          if (!Array.isArray(vector) || vector.length !== 16) {
            alert('Vector must be a valid JSON array of 16 numbers between -1.0 and 1.0.');
            return;
          }
          this.injectVectorBtn.disabled = true;
          await window.lucia.sim.stimulus.injectVector(vector, 'debug_probe');
          await this.updateSnapshot();
          await this.refreshStimulusHistory();
        } catch (e) {
          alert('Invalid JSON vector: ' + e.message);
        } finally {
          this.injectVectorBtn.disabled = false;
        }
      });
    }

    // Tab 3: Time Warp Buttons
    document.querySelectorAll('.sim-speed-btn').forEach(btn => {
      btn.addEventListener('click', async () => {
        const mult = parseFloat(btn.getAttribute('data-speed') || '1.0');
        await window.lucia.sim.clock.setSpeed(mult);
        this.currentSpeed = mult;
        this.updateClockUI();
      });
    });

    document.querySelectorAll('.sim-step-btn').forEach(btn => {
      btn.addEventListener('click', async () => {
        const delta = parseInt(btn.getAttribute('data-step') || '200', 10);
        await this.stepClock(delta);
      });
    });

    const resetClockBtn = document.getElementById('sim-reset-clock-btn');
    if (resetClockBtn) {
      resetClockBtn.addEventListener('click', async () => {
        await window.lucia.sim.clock.reset(0);
        await this.updateSnapshot();
      });
    }

    // Tab 4: Scenarios Runner
    if (this.runAllScenariosBtn) {
      this.runAllScenariosBtn.addEventListener('click', async () => {
        this.runScenario('all');
      });
    }
  }

  toggleConsoleDrawer(forceOpen) {
    if (!this.drawer) return;
    const shouldOpen = forceOpen !== undefined ? forceOpen : this.drawer.classList.contains('collapsed');
    if (shouldOpen) {
      this.drawer.classList.remove('collapsed');
      this.refreshStimulusHistory();
    } else {
      this.drawer.classList.add('collapsed');
    }
  }

  switchTab(targetTab) {
    this.activeTab = targetTab;
    Object.keys(this.tabs).forEach(k => {
      if (this.tabs[k]) this.tabs[k].classList.toggle('active', k === targetTab);
      if (this.panels[k]) this.panels[k].classList.toggle('active', k === targetTab);
    });

    if (targetTab === 'stimulus') {
      this.refreshStimulusHistory();
    }
  }

  async togglePauseResume() {
    try {
      if (this.isPaused) {
        await window.lucia.sim.clock.resume();
        this.isPaused = false;
      } else {
        await window.lucia.sim.clock.pause();
        this.isPaused = true;
      }
      this.updateClockUI();
    } catch (e) {
      console.warn('[Simulation] Error toggling clock pause/resume:', e);
    }
  }

  async stepClock(deltaMs) {
    try {
      await window.lucia.sim.clock.step(deltaMs);
      await this.updateSnapshot();
    } catch (e) {
      console.warn('[Simulation] Error stepping clock:', e);
    }
  }

  startSnapshotPolling() {
    if (this.pollInterval) clearInterval(this.pollInterval);
    this.pollInterval = setInterval(() => {
      this.updateSnapshot();
    }, 1000);
  }

  async updateSnapshot() {
    try {
      const snap = await window.lucia.runtime.getSnapshot();
      if (!snap || snap.error) return;

      // Update Clock state
      if (snap.clock) {
        this.isPaused = snap.clock.is_paused;
        this.currentSpeed = snap.clock.speed_factor;
        const timeSec = snap.clock.virtual_time_s || 0;
        const hh = String(Math.floor(timeSec / 3600)).padStart(2, '0');
        const mm = String(Math.floor((timeSec % 3600) / 60)).padStart(2, '0');
        const ss = String(Math.floor(timeSec % 60)).padStart(2, '0');
        const ms = String(Math.floor((timeSec % 1) * 1000)).padStart(3, '0');

        if (this.clockVal) this.clockVal.textContent = `${hh}:${mm}:${ss}.${ms}`;
        if (this.virtualTimeDisplay) this.virtualTimeDisplay.textContent = `T + ${timeSec.toFixed(2)}s (${hh}:${mm}:${ss})`;
        if (this.clockSpeedTag) this.clockSpeedTag.textContent = `${this.currentSpeed}x`;
        if (this.clockStatusDisplay) {
          this.clockStatusDisplay.textContent = this.isPaused ? 'PAUSED' : `RUNNING (${this.currentSpeed}x)`;
          this.clockStatusDisplay.style.color = this.isPaused ? '#fbbf24' : '#34d399';
        }
        if (this.pauseResumeBtn) {
          this.pauseResumeBtn.textContent = this.isPaused ? 'Resume' : 'Pause';
        }
      }

      // Update PAD
      if (snap.pad) {
        const p = snap.pad.pleasure !== undefined ? snap.pad.pleasure : 0;
        const a = snap.pad.arousal !== undefined ? snap.pad.arousal : 0;
        const d = snap.pad.dominance !== undefined ? snap.pad.dominance : 0;

        if (this.valPleasure) this.valPleasure.textContent = p.toFixed(3);
        if (this.valArousal) this.valArousal.textContent = a.toFixed(3);
        if (this.valDominance) this.valDominance.textContent = d.toFixed(3);

        // Calculate bar width (-1..1 -> 0%..100%)
        if (this.meterPleasure) this.meterPleasure.style.width = `${((p + 1) / 2) * 100}%`;
        if (this.meterArousal) this.meterArousal.style.width = `${((a + 1) / 2) * 100}%`;
        if (this.meterDominance) this.meterDominance.style.width = `${((d + 1) / 2) * 100}%`;
      }

      // Update Somatics
      if (snap.somatic) {
        if (this.valStability) this.valStability.textContent = (snap.somatic.stability ?? 1.0).toFixed(2);
        if (this.valTension) this.valTension.textContent = (snap.somatic.tension ?? 0.0).toFixed(2);
        if (this.valEnergy) this.valEnergy.textContent = (snap.somatic.energy ?? 1.0).toFixed(2);
        if (this.valCogLoad) this.valCogLoad.textContent = (snap.somatic.cognitive_load ?? 0.0).toFixed(2);
      }

      // Update Constraints
      if (snap.constraints) {
        if (this.valMaxTokens) this.valMaxTokens.textContent = snap.constraints.max_tokens;
        if (this.valTemperature) this.valTemperature.textContent = snap.constraints.temperature?.toFixed(2);
        if (this.valLatency) this.valLatency.textContent = `${snap.constraints.latency_ms}ms`;
        if (this.valDepth) this.valDepth.textContent = `k=${snap.constraints.reasoning_depth}`;
      }

      // Traces count
      if (this.valTraces && snap.memory) {
        this.valTraces.textContent = snap.memory.trace_count || 0;
      }

      // Badges
      if (this.inspectorStateBadge && snap.runtime) {
        this.inspectorStateBadge.textContent = snap.runtime.state || 'SIMULATING';
      }
      if (this.inspectorSafetyBadge) {
        this.inspectorSafetyBadge.textContent = 'LIFECYCLE BLOCKED (ISOLATED)';
        this.inspectorSafetyBadge.style.color = '#34d399';
      }
      if (this.inspectorStorageBadge && snap.storage) {
        this.inspectorStorageBadge.textContent = `${snap.storage.storage_type} (Zero Contamination)`;
        this.inspectorStorageBadge.style.color = '#38bdf8';
      }
    } catch (e) {
      console.warn('[Simulation] Snapshot fetch failed:', e);
    }
  }

  updateClockUI() {
    if (this.pauseResumeBtn) {
      this.pauseResumeBtn.textContent = this.isPaused ? 'Resume' : 'Pause';
    }
    if (this.clockSpeedTag) {
      this.clockSpeedTag.textContent = `${this.currentSpeed}x`;
    }
  }

  async loadPresets() {
    const container = document.getElementById('sim-presets-grid');
    if (!container || !window.lucia.sim.stimulus) return;

    try {
      const res = await window.lucia.sim.stimulus.getPresets();
      const presets = res.presets || {};
      container.innerHTML = '';

      Object.keys(presets).forEach(name => {
        const p = presets[name];
        const btn = document.createElement('button');
        btn.className = 'preset-btn';
        btn.innerHTML = `<strong>${name.replace(/_/g, ' ')}</strong><br><small style="color:#94a3b8">${p.category}</small>`;
        btn.title = `Sensory Text: "${p.sample_text}"`;
        btn.addEventListener('click', async () => {
          btn.style.opacity = '0.5';
          try {
            await window.lucia.sim.stimulus.injectPreset(name, 'sensory_text');
            await this.updateSnapshot();
            await this.refreshStimulusHistory();
          } finally {
            btn.style.opacity = '1.0';
          }
        });
        container.appendChild(btn);
      });
    } catch (e) {
      console.warn('[Simulation] Failed to load stimulus presets:', e);
    }
  }

  async refreshStimulusHistory() {
    if (!this.historyList || !window.lucia.sim.stimulus) return;
    try {
      const res = await window.lucia.sim.stimulus.getHistory(15);
      const items = res.history || [];
      if (items.length === 0) {
        this.historyList.innerHTML = '<div style="color:#64748b; font-size:0.75rem; padding:6px 0;">No stimuli recorded yet.</div>';
        return;
      }

      this.historyList.innerHTML = '';
      items.reverse().forEach(item => {
        const row = document.createElement('div');
        row.style.cssText = 'padding:6px 8px; border-bottom:1px solid rgba(255,255,255,0.06); font-size:0.75rem; display:flex; justify-content:space-between; align-items:center;';

        const left = document.createElement('div');
        const badgeColor = item.pathway === 'sensory_text' ? '#38bdf8' : '#f59e0b';
        left.innerHTML = `
          <span style="color:${badgeColor}; font-weight:600; text-transform:uppercase; font-size:0.68rem; margin-right:6px;">[${item.pathway}]</span>
          <span style="color:#f1f5f9;">${item.text || item.summary || 'Vector Injection'}</span>
          <span style="color:#64748b; font-size:0.68rem; margin-left:6px;">(${item.source})</span>
        `;

        const right = document.createElement('div');
        right.style.fontFamily = 'monospace';
        right.style.color = '#cbd5e1';
        right.textContent = `T+${(item.virtual_timestamp || 0).toFixed(1)}s`;

        row.appendChild(left);
        row.appendChild(right);
        this.historyList.appendChild(row);
      });
    } catch (e) {
      console.warn('[Simulation] Failed to fetch stimulus history:', e);
    }
  }

  async loadScenariosList() {
    if (!this.scenariosContainer || !window.lucia.sim.scenarios) return;
    try {
      const res = await window.lucia.sim.scenarios.list();
      const scenarios = res.scenarios || [];

      this.scenariosContainer.innerHTML = '';
      scenarios.forEach(sc => {
        const item = document.createElement('div');
        item.className = 'scenario-item';
        item.id = `scenario-item-${sc.id}`;

        item.innerHTML = `
          <div class="scenario-info">
            <span class="scenario-name">${sc.name}</span>
            <span class="scenario-desc">${sc.description}</span>
          </div>
          <div style="display: flex; align-items: center; gap: 8px;">
            <span class="scenario-result-badge" id="badge-${sc.id}" style="display:none;"></span>
            <button class="canopy-btn" id="run-btn-${sc.id}">Run</button>
          </div>
        `;

        const runBtn = item.querySelector(`#run-btn-${sc.id}`);
        if (runBtn) {
          runBtn.addEventListener('click', () => this.runScenario(sc.id));
        }

        this.scenariosContainer.appendChild(item);
      });
    } catch (e) {
      console.warn('[Simulation] Failed to list scenarios:', e);
    }
  }

  async runScenario(scenarioId) {
    const badge = document.getElementById(`badge-${scenarioId}`);
    if (this.runAllScenariosBtn) this.runAllScenariosBtn.disabled = true;

    if (badge) {
      badge.style.display = 'inline-block';
      badge.className = 'scenario-result-badge';
      badge.textContent = 'RUNNING...';
      badge.style.background = 'rgba(245, 158, 11, 0.2)';
      badge.style.color = '#fbbf24';
    }

    try {
      const res = await window.lucia.sim.scenarios.run(scenarioId);
      const results = res.results || [];

      results.forEach(r => {
        const b = document.getElementById(`badge-${r.scenario_id}`);
        if (b) {
          b.style.display = 'inline-block';
          b.className = `scenario-result-badge ${r.passed ? 'passed' : 'failed'}`;
          b.textContent = r.passed ? 'PASSED' : 'FAILED';
          b.title = JSON.stringify(r.details || {}, null, 2);
        }
      });

      await this.updateSnapshot();
    } catch (e) {
      console.error('[Simulation] Scenario execution error:', e);
      if (badge) {
        badge.className = 'scenario-result-badge failed';
        badge.textContent = 'ERROR';
      }
    } finally {
      if (this.runAllScenariosBtn) this.runAllScenariosBtn.disabled = false;
    }
  }
}

// Instantiate and initialize when DOM is ready
if (typeof window !== 'undefined') {
  window.addEventListener('DOMContentLoaded', () => {
    const simCtrl = new SimulationController();
    simCtrl.init();
    window.__lucia_simulation = simCtrl;
  });
}

if (typeof module !== 'undefined' && module.exports) {
  module.exports = { SimulationController };
}
