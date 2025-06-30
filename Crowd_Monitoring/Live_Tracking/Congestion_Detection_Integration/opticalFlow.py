import cv2
import numpy as np


class OpticalFlow:
    def __init__(self, predictionStep=10, predictionScale=5):
        # previousFrame and currentFrame to store the previous and current frames for optical flow calculation
        # predictionSteps and predictionScale to control the prediction steps and scale
        self.previousFrame = None
        self.currentFrame = None
        self.predictionSteps = predictionStep
        self.predictionScale = predictionScale

    def calculateFlow(self, frame):
        # Function to calculate the optical flow using Farneback method
        # Convert the frame to grayscale
        currentGray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        if self.previousFrame is None:
            self.previousFrame = currentGray
            return frame

        # Calculate the optical flow using Farneback method

        flow = cv2.calcOpticalFlowFarneback(
            self.previousFrame, currentGray, None, 0.5, 3, 15, 3, 5, 1.2, 0
        )
        self.previousFrame = currentGray
        return flow

    def predictPosition(self, trackHistories, flow):
        # Function to predict the next position of each trackID based on the optical flow
        # Initialize a dictionary to store the predicted positions
        predictedPositions = {}

        # Iterate through each trackID and its corresponding points
        # if the length of points is less than 2, skip the prediction
        for trackID, points in trackHistories.items():
            if len(points) < 2:
                continue

            # Get the last point of the track history
            # and use it to predict the next position
            lastPoint = points[-1]
            x, y = int(lastPoint[0]), int(lastPoint[1])

            # Check if the point is within the bounds of the flow array
            # get the flow vector at the last point
            # and predict the next position
            # then store the predicted position in the dictionary
            if 0 <= x < flow.shape[1] and 0 <= y < flow.shape[0]:
                dy, dx = flow[y, x]
                predictedX = x + int(dx * self.predictionScale)
                predictedY = y + int(dy * self.predictionScale)

                predictedPositions[trackID] = (predictedX, predictedY)

        return predictedPositions

    def predictTrajectory(self, trackID, points, predictedPosition):
        # Function to predict the trajectory of a trackID based on the predicted position
        # Check if the length of points is less than 2 and return an empty list
        if len(points) < 2:
            return []

        # Initialize the trajectory with the last point of the track history
        currentPosition = points[-1]
        trajectory = [currentPosition]

        # Predict the next position
        nextPosition = predictedPosition
        trajectory.append(nextPosition)

        # Iterate through the prediction steps
        # and calculate the next positions based on the flow
        for _ in range(self.predictionSteps - 1):
            if len(trajectory) >= 2:

                # Calculate the velocity vector based on the last two points
                # and update the next position
                dx = nextPosition[0] - currentPosition[0]
                dy = nextPosition[1] - currentPosition[1]
                nextPosition = (int(nextPosition[0] + dx), int(nextPosition[1] + dy))
                trajectory.append(nextPosition)

                # Update the current position to the last point in the trajectory
                currentPosition = trajectory[-2]

        return trajectory

