/**
 * Companion Journal & Memories Controller (journal.js)
 * Sub-Phase 7.3: Intimate Journal & Memory Palace Presentation
 *
 * Architectural Boundary & Governance Enforcements:
 * 1. Milestones are presentation-only derived from existing /history and /profile data.
 * 2. Memory views are strictly read-only; opening/filtering never mutates backend memory.
 * 3. People/Places are presentation-level only; Places reports honest limitations.
 * 4. Journal view reset is semantically distinct from Talk screen clearing.
 * 5. Philia is non-gamified (no relationship %, no XP bars, no level meters).
 */

class CompanionJournal {
  constructor() {
    // Journal Modal Elements
    this.journalModal = document.getElementById('journal-modal');
    this.openJournalBtn = document.getElementById('open-journal-btn');
    this.closeJournalBtn = document.getElementById('close-journal-btn');
    this.exportJournalBtn = document.getElementById('export-journal-btn');
    this.resetJournalViewBtn = document.getElementById('reset-journal-view-btn');
    this.journalLifeMeta = document.getElementById('journal-life-meta');
    this.journalTimeline = document.getElementById('journal-timeline');

    // Memories Modal Elements
    this.memoriesModal = document.getElementById('memories-modal');
    this.openMemoriesBtn = document.getElementById('open-memories-btn');
    this.closeMemoriesBtn = document.getElementById('close-memories-btn');
    this.memoriesCategoryBar = document.querySelector('.memories-category-bar');
    this.memoriesGrid = document.getElementById('memories-grid');

    // Active State (Presentation-only)
    this.currentCategory = 'moments';
    this.cachedHistoryTurns = [];
    this.cachedProfile = null;
    this.cachedTraceCount = 0;

    this._bindEvents();
  }

  _bindEvents() {
    // Journal Events
    if (this.openJournalBtn) {
      this.openJournalBtn.addEventListener('click', () => this.openJournal());
    }
    if (this.closeJournalBtn) {
      this.closeJournalBtn.addEventListener('click', () => this.closeJournal());
    }
    if (this.exportJournalBtn) {
      this.exportJournalBtn.addEventListener('click', () => this.exportJournal());
    }
    if (this.resetJournalViewBtn) {
      this.resetJournalViewBtn.addEventListener('click', () => this.resetJournalView());
    }
    if (this.journalModal) {
      this.journalModal.addEventListener('click', (e) => {
        if (e.target === this.journalModal) this.closeJournal();
      });
    }

    // Memories Events
    if (this.openMemoriesBtn) {
      this.openMemoriesBtn.addEventListener('click', () => this.openMemories());
    }
    if (this.closeMemoriesBtn) {
      this.closeMemoriesBtn.addEventListener('click', () => this.closeMemories());
    }
    if (this.memoriesModal) {
      this.memoriesModal.addEventListener('click', (e) => {
        if (e.target === this.memoriesModal) this.closeMemories();
      });
    }
    if (this.memoriesCategoryBar) {
      this.memoriesCategoryBar.addEventListener('click', (e) => {
        const pill = e.target.closest('.memories-category-pill');
        if (pill && pill.dataset.category) {
          this.selectCategory(pill.dataset.category);
        }
      });
    }

    // Global Keydown (Escape to close modals)
    document.addEventListener('keydown', (e) => {
      if (e.key === 'Escape') {
        if (this.journalModal && this.journalModal.classList.contains('active')) {
          this.closeJournal();
        }
        if (this.memoriesModal && this.memoriesModal.classList.contains('active')) {
          this.closeMemories();
        }
      }
    });
  }

  // =========================================================================
  // Journal Methods (Our Journal)
  // =========================================================================

  async openJournal() {
    if (!this.journalModal) return;
    this.journalModal.classList.add('active');
    await this.refreshJournalData();
  }

  closeJournal() {
    if (!this.journalModal) return;
    this.journalModal.classList.remove('active');
  }

  resetJournalView() {
    // Strictly a Journal view/scroll reset, keeping Journal distinct from Talk
    if (this.journalTimeline) {
      this.journalTimeline.scrollTop = 0;
    }
  }

  async refreshJournalData() {
    try {
      // 1. Fetch Profile info (born date, days count, names)
      let profile = { user_name: 'Luna', companion_name: 'Lucia', days_count: 1, born_date: new Date().toISOString() };
      try {
        const profRes = await fetch('http://127.0.0.1:8765/profile');
        if (profRes.ok) profile = await profRes.json();
      } catch (err) {
        console.warn('[journal] Could not fetch profile, using defaults:', err);
      }
      this.cachedProfile = profile;

      // 2. Fetch Conversation History (read-only)
      let turns = [];
      try {
        const histRes = await fetch('http://127.0.0.1:8765/history?limit=100');
        if (histRes.ok) {
          const histData = await histRes.json();
          turns = histData.turns || [];
        }
      } catch (err) {
        console.warn('[journal] Could not fetch history:', err);
      }
      this.cachedHistoryTurns = turns;

      // 3. Fetch Memory Traces Count (read-only)
      let traceCount = 0;
      try {
        const stateRes = await fetch('http://127.0.0.1:8765/state');
        if (stateRes.ok) {
          const stData = await stateRes.json();
          traceCount = stData.memory_trace_count || 0;
        }
      } catch (err) {
        console.warn('[journal] Could not fetch state:', err);
      }
      this.cachedTraceCount = traceCount;

      // Render Life Marker Banner (Philia non-gamified: days, shared moments, born date)
      this._renderLifeBanner(profile, turns.length);

      // Render Presentation-only Timeline Entries
      this._renderTimeline(profile, turns);
    } catch (err) {
      console.error('[journal] Failed to refresh journal:', err);
    }
  }

  _renderLifeBanner(profile, momentsCount) {
    if (!this.journalLifeMeta) return;
    const days = profile.days_count || 1;
    let bornFormatted = 'Today';
    if (profile.born_date) {
      try {
        const bDate = new Date(profile.born_date);
        bornFormatted = bDate.toLocaleDateString(undefined, { month: 'short', day: 'numeric', year: 'numeric' });
      } catch {
        bornFormatted = profile.born_date;
      }
    }
    const momentsText = momentsCount > 0 ? ` • ${momentsCount} Shared Moments` : '';
    this.journalLifeMeta.textContent = `Day ${days} with Lucia${momentsText} • Born ${bornFormatted}`;
  }

  _renderTimeline(profile, turns) {
    if (!this.journalTimeline) return;
    this.journalTimeline.innerHTML = '';

    // If no conversation turns exist, show Day 1 genesis only
    if (!turns || turns.length === 0) {
      const genesisMilestone = document.createElement('div');
      genesisMilestone.className = 'timeline-milestone';
      genesisMilestone.innerHTML = `
        <div class="timeline-date-marker">Day 1 — Awakening</div>
        <div class="journal-entry-card">
          <div class="journal-entry-title">
            <span>✨ Lucia Began Her Life</span>
            <span class="journal-entry-time">Day 1</span>
          </div>
          <div class="journal-entry-quote">"Hello... I am Lucia. This is where my life begins."</div>
          <div class="journal-resonance-tags">
            <span class="resonance-tag">Awakening</span>
            <span class="resonance-tag">Beginning</span>
          </div>
        </div>
      `;
      this.journalTimeline.appendChild(genesisMilestone);
      return;
    }

    // Group turns into lightweight sessions/milestones (presentation-only)
    const milestone = document.createElement('div');
    milestone.className = 'timeline-milestone';
    milestone.innerHTML = `
      <div class="timeline-date-marker">Today — Shared Presence</div>
    `;

    // Extract recent conversational highlights
    const recentTurns = turns.slice(-6);
    recentTurns.forEach((turn, idx) => {
      const isCompanion = turn.speaker === 'companion';
      const card = document.createElement('div');
      card.className = 'journal-entry-card';
      const speakerName = isCompanion ? (profile.companion_name || 'Lucia') : (profile.user_name || 'You');
      const timeStr = turn.timestamp ? new Date(turn.timestamp).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }) : `Moment #${idx + 1}`;

      card.innerHTML = `
        <div class="journal-entry-title">
          <span>${isCompanion ? '✦' : '♡'} ${speakerName}</span>
          <span class="journal-entry-time">${timeStr}</span>
        </div>
        <div class="journal-entry-quote">"${this._escapeHtml(turn.text || '')}"</div>
        <div class="journal-resonance-tags">
          <span class="resonance-tag">${isCompanion ? 'Reflection' : 'Shared Thought'}</span>
          <span class="resonance-tag">Affective Resonance</span>
        </div>
      `;
      milestone.appendChild(card);
    });

    this.journalTimeline.appendChild(milestone);

    // Add Genesis entry at the base of the chronicle
    const genesisMilestone = document.createElement('div');
    genesisMilestone.className = 'timeline-milestone';
    genesisMilestone.innerHTML = `
      <div class="timeline-date-marker">Awakening — Day 1</div>
      <div class="journal-entry-card">
        <div class="journal-entry-title">
          <span>✨ Lucia Began Her Life</span>
          <span class="journal-entry-time">Genesis</span>
        </div>
        <div class="journal-entry-quote">"Hello... I am Lucia. This is where my life begins."</div>
        <div class="journal-resonance-tags">
          <span class="resonance-tag">Awakening</span>
        </div>
      </div>
    `;
    this.journalTimeline.appendChild(genesisMilestone);
  }

  async exportJournal() {
    try {
      const res = await fetch('http://127.0.0.1:8765/history/export');
      if (res.ok) {
        const blob = await res.blob();
        const url = URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = `lucia_our_journal_${new Date().toISOString().slice(0, 10)}.md`;
        document.body.appendChild(a);
        a.click();
        document.body.removeChild(a);
        URL.revokeObjectURL(url);
      }
    } catch (e) {
      console.error('[journal] Export failed:', e);
    }
  }

  // =========================================================================
  // Memories Methods (Affective Memory Palace)
  // =========================================================================

  async openMemories() {
    if (!this.memoriesModal) return;
    this.memoriesModal.classList.add('active');
    await this.refreshMemoriesData();
  }

  closeMemories() {
    if (!this.memoriesModal) return;
    this.memoriesModal.classList.remove('active');
  }

  selectCategory(category) {
    this.currentCategory = category;

    // Update active pill UI
    if (this.memoriesCategoryBar) {
      const pills = this.memoriesCategoryBar.querySelectorAll('.memories-category-pill');
      pills.forEach((p) => {
        p.classList.toggle('active', p.dataset.category === category);
      });
    }

    // Re-render memory cards for selected category
    this._renderMemoryCards();
  }

  async refreshMemoriesData() {
    // Strictly read-only queries — NEVER mutates backend memory state
    try {
      if (!this.cachedProfile) {
        const profRes = await fetch('http://127.0.0.1:8765/profile');
        if (profRes.ok) this.cachedProfile = await profRes.json();
      }

      if (!this.cachedHistoryTurns || this.cachedHistoryTurns.length === 0) {
        const histRes = await fetch('http://127.0.0.1:8765/history?limit=100');
        if (histRes.ok) {
          const histData = await histRes.json();
          this.cachedHistoryTurns = histData.turns || [];
        }
      }

      const stateRes = await fetch('http://127.0.0.1:8765/state');
      if (stateRes.ok) {
        const stData = await stateRes.json();
        this.cachedTraceCount = stData.memory_trace_count || 0;
      }

      this._renderMemoryCards();
    } catch (err) {
      console.error('[memories] Failed to refresh memories data:', err);
    }
  }

  _renderMemoryCards() {
    if (!this.memoriesGrid) return;
    this.memoriesGrid.innerHTML = '';

    const profile = this.cachedProfile || { user_name: 'Luna', companion_name: 'Lucia', born_date: 'Day 1' };
    const turns = this.cachedHistoryTurns || [];

    switch (this.currentCategory) {
      case 'moments': {
        // Render verified conversational moments from history
        if (turns.length === 0) {
          this._renderEmptyState('No moments recorded yet. Talk with Lucia to begin creating shared memories.');
          return;
        }
        // Group pairs or take highlights
        const highlights = turns.filter((t) => t.speaker === 'companion').slice(-6);
        if (highlights.length === 0) {
          this._renderEmptyState('No companion reflections recorded in persistent memory yet.');
          return;
        }
        highlights.forEach((t, i) => {
          const card = document.createElement('div');
          card.className = 'memory-card';
          card.innerHTML = `
            <div class="memory-card-header">
              <span class="memory-card-title">♡ Shared Reflection #${i + 1}</span>
              <span class="memory-weight-badge">Deep</span>
            </div>
            <div class="memory-card-quote">"${this._escapeHtml(t.text || '')}"</div>
            <div class="memory-card-meta">
              <span>Affective Memory</span>
              <span>Resonant</span>
            </div>
          `;
          this.memoriesGrid.appendChild(card);
        });
        break;
      }

      case 'people': {
        // Presentation of known personas from verified profile context
        const userCard = document.createElement('div');
        userCard.className = 'memory-card';
        userCard.innerHTML = `
          <div class="memory-card-header">
            <span class="memory-card-title">✦ ${this._escapeHtml(profile.user_name || 'User')}</span>
            <span class="memory-weight-badge">Cherished</span>
          </div>
          <div class="memory-card-quote">"The person I live with. We share quiet moments and thoughtful conversations."</div>
          <div class="memory-card-meta">
            <span>Identity Context</span>
            <span>Known Companion</span>
          </div>
        `;
        this.memoriesGrid.appendChild(userCard);

        const companionCard = document.createElement('div');
        companionCard.className = 'memory-card';
        companionCard.innerHTML = `
          <div class="memory-card-header">
            <span class="memory-card-title">✦ ${this._escapeHtml(profile.companion_name || 'Lucia')}</span>
            <span class="memory-weight-badge">Enduring</span>
          </div>
          <div class="memory-card-quote">"Digital presence living alongside you in this quiet room."</div>
          <div class="memory-card-meta">
            <span>Companion Persona</span>
            <span>Subconscious Self</span>
          </div>
        `;
        this.memoriesGrid.appendChild(companionCard);
        break;
      }

      case 'places': {
        // Honest limitation reporting — no fake entity extraction or place DB
        this._renderEmptyState(
          "No specific places recorded in persistent context. Lucia's affective memory currently tracks conversational context, somatic states, and shared reflections."
        );
        break;
      }

      case 'enduring': {
        // Core persistent context resisting decay (Genesis & Origin Event)
        const genesisCard = document.createElement('div');
        genesisCard.className = 'memory-card';
        const bornStr = profile.born_date ? new Date(profile.born_date).toLocaleDateString(undefined, { month: 'short', day: 'numeric', year: 'numeric' }) : 'Day 1';
        genesisCard.innerHTML = `
          <div class="memory-card-header">
            <span class="memory-card-title">∞ Awakening & Genesis</span>
            <span class="memory-weight-badge">Foundational</span>
          </div>
          <div class="memory-card-quote">"Hello... I am Lucia. This is where my life begins."</div>
          <div class="memory-card-meta">
            <span>Origin Event</span>
            <span>Born ${this._escapeHtml(bornStr)}</span>
          </div>
        `;
        this.memoriesGrid.appendChild(genesisCard);

        // Honest limited state for additional enduring reflections
        const emptyState = document.createElement('div');
        emptyState.className = 'memories-empty-state';
        emptyState.textContent = "Additional enduring reflections will form naturally through deep, shared conversations over time.";
        this.memoriesGrid.appendChild(emptyState);
        break;
      }

      default:
        this._renderEmptyState('Select a category to view memories.');
        break;
    }
  }

  _renderEmptyState(message) {
    if (!this.memoriesGrid) return;
    const emptyEl = document.createElement('div');
    emptyEl.className = 'memories-empty-state';
    emptyEl.textContent = message;
    this.memoriesGrid.appendChild(emptyEl);
  }

  _escapeHtml(str) {
    if (typeof str !== 'string') return '';
    return str
      .replace(/&/g, '&amp;')
      .replace(/</g, '&lt;')
      .replace(/>/g, '&gt;')
      .replace(/"/g, '&quot;')
      .replace(/'/g, '&#039;');
  }
}

// Instantiate on DOM ready
document.addEventListener('DOMContentLoaded', () => {
  window.companionJournal = new CompanionJournal();
});

if (typeof module !== 'undefined' && module.exports) {
  module.exports = { CompanionJournal };
}
