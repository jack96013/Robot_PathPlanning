'''
Author: TZU-CHIEH, HSU
Mail: j.k96013@gmail.com
Department: ECIE Lab, NTUT
Date: 2024-06-09 21:37:40
LastEditTime: 2024-06-13 22:02:13
Description: 
'''

import sys
import socket
from PyQt5.QtCore import QThread, pyqtSignal
from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout, QTextEdit, QLineEdit, QPushButton

class TCPClientHandler(QThread):
    received_data = pyqtSignal(str)

    def __init__(self, host, port):
        super().__init__()
        self.host = host
        self.port = port
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.running = True

    def run(self):
        print("run")
        try:
            self.sock.connect((self.host, self.port))
            print(f"Connected to {self.host}:{self.port}")
            
            while self.running:
                data = self.sock.recv(1024)
                if not data:
                    break
                # print(data.decode('utf-8'))
        except Exception as e:
            print(f"Error: {e}")
        finally:
            self.sock.close()

    def send_data(self, data):
        try:
            self.sock.sendall(data.encode('utf-8'))
        except Exception as e:
            print(f"Send error: {e}")

    def stop(self):
        self.running = False
        self.sock.close()