import os
import json
from flask import Flask, request, jsonify
from flask_cors import CORS
from flask_socketio import SocketIO

app = Flask(__name__)
CORS(app, resources={r"/*": {"origins": "*"}})
socketio = SocketIO(app, cors_allowed_origins="*")  # 允许跨域

# 确保 static/Data 文件夹存在
data_folder = os.path.join(app.static_folder, 'Data')
if not os.path.exists(data_folder):
    os.makedirs(data_folder)

@app.route('/')
def hello_world():
    return 'Hello World!'

@app.route('/submit', methods=['POST'])
def submit_drawing():
    data = request.get_json()
    drawing = data.get('drawing')
    if not drawing:
        return jsonify({"error": "No drawing data provided"}), 400

    # 文件名可以使用当前时间戳或者其他唯一标识符
    filename = os.path.join(data_folder, 'drawing.json')

    try:
        # 将绘制数据保存到文件中
        with open(filename, 'w') as f:
            json.dump(drawing, f)
        print(f'Received drawing saved to {filename}')
    except Exception as e:
        print(f'Error saving drawing: {e}')
        return jsonify({"error": "Failed to save drawing"}), 500

    return jsonify({"message": f"Drawing received and saved to {filename}"}), 200

if __name__ == '__main__':
    socketio.run(app, host='0.0.0.0', port=5000, debug=True)
