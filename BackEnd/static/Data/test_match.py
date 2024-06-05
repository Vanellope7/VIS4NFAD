import numpy as np
import json
import matplotlib.pyplot as plt
from scipy.signal import savgol_filter
from sklearn.metrics.pairwise import cosine_similarity
from sklearn.preprocessing import normalize
from tqdm import tqdm
from joblib import Parallel, delayed
import mplcursors

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

# 计算斜率
drawing_slope = (drawing_y_coords_smooth[-1] - drawing_y_coords_smooth[0]) / (drawing_x_coords_smooth[-1] - drawing_x_coords_smooth[0])

# 提取时间序列数据并计算增减趋势和斜率
all_segments = []
for curve in smoothed_data:
    measurement_values = [point['y'] for point in curve['data']]
    measurement_trend = np.diff(measurement_values)
    measurement_trend = np.sign(measurement_trend)
    for i in range(len(measurement_trend) - len(drawing_trend) + 1):
        segment = measurement_trend[i:i + len(drawing_trend)]
        segment_values = measurement_values[i:i + len(drawing_trend) + 1]
        segment_slope = (segment_values[-1] - segment_values[0]) / (len(segment_values) - 1)
        all_segments.append((curve['name'], i, segment, segment_values, segment_slope))

# 计算欧氏距离的最大值
euclidean_distances_list = [np.linalg.norm(drawing_trend - segment[2]) for segment in all_segments]
max_euclidean_distance = np.max(euclidean_distances_list)

# 使用并行计算来提高相似度计算速度
def calculate_similarities(segment, max_euclidean_distance, drawing_slope):
    cosine_sim = cosine_similarity([drawing_trend], [segment[2]])[0][0]
    euclidean_dist = np.linalg.norm(drawing_trend - segment[2])
    slope_similarity = 1 - np.abs(drawing_slope - segment[4]) / np.max([np.abs(drawing_slope), np.abs(segment[4])])
    combined_similarity = (cosine_sim + (1 - euclidean_dist / max_euclidean_distance) + slope_similarity) / 3
    return segment[0], segment[1], combined_similarity, segment[3]

# 初步筛选阶段
initial_filtered_segments = [segment for segment in all_segments if np.sum(np.abs(segment[2] - drawing_trend)) / len(drawing_trend) < 1.5]

# 并行计算相似度
results = Parallel(n_jobs=-1)(delayed(calculate_similarities)(segment, max_euclidean_distance, drawing_slope) for segment in tqdm(initial_filtered_segments, desc="Calculating similarities"))

# 设置相似度阈值
similarity_threshold = 0.85

# 筛选超过阈值的结果
results = [res for res in results if res[2] >= similarity_threshold]

# 过滤高度重合的曲线段
filtered_results = []
used_indices = set()

for res in tqdm(results, desc="Filtering results"):
    name, index, similarity, segment_values = res
    if all(abs(index - used_index) > len(drawing_trend) for used_index in used_indices):
        filtered_results.append(res)
        used_indices.add(index)

for res in filtered_results:
    print(f"曲线: {res[0]}, 起始索引: {res[1]}, 综合相似度: {res[2]}")

# 可视化所有曲线并高亮相似度超过阈值的曲线段
fig, ax = plt.subplots(figsize=(20, 8))

# 绘制所有原始曲线
for curve in smoothed_data:
    time_values = [point['x'][0] for point in curve['data']]
    measurement_values = [point['y'] for point in curve['data']]
    ax.plot(time_values, measurement_values, color='lightgray')

# 高亮相似度超过阈值的曲线段，使用红色
highlight_color = 'red'
lines = []
for i, (name, index, similarity, segment_values) in enumerate(filtered_results):
    curve = next(curve for curve in smoothed_data if curve['name'] == name)
    segment = curve['data'][index:index + len(drawing_trend) + 1]
    time_values = [point['x'][0] for point in segment]
    measurement_values = [point['y'] for point in segment]
    line, = ax.plot(time_values, measurement_values, label=f"Segment {i+1} (Similarity: {similarity:.2f})", linewidth=2.5, color=highlight_color)
    lines.append(line)

# 添加鼠标悬浮显示相似度功能
cursor = mplcursors.cursor(lines, hover=True)
@cursor.connect("add")
def on_add(sel):
    sel.annotation.set_text(f"Similarity: {sel.artist.get_label().split(': ')[1]}")

ax.set_title('Highlighted Matching Segments')
ax.set_xlabel('Time')
ax.set_ylabel('Measurement Value')
ax.legend()

plt.tight_layout()
plt.show()
