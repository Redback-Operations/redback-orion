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
import threading
import queue
from datetime import datetime
import platform

class CameraProcessor:
    def __init__(self, source=0, is_video=False, queue_size=20, process_every_n_frames=1):
        """
        Initialize the camera processor with multi-threading support
        
        Args:
            source (str/int): Camera index, video file path, or RTSP stream
            is_video (bool): Flag to indicate if source is a video file
            queue_size (int): Maximum size of frame and results queues
            process_every_n_frames (int): Process every Nth frame (skip frames in between)
        """
        # Initialize YOLO model for object detection (use smaller model or lower image size for performance)
        self.model = YOLO("yolov8n.pt")  # Consider 'yolov8n' or even 'yolov8s' for better performance
        
        # Set up video source
        self.source = source
        self.is_video = is_video
        
        # Process control - only process every Nth frame
        self.process_every_n_frames = process_every_n_frames
        self.frame_counter = 0
        
        # Open video capture
        if is_video and not os.path.exists(source):
            raise FileNotFoundError(f"Video file not found: {source}")
        
        self.cap = cv2.VideoCapture(source)
        
        # Set lower resolution for capture if possible
        if self.is_video:  # Only for video files, not live cameras which might have fixed resolution
            width = self.cap.get(cv2.CAP_PROP_FRAME_WIDTH)
            height = self.cap.get(cv2.CAP_PROP_FRAME_HEIGHT)
            if width > 1280:  # If video is high resolution, scale it down
                new_width = 1280
                new_height = int(height * (new_width / width))
                self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, new_width)
                self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, new_height)
                print(f"Scaled video resolution to {new_width}x{new_height}")
        
        # Determine floor plan image path
        current_dir = os.path.dirname(__file__)
        floor_plan_path = os.path.join(current_dir, "/Users/apple/Desktop/Deakin/T2_2024/SIT764_Capstone/Crowd_Monitor/Stork Fountain.jpg")
        
        # Initialize tracking and annotation components
        self.track_history = defaultdict(list)
        self.floor_annotator = FloorPlanAnnotator(
            background_image=floor_plan_path,
            show_grid=True
        )
        
        # Coordinate selection and homography
        self.coordinator = CoordinateSelector(source, is_video)
        self.homography_matrix = self._calculate_homography()
        
        # Database for tracking
        # self.db = Database()
        self.current_frame_id = 0
        
        # Threading and queue setup
        self.frame_queue = queue.Queue(maxsize=queue_size)
        self.results_queue = queue.Queue(maxsize=queue_size)
        
        # Threading control
        self.running = False
        self.threads = []
        
        # FPS calculation
        self.fps = 0
        self.frame_count = 0
        self.start_time = 0
        
        # Frames for display - used to pass frames between threads safely
        self.display_frame = None
        self.display_floor_plan = None
        self.display_lock = threading.Lock()
        
        # Detect operating system for platform-specific handling
        self.is_macos = platform.system() == 'Darwin'
        print(f"Running on: {platform.system()}")
    
    def _calculate_homography(self):
        """Calculate homography matrix with fallback to default points"""
        matrix = self.coordinator.get_homography_matrix()
        if matrix is None:
            print("Using default homography points as fallback")
            pts_src = np.array([[28, 1158], [2120, 1112], [1840, 488], [350, 518], [468, 1144]])
            pts_dst = np.array([[0, 990], [699, 988], [693, 658], [0, 661], [141, 988]])
            matrix = calculateHomography(pts_src, pts_dst)
        return matrix
    
    def capture_thread(self):
        """Thread function for capturing frames"""
        print("Capture thread started")
        self.frame_count = 0
        self.start_time = time_module.time()
        frame_skip_counter = 0
        
        while self.running:
            success, frame = self.cap.read()
            if not success:
                if self.is_video:
                    self.cap.set(cv2.CAP_PROP_POS_FRAMES, 0)
                    continue
                print("Failed to read video stream")
                self.running = False
                break
            
            frame_skip_counter += 1
            
            # Only process every Nth frame to reduce computational load
            if frame_skip_counter >= self.process_every_n_frames:
                frame_skip_counter = 0
                
                if not self.frame_queue.full():
                    # Optionally resize the frame to reduce processing load
                    # frame = cv2.resize(frame, (640, 480))  # Uncomment if needed
                    
                    self.frame_queue.put(frame)
                    self.frame_count += 1
                    
                    # Calculate FPS every 30 frames
                    if self.frame_count % 30 == 0:
                        end_time = time_module.time()
                        self.fps = 30 / (end_time - self.start_time)
                        self.start_time = end_time
                else:
                    # If queue is full, skip this frame
                    time_module.sleep(0.01)
            # For skipped frames, we don't put them in the queue
    
    def processing_thread(self):
        """Thread function for processing frames"""
        print("Processing thread started")
        
        while self.running:
            if not self.frame_queue.empty():
                frame = self.frame_queue.get()
                try:
                    # Process frame
                    annotated_frame, floor_annotated_frame = self.process_frame(frame)
                    
                    # Add timestamp
                    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                    cv2.putText(annotated_frame, f"FPS: {self.fps:.2f}", (10, 30), 
                                cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
                    cv2.putText(annotated_frame, timestamp, (10, 60), 
                                cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
                    
                    # Update frames for display thread
                    with self.display_lock:
                        self.display_frame = annotated_frame
                        self.display_floor_plan = floor_annotated_frame
                except Exception as e:
                    print(f"Error processing frame: {e}")
            else:
                # If no frames to process, wait a bit
                time_module.sleep(0.01)
    
    def main_thread_display(self):
        """Function to display frames from the main thread (macOS compatible)"""
        if not self.running:
            return
        
        with self.display_lock:
            if self.display_frame is not None:
                cv2.imshow("Annotated Frame", self.display_frame)
            if self.display_floor_plan is not None:
                cv2.imshow("Floor Annotation", self.display_floor_plan)
                
        # Check for exit key - must be called from main thread
        key = cv2.waitKey(1) & 0xFF
        if key == ord('q'):
            self.running = False
    
    def process_frame(self, frame):
        """
        Process a single video frame
        
        Args:
            frame (numpy.ndarray): Input video frame
        
        Returns:
            tuple: Annotated frame and floor plan annotation
        """
        try:
            # Process with a smaller image size for better performance (reduced from 1280)
            results = self.model.track(frame, persist=True, show=False, imgsz=1280, verbose=False)
            
            # Prepare annotation frames
            annotated_frame = frame #.copy()
            floor_annotated_frame = self.floor_annotator.get_floor_plan()
            total_people = 0
            
            # Process detections
            if results[0].boxes is not None and hasattr(results[0].boxes, 'id'):
                boxes = results[0].boxes.xywh.cpu().numpy()
                track_ids = results[0].boxes.id.int().cpu().numpy()
                classes = results[0].boxes.cls.cpu().numpy()
                
                # Filter for human detections (class 0)
                human_indices = classes == 0
                human_boxes = boxes[human_indices]
                human_track_ids = track_ids[human_indices]
                
                # Pre-calculate all transformed points in batch if possible
                #updated_tracks = []
                
                # Annotate trajectories and draw bounding boxes
                for box, track_id in zip(human_boxes, human_track_ids):
                    x, y, w, h = box
                    center = (int(x), int(y + h / 2))
                    
                    # Update track history
                    self.track_history[track_id].append(center)
                    #updated_tracks.append(track_id)
                    
                    # Limit track history
                    if len(self.track_history[track_id]) > 30:  # Reduced from 50
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
                    
                    total_people += 1
                
                    # Draw trajectories for all remaining tracks
                    if len(self.track_history[track_id]) > 1:
                        points = np.array(self.track_history[track_id], dtype=np.int32)
                        
                        if len(points) > 1:
                            
                            # Draw trajectory on original frame
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
                
            # Record people count
            self.current_frame_id += 1
            #self.db.insertRecord(total_people, self.current_frame_id)
            
            return annotated_frame, floor_annotated_frame
        
        except Exception as e:
            print(f"Error processing frame: {e}")
            return frame, self.floor_annotator.get_floor_plan()
    
    def run(self):
        """Start processing with macOS-compatible threading"""
        self.running = True
        
        # Create and start worker threads
        capture_thread = threading.Thread(target=self.capture_thread)
        process_thread = threading.Thread(target=self.processing_thread)
        
        # Set as daemon threads so they exit when main program exits
        capture_thread.daemon = True
        process_thread.daemon = True
        
        # Start threads
        capture_thread.start()
        process_thread.start()
        
        # Store threads
        self.threads = [capture_thread, process_thread]
        
        # Main loop for UI operations (always runs on main thread)
        try:
            while self.running:
                # Display frames from main thread only
                self.main_thread_display()
                
                # Yield to other threads
                time_module.sleep(0.01)
        except KeyboardInterrupt:
            print("Interrupted by user")
        finally:
            self.running = False
            self.release()
    
    def get_frame(self):
        """Generator for streaming annotated frames"""
        # Start worker threads if not already running
        if not self.running:
            self.running = True
            capture_thread = threading.Thread(target=self.capture_thread)
            process_thread = threading.Thread(target=self.processing_thread)
            capture_thread.daemon = True
            process_thread.daemon = True
            capture_thread.start()
            process_thread.start()
            self.threads = [capture_thread, process_thread]
        
        while True:
            try:
                # Wait for frame to be processed
                with self.display_lock:
                    if self.display_frame is not None:
                        # Make a copy to avoid race conditions
                        frame_copy = self.display_frame.copy()
                        ret, buffer = cv2.imencode('.jpg', frame_copy)
                        frame_bytes = buffer.tobytes()
                        yield (b'--frame\r\n'
                               b'Content-Type: image/jpeg\r\n\r\n' + frame_bytes + b'\r\n')
                    else:
                        time_module.sleep(0.05)
            except Exception as e:
                print(f"Stream error: {e}")
                time_module.sleep(0.1)
    
    def get_annotated_frame(self):
        """Generator for streaming floor plan annotations"""
        # Start worker threads if not already running
        if not self.running:
            self.running = True
            capture_thread = threading.Thread(target=self.capture_thread)
            process_thread = threading.Thread(target=self.processing_thread)
            capture_thread.daemon = True
            process_thread.daemon = True
            capture_thread.start()
            process_thread.start()
            self.threads = [capture_thread, process_thread]
        
        while True:
            try:
                # Wait for floor plan to be processed
                with self.display_lock:
                    if self.display_floor_plan is not None:
                        # Make a copy to avoid race conditions
                        floor_copy = self.display_floor_plan.copy()
                        ret, buffer = cv2.imencode('.jpg', floor_copy)
                        frame_bytes = buffer.tobytes()
                        yield (b'--frame\r\n'
                               b'Content-Type: image/jpeg\r\n\r\n' + frame_bytes + b'\r\n')
                    else:
                        time_module.sleep(0.05)
            except Exception as e:
                print(f"Stream error: {e}")
                time_module.sleep(0.1)
    
    def release(self):
        """Release video capture and close windows"""
        self.running = False
        
        # Give threads time to finish
        time_module.sleep(1)
        
        # Release resources
        if self.cap is not None:
            self.cap.release()
        cv2.destroyAllWindows()
        print("Resources released")

# Example usage
if __name__ == "__main__":
    # Use default camera
    #processor = CameraProcessor(source=1)
    
    # For real-life scenarios, processing every 2-3 frames is often sufficient
    # This reduces computational load while maintaining tracking accuracy
    # For crowd monitoring, 5-10 FPS is typically enough, not 30 FPS
    processor = CameraProcessor(
        source="/Users/apple/Desktop/Deakin/T2_2024/SIT764_Capstone/Crowd_Monitor/market-square.mp4", 
        is_video=True,
        process_every_n_frames=10  # Process every 2nd frame (reduces processing by 50%)
    )
    processor.run()