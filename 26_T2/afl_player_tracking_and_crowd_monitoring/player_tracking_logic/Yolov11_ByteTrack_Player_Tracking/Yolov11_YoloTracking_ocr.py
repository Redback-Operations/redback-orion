import cv2
from ultralytics import YOLO
import numpy as np
import json

def calculate_iou(box1, box2):
    """
    Calculate Intersection over Union (IoU) of two bounding boxes.
    box format: [x1, y1, x2, y2]
    """
    x1 = max(box1[0], box2[0])
    y1 = max(box1[1], box2[1])
    x2 = min(box1[2], box2[2])
    y2 = min(box1[3], box2[3])
    
    if x2 <= x1 or y2 <= y1:
        return 0.0
    
    intersection = (x2 - x1) * (y2 - y1)
    
    box1_area = (box1[2] - box1[0]) * (box1[3] - box1[1])
    box2_area = (box2[2] - box2[0]) * (box2[3] - box2[1])
    union = box1_area + box2_area - intersection
    
    if union == 0:
        return 0.0
    
    return intersection / union

# Change to your model
model = YOLO('/home/huylx/workspace/ultralytics/runs/detect/current_best/weights/best.pt')

# Path to your test video
video_path = 'file_to_run/tackle_1 1.mp4'
output_path = video_path[:-4]+"track.mp4"

cap = cv2.VideoCapture(video_path)

fps = int(cap.get(cv2.CAP_PROP_FPS))
width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))

fourcc = cv2.VideoWriter_fourcc(*'mp4v')
out = cv2.VideoWriter(output_path, fourcc, fps, (width, height))

# Initialize tracking data
tracking_data = {
    "video_info": {
        "duration": total_frames / fps,
        "fps": fps,
        "total_frames": total_frames,
        "resolution": [width, height]
    },
    "tracking_results": []
}

frame_number = 0

# Process video frame by frame
while True:
    ret, frame = cap.read()
    if not ret:
        break
    
    results = model.track(
                        frame, 
                        persist=True, 
                        tracker="botsort.yaml"
                    )
    
    boxes = results[0].boxes
    
    if boxes is not None and len(boxes) > 0:
        xyxy = boxes.xyxy.cpu().numpy()  
        conf = boxes.conf.cpu().numpy() 
        cls = boxes.cls.cpu().numpy()  
        
        keep_indices = []
        
        for i in range(len(boxes)):
            keep = True
            current_box = xyxy[i]
            current_conf = conf[i]
            current_cls = cls[i]

            if current_conf < 0.3:
                continue
            
            for j in range(len(boxes)):
                if i == j:
                    continue
                    
                compare_box = xyxy[j]
                compare_conf = conf[j]
                compare_cls = cls[j]
                
                iou = calculate_iou(current_box, compare_box)
                
                # If boxes overlap significantly (IoU > threshold)
                if iou > 0.7:  
                    if current_conf < compare_conf:
                        keep = False
                        break
                    elif current_conf == compare_conf:
                        class_names = model.names
                        current_class_name = class_names[int(current_cls)]
                        compare_class_name = class_names[int(compare_cls)]
                        
                        if current_class_name == 'referee' and compare_class_name == 'player':
                            keep = False
                            break
            
            if keep:
                keep_indices.append(i)
        
        if keep_indices:
            filtered_boxes = boxes[keep_indices]
            results[0].boxes = filtered_boxes
    
    frame_data = {
        "frame_number": frame_number + 1,
        "timestamp": round(frame_number / fps, 3),
        "players": []
    }
    
    final_boxes = results[0].boxes
    if final_boxes is not None and len(final_boxes) > 0:
        final_xyxy = final_boxes.xyxy.cpu().numpy()
        final_conf = final_boxes.conf.cpu().numpy()
        final_ids = final_boxes.id.cpu().numpy() if final_boxes.id is not None else None
        
        for i in range(len(final_boxes)):
            bbox = final_xyxy[i]
            confidence = float(final_conf[i])
            player_id = int(final_ids[i]) if final_ids is not None else i + 1
            
            player_data = {
                "player_id": player_id,
                "bbox": {
                    "x1": int(bbox[0]),
                    "y1": int(bbox[1]),
                    "x2": int(bbox[2]),
                    "y2": int(bbox[3])
                },
                "center": {
                    "x": int((bbox[0] + bbox[2]) / 2),
                    "y": int((bbox[1] + bbox[3]) / 2)
                },
                "confidence": round(confidence, 2),
                "width": int(bbox[2] - bbox[0]),
                "height": int(bbox[3] - bbox[1])
            }
            frame_data["players"].append(player_data)
    
    tracking_data["tracking_results"].append(frame_data)
    
    annotated_frame = results[0].plot()
    
    out.write(annotated_frame)
    
    frame_number += 1

cap.release()
out.release()

# Save JSON output
json_output_path = video_path[:-4]+"track.json"
with open(json_output_path, 'w') as f:
    json.dump(tracking_data, f, indent=2)

print(f"Inference complete! Output saved to: {output_path}")
print(f"Tracking data saved to: {json_output_path}")