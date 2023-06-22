import socket
import sys
sys.path.append('/Users/Villads/Visualstudio/CDIO2023')
from pynput.keyboard import Key, Listener
import json
import threading
import time 
from Path import find_nearest_ball, reconstruct_path, astar


key_state = {
    "forward": False,
    "backward": False,
    "turn_left": False,
    "turn_right": False,
    "o": False,
    "p": False
}

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

client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

def connect_to_robot():
    global client_socket
    while True:
        try:
            print("Connecting to robot...")
            client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)  # Moved inside the loop to create new socket on reconnection
            client_socket.connect(("192.168.155.146", 1234))  # Replace with your EV3's IP address
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

def receive_tracking_data():
    data = ""
    while True:
        try:
            chunk = tracking_socket.recv(1024).decode()
            data += chunk

            if '\n' in chunk:  # If newline is received
                lines = data.split('\n')

                # If the data ended exactly with '\n', there will be an extra empty line at the end
                if not lines[-1]:  
                    lines.pop()

                # Process each line (each complete message)
                for line in lines:
                    received_data = json.loads(line.rstrip())

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
                                grid[(cross[0])][(cross[1])] = 1  # 1 represents red cross

                            # Find nearest ball
                            
                            nearest_ball = find_nearest_ball(grid, robot_position, white_balls, red_crosses)
                            #balls = white_balls and orange_balls  # if you also consider orange balls

                            print("astar")
                            print(robot_position)
                            print(nearest_ball)
                            came_from, cost_so_far, goal_reached = astar(grid, robot_position, nearest_ball)
                            print("hej")

                            if goal_reached:
                                path_to_nearest_ball = reconstruct_path(came_from, robot_position, nearest_ball)
                                
                            else:
                                print("No valid path to the goal")
                            print(20)
                            print(came_from)
                            print(robot_position)
                            print(nearest_ball)
                            path_to_nearest_ball = reconstruct_path(came_from, tuple(robot_position), nearest_ball)
                            print(path_to_nearest_ball)
                            move_robot(path_to_nearest_ball, orientation)
                            print(22)
                            # Find nearest ball again after moving the robot
                            nearest_ball = find_nearest_ball(grid, robot_position, white_balls, red_crosses)
                            print(23)
                        except OSError:
                            print("Warning: Pathing algorithm didn't work.")
                            break

                # Clean data for next reading
                data = ""
        except OSError:
            print("Warning: Cannot receive data from tracking server.")
            break

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



def reset_key_state():
    key_state['up'] = False
    key_state['down'] = False
    key_state['left'] = False
    key_state['right'] = False
    key_state['o'] = False
    key_state['p'] = False

def move_robot(path_to_nearest_ball, orientation):
    print("did the algo send?1")
    if len(path_to_nearest_ball) > 1:  # If there is at least one move to make
        next_move = path_to_nearest_ball[1]  # We choose the second element because the first one is the current robot's position
        current_pos = path_to_nearest_ball[0]
        slowmode = False
        move = (next_move[0]-current_pos[0], next_move[1]-current_pos[1])  # Calculate the difference to determine the direction
        
        #TODO insert code tht checks if the robot is near a wall/obstacle

        if move == (-1, 0):
            #move west
            if orientation > 357 and orientation < 3:
                key_state["forward"] = True
                key_state["turn_left"] = False
                key_state["turn_right"] = False
            elif orientation < 357 and orientation > 180:
                key_state["forward"] = False
                key_state["turn_left"] = False
                key_state["turn_right"] = True
            elif orientation < 180 and orientation > 3:
                key_state["forward"] = False
                key_state["turn_left"] = True
                key_state["turn_right"] = False
        elif move == (1, 0):
            #move east
            if orientation > 177 and orientation < 183:
                key_state["forward"] = True
                key_state["turn_left"] = False
                key_state["turn_right"] = False
            elif orientation < 177 and orientation > 0:
                key_state["forward"] = False
                key_state["turn_left"] = False
                key_state["turn_right"] = True
            elif orientation < 360 and orientation > 183:
                key_state["forward"] = False
                key_state["turn_left"] = True
                key_state["turn_right"] = False
        elif move == (0, -1):
            #move south
            if orientation > 267 and orientation < 273:
                key_state["forward"] = True
                key_state["turn_left"] = False
                key_state["turn_right"] = False
            elif orientation < 267 and orientation > 90:
                key_state["forward"] = False
                key_state["turn_left"] = False
                key_state["turn_right"] = True
            elif orientation < 90 and orientation > 273:
                key_state["forward"] = False
                key_state["turn_left"] = True
                key_state["turn_right"] = False
        elif move == (0, 1):
            #move north
            if orientation > 87 and orientation < 93:
                key_state["forward"] = True
                key_state["turn_left"] = False
                key_state["turn_right"] = False
            elif orientation < 87 and orientation > 270:
                key_state["forward"] = False
                key_state["turn_left"] = False
                key_state["turn_right"] = True
            elif orientation < 93 and orientation > 270:
                key_state["forward"] = False
                key_state["turn_left"] = True
                key_state["turn_right"] = False
        elif move == (-1, -1):
            #move northwest
            if orientation > 315 and orientation < 360 or orientation >= 0 and orientation < 45:
                key_state["forward"] = True
                key_state["turn_left"] = False
                key_state["turn_right"] = False
            elif orientation < 315 and orientation > 180:
                key_state["forward"] = False
                key_state["turn_left"] = False
                key_state["turn_right"] = True
            elif orientation < 180 and orientation > 45:
                key_state["forward"] = False
                key_state["turn_left"] = True
                key_state["turn_right"] = False
        elif move == (1, 1):
            #move southeast
            if orientation > 135 and orientation < 225:
                key_state["forward"] = True
                key_state["turn_left"] = False
                key_state["turn_right"] = False
            elif orientation < 135 and orientation > 0:
                key_state["forward"] = False
                key_state["turn_left"] = False
                key_state["turn_right"] = True
            elif orientation < 360 and orientation > 225:
                key_state["forward"] = False
                key_state["turn_left"] = True
                key_state["turn_right"] = False
        elif move == (-1, 1):
            #move northeast
            if orientation > 45 and orientation < 135:
                key_state["forward"] = True
                key_state["turn_left"] = False
                key_state["turn_right"] = False
            elif orientation < 45 and orientation >= 0:
                key_state["forward"] = False
                key_state["turn_left"] = False
                key_state["turn_right"] = True
            elif orientation < 360 and orientation > 135:
                key_state["forward"] = False
                key_state["turn_left"] = True
                key_state["turn_right"] = False
        elif move == (1, -1):
            #move southwest
            if orientation > 225 and orientation < 315:
                key_state["forward"] = True
                key_state["turn_left"] = False
                key_state["turn_right"] = False
            elif orientation < 225 and orientation > 90:
                key_state["forward"] = False
                key_state["turn_left"] = False
                key_state["turn_right"] = True
            elif orientation < 90 and orientation > 315:
                key_state["forward"] = False
                key_state["turn_left"] = True
                key_state["turn_right"] = False

    
        
        if slowmode == True:
            key_state["slowmode"] = True
        elif slowmode == False:
            key_state["slowmode"] = False    

    
        # Send the command to the robot
        client_socket.send((json.dumps(key_state) + '\n').encode())
        
        # After 0.5 seconds, stop the robot
        #time.sleep(0.5)
        #reset_key_state()  # You need to define this function
    
        #client_socket.send((json.dumps(key_state) + '\n').encode())
        print("did the algo send? --- yes")

tracking_connection_thread = threading.Thread(target=connect_to_tracking)
tracking_connection_thread.start()











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