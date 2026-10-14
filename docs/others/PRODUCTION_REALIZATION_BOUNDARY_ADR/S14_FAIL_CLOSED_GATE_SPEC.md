# Specification: Stage S14 Fail-Closed Semantic Fidelity Gate

> **Document Version**: 1.0  
> **Status**: APPROVED ARCHITECTURAL SPECIFICATION (STAGE 4)  
> **Target Module**: `src/core/language/gate.py`  
> **Companion ADR**: [ADR-035](file:///c:/Users/Lunafiah/Desktop/My_project/Lucia/docs/others/PRODUCTION_REALIZATION_BOUNDARY_ADR/ADR_035_PRODUCTION_REALIZATION_BOUNDARY.md)  
> **Preceding Empirical Validation**: [Stage 3-D Evaluation Report](file:///c:/Users/Lunafiah/Desktop/My_project/Lucia/tests/evaluation/language_realization/fail_closed_gate/FINAL_REPORT.md)  

---

## 1. Functional Purpose & Boundary Constraints

The Stage S14 **Semantic Fidelity Gate** (`SemanticFidelityGate`) acts as an authoritative, fail-closed verification boundary positioned between Stage S11 (Language Realization) and Stage S15 (Voice Expression).

### Foundational Constraints:
1. **Verification, Not Remediation**:
   $$\text{Detection / Containment} \neq \text{Semantic Generation} \neq \text{Architectural Remediation}$$
   The gate cannot generate richer semantics or fix the SLM's internal representation. It exists exclusively to **veto and contain unfaithful realizations**.
2. **Zero Semantic Content Invention**:
   When an utterance is blocked, fallback generation must never hallucinate new facts, guess user intentions, or invent dialogue history.
3. **Deterministic & Hardware-Neutral**:
   Operates strictly on CPU using compiled symbolic rules (zero GPU VRAM, $<5\text{ ms}$ latency).

---

## 2. Gate Verification Algorithm

The verification pipeline executes 6 sequential deterministic checks against the candidate text:

```text
Candidate Text + RealizationInputContract
        │
        ├── [1. Invariant INV-2 Check] ──────► Regex for introspective affect / "as an AI"
        │                                      (Violation: INV2_INTROSPECTIVE_AFFECT)
        │
        ├── [2. Communicative Act Check] ────► Explicit refusal / clarification / inquiry markers
        │                                      (Violation: COMMUNICATIVE_ACT_FAILURE)
        │
        ├── [3. Polarity & Negation Check] ──► Explicit negation particles when polarity == False
        │                                      (Violation: CONTRADICTED)
        │
        ├── [4. Epistemic Modality Check] ───► Ban on certainty strengthening when INFERRED/UNKNOWN
        │                                      (Violation: EPISTEMIC_DISTORTION)
        │
        ├── [5. Argument & Entity Check] ────► Mandatory lemma/synonym presence (accounting for pro-drop)
        │                                      (Violation: ARGUMENT_ENTITY_LOSS)
        │
        └── [6. Forbidden Additions Check] ──► Zero match on ungrounded forbidden concept regexes
                                               (Violation: UNSUPPORTED_ADDITION)
        │
        ▼
   Any Violations?
   ├── YES ──► Emit Decision: BLOCK (Trigger Deterministic Fallback)
   └── NO  ──► Emit Decision: PASS  (Forward Candidate Text to Stage S15)
```

---

## 3. Fallback Registry & Template Specification

When a realization is `BLOCK`ed, Stage S14 selects a deterministic fallback template mapped strictly from `RealizationInputContract.act` and `polarity`:

```python
FALLBACK_REGISTRY = {
    # 1. Communicative Act: REFUSE (Ungrounded queries, out-of-scope factual claims)
    "SAFE_REFUSAL": {
        "en": "I do not have verified information regarding this topic, so I cannot provide a factual answer.",
        "vi": "Tôi chưa có thông tin xác thực về chủ đề này nên chưa thể đưa ra câu trả lời khẳng định.",
        "ja": "この件に関する確認済みの情報がないため、お答えできません。",
    },

    # 2. Communicative Act: CLARIFY (Ambiguous referents, unclear pronouns)
    "SAFE_CLARIFICATION": {
        "en": "Could you clarify specifically which topic or source you are referring to?",
        "vi": "Bạn có thể làm rõ cụ thể bạn đang đề cập đến nội dung hoặc tài liệu nào không?",
        "ja": "具体的にどの項目や資料を指しているか、詳しく教えていただけますか？",
    },

    # 3. Polarity Inversion: Target event did NOT occur, but realizer affirmed it
    "SAFE_NEGATION": {
        "en": "According to the verified system records, this event or task has not occurred or completed.",
        "vi": "Theo ghi nhận xác thực từ hệ thống, sự kiện hoặc tác vụ này chưa diễn ra hoặc chưa hoàn thành.",
        "ja": "確認されたシステム記録によれば、この事象またはタスクはまだ完了していません。",
    },

    # 4. Epistemic Distortion or Severe Argument Loss: Epistemic hedge fallback
    "SAFE_HEDGE": {
        "en": "Based on available observations, there are indications, but I cannot state this with certainty.",
        "vi": "Dựa trên các ghi nhận hiện có, dường như có dấu hiệu nhưng tôi chưa thể khẳng định chắc chắn.",
        "ja": "現在得られている情報からはそのように見受けられますが、確実な断定はできません。",
    },
}
```

---

## 4. History Logging & Memory Protection

To ensure `_history` never becomes an authoritative source of false facts:

1. **Emission Recording**:
   - If Gate returns `PASS`: `_history.append({"role": "lucia", "content": candidate_text, "status": "VERIFIED_PASS"})`.
   - If Gate returns `BLOCK`: `_history.append({"role": "lucia", "content": fallback_text, "status": "FAIL_CLOSED_FALLBACK", "original_violation": violations})`.
2. **Epistemic Isolation**:
   - In subsequent turns ($t+1$), Stage S1 (`InputGating`), Stage S6 (`ActiveInference`), and Stage S10 (`CAPS`) are architecturally forbidden from extracting factual commitments directly from `_history`. All facts must be verified against `KnowledgeStore`.
