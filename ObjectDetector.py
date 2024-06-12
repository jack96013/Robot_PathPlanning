'''
Author: TZU-CHIEH, HSU
Mail: j.k96013@gmail.com
Department: ECIE Lab, NTUT
Date: 2024-06-06 09:11:18
LastEditTime: 2024-06-12 23:12:50
Description: 
'''
'''
Author: TZU-CHIEH, HSU
Mail: j.k96013@gmail.com
Department: ECIE Lab, NTUT
Date: 2024-06-04 09:03:40
LastEditTime: 2024-06-06 11:46:29
Description: 
'''

from PyQt5.QtCore import QThread, pyqtSignal, QMutex, QObject
from PyQt5.QtGui import QImage, QPixmap
import time
import numpy as np
import cv2
# import debugpy


color_default = {'red':  {'Lower': np.array([0, 60, 60]), 'Upper': np.array([6, 255, 255])},
              'blue': {'Lower': np.array([100, 80, 46]), 'Upper': np.array([124, 255, 255])},
              'green': {'Lower': np.array([35, 43, 35]), 'Upper': np.array([90, 255, 255])},
              'custom':None}


# color_default = {'red': {'Lower': np.array([0, 169, 33]), 'Upper': np.array([138, 255, 186])},
#               'blue': {'Lower': np.array([0, 151, 246]), 'Upper': np.array([36, 246, 255])},
#               'green': {'Lower': np.array([52, 84, 105]), 'Upper': np.array([90, 255, 174])},
#               'custom':None}


class ObjectDetector(QObject):
    frame_updated = pyqtSignal(np.ndarray)
    on_finish = pyqtSignal(dict)

    def __init__(self,cv_obj_dict):
        super().__init__()
        self.cap = None
        self.cv_obj_dict = cv_obj_dict
        self.shared_list = []
        self.mutex = QMutex()
        self.prev_time = time.time()
        

        self.cap = cv2.VideoCapture(2)
        self.cv_object_mutex = QMutex()
        self.processor = VideoProcessor(self.cap,cv_obj_dict,self.cv_object_mutex)
        self.processor.frame_updated.connect(self.frame_updated)
        self.processor.on_finish.connect(self.on_finish)


    def start(self):
        # AXIS P5512
        # http://root:root@192.168.10.163/mjpg/video.mjpg
        self.cap = cv2.VideoCapture(2)
        self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, 1920)
        self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 1080)

        self.processor.start()
        
    def stop(self):
        self.processor.stop()



class VideoProcessor(QThread):
    frame_updated = pyqtSignal(np.ndarray)
    on_finish = pyqtSignal(dict)

    def __init__(self,cap,cv_object_dict,cv_object_mutex):
        super().__init__()
        self.cap = cap
        self.prev_time = time.time()
        self.iter = 0
        self.iterList = []
        self.valueList = []

        # self.cv_object_mutex = QMutex()
        self.cv_object_dict = cv_object_dict
        self.cv_object_mutex = cv_object_mutex

        self.current_image = None

    def run(self):
        # debugpy.debug_this_thread()
        print("Thread Start")
        while True:
            ret, frame_bgr = self.cap.read()
            if not ret:
                return
            
            # frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

            gs_frame = cv2.GaussianBlur(frame_bgr, (5, 5), 0)                    # 高斯模糊
            hsv = cv2.cvtColor(gs_frame, cv2.COLOR_BGR2HSV)                  # 转化成HSV图像
            erode_hsv = cv2.erode(hsv, None, iterations=2)                   # 腐蚀 粗的变细

            
            # Find all contours object
            self.cv_object_mutex.lock()
            for key,cv_obj in self.cv_object_dict.items():
                self.detect_objects(frame_bgr, erode_hsv, cv_obj)
            self.cv_object_mutex.unlock()


            # Calculate FPS
            current_time = time.time()
            fps = 1 / (current_time - self.prev_time)
            self.prev_time = current_time

            # Display FPS on frame
            cv2.putText(frame_bgr, f'FPS: {fps:.2f}', (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
            # self.label_info_fps.setText(f'{fps:.2f}')

            

            self.iter = self.iter + 1
            self.iterList.append(int(self.iter))
            self.valueList.append(int(fps))   
            

            cv2.imshow('camera', frame_bgr)
            cv2.waitKey(1)

            # Update to Main Window
            imgage_rgb = cv2.cvtColor(frame_bgr, cv2.COLOR_BGR2RGB)
            self.frame_updated.emit(imgage_rgb)
            self.current_image = frame_bgr

            info = {}
            info["fps"]=fps
            self.on_finish.emit(info)

            time.sleep(0.01)

    def stop(self):
        self._run_flag = False
        self.wait()


    def detect_objects(self, frame_bgr, image_hsv, cv_object):
        if cv_object["Enable"] == False :
            return

        color_profile = cv_object["Color"]["Preset"]
        presetName = "red"
        if color_profile != "custom":
            presetName = color_profile
        

        lower_color = color_default[presetName]['Lower']
        upper_color = color_default[presetName]['Upper']

        inRange_hsv = cv2.inRange(image_hsv, lower_color, upper_color)
        cnts = cv2.findContours(inRange_hsv.copy(), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)[-2]
        
        large_cnts = [c for c in cnts if cv2.contourArea(c) > cv_object["AreaMin"]]

        # print(len(cnts))
        
        cv_object["Objects"].clear()
        # self.obstacles_list.clear()

        
        for c in large_cnts:
            #c = max(cnts, key=cv2.contourArea)
            rect = cv2.minAreaRect(c)
            box = cv2.boxPoints(rect)

            cv_object["Objects"].append(box)

            if (cv_object["ShowBoxEnable"]):
                cv2.drawContours(frame_bgr, [np.intp(box)], -1, (255, 255, 255), 2)

            # 顯示四個頂點的座標
            if (cv_object["ShowBoxPointEnable"]):
                for i, (x, y) in enumerate(box):
                    round_x = np.round(x,1)
                    round_y = np.round(y,1)
                    
                    cv2.putText(frame_bgr, f'({round_x:.1f}, {round_y:.1f})', (int(x), int(y)), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1, cv2.LINE_AA)
                    
            if (cv_object["ShowNameEnable"]):  
                angle = rect[2]
                #text = f'{cv_object["Name"]}-{angle:.1f}'
                text = f'{cv_object["Name"]}'
                
                # 置中顯示
                fontFace = cv2.FONT_HERSHEY_SIMPLEX
                fontScale = 0.5
                fontColor = (255, 255, 255)
                thickness = 2
                
                text_width, text_height = cv2.getTextSize(text, fontFace, fontScale, thickness)[0]
                CenterCoordinates = (int(rect[0][0]) - int(text_width / 2), int(rect[0][1]) + int(text_height / 2) + cv_object["TextOffsetH"])
                cv2.putText(frame_bgr, text , CenterCoordinates, fontFace, fontScale, fontColor, 1, cv2.LINE_AA)