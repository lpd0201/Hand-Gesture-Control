import cv2
import mediapipe as mp
import socket
import time
import math
import json
import numpy as np

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
        
        dx_hat = self.exponential_smoothing(a_d, dx, self.dx_prev) # Làm mượt vận tốc thô (dx), dùng cho việc tính tần số cắt

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

# Cấu hình IP và PORT của esp32-c3 
ESP_IP = "10.49.247.217"
ESP_PORT = 4210

# Tạo gói tin UDP
sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

# Gọi module hands từ thư viện solutions
mp_hands = mp.solutions.hands

hands = mp_hands.Hands(
    static_image_mode = False, # Đặt False -> chỉ kích hoạt chế độ theo dõi khi mất dấu tay
    max_num_hands = 1, 
    model_complexity = 1, # Độ phức tạp mô hình AI, mức 1 độ chính xác cao nhưng hơi chậm
    min_detection_confidence = 0.8, # Ngưỡng tin cậy khi phát hiện
    min_tracking_confidence = 0.8 # Ngưỡng tin cậy khi theo dõi chuyển động
)

# Tạo công cụ vẽ các chấm và các khớp
mp_draw = mp.solutions.drawing_utils

# Thêm các biến giúp UI luôn xuất hiện, tránh hiện tượng Flicker
display_raw = 0
display_filtered = 0
display_zone = "No hand"
last_hand_time = 0

last_send_time = 0

# Nếu min_cutoff quá thấp -> gây ra hiện tượng trễ (đèn sẽ tắt chậm)

brightness_filter = OneEuroFilter(min_cutoff = 0.01, beta = 0.4)

def send_udp_command(r, g, b):
    global last_send_time # Chuyển biến last_send_time thành biến toàn cục
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
    global last_hand_time, display_filtered, display_raw, display_zone

    cap = cv2.VideoCapture(0) # Bật webcam mặc định (VideoCapture(0))

    print("System started! Press 'q' to exit.")

    if not cap.isOpened():
        print("Can't open camera!")
        return
    
    while True:
        success, img = cap.read() # Chụp một khung hình, hệ thống sẽ tự động chụp khoảng 60 khung mỗi giây
        if not success: break # Nếu không có frame nào sẽ tiến hành thoát

        # Thêm bộ lọc gauss để tôi ưu xử lý nhiễu
        img = cv2.GaussianBlur(img, (5, 5), 0)
        # Lật ảnh để tránh hiện tượng gương 
        img = cv2.flip(img, 1)
        
        # OpenCV đọc ảnh với không gian màu mặc định sẽ là BGR, cần chuyển sang RGB
        img_rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        
        # Gửi ảnh đã chuyển đổi cho AI xử lý
        results = hands.process(img_rgb)

        lm_list = [] # Danh sách rỗng chứa tọa độ ngón tay
        # Tọa độ của các ngón tay trong MediaPipe Hands : 
        # 0, 4, 8, 12, 16, 20 tương ứng cổ tay, ngón cái, trỏ, giữa, áp út và ngón út

        # Các đối tượng trong multi_hand_landmarks sẽ trả về tọa độ được chuẩn hóa (0, 1), ta cần chuyển sang tọa độ pixel
        if results.multi_hand_landmarks:
            for hand_lms in results.multi_hand_landmarks:
                # Vẽ các khớp và đốt tay
                mp_draw.draw_landmarks(img, hand_lms, mp_hands.HAND_CONNECTIONS)
                # Duyệt qua tọa độ x, y và trả về xem đó là ngón nào
                for id, lm in enumerate(hand_lms.landmark):
                    h, w, c = img.shape # lấy kích thước thực tế của cửa sổ camera, w, h lần lượt là chiều rộng, chiều cao ảnh
                    # Chuyển tọa độ chuẩn hóa sang pixel 
                    cx, cy = int(lm.x * w), int(lm.y * h)
                    lm_list.append([id, cx, cy]) # Thêm vào list id ngón, tọa độ x và y (theo pixel)
        # 
        if len(lm_list) != 0:
            
            last_hand_time = time.time() # Cập nhật thời gian nhìn thấy tay
            
            # Lấy tọa độ x, y của ngón cái [4] và ngón trỏ [8] để tinh chỉnh độ sáng đèn theo công thức euclid
            x1, y1 = lm_list[4][1], lm_list[4][2]
            x2, y2 = lm_list[8][1], lm_list[8][2]

            # Vẽ đường nối giữa 2 ngón và 2 chấm tròn trên đầu ngón cái và trỏ
            cv2.circle(img, (x1, y1), 10, (100, 0, 255), cv2.FILLED)
            cv2.circle(img, (x2, y2), 10, (100, 0, 255), cv2.FILLED)
            cv2.line(img, (x1, y1), (x2, y2), (100, 0, 255), 3)

            # Tính độ sáng bằng cách di chuyển ngón cái và trỏ bằng khoảng cách Euclid
            # Trả về length tính theo pixel 
            length = math.hypot(x2 - x1, y2 - y1) 
            # Hàm nội suy
            raw_brightness = np.interp(length, [30, 200], [0, 255]) # Tính toán thô khoảng cách pixel giữa 2 ngón

            # Bộ lọc One-euro filter
            # Sau khi nội suy được khoảng cách, ta đưa nó vào bộ lọc để lọc tín hiệu
            filtered_brightness = brightness_filter.process(raw_brightness)
            current_val = int(filtered_brightness)

            # Logic vùng màu
            wrist_x = lm_list[0][1] # Lấy tọa độ x của cổ tay
            w_screen = img.shape[1] # Chiều rộng ảnh, 640x480 thì lấy 640

            r, g, b = 0, 0, 0

            # Cập nhật lại biến hiển thị
            display_raw = int(raw_brightness) # Hiển thị giá trị raw (giá trị thô)
            display_filtered = current_val # Hiển thị giá trị one-euro (giá trị sau lọc)

            if wrist_x < w_screen / 3:
                r, g, b = current_val, 0, 0
                display_zone = "RED (Left)"
            elif wrist_x < 2 * w_screen / 3:
                r, g, b = 0, current_val, 0
                display_zone = "GREEN (Center)"
            else:
                r, g, b = 0, 0, current_val
                display_zone = "BLUE (Right)"
            
            send_udp_command(r, g, b)
            # Nếu đặt các dòng cv2.putText ở trong câu lệnh if trên thì sẽ gây ra hiện tượng chớp khi cổ tay chuyển sang zone khác
        
        # Kiểm tra nếu quá 2s thì đặt các biến về trạng thái đầu
        if time.time() - last_hand_time > 2.0:
            display_zone = "No hand....."
            display_raw = 0
            display_filtered = 0
        
        # Đặt các dòng cv2.putText ở đây để đảm bảo luôn hiển thị các dòng raw, one-euro và zone màu
        cv2.putText(img, f"Raw: {display_raw}", (10, 30), 1, 1.5, (0, 0, 255), 2)
        cv2.putText(img, f"OneEuro: {display_filtered}", (10, 60), 1, 1.5, (0, 255, 0), 2)
        cv2.putText(img, f"Zone: {display_zone}", (10, 90), 1, 1.5, (255, 255, 0), 2)
        
        cv2.imshow("Hand Gesture (Update no Flicker)!", img)
        if cv2.waitKey(1) & 0xFF == ord('q'): break
    cap.release()
    cv2.destroyAllWindows()
if __name__ == "__main__":
    main()
