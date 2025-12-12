import cv2
import mediapipe as mp
import socket
import time
import math
import json
import numpy as np

# VẪN CÒN BỊ NHIỄU

# Bộ lọc One-euro filter 
# + Tay giữ yên -> Lọc tối đa
# + Tay vẩy nhanh -> Lọc tối thiểu
class OneEuroFilter:
    def __init__(self, min_cutoff = 1.0, beta = 0.0, d_cutoff = 1.0):
        
        # min_cutoff : tần số cắt tối thiểu (càng nhỏ lọc càng mạnh)
        # beta : hệ số tốc độ 
        # Cấu hình các thuộc tính
        self.min_cutoff = min_cutoff
        self.beta = beta
        self.d_cutoff = d_cutoff

        # Đặt các biến ghi nhớ cho OEF
        self.x_prev = 0.0 # Giá trị đã lọc lần trước
        self.dx_prev = 0.0 # Tốc độ lần trước
        self.time_prev = 0.0 # Thời gian lần trước
    
    # Viết các hàm phương thức

    def smoothing_factor(self, time_elapsed, cutoff):
        """ Hàm đổi tần số cắt sang hệ số alpha """
        r = 2 * math.pi * cutoff * time_elapsed
        return r / (r + 1)
    
    # Bộ lọc exponential moving average 
    def exponential_smoothing(self, a, x, x_prev):
        return a * x + (1 - a) * x_prev
    
    def process(self, x):
        t = time.time()
        # Nếu chưa có lần đo nào -> set time_prev = thời gian đầu
        if self.time_prev == 0.0:
            self.time_prev = t
            self.x_prev = x
            return x
        # time_elapsed = khoảng thời gian máy tính chạy 2 vòng lặp
        time_elapsed = t - self.time_prev
        if time_elapsed <= 0.0: return self.x_prev


    # 1. Tính vận tốc thay đổi tín hiệu (dx)
        
        a_d = self.smoothing_factor(time_elapsed, self.d_cutoff) # Tính giá trị alpha cho bộ lọc vận tốc
        
        dx = (x - self.x_prev) / time_elapsed # Tính vận tốc thô, công thức v = (x - x0) / time_elapsed
        
        dx_hat = self.exponential_smoothing(a_d, dx, self.dx_prev) # Làm mượt vận tốc thô (dx), dùng cho tính tần số cắt

    # 2. Tính tần số cắt thích ứng (cutoff)
        
        # Sau khi làm mượt vận tốc (dx_hat) -> thay vào công thức fc = fcMin + beta * dx_hat để tìm tần số cắt fc        
        cutoff = self.min_cutoff + self.beta * abs(dx_hat)
        
        # Khi đã có tần số cắt fc, đưa vào hàm smoothing_factor để tìm ra hệ số alpha cho bộ lọc tín hiệu chính
        a = self.smoothing_factor(time_elapsed, cutoff)

    # 3. Lọc tín hiệu
        # Sau khi có alpha, ta chỉ cần tính     
        x_hat = self.exponential_smoothing(a, x, self.x_prev)

        # 4. Lưu trạng thái cho lần sau
        self.x_prev = x_hat
        self.dx_prev = dx_hat
        self.time_prev = t

        return x_hat

# Cấu hình
ESP_IP = "10.49.247.217"
ESP_PORT = 4210

# Tạo gói tin UDP
sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

# Gọi module hands từ thư viện solutions
mp_hands = mp.solutions.hands

hands = mp_hands.Hands(
    static_image_mode = False, 
    max_num_hands = 1, 
    model_complexity = 1, # Độ phức tạp mô hình AI, 1 là mode full
    min_detection_confidence = 0.7, # Ngưỡng tin cậy khi phát hiện
    min_tracking_confidence = 0.7 # Ngưỡng tin cậy khi theo dõi chuyển động
)

# Tạo công cụ vẽ các chấm và các khớp
mp_draw = mp.solutions.drawing_utils

last_send_time = 0

brightness_filter = OneEuroFilter(min_cutoff = 0.01, beta = 0.5)


def send_udp_command(r, g, b):
    global last_send_time # Chuyển biến last_send_time thành biến toàn cục (như con trỏ trong C)
    # Chỉ gửi lệnh mỗi 50ms (20 lần/s) để tránh esp bị ngộp
    if time.time() - last_send_time < 0.05:
        return
    # Tạo gói tin
    payload = {
        "r" : int(r),
        "g" : int(g),
        "b" : int(b)
    }
    try:
        # Chuyển dictonary thành chuỗi rồi biến chuỗi thành văn bản dạng byte (với .encode("utf-8"))
        ms = json.dumps(payload).encode('utf-8') 
        # Gửi gói bytes đến ip và port của esp32-c3
        sock.sendto(ms, (ESP_IP, ESP_PORT))
        # Cập nhật lại lần gửi cuối
        last_send_time = time.time()
    except Exception as e:
        pass # Nếu lỗi thì không bị crash mà chỉ in ra

def main():
    
    cap = cv2.VideoCapture(0) # Bật webcam mặc định (VideoCapture(0))

    print("System started! Press 'q' to exit.")

    if not cap.isOpened():
        print("Can't open camera!")
        return
    
    while True:
        success, img = cap.read() # Chụp một khung hình, hệ thống sẽ tự động chụp khoảng 60 khung mỗi giây
        if not success: break # Nếu không có frame nào sẽ tiến hành thoát

        # Lật ảnh để tránh hiện tượng gương
        img = cv2.flip(img, 1)
        
        # Chuyển từ bgr của opencv sang rgb trong mediapipe
        img_rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        
        # Gửi ảnh đã chuyển đổi cho AI xử lý
        results = hands.process(img_rgb)

        lm_list = [] # Danh sách rỗng chứa tọa độ ngón tay

        # Mediapipe sẽ trả về tọa độ được chuẩn hóa (0, 1), ta cần chuyển sang tọa độ pixel
        if results.multi_hand_landmarks:
            for hand_lms in results.multi_hand_landmarks:
                # Vẽ các khớp và đốt tay
                mp_draw.draw_landmarks(img, hand_lms, mp_hands.HAND_CONNECTIONS)
                # Duyệt qua tọa độ x, y và trả về xem đó là ngón nào
                # ID = 4 -> ngón cái, ...
                for id, lm in enumerate(hand_lms.landmark):
                    h, w, c = img.shape # lấy kích thước thực tế của cửa sổ camera
                    # Chuyển tọa độ chuẩn hóa sang pixel 
                    cx, cy = int(lm.x * w), int(lm.y * h)
                    lm_list.append([id, cx, cy]) # Thêm vào list id ngón, tọa độ x và y (theo pixels)
        if len(lm_list) != 0:
            # Lấy tọa độ x, y của ngón cái [4] và ngón trỏ [8]
            x1, y1 = lm_list[4][1], lm_list[4][2]
            x2, y2 = lm_list[8][1], lm_list[8][2]

            # Vẽ đường nối giữa 2 ngón và 2 chấm tròn
            cv2.circle(img, (x1, y1), 10, (178, 0, 255), cv2.FILLED)
            cv2.circle(img, (x2, y2), 10, (178, 0, 255), cv2.FILLED)
            cv2.line(img, (x1, y1), (x2, y2), (178, 0, 255), 3)

            # Tính độ sáng bằng cách di chuyển ngón cái và trỏ bằng khoảng cách Euclid
            # Trả về length tính theo pixel 
            length = math.hypot(x2 - x1, y2 - y1) # Tính độ lớn nên không quan trọng thứ tự
            # Hàm nội suy
            raw_brightness = np.interp(length, [30, 200], [0, 255])

            # Bộ lọc One-euro filter thay cho EMA
            filtered_brightness = brightness_filter.process(raw_brightness)
            current_val = int(filtered_brightness)

            # Logic vùng màu
            wrist_x = lm_list[0][1] # Lấy tọa độ x của cổ tay
            w_screen = img.shape[1] # Chiều rộng ảnh, 640x480 thì lấy 640
            zone = ""
            r, g, b = 0, 0, 0
            if wrist_x < w_screen / 3:
                r, g, b = current_val, 0, 0
                zone = "RED (Left)"
            elif wrist_x < 2 * w_screen / 3:
                r, g, b = 0, current_val, 0
                zone = "GREEN (Center)"
            else:
                r, g, b = 0, 0, current_val
                zone = "BLUE (Right)"
            
            send_udp_command(r, g, b)

            cv2.putText(img, f"Raw: {int(raw_brightness)}", (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 0, 255), 2)
            cv2.putText(img, f"OneEuro: {current_val}", (10, 60), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 255, 0), 2)
            cv2.putText(img, f"Zone: {zone}", (10, 90), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (255, 255, 0), 2)
        
        cv2.imshow("One-Euro Filter Control", img)
        if cv2.waitKey(1) and 0xFF == ord('q'): break
    cap.release()
    cv2.destroyAllWindows()
if __name__ == "__main__":
    main()