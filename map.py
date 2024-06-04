import matplotlib.pyplot as plt
import numpy as np
import cv2

from robot import Robot
from endPoint import EndPoint
import math

from utils.path_point_generator import generate_path_points

from genetic_algorithm import start, path_overlaps_obstacle
import genetic_algorithm as ga

from PyQt5 import QtTest

class Map():
    def __init__(self,cv_obj_dict,fig):
        plt.ion()
        self.cv_obj_dict = cv_obj_dict
        self.sc = fig
        self.robot = Robot()
        self.end_point = EndPoint()

        self.path_point_list = list()
        self.path_validity = dict()
        self.obstacle_list = list()

        self.new_population = list()
        
        
        # self.fig, self.ax1 = plt.subplots()
        self.plot_path(self.path_point_list,self.new_population)

        pass
    
    def update(self):
        
        
        if (len(self.cv_obj_dict["robot"]["Objects"])!= 0):
            loc = self.robot.setLocation(self.cv_obj_dict["robot"]["Objects"])
        
        self.end_point.setLocation(self.cv_obj_dict["end"]["Objects"])


        for obstacle in self.cv_obj_dict["obstacles"]["Objects"]:
            rect = cv2.minAreaRect(obstacle)
            box = cv2.boxPoints(rect)
            self.obstacle_list.append(np.intp(box))


        if len(self.path_point_list) == 0:
            self._init_path_points()
            print(f'Path Points = {len(self.path_point_list)}')
        else:
            self.path_point_list[0] = (int(self.robot.getLocation()[0]),int(self.robot.getLocation()[1]))
            self.path_point_list[-1] = self.end_point.getLocation()
        
        
            
        

    def _plot_obstacles(self,obstacles):
    
        for obstacle in obstacles:
            x_values, y_values = [], []

            for vertex in obstacle:
                x_values.append(vertex[0])
                y_values.append(vertex[1])
            
            self.sc.axes.fill(x_values, y_values, 'g')

    
    def plot_map(self):
        # PLOT
        self.sc.axes.cla()
        self.sc.axes.invert_yaxis()
        self.sc.axes.xaxis.set_ticks_position('top')


        obstacles = self.cv_obj_dict["obstacles"]["Objects"]

        # Obstacles drawer
        # obstacles_loc_list = []
        
        self._plot_obstacles(obstacles)
        
        # if self.object_detector.processor.current_image is not None:
            # self.sc.axes.imshow(self.current_image)
        
        self._plot_robot()
        # self._plot_end_point()
        self._plot_path_points(self.path_point_list)

        self.plot_path(self.path_point_list,self.new_population)
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


    def _init_path_points(self):
        self.path_point_list.clear()
        generate_path_points(self.path_point_list, self.obstacle_list)
        self.path_point_list[0] =  (int(self.robot.getLocation()[0]),int(self.robot.getLocation()[1]))
        self._init_path_validity()
        pass


    def _plot_path_points(self, path_points):
        path_point_x = [path_point[0] for path_point in path_points]
        path_point_y = [path_point[1] for path_point in path_points]

        self.sc.axes.plot(path_point_x[1:-1], path_point_y[1:-1], "k.")
        self.sc.axes.plot(path_point_x[0], path_point_y[0], "bo", label='Source')
        self.sc.axes.plot(path_point_x[-1], path_point_y[-1], "go", label='Goal')

        # self.sc.axes.legend(loc="upper left")

    def _init_path_validity(self):
        for i, path_point_start in enumerate(self.path_point_list):

            if path_point_start not in self.path_validity:
                self.path_validity[path_point_start] = [True] * len(self.path_point_list)

            for j, path_point_end in enumerate(self.path_point_list):

                if path_point_end not in self.path_validity:
                    self.path_validity[path_point_end] = [True] * len(self.path_point_list)

                if path_overlaps_obstacle(path_point_start, path_point_end, self.obstacle_list):
                    self.path_validity[path_point_start][j] = False
                    self.path_validity[path_point_end][i] = False
        
    def start_planning(self):
        
        population = ga._generate_population(self.path_point_list, self.obstacle_list, self.path_validity)    # 生成所有傳播路徑 (100000001000100010100001001) One-Hot 解碼
        path_lengths = []

        for chromosome in population:   
            path_lengths.append(ga._calculate_path_length(chromosome, self.path_point_list))    # 計算所有長度

        # plot(self.obstacle_list, self.path_points, population, path_lengths, 1, False)

        # 進行疊代，疊代指定次數
        generations = int(2)
        
        for gen in range(generations - 1):
            new_population = []
            path_lengths.clear()

            fitness_list = ga._sort_by_fitness(population, self.path_point_list)

            for chromosome in population:
                self.new_population.clear()
                while True:
                    parent1 = ga._choose_random_parent(fitness_list)
                    parent2 = ga._choose_random_parent(fitness_list)

                    child = ga._crossover(parent1, parent2)

                    if ga.randint(1, 10) <= 10 * float(0.3):
                        child = ga._mutation(child)

                    if ga._chromosome_valid(child, self.obstacle_list, self.path_point_list):
                        break
                
                path_lengths.append(ga._calculate_path_length(child, self.path_point_list))
                self.new_population.append(child)
                QtTest.QTest.qWait(100)
                # print(path_lengths)
                
            population = self.new_population 
            
            print(f'gen={gen}, path_lengths={path_lengths[-1]}')
            # self.plot_path(self.path_point_list, new_population, path_lengths, (gen+2), last_gen=True if gen == generations-2 else False )
            # self.plot_path(self.path_point_list,self.new_population)
        pass
        print("finish")

    def plot_path(self , path_points, population):
        
        for i, chromosome in enumerate(population):
            path_x = [path_points[j][0] for j, c in enumerate(chromosome) if c == '1']
            path_y = [path_points[j][1] for j, c in enumerate(chromosome) if c == '1']
            self.sc.axes.plot(path_x, path_y, '-')
        
        
        # self.sc.axes.text(1, int(parser['Plot Axes']['y_end'])+1, f"Generation: {gen}, Chromosome No. {i+1}\nPath Length:{path_lengths[i]}")
