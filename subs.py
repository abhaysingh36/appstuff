import cv2
import requests
import pickle
import struct

# Open the video capture (camera)
cap = cv2.VideoCapture(0)

# Flask server URL
server_url = 'http://SERVER_IP:5000/video_feed'

while True:
    ret, frame = cap.read()
    if not ret:
        break

    # Convert the frame to JPEG format
    encode_param = [int(cv2.IMWRITE_JPEG_QUALITY), 90]
    _, img_encoded = cv2.imencode('.jpg', frame, encode_param)

    # Send the frame to the Flask server
    try:
        # Send the frame as a POST request
        response = requests.post(server_url, data=img_encoded.tobytes())
    except Exception as e:
        print(f"Error sending frame: {e}")
    
    # Optionally display the live feed locally
    cv2.imshow("Live Feed", frame)
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()