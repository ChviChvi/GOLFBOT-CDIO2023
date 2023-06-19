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
# def check_connection():
#     global client_socket
#     while True:
#         try:
#             # Try sending a small test message
#             client_socket.send((json.dumps({"test": "test"}) + '\n').encode())
#         except Exception as e:
#             print("Lost connection, trying to reconnect...")
#             client_socket = None
#             connection_event.clear()
#             wait_for_connection()
#         time.sleep(1)  # Check every second
# Create a new server socket
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
#connection_event.wait()

# # Start a new thread that checks the connection
# check_thread = threading.Thread(target=check_connection)
# check_thread.start()




def get_center_of_contour(contour):
    M = cv2.moments(contour)
    if M["m00"] == 0:
        return None
    else:
        return (int(M["m10"] / M["m00"]), int(M["m01"] / M["m00"]))

def get_hsv_values(frame):
    #frame = cv2.resize(frame, (new_width, new_height))  # Resize the frame
    
    # Display the frame in its original BGR colors
    cv2.imshow("Image", frame)

    # Let the user pick a point on the frame
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

    # Create the figure and axes for plotting
    fig, ax = plt.subplots(1, figsize=(8, 6))
    ax.imshow(frame_rgb)

    # Let the user select the 4 corners of the rectangle
    ROI = plt.ginput(4)

    if len(ROI) > 0:
        # Convert the ROI to a numpy array
        ROI = np.array(ROI, dtype=np.float32)

        # Find the minimum and maximum coordinates in each dimension
        min_x = np.min(ROI[:, 0])
        max_x = np.max(ROI[:, 0])
        min_y = np.min(ROI[:, 1])
        max_y = np.max(ROI[:, 1])

        # Translate the ROI coordinates to have the bottom-left corner as (0, 0)
        ROI[:, 0] -= min_x
        ROI[:, 1] -= min_y

        # Convert the coordinates to integers
        ROI = np.round(ROI).astype(np.int32)

        # Calculate the translation values to revert the translation later
        translate_x = int(min_x)
        translate_y = int(min_y)

        # Translate the ROI back to the original position
        ROI[:, 0] += translate_x
        ROI[:, 1] += translate_y

        # Append the first point to close the rectangle
        ROI = np.vstack([ROI, ROI[0]])

        # Draw the rectangle on the axes
        rect = patches.Polygon(ROI, linewidth=1, edgecolor='r', facecolor='none')
        ax.add_patch(rect)

        # Scatter plot the marker points
        ax.scatter(ROI[:-1, 0], ROI[:-1, 1], c='r', s=10)

        plt.show()
    else:
        print("No valid points were selected.")
        ROI = None

    return ROI


print("Waiting for camera...")
cap = cv2.VideoCapture(1,cv2.CAP_DSHOW)
print("Camera is on!")


hsv_ranges = {}
colors = ["FRONTSIDE_ROBOT_CONTOURS", "RED_CROSS", "BACKSIDE_ROBOT", "WHITE_BALL_1","WHITE_BALL_2","WHITE_BALL_3","WHITE_BALL_4", "ORANGE_BALL5"]
balls_position = []
orange_balls_position = []
robot_position = None
robot_angle = None
red_cross_centers = None
frame_corners = None

cell_size = 1

last_send_time = time.time()
last_robot_print_time = time.time()
last_print_time = time.time()

# these two functions calculate the degrees > if it return 0 is is looking east, 90 north etc.
def get_vector(p1, p2):
    if p1 is None or p2 is None:
        return None
    dx = p2[0] - p1[0]
    dy = p2[1] - p1[1]
    return dx, dy

def calculate_orientation(vector):
    x, y = vector
    rad = math.atan2(y, x)  # This returns the angle in radians
    deg = math.degrees(rad)  # Convert to degrees

    # Adjust the degrees to be in the range [0, 360)
    if deg < 0:
        deg = 360 + deg
    
    return deg


# threshold for verifying a ball
threshold_verify = 1

# a dictionary for counting the occurrence of each ball
balls_counter = {}
balls_absence_counter = {}
balls_presence_history = deque(maxlen=1500)
       

# the list for verified balls
balls_position_verified = {}
balls_position_send = {}

def is_close_or_duplicate(point, points, threshold):
    for p in points:
        if point == p or (abs(point[0] - p[0]) <= threshold and abs(point[1] - p[1]) <= threshold):
            return p
    return None

ball_ids = {}  # A dict to store the IDs of the balls
next_ball_id = 1  # The ID that will be assigned to the next new ball
ball_threshold = 20  # If a ball moves more than this many pixels between frames, it is considered a new ball



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
        new_width = int(frame_width )
        new_height = int(frame_height )
        frame = cv2.resize(frame, (new_width, new_height))
        
        #grid_size = (new_width, new_height) 
        #print(f"grid size: {grid_size}")
        
        if frame_corners is None:
            frame_corners = draw_ROI(frame)
            #frame_corners = [quantize_coordinates(point, 10) for point in frame_corners]
            if frame_corners is not None:  # Check if draw_ROI returned valid points
                frame_corners = [(int(p[0]), int(p[1])) for p in frame_corners]
                # Calculate grid size
                max_x = max(p[0] for p in frame_corners)
                max_y = max(p[1] for p in frame_corners)
                grid_size = ((max_x), (max_y))
        if hsv_ranges == {}:
            for color in colors:
                print(f"Select HSV values for {color}")
                hsv_values = get_hsv_values(frame)

                # get the min and max HSV values based on the selected HSV values
                lower = [max(0, x - 13) for x in hsv_values]
                upper = [min(255, x + 13) for x in hsv_values]

                print(lower)
                print(upper)

                hsv_ranges[color] = {
                    "lower": np.array(lower, dtype=np.uint8),
                    "upper": np.array(upper, dtype=np.uint8)
                }
            print(hsv_ranges)
    

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

            # Get a binary image isolating the orange pixels
            orange_mask = cv2.inRange(hsv, hsv_ranges['ORANGE_BALL5']['lower'], hsv_ranges['ORANGE_BALL5']['upper'])
            orange_contours, _ = cv2.findContours(orange_mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        
            # Get a binary image isolating the yellow pixels
            BACKSIDE_ROBOT_MASK = cv2.inRange(hsv, hsv_ranges['BACKSIDE_ROBOT']['lower'], hsv_ranges['BACKSIDE_ROBOT']['upper'])
            BACKSIDE_ROBOT_CONTOURS, _ = cv2.findContours(BACKSIDE_ROBOT_MASK, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        
            # Get a binary image isolating the red pixels
            red_mask = cv2.inRange(hsv, hsv_ranges['RED_CROSS']['lower'], hsv_ranges['RED_CROSS']['upper'])
            red_contours, _ = cv2.findContours(red_mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

            if FRONTSIDE_ROBOT_CONTOURS:
                robot_contour = max(FRONTSIDE_ROBOT_CONTOURS, key=cv2.contourArea)
                robot_front = get_center_of_contour(robot_contour)

                if robot_front is not None and cv2.pointPolygonTest(polygon, robot_front, False) >= 0:
                    cv2.circle(frame, robot_front, 5, (255, 0, 0), -1)           
                    #robot_position = (robot_front[0] - polygon[0][0]), (polygon[0][1] - robot_front[1])
                    #robot_position = (robot_front[0] - polygon[0][0], robot_front[1] + polygon[0][1])
                    robot_position= ((robot_front[0] - polygon[0][0]), (polygon[0][1] - robot_front[1]))
                
                    # if time.time() - last_robot_print_time >= 3:
                    # #  back_position = (robot_position[0] - robot_vector[0] / 2, robot_position[1] - robot_vector[1] / 2)
                    # #  front_position = (robot_position[0] + robot_vector[0] / 2, robot_position[1] + robot_vector[1] / 2)
                    #     print(f"Robot front at: {robot_front}")
                    # #   print(f"Robot front at: {front_position}")
                    #     if client_socket is not None:
                    #         robot_position = tuple(int(x) for x in robot_position)  # Convert numpy ints to python ints
                    #         try:
                    #             client_socket.send((json.dumps({"robot": robot_position}) + '\n').encode())
                    #         except Exception as e:
                    #             print(f"Error sending robot position: {e}")
                    #             break
                    #     last_robot_print_time = time.time()

                    #     # After identifying the yellow part of the robot:

                if BACKSIDE_ROBOT_CONTOURS:  # Check for the yellow dot at the back of the robot
                    tail_contour = max(BACKSIDE_ROBOT_CONTOURS, key=cv2.contourArea)
                    tail_center = get_center_of_contour(tail_contour)
                    if tail_center is not None and cv2.pointPolygonTest(polygon, tail_center, False) >= 0:
                        cv2.circle(frame, tail_center, 5, (0, 255, 255), -1)  # Yellow circle
                        if robot_front is not None and tail_center is not None:
                            robot_vector = get_vector(robot_front, tail_center)
                            robot_degrees = calculate_orientation(robot_vector)
                            #print(f"Robot vector: {robot_vector}")
                            
                            #robot_orientation = calculate_robot_orientation(robot_vector, frame.shape[0], frame.shape[1])
                            #robot_orientation = calculate_robot_orientation(robot_vector, frame_height, frame_width)

                            #print(f"Robot orientation: {robot_orientation}")

            
            min_contour_area = 5  # adjust this value to suit your needs

            # red cross
            hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)

            
            
            # If the red cross centers have not been computed yet
            if red_cross_centers is None:
                red_cross_centers = []
                frame_height = frame.shape[0]
                for contour in red_contours:
                    if cv2.contourArea(contour) < min_contour_area:
                        continue
                
                    for point in contour:
                        point = tuple(point[0])  # convert from [[x y]] to (x, y)
                        if cv2.pointPolygonTest(polygon, (int(point[0]), int(point[1])), False) >= 0:
                            # Convert from pixel coordinates to grid coordinates, flipping the y axis
                            cv2.circle(frame, point, 5, (255, 192, 203), -1)
                            grid_point = ((point[0] - polygon[0][0]), (polygon[0][1] - point[1]))
                            red_cross_centers.append(grid_point)
                            #grid_point = (point[0] , (frame_height - point[1]) )
                            #red_cross_centers.append(grid_point)
                            #cv2.circle(frame, point, 5, (255, 192, 203), -1)  # Draw the center of the red cross in light blue
                print(f"Red Cross at: {red_cross_centers}")

            balls_position = []  # Reset the white balls position at each frame             <-------------------------------------- TODO LOOK AT THIS
            orange_balls_position = []  # Reset the orange balls position at each frame     <-------------------------------------- TODO LOOK AT THIS

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
                                # reset the threshold for the existing ball
                                balls_position_verified[close_or_duplicate] = 50
                                # increment the counter for the existing ball
                                balls_counter[close_or_duplicate] += 1
                                # reset the absence counter for the ball
                                balls_absence_counter[close_or_duplicate] = 0
                                # if it meets the send threshold, add to balls_position_send
                                #if balls_counter[close_or_duplicate] >= 100 and close_or_duplicate not in balls_position_send:
                                if balls_counter[close_or_duplicate] >= 50 and close_or_duplicate not in balls_position_send:
                                    balls_position_send[close_or_duplicate] = 10
                            else:
                                # add the new ball with initial threshold and counter
                                balls_position_verified[ball_position] = 50
                                balls_counter[ball_position] = 1
                                balls_absence_counter[ball_position] = 0
                # decrease the threshold for the balls not found in this iteration
                for ball in list(balls_position_verified.keys()):  # copy the keys to a list to avoid runtime error
                    if ball not in balls_position:
                        balls_position_verified[ball] -= 1
                        # increment the absence counter for the ball
                        balls_absence_counter[ball] += 1
                        # if it meets the removal threshold, remove from balls_position_send
                        #if balls_absence_counter[ball] >= 100 and ball in balls_position_send:
                        if balls_absence_counter[ball] >= 33 and ball in balls_position_send:
                            del balls_position_send[ball]
                    else:
                        # do not decrease the counter for the ball if it's found
                        balls_absence_counter[ball] = 0  # reset the absence counter if the ball is found
                        # Add ball to presence history
                        balls_presence_history.append(ball)
                    # check if it reaches zero
                    if balls_position_verified[ball] <= 0:
                        del balls_position_verified[ball]
                        del balls_counter[ball]
                        del balls_absence_counter[ball]
                for ball in list(balls_position_send.keys()):
                    if ball not in balls_presence_history:
                        del balls_position_send[ball]
                #print(f"White balls at: {balls_position}")
                #print(f"Verified white balls at: {balls_position_verified.keys()}")
                if time.time() - last_send_time >= 1:
                    print(f"Send white balls at: {balls_position_send.keys()}")
                    print(f"robot poisiton - {robot_position}")
    
            #assign_ids_to_balls(balls_position)  # NEW

            # Draw the number of balls on the frame
            #cv2.putText(frame, str(len(balls_position)), (10, 50), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0,255,0), 2)


            # Before assigning IDs, draw balls and their IDs
            # for id, pos in ball_ids.items():
            #     cv2.circle(frame, pos, 5, (203, 192, 255), -1)
            #     cv2.putText(frame, str(id), (pos[0] + 10, pos[1]), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)  # Green number for ball ID
            for id, pos in ball_ids.items():
                cv2.putText(frame, str(id), (pos[0] + 10, pos[1]), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)  # Green number for ball ID


            # Calculate the vector between the robot and each ball
            if robot_position is not None and robot_vector is not None:
                for id, ball_position in ball_ids.items():
                    ball_vector = get_vector(robot_position, ball_position)
                    # If the vectors are similar, they are aligned. You might want to adjust the comparison based on your needs.
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

            if time.time() - last_send_time >= 0.3:  # Send the data every second
                print("- - - - - -NEW SEND!- - - - - -")
                print(f"Robot Degrees: {robot_degrees}")
                print(f"Send white balls at: {balls_position_send.keys()}")
                print(f"Robot poisiton - {robot_position}")
                print(f"grid_size - {grid_size}")
                last_send_time = time.time()

            
                # Create a dictionary to hold all the data
                data = {
                    "white_balls": [tuple(int(x) for x in pos) for pos in balls_position_send],
                    "orange_balls": [tuple(int(x) for x in pos) for pos in orange_balls_position],
                    "robot": None if robot_position is None else tuple(int(x) for x in robot_position),
                    "red_crosses": [tuple(int(x) for x in pos) for pos in red_cross_centers],
                    "grid_size": None if grid_size is None else tuple(int(x) for x in grid_size),
                    "orientation": None if robot_degrees is None else float(robot_degrees)
                }

                scale_factor = 1  # Adjust this value according to your needs

                scaled_data = {
                    "white_balls": [(int(x[0] / scale_factor), int(x[1] / scale_factor)) for x in data["white_balls"]],
                    "orange_balls": [(int(x[0] / scale_factor), int(x[1] / scale_factor)) for x in data["orange_balls"]],
                    "robot": None if data["robot"] is None else (int(data["robot"][0] / scale_factor), int(data["robot"][1] / scale_factor)),
                    "red_crosses": [(int(x[0] / scale_factor), int(x[1] / scale_factor)) for x in data["red_crosses"]],
                    "grid_size": None if data["grid_size"] is None else (int(data["grid_size"][0] / scale_factor), int(data["grid_size"][1] / scale_factor)),
                    "orientation": data["orientation"]
                }

                # Remove any None values
                data = {k: v for k, v in data.items() if v is not None}

                if client_socket is not None and connection_event.is_set():  # Only send data if the script is connected
                    try:
                        client_socket.send((json.dumps(data) + '\n').encode())
                    except Exception as e: 
                        print(f"Error sending data: {e}")
                        connection_event.clear()  
                        if connection_thread.is_alive():  
                            print("Waiting for connection thread to finish")
                            connection_thread.join()  
                        is_exiting = False  
                        connection_thread = threading.Thread(target=wait_for_connection)  
                        connection_thread.start()
        
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

# if is_exiting:
#     if cap is not None:
#         cap.release()
#     cv2.destroyAllWindows()
#     if client_socket is not None:
#         client_socket.close()
#     if server_socket is not None:
#         server_socket.close()

# def assign_ids_to_balls(balls_position):
#     global next_ball_id, ball_ids
#     new_ball_ids = {}
#     for pos in balls_position:
#         closest_id = None
#         closest_dist = ball_threshold
#         for id, old_pos in ball_ids.items():
#             dist = ((pos[0] - old_pos[0]) ** 2 + (pos[1] - old_pos[1]) ** 2) ** 0.5
#             if dist < closest_dist:
#                 closest_id = id
#                 closest_dist = dist
#         if closest_id is not None:
#             new_ball_ids[closest_id] = pos
#         elif len(ball_ids) < 10:  # Only assign a new ID if there are less than 10 balls being tracked
#             new_ball_ids[next_ball_id] = pos
#             next_ball_id = (next_ball_id % 10) + 1  # This will make the ID number go back to 1 after reaching 10
#     ball_ids = new_ball_ids