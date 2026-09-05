/**
 * Unit tests for CompanionJournal (journal.js) - Phase 7.3 Our Journal & Memories Palace.
 * @jest-environment jsdom
 */

describe('CompanionJournal Sub-Phase 7.3 Tests', () => {
  let CompanionJournal;
  let journal;

  beforeEach(() => {
    // Setup DOM matching index.html
    document.body.innerHTML = `
      <div id="journal-modal" class="journal-modal">
        <button id="close-journal-btn"></button>
        <span id="journal-life-meta"></span>
        <div id="journal-timeline" class="journal-timeline"></div>
        <button id="reset-journal-view-btn"></button>
        <button id="export-journal-btn"></button>
      </div>
      <button id="open-journal-btn"></button>

      <div id="memories-modal" class="journal-modal">
        <button id="close-memories-btn"></button>
        <div class="memories-category-bar">
          <button class="memories-category-pill active" data-category="moments">Moments</button>
          <button class="memories-category-pill" data-category="people">People</button>
          <button class="memories-category-pill" data-category="places">Places</button>
          <button class="memories-category-pill" data-category="enduring">Enduring</button>
        </div>
        <div id="memories-grid" class="memories-grid"></div>
      </div>
      <button id="open-memories-btn"></button>
    `;

    // Mock fetch with tracking
    window.fetch = jest.fn().mockImplementation((url, options = {}) => {
      const method = (options.method || 'GET').toUpperCase();

      if (url.includes('/profile')) {
        return Promise.resolve({
          ok: true,
          json: () => Promise.resolve({
            user_name: 'Luna',
            companion_name: 'Lucia',
            days_count: 5,
            born_date: '2026-09-01T00:00:00.000Z'
          }),
        });
      }

      if (url.includes('/history?limit=100')) {
        return Promise.resolve({
          ok: true,
          json: () => Promise.resolve({
            turns: [
              { speaker: 'user', text: 'It is raining outside tonight.', timestamp: 1725500000000 },
              { speaker: 'companion', text: 'Rain has a way of bringing peace into the room.', timestamp: 1725500005000 }
            ]
          }),
        });
      }

      if (url.includes('/state')) {
        return Promise.resolve({
          ok: true,
          json: () => Promise.resolve({
            memory_trace_count: 42,
            pad: { pleasure: 0.3, arousal: 0.1, dominance: 0.05 }
          }),
        });
      }

      if (url.includes('/history/export')) {
        return Promise.resolve({
          ok: true,
          blob: () => Promise.resolve(new Blob(['# Mock Export'])),
        });
      }

      return Promise.resolve({ ok: true, json: () => Promise.resolve({}) });
    });

    // Mock chatController to test decoupling
    window.chatController = {
      clearScreen: jest.fn(),
    };

    const mod = require('../renderer/journal/journal.js');
    CompanionJournal = mod.CompanionJournal;
    journal = new CompanionJournal();
  });

  afterEach(() => {
    jest.clearAllMocks();
  });

  describe('Modal Open & Close Transitions', () => {
    test('openJournal and closeJournal toggle active class on journal-modal', async () => {
      expect(journal.journalModal.classList.contains('active')).toBe(false);

      await journal.openJournal();
      expect(journal.journalModal.classList.contains('active')).toBe(true);

      journal.closeJournal();
      expect(journal.journalModal.classList.contains('active')).toBe(false);
    });

    test('openMemories and closeMemories toggle active class on memories-modal', async () => {
      expect(journal.memoriesModal.classList.contains('active')).toBe(false);

      await journal.openMemories();
      expect(journal.memoriesModal.classList.contains('active')).toBe(true);

      journal.closeMemories();
      expect(journal.memoriesModal.classList.contains('active')).toBe(false);
    });

    test('Escape key closes open modal', async () => {
      await journal.openJournal();
      expect(journal.journalModal.classList.contains('active')).toBe(true);

      document.dispatchEvent(new KeyboardEvent('keydown', { key: 'Escape' }));
      expect(journal.journalModal.classList.contains('active')).toBe(false);
    });
  });

  describe('Philia Philosophy (Non-Gamified Presentation)', () => {
    test('renders qualitative Life Marker and no gamified percentage meters', async () => {
      await journal.openJournal();

      // Assert life meta banner is populated with days and moments
      expect(journal.journalLifeMeta.textContent).toContain('Day 5 with Lucia');
      expect(journal.journalLifeMeta.textContent).toContain('2 Shared Moments');

      // Assert zero relationship/LSI percentages or XP meters
      expect(document.getElementById('journal-lsi-score')).toBeNull();
      expect(document.querySelector('.xp-bar')).toBeNull();
      expect(document.querySelector('.relationship-meter')).toBeNull();
    });

    test('timeline entries are derived as lightweight presentation cards', async () => {
      await journal.openJournal();

      const cards = journal.journalTimeline.querySelectorAll('.journal-entry-card');
      expect(cards.length).toBeGreaterThan(0);

      const genesisEntry = journal.journalTimeline.querySelector('.timeline-milestone');
      expect(genesisEntry).not.toBeNull();
      expect(journal.journalTimeline.textContent).toContain('Lucia Began Her Life');
    });
  });

  describe('Decoupled Journal View Reset', () => {
    test('resetJournalView resets timeline scroll and DOES NOT call chatController.clearScreen', () => {
      journal.journalTimeline.scrollTop = 250;
      journal.resetJournalView();

      expect(journal.journalTimeline.scrollTop).toBe(0);
      expect(window.chatController.clearScreen).not.toHaveBeenCalled();
    });
  });

  describe('Memories Palace Categories & Honest Scoping', () => {
    test('displays verified conversational moments under moments category', async () => {
      await journal.openMemories();
      journal.selectCategory('moments');

      const cards = journal.memoriesGrid.querySelectorAll('.memory-card');
      expect(cards.length).toBeGreaterThan(0);
      expect(journal.memoriesGrid.textContent).toContain('Rain has a way of bringing peace');
    });

    test('displays verified identity personas under people category', async () => {
      await journal.openMemories();
      journal.selectCategory('people');

      const cards = journal.memoriesGrid.querySelectorAll('.memory-card');
      expect(cards.length).toBe(2);
      expect(journal.memoriesGrid.textContent).toContain('Luna');
      expect(journal.memoriesGrid.textContent).toContain('Lucia');
    });

    test('reports honest limitation with empty state under places category', async () => {
      await journal.openMemories();
      journal.selectCategory('places');

      const emptyState = journal.memoriesGrid.querySelector('.memories-empty-state');
      expect(emptyState).not.toBeNull();
      expect(emptyState.textContent).toContain('No specific places recorded in persistent context');
    });

    test('displays genesis foundational memory and honest progression state under enduring category', async () => {
      await journal.openMemories();
      journal.selectCategory('enduring');

      expect(journal.memoriesGrid.textContent).toContain('Awakening & Genesis');
      expect(journal.memoriesGrid.textContent).toContain('Additional enduring reflections will form naturally');
      // Verify SDM matrix internal telemetry is strictly NOT leaked in companion memory view
      expect(journal.memoriesGrid.textContent).not.toContain('Sparse Distributed Memory');
      expect(journal.memoriesGrid.textContent).not.toContain('Active Affective Traces');
      expect(document.getElementById('memories-trace-summary')).toBeNull();
    });
  });

  describe('Automated Non-Mutation Verification', () => {
    test('opening and filtering Memories performs strictly read-only GET operations with ZERO state mutations', async () => {
      window.fetch.mockClear();

      // Open Memories
      await journal.openMemories();

      // Cycle through all categories
      journal.selectCategory('moments');
      journal.selectCategory('people');
      journal.selectCategory('places');
      journal.selectCategory('enduring');

      // Verify every single fetch call made was a GET request
      const calls = window.fetch.mock.calls;
      expect(calls.length).toBeGreaterThan(0);

      calls.forEach(([url, options]) => {
        const method = (options && options.method ? options.method : 'GET').toUpperCase();
        expect(method).toBe('GET');
      });

      // Verify no mutating HTTP methods (POST, PUT, DELETE, PATCH) were ever called
      const mutatingCalls = calls.filter(([, options]) => {
        if (!options || !options.method) return false;
        const m = options.method.toUpperCase();
        return ['POST', 'PUT', 'DELETE', 'PATCH'].includes(m);
      });
      expect(mutatingCalls.length).toBe(0);

      // Verify memory trace count in controller is strictly unchanged
      expect(journal.cachedTraceCount).toBe(42);
    });
  });
});
