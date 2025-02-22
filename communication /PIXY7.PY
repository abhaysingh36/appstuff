# from pymavlink import mavutil
# import time

# # Connect to the Pixhawk (replace '/dev/ttyACM0' with your actual port)
# master = mavutil.mavlink_connection('/dev/ttyACM0', baud=57600)  # Set the correct serial port

# # Wait for a heartbeat to ensure the connection is established
# timeout = time.time() + 10  # Set a timeout of 10 seconds to avoid hanging indefinitely
# while True:
#     heartbeat = master.recv_match(type='HEARTBEAT', blocking=False)
#     if heartbeat:
#         print(f"Heartbeat received from system (ID {master.target_system}, component {master.target_component})")
#         break
#     elif time.time() > timeout:
#         print("No heartbeat received, check your connection and Pixhawk.")
#         exit(1)
#     time.sleep(1)  # Wait a bit before retrying

# # Check battery voltage before arming
# master.mav.request_data_stream_send(master.target_system, master.target_component,
#                                     mavutil.mavlink.MAV_DATA_STREAM_ALL, 1, 1)

# # Wait for the SYS_STATUS message
# msg = master.recv_match(type='STATUSTEXT', blocking=0)
# if msg:
#     print(f"Battery voltage: {msg.voltage_battery / 1000.0} V")
#     if msg.voltage_battery < 10000:  # Check if voltage is below 10V (example threshold)
#         print("Warning: Battery voltage is too low to arm.")
#         exit(1)

# # Check for sensor calibration status
# master.mav.command_long_send(
#     master.target_system, master.target_component,
#     mavutil.mavlink.MAV_CMD_PREFLIGHT_CALIBRATION,  # Command for calibration
#     0,  # No confirmation needed
#     0,  # Param1 (unused)
#     0,  # Param2 (unused)
#     0,  # Param3 (unused)
#     0,  # Param4 (unused)
#     0,  # Param5 (unused)
#     0,  # Param6 (unused)
#     0   # Param7 (unused)
# )

# # Wait for a calibration status message
# msg = master.recv_match(type='STATUSTEXT', blocking=True)
# if msg:
#     print(f"Calibration message: {msg.text}")
# else:
#     print("No calibration message received.")

# # Optionally disable arming checks (only for testing in a safe environment)
# try:
#     print("Attempting to disable ARMING_CHECK...")
#     param_name = "ARMING_CHECK"
#     print(f"Parameter type: {type(param_name)}")  # Should print <class 'str'>
#     master.mav.param_set_send(
#         master.target_system,
#         master.target_component,
#         param_name.encode(),  # Encode the string as bytes to avoid ambiguity
#         0,  # Set value to 0 to disable all checks (not recommended for regular use)
#         mavutil.mavlink.MAV_PARAM_TYPE_INT32  # Parameter type
#     )
#     print("ARMING_CHECK successfully disabled.")
# except Exception as e:
#     print(f"Error while disabling ARMING_CHECK: {e}")

# # Override safety switch if necessary
# master.mav.command_long_send(
#     master.target_system,
#     master.target_component,
#     mavutil.mavlink.MAV_CMD_OVERRIDE_SAFETY,  # Override safety switch
#     0,  # Confirmation
#     1,  # Param1: 1 to override safety switch
#     0,  # Param2-7: Not used
#     0,
#     0,
#     0,
#     0,
#     0
# )
from pymavlink import mavutil
# import time

# # Connect to the Pixhawk (replace '/dev/ttyACM0' with your actual port)
# master = mavutil.mavlink_connection('/dev/ttyACM0', baud=57600)  # Set the correct serial port

# # Wait for a heartbeat to ensure the connection is established
# timeout = time.time() + 10  # Set a timeout of 10 seconds to avoid hanging indefinitely
# while True:
#     heartbeat = master.recv_match(type='HEARTBEAT', blocking=False)
#     if heartbeat:
#         print(f"Heartbeat received from system (ID {master.target_system}, component {master.target_component})")
#         break
#     elif time.time() > timeout:
#         print("No heartbeat received, check your connection and Pixhawk.")
#         exit(1)
#     time.sleep(1)  # Wait a bit before retrying

# # Check battery voltage before arming
# master.mav.request_data_stream_send(master.target_system, master.target_component,
#                                     mavutil.mavlink.MAV_DATA_STREAM_ALL, 1, 1)

# # Wait for the SYS_STATUS message
# msg = master.recv_match(type='STATUSTEXT', blocking=0)
# if msg:
#     print(f"Battery voltage: {msg.voltage_battery / 1000.0} V")
#     if msg.voltage_battery < 10000:  # Check if voltage is below 10V (example threshold)
#         print("Warning: Battery voltage is too low to arm.")
#         exit(1)

# # Check for sensor calibration status
# master.mav.command_long_send(
#     master.target_system, master.target_component,
#     mavutil.mavlink.MAV_CMD_PREFLIGHT_CALIBRATION,  # Command for calibration
#     0,  # No confirmation needed
#     0,  # Param1 (unused)
#     0,  # Param2 (unused)
#     0,  # Param3 (unused)
#     0,  # Param4 (unused)
#     0,  # Param5 (unused)
#     0,  # Param6 (unused)
#     0   # Param7 (unused)
# )

# # Wait for a calibration status message
# msg = master.recv_match(type='STATUSTEXT', blocking=True)
# if msg:
#     print(f"Calibration message: {msg.text}")
# else:
#     print("No calibration message received.")

# # Optionally disable arming checks (only for testing in a safe environment)
# try:
#     print("Attempting to disable ARMING_CHECK...")
#     param_name = "ARMING_CHECK"
#     print(f"Parameter type: {type(param_name)}")  # Should print <class 'str'>
#     master.mav.param_set_send(
#         master.target_system,
#         master.target_component,
#         param_name.encode(),  # Encode the string as bytes to avoid ambiguity
#         0,  # Set value to 0 to disable all checks (not recommended for regular use)
#         mavutil.mavlink.MAV_PARAM_TYPE_INT32  # Parameter type
#     )
#     print("ARMING_CHECK successfully disabled.")
# except Exception as e:
#     print(f"Error while disabling ARMING_CHECK: {e}")

# # Override safety switch if necessary
# master.mav.command_long_send(
#     master.target_system,
#     master.target_component,
#     mavutil.mavlink.MAV_CMD_OVERRIDE_SAFETY,  # Override safety switch
#     0,  # Confirmation
#     1,  # Param1: 1 to override safety switch
#     0,  # Param2-7: Not used
#     0,
#     0,
#     0,
#     0,
#     0
# )

# # Attempt to arm the drone
# master.mav.command_long_send(
#     master.target_system,  # Target system
#     master.target_component,  # Target component
#     mavutil.mavlink.MAV_CMD_COMPONENT_ARM_DISARM,  # Command to arm/disarm
#     0,  # Confirmation (0 means no confirmation required)
#     1,  # Param1 (1 to arm, 0 to disarm)
#     0,  # Param2 (not used, set to 0)
#     0,  # Param3 (not used, set to 0)
#     0,  # Param4 (not used, set to 0)
#     0,  # Param5 (not used, set to 0)
#     0,  # Param6 (not used, set to 0)
#     0   # Param7 (not used, set to 0)
# )

# # Wait for acknowledgment of the arm command
# ack = master.recv_match(type='COMMAND_ACK', blocking=True)
# if ack:
#     result_description = mavutil.mavlink.enums['MAV_RESULT'][ack.result].description
#     print(f"Command result: {result_description}")
# else:
#     print("No acknowledgment received. Command may have failed.")

# # Optionally, close the connection
# master.close()

#     0,  # Param5 (not used, set to 0)
#     0,  # Param6 (not used, set to 0)
#     0   # Param7 (not used, set to 0)
# )

# # Wait for acknowledgment of the arm command
# ack = master.recv_match(type='COMMAND_ACK', blocking=True)
# if ack:
#     result_description = mavutil.mavlink.enums['MAV_RESULT'][ack.result].description
#     print(f"Command result: {result_description}")
# else:
#     print("No acknowledgment received. Command may have failed.")

# # Optionally, close the connection
# master.close()


# from pymavlink import mavutil
# import time

# # Connect to the Pixhawk (replace '/dev/ttyACM0' with your actual port)
# master = mavutil.mavlink_connection('/dev/ttyACM0', baud=57600)  # Set the correct serial port

# # Wait for a heartbeat to ensure the connection is established
# timeout = time.time() + 10  # Set a timeout of 10 seconds to avoid hanging indefinitely
# while True:
#     heartbeat = master.recv_match(type='HEARTBEAT', blocking=False)
#     if heartbeat:
#         print(f"Heartbeat received from system (ID {master.target_system}, component {master.target_component})")
#         break
#     elif time.time() > timeout:
#         print("No heartbeat received, check your connection and Pixhawk.")
#         exit(1)
#     time.sleep(1)  # Wait a bit before retrying

# # Check battery voltage before arming
# master.mav.request_data_stream_send(master.target_system, master.target_component,
#                                     mavutil.mavlink.MAV_DATA_STREAM_ALL, 1, 1)

# # Wait for the SYS_STATUS message
# msg = master.recv_match(type='STATUSTEXT', blocking=0)
# if msg:
#     print(f"Battery voltage: {msg.voltage_battery / 1000.0} V")
#     if msg.voltage_battery < 10000:  # Check if voltage is below 10V (example threshold)
#         print("Warning: Battery voltage is too low to arm.")
#         exit(1)

# # Check for sensor calibration status
# master.mav.command_long_send(
#     master.target_system, master.target_component,
#     mavutil.mavlink.MAV_CMD_PREFLIGHT_CALIBRATION,  # Command for calibration
#     0,  # No confirmation needed
#     0,  # Param1 (unused)
#     0,  # Param2 (unused)
#     0,  # Param3 (unused)
#     0,  # Param4 (unused)
#     0,  # Param5 (unused)
#     0,  # Param6 (unused)
#     0   # Param7 (unused)
# )

# # Wait for a calibration status message
# msg = master.recv_match(type='STATUSTEXT', blocking=True)
# if msg:
#     print(f"Calibration message: {msg.text}")
# else:
#     print("No calibration message received.")

# # Disable ARMING_SAFETY check (if your goal is to bypass safety checks before arming)
# try:
#     print("Attempting to disable ARMING_SAFETY...")
#     param_name = "ARMING_SAFETY"  # Parameter related to safety check
#     print(f"Parameter type: {type(param_name)}")  # Should print <class 'str'>
    
#     master.mav.param_set_send(
#         master.target_system,
#         master.target_component,
#         param_name.encode(),  # Encode the string as bytes to avoid ambiguity
#         0,  # Disable safety check
#         mavutil.mavlink.MAV_PARAM_TYPE_INT32  # Parameter type for INT32
#     )
#     print(f"ARMING_SAFETY successfully disabled.")
# except Exception as e:
#     print(f"Error while disabling ARMING_SAFETY: {e}")

# # Attempt to arm the drone
# master.mav.command_long_send(
#     master.target_system,  # Target system
#     master.target_component,  # Target component
#     mavutil.mavlink.MAV_CMD_COMPONENT_ARM_DISARM,  # Command to arm/disarm
#     0,  # Confirmation (0 means no confirmation required)
#     1,  # Param1 (1 to arm, 0 to disarm)
#     0,  # Param2 (not used, set to 0)
#     0,  # Param3 (not used, set to 0)
#     0,  # Param4 (not used, set to 0)
#     0,  # Param5 (not used, set to 0)
#     0,  # Param6 (not used, set to 0)
#     0   # Param7 (not used, set to 0)
# )

# # Wait for acknowledgment of the arm command
# ack = master.recv_match(type='COMMAND_ACK', blocking=True)
# if ack:
#     result_description = mavutil.mavlink.enums['MAV_RESULT'][ack.result].description
#     print(f"Command result: {result_description}")
# else:
#     print("No acknowledgment received. Command may have failed.")

# # Optionally, close the connection
# master.close()







from pymavlink import mavutil
import time

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

# Wait for the SYS_STATUS message to check battery voltage
msg = master.recv_match(type='STATUSTEXT', blocking=0)
if msg:
    print(f"Battery voltage: {msg.voltage_battery / 1000.0} V")
    if msg.voltage_battery < 10000:  # Check if voltage is below 10V (example threshold)
        print("Warning: Battery voltage is too low to arm.")
        exit(1)

# Check for sensor calibration status
master.mav.command_long_send(
    master.target_system, master.target_component,
    mavutil.mavlink.MAV_CMD_PREFLIGHT_CALIBRATION,  # Command for calibration
    0,  # No confirmation needed
    0,  # Param1 (unused)
    0,  # Param2 (unused)
    0,  # Param3 (unused)
    0,  # Param4 (unused)
    0,  # Param5 (unused)
    0,  # Param6 (unused)
    0   # Param7 (unused)
)

# Wait for a calibration status message
msg = master.recv_match(type='STATUSTEXT', blocking=True)
if msg:
    print(f"Calibration message: {msg.text}")
else:
    print("No calibration message received.")

# Disable ARMING_SAFETY check (if your goal is to bypass safety checks before arming)
try:
    print("Attempting to disable ARMING_SAFETY...")
    param_name = "ARMING_SAFETY"  # Parameter related to safety check
    print(f"Parameter type: {type(param_name)}")  # Should print <class 'str'>
    
    master.mav.param_set_send(
        master.target_system,
        master.target_component,
        param_name.encode(),  # Encode the string as bytes to avoid ambiguity
        0,  # Disable safety check
        mavutil.mavlink.MAV_PARAM_TYPE_INT32  # Parameter type for INT32
    )
    print(f"ARMING_SAFETY successfully disabled.")
except Exception as e:
    print(f"Error while disabling ARMING_SAFETY: {e}")

# Optionally disable ARMING_CHECK if necessary
try:
    print("Attempting to disable ARMING_CHECK...")
    param_name = "ARMING_CHECK"  # Disable all arming checks
    master.mav.param_set_send(
        master.target_system,
        master.target_component,
        param_name.encode(),  # Encode the string as bytes to avoid ambiguity
        0,  # Disable all arming checks
        mavutil.mavlink.MAV_PARAM_TYPE_INT32  # Parameter type for INT32
    )
    print(f"ARMING_CHECK successfully disabled.")
except Exception as e:
    print(f"Error while disabling ARMING_CHECK: {e}")

# Attempt to arm the drone
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
    print(ack)
    result_description = mavutil.mavlink.enums['MAV_RESULT'][ack.result].description
    print(f"Command result: {result_description}")
else:
    print("No acknowledgment received. Command may have failed.")

# Optionally, close the connection
master.close()
