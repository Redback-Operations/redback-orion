import cv2
import numpy as np
from ultralytics import YOLO
from collections import defaultdict
from utils import calculateHomography, transformPoints
from database import Database
from floorReplica import floorReplica
import time as time_module

class CameraProcessor:
    def __init__(self):
        # initialize the YOLO model
        # RTSP stream URL for the video feed
        # trackHistory is a dictionary to store the movement history of each person
        # floorImage is a replica of the floor plan for annotation
        # homographyMatrix is the homography matrix for transforming points
        # db is an instance of the Database class
        # lastRecorded is the timestamp of the last recorded data
        self.model = YOLO("yolov8n.pt")
        self.rtspUrl = ''
        self.cap = cv2.VideoCapture(self.rtspUrl)
        self.trackHistory = defaultdict(list)
        self.floorImage = floorReplica(1000, 700, 25, 15, self.rtspUrl)
        self.homographyMatrix = self.calculateHomography()
        self.db = Database()
        self.lastRecorded = 0

    # Function to calculate the homography matrix
    def calculateHomography(self):
        ptsSRC = np.array([[28, 1158], [2120, 1112], [1840, 488], [350, 518], [468, 1144]])
        ptsDST = np.array([[0, 990], [699, 988], [693, 658], [0, 661], [141, 988]])
        return calculateHomography(ptsSRC, ptsDST)

    def processFrame(self, frame):
        # the try block is used to handle exceptions, when no detections are available
        try:
            results = self.model.track(frame, persist=True, show=False, imgsz=1280, verbose=False)
            
            # Create copies of the frame for annotations
            annotatedFrame = frame.copy()
            floorAnnotatedFrame = self.floorImage.copy()
            totalPeople = 0
            frameId = int(self.cap.get(cv2.CAP_PROP_POS_FRAMES))
            
            if results[0].boxes is not None and hasattr(results[0].boxes, 'id'):
                boxes = results[0].boxes.xywh.cpu().numpy()
                trackIDs = results[0].boxes.id.int().cpu().numpy()
                classes = results[0].boxes.cls.cpu().numpy()
                
                # Filter for human detections (assuming 'person' class is 0)
                human_indices = classes == 0
                human_boxes = boxes[human_indices]
                human_trackIDs = trackIDs[human_indices]
                
                # Block to draw the movement history of each person
                for trackID in np.unique(human_trackIDs):
                    history = self.trackHistory[trackID]
                    if len(history) > 1:
                        points = np.array(history, dtype=np.int32)
                        newPoints = transformPoints(points, self.homographyMatrix)
                        newPoints = newPoints.astype(np.int32)
                        
                        cv2.polylines(floorAnnotatedFrame, [newPoints], isClosed=False, color=(0, 0, 255), thickness=2)
                
                # Block to draw bounding boxes and IDs
                for box, trackID in zip(human_boxes, human_trackIDs):
                    x, y, w, h = box
                    center = (int(x), int(y + h / 2))
                    self.trackHistory[trackID].append(center)
                    
                    if len(self.trackHistory[trackID]) > 50:
                        self.trackHistory[trackID].pop(0)
                    
                    # Draw bounding box and ID on the original frame
                    cv2.rectangle(annotatedFrame, (int(x - w/2), int(y - h/2)), (int(x + w/2), int(y + h/2)), (0, 255, 0), 2)  # Green color
                    cv2.putText(annotatedFrame, f"ID: {int(trackID)}", (int(x - w/2), int(y - h/2) - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)  # Green color
                    
                    totalPeople += 1
            else:
                print("No human detections or IDs available.")
        
        except AttributeError as e:
            print(f"An AttributeError occurred: {e}")
        except Exception as e:
            print(f"An unexpected error occurred: {e}")
    
        # Always insert data, even if no people are detected
        self.db.insertRecord(totalPeople, frameId)
        
        return annotatedFrame, floorAnnotatedFrame

    # Function to run the camera processor
    def run(self):
        while True:
            success, frame = self.cap.read()
            if not success:
                raise Exception("Failed to read video stream - cameraProcessor.py - run")
            else:
                annotatedFrame, floorAnnotatedFrame = self.processFrame(frame)
                cv2.imshow("Annotated Frame", annotatedFrame)
                cv2.imshow("Floor Annotation", floorAnnotatedFrame)
                if cv2.waitKey(1) & 0xFF == ord('q'):
                    break
        self.release()

    # Function to get the raw frame from the video stream
    def getFrame(self):
        while True:
            success, frame = self.cap.read()
            if not success:
                raise Exception("Failed to read video stream - cameraProcessor.py - getFrame")
            else:
                annotatedFrame, _ = self.processFrame(frame)
                ret, buffer = cv2.imencode('.jpg', annotatedFrame)
                frame = buffer.tobytes()
                yield (b'--frame\r\n'
                    b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')

    # Function to get the annotated frame with floor plan
    def getAnnotatedFrame(self):
        while True:
            success, frame = self.cap.read()
            if not success:
                raise Exception("Failed to read video stream - cameraProcessor.py - getAnnotatedFrame")
            else:
                _, floorAnnotatedFrame = self.processFrame(frame)
                ret, buffer = cv2.imencode('.jpg', floorAnnotatedFrame)
                frame = buffer.tobytes()
                yield (b'--frame\r\n'
                    b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')

    def release(self):
        self.cap.release()
        cv2.destroyAllWindows()
