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
from Integration import Integration


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
        # self.lastRecorded = 0

        # initialise the variables for counting the current frame ID
        # initialise the congestion detection module using the homography matrix
        # initialise the optical flow amd the dwell time analysis module
        # Initialize the integration module that combines congestion and dwell time analysis
        self.congestionDetection = CongestionDetection(
            self.homographyMatrix, debug=True
        )
        self.opticalFlow = OpticalFlow(predictionStep=5, predictionScale=3)
        self.dwellTimeAnalysis = DwellTimeAnalysis(self.homographyMatrix)
        self.integration = Integration(self.congestionDetection, self.dwellTimeAnalysis)

        # Visualization settings
        self.lastFlowVisualizationTime = 0
        self.flowVisualizationInterval = 5  # Show every 5 seconds
        self.flowVisualizationDuration = 3  # Show for 3 seconds
        self.showFlowVisualization = False

        # Analysis display flags
        self.showDwellTime = True
        self.showIntegration = True

        # Default analysis mode
        self.analysisMode = (
            "integration"  # Options: "basic", "congestion", "dwell", "integration"
        )

    # Function to calculate the homography matrix
    def calculateHomography(self):
        ptsSRC = np.array(
            [[28, 1158], [2120, 1112], [1840, 488], [350, 518], [468, 1144]]
        )
        ptsDST = np.array([[0, 990], [699, 988], [693, 658], [0, 661], [141, 988]])
        return calculateHomography(ptsSRC, ptsDST)

    def processFrame(self, frame):
        # Calculate optical flow for this frame
        # and initialise the current position list to store the current positions of detected people
        # and track IDs to store the IDs of detected people
        flow = self.opticalFlow.calculateFlow(frame)
        currentPositions = []
        trackIDs = []

        # Check if it's time to update the flow visualization based on the interval
        currentTime = time_module.time()

        # Start visualization if interval has passed
        if (
            currentTime - self.lastFlowVisualizationTime
            >= self.flowVisualizationInterval
        ):
            self.showFlowVisualization = True
            self.lastFlowVisualizationTime = currentTime

        # Create copies of the frame for annotations
        # and initialise the total people count
        annotatedFrame = frame.copy()
        floorAnnotatedFrame = self.floorImage.copy()
        totalPeople = 0

        try:
            results = self.model.track(
                frame, persist=True, show=False, imgsz=1280, verbose=False
            )

            # # Get predicted positions based on optical flow
            # predictedPositions = {}
            # if flow is not None and self.showFlowVisualization:
            #     predictedPositions = self.opticalFlow.predictPosition(
            #         self.trackHistory, flow
            #     )

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

                # Process each tracked person
                for idx, trackID in enumerate(human_trackIDs):
                    # Get box dimensions
                    x, y, w, h = human_boxes[idx]
                    # Define center point (feet position)
                    center = (int(x), int(y + h / 2))

                    # Add to current positions and tracking history
                    currentPositions.append(center)
                    self.trackHistory[trackID].append(center)

                    # Limit history length
                    if len(self.trackHistory[trackID]) > 50:
                        self.trackHistory[trackID].pop(0)

                    # Draw history trails
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

                    # # Show predicted trajectories when flow visualization is active
                    # if self.showFlowVisualization and trackID in predictedPositions:
                    #     # Get predicted position
                    #     pred_x, pred_y = predictedPositions[trackID]
                    #     cv2.circle(
                    #         annotatedFrame, (pred_x, pred_y), 5, (0, 255, 255), -1
                    #     )  # Yellow dot

                    #     # Calculate and draw trajectory
                    #     trajectory = self.opticalFlow.predictTrajectory(
                    #         trackID, history, predictedPositions[trackID]
                    #     )

                    #     if len(trajectory) >= 2:
                    #         # Draw predicted path on camera view
                    #         points = np.array(trajectory, dtype=np.int32)
                    #         cv2.polylines(
                    #             annotatedFrame,
                    #             [points],
                    #             isClosed=False,
                    #             color=(0, 255, 255),
                    #             thickness=2,
                    #         )

                    #         # Add direction arrow
                    #         last_point = trajectory[-2]
                    #         end_point = trajectory[-1]
                    #         cv2.arrowedLine(
                    #             annotatedFrame,
                    #             (int(last_point[0]), int(last_point[1])),
                    #             (int(end_point[0]), int(end_point[1])),
                    #             (0, 255, 255),
                    #             3,
                    #             tipLength=0.5,
                    #         )

                    #         # Draw on floor plan too
                    #         floorTrajectory = transformPoints(
                    #             np.array(trajectory), self.homographyMatrix
                    #         )
                    #         floorTrajectory = floorTrajectory.astype(np.int32)
                    #         cv2.polylines(
                    #             floorAnnotatedFrame,
                    #             [floorTrajectory],
                    #             isClosed=False,
                    #             color=(0, 255, 255),
                    #             thickness=2,
                    #         )

                    #         # Add arrow on floor plan
                    #         if len(floorTrajectory) >= 2:
                    #             floor_last = floorTrajectory[-2]
                    #             floor_end = floorTrajectory[-1]
                    #             cv2.arrowedLine(
                    #                 floorAnnotatedFrame,
                    #                 (int(floor_last[0]), int(floor_last[1])),
                    #                 (int(floor_end[0]), int(floor_end[1])),
                    #                 (0, 255, 255),
                    #                 3,
                    #                 tipLength=0.5,
                    #             )

                    totalPeople += 1

                # Process different analysis modes
                if self.analysisMode == "basic" or self.analysisMode == "congestion":
                    # Run congestion detection
                    self.congestionDetection.drawCongestionZones(
                        annotatedFrame, floorAnnotatedFrame, transformPoints
                    )

                    # Predict future congestion
                    futureCongestion = self.congestionDetection.predictCongestionZones(
                        currentPositions, flow
                    )

                    # Draw predicted congestion
                    self.congestionDetection.drawPredictedCongestion(
                        annotatedFrame, futureCongestion
                    )

                if self.analysisMode == "basic" or self.analysisMode == "dwell":
                    # Update and visualize dwell time analysis
                    self.dwellTimeAnalysis.updateZones(currentPositions, human_trackIDs)

                    # Draw dwell time zones on both camera and floor frame
                    if self.showDwellTime:
                        floorAnnotatedFrame = self.dwellTimeAnalysis.drawDwellTimes(
                            floorAnnotatedFrame, currentPositions, human_trackIDs, True
                        )
                        annotatedFrame = self.dwellTimeAnalysis.drawDwellTimes(
                            annotatedFrame, currentPositions, human_trackIDs, False
                        )

                if self.analysisMode == "integration":
                    # Run the integrated analysis which combines congestion and dwell time
                    highRiskZones = self.integration.update(
                        currentPositions, human_trackIDs, flow
                    )

                    # Display integration visualization
                    if self.showIntegration:
                        # Draw analytics on both camera and floor views
                        annotatedFrame, floorAnnotatedFrame = (
                            self.integration.drawAnalytics(
                                annotatedFrame, floorAnnotatedFrame
                            )
                        )

            else:
                cv2.putText(
                    annotatedFrame,
                    "No human detections available",
                    (50, 50),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    1,
                    (0, 0, 255),
                    2,
                )

        except Exception as e:
            cv2.putText(
                annotatedFrame,
                f"Error: {str(e)}",
                (50, 50),
                cv2.FONT_HERSHEY_SIMPLEX,
                1,
                (0, 0, 255),
                2,
            )

        # Add info overlay
        self.addInfoOverlay(annotatedFrame, floorAnnotatedFrame, totalPeople)

        return annotatedFrame, floorAnnotatedFrame

    def addInfoOverlay(self, cameraFrame, floorFrame, totalPeople):
        # Add mode indicator to the camera frame
        cv2.putText(
            cameraFrame,
            f"Mode: {self.analysisMode.capitalize()}",
            (20, 30),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.7,
            (255, 255, 255),
            2,
        )

        # Display total people count
        cv2.putText(
            cameraFrame,
            f"People: {totalPeople}",
            (20, 60),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.7,
            (255, 255, 255),
            2,
        )

        # Add keyboard controls info
        cv2.putText(
            cameraFrame,
            "Press 'q' to quit, 'm' to change mode",
            (20, cameraFrame.shape[0] - 20),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.6,
            (255, 255, 255),
            1,
        )

    def togglingMode(self):
        modes = ["basic", "congestion", "dwell", "integration"]
        currentIndex = modes.index(self.analysisMode)
        nextIndex = (currentIndex + 1) % len(modes)
        self.analysisMode = modes[nextIndex]
        print(f"Analysis mode changed to: {self.analysisMode}")
        return self.analysisMode

    def run(self):
        while True:
            success, frame = self.cap.read()
            if not success:
                print("Failed to read video stream. Retrying...")
                continue

            annotatedFrame, floorAnnotatedFrame = self.processFrame(frame)

            # Display the frames
            cv2.imshow("Camera View", annotatedFrame)
            cv2.imshow("Floor Plan View", floorAnnotatedFrame)

            # Handle key presses
            key = cv2.waitKey(1) & 0xFF
            if key == ord("q"):
                break
            elif key == ord("m"):
                self.togglingMode()

        self.release()

    def getFrame(self):

        while True:
            success, frame = self.cap.read()
            if not success:
                print("Failed to read video stream in getFrame(). Retrying...")
                continue

            annotatedFrame, _ = self.processFrame(frame)
            ret, buffer = cv2.imencode(".jpg", annotatedFrame)
            frame = buffer.tobytes()
            yield (b"--frame\r\n" b"Content-Type: image/jpeg\r\n\r\n" + frame + b"\r\n")

    def getAnnotatedFrame(self):

        while True:
            success, frame = self.cap.read()
            if not success:
                print("Failed to read video stream in getAnnotatedFrame(). Retrying...")
                continue

            _, floorAnnotatedFrame = self.processFrame(frame)
            ret, buffer = cv2.imencode(".jpg", floorAnnotatedFrame)
            frame = buffer.tobytes()
            yield (b"--frame\r\n" b"Content-Type: image/jpeg\r\n\r\n" + frame + b"\r\n")

    def release(self):
        self.cap.release()
        cv2.destroyAllWindows()


if __name__ == "__main__":
    cameraProcessor = CameraProcessor()
    cameraProcessor.run()
