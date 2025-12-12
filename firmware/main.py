import socket
import time
import machine
import neopixel
import json

# Cấu hình cần thiết
UDP_PORT = 4210
NEO_PIN = 2
NUMPIXELS = 12
# Kiểm tra có cấu hình NeoPixel từ file boot.py chưa, nếu chưa thì tạo
try:
    np
except NameError:
    np = neopixel.NeoPixel(machine.Pin(NEO_PIN), NUMPIXELS)

# Tạo gói UDP
s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
s.bind(('0.0.0.0', UDP_PORT))
s.setblocking(False)

print(f"ESP32 DA KHOI DONG! IP: {UDP_PORT}")

# Biến thời gian
last_msg_time = time.time()
last_debug_print = time.time() # Biến để in debug

while True:
    # In ra màn hình mỗi 2 giây để biết chip còn sống 
    if time.time() - last_debug_print > 2:
        print("Dang doi tin hieu tu may tinh...")
        last_debug_print = time.time()
    # -----------------------------------------------------------------

    try:
        data, addr = s.recvfrom(1024)
        if data:
            txt = data.decode('utf-8')
            print(f"NHAN DUOC LENH: {txt}") # In ra lệnh nhận được
            
            try:
                color_info = json.loads(txt)
                r = color_info.get('r', 0)
                g = color_info.get('g', 0)
                b = color_info.get('b', 0)

                np.fill((r, g, b))
                np.write()
                last_msg_time = time.time()
                
            except ValueError:
                print("Loi JSON")

    except OSError:
        pass

    # Auto OFF sau 3s
    if time.time() - last_msg_time > 3:
        if np[0] != (0, 0, 0):
            np.fill((0, 0, 0))
            np.write()
            print("Mat tin hieu -> Tat den")
            last_msg_time = time.time() # Reset để đỡ spam

    time.sleep(0.01)