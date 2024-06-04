'''
Author: TZU-CHIEH, HSU
Mail: j.k96013@gmail.com
Department: ECIE Lab, NTUT
Date: 2024-05-30 22:20:00
LastEditTime: 2024-06-04 09:10:58
Description: 
'''

from PyQt5 import QtWidgets, QtCore, QtGui
from PyQt5.QtCore import QThread, pyqtSignal, pyqtSlot, QMutex
from PyQt5.QtGui import QImage

from ui import main_ui
import numpy as np

import cv2

import matplotlib.pyplot as plt
import matplotlib
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg, NavigationToolbar2QT as NavigationToolbar

matplotlib.use("Qt5Agg")  # 使用 Qt5
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure

import mplcursors

import math
import time

from robot import Robot
from map import Map
from ObjectDetector import ObjectDetector


color_filter_struct = {'Lower': np.array([0, 0, 0]), 'Upper': np.array([0, 0, 0])}

color_profile = {
    "Preset":0,
    "Custom":color_filter_struct,
}

cv_obj_dict = {
    "obstacles":{
        "Name":"Obstacles",
        "Color": color_profile.copy(),
        "AreaMin":500,
        "TextOffsetH": 10,
        "Objects": [],
        "Enable": True,
        "ShowBoxPointEnable":False,
        "ShowBoxEnable":True,
        "ShowNameEnable":True
    },
    "robot":{
        "Name":"Robot",
        "Color": color_profile.copy(),
        "AreaMin":500,
        "TextOffsetH": -10,
        "Objects": [],
        "Enable": True,
        "ShowBoxPointEnable":False,
        "ShowBoxEnable":True,
        "ShowNameEnable":True
    },
    "start":{
        "Name":"Start Point",
        "Color": color_profile.copy(),
        "AreaMin":500,
        "TextOffsetH": 0,
        "Objects": [],
        "Enable": True,
        "ShowBoxPointEnable":False,
        "ShowBoxEnable":True,
        "ShowNameEnable":True
    },
    "end":{
        "Name":"End Point",
        "Color": color_profile.copy(),
        "AreaMin":500,
        "TextOffsetH": 20,
        "Objects": [],
        "Enable": True,
        "ShowBoxPointEnable":False,
        "ShowBoxEnable":True,
        "ShowNameEnable":True
    },
}

plt.ion()


class MplCanvas(FigureCanvasQTAgg):

    def __init__(self, parent=None, width=5, height=4, dpi=100):
        fig = Figure(figsize=(width, height), dpi=dpi)
        self.axes = fig.add_subplot(111)
        
        super(MplCanvas, self).__init__(fig)


class Main(QtWidgets.QMainWindow, main_ui.Ui_MainWindow):
    def __init__(self):
        super().__init__()
        self.setupUi(self)

        self.setWindowTitle("ARAA Final Project ")
        self.setGeometry(100, 100, 800, 600)
        
        self.start_button.clicked.connect(self.start_webcam)
        
        # self.timer = QtCore.QTimer()
        # self.timer.timeout.connect(self.update_frame)

        self.plt1_timer = QtCore.QTimer()
        self.plt1_timer.timeout.connect(self.plt1_timer_update)
        # self.plt1_timer.start(1000)

        self.cap = None

        # self.obstacles_list = list()


        cv_obj_dict["start"]["Color"]["Preset"] = "custom"
        cv_obj_dict["end"]["Color"]["Preset"] = "red"
        cv_obj_dict["obstacles"]["Color"]["Preset"] = "green"
        cv_obj_dict["robot"]["Color"]["Preset"] = "blue"


        self.drawPlot()
        self.color_filiter_ui_init()
        
        self.color_adjust_init()
        self.color_filter_combobox_obj_init()

        self.obj_detection_checkbox_init()


        self.robot = Robot()
        self.object_detector = ObjectDetector()
        self.map = Map()

        self.comboBox_obj_select.setCurrentIndex(1)
        self.comboBox_obj_select.setCurrentIndex(0)

        self.prev_time = time.time()

        self.sc = None

        self.drawMap()

        self.iterList = []
        self.valueList = []
        self.iter = 0


        # Video Processing
        self.cap = cv2.VideoCapture(2)
        self.cv_object_mutex = QMutex()
        self.video_processor = VideoProcessor(self.cap,cv_obj_dict,self.cv_object_mutex)
        self.video_processor.frame_updated.connect(self.update_image)
        self.video_processor.on_finish.connect(self.on_finish)

    
    def obj_detection_checkbox_init(self):
        self.checkBox_obj_enable.clicked.connect(self.on_obj_detection_checkbox_click)
        self.checkBox_obj_show_box.clicked.connect(self.on_obj_detection_checkbox_click)
        self.checkBox_obj_show_box_point.clicked.connect(self.on_obj_detection_checkbox_click)
        self.checkBox_obj_show_text.clicked.connect(self.on_obj_detection_checkbox_click)

    def on_obj_detection_checkbox_click(self):
        cv_object = self.getCurrentSelectObject()
        is_enable = self.sender().isChecked()

        if (self.sender().objectName() == "checkBox_obj_enable"):
            cv_object["Enable"] = is_enable
        elif (self.sender().objectName() == "checkBox_obj_show_box"):
            cv_object["ShowBoxEnable"] = is_enable
        elif (self.sender().objectName() == "checkBox_obj_show_box_point"):
            cv_object["ShowBoxPointEnable"] = is_enable
        elif (self.sender().objectName() == "checkBox_obj_show_text"):
            cv_object["ShowNameEnable"] = is_enable
        

    def color_adjust_init(self):
        self.comboBox_color_choose.addItems(list(color_default.keys()))
        self.comboBox_color_choose.currentIndexChanged.connect(self.on_color_adjust)
        

    def on_color_adjust(self):
        #color_profile_name = str(self.sender().currentText())
        color_profile_name = str(self.sender().currentText())
        
        self.getCurrentSelectObject()["Color"]["Preset"] = color_profile_name

        if color_profile_name not in color_default.keys():
            return
        
        if color_profile_name == "custom":
            # self.verticalLayout_color_adjust.setEnabled(True)
            cv_object = self.getCurrentSelectObject()
            
            self.horizontalSlider_rmin.setValue(cv_object["Color"]["Custom"]["Lower"][0])
            self.horizontalSlider_gmin.setValue(cv_object["Color"]["Custom"]["Lower"][1])
            self.horizontalSlider_bmin.setValue(cv_object["Color"]["Custom"]["Lower"][2])

            self.horizontalSlider_rmax.setValue(cv_object["Color"]["Custom"]["Upper"][0])
            self.horizontalSlider_gmax.setValue(cv_object["Color"]["Custom"]["Upper"][1])
            self.horizontalSlider_bmax.setValue(cv_object["Color"]["Custom"]["Upper"][2])
            
        else:
            # self.verticalLayout_color_adjust.setEnabled(False)  
            self.horizontalSlider_rmin.setValue(color_default[color_profile_name]['Lower'][0])
            self.horizontalSlider_gmin.setValue(color_default[color_profile_name]['Lower'][1])
            self.horizontalSlider_bmin.setValue(color_default[color_profile_name]['Lower'][2])

            self.horizontalSlider_rmax.setValue(color_default[color_profile_name]['Upper'][0])
            self.horizontalSlider_gmax.setValue(color_default[color_profile_name]['Upper'][1])
            self.horizontalSlider_bmax.setValue(color_default[color_profile_name]['Upper'][2])

        

    def color_filter_combobox_obj_init(self):
        for key,value in cv_obj_dict.items():
            self.comboBox_obj_select.addItem(value["Name"])
        
        self.comboBox_obj_select.currentIndexChanged.connect(self.on_combobox_obj_changed)
        
    
    def on_combobox_obj_changed(self):
        index = self.sender().currentIndex()
        obj_key = list(cv_obj_dict.keys())[index]
        
        # key = list(color_default.keys())[index]

        if obj_key is None:
            return
        
        # Color Adjust Combobox
        cv_object = self.getCurrentSelectObject()
        preset_name = cv_object["Color"]["Preset"]
        preset_index = list(color_default.keys()).index(preset_name)
        self.comboBox_color_choose.setCurrentIndex(preset_index)
        
        # CheckBox
        self.checkBox_obj_enable.setChecked(cv_object["Enable"])
        self.checkBox_obj_show_box_point.setChecked(cv_object["ShowBoxPointEnable"])
        self.checkBox_obj_show_box.setChecked(cv_object["ShowBoxEnable"])
        self.checkBox_obj_show_text.setChecked(cv_object["ShowNameEnable"])

        
        
    def getCurrentSelectObject(self):
        index = self.comboBox_obj_select.currentIndex()
        key = list(cv_obj_dict.keys())[index]
        return cv_obj_dict[key] 
       

    def color_filiter_ui_init(self):
        self.horizontalSlider_rmin.valueChanged.connect(self.color_slider_changed)
        self.horizontalSlider_gmin.valueChanged.connect(self.color_slider_changed)
        self.horizontalSlider_bmin.valueChanged.connect(self.color_slider_changed)

        self.horizontalSlider_rmax.valueChanged.connect(self.color_slider_changed)
        self.horizontalSlider_gmax.valueChanged.connect(self.color_slider_changed)
        self.horizontalSlider_bmax.valueChanged.connect(self.color_slider_changed)

        self.spinBox_rmin.valueChanged.connect(self.color_spin_box_changed)
        self.spinBox_gmin.valueChanged.connect(self.color_spin_box_changed)
        self.spinBox_bmin.valueChanged.connect(self.color_spin_box_changed)

        self.spinBox_rmax.valueChanged.connect(self.color_spin_box_changed)
        self.spinBox_gmax.valueChanged.connect(self.color_spin_box_changed)
        self.spinBox_bmax.valueChanged.connect(self.color_spin_box_changed)
        
    def color_slider_changed(self):
        name = self.sender().objectName().split("_")[1]
        spin_box = self.findChild(QtWidgets.QSpinBox, f"spinBox_{name}")
        value = self.sender().value()

        if spin_box is not None:
            spin_box.setValue(value)
        
        cv_object = self.getCurrentSelectObject()
        presetName = cv_object["Color"]["Preset"]

        color_idx = 0
        color_type = None
        if (name[1:] == "min"):
            color_type = "Lower"
        else:
            color_type = "Upper"

        if (name[0] == "r"):
            color_idx = 0
        elif (name[0] == "g"):
            color_idx = 1
        elif (name[0] == "b"):
            color_idx = 2


        if (presetName == "custom"):
            cv_object["Color"]["Custom"][color_type][color_idx] = value
        
        else:
            color_default[presetName][color_type][color_idx] = value


    def color_spin_box_changed(self):
        name = self.sender().objectName().split("_")[1]
        slider_box = self.findChild(QtWidgets.QSlider, f"horizontalSlider_{name}")
        if slider_box is not None:
            slider_box.setValue(self.sender().value())

    def start_webcam(self):
        self.cap = cv2.VideoCapture(2)
        self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, 1920)
        self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 1080)
        
        self.video_processor.start()
        # self.timer.start(20)

    @pyqtSlot(np.ndarray)
    def update_image(self, frame):
        image = QtGui.QImage(frame, frame.shape[1], frame.shape[0], 
                            frame.strides[0], QtGui.QImage.Format_RGB888)
        pixmap = QtGui.QPixmap.fromImage(image)
        self.label.setPixmap(pixmap.scaled(
            self.label.size(), QtCore.Qt.KeepAspectRatio))


        pass
        

    @pyqtSlot(dict)
    def on_finish(self,info):
        self.cv_object_mutex.lock()
        self.label_info_obstacles.setText(f'{len(cv_obj_dict["obstacles"]["Objects"])}')
        self.label_info_robot_angles.setText(f'{len(cv_obj_dict["robot"]["Objects"])}')
        self.label_info_obstacles_4.setText(f'{len(cv_obj_dict["start"]["Objects"])}')
        self.label_info_obstacles_5.setText(f'{len(cv_obj_dict["end"]["Objects"])}')
        self.cv_object_mutex.unlock()
        self.label_info_fps.setText(f'{info["fps"]:.2f}')
        pass

    # def update_frame(self):
    #     pass
        # ret, frame = self.cap.read()
        # if not ret:
        #     return
        
        # frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

        # gs_frame = cv2.GaussianBlur(frame, (5, 5), 0)                    # 高斯模糊
        # hsv = cv2.cvtColor(gs_frame, cv2.COLOR_BGR2HSV)                  # 转化成HSV图像
        # erode_hsv = cv2.erode(hsv, None, iterations=2)                   # 腐蚀 粗的变细

        
        # # Find all contours object
        # for key,cv_obj in cv_obj_dict.items():
        #     self.detect_objects(frame, erode_hsv, cv_obj)


        # # Update Infomation
        # self.label_info_obstacles.setText(f'{len(cv_obj_dict["obstacles"]["Objects"])}')
        # self.label_info_robot_angles.setText(f'{len(cv_obj_dict["robot"]["Objects"])}')
        # self.label_info_obstacles_4.setText(f'{len(cv_obj_dict["start"]["Objects"])}')
        # self.label_info_obstacles_5.setText(f'{len(cv_obj_dict["end"]["Objects"])}')

        # loc = self.robot.setLocation(cv_obj_dict["robot"]["Objects"])
        # if (loc != None):
            
        #     cv2.arrowedLine(frame, (int(loc["rear"][0]),int(loc["rear"][1])),  (int(loc["front"][0]),int(loc["front"][1])), (0, 0, 255), 2) 
        #     self.label_info_obstacles_6.setText(f'{self.robot.getAngles():.1f}')
        
        # # Calculate FPS
        # current_time = time.time()
        # fps = 1 / (current_time - self.prev_time)
        # self.prev_time = current_time

        # # Display FPS on frame
        # cv2.putText(frame, f'FPS: {fps:.2f}', (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
        # self.label_info_fps.setText(f'{fps:.2f}')

        # imgage_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

       
        # self.iter = self.iter + 1
        # self.iterList.append(int(self.iter))
        # self.valueList.append(int(fps))   
        

        # cv2.imshow('camera', imgage_rgb)
        # cv2.waitKey(1)

        # image = QtGui.QImage(frame, frame.shape[1], frame.shape[0], 
        #                         frame.strides[0], QtGui.QImage.Format_RGB888)

        # self.updateImage(image)

        # print(f"FPS={fps}")




    # def detect_objects(self, frame, image, cv_object):
    #     if cv_object["Enable"] == False :
    #         return

    #     color_profile = cv_object["Color"]["Preset"]
    #     presetName = "red"
    #     if color_profile != "custom":
    #         presetName = color_profile
        

    #     lower_color = color_default[presetName]['Lower']
    #     upper_color = color_default[presetName]['Upper']

    #     inRange_hsv = cv2.inRange(image, lower_color, upper_color)
    #     cnts = cv2.findContours(inRange_hsv.copy(), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)[-2]
        
    #     large_cnts = [c for c in cnts if cv2.contourArea(c) > cv_object["AreaMin"]]

    #     # print(len(cnts))
        
    #     cv_object["Objects"].clear()
    #     # self.obstacles_list.clear()

        
    #     for c in large_cnts:
    #         cv_object["Objects"].append(c)

    #         #c = max(cnts, key=cv2.contourArea)
    #         rect = cv2.minAreaRect(c)
    #         box = cv2.boxPoints(rect)

    #         if (cv_object["ShowBoxEnable"]):
    #             cv2.drawContours(frame, [np.intp(box)], -1, (0, 0, 255), 2)

    #         # 顯示四個頂點的座標
    #         if (cv_object["ShowBoxPointEnable"]):
    #             for i, (x, y) in enumerate(box):
    #                 round_x = np.round(x,1)
    #                 round_y = np.round(y,1)
                    
    #                 cv2.putText(frame, f'({round_x:.1f}, {round_y:.1f})', (int(x), int(y)), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 255), 1, cv2.LINE_AA)
                    
    #         if (cv_object["ShowNameEnable"]):  
    #             angle = rect[2]
    #             #text = f'{cv_object["Name"]}-{angle:.1f}'
    #             text = f'{cv_object["Name"]}'
                
    #             # 置中顯示
    #             fontFace = cv2.FONT_HERSHEY_SIMPLEX
    #             fontScale = 0.5
    #             fontColor = (0, 0, 255)
    #             thickness = 2
                
    #             text_width, text_height = cv2.getTextSize(text, fontFace, fontScale, thickness)[0]
    #             CenterCoordinates = (int(rect[0][0]) - int(text_width / 2), int(rect[0][1]) + int(text_height / 2) + cv_object["TextOffsetH"])
    #             cv2.putText(frame, text , CenterCoordinates, fontFace, fontScale, fontColor, 1, cv2.LINE_AA)
    
    def updateImage(self,image):
        self.label.setPixmap(QtGui.QPixmap.fromImage(image))
        pixmap = QtGui.QPixmap.fromImage(image)
        self.label.setPixmap(pixmap.scaled(
            self.label.size(), QtCore.Qt.KeepAspectRatio))


    def closeEvent(self, event):
        self.timer.stop()
        if self.cap is not None:
            self.cap.release()
        event.accept()


    def drawPlot(self,i=0):
        # sc = MplCanvas(self, width=5, height=4, dpi=100)
        # aa = sc.axes.plot([0,1,2,3,4], [10,1,20,3,40])
        
        # c1 = mplcursors.cursor(aa, hover=True)

        # @c1.connect("add")
        # def _(sel):
        #     sel.annotation.get_bbox_patch().set(fc="white")
        #     sel.annotation.arrow_patch.set( fc="white", alpha=.5)
    

        # # Create toolbar, passing canvas as first parament, parent (self, the MainWindow) as second.
        # toolbar = NavigationToolbar(sc, self)

        # layout = QtWidgets.QVBoxLayout()
        # layout.addWidget(toolbar)
        # layout.addWidget(sc)

        # # Create a placeholder widget to hold our toolbar and canvas.
        # widget = QtWidgets.QWidget()
        # widget.setLayout(layout)

        # self.verticalLayout_main_2.addWidget(widget)

        # self.show()
        pass


    def drawMap(self):
        self.sc = MplCanvas(self, width=5, height=4, dpi=100)
        aa = self.sc.axes.plot([0,1,2,3,4], [10,1,20,3,40])
        
        c1 = mplcursors.cursor(aa, hover=True)

        @c1.connect("add")
        def _(sel):
            sel.annotation.get_bbox_patch().set(fc="white")
            sel.annotation.arrow_patch.set( fc="white", alpha=.5)
    

        # Create toolbar, passing canvas as first parament, parent (self, the MainWindow) as second.
        toolbar = NavigationToolbar(self.sc, self)

        layout = QtWidgets.QVBoxLayout()
        layout.addWidget(toolbar)
        layout.addWidget(self.sc)

        # Create a placeholder widget to hold our toolbar and canvas.
        widget = QtWidgets.QWidget()
        widget.setLayout(layout)

        self.verticalLayout_main_3.addWidget(widget)

        self.show()
    
        pass

    def _plot_obstacles(self,obstacles):
    
        for obstacle in obstacles:
            x_values, y_values = [], []

            for vertex in obstacle:
                x_values.append(vertex[0][0])
                y_values.append(vertex[0][1])
            
            self.sc.axes.fill(x_values, y_values, 'r')
            
    def plt1_timer_update(self):
        
        obstacles = cv_obj_dict["obstacles"]["Objects"]
        obstacles_loc_list = []
        for obstacle in obstacles:
            rect = cv2.minAreaRect(obstacle)
            box = cv2.boxPoints(rect)
            
            obstacles_loc_list.append(np.intp(box))

        
        self.sc.axes.cla()
        self._plot_obstacles(obstacles)
        
        
        #self.sc.axes.plot(self.iterList, self.valueList)
        self.sc.draw()
        
        print("update")



if __name__ == '__main__':
    import sys
    app = QtWidgets.QApplication(sys.argv)
    window = Main()
    window.show()
    sys.exit(app.exec_())