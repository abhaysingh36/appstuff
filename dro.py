from pymavlink import mavutil

def check_pixhawk_connection(connection_string, baudrate):
    try:
        connection = mavutil.mavlink_connection(connection_string, baud=baudrate)
        print("Connected to Pixhawk.")
        
        while True:
            msg = connection.recv_match(blocking=True, timeout=5)
            if msg:
                print(f"Received message: {msg}")
            else:
                print("No valid MAVLink message received.")
    except Exception as e:
        print(f"Connection error: {e}")

# Update with correct serial port and baudrate
connection_string = "/dev/ttyACM0"
baudrate = 115200
check_pixhawk_connection(connection_string, baudrate)
