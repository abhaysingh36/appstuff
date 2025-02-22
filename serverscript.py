from flask import Flask, request, jsonify, Response
import cv2

app = Flask(__name__)

# Initialize the video capture for the webcam (fallback option)
cap_webcam = cv2.VideoCapture(0)  # Use the webcam

# Replace with your phone's video feed URL
phone_ip = "192.168.199.252"
video_url = f"http://{phone_ip}:4747/video"  # Example URL for IP Webcam (Android app)
cap_phone = cv2.VideoCapture(video_url)  # Try to use the phone's video feed

# Choose which feed to use based on availability
cap = None
if cap_phone.isOpened():
    cap = cap_phone  # If the phone feed is available, use it
else:
    cap = cap_webcam  # Else, use the webcam

# Endpoint to receive commands from the PyQt app
@app.route('/send-command', methods=['POST'])
def send_command():
    data = request.json
    command = data.get("command")
    params = data.get("params", {})
    print(f"Received command: {command} with params: {params}")
    return jsonify({"status": "success", "message": "Command received"})

# Endpoint to receive telemetry or status updates
@app.route('/telemetry', methods=['POST'])
def telemetry():
    data = request.json
    print(f"Telemetry data received: {data}")
    return jsonify({"status": "success", "message": "Telemetry received"})

# Video streaming route
@app.route('/video_feed')
def video_feed():
    """Video streaming route."""
    return Response(generate_frames(), mimetype='multipart/x-mixed-replace; boundary=frame')

def generate_frames():
    """Generator function to yield video frames for streaming."""
    while True:
        success, frame = cap.read()  # Capture a frame from the selected feed (phone or webcam)
        if not success:
            break
        else:
            # Encode the frame as JPEG
            ret, buffer = cv2.imencode('.jpg', frame)
            if not ret:
                continue

            # Convert the encoded frame to bytes
            frame_bytes = buffer.tobytes()

            # Yield the frame bytes with the proper format for HTTP streaming
            yield (b'--frame\r\n'
                   b'Content-Type: image/jpeg\r\n\r\n' + frame_bytes + b'\r\n')

# Endpoint to retrieve a single frame for additional processing
@app.route('/get_frame', methods=['GET'])
def get_frame():
    """Fetch a single frame for additional processing."""
    success, frame = cap.read()
    if success:
        _, buffer = cv2.imencode('.jpg', frame)
        response = Response(buffer.tobytes(), content_type='image/jpeg')
        return response
    else:
        return jsonify({"status": "error", "message": "Unable to capture frame"}), 500

if __name__ == '__main__':
    try:
        app.run(host='0.0.0.0', port=5000)
    finally:
        if cap:
            cap.release()  # Release the video capture object when exiting
