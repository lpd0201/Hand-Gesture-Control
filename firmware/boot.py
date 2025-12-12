# boot.py chạy khi khởi động
import network
import machine
import time
import neopixel
import gc

# Cấu hình NeoPixel
NEO_PIN = 2
NUMPIXELS = 12
ssid = "lpd"
password = "020120077"

# Khởi tạo đèn
np = neopixel.NeoPixel(machine.Pin(NEO_PIN), NUMPIXELS)

def do_connect():
    wlan = network.WLAN(network.STA_IF) # Mode station : thu wifi, mode AP : phát wifi
    wlan.active(False)
    time.sleep(0.5)
    wlan.active(True)


    if not wlan.isconnected():
        print("Dang ket noi wifi...")
        wlan.connect(ssid, password)

        retry = 0
        while not wlan.isconnected():
            np.fill((50, 0, 0)) # Hiện màu đỏ
            np.write()
            time.sleep(0.2)
            np.fill((0, 0, 0))
            np.write()
            time.sleep(0.2)
            retry += 1
            if retry > 30: break # Nếu sau 15s không kết nối được thì break;
    if wlan.isconnected():
        print("Wifi connected: ", wlan.ifconfig()[0])
        np.fill((0, 50, 0))
        np.write()
        time.sleep(0.8)
        np.fill((0, 0, 0))
        np.write()
    else:
        print("Connected fail...")
        for _ in range(3):
            np.fill((50, 50, 0))
            np.write()
            time.sleep(0.3)
            np.fill((0, 0, 0))
            np.write()
            time.sleep(0.3)


do_connect()
