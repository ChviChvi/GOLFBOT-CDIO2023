import socket
from pynput.keyboard import Key, Listener
import json
import threading
import time 
from path import find_nearest_ball, reconstruct_path, astar
from nosidesnomore import danger_zone, Moving_back, Turning
from find_goal import rotate, release_balls
import math


key_state = {
    "forward": False,
    "backward": False,
    "turn_left": False,
    "turn_right": False,
    "o": False,
    "p": False
}

client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

def connect_to_robot():
    global client_socket
    while True:
        try:
            print("Connecting to robot...")
            client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)  
            client_socket.connect(("192.168.155.146", 1234))  # EV3's IP address
            print("Connected to robot!")
            
            while True:  # Check for active connection
                try:
                    client_socket.send(json.dumps({'ping': True}).encode())  
                    time.sleep(20)  
                except Exception as e:  
                    print(f"Lost connection to robot: {e}")
                    break  
        except ConnectionRefusedError:
            print("Failed to connect to robot. Retrying in 5 seconds...")
        except Exception as e:  
            print(f"Unexpected error while connecting to robot: {e}")
        time.sleep(5)

robot_connection_thread = threading.Thread(target=connect_to_robot)
robot_connection_thread.start()

grid2 = None
red_crosses = None
white_balls = None

def receive_tracking_data():
    
    data = ""

    robot_turnto = None
    ball_target = None
    calculation = False
    facing_ball = False
    reached_ball = False
    Balls_container = 0
    red_crosses = None
    grid_size = None
    robot_position = None
    white_balls = None
    goal_point = None
    came_from = None
    robot_position_basket = None
    nearest_ball_basket = None
    goal_basket = None

    start_time = time.time()

    came_from_counter = 0
    turning_flag = False
    move = None
    
    #trying sometihng else
    path = None

    while True:
        try:
            chunk = tracking_socket.recv(1024).decode()
            data += chunk

            if '\n' in chunk:  # If newline is received
                lines = data.split('\n')

                if not lines[-1]:  
                    lines.pop()

                for line in lines:
                    try:
                        received_data = json.loads(line.rstrip())
                    except json.JSONDecodeError:
                        print(f"Unable to parse JSON for line: {line}")
                        continue

                    #print("end line")
                    received_data = json.loads(line.rstrip())
                    print("-------------- INCOMMING DATA ------------")
                    if 'red_crosses' in received_data:
                        red_crosses = received_data["red_crosses"]
                        #print(f"THE RED CROSS IS AT: {red_crosses}")

                    if 'white_balls' in received_data:
                        white_balls = received_data["white_balls"]
                        Balls_container = 10 #-len(white_balls) 

                    if 'orange_balls' in received_data:
                        orange_balls = received_data["orange_balls"]
                        #print(f"Received orange balls positions: {orange_balls}")

                    if 'robot' in received_data:
                        robot_position = received_data['robot']
                        print(f"Received robot position: {robot_position}")

                    if 'grid_size' in received_data:
                        grid_size = received_data["grid_size"]
                        print(f"SIZE OF THE GRID IS: {grid_size}")

                    if 'goal_point' in received_data:
                        goal_point = received_data["goal_point"]
                        print(f"LOCATION OF GOAL IS: {goal_point}")

                    if 'orientation' in received_data:
                        orientation = received_data["orientation"]
                        print(f"orientation is (90 is north): {orientation}")
                        print("-------------- CALCULATION FROM HERE ------------")

                    
                        
                    if grid_size is not None:
                        
                        grid = [[0 for _ in range(grid_size[0])] for _ in range(grid_size[1])]
                       
                    if red_crosses is not None:
                        
                        for cross in red_crosses:
                            if 0 <= cross[0] < grid_size[1] and 0 <= cross[1] < grid_size[0]:  
                                grid[cross[0]][cross[1]] = 1

                    if white_balls is not None:
                        for white_ball in white_balls[:]:  
                            for red_cross in red_crosses:
                                distance = ((white_ball[0] - red_cross[0]) ** 2 + (white_ball[1] - red_cross[1]) ** 2) ** 0.5
                                if distance <= 5:
                                    white_balls.remove(white_ball)
                                    break

                    try:
                        if grid_size is not None and red_crosses is not None and robot_position is not None and white_balls is not None and goal_point is not None:
                            
                            in_danger, white_balls, zone = danger_zone(grid_size, robot_position, white_balls)
                            print(f"Received white balls positions: {white_balls}")
                            print(f"Received goal positions: {goal_point}")
                            print(f"Received robot positions: {robot_position}")

                            walkup = 10
                            if goal_point[0] > grid_size[0]/2:
                                goal_point1 = [goal_point[0]-walkup,goal_point[1]]
                            else:
                                goal_point1 = [goal_point[0]+walkup,goal_point[1]]
                            elapsed_time = time.time() - start_time
                            print(f"SECOND! : {elapsed_time}")
                            if Balls_container == 2 or len(white_balls) < 1 or elapsed_time > 300  :

                                goal_point_list = [goal_point1]
                                goal_point_list.append(goal_point1)
                                print(f"Received goal positions: {goal_point_list}")
                                goal = find_nearest_ball(grid, robot_position, goal_point_list, red_crosses)
                                
                                print("TO THE GOAL", goal)
                                
                                came_from = astar(grid, robot_position, tuple(goal))

                                robot_position_basket = robot_position
                                goal_basket = goal

                                path_to_nearest_ball = reconstruct_path(came_from, tuple(robot_position), tuple(goal))

                            
                            
                                move_robot(path_to_nearest_ball, orientation)

                                margin_x = 20
                                margin_y = 10

                                # Check if the robot position is within the margins of the goal point
                                if abs(robot_position[0] - goal_point[0]) <= margin_x and abs(robot_position[1] - goal_point[1]) <= margin_y:
                                    print("The robot is within the goal margin.")
                                    key_state=rotate(orientation, walkup)
                                    client_socket.send((json.dumps(key_state) + '\n').encode())
                                    if walkup < 0:

                                        if 0 <= orientation <= 2 or 358 <= orientation <= 360:
                                            time.sleep(5) 
                                            key_state = release_balls()
                                            client_socket.send((json.dumps(key_state) + '\n').encode())
                                    else:
                                        if 178 <= orientation <= 181:
                                            time.sleep(5) 
                                            key_state = release_balls()
                                            client_socket.send((json.dumps(key_state) + '\n').encode())
                                else:
                                    print("The robot is not within the goal margin.")

                                
                            

                            elif in_danger:
                                print("IM IN DANGER ZONE")    
                                key_state = Turning(zone, orientation)
                                client_socket.send((json.dumps(key_state) + '\n').encode())

                            else:
                                print("ROBOT POSITION :", robot_position)
                                print("WHITE BALLS :", white_balls)
                                nearest_ball = find_nearest_ball(grid, robot_position, white_balls, red_crosses)
                                print("NEAREST BALL :", nearest_ball)

                                if came_from_counter < 1:
                                    came_from = astar(grid, robot_position, nearest_ball)
                                    came_from_counter = 30

                                came_from_counter = came_from_counter - 1
                                robot_position_basket = robot_position
                                nearest_ball_basket = nearest_ball
                                path_to_nearest_ball = reconstruct_path(came_from, tuple(robot_position), tuple(nearest_ball))

                                move_robot(path_to_nearest_ball, orientation)


                    except OSError:
                        print("WARNING: robot algorithm didnt work, so no movement.")
                        continue
                    
                    data = ''
        except OSError:
            print("Warning: Cannot receive data from tracking server.")
            break

tracking_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

def connect_to_tracking():
    global tracking_socket
    while True:
        try:
            print("Connecting to tracking...")
            tracking_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)  
            tracking_socket.connect(("localhost", 1235))
            print("Connected to tracking!")
            print("Client started. Press arrow keys to control the EV3 brick.")
            print("Press O and P to control the second medium motor.")
            print("Press Ctrl+C to stop the client.")
            threading.Thread(target=receive_tracking_data, daemon=True).start()  
            while True: 
                try:
                    tracking_socket.send(b'ping')  
                    time.sleep(5)  
                except Exception as e:  
                    print(f"Lost connection to tracking: {e}")
                    break  # Break the inner loop to reconnect
        except ConnectionRefusedError:
            print("Failed to connect to tracking. Retrying in 5 seconds...")
        except Exception as e:  
            print(f"Unexpected error while connecting to tracking: {e}")
        time.sleep(5)

# not used
def reset_key_state():
    key_state['up'] = False
    key_state['down'] = False
    key_state['left'] = False
    key_state['right'] = False
    key_state['o'] = False
    key_state['p'] = False

def calculate_distance(point1, point2):
    return math.sqrt((point1[0] - point2[0])**2 + (point1[1] - point2[1])**2)

#not used
def move_to_target(robot_position, ball_target, reached_ball):
    key_state = {
        "forward": False,
        "turn_left": False,
        "turn_right": False,
        "backward": False,
        "slowmode": False,
        "o": False,
        "p": False,
    }
    

    distance_to_target = calculate_distance(robot_position, ball_target)

    if distance_to_target < 3:
        time.sleep(5)  # Wait for 5 seconds
        reached_ball = True
        Balls_container = Balls_container + 1
        return key_state, reached_ball


    key_state["forward"] = True

    return key_state, reached_ball

## TURNS ROBOT not used..
def align_orientation(robot_orientation, target_orientation, facing_ball):
    key_state = {
        "forward": False,
        "turn_left": False,
        "turn_right": False,
        "backward": False,
        "slowmode": False,
        "o": False,
        "p": False,
    }

    orientation_diff = (target_orientation - robot_orientation) % 360
    print(f"-------------- ROBOT ORIENTATION: {robot_orientation} ------------")
    print(f"-------------- TARGET ORIENTATION: {target_orientation} ------------")
    print(f"-------------- ORIENTATION DIFF: {orientation_diff} ------------")
    # If the difference is small, stop turning
    print(f"BALL FACING? {facing_ball}")
    if abs(orientation_diff) < 3:
        print("-------------- TARGET AQUIRED ------------")
        facing_ball = True
        key_state["turn_right"] = False
        key_state["turn_left"] = False
        print(f"BALL FACING? {facing_ball}")
        time.sleep(2)
        return key_state, facing_ball

    if orientation_diff > 180:
        key_state["turn_left"] = True
    elif orientation_diff <= 180:
        key_state["turn_right"] = True

    return key_state, facing_ball

def convert_path_to_directions(path):
    if len(path) > 1:
        current = path[0]
        next_pos = path[1]
        dx = next_pos[0] - current[0]
        dy = next_pos[1] - current[1]
        if dx == 0:
            direction = (0, 1 if dy > 0 else -1)  # moving vertically
        elif dy == 0:
            direction = (1 if dx > 0 else -1, 0)  # moving horizontally
        else:
            direction = (1 if dx > 0 else -1, 1 if dy > 0 else -1)  # moving diagonally
        print(f'DIRECTIOON!{direction}')
        return direction
    else:
        raise ValueError('Path should contain at least two points.')

def turning(move, orientation):
    # Determine the target orientation
    target_orientation = math.degrees(math.atan2(move[1], move[0]))
    target_orientation = (target_orientation + 360) % 360  
    
    key_state = {
        "forward": False,
        "turn_left": False,
        "turn_right": False,
        "backward": False,
        "slowmode": False,
        "o": False,
        "p": False,
    }
    
    # Check if the orientation is within the margin
    if abs(orientation - target_orientation) <= 3:
        turning_flag = True
    else:
        turning_flag = False

        if abs(orientation - target_orientation) <= 180:
            if orientation < target_orientation:
                key_state["turn_right"] = True
            else:
                key_state["turn_left"] = True
        else:
            if orientation < target_orientation:
                key_state["turn_left"] = True
            else:
                key_state["turn_right"] = True

    client_socket.send((json.dumps(key_state) + '\n').encode())
    return turning_flag

def move_robot(path_to_nearest_ball, orientation):

    key_state = {
        "forward": False,
        "turn_left": False,
        "turn_right": False,
        "backward": False,
        "slowmode": False,
        "o": False,
        "p": False,
    }
    if not path_to_nearest_ball or len(path_to_nearest_ball) <= 1:
        print("No valid path or no moves to make.")
        return  # Here you can decide what the robot should do if there's no valid path

    
    if len(path_to_nearest_ball) > 1:  # If there is at least one move to make
        directions = convert_path_to_directions(path_to_nearest_ball)
        move = directions
        print(f"MOVING: {move}")

        if move[0] == -1 and move[1] == 0: # move West
            print("direction: West")
            if 345 < orientation or orientation < 15:  # Changed
                print("forward")
                key_state["forward"] = True
                key_state["turn_left"] = False
                key_state["turn_right"] = False
            elif 165 < orientation < 346:  # Changed
                print("turn_right")
                key_state["forward"] = False
                key_state["turn_left"] = False
                key_state["turn_right"] = True
            elif 14 < orientation < 166:  # Changed
                print("turn_left")
                key_state["forward"] = False
                key_state["turn_left"] = True
                key_state["turn_right"] = False
        elif move[0] == 1 and move[1] == 0: # move East
            print("direction: East")
            if 165< orientation < 195:  # Changed
                print("forward")
                key_state["forward"] = True
                key_state["turn_left"] = False
                key_state["turn_right"] = False
            elif 0 < orientation < 166:  # Changed
                print("turn_right")
                key_state["forward"] = False
                key_state["turn_left"] = False
                key_state["turn_right"] = True
            elif 194 < orientation < 360:  # Changed
                print("turn_left")
                key_state["forward"] = False
                key_state["turn_left"] = True
                key_state["turn_right"] = False
        elif move[0] == 0 and move[1] == -1: # move South
            print("direction: South")
            if 255 < orientation < 285:  # Changed
                print("forward")
                key_state["forward"] = True
                key_state["turn_left"] = False
                key_state["turn_right"] = False
            elif 75 < orientation < 256:  # Changed
                print("turn_right")
                key_state["forward"] = False
                key_state["turn_left"] = False
                key_state["turn_right"] = True
            elif 284 < orientation or orientation < 76:  # Changed
                print("turn_left")
                key_state["forward"] = False
                key_state["turn_left"] = True
                key_state["turn_right"] = False
        elif move[0] == 0 and move[1] == 1: # move North
            print("direction: North")
            print(f"orientation : {orientation}")
            if 75 < orientation < 105:  # Changed
                print("forward")
                key_state["forward"] = True
                key_state["turn_left"] = False
                key_state["turn_right"] = False
            elif orientation < 76 or orientation > 255:  # Changed
                print("WE ARE IN HERE BOYS2")
                print("turn_right")
                key_state["forward"] = False
                key_state["turn_left"] = False
                key_state["turn_right"] = True
            elif 104 < orientation < 256:  # Changed
                print("turn_left")
                key_state["forward"] = False
                key_state["turn_left"] = True
                key_state["turn_right"] = False
        elif move[0] == -1 and move[1] == 1: # move Northwest
            print("direction: Northwest")
            if 30 < orientation < 60:  # Changed
                print("forward")
                key_state["forward"] = True
                key_state["turn_left"] = False
                key_state["turn_right"] = False
            elif 0 < orientation < 31 or 210 < orientation < 360:  # Changed
                print("turn_right")
                key_state["forward"] = False
                key_state["turn_left"] = False
                key_state["turn_right"] = True
            elif 59 < orientation < 211:  # Changed
                print("turn_left")
                key_state["forward"] = False
                key_state["turn_left"] = True
                key_state["turn_right"] = False
        elif move[0] == -1 and move[1] == -1: # move Southwest
            print("direction: Southwest")
            if 300 < orientation < 330:  # Changed
                print("forward")
                key_state["forward"] = True
                key_state["turn_left"] = False
                key_state["turn_right"] = False
            elif 330 < orientation < 360 or 0 < orientation < 120 :  # Changed
                print("turn_left")
                key_state["forward"] = False
                key_state["turn_left"] = True
                key_state["turn_right"] = False
            elif 120 < orientation < 300:  # Changed
                print("turn_right")
                key_state["forward"] = False
                key_state["turn_left"] = False
                key_state["turn_right"] = True
        elif move[0] == 1 and move[1] == 1: # move Northeast
            print("direction: Northeast")
            if 120 < orientation < 150:  # Changed
                print("forward")
                key_state["forward"] = True
                key_state["turn_left"] = False
                key_state["turn_right"] = False
            elif 0 < orientation < 121 or 300 < orientation < 360:  # Changed
                print("turn_right")
                key_state["forward"] = False
                key_state["turn_left"] = False
                key_state["turn_right"] = True
            elif 149 < orientation < 301:  # Changed
                print("turn_left")
                key_state["forward"] = False
                key_state["turn_left"] = True
                key_state["turn_right"] = False
        elif move[0] == 1 and move[1] == -1: # move Southeast
            print("direction: Southeast")  # Corrected from Southwest
            if 210 < orientation < 240:  # Changed
                print("forward")
                key_state["forward"] = True
                key_state["turn_left"] = False
                key_state["turn_right"] = False
            elif 30 < orientation < 211:  # Changed
                print("turn_right")
                key_state["forward"] = False
                key_state["turn_left"] = False
                key_state["turn_right"] = True
            elif 239 < orientation < 360 or 0 < orientation < 31:  # Changed
                print("turn_left")
                key_state["forward"] = False
                key_state["turn_left"] = True
                key_state["turn_right"] = False


        client_socket.send((json.dumps(key_state) + '\n').encode())

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

    