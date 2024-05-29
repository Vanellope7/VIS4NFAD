import scipy.io
import numpy as np
import json

# Load data from MATLAB file
mat_data = scipy.io.loadmat("hcnData.mat")

# Convert NaN values to null in the 'hcn' data
hcn_data = mat_data['hcn']
hcn_data = np.where(np.isnan(hcn_data), None, hcn_data)

# Convert NaN values to null in the 'time' data
time_data = mat_data['time']
time_data = np.where(np.isnan(time_data), None, time_data)

# Function to expand the data 100 times
def expand_data(data):
    return np.tile(data, (100, 1))  # Repeat data 100 times along the first axis

# Expand the data
hcn_data_expanded = expand_data(hcn_data)
time_data_expanded = expand_data(time_data)

# Convert the data to a Python dictionary
data_dict = {
    'hcn': hcn_data_expanded.tolist(),  # Convert to nested lists
    'time': time_data_expanded.tolist()  # Convert time data to nested lists
}

# Convert the dictionary to JSON format
json_data = json.dumps(data_dict)

# Save JSON data to a file
with open("hcnData100.json", "w") as json_file:
    json_file.write(json_data)
