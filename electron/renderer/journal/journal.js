/**
 * Companion Journal Controller (journal.js)
 * Displays relationship evolution, interaction statistics, and export controls.
 */

class CompanionJournal {
  constructor() {
    this.modal = document.getElementById('journal-modal');
    this.openBtn = document.getElementById('open-journal-btn');
    this.closeBtn = document.getElementById('close-journal-btn');
    this.exportBtn = document.getElementById('export-history-btn');
    this.clearBtn = document.getElementById('clear-history-btn');

    this.totalTurnsEl = document.getElementById('journal-total-turns');
    this.lsiScoreEl = document.getElementById('journal-lsi-score');
    this.memCountEl = document.getElementById('journal-memory-count');

    this._bindEvents();
  }

  _bindEvents() {
    if (this.openBtn) {
      this.openBtn.addEventListener('click', () => this.open());
    }
    if (this.closeBtn) {
      this.closeBtn.addEventListener('click', () => this.close());
    }
    if (this.modal) {
      this.modal.addEventListener('click', (e) => {
        if (e.target === this.modal) this.close();
      });
    }
    if (this.exportBtn) {
      this.exportBtn.addEventListener('click', () => this.exportHistory());
    }
    if (this.clearBtn) {
      this.clearBtn.addEventListener('click', () => this.clearHistory());
    }
  }

  async open() {
    if (!this.modal) return;
    this.modal.classList.add('active');
    await this.refreshData();
  }

  close() {
    if (!this.modal) return;
    this.modal.classList.remove('active');
  }

  async refreshData() {
    try {
      // 1. Fetch History
      const histRes = await fetch('http://127.0.0.1:8765/history');
      if (histRes.ok) {
        const data = await histRes.json();
        const turnCount = (data.turns || []).length;
        if (this.totalTurnsEl) this.totalTurnsEl.textContent = turnCount;
      }

      // 2. Fetch Stability Telemetry
      const stabRes = await fetch('http://127.0.0.1:8765/telemetry/stability');
      if (stabRes.ok) {
        const sData = await stabRes.json();
        if (this.lsiScoreEl) this.lsiScoreEl.textContent = `${Math.round((sData.lsi || 0) * 100)}%`;
      }

      // 3. Fetch State (Memory Traces)
      const stateRes = await fetch('http://127.0.0.1:8765/state');
      if (stateRes.ok) {
        const stData = await stateRes.json();
        if (this.memCountEl) this.memCountEl.textContent = stData.memory_trace_count || 0;
      }
    } catch (err) {
      console.warn('[journal] Failed to refresh journal telemetry:', err);
    }
  }

  async exportHistory() {
    try {
      const res = await fetch('http://127.0.0.1:8765/history/export');
      if (res.ok) {
        const blob = await res.blob();
        const url = URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = `lucia_conversation_log_${new Date().toISOString().slice(0, 10)}.md`;
        document.body.appendChild(a);
        a.click();
        document.body.removeChild(a);
        URL.revokeObjectURL(url);
      }
    } catch (e) {
      console.error('[journal] Export failed:', e);
    }
  }

  async clearHistory() {
    if (confirm('Are you sure you want to clear your current conversation history? (Lucia long-term affective memories will be preserved)')) {
      try {
        await fetch('http://127.0.0.1:8765/history', { method: 'DELETE' });
        if (window.chatController && typeof window.chatController.clearMessages === 'function') {
          window.chatController.clearMessages();
        }
        this.close();
      } catch (e) {
        console.error('[journal] Clear history failed:', e);
      }
    }
  }
}

document.addEventListener('DOMContentLoaded', () => {
  window.companionJournal = new CompanionJournal();
});

if (typeof module !== 'undefined' && module.exports) {
  module.exports = { CompanionJournal };
}
