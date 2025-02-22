# import serial
# import json
# import time

# # Change this to match your Arduino's Serial port
# SERIAL_PORT = "/dev/ttyUSB0"  # Linux/macOS: /dev/ttyUSB0 or /dev/ttyACM0, Windows: COM3, COM4, etc.
# BAUD_RATE = 115200

# def send_json_to_arduino():
#     try:
#         # Open Serial Connection
#         ser = serial.Serial(SERIAL_PORT, BAUD_RATE, timeout=1)
#         time.sleep(2)  # Wait for Serial to initialize

#         # JSON Command
#         json_command = {
#             "command": {
#                 "LEFT": 0,
#                 "RIGHT": 1,
#                 "FORWARD": 1,
#                 "BACKWARD": 0,
#                 "TAKE_OFF": 1,
#                 "LAND": 0,
#                 "THROTTLE": 50
#             },
#             "GPS": [11.0000, 10.11111]
#         }

#         # Convert JSON to String and Send
#         json_string = json.dumps(json_command) + "\n"
#         ser.write(json_string.encode())  # Send to Arduino

#         print(f"Sent to Arduino: {json_string}")

#         # Optional: Read Response from Arduino
#         time.sleep(1)  # Wait for Arduino to process
#         while ser.in_waiting > 0:
#             response = ser.readline().decode().strip()
#             print(f"Arduino Response: {response}")

#         # Close Serial Connection
#         ser.close()

#     except Exception as e:
#         print(f"Error: {e}")

# # Run the function
# send_json_to_arduino()




# import serial
# import json

# data = {
#     "command": {
#         "LEFT": 0,
#         "RIGHT": 0,
#         "FORWARD": 1,
#         "BACKWARD": 0,
#         "TAKE_OFF": 0,
#         "LAND": 0,
#         "THROTTLE": 50
#     },
#     "GPS": [37.7749, -122.4194]
# }

# ser = serial.Serial('/dev/ttyUSB0', 115200)  # Change port as needed
# json_string = json.dumps(data) + "\n"
# ser.write(json_string.encode())
# ser.close()



# import serial
# import json
# import time

# # Set the serial port (adjust if needed)
# ser = serial.Serial('/dev/ttyUSB0', 9600, timeout=1)
# time.sleep(2)  # Allow time for Arduino to reset

# while True:
#   # Take user input
#     data = {
#     "command": {
#         "LEFT": 0,
#         "RIGHT": 0,
#         "FORWARD": 1,
#         "BACKWARD": 0,
#         "TAKE_OFF": 0,
#         "LAND": 0,
#         "THROTTLE": 50
#     },
#     "GPS": [37.7749, -122.4194]
# } # Create JSON structure
#     json_data = json.dumps(data) + "\n"  # Convert to JSON string

#     ser.write(json_data.encode())  # Send JSON to Arduino
#     print(f"Sent: {json_data}")

#     time.sleep(1)  # Wait before sending again





import serial
import json
import time
import os

# Function to initialize serial port
def initialize_serial(port):
    try:
        ser = serial.Serial(port, 9600, timeout=1)
        time.sleep(2)  # Allow time for Arduino to reset
        return ser
    except FileNotFoundError as e:
        print(f"Error: {e}. Port {port} not found.")
        return None
    except serial.SerialException as e:
        print(f"Error: Could not open port {port}. {e}")
        return None

# Set the serial port (adjust if needed)
port = '/dev/ttyUSB0'

# Try to initialize the serial port
ser = initialize_serial(port)

while ser is None:
    # Retry if the serial port is not available
    print("Retrying to open the serial port...")
    time.sleep(2)
    ser = initialize_serial(port)

while True:
    # Take user input
    data = {
        "command": {
            "LEFT": 0,
            "RIGHT": 0,
            "FORWARD": 1,
            "BACKWARD": 0,
            "TAKE_OFF": 0,
            "LAND": 0,
            "THROTTLE": 50
        },
        "GPS": [37.7749, -122.4194]
    }  # Create JSON structure
    json_data = json.dumps(data) + "\n"  # Convert to JSON string

    try:
        ser.write(json_data.encode())  # Send JSON to Arduino
        print(f"Sent: {json_data}")
    except serial.SerialException as e:
        print(f"Error: {e}. Retrying...")
        time.sleep(1)  # Wait a bit before retrying

    time.sleep(1)  # Wait before sending again
