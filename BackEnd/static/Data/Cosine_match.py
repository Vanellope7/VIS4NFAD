import numpy as np
import json
import matplotlib.pyplot as plt
from scipy.signal import savgol_filter
from sklearn.metrics.pairwise import cosine_similarity
from sklearn.preprocessing import normalize

# 读取JSON文件
with open('drawing.json', 'r') as drawing_file:
    drawing_data = json.load(drawing_file)

with open('selectedSmoothedData.json', 'r') as smoothed_data_file:
    smoothed_data = json.load(smoothed_data_file)

# 提取路径信息并计算梯度
path_data = drawing_data[0]["path"]
drawing_y_coords = [command[2] for command in path_data if len(command) > 2]
drawing_x_coords = [command[1] for command in path_data if len(command) > 2]

# 上下翻转drawing的y坐标
drawing_y_coords = np.max(drawing_y_coords) - np.array(drawing_y_coords)

# 平滑手绘数据
drawing_y_coords_smooth = savgol_filter(drawing_y_coords, 11, 3)
drawing_x_coords_smooth = savgol_filter(drawing_x_coords, 11, 3)

# 计算梯度
drawing_gradients_y = np.gradient(drawing_y_coords_smooth)
drawing_gradients_x = np.gradient(drawing_x_coords_smooth)
drawing_gradients = np.sqrt(drawing_gradients_x**2 + drawing_gradients_y**2)
drawing_gradients = np.asarray(drawing_gradients).flatten()  # 转换为一维数组

# 提取时间序列数据并计算梯度
all_segments = []
for curve in smoothed_data:
    measurement_values = [point['y'] for point in curve['data']]
    measurement_gradients = np.gradient(measurement_values)
    measurement_gradients = np.asarray(measurement_gradients).flatten()  # 转换为一维数组
    for i in range(len(measurement_gradients) - len(drawing_gradients) + 1):
        segment = measurement_gradients[i:i + len(drawing_gradients)]
        all_segments.append((curve['name'], i, segment))

# 将所有段和drawing_gradients标准化
drawing_gradients = normalize(drawing_gradients.reshape(1, -1))[0]
all_segments_normalized = [normalize(segment.reshape(1, -1))[0] for _, _, segment in all_segments]

# 计算相似度
similarities = cosine_similarity([drawing_gradients], all_segments_normalized)[0]

# 获取最相似的段并按相似度排序
results = sorted([(all_segments[i][0], all_segments[i][1], similarities[i]) for i in range(len(similarities))], key=lambda x: x[2], reverse=True)

# 过滤高度重合的曲线段
filtered_results = []
used_indices = set()

for res in results:
    name, index, similarity = res
    if all(abs(index - used_index) > len(drawing_gradients) for used_index in used_indices):
        filtered_results.append(res)
        used_indices.add(index)
        if len(filtered_results) >= 25:
            break

for res in filtered_results:
    print(f"曲线: {res[0]}, 起始索引: {res[1]}, 相似度: {res[2]}")

# 可视化所有曲线并高亮相似度前25的曲线段
fig, ax = plt.subplots(figsize=(20, 8))

# 绘制所有原始曲线
for curve in smoothed_data:
    time_values = [point['x'][0] for point in curve['data']]
    measurement_values = [point['y'] for point in curve['data']]
    ax.plot(time_values, measurement_values, color='lightgray')

# 高亮相似度前25的曲线段
colors = plt.get_cmap('tab10')
for i, (name, index, similarity) in enumerate(filtered_results):
    curve = next(curve for curve in smoothed_data if curve['name'] == name)
    segment = curve['data'][index:index + len(drawing_gradients)]
    time_values = [point['x'][0] for point in segment]
    measurement_values = [point['y'] for point in segment]
    ax.plot(time_values, measurement_values, label=f"Segment {i+1} (Similarity: {similarity:.2f})", linewidth=2.5, color=colors(i / len(filtered_results)))

ax.set_title('Highlighted Matching Segments')
ax.set_xlabel('Time')
ax.set_ylabel('Measurement Value')
ax.legend()

plt.tight_layout()
plt.show()
