import socket
import threading
import cv2
import numpy as np
import time
import json
import math
import matplotlib.pyplot as plt
import matplotlib.patches as patches

def wait_for_connection():
    global client_socket
    print("Waiting for connection...")
    client_socket, addr = server_socket.accept()
    print(f"Connection made with {addr}.")
    connection_event.set()  # Set the event to signal that the client has connected


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
connection_event.wait()

def get_center_of_contour(contour):
    M = cv2.moments(contour)
    if M["m00"] == 0:
        return None
    else:
        return (int(M["m10"] / M["m00"]), int(M["m01"] / M["m00"]))

def draw_ROI(frame):
    fig,ax = plt.subplots(1)
    ax.imshow(cv2.cvtColor(frame, cv2.COLOR_BGR2RGB))  # Convert color for matplotlib display
    ROI = plt.ginput(4)  # Select the 4 corners of your rectangle
    if len(ROI) > 0:  # Check if ROI is not empty
        ROI.append(ROI[0])  # add the first point to the end to close the rectangle
        rect = patches.Polygon(ROI, linewidth=1, edgecolor='r', facecolor='none')  # Create a Rectangle patch
        ax.add_patch(rect)  # Add the patch to the Axes
        plt.show()
    else:
        print("No valid points were selected.")
        ROI = None
    return ROI
print("Waiting for camera...")
cap = cv2.VideoCapture(0)
print("Camera is on!")

lower_green = np.array([36, 25, 25])
upper_green = np.array([86, 255, 255])

# define range for red color
lower_red = np.array([0, 64, 0])
upper_red = np.array([11, 255, 255])

red_cross_centers = None

# define range for white color (light)
lower_white_light = np.array([0, 0, 200])
upper_white_light = np.array([179, 17, 255])

# define range for white color (shadow)
lower_white_shadow = np.array([16, 79, 203])
upper_white_shadow = np.array([86, 140, 255])

# define range for orange color
lower_orange = np.array([10, 114, 240])
upper_orange = np.array([51, 255, 255])

frame_corners = None
last_print_time = time.time()

balls_position = []
orange_balls_position = []
robot_position = None
last_robot_print_time = time.time()

cell_size = 10

while True:
    _, frame = cap.read()
    
    if frame_corners is None:
        frame_corners = draw_ROI(frame)
        if frame_corners is not None:  # Check if draw_ROI returned valid points
            frame_corners = [(int(p[0]), int(p[1])) for p in frame_corners]

    if frame_corners is not None:  # This is a new conditional block
        polygon = np.array(frame_corners[:-1])

        hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)

        green_mask = cv2.inRange(hsv, lower_green, upper_green)
        green_contours, _ = cv2.findContours(green_mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

        # Get a binary image isolating the white pixels (light)
        white_mask_light = cv2.inRange(hsv, lower_white_light, upper_white_light)
    
        # Get a binary image isolating the white pixels (shadow)
        white_mask_shadow = cv2.inRange(hsv, lower_white_shadow, upper_white_shadow)

        # Combine the white masks (light and shadow)
        white_mask = cv2.bitwise_or(white_mask_light, white_mask_shadow)
        white_contours, _ = cv2.findContours(white_mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

        # Get a binary image isolating the orange pixels
        orange_mask = cv2.inRange(hsv, lower_orange, upper_orange)
        orange_contours, _ = cv2.findContours(orange_mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    
        if green_contours:
            robot_contour = max(green_contours, key=cv2.contourArea)
            robot_center = get_center_of_contour(robot_contour)
            if robot_center is not None and cv2.pointPolygonTest(polygon, robot_center, False) >= 0:
                cv2.circle(frame, robot_center, 5, (255, 0, 0), -1)
                robot_position = (robot_center[0] - polygon[0][0], polygon[0][1] - robot_center[1])
                if time.time() - last_robot_print_time >= 3:
                    print(f"Robot at: {robot_position}")
                    if client_socket is not None:
                        robot_position = tuple(int(x) for x in robot_position)  # Convert numpy ints to python ints
                        try:
                            client_socket.send((json.dumps({"robot": robot_position}) + '\n').encode())
                        except Exception as e:
                            print(f"Error sending robot position: {e}")
                            break
                    last_robot_print_time = time.time()


        balls_position = []  # Reset the white balls position at each frame
        orange_balls_position = []  # Reset the orange balls position at each frame
    
        min_contour_area = 10  # adjust this value to suit your needs

        # red cross
        hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)

        # Get a binary image isolating the red pixels
        red_mask = cv2.inRange(hsv, lower_red, upper_red)
        red_contours, _ = cv2.findContours(red_mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

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
            if cv2.contourArea(contour) < min_contour_area:
                continue
            ball_center = get_center_of_contour(contour)
            if ball_center is not None and cv2.pointPolygonTest(polygon, ball_center, False) >= 0:
                cv2.circle(frame, ball_center, 5, (203, 192, 255), -1)
                balls_position.append((ball_center[0] - polygon[0][0], polygon[0][1] - ball_center[1]))

        # Find orange balls
        for contour in orange_contours:
            if cv2.contourArea(contour) < min_contour_area:
                continue
            ball_center = get_center_of_contour(contour)
            if ball_center is not None and cv2.pointPolygonTest(polygon, ball_center, False) >= 0:
                cv2.circle(frame, ball_center, 5, (0, 165, 255), -1)
                orange_balls_position.append((ball_center[0] - polygon[0][0], polygon[0][1] - ball_center[1]))

        if time.time() - last_print_time >= 10:
            balls_position = [tuple(int(x) for x in pos) for pos in balls_position]  # Convert numpy ints to python ints
            orange_balls_position = [tuple(int(x) for x in pos) for pos in orange_balls_position]  # Convert numpy ints to python ints
            try:
                client_socket.send((json.dumps({"white_balls": balls_position, "orange_balls": orange_balls_position}) + '\n').encode())
            except Exception as e:
                print(f"Error sending ball positions: {e}")
                break
            print(f"White balls at: {balls_position}")
            print(f"Orange balls at: {orange_balls_position}")
            last_print_time = time.time()
                
        cv2.polylines(frame, [polygon], True, (0,255,0), 2)
        cv2.imshow('Frame', frame)

    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()
if client_socket is not None:
    client_socket.close()
server_socket.close()
