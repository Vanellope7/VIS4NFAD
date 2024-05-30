import json

import numpy as np
import pandas as pd
from scipy.stats import zscore
from statsmodels.tsa.stattools import adfuller
from statsmodels.tsa.ar_model import AutoReg
import matplotlib.pyplot as plt
from sklearn.linear_model import LinearRegression

# 1. 异常值检测
def detect_outliers(data, threshold=3):
    z_scores = zscore(data)
    outliers = np.abs(z_scores) > threshold
    return np.where(outliers)[0]


# 2. 趋势检测
def detect_trend(x, data):
    x = np.array(x).reshape(-1, 1)
    model = LinearRegression()
    model.fit(x, data)
    trend = model.predict(x)
    slope = model.coef_[0]
    intercept = model.intercept_
    if len(trend) == 1:
        return 'None'
    return trend[1] > trend[0], slope, intercept



# 3. 平稳性检测
def check_stationarity(data):
    result = adfuller(data)
    return result[1] <= 0.05


# 4. 波动性检测
def detect_volatility(data, window_size=5):
    rolling_std = data.rolling(window=window_size).std()
    return rolling_std


class JsonEncoder(json.JSONEncoder):
    """Convert numpy classes to JSON serializable objects."""

    def default(self, obj):
        if isinstance(obj, (np.integer, np.floating, np.bool_)):
            return obj.item()
        elif isinstance(obj, np.ndarray):
            return obj.tolist()
        else:
            return super(JsonEncoder, self).default(obj)
