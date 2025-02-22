# import socket
# import cv2
# import torch
# import numpy as np
# import threading


# # Constants
# HOST = '0.0.0.0'
# PORT = 5000

# # Load YOLO model (YOLOv5 example)
# device = 'cuda' if torch.cuda.is_available() else 'cpu'
# model = torch.hub.load('ultralytics/yolov5', 'yolov5n', device=device)

# if device == 'cuda':
#     model.half()


# def start_server():
#     socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)



from flask import Flask, request, send_file, jsonify
import requests
from io import BytesIO

app = Flask(_name_)

# Target server URL
TARGET_SERVER_URL = "http://target-server-ip:port"

@app.route('/images/fetch', methods=['GET'])
def fetch_image():
    try:
        # Get the image path from query parameters
        image_path = request.args.get('imagePath')
        if not image_path:
            return jsonify({"error": "Missing 'imagePath' parameter"}), 400

        # Construct the target URL
        target_url = f"{TARGET_SERVER_URL}/{image_path}"

        # Fetch the image from the target server
        response = requests.get(target_url, stream=True)
        if response.status_code != 200:
            return jsonify({"error": f"Failed to fetch image: {response.status_code}"}), response.status_code

        # Serve the image as a response
        return send_file(
            BytesIO(response.content),
            mimetype=response.headers.get('Content-Type', 'image/jpeg'),
            as_attachment=False,
            download_name=image_path.split("/")[-1]
        )
    except Exception as e:
        return jsonify({"error": f"Error fetching image: {str(e)}"}), 500

if _name_ == '_main_':
    app.run(host='0.0.0.0', port=8080)