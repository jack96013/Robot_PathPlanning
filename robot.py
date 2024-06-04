import cv2
import math

class Robot():
    def __init__(self):
        self.angles = 0
        self.location = None
        
        self.front_center_point = ()
        self.rear_center_point = ()
        self.center_point = ()
        
        pass

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
        angle_deg = math.degrees(angle_rad)
        
        # 確保角度在 0 到 360 度範圍內
        # if angle_deg < 0:
        #     angle_deg += 360
        
        return angle_deg

    def getLocation(self):
        if self.front_center_point is None or len(self.front_center_point)!=2:
            return (None,None)
        x = (self.front_center_point[0] + self.rear_center_point[0])/2
        y = (self.front_center_point[1] + self.rear_center_point[1])/2
        return (x,y)
    
    def getAngles(self):
        return self.angles
        