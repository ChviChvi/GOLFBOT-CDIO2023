import cv2
import numpy as np
from robot_movement import RobotMovement
from ev3dev.ev3 import *


# Initialize the robot
robot = RobotMovement()

# Initialize the motors.
left_motor = LargeMotor('outB')  # Change 'outB' and 'outC' to the ports your motors are connected to
right_motor = LargeMotor('outC')

# Initialize the robot connection and other necessary setup

def get_center_of_contour(contour):
    M = cv2.moments(contour)
    if M["m00"] == 0:
        return None
    else:
        return (int(M["m10"] / M["m00"]), int(M["m01"] / M["m00"]))

# assuming your camera is available at index 0
cap = cv2.VideoCapture(0)

# define range for red color
lower_red = np.array([0, 100, 100])
upper_red = np.array([10, 255, 255])

# define range for green color
lower_green = np.array([36, 25, 25])
upper_green = np.array([86, 255, 255])

while True:
    _, frame = cap.read()

    #testing
    # Get the frame size
    frame_height, frame_width = frame.shape[:2]

    # Define the right and left boundaries
    right_boundary = frame_width * 0.75
    left_boundary = frame_width * 0.25

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

    # Find the largest red contour, which should be the rectangle
    largest_rectangle = None
    if red_contours:
        largest_rectangle = max(red_contours, key=cv2.contourArea)

    # Calculate the center of the largest green contour, which should be the robot
    if green_contours:
        robot_contour = max(green_contours, key=cv2.contourArea)
        robot_center = get_center_of_contour(robot_contour)
        if robot_center is not None:
            print("Robot's Position: ", robot_center)

    # Control the robot based on its position
    if robot_center is not None:
            robot_x = robot_center[0]
            if robot_x < right_boundary:
                robot.move_forward(500, 2000)
                left_motor.run_timed(time_sp=2000, speed_sp=500)
                right_motor.run_timed(time_sp=2000, speed_sp=500)
            elif robot_x > right_boundary:
                robot.turn_around(300, 900)
                left_motor.run_timed(time_sp=900, speed_sp=-300)
                right_motor.run_timed(time_sp=900, speed_sp=300)
            elif robot_x > left_boundary:
                robot.move_backward(500, 2000)
                left_motor.run_timed(time_sp=2000, speed_sp=-500)
                right_motor.run_timed(time_sp=2000, speed_sp=-500)
            elif robot_x < left_boundary:
                robot.turn_around(300, 900)
                left_motor.run_timed(time_sp=900, speed_sp=-300)
                right_motor.run_timed(time_sp=900, speed_sp=300)


    # Draw the rectangle contour and the robot center on the original frame
    if largest_rectangle is not None:
        cv2.drawContours(frame, [largest_rectangle], -1, (0, 255, 0), 3)

    # Only draw the robot center if it's defined
    if robot_center is not None:
        cv2.circle(frame, robot_center, 5, (255, 0, 0), -1)

    # Display the frame
    cv2.imshow('Frame', frame)

    # Break the loop on 'q' key press
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

# When everything is done, release the capture
cap.release()

# Close all OpenCV windows
cv2.destroyAllWindows()
