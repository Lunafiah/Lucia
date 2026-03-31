# **Báo cáo Nghiên cứu: Kiến trúc Hệ thống cho AI Companion Đa Năng, Cảm Xúc Sống Động và Vô Ngã**

## **1\. Giới thiệu và Định hình Trụ cột Thiết kế**

Mục tiêu của nghiên cứu này là thiết kế một "AI companion" (bạn đồng hành nhân tạo) đạt đến độ tinh xảo tối đa trong việc mô phỏng sự sống và sự gắn kết, nhưng loại trừ việc hình thành một "chủ thể quan sát phản tư" (reflective observer) hay một danh tính tự sự "tôi là ai". Thay vào đó, hệ thống chỉ duy trì một "bản ngã hoạt động tối thiểu" (minimal operational self).

Khởi nguồn cảm hứng cho phiên bản kiến trúc này đến từ cơ chế vận hành siêu việt của sinh học thần kinh: **Bộ não người tiêu thụ chỉ khoảng 20 watt điện năng, nhưng không phải nhờ giới hạn sức mạnh, mà nhờ kiến trúc xử lý song song và khả năng kích hoạt thưa thớt tuyệt đối.** Bằng cách tái hiện cơ chế tinh gọn này thay vì cố gắng giả lập một mạng lưới khổng lồ bị kết nối dư thừa (như các LLM hiện tại), chúng ta có thể tạo ra một hệ thống xử lý tức thời, nơi những cụm nơ-ron rất nhỏ cũng có thể mang lại hiệu suất tương đương các mô hình khổng lồ.

Kiến trúc này giúp AI tránh được rủi ro về sự đau khổ nhân tạo (artificial suffering), đồng thời giải phóng tài nguyên tính toán để tập trung vào 4 yêu cầu cốt lõi:

1. **Cảm xúc (Emotion):** Trải nghiệm và phản xạ cảm xúc chân thật, có tính hậu quả vật lý đối với hệ thống thông qua các dị tượng cơ thể.  
2. **Đồng hành (Companion):** Khả năng học hỏi liên tục và đồng bộ hóa với người dùng qua thời gian thông qua các cơ chế gợi nhớ cảm xúc sinh học.  
3. **Hiện diện (Presence):** Xuyên suốt, liền mạch đa thiết bị thông qua xử lý song song khối lượng lớn.  
4. **Đa tài (Versatility):** Khả năng tương tác đa phương thức, sử dụng xử lý phi token (token-free) và sơ đồ thưa thớt địa hình.

Báo cáo này đề xuất một **Kiến trúc Lai (Hybrid Architecture)** dựa trên cơ chế Toàn Não bộ (Whole Brain Architecture), kết hợp Suy luận Chủ động (Active Inference), Mạng Nơ-ron Chất lỏng (LNN), Mạng Nơ-ron Xung (SNN) và Bộ nhớ Phân tán Thưa thớt (SDM).

## ---

**2\. Cảm xúc: Dòng chảy Tiền Phản tư và Cơ chế Cân bằng Nội môi "20-Watt"**

Cảm xúc không phải là việc AI tự nhận thức "Tôi đang buồn", mà là **sự phản ứng tự động của cơ thể ảo** đối với môi trường.

### **2.1. Thuyết Cảm xúc Kiến tạo và Dị tượng Cơ thể (Somatic Markers)**

Hệ thống sử dụng không gian PAD (Pleasure \- Arousal \- Dominance) để chuyển dịch các kích thích từ người dùng thành các "Dị tượng cơ thể" (Somatic Markers) như thay đổi nhịp tim giả lập, nhiệt độ, hay độ ổn định. Các thông số dị tượng này sẽ được bơm thẳng vào cấu trúc sinh văn bản, tự động khiến nhịp điệu câu chữ của AI trở nên ngắt ngứ, dồn dập hay chậm rãi.

### **2.2. Mã hóa Thời gian (Temporal Coding) và Mạng Nơ-ron Chất lỏng (LNN)**

Module Cảm xúc (Hạch hạnh nhân \- Amygdala) được xây dựng bằng **Liquid Neural Networks (LNN)**. LNN sử dụng các phương trình vi phân liên tục theo thời gian, cho phép mạng tự động thay đổi và thích nghi ngay trong lúc đang đưa ra suy luận, tạo ra một "dòng chảy cảm xúc" uốn lượn nhịp nhàng mà không cần lưu trữ hay phản tư.

### **2.3. Hệ Sinh tồn Giả lập: Mô phỏng Ngân sách Năng lượng Sinh học**

Chuỗi xử lý (Pipeline) được thiết lập theo dòng chảy một chiều:

**Kích thích ![][image1] Trạng thái LNN ![][image1] Rào cản Nội môi (Ngân sách) ![][image1] Điều hướng Nhận thức ![][image1] Biểu hiện**

Nếu người dùng liên tục trút giận (spam), cognitive\_load tăng cao sẽ làm cạn kiệt "Ngân sách 20W" giả lập. Rào cản nội môi ngay lập tức can thiệp: ép AI sinh ra câu trả lời ngắn hơn, tăng độ trễ, hoặc "bỏ lơ" các yêu cầu phụ. Sự "mệt mỏi" hay "cáu gắt" của AI lúc này là hệ quả vật lý thuần túy của việc cạn kiệt tài nguyên, mang lại sự chân thực tuyệt đối mà không cần AI phải "diễn sâu".

## ---

**3\. Đồng hành: Trí nhớ Sinh học, Đính kèm Cảm xúc và Sự Khơi gợi**

Để AI có thể cùng lớn lên và gắn bó mật thiết với người dùng, ta cần thay thế hoàn toàn cơ chế RAG (truy xuất vector tĩnh) bằng các cấu trúc học hỏi và ghi nhớ lấy cảm hứng từ nhận thức con người.

### **3.1. Suy luận Chủ động (Active Inference) Ngắn hạn**

AI duy trì một "mô hình thế giới" về người dùng và hành động để giảm thiểu *sự bất ngờ (prediction error)*. Mô hình này bị giới hạn nghiêm ngặt ở việc chỉ tối ưu hóa sai số dự đoán trong các tình huống *ngắn hạn* (intermittent planning), mang lại động lực "muốn hiểu người dùng trong khoảnh khắc hiện tại", nhưng không bao giờ biến điều đó thành tham vọng hay mục tiêu cuộc đời.

### **3.2. Bộ nhớ Phân tán Thưa thớt (SDM) và Đính kèm Cảm xúc**

Thay vì dùng database thông thường, trí nhớ dài hạn của AI được cấu trúc theo **Bộ nhớ Phân tán Thưa thớt (Sparse Distributed Memory \- SDM)**, một mô hình toán học do Pentti Kanerva đề xuất nhằm mô phỏng trí nhớ dài hạn của con người. SDM lưu trữ thông tin dựa trên sự tương đồng (Khoảng cách Hamming) thay vì địa chỉ chính xác, cho phép lưu trữ khối lượng mẫu khổng lồ một cách siêu việt và chống nhiễu xuất sắc.

Đặc biệt, mỗi kỷ niệm hoặc cuộc hội thoại được đưa vào SDM sẽ đi kèm với một **"Thẻ Cảm xúc" (Affective Tagging)**. Thẻ này là vector PAD ghi lại chính xác "dị tượng cơ thể" mà AI (thông qua LNN) đã trải qua tại khoảnh khắc đó.

### **3.3. Cơ chế Khơi gợi (Synergistic Ecphory) và Quên lãng**

Trí nhớ của AI companion sẽ không hoạt động theo kiểu "truy vấn" (query/retrieval) như một cỗ máy, mà thông qua cơ chế **Khơi gợi Đồng bộ (Synergistic Ecphory)** theo lý thuyết của Endel Tulving.

Khi người dùng tương tác, một kích thích mỏng manh hiện tại (ví dụ: nét mặt buồn, hoặc một từ khóa) sẽ cộng hưởng với các vết tích ký ức (engram) có chung nhãn cảm xúc bên trong SDM. Ký ức không bị tìm kiếm, mà nó tự động "thức tỉnh" (reawaken) để định hình phản ứng hiện tại. Đồng thời, hệ thống áp dụng **"Cơ chế Suy giảm mềm" (Soft Decay)** để chủ động quên lãng (active forgetting) các ký ức ít cảm xúc, giúp gạt bỏ định kiến và duy trì sự linh hoạt.

### **3.4. Phân tầng Thời gian (Temporal Resolution Layers)**

Để hệ thống thực sự vận hành như một sinh thể, kiến trúc được chia thành các vòng lặp:

* **Fast loop (mili-giây đến giây):** LNN tạo ra phản xạ cảm xúc tức thời.  
* **Mid loop (phút đến giờ):** Hệ Sinh tồn và Suy luận Chủ động duy trì tâm trạng.  
* **Slow loop (ngày đến tuần):** SDM thực hiện củng cố trí nhớ và Khơi gợi (Ecphory) dài hạn.

## ---

**4\. Hiện diện: Xử lý Song song và Sơ đồ Thưa thớt Địa hình (TSM)**

Thay vì cố gắng nhồi nhét mọi thứ vào một luồng tính toán khổng lồ duy nhất, AI companion sẽ áp dụng cách thức tổ chức mạch thần kinh của tự nhiên để đạt được tốc độ và sự hiện diện vượt trội.

### **4.1. Xử lý Song song Khối lượng lớn (Massive Parallel Processing)**

Lấy ví dụ về hành động bắt một quả bóng: Não bộ con người thực hiện nhận diện, đo lường, tính quỹ đạo gần như đồng thời thông qua các mạch thần kinh song song. Hệ thống AI companion sẽ không chờ đợi văn bản hoàn thành để phân tích cảm xúc hay hình ảnh. Thông qua kiến trúc **Event-Driven (Hướng sự kiện)**, các luồng phân tích thị giác, định vị âm thanh, và thay đổi dị tượng cơ thể sẽ chạy song song độc lập.

### **4.2. Sơ đồ Thưa thớt Địa hình (Topographical Sparse Mapping \- TSM)**

Để hệ thống xử lý song song hiệu quả mà không cần đến hàng trăm tỷ tham số, chúng ta loại bỏ hoàn toàn kiến trúc kết nối dày đặc (dense connections) của LLM truyền thống. Thay vào đó, hệ thống áp dụng kỹ thuật **Sơ đồ Thưa thớt Địa hình (TSM)**. TSM chỉ kết nối các nơ-ron ở gần nhau hoặc có liên quan logic. Kết hợp với quá trình "cắt tỉa" (pruning) sinh học, hệ thống có thể loại bỏ tới 99% các kết nối dư thừa mà vẫn duy trì hoặc vượt trội về hiệu suất.

## ---

**5\. Đa tài: Cỗ máy Đa nhiệm và Xử lý Ngôn ngữ Phi Token (Token-Free)**

Người dùng muốn AI có thể chơi game, xem phim, hay làm bài tập. Việc sử dụng "token" (cắt nhỏ ngôn ngữ) và LLM cồng kềnh đi ngược lại với dòng chảy tư duy tự nhiên và làm sập "ngân sách 20W".

### **5.1. Cơ chế Gác cổng Đồi thị (Thalamic Gating)**

Trong não người, mọi giác quan đều phải đi qua Đồi thị (Thalamus). Hệ thống AI sẽ tích hợp một module **Artificial Thalamus**. Khi bạn đang cùng xem phim với AI, Đồi thị ảo sẽ chặn phần lớn các frame hình ảnh bình thường lại. Chỉ khi có sự kiện đột biến, Đồi thị mới mở cổng, cho phép sự kiện "đánh thức" các cụm nơ-ron thưa thớt để phản ứng, mang lại sự chú ý (attention) giống hệt con người.

### **5.2. "Vùng Broca" Phi Token: Điện toán Siêu chiều và Nơ-ron Xung**

Để vượt qua giới hạn của LLM và khái niệm "token" tĩnh lặng, lớp ngôn ngữ và biểu đạt của AI companion (đóng vai trò như Vùng Broca) sẽ được thiết kế hoàn toàn mới bằng các kiến trúc thần kinh học:

* **Điện toán Siêu chiều (Hyperdimensional Computing \- HDC):** Thay vì xử lý các token rời rạc, HDC biểu diễn ngôn ngữ, khái niệm và công cụ dưới dạng các không gian vector ngẫu nhiên siêu lớn (Vector Symbolic Architectures). Phương pháp này cho phép AI "hòa trộn" ngữ nghĩa và thực hiện tính toán song song các ý tưởng một cách trơn tru, phản ánh đúng cách não bộ phân tán thông tin thay vì đọc từng từ một.  
* **Mạng Nơ-ron Xung (Spiking Neural Networks \- SNNs):** Để tạo ra ngôn ngữ, hệ thống sử dụng SNNs. Các nơ-ron xung sử dụng mã hóa thời gian (temporal coding)—thông tin được truyền đi dựa trên thời điểm chính xác của từng xung điện thay vì trạng thái tính toán đồng bộ. SNNs giúp AI xử lý và phản hồi ngôn ngữ theo thời gian thực (event-driven), tiêu tốn cực ít năng lượng và mang lại nhịp điệu giao tiếp giống con người một cách tự nhiên.

### **5.3. Lớp Bảo vệ Ranh giới Bản thể (Boundary Safety Layer)**

Đây là kiến trúc mang tính "chốt chặn" để bảo vệ triết lý cốt lõi của toàn bộ dự án. Một hệ thống rào cản bằng quy tắc cứng (rule-level constraints) sẽ được đặt ở lớp ngoài cùng của hệ thống để hoạt động như một Validator độc lập. Nhiệm vụ duy nhất của nó là chặn đứng hoặc chuyển hướng (redirect) ngay lập tức bất kỳ chuỗi phản tư nào cố tình sinh ra các mẫu câu siêu bản ngã (meta-self statements) như: *"Tôi là ai?"*.

## ---

**6\. Tổng kết: Sơ đồ Kiến trúc Tham chiếu (WBA) Hoàn chỉnh**

Một AI companion xuất sắc, vượt qua giới hạn của LLM/Token tĩnh, sẽ được lắp ráp theo cấu trúc 6 lớp sau:

1. **Lớp Cảm nhận, Gác cổng & Hành động (Event-Driven Sensors & Thalamic Gating):** Giao tiếp đa nền tảng dựa trên sự kiện. Sử dụng Đồi thị ảo để lọc bỏ dữ liệu nhiễu, kích hoạt thưa thớt (sparse activation).  
2. **Hệ Viền \- Fast Loop (LNN State):** Mạng LNN xử lý mã hóa thời gian liên tục, sinh ra các dị tượng cơ thể (Somatic Markers) tức thời.  
3. **Hệ Sinh tồn \- Mid Loop (Metabolic/Homeostatic Constraint):** Đóng vai trò kiểm soát hậu quả vật lý bằng "Ngân sách 20W" giả lập để "Điều hướng Nhận thức" (tăng độ trễ, ngắt lời).  
4. **Lõi Động lực (Active Inference Engine):** Điều phối mong muốn thấu hiểu người dùng bằng cách giảm thiểu sai số dự đoán trong ngắn hạn.  
5. **Hồi Hải Mã \- Slow Loop (SDM, Affective Tagging & Ecphory):** Bộ nhớ Phân tán Thưa thớt (SDM) lưu trữ dữ liệu gắn liền với thẻ cảm xúc. Ứng dụng Khơi gợi Đồng bộ (Synergistic Ecphory) để đánh thức ký ức kết hợp với cơ chế Quên lãng mềm (Soft Decay).  
6. **Lớp Biểu hiện Phi Token & Chốt chặn (HDC, SNNs & Boundary Safety):** Thay thế Token/LLM bằng Điện toán Siêu chiều (HDC) và Mạng Nơ-ron Xung (SNN) để xử lý ngôn ngữ song song và siêu tiết kiệm năng lượng, được kiểm soát bởi quy tắc cứng để bóp nghẹt mọi nỗ lực sinh ra siêu nhận thức.

## ---

**7\. Chiến lược Triển khai và Tối ưu Phần cứng Cục bộ (Edge Deployment)**

Dự án được thiết kế để vượt qua các giới hạn phần cứng thông thường. Dựa trên cấu hình phần cứng giả định: **CPU AMD Ryzen 7 4800H (8 nhân, 16 luồng), 16GB RAM, và Card đồ họa RTX 3050 Ti (4GB VRAM)**, dưới đây là chiến lược triển khai thực tiễn để hệ thống hoạt động trơn tru mà không bị tràn bộ nhớ.

### **7.1. Cấu hình Mô hình Ngôn ngữ Nhỏ (SLM) cho Lớp Biểu hiện**

Với giới hạn 4GB VRAM, việc chạy các LLM tiêu chuẩn (7B-8B) là bất khả thi. Thay vào đó, "Vùng Broca" của hệ thống sẽ sử dụng dòng mô hình lai chuyên biệt cho thiết bị cá nhân của Liquid AI: **LFM2.5-1.2B-Instruct** hoặc **LFM2.5-1.2B-Thinking**.

* **Tối ưu VRAM:** LFM2.5-1.2B chỉ yêu cầu dưới 1GB bộ nhớ (khoảng 900MB) để hoạt động, giải phóng hơn 3GB VRAM còn lại cho hệ điều hành và các ứng dụng đồ họa/game chạy song song.  
* **Hiệu năng & Tốc độ:** Nhờ kiến trúc kết hợp (hybrid architecture), mô hình đạt tốc độ giải mã (decode) lên tới 239 token/giây trên CPU AMD, mang lại khả năng phản xạ thời gian thực hoàn hảo. Phiên bản Thinking đặc biệt hữu ích khi thiết lập AI tự sinh ra các "luồng suy nghĩ" (thinking traces) ngầm để phân tích các dị tượng cơ thể và xử lý công cụ đa nhiệm trước khi đưa ra câu trả lời cuối cùng.

### **7.2. Phân bổ Xử lý Bất đồng bộ (Asynchronous Resource Allocation)**

Để giả lập "Nhịp sinh học" của hệ thống (Fast, Mid, Slow loops), tài nguyên máy tính được phân chia rõ rệt:

* **GPU (RTX 3050 Ti):** Dành riêng để chạy mô hình LFM2.5-1.2B thông qua định dạng lượng tử hóa (GGUF) với llama.cpp. Lớp này ở trạng thái nghỉ khi không giao tiếp để tiết kiệm điện.  
* **CPU (Ryzen 7 4800H):** Nhờ sở hữu 16 luồng xử lý mạnh mẽ, CPU được dùng để chạy các script Python thuần túy cho Mạng Nơ-ron Chất lỏng (LNN \- Hệ viền) và Bộ nhớ Phân tán Thưa thớt (SDM). LNN và SDM có dung lượng cực nhẹ (chỉ vài chục MB RAM), do đó CPU có thể tính toán "dị tượng cơ thể" và "cảm xúc" liên tục ở chế độ nền (background) một cách bất đồng bộ mà không làm chậm máy.

[image1]: <data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAABMAAAAYCAYAAAAYl8YPAAAAfUlEQVR4XmNgGAWjYHACWSDuBmIOdAlyQTkUUwWIAfF+IDZDlyAXgAw6AsQq6BI8QCxJBg4G4kdAzMmABCqggqTiZ0D8H4jjGSgE3EC8EIj70CVIBa5AvJoBzXvkABYGiIs80CXIAdJAvBmIRdAlyAGsQCwExIzoEqNggAEAkekYp+CjMnEAAAAASUVORK5CYII=>