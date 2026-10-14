# Migration & Implementation Sequence: Production Realization Boundary (Stage 5)

> **Document Version**: 1.0  
> **Status**: APPROVED MIGRATION PLAN (STAGE 4 $\rightarrow$ STAGE 5)  
> **Target Execution Agent**: Antigravity  
> **Companion Documents**:
> - [ADR-035](file:///c:/Users/Lunafiah/Desktop/My_project/Lucia/docs/others/PRODUCTION_REALIZATION_BOUNDARY_ADR/ADR_035_PRODUCTION_REALIZATION_BOUNDARY.md)
> - [Typed Contract Spec](file:///c:/Users/Lunafiah/Desktop/My_project/Lucia/docs/others/PRODUCTION_REALIZATION_BOUNDARY_ADR/TYPED_REALIZATION_CONTRACT_SPEC.md)
> - [S14 Fail-Closed Gate Spec](file:///c:/Users/Lunafiah/Desktop/My_project/Lucia/docs/others/PRODUCTION_REALIZATION_BOUNDARY_ADR/S14_FAIL_CLOSED_GATE_SPEC.md)

---

## 1. Migration Overview

Stage 5 will implement the Production Realization Boundary in `src/core/` without modifying Cognitive Core semantics, limbic ODE dynamics, or Genesis lifecycle invariants.

```text
Migration Steps:
Step 1: Create typed contracts in src/core/language/contract.py
Step 2: Update PromptAssembler in src/core/language/prompt_assembler.py
Step 3: Implement production gate in src/core/language/gate.py
Step 4: Wire contract & gate into CognitiveOrchestrator (S10b -> S11 -> S14)
Step 5: Create comprehensive unit & integration tests in tests/unit/test_production_gate.py
Step 6: Run full regression suite across all existing tests
```

---

## 2. Step-by-Step Implementation Instructions

### Step 1: `src/core/language/contract.py`
* **Action**: Create new file.
* **Contents**:
  - `CommunicativeAct` enum.
  - `EpistemicStatus` enum.
  - `SemanticScopeType` enum.
  - `ProvenanceOrigin` enum.
  - `SemanticRoleBinding` frozen dataclass.
  - `ProvenanceRecord` frozen dataclass.
  - `RealizationInputContract` frozen dataclass.
* **Dependencies**: Standard library only (`dataclasses`, `enum`, `typing`).

### Step 2: `src/core/language/prompt_assembler.py`
* **Action**: Update `assemble_prompt()` method.
* **Modification**:
  - Add support for accepting `contract: Optional[RealizationInputContract] = None`.
  - Compile the contract into natural language prose directives (EN, VI, JA) according to the Compiler Mapping Matrix in `TYPED_REALIZATION_CONTRACT_SPEC.md`.
  - Maintain backward compatibility for raw string calls.

### Step 3: `src/core/language/gate.py`
* **Action**: Create new file.
* **Contents**:
  - `GateDecision` dataclass.
  - `SemanticFidelityGate` class.
  - Implement 6 deterministic symbolic checks (INV-2 regex, communicative act cues, negation particle validation, epistemic certainty check, required argument slot check, forbidden concept scan).
  - Implement `FALLBACK_REGISTRY` mapping.
* **Dependencies**: Standard library only (`re`, `time`, `dataclasses`, `typing`). Pure CPU execution.

### Step 4: `src/core/orchestrator/cognitive_orchestrator.py`
* **Action**: Update turn execution pipeline.
* **Modification**:
  - **At Stage S10 / S10b**: After constructing `CAPSResult` and `SemanticGraph`, construct `contract: RealizationInputContract`.
  - **At Stage S11**: Pass `contract` to `PromptAssembler.assemble_prompt(..., contract=contract)`.
  - **At Stage S14**: Replace or augment `BoundaryLayer.validate_content()` by invoking `self.semantic_gate.verify(contract, candidate_text)`.
  - If `decision.status == "BLOCK"`:
    - Log verification violation: `logger.warning("Stage S14 Gate BLOCKED realization: %s", decision.violation_reasons)`.
    - Set final emitted text: `final_text = decision.fallback_text`.
  - If `decision.status == "PASS"`:
    - Set final emitted text: `final_text = candidate_text`.
  - Record `final_text` in `_history`.
  - Pass `final_text` to Stage S15 `ExpressionPolicy` and Stage S16 `VoicePipeline`.

### Step 5: `tests/unit/test_production_gate.py`
* **Action**: Create comprehensive unit tests.
* **Contents**:
  - Test `RealizationInputContract` creation and immutability.
  - Test `PromptAssembler` compilation for EN, VI, JA without code tokens.
  - Test `SemanticFidelityGate` detection across all 5 error categories.
  - Test deterministic fallback emission for `REFUSE`, `CLARIFY`, `SAFE_NEGATION`, `SAFE_HEDGE`.
  - Test integration with `CognitiveOrchestrator` mock run.

### Step 6: Full Regression Verification
* Execute:
  ```powershell
  .\.venv\Scripts\pytest tests/unit/
  ```
* Verify that zero existing tests are broken.

---

## 3. Strict Prohibitions for Stage 5

* **DO NOT** modify `KnowledgeStore`, `JTMS`, or ontology triples.
* **DO NOT** modify Coupled MT-LNN ODE parameters or Philia attractor coordinates.
* **DO NOT** modify `data/profile.json` (`{"is_onboarded": false}`) or Genesis preparation semantics.
* **DO NOT** add cloud API dependencies.
* **DO NOT** hold locks (`_state_lock`, `_turn_lock`) during LLM inference.
