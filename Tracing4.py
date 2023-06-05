import cv2
import numpy as np
import time
import math

def get_center_of_contour(contour):
    M = cv2.moments(contour)
    if M["m00"] == 0:
        return None
    else:
        return (int(M["m10"] / M["m00"]), int(M["m01"] / M["m00"]))

def calculate_distance(point1, point2):
    x1, y1 = point1
    x2, y2 = point2
    return math.sqrt((x2 - x1) ** 2 + (y2 - y1) ** 2)

cap = cv2.VideoCapture(0)

lower_red = np.array([0, 100, 100])
upper_red = np.array([10, 255, 255])

lower_green = np.array([36, 25, 25])
upper_green = np.array([86, 255, 255])

# define range for white color
lower_white = np.array([0, 0, 200])
upper_white = np.array([180, 25, 255])

robot_center = None
frame_corners = None
alpha = 0.2
touching = False

# To store the time of last location print
last_print_time = time.time()

while True:
    _, frame = cap.read()
    
    hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
    
    red_mask = cv2.inRange(hsv, lower_red, upper_red)
    green_mask = cv2.inRange(hsv, lower_green, upper_green)
    
    # Get a binary image isolating the white pixels
    white_mask = cv2.inRange(hsv, lower_white, upper_white)
    
    red_contours, _ = cv2.findContours(red_mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    green_contours, _ = cv2.findContours(green_mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

    # Find contours in the white image
    white_contours, _ = cv2.findContours(white_mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    
    largest_rectangle = None
    if red_contours:
        largest_rectangle = max(red_contours, key=cv2.contourArea)
        epsilon = 0.1 * cv2.arcLength(largest_rectangle, True)
        approx = cv2.approxPolyDP(largest_rectangle, epsilon, True)
        if len(approx) == 4:
            frame_corners = [tuple(c[0]) for c in approx]
            cv2.drawContours(frame, [approx], -1, (0, 255, 0), 3)
    
    if green_contours:
        robot_contour = max(green_contours, key=cv2.contourArea)
        robot_center = get_center_of_contour(robot_contour)
        if robot_center is not None:
            cv2.circle(frame, robot_center, 5, (255, 0, 0), -1)
            if frame_corners is not None and len(frame_corners) == 4:
                for i in range(4):
                    cv2.line(frame, frame_corners[i], frame_corners[(i + 1) % 4], (0, 0, 255), 2)
                polygon = np.array(frame_corners)
                if cv2.pointPolygonTest(polygon, robot_center, False) >= 0:
                    if not touching:
                        touching = True
                        print("Robot is touching the frame!")
                else:
                    touching = False
    
    # Calculate the centers of the white contours (balls)
    for contour in white_contours:
        ball_center = get_center_of_contour(contour)
        if ball_center is not None:
            cv2.circle(frame, ball_center, 5, (203, 192, 255), -1)  # Draw a pink dot
            
            # Print the location of each ball every 10 seconds
            if time.time() - last_print_time >= 10:
                print(f"Ball at: {ball_center}")
                last_print_time = time.time()
    
    cv2.imshow('Frame', frame)
    
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()
