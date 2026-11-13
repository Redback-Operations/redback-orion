import cv2
import numpy as np
import time
from collections import defaultdict


class DwellTimeAnalysis:
    def __init__(self, homographyMatrix, floorWidth=700, floorHeight=1000):
        self.homographyMatrix = homographyMatrix
        self.floorWidth = floorWidth
        self.floorHeight = floorHeight
        self.zones = []  # List of zones [(zoneName, polygon, color)]
        self.personZoneData = defaultdict(dict)
        self.zoneStats = defaultdict(
            lambda: {
                "currentCount": 0,
                "totalVisits": 0,
                "averageDwellTime": 0,
                "maxDwellTime": 0,
            }
        )
        self.defineDefaultZones()
        self.lastUpdateTime = time.time()
        self.updateInterval = 1.0  # Update stats once per second

    def defineDefaultZones(self):

        # Calculate the height of each zone (divide floor height by 3)
        zoneHeight = self.floorHeight // 3

        # Define the three horizontal zones with distinct colors
        self.zones = [
            (
                "Emprise du Lion",
                np.array(
                    [
                        [0, 0],  # Top-left
                        [self.floorWidth, 0],  # Top-right
                        [self.floorWidth, zoneHeight],  # Bottom-right
                        [0, zoneHeight],  # Bottom-left
                    ]
                ),
                (204, 255, 229),
            ),
            (
                "Hinterlands",
                np.array(
                    [
                        [0, zoneHeight],  # Top-left
                        [self.floorWidth, zoneHeight],  # Top-right
                        [self.floorWidth, 2 * zoneHeight],  # Bottom-right
                        [0, 2 * zoneHeight],  # Bottom-left
                    ]
                ),
                (255, 255, 153),
            ),
            (
                "Chateau d'Onterre",
                np.array(
                    [
                        [0, 2 * zoneHeight],  # Top-left
                        [self.floorWidth, 2 * zoneHeight],  # Top-right
                        [self.floorWidth, self.floorHeight],  # Bottom-right
                        [0, self.floorHeight],  # Bottom-left
                    ]
                ),
                (102, 204, 0),
            ),
        ]

    def isPointInZone(self, point, zonePolygon):
        # Make sure point is a single x,y tuple, not an array
        if isinstance(point, np.ndarray) and point.ndim > 1:
            # If it's an array, return array of results
            return np.array(
                [
                    cv2.pointPolygonTest(zonePolygon, (int(x), int(y)), False) >= 0
                    for x, y in point
                ]
            )
        else:
            # For a single point
            return cv2.pointPolygonTest(zonePolygon, tuple(map(int, point)), False) >= 0

    def updateZones(self, currentPositions, trackIDs):

        currentTime = time.time()

        # Transform camera positions to floor plan coordinates
        if currentPositions:
            floorPositions = self.transformPointsToFloor(np.array(currentPositions))
        else:
            floorPositions = []

        # Update person zone data
        for idx, trackID in enumerate(trackIDs):
            if idx >= len(floorPositions):
                continue

            personPos = tuple(map(int, floorPositions[idx]))

            # Check each zone for this person
            for zoneID, (zoneName, zonePoly, _) in enumerate(self.zones):
                # If we haven't seen this person in this zone before, initialize their data
                if zoneID not in self.personZoneData[trackID]:
                    self.personZoneData[trackID][zoneID] = {
                        "enterTime": None,
                        "exitTime": None,
                        "inZone": False,
                        "totalDwellTime": 0,
                    }

                isInZone = self.isPointInZone(personPos, zonePoly)
                zoneData = self.personZoneData[trackID][zoneID]

                # Person just entered the zone
                if isInZone and not zoneData["inZone"]:
                    zoneData["enterTime"] = currentTime
                    zoneData["inZone"] = True
                    self.zoneStats[zoneID]["currentCount"] += 1
                    self.zoneStats[zoneID]["totalVisits"] += 1

                # Person just exited the zone
                elif not isInZone and zoneData["inZone"]:
                    zoneData["exitTime"] = currentTime
                    zoneData["inZone"] = False
                    self.zoneStats[zoneID]["currentCount"] -= 1

                    # Calculate dwell time for this visit
                    if zoneData["enterTime"] is not None:
                        dwellTime = zoneData["exitTime"] - zoneData["enterTime"]
                        zoneData["totalDwellTime"] += dwellTime

                        # Update zone statistics
                        self.zoneStats[zoneID]["maxDwellTime"] = max(
                            self.zoneStats[zoneID]["maxDwellTime"], dwellTime
                        )

        # Update average dwell times periodically
        if currentTime - self.lastUpdateTime >= self.updateInterval:
            self.updateZoneStats()
            self.lastUpdateTime = currentTime

    def updateZoneStats(self):

        for zoneID in range(len(self.zones)):
            totalDwellTime = 0
            visitCount = 0

            # Calculate total dwell time across all people who have visited this zone
            for trackID, zones in self.personZoneData.items():
                if zoneID in zones:
                    zoneData = zones[zoneID]

                    # Add completed visit times
                    totalDwellTime += zoneData["totalDwellTime"]

                    # For people currently in the zone, add their current dwell time
                    if zoneData["inZone"] and zoneData["enterTime"] is not None:
                        currentDwell = time.time() - zoneData["enterTime"]
                        totalDwellTime += currentDwell

                    # Count this as a visit if they've entered the zone
                    if zoneData["enterTime"] is not None:
                        visitCount += 1

            # Update average dwell time
            if visitCount > 0:
                self.zoneStats[zoneID]["averageDwellTime"] = (
                    totalDwellTime / visitCount
                )

    def transformPointsToFloor(self, cameraPoints):

        if len(cameraPoints) == 0:
            return []

        # Reshape points for transformation
        points = np.array(cameraPoints, dtype=np.float32)
        if points.ndim == 1:
            points = points.reshape(1, -1, 2)
        elif points.ndim == 2:
            points = points.reshape(-1, 1, 2)

        # Apply homography transformation
        transformedPoints = cv2.perspectiveTransform(points, self.homographyMatrix)

        # Reshape back to original format
        if transformedPoints.shape[0] == 1:
            transformedPoints = transformedPoints.reshape(-1, 2)
        else:
            transformedPoints = transformedPoints.reshape(-1, 2)

        return transformedPoints

    def getCurrentDwellTimes(self, currentTime=None):

        if currentTime is None:
            currentTime = time.time()

        dwellTimes = defaultdict(dict)

        for trackID, zones in self.personZoneData.items():
            for zoneID, zoneData in zones.items():
                if zoneData["inZone"] and zoneData["enterTime"] is not None:
                    dwellTimes[trackID][zoneID] = currentTime - zoneData["enterTime"]

        return dwellTimes

    def drawZones(self, floorPlanImage):

        for zoneName, zonePoly, color in self.zones:
            # Create a copy of the image for overlay
            overlay = floorPlanImage.copy()

            # Fill the zone polygon with semi-transparent color
            alpha = 0.3  # Transparency factor
            cv2.fillPoly(overlay, [zonePoly], color)

            # Apply the overlay with transparency
            cv2.addWeighted(
                overlay, alpha, floorPlanImage, 1 - alpha, 0, floorPlanImage
            )

            # Draw the zone polygon border
            cv2.polylines(floorPlanImage, [zonePoly], True, color, 2)

            # Calculate zone centroid for text placement
            centroidX = int(np.mean(zonePoly[:, 0]))
            centroidY = int(np.mean(zonePoly[:, 1]))

            # Draw zone name
            cv2.putText(
                floorPlanImage,
                zoneName,
                (centroidX - 40, centroidY),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.5,
                color,
                2,
            )

        return floorPlanImage

    def drawDwellTimes(
        self, image, currentPositions=None, trackIDs=None, isFloorPlan=True
    ):
        # If this is floor plan, draw the zones
        if isFloorPlan:
            image = self.drawZones(image)

        # Draw statistics board in the top-right corner
        boardWidth = 300
        boardHeight = len(self.zones) * 30 + 120  # Height based on number of zones
        boardX = image.shape[1] - boardWidth - 10  # 10px padding from right edge
        boardY = 10  # 10px padding from top

        # Create semi-transparent board background
        cv2.rectangle(
            image,
            (boardX, boardY),
            (boardX + boardWidth, boardY + boardHeight),
            (50, 50, 50),
            -1,
        )  # Dark gray background
        cv2.rectangle(
            image,
            (boardX, boardY),
            (boardX + boardWidth, boardY + boardHeight),
            (200, 200, 200),
            2,
        )  # Light gray border

        # Add title to stats board
        cv2.putText(
            image,
            "Zone Statistics",
            (boardX + 10, boardY + 25),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.7,
            (255, 255, 255),
            2,
        )

        # Draw zone statistics in the board
        statsY = boardY + 55  # Start below title
        for zoneID, (zoneName, _, color) in enumerate(self.zones):
            stats = self.zoneStats[zoneID]

            # Draw color swatch for this zone
            cv2.rectangle(
                image, (boardX + 10, statsY - 15), (boardX + 30, statsY), color, -1
            )

            # Zone name
            cv2.putText(
                image,
                f"{zoneName}",
                (boardX + 40, statsY),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.5,
                (255, 255, 255),
                1,
            )

            # Current count, average dwell time and max dwell time
            cv2.putText(
                image,
                f"Count: {stats['currentCount']} | Avg: {stats['averageDwellTime']:.1f}s | Max: {stats['maxDwellTime']:.1f}s",
                (boardX + 40, statsY + 20),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.5,
                (255, 255, 255),
                1,
            )

            statsY += 55  # Move to next zone stats position

        # If we have current positions, draw them with dwell times
        if currentPositions and trackIDs:
            # For floor plan, transform camera points to floor coordinates
            if isFloorPlan:
                positionsToUse = self.transformPointsToFloor(
                    np.array(currentPositions)
                )
            else:
                # For camera view, use original camera coordinates
                positionsToUse = np.array(currentPositions)

            currentDwellTimes = self.getCurrentDwellTimes()

            for idx, trackID in enumerate(trackIDs):

                if idx >= len(positionsToUse):
                    continue

                personPos = tuple(map(int, positionsToUse[idx]))

                # Check if this person is in any zone and display their dwell time
                for zoneID, (zoneName, zonePoly, color) in enumerate(self.zones):
                    if (
                        trackID in currentDwellTimes
                        and zoneID in currentDwellTimes[trackID]
                    ):
                        dwellTime = currentDwellTimes[trackID][zoneID]

                        # Draw dwell time near the person's position
                        cv2.putText(
                            image,
                            f"{int(dwellTime)}s",
                            (personPos[0] + 10, personPos[1]),
                            cv2.FONT_HERSHEY_SIMPLEX,
                            0.4,
                            color,
                            1,
                        )

                        # Draw circle around person colored by dwell time (redder = longer)
                        maxDwell = 60  # Consider 60 seconds as maximum intensity
                        intensity = min(dwellTime / maxDwell, 1.0)
                        dwellColour = (
                            0,
                            int(255 * (1 - intensity)),
                            int(255 * intensity),
                        )
                        cv2.circle(image, personPos, 10, dwellColour, -1)

        return image
