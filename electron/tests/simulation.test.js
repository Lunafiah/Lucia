/**
 * Phase 8: Simulation Environment Desktop UI Test Suite
 *
 * Requirements & Invariants:
 * 1. Canopy is unhidden strictly when runtime descriptor is in simulation or preview mode.
 * 2. In live mode, simulation canopy and drawer remain completely dormant.
 * 3. Text injection routes to window.lucia.sim.stimulus.injectText (sensory pathway).
 * 4. Vector injection routes to window.lucia.sim.stimulus.injectVector (instrumented probe).
 * 5. Time warp buttons step SimClock deterministically.
 * 6. Scenarios runner triggers and renders test badges.
 *
 * @jest-environment jsdom
 */

const { SimulationController } = require('../renderer/simulation/simulation');

describe('SimulationController (Phase 8)', () => {
  let controller;
  let mockLuciaAPI;

  beforeEach(() => {
    // Construct minimal DOM matching index.html simulation elements
    document.body.innerHTML = `
      <aside id="simulation-canopy" class="simulation-canopy hidden">
        <span id="sim-clock-val">00:00:00.000</span>
        <span id="sim-clock-speed">1.0x</span>
        <button id="sim-step-canopy-btn">Step 200ms</button>
        <button id="sim-pause-resume-btn">Pause</button>
        <button id="sim-toggle-console-btn">Dev Console</button>
      </aside>

      <aside id="simulation-console-drawer" class="simulation-console-drawer collapsed">
        <button id="sim-tab-inspector" class="console-tab-btn active">Inspector</button>
        <button id="sim-tab-stimulus" class="console-tab-btn">Stimulus</button>
        <button id="sim-tab-timewarp" class="console-tab-btn">Time Warp</button>
        <button id="sim-tab-scenarios" class="console-tab-btn">Scenarios</button>
        <button id="sim-drawer-close-btn">Close</button>

        <section id="sim-panel-inspector" class="console-panel active">
          <span id="sim-state-badge">SIMULATING</span>
          <span id="sim-safety-badge">BLOCKED</span>
          <span id="sim-storage-badge">In-Memory</span>
          <span id="sim-val-pleasure">+0.250</span>
          <span id="sim-val-arousal">-0.050</span>
          <span id="sim-val-dominance">+0.050</span>
          <div id="sim-meter-pleasure"></div>
          <div id="sim-meter-arousal"></div>
          <div id="sim-meter-dominance"></div>
          <span id="sim-val-stability">1.00</span>
          <span id="sim-val-tension">0.00</span>
          <span id="sim-val-energy">1.00</span>
          <span id="sim-val-cogload">0.00</span>
          <span id="sim-val-maxtokens">150</span>
          <span id="sim-val-temperature">0.75</span>
          <span id="sim-val-latency">0ms</span>
          <span id="sim-val-depth">k=1</span>
          <span id="sim-val-traces">0</span>
        </section>

        <section id="sim-panel-stimulus" class="console-panel">
          <input id="sim-stimulus-text-input" type="text" />
          <select id="sim-stimulus-source-select">
            <option value="desktop_ui">Desktop UI</option>
          </select>
          <button id="sim-inject-text-btn">Inject</button>
          <div id="sim-presets-grid"></div>
          <input id="sim-vector-input" type="text" value="[0.5, 0.2, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0]" />
          <button id="sim-inject-vector-btn">Inject Vector</button>
          <div id="sim-stimulus-history-list"></div>
        </section>

        <section id="sim-panel-timewarp" class="console-panel">
          <div id="sim-virtual-time-full">T + 0.00s</div>
          <div id="sim-clock-status">RUNNING</div>
          <button id="sim-reset-clock-btn">Reset</button>
          <button class="canopy-btn sim-speed-btn" data-speed="2.0">2.0x</button>
          <button class="canopy-btn sim-step-btn" data-step="1000">+1s</button>
        </section>

        <section id="sim-panel-scenarios" class="console-panel">
          <button id="sim-run-all-scenarios-btn">Run All</button>
          <div id="sim-scenarios-container"></div>
        </section>
      </aside>
    `;

    // Mock window.lucia
    mockLuciaAPI = {
      runtime: {
        getDescriptor: jest.fn().mockResolvedValue({
          mode: 'simulation',
          is_live: false,
          is_simulated: true,
          capabilities: ['virtual_clock', 'storage_isolation'],
        }),
        getSnapshot: jest.fn().mockResolvedValue({
          runtime: { state: 'SIMULATING', mode: 'simulation' },
          clock: { virtual_time_s: 12.5, is_paused: false, speed_factor: 1.0 },
          pad: { pleasure: 0.35, arousal: 0.1, dominance: 0.05 },
          somatic: { stability: 0.95, tension: 0.02, energy: 0.98, cognitive_load: 0.15 },
          constraints: { max_tokens: 150, temperature: 0.72, latency_ms: 0, reasoning_depth: 1 },
          memory: { trace_count: 5 },
          storage: { storage_type: 'InMemoryIsolated' },
        }),
      },
      sim: {
        clock: {
          step: jest.fn().mockResolvedValue({ virtual_time_s: 13.5 }),
          pause: jest.fn().mockResolvedValue({ is_paused: true }),
          resume: jest.fn().mockResolvedValue({ is_paused: false }),
          setSpeed: jest.fn().mockResolvedValue({ speed_factor: 2.0 }),
          reset: jest.fn().mockResolvedValue({ virtual_time_s: 0.0 }),
        },
        stimulus: {
          injectText: jest.fn().mockResolvedValue({ status: 'ok', pathway: 'sensory_text' }),
          injectVector: jest.fn().mockResolvedValue({ status: 'ok', pathway: 'debug_vector_probe' }),
          getPresets: jest.fn().mockResolvedValue({ presets: { calm: { category: 'soothing', sample_text: 'Peaceful' } } }),
          injectPreset: jest.fn().mockResolvedValue({ status: 'ok' }),
          getHistory: jest.fn().mockResolvedValue({ history: [] }),
        },
        scenarios: {
          list: jest.fn().mockResolvedValue({
            scenarios: [{ id: 'scenario_a', name: 'Conversational Turn', description: 'Test turn' }],
          }),
          run: jest.fn().mockResolvedValue({
            results: [{ scenario_id: 'scenario_a', passed: true }],
          }),
          getResults: jest.fn().mockResolvedValue({ results: [] }),
        },
      },
    };

    window.lucia = mockLuciaAPI;
  });

  afterEach(() => {
    if (controller && controller.pollInterval) {
      clearInterval(controller.pollInterval);
    }
  });

  test('activates simulation UI and unhides canopy in simulation mode', async () => {
    controller = new SimulationController();
    await controller.init();

    const canopy = document.getElementById('simulation-canopy');
    expect(canopy.classList.contains('hidden')).toBe(false);
    expect(controller.isSimulationActive).toBe(true);
  });

  test('leaves canopy hidden in live mode', async () => {
    mockLuciaAPI.runtime.getDescriptor.mockResolvedValue({
      mode: 'live',
      is_live: true,
      is_simulated: false,
    });

    controller = new SimulationController();
    await controller.init();

    const canopy = document.getElementById('simulation-canopy');
    expect(canopy.classList.contains('hidden')).toBe(true);
    expect(controller.isSimulationActive).toBe(false);
  });

  test('toggles console drawer collapsed state', async () => {
    controller = new SimulationController();
    await controller.init();

    const drawer = document.getElementById('simulation-console-drawer');
    expect(drawer.classList.contains('collapsed')).toBe(true);

    const toggleBtn = document.getElementById('sim-toggle-console-btn');
    toggleBtn.click();
    expect(drawer.classList.contains('collapsed')).toBe(false);

    toggleBtn.click();
    expect(drawer.classList.contains('collapsed')).toBe(true);
  });

  test('switches tabs between inspector and stimulus', async () => {
    controller = new SimulationController();
    await controller.init();

    const stimulusTab = document.getElementById('sim-tab-stimulus');
    stimulusTab.click();

    expect(stimulusTab.classList.contains('active')).toBe(true);
    expect(document.getElementById('sim-panel-stimulus').classList.contains('active')).toBe(true);
    expect(document.getElementById('sim-panel-inspector').classList.contains('active')).toBe(false);
  });

  test('injects natural language sensory text through sensory pathway', async () => {
    controller = new SimulationController();
    await controller.init();

    const input = document.getElementById('sim-stimulus-text-input');
    input.value = 'Hello Lucia in simulation';

    const injectBtn = document.getElementById('sim-inject-text-btn');
    injectBtn.click();

    expect(mockLuciaAPI.sim.stimulus.injectText).toHaveBeenCalledWith(
      'Hello Lucia in simulation',
      'desktop_ui'
    );
  });

  test('injects direct 16D vector probe through developer instrumentation probe', async () => {
    controller = new SimulationController();
    await controller.init();

    const injectVecBtn = document.getElementById('sim-inject-vector-btn');
    injectVecBtn.click();

    expect(mockLuciaAPI.sim.stimulus.injectVector).toHaveBeenCalled();
    const args = mockLuciaAPI.sim.stimulus.injectVector.mock.calls[0];
    expect(args[0]).toHaveLength(16);
    expect(args[1]).toBe('debug_probe');
  });

  test('interacts with SimClock discrete stepping and pause controls', async () => {
    controller = new SimulationController();
    await controller.init();

    const stepBtn = document.getElementById('sim-step-canopy-btn');
    stepBtn.click();
    expect(mockLuciaAPI.sim.clock.step).toHaveBeenCalledWith(200);

    const pauseBtn = document.getElementById('sim-pause-resume-btn');
    await controller.togglePauseResume();
    expect(mockLuciaAPI.sim.clock.pause).toHaveBeenCalled();
  });
});
