# Code Evidence & Verification Trace — F-02-A Persistence Audit

**Audit Scope:** Verbatim source code citations, exact line ranges, and behavioral facts verifying persistence topology, timing, and cross-subsystem coupling in Lucia.  
**Commit Baseline:** `32660ac4e422bdb2ecb9c7b97a4bdc04c805418e`  
**Date:** 2026-10-07  

---

## Evidence Item E-01: EmotionCore Restores Before RelationshipUpdater Is Constructed

### Code Citation
**File:** [`src/core/orchestrator/cognitive_orchestrator.py`](file:///c:/Users/Lunafiah/Desktop/My_project/Lucia/src/core/orchestrator/cognitive_orchestrator.py#L804-L836)
```python
804:     emotion_core = EmotionCore(
805:         config.to_emotion_config(),
806:         storage_path=dynamical_storage_path,
807:     )
808:     homeostatic_engine = HomeostaticEngine(HomeostaticConfig())
809:     active_inference = ActiveInferenceEngine(ActiveInferenceConfig())
810:     affective_memory = AffectiveMemory(config.to_affective_memory_config())
811:     decay_engine = DecayEngine(affective_memory, config.to_decay_config())
812:     ecphory_engine = EcphoryEngine(config.to_ecphory_config())
813:     prompt_assembler = PromptAssembler()
814:     if llm_backend is None:
815:         llm_backend = LLMBackend(config.to_llm_config())
816:     boundary_layer = BoundaryLayer(config.to_boundary_config())
...
832:     if relationship_updater is None:
833:         relationship_updater = RelationshipUpdater(
834:             storage_path=relationship_storage_path
835:         )
836: 
837:     return CognitiveOrchestrator(
```

**File:** [`src/core/emotion/emotion_core.py`](file:///c:/Users/Lunafiah/Desktop/My_project/Lucia/src/core/emotion/emotion_core.py#L200-L219)
```python
200:         self.R_0 = np.array(config.relationship_baseline, dtype=np.float64)
201:         self._R_t = self.R_0.copy()
...
216:         self._storage_path: Optional[Path] = Path(storage_path) if storage_path is not None else None
217:         if self._storage_path is not None and auto_restore:
218:             self.restore_from_checkpoint(self._storage_path)
```

### Fact From Code
1. `EmotionCore` is instantiated at line 804 with `auto_restore=True` (the default).
2. `restore_from_checkpoint()` executes inside `EmotionCore.__init__` (line 218), before line 808 is reached.
3. `RelationshipUpdater` is instantiated 29 lines later, at line 833.
4. During `EmotionCore.restore_from_checkpoint()`, `self._R_t` is strictly initialized to `self.R_0 = [0.0, 0.5, 0.0, 0.5]` (default stranger baseline).

---

## Evidence Item E-02: Downtime Unforced Idle Integration Relaxes Towards Unconditioned Philia Baseline

### Code Citation
**File:** [`src/core/emotion/emotion_core.py`](file:///c:/Users/Lunafiah/Desktop/My_project/Lucia/src/core/emotion/emotion_core.py#L332-L340)
```python
332:         if apply_elapsed_time:
333:             now = time.time() if current_time is None else current_time
334:             elapsed_s = max(0.0, now - snapshot.created_at)
335:             if elapsed_s > 0.0:
336:                 self.integrate_unforced_idle(
337:                     duration_s=elapsed_s,
338:                     dt=self._config.ode_step_size,
339:                     record_trajectory=False,
340:                 )
```

**File:** [`src/core/emotion/emotion_core.py`](file:///c:/Users/Lunafiah/Desktop/My_project/Lucia/src/core/emotion/emotion_core.py#L1047-L1057)
```python
1047:         with self._train_lock:
...
1051:                 R_t = self._R_t.copy()
...
1054:             if self._config.enable_relational_consolidation:
1055:                 delta_r = np.clip(R_t, 0.0, 1.0) - self.R_0
1056:                 s_eff = s_philia + W_rel @ delta_r
1057:                 delta_s = y_s - s_eff
```

### Fact From Code
1. If `snapshot.created_at` represents an offline period of $\Delta t > 0$, `integrate_unforced_idle` runs.
2. At line 1051, `R_t = self._R_t.copy()`. Because `self._R_t` is `self.R_0`, `delta_r = self.R_0 - self.R_0 = [0, 0, 0, 0]`.
3. Consequently, `s_eff = s_philia + W_rel @ 0 = s_philia` bit-exact!
4. The system simulates long-downtime recovery relaxing towards the unconditioned Philia attractor ($s^*_{\text{philia}}$) instead of the relationally conditioned attractor ($s^*_{\text{eff}}(R)$), even when `data/relationship.json` contains a mature bond (e.g., $R = [0.8, 0.9, 0.7, 0.8]$).

---

## Evidence Item E-03: Loaded Relationship State Is Never Synchronized to EmotionCore During Startup

### Code Citation
**File:** [`src/core/orchestrator/cognitive_orchestrator.py`](file:///c:/Users/Lunafiah/Desktop/My_project/Lucia/src/core/orchestrator/cognitive_orchestrator.py#L832-L860)
```python
832:     if relationship_updater is None:
833:         relationship_updater = RelationshipUpdater(
834:             storage_path=relationship_storage_path
835:         )
836: 
837:     return CognitiveOrchestrator(
838:         stimulus_processor=stimulus_processor,
839:         emotion_core=emotion_core,
...
852:         relationship_updater=relationship_updater,
...
859:     )
```

**File:** [`src/core/orchestrator/cognitive_orchestrator.py`](file:///c:/Users/Lunafiah/Desktop/My_project/Lucia/src/core/orchestrator/cognitive_orchestrator.py#L201-L210)
```python
201:         # --- Start background daemons ---
202:         self._emotion_core.start()
203:         self._wait_for_fast_loop()
204: 
205:         if self._decay_engine is not None:
206:             self._decay_engine.start()
207: 
208:         if self._lnn_trainer is not None:
209:             self._lnn_trainer.start()
```

### Fact From Code
1. Neither `build_cognitive_orchestrator` nor `CognitiveOrchestrator.__init__` invokes `self._emotion_core.update_relationship_context(relationship_updater.get_state().to_array())`.
2. The only call to `update_relationship_context` in the entire codebase occurs at Stage 16.3 of `CognitiveOrchestrator.process()` (lines 666–668).
3. Result: Until the user completes their **first conversational turn** post-restart, `EmotionCore` continues running its background ODE steps every 200 ms with `_R_t = R_0`.

---

## Evidence Item E-04: Non-Atomic Multi-File Write Order During Turn Execution

### Code Citation
**File:** [`src/api/server.py`](file:///c:/Users/Lunafiah/Desktop/My_project/Lucia/src/api/server.py#L221-L262)
```python
221:         store = get_history_store()
222:         store.append_turn("user", req.input)
...
229:                 result: CognitiveTurnResult = await loop.run_in_executor(
230:                     None, orch.process, req.input
231:                 )
...
258:         store.append_turn("companion", resp_text)
```

**File:** [`src/core/orchestrator/cognitive_orchestrator.py`](file:///c:/Users/Lunafiah/Desktop/My_project/Lucia/src/core/orchestrator/cognitive_orchestrator.py#L650-L690)
```python
650:         # 16.3 Structured Relationship Update (Points 1 & 3)
...
658:                 rel_state_updated, _ = self._relationship_updater.step(signal=sig)
...
668:                 self._emotion_core.update_relationship_context(rel_state_updated.to_array())
...
682:         # 16.5 F-02: Checkpoint persistent dynamical state
683:         if hasattr(self._emotion_core, "checkpoint"):
684:             try:
685:                 self._emotion_core.checkpoint()
```

### Fact From Code
The chronological write sequence across independent disk stores during a single turn is:
1. `data/chat_history.json` (User turn appended; line 222)
2. `data/relationship.json` (Stage 16.3 via `RelationshipUpdater.step()`; line 658)
3. `data/dynamical_state.json` (Stage 16.5 via `EmotionCore.checkpoint()`; line 685)
4. `data/chat_history.json` (Companion turn appended; line 258)

If a process crash, power failure, or kernel kill occurs:
- Between (1) and (2): User message recorded, but neither relationship nor dynamical state reflect the turn.
- Between (2) and (3): Relationship state is updated to turn $N+1$, but dynamical state remains at turn $N$.
- Between (3) and (4): Both relationship and dynamical state are updated, but the companion response is missing from chat history.

---

## Evidence Item E-05: Homeostatic State Discrepancy & Reset on Cold Restart

### Code Citation
**File:** [`src/core/emotion/persistence.py`](file:///c:/Users/Lunafiah/Desktop/My_project/Lucia/src/core/emotion/persistence.py#L67-L68)
```python
67:         if self.m_homeo is not None:
68:             data["state"]["m_homeo"] = [float(x) for x in self.m_homeo]
```

**File:** [`src/core/emotion/homeostatic_engine.py`](file:///c:/Users/Lunafiah/Desktop/My_project/Lucia/src/core/emotion/homeostatic_engine.py#L64-L73)
```python
64:     def __init__(self, config: Optional[HomeostaticConfig] = None) -> None:
...
69:         # Persistent state
70:         self._energy: float = 1.0
71:         self._input_timestamps: Deque[float] = deque()
72:         self._last_input_time: Optional[float] = None
73:         self._last_constraints: Optional[BehavioralConstraints] = None
```

**File:** [`src/core/orchestrator/cognitive_orchestrator.py`](file:///c:/Users/Lunafiah/Desktop/My_project/Lucia/src/core/orchestrator/cognitive_orchestrator.py#L369-L382)
```python
369:         base_markers: SomaticMarkers = self._homeostatic_engine.compute_somatic_markers(
370:             pad_final
371:         )
...
377:         if hasattr(self._emotion_core, "update_homeostatic_context"):
378:             self._emotion_core.update_homeostatic_context(
379:                 energy=markers.energy,
380:                 load=markers.cognitive_load,
381:                 tension=markers.tension,
382:                 stability=markers.stability,
383:             )
```

### Fact From Code
1. `DynamicalStateSnapshot` saves `m_homeo` into `data/dynamical_state.json`.
2. `HomeostaticEngine` does NOT persist anything to disk and initializes `_energy = 1.0` on every restart.
3. On turn 1 post-restart, Stage 5 recalculates somatic markers from `HomeostaticEngine` (which has `_energy = 0.95` after `record_input()`), completely overwriting `EmotionCore._m_homeo` at line 378.
4. Restored `m_homeo` survives only during the idle window prior to turn 1.

---

## Evidence Item E-06: SDM Affective Memory Is 100% Volatile RAM

### Code Citation
**File:** [`src/core/memory/affective_memory.py`](file:///c:/Users/Lunafiah/Desktop/My_project/Lucia/src/core/memory/affective_memory.py#L68-L77)
```python
68:     def __init__(self, config: AffectiveMemoryConfig) -> None:
...
73:         self._sdm = SDMCore(config.sdm_config)
74:         self._M = config.m
75:         self._index: Dict[int, MemoryTrace] = {}
76:         self._index_lock = threading.RLock()
```

**File:** [`src/core/memory/sdm.py`](file:///c:/Users/Lunafiah/Desktop/My_project/Lucia/src/core/memory/sdm.py#L85-L97)
```python
85:         rng = np.random.default_rng()
86:         self._hard_locs: np.ndarray = rng.integers(
87:             0, 2, size=(self._num_locations, self._D), dtype=np.uint8
88:         )
89:         self._accumulator: np.ndarray = np.zeros(
90:             (self._num_locations, self._M), dtype=np.float32
91:         )
92:         self._act_counts: np.ndarray = np.zeros(
93:             self._num_locations, dtype=np.int64
94:         )
95: 
96:         self._trace_addresses: Dict[int, np.ndarray] = {}
97:         self._next_id: int = 0
```

### Fact From Code
1. Neither `AffectiveMemory` nor `SDMCore` contains any file read/write methods, persistence paths, or serialization routines.
2. On every process restart, `_hard_locs` is generated randomly with `rng.integers()`, and `_accumulator`, `_act_counts`, and `_index` are freshly allocated.
3. Cold restart wipes 100% of Kanerva SDM memory traces.
4. There is no downtime decay mechanism across process restarts for SDM, because there are zero persistent traces to decay.

---

## Evidence Item E-07: Process Termination Is Forceful (No Shutdown Hook)

### Code Citation
**File:** [`electron/main/process-manager.js`](file:///c:/Users/Lunafiah/Desktop/My_project/Lucia/electron/main/process-manager.js#L164-L174)
```javascript
164:       try {
165:         if (process.platform === 'win32') {
166:           // On Windows, taskkill kills the process tree
167:           spawn('taskkill', ['/pid', String(pid), '/T', '/F']);
168:         } else {
169:           this.process.kill('SIGTERM');
170:         }
171:       } catch (err) {
172:         console.error('[ProcessManager] Error killing process:', err);
173:         resolve();
174:       }
```

### Fact From Code
1. On Windows, `ProcessManager.stop()` invokes `taskkill /pid <pid> /T /F` (unconditional forceful kill).
2. `src/api/server.py` does not define any `lifespan` handler, `shutdown` event, or signal handler to checkpoint dynamical state prior to termination.
3. Dynamical state is NEVER checkpointed upon exit. The latest checkpoint on disk is ALWAYS from the end of the last processed turn (Stage 16.5).
4. Any dynamical trajectory evolved during post-turn idle is discarded.
