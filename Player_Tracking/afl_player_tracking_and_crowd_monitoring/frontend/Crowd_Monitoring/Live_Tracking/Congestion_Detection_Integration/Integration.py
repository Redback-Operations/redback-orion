import cv2
import numpy as np
import time
from collections import defaultdict


class Integration:
    def __init__(self, congestionDetection, dwellTimeAnalysis):
        # Initialize the integration analysis with necessary components
        # including congestion detection and dwell time analysis
        self.congestionDetection = congestionDetection
        self.dwellTimeAnalysis = dwellTimeAnalysis
        self.homographyMatrix = congestionDetection.homographyMatrix

        # initialise the list for high risk zones
        # and other necessary data structures
        self.highRiskZones = []
        self.zoneCongestionCorrelation = defaultdict(float)
        self.zoneHistoricalData = defaultdict(list)

        # Thresholds for triggering alerts
        self.highDwellThreshold = 5
        self.highCongestionThreshold = 3

        # Update timing settings
        self.lastUpdateTime = time.time()
        self.updateInterval = 5

    def update(self, currentPositions, trackIDs, flow=None):
        # Check if there are any current positions
        if not currentPositions:
            return self.highRiskZones

        # Identify congestion zones from current positions
        congestionZones = self.congestionDetection.identifyCongestionZones(
            currentPositions
        )

        # Update dwell time analysis
        self.dwellTimeAnalysis.updateZones(currentPositions, trackIDs)

        # Periodic full analysis
        currentTime = time.time()
        if currentTime - self.lastUpdateTime > self.updateInterval:
            self.integrationAnalysis(currentPositions, trackIDs, congestionZones, flow)
            self.lastUpdateTime = currentTime

            # if optical flow is provided, perform prediction analysis
            if flow is not None:
                self.floorPrediction(currentPositions, flow)

        # return the high risk zones
        return self.highRiskZones

    def integrationAnalysis(self, currentPositions, trackIDs, congestionZones, flow):
        # Reset high risk zones for this update
        self.highRiskZones = []

        # Get current dwell times for all zones
        dwellTimes = self.dwellTimeAnalysis.getCurrentDwellTimes()

        # Transform congestion centers to floor coordinates
        floorCongestionCenters = []
        for zone in congestionZones:
            centre, radius, count = zone
            if centre and radius:
                floorCentre = self.transformPointToFloor(centre)
                floorCongestionCenters.append((floorCentre, radius, count))

        # Analyze each zone defined in the dwell time analysis
        for zoneID, (zoneName, zonePoly, zoneColor) in enumerate(
            self.dwellTimeAnalysis.zones
        ):
            zoneStats = self.dwellTimeAnalysis.zoneStats[zoneID]

            # Calculate zone centroid
            zoneCentroid = (int(np.mean(zonePoly[:, 0])), int(np.mean(zonePoly[:, 1])))

            # Check if any congestion centers fall within this zone
            zoneHasCongestion = False
            congestionCount = 0
            for floorCentre, radius, count in floorCongestionCenters:
                # Check if congestion center is in or near the zone
                distance = np.sqrt(
                    (zoneCentroid[0] - floorCentre[0]) ** 2
                    + (zoneCentroid[1] - floorCentre[1]) ** 2
                )
                if self.isPointInPolygon(zonePoly, floorCentre) or distance < radius:
                    zoneHasCongestion = True
                    congestionCount = max(congestionCount, count)

            # Get zone statistics
            averageDwellTime = zoneStats["averageDwellTime"]
            currentCount = zoneStats["currentCount"]

            # Store historical data for this zone
            self.zoneHistoricalData[zoneID].append(
                {
                    "timestamp": time.time(),
                    "count": currentCount,
                    "averageDwellTime": averageDwellTime,
                    "hasCongestion": zoneHasCongestion,
                    "congestionCount": congestionCount,
                }
            )

            # Limit historical data length
            if len(self.zoneHistoricalData[zoneID]) > 100:
                self.zoneHistoricalData[zoneID].pop(0)

            # Determine if this is a high-risk zone based on both dwell time and congestion
            if (
                zoneHasCongestion
                and averageDwellTime > self.highDwellThreshold
                and congestionCount >= self.highCongestionThreshold
            ):

                # Calculate risk score based on dwell time and congestion count
                riskScore = (averageDwellTime / self.highDwellThreshold) * (
                    congestionCount / self.highCongestionThreshold
                )

                # Create high risk zone entry
                self.highRiskZones.append(
                    {
                        "zoneID": zoneID,
                        "zoneName": zoneName,
                        "centroid": zoneCentroid,
                        "averageDwellTime": averageDwellTime,
                        "congestionCount": congestionCount,
                        "riskScore": riskScore,
                        "predictedCongestion": False,  # Not predicted yet
                        "color": zoneColor,
                    }
                )

    def floorPrediction(self, currentPositions, flow):
        # Get predicted congestion zones
        futureCongestion = self.congestionDetection.predictCongestionZones(
            currentPositions, flow
        )

        # Process each predicted congestion zone
        for zone in futureCongestion:
            centre, radius, count = zone
            floorCentre = self.transformPointToFloor(centre)

            # Check which zones this predicted congestion might affect
            for zoneID, (zoneName, zonePoly, zoneColor) in enumerate(
                self.dwellTimeAnalysis.zones
            ):
                zoneStats = self.dwellTimeAnalysis.zoneStats[zoneID]

                # If dwell time is already high and predicted congestion is in this zone
                if zoneStats[
                    "averageDwellTime"
                ] > self.highDwellThreshold and self.isPointInPolygon(
                    zonePoly, floorCentre
                ):

                    # Check if zone is already in high risk zones
                    zone_already_added = False
                    for i, riskZone in enumerate(self.highRiskZones):
                        if riskZone["zoneID"] == zoneID:
                            # Increase risk score for existing zone
                            self.highRiskZones[i]["riskScore"] *= 1.5
                            self.highRiskZones[i]["predictedCongestion"] = True
                            zone_already_added = True
                            break

                    # Add new high risk zone if not already added
                    if not zone_already_added:
                        zoneCentroid = (
                            int(np.mean(zonePoly[:, 0])),
                            int(np.mean(zonePoly[:, 1])),
                        )
                        riskScore = (
                            zoneStats["averageDwellTime"] / self.highDwellThreshold
                        ) * (count / self.highCongestionThreshold)
                        self.highRiskZones.append(
                            {
                                "zoneID": zoneID,
                                "zoneName": zoneName,
                                "centroid": zoneCentroid,
                                "averageDwellTime": zoneStats["averageDwellTime"],
                                "congestionCount": count,
                                "riskScore": riskScore,
                                "predictedCongestion": True,
                                "color": zoneColor,
                            }
                        )

    def transformPointToFloor(self, cameraPoint):
        # convert camera point to floor coordinates using homography
        pointArray = np.array([cameraPoint], dtype=np.float32).reshape(-1, 1, 2)
        transformedPoint = cv2.perspectiveTransform(pointArray, self.homographyMatrix)[
            0
        ][0]
        return (int(transformedPoint[0]), int(transformedPoint[1]))

    def transformPolygonToCamera(self, floorPolygon):
        # calculate the inverse of the homography matrix
        # and transform the polygon to camera coordinates
        try:
            inverseHomography = np.linalg.inv(self.homographyMatrix)
            floorPolygonReshaped = floorPolygon.reshape(-1, 1, 2).astype(np.float32)
            cameraPolygon = cv2.perspectiveTransform(
                floorPolygonReshaped, inverseHomography
            )
            return cameraPolygon.reshape(-1, 2).astype(int)

        except np.linalg.LinAlgError:
            print("Error: Homography matrix is singular or not invertible.")
            return None

    def isPointInPolygon(self, zonePolygon, point):
        return cv2.pointPolygonTest(zonePolygon, tuple(map(int, point)), False) >= 0

    def drawAnalytics(self, cameraFrame, floorFrame):
        # First draw dwell time information on the floor plan
        self.dwellTimeAnalysis.drawDwellTimes(floorFrame, None, None, True)

        # Draw risk zones on both camera and floor view
        for riskZone in self.highRiskZones:
            zoneID = riskZone["zoneID"]
            zoneName = riskZone["zoneName"]
            centroid = riskZone["centroid"]
            riskScore = riskZone["riskScore"]
            isPredicted = riskZone.get("predictedCongestion", False)

            # Calculate color based on risk score
            # Draw risk indicator on floor plan
            # Circle with risk color
            riskIntensity = min(riskScore / 5, 1)
            riskColor = (
                0,
                int(255 * (1 - riskIntensity)),
                int(255 * riskIntensity),
            )
            cv2.circle(floorFrame, centroid, 25, riskColor, -1)

            # Label based on prediction status
            label = "High Risk Zone"
            if isPredicted:
                label = "Predicted " + label

            # Draw labels on floor plan
            cv2.putText(
                floorFrame,
                label,
                (centroid[0] - 80, centroid[1] - 30),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.6,
                riskColor,
                2,
            )
            cv2.putText(
                floorFrame,
                f"Risk Score: {riskScore:.1f}",
                (centroid[0] - 70, centroid[1] + 30),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.5,
                riskColor,
                2,
            )

            # Add additional statistics
            cv2.putText(
                floorFrame,
                f"Dwell: {riskZone['averageDwellTime']:.1f}s",
                (centroid[0] - 70, centroid[1] + 50),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.5,
                riskColor,
                2,
            )
            cv2.putText(
                floorFrame,
                f"Count: {riskZone['congestionCount']}",
                (centroid[0] - 70, centroid[1] + 70),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.5,
                riskColor,
                2,
            )

            # Transform zone polygon to camera view
            zonePoly = self.dwellTimeAnalysis.zones[zoneID][1]
            cameraPoly = self.transformPolygonToCamera(zonePoly)

            # Draw on camera view if polygon transformation was successful
            if cameraPoly is not None:
                # Create semi-transparent overlay
                overlay = cameraFrame.copy()
                cv2.fillPoly(overlay, [cameraPoly], riskColor)
                cv2.addWeighted(overlay, 0.3, cameraFrame, 0.7, 0, cameraFrame)

                # Draw polygon outline
                cv2.polylines(cameraFrame, [cameraPoly], True, riskColor, 2)

                # Calculate camera view centroid for labels
                cameraCentroid = np.mean(cameraPoly, axis=0).astype(int)

                # Draw labels on camera view
                cv2.putText(
                    cameraFrame,
                    label,
                    (cameraCentroid[0] - 80, cameraCentroid[1] - 15),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    0.6,
                    riskColor,
                    2,
                )

                # Draw risk score on camera
                cv2.putText(
                    cameraFrame,
                    f"Risk: {riskScore:.1f}",
                    (cameraCentroid[0] - 50, cameraCentroid[1] + 15),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    0.5,
                    riskColor,
                    2,
                )

        return cameraFrame, floorFrame
