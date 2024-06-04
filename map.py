import matplotlib.pyplot as plt
import numpy as np

class Map():
    def __init__(self):
        plt.ion()

        # self.fig, self.ax1 = plt.subplots()

        pass

    def _plot_obstacles(self, obstacles):
        for obstacle in obstacles:
            x_values, y_values = [], []

            for vertex in obstacle:
                x_values.append(vertex[0])
                y_values.append(vertex[1])
            
            self.ax.fill(x_values, y_values, 'r')

    