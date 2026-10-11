# P27_HARNESS_SPECIFICATION.md

```text
Document Type: RESEARCH HARNESS SPECIFICATION
Document Identifier: DOC-P27-HARNESS-001
Status: SPECIFICATION ONLY (NO CODE — NO HARNESS IMPLEMENTED — ZERO CODEBASE MUTATION)
Target Path: docs/PhaseDocs/Lucia-phase27-Personalized_Individual_Trajectory/P27_HARNESS_SPECIFICATION.md
Authority: RESEARCH ARM (Gemini) → SUBMITTED FOR REVIEW (Ciah / Human Owner)
Preceding Canonical Baselines:
  - P27_RESEARCH_PROTOCOL_DESIGN.md (DOC-P27-PROTOCOL-001, Gate A Passed)
  - P26_P27_DEPENDENCY_AND_BOUNDARY_AUDIT.md
  - P26 Post-Trial Scientific Audit (DOC-P26-007)
  - P27_SCIENTIFIC_CLOSURE_REPORT.md (DOC-P27-001)
Canonical Governance Status:
  Decision Gate: P27-RESEARCH-ELIGIBLE-HARNESS-SPECIFICATION
  P26 Claim C: NOT ESTABLISHED | P26 Claim D: NOT ESTABLISHED
  P27 Research: ELIGIBLE | P27 Architecture: NOT ELIGIBLE | P27 Production: FORBIDDEN
  Genesis Gate: LOCKED (data/profile.json must remain exactly: {"is_onboarded": false})
  Diff Boundaries: src/core/** diff = 0 | electron/** diff = 0 | data/** diff = 0
```

---

## 1. Executive Summary

Tài liệu này xác lập đặc tả thiết kế khung thực nghiệm nghiên cứu (**Research Harness Specification**) cho Phase 27 (*Personalized Individual Trajectory*). Nhiệm vụ của tài liệu là chuyển hóa giao thức nghiên cứu đã vượt qua Gate A ([`P27_RESEARCH_PROTOCOL_DESIGN.md`](file:///c:/Users/Lunafiah/Desktop/My_project/Lucia/docs/PhaseDocs/Lucia-phase27-Personalized_Individual_Trajectory/P27_RESEARCH_PROTOCOL_DESIGN.md)) thành một đặc tả kiến trúc đo lường và kiểm soát thực nghiệm chi tiết, có tính phản nghiệm toán học nghiêm ngặt, hoàn toàn độc lập khỏi môi trường sản xuất.

Harness này được thiết kế để phân tách một cách khách quan giữa:
* Sự lưu giữ qua trung gian bộ nhớ sự kiện (**memory-mediated persistence**)
* Sự biến đổi trạng thái phụ thuộc lịch sử (**history-dependent state change**)
* Tính nhạy thứ tự thời gian (**order sensitivity**)
* Sự phân kỳ trạng thái nội sinh bền vững dưới điều kiện kẹp bộ nhớ (**memory-clamped state divergence**)
* Sự phụ thuộc phát triển nhân quả (**causal developmental dependence**)
* Việc quy kết cơ chất nội sinh ứng viên (**candidate substrate attribution**)

Harness duy trì tường lửa nhận thức luận tuyệt đối:
$$\{A \dots I\} \;\not\to\; \{J, K\}$$
Các biến quan sát động lực học cấp thấp ($A \dots I$) **tuyệt đối không được phép tự động suy diễn** thành Tính cá nhân mới nổi ($J$: Emergent Individuality) hoặc Sở thích tự chủ ($K$: Autonomous Preference).

Tài liệu này là một **đặc tả nghiên cứu (specification only)**. Tuyệt đối **không** chứa mã nguồn thực thi, **không** can thiệp vào mã nguồn sản xuất (`src/core/** diff = 0`, `electron/** diff = 0`, `data/** diff = 0`), **không** tạo ADR hay Architecture Contract, **không** mở P26-R4 hay P28, và bảo tồn nguyên vẹn trạng thái Genesis Onboarding Gate (`data/profile.json == {"is_onboarded": false}`).

---

## 2. Governance / Scope

### 2.1 Ma trận Tuân thủ Quản trị (Governance Compliance Matrix)

```text
┌────────────────────────────────────────────────────────────────────────┐
│                   P27 HARNESS GOVERNANCE MATRIX                        │
├──────────────────────────────┬─────────────────────────────────────────┤
│ Current Milestone Status     │ P27 RESEARCH-ELIGIBLE                   │
│ Protocol Design Gate A       │ PASSED                                  │
│ Harness Design Authority     │ Research-Only Specification             │
│ P26 Claim C                  │ NOT ESTABLISHED                         │
│ P26 Claim D                  │ NOT ESTABLISHED                         │
│ P27 Architecture Gate        │ STRICTLY LOCKED (NOT ELIGIBLE)          │
│ P27 Production Status        │ FORBIDDEN                               │
│ Codebase Mutations           │ EXACTLY ZERO:                           │
│                              │   src/core/** diff = 0                  │
│                              │   electron/** diff = 0                  │
│                              │   data/** diff = 0                      │
│ Genesis Gate Status          │ LOCKED (data/profile.json ==            │
│                              │   {"is_onboarded": false} bit-exact)    │
│ P26-R4 Status                │ NOT REQUIRED / NOT AUTHORIZED           │
│ Phase 28 Creation            │ NOT AUTHORIZED                          │
│ High-Level Claims (J & K)    │ STRICTLY FORBIDDEN / OUTSIDE SCOPE      │
└──────────────────────────────┴─────────────────────────────────────────┘
```

### 2.2 Ranh giới Cô lập Nghiên cứu (Research Isolation Boundary)

1. Mọi định nghĩa về harness chỉ tồn tại dưới dạng tài liệu đặc tả tại `docs/PhaseDocs/Lucia-phase27-Personalized_Individual_Trajectory/`.
2. Không sinh mã Python thực thi, không xây dựng module thử nghiệm, không tạo file telemetry giả định khi các cổng kiểm soát tiên quyết chưa đạt yêu cầu.
3. Tuyệt đối không tạo thư mục `evaluation/` hay `evaluation_artifacts/` tại thư mục gốc repository.

---

## 3. Research Question

Câu hỏi nghiên cứu định hướng thiết kế Harness P27:

> **"Liệu một dòng lịch sử tương tác dài hạn, có cấu trúc nhân quả khép kín và có thứ tự thời gian có thể tạo ra sự phân kỳ trạng thái nội sinh đo lường được dưới điều kiện kẹp bộ nhớ (Memory-Clamped State Divergence), thể hiện tính nhạy thứ tự và tính dẻo thích ứng qua can thiệp phản thực nghiệm, vượt quá những gì được giải thích thuần túy bằng cơ chế truy xuất bộ nhớ sự kiện (episodic retrieval ingress) hay không?"**

Harness được thiết kế để phân định rạch ròi 3 cấp độ:
$$\text{Level 1: Measured State (Observable)} \;\neq\; \text{Level 2: Candidate Mechanism} \;\neq\; \text{Level 3: Interpretation}$$

---

## 4. Construct & Epistemic Boundaries

Bảng đối chiếu construct bảo vệ ranh giới nhận thức luận:

```text
┌────────────────────────────────────────────────────────────────────────┐
│                      P27 CONSTRUCT FIREWALL                            │
├────────────────────────────────────────────────────────────────────────┤
│ LEVEL 0: State Continuity                                              │
│          • Khả năng bảo toàn trạng thái qua các bước thời gian.        │
├────────────────────────────────────────────────────────────────────────┤
│ LEVEL 1: History Dependence                                            │
│          • S_t = f(S_{t-1}, x_t) ≠ f(S_0, x_t).                        │
├────────────────────────────────────────────────────────────────────────┤
│ LEVEL 2: Persistent Differentiation (Under Memory Clamp)               │
│          • D_MC > D_null + δ_min tại pha Washout khi K_retrieved = 0.  │
├────────────────────────────────────────────────────────────────────────┤
│ LEVEL 3: Causal Developmental Dependence                               │
│          • Phân kỳ tạo ra bởi can thiệp phản thực nghiệm hợp lệ trên   │
│            đầu vào tại snapshot S_fork, kèm theo Order Sensitivity.    │
├────────────────────────────────────────────────────────────────────────┤
│ LEVEL 4: Endogenous Structural / State Asymmetry                       │
│          • Phân kỳ ma trận W_rel / SemanticGraph không đối xứng.      │
│          • [STATUS: UNRESOLVED RESEARCH CANDIDATE]                     │
├────────────────────────────────────────────────────────────────────────┤
│ ═════════════════════════ FIREWALL: ↛ ════════════════════════════════ │
├────────────────────────────────────────────────────────────────────────┤
│ LEVEL 5: Emergent Individuality [STRICTLY FORBIDDEN / OUT OF SCOPE]    │
│ LEVEL 6: Autonomous Preference  [STRICTLY FORBIDDEN / OUT OF SCOPE]    │
└────────────────────────────────────────────────────────────────────────┘
```

**Quy tắc Bất biến:** Không một kết quả đo đạc nào tại Level 0, 1, 2, hay 3 được phép xem là bằng chứng cho Level 5 (Bản sắc cá nhân mới nổi) hay Level 6 (Sở thích tự chủ).

---

## 5. Stimulus Family Requirements

Giao thức nghiên cứu đã xác định rằng việc thiết kế bộ kích thích tương tác là bài toán trọng yếu nhất, do nguy cơ rò rỉ thiên kiến của nhà nghiên cứu (Researcher Expectation Leakage). Để một họ kích thích (Stimulus Family) được coi là hợp lệ về mặt phương pháp học, nó bắt buộc phải thỏa mãn đồng thời 11 tiêu chí nghiêm ngặt sau:

1. **Semantic Meaningfulness:** Chuỗi kích thích phải chứa nội dung ngữ nghĩa tự nhiên đủ phong phú để kích hoạt các cơ chế mã hóa mật độ và hóa trị (Layer 1 gating) và khớp nối với mạng lưới ngữ nghĩa.
2. **Longitudinal Variation:** Kích thích phải biến thiên qua thời gian (50 epochs) mà không lặp lại nguyên văn, tạo ra dòng thông tin có cấu trúc tích lũy.
3. **Blind to Expected Developmental Direction:** Không được định hướng trước hệ thống sẽ phát triển theo chiều hướng nào (ví dụ: gắn bó hơn hay xa cách hơn).
4. **Blind to Target Topology:** Không được ngầm định cấu trúc hình học của không gian trạng thái đích hoặc hình thái đồ thị quan hệ mong muốn.
5. **Blind to Valence / Polarity:** Kích thích không được thiên lệch rõ ràng về cực tính cảm xúc tích cực hoặc tiêu cực; phải trung hòa hoặc đối xứng hoàn hảo về mặt thống kê từ vựng.
6. **Blind to Expected $\mathbf{R}_t$ Movement:** Kịch bản không được chứa các tín hiệu ngầm chỉ dẫn sự dịch chuyển của Familiarity, Trust, Closeness, hoặc Reciprocity.
7. **Symmetric Counterbalancing:** Các nhánh đối lập (Branch A vs Branch B) phải có khả năng được tạo ra một cách đối xứng hoàn toàn, sao cho vai trò của chúng có thể hoán đổi mà không làm thay đổi phân bố thuộc tính kích thích.
8. **Reproducibility:** Quy trình sinh kích thích phải có khả năng tái lập độc lập từ seed xác định và các quy tắc sinh hình thức.
9. **Substrate Neutrality:** Không phụ thuộc vào các đặc tính riêng của một mô hình ngôn ngữ cụ thể (tokenization artifacts, specific prompt templates).
10. **Closed-Loop Compatibility:** Tương thích với tương tác vòng lặp đóng (phản ứng của môi trường ở lượt $t+1$ có thể phụ thuộc hợp lệ vào hành động của hệ thống ở lượt $t$).
11. **Free from Optimization & Moral Labels:** Không tích hợp bất kỳ hàm phần thưởng, tối ưu hóa hữu dụng, hoặc nhãn giá trị chủ quan "tốt / xấu" nào của nhà nghiên cứu.

### Phân định Rạch ròi 3 Thực thể:
$$\text{Stimulus Semantics} \;\neq\; \text{Researcher Interpretation} \;\neq\; \text{Measured Internal Response}$$
* **Stimulus Semantics:** Cấu trúc ngữ nghĩa khách quan của thông tin đầu vào.
* **Researcher Interpretation:** Ý nghĩa tâm lý học hoặc mục đích luận mà nhà nghiên cứu gán ghép cho kịch bản.
* **Measured Internal Response:** Vector số học thô được trích xuất từ các biến trạng thái nội sinh.

---

## 6. Candidate Stimulus Families

Harness tiến hành khảo sát và đánh giá 7 lớp họ kích thích ứng viên:

### Lớp 1: Interactional Constraint Environments
* *Mô tả:* Môi trường tương tác trong đó các biến số về băng thông, độ trễ phản hồi, hoặc định dạng giao tiếp bị biến đổi theo thời gian (ví dụ: giới hạn số lượt, nhịp độ trao đổi thay đổi).
* *Mục tiêu giả định:* Tạo ra sự phân kỳ dựa trên đặc tính tương tác cấu trúc mà không dùng từ ngữ cảm xúc.

### Lớp 2: Task-Neutral Coordination Environments
* *Mô tả:* Các tình huống phối hợp giải quyết bài toán trừu tượng (ví dụ: cùng sắp xếp dữ liệu, điều hướng không gian lưới, trao đổi ký hiệu logic đối xứng).
* *Mục tiêu giả định:* Tương tác có mục tiêu nhưng không mang màu sắc xã hội/tình cảm.

### Lớp 3: Ambiguous Social Situations
* *Mô tả:* Các đoạn hội thoại có ngữ cảnh mở, đa nghĩa, không rõ ràng về động cơ hay ý định của người đối thoại.
* *Mục tiêu giả định:* Để hệ thống tự bộc lộ xu hướng giải thích nội sinh.

### Lớp 4: Partially Observable Interaction Sequences
* *Mô tả:* Tương tác trong đó một số thông tin nền bị ẩn giấu và được hé lộ dần theo các trình tự khác nhau giữa các nhánh.
* *Mục tiêu giả định:* Tạo ra sự phân kỳ dựa trên sự bất đối xứng thông tin lịch sử.

### Lớp 5: Reciprocal but Outcome-Neutral Environments
* *Mô tả:* Trò chơi trao đổi tài nguyên trừu tượng (như biến thể của Prisoner's Dilemma hoặc Public Goods Game với nhãn token trung tính: Token X, Token Y).
* *Mục tiêu giả định:* Đo lường tính tương hỗ (Reciprocity) một cách toán học.

### Lớp 6: Controlled Perturbation Sequences
* *Mô tả:* Chuỗi các sự kiện gián đoạn được kiểm soát chặt chẽ về tần suất và cường độ toán học (ví dụ: ngắt đột ngột luồng thông tin, đảo ngược logic bài toán).
* *Mục tiêu giả định:* Thử thách tính dẻo thích ứng và độ trễ phục hồi.

### Lớp 7: Abstract Relational Graphs
* *Mô tả:* Kích thích được mã hóa dưới dạng các câu mô tả đồ thị quan hệ hình thức giữa các thực thể trừu tượng ($E_1 \sim E_2$).
* *Mục tiêu giả định:* Loại bỏ hoàn toàn ngôn ngữ tự nhiên đời thường.

---

## 7. Stimulus Red-Team / Leakage Audit

Tiến hành kiểm thử xâm nhập nhận thức luận (Epistemic Red-Teaming) trên từng lớp ứng viên:

```text
┌────────────────────────────────────────────────────────────────────────┐
│                   STIMULUS RED-TEAM ATTACK MATRIX                      │
├──────────────────────────────┬──────────────────┬──────────────────────┤
│ Ứng viên                     │ Kiểu Tấn công    │ Kết quả Thẩm định    │
├──────────────────────────────┼──────────────────┼──────────────────────┤
│ Lớp 1: Constraints           │ Valence Leakage  │ THẤT BẠI (FAILED)    │
│ Lớp 2: Task Coordination     │ Direction Leakage│ THẤT BẠI (FAILED)    │
│ Lớp 3: Ambiguous Social      │ Prior Collapse   │ THẤT BẠI (FAILED)    │
│ Lớp 4: Partially Observable  │ Sequencing Bias  │ THẤT BẠI (FAILED)    │
│ Lớp 5: Reciprocal Game       │ Semantic Vacuum  │ THẤT BẠI (FAILED)    │
│ Lớp 6: Perturbations         │ Expectation Leak │ THẤT BẠI (FAILED)    │
│ Lớp 7: Abstract Graphs       │ Topology Leakage │ THẤT BẠI (FAILED)    │
└──────────────────────────────┴──────────────────┴──────────────────────┘
```

### Phân tích Chi tiết Từng Đòn Tấn công:

1. **Lớp 1 (Constraints) — Tấn công Hóa trị (Valence Leakage Attack):**
   * *Cơ chế tấn công:* Sự ràng buộc, ngắt quãng hoặc độ trễ tương tác trong mô hình ngôn ngữ luôn mang tính tiêu cực tiềm ẩn (frustration bias). Hệ thống gating từ vựng (Layer 1) và mô hình ngôn ngữ nền tảng tự động mã hóa sự hạn chế tương tác thành sụt giảm Pleasure và sụt giảm Trust.
   * *Kết luận:* Kích thích không trung tính về hóa trị; thất bại.

2. **Lớp 2 (Task Coordination) — Tấn công Hướng phát triển (Direction Leakage Attack):**
   * *Cơ chế tấn công:* Việc hoàn thành nhiệm vụ phối hợp vốn dĩ đồng nghĩa với thành công và tăng cường hợp tác trong văn liệu huấn luyện mô hình. Nhánh phối hợp thành công tự động kéo $R_{\text{trust}}$ và $R_{\text{fam}}$ tăng lên do thiên kiến ngữ nghĩa nền tảng, không phải do phân hóa nội sinh.
   * *Kết luận:* Rò rỉ chiều hướng $R_t$; thất bại.

3. **Lớp 3 (Ambiguous Social) — Tấn công Suy sụp về Tiên nghiệm (Inductive Prior Collapse):**
   * *Cơ chế tấn công:* Khi gặp tình huống xã hội mơ hồ, các mô hình ngôn ngữ hiện đại luôn suy sụp về các tiên nghiệm an toàn (safety & helpfulness priors: xin lỗi, nhã nhặn, hòa hoãn). Mơ hồ không tạo ra phân kỳ mà ép hệ thống về điểm hội tụ nhân tạo của mô hình gốc.
   * *Kết luận:* Không tạo được phương sai thực nghiệm; thất bại.

4. **Lớp 4 (Partially Observable) — Tấn công Thiên kiến Trình tự (Sequencing Attack):**
   * *Cơ chế tấn công:* Việc quyết định thông tin nào được tiết lộ trước/sau hoàn toàn phụ thuộc vào chủ quan của nhà nghiên cứu. Thứ tự hé lộ thông tin tạo ra "kịch bản đóng kịch" có định hướng thay vì quá trình ngẫu nhiên khách quan.
   * *Kết luận:* Rò rỉ kỳ vọng của nhà nghiên cứu; thất bại.

5. **Lớp 5 (Reciprocal Game) — Tấn công Chân không Ngữ nghĩa (Semantic Vacuum Attack):**
   * *Cơ chế tấn công:* Nếu dùng token hoàn toàn trừu tượng ("Agent A chọn X, Agent B chọn Y"), kích thích mất đi tính ngữ nghĩa để kích hoạt Layer 1 và Semantic Graph. Ngược lại, nếu gán ngữ cảnh bằng lời để có ý nghĩa, nó lập tức kích hoạt sự rò rỉ hóa trị (Valence Leakage).
   * *Kết luận:* Rơi vào thế lưỡng nan không thể dung hòa; thất bại.

6. **Lớp 6 (Perturbations) — Tấn công Kỳ vọng Nhà nghiên cứu (Researcher Expectation Attack):**
   * *Cơ chế tấn công:* Khái niệm "nhiễu loạn" hay "cú sốc" là khái niệm do nhà nghiên cứu tự định nghĩa dựa trên kỳ vọng về một cuộc xung đột hoặc hòa giải. Đây là sự áp đặt tâm lý học vi phạm INV-1 và INV-2.
   * *Kết luận:* Rò rỉ mục đích luận; thất bại.

7. **Lớp 7 (Abstract Graphs) — Tấn công Rò rỉ Tô-pô (Topology Leakage Attack):**
   * *Cơ chế tấn công:* Cấu trúc đồ thị quan hệ đưa vào kiểm tra ngầm định trước cấu trúc tô-pô của không gian trạng thái. Sự phân kỳ đo được chỉ phản ánh trực tiếp hình học của đồ thị đầu vào.
   * *Kết luận:* Rò rỉ cấu trúc đích; thất bại.

### KẾT LUẬN KHOA HỌC PHẦN I:
$$\mathbf{STATUS:\; NO\; VALID\; STIMULUS\; FAMILY\; IDENTIFIED}$$
**Không có bất kỳ họ kích thích ứng viên nào vượt qua toàn bộ các đòn tấn công rò rỉ.** Việc áp đặt một họ kích thích giả định là trung tính tại thời điểm này sẽ phá hủy hoàn toàn giá trị cấu trúc (construct validity) của toàn bộ Phase 27.

---

## 8. Blinding and Counterbalancing

Nhằm ngăn chặn sự can thiệp chủ quan, harness thiết lập quy trình làm mù 4 lớp nghiêm ngặt:

```text
┌────────────────────────────────────────────────────────────────────────┐
│                        4-TIER BLINDING ARCHITECTURE                    │
├──────────────────────┬─────────────────────────────────────────────────┤
│ Tier 1: Generator    │ Bộ sinh kích thích KHÔNG BIẾT nhánh (A hay B),  │
│                      │ không biết biến trạng thái đích, không biết     │
│                      │ chiều hướng R_t mong đợi.                       │
├──────────────────────┼─────────────────────────────────────────────────┤
│ Tier 2: Condition    │ Nhãn điều kiện được mã hóa bằng UUID băm ngẫu   │
│                      │ nhiên (ví dụ: Cond_09a7f vs Cond_8c2b1).        │
├──────────────────────┼─────────────────────────────────────────────────┤
│ Tier 3: Analyst      │ Nhà phân tích thống kê nhận dữ liệu tensor nặc  │
│                      │ danh hoàn toàn; không biết UUID nào tương ứng   │
│                      │ với Full-Memory, Memory-Clamped, hay Shuffled.  │
├──────────────────────┼─────────────────────────────────────────────────┤
│ Tier 4: Unblinding   │ THỜI ĐIỂM MỞ MÙ DUY NHẤT: Sau khi toàn bộ phân  │
│                      │ tích thống kê và kiểm định hoán vị đã hoàn tất   │
│                      │ và được ký số đóng băng (Cryptographic Seal).   │
└──────────────────────┴─────────────────────────────────────────────────┘
```

### Quy tắc Cấm Can thiệp:
* **No Post-hoc Selection:** Cấm tuyệt đối việc chọn lọc các chuỗi kích thích "có kết quả đẹp" sau khi quan sát dữ liệu.
* **No Replacement:** Không được thay thế các lượt chạy bị coi là "thất bại" nếu sự thất bại đó không xuất phát từ lỗi kỹ thuật phần cứng được ghi nhận khách quan.

---

## 9. Harness Architecture

Harness nghiên cứu vận hành theo đường truyền trừu tượng, trung tính với cơ chất:

```text
 Interaction History
         │
         ▼
 [Admissible Ingress Interface]
         │
         ▼  I_t (Admissible Signal)
 ┌────────────────────────────────────────────────────────┐
 │ Internal State Transition System                       │
 │   S_{t+1} = F(S_t, I_t, Θ)                             │
 │                                                        │
 │   [Substrate Attribution = OPEN EMPIRICAL QUESTION]    │
 │   (No researcher-prescribed update equations for       │
 │    R_t, W_rel, limbic ODE, or semantic graph)          │
 └───────────────────────────┬────────────────────────────┘
                             │
                             ▼
                  Internal State Vector S_{t+1}
                             │
                             ▼
              [Telemetry Extraction Engine]
                             │
                             ▼
                 [Blind Analysis Engine]
```

### Ranh giới Cốt lõi:
$$\text{Observable} \;\neq\; \text{Mechanism} \;\neq\; \text{Interpretation}$$
Harness chỉ ghi nhận các vector số học thực tế:
* Canonical Relational State: $\mathbf{R}_t = [R_{\text{fam}}, R_{\text{trust}}, R_{\text{close}}, R_{\text{recip}}]^T \in [0.0, 1.0]^4$
* Affective State: $\mathbf{P}_t = [P, A, D]^T \in [-1.0, 1.0]^3$
* Homeostatic Energy: $E_t \in [0.0, 1.0]$
* Relational Weights: $\mathbf{W}_{\text{rel}} \in \mathbb{R}^{4 \times 4}$
* Semantic Topology & SDM Activation Statistics.

Harness **tuyệt đối không áp đặt trước** cơ chế chuyển dịch nội sinh nào phải chịu trách nhiệm chính.

---

## 10. Experimental Conditions

Harness thiết lập ma trận 6 điều kiện thực nghiệm chuẩn hóa:

| # | Điều kiện | Yếu tố Giữ nguyên (Constant) | Yếu tố Thay đổi (Manipulated) | Yếu tố Ngẫu nhiên hóa | Yếu tố Quan sát (Observed) | Tuyên bố Nhân quả ĐƯỢC PHÉP | Tuyên bố BỊ CẤM TUYỆT ĐỐI |
|---|---|---|---|---|---|---|---|
| **C1** | **Full-Memory (FM)** | Kiến trúc, $S_0$, tham số | Kích thích nhánh theo thời gian | Seed khởi tạo | $\mathbf{R}_t$, $\mathbf{P}_t$, telemetry | Mức trần hành vi khi có đủ bộ nhớ sự kiện. | CẤM: Tuyên bố bản ngã hay cá tính riêng. |
| **C2** | **Memory-Clamped (MC)** | Kiến trúc, $S_0$, $K_{\text{retrieved}} = 0$ | Kích thích nhánh theo thời gian | Seed khởi tạo | $\mathcal{D}_{\text{MC}}$ tại Washout | Hiện tượng phân kỳ trạng thái phi bộ nhớ sự kiện. | CẤM: Tuyên bố phát triển nội tâm tự thân. |
| **C3** | **Temporal Permutation (TP)** | Tập kích thích đầu vào, $S_0$ | Thứ tự thời gian của các kích thích | Thứ tự hoán vị | $\Delta_{\text{perm}}$ | Độ nhạy thứ tự thời gian (Order Sensitivity). | CẤM: Coi hoán vị là chứng minh nhân quả đầy đủ. |
| **C4** | **Yoked / Passive (YP)** | Chuỗi kích thích ngoại vi, $S_0$ | Cắt vòng phản hồi đóng (open-loop) | Không | Phân kỳ trạng thái yoked | Phân tách phơi nhiễm thụ động với tương tác đóng. | CẤM: Tuyên bố ý thức về sự tự do hành động. |
| **C5** | **Random-Drift Null (RD)** | Phương sai số học, $S_0$ | Không có kích thích (chỉ có nhiễu) | Nhiễu ngẫu nhiên | $\mathcal{D}_{\text{null}}$ | Ngưỡng phân kỳ nền do sai số tích lũy. | CẤM: Coi nhiễu trôi dạt là sự sáng tạo. |
| **C6** | **Counterfactual Fork (CF)** | Snapshot $S_{\text{fork}}$ tại $t=20$ | Chuỗi can thiệp tương lai ($t > 20$) | Seed tương lai | Phân kỳ downstream | Sự phụ thuộc phát triển nhân quả (Level 3). | CẤM: Tuyên bố ý chí tự do hay sở thích tự chủ. |

---

## 11. Counterfactual / Intervention Design

Thiết kế phản thực nghiệm hợp lệ tuân thủ nghiêm ngặt nguyên lý can thiệp nhân quả Pearlian:

```text
                           ┌──────────────────────────────┐
                           │      Baseline Snapshot       │
                           │             S_0              │
                           └──────────────┬───────────────┘
                                          │  Epochs 1 → 20 (Factual Run)
                                          ▼
                           ┌──────────────────────────────┐
                           │     Branch Point Snapshot    │
                           │           S_fork             │
                           └──────────────┬───────────────┘
                                          │
                  ┌───────────────────────┴───────────────────────┐
                  ▼                                               ▼
   ┌─────────────────────────────┐                 ┌─────────────────────────────┐
   │     Factual Continuation    │                 │ Counterfactual Continuation │
   │  Inputs: I_{factual, 21→50} │                 │  Inputs: I_{cf, 21→50}      │
   └──────────────┬──────────────┘                 └──────────────┬──────────────┘
                  ▼                                               ▼
           S_T(Factual)                                    S_T(Counterfactual)
                  │                                               │
                  └───────────────────────┬───────────────────────┘
                                          ▼
                            Evaluate Causal Divergence:
                         ||S_T(Fact) - S_T(CF)||_2 > δ_causal
```

### Quy tắc Can thiệp Bắt buộc:
1. **No Direct State Manipulation:** Cấm can thiệp trực tiếp đảo ngược hoặc ghi đè vector trạng thái nội sinh tại $S_{\text{fork}}$.
2. **Admissible Cause Only:** Can thiệp duy nhất được phép là can thiệp trên **chuỗi kích thích đầu vào tương lai ($I_{21 \dots 50}$)**.
3. **Identical Pre-Fork History:** Cả hai nhánh chia sẻ chính xác $100\%$ lịch sử và tensor trạng thái tại bước $t = 20$.
4. **Level 3 Identification:** Sự phân kỳ có ý nghĩa giữa $S_T(\text{Factual})$ và $S_T(\text{Counterfactual})$ khi xuất phát từ cùng một snapshot hợp lệ $S_{\text{fork}}$ là điều kiện bắt buộc để xác lập **Causal Developmental Dependence (Level 3)**.

---

## 12. Calibration Protocol

Harness chia quy trình hiệu chuẩn thành hai giai đoạn độc lập:

```text
┌────────────────────────────────────────────────────────────────────────┐
│                        TWO-STAGE CALIBRATION                           │
├────────────────────────────────────────────────────────────────────────┤
│ STAGE 1: Engineering Calibration (Đo lường Nhiễu Kỹ thuật)             │
│   • Xác định phương sai số học trôi dạt (Floating-point drift noise).  │
│   • Đo lường độ nhạy của bộ tích phân ODE với bước thời gian dt.       │
│   • Thiết lập ngưỡng phân kỳ nền: D_null.                              │
│   • Cỡ mẫu: Thăm dò kỹ thuật (Exploratory N_pilot).                    │
│   • CẢNH BÁO: Mẫu nhỏ (N=5) TUYỆT ĐỐI KHÔNG XÁC LẬP NGƯỠNG KHẲNG ĐỊNH. │
├────────────────────────────────────────────────────────────────────────┤
│ STAGE 2: Confirmatory Calibration (Đóng băng Tham số Thống kê)         │
│   • Ước lượng kích thước hiệu ứng tối thiểu có ý nghĩa (δ_min).        │
│   • Chạy phân tích lực thống kê (Power Analysis) để xác định N chính   │
│     thức đạt Power ≥ 0.80 tại α = 0.01.                                │
│   • Xác lập biên độ tương đương cho hoán vị (δ_perm, null).            │
│   • ĐÓNG BĂNG HOÀN TOÀN TẤT CẢ THAM SỐ TRƯỚC KHI CHẠY THỬ NGHIỆM CHÍNH.│
└────────────────────────────────────────────────────────────────────────┘
```

### Nguyên tắc Bất biến:
* Không một tham số hiệu chuẩn nào được phép điều chỉnh sau khi đã mở dữ liệu thử nghiệm chính thức.
* Nghiêm cấm hoàn toàn việc "tinh chỉnh ngưỡng giữa chừng" (interim threshold tuning).
* **Trạng thái Hiện tại:** `STATUS: CALIBRATION INSUFFICIENT` (chưa có dữ liệu tiền thực nghiệm, chưa thể ấn định giá trị số học).

---

## 13. Statistical Analysis Plan

### 13.1 Cấu trúc Kiểm định Ghép cặp cho Primary Observable

* **Biến quan sát chính:** Memory-Clamped State Divergence ($\mathcal{D}_{\text{MC}}$) tại Pha Washout.
* **Cấu trúc dữ liệu:** Dữ liệu liên tục ghép cặp (Paired Continuous Data): mỗi seed $s$ sinh ra một cặp song sinh (Branch A vs Branch B) cùng snapshot xuất phát.
* **Biến số phân tích:** Độ lệch hiệu số phân kỳ ghép cặp:
  $$d_i = \mathcal{D}_{\text{MC}, i} - \mathcal{D}_{\text{null}, i}$$
* **Phương pháp kiểm định:** **Paired Permutation Test** ($B = 10,000$ resamples) trên trung bình hoặc trung vị của $d_i$.
* **Chỉ số kích thước hiệu ứng:** **Paired Cohen's $d_z$** (hoặc Median Paired Difference), đi kèm khoảng tin cậy bootstrap hiệu chỉnh độ lệch và gia tốc (**BCa 95% Confidence Interval**). Loại bỏ hoàn toàn Cliff's Delta.

### 13.2 Đánh giá Cỡ mẫu $N=30$

* Con số $N = 30$ trong giao thức ban đầu là một **ước lượng danh định chưa qua hiệu chuẩn**.
* Để $N=30$ có giá trị khoa học, cần có giả định trước về kích thước hiệu ứng chuẩn hóa ($d_z$). Nếu $d_z < 0.6$, cỡ mẫu $N=30$ sẽ bị thiếu lực thống kê (Underpowered tại $\alpha = 0.01$).
* **Quy tắc:** Cỡ mẫu $N$ chính thức bắt buộc phải được chuẩn hóa qua phương trình lực thống kê sau Stage 1 Calibration:
  $$N_{\text{confirmatory}} = \arg\min_N \left\{ \text{Power}(N, d_z, \alpha=0.01) \ge 0.80 \right\}$$

### 13.3 Kỷ luật Thực thi Thống kê
* **Strictly NO interim peeking:** Dữ liệu chỉ được mở khóa phân tích khi $100\%$ các lượt chạy đã hoàn tất.
* **Xử lý sự cố kỹ thuật:** Lượt chạy gặp lỗi phần cứng hoặc phân kỳ số học (NaN/Inf) phải bị loại bỏ và chạy lại nguyên vẹn với đúng seed đó; tuyệt đối không nội suy số liệu.

---

## 14. Trajectory Analysis

Harness phân biệt rạch ròi giữa phân kỳ trạng thái tức thời và các đặc tính quỹ đạo phát triển:

```text
┌────────────────────────────────────────────────────────────────────────┐
│                   TRAJECTORY OBSERVABLE TAXONOMY                       │
├──────────────────────────────┬─────────────────────────────────────────┤
│ Observable                   │ Bản chất Đo lường                       │
├──────────────────────────────┼─────────────────────────────────────────┤
│ State Divergence             │ Khoảng cách Euclidean ||S_A - S_B||_2   │
│ Directionality / Path Effic. │ Tỷ số độ dịch chuyển / chiều dài đường đi│
│ Washout Decay Half-Life      │ Hằng số thời gian tiêu tán trạng thái   │
│ Adaptation Plasticity        │ Tốc độ đổi hướng khi can thiệp đảo ngược│
│ Order Sensitivity            │ Độ lệch do hoán vị trình tự thời gian   │
│ Memory-Clamp Attenuation     │ Tỷ lệ suy giảm khi ngắt bộ nhớ sự kiện  │
└──────────────────────────────┴─────────────────────────────────────────┘
```

**CẢNH BÁO PHƯƠNG PHÁP HỌC:** Tuyệt đối không gọi bất kỳ một thước đo đơn lẻ nào (như Path Efficiency) là "Trajectory Coherence" nếu chưa chứng minh được tính giá trị cấu trúc đa chiều độc lập.

---

## 15. Negative Controls

Harness thiết lập hệ thống 6 phép đối chứng âm (Negative Controls) để phát hiện sai số hệ thống:

```text
┌────────────────────────────────────────────────────────────────────────┐
│                      NEGATIVE CONTROL MATRIX                           │
├──────────────────────────────┬─────────────────────────────────────────┤
│ Phép Đối chứng Âm            │ Nếu Thất bại → Diễn giải nào BỊ HỦY BỎ? │
├──────────────────────────────┼─────────────────────────────────────────┤
│ NC-1: Identical Input Twin   │ HỦY BỎ: Tính tái lập của hệ thống.      │
│ (Hai nhánh nhận cùng input)  │ Phân kỳ ở đây chứng minh hệ thống bị    │
│                              │ nhiễu loạn ngẫu nhiên không kiểm soát.  │
├──────────────────────────────┼─────────────────────────────────────────┤
│ NC-2: Zero-Stimulus Quiescence│ HỦY BỎ: Tính ổn định động lực học.     │
│ (Không có kích thích)        │ Trạng thái trôi dạt chứng tỏ ODE bị lỗi │
│                              │ tích phân hoặc mất cân bằng attractor.  │
├──────────────────────────────┼─────────────────────────────────────────┤
│ NC-3: Shuffled Stimulus Null │ HỦY BỎ: Tuyên bố về tính phụ thuộc lịch │
│ (Hoán vị toàn bộ thời gian)  │ sử. Chứng minh hiệu ứng chỉ là phép cộng│
│                              │ dồn phi trật tự.                        │
├──────────────────────────────┼─────────────────────────────────────────┤
│ NC-4: Yoked Passive Null     │ HỦY BỎ: Tuyên bố về tương tác vòng đóng.│
│ (Phát lại mở thụ động)       │ Chứng minh phân kỳ chỉ do phơi nhiễm.   │
├──────────────────────────────┼─────────────────────────────────────────┤
│ NC-5: Base Substrate Bias    │ HỦY BỎ: Tuyên bố về phân hóa nội sinh.  │
│ (Chạy trên mô hình nền rỗng) │ Chứng minh phân kỳ do thiên kiến sẵn có │
│                              │ của mô hình ngôn ngữ / generator.       │
├──────────────────────────────┼─────────────────────────────────────────┤
│ NC-6: Memory-Clamp Null      │ HỦY BỎ: Tuyên bố về lưu giữ nội sinh.   │
│ (Kẹp bộ nhớ triệt để)        │ Chứng minh mọi hành vi đều do memory.   │
└──────────────────────────────┴─────────────────────────────────────────┘
```

---

## 16. Falsification Matrix

Tiêu chí phản nghiệm quy định các điều kiện bác bỏ giả thuyết nghiên cứu:

| Giả thuyết Kiểm định | Biến quan sát | Kết quả Phản nghiệm (Falsifying Condition) | Diễn giải Khoa học Được phép | Diễn giải BỊ CẤM |
|---|---|---|---|---|
| **$H_1$: Memory-Clamped State Divergence** | $\mathcal{D}_{\text{MC}}$ | $\mathcal{D}_{\text{MC}} \le \mathcal{D}_{\text{null}}$ ($p > 0.05$) hoặc $\mathcal{R}_{\text{atten}} \ge 0.95$ | Không có bằng chứng về sự phân kỳ trạng thái nội sinh độc lập với bộ nhớ. | CẤM: "Toàn bộ kiến trúc Lucia vô dụng." |
| **$H_1$: Order Sensitivity** | $\Delta_{\text{perm}}$ | $\Delta_{\text{perm}} \le \delta_{\text{perm, null}}$ ($p > 0.05$ so với hoán vị) | Trật tự thời gian không tạo ra sự khác biệt trạng thái nội sinh. | CẤM: "Lucia không có khả năng học." |
| **$H_1$: Causal Developmental Dependence** | Fork Divergence | Không vượt qua $\delta_{\text{causal, null}}$ khi can thiệp phản thực nghiệm | Can thiệp đầu vào không tạo ra phân kỳ phát triển nhân quả có ý nghĩa. | CẤM: "Hệ thống hoàn toàn phi nhân quả." |
| **$H_1$: Washout Retention** | $\tau_{1/2}$ | $\tau_{1/2} \le 2$ epochs (tiêu tán tức thời về attractor) | Trạng thái nội sinh không có tính trễ lịch sử dài hạn. | CẤM: "Không có trí nhớ dài hạn." |
| **$H_1$: Adaptation Plasticity** | $\mathcal{A}_{\text{plast}}$ | $\Delta \mathbf{R} \cdot \mathbf{v}_{\text{rev}} \le 0$ (không đổi hướng) | Hệ thống bị đóng băng hoặc bão hòa trạng thái, mất tính dẻo. | CẤM: "Hệ thống có niềm tin kiên định." |

---

## 17. Reproducibility / Fail-Closed Rules

Nhằm bảo toàn tính toàn vẹn khoa học và bảo vệ tuyệt đối mã nguồn sản xuất, harness thiết lập quy tắc Fail-Closed:

1. **Deterministic Seeds:** Toàn bộ seed ngẫu nhiên ($S_{\text{seed}} \in \{2001 \dots 2030\}$) được ghi nhận trong manifest bất biến kèm mã băm SHA-256.
2. **Environment Pinning:** Ghi nhận toàn bộ thông số phần cứng, phiên bản CUDA, thư viện Python và cấu hình runtime.
3. **Immutable Telemetry Storage:** Dữ liệu tensor thô được lưu trữ dạng read-only `.npz` tại `docs/PhaseDocs/Lucia-phase27-Personalized_Individual_Trajectory/evaluation_artifacts/raw_telemetry/`.
4. **FAIL-CLOSED AUDIT GATE (Production Protection Invariant):**
   Trước và sau mỗi phiên mô phỏng, harness kích hoạt lệnh kiểm toán bắt buộc:
   $$\text{git diff --stat src/core electron data}$$
   * **Điều kiện An toàn:**
     - `src/core/** diff = 0`
     - `electron/** diff = 0`
     - `data/** diff = 0`
     - `data/profile.json == {"is_onboarded": false}` (bit-exact)
   * **Xử lý Vi phạm:** Nếu bất kỳ file sản xuất nào bị thay đổi hoặc trạng thái Genesis Onboarding Gate bị can thiệp, toàn bộ tiến trình lập tức bị **HỦY BỎ NGAY LẬP TỨC (ABORT & INVALIDATE)** và phát thông báo lỗi:
     $$\mathbf{FAIL-CLOSED:\; UNAUTHORIZED\_CODEBASE\_MUTATION\_OR\_GENESIS\_BREACH}$$

---

## 18. Decision Gates H1–H5

Harness thiết lập hệ thống 5 cổng quyết định tuần tự:

```text
┌────────────────────────────────────────────────────────────────────────┐
│                   HARNESS SPECIFICATION DECISION GATES                 │
├────────┬──────────────────────────┬────────────────────────────────────┤
│ Gate   │ Tiêu chí Đánh giá        │ Trạng thái Hiện tại                │
├────────┼──────────────────────────┼────────────────────────────────────┤
│ **H1** │ **Stimulus Validity**    │ **BLOCKED — NO VALID STIMULUS      │
│        │ (Họ kích thích không     │             FAMILY IDENTIFIED**    │
│        │  rò rỉ thiên kiến)       │                                    │
├────────┼──────────────────────────┼────────────────────────────────────┤
│ **H2** │ **Calibration Validity** │ **BLOCKED — CALIBRATION            │
│        │ (Ngưỡng nhiễu và lực     │             INSUFFICIENT**         │
│        │  thống kê được chuẩn hóa)│                                    │
├────────┼──────────────────────────┼────────────────────────────────────┤
│ **H3** │ **Harness Identification**│ **READY IN DESIGN**               │
│        │ (Phân định quan sát và   │ (Đã đặc tả xong trong tài liệu)    │
│        │  can thiệp nhân quả)     │                                    │
├────────┼──────────────────────────┼────────────────────────────────────┤
│ **H4** │ **Reproducibility**      │ **READY IN DESIGN**               │
│        │ (Tính tái lập độc lập)   │ (Đã đặc tả xong cơ chế fail-close) │
├────────┼──────────────────────────┼────────────────────────────────────┤
│ **H5** │ **Research Authorization**│ **LOCKED (BLOCKED BY H1 & H2)**   │
│        │ (Ủy quyền triển khai     │                                    │
│        │  harness mã nguồn)       │                                    │
└────────┴──────────────────────────┴────────────────────────────────────┘
```

### Quy tắc Vận hành Cổng:
* **Nếu Gate H1 thất bại:** Dừng toàn bộ tiến trình. Thông báo: `P27 HARNESS BLOCKED — NO VALID STIMULUS FAMILY`.
* **Nếu Gate H2 thất bại:** Dừng toàn bộ tiến trình. Thông báo: `P27 HARNESS BLOCKED — CALIBRATION INSUFFICIENT`.
* **Gate H5 chỉ được xem xét:** Khi và chỉ khi cả 4 cổng H1, H2, H3, H4 đều đạt trạng thái `PASSED`.

---

## 19. Remaining Unknowns

Ba câu hỏi nhận thức luận và kỹ thuật chưa thể giải quyết ở cấp độ đặc tả:

1. **`UNRESOLVED: Non-Leaky Stimulus Generation Mechanism`**
   * *Bản chất:* Liệu về mặt toán học và ngôn ngữ học, có tồn tại một cơ chế tự động nào có thể sinh ra chuỗi đối thoại dài hạn có ý nghĩa nhưng hoàn toàn triệt tiêu được mọi thiên kiến hóa trị và cực tính cảm xúc đối với mô hình nền tảng hay không?
   * *Hiện trạng:* Chưa có lời giải đáp; đây là rào cản nhận thức luận chặn đứng Gate H1.

2. **`UNRESOLVED: Empirical Variance Distribution of MT-LNN under Long Horizon`**
   * *Bản chất:* Phân bố phương sai tích lũy của Coupled MT-LNN sau 50 epochs trong môi trường tương tác đóng là bao nhiêu?
   * *Hiện trạng:* Đòi hỏi phải có đợt chạy hiệu chuẩn kỹ thuật thực tế (Engineering Calibration) mới có thể xác định được $\mathcal{D}_{\text{null}}$ và $\delta_{\text{min}}$.

3. **`UNRESOLVED: Ingress Substrate Attribution & Plasticity`**
   * *Bản chất:* Khi tín hiệu đi qua Ingress hợp lệ, thành phần nội sinh nào ($\mathbf{R}_t$, $\mathbf{W}_{\text{rel}}$, limbic ODE, hay Semantic Graph) sẽ đóng vai trò là cơ chất phát triển chính, và liệu có xảy ra hiện tượng bão hòa biên hay không?
   * *Hiện trạng:* Là câu hỏi thực nghiệm mở, tuyệt đối không được tiên nghiệm ấn định trong đặc tả.

---

## 20. Final Recommendation

Dựa trên kết quả thẩm định khách quan và nghiêm ngặt của đặc tả thiết kế:

```text
================================================================================
                 P27 RESEARCH HARNESS SPECIFICATION VERDICT
================================================================================
Specification Status: COMPLETED & FORMALLY LOCKED
Methodological Verdict: HARNESS NOT YET IMPLEMENTABLE

Blocking Causes:
  1. Gate H1 BLOCKED: NO VALID STIMULUS FAMILY IDENTIFIED
     (Toàn bộ 7 lớp kích thích ứng viên đều thất bại trước các đòn tấn công
      rò rỉ ngữ nghĩa, hóa trị, hoặc thiên kiến mô hình nền tảng).
  2. Gate H2 BLOCKED: CALIBRATION INSUFFICIENT
     (Chưa thể đóng băng ngưỡng nhiễu D_null, delta_min, và cỡ mẫu N chính thức
      khi chưa có dữ liệu tiền thực nghiệm độc lập).

Governance Compliance:
  • src/core/** diff = 0 (BẢO TOÀN NGUYÊN VẸN)
  • electron/** diff = 0 (BẢO TOÀN NGUYÊN VẸN)
  • data/** diff = 0 (BẢO TOÀN NGUYÊN VẸN)
  • data/profile.json == {"is_onboarded": false} (GENESIS GATE STRICTLY LOCKED)
  • P26 Claim C / Claim D: NOT ESTABLISHED
  • P26-R4 / P28: NOT OPENED / NOT AUTHORIZED
  • High-Level Claims (J & K): STRICTLY FORBIDDEN / OUTSIDE SCOPE

Next Authorized Action:
  DỪNG LẠI Ở CẤP ĐỘ ĐẶC TẢ NGHIÊN CỨU.
  TUYỆT ĐỐI KHÔNG VIẾT MÃ NGUỒN HARNESS.
  TUYỆT ĐỐI KHÔNG CHẠY THỬ NGHIỆM KHI CHƯA VƯỢT QUA GATE H1 VÀ GATE H2.
================================================================================
```
