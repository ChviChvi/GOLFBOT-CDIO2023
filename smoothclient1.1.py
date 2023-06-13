import socket
from pynput.keyboard import Key, Listener
import json
import threading
import time 
from pathfinding import astar, find_nearest_ball, reconstruct_path

client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

def connect_to_robot():
    global client_socket
    while True:
        try:
            print("Connecting to robot...")
            client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)  # Moved inside the loop to create new socket on reconnection
            client_socket.connect(("172.20.10.5", 1234))  # Replace with your EV3's IP address
            print("Connected to robot!")
            
            while True:  # Check for active connection
                try:
                    client_socket.send(json.dumps({'ping': True}).encode())  # Test send data
                    time.sleep(5)  # Wait 5 seconds before checking again
                except Exception as e:  # If sending data fails, connection has been lost
                    print(f"Lost connection to robot: {e}")
                    break  # Break the inner loop to reconnect
        except ConnectionRefusedError:
            print("Failed to connect to robot. Retrying in 5 seconds...")
        except Exception as e:  # Catch all other exceptions
            print(f"Unexpected error while connecting to robot: {e}")
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
            tracking_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)  # Moved inside the loop to create new socket on reconnection
            tracking_socket.connect(("localhost", 1235))
            print("Connected to tracking!")
            print("Client started. Press arrow keys to control the EV3 brick.")
            print("Press O and P to control the second medium motor.")
            print("Press Ctrl+C to stop the client.")
            threading.Thread(target=receive_tracking_data, daemon=True).start()  # Start receiving data

            while True:  # Check for active connection
                try:
                    tracking_socket.send(b'ping')  # Test send data
                    time.sleep(5)  # Wait 5 seconds before checking again
                except Exception as e:  # If sending data fails, connection has been lost
                    print(f"Lost connection to tracking: {e}")
                    break  # Break the inner loop to reconnect
        except ConnectionRefusedError:
            print("Failed to connect to tracking. Retrying in 5 seconds...")
        except Exception as e:  # Catch all other exceptions
            print(f"Unexpected error while connecting to tracking: {e}")
        time.sleep(5)  # Delay for 5 seconds before retrying

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

def move_robot(path_to_nearest_ball):
    print("did the algo send?1")
    if len(path_to_nearest_ball) > 1:  # If there is at least one move to make
        next_move = path_to_nearest_ball[1]  # We choose the second element because the first one is the current robot's position
        current_pos = path_to_nearest_ball[0]
        slowmode = False
        move = (next_move[0]-current_pos[0], next_move[1]-current_pos[1])  # Calculate the difference to determine the direction
        
        #TODO insert code tht checks if the robot is near a wall/obstacle

        print("did the algo send?2")
        # Now update key_state based on the direction
        if move == (-1, 0):
            key_state["up"] = True
        elif move == (1, 0):
            key_state["down"] = True
        elif move == (0, -1):
            key_state["left"] = True
        elif move == (0, 1):
            key_state["right"] = True
        if slowmode == True:
            key_state["slowmode"] = True
        print("did the algo send?5")
        # Send the command to the robot
        client_socket.send((json.dumps(key_state) + '\n').encode())
        print("did the algo send?4")
        # After 0.5 seconds, stop the robot
        time.sleep(0.5)
        reset_key_state()  # You need to define this function
        print("did the algo send?")
        client_socket.send((json.dumps(key_state) + '\n').encode())
        print("did the algo send? --- yes")

def reset_key_state():
    key_state['up'] = False
    key_state['down'] = False
    key_state['left'] = False
    key_state['right'] = False
    key_state['o'] = False
    key_state['p'] = False

def on_press(key):
    print(f"Key pressed: {key}")
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

                if 'red_crosses' in received_data:
                    red_crosses = received_data["red_crosses"]
                    print(f"THE RED CROSS IS AT: {red_crosses}")

                if 'white_balls' in received_data:
                    white_balls = received_data["white_balls"]
                    print(f"Received white balls positions: {white_balls}")

                if 'orange_balls' in received_data:
                    orange_balls = received_data["orange_balls"]
                    print(f"Received orange balls positions: {orange_balls}")

                if 'robot' in received_data:
                    robot_position = received_data['robot']
                    print(f"Received robot position: {robot_position}")

                if 'grid_size' in received_data:
                    grid_size = received_data["grid_size"]
                    print(f"SIZE OF THE GRID IS: {grid_size}")

                if 'orientation' in received_data:
                    orientation = received_data["orientation"]
                    print(f"orientation is (90 is north): {orientation}")


                    

                    try:
                        # Initialize grid
                        grid = [[0 for _ in range(grid_size[1])] for _ in range(grid_size[0])]

                        # Mark red crosses on the grid
                        for cross in red_crosses:
                            grid[cross[0]][cross[1]] = 1  # 1 represents red cross

                        # Find nearest ball
                        balls = white_balls + orange_balls  # if you also consider orange balls
                        nearest_ball = find_nearest_ball(grid, robot_position, balls)

                        # Find path to nearest ball
                        came_from, cost_so_far = astar(grid, robot_position, nearest_ball)
                        path_to_nearest_ball = reconstruct_path(came_from, robot_position, nearest_ball)

                        print(path_to_nearest_ball)  # Gives the path from robot to nearest ball

                        #robot moveinggg
                        move_robot(path_to_nearest_ball)
                    except OSError:
                        print("Warning: Pathing algorithm didn't work.")
                        break
        except OSError:
            print("Warning: Cannot receive data from tracking server.")
            break




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