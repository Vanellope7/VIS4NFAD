import json
import numpy as np
from scipy.spatial.distance import euclidean
from fastdtw import fastdtw
import heapq
from tqdm import tqdm

# 读取drawing.json文件
with open('../static/Data/drawing.json', 'r') as file:
    drawing_data = json.load(file)

# 读取hcnData.json文件
with open('../static/Data/hcnData.json', 'r') as file:
    hcn_data = json.load(file)

# 提取手绘数据路径
drawing_coords = []
for obj in drawing_data['objects']:
    if obj['type'] == 'path':
        for command in obj['path']:
            if command[0] in ['M', 'L', 'Q']:
                drawing_coords.append((command[1], command[2]))

drawing_coords = np.array(drawing_coords)

# 提取hcn数据，并确保数据为数值类型
def flatten_and_filter(data):
    flat_data = []
    for item in data:
        if isinstance(item, list):
            flat_data.extend(flatten_and_filter(item))
        elif isinstance(item, (int, float)):
            flat_data.append(float(item))
    return flat_data

hcn_coords = flatten_and_filter(hcn_data['hcn'])
hcn_coords = np.array(hcn_coords)

# 归一化函数
def normalize(data):
    data = np.array(data)
    data_min = np.min(data, axis=0)
    data_max = np.max(data, axis=0)
    return (data - data_min) / (data_max - data_min)

# 归一化手绘数据和hcn数据
drawing_coords = normalize(drawing_coords)
hcn_coords = normalize(hcn_coords)

# 计算相似度的函数，使用DTW算法
def calculate_similarity(seq1, seq2):
    distance, _ = fastdtw(seq1, seq2, dist=euclidean)
    return distance

# 找到前20个最匹配的段落
def find_top_matches(drawing_coords, hcn_coords, window_size=100, top_n=20):
    top_matches = []
    total_segments = len(hcn_coords) - window_size + 1

    for i in tqdm(range(total_segments), desc="Processing segments"):
        segment = hcn_coords[i:i + window_size]
        segment_coords = np.array([(x, y) for x, y in enumerate(segment)])

        distance = calculate_similarity(drawing_coords, segment_coords)

        if len(top_matches) < top_n:
            heapq.heappush(top_matches, (-distance, segment))
        else:
            heapq.heappushpop(top_matches, (-distance, segment))

    # 转换回正距离排序
    top_matches = [(-dist, seg) for dist, seg in top_matches]
    top_matches.sort()

    return top_matches

# 找到前20个最匹配的段落
top_matches = find_top_matches(drawing_coords, hcn_coords)

# 打印前20名匹配的段落及其距离
for i, (distance, match) in enumerate(top_matches):
    print(f"匹配段落 {i + 1}:")
    print("距离:", distance)
    print("段落数据:", match)
    print("\n")
