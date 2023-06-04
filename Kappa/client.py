import socket
from pynput.keyboard import Key, Listener

# Define the commands for the arrow keys
commands = {
    Key.up: "up",
    Key.down: "down",
    Key.left: "left",
    Key.right: "right",
}

# Create a new client socket
client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

# Connect to the server
client_socket.connect(("172.20.10.5", 1234))  # Replace with your EV3's IP address

def on_press(key):
    if key in commands:
        # Send the command to the server
        command = commands[key]
        print(f'Sending command: {command}')
        client_socket.send(command.encode())

# Create the listener
listener = Listener(on_press=on_press)

# Start the listener in a non-blocking manner
listener.start()

print("Client started. Press arrow keys to control the EV3 brick.")
print("Press Ctrl+C to stop the client.")

try:
    while True:
        pass
except KeyboardInterrupt:
    print('Stopping...')
    listener.stop()
    client_socket.close()
    print("Client stopped.")
