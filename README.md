# Smart Light Controlled by Gesture Recognition

![Project Status](https://img.shields.io/badge/Status-Completed-success) ![Python](https://img.shields.io/badge/Python-3.x-blue) ![Hardware](https://img.shields.io/badge/Hardware-ESP32--C3-green)

## 🚀 Giới thiệu (Introduction)
Dự án này là một dự án đơn giản để tìm hiểu về **Computer Vision**, cụ thể là xử lý ảnh với các thư viện AI có sẵn như *OpenCV* và *MediaPipe*. 

Đây là dự án cá nhân có dùng sự hỗ trợ của trợ lý AI (*Gemini*), nhận diện cử chỉ tay để điều khiển độ sáng của vòng **LED NeoPixel** thông qua vi điều khiển **ESP32-C3 Super Mini**. 

Mục tiêu của dự án này là tìm hiểu về quá trình xử lý ảnh, giao thức UDP và các kỹ thuật lọc nhiễu đơn giản.

---

## 🛠 Phần cứng & Phần mềm
### 1. Phần cứng (Hardware)
* **Vi điều khiển:** ESP32-C3 Super Mini.
* **Actuator:** Vòng đèn LED NeoPixel (WS2812B).
* **Kết nối:** Giao tiếp không dây qua giao thức UDP (User Datagram Protocol).

### 2. Phần mềm & Thư viện (Software & Libraries)
* **Ngôn ngữ:** Python 3.x, C++ (Arduino IDE).
* **Thư viện Python:** `opencv-python`, `mediapipe`, `socket`, `json`.
* **Thư viện Arduino:** `Adafruit_NeoPixel`, `WiFiUdp`.

---

## 📐 Cơ sở lý thuyết & Công thức (Mathematical Formulas)

Dự án áp dụng các bộ lọc tín hiệu số để làm mượt dữ liệu tọa độ tay, giúp đèn LED sáng ổn định và không bị rung (jitter).

### 1. Bộ lọc Exponential Moving Average (EMA)
Công thức truy hồi làm mượt dữ liệu:

$$Y_t = \alpha \cdot X_t + (1 - \alpha) \cdot Y_{t - 1}$$

Trong đó: 
- $Y_t$: Giá trị lọc hiện tại.
- $\alpha$: Hệ số làm mượt ($0 < \alpha < 1$).
- $Y_{t - 1}$: Giá trị đã lọc ở bước trước đó.
- $X_t$: Giá trị thô hiện tại vừa đọc được từ MediaPipe.

### 2. Bộ lọc One-Euro (One-Euro Filter)
Đây là bộ lọc nâng cao, tự động điều chỉnh độ mượt dựa trên tốc độ di chuyển. Tần số cắt ($f_c$) được tính như sau:

$$f_c = f_{min} + \beta \cdot |dx|$$

Trong đó:
- $f_c$: Tần số cắt thực tế.
- $f_{min}$: Tần số cắt tối thiểu (Cấu hình mặc định).
- $dx$: Tốc độ di chuyển của ngón tay (pixel/giây).
- $\beta$: Hệ số nhạy tốc độ.

> **Cơ chế hoạt động:** > - Khi $dx$ nhỏ (tay đứng yên) $\rightarrow$ $f_c \approx f_{min}$ $\rightarrow$ **Lọc kỹ** (chống rung).
> - Khi $dx$ lớn (vẩy tay nhanh) $\rightarrow$ $f_c$ tăng vọt $\rightarrow$ **Giảm lọc** (phản hồi nhanh).

### 3. Đổi từ tần số cắt $f_c$ sang hệ số $\alpha$
Để áp dụng vào code, ta cần đổi từ $f_c$ sang $\alpha$ theo các bước biến đổi sau:

Ta có công thức gốc:
$$\alpha = \frac{2 \pi f_c \Delta t}{1 + 2 \pi f_c \Delta t}$$

Đặt biến phụ $r$:
$$r = 2 \pi f_c \Delta t$$

Suy ra công thức cuối cùng:
$$\alpha = \frac{r}{r + 1}$$

*(Với $\Delta t$ là chu kỳ lấy mẫu, $\Delta t \approx 1/FPS$)*.

---

## 🧠 Quá trình phát triển & Học tập (Development & Learning Process)

**Phương pháp tiếp cận:** Tự tìm hiểu các kiến thức về OpenCV, MediaPipe và các kỹ thuật xử lý ảnh, lọc nhiễu trên Google, Github và nhờ vào sự giúp đỡ của **Gemini Pro** để giải thích các khối lệnh phức tạp. Từ đó đúc kết, ghi nhớ và tiếp thu kiến thức cho bản thân.

**Kiến thức đúc kết:**
1.  **Computer Vision:** Biết cách sử dụng các model AI có sẵn, biết cách trích xuất tọa độ `(x, y)` của 21 điểm mốc trên bàn tay. Hiểu về hiện tượng nhiễu, rung trong xử lý ảnh và cách giải quyết đơn giản.
2.  **Data Serialization:** Học cách đóng gói dữ liệu từ Python (JSON/String) và gửi về ESP32-C3 bằng giao thức UDP để đảm bảo tốc độ cao.

---

## 👤 Tác giả (Author)
**Ly Phuc Duong** **🎓 University:** HCMUTE - Faculty of Electrical and Electronics Engineering

## 📞 Liên hệ (Get in touch)
-   🔗 **LinkedIn:** [Ly Phuc Duong](https://www.linkedin.com/in/ly-phuc-duong-802b13389)
-   🌐 **Facebook:** [Lý Phúc Dương](https://facebook.com/lpd0201)