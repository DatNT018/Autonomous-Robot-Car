import cv2
from picamera2 import Picamera2
import time
import numpy as np
from main_motor import forward, stop, motor_init

# Khởi tạo Picamera2
picam2 = Picamera2()
picam2.configure(picam2.create_preview_configuration(main={"format": "RGB888", "size": (1280, 960)}))
picam2.start()

motor_init()
forward()

while True:

    img1 = picam2.capture_array()

    # Cắt ROI (khu vực quan tâm) từ frame
    img = img1[60:540, 400:800]  # ROI nhỏ hơn để tập trung hơn
    img = cv2.GaussianBlur(img, (5, 5), 0)

        # Chuyển đổi từ BGR sang HSV
    hsv = cv2.cvtColor(img, cv2.COLOR_RGB2HSV)

    # Khoang màu do thap voi dieu chinhr S và V
    red_lower = np.array([95, 255, 255], np.uint8)
    red_upper = np.array([130, 255, 255], np.uint8)

        # Định nghĩa khoảng màu xanh lá
    green_lower = np.array([35, 100,100], np.uint8)
    green_upper = np.array([86, 255, 255], np.uint8)

        # Tìm các vùng màu đỏ và xanh lá   
    red=cv2.inRange(hsv, red_lower, red_upper)
    green =cv2.inRange(hsv, green_lower, green_upper)

        # Biến đổi hình thái học để cải thiện kết quả
    kernal = np.ones((5, 5), "uint8")  # Kernel lớn hơn
    red = cv2.dilate(red, kernal)
    res=cv2.bitwise_and(img, img, mask = red)

    green = cv2.dilate(green, kernal)
    res2=cv2.bitwise_and(img, img, mask = green)

        # Tìm contour màu đỏ
    contours, _ = cv2.findContours(red, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
    for contour in contours:
        area = cv2.contourArea(contour)
        if area > 1000:  # Lọc bỏ các đối tượng nhỏ area > 1000:
            x, y, w, h = cv2.boundingRect(contour)
            img = cv2.rectangle(img, (x, y), (x + w, y + h), (0, 0, 255), 2)
            cv2.putText(img, "RED color", (x, y), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255))
            print("Red detected")
            stop()
            time.sleep(0.1)
            #continue

        # Tìm contour màu xanh lá
    contours, _ = cv2.findContours(green, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
    for contour in contours:
        area = cv2.contourArea(contour)
        if area > 1000:
            x, y, w, h = cv2.boundingRect(contour)
            img = cv2.rectangle(img, (x, y), (x + w, y + h), (0, 255, 0), 2)
            cv2.putText(img, "Green color", (x, y), cv2.FONT_HERSHEY_SIMPLEX, 1.0, (0, 255, 0))
            print("Green detected")
            forward()
            time.sleep(0.1)

        # Hiển thị hình ảnh (nếu cần)
    cv2.imshow("Color Tracking", img)

        # Nhấn 'q' để thoát
    if cv2.waitKey(1) & 0xFF == ord('q'):
            break


    # Dọn dẹp GPIO và dừng camera
GPIO.cleanup()
picam2.stop()
cv2.destroyAllWindows()
