import cv2
import numpy as np
import requests
import torch
from flask import Flask, render_template, jsonify
from flask_socketio import SocketIO, emit
from io import BytesIO
from PIL import Image

# Initialize Flask and Flask-SocketIO
app = Flask(__name__)
socketio = SocketIO(app)

# Load YOLOv5 model using PyTorch (YOLOv5 is available via torch hub)
device = 'cuda' if torch.cuda.is_available() else 'cpu'
model = torch.hub.load('ultralytics/yolov5', 'yolov5n', device=device)
if device == 'cuda':
    model.half()

# URL to fetch live feed (e.g., a video stream or an image from the camera)
LIVE_FEED_URL = 'http://192.168.142.181:5000/video_feed'  # Update this URL to match the source of the feed

def access_live_feed(url):
    # Send GET request to the server
    with requests.get(url, stream=True) as response:
        if response.status_code == 200:
            bytes_data = b""
            for chunk in response.iter_content(chunk_size=1024):
                bytes_data += chunk

                # Look for the JPEG header and footer
                a = bytes_data.find(b'\xff\xd8')  # JPEG start
                b = bytes_data.find(b'\xff\xd9')  # JPEG end

                if a != -1 and b != -1:
                    jpg_data = bytes_data[a:b+2]
                    bytes_data = bytes_data[b+2:]

                    # Convert JPEG to Image
                    image = Image.open(BytesIO(jpg_data))

                    # Convert Image to numpy array (OpenCV format)
                    frame = np.array(image)
                    frame = frame[:, :, ::-1]  # Convert RGB to BGR (OpenCV format)

                    # Perform YOLOv5 Object Detection
                    results = model(frame)

                    # Render results (bounding boxes, class names, etc.)
                    results.render()  # This will add boxes on the frame
                    frame_with_boxes = results.imgs[0]

                    # Convert the frame back to an image format and send to front-end
                    _, img_encoded = cv2.imencode('.jpg', frame_with_boxes)
                    img_bytes = img_encoded.tobytes()

                    # Emit the frame to front-end (via SocketIO)
                    socketio.emit('live_feed', {'image': img_bytes})
        else:
            print(f"Failed to connect to live feed. Status Code: {response.status_code}")


# Front-end route to render the video stream
@app.route('/')
def index():
    return render_template('index.html')  # Assuming you have an index.html file to display the video

# SocketIO event to handle the live video stream
@socketio.on('connect')
def handle_connect():
    print("Client connected to live feed!")
    access_live_feed(LIVE_FEED_URL)


if __name__ == '__main__':
    socketio.run(app, host='0.0.0.0', port=5000)
