import socket
import json
from ev3dev2.motor import MoveTank, MediumMotor, OUTPUT_B, OUTPUT_C, OUTPUT_A, OUTPUT_D

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

buffer = '' # Declare the buffer at the start of your script

try:
    while True:
        client_socket, client_address = server_socket.accept()
        print("Accepted connection from {}.".format(client_address))
        while True:
            global buffer
            try:
                data = client_socket.recv(1).decode()
                buffer += data
                try:
                    end_of_object_index = buffer.index('}') + 1
                    command_str = buffer[:end_of_object_index]
                    buffer = buffer[end_of_object_index:] 
                    command = json.loads(command_str)
                    print("Received command: {}".format(command))  # Printing Commands!!
                
                    left_motor_speed = 0
                    right_motor_speed = 0
                    motor_speed = 0
                    claw_speed = 0

                    if 'forward' in command and command['forward']:
                        left_motor_speed += 15
                        right_motor_speed += 15
                        claw_speed += 20
                    if 'backward' in command and command['backward']:
                        left_motor_speed -= 20
                        right_motor_speed -= 20
                        claw_speed -= 10
                    if 'turn_left' in command and command['turn_left']:
                        left_motor_speed += 3
                        right_motor_speed -= 3
                        claw_speed = 0
                    if 'turn_right' in command and command['turn_right']:
                        left_motor_speed -= 3
                        right_motor_speed += 3
                        claw_speed = 0                  
                    if 'o' in command and command['o']:
                        motor_speed = 20
                    if 'p' in command and command['p']:
                        motor_speed = -20

                    tank.on(left_motor_speed, right_motor_speed)
                    medium_motor_2.on(motor_speed)
                    medium_motor_1.on(claw_speed)
                except ValueError:
                    pass

            except socket.error:
                print("Connection lost. Attempting to reconnect...")
                client_socket.close()
                break  

except KeyboardInterrupt:
    # Stop the motors when the server is stopped
    tank.off()
    medium_motor_1.off()
    medium_motor_2.off()
    print('Stopping...')
finally:
    server_socket.close()
    print("Server stopped.")
