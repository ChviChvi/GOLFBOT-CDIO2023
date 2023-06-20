import socket
from pynput.keyboard import Key, Listener
import json
import threading
import time 
#from path import find_nearest_ball, reconstruct_path, astar
#from Robot_Movement import get_orientation_and_target, calculate_distance
#from Robot_Movement2 import find_path
from path import find_nearest_ball, reconstruct_path, astar
from nosidesnomore import danger_zone, Moving_back, Turning
from find_goal import rotate, release_balls



key_state = {
    "forward": False,
    "backward": False,
    "turn_left": False,
    "turn_right": False,
    "o": False,
    "p": False
}
# def on_press(key):
#     print(f"Key pressed: {key}")
#     try:
#         if key.char == 'o':
#             key_state['o'] = True
#         elif key.char == 'p':
#             key_state['p'] = True
#     except AttributeError:
#         if key == Key.up:
#             key_state['up'] = True
#         elif key == Key.down:
#             key_state['down'] = True
#         elif key == Key.left:
#             key_state['left'] = True
#         elif key == Key.right:
#             key_state['right'] = True
#     client_socket.send((json.dumps(key_state) + '\n').encode())

# def on_release(key):

#     try:
#         if key.char == 'o':
#             key_state['o'] = False
#         elif key.char == 'p':
#             key_state['p'] = False
#     except AttributeError:
#         if key == Key.up:
#             key_state['up'] = False
#         elif key == Key.down:
#             key_state['down'] = False
#         elif key == Key.left:
#             key_state['left'] = False
#         elif key == Key.right:
#             key_state['right'] = False
#     client_socket.send((json.dumps(key_state) + '\n').encode())

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

def receive_tracking_data():
    
    data = ""

    robot_turnto = None
    ball_target = None
    calculation = False
    facing_ball = False
    reached_ball = False
    Balls_container = 0
    
    #trying sometihng else
    path = None

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
                for line in lines[:-1]:
                    #3print("begin line")
                    #print(line)
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
                        #print(f"Received white balls positions: {white_balls}")
                        Balls_container = 10 -len(white_balls) 

                    if 'orange_balls' in received_data:
                        orange_balls = received_data["orange_balls"]
                        #print(f"Received orange balls positions: {orange_balls}")

                    if 'robot' in received_data:
                        robot_position = received_data['robot']
                        print(f"Received robot position: {robot_position}")

                    if 'grid_size' in received_data:
                        grid_size = received_data["grid_size"]
                        print(f"SIZE OF THE GRID IS: {grid_size}")

                    if 'orientation' in received_data:
                        orientation = round(received_data["orientation"])
                        print(f"orientation is (90 is north): {orientation}")
                        print("-------------- CALCULATION FROM HERE ------------")

                    grid = [[0 for _ in range(grid_size[0])] for _ in range(grid_size[1])]
                    print(red_crosses)
                    

                    for cross in red_crosses:
                        grid[(cross[0])][(cross[1])] = 1 

                    '''        
                    for i in range(2):
                       for j in range(grid_size[0]):
                            grid[j][i]=1

                    for i in range(2):
                        for j in range(grid_size[1]):
                            grid[i][j]=1
                            
                    for i in range(2):
                        for j in range(grid_size[1]):
                            grid[grid_size[1]-i][j]=1

                    for i in range(2):
                        for j in range(grid_size[0]):
                            grid[j][(grid_size[1])-i-1]=1
                    '''
                    try:
                    
                        #path = find_path(grid_size, robot_position, white_balls, orange_balls,red_crosses)
                        #move_robot(path, orientation)
                        in_danger, white_balls, zone = danger_zone(grid_size, robot_position, white_balls)
                        print(f"Received white balls positions: {white_balls}")

                        if in_danger:
                            print("IM IN DANGER ZONE")    
                            if zone is not "Safe":
                                print("IM IN DANGER ZONE - TURNING")
                                key_state = Turning(zone, orientation)
                            elif zone is "Safe":
                                print("IM IN DANGER ZONE - BACKING")
                                key_state = Moving_back()

                            client_socket.send((json.dumps(key_state) + '\n').encode())

                        while Balls_container == 2:
                            goal = (grid_size[0]-20,grid_size[1]/2)
                            print("TO THE GOAL")
                            came_from, cost_so_far, goal_reached = astar(grid, robot_position, goal)
                            path_to_goal = reconstruct_path(came_from, tuple(robot_position), goal)
                            move_robot(path_to_goal, orientation)

                            if goal[0] -5 < robot_position[0] < goal[0]+5 and goal[1] -5 < robot_position[1] < goal[1]+5:
                                key_state=rotate()
                                client_socket.send((json.dumps(key_state) + '\n').encode())
                                if 0 <= orientation <= 5 or 345 <= orientation <= 360:
                                    key_state = release_balls()
                                    client_socket.send((json.dumps(key_state) + '\n').encode())





                        else:
                            nearest_ball = find_nearest_ball(grid, robot_position, white_balls, red_crosses)
                            came_from, cost_so_far, goal_reached = astar(grid, robot_position, nearest_ball)
                            print("nearest ball: ", nearest_ball)
                            
                            # TODO error here
                            
                            path_to_nearest_ball = reconstruct_path(came_from, tuple(robot_position), nearest_ball)
                            print("1 step", path_to_nearest_ball[0])
                            print("2 step: ", path_to_nearest_ball[1])
                            print("goal: ", path_to_nearest_ball[len(path_to_nearest_ball)-1])                               
                            print("robot position:", robot_position)
                            print("orientation:", orientation)
                            move_robot(path_to_nearest_ball, orientation)
                        
                    

                        
                        # Here we find which way the robot has to turn, and to which coordinate that is
                        #elif not calculation:#robot_turnto is None and ball_target is None:
                            #print("-------------- IF ORIENTATION ------------")
                            #path = find_path(grid_size, robot_position, white_balls, orange_balls,red_crosses)
                            
                            #print(f"path to nearest ball!!!!! ------------ {path}")
                            #if path is not None:
                                # calculation = True
                            # if not calculation:
                            #     print("-------------- IF ORIENTATION ------------")
                            #     robot_turnto, ball_target = get_orientation_and_target(robot_position, orientation, grid_size, white_balls, orange_balls, red_crosses)
                            #     print(f"the robot has to turn to: {robot_turnto}")
                            #     print(f"the ball he is going to: {ball_target}")
                            #     #robot_turnto = robot_turnto + 180 %360
                            #     calculation = True
                            #     facing_ball = False
                        # here we check if the robot has reached

                        #elif calculation:
                            #if robot_position == path[1]:
                            #    path.pop
                            #move_robot(path, orientation)
                    
                        # elif not facing_ball:
                        #     if orientation is not None and robot_turnto is not None:
                        #         print("-------------- IF TURNING ------------")
                                
                        #         key_state, facing_ball = align_orientation(orientation, robot_turnto, facing_ball)
                            
                        #         client_socket.send((json.dumps(key_state) + '\n').encode())
                        # # handling the robot moving forward.
                        # elif facing_ball:
                        #     #check if robot front is still sending front TODO
                        #     if robot_position is not None and ball_target is not None:
                        #         key_state, reached_ball = move_to_target(robot_position, ball_target, reached_ball)
                        #         print("MOVING")
                        #         facing_ball = False
                        #         client_socket.send((json.dumps(key_state) + '\n').encode())
                        #         if reached_ball:
                        #             robot_turnto = None
                        #             ball_target = None
                        #             reached_ball = False
                        #             calculation = False

                        # # Initialize grid
                        # grid = [[0 for _ in range(grid_size[1])] for _ in range(grid_size[0])]

                        # # Mark red crosses on the grid
                        
                        # for cross in red_crosses:
                        #     grid[(cross[0])][(cross[1])] = 1  # 1 represents red cross

                        # # Find nearest ball
                        
                        # nearest_ball = find_nearest_ball(grid, robot_position, white_balls, red_crosses)
                        # #balls = white_balls and orange_balls  # if you also consider orange balls

                        # #print("astar")
                        # #print(robot_position)
                        # #print(nearest_ball)
                        # came_from, cost_so_far, goal_reached = astar(grid, robot_position, nearest_ball)
                        # #print("hej")

                        # #print(f'came_from: {came_from}')
                        # #print("error is in position")
                        # #print(f'current node: {tuple(robot_position)}')
                        # #print("error is in nearest ball")
                        # #print(f'target node: {nearest_ball}')
                        # print(f"the goal: {goal_reached}")
                        # if goal_reached:
                            
                        #     path_to_nearest_ball = reconstruct_path(came_from, robot_position, nearest_ball)
                            
                        # else:
                        #     print("No valid path to the goal")
                        #     continue
                        # print(20)
                        # #print(came_from)
                        # print("ROBOT POSITION")
                        # print(robot_position)
                        # #print(nearest_ball)
                        # #path_to_nearest_ball = reconstruct_path(came_from, tuple(robot_position), nearest_ball)
                        # #print(path_to_nearest_ball)

                        # print("ARE WE MOVING THE ROBOT??")
                        # print("ARE WE MOVING THE ROBOT??")
                        # print("ARE WE MOVING THE ROBOT??")
                        # move_robot(path_to_nearest_ball, orientation)
                        # print(22)
                        # # Find nearest ball again after moving the robot
                        # nearest_ball = find_nearest_ball(grid, robot_position, white_balls, red_crosses)
                        # print(23)
                    except OSError:
                        print("WARNING: robot algorithm didnt work, so no movement.")
                        continue

                # Clean data for next reading
                    data = lines[-1]
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

## MOVES ROBOT
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
    
    # Calculate the current distance to the target
    distance_to_target = calculate_distance(robot_position, ball_target)

    # If the distance to the target is small enough, stop moving and wait for 5 seconds
    if distance_to_target < 3:
        time.sleep(5)  # Wait for 5 seconds
        reached_ball = True
        Balls_container = Balls_container + 1
        return key_state, reached_ball

    # Otherwise, move forward
    key_state["forward"] = True

    return key_state, reached_ball


## TURNS ROBOT
def align_orientation(robot_orientation, target_orientation, facing_ball):
    # Create a key_state dictionary
    key_state = {
        "forward": False,
        "turn_left": False,
        "turn_right": False,
        "backward": False,
        "slowmode": False,
        "o": False,
        "p": False,
    }

    # Calculate the difference between the current and target orientation
    orientation_diff = (target_orientation - robot_orientation) % 360
    
    # Adjust for the shorter path around the circle
    # if orientation_diff > 180:
    #     orientation_diff -= 360

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

    # Determine if it's shorter to turn left or right
    if orientation_diff > 180:
        # Turn left
        key_state["turn_left"] = True
    elif orientation_diff <= 180:
        # Turn right
        key_state["turn_right"] = True

    # # Set slowmode if the robot needs to make a small turn
    # if abs(orientation_diff) < 30:
    #     key_state["slowmode"] = True

    
    #key_state["turn_right"] = True

    return key_state, facing_ball

def convert_path_to_directions1(path):
    directions = []
    for i in range(1, len(path)):
        current = path[i - 1]
        next_pos = path[i]
        dx = next_pos[0] - current[0]
        dy = next_pos[1] - current[1]
        if dx == 0:
            direction = (0, 1 if dy > 0 else -1)
        elif dy == 0:
            direction = (1 if dx > 0 else -1, 0)
        else:
            direction = (1 if dx > 0 else -1, 1 if dy > 0 else -1)
        directions.append(direction)
    return directions

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




def move_robot(path_to_nearest_ball, orientation):

    #print(f"path to nearest ball ------------ {path_to_nearest_ball}")
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
        # next_move = directions[2]  # We choose the second element because the first one is the current robot's position
        # current_pos = directions[1]
        # print(f"next_move {next_move}")
        # print(f"current_pos {current_pos}")
        # slowmode = False
        #move = (next_move[0]-current_pos[0], next_move[1]-current_pos[1])  # Calculate the difference to determine the direction
        move = directions
        print(f"MOVING: {move}")
        #TODO insert code tht checks if the robot is near a wall/obstacle

        if move[0] == -1 and move[1] == 0: # move West
            print("direction: West")
            if 357 < orientation or orientation < 3:
                print("forward")
                key_state["forward"] = True
                key_state["turn_left"] = False
                key_state["turn_right"] = False
            elif 180 < orientation < 357:
                print("turn_right")
                key_state["forward"] = False
                key_state["turn_left"] = False
                key_state["turn_right"] = True
            elif 3 < orientation < 180:
                print("turn_left")
                key_state["forward"] = False
                key_state["turn_left"] = True
                key_state["turn_right"] = False
        elif move[0] == 1 and move[1] == 0: # move East
            print("direction: East")
            if 177 < orientation < 183:
                print("forward")
                key_state["forward"] = True
                key_state["turn_left"] = False
                key_state["turn_right"] = False
            elif 0 < orientation < 177:
                print("turn_right")
                key_state["forward"] = False
                key_state["turn_left"] = False
                key_state["turn_right"] = True
            elif 183 < orientation < 360:
                print("turn_left")
                key_state["forward"] = False
                key_state["turn_left"] = True
                key_state["turn_right"] = False
        elif move[0] == 0 and move[1] == -1: # move South
            print("direction: South")
            if 267 < orientation < 273:
                print("forward")
                key_state["forward"] = True
                key_state["turn_left"] = False
                key_state["turn_right"] = False
            elif 90 < orientation < 267:
                print("turn_right")
                key_state["forward"] = False
                key_state["turn_left"] = False
                key_state["turn_right"] = True
            elif 273 < orientation or orientation < 90: # Corrected
                print("turn_left")
                key_state["forward"] = False
                key_state["turn_left"] = True
                key_state["turn_right"] = False
        elif move[0] == 0 and move[1] == 1: # move North
            print("direction: North")
            print("WE ARE IN HERE BOYS")
            print(f"orientation : {orientation}")
            if 87 < orientation < 93:
                print("forward")
                print("WE ARE IN HERE BOYS1")
                key_state["forward"] = True
                key_state["turn_left"] = False
                key_state["turn_right"] = False
            elif orientation < 87 or orientation > 270: # Corrected
                print("WE ARE IN HERE BOYS2")
                print("turn_right")
                key_state["forward"] = False
                key_state["turn_left"] = False
                key_state["turn_right"] = True
            elif 93 < orientation < 270: # Corrected
                print("turn_left")
                print("WE ARE IN HERE BOYS3")
                key_state["forward"] = False
                key_state["turn_left"] = True
                key_state["turn_right"] = False
        elif move[0] == -1 and move[1] == -1: # move Northwest
            print("direction: Northwest")
            if 315 < orientation < 360 or 0 <= orientation < 45:
                print("forward")
                key_state["forward"] = True
                key_state["turn_left"] = False
                key_state["turn_right"] = False
            elif 180 < orientation < 315:
                print("turn_right")
                key_state["forward"] = False
                key_state["turn_left"] = False
                key_state["turn_right"] = True
            elif 45 < orientation < 180:
                print("turn_left")
                key_state["forward"] = False
                key_state["turn_left"] = True
                key_state["turn_right"] = False
        elif move[0] == 1 and move[1] == 1: # move Southeast
            print("direction: Southeast")
            if 135 < orientation < 225:
                print("forward")
                key_state["forward"] = True
                key_state["turn_left"] = False
                key_state["turn_right"] = False
            elif 0 < orientation < 135:
                print("turn_right")
                key_state["forward"] = False
                key_state["turn_left"] = False
                key_state["turn_right"] = True
            elif 225 < orientation < 360:
                print("turn_left")
                key_state["forward"] = False
                key_state["turn_left"] = True
                key_state["turn_right"] = False
        elif move[0] == -1 and move[1] == 1: # move Northeast
            print("direction: Northeast")
            if 45 < orientation < 135:
                print("forward")
                key_state["forward"] = True
                key_state["turn_left"] = False
                key_state["turn_right"] = False
            elif 0 <= orientation < 45:
                print("turn_right")
                key_state["forward"] = False
                key_state["turn_left"] = False
                key_state["turn_right"] = True
            elif 135 < orientation < 360:
                print("turn_left")
                key_state["forward"] = False
                key_state["turn_left"] = True
                key_state["turn_right"] = False
        elif move[0] == 1 and move[1] == -1: # move Southwest
            print("direction: Southwest")
            if 225
             < orientation < 315:
                print("forward")
                key_state["forward"] = True
                key_state["turn_left"] = False
                key_state["turn_right"] = False
            elif 90 < orientation < 225:
                print("turn_right")
                key_state["forward"] = False
                key_state["turn_left"] = False
                key_state["turn_right"] = True
            elif 315 < orientation or orientation < 90: # Corrected
                print("turn_left")
                key_state["forward"] = False
                key_state["turn_left"] = True
                key_state["turn_right"] = False


    
        
        # if slowmode == True:
        #     key_state["slowmode"] = True
        # elif slowmode == False:
        #     key_state["slowmode"] = False    

    
        # Send the command to the robot
        client_socket.send((json.dumps(key_state) + '\n').encode())
        
        # After 0.5 seconds, stop the robot
        #time.sleep(0.5)
        #reset_key_state()  # You need to define this function
    
        #client_socket.send((json.dumps(key_state) + '\n').encode())


        

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