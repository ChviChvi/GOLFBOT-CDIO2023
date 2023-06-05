import socket
import json
from ev3dev2.motor import MoveTank, MediumMotor, OUTPUT_B, OUTPUT_C, OUTPUT_A, OUTPUT_D

# Create a socket object
server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

# Set IP and port
server_socket.bind(("0.0.0.0", 1234))

# Create motor objects
tank = MoveTank(OUTPUT_B, OUTPUT_C)
medium_motor_1 = MediumMotor(OUTPUT_A)
medium_motor_2 = MediumMotor(OUTPUT_D)  # Set this to the port the second medium motor is connected to

# Listen for incoming connections
server_socket.listen(1)

print("Server started. Waiting for a connection...")

def read_command(client_socket):
    command_str = ''
    while True:
        data = client_socket.recv(1).decode()
        if data == '\n':
            break
        command_str += data
    return command_str

try:
    while True:
        client_socket, client_address = server_socket.accept()
        print("Accepted connection from {}.".format(client_address))

        medium_motor_1.on(-15)  # Start the first medium motor when a client connects

        while True:
            command_str = read_command(client_socket)
            if not command_str:
                break
            command = json.loads(command_str)

            left_motor_speed = 0
            right_motor_speed = 0
            motor_speed = 0

            if command['up']:
                left_motor_speed += 50
                right_motor_speed += 50
            if command['down']:
                left_motor_speed -= 50
                right_motor_speed -= 50
            if command['left']:
                left_motor_speed -= 50
                right_motor_speed += 50
            if command['right']:
                left_motor_speed += 50
                right_motor_speed -= 50
            if command['o']:
                motor_speed = 50
            if command['p']:
                motor_speed = -50

            tank.on(left_motor_speed, right_motor_speed)
            medium_motor_2.on(motor_speed)

        medium_motor_1.off()  # Stop the first medium motor when a client disconnects

        client_socket.close()
        print("Client disconnected.")
except KeyboardInterrupt:
    medium_motor_1.off()  # Stop the first medium motor when the server is stopped
    print('Stopping...')
finally:
    server_socket.close()
    print("Server stopped.")
