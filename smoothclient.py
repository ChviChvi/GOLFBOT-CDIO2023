import socket
from pynput.keyboard import Key, Listener
import json
from ev3dev2.power import PowerSupply

power = PowerSupply()

# Get the battery voltage
voltage = power.measured_voltage / 1000  # Convert millivolts to volts

# Calculate the remaining percentage
max_voltage = 8.3  # Maximum voltage for a full battery
min_voltage = 6.0  # Minimum voltage for an empty battery
remaining_percentage = (voltage - min_voltage) / (max_voltage - min_voltage) * 100

# Display the remaining battery percentage
print("Battery Remaining: {:.2f}%".format(remaining_percentage))

# Create a new client socket
client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

# Connect to the server
client_socket.connect(("192.168.134.146", 1234))  # Replace with your EV3's IP address

key_state = {
    "up": False,
    "down": False,
    "left": False,
    "right": False,
    "o": False,
    "p": False
}

def on_press(key):
    if key == Key.up:
        key_state['up'] = True
    elif key == Key.down:
        key_state['down'] = True
    elif key == Key.left:
        key_state['left'] = True
    elif key == Key.right:
        key_state['right'] = True
    elif key.char == 'o':
        key_state['o'] = True
    elif key.char == 'p':
        key_state['p'] = True
    client_socket.send((json.dumps(key_state) + '\n').encode())

def on_release(key):
    if key == Key.up:
        key_state['up'] = False
    elif key == Key.down:
        key_state['down'] = False
    elif key == Key.left:
        key_state['left'] = False
    elif key == Key.right:
        key_state['right'] = False
    elif key.char == 'o':
        key_state['o'] = False
    elif key.char == 'p':
        key_state['p'] = False
    client_socket.send((json.dumps(key_state) + '\n').encode())

# Create the listener
listener = Listener(on_press=on_press, on_release=on_release)

# Start the listener in a non-blocking manner
listener.start()

print("Client started. Press arrow keys to control the EV3 brick.")
print("Press O and P to control the second medium motor.")
print("Press Ctrl+C to stop the client.")

try:
    while True:
        pass
except KeyboardInterrupt:
    print('Stopping...')
    listener.stop()
    client_socket.close()
    print("Client stopped.")
