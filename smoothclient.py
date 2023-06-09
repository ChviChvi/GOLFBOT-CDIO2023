import socket
from pynput.keyboard import Key, Listener
import json
import threading
import time 
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

def connect_to_robot():
    global client_socket
    while True:
        try:
            print("Connecting to robot...")
            client_socket.connect(("172.20.10.5", 1234))  # Replace with your EV3's IP address
            print("Connected to robot!")
            break
        except ConnectionRefusedError:
            print("Failed to connect to robot. Retrying in 5 seconds...")
            time.sleep(5)  # Delay for 5 seconds before retrying

robot_connection_thread = threading.Thread(target=connect_to_robot)
robot_connection_thread.start()

# Create another client socket to connect to Tracing5.py
tracking_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

def connect_to_tracking():
    global tracking_socket
    while True:
        try:
            print("Connecting to tracking...")
            tracking_socket.connect(("localhost", 1235))
            print("Connected to tracking!")
            print("Client started. Press arrow keys to control the EV3 brick.")
            print("Press O and P to control the second medium motor.")
            print("Press Ctrl+C to stop the client.")
            threading.Thread(target=receive_tracking_data, daemon=True).start() # moved here
            break
        except ConnectionRefusedError:
            print("Failed to connect to tracking. Retrying in 5 seconds...")
            time.sleep(5)
        except Exception as e:
            print(f"Unexpected error while connecting to tracking: {e}")


tracking_connection_thread = threading.Thread(target=connect_to_tracking)
tracking_connection_thread.start()

key_state = {
    "up": False,
    "down": False,
    "left": False,
    "right": False,
    "o": False,
    "p": False
}

def on_press(key):
    try:
        if key.char == 'o':
            key_state['o'] = True
        elif key.char == 'p':
            key_state['p'] = True
    except AttributeError:
        if key == Key.up:
            key_state['up'] = True
        elif key == Key.down:
            key_state['down'] = True
        elif key == Key.left:
            key_state['left'] = True
        elif key == Key.right:
            key_state['right'] = True
    client_socket.send((json.dumps(key_state) + '\n').encode())

def on_release(key):
    try:
        if key.char == 'o':
            key_state['o'] = False
        elif key.char == 'p':
            key_state['p'] = False
    except AttributeError:
        if key == Key.up:
            key_state['up'] = False
        elif key == Key.down:
            key_state['down'] = False
        elif key == Key.left:
            key_state['left'] = False
        elif key == Key.right:
            key_state['right'] = False
    client_socket.send((json.dumps(key_state) + '\n').encode())


def receive_tracking_data():
    while True:
        try:
            data = tracking_socket.recv(1024)
            if data:
                received_data = json.loads(data.decode().rstrip())
                
                if 'white_balls' in received_data:
                    white_balls_position = received_data["white_balls"]
                    print(f"Received white balls positions: {white_balls_position}")
                
                if 'orange_balls' in received_data:
                    orange_balls_position = received_data["orange_balls"]
                    print(f"Received orange balls positions: {orange_balls_position}")
                
                if 'robot' in received_data:
                    robot_position = received_data['robot']
                    print(f"Received robot position: {robot_position}")
        except OSError:
            print("Warning: Cannot receive data from tracking server.")
            break



#if tracking_socket:
#    threading.Thread(target=receive_tracking_data, daemon=True).start()

# Create the listener
listener = Listener(on_press=on_press, on_release=on_release)

# Start the listener in a non-blocking manner
listener.start()



try:
    while True:
        pass
except KeyboardInterrupt:
    print('Stopping...')
    listener.stop()
    client_socket.close()
    print("Client stopped.")

if tracking_socket:
    tracking_socket.close()
