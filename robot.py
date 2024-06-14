import cv2
import math
from AmigoBot import AmigoBot

from PyQt5.QtCore import QThread
import numpy as np


class Robot():
    def __init__(self):
        self.angles = 0
        self.location = None
        
        # For object detection
        self.front_center_point = ()
        self.rear_center_point = ()
        self.center_point = ()
        
        # For control
        self.robot_instance = AmigoBot()
        self.position_controller = RobotPositionController(self)
        
        self.velocity_l = 0
        self.velocity_r = 0
        self.velocity_kp = 0.2
        self.angle_kp = -99
        
        self.y = 0
        
        self.max_speed = 200
        
        self.error_x = 0
        self.error_y = 0
        self.omega = 0
        
        self.target = (0,0)
        
        self.theta_target = 0
        self.distance_target = 0
        
        
        
    def setLocation(self, cv_objects):
        #c = max(cnts, key=cv2.contourArea)
        contours_sorts = sorted(cv_objects, key=cv2.contourArea, reverse=True)
        
        if (len(contours_sorts) < 2):
            return None
        
        front_rect = cv2.minAreaRect(contours_sorts[1])
        rear_rect = cv2.minAreaRect(contours_sorts[0])

        self.front_center_point = front_rect[0]
        self.rear_center_point = rear_rect[0]        

        self.angles = self.calc_angle(self.rear_center_point,self.front_center_point)

        self.center_point = self.front_center_point

        return {"front":self.front_center_point, "rear":self.rear_center_point}
        

    def calc_angle(self,point1,point2):
        # 計算水平和垂直距離
        
        dx = point2[0] - point1[0]
        dy = point2[1] - point1[1]
        
        # 使用 atan2 計算角度（結果範圍為 -180 到 180）
        angle_rad = math.atan2(dy, dx)
        
        # 將弧度轉換為度數
        # angle_deg = math.degrees(angle_rad)
        
        # 確保角度在 0 到 360 度範圍內
        # if angle_deg < 0:
        #     angle_deg += 360
        
        return angle_rad

    def getLocation(self):
        if self.front_center_point is None or len(self.front_center_point)!=2:
            return (None,None)
        x = (self.front_center_point[0] + self.rear_center_point[0])/2
        y = (self.front_center_point[1] + self.rear_center_point[1])/2
        return (x,y)
    
    def getAngles(self):
        return self.angles
    
    def control_to_target(self, target_x, target_y):
        pass
    
    def start_position_control(self):
        self.position_controller.start()
    
    def stop_position_control(self):
        self.position_controller.stop()
        
    
    def move_to_target(self,target_x, target_y):
        # PI 控制
        self.error_x = target_x - self.getLocation()[0]
        self.error_y = target_y - self.getLocation()[1]
        self.target = (target_x, target_y)
        
        # self.theta_target = np.arctan2(self.error_y, self.error_x)
        self.theta_target = self.calc_angle((target_x,target_y),self.getLocation())
        error_theta = self.theta_target - self.getAngles()  # 計算角度誤差量
        
        if error_theta > math.pi:
            error_theta -= 2*math.pi
        elif error_theta < -1*math.pi:
            error_theta += 2*math.pi
        
        error_theta = min(error_theta, 2*math.pi-error_theta)
        self.distance_target = np.sqrt(self.error_x**2 + self.error_y**2)
        v = self.velocity_kp * self.distance_target
        self.omega = self.angle_kp * error_theta
        
        self.velocity_l = v - self.omega
        self.velocity_r = v + self.omega
        
        # print(f"{self.error_x},{self.error_y},{self.omega}")
        
        
        if self.velocity_l >= self.max_speed:
            self.velocity_l = self.max_speed
        elif self.velocity_l <= -1*self.max_speed:
            self.velocity_l = -1 * self.max_speed
            
        if self.velocity_r >= self.max_speed:
            self.velocity_r = self.max_speed
        elif self.velocity_r <= -1*self.max_speed:
            self.velocity_r = -1 * self.max_speed
        
        self.robot_instance.send_speed(self.velocity_l, self.velocity_r)
        # self.robot_instance.send_speed(self.velocity_r, self.velocity_l)
        
        
        
# Robot Controller (Multi Thread)
class RobotPositionController(QThread):
    def __init__(self, robot:Robot):
        super().__init__()
        self.robot = robot
        self.stopSignal = False
        
    def run(self):
        self.control_to_target(None, None)
        self.stopSignal = False
        pass
    
    def stop(self):
        self.stopSignal = True
    
    def control_to_target(self, target_x, target_y):
        
        print("Position Control Thread Start")
        pathList = [(1500, 800)]
        
        while True:
            if self.stopSignal:
                return
        
            if len(pathList) > 0:
                target = pathList[0]
                current_x = self.robot.getLocation()[0]
                current_y = self.robot.getLocation()[1]
                if (current_x is None or current_y is None):
                    continue
                
                # print(f"{current_x},{current_y},{self.robot.velocity_kp}")
                
                # 判定是否達到目標點
                if np.sqrt((current_x - target[0])**2 + (current_y - target[1])**2) < 10:
                    pathList.pop(0)
                    break
            else:
                # 如果所有路徑都迭代完
                print("finish")
                self.amigo_bot.stop()
                break
            
            if pathList:
                self.robot.move_to_target(pathList[0][0],pathList[0][1])

            self.msleep(100)
            
            # self.amigo_bot.update_position(dt)
            # self.positions.append((robot.x, robot.y))
        

