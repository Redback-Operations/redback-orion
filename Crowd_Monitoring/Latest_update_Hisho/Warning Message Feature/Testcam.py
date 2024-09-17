import cv2
import numpy as np
from ultralytics import YOLO
from collections import defaultdict
from utils import calculateHomography, transformPoints
from pymongo import MongoClient
import time as time_module
from datetime import datetime

# Load the YOLO model
model = YOLO("yolov8n.pt")

# Connect to the MongoDB database
# and set up data recording
client = MongoClient("")
db = client["Crowd_Monitoring"]
collection = db["Crowd_Count"]

lastRecorded = time_module.time()

# Connect to the RTSP stream
# rtspUrl = "rtsp://"
rtspUrl = 0
cap = cv2.VideoCapture(rtspUrl)

trackHistory = defaultdict(list)

# Load the floor image
from floorReplica import floorReplica
canvasHeight = 1000
canvasWidth = 700
tilesX = 25
tilesY = 15
floorImage = floorReplica(canvasHeight, canvasWidth, tilesX, tilesY, rtspUrl)

height, width, channels = floorImage.shape

# Define the codec and create a VideoWriter object
fourcc = cv2.VideoWriter_fourcc(*'mp4v')
video = cv2.VideoWriter('output.mp4', fourcc, 20.0, (width, height))

# Define the source and destination points for the homography matrix
# Calculate the homography matrix
ptsSRC = np.array([[28, 1158], [2120, 1112], [1840, 488], [350, 518], [468, 1144]])
ptsDST = np.array([[0, 990], [699, 988], [693, 658], [0, 661], [141, 988]])
homographyMatrix = calculateHomography(ptsSRC, ptsDST)

# Variables for speed monitoring
speed_threshold = 20  # Speed threshold to trigger a warning (adjust as needed)
tracking_distance_threshold = 50  # Maximum allowed distance to associate a person in consecutive frames
prev_positions = {}  # To track positions across frames

# Function to associate detected persons between frames based on proximity
def associate_persons(prev_positions, current_positions):
    matched_positions = {}
    for trackID, curr_pos in current_positions.items():
        # Find the closest previous position for each current position
        min_distance = float('inf')
        matched_prev_pos = None
        for prev_trackID, prev_pos in prev_positions.items():
            distance = np.linalg.norm(np.array(curr_pos) - np.array(prev_pos))
            if distance < min_distance and distance < tracking_distance_threshold:
                min_distance = distance
                matched_prev_pos = prev_pos
        if matched_prev_pos is not None:
            matched_positions[trackID] = (matched_prev_pos, curr_pos)
    return matched_positions

# Main loop
while True:
    success, frame = cap.read()
    if not success:
        print("Failed to read video stream.")
        break
    
    results = model.track(frame, persist=True, show=False, imgsz=1280, verbose=True)
    annotatedFrame = floorImage.copy()

    # Process camera results with box coordinates and confidence scores
    current_positions = {}
    for result in results:
        boxes_camera = result.boxes.cpu().numpy()
        for box in boxes_camera:
            x1, y1, x2, y2 = map(int, box.xyxy[0])
            conf = box.conf[0]
            cls = int(box.cls[0])

            if cls == 0:  # Assuming class 0 is person
                cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 255, 0), 2)
                cv2.putText(frame, f'Person: {conf:.2f}', (x1, y1 - 10),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)
                
                center_x, center_y = (x1 + x2) // 2, (y1 + y2) // 2
                current_positions[int(conf)] = (center_x, center_y)

    # Check for speed changes
    sudden_speed_detected = False
    if prev_positions:
        matched_positions = associate_persons(prev_positions, current_positions)
        for trackID, (prev_pos, curr_pos) in matched_positions.items():
            speed = np.linalg.norm(np.array(curr_pos) - np.array(prev_pos))
            if speed > speed_threshold:
                sudden_speed_detected = True
                break

    prev_positions = current_positions  # Update previous positions for the next frame

    # Display warning if sudden speed detected
    if sudden_speed_detected:
        cv2.putText(frame, 'Warning: Sudden Speed Change!', (50, 100),
                    cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 3)  # Display warning

    try:
        if results[0].boxes is not None:
            if hasattr(results[0].boxes, 'id'):
                if results[0].boxes.id.numel() > 0:
                    boxes = results[0].boxes.xywh.cpu().numpy()
                    trackIDs = results[0].boxes.id.cpu().numpy()
                    annotatedFrame = floorImage.copy()

                    for trackID in np.unique(trackIDs):
                        history = trackHistory[trackID]
                        if len(history) > 1:
                            points = np.array(history, dtype=np.int32)
                            newPoints = transformPoints(points, homographyMatrix)
                            newPoints = newPoints.astype(np.int32)
                            cv2.polylines(annotatedFrame, [newPoints], isClosed=False, color=(0, 0, 255), thickness=2)

                    for box, trackID in zip(boxes, trackIDs):
                        x, y, w, h = box
                        center = (int(x), int(y + h / 2))
                        trackHistory[trackID].append(center)

                        if len(trackHistory[trackID]) > 50:
                            trackHistory[trackID].pop(0)

                    currentTime = time_module.time()
                    if currentTime - lastRecorded > 1:
                        frameId = int(cap.get(cv2.CAP_PROP_POS_FRAMES))
                        totalPeople = len(np.unique(trackIDs))
                        timestamp = time_module.strftime("%d-%m-%Y %H:%M:%S", time_module.localtime(currentTime))
                        record = {
                            "frameId": frameId,
                            "timestamp": timestamp,
                            "totalPeople": totalPeople
                        }
                        collection.insert_one(record)
                        lastRecorded = currentTime
                    video.write(annotatedFrame)
                else:
                    print("No objects detected. No IDs available.")
            else:
                print("The 'id' attribute is not present in the boxes.")
        else:
            print("No boxes detected. The 'boxes' attribute is None.")
    except AttributeError as e:
        print(f"An AttributeError occurred: {e}")
    except Exception as e:
        print(f"An unexpected error occurred: {e}")

    cv2.imshow("Map Tracking", annotatedFrame)
    cv2.imshow("Camera Feed", frame)
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()
