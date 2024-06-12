'''
Author: TZU-CHIEH, HSU
Mail: j.k96013@gmail.com
Department: ECIE Lab, NTUT
Date: 2024-06-12 18:07:44
LastEditTime: 2024-06-12 20:05:47
Description: 
'''
'''
Author: TZU-CHIEH, HSU
Mail: j.k96013@gmail.com
Department: ECIE Lab, NTUT
Date: 2024-06-12 18:07:44
LastEditTime: 2024-06-12 18:16:57
Description: 
'''

from TCPClientHandler import TCPClientHandler


class AmigoBot:
    def __init__(self):
        # self.name = name
        # self.position = [0, 0]  # 假設機器人初始位置在原點
        # self.direction = 'N'    # 初始方向為北（N, E, S, W 分別代表北、東、南、西）
        
        self.client_host = "127.0.0.1"
        self.client_port = 27015
        self.client = TCPClientHandler(self.client_host, self.client_port)
        # self.client.received_data.connect(self.update_text_edit)
        self.speed_L = 500
        self.speed_R = 500
        
        
    def connectToRelay(self, host = None, port = None):
        if (host != None):
            self.client_host = host
            self.client_port = port
        self.client.start()
        
    def isConnected(self):
        # TODO
        # return self.client.
        pass
    
    # Direction control
    def move_forward(self):
        self.send_speed(1*self.speed_L, 1*self.speed_R)
    def move_backward(self):
        self.send_speed(-1*self.speed_L, -1*self.speed_R)

    def turn_left(self):
        self.send_speed(-1*self.speed_L, self.speed_R)

    def turn_right(self):
       self.send_speed(1*self.speed_L, -1*self.speed_R)
    
    def stop(self):
        self.send_speed(0, 0)
    
    def send_speed(self,speed_l,speed_r):
        command = f"setVel={speed_l}:{speed_r}\n"
        self.client.send_data(command)
        
    def _print_status(self):
       pass

    
