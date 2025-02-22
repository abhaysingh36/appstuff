# from dronekit import connect ,VehicleMode, LocationGlobalRelative, APIException
# import time
# import socket
# import math
# import argparse
# from collections.abc import MutableMapping


# def connect_copter():
#     conncetion_strings="/dev/ttyACM0"
#     baud_rate=57600
#     vehicle=connect(conncetion_strings,baud=baud_rate,wait_ready=True)
#     return vehicle


# def arm():
#     vehicle.mode = VehicleMode("GUIDED")
#     while not vehicle.mode.name == 'GUIDED':  # Wait until mode is set
#         print("Waiting for GUIDED mode...")
#         time.sleep(1)

#     while vehicle.is_armable==False:
#         print("waiting to armnable")
#     print("armable now")


#     vehicle.arm=True
#     print(vehicle.armed)
#     while vehicle.armed==False:
#         print("waiting to be armed")
#         time.sleep(1)
#     print("armed")
#     return None

# vehicle=connect_copter()
# arm()
# print("end of scripts")




# from dronekit import connect, VehicleMode, LocationGlobalRelative
# import time
# import socket

# def connect_copter():
#     """
#     Connects to the vehicle via serial connection.
#     """
#     connection_string = "/dev/ttyACM0"  # Set your connection string
#     baud_rate = 57600  # Set your baud rate
#     print("Connecting to vehicle...")
#     vehicle = connect(connection_string, baud=baud_rate, wait_ready=True)
#     print(f"Connected to vehicle: {vehicle}")
#     return vehicle

# def arm(vehicle):
#     """
#     Arms the vehicle if it's armable and in the correct state.
#     """
#     # Ensure vehicle is in GUIDED mode
#     vehicle.mode = VehicleMode("GUIDED")
#     while not vehicle.mode.name == 'GUIDED':  # Wait until mode is set to GUIDED
#         print("Waiting for GUIDED mode...")
#         time.sleep(1)

#     # Check if vehicle is armable
#     if vehicle.is_armable:
#         print("Vehicle is armable.")
#     else:
#         print("Vehicle is NOT armable. Check pre-arm conditions.")
#         print("GPS fix type:", vehicle.gps_0.fix_type)  # Ensure GPS is fixed
#         print("Battery voltage:", vehicle.battery.voltage)  # Ensure battery voltage is good
#         print("Sensor health:", vehicle.parameters['SYS_STATUS'])  # Check sensor health
#         print(vehicle.armed)

#         return

#     # Optional: Override safety switch (if necessary)
#     vehicle.connection.mav.command_long_send(
#          vehicle.target_system, vehicle.target_component,
#          183, 0, 1, 0, 0, 0, 0, 0, 0
#      )

#     # Wait for GPS fix (to ensure vehicle is in a good state to arm)
#     while vehicle.gps_0.fix_type < 3:  # 3 means a 3D fix
#         print("Waiting for GPS lock...")
#         time.sleep(1)
    
#     # Arm the vehicle
#     print("Arming vehicle...")
#     vehicle.arm()
#     print(vehicle.armed)
    
#     # Wait until the vehicle is armed
#     while not vehicle.armed:
#         print("Waiting for vehicle to arm...")
#         time.sleep(1)
#     print("Vehicle is armed!")

# def main():
#     """
#     Main function to run the connection and arming sequence.
#     """
#     # Connect to the vehicle
#     vehicle = connect_copter()

#     # Arm the vehicle
#     arm(vehicle)

#     print("End of script")

#     # Close the connection (optional)
#     vehicle.close()
#     print("Connection closed.")

# if __name__ == "__main__":
#     main()







from dronekit import connect, VehicleMode, LocationGlobalRelative
import time

def connect_copter():
    """
    Connects to the vehicle via serial connection.
    """
    connection_string = "/dev/ttyACM0"  # Set your connection string
    baud_rate = 57600  # Set your baud rate
    print("Connecting to vehicle...")
    vehicle = connect(connection_string, baud=baud_rate, wait_ready=True)
    print(f"Connected to vehicle: {vehicle}")
    return vehicle

def arm(vehicle):
    """
    Arms the vehicle if it's armable and in the correct state.
    """
    # Ensure vehicle is in GUIDED mode
    vehicle.mode = VehicleMode("GUIDED")
    while not vehicle.mode.name == 'GUIDED':  # Wait until mode is set to GUIDED
        print("Waiting for GUIDED mode...")
        time.sleep(1)

    # Check if vehicle is armable
    if vehicle.is_armable:
        print("Vehicle is armable.")
    else:
        print("Vehicle is NOT armable. Check pre-arm conditions.")
        print("GPS fix type:", vehicle.gps_0.fix_type)  # Ensure GPS is fixed
        print("Battery voltage:", vehicle.battery.voltage)  # Ensure battery voltage is good
        vehicle_1=vehicle
        # Get system status to check for sensor health and errors
        status_msg = vehicle.recv_match(type='SYS_STATUS', blocking=True)
        if status_msg:
            print(f"System Status: Errors Count: {status_msg.errors_count1}")
        else:
            print("Failed to get system status.")
        
        return

    # Optional: Override safety switch (if necessary)
    # vehicle.connection.mav.command_long_send(
    #     vehicle.target_system, vehicle.target_component,
    #     183, 0, 1, 0, 0, 0, 0, 0, 0
    # )

    # Wait for GPS fix (to ensure vehicle is in a good state to arm)
    while vehicle.gps_0.fix_type < 3:  # 3 means a 3D fix
        print("Waiting for GPS lock...")
        time.sleep(1)
    
    # Arm the vehicle
    print("Arming vehicle...")
    vehicle.arm()
    
    # Wait until the vehicle is armed
    while not vehicle.armed:
        print("Waiting for vehicle to arm...")
        time.sleep(1)
    print("Vehicle is armed!")

def main():
    """
    Main function to run the connection and arming sequence.
    """
    # Connect to the vehicle
    vehicle = connect_copter()

    # Arm the vehicle
    arm(vehicle)

    print("End of script")

    # Close the connection (optional)
    vehicle.close()
    print("Connection closed.")

if __name__ == "__main__":
    main()
