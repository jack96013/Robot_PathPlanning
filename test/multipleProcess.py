'''
Author: TZU-CHIEH, HSU
Mail: j.k96013@gmail.com
Department: ECIE Lab, NTUT
Date: 2024-06-05 10:55:55
LastEditTime: 2024-06-05 11:15:42
Description: 
'''
import sys
from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout, QPushButton, QLabel, QProgressBar, QMessageBox
from PyQt5.QtCore import pyqtSignal, QObject, QThread, QTimer
from multiprocessing import Process, Queue

def path_planning_task(queue):
    import time
    for i in range(100):
        time.sleep(0.1)  # 模擬耗時計算
        queue.put((i + 1) * 1)  # 每次增加20%進度
    queue.put("路徑規劃完成")

class PathPlanningWorker(QObject):
    update_signal = pyqtSignal(str)
    progress_signal = pyqtSignal(int)
    check_alive_signal = pyqtSignal(bool)

    def __init__(self):
        super().__init__()
        self.queue = Queue()
        self.process = None
        self.timer = None

    def start(self):
        self.process = Process(target=path_planning_task, args=(self.queue,))
        self.process.start()
        self.thread = QThread()
        self.moveToThread(self.thread)
        self.thread.started.connect(self.check_queue)
        self.thread.start()

        self.timer = QTimer()
        self.timer.timeout.connect(self.check_process_alive)
        self.timer.start(100)

    def check_queue(self):
        if not self.queue.empty():
            result = self.queue.get()
            if isinstance(result, str):
                self.update_signal.emit(result)
                self.cleanup()
            else:
                self.progress_signal.emit(result)
                QThread.msleep(100)
                self.check_queue()
        else:
            QThread.msleep(100)
            self.check_queue()

    def check_process_alive(self):
        print("alive")
        if self.process and not self.process.is_alive():
            self.check_alive_signal.emit(False)
            self.cleanup()

    def cleanup(self):
        if self.timer:
            self.timer.stop()
            self.timer = None
        if self.process:
            self.process.terminate()
            self.process.join()
            self.process = None
        if self.thread:
            self.thread.quit()
            self.thread.wait()
            self.thread = None

class MyApp(QWidget):
    def __init__(self):
        super().__init__()
        self.initUI()

    def initUI(self):
        self.layout = QVBoxLayout()
        self.label = QLabel("點擊按鈕開始路徑規劃")
        self.progress_bar = QProgressBar()
        self.button = QPushButton("開始")
        self.button.clicked.connect(self.start_path_planning)

        self.layout.addWidget(self.label)
        self.layout.addWidget(self.progress_bar)
        self.layout.addWidget(self.button)
        self.setLayout(self.layout)

        self.setWindowTitle('PyQt 多處理範例')
        self.setGeometry(300, 300, 300, 200)
        self.show()

    def start_path_planning(self):
        self.worker = PathPlanningWorker()
        self.worker.update_signal.connect(self.update_label)
        self.worker.progress_signal.connect(self.update_progress)
        self.worker.check_alive_signal.connect(self.check_process_alive)
        self.worker.start()

    def update_label(self, text):
        self.label.setText(text)

    def update_progress(self, value):
        self.progress_bar.setValue(value)

    def check_process_alive(self, is_alive):
        if not is_alive:
            QMessageBox.information(self, "訊息", "路徑規劃進程已終止")

if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = MyApp()
    sys.exit(app.exec_())