import os
import glob
import json
import numpy as np
import matplotlib.pyplot as plt
from scipy.signal import savgol_filter
from scipy.spatial.distance import cdist
from tqdm import tqdm

# 查找目录中最新的JSON文件并读取数据
def load_latest_drawing_data(data_folder):
    # 查找目录中所有的 JSON 文件
    json_files = glob.glob(os.path.join(data_folder, 'drawing.json'))

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

    return data

# 解析草图数据
def parse_sketch_data(sketch_data):
    path_data = sketch_data['objects'][0]['path']
    points = []
    for segment in path_data:
        if segment[0] == 'M' or segment[0] == 'L':
            points.append((segment[1], segment[2]))
        elif segment[0] == 'Q':
            points.append((segment[3], segment[4]))
    return np.array(points, dtype=np.float64)

# 曲线平滑函数
def smooth_curve(curve, window_length, polyorder):
    # 确保窗口长度为奇数且小于等于曲线长度
    if window_length >= len(curve):
        window_length = len(curve) if len(curve) % 2 == 1 else len(curve) - 1
    # 确保多项式阶数小于窗口长度
    if polyorder >= window_length:
        polyorder = window_length - 1
    y_smooth = savgol_filter(curve[:, 1], window_length, polyorder)
    return np.column_stack((curve[:, 0], y_smooth))

# 曲线归一化函数
def normalize_curve(curve):
    min_val = np.min(curve, axis=0)
    max_val = np.max(curve, axis=0)
    range_val = max_val - min_val
    if np.isscalar(range_val):
        if range_val == 0:
            range_val = 1
    else:
        range_val[range_val == 0] = 1  # 防止除以0
    return (curve - min_val) / range_val

# 动态时间规整(DTW)函数
def dtw_distance(s1, s2):
    d = cdist(s1[:, None], s2[:, None], metric='euclidean')
    cost = np.zeros_like(d)
    cost[0, 0] = d[0, 0]
    for i in range(1, s1.shape[0]):
        cost[i, 0] = cost[i - 1, 0] + d[i, 0]
    for j in range(1, s2.shape[0]):
        cost[0, j] = cost[0, j - 1] + d[0, j]
    for i in range(1, s1.shape[0]):
        for j in range(1, s2.shape[0]):
            cost[i, j] = min(cost[i - 1, j], cost[i, j - 1], cost[i - 1, j - 1]) + d[i, j]
    path = []
    i, j = s1.shape[0] - 1, s2.shape[0] - 1
    path.append((i, j))
    while i > 0 and j > 0:
        i, j = min((i - 1, j), (i, j - 1), (i - 1, j - 1), key=lambda x: cost[x[0], x[1]])
        path.append((i, j))
    path.append((0, 0))
    path.reverse()
    return cost[-1, -1], path

# 查找相似段的函数
def find_top_matches(sketch, curve, window_length, polyorder, top_n=10):
    time_series = np.arange(len(curve))
    curve_2d = np.column_stack((time_series, curve))
    smooth_curve_data = smooth_curve(curve_2d, window_length, polyorder)
    normalized_curve = normalize_curve(smooth_curve_data)
    normalized_sketch = normalize_curve(sketch)

    matches = []
    segment_length = len(normalized_sketch)
    for i in range(len(normalized_curve) - segment_length + 1):
        segment = normalized_curve[i:i + segment_length]
        distance, _ = dtw_distance(normalized_sketch[:, 1], segment[:, 1])
        matches.append((distance, i, i + segment_length))

    matches.sort(key=lambda x: x[0])
    return matches[:top_n]

# 主程序
def main():
    data_folder = '../static/Data'
    sketch_json = load_latest_drawing_data(data_folder)

    # 解析草图数据
    sketch_curve = parse_sketch_data(sketch_json)

    # 平滑和归一化草图曲线
    window_length = 50  # 平滑窗口长度
    polyorder = 2  # 多项式阶数

    # 加载Hcn数据
    hcn_file_path = '../modules/static/Data/hcnData.json'
    with open(hcn_file_path, 'r') as file:
        hcn_data = json.load(file)
    hcn_curves = np.array(hcn_data['hcn'], dtype=np.float64)
    time_data = np.arange(hcn_curves.shape[1])

    # 选择特定的Hcn曲线进行匹配，例如4043/hcn_ne001
    specific_curve = hcn_curves[0]
    curve_name = "4043/hcn_ne001"

    # 查找匹配的曲线段
    print("Processing...")
    top_matches = find_top_matches(sketch_curve, specific_curve, window_length, polyorder)
    if len(top_matches) == 0:
        print("No matched segments found.")
    else:
        print(f"Number of matched segments: {len(top_matches)}")

    # 创建两个子图
    fig, axs = plt.subplots(2, 1, figsize=(10, 12))

    # 绘制手绘曲线
    paths = []
    for obj in sketch_json['objects']:
        if obj['type'] == 'path':
            paths.append(obj['path'])

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
        axs[0].plot(x, y, marker='o', label='Hand-drawn Curve')
    axs[0].set_title('Hand-drawn Curve')
    axs[0].set_xlabel('X')
    axs[0].set_ylabel('Y')
    axs[0].grid(True)
    axs[0].legend()

    # 绘制匹配的曲线段，只高亮匹配度最高的段
    axs[1].plot(time_data, specific_curve, alpha=0.5, label='Specific Hcn Curve')
    if len(top_matches) > 0:
        best_match = top_matches[0]
        _, start, end = best_match
        axs[1].plot(time_data[start:end], specific_curve[start:end], linewidth=2, color='blue', label=f'Best Matched Segment (Dist: {best_match[0]:.2f})')
    axs[1].set_title('Matched Segments in Specific Hcn Curve')
    axs[1].set_xlabel('Time')
    axs[1].set_ylabel('Value')
    axs[1].grid(True)

    # 移动图例到右侧
    handles, labels = axs[1].get_legend_handles_labels()
    axs[1].legend(handles, labels, loc='center left', bbox_to_anchor=(1, 0.5))

    plt.tight_layout()
    plt.show()

    # 返回匹配的曲线段数据点，只返回匹配度最高的段
    matched_segments = [
        {
            "distance": best_match[0],
            "segment": specific_curve[best_match[1]:best_match[2]].tolist(),
            "start": best_match[1],
            "end": best_match[2],
            "curve_name": curve_name
        }
    ]
    return matched_segments

if __name__ == "__main__":
    matched_segments = main()
    print(f"Matched Segments: {json.dumps(matched_segments, indent=2)}")
