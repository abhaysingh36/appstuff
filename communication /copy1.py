import time
import socket
import threading
import multiprocessing
from pymavlink import mavutil

# Function to simulate reading data from server
def server():
    # Define functions to be called based on client requests
    def arm():
        print("Arm function triggered!")

    def calibration():
        print("Calibration function triggered!")

    def get_data():
        print("Get Data function triggered!")

    def live_feed():
        print("Live Feed function triggered!")

    # Dictionary to map function names to actual function calls
    functions_map = {
        'arm': arm,
        'calibration': calibration,
        'get_data': get_data,
        'live_feed': live_feed
    }

    # Handle client communication
    def handle_client(client_socket):
        while True:
            try:
                # Receive function name from client
                request = client_socket.recv(1024).decode('utf-8')
                if request:
                    print(f"Received command: {request}")

                    # Check if the function name exists in the map
                    if request in functions_map:
                        # Call the corresponding function
                        functions_map[request]()
                        client_socket.send(f"Function '{request}' executed.".encode('utf-8'))
                    else:
                        client_socket.send(f"Function '{request}' not found.".encode('utf-8'))
                else:
                    break  # No request, close connection
            except Exception as e:
                print(f"Error while handling client: {e}")
                break

        # Close the client connection
        client_socket.close()

    def start_server():
        # Set up the server socket
        server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server_socket.bind(('0.0.0.0', 5555))  # Bind to localhost and port 5555
        server_socket.listen(5)  # Max number of connections

        print("Server is running, waiting for clients to connect...")

        while True:
            try:
                # Accept a new client connection
                client_socket, addr = server_socket.accept()
                print(f"Accepted connection from {addr}")

                # Handle the client in a separate thread
                client_thread = threading.Thread(target=handle_client, args=(client_socket,))
                client_thread.start()

            except Exception as e:
                print(f"Error while accepting client: {e}")
                continue

    # Start the server
    start_server()


# Compass function to simulate data reading from Pixhawk
def compass():
    # Connect to the Pixhawk
    connection_string = "/dev/ttyACM0"  # Change to '/dev/ttyACM1' if necessary
    baud_rate = 57600
    connection = mavutil.mavlink_connection(connection_string, baud=baud_rate)

    # Wait for heartbeat
    print("Waiting for heartbeat from Pixhawk...")
    connection.wait_heartbeat()
    print("Heartbeat received from Pixhawk!")

    # Request data stream for attitude (yaw)
    connection.mav.request_data_stream_send(
        connection.target_system,
        connection.target_component,
        mavutil.mavlink.MAV_DATA_STREAM_EXTRA1,
        1,  # Rate in Hz
        1   # Enable stream
    )

    while True:
        try:
            # Receive a message
            msg = connection.recv_match(blocking=True, type=None)
            if not msg or msg.get_type() == 'BAD_DATA':
                continue

            # Parse relevant messages
            if msg.get_type() == 'ATTITUDE':
                yaw = msg.yaw  # Yaw in radians
                heading = yaw * (180.0 / 3.14159265359)  # Convert to degrees
                if heading < 0:
                    heading += 360  # Normalize to 0-360 degrees
                print(f"Compass Heading: {heading:.2f}°")

            if msg.get_type() == 'AHRS2':
                latitude = msg.lat / 1e7  # Convert to decimal degrees
                longitude = msg.lng / 1e7
                altitude = msg.altitude / 1000.0  # Convert to meters
                print(f"Latitude: {latitude}, Longitude: {longitude}, Altitude: {altitude}m")

        except KeyboardInterrupt:
            print("Exiting...")
            break                               
        except Exception as e:
            print(f"Error: {e}")
            continue

        # Avoid CPU overload
        time.sleep(0.1)


if __name__ == "__main__":
    # Create a queue for inter-process communication (if necessary)
    queue = multiprocessing.Queue()

    # Start the data_reader and data_processor processes
    reader_process = multiprocessing.Process(target=server)
    processor_process = multiprocessing.Process(target=compass)

    # Start both processes
    reader_process.start()
    processor_process.start()

    # Wait for both processes to finish
    reader_process.join()
    processor_process.join()

    print("Both processes have finished.")
