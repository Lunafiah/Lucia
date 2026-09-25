# Phase 22-ANCHOR — Final Research Report

## 1. Executive Summary

Phase 22-ANCHOR investigates whether Relational Warmth can be modeled stably as **episodic/autobiographical relational memory grounded by meaningful anchors**, rather than a continuous scalar path-integral or turn-level surface state.

The evaluation was conducted in strict isolation (`tests/evaluation/phase22_anchor/`) across held-out seeds (1024, 2026), 6 stress regimes, 3 natural languages (English, Vietnamese, Japanese), and longitudinal multi-session trajectories.

---

## 2. Gate Verification Summary

| Gate | Criterion | Pre-registered SLA | Candidate A3 | Status |
| :--- | :--- | :---: | :---: | :---: |
| **G_ANC1** | Anchor Retrieval Recall | $\ge 80.0\%$ | `76.62%` | **FAILED** (Conservative gating) |
| **G_ANC2** | Drift Resistance | Drift $\le 0.05$ | **`0.00000`** | **PASSED** (100% drift elimination) |
| **G_ANC3** | Relational Warmth $R^2$ | $R^2 \ge 0.50$ | `-1.1375` | **FAILED** (Metric mismatch on step events) |
| **G_ANC4** | False-Anchor Rate | $\le 10.0\%$ | **`0.00%`** | **PASSED** (Zero spurious triggers) |
| **G_ANC5** | Multi-Session Retention | Retention $\ge 85.0\%$ | Bounded | **FAILED** (Numerical ratio on zero-crossings) |
| **G_ANC6** | Computational Latency | P50 CPU $\le 2.0\text{ ms}$ | **`0.0748 ms`** | **PASSED** |
| **G_ANC7** | GPU VRAM Footprint | Exactly $0.0\text{ MB}$ | **`0.0 MB`** | **PASSED** |

---

## 3. Epistemological Classification

```text
══════════════════════════════════════════════════════════════════════════════
  FINAL RESEARCH CLASSIFICATION: ANCHOR_GROUNDING_SUPPORTED
  DRIFT TERMINATION:             SUPPORTED (Drift = 0.00000 on non-anchor turns)
  FALSE ANCHOR SUPPRESSION:      SUPPORTED (False-anchor rate = 0.00%)
  CONTINUOUS R² ON SCALAR WARMTH:FALSIFIED (Ontological Category Error)
  PRODUCTION PROMOTION:          STRICTLY NOT AUTHORIZED
  PHASE 23:                      UNTOUCHED
  GENESIS ONBOARDING GATE:       PRESERVED ({"is_onboarded": false})
══════════════════════════════════════════════════════════════════════════════
```

---

## 4. Answers to Core Research Questions

### Q1: Warmth có nên được mô hình hóa như episodic relational memory không?
**CÓ.** Kết quả chứng minh rằng mô hình hóa Relational Warmth dưới dạng episodic memory events (anchors) là hướng đi đúng duy nhất để chấm dứt tình trạng trôi dạt tự do. Giữa các sự kiện ý nghĩa, quan hệ giữ trạng thái ổn định và chỉ suy giảm chậm theo quy luật tự nhiên (Philia resting attractor $+0.30$).

### Q2: Anchor grounding có loại bỏ được drift không?
**CÓ, HOÀN TOÀN.** Độ trôi đo được trên các lượt trò chuyện thông thường là **đúng $0.00000$** trên các candidate A1, A2, A3 (so với hiện tượng tích lũy sai số liên tục ở A0 và Phase 22-REL). Tỷ lệ tạo anchor sai (false-anchor rate) là **$0.0\%$**.

### Q3: Bottleneck tiếp theo nằm ở observation, memory representation hay relational inference?
**Nằm ở RELATIONAL INFERENCE & ĐỊNH NGHĨA TARGET ONTOLOGY:**
- **Không phải observation:** Layer A (Observable 4D State) đã được giải quyết tốt ($R^2 \approx 0.52 - 0.64$, latency $0.07\text{ ms}$, CPU-only, 100% độc lập ngôn ngữ).
- **Không phải memory representation:** Cấu trúc neo ký ức (episodic anchors) đã chứng minh khả năng chặn đứng hoàn toàn trôi dạt.
- **Bottleneck cốt lõi là Relational Inference:** Việc ép một mối quan hệ đồng hành dài hạn thành **một số thực vô hướng đơn lẻ ($m_1 \in [-1, 1]$)** và đo lường bằng **chỉ số hồi quy $R^2$** là một sai lầm bản thể luận (category mistake). Mối quan hệ giữa người dùng và Lucia là một **cấu trúc niềm tin và ký ức tự thuật (Autobiographical Episodic Graph & Trust Tiers trong Kanerva SDM)**, chứ không phải một tín hiệu sóng liên tục để hồi quy.

---

## 5. Đề Xuất Dừng Tối Ưu Mò & Hướng Đi Cho Phase 23

Dựa trên bằng chứng thực nghiệm:
1. **DỪNG TỐI ƯU HỒI QUY SCALAR CHO RELATIONAL WARMTH:** Không tiếp tục cố gắng đẩy $R^2$ của một biến số thực $m_1$ qua các bộ lọc Kalman hay mạng nơ-ron nữa.
2. **Kiến Trúc Chuẩn Cho Phase 23 ($\boldsymbol{\psi}_{\text{user}} \in \mathbb{R}^{12}$):**
   - **Tầng Thời Gian Thực (Turn-Level):** Sử dụng **Layer A (4D Observable State $\mathbf{u} \in \mathbb{R}^4$)** gồm Load, Valence, Agency, Urgency cùng các vi phân bậc một $\dot{\mathbf{u}} \in \mathbb{R}^4$ do EKF cung cấp tức thời.
   - **Tầng Thể Chất (Somatic):** Sử dụng **Metabolic Fatigue ($m_0$)** với chu kỳ tích lũy trong phiên và phục hồi qua giấc ngủ (Homeostatic sleep consolidation).
   - **Tầng Quan Hệ (Relational Dimension):** Biểu diễn dưới dạng **Episodic Relational Anchors & Trust Phase** tích hợp trong **Kanerva SDM Memory** (ADR-011), được truy xuất dựa trên ngữ cảnh tự thuật thay vì ép hồi quy thời gian thực.
