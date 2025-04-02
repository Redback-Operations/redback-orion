import cv2
import numpy as np
from ultralytics import YOLO
from collections import defaultdict
from utils import calculateHomography, transformPoints
#from database import Database
from floorReplica import FloorPlanAnnotator
from coordinateSelector import CoordinateSelector
import time as time_module
import os

class CameraProcessor:
    def __init__(self, source=0, is_video=False):
        """
        Initialize the camera processor
        
        Args:
            source (str/int): Camera index, video file path, or RTSP stream
            is_video (bool): Flag to indicate if source is a video file
        """
        # Initialize YOLO model for object detection
        self.model = YOLO("yolov8n.pt")
        
        # Set up video source
        self.source = source
        self.is_video = is_video
        
        # Open video capture
        if is_video and not os.path.exists(source):
            raise FileNotFoundError(f"Video file not found: {source}")
        
        self.cap = cv2.VideoCapture(source)
        
        # Initialize tracking and annotation components
        self.track_history = defaultdict(list)
        self.floor_annotator = FloorPlanAnnotator()
        
        # Coordinate selection and homography
        self.coordinator = CoordinateSelector(source, is_video)
        self.homography_matrix = self._calculate_homography()
        
        # Database for tracking
        # self.db = Database()
        self.current_frame_id = 0
    
    def _calculate_homography(self):
        """Calculate homography matrix with fallback to default points"""
        matrix = self.coordinator.get_homography_matrix()
        if matrix is None:
            print("Using default homography points as fallback")
            pts_src = np.array([[28, 1158], [2120, 1112], [1840, 488], [350, 518], [468, 1144]])
            pts_dst = np.array([[0, 990], [699, 988], [693, 658], [0, 661], [141, 988]])
            matrix = calculateHomography(pts_src, pts_dst)
        return matrix
    
    def process_frame(self, frame):
        """
        Process a single video frame
        
        Args:
            frame (numpy.ndarray): Input video frame
        
        Returns:
            tuple: Annotated frame and floor plan annotation
        """
        try:
            results = self.model.track(frame, persist=True, show=False, imgsz=1280, verbose=True)
            
            # Print detection information
            print(f"Total detections: {len(results[0].boxes)}")
            print(f"Human detections: {sum(results[0].boxes.cls.cpu().numpy() == 0)}")
            
            # Prepare annotation frames
            annotated_frame = frame.copy()
            floor_annotated_frame = self.floor_annotator.get_floor_plan()
            total_people = 0
            
            # Process detections
            if results[0].boxes is not None and hasattr(results[0].boxes, 'id'):
                boxes = results[0].boxes.xywh.cpu().numpy()
                track_ids = results[0].boxes.id.int().cpu().numpy()
                classes = results[0].boxes.cls.cpu().numpy()
                
                # Filter for human detections
                human_indices = classes == 0
                human_boxes = boxes[human_indices]
                human_track_ids = track_ids[human_indices]
                
                # Annotate trajectories and draw bounding boxes
                for box, track_id in zip(human_boxes, human_track_ids):
                    x, y, w, h = box
                    center = (int(x), int(y + h / 2))
                    
                    # Update track history
                    self.track_history[track_id].append(center)
                    
                    # Limit track history
                    if len(self.track_history[track_id]) > 50:
                        self.track_history[track_id].pop(0)
                    
                    # Draw bounding box and ID
                    cv2.rectangle(annotated_frame, 
                                  (int(x - w/2), int(y - h/2)), 
                                  (int(x + w/2), int(y + h/2)), 
                                  (0, 255, 0), 2)
                    cv2.putText(annotated_frame, 
                                f"ID: {int(track_id)}", 
                                (int(x - w/2), int(y - h/2) - 10), 
                                cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)
                    
                    # Annotate trajectory on floor plan
                    if len(self.track_history[track_id]) > 1:
                        points = np.array(self.track_history[track_id], dtype=np.int32)
                        
                        # Draw trajectory on original frame
                        if len(points) > 1:
                            cv2.polylines(annotated_frame, 
                                          [points], 
                                          isClosed=False, 
                                          color=(255, 0, 0), 
                                          thickness=2)
                        
                        # Transform points for floor plan
                        transformed_points = transformPoints(points, self.homography_matrix)
                        
                        # Annotate trajectory on floor plan
                        floor_annotated_frame = self.floor_annotator.annotate_trajectory(
                            transformed_points
                        )
                    
                    total_people += 1
            
            # Record people count
            self.current_frame_id += 1
            #self.db.insertRecord(total_people, self.current_frame_id)
            
            return annotated_frame, floor_annotated_frame
        
        except Exception as e:
            print(f"Error processing frame: {e}")
            return frame, self.floor_annotator.get_floor_plan()
    
    def run(self):
        """Run continuous video processing"""
        while True:
            success, frame = self.cap.read()
            
            if not success:
                # Reset video if it's a video file
                if self.is_video:
                    self.cap.set(cv2.CAP_PROP_POS_FRAMES, 0)
                    continue
                raise Exception("Failed to read video stream")
            
            # Process and display frames
            annotated_frame, floor_annotated_frame = self.process_frame(frame)
            cv2.imshow("Annotated Frame", annotated_frame)
            cv2.imshow("Floor Annotation", floor_annotated_frame)
            print("annoted frame and floor annotation done")
            # Exit on 'q' key
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break
        
        self.release()
    
    def get_frame(self):
        """Generator for streaming annotated frames"""
        while True:
            success, frame = self.cap.read()
            if not success:
                raise Exception("Failed to read video stream")
            
            annotated_frame, _ = self.process_frame(frame)
            ret, buffer = cv2.imencode('.jpg', annotated_frame)
            frame = buffer.tobytes()
            
            yield (b'--frame\r\n'
                   b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')
    
    def get_annotated_frame(self):
        """Generator for streaming floor plan annotations"""
        while True:
            success, frame = self.cap.read()
            if not success:
                raise Exception("Failed to read video stream")
            
            _, floor_annotated_frame = self.process_frame(frame)
            ret, buffer = cv2.imencode('.jpg', floor_annotated_frame)
            frame = buffer.tobytes()
            
            yield (b'--frame\r\n'
                   b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')
    
    def release(self):
        """Release video capture and close windows"""
        self.cap.release()
        cv2.destroyAllWindows()

# Example usage
if __name__ == "__main__":
    # Use default camera
    # processor = CameraProcessor()
    
    # Use specific video file
    processor = CameraProcessor(source="/Users/apple/Desktop/Deakin/T2_2024/SIT764_Capstone/Crowd_Monitor/market-square.mp4", is_video=True)
    processor.run()