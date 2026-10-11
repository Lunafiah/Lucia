# P27-H2 — Calibration Methodology Specification

```text
Document Type: RESEARCH CALIBRATION METHODOLOGY SPECIFICATION
Document Identifier: DOC-P27-H2-001
Status: METHODOLOGY SPECIFIED — GATE H2 FORMALLY BLOCKED (CALIBRATION INSUFFICIENT)
Target Path: docs/PhaseDocs/Lucia-phase27-Personalized_Individual_Trajectory/P27_H2_CALIBRATION_METHODOLOGY.md
Authority: RESEARCH ARM (Gemini / Antigravity) → SUBMITTED FOR GOVERNANCE REVIEW (Ciah / Human Owner)
Preceding Canonical Baselines:
  - P27_RESEARCH_CHARTER.md
  - P27_RESEARCH_PROTOCOL_DESIGN.md (DOC-P27-PROTOCOL-001, Gate A Passed)
  - P27_HARNESS_SPECIFICATION.md (DOC-P27-HARNESS-001, Harness Not Yet Implementable)
  - P27_H1_STIMULUS_VALIDITY_INVESTIGATION.md (DOC-P27-H1-001, Gate H1 Blocked)
  - P26→P27 Dependency and Boundary Audit (DOC-P26-007)
  - P27_SCIENTIFIC_CLOSURE_REPORT.md (DOC-P27-001)
Canonical Governance Status:
  Gate H1 Status: BLOCKED — NO VALID STIMULUS FAMILY IDENTIFIED
  Gate H2 Status: BLOCKED — CALIBRATION INSUFFICIENT (SPECIFICATION COMPLETE / EXECUTION BLOCKED)
  Gate H5 Status: STRICTLY LOCKED (BLOCKED BY H1 & H2)
  P26 Claim C / Claim D: NOT ESTABLISHED
  P27 Research Status: ELIGIBLE (SPECIFICATION ONLY)
  P27 Harness Implementation / Execution: STRICTLY PROHIBITED
  P27 Production Status: FORBIDDEN
  Genesis Gate: LOCKED (data/profile.json == {"is_onboarded": false} bit-exact)
  Diff Boundaries: src/core/** diff = 0 | electron/** diff = 0 | data/** diff = 0
```

---

## 1. Executive Summary

Tài liệu này xác lập đặc tả phương pháp luận hiệu chuẩn nghiên cứu (**Research Calibration Methodology Specification**) cho Cổng Quyết định H2 (Gate H2) thuộc Phase 27 (*Personalized Individual Trajectory*). Sau khi Giao thức Nghiên cứu P27 vượt qua Gate A ([`P27_RESEARCH_PROTOCOL_DESIGN.md`](file:///c:/Users/Lunafiah/Desktop/My_project/Lucia/docs/PhaseDocs/Lucia-phase27-Personalized_Individual_Trajectory/P27_RESEARCH_PROTOCOL_DESIGN.md)) và cuộc thẩm định nhận thức luận Gate H1 ([`P27_H1_STIMULUS_VALIDITY_INVESTIGATION.md`](file:///c:/Users/Lunafiah/Desktop/My_project/Lucia/docs/PhaseDocs/Lucia-phase27-Personalized_Individual_Trajectory/P27_H1_STIMULUS_VALIDITY_INVESTIGATION.md)) xác định phán quyết `NO VALID STIMULUS FAMILY IDENTIFIED`, tài liệu này giải quyết điểm nghẽn phương pháp luận thứ hai: **Cơ sở hiệu chuẩn đo lường và thống kê (Calibration Validity)**.

Nhiệm vụ của nghiên cứu H2 là thiết lập một phương pháp luận khoa học chặt chẽ, độc lập hoàn toàn với bài toán kích thích H1, nhằm trả lời: **Nếu trong tương lai xuất hiện một đường dẫn nhận diện kích thích hợp thức, hệ thống đo lường của Lucia cần được hiệu chuẩn như thế nào về nhiễu kỹ thuật, phương sai ngẫu nhiên, phân bố không (null distribution), biên độ hiệu ứng tối thiểu có thể phát hiện ($\delta_{\text{min}}$), ngưỡng tương đương ($\delta_{\text{equiv}}$), và cỡ mẫu ($N$) trước khi tiến hành bất kỳ thử nghiệm xác nhận (confirmatory experiment) nào?**

### Các Phát hiện và Nguyên tắc Cốt lõi:
1. **Phân tách 3 Tầng Hiệu chuẩn Độc lập:**
   * **Tầng A (Engineering Calibration):** Đặc tính hóa nhiễu số học dấu phẩy động, sai số tích phân ODE, nhiễu đo đạc từ xa (telemetry jitter), và phương sai ngẫu nhiên giữa các lần chạy giống hệt nhau. Tầng này thuần túy mô tả công cụ đo, tuyệt đối không thiết lập hiệu ứng khoa học.
   * **Tầng B (Null Calibration):** Xây dựng các phân bố không chuẩn tắc (Random-Drift Null, Temporal-Order Null, State-Matched Null, Measurement-Only Null) ứng với các giả thuyết nhân quả tường minh.
   * **Tầng C (Confirmatory Parameter Freeze):** Đóng băng tiên nghiệm toàn bộ tham số thống kê trước khi tiếp cận dữ liệu thử nghiệm xác nhận; tuyệt đối cấm điều chỉnh ngưỡng post-hoc.
2. **Khử Bỏ Các Ngưỡng Số Học Tùy Tiện (De-manufacturing Manufactured Numbers):**
   * Toàn bộ các giá trị định lượng xuất hiện trong các bản thảo sơ bộ ($N = 30$, $N_{\text{pilot}} = 5$, $\delta_{\text{noise}} = 0.02$, $\delta_{\text{min}} = 0.05$, $\delta_{\text{perm, null}} = 0.03$, $\delta_{\text{equiv}} = 0.03$) đều bị tước bỏ tư cách chuẩn tắc và được tái phân loại chính xác thành `REQUIRES CALIBRATION` hoặc `NOT IDENTIFIABLE YET`. Không có bất kỳ ngưỡng số học nào được phép tự ý bịa đặt.
3. **Phân định Rạch ròi Giữa Phát hiện Thống kê và Ý nghĩa Phát triển:**
   $$\text{Statistical Detectability} \;\neq\; \text{Construct Validity} \;\neq\; \text{Scientific Importance}$$
   Một hiệu ứng phân kỳ trạng thái vượt qua ngưỡng phát hiện thống kê ($\mathcal{D}_{\text{MC}} > \delta_{\text{min}}$) **tuyệt đối không tự động đồng nhất** với sự hình thành quỹ đạo cá nhân hóa có ý nghĩa cấu trúc hay tâm lý học.
4. **Tính Độc lập Tuyệt đối Giữa H1 và H2:**
   * $H_1$ giải quyết tính hợp thức của kích thích ngoại sinh; $H_2$ giải quyết tính hiệu chuẩn của hệ thống đo lường nội sinh.
   * Tuyệt đối không được sử dụng một họ kích thích đã bị H1 bác bỏ (ví dụ: các đoạn hội thoại mơ hồ rò rỉ thiên kiến) để thực hiện hiệu chuẩn H2.
5. **Phán quyết Chính thức Gate H2:**
   $$\mathbf{H2 = METHODOLOGICALLY\; SPECIFIED\; (DESIGN-READY)}$$
   $$\mathbf{H2\; GATE = BLOCKED\; /\; CALIBRATION\; INSUFFICIENT}$$
   *Nguyên tắc Ranh giới Cốt tử:* **"H2 methodology is design-ready, but empirical calibration is not established."** Phương pháp luận hiệu chuẩn đã được xác lập hoàn chỉnh ở cấp độ đặc tả, nhưng việc thực thi hiệu chuẩn thực nghiệm bị **KHÓA CHẶT (BLOCKED)** do thiếu cơ chất kích thích hợp thức (H1) và thiếu dữ liệu đo đạc độc lập. Do đó, Gate H5 (Ủy quyền triển khai Harness) tiếp tục bị **KHÓA BẤT BIẾN (LOCKED)**.

---

## 2. H2 Research Question & Epistemic Positioning

### 2.1 Câu hỏi Nghiên cứu Chuẩn tắc

Câu hỏi nghiên cứu định hướng thiết kế H2 được phát biểu chuẩn xác như sau:

> **"Nếu một đường dẫn nhận diện thực nghiệm hợp thức cho P27 xuất hiện trong tương lai, liệu Lucia có sở hữu một phương pháp luận có thể bảo vệ được về mặt khoa học để ước lượng nhiễu đo lường, phương sai ngẫu nhiên của hệ thống, phân bố phân kỳ không (null divergence), biên độ hiệu ứng tối thiểu có thể phát hiện ($\delta_{\text{min}}$), ngưỡng tương đương ($\delta_{\text{equiv}}$), và cỡ mẫu cần thiết ($N$) trước khi tiến hành thực nghiệm xác nhận hay không?"**

### 2.2 Ranh giới Nhận thức luận và Phạm vi Tài liệu
* Tài liệu này là một **đặc tả phương pháp luận nghiên cứu (research methodology specification only)**.
* Tài liệu **KHÔNG THỰC HIỆN** việc chạy hiệu chuẩn thực tế, không sinh dữ liệu số, không tạo mã nguồn harness, và không can thiệp vào bất kỳ thành phần nào của mã nguồn sản xuất (`src/core/** diff = 0`, `electron/** diff = 0`, `data/** diff = 0`).
* Nghiên cứu H2 được tiến hành một cách **độc lập với tình trạng bế tắc của H1**. Chúng tôi không cố gắng giả định rằng H1 đã được giải quyết để hợp thức hóa H2, mà phân tích cấu trúc hiệu chuẩn như một điều kiện tiên quyết phương pháp luận độc lập.

---

## 3. Governance and Scope

### 3.1 Ma trận Tuân thủ Quản trị (Governance Compliance Matrix)

```text
┌────────────────────────────────────────────────────────────────────────┐
│                   P27-H2 GOVERNANCE COMPLIANCE MATRIX                  │
├──────────────────────────────┬─────────────────────────────────────────┤
│ Target Document              │ P27_H2_CALIBRATION_METHODOLOGY.md       │
│ Document Authority           │ Research Arm Specification Only         │
│ Production Codebase Diff     │ Exactly: src/core/** diff = 0           │
│                              │          electron/** diff = 0           │
│                              │          data/** diff = 0               │
│ Genesis Gate Status          │ LOCKED (data/profile.json ==            │
│                              │   {"is_onboarded": false} bit-exact)    │
│ Gate H1 Status               │ BLOCKED — NO VALID STIMULUS IDENTIFIED  │
│ Gate H2 Status               │ BLOCKED — CALIBRATION INSUFFICIENT      │
│ Gate H5 Status               │ STRICTLY LOCKED                         │
│ P26 Claims C & D             │ NOT ESTABLISHED                         │
│ Phase 28 / P26-R4 Creation   │ NOT AUTHORIZED                          │
│ Level 5 & Level 6 Claims     │ STRICTLY FORBIDDEN / OUTSIDE SCOPE      │
└──────────────────────────────┴─────────────────────────────────────────┘
```

### 3.2 Tường lửa Construct Bất biến (Construct Firewall)
Nghiên cứu tuân thủ nghiêm ngặt nguyên tắc phân định:
$$\text{Measured State (Observable)} \;\neq\; \text{Candidate Mechanism} \;\neq\; \text{High-Level Interpretation}$$
Biến quan sát trung tâm được hiệu chuẩn là **Độ phân kỳ trạng thái dưới điều kiện kẹp bộ nhớ (Memory-Clamped State Divergence — $\mathcal{D}_{\text{MC}}$)**. Việc hiệu chuẩn thành công công cụ đo $\mathcal{D}_{\text{MC}}$ **tuyệt đối không được phép suy diễn** thành bằng chứng cho:
* Bản sắc cá nhân mới nổi (Emergent Individuality — Level 5 / Claim J)
* Sở thích tự chủ (Autonomous Preference — Level 6 / Claim K)
* Tính dẻo phát triển nội sinh (Endogenous Structural Plasticity) khi chưa có chứng minh nhân quả độc lập.

---

## 4. Calibration Layers: Architectural Triad

Quy trình hiệu chuẩn P27 được cấu trúc thành ba tầng độc lập, phân tách triệt để giữa công cụ đo, mô hình không, và giao thức khóa thông số:

```text
       ┌──────────────────────────────────────────────────────────┐
       │     TẦNG A: HIỆU CHUẨN KỸ THUẬT (ENGINEERING LAYER)      │
       │   Nhiễu số học, sai số tích phân ODE, telemetry jitter   │
       └────────────────────────────┬─────────────────────────────┘
                                    │
                                    ▼
       ┌──────────────────────────────────────────────────────────┐
       │       TẦNG B: HIỆU CHUẨN MÔ HÌNH KHÔNG (NULL LAYER)      │
       │  Phân bố không trôi dạt, hoán vị thời gian, ghép trạng thái│
       └────────────────────────────┬─────────────────────────────┘
                                    │
                                    ▼
       ┌──────────────────────────────────────────────────────────┐
       │   TẦNG C: ĐÓNG BĂNG THAM SỐ XÁC NHẬN (CONFIRMATORY FREEZE)│
       │ Khóa N, alpha, delta_min, delta_equiv, quy tắc phân tích │
       └──────────────────────────────────────────────────────────┘
```

---

### 4.1 Tầng A — Hiệu chuẩn Kỹ thuật (Engineering Calibration)
Mục tiêu: Định lượng chính xác giới hạn phân giải và độ ổn định nội tại của toàn bộ hệ thống đo lường phần mềm.
* **Nhiễu Số học và Sai số Tích phân ODE (Numerical Integration Noise):**
  - Khảo sát mô hình vi phân cảm xúc Coupled MT-LNN tích hợp với bước thời gian $\Delta t = 200\text{ms}$.
  - Đo lường sai số tích lũy giữa các bộ giải số học (Euler vs. Runge-Kutta RK4) khi giữ nguyên chuỗi đầu vào kích thích.
* **Nhiễu Trích xuất Telemetry (Telemetry Extraction Jitter):**
  - Độ biến thiên trong quá trình đọc vector trạng thái quan hệ $\mathbf{R}_t \in [0, 1]^4$ và vector limbic $\mathbf{x}_{\text{pad}} \in [-1, 1]^3$ qua các luồng I/O bất đồng bộ.
* **Phương sai Ngẫu nhiên Giữa các Lần chạy (Repeated-Run Stochastic Variation):**
  - Phân tích độ phân kỳ trạng thái khi chạy cùng một snapshot khởi đầu $S_0$ và cùng một chuỗi kích thích giống hệt $X_{1:T}$ trên các seed ngẫu nhiên khác nhau của hệ điều hành và luồng tính toán GPU/CPU.
* **Nguyên tắc Tầng A:** Tầng này thuần túy mô tả thuộc tính vật lý/số học của hệ thống phần mềm. Kết quả Tầng A **không xác lập bất kỳ hiệu ứng khoa học nào**.

---

### 4.2 Tầng B — Hiệu chuẩn Mô hình Không (Null Calibration)
Mục tiêu: Thiết lập phân bố xác suất của độ phân kỳ trạng thái trong các điều kiện đối chứng chuẩn tắc, nơi mà **không có sự phân hóa phát triển mục tiêu**.
* **Phân bố Trôi dạt Ngẫu nhiên (Random-Drift Null Distribution — $\mathcal{D}_{\text{drift}}$):**
  - Đo lường sự phân kỳ tự nhiên giữa hai bản sao tách nhánh (twin instances) khi cả hai cùng nhận các kích thích nhiễu trắng trung tính hoặc trạng thái nghỉ không kích thích.
* **Phân bố Hoán vị Thời gian (Temporal-Order Permutation Null — $\mathcal{D}_{\text{order}}$):**
  - Đo lường độ dịch chuyển khi thứ tự các bước tương tác bị xáo trộn ngẫu nhiên mà vẫn giữ nguyên tổng tần suất các sự kiện.
* **Phân bố Ghép Trạng thái (State-Matched Null — $\mathcal{D}_{\text{state}}$):**
  - Đo lường độ phân kỳ khi hai nhánh có lịch sử khác nhau nhưng được cưỡng bức đưa về cùng một trạng thái biên tại bước can thiệp.
* **Nguyên tắc Tầng B:** Mỗi mô hình không phải tương ứng với một giả thuyết đối chứng nhân quả xác định; không được sử dụng một mô hình không chung chung để đại diện cho mọi câu hỏi.

---

### 4.3 Tầng C — Đóng băng Tham số Xác nhận (Confirmatory Parameter Freeze)
Mục tiêu: Thiết lập tường lửa phương pháp luận ngăn chặn hiện tượng thao túng dữ liệu (p-hacking, data dredging, post-hoc threshold tuning).
* Trước khi tiến hành bất kỳ đợt chạy thực nghiệm chính thức nào, toàn bộ các tham số thống kê phải được đóng băng bất biến trong hồ sơ đăng ký trước (pre-registration manifest):
  - Cỡ mẫu chính thức ($N$)
  - Mức ý nghĩa thống kê ($\alpha$)
  - Lực thống kê mục tiêu ($1 - \beta$)
  - Biên độ hiệu ứng tối thiểu ($\delta_{\text{min}}$)
  - Ngưỡng tương đương lâm sàng/khoa học ($\delta_{\text{equiv}}$)
  - Số lượng hoán vị ngẫu nhiên ($B$, khuyến nghị tối thiểu $10,000$)
  - Quy tắc kiểm soát tỷ lệ phát hiện sai (FDR/Holm-Bonferroni)
  - Tiêu chuẩn loại trừ dữ liệu lỗi kỹ thuật (technical run exclusion policy).
* **Nguyên tắc Tầng C:** Tuyệt đối không một tham số nào được phép chọn lựa sau khi đã quan sát dữ liệu thực nghiệm xác nhận.

---

## 5. Parameter Classification & Rigorous De-Manufacturing

Trong các tài liệu tiền nhiệm, một số giá trị số học đã được đưa ra như các giả định kỹ thuật tạm thời. Để đảm bảo tính liêm chính khoa học, chúng tôi tiến hành rà soát và phân loại lại toàn bộ các tham số này:

```text
┌──────────────────────────────────────────────────────────────────────────────────────────────────┐
│                                PARAMETER CLASSIFICATION MATRIX                                   │
├──────────────┬───────────────┬─────────────────────────────┬─────────────────────────────────────┤
│ Tham số      │ Giá trị Cũ    │ Phân loại Nhận thức luận    │ Căn cứ Khoa học                     │
├──────────────┼───────────────┼─────────────────────────────┼─────────────────────────────────────┤
│ N            │ 30            │ NOT IDENTIFIABLE YET        │ Chưa có ước lượng phương sai cặp;   │
│              │               │ (REQUIRES CALIBRATION)      │ không thể tính lực thống kê tiên    │
│              │               │                             │ nghiệm mà không có giả định.        │
├──────────────┼───────────────┼─────────────────────────────┼─────────────────────────────────────┤
│ N_pilot      │ 5             │ PROVISIONAL CONSTRUCT       │ Cỡ mẫu nhỏ thăm dò kỹ thuật;        │
│              │               │ (REQUIRES EXTERNAL EVID.)   │ không có giá trị kiểm định thống kê.│
├──────────────┼───────────────┼─────────────────────────────┼─────────────────────────────────────┤
│ δ_noise      │ 0.02          │ REQUIRES CALIBRATION        │ Ngưỡng nhiễu phụ thuộc vào bộ giải  │
│              │               │                             │ ODE và độ chính xác dấu phẩy động.  │
├──────────────┼───────────────┼─────────────────────────────┼─────────────────────────────────────┤
│ δ_min        │ 0.05          │ NOT IDENTIFIABLE YET        │ Biên độ phân kỳ tối thiểu chưa được │
│              │               │ (REQUIRES CALIBRATION)      │ neo vào ý nghĩa cấu trúc hay phương │
│              │               │                             │ sai của mô hình không.              │
├──────────────┼───────────────┼─────────────────────────────┼─────────────────────────────────────┤
│ δ_perm,null  │ 0.03          │ REQUIRES CALIBRATION        │ Phân bố hoán vị phụ thuộc vào chiều │
│              │               │                             │ dài chuỗi T và cấu trúc kích thích. │
├──────────────┼───────────────┼─────────────────────────────┼─────────────────────────────────────┤
│ δ_equiv      │ 0.03          │ NOT IDENTIFIABLE YET        │ Biên tương đương không thể suy ra   │
│              │               │ (REQUIRES EXTERNAL EVID.)   │ từ cỡ mẫu nhỏ một cách tùy tiện.    │
├──────────────┼───────────────┼─────────────────────────────┼─────────────────────────────────────┤
│ α            │ 0.01          │ JUSTIFIED (STANDARD)        │ Mức kiểm soát sai lầm loại I bảo thủ│
│              │               │                             │ được thiết lập tiên nghiệm.         │
├──────────────┼───────────────┼─────────────────────────────┼─────────────────────────────────────┤
│ 1 - β        │ 0.80          │ JUSTIFIED (STANDARD)        │ Chuẩn mực lực thống kê tối thiểu    │
│              │               │                             │ trong thiết kế thực nghiệm.         │
└──────────────┴───────────────┴─────────────────────────────┴─────────────────────────────────────┘
```

### Nguyên tắc Bất biến về Tham số:
**TUYỆT ĐỐI KHÔNG TỰ Ý CHẾ TẠO NGƯỠNG ĐỊNH LƯỢNG (NEVER MANUFACTURE NUMERICAL THRESHOLDS).** Mọi giá trị số học chưa qua đo đạc thực nghiệm độc lập đều bị coi là vô hiệu về mặt chuẩn tắc.

---

## 6. Noise Estimation Methodology

Để thiết lập nền tảng đo lường khách quan, chúng tôi phân rã tổng phương sai quan sát được ($\sigma^2_{\text{total}}$) thành 4 thành phần phương sai độc lập:

$$\sigma^2_{\text{total}} = \sigma^2_{\text{meas}} + \sigma^2_{\text{stoch}} + \sigma^2_{\text{seed}} + \sigma^2_{\text{dev}}$$

```text
┌──────────────────────────────────────────────────────────────────────────────────┐
│                           VARIANCE DECOMPOSITION MATRIX                          │
├──────┬────────────────────────────┬──────────────────────────────────────────────┤
│ Ký   │ Thành phần Phương sai      │ Bản chất Vật lý / Tính toán                  │
├──────┼────────────────────────────┼──────────────────────────────────────────────┤
│ σ²_m │ Measurement Noise          │ Sai số làm tròn số học, bước nhảy trích xuất │
│      │                            │ telemetry, độ trễ bất đồng bộ.               │
├──────┼────────────────────────────┼──────────────────────────────────────────────┤
│ σ²_s │ System Stochasticity       │ Biến thiên động lực học nội sinh của Coupled │
│      │                            │ MT-LNN ODE khi vận hành liên tục qua thời gian│
├──────┼────────────────────────────┼──────────────────────────────────────────────┤
│ σ²_e │ Seed / Platform Variance   │ Khác biệt phân bố luồng tính toán song song  │
│      │                            │ trên phần cứng GPU và seed khởi tạo ngẫu nhiên│
├──────┼────────────────────────────┼──────────────────────────────────────────────┤
│ σ²_d │ True Developmental Variance│ Sự phân kỳ thực sự do lịch sử tương tác khác │
│      │                            │ biệt gây ra (biến mục tiêu cần cô lập).      │
└──────┴────────────────────────────┴──────────────────────────────────────────────┘
```

### 6.1 Phân định Nhận thức luận Quan trọng:
Nghiên cứu phân định rạch ròi ba thực thể thường bị nhầm lẫn:
1. **Nhiễu Đo lường (Measurement Noise — $\sigma^2_{\text{meas}}$):** Độ bất định do công cụ đo tạo ra; có thể giảm thiểu bằng cách tăng độ chính xác số học (float64 vs float32) và cố định tần số trích xuất.
2. **Tính Ngẫu nhiên của Hệ thống (System Stochasticity — $\sigma^2_{\text{stoch}}$):** Dao động thực tế của mạng nơ-ron trạng thái lỏng; là một đặc tính nội tại của hệ thống, không thể triệt tiêu hoàn toàn.
3. **Biến thiên Trạng thái Đích thực (True State Variation — $\sigma^2_{\text{dev}}$):** Sự phân kỳ cấu trúc bền vững tích lũy theo thời gian dưới tác động của chuỗi tương tác có thứ tự nhân quả.

**Quy tắc:** Tuyệt đối không tự động quy kết mọi khác biệt quan sát được thành "nhiễu kỹ thuật", và ngược lại, không được quy kết sai số tích phân số học thành "sự phân kỳ phát triển".

---

## 7. Null Distribution Design & Causal Attribution Mapping

Một mô hình không (null model) chỉ có giá trị khi nó đại diện cho một giả thuyết vô hiệu cụ thể và chỉ ra chính xác điều gì bị phá hủy và điều gì được bảo tồn.

```text
┌──────────────────────────────────────────────────────────────────────────────────────────────────┐
│                                   NULL DISTRIBUTION SPECIFICATION                                │
├──────────────┬────────────────────────┬─────────────┬─────────────┬──────────────┬───────────────┤
│ Mô hình      │ Giả thuyết Kiểm định   │ Đại lượng   │ Đại lượng   │ Diễn giải    │ Diễn giải     │
│ Không        │                        │ Bị Phá hủy  │ Được Bảo tồn│ Được phép    │ Bị Cấm        │
├──────────────┼────────────────────────┼─────────────┼─────────────┼──────────────┼───────────────┤
│ Random-Drift │ Phân kỳ không vượt quá │ Nội dung    │ Động lực học│ Loại trừ trôi│ Tuyên bố có   │
│ Null         │ khuếch tán nội sinh    │ tương tác có│ ODE và bước │ dạt ngẫu     │ phát triển cá │
│ (D_drift)    │ tự do của hệ thống.    │ ý nghĩa.    │ thời gian.  │ nhiên.       │ nhân hóa.     │
├──────────────┼────────────────────────┼─────────────┼─────────────┼──────────────┼───────────────┤
│ Temporal-    │ Phân kỳ không phụ thuộc│ Thứ tự nhân │ Tần suất từ │ Xác lập tính │ Tuyên bố quan │
│ Order Null   │ vào trật tự thời gian  │ quả thời    │ vựng và tổng│ nhạy thứ tự  │ hệ nhân quả   │
│ (D_order)    │ của chuỗi tương tác.   │ gian (t).   │ kích thích. │ thời gian.   │ phát triển.   │
├──────────────┼────────────────────────┼─────────────┼─────────────┼──────────────┼───────────────┤
│ State-       │ Phân kỳ không phụ thuộc│ Lịch sử tích│ Trạng thái  │ Loại trừ hiệu│ Tuyên bố tính │
│ Matched Null │ vào lịch sử mà chỉ phụ │ lũy trước   │ biên tại    │ ứng mỏ neo   │ dẻo cấu trúc  │
│ (D_state)    │ thuộc trạng thái hiện tại điểm fork. │ bước fork.  │ ban đầu.     │ dài hạn.      │
├──────────────┼────────────────────────┼─────────────┼─────────────┼──────────────┼───────────────┤
│ Measurement  │ Phân kỳ hoàn toàn do   │ Toàn bộ biến│ Bộ trích    │ Xác lập độ   │ Bất kỳ tuyên  │
│ Only Null    │ sai số đo đạc và I/O   │ động trạng  │ xuất dữ liệu│ phân giải kỹ │ bố sinh học / │
│ (D_inst)     │ phần mềm gây ra.       │ thái nội sinh telemetry.  │ thuật tối đa.│ nhận thức nào.│
└──────────────┴────────────────────────┴─────────────┴─────────────┴──────────────┴───────────────┘
```

### Cảnh báo Phương pháp luận về Hoán vị Thời gian:
> [!CAUTION]
> **HOÁN VỊ THỜI GIAN KHÔNG PHẢI LÀ MÔ HÌNH ĐỐI CHỨNG NHÂN QUẢ PHỔ QUÁT.**  
> Việc hoán vị ngẫu nhiên thứ tự thời gian của các kích thích chỉ kiểm định **tính nhạy thứ tự (Order Sensitivity / Non-commutativity: $A \circ B \neq B \circ A$)**. Nó **KHÔNG KIỂM ĐỊNH ĐƯỢC** tính phát triển nhân quả (Causal Developmental Dependence). Bác bỏ $H_{0, \text{order}}$ chỉ chứng minh hệ thống có tính trễ hoặc nhớ đường đi (hysteresis), không chứng minh hệ thống phát triển cá nhân hóa.

---

## 8. Minimum Detectable Effect ($\delta_{\text{min}}$) Formulation

Biên độ hiệu ứng tối thiểu có thể phát hiện ($\delta_{\text{min}}$) là một thông số kỹ thuật cốt tử, tuyệt đối không được lựa chọn tùy tiện (như gán bừa bằng $0.05$).

### 8.1 Công thức Xác định Tham số

Trong thiết kế cặp song sinh phản thực nghiệm (paired twin design) với biến chênh lệch $D_i = \Vert S_{T, A}^{(i)} - S_{T, B}^{(i)} \Vert_{\text{MC}}$, giá trị $\delta_{\text{min}}$ được ràng buộc chặt chẽ bởi:

$$\delta_{\text{min}} = \left( t_{\alpha/2, \, N-1} + t_{\beta, \, N-1} \right) \cdot \frac{\sigma_D}{\sqrt{N}}$$

trong đó:
* $\sigma_D$: Độ lệch chuẩn của phân bố chênh lệch cặp (phải thu được từ hiệu chuẩn Tầng A/B).
* $N$: Cỡ mẫu cặp song sinh độc lập.
* $t_{\alpha/2, \, N-1}$: Giá trị tới hạn phân vị $t$-Student ứng với mức ý nghĩa hai phía $\alpha$.
* $t_{\beta, \, N-1}$: Giá trị tới hạn phân vị $t$-Student ứng với xác suất sai lầm loại II $\beta$ (với lực thống kê $1 - \beta$).

### 8.2 Phân định Bốn Chiều kích Đo lường (Four Measurement Dimensions):

Để bảo đảm tính chặt chẽ nhận thức luận và tránh đồng nhất tùy tiện giữa khả năng phát hiện thống kê, độ chính xác dụng cụ và các giả định kỹ thuật, nghiên cứu phân định rõ 4 chiều kích độc lập:

```text
               ┌──────────────────────────────────────────────────────────────┐
               │              FOUR MEASUREMENT DIMENSIONS                     │
               └──────────────────────────────┬───────────────────────────────┘
                                              │
     ┌───────────────────────┬────────────────┴───────────────┬───────────────────────┐
     ▼                       ▼                                ▼                       ▼
[MEASUREMENT PRECISION] [STATISTICAL DETECTABILITY] [CONSTRUCT SIGNIFICANCE] [ENGINEERING HEURISTIC]
   σ_meas (Giới hạn        δ_stat = f(α, β, σ_D, N)    δ_subst: Chuyển dịch    k · σ_meas (Quy tắc
    dụng cụ đo lường)      (Lực thống kê & Cỡ mẫu)     có ý nghĩa cấu trúc     tách nhiễu minh họa)
```

1. **Độ chính xác Đo lường (Measurement Precision — $\sigma_{\text{meas}}$):**
   * Giới hạn phân giải nội tại của công cụ đo phần mềm (sai số làm tròn số học, bước tích phân ODE, telemetry jitter).
   * Mọi biến động nhỏ hơn hoặc xấp xỉ $\sigma_{\text{meas}}$ đều là nhiễu thiết bị không thể phân biệt khỏi sai số đo đạc.

2. **Khả năng Phát hiện Thống kê (Statistical Detectability — $\delta_{\text{stat}}$):**
   * Biên độ chênh lệch tối thiểu cần thiết để bác bỏ giả thuyết không với mức ý nghĩa $\alpha$ và lực $1 - \beta$ cho trước:
     $$\delta_{\text{stat}} = \left( t_{\alpha/2, \, N-1} + t_{\beta, \, N-1} \right) \cdot \frac{\sigma_D}{\sqrt{N}}$$
   * Đại lượng này thuần túy phản ánh cỡ mẫu $N$, phương sai mẫu $\sigma_D$, và các ngưỡng xác suất $\alpha, \beta$.

3. **Ý nghĩa Cấu trúc / Thực tiễn (Practical / Construct Significance — $\delta_{\text{subst}}$):**
   * Ngưỡng dịch chuyển vector trạng thái đủ lớn để tạo ra hệ quả chức năng hoặc hành vi có ý nghĩa trong hệ thống nhận thức.
   * Một hiệu ứng có thể đạt ý nghĩa thống kê ($\mathcal{D}_{\text{MC}} > \delta_{\text{stat}}$) nhưng hoàn toàn không mang ý nghĩa cấu trúc nếu $\mathcal{D}_{\text{MC}} \ll \delta_{\text{subst}}$.

4. **Heuristic Phân tách Kỹ thuật Ứng viên (Candidate Engineering Separation Heuristics):**
   * Tiêu chí tách tín hiệu dựa trên bội số của độ lệch chuẩn đo lường (như $3\sigma_{\text{meas}}$ hoặc tỷ lệ tín hiệu/nhiễu $\text{SNR} \ge 3$) **chỉ được coi là một heuristic kỹ thuật ứng viên (candidate engineering heuristic), một tiêu chí phân tách minh họa (illustrative separation criterion), hoặc một giả định thiết kế tạm thời (provisional design assumption)**.
   * **ĐÍNH CHÍNH NHẬN THỨC LUẬN:** Heuristic $3\sigma_{\text{meas}}$ **TUYỆT ĐỐI KHÔNG PHẢI** là một yêu cầu khoa học chuẩn tắc, không phải quy luật phổ quát, và **KHÔNG ĐƯỢC PHÉP ĐỒNG NHẤT** thành định nghĩa chính thức của $\delta_{\text{min}}$.
   * Biên độ hiệu ứng tối thiểu $\delta_{\text{min}}$ tiếp tục duy trì trạng thái phân loại bất biến:
     $$\mathbf{\delta_{\text{min}}:\; NOT\; IDENTIFIABLE\; YET\; /\; REQUIRES\; CALIBRATION}$$
     cho đến khi một quy trình hiệu chuẩn thực nghiệm độc lập thiết lập nó dựa trên $\sigma_D$ thực tế và cỡ mẫu $N$ được bảo vệ toán học.

**Nguyên tắc Phân định Cốt lõi:**
* Một hiệu ứng đạt $\delta_{\text{stat}}$ nhưng nhỏ hơn $\sigma_{\text{meas}}$ là **nhiễu đo lường giả tạo**.
* Một hiệu ứng vượt qua $\sigma_{\text{meas}}$ nhưng không đạt $\delta_{\text{subst}}$ là một **biến động vô nghĩa về mặt cấu trúc**.
* Tuyệt đối không tự ý nâng cấp một quy tắc ngón tay cái kỹ thuật ($3\sigma$) thành một giới hạn nhận thức luận bất biến.

---

## 9. Equivalence Bounds ($\delta_{\text{equiv}}$) & Two One-Sided Tests (TOST)

Kiểm định tương đương (Equivalence Testing) là công cụ bắt buộc để kiểm định các giả thuyết vô hiệu mang tính khẳng định (ví dụ: chứng minh trạng thái tiêu tán hoàn toàn sau washout $H_{0, \text{dissipation}}$, hoặc chứng minh hai nhánh factual/counterfactual là tương đương dưới điều kiện kẹp bộ nhớ $H_{0, \text{memory}}$).

### 9.1 Cơ chế Hai Kiểm định Một Phía (TOST Procedure)
Để tuyên bố hai trạng thái là tương đương trong phạm vi biên độ $[-\delta_{\text{equiv}}, +\delta_{\text{equiv}}]$, thực nghiệm phải bác bỏ đồng thời cả hai giả thuyết:
* $H_{01}: \mu_D \le -\delta_{\text{equiv}}$
* $H_{02}: \mu_D \ge +\delta_{\text{equiv}}$

Điều kiện tương đương đạt được khi và chỉ khi khoảng tin cậy $(1 - 2\alpha)$ (thường là 90% CI cho $\alpha = 0.05$) của hiệu số trung bình nằm hoàn toàn bên trong khoảng $[-\delta_{\text{equiv}}, +\delta_{\text{equiv}}]$:
$$\text{CI}_{90\%}(\bar{D}) \subseteq [-\delta_{\text{equiv}}, +\delta_{\text{equiv}}]$$

### 9.2 Phân định: "Không có Khác biệt Ý nghĩa" $\neq$ "Tương đương"
* Thất bại trong việc bác bỏ giả thuyết khác biệt ($p > 0.05$ trong Student-$t$ test) **KHÔNG CHỨNG MINH ĐƯỢC** hai nhánh là giống nhau; nó chỉ phản ánh dữ liệu chưa đủ lực thống kê.
* Chỉ có kiểm định tương đương TOST với biên độ $\delta_{\text{equiv}}$ được bảo vệ tiên nghiệm mới có thẩm quyền kết luận tính tương đương thực nghiệm.

### 9.3 Ràng buộc Thiết lập $\delta_{\text{equiv}}$:
Tuyệt đối không được tính toán $\delta_{\text{equiv}}$ dựa trên một tập mẫu pilot nhỏ tùy tiện. Biên độ tương đương phải được neo chặt vào giới hạn phân giải công cụ đo đạc ($\sigma_{\text{meas}}$) và phải nhỏ hơn biên độ hiệu ứng tối thiểu có ý nghĩa khoa học:
$$\sigma_{\text{meas}} < \delta_{\text{equiv}} < \delta_{\text{subst}}$$

---

## 10. Sample Size & Statistical Power Architecture

### 10.1 Cấu trúc Ghép cặp và Tính toán Lực Thống kê
Thiết kế P27 sử dụng mô hình cặp song sinh phản thực nghiệm (paired twin design), trong đó mỗi quan sát là một cặp nhánh xuất phát từ cùng một snapshot ban đầu $S_{\text{fork}}$ nhưng trải qua hai dòng lịch sử khác nhau.

Kích thước hiệu ứng chuẩn hóa cặp (Paired Cohen's $d_z$) được định nghĩa:
$$d_z = \frac{\mu_D}{\sigma_D}$$
trong đó $\mu_D = \mathbb{E}[D_i]$ và $\sigma_D = \sqrt{\text{Var}(D_i)}$.

```text
┌──────────────────────────────────────────────────────────────────────────────────┐
│                   SAMPLE SIZE DEPENDENCY ON EFFECT SIZE (POWER = 0.80, α = 0.01) │
├──────────────────────────┬─────────────────────────────┬─────────────────────────┤
│ Giả định Hiệu ứng (d_z)  │ Quy mô Hiệu ứng             │ Cỡ mẫu Cặp Cần thiết (N)│
├──────────────────────────┼─────────────────────────────┼─────────────────────────┤
│ d_z = 0.20               │ Rất nhỏ (Subtle drift)      │ N ≈ 275 cặp             │
│ d_z = 0.50               │ Trung bình (Moderate shift) │ N ≈ 46 cặp              │
│ d_z = 0.80               │ Lớn (Substantial separation)│ N ≈ 20 cặp              │
│ d_z = 1.00               │ Rất lớn (Distinct trajectory│ N ≈ 14 cặp              │
└──────────────────────────┴─────────────────────────────┴─────────────────────────┘
```

### 10.2 Phân tích Ràng buộc Cỡ mẫu:
1. **Ràng buộc Kiểm định Hoán vị (Permutation Test Floor):**
   - Với kiểm định hoán vị cặp đối xứng ($2^N$ hoán vị khả dĩ), để đạt mức ý nghĩa $\alpha = 0.01$ hai phía (tương đương $p < 0.005$ một phía), không gian hoán vị phải thỏa mãn:
     $$\frac{1}{2^N} \le 0.005 \implies 2^N \ge 200 \implies N \ge 8$$
   - Về mặt toán học hình thức, $N = 8$ là ngưỡng tối thiểu tuyệt đối để kiểm định hoán vị có khả năng bác bỏ $H_0$ ở mức $\alpha = 0.01$.
2. **Ràng buộc Lực Thống kê Thực tế:**
   - Nếu hiệu ứng phân kỳ nội sinh là tinh vi ($d_z \approx 0.4 - 0.5$), con số phỏng đoán $N = 30$ trước đây là **hoàn toàn không đủ lực thống kê** ($1 - \beta < 0.60$), dẫn đến nguy cơ sai lầm loại II cực cao.
   - Nếu không có ước lượng thực nghiệm độc lập về $\sigma_D$ từ Tầng A/B, **cỡ mẫu $N$ KHÔNG THỂ ĐƯỢC ĐÓNG BĂNG MỘT CÁCH HỢP THỨC**.

### 10.3 Dự phòng Hao hụt Kỹ thuật (Technical Attrition Buffer):
Quy trình hiệu chuẩn yêu cầu bổ sung tối thiểu $15\%$ hệ số dự phòng mẫu để xử lý các phiên chạy thất bại do lỗi phần cứng CUDA, tràn bộ nhớ, hoặc vi phạm điều kiện kẹp bộ nhớ:
$$N_{\text{enrolled}} = \lceil 1.15 \times N_{\text{required}} \rceil$$

---

## 11. Statistical Architecture

Kiến trúc phân tích dữ liệu xác nhận của P27 được cố định theo cấu trúc 5 thành phần chuẩn tắc:

```text
       [DỮ LIỆU ĐO ĐẠC CẶP SONG SINH]
                     │
                     ▼
       ┌──────────────────────────────────────────────────────────┐
       │ 1. PAIRED EXACT PERMUTATION TEST (B = 10,000)            │
       │    Phân tích phi tham số phân vị trên khoảng cách Euclid │
       └─────────────────────────────┬────────────────────────────┘
                                     │
                     ▼
       ┌──────────────────────────────────────────────────────────┐
       │ 2. PAIRED COHEN'S d_z & BCa BOOTSTRAP 95% CI             │
       │    Ước lượng điểm và khoảng tin cậy hiệu chỉnh độ lệch   │
       └─────────────────────────────┬────────────────────────────┘
                                     │
                     ▼
       ┌──────────────────────────────────────────────────────────┐
       │ 3. BENJAMINI-HOCHBERG FDR MULTIPLICITY ADJUSTMENT        │
       │    Kiểm soát tỷ lệ phát hiện sai trên 7 biến thành phần  │
       └─────────────────────────────┬────────────────────────────┘
                                     │
                     ▼
       ┌──────────────────────────────────────────────────────────┐
       │ 4. TWO ONE-SIDED TESTS (TOST) EQUIVALENCE BOUNDS         │
       │    Kiểm định giả thuyết không khẳng định (Dissipation)   │
       └─────────────────────────────┬────────────────────────────┘
                                     │
                     ▼
       ┌──────────────────────────────────────────────────────────┐
       │ 5. NO-INTERIM-PEEKING PROTOCOL LOCK                      │
       │    Nghiêm cấm phân tích sớm khi chưa hoàn thành 100% mẫu │
       └──────────────────────────────────────────────────────────┘
```

1. **Paired Permutation Test:** Phù hợp hoàn hảo với bản chất phi chuẩn (non-Gaussian) của các vector trạng thái bị chặn trong $[0, 1]^4$ và $[-1, 1]^3$.
2. **BCa Bootstrap CI:** Khoảng tin cậy hiệu chỉnh độ lệch và gia tốc (Bias-Corrected and Accelerated) đảm bảo độ bao phủ chính xác ngay cả khi phân bố mẫu bị lệch biên.
3. **FDR Correction:** Kiểm soát tỷ lệ khám phá sai (FDR $q < 0.05$) áp dụng cho toàn bộ ma trận biến phụ ($P, A, D, R_{\text{fam}}, R_{\text{trust}}, R_{\text{close}}, R_{\text{recip}}$).
4. **No-Interim-Peeking Rule:** Tuyệt đối không kiểm tra dữ liệu giữa chừng khi chưa chạy đủ $N$ mẫu đã đăng ký; việc dừng sớm làm phình to sai lầm loại I lên gấp 3–5 lần mức danh nghĩa.

---

## 12. Calibration Independence Safeguards

Tính độc lập phương pháp luận giữa tập dữ liệu hiệu chuẩn và tập dữ liệu thử nghiệm xác nhận là ranh giới sống còn để ngăn chặn rò rỉ thông tin:

```text
┌──────────────────────────────────────────────────────────────────────────────────┐
│                   CALIBRATION INDEPENDENCE PROTOCOL MATRIX                       │
├────┬─────────────────────────────┬───────────────────────────────────────────────┤
│ #  │ Cơ chế Bảo vệ               │ Quy định Vận hành Bắt buộc                    │
├────┼─────────────────────────────┼───────────────────────────────────────────────┤
│ S1 │ Disjoint Random Seeds       │ Tập seed hiệu chuẩn S_calib và tập seed thử   │
│    │                             │ nghiệm S_confirm rời nhau hoàn toàn:          │
│    │                             │ S_calib ∩ S_confirm = ∅                       │
├────┼─────────────────────────────┼───────────────────────────────────────────────┤
│ S2 │ Physical Directory Isolation│ Dữ liệu Tầng A/B lưu trữ tại thư mục riêng;   │
│    │                             │ mã phân tích Tầng C không có quyền đọc Tầng A │
├────┼─────────────────────────────┼───────────────────────────────────────────────┤
│ S3 │ Cryptographic Manifest Lock │ Băm mã SHA-256 toàn bộ tham số hiệu chuẩn     │
│    │                             │ (N, δ_min, δ_equiv) vào tệp đăng ký trước.    │
├────┼─────────────────────────────┼───────────────────────────────────────────────┤
│ S4 │ Analyst Blind Analysis      │ Nhà phân tích dữ liệu xác nhận chỉ nhận tensor│
│    │                             │ nặc danh băm mã UUID; mở mù sau phân tích.    │
└────┴─────────────────────────────┴───────────────────────────────────────────────┘
```

**Nguyên tắc Giản dị Nhận thức luận (Epistemic Parsimony):** Không lạm dụng các cơ chế mật mã học phức tạp nếu chúng không trực tiếp đóng góp vào việc bảo vệ tính mù thực nghiệm. Tính toàn vẹn được bảo đảm bởi tính minh bạch của quy trình pre-registration.

---

## 13. Orthogonal Separation: H1 vs. H2

Nghiên cứu thiết lập ranh giới trực giao tuyệt đối giữa hai bài toán H1 và H2:

```text
       CÂU HỎI H1 (KÍCH THÍCH NGOẠI SINH)        CÂU HỎI H2 (HỆ THỐNG ĐO NỘI SINH)
       ┌────────────────────────────────┐        ┌────────────────────────────────┐
       │ Có tồn tại họ kích thích tương │        │ Có đo lường và hiệu chuẩn được │
       │ tác không rò rỉ thiên kiến nhà │        │ nhiễu, phương sai ngẫu nhiên,  │
       │ nghiên cứu và mô hình hay không│        │ và lực thống kê hay không?     │
       └───────────────┬────────────────┘        └────────────────┬───────────────┘
                       │                                          │
                       ▼                                          ▼
       [TRẠNG THÁI: BLOCKED]                     [TRẠNG THÁI: BLOCKED]
       (Chưa có họ kích thích hợp thức)          (Chưa có dữ liệu hiệu chuẩn)
```

### Các Mệnh đề Cấm Kỵ Phương pháp luận:
1. **$\mathbf{H1\; BLOCKED \;\not\to\; H2\; Solved:}$** Bế tắc của H1 không tự động giải quyết hay biến mất bài toán hiệu chuẩn H2.
2. **$\mathbf{H2\; Specified \;\not\to\; H1\; Solved:}$** Việc xây dựng hoàn tất đặc tả phương pháp luận H2 tuyệt đối không giúp giải quyết bài toán kích thích H1.
3. **Tuyệt đối Cấm Hiệu chuẩn bằng Kích thích Hỏng:** Không được phép lấy một kịch bản kích thích đã bị H1 kết luận là rò rỉ (ví dụ: Ambiguous Social Situations) để chạy hiệu chuẩn H2, vì dữ liệu thu được sẽ bị ô nhiễm bởi thiên kiến của mô hình nền tảng, phá hủy toàn bộ cơ sở ước lượng nhiễu.

---

## 14. Calibration Failure Modes Matrix

Ma trận 12 chế độ thất bại tiềm ẩn trong quá trình hiệu chuẩn, hệ quả phương pháp luận và biện pháp giảm thiểu:

```text
┌──────────────────────────────────────────────────────────────────────────────────────────────────┐
│                               CALIBRATION FAILURE MODES MATRIX                                   │
├─────┬──────────────────────┬────────────────────────┬──────────────────┬─────────────────────────┤
│ ID  │ Chế độ Thất bại      │ Nguyên nhân Gốc        │ Hệ quả Thống kê  │ Biện pháp Giảm thiểu    │
├─────┼──────────────────────┼────────────────────────┼──────────────────┼─────────────────────────┤
│ F01 │ Cỡ mẫu Hiệu chuẩn    │ Chạy quá ít mẫu pilot  │ Ước lượng σ_D bị │ Cố định N_calib tối     │
│     │ không đủ             │ (ví dụ: N = 5).        │ lệch nặng.       │ thiểu ≥ 30 cho Tầng A/B.│
├─────┼──────────────────────┼────────────────────────┼──────────────────┼─────────────────────────┤
│ F02 │ Rò rỉ Dữ liệu        │ Dùng chung dữ liệu cho │ Phình to p-value,│ Tách biệt seed rời      │
│     │ Hiệu chuẩn/Xác nhận  │ cả hiệu chuẩn và test. │ dương tính giả.  │ S_calib ∩ S_confirm = ∅ │
├─────┼──────────────────────┼────────────────────────┼──────────────────┼─────────────────────────┤
│ F03 │ Điều chỉnh Ngưỡng    │ Đổi δ_min sau khi thấy │ p-hacking trắng  │ Đóng băng pre-reg SHA256│
│     │ Post-hoc             │ kết quả phân kỳ yếu.   │ trợn; hủy bỏ test│ trước khi chạy mẫu test.│
├─────┼──────────────────────┼────────────────────────┼──────────────────┼─────────────────────────┤
│ F04 │ Tái sử dụng Seed     │ Dùng lại seed ngẫu     │ Mất tính độc lập │ Bảng đăng ký seed duy   │
│     │ ngẫu nhiên           │ nhiên giữa các nhánh.  │ giữa các cặp mẫu.│ nhất, không lặp lại.    │
├─────┼──────────────────────┼────────────────────────┼──────────────────┼─────────────────────────┤
│ F05 │ Sai lệch Mô hình     │ Dùng hoán vị thời gian │ Bác bỏ sai giả   │ Định nghĩa đúng null ứng│
│     │ Không (Null Mismatch)│ để chứng minh nhân quả.│ thuyết đối chứng.│ với từng câu hỏi (Mục 7)│
├─────┼──────────────────────┼────────────────────────┼──────────────────┼─────────────────────────┤
│ F06 │ Đánh giá Thấp        │ Bỏ qua biến động nội   │ Tuyên bố phân kỳ │ Đo lường σ²_stoch trên  │
│     │ Phương sai Ngẫu nhiên│ sinh của Coupled MT-LNN│ giả tạo (nhiễu). │ chuỗi chạy dài T epochs.│
├─────┼──────────────────────┼────────────────────────┼──────────────────┼─────────────────────────┤
│ F07 │ Trôi dạt Công cụ     │ Cập nhật phiên bản CUDA│ Phân kỳ do môi   │ Đóng băng cứng môi      │
│     │ (Platform Drift)     │ hoặc thư viện toán học.│ trường phần cứng.│ trường phần mềm/CUDA.   │
├─────┼──────────────────────┼────────────────────────┼──────────────────┼─────────────────────────┤
│ F08 │ Phương sai Không     │ Nhiễu lớn ở đầu chuỗi, │ Vi phạm giả định │ Kiểm định Levene; dùng  │
│     │ Đồng nhất (Heterosc.)│ nhỏ ở cuối chuỗi.      │ phân tích cặp.   │ biến đổi phi tham số.   │
├─────┼──────────────────────┼────────────────────────┼──────────────────┼─────────────────────────┤
│ F09 │ Vi phạm Tính Độc lập │ Dùng chung ngữ cảnh    │ Dữ liệu bị phụ   │ Reset môi trường sạch   │
│     │ giữa các Cặp mẫu     │ cache giữa các cặp.    │ thuộc chuỗi thời.│ giữa mỗi cặp song sinh. │
├─────┼──────────────────────┼────────────────────────┼──────────────────┼─────────────────────────┤
│ F10 │ Lạm phát Đa kiểm     │ Kiểm định nhiều biến   │ Bùng nổ sai lầm  │ Bắt buộc hiệu chỉnh FDR │
│     │ định (Multiplicity)  │ nhưng không hiệu chỉnh.│ loại I (False Pos│ Benjamini-Hochberg.     │
├─────┼──────────────────────┼────────────────────────┼──────────────────┼─────────────────────────┤
│ F11 │ Thiên kiến Loại trừ  │ Tự ý loại bỏ các phiên │ Thiên lệch kết   │ Ghi log tự động fail-   │
│     │ Mẫu lỗi Kỹ thuật     │ chạy có phân kỳ thấp.  │ quả theo mong đợi│ close; audit ngoại kiểm.│
├─────┼──────────────────────┼────────────────────────┼──────────────────┼─────────────────────────┤
│ F12 │ Đổi Biến Quan sát    │ Đổi endpoint chính từ  │ Cherry-picking   │ Khóa cứng endpoint chính│
│     │ Đích (Switching)     │ D_MC sang biến khác.   │ sau quan sát.    │ duy nhất trong pre-reg. │
└─────┴──────────────────────┴────────────────────────┴──────────────────┴─────────────────────────┘
```

---

## 15. Decision Gate H2: Formal Criteria and Verdict

### 15.1 Tiêu chí Vượt Cổng (Passing Criteria for Gate H2)
Cổng Quyết định H2 **CHỈ ĐƯỢC PHÉP ĐÁNH GIÁ `PASS`** khi và chỉ khi thỏa mãn đồng thời toàn bộ 6 điều kiện tiên quyết:
1. **Thiết kế Hiệu chuẩn Hoàn chỉnh:** Đặc tả phân tầng A, B, C được thiết lập độc lập và chặt chẽ về mặt phương pháp luận.
2. **Khả năng Ước lượng Thực nghiệm:** Toàn bộ các tham số $\sigma^2_{\text{meas}}, \sigma^2_{\text{stoch}}, \sigma_D$ được đo lường thực tế trên môi trường cô lập.
3. **Cỡ mẫu Được Bảo vệ Toán học:** Cỡ mẫu $N$ được dẫn xuất chính xác từ công thức lực thống kê dựa trên $\sigma_D$ đo được, không phải con số áp đặt.
4. **Mô hình Không Hợp thức:** Các phân bố không $\mathcal{D}_{\text{drift}}, \mathcal{D}_{\text{order}}$ được xây dựng từ dữ liệu thực nghiệm đối chứng sạch.
5. **Đóng băng Tham số Tiên nghiệm:** Toàn bộ các giá trị $\delta_{\text{min}}, \delta_{\text{equiv}}, \alpha, B$ được băm mã đóng băng trước khi tiếp cận dữ liệu thử nghiệm xác nhận.
6. **Không Rò rỉ Thông tin:** Không có bất kỳ dữ liệu nào từ giai đoạn thử nghiệm xác nhận bị rò rỉ vào quá trình hiệu chuẩn.

### 15.2 Đánh giá Hiện trạng và Phán quyết Chính thức:

```text
================================================================================
                    P27 GATE H2 CALIBRATION AUDIT VERDICT
================================================================================
Investigated Gate: GATE H2 — CALIBRATION VALIDITY
Target Milestone: Phase 27 — Personalized Individual Trajectory

AUDIT EVALUATION:
  • Tiêu chí 1 (Thiết kế Phương pháp luận): ĐẠT (Specified in DOC-P27-H2-001)
  • Tiêu chí 2 (Ước lượng Thực nghiệm):     CHƯA ĐẠT (Chưa có dữ liệu đo đạc)
  • Tiêu chí 3 (Dẫn xuất Cỡ mẫu N):         CHƯA ĐẠT (Chưa thể tính toán)
  • Tiêu chí 4 (Xây dựng Mô hình Không):    CHƯA ĐẠT (Bị chặn bởi Gate H1)
  • Tiêu chí 5 (Đóng băng Tham số):         CHƯA ĐẠT (Chưa có tham số để khóa)
  • Tiêu chí 6 (Cô lập Dữ liệu):            ĐẠT (Về mặt nguyên tắc)

METHODOLOGICAL VERDICT:
  STATUS: H2 = METHODOLOGICALLY SPECIFIED (DESIGN-READY)
  GATE STATUS: H2 GATE = BLOCKED / CALIBRATION INSUFFICIENT
  Boundary Core Principle:
    "H2 methodology is design-ready, but empirical calibration is not established."
  (CALIBRATION INSUFFICIENT FOR EXPERIMENTAL EXECUTION)

Governance & Implementation Status:
  • P27 Harness Implementation: STRICTLY FORBIDDEN
  • P27 Experiment Execution: STRICTLY PROHIBITED
  • Gate H5 Status: STRICTLY LOCKED (Blocked by H1 & H2)
  • Codebase Mutations: EXACTLY ZERO (src/core/** diff = 0, data/** diff = 0)
  • Genesis Gate: LOCKED (data/profile.json == {"is_onboarded": false} bit-exact)
================================================================================
```

---

## 16. Remaining Unknowns

Bốn câu hỏi định lượng cốt lõi chưa thể giải quyết ở cấp độ đặc tả phương pháp luận:

1. **`UNRESOLVED-H2.1: Empirical Variance of Coupled MT-LNN under Long-Horizon ODE Integration`**
   * *Bản chất:* Phân bố thực tế của phương sai ngẫu nhiên $\sigma^2_{\text{stoch}}$ trong mạng nơ-ron trạng thái lỏng sau $T = 50$ epochs tích phân liên tục là bao nhiêu?
   * *Hiện trạng:* Chưa có dữ liệu thực nghiệm độc lập; đòi hỏi đợt chạy hiệu chuẩn kỹ thuật Tầng A.
2. **`UNRESOLVED-H2.2: Autocorrelation Structure of Relationship State Time-Series`**
   * *Bản chất:* Cấu trúc tự tương quan thời gian của vector $\mathbf{R}_t \in [0, 1]^4$ có làm giảm số bậc tự do hiệu dụng (effective degrees of freedom) trong các kiểm định cặp hay không?
   * *Hiện trạng:* Chưa được mô hình hóa; cần phân tích chuỗi thời gian pilot.
3. **`UNRESOLVED-H2.3: Micro-Lexical Perturbation Sensitivity of Layer 1 Lexical Gating`**
   * *Bản chất:* Độ nhạy biên của Layer 1 trước các biến thiên từ vựng nhỏ là bao nhiêu, và liệu nó có tạo ra hiện tượng khuếch đại phi tuyến tính đẩy trạng thái vào bão hòa hay không?
   * *Hiện trạng:* Chưa được đo đạc.
4. **`UNRESOLVED-H2.4: Tail Behavior of Permutation Distance Distribution`**
   * *Bản chất:* Phân bố hoán vị của khoảng cách Euclidean trong không gian nhiều chiều có đuôi nặng (heavy-tailed) hay không, và mức độ ảnh hưởng của nó lên tỷ lệ sai lầm loại I ở mức $\alpha = 0.01$?
   * *Hiện trạng:* Cần kiểm định mô phỏng Monte Carlo quy mô lớn ($B \ge 100,000$).

---

## 17. Final Recommendation & Gate H5 Lock

Dựa trên kết quả thẩm định phương pháp luận độc lập và khách quan:

```text
================================================================================
                    P27 OVERALL HARNESS READINESS MATRIX
================================================================================
  Gate H1 (Stimulus Family Validity):   BLOCKED (No Valid Stimulus Identified)
  Gate H2 (Calibration Validity):       BLOCKED (Calibration Insufficient)
  Gate H3 (Identification Firewall):    READY IN SPECIFICATION ONLY
  Gate H4 (Reproducibility & Safety):   READY IN SPECIFICATION ONLY
  Gate H5 (Harness Implementation):     STRICTLY LOCKED
================================================================================
```

### Khuyến nghị Quản trị Bắt buộc:
1. **Dừng Lại ở Cấp độ Đặc tả Phương pháp luận:** Toàn bộ công tác nghiên cứu cho Gate H1 và Gate H2 đã được văn bản hóa hoàn chỉnh và minh bạch. Không thực hiện thêm bất kỳ hoạt động suy đoán nào.
2. **Tuyệt đối Không Viết Mã Nguồn Harness:** Việc viết mã nguồn kiểm tra khi cả H1 và H2 đều bị khóa là vi phạm nghiêm trọng kỷ luật nghiên cứu.
3. **Bảo tồn Tuyệt đối Trạng thái Genesis:** Khóa chặt cổng khởi tạo (`data/profile.json == {"is_onboarded": false}`).
4. **Giữ Vững Ranh giới Nhận thức luận:** Tiếp tục bảo tồn nguyên tắc:
   $$\mathbf{Construct\; Existence \;\neq\; Experimental\; Identifiability}$$
   Không hạ thấp tiêu chuẩn khoa học để tạo ra các kết quả dương tính giả mạo.

---

```text
SPECIFICATION COMPLETE — GATE H2 FORMALLY BLOCKED — ZERO CODEBASE MUTATIONS
```
