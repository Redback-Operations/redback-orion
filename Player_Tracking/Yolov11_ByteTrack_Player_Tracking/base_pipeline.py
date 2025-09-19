import cv2
import numpy as np
from ultralytics import YOLO
import os
from pathlib import Path
import glob

try:
    from deep_sort_realtime import DeepSort
except ImportError:
    try:
        from deep_sort_realtime.deepsort_tracker import DeepSort
    except ImportError:
        print("DeepSort import failed. Using simple tracking fallback.")
        DeepSort = None

def load_images_from_folder(folder_path):
    """Load all images from the specified folder and sort them"""
    image_extensions = ['*.jpg', '*.jpeg', '*.png', '*.bmp', '*.tiff']
    image_paths = []
    
    for extension in image_extensions:
        image_paths.extend(glob.glob(os.path.join(folder_path, extension)))
        image_paths.extend(glob.glob(os.path.join(folder_path, extension.upper())))
    
    # Sort images by filename to maintain frame order
    image_paths.sort()
    return image_paths

def yolo_detections_to_deepsort_format(detections):
    """Convert YOLO detections to DeepSORT format"""
    deepsort_detections = []
    
    for detection in detections:
        x1, y1, x2, y2 = detection.boxes.xyxy[0].cpu().numpy()
        confidence = detection.boxes.conf[0].cpu().numpy()
        class_id = detection.boxes.cls[0].cpu().numpy()
        
        # Only process person detections 
        if int(class_id) == 0:  # person class
            bbox = [x1, y1, x2 - x1, y2 - y1]
            deepsort_detections.append((bbox, confidence, 'person'))
    
    return deepsort_detections

def create_tracking_video(images_folder, output_video_path, fps=30):
    """Main function to create tracking video"""
    
    print("Loading YOLOv8l model...")
    model = YOLO('yolov8l.pt')  
    
    if DeepSort is not None:
        print("Initializing DeepSORT...")
        tracker = DeepSort(max_age=50, n_init=3, max_cosine_distance=0.2)
        use_deepsort = True
    else:
        print("Using YOLO's built-in tracking...")
        use_deepsort = False
    
    # Load image paths
    image_paths = load_images_from_folder(images_folder)
    if not image_paths:
        print(f"No images found in {images_folder}")
        return
    
    print(f"Found {len(image_paths)} images")
    
    first_image = cv2.imread(image_paths[0])
    height, width = first_image.shape[:2]
    
    fourcc = cv2.VideoWriter_fourcc(*'mp4v')
    video_writer = cv2.VideoWriter(output_video_path, fourcc, fps, (width, height))
    
    colors = [(255, 0, 0), (0, 255, 0), (0, 0, 255), (255, 255, 0), 
              (255, 0, 255), (0, 255, 255), (128, 0, 128), (255, 165, 0)]
    
    print("Processing frames...")
    
    for i, image_path in enumerate(image_paths):
        frame = cv2.imread(image_path)
        if frame is None:
            print(f"Could not load image: {image_path}")
            continue
        
        if use_deepsort:
            # Run YOLO detection for DeepSORT
            results = model(frame, verbose=False)
            
            # Convert detections to DeepSORT format
            detections = []
            if len(results[0].boxes) > 0:
                for j in range(len(results[0].boxes)):
                    x1, y1, x2, y2 = results[0].boxes.xyxy[j].cpu().numpy()
                    confidence = results[0].boxes.conf[j].cpu().numpy()
                    class_id = results[0].boxes.cls[j].cpu().numpy()
                    
                    # if int(class_id) == 0 and confidence > 0.5:
                    bbox = [x1, y1, x2 - x1, y2 - y1]
                    detections.append((bbox, confidence, 'person'))
            
            # Update tracker
            tracks = tracker.update_tracks(detections, frame=frame)
            
            # Draw tracking results
            for track in tracks:
                if not track.is_confirmed():
                    continue
                
                track_id = track.track_id
                bbox = track.to_ltwh()  
                
                # Convert to corner coordinates
                x1, y1, w, h = bbox
                x2, y2 = x1 + w, y1 + h
                
                color_index = abs(int(track_id))
                while color_index >= len(colors):
                    color_index -= len(colors)
                color = colors[color_index]
                
                # Draw bounding box
                cv2.rectangle(frame, (int(x1), int(y1)), (int(x2), int(y2)), color, 2)
                
                # Draw track ID
                cv2.putText(frame, f'ID: {track_id}', 
                           (int(x1), int(y1) - 10), 
                           cv2.FONT_HERSHEY_SIMPLEX, 0.6, color, 2)
        
        else:
            # Use YOLO's built-in tracking (BoT-SORT or ByteTrack)
            results = model.track(frame, classes=[0], conf=0.1, persist=True, verbose=False)
            
            # Debug: Print results structure (only for first few frames)
            if i < 3:
                print(f"Frame {i}: Results type: {type(results[0].boxes)}")
                if results[0].boxes is not None:
                    print(f"Frame {i}: Boxes shape: {results[0].boxes.xyxy.shape}")
                    if results[0].boxes.id is not None:
                        print(f"Frame {i}: Track IDs: {results[0].boxes.id.cpu().numpy()}")
            
            # Draw tracking results
            if results[0].boxes is not None and len(results[0].boxes) > 0:
                boxes = results[0].boxes.xyxy.cpu().numpy()
                confidences = results[0].boxes.conf.cpu().numpy()
                
                # Handle track IDs safely
                if results[0].boxes.id is not None:
                    track_ids = results[0].boxes.id.cpu().numpy().astype(int)
                else:
                    track_ids = list(range(len(boxes)))
                
                for j in range(len(boxes)):
                    try:
                        x1, y1, x2, y2 = boxes[j]
                        confidence = confidences[j]
                        
                        # Ensure track_id is an integer
                        if isinstance(track_ids, (list, np.ndarray)) and j < len(track_ids):
                            track_id = int(track_ids[j])
                        else:
                            track_id = j
                        
                        # Choose color based on track ID (avoid modulo operator)
                        color_index = abs(int(track_id)) 
                        while color_index >= len(colors):
                            color_index -= len(colors)
                        color = colors[color_index]
                        
                        # Draw bounding box
                        cv2.rectangle(frame, (int(x1), int(y1)), (int(x2), int(y2)), color, 2)
                        
                        # Draw track ID and confidence
                        label = f'ID: {track_id} ({confidence:.2f})'
                        cv2.putText(frame, label, 
                                   (int(x1), int(y1) - 10), 
                                   cv2.FONT_HERSHEY_SIMPLEX, 0.6, color, 2)
                        
                    except Exception as e:
                        print(f"Error processing detection {j} in frame {i}: {e}")
                        continue
        
        # Add frame number
        cv2.putText(frame, f'Frame: {i+1}', (10, 30), 
                   cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2)
        
        cv2.imwrite("demo.jpg", frame)
        # Write frame to video
        video_writer.write(frame)
        
        # Print progress
        if (i + 1) % 50 == 0:
            print(f"Processed {i+1}/{len(image_paths)} frames")
    
    # Release video writer
    video_writer.release()
    print(f"Tracking video saved to: {output_video_path}")

def extract_frames_from_video(video_path, output_folder):
    """Extract frames from video to images folder"""
    cap = cv2.VideoCapture(video_path)
    
    if not os.path.exists(output_folder):
        os.makedirs(output_folder)
    
    frame_count = 0
    while True:
        ret, frame = cap.read()
        if not ret:
            break
        
        frame_filename = os.path.join(output_folder, f'frame_{frame_count:06d}.jpg')
        cv2.imwrite(frame_filename, frame)
        frame_count += 1
        
        if frame_count % 100 == 0:
            print(f"Extracted {frame_count} frames")
    
    cap.release()
    print(f"Extracted {frame_count} frames to {output_folder}")

if __name__ == "__main__":
    IMAGES_FOLDER = "test_image" 
    OUTPUT_VIDEO = "tracking_output.mp4"
    FPS = 10  
    
    # Check if images folder exists
    if not os.path.exists(IMAGES_FOLDER):
        print(f"Images folder '{IMAGES_FOLDER}' not found!")
        print("Make sure your images are in the 'images' folder")
    else:
        # Run tracking
        create_tracking_video(IMAGES_FOLDER, OUTPUT_VIDEO, FPS)
        print("Done! Check the output video file.")