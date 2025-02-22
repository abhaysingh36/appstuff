from pymavlink import mavutil
import time
from collections.abc import MutableMapping

# Connect to the Pixhawk (replace '/dev/ttyACM0' with your actual port)
master = mavutil.mavlink_connection('/dev/ttyACM0', baud=57600)  # Set the correct serial port

# Wait for a heartbeat to ensure the connection is established
timeout = time.time() + 10  # Set a timeout of 10 seconds to avoid hanging indefinitely
while True:
    heartbeat = master.recv_match(type='HEARTBEAT', blocking=False)
    if heartbeat:
        print(f"Heartbeat received from system (ID {master.target_system}, component {master.target_component})")
        break
    elif time.time() > timeout:
        print("No heartbeat received, check your connection and Pixhawk.")
        exit(1)
    time.sleep(1)  # Wait a bit before retrying

# Check battery voltage before arming
master.mav.request_data_stream_send(master.target_system, master.target_component,
                                    mavutil.mavlink.MAV_DATA_STREAM_ALL, 1, 1)

# Wait for the SYS_STATUS message
msg = master.recv_match(type='SYS_STATUS', blocking=True)
if msg:
    print(f"Battery voltage: {msg.voltage_battery / 1000.0} V")
    if msg.voltage_battery < 10000:  # Check if voltage is below 10V (example threshold)
        print("Warning: Battery voltage is too low to arm.")
        exit(1)

    # Check if there are sensor errors
    if msg.errors_count1 > 0:
        print(f"Warning: There are {msg.errors_count1} sensor errors.")
        exit(1)
else:
    print("Failed to get SYS_STATUS message.")
    exit(1)

# Optionally disable arming checks (only for testing in a safe environment)
param_id = "ARMING_CHECK"  # Ensure this is a string
master.mav.param_set_send(
    master.target_system,
    master.target_component,
    param_id.encode('ascii'),  # Encode the string to bytes
    0,  # Set value to 0 to disable all checks (not recommended for regular use)
    mavutil.mavlink.MAV_PARAM_TYPE_INT32  # Parameter type
)

# Optionally override safety switch (if applicable and required)
# Use command ID 183 (MAV_CMD_OVERRIDE_SAFETY command ID) directly
master.mav.command_long_send(
    master.target_system,
    master.target_component,
    183,  # MAV_CMD_OVERRIDE_SAFETY command ID
    0,  # Confirmation
    1,  # Param1: 1 to override safety switch
    0,  # Param2: Not used
    0,  # Param3: Not used
    0,  # Param4: Not used
    0,  # Param5: Not used
    0,  # Param6: Not used
    0   # Param7: Not used
)

# Set mode to GUIDED (numerical value: 4) to allow waypoint control
# MAV_MODE_GUIDED is the mode that allows the drone to follow waypoints and commands
master.mav.command_long_send(
    master.target_system,
    master.target_component,
    mavutil.mavlink.MAV_CMD_DO_SET_MODE,  # Command to change mode
    0,  # Confirmation
    4,  # Param1: Mode 4 corresponds to GUIDED mode (Manual: 0, Stabilize: 0, Guided: 4, etc.)
    0,  # Param2: Not used
    0,  # Param3: Not used
    0,  # Param4: Not used
    0,  # Param5: Not used
    0,  # Param6: Not used
    0   # Param7: Not used
)

# Send arm command (arming the drone)
print("Sending arm command to the drone...")
master.mav.command_long_send(
    master.target_system,  # Target system
    master.target_component,  # Target component
    mavutil.mavlink.MAV_CMD_COMPONENT_ARM_DISARM,  # Command to arm/disarm
    0,  # Confirmation (0 means no confirmation required)
    1,  # Param1 (1 to arm, 0 to disarm)
    0,  # Param2 (not used, set to 0)
    0,  # Param3 (not used, set to 0)
    0,  # Param4 (not used, set to 0)
    0,  # Param5 (not used, set to 0)
    0,  # Param6 (not used, set to 0)
    0   # Param7 (not used, set to 0)
)

# Wait for acknowledgment of the arm command
ack = master.recv_match(type='COMMAND_ACK', blocking=True)
if ack:
    result_description = mavutil.mavlink.enums['MAV_RESULT'][ack.result].description
    print(f"Command result: {result_description}")
else:
    print("No acknowledgment received. Command may have failed.")

# Check arm status after sending the arming command
arm_status = master.recv_match(type='HEARTBEAT', blocking=True)  # Check for heartbeat to verify if the drone is armed
if arm_status:
    print(arm_status)
    if arm_status.base_mode & mavutil.mavlink.MAV_MODE_FLAG_SAFETY_ARMED:
        print("The drone is armed.")
    else:
        print("The drone is not armed.")
else:
    print("Failed to get heartbeat after arming command.")

# Optionally, close the connection
master.close()
