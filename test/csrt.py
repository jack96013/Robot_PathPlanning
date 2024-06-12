'''
Author: TZU-CHIEH, HSU
Mail: j.k96013@gmail.com
Department: ECIE Lab, NTUT
Date: 2024-06-06 20:18:50
LastEditTime: 2024-06-06 20:20:52
Description: 
'''
import cv2
import numpy as np

# 定義顏色範圍（以藍色為例）
lower_blue = np.array([100, 150, 0])
upper_blue = np.array([140, 255, 255])

# 初始化視頻捕捉
cap = cv2.VideoCapture(2)

# 初始化追蹤器
tracker = cv2.legacy.TrackerCSRT_create()
initialized = False

while True:
    ret, frame = cap.read()
    if not ret:
        break

    # 將圖像從 BGR 轉換為 HSV
    hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)

    # 創建遮罩
    mask = cv2.inRange(hsv, lower_blue, upper_blue)

    # 找到輪廓
    contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    
    if contours:
        # 找到最大的輪廓
        c = max(contours, key=cv2.contourArea)
        x, y, w, h = cv2.boundingRect(c)
        
        if not initialized:
            # 初始化追蹤器
            tracker.init(frame, (x, y, w, h))
            initialized = True

    if initialized:
        # 更新追蹤器
        ret, bbox = tracker.update(frame)
        if ret:
            (x, y, w, h) = [int(v) for v in bbox]
            # 畫出追蹤框
            cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 0), 2, 1)
        else:
            cv2.putText(frame, "Tracking failure", (100, 80), cv2.FONT_HERSHEY_SIMPLEX, 0.75, (0, 0, 255), 2)

    # 顯示結果
    cv2.imshow("Tracking", frame)
    
    # 按 'q' 鍵退出
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

# 釋放視頻捕捉對象
cap.release()
cv2.destroyAllWindows()