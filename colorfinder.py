import cv2
import numpy as np

def nothing(x):
    pass

# Create a black image, a window
cv2.namedWindow('image')

# create trackbars for color change
cv2.createTrackbar('H_low','image',0,179,nothing)
cv2.createTrackbar('H_high','image',179,179,nothing)

cv2.createTrackbar('S_low','image',0,255,nothing)
cv2.createTrackbar('S_high','image',255,255,nothing)

cv2.createTrackbar('V_low','image',0,255,nothing)
cv2.createTrackbar('V_high','image',255,255,nothing)

cap = cv2.VideoCapture(0)

while(1):
    ret, frame = cap.read()
    if not ret:
        break

    # Convert BGR to HSV
    hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)

    # get current positions of four trackbars
    h_low = cv2.getTrackbarPos('H_low','image')
    h_high = cv2.getTrackbarPos('H_high','image')
    s_low = cv2.getTrackbarPos('S_low','image')
    s_high = cv2.getTrackbarPos('S_high','image')
    v_low = cv2.getTrackbarPos('V_low','image')
    v_high = cv2.getTrackbarPos('V_high','image')

    # define range of color in HSV
    lower = np.array([h_low,s_low,v_low])
    upper = np.array([h_high,s_high,v_high])

    # Threshold the HSV image to get only selected colors
    mask = cv2.inRange(hsv, lower, upper)

    cv2.imshow('image',mask)
    k = cv2.waitKey(1) & 0xFF
    if k == 27:    # ESC key to exit
        break

cap.release()
cv2.destroyAllWindows()
