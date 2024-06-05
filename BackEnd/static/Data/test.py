import json
import matplotlib.pyplot as plt

# 读取JSON文件
with open('drawing.json', 'r') as drawing_file:
    drawing_data = json.load(drawing_file)

with open('selectedSmoothedData.json', 'r') as smoothed_data_file:
    smoothed_data = json.load(smoothed_data_file)

# 提取路径信息
path_data = drawing_data[0]["path"]

# 初始化图表
fig, axs = plt.subplots(1, 2, figsize=(14, 6))

# 绘制第一个可视化曲线
ax1 = axs[0]
ax1.set_aspect('equal')
ax1.invert_yaxis()
ax1.set_title('Drawing Path Visualization')
ax1.set_xlabel('X Coordinate')
ax1.set_ylabel('Y Coordinate')

# 设置初始点
x, y = None, None

for command in path_data:
    cmd = command[0]
    if cmd == "M":
        # 移动到初始点
        x, y = command[1], command[2]
        ax1.plot(x, y, 'bo')  # 画初始点
    elif cmd == "Q":
        # 提取贝塞尔曲线控制点和终点
        cx, cy = command[1], command[2]
        x_end, y_end = command[3], command[4]
        
        # 生成贝塞尔曲线的点
        t_values = [t / 100.0 for t in range(101)]
        x_values = [(1 - t) ** 2 * x + 2 * (1 - t) * t * cx + t ** 2 * x_end for t in t_values]
        y_values = [(1 - t) ** 2 * y + 2 * (1 - t) * t * cy + t ** 2 * y_end for t in t_values]
        
        # 绘制贝塞尔曲线
        ax1.plot(x_values, y_values, 'b', linewidth=1)
        
        # 更新当前点
        x, y = x_end, y_end
    elif cmd == "L":
        # 直线到目标点
        x_end, y_end = command[1], command[2]
        
        # 绘制直线
        ax1.plot([x, x_end], [y, y_end], 'b', linewidth=1)
        
        # 更新当前点
        x, y = x_end, y_end

# 绘制第二个可视化曲线
ax2 = axs[1]
ax2.set_title('Smoothed Time-Series Data Visualization')
ax2.set_xlabel('Time')
ax2.set_ylabel('Measurement Value')

for curve in smoothed_data:
    time_values = [point['x'][0] for point in curve['data']]
    measurement_values = [point['y'] for point in curve['data']]
    ax2.plot(time_values, measurement_values, marker='o', linestyle='-', linewidth=1, label=curve['name'])  # 调整线条宽度

ax2.legend()

plt.tight_layout()
plt.show()
