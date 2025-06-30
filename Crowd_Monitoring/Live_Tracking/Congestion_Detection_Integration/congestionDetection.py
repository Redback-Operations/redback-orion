import cv2
import numpy as np
from sklearn.cluster import DBSCAN


class CongestionDetection:
    def __init__(self, homographyMatrix, debug=False):
        # Initialize the homography matrix for transforming points
        # and set 3 as the minimum people within proximity to define congestion
        # and 120 as the pixel distance to consider for congestion
        # define a list to store congestion zones
        self.homographyMatrix = homographyMatrix
        self.congestionThreshold = 3
        self.proximityThreshold = 120
        self.congestionZones = []
        self.debug = debug

    def identifyCongestionZones(self, position):
        # Function to identify congestion zones based on the track histories
        # Define a list to store congestion zones for the current frame
        # checking if the position is empty, return an empty list
        self.congestionZones = []

        if not position:
            return []

        minCongestionThreshold = self.congestionThreshold

        # Check if the number of positions exceeds the congestion threshold
        if len(position) >= minCongestionThreshold:
            # Convert the positions to a numpy array
            pointsArray = np.array(position, dtype=np.float32)

            try:
                # Use DBSCAN clustering to identify congestion zones
                # labels the points based on proximity
                # get the unique cluster IDs
                clustering = DBSCAN(
                    eps=self.proximityThreshold, min_samples=minCongestionThreshold
                ).fit(pointsArray)
                labels = clustering.labels_
                uniqueClusters = set(labels) - {-1}

                # Iterate through each unique cluster ID
                # and calculate the center and radius of the congestion zone
                for clusterID in uniqueClusters:
                    clusterPoints = pointsArray[labels == clusterID]
                    if len(clusterPoints) >= minCongestionThreshold:
                        centerX = int(np.mean(clusterPoints[:, 0]))
                        centerY = int(np.mean(clusterPoints[:, 1]))

                        # calculate the radius based on the cluster
                        maxDistance = 0
                        for point in clusterPoints:
                            distance = np.sqrt(
                                (point[0] - centerX) ** 2 + (point[1] - centerY) ** 2
                            )
                            maxDistance = max(maxDistance, distance)

                        # Set the radius to the maximum distance and ensure it's at least the proximity threshold
                        # get the count of points in the cluster
                        radius = max(int(maxDistance) + 20, self.proximityThreshold)
                        count = len(clusterPoints)

                        # add the congestion zone to the list
                        self.congestionZones.append(((centerX, centerY), radius, count))

                        if self.debug:
                            print(
                                f"Congestion Zone: center=({centerX}, {centerY}), Radius={radius}, Count={count}"
                            )

            except ImportError as e:
                # fallback if DBSCAN is not available
                self._fallbackCongestionDetection(position)
        else:
            # Fallback if not enough positions
            self._fallbackCongestionDetection(position)

        return self.congestionZones

    def _fallbackCongestionDetection(self, position):
        # Fallback congestion detection logic if DBSCAN is not available
        # This is a simple distance-based clustering

        minNearbyPoints = self.congestionThreshold - 1

        for i, position1 in enumerate(position):
            nearbyPointsCount = 0
            nearbyPositions = []

            for j, position2 in enumerate(position):
                if i != j:
                    distance = np.sqrt(
                        (position1[0] - position2[0]) ** 2
                        + (position1[1] - position2[1]) ** 2
                    )
                    if distance < self.proximityThreshold:
                        nearbyPointsCount += 1
                        nearbyPositions.append(position2)

            # Check if the number of nearby points exceeds the threshold
            # and if so, create a congestion zone by calculating the center of the group
            if nearbyPointsCount >= minNearbyPoints:
                allPositions = [position1] + nearbyPositions
                centerX = int(np.mean([p[0] for p in allPositions]))
                centerY = int(np.mean([p[1] for p in allPositions]))

                # caculate the radius
                maxDistance = 0
                for point in allPositions:
                    distance = np.sqrt(
                        (point[0] - centerX) ** 2 + (point[1] - centerY) ** 2
                    )
                    maxDistance = max(maxDistance, distance)

                radius = int(maxDistance) + 20

            # check if the zone is already in the list
            # to avoid duplicates
            newZone = True
            for zone in self.congestionZones:
                zonecenter = zone[0]
                distance = np.sqrt(
                    (centerX - zonecenter[0]) ** 2 + (centerY - zonecenter[1]) ** 2
                )
                if distance < radius:
                    newZone = False
                    break

            if newZone:
                count = nearbyPointsCount + 1
                self.congestionZones.append(((centerX, centerY), radius, count))
                if self.debug:
                    print(
                        f"Congestion Zone: center=({centerX}, {centerY}), Radius={radius}, Count={count}"
                    )

    def predictCongestionZones(self, currentPositions, flow, predictScale=5):
        # Function to predict congestion zones based on the current positions and flow
        if not currentPositions or flow is None:
            return []

        futurePositions = []
        for x, y in currentPositions:
            # Predict the future position using the flow
            if 0 <= x < flow.shape[1] and 0 <= y < flow.shape[0]:
                dy, dx = flow[y, x]
                predictedX = int(x + dx * predictScale)
                predictedY = int(y + dy * predictScale)
                futurePositions.append((predictedX, predictedY))

        # Use the same algorithm as identifyCongestionZones but on future positions
        futureCongestions = []

        if len(futurePositions) >= self.congestionThreshold:
            # Convert future positions to numpy array
            pointsArray = np.array(futurePositions, dtype=np.float32)

            try:
                clustering = DBSCAN(
                    eps=self.proximityThreshold, min_samples=self.congestionThreshold
                ).fit(pointsArray)
                labels = clustering.labels_
                uniqueClusters = set(labels) - {-1}

                for clusterID in uniqueClusters:
                    clusterPoints = pointsArray[labels == clusterID]
                    if len(clusterPoints) >= self.congestionThreshold:
                        centerX = int(np.mean(clusterPoints[:, 0]))
                        centerY = int(np.mean(clusterPoints[:, 1]))

                        # Calculate radius based on cluster
                        maxDistance = 0
                        for point in clusterPoints:
                            distance = np.sqrt(
                                (point[0] - centerX) ** 2 + (point[1] - centerY) ** 2
                            )
                            maxDistance = max(maxDistance, distance)

                        radius = max(int(maxDistance) + 20, self.proximityThreshold)
                        count = len(clusterPoints)

                        futureCongestions.append(((centerX, centerY), radius, count))
            except:
                # Fallback if DBSCAN fails
                self._fallbackFutureCongestion(futurePositions, futureCongestions)
        else:
            # Fallback if not enough future positions
            self._fallbackFutureCongestion(futurePositions, futureCongestions)

        return futureCongestions

    def _fallbackFutureCongestion(self, positions, congestionsList):
        # Fallback future congestion detection
        minNearbyPoints = self.congestionThreshold - 1
        processed = set()

        for i, pos1 in enumerate(positions):
            if i in processed:
                continue

            nearbyPointsCount = 0
            nearbyPositions = []

            for j, pos2 in enumerate(positions):
                if i != j:
                    distance = np.sqrt(
                        (pos1[0] - pos2[0]) ** 2 + (pos1[1] - pos2[1]) ** 2
                    )
                    if distance < self.proximityThreshold:
                        nearbyPointsCount += 1
                        nearbyPositions.append(pos2)
                        processed.add(j)

            if nearbyPointsCount >= minNearbyPoints:
                allPositions = [pos1] + nearbyPositions
                centerX = int(np.mean([p[0] for p in allPositions]))
                centerY = int(np.mean([p[1] for p in allPositions]))

                # Calculate radius
                maxDistance = 0
                for point in allPositions:
                    distance = np.sqrt(
                        (point[0] - centerX) ** 2 + (point[1] - centerY) ** 2
                    )
                    maxDistance = max(maxDistance, distance)

                radius = int(maxDistance) + 20
                count = nearbyPointsCount + 1

                congestionsList.append(((centerX, centerY), radius, count))

    def drawCongestionZones(
        self, annotatedFrame, floorFrame, transformePointsFuction=None
    ):
        # Function to draw the congestion zones on the annotated frame
        for zone in self.congestionZones:
            center, radius, count = zone

            # Draw the congestion zone and count on the annotated frame
            # Drawing red circle with transparency and text
            overlay = annotatedFrame.copy()
            cv2.circle(overlay, center, radius, (0, 0, 255), -1)
            cv2.addWeighted(overlay, 0.4, annotatedFrame, 0.6, 0, annotatedFrame)
            cv2.circle(annotatedFrame, center, radius, (0, 0, 255), 2)
            cv2.putText(
                annotatedFrame,
                f"CONGESTION ZONE: {count}",
                (center[0] - 80, center[1]),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.7,
                (255, 255, 255),
                2,
            )

            # Check if floorFrame and transformePointsFuction are provided
            # and draw the congestion zone on the floor plan by:
            # Transform the center point to the floor plan coordinates
            # scale the radius and draw the circle
            if floorFrame is not None and transformePointsFuction is not None:
                transformedcenter = transformePointsFuction(
                    np.array([center]), self.homographyMatrix
                )[0]
                transformedcenter = tuple(map(int, transformedcenter))

                floorRadius = int(radius * 0.7)

                # Apply similar visualization to floor plan
                overlay = floorFrame.copy()
                cv2.circle(overlay, transformedcenter, floorRadius, (0, 0, 255), -1)
                cv2.addWeighted(overlay, 0.4, floorFrame, 0.6, 0, floorFrame)
                cv2.circle(floorFrame, transformedcenter, floorRadius, (0, 0, 255), 2)
                cv2.putText(
                    floorFrame,
                    f"CONGESTION ZONE: {count}",
                    (transformedcenter[0] - 70, transformedcenter[1]),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    0.6,
                    (255, 255, 255),
                    2,
                )

    def drawPredictedCongestion(self, annotatedFrame, predictedCongestions):
        # Function to draw the predicted congestion zones on the annotated frame with a pale blue color

        for zone in predictedCongestions:
            center, radius, count = zone

            # Draw a pale blue circle with transparency
            overlay = annotatedFrame.copy()

            # Draw the congestion zone and count on the annotated frame
            # Drawing blue circle with transparency
            cv2.circle(overlay, center, radius, (255, 200, 0), -1)
            cv2.addWeighted(overlay, 0.3, annotatedFrame, 0.7, 0, annotatedFrame)
            cv2.circle(annotatedFrame, center, radius, (255, 200, 0), 2)
            cv2.putText(
                annotatedFrame,
                f"PREDICTED CONGESTION: {count}",
                (center[0] - 80, center[1]),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.7,
                (255, 200, 0),
                2,
            )
