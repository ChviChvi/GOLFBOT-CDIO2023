import socket
import json
from ev3dev2.motor import MoveTank, MediumMotor, OUTPUT_B, OUTPUT_C, OUTPUT_A, OUTPUT_D
import threading

# Create a socket object
server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

# Set the SO_REUSEADDR socket option
server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

# Set IP and port
server_socket.bind(("0.0.0.0", 1234))

# Create motor objects
tank = MoveTank(OUTPUT_C, OUTPUT_D)
medium_motor_1 = MediumMotor(OUTPUT_B)
medium_motor_2 = MediumMotor(OUTPUT_A)  # Set this to the port the second medium motor is connected to

# Listen for incoming connections
server_socket.listen(1)

print("Server started. Waiting for a connection...")

# Create a global variable to store the latest command
latest_command = None

def execute_command():
    global latest_command
    while True:
        if latest_command:
            command = latest_command
            latest_command = None

            left_motor_speed = 0
            right_motor_speed = 0
            motor_speed = 0
            claw_speed = 0

            if 'up' in command and command['up']:
                tank.on_for_degrees(50, 50, 90)
            if 'down' in command and command['down']:
                tank.on_for_degrees(-50, -50, 90)
            if 'left' in command and command['left']:
                tank.on_for_degrees(-50, 50, 90)
            if 'right' in command and command['right']:
                tank.on_for_degrees(50, -50, 90)
            if 'o' in command and command['o']:
                medium_motor_2.on_for_degrees(25, 90)
            if 'p' in command and command['p']:
                medium_motor_2.on_for_degrees(-25, 90)

def read_command(client_socket):
    command_str = ''
    while True:
        try:
            data = client_socket.recv(1).decode()
            if data == '\n':
                break
            command_str += data
        except socket.error:
            print("Error reading from socket.")
            break
    return command_str

# Start a new thread to execute commands
command_thread = threading.Thread(target=execute_command)
command_thread.start()

try:
    while True:
        client_socket, client_address = server_socket.accept()
        print("Accepted connection from {}.".format(client_address))
        while True:
    
            try:
                command_str = read_command(client_socket)
                if not command_str:
                    break
                print("Received command: {}".format(command_str))  # Print the received command
                latest_command = json.loads(command_str)

            except json.JSONDecodeError:
                print("Received an invalid command: {}".format(command_str))
                continue
        
        client_socket.close()
        print("Client disconnected.")
except KeyboardInterrupt:
    # Stop the motors when the server is stopped
    tank.off()
    medium_motor_1.off()
    medium_motor_2.off()
    print('Stopping...')
finally:
    server_socket.close()
    print("Server stopped.")
