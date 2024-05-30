import json
import time

import numpy as np
from scipy.signal import find_peaks, argrelextrema

from public.data.func import detect_outliers, detect_trend, check_stationarity, detect_volatility, JsonEncoder
start = time.time()

# peak-version
# peaksList = []
# statesList = []
# with open('hcnData.json') as f:
#     data = json.load(f)
#     hcn = data['hcn']
#     hcn.pop(20)
#     for d in hcn:
#         d = np.array(d)
#         d[d == None] = 0
#         maxD = d.max()
#         minD = d.min()
#         # 正负峰值如何取
#         peaks, _ = find_peaks(d, height=maxD*0.8, distance=100)
#         # 找到最小峰值，通过对数据取反来实现
#         inverted_peaks, _ = find_peaks(-d, height=-minD*0.8, distance=100)
#         peaks = np.concatenate((peaks, inverted_peaks), axis=0)
#         peaks.sort()
#         peaks = list(peaks)
#         if len(peaks) == 0 or peaks[0] != 0:
#             peaks = [0] + peaks
#         if peaks[-1] != len(d)-1:
#             peaks.append(len(d)-1)
#         peaksList.append(peaks)
#         states = []
#         for i in range(len(peaks)):
#             if i == 0:
#                 continue
#             outliers = detect_outliers(d[peaks[i-1]:peaks[i]])
#             outliers = list(map(lambda t: t+peaks[i-1], outliers))
#             trend = detect_trend(d[peaks[i-1]:peaks[i]])
#             # stationarity = check_stationarity(d[peaks[i-1]:peaks[i]])
#
#             states.append({
#                 'outliers': outliers,
#                 'trend': trend,
#                 # 'stationarity': stationarity
#             })
#         statesList.append(states)
#
# with open('hcnStateData.json', 'w') as f:
#     f.write(json.dumps({
#         'peaksList': peaksList,
#         'statesList': statesList
#     }, cls=JsonEncoder))
#
# end = time.time()
# print(end - start)


# avg version
def my_find_peaks(d, maxD, minD):
    # 正负峰值如何取
    peaks, _ = find_peaks(d, height=maxD*0.95, distance=len(d))
    # 找到最小峰值，通过对数据取反来实现
    inverted_peaks, _ = find_peaks(-d, height=-minD*0.95, distance=len(d))
    # peaks = np.concatenate((peaks, inverted_peaks), axis=0)
    # peaks.sort()
    # peaks = list(peaks)

    return list(peaks), list(inverted_peaks)

segmentList = []
statesList = []
with open('hcnData500_500k_100.json') as f:
    data = json.load(f)
    hcn = data['hcn']
    timeList = list(map(lambda d: d[0], data['time']))
    hcn.pop(20)
    for j in range(len(hcn)):
        d = hcn[j]
        d = np.array(d)
        d[d == None] = 0
        if sum(d) == 0:
            continue
        maxD = d.max()
        minD = d.min()

        segment = list(range(0, len(d), 10))
        segment.append(len(d)-1)
        segmentList.append(segment)
        states = []
        pre_peaks, pre_inverted_peaks = [], []
        for i in range(len(segment)):
            if i == 0:
                continue
            outliers = detect_outliers(d[segment[i-1]:segment[i]])
            outliers = list(map(lambda t: t+segment[i-1], outliers))
            trend, slope, intercept = detect_trend(timeList[segment[i-1]:segment[i]], d[segment[i-1]:segment[i]])
            # stationarity = check_stationarity(d[peaks[i-1]:peaks[i]])
            peaks, inverted_peaks = my_find_peaks(d[segment[i-1]:segment[i]], maxD, minD)
            peaks = [d+segment[i-1] for d in peaks]
            inverted_peaks = [d+segment[i-1] for d in inverted_peaks]
            total = list(sorted(peaks + inverted_peaks))
            states.append({
                'outliers': outliers,
                'trend': [trend, slope, intercept],
                'peaks': [] if len(pre_peaks) > 0 and len(peaks) > 0 or
                               len(pre_inverted_peaks) > 0 and len(inverted_peaks) > 0 else total
                # 'stationarity': stationarity
            })
            pre_peaks, pre_inverted_peaks = peaks, inverted_peaks
        statesList.append(states)

# with open('hcnStateDataAvg.json', 'w') as f:
#     f.write(json.dumps({
#         'segmentList': segmentList,
#         'statesList': statesList
#     }, cls=JsonEncoder))

end = time.time()
print(end - start)