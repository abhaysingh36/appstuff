# import cv2
# import threading
# from flask import Flask, Response

# app = Flask(__name__)
# video_capture = cv2.VideoCapture(0)






# def generate_frames():
#     while True:
#         success, frame = video_capture.read()
#         if not success:
#             break
#         else:
#             _, buffer = cv2.imencode('.jpg', frame)
#             yield (b'--frame\r\n'
#                    b'Content-Type: image/jpeg\r\n\r\n' + buffer.tobytes() + b'\r\n')

# @app.route('/video_feed')
# def video_feed():
#     return Response(generate_frames(), mimetype='multipart/x-mixed-replace; boundary=frame')

# def run_server():
#     app.run(host='0.0.0.0', port=5000, debug=False, threaded=True)

# if __name__ == '__main__':
#     threading.Thread(target=run_server).start()



import cv2
import torch
import threading
import numpy as np
from flask import Flask, Response

app = Flask(__name__)
video_capture = cv2.VideoCapture(0)

# Load YOLOv5 Nano model
model = torch.hub.load('ultralytics/yolov5', 'yolov5n', pretrained=True)

def generate_frames():
    while True:
        success, frame = video_capture.read()
        if not success:
            break

        # Convert frame to RGB (YOLOv5 requires RGB images)
        img = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

        # YOLOv5 inference
        results = model(img)

        # Draw bounding boxes and labels
        for det in results.xyxy[0]:  # detections per frame
            x1, y1, x2, y2, conf, cls = map(int, det[:6])
            label = f"{model.names[cls]} {conf:.2f}"
            cv2.rectangle(frame, (x1, y1), (x2, y2), (255, 0, 0), 2)
            cv2.putText(frame, label, (x1, y1 - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 0, 0), 2)

        # Encode frame as JPEG
        _, buffer = cv2.imencode('.jpg', frame)
        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + buffer.tobytes() + b'\r\n')

@app.route('/video_feed')
def video_feed():
    return Response(generate_frames(), mimetype='multipart/x-mixed-replace; boundary=frame')

def run_server():
    app.run(host='0.0.0.0', port=5000, debug=False, threaded=True)

if __name__ == '__main__':
    threading.Thread(target=run_server).start()
