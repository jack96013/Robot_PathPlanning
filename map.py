import matplotlib.pyplot as plt
import numpy as np
import cv2

from robot import Robot
from endPoint import EndPoint
import math
import pathHandler 

class Map():
    def __init__(self,cv_obj_dict,fig):
        plt.ion()
        self.cv_obj_dict = cv_obj_dict
        self.sc = fig
        self.robot = Robot()
        self.end_point = EndPoint()

        # self.fig, self.ax1 = plt.subplots()

        pass
    
    def update(self):
        if (len(self.cv_obj_dict["robot"]["Objects"])!= 0):
            loc = self.robot.setLocation(self.cv_obj_dict["robot"]["Objects"])
        
        self.end_point.setLocation(self.cv_obj_dict["end"]["Objects"])

        pass
        

    def _plot_obstacles(self,obstacles):
    
        for obstacle in obstacles:
            x_values, y_values = [], []

            for vertex in obstacle:
                x_values.append(vertex[0][0])
                y_values.append(vertex[0][1])
            
            self.sc.axes.fill(x_values, y_values, 'g')

    
    def plot_map(self):
        # PLOT
        self.sc.axes.cla()
        self.sc.axes.invert_yaxis()
        self.sc.axes.xaxis.set_ticks_position('top')


        obstacles = self.cv_obj_dict["obstacles"]["Objects"]

        # Obstacles drawer
        obstacles_loc_list = []
        for obstacle in obstacles:
            rect = cv2.minAreaRect(obstacle)
            box = cv2.boxPoints(rect)
            obstacles_loc_list.append(np.intp(box))
            self._plot_obstacles(obstacles)

        
        
        
        # if self.object_detector.processor.current_image is not None:
            # self.sc.axes.imshow(self.current_image)
        
        self._plot_robot()
        self._plot_end_point()
        
        
        #self.sc.axes.plot(self.iterList, self.valueList)
        self.sc.draw()

        pass

    def _plot_robot(self):
        center_point = self.robot.getLocation()

        robot_point = plt.Circle(center_point,50,color='r')
        # robot_point2 = plt.Circle(front,10,color='r')
        
        length = 30

        dx = length*math.cos(math.radians(self.robot.getAngles()))
        dy = length*math.sin(math.radians(self.robot.getAngles()))

        # robot_arrow = plt.arrow(rear[0],rear[1],dx,dy)
        self.sc.axes.add_patch(robot_point)
        # self.sc.axes.add_patch(robot_point2)
        self.sc.axes.arrow(center_point[0],center_point[1],dx,dy,head_width=30)
        # if (loc != None):
        #     pass
        # cv2.arrowedLine(frame, (int(loc["rear"][0]),int(loc["rear"][1])),  (int(loc["front"][0]),int(loc["front"][1])), (0, 0, 255), 2) 
    
        
        
    
    def _plot_end_point(self):
        center_point = self.end_point.getLocation()
        if center_point is not None:
            end_point_circle = plt.Circle(center_point,10,color='b')
            self.sc.axes.add_patch(end_point_circle)



    

    