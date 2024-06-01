import os
import json
from flask import Flask, request, jsonify
from flask_cors import CORS
from flask_socketio import SocketIO

app = Flask(__name__)
CORS(app, resources={r"/*": {"origins": "*"}})
socketio = SocketIO(app, cors_allowed_origins="*")  # 允许跨域

table_data_path = 'modules/static/Data/tableData.json'  # 使用你保存 table_data.json 文件的实际路径

# Ensure the static/Data directory exists
data_folder = os.path.join(app.static_folder, 'Data')
if not os.path.exists(data_folder):
    os.makedirs(data_folder)


@app.route('/')
def hello_world():
    return 'Hello World!'


@app.route('/submit', methods=['POST'])
def submit_drawing():
    try:
        data = request.get_json()
        print("Received data:", data)  # Log the received data
        if not data:
            return jsonify({"error": "No data received"}), 400

        drawing = data.get('drawing')
        print("Drawing data:", drawing)  # Log the drawing data
        if not drawing:
            return jsonify({"error": "No drawing data provided"}), 400

        filename = os.path.join(data_folder, f'drawing.json')

        # Save drawing data to file
        with open(filename, 'w') as f:
            json.dump(drawing, f)
        print(f'Received drawing saved to {filename}')

        return jsonify({"message": f"Drawing received and saved to {filename}"}), 200
    except Exception as e:
        # Log detailed error information
        import traceback
        print("Exception occurred:")
        print(traceback.format_exc())
        return jsonify({"error": "Failed to process the drawing", "details": str(e)}), 500


@app.route('/get_table_data', methods=['GET'])
def get_table_data():
    try:
        with open(table_data_path, 'r') as f:
            table_data = json.load(f)
        return jsonify(table_data)
    except Exception as e:
        return jsonify({"error": "Failed to load table data", "details": str(e)}), 500


if __name__ == '__main__':
    socketio.run(app, host='0.0.0.0', port=5000, debug=True)
