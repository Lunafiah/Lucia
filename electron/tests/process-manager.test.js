const { EventEmitter } = require('events');
const { ProcessManager } = require('../main/process-manager');

describe('ProcessManager Unit Tests', () => {
  let mockWin;
  let sentEvents;

  beforeEach(() => {
    sentEvents = [];
    mockWin = {
      isDestroyed: () => false,
      webContents: {
        send: (channel, payload) => {
          sentEvents.push({ channel, payload });
        }
      }
    };
  });

  test('dispatches backend:ready when stdout emits ready token', async () => {
    const pm = new ProcessManager({ port: 8765 }, () => mockWin);

    // Mock child process
    const mockChild = new EventEmitter();
    mockChild.stdout = new EventEmitter();
    mockChild.stderr = new EventEmitter();
    mockChild.pid = 12345;

    pm._getPythonPath = () => 'python.exe';
    pm.start = function() {
      this.process = mockChild;
      mockChild.stdout.on('data', (data) => {
        if (data.toString().includes('LUCIA_BACKEND_READY')) {
          if (!this._ready) {
            this._ready = true;
            this._dispatch('backend:ready');
          }
        }
      });
      return Promise.resolve();
    };

    await pm.start();
    mockChild.stdout.emit('data', Buffer.from('LUCIA_BACKEND_READY\n'));

    expect(sentEvents.length).toBe(1);
    expect(sentEvents[0].channel).toBe('backend:ready');
  });

  test('dispatches backend:error when stdout emits error token', () => {
    const pm = new ProcessManager({ port: 8765 }, () => mockWin);
    pm._dispatch('backend:error', { code: 'model_path_not_configured' });

    expect(sentEvents.length).toBe(1);
    expect(sentEvents[0].channel).toBe('backend:error');
    expect(sentEvents[0].payload.code).toBe('model_path_not_configured');
  });
});
