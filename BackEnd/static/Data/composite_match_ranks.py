import numpy as np
import json
import matplotlib.pyplot as plt
from scipy.signal import savgol_filter
from sklearn.metrics.pairwise import cosine_similarity, euclidean_distances
from sklearn.preprocessing import normalize
from tqdm import tqdm

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

# 计算增减趋势
drawing_trend = np.diff(drawing_y_coords_smooth)
drawing_trend = np.sign(drawing_trend)

# 提取时间序列数据并计算增减趋势
all_segments = []
for curve in smoothed_data:
    measurement_values = [point['y'] for point in curve['data']]
    measurement_trend = np.diff(measurement_values)
    measurement_trend = np.sign(measurement_trend)
    for i in range(len(measurement_trend) - len(drawing_trend) + 1):
        segment = measurement_trend[i:i + len(drawing_trend)]
        all_segments.append((curve['name'], i, segment, measurement_values[i:i + len(drawing_trend) + 1]))

# 计算相似度
cosine_similarities = []
euclidean_distances_list = []

for _, _, segment, _ in tqdm(all_segments, desc="Calculating similarities"):
    cosine_similarities.append(cosine_similarity([drawing_trend], [segment])[0][0])
    euclidean_distances_list.append(euclidean_distances([drawing_trend], [segment])[0][0])

# 综合评价
similarities = [(cosine_similarities[i] + (1 - euclidean_distances_list[i] / np.max(euclidean_distances_list))) / 2 for i in range(len(cosine_similarities))]

# 获取最相似的段并按相似度排序
results = sorted([(all_segments[i][0], all_segments[i][1], similarities[i], all_segments[i][3]) for i in range(len(similarities))], key=lambda x: x[2], reverse=True)

# 过滤高度重合的曲线段
filtered_results = []
used_indices = set()

for res in tqdm(results, desc="Filtering results"):
    name, index, similarity, segment_values = res
    if all(abs(index - used_index) > len(drawing_trend) for used_index in used_indices):
        filtered_results.append(res)
        used_indices.add(index)
        if len(filtered_results) >= 40:  # 只保留前10名
            break

for res in filtered_results:
    print(f"曲线: {res[0]}, 起始索引: {res[1]}, 综合相似度: {res[2]}")

# 可视化所有曲线并高亮前10名的曲线段
fig, ax = plt.subplots(figsize=(20, 8))

# 绘制所有原始曲线
for curve in smoothed_data:
    time_values = [point['x'][0] for point in curve['data']]
    measurement_values = [point['y'] for point in curve['data']]
    ax.plot(time_values, measurement_values, color='lightgray')

# 高亮前10名的曲线段，使用红色
highlight_color = 'red'
for i, (name, index, similarity, segment_values) in enumerate(filtered_results):
    curve = next(curve for curve in smoothed_data if curve['name'] == name)
    segment = curve['data'][index:index + len(drawing_trend) + 1]
    time_values = [point['x'][0] for point in segment]
    measurement_values = [point['y'] for point in segment]
    ax.plot(time_values, measurement_values, label=f"Segment {i+1} (Similarity: {similarity:.2f})", linewidth=2.5, color=highlight_color)

ax.set_title('Highlighted Matching Segments')
ax.set_xlabel('Time')
ax.set_ylabel('Measurement Value')
ax.legend()

plt.tight_layout()
plt.show()
