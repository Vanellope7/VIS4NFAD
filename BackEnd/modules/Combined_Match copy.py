# similarity_analysis.py
import numpy as np
import json
import matplotlib.pyplot as plt
from scipy.signal import savgol_filter
from sklearn.metrics.pairwise import cosine_similarity
from tqdm import tqdm
from joblib import Parallel, delayed
import mplcursors

def run_similarity_analysis(drawing_file_path, smoothed_data_file_path, output_file):
    # 加载JSON数据
    with open(drawing_file_path, 'r') as drawing_file:
        drawing_data = json.load(drawing_file)

    with open(smoothed_data_file_path, 'r') as smoothed_data_file:
        smoothed_data = json.load(smoothed_data_file)

    # 提取并预处理路径信息
    path_data = drawing_data[0]["path"]
    drawing_x_coords = [command[1] for command in path_data if len(command) > 2]
    drawing_y_coords = [command[2] for command in path_data if len(command) > 2]

    # 垂直翻转y坐标
    drawing_y_coords = np.max(drawing_y_coords) - np.array(drawing_y_coords)

    # 水平拉伸手绘曲线以减少其斜率
    stretch_factor = 1.5  # 调整此系数以实现所需的斜率减小
    drawing_x_coords = np.array(drawing_x_coords) * stretch_factor

    # 平滑手绘数据
    drawing_y_smooth = savgol_filter(drawing_y_coords, 11, 3)
    drawing_x_smooth = savgol_filter(drawing_x_coords, 11, 3)

    # 计算平滑手绘数据的趋势和斜率
    drawing_trend = np.sign(np.diff(drawing_y_smooth))
    drawing_slope = (drawing_y_smooth[-1] - drawing_y_smooth[0]) / (drawing_x_smooth[-1] - drawing_x_smooth[0])

    # 提取测量数据的趋势和斜率
    all_segments = []
    for curve in smoothed_data:
        values = [point['y'] for point in curve['data']]
        trend = np.sign(np.diff(values))
        for i in range(len(trend) - len(drawing_trend) + 1):
            segment_trend = trend[i:i + len(drawing_trend)]
            segment_values = values[i:i + len(drawing_trend) + 1]
            segment_slope = (segment_values[-1] - segment_values[0]) / (len(segment_values) - 1)
            time_values = [point['x'][0] for point in curve['data'][i:i + len(drawing_trend) + 1]]
            all_segments.append((curve['name'], i, segment_trend, segment_values, segment_slope, time_values))

    # 计算最大欧氏距离
    max_euclidean_distance = np.max([np.linalg.norm(drawing_trend - segment[2]) for segment in all_segments])

    # 定义计算相似度的函数
    def calculate_similarities(segment, max_dist, draw_slope):
        cosine_sim = cosine_similarity([drawing_trend], [segment[2]])[0][0]
        euclidean_dist = np.linalg.norm(drawing_trend - segment[2])
        normalized_euclidean_dist = 1 - euclidean_dist / max_dist
        slope_similarity = 1 - np.abs(draw_slope - segment[4]) / max(np.abs(draw_slope), np.abs(segment[4]))
        combined_similarity = (cosine_sim + normalized_euclidean_dist + slope_similarity) / 3
        return segment[0], segment[1], combined_similarity, segment[3], segment, segment[5], cosine_sim, euclidean_dist, slope_similarity

    # 初步过滤段
    initial_filtered_segments = [seg for seg in all_segments if np.sum(np.abs(seg[2] - drawing_trend)) / len(drawing_trend) < 1.5]

    # 并行计算相似度
    results = Parallel(n_jobs=-1)(delayed(calculate_similarities)(seg, max_euclidean_distance, drawing_slope) for seg in tqdm(initial_filtered_segments, desc="Calculating similarities"))

    # 根据相似度阈值过滤段
    similarity_threshold = 0.85
    filtered_results = [res for res in results if res[2] >= similarity_threshold]

    # 如果没有段达到阈值，则选择前10个最高相似度的段
    if not filtered_results:
        filtered_results = sorted(results, key=lambda x: x[2], reverse=True)[:10]

    # 过滤高度重叠的段
    final_results = []
    used_indices = set()

    for res in tqdm(filtered_results, desc="Filtering results"):
        name, index, similarity, segment_values, segment, time_values, cosine_sim, euclidean_dist, slope_similarity = res
        if all(abs(index - used_index) > len(drawing_trend) for used_index in used_indices):
            final_results.append(res)
            used_indices.add(index)

    # 收集匹配段的详细信息
    matched_segments_info = []
    for res in final_results:
        name, index, combined_similarity, segment_values, segment, time_values, cosine_sim, euclidean_dist, slope_similarity = res
        segment_info = {
            "Curve": name,
            "Start Index": index,
            "Combined Similarity": combined_similarity,
            "Cosine Similarity": cosine_sim,
            "Euclidean Distance": euclidean_dist,
            "Slope Similarity": slope_similarity,
            "Time Values": time_values,
            "Measurement Values": segment_values,
            "Trend": segment[2].tolist(),
            "Slope": segment[4]
        }
        matched_segments_info.append(segment_info)

    # 将匹配段信息保存到JSON文件
    with open(output_file, 'w') as json_file:
        json.dump(matched_segments_info, json_file, indent=4)

    print(f"Matched segments information saved to {output_file}")

    # 可视化所有曲线并突出显示匹配段
    fig, ax = plt.subplots(figsize=(20, 8))

    # 绘制所有原始曲线
    for curve in smoothed_data:
        time_values = [point['x'][0] for point in curve['data']]
        values = [point['y'] for point in curve['data']]
        ax.plot(time_values, values, color='lightgray')

    # 红色突出显示匹配段
    highlight_color = 'red'
    lines = []
    for i, (name, index, combined_similarity, segment_values, segment, time_values, cosine_sim, euclidean_dist, slope_similarity) in enumerate(final_results):
        line, = ax.plot(time_values, segment_values, label=f"Segment {i+1} (Similarity: {combined_similarity:.2f})", linewidth=2.5, color=highlight_color)
        lines.append(line)

    # 添加悬停功能以显示相似度
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





