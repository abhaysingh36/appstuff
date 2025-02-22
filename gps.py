from pymavlink import mavutil

def connect_pixhawk(connection_string="/dev/ttyACM0", baud=57600):
    """
    Connect to Pixhawk using the MAVLink protocol.
    :param connection_string: USB port where Pixhawk is connected (e.g., /dev/ttyACM0)
    :param baud: Baud rate for the connection (default: 115200)
    :return: MAVLink connection object
    """
    print(f"Connecting to Pixhawk on {connection_string} at {baud} baud...")
    connection = mavutil.mavlink_connection(connection_string, baud=baud)
    connection.wait_heartbeat()
    connection.mav.request_data_stream_send(
    connection.target_system,
    connection.target_component,
    mavutil.mavlink.MAV_DATA_STREAM_EXTRA1,
    1,  # Rate in Hz
    1   # Enable stream
)

    print("Heartbeat received from Pixhawk.")
    return connection


def collect_gps_data(connection):
    """
    Collect GPS data from Pixhawk.
    :param connection: MAVLink connection object
    """
    print("Collecting GPS data...")
    try:
        while True:
            # Wait for a GPS_RAW_INT message
            msg = connection.recv_match(type="GPS_RAW_INT", blocking=True)
            print(msg)
            if msg:
                latitude = msg.lat / 1e7  # Convert to decimal degrees
                longitude = msg.lon / 1e7
                altitude = msg.alt / 1000.0  # Convert to meters
                print(f"Latitude: {latitude}, Longitude: {longitude}, Altitude: {altitude}m")

            else:
                print(msg)
    except KeyboardInterrupt:
        print("\nGPS data collection stopped.")
    except Exception as e:
        print(f"Error while collecting GPS data: {e}")


if __name__ == "__main__":
    # Specify the USB port Pixhawk is connected to
    pixhawk_connection_string = "/dev/ttyACM0"  # Adjust if needed
    baud_rate = 57600# Typical baud rate for USB connection

    # Connect to Pixhawk and collect GPS data
    pixhawk_connection = connect_pixhawk(connection_string=pixhawk_connection_string, baud=baud_rate)
    
    collect_gps_data(pixhawk_connection)
