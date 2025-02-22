from flask import Flask, Response
import cv2

app = Flask(__name__)

# Initialize the Raspberry Pi camera
camera = cv2.VideoCapture(0)  # 0 is the default camera index

if not camera.isOpened():
    print("Failed to open the camera.")
    exit(1)

def generate_frames():
    """Generator function to yield video frames for streaming."""
    while True:
        success, frame = camera.read()
        if not success:
            break

        # Encode the frame in JPEG format
        ret, buffer = cv2.imencode('.jpg', frame)
        if not ret:
            continue

        # Yield the frame as a byte stream
        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + buffer.tobytes() + b'\r\n')

@app.route('/video_feed')
def video_feed():
    """Route to stream the video feed."""
    return Response(generate_frames(), mimetype='multipart/x-mixed-replace; boundary=frame')

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)  