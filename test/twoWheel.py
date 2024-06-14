'''
Author: TZU-CHIEH, HSU
Mail: j.k96013@gmail.com
Department: ECIE Lab, NTUT
Date: 2024-06-12 23:39:42
LastEditTime: 2024-06-13 07:54:40
Description: 
'''
import numpy as np
import matplotlib.pyplot as plt

class TwoWheelRobot:
    def __init__(self, x=0, y=0, theta=0, Kp=1.0):
        self.x = x
        self.y = y
        self.theta = theta  # 机器人朝向角度
        self.Kp = Kp  # 比例控制增益
        self.left_wheel_speed = 0
        self.right_wheel_speed = 0

    def update_position(self, dt):
        # 根据左右轮速度更新位置和朝向
        v = (self.left_wheel_speed + self.right_wheel_speed) / 2
        omega = (self.right_wheel_speed - self.left_wheel_speed) / 2  # 机器人宽度为1
        self.x += v * np.cos(self.theta) * dt
        self.y += v * np.sin(self.theta) * dt
        self.theta += omega * dt

    def set_wheel_speeds(self, left_speed, right_speed):
        self.left_wheel_speed = left_speed
        self.right_wheel_speed = right_speed

    def control_to_target(self, target_x, target_y):
        # 简单比例控制器
        error_x = target_x - self.x
        error_y = target_y - self.y
        target_theta = np.arctan2(error_y, error_x)
        error_theta = target_theta - self.theta
        self.Kp = 0.002
        v = self.Kp * np.sqrt(error_x**2 + error_y**2)
        self.Kp = 0.01
        omega = self.Kp * error_theta
        self.set_wheel_speeds(v - omega, v + omega)
        # print(v - omega,v + omega)

# 创建机器人实例
robot = TwoWheelRobot(Kp=0.1)

# 定义路径（例如一条直线）
path = [(0, 0), (1, 2), (2, 2), (0, 3), (4, 4), (0, 7.5)]
path_cpy = path.copy()
# path = [ (5, 5)]

# 仿真参数
dt = 0.1  # 时间步长
total_time = 100000  # 总时间

# 记录机器人位置
positions = []

for t in np.arange(0, total_time, dt):
    if path:
        target = path[0]
        if np.sqrt((robot.x - target[0])**2 + (robot.y - target[1])**2) < 0.1:
            path.pop(0)  # 达到目标点，移除
    else:
        break
    if path:
        robot.control_to_target(*path[0])
    robot.update_position(dt)
    positions.append((robot.x, robot.y))

# 绘制机器人路径
positions = np.array(positions)
plt.plot(positions[:, 0], positions[:, 1], label='Robot Path')
plt.plot([p[0] for p in path], [p[1] for p in path], 'ro', label='Target Points')
plt.plot([p[0] for p in path_cpy], [p[1] for p in path_cpy], 'ro', label='Target Points')
plt.xlabel('X')
plt.ylabel('Y')
plt.legend()
plt.grid()
plt.title('Two Wheel Robot Path Tracking')
plt.show()