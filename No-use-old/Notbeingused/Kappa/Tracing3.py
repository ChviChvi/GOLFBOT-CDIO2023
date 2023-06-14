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

# assuming your camera is available at index 0
cap = cv2.VideoCapture(0)

# define range for red color
lower_red = np.array([0, 100, 100])
upper_red = np.array([10, 255, 255])

# define range for green color
lower_green = np.array([36, 25, 25])
upper_green = np.array([86, 255, 255])

robot_center = None
frame_corners = None  # Variable to store the four corners of the frame
alpha = 0.2  # Smoothing factor

touching = False  # Variable to track if the blue dot touches the frame

while True:
    _, frame = cap.read()
    
    # Convert the frame to HSV
    hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
    
    # Get a binary (black and white) image isolating the red pixels
    red_mask = cv2.inRange(hsv, lower_red, upper_red)

    # Get a binary image isolating the green pixels
    green_mask = cv2.inRange(hsv, lower_green, upper_green)
    
    # Find contours in the red image
    red_contours, _ = cv2.findContours(red_mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

    # Find contours in the green image
    green_contours, _ = cv2.findContours(green_mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

    # Find the largest red contour, which should be the frame
    largest_rectangle = None
    if red_contours:
        largest_rectangle = max(red_contours, key=cv2.contourArea)
        epsilon = 0.1 * cv2.arcLength(largest_rectangle, True)
        approx = cv2.approxPolyDP(largest_rectangle, epsilon, True)
        if len(approx) == 4:
            frame_corners = [tuple(c[0]) for c in approx]
            cv2.drawContours(frame, [approx], -1, (0, 255, 0), 3)
    
    # Calculate the center of the largest green contour, which should be the robot
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
    
    # Display the frame
    cv2.imshow('Frame', frame)
    
    # Break the loop on 'q' key press
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

# When everything is done, release the capture
cap.release()

# Close all OpenCV windows
cv2.destroyAllWindows()
