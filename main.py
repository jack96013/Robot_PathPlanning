'''
Author: TZU-CHIEH, HSU
Mail: j.k96013@gmail.com
Department: ECIE Lab, NTUT
Date: 2024-05-30 22:20:00
LastEditTime: 2024-06-12 23:21:27
Description: 
'''

import cv2
import matplotlib
import matplotlib.pyplot as plt
import numpy as np
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg
from matplotlib.backends.backend_qt5agg import \
    NavigationToolbar2QT as NavigationToolbar
from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtCore import QMutex, QThread, pyqtSignal, pyqtSlot, Qt
from PyQt5.QtGui import QPainter, QLinearGradient, QBrush, QColor
from PyQt5.QtWidgets import QLabel


from ui import main_ui

matplotlib.use("Qt5Agg")  # 使用 Qt5
import math
import time

import mplcursors
from map import Map
from matplotlib.backends.backend_qt5agg import \
    FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
from ObjectDetector import ObjectDetector, color_default

# from TCPClientHandler import TCPClientHandler
from AmigoBot import AmigoBot


color_filter_struct = {'Lower': np.array([0, 0, 0]), 'Upper': np.array([0, 0, 0])}

color_profile = {
    "Preset":0,
    "Custom":color_filter_struct,
}

cv_obj_dict = {
    "obstacles":{
        "Name":"Obstacles",
        "Color": color_profile.copy(),
        "AreaMin":1000,
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
        "Enable": False,
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

class GradientLabel(QLabel):
    def __init__(self, low_color, high_color, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.low_color = QColor(low_color)
        self.high_color = QColor(high_color)
        
    def paintEvent(self, event):
        painter = QPainter(self)
        rect = self.rect()
        gradient = QLinearGradient(0, 0, rect.width(), 0)
        gradient.setColorAt(0, self.low_color)
        gradient.setColorAt(1, self.high_color)
        brush = QBrush(gradient)
        painter.fillRect(rect, brush)
        painter.drawText(rect, Qt.AlignCenter, self.text())
    
    def setGradientColors(self, low_color, high_color):
        self.low_color = QColor(low_color[0],low_color[1],low_color[2])
        self.high_color = QColor(high_color[0],high_color[1],high_color[2])
        self.update()  # 请求重绘

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

        self.keep_update_map_enable = True
        
        self.start_button.clicked.connect(self.on_button_start_click)
        self.pushButton_simulate.clicked.connect(self.on_button_simulate_click)
        self.pushButton_generate.clicked.connect(self.on_button_generate_click)
        self.checkBox_update_map_enable.clicked.connect(self.on_checkBox_update_map_clock)
        self.checkBox_update_map_enable.setChecked(self.keep_update_map_enable)

        self.timer = QtCore.QTimer()
        self.timer.timeout.connect(self.ga_runner)
        self.timer.setSingleShot(True)

        self.plt1_timer = QtCore.QTimer()
        self.plt1_timer.timeout.connect(self.plt1_timer_update)
        self.plt1_timer.start(200)

        self.tabWidget.setCurrentIndex(0)

        self.cap = None

        # self.obstacles_list = list()


        cv_obj_dict["start"]["Color"]["Preset"] = "custom"
        cv_obj_dict["end"]["Color"]["Preset"] = "blue"
        cv_obj_dict["obstacles"]["Color"]["Preset"] = "green"
        cv_obj_dict["robot"]["Color"]["Preset"] = "red"


        self.drawPlot()
        self.color_filiter_ui_init()
        
        self.color_adjust_init()
        self.color_filter_combobox_obj_init()

        self.obj_detection_checkbox_init()


        self.comboBox_obj_select.setCurrentIndex(1)
        self.comboBox_obj_select.setCurrentIndex(0)

        self.prev_time = time.time()

        self.sc = None

        self.drawMap()
        self.map = Map(cv_obj_dict,self.sc)

        self.iterList = []
        self.valueList = []
        self.iter = 0


        # Video Processing
        # self.cap = cv2.VideoCapture(2)
        self.cv_object_mutex = QMutex()

        self.object_detector = ObjectDetector(cv_obj_dict)
        self.object_detector.frame_updated.connect(self.update_image)
        self.object_detector.on_finish.connect(self.on_finish)

        self.current_image = None

        self.tab_robot_init()
        
        self.amigoBot = AmigoBot()

        
    def tab_robot_init(self):
        self.pushButton_robot_connect.clicked.connect(self.on_button_robot_connect_click)
        self.pushButton_robot_forward.clicked.connect(self.on_button_robot_forward_click)
        self.pushButton_robot_backward.clicked.connect(self.on_button_robot_backward_click)
        self.pushButton_robot_left.clicked.connect(self.on_button_robot_left_click)
        self.pushButton_robot_right.clicked.connect(self.on_button_robot_right_click)
        self.pushButton_robot_stop.clicked.connect(self.on_button_robot_stop_click)
    
    def on_button_robot_connect_click(self):
        self.amigoBot.connectToRelay()
    
    def on_button_robot_forward_click(self):
        self.amigoBot.move_forward()
    
    def on_button_robot_backward_click(self):
        self.amigoBot.move_backward()
        
    def on_button_robot_left_click(self):
        self.amigoBot.turn_left()
        
    def on_button_robot_right_click(self):
        self.amigoBot.turn_right()
        
    def on_button_robot_stop_click(self):
        self.amigoBot.stop()    

    def on_checkBox_update_map_clock(self):
        self.keep_update_map_enable = self.sender().isChecked()
        
    def on_button_simulate_click(self):
        self.timer.start()
        pass

    def on_button_generate_click(self):
        self.map.update()
    
    
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
        self.label_color_previewNew = GradientLabel("#FF0000", "#0000FF")
        
        self.horizontalLayout_color_preview.addWidget(self.label_color_previewNew)


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
        
        color = None
        if (presetName == "custom"):
            cv_object["Color"]["Custom"][color_type][color_idx] = value
            color = cv_object["Color"]["Custom"]
        else:
            color_default[presetName][color_type][color_idx] = value
            color = color_default[presetName]
            
        rgb_lower = cv2.cvtColor(np.uint8([[color["Lower"]]]), cv2.COLOR_HSV2RGB)
        rgb_lower = rgb_lower[0][0]
        rgb_upper = cv2.cvtColor(np.uint8([[color["Upper"]]]), cv2.COLOR_HSV2RGB)
        rgb_upper = rgb_upper[0][0]
        # self.label_color_preview.setStyleSheet(f"background-color: rgb({rgb[0]},{rgb[1]},{rgb[2]})")
        self.label_color_previewNew.setGradientColors(rgb_lower, rgb_upper)


    def color_spin_box_changed(self):
        name = self.sender().objectName().split("_")[1]
        slider_box = self.findChild(QtWidgets.QSlider, f"horizontalSlider_{name}")
        if slider_box is not None:
            slider_box.setValue(self.sender().value())

    def on_button_start_click(self):
        self.object_detector.start()

    @pyqtSlot(np.ndarray)
    def update_image(self, frame):
        self.current_image = frame

        image = QtGui.QImage(frame, frame.shape[1], frame.shape[0], 
                            frame.strides[0], QtGui.QImage.Format_RGB888)
        pixmap = QtGui.QPixmap.fromImage(image)
        self.label.setPixmap(pixmap.scaled(
            self.label.size(), QtCore.Qt.KeepAspectRatio))


        pass
        

    @pyqtSlot(dict)
    def on_finish(self,info):
        self.cv_object_mutex.lock()
        

        self.label_info_obstacles_6.setText(f'{self.map.robot.getAngles():.1f}')
        
        self.label_info_obstacles.setText(f'{len(cv_obj_dict["obstacles"]["Objects"])}')
        self.label_info_robot_angles.setText(f'{len(cv_obj_dict["robot"]["Objects"])}')
        self.label_info_obstacles_4.setText(f'{len(cv_obj_dict["start"]["Objects"])}')
        self.label_info_obstacles_5.setText(f'{len(cv_obj_dict["end"]["Objects"])}')
        
        
        self.cv_object_mutex.unlock()
        self.label_info_fps.setText(f'{info["fps"]:.2f}')
        
        if self.keep_update_map_enable:
            # self.map.update()
            self.map.plot_map()
        
        pass

 
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
        
        self.sc.axes.set_xlim([0,1920])
        self.sc.axes.set_ylim([0,1080])
        self.sc.axes.invert_yaxis()
        
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
    
    def ga_runner(self):
        self.map.start_planning_thread()
        pass
            
    def plt1_timer_update(self):
        
        # self.object_detector.cv_object_mutex.lock()

        # obstacles = cv_obj_dict["obstacles"]["Objects"]

        # self.object_detector.cv_object_mutex.unlock()

        

        # obstacles_loc_list = []
        # for obstacle in obstacles:
        #     rect = cv2.minAreaRect(obstacle)
        #     box = cv2.boxPoints(rect)
            
        #     obstacles_loc_list.append(np.intp(box))

        
        # self.sc.axes.cla()
        # self.sc.axes.invert_yaxis()
        # self.sc.axes.xaxis.set_ticks_position('top')
        # # if self.object_detector.processor.current_image is not None:
        #     # self.sc.axes.imshow(self.current_image)
        # self._plot_obstacles(obstacles)
        
        
        # #self.sc.axes.plot(self.iterList, self.valueList)
        # self.sc.draw()
        
        pass


if __name__ == '__main__':
    import sys
    app = QtWidgets.QApplication(sys.argv)
    window = Main()
    window.show()
    sys.exit(app.exec_())