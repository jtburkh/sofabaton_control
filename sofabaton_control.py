from evdev import InputDevice, ecodes
import os
import json

# Path to the channel.socket file
COMMAND_FILE = "/home/jtburkh/FieldStation42/runtime/channel.socket" # Replace this with the path to your channel.socket

# Map button codes to their respective values
button_map = {
    2: "1",  # Button 1
    3: "2",  # Button 2
    4: "3",  # Button 3
    5: "4",  # Button 4
    6: "5",  # Button 5
    7: "6",  # Button 6
    8: "7",  # Button 7
    9: "8",  # Button 8
    10: "9", # Button 9
    11: "0", # Button 0
    18: "enter"  # E button (Enter)
}

# Specify the event file for the Sofabaton remote
REMOTE_DEVICE = "/dev/input/event10"  # Replace this with your device number

# Buffer to hold multi-digit channel inputs
channel_buffer = []

# Open the remote input device
try:
    remote = InputDevice(REMOTE_DEVICE)
    print(f"Listening for input on {REMOTE_DEVICE}...")
except FileNotFoundError:
    print(f"Device {REMOTE_DEVICE} not found. Ensure the remote is connected.")
    exit()

# Process remote button presses
for event in remote.read_loop():
    if event.type == ecodes.EV_KEY and event.value == 1:  # Key press event
        command = button_map.get(event.code)

        if command:
            if command == "enter":
                if channel_buffer:  # Only process if buffer is not empty
                    channel_number = int("".join(channel_buffer))
                    json_command = {
                        "command": "direct",
                        "channel": channel_number
                    }
                    with open(COMMAND_FILE, "w") as f:
                        f.write(json.dumps(json_command))  # Write as JSON
                    print(f"Sent command: {json_command}")
                    channel_buffer.clear()  # Clear buffer after processing
            else:
                # Append digit to buffer
                channel_buffer.append(command)
                print(f"Buffer updated: {''.join(channel_buffer)}")
