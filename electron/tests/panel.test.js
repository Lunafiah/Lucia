/**
 * Phase 7.6: Dedicated Diagnostics Console Test Suite
 *
 * Requirements & Invariants:
 * 1. Mathematical Attractor Distance (ΔPhilia): Euclidean distance, not relationship score.
 * 2. Russell Circumplex Mapping: Mathematical affective classification, not emotional self-report.
 * 3. VRAM Budget: Profile allocation limit representation.
 * 4. Diagnostics Read-Only Integrity: Zero sliders, inputs, or emotional mutators inside the console.
 * 5. Modal lifecycle: Open, close, toggle, keyboard navigation, and backdrop dismissal.
 * @jest-environment jsdom
 */

const { EmotionDebugPanel } = require('../renderer/debug/panel');

describe('EmotionDebugPanel (Phase 7.6 Diagnostics Console)', () => {
  let panel;

  beforeEach(() => {
    // Setup complete DOM layout matching index.html Phase 7.6 Diagnostics Modal
    document.body.innerHTML = `
      <button id="toggle-diagnostics-btn" class="nav-action-btn"></button>

      <div id="diagnostics-modal" class="journal-modal diagnostics-modal">
        <div id="diagnostics-backdrop" class="diagnostics-backdrop-layer"></div>
        <div id="debug-pane" class="journal-card diagnostics-card">
          <header class="diagnostics-header">
            <button id="close-diagnostics-btn" class="journal-close-btn">&times;</button>
          </header>

          <div class="debug-scroll-content diagnostics-scroll-content">
            <!-- Section 1: Limbic ODE State -->
            <span id="pad-p-val">+0.25</span>
            <div id="pad-p-fill"></div>
            <span id="pad-a-val">-0.05</span>
            <div id="pad-a-fill"></div>
            <span id="pad-d-val">+0.05</span>
            <div id="pad-d-fill"></div>
            <span id="conv-mood-val">Calm / Serene</span>
            <span id="pad-philia-dist">Δ = 0.000</span>

            <!-- Section 2: Homeostatic Markers & Constraints -->
            <span id="somatic-stability-val">100%</span>
            <div id="somatic-stability-fill"></div>
            <span id="somatic-energy-val">100%</span>
            <div id="somatic-energy-fill"></div>
            <span id="somatic-load-val">0%</span>
            <div id="somatic-load-fill"></div>
            <span id="somatic-tension-val">0%</span>
            <div id="somatic-tension-fill"></div>
            <span id="conv-latency-val">+0 ms</span>
            <span id="conv-depth-val">k=1</span>
            <span id="constraint-tokens-val">150</span>
            <span id="constraint-temp-val">0.75</span>

            <!-- Section 3: Sparse Distributed Memory (SDM) -->
            <span id="memory-trace-count">0</span>
            <span id="sdm-capacity-val">1,000</span>
            <span id="sdm-saturation-val">0.0%</span>
            <span id="sdm-decay-val">λ = 0.002 / hr</span>

            <!-- Section 4: Active Inference & LNN -->
            <span id="stability-status-badge" class="telemetry-badge">STABLE</span>
            <span id="telemetry-lsi-val">100%</span>
            <span id="telemetry-jitter-val">0.0 ms</span>
            <span id="telemetry-fe-val">0.0000</span>
            <span id="telemetry-variance-val">0.0000</span>
            <span id="telemetry-recovery-val">0</span>
            <span id="telemetry-uptime-val">0s</span>

            <!-- Section 5: Hardware & Inference Footprint -->
            <span id="hw-tier-val">Auto (CUDA)</span>
            <span id="hw-gpu-layers-val">32 layers</span>
            <span id="hw-vram-val">4,096 MB</span>
            <span id="hw-ctx-val">2,048 tokens</span>
            <span id="hw-cadence-val">200 ms</span>
            <span id="conv-voice-val">Quiet</span>
          </div>

          <footer class="diagnostics-footer">
            <span id="diagnostics-status-dot" class="runtime-dot live"></span>
            <span id="diagnostics-status-label" class="diagnostics-status-label live">● LIVE</span>
            <button id="done-diagnostics-btn" class="journal-btn secondary">Close</button>
          </footer>
        </div>
      </div>
    `;

    // Mock window.lucia API
    window.lucia = {
      state: {
        get: jest.fn().mockResolvedValue({
          pad: { pleasure: 0.25, arousal: -0.05, dominance: 0.05 },
          somatic: { stability: 0.98, energy: 0.85, cognitive_load: 0.12, tension: 0.05 },
          constraints: { latency_ms: 25, reasoning_depth: 2, max_tokens: 200, temperature: 0.7 },
          memory_trace_count: 42
        })
      },
      system: {
        getProfile: jest.fn().mockResolvedValue({
          tier: 'desktop_performance',
          name: 'Desktop Performance (CUDA)',
          n_gpu_layers: 28,
          vram_mb: 8192,
          n_ctx: 4096,
          loop_cadence_ms: 200,
          sdm_capacity: 2000
        })
      },
      on: jest.fn()
    };

    panel = new EmotionDebugPanel();
  });

  afterEach(() => {
    panel.stopPolling();
    jest.clearAllMocks();
  });

  // --------------------------------------------------------------------------
  // Refinement 4: Diagnostics Read-Only Integrity Test
  // --------------------------------------------------------------------------
  test('diagnostics console maintains strict read-only integrity (zero sliders, inputs, or emotional mutators)', () => {
    const debugPane = document.getElementById('debug-pane');
    expect(debugPane).not.toBeNull();

    // 1. Verify NO interactive input elements exist (range, number, text, etc.)
    const inputElements = debugPane.querySelectorAll('input');
    expect(inputElements.length).toBe(0);

    // 2. Verify NO select dropdowns exist
    const selectElements = debugPane.querySelectorAll('select');
    expect(selectElements.length).toBe(0);

    // 3. Verify NO textareas exist
    const textareaElements = debugPane.querySelectorAll('textarea');
    expect(textareaElements.length).toBe(0);

    // 4. Verify NO contenteditable regions exist
    const editableElements = debugPane.querySelectorAll('[contenteditable="true"]');
    expect(editableElements.length).toBe(0);

    // 5. Verify only legitimate dismissal/close buttons exist
    const buttons = debugPane.querySelectorAll('button');
    const buttonIds = Array.from(buttons).map((b) => b.id);
    expect(buttonIds).toEqual(expect.arrayContaining(['close-diagnostics-btn', 'done-diagnostics-btn']));
    expect(buttons.length).toBe(2);
  });

  // --------------------------------------------------------------------------
  // Refinement 1: Mathematical Attractor Distance (Euclidean)
  // --------------------------------------------------------------------------
  test('computePhiliaDistance calculates strict Euclidean distance to attractor, not relationship score', () => {
    // Exactly at resting attractor (P=+0.25, A=-0.05, D=+0.05)
    const distAtRest = panel.computePhiliaDistance(0.25, -0.05, 0.05);
    expect(distAtRest).toBeCloseTo(0.000, 4);

    // Displaced state: P=+0.50 (diff 0.25), A=+0.15 (diff 0.20), D=-0.10 (diff -0.15)
    // Distance = sqrt(0.25^2 + 0.20^2 + (-0.15)^2) = sqrt(0.0625 + 0.04 + 0.0225) = sqrt(0.125) ≈ 0.35355
    const distDisplaced = panel.computePhiliaDistance(0.50, 0.15, -0.10);
    expect(distDisplaced).toBeCloseTo(Math.sqrt(0.125), 4);

    // Verification that renderSnapshot displays formatted Euclidean distance
    panel.renderSnapshot({
      pad: { pleasure: 0.50, arousal: 0.15, dominance: -0.10 }
    });
    const distElem = document.getElementById('pad-philia-dist');
    expect(distElem.textContent).toBe('Δ = 0.354');
  });

  // --------------------------------------------------------------------------
  // Refinement 2: Russell Circumplex Affective Classification (No Self-Report)
  // --------------------------------------------------------------------------
  test('maps PAD coordinates to affective classifications without subjective self-reporting', () => {
    // High Pleasure + High Arousal
    expect(panel._deriveMood({ pleasure: 0.6, arousal: 0.5, dominance: 0.1 })).toBe('Vigorous / High Valence');

    // High Pleasure + Low Arousal
    expect(panel._deriveMood({ pleasure: 0.5, arousal: -0.3, dominance: 0.0 })).toBe('Content / Low Arousal');

    // Mild Pleasure + Neutral Arousal (Philia region)
    expect(panel._deriveMood({ pleasure: 0.25, arousal: -0.05, dominance: 0.05 })).toBe('Calm / Pleasant');

    // Low Pleasure + High Arousal
    expect(panel._deriveMood({ pleasure: -0.5, arousal: 0.4, dominance: 0.0 })).toBe('Tense / High Arousal');

    // Low Pleasure + Low Arousal
    expect(panel._deriveMood({ pleasure: -0.4, arousal: -0.2, dominance: 0.0 })).toBe('Subdued / Low Valence');

    // Low Pleasure + High Dominance
    expect(panel._deriveMood({ pleasure: -0.3, arousal: 0.1, dominance: 0.3 })).toBe('Agitated / High Dominance');

    // Basal / Neutral
    expect(panel._deriveMood({ pleasure: 0.0, arousal: 0.0, dominance: 0.0 })).toBe('Neutral / Basal');

    // Assert that NONE of the outputs contain introspective or conversational self-report patterns
    const testCases = [
      { pleasure: 0.6, arousal: 0.5, dominance: 0.1 },
      { pleasure: -0.5, arousal: 0.4, dominance: 0.0 },
      { pleasure: 0.25, arousal: -0.05, dominance: 0.05 },
      { pleasure: 0.0, arousal: 0.0, dominance: 0.0 }
    ];
    testCases.forEach((pad) => {
      const label = panel._deriveMood(pad);
      expect(label).not.toMatch(/feel/i);
      expect(label).not.toMatch(/lucia/i);
      expect(label).not.toMatch(/i am/i);
    });
  });

  // --------------------------------------------------------------------------
  // Refinement 3: Hardware Profile & VRAM Budget Rendering
  // --------------------------------------------------------------------------
  test('renders hardware profile with explicit VRAM Budget allocation', () => {
    panel.renderHardwareProfile({
      tier: 'desktop_performance',
      name: 'Desktop Performance (CUDA)',
      n_gpu_layers: 28,
      vram_mb: 8192,
      n_ctx: 4096,
      loop_cadence_ms: 200,
      sdm_capacity: 2000
    });

    expect(document.getElementById('hw-tier-val').textContent).toBe('Desktop Performance (CUDA) (DESKTOP_PERFORMANCE)');
    expect(document.getElementById('hw-gpu-layers-val').textContent).toBe('28 layers');
    expect(document.getElementById('hw-vram-val').textContent).toBe('8,192 MB');
    expect(document.getElementById('hw-ctx-val').textContent).toBe('4,096 tokens');
    expect(document.getElementById('hw-cadence-val').textContent).toBe('200 ms');
    expect(document.getElementById('sdm-capacity-val').textContent).toBe('2,000');
  });

  // --------------------------------------------------------------------------
  // PAD Bar & Somatic Progress Bar Updates
  // --------------------------------------------------------------------------
  test('updatePADBar positive pleasure extends right from 50% with emerald fill', () => {
    const fill = document.getElementById('pad-p-fill');
    const val = document.getElementById('pad-p-val');
    panel._updatePADBar(fill, val, 0.6);

    expect(val.textContent).toBe('+0.60');
    expect(fill.style.left).toBe('50%');
    expect(fill.style.width).toBe('30%');
    expect(fill.style.backgroundColor).toBe('rgb(16, 185, 129)');
  });

  test('updatePADBar negative arousal extends left from 50% with crimson fill', () => {
    const fill = document.getElementById('pad-a-fill');
    const val = document.getElementById('pad-a-val');
    panel._updatePADBar(fill, val, -0.4);

    expect(val.textContent).toBe('-0.40');
    expect(fill.style.left).toBe('30%');
    expect(fill.style.width).toBe('20%');
    expect(fill.style.backgroundColor).toBe('rgb(239, 68, 68)');
  });

  test('updateProgressBar updates percentage and track width', () => {
    const fill = document.getElementById('somatic-energy-fill');
    const val = document.getElementById('somatic-energy-val');
    panel._updateProgressBar(fill, val, 0.85);

    expect(val.textContent).toBe('85%');
    expect(fill.style.width).toBe('85%');
  });

  // --------------------------------------------------------------------------
  // Stability Telemetry Snapshot Rendering
  // --------------------------------------------------------------------------
  test('renderStabilitySnapshot populates LSI, jitter, prediction error, and uptime', () => {
    panel.renderStabilitySnapshot({
      lsi: 0.965,
      status: 'nominal',
      fast_loop_jitter_mean_ms: 1.42,
      free_energy_surprise_mean: 0.0384,
      ode_velocity_variance: 0.0012,
      recovery_count: 3,
      uptime_seconds: 3675,
      sdm_saturation_pct: 14.5
    });

    expect(document.getElementById('telemetry-lsi-val').textContent).toBe('97%');
    expect(document.getElementById('telemetry-jitter-val').textContent).toBe('1.4 ms');
    expect(document.getElementById('stability-status-badge').textContent).toBe('NOMINAL');
    expect(document.getElementById('telemetry-fe-val').textContent).toBe('0.0384');
    expect(document.getElementById('telemetry-variance-val').textContent).toBe('0.0012');
    expect(document.getElementById('telemetry-recovery-val').textContent).toBe('3');
    expect(document.getElementById('telemetry-uptime-val').textContent).toBe('1h 1m');
    expect(document.getElementById('sdm-saturation-val').textContent).toBe('14.5%');
  });

  // --------------------------------------------------------------------------
  // Modal Lifecycle & Navigation Tests
  // --------------------------------------------------------------------------
  test('diagnostics modal opens, closes, and toggles via methods, buttons, and keys', () => {
    const modal = document.getElementById('diagnostics-modal');
    const debugPane = document.getElementById('debug-pane');
    const toggleBtn = document.getElementById('toggle-diagnostics-btn');
    const closeBtn = document.getElementById('close-diagnostics-btn');
    const doneBtn = document.getElementById('done-diagnostics-btn');

    expect(panel.isDrawerOpen()).toBe(false);

    // 1. Open modal via openDrawer()
    panel.openDrawer();
    expect(panel.isDrawerOpen()).toBe(true);
    expect(modal.classList.contains('open')).toBe(true);
    expect(debugPane.classList.contains('open')).toBe(true);
    expect(toggleBtn.classList.contains('active')).toBe(true);

    // 2. Close modal via closeBtn
    closeBtn.click();
    expect(panel.isDrawerOpen()).toBe(false);
    expect(modal.classList.contains('open')).toBe(false);
    expect(debugPane.classList.contains('open')).toBe(false);
    expect(toggleBtn.classList.contains('active')).toBe(false);

    // 3. Toggle open via toggleBtn
    toggleBtn.click();
    expect(panel.isDrawerOpen()).toBe(true);

    // 4. Close via doneBtn
    doneBtn.click();
    expect(panel.isDrawerOpen()).toBe(false);

    // 5. Keyboard shortcut: Ctrl+Shift+D toggles
    window.dispatchEvent(new KeyboardEvent('keydown', { key: 'D', ctrlKey: true, shiftKey: true }));
    expect(panel.isDrawerOpen()).toBe(true);

    // 6. Keyboard shortcut: Escape dismisses
    window.dispatchEvent(new KeyboardEvent('keydown', { key: 'Escape' }));
    expect(panel.isDrawerOpen()).toBe(false);
  });

  test('diagnostics modal dismisses upon clicking backdrop layer', () => {
    const backdrop = document.getElementById('diagnostics-backdrop');
    panel.openDrawer();
    expect(panel.isDrawerOpen()).toBe(true);

    backdrop.click();
    expect(panel.isDrawerOpen()).toBe(false);
  });

  test('showStaleIndicator updates status badge, dot, and card overlay', () => {
    const debugPane = document.getElementById('debug-pane');
    const dot = document.getElementById('diagnostics-status-dot');
    const label = document.getElementById('diagnostics-status-label');

    // Initially live
    panel.showStaleIndicator(false);
    expect(debugPane.classList.contains('stale-overlay')).toBe(false);
    expect(dot.classList.contains('live')).toBe(true);
    expect(label.textContent).toBe('● LIVE');

    // Stale state
    panel.showStaleIndicator(true);
    expect(debugPane.classList.contains('stale-overlay')).toBe(true);
    expect(dot.classList.contains('stale')).toBe(true);
    expect(label.textContent).toBe('⚠ STALE');

    // Return to live
    panel.showStaleIndicator(false);
    expect(debugPane.classList.contains('stale-overlay')).toBe(false);
    expect(dot.classList.contains('live')).toBe(true);
    expect(label.textContent).toBe('● LIVE');
  });

  test('retains previous valid telemetry readings when polling fails and marks console stale', async () => {
    // 1. Initial valid render
    panel.renderSnapshot({
      pad: { pleasure: 0.4, arousal: 0.1, dominance: 0.0 },
      somatic: { stability: 0.95, energy: 0.8, cognitive_load: 0.2, tension: 0.1 },
      constraints: { latency_ms: 50, reasoning_depth: 2, max_tokens: 180, temperature: 0.72 },
      memory_trace_count: 15
    });

    expect(document.getElementById('pad-p-val').textContent).toBe('+0.40');
    expect(document.getElementById('somatic-stability-val').textContent).toBe('95%');
    expect(document.getElementById('memory-trace-count').textContent).toBe('15');

    // 2. Mock state.get failure
    window.lucia.state.get.mockRejectedValueOnce(new Error('Backend timeout'));

    await panel.pollOnce();

    // Readings must be preserved (not wiped out to 0 or undefined)
    expect(document.getElementById('pad-p-val').textContent).toBe('+0.40');
    expect(document.getElementById('somatic-stability-val').textContent).toBe('95%');
    expect(document.getElementById('memory-trace-count').textContent).toBe('15');

    // Stale indicator must be active
    expect(document.getElementById('debug-pane').classList.contains('stale-overlay')).toBe(true);
    expect(document.getElementById('diagnostics-status-label').textContent).toBe('⚠ STALE');
  });
});


