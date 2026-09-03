# Columbina (Damselette) 2D Sprite Avatar Set (v2.0)

Bộ tài nguyên 2D Sprite Avatars hoàn chỉnh cho nhân vật **Columbina (Damselette - Genshin Impact)** được tối ưu hóa cho hệ thống Lucia (`models/avatar/sprites/columbina/`).

---

## 1. Các Cải Tiến Lớn ở Bản v2.0

* **Khóa dải che mắt ren trắng đặc trưng (Signature Blindfold):** Toàn bộ 10 biểu cảm đều ở trạng thái nhắm mắt và đeo dải che mắt viền ren trắng chuẩn nguyên tác Genshin Impact. Khắc phục triệt để hiện tượng mỗi hình một màu mắt.
* **Khử họa tiết lưới/sọc trong tóc (Solid Smooth Hair):** Loại bỏ hoàn toàn hiệu ứng lưới cá (fishnet pattern/mesh) gây sọc loang lổ. Tóc đen mượt mà với lớp highlight hồng phấn bên trong nguyên bản.
* **Làm mịn viền chống răng cưa (Anti-Aliasing Sigma 1.2):** Tăng cường làm mềm viền biên giới với thuật toán Gaussian blur lọc đệm viền, mang lại các cạnh trong suốt cực kỳ sắc nét và mượt mà trên mọi nền màu.
* **Bảo toàn alpha tuyệt đối (Zero-Erosion Matting):** Ứng dụng `isnet-anime` phối hợp cùng `binary_fill_holes` đảm bảo các vùng màu trắng (váy ren, lông vũ cánh chim trên đầu, làn da trắng sứ) không bị ăn mòn hay đục lỗ trong suốt.

---

## 2. Thông số Kỹ thuật & Môi trường Prompt Engineering

* **Nhân vật:** Columbina (Damselette — Fatui Harbinger #3, Genshin Impact)
* **Định dạng file:** Transparent PNG (RGBA 32-bit, nền trong suốt)
* **Độ phân giải:** `1024 x 1024` (1:1 Aspect Ratio)
* **LoRA Model:** `columbina_2a_naiVpred-000039.safetensors`
  * Đường dẫn nguồn: `C:\Users\Lunafiah\Downloads\columbina_2a_naiVpred-000039.safetensors`
  * Trọng số (Weight): `0.8`
* **Khóa Seed:** `88889999` (Khóa Seed cố định góc xoay khuôn mặt, tỷ lệ đầu cánh và trang phục qua 10 biểu cảm)

---

## 3. Cấu trúc Prompt Tiêu Chuẩn (v2.0)

### Base Positive Prompt
```text
masterpiece, best quality, highres, anime official art, 1girl, solo, columbina genshin impact, damselette, fatui harbinger, half body portrait, upper body, facing viewer, white background, simple white background, wing hair ornament, small white feather wings on head, white lace ruffled gothic dress, pale skin, dark black hair with smooth pink inner color streaks, clean gradient black to rose pink, NO fishnet texture, NO mesh pattern in hair, smooth hair coloring, solid hair color, wearing white ornate eye blindfold with lace trim, white decorative eye bandage, eyes completely covered by blindfold, no visible eyes, <lora:columbina_2a_naiVpred-000039:0.8>, cel shaded, crisp clean lines, [CHÈN_TỪ_KHÓA_BIỂU_CẢM]
```

### Negative Prompt
```text
worst quality, low quality, normal quality, blurry, bad anatomy, bad hands, missing fingers, complex background, scenery, text, watermark, signature, open eyes, visible eyes, pupils, irises, fishnet, mesh texture in hair, striped hair, grid pattern hair, jagged edges, aliasing artifacts
```

---

## 4. Danh sách 10 File Sprite & Ánh xạ Cảm xúc trong Lucia

| File | Tên Biểu Cảm | Mô tả cử chỉ & nét mặt v2 | Trạng thái Ánh xạ Lucia (PAD) |
| :--- | :--- | :--- | :--- |
| **`idle.png`** | Nghỉ / Mặc định | Điềm tĩnh, miệng khép nhẹ, tư thế thư thái chuẩn mực | Mặc định (P: 0.0, A: -0.1, D: 0.0) |
| **`speaking.png`** | Nói / Đối thoại | Môi hé mở tự nhiên đang cất tiếng nói | Kích hoạt khi phát audio / Web Audio Lip-Sync |
| **`smile.png`** | Mỉm cười dịu dàng | Mỉm cười khép miệng ấm áp, khóe môi cong nhẹ | Niềm vui ấm áp (P > 0.3) |
| **`excited.png`** | Hào hứng / Vui sướng | Nụ cười rạng rỡ mở rộng hé răng, tràn đầy phấn khởi | Năng lượng cao & hân hoan (P > 0.5, A > 0.4) |
| **`blush.png`** | Ngượng ngùng / Đỏ mặt | Đôi gò má ửng hồng e thẹn, mỉm cười bẽn lẽn | E thẹn / Thân mật (P > 0.4, D < -0.2) |
| **`relaxed.png`** | Thư thái / Trầm tĩnh | Nét mặt êm đềm, nụ cười phảng phất, đầu hơi nghiêng | Tĩnh lặng / Yên bình (P > 0.1, A < -0.3) |
| **`thinking.png`** | Suy nghĩ / Trầm tư | Bàn tay đeo găng trắng đưa lên gần cằm suy ngẫm | Suy luận nhận thức (LLM Reasoning phase) |
| **`concerned.png`**| Lo lắng / Ân cần | Môi hé mở run rẩy nhẹ, biểu cảm quan tâm lo âu | Đồng cảm & lo lắng cho người dùng (P < -0.2) |
| **`sad.png`** | U buồn / Trầm mặc | Khóe miệng trĩu xuống u sầu, đầu hơi cúi trầm mặc | Buồn bã / Mất mát (P < -0.4, A < -0.2) |
| **`angry.png`** | Dỗi hờn / Phụng phịu | Bĩu môi phụng phịu đáng yêu, hàng lông mày nhíu trên dải che mắt | Phụng phịu / Quyết đoán (P < -0.3, D > 0.4) |

---

## 5. Trạng thái Lưu trữ & Đóng gói

1. **Thư mục Sprite RGBA:**
   * [`models/avatar/sprites/columbina/`](file:///c:/Users/Lunafiah/Desktop/My_project/Lucia/models/avatar/sprites/columbina/) (chứa đủ 10 file `.png` 1024x1024 nền trong suốt)
2. **File nén đóng gói:**
   * [`models/avatar/sprites/columbina_sprites.zip`](file:///c:/Users/Lunafiah/Desktop/My_project/Lucia/models/avatar/sprites/columbina_sprites.zip) (dung lượng ~10 MB, sẵn sàng chia sẻ/di chuyển)
