import cv2
import numpy as np
from ultralytics import YOLO
from collections import defaultdict
from utils import calculateHomography, transformPoints
from pymongo import MongoClient
from time import time

# Load the YOLO model
model = YOLO("yolov8n.pt")

# Connect to the MongoDB database
# and set up data recording
client = MongoClient("")
db = client["CrowdTracking"]
collection = db["Crowd"]
lastRecorded = 0


# Connect to the RTSP stream
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

# Main loop
while cap.isOpened():
    success, frame = cap.read()
    if not success:
        raise Exception("Failed to read video stream - mapTracking.py - main loop")
    
    results = model.track(frame, persist=True, show=False, imgsz=1280, verbose=True)

    if results[0].boxes is not None and hasattr(results[0].boxes, 'id'):
        boxes = results[0].boxes.xywh.cpu().numpy()
        trackIDs = results[0].boxes.id.int().cpu().numpy()

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

        # Record the number of people in the frame every second
        currentTime = time.time()
        if currentTime - lastRecorded >= 1:
            frameId = int(cap.get(cv2.CAP_PROP_POS_FRAMES))
            totalPeople = len(np.unique(trackIDs))

            record = {
                "frameId": frameId,
                "timestamp": currentTime.strftime("%d-%m-%Y %H:%M:%S"),
                "totalPeople": totalPeople
            }
            collection.insert_one(record)
            lastRecorded = currentTime

        video.write(annotatedFrame)
        
        cv2.imshow("Map Tracking", annotatedFrame)
        cv2.imshow("Camera Feed", frame)
        cv2.waitKey(1)
        

cap.release()
video.release()
cv2.destroyAllWindows()
