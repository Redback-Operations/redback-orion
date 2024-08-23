import cv2
import numpy as np
from ultralytics import YOLO
from collections import defaultdict
from utils import calculateHomography, transformPoints

model = YOLO("yolov8n.pt")

rtspUrl = ""
cap = cv2.VideoCapture(rtspUrl)

trackHistory = defaultdict(list)

from floorReplica import floorReplica
canvasHeight = 1000
canvasWidth = 700
tilesX = 25
tilesY = 15
floorImage = floorReplica(canvasHeight, canvasWidth, tilesX, tilesY, rtspUrl)

height, width, channels = floorImage.shape

fourcc = cv2.VideoWriter_fourcc(*'mp4v')
video = cv2.VideoWriter('output.mp4', fourcc, 20.0, (width, height))

ptsSRC = np.array([[28, 1158], [2120, 1112], [1840, 488], [350, 518], [468, 1144]])
ptsDST = np.array([[0, 990], [699, 988], [693, 658], [0, 661], [141, 988]])

homographyMatrix = calculateHomography(ptsSRC, ptsDST)

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

        video.write(annotatedFrame)
        
        cv2.imshow("Map Tracking", annotatedFrame)
        cv2.waitKey(1)
        

cap.release()
video.release()
cv2.destroyAllWindows()
