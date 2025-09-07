import cv2
import numpy as np
from utils import calculateHomography
from floorReplica import FloorPlanAnnotator
import os

class CoordinateSelector:
    def __init__(self, source, is_video=False):
        """
        Initialize the coordinate selector
        
        Args:
            source (str/int): Camera index or video file path
            is_video (bool): Flag to indicate if source is a video file
        """
        self.source = source
        self.is_video = is_video
        
        # Open the video capture
        if is_video:
            # Validate video file exists
            if not os.path.exists(source):
                raise FileNotFoundError(f"Video file not found: {source}")
            self.cap = cv2.VideoCapture(source)
        else:
            # For camera source (can be index or RTSP)
            self.cap = cv2.VideoCapture(source)
        
        # Initialize floor plan annotator
        self.floor_annotator = FloorPlanAnnotator()
        
        # Points for homography calculation
        self.camera_points = []
        self.floor_points = []
        
        # Frames and images
        self.camera_frame = None
        self.floorImage = self.floor_annotator.get_floor_plan()
    
    def mouse_callback(self, event, x, y, flags, param):
        """Handle mouse events for both camera and floor plan views"""
        if event == cv2.EVENT_LBUTTONDOWN:
            image_type = param['type']
            if image_type == 'camera' and len(self.camera_points) < 5:
                self.camera_points.append((x, y))
                cv2.circle(self.camera_frame, (x, y), 5, (0, 255, 0), -1)
                cv2.putText(self.camera_frame, str(len(self.camera_points)), (x+10, y+10),
                           cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
                cv2.imshow('Camera View', self.camera_frame)
            elif image_type == 'floor' and len(self.floor_points) < 5:
                self.floor_points.append((x, y))
                cv2.circle(self.floorImage, (x, y), 5, (0, 0, 255), -1)
                cv2.putText(self.floorImage, str(len(self.floor_points)), (x+10, y+10),
                           cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2)
                cv2.imshow('Floor Plan', self.floorImage)
    
    def select_points(self):
        """
        Main function to run the coordinate selection process
        
        Returns:
            tuple: Camera points and floor points, or None if selection is cancelled
        """
        # Reset points and floor image
        self.camera_points = []
        self.floor_points = []
        self.floorImage = self.floor_annotator.get_floor_plan()
        
        # Create windows
        cv2.namedWindow('Camera View')
        cv2.namedWindow('Floor Plan')
        
        # Set mouse callbacks
        cv2.setMouseCallback('Camera View', self.mouse_callback, {'type': 'camera'})
        cv2.setMouseCallback('Floor Plan', self.mouse_callback, {'type': 'floor'})
        
        # Instructions overlay
        instruction_text = [
            "Select 5 points in Camera View and Floor Plan",
            "Left-click to add points",
            "Press 'r' to reset points",
            "Press 'c' to confirm points",
            "Press 'q' to quit"
        ]
        
        while True:
            # Read frame
            ret, frame = self.cap.read()
            if not ret:
                # If video ends, reset to beginning
                if self.is_video:
                    self.cap.set(cv2.CAP_PROP_POS_FRAMES, 0)
                    continue
                break
            
            self.camera_frame = frame.copy()
            
            # Draw existing points
            for i, point in enumerate(self.camera_points):
                cv2.circle(self.camera_frame, point, 5, (0, 255, 0), -1)
                cv2.putText(self.camera_frame, str(i+1), (point[0]+10, point[1]+10),
                           cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
            
            # Draw instructions
            for i, text in enumerate(instruction_text):
                cv2.putText(self.camera_frame, text, (10, 30 + i*30), 
                            cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
            
            # Show frames
            cv2.imshow('Camera View', self.camera_frame)
            cv2.imshow('Floor Plan', self.floorImage)
            
            # Wait for key press
            key = cv2.waitKey(1) & 0xFF
            
            if key == ord('q'):
                # Quit without selecting points
                cv2.destroyAllWindows()
                return None, None
            
            elif key == ord('r'):
                # Reset points
                self.camera_points = []
                self.floor_points = []
                self.floorImage = self.floor_annotator.get_floor_plan()
            
            elif key == ord('c'):
                # Confirm points if 5 points are selected in both views
                if len(self.camera_points) == 5 and len(self.floor_points) == 5:
                    cv2.destroyAllWindows()
                    return np.array(self.camera_points), np.array(self.floor_points)
                else:
                    print("Please select exactly 5 points in both Camera View and Floor Plan")
        
        # Release resources
        cv2.destroyAllWindows()
        if self.is_video or isinstance(self.source, int):
            self.cap.release()
        
        return None, None
    
    def get_homography_matrix(self):
        """Get the homography matrix from selected points"""
        camera_points, floor_points = self.select_points()
        if camera_points is not None and floor_points is not None:
            return calculateHomography(camera_points, floor_points)
        return None 