import json
import matplotlib.pyplot as plt

# 从文件中读取JSON数据
with open('../static/Data/drawing.json', 'r') as file:
    data = json.load(file)

# 提取路径数据
path_data = data["objects"][0]["path"]

# 准备绘图数据
x_points = []
y_points = []

for command in path_data:
    if command[0] == "M" or command[0] == "L":
        x_points.append(command[1])
        y_points.append(command[2])
    elif command[0] == "Q":
        # 二次贝塞尔曲线的终点
        x_points.append(command[3])
        y_points.append(command[4])

# 绘制曲线
plt.figure(figsize=(8, 8))
plt.plot(x_points, [-y for y in y_points], marker='o')  # 反转Y轴方向
plt.title('Path from drawing.json')
plt.xlabel('X')
plt.ylabel('Y')
plt.grid(True)
plt.gca().set_aspect('equal', adjustable='box')
plt.show()
