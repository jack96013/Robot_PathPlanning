'''
Author: TZU-CHIEH, HSU
Mail: j.k96013@gmail.com
Department: ECIE Lab, NTUT
Date: 2024-06-12 21:30:24
LastEditTime: 2024-06-12 21:30:28
Description: 
'''
import sys
from PyQt5.QtWidgets import QApplication, QLabel, QWidget, QVBoxLayout
from PyQt5.QtGui import QPainter, QLinearGradient, QBrush, QColor
from PyQt5.QtCore import Qt

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

class MainWindow(QWidget):
    def __init__(self):
        super().__init__()
        
        self.initUI()

    def initUI(self):
        layout = QVBoxLayout()

        low_color = "#FF00FF"  # Red
        high_color = "#0000FF"  # Blue

        gradient_label = GradientLabel(low_color, high_color)
        gradient_label.setText("Gradient from Red to Blue")
        gradient_label.setFixedHeight(50)  # Optional: set a fixed height

        layout.addWidget(gradient_label)
        self.setLayout(layout)

        self.setWindowTitle("Gradient Label Example")
        self.resize(300, 100)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())