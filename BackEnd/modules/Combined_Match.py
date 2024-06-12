import numpy as np
import json
from scipy.signal import savgol_filter
from sklearn.metrics.pairwise import cosine_similarity
from tqdm import tqdm
from joblib import Parallel, delayed

def run_similarity_analysis(drawing_file_path, smoothed_data_file_path, output_file, smoothness_value):
    # Load JSON data
    with open(drawing_file_path, 'r') as drawing_file:
        drawing_data = json.load(drawing_file)

    with open(smoothed_data_file_path, 'r') as smoothed_data_file:
        smoothed_data = json.load(smoothed_data_file)

    # Extract and preprocess path information
    path_data = drawing_data[0]["path"]
    drawing_x_coords = [command[1] for command in path_data if len(command) > 2]
    drawing_y_coords = [command[2] for command in path_data if len(command) > 2]

    # Vertically flip y-coordinates
    drawing_y_coords = np.max(drawing_y_coords) - np.array(drawing_y_coords)

    # Horizontally stretch the hand-drawn curve to reduce its slope
    stretch_factor = 1.5  # Adjust this factor to achieve the desired slope reduction
    drawing_x_coords = np.array(drawing_x_coords) * stretch_factor

    # Smooth the hand-drawn data
    drawing_y_smooth = savgol_filter(drawing_y_coords, 11, 3)
    drawing_x_smooth = savgol_filter(drawing_x_coords, 11, 3)

    # Calculate trend and slope of the smoothed hand-drawn data
    drawing_trend = np.sign(np.diff(drawing_y_smooth))
    drawing_slope = (drawing_y_smooth[-1] - drawing_y_smooth[0]) / (drawing_x_smooth[-1] - drawing_x_smooth[0])

    # Extract trends and slopes of the measured data
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

    # Calculate maximum Euclidean distance
    max_euclidean_distance = np.max([np.linalg.norm(drawing_trend - segment[2]) for segment in all_segments])

    # Define a function to calculate similarities
    def calculate_similarities(segment, max_dist, draw_slope):
        cosine_sim = cosine_similarity([drawing_trend], [segment[2]])[0][0]
        euclidean_dist = np.linalg.norm(drawing_trend - segment[2])
        normalized_euclidean_dist = 1 - euclidean_dist / max_dist
        slope_similarity = 1 - np.abs(draw_slope - segment[4]) / max(np.abs(draw_slope), np.abs(segment[4]))
        combined_similarity = (cosine_sim + normalized_euclidean_dist + slope_similarity) / 3
        return segment[0], segment[1], combined_similarity, segment[3], segment, segment[5], cosine_sim, euclidean_dist, slope_similarity

    # Filter initial segments
    initial_filtered_segments = [seg for seg in all_segments if np.sum(np.abs(seg[2] - drawing_trend)) / len(drawing_trend) < 1.5]

    # Parallel computation of similarities
    total_segments = len(initial_filtered_segments)
    results = []
    for i, res in enumerate(Parallel(n_jobs=-1)(delayed(calculate_similarities)(seg, max_euclidean_distance, drawing_slope) for seg in tqdm(initial_filtered_segments, desc="Calculating similarities"))):
        results.append(res)
        yield int((i + 1) / total_segments * 100)  # Yield progress

    # Filter segments based on similarity threshold
    similarity_threshold = 0.85
    filtered_results = [res for res in results if res[2] >= similarity_threshold]

    # If no segments meet the threshold, select the top 10 highest similarity segments
    if not filtered_results:
        filtered_results = sorted(results, key=lambda x: x[2], reverse=True)[:10]

    # Filter highly overlapping segments
    final_results = []
    used_indices = set()

    for res in tqdm(filtered_results, desc="Filtering results"):
        name, index, similarity, segment_values, segment, time_values, cosine_sim, euclidean_dist, slope_similarity = res
        if all(abs(index - used_index) > len(drawing_trend) for used_index in used_indices):
            final_results.append(res)
            used_indices.add(index)

    # Collect detailed information of matched segments
    matched_segments_info = []
    for res in final_results:
        name, index, combined_similarity, segment_values, segment, time_values, cosine_sim, euclidean_dist, slope_similarity = res
        segment_info = {
            "Hcn": name,
            "StartIndex": index,
            "CombinedSimilarity": combined_similarity,
            "CosineSimilarity": cosine_sim,
            "EuclideanDistance": euclidean_dist,
            "SlopeSimilarity": slope_similarity,
            "TimeValues": time_values,
            "MeasurementValues": segment_values,
            "Trend": segment[2].tolist(),
            "Slope": segment[4],
            "Smooth": smoothness_value
        }
        matched_segments_info.append(segment_info)

    # Save matched segment information to a JSON file
    with open(output_file, 'w') as json_file:
        json.dump(matched_segments_info, json_file, indent=4)

    print(f"Matched segments information saved to {output_file}")
