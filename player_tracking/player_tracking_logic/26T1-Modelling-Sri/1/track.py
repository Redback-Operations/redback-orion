from ultralytics import YOLO


class PlayerTracker: # A class to handle tracking of players in video frames using a YOLO model
    def __init__(self, model_path, conf=0.3):
        self.model = YOLO(model_path) # Load the YOLO model from the specified path, and set the confidence threshold for tracking to 0.3 by default
        self.conf = conf

    def track(self, frame): # Track objects in the given video frame using the loaded YOLO model, and return the tracking results
        results = self.model.track(
            frame,
            conf=self.conf,
            tracker="bytetrack.yaml",
            persist=True,
            verbose=False
        )
        return results[0]