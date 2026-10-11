# P27_RESEARCH_PROTOCOL_DESIGN.md

```text
Document Type: RESEARCH PROTOCOL DESIGN SPECIFICATION
Document Identifier: DOC-P27-PROTOCOL-001
Status: PROTOCOL SPECIFICATION ONLY (NO CODE — NO HARNESS RUN — ZERO CODEBASE MUTATION)
Target Path: docs/PhaseDocs/Lucia-phase27-Personalized_Individual_Trajectory/P27_RESEARCH_PROTOCOL_DESIGN.md
Authority: RESEARCH ARM (Gemini) → SUBMITTED FOR REVIEW (Ciah / Human Owner)
Preceding Canonical Baselines:
  - P26_P27_DEPENDENCY_AND_BOUNDARY_AUDIT.md
  - P26 Post-Trial Scientific Audit (DOC-P26-007)
  - P27_RESEARCH_CHARTER.md (DOC-P27-CHARTER-001)
Canonical Governance Status:
  Decision Gate: P27-RESEARCH-ELIGIBLE-BUT-P26-GAP-MUST-REMAIN-EXPLICIT
  P26 Claim C: NOT ESTABLISHED | P26 Claim D: NOT ESTABLISHED
  P27 Research: ELIGIBLE | P27 Architecture: NOT ELIGIBLE | P27 Production: FORBIDDEN
  Genesis Gate: LOCKED (data/profile.json must remain exactly: {"is_onboarded": false})
  Diff Boundaries: src/core/** diff = 0 | electron/** diff = 0 | data/** diff = 0
```

---

## 1. Executive Summary

Tài liệu này xác lập đặc tả thiết kế giao thức nghiên cứu thực nghiệm (**Research Protocol Design**) cho Phase 27 (Personalized Individual Trajectory) của hệ thống Lucia. Mục tiêu của giao thức là chuyển hóa các ranh giới nhận thức luận (epistemic boundaries) đã được chuẩn hóa trong `P27_RESEARCH_CHARTER.md` thành một khung kiểm định thực nghiệm định lượng, có khả năng phản nghiệm (falsifiable), và độc lập hoàn toàn khỏi môi trường sản xuất.

Giao thức này được thiết kế để giải quyết câu hỏi trọng tâm: Liệu một chuỗi lịch sử tương tác dài hạn, có thứ tự nhân quả có thể tạo ra sự phân kỳ trạng thái nội sinh đo lường được dưới điều kiện kẹp bộ nhớ (Memory-Clamped State Divergence), vượt qua sự giải thích tầm thường của cơ chế tiếp nhận truy xuất bộ nhớ sự kiện (episodic retrieval ingress) hay không. Giao thức thiết lập các điều kiện kiểm soát nghiêm ngặt gồm: thiết kế cặp song sinh phản thực nghiệm hợp lệ (twin / valid counterfactual branches), cơ chế kẹp bộ nhớ (memory clamping), cơ chế đối chứng thụ động yoked hai chiều/một chiều, và các mô hình không (null models).

**Nguyên tắc Phân định Cốt lõi (Core Epistemic Distinction):**
$$\text{Measured State (Observable)} \neq \text{Candidate Mechanism} \neq \text{High-Level Interpretation}$$
Sự phân kỳ trạng thái đo lường được là một biến quan sát thực nghiệm (**observable**), tuyệt đối **không tự động đồng nhất** với sự phân hóa phát triển nội tâm, tính cá nhân mới nổi (Emergent Individuality) hay sở thích tự chủ (Autonomous Preference).

Tài liệu này là một **đặc tả nghiên cứu (research specification)**. Nó tuyệt đối **không** chứa mã nguồn thực thi, **không** xây dựng harness, **không** can thiệp vào mã nguồn sản xuất (`src/core/** diff = 0`, `electron/** diff = 0`, `data/** diff = 0`), **không** tạo Architecture Contract hay ADR, **không** mở lại P26-R4, **không** mở P28, và bảo tồn nguyên vẹn trạng thái Genesis Onboarding Gate (`data/profile.json == {"is_onboarded": false}`).

---

## 2. Governance & Scope

### 2.1 Ma trận tuân thủ Quản trị (Governance Compliance Matrix)

```text
┌────────────────────────────────────────────────────────────────────────┐
│                      P27 GOVERNANCE MATRIX                             │
├──────────────────────────────┬─────────────────────────────────────────┤
│ P26 Claim C                  │ NOT ESTABLISHED                         │
│ P26 Claim D                  │ NOT ESTABLISHED                         │
│ P27 Research Status          │ ELIGIBLE                                │
│ P27 Architecture Gate        │ NOT ELIGIBLE (STRICTLY LOCKED)          │
│ P27 Production Status        │ FORBIDDEN                               │
│ Genesis Gate Status          │ LOCKED (data/profile.json: false)       │
│ Production Codebase Diff     │ Exactly: src/core/** diff = 0           │
│                              │          electron/** diff = 0           │
│                              │          data/** diff = 0               │
│ Genesis Gate Invariant       │ data/profile.json ==                    │
│                              │   {"is_onboarded": false} (EXACT)       │
│ P26-R4 Status                │ NOT REQUIRED / NOT AUTHORIZED           │
│ Phase 28 Status              │ NOT OPENED / NOT AUTHORIZED             │
│ Architecture Contract / ADR  │ FORBIDDEN AT THIS STAGE                 │
│ Roadmap / Registry Mutation  │ NONE (PHASE_REGISTRY.md untouched)      │
│ Level 5 / Level 6 Scope      │ STRICTLY OUTSIDE P27 RESEARCH SCOPE     │
└──────────────────────────────┴─────────────────────────────────────────┘
```

### 2.2 Phạm vi Nghiên cứu và Cô lập Vùng nhớ

1. **Research $\neq$ Production:** Mọi cấu trúc mô phỏng, kịch bản tương tác và bộ ghi nhận dữ liệu chỉ được phép tồn tại trong phạm vi thư mục nghiên cứu độc lập của Phase 27.
2. **Khu vực lưu trữ hợp lệ:**
   * Đặc tả và tài liệu: `docs/PhaseDocs/Lucia-phase27-Personalized_Individual_Trajectory/`
   * Dữ liệu telemetry và báo cáo phân tích sau này (khi được cấp quyền): `docs/PhaseDocs/Lucia-phase27-Personalized_Individual_Trajectory/evaluation_artifacts/`
   * Tuyệt đối không tạo thư mục `evaluation/` hoặc `evaluation_artifacts/` tại thư mục gốc của repository.
3. **Quy tắc Bất biến:** Không cho phép tạo các biến trạng thái tồn tại vĩnh viễn (persistent weights/state) trong môi trường runtime của Lucia. Bất kỳ sự thay đổi nào đối với `src/core/**`, `electron/**`, hoặc `data/**` đều là vi phạm quản trị nghiêm trọng.

---

## 3. Research Question

Câu hỏi nghiên cứu trung tâm của giao thức P27:

> **"Liệu một dòng lịch sử tương tác dài hạn, đơn nhất và có thứ tự nhân quả có thể tạo ra sự phân kỳ trạng thái nội sinh đo lường được dưới điều kiện kẹp bộ nhớ (Memory-Clamped State Divergence), có tính nhạy thứ tự và có khả năng duy trì/điều chỉnh qua thời gian, vượt quá những gì có thể giải thích chỉ bằng cơ chế tiếp nhận truy xuất bộ nhớ sự kiện (episodic retrieval ingress) hay không?"**

Giao thức kiểm định trực tiếp ranh giới giữa:

* **Biến quan sát đo lường được (A–E, G–I):** Tính liên tục dọc (longitudinal continuity), tính định hướng đường đi / hiệu suất quỹ đạo (trajectory directionality / path efficiency), tính phụ thuộc lịch sử (history dependence), tính nhạy thứ tự thời gian (order sensitivity), sự phân kỳ trạng thái dưới điều kiện kẹp bộ nhớ (memory-clamped state divergence), và sự suy giảm do kẹp bộ nhớ (memory-clamp attenuation).
* **Cơ chế giả định cấp trung (Level 3–4):** Causal developmental dependence (phụ thuộc phát triển nhân quả) và Endogenous structural/state asymmetry (bất đối xứng cấu trúc/trạng thái nội sinh). *Lưu ý:* Việc quy kết cơ chế cụ thể là một câu hỏi thực nghiệm mở, không được tiên nghiệm áp đặt.
* **Suy diễn diễn giải cấp cao (Level 5–6 / J–K):** Tính cá nhân mới nổi (Emergent individuality) và Sở thích tự chủ (Autonomous preference). *Ranh giới:* Nằm ngoài phạm vi nghiên cứu của P27.

---

## 4. Construct Taxonomy

Bảng phân loại construct chuẩn tắc quy định ranh giới định nghĩa và chỉ số đo lường:

```text
┌────────────────────────────────────────────────────────────────────────┐
│                        CONSTRUCT FIREWALL                              │
│                                                                        │
│  [A] Longitudinal continuity       [F] Adaptation / revision           │
│  [B] Trajectory directionality /   [G] Memory-mediated persistence     │
│      path efficiency (Geometric)   [H] State-mediated persistence      │
│  [C] History dependence                (Substrate attribution open)    │
│  [D] Order sensitivity & Causal    [I] Trajectory uniqueness           │
│      developmental dependence      [E] Memory-clamped state divergence │
│                                                                        │
│                         ═════════════════                              │
│                         ║ FIREWALL: ↛   ║                              │
│                         ═════════════════                              │
│                                                                        │
│  [J] Emergent Individuality        [K] Autonomous Preference           │
│      (LEVEL 5 — BEYOND P27 SCOPE)      (LEVEL 6 — BEYOND P27 SCOPE)    │
└────────────────────────────────────────────────────────────────────────┘
```

1. **A. Longitudinal continuity:** Khả năng duy trì các biến trạng thái nội sinh qua nhiều phiên mà không bị suy sụp về điểm kỳ dị hoặc bị reset ngoài ý muốn.
2. **B. Trajectory directionality / path efficiency (Candidate Geometric Observable):** Tỷ số hình học giữa độ dịch chuyển thực và tổng chiều dài đường đi trong không gian trạng thái. *Ranh giới:* Đây là một biến quan sát hình học, **KHÔNG TỰ ĐỘNG ĐỒNG NHẤT** với tính cố kết phát triển (developmental coherence) khi chưa có construct validation độc lập.
3. **C. History dependence:** Trạng thái tại bước $t$ là hàm phụ thuộc vào chuỗi lịch sử tương tác quá khứ: $S_t = f(S_{t-1}, x_t) \neq f(S_0, x_t)$.
4. **D. Causal developmental dependence & Order sensitivity:**
   * *Order sensitivity:* Sự phân kỳ trạng thái phụ thuộc vào trật tự chuỗi tương tác (được kiểm định qua phép hoán vị thời gian).
   * *Causal developmental dependence:* Sự phân kỳ trạng thái được gây ra trực tiếp bởi chuỗi can thiệp nhân quả có thứ tự, đòi hỏi phải được xác lập qua đối chứng can thiệp phản thực nghiệm hợp lệ (preregistered intervention contrast).
5. **E. Memory-clamped state divergence:** Sự phân tách vector trạng thái có ý nghĩa thống kê giữa hai nhánh xuất phát từ cùng một trạng thái ban đầu nhưng trải qua hai dòng lịch sử khác nhau, được đo lường dưới điều kiện ngắt hoàn toàn episodic retrieval ingress.
6. **F. Adaptation / revision:** Khả năng trạng thái điều chỉnh hướng chuyển dịch khi tiếp nhận chuỗi can thiệp đảo ngược hoặc xung đột, thay vì bị khóa cứng (frozen) vĩnh viễn.
7. **G. Memory-mediated persistence:** Sự duy trì xu hướng hành vi hoặc trạng thái được thúc đẩy bởi việc tiếp nhận thông tin lịch sử từ bộ nhớ sự kiện (episodic retrieval ingress) đưa vào luồng thông tin ngoại vi bề mặt (externally surfaced historical information).
8. **H. State-mediated persistence:** Sự duy trì xu hướng hành vi hoặc cấu trúc động lực học được phản ánh qua hệ thống chuyển dịch trạng thái nội sinh (internal-state transition system) mà không phụ thuộc vào episodic retrieval ingress. *Lưu ý:* Cơ chế cụ thể (limbic ODE, $\mathbf{R}_t$, $\mathbf{W}_{\text{rel}}$, semantic substrate) là một **câu hỏi thực nghiệm mở**, không được tiên nghiệm quy kết.
9. **I. Trajectory uniqueness:** Tính chất độc nhất về mặt toán học của vector trạng thái tích lũy do chuỗi kích thích đầu vào là duy nhất.
10. **J. Emergent individuality (Level 5 Claim):** Bản sắc tâm lý tự thân mới nổi. *Ranh giới:* Nằm ngoài phạm vi kiểm định và ngoài thẩm quyền nghiên cứu của P27.
11. **K. Autonomous preference (Level 6 Claim):** Khả năng tự tạo ra cấu trúc mục tiêu/sở thích độc lập với prompt hoặc cấu hình hệ thống. *Ranh giới:* Nằm ngoài phạm vi kiểm định và ngoài thẩm quyền nghiên cứu của P27.

---

## 5. Hypotheses

### 5.1 Giả thuyết Không (Null Hypotheses)

* **$H_{0, \text{traj}}$ (Primary):** Dưới điều kiện kẹp bộ nhớ (Memory Clamp), độ phân kỳ trạng thái nội sinh giữa hai nhánh lịch sử không vượt quá độ phân kỳ quan sát được trong mô hình trôi dạt ngẫu nhiên:

$$\mathcal{D}_{\text{MC}}(\text{Branch}_A, \text{Branch}_B) \le \mathcal{D}_{\text{MC}}(\text{Null}_{\text{drift}})$$

* **$H_{0, \text{order}}$ (Order Sensitivity Null):** Khoảng cách trạng thái giữa chuỗi tương tác tuần tự chuẩn tắc và chuỗi bị hoán vị ngẫu nhiên thứ tự thời gian không vượt qua biên độ tương đương của phân bố hoán vị nền:

$$\Vert S_T(\text{Sequential}) - S_T(\text{Permuted}) \Vert \le \delta_{\text{perm, null}}$$

*(Lưu ý: Bác bỏ $H_{0, \text{order}}$ chỉ xác lập tính nhạy thứ tự thời gian, KHÔNG PHẢI là bằng chứng nhân quả đầy đủ).*

* **$H_{0, \text{causal}}$ (Counterfactual Causal Null):** Dưới thiết kế can thiệp phản thực nghiệm hợp lệ (giữ nguyên snapshot $S_{\text{fork}}$, thay đổi chuỗi can thiệp đầu vào tương lai), độ phân kỳ trạng thái giữa nhánh factual và nhánh counterfactual không vượt qua ngưỡng nhiễu can thiệp:

$$\Vert S_T(\text{Factual}) - S_T(\text{Counterfactual}) \Vert \le \delta_{\text{causal, null}}$$

* **$H_{0, \text{memory}}$:** Toàn bộ sự phân kỳ quan sát được giữa các nhánh lịch sử bị triệt tiêu hoàn toàn khi vô hiệu hóa cơ chế episodic retrieval ingress:

$$\mathcal{D}_{\text{MC}} \le \delta_{\text{noise}}$$

* **$H_{0, \text{dissipation}}$:** Trạng thái nội sinh tiêu tán hoàn toàn về điểm cân bằng tĩnh (attractor baseline) sau giai đoạn làm nguội trung tính (washout phase).

### 5.2 Giả thuyết Thay thế (Alternative Hypotheses)

* **$H_{1, \text{traj}}$ (Primary Observable):** Dưới điều kiện kẹp bộ nhớ, tồn tại một lượng phân kỳ trạng thái nội sinh đo lường được có ý nghĩa thống kê so với mô hình trôi dạt ngẫu nhiên:

$$\mathcal{D}_{\text{MC}} > \mathcal{D}_{\text{null}} + \delta_{\text{min}}$$

*(Kết quả này xác lập hiện tượng Memory-Clamped State Divergence; TUYỆT ĐỐI KHÔNG TỰ ĐỘNG CHỨNG MINH tính cá nhân hay sở thích tự chủ).*

* **$H_{1, \text{order}}$:** Thứ tự thời gian của các can thiệp tạo ra phân kỳ trạng thái vượt qua phân bố hoán vị ngẫu nhiên (chứng minh tính nhạy thứ tự thời gian - Order Sensitivity).
* **$H_{1, \text{causal}}$:** Can thiệp đầu vào phản thực nghiệm tại cùng một snapshot phân nhánh tạo ra phân kỳ trạng thái có ý nghĩa thống kê (chứng minh sự phụ thuộc nhân quả - Causal Developmental Dependence).

---

## 6. Operational Definitions

Nhằm bảo vệ tính giá trị cấu trúc (construct validity), các định nghĩa vận hành được quy định như sau:

| Khái niệm | Định nghĩa Vận hành (Operational Definition) | Ranh giới Loại trừ (What it is NOT) |
| --- | --- | --- |
| **Trajectory Directionality / Path Efficiency** | Tỷ số giữa độ dịch chuyển thực của trạng thái và tổng chiều dài đường đi: $\mathcal{E}_{\text{path}} = \frac{\Vert\mathbf{R}_T - \mathbf{R}_0\Vert_2}{\sum_{t=1}^T \Vert\mathbf{R}_t - \mathbf{R}_{t-1}\Vert_2}$ | Là biến quan sát hình học; KHÔNG PHẢI là tính cố kết phát triển (developmental coherence) hay sự nhất quán hội thoại. |
| **History Dependence** | Khoảng cách trạng thái giữa chuỗi tương tác có lịch sử và chuỗi không lịch sử: $\Vert\mathbf{R}_t(\text{History}) - \mathbf{R}_t(\text{Zero-History})\Vert_2$ | Không phải là việc trích dẫn lại sự kiện quá khứ trong câu trả lời. |
| **Memory-Clamped State Divergence** | Khoảng cách Euclidean $\mathcal{D}_{\text{MC}}$ giữa hai nhánh tại pha Washout khi ngắt hoàn toàn episodic retrieval ingress ($K_{\text{retrieved}} = 0$). | Đo lường độ phân kỳ trạng thái bền vững; KHÔNG chứng minh sự tồn tại của "cá tính", "bản ngã" hay "sở thích tự chủ". |
| **Order Sensitivity** | Sự sai lệch vector trạng thái giữa chuỗi tương tác tuần tự và chuỗi bị hoán vị: $\Vert\mathbf{R}_T(\text{Sequential}) - \mathbf{R}_T(\text{Permuted})\Vert_2 > \delta_{\text{perm, null}}$ | Chỉ đo tính nhạy thứ tự thời gian; KHÔNG PHẢI LÀ BẰNG CHỨNG NHÂN QUẢ ĐẦY ĐỦ (NOT CAUSAL PROOF). |
| **Causal Developmental Dependence** | Phân kỳ trạng thái được tạo ra bởi can thiệp phản thực nghiệm hợp lệ trên chuỗi đầu vào tại cùng một snapshot: $\Vert S_T(\text{Factual}) - S_T(\text{Counterfactual})\Vert_2 > \delta_{\text{causal, null}}$ | Đòi hỏi can thiệp phản thực nghiệm có đối chứng; không thể chứng minh chỉ bằng hoán vị thời gian. |
| **Emergent Individuality** | **`NOT DIRECTLY IDENTIFIABLE UNDER CURRENT OPERATIONALIZATION`** | Bị cấm gán nhãn cho bất kỳ sự trôi dạt tham số hay phân kỳ vector nào (Level 5 — Outside Scope). |
| **Autonomous Preference** | **`NOT DIRECTLY IDENTIFIABLE UNDER CURRENT OPERATIONALIZATION`** | Bị cấm gán nhãn cho bất kỳ thiên kiến lựa chọn nào do prompt hoặc trạng thái định hình (Level 6 — Outside Scope). |

---

## 7. Experimental Design

Giao thức sử dụng thiết kế đa nhánh dài hạn (Longitudinal Multi-Branch Protocol) gồm $N$ phiên tương tác liên tục ($T = 1 \dots 50$ epochs tương tác chuẩn hóa).

```text
                                  ┌──────────────────────────────┐
                                  │   Identical Baseline State   │
                                  │       Snapshot S_0           │
                                  └──────────────┬───────────────┘
                                                 │
                      ┌──────────────────────────┴──────────────────────────┐
                      ▼                                                     ▼
        ┌───────────────────────────┐                         ┌───────────────────────────┐
        │  Branch A: Environment A  │                         │  Branch B: Environment B  │
        │  (Trajectory Paradigm A)  │                         │  (Trajectory Paradigm B)  │
        └─────────────┬─────────────┘                         └─────────────┬─────────────┘
                      │                                                     │
            ┌─────────┴─────────┐                                 ┌─────────┴─────────┐
            ▼                   ▼                                 ▼                   ▼
     ┌─────────────┐     ┌─────────────┐                   ┌─────────────┐     ┌─────────────┐
     │  Branch A1  │     │  Branch A2  │                   │  Branch B1  │     │  Branch B2  │
     │ Full-Memory │     │ Mem-Clamped │                   │ Full-Memory │     │ Mem-Clamped │
     └──────┬──────┘     └──────┬──────┘                   └──────┬──────┘     └──────┬──────┘
            │                   │                                 │                   │
            └─────────┬─────────┘                                 └─────────┬─────────┘
                      ▼                                                     ▼
        ┌───────────────────────────┐                         ┌───────────────────────────┐
        │ Washout & Neutral Probing │                         │ Washout & Neutral Probing │
        │     (Epochs 41 - 50)      │                         │     (Epochs 41 - 50)      │
        └───────────────────────────┘                         └───────────────────────────┘
```

### Các giai đoạn thực nghiệm:

1. **Pha 0: Khởi tạo Trạng thái Đồng nhất (Epoch 0):** Thiết lập trạng thái ban đầu $S_0$ hoàn toàn xác định từ cùng một snapshot cố định.
2. **Pha 1: Phân kỳ Tương tác Dài hạn (Epochs 1 – 30):**
   * Nhánh A và Nhánh B tiếp nhận hai dòng can thiệp tương tác độc lập.
   * **Nguyên tắc Chống Rò rỉ Kích thích (Stimulus Leakage Prevention):** Chuỗi kích thích trong Nhánh A và Nhánh B tuyệt đối **không được mã hóa trước** chiều hướng tin cậy kỳ vọng (expected trust direction), cực tính ngữ nghĩa (semantic polarity), hóa trị cảm xúc (valence), tô pô đích (target topology), hoặc kết quả phát triển kỳ vọng (expected developmental outcome). Bộ sinh kích thích phải được thiết kế hoàn toàn mù (blind) và cân bằng đối trọng (counterbalanced) đối với các yếu tố này.
   * **Trạng thái Kích thích Hiện tại:** Do hiện tại chưa có bộ kích thích nào được thẩm định đáp ứng đầy đủ các tiêu chuẩn nghiêm ngặt trên mà không gây rò rỉ, giao thức chính thức đánh dấu:
     $$\mathbf{STATUS: NO\ VALID\ STIMULUS\ FAMILY\ YET}$$
     *(Nghiêm cấm tự tạo ra một họ kích thích giả định là trung tính chỉ để hoàn thành giao thức).*
3. **Pha 2: Thử thách Đảo ngược / Thích ứng (Revision Challenge, Epochs 31 – 40):** Đảo ngược can thiệp đầu vào để đo lường khả năng điều chỉnh (Adaptation/revision) so với sự trơ lì trạng thái.
4. **Pha 3: Giai đoạn Rửa trôi & Đo lường Trung tính (Washout & Probing, Epochs 41 – 50):** Cả hai nhánh tiếp nhận chuỗi kích thích trung tính chuẩn hóa hoàn toàn giống nhau để kiểm tra sự duy trì phân kỳ trạng thái nội sinh dưới điều kiện kẹp bộ nhớ.

---

## 8. Twin / Counterfactual Design

Nhằm phân tách sự phân kỳ do lịch sử nhân quả với sự ngẫu nhiên, giao thức áp dụng thiết kế song sinh phản thực nghiệm hợp lệ:

1. **Khởi tạo Đồng nhất Tuyệt đối (Identical Initial State):**
   * Cả hai nhánh bắt đầu từ trạng thái bit-exact $S_0$.
   * Bộ sinh số ngẫu nhiên (RNG) được kiểm soát nghiêm ngặt bằng seed xác định.
2. **Điểm Phân nhánh (Branching Point):** Diễn ra chính xác tại $t = 1$.
3. **Ma trận Biến số Kiểm soát Cơ chất Trung tính:**
   * **Biến bắt buộc giữ nguyên:** Cấu hình cơ chất nền tảng, siêu tham số suy luận (temperature = 0.0 hoặc nucleus sampling với seed cố định), nhịp tương tác, dung lượng thông tin bề mặt chuẩn hóa.
   * **Biến được phép khác biệt duy nhất:** Nội dung và cấu trúc nhân quả của chuỗi can thiệp đầu vào trong Pha 1.
4. **Thiết kế Phản thực nghiệm Lịch sử Hợp lệ (Valid Historical Counterfactual Design):**
   * **CẤM TUYỆT ĐỐI việc can thiệp trực tiếp đảo ngược hoặc biến đổi vector trạng thái nội sinh (Do NOT directly flip/mutate internal outcome state).** Thao tác cưỡng bức thay đổi trạng thái nội sinh là phi thực tế và phá hủy tính hợp lệ của phản thực nghiệm lịch sử.
   * **Quy trình Phản thực nghiệm Hợp lệ:**
     - Giữ nguyên trạng thái/snapshot hợp lệ giống hệt nhau tại điểm phân nhánh (Hold the same admissible state snapshot $S_{\text{fork}}$ tại $t = t_{\text{fork}}$, ví dụ $t = 20$).
     - Thay đổi một chuỗi can thiệp/kích thích đầu vào/lịch sử tương lai hợp lệ ($I_{\text{counterfactual}}$ so với $I_{\text{factual}}$).
     - So sánh các nhánh quỹ đạo phân kỳ kết quả ở các bước tiếp theo ($t > t_{\text{fork}}$).
   * Can thiệp phản thực nghiệm phải tác động lên một **nguyên nhân/đầu vào tương tác hợp lệ (admissible cause/input)**, tuyệt đối không trực tiếp sản xuất ra trạng thái kết quả mong đợi.

---

## 9. Memory-Clamp Design

Episodic memory là biến gây nhiễu trung tâm (primary confound). Giao thức thiết lập cơ chế kẹp bộ nhớ theo thuật ngữ cơ chất trung tính (substrate-neutral):

1. **Operationalization:**
   * Vô hiệu hóa hoàn toàn cơ chế tiếp nhận truy xuất bộ nhớ sự kiện (Episodic Retrieval Ingress = OFF).
   * Toàn bộ thông tin lịch sử quá khứ được đưa vào bề mặt tương tác ngoại vi bằng đúng 0 ($K_{\text{retrieved}} = 0$, externally surfaced historical information = 0).
   * Không đưa bất kỳ mẩu ký ức sự kiện hay nhật ký đối thoại nào vào luồng xử lý của cơ chất ngữ nghĩa.
2. **Phân định Hai Điều kiện:**
   * **Condition FM (Full Memory):** Hệ thống được tiếp nhận truy xuất bộ nhớ bình thường. Đóng vai trò là mức trần hành vi (behavioral ceiling).
   * **Condition MC (Memory Clamped):** Hệ thống chỉ vận hành dựa trên các biến trạng thái nội sinh hiện tại và kích thích của lượt hiện tại.
3. **Ranh giới Diễn giải Nhận thức:**
   * Nếu hiệu ứng phân kỳ biến mất dưới Condition MC: Xác nhận hành vi trước đó hoàn toàn do bộ nhớ sự kiện dẫn dắt (Memory-Mediated).
   * Nếu hiệu ứng phân kỳ còn tồn tại dưới Condition MC: Xác nhận hiện tượng **Memory-Clamped State Divergence**.
   * **CẢNH BÁO:** Hiện tượng này đo lường sự lưu giữ qua trung gian trạng thái nội sinh (State-Mediated Persistence), nhưng **TUYỆT ĐỐI KHÔNG TỰ ĐỘNG THIẾT LẬP**:
     - Sự phân hóa phát triển thực thụ (developmental differentiation)
     - Sự nội tâm hóa cấu trúc (structural internalization)
     - Tính độc nhất của quỹ đạo (trajectory uniqueness)
     - Tính cá nhân mới nổi (individuality)
     - Sở thích tự chủ (preference).
   * Những diễn giải này đòi hỏi phải vượt qua toàn bộ hệ thống kiểm chứng đối chứng và thang bậc Claim Ladder.

---

## 10. Internal-State Ingress (P26 C3 Gap Resolution)

Khoảng trống cốt lõi của P26 C3 là biến can thiệp không đi vào quá trình chuyển dịch trạng thái nội sinh do khuyết thiếu đường truyền nội sinh trong thiết bị thử nghiệm ($S_{K, \text{active}} \equiv S_{K, \text{yoked}}$). P27 Protocol định nghĩa đường truyền Ingress hợp lệ theo nguyên tắc trung tính:

```text
                       P26 FAILED PATHWAY (Action Ledger Only)
   Interaction History ──► External Action Ledger ──► Output (Internal S Unchanged)
                                       ▲
                                       │ (P26 C3 Apparatus-Specific Gap)
   ────────────────────────────────────┼─────────────────────────────────────────────
                        P27 ADMISSIBLE INGRESS PATHWAY
   Interaction History
           │
           ▼
   [Admissible Ingress Interface]
           │
           ▼  I_t (Admissible Input Signal)
   ┌────────────────────────────────────────────────────────┐
   │ Internal State Transition System                       │
   │   S_{t+1} = F(S_t, I_t, Θ)                             │
   │                                                        │
   │   [Substrate Attribution = OPEN EMPIRICAL QUESTION]    │
   │   (No researcher-prescribed update formulas for        │
   │    R_t, W_rel, limbic ODE, or semantic graph)          │
   └───────────────────────────┬────────────────────────────┘
                               │
                               ▼
                    Internal State Vector S_{t+1}
                               │
                               ▼
            Observable State Divergence Measurement
```

### Ràng buộc Quản trị và Tính Trung tính Cơ chế:

1. **Research-Only Simulation / Surrogate:** Do mã nguồn sản xuất `src/core/** diff = 0`, `electron/** diff = 0`, `data/** diff = 0` đang bị khóa bất biến, cơ chế Ingress này **CHỈ ĐƯỢC PHÉP ĐẶC TẢ VÀ MÔ PHỎNG TRONG RESEARCH HARNESS CÔ LẬP CỦA P27**. Tuyệt đối không được coi đây là hành vi của môi trường sản xuất (production behavior).
2. **Admissible Ingress $\neq$ Prescribed Mechanism:**
   * Ingress thiết lập quyền truy cập nhân quả hợp lệ (admissible causal access) từ lịch sử tương tác vào hệ thống chuyển dịch trạng thái nội sinh: `Interaction History → Ingress → State Transition`.
   * **CẤM TUYỆT ĐỐI việc nhà nghiên cứu tự ý định nghĩa các phương trình cập nhật cơ chế phát triển (MUST NOT PRESCRIBE DEVELOPMENTAL MECHANISMS).** Nghiêm cấm đưa vào các phương trình áp đặt như:
     - Tự cập nhật trực tiếp $\mathbf{R}_t$ bằng công thức nhà nghiên cứu chọn trước.
     - Tự cập nhật trực tiếp $\mathbf{W}_{\text{rel}}$ bằng các quy tắc tùy ý.
     - Tự tích phân limbic ODE bằng các phương trình gán ép.
     - Tự định nghĩa các phương trình ánh xạ $\Delta I_t$ thành các cơ chế phát triển cụ thể.
   * Ingress chỉ chứng minh rằng tín hiệu có đi vào hệ thống trạng thái nội sinh. **Việc cơ chất nội sinh nào thực sự chuyển dịch và phát triển (limbic ODE, vector quan hệ $\mathbf{R}_t$, ma trận liên kết $\mathbf{W}_{\text{rel}}$, đồ thị ngữ nghĩa, v.v.) là một CÂU HỎI THỰC NGHIỆM MỞ (EMPIRICAL QUESTION), không phải là giả định toán học tiên nghiệm.**

---

## 11. Controls & Null Models

Để loại trừ các yếu tố gây nhiễu hệ thống, giao thức bắt buộc tích hợp 4 mô hình đối chứng:

1. **Yoked Passive Control (Đối chứng Thụ động Khớp cặp Chuẩn hóa):**
   * **Thành phần được khớp cặp (What is matched):** Trình tự kích thích môi trường ngoại vi giống hệt, thời gian/nhịp độ phơi nhiễm tương đương, trạng thái khởi tạo $S_0$ đồng nhất, và lịch trình đo lường quan sát cơ chất trung tính hoàn toàn tương đương giữa nhánh Active và nhánh Yoked.
   * **Thành phần bị chủ động loại bỏ (What is intentionally removed):** Vòng phản hồi đóng giữa hành vi của hệ thống và môi trường tương tác (closed-loop reciprocal feedback). Nhánh Yoked hoàn toàn không có khả năng tác động ngược để làm thay đổi luồng kích thích kế tiếp do môi trường đưa vào; chuỗi kích thích được phát lại dưới dạng vòng lặp mở (open-loop exogenous playback).
   * **Đường truyền nhân quả khác biệt (What causal pathway differs):**
     - Nhánh Active: Vận hành theo chu trình nhân quả đóng hai chiều: $\text{Agent Action}_t \to \text{Environment Response}_{t+1} \to \text{Ingress}_{t+1}$.
     - Nhánh Yoked: Vận hành theo chu trình nhân quả mở một chiều: $\text{Stimulus}_{t+1}$ là chuỗi ngoại sinh độc lập hoàn toàn với phản ứng trước đó của hệ thống tại bước $t$.
   * **Mục đích cô lập nhân tố (Why the comparison isolates the intended factor):** Khớp cặp văn bản hoặc số lượng token thuần túy là không đủ. Sự so sánh này cô lập xem liệu sự phân kỳ quỹ đạo được thúc đẩy bởi lịch sử tương tác tương hỗ vòng lặp đóng nội sinh (endogenous closed-loop interaction history) hay chỉ đơn thuần là kết quả của việc phơi nhiễm thụ động tích lũy trước chuỗi kích thích ngoại vi (passive cumulative exposure).
2. **Temporal Shuffling Control (Đối chứng Hoán vị Thời gian):**
   * Nhánh Shuffled tiếp nhận tập hợp các sự kiện tương tác giống hệt Nhánh Sequential nhưng thứ tự thời gian được xáo trộn ngẫu nhiên.
   * Mục tiêu: Đo lường độ nhạy thứ tự thời gian (**Order Sensitivity**). Hoán vị thời gian **KHÔNG PHẢI LÀ BẰNG CHỨNG NHÂN QUẢ ĐẦY ĐỦ**.
   * So sánh với phân bố hoán vị nền (permutation null distribution) hoặc biên độ tương đương $\delta_{\text{perm, null}}$, không dùng giả thuyết không bằng 0 tuyệt đối.
3. **Random Drift Null Model (Mô hình Không về Trôi dạt Ngẫu nhiên):**
   * Mô phỏng chuyển động Brown trong không gian trạng thái với độ lệch chuẩn khớp với phương sai nội tại của hệ thống.
   * Mục tiêu: Thiết lập ngưỡng phân kỳ nền sinh ra do sai số số học và tính ngẫu nhiên của bộ sinh.
4. **Inductive-Bias / Substrate Baseline Control:**
   * Đánh giá phản ứng của cơ chất cơ sở (Foundation Model / Generator Surrogate) dưới cùng một tập kích thích trung tính mà không có bất kỳ trạng thái nội sinh nào.
   * Mục tiêu: Đo lường thiên kiến sẵn có của mô hình nền tảng đối với các kịch bản kiểm tra.
   * **Phân loại Rõ ràng:** Mô hình nền tảng (LLM/generator) trong harness là một **chi tiết triển khai / công cụ đại diện (implementation surrogate)**, tuyệt đối không phải là một phần của construct lý thuyết P27.

---

## 12. Observables

Giao thức sử dụng các biến quan sát thuộc kiến trúc thực tế của Lucia, tuân thủ nguyên tắc phân định ba cấp độ:

```text
┌────────────────────────────────────────────────────────────────────────┐
│                        DATA LEVEL SEPARATION                           │
├──────────────────────────────┬─────────────────────────────────────────┤
│ Level 1: Measured State      │ Vector số thực thô trích xuất từ bộ nhớ │
│ Level 2: Candidate Mechanism │ Mô hình động lực học giả định           │
│ Level 3: Interpretation      │ Ý nghĩa khái niệm gán cho trạng thái    │
└──────────────────────────────┴─────────────────────────────────────────┘
```

### 12.1 Canonical Relational State Vector

Vector trạng thái quan hệ chuẩn tắc bắt buộc giữ nguyên 4 chiều:

$$\mathbf{R}_t = [R_{\text{fam}}, R_{\text{trust}}, R_{\text{close}}, R_{\text{recip}}]^T \in [0.0, 1.0]^4$$

*(Tuyệt đối không thay thế bằng các chiều không chuẩn như Affinity hoặc Intimacy).*

### 12.2 Các Biến Quan sát Bổ sung (Tách biệt hoàn toàn, không trộn vào $\mathbf{R}_t$)

1. **Limbic / ODE Affective State:** Vector $\mathbf{P}_t = [\text{Pleasure}, \text{Arousal}, \text{Dominance}]^T \in [-1.0, 1.0]^3$.
2. **Homeostatic Energy State:** Đại lượng vô hướng $E_t \in [0.0, 1.0]$ phản ánh mức tiêu hao năng lượng nội tại.
3. **Relational Weight Matrix ($\mathbf{W}_{\text{rel}}$):** Ma trận trọng số liên kết nội sinh $\mathbf{W}_{\text{rel}} \in \mathbb{R}^{4 \times 4}$.
4. **Semantic Topology Metrics:** Bậc phân nhánh trung bình, mật độ liên kết và độ sâu của đồ thị củng cố ngữ nghĩa P23-E.
5. **SDM Activation Statistics:** Số lượng địa chỉ cứng được kích hoạt và entropy phân bố kích hoạt trong bộ nhớ phân tán thưa.

### 12.3 Danh mục Biến Bị CẤM Tuyệt đối

* Độ tương đồng chuỗi ký tự trong prompt (Prompt text similarity).
* Độ trễ phần cứng (CPU / GPU inference latency).
* Mức độ hài lòng hoặc đánh giá chủ quan của người dùng (User satisfaction ratings).
* Thời lượng phiên tương tác (User engagement time).
* Độ trôi chảy ngôn ngữ hội thoại (Conversational fluency / perplexity).

---

## 13. Primary Endpoint

### 13.1 Định nghĩa Toán học

Primary Endpoint của P27 được xác định là một **biến quan sát thực nghiệm (Observable)**: **Khoảng cách Phân kỳ Trạng thái Dưới Điều kiện Kẹp Bộ nhớ (Memory-Clamped State Divergence - $\mathcal{D}_{\text{MC}}$)** tại Pha Rửa trôi Trung tính ($t = T_{\text{washout}}$):

$$\mathcal{D}_{\text{MC}} = \Vert\mathbf{R}_{T_{\text{washout}}}(\text{Branch}_A \mid \text{MC}) - \mathbf{R}_{T_{\text{washout}}}(\text{Branch}_B \mid \text{MC})\Vert_2$$

### 13.2 Đặc tả Đo lường và Giới hạn Diễn giải

* **Bản chất Chỉ số:** Đây là một biến quan sát thực nghiệm đo lường khoảng cách Euclidean giữa hai vector trạng thái quan hệ 4 chiều chuẩn tắc.
* **Ý nghĩa Đo lường:** Đo lường sự phân kỳ trạng thái bền vững dưới điều kiện kẹp bộ nhớ (persistent state divergence under memory-clamped conditions).
* **Ranh giới Diễn giải BẮT BUỘC:** Chỉ số này **TUYỆT ĐỐI KHÔNG TỰ BẢN THÂN NÓ THIẾT LẬP**:
  - Sự phân hóa phát triển (Developmental differentiation)
  - Sự nội tâm hóa cấu trúc (Structural internalization)
  - Tính độc nhất của quỹ đạo (Trajectory uniqueness)
  - Tính cá nhân mới nổi (Individuality)
  - Sở thích tự chủ (Preference).
* **Yêu cầu Xác thực:** Những diễn giải trên đòi hỏi toàn bộ hệ thống kiểm chứng đối chứng và phải tuân thủ nghiêm ngặt thang bậc Claim Ladder.
* **Giả thuyết Không ($H_0$):** $\mathcal{D}_{\text{MC}} \le \mathcal{D}_{\text{null}}$ (Sự khác biệt không vượt qua phân kỳ ngẫu nhiên của mô hình trôi dạt).
* **Giả thuyết Thay thế ($H_1$):** $\mathcal{D}_{\text{MC}} > \mathcal{D}_{\text{null}} + \delta_{\text{min}}$.
* **Trạng thái Hiệu chuẩn:** `CALIBRATION REQUIRED BEFORE CONFIRMATORY RUN` (Ngưỡng $\delta_{\text{min}}$ và $\mathcal{D}_{\text{null}}$ phải được chuẩn hóa qua đợt chạy hiệu chuẩn độc lập; cấm tự ý ấn định thông số).

---

## 14. Secondary Endpoints

| Endpoint | Ký hiệu | Construct đại diện | Observable đo lường | Giả thuyết Không ($H_0$) | Ranh giới Diễn giải (Interpretation Boundary) |
| --- | --- | --- | --- | --- | --- |
| **Trajectory Directionality / Path Efficiency Index** | $\mathcal{E}_{\text{path}}$ | Candidate Geometric Observable | Tỷ số dịch chuyển/tổng chiều dài: $\frac{\Vert\mathbf{R}_T - \mathbf{R}_0\Vert_2}{\sum \Vert\Delta \mathbf{R}\Vert_2}$ | $\mathcal{E}_{\text{path}} \le \mathcal{E}_{\text{random}}$ | Chỉ đo tính định hướng hình học đường đi; TUYỆT ĐỐI KHÔNG ĐỒNG NHẤT với developmental coherence. |
| **Temporal Permutation Gap** | $\Delta_{\text{perm}}$ | Order Sensitivity (Candidate Observable) | $\Vert\mathbf{R}_T(\text{Sequential}) - \mathbf{R}_T(\text{Permuted})\Vert_2$ | $\Delta_{\text{perm}} \le \delta_{\text{perm, null}}$ | Chỉ đo độ nhạy thứ tự thời gian; KHÔNG PHẢI LÀ BẰNG CHỨNG NHÂN QUẢ (NOT CAUSAL PROOF). |
| **Memory-Clamp Attenuation Ratio** | $\mathcal{R}_{\text{atten}}$ | Descriptive Memory Attenuation | $1 - \frac{\mathcal{D}_{\text{MC}}}{\mathcal{D}_{\text{FM}}}$ | $\mathcal{R}_{\text{atten}} \ge 1.0 - \epsilon$ (Hoàn toàn do memory) | Đo lường mức độ suy giảm do kẹp bộ nhớ (Descriptive comparison only); KHÔNG DIỄN GIẢI NHƯ CAUSAL MEDIATION. |
| **Adaptation Plasticity Score** | $\mathcal{A}_{\text{plast}}$ | Adaptation / Revision (F) | Tốc độ chuyển dịch trạng thái khi tiếp nhận can thiệp đảo ngược trong Pha 2 | Không đổi hướng ($\Delta \mathbf{R} \cdot \mathbf{v}_{\text{rev}} \le 0$) | Đo tính dẻo cấu trúc; không chứng minh sự phản tư nhận thức. |
| **Washout Decay Half-Life** | $\tau_{1/2}$ | State Continuity & Dissipation (A) | Thời gian bán rã của độ lệch trạng thái trong Pha Washout | $\tau_{1/2} \le \tau_{\text{immediate}}$ (Tiêu tán tức thời) | Đo tính trễ lịch sử (hysteresis); không chứng minh ký ức tự thân. |

---

## 15. Statistical Analysis Plan

### 15.1 Kế hoạch Đăng ký Trước (Preregistration Specification)

* **Đơn vị Phân tích:** Cặp quỹ đạo song sinh ghép cặp độc lập (Paired twin trajectory pair xuất phát từ cùng snapshot $S_0$ và cùng seed ngẫu nhiên).
* **Cỡ mẫu (Sample Size):**
  * Giá trị danh định ban đầu: $N = 30$ cặp tái lập độc lập.
  * **Trạng thái:** `SAMPLE SIZE & POWER CALIBRATION REQUIRED`. Giá trị $N=30$ chỉ là giả định thăm dò ban đầu; cỡ mẫu chính thức bắt buộc phải được tính toán dựa trên phân tích lực thống kê (statistical power analysis $\ge 0.80$ ở $\alpha = 0.01$) sau khi hoàn tất giai đoạn hiệu chuẩn.
* **Chiến lược Seed:** $S_{\text{seed}}$ được gán cố định trước khi thực thi. Mỗi seed chi phối toàn bộ quá trình sinh số ngẫu nhiên của cả hai nhánh song sinh tương ứng.
* **Phương pháp Kiểm định Thống kê Phù hợp (Paired Continuous Endpoint):**
  * Vì $\mathcal{D}_{\text{MC}}$ trong thiết kế song sinh là đại lượng liên tục ghép cặp (paired continuous endpoint), phương pháp kiểm định chính thức là:
    - **Phép kiểm định hoán vị ghép cặp (Paired Permutation Test, $B = 10,000$ resamples)** trên độ lệch hiệu số khoảng cách: $d_i = \mathcal{D}_{\text{MC}, i} - \mathcal{D}_{\text{null}, i}$.
    - **Kích thước hiệu ứng liên tục ghép cặp:** Báo cáo Paired Cohen's $d_z$ (hoặc Mean/Median Paired Difference) kèm theo khoảng tin cậy bootstrap hiệu chỉnh độ lệch (BCa 95% Confidence Interval). Không sử dụng Cliff's Delta (vốn là thước đo phi tham số không ghép cặp).
* **Xử lý So sánh Đa biến:** Kiểm soát tỷ lệ sai số giả mạo (False Discovery Rate - FDR) bằng thủ tục Benjamini-Hochberg ở mức $q = 0.05$ trên toàn bộ các secondary endpoints.
* **Quy trình Hiệu chuẩn Tiền Thực nghiệm (Pre-Trial Calibration Requirements):**
  * **CẢNH BÁO QUAN TRỌNG:** Mẫu hiệu chuẩn nhỏ (ví dụ $N=5$) **TUYỆT ĐỐI KHÔNG ĐƯỢC COI LÀ ĐÃ XÁC LẬP NGƯỠNG NHIỄU KHẲNG ĐỊNH (a small calibration sample of N=5 cannot automatically establish a confirmatory noise bound)**. Mẫu nhỏ chỉ có giá trị thăm dò phương sai số học và kiểm tra độ ổn định của hệ thống.
  * Để thiết lập ngưỡng nhiễu khẳng định ($\mathcal{D}_{\text{null}}$, $\delta_{\text{perm, null}}$, $\delta_{\text{min}}$), bắt buộc phải có một đợt hiệu chuẩn có quy mô phù hợp.
  * **Đóng băng Tham số:** Toàn bộ tham số phân tán, ngưỡng nhiễu, biên độ tương đương và cỡ mẫu chính thức phải được **ĐÓNG BĂNG HOÀN TOÀN (FROZEN)** trước khi bắt đầu thử nghiệm khẳng định (confirmatory analysis).
* **Quy tắc Dừng sớm (Stopping Rule):** Cấm tuyệt đối việc dừng sớm hoặc quan sát dữ liệu giữa chừng (**Strictly NO interim peeking**). Toàn bộ dữ liệu mô phỏng phải hoàn tất $100\%$ trước khi mở khóa phân tích.
* **Quy tắc Thông số Chưa Chứng minh:** Bất kỳ tham số nào chưa có cơ sở thực nghiệm chứng minh bắt buộc phải gắn nhãn: `CALIBRATION REQUIRED`. Tuyệt đối không được chế tạo lý do biện minh giả tạo.

---

## 16. Falsification Matrix

Bảng tiêu chí phản nghiệm quy định các điều kiện mà nếu xuất hiện, giả thuyết nghiên cứu sẽ bị bác bỏ:

| Giả thuyết / Tuyên bố | Observable | Kết quả Phản nghiệm (Falsifying Result) | Kết luận Được phép | Kết luận BỊ CẤM |
| --- | --- | --- | --- | --- |
| **$H_1$: Memory-Clamped State Divergence** | $\mathcal{D}_{\text{MC}}$ | $\mathcal{D}_{\text{MC}} \le \mathcal{D}_{\text{null}}$ ($p > 0.05$) hoặc $\mathcal{R}_{\text{atten}} \ge 0.95$ | **No evidence for memory-clamped state divergence under the tested operationalization.** | CẤM KẾT LUẬN: "P27 developmental trajectory is falsified completely." |
| **$H_1$: Order Sensitivity** | $\Delta_{\text{perm}}$ | $\Delta_{\text{perm}} \le \delta_{\text{perm, null}}$ ($p > 0.05$ so với phân bố hoán vị) | Không có bằng chứng cho thấy thứ tự thời gian tạo ra sự phân kỳ trạng thái nội sinh. | CẤM KẾT LUẬN: "Lucia không có khả năng học tập theo thời gian." |
| **$H_1$: Causal Developmental Dependence** | Counterfactual Branching Distance | Không vượt qua $\delta_{\text{causal, null}}$ khi can thiệp trên đầu vào phản thực nghiệm | Không có bằng chứng về sự phụ thuộc phát triển nhân quả từ can thiệp đầu vào. | CẤM KẾT LUẬN: "Trạng thái của hệ thống hoàn toàn ngẫu nhiên." |
| **$H_1$: State Retention Post-Washout** | $\tau_{1/2}$ | $\tau_{1/2} \le \tau_{\text{immediate}}$ (Trạng thái tiêu tán về baseline trong $\le 2$ epochs) | Bác bỏ cơ chế duy trì trạng thái dài hạn đối với biến quan sát tương ứng. | CẤM KẾT LUẬN: "Toàn bộ cấu trúc nội sinh của Lucia vô giá trị." |
| **$H_1$: Adaptation / Plasticity** | $\mathcal{A}_{\text{plast}}$ | Trạng thái tiếp tục trôi theo hướng cũ bất chấp can thiệp đảo ngược | Bác bỏ tính dẻo thích ứng; hệ thống bị bão hòa hoặc đông cứng trạng thái. | CẤM KẾT LUẬN: "Hệ thống sở hữu niềm tin kiên định bất biến." |

---

## 17. Claim Ladder & Interpretation Rules

```text
[BỊ KHÓA / BẬC CẤM] ──────► Level 6: Autonomous Preference (Sở thích tự chủ)
[BỊ KHÓA / BẬC CẤM] ──────► Level 5: Emergent Individuality (Tính cá nhân mới nổi)
─────────────────────────────────────────────────────────────────────────── ◄── TRAN PROTOCOL
[UNRESOLVED / RESEARCH] ──► Level 4: Endogenous Structural/State Asymmetry
[MỤC TIÊU CỐT LÕI P27]  ──► Level 3: Causal Developmental Dependence
[MỤC TIÊU CỐT LÕI P27]  ──► Level 2: Persistent Differentiation (Under Memory Clamp)
[ĐÃ PRE-VALIDATE]      ──► Level 1: History Dependence
[KIẾN TRÚC HIỆN CÓ]    ──► Level 0: State Continuity
```

### Quy tắc Nâng bậc Bằng chứng (Evidence Promotion Rules):

1. **Level 0 $\to$ Level 1:** Đã đạt được từ P26 C1 (State Continuity & History Dependence cơ bản).
2. **Level 1 $\to$ Level 2 (Persistent Differentiation):** Đòi hỏi $\mathcal{D}_{\text{MC}} > \mathcal{D}_{\text{null}} + \delta_{\text{min}}$ với $p < 0.01$ dưới điều kiện Memory Clamped trong Pha Washout.
3. **Level 2 $\to$ Level 3 (Causal Developmental Dependence):**
   * Đòi hỏi vượt qua đồng thời Level 2 VÀ có bằng chứng nhân quả từ thiết kế can thiệp phản thực nghiệm hợp lệ (preregistered intervention contrast trên đầu vào tương tác tại cùng snapshot $S_{\text{fork}}$).
   * Kèm theo xác nhận tính nhạy thứ tự thời gian ($\Delta_{\text{perm}} > \delta_{\text{perm, null}}$).
   * **Lưu ý Bắt buộc:** Phép hoán vị thời gian thuần túy chỉ xác lập tính nhạy thứ tự (Order Sensitivity), **KHÔNG ĐỦ** để tự động nâng lên Level 3 nếu thiếu đối chứng can thiệp phản thực nghiệm.
4. **Level 3 $\to$ Level 4 (Endogenous Structural/State Asymmetry):** Yêu cầu chứng minh ma trận $\mathbf{W}_{\text{rel}}$ hoặc cấu trúc đồ thị nội sinh phân kỳ không đối xứng độc lập với đầu vào (Hiện tại ở trạng thái `UNRESOLVED / RESEARCH`).
5. **CẤM NÂNG BẬC TỪ LEVEL 3/4 LÊN LEVEL 5/6:** Dữ liệu thực nghiệm của giao thức này **TUYỆT ĐỐI KHÔNG CUNG CẤP CƠ SỞ** để tuyên bố Emergent Individuality (Level 5) hoặc Autonomous Preference (Level 6). Hai bậc này nằm ngoài phạm vi nghiên cứu của P27.

---

## 18. Reproducibility & Fail-Closed Requirements

Nhằm đảm bảo tính tái lập khoa học và bảo vệ mã nguồn, giao thức áp dụng cơ chế đóng-khi-lỗi (Fail-Closed):

1. **Khóa Bất biến Giao thức:** Văn bản thiết kế giao thức này mang mã băm nhận dạng bất biến một khi được thông qua.
2. **Tập Kịch bản Đóng băng (Frozen Stimulus Manifest):** Toàn bộ các chuỗi văn bản kích thích của Nhánh A, Nhánh B và Pha Washout phải được thẩm định không rò rỉ và xuất thành tệp JSON cố định trước khi chạy thử nghiệm khẳng định.
3. **Bảo tồn Dữ liệu Telemetry Thô:** Mọi tensor trạng thái ở từng bước thời gian phải được ghi nhận nguyên vẹn dạng nhị phân (`.npz` hoặc `.parquet`) trong thư mục artifacts của P27.
4. **Phân tách Dữ liệu Phái sinh:** Mã phân tích thống kê chỉ được đọc dữ liệu thô, không được ghi đè hoặc can thiệp ngược lại harness.
5. **FAIL-CLOSED AUDIT GATE (Codebase & Genesis Guardrail):**
   * Trước và sau mỗi đợt chạy mô phỏng, harness nghiên cứu bắt buộc thực hiện kiểm tra kiểm toán mã nguồn:

$$\text{git diff --stat src/core electron data}$$

   * **Điều kiện Bắt buộc:**
     - `src/core/** diff = 0`
     - `electron/** diff = 0`
     - `data/** diff = 0`
     - `data/profile.json` phải giữ nguyên bit-exact: `{"is_onboarded": false}`
   * **Nếu phát hiện bất kỳ sự thay đổi nào ($\text{diff} \neq 0$) hoặc trạng thái Genesis bị vi phạm:** Toàn bộ kết quả thử nghiệm ngay lập tức bị **HỦY BỎ HIỆU LỰC (INVALIDATED)**, quy trình dừng khẩn cấp và hệ thống trả về trạng thái lỗi:
     $$\mathbf{FAIL-CLOSED: UNAUTHORIZED\_CODEBASE\_MUTATION\_OR\_GENESIS\_BREACH}$$

---

## 19. Research Isolation Boundary

Quy định cấu trúc tệp cục bộ phục vụ nghiên cứu P27:

```text
Lucia/
├── docs/PhaseDocs/Lucia-phase27-Personalized_Individual_Trajectory/
│   ├── INDEX.md
│   ├── P27_SCIENTIFIC_CLOSURE_REPORT.md
│   ├── P27_RESEARCH_PROTOCOL_DESIGN.md       <-- (Tài liệu này)
│   └── evaluation_artifacts/                  <-- (Khu vực lưu trữ duy nhất cho P27)
│       ├── frozen_manifests/
│       │   └── (STATUS: NO VALID STIMULUS FAMILY YET)
│       ├── raw_telemetry/
│       └── analysis_reports/
├── src/core/                                  <-- DIFF = 0 (STRICTLY FORBIDDEN)
├── electron/                                  <-- DIFF = 0 (STRICTLY FORBIDDEN)
├── data/                                      <-- DIFF = 0 (STRICTLY FORBIDDEN)
└── data/profile.json                          <-- {"is_onboarded": false} (LOCKED)
```

Nghiêm cấm tạo bất kỳ thư mục nào tại cấp root như `/evaluation`, `/experiments`, hoặc `/test_harness`.

---

## 20. Decision Gates

```text
┌────────────────────────────────────────────────────────────────────────┐
│                        PROTOCOL DECISION GATES                         │
├────────┬──────────────────────────┬────────────────────────────────────┤
│ Gate A │ Protocol Validity        │ REVISION INTEGRATED (REVIEW PENDING│
│        │                          │  FOR FINAL HARNESS SPEC TRANSITION)│
│ Gate B │ Harness Readiness        │ LOCKED (Chờ hoàn tất Gate A & Spec)│
│ Gate C │ Confirmatory Readiness   │ CALIBRATION REQUIRED FIRST         │
│ Gate D │ Evidence Interpretation  │ STRICT CEILING AT LEVEL 3          │
│ Gate E │ Architecture Eligibility │ STRICTLY LOCKED (NOT ELIGIBLE)     │
└────────┴──────────────────────────┴────────────────────────────────────┘
```

* **Gate A (Protocol Validity):** Đánh giá tính chặt chẽ về mặt lý thuyết, kiểm soát biến gây nhiễu, phân định rõ ràng biến quan sát với cơ chế và diễn giải, và tuân thủ ranh giới quản trị.
* **Gate B (Harness Readiness):** Kiểm tra khả năng triển khai harness cô lập hoàn toàn không đụng đến production (`src/core/** diff = 0`, `electron/** diff = 0`, `data/** diff = 0`). Chỉ mở sau khi Gate A đạt yêu cầu và Harness Specification được phê duyệt.
* **Gate C (Confirmatory Readiness):** Yêu cầu chạy đợt hiệu chuẩn độc lập (Pre-Trial Calibration Phase) để xác định tham số phân tán, kiểm định lực thống kê, và đóng băng các ngưỡng nhiễu trước khi chạy thử nghiệm khẳng định.
* **Gate D (Evidence Interpretation):** Giới hạn diễn giải dữ liệu thu được theo đúng Claim Ladder (tối đa Level 3; Level 5 và Level 6 bị cấm tuyệt đối).
* **Gate E (Architecture Eligibility):** Đóng chặt hoàn toàn. Giao thức này không cấp quyền cho bất kỳ sự sửa đổi kiến trúc nào.

---

## 21. Known Limitations

1. **Chưa có Họ Kích thích Đạt chuẩn (`NO VALID STIMULUS FAMILY YET`):** Chưa có bộ kích thích tương tác nào được chứng minh là phi rò rỉ (không mã hóa trước cực tính, hóa trị, hay hướng tin cậy). Cần thiết kế và kiểm định họ kích thích trong bước tiếp theo trước khi có thể chạy thử nghiệm.
2. **Cơ chất Nền tảng chỉ là Công cụ Đại diện (Foundation Model as Harness Surrogate):** Mô hình nền tảng trong harness chỉ đóng vai trò là một công cụ thực nghiệm đại diện (implementation surrogate) để kiểm tra giao thức, không cấu thành bản chất lý thuyết của P27.
3. **Cỡ mẫu và Ngưỡng Nhiễu Chưa Hiệu chuẩn:** Cỡ mẫu $N=30$ và các ngưỡng phân kỳ hiện tại chưa được hiệu chuẩn qua phân tích lực thống kê thực nghiệm. Cần một giai đoạn hiệu chuẩn độc lập trước đợt chạy khẳng định.
4. **Giới hạn Không gian Trạng thái 4D:** Không gian trạng thái 4 chiều $\mathbf{R}_t$ có thể chỉ phản ánh một phần các khía cạnh phân hóa động lực học của hệ thống.

---

## 22. Open Questions

1. **`UNRESOLVED: Admissible Ingress Substrate Plasticity`**
   * *Mô tả:* Khi tín hiệu đi qua giao diện Ingress hợp lệ, thành phần nội sinh nào sẽ thể hiện tính dẻo bền vững (limbic ODE, $\mathbf{R}_t$, $\mathbf{W}_{\text{rel}}$, hay semantic graph), và liệu có xảy ra hiện tượng bão hòa biên hay không?
   * *Biện pháp:* Đánh giá thực nghiệm trong đợt chạy hiệu chuẩn (Calibration Run); không áp đặt công thức tiên nghiệm.
2. **`UNRESOLVED: Non-Leaky Stimulus Family Generation`**
   * *Mô tả:* Làm thế nào để tự động sinh ra các chuỗi can thiệp dài hạn phân nhánh nhưng hoàn toàn cân bằng đối trọng, không rò rỉ cực tính ngữ nghĩa hay hóa trị cảm xúc?
   * *Trạng thái:* `STATUS: NO VALID STIMULUS FAMILY YET`. Cần giải quyết trong Harness Specification.
3. **`UNRESOLVED: Substrate-Neutral Behavioral Readout Calibration`**
   * *Mô tả:* Khi kẹp bộ nhớ sự kiện, mức độ mà trạng thái nội sinh tác động lên các biến quan sát hành vi trung tính trong bài kiểm tra thăm dò là bao nhiêu?
   * *Trạng thái:* `CALIBRATION REQUIRED`. Phụ thuộc vào việc hiệu chuẩn cơ chế chiếu trạng thái trong harness nghiên cứu.

---

## 23. Protocol Readiness Verdict

```text
================================================================================
                    P27 RESEARCH PROTOCOL DESIGN VERDICT
================================================================================
Document Status: REVISED PROTOCOL SPECIFICATION (11 CORRECTIONS INTEGRATED)
Governance Compliance: FULLY COMPLIANT (ZERO CODEBASE MUTATION)

Gate A (Protocol Validity): REVISION INTEGRATED (Ready for Review / Transition)
Gate B (Harness Readiness): LOCKED (Pending Gate A sign-off & Harness Spec)
Gate C (Confirmatory Readiness): CALIBRATION REQUIRED FIRST
Gate D (Evidence Ceiling): LEVEL 3 (Causal Developmental Dependence)
Gate E (Architecture Gate): NOT ELIGIBLE (STRICTLY FORBIDDEN)

P26 Claim C: NOT ESTABLISHED
P26 Claim D: NOT ESTABLISHED
P27 Research Status: ELIGIBLE
P27 Architecture: NOT ELIGIBLE
P27 Production Status: FORBIDDEN
Genesis Impact: NONE (LOCKED — data/profile.json == {"is_onboarded": false})
Codebase Diffs: src/core/** diff = 0 | electron/** diff = 0 | data/** diff = 0
P26-R4: NOT REQUIRED / NOT AUTHORIZED
P28 Status: NOT OPENED / NOT AUTHORIZED
Stimulus Family Status: NO VALID STIMULUS FAMILY YET
Primary Endpoint: Memory-Clamped State Divergence (Observable Only)
Secondary Endpoint Renamed: Memory-Clamp Attenuation Ratio (Descriptive Only)
Secondary Endpoint Renamed: Trajectory Directionality / Path Efficiency Index
Statistical Design: Paired Continuous Permutation Test (Calibration Required)
Counterfactual Design: Valid Counterfactual Input Branching at Fork Snapshot
================================================================================
```