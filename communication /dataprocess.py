import time
import socket
import threading
import multiprocessing
from pymavlink import mavutil
import cv2
import torch
device = 'cuda' if torch.cuda.is_available() else 'cpu'
model = torch.hub.load('ultralytics/yolov5', 'yolov5n', device=device)
if device == 'cuda':
    model.half() 
    
class ObjectDetection():
    def __init__(self, label):
        super().__init__()
        self.label = label
        self.running = True
        self.cap = cv2.VideoCapture("http://127.0.0.1:5000/video_feed")  # Flask feed URL
        # Check if the webcam feed is opened correctly
        if not self.cap.isOpened():
            print("Error: Could not open webcam feed.")
            self.running = False
        self.frame_count = 0  # To control frame processing rate
    def run(self):
        while self.running:
            ret, frame = self.cap.read()
            # If the frame is not grabbed, break the loop
            if not ret:
                print("Error: Failed to capture image.")
                break
            self.frame_count += 1
            # Process every 2nd frame to reduce load
            if self.frame_count % 2 == 0:
                # Resize the frame to a smaller resolution before inference (optional)
                new_width = 640  # Set your desired width
                new_height = 480  # Set your desired height
                resized_frame = cv2.resize(frame, (new_width, new_height))
                # Perform inference on the resized frame
                results = model(resized_frame)
                # Render the results on the frame (draw bounding boxes)
                frame_with_boxes = results.render()[0]
                # Convert frame with boxes to QImage for displaying
            
            # Optional: Control the rate at which frames are processed
            # This will help ensure the thread doesn't process too many frames per second
            cv2.waitKey(1)  # 1 ms delay to let the system process other events (helpful in threading)
    def stop(self):
        """Stop the thread"""
        self.running = False
        self.cap.release()  # Release the video capture object




class PixhawkConnection:
    def __init__(self, connection_string="/dev/ttyACM0", baud_rate=57600):
        self.connection_string = connection_string
        self.baud_rate = baud_rate
        self.connection = None

    def connect(self):
        """Establish connection with the Pixhawk."""
        self.connection = mavutil.mavlink_connection(self.connection_string, baud=self.baud_rate)
        print("Waiting for heartbeat from Pixhawk...")
        self.connection.wait_heartbeat()
        print("Heartbeat received from Pixhawk!")

    def request_data_stream(self):
        """Request attitude data stream from Pixhawk."""
        if self.connection:
            self.connection.mav.request_data_stream_send(
                self.connection.target_system,
                self.connection.target_component,
                mavutil.mavlink.MAV_DATA_STREAM_EXTRA1,
                1,  # Rate in Hz
                1   # Enable stream
            )

    def get_attitude(self):
        """Retrieve attitude data from Pixhawk (e.g., yaw)."""
        if self.connection:
            msg = self.connection.recv_match(blocking=True, type='ATTITUDE')
            if msg:
                yaw = msg.yaw  # Yaw in radians
                heading = yaw * (180.0 / 3.14159265359)  # Convert to degrees
                if heading < 0:
                    heading += 360  # Normalize to 0-360 degrees
                return f"Compass Heading: {heading:.2f}°"
        return None

    def get_location(self):
        """Retrieve location data from Pixhawk."""
        if self.connection:
            msg = self.connection.recv_match(blocking=True, type='AHRS2')
            if msg:
                latitude = msg.lat / 1e7  # Convert to decimal degrees
                longitude = msg.lng / 1e7
                altitude = msg.altitude / 1000.0  # Convert to meters
                return f"Latitude: {latitude}, Longitude: {longitude}, Altitude: {altitude}m"
        return None

    def arm_drone(self):
        """Arm the drone."""
        if self.connection:
            # Send the arming command (MAV_CMD_COMPONENT_ARM_DISARM)
            print("Arming the drone...")
            self.connection.mav.command_long_send(
                self.connection.target_system,  # Target system ID
                self.connection.target_component,  # Target component ID
                mavutil.mavlink.MAV_CMD_COMPONENT_ARM_DISARM,
                0,
                1,
                0,0,0,0,0,0                
                # Other parameters (not used here)
            )
            print("Arm command sent!")
            self.is_armed()

    def disarm_drone(self):
        """Disarm the drone."""
        if self.connection:
            # Send the disarming command (MAV_CMD_COMPONENT_ARM_DISARM)
            print("Disarming the drone...")
            self.connection.mav.command_long_send(
                self.connection.target_system,
                self.connection.target_component,
                mavutil.mavlink.MAV_CMD_COMPONENT_ARM_DISARM,
                1,
                1,  # 0 to disarm, 1 to arm
                0, 0, 0, 0, 0, 0
            )
            print("Disarm command sent!")

    def is_armed(self):
        """Check if the drone is armed by reading the SYS_STATUS message."""
        if self.connection:
            print(".............here...")
            msg = self.connection.recv_match(type='COMMAND_LONG', blocking=False)
            print(msg)
            print()
            if msg:
                # Check the ARM status in the system status flags
                print(">>>>>>>there>>>>")
                armed = msg.system_status & mavutil.mavlink.MAV_STATE_ARMED
                if armed:
                    print("Drone is armed.")
                    return True
                else:
                    print("Drone is not armed.")
                    return False
        return False


class Server:
    def __init__(self, pixhawk_conn):
        self.pixhawk_conn = pixhawk_conn
        self.functions_map = {
            'arm': self.arm,
            'disarm': self.disarm,
            'calibration': self.calibration,
            'get_data': self.get_data,
            'live_feed': self.live_feed,
            'is_armed': self.is_armed
        }

    def arm(self):
        """Trigger the arming of the drone."""
        self.pixhawk_conn.arm_drone()

    def disarm(self):
        """Trigger the disarming of the drone."""
        self.pixhawk_conn.disarm_drone()

    def calibration(self):
        print("Calibration function triggered!")

    def get_data(self):
        """Fetch data from Pixhawk."""
        attitude = self.pixhawk_conn.get_attitude()
        location = self.pixhawk_conn.get_location()

        # Send data to the client
        response = ""
        if attitude:
            response += attitude + "\n"
        if location:
            response += location + "\n"
        return response

    def live_feed(self):
        print("Live Feed function triggered!")

    def is_armed(self):
        """Check if the drone is armed."""
        if self.pixhawk_conn.is_armed():
            return "Drone is armed."
        else:
            return "Drone is not armed."

    def handle_client(self, client_socket):
        """Handle incoming client requests."""
        while True:
            try:
                request = client_socket.recv(1024).decode('utf-8')
                if request:
                    print(f"Received command: {request}")
                    if request in self.functions_map:
                        response = self.functions_map[request]()
                        print(response)
                       #client_socket.send(response.encode('utf-8'))
                    else:
                        client_socket.send(f"Function '{request}' not found.".encode('utf-8'))
                else:
                    break  # No request, close connection
            except Exception as e:
                print(f"Error while handling client: {e}")
                break

        client_socket.close()

    def start_server(self):
        """Start the server to listen for client connections."""
        server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server_socket.bind(('0.0.0.0', 5555))  # Bind to localhost and port 5555
        server_socket.listen(5)  # Max number of connections

        print("Server is running, waiting for clients to connect...")

        while True:
            try:
                client_socket, addr = server_socket.accept()
                print(f"Accepted connection from {addr}")
                client_thread = threading.Thread(target=self.handle_client, args=(client_socket,))
                client_thread.start()
            except Exception as e:
                print(f"Error while accepting client: {e}")
                continue


def compass_reader(pixhawk_conn):

    """Read data from Pixhawk and print compass information."""
    while True:
        try:
            heading = pixhawk_conn.get_attitude()
            location = pixhawk_conn.get_location()

            if heading:
                print(heading)
            if location:
                print(location)
        except Exception as e:
            print(f"Error reading compass data: {e}")
        time.sleep(0.1)


def main():
    # Create and start Pixhawk connection process
    pixhawk_conn = PixhawkConnection()
    pixhawk_conn.connect()
    pixhawk_conn.request_data_stream()

# self.connection.mav.command_long_send(
    # Create server process
    server_instance = Server(pixhawk_conn)
    server_process = multiprocessing.Process(target=server_instance.start_server)

    # Create compass reading process
    compass_process = multiprocessing.Process(target=compass_reader, args=(pixhawk_conn,))

    # Start the processes
    server_process.start()
    compass_process.start()

    # Wait for processes to finish
    server_process.join()
    compass_process.join()


if __name__ == "__main__":
    main()
# self.connection.mav.command_long_send(
#                 self.connection.target_system,
#                 self.connection.target_component,
#                 mavutil.mavlink.MAV_CMD_COMPONENT_ARM_DISARM,
#                 1,
#                 1,  # 0 to disarm, 1 to arm
#                 0, 0, 0, 0, 0, 0
#             )