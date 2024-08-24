import cv2
import numpy as np
from ultralytics import YOLO
from collections import defaultdict
from utils import calculateHomography, transformPoints
from database import Database
from collections import defaultdict
from floorReplica import floorReplica

class CameraProcessor:
    def __init__(self):
        self.model = YOLO("yolov8n.pt")
        self.rtspUrl = "rtsp://"
        self.cap = cv2.VideoCapture(self.rtspUrl)
        self.trackHistory = defaultdict(list)
        self.floorImage = floorReplica(1000, 700, 25, 15, self.rtspUrl)
        self.hormographyMatrix = self.calculateHomography()
        self.db = Database()

    def calculateHomography(self):
        ptsSRC = np.array([[28, 1158], [2120, 1112], [1840, 488], [350, 518], [468, 1144]])
        ptsDST = np.array([[0, 990], [699, 988], [693, 658], [0, 661], [141, 988]])
        return calculateHomography(ptsSRC, ptsDST)
    
    def processFrame(self, frame):
        results = self.model.track(frame, persist=True, show=False, imgsz=1280, verbose=False)
        
        if results[0].boxes is not None and hasattr(results[0].boxes, 'id'):
            boxes = results[0].boxes.xywh.cpu().numpy()
            trackIDs = results[0].boxes.id.int().cpu().numpy()
            annotatedFrame = self.floorImage.copy()

            for trackID in np.unique(trackIDs):
                history = self.trackHistory[trackID]
                if len(history) > 1:
                    points = np.array(history)
                    newPoints = transformPoints(points, self.hormographyMatrix)
                    newPoints = newPoints.astype(np.int32)
                    cv2.polylines(annotatedFrame, [newPoints], isClosed=True, color=(0, 0, 255), thickness=2)
            
            for box, trackID in zip(boxes, trackIDs):
                x, y, w, h = box
                center = (int(x), int(y + h / 2))
                self.trackHistory[trackID].append(center)

                if len(self.trackHistory[trackID]) > 50:
                    self.trackHistory[trackID].pop(0)

            totalPeople = len(np.unique(trackIDs))
            frameId = int(self.cap.get(cv2.CAP_PROP_POS_FRAMES))
            self.db.insert(totalPeople, frameId)

            return annotatedFrame, frame
        
        return self.floorImage.copy(), frame
    
    def run(self):
        while True:
            success, frame = self.cap.read()
            if not success:
                raise Exception("Failed to read video stream - cameraProcessor.py - run")
            else:
                annotatedFrame, originalFrame = self.processFrame(frame)
                cv2.imshow("Annotated Frame", annotatedFrame)
                cv2.imshow("Live Tracking", originalFrame)
                if cv2.waitKey(1) & 0xFF == ord('q'):
                    break
        self.release()

    def getFrame(self):
        success, frame = self.cap.read()
        if not success:
            raise Exception("Failed to read video stream - cameraProcessor.py - getFrame")
        else:
            ret, buffer = cv2.imencode('.jpg', frame)
            frame = buffer.tobytes()
            yield (b'--frame\r\n'
                   b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')
    
    def getAnnotatedFrame(self):
        success, frame = self.cap.read()
        if not success:
            raise Exception("Failed to read video stream - cameraProcessor.py - getAnnotatedFrame")
        else:
            annotatedFrame = self.processFrame(frame)
            ret, buffer = cv2.imencode('.jpg', annotatedFrame)
            frame = buffer.tobytes()
            yield (b'--frame\r\n'
                   b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')
            
    def release(self):
        self.cap.release()
        cv2.destroyAllWindows()
            
    