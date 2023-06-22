import socket
import threading
import cv2
import numpy as np
import time
import json
from collections import deque
import math
import matplotlib.pyplot as plt
import matplotlib.patches as patches
import itertools


# Global flag
is_exiting = False
# Connects to Robot_Client
def wait_for_connection():
    global client_socket
    global is_exiting
    while True:
        if is_exiting:
            break
        try:
            print("Waiting for connection...")
            client_socket, addr = server_socket.accept()
            print(f"Connection made with {addr}.")
            connection_event.set()
            break
        except Exception as e:
            if not is_exiting:
                print(f"Error: {e}")
            time.sleep(1)

server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
# Bind the socket to a specific network interface and port number
server_socket.bind(("localhost", 1235))
# Tell the operating system to add the socket to the list of sockets
# that should be actively listening for incoming connections.
server_socket.listen(1)
# Start a new thread that waits for a client to connect
client_socket = None
connection_event = threading.Event()  # Create a new threading Event
connection_thread = threading.Thread(target=wait_for_connection)
connection_thread.start()

def get_center_of_contour(contour):
    M = cv2.moments(contour)
    if M["m00"] == 0:
        return None
    else:
        return (int(M["m10"] / M["m00"]), int(M["m01"] / M["m00"]))

def get_hsv_values(frame):
    
    # Display the frame in its original BGR colors
    cv2.imshow("Image", frame)

    point = cv2.selectROI("Image", frame, fromCenter=False, showCrosshair=True)
    cv2.destroyAllWindows()

    # Extract the selected pixel
    x, y = point[:2]
    hsv_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
    hsv_values = hsv_frame[y, x]

    return hsv_values

def quantize_coordinates(coordinates, cell_size):
    return [int(coord / cell_size) for coord in coordinates]

#   This function draws the 4 cornes at the start
def draw_ROI(frame):
    # Convert the frame to RGB for display
    frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

    fig, ax = plt.subplots(1, figsize=(8, 6))
    ax.imshow(frame_rgb)

    points = plt.ginput(5)

    if len(points) == 5:
        # Convert the ROI to a numpy array
        ROI = np.array(points[:4], dtype=np.float32)
        extra_point = np.array(points[4], dtype=np.float32) 

        min_x = np.min(ROI[:, 0])
        max_x = np.max(ROI[:, 0])
        min_y = np.min(ROI[:, 1])
        max_y = np.max(ROI[:, 1])

        ROI[:, 0] -= min_x
        ROI[:, 1] -= min_y

        ROI = np.round(ROI).astype(np.int32)

        translate_x = int(min_x)
        translate_y = int(min_y)

        ROI[:, 0] += translate_x
        ROI[:, 1] += translate_y

        ROI = np.vstack([ROI, ROI[0]])

        rect = patches.Polygon(ROI, linewidth=1, edgecolor='r', facecolor='none')
        ax.add_patch(rect)

        ax.scatter(ROI[:-1, 0], ROI[:-1, 1], c='r', s=10)
        ax.scatter([extra_point[0]], [extra_point[1]], c='b', s=50, marker='x')

        plt.show()
    else:
        print("No valid points were selected.")
        return None, None

    return ROI, extra_point


print("Waiting for camera...")
cap = cv2.VideoCapture(1,cv2.CAP_DSHOW)
print("Camera is on!")

hsv_ranges = {}
colors = ["FRONTSIDE_ROBOT_CONTOURS", "BACKSIDE_ROBOT", "RED_CROSS_1", "RED_CROSS_2", "RED_CROSS_3", "RED_CROSS_4", "WHITE_BALL_1","WHITE_BALL_2","WHITE_BALL_3","WHITE_BALL_4", "ORANGE_BALL5"]
balls_position = []
orange_balls_position = []
robot_position = None
robot_angle = None
red_cross_centers = None
frame_corners = None
extra_point = None

cell_size = 1

last_send_time = time.time()
last_robot_print_time = time.time()
last_print_time = time.time()

last_send_time_data1 = 0
last_send_time_data2 = 0
last_send_time_data3 = 0

# these two functions calculate the degrees > if it return 0 is is looking east, 90 north etc.
def get_vector(p1, p2):
    if p1 is None or p2 is None:
        return None
    dx = p2[0] - p1[0]
    dy = p2[1] - p1[1]
    return dx, dy

def calculate_orientation(vector):
    x, y = vector
    rad = math.atan2(y, x)  
    deg = math.degrees(rad) 

    # Adjust the degrees to be in the range [0, 360)
    if deg < 0:
        deg = 360 + deg
    
    return deg

threshold_verify = 1

balls_counter = {}
balls_absence_counter = {}
balls_presence_history = deque(maxlen=1500)
       
balls_position_verified = {}
balls_position_send = {}

def is_close_or_duplicate(point, points, threshold):
    for p in points:
        if point == p or (abs(point[0] - p[0]) <= threshold and abs(point[1] - p[1]) <= threshold):
            return p
    return None

ball_ids = {}  
next_ball_id = 1  
ball_threshold = 20  


robot_vector = None
robot_degrees = None

alpha = 0.7 # Contrast control (1.0-3.0)
beta = 0 # Brightness control (0-100)

try:
    while True:
        _, frame = cap.read()
        
        frame_width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
        frame_height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))

        
        frame = cv2.convertScaleAbs(frame, alpha=alpha, beta=beta)
        new_width = int(frame_width /2)
        new_height = int(frame_height /2)
        frame = cv2.resize(frame, (new_width, new_height))
        
        
        if frame_corners is None:
            frame_corners, extra_point = draw_ROI(frame)
            if frame_corners is not None:  
                frame_corners = [(int(p[0]), int(p[1])) for p in frame_corners]
               
                max_x = max(p[0] for p in frame_corners)
                max_y = max(p[1] for p in frame_corners)
                grid_size = ((max_x), (max_y))
        
        if extra_point is not None:
            extra_point = (int(extra_point[0]), int(extra_point[1]))

        if hsv_ranges == {}:
            for color in colors:
                print(f"Select HSV values for {color}")
                hsv_values = get_hsv_values(frame)

                if color == "ORANGE_BALL5":
                    lower = [max(0, x - 15) for x in hsv_values]
                    upper = [min(255, x + 15) for x in hsv_values]
                
                else:
                    lower = [max(0, x - 23) for x in hsv_values]
                    upper = [min(255, x + 23) for x in hsv_values]
                    
                hsv_ranges[color] = {
                    "lower": np.array(lower, dtype=np.uint8),
                    "upper": np.array(upper, dtype=np.uint8)
                }
    

        if frame_corners is not None:  # This is a new conditional block
            polygon = np.array(frame_corners[:-1])

            hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)

            FRONTSIDE_ROBOT_MASK = cv2.inRange(hsv, hsv_ranges['FRONTSIDE_ROBOT_CONTOURS']['lower'], hsv_ranges['FRONTSIDE_ROBOT_CONTOURS']['upper'])
            FRONTSIDE_ROBOT_CONTOURS, _ = cv2.findContours(FRONTSIDE_ROBOT_MASK, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
         
            white_mask1 = cv2.inRange(hsv, hsv_ranges['WHITE_BALL_1']['lower'], hsv_ranges['WHITE_BALL_1']['upper'])
            white_mask2 = cv2.inRange(hsv, hsv_ranges['WHITE_BALL_2']['lower'], hsv_ranges['WHITE_BALL_1']['upper'])
            white_mask3 = cv2.inRange(hsv, hsv_ranges['WHITE_BALL_3']['lower'], hsv_ranges['WHITE_BALL_1']['upper'])
            white_mask4 = cv2.inRange(hsv, hsv_ranges['WHITE_BALL_4']['lower'], hsv_ranges['WHITE_BALL_1']['upper'])
            white_contours1, _ = cv2.findContours(white_mask1, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
            white_contours2, _ = cv2.findContours(white_mask2, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
            white_contours3, _ = cv2.findContours(white_mask3, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
            white_contours4, _ = cv2.findContours(white_mask4, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

            # make mask and contour
            orange_mask = cv2.inRange(hsv, hsv_ranges['ORANGE_BALL5']['lower'], hsv_ranges['ORANGE_BALL5']['upper'])
            orange_contours, _ = cv2.findContours(orange_mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        
            # Get a binary image isolating the yellow pixels
            BACKSIDE_ROBOT_MASK = cv2.inRange(hsv, hsv_ranges['BACKSIDE_ROBOT']['lower'], hsv_ranges['BACKSIDE_ROBOT']['upper'])
            BACKSIDE_ROBOT_CONTOURS, _ = cv2.findContours(BACKSIDE_ROBOT_MASK, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        
            # Get a binary image isolating the red pixels
            red_mask1 = cv2.inRange(hsv, hsv_ranges['RED_CROSS_1']['lower'], hsv_ranges['RED_CROSS_1']['upper'])
            red_mask2 = cv2.inRange(hsv, hsv_ranges['RED_CROSS_2']['lower'], hsv_ranges['RED_CROSS_2']['upper'])
            red_mask3 = cv2.inRange(hsv, hsv_ranges['RED_CROSS_3']['lower'], hsv_ranges['RED_CROSS_3']['upper'])
            red_mask4 = cv2.inRange(hsv, hsv_ranges['RED_CROSS_4']['lower'], hsv_ranges['RED_CROSS_4']['upper'])
            red_contours1, _ = cv2.findContours(red_mask1, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
            red_contours2, _ = cv2.findContours(red_mask2, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
            red_contours3, _ = cv2.findContours(red_mask3, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
            red_contours4, _ = cv2.findContours(red_mask4, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)


            cv2.circle(frame, extra_point, 5, (203, 111, 189), -1) #goal

            if FRONTSIDE_ROBOT_CONTOURS:
                robot_contour = max(FRONTSIDE_ROBOT_CONTOURS, key=cv2.contourArea)
                robot_front = get_center_of_contour(robot_contour)

                if robot_front is not None and cv2.pointPolygonTest(polygon, robot_front, False) >= 0:
                    cv2.circle(frame, robot_front, 5, (255, 0, 0), -1)           
                    #robot_position = (robot_front[0] - polygon[0][0]), (polygon[0][1] - robot_front[1])
                    #robot_position = (robot_front[0] - polygon[0][0], robot_front[1] + polygon[0][1])
                    robot_position= ((robot_front[0] - polygon[0][0]), (polygon[0][1] - robot_front[1]))
                

                if BACKSIDE_ROBOT_CONTOURS:  # Check for the yellow dot at the back of the robot
                    tail_contour = max(BACKSIDE_ROBOT_CONTOURS, key=cv2.contourArea)
                    tail_center = get_center_of_contour(tail_contour)
                    if tail_center is not None and cv2.pointPolygonTest(polygon, tail_center, False) >= 0:
                        cv2.circle(frame, tail_center, 5, (0, 255, 255), -1)  # Yellow circle
                        if robot_front is not None and tail_center is not None:
                            robot_vector = get_vector(robot_front, tail_center)
                            robot_degrees = calculate_orientation(robot_vector)

            
            min_contour_area = 5  # adjust this 

            hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)

            def generate_surrounding_points(center, distance):
                x, y = center
                directions = [(dx, dy) for dx, dy in itertools.product(range(-distance, distance+1), repeat=2)]
                return [(x + dx, y + dy) for dx, dy in directions]

            red_cross_centers = []
            red_cross_centers_set = set()
            frame_height = frame.shape[0]
            for red_contours in [red_contours1, red_contours2, red_contours3, red_contours4]:
                for contour in red_contours:
                    if cv2.contourArea(contour) < min_contour_area:
                        continue

                    for point in contour:
                        point = tuple(point[0])  # convert from [[x y]] to (x, y)
                        if cv2.pointPolygonTest(polygon, (int(point[0]), int(point[1])), False) >= 0:
                            # Convert from pixel coordinates to grid coordinates, flipping the y axis
                            cv2.circle(frame, point, 5, (255, 192, 203), -1)
                            grid_point = ((point[0] - polygon[0][0]), (polygon[0][1] - point[1]))
                            if grid_point not in red_cross_centers_set:  # check if the point already exists
                                red_cross_centers.append(grid_point)
                                red_cross_centers_set.add(grid_point)
                                surrounding_points = generate_surrounding_points(grid_point, 3)
                                red_cross_centers.extend(surrounding_points)
                                red_cross_centers_set.update(surrounding_points)

            balls_position = [] 
            orange_balls_position = []  

            # Find white balls
            for white_contours in [white_contours1, white_contours2, white_contours3, white_contours4]:
                for contour in white_contours:
                    if cv2.contourArea(contour) < min_contour_area:
                        continue
                    ball_center = get_center_of_contour(contour)
                    if ball_center is not None and cv2.pointPolygonTest(polygon, ball_center, False) >= 0:
                        cv2.circle(frame, ball_center, 5, (0, 165, 255), -1)
                        ball_position = ((ball_center[0] - polygon[0][0]), (polygon[0][1] - ball_center[1]))
                        if not is_close_or_duplicate(ball_position, balls_position, 5):
                            balls_position.append(ball_position)
                            close_or_duplicate = is_close_or_duplicate(ball_position, balls_position_verified.keys(), 3)
                            if close_or_duplicate is not None:
                                balls_position_verified[close_or_duplicate] = 50
                                balls_counter[close_or_duplicate] += 1
                                balls_absence_counter[close_or_duplicate] = 0
                                if balls_counter[close_or_duplicate] >= 40 and close_or_duplicate not in balls_position_send:
                                    balls_position_send[close_or_duplicate] = 10
                            else:
                                balls_position_verified[ball_position] = 50
                                balls_counter[ball_position] = 1
                                balls_absence_counter[ball_position] = 0
                for ball in list(balls_position_verified.keys()):  
                    if ball not in balls_position:
                        balls_position_verified[ball] -= 1
                        # increment the absence counter for the ball
                        balls_absence_counter[ball] += 1

                        if balls_absence_counter[ball] >= 20 and ball in balls_position_send:
                            del balls_position_send[ball]
                    else:
                        
                        balls_absence_counter[ball] = 0 
                        
                        balls_presence_history.append(ball)
                    # check if it reaches zero
                    if balls_position_verified[ball] <= 0:
                        del balls_position_verified[ball]
                        del balls_counter[ball]
                        del balls_absence_counter[ball]
                for ball in list(balls_position_send.keys()):
                    if ball not in balls_presence_history:
                        del balls_position_send[ball]

            for id, pos in ball_ids.items():
                cv2.putText(frame, str(id), (pos[0] + 10, pos[1]), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)  


            if robot_position is not None and robot_vector is not None:
                for id, ball_position in ball_ids.items():
                    ball_vector = get_vector(robot_position, ball_position)
                    if abs(robot_vector[0] - ball_vector[0]) < 5 and abs(robot_vector[1] - ball_vector[1]) < 5:
                        print(f"Robot is aligned with ball {id}")

            # Find orange balls
            for contour in orange_contours:
                if cv2.contourArea(contour) < min_contour_area:
                    continue
                ball_center = get_center_of_contour(contour)
                if ball_center is not None and cv2.pointPolygonTest(polygon, ball_center, False) >= 0:
                    cv2.circle(frame, ball_center, 5, (0, 255, 0), -1)
                    orange_balls_position.append(((ball_center[0] - polygon[0][0]), (polygon[0][1] - ball_center[1])))

            current_time = time.time()

            # Sending data1 every 0.8 second
            if current_time - last_send_time_data1 >= 0.8:
                data1 = {
                    "robot": None if robot_position is None else tuple(int(x) for x in robot_position),
                    "orientation": None if robot_degrees is None else float(robot_degrees)
                }
                data = {k: v for k, v in data1.items() if v is not None}            
                try:
                    client_socket.send((json.dumps(data) + '\n').encode())
                except Exception as e: 
        
                    connection_event.clear()  
                    if connection_thread.is_alive():  

                        connection_thread.join()  
                    is_exiting = False  
                    connection_thread = threading.Thread(target=wait_for_connection)  
                    connection_thread.start()
                        
                last_send_time_data1 = current_time

            # Sending data3 every 35 seconds
            if current_time - last_send_time_data3 >= 35:
                data2 = {
                    "white_balls": [tuple(int(x) for x in pos) for pos in balls_position_send],
                    "orange_balls": [tuple(int(x) for x in pos) for pos in orange_balls_position],
                    "red_crosses": [tuple(int(x) for x in pos) for pos in red_cross_centers],
                    "grid_size": None if grid_size is None else tuple(int(x) for x in grid_size),
                }

                data = {k: v for k, v in data2.items() if v is not None} 
                try:
                    client_socket.send((json.dumps(data) + '\n').encode())
                except Exception as e: 
        
                    connection_event.clear()  
                    if connection_thread.is_alive():  

                        connection_thread.join()  
                    is_exiting = False  
                    connection_thread = threading.Thread(target=wait_for_connection)  
                    connection_thread.start()
                        
                last_send_time_data3 = current_time
            
            if current_time - last_send_time_data2 >= 10:
                print("- - - - - -NEW SEND!  CROSS SLOW- - - - - -")
                print(f"grid_size - {grid_size}")
                print(f"goal_point - {extra_point}")
                data3 = {
                    "grid_size": None if grid_size is None else tuple(int(x) for x in grid_size),
                    "goal_point": None if extra_point is None else tuple(int(x) for x in extra_point)
                }

                data = {k: v for k, v in data3.items() if v is not None}  
                try:
                    client_socket.send((json.dumps(data) + '\n').encode())
                except Exception as e: 
        
                    connection_event.clear()  
                    if connection_thread.is_alive():  

                        connection_thread.join()  
                    is_exiting = False  
                    connection_thread = threading.Thread(target=wait_for_connection)  
                    connection_thread.start()
                        
                last_send_time_data2 = current_time

            cv2.polylines(frame, [polygon], True, (0,255,0), 2)
            cv2.imshow('Frame', frame)

            if cv2.waitKey(1) & 0xFF == ord('q'):
                break
finally:
    is_exiting = True
    if cap is not None:
        cap.release()
    cv2.destroyAllWindows()
    if client_socket is not None:
        client_socket.close()
    if server_socket is not None:
        server_socket.close()

