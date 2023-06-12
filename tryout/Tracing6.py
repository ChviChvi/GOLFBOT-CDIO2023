import cv2
import numpy as np
import time
import matplotlib.pyplot as plt
import matplotlib.patches as patches

def get_color(event, x, y, flags, param):
    if event == cv2.EVENT_LBUTTONUP:
        hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
        color = hsv[y, x]
        print(f"HSV color: {color}")
        param.append(color)

def calibrate_colors(img, num_colors=3):
    colors = []
    cv2.namedWindow('image')
    cv2.setMouseCallback('image', get_color, param=colors)
    while len(colors) < num_colors:
        cv2.imshow('image', img)
        if cv2.waitKey(20) & 0xFF == 27: 
            break
    cv2.destroyAllWindows()
    return colors

def get_center_of_contour(contour):
    M = cv2.moments(contour)
    if M["m00"] == 0:
        return None
    else:
        return (int(M["m10"] / M["m00"]), int(M["m01"] / M["m00"]))

def draw_ROI(frame):
    fig,ax = plt.subplots(1)
    ax.imshow(cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)) 
    ROI = plt.ginput(4)
    if len(ROI) > 0: 
        ROI.append(ROI[0])
        rect = patches.Polygon(ROI, linewidth=1, edgecolor='r', facecolor='none')
        ax.add_patch(rect) 
        plt.show()
    else:
        print("No valid points were selected.")
        ROI = None
    return ROI

cap = cv2.VideoCapture(0)
_, frame = cap.read()

colors = calibrate_colors(frame)

lower_orange = np.array([max(colors[0][0]-10, 0), max(colors[0][1]-40, 0), max(colors[0][2]-40, 0)])
upper_orange = np.array([min(colors[0][0]+10, 180), min(colors[0][1]+40, 255), min(colors[0][2]+40, 255)])

lower_white = np.array([max(colors[1][0]-10, 0), max(colors[1][1]-40, 0), max(colors[1][2]-40, 0)])
upper_white = np.array([min(colors[1][0]+10, 180), min(colors[1][1]+40, 255), min(colors[1][2]+40, 255)])

lower_robot = np.array([max(colors[2][0]-10, 0), max(colors[2][1]-40, 0), max(colors[2][2]-40, 0)])
upper_robot = np.array([min(colors[2][0]+10, 180), min(colors[2][1]+40, 255), min(colors[2][2]+40, 255)])

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
        if frame_corners is not None:
            frame_corners = [(int(p[0]), int(p[1])) for p in frame_corners]

    if frame_corners is not None:
        polygon = np.array(frame_corners[:-1])
        hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
        mask_orange = cv2.inRange(hsv, lower_orange, upper_orange)
        mask_white = cv2.inRange(hsv, lower_white, upper_white)
        mask_robot = cv2.inRange(hsv, lower_robot, upper_robot)
        mask_orange = cv2.morphologyEx(mask_orange, cv2.MORPH_OPEN, np.ones((5, 5)))
        mask_white = cv2.morphologyEx(mask_white, cv2.MORPH_OPEN, np.ones((5, 5)))
        mask_robot = cv2.morphologyEx(mask_robot, cv2.MORPH_OPEN, np.ones((5, 5)))

        contours_orange, _ = cv2.findContours(mask_orange, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        contours_white, _ = cv2.findContours(mask_white, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        contours_robot, _ = cv2.findContours(mask_robot, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

        orange_balls_position = [get_center_of_contour(contour) for contour in contours_orange]
        balls_position = [get_center_of_contour(contour) for contour in contours_white]
        robot_position = [get_center_of_contour(contour) for contour in contours_robot]

        for pos in orange_balls_position:
            cv2.circle(frame, pos, 5, (0, 0, 255), -1)

        for pos in balls_position:
            cv2.circle(frame, pos, 5, (0, 255, 0), -1)

        if len(robot_position) > 0:
            cv2.circle(frame, robot_position[0], 5, (255, 0, 0), -1)

        cv2.polylines(frame, [polygon], True, (0, 0, 255), 2)
    
    cv2.imshow("Frame", frame)

    key = cv2.waitKey(1)
    if key == 27:  # ESC key to exit
        break

cv2.destroyAllWindows()
cap.release()
