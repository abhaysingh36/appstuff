import time
from pymavlink import mavutil

# Connect to the Pixhawk
connection_string = "/dev/ttyACM0"  # Change to '/dev/ttyACM1' if necessary
baud_rate = 57600
connection = mavutil.mavlink_connection(connection_string, baud=baud_rate)

# Wait for heartbeat
print("Waiting for heartbeat from Pixhawk...")
connection.wait_heartbeat()
print("Heartbeat received from Pixhawk!")

print()
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
        
        if msg.get_type()=='AHRS2':
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
