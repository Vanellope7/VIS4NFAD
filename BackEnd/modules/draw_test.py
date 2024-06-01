import json
import os
import glob
from datetime import datetime
import matplotlib.pyplot as plt

# 目录路径
data_folder = '../static/Data'

# 查找目录中所有的 JSON 文件
json_files = glob.glob(os.path.join(data_folder, 'drawing_*.json'))

# 如果没有找到任何文件，提示并退出
if not json_files:
    print("No JSON files found in the directory.")
    exit()

# 找到最新的 JSON 文件
latest_file = max(json_files, key=os.path.getctime)
print(f"Latest JSON file: {latest_file}")

# 读取 JSON 文件
with open(latest_file, 'r') as file:
    data = json.load(file)

# 提取路径数据
paths = []
for obj in data['objects']:
    if obj['type'] == 'path':
        paths.append(obj['path'])

# 绘制路径
for path in paths:
    x = []
    y = []
    for command in path:
        if command[0] == 'M' or command[0] == 'L':
            x.append(command[1])
            y.append(command[2])
        elif command[0] == 'Q':
            x.extend([command[1], command[3]])
            y.extend([command[2], command[4]])

    plt.plot(x, y, marker='o')

# 设置图形参数
plt.title('Drawing from Latest JSON')
plt.xlabel('X')
plt.ylabel('Y')
plt.grid(True)

# 显示图形
plt.show()
