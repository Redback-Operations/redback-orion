Key Features

1. Object Detection: Uses YOLO to detect people in each video frame.

2. Heatmap Generation: Maps detections to a grid and accumulates the density over time.

3. Visualisation:

* Displays a heatmap overlay on the video frames.
* Plots the final heatmap using Matplotlib.

Misc

1. Customisation: Adjust the confidence threshold or heatmap resolution to refine results.

2. Input Video: Replace stadium_crowd.mp4 with your video (surveillance) file showing the stadium crowd.

3. Performance: Processing large videos can be resource-intensive. Consider using a GPU-enabled OpenCV build for faster inference.

This setup provides a fundamental pipeline for crowd monitoring with heatmap visualisation. For real-time applications, integrate this script with a live camera/surveillance feed or streaming API.