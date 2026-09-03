# Live2D Model: Hoshino Ai (推しの子 / Oshi no Ko)

Mô hình Live2D Cubism hoàn chỉnh của **Hoshino Ai (星野 アイ)** được tích hợp vào hệ sinh thái avatar của **Lucia**.

---

## 1. Cấu trúc tệp tin (File Structure)

```
models/avatar/live2d/HoshinoAi/
├── Hoshino_Ai.model3.json      # File cấu hình định danh mô hình chính (Cubism 3/4)
├── Hoshino_Ai.moc3             # Dữ liệu mô hình nhị phân Live2D Cubism
├── Hoshino_Ai.physics3.json    # Mô phỏng vật lý (tóc, ruy băng, phụ kiện đung đưa)
├── Hoshino_Ai.cdi3.json        # Định nghĩa thông số tham số & tên hiển thị (Display Info)
├── donghua.motion3.json        # Motion chuyển động hoạt ảnh cơ bản
│
├── Hoshino_Ai.8192/            # Atlas vân bề mặt Texture độ phân giải cao (8192x8192)
│   ├── texture_00.png          # Texture chính (khuôn mặt, mắt, tóc, trang phục)
│   └── texture_01.png          # Texture phụ kiện & hiệu ứng
│
├── Expressions (Biểu cảm):
│   ├── xinxin.exp3.json        # Mắt sao sáng / Trái tim (Biểu tượng thần tượng Oshi no Ko)
│   ├── st.exp3.json            # Thè lưỡi tinh nghịch (Playful / Cheeky)
│   ├── sq.exp3.json            # Hờn dỗi / Tức giận (生气 - Pout / Angry)
│   ├── ku.exp3.json            # Khóc / Rơi nước mắt (哭 - Sad / Crying)
│   ├── ga.exp3.json            # Ngạc nhiên / Há hốc (Surprised)
│   ├── zs1.exp3.json           # Dáng pose thần tượng 1 (Pose 1)
│   └── zs2.exp3.json           # Dáng pose thần tượng 2 (Pose 2)
│
└── Instructions.txt            # Hướng dẫn và thông tin bản quyền từ tác giả model
```

---

## 2. Liên kết thông số với hệ thống Lucia (Parameter Mapping)

### A. Tự động Nhép môi (Lip-Sync Engine)
* **Tham số:** `ParamMouthOpenY`
* **Cơ chế:** Phân tích luồng âm thanh thoại qua `lip-sync.js` của Lucia và điều khiển độ mở của miệng theo biên độ âm thanh thời gian thực.

### B. Tự động Chớp mắt (Natural Eye Blink)
* **Tham số:** `ParamEyeLOpen`, `ParamEyeROpen`
* **Cơ chế:** Chu kỳ chớp mắt ngẫu nhiên tự nhiên (3 - 5 giây/lần).

### C. Bản đồ cảm xúc PAD (Pleasure - Arousal - Dominance Mapping)

| Trạng thái PAD của Lucia | File Expression kích hoạt | Hiệu ứng trực quan |
| :--- | :--- | :--- |
| **High Pleasure ($P > 0.5$)** | `xinxin.exp3.json` | Mắt sáng lấp lánh hình ngôi sao rực rỡ đặc trưng của Ai |
| **Playful / Cheeky ($A > 0.4, P > 0.3$)** | `st.exp3.json` | Nháy mắt thè lưỡi tinh nghịch chuẩn phong cách idol |
| **Low Pleasure ($P < -0.3$)** | `ku.exp3.json` | Khóc, rơi lệ, biểu cảm u sầu |
| **High Tension ($T > 0.4, P < 0$)** | `sq.exp3.json` | Phồng má hờn dỗi, chân mày cau nhẹ |
| **Surprise / Shock ($A > 0.6$)** | `ga.exp3.json` | Mắt mở to, miệng há ngạc nhiên |
| **Idol Presentation** | `zs1.exp3.json` / `zs2.exp3.json` | Đổi dáng tay pose idol tự tin |

---

## 3. Tác giả & Bản quyền (Credit & Terms)
* **Nhân vật:** Hoshino Ai — tác phẩm *Oshi no Ko* (Aka Akasaka / Mengo Yokoyari).
* **Modeler / Painter:** KenKenMo6 (https://twitter.com/KenKenMo6).
* **Quy định sử dụng:**
  * Cho phép sử dụng phi thương mại cho các dự án cá nhân, làm video.
  * Nghiêm cấm sử dụng để livestream thu lợi nhuận thương mại hoặc phát tán bán lại.
