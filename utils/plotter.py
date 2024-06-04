import matplotlib.pyplot as plt
import numpy as np

from config.config_parser import parser
plt.ion()
fig, (ax1, ax2) = plt.subplots(1, 2)

iterList = []
lenList = []
iter = 0

def plot(obstacles, path_points, population, path_lengths, gen, last_gen):

    for i, chromosome in enumerate(population):
        _reset_plot(obstacles, path_points)
        
        # 染色體解碼器
        path_x = [path_points[j][0] for j, c in enumerate(chromosome) if c == '1']
        path_y = [path_points[j][1] for j, c in enumerate(chromosome) if c == '1']

        ax1.plot(path_x, path_y, '-')
        ax1.text(1, int(parser['Plot Axes']['y_end'])+1, f"Generation: {gen}, Chromosome No. {i+1}\nPath Length:{path_lengths[i]}")

        # ax2.plot(gen,path_lengths)
        global iter,lenList,iterList
        iter = iter + 1
        iterList.append(iter)
        lenList.append(path_lengths[i])
        ax2.cla()
        ax2.plot(iterList,lenList)
        
        # plt.pause(0.025) this disrupts window focus, so use the below lines
        plt.gcf().canvas.draw_idle()
        plt.gcf().canvas.start_event_loop(0.025)
    
    if last_gen:
        _show_final_path(obstacles, path_points, population, path_lengths, gen)

def _show_final_path(obstacles, path_points, population, path_lengths, gen):
    index_min = np.argmin(path_lengths)

    plt.ioff()
    _reset_plot(obstacles, path_points)
    
    chromosome = population[index_min]

    path_x = [path_points[j][0] for j, c in enumerate(chromosome) if c == '1']
    path_y = [path_points[j][1] for j, c in enumerate(chromosome) if c == '1']

    ax1.plot(path_x, path_y, '-')
    ax1.text(1, int(parser['Plot Axes']['y_end']) + 1, f"Finished at generation: {gen}\nShortest Path Found:{path_lengths[index_min]}")

    plt.pause(1)
    print('Done! You may now close the window.')
    plt.show()

def _reset_plot(obstacles, path_points):
    
    ax1.cla()

    axes = parser['Plot Axes']
    ax1.axis([int(axes['x_start']), 
        int(axes['x_end']),
        int(axes['y_start']),
        int(axes['y_end'])])

    _plot_obstacles(obstacles)
    _plot_path_points(path_points)

def _plot_path_points(path_points):
    path_point_x = [path_point[0] for path_point in path_points]
    path_point_y = [path_point[1] for path_point in path_points]

    ax1.plot(path_point_x[1:-1], path_point_y[1:-1], "k.")
    ax1.plot(path_point_x[0], path_point_y[0], "bo", label='Source')
    ax1.plot(path_point_x[-1], path_point_y[-1], "go", label='Goal')

    ax1.legend(loc="upper left")

def _plot_obstacles(obstacles):
    
    for obstacle in obstacles:
        x_values, y_values = [], []

        for vertex in obstacle:
            x_values.append(vertex[0])
            y_values.append(vertex[1])
        
        ax1.fill(x_values, y_values, 'r')