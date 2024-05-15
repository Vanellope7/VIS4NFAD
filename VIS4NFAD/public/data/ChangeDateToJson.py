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

# Convert the data to a Python dictionary
data_dict = {
    'hcn': hcn_data.tolist(),  # Convert to nested lists
    'time': time_data.tolist()  # Convert time data to nested lists
}

# Convert the dictionary to JSON format
json_data = json.dumps(data_dict)

# Save JSON data to a file
with open("hcnData.json", "w") as json_file:
    json_file.write(json_data)
