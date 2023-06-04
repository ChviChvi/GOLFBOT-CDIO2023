import socket
from ev3dev2.motor import MoveTank, OUTPUT_B, OUTPUT_C

# Create the motor object
tank = MoveTank(OUTPUT_B, OUTPUT_C)

# Create a new server socket
server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

# Bind to a specific IP and port
server_socket.bind(("0.0.0.0", 1234))

# Start listening for incoming connections
server_socket.listen(1)

print("Server started. Waiting for a connection...")

while True:
    # Wait for a client to connect
    client_socket, client_address = server_socket.accept()
    print("Accepted connection from {}.".format(client_address))

    while True:
        # Receive a command from the client
        command = client_socket.recv(1024).decode()

        if not command:
            break

        # Execute the command
        print("Received command: {}".format(command))
        if command == "up":
            tank.on_for_seconds(25, 25, 0.5)
        elif command == "down":
            tank.on_for_seconds(-25, -25, 0.5)
        elif command == "left":
            tank.on_for_seconds(-25, 25, 0.5)
        elif command == "right":
            tank.on_for_seconds(25, -25, 0.5)
        
    client_socket.close()
    print("Client disconnected.")

server_socket.close()
print("Server stopped.")
