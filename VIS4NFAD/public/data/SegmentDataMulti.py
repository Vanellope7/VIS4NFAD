import json
import time

import numpy as np
from concurrent.futures import ProcessPoolExecutor

from public.data.func import detect_outliers, detect_trend


def my_find_peaks(d, maxD, minD):
    from scipy.signal import find_peaks

    # 正负峰值如何取
    peaks, _ = find_peaks(d, height=maxD * 0.95, distance=len(d))
    # 找到最小峰值，通过对数据取反来实现
    inverted_peaks, _ = find_peaks(-d, height=-minD * 0.95, distance=len(d))

    return list(peaks), list(inverted_peaks)



def process_segment(j, hcn, timeList):
    d = hcn[j]
    d = np.array(d, dtype=float)
    d[np.isnan(d)] = 0
    if sum(d) == 0:
        return None

    maxD = d.max()
    minD = d.min()

    segment = list(range(0, len(d), 10))
    segment.append(len(d) - 1)
    states = []
    pre_peaks, pre_inverted_peaks = [], []
    for i in range(len(segment)):
        if i == 0:
            continue
        # outliers = detect_outliers(d[segment[i - 1]:segment[i]])
        # outliers = list(map(lambda t: t + segment[i - 1], outliers))
        trend, slope, intercept = detect_trend(timeList[segment[i - 1]:segment[i]], d[segment[i - 1]:segment[i]])
        # peaks, inverted_peaks = my_find_peaks(d[segment[i - 1]:segment[i]], maxD, minD)
        # peaks = [p + segment[i - 1] for p in peaks]
        # inverted_peaks = [p + segment[i - 1] for p in inverted_peaks]
        # total = list(sorted(peaks + inverted_peaks))
        states.append({
            # 'outliers': outliers,
            'trend': [trend, slope, intercept],
            # 'peaks': [] if len(pre_peaks) > 0 and len(peaks) > 0 or
            #                len(pre_inverted_peaks) > 0 and len(inverted_peaks) > 0 else total
        })
        # pre_peaks, pre_inverted_peaks = peaks, inverted_peaks
    return states


if __name__ == '__main__':
    segmentList = []
    statesList = []
    start = time.time()
    with open('hcnData100_500k_100.json') as f:
        data = json.load(f)
        hcn = data['hcn']
        timeList = list(map(lambda d: d[0], data['time']))
        hcn.pop(20)

        with ProcessPoolExecutor() as executor:
            futures = [executor.submit(process_segment, j, hcn, timeList) for j in range(len(hcn))]
            for future in futures:
                result = future.result()
                if result is not None:
                    statesList.append(result)
    end = time.time()
    print(end - start)

    # 处理完后的结果在statesList中
