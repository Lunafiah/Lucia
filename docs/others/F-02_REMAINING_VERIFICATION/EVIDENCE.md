# Code Evidence & Verification Trace — F-02 Remaining Architecture Verification

**Document ID:** `VERIF-EVID-20261007`  
**Classification:** Verbatim Source Code Evidence & Numerical Trace Ledger  
**Baseline Commit:** `32660ac4e422bdb2ecb9c7b97a4bdc04c805418e`  
**Parent Document:** [`REPORT.md`](file:///c:/Users/Lunafiah/Desktop/My_project/Lucia/docs/others/F-02_REMAINING_VERIFICATION/REPORT.md)  

---

## 1. Evidence for V1 / V3: Unforced ODE Equations & Non-Linear Coupling

### Code Citation 1.1: Fast Timescale & Non-Linearity
**File:** [`src/core/emotion/emotion_core.py:1063-1070`](file:///c:/Users/Lunafiah/Desktop/My_project/Lucia/src/core/emotion/emotion_core.py#L1063-L1070)
```python
1063:             # Time constant
1064:             tau_input = W_tau @ h + U_tau @ stimulus + b_tau
1065:             tau_fast = np.clip(softplus(tau_input), self._config.tau_fast_min, self._config.tau_fast_max)
1066: 
1067:             # Fast ODE derivative
1068:             delta_s_eff = s - s_eff
1069:             h_input = W_f @ h + U_f @ stimulus + (W_fs @ delta_s_eff) + b_f
1070:             dh_dt = (-h + np.tanh(h_input)) / tau_fast
```
- **Fact:** When $stimulus = \mathbf{0}$, $h$ derivative depends non-linearly on $\tanh(W_f h + W_{fs}(s - s^*_{\text{eff}}))$.
- **Fact:** $\tau_{\text{fast}}$ is dynamic and state-dependent via $\text{softplus}(W_\tau h)$.

### Code Citation 1.2: Slow Timescale & Dynamic Homeostatic Forcing
**File:** [`src/core/emotion/emotion_core.py:1077-1082`](file:///c:/Users/Lunafiah/Desktop/My_project/Lucia/src/core/emotion/emotion_core.py#L1077-L1082)
```python
1077:             delta_m = self._m_homeo - self.m_homeo_resting
1078:             homeo_term = W_sh @ delta_m
1079: 
1080:             charge_input = (W_sf @ h) + homeo_term + rec_term
1081:             ds_dt = -(s - s_eff) / self._config.tau_slow_decay + np.tanh(charge_input) / self._config.tau_slow_charge
```
- **Fact:** $s$ is driven by $\frac{\tanh(W_{sf} h + W_{sh} \delta m)}{\tau_{\text{slow\_charge}}}$.
- **Fact:** An uncoupled linear relaxation $ds/dt = -(s - s^*_{\text{eff}})/\tau_{\text{slow\_decay}}$ completely ignores homeostatic charging ($W_{sh} \delta m$). This proves that an exact closed form is impossible while $\delta m \ne \mathbf{0}$.

---

## 2. Evidence for V5: Chat History Independence from Cognitive Prompting

### Code Citation 2.1: Chat History Appended by Server, Not Orchestrator
**File:** [`src/api/server.py:221-258`](file:///c:/Users/Lunafiah/Desktop/My_project/Lucia/src/api/server.py#L221-L258)
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
- **Fact:** `store.append_turn` writes directly to `data/chat_history.json`.

### Code Citation 2.2: CognitiveOrchestrator Working Memory Resets to Empty
**File:** [`src/core/orchestrator/cognitive_orchestrator.py:191`](file:///c:/Users/Lunafiah/Desktop/My_project/Lucia/src/core/orchestrator/cognitive_orchestrator.py#L191)
```python
191:         self._history: List[Tuple[str, str]] = []
```
**File:** [`src/core/orchestrator/cognitive_orchestrator.py:675-680`](file:///c:/Users/Lunafiah/Desktop/My_project/Lucia/src/core/orchestrator/cognitive_orchestrator.py#L675-L680)
```python
675:         # 16.4 Update dialogue history (ephemeral working memory)
676:         self._history.append(("user", input_text))
677:         self._history.append(("assistant", safe_response))
678:         max_pairs = self._max_history_turns * 2
679:         if len(self._history) > max_pairs:
680:             self._history = self._history[-max_pairs:]
```
- **Fact:** `CognitiveOrchestrator._history` is purely ephemeral in-memory cache.
- **Fact:** `CognitiveOrchestrator` never reads `data/chat_history.json`. On cold restart, dialogue context sent to the LLM prompt assembler is empty (`[]`).

---

## 3. Evidence for V7: Native Homeostatic Equilibrium

### Code Citation 3.1: Energy Recovery & Idle Threshold
**File:** [`src/core/emotion/homeostatic_engine.py:46-50`](file:///c:/Users/Lunafiah/Desktop/My_project/Lucia/src/core/emotion/homeostatic_engine.py#L46-L50)
```python
46: # Energy recovery per second during idle (after 60 s idle threshold)
47: _ENERGY_RECOVERY_PER_SECOND = 0.02
48: 
49: # Idle threshold before energy recovery starts (seconds)
50: _IDLE_RECOVERY_THRESHOLD_S = 60.0
```
**File:** [`src/core/emotion/homeostatic_engine.py:276-280`](file:///c:/Users/Lunafiah/Desktop/My_project/Lucia/src/core/emotion/homeostatic_engine.py#L276-L280)
```python
276:         idle_seconds = now - self._last_input_time
277:         if idle_seconds >= _IDLE_RECOVERY_THRESHOLD_S:
278:             recovery_seconds = idle_seconds - _IDLE_RECOVERY_THRESHOLD_S
279:             recovery = recovery_seconds * _ENERGY_RECOVERY_PER_SECOND
280:             self._energy = min(1.0, self._energy + recovery)
```
- **Fact:** Any idle period of $\Delta t \ge 60\text{s} + 1.0/0.02 = 110.0\text{s}$ restores energy to exactly $1.0$.
- **Fact:** Rolling input window is strictly $60.0\text{s}$ (`homeostatic_engine.py:284`). Any idle period $\ge 60.0\text{s}$ clears all inputs, reducing frequency component of cognitive load to $0.0$.
- **Conclusion:** Reconstructing $E = 1.0$ and $C = 0.0$ for downtime $\Delta t \ge 110\text{s}$ is bit-exact with the codebase's existing mathematical model.

---

## 4. Evidence for V8: Kanerva SDM Memory Volatility

### Code Citation 4.1: Random Re-initialization of Hard Locations
**File:** [`src/core/memory/sdm.py:85-88`](file:///c:/Users/Lunafiah/Desktop/My_project/Lucia/src/core/memory/sdm.py#L85-L88)
```python
85:         rng = np.random.default_rng()
86:         self._hard_locs: np.ndarray = rng.integers(
87:             0, 2, size=(self._num_locations, self._D), dtype=np.uint8
88:         )
```
- **Fact:** `SDMCore._hard_locs` is generated randomly via `rng.integers()` on every boot with an unseeded generator.
- **Fact:** No serialization or loading methods exist in `SDMCore` or `AffectiveMemory`. All memory traces evaporate on restart.

---

## 5. Evidence for V9: Startup Restore Dependency Ordering

### Code Citation 5.1: Current Inverted Order in Factory
**File:** [`src/core/orchestrator/cognitive_orchestrator.py:804-835`](file:///c:/Users/Lunafiah/Desktop/My_project/Lucia/src/core/orchestrator/cognitive_orchestrator.py#L804-L835)
```python
804:     emotion_core = EmotionCore(
805:         config.to_emotion_config(),
806:         storage_path=dynamical_storage_path,
807:     )
...
833:         relationship_updater = RelationshipUpdater(
834:             storage_path=relationship_storage_path
835:         )
```
- **Fact:** `EmotionCore` runs `restore_from_checkpoint()` inside `__init__` (line 218).
- **Fact:** `RelationshipUpdater` is constructed 29 lines later (line 833).
- **Fact:** Inverting this dependency requires only:
  1. Construct `RelationshipUpdater` first.
  2. Pass `rel_updater.get_state().to_array()` to `EmotionCore` before `restore_from_checkpoint()`.
  3. No other subsystem depends on `EmotionCore` being constructed prior to `RelationshipUpdater`. The graph is acyclic.
