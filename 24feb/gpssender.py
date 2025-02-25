import socket
import json
import time
import random

# Replace these with the DroneApp's actual IP and port.
SERVER_IP = "192.168.1.100"  # DroneApp's local IP address
SERVER_PORT = 9999           # Port on which your DroneApp listens for GPS updates

def simulate_gps():
    """Simulate GPS coordinates near a base location."""
    base_lat = 13.0215
    base_lng = 74.7927
    # Simulate a small variation around the base coordinates.
    lat = base_lat + random.uniform(-0.0001, 0.0001)
    lng = base_lng + random.uniform(-0.0001, 0.0001)
    return {"lat": lat, "lng": lng}

def main():
    try:
        # Create a TCP/IP socket.
        client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        client_socket.connect((SERVER_IP, SERVER_PORT))
        print(f"Connected to DroneApp server at {SERVER_IP}:{SERVER_PORT}")
        
        while True:
            gps_data = simulate_gps()
            # Convert the GPS data dictionary to a JSON string.
            message = json.dumps(gps_data)
            # Send the message with a newline as a delimiter.
            client_socket.sendall((message + "\n").encode('utf-8'))
            print(f"Sent GPS data: {message}")
            # Wait for 1 second before sending the next update.
            time.sleep(1)
            
    except KeyboardInterrupt:
        print("Terminating GPS sender...")
    except Exception as e:
        print("Error:", e)
    finally:
        client_socket.close()

if __name__ == "__main__":
    main()
