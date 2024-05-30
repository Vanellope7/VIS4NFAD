import scipy.io
import numpy as np
import json

# Load data from MATLAB file
mat_data = scipy.io.loadmat("hcnData.mat")

# Convert NaN values to null in the 'hcn' data
hcn_data = mat_data['hcn']
hcn_data = np.where(np.isnan(hcn_data), None, hcn_data).tolist()

# Convert NaN values to null in the 'time' data
time_data = mat_data['time']
time_data = np.where(np.isnan(time_data), None, time_data).tolist()

# extend data scale
size = 1000
scale = 500
nowsize = 4300
nowcate = 29
sample = 100
for i in range(1000 - nowcate):
    hcn_data.append(list(hcn_data[i%nowcate]))

for i in range(size * scale - nowsize):
    time_data.append([4.000 + i * 0.001])
    for d in hcn_data:
        d.append(d[i % size])

for i in range(len(hcn_data)):
    hcn_data[i] = hcn_data[i][::sample]
time_data = time_data[::sample]


# Convert the data to a Python dictionary
data_dict = {
    'hcn': hcn_data,  # Convert to nested lists
    'time': time_data  # Convert time data to nested lists
}

# Convert the dictionary to JSON format
json_data = json.dumps(data_dict)

data_name = '1k_500k_100'

# Save JSON data to a file
with open("hcnData{}.json".format(data_name), "w") as json_file:
    json_file.write(json_data)
