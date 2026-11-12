import cv2
import numpy as np
from ultralytics import YOLO
from collections import defaultdict
from utils import calculateHomography, transformPoints

# from database import Database
from floorReplica import floorReplica
import time as time_module
from opticalFlow import OpticalFlow
from congestionDetection import CongestionDetection
from dwellTime import DwellTimeAnalysis


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
        self.rtspUrl = 0
        self.cap = cv2.VideoCapture(self.rtspUrl)
        self.trackHistory = defaultdict(list)
        self.floorImage = floorReplica(1000, 700, 25, 15, self.rtspUrl)
        self.homographyMatrix = self.calculateHomography()
        # self.db = Database()
        #self.lastRecorded = 0
        
        # initialise the variables for counting the current frame ID
        # initialise the congestion detection module using the homography matrix
        # initialise the optical flow amd the dwell time analysis module
        self.currentFrameId = 0
        self.congestionDetection = CongestionDetection(
            self.homographyMatrix, debug=True
        )
        self.opticalFlow = OpticalFlow(predictionStep=5, predictionScale=3)
        self.dwellTimeAnalysis = DwellTimeAnalysis(self.homographyMatrix)


        self.lastFlowVisualizationTime = 0
        self.flowVisualizationInterval = 5  # Increased to 5 seconds
        self.flowVisualizationDuration = 3  # Show for 3 seconds only
        self.showFlowVisualization = False

        self.showDwellTime = True

    # Function to calculate the homography matrix
    def calculateHomography(self):
        ptsSRC = np.array(
            [[28, 1158], [2120, 1112], [1840, 488], [350, 518], [468, 1144]]
        )
        ptsDST = np.array([[0, 990], [699, 988], [693, 658], [0, 661], [141, 988]])
        return calculateHomography(ptsSRC, ptsDST)

    def processFrame(self, frame):
        # Calculate optical flow for this frame
        #  and initialise the current position list to store the current positions of detected people
        flow = self.opticalFlow.calculateFlow(frame)
        currentPositions = []

        # Check if it's time to update the flow visualization based on the interval
        currentTime = time_module.time()

        # Start visualization if interval has passed
        if (
            currentTime - self.lastFlowVisualizationTime
            >= self.flowVisualizationInterval
        ):
            self.showFlowVisualization = True
            self.lastFlowVisualizationTime = currentTime


        # the try block is used to handle exceptions, when no detections are available
        try:
            results = self.model.track(
                frame, persist=True, show=False, imgsz=1280, verbose=False
            )

            # Create copies of the frame for annotations
            # and initialise the total people count
            annotatedFrame = frame.copy()
            floorAnnotatedFrame = self.floorImage.copy()
            totalPeople = 0

            # Get predicted positions based on optical flow
            # using the if statement to check if the flow is available
            # and the visualisation is active
            predictedPositions = {}
            if flow is not None and self.showFlowVisualization:
                predictedPositions = self.opticalFlow.predictPosition(
                    self.trackHistory, flow
                )

            # verify if the bounding boxes were detected and having the id attribute
            # get the boxes coordinates, track IDs and classes
            if results[0].boxes is not None and hasattr(results[0].boxes, "id"):
                boxes = results[0].boxes.xywh.cpu().numpy()
                trackIDs = results[0].boxes.id.int().cpu().numpy()
                classes = results[0].boxes.cls.cpu().numpy()

                # Filter for human detections (assuming 'person' class is 0)
                human_indices = classes == 0
                human_boxes = boxes[human_indices]
                human_trackIDs = trackIDs[human_indices]

                # Store current positions of all detected people
                currentPositions = []

                # Process each tracked person by iterating through the unique track IDs
                # and draw their history on the floor plan
                for trackID in np.unique(human_trackIDs):
                    history = self.trackHistory[trackID]
                    if len(history) > 1:
                        points = np.array(history, dtype=np.int32)

                        # Transform points to floor coordinates
                        floorPoints = transformPoints(points, self.homographyMatrix)
                        floorPoints = floorPoints.astype(np.int32)

                        # Draw the history trail on floor plan
                        cv2.polylines(
                            floorAnnotatedFrame,
                            [floorPoints],
                            isClosed=False,
                            color=(0, 0, 255),
                            thickness=2,
                        )

                        # Calculate and visualize trajectory if predicted position exists and visualization is active
                        if self.showFlowVisualization and trackID in predictedPositions:
                            # Get predicted trajectory for this person (shorter now due to reduced predictionStep)
                            trajectory = self.opticalFlow.predictTrajectory(
                                trackID, history, predictedPositions[trackID]
                            )

                            # Draw predicted trajectory on annotated frame if visualization is active
                            if len(trajectory) >= 2:
                                # Draw predicted path on camera view
                                points = np.array(trajectory, dtype=np.int32)
                                cv2.polylines(
                                    annotatedFrame,
                                    [points],
                                    isClosed=False,
                                    color=(0, 255, 255),
                                    thickness=2,
                                )

                                # Add arrow at the end to indicate direction
                                lastPoint = trajectory[-2]
                                endPoint = trajectory[-1]
                                cv2.arrowedLine(
                                    annotatedFrame,
                                    (int(lastPoint[0]), int(lastPoint[1])),
                                    (int(endPoint[0]), int(endPoint[1])),
                                    (0, 255, 255),
                                    3,
                                    tipLength=0.5,
                                )

                                # Also draw on floor plan
                                floorTrajectory = transformPoints(
                                    np.array(trajectory), self.homographyMatrix
                                )
                                floorTrajectory = floorTrajectory.astype(np.int32)
                                cv2.polylines(
                                    floorAnnotatedFrame,
                                    [floorTrajectory],
                                    isClosed=False,
                                    color=(0, 255, 255),
                                    thickness=2,
                                )

                                # Add arrow on floor plan as well
                                # Check if there are at least two points to draw an arrow
                                # and draw the arrow to indicate direction
                                if len(floorTrajectory) >= 2:
                                    floorLast = floorTrajectory[-2]
                                    floorEnd = floorTrajectory[-1]
                                    cv2.arrowedLine(
                                        floorAnnotatedFrame,
                                        (int(floorLast[0]), int(floorLast[1])),
                                        (int(floorEnd[0]), int(floorEnd[1])),
                                        (0, 255, 255),
                                        3,
                                        tipLength=0.5,
                                    )

                # Block to draw bounding boxes and IDs
                for box, trackID in zip(human_boxes, human_trackIDs):
                    x, y, w, h = box
                    center = (int(x), int(y + h / 2))
                    self.trackHistory[trackID].append(center)
                    currentPositions.append(center)

                    if len(self.trackHistory[trackID]) > 50:
                        self.trackHistory[trackID].pop(0)

                    # Draw bounding box and ID on the original frame
                    cv2.rectangle(
                        annotatedFrame,
                        (int(x - w / 2), int(y - h / 2)),
                        (int(x + w / 2), int(y + h / 2)),
                        (0, 255, 0),
                        2,
                    )
                    cv2.putText(
                        annotatedFrame,
                        f"ID: {int(trackID)}",
                        (int(x - w / 2), int(y - h / 2) - 10),
                        cv2.FONT_HERSHEY_SIMPLEX,
                        0.5,
                        (0, 255, 0),
                        2,
                    )

                    # If showing flow visualization, add predicted position indicator
                    if self.showFlowVisualization and trackID in predictedPositions:
                        predictedX, predictedY = predictedPositions[trackID]
                        cv2.circle(
                            annotatedFrame, (predictedX, predictedY), 5, (0, 255, 255), -1
                        )  # Yellow dot

                    totalPeople += 1

                # Calculate congestion zones using the separate CongestionDetection class
                self.congestionZones = self.congestionDetection.identifyCongestionZones(
                    currentPositions
                )

                # Draw congestion zones on both frames
                self.congestionDetection.drawCongestionZones(
                    annotatedFrame, floorAnnotatedFrame, transformPoints
                )

                # Use the congestion detection class for future congestion prediction
                futureCongestion = self.congestionDetection.predictCongestionZones(
                    currentPositions, flow
                )

                # Draw future congestion zones
                self.congestionDetection.drawPredictedCongestion(
                    annotatedFrame, futureCongestion
                )

                # Update the dwell time analysis with the current positions
                self.dwellTimeAnalysis.updateZones(currentPositions, self.trackHistory)
                if self.showDwellTime:
                    # Draw dwell times on the floor plan
                    floorAnnotatedFrame = self.dwellTimeAnalysis.drawDwellTimes(
                        floorAnnotatedFrame, currentPositions, human_trackIDs
                    )
                    # Draw dwell times on the annotated frame
                    annotatedFrame = self.dwellTimeAnalysis.drawDwellTimes(
                        annotatedFrame, currentPositions, human_trackIDs
                    )

            else:
                print("No human detections or IDs available.")

        except AttributeError as e:
            print(f"An AttributeError occurred: {e}")
        except Exception as e:
            print(f"An unexpected error occurred: {e}")

        return annotatedFrame, floorAnnotatedFrame

    # Function to run the camera processor
    def run(self):
        while True:
            success, frame = self.cap.read()
            if not success:
                raise Exception(
                    "Failed to read video stream - cameraProcessor.py - run"
                )
            else:
                annotatedFrame, floorAnnotatedFrame = self.processFrame(frame)
                cv2.imshow("Annotated Frame", annotatedFrame)
                cv2.imshow("Floor Annotation", floorAnnotatedFrame)
                if cv2.waitKey(1) & 0xFF == ord("q"):
                    break
        self.release()

    # Function to get the raw frame from the video stream
    def getFrame(self):
        while True:
            success, frame = self.cap.read()
            if not success:
                raise Exception(
                    "Failed to read video stream - cameraProcessor.py - getFrame"
                )
            else:
                annotatedFrame, _ = self.processFrame(frame)
                ret, buffer = cv2.imencode(".jpg", annotatedFrame)
                frame = buffer.tobytes()
                yield (
                    b"--frame\r\n" b"Content-Type: image/jpeg\r\n\r\n" + frame + b"\r\n"
                )

    # Function to get the annotated frame with floor plan
    def getAnnotatedFrame(self):
        while True:
            success, frame = self.cap.read()
            if not success:
                raise Exception(
                    "Failed to read video stream - cameraProcessor.py - getAnnotatedFrame"
                )
            else:
                _, floorAnnotatedFrame = self.processFrame(frame)
                ret, buffer = cv2.imencode(".jpg", floorAnnotatedFrame)
                frame = buffer.tobytes()
                yield (
                    b"--frame\r\n" b"Content-Type: image/jpeg\r\n\r\n" + frame + b"\r\n"
                )

    def release(self):
        self.cap.release()
        cv2.destroyAllWindows()


if __name__ == "__main__":
    cameraProcessor = CameraProcessor()
    cameraProcessor.run()
