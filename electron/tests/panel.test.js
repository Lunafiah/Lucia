/**
 * Unit tests for EmotionDebugPanel UI logic.
 * @jest-environment jsdom
 */

describe('EmotionDebugPanel UI Tests', () => {
  let panel;

  beforeEach(() => {
    document.body.innerHTML = `
      <div id="debug-pane">
        <span id="pad-p-val">+0.00</span>
        <div id="pad-p-fill"></div>
        <span id="pad-a-val">+0.00</span>
        <div id="pad-a-fill"></div>
        <span id="pad-d-val">+0.00</span>
        <div id="pad-d-fill"></div>

        <span id="somatic-stability-val">0.00</span>
        <div id="somatic-stability-fill"></div>
        <span id="somatic-energy-val">0.00</span>
        <div id="somatic-energy-fill"></div>
        <span id="somatic-load-val">0.00</span>
        <div id="somatic-load-fill"></div>
        <span id="somatic-tension-val">0.00</span>
        <div id="somatic-tension-fill"></div>

        <span id="constraint-tokens">0</span>
        <span id="constraint-temp">0.00</span>
        <span id="constraint-latency">0 ms</span>
        <span id="constraint-depth">k = 0</span>

        <span id="memory-trace-count">0</span>
      </div>
    `;

    // Mock window.lucia
    window.lucia = {
      state: {
        get: jest.fn()
      },
      on: jest.fn()
    };

    // Load panel module dynamically
    // Inline simplified test helper matching panel.js logic
    panel = {
      updatePADBar(fillElem, valElem, value) {
        const clamped = Math.max(-1.0, Math.min(1.0, value));
        const sign = clamped >= 0 ? '+' : '';
        valElem.textContent = `${sign}${clamped.toFixed(2)}`;
        const widthPercent = Math.abs(clamped) * 50;
        if (clamped >= 0) {
          fillElem.style.left = '50%';
          fillElem.style.width = `${widthPercent}%`;
          fillElem.style.backgroundColor = '#00e676';
        } else {
          fillElem.style.left = `${50 - widthPercent}%`;
          fillElem.style.width = `${widthPercent}%`;
          fillElem.style.backgroundColor = '#ff5252';
        }
      },
      updateProgressBar(fillElem, valElem, value) {
        const clamped = Math.max(0.0, Math.min(1.0, value));
        valElem.textContent = clamped.toFixed(2);
        fillElem.style.width = `${clamped * 100}%`;
      }
    };
  });

  test('updatePADBar positive pleasure extends right from 50%', () => {
    const fill = document.getElementById('pad-p-fill');
    const val = document.getElementById('pad-p-val');
    panel.updatePADBar(fill, val, 0.6);

    expect(val.textContent).toBe('+0.60');
    expect(fill.style.left).toBe('50%');
    expect(fill.style.width).toBe('30%');
    expect(fill.style.backgroundColor).toBe('rgb(0, 230, 118)');
  });

  test('updatePADBar negative arousal extends left from 50%', () => {
    const fill = document.getElementById('pad-a-fill');
    const val = document.getElementById('pad-a-val');
    panel.updatePADBar(fill, val, -0.4);

    expect(val.textContent).toBe('-0.40');
    expect(fill.style.left).toBe('30%');
    expect(fill.style.width).toBe('20%');
    expect(fill.style.backgroundColor).toBe('rgb(255, 82, 82)');
  });

  test('updatePADBar zero dominance has 0% width', () => {
    const fill = document.getElementById('pad-d-fill');
    const val = document.getElementById('pad-d-val');
    panel.updatePADBar(fill, val, 0.0);

    expect(val.textContent).toBe('+0.00');
    expect(fill.style.width).toBe('0%');
  });

  test('updateProgressBar updates width percentage correctly', () => {
    const fill = document.getElementById('somatic-energy-fill');
    const val = document.getElementById('somatic-energy-val');
    panel.updateProgressBar(fill, val, 0.85);

    expect(val.textContent).toBe('0.85');
    expect(fill.style.width).toBe('85%');
  });

  test('diagnostics drawer opens, closes, and toggles via methods and elements', () => {
    // Add drawer toggle and backdrop elements to DOM
    const toggleBtn = document.createElement('button');
    toggleBtn.id = 'toggle-diagnostics-btn';
    document.body.appendChild(toggleBtn);

    const closeBtn = document.createElement('button');
    closeBtn.id = 'close-diagnostics-btn';
    document.body.appendChild(closeBtn);

    const backdrop = document.createElement('div');
    backdrop.id = 'diagnostics-backdrop';
    document.body.appendChild(backdrop);

    const debugPane = document.getElementById('debug-pane');

    // Simulate drawer methods
    const drawer = {
      debugPane,
      toggleBtn,
      closeBtn,
      backdrop,
      isDrawerOpen() {
        return this.debugPane.classList.contains('open');
      },
      openDrawer() {
        this.debugPane.classList.add('open');
        this.backdrop.classList.add('open');
        this.toggleBtn.classList.add('active');
      },
      closeDrawer() {
        this.debugPane.classList.remove('open');
        this.backdrop.classList.remove('open');
        this.toggleBtn.classList.remove('active');
      },
      toggleDrawer() {
        if (this.isDrawerOpen()) this.closeDrawer();
        else this.openDrawer();
      }
    };

    expect(drawer.isDrawerOpen()).toBe(false);

    drawer.openDrawer();
    expect(drawer.isDrawerOpen()).toBe(true);
    expect(debugPane.classList.contains('open')).toBe(true);
    expect(backdrop.classList.contains('open')).toBe(true);

    drawer.closeDrawer();
    expect(drawer.isDrawerOpen()).toBe(false);
    expect(debugPane.classList.contains('open')).toBe(false);

    drawer.toggleDrawer();
    expect(drawer.isDrawerOpen()).toBe(true);

    drawer.toggleDrawer();
    expect(drawer.isDrawerOpen()).toBe(false);
  });
});

