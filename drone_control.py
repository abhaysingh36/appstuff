import time
import cv2
import numpy as np
from pymavlink import mavutil
from ultralytics import YOLO

import torch

# Initialize MAVLink connection (replace with your drone's connection string)
connection_string = 'udpin:localhost:14550'  # Example for UDP connection
master = mavutil.mavlink_connection(connection_string)

# Load YOLOv5 Nano Model (using YOLOv5's official repo for Nano or your custom model)
# model = YOLO('yolov5n.pt', device='cuda' if torch.cuda.is_available() else 'cpu')
model = YOLO('yolov5n.pt')
device = 'cuda' if torch.cuda.is_available() else 'cpu'
def check_drone_connection():
    # Implement your connection logic here
    # For example, check if the Pixhawk or drone system is connected via serial or a specific interface.
    # This could involve checking if the drone responds to a "ping" or if its status can be queried.
    # You can return True if connected, otherwise False.
    return True  # Replace this with actual connection check
# Function to arm the drone
def arm_drone():
    print("Arming drone...")
    master.mav.command_long_send(
        master.target_system, master.target_component,
        mavutil.mavlink.MAV_CMD_COMPONENT_ARM_DISARM, 0,
        1, 0, 0, 0, 0, 0, 0
    )
    time.sleep(1)

# Function to take off
def take_off():
    print("Taking off...")
    master.mav.command_long_send(
        master.target_system, master.target_component,
        mavutil.mavlink.MAV_CMD_NAV_TAKEOFF, 0,
        0, 0, 0, 0, 0, 0, 10  # Altitude 10 meters
    )
    time.sleep(5)
    print("Drone has taken off.")

# Function to land
def land():
    print("Landing...")
    master.mav.command_long_send(
        master.target_system, master.target_component,
        mavutil.mavlink.MAV_CMD_NAV_LAND, 0,
        0, 0, 0, 0, 0, 0, 0
    )
    time.sleep(5)
    print("Drone has landed.")

# Function to move the drone to a specific location (lat, lon, alt)
def move_to_location(latitude, longitude, altitude):
    print(f"Moving to location: Lat {latitude}, Long {longitude}, Alt {altitude} meters")
    master.mav.set_position_target_global_int_send(
        0, 0, 0, mavutil.mavlink.MAV_FRAME_GLOBAL_RELATIVE_ALT,
        0b110111111000, latitude, longitude, altitude, 0, 0, 0, 0, 0, 0, 0
    )
    time.sleep(5)

# Function to activate the pesticide spraying system
def spray_pesticide():
    print("Activating pesticide spraying system...")
    # Control a spray system (e.g., a servo or pump)
    master.mav.command_long_send(
        master.target_system, master.target_component,
        mavutil.mavlink.MAV_CMD_DO_SET_SERVO, 0,
        1, 2000, 0, 0, 0, 0, 0  # Replace with actual servo/pump control
    )
    time.sleep(2)

# Function for image preprocessing (not necessary for YOLOv5, but included for completeness)
def preprocess_image(image, target_size):
    image = cv2.resize(image, target_size)
    image = image.astype('float32')
    image /= 255.0  # Normalize pixel values to [0, 1]
    image = np.expand_dims(image, axis=0)
    return image

# Real-time detection and control
def real_time_detection():
    arm_drone()
    take_off()

    # Initialize the camera
    camera = cv2.VideoCapture(0)

    while True:
        ret, frame = camera.read()
        
        # Run YOLOv5 Nano detection
        results = model(frame)  # Pass the frame to YOLOv5 for inference

        # Accessing the results
        boxes = results[0].boxes  # Get bounding boxes
        labels = results[0].names  # Get class names (e.g., 'locust', 'disease', etc.)
        confidences = results[0].conf  # Get confidence scores

        # Check for locust or disease detection
        locust_detected = False
        disease_detected = False
        for i, (box, label, confidence) in enumerate(zip(boxes, labels, confidences)):
            if label == 'locust' and confidence > 0.95:  # Adjust confidence threshold
                locust_detected = True
            elif label == 'disease' and confidence > 0.95:  # Adjust confidence threshold
                disease_detected = True
        
        # Take action if both locusts and disease are detected
        if locust_detected and disease_detected:
            print("Locusts and disease detected, moving to target location and spraying pesticide...")
            move_to_location(42.0, -71.0, 10.0)  # Replace with your target location
            spray_pesticide()

        # Display the frame with detection results
        results.render()  # Draw the results on the frame
        cv2.imshow('Real-time Detection', frame)

        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    camera.release()
    cv2.destroyAllWindows()
    land()


if __name__ == "__main__":
    real_time_detection()
