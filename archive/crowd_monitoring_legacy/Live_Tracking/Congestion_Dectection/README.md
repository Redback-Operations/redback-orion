# Congestion Dection

## Introduction

The program focuses on extending the analysing features of the previous real-time crowd monitoring project. Farneback algorithm, homography transformation, and Density-Based Spatial Clustering of Applications with Noise (DBSCAN) for tracking the movement of the people to provide direction and congestion predictions.

Even though utilising the previous program, the project would solely use bulit-in camera for live tracking instead of the Real-Time Streaming Protocol. Furthermore, the data recording feature via MongoDB will be commented out, since it was not a part of the initial targets.

The cameraProccesing.py will be the main Python script used for testing.

## Folder Components

### cameraProcessing.py

The main controller used for:

1. Objectives tracking using YOLOv8
2. Ochestrateing other components
3. Displaying actual camera and 2D floor plan view

### opticalFlow.py

Utilising Farneback algorithm for:

1. Analysing the crowd movement between consecutive frames
2. Providing future position and trajectories predictions

### congestionDetectio.py

This class has the purpose of:

1. Detecting the area where the people standing close to each other
2. Predicting the potential jammed areas
3. Visualising the the zones on both camera view and 2D floor

### dwellTime.py

This class is majorly integrate into the 2D plan floor. Its mechanism includes:

1. Dividing the floor into differents zones
2. OpenCV is applied to verify whether the objects are still in the zones
3. Caluclating the the dwelling time
4. Visualising the zones and their statistics
