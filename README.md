## Smart light controlled by gesture recognition using Python (MediaPipe) and ESP32-C3

![Project Status](https://img.shields.io/badge/Status-Completed-success)

## 🚀 Giới thiệu (Introduction)
Dự án này là một dự án đơn giản để tìm hiểu về **Computer Vision**, cụ thể là xử lý ảnh với các thư viện AI có sẵn như *OpenCV* và *MediaPipe*. 

Đây là dự án cá nhân có dùng sự hỗ trợ của trợ lý AI (*Gemini*), nhận diện cử chỉ tay để điều khiển độ sáng của vòng **LED NeoPixel** thông qua vi điều khiển **ESP32-C3 Super Mini**. 

Mục tiêu của dự án này là tìm hiểu về quá trình xử lý ảnh, giao thức UDP và các kỹ thuật lọc nhiễu đơn giản.

### 🛠 Phần cứng
* **Vi điều khiển:** ESP32-C3 Super Mini.
* **Actuator:** Vòng đèn LED NeoPixel.
* **Kết nối:** Giao tiếp không dây qua giao thức UDP (User Datagram Protocol).

### 📄 Phần mềm, Thư viện và các công thức được sử dụng:
**Python 3x., OpenCV, MediaPipe, AdaFruit_NeoPixel**
----

#### 1. Bộ lọc Exponential Moving Average (EMA):
$$Y_t = \alpha \cdot X_t + (1 - \alpha) \cdot Y_{t - 1}$$

Trong đó: 
- $Y_t$: Giá trị lọc hiện tại
- $\alpha (0 < \alpha < 1)$: Hệ số làm mượt 
- $Y_{t - 1}$: Giá trị đã lọc trước đó
- $X_n$: Giá trị thô hiện tại vừa đọc được từ MediaPipe
#### 2. Bộ lọc One-Euro (One-Euro Filter):
$$f_c = f_{min} + \beta \cdot |dx|$$
Trong đó:
- $f_c$: Tần số cắt thực tế. $f_c$ càng nhỏ lọc càng mạnh và ngược lại.
- $f_{min}$: Tần số cắt tối thiểu.
- $dx$: Tốc độ di chuyển của ngón tay(pixel/giây).
- $\beta$: Hệ số nhạy
**Cơ chế:** 
> - Nếu $dx$ càng nhỏ (tay đứng yên) $\rightarrow$ $f_c \approx f_{min}$ $\rightarrow$ Lọc kỹ (chống rung).
> - Nếu $dx$ càng lớn (vẩy tay nhanh) $\rightarrow$ $f_c$ tăng vọt $\rightarrow$ Giảm lọc (phản hồi nhanh).

#### 3. Đổi từ tần số cắt thực tế $f_c$ sang hệ số làm mượt $\alpha$:
Ta có:
$$\alpha = \frac{2 \pi f_c \Delta t}{1 + 2 \pi f_c \Delta t}$$
Đặt: $$r = 2 \pi f_c \Delta T$$
Suy ra: $$\alpha = \frac{r}{r + 1}$$

## 🧠 Quá trình phát triển & Học tập (Development & Learning Process)
**Phương pháp tiếp cận:** 
Tự tìm hiểu các kiến thức về OpenCV, MediaPipe và các kỹ thuật xử lý ảnh, lọc nhiễu trên Google, Github và nhờ vào sự giúp đỡ của **Gemini Pro** để giải thích các khối lệnh phức tạp, và từ đó có thể đúc kết, ghi nhớ và tiếp thu kiến thức cho bản thân.

**Kiến thức đúc kết**
1. **Computer Vision:** Biết cách sử dụng các model AI có sẵn, biết cách trích xuất tọa độ `(x, y)` của của 21 điểm mốc trên bàn tay. Hiểu về hiện tượng nhiễu, rung trong xử lý ảnh và các cách giải quyết đơn giản.
2. **Data Serialization:** Học cách đóng gói dữ liệu từ Python và gửi về ESP32-C3 bằng giao thức UDP (User Datagram Protocol).
 
**👤 Author:** Ly Phuc Duong
**🎓 University:**  HCMUTE - Faculty of Electrical and Electronics Engineering
   
## 📞 Get in touch:
-   🔗 **LinkedIn:** [Ly Phuc Duong](https://www.linkedin.com/in/ly-phuc-duong-802b13389)
-   🌐 **Facebook:** [Lý Phúc Dương](https://facebook.com/lpd0201)