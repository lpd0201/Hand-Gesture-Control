## Project Description: Smart light controlled by gesture recognition using Python (MediaPipe) and ESP32-C3

![Project Status](https://img.shields.io/badge/Status-Completed-success)

## 🚀 Giới thiệu (Introduction)
Dự án này là một dự án đơn giản để tìm hiểu về **Computer Vision**, cụ thể là xử lý ảnh với các thư viện AI có sẵn như *OpenCV* và *MediaPipe*. 

Đây là dự án cá nhân nhận diện cử chỉ tay để điều khiển độ sáng của vòng **LED NeoPixel** thông qua vi điều khiển **ESP32-C3 Super Mini**. 

Mục tiêu của dự án này là tìm hiểu về quá trình xử lý ảnh, giao thức UDP và các kỹ thuật lọc nhiễu đơn giản.

### 🛠 Phần cứng
* **Vi điều khiển:** ESP32-C3 Super Mini
* **Actuator:** Vòng đèn LED NeoPixel 
* **Kết nối:** Giao tiếp không dây qua giao thức UDP (User Datagram Protocol)

### 📄 Phần mềm & Thư viện
* *Python 3x., OpenCV, MediaPipe, AdaFruit_NeoPixel*

## 🧠 Quá trình phát triển & Học tập (Development & Learning Process)
**Phương pháp tiếp cận:** 
Tự tìm hiểu các kiến thức về OpenCV, MediaPipe và các kỹ thuật xử lý ảnh, lọc nhiễu trên Google, Github và nhờ vào sự giúp đỡ của **Gemini Pro** để giải thích các khối lệnh phức tạp, và từ đó có thể đúc kết, ghi nhớ và tiếp thu kiến thức cho bản thân.

**Kiến thức đúc kết**
1. **Computer Vision:** Biết cách sử dụng các model AI có sẵn, biết cách trích xuất tọa độ `(x, y)` của của 21 điểm mốc trên bàn tay. Hiểu về hiện tượng nhiễu Jitter và cách xử lý bằng bộ lọc Exponential Multiple Average (EMA) và cải thiện hơn bằng One-euro Filter.
2. **Data Serialization:** Học cách đóng gói dữ liệu từ Python và gửi về ESP32-C3 bằng giao thức UDP.
3. 

## 📂 Folder Structure
```text
SmartLight/
├── firmware/           # Include .bin file 
│   ├── boot.py
│   └── main.py 
├── pc_app/                # Main source
│   ├── gesture_recognition.py
├── include/            
├── docs/               
└── README.md           
```

**👤 Author:** *Ly Phuc Duong*
**🎓 University:**  HCMUTE - Faculty of Electrical and Electronics Engineering
   
## 📞 Get in touch:

-   🔗 **LinkedIn:** [Ly Phuc Duong](https://www.linkedin.com/in/ly-phuc-duong-802b13389)
-   🌐 **Facebook:** [Lý Phúc Dương](https://facebook.com/lpd0201)



