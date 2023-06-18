import cv2

# Initialize tracker with first frame and bounding box
tracker = cv2.TrackerMOSSE_create()
video = cv2.VideoCapture('video.mp4')

# Read the first frame
ok, frame = video.read()
if not ok:
    print('Cannot read video file')
    exit()

# Define an initial bounding box (this needs to be provided or detected)
bbox = (287, 23, 86, 320)

# Initialize tracker with first frame and bounding box
ok = tracker.init(frame, bbox)

while True:
    # Read a new frame
    ok, frame = video.read()
    if not ok:
        break

    # Update tracker
    ok, bbox = tracker.update(frame)

    # Draw bounding box
    if ok:
        p1 = (int(bbox[0]), int(bbox[1]))
        p2 = (int(bbox[0] + bbox[2]), int(bbox[1] + bbox[3]))
        cv2.rectangle(frame, p1, p2, (255, 0, 0), 2, 1)
    else:
        # Tracking failure
        cv2.putText(frame, "Tracking failure detected", (100, 80),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.75, (0, 0, 255), 2)

    # Display result
    cv2.imshow("Tracking", frame)

    # Exit if ESC key is pressed
    if cv2.waitKey(1) & 0xFF == 27:  # Esc key
        break