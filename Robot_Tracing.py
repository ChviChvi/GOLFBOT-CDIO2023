import socket
import threading
import cv2
import numpy as np
import time
import json
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



def get_center_of_contour(contour):
    M = cv2.moments(contour)
    if M["m00"] == 0:
        return None
    else:
        return (int(M["m10"] / M["m00"]), int(M["m01"] / M["m00"]))

def get_hsv_values(frame):
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

#   This function draws the 4 cornes at the start
def draw_ROI(frame):
    fig, ax = plt.subplots(1, figsize=(8, 6))
    ax.imshow(cv2.cvtColor(frame, cv2.COLOR_BGR2RGB))  # Convert color for matplotlib display
    ROI = plt.ginput(4)  # Select the 4 corners of your rectangle
    if len(ROI) > 0:  # Check if ROI is not empty
        ROI.append(ROI[0])  # add the first point to the end to close the rectangle
        rect = patches.Polygon(ROI, linewidth=1, edgecolor='r', facecolor='none')  # Create a Rectangle patch
        ax.add_patch(rect)  # Add the patch to the Axes

        ax.scatter([p[0] for p in ROI[:-1]], [p[1] for p in ROI[:-1]], c='r', s=10) # Increase the 's' value to make the markers bigger

        plt.show()
    else:
        print("No valid points were selected.")
        ROI = None
    return ROI

print("Waiting for camera...")
cap = cv2.VideoCapture(0)
print("Camera is on!")


hsv_ranges = {}
colors = ["green", "red", "yellow", "white", "orange"]
balls_position = []
orange_balls_position = []
robot_position = None
robot_angle = None
red_cross_centers = None
frame_corners = None

cell_size = 10

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
        new_width = frame_width // 2
        new_height = frame_height // 2
        frame = cv2.resize(frame, (new_width, new_height))


        
        if frame_corners is None:
            frame_corners = draw_ROI(frame)
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
                lower = [max(0, x - 10) for x in hsv_values]
                upper = [min(255, x + 10) for x in hsv_values]

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

            green_mask = cv2.inRange(hsv, hsv_ranges['green']['lower'], hsv_ranges['green']['upper'])
            green_contours, _ = cv2.findContours(green_mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
            # print(hsv_ranges['green']['lower'])
            # print(hsv_ranges['green']['upper'])
            

            # Get a binary image isolating the white pixels (light)
            #white_mask_light = cv2.inRange(hsv, hsv_ranges['white_shadow']['lower'], hsv_ranges['white_shadow']['upper'])
        
            # Get a binary image isolating the white pixels (shadow)
            #white_mask_shadow = cv2.inRange(hsv, hsv_ranges['white_light']['lower'], hsv_ranges['white_light']['upper'])

            # Combine the white masks (light and shadow)
            #white_mask = cv2.bitwise_or(white_mask_light, white_mask_shadow)
            white_mask = cv2.inRange(hsv, hsv_ranges['white']['lower'], hsv_ranges['white']['upper'])
        
            white_contours, _ = cv2.findContours(white_mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

            # Get a binary image isolating the orange pixels
            orange_mask = cv2.inRange(hsv, hsv_ranges['orange']['lower'], hsv_ranges['orange']['upper'])
            orange_contours, _ = cv2.findContours(orange_mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        
            # Get a binary image isolating the yellow pixels
            yellow_mask = cv2.inRange(hsv, hsv_ranges['yellow']['lower'], hsv_ranges['yellow']['upper'])
            yellow_contours, _ = cv2.findContours(yellow_mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        
            # Get a binary image isolating the red pixels
            red_mask = cv2.inRange(hsv, hsv_ranges['red']['lower'], hsv_ranges['red']['upper'])
            red_contours, _ = cv2.findContours(red_mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

            if green_contours:
                robot_contour = max(green_contours, key=cv2.contourArea)
                robot_front = get_center_of_contour(robot_contour)

                if robot_front is not None and cv2.pointPolygonTest(polygon, robot_front, False) >= 0:
                    cv2.circle(frame, robot_front, 5, (255, 0, 0), -1)           
                    robot_position = ((robot_front[0] - polygon[0][0]), (polygon[0][1] - robot_front[1]))
                    if time.time() - last_robot_print_time >= 3:
                    #  back_position = (robot_position[0] - robot_vector[0] / 2, robot_position[1] - robot_vector[1] / 2)
                    #  front_position = (robot_position[0] + robot_vector[0] / 2, robot_position[1] + robot_vector[1] / 2)
                        print(f"Robot front at: {robot_front}")
                    #   print(f"Robot front at: {front_position}")
                        if client_socket is not None:
                            robot_position = tuple(int(x) for x in robot_position)  # Convert numpy ints to python ints
                            try:
                                client_socket.send((json.dumps({"robot": robot_position}) + '\n').encode())
                            except Exception as e:
                                print(f"Error sending robot position: {e}")
                                break
                        last_robot_print_time = time.time()

                        # After identifying the yellow part of the robot:

                if yellow_contours:  # Check for the yellow dot at the back of the robot
                    tail_contour = max(yellow_contours, key=cv2.contourArea)
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

            balls_position = []  # Reset the white balls position at each frame             <-------------------------------------- TODO LOOK AT THIS
            orange_balls_position = []  # Reset the orange balls position at each frame     <-------------------------------------- TODO LOOK AT THIS
        
            min_contour_area = 5  # adjust this value to suit your needs

            # red cross
            hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)

            

            # If the red cross centers have not been computed yet
            if red_cross_centers is None:
                red_cross_centers = []
                for contour in red_contours:
                    if cv2.contourArea(contour) < min_contour_area:
                        continue

                    for point in contour:
                        point = tuple(point[0])  # convert from [[x y]] to (x, y)
                        if cv2.pointPolygonTest(polygon, (int(point[0]), int(point[1])), False) >= 0:
                            grid_point = (point[0] // cell_size, point[1] // cell_size)  # Convert from pixel coordinates to grid coordinates
                            red_cross_centers.append(point)
                            cv2.circle(frame, point, 5, (255, 192, 203), -1)  # Draw the center of the red cross in light blue

                    print(f"Red Cross at: {red_cross_centers}")

            # Find white balls
            for contour in white_contours:
                # Sort contours by area and keep only the largest 10
                white_contours = sorted(white_contours, key=cv2.contourArea, reverse=True)[:10]

                if cv2.contourArea(contour) < min_contour_area:
                    continue
                ball_center = get_center_of_contour(contour)
                if ball_center is not None and cv2.pointPolygonTest(polygon, ball_center, False) >= 0:
                    cv2.circle(frame, ball_center, 5, (0, 165, 255), -1)
                    balls_position.append(((ball_center[0] - polygon[0][0]), (polygon[0][1] - ball_center[1])))
            
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

            if time.time() - last_send_time >= 1:  # Send the data every second
                print(f"Robot Degrees: {robot_degrees}")
                last_send_time = time.time()
            
                # Create a dictionary to hold all the data
                data = {
                    "white_balls": [tuple(int(x) for x in pos) for pos in balls_position],
                    "orange_balls": [tuple(int(x) for x in pos) for pos in orange_balls_position],
                    "robot": None if robot_position is None else tuple(int(x) for x in robot_position),
                    "red_crosses": [tuple(int(x) for x in pos) for pos in red_cross_centers],
                    "grid_size": None if grid_size is None else tuple(int(x) for x in grid_size),
                    "orientation": None if robot_degrees is None else float(robot_degrees)
                }

                # Remove any None values
                data = {k: v for k, v in data.items() if v is not None}

                if client_socket is not None and connection_event.is_set():  # Only send data if the script is connected
                    try:
                        client_socket.send((json.dumps(data) + '\n').encode())
                    except Exception as e:  # If there's an error (like a disconnection), go back to trying to connect
                        print(f"Error sending data: {e}")
                        connection_event.clear()  # Clear the event to signal that the client has disconnected
                        connection_thread = threading.Thread(target=wait_for_connection)  # Start a new connection thread
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